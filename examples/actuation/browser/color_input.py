"""Browser color input actuation.

Demonstrates how Nova Act handles HTML color pickers. The SDK's
``agent_type`` actuator detects ``<input type="color">`` elements and sets
their value directly via JavaScript. If a click is attempted on a color
input, ``agent_click`` raises an ``AgentRedirectError`` to redirect the
model to ``agentType`` with a ``#RRGGBB`` format hint.

Usage:
python -m examples.actuation.browser.color_input
"""

from pathlib import Path

import fire
from nova_act import NovaAct, SecurityOptions, workflow

from examples.nova_act_client import NovaActClient
from examples.utils import get_logger

LOGGER = get_logger(__name__)

HTML_FILE_PATH = str(Path(__file__).parent / "static" / "color_input.html")


@workflow(**NovaActClient.get_workflow_kwargs())
def main() -> None:
    """Run color input actuation examples on a local test page."""
    LOGGER.info("🚀 Starting color input actuation example...")

    with NovaAct(
        starting_page=f"file://{HTML_FILE_PATH}",
        ignore_https_errors=True,
        security_options=SecurityOptions(allowed_file_open_paths=[HTML_FILE_PATH]),
    ) as nova:
        # Set the background color picker
        nova.act("Set the Background Color to #491782")
        LOGGER.info("✓ Background color set to #491782")

        # Set the text color picker
        nova.act("Set the Text Color to #c300e0")
        LOGGER.info("✓ Text color set to #c300e0")

    LOGGER.info("✓ All color input actuation tests passed")


if __name__ == "__main__":
    fire.Fire(main)
