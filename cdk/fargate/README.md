# Amazon Nova Act Fargate Example

Deploy Amazon Nova Act on AWS Fargate using container images with API key authentication.

## Prerequisites

1. See the [main CDK README](../README.md) for complete prerequisites and setup instructions.

## Quick Start

```bash
export CDK_DEFAULT_ACCOUNT="123456789012"
export CDK_DEFAULT_REGION="us-east-1"
export NOVA_ACT_API_KEY="your-api-key"
npx cdk deploy --app "npx ts-node fargate-app.ts"
```

## Files

- `fargate-stack.ts` - Complete Fargate stack with NovaActVpc and NovaActFargate constructs
- `fargate-app.ts` - CDK application entry point with environment validation
- `app.py` - Nova Act Fargate application with error handling and structured logging
- `Dockerfile` - Container configuration with Playwright and Python 3.12
- `requirements.txt` - Python dependencies (nova-act)
- `test-fargate-deploy.sh` - Complete deployment test (deploy → invoke → teardown)

## Architecture

This example creates:
- **VPC** with private/public subnets across 2 AZs and VPC Flow Logs
- **VPC Endpoints** for SSM, EC2 Messages, and SSM Messages
- **Security Group** with controlled egress (HTTP/HTTPS/DNS only)
- **ECS Cluster** with Fargate capacity provider and container insights
- **Fargate Task Definition** with Nova Act container
- **CloudWatch Logs** with non-blocking mode for monitoring

## Configuration

Default configuration:
- **CPU**: 2048 units (configurable)
- **Memory**: 4096 MB (configurable)
- **Platform**: Linux AMD64
- **Network**: Private subnets with NAT gateway
- **Browser Arguments**: `--disable-gpu --disable-dev-shm-usage --no-sandbox --single-process`

## Handler Implementation

The `app.py` file contains:
- Nova Act workflow with Fargate task implementation
- Error handling with structured logging and exception handling
- Nova Act API key loaded from environment variables
- Default prompt and starting page configuration

### Payload Structure

**Parameters:**
- `NOVA_ACT_PROMPT` (optional): Environment variable for prompt to execute. Defaults to flight search example.
- `NOVA_ACT_STARTING_PAGE` (optional): Environment variable for starting URL. Defaults to Nova Act gym.

**Example environment variables:**
```bash
NOVA_ACT_PROMPT="Find flights from Boston to Wolf on Feb 22nd"
NOVA_ACT_STARTING_PAGE="https://nova.amazon.com/act/gym/next-dot/search"
```

## Task Execution

Tasks are executed on-demand:

```bash
# Get cluster and task definition names
CLUSTER_NAME=$(aws ecs list-clusters --query 'clusterArns[?contains(@, `NovaActFargateStack`)] | [0]' --output text | cut -d'/' -f2)
TASK_DEF_ARN=$(aws ecs list-task-definitions --query 'taskDefinitionArns[?contains(@, `NovaActFargateStack`)] | [0]' --output text)

# Get network configuration
VPC_ID=$(aws ec2 describe-vpcs --filters "Name=tag:Name,Values=*NovaActFargateStack*" --query 'Vpcs[0].VpcId' --output text)
SUBNET_ID=$(aws ec2 describe-subnets --filters "Name=vpc-id,Values=$VPC_ID" "Name=tag:Name,Values=*Private*" --query 'Subnets[0].SubnetId' --output text)
SECURITY_GROUP_ID=$(aws ec2 describe-security-groups --filters "Name=group-name,Values=*NovaActFargateStack*" "Name=vpc-id,Values=$VPC_ID" --query 'SecurityGroups[0].GroupId' --output text)

# Run task with default configuration
aws ecs run-task \
  --cluster $CLUSTER_NAME \
  --task-definition $TASK_DEF_ARN \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[$SUBNET_ID],securityGroups=[$SECURITY_GROUP_ID],assignPublicIp=DISABLED}"

# Run task with custom prompt and starting page
aws ecs run-task \
  --cluster $CLUSTER_NAME \
  --task-definition $TASK_DEF_ARN \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[$SUBNET_ID],securityGroups=[$SECURITY_GROUP_ID],assignPublicIp=DISABLED}" \
  --overrides '{
    "containerOverrides": [{
      "name": "AppContainer",
      "environment": [
        {"name": "NOVA_ACT_PROMPT", "value": "Find flights from Boston to Wolf on Feb 22nd"},
        {"name": "NOVA_ACT_STARTING_PAGE", "value": "https://nova.amazon.com/act/gym/next-dot/search"}
      ]
    }]
  }'
```

## Testing

Run the complete deployment test:
```bash
./test-fargate-deploy.sh
```

This performs a full deploy → invoke → teardown cycle with test payload.

## Customization

Modify the stack in `fargate-app.ts`:

```typescript
new NovaActFargate(this, 'NovaActService', {
  containerImage: ecs.ContainerImage.fromAsset('.', {
    platform: cdk.aws_ecr_assets.Platform.LINUX_AMD64
  }),
  cpu: 4096,                    // Increase CPU
  memoryLimitMiB: 8192,        // Increase memory
  environment: {               // Add custom environment variables
    'CUSTOM_VAR': 'value'
  },
  apiKey: props.apiKey,
});
```

## Security Features

- **VPC Flow Logs** enabled for security compliance
- **VPC Endpoints** for secure AWS service access
- **Container Insights** enabled for monitoring
- **Least privilege** security group rules
- **Private subnet deployment** with controlled internet access

## Cleanup

```bash
npx cdk destroy --app "npx ts-node fargate-app.ts"
```

## Troubleshooting

**Task fails to start:**
- Check CloudWatch logs: `/aws/ecs/NovaActFargateStack`
- Verify network configuration and security groups
- Ensure sufficient Fargate capacity in region

**Task execution fails:**
- Verify task definition configuration
- Check VPC endpoints are accessible
- Review IAM permissions for task and execution roles