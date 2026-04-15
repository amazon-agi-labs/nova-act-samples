# Test Translator Configuration Reference

Unified configuration for the QA Test Translator, powered by Pydantic Settings. All settings are loaded from environment variables or a `.env` file. Copy `.env.example` to `.env` to get started.

## Structure

```
config/
├── __init__.py          # Exports AppConfig
├── app_config.py        # Pydantic Settings model with all env vars
├── decorators.py        # Validation decorator for friendly error formatting
└── exceptions.py        # ConfigurationError exception
```

## Key Classes

### `AppConfig`

Loads and validates all environment variables. Inherits from Pydantic `BaseSettings`, so values can come from `.env`, environment variables, or constructor kwargs.

See [`conftest.py`](../tests/conftest.py) and [`execution.py`](../utils/execution.py) for usage.

## Environment Variables

### Test Execution

| Variable | Purpose | Default |
|---|---|---|
| `TRANSLATE_FEATURES` | Auto-translate `.feature` files before running tests | `false` |
| `NOVA_ACT_WORKFLOW_DEFINITION_NAME` | Nova Act Workflow Definition name | `nova-act-examples` |
| `NOVA_ACT_MODEL_ID` | Nova Act model (`nova-act-latest` or `nova-act-preview`) | `nova-act-latest` |
| `NOVA_ACT_S3_BUCKET_NAME` | S3 bucket for workflow export logs | Auto-created |
| `HEADLESS` | Run browser without a visible window | `false` |

### Translation

| Variable | Purpose | Default |
|---|---|---|
| `BEDROCK_MODEL_ID` | Bedrock model ID for Strands agent translation | Strands default |
| `FEATURE_DIR` | Directory containing `.feature` files | `features` |
| `TRANSLATED_FEATURE_DIR` | Output directory for translated JSON | `features_translated` |

### Custom Functions and Variables

| Variable | Purpose | Default |
|---|---|---|
| `CUSTOM_FUNCTIONS_FILE` | Path to Python file with custom test functions | `custom_functions_sample.py` |
| `EXTRACTED_VARIABLES_DIR` | Directory for extracted variable JSON files | `extracted_variables` |

### Video Recording

| Variable | Purpose | Default |
|---|---|---|
| `ENABLE_VIDEO_RECORDING` | Record browser sessions during test execution | `false` |
| `VIDEO_RECORDING_DIR` | Directory for video recordings | `./recordings` |

### Tag-to-URL Mappings

| Variable | Purpose | Default |
|---|---|---|
| `GHERKIN_TAG_<tagname>` | Maps a Gherkin feature tag to a starting URL | — |
| `DEFAULT_TEST_URL` | Fallback URL when no tag mapping matches | — |

Tag mappings connect Gherkin feature tags to the URL where Nova Act starts the browser. For a feature tagged `@login`, set `GHERKIN_TAG_login=https://example.com/login` in `.env`.

## Notes

- All path variables can be absolute or relative to the `test_translator/` directory.
- `AppConfig` raises a formatted `ConfigurationError` (via the `@validate_app_config` decorator) when required variables are missing or invalid, instead of a raw Pydantic `ValidationError`.
