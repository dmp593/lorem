from collections import namedtuple
from app.schemas import CamelModel


PaginatedRequest = namedtuple('PaginatedRequest', ['query', 'offset', 'limit'])


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
