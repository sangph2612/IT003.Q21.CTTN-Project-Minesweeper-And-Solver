from __future__ import annotations

import subprocess
from pathlib import Path


class SolverBridge:
    """Provide an integration point between the game and the external solver."""

    def __init__(self, project_root=None):
        """Initialize solver bridge state."""
        if project_root is None:
            project_root = Path(__file__).resolve().parent.parent
        self.project_root = Path(project_root)
        self.solver_path = self.project_root / "solver.exe"

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
            return None

        process = subprocess.run(
            [str(self.solver_path)],
            input=self.build_input(game_state),
            text=True,
            capture_output=True,
            cwd=self.project_root,
            check=False,
        )

        if process.returncode != 0:
            return None

        output = process.stdout.strip()
        if not output:
            return None

        parts = output.split()
        if parts[0] == "NONE":
            return None
        if len(parts) != 3:
            return None

        move_type, row_text, col_text = parts
        try:
            row = int(row_text)
            col = int(col_text)
        except ValueError:
            return None

        if move_type not in {"SAFE", "MINE"}:
            return None

        return move_type, row, col

    def apply_next_move(self, game_state):
        """Ask the solver for one move and apply it to the current game state."""
        move = self.get_next_move(game_state)
        if move is None:
            return False

        move_type, row, col = move
        if not game_state.board.is_inside(row, col):
            return False

        if move_type == "SAFE":
            game_state.reveal_cell(row, col)
            return True

        if move_type == "MINE":
            cell = game_state.board.get_cell(row, col)
            if not cell.is_flagged:
                game_state.toggle_flag(row, col)
            return True

        return False
