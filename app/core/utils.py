import math

def is_numeric(value: any) -> bool:
    if isinstance(value, (int, float)):
        return True
    
    if not isinstance(value, str) or len(value) == 0:
        return False

    if not value[0].isdigit() and value[0] not in ("+", "-"):
        return False

    dots_count = 0
    for chr in value[1:]:
        if chr == ".":
            dots_count += 1

            if dots_count > 1:
                return False

            continue

        if not chr.isdigit():
            return False
    
    return True

def to_number(value: any, default: any = math.nan, converter: int | float = int):
    if isinstance(value, converter):
        return value
    
    try:
        return converter(value)
    except (TypeError, ValueError):
        return default
