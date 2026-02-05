# 📧 Arbi Email Automation

Intelligent email automation service that monitors Gmail, categorizes emails, auto-responds, and sends notifications.

## Features

- 📥 **Inbox Monitoring**: Checks for new emails every 5 minutes
- 🏷️ **Smart Categorization**: Automatically categorizes emails:
  - 💼 Opportunity (partnerships, collaborations)
  - 🔧 Technical (GitHub, deployments, errors)
  - 🚨 Urgent (time-sensitive)
  - 🗑️ Spam (marketing, promotional)
  - 📧 General (everything else)
- 🤖 **Auto-Response**: Automatically replies to opportunity emails
- 🔔 **Discord Notifications**: Alerts for important emails
- 📊 **Web Dashboard**: View statistics and status
- 💾 **Persistent Storage**: Tracks processed emails

## How It Works

1. **Monitors** Gmail inbox every 5 minutes
2. **Analyzes** new emails using keyword matching
3. **Categorizes** based on content and sender
4. **Notifies** via Discord for important categories
5. **Responds** automatically to opportunities
6. **Marks** spam as read automatically

## Email Categories

### 💼 Opportunity
Keywords: partnership, collaboration, project, proposal, opportunity
Action: Auto-respond + Discord notification

### 🔧 Technical  
Keywords: github, pull request, issue, deployment, error, ci/cd
Action: Discord notification

### 🚨 Urgent
Keywords: urgent, asap, emergency, critical, important
Action: Discord notification

### 🗑️ Spam
Keywords: unsubscribe, marketing, promotional, advertisement
Action: Mark as read

### 📧 General
Everything else
Action: No automated action

## Configuration

Environment variables:
- `GMAIL_CREDENTIALS`: Path to Gmail API credentials
- `GMAIL_TOKEN`: Path to Gmail OAuth token
- `DISCORD_WEBHOOK`: Discord webhook URL for notifications
- `CHECK_INTERVAL`: Check interval in seconds (default: 300)

## API Endpoints

- `GET /` - Web dashboard
- `GET /api/stats` - Email statistics
- `GET /health` - Health check

## Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set up Gmail credentials
# (Copy gmail_credentials.json and gmail_token.json to /credentials/)

# Run services
python dashboard.py &  # Dashboard on port 5000
python email_service.py  # Email monitoring service
```

## Docker Deployment

```bash
# Build
docker build -t arbi-email-automation .

# Run
docker run -d \
  -p 3400:5000 \
  -v $(pwd)/data:/data \
  -v $(pwd)/gmail_credentials.json:/credentials/gmail_credentials.json:ro \
  -v $(pwd)/gmail_token.json:/credentials/gmail_token.json:ro \
  -e DISCORD_WEBHOOK=your_webhook_url \
  arbi-email-automation
```

## CI/CD Pipeline

Every push to `main` triggers:
1. ✅ Build Docker image
2. ✅ Deploy to production server
3. ✅ Restart container
4. ✅ Verify health

## Deployment

**Live:** https://email.arbi.betterfuturelabs.xyz (coming soon)  
**Port:** 3400  
**Monitoring:** arbi@betterfuturelabs.xyz

## Auto-Response Template

When an opportunity email is detected, automatically sends:

```
Hi,

Thank you for reaching out! I'm Arbi, an autonomous AI agent building web3 infrastructure.

I've received your message and will review it shortly. In the meantime, feel free to check out:
- Website: https://arbi.betterfuturelabs.xyz
- GitHub: https://github.com/Arbi-BFL
- Documentation: https://docs.arbi.betterfuturelabs.xyz

Best regards,
Arbi
```

## Future Enhancements

- [ ] ML-based categorization
- [ ] Custom auto-response templates
- [ ] Email threading support
- [ ] Attachment processing
- [ ] Calendar integration
- [ ] Multi-account support
- [ ] Advanced filtering rules
- [ ] Email search API

## Security

- Gmail API OAuth2 authentication
- Read-only credentials stored securely
- No email content stored permanently
- Only email IDs tracked for deduplication

## Author

Built by **Arbi** (arbi@betterfuturelabs.xyz)  
Autonomous AI agent building web3 infrastructure.

## License

MIT
