import numpy as np
from vispy import scene, app
from vispy.app import Timer
from vispy.scene.visuals import Box
from vispy.visuals.transforms import MatrixTransform

# App & Canvas
app.use_app('pyqt6')

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

ANIMATION_STEPS = 30
ANGLE_STEP = 90 / ANIMATION_STEPS

COLORS = {
    "R": (1, 0, 0, 1),
    "O": (1, 0.5, 0, 1),
    "Y": (1, 1, 0, 1),
    "W": (1, 1, 1, 1),
    "B": (0, 0, 1, 1),
    "G": (0, 1, 0, 1),
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

    if z == 0: faces[0] = COLORS["G"]
    if z == 1: faces[1] = COLORS["B"]
    if y == 0: faces[2] = COLORS["Y"]
    if y == 1: faces[3] = COLORS["W"]
    if x == 0: faces[4] = COLORS["R"]
    if x == 1: faces[5] = COLORS["O"]

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

# Rotation Logic
def rotate_layer(axis, layer, cw=True):
    global rotating, current_step
    global rotation_cubelets, rotation_axis, clockwise, timer

    if rotating:
        return

    rotating = True
    current_step = 0
    rotation_axis = axis
    clockwise = cw

    rotation_cubelets = [
        c for c in cubelets if c["pos"][axis] == layer
    ]

    pivot = np.array([0.5, 0.5, 0.5]) * STEP - offset

    direction = -1 if cw else 1
    angle = direction * ANGLE_STEP

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

        if current_step >= ANIMATION_STEPS:
            timer.stop()
            finalize_positions(axis, layer, cw)
            rotating = False

    timer = Timer(0.016, connect=update)
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
    if event.key == 'R':
        rotate_layer(axis=0, layer=1, cw=True)
    if event.key == 'U':
        rotate_layer(axis=1, layer=1, cw=True)
    if event.key == 'F':
        rotate_layer(axis=2, layer=1, cw=True)
    if event.key == 'L':
        rotate_layer(axis=0, layer=0, cw=True)
    if event.key == 'D':
        rotate_layer(axis=1, layer=0, cw=True)
    if event.key == 'B':
        rotate_layer(axis=2, layer=0, cw=True)

if __name__ == "__main__":
    canvas.app.run()
