"""Electron app automation over CDP.

Connects Nova Act to a running Electron app via its Chrome DevTools Protocol (CDP)
endpoint. An example task manager app is included under app/, this example script
defaults to its CDP endpoint.

Usage:
# Connects to the CDP URL at http://localhost:9222 (the default of the example app)
python -m examples.actuation.desktop.electron.main
# Specify a CDP URL
python -m examples.actuation.desktop.electron.main --cdp_url=http://localhost:9333
"""

import fire
from nova_act import NovaAct, workflow

from examples.nova_act_client import NovaActClient
from examples.utils import get_logger

LOGGER = get_logger(__name__)

CDP_URL = "http://localhost:9222"


@workflow(**NovaActClient.get_workflow_kwargs())
def main(cdp_url: str = CDP_URL) -> None:
    """Connect to an Electron desktop app over CDP and automate it with Nova Act.

    Args:
        cdp_url: CDP endpoint URL. Defaults to http://localhost:9222.
    """
    LOGGER.info(f"🤖 Connecting Nova Act to app at {cdp_url}...")

    with NovaAct(
        cdp_endpoint_url=cdp_url,
        cdp_use_existing_page=True,
    ) as nova:
        nova.act(
            'Add a new task for "Deploy new feature to staging" with high priority'
        )

        nova.act("Filter by Active tasks")

        result = nova.act_get("How many active tasks are shown?")
        LOGGER.info(f"✓ Active tasks: {result.response}")


if __name__ == "__main__":
    fire.Fire(main)
