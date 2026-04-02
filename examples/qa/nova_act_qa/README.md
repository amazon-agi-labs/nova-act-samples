# Amazon Nova Act QA Utility Example

`NovaActQa` is a drop-in replacement for `NovaAct` with QA utilities like typed assertions, value extraction, and boolean state verification. Chain `expect(prompt)` with matchers like `to_equal()`, `to_contain()`, and `to_match()` to assert against UI state, or use `check(prompt)` for quick boolean checks. Assertions raise `AssertionError` on failure with the prompt included in the message.

## Structure

```
nova_act_qa/
├── __init__.py              # Re-exports NovaActQa and NovaActMobileQa
├── nova_act_qa.py           # NovaActQa implementation
├── nova_act_mobile_qa.py    # NovaActMobileQa implementation
```

## Key Classes

### `NovaActQa`

Extends `NovaAct` with `expect()` for assertions and `check()` for boolean state verification. Use `expect(prompt)` to extract values (`as_string`, `as_number`, `as_boolean`) or chain with matchers. See [`nova_act_qa.py`](nova_act_qa.py) for the full API.

```python
with NovaActQa(starting_page="https://example.com") as nova:
    nova.act("Log in as test user")
    nova.check("User is logged in")
    nova.expect("Page title").to_equal("Dashboard")
    nova.expect("Cart total").to_be_greater_than(0)
    order_id = nova.expect("The order ID").as_string()
```

### `NovaActMobileQa`

Combines [`NovaActMobile`](../../actuation/mobile/nova_act_mobile/README.md) with `NovaActQa` for mobile actuation and QA utilities. See [`nova_act_mobile_qa.py`](nova_act_mobile_qa.py).

```python
with NovaActMobileQa(app_package="com.example.app", app_activity=".Main") as nova:
    nova.act("Tap the login button")
    nova.check("User is logged in")
    nova.expect("Welcome message").to_contain("Hello")
```

> These are conceptual examples showing the API surface. Replace the identifiers and prompts with your own application.
