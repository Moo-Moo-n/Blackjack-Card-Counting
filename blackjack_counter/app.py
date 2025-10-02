"""Application bootstrap and top-level window management."""

import tkinter as tk
from tkinter import ttk
from typing import Dict, Optional

from pathlib import Path
import sys

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

        self._icon_image: Optional[tk.PhotoImage] = None
        self._apply_icon()
        self._init_style()

        self.girl_image: Optional[tk.PhotoImage] = self._load_girl_image()

        container = ttk.Frame(self)
        container.pack(fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames: Dict[str, ttk.Frame] = {}
        self._current_frame: Optional[ttk.Frame] = None
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

        if self._current_frame is not None and hasattr(self._current_frame, "on_hide"):
            self._current_frame.on_hide()  # type: ignore[call-arg]

        frame.tkraise()

        if hasattr(frame, "on_show"):
            frame.on_show()  # type: ignore[call-arg]

        self._current_frame = frame

    def start_mode(self, frame_name: str, decks: float = 6.0) -> None:
        frame = self.frames[frame_name]
        if hasattr(frame, "set_state"):
            frame.set_state(CountingState(decks=decks))  # type: ignore[attr-defined]
        self.show_frame(frame_name)

    def _load_girl_image(self) -> Optional[tk.PhotoImage]:
        """Load the girl illustration for reuse across frames."""

        asset_path = self._find_asset('torta_girl.png')
        if asset_path is None:
            return None

        try:
            image = tk.PhotoImage(file=str(asset_path))
        except tk.TclError:
            return None

        max_height = 220
        height = image.height()
        if height > max_height:
            scale = max(1, height // max_height)
            image = image.subsample(scale, scale)

        return image

    def _apply_icon(self) -> None:
        """Attach the table icon to the window when available."""

        icon_path = self._find_asset('blackjack_by_freepik.png')
        if icon_path is None:
            return
        try:
            icon = tk.PhotoImage(file=str(icon_path))
        except tk.TclError:
            return
        self._icon_image = icon
        self.iconphoto(True, icon)

    def _find_asset(self, filename: str) -> Optional[Path]:
        """Resolve asset path both in dev and PyInstaller bundles."""

        candidates = []
        if hasattr(sys, '_MEIPASS'):
            candidates.append(Path(sys._MEIPASS) / 'assets' / filename)
        candidates.append(Path(__file__).resolve().parent.parent / 'assets' / filename)
        for candidate in candidates:
            if candidate.exists():
                return candidate
        return None




