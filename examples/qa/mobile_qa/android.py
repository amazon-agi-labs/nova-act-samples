"""Android QA test using NovaActQa with AWS Device Farm.

Demonstrates combining the NovaActQa utilities with the
mobile actuation module to run QA test across multiple Android apps
via Device Farm remote access sessions.

Usage:
python -m examples.qa.mobile_qa.android
"""

from nova_act import workflow

from examples.actuation.mobile.nova_act_mobile import DeviceFarmActuator, MobileActuator
from examples.actuation.mobile.nova_act_mobile.app import MobileAppConfig
from examples.nova_act_client import NovaActClient
from examples.qa.nova_act_qa import NovaActQa
from examples.utils import get_logger

LOGGER = get_logger(__name__)

# Pin to a Pixel device — default apps vary by vendor.
_DEFAULT_DEVICE_ARN = (
    "arn:aws:devicefarm:us-west-2::device:876125E44C784FCD9A31D40F1E37E11F"
)

# App configs instruct the DeviceFarm and Mobile actuators how to launch and identify
# each app. See nova_act_mobile/app/config.py for details.
SETTINGS = MobileAppConfig.for_android(
    app_package="com.android.settings",
    app_activity=".Settings",
)
FILES_APP = MobileAppConfig.for_android(
    app_package="com.google.android.apps.nbu.files",
    app_activity="com.google.android.apps.nbu.files.home.HomeActivity",
)


@workflow(**NovaActClient.get_workflow_kwargs())
def main() -> None:
    """Run QA tests on Android."""
    with NovaActQa(
        actuator=DeviceFarmActuator(
            app_config=SETTINGS, device_arn=_DEFAULT_DEVICE_ARN
        ),
        starting_page=MobileActuator.app_url(SETTINGS.app_identifier),
        ignore_https_errors=True,
        ignore_screen_dims_check=True,
    ) as nova:
        # --- Settings app ---
        nova.check("The Settings page is open")

        nova.act("Go to the Battery page")
        nova.expect("The battery percentage").to_equal(100)

        LOGGER.info("✓ Settings tests passed")

        # --- Switch to Files app ---
        nova.go_to_url(MobileActuator.app_url(FILES_APP.app_identifier))

        nova.check("A list of file categories or recent files is visible")

        nova.act("Go to the Apps category")
        nova.act("Filter the Installed apps by game")
        nova.expect("The name of the first game").to_contain("Play Games")

        LOGGER.info("✓ Files tests passed")

        LOGGER.info("✓ All mobile QA tests passed")


if __name__ == "__main__":
    main()
