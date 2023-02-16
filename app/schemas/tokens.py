from pydantic import Field

from app.schemas import CamelModel
from app.token import TOKEN_MIN_LENGTH, TOKEN_MAX_LENGTH


class TokenRequest(CamelModel):
    length: int = Field(default=32, ge=TOKEN_MIN_LENGTH, le=TOKEN_MAX_LENGTH)


class TokenResponse(CamelModel):
    token: str

    class Config:
        schema_extra = {
            "example": {
                "token": "my-generated-str0ng-tøken"
            }
        }
