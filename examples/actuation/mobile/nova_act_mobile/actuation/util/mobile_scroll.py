"""Mobile scroll/swipe action implementation using W3C Actions API.

Uses the W3C WebDriver Actions API for cross-platform scroll gestures.
This is the spec-compliant approach that works on both Android (UiAutomator2)
and iOS (XCUITest) — both drivers translate W3C pointer actions into native
platform gestures.
"""

from appium.webdriver.webdriver import WebDriver
from nova_act.tools.browser.interface.types.scroll_types import ScrollDirection
from nova_act.types.api.step import BboxTLBR
from nova_act.util.logging import setup_logging
from selenium.webdriver.common.actions import interaction
from selenium.webdriver.common.actions.action_builder import ActionBuilder
from selenium.webdriver.common.actions.pointer_input import PointerInput

_LOGGER = setup_logging(__name__)

# Default scroll distances as percentage of screen size
_DEFAULT_SCROLL_PERCENTAGE = 0.5
_DEFAULT_HORIZONTAL_SCROLL_PERCENTAGE = 0.8

# Safe margin (in pixels) to keep swipe start/end away from screen edges
# where status bars, navigation bars, or system gestures can intercept touches.
_EDGE_MARGIN = 100
_HORIZONTAL_EDGE_MARGIN = 20

# Default swipe duration in milliseconds
_DEFAULT_SWIPE_DURATION_MS = 500

# Number of intermediate points for the swipe gesture. More steps produce a
# smoother path that the OS is more likely to recognise as a deliberate scroll.
_SWIPE_STEPS = 5


def mobile_scroll(
    driver: WebDriver,
    direction: ScrollDirection,
    bbox: BboxTLBR,
    value: float | None = None,
) -> None:
    """Perform a swipe gesture within the specified bounding box.

    Translates a logical scroll direction into a W3C Actions pointer swipe.
    The gesture is constrained to stay within *bbox* and respects a safe edge
    margin to avoid triggering OS-level system gestures.

    Args:
        driver: Appium WebDriver instance.
        direction: Direction to scroll (up, down, left, right).
        bbox: Bounding box defining the scrollable area (BboxTLBR).
        value: Optional scroll amount in pixels. When ``None`` the scroll
               distance defaults to a percentage of the element size.
    """
    # Calculate center and boundaries of the bbox
    center_x = (bbox.left + bbox.right) / 2
    center_y = (bbox.top + bbox.bottom) / 2

    # Calculate width and height from BboxTLBR
    width = bbox.right - bbox.left
    height = bbox.bottom - bbox.top

    # Determine scroll distance
    # Cap at screen size so a single scroll never exceeds one screenful
    try:
        window_size = driver.get_window_size()
        max_vertical = window_size["height"]
        max_horizontal = window_size["width"]
    except Exception:
        # Fallback to bbox dimensions if window size unavailable
        max_vertical = height
        max_horizontal = width

    if value is not None:
        scroll_distance = abs(value)
    else:
        # Use percentage of element size, capped to screen size
        if direction in ("up", "down"):
            scroll_distance = min(height * _DEFAULT_SCROLL_PERCENTAGE, max_vertical)
        else:  # left or right
            scroll_distance = min(
                width * _DEFAULT_HORIZONTAL_SCROLL_PERCENTAGE, max_horizontal
            )

    _LOGGER.debug(
        f"Mobile scroll {direction} - bbox: top={bbox.top}, left={bbox.left}, "
        f"bottom={bbox.bottom}, right={bbox.right} (w={width:.0f}, h={height:.0f}), "
        f"distance={scroll_distance:.0f}px"
    )

    # Calculate start and end points for the swipe
    start_x, start_y, end_x, end_y = _calculate_swipe_coordinates(
        direction=direction,
        center_x=int(center_x),
        center_y=int(center_y),
        distance=int(scroll_distance),
        bbox=bbox,
    )

    _LOGGER.debug(f"Swipe coordinates: ({start_x},{start_y}) → ({end_x},{end_y})")

    # Perform the swipe gesture
    _perform_swipe(driver, start_x, start_y, end_x, end_y)


def _calculate_swipe_coordinates(
    direction: ScrollDirection,
    center_x: int,
    center_y: int,
    distance: int,
    bbox: BboxTLBR,
) -> tuple[int, int, int, int]:
    """Calculate start and end coordinates for a swipe gesture.

    The finger movement is the *inverse* of the scroll direction: scrolling
    "down" means swiping the finger upward so that content below is revealed.

    Args:
        direction: Direction to scroll.
        center_x: X coordinate of the element center.
        center_y: Y coordinate of the element center.
        distance: Distance to scroll in pixels.
        bbox: Bounding box to constrain the swipe within (BboxTLBR).

    Returns:
        Tuple of (start_x, start_y, end_x, end_y) coordinates.

    Raises:
        ValueError: If direction is not supported.
    """
    # Calculate width and height
    height = bbox.bottom - bbox.top
    width = bbox.right - bbox.left

    if direction == "down":
        # To scroll down (reveal content below), swipe UP (from bottom to top)
        start_x = center_x
        start_y = min(center_y + distance // 2, int(bbox.top + height - _EDGE_MARGIN))
        end_x = center_x
        end_y = max(center_y - distance // 2, int(bbox.top + _EDGE_MARGIN))

    elif direction == "up":
        # To scroll up (reveal content above), swipe DOWN (from top to bottom)
        start_x = center_x
        start_y = max(center_y - distance // 2, int(bbox.top + _EDGE_MARGIN))
        end_x = center_x
        end_y = min(center_y + distance // 2, int(bbox.top + height - _EDGE_MARGIN))

    elif direction == "right":
        # To scroll right (reveal content on right), swipe LEFT (from right to left)
        start_x = min(
            center_x + distance // 2, int(bbox.left + width - _HORIZONTAL_EDGE_MARGIN)
        )
        start_y = center_y
        end_x = max(center_x - distance // 2, int(bbox.left + _HORIZONTAL_EDGE_MARGIN))
        end_y = center_y

    elif direction == "left":
        # To scroll left (reveal content on left), swipe RIGHT (from left to right)
        start_x = max(
            center_x - distance // 2, int(bbox.left + _HORIZONTAL_EDGE_MARGIN)
        )
        start_y = center_y
        end_x = min(
            center_x + distance // 2, int(bbox.left + width - _HORIZONTAL_EDGE_MARGIN)
        )
        end_y = center_y

    else:
        raise ValueError(f"Unsupported scroll direction: {direction}")

    return start_x, start_y, end_x, end_y


def _perform_swipe(
    driver: WebDriver,
    start_x: int,
    start_y: int,
    end_x: int,
    end_y: int,
    duration_ms: int = _DEFAULT_SWIPE_DURATION_MS,
) -> None:
    """Perform a swipe using the W3C Actions API.

    Constructs a touch pointer sequence: move to start → press → drag through
    intermediate points → release.  Intermediate points produce a smooth path
    that both Android and iOS reliably interpret as a scroll gesture.

    Args:
        driver: Appium WebDriver instance.
        start_x: Starting X coordinate.
        start_y: Starting Y coordinate.
        end_x: Ending X coordinate.
        end_y: Ending Y coordinate.
        duration_ms: Duration of the swipe in milliseconds.
    """
    _LOGGER.debug(
        f"W3C Actions swipe: ({start_x},{start_y}) → ({end_x},{end_y}), "
        f"duration={duration_ms}ms"
    )

    finger_input = PointerInput(interaction.POINTER_TOUCH, "finger")
    actions = ActionBuilder(driver, mouse=finger_input)

    # Move to start, press down
    actions.pointer_action.move_to_location(start_x, start_y)
    actions.pointer_action.pointer_down()
    actions.pointer_action.pause(0.1)  # Let the OS register the touch

    # Drag through intermediate points for a smooth, recognisable gesture
    duration_per_step = (duration_ms / 1000.0) / _SWIPE_STEPS
    for i in range(1, _SWIPE_STEPS + 1):
        intermediate_x = start_x + (end_x - start_x) * i // _SWIPE_STEPS
        intermediate_y = start_y + (end_y - start_y) * i // _SWIPE_STEPS
        actions.pointer_action.move_to_location(intermediate_x, intermediate_y)
        actions.pointer_action.pause(duration_per_step)

    # Release
    actions.pointer_action.pointer_up()

    actions.perform()
    _LOGGER.debug("W3C Actions swipe completed")
