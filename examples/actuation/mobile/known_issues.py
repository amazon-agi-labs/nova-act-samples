"""Known issues demo for Nova Act mobile actuation.

Reproduces three known actuation issues with the AWS Device Farm sample app:

1. Pull-to-refresh: agentScroll("up") generates a slow swipe that doesn't
   exceed the overscroll threshold required to trigger pull-to-refresh.

2. Time picker typing: agentType() fails on Android time picker inputs because
   active_element.send_keys() doesn't work on native time picker widgets.

3. Date picker navigation: The calendar opens at January 1994. The model doesn't
   identify the year label as a tappable shortcut and instead clicks the next-month
   arrow repeatedly to reach today's date.

Usage:
python -m examples.actuation.mobile.known_issues
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
    cli_args = CliArgs()  # type: ignore[call-arg]
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
        # Navigate to the Inputs screen
        nova.act("Go to the Inputs page")

        # ── Issue 1: Pull-to-refresh ──────────────────────────────────
        # agentScroll("up") performs a slow 300ms swipe across 70% of
        # the screen height. Pull-to-refresh requires a fast swipe
        # starting from the very top of the content area that exceeds
        # the overscroll threshold. The gesture never triggers refresh.
        nova.act("Scroll right until the Pull to Refresh tab")
        nova.act("Scroll up to refresh")  # <-- fails to trigger refresh

        # ── Issue 2: Time picker typing ───────────────────────────────
        # agentType() taps the time picker field, then calls
        # active_element.send_keys() on the focused element. Android
        # native time picker widgets don't accept send_keys() — the
        # active element after tapping is the picker widget itself, not
        # a text input. The iOS fallback (mobile: type) is not available
        # on Android, so the call raises ActActuationError.
        # Additionally, the clock-face time picker requires a circular
        # drag gesture to select the hour/minute hands — a gesture type
        # not supported by the current actuator primitives.
        nova.act("Scroll right to the Time Picker")
        nova.act(
            "Open the keyboard and type 0900 to set the time to 9:00 AM"
        )  # <-- raises

        # ── Issue 3: Date picker calendar navigation ──────────────────
        # The calendar opens at January 1994. The model doesn't identify
        # the year label at the top as a tappable shortcut to jump to a
        # year — it clicks the next-month arrow repeatedly to reach the date,
        # making this extremely slow or timing out.
        nova.act("Scroll right to the Date Picker")
        one_year = (datetime.now() + timedelta(days=365)).strftime("%m/%d/%Y")
        nova.act(
            f"Select date {one_year}"
        )  # <-- clicks arrow ~12 times from current month


if __name__ == "__main__":
    main()
