"""Console-based human-in-the-loop callbacks for session persistence examples.

Provides a shared HITL implementation used by all session persistence examples
to handle manual login flows during browser automation.
"""

from nova_act.tools.human.interface.human_input_callback import (
    ApprovalResponse,
    HumanInputCallbacksBase,
    UiTakeoverResponse,
)


class ConsoleHumanInputCallbacks(HumanInputCallbacksBase):
    """Human-in-the-loop callbacks for console-based interaction.

    Implements UI takeover by prompting the user in the terminal to complete
    an action (typically login) in the browser, then pressing Enter to resume.
    """

    def approve(self, message: str) -> ApprovalResponse:
        raise NotImplementedError()

    def ui_takeover(self, message: str) -> UiTakeoverResponse:
        print("\n--- Human takeover requested ---")
        print(f"   {message}")
        print("    Complete the action in the browser, then press Enter.")
        input("    Press Enter when done: \n")
        return UiTakeoverResponse.COMPLETE
