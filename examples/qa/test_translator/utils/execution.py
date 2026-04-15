"""
Execution wrapper for programmatic test execution.

This module provides a bridge between the web app backend and the pytest-based
test runner. It provides standalone execution without pytest dependencies.
"""

import importlib.util
import inspect
import json
import os
import re
import time
from pathlib import Path
from typing import Callable, Optional
from dataclasses import dataclass, field

from nova_act import Workflow

from examples.qa.test_translator.translator.models import Feature
from examples.qa.nova_act_qa import NovaActQa
from examples.qa.test_translator.utils.function_helpers import get_function_from_module
from examples.qa.test_translator.config.app_config import AppConfig
from examples.nova_act_client import NovaActClient


@dataclass
class TestResult:
    """Result of test execution"""
    success: bool
    summary: dict  # {'total_scenarios': int, 'passed': int, 'failed': int}
    duration: float  # seconds
    recording_path: Optional[str] = None
    errors: list[str] = field(default_factory=list)


def validate_function_calls_from_data(feature_data: dict, functions_file: Path) -> list[str]:
    """Validate that function calls in feature data reference existing functions.

    Args:
        feature_data: Feature dictionary (translated JSON)
        functions_file: Path to Python file containing custom functions

    Returns:
        List of error messages (empty if all valid)
    """
    if not functions_file.exists():
        return []

    spec = importlib.util.spec_from_file_location("custom_functions", functions_file)
    if spec is None or spec.loader is None:
        return [f"Cannot load functions file: {functions_file}"]

    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except Exception as e:
        return [f"Error loading functions file: {e}"]

    errors = []
    for scenario in feature_data.get('scenarios', []):
        scenario_name = scenario.get('name', 'Unknown')
        for step_idx, step in enumerate(scenario.get('steps', []), 1):
            function_call = step.get('function_call')
            if function_call is not None:
                func_name = function_call['function_name']
                original_text = step.get('original_text', '')
                func = getattr(module, func_name, None)
                if func is None:
                    errors.append(
                        f"Scenario '{scenario_name}', Step {step_idx} ('{original_text}'): "
                        f"Function '{func_name}' not found"
                    )
    return errors


def substitute_variables(text: str, variables: dict) -> str:
    """Replace ${variable_name} references with actual values.

    Args:
        text: Text containing variable references
        variables: Dictionary of extracted variables

    Returns:
        Text with all variable references replaced

    Raises:
        KeyError: If a referenced variable is not found
    """
    if not text:
        return text

    pattern = r'\$\{([^}]+)\}'

    def replacer(match):
        var_name = match.group(1)
        if var_name not in variables:
            raise KeyError(f"Variable '${{{var_name}}}' not found in context")
        return str(variables[var_name])

    return re.sub(pattern, replacer, text)


def execute_scenario_impl(scenario, base_url: str, workflow_name: str,
                         functions_file: Path, feature_data: dict, log_callback,
                         config: Optional['AppConfig'] = None):
    """Execute a single test scenario with Nova Act.

    Args:
        scenario: The test scenario to execute
        base_url: The base URL for the test
        workflow_name: The Nova Act workflow definition name
        functions_file: Path to Python file containing custom functions
        feature_data: Feature dictionary for function call validation
        log_callback: Callback for logging messages
        config: Application configuration (created from env if not provided)

    Returns:
        Dictionary of all extracted variables from the scenario
    """
    def log(message: str, level: str = "info"):
        """Helper to log messages"""
        if log_callback:
            log_callback(message, level)
        print(f"[{level.upper()}] {message}")

    # Validate function calls before execution (uses data directly, no temp files)
    validation_errors = validate_function_calls_from_data(feature_data, functions_file)
    if validation_errors:
        error_msg = "\n".join(validation_errors)
        raise RuntimeError(f"Function validation failed:\n{error_msg}")

    scenario_name = scenario.name
    steps = scenario.steps

    log(f"{'=' * 60}")
    log(f"Scenario: {scenario_name}")
    log(f"{'=' * 60}")

    extracted_values = {}

    # Load custom functions module only if file exists
    custom_functions = None
    if functions_file.exists():
        spec = importlib.util.spec_from_file_location("custom_functions", functions_file)
        custom_functions = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(custom_functions)

    # Get config for video recording settings
    if config is None:
        config = AppConfig()

    # Build NovaActQa kwargs
    nova_kwargs = {
        'starting_page': base_url,
        'workflow': None,  # Will be set from workflow context
        'headless': config.headless,
        'tty': False,  # For pytest log compatibility
    }

    # Add video recording parameters if enabled
    if config.enable_video_recording:
        video_dir = config.resolve_video_recording_dir()
        video_dir.mkdir(parents=True, exist_ok=True)
        nova_kwargs['record_video'] = True
        nova_kwargs['logs_directory'] = str(video_dir)
        log(f"Video recording enabled: {video_dir}")

    # Start Nova Act Workflow for this scenario
    model_id = os.getenv("NOVA_ACT_MODEL_ID", NovaActClient.DEFAULT_MODEL_ID)
    with Workflow(workflow_definition_name=workflow_name, model_id=model_id) as workflow:
        nova_kwargs['workflow'] = workflow
        with NovaActQa(**nova_kwargs) as nova:
            # Execute each step
            for step_idx, step in enumerate(steps, 1):
                keyword = step.original_keyword
                text = step.original_text

                log(f"Step {step_idx}: {keyword} {text}")

                try:
                    # Check if this is a function call step
                    if step.function_call:
                        func_name = step.function_call.function_name
                        parameters = step.function_call.parameters
                        storage_key = step.function_call.storage_key

                        log(f"  → Call function: {func_name}")
                        if parameters:
                            log(f"  → Parameters: {parameters}")

                        # Check if custom_functions module is available
                        if custom_functions is None:
                            raise RuntimeError(
                                f"Cannot call function '{func_name}': "
                                f"Custom functions file not found at {functions_file}"
                            )

                        # Substitute variables in parameters
                        resolved_params = {}
                        for key, value in parameters.items():
                            if isinstance(value, str):
                                resolved_params[key] = substitute_variables(value, extracted_values)
                            else:
                                resolved_params[key] = value

                        # Get the function and inspect its signature
                        func = get_function_from_module(custom_functions, func_name)

                        # Check for reserved parameter names and inject them
                        sig = inspect.signature(func)

                        if 'nova_act' in sig.parameters:
                            resolved_params['nova_act'] = nova

                        if 'context' in sig.parameters:
                            resolved_params['context'] = {
                                'variables': extracted_values
                            }

                        # Call the function with resolved parameters
                        result = func(**resolved_params)

                        # Store result if storage key specified
                        if storage_key:
                            extracted_values[storage_key] = result
                            log(f"  → Stored as: {storage_key}")

                        log(f"  ✓ Result: {result}")

                    elif step.instruction:
                        # Substitute variables in instruction before execution
                        instruction = substitute_variables(step.instruction, extracted_values)
                        log(f"  → Action: {instruction}")
                        nova.act(instruction)
                        log("  ✓ Success")

                    elif step.extraction:
                        extraction = step.extraction
                        # Substitute variables in extraction prompt before extraction
                        prompt = substitute_variables(extraction.prompt, extracted_values)
                        extraction_type = extraction.extraction_type
                        extraction_key = extraction.extraction_key

                        log(f"  → Extract ({extraction_type}): {prompt}")
                        log(f"  → Store as: {extraction_key}")

                        # Use NovaActQa expect().as_*() API
                        value = getattr(nova.expect(prompt), f"as_{extraction_type}")()

                        extracted_values[extraction_key] = value
                        log(f"  ✓ Extracted: {value}")

                    elif step.validation:
                        validation = step.validation
                        # Substitute variables in validation prompt and expected value before validation
                        prompt = substitute_variables(validation.prompt, extracted_values)
                        expected = validation.expected
                        if isinstance(expected, str):
                            expected = substitute_variables(expected, extracted_values)
                        comparison = validation.comparison

                        log(f"  → Validate ({comparison}): {prompt}")
                        if comparison not in ("true", "false"):
                            log(f"  → Expected: {expected}")

                        # Map comparison to Nova Act QA method name
                        if comparison in ("equal", "contain", "match", "greater_than", "less_than", "greater_or_equal", "less_or_equal"):
                            method_name = f"to_{comparison}"
                        else:
                            method_name = f"to_be_{comparison}"

                        expectation = nova.expect(prompt)
                        assert_method = getattr(expectation, method_name)

                        if comparison in ("true", "false"):
                            actual = assert_method()
                        else:
                            actual = assert_method(expected)

                        log(f"  ✓ Validation passed")
                        log(f"  → Actual: {actual}")

                except AssertionError as e:
                    log(f"  ✗ Validation failed: {e}", "error")
                    raise  # Re-raise to be caught by outer handler
                except Exception as e:
                    log(f"  ✗ Error: {str(e)}", "error")
                    raise  # Re-raise to be caught by outer handler

    log(f"✓ Scenario PASSED: {scenario_name}")

    # Return extracted_values dict to caller
    return extracted_values


def execute_feature(
    feature_data: dict,
    workflow_name: str,
    log_callback: Optional[Callable[[str, str], None]] = None
) -> TestResult:
    """
    Execute a feature with all its scenarios — programmatic API for external consumers.

    This is the non-pytest entry point for running translated tests. It provides a
    log_callback parameter for real-time streaming (e.g., to a WebSocket for live UI
    updates) and returns a TestResult with execution summary.

    Used by the Nova Act QA Web App (execution_service.py) for browser-based test execution.

    Args:
        feature_data: Feature dictionary (translated JSON)
        workflow_name: Nova Act workflow definition name
        log_callback: Optional callback for logging (message, level)

    Returns:
        TestResult with execution summary and status
    """
    start_time = time.time()

    def log(message: str, level: str = "info"):
        """Helper to log messages"""
        if log_callback:
            log_callback(message, level)
        print(f"[{level.upper()}] {message}")

    try:
        # Parse feature data
        feature = Feature.model_validate(feature_data)

        log(f"Starting feature execution: {feature.name}")
        log(f"Base URL: {feature.base_url}")
        log(f"Scenarios: {len(feature.scenarios)}")

        # Load config
        config = AppConfig()
        functions_file = config.resolve_custom_functions_file()

        # Track results
        total_scenarios = len(feature.scenarios)
        passed = 0
        failed = 0
        errors = []
        recording_path = None

        # Execute each scenario
        for idx, scenario in enumerate(feature.scenarios, 1):
            log(f"\n{'='*60}")
            log(f"Scenario {idx}/{total_scenarios}: {scenario.name}")
            log(f"{'='*60}")

            try:
                # Execute scenario using our standalone implementation
                extracted_vars = execute_scenario_impl(
                    scenario=scenario,
                    base_url=feature.base_url,
                    workflow_name=workflow_name,
                    functions_file=functions_file,
                    feature_data=feature_data,
                    log_callback=log_callback
                )

                passed += 1
                log(f"✓ Scenario PASSED: {scenario.name}", "info")

                if extracted_vars:
                    log(f"Extracted {len(extracted_vars)} variables", "info")

            except AssertionError as e:
                failed += 1
                error_msg = f"Scenario '{scenario.name}' failed: {str(e)}"
                errors.append(error_msg)
                log(f"✗ {error_msg}", "error")

            except Exception as e:
                failed += 1
                error_msg = f"Scenario '{scenario.name}' error: {str(e)}"
                errors.append(error_msg)
                log(f"✗ {error_msg}", "error")

        # Use logs_directory for video recording path instead of globbing
        if config.enable_video_recording:
            video_dir = config.resolve_video_recording_dir()
            if video_dir.exists():
                recording_path = str(video_dir)
                log(f"Recording directory: {recording_path}")
            else:
                log("Video recording was enabled but recording directory not found", "warning")

        # Calculate duration
        duration = time.time() - start_time

        # Build summary
        summary = {
            'total_scenarios': total_scenarios,
            'passed': passed,
            'failed': failed
        }

        success = (failed == 0)

        log(f"\n{'='*60}")
        log(f"Execution Summary:")
        log(f"  Total: {total_scenarios}")
        log(f"  Passed: {passed}")
        log(f"  Failed: {failed}")
        log(f"  Duration: {duration:.2f}s")
        log(f"  Status: {'✓ SUCCESS' if success else '✗ FAILED'}")
        log(f"{'='*60}")

        return TestResult(
            success=success,
            summary=summary,
            duration=duration,
            recording_path=recording_path,
            errors=errors
        )

    except Exception as e:
        duration = time.time() - start_time
        error_msg = f"Feature execution failed: {str(e)}"
        log(error_msg, "error")

        import traceback
        traceback_str = traceback.format_exc()
        log(f"Traceback:\n{traceback_str}", "error")

        return TestResult(
            success=False,
            summary={'total_scenarios': 0, 'passed': 0, 'failed': 0},
            duration=duration,
            recording_path=None,
            errors=[error_msg]
        )
