"""Main test runner for executing Nova Act tests from JSON feature files."""

import json
import os
from pathlib import Path

import pytest
from nova_act import Workflow

from examples.nova_act_client import NovaActClient
from examples.qa.nova_act_qa import NovaActQa
from examples.qa.test_translator.translator.models import Feature


def execute_scenario(scenario, base_url: str, workflow_name: str, headless: bool):
    """Execute a single test scenario with Nova Act by iterating over the scenario's steps."""
    scenario_name = scenario.name
    steps = scenario.steps

    print(f"\n{'=' * 70}")
    print(f"Scenario: {scenario_name}")
    print("=" * 70)

    extracted_values = {}

    # Start Nova Act Workflow for this scenario
    with Workflow(
        workflow_definition_name=workflow_name,
        model_id=os.getenv("NOVA_ACT_MODEL_ID", NovaActClient.DEFAULT_MODEL_ID),
    ) as workflow:
        with NovaActQa(
            starting_page=base_url,
            workflow=workflow,
            headless=headless,
            tty=False,  # For pytest log compatibility
        ) as nova:
            # Execute each step
            for step_idx, step in enumerate(steps, 1):
                keyword = step.original_keyword
                text = step.original_text

                print(f"\n  Step {step_idx}: {keyword} {text}")

                try:
                    if step.instruction:
                        instruction = step.instruction
                        print(f"    → Action: {instruction}")
                        nova.act(instruction)
                        print("    ✓ Success")

                    elif step.extraction:
                        extraction = step.extraction
                        prompt = extraction.prompt
                        extraction_type = extraction.extraction_type
                        extraction_key = extraction.extraction_key

                        print(f"    → Extract ({extraction_type}): {prompt}")
                        print(f"    → Store as: {extraction_key}")

                        value = getattr(nova.expect(prompt), f"as_{extraction_type}")()

                        extracted_values[extraction_key] = value
                        print(f"    ✓ Extracted: {value}")

                    elif step.validation:
                        validation = step.validation
                        prompt = validation.prompt
                        expected = validation.expected
                        comparison = validation.comparison

                        print(f"    → Validate ({comparison}): {prompt}")
                        if comparison not in ("true", "false"):
                            print(f"    → Expected: {expected}")

                        # Map comparison to Nova Act QA method name
                        if comparison in ("equal", "contain", "match"):
                            method_name = f"to_{comparison}"
                        else:
                            method_name = f"to_be_{comparison}"

                        expectation = nova.expect(prompt)
                        assert_method = getattr(expectation, method_name)

                        if comparison in ("true", "false"):
                            actual = assert_method()
                        else:
                            actual = assert_method(expected)

                        print("    ✓ Validation passed")
                        print(f"    → Actual: {actual}")

                except AssertionError as e:
                    print(f"    ✗ Validation failed: {e}")
                    pytest.fail(str(e))
                except Exception as e:
                    print(f"    ✗ Error: {str(e)}")
                    pytest.fail(f"Step failed: {str(e)}")

    print(f"\n  ✓ Scenario PASSED: {scenario_name}")


def test_feature(feature_file: Path, feature_name: str, request):
    """
    Single pytest test that executes all JSON-defined features (see translator)
    Each scenario from each JSON file becomes a separate test.
    See conftest.py::pytest_generate_tests() for details on how the tests are generated.
    See execute_scenario() for details on how the scenarios are executed.
    """
    app_config = request.config.app_config
    workflow_name = app_config.workflow_definition_name

    print(f"\n{'=' * 70}")
    print(f"Feature: {feature_name}")
    print("=" * 70)

    # Read feature JSON file
    with open(feature_file) as f:
        feature_data = json.load(f)
    feature = Feature.model_validate(feature_data)

    print(f"Name:      {feature.name}")
    print(f"Base URL:  {feature.base_url}")
    print(f"Scenarios: {len(feature.scenarios)}")

    # Execute each scenario
    for scenario in feature.scenarios:
        execute_scenario(scenario, feature.base_url, workflow_name, app_config.headless)
