from utils.dependencies import get_current_admin
from api.db.database import get_db
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status, APIRouter
from fastapi.responses import JSONResponse
from api.v1.models.about_page import AboutPage
from api.v1.schemas.about_page_schema import AboutPageContent


about_page_router = APIRouter(prefix="/api/v1", tags=["about_page_content"])


@about_page_router.get("/content/about", response_model=AboutPageContent)
def get_about_page_content(about_page_content: AboutPageContent, current_user: dict = Depends(get_current_admin), db: Session = Depends(get_db)):
    try:
        about_page = db.query(AboutPage).first()
        if not about_page:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="About page content not found"
            )

        # Convert database object to Pydantic model
        response_data = {
            "title": about_page.title,
            "introduction": about_page.introduction,
            "custom_sections": about_page.custom_sections,
            "last_update": about_page.last_update.isoformat(),
            "status_code": 200,
            "message": "Retrieved About Page content successfully"
        }

        return JSONResponse(content=response_data, status_code=status.HTTP_200_OK)
        
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Failed to retrieve About page content.")