import uvicorn
from contextlib import asynccontextmanager
from typing import Union
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.requests import Request
from api.db.database import Base, engine

from api.v1.routes.newsletter_router import router as newsletter
from api.v1.routes.newsletter_router import (
    CustomException,
    custom_exception_handler
)

from api.v1.routes.auth import auth
from api.v1.routes.roles import role
from api.v1.routes.products import product_router

from exceptions import validation_exception_handler

Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield

app = FastAPI(lifespan=lifespan)

origins = [
    "http://localhost:3000",
    "http://localhost:3001",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(CustomException, custom_exception_handler) # Newsletter custom exception registration
app.include_router(newsletter, tags=["Newsletter"])
app.add_exception_handler(RequestValidationError, validation_exception_handler)

app.include_router(auth)
app.include_router(product_router)



@app.get("/", tags=["Home"])
async def get_root(request: Request) -> dict:
    return {
        "message": "Welcome to API",
        "URL": "",
    }


if __name__ == "__main__":
    uvicorn.run("main:app", port=7001, reload=True)
