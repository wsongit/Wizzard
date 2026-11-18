"""Author the bellrunner's jointed forearm and asymmetrical hands in Blender."""

from atelier import *


def ellipsoid(name, centre, radii, mat):
    cx, cy, cz = centre
    rx, ry, rz = radii
    n = 10
    pts = [(cx, cy, cz - rz)]
    for j in range(1, 6):
        a = -math.pi / 2 + j * math.pi / 6
        for i in range(n):
            b = math.tau * i / n
            pts.append(
                (
                    cx + rx * math.cos(a) * math.cos(b),
                    cy + ry * math.cos(a) * math.sin(b),
                    cz + rz * math.sin(a),
                )
            )
    pts.append((cx, cy, cz + rz))
    faces = [(0, 1 + (i + 1) % n, 1 + i) for i in range(n)]
    for j in range(4):
        for i in range(n):
            a = 1 + j * n + i
            b = 1 + j * n + (i + 1) % n
            faces.append((a, b, b + n, a + n))
    faces.extend((41 + i, 41 + (i + 1) % n, len(pts) - 1) for i in range(n))
    return geometry(name, pts, faces, mat)


def make_avatar(lib):
    for left in [True, False]:
        init(lib, 61)
        side = -1 if left else 1
        ellipsoid("Broad palm", (0, 0, 0.009), (0.084, 0.073, 0.050), "Skin")
        ellipsoid("Furred back", (0, -0.022, 0.038), (0.078, 0.066, 0.031), "Fur")
        for j in range(4):
            x = side * (0.055 - j * 0.036)
            y = 0.051 - j * 0.002
            length = [0.062, 0.072, 0.067, 0.052][j]
            a = (x, y, 0.010)
            b = (x + side * 0.005, y + length, 0.002)
            c = (x + side * 0.005, y + length + 0.017, -0.021)
            shaft("Proximal finger", a, b, 0.024, 0.020, "Skin", 8)
            shaft("Curled fingertip", b, c, 0.020, 0.017, "Skin", 8)
            ellipsoid("Finger pad", c, (0.017, 0.016, 0.017), "Skin")
        shaft(
            "Opposed thumb",
            (-side * 0.05, -0.026, 0),
            (-side * 0.095, 0.018, -0.014),
            0.034,
            0.027,
            "Skin",
            8,
        )
        ellipsoid("Thumb tip", (-side * 0.098, 0.029, -0.014), (0.027, 0.028, 0.022), "Skin")
        shaft("Wrist binding", (0, -0.059, 0.012), (0, -0.089, 0.014), 0.059, 0.055, "BellMetal", 10)
        ellipsoid("Stamped brass stud", (0, -0.074, 0.067), (0.020, 0.014, 0.008), "Brass")
        finish("LeftPalm" if left else "RightPalm")
    init(lib, 62)
    lathe(
        "Tapered forearm",
        0,
        0,
        -0.50,
        [
            (0.034, 0),
            (0.068, 0.07),
            (0.083, 0.29),
            (0.068, 0.50),
            (0.100, 0.72),
            (0.087, 0.90),
            (0.039, 1),
        ],
        "Fur",
        10,
    )
    lathe("Woven wristband", 0, 0, -0.453, [(0.061, 0), (0.067, 0.025), (0.070, 0.051)], "BellMetal", 10)
    finish("RunnerArm")
