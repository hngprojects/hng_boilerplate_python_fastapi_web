from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from api.v1.models.feature_request import FeatureRequest
from api.v1.schemas.feature_request import FeatureRequestCreate, FeatureRequestUpdate, FeatureRequestBase, FeatureRequestInDB, FeatureRequestResponse 


class FeatureRequestService:
    @staticmethod
    def create_feature_request(db: Session, feature_request_data: FeatureRequestCreate, user_id: str):
        # Convert to dict and explicitly set status to "Pending"
        feature_request_dict = feature_request_data.dict()
        feature_request_dict["status"] = "Pending"
    
        db_feature_request = FeatureRequest(**feature_request_data.dict(), user_id=user_id)
        db.add(db_feature_request)
        db.commit()
        db.refresh(db_feature_request)
        return db_feature_request

    @staticmethod
    def get_feature_requests(db: Session, skip: int = 0, limit: int = 100):
        return db.query(FeatureRequest).offset(skip).limit(limit).all()

    @staticmethod
    def get_user_feature_requests(db: Session, user_id: str, skip: int = 0, limit: int = 100):
        return db.query(FeatureRequest).filter(FeatureRequest.user_id == user_id).offset(skip).limit(limit).all()

    @staticmethod
    def get_feature_request_by_id(db: Session, feature_request_id: str):
        return db.query(FeatureRequest).filter(FeatureRequest.id == feature_request_id).first()

    @staticmethod
    def update_feature_request(db: Session, feature_request_id: str, feature_request_update: FeatureRequestUpdate):
        db_feature_request = db.query(FeatureRequest).filter(FeatureRequest.id == feature_request_id).first()
        if db_feature_request:
            for key, value in feature_request_update.dict(exclude_unset=True).items():
                setattr(db_feature_request, key, value)
            db.commit()
            db.refresh(db_feature_request)
        return db_feature_request

    @staticmethod
    def delete_feature_request(db: Session, feature_request_id: str):
        db_feature_request = db.query(FeatureRequest).filter(FeatureRequest.id == feature_request_id).first()
        if db_feature_request:
            db.delete(db_feature_request)
            db.commit()
        return db_feature_request


    class Config:
        orm_mode = True
