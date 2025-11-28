# Amazon Nova Act Examples

Simple, focused scripts that demonstrate Nova Act's core capabilities. Each example focuses on a specific use case and can be up and running in just a few minutes with minimal configuration.

## Repository Structure

```
├── *.py                                    # Core examples
├── utils.py                                # Shared utilities for all examples
├── human_in_the_loop/                      # Human in the loop examples
├── nova_agents/                            # Nova Agent examples
└── tool_use/                               # Tool use examples
```

## Prerequisites

- Operating System: MacOS Sierra+, Ubuntu 22.04+, WSL2 or Windows 10+
- Python: 3.10 or above

> See the [Nova Act SDK repository](https://github.com/aws/nova-act?tab=readme-ov-file#pre-requisites) for a complete up-to-date list of prerequisites

## Getting Started

### Authentication Setup

Nova Act supports multiple authentication methods. See the [Nova Act SDK Authentication Guide](https://github.com/aws/nova-act?tab=readme-ov-file#authentication) to get started with your preferred authentication method.

The examples require one of these authentication methods and will automatically detect your setup using environment variables (see `get_workflow_kwargs()` in [utils.py](./utils.py)). For environment variable setup instructions, follow the section below for your authentication method.

#### API Key Authentication

1. Set the following environment variable:

   ```bash
   export NOVA_ACT_API_KEY="your-api-key-here"
   ```

#### AWS IAM Authentication

The Nova Act SDK uses [boto3](https://aws.amazon.com/sdk-for-python/) to manage AWS credentials. Your environment must have AWS credentials configured.

1. Configure your environment with AWS credentials
2. Create a workflow definition from the AWS Console or via the AWS CLI:
   ```bash
   aws nova-act create-workflow-definition --name "my-workflow"
   ```
   > Note: Ensure you have the latest AWS CLI version installed or updated to access Nova Act commands
3. Set the workflow definition name in an environment variable:
   ```bash
   export NOVA_ACT_WORKFLOW_DEFINITION_NAME="my-workflow"
   ```

### Environment Setup

1. **Ensure your environment is configured with an authentication method as described in the Authentication section**
2. **Create and activate a python virtual environment**

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install Nova Act SDK**
   ```bash
   pip install nova-act
   ```

### Run a workflow

After completing the prior steps in this section, it's time to run a workflow:

```bash
python -m examples.hello_world
```

## Usage Instructions

### Core Examples

The individual Python files (`*.py`) in this directory demonstrate specific Nova Act capabilities. Each example includes detailed usage instructions and parameter descriptions in the docstring comment at the top of the file.

### Human in the Loop (HITL)

The `human_in_the_loop/` directory contains examples that demonstrate human approval workflows and interactive automation patterns.

[Get Started with HITL →](human_in_the_loop/README.md)

### Nova Agents

The `nova_agents/` directory demonstrates how to use Nova Act with the Nova API to build intelligent agents that combine UI automation with Amazon Nova models.

[Get Started with Nova Agents →](nova_agents/README.md)

### Tool Use

The `tool_use/` directory showcases Nova Act's integration with external tools.

[Get Started with Tool Use →](tool_use/README.md)

## Next Steps

- For deploying workflows on AWS, see [CDK →](../cdk/README.md)
- For reference applications, see [Solutions →](../solutions/README.md)
- Visit the [AWS documentation →](https://docs.aws.amazon.com/nova-act)