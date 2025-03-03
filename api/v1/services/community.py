from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from api.utils.community_base_service import BaseService
from api.v1.models.community import CommunityQuestion, CommunityAnswer
from typing import Any
class CommunityQuestionService(BaseService):
    """Community Question service."""
    model = CommunityQuestion

    def create_question(self, db: Session, title: str, message: str, user_id: str) -> CommunityQuestion:
        """Creates a new community question."""
        try:
            question = CommunityQuestion(title=title, message=message, user_id=user_id)
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

    def mark_as_resolved(self, db: Session, question_id: str, is_resolved: bool = True) -> Any:
        """Mark a question as resolved or unresolved."""
        return self.update(db, question_id, {"is_resolved": is_resolved})


class CommunityAnswerService(BaseService):
    """Community Answer service."""
    model = CommunityAnswer

    def create_answer(self, db: Session, message: str, user_id: str, question_id: str) -> CommunityAnswer:
        """Creates a new answer to a community question."""
        question = db.query(CommunityQuestion).filter(CommunityQuestion.id == question_id).first()
        if not question:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Question with ID {question_id} not found"
            )
        try:
            answer = CommunityAnswer(message=message, user_id=user_id, question_id=question_id)
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

    def mark_as_accepted(self, db: Session, answer_id: str, is_accepted: bool = True) -> Any:
        """Mark an answer as accepted or not accepted."""
        answer = self.fetch_by_id(db, answer_id)
        try:
            if is_accepted:
                db.query(CommunityAnswer).filter(
                    CommunityAnswer.question_id == answer.question_id,
                    CommunityAnswer.is_accepted == True,
                    CommunityAnswer.id != answer_id
                ).update({"is_accepted": False})
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

# Create service instances
community_question_service = CommunityQuestionService()
community_answer_service = CommunityAnswerService()
