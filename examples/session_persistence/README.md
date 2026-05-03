# Amazon Nova Act Browser Session Persistence Examples

Examples demonstrating how to save and restore browser session state across Nova Act workflow runs using the Nova Act SDK's [browser session persistence](https://github.com/aws/nova-act#persisting-browser-sessions) features. Each example uses a different storage backend to persist cookies, localStorage, and other session state across workflow runs.

## Repository Structure

```
├── local.py                   # Local file browser session persistence
├── s3.py                      # S3 browser session persistence with SSE-KMS encryption
├── agentcore.py               # AgentCore browser session persistence
├── hitl.py                    # Shared console HITL callbacks
├── static_site.py             # Playwright route handler for the built-in demo site
└── static/
    └── login_dashboard.html   # Self-contained login and dashboard page
```

## Prerequisites

1. Complete the [Getting Started](../README.md#getting-started) section in the main examples directory before running these examples.
2. For `s3.py`: an S3 bucket with SSE-KMS default encryption and AWS credentials with `s3:GetObject` and `s3:PutObject` permissions on the bucket.
3. For `agentcore.py`: AWS credentials with AgentCore permissions.

## Usage

Each example configures a Nova Act SDK [browser session persistence](https://github.com/aws/nova-act#persisting-browser-sessions) provider and uses a prompt that instructs Nova Act to detect a login form and interact with a dashboard. A human-in-the-loop callback lets the user complete login manually on the first run. The provider saves browser session state on exit and restores it automatically on future runs, skipping login and resuming where the previous run left off.

All three examples include a [built-in demo site](static/login_dashboard.html) with a mock authentication flow and dashboard that use cookies and localStorage. To test against a real site, pass `--starting_page` with your target URL.

### local.py - Local File

Saves and restores browser session state on local disk using `LocalFileSessionProvider`. Suitable for single-machine development and testing.

```bash
# Run 1 — pauses for manual login, saves session on exit:
python -m examples.session_persistence.local

# Run 2 — session restored, no login needed:
python -m examples.session_persistence.local

# Use a real website instead of the built-in page:
python -m examples.session_persistence.local --starting_page https://example.com
```

| Parameter | Required | Default | Description |
|---|---|---|---|
| `starting_page` | No | Built-in demo site | URL to navigate to |
| `profile` | No | `local_example` | Session profile name |
| `session_dir` | No | `~/.nova-act/sessions` | Directory for session files |
| `headless` | No | `False` | Run browser in headless mode |

**Implementation Details:**
- Uses the Nova Act SDK's `LocalFileSessionProvider` to automatically manage browser session persistence from a local JSON file
- Browser session state saved to `<session_dir>/<profile>.json`

### s3.py - Amazon S3

Saves and restores browser session state in Amazon S3 with SSE-KMS encryption using `S3SessionProvider`. Suitable for shared or cross-machine use.

**Requires:** an S3 bucket with SSE-KMS default encryption and AWS credentials with `s3:GetObject` and `s3:PutObject` permissions.

```bash
# Run 1 — pauses for manual login, saves session to S3 on exit:
python -m examples.session_persistence.s3 --bucket my-session-bucket

# Run 2 — session restored from S3, no login needed:
python -m examples.session_persistence.s3 --bucket my-session-bucket

# Use a real website instead of the built-in page:
python -m examples.session_persistence.s3 \
    --bucket my-session-bucket --starting_page https://example.com
```

| Parameter | Required | Default | Description |
|---|---|---|---|
| `bucket` | Yes | — | S3 bucket name |
| `starting_page` | No | Built-in demo site | URL to navigate to |
| `profile` | No | `s3_example` | Session profile name |
| `kms_key_id` | No | `None` | KMS key ID or alias for encryption |
| `region` | No | `None` | AWS region |
| `headless` | No | `False` | Run browser in headless mode |

**Implementation Details:**
- Uses the Nova Act SDK's `S3SessionProvider` to automatically manage browser session persistence from an S3 object with SSE-KMS encryption
- Browser session state saved to `s3://<bucket>/nova-act-sessions/<profile>.json`

### agentcore.py - Amazon Bedrock AgentCore

Persists browser session state using `AgentCoreBrowserSessionProvider`. The provider manages an AgentCore Browser session configured with an [AgentCore browser profile](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/browser-profiles.html), which handles saving and restoring session state automatically within AgentCore's infrastructure.

**Requires:** AWS credentials with AgentCore permissions.

```bash
# Run 1 — pauses for manual login, saves profile on exit:
python -m examples.session_persistence.agentcore

# Run 2 — profile restored, no login needed:
python -m examples.session_persistence.agentcore

# Use a real website instead of the built-in page:
python -m examples.session_persistence.agentcore --starting_page https://example.com
```

| Parameter | Required | Default | Description |
|---|---|---|---|
| `starting_page` | No | Built-in demo site | URL to navigate to |
| `profile` | No | `agentcore_example` | AgentCore profile name |
| `region` | No | `us-east-1` | AWS region |
| `headless` | No | `False` | Run browser in headless mode |

**Implementation Details:**
- Uses the Nova Act SDK's `AgentCoreBrowserSessionProvider` to automatically manage browser session persistence via [AgentCore browser profiles](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/browser-profiles.html)
- Connects to the remote browser session started by `AgentCoreBrowserSessionProvider` via CDP using `provider.cdp_session()`
- Pairs well with the [Nova Act Human Intervention Service](https://github.com/amazon-agi-labs/nova-act-human-intervention) for streaming the live browser session to a local browser

## Next Steps

- Read the full browser session persistence documentation in the [SDK README →](https://github.com/aws/nova-act#persisting-browser-sessions)
- For HITL patterns, see [Human in the Loop →](../human_in_the_loop/README.md)
- For production deployments, see [CDK →](../../cdk/README.md)
- For complete applications, see [Solutions →](../../solutions/README.md)
- Visit the [Nova Act documentation →](https://docs.aws.amazon.com/nova-act)
