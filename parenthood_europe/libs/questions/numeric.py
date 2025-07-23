from .base import Question
import pandas as pd


class NumericQuestion(Question):
    """
    Class for a numeric-based survey question.
    DE1, DE10, DE11, DE22
    """

    def __init__(
        self,
        question_id: str,
        df: pd.DataFrame,
        meta: dict[str, dict],
        value_transform=None,
    ):
        super().__init__(question_id, df, meta, value_transform)

        self.min_value = 0
        self.max_value = 1000000

        self.extract_columns()
        self.extract_numeric_responses()

    def distribution(self, display=True):
        if self.responses is None or len(self.responses) == 0:
            print(
                f"[Warning] Skipping plot for question '{self.question_id}': no responses."
            )
            return None

        values = self.get_combined_responses()
        summary_stats = {
            "Min": values.min(),
            "Mean": values.mean(),
            "Median": values.median(),
            "Total Responses": len(values),
        }

        fig = self._choose_and_plot(
            self.get_labels(self.subcolumns), values, self.question_text, summary_stats
        )

        if display and fig is not None:
            fig.show()

        return fig

    def extract_numeric_responses(self):
        if self.subcolumns:
            self.responses = {
                sub: pd.to_numeric(self.df[sub], errors="coerce").dropna()
                for sub in self.subcolumns
            }
        elif self.question_id in self.df.columns:
            self.responses = pd.to_numeric(
                self.df[self.question_id], errors="coerce"
            ).dropna()
        else:
            self.responses = pd.Series([], dtype=float)

    def __repr__(self):
        if self.responses is None or self.responses.empty:
            return f"{self.question_text} — No responses provided."
        return f"{self.question_text} — {len(self.responses)} responses collected."
