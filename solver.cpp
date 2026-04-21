#include<bits/stdc++.h>
using namespace std;

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
signed main(){


    return 0;
}
