import numpy as np
from vispy import scene, app
from vispy.scene.visuals import Box

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

COLORS = {
    "R": (1, 0, 0, 1),
    "O": (1, 0.5, 0, 1),
    "Y": (1, 1, 0, 1),
    "W": (1, 1, 1, 1),
    "B": (0, 0, 1, 1),
    "G": (0, 1, 0, 1),
    "K": (0.2, 0.2, 0.2, 1)  # internal faces (transparent)
}

def expand_face_colors(face_colors):
    """
    Each face = 2 triangles, turn triangles into squares
    """
    expanded = []
    for c in face_colors:
        expanded.append(c)
        expanded.append(c)
    return expanded

def create_cubelet(x, y, z):
    """
    Create one cubelet at position (x, y, z)
    """

    # Default all faces to internal color
    faces = [COLORS["K"]] * 6

    # Assign sticker colors only on outer faces
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

    # Position cubelet
    cube.transform = scene.transforms.STTransform(
        translate=(x * STEP, y * STEP, z * STEP)
    )

    view.add(cube)
    return cube

# Build the 2x2x2 Cube
cubelets = []

for x in range(2):
    for y in range(2):
        for z in range(2):
            cubelets.append(create_cubelet(x, y, z))

# Center the Entire Cube
offset = STEP / 2
for cube in cubelets:
    cube.transform.translate -= (offset, offset, offset, 0)


if __name__ == "__main__":
    canvas.app.run()
