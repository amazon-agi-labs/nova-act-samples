"""Scroll and extract: gather values that span content taller than the viewport.

When the values you want are spread across content taller than the viewport,
you don't need to fit them all on screen at once. Give a single ``act_get`` a
prompt and a schema with one field per value — the agent works through the
content, collects each value, and returns them together. This is a useful
pattern for large extraction tasks or QA automation, any time you want to pull
or validate multiple values in one call when they aren't all visible at the
same time.

Usage:
python -m examples.actuation.browser.scroll_extract
"""

from pathlib import Path

import fire
from nova_act import NovaAct, SecurityOptions, workflow
from pydantic import BaseModel

from examples.nova_act_client import NovaActClient
from examples.utils import get_logger

LOGGER = get_logger(__name__)

HTML_FILE_PATH = str(Path(__file__).parent / "static" / "scroll_extract.html")


class TrailInfo(BaseModel):
    """Values spread top-to-bottom across a page taller than the viewport."""

    trail_name: str
    distance: str
    trail_status: str


@workflow(**NovaActClient.get_workflow_kwargs())
def main() -> None:
    """Extract every field from a page that spans more than one viewport."""
    LOGGER.info("🚀 Starting scroll and extract example...")

    with NovaAct(
        starting_page=f"file://{HTML_FILE_PATH}",
        ignore_https_errors=True,
        security_options=SecurityOptions(allowed_file_open_paths=[HTML_FILE_PATH]),
    ) as nova:
        # A single act_get gathers every value, even though a tall map graphic
        # separates the fields so they cannot all be on screen at once.
        info = TrailInfo.model_validate(
            nova.act_get(
                "Extract the trail details. A large map separates the fields on a page "
                "that is taller than the screen, so scroll from top to bottom until you "
                "have seen every one.",
                schema=TrailInfo.model_json_schema(),
            ).parsed_response
        )
        LOGGER.info(f"Extracted trail info: {info}\n")

    LOGGER.info("✓ Scroll and extract flow complete")


if __name__ == "__main__":
    fire.Fire(main)
