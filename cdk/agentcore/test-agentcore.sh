#!/bin/bash

# Comprehensive test script for standalone AgentCore deployment
set -e

echo "=== Standalone AgentCore Test Suite ==="

# Get real AWS account ID
REAL_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
export CDK_DEFAULT_ACCOUNT=${CDK_DEFAULT_ACCOUNT:-$REAL_ACCOUNT_ID}

# Validate required environment variables
if [ -z "$CDK_DEFAULT_ACCOUNT" ]; then
    echo "ERROR: CDK_DEFAULT_ACCOUNT environment variable must be set"
    exit 1
fi

# Set default region if not provided
export CDK_DEFAULT_REGION=${CDK_DEFAULT_REGION:-us-east-1}

echo "Using Account ID: $CDK_DEFAULT_ACCOUNT"
echo "Using Region: $CDK_DEFAULT_REGION"
echo "Using IAM authentication (no API key required)"
echo "CDK will build and push container automatically"

# Clean up cdk.out directory
echo "Cleaning up cdk.out directory..."
rm -rf cdk.out
echo "cdk.out directory cleaned"

# Force destroy and redeploy stack
echo "Force destroying existing stack..."
npx cdk destroy --force || true

echo "Deploying fresh stack (CDK will build container)..."
npx cdk deploy --require-approval never

# Wait for runtime to be ready
echo "Waiting for runtime to be ready..."
sleep 30

# Get runtime ARN using dynamic region
RUNTIME_ARN=$(aws bedrock-agentcore-control list-agent-runtimes --region $CDK_DEFAULT_REGION --query 'agentRuntimes[?agentRuntimeName==`NovaActAgent`].agentRuntimeArn' --output text)
echo "Runtime ARN: $RUNTIME_ARN"

# Verify container image
CONTAINER_URI=$(aws bedrock-agentcore-control get-agent-runtime --agent-runtime-id $(echo $RUNTIME_ARN | cut -d'/' -f2) --region $CDK_DEFAULT_REGION --query 'agentRuntimeArtifact.containerConfiguration.containerUri' --output text)
echo "Container URI: $CONTAINER_URI"

# Create test payload
cat > /tmp/agentcore_test_payload.json << EOF
{
  "prompt": "Navigate to https://example.com and tell me what you see",
  "starting_page": "https://example.com"
}
EOF

# Test runtime invocation
echo "Testing runtime invocation..."
aws bedrock-agentcore invoke-agent-runtime \
  --agent-runtime-arn "$RUNTIME_ARN" \
  --payload file:///tmp/agentcore_test_payload.json \
  --content-type "application/json" \
  --accept "application/json" \
  /tmp/agentcore_response.json

echo "Response:"
cat /tmp/agentcore_response.json

# Clean up test files
rm -f /tmp/agentcore_test_payload.json /tmp/agentcore_response.json

# Teardown - destroy the stack
echo "Tearing down stack..."
npx cdk destroy --force

echo "=== Standalone AgentCore Test Complete ==="
