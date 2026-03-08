"""Extract bounding box coordinates from static images using Nova Act.

Leverages Nova Act's built-in image understanding and bounding box generation
to locate UI elements in static images without browser interaction. A custom
`ImageActuator` swaps the browser screenshot in each observation with a provided
image, letting Nova Act apply the same visual grounding it uses for web pages
to any arbitrary image.

Usage:
python -m examples.bbox_locator.main
"""

import base64
from io import BytesIO
from pathlib import Path

import fire
from nova_act import STRING_SCHEMA, NovaAct, workflow
from nova_act.tools.browser.default.default_nova_local_browser_actuator import (
    DefaultNovaLocalBrowserActuator,
)
from nova_act.tools.browser.default.util.bbox_parser import parse_bbox_string
from nova_act.tools.browser.interface.browser import (
    BrowserObservation,
)
from nova_act.types.api.step import BboxTLBR
from PIL import Image, ImageDraw

from examples.nova_act_client import NovaActClient
from examples.utils import get_logger

LOGGER = get_logger(__name__)


class ImageActuator(DefaultNovaLocalBrowserActuator):
    """
    Custom actuator that overrides take_observation() to replace browser screenshots with a static image.

    Enables Nova Act to extract bounding boxes from images without browser interaction.
    Set ImageActuator.image_path before passing this class to NovaAct.
    """

    image_path: Path | None = None

    def take_observation(self) -> BrowserObservation:
        if ImageActuator.image_path is None:
            raise ValueError("ImageActuator.image_path must be set before use")

        # Take the standard observation
        observation = super().take_observation()

        # Load image and override observation with its data
        # Load image, convert to RGB (drops alpha channel for JPEG compatibility),
        # and encode as JPEG for the SDK's internal run_info_compiler.
        image = Image.open(ImageActuator.image_path).convert("RGB")
        width, height = image.size

        buffer = BytesIO()
        image.save(buffer, format="JPEG")
        image_data = buffer.getvalue()

        # Update observation dimensions to match image
        observation["browserDimensions"] = {
            "windowWidth": width,
            "windowHeight": height,
            "scrollWidth": width,
            "scrollHeight": height,
            "scrollLeft": 0,
            "scrollTop": 0,
        }

        # Replace observation screenshot with image
        image_base64 = base64.b64encode(image_data).decode("utf-8")
        observation["screenshotBase64"] = f"data:image/jpeg;base64,{image_base64}"

        return observation


SCRIPT_DIR = Path(__file__).parent.absolute()


def draw_bounding_boxes(image_path: Path, bbox: BboxTLBR) -> None:
    """Draws bounding boxes on image to validate accuracy."""

    with Image.open(image_path) as img:
        draw = ImageDraw.Draw(img)
        draw.rectangle(
            [bbox.left, bbox.top, bbox.right, bbox.bottom], outline="red", width=3
        )
        output_path = SCRIPT_DIR / f"output{image_path.suffix}"
        img.save(output_path)


@workflow(**NovaActClient.get_workflow_kwargs())
def main() -> None:
    """Extract bounding boxes from a static image."""

    ImageActuator.image_path = SCRIPT_DIR / "input.png"

    with NovaAct(
        actuator=ImageActuator,
        starting_page="about:blank",
        ignore_screen_dims_check=True,
        headless=True,
    ) as nova:
        # Extract the bounding box
        result = nova.act_get(
            "Return the bbox of the Pay Bill button",
            schema=STRING_SCHEMA,  # bbox extraction as a string is more reliable than JSON
        )
        # Parse the string response into a bounding box object
        bbox_str = str(result.parsed_response)
        bbox: BboxTLBR = parse_bbox_string(bbox_str)

    LOGGER.info(f"✓ Got bounding box: {bbox}")
    # Draw the bounding box on the image to validate accuracy
    draw_bounding_boxes(ImageActuator.image_path, bbox)


if __name__ == "__main__":
    fire.Fire(main)
