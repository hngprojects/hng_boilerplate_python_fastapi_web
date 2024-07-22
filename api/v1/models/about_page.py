from uuid_extensions import uuid7
from api.v1.models.base_model import BaseModel
from api.v1.models.base import Base
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, String, JSON



class AboutPage(BaseModel, Base):
    """
    SQLAlchemy model representing the About page.

    Attributes:
        id (UUID): Unique identifier for the About page entry.
        title (str): The title of the About page.
        introduction (str): The introduction text for the About page.
        custom_sections (dict): A JSON object containing custom sections for the About page.
    """
    
    __tablename__ = 'about_page'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid7, unique=True, nullable=False)
    title = Column(String, nullable=False)
    introduction = Column(String, nullable=False)
    custom_sections = Column(JSON, nullable=False)