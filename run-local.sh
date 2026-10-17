#!/bin/bash

# Local Development Script for AWS Agetic AI Career Guidance System
# This script sets up and runs both backend and frontend locally

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
if [ ! -f "start_server.py" ]; then
    print_error "Please run this script from the aws-agetic-ai directory"
    exit 1
fi

print_header "UTD Career Guidance AI - Local Development Setup"
echo ""

# Step 1: Check prerequisites
print_info "Step 1: Checking prerequisites..."
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    print_error "Python is not installed. Please install Python 3.11+ first."
    exit 1
fi
print_success "Python is installed ($(python3 --version))"

# Check Node.js
if ! command -v node &> /dev/null; then
    print_error "Node.js is not installed. Please install Node.js 18+ first."
    exit 1
fi
print_success "Node.js is installed ($(node --version))"

# Check npm
if ! command -v npm &> /dev/null; then
    print_error "npm is not installed. Please install npm first."
    exit 1
fi
print_success "npm is installed ($(npm --version))"

echo ""

# Step 2: Install Python dependencies
print_info "Step 2: Installing Python dependencies..."
echo ""

if [ ! -d "venv" ]; then
    print_info "Creating virtual environment..."
    python3 -m venv venv
    print_success "Virtual environment created"
fi

print_info "Activating virtual environment..."
source venv/bin/activate

print_info "Installing Python packages..."
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt
print_success "Python dependencies installed"

echo ""

# Step 3: Check AWS credentials (optional for local testing)
print_info "Step 3: Checking AWS credentials..."
echo ""

if [ -z "$AWS_ACCESS_KEY_ID" ] || [ -z "$AWS_SECRET_ACCESS_KEY" ]; then
    print_warning "AWS credentials not set in environment variables"
    print_info "The system will work with limited functionality"
    print_info "For full AI features, set your AWS credentials:"
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
fi

echo ""

# Step 4: Install Frontend dependencies
print_info "Step 4: Installing Frontend dependencies..."
echo ""

cd frontend

if [ ! -d "node_modules" ]; then
    print_info "Installing npm packages (this may take a few minutes)..."
    npm install
    print_success "Frontend dependencies installed"
else
    print_success "Frontend dependencies already installed"
fi

cd ..

echo ""

# Step 5: Start the servers
print_header "Starting Development Servers"
echo ""

print_success "Backend will run on: http://127.0.0.1:8000"
print_success "API Docs available at: http://127.0.0.1:8000/docs"
print_success "Frontend will run on: http://localhost:5173"
echo ""
print_warning "Press Ctrl+C to stop both servers"
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    print_info "Shutting down servers..."
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    print_success "Servers stopped"
    exit 0
}

trap cleanup SIGINT SIGTERM

# Start backend in background
print_info "Starting backend server..."
source venv/bin/activate
python -m uvicorn src.api.app:app --reload --host 127.0.0.1 --port 8000 > backend.log 2>&1 &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 2

# Check if backend started successfully
if ! kill -0 $BACKEND_PID 2>/dev/null; then
    print_error "Backend failed to start. Check backend.log for details."
    cat backend.log
    exit 1
fi
print_success "Backend started (PID: $BACKEND_PID)"

# Start frontend in background
print_info "Starting frontend server..."
cd frontend
npm run dev > ../frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..

# Wait a moment for frontend to start
sleep 3

# Check if frontend started successfully
if ! kill -0 $FRONTEND_PID 2>/dev/null; then
    print_error "Frontend failed to start. Check frontend.log for details."
    cat frontend.log
    kill $BACKEND_PID 2>/dev/null || true
    exit 1
fi
print_success "Frontend started (PID: $FRONTEND_PID)"

echo ""
print_header "🚀 Development Environment Running!"
echo ""
print_success "Backend API: http://127.0.0.1:8000"
print_success "API Documentation: http://127.0.0.1:8000/docs"
print_success "Frontend App: http://localhost:5173"
echo ""
print_info "Logs are being written to backend.log and frontend.log"
print_info "Press Ctrl+C to stop all servers"
echo ""

# Follow logs
tail -f backend.log frontend.log

