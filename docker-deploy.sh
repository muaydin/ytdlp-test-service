#!/bin/bash

# Docker deployment script for yt-dlp Test Service
set -e

echo "🐋 Docker Deployment Script for yt-dlp Test Service"
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is available
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    print_error "Docker Compose is not available. Please install Docker Compose."
    exit 1
fi

# Determine which compose command to use
if command -v docker-compose &> /dev/null; then
    COMPOSE_CMD="docker-compose"
else
    COMPOSE_CMD="docker compose"
fi

# Parse command line arguments
ACTION=${1:-"help"}

case $ACTION in
    "build")
        print_status "Building Docker image..."
        docker build -t ytdlp-test-service .
        print_success "Docker image built successfully!"
        ;;
    
    "up")
        print_status "Starting services with Docker Compose..."
        $COMPOSE_CMD up -d
        print_success "Services started! Access the app at: http://localhost:8090"
        ;;
    
    "up-fresh")
        print_status "Starting services with fresh build (no cache)..."
        docker build --no-cache -t ytdlp-test-service .
        $COMPOSE_CMD up -d
        print_success "Services started with fresh build! Access the app at: http://localhost:8090"
        ;;
    
    "dev")
        print_status "Development mode: Stopping, rebuilding, and starting services..."
        $COMPOSE_CMD down
        print_status "Building with cache invalidation..."
        $COMPOSE_CMD up --build -d
        print_success "Development environment ready! Access the app at: http://localhost:8090"
        ;;
    
    "down")
        print_status "Stopping services..."
        $COMPOSE_CMD down
        print_success "Services stopped!"
        ;;
    
    "restart")
        print_status "Restarting services..."
        $COMPOSE_CMD down
        $COMPOSE_CMD up -d
        print_success "Services restarted! Access the app at: http://localhost:8090"
        ;;
    
    "restart-fresh")
        print_status "Restarting services with fresh build..."
        $COMPOSE_CMD down
        docker build --no-cache -t ytdlp-test-service .
        $COMPOSE_CMD up -d
        print_success "Services restarted with fresh build! Access the app at: http://localhost:8090"
        ;;
    
    "logs")
        print_status "Showing logs..."
        $COMPOSE_CMD logs -f ytdlp-test
        ;;
    
    "status")
        print_status "Service status:"
        $COMPOSE_CMD ps
        ;;
    
    "clean")
        print_warning "This will remove all containers, images, and volumes!"
        read -p "Are you sure? (y/N): " -r
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            print_status "Cleaning up..."
            $COMPOSE_CMD down -v --rmi all
            docker system prune -f
            print_success "Cleanup completed!"
        else
            print_status "Cleanup cancelled."
        fi
        ;;
    
    "test")
        print_status "Running tests against the containerized service..."
        
        # Wait for service to be ready
        print_status "Waiting for service to be ready..."
        timeout=60
        while [ $timeout -gt 0 ]; do
            if curl -s http://localhost:8090/health > /dev/null 2>&1; then
                break
            fi
            sleep 2
            timeout=$((timeout - 2))
        done
        
        if [ $timeout -le 0 ]; then
            print_error "Service did not start within 60 seconds"
            exit 1
        fi
        
        print_success "Service is ready! Running tests..."
        
        # Test health endpoint
        if curl -s http://localhost:8090/health | grep -q "healthy"; then
            print_success "✅ Health check passed"
        else
            print_error "❌ Health check failed"
        fi
        
        # Test yt-dlp info endpoint
        if curl -s http://localhost:8090/ytdlp-info | grep -q "yt-dlp_version"; then
            print_success "✅ yt-dlp info endpoint working"
        else
            print_error "❌ yt-dlp info endpoint failed"
        fi
        
        print_success "Basic tests completed!"
        ;;
    
    "shell")
        print_status "Opening shell in container..."
        $COMPOSE_CMD exec ytdlp-test /bin/bash
        ;;
    
    "help"|*)
        echo "Usage: $0 {build|up|up-fresh|dev|down|restart|restart-fresh|logs|status|clean|test|shell|help}"
        echo ""
        echo "Commands:"
        echo "  build         - Build the Docker image"
        echo "  up            - Start services with Docker Compose"
        echo "  up-fresh      - Start services with fresh build (no cache)"
        echo "  dev           - Development mode: down + build + up (recommended for development)"
        echo "  down          - Stop services"
        echo "  restart       - Restart services"
        echo "  restart-fresh - Restart services with fresh build (no cache)"
        echo "  logs          - Show service logs"
        echo "  status        - Show service status"
        echo "  clean         - Remove all containers, images, and volumes (DANGEROUS)"
        echo "  test          - Run basic tests against the service"
        echo "  shell         - Open shell in the container"
        echo "  help          - Show this help message"
        echo ""
        echo "Development Workflow:"
        echo "  $0 dev         # Recommended: Stop, rebuild, and start (reflects code changes)"
        echo "  $0 up-fresh    # Alternative: Start with fresh build"
        echo "  $0 restart-fresh # Alternative: Restart with fresh build"
        echo ""
        echo "Production Workflow:"
        echo "  $0 build       # Build the image"
        echo "  $0 up          # Start the service"
        echo "  $0 test        # Test the running service"
        echo "  $0 logs        # View logs"
        echo "  $0 down        # Stop the service"
        ;;
esac
