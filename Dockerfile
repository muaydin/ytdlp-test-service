# Multi-stage build for optimized Docker image
FROM python:3.11-slim as builder

# Set build arguments
ARG DEBIAN_FRONTEND=noninteractive

# Install system dependencies needed for building
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --user -r requirements.txt

# Production stage
FROM python:3.11-slim

# Set build arguments
ARG DEBIAN_FRONTEND=noninteractive

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash --user-group ytdlp

# Set working directory
WORKDIR /app

# Copy Python packages from builder stage
COPY --from=builder /root/.local /home/ytdlp/.local

# Copy application files
COPY --chown=ytdlp:ytdlp . .

# Make scripts executable
RUN chmod +x setup_local.sh test_local.sh deploy.sh

# Set Python path for user-installed packages
ENV PATH="/home/ytdlp/.local/bin:${PATH}"
ENV PYTHONPATH="/home/ytdlp/.local/lib/python3.11/site-packages:${PYTHONPATH}"

# Switch to non-root user
USER ytdlp

# Create temp directory for downloads
RUN mkdir -p /tmp/ytdlp-downloads

# Expose port
EXPOSE 8090

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8090/health || exit 1

# Set environment variables
ENV PORT=8090
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1

# Default command
CMD ["python", "app.py"] 