"""Reviewer's probe of engine/nether.py: a small film-like build of "Six Seconds" beats 6, 13, 18 and 19, written from
the module docstring only, rendered through render.Session (540x960, 16 samples, motion blur, depth of field).

    $BPY -m tools.check_nether_film info                    build only, print checks (no render)
    $BPY -m tools.check_nether_film b6a b6b ...              render named frames to out/test/check_nether_<name>.png
"""
import os
import sys
import types

FILM = "check_nether_film"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INFO = {}


def build(scene):
    from mathutils import Vector

    from engine import breaking, nether, piglins, players, shots

    scene.render.resolution_x, scene.render.resolution_y = 540, 960
    scene.cycles.samples = 16
    bas = nether.build_bastion(scene)
    sky = nether.set_nether(scene, biome="nether_wastes")
    film = shots.Film(scene, fps=24)
    st = nether.Stage(scene, film, bas, sky)
    A, Y, C = bas.anchors, bas.yaws, bas.cameras
    brute = piglins.add_piglin(st, "brute", "brute")
    pigs = [piglins.add_piglin(st, "pig_%d" % k, weapon=("crossbow" if k == 3 else "default")) for k in (1, 2, 3)]
    runner = players.add_player(st, "runner", "steve")
    players.equip(runner, boots="golden")
    runner.hold("iron_pickaxe")
    lure = piglins.add_item(st, "gold_ingot", name="lure")
    toss = piglins.add_item(st, "gold_ingot", name="toss")
    for b in bas.pillar:
        st.cast[b.name] = b
    home = bas.lights_for("home")

    def cam(s, name, focus):
        c = C[name]
        s.lens(c["lens"], c["fstop"] or 4.0)
        s.move(c["pos"], c["target"])
        s.focus(focus)

    # ---- beat 6: the last block of the pit is broken, three piglins walk to the lure and drop in
    s = st.shot("b6_pit", 3.0)
    f0, f1 = s.frame_start, s.frame_end
    bas.pit_open(s, keep=[bas.pit_last.cell])
    runner.place(f0, A["home_rim_w"], Y["home_rim_w"])
    runner.look_at(f0, bas.pit_last.center, ease=0)
    mined = breaking.mine(runner, bas.pit_last, f0 + 4, camera=s)
    lure.place(f0, A["home_pit_4"])
    lure.animate(f0, f1 + 1)
    lands = []
    for k, p in enumerate(pigs, 1):
        path = bas.paths["home_pit_walk_%d" % k]
        p.place(f0, path[1], nether.yaw_to(path[1], path[2]))
        start = f0 + 18 + 9 * (k - 1)
        end = p.walk(start, path[1:], ramp=(4, 0))
        lands.append((end, p.fall(end, A["home_pit_center"][2])))
    cam(s, "pit", A["home_pit_center"])
    st.use(s, runner, lure, *pigs)
    st.hero(s, "piglin", pigs[1])
    st.lights(s, 1.0, groups={"home_pit": 2.5}, **home)
    INFO["mine"] = (mined["start"], mined["frame"], mined["drop"])
    INFO["falls"] = lands
    INFO["b6"] = (f0, f1)

    # ---- beat 13: on the netherrack pillar, the ingot dropped past the brute's snout
    s = st.shot("b13_pillar", 2.0)
    f0, f1 = s.frame_start, s.frame_end
    runner.place(f0, A["bridge_pillar_top"], Y["bridge_pillar_top"])
    runner.sneak(f0)
    brute.place(f0, A["bridge_pillar_foot"], Y["bridge_pillar_foot"])
    brute.look_at(f0, runner.head, ease=0)
    brute.flop_ears(f0, f1 + 1)
    toss.place(f0, A["bridge_pillar_top"])           # (moved by throw_item)
    aim = Vector(A["bridge_pillar_foot"]) + Vector((0.3, -0.5, 0.0))
    runner.swing_arm(f0 + 6)
    landed = piglins.throw_item(toss, f0 + 6, runner, aim, world=bas)
    toss.animate(f0 + 6, f1 + 1)
    cam(s, "bridge_pillar", brute.head)
    st.use(s, runner, brute, toss, *bas.pillar)
    st.hero(s, "brute", brute)
    st.lights(s, 1.0, **bas.lights_for("bridge"))
    INFO["toss_landed"] = landed
    INFO["b13"] = (f0, f1)

    # ---- beat 18: the gate frame, the brute small in the gateway with his back to us, lava flicker
    s = st.shot("b18_gate", 2.0)
    f0, f1 = s.frame_start, s.frame_end
    brute.place(f0, A["home_gateway"], Y["home_gateway"])
    brute.flop_ears(f0, f1 + 1)
    for k, p in enumerate(pigs, 1):
        p.place(f0, A["home_gold_%d" % k], Y["home_gold_%d" % k])
        p.look_at(f0, A["home_gold_target"], ease=0)
        p.flop_ears(f0, f1 + 1)
    bas.lava["home_channels"].flicker(f0, f1)
    cam(s, "gate", A["home_center"])
    st.use(s, brute, *pigs)
    st.hero(s, "brute", brute)
    st.lights(s, 1.0, **home)
    INFO["b18"] = (f0, f1)

    # ---- beat 19: match cut, no brute; the runner sprints in through the gateway
    s = st.shot("b19_match", 2.0)
    f0, f1 = s.frame_start, s.frame_end
    for k, p in enumerate(pigs, 1):
        p.place(f0, A["home_gold_%d" % k], Y["home_gold_%d" % k])
        p.look_at(f0, A["home_gold_target"], ease=0)
        p.flop_ears(f0, f1 + 1)
    path = bas.paths["home_run_in"]
    runner.place(f0, path[0], nether.yaw_to(path[0], path[1]))
    INFO["run_end"] = runner.walk(f0, path, sprint=True)
    cam(s, "gate", A["home_center"])
    st.use(s, runner, *pigs)
    st.lights(s, 1.0, **home)
    INFO["b19"] = (f0, f1)

    # ---- the camera suggestions the author never rendered, staged as their notes say
    s = st.shot("b4_inside", 1.0)                      # beat 4: runner sprints through the gateway at the lens
    f0, f1 = s.frame_start, s.frame_end
    brute.place(f0, A["home_landing"], Y["home_landing"])
    brute.look_at(f0, A["home_gateway_target"], ease=0)
    runner.place(f0, A["home_corridor"], Y["home_corridor"])
    runner.walk(f0, [A["home_corridor"], A["home_gateway"], (4.5, 13.0, 0.0)], sprint=True)
    cam(s, "inside_gate", runner.head)
    st.use(s, brute, runner)
    st.lights(s, 1.0, **home)
    s = st.shot("b5_boot", 1.0)                        # beat 5: boots skid to a stop, piglins at the gold behind
    f0, f1 = s.frame_start, s.frame_end
    runner.place(f0, A["home_boot_mark"], Y["home_boot_mark"])
    for k, p in enumerate(pigs, 1):
        p.place(f0, A["home_gold_%d" % k], Y["home_gold_%d" % k])
        p.look_at(f0, A["home_boot_mark"], ease=0)
    cam(s, "boot", A["home_boot_mark"])
    st.use(s, runner, *pigs)
    st.lights(s, 1.0, **home)
    s = st.shot("b9_rim", 1.0)                         # beat 9: side-on at the west rim, brute behind the runner
    f0, f1 = s.frame_start, s.frame_end
    bas.pit_open(s)
    runner.place(f0, A["home_rim_w"], Y["home_rim_w"])
    brute.place(f0, (A["home_rim_w"][0] - 1.2, A["home_rim_w"][1] + 1.0, 0.0),
                nether.yaw_to((A["home_rim_w"][0] - 1.2, A["home_rim_w"][1] + 1.0), A["home_rim_w"]))
    brute.look_at(f0, runner.head, ease=0)
    cam(s, "rim_side", runner.head)
    st.use(s, runner, brute)
    st.lights(s, 1.0, **home)
    s = st.shot("b14_profile", 1.0)                    # beat 14: the brute in clean profile at the pillar's foot
    f0, f1 = s.frame_start, s.frame_end
    brute.place(f0, A["bridge_pillar_foot"], Y["bridge_pillar_foot"])
    brute.look_at(f0, A["bridge_pillar_top_target"], ease=0)
    cam(s, "bridge_profile", brute.head)
    st.use(s, brute, *bas.pillar)
    st.lights(s, 1.0, **bas.lights_for("bridge"))
    s = st.shot("b17_corridor", 1.0)                   # beat 17: frontal portrait from the entrance corridor
    f0, f1 = s.frame_start, s.frame_end
    brute.place(f0, A["home_gateway"], Y["home_gateway"])
    for k, p in enumerate(pigs, 1):
        p.place(f0, A["home_gold_%d" % k], Y["home_gold_%d" % k])
    cam(s, "corridor", brute.head)
    st.use(s, brute, *pigs)
    st.lights(s, 1.0, **home)
    s = st.shot("b11_bridge_boot", 1.0)                # beat 11: the boot shot on the bridge
    f0, f1 = s.frame_start, s.frame_end
    runner.place(f0, A["bridge_boot_mark"], Y["bridge_boot_mark"])
    cam(s, "bridge_boot", A["bridge_boot_mark"])
    st.use(s, runner)
    st.lights(s, 1.0, **bas.lights_for("bridge"))
    st.finish()
    INFO["bas"] = bas
    return {"film": film, "captions": [], "stage": st}


FRAMES = {"b6a": ("b6_pit", 9), "b6b": ("b6_pit", 40), "b13": ("b13_pillar", 14), "b18": ("b18_gate", 20),
          "b19": ("b19_match", 30), "b19_0": ("b19_match", 0), "b4": ("b4_inside", 10), "b5": ("b5_boot", 6),
          "b9": ("b9_rim", 6), "b14": ("b14_profile", 6), "b17": ("b17_corridor", 6), "b11": ("b11_bridge_boot", 6)}


def _flip(yaw):
    import math
    return yaw + math.pi


def register():
    mod = types.ModuleType("films." + FILM)
    mod.__file__ = os.path.abspath(__file__)
    mod.build = build
    sys.modules["films." + FILM] = mod
    return mod


def main():
    import render as R

    register()
    ses = R.Session(FILM)
    bas = INFO["bas"]
    print("[probe] mine (start, break, drop):", INFO["mine"], " falls (walk end, land):", INFO["falls"])
    print("[probe] toss landed", INFO["toss_landed"], " run end", INFO["run_end"], " b6", INFO["b6"], "b13",
          INFO["b13"], "b18", INFO["b18"], "b19", INFO["b19"])
    for name in ("b6", "b13", "b18", "b19"):
        f0, f1 = INFO[name]
        print("[probe] %s pit_state %s .. %s" % (name, bas.pit_state(f0), bas.pit_state(f1)),
              "pit blocks there:", sum(b.there_at(f0 + 2) for b in bas.pit_blocks.values()), "/ 8",
              "pillar there+shown:", [round(1 - b.object.hide_render) for b in bas.pillar] if False else "")
    sc = ses.scene
    for name in ("b6", "b13", "b18", "b19"):
        f0, f1 = INFO[name]
        sc.frame_set(f0 + 2)
        pit_vis = sum(1 for b in bas.pit_blocks.values() if not b.object.hide_render)
        pil_vis = sum(1 for b in bas.pillar if not b.object.hide_render)
        lights_on = sorted({o.get("group") for o in bas.lantern_lights if not o.hide_render})
        print("[probe] frame %d (%s): pit objects rendered %d, pillar rendered %d, lantern groups on %s"
              % (f0 + 2, name, pit_vis, pil_vis, lights_on))
    want = [a for a in sys.argv[1:] if a in FRAMES]
    ses.configure((540, 960), 16, 2, None)
    for n in want:
        shot, off = FRAMES[n]
        s = next(x for x in ses.film.shots if x.name == shot)
        f = s.frame_start + off
        path = os.path.join(ROOT, "out", "test", "check_nether_%s.png" % n)
        import time
        t = time.time()
        ses.render_frame(f, path)
        print("[probe] %s frame %d -> %s %.1fs" % (n, f, path, time.time() - t), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
