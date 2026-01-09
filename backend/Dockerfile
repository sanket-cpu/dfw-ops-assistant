# Backend Dockerfile for DFW Airport RAG Assistant
# Build context should be project root (set in docker-compose.yml)
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies required by Python packages
# libgl1 provides OpenGL support needed by OpenCV
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libmagic1 \
    poppler-utils \
    tesseract-ocr \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Create app directory structure
WORKDIR /app

# Copy requirements and install dependencies first (better layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source code
COPY backend/ ./backend/

# Create data directory for ChromaDB persistence
RUN mkdir -p /app/data

# Set working directory to backend (chatbot.py uses relative paths from here)
WORKDIR /app/backend

# Expose port
EXPOSE 8000

# Health check - increased start period for first-time document indexing
HEALTHCHECK --interval=30s --timeout=10s --start-period=180s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/docs')" || exit 1

# Run the application
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
