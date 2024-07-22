import uvicorn
from contextlib import asynccontextmanager
from typing import Union
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from starlette.requests import Request

from fastapi_limiter import FastAPILimiter

from api.db.database import Base, engine
from api.utils.middlewares import RateLimitMiddleware
from api.utils.exceptions import http_exception_handler
from api.v1.routes.help_center import router as help_center
from api.v1.routes.newsletter_router import newsletter
from api.v1.routes import api_version_one
from api.v1.routes.auth import auth
from api.v1.routes.user import user
from api.v1.routes.roles import role

Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(lifespan=lifespan)
app.exception_handlers.setdefault(HTTPException, http_exception_handler)
    

origins = [
    "http://localhost:3000",
    "http://localhost:3001",
]


# Add the rate limiting middleware with custom RATE_LIMIT and TIME_WINDOW
app.add_middleware(RateLimitMiddleware, rate_limit=1, time_window=1)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(newsletter, tags=["Newsletter"])
app.include_router(auth, tags=["Auth"])
app.include_router(help_center, tags=["Help Centers"])
app.include_router(api_version_one)
app.include_router(newsletter, tags=["Newsletter"])
app.include_router(user)

@app.get("/", tags=["Home"])
async def get_root(request: Request) -> dict:
    return {
        "message": "Welcome to API",
        "URL": "",
    }


if __name__ == "__main__":
    uvicorn.run("main:app", port=7001, reload=True)
