"""Application bootstrap and top-level window management."""

import tkinter as tk
from tkinter import ttk
from typing import Dict

from blackjack_counter.frames.hilo import HiLoFrame
from blackjack_counter.frames.menu import ModeSelection, StartMenu
from blackjack_counter.frames.wong import WongHalvesFrame
from blackjack_counter.state import CountingState


class CountingApp(tk.Tk):
    """Main application window that manages frame navigation."""

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

        self.frames: Dict[str, ttk.Frame] = {}
        for frame_cls in (StartMenu, ModeSelection, HiLoFrame, WongHalvesFrame):
            frame = frame_cls(container, self)
            self.frames[frame_cls.__name__] = frame
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
            frame.on_show()  # type: ignore[call-arg]
        frame.tkraise()

    def start_mode(self, frame_name: str, decks: float = 6.0) -> None:
        frame = self.frames[frame_name]
        if hasattr(frame, "set_state"):
            frame.set_state(CountingState(decks=decks))  # type: ignore[attr-defined]
        self.show_frame(frame_name)
