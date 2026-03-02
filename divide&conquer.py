import tkinter as tk
from tkinter import messagebox
import random
import heapq
import threading
from itertools import count

# ------------------ CONSTANTS ------------------
GRID = 3
BOARD_SIZE = 480
TILE = BOARD_SIZE // GRID
BG_COLOR = "#f1e8ee"
PANEL_BG = "#efe5eb"
TEXT_COLOR = "#2f222a"
ACCENT_COLOR = "#d85ea5"
TILE_BG = "#f7f3f6"
EMPTY_BG = "#e8cfdf"
TILE_BORDER = "#d7b8ca"
BORDER_COLOR = "#34252d"

GOAL = tuple(range(1, GRID * GRID)) + (0,)
DIRS = [(-1, 0), (1, 0), (0, -1), (0, 1)]
GOAL_POS = {v: i for i, v in enumerate(GOAL)}


# NEIGHBOR GENERATION
def neighbors(state):
    i = state.index(0)
    r, c = divmod(i, GRID)
    res = []

    for dr, dc in DIRS:
        nr, nc = r + dr, c + dc
        if 0 <= nr < GRID and 0 <= nc < GRID:
            j = nr * GRID + nc
            lst = list(state)
            lst[i], lst[j] = lst[j], lst[i]
            res.append(tuple(lst))

    return res


# A* WITH POSITION PROTECTION
def astar_with_protection(current, goal_check, heuristic, protected_positions):

    def valid_neighbors(state):
        valid = []
        for n in neighbors(state):
            if all(n[idx] == val for idx, val in protected_positions.items()):
                valid.append(n)
        return valid

    tie = count()
    pq = []
    heapq.heappush(pq, (heuristic(current), 0, next(tie), current, [current]))
    visited = set()

    while pq:
        f, g, _, state, path = heapq.heappop(pq)

        if goal_check(state):
            return path

        if state in visited:
            continue
        visited.add(state)

        for nxt in valid_neighbors(state):
            if nxt not in visited:
                heapq.heappush(
                    pq,
                    (g + 1 + heuristic(nxt), g + 1, next(tie), nxt, path + [nxt])
                )

    return None

# DETERMINISTIC PREPROCESS + ROW SORT SOLVER

def is_row_preprocessed(state):
    # Each non-empty tile must be in its goal row; blank must be in last row.
    if state.index(0) // GRID != GRID - 1:
        return False

    for row in range(GRID):
        start_val = row * GRID + 1
        end_val = min(start_val + GRID, GRID * GRID)
        expected = set(range(start_val, end_val))
        row_vals = state[row * GRID:(row + 1) * GRID]
        actual = {v for v in row_vals if v != 0}
        if actual != expected:
            return False

    return True

def preprocess_rows_deterministic(state):
    full_path = [state]
    current = state

    for row in range(GRID):
        start_val = row * GRID + 1
        end_val = min(start_val + GRID, GRID * GRID)
        target_tiles = [t for t in range(start_val, end_val) if t != 0]

        protected_positions = {
            r * GRID + c: current[r * GRID + c]
            for r in range(row)
            for c in range(GRID)
        }

        def goal_check(s):
            return all(s.index(t) // GRID == row for t in target_tiles)

        def heuristic(s):
            return sum(
                abs((s.index(t) // GRID) - row) for t in target_tiles
            )

        path = astar_with_protection(
            current,
            goal_check,
            heuristic,
            protected_positions
        )

        if not path:
            return None

        full_path += path[1:]
        current = path[-1]

    if is_row_preprocessed(current):
        return full_path

    # Deterministic safety pass: enforce row membership for all tiles before sorting.
    def goal_check(s):
        return is_row_preprocessed(s)

    def heuristic(s):
        dist = 0
        for tile in range(1, GRID * GRID):
            r1 = s.index(tile) // GRID
            r2 = (tile - 1) // GRID
            dist += abs(r1 - r2)
        dist += abs((s.index(0) // GRID) - (GRID - 1))
        return dist

    path = astar_with_protection(
        current,
        goal_check,
        heuristic,
        protected_positions={}
    )
    if not path:
        return None

    full_path += path[1:]
    current = path[-1]

    if not is_row_preprocessed(current):
        return None

    return full_path

