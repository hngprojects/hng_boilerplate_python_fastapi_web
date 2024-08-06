from sqlalchemy import Column, String, Text
from api.v1.models.base_model import BaseTableModel


class TeamMember(BaseTableModel):
    __tablename__ = "team_members"

    name = Column(String, nullable=False)
    role = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    picture_url = Column(String, nullable=False)
    team_type = Column(String, nullable=True)  # e.g Executive team, Development team
    facebook_link = Column(String, nullable=True) 
    instagram_link = Column(String, nullable=True) 
    xtwitter_link = Column(String, nullable=True) 
