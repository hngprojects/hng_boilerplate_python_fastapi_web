from fastapi import(
    HTTPException,
    APIRouter,
    Request,
    Depends,
    status
)
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from api.v1.models.testimonials import Testimonial
from api.v1.schemas.testimonial import (
    UpdateTestimonial, 
    TestimonialCreate, 
    TestimonialResponse, 
    SuccessResponse,
 UpdateTestimonialResponse, 
BaseTestimonialResponse

)
from api.db.database import get_db, Base, engine
from typing import Annotated
from api.utils.dependencies import get_current_user




db_dependency = Annotated[Session , Depends(get_db)]

testimonial_router = APIRouter(prefix="/api/v1/testimonials", tags=["testimonials"])

class CustomException(HTTPException):
    """
    Custom error handling
    """
    def __init__(self, status_code: int, detail: dict):
        super().__init__(status_code=status_code, detail=detail)
        self.message = detail.get("message")
        self.success = detail.get("success")
        self.status_code = detail.get("status_code")

async def custom_exception_handler(request: Request, exc: CustomException):
    return JSONResponse(
        status_code=exc.status_code,
        message={
            "message": exc.message,
            "success": exc.success,
            "status_code": exc.status_code
        }
    )




@testimonial_router.put('/{testimonial_id}', response_model=UpdateTestimonialResponse)
def update_testimonial(testimonial_id : str, request : UpdateTestimonial , db : db_dependency, current_user: dict = Depends(get_current_user) ):
    try:
       testimonial = db.query(Testimonial).filter(Testimonial.id == testimonial_id).first()
    except :
        testimonial = None
    
    if testimonial is None:

        raise CustomException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=   {
                    "status": "Bad Request",
                    "message": "Client error",
                     "status_code": 400
                     }
                    )
    
    if current_user.id != testimonial.user_id :
        raise CustomException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                    "status":  "Forbidden",
                     "message":  "Only owners of testimonial can update",
                      "status_code": 403
             }
        )

    testimonial.content = request.content
    db.commit()
    response_text = BaseTestimonialResponse(
        user_id=testimonial.user_id,
        content=testimonial.content,
        updated_at= testimonial.updated_at

    )
    return UpdateTestimonialResponse(
        status=status.HTTP_200_OK,
        message='Testimonial Updated Successfully',
        data= response_text
    )
    
    
 


