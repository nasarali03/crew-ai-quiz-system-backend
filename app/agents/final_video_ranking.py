from crewai import Agent, Task, Crew
from typing import Dict, Any, List
import os
from dotenv import load_dotenv
from app.services.email_service import EmailService
from app.services.llm_service import LLMService

load_dotenv()

class FinalVideoRankingAgent:
    def __init__(self, db):
        self.db = db
        self.email_service = EmailService()
        self.llm_service = LLMService()
        
    async def rank_videos_and_notify(self) -> Dict[str, Any]:
        """Rank all video submissions and notify top 2 winners"""
        
        # Get all processed video submissions with transcripts
        from app.services.firebase_service import FirebaseService
        firebase_service = FirebaseService(self.db)
        
        submissions = await firebase_service.get_processed_submissions_with_transcripts()
        
        if len(submissions) < 2:
            return {
                "success": False,
                "message": "Need at least 2 video submissions to determine winners"
            }
        
        # Get top 2 submissions
        top_2_submissions = submissions[:2]
        
        # Create detailed ranking analysis
        ranking_analysis = []
        
        for i, submission in enumerate(top_2_submissions, 1):
            try:
                # Get student data
                student = await firebase_service.get_student_by_id(submission['student_id'])
                if not student:
                    continue
                
                # Use LLM service to generate ranking analysis
                ranking_prompt = f"""
                Evaluate and rank this video submission for the final competition.
                
                Student: {student['name']}
                Topic: {submission['topic']}
                Video URL: {submission['video_url']}
                Topic Coverage Score: {submission.get('transcript', {}).get('topic_coverage', 0)}
                Word Count: {submission.get('transcript', {}).get('word_count', 0)}
                Duration: {submission.get('transcript', {}).get('duration', 0)} seconds
                
                Evaluation Criteria:
                1. Topic coverage and relevance
                2. Content depth and quality
                3. Presentation clarity
                4. Originality and creativity
                5. Overall impact
                
                Provide detailed feedback and ranking justification.
                """
                
                if self.llm_service.google_api_key:
                    evaluation = await self.llm_service.generate_with_gemini(ranking_prompt)
                elif self.llm_service.groq_api_key:
                    evaluation = await self.llm_service.generate_with_groq(ranking_prompt)
                else:
                    evaluation = f"Ranked #{i} based on topic coverage score: {submission.get('transcript', {}).get('topic_coverage', 0)}"
                
                ranking_analysis.append({
                    "rank": i,
                    "student_name": student['name'],
                    "student_email": student['email'],
                    "topic_coverage": submission.get('transcript', {}).get('topic_coverage', 0),
                    "evaluation": evaluation,
                    "video_url": submission['video_url']
                })
                
            except Exception as e:
                print(f"Error analyzing submission {submission['id']}: {e}")
                continue
        
        # Send winner notifications
        notifications_sent = 0
        failed_notifications = []
        
        for winner in top_2_submissions:
            try:
                # Get student data
                student = await firebase_service.get_student_by_id(winner['student_id'])
                if not student:
                    continue
                
                # Use LLM service to generate winner notification
                winner_rank = ranking_analysis[top_2_submissions.index(winner)]['rank']
                winner_prompt = f"""
                Create a congratulatory email for the final winner.
                
                Winner: {student['name']}
                Final Rank: #{winner_rank}
                Topic Coverage: {winner.get('transcript', {}).get('topic_coverage', 0)}
                
                Requirements:
                1. Congratulate them on being a final winner
                2. Mention their excellent performance
                3. Highlight their achievement
                4. Keep the tone celebratory and professional
                5. Mention they are among the top 2 finalists
                
                Return JSON with subject and body.
                """
                
                if self.llm_service.google_api_key:
                    email_data = await self.llm_service.generate_with_gemini(winner_prompt)
                elif self.llm_service.groq_api_key:
                    email_data = await self.llm_service.generate_with_groq(winner_prompt)
                else:
                    # Fallback email
                    email_data = {
                        "subject": "Congratulations! You're a Final Winner!",
                        "body": f"""
                        Dear {student['name']},
                        
                        Congratulations! You are a final winner of the competition!
                        
                        You ranked #{winner_rank} with a topic coverage score of {winner.get('transcript', {}).get('topic_coverage', 0)}.
                        You are among the top 2 finalists and have achieved excellent results.
                        
                        Well done on your outstanding performance!
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
            "message": f"Final ranking completed. Notified {notifications_sent} winners",
            "winners": ranking_analysis,
            "notifications_sent": notifications_sent,
            "failed_notifications": failed_notifications
        }
