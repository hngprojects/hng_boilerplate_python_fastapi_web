from typing import Any, Optional
from sqlalchemy.orm import Session
from api.core.base.services import Service
from api.v1.models.user import User
from api.v1.models.data_privacy import DataPrivacySetting
from api.utils.db_validators import check_model_existence


class DataPrivacyService(Service):
    """Data Privacy Services"""

    def create(self, user: User, db: Session):
        # create data privacy setting

        data_privacy = DataPrivacySetting(user_id=user.id)

        db.add(data_privacy)
        db.commit()
        db.refresh(data_privacy)

    def fetch_all(self):
        pass

    def fetch(self, db: Session, user: User):
        # * for users create before this update

        if not user.data_privacy_setting:
            self.create(user, db)

        return user.data_privacy_setting

    def update(self, db: Session, user: User, schema):
        """Updates the user privacy settings"""

        data_privacy_setting = self.fetch(db=db, user=user)

        # Update the fields with the provided schema data
        update_data = schema.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(data_privacy_setting, key, value)

        db.commit()
        db.refresh(data_privacy_setting)
        return data_privacy_setting

    def delete(self):
        pass


data_privacy_service = DataPrivacyService()
