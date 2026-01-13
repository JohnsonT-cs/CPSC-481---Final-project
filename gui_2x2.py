import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import sys

import AlgorithmComparison as AC


# ----------------------------
# Visual mapping for stickers
# ----------------------------
COLOR_MAP = {
    "R": "#d32f2f",  # red
    "O": "#fb8c00",  # orange
    "Y": "#fdd835",  # yellow
    "W": "#ffffff",  # white
    "B": "#1976d2",  # blue
    "G": "#388e3c",  # green
}

# 2x2 face slices in your state order:
# Front(0-3), Back(4-7), Up(8-11), Down(12-15), Left(16-19), Right(20-23)
FACE_IDX = {
    "F": (0, 4),
    "B": (4, 8),
    "U": (8, 12),
    "D": (12, 16),
    "L": (16, 20),
    "R": (20, 24),
}


class CubeGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("2x2 Rubik's Cube Solver (A* / BFS / IDS)")
        self.geometry("980x560")
        self.resizable(False, False)

        # State
        self.current_state = AC.Goal_State
        self.scramble_moves = []
        self.solution_moves = []
        self.animating = False
        self.anim_index = 0

        # UI
        self._build_layout()
        self._draw_cube(self.current_state)
        self._set_status("Ready. Click Scramble.")

    # ----------------------------
    # UI Layout
    # ----------------------------
    def _build_layout(self):
        root = ttk.Frame(self, padding=12)
        root.pack(fill="both", expand=True)

        # Left: Cube canvas
        left = ttk.Frame(root)
        left.grid(row=0, column=0, sticky="n")

        ttk.Label(left, text="Cube View (2×2 faces)", font=("Segoe UI", 12, "bold")).pack(anchor="w")

        self.canvas = tk.Canvas(left, width=440, height=420, bg="#f4f4f4", highlightthickness=1, highlightbackground="#cccccc")
        self.canvas.pack(pady=10)

        # Right: Controls + output
        right = ttk.Frame(root)
        right.grid(row=0, column=1, sticky="nw", padx=(18, 0))

        # Scramble controls
        scramble_box = ttk.LabelFrame(right, text="Scramble", padding=10)
        scramble_box.pack(fill="x")

        ttk.Label(scramble_box, text="n_moves:").grid(row=0, column=0, sticky="w")
        self.scramble_var = tk.IntVar(value=5)
        self.scramble_spin = ttk.Spinbox(scramble_box, from_=0, to=14, width=6, textvariable=self.scramble_var)
        self.scramble_spin.grid(row=0, column=1, sticky="w", padx=(6, 12))

        self.scramble_btn = ttk.Button(scramble_box, text="Scramble", command=self.scramble)
        self.scramble_btn.grid(row=0, column=2, sticky="w")

        self.reset_btn = ttk.Button(scramble_box, text="Reset to Solved", command=self.reset_cube)
        self.reset_btn.grid(row=0, column=3, sticky="w", padx=(8, 0))

        

        # Algorithm controls
        algo_box = ttk.LabelFrame(right, text="Solve", padding=10)
        algo_box.pack(fill="x", pady=(12, 0))

        ttk.Label(algo_box, text="Algorithm:").grid(row=0, column=0, sticky="w")
        self.algo_var = tk.StringVar(value="A*")
        self.algo_combo = ttk.Combobox(algo_box, width=10, textvariable=self.algo_var, state="readonly")
        self.algo_combo["values"] = ("A*", "BFS", "IDS")
        self.algo_combo.grid(row=0, column=1, sticky="w", padx=(6, 0))

        self.solve_btn = ttk.Button(algo_box, text="Run", command=self.solve)
        self.solve_btn.grid(row=0, column=2, sticky="w", padx=(12, 0))
        
        self.solver_btn = ttk.Button(algo_box, text="Run 3D Solver", command=self.open_3d_solver)
        self.solver_btn.grid(row=0, column=5, sticky="w", padx=(12, 0))

        # Animation controls
        anim_box = ttk.LabelFrame(right, text="Animation", padding=10)
        anim_box.pack(fill="x", pady=(12, 0))

        ttk.Label(anim_box, text="Step delay (ms):").grid(row=0, column=0, sticky="w")
        self.delay_var = tk.IntVar(value=350)
        self.delay_spin = ttk.Spinbox(anim_box, from_=50, to=2000, increment=50, width=8, textvariable=self.delay_var)
        self.delay_spin.grid(row=0, column=1, sticky="w", padx=(6, 0))

        self.play_btn = ttk.Button(anim_box, text="Play solution", command=self.play_solution)
        self.play_btn.grid(row=0, column=2, sticky="w", padx=(12, 0))

        self.step_btn = ttk.Button(anim_box, text="Step", command=self.step_once)
        self.step_btn.grid(row=0, column=3, sticky="w", padx=(8, 0))

        self.stop_btn = ttk.Button(anim_box, text="Stop", command=self.stop_animation)
        self.stop_btn.grid(row=0, column=4, sticky="w", padx=(8, 0))


        # Output: moves + metrics
        out_box = ttk.LabelFrame(right, text="Output", padding=10)
        out_box.pack(fill="both", expand=True, pady=(12, 0))

        self.metrics_label = ttk.Label(out_box, text="Moves: 0 | Runtime: 0.0000s", font=("Segoe UI", 10, "bold"))
        self.metrics_label.pack(anchor="w")

        ttk.Label(out_box, text="Move list:").pack(anchor="w", pady=(8, 0))
        self.moves_text = tk.Text(out_box, width=48, height=16, wrap="word")
        self.moves_text.pack(fill="both", expand=True, pady=(4, 0))

        # Status bar
        self.status = ttk.Label(self, text="", anchor="w", padding=(12, 6))
        self.status.pack(fill="x", side="bottom")

    # ----------------------------
    # Cube drawing
    # ----------------------------
    def _draw_face(self, face_vals, x0, y0, size=50, gap=4):
        # face_vals: length 4, 2x2 order [0,1;2,3]
        # Draw squares
        for i in range(4):
            r = i // 2
            c = i % 2
            x1 = x0 + c * (size + gap)
            y1 = y0 + r * (size + gap)
            x2 = x1 + size
            y2 = y1 + size
            color = COLOR_MAP.get(face_vals[i], "#999999")
            self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="#333333", width=1)

    def _draw_cube(self, state):
        self.canvas.delete("all")

        # Extract faces
        F = state[FACE_IDX["F"][0]:FACE_IDX["F"][1]]
        B = state[FACE_IDX["B"][0]:FACE_IDX["B"][1]]
        U = state[FACE_IDX["U"][0]:FACE_IDX["U"][1]]
        D = state[FACE_IDX["D"][0]:FACE_IDX["D"][1]]
        L = state[FACE_IDX["L"][0]:FACE_IDX["L"][1]]
        R = state[FACE_IDX["R"][0]:FACE_IDX["R"][1]]

        # Net layout (2x2 faces):
        #       U
        #   L   F   R   B
        #       D
        size = 50
        gap = 4

        # Coordinates (tuned for 440x420 canvas)
        Ux, Uy = 180, 40
        Lx, Ly = 60, 160
        Fx, Fy = 180, 160
        Rx, Ry = 300, 160
        Bx, By = 420, 160  

        # Shift all left so B fits canvas
        shift = 70
        Ux -= shift; Lx -= shift; Fx -= shift; Rx -= shift; Bx -= shift

        # Draw faces
        self._draw_face(U, Ux, Uy, size=size, gap=gap)
        self._draw_face(L, Lx, Ly, size=size, gap=gap)
        self._draw_face(F, Fx, Fy, size=size, gap=gap)
        self._draw_face(R, Rx, Ry, size=size, gap=gap)
        self._draw_face(B, Bx, By, size=size, gap=gap)
        self._draw_face(D, Fx, Fy + 120, size=size, gap=gap)

        # Labels
        self.canvas.create_text(Ux + 50, Uy - 14, text="U", font=("Segoe UI", 11, "bold"))
        self.canvas.create_text(Lx + 50, Ly - 14, text="L", font=("Segoe UI", 11, "bold"))
        self.canvas.create_text(Fx + 50, Fy - 14, text="F", font=("Segoe UI", 11, "bold"))
        self.canvas.create_text(Rx + 50, Ry - 14, text="R", font=("Segoe UI", 11, "bold"))
        self.canvas.create_text(Bx + 50, By - 14, text="B", font=("Segoe UI", 11, "bold"))
        self.canvas.create_text(Fx + 50, Fy + 106, text="D", font=("Segoe UI", 11, "bold"))

    # ----------------------------
    # Actions
    # ----------------------------
    def _set_status(self, msg):
        self.status.config(text=msg)

    def _set_moves_output(self, moves, runtime):
        self.metrics_label.config(text=f"Moves: {len(moves) if moves else 0} | Runtime: {runtime:.4f}s")
        self.moves_text.delete("1.0", "end")
        if moves:
            self.moves_text.insert("end", " ".join(moves))
        else:
            self.moves_text.insert("end", "(no moves)")

    def open_3d_solver(self):
        subprocess.Popen([sys.executable, "solver_animation.py"])

    def reset_cube(self):
        self.stop_animation()
        self.current_state = AC.Goal_State
        self.scramble_moves = []
        self.solution_moves = []
        self._draw_cube(self.current_state)
        self._set_moves_output([], 0.0)
        self._set_status("Reset to solved.")

    def scramble(self):
        self.stop_animation()
        n = int(self.scramble_var.get())
        self.current_state, self.scramble_moves = AC.random_scramble(n)
        self.solution_moves = []
        self._draw_cube(self.current_state)
        self._set_moves_output([], 0.0)
        self._set_status(f"Scrambled with {n} moves: {' '.join(self.scramble_moves)}")

    def solve(self):
        self.stop_animation()
        algo = self.algo_var.get()

        if self.current_state == AC.Goal_State:
            messagebox.showinfo("Already solved", "Cube is already solved. Scramble first if you want.")
            return

        self._set_status(f"Running {algo}...")

        if algo == "A*":
            moves, runtime = AC.Astar(self.current_state)
        elif algo == "BFS":
            moves, runtime = AC.BFS(self.current_state)
        elif algo == "IDS":
            moves, runtime = AC.IDS(self.current_state)
        else:
            messagebox.showerror("Error", "Unknown algorithm selected.")
            return

        if moves is None:
            self.solution_moves = []
            self._set_moves_output([], runtime if runtime else 0.0)
            self._set_status(f"{algo} did not find a solution.")
            return

        self.solution_moves = moves
        self._set_moves_output(moves, runtime)
        self._set_status(f"{algo} finished. Click Play solution to animate.")

    # ----------------------------
    # Animation
    # ----------------------------
    def play_solution(self):
        if not self.solution_moves:
            messagebox.showinfo("No solution", "Run an algorithm first to get a solution.")
            return
        if self.animating:
            return
        self.animating = True
        self.anim_index = 0
        self._set_status("Animating solution...")
        self._animate_step()

    def _animate_step(self):
        if not self.animating:
            return
        if self.anim_index >= len(self.solution_moves):
            self.animating = False
            self._set_status("Animation complete.")
            return

        mv = self.solution_moves[self.anim_index]
        self.current_state = AC.apply_move(self.current_state, mv)
        self._draw_cube(self.current_state)
        self.anim_index += 1
        self._set_status(f"Move {self.anim_index}/{len(self.solution_moves)}: {mv}")

        delay = int(self.delay_var.get())
        self.after(delay, self._animate_step)

    def step_once(self):
        if not self.solution_moves:
            messagebox.showinfo("No solution", "Run an algorithm first to get a solution.")
            return
        if self.anim_index >= len(self.solution_moves):
            self._set_status("No more moves to step.")
            return
        mv = self.solution_moves[self.anim_index]
        self.current_state = AC.apply_move(self.current_state, mv)
        self._draw_cube(self.current_state)
        self.anim_index += 1
        self._set_status(f"Step {self.anim_index}/{len(self.solution_moves)}: {mv}")

    def stop_animation(self):
        self.animating = False


if __name__ == "__main__":
    app = CubeGUI()
    app.mainloop()
