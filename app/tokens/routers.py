from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorClient

from app.core import dependencies, tokens
from app.tokens.schemas import TokenRequest, TokenResponse


router = APIRouter(prefix="/@tokens", tags=["tokens"])


@router.post("")
async def generate(request: TokenRequest, client: AsyncIOMotorClient = Depends(dependencies.get_client)) -> TokenResponse:
    cursor = await client.list_databases()
    cursor_coroutine = cursor.to_list(length=None)
    
    new_token = tokens.validators.generate(request.length)
    dbs = await cursor_coroutine
    
    while new_token in dbs:
        new_token = tokens.validators.generate(request.length)
    
    return TokenResponse(token=new_token)
