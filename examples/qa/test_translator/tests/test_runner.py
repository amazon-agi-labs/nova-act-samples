"""Main test runner for executing Nova Act tests from JSON feature files."""

import json
import re
from pathlib import Path

import pytest

from examples.nova_act_client import NovaActClient
from examples.qa.test_translator.translator.models import Feature
from examples.qa.test_translator.utils.execution import execute_scenario_impl


def execute_scenario(
    scenario,
    base_url: str,
    workflow_name: str,
    functions_file: Path,
    feature_data: dict,
    app_config,
):
    """Execute a single test scenario with Nova Act by iterating over the scenario's steps.

    This is a thin wrapper around execute_scenario_impl from utils.execution that adapts
    it for pytest by converting exceptions to pytest.fail() calls.

    Args:
        scenario: The test scenario to execute
        base_url: The base URL for the test
        workflow_name: The Nova Act workflow definition name
        functions_file: Path to Python file containing custom functions
        feature_data: Feature dictionary for function call validation
        app_config: Application configuration object

    Returns:
        Dictionary of all extracted variables from the scenario
    """

    def log_callback(message: str, level: str = "info"):
        """Pytest-compatible logging callback"""
        if level == "error":
            print(f"    ✗ {message}")
        else:
            # Format to match original pytest output style
            if message.startswith("Step "):
                print(f"\n  {message}")
            elif message.startswith("  →") or message.startswith("  ✓"):
                print(f"  {message}")
            elif message.startswith("Scenario:") or message == "=" * 60:
                print(f"\n{message}")
            else:
                print(f"    {message}")

    try:
        # Call the consolidated execution engine
        return execute_scenario_impl(
            scenario=scenario,
            base_url=base_url,
            workflow_name=workflow_name,
            functions_file=functions_file,
            feature_data=feature_data,
            log_callback=log_callback,
            config=app_config,
        )
    except AssertionError as e:
        pytest.fail(str(e))
    except Exception as e:
        pytest.fail(f"Scenario failed: {str(e)}")


def test_feature(feature_file: Path, scenario_index: int, test_id: str, request):
    """Execute a single scenario from a JSON feature file.

    Each scenario is parametrized as its own test by conftest.py::pytest_generate_tests().
    Each scenario gets its own workflow definition name for per-test traceability
    in the Nova Act console and S3 logs.
    See execute_scenario() for details on how scenarios are executed.
    """
    app_config = request.config.app_config

    # Read feature JSON file
    with open(feature_file) as f:
        feature_data = json.load(f)
    feature = Feature.model_validate(feature_data)

    scenario = feature.scenarios[scenario_index]

    # Derive a per-scenario workflow definition name for traceability.
    # API limit: 40 chars, pattern [a-zA-Z0-9_-]
    # Budget: "tt-" (3) + feature (18) + "-" (1) + scenario (18) = 40
    feature_slug = re.sub(r"[^\w]+", "-", feature_file.stem).strip("-").lower()
    scenario_slug = re.sub(r"[^\w]+", "-", scenario.name).strip("-").lower()
    workflow_name = f"tt-{feature_slug[:18]}-{scenario_slug[:18]}"

    # Discover or create the workflow definition for this scenario
    NovaActClient.get_workflow_kwargs(workflow_definition_name=workflow_name)

    print(f"\n{'=' * 70}")
    print(f"Feature:  {feature.name}")
    print(f"Scenario: {scenario.name}")
    print(f"Workflow: {workflow_name}")
    print(f"Base URL: {feature.base_url}")
    print("=" * 70)

    # Load config paths
    variable_output_dir = app_config.resolve_extracted_variables_dir()
    functions_file = app_config.resolve_custom_functions_file()

    extracted_vars = execute_scenario(
        scenario,
        feature.base_url,
        workflow_name,
        functions_file,
        feature_data,
        app_config,
    )

    # Save extracted variables if any
    if extracted_vars:
        output_dir = variable_output_dir
        output_dir.mkdir(parents=True, exist_ok=True)

        safe_name = re.sub(r"[^\w\s-]", "", scenario.name)
        safe_name = re.sub(r"[-\s]+", "_", safe_name).lower()

        filepath = output_dir / f"{safe_name}.json"
        output_data = {
            "feature": feature.name,
            "scenario": scenario.name,
            "variables": extracted_vars,
        }

        with open(filepath, "w") as f:
            json.dump(output_data, f, indent=2, default=str)

        print(f"\n  → Variables saved to: {filepath}")
