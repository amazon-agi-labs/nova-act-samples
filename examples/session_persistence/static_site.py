"""Playwright route handler that serves the built-in demo site over a fake origin.

Registers a route on the browser context so that requests to STATIC_PAGE_ORIGIN
are fulfilled from the local static/login_dashboard.html file. This gives cookies
and localStorage a proper origin for realistic session persistence behavior,
and works over CDP for both local and remote (AgentCore) browsers.
"""

from pathlib import Path

from playwright.sync_api import Page, Route

STATIC_PAGE_ORIGIN = "https://app.local"
"""Fake origin used for cookie and localStorage scoping."""

_HTML_PATH = Path(__file__).parent / "static" / "login_dashboard.html"


def _serve_html(route: Route) -> None:
    """Fulfill any request under the fake origin with the static HTML page."""
    route.fulfill(body=_HTML_PATH.read_bytes(), content_type="text/html")


def setup_static_page(page: Page) -> str:
    """Register a Playwright route that serves the built-in demo site.

    Intercepts all requests to ``STATIC_PAGE_ORIGIN`` and responds with
    the static login_dashboard.html file. Call ``page.goto()`` with the
    returned URL after this function to load the page.

    Args:
        page: Playwright page to register the route on.

    Returns:
        The URL to navigate to (``STATIC_PAGE_ORIGIN/``).
    """
    page.context.route(f"{STATIC_PAGE_ORIGIN}/**", _serve_html)
    return f"{STATIC_PAGE_ORIGIN}/"
