import sys
from pathlib import Path
from IPython.display import IFrame
import question_maps
import textwrap

# cutoff question title if too long
def truncate_after_first_period(text: str) -> str:
    if "." in text:
        parts = text.split(".", 1)
        return parts[0].strip() + "."
    return text.strip()

# wrap question title (numeric)
def wrap_text(text: str, width=90) -> str:
    return "<br>".join(textwrap.wrap(text, width=width))

# wrap labels in case they're too long (single choice)
def wrap_label(label, width=20):
    return "<br>".join(textwrap.wrap(label, width=width))



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
    def __init__(self, question_id: str, df: pd.DataFrame, df_raw: pd.DataFrame, value_transform: Callable[[Any], Any] = None):
        self.question_id = question_id  # e.g., "Q1", "Q2"
        self.df = df  
        self.df_raw = df_raw
        self.value_transform = value_transform  
        
        try:
            self.metadata = getattr(question_maps, question_id)
        except AttributeError:
            self.metadata = {}

        # Default to 'continuous' if plot_type not specified
        self.plot_type = self.metadata.get("plot_type", "continuous")

    def get_labels(self, subcolumns):
        sub_map = self.metadata.get("sub_map", {})
        labels = []
        for col in subcolumns:
            suffix = col.split("_")[-1]
            label = sub_map.get(suffix, col)
            labels.append(label)
        return labels


    def _plot_bar_distribution(self, labels, values, title, summary_stats=None):
        truncated = truncate_after_first_period(title)
        wrapped_title = wrap_text(truncated, width=60)

        total = sum(values)
        percentages = [(v / total) * 100 for v in values]

        fig = px.bar(
            x=labels,
            y=percentages,
            title=wrapped_title,
            text=[f"{round(p, 1)} %" for p in percentages],  # show % in bar labels
            hover_data=None,
        )

        # Set custom marker color, black outline, etc.
        fig.update_traces(
            marker_color='#4876AE',
            marker_line_color='black',
            marker_line_width=1
        )

        # Adjust layout for narrower width, add y-axis label
        fig.update_layout(
            width=1000,         # narrower plot
            height=500,
            margin=dict(r=200),
            xaxis_title="Categories",
            yaxis_title="Percentage (%)"
        )

        if summary_stats:
            fig.add_annotation(
                text=(
                    f"<b>Min:</b> {summary_stats['Min']:.0f}<br>"
                    f"<b>Mean:</b> {summary_stats['Mean']:.0f}<br>"
                    f"<b>Median:</b> {summary_stats['Median']:.0f}<br>"
                    f"<b>Total Responses:</b> {summary_stats['Total Responses']}"
                ),
                x=1.05,
                y=0.5,
                xref="paper",
                yref="paper",
                showarrow=False,
                align="left",
                bordercolor="black",
                borderwidth=1,
                xanchor="left",
                yanchor="middle"
            )

        return fig
    

    def _plot_histogram(self, values, title, summary_stats=None):
        values = pd.to_numeric(values, errors='coerce').dropna()
        truncated = truncate_after_first_period(title)
        wrapped_title = wrap_text(truncated, width=60)

        fig = px.histogram(
            x=values,
            title=wrapped_title,
            histnorm='percent',
            nbins=None,
            range_x=[values.min() - 0.5, values.max() + 0.5]
        )
        fig.update_traces(xbins=dict(size=1))
        fig.update_traces(
            hovertemplate='x=%{x}<br>y=%{y:.2f}%<extra></extra>',
            marker_color='#4876AE',
            marker_line_color='black',
            marker_line_width=1
        )
        fig.update_layout(
            width=1000,
            height=500,
            margin=dict(r=200),
            xaxis_title="",
            yaxis_title="Percentage (%)"
        )

        if summary_stats:
            fig.add_annotation(
                text=(
                    f"<b>Min:</b> {summary_stats['Min']:.0f}<br>"
                    f"<b>Mean:</b> {summary_stats['Mean']:.0f}<br>"
                    f"<b>Median:</b> {summary_stats['Median']:.0f}<br>"
                    f"<b>Total Responses:</b> {summary_stats['Total Responses']}"
                ),
                x=1.05,
                y=0.5,
                xref="paper",
                yref="paper",
                showarrow=False,
                align="left",
                bordercolor="black",
                borderwidth=1,
                xanchor="left",
                yanchor="middle"
            )

        return fig
    

    def _plot_pie_distribution(self, labels, values, title):
        fig = px.pie(names=labels, values=values, title=title)
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(width=600, height=400, margin=dict(r=100))
        return fig




class NumericQuestion(Question):
    """
    Class for a numeric-based survey question.
    DE1, DE10, DE11, DE22
    """
    def __init__(self, question_id: str, df: pd.DataFrame, df_raw: pd.DataFrame, value_transform=None):
        super().__init__(question_id, df, df_raw, value_transform)

        text_candidate = None

        if question_id in df.columns and 1 in df.index:
            possible_text = df.loc[1, question_id]
            if isinstance(possible_text, str) and possible_text.strip():
                text_candidate = possible_text

        self.min_value = 0
        self.max_value = 1000000

        self.subcolumns = sorted(
            [col for col in df.columns if col.startswith(f"{question_id}_")]
        )

        if text_candidate is None and self.subcolumns:
            first_subcol = self.subcolumns[0]
            if first_subcol in df.columns and 1 in df.index:
                possible_text = df.loc[1, first_subcol]
                if isinstance(possible_text, str) and possible_text.strip():
                    text_candidate = possible_text

        if text_candidate:
            self.question_text = text_candidate

        if self.subcolumns:
            self.responses = {
                sub: pd.to_numeric(df[sub], errors="coerce").dropna()
                for sub in self.subcolumns
            }
        else:
            if question_id in df.columns:
                self.responses = pd.to_numeric(df[question_id], errors="coerce").dropna()
            else:
                self.responses = None


    def __repr__(self):
        if self.responses is None or self.responses.empty:
            return f"{self.question_text} — No responses provided."
        return f"{self.question_text} — {len(self.responses)} responses collected."
    

    def distribution(self, display=True):
        if not self.subcolumns and isinstance(self.responses, pd.Series):
            values = self.responses
            summary_stats = {
                "Min": values.min(),
                "Mean": values.mean(),
                "Median": values.median(),
                "Total Responses": len(values)
            }

            if self.plot_type == "continuous":
                fig = self._plot_histogram(values, self.question_text, summary_stats=summary_stats)
            else:
                counts = values.value_counts().sort_index()
                fig = self._plot_bar_distribution(
                    labels=counts.index,
                    values=counts.values,
                    title=self.question_text,
                    summary_stats=summary_stats
                )
        else:
            if not self.subcolumns:
                print(f"No columns found for {self.question_id}")
                return None
            combined_values = pd.concat([self.responses[sub] for sub in self.subcolumns])
            summary_stats = {
                "Min": combined_values.min(),
                "Mean": combined_values.mean(),
                "Median": combined_values.median(),
                "Total Responses": len(combined_values)
            }

            if self.plot_type == "continuous":
                fig = self._plot_histogram(combined_values, self.question_text, summary_stats=summary_stats)
            else:
                means = {}
                for sub in self.subcolumns:
                    means[sub] = self.responses[sub].mean()
                friendly_labels = self.get_labels(self.subcolumns)
                x_vals = friendly_labels
                y_vals = [means[sub] for sub in self.subcolumns]
                fig = self._plot_bar_distribution(x_vals, y_vals, self.question_text, summary_stats=None)

        if display and fig is not None:
            fig.show()
        return fig




class MultipleChoiceQuestion(Question):
    """
    Class for a multiple-choice survey question.
    DE3, DE7, DE9
    """
    def __init__(self, question_id: str, question_text: str, df: pd.DataFrame, response_id: str, answer_mapping: dict):
        super().__init__(question_id, question_text)
        self.responses = []
        self.custom_response = None

        participant_data = df.loc[df["responseId"] == response_id]

        if not participant_data.empty and question_id in participant_data.columns:
            raw_response = str(participant_data[question_id].values[0])
            self.responses = raw_response.split(",") if raw_response else []

        for option in self.responses:
                    text_col = f"{question_id}_{option}_TEXT"
                    if text_col in participant_data.columns:
                        text_value = participant_data[text_col].values[0]
                        if pd.notna(text_value) and text_value.strip():
                            self.custom_response = f"{answer_mapping.get(option, 'Other')}: {text_value.strip()}"
                            break  

    def __repr__(self):
        selected_text = ", ".join(self.responses) if self.responses else "No responses selected"
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

        return {"choice_counts": choice_counts, "custom_responses": self.custom_responses}
    




class SingleChoiceQuestion(Question):
    def __init__(self, question_id: str, df: pd.DataFrame, df_raw: pd.DataFrame, value_transform=None):
        super().__init__(question_id, df, df_raw, value_transform)

        # Attempt to read question text from row index 1 (exact column match)
        text_candidate = None
        if question_id in df.columns and 1 in df.index:
            possible_text = df.loc[1, question_id]
            if isinstance(possible_text, str) and possible_text.strip():
                text_candidate = possible_text

        self.subcolumns = sorted([
            col for col in df.columns
            if col.startswith(f"{question_id}_") and not col.endswith("_TEXT")
        ])

        # If no text found yet, but we do have subcolumns, check the first subcolumn
        if text_candidate is None and self.subcolumns:
            first_subcol = self.subcolumns[0]
            if first_subcol in df.columns and 1 in df.index:
                possible_text = df.loc[1, first_subcol]
                if isinstance(possible_text, str) and possible_text.strip():
                    text_candidate = possible_text

        if text_candidate:
            self.question_text = text_candidate

        # Single column or subcolumns
        if self.subcolumns:
            # Multi-column single-choice is unusual, but can happen if there's an 'other' text col
            # We'll store each subcolumn as numeric codes
            self.responses = {
                sub: pd.to_numeric(df[sub], errors="coerce").dropna()
                for sub in self.subcolumns
            }
        else:
            # Single column
            if question_id in df.columns:
                self.responses = pd.to_numeric(df[question_id], errors="coerce").dropna()
            else:
                self.responses = None
                

    def distribution(self, display=True):
        if not self.subcolumns and isinstance(self.responses, pd.Series):
            value_map = self.metadata.get("value_map", {})
            mapped_responses = self.responses.map(value_map)
            counts = mapped_responses.value_counts()  # no .sort_index() # new
            ordered_labels = []  # new
            ordered_values = []  # new
            for key in value_map:  # new - preserves the order in question_maps
                label = value_map[key]
                c = counts.get(label, 0)
                ordered_labels.append(label)
                ordered_values.append(c)
            if len(ordered_labels) < 4:
                fig = self._plot_pie_distribution(ordered_labels, ordered_values, self.question_text)
            else:
                fig = self._plot_bar_distribution(ordered_labels, ordered_values, self.question_text)
                wrapped_labels = [wrap_label(lbl, width=20) for lbl in ordered_labels]
                fig.update_xaxes(tickvals=ordered_labels, ticktext=wrapped_labels, automargin=True)

        elif self.subcolumns:
            combined = []
            for sub in self.subcolumns:
                combined.extend(self.responses[sub].dropna().tolist())
            combined_series = pd.Series(combined)
            responses_str = combined_series.astype(str)
            value_map = self.metadata.get("value_map", {})
            mapped_responses = combined_series.map(value_map)
            counts = mapped_responses.value_counts().sort_index()
            labels = counts.index.tolist()
            values = counts.values.tolist()
            if len(labels) < 4:
                fig = self._plot_pie_distribution(ordered_labels, ordered_values, self.question_text)
            else:
                fig = self._plot_bar_distribution(ordered_labels, ordered_values, self.question_text)
                wrapped_labels = [wrap_label(lbl, width=20) for lbl in ordered_labels]
                fig.update_xaxes(tickvals=labels, ticktext=wrapped_labels, automargin=True)


        if display and fig is not None:
            fig.show()
        return fig



class MatrixQuestion(Question):
    """
    Class for handling matrix-style survey questions (e.g., child birth year and country).
    Each row represents a subject (e.g., child), and each column represents an attribute (e.g., year, country).
    DE23, PL1, PL2, PL3, PL4, PL6, PL7, PL9
    """

    def __init__(self, question_id: str, question_text: str, df: pd.DataFrame, 
                 response_id: str, value_map: dict = None, row_map: dict = None, 
                 sub_map: dict = None, value_transform: Callable[[Any, str], Any] = None,
                 format: str = "auto"):
        super().__init__(question_id, question_text, value_transform)
        self.responses = {}  
        self.value_map = value_map or {}  
        self.row_map = row_map or {}
        self.sub_map = sub_map or {}
        self.format = format



        participant_data = df.loc[df["responseId"] == response_id]
        for col in participant_data.columns:
            if not col.startswith(f"{question_id}_"):
                continue

            parts = col.strip().split("_")
            if len(parts) < 2:
                continue  # Skip malformed

            if len(parts) == 3:
                if self.format == "row-sub":
                    row_key = parts[1]
                    sub_col = parts[2]
                elif self.format == "attr-row":
                    attr_key = parts[1]
                    row_key = parts[2]
                    sub_col = attr_key
                elif self.format == "auto":
                    # Heuristic: if both look like digits, assume row-sub
                    if parts[1].isdigit() and parts[2].isdigit():
                        row_key = parts[1]
                        sub_col = parts[2]
                    else:
                        row_key = parts[2]
                        sub_col = parts[1]
                else:
                    continue  # Skip malformed or unknown format

            elif len(parts) == 2:
                row_key = parts[1]
                sub_col = None
            else:
                continue  # Still malformed


            raw_value = participant_data[col].values[0]
            if isinstance(raw_value, list):
                raw_value = raw_value[0]


            decoded_row = self.row_map.get(row_key, f"Row {row_key}")
            if self.value_transform:
                decoded_value = self.value_transform(raw_value, sub_col)
            else:
                decoded_value = raw_value



            if sub_col is None:
                # Single-answer (flat)
                self.responses[decoded_row] = decoded_value
            else:
                # Multi-answer (nested dict)
                if decoded_row not in self.responses:
                    self.responses[decoded_row] = {}
                self.responses[decoded_row][sub_col] = decoded_value



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
                response_texts.append(f"{self.row_map.get(row_label, row_label)}: {answers}")

        return f"{self.question_text} Responses:\n" + "\n".join(response_texts)


    def __str__(self):
        return self.__repr__()



"""if __name__ == "__main__":
    
    from parenthood_europe.scripts.parse_survey_data import load_survey_data
    df, df_raw = load_survey_data(file_path = "parenthood_europe/data/Parenthood_test.xlsx")

    q = NumericQuestion("DE2", df, df_raw)
    q.plot_distribution()"""




if __name__ == "__main__":
    from parenthood_europe.scripts.parse_survey_data import load_survey_data
    df, df_raw = load_survey_data(file_path = "parenthood_europe/data/Parenthood_test.xlsx")
    q = SingleChoiceQuestion("DE2", df, df_raw)
    q.plot_distribution()
