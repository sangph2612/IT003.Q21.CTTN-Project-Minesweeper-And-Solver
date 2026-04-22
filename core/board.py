"""
author: Pham Thanh Sang
date: 2026-04-22
version: 1.0
last_modify: 2026-04-22
"""

from core.cell import Cell


class Board:
    """Store the Minesweeper grid and provide board-level helpers."""

    def __init__(self, rows, cols):
        """Create an empty board with the given dimensions."""
        self.rows = rows
        self.cols = cols
        self.board = [[Cell() for _ in range(cols)] for _ in range(rows)]
        self.dx = [-1, -1, -1, 0, 0, 1, 1, 1]
        self.dy = [-1, 0, 1, -1, 1, -1, 0, 1]

    def is_inside(self, row, col):
        """Return True if the given coordinates are inside the board."""
        return 0 <= row < self.rows and 0 <= col < self.cols

    def get_cell(self, row, col):
        """Return the cell object located at the given coordinates."""
        return self.board[row][col]

    def get_neighbors(self, row, col):
        """
        Return a list of valid neighboring cell coordinates.

        Args:
            row (int): Row index of the center cell.
            col (int): Column index of the center cell.

        Returns:
            list[tuple[int, int]]: Valid neighboring coordinates around the cell.
        """
        neighbors = []

        for i in range(8):
            nxt_row = row + self.dx[i]
            nxt_col = col + self.dy[i]

            if self.is_inside(nxt_row, nxt_col):
                neighbors.append((nxt_row, nxt_col))

        return neighbors
