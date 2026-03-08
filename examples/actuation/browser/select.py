"""Browser native select actuation.

Demonstrates how Nova Act handles native ``<select>`` dropdown elements.
The SDK's ``agent_type`` actuator detects native dropdowns, types the
selected value, and blurs the element. If a click is attempted on a native
dropdown, ``agent_click`` raises an ``AgentRedirectError`` with the
available options and redirects to ``agentType``.

Usage:
python -m examples.actuation.browser.select
"""

from pathlib import Path

import fire
from nova_act import NovaAct, SecurityOptions, workflow

from examples.nova_act_client import NovaActClient
from examples.utils import get_logger

LOGGER = get_logger(__name__)

HTML_FILE_PATH = str(Path(__file__).parent / "static" / "select.html")


@workflow(**NovaActClient.get_workflow_kwargs())
def main() -> None:
    """Run native select actuation examples on a local test page."""
    LOGGER.info("🚀 Starting select actuation example...")

    with NovaAct(
        starting_page=f"file://{HTML_FILE_PATH}",
        ignore_https_errors=True,
        security_options=SecurityOptions(allowed_file_open_paths=[HTML_FILE_PATH]),
    ) as nova:
        # Select a country from the dropdown
        nova.act("Select United States from the Country dropdown")
        LOGGER.info("✓ Country set to United States")

        # Select a size from the dropdown
        nova.act("Select Large from the Size dropdown")
        LOGGER.info("✓ Size set to Large")

    LOGGER.info("✓ All select actuation tests passed")


if __name__ == "__main__":
    fire.Fire(main)
