from typing import Any, Dict

from fastapi import exceptions, status


Headers =  Dict[str, Any] | None


class BadRequest(exceptions.HTTPException):
    def __init__(self, detail: Any = "Bad Request", headers: Headers = None) -> None:
        super().__init__(status.HTTP_400_BAD_REQUEST, detail, headers)


class NotFound(exceptions.HTTPException):
    def __init__(self, detail: Any = "Not Found", headers: Headers = None) -> None:
        super().__init__(status.HTTP_404_NOT_FOUND, detail, headers)
