"""iOS deep link navigation with Nova Act.

Demonstrates opening a custom URL scheme deep link on iOS at launch.
Uses the ``tel://`` scheme which is handled by the built-in Phone app.

iOS supports deep links via custom URL schemes (``myapp://...``) and the
``mobile: deepLink`` Appium command. Universal Links (``https://``) are not
available on public Device Farm devices because re-signing strips the
Associated Domains entitlement.

Usage:
python -m examples.actuation.mobile.ios_deep_link
"""

import fire
from nova_act import workflow

from examples.actuation.mobile.nova_act_mobile import NovaActMobile
from examples.nova_act_client import NovaActClient
from examples.utils import get_logger

LOGGER = get_logger(__name__)

_PHONE_BUNDLE_ID = "com.apple.mobilephone"


@workflow(**NovaActClient.get_workflow_kwargs())
def main(device_arn: str | None = None) -> None:
    """Launch the Phone app and dial a number via tel:// deep link."""
    with NovaActMobile(
        bundle_id=_PHONE_BUNDLE_ID,
        deep_link="tel://5551234567",
        device_arn=device_arn,
    ) as nova:
        result = nova.act_get("Return a summary of what you see on the page")
        LOGGER.info(f"✓ Deep link opened: {result.parsed_response}")

    LOGGER.info("✓ iOS deep link example finished")


if __name__ == "__main__":
    fire.Fire(main)
