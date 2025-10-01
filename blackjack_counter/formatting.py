"""Utility helpers used across the blackjack counter UI."""


def format_increment(value: float) -> str:
    """Format a running-count increment with clean trailing zeros."""

    rounded = round(value, 2)
    if abs(rounded) < 1e-9:
        rounded = 0.0
    if abs(rounded - round(rounded)) < 1e-9:
        return f"{int(round(rounded)):+d}"
    text = f"{rounded:+.2f}"
    if text.endswith("00"):
        text = text[:-3]
    elif text.endswith("0"):
        text = text[:-1]
    return text
