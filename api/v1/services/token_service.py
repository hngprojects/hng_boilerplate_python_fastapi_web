import secrets
import logging
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from api.v1.models.token import Token

logger = logging.getLogger(__name__)

class TokenService:
    def generate_token(self, db: Session) -> str:
        token = secrets.token_urlsafe(32)
        created_at = datetime.now(timezone.utc)
        db_token = Token(token=token, created_at=created_at, is_valid=True)
        db.add(db_token)
        db.commit()
        logger.info(f"Generated token: {token}")
        return token

    def validate_token(self, db: Session, token: str) -> bool:
        db_token = db.query(Token).filter(Token.token == token).first()
        if not db_token:
            logger.error(f"Token not found: {token}")
            return False

        expiration_time = timedelta(minutes=15)
        current_time = datetime.now(timezone.utc)
        logger.debug(f"Current time: {current_time}, Token created at: {db_token.created_at}")

        if (current_time - db_token.created_at) > expiration_time:
            logger.error(f"Token expired: {token}")
            return False

        if not db_token.is_valid:
            logger.error(f"Token invalidated: {token}")
            return False

        logger.info(f"Token validated: {token}")
        return True

    def invalidate_token(self, db: Session, token: str) -> None:
        db_token = db.query(Token).filter(Token.token == token).first()
        if db_token:
            db_token.is_valid = False
            db.commit()
            logger.info(f"Token invalidated: {token}")
