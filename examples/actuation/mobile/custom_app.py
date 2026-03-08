"""Custom app automation with Nova Act.

Demonstrates end-to-end mobile app automation using Nova Act with AWS Device
Farm. Accepts CLI arguments for app path, device selection, and platform
configuration. Defaults to the AWS Device Farm sample APK when run with no
arguments, exercising inputs, checkboxes, date pickers, and native components.

Usage:
python -m examples.actuation.mobile.custom_app
"""

from datetime import datetime, timedelta

from nova_act import NovaAct, workflow

from examples.actuation.mobile.nova_act_mobile import DeviceFarmActuator, MobileActuator
from examples.actuation.mobile.utils.cli import CliArgs
from examples.nova_act_client import NovaActClient
from examples.utils import get_logger

LOGGER = get_logger(__name__)


@workflow(**NovaActClient.get_workflow_kwargs())
def main() -> None:
    """Orchestrate Device Farm setup and execute Nova Act workflow on remote device."""

    # Parse and validate CLI arguments — defaults to Device Farm sample app if no args provided
    cli_args = CliArgs()  # type: ignore[call-arg]

    # Create configs from CLI args
    app_config = cli_args.to_app_config()
    upload_config = cli_args.to_upload_config()

    with NovaAct(
        actuator=DeviceFarmActuator(
            app_config=app_config,
            upload_config=upload_config,
            project_arn=cli_args.project_arn,
            device_arn=cli_args.device_arn,
        ),
        starting_page=MobileActuator.app_url(app_config.app_identifier),
        ignore_https_errors=True,
        ignore_screen_dims_check=True,
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
    main()
