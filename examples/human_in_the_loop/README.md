# Amazon Nova Act Human in the Loop (HITL) Examples

Examples demonstrating human approval workflows and interactive automation patterns with Nova Act. These examples show how to pause automation for human intervention when needed.

## Repository Structure

```
├── basic/                  # Simple HITL examples
```

## Prerequisites

Complete the [Getting Started](../README.md#getting-started) section in the main examples directory before running these examples.

## Implementation Details

Nova Act supports two HITL patterns:

1. Human approval — request human approval before completing automated actions, useful for confirming purchases, transactions, or validating data before submission.
2. UI takeover — pause automation to let humans handle complex interactions in the browser, useful for CAPTCHA resolution or authentication flows.

HITL workflows require implementing the `HumanInputCallbacksBase` class with two methods:

- `approve(message: str) -> ApprovalResponse` — handle approval requests
- `ui_takeover(message: str) -> UiTakeoverResponse` — handle UI takeover requests

The Nova Act SDK automatically calls these methods when human intervention is needed during workflow execution.

## Usage

### Basic Examples

The `basic/` directory contains simple implementations of both HITL patterns.

[Get Started with Basic Examples →](basic/README.md)

## Next Steps

- Learn more about HITL in the [SDK README →](https://github.com/aws/nova-act)
- Extend this example with the [Nova Act Human Intervention Service →](https://github.com/amazon-agi-labs/nova-act-human-intervention)
- For production deployments, see [CDK →](../../cdk/README.md)
- For complete applications, see [Solutions →](../../solutions/README.md)
- Visit the [Nova Act documentation →](https://docs.aws.amazon.com/nova-act)