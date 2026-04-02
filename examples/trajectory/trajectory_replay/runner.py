"""Trajectory loading, replay, and validation utilities."""

import glob
import os
from datetime import datetime
from typing import cast

from nova_act import NovaAct
from nova_act.__version__ import VERSION
from nova_act.impl.program.runner import ProgramRunner
from nova_act.tools.actuator.interface.actuator import ActionType, ActuatorBase
from nova_act.tools.browser.default.default_nova_local_browser_actuator import (
    DefaultNovaLocalBrowserActuator,
)
from nova_act.tools.browser.interface.browser import (
    BrowserActuatorBase,
    BrowserObservation,
)
from nova_act.tools.human.interface.human_input_callback import (
    DefaultHumanInputCallbacks,
    HumanInputCallbacksBase,
)
from nova_act.types.errors import InvalidTrajectoryReplay
from nova_act.util.event_handler import EventHandler
from nova_act.util.logging import make_trace_logger, trace_log_lines

from examples.trajectory.trajectory_replay.report_compiler import (
    TrajectoryReportCompiler,
)
from examples.trajectory.trajectory_replay.types import (
    Trajectory,
    TrajectoryReplayResult,
)
from examples.trajectory.trajectory_replay.validators import (
    DefaultDOMValidator,
    DefaultImageValidator,
    DefaultUrlValidator,
    StepValidationResult,
    ValidatorBase,
)
from examples.utils import get_logger

logger = get_logger(__name__)

_TRACE_LOGGER = make_trace_logger()


class TrajectoryRunner:
    """Replays a serialized Trajectory in a browser session with validation.

    Executes each step from a previously recorded trajectory, validating the browser
    state (URL, screenshot, DOM) against the original at each step. Produces a
    TrajectoryReplayResult containing per-step validation outcomes.
    """

    def __init__(
        self,
        actuator: ActuatorBase,
        human_input_callbacks: HumanInputCallbacksBase,
        tools: list[ActionType],
        event_handler: EventHandler,
        strict_sdk_version: bool = False,
        strict_validators: bool = True,
        url_validator: ValidatorBase | None = None,
        screenshot_validator: ValidatorBase | None = None,
        dom_validator: ValidatorBase | None = None,
        wait_before_replay_ms: float = 0.0,
    ):
        """Initialize the TrajectoryRunner.

        Args:
            actuator: The browser actuator to execute actions. Must be a BrowserActuatorBase.
            human_input_callbacks: Callbacks for handling human input prompts during replay.
            tools: List of available tool actions for program execution.
            event_handler: Handler for emitting events during replay.
            strict_sdk_version: If True, raises an error when the trajectory's SDK version
                differs from the current version. If False, logs a warning. Defaults to False.
            strict_validators: If True, validation failures raise errors. If False, they log
                warnings. Defaults to True.
            url_validator: Custom URL validator. Uses DefaultUrlValidator if None.
            screenshot_validator: Custom screenshot validator. Uses DefaultImageValidator if None.
            dom_validator: Custom DOM validator. Uses DefaultDOMValidator if None.
            wait_before_replay_ms: Milliseconds to wait after page load before taking the first
                observation. Useful for pages with slow client-side rendering. Defaults to 0.0.
        """
        if not isinstance(actuator, BrowserActuatorBase):
            raise ValueError(
                "Trajectory Replay currently only supports BrowserActuatorBase"
            )
        else:
            self._actuator = actuator
        self.strict_sdk_version = strict_sdk_version
        self._wait_before_replay_ms = wait_before_replay_ms

        if not isinstance(actuator, DefaultNovaLocalBrowserActuator):
            _TRACE_LOGGER.warning(
                "Detected Trajectory Replay request with custom actuator. "
                "Trajectory replaying does not support validating the consistency of actions passed; "
                "To ensure consistency, make sure your implementation matches the one used to generate "
                "and serialize the trajectory."
            )
        if not isinstance(human_input_callbacks, DefaultHumanInputCallbacks):
            _TRACE_LOGGER.warning(
                "Detected a Trajectory Replay request with custom human callbacks. "
                "Trajectory replaying does not support validating the consistency of callbacks passed; "
                "To ensure consistency, make sure your implementation matches the one used to generate "
                "and serialize the trajectory."
            )

        if len(tools) > len(actuator.list_actions() + human_input_callbacks.as_tools()):
            _TRACE_LOGGER.warning(
                "Detected a Trajectory Replay request with custom tools. "
                "Trajectory Replaying does not support validating the consistency of tools passed; "
                "To ensure consistency, make sure your implementation matches the one used to generate "
                "and serialize the trajectory."
            )

        self.program_runner = ProgramRunner(event_handler, verbose=True)
        self.tool_map = {tool.tool_name: tool for tool in tools}
        self.url_validator = url_validator or DefaultUrlValidator(
            strict=strict_validators
        )
        self.screenshot_validator = screenshot_validator or DefaultImageValidator(
            strict=strict_validators
        )
        self.dom_validator = dom_validator or DefaultDOMValidator(
            strict=strict_validators
        )

    def run(self, trajectory: Trajectory) -> TrajectoryReplayResult:
        """Replay a trajectory and collect validation results.

        Iterates through each step in the trajectory, validates the current browser
        state against the recorded state, then executes the step's program. Validation
        covers URL, screenshot, and DOM comparisons.

        Args:
            trajectory: The Trajectory to replay.

        Returns:
            A TrajectoryReplayResult with per-step validation outcomes and any error.
        """
        # Warn for SDK version mismatch
        if trajectory.sdk_version != VERSION:
            msg = (
                f"Trajectory serialized with SDK version {trajectory.sdk_version}, "
                f"but re-running with SDK version {VERSION}."
            )
            if self.strict_sdk_version:
                raise InvalidTrajectoryReplay(msg)
            else:
                _TRACE_LOGGER.warning(msg)

        validation_results: list[StepValidationResult] = []
        maybe_error: Exception | None = None

        try:
            # Wait for the page to fully load before taking the first observation.
            if (
                isinstance(self._actuator, DefaultNovaLocalBrowserActuator)
                and self._wait_before_replay_ms > 0
            ):
                self._actuator.get_page().wait_for_timeout(self._wait_before_replay_ms)

            last_observation: BrowserObservation | None = (
                self._actuator.take_observation()
            )

            for step_idx, step in enumerate(trajectory.steps):
                if not step.simplified_dom:
                    raise InvalidTrajectoryReplay(
                        "No DOM collected in trajectory. Regenerate the trajectory with replayable=True."
                    )

                step_validation = StepValidationResult(step_number=step_idx + 1)

                if last_observation:
                    # Validate URL
                    url_result = self.url_validator.validate(
                        step.active_url, last_observation["activeURL"]
                    )
                    step_validation = StepValidationResult(
                        step_number=step_idx + 1,
                        url_validation=url_result,
                    )

                    # Log active URL
                    trace_log_lines(
                        f"Current page: {last_observation['activeURL']}\n============"
                    )

                    # Validate screenshot
                    image_result = self.screenshot_validator.validate(
                        step.image, last_observation["screenshotBase64"]
                    )
                    step_validation = StepValidationResult(
                        step_number=step_idx + 1,
                        url_validation=url_result,
                        image_validation=image_result,
                    )

                    # Validate DOM
                    dom_result = self.dom_validator.validate(
                        step.simplified_dom, last_observation["simplifiedDOM"]
                    )
                    step_validation = StepValidationResult(
                        step_number=step_idx + 1,
                        url_validation=url_result,
                        image_validation=image_result,
                        dom_validation=dom_result,
                    )
                    validation_results.append(step_validation)

                    # raise if necessary
                    self.url_validator.handle_result(url_result)
                    self.screenshot_validator.handle_result(image_result)
                    self.dom_validator.handle_result(dom_result)

                # Run the step's Program
                executable = step.program.compile(self.tool_map)
                program_result = self.program_runner.run(executable)

                # Check for exit
                if exception_result := program_result.has_exception():
                    assert exception_result.error is not None
                    raise exception_result.error
                elif program_result.has_return():
                    break

                # Save next observation
                if observation_result := program_result.has_observation():
                    assert observation_result.return_value is not None
                    last_observation = cast(
                        BrowserObservation, observation_result.return_value
                    )
                else:
                    last_observation = None

                # Emit a break between steps
                trace_log_lines("")
        except Exception as e:
            maybe_error = e

        return TrajectoryReplayResult(
            trajectory=trajectory,
            step_validations=validation_results,
            replay_timestamp=datetime.now(),
            maybe_error=maybe_error,
        )


def load_trajectory(path: str) -> Trajectory:
    """Load a Trajectory from a JSON file path.

    Args:
        path: Path to a trajectory JSON file.

    Returns:
        Deserialized Trajectory.
    """
    with open(path) as f:
        return Trajectory.model_validate_json(f.read())


def load_trajectories(directory: str) -> list[Trajectory]:
    """Load all trajectory JSON files from a directory, sorted by start time.

    Args:
        directory: Directory containing trajectory JSON files.

    Returns:
        List of Trajectories sorted by start time.

    Raises:
        FileNotFoundError: If no trajectory files are found.
    """
    pattern = os.path.join(directory, "act_*_trajectory.json")
    files = glob.glob(pattern)
    if not files:
        raise FileNotFoundError(f"No trajectory files found in {directory}")
    trajectories = [load_trajectory(f) for f in files]
    trajectories.sort(key=lambda t: (t.metadata.start_time or 0) if t.metadata else 0)
    return trajectories


def replay_trajectory(
    nova: NovaAct,
    trajectory: Trajectory,
    strict: bool = True,
    url_validator: ValidatorBase | None = None,
    screenshot_validator: ValidatorBase | None = None,
    dom_validator: ValidatorBase | None = None,
) -> None:
    """Replay a serialized Trajectory with validation.

    Args:
        nova: An active NovaAct session to replay the trajectory in.
        trajectory: The Trajectory to replay.
        strict: If True (default), validation failures raise errors. If False, they log warnings.
        url_validator: Custom URL validator. Uses default if None.
        screenshot_validator: Custom screenshot validator. Uses default if None.
        dom_validator: Custom DOM validator. Uses default if None.
    """
    runner = TrajectoryRunner(
        actuator=nova._actuator,
        human_input_callbacks=nova._human_input_callbacks,
        tools=nova._client_tools,
        event_handler=nova._event_handler,
        strict_validators=strict,
        url_validator=url_validator,
        screenshot_validator=screenshot_validator,
        dom_validator=dom_validator,
        wait_before_replay_ms=5000.0,
    )
    try:
        replay_result = runner.run(trajectory)
        if replay_result.maybe_error is not None:
            raise replay_result.maybe_error
    finally:
        report_path = TrajectoryReportCompiler(nova._session_logs_directory).compile(
            replay_result
        )
        logger.info(f"View your trajectory replay here: {report_path}")
