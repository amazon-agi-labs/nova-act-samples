# Amazon Nova Act Browser Dialog Examples

Demonstrates handling browser native dialogs ([prompt](https://developer.mozilla.org/en-US/docs/Web/API/Window/prompt), [confirm](https://developer.mozilla.org/en-US/docs/Web/API/Window/confirm), [alert](https://developer.mozilla.org/en-US/docs/Web/API/Window/alert)) with Nova Act using Playwright's dialog event handlers. By default, Playwright automatically dismisses dialogs, but you can register handlers to programmatically respond to them.

## Prerequisites

Complete the [Getting Started](../README.md#getting-started) section in the main examples directory before running these examples.

## Usage Instructions

### Dialog Handling

[`main.py`](main.py)

A Nova Act implementation that demonstrates a mock game setup scenario with three buttons that trigger different dialog types:
1. Enter Name button → `prompt()` - collects player name input
2. Set Difficulty button → `confirm()` - selects difficulty level (OK=Hard, Cancel=Easy)  
3. Start New Game button → `alert()` - displays game start confirmation (disabled until steps 1 & 2 complete).

A dialog handler uses [`dialog.type`](https://playwright.dev/python/docs/api/class-dialog#dialog-type) to determine the appropriate response for each dialog type.

**Features:**

- Single handler for all dialog types (prompt, confirm, alert)
- Automatic dialog response based on dialog type
- Clean event listener management
- Realistic user interaction flow

**Usage:**

```bash
python -m examples.browser_dialogs.main
```

The example loads a local HTML file ([`ui/dialogs.html`](ui/dialogs.html)) that contains the game setup interface and dialog triggers.

## Next Steps

- Learn more about dialog handling in the [Playwright documentation →](https://playwright.dev/python/docs/dialogs#alert-confirm-prompt-dialogs)
- For production deployments, see [CDK →](../../cdk/README.md)
- For complete applications, see [Solutions →](../../solutions/README.md)
- Visit the [Nova Act documentation →](https://docs.aws.amazon.com/nova-act)