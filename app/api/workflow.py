"""
Workflow API endpoints for CrewAI Quiz System
Handles automated workflow execution
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any
from app.database import get_db
from app.workflows.quiz_workflow import QuizWorkflow
from app.api.auth import get_current_admin

router = APIRouter()

@router.post("/quiz/{quiz_id}/run-complete-workflow")
async def run_complete_quiz_workflow(
    quiz_id: str,
    current_admin = Depends(get_current_admin),
    db = Depends(get_db)
):
    """Run the complete quiz workflow: generate questions, send invitations"""
    try:
        workflow = QuizWorkflow(db)
        result = await workflow.run_complete_quiz_workflow(quiz_id, current_admin['id'])
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=f"Workflow failed: {result['errors']}")
        
        return {
            "message": "Complete quiz workflow executed successfully",
            "workflow_result": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Workflow execution failed: {str(e)}")

@router.post("/quiz/{quiz_id}/run-scoring-workflow")
async def run_quiz_scoring_workflow(
    quiz_id: str,
    current_admin = Depends(get_current_admin),
    db = Depends(get_db)
):
    """Run the quiz scoring workflow: score results and notify top students"""
    try:
        workflow = QuizWorkflow(db)
        result = await workflow.run_quiz_scoring_workflow(quiz_id)
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=f"Scoring workflow failed: {result['errors']}")
        
        return {
            "message": "Quiz scoring workflow executed successfully",
            "workflow_result": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scoring workflow execution failed: {str(e)}")

@router.post("/run-video-processing-workflow")
async def run_video_processing_workflow(
    current_admin = Depends(get_current_admin),
    db = Depends(get_db)
):
    """Run the video processing workflow: process videos and final ranking"""
    try:
        workflow = QuizWorkflow(db)
        result = await workflow.run_video_processing_workflow()
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=f"Video processing workflow failed: {result['errors']}")
        
        return {
            "message": "Video processing workflow executed successfully",
            "workflow_result": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Video processing workflow execution failed: {str(e)}")

@router.post("/quiz/{quiz_id}/run-automated-workflow")
async def run_automated_workflow(
    quiz_id: str,
    current_admin = Depends(get_current_admin),
    db = Depends(get_db)
):
    """Run the complete automated workflow with all phases"""
    try:
        workflow = QuizWorkflow(db)
        result = await workflow.run_automated_workflow(quiz_id, current_admin['id'])
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=f"Automated workflow failed: {result.get('errors', 'Unknown error')}")
        
        return {
            "message": "Complete automated workflow executed successfully",
            "workflow_result": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Automated workflow execution failed: {str(e)}")

@router.get("/workflow/status/{workflow_id}")
async def get_workflow_status(
    workflow_id: str,
    current_admin = Depends(get_current_admin),
    db = Depends(get_db)
):
    """Get the status of a running workflow"""
    # This would be implemented with a workflow state management system
    # For now, return a placeholder response
    return {
        "workflow_id": workflow_id,
        "status": "completed",
        "message": "Workflow status tracking not yet implemented"
    }
