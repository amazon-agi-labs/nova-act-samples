# Amazon Nova Act Basic HITL Examples

Simple examples demonstrating different human-in-the-loop patterns with Nova Act.

## Repository Structure

```
├── ui/                     # Local HTML files for testing
├── approval.py             # Human approval workflow
└── ui_takeover.py          # UI takeover workflow
```

## Prerequisites

Complete the [Getting Started](../../README.md#getting-started) section in the main examples directory before running these examples.

## Usage Instructions

### approval.py - Human Approval Workflow

Demonstrates requesting human approval before completing automated actions.

```bash
python -m examples.human_in_the_loop.basic.approval
```

**Features:**
- Loads local site (`ui/checkout.html`)
- Automates product selection and checkout flow
- Requests human approval via CLI before order completion
- Returns order number upon completion

### ui_takeover.py - UI Takeover Workflow

Demonstrates pausing automation to let human handle a CAPTCHA.

```bash
python -m examples.human_in_the_loop.basic.ui_takeover
```

**Features:**
- Loads CAPTCHA demo page
- Pauses when human interaction is needed
- Waits for user to complete the CAPTCHA
- Continues automation after user confirmation

## Next Steps

- Learn more about HITL in the [README ->](../README.md)
- For production deployments, see [CDK →](../../../cdk/README.md)
- For complete applications, see [Solutions →](../../../solutions/README.md)
- Visit the [Nova Act documentation →](https://docs.aws.amazon.com/nova-act)
