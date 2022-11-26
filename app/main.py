from typing import Any

from motor.motor_asyncio import AsyncIOMotorCollection
from pymongo.results import InsertOneResult, DeleteResult
from fastapi import FastAPI, Depends, Request, exceptions, status

from dependencies import get_db_collection
from filters import parse_query_params

app = FastAPI()


@app.get("/{collection}/")
async def post(request: Request, collection: AsyncIOMotorCollection = Depends(get_db_collection)):
    query_params = parse_query_params(request)

    cursor = collection.find(query_params['filters'], { '_id': 0 })

    documents = await cursor.skip(query_params['offset']).to_list(query_params['limit'])
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
