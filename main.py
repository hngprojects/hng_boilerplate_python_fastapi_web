import uvicorn
from contextlib import asynccontextmanager
from typing import Union
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.requests import Request
#from api.v1.models import user, profile, organization, org_preference
from api.db.database import Base, engine
# In main.py or wherever you initialize your app
from api.v1.models.org import Organization
from api.v1.models.preference import OrgPreference





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


# app.include_router(auth, tags=["Auth"])
# app.include_router(users, tags=["Users"])



@app.get("/", tags=["Home"])
async def get_root(request: Request) -> dict:
    return {
        "message": "Welcome to API",
        "URL": "",
    }


from api.v1.routes import preferences, users,auth,org
app.include_router(auth.router)
app.include_router(users.router, tags=["users"])
app.include_router(org.router)
app.include_router(preferences.router, tags=["preferences"])

# if __name__ == "__main__":
#     uvicorn.run("main:app", port=7001, reload=True)
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
