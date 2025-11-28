# Nova Act ECS Example

This example deploys Nova Act on AWS ECS with EC2 backing instances. The deployment is self-contained with IAM role authentication.

## Prerequisites

- AWS CLI configured with appropriate permissions
- CDK CLI installed: `npm install -g aws-cdk`
- Docker installed and running
- Node.js 18+ installed

## Files

- `ecs-stack.ts` - Complete ECS stack with NovaActEcsStack class
- `ecs-app.ts` - CDK application entry point (IAM role authentication only)
- `Dockerfile` - Container configuration with Playwright and Python 3.12
- `app.py` - Sample Nova Act application with API key from environment
- `requirements.txt` - Python dependencies (nova-act)
- `test-ecs-deploy.sh` - Full deployment test (deploy → invoke task → teardown)

## Quick Start

```bash
npm install aws-cdk-lib constructs
npx cdk deploy --app "npx ts-node ecs-app.ts"
```

## Architecture

The deployment creates:
- **VPC** with private/public subnets across 2 AZs and VPC Flow Logs
- **VPC Endpoints** for S3, ECR, ECR Docker, and CloudWatch Logs
- **Security Group** allowing HTTPS and outbound traffic
- **ECS Cluster** with EC2 capacity provider and container insights
- **Auto Scaling Group** with encrypted EBS volumes (30GB)
- **Task Definition** with Nova Act container (2048 MB memory)
- **CloudWatch Logs** for monitoring

## Configuration

Default configuration:
- **Instance Type**: m5.large (configurable)
- **Desired Capacity**: 1 instance (configurable)
- **Container Memory**: 2048 MB
- **Platform**: Linux AMD64
- **Browser Arguments**: `--disable-gpu --disable-dev-shm-usage --no-sandbox`

## Authentication

**IAM Role-Based Only**: The ECS task role provides authentication automatically. No API key configuration needed in the CDK code.

The `app.py` expects `NOVA_ACT_API_KEY` environment variable, but this should be set via task definition environment variables or removed for pure IAM authentication.

## Task Execution

Tasks are executed on-demand rather than running continuously:

```bash
# Get cluster and task definition names
CLUSTER_NAME=$(aws ecs list-clusters --query 'clusterArns[?contains(@, `NovaActEcsStack`)] | [0]' --output text | cut -d'/' -f2)
TASK_DEF_ARN=$(aws ecs list-task-definitions --query 'taskDefinitionArns[?contains(@, `NovaActEcsStack`)] | [0]' --output text)

# Run task
aws ecs run-task \
  --cluster $CLUSTER_NAME \
  --task-definition $TASK_DEF_ARN \
  --launch-type EC2

# Check logs
aws logs get-log-events \
  --log-group-name /aws/ecs/NovaActEcsStack \
  --log-stream-name ecs/AppContainer/TASK-ID
```

## Testing

Full deployment test:
```bash
./test-ecs-deploy.sh
```

This script:
1. Deploys the stack
2. Waits for container instances to register
3. Runs a test task
4. Monitors task completion and logs
5. Destroys the stack

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
