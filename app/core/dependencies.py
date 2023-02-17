import os

from functools import cache

from fastapi import Depends, Path, Request
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection, AsyncIOMotorDatabase

from app.core import tokens


@cache
def get_mongodb_connection_str() -> str:
    username: str | None = os.environ.get("DB_USER", None)
    password: str| None = os.environ.get("DB_PASS", None)
    host: str = os.environ.get("DB_HOST", "localhost")
    port: str = os.environ.get("DB_PORT", "27017")

    if not username or not password:
        return f"mongodb://{host}:{port}/"

    return f"mongodb://{username}:{password}@{host}:{port}/"


def get_client(conn_str: str = Depends(get_mongodb_connection_str)) -> AsyncIOMotorClient:
    # set a 3-second connection timeout
    return AsyncIOMotorClient(conn_str, serverSelectionTimeoutMS=3000)


def get_db(request: Request, client: AsyncIOMotorClient = Depends(get_client)) -> AsyncIOMotorDatabase:
    db_name = tokens.extract(request.headers)
    return client[db_name]


def get_collection(resource: str, db: AsyncIOMotorDatabase = Depends(get_db)) -> AsyncIOMotorCollection:
    return db[resource]


def get_collection_version(resource: str, version: int = Path(ge=0), db: AsyncIOMotorDatabase = Depends(get_db)) -> AsyncIOMotorCollection:
    return get_collection(f"@v{version}-{resource}", db)
