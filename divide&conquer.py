import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import random
import heapq
import threading
import os
from copy import deepcopy

# ------------------ PATH ------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ------------------ CONSTANTS ------------------
TILE = 160
BOARD_SIZE = 480
BG_COLOR = "misty rose"

GOAL = (1,2,3,4,5,6,7,8,0)
DIRS=[(-1,0),(1,0),(0,-1),(0,1)]

# -------------------------------------------------
# MOVE GENERATOR
# -------------------------------------------------
def neighbors(state):
    i=state.index(0)
    r,c=divmod(i,3)
    res=[]
    for dr,dc in DIRS:
        nr,nc=r+dr,c+dc
        if 0<=nr<3 and 0<=nc<3:
            j=nr*3+nc
            lst=list(state)
            lst[i],lst[j]=lst[j],lst[i]
            res.append(tuple(lst))
    return res


# -------------------------------------------------
# HEURISTIC
# -------------------------------------------------
def h(state):
    dist=0
    for i,v in enumerate(state):
        if v==0: continue
        goal=v-1
        r1,c1=divmod(i,3)
        r2,c2=divmod(goal,3)
        dist+=abs(r1-r2)+abs(c1-c2)
    return dist


# -------------------------------------------------
# A* SOLVER (CONQUER STEP)
# -------------------------------------------------
def astar(start, goal_check):

    pq=[]
    heapq.heappush(pq,(h(start),0,start,[start]))
    visited=set()

    while pq:
        f,g,state,path=heapq.heappop(pq)

        if goal_check(state):
            return path

        if state in visited:
            continue
        visited.add(state)

        for nxt in neighbors(state):
            if nxt not in visited:
                heapq.heappush(pq,(g+1+h(nxt),g+1,nxt,path+[nxt]))

    return None


# -------------------------------------------------
# DIVIDE & CONQUER SOLVER
# -------------------------------------------------
def dnc_solver(state):

    if state == GOAL:
        return [state]

    path_total=[state]
    current=state

    # ---- DIVIDE → solve first row ----
    if current[:3] != GOAL[:3]:

        def row_goal(s):
            return s[:3]==GOAL[:3]

        path=astar(current,row_goal)
        path_total+=path[1:]
        current=path[-1]

    # ---- CONQUER → solve remaining ----
    def full_goal(s):
        return s==GOAL

    path=astar(current,full_goal)
    path_total+=path[1:]

    # ---- COMBINE ----
    return path_total


# -------------------------------------------------
# RANDOM BOARD
# -------------------------------------------------
def shuffle_board():
    s=list(GOAL)
    for _ in range(40):
        i=s.index(0)
        r,c=divmod(i,3)
        moves=[]
        for dr,dc in DIRS:
            nr,nc=r+dr,c+dc
            if 0<=nr<3 and 0<=nc<3:
                moves.append(nr*3+nc)
        j=random.choice(moves)
        s[i],s[j]=s[j],s[i]
    return tuple(s)


# -------------------------------------------------
# GUI
# -------------------------------------------------
class PuzzleApp:
    def __init__(self, root):
        self.root=root
        root.title("8 Puzzle - User vs AI (Divide & Conquer)")
        root.geometry("1500x800")
        root.configure(bg=BG_COLOR)

        self.user_state=shuffle_board()
        self.ai_state=deepcopy(self.user_state)

        self.user_steps=0
        self.ai_steps=0
        self.solving=False

        self.image_name="dog.jpg"

        self.build_top()
        self.build_sidebar()
        self.build_center()
        self.load_image()
        self.update_boards()

    # ---------- TOP ----------
    def build_top(self):
        bar=tk.Frame(self.root,bg="Dark slate grey",height=80)
        bar.pack(fill="x")

        tk.Label(bar,
                 text="8 Puzzle - User vs AI (Divide & Conquer)",
                 bg="Dark slate grey",
                 fg="white",
                 font=("Segoe UI",22,"bold")).pack(pady=10)

    # ---------- SIDEBAR ----------
    def build_sidebar(self):
        side=tk.Frame(self.root,bg="Dark slate grey",width=200)
        side.pack(side="left",fill="y")

        images=["dog.jpg","girl.jpg","bike.jpg",
                "tiger.jpg","mickey.jpg","snowwhite.jpg"]

        for img_name in images:
            img_path=os.path.join(BASE_DIR,img_name)
            if not os.path.exists(img_path):
                continue
            im=Image.open(img_path).resize((90,90))
            tk_img=ImageTk.PhotoImage(im)
            b=tk.Button(side,image=tk_img,bd=0,
                        command=lambda x=img_name:self.change_image(x))
            b.image=tk_img
            b.pack(pady=10)

    # ---------- CENTER ----------
    def build_center(self):
        center=tk.Frame(self.root,bg=BG_COLOR)
        center.pack(expand=True)

        boards=tk.Frame(center,bg=BG_COLOR)
        boards.pack()

        self.user_tiles=self.create_board(boards,"USER",self.move_user)
        self.ai_tiles=self.create_board(boards,"AI",None)

        controls=tk.Frame(center,bg=BG_COLOR)
        controls.pack(pady=20)

        tk.Button(controls,text="Shuffle",
                  font=("Segoe UI",14),
                  width=12,
                  command=self.shuffle).pack(side="left",padx=10)

        tk.Button(controls,text="AI Solve",
                  font=("Segoe UI",14),
                  width=12,
                  command=self.solve_thread).pack(side="left",padx=10)

        self.info_lbl=tk.Label(center,
                               text="User Steps: 0 | AI Steps: 0",
                               font=("Segoe UI",14),
                               bg=BG_COLOR)
        self.info_lbl.pack()

    # ---------- BOARD ----------
    def create_board(self,parent,title,command):
        frame=tk.Frame(parent,bg=BG_COLOR)
        frame.pack(side="left",padx=40)

        tk.Label(frame,text=title,
                 font=("Segoe UI",16,"bold"),
                 bg=BG_COLOR).pack()

        board=tk.Frame(frame,bg="black",
                       width=BOARD_SIZE,height=BOARD_SIZE)
        board.pack(pady=10)
        board.pack_propagate(False)

        tiles=[]
        for r in range(3):
            for c in range(3):
                btn=tk.Button(board,
                              bd=0,
                              bg="black",
                              command=(lambda r=r,c=c:command(r,c))
                              if command else None)
                btn.grid(row=r,column=c)
                tiles.append(btn)
        return tiles

    # ---------- IMAGE ----------
    def load_image(self):
        try:
            img_path=os.path.join(BASE_DIR,self.image_name)
            img=Image.open(img_path).resize((BOARD_SIZE,BOARD_SIZE))
            self.cuts=[]
            for i in range(8):
                r,c=divmod(i,3)
                piece=img.crop((c*TILE,r*TILE,
                                (c+1)*TILE,(r+1)*TILE))
                self.cuts.append(ImageTk.PhotoImage(piece))
            self.cuts.append(None)
        except:
            self.cuts=[None]*9

    def change_image(self,img_name):
        self.image_name=img_name
        self.load_image()
        self.update_boards()

    # ---------- UPDATE ----------
    def update_boards(self):
        self.update_board(self.user_tiles,self.user_state)
        self.update_board(self.ai_tiles,self.ai_state)
        self.info_lbl.config(
            text=f"User Steps: {self.user_steps} | AI Steps: {self.ai_steps}"
        )

    def update_board(self,tiles,state):
        for i,v in enumerate(state):
            if v==0:
                tiles[i].config(image="",bg="black")
            else:
                tiles[i].config(image=self.cuts[v-1])

    # ---------- USER MOVE ----------
    def move_user(self,r,c):
        i=r*3+c
        zero=self.user_state.index(0)
        zr,zc=divmod(zero,3)

        if abs(r-zr)+abs(c-zc)==1:
            lst=list(self.user_state)
            lst[zero],lst[i]=lst[i],lst[zero]
            self.user_state=tuple(lst)
            self.user_steps+=1
            self.update_boards()

            if self.user_state==GOAL:
                messagebox.showinfo(
                    "User Wins",
                    f"You solved in {self.user_steps} steps!"
                )

    # ---------- SHUFFLE ----------
    def shuffle(self):
        if self.solving:
            return
        self.user_state=shuffle_board()
        self.ai_state=deepcopy(self.user_state)
        self.user_steps=0
        self.ai_steps=0
        self.update_boards()

    # ---------- AI ----------
    def solve_thread(self):
        if self.solving:
            return
        self.solving=True
        t=threading.Thread(target=self.solve_ai)
        t.start()

    def solve_ai(self):
        path=dnc_solver(self.ai_state)
        if not path:
            self.solving=False
            return
        self.animate(path)

    def animate(self,path):
        if not path:
            self.solving=False
            messagebox.showinfo(
                "AI Finished",
                f"AI solved in {self.ai_steps} steps!"
            )
            return

        self.ai_state=path.pop(0)
        self.ai_steps+=1
        self.update_boards()
        self.root.after(300,lambda:self.animate(path))


# -------------------------------------------------
# RUN
# -------------------------------------------------
if __name__=="__main__":
    root=tk.Tk()
    PuzzleApp(root)
    root.mainloop()