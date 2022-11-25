from typing import Any

from motor.motor_asyncio import AsyncIOMotorCollection
from pymongo.results import InsertOneResult, DeleteResult
from fastapi import FastAPI, Depends, Request, exceptions, status

from dependencies import get_db_collection


app = FastAPI()


@app.get("/{collection}/")
async def post(request: Request, collection: AsyncIOMotorCollection = Depends(get_db_collection)):
    lookup = {}

    for key, value in request.query_params.items():
        if key == '_page_len_':
            continue

        try:
            lookup[key] = int(value)
        except ValueError:
            lookup[key] = value

        # TODO add other filter options like array filters (query value in array)

    cursor = collection.find(lookup, { '_id': 0 })

    documents = await cursor.to_list(length=request.query_params.get('_page_len_', 100))
    return documents[0] if len(documents) == 1 else documents


@app.post("/{collection}/", status_code=status.HTTP_201_CREATED)
async def post(request: Request, collection: AsyncIOMotorCollection = Depends(get_db_collection)):
    document: Any = await request.json()
    result: InsertOneResult = await collection.insert_one(document)
    
    if not result.acknowledged:
        raise exceptions.HTTPException(status.HTTP_400_BAD_REQUEST, 'Bad Request')
    
    document.pop('_id', None)
    return document


@app.delete('/{collection}/', status_code=status.HTTP_204_NO_CONTENT)
async def delete(request: Request, collection: AsyncIOMotorCollection = Depends(get_db_collection)):
    result: DeleteResult = await collection.delete_many(request.query_params)
    
    if not result.acknowledged:
        raise exceptions.HTTPException(status.HTTP_400_BAD_REQUEST, 'Bad Request')
