"""Tool use example with a mock API call.

Demonstrates using a custom tool to make an API call between browser
automation steps. The workflow performs a browser action, calls an external
API (mocked) via a tool to retrieve state, then validates the response in Python.

Usage:
python -m examples.tool_use.basic.api_call
"""

import json
from pathlib import Path

import fire
from nova_act import NovaAct, SecurityOptions, tool, workflow

from examples.nova_act_client import NovaActClient
from examples.utils import get_logger

LOGGER = get_logger(__name__)

SCRIPT_DIR = str(Path(__file__).parent.absolute())


@tool
def validate_device_state() -> str:
    """Call an external API to check the current state of a resource.

    Returns a JSON string that the workflow can parse and assert against.
    """
    # Replace this with a real API call
    response = {
        "device_id": "thermostat-001",
        "status": "online",
        "temperature_f": 72,
        "target_temperature_f": 72,
        "mode": "cooling",
        "valid": True,
    }
    LOGGER.info(f"✓ API response: {json.dumps(response)}")
    return json.dumps(response)


@workflow(**NovaActClient.get_workflow_kwargs())
def main() -> None:
    """Perform a browser action, validate state via API, and assert the result."""
    LOGGER.info("🚀 Starting API call tool example...")

    with NovaAct(
        starting_page=f"file://{SCRIPT_DIR}/ui/device_control.html",
        security_options=SecurityOptions(allowed_file_open_paths=[f"{SCRIPT_DIR}/*"]),
        tools=[validate_device_state],
    ) as nova:
        result = nova.act_get("Turn on the device, then validate and return the status")
        status = result.parsed_response

        LOGGER.info(f"✓ Device status: {status}")
        assert status == "online", f"Expected 'online', got '{status}'"
        LOGGER.info("✓ Device state validated successfully")


if __name__ == "__main__":
    fire.Fire(main)
