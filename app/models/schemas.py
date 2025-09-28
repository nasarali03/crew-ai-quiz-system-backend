from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

# Enums
class DifficultyLevel(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"

class QuestionType(str, Enum):
    MCQ = "MCQ"

# Base schemas
class StudentBase(BaseModel):
    name: str
    email: EmailStr
    student_id: Optional[str] = None
    data: Optional[str] = None
    extra_info: Optional[str] = None

class StudentCreate(StudentBase):
    pass

class StudentResponse(StudentBase):
    id: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# Quiz schemas
class QuizSettings(BaseModel):
    title: str
    description: Optional[str] = None
    topic: str
    difficulty: DifficultyLevel
    time_per_question: int  # seconds
    question_type: QuestionType
    total_questions: int

class QuizCreate(QuizSettings):
    pass

class QuizResponse(QuizSettings):
    id: str
    is_active: bool
    created_at: datetime
    admin_id: str
    
    class Config:
        from_attributes = True

# Question schemas
class QuestionOption(BaseModel):
    text: str
    is_correct: bool

class QuestionCreate(BaseModel):
    question_text: str
    options: List[QuestionOption]
    correct_answer: str
    time_limit: int
    order: int

class QuestionResponse(BaseModel):
    id: str
    question_text: str
    options: List[str]  # Just the text options for students
    time_limit: int
    order: int
    
    class Config:
        from_attributes = True

# Quiz invitation schemas
class QuizInvitationCreate(BaseModel):
    quiz_id: str
    student_id: str

class QuizInvitationResponse(BaseModel):
    id: str
    token: str
    is_used: bool
    sent_at: Optional[datetime]
    quiz: QuizResponse
    student: StudentResponse
    
    class Config:
        from_attributes = True

# Quiz answer schemas
class QuizAnswerCreate(BaseModel):
    question_id: str
    answer: str
    time_spent: int

class QuizSubmission(BaseModel):
    answers: List[QuizAnswerCreate]

class QuizAnswerResponse(BaseModel):
    id: str
    answer: str
    is_correct: bool
    time_spent: int
    submitted_at: datetime
    question: QuestionResponse
    
    class Config:
        from_attributes = True

# Video submission schemas
class VideoSubmissionCreate(BaseModel):
    video_url: str
    topic: str

class VideoSubmissionResponse(BaseModel):
    id: str
    video_url: str
    topic: str
    is_processed: bool
    submitted_at: datetime
    student: StudentResponse
    
    class Config:
        from_attributes = True

# Video transcript schemas
class VideoTranscriptResponse(BaseModel):
    id: str
    transcript: str
    word_count: int
    duration: int
    topic_coverage: float
    evaluation: Optional[Dict[str, Any]]
    created_at: datetime
    
    class Config:
        from_attributes = True

# Quiz result schemas
class QuizResultResponse(BaseModel):
    id: str
    total_score: int
    total_questions: int
    percentage: float
    rank: Optional[int]
    completed_at: datetime
    student: StudentResponse
    
    class Config:
        from_attributes = True

# Excel upload schemas
class ExcelUploadResponse(BaseModel):
    message: str
    students_imported: int
    students: List[StudentResponse]

# Email schemas
class EmailInvitation(BaseModel):
    student_email: str
    student_name: str
    quiz_title: str
    quiz_link: str

class EmailNotification(BaseModel):
    student_email: str
    student_name: str
    message: str
    subject: str

# Admin schemas
class AdminCreate(BaseModel):
    email: EmailStr
    password: str
    name: str

class AdminLogin(BaseModel):
    email: EmailStr
    password: str

class AdminResponse(BaseModel):
    id: str
    email: str
    name: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# Token schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    admin_id: Optional[str] = None
