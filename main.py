import uvicorn
from contextlib import asynccontextmanager
from typing import Union
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.requests import Request

from api.db.database import Base, engine
from api.v1.routes.products import product_router

from exceptions import validation_exception_handler

Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield

version = 'v1'

app = FastAPI(lifespan=lifespan, version=version)

    

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

app.include_router(product_router, prefix=f"/api/{version}/products", tags=['products'])
app.add_exception_handler(RequestValidationError, validation_exception_handler)

# app.include_router(auth, tags=["Auth"])
# app.include_router(users, tags=["Users"])



@app.get("/", tags=["Home"])
async def get_root(request: Request) -> dict:
    return {
        "message": "Welcome to API",
        "URL": "",
    }


if __name__ == "__main__":
    uvicorn.run("main:app", port=7001, reload=True)
