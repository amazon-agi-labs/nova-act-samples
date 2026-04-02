"""Android quick start with Nova Act.

Launches pre-installed Android apps and performs simple interactions using
Nova Act with AWS Device Farm. No app upload or CLI configuration required.

Usage:
python -m examples.actuation.mobile.android_quick_start
"""

import fire
from nova_act import workflow

from examples.actuation.mobile.nova_act_mobile import MobileActuator, NovaActMobile
from examples.nova_act_client import NovaActClient
from examples.utils import get_logger

LOGGER = get_logger(__name__)

_DEFAULT_DEVICE_ARN = (
    "arn:aws:devicefarm:us-west-2::device:876125E44C784FCD9A31D40F1E37E11F"
)


@workflow(**NovaActClient.get_workflow_kwargs())
def main(device_arn: str = _DEFAULT_DEVICE_ARN) -> None:
    """Launch pre-installed Android apps and interact with them on Device Farm."""
    with NovaActMobile(
        app_package="com.android.vending",
        app_activity="com.google.android.finsky.activities.MainActivity",
        device_arn=device_arn,
    ) as nova:
        # Verify the Play Store launched
        result = nova.act_get("Return a summary of what you see on the page")
        LOGGER.info(f"✓ Screen summary: {result.parsed_response}")

        # Search for an app
        nova.act("Search for Nova Act")

        # Switch to the Files app
        nova.go_to_url(MobileActuator.app_url("com.google.android.apps.nbu.files"))

        # Browse file categories
        result = nova.act_get(
            "Go to the Apps category, filter the installed apps by game, and return the name of the first game"
        )
        game = result.parsed_response
        LOGGER.info(f"✓ Filtered installed apps for game: {game}")

        LOGGER.info("✓ Android example finished")


if __name__ == "__main__":
    fire.Fire(main)
