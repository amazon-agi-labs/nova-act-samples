# Amazon Nova Act QA Examples

Examples demonstrating QA testing patterns with Nova Act, including a reusable assertion and extraction class and mobile QA via AWS Device Farm.

## Repository Structure

```
├── nova_act_qa/            # NovaActQa module — QA extension of NovaAct
├── basic/                  # Simple QA test using NovaActQa
├── mobile_qa/              # Mobile QA test using Device Farm
├── test_translator/        # Gherkin-to-Nova Act test translator
```

## Prerequisites

Complete the [Getting Started](../README.md#getting-started) section in the main examples directory before running these examples.

## Implementation Details

All examples in this directory use `NovaActQa`, a drop-in replacement for `NovaAct` with typed assertions and value extraction for QA workflows. See the [NovaActQa Reference →](nova_act_qa/README.md) to learn more.

## Usage Instructions

### Basic Example

Simple QA test demonstrating `NovaActQa`'s assertion and extraction methods.

[Get Started with Basic Example →](basic/README.md)

### Mobile QA

QA testing on mobile apps using `NovaActQa` with AWS Device Farm and a [custom mobile actuator](../actuation/mobile/nova_act_mobile/actuation/README.md).

[Get Started with Mobile QA →](mobile_qa/README.md)

### Test Translator

Translates Gherkin feature files into executable Nova Act tests using a Strands agent, enabling QA teams to use AI-powered browser automation without writing automation code.

[Get Started with Test Translator →](test_translator/README.md)

## Next Steps

- For deploying workflows on AWS, see [CDK →](../../cdk/README.md)
- For complete applications, see [Solutions →](../../solutions/README.md)
- Visit the [Nova Act documentation →](https://docs.aws.amazon.com/nova-act)
