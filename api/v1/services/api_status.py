from typing import Any, List, Optional
from api.core.base.services import Service
from sqlalchemy.orm import Session
from api.v1.models.api_status import APIStatus
from api.v1.schemas.api_status import APIStatusPost
from fastapi import HTTPException


class APIStatusService(Service):

    @staticmethod
    def fetch(db: Session, status_id) -> APIStatus:
        status = db.query(APIStatus).get(status_id).first()

        return status
    
    @staticmethod
    def fetch_by_api_group(db: Session, api_group) -> APIStatus:
        status = db.query(APIStatus).filter(APIStatus.api_group == api_group).first()

        return status
    
    @staticmethod
    def fetch_all(db: Session, **query_params: Optional[Any]) -> List[APIStatus]:
        query = db.query(APIStatus)

        #  Enable filter by query parameter
        if query_params:
            for column, value in query_params.items():
                if hasattr(APIStatus, column) and value:
                    query = query.filter(getattr(APIStatus, column).ilike(f"%{value}%"))

        return query.all()

    @staticmethod
    def upsert(db: Session, schema: APIStatusPost) -> APIStatus:
        """
        Upsert an API status record into the database.

        This method attempts to insert a new API status record based on the provided schema.
        If a record with the same api_group already exists, it will be updated with the new values.

        Parameters:
            db (Session): The SQLAlchemy database session to perform the operation.
            schema (APIStatusPost): The data model containing the API status information.

        Returns:
            APIStatus: The created or updated API status record.

        Raises:
            SQLAlchemyError: If there is an issue with the database operation.
        """

        try:
            existing_status = db.query(APIStatus).filter(APIStatus.api_group == schema.api_group).first()

            if existing_status:
                existing_status.api_group = schema.api_group
                existing_status.status = schema.status
                existing_status.response_time = schema.response_time
                existing_status.details = schema.details

                db.commit()
                db.refresh(existing_status)
                return existing_status
            
            status = APIStatus(
                api_group=schema.api_group,
                status=schema.status,
                response_time=schema.response_time,
                details=schema.details,
            )
            db.add(status)
            db.commit()
            db.refresh(status)
            return status
    
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="A database error occurred."
            )

    # @staticmethod
    # def update(db: Session, schema: APIStatusPost) -> APIStatus:
    #     status = APIStatus(
    #         api_group=schema.api_group,
    #         status=schema.status,
    #         response_time=schema.response_time,
    #         details=schema.details,
    #     )
    #     db.add(status)
    #     db.commit()
    #     db.refresh(status)
    #     return status
    
    @staticmethod
    def delete_by_api_group(db: Session, api_group) -> APIStatus:
        status = db.query(APIStatus).filter(APIStatus.api_group == api_group).first()
        db.delete(status)
        db.commit()
        return status
    
    @staticmethod
    def delete_all(db: Session) -> List[APIStatus]:
        statuses = db.query(APIStatus).all()
        for status in statuses:
            db.delete(status)
        db.commit()
        return status
    
    @staticmethod
    def create():
        pass

    @staticmethod
    def update():
        pass