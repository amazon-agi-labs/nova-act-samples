"""Browser click actuation via prompt steering.

Demonstrates how to steer Nova Act to use the `clickType` parameter of
`agentClick`, which the SDK already handles but is not supported by default.
Covers single click (no steering needed), double-click, and right-click.

Usage:
python -m examples.actuation.browser.click
"""

from pathlib import Path

import fire
from nova_act import NovaAct, SecurityOptions, workflow

from examples.nova_act_client import NovaActClient
from examples.utils import get_logger

LOGGER = get_logger(__name__)

# The SDK already handles agentClick with clickType options; the model just
# needs the prompt context to produce them.
CLICK_STEERING = """
The `agentClick` statement supports a `clickType` argument to specify the type of click to perform.

Syntax:
agentClick(bbox: string, clickType: string): Clicks the specified box with the given click type.

Available clickType options:
- 'left': Single left click (default)
- 'left-double': Double left click
- 'right': Right click

Example:
agentClick(bbox, 'left-double') performs a double-click on the bbox.

Prompt:
"""

HTML_FILE_PATH = str(Path(__file__).parent / "static" / "click.html")


def with_click_steering(prompt: str) -> str:
    """Prepend the click steering reference to a prompt.

    Args:
        prompt: The user-facing action to perform.

    Returns:
        Combined prompt with click steering and the requested action.
    """
    return CLICK_STEERING + prompt


@workflow(**NovaActClient.get_workflow_kwargs())
def main() -> None:
    """Run click actuation examples on a local test page."""
    LOGGER.info("🚀 Starting click actuation example...")

    with NovaAct(
        starting_page=f"file://{HTML_FILE_PATH}",
        ignore_https_errors=True,
        security_options=SecurityOptions(allowed_file_open_paths=[HTML_FILE_PATH]),
    ) as nova:
        # Single click — works without steering, included as a baseline
        nova.act("Click the Single Click Me button")
        LOGGER.info("✓ Single click completed")

        # Double click — requires steering so the model uses 'left-double'
        nova.act(with_click_steering("Double click the Double Click Me button"))
        LOGGER.info("✓ Double click completed")

        # Right click — requires steering so the model uses 'right'
        nova.act(with_click_steering("Right click the Right Click Me button"))
        LOGGER.info("✓ Right click completed")

    LOGGER.info("✓ All click actuation tests passed")


if __name__ == "__main__":
    fire.Fire(main)
