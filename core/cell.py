class Cell:
    """Represent a single cell on the Minesweeper board."""

    def __init__(self):
        """Initialize the default state for a hidden non-mine cell."""
        self.is_mine = False
        self.is_revealed = False
        self.is_flagged = False
        self.neighbor_mines = 0
