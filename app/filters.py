import math
import re

from enum import StrEnum
from typing import Self

from app import exceptions, utils


__id_keys_candidates__ = ("id", "uuid", "uid", "code", "pk", "username", "email", "vat",)


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
    def __init__(self, *value: tuple[Filter]) -> None:
        super().__init__(GroupType.And, *value)


class Or(GroupFilter):
    def __init__(self, *value: tuple[Filter]) -> None:
        super().__init__(GroupType.Or, *value)


class Eq(Filter):
    def __call__(self) -> dict[str, dict[str, any]]:
        return {self.key: {"$eq": self.value}}


class Ne(Filter):
    def __call__(self) -> dict[str, dict[str, any]]:
        return {self.key: {"$ne": self.value}}


class Gt(Filter):
    def __call__(self) -> dict[str, dict[str, any]]:
        return {self.key: {"$gt", self.value}}


class Gte(Filter):
    def __call__(self) -> dict[str, dict[str, any]]:
        return {self.key: {"$gte", self.value}}


class Lt(Filter):
    def __call__(self) -> dict[str, dict[str, any]]:
        return {self.key: {"$lt", self.value}}


class Lte(Filter):
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
    def __call__(self) -> dict[str, dict[str, any]]:
        return {self.key: {"$in": self.value__list}}


class NotIn(ListFilter):
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
    def __call__(self) -> dict[str, dict[str, bool]]:
        return {self.key: {"$exists": self.value__bool}}


class NotExists(Exists):
    def __call__(self) -> dict[str, dict[str, bool]]:
        return {self.key: {"$exists": not self.value__bool}}


class IsNull(BooleanFilter):
    def __call__(self) -> And:
        is_null = And(
            Exists(self.key, True),
            (Eq if self.value__bool else Ne)(self.key, None)
        )

        return is_null()


class IsNotNull(BooleanFilter):
    def __call__(self) -> And:
        is_not_null = And(
            Exists(self.key, True),
            (Ne if self.value__bool else Eq)(self.key, None)
        )

        return is_not_null()


class RegexFilter(Filter):
    def __init__(self, key: str, value: str, flags: re.RegexFlag = re.RegexFlag.ASCII) -> None:
        super().__init__(key, value)
        self.flags = flags

    @property
    def value__pattern(self) -> re.Pattern:
        return re.compile(self.value, self.flags)

    def __call__(self) -> dict[dict[str, re.Pattern]]:
        return {self.key: {"$regex": self.value__pattern}}


class Contains(RegexFilter):
    ...


class StartsWith(RegexFilter):
    @property
    def value__pattern(self) -> re.Pattern:
        return re.compile(f"^{self.value}", self.flags)


class EndsWith(RegexFilter):
    @property
    def value__pattern(self) -> re.Pattern:
        return re.compile(f"{self.value}$", self.flags)


class F: # FilterFacade
    __registry__ = {
        "eq": Eq,
        "ne": Ne,
        "neq": Ne,
        "gt": Gt,
        "gte": Gte,
        "lt": Lt,
        "lte": Lte,
        "in": In,
        "nin": NotIn,
        "notin": NotIn,
        "exists": Exists,
        "nexists": NotExists,
        "notexists": NotExists,
        "contains": Contains,
        "icontains": lambda k, v: Contains(k, v, flags=re.IGNORECASE),
        "startswith": StartsWith,
        "istartswith": lambda k, v: StartsWith(k, v, flags=re.IGNORECASE),
        "endswith": EndsWith,
        "iendswith": lambda k, v: EndsWith(k, v, flags=re.IGNORECASE),
        "null": IsNull,
        "isnull": IsNull,
        "notnull": IsNotNull,
        "isnotnull": IsNotNull,
    }

    @classmethod
    def filter(cls, entries: dict[str, any]):
        query = {}
        
        for entry in entries.items():
            key, value = entry

            if key.startswith("__"):
                continue

            operator = "eq"
            if "__" in key:
                key, operator = key.rsplit("__", maxsplit=1)

            try:
                filter_cls = cls.__registry__.get(operator)
                if not filter_cls:
                    allowed_operators = ", ".join(cls.__registry__.keys())
                    raise exceptions.BadRequest(f"Invalid filter operator: '{operator}'. Allowed: {allowed_operators}")

                if isinstance(value, list) and operator in ['eq', 'ne', 'in', 'nin']:
                    filtering = In(key, value) if operator in ['eq', 'in'] else NotIn(key, value)
                elif operator in ['eq', 'ne'] and "," in value:
                    if operator == 'eq':
                        in_filter = In(key, value)
                        filtering = Or(filter_cls(key, value), in_filter, In(key, in_filter.value__list_with_numerics))
                    else:
                        nin_filter = NotIn(key, value)
                        filtering = Or(filter_cls(key, value), nin_filter, NotIn(key, nin_filter.value__list_with_numerics))
                else:
                    filtering = filter_cls(key, value)
                
                if utils.is_numeric(value) and not isinstance(filtering, RegexFilter):
                        filtering = Or(filtering, filter_cls(key, utils.to_number(value)))
                elif isinstance(filtering, ListFilter):
                    filtering = Or(filtering, filter_cls(key, filtering.value__list_with_numerics))

                query |= filtering()
            except ValueError as e: # TODO create FilterError
                raise exceptions.BadRequest(f"({entry[0]}={entry[1]}) {e}")

        return query

    @classmethod
    def find(cls, id):
        find = Or()
        id_num = utils.to_number(id)

        if id_num != None:
            for key in __id_keys_candidates__:
                find << Or(Eq(key, id), Eq(key, id_num))
        else:
            for key in __id_keys_candidates__:
                find << Eq(key, id)

        return find()
