import inspect

from functools import cache

from fastapi import Depends, Query, Request

from app.core import exceptions, utils
from app.filters import models as filters


@cache
def get_ids_keys_candidates() -> tuple[str]:
    return ("id", "uuid", "uid", "code", "pk", "username", "email", "vat",)


@cache
def get_filters_registry() -> dict[str, filters.Filter]:
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


def get_query_params_filters(request: Request) -> dict:
    return {key: val for key, val in request.query_params.items() if not key.startswith("__")}


def get_filter_key_and_operator(key: str) -> tuple[str, str]:
    operator = "eq" # default if not provided
    
    if "__" in key:
        key, operator = key.rsplit("__", maxsplit=1) # get provided operator

    return (key, operator)


def get_filters(query_params: dict[str, str] = Depends(get_query_params_filters), registry: dict[str, filters.Filter] = Depends(get_filters_registry)) -> dict:
    filters_ = {}
    
    for entry in query_params.items():
        key, value = entry

        if key.startswith("__"): continue

        key, operator = get_filter_key_and_operator(key)

        if operator not in registry:
            allowed_operators = ", ".join(registry.keys())
            raise exceptions.BadRequest(f"Invalid filter operator: '{operator}'. Allowed: {allowed_operators}") # TODO create FilterError
            
        filter_cls = registry.get(operator)

        try:
            filters_ |= filter_cls(key, value)()
        except ValueError as e: # TODO create FilterError
            raise exceptions.BadRequest(f"({entry[0]}={entry[1]}) {e}")

    return filters_


def get_filter_id(id: str | int | float = Query(), ids_keys_candidates: tuple[str] = Depends(get_ids_keys_candidates)) -> dict:
    filter_id = filters.Or()
    id_num = utils.to_number(id)

    if id_num != None:
        for key in ids_keys_candidates:
            filter_id << filters.Or(filters.Eq(key, id), filters.Eq(key, id_num))
    else:
        for key in ids_keys_candidates:
            filter_id << filters.Eq(key, id)

    return filter_id()
