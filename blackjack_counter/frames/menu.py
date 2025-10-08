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
        column.pack(expand=True, fill="both")
        column.grid_columnconfigure(0, weight=1)
        column.grid_rowconfigure(0, weight=0)
        column.grid_rowconfigure(1, weight=0)
        column.grid_rowconfigure(2, weight=0)
        column.grid_rowconfigure(3, weight=1)

        ttk.Label(column, text="Manual Blackjack Counter", style="Headline.TLabel").grid(row=0, column=0, pady=(0, 4), sticky="n")
        ttk.Label(column, text="by MooMoon", style="Subheadline.TLabel").grid(row=1, column=0, pady=(0, 12), sticky="n")

        button_container = ttk.Frame(column)
        button_container.grid(row=2, column=0, sticky="n", pady=(6, 0))
        button_container.grid_columnconfigure(0, weight=1)

        self._start_button = ttk.Button(button_container, text="New Game", command=self._open_mode_selection, width=16)
        self._start_button.grid(row=0, column=0, padx=6, pady=6, sticky="ew")

        wrapper_bottom = ttk.Frame(self)
        wrapper_bottom.pack(fill="x", side="bottom")
        ttk.Label(wrapper_bottom, text="Icon by Freepik on Flaticon", style="Caption.TLabel").pack(pady=(12, 0))

    def _open_mode_selection(self) -> None:
        self.controller.show_frame("ModeSelection")


class ModeSelection(ttk.Frame):
    """Let the player choose between the supported counting systems."""

    def __init__(self, master: ttk.Frame, controller: "CountingApp") -> None:
        super().__init__(master, padding=40)
        self.controller = controller

        wrapper = ttk.Frame(self)
        wrapper.pack(expand=True, fill="both")

        ttk.Label(wrapper, text="Choose a Counting System", style="Subheadline.TLabel").pack(pady=(0, 20))

        self._button_container = ttk.Frame(wrapper)
        self._button_container.pack(expand=True, fill="both")

        button_defs = (
            ("Hi-Lo", self._start_hilo),
            ("Wong Halves", self._start_wong),
            ("Back", self._go_back),
        )
        self._buttons = []
        for text, command in button_defs:
            button = ttk.Button(self._button_container, text=text, command=command, width=14)
            self._buttons.append(button)

        self._buttons_horizontal = False
        self._apply_button_layout(horizontal=False)
        self.bind("<Configure>", self._on_resize, add="+")

    def _start_hilo(self) -> None:
        self.controller.start_mode("HiLoFrame")

    def _start_wong(self) -> None:
        self.controller.start_mode("WongHalvesFrame")

    def _go_back(self) -> None:
        self.controller.show_frame("StartMenu")

    def _on_resize(self, event) -> None:
        if event.widget is not self:
            return
        # Flip to a horizontal layout when vertical space is tight.
        should_horizontal = event.height < 260 and event.width >= 320
        if should_horizontal != self._buttons_horizontal:
            self._buttons_horizontal = should_horizontal
            self._apply_button_layout(horizontal=should_horizontal)

    def _apply_button_layout(self, *, horizontal: bool) -> None:
        container = self._button_container

        # Clear previous layout
        for btn in self._buttons:
            btn.grid_forget()

        for index in range(len(self._buttons) + 1):
            container.grid_columnconfigure(index, weight=0)
            container.grid_rowconfigure(index, weight=0)

        if horizontal:
            for index, button in enumerate(self._buttons):
                button.grid(row=0, column=index, padx=6, pady=6, sticky="ew")
                container.grid_columnconfigure(index, weight=1)
            container.grid_rowconfigure(0, weight=1)
        else:
            for index, button in enumerate(self._buttons):
                button.grid(row=index, column=0, padx=6, pady=6)
                container.grid_rowconfigure(index, weight=1)
            container.grid_columnconfigure(0, weight=1)


