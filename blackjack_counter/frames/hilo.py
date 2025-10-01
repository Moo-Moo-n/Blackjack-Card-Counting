"""Frame that implements the Hi-Lo counting layout."""

# Hi-Lo counting notes:
# - Cards ranked 2 through 6 are considered "low" and add +1 to the running count.
# - Cards ranked 10, face cards, and aces are "high" and subtract 1 from the running count.
# - The interface mirrors that logic with Low/Hi buttons; each press records the adjustment and refreshes totals.

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
        self.columnconfigure(3, weight=1)
        self.rowconfigure(0, weight=1)

        self._build_controls()

    def _build_controls(self) -> None:
        control_frame = ttk.Frame(self)
        control_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        self.reset_button = ttk.Button(control_frame, text="Reset Shoe [Ctrl+R]", command=self._reset_shoe)
        self.reset_button.pack(fill="x", pady=(0, 10))
        self.menu_button = ttk.Button(control_frame, text="Menu", command=self._go_menu)
        self.menu_button.pack(fill="x")

        history_frame = ttk.Frame(self, padding=(10, 0))
        history_frame.grid(row=0, column=1, sticky="nsew")
        history_frame.columnconfigure(0, weight=1)

        history_box = ttk.LabelFrame(history_frame, text="Previously Counted", padding=10)
        history_box.grid(row=0, column=0, sticky="nsew")
        history_label = ttk.Label(
            history_box,
            textvariable=self.history_var,
            style="Caption.TLabel",
            anchor="w",
            justify="left",
        )
        history_label.pack(fill="x")
        self._bind_wraplength(history_label, history_box)
        self._freeze_panel_width(history_frame, column_manager=self, column_index=1, inner=history_box)

        self.low_button = ttk.Button(
            history_frame,
            text="Low (+1) [A/-/←]",
            command=lambda: self._record("Low", 1.0),
        )
        self.low_button.grid(row=1, column=0, sticky="ew", pady=(12, 0))

        true_frame = ttk.Frame(self, padding=(10, 0))
        true_frame.grid(row=0, column=2, sticky="nsew")
        true_frame.columnconfigure(0, weight=1)

        true_box = ttk.LabelFrame(true_frame, text="True Count", padding=10)
        true_box.grid(row=0, column=0, sticky="nsew")
        ttk.Label(true_box, textvariable=self.true_var, style="Value.TLabel", anchor="center").pack(fill="x")
        ttk.Label(true_box, textvariable=self.cards_var, style="Caption.TLabel", anchor="center").pack(fill="x", pady=(8, 0))

        self.undo_button = ttk.Button(true_frame, text="Undo [< / Ctrl+Z]", command=self._undo_entry)
        self.undo_button.grid(row=1, column=0, sticky="ew", pady=(12, 6))
        self.redo_button = ttk.Button(true_frame, text="Redo [> / Ctrl+Shift+Z]", command=self._redo_entry)
        self.redo_button.grid(row=2, column=0, sticky="ew")

        running_frame = ttk.Frame(self, padding=(10, 0))
        running_frame.grid(row=0, column=3, sticky="nsew")
        running_frame.columnconfigure(0, weight=1)

        running_box = ttk.LabelFrame(running_frame, text="Running Count", padding=10)
        running_box.grid(row=0, column=0, sticky="nsew")
        ttk.Label(running_box, textvariable=self.running_var, style="Value.TLabel", anchor="center").pack(fill="x")

        self.hi_button = ttk.Button(
            running_frame,
            text="Hi (-1) [D/+/→]",
            command=lambda: self._record("Hi", -1.0),
        )
        self.hi_button.grid(row=1, column=0, sticky="ew", pady=(12, 0))

    def _record(self, label: str, value: float) -> None:
        """Store the Hi-Lo adjustment so the shared state can update counts."""

        if not self.state:
            return
        # Each button press appends a CountEntry. BaseModeFrame.refresh() recomputes
        # the running and true counts from that history so the labels stay current.
        self.state.record(label, value)
        self.refresh()

    def on_show(self) -> None:
        super().on_show()

        def _wrap_low(event):
            self._record("Low", 1.0)
            return "break"

        def _wrap_hi(event):
            self._record("Hi", -1.0)
            return "break"

        for sequence in (
            "<KeyPress-a>",
            "<KeyPress-A>",
            "<KeyPress-minus>",
            "<minus>",
            "<Left>",
        ):
            self._bind_shortcut(sequence, _wrap_low)

        for sequence in (
            "<KeyPress-d>",
            "<KeyPress-D>",
            "<KeyPress-plus>",
            "<plus>",
            "<Right>",
        ):
            self._bind_shortcut(sequence, _wrap_hi)

    def on_hide(self) -> None:
        super().on_hide()
