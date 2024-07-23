import uvicorn
from contextlib import asynccontextmanager
from typing import Union
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.requests import Request
from api.db.database import Base, engine

from api.v1.routes.newsletter_router import newsletter
from api.v1.routes.newsletter_router import (
    CustomException,
    custom_exception_handler
)

from api.v1.routes.auth import auth
from api.v1.routes.user import user
from api.v1.routes.roles import role
from routers import jobs

app = FastAPI()

# Include routers
app.include_router(jobs.router)
app.include_router(newsletter, tags=["Newsletter"])
app.include_router(auth)
app.include_router(user)

# Set up CORS middleware
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

# Exception handlers
app.add_exception_handler(CustomException, custom_exception_handler)

# Create database tables
Base.metadata.create_all(bind=engine)

@app.get("/", tags=["Home"])
async def get_root(request: Request) -> dict:
    return {
        "message": "Welcome to API",
        "URL": "",
    }

if __name__ == "__main__":
    uvicorn.run("main:app", port=7001, reload=True)
