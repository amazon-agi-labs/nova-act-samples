"""Browser range input actuation.

Demonstrates how Nova Act handles HTML range sliders. The SDK's
``agent_type`` actuator detects ``<input type="range">`` elements and sets
their value programmatically via JavaScript. If a click is attempted on a
range input, ``agent_click`` raises an ``AgentRedirectError`` to redirect
the model to ``agentType`` with the slider's min/max bounds.

Usage:
python -m examples.actuation.browser.range_input
"""

from pathlib import Path

import fire
from nova_act import NovaAct, SecurityOptions, workflow

from examples.nova_act_client import NovaActClient
from examples.utils import get_logger

LOGGER = get_logger(__name__)

HTML_FILE_PATH = str(Path(__file__).parent / "static" / "range_input.html")


@workflow(**NovaActClient.get_workflow_kwargs())
def main() -> None:
    """Run range input actuation examples on a local test page."""
    LOGGER.info("🚀 Starting range input actuation example...")

    with NovaAct(
        starting_page=f"file://{HTML_FILE_PATH}",
        ignore_https_errors=True,
        security_options=SecurityOptions(allowed_file_open_paths=[HTML_FILE_PATH]),
    ) as nova:
        # Set the volume slider to 75 — the actuator detects the range input
        # and sets the value directly instead of simulating a drag.
        nova.act("Set the Volume slider to 75")
        LOGGER.info("✓ Volume slider set to 75")

        # Set the brightness slider to 30
        nova.act("Set the Brightness slider to 30")
        LOGGER.info("✓ Brightness slider set to 30")

    LOGGER.info("✓ All range input actuation tests passed")


if __name__ == "__main__":
    fire.Fire(main)
