import logging, uuid
from datetime import datetime, timedelta
from collections import OrderedDict
from urllib.parse import urlparse, parse_qs, urlencode

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import insert
from pytz import timezone

from api.v1.schemas import invitations
from api.utils.json_response import JSONResponse
from api.v1.models.invitation import Invitation
from api.v1.models.user import User
from api.v1.models.org import Organization
from api.v1.models.base import user_organization_association
from api.db.database import engine, SessionLocal
from api.v1.models.base import Base

# Define the timezone (e.g., UTC)
utc = timezone('UTC')

# Set passlib logger level to ERROR
logging.getLogger('passlib').setLevel(logging.ERROR)

Base.metadata.create_all(engine)

def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

invite = APIRouter(prefix='/api/v1/invite', tags=["org"])

@invite.post("/create", tags=["Invitation Management"])
async def generate_invite_link(invite: invitations.InvitationCreate, session: Session = Depends(get_session)):
    user = session.query(User).filter_by(id=invite.user_id).first()
    org = session.query(Organization).filter_by(id=invite.organization_id).first()

    if not user or not org:
        raise HTTPException(status_code=400, detail="Invalid user or organization ID")

    expiration = datetime.utcnow() + timedelta(days=1)
    new_invite = Invitation(user_id=invite.user_id, organization_id=invite.organization_id, expires_at=expiration)
    
    session.add(new_invite)
    session.commit()
    session.refresh(new_invite)

    # Invite link placeholder
    invite_link = f"http://127.0.0.1:8000/api/v1/invite/accept?{urlencode({'invitation_id': str(new_invite.id)})}"
    
    return {"invitation_link": invite_link}

# Add user to organization
@invite.post("/accept", tags=["Organization Management"])
async def add_user_to_organization(user_data: invitations.UserAddToOrganization, session: Session = Depends(get_session)):
    logging.info("Received request to accept invitation.")
    query_params = parse_qs(urlparse(user_data.invitation_link).query)
    invite_id = query_params.get('invitation_id', [None])[0]

    if not invite_id:
        logging.warning("Invitation ID not found in the link.")
        raise HTTPException(status_code=400, detail="Invalid invitation link")

    logging.info(f"Processing invitation ID: {invite_id}")
    try:
        invite_uuid = uuid.UUID(invite_id)
    except ValueError:
        logging.warning("Malformed invitation ID.")
        raise HTTPException(status_code=400, detail="Invalid invitation link")

    invite = session.query(Invitation).filter_by(id=invite_uuid, is_valid=True).first()

    if not invite:
        logging.warning(f"Invalid or expired invitation link: {invite_id}")
        raise HTTPException(status_code=404, detail="Invalid or expired invitation link")

    now = datetime.now(utc)
    if invite.expires_at < now:
        logging.warning(f"Expired invitation link: {invite_id}")
        invite.is_valid = False
        session.commit()
        raise HTTPException(status_code=400, detail="Expired invitation link")

    user = session.query(User).filter_by(id=invite.user_id).first()
    org = session.query(Organization).filter_by(id=invite.organization_id).first()

    if not org:
        logging.error(f"Organization not found: {invite.organization_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid organization ID"
        )

    if not user:
        logging.error(f"User not found: {invite.user_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid user ID"
        )

    user_organizations = session.execute(
        user_organization_association.select().where(
            user_organization_association.c.user_id == user.id,
            user_organization_association.c.organization_id == org.id
        )
    ).fetchall()

    if user_organizations:
        logging.warning(f"User {user.id} already in organization {org.id}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already in organization"
        )

    try:
        # Insert user and organization relationship into the association table
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
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while adding the user to the organization"
        )
