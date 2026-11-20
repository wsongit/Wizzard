// Run with node Tools/bellwake/web/frame_report_check.mjs.
import assert from "node:assert/strict";
import { HeadsetFrameReport } from "./frame_report.js";

class Session extends EventTarget {
  visibilityState = "visible";
  frameRate = 72;
  visibility(state, time) {
    this.visibilityState = state;
    const event = new Event("visibilitychange");
    Object.defineProperty(event, "timeStamp", { value: time });
    this.dispatchEvent(event);
  }
}
const report = new HeadsetFrameReport(), session = new Session();
const memory = { geometries: 21, textures: 19 };
const frame = time => report.frame(session, time, true, "Market", memory);
frame(0);
frame(14);
session.visibility("hidden", 20);
// A sleeping headset may deliver no animation frames between these two events.
session.visibility("visible", 120020);
frame(120024);
frame(120074);  // genuine foreground hitch
let market = report.summary().rooms.find(row => row.room === "Market");
assert.equal(market.gameplayFrames, 2);
assert.equal(market.worstGameplayMs, 50);
assert.equal(market.framesOverOneAndAHalfRefreshIntervals, 1);
report.beginTravel(session,120080);
report.frame(session,120090,false,"Market",memory);
session.visibility("visible-blurred",120100);
session.visibility("hidden",120110);
session.visibility("visible",180100);
report.frame(session,180109,false,"Market",memory);
report.endTravel(session,"Quay",180115);
report.frame(session,180123,true,"Quay",memory);
report.frame(session,180139,true,"Quay",memory);
let quay = report.summary().rooms.find(row => row.room === "Quay");
assert.equal(quay.meanLoadMs,35);
assert.equal(quay.worstTransitionFrameMs,16);
assert.equal(quay.gameplayFrames,1);
assert.equal(quay.worstGameplayMs,16);

report.beginTravel(session,180150);
session.visibility("hidden",180160);
report.endTravel(session,"Yard",240160);
session.visibility("visible",250160);
report.frame(session,250166,true,"Yard",memory);
let yard = report.summary().rooms.find(row => row.room === "Yard");
assert.equal(yard.meanLoadMs,10);
assert.equal(yard.worstTransitionFrameMs,0);

const next = new Session();
report.frame(next,260000,true,"Gate",memory);
session.visibility("hidden",260012);
report.frame(next,260014,true,"Gate",memory);
assert.equal(report.summary().rooms.find(row=>row.room==="Gate").worstGameplayMs,14);
console.log("PASS active play, hidden loads, first visible frame, old session events and genuine hitches");
