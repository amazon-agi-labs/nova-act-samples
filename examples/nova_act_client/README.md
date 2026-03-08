# Nova Act Client Wrapper

Manages Nova Act Workflow Definition resources and provides shared workflow configuration for all examples.

## Structure

```
nova_act_client/
├── __init__.py    # Re-exports NovaActClient
└── client.py      # Client implementation
```

## Key Classes

### `NovaActClient`

Wraps the Nova Act service API for creating, fetching, and auto-discovering WorkflowDefinitions. All operations target us-east-1 (the only supported region). On first run, `discover_workflow_definition()` creates the definition and its S3 export bucket automatically.

`get_workflow_kwargs()` is a static method used by every example to build the `@workflow` decorator arguments from environment variables:

| Variable | Purpose | Default |
|---|---|---|
| `NOVA_ACT_API_KEY` | API key (skips workflow definition discovery when set) | None |
| `NOVA_ACT_MODEL_ID` | Model identifier | `nova-act-latest` |
| `NOVA_ACT_WORKFLOW_DEFINITION_NAME` | WorkflowDefinition name | `nova-act-examples` |
| `NOVA_ACT_S3_BUCKET_NAME` | S3 bucket for workflow logs | Auto-generated from account ID |
