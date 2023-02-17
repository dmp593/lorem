import inspect

from app.core import exceptions, utils
from app.filters import models as filters

__id_keys_candidates__ = ("id", "uuid", "uid", "code", "pk", "username", "email", "vat",)


class F: # FilterFacade
    @classmethod
    def registry(cls) -> dict:
        registry = {}

        for _, filter_cls in inspect.getmembers(filters):
            if not isinstance(filter_cls, type):
                continue

            if not issubclass(filter_cls, filters.Filter):
                continue

            if not hasattr(filter_cls, 'names'):
                continue
            
            for name in filter_cls.names:
                registry[name] = filter_cls

        return registry

    @classmethod
    def query(cls, entries: dict[str, any]):
        query = {}
        
        for entry in entries.items():
            key, value = entry

            if key.startswith("__"):
                continue

            operator = "eq"
            if "__" in key:
                key, operator = key.rsplit("__", maxsplit=1)

            try:
                filter_cls = cls.registry().get(operator)
                if not filter_cls:
                    allowed_operators = ", ".join(cls.registry().keys())
                    raise exceptions.BadRequest(f"Invalid filter operator: '{operator}'. Allowed: {allowed_operators}")

                if isinstance(value, list) and operator in ['eq', 'ne', 'in', 'nin']:
                    filtering = filters.In(key, value) if operator in ['eq', 'in'] else filters.NotIn(key, value)
                elif operator in ['eq', 'ne'] and "," in value:
                    if operator == 'eq':
                        in_filter = filters.In(key, value)
                        filtering = filters.Or(filter_cls(key, value), in_filter, filters.In(key, in_filter.value__list_with_numerics))
                    else:
                        nin_filter = filters.NotIn(key, value)
                        filtering = filters.Or(filter_cls(key, value), nin_filter, filters.NotIn(key, nin_filter.value__list_with_numerics))
                else:
                    filtering = filter_cls(key, value)
                
                if utils.is_numeric(value) and not isinstance(filtering, filters.RegexFilter):
                        filtering = filters.Or(filtering, filter_cls(key, utils.to_number(value)))
                elif isinstance(filtering, filters.ListFilter):
                    filtering = filters.Or(filtering, filter_cls(key, filtering.value__list_with_numerics))

                query |= filtering()
            except ValueError as e: # TODO create FilterError
                raise exceptions.BadRequest(f"({entry[0]}={entry[1]}) {e}")

        return query

    @classmethod
    def find(cls, id):
        find = filters.Or()
        id_num = utils.to_number(id)

        if id_num != None:
            for key in __id_keys_candidates__:
                find << filters.Or(filters.Eq(key, id), filters.Eq(key, id_num))
        else:
            for key in __id_keys_candidates__:
                find << filters.Eq(key, id)

        return find()
