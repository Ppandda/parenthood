from .base import Question
from libs.plotting import bar
import pandas as pd


class SingleChoiceQuestion(Question):
    def __init__(
        self,
        question_id: str,
        df: pd.DataFrame,
        meta: dict[str, dict],
        value_transform=None,
    ):
        super().__init__(question_id, df, meta, value_transform)

        self.extract_columns()

    def as_frame(self) -> pd.DataFrame:
        if "ResponseId" not in self.df.columns:
            raise KeyError("DataFrame lacks 'ResponseId' column")

        col = self.subcolumns[0]  # the single data column
        series = self.df[col].dropna()

        # decode numeric codes → labels if value_map exists
        if self.value_map:
            series = series.astype("Int64").map(self.value_map)

        resp_ids = self.df.loc[series.index, "ResponseId"].values
        return pd.DataFrame(
            {"ResponseId": resp_ids, "value": series.values}
        ).reset_index(drop=True)

    def distribution(self, display: bool = True):
        if not self.subcolumns:
            return None

        # map numeric codes → labels, then count
        series = self.df[self.subcolumns[0]].dropna()
        if self.value_map:
            series = series.astype("Int64").map(self.value_map)

        counts = series.value_counts()
        labels, values = self.get_ordered_labels_and_values(counts)

        fig = bar(labels, values, title=self.question_text)
        if display and fig is not None:
            fig.show()
        return fig
