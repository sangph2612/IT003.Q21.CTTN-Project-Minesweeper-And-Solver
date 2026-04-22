# IT003.Q21.CTTN Project, Minesweeper with Auto Solver

A course project for Application Development that implements a playable **Minesweeper** game using **Python + Pygame**, together with a working **C++ auto solver** that can analyze the current board and choose the next move.

## Project Overview

This project has two main parts:

- **Game client in Python + Pygame**
  - Handles the window, board rendering, input, timer, restart flow, and gameplay rules.
- **Solver in C++**
  - Reads the current visible board state from the game.
  - Performs deterministic inference and CSP-based search.
  - Returns one next move for the game to apply automatically.

The goal of the project is not only to recreate the Minesweeper game, but also to apply data structures and algorithms to a practical problem involving logical reasoning, search, and probability-based decision making.

## Main Features

- Playable Minesweeper game with graphical interface
- Left click to reveal cells
- Right click to place flags
- Safe first click
- Automatic expansion for empty areas
- Restart button and in-game timer
- Auto solver toggle in the interface
- External solver integration through a Python bridge
- Modular structure for easier maintenance and extension

## Solver Features

The solver is already implemented and supports a multi-stage solving process:

1. **Basic inference**
   - Detects guaranteed safe cells or guaranteed mines from a single constraint.
2. **Subset inference**
   - Generates new constraints when one constraint is a subset of another.
3. **Constraint graph decomposition**
   - Splits the frontier into independent connected components.
4. **DFS traversal for connected components**
   - Finds groups of related frontier variables before solving them.
5. **Backtracking / branch and bound style search**
   - Enumerates valid assignments while pruning impossible partial states.
6. **Probabilistic move selection**
   - When no forced move exists, selects the cell with the lowest estimated mine probability.

### Solver output

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
- `NONE`: no valid move could be produced

## Technologies Used

- **Python 3**
- **Pygame**
- **C++**

## Project Structure

```text
minesweeper/
├── main.py
├── solver.cpp
├── solver.exe
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
│   ├── liem.png
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
Entry point of the application. Creates the app object and starts the main loop.

### `solver.cpp`
Main C++ solver implementation. Reads the current visible board, builds constraints, performs inference, and outputs one next move.

### `solver.exe`
Compiled solver executable used by the Python game.

### `assets/`
Contains image assets for tiles, numbers, flags, mines, and other game visuals.

### `core/`
Contains the main Python modules of the project.

- `app.py`: top-level app setup, game loop, and auto solver control
- `board.py`: board structure and neighbor-related helpers
- `cell.py`: representation of a single cell
- `config.py`: constants such as rows, columns, mine count, and window size
- `game_logic.py`: reveal logic, mine placement, flood fill, flags, and win/loss conditions
- `input_handler.py`: mouse and keyboard event handling
- `renderer.py`: drawing the board, buttons, timer, and status
- `solver_bridge.py`: bridge between Python and the external C++ solver
- `ui.py`: additional UI support module

## How to Run

### Requirements

- Python 3.x
- Pygame
- A C++ compiler if you want to rebuild the solver

### Install dependency

```bash
pip install pygame
```

### Run the game

```bash
python main.py
```

## How the Solver Connects to the Game

The Python game converts the visible board into the solver input format:

- `-1`: hidden cell
- `-2`: flagged cell
- `0..8`: revealed cell with the corresponding number of adjacent mines

The board is passed to `solver.exe` through standard input. The solver then returns one action, and the Python side applies that move to the current game state.

## Algorithms and Data Structures Used in the Solver

### Data structures
- **2D array / matrix** to store the visible game board
- **Vector / list** to store frontier cells and constraints
- **Map** to assign IDs to frontier cells
- **Graph adjacency list** to represent relations between frontier variables
- **Component structure** to split the problem into smaller independent parts

### Algorithms
- **Subset checking** to determine whether one constraint is contained in another
- **Set difference** to derive new reduced constraints
- **Basic logical inference** to identify forced safe cells or mines
- **DFS** to traverse connected components in the constraint graph
- **Backtracking with pruning** to enumerate valid assignments efficiently
- **Heuristic probability selection** to choose the most promising move when no forced move exists

## Notes

- The game and solver are separated clearly, making the project easier to test and maintain.
- The solver works step by step, producing one move at a time.
- The current implementation combines deterministic reasoning and probabilistic guessing for better performance on difficult board states.

## Acknowledgements

- **Lê Phú Trọng** for helping draw the game assets.

## Author

- **Phạm Thanh Sang**
- **Student ID:** 25521582
- **Class:** IT003.Q21.CTTN
