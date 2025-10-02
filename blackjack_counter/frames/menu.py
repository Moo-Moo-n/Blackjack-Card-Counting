"""Menu frames that handle app start and system selection."""

from tkinter import ttk
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:  # pragma: no cover - only for type checkers
    from blackjack_counter.app import CountingApp


class StartMenu(ttk.Frame):
    """Landing screen that offers a new game button."""

    def __init__(self, master: ttk.Frame, controller: "CountingApp") -> None:
        super().__init__(master, padding=40)
        self.controller = controller
        self._girl_label: Optional[ttk.Label] = None

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=0)

        column = ttk.Frame(self)
        column.grid(row=0, column=0, sticky="n")

        ttk.Label(column, text="Manual Blackjack Counter", style="Headline.TLabel").pack(pady=(0, 4))
        ttk.Label(column, text="by MooMoon", style="Subheadline.TLabel").pack(pady=(0, 20))
        ttk.Button(column, text="New Game", command=self._open_mode_selection, width=20).pack()

        bottom = ttk.Frame(self)
        bottom.grid(row=1, column=0, sticky="ew", pady=(12, 0))
        bottom.columnconfigure(0, weight=2)
        bottom.columnconfigure(1, weight=0)
        bottom.columnconfigure(2, weight=3)

        ttk.Label(
            bottom,
            text="Girl by Ralusek via Redbubble",
            style="Caption.TLabel",
            anchor="w",
        ).grid(row=0, column=0, sticky="sw")

        self._maybe_place_girl(bottom, column=1)

        ttk.Label(
            bottom,
            text="Icon by Freepik on Flaticon",
            style="Caption.TLabel",
            anchor="e",
        ).grid(row=0, column=2, sticky="se")

    def _maybe_place_girl(self, parent: ttk.Frame, *, column: int) -> None:
        image = getattr(self.controller, "girl_image", None)
        if not image:
            return

        self._girl_label = ttk.Label(parent, image=image)
        self._girl_label.image = image
        self._girl_label.grid(row=0, column=column, sticky="sw")

    def _open_mode_selection(self) -> None:
        self.controller.show_frame("ModeSelection")


class ModeSelection(ttk.Frame):
    """Let the player choose between the supported counting systems."""

    def __init__(self, master: ttk.Frame, controller: "CountingApp") -> None:
        super().__init__(master, padding=40)
        self.controller = controller
        self._girl_label: Optional[ttk.Label] = None

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=0)

        wrapper = ttk.Frame(self)
        wrapper.grid(row=0, column=0, sticky="n")

        ttk.Label(wrapper, text="Choose a Counting System", style="Subheadline.TLabel").pack(pady=(0, 20))

        ttk.Button(wrapper, text="Hi-Lo", width=20, command=self._start_hilo).pack(pady=6)
        ttk.Button(wrapper, text="Wong Halves", width=20, command=self._start_wong).pack(pady=6)
        ttk.Button(wrapper, text="Back", width=20, command=self._go_back).pack(pady=6)

        bottom = ttk.Frame(self)
        bottom.grid(row=1, column=0, sticky="ew", pady=(12, 0))
        bottom.columnconfigure(0, weight=2)
        bottom.columnconfigure(1, weight=0)
        bottom.columnconfigure(2, weight=3)

        ttk.Label(
            bottom,
            text="Girl by Ralusek via Redbubble",
            style="Caption.TLabel",
            anchor="w",
        ).grid(row=0, column=0, sticky="sw")

        self._maybe_place_girl(bottom, column=1)

        ttk.Frame(bottom).grid(row=0, column=2, sticky="ew")

    def _maybe_place_girl(self, parent: ttk.Frame, *, column: int) -> None:
        image = getattr(self.controller, "girl_image", None)
        if not image:
            return

        self._girl_label = ttk.Label(parent, image=image)
        self._girl_label.image = image
        self._girl_label.grid(row=0, column=column, sticky="sw")

    def _start_hilo(self) -> None:
        self.controller.start_mode("HiLoFrame")

    def _start_wong(self) -> None:
        self.controller.start_mode("WongHalvesFrame")

    def _go_back(self) -> None:
        self.controller.show_frame("StartMenu")



