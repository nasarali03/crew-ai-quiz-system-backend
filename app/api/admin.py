from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from typing import List
import pandas as pd
import io

from app.database import get_db
from app.models.schemas import (
    StudentCreate, StudentResponse, QuizCreate, QuizResponse, 
    ExcelUploadResponse, QuizResultResponse
)
from app.services.admin_service import AdminService
# from app.api.auth import get_current_admin  # Temporarily disabled for testing

router = APIRouter()

@router.post("/upload-students", response_model=ExcelUploadResponse)
async def upload_students(
    file: UploadFile = File(...),
    db = Depends(get_db)
):
    """Upload Excel file with student list"""
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="File must be an Excel file")
    
    try:
        # Read Excel file
        contents = await file.read()
        df = pd.read_excel(io.BytesIO(contents))
        
        # Validate required columns
        required_columns = ['name', 'email']
        if not all(col in df.columns for col in required_columns):
            raise HTTPException(
                status_code=400, 
                detail=f"Excel file must contain columns: {required_columns}"
            )
        
        # Check for optional columns and add them if missing
        optional_columns = ['student_id', 'data']
        for col in optional_columns:
            if col not in df.columns:
                df[col] = None
        
        admin_service = AdminService(db)
        # Use a default admin ID for testing (you can change this)
        result = await admin_service.import_students(df, "default-admin-id")
        
        return ExcelUploadResponse(
            message=f"Successfully imported {result['imported_count']} students",
            students_imported=result['imported_count'],
            students=result['students']
        )
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing file: {str(e)}")

@router.get("/students", response_model=List[StudentResponse])
async def get_students(
    db = Depends(get_db)
):
    """Get all students"""
    admin_service = AdminService(db)
    return await admin_service.get_all_students()

@router.post("/create-quiz", response_model=QuizResponse)
async def create_quiz(
    quiz_data: QuizCreate,
    db = Depends(get_db)
):
    """Create a new quiz with settings"""
    
    # Display user query from create quiz form in terminal
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    print("=" * 80)
    print("🎯 QUIZ CREATION REQUEST RECEIVED")
    print(f"⏰ Timestamp: {timestamp}")
    print("=" * 80)
    print(f"📝 Quiz Title: {quiz_data.title}")
    print(f"📄 Description: {quiz_data.description}")
    print(f"🎯 Topic: {quiz_data.topic}")
    print(f"⚡ Difficulty: {quiz_data.difficulty}")
    print(f"⏱️  Time per Question: {quiz_data.time_per_question} seconds")
    print(f"❓ Question Type: {quiz_data.question_type}")
    print(f"🔢 Total Questions: {quiz_data.total_questions}")
    print("=" * 80)
    print("🚀 Processing quiz creation...")
    print("=" * 80)
    
    admin_service = AdminService(db)
    result = await admin_service.create_quiz(quiz_data, "default-admin-id")
    
    print(f"✅ Quiz created successfully with ID: {result.id}")
    print(f"📊 Final Quiz Response:")
    print(f"   - ID: {result.id}")
    print(f"   - Title: {result.title}")
    print(f"   - Topic: {result.topic}")
    print(f"   - Difficulty: {result.difficulty}")
    print(f"   - Total Questions: {result.total_questions}")
    print(f"   - Time per Question: {result.time_per_question}s")
    print(f"   - Question Type: {result.question_type}")
    print(f"   - Is Active: {result.is_active}")
    print(f"   - Created At: {result.created_at}")
    print("=" * 80)
    print("🎉 QUIZ CREATION COMPLETED SUCCESSFULLY!")
    print("=" * 80)
    
    return result
  
@router.get("/quizzes", response_model=List[QuizResponse])
async def get_quizzes(
    db = Depends(get_db)
):
    """Get all quizzes created by admin"""
    admin_service = AdminService(db)
    return await admin_service.get_admin_quizzes("default-admin-id")

@router.get("/quiz/{quiz_id}/results", response_model=List[QuizResultResponse])
async def get_quiz_results(
    quiz_id: str,
    db = Depends(get_db)
):
    """Get quiz results and rankings"""
    admin_service = AdminService(db)
    return await admin_service.get_quiz_results(quiz_id, "default-admin-id")

@router.get("/results")
async def get_all_results(
    db = Depends(get_db)
):
    """Get all quiz results across all quizzes"""
    admin_service = AdminService(db)
    return await admin_service.get_all_quiz_results("default-admin-id")
 
@router.post("/quiz/{quiz_id}/generate-questions")
async def generate_quiz_questions(
    quiz_id: str,
    db = Depends(get_db)
):
    """Trigger QuizGenerator agent to create questions"""
    
    print("=" * 80)
    print("🎯 QUIZ QUESTION GENERATION REQUEST")
    print(f"📊 Quiz ID: {quiz_id}")
    print("=" * 80)
    
    admin_service = AdminService(db)
    result = await admin_service.generate_quiz_questions(quiz_id, "default-admin-id")
    
    if result.get("success"):
        print(f"✅ Question generation completed successfully!")
        print(f"📊 Questions generated: {result.get('questions_count', 0)}")
    else:
        print(f"❌ Question generation failed!")
        print(f"🚫 Error: {result.get('message', 'Unknown error')}")
        print("🚫 NO QUESTIONS SAVED TO DATABASE")
    
    print("=" * 80)
    
    return result

@router.post("/quiz/{quiz_id}/send-invitations")
async def send_quiz_invitations(
    quiz_id: str,
    db = Depends(get_db)
):
    """Trigger SendInvitations agent to email students"""
    admin_service = AdminService(db)
    return await admin_service.send_quiz_invitations(quiz_id, "default-admin-id")

@router.get("/invitations")
async def get_invitations(
    db = Depends(get_db)
):
    """Get all quiz invitations with student and quiz details"""
    admin_service = AdminService(db)
    return await admin_service.get_all_invitations("default-admin-id")

@router.get("/quiz/{quiz_id}/invitations")
async def get_quiz_invitations(
    quiz_id: str,
    db = Depends(get_db)
):
    """Get invitations for a specific quiz"""
    admin_service = AdminService(db)
    return await admin_service.get_invitations_by_quiz(quiz_id, "default-admin-id")

@router.put("/invitations/{invitation_id}/mark-used")
async def mark_invitation_as_used(
    invitation_id: str,
    db = Depends(get_db)
):
    """Mark an invitation as used"""
    admin_service = AdminService(db)
    success = await admin_service.mark_invitation_as_used(invitation_id, "default-admin-id")
    if success:
        return {"message": "Invitation marked as used"}
    else:
        raise HTTPException(status_code=400, detail="Failed to mark invitation as used")

@router.post("/invitations/{invitation_id}/resend")
async def resend_invitation(
    invitation_id: str,
    db = Depends(get_db)
):
    """Resend an invitation"""
    admin_service = AdminService(db)
    success = await admin_service.resend_invitation(invitation_id, "default-admin-id")
    if success:
        return {"message": "Invitation resent successfully"}
    else:
        raise HTTPException(status_code=400, detail="Failed to resend invitation")

@router.get("/quiz/{quiz_id}/export-results")
async def export_quiz_results(
    quiz_id: str,
    db = Depends(get_db)
):
    """Export quiz results to Excel format"""
    admin_service = AdminService(db)
    return await admin_service.export_quiz_results(quiz_id, "default-admin-id")

@router.get("/quizzes/{quiz_id}")
async def get_quiz(
    quiz_id: str,
    db = Depends(get_db)
):
    """Get a specific quiz by ID"""
    admin_service = AdminService(db)
    return await admin_service.get_quiz_by_id(quiz_id)

@router.put("/quizzes/{quiz_id}")
async def update_quiz(
    quiz_id: str,
    quiz_data: QuizCreate,
    db = Depends(get_db)
):
    """Update a quiz"""
    admin_service = AdminService(db)
    return await admin_service.update_quiz(quiz_id, quiz_data, "default-admin-id")

@router.get("/quiz/{quiz_id}/questions")
async def get_quiz_questions(
    quiz_id: str,
    db = Depends(get_db)
):
    """Get quiz questions for admin view (with correct answers)"""
    try:
        print(f"🔍 API: Getting questions for quiz {quiz_id}")
        admin_service = AdminService(db)
        questions = await admin_service.get_quiz_questions(quiz_id, "default-admin-id")
        
        if not questions:
            print(f"⚠️ API: No questions found for quiz {quiz_id}")
            return []
        
        print(f"✅ API: Returning {len(questions)} questions for quiz {quiz_id}")
        return questions
        
    except Exception as e:
        print(f"❌ API: Error getting questions for quiz {quiz_id}: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to get quiz questions: {str(e)}")

