from sqlalchemy.orm import Session

from api.core.base.services import Service
from api.v1.models.team import TeamMember


class TeamMemberService(Service):
    """Team service functionality"""
    @staticmethod
    def create(db: Session, schema) -> TeamMember:
        """Create a new job"""

        new_member = TeamMember(**schema.model_dump())
        db.add(new_member)
        db.commit()
        db.refresh(new_member)

        return new_member