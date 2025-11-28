"""Search for a flight.

Shows how to use Nova Act to search for a flight.

Usage:
python -m examples.flight_search
"""

from datetime import datetime, timedelta
import fire  # type: ignore
from pydantic import BaseModel

from examples.utils import get_logger, get_workflow_kwargs

from nova_act import NovaAct, workflow

LOGGER = get_logger(__name__)


class Flight(BaseModel):
    number: str
    price: str


@workflow(**get_workflow_kwargs())
def main(origin: str = "Boston", destination: str = "Wolf", date: str | None = None) -> None:
    if not date:
        date = (datetime.now() + timedelta(days=30)).strftime("%B %d, %Y")

    with NovaAct(
        starting_page="https://nova.amazon.com/act/gym/next-dot/search"
    ) as nova:
        # Search and extract the flight data
        result = nova.act_get(
            f"Find flights from {origin} to {destination} on {date} and return the cheapest one.",
            schema=Flight.model_json_schema(),
        )

        # Parse the response into the data model
        flight = Flight.model_validate(result.parsed_response)

        # Do something with the parsed data
        LOGGER.info(f"✓ Flight data:\n{flight.model_dump_json(indent=2)}")


if __name__ == "__main__":
    fire.Fire(main)
