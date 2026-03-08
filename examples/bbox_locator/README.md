# Amazon Nova Act Bounding Box Locator Examples

Leverages Nova Act's built-in image understanding and bounding box generation to locate UI elements in static images. A custom `ImageActuator` swaps the browser screenshot in each observation with a provided image, letting Nova Act apply the same visual grounding it uses for web pages to any arbitrary image.

## Repository Structure

```
├── main.py          # Entry point — extracts bounding boxes from a static image
└── input.png        # Sample input image
```

## Prerequisites

Complete the [Getting Started](../README.md#getting-started) section in the main examples directory before running this example.

## Usage

```bash
python -m examples.bbox_locator.main
```

**Implementation Details:**
- Custom `ImageActuator` extends `DefaultNovaLocalBrowserActuator` and overrides `take_observation()` to swap the browser screenshot with a static image
- Converts input to JPEG for SDK compatibility (handles PNG, JPEG, etc.)
- Extracts bounding box coordinates via `act_get()` with `STRING_SCHEMA` (more reliable than JSON for coordinate data) and parses into a `BboxTLBR` object
- Draws the resulting bounding box on the image and saves to `output.png`

## Next Steps

- For deploying workflows on AWS, see [CDK →](../../cdk/README.md)
- Visit the [Nova Act documentation →](https://docs.aws.amazon.com/nova-act)
