from crewai import Agent, Task, Crew
from typing import Dict, Any, List
import secrets
import os
import json
from dotenv import load_dotenv
from app.services.email_service import EmailService
from app.services.llm_service import LLMService
from app.config.crewai_config import configure_crewai_groq

load_dotenv()
configure_crewai_groq()

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
        
        # Define the Email Invitation Agent using CrewAI with Groq LLM
        invitation_agent = Agent(
            role='Educational Communication Specialist',
            goal='Create personalized, engaging, and professional quiz invitation emails that motivate students to participate',
            backstory="""You are an expert in educational communication with deep understanding of:
            - Student psychology and motivation
            - Professional email writing
            - Educational engagement strategies
            - Clear and concise communication
            - Building excitement for learning activities
            
            You excel at writing emails that are:
            - Personalized and warm
            - Clear about expectations
            - Motivating and encouraging
            - Professional yet friendly
            - Informative without being overwhelming""",
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
                
                # Use CrewAI to generate personalized email
                quiz_link = f"{os.getenv('FRONTEND_URL', 'http://localhost:3000')}/quiz/{token}"
                
                # Create a CrewAI Task for email generation
                email_task = Task(
                    description=f"""
                    Create a personalized quiz invitation email for student: {student['name']}
                    
                    Quiz Details:
                    - Title: {quiz['title']}
                    - Topic: {quiz['topic']}
                    - Difficulty: {quiz['difficulty']}
                    - Time per question: {quiz['time_per_question']} seconds
                    - Total questions: {quiz['total_questions']}
                    - Quiz link: {quiz_link}
                    
                    Email Requirements:
                    1. Use the student's name: {student['name']}
                    2. Make it warm and personalized
                    3. Explain what the quiz is about and why it's important
                    4. Provide clear instructions on how to take the quiz
                    5. Include the quiz link prominently
                    6. End with an encouraging message
                    7. Keep the tone professional but friendly
                    8. Make it engaging and motivating
                    
                    Return the email in this JSON format:
                    {{
                        "subject": "Quiz Invitation - [Quiz Title]",
                        "body": "HTML email body with personalized content"
                    }}
                    """,
                    agent=invitation_agent,
                    expected_output="JSON object with subject and body fields for the email"
                )
                
                # Create and execute the CrewAI crew for email generation
                email_crew = Crew(
                    agents=[invitation_agent],
                    tasks=[email_task],
                    verbose=True
                )
                
                print(f"🤖 Generating personalized email for {student['name']} using CrewAI...")
                email_result = email_crew.kickoff()
                email_data = json.loads(str(email_result))
                
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
