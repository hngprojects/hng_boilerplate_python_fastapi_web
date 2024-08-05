from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from api.db.database import get_db
from api.v1.services.language import get_unique_languages

language = APIRouter(prefix="/languages", tags=["Regions, Timezone and Language"])

@language.get("/", response_model=dict)
async def get_languages(db: Session = Depends(get_db)):
    try:
        languages = get_unique_languages(db)
        return {"languages": languages}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
