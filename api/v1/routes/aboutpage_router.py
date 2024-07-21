from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from api.v1.models.about_page import AboutPage
from api.v1.schemas.aboutpage_schema import AboutPageUpdate
from sqlalchemy.orm import Session
from api.db.database import get_db
from api.utils.dependencies import get_current_admin

router = APIRouter()

@router.put("/api/v1/content/about", response_model=AboutPageUpdate, dependencies=[Depends(get_current_admin)], tags="AboutPage")
def update_about_page(about_page_update: AboutPageUpdate, db: Session = Depends(get_db)):
    """
    Update the content of the About page.

    Args:
        about_page_update (AboutPageUpdate): The updated content for the About page.
        db (Session): The database session dependency.

    Returns:
        JSONResponse: A response containing a success message and status code 200.

    Raises:
        HTTPException: If the About page content is not found or if the update fails.
    """
    
    # Let's get the existing About page content from the database
    about_page = db.query(AboutPage).first()
    if not about_page:
        raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail="About page content not found"
		)
    
    try:
        # Okay, update the About page fields with the new values
        about_page.title = about_page_update.title
        about_page.introduction = about_page_update.introduction
        about_page.custom_sections = about_page_update.custom_sections
        
        db.commit()
        db.refresh(about_page)
        
        return JSONResponse(
			content={
				"message": "About page updated successfully",
				"status_code": 200
			}, status_code=status.HTTP_200_OK
		)
    except Exception as e:
        # An error ocurred, roll back transaction and raise an HTTP 500 error
        db.rollback()
        raise HTTPException(
			status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
			detail="Failed to update About page content"
		)
    
     