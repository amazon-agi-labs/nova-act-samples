"""Browser hover actuation via prompt steering.

Demonstrates how to steer Nova Act to use `agentHover`, which the SDK
already handles but is not supported by default.

Usage:
python -m examples.actuation.browser.hover
"""

from pathlib import Path

import fire
from nova_act import NovaAct, SecurityOptions, workflow

from examples.nova_act_client import NovaActClient
from examples.utils import get_logger

LOGGER = get_logger(__name__)

# The SDK already handles agentHover; the model just needs the prompt
# context to produce it.
HOVER_STEERING = """
The `agentHover` statement hovers the mouse over the center of the specified box.

Syntax:
agentHover(bbox: string): Hovers on the center of the specified box.

Example:
agentHover(bbox) moves the mouse pointer over the bbox without clicking.

Prompt:
"""

HTML_FILE_PATH = str(Path(__file__).parent / "static" / "hover.html")


def with_hover_steering(prompt: str) -> str:
    """Prepend the hover steering reference to a prompt.

    Args:
        prompt: The user-facing action to perform.

    Returns:
        Combined prompt with hover steering and the requested action.
    """
    return HOVER_STEERING + prompt


@workflow(**NovaActClient.get_workflow_kwargs())
def main() -> None:
    """Run hover actuation example on a local test page."""
    LOGGER.info("🚀 Starting hover actuation example...")

    with NovaAct(
        starting_page=f"file://{HTML_FILE_PATH}",
        ignore_https_errors=True,
        security_options=SecurityOptions(allowed_file_open_paths=[HTML_FILE_PATH]),
    ) as nova:
        nova.act(with_hover_steering("Hover over the Hover Over Me button"))
        LOGGER.info("✓ Hover completed")

    LOGGER.info("✓ Hover actuation test passed")


if __name__ == "__main__":
    fire.Fire(main)
