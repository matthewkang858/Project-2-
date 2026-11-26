"""Checker probe for engine/towers.py (independent review): the story's beats staged from the module docstring
alone, through films.lookdev.Stage and the golden look-dev sky, 540x960, 16 samples, 2 threads, motion blur on.

    $BPY -m tools.check_towers_beats NAME ...           -> out/test/check_towers_<NAME>.png and _zones.png
    $BPY -m tools.check_towers_beats --where NAME ...   (no render: where the heroes land in the frame, in %)
"""
import math
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "out", "test")
GOLD = dict(preset="golden", az=62.0, el=27.0, bloom=1.0, grade="warm")


def lights(st, s, fm):
    st.lights(s, scale=1.0, groups={"tower_pod": 1.0, "tower_cell": 1.0})


def cam(s, pos, target, lens, fstop=4.0, focus=None):
    s.lens(lens, fstop)
    s.move(pos, target)
    s.focus(focus if focus is not None else target)


def zombie(st, fm, f, aggro=False, look=None):
    from engine import undead
    z = st.cast.get("zombie") or undead.add_zombie(st, "zombie")
    fm.zombie_in_cell(z, f, aggro=aggro, look=look)
    return z


def b01_square(st, s, fm, H):
    """Beat 1 from the docstring: C['square'] (or lower), baby on square_baby, Steve walks at the lens."""
    from engine import players
    f0 = s.frame_start
    baby = st.actor("baby", "none", child=True)
    baby.place(f0, fm.A["square_baby"], fm.yaw["square_baby"])
    steve = players.add_player(st, "steve", "steve")
    steve.place(f0, (1.0, 3.5, 0.0), 0.0)
    c = fm.cameras["square"]
    steve.walk(f0, [(1.0, 3.5, 0.0), (c["pos"][0] - 1.2, c["pos"][1] + 0.6, 0.0)])
    baby.look_at(f0, steve, ease=0)
    st.use(s, baby, steve)
    cam(s, c["pos"], c["target"], c["lens"], c["fstop"], focus=baby.head)
    lights(st, s, fm)
    H[s.name] = dict(frame=f0 + 20, heroes={"baby head": baby.head, "steve head": steve.head},
                     points={"pod": fm.A["pod_target"]})


def b04_square(st, s, fm, H):
    """Beat 4, the end of the tilt: C['square'], Mom on mom_glass looking at the zombie, rack focus to her."""
    f0 = s.frame_start
    baby = st.actor("baby", "none", child=True)
    baby.place(f0, fm.A["square_baby"], fm.yaw["square_baby"])
    baby.look_at(f0, fm.A["pod_target"], ease=0)
    mom = st.actor("mom", "farmer")
    mom.place(f0, fm.A["mom_glass"], fm.yaw["mom_glass"])
    mom.look_at(f0, fm.zombie_eye, ease=0)
    cl, li = st.actor("cleric", "cleric"), st.actor("librarian", "librarian")
    cl.place(f0, fm.A["back_2"], fm.yaw["back_2"])
    li.place(f0, fm.A["back_3"], fm.yaw["back_3"])
    cl.look_at(f0, fm.zombie_eye, ease=0)
    li.look_at(f0, fm.zombie_eye, ease=0)
    z = zombie(st, fm, f0, look=mom)
    st.use(s, baby, mom, cl, li, z)
    c = fm.cameras["square"]
    cam(s, c["pos"], c["target"], c["lens"], c["fstop"], focus=mom.head)
    lights(st, s, fm)
    H[s.name] = dict(frame=f0 + 12, heroes={"mom head": mom.head, "baby head": baby.head},
                     points={"slot": fm.A["slot_target"], "top step": fm.A["top_step"]})


def b04_long(st, s, fm, H):
    """Beat 4 fallback: the same plaza position, a 200 mm lens on Mom at the front glass, the panes on the line
    from the lens to her hidden (fm.see_through(points=[mom]))."""
    f0 = s.frame_start
    mom = st.actor("mom", "farmer")
    mom.place(f0, fm.A["mom_glass"], fm.yaw["mom_glass"])
    mom.look_at(f0, fm.zombie_eye, ease=0)
    z = zombie(st, fm, f0, look=mom)
    st.use(s, mom, z)
    c = fm.cameras["square"]
    tgt = (fm.A["mom_glass"][0], fm.A["mom_glass"][1], fm.A["mom_glass"][2] + 1.5)
    cam(s, c["pos"], tgt, 200, 2.8, focus=mom.head)
    fm.see_through(st, s, dict(pos=c["pos"], target=tgt), points=[mom, tgt])
    lights(st, s, fm)
    H[s.name] = dict(frame=f0 + 12, heroes={"mom head": mom.head})


def b06_pan_end(st, s, fm, H):
    """Beat 6, the end of the pan: camera about (-20.5, 18.6, 11.3) now looking east to the cell."""
    f0 = s.frame_start
    mom = st.actor("mom", "farmer")
    mom.place(f0, fm.A["bed_side"], fm.yaw["bed_side"])
    mom.look_at(f0, fm.zombie_eye, ease=0)
    z = zombie(st, fm, f0, look=mom)
    st.use(s, mom, z)
    cam(s, (-20.5, 18.6, 11.3), (-18.3, 19.5, 11.2), 24, 4.0, focus=z.head)
    lights(st, s, fm)
    H[s.name] = dict(frame=f0 + 12, heroes={"zombie head": z.head, "mom head": mom.head})


def b06_pan_start(st, s, fm, H):
    """Beat 6, the start of the pan: the red bed lengthwise from its foot, two white beds beyond, Mom beside it."""
    f0 = s.frame_start
    mom = st.actor("mom", "farmer")
    mom.place(f0, fm.A["bed_side"], fm.yaw["bed_side"])
    mom.look_at(f0, fm.zombie_eye, ease=0)
    z = zombie(st, fm, f0, look=mom)
    st.use(s, mom, z)
    cam(s, (-20.5, 18.6, 11.3), (-20.9, 22.0, 10.4), 24, 4.0, focus=fm.beds["mom"]["pos"])
    lights(st, s, fm)
    H[s.name] = dict(frame=f0 + 12, heroes={"mom head": mom.head}, points={"red bed": fm.beds["mom"]["pos"]})


def b08_in_cell(st, s, fm, H):
    """Beat 8 / 23 alternative: over the zombie's right shoulder from inside its cell, its arm a soft shape at the
    frame's lower edge, the three backed against the far glass."""
    from engine import towers
    f0 = s.frame_start
    cast = []
    for i, (n, prof) in enumerate((("mom", "farmer"), ("cleric", "cleric"), ("librarian", "librarian"))):
        c = st.actor(n, prof)
        c.place(f0, fm.A["back_%d" % (i + 1)], fm.yaw["back_%d" % (i + 1)])
        towers.panic(c, f0, s.frame_end, fm.zombie_eye, seed=11 + i)
        cast.append(c)
    z = zombie(st, fm, f0, aggro=False, look=cast[1])
    st.use(s, z, *cast)
    cam(s, (-17.12, 19.86, 11.62), (-22.6, 19.55, 11.15), 24, 2.8, focus=cast[1].head)
    lights(st, s, fm)
    H[s.name] = dict(frame=f0 + 20, heroes={"mom": cast[0].head, "cleric": cast[1].head, "librarian": cast[2].head})


def b12_hopper(st, s, fm, H):
    """Beat 12 from the docstring: C['hopper'], items delivered, poppies strewn, Steve at the chest, the baby
    among the poppies."""
    from engine import mobs, players
    f0 = s.frame_start
    items = []
    for i, iid in enumerate(("iron_ingot", "iron_ingot", "iron_ingot", "poppy")):
        it = mobs.make_dropped_item(iid, name="cb_hop_%d" % i, seed=i)
        st.cast[it.name] = it
        items.append(it)
    plans = fm.deliver(items, f0 + 2, every=6, seed=2)
    lying = []
    for i in range(4):
        it = mobs.make_dropped_item("poppy", name="cb_lying_%d" % i, seed=10 + i)
        st.cast[it.name] = it
        lying.append(it)
    c = fm.cameras["hopper"]
    fm.strew(lying, f0, s.frame_end + 1, seed=3, face=c["pos"])
    steve = players.add_player(st, "steve", "steve")
    steve.hold("iron_ingot")
    steve.place(f0, fm.A["chest_front"], fm.yaw["chest_front"])
    baby = st.actor("baby", "none", child=True)
    baby.place(f0, fm.A["poppies"], fm.yaw["poppies"])
    st.use(s, steve, baby, *(items + lying))
    cam(s, c["pos"], c["target"], c["lens"], c["fstop"], focus=fm.A["hopper_target"])
    lights(st, s, fm)
    landed = plans[0]["landed"] if "landed" in plans[0] else plans[0]["frame"] - 4
    H[s.name] = dict(frame=int(landed) + 1, heroes={"steve head": steve.head, "baby head": baby.head},
                     points={"hopper": fm.A["hopper_target"]})


def b14_stairs(st, s, fm, H):
    """Beat 14: the baby on the top step beside the gap (C['stairs'] is the docstring's outside view of the top
    step), through the glass the beds and the straw hat (Mom on bed_side)."""
    f0 = s.frame_start
    baby = st.actor("baby", "none", child=True)
    s8 = fm.set["stairs"][8]
    baby.place(f0, s8, fm.yaw["top_step"])
    fm.climb(baby, f0 + 4, 9, 9, approach=False)
    mom = st.actor("mom", "farmer")
    mom.place(f0, fm.A["bed_side"], fm.yaw["bed_side"])
    mom.look_at(f0, fm.zombie_eye, ease=0)
    z = zombie(st, fm, f0, look=mom)
    st.use(s, baby, mom, z)
    c = fm.cameras["stairs"]
    cam(s, c["pos"], c["target"], c["lens"], c["fstop"], focus=fm.A["gap_target"])
    lights(st, s, fm)
    H[s.name] = dict(frame=f0 + 30, heroes={"baby head": baby.head, "mom head": mom.head},
                     points={"gap": fm.A["gap_target"], "plug": (fm.A["gap_target"][0], fm.A["gap_target"][1],
                                                                fm.A["gap_target"][2] + 1.0)})


def b16_red_bed(st, s, fm, H):
    """Beat 16: two-shot at the red bed, Mom on bed_side looking at the zombie, the baby against her on the lens
    side, the zombie's arms soft in the background (camera chosen by the checker: none is given)."""
    from engine.village import yaw_to
    f0 = s.frame_start
    mom = st.actor("mom", "farmer")
    mom.place(f0, fm.A["bed_side"], fm.yaw["bed_side"])
    mom.look_at(f0, fm.zombie_eye, ease=0)
    z = zombie(st, fm, f0, aggro=True, look=mom)
    campos = (-22.75, 21.05, 11.3)
    baby = st.actor("baby", "none", child=True)
    bp = (fm.A["bed_side"][0] - 0.55, fm.A["bed_side"][1] + 0.05, fm.A["bed_side"][2])
    baby.place(f0, bp, yaw_to(bp, (0.5 * campos[0] + 0.5 * fm.A["bed_side"][0], 0.5 * campos[1] + 0.5 * fm.A["bed_side"][1])))
    baby.look_at(f0, mom, ease=0)
    st.use(s, mom, baby, z)
    cam(s, campos, (-18.6, 19.7, 10.75), 30, 2.8, focus=baby.head)
    lights(st, s, fm)
    H[s.name] = dict(frame=f0 + 12, heroes={"baby head": baby.head, "mom head": mom.head, "zombie head": z.head})


def b20_gap_adult(st, s, fm, H):
    """Beat 20 from the docstring: about (-21.4, 22.4, 10.9) looking east at the gap; narrator on gap_in."""
    f0 = s.frame_start
    nar = st.actor("narrator", "none")
    nar.place(f0, fm.A["gap_in"], fm.yaw["gap_in"])
    nar.look_at(f0, fm.A["gap_target"], ease=0)
    st.use(s, nar)
    cam(s, (-21.4, 22.4, 10.9), (-18.5, 22.95, 10.75), 22, 4.0, focus=nar.head)
    lights(st, s, fm)
    H[s.name] = dict(frame=f0 + 12, heroes={"narrator head": nar.head}, points={"gap": fm.A["gap_target"]})


def b22_back(st, s, fm, H):
    """Beat 22: past the narrator's three-quarter face through the back glass, Steve on one_down breaks the top
    step (camera chosen by the checker: none is given)."""
    from engine import players
    f0 = s.frame_start
    nar = st.actor("narrator", "none")
    np_ = (-20.35, 22.35, 10.0)
    nar.place(f0, np_, math.radians(200.0))
    steve = players.add_player(st, "steve", "steve")
    steve.place(f0, fm.A["one_down"], fm.yaw["one_down"])
    steve.look_at(f0, fm.top_step.center, ease=0)
    m = fm.break_top_step(steve, f0 + 6, camera=s)
    nar.look_at(f0, steve, ease=0)
    st.cast[fm.top_step.name] = fm.top_step
    st.use(s, nar, steve, fm.top_step)
    cam(s, (-21.35, 21.05, 11.45), (-19.3, 24.3, 10.4), 26, 2.8, focus=steve.head)
    lights(st, s, fm)
    H[s.name] = dict(frame=m["start"] + 10, heroes={"narrator head": nar.head, "steve head": steve.head},
                     points={"top step": fm.top_step.center})


NAMES = [k for k in list(globals()) if k[:1] == "b" and k[1:3].isdigit()]


def build(scene, names):
    from engine import look, shots, towers, village
    from films.lookdev import Stage

    look.setup_render(scene, res=(540, 960), samples=16, threads=2)
    v = village.build_village(scene, seed=1, edit=lambda b: towers.iron_farm(b))
    fm = towers.farm(v)
    sk = Stage.build_sky(scene, GOLD)
    film = shots.Film(scene, fps=24)
    st = Stage(scene, film, v, sk)
    H = {}
    sh = {}
    for n in names:
        s = st.shot(n, 2.0)
        globals()[n](st, s, fm, H)
        sh[n] = s
    st.finish()
    return film, st, fm, H, sh


def where(scene, film, H, name):
    import bpy
    from bpy_extras.object_utils import world_to_camera_view
    from mathutils import Vector
    f = H[name]["frame"]
    film.goto(f)
    cam = scene.camera
    out = {}
    for label, ob in H[name].get("heroes", {}).items():
        p = ob.matrix_world.translation + ob.matrix_world.to_3x3() @ Vector((0, 0, 0.25))
        q = world_to_camera_view(scene, cam, p)
        out[label] = (round(100 * q.x), round(100 * (1 - q.y)), round(q.z, 2))
    for label, p in H[name].get("points", {}).items():
        q = world_to_camera_view(scene, cam, Vector(p))
        out[label] = (round(100 * q.x), round(100 * (1 - q.y)), round(q.z, 2))
    return f, out


def main(argv):
    import bpy
    from PIL import Image
    from engine import post

    only_where = "--where" in argv
    names = [a for a in argv if not a.startswith("-")]
    bad = [n for n in names if n not in NAMES]
    if bad:
        print("unknown %s; known %s" % (bad, NAMES))
        return 2
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    t0 = time.time()
    film, st, fm, H, sh = build(scene, names)
    print("[check] built in %.1f s" % (time.time() - t0), flush=True)
    for n in names:
        f, pos = where(scene, film, H, n)
        print("[check] %-14s frame %d  (x %%, y %%, depth): %s" % (n, f, pos), flush=True)
        if only_where:
            continue
        t = time.time()
        film.goto(f)
        path = os.path.join(OUT, "check_towers_%s.png" % n)
        scene.render.filepath = path[:-4] + "_part"
        scene.render.use_file_extension = True
        bpy.ops.render.render(write_still=True)
        os.replace(path[:-4] + "_part.png", path)
        post.draw_zones(Image.open(path)).save(path[:-4] + "_zones.png")
        print("[check] %-14s -> %s  %.1f s" % (n, path, time.time() - t), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
