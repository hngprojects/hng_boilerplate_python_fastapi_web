from fastapi.responses import JSONResponse
import uvicorn
from fastapi import HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from starlette.requests import Request
from api.utils.json_response import JsonResponseDict

from api.utils.logger import logger
from api.v1.routes.newsletter import (
    CustomException,
    custom_exception_handler
)
from api.v1.routes import api_version_one


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


@app.get("/", tags=["Home"])
async def get_root(request: Request) -> dict:
    return JsonResponseDict(
        message="Welcome to API",
        status_code=status.HTTP_200_OK,
        data={"URL": ""}
	)


# REGISTER EXCEPTION HANDLERS

@app.exception_handler(HTTPException)
async def http_exception(request: Request, exc: HTTPException):
    '''HTTP exception handler'''

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "status_code": exc.status_code,
            "message": exc.detail
        }
    )

@app.exception_handler(RequestValidationError)
async def validation_exception(request: Request, exc: RequestValidationError):
    '''Validation exception handler'''

    errors = [{"loc": error["loc"], "msg": error["msg"], "type": error["type"]} for error in exc.errors()]

    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "status_code": 422,
            "message": "Invalid input",
            "errors": errors
        }
    )

@app.exception_handler(Exception)
async def exception(request: Request, exc: Exception):
    '''Other exception handlers'''
    
    logger.exception(f'Exception occured; {exc}')

    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "status_code": 500,
            "message": f"An unexpected error occurred: {exc}"
        }
    )


if __name__ == "__main__":
    uvicorn.run("main:app", port=7001, reload=True)