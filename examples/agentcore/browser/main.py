"""AgentCore Browser example.

Demonstrates how to use Amazon Nova Act with Amazon Bedrock AgentCore Browser for managed remote browser sessions.

Usage:
python -m examples.agentcore.browser.main
"""

import boto3
import fire
from bedrock_agentcore.tools.browser_client import browser_session
from nova_act import NovaAct, workflow

from examples.agentcore.browser.utils import get_console_live_view_url
from examples.nova_act_client import NovaActClient
from examples.utils import get_logger

LOGGER = get_logger(__name__)


@workflow(**NovaActClient.get_workflow_kwargs())
def main() -> None:
    """Starts a AgentCore Browser Session and runs a Nova Act Workflow on it"""

    LOGGER.info("🚀 Initializing AgentCore Browser Session...")

    # Initialize AgentCore Browser session
    region = boto3.Session().region_name or "us-east-1"
    with browser_session(region) as browser_client:
        # Get and print the live view URL
        live_view_url = get_console_live_view_url(browser_client)
        LOGGER.info(
            f"🌐 Browser Session created, view it on the AWS Console: {live_view_url}"
        )
        # Get browser session CDP endpoint and headers
        cdp_endpoint_url, cdp_headers = browser_client.generate_ws_headers()

        LOGGER.info(
            "🤖 Starting Nova Act and connecting it to AgentCore Browser Session..."
        )

        # Start Nova Act and connect to the browser session over CDP
        with NovaAct(
            starting_page="https://nova.amazon.com/act/gym/next-dot/search",
            cdp_endpoint_url=cdp_endpoint_url,
            cdp_headers=cdp_headers,
        ) as nova:
            nova.act("Find flights from Boston to Wolf on Feb 22nd")


if __name__ == "__main__":
    fire.Fire(main)
