import uvicorn
from contextlib import asynccontextmanager
from typing import Union
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.requests import Request
from api.db.database import Base, engine
from api.v1.models.org import Organization
from api.v1.models.preference import OrgPreference

from api.v1.routes.job import job


from api.v1.routes.newsletter_router import newsletter
from api.v1.routes.newsletter_router import (
    CustomException,
    custom_exception_handler
)

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

app.include_router(job)
# app.include_router(users, tags=["Users"])

app.include_router(newsletter, tags=["Newsletter"])


@app.get("/", tags=["Home"])
async def get_root(request: Request) -> dict:
    return {
        "message": "Welcome to API",
        "URL": "",
    }


from api.v1.routes import preferences, users,org,login

app.include_router(login.router)
app.include_router(users.router, tags=["users"])
app.include_router(org.router)
app.include_router(preferences.router, tags=["preferences"])

# if __name__ == "__main__":
#     uvicorn.run("main:app", port=7001, reload=True)
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
