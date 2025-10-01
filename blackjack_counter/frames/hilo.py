"""Frame that implements the Hi-Lo counting layout."""

from tkinter import ttk
from typing import TYPE_CHECKING

from blackjack_counter.frames.base import BaseModeFrame

if TYPE_CHECKING:  # pragma: no cover - only for type checkers
    from blackjack_counter.app import CountingApp


class HiLoFrame(BaseModeFrame):
    """Four-column layout with high and low buttons for the Hi-Lo system."""

    def __init__(self, master: ttk.Frame, controller: "CountingApp") -> None:
        super().__init__(master, controller)

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=2)
        self.columnconfigure(2, weight=1)
        self.columnconfigure(3, weight=2)
        self.rowconfigure(0, weight=1)

        self._build_controls()

    def _build_controls(self) -> None:
        control_frame = ttk.Frame(self)
        control_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        ttk.Button(control_frame, text="Reset Shoe", command=self._reset_shoe).pack(fill="x", pady=(0, 10))
        ttk.Button(control_frame, text="Menu", command=self._go_menu).pack(fill="x")

        history_frame = ttk.Frame(self, padding=(10, 0))
        history_frame.grid(row=0, column=1, sticky="nsew")
        history_frame.columnconfigure(0, weight=1)

        history_box = ttk.LabelFrame(history_frame, text="Previously Counted", padding=10)
        history_box.grid(row=0, column=0, sticky="nsew")
        ttk.Label(history_box, textvariable=self.history_var, style="Caption.TLabel", anchor="center", justify="center", wraplength=1000).pack(fill="x")

        ttk.Button(history_frame, text="Low (+1)", command=lambda: self._record("Low", 1.0)).grid(row=1, column=0, sticky="ew", pady=(12, 0))

        true_frame = ttk.Frame(self, padding=(10, 0))
        true_frame.grid(row=0, column=2, sticky="nsew")
        true_frame.columnconfigure(0, weight=1)

        true_box = ttk.LabelFrame(true_frame, text="True Count", padding=10)
        true_box.grid(row=0, column=0, sticky="nsew")
        ttk.Label(true_box, textvariable=self.true_var, style="Value.TLabel", anchor="center").pack(fill="x")
        ttk.Label(true_box, textvariable=self.cards_var, style="Caption.TLabel", anchor="center").pack(fill="x", pady=(8, 0))

        ttk.Button(true_frame, text="Undo", command=self._undo_entry).grid(row=1, column=0, sticky="ew", pady=(12, 0))

        running_frame = ttk.Frame(self, padding=(10, 0))
        running_frame.grid(row=0, column=3, sticky="nsew")
        running_frame.columnconfigure(0, weight=1)

        running_box = ttk.LabelFrame(running_frame, text="Running Count", padding=10)
        running_box.grid(row=0, column=0, sticky="nsew")
        ttk.Label(running_box, textvariable=self.running_var, style="Value.TLabel", anchor="center").pack(fill="x")

        ttk.Button(running_frame, text="Hi (-1)", command=lambda: self._record("Hi", -1.0)).grid(row=1, column=0, sticky="ew", pady=(12, 0))

    def _record(self, label: str, value: float) -> None:
        if not self.state:
            return
        self.state.record(label, value)
        self.refresh()
