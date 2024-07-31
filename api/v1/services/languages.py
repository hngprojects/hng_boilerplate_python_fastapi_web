from typing import Any, Optional
from sqlalchemy.orm import Session
from api.core.base.services import Service
from api.v1.models.regions import Language
from api.v1.schemas.regions import LanguageCreate, LanguageUpdate
from api.utils.db_validators import check_model_existence


class LanguageService(Service):
    '''Payment service functionality'''

    def create(self, db: Session, schema: LanguageCreate):
        '''Create a new FAQ'''

        new_lang = Language(**schema.model_dump())
        db.add(new_lang)
        db.commit()
        db.refresh(new_lang)

        return new_lang
    

    def fetch_all(self, db: Session, **query_params: Optional[Any]):
        '''Fetch all FAQs with option to search using query parameters'''

        query = db.query(Language)

        # Enable filter by query parameter
        if query_params:
            for column, value in query_params.items():
                if hasattr(Language, column) and value:
                    query = query.filter(getattr(Language, column).ilike(f'%{value}%'))

        return query.all()

    
    def fetch(self, db: Session, lang_id: str):
        '''Fetches a, FAQ by id'''

        region = check_model_existence(db, Language, lang_id)
        return region
    

    def update(self, db: Session, lang_id: str, schema: LanguageUpdate):
        '''Updates an FAQ'''

        lang = self.fetch(db=db, lang_id=lang_id)
        
        # Update the fields with the provided schema data
        update_data = schema.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(lang, key, value)
        
        db.commit()
        db.refresh(lang)
        return lang
    

    def delete(self, db: Session, lang_id: str):
        '''Deletes an FAQ'''
        
        lang = self.fetch(db=db, lang_id=lang_id)
        db.delete(lang)
        db.commit()


lang_service = LanguageService()