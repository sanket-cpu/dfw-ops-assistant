# Docker Guide for Beginners

Welcome! This guide will help you understand Docker and how it's used in this project. No prior Docker knowledge required.

## Table of Contents
1. [What is Docker?](#what-is-docker)
2. [Why Use Docker?](#why-use-docker)
3. [Key Docker Concepts](#key-docker-concepts)
4. [How This Project Uses Docker](#how-this-project-uses-docker)
5. [Getting Started](#getting-started)
6. [Common Commands](#common-commands)
7. [Troubleshooting](#troubleshooting)

---

## What is Docker?

Think of Docker like a **shipping container** for software. Just like how shipping containers standardized global trade by ensuring any container fits on any ship, truck, or crane, Docker standardizes software deployment.

**Without Docker:**
- "It works on my machine!" - A common frustration when code works for one developer but not another
- Different computers have different operating systems, software versions, and configurations
- Setting up a development environment can take hours or days

**With Docker:**
- Your application runs in an isolated "container" that includes everything it needs
- The same container runs identically on any computer with Docker installed
- Setup takes minutes instead of hours

## Why Use Docker?

| Problem | Docker Solution |
|---------|-----------------|
| "I need Python 3.12, but I have Python 3.9" | Each container has its own Python version |
| "I can't install these dependencies" | Dependencies are isolated inside containers |
| "It works on Mac but not Windows" | Containers work identically everywhere |
| "Setting up the database is complicated" | Database comes pre-configured in a container |

## Key Docker Concepts

### 1. Image
An **image** is like a recipe or blueprint. It contains:
- A base operating system (usually Linux)
- Your application code
- All dependencies and libraries
- Instructions for how to run everything

Images are **read-only** - they don't change.

### 2. Container
A **container** is a running instance of an image. Think of it like this:
- Image = Cookie cutter
- Container = The actual cookie

You can run multiple containers from the same image.

### 3. Dockerfile
A **Dockerfile** is a text file with instructions for building an image. It's like a recipe that Docker follows step-by-step.

Example from this project (`backend/Dockerfile`):
```dockerfile
# Start with a Python image (like choosing a base cake)
FROM python:3.12-slim

# Install system tools (like adding frosting ingredients)
RUN apt-get update && apt-get install -y \
    build-essential \
    libmagic1

# Copy our code into the image
COPY backend/ ./backend/

# Tell Docker how to run our app
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 4. Docker Compose
**Docker Compose** manages multiple containers that work together. Our app needs:
1. A backend container (Python/FastAPI)
2. A frontend container (React/nginx)

Instead of starting them separately, Docker Compose starts them all with one command.

### 5. Volume
A **volume** is persistent storage. Containers are temporary - when you delete one, its data is lost. Volumes let you keep data between container restarts.

This project uses a volume to store the ChromaDB vector database, so your indexed documents persist.

### 6. Port Mapping
Containers are isolated from your computer. **Port mapping** creates a tunnel so you can access services inside containers.

```
Your Browser -> localhost:80 -> Frontend Container (port 80)
Your Browser -> localhost:8000 -> Backend Container (port 8000)
```

---

## How This Project Uses Docker

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Your Computer                            │
│                                                             │
│  ┌─────────────────┐              ┌─────────────────────┐   │
│  │    Frontend     │              │      Backend        │   │
│  │   (nginx)       │───/ask───>   │    (FastAPI)        │   │
│  │                 │              │                     │   │
│  │  React App      │              │  - OpenAI API       │   │
│  │  Port 80        │              │  - ChromaDB         │   │
│  └─────────────────┘              │  - PDF Processing   │   │
│                                   │  Port 8000          │   │
│                                   └─────────────────────┘   │
│                                             │               │
│                                   ┌─────────────────────┐   │
│                                   │   chroma_data       │   │
│                                   │   (Volume)          │   │
│                                   │   Persists your     │   │
│                                   │   indexed documents │   │
│                                   └─────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Project Files Explained

| File | Purpose |
|------|---------|
| `docker-compose.yml` | Defines both services, their settings, and how they connect |
| `backend/Dockerfile` | Instructions to build the Python backend image |
| `frontend/Dockerfile` | Instructions to build the React frontend image |
| `frontend/nginx.conf` | Configures the web server to serve React and proxy API calls |
| `.dockerignore` | Lists files Docker should ignore (like node_modules) |

### What Happens When You Run `docker compose up`

1. **Docker reads `docker-compose.yml`** - Learns what services to create
2. **Builds images** (if needed) - Follows Dockerfile instructions
3. **Creates containers** - Instances of each image
4. **Creates network** - So containers can talk to each other
5. **Creates volumes** - For persistent data storage
6. **Starts containers** - Backend first, then frontend (because frontend depends on backend)
7. **Health checks** - Waits for backend to be ready before starting frontend

---

## Getting Started

### Prerequisites

1. **Install Docker Desktop**
   - Windows: [Download Docker Desktop](https://www.docker.com/products/docker-desktop/)
   - Mac: Same link, choose Mac version
   - Linux: Follow [official instructions](https://docs.docker.com/engine/install/)

2. **Verify Installation**
   ```bash
   docker --version
   # Should show something like: Docker version 24.0.0

   docker compose version
   # Should show something like: Docker Compose version v2.20.0
   ```

### Running the Application

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd dfw-ops-copilot
   ```

2. **Create environment file**
   ```bash
   # Copy the example file
   cp .env.example .env

   # Edit .env and add your OpenAI API key
   # OPENAI_API_KEY=sk-your-key-here
   ```

3. **Start the application**
   ```bash
   docker compose up -d
   ```

   The `-d` flag runs containers in "detached" mode (in the background).

4. **Wait for startup**

   The first startup takes 2-3 minutes because:
   - Docker downloads base images
   - Backend indexes PDF documents
   - Health checks verify services are ready

5. **Access the application**
   - Frontend: http://localhost
   - Backend API docs: http://localhost:8000/docs

---

## Common Commands

### Essential Commands

```bash
# Start the application
docker compose up -d

# Stop the application
docker compose down

# View running containers
docker ps

# View container logs
docker compose logs

# View specific service logs
docker compose logs backend
docker compose logs frontend

# Follow logs in real-time (like tail -f)
docker compose logs -f backend
```

### Rebuilding After Code Changes

```bash
# Rebuild and restart a specific service
docker compose up -d --build backend

# Rebuild everything
docker compose up -d --build

# Force complete rebuild (no cache)
docker compose build --no-cache
docker compose up -d
```

### Troubleshooting Commands

```bash
# Check container status
docker ps -a

# See why a container stopped
docker logs dfw-copilot-backend

# Get a shell inside a running container
docker exec -it dfw-copilot-backend /bin/bash

# Check container resource usage
docker stats
```

### Cleanup Commands

```bash
# Stop and remove containers, networks
docker compose down

# Also remove volumes (deletes indexed data!)
docker compose down -v

# Remove unused images
docker image prune

# Remove all unused Docker resources
docker system prune
```

---

## Troubleshooting

### Container Won't Start

**Symptom:** `docker compose up` shows errors

**Solutions:**
1. Check logs: `docker compose logs backend`
2. Ensure `.env` file exists with valid `OPENAI_API_KEY`
3. Make sure ports 80 and 8000 aren't used by other apps

### "Port Already in Use" Error

**Symptom:** Error message about port 80 or 8000

**Solutions:**
```bash
# Find what's using the port (Windows PowerShell)
netstat -ano | findstr :80

# Find what's using the port (Mac/Linux)
lsof -i :80

# Either stop the conflicting app, or change ports in docker-compose.yml:
# Change "80:80" to "3000:80" to use port 3000 instead
```

### Backend Unhealthy

**Symptom:** Frontend won't start because backend is unhealthy

**Solutions:**
1. Check backend logs: `docker compose logs backend`
2. Wait longer (first startup indexes documents)
3. Ensure OpenAI API key is valid

### Changes Not Reflected

**Symptom:** Code changes don't appear in the running app

**Solutions:**
```bash
# Rebuild the changed service
docker compose up -d --build backend

# For frontend changes
docker compose up -d --build frontend
```

### Out of Disk Space

**Symptom:** Build fails with disk space errors

**Solutions:**
```bash
# Remove unused images and containers
docker system prune -a

# Check Docker disk usage
docker system df
```

### "Cannot Connect to Docker" Error

**Symptom:** Docker commands fail with connection errors

**Solutions:**
1. Make sure Docker Desktop is running
2. Restart Docker Desktop
3. On Windows, ensure WSL 2 is properly installed

---

## Understanding the docker-compose.yml File

Let's break down each section:

```yaml
services:
  # The backend Python/FastAPI service
  backend:
    build:
      context: .                    # Build from project root
      dockerfile: backend/Dockerfile # Use this Dockerfile
    container_name: dfw-copilot-backend  # Name for the container
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}  # Pass API key from .env
    volumes:
      - chroma_data:/app/data       # Persist database
      - ./backend/files:/app/backend/files:ro  # Mount PDFs (read-only)
    ports:
      - "8000:8000"                 # Map host:container ports
    restart: unless-stopped         # Auto-restart if it crashes
    healthcheck:                    # Verify service is working
      test: ["CMD", "python", "-c", "..."]
      start_period: 180s            # Wait 3 min for first startup

  # The frontend React/nginx service
  frontend:
    build:
      context: .
      dockerfile: frontend/Dockerfile
    container_name: dfw-copilot-frontend
    ports:
      - "80:80"
    depends_on:
      backend:
        condition: service_healthy  # Wait for backend to be ready
    restart: unless-stopped

volumes:
  chroma_data:                      # Named volume for database
    name: dfw-copilot-chroma-data
```

---

## Next Steps

Now that you understand Docker basics, here are ways to learn more:

1. **Experiment**: Try modifying `docker-compose.yml` and see what happens
2. **Explore containers**: Use `docker exec -it <container> /bin/bash` to look inside
3. **Read the docs**: [Docker's official getting started guide](https://docs.docker.com/get-started/)
4. **Practice**: Try dockerizing a simple app of your own

---

## Quick Reference Card

```bash
# Start app
docker compose up -d

# Stop app
docker compose down

# View logs
docker compose logs -f

# Rebuild after changes
docker compose up -d --build

# Check status
docker ps

# Cleanup
docker system prune
```

---

*Happy containerizing!*
