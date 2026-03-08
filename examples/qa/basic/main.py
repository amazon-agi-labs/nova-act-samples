"""Basic QA test using NovaActQa.

NovaActQa extends NovaAct with assertion and extraction methods. This example
mirrors ``examples/qa_simple.py`` but replaces raw ``act_get()`` calls and
assertions with ``expect()`` and ``check()``.

NOTE: Failed tests are expected for example purposes.

Usage:
python -m examples.qa.basic.main
"""

from nova_act import workflow

from examples.nova_act_client import NovaActClient
from examples.qa.nova_act_qa import NovaActQa
from examples.utils import get_logger

LOGGER = get_logger(__name__)


@workflow(**NovaActClient.get_workflow_kwargs())
def main() -> None:
    """Run QA tests."""
    with NovaActQa(starting_page="https://nova.amazon.com/act/gym/next-dot/") as nova:
        nova.act("Go to the Teegarden B Destination page")
        nova.check("The Teegarden Destination page is loaded")

        nova.expect("The planet mass").to_equal(1.05)
        nova.expect("The planet average temperature").to_equal(15)
        # Expected to fail for example purposes
        nova.expect("The planet gravity").to_equal(1.10)

        LOGGER.info("✓ All QA tests passed")


if __name__ == "__main__":
    main()
