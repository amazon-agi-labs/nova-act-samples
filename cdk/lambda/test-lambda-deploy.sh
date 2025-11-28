#!/bin/bash

# Full test script: deploy + invoke + teardown
set -e

echo "Starting full Lambda deployment test..."

# Get actual AWS account and region
ACCOUNT=$(aws sts get-caller-identity --query Account --output text)
REGION=$(aws configure get region || echo "us-east-1")

export CDK_DEFAULT_ACCOUNT=$ACCOUNT
export CDK_DEFAULT_REGION=$REGION

echo "Using AWS Account: $ACCOUNT, Region: $REGION"

# Clean up
echo "Cleaning CDK output directory..."
rm -rf cdk.out

# Deploy
echo "Deploying Lambda stack..."
npx cdk deploy --app "npx ts-node lambda-app.ts" --require-approval never

# Get function name
FUNCTION_NAME=$(aws lambda list-functions --query "Functions[?starts_with(FunctionName, 'NovaActLambdaStack-NovaActWithIAMFunction')].FunctionName" --output text)
echo "Found Lambda function: $FUNCTION_NAME"

# Invoke function
echo "Invoking Lambda function..."
aws lambda invoke \
  --function-name "$FUNCTION_NAME" \
  --payload '{"prompts":["Go to google.com"],"starting_page":"https://google.com"}' \
  response.json

echo "Lambda response:"
cat response.json
echo

# Teardown
echo "Destroying Lambda stack..."
npx cdk destroy --app "npx ts-node lambda-app.ts" --force

# Cleanup
rm -f response.json
rm -rf cdk.out

echo "Full Lambda deployment test completed successfully!"
