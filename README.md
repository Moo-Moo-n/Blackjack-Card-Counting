# Blackjack Card Counting Helper

A lightweight desktop helper that lets you practice and run two common blackjack counting systems: **Hi-Lo** and **Wong Halves**. The interface stays true to the layouts you described and keeps the running / historical counts presented horizontally for quick scanning while you play.

## Features
- Start menu with quick access to each counting mode.
- Hi-Lo layout with dedicated _Low_, _High_, _Undo_, and _Reset Shoe_ controls.
- Wong Halves layout adds 2-A card buttons alongside the shared controls.
- Running and true counts update live, including a history feed of the increments you entered.
- Unlimited undo plus shoe resets to restart a practice session instantly.
- Resizable window with responsive panes so the counter can sit beside another app while you play.

## Running the app
1. Ensure you have Python 3.9+ installed on Windows (https://www.python.org/downloads/).
2. From this project folder run:
   `powershell
   python main.py
   `
   The counter opens in a new window.

## Building a standalone .exe
The app has no external dependencies beyond the standard library, so you can bundle it with [PyInstaller](https://pyinstaller.org/en/stable/).

1. Install PyInstaller (one time):
   `powershell
   pip install pyinstaller
   `
2. Build a single-file, windowed executable:
   `powershell
   pyinstaller --onefile --windowed main.py
   `
3. Your distributable executable will be under dist\main.exe. Share that file with friends; they won't need Python installed.

If you want to customize the executable name or icon, PyInstaller flags such as --name and --icon work as usual.

## Notes & tips
- The counter assumes a six-deck shoe. You can change the deck estimate in code by passing a different value to start_mode if you prefer another baseline.
- The true count will never divide by fewer than a quarter-deck to avoid extreme spikes once the shoe runs out.
- Undo removes the most recent entry (card or low/high press) so the history and counts always stay in sync.

Happy practicing!

