from fastapi import APIRouter, Depends, status

from app.core.dependencies import verify_resource_name
from app.resources.repositories import ResourceRepository
from app.faker.schemas import FakerSchema
from app.tokens.services import FakerService


router = APIRouter(prefix="/@faker", tags=["faker"])


@router.post("/", status_code=status.HTTP_200_OK)
def plan(schema: FakerSchema, faker: FakerService = Depends()):
    return faker.fake(schema)


@router.post("/{resource}", status_code=status.HTTP_200_OK, dependencies=[Depends(verify_resource_name(path_index=2))])
async def apply(schema: FakerSchema, faker: FakerService = Depends(), repository: ResourceRepository = Depends()):
    faked = faker.fake(schema)
    return await repository.insert_one_or_many(faked)
