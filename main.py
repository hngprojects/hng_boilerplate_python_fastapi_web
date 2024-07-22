import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from starlette.requests import Request
from api.v1.routes.newsletter_router import (
    CustomException,
    custom_exception_handler
)
from api.v1.routes import api_version_one
from api.utils.json_response import JsonResponseDict


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
# app.include_router(users, tags=["Users"])


@app.get("/", tags=["Home"])
async def get_root(request: Request) -> dict:
    return JsonResponseDict(
        message="Welcome to API",
        status_code=status.HTTP_200_OK,
        data={"URL": ""}
	)


if __name__ == "__main__":
    uvicorn.run("main:app", port=7001, reload=True)
