"""blender -b --python-exit-code 1 --python Tools/bellwake/build.py -- LIBRARY [ROOM]"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sets import make, ROOMS

args = sys.argv[sys.argv.index("--") + 1 :]
from avatar import make_avatar
from trails import roadside

for room in args[1:] or ROOMS + ["Runner", "Trails"]:
    if room == "Runner":
        make_avatar(Path(args[0]))
    elif room == "Trails":
        roadside(Path(args[0]))
    else:
        make(room, Path(args[0]))
