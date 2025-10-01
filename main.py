import tkinter as tk
from tkinter import ttk
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class CountEntry:
    label: str
    value: float


class CountingState:
    def __init__(self, decks: float = 6.0) -> None:
        self.decks_total = decks
        self.history: List[CountEntry] = []

    def reset(self) -> None:
        self.history.clear()

    def record(self, label: str, value: float) -> None:
        self.history.append(CountEntry(label, value))

    def undo(self) -> Optional[CountEntry]:
        if self.history:
            return self.history.pop()
        return None

    @property
    def running_count(self) -> float:
        return sum(entry.value for entry in self.history)

    @property
    def cards_seen(self) -> int:
        return len(self.history)

    @property
    def decks_remaining(self) -> float:
        remaining = self.decks_total - (self.cards_seen / 52.0)
        return remaining if remaining > 0 else 0.0

    @property
    def true_count(self) -> float:
        if not self.history:
            return 0.0
        decks_remaining = max(0.25, self.decks_remaining)
        return self.running_count / decks_remaining


def format_increment(value: float) -> str:
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


class CountingApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Blackjack Counter")
        self.geometry("1100x640")
        self.minsize(960, 540)

        self._init_style()

        container = ttk.Frame(self)
        container.pack(fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for FrameClass in (StartMenu, ModeSelection, HiLoFrame, WongHalvesFrame):
            frame = FrameClass(container, self)
            self.frames[FrameClass.__name__] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("StartMenu")

    def _init_style(self) -> None:
        style = ttk.Style(self)
        style.configure("Headline.TLabel", font=("Segoe UI", 24, "bold"))
        style.configure("Subheadline.TLabel", font=("Segoe UI", 16))
        style.configure("Value.TLabel", font=("Segoe UI", 18, "bold"))
        style.configure("Caption.TLabel", font=("Segoe UI", 10))
        style.configure("Card.TButton", padding=(6, 4))

    def show_frame(self, name: str) -> None:
        frame = self.frames[name]
        if hasattr(frame, "on_show"):
            frame.on_show()
        frame.tkraise()

    def start_mode(self, frame_name: str, decks: float = 6.0) -> None:
        frame = self.frames[frame_name]
        if isinstance(frame, BaseModeFrame):
            frame.set_state(CountingState(decks=decks))
        self.show_frame(frame_name)


class StartMenu(ttk.Frame):
    def __init__(self, master: ttk.Frame, controller: CountingApp) -> None:
        super().__init__(master, padding=40)
        self.controller = controller

        column = ttk.Frame(self)
        column.pack(expand=True)

        ttk.Label(column, text="Manual Blackjack Counter", style="Headline.TLabel").pack(pady=(0, 20))
        ttk.Button(column, text="New Game", command=self._open_mode_selection, width=20).pack()

    def _open_mode_selection(self) -> None:
        self.controller.show_frame("ModeSelection")


class ModeSelection(ttk.Frame):
    def __init__(self, master: ttk.Frame, controller: CountingApp) -> None:
        super().__init__(master, padding=40)
        self.controller = controller

        wrapper = ttk.Frame(self)
        wrapper.pack(expand=True)

        ttk.Label(wrapper, text="Choose a Counting System", style="Subheadline.TLabel").pack(pady=(0, 20))

        ttk.Button(wrapper, text="Hi-Lo", width=20, command=self._start_hilo).pack(pady=6)
        ttk.Button(wrapper, text="Wong Halves", width=20, command=self._start_wong).pack(pady=6)
        ttk.Button(wrapper, text="Back", width=20, command=self._go_back).pack(pady=6)

    def _start_hilo(self) -> None:
        self.controller.start_mode("HiLoFrame")

    def _start_wong(self) -> None:
        self.controller.start_mode("WongHalvesFrame")

    def _go_back(self) -> None:
        self.controller.show_frame("StartMenu")


class BaseModeFrame(ttk.Frame):
    def __init__(self, master: ttk.Frame, controller: CountingApp, **kwargs) -> None:
        super().__init__(master, padding=20, **kwargs)
        self.controller = controller
        self.state: Optional[CountingState] = None

        self.history_var = tk.StringVar(value="")
        self.running_var = tk.StringVar(value="0")
        self.true_var = tk.StringVar(value="0.00")
        self.cards_var = tk.StringVar(value="Cards seen: 0")

    def set_state(self, state: CountingState) -> None:
        self.state = state
        self.refresh()

    def refresh(self) -> None:
        if not self.state:
            return

        history_text = "  ".join(
            f"{entry.label}({format_increment(entry.value)})" for entry in self.state.history
        )
        self.history_var.set(history_text if history_text else "-")

        running = self.state.running_count
        self.running_var.set(format_increment(running))

        true_count = self.state.true_count
        self.true_var.set(f"{true_count:+.2f}")

        self.cards_var.set(f"Cards seen: {self.state.cards_seen}")

    def _reset_shoe(self) -> None:
        if not self.state:
            return
        self.state.reset()
        self.refresh()

    def _undo_entry(self) -> None:
        if not self.state:
            return
        removed = self.state.undo()
        if removed is not None:
            self.refresh()

    def _go_menu(self) -> None:
        self.controller.show_frame("ModeSelection")


class HiLoFrame(BaseModeFrame):
    def __init__(self, master: ttk.Frame, controller: CountingApp) -> None:
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
        ttk.Label(history_box, textvariable=self.history_var, style="Caption.TLabel", anchor="center", justify="center", wraplength=1_000).pack(fill="x")

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


class WongHalvesFrame(BaseModeFrame):
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

    def __init__(self, master: ttk.Frame, controller: CountingApp) -> None:
        super().__init__(master, controller)

        self.columnconfigure(0, weight=3)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        self._build_layout()

    def _build_layout(self) -> None:
        primary = ttk.Frame(self)
        primary.grid(row=0, column=0, sticky="nsew")

        primary.columnconfigure(0, weight=1)
        primary.columnconfigure(1, weight=2)
        primary.columnconfigure(2, weight=1)
        primary.columnconfigure(3, weight=2)
        primary.rowconfigure(0, weight=1)

        control_frame = ttk.Frame(primary)
        control_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        ttk.Button(control_frame, text="Reset Shoe", command=self._reset_shoe).pack(fill="x", pady=(0, 10))
        ttk.Button(control_frame, text="Menu", command=self._go_menu).pack(fill="x")

        history_frame = ttk.Frame(primary, padding=(10, 0))
        history_frame.grid(row=0, column=1, sticky="nsew")
        history_frame.columnconfigure(0, weight=1)
        history_box = ttk.LabelFrame(history_frame, text="Previously Counted", padding=10)
        history_box.grid(row=0, column=0, sticky="nsew")
        ttk.Label(history_box, textvariable=self.history_var, style="Caption.TLabel", anchor="center", justify="center", wraplength=1_000).pack(fill="x")
        ttk.Button(history_frame, text="Low (+1)", command=lambda: self._record_generic("Low", 1.0)).grid(row=1, column=0, sticky="ew", pady=(12, 0))

        true_frame = ttk.Frame(primary, padding=(10, 0))
        true_frame.grid(row=0, column=2, sticky="nsew")
        true_frame.columnconfigure(0, weight=1)
        true_box = ttk.LabelFrame(true_frame, text="True Count", padding=10)
        true_box.grid(row=0, column=0, sticky="nsew")
        ttk.Label(true_box, textvariable=self.true_var, style="Value.TLabel", anchor="center").pack(fill="x")
        ttk.Label(true_box, textvariable=self.cards_var, style="Caption.TLabel", anchor="center").pack(fill="x", pady=(8, 0))
        ttk.Button(true_frame, text="Undo", command=self._undo_entry).grid(row=1, column=0, sticky="ew", pady=(12, 0))

        running_frame = ttk.Frame(primary, padding=(10, 0))
        running_frame.grid(row=0, column=3, sticky="nsew")
        running_frame.columnconfigure(0, weight=1)
        running_box = ttk.LabelFrame(running_frame, text="Running Count", padding=10)
        running_box.grid(row=0, column=0, sticky="nsew")
        ttk.Label(running_box, textvariable=self.running_var, style="Value.TLabel", anchor="center").pack(fill="x")
        ttk.Button(running_frame, text="Hi (-1)", command=lambda: self._record_generic("Hi", -1.0)).grid(row=1, column=0, sticky="ew", pady=(12, 0))

        card_panel = ttk.Frame(self, padding=(10, 0))
        card_panel.grid(row=0, column=1, sticky="nsew")
        card_panel.rowconfigure(0, weight=1)
        card_panel.rowconfigure(1, weight=0)
        card_panel.columnconfigure(0, weight=1)

        buttons_frame = ttk.Frame(card_panel)
        buttons_frame.grid(row=1, column=0, sticky="ew")
        buttons_frame.columnconfigure(tuple(range(7)), weight=1)

        cards = list(self.CARD_VALUES.items())
        for index, (card, value) in enumerate(cards):
            row = index // 7
            col = index % 7
            ttk.Button(
                buttons_frame,
                text=f"{card}\n({format_increment(value)})",
                style="Card.TButton",
                command=lambda c=card, v=value: self._record_card(c, v),
            ).grid(row=row, column=col, padx=2, pady=3, sticky="ew")

    def _record_generic(self, label: str, value: float) -> None:
        if not self.state:
            return
        self.state.record(label, value)
        self.refresh()

    def _record_card(self, card: str, value: float) -> None:
        if not self.state:
            return
        self.state.record(card, value)
        self.refresh()


if __name__ == "__main__":
    app = CountingApp()
    app.mainloop()

