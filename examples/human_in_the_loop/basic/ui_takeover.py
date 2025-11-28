"""Demonstrates how to configure Nova Act for a HITL UI takeover workflow.

See the README for more details.

Usage:
python -m examples.human_in_the_loop.basic.ui_takeover
"""

from examples.utils import get_logger, get_workflow_kwargs

from nova_act import NovaAct, workflow
from nova_act.tools.human.interface.human_input_callback import (
    ApprovalResponse,
    HumanInputCallbacksBase,
    UiTakeoverResponse,
)
from nova_act.types.act_errors import NoHumanInputToolAvailable

LOGGER = get_logger(__name__)


class UiTakeoverCallbacks(HumanInputCallbacksBase):
    """
    Implements ui_takeover() callback which simply pauses execution until the enter key is pressed
    """

    def __init__(self) -> None:
        super().__init__()

    def approve(self, message: str) -> ApprovalResponse:
        """See approval.py for a Approval example"""
        raise NoHumanInputToolAvailable(message)

    def ui_takeover(self, message: str) -> UiTakeoverResponse:
        print(
            f"\n🤖 UI Takeover required for act_id: {self.current_act_id} inside act_session_id: {self.act_session_id}:"
        )
        print(f"   {message}")
        print("   Please complete the action in the browser...")
        input("   Press Enter when completed: ")
        return UiTakeoverResponse.COMPLETE


@workflow(**get_workflow_kwargs())
def main():
    with NovaAct(
        starting_page="https://www.google.com/recaptcha/api2/demo",
        human_input_callbacks=UiTakeoverCallbacks(),
    ) as nova:
        result = nova.act_get("Submit the form and return the result text")
        text = result.parsed_response
        LOGGER.info(f"✓ Form submited with response: {text}")


if __name__ == "__main__":
    main()
