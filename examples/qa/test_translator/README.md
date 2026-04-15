# Amazon Nova Act QA Test Translator Example

Translates Gherkin feature files into executable Nova Act tests, enabling QA teams to use AI-powered browser automation without writing or maintaining automation code. A Strands agent converts BDD test steps into Nova Act instructions, while pytest handles execution and reporting via [pytest-html](https://github.com/pytest-dev/pytest-html) and [pytest-html-nova-act](https://github.com/aws/pytest-html-nova-act).

## Repository Structure

```
test_translator/
├── features/                  # Gherkin .feature files (input)
├── tests/                     # Pytest test execution
├── translator/                # Gherkin-to-JSON translation module
├── utils/                     # Shared utilities
├── config/                    # Configuration management
├── custom_functions_sample.py # Sample custom test functions
├── pytest.ini                 # Pytest configuration
└── requirements.txt           # Python dependencies
```

## Prerequisites

1. Complete the [Getting Started](../../README.md#getting-started) section in the main examples directory
2. Configure environment with AWS credentials for access to Amazon Bedrock (for translation) and Amazon Nova Act (for test execution)
3. Install dependencies:
   ```bash
   pip install -r examples/qa/test_translator/requirements.txt
   ```
4. Copy the environment file:
   ```bash
   cp examples/qa/test_translator/.env.example examples/qa/test_translator/.env
   ```
   See the [Configuration Reference](config/README.md) for all available environment variables.

## Quick Start

An example feature file ([`features/destination_selection.feature`](features/destination_selection.feature)) is included with three scenarios demonstrating basic validation, variable extraction, and custom function calls. A matching tag mapping (`GHERKIN_TAG_nextdotgym`) is preconfigured in `.env.example`. After copying `.env.example` to `.env`, everything works out of the box:

```bash
python -m pytest examples/qa/test_translator/tests/
```

On first run (or when no JSON files exist in `features_translated/`), translation happens automatically. Subsequent runs reuse existing JSON files unless `TRANSLATE_FEATURES=true` is set.

### View test results

After the tests run, test results are generated as HTML in `reports/report.html` with embedded Nova Act trajectory logs.

```bash
open reports/report.html
```

### Translate without running tests

```bash
python -m examples.qa.test_translator.translator.main
```

See the [translator README](translator/README.md) for standalone CLI options.

## Bring Your Own Tests

### Requirements

1. Each feature must have a tag (e.g., `@search`) that maps to a URL in `.env` (see [Configuring tag-to-URL mappings](#configuring-tag-to-url-mappings)) for the test to start at
2. Use standard Gherkin syntax (Given/When/Then/And/But)
3. Write steps in natural language describing user actions and expectations

### Additional Features

The translator supports the following Gherkin features beyond basic step translation:

- **[Tag-to-URL Mappings](#configuring-tag-to-url-mappings)**: Map Gherkin feature tags to starting URLs for tests
- **[Variable Extraction and References](#variable-extraction-and-references)**: Extract values from the page and reference them in later steps
- **[Custom Functions](#custom-functions)**: Call Python functions from Gherkin steps for custom logic and data generation

### Writing Gherkin features

Place `.feature` files in the `features/` directory (configurable via `FEATURE_DIR` in `.env`):

```gherkin
@search
Feature: Product Search
  As a user
  I want to search for products
  So that I can find items I'm interested in

  Scenario: Search for a product
    Given I am on the homepage
    When I enter "laptop" in the search box
    And I click the search button
    Then I should see search results
    And the results should contain "laptop"
    And there should be at least 5 products displayed
```

### Configuring tag-to-URL mappings

Each feature must have a tag (e.g., `@search`) that maps to a starting URL. Add mappings to `.env` using the `GHERKIN_TAG_<tagname>` format:

```bash
GHERKIN_TAG_search=https://example.com
GHERKIN_TAG_login=https://example.com/login
GHERKIN_TAG_checkout=https://example.com/cart/checkout
```

If no mapping is found for a tag, `DEFAULT_TEST_URL` is used as a fallback. See the [Configuration Reference](config/README.md) for the full list of environment variables.

### Variable extraction and references

Extract values from web pages and reference them in subsequent steps using `${variable_name}` syntax:

```gherkin
@checkout
Feature: Order Processing
  Scenario: Place order and verify confirmation
    Given I am on the product page
    When I click "Add to Cart"
    And I navigate to checkout
    And I extract the order ID as "order_id"
    And I extract the total price as "total_price"
    And I click "Place Order"
    Then I should see "Order Confirmed"
    And the confirmation page should show order "${order_id}"
    And the confirmation total should be "${total_price}"
```

**Notes:**
- Variables must be extracted before they are referenced
- Each scenario has independent variable scope
- Extracted variables are saved to `extracted_variables/<scenario_name>.json` (configurable via `EXTRACTED_VARIABLES_DIR` in `.env`)

### Custom functions

Call custom Python functions from Gherkin steps for custom logic, data generation, and calculations:

```gherkin
@shopping
Feature: Shopping Cart with Discounts
  Scenario: Apply discount and verify final price
    Given I am on the product page
    When I extract the product price as "original_price"
    And I call "calculate_discount" with price ${original_price} and discount_percent 20 and store as "discounted_price"
    And I call "calculate_tax" with amount ${discounted_price} and rate 0.08 and store as "tax_amount"
    And I apply the discount code "SAVE20"
    Then the cart total should be "${discounted_price}"
```

Define functions in a Python file and set `CUSTOM_FUNCTIONS_FILE` in `.env` (defaults to `custom_functions_sample.py`). The translator recognizes steps containing phrases like "I call" or "call function" and parses the function name, parameters, and storage key from the natural language. At test time, the runner loads the Python file and calls the matching function by name. See [`custom_functions_sample.py`](custom_functions_sample.py) for examples and the [utils README](utils/README.md) for reserved parameter injection (`nova_act`, `context`).

### Force re-translation

```bash
TRANSLATE_FEATURES=true python -m pytest examples/qa/test_translator/tests/
```

## Implementation Details

The translator converts `.feature` files to structured JSON using a Strands agent. Each Gherkin step is classified as one of:

- Instruction: an action to perform (e.g., "Click the login button")
- Extraction: extract and store a value for later use (e.g., extract an order ID)
- Validation: extract a value and assert it matches expectations (e.g., verify page title equals "Dashboard")
- Function call: invoke a custom Python function with parameters (e.g., call "calculate_discount" with a price)

At test time, `test_runner.py` loads the JSON, creates a Nova Act `Workflow` session, and iterates through each scenario's steps using [`NovaActQa`](../nova_act_qa/README.md). For each step, the runner checks the step type and delegates accordingly: instructions are passed to `act()`, extractions use `expect().as_*()` to capture a value and store it in a shared variable dictionary, validations use `expect().to_*()` to assert against an expected value, and function calls load the matching function from the custom functions file and invoke it with resolved parameters. Variable references (`${name}`) in any step are substituted from the shared dictionary before execution. Results are reported through standard pytest assertions with HTML reports generated by pytest-html and pytest-html-nova-act.

### Test execution flow

1. Pytest session starts and translates `.feature` files if needed
2. `pytest_generate_tests` discovers JSON files in `features_translated/` and parametrizes one test per scenario across all features
3. For each scenario, `test_runner.py` loads the parent feature JSON, validates it with Pydantic models, and executes that scenario's steps sequentially
4. Extracted values are stored for use in subsequent steps within the same scenario

For running tests outside of pytest (e.g., from a CI/CD pipeline or web app), see the [`execute_feature()` API](utils/README.md).

## Limitations

- Sequential execution only, no parallelization (consider using [`pytest-xdist`](https://pypi.org/project/pytest-xdist/) for parallelization)
- Pytest HTML reports only, no Allure or advanced reporting
- The translator's system prompt (`translator/system_prompt.md`) may need tweaking for your application's domain or terminology to improve translation accuracy
- The translator uses the Strands default Bedrock model for translation — depending on your domain complexity, you may want to configure `BEDROCK_MODEL_ID` in `.env` to a model that better suits your translation needs

## Next Steps

- For the full `NovaActQa` API reference, see [NovaActQa →](../nova_act_qa/README.md)
- For mobile QA, see [Mobile QA](../mobile_qa/README.md)
- For deploying workflows on AWS, see [CDK](../../../cdk/README.md)
- Visit the [Nova Act documentation →](https://docs.aws.amazon.com/nova-act)
