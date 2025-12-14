# Nova Act AgentCore Runtime Example

Deploy Nova Act on Amazon Bedrock AgentCore Runtime with Amazon Bedrock AgentCore Browser integration.

## Prerequisites

1. See the [main CDK README](../README.md) for complete prerequisites and setup instructions.

## Quick Start

```bash
export CDK_DEFAULT_ACCOUNT="123456789012"
export CDK_DEFAULT_REGION="us-east-1"
export NOVA_ACT_API_KEY="your-api-key"
npx cdk deploy --app "npx ts-node agentcore-app.ts"
```

## Files

- `agentcore-stack.ts` - AgentCore stack with embedded runtime construct
- `agentcore-app.ts` - CDK application entry point with environment validation
- `handler.py` - Nova Act workflow with AgentCore handler with @app.entrypoint decorator
- `Dockerfile` - Container configuration for AgentCore Runtime
- `requirements.txt` - Python dependencies (boto3, nova-act, bedrock_agentcore)
- `test-agentcore.sh` - Complete deployment test (deploy → invoke → teardown)

## Architecture

This example creates:

- **AgentCore Runtime Agent** to run Nova Act workflow integrated with AgentCore Browser Tool
- **IAM Role** with Bedrock, ECR, CloudWatch, and browser session permissions
- **Container Image** built from local Dockerfile and pushed to ECR

## Handler Implementation

The `handler.py` file contains:

- Nova Act workflow
- AgentCore Runtime implementation with `@app.entrypoint` decorator
- AgentCore Browser session integration with `browser_session(region)`
- AgentCore Browser CDP endpoint URL and headers for Nova Act
- Nova Act API key loaded from environment variables

### Payload Structure

**Parameters:**

- `prompt`: Single prompt to execute.
- `starting_page`: Starting URL for Nova Act.

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
./test-agentcore.sh
```

This performs a full deploy → invoke → teardown cycle with test payload.

## Cleanup

```bash
cdk destroy --app "npx ts-node agentcore-app.ts"
```

## Customization

- **Change agent name**: Modify `agentName` in `agentcore-app.ts`
- **Update container platform**: Change `Platform.LINUX_ARM64` in `agentcore-stack.ts`
- **Add environment variables**: Extend `createEnvironmentVariables()` method
- **Modify IAM permissions**: Update policy methods in the stack
