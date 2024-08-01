from typing import Any, Optional
from sqlalchemy.orm import Session
from api.core.base.services import Service
from api.v1.models.regions import Region
from api.v1.schemas.regions import RegionUpdate, RegionCreate
from api.utils.db_validators import check_model_existence


class RegionService(Service):
    """Region Services"""

    def create(self, db: Session, schema: RegionCreate, user_id: str):
        '''Create a new Region'''

        new_region = Region(**schema.model_dump(), user_id=user_id)
        db.add(new_region)
        db.commit()
        db.refresh(new_region)

        return new_region
    

    def fetch_all(self, db: Session, **query_params: Optional[Any]):
        '''Fetch all Region with option to search using query parameters'''

        query = db.query(Region)

        # Enable filter by query parameter
        if query_params:
            for column, value in query_params.items():
                if hasattr(Region, column) and value:
                    query = query.filter(getattr(Region, column).ilike(f'%{value}%'))

        return query.all()

    
    def fetch(self, db: Session, region_id: str):
        '''Fetches a Region by id'''

        region = check_model_existence(db, Region, region_id)
        return region
    

    def update(self, db: Session, region_id: str, schema: RegionUpdate):
        '''Updates a Region'''

        region = self.fetch(db=db, region_id=region_id)
        
        # Update the fields with the provided schema data
        update_data = schema.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(region, key, value)
        
        db.commit()
        db.refresh(region)
        return region
    

    def delete(self, db: Session, region_id: str):
        '''Deletes a region service'''
        
        region = self.fetch(db=db, region_id=region_id)
        db.delete(region)
        db.commit()


region_service = RegionService()
