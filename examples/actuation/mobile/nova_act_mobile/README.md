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

For lower-level actuator usage, see [`actuation/`](actuation/README.md).

### `Platform`

`StrEnum` identifying the target mobile platform (`ANDROID`, `IOS`). Provides properties for Appium automation name, Device Farm upload type, and app file extension. See [`platform.py`](platform.py).

### `MobileActuator`

Infrastructure-agnostic Appium actuator. See [`actuation/`](actuation/README.md) for details.

### `DeviceFarmActuator`

Extends `MobileActuator` with automatic Device Farm session lifecycle. See [`actuation/`](actuation/README.md) for details.

## Subpackages

- [`actuation/`](actuation/README.md) — Appium actuator implementations
- [`app/`](app/README.md) — `MobileAppConfig` for app identity
- [`device_farm/`](device_farm/README.md) — AWS Device Farm client and upload config
