from fastapi import APIRouter

from typing import Any, List

from motor.motor_asyncio import AsyncIOMotorCollection
from pymongo.results import InsertOneResult, InsertManyResult, DeleteResult
from fastapi import Depends, Request, status

from fastapi import Depends

from app import exceptions

from app.dependencies import get_collection, verify_collection_name
from app.filters import smart_find, parse_query_params





router = APIRouter(
    dependencies=[Depends(verify_collection_name(path_index=1))]
)


@router.get("/{collection}")
async def get_many(request: Request, collection: AsyncIOMotorCollection = Depends(get_collection)):
    query_params = parse_query_params(request)
    cursor = collection.find(query_params["filters"], { "_id": 0 })

    documents = await cursor.skip(query_params["offset"]).to_list(query_params["limit"])
    return documents[0] if len(documents) == 1 else documents


@router.get("/{collection}/{id}")
async def get_one(id: str, collection: AsyncIOMotorCollection = Depends(get_collection)):
    document = await collection.find_one(smart_find(id), { "_id": 0 })

    if not document:
        raise exceptions.NotFound()

    return document


async def insert_many(documents: List[Any], db_collection: AsyncIOMotorCollection) -> List[Any]:
    result: InsertManyResult = await db_collection.insert_many(documents)

    if not result.acknowledged:
        raise exceptions.BadRequest()

    for document in documents:
        document.pop("_id")

    return documents


async def insert_one(document: Any, db_collection: AsyncIOMotorCollection) -> List[Any]:
    result: InsertOneResult = await db_collection.insert_one(document)

    if not result.acknowledged:
        raise exceptions.BadRequest()

    document.pop("_id")
    return document


@router.post("/{collection}", status_code=status.HTTP_201_CREATED)
async def insert_one_or_many(request: Request, collection: AsyncIOMotorCollection = Depends(get_collection)):
    json = await request.json()

    return await (
        insert_many(json, collection) if isinstance(json, list) else insert_one(json, collection)
    )


@router.delete("/{collection}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_many(request: Request, collection: AsyncIOMotorCollection = Depends(get_collection)):
    result: DeleteResult = await collection.delete_many(request.query_params)
    
    if not result.acknowledged:
        raise exceptions.BadRequest()


@router.delete("/{collection}/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_one(id: str, collection: AsyncIOMotorCollection = Depends(get_collection)):
    document = await collection.delete_one(smart_find(id), { "_id": 0 })

    if not document:
        raise exceptions.NotFound()

    return document
