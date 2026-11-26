"""Checker probe for engine/music.py (written by the independent checker, not the module's author).

A film-like build of "The Crammys" beats staged ONLY from engine/music.py's docstring (BEATS section, PUBLIC API,
GOTCHAS), through films.lookdev.Stage with music.SKIES, rendered through the real look at 540x960, 16 samples, motion
blur on (look.setup_render default), 2 threads:

    $BPY -m tools.check_music_probe zones                 # no render: faces / hero props vs the Reels safe area
    $BPY -m tools.check_music_probe gold b1 b3 b6          # stills  -> out/test/check_music_<shot>.png
    $BPY -m tools.check_music_probe gold b5x               # action  -> out/test/check_music_b5x_<k>.png (5 frames)
    $BPY -m tools.check_music_probe night b8x              # action  -> out/test/check_music_b8x_<k>.png (5 frames)
"""
import math
import os
import sys
import time

import bpy
from mathutils import Vector

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "out", "test")
NIGHT = 1.3


def build(scene, sky=None):
    """The probe film (every shot in every build, as a multi-sky film must)."""
    from engine import look, music, players, shots, village
    from films.lookdev import Stage

    look.setup_render(scene, res=(540, 960), samples=16, threads=2)
    v = village.build_village(scene, seed=1, edit=music.crammys_set)
    bd = music.band(v)
    film = shots.Film(scene, fps=24)
    st = Stage(scene, film, v, skies=music.SKIES, sky=sky)
    P = {}

    def pl(name):
        if name not in P:
            P[name] = players.add_player(st, name, name)
        return P[name]

    def put(p, key, f0):
        p.place(f0, bd.A[key], bd.yaw.get(key, 0.0))
        for hand in ("right", "left"):                          # KEY HOLDS PER SHOT (docstring GOTCHAS)
            if p.holding_at(hand, f0) is not None:
                p.hold(None, hand=hand, frame=f0)
        return p

    def cam(s, c, moving=True, focus=None):
        s.lens(c["lens"], c["fstop"])
        if moving and ("pos1" in c or "target1" in c):
            s.move(c["pos"], c["target"], c.get("pos1", c["pos"]), c.get("target1", c["target"]))
        else:
            s.move(c["pos"], c["target"])
        s.focus(c["focus"] if focus is None else focus)

    info = {"heroes": {}, "still": {}, "frames": {}}

    # ---------------- beat 1 (gold) -----------------------------------------------------------------------------
    s = st.shot("b1", 2.5, sky="gold")
    f0, f1 = s.frame_start, s.frame_end
    steve = put(pl("steve"), "steve_front", f0)
    z, k, su, no = (put(pl(n), n, f0) for n in ("zuri", "kai", "sunny", "noor"))
    bd.tap("zuri", z, f0 + 6, camera=s)
    bd.tap("kai", k, f0 + 10, camera=s)
    bd.tap("sunny", su, f0 + 14, camera=s)
    music.hold(no, "goat_horn", frame=f0)
    no.toot(f0 + 4, f1)
    st.use(s, steve, z, k, su, no)
    cam(s, bd.cameras["b1"])
    bd.lights(st, s, scale=1.0)
    info["still"]["b1"] = f0 + 20
    info["heroes"]["b1"] = [("steve", steve.head), ("zuri", z.head), ("kai", k.head), ("sunny", su.head),
                            ("noor", no.head)]

    # ---------------- beat 3 (gold) -----------------------------------------------------------------------------
    s = st.shot("b3", 2.5)
    f0, f1 = s.frame_start, s.frame_end
    steve = put(pl("steve"), "steve_kai", f0)
    k = put(pl("kai"), "kai", f0)
    bd.notes["kai"].song(k, f0 + 6, count=3, every=12, camera=s)
    st.use(s, steve, k)
    cam(s, bd.cameras["b3"])
    s.focus(k.head, at_s=film.seconds(f0 + 30))
    bd.lights(st, s, scale=1.0)
    info["still"]["b3"] = f0 + 50
    info["heroes"]["b3"] = [("kai", k.head)]

    # ---------------- beat 5 (gold, action) ---------------------------------------------------------------------
    s = st.shot("b5x", 3.0)
    f0, f1 = s.frame_start, s.frame_end
    c5 = bd.cameras["b5"]
    t = bd.totem(f0, f1 + 1, face=c5["pos"])
    st.cast[t.name] = t
    a = put(pl("alex"), "alex_post", f0)
    music.hold(a, "lantern", frame=f0)
    lf = f0 + 50
    bd.last_lantern.place(lf, player=a)
    a.hold(None, frame=lf + 1)
    st.use(s, t, a)
    cam(s, c5)
    bd.lights(st, s, scale=1.0)
    info["frames"]["b5x"] = [f0 + 2, f0 + 24, lf - 1, lf + 4, f1]
    info["heroes"]["b5x"] = [("totem", t.sprite), ("alex", a.head)]

    # ---------------- beat 6 (gold) -----------------------------------------------------------------------------
    s = st.shot("b6", 3.0)
    f0, f1 = s.frame_start, s.frame_end
    c6 = bd.cameras["b6"]
    acts = (("zuri", "note_block"), ("noor", "goat_horn"), ("alex", "music_disc_cat"), ("sunny", "pumpkin"))
    line = []
    for i, (w, item) in enumerate(acts, 1):
        p = put(pl(w), "line_%d" % i, f0)
        music.hold(p, item, frame=f0)
        y = bd.A["line_%d" % i][1]
        music.present(p, f0, f1, (-13.0, y + 1.0, 1.5))
        line.append(p)
    steve = put(pl("steve"), "line_5", f0)
    st.use(s, steve, *line)
    cam(s, c6)
    if os.environ.get("CHECK_MUSIC_B6") == "noor":                 # a fixed focus on Noor's horn
        s.focus(line[1].item(frame=f0))
        info["still"]["b6n"] = f0 + 22
    else:
        for i, p in enumerate(line[1:] + [steve], 1):              # rack the focus along the line
            s.focus(p.head if p is steve else p.item(), at_s=film.seconds(f0 + 14 * i))
    bd.lights(st, s, scale=1.0)
    info["still"]["b6"] = f0 + 30
    info["heroes"]["b6"] = [("alex disc", line[2].item()), ("alex", line[2].head), ("noor", line[1].head)]

    # ---------------- beat 8 (night, action) --------------------------------------------------------------------
    s = st.shot("b8x", 3.0, sky="night")
    f0, f1 = s.frame_start, s.frame_end
    steve = put(pl("steve"), "steve_watch", f0)
    a = put(pl("alex"), "alex_eject", f0)
    z = put(pl("zuri"), "zuri", f0)                              # the docstring does not say where they stand
    k = put(pl("kai"), "kai", f0)
    ef = f0 + 16
    bd.jukebox.play(f0 - 30, ef, disc="music_disc_cat", camera=s)
    item = bd.jukebox.eject(ef, player=a, disc="music_disc_cat", camera=s, until=f1 + 1)
    st.cast[item.name] = item
    steve.look_at(ef + 2, item.root, ease=6)
    steve.look_at(ef + 40, (-16.0, -6.0, 1.6), ease=12)            # ... then away to the dark end of the square
    st.use(s, steve, a, z, k, item)
    cam(s, bd.cameras["b8"])
    s.focus(steve.head, at_s=film.seconds(ef + 40))
    bd.lights(st, s, scale=NIGHT)
    info["frames"]["b8x"] = [f0 + 8, ef + 4, ef + 12, ef + 30, f1 - 2]
    info["heroes"]["b8x"] = [("disc", item.sprite), ("steve", steve.head), ("alex", a.head)]

    # ---------------- beat 20 (night) ---------------------------------------------------------------------------
    s = st.shot("b20", 2.5)
    f0, f1 = s.frame_start, s.frame_end
    c20 = bd.cameras["b20"]
    steve = put(pl("steve"), "steve_jukebox", f0)
    a = put(pl("alex"), "alex_beside", f0)
    music.hold(steve, "music_disc_11", frame=f0)
    music.hold(a, "music_disc_cat", frame=f0)
    music.present(steve, f0, f0 + 36, c20["pos"])
    music.present(a, f0, f1, c20["pos"])
    bd.jukebox.insert(f0 + 44, player=steve, disc="music_disc_11", camera=s, until=f0 + 400)
    st.use(s, steve, a)
    cam(s, c20)
    bd.lights(st, s, scale=NIGHT)
    info["still"]["b20"] = f0 + 20
    info["heroes"]["b20"] = [("disc 11", steve.item(frame=f0 + 20)), ("cat", a.item(frame=f0 + 20)),
                             ("steve", steve.head)]

    # ---------------- beat 22 (night) ---------------------------------------------------------------------------
    s = st.shot("b22", 2.5)
    f0, f1 = s.frame_start, s.frame_end
    who = {"steve": "flank_s1", "zuri": "flank_n1", "kai": "flank_n2", "alex": "flank_n3", "sunny": "flank_s2",
           "noor": "flank_s3"}
    six = [put(pl(n), key, f0) for n, key in who.items()]
    st.use(s, *six)
    cam(s, bd.cameras["b22"])
    bd.lights(st, s, scale=NIGHT)
    info["still"]["b22"] = f0 + 20
    info["heroes"]["b22"] = [(p.name, p.head) for p in six]

    # ---------------- beat 23 (night) ---------------------------------------------------------------------------
    s = st.shot("b23", 2.5)
    f0, f1 = s.frame_start, s.frame_end
    six = {n: put(pl(n), key, f0) for n, key in who.items()}
    kai = six["kai"]
    st.use(s, *six.values())
    cam(s, bd.cameras["b23"])
    kai.look_at(f0 + 4, six["steve"], ease=8)
    for i, n in enumerate(("zuri", "sunny", "noor", "alex")):
        six[n].look_at(f0 + 14 + 6 * i, six["steve"], ease=6)
    bd.lights(st, s, scale=NIGHT)
    info["still"]["b23"] = f0 + 50
    info["heroes"]["b23"] = [(n, p.head) for n, p in six.items()]

    # ---------------- beat 24 (night) ---------------------------------------------------------------------------
    s = st.shot("b24", 3.0)
    f0, f1 = s.frame_start, s.frame_end
    c24 = bd.cameras["b24"]
    steve = put(pl("steve"), "steve_center", f0)
    music.hold(steve, "totem_of_undying", frame=f0)
    music.present(steve, f0, f1, c24["pos"])
    five = []
    for i, (n, key) in enumerate((("zuri", "flank_n1"), ("kai", "flank_n2"), ("alex", "flank_n3"),
                                  ("sunny", "flank_s2"), ("noor", "flank_s3"))):
        p = put(pl(n), key, f0)
        music.clap(p, f0 + 30 + 2 * i, count=6)
        five.append(p)
    st.use(s, steve, *five)
    cam(s, c24)
    s.focus(steve.item(frame=f0))
    bd.lights(st, s, scale=NIGHT)
    info["still"]["b24"] = f0 + 2
    info["still"]["b24e"] = f1 - 1
    info["heroes"]["b24"] = [("totem", steve.item(frame=f0)), ("steve", steve.head)]
    info["heroes"]["b24e"] = [(p.name, p.head) for p in [steve] + five]

    st.finish()
    return dict(film=film, stage=st, village=v, band=bd, info=info, players=P)


def zones(scene, film, info):
    """Project every hero point of every still; report what leaves x 8-82 %, y 14-60 %."""
    from bpy_extras.object_utils import world_to_camera_view

    bad = []
    for name, frame in sorted(info["still"].items(), key=lambda kv: kv[1]):
        film.goto(frame)
        cam = scene.camera
        dg = bpy.context.evaluated_depsgraph_get()
        row = []
        for label, ob in info["heroes"].get(name, []):
            if ob is None:
                row.append("%s: none" % label)
                continue
            ev = ob.evaluated_get(dg)
            if ev.type == "MESH" and len(ev.data.vertices):
                pts = [ev.matrix_world @ vt.co for vt in ev.data.vertices]
                c = sum(pts, Vector()) / len(pts)
            else:
                c = ev.matrix_world.translation
            p = world_to_camera_view(scene, cam, c)
            x, y = 100.0 * p.x, 100.0 * (1.0 - p.y)
            ok = 8 <= x <= 82 and 14 <= y <= 60 and p.z > 0
            row.append("%s %s(%.0f%%, %.0f%%)" % ("" if ok else "OUT", label, x, y))
            if not ok:
                bad.append((name, label, round(x), round(y)))
        print("[zones] %-5s f%-4d %s" % (name, frame, "  ".join(row)), flush=True)
    return bad


def render(scene, film, frame, path):
    film.goto(frame)
    tmp = path[:-4] + "_part"
    scene.render.filepath = tmp
    bpy.ops.render.render(write_still=True)
    os.replace(tmp + ".png", path)
    return path


def zones_author(sky):
    """The author's own proof shots (tools/music_proof.py): every player's face and every registered item at the
    proof frame, against the Reels safe area."""
    from tools import music_proof as mp

    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    b = mp.build(scene, sky, res=(540, 960), samples=1)
    film, st = b["film"], b["stage"]
    info = {"still": {}, "heroes": {}}
    for s in film.shots:
        fr = b["frames"].get(s.name)
        if not fr:
            continue
        info["still"][s.name] = fr[0]
        obs = []
        for n in sorted(st.in_shot.get(s.name, ())):
            c = st.cast[n]
            obs.append((n, getattr(c, "head", None) or getattr(c, "sprite", None)))
        info["heroes"][s.name] = obs
    return zones(scene, film, info)


def palette(sky, names):
    """tools.palette_check on stills already rendered by this probe (same build, same frames)."""
    from tools import palette_check as pc

    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    b = build(scene, sky)
    film, info = b["film"], b["info"]
    failed = 0
    for n in names:
        f = info["still"][n] if n in info["still"] else info["frames"][n.rsplit("_", 1)[0]][int(n.rsplit("_", 1)[1])]
        film.goto(f)
        rep = pc.evaluate(pc.probe(scene), os.path.join(OUT, "check_music_%s.png" % n))
        pc.print_report(n, rep)
        failed += len(rep["failed"])
    print("[palette] %d failed" % failed)


def main(argv):
    if argv and argv[0] == "palette":
        palette(argv[1], argv[2:])
        return 0
    if argv and argv[0] == "author":
        for sky in ("gold", "night"):
            print("[zones] author's shots, %s: outside %s" % (sky, zones_author(sky)))
        return 0
    sky = argv[0] if argv and argv[0] in ("gold", "night", "zones") else "gold"
    names = argv[1:] if argv and argv[0] in ("gold", "night") else []
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    t0 = time.time()
    b = build(scene, None if sky == "zones" else sky)
    print("[probe] built %s in %.1f s" % (sky, time.time() - t0), flush=True)
    film, info = b["film"], b["info"]
    if sky == "zones":
        bad = zones(scene, film, info)
        print("[zones] outside the safe area: %s" % bad)
        return 0
    os.makedirs(OUT, exist_ok=True)
    for n in names:
        t = time.time()
        if n in info["frames"]:
            for i, f in enumerate(info["frames"][n]):
                p = render(scene, film, f, os.path.join(OUT, "check_music_%s_%d.png" % (n, i)))
                print("[probe] %s f%d -> %s %.1f s" % (n, f, p, time.time() - t), flush=True)
                t = time.time()
        else:
            p = render(scene, film, info["still"][n], os.path.join(OUT, "check_music_%s.png" % n))
            print("[probe] %s f%d -> %s %.1f s" % (n, info["still"][n], p, time.time() - t), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
