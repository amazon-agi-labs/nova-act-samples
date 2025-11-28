# Amazon Nova Act Basic Tool Use Examples

Simple examples demonstrating how to create and use custom tools with Nova Act.

## Repository Structure

```
├── ui/                     # Local HTML files for testing
└── get_current_date.py     # Custom date tool example
```

## Prerequisites

Complete the [Getting Started](../../README.md#getting-started) section in the main examples directory before running these examples.

## Usage Instructions

### get_current_date.py - Custom Date Tool

Demonstrates using a custom tool to get current date and enter it in a form.

```bash
python -m examples.tool_use.basic.get_current_date
```

**Features:**
- Loads local HTML form (`ui/date_form.html`)
- Custom `get_current_date()` tool function
- Automated date entry and form submission
- Returns submitted date

## Next Steps

- Learn more about tools in the [README →](../README.md)
- For production deployments, see [CDK →](../../../cdk/README.md)
- For complete applications, see [Solutions →](../../../solutions/README.md)
- Visit the [Nova Act documentation →](https://docs.aws.amazon.com/nova-act)
