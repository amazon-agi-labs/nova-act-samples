"""NovaActQa — NovaAct extension with QA assertions and extraction."""

from __future__ import annotations

import re
from typing import Self, cast, overload

from nova_act import NovaAct


class Expectation:
    """Assertion builder returned by ``NovaActQa.expect()``.

    Each method extracts a value from the page using the appropriate
    JSON schema and asserts against it.

    Example:
        nova.expect("Page title").to_equal("Dashboard")
        nova.expect("Cart total").to_be_greater_than(0)
        nova.expect("User is logged in").to_be_true()
    """

    def __init__(self, nova: NovaActQa, prompt: str) -> None:
        self._nova = nova
        self._prompt = prompt

    # ── Private extraction helpers ──────────────────────────────────────

    def _extract_string(self) -> str:
        result = self._nova.act_get(self._prompt, schema={"type": "string"})
        return cast(str, result.parsed_response)

    def _extract_number(self) -> float:
        result = self._nova.act_get(self._prompt, schema={"type": "number"})
        return cast(float, result.parsed_response)

    def _extract_boolean(self) -> bool:
        result = self._nova.act_get(self._prompt, schema={"type": "boolean"})
        return cast(bool, result.parsed_response)

    def _fail(self, default: str, msg: str | None) -> str:
        if msg is not None:
            return msg
        return f"[{self._prompt}] {default}"

    # ── Raw extraction (no assertion) ───────────────────────────────────

    def as_string(self) -> str:
        """Extract the value as a string without asserting."""
        return self._extract_string()

    def as_number(self) -> float:
        """Extract the value as a number without asserting."""
        return self._extract_number()

    def as_boolean(self) -> bool:
        """Extract the value as a boolean without asserting."""
        return self._extract_boolean()

    # ── Equality (type-dispatched) ──────────────────────────────────────

    @overload
    def to_equal(self, expected: bool, *, msg: str | None = None) -> bool: ...
    @overload
    def to_equal(self, expected: float, *, msg: str | None = None) -> float: ...
    @overload
    def to_equal(self, expected: str, *, msg: str | None = None) -> str: ...

    def to_equal(
        self, expected: str | float | bool, *, msg: str | None = None
    ) -> str | float | bool:
        """Extract a value and assert it equals ``expected``.

        The JSON schema is inferred from the type of ``expected``:
        bool → boolean, int/float → number, str → string.
        """
        if isinstance(expected, bool):
            actual = self._extract_boolean()
            assert actual == expected, self._fail(
                f"Expected {expected}, got {actual}", msg
            )
            return actual
        if isinstance(expected, (int, float)):
            actual = self._extract_number()
            assert actual == expected, self._fail(
                f"Expected {expected}, got {actual}", msg
            )
            return actual
        actual = self._extract_string()
        assert actual == expected, self._fail(
            f"Expected '{expected}', got '{actual}'", msg
        )
        return actual

    # ── String assertions ───────────────────────────────────────────────

    def to_contain(self, expected: str, *, msg: str | None = None) -> str:
        """Extract a string and assert it contains ``expected``."""
        actual = self._extract_string()
        assert expected in actual, self._fail(
            f"Expected '{actual}' to contain '{expected}'", msg
        )
        return actual

    def to_match(self, pattern: str, *, msg: str | None = None) -> str:
        r"""Extract a string and assert it matches regex ``pattern``."""
        actual = self._extract_string()
        assert re.match(pattern, actual), self._fail(
            f"Expected '{actual}' to match pattern '{pattern}'", msg
        )
        return actual

    # ── Number assertions ───────────────────────────────────────────────

    def to_be_greater_than(self, expected: float, *, msg: str | None = None) -> float:
        """Extract a number and assert it is > ``expected``."""
        actual = self._extract_number()
        assert actual > expected, self._fail(f"Expected {actual} > {expected}", msg)
        return actual

    def to_be_less_than(self, expected: float, *, msg: str | None = None) -> float:
        """Extract a number and assert it is < ``expected``."""
        actual = self._extract_number()
        assert actual < expected, self._fail(f"Expected {actual} < {expected}", msg)
        return actual

    def to_be_greater_or_equal(
        self, expected: float, *, msg: str | None = None
    ) -> float:
        """Extract a number and assert it is >= ``expected``."""
        actual = self._extract_number()
        assert actual >= expected, self._fail(f"Expected {actual} >= {expected}", msg)
        return actual

    def to_be_less_or_equal(self, expected: float, *, msg: str | None = None) -> float:
        """Extract a number and assert it is <= ``expected``."""
        actual = self._extract_number()
        assert actual <= expected, self._fail(f"Expected {actual} <= {expected}", msg)
        return actual

    # ── Boolean assertions ──────────────────────────────────────────────

    def to_be_true(self, *, msg: str | None = None) -> bool:
        """Extract a boolean and assert it is True."""
        actual = self._extract_boolean()
        assert actual is True, self._fail(f"Expected True, got {actual}", msg)
        return actual

    def to_be_false(self, *, msg: str | None = None) -> bool:
        """Extract a boolean and assert it is False."""
        actual = self._extract_boolean()
        assert actual is False, self._fail(f"Expected False, got {actual}", msg)
        return actual


class NovaActQa(NovaAct):
    """NovaAct extension with assertions and extraction for QA workflows.

    Example:
        with NovaActQa(starting_page="https://example.com") as nova:
            nova.expect("The page loads").to_be_true()
            nova.expect("Page title").to_equal("Dashboard")
            nova.expect("Cart total").to_be_greater_than(0)
            order_id = nova.expect("The order ID").as_string()
    """

    def __enter__(self) -> Self:
        """Enter the context manager, returning the NovaActQa instance."""
        super().__enter__()
        return self

    def expect(self, prompt: str) -> Expectation:
        """Begin an assertion or extraction for a natural-language prompt.

        Args:
            prompt: Natural language describing what to extract from the page.

        Returns:
            An ``Expectation`` with assertion and extraction methods.

        Example:
            nova.expect("Page title").to_equal("Dashboard")
            nova.expect("Cart total").to_be_greater_than(0)
            nova.expect("User is logged in").to_be_true()
            order_id = nova.expect("The order ID").as_string()
        """
        return Expectation(self, prompt)

    def check(self, prompt: str, *, msg: str | None = None) -> bool:
        """Shorthand for ``expect(prompt).to_be_true()``.

        Args:
            prompt: Natural language describing a boolean condition to verify.
            msg: Optional custom failure message.

        Returns:
            True if the check passes.

        Example:
            nova.check("The page loads")
            nova.check("User is logged in")
        """
        return self.expect(prompt).to_be_true(msg=msg)
