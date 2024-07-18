import uvicorn
from contextlib import asynccontextmanager
from typing import Union
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.requests import Request
from api.db.database import create_database
# from api.db.mongo import create_nosql_db
# from api.v1.routes.auth import app as auth
from api.v1.routes.help_center import app as help_center


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_database()
    # create_nosql_db()
    yield
    ## write shutdown logic below yield


app = FastAPI(lifespan=lifespan)


# create_nosql_db()
    

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


# app.include_router(auth, tags=["Auth"])
# app.include_router(users, tags=["Users"])
app.include_router(help_center, tags=["Help Centers"])



@app.get("/", tags=["Home"])
async def get_root(request: Request) -> dict:
    return {
        "message": "Welcome to API",
        "URL": "",
    }


if __name__ == "__main__":
    uvicorn.run("main:app", port=7001, reload=True)
