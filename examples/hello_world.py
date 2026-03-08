"""Hello World example.

A simple example to get started with.

Usage:
python -m examples.hello_world
"""

import fire
from nova_act import NovaAct, workflow

from examples.nova_act_client import NovaActClient


@workflow(**NovaActClient.get_workflow_kwargs())
def main() -> None:
    with NovaAct(
        starting_page="https://nova.amazon.com/act/gym/next-dot/search"
    ) as nova:
        nova.act("Find flights from Boston to Wolf on Feb 22nd")


if __name__ == "__main__":
    fire.Fire(main)
