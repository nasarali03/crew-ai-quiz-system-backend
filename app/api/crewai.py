"""
CrewAI API endpoints for processing user queries
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, Optional
from pydantic import BaseModel

from app.database import get_db
from app.agents.crewai_quiz_system import CrewAIQuizSystem

router = APIRouter()

class UserQueryRequest(BaseModel):
    query: str
    context: Optional[Dict[str, Any]] = None

class UserQueryResponse(BaseModel):
    success: bool
    message: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

@router.post("/process-query", response_model=UserQueryResponse)
async def process_user_query(
    request: UserQueryRequest,
    db = Depends(get_db)
):
    """
    Process user query using CrewAI system
    """
    try:
        print(f"🎯 CrewAI API: Processing user query: {request.query}")
        
        # Initialize CrewAI system
        crewai_system = CrewAIQuizSystem(db)
        
        # Process the query
        result = await crewai_system.process_user_query(
            user_query=request.query,
            context=request.context
        )
        
        if result.get("success"):
            return UserQueryResponse(
                success=True,
                message=result.get("message", "Query processed successfully"),
                result=result
            )
        else:
            return UserQueryResponse(
                success=False,
                message=result.get("message", "Query processing failed"),
                error=result.get("error")
            )
            
    except Exception as e:
        print(f"❌ CrewAI API: Error processing query: {str(e)}")
        return UserQueryResponse(
            success=False,
            message=f"Error processing query: {str(e)}",
            error=str(e)
        )

@router.post("/generate-quiz", response_model=UserQueryResponse)
async def generate_quiz_from_query(
    request: UserQueryRequest,
    db = Depends(get_db)
):
    """
    Generate quiz from user query using CrewAI system
    """
    try:
        print(f"🎓 CrewAI API: Generating quiz from query: {request.query}")
        
        # Initialize CrewAI system
        crewai_system = CrewAIQuizSystem(db)
        
        # Process the query for quiz generation
        result = await crewai_system.process_user_query(
            user_query=request.query,
            context=request.context
        )
        
        if result.get("success"):
            return UserQueryResponse(
                success=True,
                message=result.get("message", "Quiz generated successfully"),
                result=result
            )
        else:
            return UserQueryResponse(
                success=False,
                message=result.get("message", "Quiz generation failed"),
                error=result.get("error")
            )
            
    except Exception as e:
        print(f"❌ CrewAI API: Error generating quiz: {str(e)}")
        return UserQueryResponse(
            success=False,
            message=f"Error generating quiz: {str(e)}",
            error=str(e)
        )

@router.get("/test-system")
async def test_crewai_system(db = Depends(get_db)):
    """
    Test the CrewAI system with a sample query
    """
    try:
        print("🧪 Testing CrewAI system...")
        
        # Initialize CrewAI system
        crewai_system = CrewAIQuizSystem(db)
        
        # Test with a sample query
        test_query = "Create a medium difficulty quiz about Python programming with 5 questions"
        
        result = await crewai_system.process_user_query(
            user_query=test_query,
            context={"test": True}
        )
        
        return {
            "success": True,
            "message": "CrewAI system test completed",
            "test_query": test_query,
            "result": result
        }
        
    except Exception as e:
        print(f"❌ CrewAI system test failed: {str(e)}")
        return {
            "success": False,
            "message": f"CrewAI system test failed: {str(e)}",
            "error": str(e)
        }
