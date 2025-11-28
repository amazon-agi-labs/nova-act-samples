# Amazon Nova Act Tool Use Examples

Examples demonstrating Nova Act's tool use capability. These examples show how to integrate Nova Act with custom tools.

## Repository Structure

```
├── basic/                  # Simple tool use examples
└── excel/                  # Excel integration examples
```

## Prerequisites

Complete the [Getting Started](../README.md#getting-started) section in the main examples directory before running these examples.

## Implementation Details

Tool use workflows use the `@tool` decorator to create custom functions that Nova Act can call during execution. These decorated functions are passed to Nova Act, which will call the tools when necessary to complete the requested task.

Learn more about tools in [the docs](https://github.com/aws/nova-act).

## Usage Instructions

### Basic Examples

The `basic/` directory contains simple implementations of custom tool creation and usage patterns.

[Get Started with Basic Examples →](basic/README.md)

### Excel Examples

The `excel/` directory showcases Nova Act's ability to call tools that interact with Excel files.

[Get Started with Excel Examples →](excel/README.md)

## Next Steps

- Learn more about tools in the [SDK README →](https://github.com/aws/nova-act)
- For production deployments, see [CDK →](../../cdk/README.md)
- For complete applications, see [Solutions →](../../solutions/README.md)
- Visit the [Nova Act documentation →](https://docs.aws.amazon.com/nova-act)
