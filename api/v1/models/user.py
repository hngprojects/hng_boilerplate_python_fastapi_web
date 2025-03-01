""" User data model
"""

from sqlalchemy import Column, String, text, Boolean
from sqlalchemy.orm import relationship
from api.v1.models.associations import user_organisation_association
from api.v1.models.permissions.user_org_role import user_organisation_roles
from api.v1.models.base_model import BaseTableModel


class User(BaseTableModel):
    __tablename__ = "users"

    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    avatar_url = Column(String, nullable=True)
    is_active = Column(Boolean, server_default=text("true"))
    is_superadmin = Column(Boolean, server_default=text("false"))
    is_deleted = Column(Boolean, server_default=text("false"))
    is_verified = Column(Boolean, server_default=text("false"))

    profile = relationship(
        "Profile", uselist=False, back_populates="user", cascade="all, delete-orphan"
    )
    organisations = relationship(
        "Organisation", secondary=user_organisation_roles, back_populates="users"
    )
    notifications = relationship(
        "Notification", back_populates="user", cascade="all, delete-orphan"
    )
    activity_logs = relationship(
        "ActivityLog", back_populates="user", cascade="all, delete-orphan"
    )
    jobs = relationship("Job", back_populates="author", cascade="all, delete-orphan")
    token_login = relationship(
        "TokenLogin", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    oauth = relationship(
        "OAuth", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    testimonials = relationship(
        "Testimonial", back_populates="author", cascade="all, delete-orphan"
    )
    payments = relationship(
        "Payment", back_populates="user", cascade="all, delete-orphan"
    )
    blogs = relationship("Blog", back_populates="author", cascade="all, delete-orphan")
    comments = relationship(
        "Comment", back_populates="user", cascade="all, delete-orphan"
    )
    invitations = relationship(
        "Invitation", back_populates="user", cascade="all, delete-orphan"
    )
    messages = relationship(
        "Message", back_populates="user", cascade="all, delete-orphan"
    )
    blog_likes = relationship(
        "BlogLike", back_populates="user", cascade="all, delete-orphan"
    )
    blog_dislikes = relationship(
        "BlogDislike", back_populates="user", cascade="all, delete-orphan"
    )
    comment_likes = relationship(
        "CommentLike", back_populates="user", cascade="all, delete-orphan"
    )
    comment_dislikes = relationship(
        "CommentDislike", back_populates="user", cascade="all, delete-orphan"
    )
    notification_setting = relationship(
        "NotificationSetting",
        back_populates="user",
        cascade="all, delete-orphan",
        uselist=False,
    )
    region = relationship("Region", back_populates="user", cascade="all, delete-orphan")
    squeeze = relationship(
        "Squeeze", back_populates="user", cascade="all, delete-orphan"
    )
    data_privacy_setting = relationship(
        "DataPrivacySetting",
        uselist=False,
        back_populates="user",
        cascade="all, delete-orphan",
    )
    product_comments = relationship("ProductComment", back_populates="user", cascade="all, delete-orphan")

    subscriptions = relationship(
        "UserSubscription", back_populates="user", cascade="all, delete-orphan"
    )

    reset_password_token = relationship("ResetPasswordToken",
                                        back_populates="user",
                                        cascade="all, delete-orphan")
    
    totp_device = relationship("TOTPDevice", back_populates="user", cascade="all, delete-orphan")
    
    def to_dict(self):
        obj_dict = super().to_dict()
        obj_dict.pop("password")
        return obj_dict

    def __str__(self):
        return self.email
