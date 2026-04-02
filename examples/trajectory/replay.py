"""Replay a saved trajectory with validation.

Loads a trajectory JSON file (produced by save.py or any run with replayable=True)
and replays it in a new browser session, validating the browser state at each step
against the original trajectory (URL, screenshot, DOM).

Usage:
python -m examples.trajectory.replay --trajectory_file=path/to/trajectory.json
"""

import fire
from nova_act import NovaAct, workflow

from examples.nova_act_client import NovaActClient
from examples.trajectory.trajectory_replay.runner import (
    load_trajectory,
    replay_trajectory,
)
from examples.utils import get_logger

LOGGER = get_logger(__name__)


@workflow(**NovaActClient.get_workflow_kwargs())
def main(trajectory_file: str, strict: bool = True) -> None:
    """Replay a trajectory from a JSON file.

    Args:
        trajectory_file: Path to trajectory JSON file.
        strict: If True (default), validation failures raise errors. If False, they log warnings.
    """
    trajectory = load_trajectory(trajectory_file)

    LOGGER.info(
        f"Loaded trajectory: prompt='{trajectory.prompt}', "
        f"steps={len(trajectory.steps)}, sdk_version={trajectory.sdk_version}"
    )

    page = trajectory.steps[0].active_url
    LOGGER.info(f"Starting replay from: {page}")

    with NovaAct(starting_page=page, replayable=True) as nova:
        replay_trajectory(nova, trajectory, strict=strict)

    LOGGER.info("Trajectory replay completed successfully")


if __name__ == "__main__":
    fire.Fire(main)
