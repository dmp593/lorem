import re

from enum import StrEnum
from typing import Any, Dict, Self
from fastapi import Request

from app.exceptions import BadRequest


__ID_PATHS__ = ('id', 'uuid', 'code', 'pk', 'username', 'email',)


def tonum(value: Any, default: int | None = None, converter: int | float = int):
    if isinstance(value, converter):
        return value
    
    try:
        return converter(value)
    except (TypeError, ValueError):
        return default


class Filter:
    def __init__(self, key: str, value: Any) -> None:
        self.key = key
        self.value = value

    def __call__(self) -> dict[str, Any]:
        return {self.key: self.value}


class GroupType(StrEnum):
    Expr = "$expr"
    And = "$and"
    Or = "$or"

class GroupFilter(Filter):
    def __init__(self, key: GroupType, *value: Filter) -> None:
        super().__init__(key.value, value)

    def __lshift__(self, rhs) -> Self:
        self.value.append(rhs)
        return self

    def __get__(self, instance=None, owner=None) -> dict[str, Any]:
        return {self.key: [value() for value in self.value]}

class And(GroupFilter):
    def __init__(self, *value: Filter) -> None:
        super().__init__(GroupType.And, *value)

class Or(GroupFilter):
    def __init__(self, *value: Filter) -> None:
        super().__init__(GroupType.Or, *value)


class Eq(Filter):
    def __call__(self) -> dict[str, dict[str, Any]]:
        return {self.key: {"$eq": self.value}}


class Ne(Filter):
    def __call__(self) -> dict[str, dict[str, Any]]:
        return {self.key: {"$ne": self.value}}


class Gt(Filter):
    def __call__(self) -> dict[str, dict[str, Any]]:
        return {self.key: {"$gt", self.value}}


class Gte(Filter):
    def __call__(self) -> dict[str, dict[str, Any]]:
        return {self.key: {"$gte", self.value}}


class Lt(Filter):
    def __call__(self) -> dict[str, dict[str, Any]]:
        return {self.key: {"$lt", self.value}}


class Lte(Filter):
    def __call__(self) -> dict[str, dict[str, Any]]:
        return {self.key: {"$lte", self.value}}


class ListFilter(Filter):
    @property
    def value__list(self):
        value = self.value
        
        if isinstance(value, list):
            return value

        if isinstance(value, str) and "," in value:
            value = [tonum(v, default=v) for v in value.split(",")]
        
        return [value]


class In(ListFilter):
    def __call__(self) -> dict[str, dict[str, Any]]:
        return {self.key: {"$in": self.value__list}}


class NotIn(ListFilter):
    def __call__(self) -> dict[str, dict[str, Any]]:
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
            
            if value_ in ['true', 'yes', 'y', '1', '']:
                return True    
            elif value_ in ['false', 'no', 'n', '0']:
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


class FiltersRegistry:
    _filters = {
        'eq': Eq,
        'ne': Ne,
        'neq': Ne,
        'gt': Gt,
        'gte': Gte,
        'lt': Lt,
        'lte': Lte,
        'in': In,
        'nin': NotIn,
        'notin': NotIn,
        'exists': Exists,
        'nexists': NotExists,
        'notexists': NotExists,
        'contains': Contains,
        'icontains': lambda k, v: Contains(k, v, flags=re.IGNORECASE),
        'startswith': StartsWith,
        'istartswith': lambda k, v: StartsWith(k, v, flags=re.IGNORECASE),
        'endswith': EndsWith,
        'iendswith': lambda k, v: EndsWith(k, v, flags=re.IGNORECASE),
        'null': IsNull,
        'isnull': IsNull,
        'notnull': IsNotNull,
        'isnotnull': IsNotNull,
    }

    @classmethod
    def parse(cls, entries: Dict[str, Any]):
        builder = {}
        
        for query_param in entries.items():
            key, value = query_param

            if key.startswith('__'):
                continue

            operator = 'eq'

            if '__' in key:
                key, operator = key.split('__', maxsplit=1)

            try:
                filter_cls = cls._filters.get(operator)

                if not filter_cls:
                    allowed_operators = ', '.join(cls._filters.keys())
                    raise BadRequest(f"Invalid filter operator: '{operator}'. Allowed: {allowed_operators}")

                filter_ = filter_cls(key, value)

                builder += filter_()
            except ValueError as e: # TODO create FilterError
                raise BadRequest(f"({query_param[0]}={query_param[1]}) {e}")

        return builder


def parse_query_params(request: Request):
    return {
        "limit": tonum(request.query_params.get('__limit'), 100),
        "offset": tonum(request.query_params.get('__offset'), 0),
        "filters": FiltersRegistry.parse(request.query_params),
    }


def smart_find_by_id(id):
    or_filter = Or()
    [or_filter << Eq(key, id) for key in __ID_PATHS__]
    return or_filter
