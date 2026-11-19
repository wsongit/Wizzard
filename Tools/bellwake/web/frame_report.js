// A bounded history for on-headset checks. Each visited room and refresh rate
// gets its last 360 animation-frame intervals, plus lifetime totals for that visit set.
export class HeadsetFrameReport {
  constructor() {
    this.rooms = new Map();
    this.previous = null;
    this.travel = null;
    this.current = null;
    this.session = null;
    this.tail = null;
  }

  room(name, hz) {
    if (this.current?.name === name && this.current.hz === hz) return this.current;
    const key = name + "/" + hz;
    if (!this.rooms.has(key)) this.rooms.set(key, {
      name, hz, intervals: new Float32Array(360), cursor: 0, total: 0, slow: 0, worst: 0,
      geometries: 0, textures: 0, loads: 0, travelMs: 0, worstLoad: 0, worstTravelInterval: 0,
    });
    this.current = this.rooms.get(key);
    return this.current;
  }

  beginTravel(session, now) {
    this.travel = session ? {session, start: now, previous: this.previous, worst: 0} : null;
    this.previous = null;
  }

  endTravel(session, name, now) {
    if (session && this.travel?.session === session) {
      const row = this.room(name, session.frameRate || null);
      const elapsed = now - this.travel.start;
      row.loads++;
      row.travelMs += elapsed;
      row.worstLoad = Math.max(row.worstLoad, elapsed);
      row.worstTravelInterval = Math.max(row.worstTravelInterval, this.travel.worst);
      this.tail = {session, row, previous: this.travel.previous};
    }
    this.travel = null;
    this.previous = null;
  }

  frame(session, time, playing, name, memory) {
    if (this.session !== session) {
      this.previous = null;
      this.session = session;
    }
    if (this.tail) {
      if (session && session === this.tail.session && session.visibilityState === "visible" && this.tail.previous !== null)
        this.tail.row.worstTravelInterval = Math.max(this.tail.row.worstTravelInterval, time - this.tail.previous);
      this.tail = null;
    }
    if (!session || session.visibilityState !== "visible") {
      this.previous = null;
      if (this.travel) this.travel.previous = null;
      return;
    }
    if (this.travel) {
      if (this.travel.previous !== null)
        this.travel.worst = Math.max(this.travel.worst, time - this.travel.previous);
      this.travel.previous = time;
    }
    if (!playing) { this.previous = null; return; }
    const row = this.room(name, session.frameRate || null);
    const interval = this.previous === null ? 0 : time - this.previous;
    this.previous = time;
    if (interval <= 0) return;
    row.intervals[row.cursor] = interval;
    row.cursor = (row.cursor + 1) % row.intervals.length;
    row.total++;
    row.worst = Math.max(row.worst, interval);
    if (row.hz && interval > 1500 / row.hz) row.slow++;
    row.geometries = Math.max(row.geometries, memory.geometries);
    row.textures = Math.max(row.textures, memory.textures);
  }

  summary() {
    const ms = value => Math.round(value * 10) / 10;
    return {
      clock: "WebXR animation-frame timestamps. Journal, hidden sessions and transitions are excluded from play intervals.",
      rooms: Array.from(this.rooms.values(), r => {
        const recent = r.intervals.slice(0, Math.min(r.total, r.intervals.length)).sort();
        const percentile = p => recent.length ? ms(recent[Math.ceil(recent.length * p) - 1]) : null;
        return {room: r.name, reportedRefreshHz: r.hz, gameplayFrames: r.total, recentFrames: recent.length,
          recentMedianMs: percentile(.5), recentP95Ms: percentile(.95), worstGameplayMs: ms(r.worst),
          framesOverOneAndAHalfRefreshIntervals: r.hz ? r.slow : null,
          maxRendererGeometries: r.geometries, maxRendererTextures: r.textures,
          loads: r.loads, meanLoadMs: r.loads ? ms(r.travelMs / r.loads) : null, maxLoadMs: ms(r.worstLoad),
          worstTransitionFrameMs: ms(r.worstTravelInterval)};
      }),
    };
  }
}
