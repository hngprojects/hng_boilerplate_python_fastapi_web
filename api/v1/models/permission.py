# from sqlalchemy import Column, String, Integer, DateTime, func
# from sqlalchemy.orm import relationship
# from api.v1.models.base import Base
# from api.v1.models.base_model import BaseTableModel
# from api.v1.models.base import role_permission_association
# from uuid_extensions import uuid7
# from sqlalchemy.dialects.postgresql import UUID

# class Permission(BaseTableModel):
#     __tablename__ = 'permissions'

#     name = Column(String, index=True, nullable=False)

#     roles = relationship('Role', secondary=role_permission_association, back_populates='permissions')


# def get_user_permissions(self):
#     """Get all permissions assigned to a user."""
#     permissions = set()
#     for role in self.roles:
#         for permission in role.permissions:
#             permissions.add(permission.name)
#     return permissions

# def user_has_permission(self, permission) -> bool:
#     """Check if a user has a specific permission."""
#     perms = self.get_user_permissions()
#     if permission in perms:
#             return True
#     else:
#             return False

