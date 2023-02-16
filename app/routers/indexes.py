import pymongo

from fastapi import APIRouter, Depends, Path, status
from pymongo import errors as pymongo_errors

from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorCollection

from app import exceptions
from app.dependencies import get_collection, get_db, verify_collection_name
from app.schemas import indexes


router = APIRouter(prefix="/@indexes", tags=["indexes"])


async def get_indexes(collection: AsyncIOMotorCollection):
    col_indexes = await collection.index_information()

    if len(col_indexes) == 0:
        return {}

    col_indexes.pop('_id_')

    indexes = {}

    for key, val in col_indexes.items():
        fields = {field: "asc" if order == 1 else "desc" for field, order in val['key']}
        unique = val['unique']

        indexes[key] = {'fields': fields, 'unique': unique}

    return indexes


@router.get("", status_code=status.HTTP_200_OK)
async def list_all_indexes(db: AsyncIOMotorDatabase = Depends(get_db)):
    collections_info = await db.list_collections()
    indexes = {}

    for collection_info in collections_info:
        collection_name = collection_info.get('name')
        indexes[collection_name] = await get_indexes(db[collection_name])

    return indexes


@router.get("/{resource}", status_code=status.HTTP_200_OK, dependencies=[Depends(verify_collection_name(path_index=2))])
async def list_collection_indexes(collection: AsyncIOMotorCollection = Depends(get_collection)):
    return await get_indexes(collection)


@router.patch("/{resource}", status_code=status.HTTP_201_CREATED, dependencies=[Depends(verify_collection_name(path_index=2))])
async def create_index(index: indexes.IndexRequest, collection: AsyncIOMotorCollection = Depends(get_collection)):
    try:
        return await collection.create_index(index.keys.items(), unique=index.unique)
    except pymongo_errors.OperationFailure:
        raise exceptions.BadRequest()


@router.delete("/{resource}/{index}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(verify_collection_name(path_index=2))])
async def drop_collection_index(collection: AsyncIOMotorCollection = Depends(get_collection), index: str = Path()):
    return await collection.drop_index(index)


@router.delete("/{resource}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(verify_collection_name(path_index=2))])
async def drop_collection_indexes(collection: AsyncIOMotorCollection = Depends(get_collection)):
    return await collection.drop_indexes()


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
async def drop_all_indexes(db: AsyncIOMotorDatabase = Depends(get_db)):
    collections_info = await db.list_collections()

    for collection_info in collections_info:
        collection_name = collection_info.get('name')
        await db[collection_name].drop_indexes()
