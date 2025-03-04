from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from typing import Optional, Any, List, Dict
from api.utils.community_base_service import BaseService
from api.v1.models.community import CommunityQuestion, CommunityAnswer


class CommunityQuestionService(BaseService):
    """Community Question service"""
    def __init__(self,model) -> Any:
        super().__init__(model)

    def create_question(self, db: Session, title: str, message: str, user_id: str):
        """Creates a new community question"""
        try:
            question = CommunityQuestion(
                title=title,
                message=message,
                user_id=user_id
            )
            db.add(question)
            db.commit()
            db.refresh(question)
            return question
        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create question: {str(e)}"
            )

    def fetch_all(self, db: Session, **query_params: Optional[Any]):
        """Fetch all questions with option to search using query parameters"""
        return super().fetch_all(db, **query_params)
    
    def fetch_by_id(self, db: Session, question_id: str):
        """Fetch a question by its ID"""
        return super().fetch_by_id(db, question_id)
    
    def fetch_by_user_id(self, db: Session, user_id: str):
        """Fetch all questions by a specific user"""
        return db.query(CommunityQuestion).filter(CommunityQuestion.user_id == user_id).all()
    
    def update_question(self, db: Session, question_id: str, update_data: Dict[str, Any]):
        """Update a question with the provided data"""
        return super().update(db, question_id, update_data)
    
    def mark_as_resolved(self, db: Session, question_id: str, is_resolved: bool = True):
        """Mark a question as resolved or unresolved"""
        return self.update_question(db, question_id, {"is_resolved": is_resolved})
    
    def delete_question(self, db: Session, question_id: str):
        """Delete a question by its ID"""
        return super().delete(db, question_id)

class CommunityAnswerService:
    """Community Answer service"""
    def __init__(self,model):
        super().__init__(model)

    def create_answer(self, db: Session, message: str, user_id: str, question_id: str):
        """Creates a new answer to a community question"""
        # First verify the question exists
        question = db.query(CommunityQuestion).filter(CommunityQuestion.id == question_id).first()
        if not question:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Question with ID {question_id} not found"
            )
            
        try:
            answer = CommunityAnswer(
                message=message,
                user_id=user_id,
                question_id=question_id
            )
            db.add(answer)
            db.commit()
            db.refresh(answer)
            return answer
        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create answer: {str(e)}"
            )

    def fetch_all(self, db: Session, **query_params: Optional[Any]):
        """Fetch all answers with option to search using query parameters"""
        return super().fetch_all(db, **query_params)
    
    def fetch_by_id(self, db: Session, answer_id: str):
        """Fetch an answer by its ID"""
        return super().fetch_by_id(db, answer_id)
    
    def fetch_by_question_id(self, db: Session, question_id: str):
        """Fetch all answers for a specific question"""
        return db.query(CommunityAnswer).filter(CommunityAnswer.question_id == question_id).all()
    
    def fetch_by_user_id(self, db: Session, user_id: str):
        """Fetch all answers by a specific user"""
        return db.query(CommunityAnswer).filter(CommunityAnswer.user_id == user_id).all()
    
    def update_answer(self, db: Session, answer_id: str, update_data: Dict[str, Any]):
        """Update an answer with the provided data"""
        return super().update(db, answer_id, update_data)
    def mark_as_accepted(self, db: Session, answer_id: str, is_accepted: bool = True):
        """Mark an answer as accepted or not accepted"""
        answer = self.fetch_by_id(db, answer_id)
        
        try:
            # If marking as accepted, unmark any previously accepted answers for this question
            if is_accepted:
                previously_accepted = db.query(CommunityAnswer).filter(
                    CommunityAnswer.question_id == answer.question_id,
                    CommunityAnswer.is_accepted == True,
                    CommunityAnswer.id != answer_id
                ).all()
                
                for prev_answer in previously_accepted:
                    prev_answer.is_accepted = False
            
            # Mark the current answer
            answer.is_accepted = is_accepted
            db.commit()
            db.refresh(answer)
            return answer
        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update answer acceptance status: {str(e)}"
            )
    
    def delete_answer(self, db: Session, answer_id: str):
        """Delete an answer by its ID"""
        return super().delete(db, answer_id)

# Create service instances
community_question_service = CommunityQuestionService(CommunityQuestion)
community_answer_service = CommunityAnswerService(CommunityAnswer)