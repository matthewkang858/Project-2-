"""Proof stills for engine/fixtures.py: chests, hopper, water, lava, glass and falling anvils in the REAL village
(edit hook, films.lookdev.Stage, engine.look's golden hour or night sky), 540x960, 16 samples, 2 threads.

    $BPY -m engine.fixtures stills chest hopper          # -> out/test/fixtures_<name>.png (10-30 s each: up to
                                                         #    eight names per call stay under the 300 s limit)
    $BPY -m engine.fixtures stills night night_flicker   # the night stills (another sky = another build)
    $BPY -m tools.fixtures_proof chest                   # the same
Each still is followed by tools.palette_check's report (printed). All shots exist in every build (keying is cheap);
a call renders only the frames of the names it is given.

Every structure stands in the flat meadow beyond the exit gate, away from the houses and the exit road (the hook
removes the ring oak at (-25, 37) and the meadow oak at (-13, 47) and clears the plants there):
  east of the road (x 3..14)   y 28..30  anvil wall (stone bricks, 8 high), a plank shelf (fixtures.block) over a
                                         cobblestone road with six anvils on it (fixtures.shelf: they fall, two chip),
                                         three standing anvils (anvil, chipped, damaged: village mesh)
                               y 34      Steve holding an anvil
                               y 40      four static chests (latch north / east / south / west) and a double chest
                               y 44      an animated chest (opens), a hopper on a chest (the ingot stream)
                               y 50      five hoppers: down, north, east, south, west
  west of the road             x -11..-5, y 29..36: the glass pod on its stone pillar (a cleric and a lantern inside,
                                         a librarian on the balcony north of it: behind two walls of glass)
                               x -19..-15, y 31..35: platform A: water as the GAME spreads it (sources along its
                                         north edge, flowing south: 8 7 6 5 4), a 2-wide lava slot south of it
                               x -19..-15, y 39..43: platform B: the film's cheat, a level sheet 1/9 deep (amount 1)
                                         drawn flowing south, the same slot (the golem slides into it)
                               x -21..-15, y 49..55: a 7 x 7 lava lake sunk in the ground ("far lava")
Names (golden hour): chest chest_open hopper hoppers platform_a platform_b platform_top slide pod_out pod_cut pod_in
lava_far anvils hold fall fallen flicker; night sky: night (platform A), night_far, night_flicker. Strips (several
frames side by side, 270x480 each): chest_open (3), hopper (5), fall (6), slide (5), flicker (6).
"""
import math
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "out", "test")
GOLD = dict(preset="golden", az=62.0, el=27.0, bloom=1.0, grade="warm")
NIGHT = dict(preset="night", az=176.0, el=21.0, bloom=1.3, grade="cool")

# shot name -> (seconds, frames to render as offsets into the shot (one = a still, several = a strip))
SHOTS = [
    ("chest", 1.0, [12]), ("chest_open", 2.0, [2, 9, 22]), ("hopper", 4.0, None), ("platform_a", 1.0, [12]),
    ("platform_b", 1.0, [12]), ("platform_top", 1.0, [12]), ("pod_out", 1.0, [12]), ("pod_cut", 1.0, [12]),
    ("pod_in", 1.0, [12]), ("lava_far", 1.0, [12]), ("anvils", 1.0, [12]), ("hold", 1.0, [12]),
    ("fall", 3.0, None), ("fallen", 1.0, [12]), ("slide", 5.0, None), ("hoppers", 1.0, [12]),
    ("flicker", 2.0, [4, 6, 8, 12, 20, 34]),
]
NIGHT_SHOTS = {"night": "platform_a", "night_far": "lava_far", "night_flicker": "flicker"}
STRIP_RES = (270, 480)


# ----------------------------------------------------------------------------------------------------
# the set (inside the village's edit hook)
# ----------------------------------------------------------------------------------------------------
def build_set(b):
    """Everything the stills need, put into the village through the edit hook. Returns a dict of handles."""
    from engine import fixtures as fx

    from engine import sets

    w = b.w
    out = {}
    for x, y in ((-25, 37), (-13, 47)):                      # a ring oak where the platform cameras stand, and
        oak = b.tree_at(x, y)                                # the meadow oak over the lava lake
        if oak is not None:
            sets.remove_tree(b, oak)
    zones = [(3, 27, 14, 60), (-31, 27, -4, 47), (-23, 47, -13, 57)]
    for x0, y0, x1, y1 in zones:
        for x in range(x0, x1 + 1):
            for y in range(y0, y1 + 1):
                b.clear_plants(x, y)
                b.reserved.add((x, y))

    # ---- east: the anvil wall and the road under it
    for x in range(3, 15):
        w.fill(x, 28, 0, x, 28, 7, "stone_bricks")
        w.set(x, 29, -1, "cobblestone")
        w.set(x, 30, -1, "cobblestone")
    planks = [fx.block(b, "oak_planks", (x, 29, 7)) for x in range(4, 10)]
    anvils = fx.shelf(b, [(x, 29, 8) for x in range(4, 10)], "anvil", {"facing": "north"})
    out.update(planks=planks, shelf=anvils)
    for i, (x, bid) in enumerate(((11, "anvil"), (12, "chipped_anvil"), (13, "damaged_anvil"))):
        w.set(x, 30, 0, bid, {"facing": "north"})      # static: part of the village mesh
    # ---- east: chests
    out["chests"] = [fx.chest(b, (x, 40, 0), f, animated=False) for x, f in
                     ((5, "north"), (7, "east"), (9, "south"), (11, "west"))]
    out["chest"] = fx.chest(b, (7, 44, 0), "north")
    out["double"] = fx.chest(b, (13, 40, 0), "south", animated=False, partner=(14, 40, 0))
    out["hoppers"] = [fx.hopper(b, (x, 50, 0), f) for x, f in ((4, "down"), (6, "north"), (8, "east"), (10, "south"),
                                                               (12, "west"))]
    out["hopper"], out["hopper_chest"] = fx.hopper_on_chest(b, (11, 44, 0), "north", animated=False)

    # ---- west: the glass pod on its pillar
    w.fill(-9, 30, 0, -7, 32, 2, "stone")
    w.fill(-11, 29, 3, -5, 36, 3, "stone")                   # the floor, with a balcony north of the glass
    out["pod"] = fx.glass_box(b, -11, 29, 4, -5, 33, 6, name="pod")
    b.torch((-6, 32, 4), "lantern", {"hanging": "false"}, group="pod")

    # ---- west: platform A (the game's flow) and B (the level sheet), each with a 2-wide lava slot to the west
    for name, y0 in (("a", 31), ("b", 39)):
        y1 = y0 + 4
        w.fill(-19, y0, 0, -15, y1, 2, "stone")              # the platform: solid, its top at z 3
        w.fill(-19, y0 - 3, -1, -15, y0 - 3, 3, "stone")     # the slot's outer wall (the slot: y0 - 2 .. y0 - 1)
        w.fill(-19, y0 - 2, -2, -15, y0 - 1, -2, "stone")    # under the lava
        if name == "a":
            water = fx.water(b, [(x, y, 3) for x in range(-19, -14) for y in range(y0, y1 + 1)],
                             sources=[(x, y1, 3) for x in range(-19, -14)], name="water_a")
        else:
            water = fx.water_sheet(b, -19, y0, -15, y1, 3, toward="south", amount=1, name="water_b")
        lava = fx.lava(b, [(x, y, -1) for x in range(-19, -14) for y in (y0 - 2, y0 - 1)], name="lava_" + name)
        out["water_" + name], out["lava_" + name] = water, lava
    # ---- west: the far lava lake
    w.fill(-21, 49, -2, -15, 55, -2, "stone")
    out["lake"] = fx.lava(b, [(x, y, -1) for x in range(-21, -14) for y in range(49, 56)], name="lake")
    b.v.sets["fixtures_proof"] = out
    return out


# ----------------------------------------------------------------------------------------------------
# the shots
# ----------------------------------------------------------------------------------------------------
def _cam(s, pos, target, lens, fstop=4.0, focus=None):
    s.lens(lens, fstop)
    s.move(pos, target)
    s.focus(focus if focus is not None else target)


def shot_chest(st, s, h):
    """Four static chests, latch north / east / south / west, a villager beside them for scale."""
    from films.lookdev import yaw_to

    f0 = s.frame_start
    vil = st.actor("chest_vil", "librarian")
    p = (8.0, 38.4, 0.0)
    vil.place(f0, p, yaw_to(p, (9.5, 33.0)))
    st.use(s, vil)
    _cam(s, (11.6, 31.4, 2.6), (10.5, 40.3, 0.8), 22, 5.6, (9.0, 39.0, 0.8))
    st.lights(s, scale=0.0)


def shot_chest_open(st, s, h):
    """The animated chest opening (frames: shut, opening, open), a villager beside it."""
    from films.lookdev import yaw_to

    f0 = s.frame_start
    c = h["chest"]
    c.open(f0 + 4)
    vil = st.actor("chest_vil2", "farmer")
    p = (8.75, 44.9, 0.0)
    vil.place(f0, p, yaw_to(p, (6.5, 46.5)))
    vil.look_at(f0, c.center, ease=0)
    st.use(s, vil)
    _cam(s, (8.3, 49.6, 1.7), (7.6, 44.5, 0.6), 38, 4.0, c.center)
    st.lights(s, scale=0.0)


def shot_hopper(st, s, h):
    """Three iron ingots and a poppy dropped onto the hopper one after another: they land and vanish in turn."""
    from engine import mobs

    f0 = s.frame_start
    hop = h["hopper"]
    items = []
    for i, iid in enumerate(("iron_ingot", "iron_ingot", "poppy", "iron_ingot")):
        it = mobs.make_dropped_item(iid, name="hop_%d" % i, seed=i)
        st.cast[it.name] = it
        st.use(s, it)
        items.append(it)
    plans = hop.stream(items, f0 + 2, every=6, height=2.2, spread=0.18, seed=3)
    h["hopper_plans"] = plans
    _cam(s, (13.6, 48.6, 3.0), (11.5, 44.5, 2.0), 35, 5.6, (11.5, 44.5, 1.7))
    st.lights(s, scale=0.0)


def shot_platform(st, s, h, which="a", top=False):
    """A golem standing in the water of platform A / B, the 2-wide lava slot to its west (seen from the south-west
    and a little below the floor, or from above)."""
    from engine import mobs

    f0 = s.frame_start
    y0 = 31 if which == "a" else 39
    g = st.cast.get("golem_" + which)
    if g is None:
        g = st.cast["golem_" + which] = mobs.make_iron_golem("golem_" + which)
    feet = (-17.0, y0 + 2.0, 3.0)
    g.place(f0, feet, math.radians(-135.0))          # three-quarter toward the camera, the pod to its right
    st.use(s, g)
    if top:
        _cam(s, (-24.0, y0 + 9.0, 12.0), (-17.0, y0 + 0.5, 2.0), 32, 5.6)
    else:
        _cam(s, (-25.6, y0 + 7.4, 3.7), (-17.0, y0 + 0.6, 3.2), 30, 5.6, (-17.0, y0 + 2.0, 3.6))
    st.lights(s, scale=1.0, near=(-16.0, y0, 3.0), radius=12.0)


def shot_pod(st, s, h, mode):
    """The glass pod: from outside (mode 'out'), from outside with its south wall hidden to the camera ('cut'),
    or from inside ('in'); a villager inside, the lantern on the floor."""
    from films.lookdev import yaw_to

    f0 = s.frame_start
    vil = st.actor("pod_vil", "cleric")
    out = st.actor("pod_vil2", "librarian")                  # outside, on the balcony: behind TWO walls of glass
    p, q = (-8.2, 31.3, 4.0), (-6.9, 35.0, 4.0)
    cam_in = (-9.6, 32.55, 5.3)
    vil.place(f0, p, yaw_to(p, cam_in if mode == "in" else (-3.0, 25.0)))
    out.place(f0, q, yaw_to(q, (-3.0, 25.0)))
    st.use(s, vil, out)
    if mode == "in":
        _cam(s, cam_in, (-7.0, 30.4, 4.9), 20, 5.6, vil.head)
    elif mode == "cut":
        st.see_through(s, "pod_south")
        _cam(s, (-5.5, 22.8, 5.6), (-8.0, 31.0, 4.8), 38, 5.6, vil.head)
    else:
        _cam(s, (-2.6, 25.4, 5.2), (-7.8, 32.2, 5.0), 32, 5.6, vil.head)
    st.lights(s, scale=1.0, groups={"pod": 1.0}, near=(-8.0, 31.0, 4.0), radius=6.0)


def shot_hoppers(st, s, h):
    """engine.blocks' hopper model in every facing: down, north, east, south, west (left to right)."""
    _cam(s, (8.5, 59.6, 1.7), (8.5, 50.5, 0.45), 20, 8.0)
    st.lights(s, scale=0.0)


def shot_flicker(st, s, h):
    """Something falls into platform A's slot ON frame f0 + 6: the lava light is smothered, flares and settles."""
    f0 = s.frame_start
    h["lava_a"].flicker(f0, f0 + 40, at=f0 + 6)
    _cam(s, (-23.6, 26.2, 2.6), (-17.0, 29.6, 0.8), 28, 5.6)
    st.lights(s, scale=0.0)


def shot_lava_far(st, s, h):
    """The far lava lake from bridge height (13 blocks up, 12 blocks back)."""
    _cam(s, (-9.8, 42.5, 13.0), (-18.0, 52.0, -0.5), 45, 8.0)
    st.lights(s, scale=0.0)


def shot_anvils(st, s, h):
    """The anvil, the chipped anvil and the damaged anvil side by side on the road, close."""
    _cam(s, (12.4, 34.4, 2.6), (12.2, 30.5, 0.55), 24, 5.6, (12.0, 30.5, 0.6))
    st.lights(s, scale=0.0)


def shot_hold(st, s, h):
    """Steve holding an anvil (the block item's third-person transform)."""
    from engine import players

    from films.lookdev import yaw_to

    f0 = s.frame_start
    p = players.add_player(st, "steve")
    pos = (9.0, 34.5, 0.0)
    p.place(f0, pos, yaw_to(pos, (11.5, 37.6)))
    p.hold("anvil")
    st.use(s, p)
    _cam(s, (11.0, 37.4, 1.7), (9.0, 34.5, 1.15), 45, 4.0, p.head)
    st.lights(s, scale=0.0)


def shot_fall(st, s, h):
    """The planks are pulled ON frame f0 + 6, the six anvils hang two ticks and fall, two of them chip."""
    from engine import fixtures as fx

    f0 = s.frame_start + 6
    for pl in h["planks"]:
        pl.remove(f0)
    drops = fx.release(h["shelf"], f0, world=st.v, chip=[1, 4])
    h["drops"] = drops
    _cam(s, (13.0, 38.5, 1.3), (6.5, 29.5, 4.0), 24, 8.0)
    st.lights(s, scale=0.0)


def shot_fallen(st, s, h):
    """After the fall: six anvils standing on the cobblestones, two chipped."""
    _cam(s, (10.6, 33.6, 3.0), (6.6, 29.6, 0.4), 28, 5.6)
    st.lights(s, scale=0.0)


def shot_slide(st, s, h):
    """The golem on platform B pushed west by the current, over the rim and down into the slot."""
    from engine import fixtures as fx
    from engine import mobs

    f0 = s.frame_start
    g = st.cast.get("golem_slide")
    if g is None:
        g = st.cast["golem_slide"] = mobs.make_iron_golem("golem_slide")
    start = (-17.0, 41.5, 3.0)
    g.place(f0, start, math.radians(90.0))           # facing west, the current pushes it south: sideways
    # its middle must be 0.7 past the rim (y 39) before it falls: 2.5 + 0.7 blocks, then 3.9 down into the lava
    r = fx.slide(g, f0 + 4, "south", 3.2, drop=3.9)
    h["slide"] = r
    st.use(s, g)
    _cam(s, (-26.6, 40.0, 3.4), (-17.0, 38.8, 2.6), 30, 5.6, (-17.0, 39.5, 3.2))
    st.lights(s, scale=1.0, near=(-16.0, 37.0, 3.0), radius=12.0)


BUILDERS = {
    "chest": shot_chest, "chest_open": shot_chest_open, "hopper": shot_hopper,
    "platform_a": lambda st, s, h: shot_platform(st, s, h, "a"),
    "platform_b": lambda st, s, h: shot_platform(st, s, h, "b"),
    "platform_top": lambda st, s, h: shot_platform(st, s, h, "a", top=True),
    "pod_out": lambda st, s, h: shot_pod(st, s, h, "out"), "pod_cut": lambda st, s, h: shot_pod(st, s, h, "cut"),
    "pod_in": lambda st, s, h: shot_pod(st, s, h, "in"), "lava_far": shot_lava_far, "anvils": shot_anvils,
    "hold": shot_hold, "fall": shot_fall, "fallen": shot_fallen, "slide": shot_slide, "hoppers": shot_hoppers,
    "flicker": shot_flicker,
}


def build(scene, sky=None, res=(540, 960), samples=16, threads=2):
    """The village with the test set, one shot per entry of SHOTS (all of them, in order: a strip or still renders
    only its own frames). Returns dict(film, stage, village, set, frames {name: [frame, ...]})."""
    from engine import look, shots, village
    from films.lookdev import Stage

    sky = sky or GOLD
    look.setup_render(scene, res=res, samples=samples, threads=threads)
    out = {}
    v = village.build_village(scene, seed=1, edit=lambda b: out.update(build_set(b)))
    sk = look.set_time(scene, sky["preset"], sun_azimuth=sky["az"], sun_elevation=sky["el"])
    look.setup_compositor(scene, bloom=sky["bloom"], grade=sky["grade"])
    film = shots.Film(scene, fps=24)
    st = Stage(scene, film, v, sk)
    frames = {}
    for name, secs, offs in SHOTS:
        s = st.shot(name, secs)
        BUILDERS[name](st, s, out)
        if offs is None:
            offs = _strip_offsets(name, s, out)
        frames[name] = [s.frame_start + o for o in offs]
    st.finish()
    return dict(film=film, stage=st, village=v, set=out, frames=frames)


def _strip_offsets(name, s, h):
    """Frames of the strips that follow the action: the hopper's takes, the anvils' fall, the golem's slide."""
    f0 = s.frame_start
    if name == "hopper":
        plans = h["hopper_plans"]
        lands = [p["landed"] for p in plans if p["landed"] is not None]
        takes = [p["frame"] for p in plans]
        want = [lands[0] - 4 if lands else f0 + 6, lands[0] + 2 if lands else f0 + 10, takes[0], takes[1] + 1,
                takes[-1] + 2]
        return [w - f0 for w in want]
    if name == "fall":
        d = h["drops"][0]
        a, z = d["frame_release"], d["frame_land"]
        return [a - 1 - f0, a + 3 - f0, (a + z) // 2 - f0, z - 3 - f0, z - 1 - f0, z + 1 - f0]
    if name == "slide":
        r = h["slide"]
        a, e, g = r["frame"], r["edge"], r["gone"] or r["frame_end"]
        return [a - f0, (a + e) // 2 - f0, e - f0, (e + g) // 2 - f0, g - f0]
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
    """tools.palette_check on a rendered still (printed; returns the number of failed checks)."""
    from tools import palette_check as pc

    film.goto(frame)
    rec = pc.probe(scene)
    rep = pc.evaluate(rec, path, heroes=heroes)
    pc.print_report(name, rep)
    return rep


def render(names, night=False):
    """Render the named stills / strips to out/test/fixtures_<name>.png."""
    import bpy
    from PIL import Image, ImageDraw

    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    t0 = time.time()
    built = build(scene, NIGHT if night else GOLD)
    film = built["film"]
    print("[fixtures proof] built in %.1f s" % (time.time() - t0), flush=True)
    os.makedirs(OUT, exist_ok=True)
    for name in names:
        shot = NIGHT_SHOTS.get(name, name) if night else name
        frames = built["frames"][shot]
        path = os.path.join(OUT, "fixtures_%s.png" % name)
        t = time.time()
        if len(frames) == 1:
            _render(scene, film, frames[0], path)
            _check(scene, film, frames[0], path, name)
        else:
            r = scene.render
            full = (r.resolution_x, r.resolution_y)
            r.resolution_x, r.resolution_y = STRIP_RES
            tiles = []
            for f in frames:
                p = os.path.join(OUT, "fixtures_%s_f%d.png" % (name, f))
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
        print("[fixtures proof] %-12s frames %s -> %s  %.1f s" % (name, frames, path, time.time() - t), flush=True)
    return built


def main(argv):
    """Command line: names (see the module docstring); 'night' / 'night_far' build the night sky."""
    names = [a for a in argv if not a.startswith("-")] or ["chest"]
    night = [n for n in names if n in NIGHT_SHOTS]
    gold = [n for n in names if n not in NIGHT_SHOTS]
    unknown = [n for n in gold if n not in BUILDERS]
    if unknown:
        print("unknown proof names %s; known: %s %s" % (unknown, sorted(BUILDERS), sorted(NIGHT_SHOTS)))
        return 2
    if gold:
        render(gold)
    if night:
        render(night, night=True)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
