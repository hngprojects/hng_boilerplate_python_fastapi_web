from fastapi import Depends, HTTPException, APIRouter, Request, Response, status
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse

from api.utils.success_response import success_response
from api.v1.models.testimonial import Testimonial
from api.v1.models.user import User
# from api.v1.schemas.user import DeactivateUserSchema, UserBase
from api.db.database import get_db
from api.v1.services.testimonial import testimonial_service
from api.v1.services.user import user_service


testimonial = APIRouter(prefix='/testimonials', tags=['Testimonial'])

@testimonial.get('/{testimonial_id}', status_code=status.HTTP_200_OK)
def get_testimonial(testimonial_id, db: Session = Depends(get_db), current_user: User = Depends(user_service.get_current_user)):
    '''Endpoint to get testimonial by id'''

    testimonial = testimonial_service.fetch(db, testimonial_id)
    if testimonial and testimonial_id == testimonial.id:
        return success_response(
            status_code=200,
            message=f'Testimonial {testimonial_id} retrieved successfully',
            data={
                'id': testimonial.id,
                'client_designation': testimonial.client_designation,
                'client_name': testimonial.client_name,
                'author_id': testimonial.author_id,
                'comments': testimonial.comments,
                'content': testimonial.content,
                'ratings': testimonial.ratings, 
            }
        )
    return JSONResponse(
        status_code=404,
        content={
            "success": False,
            "status_code": 404,
            "message": f'Testimonial {testimonial_id} not found'
        }
    )
