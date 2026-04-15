"""Function execution helpers - utilities for calling custom functions from tests."""

from typing import Any


def get_function_from_module(module: Any, function_name: str) -> callable:
    """Get a function from module, supporting dot notation.
    
    Args:
        module: The loaded Python module
        function_name: Function name (e.g., "calculate_discount" or "user_service.create_user")
        
    Returns:
        The callable function
        
    Raises:
        AttributeError: If function not found
    """
    if '.' in function_name:
        # Handle dot notation: "user_service.create_user"
        parts = function_name.split('.')
        obj = getattr(module, parts[0])
        for part in parts[1:]:
            obj = getattr(obj, part)
        return obj
    else:
        # Simple function name
        return getattr(module, function_name)
