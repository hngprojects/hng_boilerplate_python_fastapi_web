import logging
from datetime import datetime, timedelta
from pytz import utc
from sqlalchemy.orm import Session
from sqlalchemy import insert
from fastapi import HTTPException, Request, Depends, status
from collections import OrderedDict
from fastapi.responses import JSONResponse
from api.v1.models.invitation import Invitation
from api.v1.models.organization import Organization
from api.v1.models.user import User
from sqlalchemy.exc import IntegrityError
from api.v1.models.permissions.role import Role
from api.v1.schemas.permissions.roles import RoleCreate
from api.v1.services.permissions.role_service import role_service
from api.v1.models.permissions.user_org_role import user_organization_roles
from api.v1.schemas import invitations
from urllib.parse import urlencode


class InviteService:
    @staticmethod
    def create(
        invite: invitations.InvitationCreate, request: Request, session: Session
    ):

        user_email = session.query(User).filter_by(email=invite.user_email).first()
        org = session.query(Organization).filter_by(id=invite.organization_id).first()

        if not user_email or not org:
            exceptions = HTTPException(
                status_code=404, detail="invalid user or organization id"
            )
            print(exceptions)
            raise exceptions

        user_organizations = session.execute(
            user_organization_roles.select().where(
                user_organization_roles.c.user_id == user_email.id,
                user_organization_roles.c.organization_id == org.id,
            )
        ).fetchall()

        if user_organizations:
            logging.warning(f"User {user_email.id} already in organization {org.id}")
            raise HTTPException(status_code=400, detail="User already in organization")

        expiration = datetime.now(utc) + timedelta(days=1)
        new_invite = Invitation(
            user_id=user_email.id,
            organization_id=invite.organization_id,
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
    def add_user_to_organization(invite_id: str, session: Session):
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

        # Fetch user and organization
        user = session.query(User).filter_by(id=invite.user_id).first()
        org = session.query(Organization).filter_by(id=invite.organization_id).first()

        if not org:
            logging.error(f"Organization not found: {invite.organization_id}")
            raise HTTPException(status_code=404, detail="Invalid organization ID")

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

        # Check if the user is already assigned to the role within the organization
        existing_assignment = session.query(user_organization_roles).filter_by(
            user_id=user.id,
            organization_id=org.id,
            role_id=role.id
        ).first()

        if existing_assignment:
            #logging.warning(f"User {user} is already assigned to the role '{role.name}' in organization {org.id}")
            raise HTTPException(
                status_code=400, 
                detail=f"User is already assigned to the role in this organization"
            )

        try:
            # Insert user-organization-role association
            stmt = insert(user_organization_roles).values(
                user_id=user.id,
                organization_id=org.id,
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
                    ("message", "User added to organization and default role assigned successfully"),
                ]
            )
            logging.info(f"User {user.id} added to organization {org.id} and default role assigned successfully.")
            return JSONResponse(content=response)

        except IntegrityError as e:
            session.rollback()
            logging.error(f"IntegrityError: {e}")
            raise HTTPException(
                status_code=400, 
                detail="An error occurred while assigning the role to the user in the organization"
            )
        except Exception as e:
            session.rollback()
            logging.error(f"Error adding user to organization: {e}")
            raise HTTPException(
                status_code=500,
                detail="An error occurred while adding the user to the organization"
            )

invite_service = InviteService()