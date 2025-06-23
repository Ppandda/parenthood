from .base import Question
import pandas as pd
import numpy as np
import plotly.express as px
from typing import Optional
from transform_time import unified_time_to_weeks


def auto_bin_grouped_df(df, value_col="Value", group_col="Group"):
    bin_edges = np.histogram_bin_edges(df[value_col], bins="auto")
    df["Value_binned"] = pd.cut(df[value_col], bins=bin_edges, include_lowest=True)

    def interval_to_range_label(interval):
        return f"{int(interval.left)}–{int(interval.right)}"

    df["Bin_Label"] = df["Value_binned"].apply(interval_to_range_label)

    binned = (
        df.groupby([group_col, "Bin_Label"]).agg(Count=("Count", "sum")).reset_index()
    )

    binned["Percentage"] = binned.groupby(group_col)["Count"].transform(
        lambda x: 100 * x / x.sum()
    )

    return binned, bin_edges


class MatrixQuestion(Question):
    """
    Class for handling matrix-style survey questions (e.g., child birth year and country).
    Each row represents a subject (e.g., child), and each column represents an attribute (e.g., year, country).
    DE23, PL1, PL2, PL3, PL4, PL6, PL7, PL9
    """

    def __init__(
        self,
        question_id,
        df,
        df_raw,
        value_transform=None,
        gender_lookup=None,
        **kwargs,
    ):
        super().__init__(question_id, df, df_raw, value_transform)

        self.df.index = self.df.index.astype(int)
        self.df_raw.index = self.df_raw.index.astype(int)

        self.extract_columns()
        self.gender_lookup = gender_lookup
        self.get_mappings()
        self.row_map = self.metadata.get("row_map", {})
        self.grouping_key = self.metadata.get("row_grouping_label", "Group")
        self.anchor_type = kwargs.get("anchor_type", "parent_gender")

    def get_parent_gender(
        self, respondent_id: int, parent_number: str
    ) -> Optional[str]:
        """
        Given a respondent and whether it's parent 1 or 2, fetch the gender label.
        """
        gender_question_id = (
            "DE14"  # hardcoded because we know this special logic only applies to DE14
        )
        gender_column = f"{gender_question_id}_{parent_number}"
        try:
            gender_code = self.df_raw.at[respondent_id, gender_column]
            if pd.isna(gender_code):
                return None
            gender_label = self.metadata.get("value_map", {}).get(int(gender_code))

            return gender_label
        except KeyError:
            return None

    def normalize_units(self, responses: pd.Series, subcol: str) -> pd.Series:
        """Convert responses to weeks if sub_map is defined and subcol encodes a unit."""
        if hasattr(self, "sub_map") and self.sub_map:
            try:
                unit_code = subcol.split("_")[-1]
                unit_label = self.sub_map.get(int(unit_code), unit_code)
                return responses.apply(lambda v: unified_time_to_weeks(v, unit_label))
            except Exception as e:
                print(f"[Warning] Failed to normalize time in {subcol}: {e}")
        return responses

    def distribution(self, display=False):
        if not self.subcolumns:
            print(
                f"[Warning] Skipping plot for question '{self.question_id}': no subcolumns."
            )
            return None

        data = []

        for subcol in self.subcolumns:
            responses = self.responses[subcol].dropna()
            mapped = self.normalize_units(responses, subcol)

            if not self.sub_map:
                if self.value_map:
                    if all(isinstance(k, int) for k in self.value_map):
                        responses_numeric = pd.to_numeric(responses, errors="coerce")
                        mapped = (
                            responses_numeric.round()
                            .astype("Int64")
                            .map(self.value_map)
                        )
                    else:
                        mapped = responses.map(self.value_map)
                else:
                    mapped = responses

            sub_id = subcol.split("_")[-1]

            for respondent_id, value in mapped.dropna().items():
                if self.anchor_type == "parent_gender":
                    if self.question_id == "DE14":
                        gender_label = self.get_parent_gender(respondent_id, sub_id)
                        if gender_label and self.gender_lookup is not None:
                            self.gender_lookup[(respondent_id, sub_id)] = gender_label
                    else:
                        gender_label = (
                            self.gender_lookup.get((respondent_id, sub_id))
                            if self.gender_lookup
                            else None
                        )

                    if gender_label is None:
                        if self.question_id == "DE14":
                            gender_label = self.value_map.get(int(sub_id), None)
                        else:
                            try:
                                de14_val = self.df.loc[respondent_id, f"DE14_{sub_id}"]
                                gender_label = (
                                    "Woman"
                                    if de14_val == 1
                                    else (
                                        "Man"
                                        if de14_val == 2
                                        else (
                                            "Non-binary person"
                                            if de14_val == 3
                                            else None
                                        )
                                    )
                                )
                            except KeyError:
                                gender_label = None

                    group_label = gender_label
                    value_label = (
                        value if self.question_id != "DE14" else gender_label
                    )  # Special handling for DE14 only
                else:
                    group_label = self.row_map.get(
                        int(sub_id), f"{self.question_id}_{sub_id}"
                    )
                    value_label = self.value_map.get(value, value)
                    # else:
                    # anchor_type == "none"
                    #   group_label = self.value_map.get(value, value)
                    #  value_label = self.sub_map.get(
                    #     f"{self.question_id}_{sub_id}", f"{self.question_id}_{sub_id}"
                    # )

                    """data.append(
                        {
                            "Group": gender_label,
                            "Value": value if self.question_id != "DE14" else gender_label,
                            "Count": 1,
                            "Percentage": 100,
                        }
                    )"""
                data.append(
                    {
                        "Group": group_label,
                        "Value": value_label,
                        "Count": 1,
                        "Percentage": 100,
                    }
                )

        if not data:
            return None

        df_data = pd.DataFrame(data)

        grouped = (
            df_data.groupby(["Group", "Value"])
            .agg(Count=("Count", "sum"))
            .reset_index()
        )

        """# if self.question_id == "DE14":
        if self.anchor_type == "parent_gender":
            grouped["Percentage"] = 100 * grouped["Count"] / grouped["Count"].sum()
        else:
            grouped["Percentage"] = grouped.groupby("Group")["Count"].transform(
                lambda x: 100 * x / x.sum()
            )"""

        if self.anchor_type == "parent_gender":
            grouped["Percentage"] = (
                0
                if grouped["Count"].sum() == 0
                else 100 * grouped["Count"] / grouped["Count"].sum()
            )
        else:
            for name, group in grouped.groupby("Group"):
                total = group["Count"].sum()
                print(f"Group: {name}, Count sum: {total}")
                assert not pd.isna(total), "Count sum is NaN"
                assert total != 0, f"Zero sum in group {name}"
            grouped["Percentage"] = grouped.groupby("Group")["Count"].transform(
                lambda x: 0 if x.sum() == 0 else 100 * x / x.sum()
            )

        # Automatically bin values if question is numeric and continuous
        if pd.api.types.is_numeric_dtype(grouped["Value"]):
            grouped, bin_edges = auto_bin_grouped_df(
                grouped, value_col="Value", group_col=self.grouping_key
            )
            value_key = "Bin_Label"
        else:
            value_key = "Value"

        fig = self._plot_grouped_bar_distribution(
            grouped,
            self.question_text,
            value_key=value_key,
            group_key=self.grouping_key,
        )

        if display and fig is not None:
            fig.show()

        return fig

    def _plot_grouped_bar_distribution(
        self, df, title, value_key="Value", group_key="Group"
    ):
        raw_title = self.truncate_after_first_period(self.question_text)
        wrapped_title = self.wrap_text(raw_title, width=60)

        value_order = list(self.metadata.get("value_map", {}).values())
        group_order = list(self.metadata.get("row_map", {}).values())

        label_lengths = [len(str(v)) for v in value_order]
        long_labels = any(l > 13 for l in label_lengths) or (
            sum(label_lengths) / len(label_lengths) > 18 if label_lengths else False
        )

        xaxis_kwargs = {}
        if long_labels:
            wrapped_labels = [self.wrap_label(label, width=12) for label in value_order]
            xaxis_kwargs = {
                "tickmode": "array",
                "tickvals": value_order,
                "ticktext": wrapped_labels,
                "tickfont": dict(size=12),
            }

        # Legend/axis category order
        category_order = {value_key: value_order}
        if group_key == "Group":
            if self.anchor_type == "parent_gender":
                category_order["Group"] = ["Woman", "Man", "Non-binary person"]
            elif group_order:
                category_order["Group"] = group_order

        # Colors
        if self.question_id in {"DE14", "DE15", "DE16"}:
            color_args = {
                "color_discrete_map": {
                    "Woman": "#D7D9B1",
                    "Man": "#3A6992",
                    "Non-binary person": "#BB4430",
                }
            }
        else:
            color_args = {
                "color_discrete_sequence": [
                    "#D7D9B1",
                    "#3A6992",
                    "#BB4430",
                    "#795663",
                    "#B89685",
                    "#808F85",
                ]
            }

        # Plot
        if self.question_id == "DE14":
            df["BarWidth"] = 0.6
            fig = px.bar(
                df,
                x="Value",
                y="Percentage",
                color="Value",
                title=wrapped_title,
                text=df["Percentage"].apply(lambda x: f"{round(x, 1)}%"),
                hover_data=["Count"],
                category_orders=category_order,
                **color_args,
            )
            fig.update_traces(width=df["BarWidth"])
        else:
            fig = px.bar(
                df,
                x=value_key,
                y="Percentage",
                color=group_key,
                barmode="group",
                title=wrapped_title,
                text=df["Percentage"].apply(lambda x: f"{round(x, 1)}%"),
                hover_data=["Count"],
                category_orders=category_order,
                **color_args,
            )

        fig.update_layout(
            width=1000,
            height=max(400, 30 * len(value_order)),
            margin=dict(r=200),
            xaxis_title="",
            yaxis_title="Percentage (%)",
            xaxis=xaxis_kwargs,
        )

        fig.update_traces(marker_line_color=None, marker_line_width=1)

        return fig

    def __repr__(self):
        if not self.responses:
            return f"{self.question_text} No answer provided."

        response_texts = []
        for row_label, answers in self.responses.items():
            if isinstance(answers, dict):
                # nested dict (DE23)
                items = []
                for k, v in answers.items():
                    label = self.sub_map.get(k, k)
                    if self.value_transform and k != "1":
                        label = "weeks"

                    items.append(f"{label}: {v}")
                response_texts.append(f"{row_label}: " + ", ".join(items))
            else:
                # Flat (DE5)
                response_texts.append(
                    f"{self.row_map.get(row_label, row_label)}: {answers}"
                )

        return f"{self.question_text} Responses:\n" + "\n".join(response_texts)

    def __str__(self):
        return self.__repr__()
