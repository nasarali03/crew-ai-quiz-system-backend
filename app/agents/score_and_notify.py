from crewai import Agent, Task, Crew
from typing import Dict, Any, List
import os
from dotenv import load_dotenv
from app.services.email_service import EmailService
from app.services.llm_service import LLMService

load_dotenv()

class ScoreAndNotifyAgent:
    def __init__(self, db):
        self.db = db
        self.email_service = EmailService()
        self.llm_service = LLMService()
        
    async def score_and_notify(self, quiz_id: str) -> Dict[str, Any]:
        """Score quiz results and notify top 5 students"""
        
        # Get quiz results ordered by score
        from app.services.firebase_service import FirebaseService
        firebase_service = FirebaseService(self.db)
        
        results = await firebase_service.get_quiz_results_by_quiz(quiz_id)
        
        if not results:
            return {
                "success": False,
                "message": "No quiz results found"
            }
        
        # Update rankings
        for i, result in enumerate(results, 1):
            await firebase_service.update_quiz_result(
                result['id'],
                {"rank": i}
            )
        
        # Get top 5 students
        top_5_students = results[:5]
        
        # Get quiz details
        quiz = await firebase_service.get_quiz_by_id(quiz_id)
        
        notifications_sent = 0
        failed_notifications = []
        
        for i, result in enumerate(top_5_students, 1):
            try:
                # Get student data
                student = await firebase_service.get_student_by_id(result['student_id'])
                if not student:
                    continue
                
                # Use LLM service to generate personalized notification
                video_submit_link = f"{os.getenv('FRONTEND_URL', 'http://localhost:3000')}/video-submit"
                
                # Create a simple notification message using LLM
                notification_prompt = f"""
                Create a congratulatory email for a top-performing student.
                
                Student: {student['name']}
                Score: {result['total_score']}/{result['total_questions']} ({result['percentage']:.1f}%)
                Rank: #{i} out of {len(results)} students
                Quiz: {quiz['title']} on {quiz['topic']}
                
                Next step: Submit a video about "{quiz['topic']}" at {video_submit_link}
                Only top 2 video submissions will be final winners.
                
                Return JSON with subject and body.
                """
                
                if self.llm_service.google_api_key:
                    email_data = await self.llm_service.generate_with_gemini(notification_prompt)
                elif self.llm_service.groq_api_key:
                    email_data = await self.llm_service.generate_with_groq(notification_prompt)
                else:
                    # Fallback email
                    email_data = {
                        "subject": f"Congratulations! You've Qualified for Video Round - {quiz['title']}",
                        "body": f"""
                        Dear {student['name']},
                        
                        Congratulations! You scored {result['total_score']}/{result['total_questions']} ({result['percentage']:.1f}%) 
                        and ranked #{i} out of {len(results)} students in the {quiz['title']} quiz.
                        
                        You've qualified for the next round! Please submit a video about "{quiz['topic']}":
                        {video_submit_link}
                        
                        Only the top 2 video submissions will be selected as final winners.
                        
                        Good luck!
                        """
                    }
                
                # Send the email
                email_sent = await self.email_service.send_email(
                    to_email=student['email'],
                    subject=email_data['subject'],
                    body=email_data['body']
                )
                
                if email_sent:
                    notifications_sent += 1
                else:
                    failed_notifications.append(student['email'])
                    
            except Exception as e:
                failed_notifications.append(f"{student['email']}: {str(e)}")
                continue
        
        return {
            "success": notifications_sent > 0,
            "message": f"Sent {notifications_sent} notifications to top students",
            "notifications_sent": notifications_sent,
            "top_5_students": [
                {
                    "name": student['name'],
                    "email": student['email'],
                    "score": result['total_score'],
                    "percentage": result['percentage'],
                    "rank": i
                } for i, result in enumerate(top_5_students, 1)
            ],
            "failed_notifications": failed_notifications
        }
