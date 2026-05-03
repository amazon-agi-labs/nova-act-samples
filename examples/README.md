# Amazon Nova Act Examples

Simple, focused scripts that demonstrate Nova Act's core capabilities. Each example focuses on a specific use case and can be up and running in just a few minutes with minimal configuration.

## Repository Structure

```
├── *.py                                    # Core examples
├── utils.py                                # Shared utilities for all examples
├── actuation/                              # Actuation examples (mobile, browser, custom)
├── agentcore/                              # AgentCore integration examples
├── bbox_locator/                           # Bounding box locator from static images
├── browser_dialogs/                        # Browser dialog handling examples
├── clipboard_manager/                      # Browser clipboard interaction examples
├── element_resolver/                       # DOM element resolution from bounding boxes
├── human_in_the_loop/                      # Human in the loop examples
├── nova_act_client/                        # Shared client wrapper for workflow configuration
├── nova_agents/                            # Nova Agent examples
├── qa/                                     # QA testing examples and utilities
├── session_persistence/                    # Session persistence examples
├── tool_use/                               # Tool use examples
└── trajectory/                             # Trajectory replay examples
```

## Prerequisites

- Operating System: MacOS Sierra+, Ubuntu 22.04+, WSL2 or Windows 10+
- Python: 3.11 or above

> See the [Nova Act SDK repository](https://github.com/aws/nova-act?tab=readme-ov-file#pre-requisites) for a complete up-to-date list of prerequisites

## Getting Started

### Authentication Setup

Nova Act supports multiple authentication methods. See the [Nova Act SDK Authentication Guide](https://github.com/aws/nova-act?tab=readme-ov-file#authentication) to get started with your preferred authentication method.

The examples require one of these authentication methods and will automatically detect your setup using environment variables (see `NovaActClient.get_workflow_kwargs()` in [nova_act_client/client.py](./nova_act_client/client.py)). For environment variable setup instructions, follow the section below for your authentication method.

#### API Key Authentication

1. Set the following environment variable:

   ```bash
   export NOVA_ACT_API_KEY="your-api-key-here"
   ```

#### AWS IAM Authentication

The Nova Act SDK uses [boto3](https://aws.amazon.com/sdk-for-python/) to manage AWS credentials. Your environment must have AWS credentials configured.

1. Configure your environment with AWS credentials. See the [Nova Act IAM documentation](https://docs.aws.amazon.com/nova-act/latest/userguide/security-iam-awsmanpol.html) for required AWS IAM permissions and service-linked roles. The examples auto-discover or create a workflow definition and S3 bucket on first run, which requires these additional permissions:
   - `nova-act:GetWorkflowDefinition`, `nova-act:CreateWorkflowDefinition`
   - `s3:HeadBucket`, `s3:CreateBucket`
   - `sts:GetCallerIdentity`

> By default, the examples use a workflow definition named `nova-act-examples`. To customize:
> ```bash
> export NOVA_ACT_WORKFLOW_DEFINITION_NAME="my-workflow"
> export NOVA_ACT_S3_BUCKET_NAME="my-bucket"
> ```

### Environment Setup

1. **Ensure your environment is configured with an authentication method as described in the Authentication section**
2. **Create and activate a python virtual environment**

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r examples/requirements.txt
   ```

> Some examples have additional dependencies. Check their READMEs for install instructions.

### Run an example

After completing the prior steps in this section, it's time to run an example workflow:

```bash
python -m examples.hello_world
```

## Usage Instructions

### Core Examples

The individual Python files (`*.py`) in this directory demonstrate specific Nova Act capabilities. Each example includes detailed usage instructions and parameter descriptions in the docstring comment at the top of the file.

| Example | Description |
| --- | --- |
| `hello_world.py` | A simple example to get started with |
| `booking.py` | Fill out a multi-step form to book a trip |
| `data_extraction.py` | Extract structured data from websites |
| `flight_search.py` | Search for a flight |
| `qa_simple.py` | Data-driven QA testing with test steps defined as dictionaries |
| `search_apartments_calculate_commute.py` | Search for apartments and calculate distance to transit stations |
| `setup_chrome_user_data_dir.py` | Configure a persistent browser profile for Nova Act workflows |

### Actuation

The `actuation/` directory groups examples that extend or replace Nova Act's default browser actuator — mobile automation, expanded browser actuation, and custom actuator implementations.

[Get Started with Actuation →](actuation/README.md)

### Amazon Bedrock AgentCore

The `agentcore/` directory demonstrates how to use Nova Act with AgentCore capabilities.

[Get Started with AgentCore →](agentcore/README.md)

### Bounding Box Locator

The `bbox_locator/` directory uses Nova Act's image understanding to locate UI elements in static images via a custom `ImageActuator`.

[Get Started with Bounding Box Locator →](bbox_locator/README.md)

### Browser Dialogs

The `browser_dialogs/` directory shows how to handle browser native dialogs (prompt, confirm, alert) using Playwright's dialog event handlers.

[Get Started with Browser Dialogs →](browser_dialogs/README.md)

### Clipboard Manager

The `clipboard_manager/` directory demonstrates how to interact with the browser clipboard using Playwright's permissions and the JavaScript Clipboard API.

[Get Started with Clipboard Manager →](clipboard_manager/README.md)

### Element Resolver

The `element_resolver/` directory shows how to build a custom actuator that resolves bounding box coordinates back to DOM elements, mapping Nova Act interactions to DOM selectors.

[Get Started with Element Resolver →](element_resolver/README.md)

### Human in the Loop (HITL)

The `human_in_the_loop/` directory contains examples that demonstrate human approval workflows and interactive automation patterns.

[Get Started with HITL →](human_in_the_loop/README.md)

### Nova Agents

The `nova_agents/` directory demonstrates how to use Nova Act with the Nova API to build intelligent agents that combine UI automation with Amazon Nova models.

[Get Started with Nova Agents →](nova_agents/README.md)

### QA Testing

The `qa/` directory provides a `NovaActQa` extension class with typed assertions and extraction, along with examples for basic QA patterns and mobile testing via AWS Device Farm.

[Get Started with QA →](qa/README.md)

### Session Persistence

The `session_persistence/` directory demonstrates the Nova Act SDK's [browser session persistence](https://github.com/aws/nova-act#persisting-browser-sessions) features, saving and restoring session state across runs using local files, S3, or [AgentCore browser profiles](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/browser-profiles.html).

[Get Started with Session Persistence →](session_persistence/README.md)

### Tool Use

The `tool_use/` directory showcases Nova Act's integration with external tools.

[Get Started with Tool Use →](tool_use/README.md)

### Trajectory Replay

The `trajectory/` directory demonstrates saving, replaying, and validating Nova Act trajectories.

[Get Started with Trajectory Replay →](trajectory/README.md)

## Next Steps

- For deploying workflows on AWS, see [CDK →](../cdk/README.md)
- For reference applications, see [Solutions →](../solutions/README.md)
- Visit the [AWS documentation →](https://docs.aws.amazon.com/nova-act)
