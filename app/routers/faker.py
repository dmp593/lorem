from fastapi import APIRouter, Depends, status

from app import exceptions
from app.dependencies import verify_collection_name
from app.repositories.collection import CollectionRepository
from app.schemas.faker import FakerSchema
from app.services.faker import FakerService


router = APIRouter(prefix="/@faker", tags=["faker"])


@router.post("/", status_code=status.HTTP_200_OK)
def plan(schema: FakerSchema, faker: FakerService = Depends()):
    return faker.fake(schema)


@router.post("/{resource}", status_code=status.HTTP_200_OK, dependencies=[Depends(verify_collection_name(path_index=2))])
async def apply(schema: FakerSchema, faker: FakerService = Depends(), repository: CollectionRepository = Depends()):
    faked = faker.fake(schema)
    return await repository.insert_one_or_many(faked)