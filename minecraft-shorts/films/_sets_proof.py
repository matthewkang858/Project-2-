"""Proof stills for engine/sets.py: the set of "The Hello" (hello_set) in the real village, cast and look.

Not a film: one 1-second shot per still, golden hour (the look-dev sun, azimuth 62, elevation 27); the night
still is films/_sets_proof_night.py (a module has one sky).

    $BPY -m engine.sets gate gap            # -> out/test/sets_gate.png, sets_gap.png (540x960, 16 samples, 2 threads)
    $BPY -m engine.sets night               # the forest edge under the look-dev moon
    $BPY -m engine.sets map                 # top-down map of the changed area with anchors and paths
    $BPY -m render _sets_proof --still 0.5  # any render.py action works on it too

    gate      beat 6   the road from the exit gate, the forest wall across its end, the baby villager in the
                       foreground, Steve in diamond armor walking away
    gap       beat 7   the same frame: a small figure standing at the gap, bare arms and head
    side      beat 8   the tree line from the side on the road, the child three blocks short of him
    inside             from inside the forest, out along the corridor to the meadow and the village
    floating  beat 12  the floating oak, the baby villager under it, against the sky
    bare      beat 13  the three bare oaks, a figure among them from behind, the village roofs beyond
    pyramid   beat 14  the sand pyramid, the baby villager beside it, the bare trunks behind
"""
import os
import sys

from engine import look, sets, shots, village
from films.lookdev import Stage, up, yaw_to

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKY = dict(preset="golden", az=62.0, el=27.0, bloom=1.0, grade="warm")
PROOF = ["gate", "gap", "side", "inside", "floating", "bare", "pyramid"]
NIGHT = ["night"]
STILL_AT = 0.5                      # seconds into each 1-second shot
FOREST_OPTIONS = {}                 # keyword arguments for sets.dark_forest in these stills (default: none)


def _player(st, name, skin="steve"):
    """A player through engine.players if it loads, else the old rig."""
    try:
        from engine import players

        return players.add_player(st, name, skin)
    except Exception as e:                                   # noqa: BLE001 - another agent may be editing it
        print("[sets proof] engine.players not usable (%s): using characters.make_player" % e)
        return st.actor(name, "steve")


def _cam(s, cam, focus=None):
    s.lens(cam["lens"], cam.get("fstop", 4.0))
    s.move(cam["pos"], cam["target"])
    s.focus(focus if focus is not None else cam["target"])


def shot_gate(st, s, hello):
    """Beat 6: the exit gate, low; the child in the foreground on the last full path block, three-quarter from
    behind; Steve in his best armor half way down the road, walking at the forest."""
    f0 = s.frame_start
    kid = st.actor("kid", "farmer", child=True)
    steve = _player(st, "steve")
    try:
        from engine import players

        players.equip(steve, "diamond", enchanted=True)
        steve.hold("diamond_sword")
    except Exception as e:                                   # noqa: BLE001
        print("[sets proof] no armor:", e)
    road = st.v.paths["road_to_forest"]
    steve.place(f0 - 150, road[0], yaw_to(road[0], road[1]))
    steve.walk(f0 - 150, road, speed=3.2)
    spot = (0.15, 26.6, st.v.ground(0, 26) - 0.0625)
    kid.place(f0, spot, yaw_to(spot, (2.2, 40.0)))
    kid.look_at(f0, steve, ease=0)
    st.use(s, kid, steve)
    _cam(s, hello["cameras"]["gate"], kid.head)
    st.hero(s, "child", kid)
    st.lights(s, scale=1.0, near=st.v.anchors["exit_gate"], radius=14.0)


def shot_gap(st, s, hello):
    """Beat 7: the identical frame; the road is empty, one figure in the plain teal shirt stands at the gap."""
    f0 = s.frame_start
    kid = st.actor("kid2", "farmer", child=True)
    him = _player(st, "watcher")
    gap = st.v.anchors["forest_gap"]
    him.place(f0, gap, st.v.yaws["forest_gap"])
    spot = (0.15, 26.6, st.v.ground(0, 26) - 0.0625)
    kid.place(f0, spot, yaw_to(spot, (2.2, 40.0)))
    kid.look_at(f0, up(gap, 3.0), ease=0)
    st.use(s, kid, him)
    _cam(s, hello["cameras"]["gate"], kid.head)
    st.hero(s, "child", kid)
    st.lights(s, scale=1.0, near=st.v.anchors["exit_gate"], radius=14.0)


def shot_side(st, s, hello):
    """Beat 8: the road from the side at child height; the child three blocks short of him, head tipped back."""
    f0 = s.frame_start
    kid = st.actor("kid3", "farmer", child=True)
    him = _player(st, "watcher2")
    gap = st.v.anchors["forest_gap"]
    him.place(f0, gap, st.v.yaws["forest_gap"])
    spot = (gap[0], gap[1] - 3.0, gap[2])
    kid.place(f0, spot, yaw_to(spot, gap))
    kid.look_at(f0, him, ease=0)
    st.use(s, kid, him)
    _cam(s, hello["cameras"]["side"], kid.head)
    st.hero(s, "child", kid)
    st.lights(s, scale=0.0)


def shot_inside(st, s, hello):
    """From inside the wood: the corridor, the gap between the two trunks, the meadow and the village in the light."""
    f0 = s.frame_start
    kid = st.actor("kid4", "farmer", child=True)
    spot = st.v.anchors["forest_approach"]
    kid.place(f0, spot, st.v.yaws["forest_approach"])
    st.use(s, kid)
    _cam(s, hello["cameras"]["inside"], kid.head)
    st.lights(s, scale=0.0)


def shot_floating(st, s, hello):
    """Beat 12: the canopy and its two logs hang in the air; the child stands in the gap underneath, looking up."""
    f0 = s.frame_start
    kid = st.actor("kid5", "farmer", child=True)
    fl = hello["floating"]
    cam = hello["cameras"]["floating"]
    spot = (fl["under"][0] + 0.2, fl["under"][1] - 1.0, fl["under"][2])
    kid.place(f0, spot, yaw_to(spot, (cam["pos"][0], cam["pos"][1] + 5.0)))
    kid.look_at(f0, fl["canopy"], ease=0)
    st.use(s, kid)
    _cam(s, cam, kid.head)
    st.hero(s, "child", kid)
    st.lights(s, scale=0.0)


def shot_bare(st, s, hello):
    """Beat 13: three leafless oaks; he stands among them with his back to the camera, facing the village; the
    child small at the edge of the frame, nose in profile, looking at him."""
    f0 = s.frame_start
    kid = st.actor("kid6", "farmer", child=True)
    him = _player(st, "watcher3")
    ba = hello["bare"]
    cam = hello["cameras"]["bare"]
    him.place(f0, ba["among"], st.v.yaws["bare_oaks_among"])
    spot = (ba["among"][0] + 2.3, ba["among"][1] + 2.4, st.v.ground(ba["among"][0] + 2.3, ba["among"][1] + 2.4))
    kid.place(f0, spot, yaw_to(spot, (ba["among"][0] - 2.0, ba["among"][1] + 2.0)))
    kid.look_at(f0, him, ease=0)
    st.use(s, kid, him)
    _cam(s, cam, him.head)
    st.hero(s, "watcher", him)
    st.lights(s, scale=0.0)


def shot_pyramid(st, s, hello):
    """Beat 14: the three-layer sand pyramid on the grass, taller than the child, the bare trunks behind it."""
    f0 = s.frame_start
    kid = st.actor("kid7", "farmer", child=True)
    py = hello["pyramid"]
    cam = hello["cameras"]["pyramid"]
    spot = (py["sides"]["west"][0] - 0.4, py["sides"]["west"][1] - 1.9, py["sides"]["west"][2])
    kid.place(f0, spot, yaw_to(spot, (spot[0] + 1.0, spot[1] + 3.0)))
    kid.look_at(f0, py["top"], ease=0)
    st.use(s, kid)
    _cam(s, cam, kid.head)
    st.hero(s, "child", kid)
    st.lights(s, scale=0.0)


def shot_night(st, s, hello):
    """The forest edge at night, from the road 14 blocks out: the gap, a figure at it, the moonlit meadow."""
    f0 = s.frame_start
    him = _player(st, "watcher_n")
    gap = st.v.anchors["forest_gap"]
    him.place(f0, gap, st.v.yaws["forest_gap"])
    st.use(s, him)
    _cam(s, dict(pos=(gap[0] - 2.4, gap[1] - 15.0, 0.9), target=(gap[0] + 0.6, gap[1], 3.4), lens=28.0, fstop=4.0),
         him.head)
    st.lights(s, scale=0.0)


BUILDERS = {"gate": shot_gate, "gap": shot_gap, "side": shot_side, "inside": shot_inside, "floating": shot_floating,
            "bare": shot_bare, "pyramid": shot_pyramid, "night": shot_night}


def build_film(scene, names, sky, with_set=True):
    """The village with (or, for the stamp check, without) hello_set and one shot per name."""
    out = {}
    kw = FOREST_OPTIONS                                    # (a place to try dark_forest options from the command line)
    v = village.build_village(scene, seed=1,
                              edit=(lambda b: out.update(hello=sets.hello_set(b, forest=kw))) if with_set else None)
    sk = look.set_time(scene, sky["preset"], sun_azimuth=sky["az"], sun_elevation=sky["el"])
    look.setup_compositor(scene, bloom=sky["bloom"], grade=sky["grade"])
    film = shots.Film(scene, fps=24)
    st = Stage(scene, film, v, sk)
    if with_set:
        for n in names:
            BUILDERS[n](st, st.shot(n, 1.0), out["hello"])
    else:
        for n in names:
            s = st.shot(n, 1.0)
            s.lens(32, 4.0)
            s.move((0.9, 22.6, 0.75), (0.5, 58.0, 2.6))
            s.focus((0.5, 40.0, 1.0))
    st.finish()
    return {"film": film, "captions": [], "stage": st, "hello": out.get("hello")}


def build(scene):
    """`$BPY -m render _sets_proof ...`: the golden-hour proof shots."""
    return build_film(scene, PROOF, SKY)


def still_frame(film, name):
    """Frame of the proof still of shot `name`."""
    shot = next(s for s in film.shots if s.name == name)
    return shot.frame_start + int(round(STILL_AT * film.fps))


def render_map(path, half=44.0, center=(0.0, 52.0)):
    """Top-down orthographic map of the changed area with the set's anchors and paths drawn in."""
    import bpy
    from PIL import Image, ImageDraw

    from engine import quick

    scene = quick.reset()
    quick.setup(scene, res=(1080, 1080), samples=8)
    out = {}
    v = village.build_village(scene, seed=1, edit=lambda b: out.update(hello=sets.hello_set(b)))
    quick.light(scene, "day")
    cam = bpy.data.cameras.new("map")
    cam.type = "ORTHO"
    cam.ortho_scale = half * 2
    ob = bpy.data.objects.new("map", cam)
    ob.location = (center[0], center[1], 150.0)
    scene.collection.objects.link(ob)
    scene.camera = ob
    tmp = quick.render(scene, "sets_map")
    img = Image.open(tmp).convert("RGB")
    d = ImageDraw.Draw(img)
    k = 1080 / (half * 2)

    def px(p):
        return ((p[0] - center[0] + half) * k, (half - (p[1] - center[1])) * k)

    for name, pts in v.paths.items():
        new = name in ("road_to_forest", "pyramid_round")
        d.line([px(p) for p in pts], fill=(255, 60, 60) if new else (255, 170, 170), width=3 if new else 1)
    for name, p in v.anchors.items():
        if not name.startswith(("forest", "floating", "bare", "pyramid", "exit_gate", "meadow_far")):
            continue
        x, y = px(p)
        d.ellipse([x - 4, y - 4, x + 4, y + 4], fill=(255, 255, 0), outline=(0, 0, 0))
        d.text((x + 6, y - 6), name, fill=(255, 255, 255), stroke_width=2, stroke_fill=(0, 0, 0))
    for name, c in out["hello"]["cameras"].items():
        x, y = px(c["pos"])
        tx, ty = px(c["target"])
        d.line([(x, y), (x + (tx - x) * 0.25, y + (ty - y) * 0.25)], fill=(80, 200, 255), width=2)
        d.rectangle([x - 4, y - 4, x + 4, y + 4], fill=(80, 200, 255), outline=(0, 0, 0))
        d.text((x + 6, y + 4), "cam " + name, fill=(160, 230, 255), stroke_width=2, stroke_fill=(0, 0, 0))
    for y in range(int(center[1] - half) // 10 * 10, int(center[1] + half) + 1, 10):
        d.text((4, px((0, y))[1] - 6), "y %d" % y, fill=(255, 255, 255), stroke_width=2, stroke_fill=(0, 0, 0))
    for x in range(int(center[0] - half) // 10 * 10, int(center[0] + half) + 1, 10):
        d.text((px((x, 0))[0] - 8, 1062), "x %d" % x, fill=(255, 255, 255), stroke_width=2, stroke_fill=(0, 0, 0))
    img.save(path)
    print("[sets proof] wrote", path, "edit problems:", v.edit_problems, "validate:", v.validate())
    return path


def main(names, res=(540, 960), samples=16, threads=2):
    """Render the named proof stills to out/test/sets_<name>.png ('all' = every one, 'map' = the top-down map)."""
    import time

    import render as R

    if "all" in names:
        names = PROOF + NIGHT + ["map"]
    out_dir = os.path.join(ROOT, "out", "test")
    if "map" in names:
        render_map(os.path.join(out_dir, "sets_map.png"))
    for module, group in (("_sets_proof", PROOF), ("_sets_proof_night", NIGHT)):
        wanted = [n for n in names if n in group]
        if not wanted:
            continue
        ses = R.Session(module)
        ses.configure(res, samples, threads, None)
        for n in wanted:
            t = time.time()
            path = os.path.join(out_dir, "sets_%s.png" % n)
            ses.render_frame(still_frame(ses.film, n), path)
            print("[sets proof] %-9s -> %s  %.1f s" % (n, path, time.time() - t), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:] or ["all"]))
