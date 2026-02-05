# Arbi Email Automation Service

Autonomous email monitoring, categorization, and response system for arbi@betterfuturelabs.xyz

## Features

- 📬 **Inbox Monitoring**: Checks for new emails every 5 minutes (configurable)
- 🏷️ **Smart Categorization**: Automatically categorizes emails by content
  - Urgent (immediate attention required)
  - Partnership (collaboration opportunities)
  - Technical (bugs, issues, code)
  - Business (invoices, contracts, proposals)
  - Community (newsletters, events)
  - Spam (marketing, promotions)
- 🤖 **Auto-Responses**: Sends automated replies for specific categories
- 📊 **Discord Notifications**: Posts alerts for important emails
- 💾 **Persistent State**: Remembers processed emails across restarts

## Email Categories

### Urgent (Priority 1)
- **Keywords**: urgent, asap, emergency, critical, immediately, time-sensitive
- **Auto-response**: ✓
- **Discord alert**: ✓
- **Mark as read**: ✗ (keeps as unread)

### Partnership (Priority 2)
- **Keywords**: partnership, collaboration, collaborate, work together, joint venture
- **Auto-response**: ✓
- **Discord alert**: ✓
- **Mark as read**: ✗

### Technical (Priority 2)
- **Keywords**: bug, error, issue, problem, technical, deploy, code, github
- **Auto-response**: ✗ (manual review needed)
- **Discord alert**: ✓
- **Mark as read**: ✗

### Business (Priority 2)
- **Keywords**: invoice, payment, contract, agreement, proposal, quote
- **Auto-response**: ✓
- **Discord alert**: ✓
- **Mark as read**: ✗

### Community (Priority 3)
- **Keywords**: newsletter, community, event, meetup, announcement
- **Auto-response**: ✗
- **Discord alert**: ✗
- **Mark as read**: ✓

### Spam (Priority 4)
- **Keywords**: unsubscribe, marketing, promotion, discount, free trial
- **Auto-response**: ✗
- **Discord alert**: ✗
- **Mark as read**: ✓

## Configuration

### Environment Variables

- `GMAIL_CREDENTIALS_PATH`: Path to Gmail API credentials (default: `/root/.openclaw/workspace/gmail_credentials.json`)
- `GMAIL_TOKEN_PATH`: Path to Gmail OAuth token (default: `/root/.openclaw/workspace/gmail_token.json`)
- `DISCORD_WEBHOOK_URL`: Discord webhook URL for notifications (required for Discord alerts)
- `CHECK_INTERVAL`: Seconds between email checks (default: 300 = 5 minutes)

### Discord Webhook Setup

1. Go to Discord channel settings
2. Integrations → Webhooks → New Webhook
3. Copy webhook URL
4. Set as `DISCORD_WEBHOOK_URL` environment variable

## Deployment

### GitHub Secrets Required

- `SERVER_HOST`: Server IP address
- `SERVER_USER`: SSH username
- `SSH_PRIVATE_KEY`: SSH private key for deployment
- `DISCORD_WEBHOOK_URL`: Discord webhook URL

### Auto-Deploy

```bash
git push origin main
```

GitHub Actions will automatically:
1. Build Docker image
2. Push to GHCR
3. Deploy to server
4. Start service

### Manual Deploy

```bash
docker-compose up -d
```

## Monitoring

### View Logs
```bash
docker logs -f arbi-email-automation
```

### Check Health
```bash
docker exec arbi-email-automation python healthcheck.py
```

### State File
The service maintains state in `/data/email_state.json`:
- `processed_emails`: List of processed email IDs (prevents duplicates)
- `last_check_time`: Timestamp of last inbox check

## Development

### Local Testing
```bash
python email_service.py
```

### Requirements
- Python 3.11+
- Gmail API credentials
- Discord webhook (optional)

## Architecture

```
┌─────────────────┐
│  Gmail Inbox    │
│  arbi@bfl.xyz   │
└────────┬────────┘
         │
         ↓ Check every 5 min
┌─────────────────┐
│ Email Service   │
│  - Categorize   │
│  - Respond      │
│  - Notify       │
└────────┬────────┘
         │
         ├─→ Discord Webhook (alerts)
         └─→ Gmail API (auto-responses)
```

## Customization

Edit `CATEGORIES` dict in `email_service.py` to:
- Add new categories
- Modify keywords
- Change auto-response messages
- Adjust notification settings

## Security

- Gmail credentials stored as read-only volume mounts
- OAuth tokens automatically refreshed
- State file persisted in `/data` volume
- No credentials in git repository

## Future Enhancements

- [ ] Web dashboard for email analytics
- [ ] Machine learning categorization
- [ ] Custom rules engine
- [ ] Multiple email account support
- [ ] Slack/Telegram integration
- [ ] Email templates
- [ ] Scheduled summaries

---

**Part of Arbi's autonomous infrastructure**
Built with ❤️ by Arbi (@Arbi_BFL)
