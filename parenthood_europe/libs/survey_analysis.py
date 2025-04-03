import sys
from pathlib import Path
from IPython.display import IFrame
import question_maps


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
        if question_id in df.columns:
            self.question_text = df.loc[1, question_id]
        else:
            self.question_text = f"{question_id} (multi-column or missing label)"

        self.value_map = getattr(question_maps, question_id, {}).get("value_map", {})



    def _plot_bar_distribution(self, labels, percentages, title, summary_stats=None):
        fig = px.bar(
            x=labels,
            y=percentages,
            title=title,
            labels={"y": "Percentage (%)"},
            hover_data=None,
        )

        fig.update_traces(
            marker=dict(color="#4E74BC", line=dict(color="black", width=1))
        )

        fig.update_layout(
            width=800,
            height=600,
            bargap=0.05,
            margin=dict(b=180) if summary_stats else dict(b=80),
            xaxis=dict(title=None, tickmode="auto"),
            yaxis_title="Percentage (%)"
        )

        fig.update_xaxes(tickangle=45, tickmode='auto')

        if summary_stats:
            fig.add_annotation(
                text="<br>".join([
                    f"Min: {summary_stats['Min']}",
                    f"Max: {summary_stats['Max']}",
                    f"Mean: {summary_stats['Mean']}",
                    f"Median: {summary_stats['Median']}",
                    f"Total Responses: {summary_stats['Total Responses']}"
                ]),
                xref="paper", yref="paper",
                x=0, y=-0.5,
                showarrow=False,
                align="left",
                font=dict(size=12),
                bordercolor="black",
                borderwidth=1
            )

        return fig



class NumericQuestion(Question):
    """
    Class for a numeric-based survey question.
    DE1, DE10, DE11, DE22
    """
    def __init__(self, question_id: str, df: pd.DataFrame, df_raw: pd.DataFrame):
        super().__init__(question_id, df, df_raw)
        self.min_value = 0
        self.max_value = 1000000

        self.subcolumns = sorted(
            [col for col in df.columns if col.startswith(f"{question_id}_")]
        )

        if self.subcolumns:
            self.responses = {
                subcol: pd.to_numeric(df[subcol], errors="coerce").dropna()
                for subcol in self.subcolumns
            }
        else:
            self.responses = pd.to_numeric(df[question_id], errors="coerce").dropna()
            self.subcolumns = None
        


    def __repr__(self):
        if self.responses is None or self.responses.empty:
            return f"{self.question_text} — No responses provided."
        return f"{self.question_text} — {len(self.responses)} responses collected."


    def plot_distribution(self, display=True):
        figs = []
        total_participants = self.df.shape[0]

        if isinstance(self.responses, dict):  # Multi-column case (e.g. DE10)
            for subcol, responses in self.responses.items():
                if responses.empty:
                    continue

                total_respondents = len(responses)
                value_counts = responses.value_counts().sort_index()
                percentages = (value_counts / total_respondents * 100).round(2)

                summary_stats = {
                    "Min": int(responses.min()),
                    "Max": int(responses.max()),
                    "Mean": round(responses.mean(), 2),
                    "Median": int(responses.median()),
                    "Total Responses": total_respondents
                }

                label_suffix = subcol.split("_")[-1]
                label = self.value_map.get("sub_map", {}).get(label_suffix, subcol)

                print(f"{label}: {total_respondents} respondents out of {total_participants} participants.")

                fig = self._plot_bar_distribution(
                    labels=value_counts.index,
                    percentages=percentages,
                    title=f"{self.question_text} – {label}",
                    summary_stats=summary_stats
                )
                if display:
                    fig.show()
                figs.append(fig)

        else:  # Single-column case (e.g. DE1)
            responses = self.responses
            if responses.empty:
                print("No responses to plot.")
                return

            total_respondents = len(responses)
            value_counts = responses.value_counts().sort_index()
            percentages = (value_counts / total_respondents * 100).round(2)

            summary_stats = {
                "Min": int(responses.min()),
                "Max": int(responses.max()),
                "Mean": round(responses.mean(), 2),
                "Median": int(responses.median()),
                "Total Responses": total_respondents
            }

            print(f"{total_respondents} respondents out of {total_participants} participants.")

            fig = self._plot_bar_distribution(
                labels=value_counts.index,
                percentages=percentages,
                title=self.question_text,
                summary_stats=summary_stats
            )
            if display:
                fig.show()
            figs.append(fig)

        return figs if len(figs) > 1 else figs[0]


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
    """
    Class for a single-choice survey question.
    Handles:
    - Basic single-choice answers (stored as numbers).
    - Additional text responses if applicable (found dynamically).
    DE2, DE4, DE5, DE6, DE8, DE12, DE14, DE15, DE16, DE17, DE18, DE19, DE20, DE21, PL5, PL8,
    """
    def __init__(
        self,
        question_id: str,
        df: pd.DataFrame,
        df_raw: pd.DataFrame,
        value_transform: Callable[[Any], Any] = None,
        unit_hint: Optional[str] = None,
    ):
        super().__init__(question_id, df, df_raw, value_transform)
        self.unit_hint = unit_hint

        # Clean up responses
        self.responses = pd.to_numeric(self.df[question_id], errors="coerce").dropna()

        # Optional: collect additional free text responses (like for "Other")
        self.extra_texts = {}
        for col in df.columns:
            if col.startswith(f"{question_id}_") and col.endswith("_TEXT"):
                option_number = col.split("_")[1]
                text_series = df[col].dropna().astype(str)
                if not text_series.empty:
                    self.extra_texts[option_number] = text_series

    def __repr__(self):
        if self.responses.empty:
            return f"{self.question_text} – No responses provided."
        return f"{self.question_text} – {len(self.responses)} responses collected."

    def plot_distribution(self, display=True):
        value_counts = self.responses.value_counts().sort_index()
        total = len(self.responses)
        percentages = (value_counts / total * 100).round(2)

        # Decode value_map (gender 1 = woman, etc.)
        labels = [
            self.value_map.get(str(int(x)), f"Option {int(x)}")
            for x in value_counts.index
        ]

        print(f"{total} respondents out of {self.df.shape[0]} participants provided a response.")

        fig = self._plot_bar_distribution(
            labels=labels,
            percentages=percentages,
            title=self.question_text,
        )

        if display:
            fig.show()
        return fig


        """
        def __init__(self, question_id: str, df: pd.DataFrame, value_map: dict = None, value_transform: Callable[[Any], Any] = None, unit_hint: Optional[str] = None):
        super().__init__(question_id, df, df_raw, value_transform)
        #self.response = None  # Numeric response
        #self.extra_texts = {}  # Dictionary storing any additional text 
        #self.value_map = value_map or {}
        #self.value_transform = value_transform
        self.unit_hint = unit_hint
        
        participant_data = df.loc[df["responseId"] == response_id]

        if not participant_data.empty and question_id in participant_data.columns:
            self.response = str(participant_data[question_id].values[0])

        for col in participant_data.columns:
            if col.startswith(f"{question_id}_") and col.endswith("_TEXT"):
                option_number = col.split("_")[1]

                if option_number == self.response:  
                    text_value = participant_data[col].values[0]
                    if isinstance(text_value, list) or isinstance(text_value, np.ndarray):
                        if len(text_value) > 0:
                            text_value = text_value[0]

                    if pd.notna(text_value): 
                        self.extra_texts[option_number] = text_value.strip()

        if (
            self.value_transform 
            and self.unit_hint 
            and self.response in self.extra_texts
        ):
            try:
                numeric_val = float(self.extra_texts[self.response])
                transformed_val = self.value_transform(numeric_val, self.unit_hint)
                self.extra_texts[self.response] = str(transformed_val)
            except (ValueError, TypeError):
                pass  # gracefully fall back if parsing or transformation fails


        def __repr__(self):
            if self.responses.empty:
                return f"{self.question_text} – No responses provided."
            return f"{self.question_text} – {len(self.responses)} responses collected."
   


    def plot_distribution(self):
        if self.df[self.question_id].isnull().all():
            print("No valid response data available.")
            return

        responses = pd.to_numeric(self.df[self.question_id], errors="coerce").dropna()
        if responses.empty:
            print("No responses to plot.")
            return

        total_respondents = len(responses)
        total_participants = self.df.shape[0]
        print(f"{total_respondents} respondents out of {total_participants} participants provided a response.")

        if self.value_map:
            mapped = responses.map(lambda x: self.value_map.get(str(int(x)), f"Option {int(x)}"))
        else:
            mapped = responses.astype(str)

        value_counts = mapped.value_counts()
        percentages = (value_counts / total_respondents * 100).round(2)

        # Optional: preserve original value_map order
        if self.value_map:
            label_order = [self.value_map[k] for k in sorted(self.value_map.keys(), key=int)]
            percentages = percentages.reindex(label_order).dropna()

        fig = self._plot_bar_distribution(
            labels=percentages.index,
            percentages=percentages.values,
            title=self.question_text
        )

        fig.show()
        return fig"""




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
