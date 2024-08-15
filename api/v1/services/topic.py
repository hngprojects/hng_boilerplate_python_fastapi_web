from typing import Any, Optional, List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from api.core.base.services import Service
from api.utils.db_validators import check_model_existence
from api.v1.models.topic import Topic
from api.v1.schemas.topic import TopicUpdateSchema

    

class TopicService(Service):
    '''Topic service functionality'''

    def create(self, db: Session, title: str, content: str, tags: Optional[list] = None):
        '''Function to like a topic'''
        
        topic_data = db.query(Topic).filter_by(title=title).first()
        if topic_data:
            raise HTTPException(status_code=status.HTTP_200_OK, detail="You've already created this topic")
        new_topic = Topic(title=title, content=content, tags=tags)
        db.add(new_topic)
        db.commit()
        db.refresh(new_topic)
        return new_topic

    def fetch_all(self, db: Session, **query_params: Optional[Any]):
        '''Fetch all topics with optional search using query parameters'''

        query = db.query(Topic)

        if query_params:
            for column, value in query_params.items():
                if hasattr(Topic, column) and value:
                    query = query.filter(getattr(Topic, column).ilike(f'%{value}%'))

        return query.all()

    def fetch(self, db: Session, id: str):
        '''Fetch a topic by id'''

        topic = check_model_existence(db, Topic, id)
        return topic

    def update(self, db: Session, schema: TopicUpdateSchema, topic_id: str):
        '''Updates a topic'''

        topic = self.fetch(db=db, id=topic_id)
        
        update_data = schema.dict(exclude_unset=True, exclude={"id"})
        for key, value in update_data.items():
            setattr(topic, key, value)

        db.commit()
        db.refresh(topic)
        return topic

    def delete(self, db: Session, id: str):
        """Deletes a topic"""

        topic = self.fetch(db=db, id=id)
        db.delete(topic)
        db.commit()
    
    def search(self, db: Session, title_query: str, content_query: str):
        """
        Search for topics based on title, content, tags, or topic IDs.
        """
        query = db.query(Topic).filter(
            (Topic.title.ilike(f'%{title_query}%')) |
            (Topic.content.ilike(f'%{content_query}%'))
        )
        return query.all()


topic_service = TopicService()