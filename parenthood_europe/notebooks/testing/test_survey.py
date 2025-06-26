import sys
import os

# Add the parent directory so Python can find 'libs'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "libs")))

# Now import the Question class
import survey_analysis as sa
from survey_analysis import Question

# Create a test Question object
question1 = Question(
    question_id="Q1",
    question_text="How satisfied are you with our service?",
    responses=["Very satisfied", "Satisfied", "Neutral", "Dissatisfied", "Very satisfied"]
)
question1.pretty_print()



question2 = Question(
    question_id="Q2",
    question_text="How much do you agree with the statement?",
    responses=["Agree", "Strongly Agree", "Neutral", "Disagree", "Agree", "Strongly Disagree"]
)
question2.pretty_print()

# Print the object to check if everything works
#print(question)
# Print individual attributes
#print("Question ID:", question.question_id)
#print("Question Text:", question.question_text)
#print("Responses:", question.responses)

#likert_question = LikertQuestion(
#    question_id="Q2",
#    question_text="How much do you agree with the statement?",
#    responses=["Agree", "Strongly Agree", "Neutral", "Disagree", "Agree", "Strongly Disagree"],
#    scale_labels=["Strongly Disagree", "Disagree", "Neutral", "Agree", "Strongly Agree"]
#)

# Print the LikertQuestion object and analyze responses
#print(likert_question)
#print("Likert Analysis:", likert_question.analyze())