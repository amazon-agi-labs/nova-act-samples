"""AgentCore Browser Tool actuator for Nova Act.

A custom actuator that extends the SDK's default Playwright-based browser
actuator to manage the lifecycle of an Amazon Bedrock AgentCore Browser Tool
(ACBT) session. Provisions a managed browser session in start() and tears it
down in stop(), while delegating all browser actuation (clicks, typing,
scrolling, screenshots) to the parent class.

Pass the class (not an instance) to NovaAct so the SDK constructs it with
the correct PlaywrightInstanceOptions. The actuator patches in the ACBT CDP
connection details at start time.
"""

from typing import Any

import boto3
from bedrock_agentcore.tools.browser_client import BrowserClient, browser_session
from nova_act.tools.browser.default.default_nova_local_browser_actuator import (
    DefaultNovaLocalBrowserActuator,
)
from nova_act.tools.browser.default.playwright_instance_options import (
    PlaywrightInstanceOptions,
)
from nova_act.util.logging import setup_logging

LOGGER = setup_logging(__name__)


def _get_console_live_view_url(browser_client: BrowserClient, region: str) -> str:
    """Generate the AWS Console live view URL for the ACBT session."""
    session_id = browser_client.get_session()["sessionId"]
    return (
        f"https://{region}.console.aws.amazon.com/bedrock-agentcore/browser/"
        f"aws.browser.v1/session/{session_id}?region={region}"
    )


class AgentCoreBrowserActuator(DefaultNovaLocalBrowserActuator):
    """Actuator that provisions an ACBT session and connects via CDP.

    Defers parent initialization to ``start()`` so the ACBT session can be
    provisioned first and its CDP endpoint patched into the options before
    the Playwright actuator is created.

    Lifecycle: ``start()`` provisions ACBT → patches CDP details → inits
    parent. ``stop()`` tears down Playwright, then the ACBT session.

    Pass as a class (not an instance) so the SDK constructs it with
    ``PlaywrightInstanceOptions``::

        with NovaAct(
            actuator=AgentCoreBrowserActuator,
            starting_page="https://www.example.com",
        ) as nova:
            nova.act("Click the login button")
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # type: ignore[explicit-any]
        """Stash constructor args for deferred parent init.

        Does not call ``super().__init__()`` — that happens in ``start()``
        after the ACBT session provides the CDP endpoint.
        """
        # Don't call super().__init__() yet — we need to patch CDP details first
        self._init_args = args
        self._init_kwargs = kwargs
        self._region = boto3.Session().region_name or "us-east-1"
        self._browser_context_manager: Any = None  # type: ignore[explicit-any]
        self._browser_client: BrowserClient | None = None

    @property
    def started(self, **kwargs: Any) -> bool:  # type: ignore[explicit-any]
        """Check if the actuator is fully started."""
        if self._browser_client is None:
            return False
        return super().started

    @property
    def console_live_view_url(self) -> str | None:
        """AWS Console URL to view the live browser session, or None if not started."""
        if self._browser_client is None:
            return None
        return _get_console_live_view_url(self._browser_client, self._region)

    def start(self, **kwargs: Any) -> None:  # type: ignore[explicit-any]
        """Provision an ACBT session, then start the Playwright actuator over CDP.

        Args:
            **kwargs: Passed through to the parent start().
        """
        if self._browser_client is not None:
            LOGGER.warning("ACBT session already active")
            super().start(**kwargs)
            return

        LOGGER.info(f"Provisioning ACBT session in {self._region}...")
        self._browser_context_manager = browser_session(self._region)
        self._browser_client = self._browser_context_manager.__enter__()

        if self._browser_client is None:
            raise RuntimeError(
                "Failed to provision ACBT session — browser_session() returned None"
            )

        cdp_endpoint_url, cdp_headers = self._browser_client.generate_ws_headers()

        LOGGER.info(f"✓ ACBT session ready — console: {self.console_live_view_url}")

        # Patch the Playwright options with ACBT's CDP connection details
        playwright_options = self._init_kwargs.get(
            "playwright_options", self._init_args[0] if self._init_args else None
        )
        if not isinstance(playwright_options, PlaywrightInstanceOptions):
            raise TypeError(
                f"Expected PlaywrightInstanceOptions, got {type(playwright_options)}"
            )
        playwright_options.cdp_endpoint_url = cdp_endpoint_url
        playwright_options.cdp_headers = cdp_headers
        playwright_options.owns_context = False
        playwright_options.__post_init__()

        # Now initialize the parent with the patched options
        super().__init__(*self._init_args, **self._init_kwargs)
        super().start(**kwargs)

    def stop(self, **kwargs: Any) -> None:  # type: ignore[explicit-any]
        """Stop the Playwright actuator, then tear down the ACBT session.

        Args:
            **kwargs: Passed through to the parent stop().
        """
        try:
            super().stop(**kwargs)
        finally:
            if self._browser_context_manager is not None:
                try:
                    self._browser_context_manager.__exit__(None, None, None)
                    LOGGER.info("✓ ACBT session stopped")
                except Exception as e:
                    LOGGER.error(f"Failed to stop ACBT session: {e}")
                finally:
                    self._browser_client = None
                    self._browser_context_manager = None
