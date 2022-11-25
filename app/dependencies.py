import os

from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection, AsyncIOMotorDatabase


def get_connection_string() -> str:
    driver: str = 'mongodb'
    username: str = os.environ['DB_USER']
    password: str = os.environ['DB_PASS']
    host: str = os.environ['DB_HOST']
    port: str = os.environ['DB_PORT']

    return f"{driver}://{username}:{password}@{host}:{port}/"


def get_client(conn_str: str = Depends(get_connection_string)) -> AsyncIOMotorClient:
    # set a 5-second connection timeout
    return AsyncIOMotorClient(conn_str, serverSelectionTimeoutMS=5000)

def get_db(client: AsyncIOMotorClient = Depends(get_client), db_name: str = 'lorem') -> AsyncIOMotorDatabase:
    return client[db_name]


def get_db_collection(collection: str, db: AsyncIOMotorDatabase = Depends(get_db)) -> AsyncIOMotorCollection:
    return db[collection]
