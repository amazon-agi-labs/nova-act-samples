"""iOS QA test using NovaActMobileQa with AWS Device Farm.

Demonstrates combining QA assertions with mobile actuation to run
QA tests across multiple iOS apps via Device Farm remote access sessions.

Usage:
python -m examples.qa.mobile_qa.ios
"""

from nova_act import workflow

from examples.actuation.mobile.nova_act_mobile import MobileActuator
from examples.nova_act_client import NovaActClient
from examples.qa.nova_act_qa import NovaActMobileQa
from examples.utils import get_logger

LOGGER = get_logger(__name__)


@workflow(**NovaActClient.get_workflow_kwargs())
def main() -> None:
    """Run QA tests on iOS."""
    with NovaActMobileQa(bundle_id="com.apple.Preferences") as nova:
        # --- Settings app ---
        nova.expect("The page title").to_equal("Settings")

        nova.act("Go to the Battery page")
        nova.expect("The battery percentage").to_equal(100)

        LOGGER.info("✓ Settings tests passed")

        # --- Switch to Phone app ---
        nova.go_to_url(MobileActuator.app_url("com.apple.mobilephone"))

        nova.act("Go to the Contacts tab")
        nova.check("An empty contacts list shows")
        contact_data = {"first_name": "Nova", "last_name": "Act", "company": "Amazon"}
        nova.act(f"Add a new contact with the following data: {contact_data}")
        nova.expect("The contact name").to_equal(
            f"{contact_data['first_name']} {contact_data['last_name']}"
        )

        LOGGER.info("✓ Contacts tests passed")

        LOGGER.info("✓ All mobile QA tests passed")


if __name__ == "__main__":
    main()
