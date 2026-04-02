"""Android QA test using NovaActMobileQa with AWS Device Farm.

Demonstrates combining QA assertions with mobile actuation to run
QA tests across multiple Android apps via Device Farm remote access sessions.

Usage:
python -m examples.qa.mobile_qa.android
"""

from nova_act import workflow

from examples.actuation.mobile.nova_act_mobile import MobileActuator
from examples.nova_act_client import NovaActClient
from examples.qa.nova_act_qa import NovaActMobileQa
from examples.utils import get_logger

LOGGER = get_logger(__name__)

# Pin to a Pixel device — default apps vary by vendor.
_DEFAULT_DEVICE_ARN = (
    "arn:aws:devicefarm:us-west-2::device:876125E44C784FCD9A31D40F1E37E11F"
)


@workflow(**NovaActClient.get_workflow_kwargs())
def main() -> None:
    """Run QA tests on Android."""
    with NovaActMobileQa(
        app_package="com.android.settings",
        app_activity=".Settings",
        device_arn=_DEFAULT_DEVICE_ARN,
    ) as nova:
        # --- Settings app ---
        nova.check("The Settings page is open")

        nova.act("Go to the Battery page")
        nova.expect("The battery percentage").to_equal(100)

        LOGGER.info("✓ Settings tests passed")

        # --- Switch to Files app ---
        nova.go_to_url(MobileActuator.app_url("com.google.android.apps.nbu.files"))

        nova.check("A list of file categories or recent files is visible")

        nova.act("Go to the Apps category")
        nova.act("Filter the Installed apps by game")
        nova.expect("The name of the first app").to_contain("Play Games")

        LOGGER.info("✓ Files tests passed")

        LOGGER.info("✓ All mobile QA tests passed")


if __name__ == "__main__":
    main()
