from __future__ import annotations

import subprocess
from pathlib import Path
from core.config import SOLVER_NAME


class SolverBridge:
    """Provide an integration point between the game and the external solver."""

    def __init__(self, project_root=None):
        """Initialize solver bridge state."""
        if project_root is None:
            project_root = Path(__file__).resolve().parent.parent
        self.project_root = Path(project_root)
        self.solver_path = self.project_root / SOLVER_NAME

    def is_available(self):
        """Return True if the compiled solver executable is available."""
        return self.solver_path.exists()

    def build_input(self, game_state):
        """Convert the current game state into the solver board encoding."""
        lines = [f"{game_state.rows} {game_state.cols}"]

        for row in range(game_state.rows):
            values = []
            for col in range(game_state.cols):
                cell = game_state.board.get_cell(row, col)
                if cell.is_flagged:
                    values.append("-2")
                elif not cell.is_revealed:
                    values.append("-1")
                else:
                    values.append(str(cell.neighbor_mines))
            lines.append(" ".join(values))

        return "\n".join(lines) + "\n"

    def get_next_move(self, game_state):
        """Run the external solver and parse its next suggested move."""
        if not self.is_available():
            return "UNAVAILABLE", None

        process = subprocess.run(
            [str(self.solver_path)],
            input=self.build_input(game_state),
            text=True,
            capture_output=True,
            cwd=self.project_root,
            check=False,
        )

        if process.returncode != 0:
            return "ERROR", None

        output = process.stdout.strip()
        if not output:
            return "NONE", None

        parts = output.split()
        if parts[0] == "NONE":
            return "NONE", None
        if len(parts) != 3:
            return "ERROR", None

        move_type, row_text, col_text = parts
        try:
            row = int(row_text)
            col = int(col_text)
        except ValueError:
            return "ERROR", None

        if move_type not in {"SAFE", "MINE"}:
            return "ERROR", None

        return "MOVE", (move_type, row, col)

    def apply_next_move(self, game_state):
        """Ask the solver for one move and apply it to the current game state."""
        status, move = self.get_next_move(game_state)
        if status != "MOVE":
            return status

        move_type, row, col = move
        if not game_state.board.is_inside(row, col):
            return "ERROR"

        if move_type == "SAFE":
            self._apply_safe_move(game_state, row, col)
            return "MOVE"

        if move_type == "MINE":
            cell = game_state.board.get_cell(row, col)
            if not cell.is_flagged:
                game_state.toggle_flag(row, col)
            return "MOVE"

        return "ERROR"

    def _apply_safe_move(self, game_state, row, col):
        """Apply a safe solver move, including the first-click bootstrap case."""
        if game_state.first_click_done:
            game_state.reveal_cell(row, col)
            return

        game_state.place_mines(row, col)
        game_state.calculate_neighbor_mines()
        game_state.first_click_done = True
        game_state.reveal_cell(row, col)
