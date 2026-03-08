"""Extract data from websites.

Shows how to use Nova Act to extract data from a website.

Usage:
# Default
python -m examples.data_extraction
# Specify a planet
python -m examples.data_extraction --planet <planet name from https://nova.amazon.com/act/gym/next-dot/>
"""

import fire
from nova_act import NovaAct, workflow
from pydantic import BaseModel

from examples.nova_act_client import NovaActClient
from examples.utils import get_logger

LOGGER = get_logger(__name__)


class Measurement(BaseModel):
    value: float
    unit: str


class PlanetData(BaseModel):
    gravity: Measurement
    average_temperature: Measurement


@workflow(**NovaActClient.get_workflow_kwargs())
def main(planet: str = "Proxima Centauri b") -> None:
    with NovaAct(starting_page="https://nova.amazon.com/act/gym/next-dot") as nova:
        # Extract the planet data
        result = nova.act_get(
            f"Go to the {planet} page and return the gravity and average temperature.",
            schema=PlanetData.model_json_schema(),
        )

        # Parse the response into the data model
        planet_data = PlanetData.model_validate(result.parsed_response)

        # Do something with the parsed data
        LOGGER.info(f"✓ {planet} data:\n{planet_data.model_dump_json(indent=2)}")


if __name__ == "__main__":
    fire.Fire(main)
