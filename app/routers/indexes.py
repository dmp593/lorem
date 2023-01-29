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
        collection = db[collection_info.get('name')]
        indexes[collection.name] = await get_indexes(collection)

    return indexes


@router.get("/{collection}", status_code=status.HTTP_200_OK, dependencies=[Depends(verify_collection_name(path_index=2))])
async def list_collection_indexes(collection: AsyncIOMotorCollection = Depends(get_collection)):
    return await get_indexes(collection)


@router.patch("/{collection}", status_code=status.HTTP_201_CREATED, dependencies=[Depends(verify_collection_name(path_index=2))])
async def create_index(index: indexes.IndexRequest, collection: AsyncIOMotorCollection = Depends(get_collection)):
    if isinstance(index.keys, list):
        index.keys = {key: "asc" for key in index.keys}
    
    for k, v in index.keys.items():
        match v.lower():
            case "asc" | "ascending" | "1" | 1:
                index.keys[k] = pymongo.ASCENDING
            case "desc" | "descending" | "-1" | -1:
                index.keys[k] = pymongo.DESCENDING
            case "geo2d" | "2d":
                index.keys[k] = pymongo.GEO2D
            case "geo" | "geosphere" | "2dsphere":
                index.keys[k] = pymongo.GEOSPHERE
            case "hash" | "hashed":
                index.keys[k] = pymongo.HASHED
            case "txt" | "text":
                index.keys[k] = pymongo.TEXT
            case _:
                raise exceptions.BadRequest("Invalid index configuration")
    
    try:
        return await collection.create_index(index.keys.items(), unique=index.unique)
    except pymongo_errors.OperationFailure:
        raise exceptions.BadRequest()


@router.delete("/{collection}/{index}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(verify_collection_name(path_index=2))])
async def drop_collection_index(collection: AsyncIOMotorCollection = Depends(get_collection), index: str = Path()):
    return await collection.drop_index(index)


@router.delete("/{collection}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(verify_collection_name(path_index=2))])
async def drop_collection_indexes(collection: AsyncIOMotorCollection = Depends(get_collection)):
    return await collection.drop_indexes()


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
async def drop_all_indexes(db: AsyncIOMotorDatabase = Depends(get_db)):
    collections_info = await db.list_collections()

    for collection_info in collections_info:
        await db[collection_info.get('name')].drop_indexes()
