# Amazon Nova Act Mobile QA Examples

QA testing on mobile apps using `NovaActQa` with AWS Device Farm. Includes examples for both iOS and Android.

## Repository Structure

```
├── android.py         # Android QA test
├── ios.py             # iOS QA test
├── requirements.txt   # Python dependencies
```

## Prerequisites

1. Complete the [Getting Started](../../README.md#getting-started) section in the main examples directory
2. Configure AWS credentials with Device Farm access
3. Install dependencies (includes [mobile actuation](../../actuation/mobile/README.md) dependencies):
   ```bash
   pip install -r examples/qa/mobile_qa/requirements.txt
   ```

## Usage

### android.py - Android QA Test

Runs QA tests across multiple Android apps via Device Farm remote access sessions.

```bash
python -m examples.qa.mobile_qa.android
```

**Implementation Details:**
- Combines `NovaActQa` with `DeviceFarmActuator` for Android device provisioning
- Tests span multiple apps by switching via `go_to_url()` with `MobileAppConfig` identifiers

### ios.py - iOS QA Test

Runs QA tests across multiple iOS apps via Device Farm remote access sessions.

```bash
python -m examples.qa.mobile_qa.ios
```

**Implementation Details:**
- Combines `NovaActQa` with `DeviceFarmActuator` for iOS device provisioning
- Tests span multiple apps by switching via `go_to_url()` with `MobileAppConfig` identifiers

## Next Steps

- For the full `NovaActQa` API reference, see [NovaActQa →](../nova_act_qa/README.md)
- For basic QA testing, see [Basic Example →](../basic/README.md)
