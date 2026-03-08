# Amazon Nova Act Basic Tool Use Examples

Simple examples demonstrating how to create and use custom tools with Nova Act.

## Repository Structure

```
├── get_current_date.py     # Custom date tool example
├── api_call.py             # API call between browser automation steps
└── ui/
    ├── date_form.html      # Date entry form for get_current_date
    └── device_control.html # Device control panel for api_call
```

## Prerequisites

Complete the [Getting Started](../../README.md#getting-started) section in the main examples directory before running these examples.

## Usage

### get_current_date.py - Custom Date Tool

Demonstrates using a custom tool to get the current date and enter it in a form.

```bash
python -m examples.tool_use.basic.get_current_date
```

**Implementation Details:**
- Defines a `get_current_date()` tool that returns the current date
- Loads a local HTML form ([`ui/date_form.html`](ui/date_form.html)) and submits the date
- Returns the submitted date via `act_get()`

### api_call.py - API Call Tool

Demonstrates using a custom tool to make an API call between browser automation steps. The workflow performs a browser action, calls an external API via a tool to retrieve state, then validates the response in Python.

```bash
python -m examples.tool_use.basic.api_call
```

**Implementation Details:**
- Defines a `validate_device_state()` tool that simulates an API request returning JSON
- Loads a local device control page ([`ui/device_control.html`](ui/device_control.html)) and performs a browser action
- Calls the tool to check state, then parses and asserts the result in the workflow

## Next Steps

- Learn more about tools in the [README →](../README.md)
- For production deployments, see [CDK →](../../../cdk/README.md)
- For complete applications, see [Solutions →](../../../solutions/README.md)
- Visit the [Nova Act documentation →](https://docs.aws.amazon.com/nova-act)
