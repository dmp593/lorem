from fastapi import Query

from app.schemas import CamelModel

class PageRequest:
    def __init__(self, offset: int, limit: int) -> None:
        self.offset = offset
        self.limit = limit

    @staticmethod
    def from_query(offset: int = Query(default=0, alias='__offset'), limit: int = Query(default=30,  alias='__limit')):
        return PageRequest(offset, limit)


class PaginatedMetadataResponse(CamelModel):
    length: int = 0
    count: int = 0
    total_count: int = 0
    previous_offset: int = 0
    next_offset: int | None = 0
    limit: int = 0


class PaginatedResponse(CamelModel):
    data: list
    metadata: PaginatedMetadataResponse

    @classmethod
    def render(cls, page: PageRequest, data, total_count) -> None:
        metadata = PaginatedMetadataResponse(
            length=len(data),
            total_count=total_count,
            previous_offset=page.offset,
            limit=page.limit
        )
        

        if page.offset <= total_count:
            metadata.count=page.offset + metadata.length
            metadata.next_offset=metadata.count
        else:
            metadata.count = total_count
            metadata.next_offset = None
        

        return PaginatedResponse(data=data, metadata=metadata)
