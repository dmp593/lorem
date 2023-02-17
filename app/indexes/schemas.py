import pymongo

from pydantic import BaseModel, validator


class IndexRequest(BaseModel):
    keys: dict[str, str | int] | list[str]
    unique: bool

    @validator("keys")
    def keys_ascending_or_descending(cls, keys):
        if isinstance(keys, list):
            return { key: pymongo.ASCENDING for key in keys }

        for key, order in keys.items():
            match order.lower():
                case "asc" | "ascending" | "1" | 1:
                    keys[key] = pymongo.ASCENDING
                case "desc" | "descending" | "-1" | -1:
                    keys[key] = pymongo.DESCENDING
                case "geo2d" | "2d":
                    keys[key] = pymongo.GEO2D
                case "geo" | "geosphere" | "2dsphere":
                    keys[key] = pymongo.GEOSPHERE
                case "hash" | "hashed":
                    keys[key] = pymongo.HASHED
                case "txt" | "text":
                    keys[key] = pymongo.TEXT
                case _:
                    raise ValueError(f"Invalid index configuration: {key} -> {order}")
        return keys

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "keys": {
                    "username": "asc"
                },
                "unique": True
            }
        }
