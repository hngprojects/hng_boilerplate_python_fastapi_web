import uvicorn
from contextlib import asynccontextmanager
from typing import Union
from fastapi import FastAPI, status, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.requests import Request
from api.db.database import Base, engine

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

@app.exception_handler(RequestValidationError)
async def custom_request_validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "errors": [
                {
                    "field": str(err["loc"][-1]),
                    "message": err["msg"]
                }
                for err in exc.errors()
                ]
                }
            )

@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    if exc.status_code == status.HTTP_401_UNAUTHORIZED:
        status_text = "Unauthorized"
        msg = "User not authenticated"
    elif exc.status_code == status.HTTP_400_BAD_REQUEST:
        status_text = "Bad Request"
        msg = "Client error"
    else:
        status_text = "Error"
        msg = exc.detail
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": status_text,
            "message": msg,
            "status_code": exc.status_code,
        }
    )

@app.get("/", tags=["Home"])
async def get_root(request: Request) -> dict:
    return {
        "message": "Welcome to API",
        "URL": "",
    }


if __name__ == "__main__":
    uvicorn.run("main:app", port=7001, reload=True)
