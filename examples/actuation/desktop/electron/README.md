# Amazon Nova Act Electron Actuation Examples

Demonstrates connecting Nova Act to an Electron app via the Chrome DevTools Protocol. Includes a task manager Electron app as the automation target, but works with any Electron app exposing a CDP endpoint.

## Repository Structure

```
├── main.py              # Nova Act workflow that connects to an Electron app over CDP
└── app/                 # Minimal Electron task manager app (see app/README.md)
```

## Prerequisites

1. Complete the [Getting Started](../../../README.md#getting-started) section in the main examples directory
2. [Node.js](https://nodejs.org/) 24+ (for the included Electron app)

## Usage

Start an Electron app with `--remote-debugging-port` in one terminal, then run the Nova Act script in another.

### With the included task manager app

**Terminal 1:**

```bash
cd examples/actuation/desktop/electron/app
npm install
npm start
```

**Terminal 2:**

```bash
python -m examples.actuation.desktop.electron.main
```

### With your own Electron app

Launch your app with `--remote-debugging-port` enabled, then point the script at it:

```bash
python -m examples.actuation.desktop.electron.main --cdp_url=http://localhost:9333
```

**Implementation Details:**
- Connects to the Electron app over CDP using the Nova Act SDK's `cdp_endpoint_url` and `cdp_use_existing_page` parameters
- Adds a task, filters by active tasks, and extracts the active task count

## Next Steps

- For the standard AgentCore Browser CDP integration, see [AgentCore Browser →](../../../agentcore/browser/README.md)
- For deploying workflows on AWS, see [CDK →](../../../../cdk/README.md)
- Visit the [Nova Act documentation →](https://docs.aws.amazon.com/nova-act)
