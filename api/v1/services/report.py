from typing import Any, Optional, List
from sqlalchemy.orm import Session
from api.core.base.services import Service
from api.v1.models.report import Report
from api.v1.schemas.report import ReportCreateSchema, ReportResponseSchema
from api.utils.db_validators import check_model_existence
from sqlalchemy import distinct
from fastapi import HTTPException


class ReportService(Service):
    """Report Services"""

    def create(self, db: Session, schema: ReportCreateSchema, user_id: str):
        '''Create a new Region'''
        new_report = Report(**schema.model_dump(), reported_by=user_id)
        db.add(new_report)
        db.commit()
        db.refresh(new_report)

        return new_report
    

    def fetch_all(self, db: Session, **query_params: Optional[Any]):
        '''Fetch all Region with option to search using query parameters'''

        query = db.query(Report)

        # Enable filter by query parameter
        if query_params:
            for column, value in query_params.items():
                if hasattr(Report, column) and value:
                    query = query.filter(getattr(Report, column).ilike(f'%{value}%'))

        return query.all()

    
    def fetch(self, db: Session, report_id: str):
        '''Fetches a Region by id'''

        report = check_model_existence(db, Report, report_id)
        return report
    

    def update(self, db: Session, report_id: str):
        '''Updates a Region'''

        region = self.fetch(db=db, report_id=report_id)
        
        # Update the fields with the provided schema data
        
        db.commit()
        db.refresh(region)
        return region
    

    def delete(self, db: Session, report_id: str):
        '''Deletes a region service'''
        
        report = self.fetch(db=db, report_id=report_id)
        db.delete(report)
        db.commit()
    


report_service = ReportService()
