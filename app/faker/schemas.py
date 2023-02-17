import typing

from pydantic import Field

from app.core.schemas import CamelModel


class FakerSchema(CamelModel):
    fake: typing.List[str]
    size: int = Field(1, gt=0)

    class Config:
        orm_mode = True
