"""Server file"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import api_version_one
from datetime import date


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_version_one)


@app.get("/healthcheck")
async def healthcheck():
    """check if server is active"""
    return {"status": "active"}
