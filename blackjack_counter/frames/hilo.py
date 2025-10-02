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

    def __init__(self, master: ttk.Frame, controller: "CountingApp") -> None:
        super().__init__(master, controller)

        self._is_active = False
        self._hotkey_window: Optional[tk.Toplevel] = None
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
        control_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        self.reset_button = ttk.Button(control_frame, text="Reset Shoe [Ctrl+R]", command=self._reset_shoe)
        self.reset_button.pack(fill="x", pady=(0, 10))
        self.menu_button = ttk.Button(control_frame, text="Menu", command=self._go_menu)
        self.menu_button.pack(fill="x")

        self.hotkey_button = ttk.Button(control_frame, text="Hotkeys…", command=self._show_hotkeys)
        self.hotkey_button.pack(fill="x", pady=(10, 0))

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

            text="Low (+1)",

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

            text="Hi (-1)",

            command=lambda: self._record("Hi", -1.0),
        )
        self.hi_button.grid(row=1, column=0, sticky="ew", pady=(12, 0))

    def _record(self, label: str, value: float) -> None:
        """Store the Hi-Lo adjustment so the shared state can update counts."""
        if not self.state:
            return
        self.state.record(label, value)
        self.refresh()

    def on_show(self) -> None:
        super().on_show()

        self._is_active = True

        for name in self._group_bindings:
            self._group_bindings[name] = []

        self._bind_enabled_hotkeys()

    def on_hide(self) -> None:
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

        actions_frame = ttk.LabelFrame(container, text="Other Controls", padding=10)
        actions_frame.grid(row=2, column=0, sticky="ew")
        actions_frame.columnconfigure(0, weight=1)

        ttk.Label(
            actions_frame,
            text="Undo: <, ,, Ctrl+Z\nRedo: >, ., Ctrl+Shift+Z\nReset Shoe: Ctrl+R",
            justify="left",
        ).grid(row=0, column=0, sticky="w")

        ttk.Button(container, text="Close", command=window.destroy).grid(
            row=3, column=0, sticky="e", pady=(12, 0)
        )

        window.bind("<Destroy>", self._on_hotkey_window_destroy)
        window.focus_force()

        self._hotkey_window = window

