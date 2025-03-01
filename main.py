import os
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from slowapi import Limiter
from slowapi.util import get_remote_address
from starlette.middleware.sessions import SessionMiddleware

from api.utils.json_response import JsonResponseDict
from api.utils.logger import logger
from api.utils.settings import settings
from api.v1.routes import api_version_one
from scripts.populate_db import populate_roles_and_permissions
from sqlalchemy.exc import IntegrityError
from fastapi.templating import Jinja2Templates

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handles FastAPI application lifespan events."""
    yield

app = FastAPI(
    lifespan=lifespan,
    title="HNG Boilerplate",
    description="A boilerplate for creating an API using FastAPI and SQLAlchemy",
    version="1.0.0",
)

# Rate limiter
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

# Email template setup
email_templates = Jinja2Templates(directory='api/core/dependencies/email/templates')

# Directory setup
MEDIA_DIR = "./media"
STATIC_DIR = "static/profile_images"
os.makedirs(MEDIA_DIR, exist_ok=True)
os.makedirs(STATIC_DIR, exist_ok=True)

# Mount static directories
app.mount('/media', StaticFiles(directory=MEDIA_DIR), name='media')
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# CORS setup
origins = [
    "http://localhost:3000",
    "http://localhost:3001",
    "https://anchor-python.teams.hng.tech",
]
app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(api_version_one)

@app.get("/", tags=["Home"])
async def get_root(request: Request) -> dict:
    return JsonResponseDict(
        message="Welcome to API", status_code=status.HTTP_200_OK, data={"URL": ""}
    )

@app.get("/probe", tags=["Home"])
async def probe():
    return {"message": "I am the Python FastAPI API responding"}

# Exception Handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handles HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"status": False, "status_code": exc.status_code, "message": exc.detail},
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handles validation exceptions"""
    errors = [{"loc": err["loc"], "msg": err["msg"], "type": err["type"]} for err in exc.errors()]
    return JSONResponse(
        status_code=422,
        content={"status": False, "status_code": 422, "message": "Invalid input", "errors": errors},
    )

@app.exception_handler(IntegrityError)
async def integrity_error_handler(request: Request, exc: IntegrityError):
    """Handles database integrity errors"""
    logger.exception(f"IntegrityError: {exc}")
    return JSONResponse(
        status_code=400,
        content={"status": False, "status_code": 400, "message": "Database integrity error"},
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handles unexpected exceptions"""
    logger.exception(f"Unhandled Exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"status": False, "status_code": 500, "message": "Internal Server Error"},
    )

# Run the application
if __name__ == "__main__":
    uvicorn.run("main:app", port=7001, reload=True)

