"""
author: Pham Thanh Sang
date: 2026-04-22
version: 1.0
last_modify: 2026-04-22
"""

from core.app import App


def main():
    """
    Create the application instance and start the main game loop.

    Returns:
        None
    """
    app = App()
    app.run()


if __name__ == "__main__":
    main()
