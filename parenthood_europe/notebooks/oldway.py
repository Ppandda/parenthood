import sys
import os


def print_question(question_id, question_text, responses):
    print(f"Question ID: {question_id}")
    print(f"Question Text: {question_text}")
    print(f"Responses: {responses}")
    
    

question_id1 = "Q1"
question_text1 = "How satisfied are you with our service?"
responses1 = ["Very satisfied", "Satisfied", "Neutral", "Dissatisfied", "Very satisfied"]

print_question(question_id1, question_text1, responses1)

question_id2 = "Q2"
question_text2 = "How much do you agree with the statement?"
responses2 = ["Agree", "Strongly Agree", "Neutral", "Disagree", "Agree", "Strongly Disagree"]

print_question(question_id2, question_text2, responses2)

print_question("Not Satisfied", "Answer 1", "Sudhang")




###################

if __name__ == "__main__":
    text_question = SingleChoiceQuestion(
        question_id="DE2",
        question_text="What is your gender identity?",
        choices = ["Woman", "Man", "Non-binary person", "Prefer not to answer"],
        responses=["Woman"]





        class SingleChoiceQuestion(Question):
    """
    Class for a single-choice survey question.
    DE2, DE4, DE5, DE6,
    """
    def __init__(self, question_id: str, question_text: str, responses: list):
        super().__init__(question_id, question_text)
        #self.responses = responses
        self.response = responses[0] if responses else None  
        self.tenure_year = None
        self.custom_response = None

        if len(responses) > 1:
                print(f"⚠️ Data Issue: Question {question_id} should have 1 response but got multiple!")

        # Handle "I am tenured" in DE8
        if isinstance(self.response, str) and "tenured" in self.response.lower():
            self.tenure_year = next((resp for resp in responses if isinstance(resp, str) and resp.isdigit()), None)

        # "Other" in DE8
        if isinstance(self.response, str) and "other" in self.response.lower():
            self.custom_response = next((resp for resp in responses if isinstance(resp, str)), None)

    def __repr__(self):
        tenure_text = f", Tenure year: {self.tenure_year}" if self.tenure_year else ""
        other_text = f", Other response: {self.custom_response}" if self.custom_response else ""
        return f"{self.question_text} Answer: {self.response}{tenure_text}{other_text}."
    

    def analyze(self):
        """
        Analyze the single-choice responses.
        """
        # Count the number of responses for each choice
        choice_counts = {choice: 0 for choice in self.choices}
        for response in self.responses:
            choice_counts[response] += 1
        
        return choice_counts