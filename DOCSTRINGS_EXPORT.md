# Docstrings and Comments Export

## core/__init__.py

_No docstrings found._

## core/app.py

### Class: `App`

```text
Manage application setup, the main loop, and top-level game flow.
```

### Method: `App.__init__`

```text
Initialize pygame, create the window, and prepare game components.
```

### Method: `App.reset_timer`

```text
Reset the in-game timer for a new match.
```

### Method: `App.run`

```text

        Run the main application loop until the window is closed.

        Returns:
            None
```

### Method: `App.handle_events`

```text

        Process pygame events, player input, and match-ending timer freeze.

        Returns:
            None
```

### Method: `App.update`

```text
Update game state between frames and drive auto solver when enabled.
```

### Method: `App.draw`

```text

        Render the current game scene, UI panels, and timer information.

        Returns:
            None
```

## core/board.py

### Class: `Board`

```text
Store the Minesweeper grid and provide board-level helpers.
```

### Method: `Board.__init__`

```text
Create an empty board with the given dimensions.
```

### Method: `Board.is_inside`

```text
Return True if the given coordinates are inside the board.
```

### Method: `Board.get_cell`

```text
Return the cell object located at the given coordinates.
```

### Method: `Board.get_neighbors`

```text

        Return a list of valid neighboring cell coordinates.

        Args:
            row (int): Row index of the center cell.
            col (int): Column index of the center cell.

        Returns:
            list[tuple[int, int]]: Valid neighboring coordinates around the cell.
```

## core/cell.py

### Class: `Cell`

```text
Represent a single cell on the Minesweeper board.
```

### Method: `Cell.__init__`

```text
Initialize the default state for a hidden non-mine cell.
```

## core/config.py

_No docstrings found._

## core/game_logic.py

### Class: `GameState`

```text
Hold the current Minesweeper match state and core gameplay rules.
```

### Method: `GameState.__init__`

```text
Initialize a new game state with board size and mine count.
```

### Method: `GameState.reset_game`

```text
Reset all game data so a fresh match can begin.
```

### Method: `GameState.place_mines`

```text

        Place mines randomly while keeping the first clicked cell safe.

        Args:
            safe_row (int): Row index of the guaranteed safe starting cell.
            safe_col (int): Column index of the guaranteed safe starting cell.

        Returns:
            None
```

### Method: `GameState.calculate_neighbor_mines`

```text

        Compute the number of adjacent mines for every non-mine cell.

        Returns:
            None
```

### Method: `GameState.reveal_cell`

```text

        Reveal a cell and apply the main Minesweeper gameplay rules.

        Args:
            row (int): Row index of the cell to reveal.
            col (int): Column index of the cell to reveal.

        Returns:
            None
```

### Method: `GameState.caculate_neighbor_flagged`

```text
Count number of neighbor which has a flag
```

### Method: `GameState.toggle_flag`

```text

        Add or remove a flag on a hidden cell.

        Args:
            row (int): Row index of the target cell.
            col (int): Column index of the target cell.

        Returns:
            None
```

### Method: `GameState.flood_fill`

```text

        Recursively reveal neighboring empty areas starting from a zero-value cell.

        Args:
            row (int): Row index of the starting cell.
            col (int): Column index of the starting cell.

        Returns:
            None
```

### Method: `GameState.reveal_all_mines`

```text
Reveal every mine after the player hits one.
```

### Method: `GameState.check_win`

```text

        Check whether all non-mine cells have been revealed.

        Returns:
            bool: True if the player has won, otherwise False.
```

### Method: `GameState.get_remaining_mines`

```text

        Return the remaining mine counter based on placed flags.

        Returns:
            int: Estimated number of mines that are still unflagged.
```

## core/input_handler.py

### Class: `InputHandler`

```text
Translate mouse and keyboard input into game actions.
```

### Method: `InputHandler.__init__`

```text
Store rendering context and input-related state.
```

### Method: `InputHandler.mouse_to_grid`

```text

        Convert mouse coordinates on screen into board row and column indices.

        Args:
            mouse_x (int): Horizontal mouse position in pixels.
            mouse_y (int): Vertical mouse position in pixels.

        Returns:
            tuple[int, int]: Row and column indices on the board.
```

### Method: `InputHandler.handle_mouse_down`

```text

        Handle mouse press events for reset, reveal, flag, and auto-solver toggle actions.

        Args:
            event (pygame.event.Event): Mouse button event from pygame.
            game_state (GameState): Current game state to update.
            app (App | None): Application object for toggling auto solver.

        Returns:
            bool: True if the game was reset, otherwise False.
```

### Method: `InputHandler.handle_mouse_up`

```text
Reset button press visuals when the left mouse button is released.
```

### Method: `InputHandler.handle_key`

```text

        Handle keyboard shortcuts such as restarting the current match.

        Args:
            event (pygame.event.Event): Keyboard event from pygame.
            game_state (GameState): Current game state to update.
            app (App | None): Application object for toggling auto solver.

        Returns:
            bool: True if the game was reset, otherwise False.
```

### Method: `InputHandler.handle_event`

```text

        Dispatch a pygame event to the appropriate input handler.

        Args:
            event (pygame.event.Event): Event to process.
            game_state (GameState): Current game state to update.
            app (App | None): Application object for extra controls.

        Returns:
            bool: True if the game was reset, otherwise False.
```

## core/renderer.py

### Class: `Renderer`

```text
Render the Minesweeper board, interface panels, and status indicators.
```

### Method: `Renderer.__init__`

```text
Load drawing resources and precompute layout rectangles.
```

### Method: `Renderer.draw_rounded_panel`

```text
Draw a rounded panel with an optional border and drop shadow.
```

### Method: `Renderer.draw_background`

```text
Draw the window background and the static interface panels.
```

### Method: `Renderer.get_cell_rect`

```text
Return the screen rectangle for a board cell at the given coordinates.
```

### Method: `Renderer.draw_board`

```text

        Draw all visible cells of the current board state.

        Args:
            board (Board): Board object containing the cells to render.
            animation_time (int): Current tick count used for simple animation effects.

        Returns:
            None
```

### Method: `Renderer.draw_cell`

```text

        Draw one cell, including revealed values, mines, flags, and effects.

        Args:
            cell (Cell): Cell object to render.
            row (int): Row index of the cell.
            col (int): Column index of the cell.
            pulse (float): Animation factor used for zero-cell glow effects.

        Returns:
            None
```

### Method: `Renderer.draw_text`

```text
Render a text string to the screen using the chosen font and color.
```

### Method: `Renderer.draw_restart_button`

```text

        Draw the smiley restart button with an expression matching the game state.

        Args:
            game_state (GameState): Current game state used to choose the button face.
            pressed (bool): Whether the button is currently being pressed.

        Returns:
            None
```

### Method: `Renderer.draw_auto_solver_button`

```text
Draw the auto solver toggle button.
```

### Method: `Renderer.draw_time_label`

```text

        Draw the elapsed time label and highlight it when the timer is frozen.

        Args:
            elapsed_seconds (int): Number of elapsed seconds to display.
            frozen (bool): Whether the timer should be shown in a frozen state.

        Returns:
            None
```

### Method: `Renderer.draw_status`

```text

        Draw the footer message and simple animation based on the current result.

        Args:
            game_state (GameState): Current game state used to choose status text.
            animation_time (int): Current tick count used for simple animation effects.
            auto_solver_enabled (bool): Whether auto solver mode is active.
            solver_available (bool): Whether the compiled solver can be called.

        Returns:
            None
```

## core/solver_bridge.py

### Class: `SolverBridge`

```text
Provide an integration point between the game and the external solver.
```

### Method: `SolverBridge.__init__`

```text
Initialize solver bridge state.
```

### Method: `SolverBridge.is_available`

```text
Return True if the compiled solver executable is available.
```

### Method: `SolverBridge.build_input`

```text
Convert the current game state into the solver board encoding.
```

### Method: `SolverBridge.get_next_move`

```text
Run the external solver and parse its next suggested move.
```

### Method: `SolverBridge.apply_next_move`

```text
Ask the solver for one move and apply it to the current game state.
```

### Method: `SolverBridge._apply_safe_move`

```text
Apply a safe solver move, including the first-click bootstrap case.
```

## core/ui.py

### Class: `UI`

```text
Reserve a placeholder class for future standalone UI helpers.
```

### Method: `UI.__init__`

```text
Initialize UI helper state.
```

## main.py

### Function: `main`

```text
Create the application instance and start the main game loop.
```

## solver.cpp

### Symbol: `bool is_inside(int row, int col) {`

```cpp
/**
 * @brief Check whether a cell coordinate is inside the board.
 *
 * @param row Row index to validate.
 * @param col Column index to validate.
 * @return true if the coordinate is valid, otherwise false.
 */
```

### Symbol: `bool is_hidden(int row, int col) {`

```cpp
/**
 * @brief Check whether a cell is still hidden.
 *
 * @param row Row index of the cell.
 * @param col Column index of the cell.
 * @return true if the cell is hidden, otherwise false.
 */
```

### Symbol: `bool is_flagged(int row, int col) {`

```cpp
/**
 * @brief Check whether a cell is currently flagged.
 *
 * @param row Row index of the cell.
 * @param col Column index of the cell.
 * @return true if the cell is flagged, otherwise false.
 */
```

### Symbol: `bool is_revealed_number(int row, int col) {`

```cpp
/**
 * @brief Check whether a cell has already been revealed as a number.
 *
 * @param row Row index of the cell.
 * @param col Column index of the cell.
 * @return true if the cell contains a revealed value from 0 to 8.
 */
```

### Symbol: `vector<CellPos> get_neighbors(int row, int col) {`

```cpp
/**
 * @brief Return all 8 neighboring coordinates around a cell.
 *
 * @param row Row index of the center cell.
 * @param col Column index of the center cell.
 * @return vector<CellPos> Neighbor coordinates in 8 directions.
 */
```

### Symbol: `void read_input() {`

```cpp
/**
 * @brief Read the current visible board state from standard input.
 *
 * This function should load the board dimensions and the encoded cell values.
 */
```

### Symbol: `bool is_frontier_cell(int row, int col) {`

```cpp
/**
 * @brief Determine whether a hidden cell belongs to the frontier.
 *
 * A frontier cell is a hidden cell that touches at least one revealed numbered cell.
 * Frontier cells are the variables used in the constraint system.
 *
 * @param row Row index of the candidate cell.
 * @param col Column index of the candidate cell.
 * @return true if the cell belongs to the frontier, otherwise false.
 */
```

### Symbol: `void collect_frontier_cells() {`

```cpp
/**
 * @brief Collect all frontier cells and map them to variable ids.
 *
 * This function should fill frontier_cells and frontier_id.
 */
```

### Symbol: `void normalize_constraint(Constraint &constraint) {`

```cpp
/**
 * @brief Normalize a constraint by sorting and removing duplicated variables.
 *
 * @param constraint Constraint to normalize.
 */
```

### Symbol: `void build_constraints() {`

```cpp
/**
 * @brief Build linear constraints from the currently revealed numbered cells.
 *
 * Each numbered cell should generate one equation of the form:
 * x1 + x2 + ... + xm = k
 * where xi represents a frontier variable and k is the number of mines still needed.
 */
```

### Symbol: `bool is_subset(const vector<int> &a, const vector<int> &b) {`

```cpp
/**
 * @brief Check whether one sorted variable set is a subset of another.
 *
 * @param a Candidate subset.
 * @param b Candidate superset.
 * @return true if every variable in a also appears in b.
 */
```

### Symbol: `vector<int> set_difference_vec(const vector<int> &a, const vector<int> &b) {`

```cpp
/**
 * @brief Compute the set difference between two sorted variable sets.
 *
 * This helper is mainly used for subset or equation-subtraction inference.
 *
 * @param a Smaller set.
 * @param b Larger set.
 * @return vector<int> Variables that are in b but not in a.
 */
```

### Symbol: `Move apply_basic_inference() {`

```cpp
/**
 * @brief Apply direct deterministic rules on a single constraint.
 *
 * Main ideas:
 * - If mines_needed == 0, all remaining variables are SAFE.
 * - If mines_needed == vars.size(), all remaining variables are MINE.
 *
 * @return Move A forced move if one is found, otherwise {"NONE", -1, -1}.
 */
```

### Symbol: `bool generate_subset_constraints() {`

```cpp
/**
 * @brief Generate new constraints using subset-based equation subtraction.
 *
 * If constraint A is a subset of constraint B, the solver can derive a new
 * constraint on the variables in B \ A:
 *
 * sum(B \ A) = mines(B) - mines(A)
 *
 * Newly derived constraints should be normalized and added to the global
 * constraint list only if they are valid and not already present.
 *
 * @return true if at least one new constraint is generated, otherwise false.
 */
```

### Symbol: `Move deterministic_inference() {`

```cpp
/**
 * @brief Repeatedly run deterministic inference until no more progress is possible.
 *
 * This function should keep applying direct inference rules first. If no forced
 * move is found, it should try to generate new subset-derived constraints and
 * repeat the process until either a move is found or no new information can be added.
 *
 * @return Move A forced move if one is found, otherwise {"NONE", -1, -1}.
 */
```

### Symbol: `void build_variable_graph() {`

```cpp
/**
 * @brief Build an adjacency graph between frontier variables.
 *
 * Two variables should be connected if they appear together in at least one constraint.
 * This graph is used to split the CSP into independent components.
 */
```

### Symbol: `void dfs_component(int start_var, vector<int> &visited_vars, Component &component) {`

```cpp
/**
 * @brief Traverse one connected component of the variable graph.
 *
 * @param start_var Variable id where DFS starts.
 * @param visited_vars Marks variables that have already been visited.
 * @param component Output component being constructed.
 */
```

### Symbol: `void split_into_components() {`

```cpp
/**
 * @brief Split the full constraint system into connected components.
 *
 * Each component contains the frontier variables and constraints that depend on each other.
 */
```

### Symbol: `bool is_partial_assignment_valid(const Component &component, const vector<int> &local_assignment) {`

```cpp
/**
 * @brief Check whether a partial assignment is still consistent with a component.
 *
 * This function is used for pruning during recursive CSP search.
 *
 * @param component Component currently being solved.
 * @param local_assignment Current partial local assignment.
 * @return true if the partial assignment is still valid, otherwise false.
 */
```

### Symbol: `void backtrack_component( const Component &component, int depth, vector<int> &local_assignment, ComponentStats &stats ) {`

```cpp
/**
 * @brief Enumerate all valid assignments for one component using backtracking.
 *
 * @param component Component currently being analyzed.
 * @param depth Current recursion depth.
 * @param local_assignment Current assignment of local variables.
 * @param stats Statistics accumulated from valid solutions.
 */
```

### Symbol: `ComponentStats analyze_component(const Component &component) {`

```cpp
/**
 * @brief Analyze one component and compute solution statistics.
 *
 * @param component Connected component to solve.
 * @return ComponentStats Total valid solutions and mine counts per variable.
 */
```

### Symbol: `Move find_forced_move_from_stats(const Component &component, const ComponentStats &stats) {`

```cpp
/**
 * @brief Find a guaranteed SAFE or MINE move from component statistics.
 *
 * @param component Component being analyzed.
 * @param stats Statistics produced for that component.
 * @return Move A forced move if one exists, otherwise {"NONE", -1, -1}.
 */
```

### Symbol: `pair<long double, Move> choose_best_probability_move(const Component &component, const ComponentStats &stats) {`

```cpp
/**
 * @brief Choose the best probabilistic move when no forced move is available.
 *
 * The default strategy is to choose the variable with the lowest mine probability.
 *
 * @param component Component being analyzed.
 * @param stats Statistics produced for that component.
 * @return Move The best guess move, or {"NONE", -1, -1} if unavailable.
 */
```

### Symbol: `Move solve_with_csp() {`

```cpp
/**
 * @brief Solve the current board using CSP decomposition and backtracking.
 *
 * This stage should split the system into components, analyze them, and return
 * either a forced move or the best probabilistic guess.
 *
 * @return Move The move selected by the CSP stage, or {"NONE", -1, -1}.
 */
```

### Symbol: `void print_move(const Move &move) {`

```cpp
/**
 * @brief Print the selected move in solver output format.
 *
 * @param move Move to print.
 */
```
