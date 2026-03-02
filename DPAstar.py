import tkinter as tk
from tkinter import messagebox
import heapq
import random

TILE = 96
TILE_GAP = 10
BOARD_SIZE = TILE * 3 + TILE_GAP * 2 + 16
BG_COLOR = "#f3edf1"
PANEL_BG = "#f0e6ec"
TEXT_COLOR = "#2d2028"
ACCENT_COLOR = "#df5bab"
TILE_BG = "#fcf9fb"
EMPTY_BG = "#edd3e3"
TILE_BORDER = "#d9bccd"
BORDER_COLOR = "#2c2027"

GOAL_STATE = (1, 2, 3, 4, 5, 6, 7, 8, 0)
DIRS = [(-1, 0), (1, 0), (0, -1), (0, 1)]

goal_positions = {
    1: (0, 0),
    2: (0, 1),
    3: (0, 2),
    4: (1, 0),
    5: (1, 1),
    6: (1, 2),
    7: (2, 0),
    8: (2, 1),
}

# A* + DP SEARCH ENGINE

def manhattan(state):
    distance = 0
    for i, tile in enumerate(state):
        if tile == 0:
            continue
        r, c = divmod(i, 3)
        gr, gc = goal_positions[tile]
        distance += abs(r - gr) + abs(c - gc)
    return distance


def get_neighbors(state):
    neighbors = []
    zero_index = state.index(0)
    r, c = divmod(zero_index, 3)

    for dr, dc in DIRS:
        nr, nc = r + dr, c + dc
        if 0 <= nr < 3 and 0 <= nc < 3:
            new_index = nr * 3 + nc
            new_state = list(state)
            new_state[zero_index], new_state[new_index] = (
                new_state[new_index],
                new_state[zero_index],
            )
            neighbors.append(tuple(new_state))

    return neighbors


def reconstruct_path(parent, state):
    path = []
    while state is not None:
        path.append(state)
        state = parent[state]
    path.reverse()
    return path


def astar_dp(start):
    open_heap = []
    heapq.heappush(open_heap, (manhattan(start), 0, start))

    g_score = {start: 0}
    parent = {start: None}
    visited = set()

    while open_heap:
        _, g, current = heapq.heappop(open_heap)

        if current == GOAL_STATE:
            return reconstruct_path(parent, current)

        if current in visited:
            continue

        visited.add(current)

        for neighbor in get_neighbors(current):
            tentative_g = g + 1

            if neighbor not in g_score or tentative_g < g_score[neighbor]:
                g_score[neighbor] = tentative_g
                parent[neighbor] = current
                f_score = tentative_g + manhattan(neighbor)
                heapq.heappush(open_heap, (f_score, tentative_g, neighbor))

    return None


# SECTION 3 — GUI STRUCTURE (UI BUILDER)

class PuzzleApp:
    def __init__(self, root):
        self.root = root
        root.title("Mystic Square - Level 1")
        root.geometry("1060x760")
        root.configure(bg=BG_COLOR)

        self.state = GOAL_STATE
        self.move_count = 0
        self.ai_steps = 0
        self.solving = False
        self.round_active = False
        self.timer_seconds = 0

        self.build_layout()
        self.update_boards()
        self.tick_timer()

    def build_layout(self):
        shell = tk.Frame(self.root, bg=BG_COLOR)
        shell.pack(fill="both", expand=True)

        left_panel = tk.Frame(shell, bg=BG_COLOR)
        left_panel.pack(side="left", fill="both", expand=True)

        stats_panel = tk.Frame(shell, width=132, bg=PANEL_BG)
        stats_panel.pack(side="right", fill="y")

        self.build_top(left_panel)
        self.build_center(left_panel)
        self.build_stats(stats_panel)

    def build_top(self, parent):
        bar = tk.Frame(parent, bg=PANEL_BG, height=56)
        bar.pack(fill="x")

        tk.Label(
            bar,
            text="Mystic Square - Level 1",
            bg=PANEL_BG,
            fg=TEXT_COLOR,
            font=("Consolas", 18, "bold"),
        ).pack(side="left", padx=18)

        tk.Button(
            bar,
            text="HOW TO PLAY?",
            command=self.show_help,
            bg=PANEL_BG,
            fg=TEXT_COLOR,
        ).pack(side="right", padx=18)

    def build_center(self, parent):
        play_area = tk.Frame(parent, bg=BG_COLOR)
        play_area.pack(fill="both", expand=True)

        board_wrap = tk.Frame(play_area, bg=BG_COLOR)
        board_wrap.pack(expand=True, pady=(48, 28))
        self.tiles = self.create_board(board_wrap, self.move_user)

        controls = tk.Frame(play_area, bg=BG_COLOR)
        controls.pack(side="bottom", pady=(0, 10))

        tk.Button(controls, text="Shuffle", command=self.shuffle).pack(side="left", padx=8)
        tk.Button(controls, text="AI Solve", command=self.solve).pack(side="left", padx=8)

        self.status_lbl = tk.Label(play_area, text="Status: Ready", bg=BG_COLOR)
        self.status _lbl.pack(side="bottom", pady=(0, 20))

# =========================================================
# SECTION 4 — GAME LOGIC + CONTROLLER
# =========================================================

    def move_user(self, r, c):
        if self.solving:
            return

        index = r * 3 + c
        zero = self.state.index(0)
        zr, zc = divmod(zero, 3)

        if abs(r - zr) + abs(c - zc) == 1:
            new_state = list(self.state)
            new_state[zero], new_state[index] = new_state[index], new_state[zero]
            self.state = tuple(new_state)
            self.move_count += 1
            self.update_boards()

    def shuffle(self):
        state = GOAL_STATE
        for _ in range(50):
            state = random.choice(get_neighbors(state))
        self.state = state
        self.update_boards()

    def solve(self):
        if self.solving:
            return

        self.solving = True
        path = astar_dp(self.state)

        if not path:
            self.solving = False
            messagebox.showinfo("No Solution", "Unsolvable configuration!")
            return

        self.animate(path, 0)

    def animate(self, path, index):
        if index < len(path):
            self.state = path[index]
            self.ai_steps = index
            self.update_boards()
            self.root.after(300, lambda: self.animate(path, index + 1))
        else:
            self.solving = False


# =========================================================
# PROGRAM ENTRY POINT
# =========================================================

if __name__ == "__main__":
    root = tk.Tk()
    PuzzleApp(root)
    root.mainloop()
