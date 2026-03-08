# Amazon Nova Act Custom Actuator with AgentCore Browser Tool Examples

Demonstrates how to use a custom actuator that manages an Amazon Bedrock AgentCore Browser Tool (ACBT) session, so individual workflows don't need to handle session provisioning and teardown themselves. The actuator hooks into `start()` and `stop()` to manage the ACBT lifecycle.

## Repository Structure

```
├── main.py              # Entry point — runs a workflow using the custom actuator
└── acbt_actuator.py     # AgentCoreBrowserActuator implementation
```

## Prerequisites

1. Complete the [Getting Started](../../README.md#getting-started) section in the main examples directory
2. Configure environment with AWS credentials for full access to AgentCore and Nova Act
   - Note: full access is for example purposes only, permissions should be scoped down for further use
3. Install dependencies:
   ```bash
   pip install -r examples/agentcore/browser_actuator/requirements.txt
   ```

## Usage

```bash
python -m examples.agentcore.browser_actuator.main
```

**Implementation Details:**
- `AgentCoreBrowserActuator` extends `DefaultNovaLocalBrowserActuator`, the same Playwright-based actuator that NovaAct uses internally
- When passed as a class (not an instance), NovaAct constructs it with `PlaywrightInstanceOptions` containing all user settings (screen size, headless mode, user agent, etc.)
- `start()` provisions an ACBT session, patches the CDP endpoint/headers into the options, then calls `super().__init__()` and `super().start()` to initialize the Playwright actuator over CDP
- `stop()` tears down the Playwright actuator, then the ACBT session (both best-effort)
- The `console_live_view_url` property provides an AWS Console URL to watch the session live

## Next Steps

- For the standard AgentCore Browser integration (without a custom actuator), see [AgentCore Browser →](../browser/README.md)
- For deploying workflows on AWS, see [CDK →](../../../cdk/README.md)
- Visit the [Nova Act documentation →](https://docs.aws.amazon.com/nova-act)
