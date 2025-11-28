#!/bin/bash

# Full test script for standalone Fargate CDK deployment
set -e

STACK_NAME="NovaActFargateStack"
APP_CMD="npx ts-node fargate-app.ts"

cleanup() {
    echo "Cleaning up resources..."
    npx cdk destroy --app "$APP_CMD" --force || true
    rm -rf cdk.out
}

trap cleanup EXIT

echo "Starting full Fargate deployment test..."

# Clean CDK output directory
echo "Cleaning CDK output directory..."
rm -rf cdk.out

# Bootstrap CDK
echo "Bootstrapping CDK..."
npx cdk bootstrap --app "$APP_CMD" --require-approval never

# Deploy the stack
echo "Deploying Fargate stack..."
npx cdk deploy --app "$APP_CMD" --require-approval never

# Wait for service to be stable
echo "Waiting for Fargate service to stabilize..."
CLUSTER_NAME=$(aws ecs list-clusters --query "clusterArns[?contains(@, '$STACK_NAME')]" --output text | head -1)
SERVICE_NAME=$(aws ecs list-services --cluster "$CLUSTER_NAME" --query "serviceArns[0]" --output text)

if [ -n "$SERVICE_NAME" ]; then
    aws ecs wait services-stable --cluster "$CLUSTER_NAME" --services "$SERVICE_NAME"
    echo "Service is stable"
    
    # Check task status
    TASK_ARN=$(aws ecs list-tasks --cluster "$CLUSTER_NAME" --service-name "$SERVICE_NAME" --query "taskArns[0]" --output text)
    if [ -n "$TASK_ARN" ] && [ "$TASK_ARN" != "None" ]; then
        echo "Task is running: $TASK_ARN"
        
        # Get task logs (last 10 minutes)
        LOG_GROUP="/aws/ecs/$STACK_NAME"
        echo "Checking recent logs..."
        aws logs describe-log-streams --log-group-name "$LOG_GROUP" --order-by LastEventTime --descending --max-items 1 --query "logStreams[0].logStreamName" --output text | xargs -I {} aws logs get-log-events --log-group-name "$LOG_GROUP" --log-stream-name {} --start-time $(($(date +%s) * 1000 - 600000)) --query "events[].message" --output text || echo "No recent logs found"
    else
        echo "No tasks found"
    fi
else
    echo "Service not found"
fi

echo "Full deployment test completed successfully!"
