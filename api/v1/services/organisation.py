import csv
from io import StringIO
import logging
from typing import Any, Optional, Annotated
from fastapi import HTTPException, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from fastapi import HTTPException, status
from sqlalchemy import select
from api.core.base.services import Service
from api.utils.db_validators import check_model_existence, check_user_in_org
from api.utils.pagination import paginated_response
from api.v1.models.permissions.role import Role
from api.v1.models.product import Product
from api.v1.models.permissions.role_permissions import role_permissions
from api.v1.models.permissions.permissions import Permission
from api.v1.models.associations import user_organisation_association
from api.v1.models.permissions.user_org_role import user_organisation_roles
from api.v1.models.organisation import Organisation
from api.v1.models.user import User
from api.v1.schemas.organisation import (
    CreateUpdateOrganisation,
    AddUpdateOrganisationRole,
    RemoveUserFromOrganisation,
    OrganisationData
)
from api.db.database import get_db


class OrganisationService(Service):
    """Organisation service functionality"""

    def get_role_id(self, db: Session, role: str):
        '''Returns the role id associated with a role'''

        role_ = db.query(Role).filter(Role.name == role).first()

        if not role_:
            raise HTTPException(status_code=404, detail="Admin role not found")

        return role_.id
    

    def create(self, db: Session, schema: CreateUpdateOrganisation, user: User):
        """Create a new product"""

        # Create a new organisation
        new_organisation = Organisation(**schema.model_dump())
        
        email = schema.model_dump()["email"]
        self.check_by_email(db, email)

        db.add(new_organisation)
        db.commit()
        db.refresh(new_organisation)

        # Add user as owner to the new organisation
        stmt = user_organisation_association.insert().values(
            user_id=user.id, 
            organisation_id=new_organisation.id, 
            role='owner'
        )
        db.execute(stmt)
        db.commit()
        admin_role = db.query(Role).filter_by(name="admin").first()
        if not admin_role:
            admin_role = Role(
                name="admin",
                description="Organization Admin",
                is_builtin=True
                )
            db.add(admin_role)
            db.commit()
        else:
            user_role_stmt = user_organisation_roles.insert().values(
                user_id=user.id,
                organisation_id=new_organisation.id,
                role_id=admin_role.id,
                is_owner=True,
            )
            db.execute(user_role_stmt)
            db.commit()

        return new_organisation


    def fetch_all(self, db: Session, **query_params: Optional[Any]):
        """Fetch all products with option tto search using query parameters"""

        query = db.query(Organisation)

        # Enable filter by query parameter
        if query_params:
            for column, value in query_params.items():
                if hasattr(Organisation, column) and value:
                    query = query.filter(
                        getattr(Organisation, column).ilike(f"%{value}%")
                    )

        return query.all()


    def fetch(self, db: Session, id: str):
        """Fetches an organisation by id"""

        organisation = check_model_existence(db, Organisation, id)

        return organisation

    def get_organisation_user_role(self, user_id: str, org_id: str, db: Session):
        try:
            stmt = select(user_organisation_association.c.role).where(
                user_organisation_association.c.user_id == user_id,
                user_organisation_association.c.organisation_id == org_id,
            )
            result = db.execute(stmt).scalar_one_or_none()
            return result
        except Exception as e:
            print(f"An error occurred: {e}")
            return None

    def update(self, db: Session, id: str, schema, current_user: User):
        """Updates a product"""

        organisation = self.fetch(db=db, id=id)

        # check if the current user has the permission to update the organisation
        role = self.get_organisation_user_role(current_user.id, id, db)
        if role not in ["admin", "owner"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
            )

        # Update the fields with the provided schema data
        update_data = schema.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(organisation, key, value)

        db.commit()
        db.refresh(organisation)
        return organisation

    def delete(self, db: Session, id: str):
        '''Deletes a product'''
        
        organisation = self.fetch(db, id=id)
        db.delete(organisation)
        db.commit()

    def check_user_role_in_org(self, db: Session, user: User, org: Organisation, role: str):
        '''Check user role in organisation'''

        if role not in ['user', 'guest', 'admin', 'owner']:
            raise HTTPException(status_code=400, detail="Invalid role")

        stmt = user_organisation_association.select().where(
            user_organisation_association.c.user_id == user.id,
            user_organisation_association.c.organisation_id == org.id,
            user_organisation_association.c.role == role,
        )

        result = db.execute(stmt).fetchone()

        if result is None:
            raise HTTPException(status_code=403, detail=f"Permission denied as user is not of {role} role")


    # def update_user_role(self, schema: AddUpdateOrganisationRole, db: Session, org_id: str, user_to_update_id: str):
    def update_user_role(self, schema: AddUpdateOrganisationRole, db: Session):
        '''Updates a user role'''

        # Fetch the user and organisation
        user = check_model_existence(db, User, schema.user_id)
        organisation = check_model_existence(db, Organisation, schema.org_id)

        # Check if user is not in organisation
        check_user_in_org(user, organisation)

        # Update user role
        stmt = user_organisation_association.update().where(
            user_organisation_association.c.user_id == schema.user_id,
            user_organisation_association.c.organisation_id == schema.org_id,
        ).values(role=schema.role)

        db.execute(stmt)
        db.commit()


    # def add_user_to_organisation(self, db: Session, org_id: str, user_id: str):
    def add_user_to_organisation(self, schema: AddUpdateOrganisationRole, db: Session):
        '''Adds a user to an organisation'''

        # Fetch the user and organisation
        user = check_model_existence(db, User, schema.user_id)
        organisation = check_model_existence(db, Organisation, schema.org_id)

        # Check if user is not in organisation
        check_user_in_org(user, organisation)

        # Check for user role permissions
        self.check_user_role_in_org(db=db, user=user, org=organisation, role='admin')\
              or self.check_user_role_in_org(db=db, user=user, org=organisation, role='owner')

        # Update user role
        stmt = user_organisation_association.insert().values(
            user_id=user.id,
            organisation_id=organisation.id,
            role=schema.role
        )

        db.execute(stmt)
        db.commit()


    # # def remove_user_from_organisation(self, db: Session, org_id: str, user_id: str):
    def remove_user_from_organisation(self, schema: RemoveUserFromOrganisation, db: Session):
        '''Deletes a user from an organisation'''

        # Fetch the user and organisation
        user = check_model_existence(db, User, schema.user_id)
        organisation = check_model_existence(db, Organisation, schema.org_id)

        # Check if user is not in organisation
        check_user_in_org(user, organisation)

        # Check for user role permissions
        self.check_user_role_in_org(db=db, user=user, org=organisation, role='admin')\
          or self.check_user_role_in_org(db=db, user=user, org=organisation, role='owner')

        # Update user role
        stmt = user_organisation_association.delete().where(
            user_organisation_association.c.user_id == schema.user_id,
            user_organisation_association.c.organisation_id == schema.org_id,
        )

        db.execute(stmt)
        db.commit()


    def get_users_in_organisation(self, db: Session, org_id: str):
        '''Fetches all users in an organisation'''

        organisation = check_model_existence(db, Organisation, org_id)

        # Fetch all users associated with the organisation
        return organisation.users


    def paginate_users_in_organisation(
            self,
            db: Session,
            org_id: str,
            page: int,
            per_page: int
    ):
        '''Fetches all users in an organisation'''

        check_model_existence(db, Organisation, org_id)

        return paginated_response(
            db=db,
            model=User,
            skip=page,
            join=user_organisation_association,
            filters={'organisation_id': org_id},
            limit=per_page
        )



    def get_user_organisations(self, db: Session, user_id: str):
        '''Fetches all organisations that belong to a user'''

        user = check_model_existence(db, User, user_id)

        # Fetch all users associated with the organisation
        return user.organisations

    def check_by_email(self, db: Session, email):
        """Fetches a user by their email"""

        org = db.query(Organisation).filter(Organisation.email == email).first()

        if org:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="an organisation with this email already exist")

        return False

    def check_by_name(self, db: Session, name):
        """Fetches a user by their email"""

        org = db.query(Organisation).filter(Organisation.name == name).first()

        if org:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="an organisation with this name already exist")

        return False

    def check_organisation_exist(self, db: Session, org_id):
        organisation = db.query(Organisation).filter(Organisation.id == org_id).first()
        if organisation is None:
            raise HTTPException(status_code=404, detail="Organisation not found")
        else:
            return True
        
    def export_organisation_members(self, db: Session, org_id: str):
        '''Exports the organisation members'''

        org = self.fetch(db=db, id=org_id)

        csv_file = StringIO()
        csv_writer = csv.writer(csv_file)

        # Write headers
        csv_writer.writerow(["ID", "First name", 'Last name', "Email", 'Date registered'])

        # Write member data
        for user in org.users:
            csv_writer.writerow([user.id, user.first_name, user.last_name, user.email, user.created_at])

        # Move to the beginning of the file
        csv_file.seek(0)

        return csv_file
    
    def retrieve_user_organizations(self, user: User,
                                    db: Annotated[Session, Depends(get_db)]):
        """
        Retrieves all organizations a user belongs to.
       
        Args:
            user: the user to retrieve the organizations
        """
        builtin_roles = ['user', 'admin', 'manager', 'guest']

        user_organisations = db.query(Organisation).join(
            user_organisation_association,
            Organisation.id == user_organisation_association.c.organisation_id
        ).filter(
            user_organisation_association.c.user_id == user.id
        ).all()
       
        if user_organisations:
            organisation_roles = db.query(
                Role
                ).outerjoin(
                    user_organisation_roles,
                    Role.id == user_organisation_roles.c.role_id,
                ).filter(
                    or_(
                        and_(
                            user_organisation_roles.c.user_id == user.id,
                            Role.is_builtin == False
                        ),
                        Role.is_builtin == True
                    )
                ).all()

            if len(organisation_roles) < 1:
                organisation_roles = builtin_roles
            else:
                organisation_roles = [role.name for role in organisation_roles if role]

            return [OrganisationData(
                id=org.id,
                created_at=org.created_at,
                updated_at=org.updated_at,
                name=org.name,
                email=org.email,
                industry=org.industry,
                user_role=organisation_roles,
                type=org.type,
                country=org.country,
                state=org.state,
                address=org.address,
                description=org.description,
                organisation_id=org.id
            ) for org in user_organisations]


organisation_service = OrganisationService()
