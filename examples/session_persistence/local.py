"""Session persistence with LocalFileSessionProvider.

Saves and restores browser session state (cookies + localStorage) across
Nova Act runs via the Nova Act SDK's ``LocalFileSessionProvider``. Includes a built-in demo
site for self-contained demos; pass --starting_page to use a real site
instead.

Usage:
python -m examples.session_persistence.local
python -m examples.session_persistence.local --starting_page https://example.com --profile my-agent
"""

import fire
from nova_act import LocalFileSessionProvider, NovaAct, workflow

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
    profile: str = "local_example",
    session_dir: str = "~/.nova-act/sessions",
    headless: bool = False,
) -> None:
    use_static = starting_page is None
    provider = LocalFileSessionProvider(
        profile=profile, directory=session_dir, restore_local_storage=True
    )

    with NovaAct(
        starting_page="about:blank" if use_static else starting_page,
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
