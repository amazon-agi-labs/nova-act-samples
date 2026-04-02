"""Mobile keyboard input implementation."""

import time
from typing import Literal

from appium.webdriver.webdriver import WebDriver
from nova_act.types.api.step import BboxTLBR
from nova_act.util.logging import setup_logging

from examples.actuation.mobile.nova_act_mobile.actuation.util import get_platform
from examples.actuation.mobile.nova_act_mobile.actuation.util.mobile_click import (
    mobile_click,
)

_LOGGER = setup_logging(__name__)


def _press_enter(driver: WebDriver) -> None:
    """Press Enter/Return using platform-native actions.

    Avoids ``Keys.RETURN`` which injects a literal Unicode character
    (U+E006) into the text field on many mobile WebDrivers.

    iOS: sends ``\\n`` via the active element, which XCUITest interprets
    as the Return key.
    Android: uses ``press_keycode(66)`` (KEYCODE_ENTER).
    """
    if get_platform(driver) == "ios":
        driver.switch_to.active_element.send_keys("\n")
    else:
        driver.press_keycode(66)
    _LOGGER.debug("Pressed Enter (native)")


def _select_all_and_delete(driver: WebDriver) -> None:
    """Clear the focused field.

    iOS: uses ``active_element.clear()`` which is reliable under XCUITest.
    ``press_keycode`` is not available on iOS (no KeyEvent system), and
    WDA's ``mobile: pressButton`` only supports home, volumeUp, and
    volumeDown — so ``.clear()`` is the best option.

    Android: uses Ctrl+A → Delete via key codes instead of
    ``active_element.clear()``, which can behave inconsistently across
    apps and input field types (sometimes failing to clear, losing focus,
    or dismissing the keyboard).
    """
    try:
        if get_platform(driver) == "ios":
            driver.switch_to.active_element.clear()
        else:
            # Android: Ctrl+A (KEYCODE_A=29 with META_CTRL_ON=0x1000)
            driver.press_keycode(29, metastate=0x1000)
            time.sleep(0.1)
            # KEYCODE_DEL = 67 (backspace)
            driver.press_keycode(67)
        _LOGGER.debug("Cleared field")
    except Exception as e:
        _LOGGER.debug(f"Field clear failed: {e}")


def mobile_type(
    bbox: BboxTLBR,
    value: str,
    driver: WebDriver,
    press_enter: Literal["pressEnter"] | None = None,
) -> None:
    """Type text into a mobile element at the specified bounding box.

    This function first taps the element to focus it, clears existing text,
    sends the new text, and optionally presses Enter/Return.

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

        # Clear existing text
        _select_all_and_delete(driver)

        # Send the text
        active_element.send_keys(value)

        _LOGGER.debug(f"Successfully typed {len(value)} characters")

        # Press Enter if requested
        if press_enter == "pressEnter":
            _press_enter(driver)

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
    if get_platform(driver) != "ios":
        raise RuntimeError(
            "No typing fallback available for Android — active_element.send_keys() already failed"
        )

    try:
        driver.execute_script("mobile: type", {"text": value})
        if press_enter == "pressEnter":
            _press_enter(driver)
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
