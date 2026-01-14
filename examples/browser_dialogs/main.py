"""Browser Dialogs example.

Demonstrates handling browser dialogs with Nova Act. The UI (ui/dialogs.html)
has buttons that trigger dialogs for game setup:

1. Enter Name button -> prompt() - collects player name input
2. Set Difficulty button -> confirm() - selects difficulty (OK=Hard, Cancel=Easy)
3. Start New Game button -> alert() - displays game start confirmation (enabled after steps 1 & 2)

Usage:
python -m examples.browser_dialogs.main
"""

import os
from nova_act import NovaAct, SecurityOptions, workflow
from playwright.sync_api import Dialog
from examples.utils import get_workflow_kwargs, get_logger


LOGGER = get_logger(__name__)


def handle_dialog(dialog: Dialog):
    """Handle all dialog types based on dialog.type."""
    LOGGER.info(f"\n\n{dialog.type.capitalize()} dialog triggered with message: {dialog.message}\n\n")

    if dialog.type == "prompt":
        dialog.accept("Nova Act")
    elif dialog.type == "confirm":
        dialog.accept()
    elif dialog.type == "alert":
        dialog.dismiss()


@workflow(**get_workflow_kwargs())
def main() -> None:
    """Run Nova Act on a website that uses browser native dialogs."""

    HTML_FILE_DIR = os.path.join(os.path.dirname(__file__), "ui", "dialogs.html")

    with NovaAct(
        starting_page=f"file://{HTML_FILE_DIR}",
        ignore_https_errors=True,
        security_options=SecurityOptions(allowed_file_open_paths=[HTML_FILE_DIR]),
    ) as nova:
        # Register dialog handler
        nova.page.on("dialog", handle_dialog)

        # Click buttons to set up the game
        nova.act("Click the Enter Name button")
        nova.act("Click the Set Difficulty button")
        nova.act("Click the Start New Game button")

        # Unregister dialog handler
        nova.page.remove_listener("dialog", handle_dialog)

        result = nova.act_get("Return the Player and Difficulty")
        LOGGER.info(f"Game setup complete with: {result.parsed_response}")

if __name__ == "__main__":
    main()
