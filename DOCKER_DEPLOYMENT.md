# Docker Deployment Guide

This guide shows how to deploy the yt-dlp service locally using Docker.

## Prerequisites

- Docker Desktop installed and running
- Git (to clone the repository)

## Quick Start

1. **Start the service:**
   ```bash
   ./deploy-local.sh start
   ```

2. **Access the service:**
   - Open your browser and go to: http://localhost:8090
   - Use the web interface to test video downloads and caption extraction

3. **Stop the service:**
   ```bash
   ./deploy-local.sh stop
   ```

## Available Commands

### Simple Deployment Script (`deploy-local.sh`)

```bash
./deploy-local.sh start     # Start the service (rebuilds if needed)
./deploy-local.sh stop      # Stop the service
./deploy-local.sh restart   # Restart with fresh build
./deploy-local.sh logs      # View service logs
./deploy-local.sh status    # Show container status
./deploy-local.sh test      # Run tests against the service
./deploy-local.sh clean     # Remove all containers and images
./deploy-local.sh help      # Show help
```

### Advanced Deployment Script (`docker-deploy.sh`)

For more advanced usage, you can use the full-featured deployment script:

```bash
./docker-deploy.sh build       # Build Docker image only
./docker-deploy.sh up          # Start services (existing build)
./docker-deploy.sh up-fresh    # Start with fresh build (no cache)
./docker-deploy.sh dev         # Development mode (recommended)
./docker-deploy.sh down        # Stop services
./docker-deploy.sh restart     # Restart services
./docker-deploy.sh logs        # Show logs
./docker-deploy.sh status      # Show status
./docker-deploy.sh test        # Run tests
./docker-deploy.sh shell       # Open shell in container
./docker-deploy.sh clean       # Remove everything (DANGEROUS)
```

## What's Included

The Docker deployment includes:

- **Web Interface** at http://localhost:8090
- **REST API Endpoints:**
  - `GET /health` - Health check
  - `GET /ytdlp-info` - Service information
  - `POST /test-ytdlp` - Extract video metadata
  - `POST /test-download` - Test video downloading
  - `POST /extract-captions` - Extract video captions/subtitles
  - `POST /terminal` - Execute commands
  - `GET /api-docs` - API documentation

## Testing the Service

### Web Interface
1. Open http://localhost:8090 in your browser
2. Use the interactive forms to test different features
3. Try the new "Caption Extraction" form with a YouTube URL

### API Testing
```bash
# Test health endpoint
curl http://localhost:8090/health

# Test caption extraction
curl -X POST http://localhost:8090/extract-captions \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.youtube.com/watch?v=jNQXAC9IVRw"}'

# Test video metadata extraction
curl -X POST http://localhost:8090/test-ytdlp \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"}'
```

## Architecture

The deployment uses:
- **Multi-stage Docker build** for optimized image size
- **Non-root user** for security
- **Health checks** for reliability
- **Volume mounting** for temporary files
- **Network isolation** with custom Docker network

## Troubleshooting

### Docker not running
```bash
# On macOS
open -a Docker

# Wait for Docker to start, then retry deployment
```

### Port 8090 already in use
```bash
# Stop any existing services
./deploy-local.sh stop

# Or kill processes using the port
sudo lsof -ti:8090 | xargs kill -9
```

### View logs for debugging
```bash
./deploy-local.sh logs
```

### Clean up everything and start fresh
```bash
./deploy-local.sh clean
./deploy-local.sh start
```

## Development Workflow

For active development:

1. **Make code changes**
2. **Restart with fresh build:**
   ```bash
   ./deploy-local.sh restart
   ```
3. **Test changes:**
   ```bash
   ./deploy-local.sh test
   ```

## Production Considerations

For production deployment, consider:
- Using environment-specific configuration
- Setting up proper logging
- Configuring reverse proxy (nginx)
- Setting up SSL/TLS
- Monitoring and alerting
- Resource limits and scaling 