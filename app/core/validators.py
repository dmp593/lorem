import typing

from fastapi import Request

from app.core import exceptions


def validate_resource_name(path_index: int) -> typing.Callable[[Request,], None]:
    def wrapper(request: Request):
        resource = request.url.path.split('/')[path_index]

        if resource.startswith('@'):
            raise exceptions.Forbidden(f"Invalid resource name: {resource}. Please favor strict alphanumeric characters.")  
    
    return wrapper
