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
        self.geometry("1231x294")
        self.minsize(620, 160)
        self._base_window_size = (1231, 294)
        self._current_font_scale = 1.0

        self._icon_image: Optional[tk.PhotoImage] = None
        self._apply_icon()
        self._init_style()
        self._configure_responsive_fonts()

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
        self._base_fonts = {
            "Headline.TLabel": ("Segoe UI", 24, "bold"),
            "Subheadline.TLabel": ("Segoe UI", 16),
            "Value.TLabel": ("Segoe UI", 18, "bold"),
            "Caption.TLabel": ("Segoe UI", 10),
            "TButton": ("Segoe UI", 11),
            "Card.TButton": ("Segoe UI", 12),
        }
        self._base_paddings = {
            "TButton": (6, 4),
            "Card.TButton": (6, 4),
        }

        for style_name, font_spec in self._base_fonts.items():
            style.configure(style_name, font=font_spec)

        for style_name, padding in self._base_paddings.items():
            style.configure(style_name, padding=padding)

    def _configure_responsive_fonts(self) -> None:
        self.bind("<Configure>", self._on_main_configure, add="+")

    def _on_main_configure(self, event: tk.Event) -> None:
        if event.widget is not self:
            return

        width = max(1, event.width)
        height = max(1, event.height)
        base_width, base_height = self._base_window_size
        scale = min(width / base_width, height / base_height)
        scale = max(0.7, min(1.0, scale))
        if abs(scale - self._current_font_scale) < 0.02:
            return

        self._current_font_scale = scale
        self._apply_font_scale(scale)

    def _apply_font_scale(self, scale: float) -> None:
        style = ttk.Style(self)
        for style_name, font_spec in self._base_fonts.items():
            family = font_spec[0]
            size = font_spec[1]
            extras = font_spec[2:]
            new_size = max(8, round(size * scale))
            style.configure(style_name, font=(family, new_size, *extras))

        for style_name, padding in self._base_paddings.items():
            scaled_padding = tuple(max(2, round(value * scale)) for value in padding)
            style.configure(style_name, padding=scaled_padding)

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

