"""iOS permission dialog handling with Nova Act.

Demonstrates handling iOS permission dialogs using the ``mobile: alert``
Appium command. Unlike Android, iOS cannot pre-grant permissions on real
devices — dialogs must be accepted as they appear.

The ``mobile: alert`` command directly accepts whatever system alert is showing.
A retry loop is needed because calling it before a dialog appears will throw.

Usage:
python -m examples.actuation.mobile.ios_permissions
"""

import time

import fire
from nova_act import workflow

from examples.actuation.mobile.nova_act_mobile import NovaActMobile
from examples.nova_act_client import NovaActClient
from examples.utils import get_logger

LOGGER = get_logger(__name__)

_SAFARI_BUNDLE_ID = "com.apple.mobilesafari"


def _accept_alerts(nova: NovaActMobile, max_attempts: int = 5) -> int:
    """Accept all pending system alerts via mobile: alert.

    Returns the number of alerts accepted. Stops when no more alerts are
    present (the command throws when there's nothing to accept).
    """
    handled = 0
    for _ in range(max_attempts):
        try:
            nova.driver.execute_script("mobile: alert", {"action": "accept"})
            handled += 1
            LOGGER.info(f"✓ Alert {handled} accepted")
            time.sleep(1)
        except Exception:
            break
    return handled


@workflow(**NovaActClient.get_workflow_kwargs())
def main(device_arn: str | None = None) -> None:
    """Trigger a location permission dialog and handle it via mobile: alert."""
    with NovaActMobile(
        bundle_id=_SAFARI_BUNDLE_ID,
        device_arn=device_arn,
    ) as nova:
        # Navigate to a page that triggers a location permission dialog
        nova.act("Search for 'weather near me'")
        # Wait to let alerts settle
        time.sleep(3)

        # Handle permission dialogs via mobile: alert (no inference cost)
        handled = _accept_alerts(nova)
        LOGGER.info(f"✓ Handled {handled} permission dialog(s)")

        result = nova.act_get("Return a summary of what you see on the page")
        LOGGER.info(f"✓ Screen summary: {result.parsed_response}")

    LOGGER.info("✓ iOS permissions example finished")


if __name__ == "__main__":
    fire.Fire(main)
