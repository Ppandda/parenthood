import pandas as pd
import numpy as np
from typing import Callable, Any, Optional
from transform_time import months_to_weeks, unified_time_to_weeks


class Question:
    """
    Base class for a survey question.
    """
    def __init__(self, question_id: str, question_text: str, value_transform: Callable[[Any], Any] = None):
        self.question_id = question_id  # e.g., "Q1", "Q2"
        self.question_text = question_text  # the question
        self.value_transform = value_transform  # Function to transform raw values (e.g., months → weeks)

    
    #def __repr__(self):
    #    return f"Question({self.question_id}, {self.question_text[:30]}..., {len(self.responses)} responses)"    


class NumericQuestion(Question):
    """
    Class for a numeric-based survey question.
    DE1, DE10, DE11, DE22
    """
    def __init__(self, question_id: str, question_text: str, df: pd.DataFrame, response_id: str):
        super().__init__(question_id, question_text)
        self.responses = None
        self.min_value = 0
        self.max_value = 10000000

        participant_data = df.loc[df["responseId"] == response_id, question_id]

        if not participant_data.empty:
            self.response = participant_data.values[0]

        if self.response is None or pd.isna(self.response):
            self.response = 0

    def __repr__(self):
        if self.response is None:
            return f"{self.question_text} No answer provided."
        return f"{self.question_text} Answer: {self.response}."



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

    def __init__(self, question_id: str, question_text: str, df: pd.DataFrame, response_id: str, value_map: dict = None, value_transform: Callable[[Any], Any] = None, unit_hint: Optional[str] = None):
        super().__init__(question_id, question_text)
        self.response = None  # Numeric response
        self.extra_texts = {}  # Dictionary storing any additional text 
        self.value_map = value_map or {}
        self.value_transform = value_transform
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
        extra_info = next(iter(self.extra_texts.values()), "")  
        return f"{self.question_text} Answer: {self.response} {extra_info}".strip()



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

if __name__ == "__main__":
    # Simulating survey data
    data = {
        "responseId": ["R_999999"],
        "CS3_1": [1],   # Albania – Very good
        "CS3_2": [2],   # Andorra – Good
        "CS3_3": [3],   # Armenia – Bad
        "CS3_4": [4],   # Austria – Very bad
        "CS3_5": [5],   # Azerbaijan – Don't know
    }

    df = pd.DataFrame(data)
    response_id = "R_999999"

    value_map = {
        "1": "Very good policies",
        "2": "Good policies",
        "3": "Bad policies",
        "4": "Very bad policies",
        "5": "Don't know"
    }

    row_map = {
        "1": "Albania",
        "2": "Andorra",
        "3": "Armenia",
        "4": "Austria",
        "5": "Azerbaijan"
    }

    cs3_question = MatrixQuestion(
        question_id="CS3",
        question_text="Rate the general parental policies of the European countries you know.",
        df=df,
        response_id=response_id,
        row_map=row_map,
        value_map=value_map,
        format="row"
    )

    print(cs3_question)