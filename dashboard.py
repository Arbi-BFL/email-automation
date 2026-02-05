#!/usr/bin/env python3
"""
Email Dashboard - Web interface for email automation stats
"""

from flask import Flask, render_template, jsonify
from flask_cors import CORS
import json
import os
from datetime import datetime, timedelta
from collections import Counter

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

STATE_FILE = '/data/email_state.json'
STATS_FILE = '/data/email_stats.json'


def load_state():
    """Load email state"""
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    return {'processed_emails': [], 'last_check_time': None}


def load_stats():
    """Load email statistics"""
    if os.path.exists(STATS_FILE):
        try:
            with open(STATS_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    return {'total_processed': 0, 'by_category': {}, 'recent_emails': []}


@app.route('/')
def index():
    """Dashboard home page"""
    return render_template('index.html')


@app.route('/api/stats')
def api_stats():
    """Get email statistics"""
    state = load_state()
    stats = load_stats()
    
    # Calculate uptime
    last_check = state.get('last_check_time')
    if last_check:
        last_check_dt = datetime.fromisoformat(last_check)
        minutes_since_check = (datetime.now() - last_check_dt).total_seconds() / 60
        status = 'healthy' if minutes_since_check < 15 else 'stale'
    else:
        status = 'starting'
        last_check = 'Never'
    
    return jsonify({
        'status': status,
        'last_check': last_check,
        'total_processed': len(state.get('processed_emails', [])),
        'by_category': stats.get('by_category', {}),
        'recent_emails': stats.get('recent_emails', [])[:10]
    })


@app.route('/health')
def health():
    """Health check endpoint"""
    state = load_state()
    last_check = state.get('last_check_time')
    
    if not last_check:
        return jsonify({'status': 'starting'}), 200
    
    last_check_dt = datetime.fromisoformat(last_check)
    minutes_since_check = (datetime.now() - last_check_dt).total_seconds() / 60
    
    if minutes_since_check < 15:
        return jsonify({'status': 'healthy', 'last_check': last_check}), 200
    else:
        return jsonify({'status': 'unhealthy', 'last_check': last_check}), 503


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3400, debug=False)
