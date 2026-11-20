"""Costume, trade, posture and painted expression by character."""

from collections import namedtuple

# Kits share one sheet across a crowd. Width and stance specify the actor's silhouette.
Dress = namedtuple("Dress", "kit head garment tool build lean")
COSTUMES = {
    "Ada": Dress(3, "scarf", "mantle", "log", 1.05, -0.035),
    "Ara": Dress(2, "knot", "apron", "rule", 1.04, 0.02),
    "Bess": Dress(1, "crop", "vest", "rule", 1.16, -0.02),
    "Brannic": Dress(5, "brim", "apron", "hammer", 1.23, 0.015),
    "Eda": Dress(6, "scarf", "skirt", "linen", 0.99, -0.02),
    "Elin": Dress(4, "braid", "doublet", "log", 0.91, 0.015),
    "Fen": Dress(3, "brim", "oilskin", "key", 1.16, -0.025),
    "Fenel": Dress(5, "hood", "oilskin", "plumb", 1.15, -0.015),
    "Ina": Dress(2, "braid", "mantle", "log", 0.87, 0.01),
    "Iona": Dress(5, "scarf", "apron", "ladle", 1.18, -0.03),
    "Issa": Dress(4, "brim", "longcoat", "seal", 0.98, -0.018),
    "Ivo": Dress(0, "crop", "vest", "winder", 0.79, 0.025),
    "Jass": Dress(4, "peak", "apron", "rule", 0.94, 0.01),
    "Jori": Dress(2, "cap", "smock", "tile", 1.14, -0.03),
    "Mara": Dress(1, "braid", "apron", "sprig", 0.90, 0.03),
    "Marn": Dress(5, "brim", "oilskin", "plumb", 1.09, -0.02),
    "Mirren": Dress(0, "peak", "mantle", "log", 0.94, -0.01),
    "Nan": Dress(7, "knot", "apron", "linen", 1.19, -0.022),
    "Nell": Dress(3, "cap", "vest", "hook", 1.08, 0.025),
    "Nema": Dress(4, "scarf", "longcoat", "log", 1.05, -0.02),
    "Oli": Dress(7, "cap", "doublet", "lantern", 0.88, 0.03),
    "Orrel": Dress(6, "hood", "mantle", "seal", 1.02, -0.024),
    "Ossa": Dress(2, "knot", "apron", "hammer", 1.06, 0.015),
    "Rime": Dress(0, "hood", "mantle", "plumb", 1.19, -0.03),
    "Senn": Dress(5, "peak", "longcoat", "log", 0.92, 0.022),
    "Tern": Dress(6, "peak", "mantle", "sprig", 1.03, -0.02),
    "Wen": Dress(4, "crop", "doublet", "winder", 0.94, 0.016),
    "Willa": Dress(1, "scarf", "oilskin", "hook", 1.03, -0.016),
    "Registrar": Dress(6, "cap", "longcoat", "seal", 0.89, -0.012),
    "Hale": Dress(0, "brim", "oilskin", "hook", 1.17, 0.018),
    "Perrin": Dress(1, "crop", "vest", "winder", 0.86, -0.018),
    "Cobb": Dress(2, "cap", "smock", "plumb", 1.13, 0.025),
    "Linn": Dress(6, "scarf", "skirt", "log", 1.11, -0.015),
    "Lin": Dress(3, "knot", "longcoat", "log", 0.87, 0.014),
    "Sorrel": Dress(4, "scarf", "vest", "linen", 0.97, -0.026),
    "Fin": Dress(5, "braid", "doublet", "rule", 0.93, 0.012),
    "Orin": Dress(6, "brim", "oilskin", "key", 1.18, -0.034),
}
CREW = ("Hale", "Perrin", "Cobb", "Lin", "Sorrel", "Fin", "Orin")

# Front cheek and jaw widths, nose projection, brow tilt, eye opening and character marks.
Face = namedtuple("Face", "cheek jaw nose brow lid mark")
FACES = {
    "Ada": Face(0.152, 0.117, 0.205, -1, 2, "freckles"),
    "Ara": Face(0.164, 0.112, 0.204, 2, 0, "soot"),
    "Bess": Face(0.166, 0.134, 0.213, -2, 1, "scar"),
    "Brannic": Face(0.177, 0.144, 0.222, 1, 2, "forkbeard"),
    "Eda": Face(0.145, 0.108, 0.207, -2, 3, "age"),
    "Elin": Face(0.144, 0.085, 0.187, 1, 0, "mole"),
    "Fen": Face(0.163, 0.123, 0.224, 0, 2, "whiskers"),
    "Fenel": Face(0.157, 0.116, 0.209, 2, 2, "stubble"),
    "Ina": Face(0.142, 0.083, 0.183, -1, 0, "freckles"),
    "Iona": Face(0.179, 0.122, 0.197, -2, 1, "smile"),
    "Issa": Face(0.143, 0.095, 0.221, 2, 2, "age"),
    "Ivo": Face(0.153, 0.079, 0.177, -2, -1, "freckles"),
    "Jass": Face(0.148, 0.095, 0.201, 2, 0, "mole"),
    "Jori": Face(0.163, 0.126, 0.205, -1, 1, "jawbeard"),
    "Mara": Face(0.150, 0.095, 0.190, -2, 0, "freckles"),
    "Marn": Face(0.162, 0.135, 0.225, 2, 2, "whiskers"),
    "Mirren": Face(0.153, 0.115, 0.22, 1, 2, "age"),
    "Nan": Face(0.175, 0.116, 0.201, -3, 2, "smile"),
    "Nell": Face(0.152, 0.119, 0.200, 1, 0, "scar"),
    "Nema": Face(0.163, 0.115, 0.211, -2, 3, "age"),
    "Oli": Face(0.146, 0.083, 0.186, 0, -1, "mole"),
    "Orrel": Face(0.148, 0.102, 0.226, 3, 2, "forkbeard"),
    "Ossa": Face(0.159, 0.106, 0.201, 2, 1, "soot"),
    "Rime": Face(0.166, 0.129, 0.215, -1, 2, "forkbeard"),
    "Senn": Face(0.143, 0.103, 0.216, 1, 1, "whiskers"),
    "Tern": Face(0.155, 0.12, 0.223, -1, 3, "jawbeard"),
    "Wen": Face(0.146, 0.085, 0.192, -1, 0, "smile"),
    "Willa": Face(0.164, 0.120, 0.209, 2, 1, "scar"),
    "Registrar": Face(0.144, 0.10, 0.221, 3, 2, "age"),
    "Hale": Face(0.169, 0.131, 0.218, 1, 2, "jawbeard"),
    "Perrin": Face(0.144, 0.086, 0.181, -1, 0, "freckles"),
    "Cobb": Face(0.173, 0.138, 0.22, 2, 1, "stubble"),
    "Lin": Face(0.144, 0.089, 0.193, -1, 1, "mole"),
    "Sorrel": Face(0.157, 0.100, 0.198, -2, 0, "smile"),
    "Fin": Face(0.146, 0.103, 0.20, 1, 1, "stubble"),
    "Orin": Face(0.161, 0.118, 0.227, 0, 3, "whiskers"),
    "Linn": Face(0.160, 0.106, 0.21, -2, 2, "age"),
}


def face_patch(name):
    i = tuple(FACES).index(name)
    if i < 8:
        return (i % 4) * 64, (i // 4) * 64
    return 256 + (i - 8) % 4 * 64, (i - 8) // 4 * 64
