"""Independent checker's probe of engine/breaking.py (not the author's): a film-like use of the door knocking the
way a director of "The Hello" would write beats 18-20, numeric robustness checks, and a few stills.

    $BPY -m tools.check_breaking_probe import          importing the module leaves an empty scene empty
    $BPY -m tools.check_breaking_probe numeric         robustness (no rendering)
    $BPY -m tools.check_breaking_probe render NAME F1,F2,...   stills out/test/check_breaking_<NAME>_<frame>.png
"""
import math
import os
import sys
import time

import bpy

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "out", "test")
BAD = []


def ok(label, cond, detail=""):
    """Print one case and remember a failure."""
    if not cond:
        BAD.append(label)
    print("%-4s %s%s" % ("OK" if cond else "FAIL", label, ("  [%s]" % detail) if detail else ""), flush=True)


def counts():
    """Number of datablocks of every kind that matters."""
    d = bpy.data
    return {k: len(getattr(d, k)) for k in ("objects", "meshes", "materials", "images", "actions", "lights",
                                            "collections", "node_groups", "cameras")}


def build_hello(scene, cam="side", shudder=8.0, half="both", along=-0.3, attempt=48, every=16, order="forward",
                twice=False, start_pad=0.0, sky="night"):
    """Beats 18, 19 and 20 of The Hello as the docstring's recipe writes them: knock (3.2 s), watch (2.5 s, the
    camera drifts left to a watcher two blocks along the wall), morning (2 s: flesh on the step, the door opens)."""
    from engine import breaking, look, mobs, shots, undead, village
    from films.lookdev import Stage

    v = village.build_village(scene, seed=1)
    if sky == "night":
        skyobj = look.set_time(scene, "night", sun_azimuth=176.0, sun_elevation=21.0)
        look.setup_compositor(scene, bloom=1.3, grade="cool")
    else:
        skyobj = look.set_time(scene, "golden", sun_azimuth=215.0, sun_elevation=27.0)
        look.setup_compositor(scene, bloom=1.0, grade="warm")
    film = shots.Film(scene, fps=24)
    st = Stage(scene, film, v, skyobj)
    door = v.doors["house_a"]
    lights = breaking.door_torches(v, "house_a")
    z = undead.add_zombie(st, "zombie")
    watcher = st.actor("watcher", "steve")
    out = dict(film=film, st=st, v=v, door=door, z=z, lights=lights, watcher=watcher)
    if start_pad:
        s0 = st.shot("pad", start_pad)
        s0.lens(47, 4.0)
        s0.move(*breaking.DOOR_CAM["plaza"][:2])
        st.lights(s0, scale=1.3)
    s1 = st.shot("knock", 3.2)
    s2 = st.shot("watch", 2.5)
    s3 = st.shot("morning", 2.0)
    pos, target, lens = breaking.DOOR_CAM[cam]
    kw = dict(attempt=attempt, every=every, half=half, along=along, shudder=shudder, world=v)

    def first():
        return breaking.bang_on_door(z, door, s1.frame_start, s1.frame_end + 1, phase=0.35, camera=s1, **kw)

    def second(phase):
        return breaking.bang_on_door(z, door, s2.frame_start, s2.frame_end + 1, phase=phase, place=False,
                                     camera=s2, **kw)

    if order == "forward":
        r1 = first()
        if twice:
            r1 = first()
        r2 = second(r1["phase"])
        if twice:
            r2 = second(r1["phase"])
    else:                                                     # a director who writes the later shot first
        probe_phase = ((0.35 * attempt + (s1.frame_end + 1 - s1.frame_start)) % (attempt + 2)) / attempt
        r2 = second(min(probe_phase, 0.999))
        r1 = first()
    out.update(r1=r1, r2=r2, s1=s1, s2=s2, s3=s3)
    s1.lens(lens, 4.0)
    s1.move(pos, target)
    s1.focus((10.0, -7.5, 2.0))
    s1.handheld(0.012, seed=7)
    st.use(s1, z)
    st.lights(s1, scale=1.3)
    # beat 19: the camera drifts a block and a half to the left (north for a camera looking east): the watcher
    wpos = (9.45, -5.4, v.ground(9.45, -5.4))
    watcher.place(s2.frame_start, wpos, math.pi / 2.0)
    s2.lens(lens, 4.0)
    s2.move(pos, target, (pos[0], pos[1] + 1.5, pos[2]), (target[0], target[1] + 1.5, target[2]))
    s2.focus((10.0, -7.5, 2.0))
    s2.handheld(0.012, seed=8)
    st.use(s2, z, watcher)
    st.lights(s2, scale=1.3)
    # beat 20: the flesh on the step, the door opens
    flesh = mobs.make_dropped_item("rotten_flesh")
    flesh.place(s3.frame_start, breaking.stand_point(door)[0])
    flesh.animate(s3.frame_start, s3.frame_end + 1)
    st.cast[flesh.name] = flesh
    st.use(s3, flesh)
    v.door_open("house_a", s3.frame_start + 12, open=True, frames=8)
    s3.lens(lens, 4.0)
    s3.move(pos, target)
    s3.focus((10.0, -7.5, 2.0))
    st.lights(s3, scale=1.3)
    out["flesh"] = flesh
    st.finish()
    return out


def fresh(res=(540, 960), samples=16):
    """An empty scene with the test render settings (motion blur on, 2 threads)."""
    from engine import look

    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    look.setup_render(scene, res=res, samples=samples, threads=2, motion_blur=True)
    return scene


def door_yaw(door, f):
    """The door's keyed yaw minus its closed yaw at (fractional) frame f."""
    from engine.shots import fcurves_of

    for fc in fcurves_of(door):
        if fc.data_path == "rotation_euler" and fc.array_index == 2:
            return fc.evaluate(f) - float(door["closed_yaw"])
    return float(door.rotation_euler[2]) - float(door["closed_yaw"])


def rendered(scene, objs, f):
    """Names of the objects of `objs` that are rendered on frame f."""
    scene.frame_set(int(f))
    return [o.name for o in objs if not o.hide_render]


def numeric():
    """Robustness without rendering."""
    from engine import breaking, stamp
    from engine.breaking import _door

    scene = fresh()
    p = build_hello(scene)
    door, z, r1, r2, s1, s2, s3 = p["door"], p["z"], p["r1"], p["r2"], p["s1"], p["s2"], p["s3"]
    t = _door(door)
    print("shots: knock %d-%d, watch %d-%d, morning %d-%d" % (s1.frame_start, s1.frame_end, s2.frame_start,
                                                              s2.frame_end, s3.frame_start, s3.frame_end))
    print("knocks1", r1["knocks"], "hits1", r1["hits"], "resets1", r1["resets"], "phase", round(r1["phase"], 3))
    print("knocks2", r2["knocks"], "hits2", r2["hits"], "resets2", r2["resets"])
    seq = [breaking.stage_at(door, f) for f in range(s1.frame_start, s3.frame_start + 3)]
    print("stages per frame:", "".join("." if s < 0 else str(s) for s in seq))
    cut = s2.frame_start
    a, b = breaking.stage_at(door, cut - 1), breaking.stage_at(door, cut)
    ok("across the cut the climb continues (stage on the last frame of knock, first of watch)", b in (a, a + 1)
       or (a == 9 and b in (-1, 0)), "%d -> %d" % (a, b))
    one = [len(rendered(scene, t.objects, f)) for f in range(s1.frame_start, s3.frame_end + 1)]
    ok("exactly one copy of the door is rendered on every frame of the three shots", set(one) == {1}, str(set(one)))
    ok("morning: the plain door is what is rendered (it opens), no cracks left",
       rendered(scene, t.objects, s3.frame_start) == [door.name] and breaking.stage_at(door, s3.frame_start) == -1)
    # the swing rhythm across the cut
    gaps = [b_ - a_ for a_, b_ in zip(r1["knocks"] + r2["knocks"], (r1["knocks"] + r2["knocks"])[1:])]
    ok("swing rhythm across the cut: gaps between swing starts are all `every` (16) frames", set(gaps) == {16},
       str(gaps))
    arms = [round(math.degrees(z.arm_base(f)), 1) for f in (cut - 2, cut - 1, cut, cut + 1, cut + 2, cut + 3)]
    ok("the raised arms do not drop at the cut (place=False)", len(set(arms)) == 1, str(arms))
    # door at rest between blows and in the morning, opening only when door_open says
    f_open = s3.frame_start + 12
    drift = max(abs(door_yaw(door, f / 4.0)) for f in range(4 * (r2["hits"][-1] + 4), 4 * f_open + 1))
    ok("the door is exactly shut between the last shudder and door_open (no bezier drift)", drift < 1e-6,
       "max %.5f rad" % drift)
    opened = door_yaw(door, f_open + 8)
    ok("door_open after the knocking opens it fully", abs(abs(opened) - math.pi / 2) < 1e-4, "%.3f" % opened)
    amp = [round(door_yaw(door, h), 4) for h in r1["hits"]]
    want = 8.0 * 0.5 / 16.0
    ok("shudder=8: every blow of shot 1 peaks at 0.25 rad inward on the hit frame", all(abs(x - want) < 1e-4 for x in amp),
       str(amp))
    print("door open_angle %.3f; shudder sign %+d (same sign as opening = away from the front)" % (
        door["open_angle"], 1 if amp[0] > 0 else -1))
    # hits relative to the swing: when are the arms lowest?
    k = r1["knocks"][1]
    low = min(range(0, 60), key=lambda i: -z.swing_value(k + i / 4.0)) / 4.0
    print("swing started on %d: swing_value peaks %.2f frames later; the shudder is keyed %d frames later" % (
        k, low, r1["hits"][1] - k))
    # stamp: every frame where the picture changes has another fingerprint
    fp = stamp.Fingerprinter(scene, p["film"])
    frames = list(range(s1.frame_start, s1.frame_start + 40))
    prints = {f: fp.frame(f)["parts"]["o"] for f in frames}
    same = [f for f in frames[1:] if prints[f] == prints[f - 1]]
    print("frames of shot 1 with the same object fingerprint as the frame before:", same)
    snap = {f: (door_yaw(door, f), z.swing_value(f), breaking.stage_at(door, f)) for f in range(s1.frame_start, s3.frame_end + 1)}

    # ---- called twice
    scene = fresh()
    q = build_hello(scene, twice=True)
    snap2 = {f: (door_yaw(q["door"], f), q["z"].swing_value(f), breaking.stage_at(q["door"], f))
             for f in range(q["s1"].frame_start, q["s3"].frame_end + 1)}
    worst = max((abs(snap[f][0] - snap2[f][0]), f) for f in snap)
    ok("the same bang_on_door calls made twice give the same door motion (shudder not doubled)", worst[0] < 1e-6,
       "largest difference %.4f rad on frame %d" % worst)
    ok("... the same swings and stages", all(snap[f][1:] == snap2[f][1:] for f in snap))

    # ---- later shot keyed first
    scene = fresh()
    q = build_hello(scene, order="reverse")
    cut = q["s2"].frame_start
    seq2 = [breaking.stage_at(q["door"], f) for f in range(q["s1"].frame_start, q["s3"].frame_start + 3)]
    print("reverse order stages:", "".join("." if s < 0 else str(s) for s in seq2))
    ok("shots keyed in reverse order: the same stages as in forward order", seq2 == seq,
       "first difference at frame %s" % next((q["s1"].frame_start + i for i, (x, y) in enumerate(zip(seq, seq2))
                                               if x != y), None))

    # ---- at frame 1, the game's own timing, plain staging
    scene = fresh()
    from engine import look, shots, undead, village
    from films.lookdev import Stage

    v = village.build_village(scene, seed=1)
    skyobj = look.set_time(scene, "night", sun_azimuth=176.0, sun_elevation=21.0)
    film = shots.Film(scene, fps=24)
    st = Stage(scene, film, v, skyobj)
    s = st.shot("one", 3.0)
    s.move(*breaking.DOOR_CAM["plaza"][:2])
    z = undead.add_zombie(st, "zombie")
    door = v.doors["house_a"]
    before = counts()
    r = breaking.bang_on_door(z, door, s.frame_start, s.frame_end + 1)
    st.use(s, z)
    st.finish()
    print("frame-1 call, defaults: knocks %s stages %s" % (r["knocks"], r["stages"]))
    ok("defaults at frame 1: the game's 288-frame attempt (stage 0 on frame 1, stage 1 on frame 30), swings 31.2 "
       "frames apart", r["stages"][0] == (1, 0) and r["stages"][1][0] in (29, 30) and r["knocks"][:2] == [3, 34],
       str(r["stages"][:3]))
    scene.frame_set(1)
    ok("on frame 1 the cracked copy is rendered, on frame 0 (before the film) the plain door",
       rendered(scene, _door(door).objects, 1) != [door.name] and rendered(scene, _door(door).objects, 0) == [door.name])
    zpos = z.pos_at(1)
    print("zombie at", tuple(round(c, 3) for c in zpos), "yaw", round(math.degrees(z.yaw_at(1)), 1))
    w = v.world
    print("blocks under the zombie:", [(c, w.get(*c)) for c in ((9, -8, 0), (9, -8, 1), (8, -8, 0), (9, -8, -1),
                                                                (10, -8, 1), (10, -8, 2), (10, -8, 0))])
    # a second zombie on another door at the same time
    z2 = undead.make_zombie("zombie_b")
    other = next(n for n in sorted(v.doors) if n != "house_a")
    rb = breaking.bang_on_door(z2, v.doors[other], 1, 73, attempt=40, every=16, shudder=4)
    ok("two doors at once: each keeps its own stages", breaking.stage_at(v.doors[other], 20) == 4
       and breaking.stage_at(door, 20) == 0, "%s stage %d, house_a stage %d" % (
           other, breaking.stage_at(v.doors[other], 20), breaking.stage_at(door, 20)))
    info = breaking.door_info(v.doors[other])
    sp = rb["stand"]
    cellz = (int(math.floor(sp[0])), int(math.floor(sp[1])), int(round(sp[2])) - 1)
    print("door %s: stand %s, block under it %s, block at it %s" % (
        other, tuple(round(c, 2) for c in sp), w.get(*cellz), w.get(cellz[0], cellz[1], cellz[2] + 1)))
    for name in sorted(v.doors):
        d = v.doors[name]
        (x, y, zz), yaw = breaking.stand_point(d)
        c = (int(math.floor(x)), int(math.floor(y)))
        g = v.ground(x, y)
        under = w.get(c[0], c[1], int(round(zz)) - 1)
        at = w.get(c[0], c[1], int(round(zz)))
        print("  %-12s stand (%.2f, %.2f, %.2f) ground() %.2f  under %s  in cell %s" % (name, x, y, zz, g, under and under[0], at and at[0]))
    print("[probe] numeric: %d failed%s" % (len(BAD), ": " + "; ".join(BAD) if BAD else ""))
    return len(BAD)


def check_import():
    """Importing engine.breaking adds nothing to an empty scene."""
    bpy.ops.wm.read_factory_settings(use_empty=True)
    a = counts()
    from engine import breaking  # noqa: F401

    b = counts()
    ok("import engine.breaking leaves the empty scene untouched", a == b, "%s -> %s" % (a, b))
    return len(BAD)


def render(name, frames, **kw):
    """Stills of the probe film."""
    scene = fresh()
    p = build_hello(scene, **kw)
    print("shots: knock %d-%d, watch %d-%d, morning %d-%d; hits %s / %s; resets %s" % (
        p["s1"].frame_start, p["s1"].frame_end, p["s2"].frame_start, p["s2"].frame_end, p["s3"].frame_start,
        p["s3"].frame_end, p["r1"]["hits"], p["r2"]["hits"], p["r1"]["resets"]), flush=True)
    for f in frames:
        t = time.time()
        p["film"].goto(f)
        scene.render.filepath = os.path.join(OUT, "check_breaking_%s_%03d.png" % (name, f))
        bpy.ops.render.render(write_still=True)
        from engine import breaking

        print("[probe] %s frame %d stage %d  %.1f s" % (name, f, breaking.stage_at(p["door"], f), time.time() - t),
              flush=True)
    return 0


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "numeric"
    if mode == "import":
        sys.exit(1 if check_import() else 0)
    if mode == "numeric":
        sys.exit(1 if numeric() else 0)
    if mode == "render":
        opts = {}
        for a in sys.argv[4:]:
            k, val = a.split("=")
            opts[k] = val if k in ("cam", "half", "order", "sky") else float(val)
        sys.exit(render(sys.argv[2], [int(x) for x in sys.argv[3].split(",")], **opts))
