from api.db.database import get_db
from api.v1.models.permissions.role import Role
from api.v1.models.permissions.permissions import Permission

db = next(get_db())

def populate_roles_and_permissions():
    '''Function to populate database with roles and permissions'''

    # Define roles
    roles = [
        {"name": "admin", "description": "Administrator with full access", "is_builtin": True},
        {"name": "user", "description": "Regular user with limited access", "is_builtin": True},
        # {"name": "Manager", "description": "Manager with management access", "is_builtin": False},
    ]

    # Define permissions
    permissions = [
        {"title": "create_user"},
        {"title": "delete_user"},
        {"title": "update_user"},
        {"title": "view_user"},
        {"title": "manage_organisation"},
        {"title": "delete_organisation"},
    ]

    # Insert roles into the database
    for role_data in roles:
        if not db.query(Role).filter(Role.name == role_data['name']).first():
            role = Role(
                name=role_data["name"], 
                description=role_data["description"], 
                is_builtin=role_data["is_builtin"]
            )
            db.add(role)
            db.commit()
            db.refresh(role)
        
    # Insert permissions into the database
    for perm_data in permissions:
        if not db.query(Permission).filter(Permission.title == perm_data['title']).first():
            permission = Permission(title=perm_data["title"])
            db.add(permission)
            db.commit()
            db.refresh(permission)
    
    # Assign permissions to roles (example)
    admin_role = db.query(Role).filter_by(name="admin").first()
    user_role = db.query(Role).filter_by(name="user").first()
    
    if not admin_role and not user_role:
        admin_permissions = db.query(Permission).all()
        user_permissions = db.query(Permission).filter(Permission.title == "view_user").all()

        admin_role.permissions.extend(admin_permissions)
        user_role.permissions.extend(user_permissions)

        db.commit()

    db.close()
