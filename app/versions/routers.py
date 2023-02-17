from fastapi import APIRouter

from fastapi import Depends, Request, status

from app.core import exceptions
from app.core.dependencies import verify_resource_name
from app.resources.repositories import ResourceRepository
from app.core.schemas import PageRequest, PaginatedResponse
from app.filters.dependencies import get_filters


router = APIRouter(
    prefix="/@v",
    tags=["versions"],
    dependencies=[Depends(verify_resource_name(path_index=2))]
)


@router.get("{version:int}/{resource}")
async def get_many(filters = Depends(get_filters), page = Depends(PageRequest), repository: ResourceRepository = Depends(ResourceRepository.versioned)):
    documents = await repository.list(filters, page.offset, page.limit)
    total_count = await repository.count(filters)

    return PaginatedResponse.render(page, documents, total_count)


@router.get("{version:int}/{resource}/{id}")
async def get_one(id: str, repository: ResourceRepository = Depends(ResourceRepository.versioned)):
    document = await repository.get(id)

    if not document:
        raise exceptions.NotFound()

    return document


@router.post("{version:int}/{resource}", status_code=status.HTTP_201_CREATED)
async def insert_one_or_many(request: Request, repository: ResourceRepository = Depends(ResourceRepository.versioned)):
    json = await request.json()
    return await repository.insert_one_or_many(json)


@router.delete("{version:int}/{resource}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_many(filters = Depends(get_filters), repository: ResourceRepository = Depends(ResourceRepository.versioned)) -> None:
    if not await repository.delete_many(filters):
        raise exceptions.BadRequest()


@router.delete("{version:int}/{resource}/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_one(id: str, repository: ResourceRepository = Depends(ResourceRepository.versioned)) -> None:
    document = await repository.delete_one(id)

    if not document:
        raise exceptions.NotFound()
