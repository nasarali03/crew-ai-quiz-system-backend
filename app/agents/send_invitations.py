from crewai import Agent, Task, Crew
from typing import Dict, Any, List
import secrets
import os
import json
import asyncio
from datetime import datetime
from dotenv import load_dotenv
from app.services.email_service import EmailService
from app.services.llm_service import LLMService
from app.config.crewai_config import configure_crewai_groq
from app.agents.email_generator import EmailGeneratorAgent

load_dotenv()
configure_crewai_groq()

class SendInvitationsAgent:
    def __init__(self, db):
        self.db = db
        self.email_service = EmailService()
        self.llm_service = LLMService()
        self.email_generator = EmailGeneratorAgent()
        
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
        
        # Generate email template once using CrewAI
        print("🤖 Generating email template using CrewAI...")
        quiz_data = {
            'title': quiz['title'],
            'topic': quiz['topic'],
            'difficulty': quiz['difficulty'],
            'time_per_question': quiz['time_per_question'],
            'total_questions': quiz['total_questions']
        }
        
        email_template = await self.email_generator.generate_bulk_quiz_invitation(quiz_data)
        
        # Create invitation tokens and send emails one at a time
        invitations_sent = 0
        failed_invitations = []

        for i, student in enumerate(students):
            try:
                # Add delay between emails to avoid rate limiting
                if i > 0:
                    print(f"⏳ Waiting 10 seconds before sending next email...")
                    await asyncio.sleep(10)  # Wait 10 seconds between emails
                
                # Generate unique token for this student
                token = secrets.token_urlsafe(32)
                print(f"🎲 Generated token for {student['name']}: {token}")

                # Get quiz questions at the time of invitation
                print(f"📋 Getting questions for quiz {quiz['id']} at invitation time...")
                quiz_questions = await firebase_service.get_questions_by_quiz(quiz['id'])
                
                if not quiz_questions:
                    print(f"⚠️ No questions found for quiz {quiz['id']}. Skipping invitation for {student['name']}")
                    failed_invitations.append(f"{student['email']}: No questions available for quiz")
                    continue

                print(f"✅ Found {len(quiz_questions)} questions for invitation")

                # Create enhanced quiz invitation with quiz snapshot
                invitation_dict = {
                    "quiz_id": quiz['id'],
                    "student_id": student['id'],
                    "token": token,
                    "is_used": False,
                    # Quiz snapshot at invitation time
                    "quiz_snapshot": {
                        "title": quiz['title'],
                        "description": quiz['description'],
                        "topic": quiz['topic'],
                        "difficulty": quiz['difficulty'],
                        "time_per_question": quiz['time_per_question'],
                        "total_questions": quiz['total_questions'],
                        "question_type": quiz.get('question_type', 'multiple_choice'),
                        "is_active": quiz['is_active'],
                        "admin_id": quiz['admin_id']
                    },
                    # Questions snapshot at invitation time
                    "questions_snapshot": [
                        {
                            "id": q['id'],
                            "question_text": q['question_text'],
                            "options": q['options'],
                            "correct_answer": q['correct_answer'],
                            "time_limit": q['time_limit'],
                            "order": q['order']
                        } for q in quiz_questions
                    ],
                    "questions_count": len(quiz_questions),
                    "invitation_created_at": datetime.utcnow().isoformat()
                }
                
                invitation = await firebase_service.create_quiz_invitation(invitation_dict)
                print(f"✅ Created enhanced invitation in Firebase with ID: {invitation['id']}")
                print(f"📊 Invitation includes {len(quiz_questions)} questions snapshot")

                # Create personalized quiz link for localhost development
                frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:3000')
                # Ensure the URL doesn't have trailing slash
                frontend_url = frontend_url.rstrip('/')
                quiz_link = f"{frontend_url}/quiz/{token}"
                
                print(f"🔗 Generated quiz link: {quiz_link}")
                print(f"📝 Token length: {len(token)} characters")

                # Personalize the email template
                personalized_subject = email_template['subject']
                personalized_body = email_template['body'].replace('{{QUIZ_LINK}}', quiz_link)
                personalized_body = personalized_body.replace('Dear Student', f"Dear {student['name']}")
                
                print(f"📧 Email body contains link: {'{{QUIZ_LINK}}' in email_template['body']}")
                print(f"📧 Personalized body contains actual link: {quiz_link in personalized_body}")

                print(f"📧 Sending email to {student['name']} ({student['email']})")

                # Send the email
                email_sent = await self.email_service.send_email(
                    to_email=student['email'],
                    subject=personalized_subject,
                    body=personalized_body
                )

                if email_sent:
                    # Mark invitation as sent
                    await firebase_service.update_invitation(
                        invitation['id'],
                        {"sent_at": "now()"}
                    )
                    invitations_sent += 1
                    print(f"✅ Email sent successfully to {student['name']}")
                else:
                    failed_invitations.append(student['email'])
                    print(f"❌ Failed to send email to {student['name']}")

            except Exception as e:
                failed_invitations.append(f"{student['email']}: {str(e)}")
                print(f"❌ Error sending email to {student['name']}: {str(e)}")
                continue
        
        return {
            "success": invitations_sent > 0,
            "message": f"Sent {invitations_sent} invitations successfully",
            "invitations_sent": invitations_sent,
            "total_students": len(students),
            "failed_invitations": failed_invitations
        }
