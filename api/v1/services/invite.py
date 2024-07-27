import logging
from datetime import datetime, timedelta
from pytz import utc
from sqlalchemy.orm import Session
from sqlalchemy import insert
from fastapi import HTTPException, Request
from collections import OrderedDict
from fastapi.responses import JSONResponse
from api.db.database import get_db
from api.v1.models.invitation import Invitation
from api.v1.models.org import Organization
from api.v1.models.user import User
from api.v1.models.base import user_organization_association
from api.v1.schemas import invitations
from urllib.parse import urlencode

class InviteService:
    @staticmethod
    def create(invite: invitations.InvitationCreate, request: Request, session: Session):
        user = session.query(User).filter_by(id=invite.user_id).first()
        org = session.query(Organization).filter_by(id=invite.organization_id).first()

        if not user or not org:
            raise HTTPException(status_code=400, detail="Invalid user or organization ID")

        expiration = datetime.now(utc) + timedelta(days=1)
        new_invite = Invitation(user_id=invite.user_id, organization_id=invite.organization_id, expires_at=expiration)
        
        session.add(new_invite)
        session.commit()
        session.refresh(new_invite)

        base_url = request.base_url
        invite_link = f'{base_url}api/v1/invite/accept?{urlencode({"invitation_id": str(new_invite.id)})}'
        
        return {"invitation_link": invite_link}

    @staticmethod
    def add_user_to_organization(invite_id: str, session: Session):
        logging.info(f"Processing invitation ID: {invite_id}")

        invite = session.query(Invitation).filter_by(id=invite_id, is_valid=True).first()
        logging.info(f"Found invitation: {invite}")

        if not invite:
            logging.warning(f"Invitation with ID {invite_id} not found or already used")
            raise HTTPException(status_code=404, detail="Invitation not found or already used")

        now = datetime.now(utc)
        logging.info(f"Current UTC time: {now}")
        logging.info(f"Invitation expires at: {invite.expires_at}")

        if invite.expires_at < now:
            logging.warning(f"Expired invitation link: {invite_id}")
            invite.is_valid = False
            session.commit()
            raise HTTPException(status_code=400, detail="Expired invitation link")

        user = session.query(User).filter_by(id=invite.user_id).first()
        org = session.query(Organization).filter_by(id=invite.organization_id).first()

        if not org:
            logging.error(f"Organization not found: {invite.organization_id}")
            raise HTTPException(status_code=404, detail="Invalid organization ID")

        if not user:
            logging.error(f"User not found: {invite.user_id}")
            raise HTTPException(status_code=404, detail="Invalid user ID")

        user_organizations = session.execute(
            user_organization_association.select().where(
                user_organization_association.c.user_id == user.id,
                user_organization_association.c.organization_id == org.id
            )
        ).fetchall()

        if user_organizations:
            logging.warning(f"User {user.id} already in organization {org.id}")
            raise HTTPException(status_code=400, detail="User already in organization")

        try:
            stmt = insert(user_organization_association).values(user_id=user.id, organization_id=org.id)
            session.execute(stmt)
            session.commit()

            invite.is_valid = False
            session.commit()

            response = OrderedDict([
                ("status", "success"),
                ("message", "User added to organization successfully")
            ])
            logging.info(f"User {user.id} added to organization {org.id} successfully.")
            return JSONResponse(content=response)
        
        except Exception as e:
            session.rollback()
            logging.error(f"Error adding user to organization: {e}")
            raise HTTPException(status_code=500, detail="An error occurred while adding the user to the organization")

invite_service = InviteService()