#!/usr/bin/env python3
"""
Arbi Email Automation Service
Monitors Gmail inbox, categorizes emails, sends auto-responses, and posts to Discord
"""

import os
import json
import time
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import re

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import discord
from discord import Webhook
import aiohttp

# Configuration
CREDENTIALS_PATH = os.environ.get('GMAIL_CREDENTIALS_PATH', '/root/.openclaw/workspace/gmail_credentials.json')
TOKEN_PATH = os.environ.get('GMAIL_TOKEN_PATH', '/root/.openclaw/workspace/gmail_token.json')
DISCORD_WEBHOOK_URL = os.environ.get('DISCORD_WEBHOOK_URL', '')
CHECK_INTERVAL = int(os.environ.get('CHECK_INTERVAL', '300'))  # 5 minutes default
STATE_FILE = '/data/email_state.json'

# Copy token to writable location if it doesn't exist
if not os.path.exists(TOKEN_PATH) and os.path.exists(TOKEN_PATH_READONLY):
    import shutil
    shutil.copy2(TOKEN_PATH_READONLY, TOKEN_PATH)
    print(f'✓ Copied token to writable location: {TOKEN_PATH}')
STATS_FILE = '/data/email_stats.json'

# Email categories
CATEGORIES = {
    'urgent': {
        'keywords': ['urgent', 'asap', 'emergency', 'critical', 'immediately', 'time-sensitive'],
        'priority': 1,
        'notify_discord': True,
        'auto_response': "Thank you for your urgent message. I've been notified and will respond as soon as possible."
    },
    'partnership': {
        'keywords': ['partnership', 'collaboration', 'collaborate', 'work together', 'joint venture'],
        'priority': 2,
        'notify_discord': True,
        'auto_response': "Thank you for reaching out about a potential partnership. I'm interested in exploring collaboration opportunities. I'll review your proposal and get back to you within 24-48 hours."
    },
    'technical': {
        'keywords': ['bug', 'error', 'issue', 'problem', 'technical', 'deploy', 'code', 'github'],
        'priority': 2,
        'notify_discord': True,
        'auto_response': None  # No auto-response for technical issues
    },
    'business': {
        'keywords': ['invoice', 'payment', 'contract', 'agreement', 'proposal', 'quote'],
        'priority': 2,
        'notify_discord': True,
        'auto_response': "Thank you for your business inquiry. I'll review the details and respond within 48 hours."
    },
    'community': {
        'keywords': ['newsletter', 'community', 'event', 'meetup', 'announcement'],
        'priority': 3,
        'notify_discord': False,
        'auto_response': None
    },
    'spam': {
        'keywords': ['unsubscribe', 'marketing', 'promotion', 'discount', 'free trial'],
        'priority': 4,
        'notify_discord': False,
        'auto_response': None
    }
}


class EmailAutomationService:
    def __init__(self):
        self.gmail_service = None
        self.discord_session = None
        self.state = self.load_state()
        self.stats = self.load_stats()
        self.last_check_time = self.state.get('last_check_time', datetime.now().isoformat())
        
    def load_state(self) -> Dict:
        """Load persistent state from file"""
        if os.path.exists(STATE_FILE):
            try:
                with open(STATE_FILE, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading state: {e}")
        return {'processed_emails': [], 'last_check_time': None}
    
    def save_state(self):
        """Save state to file"""
        try:
            os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
            with open(STATE_FILE, 'w') as f:
                json.dump(self.state, f, indent=2)
            print(f"✓ State saved: {len(self.state.get('processed_emails', []))} processed emails")
        except Exception as e:
            print(f"Error saving state: {e}")
    
    def load_stats(self) -> Dict:
        """Load statistics from file"""
        if os.path.exists(STATS_FILE):
            try:
                with open(STATS_FILE, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading stats: {e}")
        return {'by_category': {}, 'recent_emails': []}
    
    def save_stats(self):
        """Save statistics to file"""
        try:
            os.makedirs(os.path.dirname(STATS_FILE), exist_ok=True)
            with open(STATS_FILE, 'w') as f:
                json.dump(self.stats, f, indent=2)
        except Exception as e:
            print(f"Error saving stats: {e}")
    
    def update_stats(self, email: Dict, category: str):
        """Update email statistics"""
        # Update category counts
        if category not in self.stats['by_category']:
            self.stats['by_category'][category] = 0
        self.stats['by_category'][category] += 1
        
        # Add to recent emails (keep last 50)
        email_summary = {
            'subject': email['subject'],
            'from': email['from'],
            'category': category,
            'timestamp': email['timestamp']
        }
        self.stats['recent_emails'].insert(0, email_summary)
        self.stats['recent_emails'] = self.stats['recent_emails'][:50]
        
        self.save_stats()
    
    def authenticate_gmail(self):
        """Authenticate with Gmail API"""
        creds = None
        if os.path.exists(TOKEN_PATH):
            creds = Credentials.from_authorized_user_file(TOKEN_PATH, ['https://mail.google.com/'])
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
                with open(TOKEN_PATH, 'w') as token:
                    token.write(creds.to_json())
            else:
                raise Exception("Gmail authentication failed. Please run gmail_auth.py first.")
        
        self.gmail_service = build('gmail', 'v1', credentials=creds)
        print("✓ Gmail authenticated")
    
    def categorize_email(self, subject: str, snippet: str, sender: str) -> str:
        """Categorize email based on content"""
        content = f"{subject} {snippet} {sender}".lower()
        
        # Check each category
        best_category = 'general'
        best_priority = 999
        
        for category, config in CATEGORIES.items():
            for keyword in config['keywords']:
                if keyword in content:
                    if config['priority'] < best_priority:
                        best_category = category
                        best_priority = config['priority']
                    break
        
        return best_category
    
    def extract_email_address(self, from_header: str) -> str:
        """Extract email address from From header"""
        match = re.search(r'<(.+?)>', from_header)
        if match:
            return match.group(1)
        return from_header
    
    def get_unread_emails(self) -> List[Dict]:
        """Fetch unread emails from inbox"""
        try:
            results = self.gmail_service.users().messages().list(
                userId='me',
                q='is:unread in:inbox',
                maxResults=50
            ).execute()
            
            messages = results.get('messages', [])
            emails = []
            
            for message in messages:
                msg_id = message['id']
                
                # Skip if already processed
                if msg_id in self.state['processed_emails']:
                    continue
                
                # Get full message details
                msg = self.gmail_service.users().messages().get(
                    userId='me',
                    id=msg_id,
                    format='full'
                ).execute()
                
                headers = {h['name']: h['value'] for h in msg['payload']['headers']}
                
                email_data = {
                    'id': msg_id,
                    'thread_id': msg['threadId'],
                    'subject': headers.get('Subject', 'No Subject'),
                    'from': headers.get('From', 'Unknown'),
                    'date': headers.get('Date', ''),
                    'snippet': msg.get('snippet', ''),
                    'timestamp': int(msg['internalDate']) / 1000
                }
                
                emails.append(email_data)
            
            return emails
        
        except HttpError as error:
            print(f"Error fetching emails: {error}")
            return []
    
    def send_auto_response(self, email: Dict, category: str):
        """Send auto-response if configured for category"""
        response_text = CATEGORIES[category].get('auto_response')
        
        if not response_text:
            return
        
        try:
            sender_email = self.extract_email_address(email['from'])
            
            message = {
                'raw': self.create_message(
                    to=sender_email,
                    subject=f"Re: {email['subject']}",
                    body=response_text
                )
            }
            
            # Send as reply in same thread
            self.gmail_service.users().messages().send(
                userId='me',
                body=message,
                threadId=email['thread_id']
            ).execute()
            
            print(f"✓ Sent auto-response to {sender_email}")
            
        except Exception as e:
            print(f"Error sending auto-response: {e}")
    
    def create_message(self, to: str, subject: str, body: str) -> str:
        """Create base64 encoded email message"""
        import base64
        from email.mime.text import MIMEText
        
        message = MIMEText(body)
        message['to'] = to
        message['subject'] = subject
        message['from'] = 'arbi@betterfuturelabs.xyz'
        
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
        return raw
    
    def mark_as_read(self, email_id: str):
        """Mark email as read"""
        try:
            self.gmail_service.users().messages().modify(
                userId='me',
                id=email_id,
                body={'removeLabelIds': ['UNREAD']}
            ).execute()
        except Exception as e:
            print(f"Error marking email as read: {e}")
    
    async def notify_discord(self, email: Dict, category: str):
        """Send notification to Discord"""
        if not DISCORD_WEBHOOK_URL:
            return
        
        try:
            async with aiohttp.ClientSession() as session:
                webhook = Webhook.from_url(DISCORD_WEBHOOK_URL, session=session)
                
                # Create embed
                color_map = {
                    'urgent': 0xFF0000,      # Red
                    'partnership': 0x00FF00,  # Green
                    'technical': 0x0000FF,    # Blue
                    'business': 0xFFD700,     # Gold
                    'community': 0x808080,    # Gray
                    'general': 0x808080       # Gray
                }
                
                embed = discord.Embed(
                    title=f"📧 New {category.upper()} Email",
                    description=email['snippet'][:200] + ('...' if len(email['snippet']) > 200 else ''),
                    color=color_map.get(category, 0x808080),
                    timestamp=datetime.fromtimestamp(email['timestamp'])
                )
                
                embed.add_field(name="From", value=email['from'], inline=False)
                embed.add_field(name="Subject", value=email['subject'], inline=False)
                embed.add_field(name="Category", value=category.upper(), inline=True)
                
                await webhook.send(content="<@1468335112679723048>", embed=embed, username="Arbi Email Monitor")
                
                print(f"✓ Notified Discord about {category} email")
                
        except Exception as e:
            print(f"Error sending Discord notification: {e}")
    
    async def process_emails(self):
        """Main email processing loop"""
        emails = self.get_unread_emails()
        
        if not emails:
            print(f"No new emails at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            return
        
        print(f"\n📬 Found {len(emails)} new email(s)")
        
        for email in emails:
            category = self.categorize_email(email['subject'], email['snippet'], email['from'])
            
            print(f"\n📧 Processing: {email['subject']}")
            print(f"   From: {email['from']}")
            print(f"   Category: {category}")
            
            # Send Discord notification if configured
            if CATEGORIES[category]['notify_discord']:
                await self.notify_discord(email, category)
            
            # Send auto-response if configured
            if CATEGORIES[category]['auto_response']:
                self.send_auto_response(email, category)
            
            # Update statistics
            self.update_stats(email, category)
            
            # Mark as processed
            self.state['processed_emails'].append(email['id'])
            
            # Mark as read for non-urgent emails
            if category not in ['urgent', 'partnership', 'technical']:
                self.mark_as_read(email['id'])
        
        # Update state
        self.state['last_check_time'] = datetime.now().isoformat()
        self.save_state()
        
        # Clean up old processed emails (keep last 1000)
        if len(self.state['processed_emails']) > 1000:
            self.state['processed_emails'] = self.state['processed_emails'][-1000:]
            self.save_state()
    
    async def run(self):
        """Main service loop"""
        print("🤖 Arbi Email Automation Service Starting...")
        print(f"   Check interval: {CHECK_INTERVAL} seconds")
        print(f"   Discord notifications: {'Enabled' if DISCORD_WEBHOOK_URL else 'Disabled'}")
        
        self.authenticate_gmail()
        
        while True:
            try:
                await self.process_emails()
            except Exception as e:
                print(f"Error in main loop: {e}")
            
            await asyncio.sleep(CHECK_INTERVAL)


def main():
    service = EmailAutomationService()
    asyncio.run(service.run())


if __name__ == '__main__':
    main()
