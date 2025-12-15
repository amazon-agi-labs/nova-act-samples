#!/bin/bash

# Full test script: deploy + invoke + teardown
set -e

echo "🚀 Starting full Lambda deployment test..."

STACK_NAME="NovaActLambdaStack"
APP_CMD="npx ts-node lambda-app.ts"

# Clean up any previous deployments
echo "🧹 Cleaning CDK output directory..."
rm -rf cdk.out

# Deploy the stack
echo "🏗️ Deploying Lambda stack..."
npx cdk deploy --app "$APP_CMD" --require-approval never

# Get function name
FUNCTION_NAME=$(aws lambda list-functions --query "Functions[?starts_with(FunctionName, '$STACK_NAME-NovaActLambdaFunction')].FunctionName" --output text)
echo "Found Lambda function: $FUNCTION_NAME"

# Invoke function with extended timeout
echo "▶️ Invoking Lambda function..."
aws lambda invoke \
  --function-name "$FUNCTION_NAME" \
  --cli-binary-format raw-in-base64-out \
  --cli-read-timeout 300 \
  --payload '{"prompt":"Find flights from Boston to Wolf on Feb 22nd","starting_page":"https://nova.amazon.com/act/gym/next-dot/search"}' \
  response.json

echo "📋 Lambda response:"
cat response.json
echo

# Cleanup
rm -f response.json

# Teardown
echo ""
echo "🗑️ Destroying Lambda stack..."
npx cdk destroy --app "$APP_CMD" --force

echo "🎉 Full Lambda deployment test completed successfully!"