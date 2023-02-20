from fastapi import APIRouter, Depends, Request, status

from app.core.validators import validate_resource_name
from app.resources.repositories import ResourceRepository
from app.faker.services import FakerService


router = APIRouter(prefix="/@faker", tags=["faker"])


@router.post("/", status_code=status.HTTP_200_OK)
async def plan(request: Request, faker: FakerService = Depends()):
    json = await request.json()
    return faker.fake(json)


@router.post("/{resource}", status_code=status.HTTP_200_OK, dependencies=[Depends(validate_resource_name(path_index=2))])
async def apply(request: Request, faker: FakerService = Depends(), repository: ResourceRepository = Depends()):
    json = await request.json()
    faked = faker.fake(json)
    
    return await repository.insert_one_or_many(faked)
