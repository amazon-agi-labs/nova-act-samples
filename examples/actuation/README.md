# Amazon Nova Act Actuation Examples

Examples demonstrating how to extend or replace Nova Act's default browser actuator with custom implementations for different platforms and environments.

> **Note:** The custom actuator API is experimental and subject to change.

## Repository Structure

```
├── browser/                    # Browser actuation steering
├── desktop/                    # Desktop app automation
└── mobile/                     # Mobile app automation on AWS Device Farm
```

## What is an Actuator?

An actuator is the component that translates Nova Act's high-level actions (click, type, scroll) into platform-specific commands. The SDK ships with a default Playwright-based browser actuator, but you can swap it for any implementation of `BrowserActuatorBase`.

## Examples

### Browser

Demonstrates how to steer Nova Act to use actuation types supported by the SDK but outside the default behavior, such as click variants and hover.

[Get Started with Browser Actuation →](browser/README.md)

### Desktop

Desktop app automation. Includes an Electron example with a task manager app.

[Get Started with Desktop Actuation →](desktop/README.md)

### Mobile

End-to-end mobile app automation on Android and iOS using AWS Device Farm. Includes a full `MobileActuator` implementation and Device Farm session lifecycle management.

[Get Started with Mobile Actuation →](mobile/README.md)

## Next Steps

- For standalone actuator patterns (image bounding boxes, DOM resolution), see [Bounding Box Locator →](../bbox_locator/README.md) and [Element Resolver →](../element_resolver/README.md)
- For deploying workflows on AWS, see [CDK →](../../cdk/README.md)
- Visit the [Nova Act documentation →](https://docs.aws.amazon.com/nova-act)
