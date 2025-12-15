# Amazon Nova Act ECS Example

Deploy Amazon Nova Act on AWS ECS with EC2 backing instances using container images with API key authentication.

## Prerequisites

1. See the [main CDK README](../README.md) for complete prerequisites and setup instructions.

## Quick Start

```bash
export CDK_DEFAULT_ACCOUNT="123456789012"
export CDK_DEFAULT_REGION="us-east-1"
export NOVA_ACT_API_KEY="your-api-key"
npx cdk deploy --app "npx ts-node ecs-app.ts"
```

## Files

- `ecs-stack.ts` - Complete ECS stack with NovaActEcsStack class
- `ecs-app.ts` - CDK application entry point with environment validation
- `app.py` - Nova Act ECS application with error handling and structured logging
- `Dockerfile` - Container configuration with Playwright and Python 3.12
- `requirements.txt` - Python dependencies (nova-act)
- `test-ecs-deploy.sh` - Complete deployment test (deploy → invoke → teardown)

## Architecture

This example creates:
- **VPC** with private/public subnets across 2 AZs and VPC Flow Logs
- **VPC Endpoints** for S3, ECR, ECR Docker, and CloudWatch Logs
- **Security Group** allowing HTTPS and outbound traffic
- **ECS Cluster** with EC2 capacity provider and container insights
- **Auto Scaling Group** with encrypted EBS volumes
- **Task Definition** with Nova Act container
- **CloudWatch Logs** for monitoring

## Configuration

Default configuration:
- **Instance Type**: m5.large (configurable)
- **Desired Capacity**: 1 instance (configurable)
- **Container Memory**: 2048 MB
- **Platform**: Linux AMD64
- **Browser Arguments**: `--disable-gpu --disable-dev-shm-usage --no-sandbox`

## Handler Implementation

The `app.py` file contains:
- Nova Act workflow with ECS task implementation
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

Tasks are executed on-demand rather than running continuously:

```bash
# Get cluster and task definition names
CLUSTER_NAME=$(aws ecs list-clusters --query 'clusterArns[?contains(@, `NovaActEcsStack`)] | [0]' --output text | cut -d'/' -f2)
TASK_DEF_ARN=$(aws ecs list-task-definitions --query 'taskDefinitionArns[?contains(@, `NovaActEcsStack`)] | [0]' --output text)

# Run task with default configuration
aws ecs run-task \
  --cluster $CLUSTER_NAME \
  --task-definition $TASK_DEF_ARN \
  --launch-type EC2

# Run task with custom prompt and starting page
aws ecs run-task \
  --cluster $CLUSTER_NAME \
  --task-definition $TASK_DEF_ARN \
  --launch-type EC2 \
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
./test-ecs-deploy.sh
```

This performs a full deploy → invoke → teardown cycle with test payload.

## Customization
Modify the stack in `ecs-app.ts`:

```typescript
new NovaActEcsStack(app, 'NovaActEcsStack', {
  instanceType: ec2.InstanceType.of(ec2.InstanceClass.M5, ec2.InstanceSize.XLARGE),
  desiredCapacity: 2,
  containerImage: ecs.ContainerImage.fromAsset('.'),
});
```

## Security Features

- **VPC Flow Logs** enabled for security compliance
- **Encrypted EBS volumes** for container instances
- **VPC Endpoints** for secure AWS service access
- **Container Insights** enabled for monitoring
- **Least privilege** security group rules

## Cleanup

```bash
npx cdk destroy --app "npx ts-node ecs-app.ts"
```

## Troubleshooting

**Container fails to start:**
- Check CloudWatch logs: `/aws/ecs/NovaActEcsStack`
- Verify container instances are registered with cluster
- Ensure sufficient memory allocation

**Task execution fails:**
- Verify ECS cluster has available capacity
- Check task definition configuration
- Review IAM permissions for task role