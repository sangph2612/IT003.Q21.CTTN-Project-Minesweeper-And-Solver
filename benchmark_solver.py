from __future__ import annotations

import argparse
import csv
import json
import random
import statistics
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any

from core.config import COLS, MINE_COUNT, ROWS
from core.game_logic import GameState
from core.solver_bridge import SolverBridge


DEFAULT_PRESETS: dict[str, dict[str, int]] = {
    "beginner": {"rows": 9, "cols": 9, "mines": 10},
    "intermediate": {"rows": 14, "cols": 18, "mines": 40},
    "expert": {"rows": 16, "cols": 30, "mines": 99},
    "project": {"rows": ROWS, "cols": COLS, "mines": MINE_COUNT},
}

DIFFICULTY_PRESETS: dict[str, list[dict[str, Any]]] = {
    "classic": [
        {"label": "easy", "preset": "beginner"},
        {"label": "medium", "rows": 12, "cols": 16, "mines": 25},
        {"label": "hard", "rows": 14, "cols": 18, "mines": 35},
    ],
    "project": [
        {"label": "easy", "rows": 9, "cols": 12, "mines": 10},
        {"label": "medium", "rows": 12, "cols": 16, "mines": 24},
        {"label": "hard", "rows": 14, "cols": 18, "mines": 35},
    ],
}


@dataclass
class RunResult:
    run_id: int
    difficulty_label: str
    rows: int
    cols: int
    mines: int
    mine_density: float
    seed: int
    status: str
    steps: int
    reveal_moves: int
    flag_moves: int
    duration_ms: float
    revealed_cells: int
    flags_used: int
    first_click_row: int | None
    first_click_col: int | None
    failure_reason: str | None


class SolverBenchmark:
    def __init__(
        self,
        runs: int,
        seed: int,
        max_steps: int,
        output_dir: Path,
        first_click_mode: str,
        first_click_row: int | None,
        first_click_col: int | None,
        scenarios: list[dict[str, Any]],
    ) -> None:
        self.runs = runs
        self.seed = seed
        self.max_steps = max_steps
        self.output_dir = output_dir
        self.first_click_mode = first_click_mode
        self.fixed_first_click_row = first_click_row
        self.fixed_first_click_col = first_click_col
        self.scenarios = scenarios
        self.solver = SolverBridge(project_root=Path(__file__).resolve().parent)

    def run(self) -> dict[str, Any]:
        if not self.solver.is_available():
            raise FileNotFoundError(f"Solver executable not found: {self.solver.solver_path}")

        self.output_dir.mkdir(parents=True, exist_ok=True)
        random.seed(self.seed)

        results: list[RunResult] = []
        for scenario_index, scenario in enumerate(self.scenarios, start=1):
            scenario_seed = self.seed + scenario_index * 1000003
            rng = random.Random(scenario_seed)
            seeds = [rng.randint(0, 2**31 - 1) for _ in range(self.runs)]
            for run_id, run_seed in enumerate(seeds, start=1):
                results.append(self._run_single(run_id, run_seed, scenario))

        summary = self._build_summary(results)
        self._write_outputs(summary, results)
        return summary

    def _run_single(self, run_id: int, run_seed: int, scenario: dict[str, Any]) -> RunResult:
        rows = scenario["rows"]
        cols = scenario["cols"]
        mines = scenario["mines"]
        difficulty_label = scenario["label"]
        mine_density = round(mines / (rows * cols), 4)

        random.seed(run_seed)
        game = GameState(rows, cols, mines)
        first_click_row, first_click_col = self._resolve_first_click(run_seed, rows, cols)

        if first_click_row is not None and first_click_col is not None:
            game.reveal_cell(first_click_row, first_click_col)

        started = time.perf_counter()
        reveal_moves = 1 if first_click_row is not None else 0
        flag_moves = 0
        failure_reason = None
        status = "running"

        while not game.game_over and not game.victory:
            if game.move_count >= self.max_steps:
                status = "max_steps"
                failure_reason = "Reached max step limit"
                break

            solver_status, move = self.solver.get_next_move(game)

            if solver_status == "MOVE" and move is not None:
                move_type, row, col = move
                before_moves = game.move_count
                before_revealed = game.count_revealed
                before_flags = game.flags_used
                applied_status = self.solver.apply_next_move(game)
                if applied_status != "MOVE":
                    status = "error"
                    failure_reason = f"Solver apply failed with status {applied_status}"
                    break
                if game.move_count == before_moves and game.count_revealed == before_revealed and game.flags_used == before_flags:
                    status = "stalled"
                    failure_reason = "Solver repeated a no-op move"
                    break
                if move_type == "SAFE":
                    reveal_moves += 1
                elif move_type == "MINE":
                    flag_moves += 1
                continue

            if solver_status == "NONE":
                status = "none"
                failure_reason = "Solver returned NONE"
                break

            if solver_status == "UNAVAILABLE":
                status = "unavailable"
                failure_reason = "Solver executable unavailable during run"
                break

            status = "error"
            failure_reason = f"Solver returned status {solver_status}"
            break

        ended = time.perf_counter()

        if game.victory:
            status = "victory"
            failure_reason = None
        elif game.game_over:
            status = "hit_mine"
            if failure_reason is None:
                failure_reason = "Solver revealed a mine"

        return RunResult(
            run_id=run_id,
            difficulty_label=difficulty_label,
            rows=rows,
            cols=cols,
            mines=mines,
            mine_density=mine_density,
            seed=run_seed,
            status=status,
            steps=game.move_count,
            reveal_moves=reveal_moves,
            flag_moves=flag_moves,
            duration_ms=round((ended - started) * 1000, 3),
            revealed_cells=game.count_revealed,
            flags_used=game.flags_used,
            first_click_row=first_click_row,
            first_click_col=first_click_col,
            failure_reason=failure_reason,
        )

    def _resolve_first_click(self, run_seed: int, rows: int, cols: int) -> tuple[int | None, int | None]:
        if self.first_click_mode == "none":
            return None, None
        if self.first_click_mode == "fixed":
            if self.fixed_first_click_row is None or self.fixed_first_click_col is None:
                raise ValueError("Fixed first click requires both --first-click-row and --first-click-col")
            if not (0 <= self.fixed_first_click_row < rows and 0 <= self.fixed_first_click_col < cols):
                raise ValueError("Fixed first click is outside the board")
            return self.fixed_first_click_row, self.fixed_first_click_col

        rng = random.Random(run_seed)
        return rng.randrange(rows), rng.randrange(cols)

    def _build_summary(self, results: list[RunResult]) -> dict[str, Any]:
        overall = self._summarize_group(results)
        by_difficulty: dict[str, Any] = {}
        for label in self._ordered_difficulty_labels(results):
            group = [result for result in results if result.difficulty_label == label]
            by_difficulty[label] = self._summarize_group(group)

        return {
            "config": {
                "runs_per_difficulty": self.runs,
                "seed": self.seed,
                "max_steps": self.max_steps,
                "first_click_mode": self.first_click_mode,
                "first_click_row": self.fixed_first_click_row,
                "first_click_col": self.fixed_first_click_col,
                "solver_path": str(self.solver.solver_path),
                "scenarios": self.scenarios,
            },
            "summary": overall,
            "by_difficulty": by_difficulty,
            "results": [asdict(result) for result in results],
        }

    def _ordered_difficulty_labels(self, results: list[RunResult]) -> list[str]:
        ordered: list[str] = []
        for result in results:
            if result.difficulty_label not in ordered:
                ordered.append(result.difficulty_label)
        return ordered

    def _summarize_group(self, results: list[RunResult]) -> dict[str, Any]:
        total = len(results)
        wins = [result for result in results if result.status == "victory"]
        losses = [result for result in results if result.status != "victory"]
        durations = [result.duration_ms for result in results]
        steps = [result.steps for result in results]

        status_breakdown: dict[str, int] = {}
        for result in results:
            status_breakdown[result.status] = status_breakdown.get(result.status, 0) + 1

        board_configs = []
        for result in results:
            config = {
                "rows": result.rows,
                "cols": result.cols,
                "mines": result.mines,
                "mine_density": result.mine_density,
            }
            if config not in board_configs:
                board_configs.append(config)

        return {
            "runs": total,
            "pass_rate": round(len(wins) / total, 4) if total else 0.0,
            "wins": len(wins),
            "losses": len(losses),
            "status_breakdown": status_breakdown,
            "avg_duration_ms": round(statistics.fmean(durations), 3) if durations else 0.0,
            "median_duration_ms": round(statistics.median(durations), 3) if durations else 0.0,
            "avg_steps": round(statistics.fmean(steps), 3) if steps else 0.0,
            "median_steps": round(statistics.median(steps), 3) if steps else 0.0,
            "board_configs": board_configs,
        }

    def _write_outputs(self, summary: dict[str, Any], results: list[RunResult]) -> None:
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        summary_path = self.output_dir / f"benchmark-summary-{timestamp}.json"
        csv_path = self.output_dir / f"benchmark-runs-{timestamp}.csv"

        summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

        with csv_path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(asdict(results[0]).keys()))
            writer.writeheader()
            for result in results:
                writer.writerow(asdict(result))

        print(f"Summary written to {summary_path}")
        print(f"Run details written to {csv_path}")
        print(json.dumps(summary["summary"], indent=2))
        print(json.dumps(summary["by_difficulty"], indent=2))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Benchmark the Minesweeper solver pass rate.")
    parser.add_argument("--preset", choices=sorted(DEFAULT_PRESETS.keys()), default="project")
    parser.add_argument("--difficulty-preset", choices=sorted(DIFFICULTY_PRESETS.keys()))
    parser.add_argument("--rows", type=int, help="Override row count")
    parser.add_argument("--cols", type=int, help="Override column count")
    parser.add_argument("--mines", type=int, help="Override mine count")
    parser.add_argument("--difficulty-label", default="custom", help="Label used in the report for single-board runs")
    parser.add_argument("--runs", type=int, default=100, help="Number of benchmark games per difficulty")
    parser.add_argument("--seed", type=int, default=42, help="Seed used to generate per-run seeds")
    parser.add_argument("--max-steps", type=int, default=5000, help="Safety cap for game moves")
    parser.add_argument("--output-dir", type=Path, default=Path("benchmark_results"))
    parser.add_argument(
        "--first-click-mode",
        choices=("random", "fixed", "none"),
        default="random",
        help="How to initialize the board before the solver loop",
    )
    parser.add_argument("--first-click-row", type=int)
    parser.add_argument("--first-click-col", type=int)
    return parser.parse_args()


def resolve_board_config(preset_name: str, rows: int | None, cols: int | None, mines: int | None) -> tuple[int, int, int]:
    preset = DEFAULT_PRESETS[preset_name]
    resolved_rows = rows or preset["rows"]
    resolved_cols = cols or preset["cols"]
    resolved_mines = mines or preset["mines"]
    return resolved_rows, resolved_cols, resolved_mines


def build_scenarios(args: argparse.Namespace) -> list[dict[str, Any]]:
    if args.difficulty_preset:
        scenarios: list[dict[str, Any]] = []
        for scenario in DIFFICULTY_PRESETS[args.difficulty_preset]:
            if "preset" in scenario:
                rows, cols, mines = resolve_board_config(scenario["preset"], None, None, None)
            else:
                rows, cols, mines = scenario["rows"], scenario["cols"], scenario["mines"]
            scenarios.append(
                {
                    "label": scenario["label"],
                    "rows": rows,
                    "cols": cols,
                    "mines": mines,
                }
            )
        return scenarios

    rows, cols, mines = resolve_board_config(args.preset, args.rows, args.cols, args.mines)
    return [
        {
            "label": args.difficulty_label,
            "rows": rows,
            "cols": cols,
            "mines": mines,
        }
    ]


def main() -> None:
    args = parse_args()
    scenarios = build_scenarios(args)

    benchmark = SolverBenchmark(
        runs=args.runs,
        seed=args.seed,
        max_steps=args.max_steps,
        output_dir=args.output_dir,
        first_click_mode=args.first_click_mode,
        first_click_row=args.first_click_row,
        first_click_col=args.first_click_col,
        scenarios=scenarios,
    )
    benchmark.run()


if __name__ == "__main__":
    main()
