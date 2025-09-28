from typing import List, Optional, Dict, Any
from app.models.schemas import (
    VideoSubmissionCreate, VideoSubmissionResponse, 
    VideoTranscriptResponse, EmailNotification
)
from app.agents.process_video import ProcessVideoAgent
from app.agents.final_video_ranking import FinalVideoRankingAgent
from app.services.firebase_service import FirebaseService

class VideoService:
    def __init__(self, db):
        self.db = db
        self.firebase_service = FirebaseService(db)

    async def submit_video(self, video_data: VideoSubmissionCreate, student_email: str = None) -> Optional[VideoSubmissionResponse]:
        """Submit video URL for evaluation"""
        # Find student by email (assuming we have student email in the request)
        # This would need to be modified based on your authentication flow
        if not student_email:
            return None
            
        student = await self.firebase_service.get_student_by_email(student_email)
        
        if not student:
            return None
        
        # Create video submission
        submission_dict = {
            "student_id": student['id'],
            "video_url": video_data.video_url,
            "topic": video_data.topic,
            "is_processed": False
        }
        submission = await self.firebase_service.create_video_submission(submission_dict)
        
        return VideoSubmissionResponse(
            id=submission['id'],
            video_url=submission['video_url'],
            topic=submission['topic'],
            is_processed=submission['is_processed'],
            submitted_at=submission['submitted_at'],
            student=StudentResponse(
                id=student['id'],
                name=student['name'],
                email=student['email'],
                extra_info=student['extra_info'],
                created_at=student['created_at']
            )
        )

    async def get_all_submissions(self) -> List[VideoSubmissionResponse]:
        """Get all video submissions"""
        submissions = await self.firebase_service.get_all_video_submissions()
        
        result = []
        for submission in submissions:
            student = await self.firebase_service.get_student_by_id(submission['student_id'])
            if student:
                result.append(VideoSubmissionResponse(
                    id=submission['id'],
                    video_url=submission['video_url'],
                    topic=submission['topic'],
                    is_processed=submission['is_processed'],
                    submitted_at=submission['submitted_at'],
                    student=StudentResponse(
                        id=student['id'],
                        name=student['name'],
                        email=student['email'],
                        extra_info=student['extra_info'],
                        created_at=student['created_at']
                    )
                ))
        return result

    async def get_video_transcript(self, submission_id: str) -> Optional[VideoTranscriptResponse]:
        """Get video transcript and evaluation"""
        transcript = await self.firebase_service.get_transcript_by_submission(submission_id)
        
        if not transcript:
            return None
        
        return VideoTranscriptResponse(
            id=transcript['id'],
            transcript=transcript['transcript'],
            word_count=transcript['word_count'],
            duration=transcript['duration'],
            topic_coverage=transcript['topic_coverage'],
            evaluation=transcript['evaluation'],
            created_at=transcript['created_at']
        )

    async def process_all_pending_videos(self) -> Dict[str, Any]:
        """Trigger ProcessVideo agent to evaluate all pending videos"""
        # Get all unprocessed video submissions
        pending_submissions = await self.firebase_service.get_pending_video_submissions()
        
        if not pending_submissions:
            return {"message": "No pending videos to process"}
        
        # Initialize ProcessVideo agent
        process_video = ProcessVideoAgent(self.db)
        results = []
        
        for submission in pending_submissions:
            result = await process_video.process_video(submission)
            results.append(result)
        
        return {
            "message": f"Processed {len(results)} videos",
            "results": results
        }

    async def final_video_ranking(self) -> Dict[str, Any]:
        """Trigger FinalVideoRanking agent to rank videos and notify winners"""
        # Initialize FinalVideoRanking agent
        final_ranking = FinalVideoRankingAgent(self.db)
        result = await final_ranking.rank_videos_and_notify()
        
        return result

    async def get_video_rankings(self) -> Dict[str, Any]:
        """Get final video rankings and winners"""
        # Get all processed video submissions with transcripts
        submissions = await self.firebase_service.get_processed_submissions_with_transcripts()
        
        rankings = []
        for i, submission in enumerate(submissions, 1):
            student = await self.firebase_service.get_student_by_id(submission['student_id'])
            if student:
                rankings.append({
                    "rank": i,
                    "student_name": student['name'],
                    "student_email": student['email'],
                    "topic_coverage": submission.get('transcript', {}).get('topic_coverage', 0),
                    "video_url": submission['video_url'],
                    "submitted_at": submission['submitted_at']
                })
        
        return {
            "total_submissions": len(rankings),
            "rankings": rankings,
            "winners": rankings[:2] if len(rankings) >= 2 else rankings
        }
