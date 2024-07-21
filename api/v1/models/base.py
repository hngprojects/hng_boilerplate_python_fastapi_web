#!/usr/bin/env python3
""" Base
"""
from sqlalchemy import (
        Column,
        Integer,
        ForeignKey,
        Table,
        DateTime,
        func
        )
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID


Base = declarative_base()


user_organization_association = Table('user_organization', Base.metadata,
        Column('user_id', UUID(as_uuid=True), ForeignKey('users.id',  ondelete='CASCADE'), primary_key=True),
        Column('organization_id', UUID(as_uuid=True), ForeignKey('organizations.id',  ondelete='CASCADE'), primary_key=True)
        )

user_role_association = Table('user_role', Base.metadata,
    Column('user_id', UUID(as_uuid=True), ForeignKey('users.id',  ondelete='CASCADE'), primary_key=True),
    Column('role_id', UUID(as_uuid=True), ForeignKey('roles.id',  ondelete='CASCADE'), primary_key=True)
)

role_permission_association = Table(
    'role_permission', Base.metadata,
    Column('role_id', UUID(as_uuid=True), ForeignKey('roles.id',  ondelete='CASCADE'), primary_key=True),
    Column('permission_id', UUID(as_uuid=True), ForeignKey('permissions.id',  ondelete='CASCADE'), primary_key=True)
)



class BaseModel():
    """ This model creates helper methods for all models
    """
    __abstract__ = True

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def to_dict(self):
        """ returns a dictionary representation of the instance
        """
        obj_dict = self.__dict__.copy()
        del obj_dict["_sa_instance_state"]
        obj_dict['id'] = str(self.id)
        if self.created_at:
            obj_dict["created_at"] = self.created_at.isoformat()
        if self.updated_at:
            obj_dict["updated_at"] = self.updated_at.isoformat()
        return obj_dict

    @classmethod
    def get_all(cls):
        """ returns all instance of the class in the db
        """
        from api.db.database import db
        return db.query(cls).all()

    @classmethod
    def get_by_id(cls, id):
        """ returns a single object from the db
        """
        from api.db.database import db
        obj = db.query(cls).filter_by(id=id).first()
        return obj
