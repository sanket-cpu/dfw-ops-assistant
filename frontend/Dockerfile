# Frontend Dockerfile for DFW Airport RAG Assistant
# Multi-stage build: Node for building, nginx for serving
# Build context should be project root (set in docker-compose.yml)

# ============== Build Stage ==============
FROM node:20-alpine AS builder

WORKDIR /app

# Copy package files
COPY frontend/package*.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY frontend/ ./

# Set API URL to empty string so it uses relative path (nginx will proxy to backend)
ENV VITE_API_URL=""

# Build the application
RUN npm run build

# ============== Production Stage ==============
FROM nginx:alpine

# Copy custom nginx config
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf

# Copy built assets from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Expose port
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost/ || exit 1

# nginx runs as daemon by default
CMD ["nginx", "-g", "daemon off;"]
