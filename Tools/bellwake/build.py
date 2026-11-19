"""blender -b --python-exit-code 1 --python Tools/bellwake/build.py -- LIBRARY [ROOM]"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sets import make, ROOMS

args = sys.argv[sys.argv.index("--") + 1 :]
from avatar import make_avatar
from trails import roadside
from passage_sets import scene as passage_set
from passages import REGIONS
from underworks import rooms as chambers
from works_sets import make as make_works
work_keys = [r["key"] for r in chambers]

passage_keys = [region["key"] for region in REGIONS]

for room in args[1:] or ROOMS + passage_keys + work_keys + ["Runner", "Trails"]:
    if room == "Runner":
        make_avatar(Path(args[0]))
    elif room == "Trails":
        roadside(Path(args[0]))
    elif room in work_keys:
        make_works(work_keys.index(room),Path(args[0]))
    elif room in passage_keys:
        passage_set(passage_keys.index(room), Path(args[0]))
    else:
        make(room, Path(args[0]))
