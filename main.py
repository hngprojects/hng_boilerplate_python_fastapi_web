import uvicorn
from contextlib import asynccontextmanager
from typing import Union
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from starlette.requests import Request
from api.db.database import Base, engine

from api.v1.routes.newsletter_router import newsletter
from api.v1.routes.newsletter_router import CustomException, custom_exception_handler
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, constr

from api.v1.routes.auth import auth
from api.v1.routes.user import user
from api.v1.routes.roles import role
from api.v1.routes.products import product

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


@app.exception_handler(RequestValidationError)
async def product_exception_handler(request: Request, exc: RequestValidationError):
    if request.url.path.startswith("/products/"):
        return JSONResponse(
            content={"message": "Bad Request", "statusCode": 400}, status_code=400
        )
    else:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=jsonable_encoder({"detail": exc.errors(), "body": exc.body}),
        )


app.add_exception_handler(RequestValidationError, product_exception_handler)

app.add_exception_handler(
    CustomException, custom_exception_handler
)  # Newsletter custom exception registration
app.include_router(newsletter, tags=["Newsletter"])

app.include_router(auth)
app.include_router(user)
app.include_router(product)
# app.include_router(users, tags=["Users"])


@app.get("/", tags=["Home"])
async def get_root(request: Request) -> dict:
    return {
        "message": "Welcome to API",
        "URL": "",
    }


if __name__ == "__main__":
    uvicorn.run("main:app", port=7001, reload=True)
