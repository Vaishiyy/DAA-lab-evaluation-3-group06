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
