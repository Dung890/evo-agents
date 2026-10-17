#!/bin/bash

# Docker-based Local Development Script
# Mimics AWS deployment environment locally

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

print_header() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
}

# Check if we're in the right directory
if [ ! -f "Dockerfile" ]; then
    print_error "Please run this script from the aws-agetic-ai directory"
    exit 1
fi

print_header "Docker-based Local Development"
print_info "This mimics how the app runs on AWS"
echo ""

# Step 1: Check prerequisites
print_info "Step 1: Checking prerequisites..."
echo ""

# Check Docker
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker daemon is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker Desktop and try again."
    exit 1
fi
print_success "Docker is running ($(docker --version))"

# Check docker-compose
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null 2>&1; then
    print_error "docker-compose is not installed. Please install docker-compose first."
    exit 1
fi
print_success "docker-compose is available"

echo ""

# Step 2: Check AWS credentials (optional)
print_info "Step 2: Checking AWS credentials..."
echo ""

if [ -z "$AWS_ACCESS_KEY_ID" ] || [ -z "$AWS_SECRET_ACCESS_KEY" ]; then
    print_warning "AWS credentials not set in environment variables"
    print_info "The system will work with limited functionality (no AI features)"
    print_info "To enable full AI features with AWS Bedrock, set:"
    echo ""
    echo "  export AWS_ACCESS_KEY_ID=your_access_key"
    echo "  export AWS_SECRET_ACCESS_KEY=your_secret_key"
    echo "  export AWS_DEFAULT_REGION=us-east-1"
    echo ""
    read -p "Continue without AWS credentials? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_error "Setup cancelled"
        exit 1
    fi
else
    print_success "AWS credentials found"
    print_info "AWS Region: ${AWS_DEFAULT_REGION:-us-east-1}"
fi

echo ""

# Step 3: Clean up any previous containers
print_info "Step 3: Cleaning up previous containers..."
echo ""

if docker-compose ps -q 2>/dev/null | grep -q .; then
    print_info "Stopping existing containers..."
    docker-compose down
    print_success "Previous containers stopped"
else
    print_success "No existing containers to clean up"
fi

echo ""

# Step 4: Build the Docker image
print_header "Building Docker Image (AWS-style)"
echo ""
print_warning "This may take 5-10 minutes on first run..."
print_info "Building frontend and backend in production mode..."
echo ""

if docker-compose build; then
    print_success "Docker image built successfully!"
else
    print_error "Docker build failed. Check the output above for errors."
    exit 1
fi

echo ""

# Step 5: Start the container
print_header "Starting Application Container"
echo ""

print_info "Starting container in detached mode..."
if docker-compose up -d; then
    print_success "Container started successfully!"
else
    print_error "Failed to start container"
    exit 1
fi

echo ""

# Step 6: Wait for application to be ready
print_info "Waiting for application to be ready..."
echo ""

MAX_ATTEMPTS=30
ATTEMPT=0

while [ $ATTEMPT -lt $MAX_ATTEMPTS ]; do
    if docker-compose exec -T backend curl -f http://localhost:8080/health > /dev/null 2>&1; then
        print_success "Application is ready!"
        break
    fi
    ATTEMPT=$((ATTEMPT + 1))
    echo -n "."
    sleep 2
done

if [ $ATTEMPT -eq $MAX_ATTEMPTS ]; then
    print_error "Application failed to start within timeout"
    print_info "Checking logs..."
    docker-compose logs --tail=50
    exit 1
fi

echo ""
echo ""

# Step 7: Display access information
print_header "🚀 Application Running!"
echo ""
print_success "Application URL: http://localhost:8080"
print_success "API Documentation: http://localhost:8080/docs"
print_success "Health Check: http://localhost:8080/health"
echo ""
print_info "The app runs on port 8080 (same as AWS Elastic Beanstalk)"
print_info "Frontend and backend are served from the same container"
echo ""

# Step 8: Show useful commands
print_header "Useful Commands"
echo ""
echo "  View logs:           docker-compose logs -f"
echo "  Stop application:    docker-compose down"
echo "  Restart:             docker-compose restart"
echo "  Rebuild:             docker-compose build --no-cache"
echo "  Enter container:     docker-compose exec backend bash"
echo ""

# Step 9: Follow logs
print_info "Showing application logs (Ctrl+C to exit, app keeps running)..."
echo ""
sleep 2

docker-compose logs -f

