"""Shared frame utilities for the different counting modes."""

import tkinter as tk
from tkinter import ttk
from typing import List, Optional, Tuple, TYPE_CHECKING

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

        self.reset_button: Optional[ttk.Button] = None
        self.menu_button: Optional[ttk.Button] = None
        self.undo_button: Optional[ttk.Button] = None
        self.redo_button: Optional[ttk.Button] = None

        self._shortcut_bindings: List[Tuple[str, str]] = []

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

        self._sync_control_states()

    def _sync_control_states(self) -> None:
        """Enable or disable undo/redo buttons based on availability."""

        undo_enabled = bool(self.state and self.state.can_undo)
        redo_enabled = bool(self.state and self.state.can_redo)

        if self.undo_button is not None:
            self.undo_button.configure(state="normal" if undo_enabled else "disabled")

        if self.redo_button is not None:
            self.redo_button.configure(state="normal" if redo_enabled else "disabled")

    def _bind_wraplength(self, label: ttk.Label, container: tk.Widget, padding: int = 18) -> None:
        """Keep label text wrapping in sync with the container width."""

        def _sync_wrap(event) -> None:
            usable_width = max(60, event.width - padding)
            label.configure(wraplength=usable_width)

        container.bind("<Configure>", _sync_wrap, add="+")
        container.after_idle(lambda: label.configure(wraplength=max(60, container.winfo_width() - padding)))


    def _freeze_panel_width(self, panel: tk.Widget, *, column_manager: tk.Widget, column_index: int, inner: Optional[tk.Widget] = None) -> None:
        """Keep a panel from growing wider than its initial width."""

        if getattr(panel, "_width_locked", False):
            return

        def _capture_width() -> None:
            panel.update_idletasks()
            width = panel.winfo_width()
            if width <= 1:
                panel.after(50, _capture_width)
                return

            column_manager.columnconfigure(column_index, weight=0, minsize=width)
            try:
                panel.configure(width=width)
            except tk.TclError:
                pass
            try:
                panel.grid_propagate(False)
            except tk.TclError:
                pass
            if inner is not None:
                try:
                    inner.configure(width=width)
                except tk.TclError:
                    pass
            panel._width_locked = True  # type: ignore[attr-defined]

        panel.after_idle(_capture_width)

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

    def _redo_entry(self) -> None:
        """Reapply the most recently undone value."""

        if not self.state:
            return
        restored = self.state.redo()
        if restored is not None:
            self.refresh()

    def _go_menu(self) -> None:
        """Return to the mode-selection screen."""

        self.controller.show_frame("ModeSelection")


    def _bind_shortcut(self, sequence: str, callback) -> str:

        """Register a keyboard shortcut and track it for later cleanup."""

        funcid = self.controller.bind(sequence, callback, add="+")
        self._shortcut_bindings.append((sequence, funcid))

        return funcid

    def _unbind_shortcut(self, sequence: str, funcid: str) -> None:
        """Remove a previously registered shortcut if it is active."""

        try:
            self.controller.unbind(sequence, funcid)
        finally:
            try:
                self._shortcut_bindings.remove((sequence, funcid))
            except ValueError:
                pass


    def on_show(self) -> None:
        """Prepare the frame when it becomes visible."""

        self.focus_set()
        self._shortcut_bindings.clear()

        def _wrap(action):
            def handler(event):
                action()
                return "break"

            return handler

        self._bind_shortcut("<Control-r>", _wrap(self._reset_shoe))
        for sequence in ("<less>", "<KeyPress-comma>", "<Control-z>"):
            self._bind_shortcut(sequence, _wrap(self._undo_entry))
        for sequence in ("<greater>", "<KeyPress-period>", "<Control-Shift-Z>"):
            self._bind_shortcut(sequence, _wrap(self._redo_entry))

    def on_hide(self) -> None:
        """Remove any active bindings before the frame is hidden."""

        for sequence, funcid in self._shortcut_bindings:
            self.controller.unbind(sequence, funcid)
        self._shortcut_bindings.clear()


