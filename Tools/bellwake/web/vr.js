import * as T from "three";
import { Capsule } from "three/examples/jsm/math/Capsule.js";

const up = new T.Vector3(0, 1, 0);
export class TrackedRunner {
  constructor(scene, camera, renderer, load, world, use, book, exit, callGuide) {
    this.renderer = renderer;
    this.world = world;
    this.callGuide = callGuide;
    this.book = book;
    this.rig = new T.Group();
    scene.add(this.rig);
    this.rig.add(camera);
    this.body = new Capsule(new T.Vector3(), new T.Vector3(), 0.23);
    this.ball = new T.Sphere(new T.Vector3(), 0.1);
    for (const key of [
      "head",
      "direction",
      "velocity",
      "launch",
      "motion",
      "delta",
      "step",
      "work",
      "start",
      "push",
    ])
      this[key] = new T.Vector3();
    this.rotation = new T.Quaternion();
    this.hands = [0, 1].map(() => ({
      target: new T.Vector3(),
      prev: new T.Vector3(),
      anchor: new T.Vector3(),
      q: new T.Quaternion(),
      valid: false,
      contact: false,
    }));
    this.canvas = document.createElement("canvas");
    this.canvas.width = 896;
    this.canvas.height = 240;
    this.ink = new T.CanvasTexture(this.canvas);
    this.ink.colorSpace = T.SRGBColorSpace;
    this.card = new T.Mesh(
      new T.PlaneGeometry(1.42, 0.38),
      new T.MeshBasicMaterial({ map: this.ink, depthTest: false, depthWrite: false }),
    );
    scene.add(this.card);
    this.card.renderOrder = 90;
    this.card.visible = false;
    this.guard = new T.Mesh(
      new T.PlaneGeometry(1.8, 1.8),
      new T.MeshBasicMaterial({ color: 0, depthTest: false, depthWrite: false }),
    );
    this.guard.renderOrder = 100;
    this.guard.visible = false;
    scene.add(this.guard);
    this.safeHead = new T.Vector3();
    this.headBall = new T.Sphere(new T.Vector3(), 0.12);
    this.guardRay = new T.Ray();
    this.limbs = new T.Group();
    scene.add(this.limbs);
    this.limbs.visible = false;
    this.enter = async () => {
      if (this.session) return;
      const session = await navigator.xr.requestSession("immersive-vr", {
        requiredFeatures: ["local-floor"],
      });
      this.session = session;
      session.addEventListener("selectstart", use);
      session.addEventListener(
        "end",
        () => {
          this.session = null;
          this.ready = false;
          this.card.visible = false;
          this.guard.visible = false;
          this.limbs.visible = false;
          this.rig.position.set(0, 0, 0);
          this.rig.rotation.set(0, 0, 0);
          exit();
        },
        { once: true },
      );
      try {
        renderer.xr.setReferenceSpaceType("local-floor");
        renderer.xr.setFramebufferScaleFactor(0.85);
        await renderer.xr.setSession(session);
        renderer.xr.setFoveation(1);
        if (!this.palms) {
          const [left, right, arm] = await Promise.all(["LeftPalm", "RightPalm", "RunnerArm"].map(load));
          this.palms = [left, right];
          this.arms = [arm, arm.clone(true)];
          this.limbs.add(...this.palms, ...this.arms);
        }
        this.ready = true;
        this.reset();
        this.limbs.visible = true;
      } catch (e) {
        await session.end();
        throw e;
      }
    };
  }
  reset() {
    this.pending = true;
    this.clearPose = false;
    this.velocity.set(0, 0, 0);
    this.launch.set(0, 0, 0);
    this.hands.forEach((h) => {
      h.valid = h.contact = false;
    });
    this.rig.rotation.set(0, 0, 0);
    this.cached = "";
  }
  sweep(tree, move) {
    const n = Math.max(1, Math.min(16, Math.ceil(move.length() / 0.09)));
    this.step.copy(move).multiplyScalar(1 / n);
    for (let i = 0; i < n; i++) {
      this.body.translate(this.step);
      const hit = tree.capsuleIntersect(this.body);
      if (hit) this.body.translate(hit.normal.multiplyScalar(hit.depth));
    }
  }
  update(frame, dt, paused) {
    if (!this.ready || !frame) return;
    const ref = this.renderer.xr.getReferenceSpace(),
      viewer = frame.getViewerPose(ref),
      { tree, spawn, radius } = this.world();
    if (!viewer || !tree) return;
    const pos = viewer.transform.position,
      q = viewer.transform.orientation;
    if (this.pending) {
      this.rig.position.set(spawn.x - pos.x, spawn.y, spawn.z - pos.z);
      this.body.start.set(spawn.x, spawn.y + 0.23, spawn.z);
      this.body.end.copy(this.body.start);
      this.pending = false;
    }
    this.rig.updateMatrixWorld(true);
    this.head.set(pos.x, pos.y, pos.z).applyMatrix4(this.rig.matrixWorld);
    this.rotation.set(q.x, q.y, q.z, q.w).premultiply(this.rig.quaternion);
    this.direction.set(0, 0, -1).applyQuaternion(this.rotation);
    this.body.end.y = this.body.start.y + Math.max(0.12, pos.y - 0.38);
    this.delta.set(this.head.x - this.body.start.x, 0, this.head.z - this.body.start.z);
    this.start.copy(this.body.start);
    this.sweep(tree, this.delta);
    this.work.copy(this.body.start).sub(this.start).sub(this.delta);
    this.rig.position.add(this.work);
    this.head.add(this.work);
    this.rig.updateMatrixWorld(true);
    let squeeze = false,
      book = false,
      turn = 0,
      contacts = 0;
    const had = this.hands[0].contact || this.hands[1].contact;
    this.push.set(0, 0, 0);
    for (let i = 0; i < 2; i++) {
      let input;
      for (const source of this.session.inputSources)
        if (source.handedness === (i ? "right" : "left")) input = source;
      const h = this.hands[i],
        pose = input?.gripSpace ? frame.getPose(input.gripSpace, ref) : null;
      this.palms[i].visible = this.arms[i].visible = !!pose;
      if (!pose) {
        h.valid = h.contact = false;
        continue;
      }
      if (!i) squeeze = !!input.gamepad?.buttons[1]?.pressed;
      book ||= !!input.gamepad?.buttons[4]?.pressed;
      if (i && input.gamepad) turn = input.gamepad.axes[2] || input.gamepad.axes[0] || 0;
      const t = pose.transform.position,
        r = pose.transform.orientation;
      h.q.set(r.x, r.y, r.z, r.w).premultiply(this.rig.quaternion);
      h.target.set(t.x, t.y, t.z).applyMatrix4(this.rig.matrixWorld);
      this.work
        .set(i ? 0.18 : -0.18, -0.22, 0)
        .applyQuaternion(this.rig.quaternion)
        .add(this.head);
      h.target.sub(this.work).clampLength(0, 0.98).add(this.work);
      if (!h.valid) {
        h.prev.copy(h.target);
        h.valid = true;
      }
      const held = h.contact;
      h.contact = false;
      if (!paused) {
        this.delta.copy(h.target).sub(h.prev);
        // The collision correction deliberately leaves the palm just clear of
        // the floor. A wider release threshold keeps a planted hand anchored
        // during a tangential stroke, until the user actually lifts it.
        if (held && this.delta.lengthSq() < 0.25) {
          this.ball.center.copy(h.target);
          this.ball.radius = 0.145;
          h.contact = !!tree.sphereIntersect(this.ball);
          this.ball.radius = 0.1;
          if (h.contact) {
            this.push.add(this.work.copy(h.anchor).sub(h.target));
            contacts++;
            continue;
          }
        }
        const n = Math.min(12, Math.max(1, Math.ceil(this.delta.length() / 0.065)));
        for (let j = 1; j <= n; j++) {
          this.ball.center.copy(h.prev).addScaledVector(this.delta, j / n);
          const hit = tree.sphereIntersect(this.ball);
          if (!hit) continue;
          if (!held || this.delta.lengthSq() > 0.2)
            h.anchor.copy(this.ball.center).addScaledVector(hit.normal, hit.depth + 0.002);
          h.contact = true;
          this.push.add(this.work.copy(h.anchor).sub(h.target));
          contacts++;
          break;
        }
      }
    }
    if (!paused && squeeze && !this.squeezeHeld) this.callGuide();
    this.squeezeHeld = squeeze;
    if (book && !this.bookHeld) this.book();
    this.bookHeld = book;
    if (!paused && Math.abs(turn) > 0.76 && !this.turnHeld) {
      const a = (-Math.sign(turn) * Math.PI) / 4;
      this.rig.position.sub(this.head).applyAxisAngle(up, a).add(this.head);
      this.rig.rotation.y += a;
      this.hands.forEach((h) => {
        h.valid = h.contact = false;
      });
      this.turnHeld = true;
      return;
    }
    if (Math.abs(turn) < 0.3) this.turnHeld = false;
    if (contacts) {
      this.motion
        .copy(this.push)
        .multiplyScalar(1 / contacts)
        .clampLength(0, 0.29);
      this.velocity.set(0, 0, 0);
    } else {
      if (had && this.hands.every((h) => h.valid)) this.velocity.copy(this.launch).clampLength(0, 7);
      this.velocity.y = Math.max(-18, this.velocity.y - 11 * dt);
      this.motion.copy(this.velocity).multiplyScalar(dt);
    }
    if (paused) this.motion.set(0, 0, 0);
    this.start.copy(this.body.start);
    this.sweep(tree, this.motion);
    this.delta.copy(this.body.start).sub(this.start);
    if (contacts && dt > 0) this.launch.lerp(this.work.copy(this.delta).multiplyScalar(1 / dt), 0.4);
    if (this.delta.y > this.motion.y + 0.001 && this.velocity.y < 0) this.velocity.y = -0.5;
    this.rig.position.add(this.delta);
    this.head.add(this.delta);
    for (let i = 0; i < 2; i++) {
      const h = this.hands[i];
      if (!h.valid) continue;
      const palm = this.palms[i],
        arm = this.arms[i];
      palm.position.copy(h.contact ? h.anchor : h.target);
      if (!h.contact) palm.position.add(this.delta);
      palm.quaternion.copy(h.q);
      h.prev.copy(palm.position);
      this.work
        .set(i ? 0.23 : -0.23, -0.38, 0)
        .applyQuaternion(this.rig.quaternion)
        .add(this.head);
      arm.position.copy(this.work).lerp(palm.position, 0.5);
      this.work.sub(palm.position);
      arm.scale.set(1, this.work.length(), 1);
      arm.quaternion.setFromUnitVectors(up, this.work.normalize());
    }
    if (
      this.body.start.y < -0.5 ||
      Math.max(Math.abs(this.body.start.x), Math.abs(this.body.start.z)) > radius + 0.7
    )
      this.reset();
    this.headBall.center.copy(this.head);
    let blocked = !!tree.sphereIntersect(this.headBall);
    if (this.clearPose && !blocked) {
      this.work.copy(this.head).sub(this.safeHead);
      const travel = this.work.length();
      if (travel > 0.01) {
        this.guardRay.set(this.safeHead, this.work.normalize());
        const hit = tree.rayIntersect(this.guardRay);
        blocked = !!hit && hit.distance < travel;
      }
    }
    if (!blocked) {
      this.safeHead.copy(this.head);
      this.clearPose = true;
    }
    this.guard.visible = blocked;
    if (blocked) {
      this.guard.position.copy(this.head).addScaledVector(this.direction, 0.16);
      this.guard.quaternion.copy(this.rotation);
    }
    this.card.position
      .set(0, this.mapMode ? -0.06 : -0.38, -1.63)
      .applyQuaternion(this.rotation)
      .add(this.head);
    this.card.quaternion.copy(this.rotation);
  }
  surveyChanged() {
    if (this.mapInk) this.mapInk.needsUpdate = true;
  }
  showSurvey(canvas) {
    if (!this.mapInk) {
      this.mapInk = new T.CanvasTexture(canvas);
      this.mapInk.colorSpace = T.SRGBColorSpace;
    }
    this.mapMode = true;
    this.card.visible = true;
    this.card.scale.y = (1.42 * 544) / 768 / 0.38;
    this.card.material.map = this.mapInk;
  }
  caption(title, words) {
    if (this.mapMode) {
      this.card.material.map = this.ink;
      this.card.scale.y = 1;
      this.mapMode = false;
    }
    if (!this.ready) return;
    this.card.visible = !!words;
    if (!words) return;
    const key = title + "\n" + words;
    if (key === this.cached) return;
    this.cached = key;
    const c = this.canvas.getContext("2d");
    c.fillStyle = "#172923";
    c.fillRect(0, 0, 896, 240);
    c.fillStyle = "#d5ae68";
    c.fillRect(0, 0, 7, 240);
    c.font = "bold 24px sans-serif";
    c.fillText(title.toUpperCase(), 30, 40);
    c.font = "32px Georgia, serif";
    c.fillStyle = "#fff2cf";
    let line = "",
      y = 86;
    for (const w of words.split(/\s+/)) {
      const next = line ? line + " " + w : w;
      if (line && c.measureText(next).width > 830) {
        c.fillText(line, 30, y);
        y += 37;
        line = w;
      } else line = next;
    }
    c.fillText(line, 30, y);
    this.ink.needsUpdate = true;
  }
}
