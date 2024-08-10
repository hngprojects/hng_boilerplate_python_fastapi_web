from api.db.database import get_db
from api.v1.models.contact_us import ContactUs
from fastapi import HTTPException, status
from api.v1.models.associations import user_organisation_association
from api.v1.services.organisation import OrganisationService


class ContactMessage(object):
    def __init__(self):
        pass

    def fetch_message(self, db, message_id):
        # result = ContactUs.get_by_id(message_id)
        result = db.query(ContactUs).filter_by(id=message_id).first()
        if not result:
            raise self.raise_not_found()
        return result

    def check_admin_access(self, db, admin_id, org_id):
        org_service_obj = OrganisationService()
        role = org_service_obj.get_organisation_user_role(user_id=admin_id, org_id=org_id, db=db)
        if role != 'admin':
            self.raise_unauthorized_admin()

    @staticmethod
    def raise_unauthorized():
        raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token format",
                headers={"WWW-Authenticate": "Bearer"},
            )

    @staticmethod
    def raise_unauthorized_admin():
        raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Admin is unauthorized",
            )

    @staticmethod
    def raise_not_found():
        raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Message Not FOUND"
            )
