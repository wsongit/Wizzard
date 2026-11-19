"""The field's survey grid is in metres. Roads follow gently warped survey lines."""
import math

EAST = tuple(range(-540, 541, 180))
NORTH = tuple(range(-425, 426, 170))
MEADOW = (0, -510)
HALF_WIDTH, HALF_DEPTH = 720, 600

def chart(u, v):
    return (u + 23 * math.sin(v / 98) + 11 * math.sin((u + v) / 177),
            v + 19 * math.sin(u / 115) + 9 * math.sin((u - v) / 130))

def height(x, y):
    return (22 + 11 * math.sin(x / 149) * math.cos(y / 176)
            + 5.6 * math.sin((x + y) / 82) + 2 * math.cos(y / 46)
            + 22 * math.exp(-((x - 160)**2 + (y - 280)**2) / 27000))

def lattice(limit, lines):
    values = set(range(-limit, limit + 1, 12)) | {-limit, limit}
    for line in lines:
        values.update((line - 2.4, line, line + 2.4))
    return sorted(values)
