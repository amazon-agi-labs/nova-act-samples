"""Data-driven QA testing with Nova Act.

Defines test steps as a list of dictionaries and iterates over them at runtime,
making it easy to add or modify checks without changing control flow. Uses only
`act()` and `act_get()` with `BOOL_SCHEMA` — no extra utilities or helper classes
required.

For more robust QA workflows with typed assertions and structured reporting,
see the `examples/qa/` package and its `NovaActQa` extension class.

NOTE: Failed tests are expected for example purposes.

Usage:
python -m examples.qa_simple
"""

import fire
from nova_act import BOOL_SCHEMA, NovaAct, workflow

from examples.nova_act_client import NovaActClient
from examples.utils import get_logger

LOGGER = get_logger(__name__)

# Test step Constants
TEST_STEPS = [
    {
        "action": "Go to the Teegarden B Destination page",
        "expected_result": "The Teegarden Destination page is loaded",
    },
    {"expected_result": "Mass is 1.05x Earth mass"},
    {"expected_result": "Average Temperature is 15C"},
    # Expected to fail for example purposes
    {"expected_result": "Surface Gravity is 1.10g"},
]


@workflow(**NovaActClient.get_workflow_kwargs())
def main() -> None:
    with NovaAct(starting_page="https://nova.amazon.com/act/gym/next-dot/") as nova:
        # Iterate over the test steps
        for i, step in enumerate(TEST_STEPS, 1):
            # Get this step's action and expected result
            action = step.get("action")
            expected_result = step.get("expected_result")

            LOGGER.info(
                f"\nStep {i}: Processing action='{action}', expected='{expected_result}'\n"
            )

            # Execute the test action
            if action:
                nova.act(action)

            # Extract and assert the expected result
            if expected_result:
                # Use act_get() to extract the actual result from the page. Extend this to extract other data types using the `schema` argument!
                result = nova.act_get(expected_result, schema=BOOL_SCHEMA)
                actual = result.parsed_response
                expected = True

                assert actual is expected, (
                    f"Test step {i} failed: Expected '{expected}' but got '{actual}' for action '{action}' and expected result '{expected_result}'"
                )

            LOGGER.info(f"✓ Step {i} passed\n")


if __name__ == "__main__":
    fire.Fire(main)
