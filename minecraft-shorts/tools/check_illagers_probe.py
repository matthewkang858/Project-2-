"""Checker probe (independent review of engine/illagers.py): a film-like build of "Leg Day" beats 15, 16, 19 and 20,
written from the module docstring only, run through render.py (--still) and audited for cut leaks.

    $BPY -m tools.check_illagers_probe audit                 build, then print what is visible in which shot
    $BPY -m tools.check_illagers_probe still 1.2,3.9         render.py --still at those seconds (540x960, 16 spp, mb)

The film is registered in-process as films.check_illagers_probe (no file is written under films/).
"""
import math
import sys
import types

NAME = "check_illagers_probe"
INFO = {}


def _hook(b):
    """Cobblestone strip on the exit road (x -1..1, y 26..46), and a shelf of 12 planks + anvils 18 above it."""
    from engine import fixtures

    b.allow((-2, 25, 2, 47))
    for x in range(-1, 2):
        for y in range(26, 47):
            g = b.ground(x + 0.5, y + 0.5)
            if g is None:
                continue
            b.clear_plants(x, y)
            b.w.set(x, y, int(round(g)) - 1, "cobblestone")
            b.reserved.add((x, y))
    INFO["planks"] = [fixtures.block(b, "oak_planks", (0, y, 17)) for y in range(30, 42)]
    INFO["anvils"] = fixtures.shelf(b, [(0, y, 18) for y in range(30, 42)], "anvil", {"facing": "east"})


def build(scene):
    from engine import fixtures, illagers, look, shots, village
    from films.lookdev import Stage

    INFO.clear()
    v = village.build_village(scene, seed=1, edit=_hook)
    sky = look.set_time(scene, "golden", sun_azimuth=62.0, sun_elevation=27.0)
    look.setup_compositor(scene, bloom=1.0, grade="warm")
    film = shots.Film(scene, fps=24)
    st = Stage(scene, film, v, sky)
    scene.render.resolution_x, scene.render.resolution_y = 540, 960
    scene.cycles.samples = 16

    patrol = illagers.add_patrol(st, 5, prefix="pillager")

    # ---- beat 15: five pillagers walk up the road toward the lens, in single file, captain in front
    s1 = st.shot("patrol", 2.0)
    end1 = illagers.march(patrol, [(0.5, 42.0, 0.0), (0.5, 30.0, 0.0)], s1.frame_start)
    st.use(s1, *patrol)
    st.hero(s1, "captain", patrol[0])
    s1.lens(85, 3.2)
    s1.move((0.9, 21.0, 0.45), (0.5, 40.0, 1.6))
    s1.focus(patrol[0].head)
    st.lights(s1, 1.0)

    # ---- beat 16: three arrows thud into the road in front of the runners (shooters off screen)
    s2 = st.shot("arrows", 1.5)
    arrows = []
    for i, (x, y) in enumerate(((0.2, 29.0), (0.9, 29.6), (0.4, 30.3))):
        a = illagers.shoot_arrow((0.5 + 0.3 * i, 45.0, 1.55), (x, y, 0.0), s2.frame_start + 6 + 4 * i, name="probe_arrow_%d" % i)
        st.cast[a.name] = a
        arrows.append(a)
    st.use(s2, *arrows)
    s2.lens(35, 4.0)
    s2.move((-2.5, 25.5, 0.6), (0.6, 30.0, 0.3))
    s2.focus((0.5, 29.6, 0.2))
    st.lights(s2, 1.0)

    # ---- beat 19: the file marches under the shelf; the anvils fall; each flashes red, tips over, puffs away
    s3 = st.shot("drop", 4.0)
    f0 = s3.frame_start
    end3 = illagers.march(patrol, [(0.5, 35.6, 0.0), (0.5, 24.0, 0.0)], f0)
    st.use(s3, *patrol)
    st.hero(s3, "captain", patrol[0])
    f_rel = f0 + 12
    for p in INFO["planks"]:
        p.remove(f_rel)
    drops = fixtures.release(INFO["anvils"], f_rel, world=v, chip=list(range(0, 12, 2)))
    patrol[0].look_at(f_rel + 2, (0.5, 33.0, 18.0), ease=6)               # the captain tips his head up
    hits = fixtures.strikes(drops, {p.name: p.pos_at(drops[0]["frame_land"]) for p in patrol})
    import os
    cam3 = (3.8, 27.0, 0.5) if os.environ.get("CHECK_ILL_EAST") else (-2.6, 26.5, 0.5)
    results = {}
    for p in patrol:
        if p.name not in hits:
            print("[probe] %s is under no anvil" % p.name)
            continue
        spots = [(1.45, 31.2, 0.0), (1.45, 32.0, 0.0)] if p.captain else None
        results[p.name] = illagers.crushed_by(p, hits[p.name]["drop"], camera=s3, stage=st, knockback=False, village=v,
                                              spots=spots, face=cam3)
    for blk in INFO["anvils"] + INFO["planks"]:
        st.cast[blk.name] = blk
        st.use(s3, blk)
    s3.lens(24, 4.0)
    s3.move(cam3, (0.5, 36.0, 4.0))
    s3.focus((0.5, 33.0, 1.2))
    st.lights(s3, 1.0)

    # ---- beat 20 (a new shot): banner and bottle turn among the anvils (docstring: add_dropped_banner / _bottle)
    s4 = st.shot("loot", 2.0)
    g0 = s4.frame_start
    banner = illagers.add_dropped_banner(st)
    bottle = illagers.add_dropped_bottle(st)
    cam4 = (3.6, 29.6, 0.55)
    banner.place(g0, (1.45, 32.0, 0.0))
    bottle.place(g0, (1.45, 31.2, 0.0))
    banner.face(g0 + 20, cam4)
    bottle.face(g0 + 20, cam4)
    banner.animate(g0, s4.frame_end + 10)
    bottle.animate(g0, s4.frame_end + 10)
    st.use(s4, banner, bottle, *[b for b in INFO["anvils"]])
    s4.lens(50, 3.2)
    s4.move(cam4, (1.4, 31.6, 0.25), (3.0, 30.2, 0.45), (1.4, 31.6, 0.25))
    s4.focus((1.45, 31.6, 0.25))
    st.lights(s4, 1.0)
    st.finish()
    INFO.update(st=st, v=v, patrol=patrol, arrows=arrows, drops=drops, hits=hits, results=results, banner=banner,
                bottle=bottle, shots=(s1, s2, s3, s4), f_rel=f_rel, end1=end1, end3=end3)
    print("[probe] shots: " + ", ".join("%s %d-%d" % (s.name, s.frame_start, s.frame_end) for s in (s1, s2, s3, s4)))
    print("[probe] release %d, land %s" % (f_rel, sorted({d["frame_land"] for d in drops})))
    for n, r in results.items():
        print("[probe] %s: frame %d damage %.1f lethal %s gone %s items %s" % (n, r["frame"], r["damage"], r["lethal"], r["gone"],
                                                                                [it.name for it in r["items"]]))
    return {"film": film, "captions": [], "stage": st}


def register():
    mod = types.ModuleType("films." + NAME)
    mod.build = build
    mod.__file__ = __file__
    sys.modules["films." + NAME] = mod
    import films
    setattr(films, NAME, mod)


def _visible(obs):
    return [o.name for o in obs if not o.hide_render]


def audit():
    import bpy

    import render
    from engine import illagers

    register()
    ses = render.Session(NAME)
    scene = ses.scene
    s1, s2, s3, s4 = INFO["shots"]
    patrol = INFO["patrol"]
    cap = patrol[0]
    groups = {}
    for p in patrol:
        groups[p.name] = p.objects() + list(illagers.twins_of(p).values())
    for r in INFO["results"].values():
        for it in r["items"]:
            groups[it.name] = [it.root, it.spinner] + list(it.copies)
    for a in INFO["arrows"]:
        groups[a.name] = [a.object]
    groups["dropped_banner"] = list(INFO["banner"].copies)
    groups["dropped_bottle"] = list(INFO["bottle"].copies)
    poof = [o for o in bpy.data.objects if o.name.startswith("undead_poof")]
    groups["poof"] = poof
    rows = []
    for s in (s1, s2, s3, s4):
        for f in (s.frame_start, (s.frame_start + s.frame_end) // 2, s.frame_end):
            scene.frame_set(f)
            vis = {k: len(_visible([o for o in obs if o.type == "MESH"])) for k, obs in groups.items()}
            rows.append((s.name, f, {k: n for k, n in vis.items() if n}))
    for name, f, vis in rows:
        print("AUDIT %-7s %4d %s" % (name, f, vis))
    # who is where on the landing frame, and the order of events
    for p in patrol:
        r = INFO["results"].get(p.name)
        print("POS %s at release %s at hit %s" % (p.name, tuple(round(c, 2) for c in p.pos_at(INFO["f_rel"])),
                                                 tuple(round(c, 2) for c in p.pos_at(r["frame"])) if r else None))
    print("captain banner on head at hit-1 / hit: %s / %s" % (cap.wears_banner_at(INFO["results"][cap.name]["frame"] - 1),
                                                           cap.wears_banner_at(INFO["results"][cap.name]["frame"])))
    print("crossbow states: %s" % sorted({p.crossbow_at(f) for p in patrol for f in range(1, s4.frame_end)}))
    return ses


def still(seconds):
    import render

    register()
    return render.main([NAME, "--still", seconds])


if __name__ == "__main__":
    what = sys.argv[1] if len(sys.argv) > 1 else "audit"
    if what == "audit":
        audit()
    elif what == "still":
        sys.exit(still(sys.argv[2]) or 0)
    else:
        raise SystemExit("use: audit | still S[,S...]")
