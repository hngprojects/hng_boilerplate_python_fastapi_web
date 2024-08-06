
#!/usr/bin/env python3

"""Teams services"""

from sqlalchemy.orm import Session

from api.core.base.services import Service
from api.v1.models.team import TeamMember

from api.core.base.services import Service
from api.utils.db_validators import check_model_existence
from api.v1.models.team import TeamMember


class TeamServices(Service):
    """Team services functionality"""

    @staticmethod
    def create(db: Session, schema) -> TeamMember:
        """Create a new job"""

        new_member = TeamMember(**schema.model_dump())
        db.add(new_member)
        db.commit()
        db.refresh(new_member)

        return new_member

    def create(self, db, data):
        """Create team"""
        pass

    def fetch_all(self, db, page, page_size):
        """Fetch all teams"""
        pass

    def fetch(self, db, id):
        """Fetch a single team"""
        team = check_model_existence(db, TeamMember, id)

        return team

    def update(self, db, id, data):
        """Update a team"""
        pass

    def delete(self, db, id):
        """Delete a team"""
        pass

    def delete_all(self, db):
        """Delete all teams"""
        pass


team_service = TeamServices()