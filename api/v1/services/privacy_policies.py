from typing import Any, Optional
from sqlalchemy.orm import Session
from api.core.base.services import Service
from api.v1.models.privacy import PrivacyPolicy
from api.v1.schemas.privacy_policies import PrivacyPolicyCreate, PrivacyPolicyUpdate
from api.utils.db_validators import check_model_existence


class PrivacyService(Service):
    """Privacy Services"""

    def create(self, db: Session, schema: PrivacyPolicyCreate):
        '''Create a new Privacy'''

        new_privacy = PrivacyPolicy(**schema.model_dump())
        db.add(new_privacy)
        db.commit()
        db.refresh(new_privacy)

        return new_privacy
    

    def fetch_all(self, db: Session, **query_params: Optional[Any]):
        '''Fetch all Privacy with option to search using query parameters'''

        query = db.query(PrivacyPolicy)

        # Enable filter by query parameter
        if query_params:
            for column, value in query_params.items():
                if hasattr(PrivacyPolicy, column) and value:
                    query = query.filter(getattr(PrivacyPolicy, column).ilike(f'%{value}%'))

        return query.all()

    
    def fetch(self, db: Session, privacy_id: str):
        '''Fetches a privacy by id'''

        privacy = check_model_existence(db, PrivacyPolicy, privacy_id)
        return privacy
    

    def update(self, db: Session, privacy_id: str, schema: PrivacyPolicyUpdate):
        '''Updates a Privacy'''

        privacy = self.fetch(db=db, privacy_id=privacy_id)
        
        # Update the fields with the provided schema data
        update_data = schema.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(privacy, key, value)
        
        db.commit()
        db.refresh(privacy)
        return privacy
    

    def delete(self, db: Session, privacy_id: str):
        '''Deletes a privacy service'''
        
        privacy = self.fetch(db=db, privacy_id=privacy_id)
        db.delete(privacy)
        db.commit()


privacy_service = PrivacyService()
