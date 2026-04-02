"""NovaActMobileQa — NovaAct extension with mobile actuation and QA assertions."""

from __future__ import annotations

from typing import Self

from examples.actuation.mobile.nova_act_mobile.nova_act_mobile import NovaActMobile
from examples.qa.nova_act_qa.nova_act_qa import NovaActQa


class NovaActMobileQa(NovaActMobile, NovaActQa):
    """NovaAct with both mobile actuator support and QA assertions."""

    def __enter__(self) -> Self:
        super().__enter__()
        return self
