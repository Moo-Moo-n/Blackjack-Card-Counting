"""Menu frames that handle app start and system selection."""

from tkinter import ttk
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover - only for type checkers
    from blackjack_counter.app import CountingApp


class StartMenu(ttk.Frame):
    """Landing screen that offers a new game button."""

    def __init__(self, master: ttk.Frame, controller: "CountingApp") -> None:
        super().__init__(master, padding=40)
        self.controller = controller

        column = ttk.Frame(self)
        column.pack(expand=True)

        ttk.Label(column, text="Manual Blackjack Counter", style="Headline.TLabel").pack(pady=(0, 4))
        ttk.Label(column, text="by MooMoon", style="Subheadline.TLabel").pack(pady=(0, 20))
        ttk.Button(column, text="New Game", command=self._open_mode_selection, width=20).pack()

        ttk.Label(self, text="Icon by Smashingstocks on Flaticon", style="Caption.TLabel").pack(side="bottom", pady=(20, 0))

    def _open_mode_selection(self) -> None:
        self.controller.show_frame("ModeSelection")


class ModeSelection(ttk.Frame):
    """Let the player choose between the supported counting systems."""

    def __init__(self, master: ttk.Frame, controller: "CountingApp") -> None:
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

