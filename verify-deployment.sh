#!/bin/bash

# Post-deployment verification script
# Run this after deploying to verify everything is working

set +e

echo "================================================"
echo "AWS Career Guidance AI - Deployment Verification"
echo "================================================"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

check_pass() {
    echo -e "${GREEN}✓${NC} $1"
}

check_fail() {
    echo -e "${RED}✗${NC} $1"
}

check_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

# Get stack outputs
echo "Fetching deployment information..."
REGION=$(aws configure get region || echo "us-east-1")

if ! aws cloudformation describe-stacks --stack-name aws-agetic-ai --region $REGION > /dev/null 2>&1; then
    check_fail "Stack 'aws-agetic-ai' not found. Have you deployed yet?"
    echo ""
    echo "Deploy with: ./deploy.sh"
    exit 1
fi

echo ""
echo "Stack Status:"
STACK_STATUS=$(aws cloudformation describe-stacks --stack-name aws-agetic-ai --region $REGION --query 'Stacks[0].StackStatus' --output text 2>/dev/null)
echo "  Status: $STACK_STATUS"

if [[ "$STACK_STATUS" == *"IN_PROGRESS"* ]]; then
    check_info "Deployment still in progress... Please wait."
    exit 0
elif [[ "$STACK_STATUS" == *"COMPLETE"* ]]; then
    check_pass "Stack deployment complete"
else
    check_fail "Stack in unexpected state: $STACK_STATUS"
    exit 1
fi

# Get outputs
echo ""
echo "Deployment Outputs:"
CLOUDFRONT_URL=$(aws cloudformation describe-stacks --stack-name aws-agetic-ai --region $REGION --query 'Stacks[0].Outputs[?OutputKey==`CloudFrontURL`].OutputValue' --output text 2>/dev/null)
ALB_URL=$(aws cloudformation describe-stacks --stack-name aws-agetic-ai --region $REGION --query 'Stacks[0].Outputs[?OutputKey==`LoadBalancerURL`].OutputValue' --output text 2>/dev/null)
EC2_IP=$(aws cloudformation describe-stacks --stack-name aws-agetic-ai --region $REGION --query 'Stacks[0].Outputs[?OutputKey==`EC2InstanceIP`].OutputValue' --output text 2>/dev/null)

echo "  CloudFront URL: $CLOUDFRONT_URL"
echo "  Load Balancer URL: $ALB_URL"
echo "  EC2 Instance IP: $EC2_IP"

# Save to file
cat > deployment-info.txt << EOF
AWS Career Guidance AI - Deployment Information
================================================

CloudFront URL: $CLOUDFRONT_URL
Load Balancer URL: $ALB_URL
EC2 Instance IP: $EC2_IP

Access your application at:
$CLOUDFRONT_URL

API Documentation:
${CLOUDFRONT_URL}/docs

Health Check:
${CLOUDFRONT_URL}/health

SSH Access:
ssh -i aws-agetic-ai-key.pem ec2-user@${EC2_IP}

Deployed on: $(date)
Region: $REGION
EOF

check_pass "Deployment info saved to deployment-info.txt"

# Test endpoints
echo ""
echo "Testing Endpoints:"

# Wait a bit for services to be ready
sleep 2

# Test health endpoint via ALB (direct)
echo -n "  Testing ALB health endpoint... "
if curl -s -f -m 10 "${ALB_URL}/health" > /dev/null 2>&1; then
    check_pass "ALB backend is responding"
else
    check_fail "ALB backend not responding yet (may still be starting up)"
fi

# Test CloudFront (may take longer to propagate)
echo -n "  Testing CloudFront... "
if curl -s -f -m 10 -o /dev/null "${CLOUDFRONT_URL}" 2>&1; then
    check_pass "CloudFront is serving content"
else
    check_fail "CloudFront not ready yet (wait 5-10 min for propagation)"
fi

# Test CloudFront health endpoint
echo -n "  Testing CloudFront → Backend connection... "
if curl -s -f -m 10 "${CLOUDFRONT_URL}/health" > /dev/null 2>&1; then
    check_pass "CloudFront → Backend working"
else
    check_fail "CloudFront → Backend not connected yet (wait a few minutes)"
fi

# Check EC2 instance status
echo ""
echo "EC2 Instance Status:"
INSTANCE_ID=$(aws ec2 describe-instances --region $REGION --filters "Name=tag:Name,Values=*aws-agetic-ai*" "Name=instance-state-name,Values=running" --query 'Reservations[0].Instances[0].InstanceId' --output text 2>/dev/null)

if [ "$INSTANCE_ID" != "None" ] && [ -n "$INSTANCE_ID" ]; then
    INSTANCE_STATE=$(aws ec2 describe-instances --instance-ids $INSTANCE_ID --region $REGION --query 'Reservations[0].Instances[0].State.Name' --output text 2>/dev/null)
    echo "  Instance ID: $INSTANCE_ID"
    echo "  State: $INSTANCE_STATE"
    
    if [ "$INSTANCE_STATE" == "running" ]; then
        check_pass "EC2 instance is running"
    else
        check_fail "EC2 instance not running: $INSTANCE_STATE"
    fi
else
    check_fail "Could not find EC2 instance"
fi

# Check ALB target health
echo ""
echo "Load Balancer Health:"
TARGET_GROUP_ARN=$(aws elbv2 describe-target-groups --region $REGION --query 'TargetGroups[?contains(TargetGroupName, `aws-agetic-ai`)].TargetGroupArn' --output text 2>/dev/null | head -1)

if [ -n "$TARGET_GROUP_ARN" ]; then
    HEALTH_STATUS=$(aws elbv2 describe-target-health --target-group-arn $TARGET_GROUP_ARN --region $REGION --query 'TargetHealthDescriptions[0].TargetHealth.State' --output text 2>/dev/null)
    echo "  Target Health: $HEALTH_STATUS"
    
    if [ "$HEALTH_STATUS" == "healthy" ]; then
        check_pass "Load balancer target is healthy"
    elif [ "$HEALTH_STATUS" == "initial" ]; then
        check_info "Health check in progress (initial state)"
    else
        check_fail "Target not healthy: $HEALTH_STATUS"
    fi
else
    check_fail "Could not find target group"
fi

# Summary
echo ""
echo "================================================"
echo "Summary"
echo "================================================"
echo ""
echo -e "${GREEN}Your application is deployed!${NC}"
echo ""
echo "🌐 Access your app at:"
echo "   $CLOUDFRONT_URL"
echo ""
echo "📚 API Documentation:"
echo "   ${CLOUDFRONT_URL}/docs"
echo ""
echo "❤️  Health Check:"
echo "   ${CLOUDFRONT_URL}/health"
echo ""
echo "⚠️  Note: If CloudFront shows 503/404, wait 5-10 minutes for full propagation"
echo ""
echo "🔧 Debug backend if needed:"
echo "   ssh -i aws-agetic-ai-key.pem ec2-user@${EC2_IP}"
echo "   sudo docker logs \$(sudo docker ps -q)"
echo ""
echo "📋 Full deployment info saved to: deployment-info.txt"
echo ""
