"""Simple tool use example with NovaAct.

Demonstrates using a custom tool to get current date and enter it in a form.

Usage:
python -m examples.tool_use.basic.get_current_date
"""

from datetime import datetime
from pathlib import Path

from examples.utils import get_logger, get_workflow_kwargs

from nova_act import NovaAct, SecurityOptions, tool, workflow

LOGGER = get_logger(__name__)


@tool
def get_current_date():
    """Gets the current date in MM/DD/YYYY format."""
    return datetime.now().strftime("%m/%d/%Y")


@workflow(**get_workflow_kwargs())
def main():
    with NovaAct(
        starting_page=f"file://{Path(__file__).parent.absolute() / 'ui' / 'date_form.html'}",
        security_options=SecurityOptions(allow_file_urls=True),
        tools=[get_current_date],
    ) as nova:
        result = nova.act_get("Submit today's date and return the submitted date")
        LOGGER.info(f"✓ Form submitted with date: {result.parsed_response}")


if __name__ == "__main__":
    main()
