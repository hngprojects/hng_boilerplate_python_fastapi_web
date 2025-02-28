from abc import ABC, abstractmethod
from sqlalchemy.orm import Session
from fastapi import HTTPException


class Service(ABC):
    @abstractmethod
    def create(self):
        pass

    @abstractmethod
    def fetch(self, db: Session, id: str):
        """Fetch a single record by ID and raise 404 if not found."""
        if not self.model:
            raise ValueError("Model is not defined for this service")

        instance = db.query(self.model).filter(self.model.id == id).first()
        if not instance:
            raise HTTPException(status_code=404, detail=f"{self.model.__name__} not found")
        return instance

    def fetch_all(self, db: Session):
        """Fetch all records."""
        if not self.model:
            raise ValueError("Model is not defined for this service")

        return db.query(self.model).all()
    
    @abstractmethod
    def fetch_all(self):
        pass

    @abstractmethod
    def update(self):
        pass

    @abstractmethod
    def delete(self):
        pass
