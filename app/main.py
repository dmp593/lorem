from typing import Any, List

from motor.motor_asyncio import AsyncIOMotorCollection
from pymongo.results import InsertOneResult, InsertManyResult, DeleteResult
from fastapi import FastAPI, Depends, Request, exceptions, status

from dependencies import get_db_collection
from filters import smart_find_by_id, parse_query_params

app = FastAPI()


@app.get("/{collection}/")
async def post(request: Request, collection: AsyncIOMotorCollection = Depends(get_db_collection)):
    query_params = parse_query_params(request)

    cursor = collection.find(query_params['filters'], { '_id': 0 })

    documents = await cursor.skip(query_params['offset']).to_list(query_params['limit'])
    return documents[0] if len(documents) == 1 else documents


@app.get("/{collection}/{id}/")
async def post(id: str, collection: AsyncIOMotorCollection = Depends(get_db_collection)):
    document = await collection.find_one(smart_find_by_id(id), { '_id': 0 })

    if not document:
        raise exceptions.HTTPException(status.HTTP_404_NOT_FOUND, 'Not Found')

    return document


async def insert_many(documents: List[Any], db_collection: AsyncIOMotorCollection) -> List[Any]:
    result: InsertManyResult = await db_collection.insert_many(documents)

    if not result.acknowledged:
        raise exceptions.HTTPException(status.HTTP_400_BAD_REQUEST, 'Bad Request')

    for document in documents:
        document.pop('_id')

    return documents


async def insert_one(document: Any, db_collection: AsyncIOMotorCollection) -> List[Any]:
    result: InsertOneResult = await db_collection.insert_one(document)

    if not result.acknowledged:
        raise exceptions.HTTPException(status.HTTP_400_BAD_REQUEST, 'Bad Request')

    document.pop('_id')
    return document


@app.post("/{collection}/", status_code=status.HTTP_201_CREATED)
async def post(request: Request, collection: AsyncIOMotorCollection = Depends(get_db_collection)):
    json = await request.json()

    return await (
        insert_many(json, collection) 
        if isinstance(json, list) 
        else insert_one(json, collection)
    )


@app.delete('/{collection}/', status_code=status.HTTP_204_NO_CONTENT)
async def delete(request: Request, collection: AsyncIOMotorCollection = Depends(get_db_collection)):
    result: DeleteResult = await collection.delete_many(request.query_params)
    
    if not result.acknowledged:
        raise exceptions.HTTPException(status.HTTP_400_BAD_REQUEST, 'Bad Request')


@app.delete("/{collection}/{id}/", status_code=status.HTTP_204_NO_CONTENT)
async def post(id: str, collection: AsyncIOMotorCollection = Depends(get_db_collection)):
    document = await collection.delete_one(smart_find_by_id(id), { '_id': 0 })

    if not document:
        raise exceptions.HTTPException(status.HTTP_404_NOT_FOUND, 'Not Found')

    return document
