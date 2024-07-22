import uvicorn
from contextlib import asynccontextmanager
from typing import Union
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.requests import Request
from api.db.database import Base, engine
from api.db.database import create_database
from api.v1.routes.testimonial import route as testimonial

from api.v1.routes.newsletter_router import newsletter
from api.v1.routes.newsletter_router import (
    CustomException,
    custom_exception_handler
)

from api.v1.routes.auth import auth
from api.v1.routes.roles import role
from api.v1.routes import api_version_one
from api.v1.routes.user import user
from api.v1.routes.roles import role

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

app.include_router(auth)
#app.include_router(auth, tags=["Auth"])
#app.include_router(users, tags=["Users"])

app.include_router(testimonial, tags=["testimonial"])
app.include_router(api_version_one)

app.include_router(user)
# app.include_router(users, tags=["Users"])


@app.get("/", tags=["Home"])
async def get_root(request: Request) -> dict:
    return {
        "message": "Welcome to API",
        "URL": "",
    }


if __name__ == "__main__":
    uvicorn.run("main:app", port=7001, reload=True)
