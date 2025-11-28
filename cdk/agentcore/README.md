# Nova Act AgentCore Runtime Example

This is a **standalone, customer-ready** example that demonstrates how to deploy Nova Act on AWS AgentCore Runtime.

## Prerequisites

- AWS CLI configured with appropriate permissions
- CDK CLI installed (`npm install -g aws-cdk`)
- Docker for container builds (CDK manages this automatically)

## Required Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `CDK_DEFAULT_ACCOUNT` | AWS Account ID | `123456789012` |
| `CDK_DEFAULT_REGION` | AWS Region | `us-east-1` |

## Files

- `agentcore-stack.ts` - AgentCore stack with embedded runtime construct
- `agentcore-app.ts` - CDK application entry point with environment validation
- `handler.py` - Nova Act AgentCore handler with @app.entrypoint decorator
- `Dockerfile` - Container configuration with OpenTelemetry integration
- `requirements.txt` - Python dependencies (boto3, nova-act, bedrock_agentcore)
- `test-agentcore.sh` - Complete deployment test (deploy → invoke → teardown)
- `build-and-push.sh` - Manual container build script
- `package.json` - Node.js dependencies for CDK
- `tsconfig.json` - TypeScript configuration

## Quick Start

```bash
export CDK_DEFAULT_ACCOUNT="123456789012"
export CDK_DEFAULT_REGION="us-east-1"
npm install
cdk deploy
```

CDK automatically builds and pushes the container image to ECR during deployment.

## Architecture

This example creates:
- **AgentCore Runtime** (`CfnRuntime`) with Nova Act container
- **IAM Role** with comprehensive permissions:
  - Bedrock full access
  - API Gateway invoke access
  - ECR, CloudWatch, X-Ray access
  - Bedrock AgentCore browser session permissions
  - S3 access for Nova Act buckets
- **Container Image** built from local Dockerfile (ARM64 platform)
- **Environment Variables** for Nova Act configuration
- **Public Network Mode** for internet access

## Authentication

**IAM Role Authentication** (Production Ready):
- AgentCore role provides Nova Act service access automatically
- No API keys required
- Comprehensive AWS service permissions included
- Uses bedrock_agentcore.tools.browser_client for browser sessions

## Handler Implementation

The `handler.py` uses the required AgentCore pattern:
- `@app.entrypoint` decorator for AgentCore runtime
- Browser session integration with `browser_session(region)`
- CDP endpoint URL and headers for Nova Act
- Comprehensive error handling and logging

## Testing

Complete deployment test:
```bash
./test-agentcore.sh
```

This script:
1. Validates environment variables
2. Deploys the stack
3. Waits for runtime to be ready
4. Invokes the runtime with test payload
5. Destroys the stack

## Container Management

CDK handles all container operations:
- Builds Docker image during `cdk deploy`
- Creates ECR repository if needed
- Pushes image with content-based tags
- Updates AgentCore runtime with new image URI

## Environment Variables

The runtime is configured with:
- `NOVA_ACT_BROWSER_ARGS`: `--disable-gpu --disable-dev-shm-usage --no-sandbox --single-process`
- `NOVA_ACT_HEADLESS`: `true`
- `OTEL_SDK_DISABLED`: `true`

## Cleanup

```bash
cdk destroy
```

## Customization

To customize the deployment:

1. **Change agent name**: Modify `agentName` in `agentcore-app.ts`
2. **Update container platform**: Change `Platform.LINUX_ARM64` in `agentcore-stack.ts`
3. **Add environment variables**: Extend `createEnvironmentVariables()` method
4. **Modify IAM permissions**: Update policy methods in the stack
