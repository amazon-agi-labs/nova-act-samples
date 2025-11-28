# Nova Act Lambda Example

This example demonstrates how to deploy Nova Act on AWS Lambda using IAM role authentication with container images.

## Prerequisites

- AWS CLI configured with appropriate permissions
- CDK CLI installed (`npm install -g aws-cdk`)
- Docker installed and running

## Files

- `lambda-stack.ts` - NovaActLambda construct and NovaActLambdaStack
- `lambda-app.ts` - CDK application entry point with environment validation
- `Dockerfile` - Container configuration based on Playwright Python image
- `app.py` - Sample Nova Act Lambda handler
- `requirements.txt` - Python dependencies (nova-act, awslambdaric)
- `test-lambda-deploy.sh` - Full deployment test (deploy → invoke → teardown)

## Architecture

This example creates:
- **Lambda Function** with container image from ECR
- **Docker Image Asset** built from local Dockerfile (Linux AMD64)
- **IAM Execution Role** with CloudWatch Logs permissions
- **Environment Variables** for Nova Act configuration

## Configuration

The Lambda function is configured with:
- **Memory**: 3008 MB (recommended for browser automation)
- **Timeout**: 15 minutes
- **Runtime**: FROM_IMAGE (container-based)
- **Platform**: Linux AMD64
- **Browser Path**: `/ms-playwright` (system Playwright browsers)

## Environment Variables

- `NOVA_ACT_BROWSER_ARGS`: `--disable-gpu --disable-dev-shm-usage --no-sandbox --single-process`
- `NOVA_ACT_HEADLESS`: `true`
- `NOVA_ACT_SKIP_PLAYWRIGHT_INSTALL`: `1`
- `PLAYWRIGHT_BROWSERS_PATH`: `/ms-playwright`

## Deployment

```bash
export CDK_DEFAULT_ACCOUNT="123456789012"
export CDK_DEFAULT_REGION="us-east-1"
cdk deploy --app "npx ts-node lambda-app.ts"
```

## Handler Implementation

The `app.py` handler expects:
- `event.prompts`: Array of prompts to execute
- `event.starting_page`: Starting URL for Nova Act

Example invocation payload:
```json
{
  "prompts": ["Go to google.com"],
  "starting_page": "https://google.com"
}
```

## Testing

Full deployment test:
```bash
./test-lambda-deploy.sh
```

This script:
1. Sets environment variables
2. Deploys the Lambda stack
3. Invokes the function with test payload
4. Destroys the stack

## Authentication

**IAM Role Authentication Only**: The Lambda execution role provides authentication. No API key management required.

## Container Details

The Dockerfile:
- Uses `mcr.microsoft.com/playwright/python:v1.55.0-noble` base image
- Installs Nova Act and AWS Lambda Runtime Interface Client
- Pre-configures Playwright browsers at `/ms-playwright`
- Sets up Lambda-specific environment variables

## Cleanup

```bash
cdk destroy --app "npx ts-node lambda-app.ts"
```

## Customization

Modify the NovaActLambda construct:

```typescript
new NovaActLambda(this, 'NovaActWithIAM', {
  dockerfilePath: '.',
  memorySize: 4096,              // Increase memory
  timeout: Duration.minutes(10), // Adjust timeout
  environment: {                 // Add custom variables
    'CUSTOM_VAR': 'value'
  }
});
```

## Limitations

- **15-minute maximum execution time** (AWS Lambda limit)
- **Container image size limits** apply
- **Cold start latency** for infrequent invocations
- **Memory constraints** may affect browser performance
