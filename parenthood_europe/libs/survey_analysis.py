import pandas as pd

class Question:
    """
    Base class for a survey question.
    """
    def __init__(self, question_id: str, question_text: str):
        self.question_id = question_id  # e.g., "Q1", "Q2"
        self.question_text = question_text  # Full text of the question
    
    #def __repr__(self):
    #    return f"Question({self.question_id}, {self.question_text[:30]}..., {len(self.responses)} responses)"



class TextQuestion(Question):
    """
    Class for a text-based survey question.
    """
    def __init__(self, question_id: str, question_text: str, responses: list):
        super().__init__(question_id, question_text)
        self.responses = responses
    


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


class LikertQuestion(Question):
    """
    Class for a Likert-scale survey question.
    """
    def __init__(self, question_id: str, question_text: str, responses: list, scale_labels: list):
        super().__init__(question_id, question_text)
        self.scale_labels = scale_labels  # e.g., ["Strongly Disagree", "Disagree", "Neutral", "Agree", "Strongly Agree"]
        self.responses = responses
    
    def analyze(self):
        """
        Analyze the Likert-scale responses.
        """
        # Count the number of responses for each scale label
        scale_counts = {label: 0 for label in self.scale_labels}
        for response in self.responses:
            scale_counts[response] += 1
        
        return scale_counts
    


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
    DE2, DE4, DE5, DE6, DE8, DE12, DE14, DE15, DE16, DE17, DE18, DE19, DE20, DE21
    """

    def __init__(self, question_id: str, question_text: str, df: pd.DataFrame, response_id: str):
        super().__init__(question_id, question_text)
        self.response = None  # Numeric response
        self.extra_texts = {}  # Dictionary storing any additional text 

        participant_data = df.loc[df["responseId"] == response_id]

        if not participant_data.empty and question_id in participant_data.columns:
            self.response = str(participant_data[question_id].values[0])

        for col in participant_data.columns:
            if col.startswith(f"{question_id}_") and col.endswith("_TEXT"):
                option_number = col.split("_")[1]

                if option_number == self.response:  
                    text_value = participant_data[col].values[0]
                    if pd.notna(text_value): 
                        self.extra_texts[option_number] = text_value.strip()


    def __repr__(self):
        extra_info = next(iter(self.extra_texts.values()), "")  
        return f"{self.question_text} Answer: {self.response} {extra_info}".strip()



class MatrixQuestion(Question):
    """
    Class for handling matrix-style survey questions (e.g., child birth year and country).
    Each row represents a subject (e.g., child), and each column represents an attribute (e.g., year, country).
    DE23, PL1
    """

    def __init__(self, question_id: str, question_text: str, df: pd.DataFrame, response_id: str, value_map: dict = None, row_map: dict = None, sub_map: dict = None):
        super().__init__(question_id, question_text)
        self.responses = {}  
        self.value_map = value_map or {}  
        self.row_map = row_map or {}
        self.sub_map = sub_map or {}


        participant_data = df.loc[df["responseId"] == response_id]
        for col in participant_data.columns:
            if not col.startswith(f"{question_id}_"):
                continue

            parts = col.strip().split("_")
            if len(parts) < 2:
                continue  # Skip malformed

            if len(parts) == 3:
                attr_key = parts[1]
                row_key = parts[2]
                sub_col = attr_key
            elif len(parts) == 2:
                row_key = parts[1]
                sub_col = None
            else:
                continue  # Still malformed


            raw_value = participant_data[col].values[0]
            if isinstance(raw_value, list):
                raw_value = raw_value[0]


            decoded_row = self.row_map.get(row_key, f"Row {row_key}")
            decoded_value = self.value_map.get(str(raw_value), str(raw_value))

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
                items = [f"{self.sub_map.get(k, k)}: {v}" for k, v in answers.items()]
                response_texts.append(f"{row_label}: " + ", ".join(items))
            else:
                # Flat (DE5)
                response_texts.append(f"{self.row_map.get(row_label, row_label)}: {answers}")

        return f"{self.question_text} Responses:\n" + "\n".join(response_texts)


    def __str__(self):
        return self.__repr__()




"""
if __name__ == "__main__":
    text_question = SingleChoiceQuestion(
        question_id="DE7",
        question_text="Whats your current position?",
        responses = ["I am tenured (please, indicate the year you received tenure, e.g., 2010)", "2015"] #["Other (please, specify)", "blabliblupp"] 
        #custom_responses = ["A mix of them all"]
    )


    print(text_question)"""

""" # multiple testcases

if __name__ == "__main__":
    # Simulating survey data in a DataFrame
    data = {
        "responseId": ["R_123456"],  
        "DE2": ["1"],  # Gender identity (numeric)
        "DE4": ["2"],  # Economic situation (numeric)
        "DE5": ["25"],  # Country lived in childhood (numeric)
        "DE6": ["42"],  # Current residence (numeric)
        "DE8": ["5"],  # "I am tenured" (numeric response)
        "DE8_4_TEXT": ["2015"],  # Extra field for tenure year
        "DE8_5_TEXT": ["Independent researcher"],  # Extra field for "Other"
    }

    df = pd.DataFrame(data)

    response_id = "R_123456"

    text_question = SingleChoiceQuestion(
        question_id="DE8",
        question_text="What is your current academic status?",
        df=df,
        response_id=response_id
    )

    print(text_question)"""


""" # testcase DE7

if __name__ == "__main__":
    # Simulating survey data in a DataFrame
    data = {
        "responseId": ["R_123456"],  # Unique participant ID
        "DE7": ["1,3,5"],  # Multiple selections stored as comma-separated values
        "DE7_5_TEXT": ["I identify differently"],  # Custom text for "Self describe"
    }

    df = pd.DataFrame(data)

    response_id = "R_123456"

    # Instantiate MultipleChoiceQuestion for a sample multiple-choice question
    multi_question = MultipleChoiceQuestion(
        question_id="DE7",
        question_text="What is your origin?",
        df=df,
        response_id=response_id
    )

    print(multi_question)"""


 
"""# testcase DE9

if __name__ == "__main__":
    # Simulating survey data in a DataFrame
    data = {
        "responseId": ["R_123456"],
        "DE9": ["Austria, France, Germany"],  # Multiple selected countries
        "DE9_TEXT": [""]  # Empty if no "Other" text input
    }

    df = pd.DataFrame(data)

    response_id = "R_123456"

    # Instantiate the MultipleChoiceQuestion class
    affiliation_question = MultipleChoiceQuestion(
        question_id="DE9",
        question_text="Select ALL the European countries where you have been affiliated in academia.",
        df=df,
        response_id=response_id
    )

    # Print output
    print(affiliation_question)"""


    # modified testcase with text versatility DE9

"""if __name__ == "__main__":
    # Simulating survey data in a DataFrame
    data = {
        "responseId": ["R_123456"],
        "DE9": ["1,2,3"],  # User selects "Other" in addition to Austria & France
        "DE9_3_TEXT": ["I have been affiliated in an unlisted country"]  # User provides custom text
    }

    df = pd.DataFrame(data)

    response_id = "R_123456"

    # Define an answer mapping where "10" represents "Other" (or "Self Describe")
    answer_mapping_DE9 = {
        "1": "Austria",
        "2": "France",
        "3": "Other"
    }

    # Instantiate the MultipleChoiceQuestion class
    affiliation_question = MultipleChoiceQuestion(
        question_id="DE9",
        question_text="Select ALL the European countries where you have been affiliated in academia.",
        df=df,
        response_id=response_id,
        answer_mapping=answer_mapping_DE9
    )

    # Print output
    print(affiliation_question)"""


""" # testcase DE10

if __name__ == "__main__":
    # Simulating survey data for time allocation
    data = {
        "responseId": ["R_123456"],
        "DE10_1": [8],  # Career-focused activities
        "DE10_3": [4],  # Leisure (Skipping DE10_2)
        "DE10_4": [6]   # Sleep
    }

    df = pd.DataFrame(data)

    response_id = "R_123456"

    career_question = NumericQuestion(
        question_id="DE10_1",
        question_text="How many hours did you spend on career-focused activities?",
        df=df,
        response_id=response_id
    )

    leisure_question = NumericQuestion(
        question_id="DE10_3",
        question_text="How many hours did you spend on leisure?",
        df=df,
        response_id=response_id
    )

    missing_question = NumericQuestion(
        question_id="DE10_4",  # This column does not exist in df
        question_text="How many hours did you spend on household work?",
        df=df,
        response_id=response_id
    )

    print(career_question)
    print(leisure_question)
    print(missing_question)"""


""" # testcase DE14

if __name__ == "__main__":
    
    data = {
    "responseId": ["R_789123"],
    "DE13_1": ["1"],  # Parent 1: Woman
    "DE13_2": ["2"],  # Parent 2: Man
}

df = pd.DataFrame(data)

response_id = "R_789123"

# Creating SingleChoiceQuestion instances for each parent
parent1_question = SingleChoiceQuestion(
    question_id="DE13_1",
    question_text="What is the gender identity of Parent 1?",
    df=df,
    response_id=response_id
)

parent2_question = SingleChoiceQuestion(
    question_id="DE13_2",
    question_text="What is the gender identity of Parent 2?",
    df=df,
    response_id=response_id
)

# Printing results
print(parent1_question)
print(parent2_question)"""



"""# testcase DE15, DE16

data = {
    "responseId": ["R_123456"],
    "DE14_1": [3],  # Parent 1 selected option 3
    "DE14_2": [6]   # Parent 2 selected option 7
}

df = pd.DataFrame(data)
response_id = "R_123456"

parent1_question = SingleChoiceQuestion(
    question_id="DE14_1",
    question_text="Which category best describes Parent 1?",
    df=df,
    response_id=response_id
)

parent2_question = SingleChoiceQuestion(
    question_id="DE14_2",
    question_text="Which category best describes Parent 2?",
    df=df,
    response_id=response_id
)

print(parent1_question)
print(parent2_question)"""


"""# testcase DE18

if __name__ == "__main__":
    data = {
        "responseId": ["R_123456"],
        "DE16": [9],  # Respondent selected "Other (please specify)" (assuming it's encoded as 9)
        "DE16_8_TEXT": ["Freelance consultant"],  # The custom response provided
    }

    df = pd.DataFrame(data)

    response_id = "R_123456"

    # Creating the SingleChoiceQuestion instance
    partner_occupation_question = SingleChoiceQuestion(
        question_id="DE16",
        question_text="What is the primary occupation of your partner/spouse?",
        df=df,
        response_id=response_id
    )

    # Print output
    print(partner_occupation_question)"""


"""# testcase DE20/21

import pandas as pd

if __name__ == "__main__":
    data = {
        "responseId": ["R_123456"],
        "DE20": [1],  # Partner holds a PhD (1 = Yes, 2 = No)
        "DE21": [5],  # Partner has no income (assuming encoding)
    }

    df = pd.DataFrame(data)
    response_id = "R_123456"

    # DE20: PhD question
    phd_question = SingleChoiceQuestion(
        question_id="DE20",
        question_text="Does your partner/spouse hold a PhD. or doctorate degree?",
        df=df,
        response_id=response_id
    )

    # DE21: Income comparison
    income_question = SingleChoiceQuestion(
        question_id="DE21",
        question_text="Does your partner/spouse earn more than you?",
        df=df,
        response_id=response_id
    )

    print(phd_question)
    print(income_question)"""


# testcase DE23

if __name__ == "__main__":
    data = {
        "responseId": ["R_123456"],
        "DE23_1_1": [1],    # First child – Year (encoded)
        "DE23_1_2": [2],    # First child – Country (encoded)
        "DE23_2_1": [100],  # Second child – Year (encoded)
        "DE23_2_2": [101],  # Second child – Country (encoded)
    }

    df = pd.DataFrame(data)
    response_id = "R_123456"

    # Encoding maps
    year_mapping = {1: 1990, 2: 1995}
    country_mapping = {100: "Germany", 101: "France"}
    value_map = {**year_mapping, **country_mapping}

    # New: Add row + sub maps for readable output
    row_map = {
        "1": "First child",
        "2": "Second child"
    }
    sub_map = {
        "1": "Year",
        "2": "Country"
    }

    birth_question = MatrixQuestion(
        question_id="DE23",
        question_text="When and where was each child born?",
        df=df,
        response_id=response_id,
        value_map=value_map,
        row_map=row_map,
        sub_map=sub_map
    )

    print(birth_question)


"""# testcase DE24

if __name__ == "__main__":
    data = {
        "responseId": ["R_123456"],
        "DE35": ["1,3,6,10"],  # Selected options: "I simply don't want kids", "Financial reasons", "Age", "Other reasons"
        "DE35_10_TEXT": ["Religious beliefs"],  # Extra text field for "Other reasons"
    }

    df = pd.DataFrame(data)
    response_id = "R_123456"

    # Creating MultipleChoiceQuestion instance
    reasons_question = MultipleChoiceQuestion(
        question_id="DE35",
        question_text="Could you please share the primary reason for not having children?",
        df=df,
        response_id=response_id
    )

    print(reasons_question)"""


# testcase DE24

"""if __name__ == "__main__":
    data = {
        "responseId": ["R_123456"],
        "DE9": ["1,3,6,8"],  # Options selected, including "Other" (8)
        "DE9_8_TEXT": ["Religious beliefs"]  # The user provided additional text
    }

    df = pd.DataFrame(data)
    answer_mapping = {
        "1": "I simply don't want kids",
        "3": "Financial reasons",
        "6": "Age",
        "8": "Other reasons"  # Now "Other" is option 8 instead of 10
    }

    response_id = "R_123456"

    question = MultipleChoiceQuestion(
        question_id="DE9",
        question_text="Could you please share the primary reason for not having children?",
        df=df,
        response_id=response_id,
        answer_mapping=answer_mapping
    )

    print(question)"""


# testcase PL1

"""if __name__ == "__main__":
    data = {
        "responseId": ["R_123456"],
        "PL1_1": ["1"],  
        "PL1_2": ["2"],  
        "PL1_3": ["3"],  
        "PL1_4": ["4"], 
        "PL1_5": ["5"]
    }

    df = pd.DataFrame(data)
    response_id = "R_123456"

    value_map = {1: "No", 2: "Yes, teaching relief only", 3: "Yes, teaching and service relief", 4: "Yes, full relief of duties", 5: "Dont know"}  
    row_map = {
        "1": "PhD students",
        "2": "Postdocs",
        "3": "Assistant professors",
        "4": "Associate professors",
        "5": "Full professors"
    }

    PL_question = MatrixQuestion(
        question_id="PL1",
        question_text="Does your current inst offer paid parental leave to academics of your same legal gender?",
        df=df,
        response_id=response_id,
        value_map=value_map,
        row_map=row_map
    )

    print(PL_question)"""








