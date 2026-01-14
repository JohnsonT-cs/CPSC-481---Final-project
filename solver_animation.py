import numpy as np
from vispy import scene, app
from vispy.app import Timer
from vispy.scene.visuals import Box
from vispy.visuals.transforms import MatrixTransform
import tkinter as tk
import sys

import AlgorithmComparison as AC

# App & Canvas
app.use_app('pyqt6')

# Solution animation (slow, visible)
SOLVE_STEPS = 30
SOLVE_DURATION = 0.2

# Scramble animation (fast)
SCRAMBLE_STEPS = 6
SCRAMBLE_DURATION = 0.08


#cube_state = AC.Goal_State

MOVE_MAP = {
    "RU": ("R", True),
    "RD": ("R", False),

    "UL": ("U", True),
    "UR": ("U", False),

    "FR": ("F", True),
    "FL": ("F", False),

    "LU": ("L", True),
    "LD": ("L", False),

    "DR": ("D", True),
    "DL": ("D", False),

    "BR": ("B", True),
    "BL": ("B", False)
}

scrambling = True
scramble_moves = []
solve_moves = []
if len(sys.argv) > 1:
    scramble_moves = [MOVE_MAP[m] for m in sys.argv[1].split(',')]

if len(sys.argv) > 2:
    solve_moves = [MOVE_MAP[m] for m in sys.argv[2].split(',')]

moves = []

canvas = scene.SceneCanvas(
    keys='interactive',
    bgcolor=(0.1, 0.1, 0.1, 1),
    size=(900, 700),
    show=True
)

view = canvas.central_widget.add_view()
view.camera = scene.cameras.TurntableCamera(
    fov=45,
    distance=6,
    azimuth=45,
    elevation=30
)

# Cube Constants
CUBELET_SIZE = 0.95
GAP = 0.03
STEP = CUBELET_SIZE + GAP

ANIMATION_STEPS = 6
ANGLE_STEP = 90 / ANIMATION_STEPS

COLORS = {
    "R": (1, 0, 0, 1),
    "O": (1, 0.5, 0, 1),
    "Y": (1, 1, 0, 1),
    "W": (1, 1, 1, 1),
    "G": (0, 0, 1, 1),
    "B": (0, 1, 0, 1),
    "K": (0.2, 0.2, 0.2, 1)
}

# Helpers
def expand_face_colors(face_colors):
    expanded = []
    for c in face_colors:
        expanded.append(c)
        expanded.append(c)
    return expanded

# Cubelet Creation
def create_cubelet(x, y, z):
    faces = [COLORS["K"]] * 6

    if z == 0: faces[0] = COLORS["R"]
    if z == 1: faces[1] = COLORS["O"]
    if y == 0: faces[2] = COLORS["Y"]
    if y == 1: faces[3] = COLORS["W"]
    if x == 0: faces[4] = COLORS["G"]
    if x == 1: faces[5] = COLORS["B"]

    cube = Box(
        width=CUBELET_SIZE,
        height=CUBELET_SIZE,
        depth=CUBELET_SIZE,
        face_colors=expand_face_colors(faces),
        edge_color='black'
    )

    transform = MatrixTransform()
    transform.translate((x * STEP, y * STEP, z * STEP))
    cube.transform = transform
    view.add(cube)

    return {
        "visual": cube,
        "pos": np.array([x, y, z], dtype=int),
        "transform": transform
    }

# Build Cube
cubelets = []
for x in range(2):
    for y in range(2):
        for z in range(2):
            cubelets.append(create_cubelet(x, y, z))

# Center cube
offset = STEP / 2
for c in cubelets:
    c["transform"].translate((-offset, -offset, -offset))

# Animation State
rotating = False
current_step = 0
rotation_cubelets = []
rotation_axis = None
clockwise = True
timer = None

def start_rotation_sequence():
    global moves, scrambling
    moves = scramble_moves.copy()
    scrambling = True
    play_next_move()

def play_next_move():
    global scrambling
    
    if not moves:
        if scrambling:
            # switch to solve phase
            moves.extend(solve_moves)
            scrambling = False
        else:
            return

    face, cw = moves.pop(0)

    if face == 'R':
        rotate_layer(axis=0, layer=1, cw=cw, fast=scrambling)
    elif face == 'L':
        rotate_layer(axis=0, layer=0, cw=cw, fast=scrambling)
    elif face == 'U':
        rotate_layer(axis=1, layer=1, cw=cw, fast=scrambling)
    elif face == 'D':
        rotate_layer(axis=1, layer=0, cw=cw, fast=scrambling)
    elif face == 'F':
        rotate_layer(axis=2, layer=1, cw=cw, fast=scrambling)
    elif face == 'B':
        rotate_layer(axis=2, layer=0, cw=cw, fast=scrambling)

# Rotation Logic
def rotate_layer(axis, layer, cw=True, fast=False):
    global rotating, current_step
    global rotation_cubelets, rotation_axis, clockwise, timer

    if rotating:
        return

    # Pick speed
    if fast:
        steps = SCRAMBLE_STEPS
        duration = SCRAMBLE_DURATION
    else:
        steps = SOLVE_STEPS
        duration = SOLVE_DURATION

    angle_step = 90 / steps
    direction = -1 if cw else 1
    angle = direction * angle_step

    rotating = True
    current_step = 0
    rotation_axis = axis
    clockwise = cw

    rotation_cubelets = [
        c for c in cubelets if c["pos"][axis] == layer
    ]

    pivot = np.array([0.5, 0.5, 0.5]) * STEP - offset

    def update(event):
        global current_step, rotating

        for c in rotation_cubelets:
            t = c["transform"]
            t.translate(-pivot)

            if axis == 0:
                t.rotate(angle, (1, 0, 0))
            elif axis == 1:
                t.rotate(angle, (0, 1, 0))
            elif axis == 2:
                t.rotate(angle, (0, 0, 1))

            t.translate(pivot)

        current_step += 1

        if current_step >= steps:
            timer.stop()
            finalize_positions(axis, layer, cw)
            rotating = False
            play_next_move()

    timer = Timer(duration / steps, connect=update)
    timer.start()


# Snap Logical Positions
def finalize_positions(axis, layer, cw):
    for c in cubelets:
        if c["pos"][axis] != layer:
            continue

        x, y, z = c["pos"]

        

        if axis == 0:
            c["pos"] = np.array([
                x,
                z if cw else 1 - z,
                1 - y if cw else y
            ])

        elif axis == 1:
            c["pos"] = np.array([
                1 - z if cw else z,
                y,
                x if cw else 1 - x
            ])
        
        if axis == 2:
            c["pos"] = np.array([
                y if cw else 1 - y,
                1 - x if cw else x,
                z
            ])
        

# Manual rotations
@canvas.events.key_press.connect
def on_key(event):
    if event.key == 'R': # RU
        rotate_layer(axis=0, layer=1, cw=True)
    if event.key == 'U':
        rotate_layer(axis=1, layer=1, cw=True)
    if event.key == 'F': # UL
        rotate_layer(axis=2, layer=1, cw=True)
    if event.key == 'L': # LU
        rotate_layer(axis=0, layer=0, cw=True)
    if event.key == 'D': # FL
        rotate_layer(axis=1, layer=0, cw=True)
    if event.key == 'B': # DL
        rotate_layer(axis=2, layer=0, cw=True)


    if event.key == 'G': # LD
        rotate_layer(axis=0, layer=0, cw=False)
    if event.key == 'H': # FR
        rotate_layer(axis=1, layer=0, cw=False)
    if event.key == 'J': # DR
        rotate_layer(axis=2, layer=0, cw=False)
    if event.key == 'K': # RD
        rotate_layer(axis=0, layer=1, cw=False)
    if event.key == 'I': # UR
        rotate_layer(axis=2, layer=1, cw=False)
    
    if event.key == "T":
        global moves
        moves = test.copy()
        next_move = moves.pop(0)
        if next_move == 'R':
            rotate_layer(axis=0, layer=1, cw=True)
        elif next_move == 'U':
            rotate_layer(axis=1, layer=1, cw=True)
        elif next_move == 'F':
            rotate_layer(axis=2, layer=1, cw=True)
        elif next_move == 'L':
            rotate_layer(axis=0, layer=0, cw=True)
        elif next_move == 'D':
            rotate_layer(axis=1, layer=0, cw=True)
        elif next_move == 'B':
            rotate_layer(axis=2, layer=0, cw=True)
        elif event.key == 'G': # LD
            rotate_layer(axis=0, layer=0, cw=False)
        elif event.key == 'H': # FR
            rotate_layer(axis=1, layer=0, cw=False)
        elif event.key == 'J': # DR
            rotate_layer(axis=2, layer=0, cw=False)
        elif event.key == 'K': # RD
            rotate_layer(axis=0, layer=1, cw=False)
        elif event.key == 'I': # UR
            rotate_layer(axis=2, layer=1, cw=False)

        

if __name__ == "__main__":
    if scramble_moves:
        start_rotation_sequence()
    canvas.app.run()