#!/usr/bin/env python3

"""Teams services"""


from api.core.base.services import Service
from api.utils.db_validators import check_model_existence
from api.v1.models.team import TeamMember


class TeamServices(Service):
    """Team services functionality"""

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
        team = check_model_existence(db, TeamMember, id)

        db.query(TeamMember).filter(TeamMember.id == id).update(data)
        db.commit()
        db.refresh(team)
        return team

    def delete(self, db, id):
        """Delete a team"""
        pass

    def delete_all(self, db):
        """Delete all teams"""
        pass


team_service = TeamServices()
