from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import routers
from app.api import admin, quiz, video, auth, workflow
from app.database import init_db

# Create FastAPI app
app = FastAPI(
    title="CrewAI Quiz System API",
    description="Backend API for automated quiz generation and student management",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_URL", "http://localhost:3000")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])
app.include_router(quiz.router, prefix="/api/quiz", tags=["Quiz"])
app.include_router(video.router, prefix="/api/video", tags=["Video"])
app.include_router(workflow.router, prefix="/api/workflow", tags=["Workflow"])

# Initialize database
@app.on_event("startup")
async def startup_event():
    try:
        db = init_db()
        if db is None:
            print("⚠️  Firebase not initialized. Some features may not work.")
        else:
            print("✅ Database initialized successfully")
    except Exception as e:
        print(f"⚠️  Database initialization failed: {e}")
        print("Server will start without database. Some features may not work.")

@app.get("/")
async def root():
    return {"message": "CrewAI Quiz System API", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "crewai-quiz-api"}

@app.get("/api/health")
async def api_health_check():
    return {"status": "healthy", "service": "crewai-quiz-api", "version": "1.0.0"}

@app.get("/api/test-groq")
async def test_groq():
    """Test Groq API connection"""
    try:
        from app.services.llm_service import LLMService
        llm_service = LLMService()
        
        print("🧪 Testing Groq API connection...")
        print(f"🔑 Groq API Key configured: {bool(llm_service.groq_api_key)}")
        
        # Test with a simple prompt
        response = await llm_service.generate_with_groq(
            "Generate 2 multiple choice questions about Python programming. Return in JSON format with questions array."
        )
        
        print(f"✅ Groq test successful, response length: {len(response)}")
        
        return {
            "success": True,
            "message": "Groq API is working!",
            "response": response,
            "response_length": len(response)
        }
    except Exception as e:
        print(f"❌ Groq test failed: {str(e)}")
        return {
            "success": False,
            "message": f"Groq API error: {str(e)}",
            "error": str(e)
        }

@app.post("/api/test-ai-questions")
async def test_ai_questions():
    """Test AI question generation and print to terminal"""
    try:
        from app.services.llm_service import LLMService
        llm_service = LLMService()
        
        print("🤖 Testing AI Question Generation...")
        print("=" * 50)
        
        # Generate questions using AI
        questions_data = await llm_service.generate_quiz_questions(
            topic="Python Programming",
            difficulty="medium",
            num_questions=3
        )
        
        questions = questions_data.get('questions', [])
        print(f"📝 Generated {len(questions)} AI questions:")
        print("=" * 50)
        
        for i, question in enumerate(questions, 1):
            print(f"\n🔢 Question {i}:")
            print(f"❓ {question.get('question_text', 'No question text')}")
            print("📋 Options:")
            for j, option in enumerate(question.get('options', []), 1):
                marker = "✅" if option == question.get('correct_answer') else "  "
                print(f"   {marker} {chr(64+j)}. {option}")
            print(f"💡 Explanation: {question.get('explanation', 'No explanation')}")
            print("-" * 30)
        
        print(f"\n✅ Successfully generated {len(questions)} AI questions!")
        print("=" * 50)
        
        return {
            "success": True,
            "message": f"Generated {len(questions)} AI questions",
            "questions": questions,
            "questions_count": len(questions)
        }
        
    except Exception as e:
        print(f"❌ AI question generation failed: {str(e)}")
        return {
            "success": False,
            "message": f"AI question generation error: {str(e)}",
            "error": str(e)
        }

@app.delete("/api/clear-all-quizzes")
async def clear_all_quizzes():
    """Clear all quizzes from database (for testing)"""
    try:
        from app.services.firebase_service import FirebaseService
        from app.database import get_db
        
        db = get_db()
        firebase_service = FirebaseService(db)
        
        success = await firebase_service.clear_all_quizzes()
        
        if success:
            return {
                "success": True,
                "message": "All quizzes cleared from database"
            }
        else:
            return {
                "success": False,
                "message": "Failed to clear quizzes"
            }
            
    except Exception as e:
        print(f"❌ Clear quizzes failed: {str(e)}")
        return {
            "success": False,
            "message": f"Error clearing quizzes: {str(e)}",
            "error": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
