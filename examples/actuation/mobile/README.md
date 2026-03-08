# Amazon Nova Act Mobile Actuation with AWS Device Farm Examples

End-to-end mobile app automation using Nova Act with [AWS Device Farm](https://docs.aws.amazon.com/devicefarm/latest/developerguide/welcome.html). Demonstrates running Nova Act workflows on Android and iOS apps on real devices via [Remote Access Sessions](https://docs.aws.amazon.com/devicefarm/latest/developerguide/remote-access.html).

## Repository Structure

```
├── android_quick_start.py      # Android quick start — pre-installed apps
├── ios_quick_start.py          # iOS quick start — pre-installed apps
├── custom_app.py               # Custom app testing with CLI configuration
├── nova_act_mobile/            # Mobile automation package
└── utils/                      # CLI args and polling helpers
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
- Uses `MobileAppConfig.for_android()` to configure app identity by package and activity

### ios_quick_start.py - iOS Quick Start

Launch pre-installed iOS apps and perform simple interactions on a Device Farm device. No app upload or CLI configuration required.

```bash
python -m examples.actuation.mobile.ios_quick_start
```

**Implementation Details:**
- Connects to a Device Farm iOS device and launches pre-installed apps
- Demonstrates Nova Act automating iOS device actions
- Demonstrates app switching via `go_to_url()` with `MobileActuator.app_url()`
- Uses `MobileAppConfig.for_ios()` to configure app identity by bundle ID

### custom_app.py - Custom App Automation

End-to-end mobile app automation with CLI-configurable app path, device selection, and platform. Defaults to the AWS Device Farm sample APK when run with no arguments.

```bash
python -m examples.actuation.mobile.custom_app
```

Pass your own app binary and identifiers via CLI args:

```bash
# Android
python -m examples.actuation.mobile.custom_app \
  --app-path /path/to/app.apk \
  --package com.example.app \
  --activity com.example.MainActivity

# iOS
python -m examples.actuation.mobile.custom_app \
  --app-path /path/to/app.ipa \
  --bundle-id com.example.app
```

**Implementation Details:**
- Uses `CliArgs` (`pydantic-settings`) for CLI parsing with platform auto-detection
- Uploads app binaries to Device Farm with deduplication via `DeviceFarmUploadConfig`
- Exercises inputs, checkboxes, date pickers, and native components on the sample app
- Supports `--project-arn`, `--device-arn`, and `--force-app-upload` for advanced configuration

## Next Steps

- For architecture details, class documentation, and local Appium usage, see [`nova_act_mobile/`](nova_act_mobile/README.md)
- For deploying workflows on AWS, see [CDK →](../../../cdk/README.md)
- For complete applications, see [Solutions →](../../../solutions/README.md)
- Visit the [Nova Act documentation →](https://docs.aws.amazon.com/nova-act)
