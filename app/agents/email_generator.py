from crewai import Agent, Task, Crew
from typing import Dict, Any
import json
import os
from dotenv import load_dotenv
from app.config.crewai_config import configure_crewai_groq, get_crewai_llm

load_dotenv()
configure_crewai_groq()

class EmailGeneratorAgent:
    def __init__(self):
        # Get the configured Groq LLM
        self.llm = get_crewai_llm()
        
        self.email_agent = Agent(
            role='Email Marketing Specialist',
            goal='Create engaging, professional, and personalized email content that motivates students to participate in quizzes',
            backstory="""You are an expert email marketing specialist with deep understanding of:
            - Educational email communication
            - Student engagement strategies
            - Professional email writing
            - Clear and compelling call-to-actions
            - Building excitement for learning activities
            
            You excel at writing emails that are:
            - Personalized and warm
            - Clear about expectations
            - Motivating and encouraging
            - Professional yet friendly
            - Informative without being overwhelming
            - Include clear instructions and next steps""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm  # Use Groq LLM
        )
    
    async def generate_quiz_invitation_email(self, quiz_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a quiz invitation email using CrewAI"""
        
        # Create email generation task
        email_task = Task(
            description=f"""
            Create a professional quiz invitation email with the following details:
            
            Quiz Information:
            - Title: {quiz_data.get('title', 'Quiz')}
            - Topic: {quiz_data.get('topic', 'General Knowledge')}
            - Difficulty: {quiz_data.get('difficulty', 'Medium')}
            - Time per question: {quiz_data.get('time_per_question', 60)} seconds
            - Total questions: {quiz_data.get('total_questions', 10)}
            - Quiz link: {quiz_data.get('quiz_link', 'http://localhost:3000/quiz/token')}
            
            Email Requirements:
            1. Create an engaging subject line
            2. Write a warm, personalized greeting
            3. Explain what the quiz is about and why it's important
            4. Provide clear instructions on how to take the quiz
            5. Include the quiz link prominently
            6. End with an encouraging message
            7. Keep the tone professional but friendly
            8. Make it engaging and motivating
            9. Use HTML formatting for better presentation
            
            Return the email in this JSON format:
            {{
                "subject": "Quiz Invitation - [Quiz Title]",
                "body": "HTML email body with personalized content"
            }}
            """,
            agent=self.email_agent,
            expected_output="JSON object with subject and body fields for the email"
        )
        
        # Create and execute the CrewAI crew
        email_crew = Crew(
            agents=[self.email_agent],
            tasks=[email_task],
            verbose=True,
            llm=self.llm  # Use Groq LLM
        )
        
        print("🤖 Generating quiz invitation email using CrewAI...")
        email_result = email_crew.kickoff()
        
        try:
            email_data = json.loads(str(email_result))
            print("✅ Email generated successfully")
            return email_data
        except json.JSONDecodeError as e:
            print(f"❌ Error parsing email result: {e}")
            # Return a fallback email
            return {
                "subject": f"Quiz Invitation - {quiz_data.get('title', 'Quiz')}",
                "body": f"""
                <html>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                        <h2 style="color: #2c3e50;">Quiz Invitation</h2>
                        <p>You've been invited to take a quiz on <strong>{quiz_data.get('topic', 'General Knowledge')}</strong>.</p>
                        <p><a href="{quiz_data.get('quiz_link', '#')}" style="background-color: #3498db; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Start Quiz</a></p>
                    </div>
                </body>
                </html>
                """
            }
    
    async def generate_bulk_quiz_invitation(self, quiz_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a single email template for bulk sending to all students"""
        
        # Create bulk email generation task
        bulk_email_task = Task(
            description=f"""
            Create a professional quiz invitation email template that can be sent to multiple students.
            
            Quiz Information:
            - Title: {quiz_data.get('title', 'Quiz')}
            - Topic: {quiz_data.get('topic', 'General Knowledge')}
            - Difficulty: {quiz_data.get('difficulty', 'Medium')}
            - Time per question: {quiz_data.get('time_per_question', 60)} seconds
            - Total questions: {quiz_data.get('total_questions', 10)}
            
            Email Requirements:
            1. Create an engaging subject line
            2. Write a warm, professional greeting (use "Dear Student" or similar)
            3. Explain what the quiz is about and why it's important
            4. Provide clear instructions on how to take the quiz
            5. Include a prominent button/link using the placeholder: {{QUIZ_LINK}}
            6. Mention that the link is unique and can only be used once
            7. Include quiz details (topic, difficulty, time per question, total questions)
            8. End with an encouraging message
            9. Keep the tone professional but friendly
            10. Make it engaging and motivating
            11. Use HTML formatting for better presentation
            12. Make it suitable for bulk sending to multiple students
            13. Ensure the quiz link is clearly visible and clickable
            
            Return the email in this JSON format:
            {{
                "subject": "Quiz Invitation - [Quiz Title]",
                "body": "HTML email body template with {{QUIZ_LINK}} placeholder"
            }}
            """,
            agent=self.email_agent,
            expected_output="JSON object with subject and body fields for the email template"
        )
        
        # Create and execute the CrewAI crew
        email_crew = Crew(
            agents=[self.email_agent],
            tasks=[bulk_email_task],
            verbose=True,
            llm=self.llm  # Use Groq LLM
        )
        
        print("🤖 Generating bulk quiz invitation email template using CrewAI...")
        email_result = email_crew.kickoff()
        
        try:
            email_data = json.loads(str(email_result))
            print("✅ Bulk email template generated successfully")
            return email_data
        except json.JSONDecodeError as e:
            print(f"❌ Error parsing email result: {e}")
            # Return a fallback email template
            return {
                "subject": f"Quiz Invitation - {quiz_data.get('title', 'Quiz')}",
                "body": f"""
                <html>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 8px;">
                        <h2 style="color: #2c3e50; text-align: center;">🎯 Quiz Invitation</h2>
                        <p>Dear Student,</p>
                        <p>You've been invited to take a quiz on <strong>{quiz_data.get('topic', 'General Knowledge')}</strong>.</p>
                        
                        <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
                            <h3 style="margin-top: 0; color: #495057;">Quiz Details:</h3>
                            <ul>
                                <li><strong>Topic:</strong> {quiz_data.get('topic', 'General Knowledge')}</li>
                                <li><strong>Difficulty:</strong> {quiz_data.get('difficulty', 'Medium')}</li>
                                <li><strong>Questions:</strong> {quiz_data.get('total_questions', 10)}</li>
                                <li><strong>Time per question:</strong> {quiz_data.get('time_per_question', 60)} seconds</li>
                            </ul>
                        </div>
                        
                        <div style="text-align: center; margin: 30px 0;">
                            <a href="{{{{QUIZ_LINK}}}}" style="background-color: #007bff; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; font-size: 16px; font-weight: bold; display: inline-block;">🚀 Start Quiz Now</a>
                        </div>
                        
                        <p style="color: #6c757d; font-size: 14px;"><strong>Important:</strong> This link is unique to you and can only be used once. Please click the link above to access your quiz.</p>
                        
                        <p>Good luck with your quiz!</p>
                        
                        <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
                        <p style="color: #6c757d; font-size: 12px; text-align: center;">This email was sent from the Quiz System. If you have any questions, please contact your instructor.</p>
                    </div>
                </body>
                </html>
                """
            }
