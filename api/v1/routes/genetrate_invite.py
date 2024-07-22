import logging
import uuid
from datetime import datetime, timedelta
from collections import OrderedDict
from urllib.parse import urlencode

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import insert
from pytz import timezone


from api.v1.schemas import invitations
from api.utils.json_response import JSONResponse
from api.v1.models.invitation import Invitation
from api.v1.models.user import User
from api.v1.models.org import Organization
from api.v1.models.base import user_organization_association, Base
from api.db.database import engine, SessionLocal

# Configure logging
logging.getLogger('passlib').setLevel(logging.ERROR)

# Define constants
UTC = timezone('UTC')
INVITE_URL = "http://127.0.0.1:8000/api/v1/invite/accept"

# Create database tables
Base.metadata.create_all(engine)


def get_session():
    """
    Provide a transactional scope around a series of operations.
    """
    session = SessionLocal()
    try:
        yield session
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


# APIRouter instance
invite = APIRouter(prefix='/api/v1/invite', tags=["org"])


@invite.post("/create", tags=["Invitation Management"])
async def generate_invite_link(invite: invitations.InvitationCreate, session: Session = Depends(get_session)):
    """
    Generate an invitation link for a user to join an organization.
    """
    user = session.query(User).filter_by(id=invite.user_id).first()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid user ID")

    org = session.query(Organization).filter_by(id=invite.organization_id).first()
    if not org:
        raise HTTPException(status_code=400, detail="Invalid organization ID")

    expiration = datetime.utcnow() + timedelta(days=1)
    new_invite = Invitation(user_id=invite.user_id, organization_id=invite.organization_id, expires_at=expiration)

    session.add(new_invite)
    session.commit()
    session.refresh(new_invite)

    invite_link = f"{INVITE_URL}?{urlencode({'invitation_id': str(new_invite.id)})}"

    return {"invitation_link": invite_link}
