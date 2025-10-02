from fastapi import APIRouter, Depends, HTTPException
from typing import List

from app.database import get_db
from app.models.schemas import (
    QuizResponse, QuestionResponse, QuizSubmission, 
    QuizAnswerResponse, QuizResultResponse
)
from app.services.quiz_service import QuizService

router = APIRouter()

@router.get("/{token}", response_model=QuizResponse)
async def get_quiz_by_token(
    token: str,
    db = Depends(get_db)
):
    """Get quiz details by invitation token"""
    quiz_service = QuizService(db)
    quiz = await quiz_service.get_quiz_by_token(token)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found or token invalid")
    return quiz

@router.get("/{token}/questions", response_model=List[QuestionResponse])
async def get_quiz_questions(
    token: str,
    db = Depends(get_db)
):
    """Get quiz questions for student (without correct answers)"""
    quiz_service = QuizService(db)
    questions = await quiz_service.get_quiz_questions_by_token(token)
    if not questions:
        raise HTTPException(status_code=404, detail="Quiz questions not found")
    return questions

@router.post("/{token}/submit", response_model=QuizResultResponse)
async def submit_quiz_answers(
    token: str,
    submission: QuizSubmission,
    db = Depends(get_db)
):
    """Submit quiz answers and get results"""
    quiz_service = QuizService(db)
    result = await quiz_service.submit_quiz_answers(token, submission)
    if not result:
        raise HTTPException(status_code=400, detail="Invalid submission or quiz not found")
    return result

@router.get("/{token}/status")
async def get_quiz_status(
    token: str,
    db = Depends(get_db)
):
    """Check if quiz is accessible and get basic info"""
    quiz_service = QuizService(db)
    status = await quiz_service.get_quiz_status(token)
    if not status:
        raise HTTPException(status_code=404, detail="Quiz not found or token invalid")
    return status

@router.get("/debug/invitations")
async def debug_invitations(db = Depends(get_db)):
    """Debug endpoint to check all invitations in database"""
    from app.services.firebase_service import FirebaseService
    firebase_service = FirebaseService(db)
    
    try:
        # Get all invitations
        invitations = []
        for doc in firebase_service.db.collection('quiz_invitations').limit(10).stream():
            invitation_data = doc.to_dict()
            invitation_data['id'] = doc.id
            # Only show first 10 chars of token for security
            invitation_data['token_preview'] = invitation_data.get('token', '')[:10] + '...'
            invitation_data.pop('token', None)  # Remove full token
            invitations.append(invitation_data)
        
        return {
            "total_invitations": len(invitations),
            "invitations": invitations
        }
    except Exception as e:
        return {"error": str(e)}