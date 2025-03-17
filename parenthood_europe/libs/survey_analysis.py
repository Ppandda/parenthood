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
    DE1, 
    """
    def __init__(self, question_id: str, question_text: str, responses: list):
        super().__init__(question_id, question_text)
        self.responses = responses
        self.min_value = 0
        self.max_value = 10000000

    def __repr__(self):
        if not self.responses:
            return f"{self.question_text} No answer provided."

        response_text = ", ".join(map(str, self.responses))
        return f"{self.question_text} Answer: {response_text}."

    

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
    DE3, DE7
    """
    def __init__(self, question_id: str, question_text: str, responses: list, custom_responses: list = None):
        super().__init__(question_id, question_text)
        self.responses = responses
        self.custom_responses = custom_responses or []

        for response in self.responses:
            if response != "Self describe":
                continue
            self.custom_responses.append(response)

    def __repr__(self):
        selected_responses = [r for r in self.responses if r != "Self describe"]
        selected_text = ", ".join(selected_responses) if selected_responses else "No responses selected"
        custom_text = f", Self describe: {self.custom_responses[0]}" if self.custom_responses else ""

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


if __name__ == "__main__":
    text_question = SingleChoiceQuestion(
        question_id="DE7",
        question_text="Whats your current position?",
        responses = ["I am tenured (please, indicate the year you received tenure, e.g., 2010)", "2015"] #["Other (please, specify)", "blabliblupp"] 
        #custom_responses = ["A mix of them all"]
    )

    ## look at the data tenured will be DE_7_4 something and other might be DE_7_5_1 - the cols are more for these options!

    print(text_question)
