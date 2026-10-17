#!/bin/bash

# Pre-deployment checklist script
# Run this before deploying to AWS

set +e  # Don't exit on errors, we want to check everything

echo "================================================"
echo "AWS Career Guidance AI - Pre-Deployment Checks"
echo "================================================"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

ERRORS=0
WARNINGS=0

check_pass() {
    echo -e "${GREEN}✓${NC} $1"
}

check_fail() {
    echo -e "${RED}✗${NC} $1"
    ((ERRORS++))
}

check_warn() {
    echo -e "${YELLOW}⚠${NC} $1"
    ((WARNINGS++))
}

# Check 1: Docker
echo "1. Checking Docker..."
if docker info > /dev/null 2>&1; then
    check_pass "Docker is running"
else
    check_fail "Docker is NOT running - please start Docker Desktop"
fi

# Check 2: Python
echo "2. Checking Python..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)
    
    if [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -ge 12 ]; then
        check_pass "Python $PYTHON_VERSION (>= 3.12 required)"
    else
        check_fail "Python $PYTHON_VERSION found, but 3.12+ required"
    fi
else
    check_fail "Python 3 not found"
fi

# Check 3: Node.js
echo "3. Checking Node.js..."
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version | cut -d'v' -f2)
    NODE_MAJOR=$(echo $NODE_VERSION | cut -d'.' -f1)
    
    if [ "$NODE_MAJOR" -ge 18 ]; then
        check_pass "Node.js v$NODE_VERSION (>= 18 required)"
    else
        check_fail "Node.js v$NODE_VERSION found, but 18+ required"
    fi
else
    check_fail "Node.js not found"
fi

# Check 4: AWS CLI
echo "4. Checking AWS CLI..."
if command -v aws &> /dev/null; then
    AWS_VERSION=$(aws --version 2>&1 | cut -d' ' -f1)
    check_pass "AWS CLI installed ($AWS_VERSION)"
else
    check_fail "AWS CLI not found"
fi

# Check 5: AWS Credentials
echo "5. Checking AWS credentials..."
if aws sts get-caller-identity > /dev/null 2>&1; then
    ACCOUNT=$(aws sts get-caller-identity --query Account --output text 2>/dev/null)
    ARN=$(aws sts get-caller-identity --query Arn --output text 2>/dev/null)
    check_pass "AWS credentials configured (Account: $ACCOUNT)"
else
    check_fail "AWS credentials not configured - run 'aws configure'"
fi

# Check 6: AWS Region
echo "6. Checking AWS region..."
REGION=$(aws configure get region 2>/dev/null)
if [ -z "$REGION" ]; then
    check_warn "No default region set - will use us-east-1"
    export CDK_DEFAULT_REGION="us-east-1"
else
    check_pass "AWS region: $REGION"
    export CDK_DEFAULT_REGION="$REGION"
fi

# Check 7: CDK
echo "7. Checking AWS CDK..."
if command -v cdk &> /dev/null; then
    CDK_VERSION=$(cdk --version 2>&1)
    check_pass "AWS CDK installed ($CDK_VERSION)"
else
    check_warn "AWS CDK not found - will be installed with dependencies"
fi

# Check 8: CDK Bootstrap
echo "8. Checking CDK bootstrap status..."
export CDK_DEFAULT_ACCOUNT=$(aws sts get-caller-identity --query Account --output text 2>/dev/null)
if [ -n "$CDK_DEFAULT_ACCOUNT" ] && [ -n "$CDK_DEFAULT_REGION" ]; then
    if aws cloudformation describe-stacks --stack-name CDKToolkit --region $CDK_DEFAULT_REGION > /dev/null 2>&1; then
        check_pass "CDK already bootstrapped in $CDK_DEFAULT_REGION"
    else
        check_warn "CDK not bootstrapped - will be done during deployment"
    fi
fi

# Check 9: SSH Key Pair
echo "9. Checking SSH key pair..."
if [ -n "$CDK_DEFAULT_REGION" ]; then
    if aws ec2 describe-key-pairs --key-names aws-agetic-ai-key --region $CDK_DEFAULT_REGION > /dev/null 2>&1; then
        check_pass "SSH key pair 'aws-agetic-ai-key' exists"
    else
        check_warn "SSH key pair not found - will be created during deployment"
    fi
fi

# Check 10: Bedrock Access (requires region)
echo "10. Checking AWS Bedrock access..."
if [ -n "$CDK_DEFAULT_REGION" ]; then
    # Try to list foundation models
    if aws bedrock list-foundation-models --region $CDK_DEFAULT_REGION > /dev/null 2>&1; then
        # Check if Claude 3 Sonnet is available
        if aws bedrock list-foundation-models --region $CDK_DEFAULT_REGION --query "modelSummaries[?contains(modelId, 'claude-3-sonnet')]" 2>/dev/null | grep -q "claude"; then
            check_pass "AWS Bedrock access confirmed (Claude 3 Sonnet available)"
        else
            check_warn "Bedrock accessible but Claude 3 Sonnet may not be enabled"
        fi
    else
        check_warn "Cannot verify Bedrock access - ensure Claude 3 Sonnet is enabled"
    fi
else
    check_warn "Cannot check Bedrock - region not set"
fi

# Check 11: Disk Space
echo "11. Checking disk space..."
AVAILABLE_GB=$(df -BG . | awk 'NR==2 {print $4}' | sed 's/G//')
if [ "$AVAILABLE_GB" -gt 5 ]; then
    check_pass "Sufficient disk space (${AVAILABLE_GB}GB available)"
else
    check_warn "Low disk space (${AVAILABLE_GB}GB available, 5GB+ recommended)"
fi

# Check 12: Frontend dependencies
echo "12. Checking frontend dependencies..."
if [ -f "frontend/package.json" ]; then
    check_pass "Frontend package.json exists"
    if [ -d "frontend/node_modules" ]; then
        check_pass "Frontend node_modules exists"
    else
        check_warn "Frontend dependencies not installed - will be installed during build"
    fi
else
    check_fail "Frontend package.json not found"
fi

# Check 13: Python dependencies
echo "13. Checking Python dependencies..."
if [ -f "requirements.txt" ]; then
    check_pass "requirements.txt exists"
    # Try to import key packages
    if python3 -c "import fastapi, boto3, aws_cdk" 2>/dev/null; then
        check_pass "Key Python dependencies installed"
    else
        check_warn "Some Python dependencies missing - will be installed during deployment"
    fi
else
    check_fail "requirements.txt not found"
fi

# Summary
echo ""
echo "================================================"
echo "Summary"
echo "================================================"

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}All checks passed!${NC} Ready to deploy."
    echo ""
    echo "Run deployment with:"
    echo "  ./deploy.sh"
    echo "or:"
    echo "  cdk deploy --require-approval never"
    exit 0
elif [ $ERRORS -eq 0 ]; then
    echo -e "${YELLOW}$WARNINGS warning(s) found${NC}, but can proceed with deployment."
    echo ""
    echo "Run deployment with:"
    echo "  ./deploy.sh"
    exit 0
else
    echo -e "${RED}$ERRORS error(s) found${NC}, please fix before deploying."
    if [ $WARNINGS -gt 0 ]; then
        echo -e "${YELLOW}$WARNINGS warning(s) also found${NC}"
    fi
    echo ""
    echo "Common fixes:"
    echo "  - Start Docker Desktop"
    echo "  - Run 'aws configure' to set up credentials"
    echo "  - Install Node.js 18+ and Python 3.12+"
    exit 1
fi
