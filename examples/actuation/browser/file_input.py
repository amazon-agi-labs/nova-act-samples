"""Browser file input actuation.

Demonstrates how Nova Act handles ``<input type="file">`` elements. The
SDK's ``agent_type`` actuator detects file inputs and uses Playwright's
``set_input_files`` to upload the file. If a click is attempted on a file
input, ``agent_click`` detects the file chooser dialog and raises an
``AgentRedirectError`` to redirect the model to ``agentType``.

File uploads require configuring ``SecurityOptions`` with
``allowed_file_upload_paths`` to allowlist which paths the SDK can access.

Usage:
python -m examples.actuation.browser.file_input
"""

from pathlib import Path

import fire
from nova_act import NovaAct, SecurityOptions, workflow

from examples.nova_act_client import NovaActClient
from examples.utils import get_logger

LOGGER = get_logger(__name__)

STATIC_DIR = Path(__file__).parent / "static"
HTML_FILE_PATH = str(STATIC_DIR / "file_input.html")
UPLOAD_FILE_PATH = str(STATIC_DIR / "file.txt")


@workflow(**NovaActClient.get_workflow_kwargs())
def main() -> None:
    """Run file input actuation example on a local test page."""
    LOGGER.info("🚀 Starting file input actuation example...")

    with NovaAct(
        starting_page=f"file://{HTML_FILE_PATH}",
        ignore_https_errors=True,
        security_options=SecurityOptions(
            allowed_file_open_paths=[HTML_FILE_PATH],
            allowed_file_upload_paths=[UPLOAD_FILE_PATH],
        ),
    ) as nova:
        nova.act(f"Upload the file {UPLOAD_FILE_PATH}")
        LOGGER.info("✓ File uploaded")

    LOGGER.info("✓ File input actuation test passed")


if __name__ == "__main__":
    fire.Fire(main)
