"""Simple tool use example with NovaAct.

Demonstrates using a custom tool to get current date and enter it in a form.

Usage:
python -m examples.tool_use.basic.get_current_date
"""

from datetime import datetime
from pathlib import Path

from nova_act import NovaAct, SecurityOptions, tool, workflow

from examples.nova_act_client import NovaActClient
from examples.utils import get_logger

LOGGER = get_logger(__name__)


@tool
def get_current_date():
    """Gets the current date in MM/DD/YYYY format."""
    return datetime.now().strftime("%m/%d/%Y")


SCRIPT_DIR = str(Path(__file__).parent.absolute())


@workflow(**NovaActClient.get_workflow_kwargs())
def main():
    with NovaAct(
        starting_page=f"file://{SCRIPT_DIR}/ui/date_form.html",
        security_options=SecurityOptions(allowed_file_open_paths=[f"{SCRIPT_DIR}/*"]),
        tools=[get_current_date],
    ) as nova:
        result = nova.act_get("Submit today's date and return the submitted date")
        LOGGER.info(f"✓ Form submitted with date: {result.parsed_response}")


if __name__ == "__main__":
    main()
