# IT003.Q21.CTTN Project, Minesweeper with Auto Solver

A course project for Application Development that implements a playable **Minesweeper** game using **Python** and **Pygame**, together with a **C++ solver** designed to suggest or perform the next move automatically.

## Project Overview

This project has two main parts:

- **Game client in Python + Pygame**
  - Handles the game window, board rendering, mouse and keyboard input, timer, restart button, and gameplay flow.
- **Solver in C++**
  - Receives the current visible board state and returns exactly one next action:
    - `SAFE row col` for a cell that can be opened safely
    - `MINE row col` for a cell that should be flagged
    - `NONE` if no deterministic move can be inferred

The goal of the project is not only to recreate the Minesweeper game, but also to apply data structures and algorithms to a practical problem involving logical inference.

## Technologies Used

- **Python**
- **Pygame**
- **C++**

## Project Structure

```text
minesweeper/
├── main.py
├── solver.cpp
├── README.md
├── TODO.md
├── assets/
│   ├── 0.png
│   ├── 1.png
│   ├── 2.png
│   ├── 3.png
│   ├── 4.png
│   ├── 5.png
│   ├── 6.png
│   ├── 7.png
│   ├── 8.png
│   ├── cut.png
│   ├── flag.png
│   └── tile.png
└── core/
    ├── __init__.py
    ├── app.py
    ├── board.py
    ├── cell.py
    ├── config.py
    ├── game_logic.py
    ├── input_handler.py
    ├── renderer.py
    ├── solver_bridge.py
    └── ui.py
```

## Folder and File Description

### `main.py`
Entry point of the application. This file creates the app object and starts the main game loop.

### `solver.cpp`
C++ solver module. It is intended to read the current board state and return one next action for the game.

### `assets/`
Contains image assets used by the game interface, including closed tiles, flags, mines, and revealed numbered cells.

### `core/`
Contains the main Python modules of the project.

- `app.py`: top-level application setup and main loop
- `board.py`: board structure and neighbor-related helpers
- `cell.py`: representation of a single Minesweeper cell
- `config.py`: game configuration constants such as rows, columns, cell size, and mine count
- `game_logic.py`: main gameplay logic such as mine placement, reveal, flagging, flood fill, and win/loss checks
- `input_handler.py`: keyboard and mouse event handling
- `renderer.py`: drawing the board, status bar, timer, and buttons
- `solver_bridge.py`: planned bridge between Python and the C++ solver
- `ui.py`: placeholder for additional UI-related logic

## How to Run

### Requirements

- Python 3.x
- Pygame
- A C++ compiler if you want to build the solver later

### Run the game

```bash
python main.py
```

## Solver Input and Output Format

### Input
The solver receives the current visible board state.

- First line:

```text
rows cols
```

- Next `rows` lines: each line contains `cols` integers

Cell encoding:

- `-1`: hidden cell
- `-2`: flagged cell
- `0..8`: revealed cell with the corresponding number of neighboring mines

Example:

```text
5 5
1 1 1 -1 -1
1 -2 2 -1 -1
1 2 3 2 1
0 1 -1 -1 1
0 1 2 2 1
```

### Output
The solver returns exactly one action:

```text
SAFE row col
```

or

```text
MINE row col
```

or

```text
NONE
```

Meaning:

- `SAFE row col`: the cell can be safely revealed
- `MINE row col`: the cell should be flagged as a mine
- `NONE`: no certain move can be inferred

## Main Features

- Playable Minesweeper game with graphical interface
- Left click to reveal cells
- Right click to place flags
- Automatic empty-area expansion using flood fill
- Restart button and in-game timer
- Modular project structure for easier maintenance and future expansion
- Planned integration with a C++ auto solver

## Notes

- The Python game is already structured into modules to separate rendering, input handling, board management, and game logic.
- The solver interface has been documented, even if the solving logic is still being developed.

## Author

- **Pham Thanh Sang**
- **Student ID:** 25521582
- **Class:** IT003.Q21.CTTN
