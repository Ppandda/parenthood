from .base import Question
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

    def distribution(self, display=True):
        if self.responses is None or len(self.responses) == 0:
            print(
                f"[Warning] Skipping plot for question '{self.question_id}': no responses."
            )
            return None

        counts = self.responses[self.subcolumns[0]].map(self.value_map).value_counts()
        labels, values = self.get_ordered_labels_and_values(counts)

        fig = self._choose_and_plot(labels, values, self.question_text)

        if display and fig is not None:
            fig.show()

        return fig
