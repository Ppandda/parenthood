import sys
from pathlib import Path
from IPython.display import IFrame
import question_maps
import textwrap
import numpy as np
import plotly.graph_objects as go


# Automatically add the project root to sys.path
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pandas as pd
import numpy as np
from typing import Callable, Any, Optional
from transform_time import months_to_weeks, unified_time_to_weeks
import plotly.express as px


class Question:
    """
    Base class for a survey question.
    """

    def __init__(
        self,
        question_id: str,
        df: pd.DataFrame,
        meta: dict[str, dict],
        value_transform: Callable[[Any], Any] = None,
    ):
        self.question_id = question_id  # e.g., "Q1", "Q2"
        self.df = df
        self.meta = meta
        self.value_transform = value_transform
        self.question_text = self.get_question_text()
        self.get_mappings()
        self.extract_columns()

    def get_question_text(self) -> str:
        for k in self.meta:
            if k.startswith(self.question_id):
                return self.meta[k]
        return self.question_id

    """def extract_question_text(self, col):
        if 1 in self.df.index and col in self.df.columns:
            try:
                question_text = self.df.loc[1, col]
                if isinstance(question_text, str) and question_text.strip():
                    return question_text.strip()
            except Exception:
                pass
        return None"""

    """def parse_column_id(self, col, question_id):
        remainder = col.replace(question_id + "_", "")
        is_text = remainder.endswith("_TEXT")
        option_id = remainder.replace("_TEXT", "")
        question_text = None

        if is_text and 1 in self.df_raw.index:
            try:
                candidate = self.df_raw.loc[1, col]
                if isinstance(candidate, str) and candidate.strip():
                    question_text = candidate.strip()
            except Exception:
                pass

        return {
            "question_id": question_id,
            "option_id": option_id,
            "is_text": is_text,
            "question_text": question_text,
        }"""

    def parse_column_id(self, col: str, question_id: str) -> dict[str, Any]:
        """
        Parses column names like:
        - DE14_1
        - PL2_3_4
        - DE23_1_2
        And returns row/sub IDs and labels based on metadata.
        """
        result = {
            "question_id": question_id,
            "raw_column": col,
            "row": None,
            "sub": None,
            "row_label": None,
            "sub_label": None,
            "is_text": col.endswith("_TEXT"),
        }

        if col == question_id or col.endswith("_TEXT"):
            return result  # No further parsing needed

        remainder = col.replace(question_id + "_", "")
        parts = remainder.split("_")

        try:
            if self.row_map:
                result["row"] = int(parts[0])
                result["row_label"] = self.row_map.get(
                    result["row"], str(result["row"])
                )
                parts = parts[1:]

            if self.sub_map and parts:
                result["sub"] = int(parts[0])
                result["sub_label"] = self.sub_map.get(
                    result["sub"], str(result["sub"])
                )
        except Exception:
            pass  # fallback to None if parsing fails

        return result

    def get_mappings(self):
        try:
            self.metadata = getattr(question_maps, self.question_id)
        except AttributeError:
            self.metadata = {}

        self.value_map = self.metadata.get("value_map", {})
        self.sub_map = self.metadata.get("sub_map", {})
        self.plot_type = self.metadata.get("plot_type", "continuous")
        self.row_map = self.metadata.get("row_map", {})
        self.xaxis_title = self.metadata.get("xaxis_title", "")
        self.yaxis_title = self.metadata.get("yaxis_title", "")

    def extract_columns(self):
        self.subcolumns = []
        self.text_columns = []
        found_any = False

        for col in self.df.columns:
            if col == self.question_id or col.startswith(f"{self.question_id}_"):
                if col.endswith("_TEXT"):
                    self.text_columns.append(col)
                else:
                    self.subcolumns.append(col)
                found_any = True
            elif found_any:
                break

        self.subcolumns.sort()
        self.text_columns.sort()

        self.responses = (
            self.df[self.subcolumns].dropna(how="all") if self.subcolumns else None
        )

    """def _column_question_text(self, col):
        return self.meta.get(col, {})"""

    @staticmethod
    def _parse_column_id(col: str, question_id: str) -> dict[str, Any]:
        remainder = col.replace(question_id + "_", "")
        is_text = remainder.endswith("_TEXT")
        option_id = remainder.replace("_TEXT", "")
        return {"question_id": question_id, "option_id": option_id, "is_text": is_text}

    def get_labels(self, subcolumns):
        labels = []
        for col in subcolumns:
            if "_" not in col:
                labels.append(col)  # fallback to raw col name
                continue
            parsed = self.parse_column_id(col, self.question_id)

            if parsed["row_label"] and parsed["sub_label"]:
                label = f"{parsed['row_label']} — {parsed['sub_label']}"
            elif parsed["row_label"]:
                label = parsed["row_label"]
            elif parsed["sub_label"]:
                label = parsed["sub_label"]
            else:
                label = col
            """parsed = self.parse_column_id(col, self.question_id)
            option_id = int(parsed["option_id"])
            label = self.sub_map.get(option_id, col)"""
            labels.append(label)
        return labels

    def _get_ordered_label_value_pairs(self, responses: pd.Series) -> tuple[list, list]:
        value_map = self.metadata.get("value_map", {})
        mapped = responses.map(value_map)
        counts = mapped.value_counts()

        ordered_labels = []
        ordered_values = []

        for key in value_map:
            label = value_map[key]
            count = counts.get(label, 0)
            ordered_labels.append(label)
            ordered_values.append(count)

        return ordered_labels, ordered_values

    def get_combined_responses(self):
        if isinstance(self.responses, pd.Series):
            return self.responses
        elif isinstance(self.responses, dict):
            return pd.concat(self.responses.values())
        return pd.Series([], dtype=float)

    def as_frame(self) -> pd.DataFrame:
        """
        Return a tidy DataFrame with at least:
        - ResponseId : respondent key
        - value      : the interpreted answer
        Subclasses may append extra columns (row, unit, etc.).
        Rows with missing data are omitted.
        """
        if "ResponseId" not in self.df.columns:
            raise KeyError("DataFrame must contain a 'ResponseId' column")

        series = self.get_combined_responses()
        if series.empty:
            return pd.DataFrame(columns=["ResponseId", "value"])

        resp_ids = self.df.loc[series.index, "ResponseId"].values
        out = (
            pd.DataFrame({"ResponseId": resp_ids, "value": series.values})
            .dropna(subset=["value"])
            .reset_index(drop=True)
        )
        return out

    # cutoff question title if too long
    @staticmethod
    def truncate_after_first_period(text: str) -> str:
        if not text:
            return "<MISSING QUESTION TITLE>"
        if "?" in text:
            return text.split("?", 1)[0].strip() + "?"
        elif "." in text:
            return text.split(".", 1)[0].strip() + "."
        return text.strip()

    # wrap question title (numeric)
    @staticmethod
    def wrap_text(text: str, width=100) -> str:
        return "<br>".join(textwrap.wrap(text, width=width))

    # wrap labels in case they're too long (single choice)
    @staticmethod
    def wrap_label(label, width=20):
        return "<br>".join(textwrap.wrap(label, width=width))

    def get_ordered_labels_and_values(
        self, counts: pd.Series
    ) -> tuple[list[str], list[int]]:
        value_map = self.metadata.get("value_map", {})
        counts = counts.sort_values(ascending=False)

        ordered_labels = []
        ordered_values = []

        for key in counts.index:
            label = value_map.get(key, key)
            ordered_labels.append(label)
            ordered_values.append(counts[key])

        return ordered_labels, ordered_values

    def get_mean_std_per_subcolumn(self) -> tuple[list[str], list[float], list[float]]:
        labels = self.get_labels(self.subcolumns)
        means = []
        stds = []
        for col in self.subcolumns:
            series = self.responses.get(col, pd.Series(dtype=float)).dropna()
            means.append(series.mean())
            stds.append(series.std())
        return labels, means, stds
