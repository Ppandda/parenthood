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
        df_raw: pd.DataFrame,
        value_transform: Callable[[Any], Any] = None,
    ):
        self.question_id = question_id  # e.g., "Q1", "Q2"
        self.df = df
        self.df_raw = df_raw
        self.value_transform = value_transform
        self.question_text = None
        self.get_mappings()
        self.extract_columns()

    def extract_question_text(self, col):
        """
        Extracts the survey question text from df row 1 for the given column.
        For example: "In what year were you born?" from df.loc[1, "DE1"].

        Returns None if no valid text is found.
        """
        if 1 in self.df.index and col in self.df.columns:
            try:
                question_text = self.df.loc[1, col]
                if isinstance(question_text, str) and question_text.strip():
                    return question_text.strip()
            except Exception:
                pass
        return None

    def parse_column_id(self, col, question_id):
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
        }

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

        for col in self.df_raw.columns:
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

        if self.subcolumns:
            self.question_text = self.extract_question_text(self.subcolumns[0])
        elif self.question_id in self.df_raw.columns:
            self.question_text = self.extract_question_text(self.question_id)
        else:
            self.question_text = self.question_id

        self.responses = (
            self.df[self.subcolumns].dropna(how="all") if self.subcolumns else None
        )

    def get_labels(self, subcolumns):
        labels = []
        for col in subcolumns:
            if "_" not in col:
                labels.append(col)  # fallback to raw col name
                continue
            parsed = self.parse_column_id(col, self.question_id)
            option_id = int(parsed["option_id"])
            label = self.sub_map.get(option_id, col)
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

    def _choose_and_plot(self, labels, values, title, summary_stats=None):
        truncated = self.truncate_after_first_period(title)
        wrapped_title = self.wrap_text(truncated, width=80)

        if self.plot_type == "continuous":
            return self._plot_histogram(values, wrapped_title, summary_stats)

        elif self.plot_type == "categorical":
            if len(labels) < 3:
                return self._plot_pie_distribution(labels, values, wrapped_title)
            else:
                orientation = "h" if len(labels) > 7 else "v"
                return self._plot_bar_distribution(
                    labels,
                    values,
                    wrapped_title,
                    summary_stats,
                    orientation=orientation,
                )

        elif self.plot_type == "average":
            if hasattr(self, "subcolumns") and self.subcolumns:
                labels, means, stds = self.get_mean_std_per_subcolumn()
                return self._plot_bar_distribution_avg(
                    labels, means, wrapped_title, error_y=stds
                )
            else:
                orientation = "h" if len(labels) > 7 else "v"
                return self._plot_bar_distribution(
                    labels,
                    values,
                    wrapped_title,
                    summary_stats,
                    orientation=orientation,
                )

        else:
            raise ValueError(f"Unknown plot_type: {self.plot_type}")

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

    def _plot_bar_distribution(
        self, labels, values, title, summary_stats=None, orientation="v"
    ):
        if not values or sum(values) == 0:
            print(
                f"[Warning] Skipping plot for question '{self.question_id}': no responses."
            )
            return None

        percentages = [(v / sum(values)) * 100 for v in values]
        raw_counts = [sum(values) * (p / 100) for p in percentages]
        customdata = [int(round(v)) for v in raw_counts]

        # Sort descending
        sorted_data = sorted(
            zip(percentages, labels, values, customdata),
            key=lambda x: x[0],
            reverse=True,
        )
        percentages, labels, values, customdata = zip(*sorted_data)
        wrapped_labels = (
            labels
            if orientation == "h"
            else [self.wrap_label(label, width=20) for label in labels]
        )

        # Axis logic
        category_axis = "y" if orientation == "h" else "x"
        category_orders = {category_axis: list(wrapped_labels)}

        if orientation == "h":
            fig = px.bar(
                y=wrapped_labels,
                x=percentages,
                orientation="h",
                title=title,
                text=[f"{round(p, 1)} %" for p in percentages],
                hover_data=None,
                category_orders=category_orders,
            )
        else:
            fig = px.bar(
                x=wrapped_labels,
                y=percentages,
                orientation="v",
                title=title,
                text=[f"{round(p, 1)} %" for p in percentages],
                hover_data=None,
                category_orders=category_orders,
            )

        fig.update_layout(
            width=1000,
            height=max(600, 30 * len(labels)) if orientation == "h" else 500,
            margin=dict(r=200),
            xaxis_title="Percentage (%)" if orientation == "h" else "",
            yaxis_title="" if orientation == "h" else "Percentage (%)",
        )

        fig.update_traces(
            customdata=customdata,
            hovertemplate="Total responses: %{customdata}<extra></extra>",
            marker_color="#4876AE",
            marker_line_color=None,
            marker_line_width=1,
        )

        return fig

    def _plot_histogram(self, values, title, summary_stats=None):
        values = pd.to_numeric(pd.Series(values), errors="coerce").dropna()
        truncated = self.truncate_after_first_period(title)
        wrapped_title = self.wrap_text(truncated, width=60)

        counts = values.value_counts().sort_index()  # exact years
        percentages = counts / counts.sum() * 100

        x = counts.index  # e.g., 1965, 1966, 1967...
        y = percentages

        customdata = list(zip(x, counts))

        x_label = self.metadata.get("x_label", "Value")
        hovertemplate = f"{x_label}: %{{customdata[0]}}<br>Total responses: %{{customdata[1]}}<extra></extra>"

        # Manually construct the bar chart
        fig = go.Figure(
            data=[
                go.Bar(
                    x=x,
                    y=y,
                    customdata=customdata,
                    hovertemplate=hovertemplate,
                    marker_color="#4876AE",
                    marker_line_color="black",
                    marker_line_width=1,
                )
            ]
        )

        fig.update_layout(
            title=wrapped_title,
            width=1000,
            height=500,
            margin=dict(r=200),
            xaxis_title=self.metadata.get("x_label", "Value"),
            yaxis_title="Percentage (%)",
        )
        return fig

    def get_mean_std_per_subcolumn(self) -> tuple[list[str], list[float], list[float]]:
        labels = self.get_labels(self.subcolumns)
        means = []
        stds = []
        for col in self.subcolumns:
            series = self.responses.get(col, pd.Series(dtype=float)).dropna()
            means.append(series.mean())
            stds.append(series.std())
        return labels, means, stds

    def _plot_bar_distribution_avg(self, labels, values, title, error_y=None):
        fig = px.bar(
            x=labels,
            y=values,
            error_y=error_y,
            text=[f"{v:.1f} h" for v in values],
            title=title,
            hover_data=None,
        )
        try:
            subcolumns = self.subcolumns
            customdata = [len(self.responses[sub].dropna()) for sub in subcolumns]
        except AttributeError:
            customdata = [None] * len(labels)
        fig.update_traces(
            customdata=customdata,
            hovertemplate="Average: %{y:.1f} h<br>Total responses: %{customdata}<extra></extra>",
        )

        wrapped_labels = [self.wrap_label(lbl, width=20) for lbl in labels]
        fig.update_xaxes(
            type="category",
            tickvals=labels,
            ticktext=wrapped_labels,
            tickangle=0,
            automargin=True,
        )

        fig.update_traces(
            marker_color="#4876AE",
            marker_line_color="black",
            marker_line_width=1,
            textposition="auto",
        )

        fig.update_layout(
            title=title,
            width=1000,
            height=500,
            margin=dict(t=80, b=120),
            xaxis_title=self.xaxis_title,
            yaxis_title=self.yaxis_title,
            xaxis_tickangle=0,
        )

        return fig

    def _plot_pie_distribution(self, labels, values, title):
        truncated = self.truncate_after_first_period(title)
        wrapped_title = self.wrap_text(truncated, width=80)

        fig = px.pie(names=labels, values=values, title=wrapped_title)
        fig.update_traces(textposition="inside", textinfo="percent+label")
        fig.update_layout(width=600, height=400, margin=dict(r=100))
        return fig
