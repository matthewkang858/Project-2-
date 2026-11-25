"""Independent checker probe: a small film on the set of "The Hello", through the real village, cast and look.

    $BPY -m tools.check_sets_film <variant> <frames...>      -> out/test/check_sets_<variant>_f<frame>.png (540x960, 16 spp)
    $BPY -m tools.check_sets_film <variant> info             positions per frame, no render

variants: film (default sky), south (sun azimuth 230), haze0 (haze off), moody (dark_forest brightness 0),
          night, night0 (night, haze off), plain (village without the set, same cameras)
Shots (24 fps): walkin 1-72 (gate camera; Steve in diamond walks the end of road_to_forest and is hidden at the end),
side 73-120 (side camera; the child runs up and stops 3 short of the watcher), round 121-192 (pyramid camera; the
child walks pyramid_round), under 193-216 (floating oak), deep 217-240 (inside the wood, looking further in),
edge 241-264 (close on the tree line: trunk, leaves, grass, mushrooms).
"""
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VARIANT = {"name": "film"}
PROBE_SKY = {
    "film": dict(preset="golden", az=62.0, el=27.0, bloom=1.0, grade="warm"),
    "south": dict(preset="golden", az=230.0, el=27.0, bloom=1.0, grade="warm"),
    "haze0": dict(preset="golden", az=62.0, el=27.0, bloom=1.0, grade="warm", haze=0.0),
    "moody": dict(preset="golden", az=62.0, el=27.0, bloom=1.0, grade="warm"),
    "night": dict(preset="night", az=176.0, el=21.0, bloom=1.3, grade="cool"),
    "night0": dict(preset="night", az=176.0, el=21.0, bloom=1.3, grade="cool", haze=0.0),
    "plain": dict(preset="golden", az=62.0, el=27.0, bloom=1.0, grade="warm"),
    "noshade": dict(preset="golden", az=62.0, el=27.0, bloom=1.0, grade="warm"),
    "float3": dict(preset="golden", az=62.0, el=27.0, bloom=1.0, grade="warm"),
    "float4": dict(preset="golden", az=62.0, el=27.0, bloom=1.0, grade="warm"),
}
INFO = {}


def build(scene):
    from engine import look, players, sets, shots, village
    from films.lookdev import Stage, up, yaw_to

    name = VARIANT["name"]
    sky = PROBE_SKY[name]
    out = {}
    fk = {"brightness": 0.0} if name == "moody" else ({"shade": False, "biome": False} if name == "noshade" else {})

    def edit(b):
        if name in ("float3", "float4"):
            # what a director must do to get another floating oak: hello_set has no argument for it
            L = dict(sets.HELLO)
            forest = sets.dark_forest(b, gap=L["forest_gap"], keep_clear=[(L["floating"][0], L["floating"][1], 13.0)])
            fl = sets.floating_oak(b, b.tree_at(*L["floating"], radius=1.5) or L["floating"], logs=3 if name == "float3" else 4)
            bare = sets.bare_oaks(b, L["bare"])
            py = sets.sand_pyramid(b, L["pyramid"])
            res = dict(forest=forest, floating=fl, bare=bare, pyramid=py)
            res["cameras"] = sets.hello_cameras(res)
            sets.clear_view(b, res["cameras"]["floating"]["pos"], res["cameras"]["floating"]["target"], 2.2)
            out["hello"] = res
        else:
            out["hello"] = sets.hello_set(b, forest=fk)

    v = village.build_village(scene, seed=1, edit=None if name == "plain" else edit)
    kw = {}
    sk = look.set_time(scene, sky["preset"], sun_azimuth=sky["az"], sun_elevation=sky["el"])
    if "haze" in sky:
        kw["haze"] = sky["haze"]
    look.setup_compositor(scene, bloom=sky["bloom"], grade=sky["grade"], **kw)
    film = shots.Film(scene, fps=24)
    st = Stage(scene, film, v, sk)
    if name == "plain":
        s = st.shot("walkin", 3.0)
        s.lens(32, 4.0)
        s.move((0.9, 22.6, 0.75), (0.5, 57.6, 2.6))
        s.focus((0.15, 26.6, 0.8))
        st.finish()
        return {"film": film, "captions": [], "stage": st}
    hello = out["hello"]
    cams = hello["cameras"]
    A = v.anchors
    road = v.paths["road_to_forest"]

    # --- shot 1: beat 6, the walk in (the end of it), gate camera
    s = st.shot("walkin", 3.0)
    f0 = s.frame_start
    kid = st.actor("kid", "farmer", child=True)
    steve = players.add_player(st, "steve", "steve")
    players.equip(steve, "diamond", enchanted=True)
    steve.hold("diamond_sword")
    tail = [(0.5, 49.0, v.ground(0.5, 49.0))] + [p for p in road if p[1] > 50.0]
    steve.place(f0 - 17, tail[0], yaw_to(tail[0], tail[1]))
    end = steve.walk(f0 - 17, tail, ramp=(False, True))
    steve.show(end, False)
    INFO["walk_end"] = end
    INFO["tail"] = tail
    spot = (0.15, 26.6, v.ground(0, 26) - 0.0625)
    kid.place(f0, spot, yaw_to(spot, (2.2, 40.0)))
    kid.look_at(f0, steve, ease=0)
    st.use(s, kid, steve)
    s.lens(float(os.environ.get("CHECK_LENS", cams["gate"]["lens"])), cams["gate"]["fstop"])
    s.move(cams["gate"]["pos"], cams["gate"]["target"])
    s.focus(kid.head)
    st.hero(s, "child", kid)
    st.lights(s, scale=1.0, near=A["exit_gate"], radius=14.0)

    # --- shot 2: beat 8, the side camera; the child runs up the road and stops 3 short
    s = st.shot("side", 2.0)
    f0 = s.frame_start
    kid2 = st.actor("kid2", "farmer", child=True)
    him = players.add_player(st, "watcher", "herobrine")
    gap = A["forest_gap"]
    him.place(f0, gap, v.yaws["forest_gap"])
    run = [(0.5, 50.6, v.ground(0.5, 50.6)), (0.5, 52.0, v.ground(0.5, 52.0)), (gap[0], gap[1] - 3.0, gap[2])]
    kid2.place(f0, run[0], yaw_to(run[0], run[1]))
    e2 = kid2.walk(f0, run, speed=3.4, run=True)
    kid2.look_at(e2, him, ease=4)
    INFO["run_end"] = e2
    st.use(s, kid2, him)
    s.lens(cams["side"]["lens"], cams["side"]["fstop"])
    s.move(cams["side"]["pos"], cams["side"]["target"])
    s.focus(kid2.head)
    st.hero(s, "child", kid2)
    st.lights(s, scale=0.0)

    # --- shot 3: beat 14, pyramid; the child walks half way round; slow sideways track
    s = st.shot("round", 3.0)
    f0 = s.frame_start
    kid3 = st.actor("kid3", "farmer", child=True)
    ring = v.paths["pyramid_round"]
    kid3.place(f0, ring[0], yaw_to(ring[0], ring[1]))
    e3 = kid3.walk(f0, ring, speed=3.2)
    INFO["round_end"] = e3
    st.use(s, kid3)
    c = cams["pyramid"]
    s.lens(c["lens"], c["fstop"])
    s.move(c["pos"], c["target"], (c["pos"][0], c["pos"][1] + 2.0, c["pos"][2]), c["target"])
    s.focus(kid3.head)
    st.hero(s, "child", kid3)
    st.lights(s, scale=0.0)

    # --- shot 4: beat 12, floating oak
    s = st.shot("under", 1.0)
    f0 = s.frame_start
    kid4 = st.actor("kid4", "farmer", child=True)
    fl = hello["floating"]
    c = cams["floating"]
    spot = (fl["under"][0] + 0.2, fl["under"][1] - 1.0, fl["under"][2])
    kid4.place(f0, spot, yaw_to(spot, (c["pos"][0], c["pos"][1] + 5.0)))
    kid4.look_at(f0, fl["canopy"], ease=0)
    st.use(s, kid4)
    s.lens(c["lens"], c["fstop"])
    # a lower, farther, more level camera than the proof still: the canopy and the gap against the sky
    pos = (fl["under"][0] + 9.5, fl["under"][1] + 3.0, 0.5)
    s.move(pos, (fl["under"][0], fl["under"][1], 2.6))
    s.lens(26, 4.0)
    s.focus(kid4.head)
    st.hero(s, "child", kid4)
    st.lights(s, scale=0.0)

    # --- shot 5: inside the wood, looking further in (north) from the gap, a watcher at forest_deep
    s = st.shot("deep", 1.0)
    f0 = s.frame_start
    him2 = players.add_player(st, "watcher2", "herobrine")
    him2.place(f0, A["forest_deep"], v.yaws["forest_gap"])
    st.use(s, him2)
    s.lens(24, 4.0)
    s.move((gap[0] - 0.6, gap[1] - 2.5, 1.5), (gap[0], gap[1] + 6.0, 1.6))
    s.focus(him2.head)
    st.lights(s, scale=0.0)

    # --- shot 6: close on the tree line east of the gap: trunk, leaves, grass, tall grass
    s = st.shot("edge", 1.0)
    f0 = s.frame_start
    st.use(s)
    s.lens(35, 4.0)
    s.move((gap[0] + 6.5, gap[1] - 6.0, 1.3), (gap[0] + 9.5, gap[1] + 1.0, 2.4))
    s.focus((gap[0] + 9.0, gap[1], 2.0))
    st.lights(s, scale=0.0)

    st.finish()
    INFO.update(v=v, steve=steve, kid2=kid2, kid3=kid3, hello=hello)
    return {"film": film, "captions": [], "stage": st}


def main(argv):
    import time

    import render as R

    name = argv[0]
    VARIANT["name"] = name
    sys.modules["films.check_sets_film"] = sys.modules[__name__]
    ses = R.Session("check_sets_film")
    scene = ses.scene
    if argv[1:] == ["info"]:
        for label, who, frames in (("steve", INFO["steve"], range(1, 73, 2)), ("kid2", INFO["kid2"], range(73, 121, 4)),
                                   ("kid3", INFO["kid3"], range(121, 193, 6))):
            for f in frames:
                scene.frame_set(f)
                m = who.root.matrix_world
                print("%s f%3d  (%.2f, %.2f, %.3f)  hidden=%s" % (label, f, m.translation.x, m.translation.y, m.translation.z,
                                                                 who.root.hide_render))
        print("walk_end", INFO["walk_end"], "run_end", INFO["run_end"], "round_end", INFO["round_end"])
        print("tail", INFO["tail"])
        return 0
    ses.configure((540, 960), 16, 2, None)
    if os.environ.get("CHECK_SEED"):
        print("seed was", scene.cycles.seed, "animated", scene.cycles.use_animated_seed)
        scene.cycles.seed = int(os.environ["CHECK_SEED"])
    if os.environ.get("CHECK_TB"):
        print("transparent_max_bounces was", scene.cycles.transparent_max_bounces, "max_bounces", scene.cycles.max_bounces)
        scene.cycles.transparent_max_bounces = int(os.environ["CHECK_TB"])
    for a in argv[1:]:
        f = int(a)
        t = time.time()
        path = os.path.join(ROOT, "out", "test", "check_sets_%s%s_f%03d.png" % (name, os.environ.get("CHECK_TAG", ""), f))
        ses.render_frame(f, path)
        print("[check_sets_film] %s frame %d -> %s  %.1f s" % (name, f, path, time.time() - t), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
