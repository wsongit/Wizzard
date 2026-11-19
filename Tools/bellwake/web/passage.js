const bearings = ["North", "East", "South", "West"];
export class Passage {
  constructor(atlas, old, room, ending) {
    this.atlas = atlas;
    this.progress = { active: false, completed: room, sheet: 0, position: 0, logs: 0, ...old };
    const p = this.progress;
    for (const k of ["completed", "sheet", "position", "logs"])
      if (!Number.isInteger(p[k]) || p[k] < 0) p[k] = 0;
    p.completed = Math.min(atlas.length, Math.max(room, p.completed));
    p.active = !!p.active && room === p.completed && room < atlas.length && !ending;
    p.logs &= 7;
  }
  get region() {
    return this.atlas[this.progress.completed];
  }
  get active() {
    return this.progress.active;
  }
  get page() {
    return Math.min(this.progress.sheet, this.region.charts.length - 1);
  }
  get done() {
    return this.progress.sheet === this.region.charts.length;
  }
  get piece() {
    return this.book.boards[this.page].states[this.progress.position];
  }
  get surveyed() {
    return !!(this.progress.logs & (1 << Math.floor(this.page / 3)));
  }
  bind(book) {
    this.book = book;
    if (this.progress.sheet > this.region.charts.length) this.progress.sheet = 0;
    if (!this.piece) this.progress.position = 0;
  }
  leave() {
    this.progress = { active: false, completed: this.progress.completed + 1, sheet: 0, position: 0, logs: 0 };
    this.book = null;
  }
  objective() {
    if (this.done) return "The passage is open. Take the northern arch.";
    if (!this.surveyed)
      return "Find the witness post at " + this.region.sites[Math.floor(this.page / 3)] + ".";
    if (this.piece.win) return "Seal the chart at the stamping desk.";
    return (
      this.page +
      1 +
      "/" +
      this.region.charts.length +
      "  ·  " +
      this.region.charts[this.page] +
      "  ·  " +
      this.region.rule
    );
  }
  label(id) {
    if (id.startsWith("A_Key")) return bearings[+id.at(-1)];
    if (id.startsWith("A_Log")) return this.region.sites[+id.at(-1)];
    return {
      A_Talk: this.region.guide,
      A_Stamp: "Stamp the dispatch",
      A_Hint: "Navigator’s notes",
      A_Reset: "Rewind chart",
      A_Gate: "Way arch",
    }[id];
  }
  use(id) {
    const p = this.progress,
      r = this.region;
    this.travel = null;
    if (id.startsWith("A_Log")) {
      const i = +id.at(-1);
      p.logs |= 1 << i;
      return r.testimony[i];
    }
    if (id === "A_Talk") return this.done ? r.ending : p.logs === 0 ? r.intro : r.rule;
    if (this.done) return r.ending;
    if (id === "A_Gate" || !this.surveyed) return this.objective();
    if (id === "A_Stamp") {
      if (!this.piece.win) return "The seal stays cold. " + this.objective();
      p.sheet++;
      if (this.done) return r.ending;
      p.position = 0;
      return "Dispatch sealed. " + this.objective();
    }
    if (id === "A_Hint")
      return this.piece.win
        ? this.objective()
        : this.piece.hint < 0
          ? "This cart is wedged. Use the rewind lever."
          : "From here, steer " + bearings[this.piece.hint] + ". " + r.rule;
    if (id === "A_Reset") {
      p.position = 0;
      return "This chart is back at its starting mark.";
    }
    if (!id.startsWith("A_Key") || this.piece.win) return this.objective();
    const d = +id.at(-1),
      next = this.piece.move[d];
    if (next === p.position) return "The way is blocked.";
    this.travel =
      this.piece.paths?.[d] ?? String.fromCharCode(65 + this.book.boards[this.page].states[next].p);
    p.position = next;
    return this.piece.win
      ? "The arrival ring answers. Stamp this dispatch."
      : r.charts[this.page] + "  ·  " + bearings[d];
  }
}
