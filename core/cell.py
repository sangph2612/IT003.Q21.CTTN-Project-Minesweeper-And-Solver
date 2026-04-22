"""
author: Pham Thanh Sang
date: 2026-04-22
version: 1.0
last_modify: 2026-04-22
"""


"""
author: Pham Thanh Sang
date: 2026-04-22
version: 1.0
last_modify: 2026-04-22
"""

class Cell:
    """Represent a single cell on the Minesweeper board."""

    def __init__(self):
        """Initialize the default state for a hidden non-mine cell."""
        self.is_mine = False
        self.is_revealed = False
        self.is_flagged = False
        self.neighbor_mines = 0
