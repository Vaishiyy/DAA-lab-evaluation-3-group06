import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
from copy import deepcopy
import random
from collections import deque
import os

# ------------------ PATH SETUP ------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ------------------ CONSTANTS ------------------

TILE = 160
BOARD_SIZE = 480
BG_COLOR = "misty rose"

GOAL_STATE = (1, 2, 3, 4, 5, 6, 7, 8, 0)
DIRS = [(-1, 0), (1, 0), (0, -1), (0, 1)]

# ------------------ TRUE DP TABLE ------------------

dp_table = {}


def build_dp_table():
    if dp_table:
        return

    queue = deque([GOAL_STATE])
    dp_table[GOAL_STATE] = None

    while queue:
        curr = queue.popleft()

        idx = curr.index(0)
        r, c = divmod(idx, 3)

        for dr, dc in DIRS:
            nr, nc = r + dr, c + dc
            if 0 <= nr < 3 and 0 <= nc < 3:
                ni = nr * 3 + nc
                nxt = list(curr)
                nxt[idx], nxt[ni] = nxt[ni], nxt[idx]
                nxt = tuple(nxt)

                if nxt not in dp_table:
                    dp_table[nxt] = curr
                    queue.append(nxt)


def reconstruct_path(start):
    if start not in dp_table:
        return []

    path = [start]
    curr = start

    while curr != GOAL_STATE:
        curr = dp_table[curr]
        path.append(curr)

    return path


# ------------------ GUI ------------------

class PuzzleApp:
    def __init__(self, root):
        self.root = root
        root.title("8 Puzzle - User vs DP Machine")
        root.geometry("1500x800")
        root.configure(bg=BG_COLOR)

        self.goal_grid = [list(GOAL_STATE[0:3]), list(GOAL_STATE[3:6]), list(GOAL_STATE[6:9])]

        self.user_state = deepcopy(self.goal_grid)
        self.ai_state = deepcopy(self.goal_grid)

        self.user_steps = 0
        self.ai_steps = 0

        self.user_finished = False
        self.ai_finished = False
        self.ai_solving = False
        self.round_active = False

        self.image_name = "dog.jpg"

        self.build_top()
        self.build_sidebar()
        self.build_center()
        self.load_image()

        build_dp_table()

        self.update_boards()

    def build_top(self):
        bar = tk.Frame(self.root, bg="Dark slate grey", height=80)
        bar.pack(fill="x")

        tk.Label(
            bar,
            text="8 Puzzle - User vs AI",
            bg="Dark slate grey",
            fg="white",
            font=("Segoe UI", 22, "bold"),
        ).pack(pady=10)

    def build_sidebar(self):
        side = tk.Frame(self.root, bg="Dark slate grey", width=200)
        side.pack(side="left", fill="y")

        images = ["dog.jpg", "girl.jpg", "bike.jpg", "tiger.jpg", "mickey.jpg", "snowwhite.jpg"]

        for img_name in images:
            img_path = os.path.join(BASE_DIR, img_name)
            if not os.path.exists(img_path):
                continue
            im = Image.open(img_path).resize((90, 90))
            tk_img = ImageTk.PhotoImage(im)
            b = tk.Button(side, image=tk_img, bd=0, command=lambda x=img_name: self.change_image(x))
            b.image = tk_img
            b.pack(pady=10)

    def build_center(self):
        center = tk.Frame(self.root, bg=BG_COLOR)
        center.pack(expand=True)

        boards = tk.Frame(center, bg=BG_COLOR)
        boards.pack()

        self.user_tiles = self.create_board(boards, "USER", self.move_user)
        self.ai_tiles = self.create_board(boards, "AI", None)

        controls = tk.Frame(center, bg=BG_COLOR)
        controls.pack(pady=20)

        tk.Button(controls, text="Shuffle", font=("Segoe UI", 14), width=12, command=self.shuffle).pack(
            side="left", padx=10
        )

        tk.Button(controls, text="AI Solve", font=("Segoe UI", 14), width=12, command=self.solve).pack(
            side="left", padx=10
        )

        self.info = tk.Label(
            center,
            text="User Steps: 0 | Machine Steps: 0",
            font=("Segoe UI", 14),
            bg=BG_COLOR,
        )
        self.info.pack()

        self.status_lbl = tk.Label(
            center,
            text="Status: Shuffle to start",
            font=("Segoe UI", 12, "bold"),
            bg=BG_COLOR,
        )
        self.status_lbl.pack(pady=5)

    def create_board(self, parent, title, command):
        frame = tk.Frame(parent, bg=BG_COLOR)
        frame.pack(side="left", padx=40)

        tk.Label(frame, text=title, font=("Segoe UI", 16, "bold"), bg=BG_COLOR).pack()

        board = tk.Frame(frame, bg="black", width=BOARD_SIZE, height=BOARD_SIZE)
        board.pack(pady=10)
        board.pack_propagate(False)

        tiles = []
        for r in range(3):
            for c in range(3):
                b = tk.Button(
                    board,
                    bd=0,
                    bg="black",
                    activebackground="black",
                    command=(lambda r=r, c=c: command(r, c)) if command else None,
                )
                b.grid(row=r, column=c)
                tiles.append(b)
        return tiles

    def load_image(self):
        try:
            img_path = os.path.join(BASE_DIR, self.image_name)
            img = Image.open(img_path).resize((BOARD_SIZE, BOARD_SIZE))
            self.cuts = []
            for i in range(8):
                r, c = divmod(i, 3)
                piece = img.crop((c * TILE, r * TILE, (c + 1) * TILE, (r + 1) * TILE))
                self.cuts.append(ImageTk.PhotoImage(piece))
            self.cuts.append(None)
        except Exception:
            self.cuts = [None] * 9

    def change_image(self, img_name):
        self.image_name = img_name
        self.load_image()
        self.update_boards()

    def update_boards(self):
        self.update_board(self.user_tiles, self.user_state)
        self.update_board(self.ai_tiles, self.ai_state)
        self.info.config(text=f"User Steps: {self.user_steps} | Machine Steps: {self.ai_steps}")

    def update_board(self, tiles, state):
        flat = [x for row in state for x in row]

        for i, v in enumerate(flat):
            if v == 0:
                tiles[i].config(image="", text="", bg="black")
            else:
                if self.cuts[v - 1]:
                    tiles[i].config(image=self.cuts[v - 1], text="", bg="black")
                else:
                    tiles[i].config(text=str(v), font=("Segoe UI", 26, "bold"), fg="white", bg="black")

    def find_zero(self, state):
        for r in range(3):
            for c in range(3):
                if state[r][c] == 0:
                    return r, c

    def move_user(self, r, c):
        if not self.round_active or self.ai_solving or self.user_finished:
            return

        zr, zc = self.find_zero(self.user_state)

        if abs(r - zr) + abs(c - zc) == 1:
            self.user_state[zr][zc], self.user_state[r][c] = self.user_state[r][c], 0
            self.user_steps += 1
            self.update_boards()

            if self.user_state == self.goal_grid:
                self.user_finished = True
                self.round_active = False
                self.status_lbl.config(text="Status: User solved. Click AI Solve for result.")
                messagebox.showinfo("User Solved", f"You solved it in {self.user_steps} moves.")

    def shuffle(self):
        state = deepcopy(self.goal_grid)

        for _ in range(150):
            zr, zc = self.find_zero(state)
            dr, dc = random.choice(DIRS)
            nr, nc = zr + dr, zc + dc
            if 0 <= nr < 3 and 0 <= nc < 3:
                state[zr][zc], state[nr][nc] = state[nr][nc], 0

        self.user_state = deepcopy(state)
        self.ai_state = deepcopy(state)

        self.user_steps = 0
        self.ai_steps = 0

        self.user_finished = False
        self.ai_finished = False
        self.ai_solving = False
        self.round_active = True

        self.status_lbl.config(text="Status: Round active")
        self.update_boards()

    def solve(self):
        if not self.round_active and not self.user_finished:
            messagebox.showinfo("Ai Solve", "Press Shuffle to start a round first.")
            return

        if self.ai_solving or self.ai_finished:
            return

        self.ai_solving = True
        self.round_active = False
        self.status_lbl.config(text="Status: AI solving...")
        self.update_boards()

        start = tuple(x for row in self.ai_state for x in row)
        path = reconstruct_path(start)

        if not path:
            self.ai_solving = False
            self.status_lbl.config(text="Status: No solution from current state")
            messagebox.showinfo("AI Solver", "No solution exists!")
            return

        self.animate(path, 0)

    def animate(self, path, i):
        if i < len(path):
            flat = path[i]
            self.ai_state = [list(flat[0:3]), list(flat[3:6]), list(flat[6:9])]
            self.ai_steps = i

            self.update_boards()
            self.root.after(300, lambda: self.animate(path, i + 1))
            return

        self.ai_finished = True
        self.ai_solving = False
        self.status_lbl.config(text="Status: Round finished")
        self.update_boards()

        if self.user_finished and self.user_steps < self.ai_steps:
            messagebox.showinfo(
                "Result",
                f"User wins in {self.user_steps} moves.\nMachine solved in {self.ai_steps} moves.",
            )
        else:
            if self.user_finished:
                messagebox.showinfo(
                    "Result",
                    f"Machine wins in {self.ai_steps} moves.\nUser solved in {self.user_steps} moves.",
                )
            else:
                messagebox.showinfo(
                    "Result",
                    f"Machine wins in {self.ai_steps} moves.\nUser did not solve before machine.",
                )


# ------------------ RUN ------------------

if __name__ == "__main__":
    root = tk.Tk()
    PuzzleApp(root)
    root.mainloop()