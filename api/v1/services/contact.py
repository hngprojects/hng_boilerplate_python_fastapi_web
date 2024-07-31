from api.db.database import get_db
from api.v1.models.contact_us import ContactUs
from fastapi import HTTPException, status


class ContactMessage(object):
    def __init__(self):
        pass

    @staticmethod
    def fetch_message(db, message_id):
        # result = ContactUs.get_by_id(message_id)
        result = db.query(ContactUs).filter_by(id=message_id).first()
        try:
            if message_id != result.id:
                return None
        except Exception as e:
            pass
        return result

    @staticmethod
    def check_admin_access(admin_id, message_id):
        pass


    @staticmethod
    def raise_unauthorized():
        raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token format",
                headers={"WWW-Authenticate": "Bearer"},
            )

    @staticmethod
    def raise_not_found():
        raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Message Not FOUND"
            )
