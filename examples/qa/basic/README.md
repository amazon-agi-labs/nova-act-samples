# Amazon Nova Act Basic QA Test

Runs QA tests using `NovaActQa`'s typed extraction and assertion methods. Mirrors the `examples/qa_simple.py` example but replaces manual `act_get()` + assert with `expect()` and `check()`.

## Prerequisites

Complete the [Getting Started](../../README.md#getting-started) section in the main examples directory.

## Usage

```bash
python -m examples.qa.basic.main
```

## Implementation Details

The example navigates to a destination page and runs a series of QA tests using `NovaActQa`. Compare with `examples/qa_simple.py` to see how `NovaActQa` simplifies the same test pattern.

## Next Steps

- For the full `NovaActQa` API reference, see [NovaActQa →](../nova_act_qa/README.md)
- For mobile QA, see [Mobile QA →](../mobile_qa/README.md)
