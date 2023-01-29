import os
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


from app.routers import collection, indexes, tokens


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


app.include_router(indexes.router)
app.include_router(tokens.router)
app.include_router(collection.router)
