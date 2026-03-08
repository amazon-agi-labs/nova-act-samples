"""Clipboard Manager with Nova Act.

Demonstrates how to interact with the browser clipboard using Nova Act.
Shows how to grant clipboard permissions and read clipboard content.

Usage:
python -m examples.clipboard_manager.main
"""

import fire
from nova_act import NovaAct, workflow

from examples.nova_act_client import NovaActClient
from examples.utils import get_logger

LOGGER = get_logger(__name__)


@workflow(**NovaActClient.get_workflow_kwargs())
def main() -> None:
    with NovaAct(
        starting_page="https://nova.amazon.com/act?tab=dev_tools",
    ) as nova:
        # Grant clipboard permissions
        # - clipboard-write: allows the website to write to the clipboard
        # - clipboard-read: allows us to read the clipboard content
        nova.page.context.grant_permissions(["clipboard-read", "clipboard-write"])
        # Copy a value
        nova.act("Click the Copy button")
        # Read the value from the clipboard
        clipboard_text = nova.page.evaluate(
            """
            async () => {
                return await navigator.clipboard.readText();
            }
        """
        )
        LOGGER.info(f"Clipboard: {clipboard_text}\n")


if __name__ == "__main__":
    fire.Fire(main)
