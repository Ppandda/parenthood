import sys
sys.path.insert(0, "/Users/Paula_1/CodingProjects/parenthood")

from libs.survey_analysis import NumericQuestion


def test_DE1_numeric_question():
    data = {
        "responseId": ["R_999001"],
        "DE1": ["1990"]
    }

    df = pd.DataFrame(data)
    response_id = "R_999001"

    birth_year_question = NumericQuestion(
        question_id="DE1",
        question_text="In what year were you born?",
        df=df,
        response_id=response_id,
    )

    print(birth_year_question)



def test_de10_numeric_question():
    data = {
        "responseId": ["R_123456"],
        "DE10_1": [8],   # Career-focused activities
        "DE10_3": [4],   # Leisure
        "DE10_4": [6],   # Sleep
    }

    df = pd.DataFrame(data)
    response_id = "R_123456"

    career_question = NumericQuestion(
        question_id="DE10_1",
        question_text="How many hours did you spend on career-focused activities?",
        df=df,
        response_id=response_id,
    )

    leisure_question = NumericQuestion(
        question_id="DE10_3",
        question_text="How many hours did you spend on leisure?",
        df=df,
        response_id=response_id,
    )

    missing_question = NumericQuestion(
        question_id="DE10_2",
        question_text="How many hours did you spend on household work?",
        df=df,
        response_id=response_id,
    )

    print(career_question)
    print(leisure_question)
    print(missing_question)

if __name__ == "__main__":
    test_DE1_numeric_question()
    test_de10_numeric_question()
