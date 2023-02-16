from typing import Self
from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorCollection
from pymongo.results import InsertOneResult, InsertManyResult, DeleteResult

from app.dependencies import get_collection, get_collection_version
from app.filters import F


class CollectionRepository:
    def __init__(self, collection: AsyncIOMotorCollection = Depends(get_collection)) -> None:
        self.collection = collection
        self.projection = { "_id": 0 } # default projection

    @classmethod
    def versioned(cls, collection: AsyncIOMotorCollection = Depends(get_collection_version)) -> Self:
        return cls(collection)

    async def count(self, filters: dict) -> int:
        query = F.query(filters)
        return await self.collection.count_documents(query)

    async def list(self, filters: dict, offset: int, limit: int = 30):
        query = F.query(filters)
        cursor = self.collection.find(query, self.projection)
        return await cursor.skip(offset).to_list(limit)

    async def get(self, id: str) -> dict | None:
        query = F.find(id)
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

    async def delete_one(self, id: str):
        query = F.find(id)
        return await self.collection.delete_one(query, self.projection)

    async def delete_many(self, filters: dict) -> bool:
        if not filters:
            return await self.collection.drop()

        query = F.query(filters)
        result: DeleteResult = await self.collection.delete_many(query)
        return result.acknowledged
