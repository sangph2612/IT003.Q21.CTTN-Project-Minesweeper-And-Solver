"""
author: Pham Thanh Sang
date: 2026-04-22
version: 1.0
last_modify: 2026-04-22
"""

from core.board import Board
import random


class GameState:
    """Hold the current Minesweeper match state and core gameplay rules."""

    def __init__(self, rows, cols, num_mines):
        """Initialize a new game state with board size and mine count."""
        self.rows = rows
        self.cols = cols
        self.num_mines = num_mines
        self.board = Board(rows=rows, cols=cols)
        self.game_over = False
        self.victory = False
        self.first_click_done = False
        self.flags_used = 0
        self.count_revealed = 0
        self.move_count = 0

    def reset_game(self):
        """Reset all game data so a fresh match can begin."""
        self.board = Board(rows=self.rows, cols=self.cols)
        self.game_over = False
        self.victory = False
        self.first_click_done = False
        self.flags_used = 0
        self.count_revealed = 0
        self.move_count = 0

    def place_mines(self, safe_row, safe_col):
        """
        Place mines randomly while keeping the first clicked cell safe.

        Args:
            safe_row (int): Row index of the guaranteed safe starting cell.
            safe_col (int): Column index of the guaranteed safe starting cell.

        Returns:
            None
        """
        neighbors = self.board.get_neighbors(safe_row, safe_col)
        neighbors.append((safe_row, safe_col))
        cells = [
            (i, j)
            for i in range(self.rows)
            for j in range(self.cols)
            if not (i, j) in neighbors
        ]
        mine_positions = random.sample(cells, self.num_mines)

        for row, col in mine_positions:
            self.board.get_cell(row, col).is_mine = True

    def calculate_neighbor_mines(self):
        """
        Compute the number of adjacent mines for every non-mine cell.

        Returns:
            None
        """
        for row in range(self.rows):
            for col in range(self.cols):
                cell = self.board.get_cell(row, col)

                if cell.is_mine:
                    continue

                count = 0
                neighbors = self.board.get_neighbors(row, col)

                for neighbor_row, neighbor_col in neighbors:
                    neighbor_cell = self.board.get_cell(neighbor_row, neighbor_col)
                    if neighbor_cell.is_mine:
                        count += 1

                cell.neighbor_mines = count
    
    def reveal_cell(self, row, col):
        """
        Reveal a cell and apply the main Minesweeper gameplay rules.

        Args:
            row (int): Row index of the cell to reveal.
            col (int): Column index of the cell to reveal.

        Returns:
            None
        """

        cell = self.board.get_cell(row, col)

        if self.game_over or self.victory or cell.is_flagged or cell.is_revealed:
            return
        
        if not self.first_click_done:
            self.place_mines(row, col)
            self.calculate_neighbor_mines()
            self.first_click_done = True

        self.move_count += 1

        if cell.is_mine:
            cell.is_revealed = True
            self.game_over = True
            self.reveal_all_mines()
            return

        self.count_revealed += 1
        cell.is_revealed = True

        if cell.neighbor_mines == 0:
            self.flood_fill(row, col)

        if self.check_win():
            self.victory = True

    def caculate_neighbor_flagged(self, row, col):
        """
        Count the number of flagged neighboring cells around a revealed cell.

        Args:
            row (int): Row index of the center cell.
            col (int): Column index of the center cell.

        Returns:
            int: Number of adjacent flagged cells.
        """
        count = 0
        neighbors = self.board.get_neighbors(row, col)
        for neighbor_row, neighbor_col in neighbors:
            neighbor_cell = self.board.get_cell(neighbor_row, neighbor_col)
            if neighbor_cell.is_flagged:
                count += 1
        
        return count

    def toggle_flag(self, row, col):
        """
        Add or remove a flag on a hidden cell.

        Args:
            row (int): Row index of the target cell.
            col (int): Column index of the target cell.

        Returns:
            None
        """

        if self.game_over or self.victory:
            return
        cell = self.board.get_cell(row, col)
        if cell.is_revealed:
            if self.caculate_neighbor_flagged(row, col) == cell.neighbor_mines:
                neighbors = self.board.get_neighbors(row, col)
                for neighbor_row, neighbor_col in neighbors:
                    neighbor_cell = self.board.get_cell(neighbor_row, neighbor_col)
                    if not neighbor_cell.is_revealed:
                        self.reveal_cell(neighbor_row, neighbor_col)
            
            return
        self.move_count += 1
        if cell.is_flagged:
            cell.is_flagged = False
            self.flags_used -= 1
        else:
            cell.is_flagged = True
            self.flags_used += 1

    def flood_fill(self, row, col):
        """
        Recursively reveal neighboring empty areas starting from a zero-value cell.

        Args:
            row (int): Row index of the starting cell.
            col (int): Column index of the starting cell.

        Returns:
            None
        """
        neighbors = self.board.get_neighbors(row, col)
        for neighbor_row, neighbor_col in neighbors:
            cell = self.board.get_cell(neighbor_row, neighbor_col)
            if not cell.is_revealed and not cell.is_flagged:
                self.reveal_cell(neighbor_row, neighbor_col)

    def reveal_all_mines(self):
        """Reveal every mine after the player hits one."""
        for row in range(self.rows):
            for col in range(self.cols):
                cell = self.board.get_cell(row, col)
                if cell.is_mine:
                    cell.is_revealed = True

    def check_win(self):
        """
        Check whether all non-mine cells have been revealed.

        Returns:
            bool: True if the player has won, otherwise False.
        """
        return self.rows * self.cols - self.count_revealed == self.num_mines

    def get_remaining_mines(self):
        """
        Return the remaining mine counter based on placed flags.

        Returns:
            int: Estimated number of mines that are still unflagged.
        """
        return self.num_mines - self.flags_used
