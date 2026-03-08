# Amazon Nova Act Clipboard Manager Examples

Demonstrates how to interact with the browser clipboard using Nova Act. Shows how to grant clipboard permissions via Playwright's browser context and read clipboard content using the JavaScript Clipboard API.

## Repository Structure

```
├── main.py          # Entry point — clipboard read via Playwright page
```

## Prerequisites

Complete the [Getting Started](../README.md#getting-started) section in the main examples directory before running this example.

## Usage

```bash
python -m examples.clipboard_manager.main
```

**Implementation Details:**
- Grants `clipboard-read` and `clipboard-write` permissions to the browser context
- Triggers a copy action on the page, then reads the clipboard content using `navigator.clipboard.readText()` via Playwright's `page.evaluate()`

## Next Steps

- For tool use patterns, see [Tool Use →](../tool_use/README.md)
- For deploying workflows on AWS, see [CDK →](../../cdk/README.md)
- Visit the [Nova Act documentation →](https://docs.aws.amazon.com/nova-act)
