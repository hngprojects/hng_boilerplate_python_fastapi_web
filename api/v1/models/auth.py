from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, BIGINT, Text
from sqlalchemy.orm import relationship
from datetime import datetime, date
from api.db.database import Base
import passlib.hash as _hash


class User(Base):
    __tablename__ = "users"
    id = Column(BIGINT, primary_key=True, autoincrement=True, index=True)
    unique_id = Column(String(255), nullable=True)
    first_name = Column(String(255), nullable=False)
    last_name = Column(String(255), nullable=False)
    email = Column(String(500), unique=True, index=True, nullable=False)
    password = Column(String(500), nullable=False)
    is_active = Column(Boolean, default=True)
    date_created = Column(DateTime,default=datetime.utcnow)
    last_updated = Column(DateTime,default=datetime.utcnow)
    is_deleted = Column(Boolean, default=False)

class BlackListToken(Base):
    __tablename__ = "blacklist_tokens"
    id = Column(BIGINT, primary_key=True, autoincrement=True, index=True)
    created_by = Column(BIGINT, ForeignKey('users.id'), index=True)
    token = Column(String(255), index=True)
    date_created = Column(DateTime, default= datetime.utcnow)


