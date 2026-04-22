# Amazon Nova Act Mobile Actuation with AWS Device Farm Examples

End-to-end mobile app automation using Nova Act with [AWS Device Farm](https://docs.aws.amazon.com/devicefarm/latest/developerguide/welcome.html). Uses [`NovaActMobile`](nova_act_mobile/README.md) to run Nova Act workflows on Android and iOS apps on real devices via [Remote Access Sessions](https://docs.aws.amazon.com/devicefarm/latest/developerguide/remote-access.html).

## Repository Structure

```
├── android_quick_start.py      # Android quick start with pre-installed apps
├── ios_quick_start.py          # iOS quick start with pre-installed apps
├── custom_app.py               # Custom app testing with CLI args
├── android_deep_link.py        # Android deep link navigation
├── android_activity_launch.py  # Android activity launch and switching
├── android_permissions.py      # Android permission pre-granting
├── ios_deep_link.py            # iOS deep link navigation
├── ios_permissions.py          # iOS permission dialog handling
├── nova_act_mobile/            # Mobile automation package
└── utils/
```

## Prerequisites

1. Complete the [Getting Started](../../README.md#getting-started) section in the main examples directory
2. Configure environment with AWS credentials for full access to Device Farm and Nova Act
   - Note: full access is for example purposes only, permissions should be scoped down for further use
3. Install dependencies:
   ```bash
   pip install -r examples/actuation/mobile/requirements.txt
   ```

## Usage

### android_quick_start.py - Android Quick Start

Launch pre-installed Android apps and perform simple interactions on a Device Farm device. No app upload or CLI configuration required.

```bash
python -m examples.actuation.mobile.android_quick_start
```

**Implementation Details:**
- Connects to a default Device Farm Android device and launches pre-installed apps
- Demonstrates Nova Act automating Android device actions
- Demonstrates app switching via `go_to_url()` with `MobileActuator.app_url()`
- Uses `NovaActMobile` with `app_package` and `app_activity`

### ios_quick_start.py - iOS Quick Start

Launch pre-installed iOS apps and perform simple interactions on a Device Farm device. No app upload or CLI configuration required.

```bash
python -m examples.actuation.mobile.ios_quick_start
```

**Implementation Details:**
- Connects to a Device Farm iOS device and launches pre-installed apps
- Demonstrates Nova Act automating iOS device actions
- Demonstrates app switching via `go_to_url()` with `MobileActuator.app_url()`
- Uses `NovaActMobile` with `bundle_id`

### custom_app.py - Custom App Automation

End-to-end mobile app automation with configurable app path and device selection. Defaults to the Device Farm sample APK when run with no arguments.

```bash
python -m examples.actuation.mobile.custom_app
```

Pass your own app binary and identifiers via CLI args:

```bash
python -m examples.actuation.mobile.custom_app \
  --app-package com.example.app \
  --app-activity com.example.MainActivity \
  --app-path /path/to/app.apk
```

**Implementation Details:**
- Uses `NovaActMobile` for automatic platform detection and actuator setup
- Uploads app binaries to Device Farm with deduplication
- Exercises inputs, checkboxes, date pickers, and native components on the sample app
- Supports `--project-arn` and `--device-arn` for advanced configuration

### android_deep_link.py - Android Deep Link Navigation

Launch an app with a custom URL scheme deep link and navigate to a different deep link mid-workflow. Uses the [AWS Device Farm sample app](https://github.com/aws-samples/aws-device-farm-sample-app-for-android) with the `dfsample://` URL scheme.

```bash
python -m examples.actuation.mobile.android_deep_link
```

**Implementation Details:**
- Uses the `deep_link` parameter on `NovaActMobile` to open `dfsample://main` at session start
- Navigates to a second deep link mid-workflow via `go_to_url()` with `MobileActuator.app_url(deep_link=...)`
- Deep links require app-side support. The app must register a [custom URL scheme](https://developer.android.com/training/app-links/deep-linking) and route incoming links to the correct screen. Dispatched via the Appium [`mobile: deepLink`](https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-deeplink) command.

### android_activity_launch.py - Android Activity Launch

Launch an app into a specific exported Activity and switch to a different Activity mid-workflow. Uses the [AWS Device Farm sample app](https://github.com/aws-samples/aws-device-farm-sample-app-for-android) which has multiple exported activities.

```bash
python -m examples.actuation.mobile.android_activity_launch
```

**Implementation Details:**
- Uses `app_activity` on `NovaActMobile` to launch directly into `BackNavigationActivity` instead of the default launcher
- Switches to `UpNavigationActivity` mid-workflow via `go_to_url()` with `MobileActuator.app_url(activity=...)`
- Under the hood, both use the Appium [`mobile: startActivity`](https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-startactivity) command
- Only works for multi-activity Android apps with `android:exported="true"` on the target activities

### android_permissions.py - Android Permission Pre-Granting

Supress permission dialogs on Android by granting permissions at the OS level before the app launches. Uses the [AWS Device Farm sample app](https://github.com/aws-samples/aws-device-farm-sample-app-for-android) which requests CAMERA and ACCESS_FINE_LOCATION permissions.

```bash
python -m examples.actuation.mobile.android_permissions
```

**Implementation Details:**
- Uses `additional_capabilities` to pass [`appium:autoLaunch: false`](https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#app), preventing the app from starting before permissions are granted
- Calls Appium [`mobile: changePermissions`](https://github.com/appium/appium-uiautomator2-driver?tab=readme-ov-file#mobile-changepermissions) to grant all permissions at the OS level via [`adb shell pm grant`](https://developer.android.com/tools/adb#pm)
- Launches the app after granting. All permissions are already granted, so zero dialogs appear.

### ios_deep_link.py - iOS Deep Link Navigation

Open a custom URL scheme deep link on iOS at launch.

```bash
python -m examples.actuation.mobile.ios_deep_link
```

**Implementation Details:**
- Uses the `deep_link` parameter on `NovaActMobile` to open `tel://5551234567` at session start, which dispatches to the built-in Phone app
- iOS deep links use [custom URL schemes](https://developer.apple.com/documentation/xcode/defining-a-custom-url-scheme-for-your-app) dispatched via the Appium [`mobile: deepLink`](https://appium.github.io/appium-xcuitest-driver/latest/reference/execute-methods/#mobile-deeplink) command (requires iOS 16.4+)
- [Universal Links](https://developer.apple.com/documentation/xcode/allowing-apps-and-websites-to-link-to-your-content) are not available on public Device Farm devices because [re-signing strips the Associated Domains entitlement](https://docs.aws.amazon.com/devicefarm/latest/developerguide/skip-app-re-signing-on-private-devices.html)

### ios_permissions.py - iOS Permission Dialog Handling

Handle iOS permission dialogs using the `mobile: alert` Appium command.

```bash
python -m examples.actuation.mobile.ios_permissions
```

**Implementation Details:**
- Unlike Android, iOS cannot pre-grant permissions on real devices. Dialogs must be accepted as they appear.
- Uses the Appium [`mobile: alert`](https://appium.github.io/appium-xcuitest-driver/latest/reference/execute-methods/#mobile-alert) command with `action: accept` in a retry loop to handle dialogs as they appear, since calling it before a dialog is present will throw

## Next Steps

- For architecture details and class documentation, see [`nova_act_mobile/`](nova_act_mobile/README.md)
- For deploying workflows on AWS, see [CDK →](../../../cdk/README.md)
- For complete applications, see [Solutions →](../../../solutions/README.md)
- Visit the [Nova Act documentation →](https://docs.aws.amazon.com/nova-act)
