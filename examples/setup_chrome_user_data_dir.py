"""Configure a persistent browser profile for Nova Act workflows.

Opens a browser window where you can log in, set preferences, and configure
any sites you need. Those sessions are saved to a user_data_dir on disk.
When you later run a Nova Act workflow configured with the same user_data_dir,
all browser state carries over — cookies, local storage, auth sessions, and
site preferences — so you won't need to re-authenticate until the provider's
session expires.

See the SDK README for more details:
https://github.com/aws/nova-act?tab=readme-ov-file#authentication-cookies-and-persistent-browser-state

Usage:
python -m examples.setup_chrome_user_data_dir
"""

import os
from pathlib import Path

import fire
from nova_act import NovaAct, workflow

from examples.nova_act_client import NovaActClient
from examples.utils import get_logger

LOGGER = get_logger(__name__)

_DEFAULT_USER_DATA_DIR = str(Path.home() / ".nova-act-examples" / "user-data-dir")


@workflow(**NovaActClient.get_workflow_kwargs())
def main(user_data_dir: str = _DEFAULT_USER_DATA_DIR) -> None:
    os.makedirs(user_data_dir, exist_ok=True)

    with NovaAct(
        starting_page="about:blank",
        user_data_dir=user_data_dir,  # Point to our user data dir path
        clone_user_data_dir=False,  # Disable cloning of the dir so its reused
    ):
        input(
            "A browser window has opened. Navigate to your sites and log in, "
            "then press Enter here to save your session..."
        )

    LOGGER.info(f"✓ User data dir saved to {user_data_dir}")


if __name__ == "__main__":
    fire.Fire(main)
