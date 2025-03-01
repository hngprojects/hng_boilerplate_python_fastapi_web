from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from api.v1.models.base_model import BaseTableModel

class CommunityQuestion(BaseTableModel):
    __tablename__ = "community_questions"
    
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    is_resolved = Column(Boolean, default=False)
    
    # Relationships
    user = relationship("User", back_populates="questions")
    answers = relationship("CommunityAnswer", back_populates="question", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<CommunityQuestion(id='{self.id}', title='{self.title}', user_id='{self.user_id}')>"


class CommunityAnswer(BaseTableModel):
    __tablename__ = "community_answers"
    
    message = Column(Text, nullable=False)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    question_id = Column(String, ForeignKey("community_questions.id", ondelete="CASCADE"), nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    is_accepted = Column(Boolean, default=False)
    
    # Relationships
    user = relationship("User", back_populates="answers")
    question = relationship("CommunityQuestion", back_populates="answers")
    
    def __repr__(self):
        return f"<CommunityAnswer(id='{self.id}', question_id='{self.question_id}', user_id='{self.user_id}')>"

