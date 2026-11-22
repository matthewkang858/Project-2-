"""Independent probe of engine/fx.py (checker's script; not part of the engine).

  $BPY -m tools.check_fx_probe check                 numeric checks only
  $BPY -m tools.check_fx_probe render 7 13 17 ...    render those frames to out/test/check_fx_f###.png
  $BPY -m tools.check_fx_probe glint                 A/B of the book with and without the glint
"""
import math
import os
import sys
import time

import bpy
from mathutils import Vector

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "out", "test")


def snapshot():
    """Counts of every datablock kind and the scene's object names."""
    d = bpy.data
    return {k: len(getattr(d, k)) for k in ("objects", "meshes", "materials", "images", "collections", "actions",
                                             "node_groups", "cameras", "lights")}


def build(scene, glint_strength=1.0):
    from films import lookdev

    from engine import fx, look, shots, village

    v = village.build_village(scene, seed=1)
    sky = look.set_time(scene, "golden", sun_azimuth=62.0, sun_elevation=27.0, key_strength=1.0, ambient_strength=1.0)
    look.setup_compositor(scene, bloom=1.0, grade="warm")
    film = shots.Film(scene, fps=24)
    st = lookdev.Stage(scene, film, v, sky)
    A = v.anchors
    lec = fx.extract_block(v, "cell_1")                         # by anchor name
    tab = fx.hall_job_block(v, 2)                               # full cube: the fletching table
    lib = st.cast["lib"] = fx.make_job_villager("lib", ("librarian", "none"))
    fl = st.cast["fl"] = fx.make_job_villager("fl", ("fletcher", "none"))
    steve = st.actor("steve", "steve")
    spot1, spot2 = A["cell_1"], A["cell_2"]
    yaw = v.yaws["cell_1"]

    # ---- shot 1: wide, from the east end of the aisle, Steve at the lectern, cells 1 and 2 in view ----------
    s = st.shot("wide", 3.0)
    f0, f1 = s.frame_start, s.frame_end
    cam = (-3.0, -27.5, 1.70)
    s.lens(20, 3.4)
    s.move(cam, (-4.75, -30.53, 1.05), (cam[0] - 0.12, cam[1], cam[2]))
    lib.place(f0, spot1, yaw)
    fl.place(f0, spot2, yaw)
    stand = (-5.3, -29.3, 0.0)
    steve.place(f0, stand, lookdev.yaw_to(stand, lec.center))
    steve.look_at(f0, (lec.center.x, lec.center.y, lec.top - 0.2), ease=0)
    lib.look_at(f0, steve, ease=0)
    fl.look_at(f0, steve, ease=0)
    lib.idle(f0, f1 + 1, seed=4)
    fl.idle(f0, f1 + 1, seed=5)
    st.use(s, lib, fl, steve)
    bursts = {}
    swings = fx.mining_swings(steve, 1, 13)
    bursts["break"] = fx.break_block(lec, 1, 13, camera=s, hit_from=steve, seed=3)        # starts ON frame 1
    lib.lose_profession(19)
    bursts["break_tab"] = fx.break_block(tab, 24, 36, camera=s, hit_from=(-3.5, -29.5, 0.0), seed=4)
    fl.lose_profession(42)
    steve.swing_arm(44)
    fx.place_block(lec, 46)
    bursts["happy"] = lib.gain_profession(56, "librarian", camera=film, seed=9)           # lives across the cut
    bursts["angry"] = fx.emit("angry_villager", fl, 60, camera=film, seed=2, village=v, in_air=True)
    s.focus(lib.head)
    s.handheld(0.004, seed=11)
    st.lights(s, scale=0.0, groups={"hall": 0.8}, inside="hall")

    # ---- shot 2: close on the librarian holding out the enchanted book --------------------------------------
    sb = st.shot("close", 2.0)
    h0, h1 = sb.frame_start, sb.frame_end
    mid = (spot1[0], spot1[1] - 0.22, spot1[2])
    lib.place(h0, mid, yaw)
    book = fx.hold_out(lib, "enchanted_book", h0, h1 + 1, enchanted=True, strength=glint_strength)
    camb = (-4.75, -29.2, 1.70)
    lib.look_at(h0, camb, ease=0)
    lib.idle(h0, h1 + 1, seed=6)
    st.use(sb, lib)
    sb.lens(50, 3.4)
    sb.move(camb, (-5.5, -31.1, 1.35), (camb[0] - 0.05, camb[1], camb[2]))
    sb.focus(book)
    sb.handheld(0.003, seed=12)
    st.lights(sb, scale=0.0, groups={"hall": 0.8}, inside="hall")
    st.finish()
    return dict(fx=fx, film=film, st=st, v=v, lec=lec, tab=tab, lib=lib, fl=fl, steve=steve, book=book,
                bursts=bursts, shots=(s, sb), swings=swings)


def curve(idb, path, index=0):
    from engine.shots import fcurves_of

    for fc in fcurves_of(idb):
        if fc.data_path == path and fc.array_index == index:
            return fc
    return None


def visible(ob, frame):
    fc = curve(ob, "hide_render")
    return (fc.evaluate(frame) < 0.5) if fc is not None else (not ob.hide_render)


def check(p):
    fx, film, scene = p["fx"], p["film"], p["film"].scene
    bad = []

    def ok(label, cond, detail=""):
        print("%-4s %s %s" % ("OK" if cond else "FAIL", label, detail))
        if not cond:
            bad.append(label)

    lec, tab, lib, fl, steve, book = p["lec"], p["tab"], p["lib"], p["fl"], p["steve"], p["book"]
    s, sb = p["shots"]
    print("lectern", lec.stats, "top", lec.top, "props", lec.props)
    print("table  ", tab.block_id, tab.stats, "shape", tab.shape)
    # block state per frame
    for name, blk, f_gone, f_back in (("lectern", lec, 13, 46), ("table", tab, 36, None)):
        row = {f: (visible(blk.object, f), blk.stage_at(f), [visible(q, f) for q in blk.patches]) for f in
               (0, 1, 2, 7, 12, 13, 14, 23, 24, 35, 36, 45, 46, 47, 72, 73, 120)}
        print(name, row)
    ok("lectern: visible and stage 0 ON frame 1", visible(lec.object, 1) and lec.stage_at(1) == 0 and lec.stage_at(0) == -1)
    ok("lectern: stage 9 on 12, gone on 13, back uncracked on 46",
       lec.stage_at(12) == 9 and not visible(lec.object, 13) and visible(lec.object, 46) and lec.stage_at(46) == -1
       and not visible(lec.object, 45))
    ok("table (full cube): gone 36.., patches shown exactly then",
       visible(tab.object, 35) and not visible(tab.object, 36) and all(visible(q, 36) for q in tab.patches)
       and not any(visible(q, 35) for q in tab.patches) and tab.stats["patch_faces"] >= 3, str(tab.stats))
    nb = len([q for q in p["bursts"]["break_tab"].particles if q["spawn"] == 36.0 and q["first"] == 36])
    ok("full cube: 64 destroy particles", nb == 64, str(nb))
    n1 = len([q for q in p["bursts"]["break"].particles if q["spawn"] == 13.0 and q["first"] == 13])
    ok("lectern: 112 destroy particles", n1 == 112, str(n1))
    # outfits per frame, incl. Stage.finish visibility
    def worn(c, f):
        return sorted(prof for prof, obs in c.outfits.items() if all(visible(o, f) for o in obs)), \
            sorted(prof for prof, obs in c.outfits.items() if any(visible(o, f) for o in obs))
    rows = {f: (worn(lib, f), worn(fl, f)) for f in (0, 1, 18, 19, 41, 42, 55, 56, 72, 73, 120)}
    for f, r in rows.items():
        print("outfits", f, r)
    ok("lib: librarian, none 19..55, librarian from 56 (also after the cut)",
       worn(lib, 1)[1] == ["librarian"] and worn(lib, 19)[1] == ["none"] and worn(lib, 55)[1] == ["none"]
       and worn(lib, 56)[1] == ["librarian"] and worn(lib, 73)[1] == ["librarian"])
    ok("fl: hidden completely in shot 2 (not in st.use), plain from 42",
       worn(fl, 41)[1] == ["fletcher"] and worn(fl, 42)[1] == ["none"] and worn(fl, 73)[1] == [] and worn(fl, 120)[1] == [])
    # particle facing: quad +Z must equal camera +Z (the game: quad rotated by the camera rotation)
    dg = bpy.context.evaluated_depsgraph_get()
    worst = {}
    for f in (2, 8, 14, 20, 37, 58, 62, 72, 73, 80, 110):
        film.goto(f)
        scene.frame_set(f)
        dg = bpy.context.evaluated_depsgraph_get()
        cam = scene.camera.evaluated_get(dg)
        cz = (cam.matrix_world.to_3x3() @ Vector((0, 0, 1))).normalized()
        cy = (cam.matrix_world.to_3x3() @ Vector((0, 1, 0))).normalized()
        n_vis, w = 0, 1.0
        wy = 1.0
        for b in p["bursts"].values():
            for q in b.particles:
                ob = q["object"]
                if not visible(ob, f):
                    continue
                n_vis += 1
                m = ob.evaluated_get(dg).matrix_world.to_3x3()
                w = min(w, (m @ Vector((0, 0, 1))).normalized().dot(cz))
                wy = min(wy, (m @ Vector((0, 1, 0))).normalized().dot(cy))
        worst[f] = (n_vis, round(w, 5), round(wy, 5), scene.camera.name)
    print("particle facing (frame: visible, min dot z, min dot y, camera):", worst)
    ok("every visible particle faces the frame's camera (both shots, across the cut)",
       all(w[1] > 0.9999 and w[2] > 0.9999 for w in worst.values() if w[0]))
    ok("happy particles are alive on both sides of the cut", worst[72][0] >= 1 and worst[73][0] >= 1, str((worst[72], worst[73])))
    # Steve's arm during mining_swings: sample for jumps
    arm = steve.arm_r
    vals = []
    for i in range(0, 4 * 24 + 1):
        f = i / 4.0
        c = curve(arm, "rotation_euler", 0)
        vals.append((f, c.evaluate(f) if c else 0.0))
    steps = [(vals[i][0], vals[i][1] - vals[i - 1][1]) for i in range(1, len(vals))]
    big = max(steps, key=lambda t: abs(t[1]))
    print("steve arm_r rot x per frame 0..24:", [round(v, 2) for f, v in vals if abs(f - round(f)) < 1e-6])
    print("swings at", p["swings"], "largest quarter-frame step %.3f rad at %.2f" % (big[1], big[0]))
    ok("mining swing has no pop (quarter-frame step < 0.6 rad)", abs(big[1]) < 0.6, "%.3f at %.2f" % (big[1], big[0]))
    # book
    ok("book hidden before its shot, shown in it", not visible(book, 72) and visible(book, 73) and visible(book, 120)
       and not visible(book, 121))
    film.goto(100)
    scene.frame_set(100)
    dg = bpy.context.evaluated_depsgraph_get()
    bw = book.evaluated_get(dg).matrix_world
    pt = fx.held_item_point(lib, 100)
    feet = lib.pos_at(100)
    print("book centre %s vs held_item_point %s, feet %s" % (tuple(round(c, 3) for c in bw.translation),
                                                          tuple(round(c, 3) for c in pt), tuple(round(c, 3) for c in feet)))
    ok("book sits where held_item_point says", (bw.translation - pt).length < 1e-4)
    ok("book: 1.226 above the feet and 0.40 in front (independent calculation from CrossedArmsItemLayer)",
       abs(bw.translation.z - feet.z - 1.2264) < 0.01 and abs((bw.translation.y - feet.y) - 0.3997) < 0.02,
       "dz %.4f dy %.4f" % (bw.translation.z - feet.z, bw.translation.y - feet.y))
    # sprite normal: front (-Y local of the sprite) must face the customer (north = +Y world here)
    front = (bw.to_3x3() @ Vector((0, -1, 0))).normalized()
    right = (bw.to_3x3() @ Vector((1, 0, 0))).normalized()
    print("book front normal %s, sprite +u axis %s" % (tuple(round(c, 2) for c in front), tuple(round(c, 2) for c in right)))
    # glint called twice on one object, and on a second object
    m1 = book.data.materials[0]
    m2 = fx.glint(book, 73, 121)
    ok("glint() twice reuses the material", m1 is m2 and len([n for n in m2.node_tree.nodes if n.name.startswith("fx_glint")]) == 4)
    from engine import props

    em = props.make_item("emerald")
    em0 = em.data.materials[0]
    fx.glint(em, 80)
    ok("glint on a second item does not touch the first / the shared base material",
       em.data.materials[0] is not em0 and em.data.materials[0] is not m1 and not em0.get("fx_glint"))
    plain = props.make_item("enchanted_book")
    ok("a later plain enchanted_book still gets the un-glinted shared material",
       not plain.data.materials[0].get("fx_glint"), plain.data.materials[0].name)
    em.hide_render = plain.hide_render = True
    # API errors
    for label, fn, exc in (
            ("unknown kind", lambda: fx.emit("poof", (0, 0, 0), 5, camera=s), ValueError),
            ("air cell", lambda: fx.extract_block(p["v"], (-6, -30, 1)), ValueError),
            ("unknown anchor", lambda: fx.extract_block(p["v"], "no_such_anchor"), KeyError),
            ("break with f1 <= f0", lambda: fx.break_block(lec, 60, 60, camera=s), ValueError),
            ("unknown outfit", lambda: lib.set_profession(90, "farmer"), ValueError)):
        try:
            fn()
            ok("error: " + label, False, "no exception")
        except exc as e:
            ok("error: " + label, True, str(e)[:90])
        except Exception as e:                                  # noqa: BLE001
            ok("error: " + label, False, "%s: %s" % (type(e).__name__, e))
    ok("extract twice -> same Block", fx.extract_block(p["v"], "cell_1") is lec and fx.hall_job_block(p["v"], 1) is lec)
    # object counts
    n_fx = len([o for o in bpy.data.objects if o.name.startswith("fx_")])
    print("fx objects in the scene:", n_fx, "of", len(bpy.data.objects))
    print("[probe] %d failed%s" % (len(bad), ": " + "; ".join(bad) if bad else ""))
    return len(bad)


def main(argv):
    mode = argv[0] if argv else "check"
    bpy.ops.wm.read_factory_settings(use_empty=True)
    before = snapshot()
    import engine.fx as fx_mod                                  # noqa: F401

    after = snapshot()
    print("import engine.fx: datablocks before %s" % before)
    print("import engine.fx: datablocks after  %s -> %s" % (after, "UNTOUCHED" if before == after else "CHANGED"))
    from engine import look

    scene = bpy.context.scene
    look.setup_render(scene, res=(540, 960), samples=16, threads=2)
    t = time.time()
    p = build(scene, glint_strength=0.0 if mode == "noglint" else 1.0)
    print("[probe] built in %.1f s, frames %d-%d" % (time.time() - t, p["film"].frame_start, p["film"].frame_end))
    if mode == "check":
        return check(p)
    os.makedirs(OUT, exist_ok=True)
    if mode in ("render", "noglint"):
        tag = "" if mode == "render" else "noglint_"
        for a in argv[1:]:
            f = int(a)
            t = time.time()
            p["film"].goto(f)
            scene.render.filepath = os.path.join(OUT, "check_fx_%sf%03d.png" % (tag, f))
            bpy.ops.render.render(write_still=True)
            print("[probe] frame %d -> %s  %.1f s" % (f, scene.render.filepath, time.time() - t), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(1 if main(sys.argv[1:]) else 0)
