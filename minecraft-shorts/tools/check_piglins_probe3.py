"""Independent checker's probe 3 of engine/piglins.py: what the shot list of the piglin film (SHOTLISTS.md) asks of
it. Numbers first, then stills with the films' render settings.

Run:  $BPY -m tools.check_piglins_probe3 [num] [side] [pit:<offset> ...] [low]
Stills: out/test/check_piglins_probe3_*.png
"""
import math
import os
import sys
import time

import bpy
from mathutils import Vector


def numbers(scene):
    from engine import characters as ch
    from engine import mobs, piglins

    print("--- walk off a rim (the shot list: 'three piglins step off the rim and drop in')")
    p = piglins.make_piglin("faller")
    p.place(1, (0, 0, 0), 0.0)
    try:
        end = p.walk(1, [(0, 0, 0), (0, -1.5, 0), (0, -2.2, -2.0)])
        zs = [(f, round(p.pos_at(f).y, 2), round(p.pos_at(f).z, 2)) for f in range(1, end + 1, 4)]
        print("   walk with a 2-block drop in its last leg ends", end, "| (frame, y, z):", zs)
    except Exception as err:                                    # noqa
        print("   walk with a drop raises:", type(err).__name__, err)
    print("   fall / drop / jump in the API:", [n for n in dir(p) if n in ("fall", "drop", "jump", "hop", "drop_to", "fall_to")])

    print("--- barter results other than a pearl (the shot list: 'mostly gravel')")
    q = piglins.make_piglin("trader")
    q.place(1, (0, 0, 0), 0.0)
    try:
        b1 = piglins.barter(q, None, 10, "gravel", toward=(0, -3, 0), admire_ticks=20)
        print("   gravel:", {k: v for k, v in b1.items() if k not in ("item", "rest")}, "item", b1["item"])
        b2 = piglins.barter(q, None, b1["throw"] + 2, "ender_pearl", toward=(0, -3, 0), admire_ticks=20, count=2)
        b3 = piglins.barter(q, None, b2["throw"] + 2, "gravel", toward=(0.5, -3, 0), admire_ticks=20, seed=2)
        print("   three barters in a row on one piglin:", b1["throw"], b2["throw"], b3["throw"], "| rests",
              [tuple(round(c, 2) for c in b["rest"]) for b in (b1, b2, b3)])
        for f in (b1["throw"] - 1, b1["throw"], b1["throw"] + 1, b2["throw"] - 1, b2["throw"] + 1):
            scene.frame_set(f)
            print("     frame %d: ingot in hand %s, admiring %s, head pitch %.2f, left arm %.2f" %
                  (f, not q.item_object("gold_ingot", "off").hide_render, q.admiring_at(f), q.head.rotation_euler.x, q.arm_l.rotation_euler.x))
    except Exception as err:                                    # noqa
        import traceback
        traceback.print_exc()

    print("--- a 2 x 2 pit two deep: do the results come out?")
    from engine.blocks import World
    w = World()
    for x in range(-6, 7):
        for y in range(-6, 7):
            for z in (-3, -2, -1):
                w.set(x, y, z, "blackstone")
    for x in (0, 1):
        for y in (0, 1):
            for z in (-2, -1):
                w.set(x, y, z, None)
    for name, feet in (("pit_a", (0.5, 0.5, -2.0)), ("pit_b", (1.5, 0.5, -2.0)), ("pit_c", (1.0, 1.5, -2.0))):
        t = piglins.make_piglin(name)
        t.place(1, feet, 0.0)
        for dist in (1.0, 1.5, 2.0, 3.0):
            stand = Vector((1.0, 0.0 - dist, 0.0))                       # the player on the south rim, `dist` from the pit's edge
            try:
                b = piglins.barter(t, None, 10, "ender_pearl", toward=stand, admire_ticks=10, world=w)
                r = b["rest"]
                print("   %s at %s, player %.1f from the edge: result rests at (%.2f, %.2f, %.2f) %s after %d frames" %
                      (name, feet, dist, r.x, r.y, r.z, "OUT" if r.z > -0.5 else "back in the pit", b["landed"] - b["throw"]))
            except Exception as err:                                # noqa
                print("   barter raises:", type(err).__name__, err)
            t.place(1, feet, 0.0)

    print("--- the brute and gold")
    br = piglins.make_piglin("b", "brute")
    br.place(1, (0, 0, 0), 0.0)
    br.look_at(1, (0, -0.6, 0.0), ease=0)
    scene.frame_set(1)
    print("   brute looks at an ingot 0.6 in front of its feet: head pitch %.1f deg (needs %.1f)" %
          (math.degrees(br.head.rotation_euler.x), math.degrees(math.atan2(1.79, 0.6))))
    br.look_at(1, (0, -0.4, 4.9), ease=0)
    scene.frame_set(1)
    print("   brute looks up a 3-block pillar: head pitch %.1f deg" % math.degrees(br.head.rotation_euler.x))
    try:
        br.admire(10)
        print("   brute.admire() is ALLOWED (the game never shows it; barter() refuses)")
    except Exception as err:                                    # noqa
        print("   brute.admire() raises:", err)


def stage(scene, pit=False):
    from engine import look, props
    from engine.blocks import World, new_collection

    look.setup_render(scene, res=(540, 960), samples=16, threads=2, motion_blur=True)
    world = bpy.data.worlds.new("probe_nether")
    world.use_nodes = True
    bg = world.node_tree.nodes["Background"]
    bg.inputs[0].default_value = (0.30, 0.10, 0.06, 1.0)
    bg.inputs[1].default_value = 0.5
    scene.world = world
    look.setup_compositor(scene, bloom=1.0, vignette=0.35, grade="warm", haze=0.0)
    w = World()
    for x in range(-8, 9):
        for y in range(-8, 9):
            for z in (-3, -2, -1):
                w.set(x, y, z, "blackstone" if (x * 3 + y * 7) % 5 else "polished_blackstone_bricks")
    for x in range(-8, 9):
        for z in range(0, 4):
            w.set(x, 8, z, "gold_block" if -2 <= x <= 2 and z < 3 else "polished_blackstone_bricks")
    if pit:
        for x in (0, 1):
            for y in (0, 1):
                for z in (-2, -1):
                    w.set(x, y, z, None)
    w.cull_below = -3
    w.build(new_collection(scene, "set"))
    lamps = new_collection(scene, "lamps")
    for pos, energy in (((-3.0, -3.0, 3.6), 600.0), ((4.0, 2.0, 3.2), 420.0), ((0.5, 5.0, 3.0), 420.0), ((1.0, 1.0, 1.6), 160.0)):
        lamp = props.make_light("lantern", lamps)
        lamp.location = pos
        lamp.data.energy = energy
    return w


def render(scene, name):
    from engine import quick
    path = os.path.join(quick.TEST_DIR, "check_piglins_probe3_%s.png" % name)
    scene.render.filepath = path
    t = time.time()
    bpy.ops.render.render(write_still=True)
    print("wrote %s in %.0f s" % (path, time.time() - t))


def side(scene):
    """Shot 2 of the shot list: side-on close shot at snout height, two piglins admiring."""
    from engine import piglins, shots
    from films.lookdev import Stage

    stage(scene)
    film = shots.Film(scene, fps=24)
    st = Stage(scene, film, None, None)
    a = piglins.add_piglin(st, "a")
    b = piglins.add_piglin(st, "b", armor=("helmet",))
    br = piglins.add_piglin(st, "br", "brute")
    for name, (cam, aim, lens) in (("side", ((-4.5, 7.0, 1.5), (0.6, 6.9, 1.4), 60)),
                                   ("threeq", ((-2.6, 9.6, 1.6), (0.5, 6.8, 1.4), 60))):
        s = st.shot(name, 1.0)
        f0 = s.frame_start
        a.place(f0, (0.0, 6.5, 0.0), math.pi)                 # facing +Y, the gold wall
        b.place(f0, (1.2, 6.1, 0.0), math.pi)
        br.place(f0, (-1.3, 4.6, 0.0), math.radians(60))
        a.admire(f0)
        b.admire(f0)
        a.flop_ears(f0, s.frame_end + 1)
        b.flop_ears(f0, s.frame_end + 1)
        br.idle(f0, s.frame_end + 1, seed=2)
        s.lens(lens, 2.8)
        s.move(cam, aim)
        s.focus(a.item_point(f0 + 1, "off"))
        st.use(s, a, b, br)
        st.hero(s, "a", a)
    st.finish()
    for s in film.shots:
        film.goto(s.frame_start + 8)
        bpy.context.view_layer.update()
        render(scene, s.name)


def pit(scene, offsets):
    """Shot 7: over the player's shoulder into the pit; three piglins admire; a pearl and gravel come out."""
    from engine import piglins, shots
    from films.lookdev import Stage

    w = stage(scene, pit=True)
    film = shots.Film(scene, fps=24)
    st = Stage(scene, film, None, None)
    steve = st.actor("steve", "steve")
    crew = [piglins.add_piglin(st, n) for n in ("pa", "pb", "pc")]
    s = st.shot("pit", 4.0)
    f0 = s.frame_start
    stand = Vector((1.0, -0.9, 0.0))
    steve.place(f0, stand, math.pi)
    steve.look_at(f0, (1.0, 0.8, -1.0), ease=0)
    spots = [(0.5, 0.5, -2.0), (1.5, 0.45, -2.0), (1.0, 1.5, -2.0)]
    beats = []
    for i, (p, feet) in enumerate(zip(crew, spots)):
        p.place(f0, feet, 0.0)
        p.look_at(f0, steve, ease=0)
        b = piglins.barter(p, None, f0 + 4 + 18 * i, "ender_pearl" if i == 0 else "gravel", toward=steve,
                           admire_ticks=20 + 10 * i, world=w, count=2, seed=i)
        st.cast[b["item"].name] = b["item"]
        beats.append(b)
        print("  ", p.name, {k: (tuple(round(c, 2) for c in v) if isinstance(v, Vector) else v) for k, v in b.items() if k != "item"})
    s.lens(24, 4.0)
    s.move(stand + Vector((0.75, -1.5, 2.55)), Vector((1.0, 0.9, -1.0)))
    s.focus(crew[0].head)
    st.use(s, steve, *crew, *[b["item"] for b in beats])
    st.hero(s, "pa", crew[0])
    st.finish()
    for off in offsets:
        film.goto(f0 + off)
        bpy.context.view_layer.update()
        render(scene, "pit_%d" % off)


def low(scene):
    """Shots 21 / 22: the brute over an ingot turning at its feet, low close-up."""
    from engine import mobs, piglins, shots
    from films.lookdev import Stage

    stage(scene)
    film = shots.Film(scene, fps=24)
    st = Stage(scene, film, None, None)
    br = piglins.add_piglin(st, "br", "brute")
    ingot = piglins.add_item(st, "gold_ingot")
    s = st.shot("low", 2.0)
    f0 = s.frame_start
    br.place(f0, (0.0, 6.0, 0.0), 0.0)
    ingot.place(f0, (0.0, 5.3, 0.0))
    ingot.animate(f0, s.frame_end + 1)
    br.look_at(f0, ingot.root, ease=0)
    br.flop_ears(f0, s.frame_end + 1)
    s.lens(50, 2.8)
    s.move((0.9, 3.6, 0.5), (0.0, 5.7, 1.15))
    s.focus(br.head)
    st.use(s, br, ingot)
    st.hero(s, "br", br)
    st.finish()
    film.goto(f0 + 20)
    bpy.context.view_layer.update()
    render(scene, "low")


def main(argv):
    from engine import quick

    for arg in argv:
        scene = quick.reset()
        if arg == "num":
            numbers(scene)
        elif arg == "side":
            side(scene)
        elif arg == "low":
            low(scene)
        elif arg.startswith("pit"):
            pit(scene, [int(o) for o in arg.split(":")[1:]])
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
