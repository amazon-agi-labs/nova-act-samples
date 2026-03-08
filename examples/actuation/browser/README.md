# Amazon Nova Act Browser Actuation Examples

Demonstrates browser actuation capabilities in Nova Act. The SDK natively handles several HTML element types like selects, range sliders, and color pickers with specialized actuator logic, while other actuation types require prompt steering to guide the model toward the correct action.

> **Note:** Actuation types that require steering are supported by the SDK but are not yet optimized to be produced reliably. Treat those examples as experimental.

## Repository Structure

```
├── click.py             # Click actuation steering (single, double, right)
├── color_input.py       # Color picker actuation
├── file_input.py        # File upload actuation
├── hover.py             # Hover actuation steering
├── range_input.py       # Range slider actuation
├── select.py            # Native dropdown actuation
└── static/
    ├── click.html       # Click test page
    ├── color_input.html # Color picker test page
    ├── file_input.html  # File upload test page
    ├── hover.html       # Hover test page
    ├── range_input.html # Range slider test page
    └── select.html      # Native dropdown test page
```

## Prerequisites

Complete the [Getting Started](../../README.md#getting-started) section in the main examples directory before running these examples.

## Usage

### click.py - Click Actuation

Steering for the different `clickType` options of `agentClick`. Single click works without steering (included as a baseline), while double-click and right-click require the steering reference so the model selects the correct `clickType`.

```bash
python -m examples.actuation.browser.click
```

**Implementation Details:**
- Defines a `CLICK_STEERING` constant with the `agentClick` syntax and available `clickType` options
- Prepends the steering reference to prompts via `with_click_steering()` only for actuation types that need it
- Loads a local test page ([`static/click.html`](static/click.html)) with per-button counters to verify the correct actuation fired
- See the [`agent_click` implementation](https://github.com/aws/nova-act/blob/df800f8d45bccd9bb5fea1d60954c6b6855e530f/src/nova_act/tools/browser/default/util/agent_click.py#L44-L49) in the Nova Act SDK for more details

### hover.py - Hover Actuation

Steering for `agentHover` to hover over an element.

```bash
python -m examples.actuation.browser.hover
```

**Implementation Details:**
- Defines a `HOVER_STEERING` constant with the `agentHover` syntax
- Prepends the steering reference to prompts via `with_hover_steering()`
- The test page ([`static/hover.html`](static/hover.html)) button shows a tooltip and increments a hover counter on `mouseenter`
- See the [`agent_hover` implementation](https://github.com/aws/nova-act/blob/df800f8d45bccd9bb5fea1d60954c6b6855e530f/src/nova_act/tools/browser/default/util/agent_hover.py#L21) in the Nova Act SDK for more details

### select.py - Native Select Actuation

Demonstrates how Nova Act handles native [`<select>`](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/select) dropdown elements. The SDK's `agent_type` actuator detects native dropdowns, types the selected value, and blurs the element.

```bash
python -m examples.actuation.browser.select
```

**Implementation Details:**
- The test page ([`static/select.html`](static/select.html)) renders native `<select>` dropdowns that display the selected option
- Uses standard `nova.act()` calls and relies on the SDK's built-in support to handle controlling native dropdowns
- If a `<select>` element is clicked, [`agent_click` detects](https://github.com/aws/nova-act/blob/df800f8d45bccd9bb5fea1d60954c6b6855e530f/src/nova_act/tools/browser/default/util/agent_click.py#L66) the native dropdown and [raises an `AgentRedirectError`](https://github.com/aws/nova-act/blob/df800f8d45bccd9bb5fea1d60954c6b6855e530f/src/nova_act/tools/browser/default/util/agent_click.py#L71) with the available option values
- [`agent_type` checks](https://github.com/aws/nova-act/blob/df800f8d45bccd9bb5fea1d60954c6b6855e530f/src/nova_act/tools/browser/default/util/agent_type.py#L109-L113) if the target element is a `<select>`, focuses it, and types the value to select it

### file_input.py - File Input Actuation

Demonstrates how Nova Act handles `<input type="file">` elements. The SDK's `agent_type` actuator detects file inputs and uses Playwright's `set_input_files` to upload the file. Requires configuring [`SecurityOptions`](https://github.com/aws/nova-act/tree/main?tab=readme-ov-file#security-options).

```bash
python -m examples.actuation.browser.file_input
```

**Implementation Details:**
- The test page ([`static/file_input.html`](static/file_input.html)) renders a file input that displays the uploaded filename
- Uses standard `nova.act()` calls with `SecurityOptions` to allowlist the upload path
- If a file input is clicked, [`agent_click` detects](https://github.com/aws/nova-act/blob/df800f8d45bccd9bb5fea1d60954c6b6855e530f/src/nova_act/tools/browser/default/util/agent_click.py#L77) the file chooser dialog and raises an `AgentRedirectError` to redirect to `agentType`
- [`agent_type` checks](https://github.com/aws/nova-act/blob/df800f8d45bccd9bb5fea1d60954c6b6855e530f/src/nova_act/tools/browser/default/util/agent_type.py#L99-L103) if the target element is an `<input type="file">` and calls Playwright's `set_input_files`

### range_input.py - Range Input Actuation

Demonstrates how Nova Act handles [`<input type="range">`](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/input/range) elements. The SDK's `agent_type` actuator detects range inputs and sets their value via JavaScript.

```bash
python -m examples.actuation.browser.range_input
```

**Implementation Details:**
- The test page ([`static/range_input.html`](static/range_input.html)) renders range sliders that display their current value via `input` event listeners
- Uses standard `nova.act()` calls and relies on the SDK's built-in support to handle controlling range inputs
- If a range input is clicked, [`agent_click` detects](https://github.com/aws/nova-act/blob/df800f8d45bccd9bb5fea1d60954c6b6855e530f/src/nova_act/tools/browser/default/util/agent_click.py#L64) the element type and [raises an `AgentRedirectError`](https://github.com/aws/nova-act/blob/df800f8d45bccd9bb5fea1d60954c6b6855e530f/src/nova_act/tools/browser/default/util/agent_click.py#L179-L185) to redirect to `agentType` with the slider's min/max bounds
- [`agent_type` checks](https://github.com/aws/nova-act/blob/df800f8d45bccd9bb5fea1d60954c6b6855e530f/src/nova_act/tools/browser/default/util/agent_type.py#L104-L106) if the target element is an `<input type="range">`, and calls [`handle_range_input`](https://github.com/aws/nova-act/blob/df800f8d45bccd9bb5fea1d60954c6b6855e530f/src/nova_act/tools/browser/default/util/agent_type.py#L207-L234) which validates the value is numeric and sets it via `element.value`

### color_input.py - Color Input Actuation

Demonstrates how Nova Act handles [`<input type="color">`](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/input/color) elements. The SDK's `agent_type` actuator detects color inputs and sets their hex value directly via JavaScript.

```bash
python -m examples.actuation.browser.color_input
```

**Implementation Details:**
- The test page ([`static/color_input.html`](static/color_input.html)) renders color pickers
- Uses standard `nova.act()` calls and relies on the SDK's built-in support to handle controlling color inputs
- If a color input is clicked, [`agent_click` detects](https://github.com/aws/nova-act/blob/df800f8d45bccd9bb5fea1d60954c6b6855e530f/src/nova_act/tools/browser/default/util/agent_click.py#L64) the element type and [raises an `AgentRedirectError`](https://github.com/aws/nova-act/blob/df800f8d45bccd9bb5fea1d60954c6b6855e530f/src/nova_act/tools/browser/default/util/agent_click.py#L175-L178) with a `#RRGGBB` format hint
- [`agent_type` checks](https://github.com/aws/nova-act/blob/df800f8d45bccd9bb5fea1d60954c6b6855e530f/src/nova_act/tools/browser/default/util/agent_type.py#L96-L98) if the target element is an `<input type="color">`, and calls [`handle_color_input`](https://github.com/aws/nova-act/blob/df800f8d45bccd9bb5fea1d60954c6b6855e530f/src/nova_act/tools/browser/default/util/agent_type.py#L135-L154) which validates the hex format and sets `element.value`

## Next Steps

- For browser dialog handling, see [Browser Dialogs →](../../browser_dialogs/README.md)
- For production deployments, see [CDK →](../../../cdk/README.md)
- Visit the [Nova Act documentation →](https://docs.aws.amazon.com/nova-act)
