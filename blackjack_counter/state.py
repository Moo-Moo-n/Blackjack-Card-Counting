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
        self._redo_stack: List[CountEntry] = []
        self._undo_limit = 5
        self._redo_limit = 20
        self._undos_since_record = 0

    def reset(self) -> None:
        """Clear all recorded cards and adjustments."""

        self.history.clear()
        self._redo_stack.clear()
        self._undos_since_record = 0

    def record(self, label: str, value: float) -> None:
        """Append a new adjustment to the running count history."""

        self.history.append(CountEntry(label, value))
        self._redo_stack.clear()
        self._undos_since_record = 0

    def undo(self) -> Optional[CountEntry]:
        """Remove and return the most recent entry if one exists."""

        if not self.history or self._undos_since_record >= self._undo_limit:
            return None

        entry = self.history.pop()
        self._redo_stack.append(entry)
        self._undos_since_record += 1

        if len(self._redo_stack) > self._redo_limit:
            self._redo_stack.pop(0)

        return entry

    def redo(self) -> Optional[CountEntry]:
        """Reapply the most recently undone entry if available."""

        if not self._redo_stack:
            return None

        entry = self._redo_stack.pop()
        self.history.append(entry)
        if self._undos_since_record:
            self._undos_since_record -= 1
        return entry

    @property
    def can_undo(self) -> bool:
        """Indicate whether an undo action is currently allowed."""

        return bool(self.history) and self._undos_since_record < self._undo_limit

    @property
    def can_redo(self) -> bool:
        """Indicate whether a redo action is currently allowed."""

        return bool(self._redo_stack)

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
