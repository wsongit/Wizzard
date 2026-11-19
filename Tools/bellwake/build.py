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
from pilgrim import FIELDS
from tide_engine import KEYS as engine_rooms
from underworks import rooms as chambers
from works_sets import make as make_works
work_keys = [r["key"] for r in chambers]

passage_keys = [region["key"] for region in REGIONS]

for room in args[1:] or ROOMS + passage_keys + work_keys + ["Runner", "Trails"]:
    if room == "Runner":
        make_avatar(Path(args[0]))
    elif room == "Trails":
        roadside(Path(args[0]))
    elif room in [field[0] for field in FIELDS]:
        from pilgrim_art import make as make_ward
        make_ward(next(i for i,f in enumerate(FIELDS) if f[0]==room), Path(args[0]))
    elif room=="DriftFen":
        from drift_fen_art import make as make_fen
        make_fen(Path(args[0]))
    elif room=="SwallowLock":
        from swallow_art import make as make_stair
        make_stair(Path(args[0]))
    elif room.startswith("Sillwater"):
        from sillwater_art import make as make_parish
        make_parish(room, Path(args[0]))
    elif room=="PaperCourt":
        from theatre_art import make as make_theatre
        make_theatre(Path(args[0]))
    elif room=="KettleYard":
        from kitchen_art import make as make_kitchen
        make_kitchen(Path(args[0]))
    elif room in engine_rooms:
        from engine_art import make as make_engine
        make_engine(engine_rooms.index(room),Path(args[0]))
    elif room == "Wrenfall":
        from wrenfall import make as make_headland
        make_headland(Path(args[0]))
    elif room in work_keys:
        make_works(work_keys.index(room),Path(args[0]))
    elif room in passage_keys:
        passage_set(passage_keys.index(room), Path(args[0]))
    else:
        make(room, Path(args[0]))
