from fastapi import exceptions, status


Headers =  dict[str, any] | None


class BadRequest(exceptions.HTTPException):
    def __init__(self, detail: any = "Bad Request", headers: Headers = None) -> None:
        super().__init__(status.HTTP_400_BAD_REQUEST, detail, headers)


class NotFound(exceptions.HTTPException):
    def __init__(self, detail: any = "Not Found", headers: Headers = None) -> None:
        super().__init__(status.HTTP_404_NOT_FOUND, detail, headers)
