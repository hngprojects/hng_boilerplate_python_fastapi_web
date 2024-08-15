import logging
from datetime import datetime, timedelta
from pytz import utc
from sqlalchemy.orm import Session
from sqlalchemy import insert
from fastapi import HTTPException, Request, Depends, status
from collections import OrderedDict
from fastapi.responses import JSONResponse
from api.v1.models.invitation import Invitation
from api.v1.models.organisation import Organisation
from api.v1.models.user import User
from api.v1.services.user import user_service
from sqlalchemy.exc import IntegrityError
from api.v1.models.permissions.role import Role
from api.v1.schemas.permissions.roles import RoleCreate
from api.v1.services.permissions.role_service import role_service
from api.v1.models.permissions.user_org_role import user_organisation_roles
from api.v1.schemas import invitations
from api.core.base.services import Service
from urllib.parse import urlencode


class InviteService(Service):
    @staticmethod
    def create(
        invite: invitations.InvitationCreate, request: Request, session: Session
    ):

        user_email = session.query(User).filter_by(email=invite.user_email).first()
        org = session.query(Organisation).filter_by(id=invite.organisation_id).first()

        if not user_email or not org:
            exceptions = HTTPException(
                status_code=404, detail="invalid user or organisation id"
            )
            print(exceptions)
            raise exceptions

        user_organisations = session.execute(
            user_organisation_roles.select().where(
                user_organisation_roles.c.user_id == user_email.id,
                user_organisation_roles.c.organisation_id == org.id,
            )
        ).fetchall()

        if user_organisations:
            logging.warning(f"User {user_email.id} already in organisation {org.id}")
            raise HTTPException(status_code=400, detail="User already in organisation")

        expiration = datetime.now(utc) + timedelta(days=1)
        new_invite = Invitation(
            user_id=user_email.id,
            organisation_id=invite.organisation_id,
            expires_at=expiration,
        )

        session.add(new_invite)
        session.commit()
        session.refresh(new_invite)

        base_url = request.base_url
        invite_link = f'{base_url}api/v1/invite/accept?{urlencode({"invitation_id": str(new_invite.id)})}'

        response = {
            "message": "Invitation link created successfully",
            "data": {
                "invitation_link": invite_link,
                "success": True,
                "status_code": status.HTTP_201_CREATED,
            },
        }
        return response



    @staticmethod
    def add_user_to_organisation(invite_id: str, session: Session):
        logging.info(f"Processing invitation ID: {invite_id}")

        # Fetch the invitation
        invite = session.query(Invitation).filter_by(id=invite_id, is_valid=True).first()
        logging.info(f"Found invitation: {invite}")

        if not invite:
            logging.warning(f"Invitation with ID {invite_id} not found or already used")
            raise HTTPException(status_code=404, detail="Invitation not found or already used")

        # Check invitation expiration

        now = datetime.now(utc)
        logging.info(f"Current UTC time: {now}")
        logging.info(f"Invitation expires at: {invite.expires_at}")

        if invite.expires_at < now:
            logging.warning(f"Expired invitation link: {invite_id}")
            invite.is_valid = False
            session.commit()
            raise HTTPException(status_code=400, detail="Expired invitation link")

        # Fetch user and organisation
        user = session.query(User).filter_by(id=invite.user_id).first()
        org = session.query(Organisation).filter_by(id=invite.organisation_id).first()

        if not org:
            logging.error(f"Organisation not found: {invite.organisation_id}")
            raise HTTPException(status_code=404, detail="Invalid organisation ID")

        if not user:
            logging.error(f"User not found: {invite.user_id}")
            raise HTTPException(status_code=404, detail="Invalid user ID")

        # Define the default role name
        default_role_name = "user"

        # Check if the default role exists
        role = session.query(Role).filter_by(name=default_role_name).first()

        if not role:
            # Create the default role if it doesn't exist
            logging.info(f"Role '{default_role_name}' not found. Creating new role.")
            role_create_data = RoleCreate(name=default_role_name, is_builtin=True)
            role = role_service.create_role(session, role_create_data)

        # Check if the user is already assigned to the role within the organisation
        existing_assignment = session.query(user_organisation_roles).filter_by(
            user_id=user.id,
            organisation_id=org.id,
            role_id=role.id
        ).first()

        if existing_assignment:
            #logging.warning(f"User {user} is already assigned to the role '{role.name}' in organisation {org.id}")
            raise HTTPException(
                status_code=400, 
                detail=f"User is already assigned to the role in this organisation"
            )

        try:
            # Insert user-organisation-role association
            stmt = insert(user_organisation_roles).values(
                user_id=user.id,
                organisation_id=org.id,
                role_id=role.id,
                status="active"  # Default status
            )
            session.execute(stmt)

            # Mark the invitation as used
            invite.is_valid = False
            session.commit()

            response = OrderedDict(
                [
                    ("status", "success"),
                    ("message", "User added to organisation and default role assigned successfully"),
                ]
            )
            logging.info(f"User {user.id} added to organisation {org.id} and default role assigned successfully.")
            return JSONResponse(content=response)

        except IntegrityError as e:
            session.rollback()
            logging.error(f"IntegrityError: {e}")
            raise HTTPException(
                status_code=400, 
                detail="An error occurred while assigning the role to the user in the organisation"
            )
        except Exception as e:
            session.rollback()
            logging.error(f"Error adding user to organisation: {e}")
            raise HTTPException(
                status_code=500,
                detail="An error occurred while adding the user to the organisation"
            )
    @staticmethod
    def delete(session: Session, id: str):
        """Function to delete invite link
        
        Args:
            session(Session): The current ORM session object.
            id(str): Invite id string

        Returns:
            True if delete is successful else False
        
        """
        invite = (
            session.query(Invitation).filter_by(id=id).first()
        )
        
        if invite is None:
            return False
        session.delete(invite)
        session.commit()
        return True
    
    @staticmethod
    def delete_all(session: Session):
        """Function to delete all invite links
        
        Args:
            session(Session): The current ORM session object.
            id(str): Invite id string
        
        """
        all_invites = session.query(Invitation).all()
        
        for invite in all_invites:
            session.delete(invite)
        
        session.commit()
    
    def fetch(self):
        pass

    def fetch_all(self):
        pass
    def update(self):
        pass
    
invite_service = InviteService()