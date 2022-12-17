from pydantic import BaseModel


class IndexRequest(BaseModel):
    keys: dict[str, str]
    unique: bool
