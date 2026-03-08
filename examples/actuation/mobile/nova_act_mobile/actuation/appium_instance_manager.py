"""Manages the lifecycle of an Appium WebDriver session.

Handles driver initialization, capability configuration, implicit waits,
video recording, and cleanup. Used internally by MobileActuator — not
intended for direct use.
"""

import base64
import os
from typing import Any

from appium import webdriver
from appium.webdriver.webdriver import WebDriver
from nova_act.types.errors import ClientNotStarted, StartFailed
from nova_act.util.logging import setup_logging
from selenium.common.exceptions import WebDriverException

from examples.actuation.mobile.nova_act_mobile.actuation.appium_instance_options import (
    AppiumInstanceOptions,
)
from examples.actuation.mobile.nova_act_mobile.platform import Platform

_LOGGER = setup_logging(__name__)


class AppiumInstanceManager:
    """RAII Manager for the Appium WebDriver.

    This class manages the lifecycle of an Appium WebDriver session,
    including initialization, configuration, and cleanup.
    """

    def __init__(self, options: AppiumInstanceOptions):
        """Initialize the Appium instance manager.

        Args:
            options: Configuration options for the Appium session.
        """
        self._options = options
        self._driver: WebDriver | None = None
        self._session_logs_directory: str | None = None

    @property
    def started(self) -> bool:
        """Check if the Appium driver is started."""
        return self._driver is not None

    def start(self, session_logs_directory: str | None = None) -> None:
        """Start and initialize the Appium driver.

        Args:
            session_logs_directory: Optional directory for session logs and recordings.

        Raises:
            StartFailed: If the driver fails to start or initialize.
        """
        if self._driver is not None:
            _LOGGER.warning("Appium driver already started")
            return

        if self._options.record_video and session_logs_directory is None:
            raise ValueError(
                "session_logs_directory required when record_video is True"
            )

        self._session_logs_directory = session_logs_directory

        try:
            _LOGGER.info(
                f"Starting Appium session for {self._options.platform} "
                f"device '{self._options.device_name}' "
                f"on server {self._options.appium_server_url}"
            )

            # Build capabilities
            capabilities = self._options.to_capabilities()

            # Add video recording capability if requested
            if self._options.record_video and session_logs_directory:
                # Platform-specific video recording
                if self._options.platform == Platform.ANDROID:
                    capabilities["appium:videoSize"] = "1280x720"
                elif self._options.platform == Platform.IOS:
                    capabilities["appium:videoType"] = "h264"
                    capabilities["appium:videoQuality"] = "medium"

            _LOGGER.debug(f"Appium capabilities: {capabilities}")

            # Create the driver
            self._driver = webdriver.Remote(  # type: ignore[attr-defined]
                command_executor=self._options.appium_server_url,
                options=self._create_driver_options(capabilities),
            )

            # Set implicit wait
            self._driver.implicitly_wait(1)

            _LOGGER.info(
                f"Appium session started successfully. Session ID: {self._driver.session_id}"
            )

        except WebDriverException as e:
            _LOGGER.exception(f"Failed to start Appium driver: {e}")
            self.stop()
            raise StartFailed(f"Failed to start Appium driver: {str(e)}") from e
        except Exception as e:
            _LOGGER.exception(f"Unexpected error starting Appium: {e}")
            self.stop()
            raise StartFailed(f"Failed to start Appium driver: {str(e)}") from e

    def _create_driver_options(self, capabilities: dict[str, Any]) -> Any:  # type: ignore[explicit-any]
        """Create platform-specific driver options.

        Args:
            capabilities: Appium capabilities dictionary.

        Returns:
            Platform-specific options object (UiAutomator2Options or XCUITestOptions).
        """
        if self._options.platform == Platform.ANDROID:
            from appium.options.android import (
                UiAutomator2Options,  # type: ignore[attr-defined]
            )

            options: Any = UiAutomator2Options()  # type: ignore[explicit-any]
        elif self._options.platform == Platform.IOS:
            from appium.options.ios import XCUITestOptions  # type: ignore[attr-defined]

            options = XCUITestOptions()
        else:
            raise ValueError(f"Unsupported platform: {self._options.platform}")

        # Load capabilities into options
        options.load_capabilities(capabilities)
        return options

    def stop(self) -> None:
        """Stop and cleanup the Appium driver."""
        if self._driver is not None:
            try:
                # Handle video recording cleanup
                if self._options.record_video and self._session_logs_directory:
                    self._save_recording()

                # Quit the driver session
                _LOGGER.info("Stopping Appium session")
                self._driver.quit()
            except Exception as e:
                _LOGGER.error(f"Error stopping Appium driver: {e}")
            finally:
                self._driver = None
                self._session_logs_directory = None

    def _save_recording(self) -> None:
        """Save the session recording to the logs directory."""
        if self._driver is None or self._session_logs_directory is None:
            return

        try:
            # Get the video recording from the session
            video_data = self._driver.stop_recording_screen()

            if video_data:
                # Decode and save the video
                video_path = os.path.join(
                    self._session_logs_directory, "session_recording.mp4"
                )
                with open(video_path, "wb") as f:
                    f.write(base64.b64decode(video_data))
                _LOGGER.info(f"Session recording saved to {video_path}")
        except Exception as e:
            _LOGGER.warning(f"Failed to save session recording: {e}")

    @property
    def driver(self) -> WebDriver:
        """Get the active Appium WebDriver instance.

        Returns:
            The active WebDriver instance.

        Raises:
            ClientNotStarted: If the driver has not been started.
        """
        if self._driver is None:
            raise ClientNotStarted("Appium driver not started, call start() first")
        return self._driver

    def get_driver(self) -> WebDriver:
        """Get the active Appium WebDriver instance.

        Returns:
            The active WebDriver instance.

        Raises:
            ClientNotStarted: If the driver has not been started.
        """
        return self.driver
