from .base import Question
import question_maps
from libs.matrix_utils import numeric_sort
from libs.plotting import grouped_bar
from libs.matrix_utils import (
    build_long_df,
    bin_numeric,
    percent_within,
    resolve_gender,
)
import pandas as pd
import numpy as np

# import plotly.express as px
from typing import Optional

# from question_maps import DE5 as _COUNTRY_MAP
# import country_converter as coco

# cc = coco.CountryConverter()

YEAR_ZERO = 2025


# -------------------------------------------------------------------------
#  special‑case matrix (child birth year × country)
# -------------------------------------------------------------------------
class BirthYearMatrixQuestion(Question):
    """Handles DE23 only."""

    def __init__(self, question_id, df, meta, question_text=None):
        super().__init__(question_id, df, meta)
        if question_text:
            self.question_text = question_text

    def distribution(self, display: bool = True):
        data = []
        for child_id in self.row_map:
            ycol = f"{self.question_id}_{child_id}_1"
            ccol = f"{self.question_id}_{child_id}_2"
            if ycol not in self.df or ccol not in self.df:
                continue
            yrs = self.df[ycol].dropna()
            for rid, year in yrs.items():
                country = self.df.at[rid, ccol]
                if pd.isna(country):
                    continue
                data.append(
                    {
                        "Group": self._country_to_region(country),
                        "Value": YEAR_ZERO - int(year),
                        "Count": 1,
                    }
                )
        if not data:
            return None
        df = pd.DataFrame(data)
        df["Value"] = (df["Value"] // 10 * 10).astype(int)  # decade buckets
        grp = percent_within(df, ["Group", "Value"])
        fig = grouped_bar(
            grp,
            x="Value",
            y="Percentage",
            hue="Group",
            title=self.question_text,
            category_orders={
                "Value": sorted(grp["Value"].unique()),
                "Group": sorted(grp["Group"].unique()),
            },
        )

        meta = self.metadata or {}
        if fig:
            xlbl = meta.get("x_label")
            fig.update_layout(xaxis_title=xlbl)
            if meta.get("legend_title"):
                fig.update_layout(legend_title_text=meta["legend_title"])

        if display and fig:
            fig.show()
        return fig

    # --- utils -------------------------------------------------------------
    from question_maps import DE5 as _COUNTRY_MAP
    import country_converter as coco

    _cc = coco.CountryConverter()

    def _country_to_region(self, code: int) -> str:
        name = self._COUNTRY_MAP["value_map"].get(int(code), str(code))
        if name in {"Serbia and Montenegro", "Serbia", "Montenegro"}:
            return "Europe"
        region = self._cc.convert(names=name, to="Continent", not_found=None)
        return region or name


# -------------------------------------------------------------------------
#  generic matrix question
# -------------------------------------------------------------------------
class MatrixQuestion(Question):
    """
    Handles PL1, PL2, PL3, PL4, PL6, PL7, PL9, DE14, DE15, DE16
    """

    def __init__(
        self,
        question_id,
        df,
        meta: dict[str, dict],
        value_transform=None,
        gender_lookup=None,
        **kwargs,
    ):
        super().__init__(question_id, df, meta, value_transform)
        self.df.index = self.df.index.astype(int)
        self.extract_columns()
        self.gender_lookup = gender_lookup or {}
        self.get_mappings()
        self.row_map = self.metadata.get("row_map", {})
        self.sub_map = self.metadata.get("sub_map", {})
        self.grouping_key = self.metadata.get("row_grouping_label", "Group")
        self.anchor_type = kwargs.get(
            "anchor_type", self.metadata.get("group_by", "row")
        )

    # ------------------------------------------------------------------ #
    # MAIN API
    # ------------------------------------------------------------------ #
    def distribution(self, display: bool = True):
        if not self.subcolumns:
            return None
        if self.question_id == "DE23":
            return BirthYearMatrixQuestion(
                self.question_id,
                self.df,
                self.metadata,
                question_text=self.question_text,
            ).distribution(display)

        df_long = build_long_df(self)

        decoded = False

        vm_cfg = getattr(question_maps, self.question_id, {}).get("value_map", {})
        if vm_cfg and not (
            self.question_id == "DE14" and self.anchor_type == "parent_gender"
        ):
            codes = pd.to_numeric(df_long["value"], errors="coerce")
            vm_keys = {int(k) for k in vm_cfg.keys() if str(k).isdigit()}
            if vm_keys and (codes.isin(vm_keys).mean() >= 0.5):
                df_long["value"] = codes.map({int(k): v for k, v in vm_cfg.items()})
                decoded = True

        handled = False
        bin_cfg = None  # so we can safely reference it later
        if "Count" not in df_long.columns:  # needed before any percent_within()
            df_long["Count"] = 1

        # PL6 (and similar): show % per child → x=child (Group), hue=option (value)
        swap_cfg = (self.metadata or {}).get("swap_axes") or getattr(
            question_maps, self.question_id, {}
        ).get("swap_axes")

        if swap_cfg:
            # consistent orders
            child_order = sorted(df_long["Group"].unique(), key=lambda s: int(str(s)))
            option_order = (
                [vm_cfg[k] for k in vm_cfg]
                if vm_cfg
                else list(df_long["value"].unique())
            )

            if swap_cfg == "value_on_x":
                # x = option, hue = child
                grouped = percent_within(df_long, ["value", "Group"])
                self.grouping_key = "Group"
                value_key = "value"
                order_for_x = option_order
                hue_order = child_order
            else:
                # x = child, hue = option (previous behavior)
                grouped = percent_within(df_long, ["Group", "value"])
                self.grouping_key = "value"
                value_key = "Group"
                order_for_x = child_order
                hue_order = option_order

            handled = True
        # ------- parent‑gender override -----------------------------------
        elif (
            (not handled)
            and self.anchor_type == "parent_gender"
            and self.question_id == "DE14"
        ):
            df_long["Group"] = df_long.apply(
                lambda r: resolve_gender(
                    self.df,
                    r["ResponseId"],
                    r["Group"].split("_")[-1],  # parent number
                    self.gender_lookup,
                    question_maps.DE14["value_map"],
                ),
                axis=1,
            )

        # ------------------------------------------------------------------
        # 1.  Binning logic (PL2 has its own fixed bins, everything else generic)
        # ------------------------------------------------------------------
        if not handled:
            bin_cfg = (self.metadata or {}).get("binning") or getattr(
                question_maps, self.question_id, {}
            ).get("binning")
            if bin_cfg:
                vals = pd.to_numeric(df_long["value"], errors="coerce")
                edges = bin_cfg["edges"]
                labels = bin_cfg["labels"]
                df_long["Bin_Label"] = pd.cut(
                    vals, bins=edges, labels=labels, right=False
                )
                df_long = df_long.dropna(subset=["Bin_Label"])
                value_key = "Bin_Label"
                order_for_x = labels
            else:
                if pd.api.types.is_numeric_dtype(df_long["value"]):
                    df_long["Bin_Label"] = bin_numeric(df_long["value"])
                    value_key = "Bin_Label"
                    order_for_x = numeric_sort(list(df_long[value_key].unique()))
                else:
                    value_key = "value"
                    order_for_x = sorted(df_long[value_key].unique())

        # ------------------------------------------------------------------
        # 2. Before aggregation and plotting
        # ------------------------------------------------------------------

        if (
            (not handled)
            and self.anchor_type == "parent_gender"
            and self.question_id == "DE14"
        ):
            # --- map codes -> labels and lock the semantic order ---
            vm = question_maps.DE14["value_map"]  # {1:'Woman', 2:'Man', 3:'Non-binary'}
            label_order = [vm[k] for k in vm]  # preserve map insertion order

            if not decoded:
                df_long["value"] = pd.to_numeric(df_long["value"], errors="coerce").map(
                    vm
                )

            df_long["value"] = pd.Categorical(
                df_long["value"], categories=label_order, ordered=True
            )

            # --- aggregate globally over 'value' ---
            grouped = (
                df_long.groupby("value", observed=True)
                .agg(Count=("Count", "sum"))
                .reset_index()
            )

            # keep categorical order in the aggregated frame too
            grouped["value"] = pd.Categorical(
                grouped["value"], categories=label_order, ordered=True
            )
            grouped = grouped.sort_values("value")

            total_count = grouped["Count"].sum()
            grouped["Percentage"] = (
                100 * grouped["Count"] / total_count if total_count > 0 else 0
            )

            self.grouping_key = "value"
            value_key = "value"
            order_for_x = label_order  # <- use semantic order

        elif not handled:
            # Existing logic for all other questions
            grouped = percent_within(df_long, ["Group", value_key])

            if self.anchor_type != "parent_gender":
                self.grouping_key = "Group"

            if bin_cfg:
                pass
            else:
                if pd.api.types.is_numeric_dtype(df_long[value_key]):
                    order_for_x = sorted(grouped[value_key].unique())
                else:
                    totals = (
                        grouped.groupby(value_key, observed=True)["Percentage"]
                        .sum()
                        .sort_values(ascending=False)
                    )
                    order_for_x = list(totals.index)

        # --- Plotting ---

        # Use the grouping key unless it would duplicate x
        hue_key = self.grouping_key
        if hue_key == value_key:  # <— generic, no QID hardcode
            hue_key = None  # single full-width bar per category

        cat_orders = {value_key: order_for_x}
        if hue_key:
            cat_orders[hue_key] = (
                hue_order
                if "hue_order" in locals() and hue_order is not None
                else sorted(grouped[hue_key].unique())
            )

        fig = grouped_bar(
            grouped,
            x=value_key,
            y="Percentage",
            hue=hue_key,
            title=self.question_text,
            category_orders=cat_orders,
        )

        meta = self.metadata or {}
        if fig is not None and bin_cfg and bin_cfg.get("unit"):
            fig.update_layout(xaxis_title=bin_cfg["unit"].capitalize())
        elif "x_label" in meta:
            fig.update_layout(xaxis_title=meta["x_label"] or "")
        if "legend_title" in meta:
            fig.update_layout(legend_title_text=meta["legend_title"] or "")

        if display and fig is not None:
            fig.show()

        return fig
