# Amazon Nova Act Browser Dialog Examples

Demonstrates handling browser native dialogs ([prompt](https://developer.mozilla.org/en-US/docs/Web/API/Window/prompt), [confirm](https://developer.mozilla.org/en-US/docs/Web/API/Window/confirm), [alert](https://developer.mozilla.org/en-US/docs/Web/API/Window/alert)) with Nova Act using Playwright's dialog event handlers. By default, Playwright automatically dismisses dialogs, but you can register handlers to programmatically respond to them.

## Repository Structure

```
├── main.py              # Entry point — dialog handling workflow
└── ui/
    └── dialogs.html     # Local test page with dialog-triggering buttons
```

## Prerequisites

Complete the [Getting Started](../README.md#getting-started) section in the main examples directory before running these examples.

## Usage

```bash
python -m examples.browser_dialogs.main
```

**Implementation Details:**
- Loads a local game setup page (`ui/dialogs.html`) with prompt, confirm, and alert dialogs
- Registers a Playwright dialog handler on `nova.page` that inspects [`dialog.type`](https://playwright.dev/python/docs/api/class-dialog#dialog-type) to respond programmatically by dialog type
- By default, Playwright automatically dismisses browser dialogs — the handler overrides this behavior
- Register the handler before Nova Act triggers any dialog-producing actions, and remove it when no longer needed to avoid interfering with subsequent interactions

## Next Steps

- Learn more about dialog handling in the [Playwright documentation →](https://playwright.dev/python/docs/dialogs#alert-confirm-prompt-dialogs)
- For production deployments, see [CDK →](../../cdk/README.md)
- For complete applications, see [Solutions →](../../solutions/README.md)
- Visit the [Nova Act documentation →](https://docs.aws.amazon.com/nova-act)