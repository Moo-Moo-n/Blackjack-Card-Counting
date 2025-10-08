# Blackjack Card Counting Helper

A lightweight desktop helper that lets you practice and run two common blackjack counting systems: **Hi-Lo** and **Wong Halves**. The interface stays true to the layouts you described and keeps the running / historical counts presented horizontally for quick scanning while you play.

## Project structure
- main.py keeps the entry point tiny and easy to read.
- \blackjack_counter/app.py wires up the window, navigation, and shared styling.
- \blackjack_counter/state.py and \blackjack_counter/formatting.py hold the core logic.
- \blackjack_counter/frames/ contains the reusable base frame plus one module per screen.

## Features
- Start menu with quick access to each counting mode.
- Hi-Lo layout with dedicated _Low_, _High_, _Undo_, and _Reset Shoe_ controls.
- Wong Halves layout adds 2-A card buttons alongside the shared controls.
- Running and true counts update live, including a history feed of the increments you entered.
- Unlimited undo plus shoe resets to restart a practice session instantly.
- Resizable window with responsive panes so the counter can sit beside another app while you play.

## Running the app
1. Ensure you have Python 3.9+ installed on Windows (https://www.python.org/downloads/).
2. Run .exe in dist folder (exe made possible using PyInstaller)


If you need to tweak the packaging further, edit main.spec to match your preferences.

## Notes & tips
- The counter assumes a six-deck shoe. You can change the deck estimate in code by passing a different value to start_mode if you prefer another baseline.
- The true count will never divide by fewer than a quarter-deck to avoid extreme spikes once the shoe runs out.
- Undo removes the most recent entry (card or low/high press) so the history and counts always stay in sync.

## Credits
- Icon by Freepik: <a href="https://www.flaticon.com/free-icons/gambling" title="gambling icons">Gambling icons created by Freepik - Flaticon</a>.

Happy practicing!

