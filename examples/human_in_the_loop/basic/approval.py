"""Demonstrates how to configure Nova Act for a HITL approval workflow.

See the README for more details.

Usage:
python -m examples.human_in_the_loop.basic.approval
"""

from pathlib import Path

from nova_act import NovaAct, SecurityOptions, workflow
from nova_act.tools.human.interface.human_input_callback import (
    ApprovalResponse,
    HumanInputCallbacksBase,
    UiTakeoverResponse,
)
from nova_act.types.act_errors import NoHumanInputToolAvailable

from examples.nova_act_client import NovaActClient
from examples.utils import get_logger

LOGGER = get_logger(__name__)


class ApprovalCallbacks(HumanInputCallbacksBase):
    """
    Implements an approval() callback which prompts user for their answer
    """

    def approve(self, message: str) -> ApprovalResponse:
        print(
            f"\n🤖 Approval required for act_id: {self.current_act_id} inside act_session_id: {self.act_session_id}:"
        )
        print(f"   {message}")

        while True:
            answer = input("   Please enter '(y)es' or '(n)o' to approve the request: ")
            if answer in ["n", "y"]:
                return (
                    ApprovalResponse.YES if answer == "y" else ApprovalResponse.CANCEL
                )

    def ui_takeover(self, message: str) -> UiTakeoverResponse:
        """See ui_takeover.py for a UI Takeover example"""
        raise NoHumanInputToolAvailable(message)


SCRIPT_DIR = str(Path(__file__).parent.absolute())


@workflow(**NovaActClient.get_workflow_kwargs())
def main():
    with NovaAct(
        starting_page=f"file://{SCRIPT_DIR}/ui/checkout.html",
        security_options=SecurityOptions(allowed_file_open_paths=[f"{SCRIPT_DIR}/*"]),
        human_input_callbacks=ApprovalCallbacks(),
        tty=False,
    ) as nova:
        result = nova.act_get(
            "Purchase the T Shirt. Ask for approval before order completion and return the order number."
        )
        order_number = result.parsed_response
        LOGGER.info(f"✓ Purchase complete with: {order_number}")


if __name__ == "__main__":
    main()
