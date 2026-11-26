"""Proof stills for engine/towers.py: the iron farm tower of "Twenty Minutes" in the REAL village (the edit hook,
films.lookdev.Stage, engine.look's golden hour or dusk), 540x960, 16 samples, 2 threads.

    $BPY -m engine.towers stills square pod_out           # -> out/test/towers_<name>.png (one build per call:
    $BPY -m tools.towers_proof square pod_out              #    at most 4-5 names per call stay under 300 s)
    $BPY -m engine.towers stills square_dusk pod_out_dusk  # the same shots under the dusk sky (another build)
    TOWERS_RES=270x480 TOWERS_SAMPLES=8 $BPY -m tools.towers_proof square     # quick framing tests
Each still is followed by tools.palette_check's report (printed). Every shot exists in every build (keying is
cheap); a call renders only the frames of the names it is given. Strips (several frames side by side, 270x480
each, motion blur on): slide (the golem appears, slides, drops into the glowing slot), hopper (an ingot and a
poppy fall into the hopper), stairs (the top step cracks and breaks), bounce, push.
"""
import math
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "out", "test")
GOLD = dict(preset="golden", az=62.0, el=27.0, bloom=1.0, grade="warm")
DUSK = dict(preset="dusk", az=187.0, el=5.0, bloom=1.3, grade="warm")
STRIP_RES = (270, 480)

# shot name -> (seconds, frames to render as offsets into the shot (one = a still, several = a strip))
SHOTS = [
    ("square", 1.0, [12]), ("square_wide", 1.0, [12]), ("foot", 1.0, [12]), ("push", 6.0, None), ("pod_out", 1.0, [12]),
    ("pod_in", 1.0, [12]), ("cell_side", 2.0, [36]), ("platform", 1.5, [20]), ("two_shot", 1.0, [12]), ("back", 1.0, [12]), ("gap", 1.0, [12]),
    ("bounce", 4.0, None), ("lineup", 1.0, [12]), ("slide", 6.0, None), ("hopper", 5.0, None),
    ("grow", 2.0, None), ("high", 2.0, [30]), ("stairs", 3.0, None),
]
DUSK_SHOTS = {"square_dusk": "square_wide", "pod_out_dusk": "pod_out", "pod_in_dusk": "pod_in",
              "cell_side_dusk": "cell_side"}


# ----------------------------------------------------------------------------------------------------
# the shots
# ----------------------------------------------------------------------------------------------------
def _cam(s, cam, focus=None):
    s.lens(cam["lens"], cam.get("fstop", 4.0))
    s.move(cam["pos"], cam["target"])
    s.focus(focus if focus is not None else cam.get("focus", cam["target"]))


def _pod_cast(st, fm, s, f0, mom_spot="mom", zombie=True, others=True, panic=False):
    """Mom (farmer) at a spot looking at the zombie, the cleric and the librarian, the zombie in its cell."""
    from engine import towers, undead

    mom = st.actor("mom", "farmer")
    cast = [mom]
    mom.place(f0, fm.A[mom_spot], fm.yaw[mom_spot])
    if others:
        cl, li = st.actor("cleric", "cleric"), st.actor("librarian", "librarian")
        cl.place(f0, fm.A["back_2"], fm.yaw["back_2"])
        li.place(f0, fm.A["back_3"], fm.yaw["back_3"])
        cast += [cl, li]
    z = None
    if zombie:
        z = st.cast.get("zombie") or undead.add_zombie(st, "zombie")
        fm.zombie_in_cell(z, f0, look=mom)
        cast.append(z)
    for c in cast:
        if c is not z:
            if panic:
                towers.panic(c, f0, s.frame_end, fm.zombie_eye, seed=hash(c.name) % 97)
            else:
                c.look_at(f0, fm.zombie_eye, ease=0)
    st.use(s, *cast)
    return cast


def shot_square(st, s, fm, h):
    """Beat 4: over the baby's shoulder by the well, the tower above the roofs."""
    f0 = s.frame_start
    baby = st.actor("baby", "none", child=True)
    p = fm.A["square_baby"]
    baby.place(f0, p, fm.yaw["square_baby"])
    baby.look_at(f0, fm.A["pod_target"], ease=0)
    mom = st.actor("mom", "farmer")
    mom.place(f0, fm.A["mom_glass"], fm.yaw["mom_glass"])
    mom.look_at(f0, fm.zombie_eye, ease=0)
    st.use(s, baby, mom)
    _cam(s, fm.cameras["square"])
    st.lights(s, scale=1.0, groups={fm.set["lights"][0]: 1.0, fm.set["lights"][1]: 1.0})


def shot_square_wide(st, s, fm, h):
    """The establishing wide from the plaza: the well and the bell in front, the tower above the roofs."""
    f0 = s.frame_start
    mom = st.actor("mom", "farmer")
    mom.place(f0, fm.A["mom_glass"], fm.yaw["mom_glass"])
    mom.look_at(f0, fm.zombie_eye, ease=0)
    st.use(s, mom)
    _cam(s, fm.cameras["square_wide"])
    st.lights(s, scale=1.0)


def shot_foot(st, s, fm, h):
    """Beat 5: the baby at the front of the stone base, full figure, head up."""
    f0 = s.frame_start
    baby = st.actor("baby", "none", child=True)
    baby.place(f0, fm.A["foot_front"], fm.yaw["foot_front"])
    up = baby.pos_at(f0)
    baby.look_at(f0, (up.x + 0.8, up.y - 2.0, up.z + 4.0), ease=0)
    st.use(s, baby)
    st.hero(s, "baby", baby)
    _cam(s, fm.cameras["foot"], focus=baby.head)
    st.lights(s, scale=1.0)


def shot_pod_out(st, s, fm, h):
    """The pod from outside: villagers in their beds, Mom up, the zombie in its cell, one pane hidden."""
    from engine import undead

    f0 = s.frame_start
    cast = []
    for key, prof in (("white_1", "cleric"), ("white_2", "librarian")):
        c = st.actor(prof, prof)
        bed = fm.beds[key]
        c.lie_down(f0, bed["pos"], bed["yaw"])
        cast.append(c)
    mom = st.actor("mom", "farmer")
    mom.place(f0, fm.A["bed_side"], fm.yaw["bed_side"])
    mom.look_at(f0, fm.zombie_eye, ease=0)
    z = st.cast.get("zombie") or undead.add_zombie(st, "zombie")
    fm.zombie_in_cell(z, f0, look=mom)
    st.use(s, mom, z, *cast)
    cam = fm.cameras["pod_out"]
    _cam(s, cam, focus=mom.head)
    pillow = fm.beds["white_2"]["head"]
    mp = fm.A["bed_side"]
    pts = [mom, (mp[0], mp[1], mp[2] + 0.5), fm.zombie_eye]
    for key in ("white_1", "white_2", "mom"):
        bd = fm.beds[key]
        pts += [(bd["head"][0], bd["head"][1], bd["head"][2] + 0.3), (bd["foot"][0], bd["foot"][1], bd["foot"][2] + 0.3)]
    fm.see_through(st, s, cam, points=pts)
    st.hero(s, "mom", mom)
    st.lights(s, scale=1.0, groups={fm.set["lights"][0]: 1.0, fm.set["lights"][1]: 1.0})


def shot_pod_in(st, s, fm, h):
    """Beat 6/8: inside at villager eye height, Mom by the window, the cleric and librarian against the glass."""
    f0 = s.frame_start
    cast = _pod_cast(st, fm, s, f0, panic=True)
    _cam(s, fm.cameras["pod_in"], focus=cast[0].head)
    st.hero(s, "mom", cast[0])
    st.lights(s, scale=1.0, groups={fm.set["lights"][0]: 1.0, fm.set["lights"][1]: 1.0})


def shot_cell_side(st, s, fm, h, camera="cell_side"):
    """Beats 8 / 23 / 24: from beside the zombie cell, the three backed against the far glass, trembling, heads on
    the zombie; through the glass a golem appears on the platform (beat 24)."""
    from engine import mobs, towers, undead

    f0 = s.frame_start
    cast = []
    for i, (n, prof) in enumerate((("mom", "farmer"), ("cleric", "cleric"), ("librarian", "librarian"))):
        c = st.actor(n, prof)
        c.place(f0, fm.A["back_%d" % (i + 1)], fm.yaw["back_%d" % (i + 1)])
        towers.panic(c, f0, s.frame_end, fm.zombie_eye, seed=11 if n == "mom" else 20 + i)
        cast.append(c)
    z = st.cast.get("zombie") or undead.add_zombie(st, "zombie")
    fm.zombie_in_cell(z, f0, aggro=True, look=cast[0])
    g = st.cast.get("golem")
    if g is None:
        g = st.cast["golem"] = mobs.make_iron_golem("golem")
    fm.golem_spawn(g, f0 + 12, pos=(fm.A["golem_spawn"][0] - 0.3, fm.A["golem_spawn"][1] + 1.6, fm.L["F"]),
                   yaw=math.radians(-60.0), look=fm.A["pod_target"], look_after=4)
    st.use(s, z, g, *cast)
    st.hero(s, "mom", cast[0])
    _cam(s, fm.cameras[camera], focus=cast[1].head)
    st.lights(s, scale=1.0, groups={fm.set["lights"][0]: 1.0, fm.set["lights"][1]: 1.0})


def shot_platform(st, s, fm, h):
    """Beat 9: low on the platform, a golem appears out of nothing and turns its head to the pod."""
    from engine import mobs

    f0 = s.frame_start
    g = st.cast.get("golem")
    if g is None:
        g = st.cast["golem"] = mobs.make_iron_golem("golem")
    fm.golem_spawn(g, f0 + 4, yaw=math.radians(-150.0), look=fm.A["pod_target"], look_after=4)
    cast = []
    for i, (n, prof) in enumerate((("mom", "farmer"), ("cleric", "cleric"), ("librarian", "librarian"))):
        c = st.actor(n, prof)
        c.place(f0, fm.A["back_%d" % (i + 1)], fm.yaw["back_%d" % (i + 1)])
        c.look_at(f0, fm.zombie_eye, ease=0)
        cast.append(c)
    st.use(s, g, *cast)
    st.hero(s, "golem", g)
    _cam(s, fm.cameras["platform"], focus=g.head)
    st.lights(s, scale=1.0, groups={fm.set["lights"][0]: 1.0, fm.set["lights"][1]: 1.0})


def shot_two_shot(st, s, fm, h):
    """Beat 7: the zombie's arms out of the window, one empty block, Mom's face (long lens, profile)."""
    f0 = s.frame_start
    cast = _pod_cast(st, fm, s, f0, others=False)
    cast[-1].aggro(f0, ease=0)
    st.see_through(s, fm.name + "_pod_north")
    _cam(s, fm.cameras["two_shot"], focus=cast[0].head)
    st.hero(s, "mom", cast[0])
    st.lights(s, scale=1.0, groups={fm.set["lights"][0]: 1.0, fm.set["lights"][1]: 1.0})


def shot_high(st, s, fm, h):
    """Beat 21: high over Steve's shoulder, the roof hidden to the camera: four in a row, the second bed appears."""
    from engine import players

    f0 = s.frame_start
    names = (("librarian", "librarian"), ("cleric", "cleric"), ("narrator", "none"), ("mom", "farmer"))
    cast = []
    steve = players.add_player(st, "steve", "steve")
    steve.place(f0, fm.A["top_step"], fm.yaw["top_step"])
    for i, (n, prof) in enumerate(names):
        c = st.actor(n, prof)
        c.place(f0, fm.A["row_%d" % (i + 1)], fm.yaw["row_%d" % (i + 1)])
        cast.append(c)
    for c in cast[:2]:
        c.look_at(f0, (c.pos_at(f0).x - 3.0, c.pos_at(f0).y - 1.0, fm.L["F"] + 1.6), ease=0)
    cast[2].look_at(f0, steve, ease=0)
    cast[3].look_at(f0, fm.zombie_eye, ease=0)
    steve.watch(f0, s.frame_end, cast[2])
    steve.attack(f0 + 18)
    fm.bed2.place_at(f0 + 20)
    st.use(s, steve, *cast)
    st.see_through(s, fm.name + "_pod_roof")
    _cam(s, fm.cameras["high"], focus=cast[2].head)
    st.lights(s, scale=1.0, groups={fm.set["lights"][0]: 1.0, fm.set["lights"][1]: 1.0})


def shot_slide(st, s, fm, h):
    """Beats 9-11: a golem appears on the platform, turns its head to the pod, slides west and drops into the slot;
    the puff, the glow's flicker."""
    from engine import mobs

    f0 = s.frame_start
    g = st.cast.get("golem")
    if g is None:
        g = st.cast["golem"] = mobs.make_iron_golem("golem")
    fm.golem_spawn(g, f0 + 6, look=fm.A["pod_target"], look_after=8)
    e = fm.golem_step(g, f0 + 30)
    r = fm.golem_slide(g, e + 2)
    d = fm.golem_death(g, r, camera=s)
    h["slide"] = dict(r, death=d, spawn=f0 + 6)
    st.use(s, g)
    _cam(s, fm.cameras["slide"], focus=fm.A["golem_spawn"])
    st.lights(s, scale=1.0)


def shot_hopper(st, s, fm, h):
    """Beat 11: three iron ingots and a poppy land on the hopper and vanish; poppies lie on the grass; Steve with
    an ingot."""
    from engine import mobs, players

    f0 = s.frame_start
    items = []
    for i, iid in enumerate(("iron_ingot", "iron_ingot", "poppy", "iron_ingot")):
        it = mobs.make_dropped_item(iid, name="hop_%d" % i, seed=i)
        st.cast[it.name] = it
        items.append(it)
    plans = fm.deliver(items, f0 + 4, every=7, seed=2)
    lying = []
    for i in range(5):
        it = mobs.make_dropped_item("poppy", name="lying_%d" % i, seed=10 + i)
        st.cast[it.name] = it
        lying.append(it)
    cam = fm.cameras["hopper"]
    cx, cy = fm.L["chest"][0] + 0.5, fm.L["chest"][1] + 0.5
    spots = [(cx - 0.55, cy + 1.75), (cx + 0.7, cy + 2.15), (cx - 0.1, cy + 2.6), (cx + 1.15, cy + 1.6),
             (cx - 1.05, cy + 2.35)]
    fm.strew(lying, f0, s.frame_end + 1, seed=3, spots=spots, face=cam["pos"])
    steve = players.add_player(st, "steve", "steve")
    steve.hold("iron_ingot")
    steve.place(f0, fm.A["chest_aside"], fm.yaw["chest_aside"])
    st.use(s, steve, *(items + lying))
    h["hopper"] = plans
    _cam(s, cam, focus=fm.A["hopper_target"])
    st.lights(s, scale=1.0)


def shot_stairs(st, s, fm, h):
    """Beat 22: Steve one step down breaks the top dirt step by hand (cracks, then the crumbs)."""
    from engine import players

    f0 = s.frame_start
    steve = players.add_player(st, "steve", "steve")
    steve.place(f0, fm.A["one_down"], fm.yaw["one_down"])
    steve.look_at(f0, fm.top_step.center, ease=0)
    m = fm.break_top_step(steve, f0 + 10, camera=s)
    h["stairs"] = m
    st.cast[fm.top_step.name] = fm.top_step
    st.use(s, steve, fm.top_step)
    _cam(s, fm.cameras["stairs"], focus=fm.top_step.center)
    st.lights(s, scale=1.0)


def shot_lineup(st, s, fm, h):
    """The narrator: baby, the grown narrator (unemployed: plain brown robe), a nitwit (green robe) side by side."""
    f0 = s.frame_start
    spot = fm.A["lineup"]
    who = (("lineup_baby", "none", True), ("narrator_adult", "none", False), ("lineup_nitwit", "nitwit", False))
    cast = []
    for i, (n, prof, child) in enumerate(who):
        c = st.actor(n, prof, child=child) if child else st.actor(n, prof)
        p = (spot[0], spot[1] + 0.95 - i * 0.95, spot[2])
        c.place(f0, p, fm.yaw["lineup"])
        cast.append(c)
    st.use(s, *cast)
    _cam(s, fm.cameras["lineup"], focus=cast[1].head)
    st.lights(s, scale=1.0)


def shot_back(st, s, fm, h):
    """Beat 12: the back of the tower, locked tall: the dirt zigzag, the stray dirt, the baby at the foot."""
    f0 = s.frame_start
    baby = st.actor("baby", "none", child=True)
    baby.place(f0, fm.A["stairs_foot"], fm.yaw["stairs_foot"])
    baby.look_at(f0, fm.A["stairs_target"], ease=0)
    st.use(s, baby)
    _cam(s, fm.cameras["back"])
    st.lights(s, scale=1.0)


def shot_gap(st, s, fm, h):
    """Beat 14: inside at floor level, the gap in the middle, the cleric against the plug, the baby under it."""
    f0 = s.frame_start
    cl = st.actor("cleric", "cleric")
    cl.place(f0, fm.A["gap_side"], fm.yaw["gap_side"])
    baby = st.actor("baby", "none", child=True)
    baby.place(f0, (fm.A["gap_in"][0] + 0.1, fm.A["gap_in"][1] + 0.75, fm.A["gap_in"][2]), 0.0)
    st.use(s, cl, baby)
    _cam(s, fm.cameras["gap"], focus=fm.A["gap_target"])
    st.lights(s, scale=1.0, groups={fm.set["lights"][0]: 1.0, fm.set["lights"][1]: 1.0})


def shot_bounce(st, s, fm, h):
    """Beat 17: the baby bounces twice on Mom's red bed."""
    from engine import towers

    f0 = s.frame_start
    baby = st.actor("baby", "none", child=True)
    e = fm.bounce(baby, f0 + 2, "mom", jumps=1)
    h["bounce"] = (f0 + 2, e)
    mom = st.actor("mom", "farmer")
    mom.place(f0, fm.A["bed_side"], fm.yaw["bed_side"])
    mom.look_at(f0, fm.zombie_eye, ease=0)
    st.use(s, baby, mom)
    _cam(s, fm.cameras["bounce"], focus=baby.head)
    st.lights(s, scale=1.0, groups={fm.set["lights"][0]: 1.0, fm.set["lights"][1]: 1.0})


def shot_push(st, s, fm, h):
    """Beat 3: Steve shoves Mom along the ground toward the tower (side-on)."""
    from engine import players, towers

    f0 = s.frame_start
    steve = players.add_player(st, "steve", "steve")
    mom = st.actor("mom", "farmer")
    route = fm.set["push_route"]
    r = towers.push(steve, mom, f0 + 2, route)
    mom.look_at(f0 + 2, (route[0][0] - 1.0, route[0][1] + 4.0, 1.6), ease=0)
    h["push"] = r
    st.use(s, steve, mom)
    _cam(s, fm.cameras["push"], focus=mom.head)
    st.lights(s, scale=1.0)


def shot_grow(st, s, fm, h):
    """Beats 16 / 18: the locked side view at the front glass; the baby at Mom's folded arms snaps to the grown
    narrator (unemployed, plain brown robe) in one frame. Mom's head stays on the zombie."""
    from engine import towers

    f0 = s.frame_start
    mom = st.actor("mom", "farmer")
    mom.place(f0, fm.A["mom_glass"], fm.yaw["mom_glass"])
    mom.look_at(f0, fm.zombie_eye, ease=0)
    baby = st.actor("baby", "none", child=True)
    baby.place(f0, fm.A["baby_glass"], fm.yaw["baby_glass"])
    baby.look_at(f0, fm.zombie_eye, ease=0)
    adult = st.actor("narrator", "none")
    f = f0 + 24
    towers.grow_up(baby, adult, f, look=fm.zombie_eye)
    h["grow"] = f
    st.use(s, mom, baby, adult)
    _cam(s, fm.cameras["grow"], focus=mom.head)
    st.lights(s, scale=1.0, groups={fm.set["lights"][0]: 1.0, fm.set["lights"][1]: 1.0})


BUILDERS = {name: globals()["shot_" + name] for name, _secs, _offs in SHOTS}


def build(scene, sky=None, res=(540, 960), samples=16, threads=2):
    """The village with the tower, one shot per entry of SHOTS. Returns dict(film, stage, village, farm, frames)."""
    from engine import look, shots, towers, village
    from films.lookdev import Stage

    sky = sky or GOLD
    look.setup_render(scene, res=res, samples=samples, threads=threads)
    v = village.build_village(scene, seed=1, edit=lambda b: towers.iron_farm(b))
    fm = towers.farm(v)
    sk = Stage.build_sky(scene, sky)
    film = shots.Film(scene, fps=24)
    st = Stage(scene, film, v, sk)
    h = dict(sky=sky)
    frames = {}
    for name, secs, offs in SHOTS:
        s = st.shot(name, secs)
        BUILDERS[name](st, s, fm, h)
        if offs is None:
            offs = _strip_offsets(name, s, h)
        frames[name] = [s.frame_start + o for o in offs]
    st.finish()
    return dict(film=film, stage=st, village=v, farm=fm, frames=frames, h=h)


def _strip_offsets(name, s, h):
    f0 = s.frame_start
    if name == "slide":
        r = h["slide"]
        return [r["spawn"] - f0 - 1, r["spawn"] - f0, r["frame"] + 14 - f0, r["edge"] - f0 + 2,
                r["gone"] - f0 - 2, r["gone"] - f0 + 6]
    if name == "hopper":
        plans = h["hopper"]
        first = int(round(plans[0]["track"][0][0]))
        return [first - 1 - f0, first + 4 - f0, plans[0]["frame"] - f0, plans[2]["frame"] - 2 - f0,
                plans[-1]["frame"] + 1 - f0]
    if name == "stairs":
        m = h["stairs"]
        a, z = m["start"], m["frame"]
        return [a - 1 - f0, a + (z - a) // 3 - f0, a + 2 * (z - a) // 3 - f0, z - 1 - f0, z + 3 - f0]
    if name == "grow":
        f = h["grow"]
        return [f - 1 - f0, f - f0]
    if name == "bounce":
        a, e = h["bounce"]
        return [a - f0 + k for k in (0, 3, 6, 10, 14)] + [min(e, s.frame_end) - f0]
    if name == "push":
        r = h["push"]
        e = r["end"]
        n = min(e, s.frame_end) - f0
        return [2] + [int(2 + (n - 2) * k / 5.0) for k in range(1, 6)]
    return [12]


# ----------------------------------------------------------------------------------------------------
# rendering
# ----------------------------------------------------------------------------------------------------
def _render(scene, film, frame, path):
    import bpy

    film.goto(frame)
    tmp = path[:-4] + "_part"
    scene.render.filepath = tmp
    scene.render.use_file_extension = True
    bpy.ops.render.render(write_still=True)
    os.replace(tmp + ".png", path)
    return path


def _check(scene, film, frame, path, name, heroes=()):
    from tools import palette_check as pc

    film.goto(frame)
    rec = pc.probe(scene)
    rep = pc.evaluate(rec, path, heroes=heroes)
    pc.print_report(name, rep)
    return rep


def _env_res():
    r = os.environ.get("TOWERS_RES")
    if r:
        w, h = r.lower().split("x")
        return int(w), int(h)
    return 540, 960


def render(names, dusk=False):
    """Render the named stills / strips to out/test/towers_<name>.png (dusk=True: the dusk sky)."""
    import bpy
    from PIL import Image, ImageDraw

    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    t0 = time.time()
    res = _env_res()
    samples = int(os.environ.get("TOWERS_SAMPLES", "16"))
    built = build(scene, DUSK if dusk else GOLD, res=res, samples=samples)
    film = built["film"]
    print("[towers proof] built in %.1f s" % (time.time() - t0), flush=True)
    os.makedirs(OUT, exist_ok=True)
    tag = os.environ.get("TOWERS_TAG", "")
    reports = {}
    for name in names:
        shot = DUSK_SHOTS.get(name, name) if dusk else name
        frames = built["frames"][shot]
        if os.environ.get("TOWERS_FRAMES"):
            frames = [built["film"].shots_by_name[shot].frame_start + int(o)
                      for o in os.environ["TOWERS_FRAMES"].split(",")] if hasattr(built["film"], "shots_by_name") \
                else frames
        path = os.path.join(OUT, "towers_%s%s.png" % (name, tag))
        t = time.time()
        if len(frames) == 1:
            _render(scene, film, frames[0], path)
            heroes = [ob for _l, obs in built["stage"].heroes.get(shot, []) for ob in obs]
            reports[name] = _check(scene, film, frames[0], path, name, heroes=heroes)
        else:
            r = scene.render
            full = (r.resolution_x, r.resolution_y)
            r.resolution_x, r.resolution_y = STRIP_RES
            tiles = []
            for f in frames:
                p = os.path.join(OUT, "towers_%s_f%d.png" % (name, f))
                _render(scene, film, f, p)
                tiles.append((f, Image.open(p).convert("RGB")))
                os.remove(p)
            r.resolution_x, r.resolution_y = full
            W, H = STRIP_RES
            sheet = Image.new("RGB", (W * len(tiles), H + 22), (20, 20, 20))
            d = ImageDraw.Draw(sheet)
            for i, (f, im) in enumerate(tiles):
                sheet.paste(im, (i * W, 22))
                d.text((i * W + 6, 5), "frame %d" % f, fill=(255, 255, 255))
            sheet.save(path)
        print("[towers proof] %-12s frames %s -> %s  %.1f s" % (name, frames, path, time.time() - t), flush=True)
    return built, reports


def main(argv):
    """Command line: names (see the module docstring)."""
    names = [a for a in argv if not a.startswith("-")] or ["square"]
    dusk = [n for n in names if n in DUSK_SHOTS]
    gold = [n for n in names if n not in DUSK_SHOTS]
    unknown = [n for n in gold if n not in BUILDERS]
    if unknown:
        print("unknown proof names %s; known: %s %s" % (unknown, sorted(BUILDERS), sorted(DUSK_SHOTS)))
        return 2
    failed = 0
    for group, is_dusk in ((gold, False), (dusk, True)):
        if group:
            _built, reports = render(group, dusk=is_dusk)
            failed += sum(len(r["failed"]) for r in reports.values())
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
