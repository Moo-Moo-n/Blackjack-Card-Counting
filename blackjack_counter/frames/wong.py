"""Frame that implements the Wong Halves counting layout."""

# Wong Halves counting notes:
# - Each rank has a half-step weight (e.g., 5 = +1.5, 9 = -0.5) to better model the shoe.
# - The buttons for 2 through A add those fractional adjustments to the running count.
# - We keep the low/high shortcuts so players can apply generic +1/-1 presses as needed.

from tkinter import messagebox, ttk
from typing import Dict, Iterable, TYPE_CHECKING

from blackjack_counter.formatting import format_increment
from blackjack_counter.frames.base import BaseModeFrame

if TYPE_CHECKING:  # pragma: no cover - only for type checkers
    from blackjack_counter.app import CountingApp


class WongHalvesFrame(BaseModeFrame):
    """Two-pane layout with dedicated card buttons for Wong Halves."""

    CARD_VALUES = {
        "2": 0.5,
        "3": 1.0,
        "4": 1.0,
        "5": 1.5,
        "6": 1.0,
        "7": 0.5,
        "8": 0.0,
        "9": -0.5,
        "10": -1.0,
        "J": -1.0,
        "Q": -1.0,
        "K": -1.0,
        "A": -1.0,
    }

    # Keep the codex key layout + Hotkeys dialog
    CARD_KEY_BINDINGS: Dict[str, Iterable[str]] = {
        "2": ("q",),
        "3": ("w",),
        "4": ("e",),
        "5": ("r",),
        "6": ("a",),
        "7": ("s",),
        "8": ("d",),
        "9": ("f",),
        "10": ("g",),
        "J": ("z",),
        "Q": ("x",),
        "K": ("c",),
        "A": ("v",),
    }

    def __init__(self, master: ttk.Frame, controller: "CountingApp") -> None:
        super().__init__(master, controller)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=5)
        self.rowconfigure(1, weight=1)

        self._build_layout()

    def _build_layout(self) -> None:
        top_panel = ttk.Frame(self)
        top_panel.grid(row=0, column=0, sticky="nsew")

        bottom_panel = ttk.Frame(self, padding=(10, 6))
        bottom_panel.grid(row=1, column=0, sticky="nsew")

        top_panel.columnconfigure(0, weight=1)
        top_panel.columnconfigure(1, weight=2)
        top_panel.columnconfigure(2, weight=1)
        top_panel.columnconfigure(3, weight=1)
        top_panel.rowconfigure(0, weight=1)

        control_frame = ttk.Frame(top_panel)
        control_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        self.reset_button = ttk.Button(control_frame, text="Reset Shoe [Ctrl+R]", command=self._reset_shoe)
        self.reset_button.pack(fill="x", pady=(0, 10))
        self.menu_button = ttk.Button(control_frame, text="Menu", command=self._go_menu)
        self.menu_button.pack(fill="x")
        self.hotkey_button = ttk.Button(control_frame, text="Hotkeys…", command=self._show_hotkeys)
        self.hotkey_button.pack(fill="x", pady=(10, 0))

        history_frame = ttk.Frame(top_panel, padding=(10, 0))
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
        self._freeze_panel_width(history_frame, column_manager=top_panel, column_index=1, inner=history_box)

        self.low_button = ttk.Button(
            history_frame,
            text="Low (+1) [A/-/←]",
            command=lambda: self._record_generic("Low", 1.0),
        )
        self.low_button.grid(row=1, column=0, sticky="ew", pady=(12, 0))

        true_frame = ttk.Frame(top_panel, padding=(10, 0))
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

        running_frame = ttk.Frame(top_panel, padding=(10, 0))
        running_frame.grid(row=0, column=3, sticky="nsew")
        running_frame.columnconfigure(0, weight=1)

        running_box = ttk.LabelFrame(running_frame, text="Running Count", padding=10)
        running_box.grid(row=0, column=0, sticky="nsew")
        ttk.Label(running_box, textvariable=self.running_var, style="Value.TLabel", anchor="center").pack(fill="x")
        self.hi_button = ttk.Button(
            running_frame,
            text="Hi (-1) [D/+/→]",
            command=lambda: self._record_generic("Hi", -1.0),
        )
        self.hi_button.grid(row=1, column=0, sticky="ew", pady=(12, 0))

        for column in range(len(self.CARD_VALUES)):
            bottom_panel.columnconfigure(column, weight=1, uniform="cards")
        bottom_panel.rowconfigure(0, weight=1)

        cards = list(self.CARD_VALUES.items())
        for index, (card, value) in enumerate(cards):
            hints = " / ".join(key.upper() for key in self.CARD_KEY_BINDINGS.get(card, ()))
            label = f"{card}\n({format_increment(value)})"
            if hints:
                label += f"\n[{hints}]"

            ttk.Button(
                bottom_panel,
                text=label,
                style="Card.TButton",
                command=lambda c=card, v=value: self._record_card(c, v),
            ).grid(row=0, column=index, padx=2, pady=3, sticky="nsew")

    def _record_generic(self, label: str, value: float) -> None:
        """Record a quick +1/-1 adjustment alongside card-specific presses."""
        if not self.state:
            return
        self.state.record(label, value)
        self.refresh()

    def _record_card(self, card: str, value: float) -> None:
        """Log the fractional Wong Halves value for the chosen card rank."""
        if not self.state:
            return
        self.state.record(card, value)
        self.refresh()

    def on_show(self) -> None:
        super().on_show()

        def _wrap_generic(label: str, value: float):
            def handler(event):
                self._record_generic(label, value)
                return "break"
            return handler

        for sequence in ("<KeyPress-a>", "<KeyPress-A>", "<KeyPress-minus>", "<minus>", "<Left>"):
            self._bind_shortcut(sequence, _wrap_generic("Low", 1.0))

        for sequence in ("<KeyPress-d>", "<KeyPress-D>", "<KeyPress-plus>", "<plus>", "<Right>"):
            self._bind_shortcut(sequence, _wrap_generic("Hi", -1.0))

        for card, keys in self.CARD_KEY_BINDINGS.items():
            value = self.CARD_VALUES[card]

            def _make_handler(c: str, v: float):
                def handler(event):
                    self._record_card(c, v)
                    return "break"
                return handler

            handler = _make_handler(card, value)
            for key in keys:
                sequences = [f"<KeyPress-{key}>"]
                if key.isalpha():
                    sequences.append(f"<KeyPress-{key.upper()}>")
                for sequence in sequences:
                    self._bind_shortcut(sequence, handler)

    def on_hide(self) -> None:
        super().on_hide()

    def _show_hotkeys(self) -> None:
        """Display the key bindings for the Wong Halves layout."""
        card_hints = [
            "2: Q", "3: W", "4: E", "5: R",
            "6: A", "7: S", "8: D", "9: F",
            "10: G", "J: Z", "Q: X", "K: C", "A: V",
        ]
        hotkeys = (
            "Low (+1): A, -, Left Arrow",
            "Hi (-1): D, +, Right Arrow",
            "Cards:\n  " + "\n  ".join(card_hints),
            "Undo: <, ,, Ctrl+Z",
            "Redo: >, ., Ctrl+Shift+Z",
            "Reset Shoe: Ctrl+R",
        )
        messagebox.showinfo("Wong Halves Hotkeys", "\n\n".join(hotkeys), parent=self)
