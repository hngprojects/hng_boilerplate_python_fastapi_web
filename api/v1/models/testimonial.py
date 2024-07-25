from sqlalchemy import Column, String, ForeignKey, Text, Integer, DateTime, Float
from sqlalchemy.orm import relationship
from api.v1.models.base_model import BaseTableModel

class Testimonial(BaseTableModel):
    __tablename__ = "testimonials"

    client_designation = Column(String, nullable=True)
    client_name = Column(String, nullable=True)
    author_id = Column(String, ForeignKey('users.id', ondelete="CASCADE"), nullable=False)
    comments = Column(Text, nullable=True)
    content = Column(Text, nullable=False)
    ratings = Column(Float, nullable=True)

    author = relationship("User", back_populates="testimonials")