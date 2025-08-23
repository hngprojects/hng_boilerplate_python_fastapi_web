from api.v1.models.report import Report
from api.v1.schemas.report import ReportCreateSchema, ReportResponseSchema
from fastapi import Depends, APIRouter, HTTPException, status, Request
from sqlalchemy.orm import Session
from api.db.database import get_db
from api.utils.logger import logger
from api.utils.success_response import success_response
from api.v1.models.user import User
from api.v1.services.user import user_service
from api.v1.services.report import report_service
from fastapi.encoders import jsonable_encoder



report = APIRouter(prefix="/reports", tags=["Reports"])

@report.post("", response_model=success_response, status_code=status.HTTP_201_CREATED)
def create_report(report_request: ReportCreateSchema, reported_by: User = Depends(user_service.get_current_user),  db: Session = Depends(get_db)):

    reported_user = user_service.get_user_by_id(db, report_request.reported_user)


    if (reported_by.id == reported_user.id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User cannot report itself")
    
    reason = report_request.reason

    if (len(reason) == 0):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="reason user been reported cannot be empty")
    
    report = report_service.create(db, report_request, reported_by.id)

    return success_response(
        status_code=status.HTTP_201_CREATED,
        message="report successfully created",
        data=jsonable_encoder(report)
    )

@report.get("", response_model=success_response, status_code=status.HTTP_200_OK)
def get_all_report(admin_user: User = Depends(user_service.get_current_super_admin), db: Session = Depends(get_db)):

    reports = report_service.fetch_all(db)

    if not reports:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No report Found")
    
    return success_response(
        status_code=status.HTTP_200_OK,
        message="Report retrieced successfully",
        data=jsonable_encoder(reports)
        )