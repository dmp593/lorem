import re

from enum import StrEnum
from typing import Any, Dict, Self
from fastapi import Request

from exceptions import BadRequest


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

    def __call__(self) -> dict[str, Any]:
        print(self.value)
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

        if "," in value:
            value = [tonum(v, default=v) for v in value.split(",")]
        
        return [value]


class In(ListFilter):
    def __call__(self) -> dict[str, dict[str, Any]]:
        return {self.key: {"$in": self.value__list}}


class Nin(ListFilter):
    def __call__(self) -> dict[str, dict[str, Any]]:
        return {self.key: {"$nin": self.value__list}}


class Exists(Filter):
    def __init__(self, key: str, value: bool | int | str = True) -> None:
        super().__init__(key, value)

    @property
    def value__bool(self):
        if isinstance(self.value, bool):
            return self.value

        if isinstance(self.value, int):
            return self.value == 1

        if isinstance(self.value, str):
            return self.value.lower() in ['true', 'yes', 'y', '1']

        raise ValueError(f"{self.value}: not a valid boolean value")

    def __call__(self) -> dict[str, dict[str, bool]]:
        return {self.key: {"$exists": self.value__bool}}


class IsNull(Exists):
    def __call__(self) -> And:
        is_null = And(
            super().__call__(),
            (Eq if self.value__bool else Ne)(self.key, None)
        )

        return is_null()


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
        'gt': Gt,
        'gte': Gte,
        'lt': Lt,
        'lte': Lte,
        'in': In,
        'nin': Nin,
        'exists': Exists,
        'contains': Contains,
        'icontains': lambda k, v: Contains(k, v, flags=re.IGNORECASE),
        'startswith': StartsWith,
        'istartswith': lambda k, v: StartsWith(k, v, flags=re.IGNORECASE),
        'endswith': EndsWith,
        'iendswith': lambda k, v: EndsWith(k, v, flags=re.IGNORECASE),
        'isnull': IsNull
    }

    @classmethod
    def invalidate(cls, operator: str):
        allowed_operators = ', '.join(cls._filters.keys())
        raise BadRequest(f"Invalid filter operator: '{operator}'. Allowed: {allowed_operators}")
        

    @classmethod
    def parse(cls, entries: Dict[str, Any]):
        builder = {}
        
        for key, value in entries.items():
            if key.startswith('__'):
                continue

            key_and_operator = key.split('__', maxsplit=1)
            operator = 'eq'

            if len(key_and_operator) == 2:
                key, operator = key_and_operator

            filter_cls = cls._filters.get(operator, lambda: cls.invalidate)
            filter_ = filter_cls(key, value)

            builder.update(filter_())

        return builder


def parse_query_params(request: Request):
    return {
        "limit": tonum(request.query_params.get('__limit'), 100),
        "offset": tonum(request.query_params.get('__offset'), 0),
        "filters": FiltersRegistry.parse(request.query_params),
    }


def smart_find_by_id(id):
    id_filters = [Eq(key, id) for key in __ID_PATHS__]
    or_filter = Or(*id_filters)
    
    return or_filter()
