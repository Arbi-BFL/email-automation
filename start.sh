#!/bin/bash
# Start both email service and dashboard

# Start email monitoring service in background
python -u email_service.py &
EMAIL_PID=$!

# Start dashboard web server
python -u dashboard.py &
DASH_PID=$!

# Wait for both processes
wait $EMAIL_PID $DASH_PID
