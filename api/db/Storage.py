from fastapi import HTTPException, status
from typing import Optional, List
from api.db.database import SessionLocal as SessionMaker, engine, Base
from enum import Enum as Pyenum
import sys
from sqlalchemy import  text, desc, asc, or_, and_,  cast, Date, text
from sqlalchemy.orm import joinedload


import logging as logger
from enum import Enum


logger.basicConfig(
    level=logger.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class APP_INIT(Enum):
	DATABASE = "DATABASE_INIT"

          

class SortEnum(Pyenum):
    asc="asc"
    desc="desc"

class DB:
    # ------------------ SYSTEM -----------------
    def __init__(self):
        self.session = None

    def connect(self):
        try:
            if not self.session:
                self.session = SessionMaker()
                self.session.execute(text('SELECT 1'))
                logger.info("[SUCCESS]", extra={
                    "operation": str(APP_INIT.DATABASE),
                    "success": "DB CONNECT SUCCESS"
                })
            return self.session
        except Exception as e:
            logger.info("[ERROR]", extra={
                    "operation": str(APP_INIT.DATABASE),
                    "error": str(e)
                })
            sys.exit(1)

    def createAllTables(self):
        Base.metadata.create_all(engine)
        logger.info("[SUCCESS]", extra={
                    "operation": str(APP_INIT.DATABASE),
                    "success": "DB TABLE CREATED"
                })
    
    def teardown(self):
        if self.session:
            self.session.close()
    
    def query(self, *args, **kwargs):
        return self.session.query(*args, **kwargs)

    # --------------------- CRUD ---------------------
    def create(self, model_class, **data):
        """Dynamically creates a new record in the database."""
        try:
            instance = model_class(**data)
            self.session.add(instance)
            self.session.commit()
            self.session.refresh(instance)
            return instance
        except Exception as e:
            self.session.rollback()
            logger.error("[ERROR]", extra={
                "operation": str(APP_INIT.DATABASE),
                "error": f"DB CREATE ERROR: {str(e)}"
            })
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to create {model_class.__name__} invalid request")

    def read(self, model_class, join_loads=None, **filters):
        """Dynamically retrieves a record from the database with optional joined loads."""
        try:
            query = self._build_query(model_class, **filters)
    
            if join_loads:
                for relation in join_loads:
                    query = query.options(joinedload(getattr(model_class, relation)))
    
            result = query.first()

            if not result:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No {model_class.__name__} found with given filters.")
            return result
        except HTTPException as http_exc:
            raise http_exc
        except Exception as e:
            self.session.rollback()
            logger.error("[ERROR]", extra={
                "operation": str(APP_INIT.DATABASE),
                "error": f"DB READ ERROR: {str(e)}"
            })
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error while reading from the database.")

    def update(self, model_class, filter_conditions: dict, update_values: dict) -> bool:
        """Dynamically updates a record in the database."""
        try:
            query = self._build_query(model_class, **filter_conditions)
            result = query.update(update_values)
            if result == 0:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"No {model_class.__name__} found to update.")
            self.session.commit()
            return True
        except HTTPException as http_exc:
            raise http_exc
        except Exception as e:
            self.session.rollback()
            logger.error("[ERROR]", extra={
                "operation": str(APP_INIT.DATABASE),
                "error": f"DB UPDATE ERROR: {str(e)}"
            })
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error while updating the record for {model_class.__name__} found with given filters.")

    def delete(self, model_class, **filters) -> bool:
        """Dynamically deletes a record from the database."""
        try:
            query = self._build_query(model_class, **filters)
            result = query.delete()
            self.session.commit()

            if result == 0:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"No {model_class.__name__} found to delete.")
            return True
        except HTTPException as http_exc:
            raise http_exc

        except Exception as e:
            self.session.rollback()
            logger.error("[ERROR]", extra={
                "operation": str(APP_INIT.DATABASE),
                "error": f"DB DELETE ERROR: {str(e)}"
            })
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error while deleting the record.")

    # --------------------- BULK OPERATIONS ---------------------
    def bulk_create(self, model_class, data_list: List[dict], **kwargs):
        """Bulk creates new records in the database."""
        try:
            instances = [model_class(**data) for data in data_list]
            self.session.bulk_save_objects(instances)
            self.session.commit()
            return instances
        except Exception as e:
            self.session.rollback()
            logger.error("[ERROR]", extra={
                "operation": str(APP_INIT.DATABASE),
                "error": f"DB BULK CREATE ERROR: {str(e)}"
            })
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to bulk create {model_class.__name__}")

    def bulk_read(self, model_class, 
              filters: Optional[dict] = None, 
              sort_column: str = None,
              sort_direction: str  = None,
              limit: int = 0, 
              offset: int = 0,
              join_loads: Optional[List[str]] = None, 
              date_filters: Optional[dict] = None,  # New argument for date filtering
             ) -> List[dict]:
        """
        Bulk retrieves records from the database with support for limit, offset, sorting, filtering, and join loading.

        :param model_class: The SQLAlchemy model class.
        :param filters: A dictionary of filters to apply.
        :param order_by: A list of fields to order by. Use '-' prefix for descending order (e.g., '-created_at').
        :param limit: The number of records to retrieve.
        :param offset: The starting offset for the query.
        :param join_loads: A list of relationships to eagerly load.
        :param date_filters: A dictionary of date filters (field names as keys and date values).
        :return: A list of dictionaries representing the retrieved records.
        """
        try:
            # Start building the query with or without filters
            query = self._build_query(model_class, join_loads=join_loads, **filters) if filters else self.session.query(model_class)
            
            # Apply join loading if provided
            if join_loads:
                for relation in join_loads:
                    query = query.options(joinedload(getattr(model_class, relation)))
            
            # Apply date filters
            if date_filters:
                for date_field, date_value in date_filters.items():
                    query = query.filter(cast(getattr(model_class, date_field), Date) == date_value)

            # Apply ordering
            if sort_column and sort_direction:
                if sort_direction == "desc":
                    query = query.order_by(desc(getattr(model_class, sort_column)))    
                else:
                    query = query.order_by(asc(getattr(model_class, sort_column)))
            
            # Apply limit and offset
            if limit > 0:
                query = query.limit(limit).offset(offset)
            
            # Execute the query and return results
            results = query.all()
            return results
        
        except Exception as e:
            logger.error("[ERROR]", extra={
                "operation": str(APP_INIT.DATABASE),
                "error": f"DB BULK READ ERROR: {str(e)}"
            })
            self.session.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid Request filter for {model_class.__name__}.")



    def bulk_update(self, model_class, filter_conditions: dict, update_values: dict) -> bool:
        """Bulk updates records in the database."""
        try:
            query = self._build_query(model_class, **filter_conditions)
            query.update(update_values, synchronize_session=False)
            self.session.commit()
            return True
        except Exception as e:
            self.session.rollback()
            logger.error("[ERROR]", extra={
                "operation": str(APP_INIT.DATABASE),
                "error": f"DB BULK UPDATE ERROR: {str(e)}"
            })
            return False

    def bulk_delete(self, model_class, **filters) -> bool:
        """Bulk deletes records from the database."""
        try:
            query = self._build_query(model_class, **filters)
            result = query.delete(synchronize_session=False)
            self.session.commit()
            if result == 0:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"No {model_class.__name__} records found to delete.")
            return True
        except Exception as e:
            self.session.rollback()
            logger.error("[ERROR]", extra={
                "operation": str(APP_INIT.DATABASE),
                "error": f"DB BULK DELETE ERROR: {str(e)}"
            })
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error while bulk deleting the records.")

    def read_with_join(self, primary_model, related_model, primary_key, related_key, 
                       filters: Optional[dict] = None, 
                       related_filters: Optional[dict] = None, join_loads=[]) -> dict:
        """
        Reads a record from the primary model and joins it with a related model.

        :param primary_model: The primary SQLAlchemy model class.
        :param related_model: The related SQLAlchemy model class to join with.
        :param primary_key: The foreign key in the primary model.
        :param related_key: The key in the related model to join on.
        :param filters: Filters to apply on the primary model.
        :param related_filters: Filters to apply on the related model.
        :return: A dictionary representing the joined records.
        """
        try:
            query = self._build_query(primary_model, **filters) if filters else self.session.query(primary_model)
            query = query.join(related_model, getattr(primary_model, primary_key) == getattr(related_model, related_key))

            if related_filters:
                for key, value in related_filters.items():
                    query = query.filter(getattr(related_model, key) == value)
            
            result = query.first()
            if result:
                return self.to_dict(result, include_relationships=True, relationships_to_include=join_loads)
            return None

        except Exception as e:
            logger.error("[ERROR]", extra={
                "operation": str(APP_INIT.DATABASE),
                "error": f"DB READ WITH JOIN ERROR: {str(e)}"
            })
            return False


    # --------------------- HELPER METHODS ---------------------

    def _build_query(self, model_class, join_loads=None, **filters):
        """Dynamically builds a query based on the provided model and filters."""
        query = self.session.query(model_class)
        if join_loads:
            for relation in join_loads:
                query = query.options(joinedload(getattr(model_class, relation)))


        for key, value in filters.items():
            column_attr = getattr(model_class, key)

            if isinstance(value, list):
                for condition in value:
                    if isinstance(condition, dict):
                        for operator, filter_value in condition.items():
                            query = self._apply_filter(query, column_attr, operator, filter_value)

            elif isinstance(value, dict):
                for operator, filter_value in value.items():
                    query = self._apply_filter(query, column_attr, operator, filter_value)
            else:
                query = query.filter(column_attr == value)

        return query

    def _apply_filter(self, query, column_attr, operator, filter_value):
        """Applies the corresponding SQLAlchemy filter based on the operator."""
        if operator == "$gte":  # Greater than or equal
            return query.filter(column_attr >= filter_value)
        elif operator == "$gt":  # Greater than
            return query.filter(column_attr > filter_value)
        elif operator == "$lte":  # Less than or equal
            return query.filter(column_attr <= filter_value)
        elif operator == "$lt":  # Less than
            return query.filter(column_attr < filter_value)
        elif operator == "$eq":  # Equal
            return query.filter(column_attr == filter_value)
        elif operator == "$ne":  # Not equal
            return query.filter(column_attr != filter_value)
        elif operator == "$in" and filter_value:  # In a list of values
            return query.filter(column_attr.in_(filter_value))
        elif operator == "$not_in" and filter_value:  # Not in a list of values
            return query.filter(~column_attr.in_(filter_value))
        elif operator == "$like":  # LIKE query
            return query.filter(column_attr.like(f"%{filter_value}%"))
        elif operator == "$not_like":  # NOT LIKE query
            return query.filter(~column_attr.like(f"%{filter_value}%"))
        elif operator == "$or":  # OR condition
            conditions = [getattr(column_attr, k) == v for k, v in filter_value.items()]
            return query.filter(or_(*conditions))
        elif operator == "$and":  # AND condition
            conditions = [getattr(column_attr, k) == v for k, v in filter_value.items()]
            return query.filter(and_(*conditions))
        else:
            raise ValueError(f"Unsupported filter operator: {operator}")
        

def get_db():
    db = DB()
    try:
        yield db
    finally:
        db.close()