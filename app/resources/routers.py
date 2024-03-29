from fastapi import APIRouter
from fastapi import Depends, Request, status

from app.core import exceptions
from app.resources.repositories import ResourceRepository
from app.core.validators import validate_resource_name
from app.core.schemas import PageRequest, PaginatedResponse
from app.filters.dependencies import get_filters, get_filter_id

router = APIRouter(
    tags=["resources"],
    dependencies=[Depends(validate_resource_name(path_index=1))]
)


@router.get("/{resource}")
async def get_many(filters: dict = Depends(get_filters), page = Depends(PageRequest), repository: ResourceRepository = Depends()):
    documents = await repository.list(filters, page.offset, page.limit)
    total_count = await repository.count(filters)

    return PaginatedResponse.render(page, documents, total_count)


@router.get("/{resource}/{id}")
async def get_one(id: dict = Depends(get_filter_id), repository: ResourceRepository = Depends()):
    document = await repository.get(id)

    if not document:
        raise exceptions.NotFound()

    return document


@router.post("/{resource}", status_code=status.HTTP_201_CREATED)
async def insert_one_or_many(request: Request, repository: ResourceRepository = Depends()):
    json = await request.json()
    return await repository.insert_one_or_many(json)


@router.delete("/{resource}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_many(filters: dict = Depends(get_filters), repository: ResourceRepository = Depends()) -> None:
    if not await repository.delete_many(filters):
        raise exceptions.BadRequest()


@router.delete("/{resource}/{id}", status_code=status.HTTP_204_NO_CONTENT) 
async def delete_one(id: dict = Depends(get_filter_id), repository: ResourceRepository = Depends()) -> None:
    document = await repository.delete_one(id)

    if not document:
        raise exceptions.NotFound()
