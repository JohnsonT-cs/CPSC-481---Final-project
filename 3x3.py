import heapq
import random
import time

# Cube Definition
# 3x3x3 cube: 6 faces, 54 stickers
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

# Length = 54
Goal_State = (
    'R','R','R','R','R','R','R','R','R',  # Front
    'O','O','O','O','O','O','O','O','O',  # Back
    'Y','Y','Y','Y','Y','Y','Y','Y','Y',  # Up
    'W','W','W','W','W','W','W','W','W',  # Down
    'B','B','B','B','B','B','B','B','B',  # Left
    'G','G','G','G','G','G','G','G','G',  # Right
)

# Original: (0,1,2,3,4,5,6,7,8, 9,10,11,12,13,14,15,16,17, 18,19,20,21,22,23,24,25,26, 27,28,29,30,31,32,33,34,35, 36,37,38,39,40,41,42,43,44, 45,46,47,48,49,50,51,52,53)
Moves = {
    "FR": (6,3,0,7,4,1,8,5,2, 9,10,11,12,13,14,15,16,17, 18,19,20,21,22,23,44,41,38, 51,48,45,30,31,32,33,34,35, 36,37,27,39,40,28,42,43,29, 24,46,47,25,49,50,26,52,53),
    "LD": (18,1,2,21,4,5,24,7,8, 9,10,33,12,13,30,15,16,27, 17,19,20,14,22,23,11,25,26, 0,28,29,3,31,32,6,34,35, 42,39,36,43,40,37,44,41,38, 45,46,47,48,49,50,51,52,53),
    "RU": (0,1,29,3,4,32,6,7,35, 26,10,11,23,13,14,20,16,17, 18,19,2,21,22,5,24,25,8, 27,28,15,30,31,12,33,34,9, 36,37,38,39,40,41,42,43,44, 51,48,45,52,49,46,53,50,47),
    "UL": (45,46,47,3,4,5,6,7,8, 36,37,38,12,13,14,15,16,17, 24,21,18,25,22,19,26,23,20, 27,28,29,30,31,32,33,34,35, 0,1,2,39,40,41,42,43,44, 9,10,11,48,49,50,51,52,53),
    "DR": (0,1,2,3,4,5,42,43,44, 9,10,11,12,13,14,51,52,53, 18,19,20,21,22,23,24,25,26, 33,30,27,34,31,28,35,32,29, 36,37,38,39,40,41,15,16,17, 45,46,47,48,49,50,6,7,8),

    # Inverse
    "FL": (2,5,8,1,4,7,0,3,9, 9,10,11,12,13,14,15,16,17, 18,19,20,21,22,23,45,48,51, 38,41,44,30,31,32,33,34,35, 36,37,26,39,40,25,42,43,24, 29,46,47,28,49,50,27,52,53),
    "LU": (27,1,2,30,4,5,33,7,8, 9,10,24,12,13,21,15,16,18, 0,19,20,3,22,23,6,25,26, 17,28,29,14,31,32,11,34,35, 38,41,44,37,40,43,36,39,42, 45,46,47,48,49,50,51,52,53),
    "RD": (0,1,20,3,4,23,6,7,26, 35,10,11,32,13,14,29,16,17, 18,19,15,21,22,12,24,25,9, 27,28,2,30,31,5,33,34,8, 36,37,38,39,40,41,42,43,44, 47,50,53,46,49,52,45,48,51),
    "UR": (36,37,38,3,4,5,6,7,8, 45,46,47,12,13,14,15,16,17, 20,23,26,19,22,25,18,21,24, 27,28,29,30,31,32,33,34,35, 9,10,11,39,40,41,42,43,44, 0,1,2,48,49,50,51,52,53),
    "DL": (0,1,2,3,4,5,51,52,53, 9,10,11,12,13,14,42,43,44, 18,19,20,21,22,23,24,25,26, 29,32,35,28,31,34,27,30,33, 36,37,38,39,40,41,6,7,8, 45,46,47,48,49,50,15,16,17)
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
    print("Front:", state[0:9])
    print("Back: ", state[9:18])
    print("Up:   ", state[18:27])
    print("Down: ", state[27:36])
    print("Left: ", state[36:45])
    print("Right:", state[45:54])

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
    scrambled_state, scramble_moves = random_scramble(n_moves = 2)
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