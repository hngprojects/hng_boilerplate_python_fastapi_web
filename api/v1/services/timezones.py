from typing import Any, Optional
from sqlalchemy.orm import Session
from api.core.base.services import Service
from api.v1.models.regions import Timezone
from api.v1.schemas.regions import TimezoneCreate, TimezoneUpdate
from api.utils.db_validators import check_model_existence


class TimezoneService(Service):
    '''Payment service functionality'''

    def create(self, db: Session, schema: TimezoneCreate):
        '''Create a new FAQ'''

        new_timezone = Timezone(**schema.model_dump())
        db.add(new_timezone)
        db.commit()
        db.refresh(new_timezone)

        return new_timezone
    

    def fetch_all(self, db: Session, **query_params: Optional[Any]):
        '''Fetch all FAQs with option to search using query parameters'''

        query = db.query(Timezone)

        # Enable filter by query parameter
        if query_params:
            for column, value in query_params.items():
                if hasattr(Timezone, column) and value:
                    query = query.filter(getattr(Timezone, column).ilike(f'%{value}%'))

        return query.all()

    
    def fetch(self, db: Session, timezone_id: str):
        '''Fetches a, FAQ by id'''

        timezone = check_model_existence(db, Timezone, timezone_id)
        return timezone
    

    def update(self, db: Session, timezone_id: str, schema: TimezoneCreate):
        '''Updates an FAQ'''

        timezone = self.fetch(db=db, timezone_id=timezone_id)
        
        # Update the fields with the provided schema data
        update_data = schema.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(timezone, key, value)
        
        db.commit()
        db.refresh(timezone)
        return timezone
    

    def delete(self, db: Session, timezone_id: str):
        '''Deletes an FAQ'''
        
        timezone = self.fetch(db=db, timezone_id=timezone_id)
        db.delete(timezone)
        db.commit()


timezone_service = TimezoneService()