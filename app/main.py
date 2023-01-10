from typing import Any, List

import pymongo

from motor.motor_asyncio import AsyncIOMotorCollection
from pymongo import errors as pymongo_errors
from pymongo.results import InsertOneResult, InsertManyResult, DeleteResult
from fastapi import FastAPI, Depends, Request, status
from fastapi.middleware.cors import CORSMiddleware

import exceptions

from dependencies import get_db_collection
from filters import smart_find_by_id, parse_query_params
from schemas import IndexRequest


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)


@app.get("/{collection}/")
async def post(request: Request, collection: AsyncIOMotorCollection = Depends(get_db_collection)):
    query_params = parse_query_params(request)

    cursor = collection.find(query_params['filters'], { '_id': 0 })

    documents = await cursor.skip(query_params['offset']).to_list(query_params['limit'])
    return documents[0] if len(documents) == 1 else documents



@app.get("/{collection}/__index/", status_code=status.HTTP_200_OK)
async def get_index(collection: AsyncIOMotorCollection = Depends(get_db_collection)):
    indexes = await collection.index_information()
    return indexes.keys()


@app.post("/{collection}/__index/", status_code=status.HTTP_201_CREATED)
async def create_index(index: IndexRequest, collection: AsyncIOMotorCollection = Depends(get_db_collection)):
    for k, v in index.keys.items():
        match v.lower():
            case 'asc' | 'ascending' | '1':
                index.keys[k] = pymongo.ASCENDING
            case 'desc' | 'descending' | '-1':
                index.keys[k] = pymongo.DESCENDING
            case 'geo2d' | '2d':
                index.keys[k] = pymongo.GEO2D
            case 'geo' | 'geosphere' | '2dsphere':
                index.keys[k] = pymongo.GEOSPHERE
            case 'hash' | 'hashed':
                index.keys[k] = pymongo.HASHED
            case 'txt' | 'text':
                index.keys[k] = pymongo.TEXT
            case _:
                raise exceptions.BadRequest("Invalid index configuration")
    
    try:
        return await collection.create_index(
            index.keys.items(),
            unique=index.unique
        )
    except pymongo_errors.OperationFailure:
        raise exceptions.BadRequest()


@app.get("/{collection}/{id}/")
async def post(id: str, collection: AsyncIOMotorCollection = Depends(get_db_collection)):
    document = await collection.find_one(smart_find_by_id(id), { '_id': 0 })

    if not document:
        raise exceptions.NotFound()

    return document


async def insert_many(documents: List[Any], db_collection: AsyncIOMotorCollection) -> List[Any]:
    result: InsertManyResult = await db_collection.insert_many(documents)

    if not result.acknowledged:
        raise exceptions.BadRequest()

    for document in documents:
        document.pop('_id')

    return documents


async def insert_one(document: Any, db_collection: AsyncIOMotorCollection) -> List[Any]:
    result: InsertOneResult = await db_collection.insert_one(document)

    if not result.acknowledged:
        raise exceptions.BadRequest()

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
        raise exceptions.BadRequest()


@app.delete("/{collection}/{id}/", status_code=status.HTTP_204_NO_CONTENT)
async def post(id: str, collection: AsyncIOMotorCollection = Depends(get_db_collection)):
    document = await collection.delete_one(smart_find_by_id(id), { '_id': 0 })

    if not document:
        raise exceptions.NotFound()

    return document
