from datetime import datetime, timedelta
from fastapi import Depends, status, HTTPException
from sqlalchemy.orm import Session
from fastapi import HTTPException, Depends, status
from jose import jwt, JWTError
from api.db.database import get_db
from api.v1.models import User, ResetPasswordToken, Organisation
from api.v1.models.associations import user_organisation_association
from api.v1.schemas.request_password_reset import (ResetPasswordRequest,
                                                   UserData,
                                                   OrganizationData,
                                                   ResetPasswordSuccesful)
from typing import Annotated, List
from api.utils.settings import settings
from api.core.base.services import Service
from api.v1.services.user import user_service


SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM


class RequestPasswordService(Service):
    def fetch(self, email: str, db: Annotated[Session, Depends(get_db)]):
        """
        Retrieve user by email.
       
        Args:
            email: the email of the user requesting for password reset
            db: database Session object
        Returns:
            user: The user object
        """
        user = db.query(User).filter_by(email=email).one_or_none()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="User not found")
        return user
   
    def create(self, user: User, db: Annotated[Session, Depends(get_db)]):
        """
        Creates an entry in the password reset token table for the user.
       
        Args:
            user: the user with the entry
            db: database Session object
        Returns:
            password_reset_token: password reset token
        """
        check_reset_token = db.query(ResetPasswordToken).filter_by(user_id=user.id).one_or_none()
        if check_reset_token:
            return self.generate_password_reset_token(user)
        reset_token = ResetPasswordToken(
            user_id=user.id,
            jti=user.id
        )
        db.add(reset_token)
        db.commit()
        return self.generate_password_reset_token(user)
   
    def generate_password_reset_token(self, user: User):
        """
        Creates Generates a password reset token for the user
       
        Args:
            user: the user with the entry
        Returns:
            password_reset_token: password reset token
        """
        now = datetime.utcnow()
        expire = now + timedelta(minutes=5)
        payload = {"email": user.email, "jti": user.id,
                   "iat": now, "exp": expire}
        return jwt.encode(claims=payload, key=SECRET_KEY, algorithm=ALGORITHM)


    def update(self, reset_password_data: ResetPasswordRequest,
               db: Annotated[Session, Depends(get_db)]):
        """
        Updates the user's password with the new password.
       
        Args:
            reset_password_data: the reset password data request object
            db: database Session object
        Returns:
            password_reset_response: password reset response for the user
        Raises:
            HTTPException: If anything goes wrong
        """
        payload = self.verify_reset_token(reset_password_data.reset_token)
        email = payload.get("email")
        jti = payload.get('jti')
        user_token: object = db.query(ResetPasswordToken).filter_by(jti=jti).one_or_none()
        if user_token:
            access_token = user_service.create_access_token(user_token.user_id)
            refresh_token = user_service.create_refresh_token(user_token.user_id)
           
            hashed_password = user_service.hash_password(reset_password_data.new_password)
            user = db.query(User).filter_by(id=user_token.user_id,
                                            email=email).one_or_none()
            if not user:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
            user.password = hashed_password
            db.commit()
           
            organizations = (db.query(Organisation)
                             .join(user_organisation_association,
                                   Organisation.id == user_organisation_association.c.organisation_id
                            ).filter(
                                user_organisation_association.c.user_id == user.id
                            ).all())
            self.delete(user_token, db)
            return self.get_reset_token_response(access_token,
                                                 user,
                                                 organizations), refresh_token
        else:
            raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                                detail="reset_token already used")
    def fetch_all(self):
        """
        Fetch all
        """
        pass
    def delete(self, user_token: ResetPasswordToken,
               db: Annotated[Session, Depends(get_db)]):
        """
        Delete the user's password_reset_token entry from the database.
       
        Args:
            user_token: the token object to delete
            db: database Session object
        Returns:
            None
        """
        db.delete(user_token)
        db.commit()
        return
   
    def get_reset_token_response(self, access_token: str,
                                 user: User,
                                 organization: Organisation):
        """
        Generates a response for the user
       
        Args:
            access_token: the token string to return
            user: user object
            organizations: the organizations of the user
        Returns:
            ResetPasswordSuccesful: the response for the user
        """
        organization_data: List[OrganizationData] = [OrganizationData.model_validate(
            org,
            from_attributes=True
        ) for org in organization]
        user_data = UserData.model_validate(
            user,
            from_attributes=True
        )
        return ResetPasswordSuccesful(
            message='password successfully reset',
            status_code=status.HTTP_201_CREATED,
            access_token=access_token,
            data={"user": user_data, "organisations": organization_data}
        )


    def verify_reset_token(self, reset_token: str):
        """
        Verifies the reset token.
       
        Args:
            reset_token: the token string to verify
        Returns:
            claims: the claims associated with the reset token
        """
        try:
            return jwt.decode(reset_token, SECRET_KEY, algorithms=[ALGORITHM])
        except JWTError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="reset token invalid")


reset_password_service = RequestPasswordService()
