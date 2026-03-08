# Amazon Nova Act Element Resolver Example

Demonstrates how to build a custom actuator that resolves bounding box coordinates back to DOM elements. The actuator overrides `agent_click` to perform the default Playwright click, then extracts the element's tag, id, class, text content, and attributes from the bounding box center point. This pattern can be extended to any actuation method to map Nova Act interactions to DOM selectors.

## Repository Structure

```
├── main.py          # Entry point — runs the element resolver example
```

## Prerequisites

1. Complete the [Getting Started](../README.md#getting-started) section in the main examples directory

## Usage

```bash
python -m examples.element_resolver.main
```

**Implementation Details:**
- The `ElementResolverActuator` in [`main.py`](main.py) extends `DefaultNovaLocalBrowserActuator` to intercept clicks and resolve the clicked coordinates to a DOM element
- After performing the standard Playwright click via the parent class, it parses the bounding box string into a center point and uses `get_element_at_point` from the Nova Act SDK to look up the element at those coordinates, returning its tag, id, class, text content, and attributes

## Next Steps

- For deploying workflows on AWS, see [CDK →](../../cdk/README.md)
- Visit the [Nova Act documentation →](https://docs.aws.amazon.com/nova-act)
