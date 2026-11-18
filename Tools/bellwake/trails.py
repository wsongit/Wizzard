"""The optional meadow's climbable outcrops and the approach to Mossbell."""

from atelier import *
from sets import arch, lamp


def roadside(lib):
    init(lib, 310)
    rings = [(1.66, -0.48), (2.05, 0.32), (1.78, 1.26), (1.48, 2.07), (0.86, 2.64)]
    points = []
    for j, (radius, z) in enumerate(rings):
        for i in range(9):
            angle = (i + 0.13 * math.sin(j * 0.7)) * math.tau / 9
            r = radius * (1 + 0.16 * math.sin(i * 3.7) + 0.095 * math.cos(i * 2.3 + j * 0.4))
            points.append(
                (
                    r * math.cos(angle) + 0.17 * j,
                    r * 0.76 * math.sin(angle),
                    z + 0.15 * math.cos(i * 2 + 0.3 * j),
                )
            )
    faces = [tuple(reversed(range(9)))]
    for j in range(4):
        for i in range(9):
            a = j * 9 + i
            b = j * 9 + (i + 1) % 9
            faces.extend([(a, b, b + 9), (a, b + 9, a + 9)])
    faces.append(tuple(range(36, 45)))
    rock = geometry("Weathered meadow erratic", points, faces, "Mountain")
    rock.data.materials.append(mats["MossRock"])
    for f in rock.data.polygons:
        if f.normal.z > 0.64:
            f.material_index = 1
    finish("MeadowOutcrop")
    init(lib, 311)
    n = 30
    points = []
    for i in range(n + 1):
        a = math.radians(-65 + 310 * i / n)
        for r, z in [(46, -2), (46, 0), (27, 20 + 3 * math.sin(5 * a)), (15, 10), (15, -2)]:
            points.append((r * math.cos(a), r * math.sin(a), z))
    faces = []
    for i in range(n):
        for j in range(5):
            a = i * 5 + j
            b = i * 5 + (j + 1) % 5
            faces.extend([(a, a + 5, b), (b, a + 5, b + 5)])
    faces.extend([tuple(range(5)), tuple(reversed(range(n * 5, n * 5 + 5)))])
    geometry("Capped mountain cut", points, faces, "Mountain", "Escarpment")
    arch(0, -36, 0, 6.4, 7, "Masonry", "Wood")
    block("Village name board", (0, -36.45, 5.4), (4.7, 0.20, 0.83), "Wood")
    for x in [-2.18, 2.18]:
        shaft("Plaque nail", (x, -36.57, 5.4), (x, -36.61, 5.4), 0.07, 0.055, "Brass", 6)
    for sign in [-1, 1]:
        lamp(sign * 5.15, -36, 0)
    marker("GateAt", 0, -36, 0)
    marker("GateIn", 0, 0, 0)
    finish("MossbellApproach")
