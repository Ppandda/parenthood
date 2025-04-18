import sys
from pathlib import Path
from IPython.display import IFrame
import question_maps
import textwrap
import numpy as np

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
        self.question_text = None
        self.get_mappings()
        

    
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


    def extract_columns(self):
        self.subcolumns = sorted([
            col for col in self.df.columns
            if col == self.question_id or col.startswith(f"{self.question_id}_")
        ])
        self.text_columns = sorted([
            col for col in self.df_raw.columns
            if col.startswith(f"{self.question_id}_") and col.endswith("_TEXT")
        ])

        if self.subcolumns:
                self.question_text = self.extract_question_text(self.subcolumns[0])
        elif self.question_id in self.df_raw.columns:
            self.question_text = self.extract_question_text(self.question_id)

        if self.question_text is None:
            self.question_text = self.question_id

        if self.subcolumns:
            self.responses = self.df[self.subcolumns].apply(
                pd.to_numeric, errors="coerce"
            ).dropna(how="all")
        else:
            self.responses = None


    def get_labels(self, subcolumns):
        labels = []
        for col in subcolumns:
            parsed = self.parse_column_id(col, self.question_id)
            option_id = parsed["option_id"]
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
        if self.plot_type == "continuous":
            return self._plot_histogram(values, title, summary_stats)

        elif self.plot_type == "categorical":
            if len(labels) < 4:
                return self._plot_pie_distribution(labels, values, title)
            else:
                return self._plot_bar_distribution(labels, values, title, summary_stats)

        elif self.plot_type == "average":
            return self._plot_bar_distribution_avg(labels, values, title)

        else:
            raise ValueError(f"Unknown plot_type: {self.plot_type}")
        
    
    # cutoff question title if too long
    @staticmethod
    def truncate_after_first_period(text: str) -> str:
        for punct in [".", "?"]:
            if punct in text:
                parts = text.split(punct, 1)
                return parts[0].strip() + punct
        return text.strip()



    # wrap question title (numeric)
    @staticmethod
    def wrap_text(text: str, width=90) -> str:
        return "<br>".join(textwrap.wrap(text, width=width))

    # wrap labels in case they're too long (single choice)
    @staticmethod
    def wrap_label(label, width=20):
        return "<br>".join(textwrap.wrap(label, width=width))



    def plot_distribution_from_counts(self, counts: pd.Series, title: str):
        """
        Plot pie if few options, else bar. Applies label mapping, wrapping, truncation.
        """
        value_map = self.metadata.get("value_map", {})
        
        # Sort counts descending
        counts = counts.sort_values(ascending=False)
        
        ordered_labels = []
        ordered_values = []

        for key in counts.index:
            label = value_map.get(key, key)  # fallback to raw key if mapping missing
            ordered_labels.append(label)
            ordered_values.append(counts[key])

        if len(ordered_labels) < 4:
            return self._plot_pie_distribution(ordered_labels, ordered_values, title)
        else:
            wrapped_labels = [self.wrap_label(lbl, width=20) for lbl in ordered_labels]
            fig = self._plot_bar_distribution(ordered_labels, ordered_values, title)
            if fig is not None:
                fig.update_xaxes(tickvals=ordered_labels, ticktext=wrapped_labels, automargin=True)
            return fig





    def _plot_bar_distribution(self, labels, values, title, summary_stats=None):
        truncated = self.truncate_after_first_period(title)
        wrapped_title = self.wrap_text(truncated, width=60)

        total = sum(values)
        if total == 0:
            print(f"[Warning] Skipping plot for question '{self.question_id}': no responses.")
            return None

        percentages = [(v / total) * 100 for v in values]
        raw_counts = [total * (p / 100) for p in percentages]
        customdata = [int(round(v)) for v in raw_counts]

        # Sort descending by percentage
        sorted_data = sorted(zip(percentages, labels, values, customdata), key=lambda x: x[0], reverse=True)
        percentages, labels, values, customdata = zip(*sorted_data)


        use_horizontal = len(labels) > 10

        if use_horizontal:
            fig = px.bar(
                y=labels,
                x=percentages,
                orientation='h',
                title=wrapped_title,
                text=[f"{round(p, 1)} %" for p in percentages],
                hover_data=None,
                category_orders={"y": list(labels)}

            )
            fig.update_layout(
                width=1000,
                height=max(600, 30 * len(labels)),  
                margin=dict(r=200),
                xaxis_title="Percentage (%)",
                yaxis_title="Categories"
            )
        else:
            fig = px.bar(
                x=labels,
                y=percentages,
                title=wrapped_title,
                text=[f"{round(p, 1)} %" for p in percentages],
                hover_data=None
            )
            fig.update_layout(
                width=1000,
                height=500,
                margin=dict(r=200),
                xaxis_title="Categories",
                yaxis_title="Percentage (%)"
            )


        fig.update_traces(
            customdata=customdata,
            hovertemplate="Total responses: %{customdata}<extra></extra>",
            marker_color="#4876AE",
            marker_line_color="black",
            marker_line_width=1,
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
        values = pd.to_numeric(pd.Series(values), errors="coerce").dropna()
        truncated = self.truncate_after_first_period(title)
        wrapped_title = self.wrap_text(truncated, width=60)

        fig = px.histogram(
            x=values,
            title=wrapped_title,
            histnorm='percent',
            nbins=None,
            range_x=[values.min() - 0.5, values.max() + 0.5]
        )

        counts, bins = np.histogram(values, bins='auto')
        customdata = counts.tolist()

        fig.update_traces(xbins=dict(size=1))
        fig.update_traces(
            marker_color='#4876AE',
            marker_line_color='black',
            marker_line_width=1,
            customdata=customdata,
            hovertemplate="Total responses: %{customdata}<extra></extra>"
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
    
    
    def _plot_bar_distribution_avg(self, labels, values, title):
        fig = px.bar(
            x=labels,
            y=values,
            text=[f"{v:.1f} h" for v in values],
            title=self.wrap_text(title),
            hover_data=None
        )
        try:
            subcolumns = self.subcolumns
            customdata = [len(self.responses[sub].dropna()) for sub in subcolumns]
        except AttributeError:
            customdata = [None] * len(labels)
        fig.update_traces(
            customdata=customdata,
            hovertemplate="Total responses: %{customdata}<extra></extra>"
        )

        wrapped_labels = [self.wrap_label(lbl, width=20) for lbl in labels]
        fig.update_xaxes(
            type="category",             
            tickvals=labels,
            ticktext=wrapped_labels,
            tickangle=0,
            automargin=True
        )

        fig.update_traces(
            marker_color="#4876AE",
            marker_line_color="black",
            marker_line_width=1,
            textposition="auto"
        )

        fig.update_layout(
            title=self.wrap_text(self.truncate_after_first_period(title)),
            width=1000,
            height=500,
            margin=dict(t=80, b=120),
            xaxis_title="Activities",
            yaxis_title="Average hours per day",
            xaxis_tickangle=0
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

        self.min_value = 0
        self.max_value = 1000000

        self.extract_columns()  
        self.extract_numeric_responses()


    def extract_numeric_responses(self):
        if self.subcolumns:
            self.responses = {
                sub: pd.to_numeric(self.df[sub], errors="coerce").dropna()
                for sub in self.subcolumns
            }
        elif self.question_id in self.df.columns:
            self.responses = pd.to_numeric(self.df[self.question_id], errors="coerce").dropna()
        else:
            self.responses = pd.Series([], dtype=float)


    def __repr__(self):
        if self.responses is None or self.responses.empty:
            return f"{self.question_text} — No responses provided."
        return f"{self.question_text} — {len(self.responses)} responses collected."
    

    def distribution(self, display=True):
        if self.responses is None or len(self.responses) == 0:
            print(f"[Warning] Skipping plot for question '{self.question_id}': no responses.")
            return None

        plot_type = self.metadata.get("plot_type", "continuous")

        if not self.subcolumns:
            values = self.get_combined_responses()
            summary_stats = {
                "Min": values.min(),
                "Mean": values.mean(),
                "Median": values.median(),
                "Total Responses": len(values)
            }

            if plot_type == "continuous":
                fig = self._plot_histogram(values, self.question_text, summary_stats=summary_stats)

            elif plot_type == "categorical":
                counts = values.value_counts().sort_index()
                fig = self._plot_bar_distribution(
                    labels=counts.index,
                    values=counts.values,
                    title=self.question_text,
                    summary_stats=summary_stats,
                )
            else:
                raise ValueError(f"Unknown plot_type: {plot_type}")

        else:
            # For subcolumns: combine values from each subcolumn
            combined_values = pd.concat([self.responses[sub] for sub in self.subcolumns])
            summary_stats = {
                "Min": combined_values.min(),
                "Mean": combined_values.mean(),
                "Median": combined_values.median(),
                "Total Responses": len(combined_values)
            }

            if plot_type == "continuous":
                fig = self._plot_histogram(combined_values, self.question_text, summary_stats=summary_stats)

            elif plot_type == "categorical":
                means = {sub: self.responses[sub].mean() for sub in self.subcolumns}
                x_vals = self.get_labels(self.subcolumns)
                y_vals = [means[sub] for sub in self.subcolumns]

                fig = self._plot_bar_distribution_avg(
                    x_vals,
                    y_vals,
                    self.question_text
                )
            else:
                raise ValueError(f"Unknown plot_type: {plot_type}")

        if display and fig is not None:
            fig.show()
        return fig 



class MultipleChoiceQuestion(Question):
    """
    Class for a multiple-choice survey question.
    DE3, DE7, DE9
    """
    def __init__(self, question_id: str, df: pd.DataFrame, df_raw: pd.DataFrame, value_transform=None):
        super().__init__(question_id, df, df_raw, value_transform)
        self.extract_columns()

    def extract_columns(self):
        super().extract_columns()  
        if self.question_id in self.df.columns:
            raw_series = self.df[self.question_id].dropna().astype(str)
            self.responses = raw_series
            self.subcolumns = [self.question_id]  



    def get_flattened_responses(self) -> pd.Series:
        combined = []
        for row in self.responses.dropna():
            combined.extend(row.split(","))
        return pd.Series(combined, dtype=str)


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

    
    
    def distribution(self, display=True):
        combined_series = self.get_flattened_responses()
        mapped = combined_series.map(self.value_map)
        counts = mapped.value_counts()

        title = self.truncate_after_first_period(self.question_text)
        fig = self.plot_distribution_from_counts(counts, title)

        if display and fig is not None:
            fig.show()

        return fig








class SingleChoiceQuestion(Question):
    def __init__(self, question_id: str, df: pd.DataFrame, df_raw: pd.DataFrame, value_transform=None):
        super().__init__(question_id, df, df_raw, value_transform)

        #self.extract_columns()
        #self.extract_string_responses()

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

    def extract_string_responses(self):
        if self.subcolumns:
            combined = []
            for sub in self.subcolumns:
                values = self.df[sub].dropna().astype(str).tolist()
                combined.extend(values)
            self.responses = pd.Series(combined)
        elif self.question_id in self.df.columns:
            self.responses = self.df[self.question_id].dropna().astype(str)
        else:
            self.responses = pd.Series([], dtype=str)


    def distribution(self, display=True):
        if not self.subcolumns and isinstance(self.responses, pd.Series):
            value_map = self.metadata.get("value_map", {})
            mapped_responses = self.responses.map(value_map)
            counts = mapped_responses.value_counts()  # no .sort_index() # new
            ordered_labels = []  # new
            ordered_values = []  # new
            for key in value_map:  # new – preserves the order in question_maps
                label = value_map[key]
                c = counts.get(label, 0)
                ordered_labels.append(label)
                ordered_values.append(c)
            if len(ordered_labels) < 4:
                fig = self._plot_pie_distribution(ordered_labels, ordered_values, self.question_text)
            else:
                fig = self._plot_bar_distribution(ordered_labels, ordered_values, self.question_text)
                wrapped_labels = [self.wrap_label(lbl, width=20) for lbl in ordered_labels]
                fig.update_xaxes(tickvals=ordered_labels, ticktext=wrapped_labels, automargin=True)

        elif self.subcolumns:
            combined = []
            for sub in self.subcolumns:
                combined.extend(self.responses[sub].dropna().tolist())
            combined_series = pd.Series(combined)
            responses_str = combined_series.astype(str)
            value_map = self.metadata.get("value_map", {})
            mapped_responses = responses_str.map(value_map)
            counts = mapped_responses.value_counts().sort_index()
            labels = counts.index.tolist()
            values = counts.values.tolist()
            if len(labels) < 4:
                fig = self._plot_pie_distribution(ordered_labels, ordered_values, self.question_text)
            else:
                ordered_labels = labels
                fig = self._plot_bar_distribution(ordered_labels, values, self.question_text)
                wrapped_labels = [self.wrap_label(lbl, width=20) for lbl in ordered_labels]
                fig.update_xaxes(tickvals=ordered_labels, ticktext=wrapped_labels, automargin=True)

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
