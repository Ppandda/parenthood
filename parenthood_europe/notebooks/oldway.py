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