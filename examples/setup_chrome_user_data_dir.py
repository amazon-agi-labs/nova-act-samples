"""Configure Nova Act to use websites with your browser data.

Set up a user_data_dir for your browser data and configure Nova Act with it.
See the SDK README for more details.

Usage:
python -m examples.setup_chrome_user_data_dir --user_data_dir <directory>
"""

import os

import fire  # type: ignore

from examples.utils import get_logger, get_workflow_kwargs

from nova_act import NovaAct, workflow

LOGGER = get_logger(__name__)


@workflow(**get_workflow_kwargs())
def main(url: str, user_data_dir: str) -> None:
    os.makedirs(user_data_dir, exist_ok=True)

    with NovaAct(
        starting_page=url,
        user_data_dir=user_data_dir,  # Point to our user data dir path
        clone_user_data_dir=False,  # Disable cloning of the dir so its reused
    ):
        input("Log into your websites, then press enter...")

    LOGGER.info(f"✓ User data dir saved to {user_data_dir}")


if __name__ == "__main__":
    fire.Fire(main)
