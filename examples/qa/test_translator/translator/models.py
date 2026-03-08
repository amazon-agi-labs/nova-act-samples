"""Shared data models for QA Test Translator."""

from typing import List, Literal, Optional

from pydantic import BaseModel, model_validator


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


class TestStep(BaseModel):
    """Represents a single Gherkin step.

    Each step must have exactly one of: instruction, extraction, or validation.
    This XOR constraint is enforced by the model_validator.
    """

    original_keyword: str  # "Given", "When", "Then", "And", "But"
    original_text: str  # Original Gherkin step text
    instruction: Optional[str] = None  # Nova Act prompt for act()
    extraction: Optional[Extraction] = (
        None  # Extraction config for act_get() - stores value
    )
    validation: Optional[Validation] = (
        None  # Validation config for act_get() - checks value
    )

    @model_validator(mode="after")
    def check_exactly_one_set(self) -> "TestStep":
        """Ensure exactly one of instruction, extraction, or validation is set (XOR)."""
        has_instruction = self.instruction is not None
        has_extraction = self.extraction is not None
        has_validation = self.validation is not None

        set_count = sum([has_instruction, has_extraction, has_validation])

        if set_count == 0:
            raise ValueError(
                "One of instruction, extraction, or validation must be set"
            )
        if set_count > 1:
            raise ValueError(
                "Cannot set multiple fields - each step should be one action, extraction, or validation"
            )
        return self


class TestScenario(BaseModel):
    """Represents a Gherkin scenario.

    A scenario is a concrete example of how the system should behave,
    consisting of a sequence of steps.
    """

    name: str
    tags: List[str] = []
    steps: List[TestStep]


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
