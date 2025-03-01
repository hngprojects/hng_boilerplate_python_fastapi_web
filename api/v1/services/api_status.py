from typing import Any, List, Optional
from api.core.base.services import Service
from sqlalchemy.orm import Session
from api.v1.models.api_status import APIStatus
from api.v1.schemas.api_status import APIStatusPost, APIStatusUpdate
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
    @staticmethod
    def update(db: Session, api_group: str, schema: APIStatusUpdate) -> APIStatus:
        """
        Update an existing API status record by api_group.

        Parameters:
            db (Session): The SQLAlchemy database session.
            api_group (str): The api_group identifier to update.
            schema (APIStatusUpdate): The data model with updated API status info.

        Returns:
            APIStatus: The updated API status record.

        Raises:
            HTTPException: 404 if the api_group doesn't exist, 500 for db errors.
        """
        try:
            existing_status = db.query(APIStatus).filter(APIStatus.api_group == api_group).first()
            if not existing_status:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="API Status not found"
                )
            if schema.status is not None:
                existing_status.status = schema.status
            if schema.response_time is not None:
                existing_status.response_time = Decimal(schema.response_time)
            if schema.details is not None:
                existing_status.details = schema.details
            if schema.last_checked is not None:
                existing_status.last_checked = schema.last_checked

            db.commit()
            db.refresh(existing_status)
            return existing_status

        except HTTException as e:
            raise e
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="A database error occured."
            )

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