"""Shared data models for QA Test Translator."""

import re
from typing import Any, List, Literal, Optional

from pydantic import BaseModel, model_validator

# Pattern for matching ${variable_name} references
_VARIABLE_PATTERN = re.compile(r'\$\{([^}]+)\}')


class Extraction(BaseModel):
    """Extraction configuration for a test step.

    Used when a step needs to extract data from the UI using
    ``NovaActQa.expect().as_*()`` methods and store it for later use
    in subsequent steps.
    """

    prompt: str  # NovaActQa prompt for extraction
    extraction_key: (
        str  # Variable name to store extracted value (e.g., "order_id", "user_email")
    )
    extraction_type: Literal[
        "string",
        "number",
        "boolean",
    ] = "string"  # Type of value to extract


class Validation(BaseModel):
    """Validation configuration for a test step.

    Used when a step needs to extract data from the UI and compare it against
    an expected value using ``NovaActQa.expect().to_*()`` assertions.
    """

    prompt: str  # NovaActQa prompt for extraction
    expected: str | float | bool | None = (
        None  # Expected value (not needed for true/false)
    )
    comparison: Literal[
        # String comparisons
        "equal",
        "contain",
        "match",  # regex pattern
        # Number comparisons
        "greater_than",
        "less_than",
        "greater_or_equal",
        "less_or_equal",
        # Boolean comparisons
        "true",
        "false",
    ]


class FunctionCall(BaseModel):
    """Function call configuration for a test step.

    Used when a step needs to call a custom Python function.
    """

    function_name: str  # Name of function to call (e.g., "calculate_discount" or "user_service.create_user")
    parameters: dict[str, Any] = {}  # Function parameters as key-value pairs
    storage_key: Optional[str] = None  # Variable name to store result (if specified)


class TestStep(BaseModel):
    """Represents a single Gherkin step.

    Each step must have exactly one of: instruction, extraction, validation, or function_call.
    This XOR constraint is enforced by the model_validator.
    """

    original_keyword: str  # "Given", "When", "Then", "And", "But"
    original_text: str  # Original Gherkin step text
    instruction: Optional[str] = None  # Nova Act prompt for act()
    extraction: Optional[Extraction] = None  # Extraction config for act_get() - stores value
    validation: Optional[Validation] = None  # Validation config for act_get() - checks value
    function_call: Optional[FunctionCall] = None  # Function call config for custom functions

    @model_validator(mode="after")
    def check_exactly_one_set(self) -> "TestStep":
        """Ensure exactly one of instruction, extraction, validation, or function_call is set (XOR)."""
        has_instruction = self.instruction is not None
        has_extraction = self.extraction is not None
        has_validation = self.validation is not None
        has_function_call = self.function_call is not None

        set_count = sum([has_instruction, has_extraction, has_validation, has_function_call])

        if set_count == 0:
            raise ValueError("One of instruction, extraction, validation, or function_call must be set")
        if set_count > 1:
            raise ValueError("Cannot set multiple fields - each step should be one action, extraction, validation, or function call")
        return self


class TestScenario(BaseModel):
    """Represents a Gherkin scenario.

    A scenario is a concrete example of how the system should behave,
    consisting of a sequence of steps.
    """

    name: str
    tags: List[str] = []
    steps: List[TestStep]

    @model_validator(mode="after")
    def validate_variable_references(self) -> "TestScenario":
        """Validate that all ${variable_name} references point to variables
        defined by extraction or function call steps earlier in the scenario.

        Variables are registered after validation so a step cannot reference
        its own extraction key (fixes #12).
        """
        defined_variables: set[str] = set()

        for step_idx, step in enumerate(self.steps, 1):
            # Collect all text fields that may contain variable references
            texts_to_check: list[str] = []

            if step.instruction:
                texts_to_check.append(step.instruction)
            if step.extraction:
                texts_to_check.append(step.extraction.prompt)
            if step.validation:
                texts_to_check.append(step.validation.prompt)
                if isinstance(step.validation.expected, str):
                    texts_to_check.append(step.validation.expected)
            if step.function_call:
                for param_value in step.function_call.parameters.values():
                    if isinstance(param_value, str):
                        texts_to_check.append(param_value)

            # Validate references BEFORE registering this step's key (#12 fix)
            for text in texts_to_check:
                for match in _VARIABLE_PATTERN.finditer(text):
                    var_name = match.group(1)
                    if var_name not in defined_variables:
                        raise ValueError(
                            f"Undefined variable reference '${{{var_name}}}' in step {step_idx}: "
                            f"'{step.original_text}'. Variable must be extracted in an earlier step."
                        )

            # Register variables defined by this step (after validation)
            if step.extraction:
                defined_variables.add(step.extraction.extraction_key)
            if step.function_call and step.function_call.storage_key:
                defined_variables.add(step.function_call.storage_key)

        return self


class Feature(BaseModel):
    """Represents a Gherkin feature.

    A feature is a high-level description of a software feature and
    contains one or more scenarios that test that feature.
    """

    name: str
    description: str
    base_url: str  # Derived from tags using env var mapping
    tags: List[str] = []
    scenarios: List[TestScenario]

    # Metadata fields
    conversion_timestamp: str  # ISO 8601 timestamp of when conversion occurred
    source_file: str  # Original .feature filename
    bedrock_model_id: str  # Bedrock model used for conversion
