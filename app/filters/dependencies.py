import inspect

from functools import cache

from fastapi import Depends, Query, Request

from app.core import exceptions, utils
from app.filters import models as filters
from app.filters.exceptions import FilterError, FilterOperatorNotExistsError


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


def get_filter_key_and_operator(key: str, registry: dict[str, filters.Filter], raise_if_invalid_operator: bool = True) -> tuple[str, str]:
    operator = "eq" # default if not provided
    
    if "__" in key:
        key, operator = key.rsplit("__", maxsplit=1) # get provided operator

    if operator not in registry and raise_if_invalid_operator:
        raise FilterOperatorNotExistsError(operator, registry)

    return (key, operator)


def get_filters(query_params: dict[str, str] = Depends(get_query_params_filters), registry: dict[str, filters.Filter] = Depends(get_filters_registry)) -> dict:
    applied_filters = {}
    
    for entry in query_params.items():
        key, value = entry

        if key.startswith("__"): continue

        key, operator = get_filter_key_and_operator(key, registry, raise_if_invalid_operator=True)
        filter_cls = registry.get(operator)

        try:
            applied_filters |= filter_cls(key, value)()
        except ValueError as err:
            raise FilterError(key=entry[0], value=entry[1], err=err)

    return applied_filters


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
