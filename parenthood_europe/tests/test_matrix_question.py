from libs.survey_analysis import MatrixQuestion
from libs.transform_time import unified_time_to_weeks, months_to_weeks
import pandas as pd

def test_de23_matrix_question_birth_details():
    data = {
        "responseId": ["R_123456"],
        "DE23_1_1": [1],   # First child – Year (encoded)
        "DE23_1_2": [2],   # First child – Country (encoded)
        "DE23_2_1": [100], # Second child – Year (encoded)
        "DE23_2_2": [101], # Second child – Country (encoded)
    }

    df = pd.DataFrame(data)
    response_id = "R_123456"

    # Encoding maps
    year_mapping = {
        1: 1990,
        2: 1995
    }
    country_mapping = {
        100: "Germany",
        101: "France"
    }
    value_map = {**year_mapping, **country_mapping}

    # Row and sub-column maps for readability
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



def test_pl1_matrix_question_gender_leave():
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

    value_map = {
        1: "No",
        2: "Yes, teaching relief only",
        3: "Yes, teaching and service relief",
        4: "Yes, full relief of duties",
        5: "Dont know"
    }

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

    print(PL_question)



def test_pl2_matrix_question_leave_duration():
    data = {
        "responseId": ["R_654321"],
        "PL2_1_1": [12],    # 12 weeks
        "PL2_2_1": [3],     # 3 months
        "PL2_3_1": [1],     # 1 quarter
        "PL2_4_1": [1],     # 1 semester
        "PL2_5_1": [None]   # Skipped
    }

    df = pd.DataFrame(data)
    response_id = "R_654321"

    row_map = {
        "1": "PhD students",
        "2": "Postdocs",
        "3": "Faculty (untenured)",
        "4": "Faculty (tenure-track)",
        "5": "Faculty (tenured)"
    }

    sub_map = {
        "1": "weeks",
        "2": "months",
        "3": "quarters",
        "4": "semesters"
    }

    parental_leave_units = MatrixQuestion(
        question_id="PL2",
        question_text="How long was the paid parental leave taken, normalized to weeks?",
        df=df,
        response_id=response_id,
        row_map=row_map,
        sub_map=sub_map,
        value_transform=unified_time_to_weeks  # assumes this function is imported
    )

    print(parental_leave_units)



def test_pl4_matrix_question_maternal_vs_paternal_leave():
    data = {
        "responseId": ["R_987654"],
        "PL4_1_1": [6],  # PhD, maternal → 6 months
        "PL4_1_2": [2],  # PhD, paternal → 2 months
        "PL4_2_1": [5],  # Postdoc, maternal
        "PL4_2_2": [1],  # Postdoc, paternal
        "PL4_3_1": [4],  # Professor, maternal
        "PL4_3_2": [1],  # Professor, paternal
    }

    df = pd.DataFrame(data)
    response_id = "R_987654"

    row_map = {
        "1": "PhD students",
        "2": "Postdocs",
        "3": "Professors"
    }

    sub_map = {
        "1": "Maternal (mother)",
        "2": "Paternal (father)"
    }

    parental_leave_question = MatrixQuestion(
        question_id="PL4",
        question_text="How long should paid parental leave be (in weeks)?",
        df=df,
        response_id=response_id,
        row_map=row_map,
        sub_map=sub_map,
        value_transform=months_to_weeks,  # assumes this is imported
        format="row-sub"
    )

    print(parental_leave_question)



def test_pl6_matrix_question_leave_use_by_child():
    data = {
        "responseId": ["R_456789"],
        "PL5_1": [6],  # Not applicable
        "PL5_2": [1],  # No, I did not take the leave
        "PL5_3": [2],  # Yes, no work
        "PL5_4": [3],  # Yes, up to 1/3
        "PL5_5": [4],  # Yes, about half
        "PL5_6": [5],  # Yes, at least 2/3
        "PL5_7": [6],
        "PL5_8": [6],
        "PL5_9": [6],
        "PL5_10": [6]
    }

    df = pd.DataFrame(data)
    response_id = "R_456789"

    value_map = {
        "1": "No, I did not take the leave",
        "2": "Yes, and I did not do anything work-related during that time",
        "3": "Yes, and I spent up to 1/3 of that time on work-related activities",
        "4": "Yes, and I spent about half of that time on work-related activities",
        "5": "Yes, and I spent at least 2/3 of that time on work-related activities",
        "6": "Not applicable"
    }

    sub_map = {
        "1": "Your 1st child",
        "2": "Your 2nd child",
        "3": "Your 3rd child",
        "4": "Your 4th child",
        "5": "Your 5th child",
        "6": "Your 6th child",
        "7": "Your 7th child",
        "8": "Your 8th child",
        "9": "Your 9th child",
        "10": "Your 10th child (if more than 10, consider youngest)"
    }

    leave_use_question = MatrixQuestion(
        question_id="PL5",
        question_text="For each child: Did you take the leave? If yes, did you do any work related activities during that time?",
        df=df,
        response_id=response_id,
        value_map=value_map,
        sub_map=sub_map,
        format="row-sub"
    )

    print(leave_use_question)




def test_pl7_matrix_question_leave_duration_by_child():
    data = {
        "responseId": ["R_246810"],
        "PL6_1_1": [12],  # 1st child – 12 weeks
        "PL6_2_2": [3],   # 2nd child – 3 months
        "PL6_3_3": [2],   # 3rd child – 2 quarters
        "PL6_4_4": [1]    # 4th child – 1 semester
    }

    df = pd.DataFrame(data)
    response_id = "R_246810"

    row_map = {
        "1": "1st child",
        "2": "2nd child",
        "3": "3rd child",
        "4": "4th child",
        "5": "5th child",
        "6": "6th child",
        "7": "7th child",
        "8": "8th child",
        "9": "9th child",
        "10": "10th child (youngest if more than 10)"
    }

    sub_map = {
        "1": "Weeks",
        "2": "Months",
        "3": "Quarters",
        "4": "Semesters"
    }

    parental_leave_duration = MatrixQuestion(
        question_id="PL6",
        question_text="For each child for whom you took parental leave, please specify the duration of the leave.",
        df=df,
        response_id=response_id,
        row_map=row_map,
        sub_map=sub_map,
        value_transform=unified_time_to_weeks  # assumes imported from transform_time
    )

    print(parental_leave_duration)

  


def test_pl9_matrix_question_tenure_clock_stop():
    data = {
        "responseId": ["R_999999"],
        "PL9_1": [1],  # 1st child: Yes
        "PL9_2": [2],  # 2nd child: No
        "PL9_3": [1],  # 3rd child: Yes
        "PL9_4": [2],  # 4th child: No
    }

    df = pd.DataFrame(data)
    response_id = "R_999999"

    row_map = {
        "1": "1st child",
        "2": "2nd child",
        "3": "3rd child",
        "4": "4th child",
        "5": "5th child",
        "6": "6th child",
        "7": "7th child",
        "8": "8th child",
        "9": "9th child",
        "10": "10th child (youngest if more than 10)"
    }

    value_map = {
        "1": "Yes",
        "2": "No"
    }

    tenure_clock_question = MatrixQuestion(
        question_id="PL9",
        question_text="For each child for whom you took parental leave: did your tenure-clock stop when they were born or adopted?",
        df=df,
        response_id=response_id,
        row_map=row_map,
        value_map=value_map,
        format="row-sub"  # Explicit format declaration
    )

    print(tenure_clock_question)




def test_cs1_matrix_childcare_support():
    import pandas as pd
    from libs.survey_analysis import MatrixQuestion

    data = {
        "responseId": ["R_777777"],
        "CS1_1_1": [2],  # Yes
        "CS1_1_2": [4],  # Not applicable
        "CS1_2_1": [2],
        "CS1_2_2": [4],
        "CS1_3_1": [2],
        "CS1_3_2": [4],
        "CS1_4_1": [2],
        "CS1_4_2": [4],
        "CS1_5_1": [2],
        "CS1_5_2": [4],
        "CS1_6_1": [2],
        "CS1_6_2": [4],
        "CS1_7_1": [2],
        "CS1_7_2": [4],
        "CS1_8_1": [2],
        "CS1_8_2": [4],
        "CS1_9_1": [2],
        "CS1_9_2": [4],
        "CS1_10_1": [2],
        "CS1_10_2": [4],
    }

    df = pd.DataFrame(data)
    response_id = "R_777777"

    row_map = {
        "1": "Your 1st child",
        "2": "Your 2nd child",
        "3": "Your 3rd child",
        "4": "Your 4th child",
        "5": "Your 5th child",
        "6": "Your 6th child",
        "7": "Your 7th child",
        "8": "Your 8th child",
        "9": "Your 9th child",
        "10": "Your 10th child (or youngest if more than 10)",
    }

    sub_map = {
        "1": "Childcare provided",
        "2": "Did you use it?",
    }

    value_map = {
        "1": "No",
        "2": "Yes",
        "3": "Don't know",
        "4": "Not applicable",  # only relevant for second column
    }

    question = MatrixQuestion(
        question_id="CS1",
        question_text="For each of your children, did your employer provide subsidies, facilities, or other direct benefits for childcare? If so, did you use it?",
        df=df,
        response_id=response_id,
        row_map=row_map,
        sub_map=sub_map,
        value_map=value_map,
        format="row-sub"
    )

    print(question)




def test_cs3_likert_countries():
    import pandas as pd
    from parenthood_europe.libs.survey_analysis import MatrixQuestion

    data = {
        "responseId": ["R_999999"],
        "CS3_1": [1],   # Albania – Very good
        "CS3_2": [2],   # Andorra – Good
        "CS3_3": [3],   # Armenia – Bad
        "CS3_4": [4],   # Austria – Very bad
        "CS3_5": [5],   # Azerbaijan – Don't know
        # ... add more if needed
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
        "5": "Azerbaijan",
        # ... continue up to "51": "Vatican City"
    }

    country_policy_rating = MatrixQuestion(
        question_id="CS3",
        question_text="Rate the general parental policies of the European countries you know.",
        df=df,
        response_id=response_id,
        row_map=row_map,
        value_map=value_map,
        format="row"
    )

    print(country_policy_rating)




if __name__ == "__main__":
    test_de23_matrix_question_birth_details()
    test_pl1_matrix_question_gender_leave()
    test_pl2_matrix_question_leave_duration()
    test_pl4_matrix_question_maternal_vs_paternal_leave()
    test_pl6_matrix_question_leave_use_by_child()  
    test_pl7_matrix_question_leave_duration_by_child()
    test_pl9_matrix_question_tenure_clock_stop()
    test_cs1_matrix_childcare_support()
    test_cs3_likert_countries() 


