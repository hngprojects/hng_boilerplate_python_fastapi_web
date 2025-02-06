from typing import Any, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from api.core.base.services import Service
from api.v1.models.waitlist import Waitlist
from pydantic import BaseModel


class WaitListService(Service):
    """waitlist user service functionality"""

    def create(self, db: Session, schema: BaseModel):
        """Create a new waitlist user"""

        new_waitlist_user = Waitlist(**schema.model_dump())
        db.add(new_waitlist_user)
        db.commit()
        db.refresh(new_waitlist_user)

        return new_waitlist_user

    def fetch_all(self, db: Session, **query_params: Optional[Any]):
        """Fetch all waitlist users with option to search using query parameters"""

        query = db.query(Waitlist)

        # Enable filter by query parameter
        if query_params:
            for column, value in query_params.items():
                if hasattr(Waitlist, column) and value:
                    query = query.filter(getattr(Waitlist, column).ilike(f"%{value}%"))

        return query.all()

    def fetch(self, db: Session, id: str):
        """Fetches a waitlist user by their id"""

        waitlist_user = db.query(Waitlist).filter(Waitlist.id == id).first()
        return waitlist_user

    def fetch_by_email(self, db: Session, email: str):
        """Fetches a waitlist user by their email"""

        waitlist_user = db.query(Waitlist).filter(Waitlist.email == email).first()

        return waitlist_user

    def update(self, db: Session, id: str, schema):
        """Updates a waitlist user"""
        pass

    def delete(self, db: Session, id: str):
        """Deletes a waitlist user"""

        waitlist_user = self.fetch(db=db, id=id)
        if not waitlist_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No waitlisted user found with given id",
            )

        db.delete(waitlist_user)
        db.commit()


waitlist_service = WaitListService()
