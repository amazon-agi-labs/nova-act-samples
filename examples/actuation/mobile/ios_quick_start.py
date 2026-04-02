"""iOS quick start with Nova Act.

Launches pre-installed iOS apps and performs simple interactions using
Nova Act with AWS Device Farm. No app upload or CLI configuration required.

Usage:
python -m examples.actuation.mobile.ios_quick_start
"""

from nova_act import workflow

from examples.actuation.mobile.nova_act_mobile import MobileActuator, NovaActMobile
from examples.nova_act_client import NovaActClient
from examples.utils import get_logger

LOGGER = get_logger(__name__)


@workflow(**NovaActClient.get_workflow_kwargs())
def main() -> None:
    """Launch pre-installed iOS apps and interact with them on Device Farm."""
    with NovaActMobile(bundle_id="com.apple.Preferences") as nova:
        # Navigate through Settings
        result = nova.act_get("Return a summary of what you see on the page")
        LOGGER.info(f"✓ Screen summary: {result.parsed_response}")

        nova.act("Go to General > About")
        LOGGER.info("✓ Settings navigation completed")

        # Switch to the Phone app and add a contact
        nova.go_to_url(MobileActuator.app_url("com.apple.mobilephone"))

        nova.act("Go to the Contacts tab")
        contact_data = {"first_name": "Nova", "last_name": "Act", "company": "Amazon"}
        nova.act(f"Add a new contact with the following data: {contact_data}")
        LOGGER.info("✓ Contact created")

        LOGGER.info("✓ iOS example finished")


if __name__ == "__main__":
    main()
