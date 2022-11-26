from typing import Any, Dict

from fastapi import Request


def is_truthful(value):
    return value in [True, 1, 'true', 'TRUE', 'True', 'yes', 'YES', 'Yes', 'y', '1']


def parse_filters(raw_filters: Dict[str, Any]):
    filters = {}

    for key, value in raw_filters.items():
        if key.startswith('$$'): # instruction to include the '$' sign, because it conflicts with the API. for example: $limit and $offset
            key = key[1:]
        elif key.startswith('$'):
            continue

        key_and_operand = key.split('__', maxsplit=1)
        operand = 'eq'

        if len(key_and_operand) == 2:
            key, operand = key_and_operand
            
        if ',' in value:
            value = value.split(',')

        else:
            try:
                value = float(value)

                if value.is_integer():
                    value = int(value)

            except ValueError:
                ...
        
        if operand == 'isnull':
            filters[key] = { '$exists': True, '$eq' if is_truthful(value) else '$neq': None }
        elif operand == 'exists':
            filters[key] = { '$exists': is_truthful(value) }
        else:
            filters[key] = { f'${operand}': value }

    return filters


def parse_query_params(request: Request):
    return {
        'limit': request.get('$limit', 100),
        'offset': request.get('$offset', 0),
        'filters': parse_filters(request.query_params)
    }
