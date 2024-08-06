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

    def update(self):
        pass

    def delete(self):
        pass


data_privacy_service = DataPrivacyService()
