# Nova Act Mobile Automation Package Example

Mobile actuation package for Nova Act on iOS and Android. Provides Appium-based actuators that implement the Nova Act `BrowserActuatorBase` interface, AWS Device Farm integration for remote device provisioning, and `NovaActMobile` — a convenience class that handles platform detection and actuator setup from flat constructor arguments.

## Structure

```
nova_act_mobile/
├── nova_act_mobile.py  # NovaActMobile convenience class
├── platform.py         # Platform enum (Android / iOS)
├── actuation/          # Mobile actuator implementations for Appium and Device Farm
├── app/                # Infrastructure-agnostic mobile app config and sample mobile app
└── device_farm/        # AWS Device Farm client and upload config
```

## Key Classes

### `NovaActMobile`

Extends `NovaAct` with a mobile-first constructor. Provide `app_package` + `app_activity` for Android, or `bundle_id` for iOS. Supports `"device-farm"` (default) and `"local"` modes. See [`nova_act_mobile.py`](nova_act_mobile.py).

#### Device Farm (default)

```python
# Android
with NovaActMobile(
    app_package="com.example.app",
    app_activity=".MainActivity",
    app_path="path/to/app.apk",
) as nova:
    nova.act("Tap the login button")
```

```python
# iOS
with NovaActMobile(
    bundle_id="com.example.app",
    app_path="path/to/app.ipa",
) as nova:
    nova.act("Tap the login button")
```

#### Local Appium

```python
# Android
with NovaActMobile(
    app_package="com.example.app",
    app_activity=".MainActivity",
    mode="local",
    device_name="emulator-5554",
    platform_version="15",
) as nova:
    nova.act("Tap the login button")
```

```python
# iOS
with NovaActMobile(
    bundle_id="com.example.app",
    mode="local",
    device_name="iPhone 15",
    platform_version="17",
) as nova:
    nova.act("Tap the login button")
```

#### Deep Links

```python
# Launch with a deep link
with NovaActMobile(
    app_package="com.example.app",
    app_activity=".MainActivity",
    deep_link="myapp://target/screen",
) as nova:
    nova.act("Interact with the target screen")

    # Navigate to a different deep link mid-workflow
    nova.go_to_url(MobileActuator.app_url("com.example.app", deep_link="myapp://other"))
```

#### Activity Launch (Android)

```python
# Launch into a specific activity
with NovaActMobile(
    app_package="com.example.app",
    app_activity=".DetailActivity",
) as nova:
    nova.act("Interact with the detail screen")

    # Switch to a different activity mid-workflow
    nova.go_to_url(MobileActuator.app_url("com.example.app", activity=".OtherActivity"))
```

#### Additional Appium Capabilities

```python
# Pass any Appium capabilities to the session
with NovaActMobile(
    app_package="com.example.app",
    app_activity=".MainActivity",
    additional_capabilities={
        "appium:autoLaunch": False,
        "appium:noReset": True,
    },
) as nova:
    nova.act("...")
```

For lower-level actuator usage, see [`actuation/`](actuation/README.md).

### `Platform`

`StrEnum` identifying the target mobile platform (`ANDROID`, `IOS`). Provides properties for Appium automation name, Device Farm upload type, and app file extension. See [`platform.py`](platform.py).

### `MobileActuator`

Infrastructure-agnostic Appium actuator. Provides `app_url()` for building navigation URLs and `go_to_url()` for dispatching them. See [`actuation/`](actuation/README.md) for details.

`app_url()` encodes app identifiers, deep links, and activities into URLs that `go_to_url()` knows how to dispatch:

```python
# Launch App
MobileActuator.app_url("com.example.app")
# Open deep link
MobileActuator.app_url("com.example.app", deep_link="myapp://screen")
# Launch Android activity
MobileActuator.app_url("com.example.app", activity=".DetailActivity")
```

### `DeviceFarmActuator`

Extends `MobileActuator` with automatic Device Farm session lifecycle. See [`actuation/`](actuation/README.md) for details.

## Subpackages

- [`actuation/`](actuation/README.md) — Appium actuator implementations
- [`app/`](app/README.md) — `MobileAppConfig` for app identity
- [`device_farm/`](device_farm/README.md) — AWS Device Farm client and upload config

## App Navigation

There are several ways to navigate to a specific screen in a mobile app. Which one applies depends on the app's architecture and the target platform.

### Deep Links (Android and iOS)

A deep link tells the app which screen to navigate to. This works on both platforms but requires the app to support it. There are two types:

- Custom URL schemes (`myapp://products/123`). The app registers a custom scheme and routes incoming links to the right screen. See [iOS](https://developer.apple.com/documentation/xcode/defining-a-custom-url-scheme-for-your-app) and [Android](https://developer.android.com/training/app-links/deep-linking) docs.
- [Universal Links](https://developer.apple.com/documentation/xcode/allowing-apps-and-websites-to-link-to-your-content) (iOS) / [App Links](https://developer.android.com/training/app-links) (Android). Uses verified `https://` links. On iOS, unavailable on public Device Farm devices because [app re-signing strips the Associated Domains entitlement](https://docs.aws.amazon.com/devicefarm/latest/developerguide/skip-app-re-signing-on-private-devices.html). On Android, re-signing changes the certificate fingerprint, breaking [domain verification via `assetlinks.json`](https://developer.android.com/training/app-links/verify-android-applinks). Unverified Android web links aren't affected by re-signing but are unreliable on Android 12+, where the OS routes them to the browser by default.

> When this README says "deep links," it means custom URL schemes unless otherwise noted.

Use the `deep_link` parameter on `NovaActMobile` for launch-time navigation, or `MobileActuator.app_url(deep_link=...)` with `go_to_url()` for mid-workflow navigation. Under the hood, deep links are dispatched via [`mobile: deepLink`](https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-deeplink) on Android and [`mobile: deepLink`](https://appium.github.io/appium-xcuitest-driver/latest/reference/execute-methods/#mobile-deeplink) on iOS.

On iOS, `mobile: deepLink` requires iOS 16.4+/Xcode 14.3+ (it relies on the XCTest `open()` API). Reliability on Device Farm real devices is mixed due to the multi-hop relay through WebDriverAgent.

### Activity Launch (Android Only)

Multi-activity Android apps can expose screens as separate Activities. You can launch any exported Activity directly via [`mobile: startActivity`](https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-startactivity).

Use `app_activity` on `NovaActMobile` for launch-time activity selection, or `MobileActuator.app_url(activity=...)` with `go_to_url()` for mid-workflow switching.

The target activity must have `android:exported="true"` in the manifest. On Android 12+ (`targetSdkVersion 31+`), most apps only export their main launcher activity. This doesn't apply to single-activity apps where one Activity hosts all screens via internal navigation.

iOS has no activity concept. Deep links are the only way to navigate to a specific page on iOS.

### App Switching

To switch between different apps mid-workflow, use `go_to_url()` with `MobileActuator.app_url("com.other.app")`. This calls `activate_app` under the hood, which brings the target app to the foreground on both platforms.

## Permission Dialog Handling

Nova Act can handle permission dialogs via `nova.act()`. The sections below cover Appium-level alternatives that don't require agentic interaction.

### Android

On Android, permissions for the target app can be granted at the OS level before the app launches, eliminating all permission dialogs:

1. Pass `additional_capabilities={"appium:autoLaunch": False}` to `NovaActMobile` to prevent the app from starting (see [`appium:autoLaunch`](https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#capabilities))
2. Call [`mobile: changePermissions`](https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-changepermissions) with `permissions: "all", action: "grant", target: "pm"` to grant all runtime permissions for the app via [`adb shell pm grant`](https://developer.android.com/tools/adb#pm). You can also pass a specific list of permissions instead of `"all"` to scope grants to what the app actually needs.
3. Launch the app. All permissions are already granted, zero dialogs appear.

### iOS

iOS has no mechanism to pre-authorize permissions on a real device before the app runs. Dialogs must be handled as they appear.

To handle dialogs at the Appium level, use the [`mobile: alert`](https://appium.github.io/appium-xcuitest-driver/latest/reference/execute-methods/#mobile-alert) command. Set `action` to `accept` to grant a permission or `dismiss` to deny it. The command deterministically acts on whatever system alert is currently showing. A retry loop is needed since calling it before a dialog appears will throw. Be aware that timing-sensitive dialogs can lead to unexpected application states if the alert is accepted or dismissed before the app is ready to proceed.

## Known Issues

### Newest OS Versions

The latest iOS and Android versions can be flaky when the Appium drivers haven't fully caught up with a new OS release. If you hit unexpected failures, try targeting a device running a more established OS version.

### Pull-to-Refresh

`agentScroll("up")` generates a slow swipe that doesn't exceed the overscroll threshold required to trigger pull-to-refresh.

### Time Picker Typing (Android)

`agentType()` fails on Android native time picker widgets because `send_keys()` doesn't work on picker elements. The clock-face time picker also requires a circular drag gesture not supported by the current actuator primitives.

### Date Picker Navigation

The calendar may open at a distant date. The model doesn't always identify the year label as a tappable shortcut and instead clicks the next-month arrow repeatedly, making navigation slow or timing out.
