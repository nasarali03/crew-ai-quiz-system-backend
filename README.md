# CrewAI Quiz System Backend

A comprehensive backend system for automated quiz generation, student management, and invitation-based quiz taking using CrewAI agents and Firebase.

## 🚀 Quick Start

1. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment:**

   Create a `.env` file with your configuration (see Environment Variables section)

3. **Start the server:**

   ```bash
   python run.py
   ```

   Or for development:

   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

## 📋 Features

- **Automated Quiz Generation** using CrewAI agents with Groq LLM
- **Student Management** with Excel import/export
- **Invitation-Based Quiz System** with unique tokens and snapshots
- **Email Notifications** with personalized content via Mailtrap/Gmail SMTP
- **Quiz Version Control** - each invitation preserves quiz/questions at send time
- **Real-time Results** with comprehensive analytics
- **Firebase Integration** for scalable data storage
- **RESTful API** with comprehensive documentation
- **Admin Dashboard Integration** for complete management

## 🏗️ Architecture

### Core Components

- **FastAPI** - Modern Python web framework
- **Firebase Firestore** - NoSQL database with real-time capabilities
- **CrewAI** - AI agent orchestration framework
- **Groq LLM** - Primary language model provider
- **Mailtrap/Gmail SMTP** - Email delivery services
- **JWT Authentication** - Secure admin authentication

### CrewAI Agents

1. **QuizGeneratorAgent** - Generates quiz questions using Groq LLM
2. **EmailGeneratorAgent** - Creates personalized email templates
3. **SendInvitationsAgent** - Orchestrates invitation sending with quiz snapshots
4. **ProcessVideoAgent** - Processes video submissions (future feature)
5. **FinalVideoRankingAgent** - Ranks videos and notifies winners (future feature)

### API Endpoints

- **Authentication** (`/api/auth/`) - Admin registration and login
- **Admin Management** (`/api/admin/`) - Student and quiz management, results
- **Quiz System** (`/api/quiz/`) - Token-based quiz access and submission
- **Simple Quiz** (`/api/simple-quiz/`) - Alternative quiz interface
- **Video System** (`/api/video/`) - Video submission and processing (future)

## 📁 Project Structure

```
backend/
├── app/
│   ├── agents/           # CrewAI agents
│   │   ├── quiz_generator.py
│   │   ├── email_generator.py
│   │   └── send_invitations.py
│   ├── api/             # API endpoints
│   │   ├── auth.py      # Authentication
│   │   ├── admin.py     # Admin management
│   │   ├── quiz.py      # Quiz system
│   │   └── video.py     # Video system
│   ├── config/          # Configuration
│   │   ├── crewai_config.py
│   │   └── llm_config.py
│   ├── models/          # Data models and schemas
│   │   └── schemas.py
│   ├── services/        # Business logic
│   │   ├── firebase_service.py
│   │   ├── quiz_service.py
│   │   ├── email_service.py
│   │   └── auth_service.py
│   ├── utils/           # Utility functions
│   ├── workflows/       # Workflow orchestration
│   ├── database.py      # Database configuration
│   ├── main.py          # FastAPI application
│   └── serviceAccountKey.json  # Firebase credentials (local only)
├── requirements.txt     # Python dependencies
├── run.py              # Application runner
└── README.md           # This file
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# Firebase Configuration (choose one method)
# Method 1: Service account file (local development)
FIREBASE_CREDENTIALS_PATH=app/serviceAccountKey.json

# Method 2: Complete JSON (recommended for deployment)
FIREBASE_CREDENTIALS_JSON={"type":"service_account","project_id":"..."}

# Method 3: Individual variables (alternative for deployment)
FIREBASE_PROJECT_ID=your_project_id
FIREBASE_PRIVATE_KEY=-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n
FIREBASE_CLIENT_EMAIL=firebase-adminsdk-xxx@your-project.iam.gserviceaccount.com
FIREBASE_CLIENT_ID=your_client_id

# LLM Configuration
GROQ_API_KEY=your_groq_api_key

# JWT Configuration
JWT_SECRET_KEY=your_jwt_secret_key
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=1440

# Email Configuration (choose one)
# Mailtrap (recommended for testing)
SMTP_HOST=sandbox.smtp.mailtrap.io
SMTP_PORT=587
SMTP_USERNAME=your_mailtrap_username
SMTP_PASSWORD=your_mailtrap_password
SMTP_FROM_EMAIL=noreply@quizsystem.com

# Gmail SMTP (alternative)
# SMTP_HOST=smtp.gmail.com
# SMTP_PORT=587
# SMTP_USERNAME=your_email@gmail.com
# SMTP_PASSWORD=your_app_password

# SendGrid (alternative)
# SENDGRID_API_KEY=your_sendgrid_api_key

# Server Configuration
FRONTEND_URL=http://localhost:3000
```

### Firebase Setup

1. Create a Firebase project
2. Enable Firestore Database
3. Generate service account key
4. Download JSON file and update `.env`

## 🚀 Deployment

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment
# Create .env file with your configuration

# Run the server
python run.py
```

### Vercel Deployment

1. **Set Root Directory**: `backend/`
2. **Build Command**: `pip install -r requirements.txt`
3. **Output Directory**: Leave empty
4. **Install Command**: `pip install -r requirements.txt`
5. **Development Command**: `python run.py`

**Environment Variables for Vercel:**

```env
FIREBASE_CREDENTIALS_JSON={"type":"service_account",...}
GROQ_API_KEY=your_groq_api_key
JWT_SECRET_KEY=your_jwt_secret
SMTP_HOST=sandbox.smtp.mailtrap.io
SMTP_PORT=587
SMTP_USERNAME=your_mailtrap_username
SMTP_PASSWORD=your_mailtrap_password
SMTP_FROM_EMAIL=noreply@quizsystem.com
FRONTEND_URL=https://your-frontend-domain.vercel.app
```

### Production Mode (Manual)

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## 📚 API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

### Test API Endpoints

```bash
# Health check
curl http://localhost:8000/health

# Register admin
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "password": "password", "name": "Admin"}'
```

## 🔄 Quiz Workflow

### Complete Quiz Process

1. **Admin Setup**

   - Register/Login as admin
   - Upload students via Excel file
   - Create quiz with topic and settings

2. **Question Generation**

   - Generate questions using CrewAI + Groq LLM
   - Questions are stored in Firebase
   - Preview and edit questions if needed

3. **Invitation Process**

   - Send invitations creates quiz/questions snapshots
   - Each invitation gets unique token
   - Personalized emails sent via Mailtrap/Gmail
   - 10-second delay between emails to avoid rate limits

4. **Student Quiz Taking**

   - Students click unique link from email
   - Quiz loads from invitation snapshot (version control)
   - Timed questions with progress tracking
   - Answers submitted and scored

5. **Results & Analytics**
   - Real-time results in admin dashboard
   - Student performance analytics
   - Export capabilities for further analysis

### API Usage Example

```python
import requests

BASE_URL = "http://localhost:8000"

# 1. Register and login
response = requests.post(f'{BASE_URL}/api/auth/register', json={
    'email': 'admin@example.com',
    'password': 'password123',
    'name': 'Admin User'
})

login_response = requests.post(f'{BASE_URL}/api/auth/login', data={
    'username': 'admin@example.com',
    'password': 'password123'
})
token = login_response.json()['access_token']
headers = {'Authorization': f'Bearer {token}'}

# 2. Create quiz
quiz_response = requests.post(f'{BASE_URL}/api/admin/create-quiz', json={
    'title': 'Python Fundamentals',
    'description': 'Basic Python programming concepts',
    'topic': 'Python Programming',
    'difficulty': 'medium',
    'time_per_question': 60,
    'total_questions': 10
}, headers=headers)
quiz_id = quiz_response.json()['id']

# 3. Generate questions
requests.post(f'{BASE_URL}/api/admin/quiz/{quiz_id}/generate-questions',
              headers=headers)

# 4. Send invitations (creates snapshots)
requests.post(f'{BASE_URL}/api/admin/quiz/{quiz_id}/send-invitations',
              headers=headers)

# 5. Get results
results = requests.get(f'{BASE_URL}/api/admin/quiz/{quiz_id}/results',
                      headers=headers)
```

## 🛠️ Development

### Adding New Agents

1. Create agent file in `app/agents/`
2. Implement agent class with required methods
3. Add to workflow in `app/workflows/`
4. Update API endpoints if needed

### Adding New API Endpoints

1. Create endpoint file in `app/api/`
2. Implement router with endpoints
3. Add to main app in `app/main.py`
4. Update documentation

### Database Schema

The system uses Firebase Firestore with these collections:

#### Core Collections

- **`admins`** - Admin user accounts with authentication
- **`students`** - Student information imported from Excel
- **`quizzes`** - Quiz configurations and metadata
- **`questions`** - Generated quiz questions with answers
- **`quiz_invitations`** - Enhanced invitations with snapshots
  ```json
  {
    "quiz_id": "quiz-uuid",
    "student_id": "student-uuid",
    "token": "unique-token",
    "is_used": false,
    "quiz_snapshot": {
      /* complete quiz data */
    },
    "questions_snapshot": [
      /* all questions */
    ],
    "invitation_created_at": "2024-01-01T00:00:00Z"
  }
  ```
- **`quiz_answers`** - Individual student answers
- **`quiz_results`** - Calculated quiz results and scores

#### Future Collections

- **`video_submissions`** - Video submissions (planned feature)
- **`video_transcripts`** - Video transcripts (planned feature)

## 🚨 Troubleshooting

### Common Issues

1. **Firebase Connection Error**

   - Check service account file path
   - Verify Firebase project ID
   - Ensure Firestore is enabled

2. **LLM API Errors**

   - Verify API keys are correct
   - Check API quotas and limits
   - Ensure internet connectivity

3. **Email Sending Issues**

   - Check SMTP credentials
   - Verify SendGrid API key
   - Check email service quotas

4. **CrewAI Agent Errors**
   - Check LLM service configuration
   - Verify agent dependencies
   - Review agent logs

### Debug Mode

Set environment variable for debug logging:

```bash
export DEBUG=true
python run.py
```

## 📖 Documentation

- [Backend Setup Guide](BACKEND_SETUP.md)
- [API Documentation](API_DOCUMENTATION.md)
- [CrewAI Documentation](https://docs.crewai.com/)
- [Firebase Documentation](https://firebase.google.com/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:

1. Check the documentation
2. Review the logs
3. Test individual components
4. Check Firebase console
5. Contact the development team

## 🎯 Roadmap

- [ ] Real-time notifications with WebSockets
- [ ] Advanced analytics dashboard
- [ ] Multi-language support
- [ ] Mobile app integration
- [ ] Advanced AI features
- [ ] Performance optimizations
- [ ] Security enhancements
- [ ] Monitoring and logging
