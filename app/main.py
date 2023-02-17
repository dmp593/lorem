import os
import logging

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse


from app import faker, filters, tokens, indexes, versions, resources


log_level = os.environ.get('LOG_LEVEL', 'info')
logging.basicConfig(level=log_level.upper())


app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)


@app.exception_handler(filters.exceptions.FilterError)
async def filter_error_exception_handler(request: Request, error: filters.exceptions.FilterError):
    return JSONResponse(
        {
            'key': error.key,
            'value': error.value,
            'reason': error.reason,
            'detail': str(error)
        },
        status_code=status.HTTP_400_BAD_REQUEST
    )


@app.exception_handler(filters.exceptions.FilterOperatorNotExistsError)
async def filter_operator_not_exists_exception_handler(request: Request, error: filters.exceptions.FilterOperatorNotExistsError):
    return JSONResponse(
        {
            'operator': error.invalid_operator,
            'allowed': error.allowed_operators,
            'detail': str(error)
        },
        status_code=status.HTTP_400_BAD_REQUEST
    )


app.include_router(tokens.router)
app.include_router(faker.router)
app.include_router(indexes.router)
app.include_router(versions.router)
app.include_router(resources.router)
