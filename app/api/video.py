from fastapi import APIRouter, Depends, HTTPException
from typing import List

from app.database import get_db
from app.models.schemas import (
    VideoSubmissionCreate, VideoSubmissionResponse, 
    VideoTranscriptResponse, EmailNotification
)
from app.services.video_service import VideoService

router = APIRouter()

@router.post("/submit", response_model=VideoSubmissionResponse)
async def submit_video(
    video_data: VideoSubmissionCreate,
    student_email: str = None,
    db = Depends(get_db)
):
    """Submit video URL for evaluation"""
    video_service = VideoService(db)
    submission = await video_service.submit_video(video_data, student_email)
    if not submission:
        raise HTTPException(status_code=400, detail="Invalid video submission")
    return submission

@router.get("/submissions", response_model=List[VideoSubmissionResponse])
async def get_video_submissions(
    db = Depends(get_db)
):
    """Get all video submissions"""
    video_service = VideoService(db)
    return await video_service.get_all_submissions()

@router.get("/submission/{submission_id}/transcript", response_model=VideoTranscriptResponse)
async def get_video_transcript(
    submission_id: str,
    db = Depends(get_db)
):
    """Get video transcript and evaluation"""
    video_service = VideoService(db)
    transcript = await video_service.get_video_transcript(submission_id)
    if not transcript:
        raise HTTPException(status_code=404, detail="Transcript not found")
    return transcript

@router.post("/process-videos")
async def process_videos(
    db = Depends(get_db)
):
    """Trigger ProcessVideo agent to evaluate all pending videos"""
    video_service = VideoService(db)
    return await video_service.process_all_pending_videos()

@router.post("/final-ranking")
async def final_video_ranking(
    db = Depends(get_db)
):
    """Trigger FinalVideoRanking agent to rank videos and notify winners"""
    video_service = VideoService(db)
    return await video_service.final_video_ranking()

@router.get("/rankings")
async def get_video_rankings(
    db = Depends(get_db)
):
    """Get final video rankings and winners"""
    video_service = VideoService(db)
    return await video_service.get_video_rankings()
