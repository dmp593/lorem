from fastapi import Request

from app import utils
from app.filters import F
from app.schemas.paginated import PaginatedRequest, PaginatedMetadataResponse, PaginatedResponse


def paginated_request(request: Request) -> PaginatedRequest:
    return PaginatedRequest(
        limit=utils.to_number(request.query_params.get("__limit"), 15),
        offset=utils.to_number(request.query_params.get("__offset"), 0),
        query=F.filter(request.query_params),
    )


def paginated_response(data: list[any], total_count: int, request: PaginatedRequest):
    data_length = len(data)
    
    metadata = PaginatedMetadataResponse(
        length=data_length,
        total_count=total_count,
        previous_offset=request.offset,
        limit=request.limit
    )
    
    if request.offset <= total_count:
        metadata.count=request.offset + data_length
        metadata.next_offset=metadata.count
    else:
        metadata.count = total_count
        metadata.next_offset = None

    return PaginatedResponse(data=data, metadata=metadata)
