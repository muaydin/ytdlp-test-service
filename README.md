# 🎥 yt-dlp Test Service

A comprehensive Flask-based web service for testing yt-dlp (YouTube video downloader) functionality with a beautiful modern UI and robust API.

![yt-dlp Test Service](https://img.shields.io/badge/Python-3.7+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-2.3.3-green.svg)
![yt-dlp](https://img.shields.io/badge/yt--dlp-2025.09.05-red.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## ✨ Features

- **�� Modern Web UI**: Beautiful, responsive interface with progress bars and real-time feedback
- **📊 Metadata Extraction**: Get video information without downloading
- **⬇️ Download Testing**: Test actual video downloads to memory with verification
- **🔗 RESTful API**: Complete REST API with JSON responses
- **📚 API Documentation**: Built-in comprehensive API documentation
- **🐋 Docker Ready**: Complete Docker setup with Compose and deployment scripts
- **🛡️ Security**: Input validation and sandboxed command execution
- **📱 Mobile Responsive**: Works perfectly on desktop and mobile devices

## 🚀 Quick Start

### Option 1: Docker (Recommended) 🐋

**Prerequisites**: Docker and Docker Compose installed

```bash
# Clone the repository
git clone https://github.com/muaydin/ytdlp-test-service.git
cd ytdlp-test-service

# Start with one command
./docker-deploy.sh up

# Access the service at http://localhost:8090
```

**That's it!** The service is now running in a container with all dependencies included.

### Option 2: Local Python Setup

**Prerequisites**: Python 3.7+ and pip

```bash
# Clone the repository
git clone https://github.com/muaydin/ytdlp-test-service.git
cd ytdlp-test-service

# Run the automated setup
./setup_local.sh

# Start the service
python app.py
```

The service will start on `http://localhost:8090`

## 🐋 Docker Usage Guide

### Quick Commands

| Command | Description |
|---------|-------------|
| `./docker-deploy.sh up` | Start the service |
| `./docker-deploy.sh down` | Stop the service |
| `./docker-deploy.sh logs` | View service logs |
| `./docker-deploy.sh status` | Check service status |
| `./docker-deploy.sh test` | Run API tests |
| `./docker-deploy.sh clean` | Remove everything |

### Detailed Docker Commands

**Start the service:**
```bash
./docker-deploy.sh up
# or
docker-compose up -d
```

**View logs:**
```bash
./docker-deploy.sh logs
# or
docker-compose logs -f
```

**Stop the service:**
```bash
./docker-deploy.sh down
# or
docker-compose down
```

**Rebuild and restart:**
```bash
./docker-deploy.sh build
./docker-deploy.sh up
```

**Access container shell:**
```bash
./docker-deploy.sh shell
# or
docker-compose exec ytdlp-test bash
```

### Docker Features

- **🏗️ Multi-stage Build**: Optimized image (~800MB) with all dependencies
- **🔒 Security**: Runs as non-root user (`ytdlp`)
- **📦 Complete Stack**: Includes FFmpeg, Python, and all dependencies
- **🩺 Health Checks**: Automatic container health monitoring
- **🔄 Auto-restart**: Containers restart on failure
- **📊 Volume Management**: Persistent storage for temporary files
- **🌐 Network Isolation**: Dedicated Docker network

### Manual Docker Commands

If you prefer manual control:

```bash
# Build the image
docker build -t ytdlp-test-service .

# Run the container
docker run -d \
  --name ytdlp-test \
  -p 8090:8090 \
  --restart unless-stopped \
  ytdlp-test-service

# View logs
docker logs -f ytdlp-test

# Stop and remove
docker stop ytdlp-test
docker rm ytdlp-test
```

## 🧪 Testing

### Quick Test Script
```bash
# For Docker
./docker-deploy.sh test

# For local setup
./test_local.sh
```

### Manual Testing
```bash
# Health check
curl http://localhost:8090/health

# Get yt-dlp info
curl http://localhost:8090/ytdlp-info

# Test metadata extraction
curl -X POST http://localhost:8090/test-ytdlp \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"}'

# Test video download
curl -X POST http://localhost:8090/test-download \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"}'
```

## 📋 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Modern web interface with interactive forms |
| `GET` | `/health` | Service health check |
| `GET` | `/ytdlp-info` | yt-dlp version and capabilities |
| `POST` | `/test-ytdlp` | Extract video metadata |
| `POST` | `/test-download` | Download video to memory for testing |
| `POST` | `/terminal` | Execute yt-dlp commands directly |
| `GET` | `/api-docs` | Complete API documentation |

### Example Responses

**Metadata Extraction (`/test-ytdlp`)**:
```json
{
  "success": true,
  "title": "Rick Astley - Never Gonna Give You Up",
  "duration": 213,
  "uploader": "Rick Astley",
  "view_count": 1692567350,
  "formats_available": 22
}
```

**Download Test (`/test-download`)**:
```json
{
  "success": true,
  "video_title": "Rick Astley - Never Gonna Give You Up",
  "downloaded_bytes": 241672132,
  "downloaded_size_mb": 230.48,
  "download_type": "video",
  "file_extension": ".webm"
}
```

## 🌐 Web Interface

The modern web interface includes:

- **Interactive Forms**: Real-time form validation and submission
- **Progress Bars**: Visual feedback during processing
- **Result Display**: Formatted success/error messages
- **API Documentation**: Built-in endpoint documentation
- **Sample URLs**: Pre-filled test URLs for quick testing
- **Mobile Responsive**: Optimized for all screen sizes

## 🔧 Configuration

### Environment Variables
- `PORT`: Server port (default: 8090)
- `FLASK_ENV`: Environment mode (development/production)

### Sample URLs for Testing
- **Classic**: `https://www.youtube.com/watch?v=dQw4w9WgXcQ`
- **Short**: `https://www.youtube.com/watch?v=jNQXAC9IVRw`
- **Recent**: `https://www.youtube.com/watch?v=2NRkV7ZQUJA`

## 🚢 Deployment

### Docker (Recommended for Production)

**Quick Start with Docker Compose:**
```bash
# Clone the repository
git clone https://github.com/muaydin/ytdlp-test-service.git
cd ytdlp-test-service

# Start with Docker Compose (easiest)
./docker-deploy.sh up

# Access the service at http://localhost:8090
```

**Production Deployment:**
```bash
# Build production image
./docker-deploy.sh build

# Start with restart policy
docker-compose up -d

# Monitor health
./docker-deploy.sh status
```

### Railway (Alternative)
```bash
# Install Railway CLI
npm install -g @railway/cli

# Deploy
railway login
railway link
railway up
```

### Manual Deployment
1. Install dependencies: `pip install -r requirements.txt`
2. Use production WSGI server: `gunicorn app:app`

## 🛠️ Development

### Project Structure
```
ytdlp-test-service/
├── app.py              # Main Flask application
├── requirements.txt    # Python dependencies
├── Dockerfile          # Multi-stage Docker build
├── docker-compose.yml  # Docker Compose configuration
├── .dockerignore       # Docker build exclusions
├── docker-deploy.sh    # Docker deployment script
├── setup_local.sh      # Automated setup script
├── test_local.sh       # Testing script
├── README.md           # This file
├── LICENSE             # MIT License
├── .gitignore          # Git ignore rules
├── Procfile            # Railway deployment config
└── railway.toml        # Railway configuration
```

### Docker Development

**Build and test locally:**
```bash
# Build the image
./docker-deploy.sh build

# Run tests
./docker-deploy.sh test

# Access container for debugging
./docker-deploy.sh shell
```

**Development workflow:**
```bash
# Make changes to code
# Rebuild image
./docker-deploy.sh build

# Restart services
./docker-deploy.sh up

# Test changes
./docker-deploy.sh test
```

### Adding New Features
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with Docker: `./docker-deploy.sh test`
5. Add tests if applicable
6. Submit a pull request

## 🚨 Important Notes

- **YouTube Restrictions**: Due to YouTube's bot protection, downloads may only retrieve storyboard images or metadata rather than actual video files. This is normal and expected behavior.
- **Rate Limiting**: YouTube may temporarily block requests if too many are made quickly.
- **Legal Compliance**: This tool is for testing purposes only. Respect YouTube's Terms of Service and copyright laws.
- **Docker Requirements**: Docker Desktop or Docker Engine required for containerized deployment.

## 🐛 Troubleshooting

### Docker Issues

**Container won't start:**
```bash
# Check Docker status
docker ps -a

# View logs
./docker-deploy.sh logs

# Rebuild image
./docker-deploy.sh build
```

**Port conflicts:**
```bash
# Check what's using port 8090
lsof -i :8090

# Use different port
docker run -p 8091:8090 ytdlp-test-service
```

**Permission issues:**
```bash
# Clean up and rebuild
./docker-deploy.sh clean
./docker-deploy.sh build
```

### Common Issues

1. **Port already in use**: Change port with `PORT=8080 python app.py`
2. **Import errors**: Ensure virtual environment is activated
3. **yt-dlp errors**: Check `/ytdlp-info` endpoint for status
4. **Download failures**: Usually due to YouTube restrictions (expected)
5. **Docker not found**: Install Docker Desktop or Docker Engine

### Getting Help
- Check the built-in API documentation: `http://localhost:8090/api-docs`
- Review the test script output: `./test_local.sh` or `./docker-deploy.sh test`
- Enable debug mode: `FLASK_ENV=development python app.py`
- View Docker logs: `./docker-deploy.sh logs`

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## 🙏 Acknowledgments

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - The excellent YouTube downloader
- [Flask](https://flask.palletsprojects.com/) - The web framework
- [Docker](https://www.docker.com/) - Containerization platform
- [Railway](https://railway.app/) - Deployment platform

---

**Made with ❤️ for testing yt-dlp functionality**
