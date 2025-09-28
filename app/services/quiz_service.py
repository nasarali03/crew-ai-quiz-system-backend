import secrets
from typing import List, Optional, Dict, Any
from app.models.schemas import (
    QuizResponse, QuestionResponse, QuizSubmission, 
    QuizAnswerResponse, QuizResultResponse
)
from app.agents.score_and_notify import ScoreAndNotifyAgent
from app.services.firebase_service import FirebaseService

class QuizService:
    def __init__(self, db):
        self.db = db
        self.firebase_service = FirebaseService(db)

    async def get_quiz_by_token(self, token: str) -> Optional[QuizResponse]:
        """Get quiz details by invitation token"""
        invitation = await self.firebase_service.get_invitation_by_token(token)
        
        if not invitation or invitation.get('is_used', False):
            return None
        
        quiz = await self.firebase_service.get_quiz_by_id(invitation['quiz_id'])
        if not quiz:
            return None
        
        return QuizResponse(
            id=quiz['id'],
            title=quiz['title'],
            description=quiz['description'],
            topic=quiz['topic'],
            difficulty=quiz['difficulty'],
            time_per_question=quiz['time_per_question'],
            question_type=quiz['question_type'],
            total_questions=quiz['total_questions'],
            is_active=quiz['is_active'],
            created_at=quiz['created_at'],
            admin_id=quiz['admin_id']
        )

    async def get_quiz_questions_by_token(self, token: str) -> List[QuestionResponse]:
        """Get quiz questions for student (without correct answers)"""
        invitation = await self.firebase_service.get_invitation_by_token(token)
        
        if not invitation or invitation.get('is_used', False):
            return []
        
        questions = await self.firebase_service.get_questions_by_quiz(invitation['quiz_id'])
        return [
            QuestionResponse(
                id=question['id'],
                question_text=question['question_text'],
                options=question['options'],  # This should be just the text options
                time_limit=question['time_limit'],
                order=question['order']
            ) for question in sorted(questions, key=lambda x: x['order'])
        ]

    async def submit_quiz_answers(self, token: str, submission: QuizSubmission) -> Optional[QuizResultResponse]:
        """Submit quiz answers and get results"""
        # Get invitation
        invitation = await self.firebase_service.get_invitation_by_token(token)
        
        if not invitation or invitation.get('is_used', False):
            return None
        
        # Mark invitation as used
        await self.firebase_service.update_invitation(invitation['id'], {"is_used": True})
        
        # Get quiz and questions
        quiz = await self.firebase_service.get_quiz_by_id(invitation['quiz_id'])
        questions = await self.firebase_service.get_questions_by_quiz(invitation['quiz_id'])
        student = await self.firebase_service.get_student_by_id(invitation['student_id'])
        
        if not quiz or not questions or not student:
            return None
        
        # Process answers
        total_score = 0
        total_questions = len(questions)
        
        for answer_data in submission.answers:
            # Get question
            question = next(
                (q for q in questions if q['id'] == answer_data.question_id), 
                None
            )
            if not question:
                continue
            
            # Check if answer is correct
            is_correct = answer_data.answer == question['correct_answer']
            
            if is_correct:
                total_score += 1
            
            # Save answer
            await self.firebase_service.create_quiz_answer({
                "question_id": answer_data.question_id,
                "student_id": invitation['student_id'],
                "invitation_id": invitation['id'],
                "quiz_id": invitation['quiz_id'],
                "answer": answer_data.answer,
                "is_correct": is_correct,
                "time_spent": answer_data.time_spent
            })
        
        # Calculate percentage
        percentage = (total_score / total_questions) * 100 if total_questions > 0 else 0
        
        # Create quiz result
        quiz_result = await self.firebase_service.create_quiz_result({
            "quiz_id": invitation['quiz_id'],
            "student_id": invitation['student_id'],
            "total_score": total_score,
            "total_questions": total_questions,
            "percentage": percentage
        })
        
        # Trigger ScoreAndNotify agent if this is the last submission
        # (This would need to be implemented based on your business logic)
        
        return QuizResultResponse(
            id=quiz_result['id'],
            total_score=total_score,
            total_questions=total_questions,
            percentage=percentage,
            rank=None,  # Will be calculated later
            completed_at=quiz_result['completed_at'],
            student=StudentResponse(
                id=student['id'],
                name=student['name'],
                email=student['email'],
                extra_info=student['extra_info'],
                created_at=student['created_at']
            )
        )

    async def get_quiz_status(self, token: str) -> Dict[str, Any]:
        """Check if quiz is accessible and get basic info"""
        invitation = await self.firebase_service.get_invitation_by_token(token)
        
        if not invitation:
            return None
        
        quiz = await self.firebase_service.get_quiz_by_id(invitation['quiz_id'])
        student = await self.firebase_service.get_student_by_id(invitation['student_id'])
        
        if not quiz or not student:
            return None
        
        return {
            "quiz_id": invitation['quiz_id'],
            "quiz_title": quiz['title'],
            "student_name": student['name'],
            "is_used": invitation.get('is_used', False),
            "is_active": quiz['is_active']
        }
