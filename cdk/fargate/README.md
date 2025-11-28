# Nova Act Fargate Example

This example demonstrates how to deploy Nova Act on AWS Fargate using standalone CDK constructs.

## Prerequisites

- AWS CLI configured with appropriate permissions
- CDK CLI installed (`npm install -g aws-cdk`)
- Docker installed and running

## Files

- `fargate-stack.ts` - Complete Fargate stack with NovaActVpc and NovaActFargate constructs
- `fargate-app.ts` - CDK application entry point
- `Dockerfile` - Container configuration with Playwright and Python 3.12
- `app.py` - Sample Nova Act Python application
- `requirements.txt` - Python dependencies (nova-act)
- `test-fargate-deploy.sh` - Full deployment test script (deploy → test → teardown)

## Architecture

This example creates:
- **NovaActVpc**: VPC with private/public subnets, VPC endpoints (SSM, EC2Messages, SSMMessages), and VPC Flow Logs
- **ECS Cluster** with container insights enabled
- **Fargate Service** with Nova Act container in private subnets
- **Security Groups** with controlled egress (HTTP/HTTPS/DNS only)
- **CloudWatch Logs** with non-blocking mode

## Configuration

The Fargate service is configured with:
- **2048 CPU units and 4096 MB memory** (default)
- **Private subnet deployment** with NAT gateway for internet access
- **IAM role-based authentication** (no API key required)
- **Browser arguments**: `--disable-gpu --disable-dev-shm-usage --no-sandbox --single-process`
- **Headless mode** enabled
- **Platform**: Linux AMD64

## Deployment

```bash
cdk deploy --app "npx ts-node fargate-app.ts"
```

## Testing

Full deployment test (includes actual AWS deployment):
```bash
./test-fargate-deploy.sh
```

This script:
1. Deploys the stack
2. Waits for service to stabilize
3. Checks task status and logs
4. Destroys the stack

## Cleanup

```bash
cdk destroy --app "npx ts-node fargate-app.ts"
```

## Security Features

- **VPC Flow Logs** for security compliance (AwsSolutions-VPC7)
- **Container Insights** enabled (AwsSolutions-ECS4)
- **Encrypted traffic** through VPC endpoints
- **Least privilege** security group rules
- **CDK-Nag suppressions** with justifications for environment variables

## Customization

Modify the NovaActFargate construct in `fargate-app.ts`:

```typescript
new NovaActFargate(this, 'NovaActService', {
  containerImage: ecs.ContainerImage.fromAsset('.', {
    platform: cdk.aws_ecr_assets.Platform.LINUX_AMD64
  }),
  cpu: 4096,                    // Increase CPU
  memoryLimitMiB: 8192,        // Increase memory
  desiredCount: 2,             // Scale to 2 instances
  environment: {               // Add custom environment variables
    'CUSTOM_VAR': 'value'
  }
});
```
