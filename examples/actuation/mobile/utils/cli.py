"""CLI configuration using Pydantic Settings with CLI parsing."""

import os
from typing import cast

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from examples.actuation.mobile.nova_act_mobile.app import MobileAppConfig
from examples.actuation.mobile.nova_act_mobile.device_farm import (
    DeviceFarmConfig,
    DeviceFarmUploadConfig,
)
from examples.actuation.mobile.nova_act_mobile.platform import Platform


class CliArgs(BaseSettings):
    """Command-line configuration for Nova Act mobile testing.

    Running with no arguments uses the AWS Device Farm sample app by default.
    """

    model_config = SettingsConfigDict(cli_parse_args=True)

    # Device Farm arguments
    project_arn: str | None = Field(
        None, description="Device Farm project ARN (overrides auto-discovery)"
    )
    device_arn: str | None = Field(
        None, description="Device Farm device ARN (overrides auto-discovery)"
    )

    # Pre-existing upload ARN (skips upload entirely)
    app_arn: str | None = Field(
        None,
        description="Existing Device Farm upload ARN to use directly (skips upload). "
        "Defaults to the AWS Device Farm sample app when no other app args are provided.",
    )

    # Platform (can be explicitly provided or auto-detected)
    platform: Platform | None = Field(
        None,
        description="Platform to test (Android or iOS). Defaults to Android when using default app.",
    )

    # App identification
    app_name: str | None = Field(
        None,
        description="Display name used for Device Farm upload filename and session naming.",
    )

    # App file path
    app_path: str | None = Field(
        None, description="Path to app file (.apk for Android, .ipa for iOS)"
    )

    # Force app upload (skip reuse of existing upload)
    force_app_upload: bool = Field(
        False,
        description="Force upload even if app with same filename already exists in Device Farm",
    )

    # Android-specific
    package: str | None = Field(
        None,
        description="Android package name (e.g., com.example.app).",
    )
    activity: str | None = Field(
        None,
        description="Android main activity (e.g., .MainActivity).",
    )

    # iOS-specific
    bundle_id: str | None = Field(
        None,
        description="iOS bundle ID (e.g., com.apple.mobilesafari).",
    )

    @field_validator("app_path")
    @classmethod
    def validate_app_path_exists(cls, v: str | None) -> str | None:
        """Validate app file exists if path provided."""
        if v and not os.path.exists(v):
            raise ValueError(f"App file not found: {v}")
        return v

    @model_validator(mode="after")
    def validate_and_set_defaults(self):
        """Detect platform, apply defaults, and validate requirements."""
        using_default_app = (
            not self.app_path
            and not self.app_arn
            and not self.package
            and not self.bundle_id
        )

        # Apply Device Farm sample app defaults when nothing is specified
        if using_default_app:
            self.platform = Platform.ANDROID
            self.package = DeviceFarmConfig.DEFAULT_APP_PACKAGE
            self.activity = DeviceFarmConfig.DEFAULT_APP_ACTIVITY
            self.app_name = DeviceFarmConfig.DEFAULT_APP_NAME
            self.app_path = DeviceFarmConfig.DEFAULT_APP_PATH
            if not os.path.exists(self.app_path):
                raise ValueError(
                    f"Default sample app not found at {self.app_path}.\n"
                    "Build it from: https://github.com/aws-samples/aws-device-farm-sample-app-for-android"
                )
            return self

        # Auto-detect platform from provided args
        if not self.platform:
            if self.bundle_id:
                self.platform = Platform.IOS
            elif self.package or self.activity:
                self.platform = Platform.ANDROID
            else:
                raise ValueError(
                    "Cannot detect platform. Provide either:\n"
                    "  - --package and --activity (Android)\n"
                    "  - --bundle-id (iOS)\n"
                    "  - Or run with no arguments to use the default Device Farm sample app"
                )

        # Validate platform-specific required fields
        if self.platform == Platform.ANDROID:
            if not self.package:
                raise ValueError("--package is required for Android")
            if not self.activity:
                raise ValueError("--activity is required for Android")
        elif self.platform == Platform.IOS:
            if not self.bundle_id:
                raise ValueError("--bundle-id is required for iOS")

        # Set app_name default
        if not self.app_name:
            if self.app_path:
                self.app_name = os.path.splitext(os.path.basename(self.app_path))[0]
            else:
                self.app_name = (
                    self.package
                    if self.platform == Platform.ANDROID
                    else self.bundle_id
                )

        return self

    def to_app_config(self) -> MobileAppConfig:
        """Convert CLI args to a MobileAppConfig (app identity only)."""
        if self.platform == Platform.ANDROID:
            return MobileAppConfig.for_android(
                app_package=cast(str, self.package),
                app_activity=cast(str, self.activity),
            )
        elif self.platform == Platform.IOS:
            return MobileAppConfig.for_ios(
                bundle_id=cast(str, self.bundle_id),
            )
        raise ValueError(f"Unsupported platform: {self.platform}")

    def to_upload_config(self) -> DeviceFarmUploadConfig | None:
        """Convert CLI args to a DeviceFarmUploadConfig, or None if no upload needed."""
        if not self.app_path and not self.app_arn:
            return None
        return DeviceFarmUploadConfig(
            app_name=cast(str, self.app_name),
            app_path=self.app_path,
            app_arn=self.app_arn,
            force_upload=self.force_app_upload,
        )
