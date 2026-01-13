import heapq
import random
import time

# Cube Definition
# 2x2x2 cube: 6 faces, 24 stickers
# W: White, Y: Yellow, G: Green, B: Blue, O: Orange, R: Red

# ----- Moves Definition -----
# [FR] Front Right (Clockwise) 
# [LD] Left side Down 
# [RU] Right side Up
# [UL] Upper layer Left 
# [DR] Down layer Right

# --------- Inverse ---------
# [FL] Front Left (Counter-Clockwise)
# [LU] Left side Up
# [RD] Right side Down
# [UR] Upper layer Right
# [DL] Down layer Left

# Length = 24
Goal_State = (
    'R','R','R','R',  # Front
    'O','O','O','O',  # Back
    'Y','Y','Y','Y',  # Up
    'W','W','W','W',  # Down
    'B','B','B','B',  # Left
    'G','G','G','G'   # Right
)

# Original: (0,1,2,3, 4,5,6,7, 8,9,10,11, 12,13,14,15, 16,17,18,19, 20,21,22,23)
Moves = {
    "FR": (2,0,3,1, 4,5,6,7, 8,9,17,19, 20,22,14,15, 16,12,18,13, 10,21,11,23),
    "LD": (8,1,10,3, 12,5,14,7, 4,9,6,11, 0,13,2,15, 18,16,19,17, 20,21,22,23),
    "RU": (0,13,2,15, 4,9,6,11, 8,1,10,3, 12,5,14,7, 16,17,18,19, 22,20,23,21),
    "UL": (20,21,2,3, 16,17,6,7, 10,8,11,9, 12,13,14,15, 0,1,18,19, 4,5,22,23),
    "DR": (0,1,18,19, 4,5,22,23, 8,9,10,11, 14,12,15,13, 16,17,6,7, 20,21,2,3),

    # Inverse
    "FL": (1,3,0,2, 4,5,6,7, 8,9,20,22, 17,19,14,15, 16,10,18,11, 12,21,13,23),
    "LU": (12,1,14,3, 8,5,10,7, 0,9,2,11, 4,13,6,15, 17,19,16,18, 20,21,22,23),
    "RD": (0,9,2,11, 4,13,6,15, 8,5,10,7, 12,1,14,3, 16,17,18,19, 21,23,20,22),
    "UR": (16,17,2,3, 20,21,6,7, 9,11,8,10, 12,13,14,15, 4,5,18,19, 0,1,22,23),
    "DL": (0,1,22,23, 4,5,18,19, 8,9,10,11, 13,15,12,14, 16,17,2,3, 20,21,6,7)
}

# Functions
def apply_move(state, move):
    # Apply a move and return the new cube state
    mapping = Moves[move]
    return tuple(state[i] for i in mapping)

def heuristic(state):
    # Count the number of misplaced stickers
    return sum(1 for i in range(len(state)) if state[i] != Goal_State[i])

inverse_map = {
    "FR":"FL", "FL":"FR",
    "LD":"LU", "LU":"LD",
    "RU":"RD", "RD":"RU",
    "UL":"UR", "UR":"UL",
    "DR":"DL", "DL":"DR"
}

def Astar(start):
    # A* search to solve the cube
    start_time = time.time()
    frontier = []
    heapq.heappush(frontier, (heuristic(start), 0, start, [], None))  # last_move = None
    visited = set()

    while frontier:
        f, g, state, path, last_move = heapq.heappop(frontier)

        if state == Goal_State:
            return path, time.time() - start_time

        if state in visited:
            continue

        visited.add(state)

        for move in Moves:
            # Skips the inverse of last move
            if last_move and move == inverse_map.get(last_move):
                continue

            next_state = apply_move(state, move)
            if next_state not in visited:
                heapq.heappush(
                    frontier,
                    (g + 1 + heuristic(next_state), g + 1, next_state, path + [move], move)
                )
    return None, None

def random_scramble(n_moves):
    # Scramble the cube with n random moves
    state = Goal_State
    moves = []
    move_keys = list(Moves.keys())

    for _ in range(n_moves):
        move = random.choice(move_keys)
        state = apply_move(state, move)
        moves.append(move)
    return state, moves

def display_cube(state):
    # Simple Display of The Cube
    print("Front: ", state[0:4])
    print("Back:  ", state[4:8])
    print("Up:    ", state[8:12])
    print("Down:  ", state[12:16])
    print("Left:  ", state[16:20])
    print("Right: ", state[20:24])

def show_solution_states(start_state, solution_moves):
    state = start_state

    for i, move in enumerate(solution_moves, 1):
        state = apply_move(state, move)
        print("-" * 30)
        print(f"Move {i}: {move}")
        display_cube(state)

# Main
if __name__ == "__main__":
    # Random scramble
    scrambled_state, scramble_moves = random_scramble(n_moves = 5)
    print("Scramble moves applied:", scramble_moves)
    print("-" * 30)
    print("Scrambled Cube:")
    display_cube(scrambled_state)
    print("-" * 30)

    # Solve with A*
    print("\nSolving the cube using A*...")
    solution, runtime = Astar(scrambled_state)

    if solution:
        print("Solution found!")
        print("Moves to solve:", solution)
        print("Number of moves:", len(solution))
        print("Runtime: {:.4f} seconds".format(runtime))

        # Show step-by-step states
        print("\nShowing solution states step-by-step:")
        show_solution_states(scrambled_state, solution)
        print("-" * 30)
        print()
    else:
        print("No solution found.\n")