#include<bits/stdc++.h>
using namespace std;

using CellPos = pair<int, int>;

const int HIDDEN = -1;
const int FLAGGED = -2;

const int VAR_UNKNOWN = -1;
const int VAR_SAFE = 0;
const int VAR_MINE = 1;
const int dx[8] = {-1, -1, -1, 0, 0, 1, 1, 1};
const int dy[8] = {-1, 0, 1, -1, 1, -1, 0, 1};

struct Move {
    string type;
    int row;
    int col;
};

struct Constraint {
    vector<int> vars;
    int mines_needed;
};

struct Component {
    vector<int> vars;
    vector<int> constraint_ids;
};

struct ComponentStats {
    long long total_solutions;
    vector<long long> mine_count;
};

int rows, cols;
vector<vector<int>> board;
vector<CellPos> frontier_cells;
map<CellPos, int> frontier_id;
vector<Constraint> constraints;
vector<int> assignment;
vector<vector<int>> var_graph;
vector<Component> components;

/**
 * @file solver.cpp
 * @brief Minesweeper solver entry point.
 *
 * Expected input format:
 * - The first line contains two integers: rows cols
 * - The next `rows` lines each contain `cols` integers describing the current visible board state
 *
 * Cell encoding:
 * -1 : hidden cell
 * -2 : flagged cell
 *  0 : revealed cell with 0 neighboring mines
 *  1..8 : revealed cell with the corresponding number of neighboring mines
 *
 * Example input:
 * 5 5
 * 1 1 1 -1 -1
 * 1 -2 2 -1 -1
 * 1 2 3 2 1
 * 0 1 -1 -1 1
 * 0 1 2 2 1
 *
 * Expected output format:
 * - The solver returns exactly one action for the next move
 * - Possible outputs are:
 *   SAFE row col
 *   MINE row col
 *   NONE
 *
 * Output meaning:
 * - SAFE row col : the solver concludes that the cell can be safely revealed
 * - MINE row col : the solver concludes that the cell should be flagged as a mine
 * - NONE : no deterministic move can be inferred from the current board
 *
 * Example output:
 * SAFE 0 3
 *
 * Notes:
 * - Indices are zero-based.
 * - The solver receives only the visible board state, not the true mine layout.
 * - The solver is intended to be called repeatedly, one move at a time.
 */

/**
 * @brief Check whether a cell coordinate is inside the board.
 *
 * @param row Row index to validate.
 * @param col Column index to validate.
 * @return true if the coordinate is valid, otherwise false.
 */
bool is_inside(int row, int col) {
    return row >= 0 && row < rows && col >= 0 && col < cols;
}

/**
 * @brief Check whether a cell is still hidden.
 *
 * @param row Row index of the cell.
 * @param col Column index of the cell.
 * @return true if the cell is hidden, otherwise false.
 */
bool is_hidden(int row, int col) {
    return board[row][col] == HIDDEN;
}

/**
 * @brief Check whether a cell is currently flagged.
 *
 * @param row Row index of the cell.
 * @param col Column index of the cell.
 * @return true if the cell is flagged, otherwise false.
 */
bool is_flagged(int row, int col) {
    return board[row][col] == FLAGGED;
}

/**
 * @brief Check whether a cell has already been revealed as a number.
 *
 * @param row Row index of the cell.
 * @param col Column index of the cell.
 * @return true if the cell contains a revealed value from 0 to 8.
 */
bool is_revealed_number(int row, int col) {
    return board[row][col] >= 0; 
}

/**
 * @brief Return all 8 neighboring coordinates around a cell.
 *
 * @param row Row index of the center cell.
 * @param col Column index of the center cell.
 * @return vector<CellPos> Neighbor coordinates in 8 directions.
 */
vector<CellPos> get_neighbors(int row, int col) {
    vector<CellPos> ans;
    for (int i = 0;  i < 8; i++){
        int neighbor_row = row + dx[i];
        int neighbor_col = col + dy[i];
        if (is_inside(neighbor_row, neighbor_col))
            ans.push_back({neighbor_row, neighbor_col});
    }
    return ans;
}

/**
 * @brief Read the current visible board state from standard input.
 *
 * This function should load the board dimensions and the encoded cell values.
 */
void read_input() {
    cin >> rows >> cols;
    board = vector<vector<int>> (rows, vector<int> (cols));
    for (auto &x : board){
        for (auto &y : x) cin >> y;
    }
}

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
bool is_frontier_cell(int row, int col) {
    if (!is_hidden(row, col)) return false;
    for (CellPos cell : get_neighbors(row, col)){
        if (is_revealed_number(cell.first, cell.second)) return true;
    }
    return false;
}

bool is_start_board(){
    for (int row = 0; row < rows; row++)
        for (int col = 0; col < cols; col++)
            if (!is_hidden(row, col)) return false;
    return true;
}

/**
 * @brief Collect all frontier cells and map them to variable ids.
 *
 * This function should fill frontier_cells and frontier_id.
 */
void collect_frontier_cells() {
    frontier_cells.clear();
    frontier_id.clear();
    for (int row = 0; row < rows; row++)
        for (int col = 0; col < cols; col++)
            if (is_frontier_cell(row, col)){
                frontier_id[{row, col}] = frontier_cells.size();
                frontier_cells.push_back({row, col});
            }
}

/**
 * @brief Normalize a constraint by sorting and removing duplicated variables.
 *
 * @param constraint Constraint to normalize.
 */
void normalize_constraint(Constraint &constraint) {
    vector<int> &vars = constraint.vars;
    sort(vars.begin(), vars.end());
    vars.resize(unique(vars.begin(), vars.end()) - vars.begin());
}

/**
 * @brief Build linear constraints from the currently revealed numbered cells.
 *
 * Each numbered cell should generate one equation of the form:
 * x1 + x2 + ... + xm = k
 * where xi represents a frontier variable and k is the number of mines still needed.
 */
void build_constraints() {
    constraints.clear();
    for (int row = 0; row < rows; row++)
        for (int col = 0; col < cols; col++){
            if (!is_revealed_number(row, col)) continue;
            vector<CellPos> neighbors = get_neighbors(row, col);
            Constraint newCons;
            newCons.vars.clear();
            newCons.mines_needed = board[row][col];
            for (CellPos cell : neighbors){
                if (is_hidden(cell.first, cell.second)) newCons.vars.push_back(frontier_id[cell]); 
                if (is_flagged(cell.first, cell.second)) newCons.mines_needed--;
            }
            normalize_constraint(newCons);
            if (!newCons.vars.empty())
                constraints.push_back(newCons);
        }
}

/**
 * @brief Check whether one sorted variable set is a subset of another.
 *
 * @param a Candidate subset.
 * @param b Candidate superset.
 * @return true if every variable in a also appears in b.
 */
bool is_subset(const vector<int> &a, const vector<int> &b) {
    map<int, bool> dd;
    for (int x : b) dd[x] = 1;
    for (int x : a) if (!dd[x]) return false;
    return true;
}

/**
 * @brief Compute the set difference between two sorted variable sets.
 *
 * This helper is mainly used for subset or equation-subtraction inference.
 *
 * @param a Smaller set.
 * @param b Larger set.
 * @return vector<int> Variables that are in b but not in a.
 */
vector<int> set_difference_vec(const vector<int> &a, const vector<int> &b) {
    vector<int> Variables;
    map<int, bool> dd;
    for (int x : a) dd[x] = 1;
    for (int x : b) if (!dd[x]) Variables.push_back(x);
    return Variables;
}

/**
 * @brief Apply direct deterministic rules on a single constraint.
 *
 * Main ideas:
 * - If mines_needed == 0, all remaining variables are SAFE.
 * - If mines_needed == vars.size(), all remaining variables are MINE.
 *
 * @return Move A forced move if one is found, otherwise {"NONE", -1, -1}.
 */
Move apply_basic_inference() {
    for (auto constraint : constraints){
        if (constraint.mines_needed == 0){
            CellPos cell = frontier_cells[constraint.vars[0]];
            return {"SAFE", cell.first, cell.second};
        }
        if (constraint.mines_needed == (int)constraint.vars.size()){
            CellPos cell = frontier_cells[constraint.vars[0]];
            return {"MINE", cell.first, cell.second};
        }
    }
    return {"NONE", -1, -1};
}

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
bool generate_subset_constraints() {
    bool added = false;
    vector<Constraint> new_constraints;

    for (int i = 0; i < (int)constraints.size(); i++) {
        for (int j = 0; j < (int)constraints.size(); j++) {
            if (i == j) continue;
            if (!is_subset(constraints[i].vars, constraints[j].vars)) continue;

            Constraint newCons;
            newCons.vars = set_difference_vec(constraints[i].vars, constraints[j].vars);
            newCons.mines_needed = constraints[j].mines_needed - constraints[i].mines_needed;

            if (newCons.vars.empty()) continue;
            if (newCons.mines_needed < 0) continue;
            if (newCons.mines_needed > (int)newCons.vars.size()) continue;

            normalize_constraint(newCons);

            bool exists = false;

            for (const Constraint &oldCons : constraints) {
                if (oldCons.vars == newCons.vars && oldCons.mines_needed == newCons.mines_needed) {
                    exists = true;
                    break;
                }
            }

            if (!exists) {
                for (const Constraint &extraCons : new_constraints) {
                    if (extraCons.vars == newCons.vars && extraCons.mines_needed == newCons.mines_needed) {
                        exists = true;
                        break;
                    }
                }
            }

            if (!exists) {
                new_constraints.push_back(newCons);
                added = true;
            }
        }
    }

    for (const Constraint &c : new_constraints) {
        constraints.push_back(c);
    }

    return added;
}

/**
 * @brief Repeatedly run deterministic inference until no more progress is possible.
 *
 * This function should keep applying direct inference rules first. If no forced
 * move is found, it should try to generate new subset-derived constraints and
 * repeat the process until either a move is found or no new information can be added.
 *
 * @return Move A forced move if one is found, otherwise {"NONE", -1, -1}.
 */
Move deterministic_inference() {
    Move move = apply_basic_inference();
    if (move.row != -1)
        return move;
    while (generate_subset_constraints())
    {
        Move move = apply_basic_inference();
        if (move.row != -1)
            return move;
    }
    return {"NONE", -1, -1};    
}

/**
 * @brief Build an adjacency graph between frontier variables.
 *
 * Two variables should be connected if they appear together in at least one constraint.
 * This graph is used to split the CSP into independent components.
 */
void build_variable_graph() {
    var_graph = vector<vector<int>>(frontier_cells.size());
    set<pair<int, int>> edges;
    for (Constraint &constraint: constraints){
        for (int i = 0; i < constraint.vars.size(); i++)
            for (int j = i + 1; j < constraint.vars.size(); j++)
                edges.insert({constraint.vars[i], constraint.vars[j]});
    }
    for (auto x : edges) {
        var_graph[x.first].push_back(x.second);
        var_graph[x.second].push_back(x.first);
    }
}

/**
 * @brief Traverse one connected component of the variable graph.
 *
 * @param start_var Variable id where DFS starts.
 * @param visited_vars Marks variables that have already been visited.
 * @param component Output component being constructed.
 */
void dfs_component(int start_var, vector<int> &visited_vars, Component &component) {
    visited_vars[start_var] = 1;
    component.vars.push_back(start_var);

    for (int next_var : var_graph[start_var]) {
        if (!visited_vars[next_var]) {
            dfs_component(next_var, visited_vars, component);
        }
    }
}

/**
 * @brief Split the full constraint system into connected components.
 *
 * Each component contains the frontier variables and constraints that depend on each other.
 */
void split_into_components() {
    components.clear();

    int num_vars = (int)frontier_cells.size();
    vector<int> visited_vars(num_vars, 0);

    for (int start_var = 0; start_var < num_vars; start_var++) {
        if (visited_vars[start_var]) continue;

        Component component;
        dfs_component(start_var, visited_vars, component);

        vector<int> in_component(num_vars, 0);
        for (int var : component.vars) {
            in_component[var] = 1;
        }

        for (int cid = 0; cid < (int)constraints.size(); cid++) {
            if (in_component[constraints[cid].vars[0]])
                component.constraint_ids.push_back(cid);
        }
        components.push_back(component);
    }
}

/**
 * @brief Check whether a partial assignment is still consistent with a component.
 *
 * This function is used for pruning during recursive CSP search.
 *
 * @param component Component currently being solved.
 * @param local_assignment Current partial local assignment.
 * @return true if the partial assignment is still valid, otherwise false.
 */
bool is_partial_assignment_valid(const Component &component, const vector<int> &local_assignment) {
    map<int, int> local_index;
    for (int i = 0; i < (int)component.vars.size(); i++) {
        local_index[component.vars[i]] = i;
    }

    for (int cid : component.constraint_ids) {
        const Constraint &constraint = constraints[cid];

        int mine_count = 0;
        int unknown_count = 0;

        for (int global_var : constraint.vars) {
            int idx = local_index[global_var];
            int value = local_assignment[idx];

            if (value == VAR_MINE) mine_count++;
            else if (value == VAR_UNKNOWN) unknown_count++;
        }

        if (mine_count > constraint.mines_needed) return false;
        if (mine_count + unknown_count < constraint.mines_needed) return false;
    }

    return true;
}

/**
 * @brief Enumerate all valid assignments for one component using backtracking.
 *
 * @param component Component currently being analyzed.
 * @param depth Current recursion depth.
 * @param local_assignment Current assignment of local variables.
 * @param stats Statistics accumulated from valid solutions.
 */
void backtrack_component(
    const Component &component,
    int depth,
    vector<int> &local_assignment,
    ComponentStats &stats
) {
    if (!is_partial_assignment_valid(component, local_assignment)) return;
    if (depth == (int)component.vars.size()){
        stats.total_solutions++;
        for (int i = 0; i < component.vars.size(); i++){
            stats.mine_count[i] += local_assignment[i];
        }
        return;
    }
    for (int j = 0; j <= 1; j++){
        local_assignment[depth] = j;    
        backtrack_component(component, depth+1, local_assignment, stats);
        local_assignment[depth] = VAR_UNKNOWN;
    }
}

/**
 * @brief Analyze one component and compute solution statistics.
 *
 * @param component Connected component to solve.
 * @return ComponentStats Total valid solutions and mine counts per variable.
 */
ComponentStats analyze_component(const Component &component) {
    ComponentStats stats;
    stats.total_solutions = 0;
    stats.mine_count = vector<long long> (component.vars.size(), 0);
    vector<int> local_assignment(component.vars.size(), VAR_UNKNOWN);
    backtrack_component(component, 0, local_assignment, stats);
    return stats;
}

/**
 * @brief Find a guaranteed SAFE or MINE move from component statistics.
 *
 * @param component Component being analyzed.
 * @param stats Statistics produced for that component.
 * @return Move A forced move if one exists, otherwise {"NONE", -1, -1}.
 */
Move find_forced_move_from_stats(const Component &component, const ComponentStats &stats) {
    
    for (int i = 0; i < component.vars.size(); i++){
        if (stats.mine_count[i] == stats.total_solutions){
            CellPos cell = frontier_cells[component.vars[i]];
            return {"MINE", cell.first, cell.second};
        }
        if (stats.mine_count[i] == 0){
            CellPos cell = frontier_cells[component.vars[i]];
            return {"SAFE", cell.first, cell.second};
        }
    }
    return {"NONE", -1, -1};
}

/**
 * @brief Choose the best probabilistic move when no forced move is available.
 *
 * The default strategy is to choose the variable with the lowest mine probability.
 *
 * @param component Component being analyzed.
 * @param stats Statistics produced for that component.
 * @return Move The best guess move, or {"NONE", -1, -1} if unavailable.
 */
pair<long double, Move> choose_best_probability_move(const Component &component, const ComponentStats &stats) {
    if (stats.total_solutions == 0) return {100, {"NONE", -1, -1}};
    double curMin = 1;
    int best = -1;
    for (int i = 0; i < component.vars.size(); i++){
        if ((long double)stats.mine_count[i]/stats.total_solutions < curMin){
            best = component.vars[i];
            curMin = (long double)stats.mine_count[i]/stats.total_solutions;
        }
    }
    CellPos cell = frontier_cells[best];
    return {curMin, {"SAFE", cell.first, cell.second}};
}

/**
 * @brief Solve the current board using CSP decomposition and backtracking.
 *
 * This stage should split the system into components, analyze them, and return
 * either a forced move or the best probabilistic guess.
 *
 * @return Move The move selected by the CSP stage, or {"NONE", -1, -1}.
 */
Move solve_with_csp() {
    build_variable_graph();
    split_into_components();
    pair<long double, Move> best = {100, {"NONE", -1, -1}};
    for (Component &component : components){
        ComponentStats stats = analyze_component(component);
        Move move = find_forced_move_from_stats(component, stats);
        if (move.row != -1){
            return move;
        }
        pair<long double, Move> cur = choose_best_probability_move(component, stats);
        if (best.first > cur.first)
            best = cur;
    }
    return best.second;
}

/**
 * @brief Print the selected move in solver output format.
 *
 * @param move Move to print.
 */
void print_move(const Move &move) {
    cout << move.type << ' ' << move.row << ' ' << move.col;
    exit(0);
}

signed main(){
    read_input();
    if (is_start_board()){
        Move move = {"SAFE", 0, 0};
        print_move(move);
    }
    collect_frontier_cells();
    build_constraints();
    Move move = deterministic_inference();
    if (move.row != -1)
        print_move(move);
    else 
        print_move(solve_with_csp());
    return 0;
}
