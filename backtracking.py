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
    
def pure_backtrack_simple(current, goal, visited, path, explored_states, depth=0, max_depth=100):
    """
    Pure Simple Recursive Backtracking Algorithm
    Now also tracks ALL explored states in order
    """
    
    # Record this state as explored
    explored_states.append(current)
    
    # Base case: goal found
    if current == goal:
        return path + [current]
    
    # Prevent infinite recursion
    if depth > max_depth:
        return None
    
    # Mark as visited
    visited.add(current)
    
    # Generate neighbors on-the-fly
    neighbors = generate_neighbors(current)
    
    # Try each unvisited neighbor
    for neighbor in neighbors:
        if neighbor not in visited:
            result = pure_backtrack_simple(neighbor, goal, visited, path + [current], 
                                          explored_states, depth + 1, max_depth)
            if result is not None:
                return result
    
    # Backtrack
    return None
class EightPuzzleUI:
    """Main UI for 8-Puzzle Game with Dual Visualization"""
    
    def _init_(self, root):
        self.root = root
        self.root.title("8-Puzzle Solver - Dual Visualization")
        self.root.geometry("1400x750")
        self.root.configure(bg="#FFFFFF")
        
        # Game state
        self.current_state = (1, 2, 3, 4, 5, 6, 7, 8, 0)
        self.goal_state = (1, 2, 3, 4, 5, 6, 7, 8, 0)
        self.move_count = 0
        self.elapsed_time = 0
        self.solving = False
        self.tiles_left = {}
        self.tiles_right = {}
        self.tile_buttons_left = {}
        self.tile_buttons_right = {}
        self.timer_running = True
        self.status_label = None
        self.explored_states = []
        self.solution_path = []
        self.exploration_index = 0
        self.solution_index = 0

         # Create UI
        self.create_ui()
        self.start_timer()
     def create_ui(self):
        """Create the user interface with dual visualization"""
        
        # Main container
        main_frame = tk.Frame(self.root, bg="#FFFFFF")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # ===== CONTROL PANEL (TOP) =====
        control_frame = tk.Frame(main_frame, bg="#FFFFFF")
        control_frame.pack(fill=tk.X, pady=(0, 20))
        
        title_label = tk.Label(
            control_frame,
            text="8-Puzzle Solver - Dual Visualization",
            font=("Arial", 18, "bold"),
            bg="#FFFFFF",
            fg="#333333"
        )
        title_label.pack(side=tk.LEFT)
        
        how_to_button = tk.Button(
            control_frame,
            text="HOW TO PLAY?",
            font=("Arial", 10, "bold"),
            bg="#FFFFFF",
            fg="#333333",
            relief=tk.SOLID,
            bd=2,
            padx=15,
            pady=5,
            command=self.show_instructions
        )
        how_to_button.pack(side=tk.RIGHT, padx=(0, 10))
        
        # ===== MIDDLE SECTION: Two Puzzles Side by Side =====
        middle_frame = tk.Frame(main_frame, bg="#FFFFFF")
        middle_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # LEFT SIDE - EXPLORATION VISUALIZATION
        left_container = tk.Frame(middle_frame, bg="#FFFFFF")
        left_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        left_title = tk.Label(
            left_container,
            text=" Algorithm Exploration",
            font=("Arial", 14, "bold"),
            bg="#FFFFFF",
            fg="#E6A8D7"
        )
        left_title.pack(pady=(0, 10))
        
        # Left puzzle container
        left_puzzle_container = tk.Frame(
            left_container,
            bg="#F5D5E3",
            relief=tk.SOLID,
            bd=3
        )
        left_puzzle_container.pack(fill=tk.BOTH, expand=True)
        
        # Left puzzle grid
        left_grid_frame = tk.Frame(left_puzzle_container, bg="#F5D5E3")
        left_grid_frame.pack(expand=True, pady=10)
        
        for i in range(9):
            row = i // 3
            col = i % 3
            tile_button = tk.Button(
                left_grid_frame,
                text=str(self.current_state[i]) if self.current_state[i] != 0 else "",
                width=8,
                height=4,
                font=("Arial", 20, "bold"),
                bg="#FFFFFF" if self.current_state[i] != 0 else "#F5D5E3",
                fg="#333333",
                relief=tk.SOLID,
                bd=3,
                state=tk.DISABLED
            )
            tile_button.grid(row=row, column=col, padx=3, pady=3)
            self.tile_buttons_left[i] = tile_button
        
        # LEFT info label
        self.left_info_label = tk.Label(
            left_container,
            text="Exploration Progress: 0 states",
            font=("Arial", 10),
            bg="#FFFFFF",
            fg="#E6A8D7"
        )
        self.left_info_label.pack(pady=(10, 0))
        
        # RIGHT SIDE - SOLUTION PATH VISUALIZATION
        right_container = tk.Frame(middle_frame, bg="#FFFFFF")
        right_container.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        right_title = tk.Label(
            right_container,
            text="✓ Solution Path",
            font=("Arial", 14, "bold"),
            bg="#FFFFFF",
            fg="#27AE60"
        )
        right_title.pack(pady=(0, 10))
        
        # Right puzzle container
        right_puzzle_container = tk.Frame(
            right_container,
            bg="#E8F8F5",
            relief=tk.SOLID,
            bd=3
        )
        right_puzzle_container.pack(fill=tk.BOTH, expand=True)
        
        # Right puzzle grid
        right_grid_frame = tk.Frame(right_puzzle_container, bg="#E8F8F5")
        right_grid_frame.pack(expand=True, pady=10)
        
        for i in range(9):
            row = i // 3
            col = i % 3
            tile_button = tk.Button(
                right_grid_frame,
                text=str(self.current_state[i]) if self.current_state[i] != 0 else "",
                width=8,
                height=4,
                font=("Arial", 20, "bold"),
                bg="#FFFFFF" if self.current_state[i] != 0 else "#E8F8F5",
                fg="#333333",
                relief=tk.SOLID,
                bd=3,
                state=tk.DISABLED
            )
            tile_button.grid(row=row, column=col, padx=3, pady=3)
            self.tile_buttons_right[i] = tile_button
        
        # RIGHT info label
        self.right_info_label = tk.Label(
            right_container,
            text="Solution Steps: 0/0",
            font=("Arial", 10),
            bg="#FFFFFF",
            fg="#27AE60"
        )
        self.right_info_label.pack(pady=(10, 0))
        
        # ===== BOTTOM CONTROL PANEL =====
        bottom_frame = tk.Frame(main_frame, bg="#FFFFFF")
        bottom_frame.pack(fill=tk.X)
        
        button_row1 = tk.Frame(bottom_frame, bg="#FFFFFF")
        button_row1.pack(fill=tk.X, pady=(0, 10))
        
        shuffle_button = tk.Button(
            button_row1,
            text=" SHUFFLE",
            font=("Arial", 11, "bold"),
            bg="#E6A8D7",
            fg="white",
            relief=tk.SOLID,
            bd=0,
            padx=20,
            pady=10,
            command=self.shuffle_tiles
        )
        shuffle_button.pack(side=tk.LEFT, padx=(0, 10))
        
        reset_button = tk.Button(
            button_row1,
            text="↺ RESET",
            font=("Arial", 11, "bold"),
            bg="#E6A8D7",
            fg="white",
            relief=tk.SOLID,
            bd=0,
            padx=20,
            pady=10,
            command=self.reset_game
        )
        reset_button.pack(side=tk.LEFT)
        
        button_row2 = tk.Frame(bottom_frame, bg="#FFFFFF")
        button_row2.pack(fill=tk.X)
        
        solve_button = tk.Button(
            button_row2,
            text=" SOLVE & VISUALIZE",
            font=("Arial", 11, "bold"),
            bg="#E6A8D7",
            fg="white",
            relief=tk.SOLID,
            bd=0,
            padx=20,
            pady=10,
            command=self.solve_with_visualization
        )
        solve_button.pack(side=tk.LEFT)
        
        self.status_label = tk.Label(
            bottom_frame,
            text="",
            font=("Arial", 10),
            bg="#FFFFFF",
            fg="#E6A8D7"
        )
        self.status_label.pack(fill=tk.X, pady=(10, 0))
    
    def start_timer(self):
        """Start the game timer"""
        def update_timer():
            while self.timer_running:
                self.elapsed_time += 1
                time.sleep(1)
        
        Thread(target=update_timer, daemon=True).start()
    
    def shuffle_tiles(self):
        """Shuffle the puzzle tiles"""
        if self.solving:
            messagebox.showwarning("Solving", "Cannot shuffle while solving!")
            return
        
        self.status_label.config(text="Shuffling tiles...")
        self.root.update()
        
        shuffled = self.goal_state
        for _ in range(random.randint(10, 20)):
            blank_pos = shuffled.index(0)
            valid_moves = []
            
            if blank_pos % 3 != 0:
                valid_moves.append(-1)
            if blank_pos % 3 != 2:
                valid_moves.append(1)
            if blank_pos // 3 != 0:
                valid_moves.append(-3)
            if blank_pos // 3 != 2:
                valid_moves.append(3)
            
            if valid_moves:
                move = random.choice(valid_moves)
                new_pos = blank_pos + move
                shuffled_list = list(shuffled)
                shuffled_list[blank_pos], shuffled_list[new_pos] = \
                    shuffled_list[new_pos], shuffled_list[blank_pos]
                shuffled = tuple(shuffled_list)
        
        self.current_state = shuffled
        self.move_count = 0
        self.elapsed_time = 0
        self.update_both_displays(self.current_state, self.current_state)
        self.status_label.config(text="✓ Tiles shuffled! Ready to solve.")
    
    def update_both_displays(self, left_state, right_state):
        """Update both puzzle displays"""
        for i in range(9):
            number = left_state[i]
            button = self.tile_buttons_left[i]
            if number == 0:
                button.config(text="", bg="#F5D5E3")
            else:
                button.config(text=str(number), bg="#FFFFFF")
        
        for i in range(9):
            number = right_state[i]
            button = self.tile_buttons_right[i]
            if number == 0:
                button.config(text="", bg="#E8F8F5")
            else:
                button.config(text=str(number), bg="#FFFFFF")
    
    def solve_with_visualization(self):
        """Solve and show dual visualization"""
        if self.solving:
            messagebox.showinfo("Already Solving", "Wait for current solve to complete!")
            return
        
        if self.current_state == self.goal_state:
            messagebox.showinfo("Already Solved", "The puzzle is already solved!")
            return
        
        self.solving = True
        self.status_label.config(text=" Solving and recording exploration...")
        self.root.update()
        
        def solve_in_thread():
            try:
                start_time = time.time()
                
                self.explored_states = []
                visited = set()
                self.solution_path = pure_backtrack_simple(
                    self.current_state,
                    self.goal_state,
                    visited,
                    [],
                    self.explored_states,
                    depth=0,
                    max_depth=50
                )
                
                elapsed = time.time() - start_time
                
                if self.solution_path:
                    messagebox.showinfo(
                        "Solution Found!",
                        f"Time: {elapsed:.2f}s\n"
                        f"States explored: {len(self.explored_states)}\n"
                        f"Solution length: {len(self.solution_path) - 1} moves"
                    )
                    self.animate_dual_visualization()
                else:
                    messagebox.showwarning(
                        "No Solution",
                        f"Could not find solution.\n"
                        f"States explored: {len(self.explored_states)}"
                    )
                    self.solving = False
                    self.status_label.config(text="✗ No solution found!")
                    
            except RecursionError:
                messagebox.showerror("Error", "Recursion limit exceeded!")
                self.solving = False
                self.status_label.config(text="✗ Error!")
            except Exception as e:
                messagebox.showerror("Error", f"Error: {str(e)}")
                self.solving = False
                self.status_label.config(text="✗ Error!")
        
        Thread(target=solve_in_thread, daemon=True).start()
    
    def animate_dual_visualization(self):
        def animate():
            self.exploration_index = 0
            self.solution_index = 0
            total_exploration = len(self.explored_states)
            total_solution = len(self.solution_path)
            
            while self.exploration_index < total_exploration or self.solution_index < total_solution:
                
                if self.exploration_index < total_exploration:
                    current_explored = self.explored_states[self.exploration_index]
                    self.update_left_display(current_explored)
                    self.left_info_label.config(
                        text=f"Exploration Progress: {self.exploration_index + 1}/{total_exploration} states"
                    )
                    self.exploration_index += 1
                
                if self.solution_index < total_solution:
                    current_solution = self.solution_path[self.solution_index]
                    self.update_right_display(current_solution)
                    self.right_info_label.config(
                        text=f"Solution Steps: {self.solution_index + 1}/{total_solution}"
                    )
                    self.solution_index += 1
                
                self.root.update()
                time.sleep(0.1)
            
            self.solving = False
            self.status_label.config(text="✓ Visualization complete!")
        
        Thread(target=animate, daemon=True).start()
    
    def update_left_display(self, state):
        for i in range(9):
            number = state[i]
            button = self.tile_buttons_left[i]
            if number == 0:
                button.config(text="", bg="#F5D5E3")
            else:
                button.config(text=str(number), bg="#FFFFFF")
    
    def update_right_display(self, state):
        for i in range(9):
            number = state[i]
            button = self.tile_buttons_right[i]
            if number == 0:
                button.config(text="", bg="#E8F8F5")
            else:
                button.config(text=str(number), bg="#FFFFFF")
    
    def reset_game(self):
        if self.solving:
            messagebox.showwarning("Solving", "Cannot reset while solving!")
            return
        
        self.current_state = (1, 2, 3, 4, 5, 6, 7, 8, 0)
        self.move_count = 0
        self.elapsed_time = 0
        self.explored_states = []
        self.solution_path = []
        self.exploration_index = 0
        self.solution_index = 0
        self.update_both_displays(self.current_state, self.current_state)
        self.left_info_label.config(text="Exploration Progress: 0 states")
        self.right_info_label.config(text="Solution Steps: 0/0")
        self.status_label.config(text="Game reset! Click SHUFFLE to begin.")
    
    def show_instructions(self):
        messagebox.showinfo(
            "How to Play",
            "8-Puzzle Solver with Dual Visualization:\n\n"
            "LEFT SIDE: Shows the algorithm's exploration process\n"
            "RIGHT SIDE: Shows the final solution path"
        )

if __name__== "__main__":
    root = tk.Tk()
    app = EightPuzzleUI(root)
    root.mainloop()
