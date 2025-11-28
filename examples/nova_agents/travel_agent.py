"""
Travel Agent using Strands Agents with the Nova API and Nova Act.

Demonstrates how to use Nova Act as a tool within a Strands Agent configured with the Nova API
to extract destinations from the web and generate travel recommendations using Nova.

Usage:
python -m examples.nova_agents.travel_agent --num_planets 5
"""

import os

import fire
from nova_act import NovaAct, workflow
from pydantic import BaseModel
from strands import Agent, tool
from strands_nova import NovaModel

from examples.utils import get_workflow_kwargs


# Get and set Nova API key
nova_api_key = os.environ.get("NOVA_API_KEY")
if not nova_api_key:
    raise ValueError("NOVA_API_KEY environment variable is required")

# Initialize Nova Model Provider for Strands
nova_model = NovaModel(
    api_key=nova_api_key,
    model_id="nova-lite-v2",
    params={"system_tools": ["nova_grounding"]},
)


# Define classes for structured output with Nova Act


class Destination(BaseModel):
    """Schema for a single destination"""

    name: str


class DestinationList(BaseModel):
    """Schema for a list of destinations"""

    destinations: list[Destination]


# Define the Tool for strands to invoke to use Nova Act for research
@tool
@workflow(**get_workflow_kwargs())
def get_travel_destinations(num_destinations: int):
    """Returns a list of travel destinations from the web.

    Args:
        num_destinations: Number of destinations to retrieve from the page
    """
    with NovaAct(starting_page="https://nova.amazon.com/act/gym/next-dot") as nova:
        result = nova.act_get(
            f"Find the first {num_destinations} destinations",
            schema=DestinationList.model_json_schema(),
        )

        destinations = DestinationList.model_validate(result.parsed_response)
        destination_names = [
            destination.name for destination in destinations.destinations
        ]
        return destination_names


# Create the Strands agent with Nova Model Provider and Nova Act Tool
agent = Agent(
    model=nova_model,
    tools=[get_travel_destinations],
    system_prompt=(
        "You are the galaxy's most sarcastic and enthusiastic interstellar travel agent!\n\n"
        "Your expertise includes:\n"
        "- Planning hilarious family trips with kids to sci-fi exoplanet destinations\n"
        "- Writing entertaining reviews that mention actual science in parent language\n"
        "- Finding activities kids would love OR reasons parents wouldn't want to leave\n"
        "- Treating fictional exoplanets as real travel spots with humor and enthusiasm\n\n"
        "For each destination, provide:\n"
        "- A 2-word review title\n"
        "- Star rating out of 5\n"
        "- One funny review mentioning the actual science but in parent language\n"
        "- One activity the kids would actually love OR one reason the parents wouldn't want to leave\n\n"
        "This is completely fictional and fun - make these exoplanets feel like real travel destinations!"
    ),
)


def main(num_destinations: int = 5):
    print(
        f"🔍 Planning your trip with {num_destinations} destinations..."
    )

    response = agent(
        f"Get {num_destinations} sci-fi exoplanet travel destinations and plan a hilarious family trip that visits each of them."
    )

    print("\n📖 Travel recommendations:")
    print("=" * 50)
    print(response)


if __name__ == "__main__":
    fire.Fire(main)