"""
Financial Analyst using Nova Act and Nova API.

A Strands Agent that uses Nova Act to extract stock symbols from websites
and Nova model to analyze market trends and provide insights into ticker performance.
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


class Stock(BaseModel):
    """A stock with symbol."""

    symbol: str


class StockList(BaseModel):
    """A list of stocks."""

    stocks: list[Stock]


# Define the Tool for strands to invoke to use Nova Act for research
@tool
@workflow(**get_workflow_kwargs())
def extract_stock_symbols(website_url: str, prompt: str) -> StockList:
    """Returns a list of stock symbols from a website using Nova Act."""
    with NovaAct(starting_page=website_url) as nova:
        result = nova.act_get(
            prompt,
            schema=StockList.model_json_schema(),
        )

        return StockList.model_validate(result.parsed_response)


# Create the Strands agent with Nova Model Provider and Nova Act Tool
agent = Agent(
    model=nova_model,
    tools=[extract_stock_symbols],
    system_prompt=(
        "You are a financial analyst specializing in stock analysis and market insights.\n\n"
        "Your expertise includes:\n"
        "- Analyzing individual stock performance and price movements\n"
        "- Understanding market dynamics and sector trends\n"
        "- Providing detailed insights into what drives stock performance\n"
        "- Explaining market sentiment and technical indicators\n\n"
        "When analyzing stocks, focus on:\n"
        "- Recent price performance and volatility\n"
        "- Sector and industry context\n"
        "- Market conditions affecting the stock\n"
        "- Technical patterns and trading volume\n"
        "- Key factors driving current performance"
    ),
)


def main(website_url: str, nova_act_prompt: str = "Find the top gainers"):
    """
    Run the financial analyst agent.

    Args:
        website_url: The website URL to extract stock data from (required)
        nova_act_prompt: Complete Nova Act prompt for stock extraction
    """
    # Extract stocks and analyze them
    response = agent(
        f"Extract stock symbols from {website_url} using the prompt '{nova_act_prompt}', then generate a report outlining each stocks performance. Analyze what's driving their current price movements, market sentiment, and key factors affecting their performance."
    )

    print(response)


if __name__ == "__main__":
    fire.Fire(main)