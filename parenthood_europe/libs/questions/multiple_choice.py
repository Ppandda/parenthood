from .base import Question
import pandas as pd


class MultipleChoiceQuestion(Question):
    """
    Class for a multiple-choice survey question.
    DE3, DE7, DE9
    """

    def __init__(
        self,
        question_id: str,
        df: pd.DataFrame,
        df_raw: pd.DataFrame,
        value_transform=None,
    ):
        super().__init__(question_id, df, df_raw, value_transform)
        self.extract_columns()

    def extract_columns(self):
        super().extract_columns()
        if self.question_id in self.df.columns:
            raw_series = self.df[self.question_id].dropna().astype(str)
            self.responses = raw_series
            self.subcolumns = [self.question_id]

    """def get_flattened_responses(self) -> pd.Series:
        combined = []
        for row in self.responses.dropna():
            combined.extend(row.split(","))
        return pd.Series(combined, dtype=str)"""

    def get_flattened_responses(self) -> pd.Series:
        if self.responses is None:
            return pd.Series([], dtype=str)

        combined = []
        for row in self.responses.dropna():
            combined.extend(row.split(","))

        return pd.Series(combined, dtype=str)

    def __repr__(self):
        selected_text = (
            ", ".join(self.responses) if self.responses else "No responses selected"
        )
        custom_text = f", {self.custom_response}" if self.custom_response else ""
        return f"{self.question_text} Answer: {selected_text}{custom_text}."

    def analyze(self):
        """
        Analyze the multiple-choice responses.
        """
        choice_counts = {choice: 0 for choice in self.choices}

        for response in self.responses:
            if response in choice_counts:
                choice_counts[response] += 1
            else:
                print(f"Custom response detected: {response}")

        return {
            "choice_counts": choice_counts,
            "custom_responses": self.custom_responses,
        }

    def distribution(self, display=True):
        combined_series = self.get_flattened_responses()
        mapped = combined_series.astype(str).map(
            {str(k): v for k, v in self.value_map.items()}
        )
        counts = mapped.value_counts()

        # title = self.truncate_after_first_period(self.question_text)
        # fig = self.plot_distribution_from_counts(counts, title)
        labels, values = self.get_ordered_labels_and_values(counts)
        fig = self._choose_and_plot(labels, values, self.question_text)

        if display and fig is not None:
            fig.show()

        return fig
