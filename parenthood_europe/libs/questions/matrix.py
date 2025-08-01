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

        # ------- parent‑gender override -----------------------------------
        if self.anchor_type == "parent_gender":
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
        if self.question_id == "PL2":
            df_long["value"] = df_long["value"].clip(lower=0, upper=60)

            bins = [0, 2, 4, 7, 13, 19, 25, 37, float("inf")]
            labels = ["0–1", "2–3", "4–6", "7–12", "13–18", "19–24", "25–36", "37+"]

            df_long["Bin_Label"] = pd.cut(
                df_long["value"], bins=bins, labels=labels, right=False
            )
            df_long = df_long.dropna(subset=["Bin_Label"])
            value_key = "Bin_Label"
            order_for_x = labels  # preserve our fixed order
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

        df_long["Count"] = 1

        if self.anchor_type == "parent_gender" and self.question_id == "DE14":
            # For DE14, aggregate only by 'value' (gender label) globally
            grouped = (
                df_long.groupby("value", observed=True)
                .agg(Count=("Count", "sum"))
                .reset_index()
            )
            # Compute percentages globally (sum to 100%)
            total_count = grouped["Count"].sum()
            grouped["Percentage"] = (
                100 * grouped["Count"] / total_count if total_count > 0 else 0
            )

            self.grouping_key = "value"
            value_key = "value"
            order_for_x = sorted(grouped[value_key].unique())

        else:
            # Existing logic for all other questions
            grouped = percent_within(df_long, ["Group", value_key])

            if self.anchor_type != "parent_gender":
                self.grouping_key = "Group"

            # Sort x-axis labels for plotting
            if pd.api.types.is_numeric_dtype(df_long[value_key]):
                order_for_x = sorted(grouped[value_key].unique())
            else:
                order_for_x = sorted(grouped[value_key].unique())

        # --- Plotting ---

        fig = grouped_bar(
            grouped,
            x=value_key,
            y="Percentage",
            hue=self.grouping_key,
            title=self.question_text,
            category_orders={
                value_key: order_for_x,
                self.grouping_key: sorted(grouped[self.grouping_key].unique()),
            },
        )

        if self.question_id == "PL2":
            fig.update_layout(xaxis_title="Months")

        if display and fig:
            fig.show()

        return fig
