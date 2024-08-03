import uvicorn
import os
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, Request
from fastapi.templating import Jinja2Templates
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse, JSONResponse
from contextlib import asynccontextmanager
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from starlette.requests import Request
from api.utils.email_service import send_mail
from api.utils.json_response import JsonResponseDict
from starlette.middleware.sessions import SessionMiddleware  # required by google oauth

from api.utils.logger import logger
from api.core.dependencies.email_sender import send_email
from api.v1.routes import api_version_one
from api.utils.settings import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(lifespan=lifespan)


# Set up email templates and css static files
email_templates = Jinja2Templates(directory='api/core/dependencies/email/templates')

origins = [
    "http://localhost:3000",
    "http://localhost:3001",
]


app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_version_one)

@app.get("/", tags=["Home"])
async def get_root(request: Request) -> dict:
    return JsonResponseDict(
        message="Welcome to API", status_code=status.HTTP_200_OK, data={"URL": ""}
    )


@app.get("/probe", tags=["Home"])
async def probe():
    return {"message": "I am the Python FastAPI API responding"}


# REGISTER EXCEPTION HANDLERS
@app.exception_handler(HTTPException)
async def http_exception(request: Request, exc: HTTPException):
    """HTTP exception handler"""

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "status_code": exc.status_code,
            "message": exc.detail,
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception(request: Request, exc: RequestValidationError):
    """Validation exception handler"""

    errors = [
        {"loc": error["loc"], "msg": error["msg"], "type": error["type"]}
        for error in exc.errors()
    ]

    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "status_code": 422,
            "message": "Invalid input",
            "errors": errors,
        },
    )


@app.exception_handler(IntegrityError)
async def exception(request: Request, exc: IntegrityError):
    """Integrity error exception handlers"""

    logger.exception(f"Exception occured; {exc}")

    return JSONResponse(
        status_code=400,
        content={
            "success": False,
            "status_code": 400,
            "message": f"An unexpected error occurred: {exc}",
        },
    )


@app.exception_handler(Exception)
async def exception(request: Request, exc: Exception):
    """Other exception handlers"""

    logger.exception(f"Exception occured; {exc}")

    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "status_code": 500,
            "message": f"An unexpected error occurred: {exc}",
        },
    )


if __name__ == "__main__":
    uvicorn.run("main:app", port=7001, reload=True)
