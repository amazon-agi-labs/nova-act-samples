"""Types for trajectory replay results.

Re-exports TrajectoryStep, TrajectoryMetadata, and Trajectory from the SDK,
and defines additional types used by the trajectory replay module.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import NamedTuple

from nova_act.impl.trajectory.types import (
    Trajectory,
    TrajectoryMetadata,
    TrajectoryStep,
)
from pydantic import BaseModel

from examples.trajectory.trajectory_replay.validators import StepValidationResult

# Re-export SDK types for convenience
__all__ = [
    "Trajectory",
    "TrajectoryMetadata",
    "TrajectoryStep",
    "TrajectoryReplayResult",
    "ValidationSummary",
    "ValidationSummaryByType",
]


class ValidationSummary(NamedTuple):
    """Summary of the validations for a TrajectoryReplay.Result"""

    passed: int
    """Number of validations passed."""
    total: int
    """Total validations run."""


class ValidationSummaryByType(BaseModel):
    """Validation Summaries for each validation type."""

    url: ValidationSummary
    """Summary for the URL validation."""
    image: ValidationSummary
    """Summary for the image validation."""
    dom: ValidationSummary
    """Summary for the DOM validation."""


@dataclass(frozen=True)
class TrajectoryReplayResult:
    """Result of replaying a trajectory with validation results."""

    trajectory: Trajectory
    step_validations: list[StepValidationResult]
    replay_timestamp: datetime
    maybe_error: Exception | None = None

    @property
    def all_passed(self) -> bool:
        return all(step.all_passed for step in self.step_validations)

    @property
    def validation_summary(self) -> ValidationSummary:
        """Get (passed_validations, total_validations) across all steps."""
        passed = sum(
            p for step in self.step_validations for p, _ in [step.validation_count]
        )
        total = sum(
            t for step in self.step_validations for _, t in [step.validation_count]
        )
        return ValidationSummary(passed=passed, total=total)

    @property
    def validation_summary_by_type(self) -> ValidationSummaryByType:
        """Get validation summary by validator type."""
        url_passed = sum(
            1
            for step in self.step_validations
            if step.url_validation and step.url_validation.passed
        )
        url_total = sum(1 for step in self.step_validations if step.url_validation)

        image_passed = sum(
            1
            for step in self.step_validations
            if step.image_validation and step.image_validation.passed
        )
        image_total = sum(1 for step in self.step_validations if step.image_validation)

        dom_passed = sum(
            1
            for step in self.step_validations
            if step.dom_validation and step.dom_validation.passed
        )
        dom_total = sum(1 for step in self.step_validations if step.dom_validation)

        return ValidationSummaryByType(
            url=ValidationSummary(passed=url_passed, total=url_total),
            image=ValidationSummary(passed=image_passed, total=image_total),
            dom=ValidationSummary(passed=dom_passed, total=dom_total),
        )
