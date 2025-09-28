# CrewAI Quiz System API Documentation

## Overview

The CrewAI Quiz System API provides endpoints for automated quiz generation, student management, and video evaluation using AI agents.

## Base URL

- Development: `http://localhost:8000`
- Production: `https://your-domain.com`

## Authentication

Most endpoints require JWT authentication. Include the token in the Authorization header:

```
Authorization: Bearer <your_jwt_token>
```

## API Endpoints

### Authentication Endpoints

#### Register Admin

```http
POST /api/auth/register
Content-Type: application/json

{
  "email": "admin@example.com",
  "password": "secure_password",
  "name": "Admin Name"
}
```

**Response:**

```json
{
  "id": "admin_id",
  "email": "admin@example.com",
  "name": "Admin Name",
  "created_at": "2024-01-01T00:00:00Z"
}
```

#### Login Admin

```http
POST /api/auth/login
Content-Type: application/x-www-form-urlencoded

username=admin@example.com&password=secure_password
```

**Response:**

```json
{
  "access_token": "jwt_token_here",
  "token_type": "bearer"
}
```

#### Get Current Admin

```http
GET /api/auth/me
Authorization: Bearer <token>
```

### Admin Management Endpoints

#### Upload Students

```http
POST /api/admin/upload-students
Authorization: Bearer <token>
Content-Type: multipart/form-data

file: <excel_file>
```

**Response:**

```json
{
  "message": "Successfully imported 25 students",
  "students_imported": 25,
  "students": [...]
}
```

#### Get All Students

```http
GET /api/admin/students
Authorization: Bearer <token>
```

#### Create Quiz

```http
POST /api/admin/create-quiz
Authorization: Bearer <token>
Content-Type: application/json

{
  "title": "Python Programming Quiz",
  "description": "Test your Python knowledge",
  "topic": "Python Programming",
  "difficulty": "medium",
  "time_per_question": 30,
  "question_type": "MCQ",
  "total_questions": 10
}
```

#### Get Admin Quizzes

```http
GET /api/admin/quizzes
Authorization: Bearer <token>
```

#### Get Quiz Results

```http
GET /api/admin/quiz/{quiz_id}/results
Authorization: Bearer <token>
```

#### Generate Quiz Questions

```http
POST /api/admin/quiz/{quiz_id}/generate-questions
Authorization: Bearer <token>
```

#### Send Quiz Invitations

```http
POST /api/admin/quiz/{quiz_id}/send-invitations
Authorization: Bearer <token>
```

### Quiz System Endpoints

#### Get Quiz by Token

```http
GET /api/quiz/{token}
```

**Response:**

```json
{
  "id": "quiz_id",
  "title": "Python Programming Quiz",
  "description": "Test your Python knowledge",
  "topic": "Python Programming",
  "difficulty": "medium",
  "time_per_question": 30,
  "question_type": "MCQ",
  "total_questions": 10,
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z"
}
```

#### Get Quiz Questions

```http
GET /api/quiz/{token}/questions
```

**Response:**

```json
[
  {
    "id": "question_id",
    "question_text": "What is Python?",
    "options": [
      "A programming language",
      "A snake",
      "A type of coffee",
      "A car"
    ],
    "time_limit": 30,
    "order": 1
  }
]
```

#### Submit Quiz Answers

```http
POST /api/quiz/{token}/submit
Content-Type: application/json

{
  "answers": [
    {
      "question_id": "question_id",
      "answer": "A programming language",
      "time_spent": 25
    }
  ]
}
```

**Response:**

```json
{
  "id": "result_id",
  "total_score": 8,
  "total_questions": 10,
  "percentage": 80.0,
  "rank": null,
  "completed_at": "2024-01-01T00:00:00Z",
  "student": {...}
}
```

#### Get Quiz Status

```http
GET /api/quiz/{token}/status
```

### Video System Endpoints

#### Submit Video

```http
POST /api/video/submit
Content-Type: application/json

{
  "video_url": "https://youtube.com/watch?v=example",
  "topic": "Python Programming"
}
```

#### Get Video Submissions

```http
GET /api/video/submissions
```

#### Get Video Transcript

```http
GET /api/video/submission/{submission_id}/transcript
```

#### Process Videos

```http
POST /api/video/process-videos
```

#### Final Video Ranking

```http
POST /api/video/final-ranking
```

#### Get Video Rankings

```http
GET /api/video/rankings
```

### Workflow Endpoints

#### Run Complete Quiz Workflow

```http
POST /api/workflow/quiz/{quiz_id}/run-complete-workflow
Authorization: Bearer <token>
```

**Response:**

```json
{
  "message": "Complete quiz workflow executed successfully",
  "workflow_result": {
    "quiz_id": "quiz_id",
    "admin_id": "admin_id",
    "steps_completed": ["quiz_generation", "invitations_sent"],
    "errors": [],
    "success": true
  }
}
```

#### Run Quiz Scoring Workflow

```http
POST /api/workflow/quiz/{quiz_id}/run-scoring-workflow
Authorization: Bearer <token>
```

#### Run Video Processing Workflow

```http
POST /api/workflow/run-video-processing-workflow
Authorization: Bearer <token>
```

#### Run Automated Workflow

```http
POST /api/workflow/quiz/{quiz_id}/run-automated-workflow
Authorization: Bearer <token>
```

## Data Models

### Student

```json
{
  "id": "string",
  "name": "string",
  "email": "string",
  "extra_info": "string",
  "created_at": "datetime"
}
```

### Quiz

```json
{
  "id": "string",
  "title": "string",
  "description": "string",
  "topic": "string",
  "difficulty": "easy|medium|hard",
  "time_per_question": "integer",
  "question_type": "MCQ",
  "total_questions": "integer",
  "is_active": "boolean",
  "created_at": "datetime",
  "admin_id": "string"
}
```

### Question

```json
{
  "id": "string",
  "question_text": "string",
  "options": "array of strings",
  "correct_answer": "string",
  "time_limit": "integer",
  "order": "integer",
  "quiz_id": "string"
}
```

### Quiz Result

```json
{
  "id": "string",
  "total_score": "integer",
  "total_questions": "integer",
  "percentage": "float",
  "rank": "integer",
  "completed_at": "datetime",
  "quiz_id": "string",
  "student_id": "string"
}
```

### Video Submission

```json
{
  "id": "string",
  "video_url": "string",
  "topic": "string",
  "is_processed": "boolean",
  "submitted_at": "datetime",
  "student_id": "string"
}
```

### Video Transcript

```json
{
  "id": "string",
  "transcript": "string",
  "word_count": "integer",
  "duration": "integer",
  "topic_coverage": "float",
  "evaluation": "object",
  "created_at": "datetime",
  "video_submission_id": "string"
}
```

## Error Responses

### 400 Bad Request

```json
{
  "detail": "Error message"
}
```

### 401 Unauthorized

```json
{
  "detail": "Could not validate credentials"
}
```

### 404 Not Found

```json
{
  "detail": "Resource not found"
}
```

### 500 Internal Server Error

```json
{
  "detail": "Internal server error"
}
```

## CrewAI Agents

### QuizGeneratorAgent

- **Role**: Quiz Question Generator
- **Goal**: Generate high-quality quiz questions
- **Input**: Topic, difficulty, number of questions
- **Output**: Generated questions with options and correct answers

### SendInvitationsAgent

- **Role**: Email Invitation Specialist
- **Goal**: Send personalized quiz invitations
- **Input**: Student list, quiz details
- **Output**: Sent invitations with unique tokens

### ScoreAndNotifyAgent

- **Role**: Quiz Scoring Specialist
- **Goal**: Score quizzes and notify top students
- **Input**: Quiz results
- **Output**: Rankings and notifications

### ProcessVideoAgent

- **Role**: Video Processing Specialist
- **Goal**: Process video submissions and generate transcripts
- **Input**: Video URLs
- **Output**: Transcripts and analysis

### FinalVideoRankingAgent

- **Role**: Video Ranking Specialist
- **Goal**: Rank videos and notify winners
- **Input**: Processed videos
- **Output**: Final rankings and winner notifications

## Workflow Examples

### Complete Quiz Workflow

1. Admin creates quiz
2. System generates questions using LLM
3. System sends invitations to students
4. Students take quiz
5. System scores results
6. System notifies top students
7. Students submit videos
8. System processes videos
9. System ranks videos and notifies winners

### API Usage Example

```python
import requests

# Register admin
response = requests.post('http://localhost:8000/api/auth/register', json={
    'email': 'admin@example.com',
    'password': 'password',
    'name': 'Admin'
})

# Login
response = requests.post('http://localhost:8000/api/auth/login', data={
    'username': 'admin@example.com',
    'password': 'password'
})
token = response.json()['access_token']

# Create quiz
headers = {'Authorization': f'Bearer {token}'}
response = requests.post('http://localhost:8000/api/admin/create-quiz',
                        json={
                            'title': 'Python Quiz',
                            'topic': 'Python Programming',
                            'difficulty': 'medium',
                            'total_questions': 10
                        }, headers=headers)

# Run workflow
response = requests.post(f'http://localhost:8000/api/workflow/quiz/{quiz_id}/run-complete-workflow',
                        headers=headers)
```

## Rate Limits

- Authentication: 5 requests per minute
- Quiz operations: 10 requests per minute
- Video processing: 3 requests per minute
- Workflow operations: 2 requests per minute

## Webhooks

The system supports webhooks for workflow events:

- `quiz.completed` - Quiz workflow completed
- `scoring.completed` - Scoring workflow completed
- `video.processing.completed` - Video processing completed
- `ranking.completed` - Final ranking completed

## SDKs

### Python SDK

```python
from crewai_quiz_sdk import QuizClient

client = QuizClient(api_key='your_api_key')
quiz = client.create_quiz(title='Python Quiz', topic='Python')
result = client.run_workflow(quiz.id)
```

### JavaScript SDK

```javascript
import { QuizClient } from "crewai-quiz-sdk";

const client = new QuizClient({ apiKey: "your_api_key" });
const quiz = await client.createQuiz({ title: "Python Quiz", topic: "Python" });
const result = await client.runWorkflow(quiz.id);
```

## Support

For API support:

- Documentation: `/docs` (Swagger UI)
- Health Check: `/health`
- Status: `/` (API status)

For issues:

- Check logs for error details
- Verify authentication tokens
- Ensure proper request format
- Contact support team
