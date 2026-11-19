"""Keep a timed playthrough's last earned chapter entry across browser restarts."""

import json
import time
from pathlib import Path


def write_json(path, value):
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(value, indent=2) + "\n")
    tmp.replace(path)


class RouteCheckpoint:
    def __init__(self, directory, resume):
        self.path = Path(directory) / "route-checkpoint.json"
        self.entry = None
        self.previous_seconds = 0
        self.started = time.monotonic()
        if resume:
            self.entry = json.loads(self.path.read_text())
            if self.entry["version"] != 1:
                raise ValueError("Unsupported timed-route checkpoint")
            self.previous_seconds = self.entry["elapsedSeconds"]
        elif self.path.exists():
            raise FileExistsError(f"Use --resume or choose a fresh result directory: {self.path}")

    @property
    def elapsed(self):
        return self.previous_seconds + time.monotonic() - self.started

    async def restore(self, page):
        if self.entry and self.entry["save"] is not None:
            await page.add_init_script(
                "if(!sessionStorage.routeRestored){"
                "localStorage.setItem('wizzard.bellwake.desktop.v1',"
                + json.dumps(self.entry["save"])
                + ");sessionStorage.routeRestored='1'}"
            )

    async def enter(self, stage, page):
        if self.entry:
            if self.entry["stage"] != stage:
                return False
            district = await page.evaluate("bellProbe().district")
            if district != self.entry["district"]:
                raise ValueError(f"Restored {district}, expected {self.entry['district']}")
            print(f"Resumed {stage} in {district}", flush=True)
            self.entry = None
        district, save = await page.evaluate(
            "[bellProbe().district, localStorage.getItem('wizzard.bellwake.desktop.v1')]"
        )
        if save is None and stage != "Market":
            raise ValueError(f"Missing earned save at {stage}")
        record = dict(version=1, stage=stage, district=district, save=save,
                      elapsedSeconds=round(self.elapsed, 3))
        write_json(self.path, record)
        print(f"Checkpoint {stage} in {district}", flush=True)
        return True
