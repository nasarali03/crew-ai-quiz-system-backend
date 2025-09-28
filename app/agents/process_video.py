from crewai import Agent, Task, Crew
from typing import Dict, Any, List
import os
import re
from dotenv import load_dotenv
from youtube_transcript_api import YouTubeTranscriptApi
from app.services.llm_service import LLMService

load_dotenv()

class ProcessVideoAgent:
    def __init__(self, db):
        self.db = db
        self.llm_service = LLMService()
        
    async def process_video(self, video_submission) -> Dict[str, Any]:
        """Process video submission and generate transcript"""
        
        try:
            # Extract video ID from YouTube URL
            video_id = self._extract_youtube_id(video_submission['video_url'])
            if not video_id:
                return {
                    "success": False,
                    "message": "Invalid YouTube URL"
                }
            
            # Get transcript from YouTube
            transcript_data = self._get_youtube_transcript(video_id)
            if not transcript_data:
                return {
                    "success": False,
                    "message": "Could not retrieve transcript from video"
                }
            
            # Combine transcript text
            transcript_text = " ".join([item['text'] for item in transcript_data])
            word_count = len(transcript_text.split())
            
            # Use LLM service to analyze transcript
            analysis = await self.llm_service.analyze_video_transcript(
                transcript=transcript_text,
                required_topic=video_submission['topic']
            )
            
            # Save transcript and analysis to database
            from app.services.firebase_service import FirebaseService
            firebase_service = FirebaseService(self.db)
            
            transcript_dict = {
                "video_submission_id": video_submission['id'],
                "transcript": transcript_text,
                "word_count": word_count,
                "duration": transcript_data[-1]['start'] + transcript_data[-1]['duration'] if transcript_data else 0,
                "topic_coverage": analysis['topic_coverage'],
                "evaluation": analysis
            }
            transcript = await firebase_service.create_video_transcript(transcript_dict)
            
            # Mark video as processed
            await firebase_service.update_video_submission(
                video_submission['id'],
                {"is_processed": True, "processed_at": "now()"}
            )
            
            return {
                "success": True,
                "message": "Video processed successfully",
                "transcript_id": transcript['id'],
                "topic_coverage": analysis['topic_coverage'],
                "word_count": word_count
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error processing video: {str(e)}",
                "error": str(e)
            }
    
    def _extract_youtube_id(self, url: str) -> str:
        """Extract YouTube video ID from URL"""
        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&\n?#]+)',
            r'youtube\.com\/watch\?.*v=([^&\n?#]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None
    
    def _get_youtube_transcript(self, video_id: str) -> List[Dict]:
        """Get transcript from YouTube video"""
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            return transcript
        except Exception as e:
            print(f"Error getting transcript: {e}")
            return None
