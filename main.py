"""Entrypoint for the blackjack counter application."""

from blackjack_counter.app import CountingApp


def main() -> None:
    app = CountingApp()
    app.mainloop()


if __name__ == "__main__":
    main()
