# Amazon Nova Act with Amazon Bedrock AgentCore Examples

Examples demonstrating how to use Nova Act with Amazon Bedrock AgentCore to build scalable UI automation workflows using managed infrastructure. These examples show how Nova Act's automation capabilities can be enhanced with AgentCore's managed services to create reliable, cost-effective automation solutions.

## Repository Structure

```
├── browser/
│   └── main.py             # AgentCore Browser session example
├── browser_actuator/
│   ├── main.py             # Custom actuator with AgentCore Browser Tool
│   └── acbt_actuator.py    # AgentCoreBrowserActuator implementation
```

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

## Usage

### AgentCore Browser

The `browser/` directory contains examples for managed browser sessions with Nova Act.

[Get Started with AgentCore Browser →](browser/README.md)

### AgentCore Browser Actuator

Custom actuator that manages an AgentCore Browser Tool session, connecting Nova Act to a remote browser via CDP.

[Get Started with AgentCore Browser Actuator →](browser_actuator/README.md)

## Next Steps

- Learn more about AgentCore in the [AWS documentation](https://docs.aws.amazon.com/bedrock-agentcore/)
- For production deployments, see [CDK →](../../cdk/README.md)
- For complete applications, see [Solutions →](../../solutions/README.md)
- Visit the [Nova Act documentation →](https://docs.aws.amazon.com/nova-act)