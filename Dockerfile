# Use Python slim
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY *.py ./

# Create data directory
RUN mkdir -p /data

# Expose port for dashboard
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:5000/health')"

# Start services (both email service and dashboard)
CMD ["sh", "-c", "python dashboard.py & python email_service.py"]
