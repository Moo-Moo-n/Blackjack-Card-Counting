"""Frame that implements the Hi-Lo counting layout."""

# Hi-Lo counting notes:
# - Cards ranked 2 through 6 are considered "low" and add +1 to the running count.
# - Cards ranked 10, face cards, and aces are "high" and subtract 1 from the running count.
# - The interface mirrors that logic with Low/Hi buttons; each press records the adjustment and refreshes totals.


import tkinter as tk
from tkinter import ttk
from typing import TYPE_CHECKING, Dict, List, Optional, Tuple


from blackjack_counter.frames.base import BaseModeFrame

if TYPE_CHECKING:  # pragma: no cover - only for type checkers
    from blackjack_counter.app import CountingApp


class HiLoFrame(BaseModeFrame):
    """Four-column layout with high and low buttons for the Hi-Lo system."""

    LOW_CARD_LABELS: Tuple[str, ...] = ("2", "3", "4", "5", "6")
    HIGH_CARD_LABELS: Tuple[str, ...] = ("10", "J", "Q", "K", "A")
    RANK_MODE_ENTRIES: Tuple[Tuple[str, str, str], ...] = (
        ("2", "2", "low"),
        ("3", "3", "low"),
        ("4", "4", "low"),
        ("5", "5", "low"),
        ("6", "6", "low"),
        ("7", "7", "neutral"),
        ("8", "8", "neutral"),
        ("9", "9", "neutral"),
        ("0", "10", "hi"),
        ("q", "J", "hi"),
        ("w", "Q", "hi"),
        ("e", "K", "hi"),
        ("1", "A", "hi"),
    )

    def __init__(self, master: ttk.Frame, controller: "CountingApp") -> None:
        super().__init__(master, controller)

        self._is_active = False
        self._hotkey_window: Optional[tk.Toplevel] = None
        self._rank_mode_var = tk.BooleanVar(master=self, value=False)
        self._rank_bindings: List[Tuple[str, str]] = []
        self._rank_mode_active = False
        self._rank_info_label: Optional[ttk.Label] = None
        # Hotkey definitions live here; tweak sequences/filters below before they get bound.
        self._hotkey_groups = [
            {
                "name": "letters",
                "title": "Letters",
                "low_label": "L",
                "hi_label": "H",
                "low_sequences": ("<KeyPress-l>", "<KeyPress-L>"),
                "hi_sequences": ("<KeyPress-h>", "<KeyPress-H>"),
            },
            {
                "name": "adjacent",
                "title": "A / D",
                "low_label": "A",
                "hi_label": "D",
                "low_sequences": ("<KeyPress-a>", "<KeyPress-A>"),
                "hi_sequences": ("<KeyPress-d>", "<KeyPress-D>"),
            },
            {
                "name": "symbols",
                "title": "Minus / Plus",
                "low_label": "-",
                "hi_label": "+",
                "low_sequences": ("<KeyPress-minus>", "<minus>", "<KeyPress-KP_Subtract>", "<KP_Subtract>"),
                "hi_sequences": (
                    "<KeyPress-plus>",
                    "<plus>",
                    "<KeyPress-equal>",
                    "<equal>",
                    "<KeyPress-KP_Add>",
                    "<KP_Add>",
                ),
                "hi_expected_keysyms": ("plus", "equal", "KP_Add"),
            },
            {
                "name": "horizontal_arrows",
                "title": "Arrow Keys",
                "low_label": "←",
                "hi_label": "→",
                "low_sequences": ("<Left>",),
                "hi_sequences": ("<Right>",),
            },
            {
                "name": "vertical_arrows",
                "title": "Vertical Arrows",
                "low_label": "↓",
                "hi_label": "↑",
                "low_sequences": ("<Down>",),
                "hi_sequences": ("<Up>",),
            },
            {
                "name": "brackets",
                "title": "Brackets",
                "low_label": "[",
                "hi_label": "]",
                "low_sequences": ("<KeyPress-bracketleft>", "<bracketleft>"),
                "hi_sequences": ("<KeyPress-bracketright>", "<bracketright>"),
            },
        ]
        self._hotkey_lookup = {group["name"]: group for group in self._hotkey_groups}
        self._group_enabled: Dict[str, bool] = {
            group_name: True for group_name in self._hotkey_lookup
        }
        self._group_bindings: Dict[str, List[Tuple[str, str]]] = {
            group_name: [] for group_name in self._hotkey_lookup
        }
        self._hotkey_vars: Dict[str, tk.BooleanVar] = {
            name: tk.BooleanVar(master=self, value=True) for name in self._hotkey_lookup
        }

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=2)
        self.columnconfigure(2, weight=1)
        self.columnconfigure(3, weight=1)
        self.rowconfigure(0, weight=1)

        self._build_controls()

    def _build_controls(self) -> None:
        control_frame = ttk.Frame(self)
        control_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        self.reset_button = ttk.Button(control_frame, text="Reset Shoe [Ctrl+R]", command=self._reset_shoe)
        self.reset_button.pack(fill="x", pady=(0, 6))
        self.menu_button = ttk.Button(control_frame, text="Menu", command=self._go_menu)
        self.menu_button.pack(fill="x")

        self.hotkey_button = ttk.Button(control_frame, text="Hotkeys…", command=self._show_hotkeys)
        self.hotkey_button.pack(fill="x", pady=(6, 0))

        history_frame = ttk.Frame(self, padding=(6, 0))
        history_frame.grid(row=0, column=1, sticky="nsew")
        history_frame.columnconfigure(0, weight=1)
        history_frame.rowconfigure(0, weight=1)

        history_box = ttk.LabelFrame(history_frame, text="Previously Counted", padding=8)
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

        reference_frame = ttk.Frame(history_frame)
        reference_frame.grid(row=1, column=0, sticky="ew", pady=(8, 0))
        reference_frame.columnconfigure(0, weight=1)
        reference_frame.columnconfigure(1, weight=1)

        low_frame = ttk.LabelFrame(reference_frame, text="Low Cards (+1)", padding=6)
        low_frame.grid(row=0, column=0, sticky="ew", padx=(0, 4))
        ttk.Label(
            low_frame,
            text=" ".join(self.LOW_CARD_LABELS),
            anchor="center",
            justify="center",
        ).pack(fill="x")

        high_frame = ttk.LabelFrame(reference_frame, text="High Cards (-1)", padding=6)
        high_frame.grid(row=0, column=1, sticky="ew", padx=(4, 0))
        ttk.Label(
            high_frame,
            text=" ".join(self.HIGH_CARD_LABELS),
            anchor="center",
            justify="center",
        ).pack(fill="x")

        button_bar = ttk.Frame(history_frame)
        button_bar.grid(row=2, column=0, sticky="ew", pady=(8, 0))
        button_bar.columnconfigure(0, weight=1, uniform="history_hi_lo")
        button_bar.columnconfigure(1, weight=1, uniform="history_hi_lo")

        self.low_button = ttk.Button(
            button_bar,

            text="Low (+1)",

            command=lambda: self._record("Low", 1.0),
        )
        self.low_button.grid(row=0, column=0, sticky="ew", padx=(0, 4))

        self.hi_button = ttk.Button(
            button_bar,

            text="Hi (-1)",

            command=lambda: self._record("Hi", -1.0),
        )
        self.hi_button.grid(row=0, column=1, sticky="ew")

        true_frame = ttk.Frame(self, padding=(6, 0))
        true_frame.grid(row=0, column=2, sticky="nsew")
        true_frame.columnconfigure(0, weight=1)
        true_frame.bind("<Configure>", self._update_history_column_minsize, add="+")

        true_box = ttk.LabelFrame(true_frame, text="True Count", padding=8)
        true_box.grid(row=0, column=0, sticky="nsew")
        ttk.Label(true_box, textvariable=self.true_var, style="Value.TLabel", anchor="center").pack(fill="x")
        ttk.Label(true_box, textvariable=self.cards_var, style="Caption.TLabel", anchor="center").pack(fill="x", pady=(6, 0))

        self.undo_button = ttk.Button(true_frame, text="Undo [< / Ctrl+Z]", command=self._undo_entry)
        self.undo_button.grid(row=1, column=0, sticky="ew", pady=(8, 4))
        self.redo_button = ttk.Button(true_frame, text="Redo [> / Ctrl+Shift+Z]", command=self._redo_entry)
        self.redo_button.grid(row=2, column=0, sticky="ew")

        running_frame = ttk.Frame(self, padding=(6, 0))
        running_frame.grid(row=0, column=3, sticky="nsew")
        running_frame.columnconfigure(0, weight=1)
        running_frame.rowconfigure(0, weight=0)
        running_frame.rowconfigure(1, weight=1)

        running_box = ttk.LabelFrame(running_frame, text="Running Count", padding=8)
        running_box.grid(row=0, column=0, sticky="new")
        ttk.Label(running_box, textvariable=self.running_var, style="Value.TLabel", anchor="center").pack(fill="x")

    def _record(self, label: str, value: float) -> None:
        """Store the Hi-Lo adjustment so the shared state can update counts."""
        if not self.state:
            return
        self.state.record(label, value)
        self.refresh()

    def _update_history_column_minsize(self, event: tk.Event) -> None:
        """Keep the history column allowed to shrink down to the true-count width."""

        width = max(1, event.width)
        self.columnconfigure(1, minsize=width)

    def _toggle_rank_mode(self) -> None:
        """Enable or disable rank-based shortcuts based on the checkbox state."""

        enabled = self._rank_mode_var.get()
        if enabled:
            if self._is_active:
                self._bind_rank_keys()
        else:
            self._unbind_rank_keys()
        self._refresh_rank_mode_ui()

    def _bind_rank_keys(self) -> None:
        """Attach key bindings for each rank-to-action mapping."""

        if self._rank_mode_active:
            return

        self._rank_bindings = []

        for key, _card, category in self.RANK_MODE_ENTRIES:
            if category == "low":
                handler = self._handle_low_key
            elif category == "hi":
                handler = self._handle_hi_key
            else:
                continue

            sequences = [f"<KeyPress-{key}>"]
            if key.isalpha():
                sequences.append(f"<KeyPress-{key.upper()}>")

            for sequence in sequences:
                funcid = self._bind_shortcut(sequence, handler)
                self._rank_bindings.append((sequence, funcid))

        self._rank_mode_active = True

    def _unbind_rank_keys(self) -> None:
        """Remove rank-based key bindings if they are active."""

        if not self._rank_bindings:
            self._rank_mode_active = False
            return

        for sequence, funcid in self._rank_bindings:
            self._unbind_shortcut(sequence, funcid)

        self._rank_bindings = []
        self._rank_mode_active = False

    def _refresh_rank_mode_ui(self) -> None:
        """Update the descriptive text shown in the rank-mode section."""

        if self._rank_info_label is None:
            return

        if self._rank_mode_var.get():
            low_entries: List[str] = []
            high_entries: List[str] = []
            neutral_entries: List[str] = []

            for key, card, category in self.RANK_MODE_ENTRIES:
                key_display = key.upper() if key.isalpha() else key
                entry = f"{card} [{key_display}]"
                if category == "low":
                    low_entries.append(entry)
                elif category == "hi":
                    high_entries.append(entry)
                else:
                    neutral_entries.append(entry)

            lines = [
                "Low (+1): " + ", ".join(low_entries),
                "High (-1): " + ", ".join(high_entries),
            ]
            if neutral_entries:
                lines.append("Neutral (0): " + ", ".join(neutral_entries) + " (no change)")
            text = "\n".join(lines)
        else:
            text = "Enable rank mode to use card-rank shortcuts (2-A)."

        self._rank_info_label.configure(text=text)

    def on_show(self) -> None:
        super().on_show()

        self._is_active = True

        for name in self._group_bindings:
            self._group_bindings[name] = []

        self._bind_enabled_hotkeys()
        if self._rank_mode_var.get():
            self._bind_rank_keys()

    def on_hide(self) -> None:
        self._unbind_rank_keys()
        self._is_active = False

        if self._hotkey_window is not None and self._hotkey_window.winfo_exists():
            self._hotkey_window.destroy()

        super().on_hide()

        for name in self._group_bindings:
            self._group_bindings[name] = []

    def _handle_low_key(self, event) -> str:
        self._record("Low", 1.0)
        return "break"

    def _handle_hi_key(self, event) -> str:
        self._record("Hi", -1.0)
        return "break"

    def _bind_enabled_hotkeys(self) -> None:
        for name, enabled in self._group_enabled.items():
            if enabled:
                self._bind_hotkey_group(name)

    def _char_filtered_handler(self, handler, *, expected_char: Optional[str], expected_keysyms: Tuple[str, ...]):
        """Return a handler that only fires when the expected char or keysym is pressed."""

        def _filtered(event):
            char = getattr(event, "char", "")
            keysym = getattr(event, "keysym", "")
            if expected_char is not None and char == expected_char:
                return handler(event)
            if expected_keysyms and keysym in expected_keysyms:
                return handler(event)
            return None

        return _filtered

    def _bind_hotkey_group(self, name: str) -> None:
        self._unbind_hotkey_group(name)

        group = self._hotkey_lookup[name]
        low_expected_char = group.get("low_expected_char")
        low_expected_keysyms: Tuple[str, ...] = tuple(group.get("low_expected_keysyms", ()))
        if low_expected_char is None and not low_expected_keysyms:
            low_handler = self._handle_low_key
        else:
            low_handler = self._char_filtered_handler(
                self._handle_low_key,
                expected_char=low_expected_char,
                expected_keysyms=low_expected_keysyms,
            )

        hi_expected_char = group.get("hi_expected_char")
        hi_expected_keysyms: Tuple[str, ...] = tuple(group.get("hi_expected_keysyms", ()))
        if hi_expected_char is None and not hi_expected_keysyms:
            hi_handler = self._handle_hi_key
        else:
            hi_handler = self._char_filtered_handler(
                self._handle_hi_key,
                expected_char=hi_expected_char,
                expected_keysyms=hi_expected_keysyms,
            )

        bindings: List[Tuple[str, str]] = []

        for seq in group["low_sequences"]:
            funcid = self._bind_shortcut(seq, low_handler)
            bindings.append((seq, funcid))

        for seq in group["hi_sequences"]:
            funcid = self._bind_shortcut(seq, hi_handler)
            bindings.append((seq, funcid))

        self._group_bindings[name] = bindings

    def _unbind_hotkey_group(self, name: str) -> None:
        bindings = self._group_bindings.get(name)
        if not bindings:
            return

        for sequence, funcid in bindings:
            self._unbind_shortcut(sequence, funcid)

        self._group_bindings[name] = []

    def _set_hotkey_group_enabled(self, name: str, enabled: bool) -> None:
        previous = self._group_enabled.get(name, True)
        self._group_enabled[name] = enabled

        if not self._is_active:
            return

        if enabled and not previous:
            self._bind_hotkey_group(name)
        elif not enabled and previous:
            self._unbind_hotkey_group(name)

    def _toggle_hotkey_group(self, name: str) -> None:
        enabled = self._hotkey_vars[name].get()
        self._set_hotkey_group_enabled(name, enabled)

    def _on_hotkey_window_destroy(self, event) -> None:
        if event.widget is self._hotkey_window:
            self._hotkey_window = None
            self._rank_info_label = None

    def _show_hotkeys(self) -> None:
        """Present a toggleable reference of the Hi-Lo keyboard shortcuts."""

        if self._hotkey_window is not None and self._hotkey_window.winfo_exists():
            self._hotkey_window.lift()
            self._hotkey_window.focus_force()
            return

        window = tk.Toplevel(self)
        window.title("Hi-Lo Hotkeys")
        window.resizable(False, False)
        window.transient(self.winfo_toplevel())

        container = ttk.Frame(window, padding=16)
        container.grid(row=0, column=0, sticky="nsew")
        window.columnconfigure(0, weight=1)
        window.rowconfigure(0, weight=1)

        ttk.Label(
            container,
            text="Toggle any pair to enable or disable its keyboard shortcut.",
            style="Caption.TLabel",
            anchor="w",
            justify="left",
        ).grid(row=0, column=0, sticky="w")

        groups_frame = ttk.Frame(container)
        groups_frame.grid(row=1, column=0, sticky="nsew", pady=(12, 12))
        groups_frame.columnconfigure(0, weight=1)
        groups_frame.columnconfigure(1, weight=1)

        for index, group in enumerate(self._hotkey_groups):
            row, column = divmod(index, 2)
            groups_frame.rowconfigure(row, weight=1)
            card = ttk.LabelFrame(groups_frame, text=group["title"], padding=10)
            card.grid(row=row, column=column, padx=6, pady=6, sticky="nsew")
            card.columnconfigure(0, weight=1)
            card.columnconfigure(1, weight=1)

            ttk.Label(card, text=f"Low: {group['low_label']}", anchor="center").grid(
                row=0, column=0, sticky="ew"
            )
            ttk.Label(card, text=f"Hi: {group['hi_label']}", anchor="center").grid(
                row=0, column=1, sticky="ew"
            )

            check = ttk.Checkbutton(
                card,
                text="Enabled",
                variable=self._hotkey_vars[group["name"]],
                command=lambda name=group["name"]: self._toggle_hotkey_group(name),
            )
            check.grid(row=1, column=0, columnspan=2, pady=(8, 0))

        rank_frame = ttk.LabelFrame(container, text="Rank Mode", padding=10)
        rank_frame.grid(row=2, column=0, sticky="ew", pady=(0, 12))
        rank_frame.columnconfigure(0, weight=1)

        ttk.Checkbutton(
            rank_frame,
            text="Enable rank-based hotkeys (2-A)",
            variable=self._rank_mode_var,
            command=self._toggle_rank_mode,
        ).grid(row=0, column=0, sticky="w")

        self._rank_info_label = ttk.Label(rank_frame, anchor="w", justify="left")
        self._rank_info_label.grid(row=1, column=0, sticky="ew", pady=(8, 0))
        self._refresh_rank_mode_ui()

        actions_frame = ttk.LabelFrame(container, text="Other Controls", padding=10)
        actions_frame.grid(row=3, column=0, sticky="ew")
        actions_frame.columnconfigure(0, weight=1)

        ttk.Label(
            actions_frame,
            text="Shortcut hints are shown on each matching button in the main window.",
            justify="left",
            anchor="w",
        ).grid(row=0, column=0, sticky="w")

        ttk.Button(container, text="Close", command=window.destroy).grid(
            row=4, column=0, sticky="e", pady=(12, 0)
        )

        window.bind("<Destroy>", self._on_hotkey_window_destroy)
        window.focus_force()

        self._hotkey_window = window




