# Amazon Bedrock AgentCore Examples

Examples demonstrating how to use Nova Act with Amazon Bedrock AgentCore to build scalable UI automation workflows using managed infrastructure. These examples show how Nova Act's automation capabilities can be enhanced with AgentCore's managed services to create reliable, cost-effective automation solutions.

## Prerequisites

1. Complete the [Getting Started](../README.md#getting-started) section in the main examples directory before running these examples.
2. Configure environment with AWS credentials for full access to AgentCore and Nova Act
    - Note: full access is for example purposes only, permissions should be scoped down for further use
3. Install dependencies:
   ```bash
   pip install -r examples/agentcore/requirements.txt
   ```

## Implementation Details

These AgentCore workflows leverage Amazon Bedrock AgentCore's managed services to provide scalable infrastructure for Amazon Nova Act. AgentCore handles the complexity of managing compute resources, scaling, and security isolation, allowing you to focus on building automation workflows without infrastructure overhead.

Learn more about AgentCore in the [AWS documentation](https://docs.aws.amazon.com/bedrock-agentcore/).

## Usage Instructions

### AgentCore Browser

[`agentcore_browser.py`](agentcore_browser.py)

A Nova Act implementation that uses Amazon Bedrock AgentCore Browser Tool for UI automation tasks. Uses the `BrowserClient` from [the `bedrock-agentcore` package](https://pypi.org/project/bedrock-agentcore/) to create managed browser sessions that Nova Act connects to via CDP (Chrome DevTools Protocol).

**Features:**

- Managed browser sessions with automatic scaling
- Isolated execution environments for security
- Cost optimization through pay-per-use model
- Automatic resource cleanup
- CDP integration for seamless Nova Act connection

**Usage:**

```bash
python -m examples.agentcore.agentcore_browser
```

## Next Steps

- Learn more about AgentCore in the [AWS documentation](https://docs.aws.amazon.com/bedrock-agentcore/)
- For production deployments, see [CDK →](../../cdk/README.md)
- For complete applications, see [Solutions →](../../solutions/README.md)
- Visit the [Nova Act documentation →](https://docs.aws.amazon.com/nova-act)