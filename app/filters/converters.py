import re

from app.core import utils


def value_is_numeric(value: str | int | float) -> bool:
    return utils.is_numeric(value)


def value_as_number(value: str | int | float) -> int | float:
    return utils.to_number(value)


def value_is_listable(value: str | list) -> list[any]:
    return isinstance(value, list) or (isinstance(value, str) and "," in value)


def value_is_listable_with_numerics(value: str | list) -> bool:
    if not value_is_listable(value):
        return False
    
    list_of_values: list = value_as_list_with_numerics(value)

    return any(map(lambda v: isinstance(v, (int, float)), list_of_values))


def value_as_list(value: str | list) -> list[any]:
    if isinstance(value, list):
        return value

    if isinstance(value, str) and "," in value:
        return [v for v in value.split(",")]
    
    return [value]


def value_as_list_with_numerics(value: str | list) -> list[any]:
    return [utils.to_number(v, default=v) for v in value_as_list(value)]


def value_is_booleanable(value):
    if isinstance(value, (bool, int, float)):
        return True
    
    if isinstance(value, str) in ["true", "yes", "y", "1", "", "false", "no", "n", "0"]:
        return True
    
    return False


def value_as_bool(value):
    if isinstance(value, bool):
        return value

    if isinstance(value, (int, float)):
        return value != 0

    if isinstance(value, str):
        value_ = value.lower()
        
        if value_ in ["true", "yes", "y", "1", ""]:
            return True    
        elif value_ in ["false", "no", "n", "0"]:
            return False
    
    raise ValueError(f"'{value}' is not a valid boolean value")


def value_as_pattern(value: str, flags = re.RegexFlag.ASCII) -> re.Pattern:
    return re.compile(value, flags)
