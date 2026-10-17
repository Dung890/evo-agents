#!/bin/bash

# Deployment script for AWS Agetic AI Career Guidance System
# This script automates the deployment process

set -e  # Exit on any error

echo "======================================"
echo "AWS Agetic AI - Deployment Script"
echo "======================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
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
    echo -e "${NC}ℹ $1${NC}"
}

# Step 1: Check prerequisites
echo "Step 1: Checking prerequisites..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker Desktop and try again."
    exit 1
fi
print_success "Docker is running"

# Check if AWS CLI is configured
if ! aws sts get-caller-identity > /dev/null 2>&1; then
    print_error "AWS CLI is not configured. Please run 'aws configure' first."
    exit 1
fi
print_success "AWS CLI is configured"

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    print_error "Node.js is not installed. Please install Node.js 18+ first."
    exit 1
fi
print_success "Node.js is installed ($(node --version))"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed. Please install Python 3.12+ first."
    exit 1
fi
print_success "Python is installed ($(python3 --version))"

# Step 2: Set environment variables
echo ""
echo "Step 2: Setting up environment variables..."

export CDK_DEFAULT_ACCOUNT=$(aws sts get-caller-identity --query Account --output text)
export CDK_DEFAULT_REGION=$(aws configure get region)

if [ -z "$CDK_DEFAULT_REGION" ]; then
    export CDK_DEFAULT_REGION="us-east-1"
    print_warning "No default region set, using us-east-1"
fi

print_success "AWS Account: $CDK_DEFAULT_ACCOUNT"
print_success "AWS Region: $CDK_DEFAULT_REGION"

# Step 3: Check for SSH key pair
echo ""
echo "Step 3: Checking SSH key pair..."

if ! aws ec2 describe-key-pairs --key-names aws-agetic-ai-key --region $CDK_DEFAULT_REGION > /dev/null 2>&1; then
    print_warning "SSH key pair 'aws-agetic-ai-key' not found in region $CDK_DEFAULT_REGION"
    read -p "Do you want to create it now? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        aws ec2 create-key-pair \
            --key-name aws-agetic-ai-key \
            --query 'KeyMaterial' \
            --output text > aws-agetic-ai-key.pem
        chmod 400 aws-agetic-ai-key.pem
        print_success "SSH key pair created and saved to aws-agetic-ai-key.pem"
    else
        print_error "Cannot continue without SSH key pair. Please create it manually."
        exit 1
    fi
else
    print_success "SSH key pair exists"
fi

# Step 4: Install Python dependencies
echo ""
echo "Step 4: Installing Python dependencies..."
# Use python3 -m pip to ensure we install into the same Python interpreter
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 not found. Install Python 3.12+ and retry."
    exit 1
fi
python3 -m pip install --upgrade pip >/dev/null 2>&1 || true
python3 -m pip install -q -r requirements.txt
print_success "Python dependencies installed"

# Step 5: Bootstrap CDK (if needed)
echo ""
echo "Step 5: Checking CDK bootstrap..."

# Ensure AWS CDK is installed and available
if ! command -v cdk &> /dev/null; then
    print_error "AWS CDK (cdk) not found. Install it with: npm install -g aws-cdk"
    exit 1
fi
print_success "AWS CDK is installed ($(cdk --version))"

if ! aws cloudformation describe-stacks --stack-name CDKToolkit --region $CDK_DEFAULT_REGION > /dev/null 2>&1; then
    print_warning "CDK not bootstrapped in this region"
    print_info "Bootstrapping CDK (this may take a few minutes)..."
    cdk bootstrap aws://$CDK_DEFAULT_ACCOUNT/$CDK_DEFAULT_REGION
    print_success "CDK bootstrapped"
else
    print_success "CDK already bootstrapped"
fi

# Step 6: Synthesize CDK template
echo ""
echo "Step 6: Synthesizing CDK template..."
cdk synth > /dev/null 2>&1
print_success "CDK template synthesized"

# Step 7: Deploy
echo ""
echo "Step 7: Deploying to AWS..."
print_warning "This will take 10-15 minutes. Please be patient..."
echo ""

# Ask for confirmation
read -p "Ready to deploy? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_error "Deployment cancelled"
    exit 1
fi

# Deploy with CDK
cdk deploy --require-approval never

# Step 8: Show outputs
echo ""
echo "======================================"
echo "Deployment Complete!"
echo "======================================"
print_success "Your application has been deployed successfully!"
echo ""
print_info "It may take 5-10 minutes for CloudFront to fully propagate."
echo ""
print_info "Access your application using the CloudFrontURL shown above."
echo ""

# Save outputs to a file
echo "Saving deployment outputs to deployment-outputs.txt..."
aws cloudformation describe-stacks \
    --stack-name aws-agetic-ai \
    --query 'Stacks[0].Outputs' \
    --region $CDK_DEFAULT_REGION > deployment-outputs.txt 2>/dev/null || true

print_success "Done! Check DEPLOYMENT_GUIDE.md for next steps."
