#!/usr/bin/env python3

"""Teams services"""

from sqlalchemy.orm import Session

from api.core.base.services import Service
from api.v1.models.team import TeamMember

from api.utils.db_validators import check_model_existence


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

    def fetch_all(self, db: Session):
        """Fetch all team members"""
        team_members = db.query(TeamMember).all()
        return team_members

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
        check_model_existence(db, TeamMember, id)

        db.query(TeamMember).filter(TeamMember.id == id).delete()
        db.commit()
        return None

    def delete_all(self, db):
        """Delete all teams"""
        pass


team_service = TeamServices()
