"""Android permission pre-granting with Nova Act.

Demonstrates eliminating all permission dialogs on Android by granting
permissions at the OS level before the app launches. Uses
``additional_capabilities`` to pass ``appium:autoLaunch: false`` so
permissions can be granted before the app starts.

Usage:
python -m examples.actuation.mobile.android_permissions
"""

from pathlib import Path

import fire
from nova_act import workflow

from examples.actuation.mobile.nova_act_mobile import MobileActuator, NovaActMobile
from examples.nova_act_client import NovaActClient
from examples.utils import get_logger

LOGGER = get_logger(__name__)

_PACKAGE = "com.amazonaws.devicefarm.android.referenceapp"
_ACTIVITY = "com.amazonaws.devicefarm.android.referenceapp.Activities.MainActivity"
_APK_PATH = str(
    Path(__file__).resolve().parent
    / "nova_act_mobile"
    / "app"
    / "samples"
    / "aws-device-farm-sample"
    / "app-debug.apk"
)


@workflow(**NovaActClient.get_workflow_kwargs())
def main(device_arn: str | None = None) -> None:
    """Pre-grant permissions on Android OS first, then open the app."""
    # autoLaunch: false prevents the app from starting before we grant
    # permissions. The actuator's default is already false, but we set it
    # explicitly here to show the pattern.
    with NovaActMobile(
        app_package=_PACKAGE,
        app_activity=_ACTIVITY,
        app_path=_APK_PATH,
        device_arn=device_arn,
        additional_capabilities={
            "appium:autoLaunch": False,
        },
    ) as nova:
        # Grant all permissions at the OS level — no inference cost
        LOGGER.info("Granting all permissions via mobile: changePermissions...")
        nova.driver.execute_script(
            "mobile: changePermissions",
            {
                "permissions": "all",
                "action": "grant",
                "target": "pm",
            },
        )
        LOGGER.info("✓ Permissions granted")

        # Launch the app — all permissions already granted
        nova.go_to_url(MobileActuator.app_url(_PACKAGE))

        # Run the workflow — no permission dialogs should appear
        result = nova.act_get("Return a summary of what you see on the page")
        LOGGER.info(f"✓ Screen summary: {result.parsed_response}")

        nova.act("Go to the Native Components page")
        LOGGER.info("✓ Navigated to Native Components — no permission dialogs")

    LOGGER.info("✓ Android permissions example finished")


if __name__ == "__main__":
    fire.Fire(main)
