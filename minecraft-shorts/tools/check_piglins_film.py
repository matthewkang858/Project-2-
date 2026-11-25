"""Independent check of engine/piglins.py used the way a director would use it (from its docstring): a three-shot
film on a small bastion floor, built on films.lookdev.Stage with the films' render settings (engine.look.setup_render:
motion blur with shutter 0.5, the films' Cycles settings) and depth of field, at 540x960 / 16 samples / 2 threads.

    hole    a piglin trapped in a two-deep hole: Steve throws an ingot in, the piglin admires it and throws
            ender pearls out to him (item physics against the blocks of the set)
    chase   the brute runs at Steve with its axe held high and swings
    death   Steve hits a piglin twice: hurt flash with the knock-back hop, then death and the poof

Run:  $BPY -m tools.check_piglins_film [fp] [<shot>:<offset> ...]        e.g.  hole:30 chase:-6 death:40
      fp = print the scene fingerprints (engine/stamp.py) of a few frames, twice in a row they must be equal
Stills: out/test/check_piglins_<shot>_<offset>.png
(The Nether sky / fog look and a real bastion set are other modules' work: here a dim red world and warm lamps.)
"""
import math
import os
import sys
import time

import bpy
from mathutils import Vector


def build(scene):
    from engine import characters as ch
    from engine import look, piglins, props, shots
    from engine.blocks import World, new_collection
    from films.lookdev import Stage

    look.setup_render(scene, res=(540, 960), samples=16, threads=2, motion_blur=True)
    world = bpy.data.worlds.new("nether_test")
    world.use_nodes = True
    bg = world.node_tree.nodes["Background"]
    bg.inputs[0].default_value = (0.30, 0.09, 0.05, 1.0)
    bg.inputs[1].default_value = 0.4
    scene.world = world

    w = World()
    kinds = ["polished_blackstone_bricks"] * 5 + ["cracked_polished_blackstone_bricks", "blackstone", "gilded_blackstone"]
    for x in range(-9, 10):
        for y in range(-9, 10):
            for z in (-3, -2, -1):
                w.set(x, y, z, kinds[(x * 7 + y * 13 + x * y) % len(kinds)] if z == -1 else "blackstone")
    for z in (-2, -1):
        w.set(0, 0, z, None)                                             # the hole: 1 x 1, two deep
    for x in range(-9, 10):
        for z in range(0, 5):
            w.set(x, 9, z, "polished_blackstone_bricks" if (x + z) % 4 else "gilded_blackstone")
    w.set(-3, 6, 0, "gold_block")
    w.set(-3, 7, 0, "gold_block")
    w.set(-3, 7, 1, "gold_block")
    for z in range(0, 4):
        w.set(4, 7, z, "basalt", {"axis": "y"})
    w.cull_below = -3
    w.build(new_collection(scene, "set"))
    lamps = new_collection(scene, "lamps")
    for pos, energy in (((-3.0, -3.0, 3.6), 620.0), ((4.0, 2.0, 3.0), 320.0), ((0.5, 0.5, 2.6), 180.0), ((0.5, 0.5, -0.4), 14.0),
                        ((-2.0, 6.0, 3.0), 300.0)):
        lamp = props.make_light("lantern", lamps)
        lamp.location = pos
        lamp.data.energy = energy

    film = shots.Film(scene, fps=24)
    st = Stage(scene, film, None, None)
    info = {}
    steve = st.actor("steve", "steve")
    trapped = piglins.add_piglin(st, "trapped", armor=("helmet",))
    brute = piglins.add_piglin(st, "brute", "brute")
    victim = piglins.add_piglin(st, "victim", weapon="crossbow")
    kid = piglins.add_piglin(st, "kid", baby=True)
    ingot = piglins.add_item(st, "gold_ingot")
    pearl = piglins.add_item(st, "ender_pearl", count=3)
    centre = Vector((0.5, 0.5, 0.0))

    # ---- 1. hole
    s = st.shot("hole", 6.0)
    f0 = s.frame_start
    stand = centre + Vector((0.2, -1.4, 0.0))                            # within 1.6 of the hole: the pearls come out
    steve.place(f0, stand, math.pi)
    steve.look_at(f0, centre + Vector((0.0, 0.0, -0.6)), ease=0)
    trapped.place(f0, centre + Vector((0.0, 0.0, -2.0)), 0.0)
    trapped.look_at(f0, steve, ease=0)
    trapped.flop_ears(f0, f0 + 60)
    brute.place(f0, centre + Vector((1.9, 0.5, 0.0)), 0.0)
    brute.face(f0, centre, ease=0)
    brute.look_at(f0, steve, ease=0)
    brute.idle(f0, s.frame_end + 1, seed=2)
    kid.place(f0, centre + Vector((4.5, -3.6, 0.0)), 0.0)
    kid.walk(f0 + 10, [centre + Vector((4.5, -3.6, 0.0)), centre + Vector((2.3, -2.4, 0.0)), centre + Vector((-2.4, -3.4, 0.0))])
    cam = centre + Vector((-2.2, 4.4, 4.4))
    throw = f0 + 8
    steve.swing_arm(throw)
    landed = piglins.throw_item(ingot, throw, steve, centre + Vector((0.0, 0.0, -0.5)), world=w, seed=1)
    ingot.animate(throw, landed + 60)
    take = max(landed + 2, throw + int(piglins.PLAYER_DROP_DELAY_TICKS * piglins.TICK))
    assert piglins.in_reach(trapped, ingot, take), "the ingot must lie in the hole"
    beats = piglins.barter(trapped, ingot, take, pearl, toward=steve, admire_ticks=30, world=w, face=cam)
    assert beats["rest"].z > -0.5, "the pearls must land on the rim, not back in the hole"
    s.lens(27, 3.2)
    s.move(cam, centre + Vector((0.2, -0.5, 0.6)))
    s.focus(trapped.head)
    st.use(s, steve, trapped, brute, kid, ingot, pearl)
    st.hero(s, "trapped", trapped)
    info["hole"] = dict(throw=throw, landed=landed, ingot=tuple(round(c, 2) for c in ingot.rest_pos),
                        beats={k: v for k, v in beats.items() if k not in ("item", "rest")},
                        pearl=tuple(round(c, 2) for c in beats["rest"]))

    # ---- 2. chase: the brute runs 7 blocks at Steve, axe high, and swings when it is 1.3 away
    s = st.shot("chase", 2.5)
    f0 = s.frame_start
    sp = Vector((6.0, -4.0, 0.0))
    steve.place(f0, sp, math.radians(-90))                              # facing -X, toward the brute
    brute.place(f0, sp + Vector((-8.3, 0.0, 0.0)), math.radians(90))
    brute.aggro(f0)
    end = brute.walk(f0, [sp + Vector((-8.3, 0.0, 0.0)), sp + Vector((-1.3, 0.0, 0.0))], run=True, ramp=(0, 3))
    brute.look_at(f0, steve, ease=0)
    hit = brute.attack(end)
    steve.flinch(end)
    s.lens(24, 2.8)
    s.move(sp + Vector((-6.5, -5.6, 1.2)), brute.head, sp + Vector((-0.4, -4.6, 1.2)), brute.head)
    s.focus(brute.head)
    st.use(s, steve, brute)
    st.hero(s, "brute", brute)
    info["chase"] = dict(walk={k: brute.last_walk[k] for k in ("frames", "speed", "swing", "steps", "step_frames", "slides")},
                         swing=(end, hit))

    # ---- 3. death: two hits
    s = st.shot("death", 4.0)
    f0 = s.frame_start
    vp = Vector((-4.0, 2.0, 0.0))
    victim.place(f0, vp, math.radians(-90))
    steve.place(f0, vp + Vector((-1.4, 0.0, 0.0)), math.radians(90))
    victim.aim_crossbow(f0)
    steve.swing_arm(f0 + 6)
    back = victim.hurt(f0 + 8, source=steve)
    victim.aim_crossbow(f0 + 8, on=False)
    steve.walk(f0 + 16, [vp + Vector((-1.4, 0.0, 0.0)), vp + Vector((0.55, 0.0, 0.0))], speed=2.6)
    steve.swing_arm(back + 4)
    gone = victim.die(back + 6, source=steve, camera=s, seed=5)
    s.lens(20, 3.2)
    s.move(vp + Vector((1.5, -8.5, 1.6)), vp + Vector((1.5, 0.0, 1.0)))
    s.focus(victim.head)
    st.use(s, steve, victim)
    st.hero(s, "victim", victim)
    info["death"] = dict(hurt=f0 + 8, still=back, dies=back + 6, gone=gone, poof=victim.last_death["burst"])

    st.finish()
    return film, st, dict(steve=steve, trapped=trapped, brute=brute, victim=victim, kid=kid, ingot=ingot, pearl=pearl,
                          info=info, world=w)


def main(argv):
    from engine import quick, stamp

    scene = quick.reset()
    t0 = time.time()
    film, st, cast = build(scene)
    print("built in %.1f s; shots:" % (time.time() - t0), [(s.name, s.frame_start, s.frame_end) for s in film.shots])
    for name, data in cast["info"].items():
        print(" ", name, data)
    if "fp" in argv:
        fp = stamp.Fingerprinter(scene, film)
        info = cast["info"]
        for f in (1, info["hole"]["beats"]["pickup"] + 1, info["hole"]["beats"]["throw"] + 3, info["chase"]["swing"][0] + 3,
                  info["death"]["hurt"] + 2, info["death"]["gone"] + 3):
            r = fp.frame(f)
            print("FP", f, r["fp"], r["parts"])
    for arg in argv:
        if ":" not in arg:
            continue
        name, off = arg.split(":")
        shot = next(s for s in film.shots if s.name == name)
        frame = shot.frame_start + int(off) if int(off) >= 0 else shot.frame_end + 1 + int(off)
        film.goto(frame)
        bpy.context.view_layer.update()
        v = cast["victim"]
        print("%s frame %d: trapped admiring %s | brute at %s arm %.2f | victim hurt %s gone %s roll %.0f" %
              (arg, frame, cast["trapped"].admiring_at(frame), tuple(round(c, 2) for c in cast["brute"].root.matrix_world.translation),
               cast["brute"].arm_r.rotation_euler.x, v.hurt_at(frame), v.gone_at(frame), math.degrees(v.root.rotation_euler.y)))
        path = os.path.join(quick.TEST_DIR, "check_piglins_%s_%s.png" % (name, off.replace("-", "m")))
        scene.render.filepath = path
        t1 = time.time()
        bpy.ops.render.render(write_still=True)
        print("wrote %s in %.0f s" % (path, time.time() - t1))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
