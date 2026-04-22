"""Android activity launch with Nova Act.

Demonstrates launching an app into a specific exported Activity and switching
to a different Activity mid-workflow. Uses the AWS Device Farm sample app
which has multiple exported activities.

This only works for multi-activity Android apps with ``android:exported="true"``
on the target activities. Single-activity apps (Jetpack Compose, React Native,
Flutter) host all screens in one Activity — use deep links instead.
iOS has no activity concept; deep links are the only option there.

Usage:
python -m examples.actuation.mobile.android_activity_launch
"""

from pathlib import Path

import fire
from nova_act import workflow

from examples.actuation.mobile.nova_act_mobile import MobileActuator, NovaActMobile
from examples.nova_act_client import NovaActClient
from examples.utils import get_logger

LOGGER = get_logger(__name__)

_PACKAGE = "com.amazonaws.devicefarm.android.referenceapp"
_BACK_NAV_ACTIVITY = (
    "com.amazonaws.devicefarm.android.referenceapp.Activities.BackNavigationActivity"
)
_UP_NAV_ACTIVITY = (
    "com.amazonaws.devicefarm.android.referenceapp.Activities.UpNavigationActivity"
)
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
    """Launch into BackNavigationActivity, then switch to UpNavigationActivity."""
    with NovaActMobile(
        app_package=_PACKAGE,
        app_activity=_BACK_NAV_ACTIVITY,
        app_path=_APK_PATH,
        device_arn=device_arn,
    ) as nova:
        result = nova.act_get("Return a summary of what you see on the page")
        LOGGER.info(f"✓ BackNavigationActivity: {result.parsed_response}")

        # Switch to a different activity mid-workflow via go_to_url
        nova.go_to_url(MobileActuator.app_url(_PACKAGE, activity=_UP_NAV_ACTIVITY))
        result = nova.act_get("Return a summary of what you see on the page")
        LOGGER.info(f"✓ UpNavigationActivity: {result.parsed_response}")

    LOGGER.info("✓ Android activity launch example finished")


if __name__ == "__main__":
    fire.Fire(main)
