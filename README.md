# CrewAI Quiz System Backend

A comprehensive backend system for automated quiz generation, student management, and video evaluation using CrewAI agents and Firebase.

## 🚀 Quick Start

1. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment:**

   ```bash
   cp env.example .env
   # Edit .env with your actual values
   ```

3. **Run setup:**

   ```bash
   python setup.py
   ```

4. **Start the server:**
   ```bash
   python start.py
   ```

## 📋 Features

- **Automated Quiz Generation** using LLM (Gemini/Groq)
- **Student Management** with Excel import
- **Email Notifications** with personalized content
- **Video Processing** with YouTube transcript extraction
- **AI-Powered Evaluation** using CrewAI agents
- **Firebase Integration** for scalable data storage
- **RESTful API** with comprehensive documentation

## 🏗️ Architecture

### Core Components

- **FastAPI** - Modern Python web framework
- **Firebase Firestore** - NoSQL database
- **CrewAI** - AI agent orchestration
- **Google Gemini** - Primary LLM provider
- **Groq** - Alternative LLM provider
- **SendGrid/SMTP** - Email services

### CrewAI Agents

1. **QuizGeneratorAgent** - Generates quiz questions
2. **SendInvitationsAgent** - Sends personalized emails
3. **ScoreAndNotifyAgent** - Scores quizzes and notifies students
4. **ProcessVideoAgent** - Processes video submissions
5. **FinalVideoRankingAgent** - Ranks videos and notifies winners

### API Endpoints

- **Authentication** - Admin registration and login
- **Admin Management** - Student and quiz management
- **Quiz System** - Quiz taking and submission
- **Video System** - Video submission and processing
- **Workflow Management** - Automated workflow execution

## 📁 Project Structure

```
backend/
├── app/
│   ├── agents/           # CrewAI agents
│   ├── api/             # API endpoints
│   ├── config/          # Configuration
│   ├── models/          # Data models
│   ├── services/        # Business logic
│   ├── workflows/       # Workflow orchestration
│   ├── database.py      # Database configuration
│   └── main.py          # FastAPI application
├── requirements.txt     # Python dependencies
├── env.example         # Environment variables template
├── setup.py            # Setup script
├── start.py            # Startup script
├── test_backend.py     # Test script
└── README.md           # This file
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# Firebase Configuration
FIREBASE_CREDENTIALS_PATH=path/to/firebase-service-account.json

# LLM API Keys
GOOGLE_API_KEY=your_google_api_key
GROQ_API_KEY=your_groq_api_key

# JWT Configuration
JWT_SECRET=your_jwt_secret

# Email Configuration
SENDGRID_API_KEY=your_sendgrid_api_key
# OR SMTP settings
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password

# Server Configuration
HOST=0.0.0.0
PORT=8000
FRONTEND_URL=http://localhost:3000
```

### Firebase Setup

1. Create a Firebase project
2. Enable Firestore Database
3. Generate service account key
4. Download JSON file and update `.env`

## 🚀 Running the Backend

### Development Mode

```bash
python start.py
```

### Production Mode

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Using Docker

```bash
docker build -t crewai-quiz-backend .
docker run -p 8000:8000 crewai-quiz-backend
```

## 📚 API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## 🧪 Testing

### Run Tests

```bash
python test_backend.py
```

### Test API Endpoints

```bash
# Health check
curl http://localhost:8000/health

# Register admin
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "password": "password", "name": "Admin"}'
```

## 🔄 Workflows

### Complete Quiz Workflow

1. Generate quiz questions using LLM
2. Send personalized invitations to students
3. Wait for quiz completion
4. Score results and notify top students
5. Process video submissions
6. Rank videos and notify winners

### API Usage Example

```python
import requests

# Register and login
response = requests.post('http://localhost:8000/api/auth/register', json={
    'email': 'admin@example.com',
    'password': 'password',
    'name': 'Admin'
})

response = requests.post('http://localhost:8000/api/auth/login', data={
    'username': 'admin@example.com',
    'password': 'password'
})
token = response.json()['access_token']

# Create quiz and run workflow
headers = {'Authorization': f'Bearer {token}'}
response = requests.post('http://localhost:8000/api/admin/create-quiz',
                        json={'title': 'Python Quiz', 'topic': 'Python'},
                        headers=headers)

# Run automated workflow
response = requests.post(f'http://localhost:8000/api/workflow/quiz/{quiz_id}/run-automated-workflow',
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

- `admins` - Admin users
- `students` - Student information
- `quizzes` - Quiz configurations
- `questions` - Quiz questions
- `quiz_invitations` - Invitation tokens
- `quiz_answers` - Student answers
- `quiz_results` - Quiz results
- `video_submissions` - Video submissions
- `video_transcripts` - Video transcripts

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
python start.py
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
