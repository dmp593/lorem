from pydantic import BaseModel


class IndexRequest(BaseModel):
    keys: list[str] | dict[str, str | int]
    unique: bool

    class Config:
        orm_mode = True
