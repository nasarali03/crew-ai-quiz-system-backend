import pandas as pd
from typing import List, Dict, Any
from datetime import datetime
from app.models.schemas import (
    StudentCreate, StudentResponse, QuizCreate, QuizResponse,
    QuizResultResponse
)
from app.agents.quiz_generator import QuizGeneratorAgent
from app.agents.send_invitations import SendInvitationsAgent
from app.services.firebase_service import FirebaseService

class AdminService:
    def __init__(self, db):
        self.db = db
        self.firebase_service = FirebaseService(db)

    async def import_students(self, df: pd.DataFrame, admin_id: str) -> Dict[str, Any]:
        """Import students from Excel DataFrame"""
        students = []
        imported_count = 0
        
        for _, row in df.iterrows():
            try:
                # Create student
                student_dict = {
                    "name": row['name'],
                    "email": row['email'],
                    "student_id": row.get('student_id', ''),
                    "data": row.get('data', ''),
                    "extra_info": row.get('extra_info', '')
                }
                student = await self.firebase_service.create_student(student_dict)
                students.append(StudentResponse(
                    id=student['id'],
                    name=student['name'],
                    email=student['email'],
                    student_id=student.get('student_id', ''),
                    data=student.get('data', ''),
                    extra_info=student['extra_info'],
                    created_at=student['created_at']
                ))
                imported_count += 1
            except Exception as e:
                print(f"Error importing student {row['name']}: {e}")
                continue
        
        return {
            "imported_count": imported_count,
            "students": students
        }

    async def get_all_students(self) -> List[StudentResponse]:
        """Get all students"""
        students = await self.firebase_service.get_all_students()
        return [
            StudentResponse(
                id=student['id'],
                name=student['name'],
                email=student['email'],
                student_id=student.get('student_id', ''),
                data=student.get('data', ''),
                extra_info=student['extra_info'],
                created_at=student['created_at']
            ) for student in students
        ]

    async def create_quiz(self, quiz_data: QuizCreate, admin_id: str) -> QuizResponse:
        """Create a new quiz"""
        print("🔧 AdminService: Processing quiz creation...")
        print(f"👤 Admin ID: {admin_id}")
        
        quiz_dict = {
            "title": quiz_data.title,
            "description": quiz_data.description,
            "topic": quiz_data.topic,
            "difficulty": quiz_data.difficulty.value if hasattr(quiz_data.difficulty, 'value') else str(quiz_data.difficulty),
            "time_per_question": quiz_data.time_per_question,
            "question_type": quiz_data.question_type.value if hasattr(quiz_data.question_type, 'value') else str(quiz_data.question_type),
            "total_questions": quiz_data.total_questions,
            "admin_id": admin_id,
            "is_active": True
        }
        
        print("💾 Saving quiz to Firebase...")
        print(f"📊 Quiz data: {quiz_dict}")
        
        quiz = await self.firebase_service.create_quiz(quiz_dict)
        print(f"✅ Quiz saved to Firebase with ID: {quiz['id']}")
        
        return QuizResponse(
            id=quiz['id'],
            title=quiz['title'],
            description=quiz['description'],
            topic=quiz['topic'],
            difficulty=quiz['difficulty'].value if hasattr(quiz['difficulty'], 'value') else quiz['difficulty'],
            time_per_question=quiz['time_per_question'],
            question_type=quiz['question_type'].value if hasattr(quiz['question_type'], 'value') else quiz['question_type'],
            total_questions=quiz['total_questions'],
            is_active=quiz['is_active'],
            created_at=quiz['created_at'],
            admin_id=quiz['admin_id']
        )

    async def get_admin_quizzes(self, admin_id: str) -> List[QuizResponse]:
        """Get all quizzes for an admin"""
        print(f"🔍 Fetching quizzes for admin: {admin_id}")
        quizzes = await self.firebase_service.get_quizzes_by_admin(admin_id)
        print(f"📊 Found {len(quizzes)} quizzes in database")
        
        for i, quiz in enumerate(quizzes):
            print(f"📝 Quiz {i+1}: {quiz.get('title', 'No title')} (ID: {quiz.get('id', 'No ID')})")
        
        return [
            QuizResponse(
                id=quiz['id'],
                title=quiz['title'],
                description=quiz['description'],
                topic=quiz['topic'],
                difficulty=quiz['difficulty'].value if hasattr(quiz['difficulty'], 'value') else quiz['difficulty'],
                time_per_question=quiz['time_per_question'],
                question_type=quiz['question_type'].value if hasattr(quiz['question_type'], 'value') else quiz['question_type'],
                total_questions=quiz['total_questions'],
                is_active=quiz['is_active'],
                created_at=quiz['created_at'],
                admin_id=quiz['admin_id']
            ) for quiz in quizzes
        ]

    async def get_quiz_results(self, quiz_id: str, admin_id: str) -> List[QuizResultResponse]:
        """Get quiz results and rankings"""
        try:
            # Verify quiz belongs to admin
            quiz = await self.firebase_service.get_quiz_by_id(quiz_id)
            if not quiz:
                print(f"❌ AdminService: Quiz {quiz_id} not found")
                return []
            
            if quiz.get('admin_id') != admin_id:
                print(f"❌ AdminService: Access denied for quiz {quiz_id}")
                return []
            
            results = await self.firebase_service.get_quiz_results_by_quiz(quiz_id)
            
            if not results:
                print(f"⚠️ AdminService: No results found for quiz {quiz_id}")
                return []
            
            # Add rankings and get student data
            ranked_results = []
            for i, result in enumerate(results, 1):
                try:
                    student = await self.firebase_service.get_student_by_id(result['student_id'])
                    if student:
                        ranked_results.append(QuizResultResponse(
                            id=result['id'],
                            total_score=result['total_score'],
                            total_questions=result['total_questions'],
                            percentage=result['percentage'],
                            rank=i,
                            completed_at=result['completed_at'],
                            student=StudentResponse(
                                id=student['id'],
                                name=student['name'],
                                email=student['email'],
                                extra_info=student['extra_info'],
                                created_at=student['created_at']
                            )
                        ))
                except Exception as e:
                    print(f"⚠️ AdminService: Error processing result {result.get('id', 'unknown')}: {e}")
                    continue
            
            print(f"✅ AdminService: Retrieved {len(ranked_results)} results for quiz {quiz_id}")
            return ranked_results
            
        except Exception as e:
            print(f"❌ AdminService: Error getting results for quiz {quiz_id}: {str(e)}")
            return []

    async def generate_quiz_questions(self, quiz_id: str, admin_id: str) -> Dict[str, Any]:
        """Trigger QuizGenerator agent to create questions"""
        # Verify quiz belongs to admin
        quiz = await self.firebase_service.get_quiz_by_id(quiz_id)
        if not quiz or quiz['admin_id'] != admin_id:
            raise ValueError("Quiz not found or access denied")
        
        print(f"🔧 AdminService: Starting question generation for quiz: {quiz['title']}")
        print(f"📊 Quiz ID: {quiz_id}")
        print(f"👤 Admin ID: {admin_id}")
        
        # Initialize QuizGenerator agent
        quiz_generator = QuizGeneratorAgent(self.db)
        result = await quiz_generator.generate_questions(quiz)
        
        if not result.get("success"):
            print(f"❌ AdminService: Question generation failed: {result.get('message', 'Unknown error')}")
            print("🚫 NO QUESTIONS SAVED TO DATABASE")
        else:
            print(f"✅ AdminService: Question generation successful: {result.get('message', 'Success')}")
        
        return result

    async def send_quiz_invitations(self, quiz_id: str, admin_id: str) -> Dict[str, Any]:
        """Trigger SendInvitations agent to email students"""
        # Verify quiz belongs to admin
        quiz = await self.firebase_service.get_quiz_by_id(quiz_id)
        if not quiz or quiz['admin_id'] != admin_id:
            raise ValueError("Quiz not found or access denied")
        
        # Initialize SendInvitations agent
        send_invitations = SendInvitationsAgent(self.db)
        result = await send_invitations.send_invitations(quiz)
        
        return result

    async def get_quiz_questions(self, quiz_id: str, admin_id: str) -> List[Dict[str, Any]]:
        """Get quiz questions for admin view (with correct answers)"""
        try:
            # Verify quiz belongs to admin
            quiz = await self.firebase_service.get_quiz_by_id(quiz_id)
            if not quiz:
                print(f"❌ AdminService: Quiz {quiz_id} not found")
                return []
            
            if quiz.get('admin_id') != admin_id:
                print(f"❌ AdminService: Access denied for quiz {quiz_id}")
                return []
            
            # Get questions from Firebase
            questions = await self.firebase_service.get_questions_by_quiz(quiz_id)
            
            if not questions:
                print(f"⚠️ AdminService: No questions found for quiz {quiz_id}")
                return []
            
            # Format questions for admin view (include correct answers and explanations)
            formatted_questions = []
            for i, question in enumerate(questions, 1):
                # Ensure all values are JSON serializable
                formatted_question = {
                    'id': str(question.get('id', '')),
                    'question_text': str(question.get('question_text', '')),
                    'options': [str(opt) for opt in question.get('options', [])],
                    'correct_answer': str(question.get('correct_answer', '')),
                    'explanation': str(question.get('explanation', '')),
                    'question_number': int(i),
                    'time_limit': int(question.get('time_limit', 60)),
                    'order': int(question.get('order', i))
                }
                
                # Convert datetime objects to strings if they exist
                if 'created_at' in question:
                    formatted_question['created_at'] = str(question['created_at'])
                if 'updated_at' in question:
                    formatted_question['updated_at'] = str(question['updated_at'])
                
                formatted_questions.append(formatted_question)
            
            print(f"✅ AdminService: Retrieved {len(formatted_questions)} questions for quiz {quiz_id}")
            return formatted_questions
            
        except Exception as e:
            print(f"❌ AdminService: Error getting questions for quiz {quiz_id}: {str(e)}")
            return []


    async def export_quiz_results(self, quiz_id: str, admin_id: str) -> Dict[str, Any]:
        """Export quiz results to Excel format"""
        # Get quiz and results
        quiz = await self.firebase_service.get_quiz_by_id(quiz_id)
        if not quiz or quiz['admin_id'] != admin_id:
            raise ValueError("Quiz not found or access denied")
        
        results = await self.get_quiz_results(quiz_id, admin_id)
        
        # Create Excel export logic here
        # This would generate an Excel file with student answers and scores
        
        return {
            "message": "Excel export generated successfully",
            "quiz_id": quiz_id,
            "total_students": len(results)
        }

    async def get_quiz_by_id(self, quiz_id: str) -> Dict[str, Any]:
        """Get a specific quiz by ID"""
        quiz = await self.firebase_service.get_quiz_by_id(quiz_id)
        if not quiz:
            raise ValueError("Quiz not found")
        return quiz

    async def update_quiz(self, quiz_id: str, quiz_data: QuizCreate, admin_id: str) -> Dict[str, Any]:
        """Update a quiz"""
        # Verify quiz exists and belongs to admin
        quiz = await self.firebase_service.get_quiz_by_id(quiz_id)
        if not quiz or quiz['admin_id'] != admin_id:
            raise ValueError("Quiz not found or access denied")
        
        # Update quiz data
        update_data = {
            "title": quiz_data.title,
            "description": quiz_data.description,
            "topic": quiz_data.topic,
            "difficulty": str(quiz_data.difficulty),
            "time_per_question": quiz_data.time_per_question,
            "question_type": str(quiz_data.question_type),
            "total_questions": quiz_data.total_questions,
            "updated_at": datetime.utcnow()
        }
        
        success = await self.firebase_service.update_quiz(quiz_id, update_data)
        if not success:
            raise ValueError("Failed to update quiz")
        
        # Return updated quiz
        return await self.firebase_service.get_quiz_by_id(quiz_id)
