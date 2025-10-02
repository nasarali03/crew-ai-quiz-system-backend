# Quiz Invitation System Guide

## Overview

The invitation system allows administrators to send personalized quiz invitations to students via email. The system uses CrewAI agents to generate personalized email content and integrates with email services (SendGrid/SMTP) for delivery.

## System Architecture

### Backend Components

1. **SendInvitationsAgent** (`app/agents/send_invitations.py`)

   - CrewAI agent that generates personalized email content
   - Creates unique tokens for each student
   - Sends emails using EmailService

2. **EmailService** (`app/services/email_service.py`)

   - Supports both SendGrid and SMTP email delivery
   - Handles email formatting and sending

3. **AdminService** (`app/services/admin_service.py`)

   - Manages invitation operations
   - Handles invitation status tracking
   - Provides invitation management functions

4. **FirebaseService** (`app/services/firebase_service.py`)
   - Database operations for invitations
   - Student and quiz data management

### Frontend Components

1. **Invitations Page** (`frontend/app/admin/invitations/page.tsx`)

   - Admin dashboard for managing invitations
   - View invitation status and statistics
   - Send new invitations and resend existing ones

2. **API Routes** (`frontend/app/api/admin/invitations/`)
   - Frontend API endpoints for invitation operations
   - Proxy requests to backend services

## API Endpoints

### Backend Endpoints

- `GET /api/admin/invitations` - Get all invitations
- `GET /api/admin/quiz/{quiz_id}/invitations` - Get invitations for specific quiz
- `POST /api/admin/quiz/{quiz_id}/send-invitations` - Send invitations for quiz
- `POST /api/admin/invitations/{invitation_id}/resend` - Resend specific invitation
- `PUT /api/admin/invitations/{invitation_id}/mark-used` - Mark invitation as used

### Frontend Endpoints

- `GET /api/admin/invitations` - Fetch invitations for admin dashboard
- `POST /api/admin/invitations` - Send new invitations
- `POST /api/admin/invitations/{id}/resend` - Resend invitation

## Database Schema

### QuizInvitation Model

```typescript
{
  id: string
  token: string (unique)
  isUsed: boolean
  sentAt: DateTime?
  createdAt: DateTime
  updatedAt: DateTime
  quizId: string
  studentId: string
  quiz: Quiz (relation)
  student: Student (relation)
  quizAnswers: QuizAnswer[] (relation)
}
```

## Workflow

### 1. Creating Invitations

1. Admin creates a quiz
2. Admin generates quiz questions
3. Admin triggers invitation sending
4. System creates unique tokens for each student
5. CrewAI generates personalized email content
6. Emails are sent via EmailService

### 2. Invitation Management

1. Admin can view all invitations in dashboard
2. Admin can see invitation status (pending/used)
3. Admin can resend invitations
4. System tracks invitation usage

### 3. Student Experience

1. Student receives personalized email
2. Student clicks quiz link with unique token
3. Student takes quiz
4. System marks invitation as used

## Configuration

### Environment Variables

```bash
# Email Configuration (Priority: Brevo > SendGrid > SMTP)

# Brevo (Recommended - Priority 1)
BREVO_API_KEY=your-brevo-api-key
SMTP_FROM_EMAIL=your-verified-email@domain.com

# SendGrid (Alternative - Priority 2)
SENDGRID_API_KEY=your-sendgrid-api-key
SMTP_FROM_EMAIL=your-verified-email@domain.com

# SMTP (Fallback - Priority 3)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=your-email@gmail.com

# Frontend URL
FRONTEND_URL=http://localhost:3000
```

### Brevo Setup

1. **Create Brevo Account**

   - Visit [Brevo.com](https://www.brevo.com)
   - Sign up for a free account
   - Verify your email address

2. **Get API Key**

   - Go to Settings > API Keys
   - Create a new API key
   - Copy the API key

3. **Verify Sender Email**

   - Go to Senders & IP > Senders
   - Add and verify your sender email
   - This email will be used as the "from" address

4. **Configure Environment**
   ```bash
   BREVO_API_KEY=xkeys-your-api-key-here
   SMTP_FROM_EMAIL=your-verified-email@domain.com
   ```

### Email Templates

The system uses CrewAI to generate personalized email content. The agent creates:

- Personalized subject lines
- Engaging email body content
- Clear instructions for taking the quiz
- Professional yet friendly tone

## Usage Examples

### Sending Invitations

```python
# Backend
admin_service = AdminService(db)
result = await admin_service.send_quiz_invitations(quiz_id, admin_id)
```

```javascript
// Frontend
const response = await fetch("/api/admin/invitations", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ quiz_id: "quiz-123" }),
});
```

### Managing Invitations

```python
# Get all invitations
invitations = await admin_service.get_all_invitations(admin_id)

# Get invitations for specific quiz
quiz_invitations = await admin_service.get_invitations_by_quiz(quiz_id, admin_id)

# Resend invitation
success = await admin_service.resend_invitation(invitation_id, admin_id)

# Mark as used
success = await admin_service.mark_invitation_as_used(invitation_id, admin_id)
```

## Testing

### Run the Test Suite

```bash
cd backend
python test_invitation_workflow.py
```

### Manual Testing

1. Start backend: `python run.py`
2. Start frontend: `cd frontend && npm run dev`
3. Visit: `http://localhost:3000/admin/invitations`
4. Create a quiz and send invitations
5. Verify emails are received
6. Test invitation management features

## Troubleshooting

### Common Issues

1. **Emails not sending**

   - Check SMTP/SendGrid configuration
   - Verify email credentials
   - Check firewall settings

2. **Invitations not appearing**

   - Verify database connection
   - Check Firebase configuration
   - Ensure students exist

3. **CrewAI errors**
   - Check Groq API key
   - Verify CrewAI configuration
   - Check network connectivity

### Debug Logging

The system includes comprehensive logging:

```python
print(f"🔍 AdminService: Fetching invitations for admin: {admin_id}")
print(f"✅ AdminService: Retrieved {len(invitations)} invitations")
print(f"❌ AdminService: Error getting invitations: {str(e)}")
```

## Security Considerations

1. **Token Security**

   - Tokens are cryptographically secure
   - Tokens are unique per student/quiz combination
   - Tokens expire when quiz is completed

2. **Access Control**

   - Only quiz owners can manage invitations
   - Admin authentication required
   - Student data protection

3. **Email Security**
   - No sensitive data in email content
   - Secure email delivery
   - Spam prevention measures

## Performance Optimization

1. **Batch Processing**

   - Invitations sent in batches
   - Async email processing
   - Rate limiting for email services

2. **Caching**

   - Student data caching
   - Quiz data caching
   - Invitation status caching

3. **Database Optimization**
   - Indexed queries
   - Efficient data retrieval
   - Connection pooling

## Future Enhancements

1. **Email Templates**

   - Customizable email templates
   - Multiple language support
   - Rich HTML emails

2. **Analytics**

   - Invitation open rates
   - Click-through rates
   - Student engagement metrics

3. **Advanced Features**
   - Scheduled invitations
   - Reminder emails
   - Bulk invitation management

## Support

For issues or questions:

1. Check the logs for error messages
2. Verify configuration settings
3. Test with the provided test suite
4. Review the API documentation

The invitation system is designed to be robust, scalable, and user-friendly. It integrates seamlessly with the existing CrewAI quiz system and provides comprehensive invitation management capabilities.
