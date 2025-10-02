# Brevo Email Service Setup Guide

## Overview

Brevo (formerly Sendinblue) is a powerful email service provider that offers excellent deliverability and analytics. This guide will help you set up Brevo for your CrewAI Quiz System.

## Why Choose Brevo?

- ✅ **High Deliverability**: Better inbox placement than SMTP
- ✅ **Free Tier**: 300 emails/day for free
- ✅ **Analytics**: Track email opens, clicks, and bounces
- ✅ **Reliability**: 99.9% uptime guarantee
- ✅ **Easy Integration**: Simple REST API
- ✅ **Template Management**: Create and manage email templates

## Step-by-Step Setup

### 1. Create Brevo Account

1. Visit [Brevo.com](https://www.brevo.com)
2. Click "Sign up for free"
3. Enter your email and create a password
4. Verify your email address

### 2. Get Your API Key

1. Log in to your Brevo dashboard
2. Go to **Settings** → **API Keys**
3. Click **"Create a new API key"**
4. Give it a name (e.g., "Quiz System")
5. Copy the API key (starts with `xkeys-`)

### 3. Verify Your Sender Email

1. Go to **Senders & IP** → **Senders**
2. Click **"Add a new sender"**
3. Enter your email address
4. Check your email and click the verification link
5. Your sender is now verified

### 4. Configure Environment Variables

Create or update your `.env` file:

```bash
# Brevo Configuration
BREVO_API_KEY=xkeys-your-api-key-here
SMTP_FROM_EMAIL=your-verified-email@domain.com

# Frontend URL
FRONTEND_URL=http://localhost:3000
```

### 5. Test the Integration

Run the Brevo test script:

```bash
cd backend
python test_brevo_email.py
```

## Email Service Priority

The system automatically selects the best available email service:

1. **Brevo** (if `BREVO_API_KEY` is set)
2. **SendGrid** (if `SENDGRID_API_KEY` is set)
3. **SMTP** (fallback)

## Brevo API Features

### Email Sending

- Send transactional emails
- HTML and text content support
- Personalized recipient names
- Delivery tracking

### Analytics

- Open rates
- Click rates
- Bounce rates
- Unsubscribe rates

### Templates

- Create reusable email templates
- Dynamic content insertion
- A/B testing support

## Configuration Examples

### Basic Configuration

```bash
BREVO_API_KEY=xkeys-abc123def456
SMTP_FROM_EMAIL=noreply@yourdomain.com
```

### With Custom Sender Name

```python
# In your email service, you can customize the sender name
payload = {
    "sender": {
        "name": "Your Quiz System",
        "email": self.from_email
    },
    # ... rest of the payload
}
```

## Troubleshooting

### Common Issues

1. **"Invalid API Key" Error**

   - Verify your API key is correct
   - Check if the key has proper permissions
   - Ensure the key is not expired

2. **"Sender not verified" Error**

   - Verify your sender email in Brevo dashboard
   - Check spam folder for verification email
   - Try a different sender email

3. **"Rate limit exceeded" Error**
   - Check your Brevo plan limits
   - Implement rate limiting in your code
   - Consider upgrading your plan

### Debug Logging

The system includes comprehensive logging:

```python
print(f"📧 Brevo: Sending email to {to_email}")
print(f"✅ Brevo: Email sent successfully to {to_email}")
print(f"❌ Brevo: Failed to send email. Status: {response.status_code}")
```

## Best Practices

### 1. Email Content

- Use clear, engaging subject lines
- Include both HTML and text versions
- Test emails before sending to all users
- Respect unsubscribe requests

### 2. Sending Limits

- Stay within your plan's daily limits
- Implement proper error handling
- Use batch sending for large volumes
- Monitor your sending reputation

### 3. Security

- Keep your API key secure
- Use environment variables
- Don't commit API keys to version control
- Regularly rotate your API keys

## Monitoring and Analytics

### Brevo Dashboard

- Track email performance
- Monitor bounce rates
- View delivery statistics
- Manage your sender reputation

### Custom Analytics

You can extend the system to track:

- Email open rates
- Click-through rates
- Quiz completion rates
- Student engagement metrics

## Advanced Features

### Template Management

```python
# Use Brevo templates
payload = {
    "templateId": 1,
    "to": [{"email": to_email, "name": student_name}],
    "params": {
        "quiz_title": quiz_title,
        "student_name": student_name,
        "quiz_link": quiz_link
    }
}
```

### Batch Sending

```python
# Send to multiple recipients
payload = {
    "to": [
        {"email": "student1@example.com", "name": "Student 1"},
        {"email": "student2@example.com", "name": "Student 2"}
    ],
    # ... rest of payload
}
```

## Support and Resources

### Brevo Documentation

- [Brevo API Documentation](https://developers.brevo.com/)
- [Email API Reference](https://developers.brevo.com/reference/sendtransacemail)
- [Best Practices Guide](https://developers.brevo.com/docs/best-practices)

### System Support

- Check the logs for detailed error messages
- Test with the provided test script
- Verify your configuration settings
- Contact Brevo support for API issues

## Migration from Other Services

### From SMTP

1. Set up Brevo account
2. Add `BREVO_API_KEY` to environment
3. Remove SMTP configuration
4. Test email sending

### From SendGrid

1. Keep both API keys during transition
2. Brevo will be used automatically (higher priority)
3. Remove SendGrid configuration when ready
4. Update any SendGrid-specific code

## Cost Optimization

### Free Tier Limits

- 300 emails per day
- Unlimited contacts
- Basic analytics
- Email support

### Paid Plans

- Higher sending limits
- Advanced analytics
- Priority support
- Custom domains

## Security Considerations

1. **API Key Security**

   - Store in environment variables
   - Use different keys for different environments
   - Regularly rotate keys
   - Monitor API usage

2. **Email Security**

   - Verify all sender addresses
   - Use SPF, DKIM, and DMARC records
   - Monitor for abuse
   - Implement rate limiting

3. **Data Protection**
   - Comply with GDPR/CCPA
   - Secure data transmission
   - Regular security audits
   - User consent management

The Brevo integration provides a robust, scalable, and reliable email solution for your CrewAI Quiz System. With proper setup and monitoring, it will significantly improve your email deliverability and provide valuable insights into student engagement.
