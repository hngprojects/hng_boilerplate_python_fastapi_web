from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from urllib.parse import urlparse, parse_qs
from api.v1.schemas import invitations
from api.db.database import get_db as get_session
from api.v1.services import invite
from api.v1.models.user import User
from api.v1.services.user import user_service
import logging

invites = APIRouter(prefix="/invite", tags=["Invitation Management"])

# Add other necessary imports


# generate invitation link to join organization
@invites.post("/create", tags=["Invitation Management"])
async def generate_invite_link(
    invite_schema: invitations.InvitationCreate, 
    request: Request, 
    session: Session = Depends(get_session), 
    current_user: User = Depends(user_service.get_current_user)
):
    return invite.InviteService.create(invite_schema, request, session)


# Add user to organization
@invites.post("/accept", tags=["Invitation Management"])
async def add_user_to_organization(
    request: Request, 
    user_data: invitations.UserAddToOrganization, 
    session: Session = Depends(get_session), 
    current_user: User = Depends(user_service.get_current_user)
):
    logging.info("Received request to accept invitation.")
    query_params = parse_qs(urlparse(user_data.invitation_link).query)
    invite_id = query_params.get("invitation_id", [None])[0]

    if not invite_id:
        logging.warning("Invitation ID not found in the link.")
        raise HTTPException(status_code=400, detail="Invalid invitation link")

    logging.info(f"Processing invitation ID: {invite_id}")

    return invite.InviteService.add_user_to_organization(invite_id, session)