# Amazon Nova Act QA Utility Example

`NovaActQa` is a drop-in replacement for `NovaAct` with QA utilities like typed assertions, value extraction, and boolean state verification. Chain `expect(prompt)` with matchers like `to_equal()`, `to_contain()`, and `to_match()` to assert against UI state, or use `check(prompt)` for quick boolean checks. Assertions raise `AssertionError` on failure with the prompt included in the message.

## Structure

```
nova_act_qa/
├── __init__.py        # Re-exports NovaActQa
├── nova_act_qa.py     # Implementation
```

## Key Classes

### `NovaActQa`

Extends `NovaAct` with `expect()` for assertions and `check()` for boolean state verification. Use `expect(prompt)` to create an assertion chain (`to_equal`, `to_contain`, `to_be_true`, etc.) or extract values (`as_string`, `as_number`, `as_boolean`). Use `check(prompt)` as shorthand for `expect(prompt).to_be_true()`. Assertions raise `AssertionError` on failure with the prompt included in the message. See [`nova_act_qa.py`](nova_act_qa.py) for the full API and the [parent QA example](../README.md) for usage.

### Quick Example

```python
with NovaActQa(starting_page="https://example.com") as nova:
    nova.act("Log in as test user")
    nova.check("User is logged in")
    nova.expect("Page title").to_equal("Dashboard")
    nova.expect("Cart total").to_be_greater_than(0)
    order_id = nova.expect("The order ID").as_string()
```

> This is a conceptual example showing the API surface. Replace the URL and prompts with your own application.
