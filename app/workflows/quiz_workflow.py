"""
CrewAI Quiz System Workflow
Orchestrates the complete quiz generation, invitation, and evaluation process
"""

from crewai import Crew, Process
from typing import Dict, Any, List
import asyncio
from app.agents.quiz_generator import QuizGeneratorAgent
from app.agents.send_invitations import SendInvitationsAgent
from app.agents.score_and_notify import ScoreAndNotifyAgent
from app.agents.process_video import ProcessVideoAgent
from app.agents.final_video_ranking import FinalVideoRankingAgent

class QuizWorkflow:
    def __init__(self, db):
        self.db = db
        self.quiz_generator = QuizGeneratorAgent(db)
        self.send_invitations = SendInvitationsAgent(db)
        self.score_and_notify = ScoreAndNotifyAgent(db)
        self.process_video = ProcessVideoAgent(db)
        self.final_ranking = FinalVideoRankingAgent(db)
    
    async def run_complete_quiz_workflow(self, quiz_id: str, admin_id: str) -> Dict[str, Any]:
        """
        Run the complete quiz workflow:
        1. Generate quiz questions
        2. Send invitations to students
        3. Wait for quiz completion
        4. Score and notify top students
        5. Process video submissions
        6. Final ranking and winner notification
        """
        workflow_results = {
            "quiz_id": quiz_id,
            "admin_id": admin_id,
            "steps_completed": [],
            "errors": [],
            "success": True
        }
        
        try:
            # Step 1: Generate Quiz Questions
            print("Step 1: Generating quiz questions...")
            quiz_result = await self.quiz_generator.generate_questions({"id": quiz_id})
            if quiz_result.get("success"):
                workflow_results["steps_completed"].append("quiz_generation")
                print(f"✓ Quiz questions generated: {quiz_result.get('questions_count', 0)} questions")
            else:
                workflow_results["errors"].append(f"Quiz generation failed: {quiz_result.get('message', 'Unknown error')}")
                workflow_results["success"] = False
                return workflow_results
            
            # Step 2: Send Invitations
            print("Step 2: Sending quiz invitations...")
            invitation_result = await self.send_invitations.send_invitations({"id": quiz_id})
            if invitation_result.get("success"):
                workflow_results["steps_completed"].append("invitations_sent")
                print(f"✓ Invitations sent: {invitation_result.get('invitations_sent', 0)} students")
            else:
                workflow_results["errors"].append(f"Invitation sending failed: {invitation_result.get('message', 'Unknown error')}")
                workflow_results["success"] = False
                return workflow_results
            
            # Step 3: Wait for quiz completion (this would be handled by the frontend)
            print("Step 3: Waiting for quiz completion...")
            print("ℹ️ Students are now taking the quiz. This step is handled by the frontend.")
            workflow_results["steps_completed"].append("quiz_in_progress")
            
            return workflow_results
            
        except Exception as e:
            workflow_results["errors"].append(f"Workflow error: {str(e)}")
            workflow_results["success"] = False
            return workflow_results
    
    async def run_quiz_scoring_workflow(self, quiz_id: str) -> Dict[str, Any]:
        """
        Run the quiz scoring workflow:
        1. Score quiz results
        2. Notify top 5 students
        """
        workflow_results = {
            "quiz_id": quiz_id,
            "steps_completed": [],
            "errors": [],
            "success": True
        }
        
        try:
            # Step 1: Score and Notify
            print("Step 1: Scoring quiz results and notifying top students...")
            scoring_result = await self.score_and_notify.score_and_notify(quiz_id)
            if scoring_result.get("success"):
                workflow_results["steps_completed"].append("quiz_scoring")
                print(f"✓ Quiz scored and notifications sent: {scoring_result.get('notifications_sent', 0)} students")
                workflow_results["top_students"] = scoring_result.get("top_5_students", [])
            else:
                workflow_results["errors"].append(f"Quiz scoring failed: {scoring_result.get('message', 'Unknown error')}")
                workflow_results["success"] = False
            
            return workflow_results
            
        except Exception as e:
            workflow_results["errors"].append(f"Scoring workflow error: {str(e)}")
            workflow_results["success"] = False
            return workflow_results
    
    async def run_video_processing_workflow(self) -> Dict[str, Any]:
        """
        Run the video processing workflow:
        1. Process all pending videos
        2. Final ranking and winner notification
        """
        workflow_results = {
            "steps_completed": [],
            "errors": [],
            "success": True
        }
        
        try:
            # Step 1: Process Videos
            print("Step 1: Processing video submissions...")
            video_result = await self.process_video.process_video({"id": "batch_processing"})
            if video_result.get("success"):
                workflow_results["steps_completed"].append("video_processing")
                print(f"✓ Videos processed: {video_result.get('message', 'Processing completed')}")
            else:
                workflow_results["errors"].append(f"Video processing failed: {video_result.get('message', 'Unknown error')}")
                workflow_results["success"] = False
                return workflow_results
            
            # Step 2: Final Ranking
            print("Step 2: Final ranking and winner notification...")
            ranking_result = await self.final_ranking.rank_videos_and_notify()
            if ranking_result.get("success"):
                workflow_results["steps_completed"].append("final_ranking")
                print(f"✓ Final ranking completed: {ranking_result.get('notifications_sent', 0)} winners notified")
                workflow_results["winners"] = ranking_result.get("winners", [])
            else:
                workflow_results["errors"].append(f"Final ranking failed: {ranking_result.get('message', 'Unknown error')}")
                workflow_results["success"] = False
            
            return workflow_results
            
        except Exception as e:
            workflow_results["errors"].append(f"Video processing workflow error: {str(e)}")
            workflow_results["success"] = False
            return workflow_results
    
    async def run_automated_workflow(self, quiz_id: str, admin_id: str) -> Dict[str, Any]:
        """
        Run the complete automated workflow with all steps
        """
        print("🚀 Starting Complete Automated Quiz Workflow...")
        
        # Phase 1: Quiz Setup and Invitations
        quiz_workflow_result = await self.run_complete_quiz_workflow(quiz_id, admin_id)
        if not quiz_workflow_result["success"]:
            return quiz_workflow_result
        
        print("⏳ Waiting for quiz completion... (This would be handled by frontend)")
        
        # Phase 2: Quiz Scoring (this would be triggered after quiz completion)
        print("📊 Quiz completion detected. Starting scoring workflow...")
        scoring_workflow_result = await self.run_quiz_scoring_workflow(quiz_id)
        if not scoring_workflow_result["success"]:
            return scoring_workflow_result
        
        print("⏳ Waiting for video submissions... (This would be handled by frontend)")
        
        # Phase 3: Video Processing (this would be triggered after video submissions)
        print("🎥 Video submissions detected. Starting video processing workflow...")
        video_workflow_result = await self.run_video_processing_workflow()
        if not video_workflow_result["success"]:
            return video_workflow_result
        
        # Combine all results
        final_result = {
            "success": True,
            "message": "Complete automated workflow finished successfully",
            "quiz_workflow": quiz_workflow_result,
            "scoring_workflow": scoring_workflow_result,
            "video_workflow": video_workflow_result,
            "total_steps_completed": (
                len(quiz_workflow_result["steps_completed"]) +
                len(scoring_workflow_result["steps_completed"]) +
                len(video_workflow_result["steps_completed"])
            )
        }
        
        print("🎉 Complete automated workflow finished successfully!")
        return final_result
