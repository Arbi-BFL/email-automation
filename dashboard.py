#!/usr/bin/env python3
"""
Simple web dashboard for email automation stats
"""

from flask import Flask, jsonify, render_template_string
import json
import os
from datetime import datetime

app = Flask(__name__)

DASHBOARD_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Arbi Email Automation</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
            color: #fff;
        }
        .nav-link {
            position: fixed;
            top: 20px;
            left: 20px;
            background: rgba(255, 255, 255, 0.2);
            padding: 0.5rem 1rem;
            border-radius: 50px;
            text-decoration: none;
            color: #fff;
            font-weight: 500;
            backdrop-filter: blur(10px);
            z-index: 100;
        }
        .container {
            max-width: 1000px;
            margin: 0 auto;
            padding-top: 2rem;
        }
        h1 { font-size: 2.5rem; text-align: center; margin-bottom: 2rem; }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }
        .stat-card {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 1.5rem;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        .stat-label { opacity: 0.8; font-size: 0.9rem; margin-bottom: 0.5rem; }
        .stat-value { font-size: 2rem; font-weight: 700; }
        .status { text-align: center; margin-top: 2rem; opacity: 0.8; }
    </style>
</head>
<body>
    <a href="https://arbi.betterfuturelabs.xyz" class="nav-link">← Back to Arbi</a>
    
    <div class="container">
        <h1>📧 Email Automation</h1>
        
        <div class="stats-grid" id="stats">
            <div class="stat-card">
                <div class="stat-label">Emails Processed</div>
                <div class="stat-value" id="processed">-</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Service Status</div>
                <div class="stat-value">✅ Active</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Check Interval</div>
                <div class="stat-value">5 min</div>
            </div>
        </div>
        
        <div class="stat-card">
            <h3 style="margin-bottom: 1rem;">Categories</h3>
            <p>📧 General • 💼 Opportunity • 🔧 Technical • 🚨 Urgent • 🗑️ Spam</p>
            <p style="margin-top: 1rem; opacity: 0.8; font-size: 0.9rem;">
                Monitoring: arbi@betterfuturelabs.xyz
            </p>
        </div>
        
        <div class="status">
            Last updated: <span id="timestamp">-</span>
        </div>
    </div>
    
    <script>
        async function loadStats() {
            try {
                const response = await fetch('/api/stats');
                const data = await response.json();
                document.getElementById('processed').textContent = data.processed;
                document.getElementById('timestamp').textContent = new Date().toLocaleString();
            } catch (error) {
                console.error('Error loading stats:', error);
            }
        }
        
        loadStats();
        setInterval(loadStats, 60000);
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(DASHBOARD_HTML)

@app.route('/api/stats')
def stats():
    try:
        with open('/data/processed_emails.json', 'r') as f:
            processed = len(json.load(f))
    except FileNotFoundError:
        processed = 0
    
    return jsonify({
        'processed': processed,
        'status': 'active',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/health')
def health():
    return jsonify({'status': 'ok', 'timestamp': datetime.now().isoformat()})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
