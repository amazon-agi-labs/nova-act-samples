"""iOS quick start with Nova Act.

Launches pre-installed iOS apps and performs simple interactions using
Nova Act with AWS Device Farm. No app upload or CLI configuration required.

Usage:
python -m examples.actuation.mobile.ios_quick_start
"""

from nova_act import NovaAct, workflow

from examples.actuation.mobile.nova_act_mobile import DeviceFarmActuator, MobileActuator
from examples.actuation.mobile.nova_act_mobile.app import MobileAppConfig
from examples.nova_act_client import NovaActClient
from examples.utils import get_logger

LOGGER = get_logger(__name__)

# Pre-installed iOS apps to interact with — swap these to target different apps.
# Configs instruct the DeviceFarm and Mobile actuators how to launch and identify
# each app. See nova_act_mobile/app/config.py for details.
SETTINGS = MobileAppConfig.for_ios(bundle_id="com.apple.Preferences")
PHONE = MobileAppConfig.for_ios(bundle_id="com.apple.mobilephone")


@workflow(**NovaActClient.get_workflow_kwargs())
def main() -> None:
    """Launch pre-installed iOS apps and interact with them on Device Farm."""
    with NovaAct(
        actuator=DeviceFarmActuator(app_config=SETTINGS),
        starting_page=MobileActuator.app_url(SETTINGS.app_identifier),
        ignore_https_errors=True,
        ignore_screen_dims_check=True,
    ) as nova:
        # Navigate through Settings
        result = nova.act_get("Return a summary of what you see on the page")
        LOGGER.info(f"✓ Screen summary: {result.parsed_response}")

        nova.act("Go to General > About")
        LOGGER.info("✓ Settings navigation completed")

        # Switch to the Phone app and add a contact
        nova.go_to_url(MobileActuator.app_url(PHONE.app_identifier))

        nova.act("Go to the Contacts tab")
        contact_data = {"first_name": "Nova", "last_name": "Act", "company": "Amazon"}
        nova.act(f"Add a new contact with the following data: {contact_data}")
        LOGGER.info("✓ Contact created")

        LOGGER.info("✓ iOS example finished")


if __name__ == "__main__":
    main()
