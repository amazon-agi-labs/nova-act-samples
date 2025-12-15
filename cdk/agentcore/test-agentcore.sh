#!/bin/bash

# Full test script: deploy + invoke + teardown
set -e

echo "🚀 Starting standalone AgentCore deployment test..."

STACK_NAME="NovaActAgentCoreStack"
APP_CMD="npx ts-node agentcore-app.ts"

# Clean up any previous deployments
echo "🧹 Cleaning up cdk.out directory..."
rm -rf cdk.out

# Deploy the stack
echo "🏗️  Deploying AgentCore stack..."
npx cdk deploy --app "$APP_CMD" --require-approval never

# Wait for runtime to be ready
echo "⏳ Waiting for runtime to be ready..."
sleep 30

# Get runtime ARN using dynamic region
REGION=$(aws configure get region || echo "us-east-1")
RUNTIME_ARN=$(aws bedrock-agentcore-control list-agent-runtimes --region $REGION --query 'agentRuntimes[?agentRuntimeName==`NovaActAgent`].agentRuntimeArn' --output text)
echo "Runtime ARN: $RUNTIME_ARN"

# Verify container image
CONTAINER_URI=$(aws bedrock-agentcore-control get-agent-runtime --agent-runtime-id $(echo $RUNTIME_ARN | cut -d'/' -f2) --region $REGION --query 'agentRuntimeArtifact.containerConfiguration.containerUri' --output text)
echo "Container URI: $CONTAINER_URI"

# Create test payload and encode as base64
PAYLOAD_JSON='{"prompt": "Find flights from Boston to Wolf on Feb 22nd", "starting_page": "https://nova.amazon.com/act/gym/next-dot/search"}'
PAYLOAD_BASE64=$(echo -n "$PAYLOAD_JSON" | base64)

# Test runtime invocation with extended timeout
echo "▶️ Testing runtime invocation..."
aws bedrock-agentcore invoke-agent-runtime \
  --agent-runtime-arn "$RUNTIME_ARN" \
  --payload "$PAYLOAD_BASE64" \
  --content-type "application/json" \
  --accept "application/json" \
  --cli-read-timeout 300 \
  /tmp/agentcore_response.json

echo "📋 Response:"
cat /tmp/agentcore_response.json

# Clean up test files
rm -f /tmp/agentcore_response.json

# Teardown - destroy the stack
echo ""
echo "🗑️ Tearing down stack..."
npx cdk destroy --app "$APP_CMD" --force

echo "🎉 Standalone AgentCore deployment test completed successfully!"