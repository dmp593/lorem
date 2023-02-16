import typing

from pydantic import Field

from app.schemas.camel import CamelModel


class FakerSchema(CamelModel):
    fake: typing.List[str]
    size: int = Field(1, gt=0)

    class Config:
        orm_mode = True
