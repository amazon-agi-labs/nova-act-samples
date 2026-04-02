"""Save a trajectory from an act execution.

Runs a workflow with replayable=True and prints the trajectory file path.
The output can be replayed using the replay example.

Usage:
python -m examples.trajectory.save
"""

from pathlib import Path

import fire
from nova_act import NovaAct, workflow

from examples.nova_act_client import NovaActClient
from examples.utils import get_logger

LOGGER = get_logger(__name__)

_DEFAULT_LOGS_DIR = str(Path(__file__).parent / "logs")


@workflow(**NovaActClient.get_workflow_kwargs())
def main(logs_directory: str = _DEFAULT_LOGS_DIR) -> None:
    """Run an act and print the trajectory file path.

    Args:
        logs_directory: Directory to write session logs and trajectory files to.
            Defaults to a logs/ directory alongside this script.
    """
    Path(logs_directory).mkdir(parents=True, exist_ok=True)
    with NovaAct(
        starting_page="https://nova.amazon.com/act/gym/next-dot",
        replayable=True,
        logs_directory=logs_directory,
    ) as nova:
        result = nova.act("Go to the Destinations page")
        LOGGER.info(f"Trajectory saved to: {result.trajectory_file_path}")


if __name__ == "__main__":
    fire.Fire(main)
