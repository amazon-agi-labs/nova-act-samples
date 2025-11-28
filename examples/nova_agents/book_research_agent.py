"""
Book Research Agent using Strands Agents with the Nova API and Nova Act.

A Strands Agent that uses Nova Act to extract top books from websites
and Nova model to analyze why they're popular and recommend similar books.
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


class Book(BaseModel):
    """A book with title and author."""

    title: str
    author: str


class BookList(BaseModel):
    """A list of books."""

    books: list[Book]


# Define the Tool for strands to invoke to use Nova Act for research
@tool
@workflow(**get_workflow_kwargs())
def extract_top_books(website_url: str, prompt: str) -> BookList:
    """Extract top books from a website using Nova Act."""
    with NovaAct(starting_page=website_url) as nova:
        result = nova.act_get(
            prompt,
            schema=BookList.model_json_schema(),
        )

        return BookList.model_validate(result.parsed_response)


# Create the Strands agent with Nova Model Provider and Nova Act Tool
agent = Agent(
    model=nova_model,
    tools=[extract_top_books],
    system_prompt=(
        "You are a literary research assistant specializing in book analysis and recommendations.\n\n"
        "Your expertise includes:\n"
        "- Analyzing why books become popular or highly rated\n"
        "- Understanding literary trends and reader preferences\n"
        "- Recommending similar books based on themes, style, and appeal\n"
        "- Providing insights into what makes books successful\n\n"
        "When analyzing books, consider factors like:\n"
        "- Genre and themes\n"
        "- Writing style and narrative structure\n"
        "- Cultural relevance and timing\n"
        "- Author reputation and previous works\n"
        "- Reader demographics and preferences"
    ),
)


def main(website_url: str, nova_act_prompt: str = "Find the top 5 fiction books"):
    """
    Run the book research agent.

    Args:
        website_url: The website URL to extract books from (required)
        prompt: Complete Nova Act prompt for book extraction
    """
    # Extract books and analyze them
    response = agent(
        f"Extract books from {website_url} using the prompt '{nova_act_prompt}', then analyze why these books are popular and recommend 3 similar books for each one. Provide insights into what makes these books successful and appealing to readers."
    )

    print(response)


if __name__ == "__main__":
    fire.Fire(main)