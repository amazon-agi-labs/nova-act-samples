"""Run QA tests on your website.

Runs a series of QA tests on a Nova Act gym.
A `TEST_STEPS` data structure is declared and iterated over in the main function to execute the tests.

NOTE: Failed tests should be expected for example purposes.

Usage:
python -m examples.qa
"""

import fire  # type: ignore

from examples.utils import get_logger, get_workflow_kwargs

from nova_act import BOOL_SCHEMA, NovaAct, workflow

LOGGER = get_logger(__name__)

# Test step Constants
TEST_STEPS = [
    {
        "action": "Go to the Teegarden B Destination page",
        "expected_result": "The Teegarden Destination page is loaded",
    },
    {"expected_result": "Mass is 1.05x Earth mass"},
    {"expected_result": "Average Temperature is 15C"},
    {"expected_result": "Surface Gravity is 1.10g"},
]


@workflow(**get_workflow_kwargs())
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

                assert (
                    actual is expected
                ), f"Test step {i} failed: Expected '{expected}' but got '{actual}' for action '{action}' and expected result '{expected_result}'"

            LOGGER.info(f"✓ Step {i} passed\n")


if __name__ == "__main__":
    fire.Fire(main)
