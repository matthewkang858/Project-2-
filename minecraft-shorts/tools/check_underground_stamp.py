"""Checker: do render.py's frame fingerprints (engine.stamp) follow what engine/underground.py builds and animates?

    $BPY -m tools.check_underground_stamp          (no rendering, about a minute; exit code 1 if a case fails)

The set bakes the game's light into its materials (tinted textures + an emission multiplier): static, but every one
of them must reach the fingerprint (a change of the bake must make frames stale). What moves is keyed on objects:
the piston wall and the lever (engine.redstone), the pushed villager, the bouncing child, the jumping player. The
tool fingerprints a small film twice in this process, once more after a change, and once in a child process.
"""
import hashlib
import subprocess
import sys

import bpy

from engine import characters, look, players, shots, stamp
from engine import underground as U

FAILED = []


def ok(label, cond, detail=""):
    if not cond:
        FAILED.append(label)
    print("%-4s %s%s" % ("OK" if cond else "FAIL", label, ("  [%s]" % detail) if detail else ""), flush=True)


def build(emit=None):
    """A three-shot film: the wall opening, the push down the step, the bed bounce."""
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    look.setup_render(scene, res=(540, 960), samples=16, threads=2)
    old = U.EMIT
    if emit is not None:
        U.EMIT = emit
    try:
        v, ug = U.build_village(scene, seed=1)
    finally:
        U.EMIT = old
    look.set_time(scene, "dusk", sun_azimuth=187.0, sun_elevation=5.0, key_strength=0.0, ambient_strength=0.0)
    film = shots.Film(scene, fps=24)
    out = {"film": film, "ug": ug, "v": v}
    s = film.shot("wall", 0.0, 1.5)
    c = U.CAMERAS["b10_cell_side"]
    s.lens(c["lens"], c["fstop"])
    s.move(c["pos"], c["target"])
    s.focus(c["target"])
    out["open"] = ug.open_wall(s.frame_start + 8)
    s2 = film.shot("push", 1.5, 7.5)
    c = U.CAMERAS["b03_push"]
    s2.lens(c["lens"], c["fstop"])
    s2.move(c["pos"], c["target"])
    s2.focus(c["target"])
    dad = characters.make_villager("st_dad", "librarian")
    steve = players.make_player("st_steve")
    path = list(v.paths["ug_push"]) + [(5.0, -2.0, 0.0)]
    out["push"] = U.push(steve, dad, s2.frame_start, path, v.world)
    s3 = film.shot("bed", 7.5, 10.5)
    c = U.CAMERAS["b04_bed"]
    s3.lens(c["lens"], c["fstop"])
    s3.move(c["pos"], c["target"])
    s3.focus(c["target"])
    kid = characters.make_villager("st_kid", "farmer", child=True)
    out["bed"] = U.bed_bounce(kid, s3.frame_start, v.beds[U.BED]["foot"], jumps=3)
    # beat 7 / 16: a see-through cutaway (keyed as Stage.see_through does), Steve's jump loop, a shot-local bounce
    s4 = film.shot("down", 10.5, 12.0)
    c = U.CAMERAS["b07_down"]
    s4.lens(c["lens"], c["fstop"])
    s4.move(c["pos0"], c["target0"], c["pos"], c["target"])
    s4.focus(c["target"])
    for ob in v.cutaways["ug_ceiling"]:
        for f, val in ((film.frame_start, True), (s4.frame_start, False), (s4.frame_end + 1, True)):
            ob.visible_camera = val
            ob.keyframe_insert("visible_camera", frame=f)
    jumper = players.make_player("st_jumper")
    jumper.place(s4.frame_start, v.anchors["ug_jump_spot"], 0.0)
    out["jumps"] = U.jump_loop(jumper, s4.frame_start, s4.frame_end)

    class _St:                                       # what U.bounce needs of a Stage
        pass
    st = _St()
    st.v, st.film = v, film

    def key(ob, path, frame, value):
        setattr(ob, path, value)
        ob.keyframe_insert(path, frame=frame)
    st.key = key
    out["bounce"] = U.bounce(st, s4, U.COUNTER_BOUNCE)
    for ch_, shot in ((dad, s2), (steve, s2), (kid, s3), (jumper, s4)):
        for other in film.shots:
            ch_.show(other.frame_start, other is shot)
    film.finalize()
    return out


def prints(b, frames, order=None):
    fp = stamp.Fingerprinter(b["film"].scene, b["film"])
    out = {}
    for f in (order or frames):
        p = fp.frame(f)["parts"]
        out[f] = p["o"] + p["l"] + p["c"]
    return out


def digest(a, frames):
    h = hashlib.sha1()
    for f in frames:
        h.update(a[f].encode())
    return h.hexdigest()[:16]


def frames_of(b, name):
    s = next(s for s in b["film"].shots if s.name == name)
    return list(range(s.frame_start, s.frame_end + 1))


def main(argv):
    b = build()
    frames = [f for n in ("wall", "push", "bed", "down") for f in frames_of(b, n)]
    if "--child" in argv:
        print("DIGEST", digest(prints(b, frames), frames), flush=True)
        return 0
    a = prints(b, frames)
    r = prints(b, frames, order=list(reversed(frames)))
    ok("fingerprints do not depend on the order frames are taken in (%d frames)" % len(frames), a == r)
    fw = frames_of(b, "wall")
    changed = [f for f in fw[1:] if a[f] != a[f - 1]]
    o = b["open"]
    ok("wall: the frames change on the lever's flip and while the two blocks move, never before the flip",
       changed and min(changed) == o["flip"] and max(changed) <= o["open_end"] + 1,
       "changed %s, flip %d, open %d-%d" % (changed, o["flip"], o["open"], o["open_end"]))
    fp_ = frames_of(b, "push")
    moving = [f for f in fp_[1:] if a[f] != a[f - 1]]
    ok("push: the fingerprint changes on the frames where they move (%d of %d)" % (len(moving), len(fp_) - 1),
       len(moving) > 0.5 * (b["push"]["end"] - fp_[0]))
    fb = frames_of(b, "bed")
    still = [f for f in fb[1:] if f > b["bed"]["end"] + 1 and a[f] != a[f - 1]]
    ok("bed: no change once the bounce has died out", not still, "%s" % still)
    fd = frames_of(b, "down")
    jumping = [f for f in fd[1:] if a[f] != a[f - 1]]
    ok("down: the frames change while the camera slides and Steve jumps (%d of %d)" % (len(jumping), len(fd) - 1),
       len(jumping) >= len(fd) - 2)
    # the see-through ceiling and the bounce light are in the fingerprint: take them away and the frame differs
    f = fd[len(fd) // 2]
    scene = b["film"].scene
    for ob in b["v"].cutaways["ug_ceiling"]:
        ob.animation_data_clear()
        ob.visible_camera = True
    seen = prints(b, [f])[f]
    ok("down: the see-through ceiling (visible_camera keys) is in the fingerprint", seen != a[f])
    bo = b["bounce"]
    bo.animation_data_clear()
    bo.hide_render = True
    gone = prints(b, [f])[f]
    ok("down: the shot-local bounce light (hide_render keys) is in the fingerprint", gone != seen)
    fb2 = frames_of(b, "bed")[0]
    bo.hide_render = True
    ok("the bounce light is not in another shot's frames", prints(b, [fb2])[fb2] == a[fb2])
    b2 = build()
    a2 = prints(b2, frames)
    ok("built again in this process: identical fingerprints", a2 == a,
       "differ on %d frames" % sum(1 for f in frames if a2[f] != a[f]))
    b3 = build(emit=0.9)
    a3 = prints(b3, frames)
    ok("the bake is in the fingerprint: EMIT 0.9 instead of 1.0 changes the hall's frames",
       all(a3[f] != a[f] for f in fw))
    out = subprocess.run([sys.executable, "-m", "tools.check_underground_stamp", "--child"], capture_output=True,
                         text=True, timeout=280)
    line = [ln for ln in out.stdout.splitlines() if ln.startswith("DIGEST")]
    mine = digest(a, frames)
    ok("the same digest in a second process (%s)" % mine, bool(line) and line[0].split()[1] == mine,
       line[0] if line else out.stderr[-400:])
    print("check_underground_stamp: %s" % ("all passed" if not FAILED else "FAILED: %s" % FAILED))
    return 1 if FAILED else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
