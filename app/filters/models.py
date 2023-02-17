import re

from typing import Self

from app.filters import converters


class Filter:
    operator = None

    def __init__(self, key: str, value: any) -> None:
        self.key = key
        self.value = value

    def __call__(self) -> dict[str, any]:
        if not self.operator:
            return {self.key: self.value}
        
        return {
            self.key: {
                self.operator: self.value
            }
        }


class GroupFilter(Filter):
    def __init__(self, *value: tuple[Filter | dict]) -> None:
        self.value = list(value)
    
    def __lshift__(self, rhs) -> Self:
        self.value.append(rhs)
        return self

    def __call__(self) -> dict[str, any]:
        return {
            self.operator: [
                value() if callable(value) else value 
                for value in self.value
            ]
        }


class And(GroupFilter):
    operator = '$and'


class Or(GroupFilter):
    operator = '$or'


class EqualityFilter(Filter):
    def __call__(self) -> dict[str, dict[str, any]]:
        eq = {
            self.key: {
                self.operator: self.value
            }
        }
        
        if converters.value_is_numeric(self.value):
            eq_number = {
                self.key: {
                    self.operator: converters.value_as_number(self.value)
                }
            }

            return Or(eq, eq_number)()

        if converters.value_is_listable(self.value):
            eq_list = self.as_equality_list()
            return Or(eq, eq_list)()

        return eq


class Eq(EqualityFilter):
    operator = '$eq'
    names = ['eq', 'equals']

    def as_equality_list(self):
        return In(self.key, self.value)


class Ne(EqualityFilter):
    operator = '$ne'
    names = ['ne', 'neq', 'noteq', 'notequals']

    def as_equality_list(self):
        return NotIn(self.key, self.value)

class LimitsFilter(Filter):
    def __call__(self) -> dict[str, dict[str, any]]:
        limit_than = {self.key: {self.operator: self.value}}

        if converters.value_is_numeric(self.value):
            limit_than_number = {
                self.key: {
                    self.operator: converters.value_as_number(self.value)
                }
            }

            return Or(limit_than, limit_than_number)()

        return limit_than


class Gt(LimitsFilter):
    operator = '$gt'
    names = ['gt']



class Ge(LimitsFilter):
    operator = '$gte'
    names = ['ge', 'gte']


class Lt(LimitsFilter):
    operator = '$lt'
    names = ['lt']


class Le(LimitsFilter):
    operator = '$lte'
    names = ['le', 'lte']


class ListFilter(Filter):
    def __call__(self) -> dict[str, dict[str, any]]:
        or_filter = Or(
            {
                self.key: {
                    self.operator: converters.value_as_list(self.value)
                }
            },
            {
                self.key: {
                    self.operator: converters.value_as_list_with_numerics(self.value)
                }
            }
        )

        return or_filter()


class In(ListFilter):
    operator = '$in'
    names = ['in']


class NotIn(ListFilter):
    operator = '$nin'
    names = ['nin', 'notin']


class BooleanFilter(Filter):
    operator = '$exists'
    def __init__(self, key: str, value: bool | int | str = True) -> None:
        super().__init__(key, value)


class Exists(BooleanFilter):
    names = ['exists']
    
    def __call__(self) -> dict[str, dict[str, bool]]:
        return {self.key: {self.operator: converters.value_as_bool(self.value)}}


class NotExists(Exists):
    names = ['nexists', 'notexists']

    def __call__(self) -> dict[str, dict[str, bool]]:
        return {self.key: {self.operator: not converters.value_as_bool(self.value)}}


class IsNull(BooleanFilter):
    names = ['null', 'isnull']

    def __call__(self) -> And:
        is_null = And(
            Exists(self.key, True),
            (Eq if converters.value_as_bool(self.value) else Ne)(self.key, None)
        )

        return is_null()


class IsNotNull(BooleanFilter):
    names = ['nnull', 'notnull', 'isnotnull']

    def __call__(self) -> And:
        is_not_null = And(
            Exists(self.key, True),
            (Ne if converters.value_as_bool(self.value) else Eq)(self.key, None)
        )

        return is_not_null()


class RegexFilter(Filter):
    operator = '$regex'
    names = ['re', 'regex']

    def __init__(self, key: str, value: str, flags: re.RegexFlag = re.RegexFlag.ASCII) -> None:
        super().__init__(key, value)
        self.flags = flags

    def __call__(self) -> dict[dict[str, re.Pattern]]:
        return {self.key: {self.operator: converters.value_as_pattern(self.value, self.flags)}}


class Contains(RegexFilter):
    names = ['contains']


class IContains(RegexFilter):
    names = ['icontains']

    def __init__(self, key: str, value: str, flags: re.RegexFlag = re.RegexFlag.ASCII) -> None:
        super().__init__(key, value, flags | re.RegexFlag.IGNORECASE)


class StartsWith(RegexFilter):
    names = ['starts', 'startswith']

    def __call__(self) -> dict[dict[str, re.Pattern]]:
        return {self.key: {self.operator: converters.value_as_pattern(f"^{self.value}", self.flags)}}


class IStartsWith(StartsWith):
    names = ['istarts', 'istartswith']

    def __init__(self, key: str, value: str, flags: re.RegexFlag = re.RegexFlag.ASCII) -> None:
        super().__init__(key, value, flags | re.RegexFlag.IGNORECASE)


class EndsWith(RegexFilter):
    names = ['ends', 'endswith']

    def __call__(self) -> dict[dict[str, re.Pattern]]:
        return {self.key: {self.operator: converters.value_as_pattern(f"{self.value}$", self.flags)}}


class IEndsWith(EndsWith):
    names = ['iends', 'iendswith']

    def __init__(self, key: str, value: str, flags: re.RegexFlag = re.RegexFlag.ASCII) -> None:
        super().__init__(key, value, flags | re.RegexFlag.IGNORECASE)
