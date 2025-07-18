import pandas as pd
from pathlib import Path


def load_survey_data(
    file_path="parenthood_europe/data/Parenthood in Academia_November 7, 2024_15.52",
    cols_to_use=None,
):
    data_file = Path(file_path)

    df_raw = pd.read_excel(data_file, header=None, usecols=cols_to_use)

    # Step 5: Promote first row to column headers
    df_raw.columns = df_raw.iloc[0]

    # Step 6: Get response data only (starting from row 2)
    df = df_raw[2:].copy()
    df.reset_index(drop=True, inplace=True)

    return df_raw, df


def load_survey_data_and_meta(
    file_path="parenthood_europe/data/Parenthood in Academia_November 7, 2024_15.52",
    cols_to_use=None,
):
    data_file = Path(file_path)

    df_raw = pd.read_excel(data_file, header=0, usecols=cols_to_use)
    meta_row = df_raw.iloc[0]
    metadata = {col: meta_row[col] for col in df_raw.columns if col != "Response ID"}

    df = df_raw.drop(index=0)
    df.reset_index(drop=True, inplace=True)

    return df, metadata
