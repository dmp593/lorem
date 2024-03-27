from fastapi import exceptions, status


Headers = dict[str, any] | None


class BadRequest(exceptions.HTTPException):
    def __init__(self, detail: any = "Bad Request", headers: Headers = None) -> None:
        super().__init__(status.HTTP_400_BAD_REQUEST, detail, headers)


class Forbidden(exceptions.HTTPException):
    def __init__(self, detail: any = "Forbidden", headers: Headers = None) -> None:
        super().__init__(status.HTTP_403_FORBIDDEN, detail, headers)


class NotFound(exceptions.HTTPException):
    def __init__(self, detail: any = "Not Found", headers: Headers = None) -> None:
        super().__init__(status.HTTP_404_NOT_FOUND, detail, headers)


class Unauthorized(exceptions.HTTPException):
    def __init__(self, detail: any = "Unauthorized", headers: Headers = None) -> None:
        super().__init__(status.HTTP_401_UNAUTHORIZED, detail, headers)
