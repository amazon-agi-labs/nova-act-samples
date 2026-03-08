"""Android quick start with Nova Act.

Launches pre-installed Android apps and performs simple interactions using
Nova Act with AWS Device Farm. No app upload or CLI configuration required.

Usage:
python -m examples.actuation.mobile.android_quick_start
"""

from nova_act import NovaAct, workflow

from examples.actuation.mobile.nova_act_mobile import DeviceFarmActuator, MobileActuator
from examples.actuation.mobile.nova_act_mobile.app import MobileAppConfig
from examples.nova_act_client import NovaActClient
from examples.utils import get_logger

LOGGER = get_logger(__name__)

_DEFAULT_DEVICE_ARN = (
    "arn:aws:devicefarm:us-west-2::device:876125E44C784FCD9A31D40F1E37E11F"
)

# Pre-installed Android apps to interact with — swap these to target different apps.
# Configs instruct the DeviceFarm and Mobile actuators how to launch and identify
# each app. See nova_act_mobile/app/config.py for details.
PLAY_STORE = MobileAppConfig.for_android(
    app_package="com.android.vending",
    app_activity="com.google.android.finsky.activities.MainActivity",
)
FILES_APP = MobileAppConfig.for_android(
    app_package="com.google.android.apps.nbu.files",
    app_activity="com.google.android.apps.nbu.files.home.HomeActivity",
)


@workflow(**NovaActClient.get_workflow_kwargs())
def main(device_arn: str = _DEFAULT_DEVICE_ARN) -> None:
    """Launch pre-installed Android apps and interact with them on Device Farm."""
    with NovaAct(
        actuator=DeviceFarmActuator(app_config=PLAY_STORE, device_arn=device_arn),
        starting_page=MobileActuator.app_url(PLAY_STORE.app_identifier),
        ignore_https_errors=True,
        ignore_screen_dims_check=True,
    ) as nova:
        # Verify the Play Store launched
        result = nova.act_get("Return a summary of what you see on the page")
        LOGGER.info(f"✓ Screen summary: {result.parsed_response}")

        # Search for an app
        nova.act("Search for Nova Act")

        # Switch to the Files app
        nova.go_to_url(MobileActuator.app_url(FILES_APP.app_identifier))

        # Browse file categories
        result = nova.act_get(
            "Go to the Apps category, filter the installed apps by game, and return the name of the first game"
        )
        game = result.parsed_response
        LOGGER.info(f"✓ Filtered installed apps for game: {game}")

        LOGGER.info("✓ Android example finished")


if __name__ == "__main__":
    import fire

    fire.Fire(main)
