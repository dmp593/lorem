import re

from enum import StrEnum
from typing import Self

from app.core import utils


class Filter:
    def __init__(self, key: str, value: any) -> None:
        self.key = key
        self.value = value

    def __call__(self) -> dict[str, any]:
        return {self.key: self.value}

    @property
    def value__isnumeric(self) -> bool:
        return utils.is_numeric(self.value)

    @property
    def value__number(self) -> int | float:
        return utils.to_number(self.value)


class GroupType(StrEnum):
    Expr = "$expr"
    And = "$and"
    Or = "$or"


class GroupFilter(Filter):
    def __init__(self, key: GroupType, *value: tuple[Filter]) -> None:
        super().__init__(key, list(value))

    def __lshift__(self, rhs) -> Self:
        self.value.append(rhs)
        return self

    def __call__(self) -> dict[str, any]:
        return {self.key.value: [value() for value in self.value]}


class And(GroupFilter):
    names = ['and']

    def __init__(self, *value: tuple[Filter]) -> None:
        super().__init__(GroupType.And, *value)


class Or(GroupFilter):
    def __init__(self, *value: tuple[Filter]) -> None:
        super().__init__(GroupType.Or, *value)


class Eq(Filter):
    names = ['eq']

    def __call__(self) -> dict[str, dict[str, any]]:
        return {self.key: {"$eq": self.value}}


class Ne(Filter):
    names = ['ne']

    def __call__(self) -> dict[str, dict[str, any]]:
        return {self.key: {"$ne": self.value}}


class Gt(Filter):
    names = ['gt']

    def __call__(self) -> dict[str, dict[str, any]]:
        return {self.key: {"$gt", self.value}}


class Gte(Filter):
    names = ['ge']

    def __call__(self) -> dict[str, dict[str, any]]:
        return {self.key: {"$gte", self.value}}


class Lt(Filter):
    names = ['lt']

    def __call__(self) -> dict[str, dict[str, any]]:
        return {self.key: {"$lt", self.value}}


class Lte(Filter):
    names = ['lte']

    def __call__(self) -> dict[str, dict[str, any]]:
        return {self.key: {"$lte", self.value}}


class ListFilter(Filter):
    @property
    def value__list(self):
        value = self.value
        
        if isinstance(value, list):
            return value

        if isinstance(value, str) and "," in value:
            return [v for v in value.split(",")]
        
        return [value]

    @property
    def value__list_with_numerics(self):
        return [utils.to_number(v, default=v) for v in self.value__list]


class In(ListFilter):
    names = ['in']

    def __call__(self) -> dict[str, dict[str, any]]:
        return {self.key: {"$in": self.value__list}}


class NotIn(ListFilter):
    names = ['nin', 'notin']
    
    def __call__(self) -> dict[str, dict[str, any]]:
        return {self.key: {"$nin": self.value__list}}


class BooleanFilter(Filter):
    def __init__(self, key: str, value: bool | int | str = True) -> None:
        super().__init__(key, value)

    @property
    def value__bool(self):
        if isinstance(self.value, bool):
            return self.value

        if isinstance(self.value, (int, float)):
            return self.value != 0

        if isinstance(self.value, str):
            value_ = self.value.lower()
            
            if value_ in ["true", "yes", "y", "1", ""]:
                return True    
            elif value_ in ["false", "no", "n", "0"]:
                return False
        
        raise ValueError(f"'{self.value}' is not a valid boolean value")


class Exists(BooleanFilter):
    names = ['exists']
    
    def __call__(self) -> dict[str, dict[str, bool]]:
        return {self.key: {"$exists": self.value__bool}}


class NotExists(Exists):
    names = ['nexists', 'notexists']

    def __call__(self) -> dict[str, dict[str, bool]]:
        return {self.key: {"$exists": not self.value__bool}}


class IsNull(BooleanFilter):
    names = ['null', 'isnull']

    def __call__(self) -> And:
        is_null = And(
            Exists(self.key, True),
            (Eq if self.value__bool else Ne)(self.key, None)
        )

        return is_null()


class IsNotNull(BooleanFilter):
    names = ['nnull', 'notnull', 'isnotnull']

    def __call__(self) -> And:
        is_not_null = And(
            Exists(self.key, True),
            (Ne if self.value__bool else Eq)(self.key, None)
        )

        return is_not_null()


class RegexFilter(Filter):
    names = ['re', 'regex']

    def __init__(self, key: str, value: str, flags: re.RegexFlag = re.RegexFlag.ASCII) -> None:
        super().__init__(key, value)
        self.flags = flags

    @property
    def value__pattern(self) -> re.Pattern:
        return re.compile(self.value, self.flags)

    def __call__(self) -> dict[dict[str, re.Pattern]]:
        return {self.key: {"$regex": self.value__pattern}}


class Contains(RegexFilter):
    names = ['contains']


class IContains(RegexFilter):
    names = ['icontains']

    def __init__(self, key: str, value: str, flags: re.RegexFlag = re.RegexFlag.ASCII) -> None:
        super().__init__(key, value, flags | re.RegexFlag.IGNORECASE)


class StartsWith(RegexFilter):
    names = ['starts', 'startswith']

    @property
    def value__pattern(self) -> re.Pattern:
        return re.compile(f"^{self.value}", self.flags)


class IStartsWith(StartsWith):
    names = ['istarts', 'istartswith']

    def __init__(self, key: str, value: str, flags: re.RegexFlag = re.RegexFlag.ASCII) -> None:
        super().__init__(key, value, flags | re.RegexFlag.IGNORECASE)


class EndsWith(RegexFilter):
    names = ['ends', 'endswith']

    @property
    def value__pattern(self) -> re.Pattern:
        return re.compile(f"{self.value}$", self.flags)


class IEndsWith(EndsWith):
    names = ['iends', 'iendswith']

    def __init__(self, key: str, value: str, flags: re.RegexFlag = re.RegexFlag.ASCII) -> None:
        super().__init__(key, value, flags | re.RegexFlag.IGNORECASE)
