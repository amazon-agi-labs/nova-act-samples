#!/bin/bash

# Full test script for standalone Fargate CDK deployment
set -e

STACK_NAME="NovaActFargateStack"
APP_CMD="npx ts-node fargate-app.ts"

echo "🧹 Cleaning up previous deployments..."
rm -rf cdk.out

echo "Starting full Fargate deployment test..."

# Deploy the stack
echo "Deploying Fargate stack..."
npx cdk deploy --app "$APP_CMD" --require-approval never

# Get cluster and task definition info
echo "Getting cluster and task definition info..."
CLUSTER_ARN=$(aws ecs list-clusters --query 'clusterArns[?contains(@, `'$STACK_NAME'`)] | [0]' --output text)
CLUSTER_NAME=$(echo $CLUSTER_ARN | cut -d'/' -f2)
TASK_DEF_ARN=$(aws ecs list-task-definitions --query 'taskDefinitionArns[?contains(@, `'$STACK_NAME'`)] | [0]' --output text)

if [ "$CLUSTER_ARN" == "None" ] || [ "$TASK_DEF_ARN" == "None" ]; then
    echo "❌ Failed to get cluster or task definition ARNs"
    exit 1
fi

echo "✅ Cluster: $CLUSTER_NAME"
echo "✅ Task Definition: $TASK_DEF_ARN"

# Get network configuration
echo "Getting network configuration..."
VPC_ID=$(aws ec2 describe-vpcs --filters "Name=tag:Name,Values=*$STACK_NAME*" --query 'Vpcs[0].VpcId' --output text)
SUBNET_ID=$(aws ec2 describe-subnets --filters "Name=vpc-id,Values=$VPC_ID" "Name=tag:Name,Values=*Private*" --query 'Subnets[0].SubnetId' --output text)
SECURITY_GROUP_ID=$(aws ec2 describe-security-groups --filters "Name=group-name,Values=*$STACK_NAME*" "Name=vpc-id,Values=$VPC_ID" --query 'SecurityGroups[0].GroupId' --output text)

echo "✅ VPC: $VPC_ID"
echo "✅ Subnet: $SUBNET_ID"
echo "✅ Security Group: $SECURITY_GROUP_ID"

NETWORK_CONFIG="awsvpcConfiguration={subnets=[$SUBNET_ID],securityGroups=[$SECURITY_GROUP_ID],assignPublicIp=DISABLED}"

# Run a test task with custom environment variables
echo "▶️  Running test task with custom prompt and starting page..."
TASK_ARN=$(aws ecs run-task \
    --cluster $CLUSTER_NAME \
    --task-definition $TASK_DEF_ARN \
    --launch-type FARGATE \
    --network-configuration "$NETWORK_CONFIG" \
    --overrides '{
        "containerOverrides": [{
            "name": "AppContainer",
            "environment": [
                {"name": "NOVA_ACT_PROMPT", "value": "Find flights from SF to Wolf on Feb 22nd"},
                {"name": "NOVA_ACT_STARTING_PAGE", "value": "https://nova.amazon.com/act/gym/next-dot/search"}
            ]
        }]
    }' \
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
npx cdk destroy --app "npx ts-node fargate-app.ts" --force

echo "🎉 Full Fargate deployment test completed successfully!"
echo "✅ Deploy → Invoke → Teardown cycle validated"
