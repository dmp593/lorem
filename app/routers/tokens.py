import asyncio

from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorClient

from app import token
from app.dependencies import get_client


router = APIRouter(
    prefix='/$tokens',
    tags=['token']
)


@router.post('')
async def generate(client: AsyncIOMotorClient = Depends(get_client), length: int = token.TokenLengthBody) -> dict[str, str]:
    cursor = await client.list_databases()
    cursor_coroutine = cursor.to_list(length=None)
    
    new_token = token.generate(length)
    dbs = await cursor_coroutine
    
    while new_token in dbs:
        new_token = token.generate(length)
    
    return {'token': new_token}
