from parenthood_europe.libs.survey_analysis import MultipleChoiceQuestion
import pandas as pd

def test_de2_multiple_choice_origin():
    data = {
        "responseId": ["R_123456"],  # Unique participant ID
        "DE7": ["1,3,5"],            # Multiple selections as comma-separated values
        "DE7_5_TEXT": ["I identify differently!"],  # Custom text input for "Self describe"
    }

    df = pd.DataFrame(data)
    response_id = "R_123456"

    multi_question = MultipleChoiceQuestion(
        question_id="DE7",
        question_text="What is your origin?",
        df=df,
        response_id=response_id
    )

    print(multi_question)


def test_de9_multiple_choice_affiliation():
    data = {
        "responseId": ["R_123456"],
        "DE9": ["Austria, France, Germany"],  # Multiple countries selected
        "DE9_TEXT": [""]  # Empty "Other" text
    }

    df = pd.DataFrame(data)
    response_id = "R_123456"

    affiliation_question = MultipleChoiceQuestion(
        question_id="DE9",
        question_text="Select ALL the European countries where you have been affiliated in academia.",
        df=df,
        response_id=response_id
    )

    print(affiliation_question)


def test_de9_multiple_choice_affiliation_with_text():
    data = {
        "responseId": ["R_123456"],
        "DE9": ["1,2,3"],  # Includes "Other"
        "DE9_3_TEXT": ["I have been affiliated in an unlisted country"]
    }

    df = pd.DataFrame(data)
    response_id = "R_123456"

    answer_mapping_DE9 = {
        "1": "Austria",
        "2": "France",
        "3": "Other"
    }

    affiliation_question = MultipleChoiceQuestion(
        question_id="DE9",
        question_text="Select ALL the European countries where you have been affiliated in academia.",
        df=df,
        response_id=response_id,
        answer_mapping=answer_mapping_DE9
    )

    print(affiliation_question)


def test_de24_multiple_choice_no_kids_basic():
    data = {
        "responseId": ["R_123456"],
        "DE35": ["1,3,6,10"],
        "DE35_10_TEXT": ["Religious beliefs"]
    }

    df = pd.DataFrame(data)
    response_id = "R_123456"

    reasons_question = MultipleChoiceQuestion(
        question_id="DE35",
        question_text="Could you please share the primary reason for not having children?",
        df=df,
        response_id=response_id
    )

    print(reasons_question)



def test_de24_multiple_choice_no_kids_with_mapping():
    # Test with answer mapping, where "Other" is mapped to 8
    data = {
        "responseId": ["R_123456"],
        "DE9": ["1,3,6,8"],  # Includes "Other" as option 8
        "DE9_8_TEXT": ["Religious beliefs"]
    }

    df = pd.DataFrame(data)
    response_id = "R_123456"

    answer_mapping = {
        "1": "I simply don't want kids",
        "3": "Financial reasons",
        "6": "Age",
        "8": "Other reasons"
    }

    question = MultipleChoiceQuestion(
        question_id="DE9",
        question_text="Could you please share the primary reason for not having children?",
        df=df,
        response_id=response_id,
        answer_mapping=answer_mapping
    )

    print(question)


if __name__ == "__main__":
    test_de7_multiple_choice_origin()
    test_de9_multiple_choice_affiliation()
    test_de9_multiple_choice_affiliation_with_text()
    test_de24_multiple_choice_no_kids_basic()
    test_de24_multiple_choice_no_kids_with_mapping()
