import uvicorn
import redis.asyncio as redis
from contextlib import asynccontextmanager
from typing import Union
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from starlette.requests import Request

from api.db.database import create_database
# from api.db.mongo import create_nosql_db
# from api.v1.routes.auth import app as auth
from api.utils.settings import REDIS_URL
from api.v1.routes.help_center import app as help_center
from api.utils.exceptions import rate_limit_callback, http_exception_handler

from fastapi_limiter import FastAPILimiter


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_database()
    # create_nosql_db()
    redis_connection = redis.from_url(REDIS_URL, encoding="utf8")
    await FastAPILimiter.init(
        redis=redis_connection,
        http_callback=rate_limit_callback,
    )
    yield
    ## write shutdown logic below yield
    await FastAPILimiter.close()


app = FastAPI(lifespan=lifespan)
app.exception_handlers.setdefault(HTTPException, http_exception_handler)


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
