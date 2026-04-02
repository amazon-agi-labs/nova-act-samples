from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from difflib import SequenceMatcher
from typing import Literal
from urllib.parse import urlparse

from pydantic import BaseModel, Field

from nova_act.tools.browser.default.util.image_helpers import compare_images, crop_image_with_box_to_data_url
from nova_act.types.api.step import BboxTLBR
from nova_act.types.errors import InvalidTrajectoryReplay
from nova_act.util.logging import make_trace_logger

_TRACE_LOGGER = make_trace_logger()


UrlComponent = Literal["scheme", "netloc", "path", "params", "query", "fragment"]
ValidatorType = Literal["url", "image", "dom"]


class ValidationResult(BaseModel):
    """Result of a validation comparison during trajectory replay."""

    validator_type: ValidatorType
    passed: bool
    expected: str
    observed: str
    difference: float  # Percentage difference (0.0 - 100.0)
    threshold: float  # Percentage threshold (0.0 - 100.0)
    details: dict[str, str | float | None] = Field(default_factory=dict)

    @property
    def status(self) -> Literal["passed", "failed"]:
        """Get status as a string."""
        return "passed" if self.passed else "failed"


class StepValidationResult(BaseModel):
    """Aggregated validation results for a single trajectory step."""

    step_number: int
    url_validation: ValidationResult | None = None
    image_validation: ValidationResult | None = None
    dom_validation: ValidationResult | None = None

    @property
    def all_passed(self) -> bool:
        """Check if all validations passed."""
        validations = [self.url_validation, self.image_validation, self.dom_validation]
        return all(v.passed for v in validations if v is not None)

    @property
    def validation_count(self) -> tuple[int, int]:
        """Get (passed_count, total_count) for this step."""
        validations = [self.url_validation, self.image_validation, self.dom_validation]
        nonnull_validations = [v for v in validations if v is not None]
        passed = sum(1 for v in nonnull_validations if v.passed)
        return passed, len(nonnull_validations)


@dataclass(frozen=True)
class PermissiveEqualsMixin:
    tolerance: float = 0.1

    def calculate_string_difference(self, reference: str, observed: str) -> float:
        """Calculate percentage difference between two strings."""
        if len(reference) == len(observed) == 0:
            return 0.0
        matcher = SequenceMatcher(None, reference, observed)
        opcodes = matcher.get_opcodes()
        distance = sum(len(range(op[1], op[2])) - len(range(op[3], op[4])) for op in opcodes if op[0] != "equal")
        max_length = max(len(reference), len(observed))
        return abs(distance / max_length)

    def equals(self, reference: str, observed: str) -> bool:
        """Determine if difference between two strings is within tolerance."""
        return self.calculate_string_difference(reference, observed) <= self.tolerance


@dataclass(frozen=True)
class ValidatorBase(ABC):
    strict: bool = True

    def warn_or_raise(self, msg: str) -> None:
        """Warn or raise."""
        if self.strict:
            raise InvalidTrajectoryReplay(msg)
        else:
            _TRACE_LOGGER.warning(msg)

    @abstractmethod
    def validate(self, reference: str, observed: str) -> ValidationResult:
        """Validate and return a ValidationResult."""

    @abstractmethod
    def handle_result(self, validation_result: ValidationResult) -> None:
        """Warn or raise on a Validation if necessary."""


@dataclass(frozen=True)
class DefaultUrlValidator(PermissiveEqualsMixin, ValidatorBase):
    """Default Validator for Active URL comparison."""

    tolerance: float = 0.0  # override superclass default value
    components: list[UrlComponent] = field(default_factory=lambda: ["scheme", "netloc", "path"])

    def __post_init__(self) -> None:
        if not isinstance(self.components, list):
            raise TypeError(f"'components' must be a list; got type {type(self.components).__name__}")

        allowed_components = UrlComponent.__args__  # type: ignore[attr-defined]

        for component in self.components:
            if component not in allowed_components:
                raise TypeError(f"{component} is not a valid component; choose from {allowed_components}")

    def validate(self, reference: str, observed: str) -> ValidationResult:
        """Validate two URLs and return ValidationResult."""
        parsed_reference = urlparse(reference)
        parsed_observed = urlparse(observed)

        # Calculate max difference across all components
        max_difference = 0.0
        component_diffs: dict[str, float] = {}

        for component in self.components:
            ref_component = getattr(parsed_reference, component)
            obs_component = getattr(parsed_observed, component)
            diff = self.calculate_string_difference(ref_component, obs_component)
            component_diffs[component] = diff
            max_difference = max(max_difference, diff)

        passed = max_difference <= self.tolerance

        return ValidationResult(
            validator_type="url",
            passed=passed,
            expected=reference,
            observed=observed,
            difference=max_difference * 100,  # Convert to percentage
            threshold=self.tolerance * 100,  # Convert to percentage
            details={
                "components_checked": ",".join(self.components),
                **{f"component_{comp}_diff": diff * 100 for comp, diff in component_diffs.items()},
            },
        )

    def handle_result(self, result: ValidationResult) -> None:
        """Compare two URLs."""
        if not result.passed:
            self.warn_or_raise(
                f"Detected reference URL mismatch; component differs by more than "
                f"{result.threshold: .1f}%. Expected: {result.expected}, got: {result.observed}."
            )


@dataclass(frozen=True)
class DefaultImageValidator(PermissiveEqualsMixin, ValidatorBase):
    """Default Validator for Screenshot comparison."""

    target_boundary: BboxTLBR | None = None

    @property
    def bounding_box(self) -> str | None:
        """Get bounding box as a string."""
        if not self.target_boundary:
            return None
        b = self.target_boundary
        return f"<box>{b.top},{b.left},{b.bottom},{b.right}</box>"

    def validate(self, reference: str, observed: str) -> ValidationResult:
        """Validate two images and return ValidationResult."""
        if self.bounding_box:
            cropped_reference = crop_image_with_box_to_data_url(image_data=reference, box_string=self.bounding_box)
            cropped_observed = crop_image_with_box_to_data_url(image_data=observed, box_string=self.bounding_box)
        else:
            cropped_reference, cropped_observed = reference, observed

        percent_diff = compare_images(cropped_reference, cropped_observed)
        percent_tolerance = 100 * self.tolerance  # compare_images returns percent, not decimal
        passed = percent_diff <= percent_tolerance

        details: dict[str, str | float | None] = {}
        if self.bounding_box:
            details["bounding_box"] = self.bounding_box
        else:
            details["bounding_box"] = None

        return ValidationResult(
            validator_type="image",
            passed=passed,
            expected=reference,
            observed=observed,
            difference=percent_diff,
            threshold=percent_tolerance,
            details=details,
        )

    def handle_result(self, result: ValidationResult) -> None:
        """Compare two [cropped] base64-encoded images."""
        if not result.passed:
            self.warn_or_raise(
                f"Detected reference image mismatch; calculated diff {result.difference: .1f}% "
                f"exceeds threshold {result.threshold: .1f}%"
            )


@dataclass(frozen=True)
class DefaultDOMValidator(PermissiveEqualsMixin, ValidatorBase):
    """Default validator for Simplified DOM comparison."""

    def validate(self, reference: str, observed: str) -> ValidationResult:
        """Validate two simplified DOMs and return ValidationResult."""
        difference = self.calculate_string_difference(reference, observed)
        passed = difference <= self.tolerance

        return ValidationResult(
            validator_type="dom",
            passed=passed,
            expected=reference,
            observed=observed,
            difference=difference * 100,  # Convert to percentage
            threshold=self.tolerance * 100,  # Convert to percentage
            details={},
        )

    def handle_result(self, result: ValidationResult) -> None:
        """Compare two simplified DOMs."""
        if not result.passed:
            self.warn_or_raise(
                "Detected reference DOM mismatch; observed differs from reference "
                f"by more than {result.threshold: .1f}%."
            )
