# Nova Act Lambda Example

Deploy Nova Act on AWS Lambda using container images with IAM role authentication.

## Prerequisites

1. See the [main CDK README](../README.md) for complete prerequisites and setup instructions.

## Quick Start

```bash
export CDK_DEFAULT_ACCOUNT="123456789012"
export CDK_DEFAULT_REGION="us-east-1"
export NOVA_ACT_API_KEY="your-api-key"
npx cdk deploy --app "npx ts-node lambda-app.ts"
```

## Files

- `lambda-stack.ts` - NovaActLambda construct and NovaActLambdaStack
- `lambda-app.ts` - CDK application entry point with environment validation
- `app.py` - Nova Act Lambda handler with error handling and structured responses
- `Dockerfile` - Container configuration based on Playwright Python image
- `requirements.txt` - Python dependencies (nova-act, awslambdaric)
- `test-lambda-deploy.sh` - Complete deployment test (deploy → invoke → teardown)

## Architecture

This example creates:

- **Lambda Function** with container image from ECR
- **IAM Execution Role** with CloudWatch Logs permissions
- **Container Image** built from local Dockerfile and pushed to ECR

## Handler Implementation

The `app.py` file contains:

- Nova Act workflow with Lambda handler function
- Error handling with try-catch blocks and structured responses
- Nova Act API key loaded from environment variables
- Default prompt and starting page configuration

### Payload Structure

**Parameters:**

- `prompt` (optional): Single prompt to execute. Defaults to flight search example.
- `starting_page` (optional): Starting URL for Nova Act. Defaults to Nova Act gym.

**Example payload:**

```json
{
  "prompt": "Find flights from Boston to Wolf on Feb 22nd",
  "starting_page": "https://nova.amazon.com/act/gym/next-dot/search"
}
```

## Testing

Run the complete deployment test:

```bash
./test-lambda-deploy.sh
```

This performs a full deploy → invoke → teardown cycle with test payload.

## Cleanup

```bash
cdk destroy --app "npx ts-node lambda-app.ts"
```

## Customization

Modify the NovaActLambda construct:

```typescript
new NovaActLambda(this, "NovaActLambda", {
  dockerfilePath: ".",
  memorySize: 4096, // Increase memory
  timeout: Duration.minutes(10), // Adjust timeout
  environment: {
    // Add custom variables
    CUSTOM_VAR: "value",
  },
});
```

## Limitations

- **15-minute maximum execution time** (AWS Lambda limit)
- **Container image size limits** apply
- **Cold start latency** for infrequent invocations
- **Memory constraints** may affect browser performance
