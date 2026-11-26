"""Checker probe for engine/towers.py (independent review): two beats with action, staged from the module
docstring through films.lookdev.Stage (golden look-dev sky), 3 s each, frames rendered at 540x960, 16 samples,
2 threads, motion blur on (the final look), side by side in one sheet.

    $BPY -m tools.check_towers_action b24     # beat 23/24: four trembling villagers, the golem pops in behind the
                                              #   glass, steps, starts to slide; rack focus to it
    $BPY -m tools.check_towers_action b22     # beat 22: Steve breaks the top dirt step and hops down out of sight,
                                              #   seen from inside through the back glass
    $BPY -m tools.check_towers_action b03     # beat 3 numbers only: the push along tower_push_square
"""
import math
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "out", "test")
GOLD = dict(preset="golden", az=62.0, el=27.0, bloom=1.0, grade="warm")


def setup(scene):
    from engine import look, shots, towers, village
    from films.lookdev import Stage

    look.setup_render(scene, res=(540, 960), samples=16, threads=2)
    v = village.build_village(scene, seed=1, edit=lambda b: towers.iron_farm(b))
    fm = towers.farm(v)
    sk = Stage.build_sky(scene, GOLD)
    film = shots.Film(scene, fps=24)
    st = Stage(scene, film, v, sk)
    return v, fm, film, st


def probe_b24(scene):
    from engine import mobs, towers, undead
    v, fm, film, st = setup(scene)
    A = fm.A
    # a lead-in shot so the golem has a history (beat 11's slide) before the held cell_side shot
    s0 = st.shot("lead", 4.0)
    g = mobs.make_iron_golem("golem")
    st.cast["golem"] = g
    fm.golem_spawn(g, s0.frame_start + 2, look=A["pod_target"])
    r = fm.golem_slide(g, s0.frame_start + 6)
    s0.lens(20)
    s0.move(fm.cameras["slide"]["pos"], fm.cameras["slide"]["target"])
    st.use(s0, g)
    st.lights(s0, 1.0)
    # beats 23 + 24 in one held shot, as the docstring stages them
    s = st.shot("b24", 3.0)
    f0 = s.frame_start
    mom, nar = st.actor("mom", "farmer"), st.actor("narrator", "none")
    cl, li = st.actor("cleric", "cleric"), st.actor("librarian", "librarian")
    spots = [("mom", mom, A["back_1"], fm.yaw["back_1"]), ("narrator", nar, A["back_2"], fm.yaw["back_2"]),
             ("cleric", cl, A["back_3"], fm.yaw["back_3"]),
             ("librarian", li, (-21.9, 18.55, A["back_1"][2]), None)]
    for name, c, p, y in spots:
        c.place(f0, p, y if y is not None else math.atan2(fm.zombie_eye[0] - p[0], -(fm.zombie_eye[1] - p[1])))
    towers.panic(mom, f0, s.frame_end, fm.zombie_eye, seed=7)
    towers.panic(nar, f0, s.frame_end, fm.zombie_eye, seed=7)
    towers.panic(cl, f0, s.frame_end, fm.zombie_eye, seed=21)
    towers.panic(li, f0, s.frame_end, fm.zombie_eye, seed=22)
    z = undead.add_zombie(st, "zombie")
    fm.zombie_in_cell(z, f0, aggro=True, look=mom)
    spawn = f0 + 10
    fm.golem_spawn(g, spawn, pos=(-26.8, 22.1, 10.0), look=A["pod_target"])
    e = fm.golem_step(g, spawn + 14)
    rr = fm.golem_slide(g, e + 2)
    st.use(s, mom, nar, cl, li, z, g)
    c = fm.cameras["cell_side"]
    s.lens(c["lens"], c["fstop"])
    s.move(c["pos"], c["target"])
    s.focus(nar.head)
    s.focus(g.head, at_s=(spawn + 20 - 1) / 24.0)
    st.lights(s, scale=1.0, groups={"tower_pod": 1.0, "tower_cell": 1.0})
    st.finish()
    frames = [spawn - 1, spawn, e - 2, rr["frame"] + 14, s.frame_end]
    info = dict(spawn=spawn, step_end=e, slide=rr["frame"], edge=rr["edge"], gone=rr["gone"], shot=(f0, s.frame_end))
    return film, frames, info


def probe_b22out(scene):
    """Beat 22's action from C['stairs'] (the docstring's outside view): the hops down the steps."""
    return probe_b22(scene, outside=True)


def probe_b22(scene, outside=False):
    from engine import players, towers
    v, fm, film, st = setup(scene)
    A = fm.A
    s = st.shot("b22", 3.0)
    f0 = s.frame_start
    nar = st.actor("narrator", "none")
    steve = players.add_player(st, "steve", "steve")
    steve.place(f0, A["one_down"], fm.yaw["one_down"])
    steve.look_at(f0, fm.top_step.center, ease=0)
    m = fm.break_top_step(steve, f0 + 6, camera=s)
    # then down the steps, a hop per step, as the docstring says (k = 7, 6, ...)
    f = m["frame"] + 4
    hops = []
    for k in (7, 6, 5):
        f = towers.hop(steve, f, fm.set["stairs"][k]) + 2
        hops.append(f)
    np_ = (-21.25, 21.7, 10.0)
    nar.place(f0, np_, 0.0)
    nar.look_at(f0, (A["one_down"][0], A["one_down"][1], A["one_down"][2] + 1.5), ease=0)
    st.cast[fm.top_step.name] = fm.top_step
    st.use(s, nar, steve, fm.top_step)
    if outside:
        c = fm.cameras["stairs"]
        s.lens(c["lens"], c["fstop"])
        s.move(c["pos"], c["target"])
    else:
        s.lens(24, 2.8)
        s.move((-20.0, 18.4, 11.45), (-20.2, 24.0, 10.6))
    s.focus(steve.head)
    st.lights(s, scale=1.0, groups={"tower_pod": 1.0, "tower_cell": 1.0})
    st.finish()
    frames = [f0 + 5, m["start"] + 9, m["frame"] + 1, hops[0] - 4, hops[1]]
    if outside:
        frames = [m["frame"] + 3, hops[0] - 8, hops[0] - 3, hops[1] - 6, hops[2] - 4]
    info = dict(click=m["start"], broken=m["frame"], hops=hops, shot=(f0, s.frame_end),
                heroes={"narrator": nar.head, "steve": steve.head})
    return film, frames, info


def probe_b03():
    """Numbers only: the push along v.paths['tower_push_square'] on the plaza."""
    import bpy
    from engine import players, quick, towers, village, characters
    scene = quick.reset()
    quick.setup(scene)
    v = village.build_village(scene, seed=1, edit=lambda b: towers.iron_farm(b))
    path = v.paths["tower_push_square"]
    print("path", path)
    w = v.world
    blocked = []
    for i in range(0, 71):
        x = path[0][0] + (path[1][0] - path[0][0]) * i / 70.0
        y = path[0][1]
        for dy in (-0.3, 0.0, 0.3):
            for z in (int(math.floor(path[0][2])), int(math.floor(path[0][2])) + 1):
                c = (int(math.floor(x)), int(math.floor(y + dy)), z)
                if w.is_solid(*c):
                    blocked.append((c, w.block_id(*c)))
    print("solid cells within 0.3 of the push line at body height:", sorted(set(blocked)))
    steve = players.make_player("p_steve", "steve")
    mom = characters.make_villager("p_mom", "farmer")
    r = towers.push(steve, mom, 10, path)
    gap0 = steve.pos_at(10)
    print("push: %d frames for %.1f blocks; Steve starts at %s (path start %s)" % (r["end"] - 10, abs(path[1][0] - path[0][0]),
          tuple(round(a, 2) for a in gap0), path[0]))
    sx = int(math.floor(gap0.x))
    print("Steve's start cell solid?", w.is_solid(sx, int(math.floor(gap0.y)), int(math.floor(gap0.z))),
          w.block_id(sx, int(math.floor(gap0.y)), int(math.floor(gap0.z))))


def render(scene, film, frames, name):
    import bpy
    from PIL import Image, ImageDraw
    tiles = []
    for f in frames:
        t = time.time()
        film.goto(f)
        p = os.path.join(OUT, "check_towers_%s_f%d" % (name, f))
        scene.render.filepath = p
        scene.render.use_file_extension = True
        bpy.ops.render.render(write_still=True)
        tiles.append((f, Image.open(p + ".png").convert("RGB")))
        os.remove(p + ".png")
        print("[check] frame %d %.1f s" % (f, time.time() - t), flush=True)
    W, H = tiles[0][1].size
    sheet = Image.new("RGB", (W * len(tiles), H + 24), (20, 20, 20))
    d = ImageDraw.Draw(sheet)
    for i, (f, im) in enumerate(tiles):
        sheet.paste(im, (i * W, 24))
        d.text((i * W + 6, 6), "frame %d" % f, fill=(255, 255, 255))
    path = os.path.join(OUT, "check_towers_%s.png" % name)
    sheet.save(path)
    small = sheet.resize((sheet.width // 2, sheet.height // 2), Image.LANCZOS)
    small.save(path[:-4] + "_half.png")
    print("[check] -> %s" % path)


def main(argv):
    import bpy
    name = argv[0] if argv else "b24"
    if name == "b03":
        probe_b03()
        return 0
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    t0 = time.time()
    film, frames, info = globals()["probe_" + name](scene)
    print("[check] built in %.1f s; %s; frames %s" % (time.time() - t0, info, frames), flush=True)
    if "--plan" in argv:
        from bpy_extras.object_utils import world_to_camera_view
        for f in frames:
            film.goto(f)
            out = {}
            for k, ob in info.get("heroes", {}).items():
                q = world_to_camera_view(scene, scene.camera, ob.matrix_world.translation)
                out[k] = (round(100 * q.x), round(100 * (1 - q.y)), round(q.z, 2))
            print("[check] frame %d heads (x%%, y%%, depth) %s" % (f, out))
        return 0
    render(scene, film, frames, name)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
