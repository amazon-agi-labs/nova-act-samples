"""Resolve bounding box coordinates to DOM elements.

Demonstrates how to build a custom actuator that resolves the DOM element at
the coordinates Nova Act interacts with. The actuator overrides `agent_click`
to perform the default Playwright click, then extracts the element's tag,
id, class, text content, and attributes from the bounding box center point.

Usage:
python -m examples.element_resolver.main
"""

import fire
from nova_act import DefaultNovaLocalBrowserActuator, NovaAct, workflow
from nova_act.tools.browser.default.util.bbox_parser import (
    bounding_box_to_point,
    parse_bbox_string,
)
from nova_act.tools.browser.default.util.element_helpers import get_element_at_point
from nova_act.tools.browser.interface.types.click_types import ClickOptions

from examples.nova_act_client import NovaActClient
from examples.utils import get_logger

LOGGER = get_logger(__name__)


class ElementResolverActuator(DefaultNovaLocalBrowserActuator):
    """Custom actuator that logs DOM element info after each click."""

    def agent_click(
        self,
        box: str,
        click_type: str | None = None,
        click_options: ClickOptions | None = None,
    ):
        # Execute default Playwright actuation
        super().agent_click(box, click_type, click_options)

        # Get the center point of the bounding box
        bbox = parse_bbox_string(box)
        point = bounding_box_to_point(bbox)

        # Find the element at the point
        element_info = get_element_at_point(
            self._playwright_manager.main_page, point["x"], point["y"]
        )

        if element_info:
            element_id = element_info.get("id")
            tag_name = element_info.get("tagName", "")
            class_name = element_info.get("className")
            text_content = element_info.get("textContent")
            attributes = element_info.get("attributes", {})

            LOGGER.info(
                f"✓ Clicked element: tag={tag_name}, id={element_id}, "
                f"class={class_name}, text={text_content}, attrs={attributes}"
            )

        return None


@workflow(**NovaActClient.get_workflow_kwargs())
def main() -> None:
    with NovaAct(
        starting_page="https://nova.amazon.com/act/gym/next-dot",
        actuator=ElementResolverActuator,
    ) as nova:
        nova.act("Click on Destinations")


if __name__ == "__main__":
    fire.Fire(main)
