"""
Simple Quiz API - Streamlined endpoint for quiz generation
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any
from pydantic import BaseModel

from app.database import get_db
from app.utils.streamlined_quiz_generator import get_quiz_generator

router = APIRouter()

class QuizRequest(BaseModel):
    topic: str
    difficulty: str = "medium"
    num_questions: int = 5

class QuizResponse(BaseModel):
    success: bool
    message: str
    questions: list = []
    system_used: str = ""

@router.post("/generate", response_model=QuizResponse)
async def generate_quiz(
    request: QuizRequest,
    db = Depends(get_db)
):
    """
    Generate quiz questions - Simple and efficient endpoint
    """
    try:
        print(f"🎯 API: Generating quiz for topic: {request.topic}")
        
        # Get quiz generator
        generator = get_quiz_generator(db)
        
        # Generate quiz
        result = await generator.generate_quiz(
            topic=request.topic,
            difficulty=request.difficulty,
            num_questions=request.num_questions
        )
        
        if result.get("success"):
            return QuizResponse(
                success=True,
                message=result.get("message", "Quiz generated successfully"),
                questions=result.get("questions", []),
                system_used=result.get("system_used", "Streamlined CrewAI")
            )
        else:
            raise HTTPException(
                status_code=400,
                detail=result.get("message", "Quiz generation failed")
            )
            
    except Exception as e:
        print(f"❌ API Error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "simple-quiz-api",
        "version": "1.0.0"
    }
