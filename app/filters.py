import re

from typing import Any, Dict

from exceptions import BadRequest

from fastapi import Request


__ALLOWED_FILTER_OPERATORS__ = [
    'eq',
    'ne',
    'gt',
    'gte',
    'lt',
    'lte',
    'in',
    'nin',
    'exists',
    'contains',
    'icontains',
    'startswith',
    'istartswith',
    'endswith',
    'iendswith',
    'isnull',
]


def is_truthful(value):
    return value in [True, 1, 'true', 'TRUE', 'True', 'yes', 'YES', 'Yes', 'y', '1']


def to_number(value: Any, or_default: int | None = None, converter: int | float = int):
    try:
        return converter(value)
    except ValueError:
        return or_default


def parse_filters(raw_filters: Dict[str, Any]):
    filters = {}

    for key, value in raw_filters.items():
        if key.startswith('__'):
            continue

        key_and_operator = key.split('__', maxsplit=1)
        operator = 'eq'

        if len(key_and_operator) == 2:
            key, operator = key_and_operator

        if operator not in __ALLOWED_FILTER_OPERATORS__:
            allowed_ops = ', '.join(__ALLOWED_FILTER_OPERATORS__)
            raise BadRequest(f"Invalid filter operator: '{operator}'. Allowed: {allowed_ops}")
        
        if ',' in value:
            value = [to_number(v, converter=float, or_default=v) for v in value.split(',')]
        else:
            value = to_number(value, converter=float, or_default=value)
        
        if operator == 'isnull':
            filters[key] = { '$exists': True, '$eq' if is_truthful(value) else '$ne': None }
        elif operator == 'exists':
            filters[key] = { '$exists': is_truthful(value) }
        elif operator == 'in' and not isinstance(value, list):
            filters[key] = { f'${operator}': [value] }
        elif operator in ['startswith', 'istartswith', 'contains', 'icontains', 'endswith', 'iendswith']:
            flags = re.RegexFlag.ASCII

            if operator.startswith('i'):
                flags, operator = re.IGNORECASE, operator[1:]
            
            if operator == 'startswith':
                value = f"^{value}"
            elif operator == 'endswith':
                value = f"{value}$"

            filters[key] = { '$regex': re.compile(value, flags), }
        else:
            filters[key] = { f'${operator}': value }

    return filters


def parse_query_params(request: Request):
    query_params = {
        'limit': 100,
        'offset': 0,
        'filters': parse_filters(request.query_params)
    }

    if '__limit' in request.query_params:
        query_params['limit'] = to_number(request.query_params['__limit'], or_default=query_params['limit'])
    
    if '__offset' in request.query_params:
        query_params['offset'] = to_number(request.query_params['__offset'], or_default=query_params['offset'])

    return query_params


def smart_find_by_id(id):
    return {
        "$or": [
            { field_name: id }
            for field_name in ('id', 'uuid', 'code', 'pk', 'username', 'email',)
        ]
    }
