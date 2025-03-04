from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from typing import Optional, Any, Dict, Type, List

class BaseService:
    """Base service class to handle common CRUD operations."""
    def __init__(self,model: Type[Any]) -> None:
        self.model = model

    def fetch_all(self, db: Session, **query_params: Optional[Any]) -> List[Any]:
        """Fetch all records with optional filtering."""
        query = db.query(self.model)
        if query_params:
            for column, value in query_params.items():
                if hasattr(self.model, column) and value:
                    query = query.filter(getattr(self.model, column).ilike(f"%{value}%"))
        return query.all()

    def fetch_by_id(self, db: Session, item_id: str) -> Any:
        """Fetch a record by its ID."""
        item = db.query(self.model).filter(self.model.id == item_id).first()
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{self.model.__name__} with ID {item_id} not found"
            )
        return item

    def fetch_by_column(self, db: Session, column: str, value: Any) -> List[Any]:
        """Fetch records by a specific column value."""
        if hasattr(self.model, column):
            return db.query(self.model).filter(getattr(self.model, column) == value).all()
        return []

    def update(self, db: Session, item_id: str, update_data: Dict[str, Any]) -> Any:
        """Update a record with the provided data."""
        item = self.fetch_by_id(db, item_id)
        try:
            for key, value in update_data.items():
                if hasattr(item, key):
                    setattr(item, key, value)
            db.commit()
            db.refresh(item)
            return item
        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update {self.model.__name__}: {str(e)}"
            )

    def delete(self, db: Session, item_id: str) -> Dict[str, str]:
        """Delete a record by its ID."""
        item = self.fetch_by_id(db, item_id)
        try:
            db.delete(item)
            db.commit()
            return {"status": "success", "detail": f"{self.model.__name__} with ID {item_id} deleted successfully"}
        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete {self.model.__name__}: {str(e)}"
            )

