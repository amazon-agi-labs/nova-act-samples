# Amazon Nova Act AgentCore Browser Examples

Uses Amazon Bedrock AgentCore Browser Tool to run Nova Act workflows on managed remote browser sessions connected via CDP (Chrome DevTools Protocol).

## Repository Structure

```
├── main.py          # AgentCore Browser session example
└── utils.py         # Shared utility functions
```

## Prerequisites

1. Complete the [Getting Started](../../README.md#getting-started) section in the main examples directory
2. Configure environment with AWS credentials for full access to AgentCore and Nova Act
   - Note: full access is for example purposes only, permissions should be scoped down for further use
3. Install dependencies:
   ```bash
   pip install -r examples/agentcore/requirements.txt
   ```

## Usage

### main.py - AgentCore Browser Session

Creates a managed browser session via `BrowserClient` and runs a Nova Act workflow on it.

```bash
python -m examples.agentcore.browser.main
```

**Implementation Details:**
- Managed browser sessions with automatic scaling
- Isolated execution environments for security
- Automatic resource cleanup
- CDP integration for seamless Nova Act connection
- Live console URL to watch the session in the AWS Console

## Next Steps

- Learn more about AgentCore in the [AWS documentation](https://docs.aws.amazon.com/bedrock-agentcore/)
- Visit the [Nova Act documentation →](https://docs.aws.amazon.com/nova-act)
