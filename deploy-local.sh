#!/bin/bash

# Simple Local Docker Deployment for yt-dlp Service
# This script provides a streamlined way to deploy the service locally using Docker

echo "🚀 yt-dlp Service - Local Docker Deployment"
echo "============================================="

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[NOTE]${NC} $1"
}

# Check if docker-deploy.sh exists
if [ ! -f "./docker-deploy.sh" ]; then
    echo "Error: docker-deploy.sh not found in current directory"
    exit 1
fi

# Make docker-deploy.sh executable
chmod +x ./docker-deploy.sh

# Parse command line arguments
ACTION=${1:-"start"}

case $ACTION in
    "start")
        print_info "Starting yt-dlp service with Docker..."
        ./docker-deploy.sh dev
        
        if [ $? -eq 0 ]; then
            print_success "🎉 yt-dlp service is now running!"
            echo ""
            print_warning "Access the service at: http://localhost:8090"
            print_warning "To view logs: ./deploy-local.sh logs"
            print_warning "To stop: ./deploy-local.sh stop"
            echo ""
            print_info "Testing the service..."
            sleep 3
            ./docker-deploy.sh test
        fi
        ;;
    
    "stop")
        print_info "Stopping yt-dlp service..."
        ./docker-deploy.sh down
        ;;
    
    "restart")
        print_info "Restarting yt-dlp service..."
        ./docker-deploy.sh restart-fresh
        ;;
    
    "logs")
        print_info "Showing service logs (Press Ctrl+C to exit)..."
        ./docker-deploy.sh logs
        ;;
    
    "status")
        print_info "Service status:"
        ./docker-deploy.sh status
        ;;
    
    "test")
        print_info "Running tests..."
        ./docker-deploy.sh test
        echo ""
        print_info "Testing caption extraction endpoint..."
        curl -X POST http://localhost:8090/extract-captions \
             -H "Content-Type: application/json" \
             -d '{"url": "https://www.youtube.com/watch?v=jNQXAC9IVRw"}' \
             --silent --fail > /dev/null
        
        if [ $? -eq 0 ]; then
            print_success "✅ Caption extraction endpoint working"
        else
            echo "❌ Caption extraction endpoint failed"
        fi
        ;;
    
    "clean")
        print_warning "This will remove all Docker containers and images for the service"
        ./docker-deploy.sh clean
        ;;
    
    "help"|*)
        echo "Usage: $0 {start|stop|restart|logs|status|test|clean|help}"
        echo ""
        echo "Commands:"
        echo "  start    - Start the yt-dlp service (default)"
        echo "  stop     - Stop the service"
        echo "  restart  - Restart the service with fresh build"
        echo "  logs     - Show service logs"
        echo "  status   - Show service status"
        echo "  test     - Run tests against the service"
        echo "  clean    - Remove all containers and images"
        echo "  help     - Show this help message"
        echo ""
        echo "Quick Start:"
        echo "  ./deploy-local.sh start    # Start the service"
        echo "  open http://localhost:8090 # Access the web interface"
        echo "  ./deploy-local.sh stop     # Stop when done"
        ;;
esac 