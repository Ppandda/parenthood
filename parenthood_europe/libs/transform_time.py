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
