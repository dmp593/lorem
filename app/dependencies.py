import os

from functools import cache

from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection, AsyncIOMotorDatabase

from app.token import TokenHeader


@cache
def get_mongodb_connection_str() -> str:
    username: str | None = os.environ.get('DB_USER', None)
    password: str| None = os.environ.get('DB_PASS', None)
    host: str = os.environ.get('DB_HOST', 'localhost')
    port: str = os.environ.get('DB_PORT', '27017')

    if not username or not password:
        return f"mongodb://{host}:{port}/"

    return f"mongodb://{username}:{password}@{host}:{port}/"


def get_client(conn_str: str = Depends(get_mongodb_connection_str)) -> AsyncIOMotorClient:
    # set a 3-second connection timeout
    return AsyncIOMotorClient(conn_str, serverSelectionTimeoutMS=3000)


def get_db(client: AsyncIOMotorClient = Depends(get_client), x_token: str = TokenHeader) -> AsyncIOMotorDatabase:
    return client[x_token]


def get_collection(collection: str, db: AsyncIOMotorDatabase = Depends(get_db)) -> AsyncIOMotorCollection:
    return db[collection]
