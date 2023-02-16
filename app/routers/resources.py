from fastapi import APIRouter
from fastapi import Depends, Query, Request, status

from app import exceptions
from app.repositories.collection import CollectionRepository
from app.dependencies import get_filters, verify_collection_name
from app.schemas.paginated import PageRequest, PaginatedResponse


router = APIRouter(
    tags=["resources"],
    dependencies=[Depends(verify_collection_name(path_index=1))]
)


@router.get("/{resource}")
async def get_many(filters = Depends(get_filters), page = Depends(PageRequest), repository: CollectionRepository = Depends()):
    documents = await repository.list(filters, page.offset, page.limit)
    total_count = await repository.count(filters)

    return PaginatedResponse.render(page, documents, total_count)


@router.get("/{resource}/{id}")
async def get_one(id: str, repository: CollectionRepository = Depends()):
    document = await repository.get(id)

    if not document:
        raise exceptions.NotFound()

    return document


@router.post("/{resource}", status_code=status.HTTP_201_CREATED)
async def insert_one_or_many(request: Request, repository: CollectionRepository = Depends()):
    json = await request.json()
    return await repository.insert_one_or_many(json)


@router.delete("/{resource}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_many(filters = Depends(get_filters), repository: CollectionRepository = Depends()) -> None:
    if not await repository.delete_many(filters):
        raise exceptions.BadRequest()


@router.delete("/{resource}/{id}", status_code=status.HTTP_204_NO_CONTENT) 
async def delete_one(id: str, repository: CollectionRepository = Depends()) -> None:
    document = await repository.delete_one(id)

    if not document:
        raise exceptions.NotFound()
