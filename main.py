import uvicorn
import logging
from fastapi import FastAPI, HTTPException, Request
from contextlib import asynccontextmanager
from typing import Union
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.requests import Request
from api.db.database import Base, engine
from fastapi.responses import JSONResponse

from api.v1.routes.newsletter_router import router as newsletter
from api.v1.routes.product import router as product_router
from api.v1.routes.newsletter_router import (
    CustomException,
    custom_exception_handler
)

from api.v1.routes import api_version_one

Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield

app = FastAPI(lifespan=lifespan)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

app.include_router(api_version_one)

app.include_router(auth)
app.include_router(product_router, prefix="/api/v1/products", tags=["Products"])


@app.get("/", tags=["Home"])
async def get_root(request: Request) -> dict:
    return {
        "message": "Welcome to API",
        "URL": "",
    }

@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    if exc.status_code == 400:
        if exc.detail == "The query parameter 'q' is required.":
            return JSONResponse(
                status_code=400,
                content={
                    "error": "Bad Request",
                    "message": exc.detail
                }
            )
        elif exc.detail == "The query parameter 'q' must be a non-empty string.":
            return JSONResponse(
                status_code=400,
                content={
                    "error": "Bad Request",
                    "message": exc.detail
                }
            )
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail
        }
    )


if __name__ == "__main__":
    uvicorn.run("main:app", port=7001, reload=True)
