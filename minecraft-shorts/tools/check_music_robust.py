"""Checker probe for engine/music.py (independent checker): robustness without rendering.

    $BPY -m tools.check_music_robust import       # importing engine.music leaves a scene untouched
    $BPY -m tools.check_music_robust twice        # two builds in one process; band(v) twice; set vs plain village
    $BPY -m tools.check_music_robust cuts         # what of the module stays visible in shots it is not used in
    $BPY -m tools.check_music_robust films NAME.. # finished films still build (render.Session, first sky)
"""
import math
import sys

import bpy


def _counts():
    return {k: len(getattr(bpy.data, k)) for k in ("objects", "meshes", "materials", "images", "collections",
                                                   "lights", "node_groups", "actions")}


def cmd_import():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    before = _counts()
    import engine.music  # noqa: F401
    after = _counts()
    print("[robust] import: before %s after %s -> %s" % (before, after, "SAME" if before == after else "CHANGED"))


def _blocks(w):
    out = {}
    for c in w.blocks:
        bid, props = w.get(*c)
        out[c] = (bid, tuple(sorted((props or {}).items())))
    return out


def _build(seed=1, edit=None):
    from engine import quick, village

    scene = quick.reset()
    quick.setup(scene, res=(270, 480), samples=1)
    return scene, village.build_village(scene, seed=seed, edit=edit)


def cmd_twice():
    from engine import music

    _s, v1 = _build(edit=music.crammys_set)
    b1 = _blocks(v1.world)
    a1 = dict(v1.anchors)
    n_obj1 = len(bpy.data.objects)
    bd = music.band(v1)
    n_after_band = len(bpy.data.objects)
    bd2 = music.band(v1)
    n_after_band2 = len(bpy.data.objects)
    lant = [o.name for o in bpy.data.objects if "last_lantern" in o.name]
    print("[robust] band(v) twice on one village: objects %d -> %d -> %d; last-lantern objects %s"
          % (n_obj1, n_after_band, n_after_band2, lant))
    _s, v2 = _build(edit=music.crammys_set)
    b2 = _blocks(v2.world)
    print("[robust] two builds in one process: blocks equal %s (%d cells), anchors equal %s"
          % (b1 == b2, len(b1), dict(v2.anchors) == a1))
    _s, v0 = _build(edit=None)
    b0 = _blocks(v0.world)
    diff = sorted(set(b0) ^ set(b2) | {k for k in set(b0) & set(b2) if b0[k] != b2[k]})

    def in_set(c):
        x, y = c[0], c[1]
        return (-10 <= x <= -4 and -5 <= y <= 7) or (x, y) in ((1, 15), (1, 17))

    outside = [c for c in diff if not in_set(c)]
    print("[robust] set village vs plain village: %d cells differ, %d outside the bandstand / doorstep footprint"
          % (len(diff), len(outside)))
    for c in outside[:40]:
        print("   ", c, b0.get(c), "->", b2.get(c))
    moved = {k: (tuple(round(x, 2) for x in v0.anchors[k]), tuple(round(x, 2) for x in v2.anchors[k]))
             for k in v0.anchors if k in v2.anchors and math.dist(v0.anchors[k], v2.anchors[k]) > 1e-6}
    print("[robust] village anchors that moved: %s" % moved)
    pchg = [k for k in v0.paths if k in v2.paths and [tuple(p) for p in v0.paths[k]] != [tuple(p) for p in v2.paths[k]]]
    print("[robust] village paths that changed: %s" % pchg)
    l0 = sorted((round(o.location.x, 2), round(o.location.y, 2), round(o.location.z, 2)) for o in v0.lantern_lights)
    l2 = sorted((round(o.location.x, 2), round(o.location.y, 2), round(o.location.z, 2)) for o in v2.lantern_lights)
    print("[robust] lights: plain %d, with set %d; plain lights missing with the set: %s"
          % (len(l0), len(l2), [p for p in l0 if p not in l2]))


def cmd_cuts():
    """Two shots: A at the bandstand uses the module's things, B is elsewhere and uses none. What renders in B?"""
    from engine import look, music, players, shots, village
    from films.lookdev import Stage

    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    look.setup_render(scene, res=(270, 480), samples=1, threads=2)
    v = village.build_village(scene, seed=1, edit=music.crammys_set)
    bd = music.band(v)
    film = shots.Film(scene, fps=24)
    st = Stage(scene, film, v, skies=music.SKIES, sky="night")
    a = st.shot("a", 2.0, sky="night")
    b = st.shot("b", 2.0)
    alex = players.add_player(st, "alex", "alex")
    alex.place(a.frame_start, bd.A["alex_eject"], bd.yaw["alex_eject"])
    bd.jukebox.play(a.frame_start, a.frame_end - 2, camera=a)
    item = bd.jukebox.eject(a.frame_end - 20, player=alex, camera=a)          # NOT registered with the Stage
    tot = bd.totem(a.frame_start, a.frame_end)                                # NOT registered with the Stage
    bd.notes["zuri"].tap(None, a.frame_end - 3, camera=a)                     # a note that crosses the cut
    st.use(a, alex)
    a.move((-12.0, 0.5, 2.5), (-6.5, 0.5, 2.0))
    b.move((5.0, 30.0, 2.0), (0.0, 40.0, 1.0))
    bd.lights(st, a, scale=1.3)
    st.lights(b, scale=1.3)
    st.finish()
    for f in (1, a.frame_start, a.frame_end, b.frame_start, b.frame_start + 2, b.frame_end):
        scene.frame_set(f)
        seen = []
        for ob in bpy.data.objects:
            if ob.type in ("MESH", "LIGHT") and not ob.hide_render and (
                    ob.name.startswith(("music_", "light_music", "drop_music", "proof_")) or "music_disc" in ob.name
                    or "totem" in ob.name):
                seen.append(ob.name)
        print("[robust] frame %4d (%s): music things rendered: %s"
              % (f, "shot a" if f <= a.frame_end else "shot b", sorted(seen)[:12] + (["..."] if len(seen) > 12 else [])))
    print("[robust] last lantern light energy at b: %.1f W hidden %s"
          % (bd.last_lantern.light.data.energy, bd.last_lantern.light.hide_render))


def cmd_films(names):
    import importlib
    import time

    import render

    for n in names:
        t = time.time()
        try:
            s = render.Session(n)
            print("[robust] film %s builds: %d shots, frames %d-%d (%.1f s)" % (
                n, len(s.film.shots), s.scene.frame_start, s.scene.frame_end, time.time() - t), flush=True)
        except Exception as e:  # noqa: BLE001
            print("[robust] film %s FAILED: %r" % (n, e), flush=True)
        importlib.invalidate_caches()


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "import"
    if cmd == "import":
        cmd_import()
    elif cmd == "twice":
        cmd_twice()
    elif cmd == "cuts":
        cmd_cuts()
    elif cmd == "films":
        cmd_films(sys.argv[2:])
