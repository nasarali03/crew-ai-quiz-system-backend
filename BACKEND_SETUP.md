# CrewAI Quiz System Backend Setup

This document provides comprehensive setup instructions for the CrewAI Quiz System backend.

## Overview

The backend is built with:

- **FastAPI** - Modern Python web framework
- **Firebase Firestore** - NoSQL database
- **CrewAI** - AI agent orchestration framework
- **Google Gemini & Groq** - LLM providers
- **YouTube Transcript API** - Video processing
- **SendGrid/SMTP** - Email services

## Prerequisites

- Python 3.8+
- Firebase project with Firestore enabled
- Google API key (for Gemini)
- Groq API key (alternative LLM)
- Email service (SendGrid or SMTP)

## Installation

1. **Clone and navigate to backend directory:**

   ```bash
   cd backend
   ```

2. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**

   ```bash
   cp env.example .env
   ```

4. **Configure Firebase:**

   - Create a Firebase project at https://console.firebase.google.com
   - Enable Firestore Database
   - Generate a service account key
   - Download the JSON file and place it in the backend directory
   - Update `.env` with the path to your service account file

5. **Configure API keys:**

   - Get Google API key from https://console.cloud.google.com
   - Get Groq API key from https://console.groq.com
   - Update `.env` with your API keys

6. **Configure email service:**
   - Option 1: Use SendGrid (recommended for production)
   - Option 2: Use SMTP (Gmail, etc.)

## Environment Variables

Create a `.env` file with the following variables:

```env
# Firebase Configuration
FIREBASE_CREDENTIALS_PATH=path/to/your/firebase-service-account.json

# LLM API Keys
GOOGLE_API_KEY=your_google_api_key_here
GROQ_API_KEY=your_groq_api_key_here

# JWT Configuration
JWT_SECRET=your_jwt_secret_key_here

# Email Configuration (SMTP)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
SMTP_FROM_EMAIL=your_email@gmail.com

# Email Configuration (SendGrid - Alternative)
SENDGRID_API_KEY=your_sendgrid_api_key_here

# Frontend URL
FRONTEND_URL=http://localhost:3000

# Server Configuration
HOST=0.0.0.0
PORT=8000
RELOAD=true
ENVIRONMENT=development
```

## Firebase Setup

1. **Create Firebase Project:**

   - Go to https://console.firebase.google.com
   - Create a new project
   - Enable Firestore Database

2. **Generate Service Account:**

   - Go to Project Settings > Service Accounts
   - Click "Generate new private key"
   - Download the JSON file
   - Place it in your backend directory

3. **Firestore Security Rules:**
   ```javascript
   rules_version = '2';
   service cloud.firestore {
     match /databases/{database}/documents {
       // Allow read/write access to all documents
       match /{document=**} {
         allow read, write: if true;
       }
     }
   }
   ```

## API Endpoints

### Authentication

- `POST /api/auth/register` - Register admin
- `POST /api/auth/login` - Login admin
- `GET /api/auth/me` - Get current admin

### Admin Management

- `POST /api/admin/upload-students` - Upload student list
- `GET /api/admin/students` - Get all students
- `POST /api/admin/create-quiz` - Create quiz
- `GET /api/admin/quizzes` - Get admin quizzes
- `GET /api/admin/quiz/{quiz_id}/results` - Get quiz results

### Quiz System

- `GET /api/quiz/{token}` - Get quiz by token
- `GET /api/quiz/{token}/questions` - Get quiz questions
- `POST /api/quiz/{token}/submit` - Submit quiz answers
- `GET /api/quiz/{token}/status` - Get quiz status

### Video System

- `POST /api/video/submit` - Submit video
- `GET /api/video/submissions` - Get all submissions
- `GET /api/video/submission/{id}/transcript` - Get video transcript
- `POST /api/video/process-videos` - Process videos
- `POST /api/video/final-ranking` - Final ranking

### Workflow Management

- `POST /api/workflow/quiz/{quiz_id}/run-complete-workflow` - Run complete quiz workflow
- `POST /api/workflow/quiz/{quiz_id}/run-scoring-workflow` - Run scoring workflow
- `POST /api/workflow/run-video-processing-workflow` - Run video processing workflow
- `POST /api/workflow/quiz/{quiz_id}/run-automated-workflow` - Run automated workflow

## Running the Backend

### Development Mode

```bash
python run.py
```

### Production Mode

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Using Docker (Optional)

```bash
docker build -t crewai-quiz-backend .
docker run -p 8000:8000 crewai-quiz-backend
```

## CrewAI Agents

The system includes 5 specialized CrewAI agents:

1. **QuizGeneratorAgent** - Generates quiz questions using LLM
2. **SendInvitationsAgent** - Sends personalized email invitations
3. **ScoreAndNotifyAgent** - Scores quizzes and notifies top students
4. **ProcessVideoAgent** - Processes video submissions and transcripts
5. **FinalVideoRankingAgent** - Ranks videos and notifies winners

## Workflow System

The backend includes automated workflows:

1. **Complete Quiz Workflow:**

   - Generate quiz questions
   - Send invitations to students
   - Wait for quiz completion

2. **Scoring Workflow:**

   - Score quiz results
   - Notify top 5 students

3. **Video Processing Workflow:**
   - Process video submissions
   - Generate transcripts
   - Final ranking and winner notification

## Database Schema

The system uses Firebase Firestore with the following collections:

- `admins` - Admin users
- `students` - Student information
- `quizzes` - Quiz configurations
- `questions` - Quiz questions
- `quiz_invitations` - Quiz invitation tokens
- `quiz_answers` - Student answers
- `quiz_results` - Quiz results and rankings
- `video_submissions` - Video submissions
- `video_transcripts` - Video transcripts and analysis

## Testing

### Test the API

```bash
# Health check
curl http://localhost:8000/health

# Register admin
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "password": "password", "name": "Admin"}'

# Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@example.com&password=password"
```

### Test CrewAI Agents

```bash
# Test quiz generation
curl -X POST http://localhost:8000/api/workflow/quiz/{quiz_id}/run-complete-workflow \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Troubleshooting

### Common Issues

1. **Firebase Connection Error:**

   - Check service account file path
   - Verify Firebase project ID
   - Ensure Firestore is enabled

2. **LLM API Errors:**

   - Verify API keys are correct
   - Check API quotas and limits
   - Ensure internet connectivity

3. **Email Sending Issues:**

   - Check SMTP credentials
   - Verify SendGrid API key
   - Check email service quotas

4. **CrewAI Agent Errors:**
   - Check LLM service configuration
   - Verify agent dependencies
   - Review agent logs

### Logs

The application logs are available in the console. For production, consider using a logging service like Loggly or CloudWatch.

## Production Deployment

### Environment Variables for Production

```env
ENVIRONMENT=production
RELOAD=false
HOST=0.0.0.0
PORT=8000
```

### Security Considerations

- Use strong JWT secrets
- Implement rate limiting
- Use HTTPS in production
- Secure Firebase rules
- Monitor API usage

### Scaling

- Use Firebase auto-scaling
- Consider Redis for caching
- Implement load balancing
- Monitor performance metrics

## Support

For issues and questions:

1. Check the logs for error messages
2. Verify environment variables
3. Test individual components
4. Review Firebase console
5. Check API documentation at http://localhost:8000/docs
