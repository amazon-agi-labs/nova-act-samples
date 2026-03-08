"""Mobile keyboard input implementation."""

import time
from typing import Literal

from appium.webdriver.webdriver import WebDriver
from nova_act.types.api.step import BboxTLBR
from nova_act.util.logging import setup_logging
from selenium.webdriver.common.keys import Keys

from examples.actuation.mobile.nova_act_mobile.actuation.util.mobile_click import (
    mobile_click,
)

_LOGGER = setup_logging(__name__)


def mobile_type(
    bbox: BboxTLBR,
    value: str,
    driver: WebDriver,
    press_enter: Literal["pressEnter"] | None = None,
) -> None:
    """Type text into a mobile element at the specified bounding box.

    This function first taps the element to focus it, then sends the text,
    and optionally presses Enter/Return.

    Args:
        bbox: Bounding box of the target input element (BboxTLBR).
        value: Text to type into the element.
        driver: Appium WebDriver instance.
        press_enter: If "pressEnter", presses Enter/Return after typing.

    Raises:
        ValueError: If the element cannot be focused or text cannot be sent.
    """
    _LOGGER.debug(f"Mobile type: '{value}' into element at bbox {bbox}")

    # First, tap the element to focus it and bring up the keyboard
    mobile_click(bbox, driver, click_type="left")

    # Small delay to allow keyboard to appear

    time.sleep(0.3)

    # Get the currently active element (should be the focused input)
    try:
        active_element = driver.switch_to.active_element

        # Clear existing text if any (optional - can be made configurable)
        # active_element.clear()

        # Send the text
        active_element.send_keys(value)

        _LOGGER.debug(f"Successfully typed {len(value)} characters")

        # Press Enter if requested
        if press_enter == "pressEnter":
            active_element.send_keys(Keys.RETURN)
            _LOGGER.debug("Pressed Enter key")

    except Exception as e:
        _LOGGER.debug(f"Primary typing failed, trying fallback: {e}")
        _type_via_coordinate_fallback(driver, value, press_enter)


def _type_via_coordinate_fallback(
    driver: WebDriver,
    value: str,
    press_enter: Literal["pressEnter"] | None = None,
) -> None:
    """Fallback method to type text using platform-specific commands.

    Uses `mobile: type` on iOS (XCUITest). On Android there is no equivalent
    fallback — raises immediately so the caller surfaces the original error.

    Args:
        driver: Appium WebDriver instance.
        value: Text to type.
        press_enter: Whether to press Enter after typing.

    Raises:
        RuntimeError: If fallback typing fails or platform is Android.
    """
    platform = driver.capabilities.get("platformName", "").lower()
    if "ios" not in platform:
        raise RuntimeError(
            "No typing fallback available for Android — active_element.send_keys() already failed"
        )

    try:
        driver.execute_script("mobile: type", {"text": value})
        if press_enter == "pressEnter":
            driver.execute_script("mobile: type", {"text": "\n"})
    except Exception as e:
        raise RuntimeError(f"iOS mobile: type fallback failed: {e}") from e


def hide_keyboard(driver: WebDriver) -> None:
    """Hide the mobile keyboard if it's currently visible.

    Args:
        driver: Appium WebDriver instance.
    """
    try:
        driver.hide_keyboard()
        _LOGGER.debug("Keyboard hidden")
    except Exception as e:
        # Keyboard might already be hidden, or method not supported
        _LOGGER.debug(f"Could not hide keyboard (may already be hidden): {e}")


def is_keyboard_shown(driver: WebDriver) -> bool:
    """Check if the mobile keyboard is currently visible.

    Args:
        driver: Appium WebDriver instance.

    Returns:
        True if keyboard is visible, False otherwise.
    """
    try:
        return driver.is_keyboard_shown()
    except Exception as e:
        _LOGGER.debug(f"Could not determine keyboard state: {e}")
        return False
