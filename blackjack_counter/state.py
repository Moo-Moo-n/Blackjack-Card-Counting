"""Domain models that track running and true counts for the blackjack counter."""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class CountEntry:
    """Represents a single counting adjustment and its label."""

    label: str
    value: float


class CountingState:
    """Mutable state for the running and true counts across the shoe."""

    def __init__(self, decks: float = 6.0) -> None:
        self.decks_total = decks
        self.history: List[CountEntry] = []

    def reset(self) -> None:
        """Clear all recorded cards and adjustments."""

        self.history.clear()

    def record(self, label: str, value: float) -> None:
        """Append a new adjustment to the running count history."""

        self.history.append(CountEntry(label, value))

    def undo(self) -> Optional[CountEntry]:
        """Remove and return the most recent entry if one exists."""

        if self.history:
            return self.history.pop()
        return None

    @property
    def running_count(self) -> float:
        """Current running count derived from all history entries."""

        return sum(entry.value for entry in self.history)

    @property
    def cards_seen(self) -> int:
        """Total number of cards/presses recorded."""

        return len(self.history)

    @property
    def decks_remaining(self) -> float:
        """Estimated number of decks left, clamped to zero."""

        remaining = self.decks_total - (self.cards_seen / 52.0)
        return remaining if remaining > 0 else 0.0

    @property
    def true_count(self) -> float:
        """True count computed against the decks that remain."""

        if not self.history:
            return 0.0
        decks_remaining = max(0.25, self.decks_remaining)
        return self.running_count / decks_remaining
