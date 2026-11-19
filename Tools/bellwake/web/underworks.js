export class Underworks {
  constructor(plan, data, eligible) {
    this.plan = plan;
    const saved = data || {};
    this.progress = {
      active: !!saved.active && eligible,
      invited: !!saved.invited,
      returnTicket: !!saved.returnTicket,
      camp: typeof saved.camp === "string" ? saved.camp : "",
      chamber: Number.isInteger(saved.chamber) && plan.rooms[saved.chamber] ? saved.chamber : 0,
      badges: (saved.badges | 0) & ((1 << Math.min(30,plan.flags.length)) - 1),
      furtherBadges: Array.from({length: Math.max(0,Math.floor((plan.flags.length-1)/30))},(_,i)=>saved.furtherBadges?.[i] | 0),
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
  moveMachine(key, op) {
    const i=this.plan.machines.findIndex(m=>m.key===key), m=this.plan.machines[i];
    this.progress.machines[i]=m.rows[this.progress.machines[i]].moves[m.controls.indexOf(op)];
  }
  playMorningSong(control) {
    this.moveMachine("dawnwatch",control);
    this.refresh();
    return this.signals.dawnStep;
  }
  refresh() {
    const p = this.progress;
    this.signals = {};
    this.plan.flags.forEach((s,i)=>{
      const bits=i<30 ? p.badges : p.furtherBadges[Math.floor(i/30)-1];
      this.signals[s]=(bits >> (i%30)) & 1;
    });
    this.plan.machines.forEach((m, i) =>
      m.channels.forEach((s, j) => (this.signals[s] = m.rows[p.machines[i]].values[j])),
    );
  }
  station(id) {
    return this.room.stations.find((s) => s.id === id);
  }
  kitchenJournal() {
    return this.plan.supperNotes
      .filter((slip) => this.signals[slip.signal])
      .map((slip) => slip.title + "   ·   " + slip.notes).join("   /   ");
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
  nextGoal() {
    return this.room.goals?.find((g) => g.when.every((c) => this.signals[c.signal] === c.value));
  }
  guideTrail(cell) {
    if (!this.room.early || !this.signals.QuinceFoldKnife) return [];
    const trail = this.station(this.nextGoal()?.lead)?.trail;
    if (!trail) return [];
    const cells = [cell],
      steps = { N: 15, S: -15, E: 1, W: -1 };
    while (cells.length < 5 && trail[cell] !== ".") {
      cell += steps[trail[cell]];
      cells.push(cell);
    }
    return cells;
  }
  objective() {
    const s = this.signals;
    if (this.progress.returnTicket && this.room.key.startsWith("Sillwater") && !s.parishWarrant)
      return "Welcome to Sillwater. Open your field sheet and find Ada near the south bell. The northeast towpath takes your return ticket whenever you want to leave.";
    if (this.progress.returnTicket && this.room.key.startsWith("Sillwater") && s.parishSigned)
      return "Your signed title is in the witness book. Use your return ticket at the northeast towpath on either shore.";
    const goal = this.nextGoal();
    if (goal) {
      const line = this.format(goal.line);
      if (this.progress.returnTicket && this.room.key==="RowanHollow") return line+" The north wicket takes you back to Bellmarket whenever you want.";
      if (this.progress.returnTicket && this.room.key==="DriftFen") return line+" Your return boat is at Swallow Stair.";
      if (this.progress.returnTicket && this.room.key==="SwallowLock") return line+" The northeast towpath takes your return fare at any time.";
      return line;
    }
    if (this.room.key === "Wrenfall") {
      if (s.landed) return "The Linnet is at the north landing. Collect Elin’s flood book.";
      if (!s.charter) return this.room.intro;
      return (
        "Field chart   /   Chapel: " +
        (s.sounding ? "wing" : "unread") +
        "   ·   Split Stone: " +
        (s.leading ? "bell" : "unsighted") +
        "   ·   Lookout: " +
        (s.distress ? "star" : "unread") +
        ". Eastern mast: " +
        s.signalBar +
        " of 3 signals acknowledged."
      );
    }
    if (this.progress.chamber !== 0 || !this.signals.admitted) return this.room.intro;
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
  format(line) {
    return line.replace(/\{(\w+)\}/g, (_, key) => this.signals[key]);
  }
  takePacket(fen = false) {
    this.takeReturnWalk(fen?"DriftFen":"SillwaterEbb", fen?"RestGuide":"RestGate");
  }
  takeSchoolPath() {
    this.takeReturnWalk("RowanHollow","RestLinn");
  }
  takeReturnWalk(place, arrival) {
    this.progress.active = true;
    this.progress.returnTicket = true;
    this.progress.chamber = this.plan.rooms.findIndex(r => r.key === place);
    this.progress.camp = arrival;
  }
  use(id) {
    if (this.progress.returnTicket && (this.room.middle || this.room.key==="RowanHollow") && id === "A_Gate") {
      this.progress.returnTicket = false;
      this.progress.camp = "";
      return {to:this.room.key==="RowanHollow"?"@market":"@reedwater",line:""};
    }
    const station = this.station(id);
    const r = station?.rules.find((rule) => rule.when.every((c) => this.signals[c.signal] === c.value));
    if (!r) return { line: this.objective(), to: "" };
    const p = this.progress;
    if (r.award) {
      const index=this.plan.flags.indexOf(r.award), bit=1 << (index%30);
      if(index<30) p.badges|=bit;
      else p.furtherBadges[Math.floor(index/30)-1]|=bit;
    }
    if (r.move) {
      this.moveMachine(...r.move.split("."));
    }
    this.refresh();
    if (station.camp) p.camp = station.camp;
    if (r.to) {
      p.camp = r.to.startsWith("#") ? r.to.slice(1) : r.arrival || "";
      if (!r.to.startsWith("@") && !r.to.startsWith("#"))
        p.chamber = this.plan.rooms.findIndex((room) => room.key === r.to);
    }
    return { to: r.to, line: this.format(r.line) };
  }
}
