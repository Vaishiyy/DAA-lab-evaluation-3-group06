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
