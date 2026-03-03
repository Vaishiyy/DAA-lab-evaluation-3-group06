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

def sort_row_with_protection(current, row, solved_rows):
    start = row * GRID
    goal_slice = GOAL[start:start + GRID]

    protected_positions = {
        r * GRID + c: current[r * GRID + c]
        for r in solved_rows
        for c in range(GRID)
    }

    def goal_check(s):
        return tuple(s[start:start + GRID]) == goal_slice

    def heuristic(s):
        dist = 0
        for tile in goal_slice:
            if tile == 0:
                continue
            cur = s.index(tile)
            r1, c1 = divmod(cur, GRID)
            r2, c2 = divmod(GOAL_POS[tile], GRID)
            dist += abs(r1 - r2) + abs(c1 - c2)
        return dist

    return astar_with_protection(
        current,
        goal_check,
        heuristic,
        protected_positions
    )


def solver(state):
    if state == GOAL:
        return [state]

    preprocess_path = preprocess_rows_deterministic(state)
    if not preprocess_path:
        return None

    full_path = preprocess_path
    current = preprocess_path[-1]
    if not is_row_preprocessed(current):
        return None

    solved_rows = []

    # Step 1: solve row 1.
    if GRID >= 1:
        path = sort_row_with_protection(current, 0, solved_rows)
        if not path:
            return None
        full_path += path[1:]
        current = path[-1]
        solved_rows.append(0)

    # Step 2: solve row 2 while row 1 stays locked.
    # Row 3 (and below) are free workspace because only solved_rows are protected.
    if GRID >= 2:
        path = sort_row_with_protection(current, 1, solved_rows)
        if not path:
            return None
        full_path += path[1:]
        current = path[-1]
        solved_rows.append(1)

    # Step 3: solve remaining rows the same way.
    for row in range(2, GRID):
        path = sort_row_with_protection(current, row, solved_rows)

        if not path:
            return None

        full_path += path[1:]
        current = path[-1]
        solved_rows.append(row)

    return full_path
class PuzzleApp:
    def move_user(self, r, c):
        if self.solving:
            return

        i = r * GRID + c
        zero = self.state.index(0)
        zr, zc = divmod(zero, GRID)

        if abs(r - zr) + abs(c - zc) == 1:
            lst = list(self.state)
            lst[zero], lst[i] = lst[i], lst[zero]
            self.state = tuple(lst)
            self.user_steps += 1
            self.update_display()
            if self.state == GOAL:
                messagebox.showinfo(
                    "Solved",
                    f"You solved it in {self.user_steps} moves."
                )

    def shuffle(self):
        if self.solving:
            return
        self.state = shuffle_board()
        self.user_steps = 0
        self.ai_steps = 0
        self.timer_seconds = 0
        self.update_display()

    def solve_thread(self):
        if self.solving:
            return
        self.solving = True
        self.paused = False
        self.anim_path = None
        self.anim_idx = 0
        self.ai_steps = 0
        self.pause_btn.config(state="normal", text="Pause")
        self.solve_btn.config(state="disabled")
        self.update_display()
        threading.Thread(target=self.solve_ai, daemon=True).start()

    def solve_ai(self):
        path = solver(self.state)
        if not path:
            self.root.after(0, self.solve_failed)
            return
        self.root.after(0, lambda p=path: self.start_animation(p))

    def solve_failed(self):
        self.solving = False
        self.paused = False
        self.pause_btn.config(state="disabled", text="Pause")
        self.solve_btn.config(state="normal")
        self.update_display()
        messagebox.showerror("Failed", "Solver could not find solution.")
        
    def show_help(self):
        messagebox.showinfo(
            "How To Play",
            "Click tiles adjacent to the empty slot.\n"
            "Use AI Solve to animate the deterministic solver.\n"
            "Pause freezes the board exactly at the current step."
        )
    


