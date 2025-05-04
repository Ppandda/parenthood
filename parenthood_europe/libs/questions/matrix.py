from .base import Question
import pandas as pd
import plotly.express as px
from typing import Optional


class MatrixQuestion(Question):
    """
    Class for handling matrix-style survey questions (e.g., child birth year and country).
    Each row represents a subject (e.g., child), and each column represents an attribute (e.g., year, country).
    DE23, PL1, PL2, PL3, PL4, PL6, PL7, PL9
    """

    def __init__(
        self, question_id, df, df_raw, value_transform=None, gender_lookup=None
    ):
        super().__init__(question_id, df, df_raw, value_transform)

        self.df.index = self.df.index.astype(int)
        self.df_raw.index = self.df_raw.index.astype(int)

        self.extract_columns()
        self.gender_lookup = gender_lookup
        self.get_mappings()
        self.row_map = self.metadata.get("row_map", {})
        self.grouping_key = self.metadata.get("row_grouping_label", "Group")

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

    def distribution(self, display=False):
        if not self.subcolumns:
            print(
                f"[Warning] Skipping plot for question '{self.question_id}': no subcolumns."
            )
            return None

        data = []

        for subcol in self.subcolumns:
            responses = self.responses[subcol].dropna()

            if self.value_map:
                mapped = responses.astype("Int64").map(self.value_map)
            else:
                mapped = responses

            sub_id = subcol.split("_")[-1]

            for respondent_id, value in mapped.dropna().items():
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
                        # basically i need to read the answer to DE14 here
                        # sub_id is the parent number
                        # we need to get the answer to DE14_1 if sub_id is 1
                        # and DE14_2 if sub_id is 2
                        de14_resp = self.df.loc[respondent_id, f"DE14_{sub_id}"]
                        gender_label = (
                            "Woman"
                            if de14_resp == 1
                            else (
                                "Man"
                                if de14_resp == 2
                                else "Non-binary person" if de14_resp == 3 else None
                            )
                        )

                data.append(
                    {
                        "Group": gender_label,
                        "Value": value if self.question_id != "DE14" else gender_label,
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

        if self.question_id == "DE14":
            grouped["Percentage"] = 100 * grouped["Count"] / grouped["Count"].sum()
        else:
            grouped["Percentage"] = grouped.groupby("Value")["Count"].transform(
                lambda x: 100 * x / x.sum()
            )

        fig = self._plot_grouped_bar_distribution(
            grouped,
            self.question_text,
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

        value_order = list(self.value_map.values())
        unique_labels = value_order
        label_lengths = [len(l) for l in unique_labels]
        long_labels = (
            any(length > 13 for length in label_lengths)
            or (sum(label_lengths) / len(label_lengths)) > 18
        )

        if long_labels:
            wrapped_labels = [
                self.wrap_label(label, width=12) for label in unique_labels
            ]
            xaxis_kwargs = {
                "tickmode": "array",
                "tickvals": unique_labels,
                "ticktext": wrapped_labels,
                "tickfont": dict(size=12),
            }
        else:
            xaxis_kwargs = {}

        GENDER_COLOR_SEQUENCE = {
            "Woman": "#D7D9B1",
            "Man": "#3A6992",
            "Non-binary person": "#BB4430",
        }

        GENDER_ORDER = ["Woman", "Man", "Non-binary person"]

        if self.question_id in {"DE14", "DE15", "DE16"}:
            color_args = {"color_discrete_map": GENDER_COLOR_SEQUENCE}
        else:
            color_args = {"color_discrete_sequence": ["#D7D9B1", "#3A6992", "#BB4430"]}

        # Pull value order from question_maps.py
        value_order = (
            list(self.value_map.values()) if hasattr(self, "value_map") else []
        )
        category_order = {value_key: value_order}

        # For gender questions: fix legend/group order
        if group_key == "Group" and self.question_id in {"DE14", "DE15", "DE16"}:
            category_order["Group"] = GENDER_ORDER

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
                **color_args,
                title=wrapped_title,
                text=df["Percentage"].apply(lambda x: f"{round(x, 1)}%"),
                hover_data=["Count"],
                category_orders=category_order,
            )

        fig.update_layout(
            width=1000,
            height=max(400, 30 * len(unique_labels)),
            margin=dict(r=200),
            xaxis_title="",
            yaxis_title="Percentage (%)",
            xaxis=xaxis_kwargs,
        )

        fig.update_traces(
            marker_line_color=None,
            marker_line_width=1,
        )

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
