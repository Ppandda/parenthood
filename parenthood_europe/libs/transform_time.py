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
