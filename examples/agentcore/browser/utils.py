"""Utility functions for AgentCore Browser examples."""

from bedrock_agentcore.tools.browser_client import BrowserClient


def get_console_live_view_url(browser_client: BrowserClient) -> str:
    """Generate the AWS Console live view URL for the AgentCore Browser session."""
    session_id = browser_client.get_session()["sessionId"]
    region = browser_client.region
    return (
        f"https://{region}.console.aws.amazon.com/bedrock-agentcore/browser/"
        f"aws.browser.v1/session/{session_id}?region={region}"
    )
