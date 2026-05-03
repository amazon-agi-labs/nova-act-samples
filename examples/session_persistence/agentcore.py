"""Session persistence with AgentCoreBrowserSessionProvider.

Saves and restores browser session state server-side using AgentCore
browser profiles via the Nova Act SDK's ``AgentCoreBrowserSessionProvider``.
Includes a built-in demo site served over CDP for self-contained demos;
pass --starting_page to use a real site instead.

Usage:
python -m examples.session_persistence.agentcore
python -m examples.session_persistence.agentcore --starting_page https://example.com --profile my-agent
"""

import fire
from nova_act import AgentCoreBrowserSessionProvider, NovaAct, workflow

from examples.nova_act_client import NovaActClient
from examples.session_persistence.hitl import ConsoleHumanInputCallbacks
from examples.session_persistence.static_site import (
    setup_static_page,
)

ACT_PROMPT = (
    "If you see a login page, ask the user to login. "
    "If there is a Save Preferences button, click it. "
    "Then describe what you see on the page."
)


@workflow(**NovaActClient.get_workflow_kwargs())
def main(
    starting_page: str | None = None,
    profile: str = "agentcore_example",
    region: str = "us-east-1",
    headless: bool = False,
) -> None:
    use_static = starting_page is None
    provider = AgentCoreBrowserSessionProvider(profile=profile, region=region)

    with provider.cdp_session() as (ws_url, headers):
        with NovaAct(
            starting_page="about:blank" if use_static else starting_page,
            cdp_endpoint_url=ws_url,
            cdp_headers=headers,
            browser_auth=provider,
            headless=headless,
            ignore_https_errors=use_static,
            human_input_callbacks=ConsoleHumanInputCallbacks(),
        ) as nova:
            if use_static:
                url = setup_static_page(nova.page)
                nova.page.goto(url)

            nova.act(ACT_PROMPT)


if __name__ == "__main__":
    fire.Fire(main)
