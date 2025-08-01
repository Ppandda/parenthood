from .questions.base import Question
import question_maps
import pandas as pd
import re
from transform_time import unified_time_to_months


# ---------- 1.  flatten sub‑columns into tidy long df ----------------------
def build_long_df(question: Question) -> pd.DataFrame:
    """
    Parameters
    ----------
    df          : full survey dataframe
    subcolumns  : list of PL2_1_1 ... etc.
    row_map     : {row_code:int → label:str}
    sub_map     : {unit_code:int → unit_label:str}  (can be {})
    Returns
    -------
    tidy DataFrame with columns
        ResponseId | Group | Value
    """
    records = []
    for col in question.subcolumns:
        parsed = question.parse_column_id(col, question.question_id)
        series = question.responses[col].dropna()

        # parent number: from column name suffix
        parent_number = col.split("_")[-1]

        for idx, val in series.items():
            record = {
                "ResponseId": question.df.loc[idx, "ResponseId"],
                "value": val,
            }

            # Inject row/unit labels if applicable
            if parsed["row_label"]:
                record["row"] = parsed["row_label"]
            if parsed["sub_label"]:
                record["unit"] = parsed["sub_label"]

            # ------------ GROUP assignment (row- or gender-based) ----------------
            if question.anchor_type == "parent_gender":
                group = resolve_gender(
                    question.df,
                    respondent_id=idx,
                    parent_num=parent_number,
                    lookup=question.gender_lookup,
                    value_map=question_maps.DE14["value_map"],
                )
                record["Group"] = group
            elif parsed["row_label"]:
                record["Group"] = parsed["row_label"]

            records.append(record)

    return pd.DataFrame(records)
    """unit_code = subcol.split("_")[-1]
    row_code = subcol.split("_")[-2] if len(subcol.split("_")) >= 2 else None
    group_lbl = row_map.get(int(row_code), row_code)

    series = df[["ResponseId", subcol]].dropna(subset=[subcol])
    # convert units → months if sub_map present
    # ----- convert units → months if sub_map present -----------------
    if sub_map:
        # look up text label ("Weeks", "Months", …) for this unit_code
        unit_label = sub_map.get(int(unit_code), unit_code)

        # normalise: lower‑case, singular  →  "Weeks"→"week"
        unit_label = str(unit_label).lower().rstrip("s")

        series[subcol] = series[subcol].apply(
            lambda v: unified_time_to_months(v, unit_label)
        )

    for rid, val in series[["ResponseId", subcol]].values:
        records.append({"ResponseId": rid, "Group": group_lbl, "Value": val})

return pd.DataFrame.from_records(records)"""


# ---------- 2.  numeric binning -------------------------------------------
def bin_numeric(series: pd.Series, max_bins: int = 8) -> pd.Series:
    """Return a categorical Series with ≤ max_bins quantile bins."""
    try:
        return pd.qcut(series, q=max_bins, duplicates="drop").astype(str)
    except ValueError:
        return pd.cut(series, bins=4).astype(str)  # fallback


def numeric_sort(labels: list[str]) -> list[str]:
    """
    Return labels sorted by the *first* numeric value inside each string.
    “0–1”, “2–3”… → proper ascending order.
    Non-numeric labels fall back to lexicographic ordering at the end.
    """

    def key(lbl):
        nums = re.findall(r"-?\d+(?:\.\d+)?", str(lbl))
        return float(nums[0]) if nums else float("inf")

    return sorted(labels, key=key)


# ---------- 3.  percentage within group -----------------------------------
def percent_within(df: pd.DataFrame, group_cols: list[str]) -> pd.DataFrame:
    out = (
        df.groupby(group_cols, observed=True).agg(Count=("Count", "sum")).reset_index()
    )
    grp = group_cols[:-1]  # all except the last key
    out["Percentage"] = 100 * out["Count"] / out.groupby(grp)["Count"].transform("sum")
    return out


# ---------- 4.  parent‑gender resolver ------------------------------------
def resolve_gender(df, respondent_id, parent_num, lookup, value_map):
    """Return 'Woman' / 'Man' / 'Non‑binary' or None."""
    if (respondent_id, parent_num) in lookup:
        return lookup[(respondent_id, parent_num)]
    col = f"DE14_{parent_num}"
    try:
        code = df.at[respondent_id, col]
    except KeyError:
        return None
    if pd.isna(code):
        return None
    return value_map.get(int(code))
