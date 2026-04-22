"""Android deep link navigation with Nova Act.

Demonstrates launching an app with a custom URL scheme deep link and
navigating to a different deep link mid-workflow. Uses the AWS Device Farm
sample app with the ``dfsample://`` URL scheme.

Deep links require app-side support — the app must register a custom URL
scheme and route incoming links to the correct screen. This example uses
``dfsample://main`` and ``dfsample://back-nav``, which are handled by the
AWS Device Farm sample app.

Usage:
python -m examples.actuation.mobile.android_deep_link
"""

from pathlib import Path

import fire
from nova_act import workflow

from examples.actuation.mobile.nova_act_mobile import MobileActuator, NovaActMobile
from examples.nova_act_client import NovaActClient
from examples.utils import get_logger

LOGGER = get_logger(__name__)

_PACKAGE = "com.amazonaws.devicefarm.android.referenceapp"
_MAIN_ACTIVITY = "com.amazonaws.devicefarm.android.referenceapp.Activities.MainActivity"
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
    """Launch with a deep link, then navigate to another deep link mid-workflow."""
    with NovaActMobile(
        app_package=_PACKAGE,
        app_activity=_MAIN_ACTIVITY,
        app_path=_APK_PATH,
        device_arn=device_arn,
        # deep_link opens dfsample://main at session start
        deep_link="dfsample://main",
    ) as nova:
        result = nova.act_get("Return a summary of what you see on the page")
        LOGGER.info(f"✓ Launched with deep link: {result.parsed_response}")

        # Navigate to a different deep link mid-workflow
        nova.go_to_url(
            MobileActuator.app_url(_PACKAGE, deep_link="dfsample://back-nav")
        )
        result = nova.act_get("Return a summary of what you see on the page")
        LOGGER.info(f"✓ Mid-workflow deep link: {result.parsed_response}")

    LOGGER.info("✓ Android deep link example finished")


if __name__ == "__main__":
    fire.Fire(main)
