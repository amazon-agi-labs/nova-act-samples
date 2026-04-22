"""NovaActMobile — NovaAct extension for mobile automation."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal, Self

from nova_act import NovaAct, Workflow

from examples.actuation.mobile.nova_act_mobile.actuation.appium_driver_manager import (
    AppiumDriverManagerBase,
)
from examples.actuation.mobile.nova_act_mobile.actuation.appium_instance_options import (
    AppiumInstanceOptions,
)
from examples.actuation.mobile.nova_act_mobile.actuation.mobile_actuator import (
    MobileActuator,
)
from examples.actuation.mobile.nova_act_mobile.actuation.util.mobile_type import (
    _press_enter,
    _select_all_and_delete,
)
from examples.actuation.mobile.nova_act_mobile.app import MobileAppConfig
from examples.actuation.mobile.nova_act_mobile.device_farm import DeviceFarmUploadConfig

if TYPE_CHECKING:
    from appium.webdriver.webdriver import WebDriver


class NovaActMobile(NovaAct):
    """NovaAct extension for automating mobile apps on Android and iOS.

    Provide ``app_package`` + ``app_activity`` for Android, or ``bundle_id``
    for iOS. Supports Device Farm and local Appium modes.

    Args:
        app_package: Android app package (e.g. ``"com.example.app"``).
        app_activity: Android launch activity (e.g. ``".MainActivity"``).
        bundle_id: iOS bundle identifier.
        app_path: Path to ``.apk`` / ``.ipa`` for Device Farm upload.
        deep_link: Deep link URL to open at launch (e.g. ``"myapp://screen"``).
        additional_capabilities: Extra Appium capabilities merged into the session
            (e.g. ``{"appium:autoLaunch": False, "appium:noReset": True}``).
        mode: Execution mode — ``"device-farm"`` (default) or ``"local"``.
        device_name: Appium device name (local mode, default ``"emulator-5554"``).
        platform_version: OS version string (local mode).
        appium_server_url: Appium server URL (local mode).
        project_arn: Device Farm project ARN (auto-discovered if None).
        device_arn: Device Farm device ARN (auto-discovered if None).
        force_upload: Force re-upload app to Device Farm.
        workflow: Nova Act Workflow instance.
        **kwargs: Passed through to ``NovaAct.__init__``.

    Example (Android, Device Farm)::

        with NovaActMobile(app_package="com.example.app", app_activity=".Main") as nova:
            nova.act("Tap the login button")

    Example (iOS, Device Farm)::

        with NovaActMobile(bundle_id="com.example.app") as nova:
            nova.act("Tap the login button")
    """

    def __init__(
        self,
        *,
        # App identity — provide (app_package + app_activity) OR bundle_id
        app_package: str | None = None,
        app_activity: str | None = None,
        bundle_id: str | None = None,
        app_path: str | None = None,
        # Navigation
        deep_link: str | None = None,
        additional_capabilities: dict[str, Any] | None = None,
        # Mode
        mode: Literal["device-farm", "local"] = "device-farm",
        # Local Appium options
        device_name: str = "emulator-5554",
        platform_version: str | None = None,
        appium_server_url: str = "http://127.0.0.1:4723",
        # Device Farm options
        project_arn: str | None = None,
        device_arn: str | None = None,
        force_upload: bool = False,
        # NovaAct options
        workflow: Workflow | None = None,
        **kwargs: Any,
    ) -> None:
        # Build MobileAppConfig from flat args
        if app_package:
            app = MobileAppConfig.for_android(
                app_package=app_package,
                app_activity=app_activity or "",
            )
        elif bundle_id:
            app = MobileAppConfig.for_ios(bundle_id=bundle_id)
        else:
            raise ValueError("Provide app_package (Android) or bundle_id (iOS).")

        # Build actuator
        if mode == "device-farm":
            from examples.actuation.mobile.nova_act_mobile.actuation.device_farm_actuator import (
                DeviceFarmActuator,
            )

            upload_config = None
            if app_path:
                upload_config = DeviceFarmUploadConfig(
                    app_name=Path(app_path).stem,
                    app_path=app_path,
                    force_upload=force_upload,
                )

            actuator = DeviceFarmActuator(
                app_config=app,
                upload_config=upload_config,
                project_arn=project_arn,
                device_arn=device_arn,
                additional_capabilities=additional_capabilities,
            )
        elif mode == "local":
            options = AppiumInstanceOptions(
                platform=app.platform,
                device_name=device_name,
                platform_version=platform_version,
                appium_server_url=appium_server_url,
                app_package=app.app_package,
                app_activity=app.app_activity,
                bundle_id=app.bundle_id,
                app_path=app_path,
                additional_capabilities=additional_capabilities,
            )
            actuator = MobileActuator(appium_options=options)
        else:
            raise ValueError(f"Unknown mode: {mode!r}. Use 'device-farm' or 'local'.")

        # Sensible mobile defaults
        kwargs.setdefault("ignore_https_errors", True)
        kwargs.setdefault("ignore_screen_dims_check", True)

        super().__init__(
            starting_page=MobileActuator.app_url(
                app.app_identifier,
                deep_link=deep_link,
            ),
            actuator=actuator,
            workflow=workflow,
            **kwargs,
        )

    def __enter__(self) -> Self:
        super().__enter__()
        return self

    # ── Driver access ───────────────────────────────────────────────────

    @property
    def driver(self) -> WebDriver:
        """The Appium WebDriver for the current session."""
        if not isinstance(self._actuator, AppiumDriverManagerBase):
            raise TypeError(
                "NovaActMobile requires a mobile actuator. "
                "Use NovaAct with nova.page for browser actuators."
            )
        return self._actuator.driver

    @property  # type: ignore[override]
    def page(self):  # noqa: ANN201
        """Not available on mobile — use ``nova.driver`` instead."""
        raise AttributeError(
            "nova.page is not available with a mobile actuator. "
            "Use nova.driver, nova.type_text(), or nova.press_enter()."
        )

    # ── Mobile helpers ──────────────────────────────────────────────────

    def type_text(self, text: str) -> None:
        """Type text into the currently focused element."""
        self.driver.switch_to.active_element.send_keys(text)

    def press_enter(self) -> None:
        """Press Enter/Return using platform-native key events."""
        _press_enter(self.driver)

    def clear_focused(self) -> None:
        """Clear the currently focused field (select-all + delete)."""
        _select_all_and_delete(self.driver)
