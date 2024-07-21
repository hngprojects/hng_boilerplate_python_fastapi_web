from sqlalchemy import Column, String
from api.db.database import Base
from api.v1.models.base_model import BaseModel


class Permission(BaseModel, Base):
    __tablename__ = "permissions"

    name = Column(String, index=True, nullable=False)

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)


def get_user_permissions(self):
    """Get all permissions assigned to a user."""
    permissions = set()
    for role in self.roles:
        for permission in role.permissions:
            permissions.add(permission.name)
    return permissions

def user_has_permission(self, permission) -> bool:
    """Check if a user has a specific permission."""
    perms = self.get_user_permissions()
    if permission in perms:
            return True
    else:
            return False
