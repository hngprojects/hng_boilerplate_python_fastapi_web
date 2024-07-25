""" User data model
"""
from sqlalchemy import (
        create_engine,
        Column,
        Integer,
        String,
        Text,
        text,
        Date,
        ForeignKey,
        Numeric,
        DateTime,
        func,
        Table,
        Boolean
        )
from sqlalchemy.orm import relationship
from datetime import datetime
from api.v1.models.base import Base, user_organization_association, user_newsletter_association
from api.v1.models.base_model import BaseTableModel



class User(BaseTableModel):
    __tablename__ = 'users'

    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    is_active = Column(Boolean, server_default=text("false"))
    is_super_admin = Column(Boolean, server_default=text("false"))
    is_deleted = Column(Boolean, server_default=text("false"))
    is_verified = Column(Boolean, server_default=text("false"))

    profile = relationship("Profile", uselist=False, back_populates="user", cascade="all, delete-orphan")
    organizations = relationship("Organization", secondary=user_organization_association, back_populates="users")
    roles = relationship("OrgRole", back_populates="user", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    activity_logs = relationship("ActivityLog", back_populates="user", cascade="all, delete-orphan")
    jobs = relationship("Job", back_populates="author", cascade="all, delete-orphan")
    token_login = relationship("TokenLogin", back_populates="user", uselist=False, cascade="all, delete-orphan")
    oauth = relationship("OAuth", back_populates="user", uselist=False, cascade="all, delete-orphan")
    testimonials = relationship("Testimonial", back_populates="author", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="user", cascade="all, delete-orphan") 
    blogs = relationship("Blog", back_populates="author", cascade="all, delete-orphan") 
    comments = relationship("Comment", back_populates="user", cascade="all, delete-orphan")
    invitations = relationship("Invitation", back_populates="user", cascade="all, delete-orphan")
    messages = relationship("Message", back_populates="user", cascade="all, delete-orphan")
    newsletters = relationship("Newsletter", secondary=user_newsletter_association, back_populates="subscribers")
    blog_likes = relationship("BlogLike", back_populates="user", cascade="all, delete-orphan")
    blog_dislikes = relationship("BlogDislike", back_populates="user", cascade="all, delete-orphan")
    
    def to_dict(self):
        obj_dict = super().to_dict()
        obj_dict.pop("password")
        return obj_dict


    def __str__(self):
        return self.email