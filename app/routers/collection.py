from fastapi import APIRouter
from fastapi import Depends, Request, status
from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorCollection
from pymongo.results import InsertOneResult, InsertManyResult, DeleteResult

from app import exceptions, paginator as pag
from app.dependencies import get_collection, verify_collection_name
from app.filters import F

router = APIRouter(
    dependencies=[Depends(verify_collection_name(path_index=1))]
)


@router.get("/{collection}")
async def get_many(pag_req: pag.PaginatedRequest = Depends(pag.paginated_request), collection: AsyncIOMotorCollection = Depends(get_collection)):
    cursor = collection.find(pag_req.query, { "_id": 0 })
    documents = await cursor.skip(pag_req.offset).to_list(pag_req.limit)
    total_count = await collection.count_documents(pag_req.query)
    return pag.paginated_response(documents, total_count, pag_req)


@router.get("/{collection}/{id}")
async def get_one(id: str, collection: AsyncIOMotorCollection = Depends(get_collection)):
    document = await collection.find_one(F.find(id), { "_id": 0 })

    if not document:
        raise exceptions.NotFound()

    return document


async def insert_many(documents: list[any], db_collection: AsyncIOMotorCollection) -> list[any]:
    result: InsertManyResult = await db_collection.insert_many(documents)

    if not result.acknowledged:
        raise exceptions.BadRequest()

    for document in documents:
        document.pop("_id")

    return documents


async def insert_one(document: any, db_collection: AsyncIOMotorCollection) -> list[any]:
    result: InsertOneResult = await db_collection.insert_one(document)

    if not result.acknowledged:
        raise exceptions.BadRequest()

    document.pop("_id")
    return document


@router.post("/{collection}", status_code=status.HTTP_201_CREATED)
async def insert_one_or_many(request: Request, collection: AsyncIOMotorCollection = Depends(get_collection)):
    json = await request.json()

    return await (
        insert_many(json, collection) if isinstance(json, list) else insert_one(json, collection)
    )


@router.delete("/{collection}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_many(request: Request, collection: AsyncIOMotorCollection = Depends(get_collection)):
    query = F.filter(request.query_params)

    if not query:
        return await collection.drop()

    result: DeleteResult = await collection.delete_many(query)

    if not result.acknowledged:
        raise exceptions.BadRequest()


@router.delete("/{collection}/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_one(id: str, collection: AsyncIOMotorCollection = Depends(get_collection)):
    document = await collection.delete_one(F.find(id), { "_id": 0 })

    if not document:
        raise exceptions.NotFound()

    return document
