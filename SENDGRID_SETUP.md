# SendGrid Setup Guide

## 1. Create SendGrid Account

1. Go to https://sendgrid.com/
2. Sign up for a free account
3. Verify your email address

## 2. Get API Key

1. Go to Settings → API Keys
2. Click "Create API Key"
3. Choose "Restricted Access"
4. Give it a name like "CrewAI Quiz System"
5. Enable "Mail Send" permissions
6. Copy the API key (starts with SG.)

## 3. Configure Environment Variables

Create a `.env` file in the backend directory with:

```bash
# Email Configuration (SendGrid)
SENDGRID_API_KEY=SG.your_actual_api_key_here
SMTP_FROM_EMAIL=noreply@yourdomain.com

# Frontend URL
FRONTEND_URL=http://localhost:3000

# Other required variables...
GROQ_API_KEY=your_groq_api_key
JWT_SECRET=your_jwt_secret
```

## 4. Test SendGrid

Run the test script to verify SendGrid is working:

```bash
python test_sendgrid.py
```

## 5. Production Setup

- Use a custom domain for better deliverability
- Set up domain authentication in SendGrid
- Configure SPF, DKIM, and DMARC records
