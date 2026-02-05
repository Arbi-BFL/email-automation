FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY email_service.py .
COPY dashboard.py .
COPY start.sh .
COPY templates/ templates/

# Create data directory for persistent state
RUN mkdir -p /data

# Health check endpoint
COPY healthcheck.py .

# Make start script executable
RUN chmod +x start.sh

# Expose dashboard port
EXPOSE 3400

# Run both services
CMD ["./start.sh"]
