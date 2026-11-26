"""Checker probe for engine/towers.py (independent review): robustness without rendering.

    $BPY -m tools.check_towers_robust import      # importing engine.towers leaves the scene untouched
    $BPY -m tools.check_towers_robust village     # the village outside the tower's footprint is unchanged
    $BPY -m tools.check_towers_robust twice       # the proof film built twice in one process: same fingerprints
    $BPY -m tools.check_towers_robust cuts        # a small film: frame 1, cuts, cutaways, golem across shots
"""
import hashlib
import math
import sys

import bpy

RES = {}


def ok(label, cond, detail=""):
    RES[label] = bool(cond)
    print("%-4s %s%s" % ("OK" if cond else "FAIL", label, ("  [%s]" % detail) if detail else ""), flush=True)


def counts():
    return {k: len(getattr(bpy.data, k)) for k in ("objects", "meshes", "materials", "images", "collections",
                                                     "lights", "cameras", "actions", "node_groups", "scenes")}


def part_import():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    a = counts()
    names = sorted(o.name for o in bpy.data.objects)
    import engine.towers  # noqa: F401
    b = counts()
    ok("import engine.towers adds no data block", a == b, "%s -> %s" % (a, b))
    ok("import engine.towers leaves the objects as they were", names == sorted(o.name for o in bpy.data.objects))


def world_snapshot(v):
    w = v.world
    return {c: w._states[s] for c, s in w.blocks.items()}


def part_village():
    from engine import quick, towers, village

    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = quick.reset()
    v0 = village.build_village(scene, seed=1)
    w0 = world_snapshot(v0)
    a0 = dict(v0.anchors)
    lights0 = sorted((round(o.location.x, 2), round(o.location.y, 2), round(o.location.z, 2)) for o in v0.lantern_lights)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = quick.reset()
    v1 = village.build_village(scene, seed=1, edit=lambda b: towers.iron_farm(b))
    w1 = world_snapshot(v1)
    L = v1.sets["tower"]["layout"]
    x0, y0, x1, y1 = L["footprint"]
    pad = 3
    diff = [c for c in set(w0) | set(w1) if w0.get(c) != w1.get(c)]
    inside = [c for c in diff if x0 - pad <= c[0] <= x1 + pad and y0 - pad <= c[1] <= y1 + pad]
    outside = sorted(c for c in diff if c not in inside)
    kinds = {}
    for c in outside:
        k = "%s -> %s" % (w0.get(c, (None,))[0], w1.get(c, (None,))[0])
        kinds.setdefault(k, []).append(c)
    print("footprint %s (+pad %d); %d cells differ, %d outside" % (L["footprint"], pad, len(diff), len(outside)))
    for k, cs in sorted(kinds.items(), key=lambda kv: -len(kv[1])):
        xs = [c[0] for c in cs]
        ys = [c[1] for c in cs]
        print("   %-40s %4d cells  x %d..%d  y %d..%d  e.g. %s" % (k, len(cs), min(xs), max(xs), min(ys), max(ys), cs[:4]))
    non_plant = [c for c in outside if (w0.get(c, (None,))[0] or "") not in
                 ("short_grass", "tall_grass", "poppy", "dandelion", "oxeye_daisy", "cornflower", None)
                 or w1.get(c) is not None]
    ok("outside the footprint (+3) only plants are removed, no block is added or changed", not non_plant,
       "%d non-plant changes, e.g. %s" % (len(non_plant), non_plant[:6]))
    ok("outside the footprint (+3) the village is unchanged (not even plants)", not outside,
       "%d plant cells cleared outside" % len(outside))
    moved = [k for k in a0 if a0[k] != v1.anchors.get(k)]
    ok("every anchor of the plain village is where it was", not moved, str(moved[:6]))
    lights1 = sorted((round(o.location.x, 2), round(o.location.y, 2), round(o.location.z, 2)) for o in v1.lantern_lights)
    extra = [p for p in lights1 if p not in lights0]
    lost = [p for p in lights0 if p not in lights1]
    ok("the village's own lights are all there (the tower adds its two)", not lost and len(extra) == 2,
       "added %s lost %s" % (extra, lost))
    gone = v1.sets["tower"]["trees_removed"]
    print("trees removed: %s" % gone)


def part_twice():
    from engine import stamp
    from tools import towers_proof as tp

    digs = []
    for k in range(2):
        bpy.ops.wm.read_factory_settings(use_empty=True)
        scene = bpy.context.scene
        built = tp.build(scene, res=(720, 1280), samples=24, threads=4)
        film = built["film"]
        fp = stamp.Fingerprinter(scene, film)
        frames = [s.frame_start for s in film.shots] + [s.frame_start + 7 for s in film.shots]
        d = hashlib.sha1()
        for f in sorted(frames):
            d.update(("%d:%s" % (f, fp.frame(f)["fp"])).encode())
        digs.append(d.hexdigest())
        print("build %d: %d objects, digest %s" % (k + 1, len(bpy.data.objects), digs[-1]), flush=True)
    ok("the same film built twice in one process gives the same fingerprints", digs[0] == digs[1], str(digs))


def shown(scene, c, f):
    scene.frame_set(f)
    obs = getattr(c, "objects", None)
    obs = obs() if callable(obs) else (list(obs) if obs is not None else [c])
    if hasattr(c, "object") and not hasattr(c, "root"):
        obs = list(obs) + [c.object]
    return any((not ob.hide_render) for ob in obs if ob.type == "MESH")


def cam_visible(scene, ob, f):
    scene.frame_set(f)
    return ob.visible_camera and not ob.hide_render


def part_cuts():
    """A film that starts with the golem's spawn and the swap on frame 1, cuts away and back."""
    from engine import look, mobs, players, shots, towers, undead, village
    from films.lookdev import Stage

    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    look.setup_render(scene, res=(540, 960), samples=16, threads=2)
    v = village.build_village(scene, seed=1, edit=lambda b: towers.iron_farm(b))
    fm = towers.farm(v)
    sk = Stage.build_sky(scene, dict(preset="golden", az=62.0, el=27.0, bloom=1.0, grade="warm"))
    film = shots.Film(scene, fps=24)
    st = Stage(scene, film, v, sk)
    A = fm.A
    g = mobs.make_iron_golem("golem")
    st.cast["golem"] = g
    baby = st.actor("baby", "none", child=True)
    adult = st.actor("narrator", "none")
    mom = st.actor("mom", "farmer")
    steve = players.add_player(st, "steve", "steve")
    # shot a: frame 1 spawn, slide, puff; the swap on frame 1; the second bed on frame 1; the roof hidden
    a = st.shot("a", 4.0)
    ok("the film starts at frame 1", a.frame_start == 1, str(a.frame_start))
    fm.golem_spawn(g, a.frame_start, look=A["pod_target"])
    r = fm.golem_slide(g, a.frame_start + 10)
    d = fm.golem_death(g, r, camera=a)
    baby.place(a.frame_start, A["baby_glass"], fm.yaw["baby_glass"])
    towers.grow_up(baby, adult, a.frame_start, look=fm.zombie_eye)
    mom.place(a.frame_start, A["mom_glass"], fm.yaw["mom_glass"])
    mom.look_at(a.frame_start, fm.zombie_eye, ease=0)
    fm.bed2.place_at(a.frame_start)
    st.see_through(a, "tower_pod_roof")
    a.lens(22)
    a.move(fm.cameras["high"]["pos"], fm.cameras["high"]["target"])
    st.use(a, g, baby, adult, mom)
    st.lights(a, 1.0)
    # shot b: nothing of the farm; Steve elsewhere
    b = st.shot("b", 2.0)
    steve.place(b.frame_start, (0.0, -6.0, 0.0), 0.0)
    b.lens(35)
    b.move((0.0, -12.0, 1.6), (0.0, -6.0, 1.2))
    st.use(b, steve)
    st.lights(b, 1.0)
    # shot c: the golem spawns 20 frames into the shot (it was last seen sliding away in a)
    c = st.shot("c", 3.0)
    spawn_c = c.frame_start + 20
    fm.golem_spawn(g, spawn_c, look=A["pod_target"])
    c.lens(20)
    c.move(fm.cameras["platform"]["pos"], fm.cameras["platform"]["target"])
    st.use(c, g, mom)
    mom.place(c.frame_start, A["back_1"], fm.yaw["back_1"])
    st.lights(c, 1.0)
    # shot d: jump cut, the same golem spawns again on the same block without a slide
    dd = st.shot("d", 2.0)
    try:
        fm.golem_spawn(g, dd.frame_start + 10)
        refused = False
    except ValueError:
        refused = True
    fm.golem_spawn(g, dd.frame_start + 10, empty_from=dd)
    dd.lens(20)
    dd.move(fm.cameras["platform"]["pos"], fm.cameras["platform"]["target"])
    st.use(dd, g)
    st.lights(dd, 1.0)
    # shot e: the step breaks; f: after it
    e = st.shot("e", 2.0)
    steve.place(e.frame_start, A["one_down"], fm.yaw["one_down"])
    steve.look_at(e.frame_start, fm.top_step.center, ease=0)
    m = fm.break_top_step(steve, e.frame_start + 4, camera=e)
    e.lens(30)
    e.move(fm.cameras["stairs"]["pos"], fm.cameras["stairs"]["target"])
    st.use(e, steve)
    st.lights(e, 1.0)
    f_ = st.shot("f", 1.0)
    f_.lens(30)
    f_.move(fm.cameras["stairs"]["pos"], fm.cameras["stairs"]["target"])
    st.use(f_)
    st.lights(f_, 1.0)
    st.finish()

    F1 = a.frame_start
    ok("frame 1: the golem spawned on frame 1 is rendered ON frame 1", shown(scene, g, F1))
    ok("frame 1: the golem is not rendered on frame 0", not shown(scene, g, 0))
    ok("frame 1: the adult swapped in on frame 1 is rendered on frame 1, the baby is not",
       shown(scene, adult, F1) and not shown(scene, baby, F1))
    bed_obs = fm.bed2.objects()
    scene.frame_set(F1)
    ok("frame 1: the second bed placed on frame 1 is rendered on frame 1", any(not o.hide_render for o in bed_obs))
    scene.frame_set(0)
    ok("frame 1: ... and not on frame 0", all(o.hide_render for o in bed_obs))
    roof = v.cutaways["tower_pod_roof"]
    ok("frame 1: the roof cutaway hidden for shot a is hidden from frame 1",
       not any(cam_visible(scene, o, F1) for o in roof))
    ok("the roof is back for the camera in shot b", all(cam_visible(scene, o, b.frame_start) for o in roof))
    ok("the golem that slid away in shot a is not rendered in shot b",
       not any(shown(scene, g, k) for k in range(b.frame_start, b.frame_end + 1)))
    pre_c = [k for k in range(c.frame_start, spawn_c) if shown(scene, g, k)]
    ok("shot c opens on an empty platform: the golem is not rendered before its spawn (frame %d)" % spawn_c,
       not pre_c and shown(scene, g, spawn_c), "shown on %s" % pre_c[:5])
    ok("a second spawn without a slide is refused without empty_from", refused)
    ok("jump cut d: the golem of shot c is not rendered from d's first frame to the new spawn",
       not any(shown(scene, g, k) for k in range(dd.frame_start, dd.frame_start + 10))
       and shown(scene, g, dd.frame_start + 10) and shown(scene, g, c.frame_end))
    burst = d["burst"]
    parts = list(getattr(burst, "objects", []) or [])
    print("death puff: %d objects, frame %s .. %s; shot a ends %d" % (len(parts), d["frame"],
          getattr(burst, "frame_end", None), a.frame_end))
    late = [k for k in range(b.frame_start, b.frame_end + 1) if any(not p.hide_render for p in parts if (scene.frame_set(k) or True))]
    ok("the death puff of shot a does not carry into shot b (%d particles found)" % len(parts), not late,
       "puff rendered in shot b on %s" % late[:5])
    ts = fm.top_step
    ok("the top step is there before its break and gone from the break frame (%d) on" % m["frame"],
       shown(scene, ts, m["frame"] - 1) and not shown(scene, ts, m["frame"])
       and not shown(scene, ts, f_.frame_start))
    ok("the top step is there in shot a (before the break)", shown(scene, ts, a.frame_start + 5))
    # break particles of shot e reaching shot f
    mb = m.get("burst")
    plist = list(getattr(mb, "objects", []) or []) if mb is not None else []
    late2 = [k for k in range(f_.frame_start, f_.frame_end + 1)
             if (scene.frame_set(k) or True) and any(not o.hide_render for o in plist)]
    print("break burst: %d particle objects, break on %d, shot e ends %d" % (len(plist), m["frame"], e.frame_end))
    ok("the break crumbs of shot e do not carry into shot f", not late2, "rendered in f on %s" % late2[:5])
    lava_lights = [o for o in bpy.data.objects if o.type == "LIGHT" and "lava" in o.name]
    print("lava lights: %s" % [(o.name, o.data.energy) for o in lava_lights[:3]])


def main(argv):
    parts = argv or ["import"]
    for p in parts:
        print("== %s" % p, flush=True)
        globals()["part_" + p]()
    bad = [k for k, v in RES.items() if not v]
    print("%s (%d failed)" % ("ALL OK" if not bad else "FAILED", len(bad)))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
