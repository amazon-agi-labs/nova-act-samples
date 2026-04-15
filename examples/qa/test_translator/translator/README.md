# Gherkin-to-JSON Translator

Converts Gherkin `.feature` files into structured JSON using a [Strands](http://strandsagents.com/) agent with validated Pydantic output. Self-contained module that can be used standalone via CLI or imported programmatically.

## Structure

```
translator/
├── __init__.py          # Exports translate_all_features and Feature
├── agent.py             # Translation logic and Strands agent setup
├── main.py              # Standalone CLI entry point
├── models.py            # Pydantic models (Feature, Scenario, Step, etc.)
└── system_prompt.md     # AI agent system prompt with conversion guidelines
```

## Usage

### CLI

Translate `.feature` files standalone. Paths default to `features/` and `features_translated/` relative to the `test_translator/` directory:

```bash
python -m examples.qa.test_translator.translator.main
```

Override paths, tag mappings, or the translation model:

```bash
python -m examples.qa.test_translator.translator.main \
  --feature_dir path/to/features \
  --output_dir path/to/output \
  --tag search=https://example.com \
  --tag login=https://example.com/login \
  --default_url https://example.com \
  --model_id us.amazon.nova-2-lite-v1:0
```

Tag mappings can also be set via `GHERKIN_TAG_*` environment variables. CLI `--tag` flags take precedence.

Standalone translation is useful for:
- Validating feature file syntax before running tests
- Previewing translated JSON to check step classification
- CI/CD pipelines that separate translation from test execution

### Programmatic

```python
from pathlib import Path
from examples.qa.test_translator.translator import translate_all_features

features = translate_all_features(
    input_dir=Path("features"),
    output_dir=Path("features_translated"),
    tag_url_map={"search": "https://example.com", "default": "https://example.com"},
    bedrock_model_id="amazon.nova-2-lite-v1:0",
)
```

## How It Works

Callers provide an input directory of `.feature` files, an output directory for JSON results, a tag-to-URL mapping, and a Bedrock model ID. The translator parses each `.feature` file into a Gherkin AST using the `gherkin-official` parser, serializes the AST to JSON, and sends it to a Strands agent as a prompt. The agent is configured with `structured_output_model=Feature`, so its response is automatically validated against the `Feature` Pydantic schema defined in `models.py`.

The system prompt in `system_prompt.md` tells the agent how to interpret each Gherkin step. For every step, the agent decides whether it represents an action the browser should perform (instruction), a value to extract and store for later (extraction), or a check against an expected result (validation). Each `TestStep` in the output carries exactly one of these three, enforced by a Pydantic model validator.

Tags and metadata are handled after the agent returns. Feature tags are matched against the provided `tag_url_map` to resolve the starting URL. Metadata like the source filename, conversion timestamp, and model ID are also attached at this stage.

A single `Agent` instance is created per `translate_all_features()` call and reused across all feature files. Translated results are saved as JSON files to the provided output directory.

## Key Classes

The Pydantic models in `models.py` define the JSON schema for translated output. The hierarchy is:

`Feature` → `TestScenario` → `TestStep` → one of `Extraction`, `Validation`, or `FunctionCall`

### `Feature`

Top-level model representing a translated `.feature` file.

| Field | Purpose |
|---|---|
| `name` | Feature name from Gherkin |
| `base_url` | Starting URL resolved from tag mapping |
| `scenarios` | List of `TestScenario` |
| `conversion_timestamp` | ISO 8601 timestamp of translation |
| `source_file` | Original `.feature` filename |
| `bedrock_model_id` | Model used for translation |

### `TestStep`

A single translated Gherkin step. Exactly one of the four fields must be set (enforced by a model validator):

| Field | Type | When used |
|---|---|---|
| `instruction` | `str` | Browser action via `act()` |
| `extraction` | `Extraction` | Extract and store a value via `expect().as_*()` |
| `validation` | `Validation` | Assert a value via `expect().to_*()` |
| `function_call` | `FunctionCall` | Call a custom Python function |

### `Validation`

| Field | Purpose |
|---|---|
| `prompt` | `NovaActQa` extraction prompt |
| `expected` | Expected value to compare against |
| `comparison` | Comparison type: `equal`, `contain`, `match`, `greater_than`, `less_than`, `true`, `false`, etc. |

## Notes

- The Bedrock model ID is configurable. Larger models produce more reliable translations, especially for complex validation steps with expected values.
- `models.py` defines the JSON schema for the translated output
