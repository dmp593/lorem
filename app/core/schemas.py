import humps

from pydantic import BaseModel, Field


class CamelModel(BaseModel):
    model_config = {
        "alias_generator": humps.camelize,
        "populate_by_name": True
    }


class PageRequest(CamelModel):
    offset: int = Field(default=0, alias='__offset')
    limit: int = Field(default=30,  alias='__limit')


class PaginatedMetadataResponse(CamelModel):
    length: int = 0
    count: int = 0
    total_count: int = 0
    previous_offset: int | None = 0
    current_offset: int = 0
    next_offset: int | None = 0
    limit: int = 0


class PaginatedResponse(CamelModel):
    data: list
    metadata: PaginatedMetadataResponse

    @classmethod
    def render(cls, page: PageRequest, data, total_count) -> None:
        previous_offset = page.offset - page.limit
        if previous_offset < 0:
            previous_offset = None

        metadata = PaginatedMetadataResponse(
            length=len(data),
            total_count=total_count,
            previous_offset=previous_offset,
            current_offset=page.offset,
            limit=page.limit
        )
        
        if page.offset <= total_count:
            metadata.count=page.offset + metadata.length
            metadata.next_offset=metadata.count if metadata.count < total_count else None
        else:
            metadata.count = total_count
            metadata.next_offset = None
        
        return PaginatedResponse(data=data, metadata=metadata)
