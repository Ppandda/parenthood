# transforms.py


def months_to_weeks(months):
    """
    Convert a numeric value in months to an approximate value in weeks.
    Uses average month length: 4.345 weeks.
    """
    try:
        return round(float(months) * 4.345)
    except (TypeError, ValueError):
        return months  # fail-safe fallback


def unified_time_to_weeks(value, unit_code):
    try:
        value = float(value)
        unit_code_str = str(unit_code).lower()
        factor_map = {
            "1": 1,
            "week": 1,
            "2": 4.345,
            "month": 4.345,
            "3": 13.035,
            "quarter": 13.035,
            "4": 26.07,
            "semester": 26.07,
            "year": 52,  # for unit_hint case
        }
        return round(value * factor_map.get(str(unit_code_str, 1).lower(), 1))
    except:
        return value


def unified_time_to_months(value, unit_code):
    try:
        value = float(value)
        unit_code_str = str(unit_code).lower()
        factor_map = {
            "week": 1 / 4.345,
            "month": 1,
            "quarter": 3,
            "semester": 6,
            "year": 12,
            # optionally keep int keys too
            "1": 1 / 4.345,
            "2": 1,
            "3": 3,
            "4": 6,
        }
        return round(value * factor_map.get(unit_code_str, 1), 2)
    except:
        return value


# --- new canonical entry‑point ----------------------------------------------
import pandas as pd
from typing import Dict

_FACTOR_TO_MONTHS = {
    "week": 1 / 4.345,
    "month": 1,
    "quarter": 3,
    "semester": 6,
    "year": 12,
}


def to_months(
    series: pd.Series, unit_code: str, *, sub_map: Dict[int, str] | None = None
) -> pd.Series:
    """
    Vectorised conversion of a numeric Series to *months*.

    Parameters
    ----------
    series     : pd.Series of numbers (may contain NaNs)
    unit_code  : the suffix from the column name (e.g. «1», «2», «week» …)
    sub_map    : optional mapping from numeric codes → unit labels
                 taken from question_maps.<QID>["sub_map"].

    Returns
    -------
    pd.Series (float) in months, with NaNs preserved.
    """
    # Resolve code → label
    if unit_code.isdigit() and sub_map:
        unit_label = sub_map.get(int(unit_code), None)
    else:
        unit_label = str(unit_code)

    if unit_label is None:
        raise ValueError(f"Unknown unit code {unit_code!r} with no sub_map")

    unit_label = unit_label.lower()
    if unit_label not in _FACTOR_TO_MONTHS:
        raise ValueError(f"Unsupported time unit: {unit_label!r}")

    factor = _FACTOR_TO_MONTHS[unit_label]
    return series.astype(float) * factor
