from crewai import Agent, Task, Crew
from typing import Dict, Any, List
import secrets
import os
from dotenv import load_dotenv
from app.services.email_service import EmailService
from app.services.llm_service import LLMService

load_dotenv()

class SendInvitationsAgent:
    def __init__(self, db):
        self.db = db
        self.email_service = EmailService()
        self.llm_service = LLMService()
        
    async def send_invitations(self, quiz) -> Dict[str, Any]:
        """Send personalized quiz invitations to all students"""
        
        # Get all students
        from app.services.firebase_service import FirebaseService
        firebase_service = FirebaseService(self.db)
        students = await firebase_service.get_all_students()
        
        if not students:
            return {
                "success": False,
                "message": "No students found to send invitations to"
            }
        
        # Define the Email Invitation Agent
        invitation_agent = Agent(
            role='Email Invitation Specialist',
            goal='Send personalized quiz invitations to students with clear instructions',
            backstory="""You are a professional communication specialist who excels at 
            writing engaging, clear, and personalized emails. You understand how to 
            motivate students while providing all necessary information.""",
            verbose=True,
            allow_delegation=False
        )
        
        # Create invitation tokens and send emails
        invitations_sent = 0
        failed_invitations = []
        
        for student in students:
            try:
                # Generate unique token for this student
                token = secrets.token_urlsafe(32)
                
                # Create quiz invitation
                invitation_dict = {
                    "quiz_id": quiz['id'],
                    "student_id": student['id'],
                    "token": token,
                    "is_used": False
                }
                invitation = await firebase_service.create_quiz_invitation(invitation_dict)
                
                # Use LLM service to generate personalized email
                quiz_link = f"{os.getenv('FRONTEND_URL', 'http://localhost:3000')}/quiz/{token}"
                email_data = await self.llm_service.generate_email_content(
                    student_name=student['name'],
                    quiz_title=quiz['title'],
                    quiz_link=quiz_link
                )
                
                # Send the email
                email_sent = await self.email_service.send_email(
                    to_email=student['email'],
                    subject=email_data['subject'],
                    body=email_data['body']
                )
                
                if email_sent:
                    # Mark invitation as sent
                    await firebase_service.update_invitation(
                        invitation['id'], 
                        {"sent_at": "now()"}
                    )
                    invitations_sent += 1
                else:
                    failed_invitations.append(student['email'])
                    
            except Exception as e:
                failed_invitations.append(f"{student['email']}: {str(e)}")
                continue
        
        return {
            "success": invitations_sent > 0,
            "message": f"Sent {invitations_sent} invitations successfully",
            "invitations_sent": invitations_sent,
            "total_students": len(students),
            "failed_invitations": failed_invitations
        }
