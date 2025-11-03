# Use official Python runtime as base image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements files
COPY requirements.txt .
COPY ../requirements.txt ./requirements-parent.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -r requirements-parent.txt

# Copy application code
COPY . .

# Copy parent scripts directory
COPY ../scripts /app/scripts

# Expose port (Cloud Run will set $PORT)
ENV PORT=8080
EXPOSE 8080

# Run the application
CMD exec uvicorn main:app --host 0.0.0.0 --port ${PORT}
