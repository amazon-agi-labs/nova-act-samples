"""Book a trip.

Shows how to use Nova Act to fill out a multi-step form to book a trip.

Usage:
python -m examples.booking
"""

import fire  # type: ignore

from examples.utils import get_logger, get_workflow_kwargs

from nova_act import NovaAct, workflow

LOGGER = get_logger(__name__)


@workflow(**get_workflow_kwargs())
def main() -> None:
    # Define form data, could be fetched from API
    form_data = {
        "name": "John Doe",
        "date_of_birth": "1/8/2025",
        "emergency_contact_name": "Jane Smith",
        "emergency_contact_relationship": "Spouse",
        "emergency_contact_phone": "555-555-5555",
        "medical_has_traveled_interstellar": "yes",
        "medical_implants": "no",
        "cabin_selection": "premium",
        "additional_cargo": "no",
        "payment_prepaid_code": "NOVAACT2025",
    }

    with NovaAct(
        starting_page="https://nova.amazon.com/act/gym/next-dot/booking/step/1"
    ) as nova:
        result = nova.act_get(
            f"Book a flight with the following data and return the booking number: {form_data}"
        )

        LOGGER.info(f"✓ Booking number: {result.parsed_response}")


if __name__ == "__main__":
    fire.Fire(main)
