#!/usr/bin/env python3
"""Health check for email automation service"""

import os
import json
from datetime import datetime, timedelta

STATE_FILE = '/data/email_state.json'

def check_health():
    """Check if service is healthy"""
    try:
        # Check if state file exists
        if not os.path.exists(STATE_FILE):
            print("HEALTHY: Service starting up")
            return True
        
        # Check last check time
        with open(STATE_FILE, 'r') as f:
            state = json.load(f)
        
        if 'last_check_time' in state:
            last_check = datetime.fromisoformat(state['last_check_time'])
            check_interval = int(os.environ.get('CHECK_INTERVAL', '300'))
            max_age = timedelta(seconds=check_interval * 3)  # 3x check interval
            
            if datetime.now() - last_check > max_age:
                print(f"UNHEALTHY: Last check was {datetime.now() - last_check} ago")
                return False
        
        print("HEALTHY: Service running normally")
        return True
        
    except Exception as e:
        print(f"UNHEALTHY: {e}")
        return False

if __name__ == '__main__':
    exit(0 if check_health() else 1)
