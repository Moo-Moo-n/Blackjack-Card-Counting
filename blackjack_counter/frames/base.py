"""Shared frame utilities for the different counting modes."""

import tkinter as tk
from tkinter import ttk
from typing import Optional, TYPE_CHECKING

from blackjack_counter.formatting import format_increment
from blackjack_counter.state import CountingState

if TYPE_CHECKING:  # pragma: no cover - only for type checkers
    from blackjack_counter.app import CountingApp


class BaseModeFrame(ttk.Frame):
    """Base layout that provides shared controls and data binding."""

    def __init__(self, master: ttk.Frame, controller: "CountingApp", **kwargs) -> None:
        super().__init__(master, padding=20, **kwargs)
        self.controller = controller
        self.state: Optional[CountingState] = None

        self.history_var = tk.StringVar(value="-")
        self.running_var = tk.StringVar(value="0")
        self.true_var = tk.StringVar(value="0.00")
        self.cards_var = tk.StringVar(value="Cards seen: 0")

    def set_state(self, state: CountingState) -> None:
        """Attach a new counting state and refresh the visuals."""

        self.state = state
        self.refresh()

    def refresh(self) -> None:
        """Pull data from the state object into the bound widgets."""

        if not self.state:
            return

        history_text = "  ".join(
            f"{entry.label}({format_increment(entry.value)})" for entry in self.state.history
        )
        self.history_var.set(history_text if history_text else "-")

        self.running_var.set(format_increment(self.state.running_count))
        self.true_var.set(f"{self.state.true_count:+.2f}")
        self.cards_var.set(f"Cards seen: {self.state.cards_seen}")

    def _bind_wraplength(self, label: ttk.Label, container: tk.Widget, padding: int = 18) -> None:
        """Keep label text wrapping in sync with the container width."""

        def _sync_wrap(event) -> None:
            usable_width = max(60, event.width - padding)
            label.configure(wraplength=usable_width)

        container.bind("<Configure>", _sync_wrap, add="+")
        container.after_idle(lambda: label.configure(wraplength=max(60, container.winfo_width() - padding)))

    def _reset_shoe(self) -> None:
        """Clear the shoe back to an empty state."""

        if not self.state:
            return
        self.state.reset()
        self.refresh()

    def _undo_entry(self) -> None:
        """Remove the most recent recorded value."""

        if not self.state:
            return
        removed = self.state.undo()
        if removed is not None:
            self.refresh()

    def _go_menu(self) -> None:
        """Return to the mode-selection screen."""

        self.controller.show_frame("ModeSelection")


