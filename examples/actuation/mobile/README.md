# Amazon Nova Act Mobile Actuation with AWS Device Farm Examples

End-to-end mobile app automation using Nova Act with [AWS Device Farm](https://docs.aws.amazon.com/devicefarm/latest/developerguide/welcome.html). Uses [`NovaActMobile`](nova_act_mobile/README.md) to run Nova Act workflows on Android and iOS apps on real devices via [Remote Access Sessions](https://docs.aws.amazon.com/devicefarm/latest/developerguide/remote-access.html).

## Repository Structure

```
├── android_quick_start.py      # Android quick start — pre-installed apps
├── ios_quick_start.py          # iOS quick start — pre-installed apps
├── custom_app.py               # Custom app testing with CLI args
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

## Next Steps

- For architecture details and class documentation, see [`nova_act_mobile/`](nova_act_mobile/README.md)
- For deploying workflows on AWS, see [CDK →](../../../cdk/README.md)
- For complete applications, see [Solutions →](../../../solutions/README.md)
- Visit the [Nova Act documentation →](https://docs.aws.amazon.com/nova-act)
