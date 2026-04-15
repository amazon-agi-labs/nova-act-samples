"""Custom functions for test execution.

These functions can be called from Gherkin steps using function call syntax.
"""


def calculate_travel_cost(base_price: float, distance_multiplier: float) -> float:
    """Calculate travel cost based on base price and distance multiplier.

    Args:
        base_price: Base price for the journey
        distance_multiplier: Multiplier based on distance

    Returns:
        Total travel cost
    """
    return base_price * distance_multiplier


def format_destination_info(destination_name: str, mass: str) -> str:
    """Format destination information as a readable string.

    Args:
        destination_name: Name of the destination
        mass: Mass information

    Returns:
        Formatted string with destination info
    """
    return f"Destination: {destination_name}, Mass: {mass}"


def verify_page_contains_text(text: str, nova_act) -> bool:
    """Verify that the current page contains specific text.

    This function uses the reserved `nova_act` parameter to access
    the Nova Act instance for page inspection.

    Args:
        text: Text to search for
        nova_act: Nova Act instance (injected automatically)

    Returns:
        True if text is found, False otherwise
    """
    # Use Nova Act to check if text exists on the page
    result = nova_act.expect(f"The text '{text}' is visible on the page").as_boolean()
    return result


def get_extracted_variable(variable_name: str, context: dict) -> str:
    """Get a previously extracted variable from the context.

    This function uses the reserved `context` parameter to access
    extracted variables from previous steps.

    Args:
        variable_name: Name of the variable to retrieve
        context: Context dictionary (injected automatically)

    Returns:
        Value of the variable
    """
    variables = context.get('variables', {})
    if variable_name not in variables:
        raise ValueError(f"Variable '{variable_name}' not found in context")
    return str(variables[variable_name])
