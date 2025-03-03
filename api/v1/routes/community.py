from fastapi import APIRouter, Depends, status, HTTPException, Query
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from typing import Optional, List

from api.v1.models.user import User
from api.v1.schemas.community import (
    CommunityQuestionCreate, 
    CommunityQuestionResponse, 
    CommunityAnswerCreate, 
    CommunityAnswerResponse,
    CommunityQuestionWithAnswers
)
from api.v1.services.community import community_question_service, community_answer_service
from api.v1.services.user import user_service
from api.db.database import get_db
from api.utils.success_response import success_response

# Router for Questions
community_questions = APIRouter(prefix="/community/questions", tags=["Community Questions"])

@community_questions.post("/create", status_code=status.HTTP_201_CREATED)
async def create_question(
    question: CommunityQuestionCreate, 
    current_user: User = Depends(user_service.get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new community question"""
    
    new_question = community_question_service.create_question(
        db=db,
        title=question.title,
        message=question.message,
        user_id=current_user.id  # Use the authenticated user's ID
    )
    
    return success_response(
        status_code=201,
        message="Question created successfully",
        data=jsonable_encoder(new_question)
    )

@community_questions.get("", response_model=List[CommunityQuestionResponse])
async def get_all_questions(
    title: Optional[str] = Query(None, description="Filter by title"),
    is_resolved: Optional[bool] = Query(None, description="Filter by resolution status"),
    db: Session = Depends(get_db)
):
    """Get all community questions with optional filters"""
    
    query_params = {}
    if title:
        query_params["title"] = title
    if is_resolved is not None:
        query_params["is_resolved"] = is_resolved
        
    questions = community_question_service.fetch_all(db=db, **query_params)
    
    return success_response(
        status_code=200,
        message="Questions retrieved successfully",
        data=jsonable_encoder(questions)
    )

@community_questions.get("/{question_id}", response_model=CommunityQuestionWithAnswers)
async def get_question_with_answers(
    question_id: str,
    db: Session = Depends(get_db)
):
    """Get a specific question with all its answers"""
    
    question = community_question_service.fetch_by_id(db=db, question_id=question_id)

    if question is None:
        raise HTTPException(
            status_code=404,
            detail=f"Question with ID {question_id} not found"
        )

    answers = community_answer_service.fetch_by_question_id(db=db, question_id=question_id)
    
    question_data = jsonable_encoder(question)
    question_data["answers"] = jsonable_encoder(answers)
    question_data["answer_count"] = len(answers)
    
    return success_response(
        status_code=200,
        message="Question and answers retrieved successfully",
        data=question_data
    )


@community_questions.get("/user/{user_id}", response_model=List[CommunityQuestionResponse])
async def get_user_questions(
    user_id: str,
    current_user: User = Depends(user_service.get_current_user),
    db: Session = Depends(get_db)
):
    """Get all questions asked by a specific user"""
    
    # Check if user is requesting their own questions or is an admin
    if current_user.id != user_id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own questions unless you're an admin"
        )
    
    questions = community_question_service.fetch_by_user_id(db=db, user_id=user_id)
    
    return success_response(
        status_code=200,
        message=f"Questions for user {user_id} retrieved successfully",
        data=jsonable_encoder(questions)
    )

@community_questions.put("/{question_id}", response_model=CommunityQuestionResponse)
async def update_question(
    question_id: str,
    question_update: CommunityQuestionCreate,
    current_user: User = Depends(user_service.get_current_user),
    db: Session = Depends(get_db)
):
    """Update a specific question"""
    
    # Fetch the question first to check ownership
    existing_question = community_question_service.fetch_by_id(db=db, question_id=question_id)
    
    if existing_question is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Question with ID {question_id} not found"
        )
    
    # Check if user is the owner or an admin
    if existing_question.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own questions"
        )
    
    update_data = {
        "title": question_update.title,
        "message": question_update.message
    }
    
    updated_question = community_question_service.update(
        db=db, 
        id=question_id, 
        data=update_data
    )
    
    return success_response(
        status_code=200,
        message="Question updated successfully",
        data=jsonable_encoder(updated_question)
    )

@community_questions.patch("/{question_id}/resolve", response_model=CommunityQuestionResponse)
async def mark_question_resolved(
    question_id: str,
    is_resolved: bool = True,
    current_user: User = Depends(user_service.get_current_user),
    db: Session = Depends(get_db)
):
    """Mark a question as resolved or unresolved"""
    
    # Fetch the question first to check ownership
    existing_question = community_question_service.fetch_by_id(db=db, question_id=question_id)
    
    if existing_question is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Question with ID {question_id} not found"
        )
    
    # Check if user is the owner or an admin
    if existing_question.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only mark your own questions as resolved"
        )
    
    updated_question = community_question_service.mark_as_resolved(
        db=db, 
        question_id=question_id, 
        is_resolved=is_resolved
    )
    
    return success_response(
        status_code=200,
        message=f"Question marked as {'resolved' if is_resolved else 'unresolved'} successfully",
        data=jsonable_encoder(updated_question)
    )

@community_questions.delete("/{question_id}", status_code=status.HTTP_200_OK)
async def delete_question(
    question_id: str,
    current_user: User = Depends(user_service.get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a specific question"""
    
    # Fetch the question first to check ownership
    existing_question = community_question_service.fetch_by_id(db=db, question_id=question_id)
    
    if existing_question is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Question with ID {question_id} not found"
        )
    
    # Check if user is the owner or an admin
    if existing_question.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own questions"
        )
    
    # Using the delete method from BaseService
    community_question_service.delete(db=db, id=question_id)
    
    return success_response(
        status_code=200,
        message="Question deleted successfully"
    )

# Router for Answers
community_answers = APIRouter(prefix="/community/answers", tags=["Community Answers"])

@community_answers.post("/create", status_code=status.HTTP_201_CREATED)
async def create_answer(
    answer: CommunityAnswerCreate,
    current_user: User = Depends(user_service.get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new answer to a community question"""
    
    new_answer = community_answer_service.create_answer(
        db=db,
        message=answer.message,
        user_id=current_user.id,  # Use the authenticated user's ID
        question_id=answer.question_id
    )
    
    return success_response(
        status_code=201,
        message="Answer created successfully",
        data=jsonable_encoder(new_answer)
    )

@community_answers.get("/question/{question_id}", response_model=List[CommunityAnswerResponse])
async def get_question_answers(
    question_id: str,
    db: Session = Depends(get_db)
):
    """Get all answers for a specific question"""
    
    # First check if question exists
    question = community_question_service.fetch_by_id(db=db, question_id=question_id)
    if question is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Question with ID {question_id} not found"
        )
    
    answers = community_answer_service.fetch_by_question_id(db=db, question_id=question_id)
    
    return success_response(
        status_code=200,
        message="Answers retrieved successfully",
        data=jsonable_encoder(answers)
    )

@community_answers.get("/user/{user_id}", response_model=List[CommunityAnswerResponse])
async def get_user_answers(
    user_id: str,
    current_user: User = Depends(user_service.get_current_user),
    db: Session = Depends(get_db)
):
    """Get all answers provided by a specific user"""
    
    # Check if user is requesting their own answers or is an admin
    if current_user.id != user_id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own answers unless you're an admin"
        )
    
    answers = community_answer_service.fetch_by_user_id(db=db, user_id=user_id)
    
    return success_response(
        status_code=200,
        message=f"Answers for user {user_id} retrieved successfully",
        data=jsonable_encoder(answers)
    )

@community_answers.put("/{answer_id}", response_model=CommunityAnswerResponse)
async def update_answer(
    answer_id: str,
    answer_update: CommunityAnswerCreate,
    current_user: User = Depends(user_service.get_current_user),
    db: Session = Depends(get_db)
):
    """Update a specific answer"""
    
    # Fetch the answer first to check ownership
    existing_answer = community_answer_service.fetch_by_id(db=db, answer_id=answer_id)
    
    if existing_answer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Answer with ID {answer_id} not found"
        )
    
    # Check if user is the owner or an admin
    if existing_answer.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own answers"
        )
    
    update_data = {
        "message": answer_update.message
    }
    
    updated_answer = community_answer_service.update(
        db=db, 
        id=answer_id, 
        data=update_data
    )
    
    return success_response(
        status_code=200,
        message="Answer updated successfully",
        data=jsonable_encoder(updated_answer)
    )

@community_answers.patch("/{answer_id}/accept", response_model=CommunityAnswerResponse)
async def mark_answer_accepted(
    answer_id: str,
    is_accepted: bool = True,
    current_user: User = Depends(user_service.get_current_user),
    db: Session = Depends(get_db)
):
    """Mark an answer as accepted or not accepted"""
    
    # Fetch the answer
    answer = community_answer_service.fetch_by_id(db=db, answer_id=answer_id)
    
    if answer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Answer with ID {answer_id} not found"
        )
    
    # Fetch the question to check ownership
    question = community_question_service.fetch_by_id(db=db, question_id=answer.question_id)
    
    if question is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Question with ID {answer.question_id} not found"
        )
    
    # Only the question owner or an admin can mark an answer as accepted
    if question.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the question owner can mark an answer as accepted"
        )
    
    updated_answer = community_answer_service.mark_as_accepted(
        db=db, 
        answer_id=answer_id, 
        is_accepted=is_accepted
    )
    
    return success_response(
        status_code=200,
        message=f"Answer marked as {'accepted' if is_accepted else 'not accepted'} successfully",
        data=jsonable_encoder(updated_answer)
    )

@community_answers.delete("/{answer_id}", status_code=status.HTTP_200_OK)
async def delete_answer(
    answer_id: str,
    current_user: User = Depends(user_service.get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a specific answer"""
    
    # Fetch the answer first to check ownership
    existing_answer = community_answer_service.fetch_by_id(db=db, answer_id=answer_id)
    
    if existing_answer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Answer with ID {answer_id} not found"
        )
    
    # Check if user is the owner or an admin
    if existing_answer.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own answers"
        )
    
    # Using the delete method from BaseService
    community_answer_service.delete(db=db, id=answer_id)
    
    return success_response(
        status_code=200,
        message="Answer deleted successfully"
    )