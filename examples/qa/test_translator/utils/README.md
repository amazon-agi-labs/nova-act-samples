# Test Translator Execution and Function Utilities

Utilities for programmatic test execution and custom function loading. Used internally by [`test_runner.py`](../tests/test_runner.py) and available as a standalone API for running tests outside of pytest.

## Structure

```
utils/
├── __init__.py              # Package marker
├── execution.py             # Programmatic execution API and scenario runner
└── function_helpers.py      # Custom function loader with dot-notation support
```

## Key Classes

### `TestResult`

Dataclass returned by `execute_feature()` with execution summary.

| Field | Type | Purpose |
|---|---|---|
| `success` | `bool` | Whether all scenarios passed |
| `summary` | `dict` | Counts: `total_scenarios`, `passed`, `failed` |
| `duration` | `float` | Total execution time in seconds |
| `recording_path` | `str \| None` | Path to video recording directory |
| `errors` | `list[str]` | Error messages from failed scenarios |

## Key Functions

### `execute_feature()`

Programmatic entry point for running translated tests without pytest. Accepts a translated feature dict, a workflow name, and an optional `log_callback` for real-time log streaming (e.g., to a WebSocket).

```python
from examples.qa.test_translator.utils.execution import execute_feature

result = execute_feature(
    feature_data=translated_json,
    workflow_name="my-workflow",
    log_callback=lambda msg, level: print(f"[{level}] {msg}"),
)
print(f"Passed: {result.summary['passed']}/{result.summary['total_scenarios']}")
```

### `get_function_from_module()`

Loads a function from a Python module by name. Supports dot notation for nested attributes (e.g., `"user_service.create_user"`).

## Custom Function Reserved Parameters

When writing custom functions called from Gherkin steps, two parameter names are automatically injected by the test runner:

| Parameter | Injected Value | Purpose |
|---|---|---|
| `nova_act` | `NovaActQa` instance | Browser interactions during the test |
| `context` | `{"variables": {...}}` | All previously extracted variables |

See [`custom_functions_sample.py`](../custom_functions_sample.py) for examples.
