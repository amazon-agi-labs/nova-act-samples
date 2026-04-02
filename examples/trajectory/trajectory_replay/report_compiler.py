"""Utilities for generating HTML reports from trajectory replay results."""

import html
import os

from nova_act.types.errors import ValidationFailed
from nova_act.util.logging import setup_logging

from examples.trajectory.trajectory_replay.types import TrajectoryReplayResult
from examples.trajectory.trajectory_replay.validators import (
    StepValidationResult,
    ValidationResult,
)

_LOGGER = setup_logging(__name__)


HTML_TEMPLATE = """<!doctype html>
<html lang="en" style="scroll-behavior: smooth;">
<head>
    <meta http-equiv="Content-Type" content="text/html;charset=UTF-8" />
    <title>NovaAct Trajectory Replay Report</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto',
                         'Oxygen', 'Ubuntu', 'Cantarell', 'Helvetica Neue',
                         sans-serif;
            padding: 2rem 4rem;
            background: #f5f6f7;
            color: #1a1a1a;
            margin: 0;
            font-size: 14px;
        }}
        h1, h2, h3, h4 {{
            color: #333;
            margin: 0;
            padding: 8px 0;
        }}
        pre {{
            background: #f4f4f4;
            padding: 10px;
            border-radius: 5px;
            overflow-x: auto;
            font-size: 14px;
            white-space: pre-wrap;
            word-wrap: break-word;
            margin: 0;
            display: block;
        }}
        .report-header {{
            border: 1px solid #ddd;
            padding: 16px 32px 4px;
            background: white;
        }}
        .report-container {{
            flex-grow: 1;
            overflow: scroll;
            display: flex;
            flex-direction: column;
            gap: 8px;
        }}
        .id-container {{
            display: flex;
            font-size: 14px;
            gap: 16px;
            margin-top: 8px;
        }}
        .summary-container {{
            padding: 16px 0;
            border-top: 1px solid #ddd;
            margin-top: 8px;
        }}
        .summary-stats {{
            display: flex;
            gap: 24px;
            font-size: 14px;
            padding: 8px 0;
        }}
        .status-badge {{
            padding: 4px 12px;
            border-radius: 4px;
            font-weight: bold;
            display: inline-block;
        }}
        .status-badge.passed {{
            background: #4caf50;
            color: white;
        }}
        .status-badge.failed {{
            background: #f44336;
            color: white;
        }}
        .step-container {{
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 16px;
            margin: 8px 16px;
            background: white;
            display: flex;
            flex-direction: column;
            gap: 12px;
        }}
        .image-comparison-grid {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 16px;
        }}
        .image-comparison-grid img {{
            border-radius: 5px;
            object-fit: contain;
            background-color: lightblue;
            width: 100%;
        }}
        .validation-results {{
            display: flex;
            flex-direction: column;
            gap: 12px;
        }}
        .validation-item {{
            border: 1px solid #ddd;
            border-radius: 4px;
            padding: 12px;
        }}
        .validation-item.validation-passed {{
            background: #f0f9f0;
            border-color: #4caf50;
        }}
        .validation-item.validation-failed {{
            background: #fff0f0;
            border-color: #f44336;
        }}
        .validation-header {{
            display: flex;
            align-items: center;
            gap: 8px;
            margin-bottom: 8px;
            font-weight: bold;
        }}
        .status-icon {{
            font-size: 18px;
        }}
        .validation-type {{
            flex-grow: 1;
        }}
        .validation-badge {{
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: bold;
        }}
        .validation-badge.passed {{
            background: #4caf50;
            color: white;
        }}
        .validation-badge.failed {{
            background: #f44336;
            color: white;
        }}
        .validation-details {{
            font-size: 13px;
            line-height: 1.6;
        }}
        .validation-details > div {{
            margin: 4px 0;
        }}
        details {{
            margin-top: 8px;
        }}
        summary {{
            cursor: pointer;
            color: #007bff;
            font-weight: 500;
        }}
        summary:hover {{
            text-decoration: underline;
        }}
        @media (max-width: 767px) {{
            .id-container {{
                flex-direction: column;
                gap: 0;
            }}
            .summary-stats {{
                flex-direction: column;
                gap: 8px;
            }}
            .image-comparison-grid {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="report-header">
        <h2>Amazon Nova Act Trajectory Replay Report</h2>
        <h4>Original Prompt</h4>
        <pre>{prompt}</pre>
        <div class="id-container">
            <div><b>Trajectory File:</b> {trajectory_filename}</div>
            <div><b>SDK Version:</b> {sdk_version}</div>
            <div><b>Replay Time:</b> {replay_timestamp}</div>
            <div><b>Status:</b> {status_badge}</div>
        </div>
        <div class="summary-container">
            <h4>Validation Summary</h4>
            <div class="summary-stats">
                <div><b>Total Steps:</b> {total_steps}</div>
                <div><b>Validations:</b> {passed_validations}/{total_validations} passed ({pass_percentage}%)</div>
            </div>
            <div class="summary-stats">
                <div><b>URL:</b> {url_passed}/{url_total}</div>
                <div><b>Image:</b> {image_passed}/{image_total}</div>
                <div><b>DOM:</b> {dom_passed}/{dom_total}</div>
            </div>
        </div>
    </div>
    <div class="report-container">
        {step_reports}
    </div>
</body>
</html>"""


def _format_validation_result(validation: ValidationResult) -> str:
    """Format a single ValidationResult as HTML."""
    icon = "✓" if validation.passed else "✗"
    css_class = "validation-passed" if validation.passed else "validation-failed"
    badge_class = "passed" if validation.passed else "failed"
    badge_text = "PASSED" if validation.passed else "FAILED"
    type_name = validation.validator_type.upper()

    details_parts = [
        f"<div><b>Expected:</b> {html.escape(_truncate_string(validation.expected, 100))}</div>",
        f"<div><b>Observed:</b> {html.escape(_truncate_string(validation.observed, 100))}</div>",
        f"<div><b>Difference:</b> {validation.difference:.2f}%</div>",
        f"<div><b>Threshold:</b> {validation.threshold:.2f}%</div>",
    ]

    # Add type-specific details
    if validation.validator_type == "url":
        components = validation.details.get("components_checked", "")
        details_parts.append(f"<div><b>Components Checked:</b> {components}</div>")
    elif validation.validator_type == "image":
        bbox = validation.details.get("bounding_box")
        if bbox:
            details_parts.append(f"<div><b>Bounding Box:</b> {bbox}</div>")
        else:
            details_parts.append("<div><b>Bounding Box:</b> None (full image)</div>")

    details_html = "\n".join(details_parts)

    # Add expandable diff for failed validations
    if not validation.passed and len(validation.expected) > 100:
        details_html += f"""
                <details>
                    <summary>Show full expected value</summary>
                    <pre>{html.escape(validation.expected[:1000])}</pre>
                </details>"""
    if not validation.passed and len(validation.observed) > 100:
        details_html += f"""
                <details>
                    <summary>Show full observed value</summary>
                    <pre>{html.escape(validation.observed[:1000])}</pre>
                </details>"""

    return f"""<div class="validation-item {css_class}">
            <div class="validation-header">
                <span class="status-icon">{icon}</span>
                <span class="validation-type">{type_name} Validation</span>
                <span class="validation-badge {badge_class}">{badge_text}</span>
            </div>
            <div class="validation-details">
                {details_html}
            </div>
        </div>"""


def _format_step_validations(
    step_validation: StepValidationResult, expected_image: str, observed_image: str
) -> str:
    """Format validation results for a single step."""
    validation_items = []

    if step_validation.url_validation:
        validation_items.append(
            _format_validation_result(step_validation.url_validation)
        )
    if step_validation.image_validation:
        validation_items.append(
            _format_validation_result(step_validation.image_validation)
        )
    if step_validation.dom_validation:
        validation_items.append(
            _format_validation_result(step_validation.dom_validation)
        )

    # Join validation items with newlines
    validations_html = "\n".join(validation_items)

    passed, total = step_validation.validation_count
    step_status = (
        "✓ All validations passed"
        if step_validation.all_passed
        else f"⚠ {passed}/{total} validations passed"
    )

    return f"""<div class="step-container">
        <h3>Step {step_validation.step_number} - {step_status}</h3>
            <div class="image-comparison-grid">
                <div>
                    <h4>Expected Screenshot</h4>
                    <img src="{expected_image}" alt="Expected screenshot">
                </div>
                <div>
                    <h4>Observed Screenshot</h4>
                    <img src="{observed_image}" alt="Observed screenshot">
                </div>
            </div>
        <div class="validation-results">
            {validations_html}
        </div>
    </div>
"""


def _truncate_string(s: str, max_length: int) -> str:
    """Truncate a string to max_length, adding ellipsis if truncated."""
    if len(s) <= max_length:
        return s
    return s[:max_length] + "..."


def _write_html_file(output_directory: str, filename: str, html_content: str) -> str:
    """Write HTML content to a file."""
    os.makedirs(output_directory, exist_ok=True)
    output_path = os.path.join(output_directory, filename)
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        return output_path
    except OSError as e:
        _LOGGER.warning(f"Failed to write HTML report to {output_path}: {e}")
        return ""


class TrajectoryReportCompiler:
    """Compiler for generating HTML reports from trajectory replay results."""

    def __init__(self, output_directory: str):
        """
        Initialize the compiler.

        Args:
            output_directory: Directory to write report files to.
        """
        self._output_directory = output_directory
        if not self._output_directory:
            raise ValidationFailed(
                f"Invalid output directory: {self._output_directory}"
            )

    def compile(
        self,
        replay_result: TrajectoryReplayResult,
        trajectory_filename: str = "trajectory",
    ) -> str:
        """
        Compile trajectory replay result into an HTML report.

        Args:
            replay_result: The trajectory replay result to compile.
            trajectory_filename: Name of the trajectory file (for display).

        Returns:
            Path to the generated HTML report file.
        """
        # Generate step reports
        step_reports_html = ""
        for i, step_validation in enumerate(replay_result.step_validations):
            # Get expected and observed images from the trajectory steps
            if i < len(replay_result.trajectory.steps):
                expected_image = replay_result.trajectory.steps[i].image
            else:
                expected_image = ""

            # For observed image, use the one from image_validation if available
            if step_validation.image_validation:
                observed_image = step_validation.image_validation.observed
            else:
                observed_image = expected_image  # Fallback to expected if no validation

            step_reports_html += _format_step_validations(
                step_validation, expected_image, observed_image
            )

        # Calculate summary statistics
        passed_validations, total_validations = replay_result.validation_summary
        pass_percentage = (
            (passed_validations / total_validations * 100)
            if total_validations > 0
            else 0.0
        )

        by_type = replay_result.validation_summary_by_type
        url_passed, url_total = by_type.url
        image_passed, image_total = by_type.image
        dom_passed, dom_total = by_type.dom

        # Create status badge
        status_badge_class = "passed" if replay_result.all_passed else "failed"
        status_badge_text = "✓ ALL PASSED" if replay_result.all_passed else "✗ FAILED"
        status_badge = f'<span class="status-badge {status_badge_class}">{status_badge_text}</span>'

        # Generate HTML
        html_content = HTML_TEMPLATE.format(
            prompt=replay_result.trajectory.prompt,
            trajectory_filename=trajectory_filename,
            sdk_version=replay_result.trajectory.sdk_version,
            replay_timestamp=replay_result.replay_timestamp.isoformat(),
            status_badge=status_badge,
            total_steps=len(replay_result.step_validations),
            passed_validations=passed_validations,
            total_validations=total_validations,
            pass_percentage=f"{pass_percentage:.1f}",
            url_passed=url_passed,
            url_total=url_total,
            image_passed=image_passed,
            image_total=image_total,
            dom_passed=dom_passed,
            dom_total=dom_total,
            step_reports=step_reports_html,
        )

        # Write HTML file
        filename = f"trajectory_replay_{replay_result.replay_timestamp.strftime('%Y%m%d_%H%M%S')}.html"
        output_path = _write_html_file(self._output_directory, filename, html_content)

        return output_path
