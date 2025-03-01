from datetime import datetime, timezone
from sqlalchemy.orm import Session

from fastapi import HTTPException

from api.v1.schemas.session import SessionCreate
from api.v1.models.session import UserSession

class SessionService:
    """Session service functionality."""

    def __init__(self, db: Session):
        self.db = db

    def is_revoked_or_expired(self, refresh_token: str):
        """Check if a session (refresh token) is revoked."""
        session = self.db.query(UserSession).filter(UserSession.refresh_token == refresh_token).first()
        if not session:
            return True
        if isinstance(session.expires_at, str):
            session.expires_at = datetime.fromisoformat(session.expires_at)
        current_time = datetime.now(timezone.utc)
        if session.is_revoked or (session.expires_at < current_time):
            return True
        return False

    def revoke_sessions(self, sessions):
        """Revoke sessions associated with IP and user-agent."""
        try:
            for session in sessions:
                session.is_revoked = True
            self.db.commit()
            self.db.refresh(session)
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=400, detail="Could not update session"
            )

    def fetch_by_ip_and_user_agent(self, ip_address: str, user_agent: str):
        """Fetch sessions by IP address and user agent."""
        sessions = self.db.query(UserSession).filter(
            UserSession.ip_address == ip_address,
            UserSession.device == user_agent,
            UserSession.is_revoked == False
        ).all()
        return sessions
  
    def create(self, db: Session, schema: SessionCreate, user_id: str):
        """Create a new session."""
        sessions = self.fetch_by_ip_and_user_agent(schema.ip_address, schema.device)
        if sessions:
            print(sessions)
            self.revoke_sessions(sessions)
        new_session = UserSession(**schema.model_dump(), user_id=user_id)
        db.add(new_session)
        db.commit()
        db.refresh(new_session)
        return new_session

    def fetch_all(self, user_id):
        """Fetch all active sessions."""
        sessions = self.db.query(UserSession).filter(UserSession.is_revoked == False, UserSession.user_id == user_id).all()
        return sessions
    
    def fetch(self, user_id, session_id):
        """Fetch a session by its ID."""
        session = self.db.query(UserSession).filter(UserSession.id == session_id, UserSession.user_id == user_id).first()
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        return session
    
    def delete(self, user_id, session_id):
        """Delete a session."""
        session = self.fetch(user_id, session_id)
        if not session:
            raise HTTPException(
                status_code=404, detail="Session not found"
            )
        try:
            self.db.delete(session)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=500, detail="Could not delete session"
            )
        
    def delete_all(self, user_id):
        """Delete all sessions associated to a user"""
        sessions = self.fetch_all(user_id)
        try:
            for session in sessions:
                self.db.delete(session)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=500,
                detail="Could not delete sessions"
            )