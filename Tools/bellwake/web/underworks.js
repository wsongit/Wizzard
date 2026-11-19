export class Underworks {
  constructor(plan, data, eligible) {
    this.plan = plan;
    const saved = data || {};
    this.progress = {
      active: !!saved.active && eligible,
      chamber: Number.isInteger(saved.chamber) && plan.rooms[saved.chamber] ? saved.chamber : 0,
      badges: (saved.badges | 0) & ((1 << plan.flags.length) - 1),
      machines: plan.machines.map((m, i) =>
        Number.isInteger(saved.machines?.[i]) && m.rows[saved.machines[i]] ? saved.machines[i] : 0,
      ),
    };
    this.refresh();
  }
  get room() {
    return this.plan.rooms[this.progress.chamber];
  }
  get active() {
    return this.progress.active;
  }
  refresh() {
    const p = this.progress;
    this.signals = {};
    this.plan.flags.forEach((s, i) => (this.signals[s] = (p.badges >> i) & 1));
    this.plan.machines.forEach((m, i) =>
      m.channels.forEach((s, j) => (this.signals[s] = m.rows[p.machines[i]].values[j])),
    );
  }
  station(id) {
    return this.room.stations.find((s) => s.id === id);
  }
  register() {
    const s = this.signals;
    if (s.named) return "Ina is on the night roll. Her nameplate will be waiting at the market.";
    if (s.token) return "Carry Ossa’s nameplate back to Nema in the cistern.";
    if (!s.petition) return "Nema keeps the night roll at the cistern entrance.";
    return (
      "Fen’s knot " +
      s.knot +
      "/1. Orrel’s pay leaf " +
      s.blank +
      "/1. Brannic’s spare wage " +
      s.wage +
      "/1. Take the three proofs to Ossa."
    );
  }
  objective() {
    if (this.progress.chamber !== 0 || !this.signals.admitted) return this.room.intro;
    const s = this.signals;
    if (s.reed && s.yoke && s.glass)
      return "All three witnesses are present. Take the northeastern resonator lift.";
    return (
      "Find the trades’ witnesses. River reed " +
      s.reed +
      "/1, bronze yoke " +
      s.yoke +
      "/1, nightglass " +
      s.glass +
      "/1."
    );
  }
  use(id) {
    const station = this.station(id);
    const r = station?.rules.find((rule) => rule.when.every((c) => this.signals[c.signal] === c.value));
    if (!r) return { line: this.objective(), to: "" };
    const p = this.progress;
    if (r.award) p.badges |= 1 << this.plan.flags.indexOf(r.award);
    if (r.move) {
      const [key, op] = r.move.split("."),
        i = this.plan.machines.findIndex((m) => m.key === key),
        m = this.plan.machines[i];
      p.machines[i] = m.rows[p.machines[i]].moves[m.controls.indexOf(op)];
    }
    this.refresh();
    if (r.to && r.to !== "@final") p.chamber = this.plan.rooms.findIndex((room) => room.key === r.to);
    return { to: r.to, line: r.line.replace(/\{(\w+)\}/g, (_, k) => this.signals[k]) };
  }
}
