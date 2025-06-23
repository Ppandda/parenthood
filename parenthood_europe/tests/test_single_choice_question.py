import pandas as pd
import libs
from libs.questions.single_choice import SingleChoiceQuestion
from libs.transform_time import unified_time_to_weeks

# multiple testcases


def test_de7_single_choice_position():
    text_question = SingleChoiceQuestion(
        question_id="DE7",
        question_text="What's your current position?",
        responses=[
            "I am tenured (please, indicate the year you received tenure, e.g., 2010)",
            "2015",
        ],
        # custom_responses=["A mix of them all"]  # Uncomment if needed
    )
    print(text_question)


def test_de8_academic_status_with_extras():
    data = {
        "responseId": ["R_123456"],
        "DE2": ["1"],  # Gender identity
        "DE4": ["2"],  # Economic situation
        "DE5": ["25"],  # Childhood country
        "DE6": ["42"],  # Current residence
        "DE8": ["5"],  # Academic status: tenure
        "DE8_4_TEXT": ["2015"],  # Extra field for tenure year
        "DE8_5_TEXT": ["Independent researcher"],  # Extra field for "Other"
    }

    df = pd.DataFrame(data)
    response_id = "R_123456"

    text_question = SingleChoiceQuestion(
        question_id="DE8",
        question_text="What is your current academic status?",
        df=df,
        response_id=response_id,
    )

    print(text_question)


def test_de14_gender_identity():
    data = {
        "responseId": ["R_789123"],
        "DE13_1": ["1"],  # Parent 1: Woman
        "DE13_2": ["2"],  # Parent 2: Man
    }

    df = pd.DataFrame(data)
    response_id = "R_789123"

    parent1_question = SingleChoiceQuestion(
        question_id="DE13_1",
        question_text="What is the gender identity of Parent 1?",
        df=df,
        response_id=response_id,
    )

    parent2_question = SingleChoiceQuestion(
        question_id="DE13_2",
        question_text="What is the gender identity of Parent 2?",
        df=df,
        response_id=response_id,
    )

    print(parent1_question)
    print(parent2_question)


def test_de15_de16_parent_categories():
    data = {
        "responseId": ["R_123456"],
        "DE14_1": [3],  # Parent 1 selected option 3
        "DE14_2": [6],  # Parent 2 selected option 7
    }

    df = pd.DataFrame(data)
    response_id = "R_123456"

    parent1_question = SingleChoiceQuestion(
        question_id="DE14_1",
        question_text="Which category best describes Parent 1?",
        df=df,
        response_id=response_id,
    )

    parent2_question = SingleChoiceQuestion(
        question_id="DE14_2",
        question_text="Which category best describes Parent 2?",
        df=df,
        response_id=response_id,
    )

    print(parent1_question)
    print(parent2_question)


def test_de8_single_choice_with_extra_texts():
    data = {
        "responseId": ["R_123456"],
        "DE8": ["1"],  # I am tenured
        "DE8_4_TEXT": ["2015"],  # Extra field for tenure year
        "DE8_5_TEXT": ["Independent researcher"],  # Extra for "Other"
    }

    df = pd.DataFrame(data)
    response_id = "R_123456"

    text_question = SingleChoiceQuestion(
        question_id="DE8",
        question_text="What is your current academic status?",
        df=df,
        response_id=response_id,
    )

    print(text_question)


def test_de13_single_choice_two_parents():
    data = {
        "responseId": ["R_789123"],
        "DE13_1": ["1"],  # Parent 1: Woman
        "DE13_2": ["2"],  # Parent 2: Man
    }

    df = pd.DataFrame(data)
    response_id = "R_789123"

    parent1_question = SingleChoiceQuestion(
        question_id="DE13_1",
        question_text="What is the gender identity of Parent 1?",
        df=df,
        response_id=response_id,
    )

    parent2_question = SingleChoiceQuestion(
        question_id="DE13_2",
        question_text="What is the gender identity of Parent 2?",
        df=df,
        response_id=response_id,
    )

    print(parent1_question)
    print(parent2_question)


def test_de14_category_description_parents():
    data = {
        "responseId": ["R_123456"],
        "DE14_1": [3],  # Parent 1 selected option 3
        "DE14_2": [6],  # Parent 2 selected option 7
    }

    df = pd.DataFrame(data)
    response_id = "R_123456"

    parent1_question = SingleChoiceQuestion(
        question_id="DE14_1",
        question_text="Which category best describes Parent 1?",
        df=df,
        response_id=response_id,
    )

    parent2_question = SingleChoiceQuestion(
        question_id="DE14_2",
        question_text="Which category best describes Parent 2?",
        df=df,
        response_id=response_id,
    )

    print(parent1_question)
    print(parent2_question)


def test_de18_partner_occupation_other():
    data = {
        "responseId": ["R_123456"],
        "DE16": [9],  # Respondent selected "Other"
        "DE16_8_TEXT": ["Freelance consultant"],  # Custom text response
    }
    df = pd.DataFrame(data)
    response_id = "R_123456"

    partner_occupation_question = SingleChoiceQuestion(
        question_id="DE16",
        question_text="What is the primary occupation of your partner/spouse?",
        df=df,
        response_id=response_id,
    )

    print(partner_occupation_question)


def test_de20_de21_partner_phd_and_income():
    data = {
        "responseId": ["R_123456"],
        "DE20": [1],  # Partner holds PhD
        "DE21": [5],  # Partner has no income
    }
    df = pd.DataFrame(data)
    response_id = "R_123456"

    phd_question = SingleChoiceQuestion(
        question_id="DE20",
        question_text="Does your partner/spouse hold a PhD. or doctorate degree?",
        df=df,
        response_id=response_id,
    )

    income_question = SingleChoiceQuestion(
        question_id="DE21",
        question_text="Does your partner/spouse earn more than you?",
        df=df,
        response_id=response_id,
    )

    print(phd_question)
    print(income_question)


def test_pl3_ideal_parental_leave():
    data = {
        "responseId": ["R_987654"],
        "PL3": ["3"],  # Selected: "Teaching and service relief"
        "PL3_5_TEXT": [
            "Something flexible, depending on the semester"
        ],  # Extra text (likely for option "5")
    }

    df = pd.DataFrame(data)
    response_id = "R_987654"

    value_map = {
        "1": "There is no need for it",
        "2": "Teaching relief only",
        "3": "Teaching and service relief",
        "4": "Full relief of duties",
        "5": "Other",
    }

    ideal_leave_question = SingleChoiceQuestion(
        question_id="PL3",
        question_text="If you could freely choose, which type of parental leave would be ideal for you?",
        df=df,
        response_id=response_id,
        value_map=value_map,
    )

    print(ideal_leave_question)


def test_pl5_unpaid_parental_leave():
    data = {
        "responseId": ["R_987654"],
        "PL5": ["4"],  # Selected: "Something else"
        "PL5_4_TEXT": ["Depends on institutional norms and family structure."],
    }

    df = pd.DataFrame(data)
    response_id = "R_987654"

    value_map = {
        "1": "Men and women should be offered the same unpaid parental leave",
        "2": "Women should get more",
        "3": "Men should get more",
        "4": "Something else (please, elaborate more on this answer)",
    }

    unpaid_leave_question = SingleChoiceQuestion(
        question_id="PL5",
        question_text="Do you think that men and women faculty should be offered equal unpaid parental leave, or not?",
        df=df,
        response_id=response_id,
        value_map=value_map,
    )

    print(unpaid_leave_question)


def test_pl8_tenure_clock_stop_conversion():
    data = {
        "responseId": ["R_112233"],
        "PL8": ["3"],  # Selected: Yes, enter years
        "PL8_3_TEXT": ["1.5"],  # Entered value: 1.5 years
    }

    df = pd.DataFrame(data)
    response_id = "R_112233"

    value_map = {
        "1": "No",
        "2": "Yes, but don't know how long",
        "3": "Yes (please, enter how many years per child in numeric digits)",
        "4": "Don't know",
    }

    tenure_stop_question = SingleChoiceQuestion(
        question_id="PL8",
        question_text="Does your current institution offer tenure-clock stop to faculty of your legal gender?",
        df=df,
        response_id=response_id,
        value_map=value_map,
        value_transform=unified_time_to_weeks,
        unit_hint="year",
    )

    print(tenure_stop_question)


def test_pl10_single_choice_parental_support():
    import pandas as pd
    from libs.survey_analysis import SingleChoiceQuestion

    data = {
        "responseId": ["R_999001"],
        "PL10": ["1"],  # Chose "Yes, much better"
    }

    df = pd.DataFrame(data)
    response_id = "R_999001"

    value_map = {
        "1": "Yes, much better",
        "2": "Yes, slightly better",
        "3": "Just the bare minimum",
        "4": "Don't know",
    }

    question = SingleChoiceQuestion(
        question_id="PL10",
        question_text=(
            'Overall, is the "parental leave" support offered by your current institution '
            "better than the minimum required by law in the country?"
        ),
        df=df,
        response_id=response_id,
        value_map=value_map,
    )

    print(question)


def test_cs2_single_choice_childcare_support():
    data = {"responseId": ["R_7891011"], "CS2": [4]}  # e.g., "Don't know"

    df = pd.DataFrame(data)
    response_id = "R_7891011"

    # Define value mapping
    answer_mapping = {
        1: "Yes, much better",
        2: "Yes, slightly better",
        3: "Just the bare minimum",
        4: "Don't know",
    }

    # Instantiate the question
    cs2_question = SingleChoiceQuestion(
        question_id="CS2",
        question_text="Overall, is the 'childcare' support offered by your current institution better than the minimum required by law in the country?",
        df=df,
        response_id=response_id,
        answer_mapping=answer_mapping,
    )

    print(cs2_question)


if __name__ == "__main__":
    test_de7_single_choice_position()
    test_de8_academic_status_with_extras()
    test_de14_gender_identity()
    test_de15_de16_parent_categories()
    test_de18_partner_occupation_other()
    test_de20_de21_partner_phd_and_income()
    test_pl3_ideal_parental_leave()
    test_pl5_unpaid_parental_leave()
    test_pl8_tenure_clock_stop_conversion()
    test_pl10_single_choice_parental_support()
    test_cs2_single_choice_childcare_support()
