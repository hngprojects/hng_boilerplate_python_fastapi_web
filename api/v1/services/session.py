from datetime import datetime, timezone
from sqlalchemy.orm import Session
from typing import List

from fastapi import HTTPException

from api.db.database import get_db
from api.v1.schemas.session import SessionCreate
from api.v1.models.session import UserSession

class SessionService:
    """Session service functionality."""

    def logout_session(self, db: Session, user_id: str, refresh_token: str):
        """Logout a session."""
        session = db.query(UserSession).filter(
            UserSession.refresh_token == refresh_token, UserSession.user_id == user_id).first()
        if not session:
            return
        db.delete(session)
        db.commit()

    def is_revoked_or_expired(self, db: Session, refresh_token: str) -> bool:
        """Check if a session (refresh token) is revoked."""
        session = db.query(UserSession).filter(UserSession.refresh_token == refresh_token).first()
        if not session:
            return True
        if isinstance(session.expires_at, str):
            session.expires_at = datetime.fromisoformat(session.expires_at)

        session.expires_at = session.expires_at.astimezone(timezone.utc)
        current_time = datetime.now(timezone.utc)
        if session.is_revoked or (session.expires_at < current_time):
            return True
        return False

    def revoke_sessions(self, db: Session, sessions: List[UserSession]):
        """Revoke sessions associated with IP and user-agent."""
        try:
            for session in sessions:
                session.is_revoked = True
            db.commit()
            db.refresh(session)
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=400, detail="Could not revoke session(s)"
            )

    def fetch_by_ip_and_user_agent(self, db: Session, ip_address: str, user_agent: str) -> List[UserSession]:
        """Fetch sessions by IP address and user agent."""
        sessions = db.query(UserSession).filter(
            UserSession.ip_address == ip_address,
            UserSession.device == user_agent,
            UserSession.is_revoked == False
        ).all()
        return sessions
  
    def create(self, db: Session, schema: SessionCreate, user_id: str) -> UserSession:
        """Create a new session."""
        sessions = self.fetch_by_ip_and_user_agent(db, schema.ip_address, schema.device)
        if sessions:
            self.revoke_sessions(db, sessions)
        new_session = UserSession(**schema.model_dump(), user_id=user_id)
        db.add(new_session)
        db.commit()
        db.refresh(new_session)
        return new_session

    def fetch_all(self, db: Session, user_id: str) -> List[UserSession]:
        """Fetch all active sessions."""
        sessions = db.query(UserSession).filter(UserSession.is_revoked == False, UserSession.user_id == user_id).all()
        return sessions
    
    def fetch(self, db: Session, user_id: str, session_id: str) -> UserSession:
        """Fetch a session by its ID."""
        session = db.query(UserSession).filter(UserSession.id == session_id, UserSession.user_id == user_id).first()
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        return session
    
    def delete(self, db: Session, user_id: str, session_id: str):
        """Delete a session."""
        session = self.fetch(db, user_id, session_id)
        if not session:
            raise HTTPException(
                status_code=404, detail="Session not found"
            )
        self.revoke_sessions(db, [session])

    def delete_all(self, db: Session, user_id: str):
        """Revoke all sessions associated to a user"""
        sessions = self.fetch_all(db, user_id)
        self.revoke_sessions(db, sessions)


session_service = SessionService()