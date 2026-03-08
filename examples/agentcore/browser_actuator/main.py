"""AgentCoreBrowserActuator usage example.

See acbt_actuator.py for the actuator implementation.

Usage:
python -m examples.agentcore.browser_actuator.main
"""

import fire
from nova_act import NovaAct, workflow

from examples.agentcore.browser_actuator.acbt_actuator import (
    AgentCoreBrowserActuator,
)
from examples.nova_act_client import NovaActClient
from examples.utils import get_logger

LOGGER = get_logger(__name__)


@workflow(**NovaActClient.get_workflow_kwargs())
def main() -> None:
    """Run a Nova Act workflow using a custom AgentCore Browser Tool actuator."""
    LOGGER.info("🚀 Starting custom actuator example...")

    with NovaAct(
        actuator=AgentCoreBrowserActuator,
        starting_page="https://nova.amazon.com/act/gym/next-dot/destination/proxima-b",
    ) as nova:
        nova.act_get("Return the gravity of the planet")


if __name__ == "__main__":
    fire.Fire(main)
