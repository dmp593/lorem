from typing import Any, Dict

from fastapi import Request


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

        key_and_operand = key.split('__', maxsplit=1)
        operand = 'eq'

        if len(key_and_operand) == 2:
            key, operand = key_and_operand
            
        if ',' in value:
            value = [to_number(v, converter=float, or_default=v) for v in value.split(',')]
        else:
            value = to_number(value, converter=float, or_default=value)
        
        if operand == 'isnull':
            filters[key] = { '$exists': True, '$eq' if is_truthful(value) else '$ne': None }
        elif operand == 'exists':
            filters[key] = { '$exists': is_truthful(value) }
        elif operand == 'in' and not isinstance(value, list):
            filters[key] = { f'${operand}': [value] }
        else:
            filters[key] = { f'${operand}': value }

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
