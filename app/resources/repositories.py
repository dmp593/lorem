from typing import Self
from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorCollection
from pymongo.results import InsertOneResult, InsertManyResult, DeleteResult

from app.core.dependencies import get_collection, get_collection_version


class ResourceRepository:
    def __init__(self, collection: AsyncIOMotorCollection = Depends(get_collection)) -> None:
        self.collection = collection
        self.projection = { "_id": 0 } # default projection

    @classmethod
    def versioned(cls, collection: AsyncIOMotorCollection = Depends(get_collection_version)) -> Self:
        return cls(collection)

    async def count(self, query: dict) -> int:
        return await self.collection.count_documents(query)

    async def list(self, query: dict, offset: int, limit: int = 30):
        cursor = self.collection.find(query, self.projection)
        return await cursor.skip(offset).to_list(limit)

    async def get(self, query: dict) -> dict | None:
        return await self.collection.find_one(query, self.projection)

    async def insert_many(self, documents: list):
        result: InsertManyResult = await self.collection.insert_many(documents)

        if not result.acknowledged:
            return None

        for document in documents:
            document.pop("_id")

        return documents

    async def insert_one(self, document: dict) -> dict | None:
        result: InsertOneResult = await self.collection.insert_one(document)

        if not result.acknowledged:
            return None

        document.pop("_id")
        return document

    async def insert_one_or_many(self, data):
        return await (
            self.insert_many(data) if isinstance(data, list) else self.insert_one(data)
        )

    async def delete_one(self, query: dict):
        return await self.collection.delete_one(query, self.projection)

    async def delete_many(self, query: dict) -> bool:
        if not query:
            return await self.collection.drop()

        result: DeleteResult = await self.collection.delete_many(query)
        return result.acknowledged
