"""Custom app automation with Nova Act.

Demonstrates end-to-end mobile app automation using Nova Act with AWS Device
Farm. Accepts CLI arguments for app path, device selection, and platform
configuration. Defaults to the AWS Device Farm sample APK when run with no
arguments, exercising inputs, checkboxes, date pickers, and native components.

Usage:
python -m examples.actuation.mobile.custom_app
"""

from datetime import datetime, timedelta
from pathlib import Path

import fire
from nova_act import workflow

from examples.actuation.mobile.nova_act_mobile import NovaActMobile
from examples.nova_act_client import NovaActClient
from examples.utils import get_logger

LOGGER = get_logger(__name__)

# Default sample app
_SAMPLE_APP_PACKAGE = "com.amazonaws.devicefarm.android.referenceapp"
_SAMPLE_APP_ACTIVITY = (
    "com.amazonaws.devicefarm.android.referenceapp.Activities.MainActivity"
)
_SAMPLE_APP_PATH = str(
    Path(__file__).resolve().parent
    / "nova_act_mobile"
    / "app"
    / "samples"
    / "aws-device-farm-sample"
    / "app-debug.apk"
)


@workflow(**NovaActClient.get_workflow_kwargs())
def main(
    app_package: str = _SAMPLE_APP_PACKAGE,
    app_activity: str = _SAMPLE_APP_ACTIVITY,
    app_path: str = _SAMPLE_APP_PATH,
    project_arn: str | None = None,
    device_arn: str | None = None,
) -> None:
    """Orchestrate Device Farm setup and execute Nova Act workflow on remote device."""
    with NovaActMobile(
        app_package=app_package,
        app_activity=app_activity,
        app_path=app_path,
        project_arn=project_arn,
        device_arn=device_arn,
    ) as nova:
        result = nova.act_get("Return a summary of what you see on the page")
        LOGGER.info(f"✓ Screen summary: {result.parsed_response}")

        # Taps the hamburger icon to open nav drawer and taps the Inputs option to navigate to the Inputs screen
        nova.act("Go to the Inputs page")
        # Types in a text input
        nova.act("Type Hello World into the input field submit the form")
        # Swipes left to the Checkbox tab
        nova.act("Scroll right to the Checkbox tab")
        # Taps the checkbox to select it
        nova.act("Check the checkbox")
        # Picks a date
        nova.act("Scroll right until the Date Picker tab")
        one_week = (datetime.now() + timedelta(weeks=1)).strftime("%m/%d/%Y")
        nova.act(f"Select date {one_week}")
        # Taps the hamburger icon to open nav drawer and taps the Native Components option
        nova.act("Go to the Native Components page")
        # Swipes to the Content Scrolling tab
        nova.act("Scroll right to to Content Scrolling tab")
        # Swipes up to scroll the screen down
        nova.act("Scroll down")


if __name__ == "__main__":
    fire.Fire(main)
