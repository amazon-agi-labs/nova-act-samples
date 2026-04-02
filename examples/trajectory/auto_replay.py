"""Save and replay trajectories using a NovaAct subclass.

ReplayableNovaAct overrides act() to save each trajectory to a trajectories/
directory on first run, and replay from the saved file on subsequent runs.

Usage:
python -m examples.trajectory.auto_replay
"""

import glob
import shutil
from pathlib import Path

import fire
from nova_act import ActResult, NovaAct, workflow

from examples.nova_act_client import NovaActClient
from examples.trajectory.trajectory_replay.runner import (
    load_trajectory,
    replay_trajectory,
)
from examples.utils import get_logger

LOGGER = get_logger(__name__)

TRAJECTORY_DIR = Path(__file__).parent / "trajectories"


class ReplayableNovaAct(NovaAct):
    """NovaAct subclass that automatically saves and replays trajectories.

    On first call to act() with a given prompt, runs the act normally and copies
    the trajectory to a stable trajectories/ directory. On subsequent calls,
    replays the saved trajectory instead.
    """

    def __init__(self, *args, strict: bool = True, **kwargs):
        kwargs["replayable"] = True
        super().__init__(*args, **kwargs)
        self._strict = strict
        self._act_index = 0
        TRAJECTORY_DIR.mkdir(parents=True, exist_ok=True)

    def act(self, prompt: str, **kwargs) -> ActResult | None:
        """Run an act or replay from a saved trajectory.

        On first run, executes the act and saves the trajectory file. On subsequent
        runs, detects the saved file and replays it with validation.

        Args:
            prompt: The natural language instruction for the act.
            **kwargs: Additional keyword arguments passed to NovaAct.act().

        Returns:
            ActResult on first run, None during replay.
        """
        pattern = str(TRAJECTORY_DIR / f"{self._act_index:03d}_*.json")
        matches = glob.glob(pattern)
        self._act_index += 1

        if matches:
            LOGGER.info(f"Replaying trajectory: {Path(matches[0]).name}")
            trajectory = load_trajectory(matches[0])
            replay_trajectory(self, trajectory, strict=self._strict)
            return None

        LOGGER.info(f"Running act: {prompt}")
        result = super().act(prompt, **kwargs)

        trajectory_path = result.trajectory_file_path
        if trajectory_path:
            filename = f"{self._act_index - 1:03d}_{Path(trajectory_path).name}"
            shutil.copy2(trajectory_path, TRAJECTORY_DIR / filename)
            LOGGER.info(f"Saved trajectory: {filename}")
        else:
            LOGGER.warning(f"No trajectory file for act: {prompt}")

        return result


@workflow(**NovaActClient.get_workflow_kwargs())
def main(strict: bool = True) -> None:
    """Run a multi-act workflow with automatic trajectory save and replay.

    Args:
        strict: If True (default), validation failures raise errors during replay.
    """
    with ReplayableNovaAct(
        starting_page="https://nova.amazon.com/act/gym/next-dot",
        strict=strict,
    ) as nova:
        nova.act("Go to the Destinations page")
        nova.act("View the details of the first destination")


if __name__ == "__main__":
    fire.Fire(main)
