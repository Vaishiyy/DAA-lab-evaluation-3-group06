import tkinter as tk
from tkinter import messagebox, ttk
import time
from threading import Thread
import random
import sys

# Increase recursion limit for backtracking
sys.setrecursionlimit(10000)

def generate_neighbors(state):
    """Generate all valid neighboring states from current state"""
    blank_pos = state.index(0)
    neighbors = []
    
    valid_moves = []
    
    if blank_pos % 3 != 0:
        valid_moves.append(-1)
    if blank_pos % 3 != 2:
        valid_moves.append(1)
    if blank_pos // 3 != 0:
        valid_moves.append(-3)
    if blank_pos // 3 != 2:
        valid_moves.append(3)
    
    for move_offset in valid_moves:
        new_blank_pos = blank_pos + move_offset
        new_state = list(state)
        new_state[blank_pos], new_state[new_blank_pos] = \
            new_state[new_blank_pos], new_state[blank_pos]
        neighbors.append(tuple(new_state))
    
    return neighbors
