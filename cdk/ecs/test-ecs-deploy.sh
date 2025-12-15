#!/bin/bash

# Full test script: deploy + invoke + teardown
set -e

echo "🚀 Starting full ECS deployment test..."

STACK_NAME="NovaActEcsStack"
APP_CMD="npx ts-node ecs-app.ts"

# Clean up any previous deployments
echo "🧹 Cleaning up previous deployments..."
rm -rf cdk.out

# Deploy the stack
echo "🏗️  Deploying ECS stack..."
npx cdk deploy --app "$APP_CMD" --require-approval never

# Get cluster and task definition info
echo "🔍 Getting cluster and task definition info..."
CLUSTER_ARN=$(aws ecs list-clusters --query 'clusterArns[?contains(@, `'$STACK_NAME'`)] | [0]' --output text)
if [ "$CLUSTER_ARN" == "None" ] || [ -z "$CLUSTER_ARN" ]; then
    echo "❌ Failed to find cluster for stack $STACK_NAME"
    exit 1
fi
CLUSTER_NAME=$(echo $CLUSTER_ARN | cut -d'/' -f2)

TASK_DEF_ARN=$(aws ecs list-task-definitions --query 'taskDefinitionArns[?contains(@, `'$STACK_NAME'`)] | [0]' --output text)
if [ "$TASK_DEF_ARN" == "None" ] || [ -z "$TASK_DEF_ARN" ]; then
    echo "❌ Failed to find task definition for stack $STACK_NAME"
    exit 1
fi

echo "✅ Cluster ARN: $CLUSTER_ARN"
echo "✅ Task Definition ARN: $TASK_DEF_ARN"

# Wait for container instances to register with the cluster
echo "⏳ Waiting for container instances to register..."
CONTAINER_WAIT_TIMEOUT=300  # 5 minutes
CONTAINER_WAIT_ELAPSED=0
CONTAINER_WAIT_INTERVAL=15

while [ $CONTAINER_WAIT_ELAPSED -lt $CONTAINER_WAIT_TIMEOUT ]; do
    CONTAINER_COUNT=$(aws ecs describe-clusters \
        --clusters $CLUSTER_NAME \
        --query 'clusters[0].registeredContainerInstancesCount' \
        --output text)
    
    echo "Container instances registered: $CONTAINER_COUNT"
    
    if [ "$CONTAINER_COUNT" -gt "0" ]; then
        echo "✅ Container instances are ready!"
        break
    fi
    
    sleep $CONTAINER_WAIT_INTERVAL
    CONTAINER_WAIT_ELAPSED=$((CONTAINER_WAIT_ELAPSED + CONTAINER_WAIT_INTERVAL))
done

if [ $CONTAINER_WAIT_ELAPSED -ge $CONTAINER_WAIT_TIMEOUT ]; then
    echo "❌ Timeout waiting for container instances to register"
    exit 1
fi

# Run a test task
echo "▶️  Running test task..."
TASK_ARN=$(aws ecs run-task \
    --cluster $CLUSTER_NAME \
    --task-definition $TASK_DEF_ARN \
    --launch-type EC2 \
    --query 'tasks[0].taskArn' \
    --output text)

if [ "$TASK_ARN" == "None" ]; then
    echo "❌ Failed to start task"
    exit 1
fi

echo "✅ Task started: $TASK_ARN"

# Wait for task to complete (with timeout)
echo "⏳ Waiting for task to complete..."
TIMEOUT=300  # 5 minutes
ELAPSED=0
INTERVAL=10

while [ $ELAPSED -lt $TIMEOUT ]; do
    TASK_STATUS=$(aws ecs describe-tasks \
        --cluster $CLUSTER_NAME \
        --tasks $TASK_ARN \
        --query 'tasks[0].lastStatus' \
        --output text)
    
    echo "Task status: $TASK_STATUS"
    
    if [ "$TASK_STATUS" == "STOPPED" ]; then
        # Get exit code
        EXIT_CODE=$(aws ecs describe-tasks \
            --cluster $CLUSTER_NAME \
            --tasks $TASK_ARN \
            --query 'tasks[0].containers[0].exitCode' \
            --output text)
        
        if [ "$EXIT_CODE" == "0" ]; then
            echo "✅ Task completed successfully!"
            break
        else
            echo "❌ Task failed with exit code: $EXIT_CODE"
            exit 1
        fi
    fi
    
    sleep $INTERVAL
    ELAPSED=$((ELAPSED + INTERVAL))
done

if [ $ELAPSED -ge $TIMEOUT ]; then
    echo "❌ Task execution timed out"
    exit 1
fi

# Show task logs
echo "📋 Task logs:"
LOG_GROUP=$(aws ecs describe-task-definition \
    --task-definition $TASK_DEF_ARN \
    --query 'taskDefinition.containerDefinitions[0].logConfiguration.options."awslogs-group"' \
    --output text)
LOG_STREAM=$(aws logs describe-log-streams \
    --log-group-name $LOG_GROUP \
    --order-by LastEventTime \
    --descending \
    --limit 1 \
    --query 'logStreams[0].logStreamName' \
    --output text)

if [ "$LOG_STREAM" != "None" ]; then
    aws logs get-log-events \
        --log-group-name $LOG_GROUP \
        --log-stream-name $LOG_STREAM \
        --query 'events[].message' \
        --output text
fi

# Teardown
echo "🗑️  Tearing down stack..."
npx cdk destroy --app "$APP_CMD" --force

echo "🎉 Full ECS deployment test completed successfully!"
echo "✅ Deploy → Invoke → Teardown cycle validated"