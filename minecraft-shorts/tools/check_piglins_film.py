"""Independent check of engine/piglins.py used the way a director would use it (from its docstring): a six-shot
film on a small bastion floor, built on films.lookdev.Stage with the films' render settings (engine.look.setup_render:
motion blur with shutter 0.5, the films' Cycles settings) and depth of field, at 540x960 / 16 samples / 2 threads.

    hole    a piglin trapped in a two-deep hole: Steve throws an ingot in, the piglin admires it and throws
            ender pearls out to him (item physics against the blocks of the set)
    chase   the brute runs at Steve with its axe held high and swings
    death   Steve hits a piglin twice: hurt flash with the knock-back hop, then death and the poof (default glow)
    after   another corner of the set straight after the death: no puff of the death may hang in it
    flash   a one-second flash cut: the brute, a puff that is already in the air on the first frame (started 8
            frames before the cut) and a pair of golden boots spinning at his feet
    pit     two piglins walk off the rim of a 2 x 2 pit and fall in; a third, already in the far half, admires
            and lobs gravel out to Steve's boots (barter(lob=True))

Run:  $BPY -m tools.check_piglins_film [fp] [<shot>:<offset> ...]        e.g.  hole:30 chase:-6 death:40 after:0
      fp = print the scene fingerprints (engine/stamp.py) of a few frames, twice in a row they must be equal
      (at most three stills per call: each takes about a minute)
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
    for x in range(-9, 13):
        for y in range(-15, 10):
            for z in (-3, -2, -1):
                w.set(x, y, z, kinds[(x * 7 + y * 13 + x * y) % len(kinds)] if z == -1 else "blackstone")
    for z in (-2, -1):
        w.set(0, 0, z, None)                                             # the hole: 1 x 1, two deep
        for x in (5, 6):
            for y in (-8, -7):
                w.set(x, y, z, None)                                     # the pit: 2 x 2, two deep (x 5..7, y -8..-6)
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
                        ((-2.0, 6.0, 3.0), 300.0), ((7.5, -5.0, 3.4), 420.0), ((6.0, -7.0, 0.8), 80.0), ((6.0, -7.0, -0.9), 20.0)):
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
    gone = victim.die(back + 6, source=steve, camera=s, seed=5)         # camera = the Shot: the puffs end with it
    s.lens(20, 3.2)
    s.move(vp + Vector((1.5, -8.5, 1.6)), vp + Vector((1.5, 0.0, 1.0)))
    s.focus(victim.head)
    st.use(s, steve, victim)
    st.hero(s, "victim", victim)
    burst = victim.last_death["burst"]
    info["death"] = dict(hurt=f0 + 8, still=back, dies=back + 6, gone=gone, poof=burst)
    death_shot = s

    # ---- 4. after: the same floor seen from the other side, straight after the death (the burst would last on)
    s = st.shot("after", 1.5)
    f0 = s.frame_start
    kid.place(f0, vp + Vector((2.5, 1.0, 0.0)), 0.0)
    kid.walk(f0, [vp + Vector((2.5, 1.0, 0.0)), vp + Vector((0.5, -1.5, 0.0))])
    s.lens(24, 3.2)
    s.move(vp + Vector((1.5, -7.5, 1.6)), vp + Vector((1.5, 0.0, 1.0)))
    s.focus(kid.head)
    st.use(s, kid)
    st.hero(s, "kid", kid)
    assert burst.frame_end == death_shot.frame_end, "the death's puffs must end with its shot"
    info["after"] = dict(burst_ends=burst.frame_end, shot_starts=f0)

    # ---- 5. flash: a flash cut with a puff that is already in the air on its first frame
    s = st.shot("flash", 1.0)
    f0 = s.frame_start
    bp = Vector((-1.0, -4.0, 0.0))
    brute.place(f0, bp, math.radians(20))
    brute.idle(f0, s.frame_end + 1, seed=3)
    boots = piglins.add_item(st, "golden_boots")
    boots.place(f0, bp + Vector((0.9, -0.5, 0.0)))
    boots.animate(f0, s.frame_end + 1)
    puff = piglins.poof(bp + Vector((1.3, -0.2, 0.0)), f0 - 8, camera=s, size=(0.6, 1.8), seed=2)   # a player's box
    s.lens(32, 2.8)
    s.move(bp + Vector((1.6, -5.2, 1.3)), bp + Vector((0.5, 0.0, 1.0)))
    s.focus(brute.head)
    st.use(s, brute, boots)
    st.hero(s, "brute", brute)
    info["flash"] = dict(first=f0, puff=puff)
    flash_shot = s

    # ---- 6. pit: two walk off the rim and fall in, a third lobs gravel out to Steve
    s = st.shot("pit", 4.0)
    f0 = s.frame_start
    pc = Vector((6.0, -7.0, 0.0))                                        # the middle of the pit (x 5..7, y -8..-6)
    stand = pc + Vector((0.0, -2.2, 0.0))                                # 1.2 from its south edge
    steve.place(f0, stand, math.pi)
    steve.look_at(f0, pc + Vector((0.0, 0.0, -1.0)), ease=0)
    victim.place(f0, pc + Vector((0.4, 0.5, -2.0)), 0.0)                 # already in the far half
    victim.look_at(f0, steve, ease=0)
    trapped.place(f0, pc + Vector((-4.0, -0.5, 0.0)), math.radians(90))
    brute.place(f0, pc + Vector((2.6, 3.2, 0.0)), 0.0)
    brute.face(f0, steve, ease=0)
    brute.idle(f0, s.frame_end + 1, seed=4)
    end1 = trapped.walk(f0, [pc + Vector((-4.0, -0.5, 0.0)), pc + Vector((-0.7, -0.5, 0.0))], ramp=(4, 0))   # 0.3 past the rim
    land1 = trapped.fall(end1, -2.0)
    trapped.look_at(land1 + 4, steve, ease=8)
    trapped.flop_ears(trapped.last_fall["still"], s.frame_end + 1)
    cam = pc + Vector((2.6, -5.6, 5.2))
    beside = stand + Vector((0.65, 0.2, 0.0))                            # beside his boots, on the camera's side
    lobbed = piglins.barter(victim, None, f0 + 6, "gravel", toward=beside, admire_ticks=30, world=w, lob=True, face=cam)
    st.cast[lobbed["item"].name] = lobbed["item"]
    assert (lobbed["rest"] - beside).length < 0.06, "the gravel must come to rest where it was sent"
    s.lens(27, 3.2)
    s.move(cam, pc + Vector((-0.2, -0.6, -0.4)))
    s.focus(victim.head)
    st.use(s, steve, victim, trapped, brute, lobbed["item"])
    st.hero(s, "victim", victim)
    info["pit"] = dict(walk_ends=end1, lands=land1, fall=trapped.last_fall,
                       lob={k: v for k, v in lobbed.items() if k not in ("item", "rest")},
                       rest=tuple(round(c, 2) for c in lobbed["rest"]))

    st.finish()
    for f in range(death_shot.frame_end + 1, flash_shot.frame_start):   # nothing of any burst in the shot 'after'
        scene.frame_set(f)
        assert all(ob.hide_render for b in (burst, puff) for ob in b.objects), "a puff hangs in frame %d" % f
    scene.frame_set(flash_shot.frame_start)
    assert sum(1 for ob in puff.objects if not ob.hide_render) == 20, "the flash cut opens with its puffs in the air"
    scene.frame_set(flash_shot.frame_end + 1)
    assert all(ob.hide_render for ob in puff.objects), "the flash cut's puffs end with it"
    scene.frame_set(1)
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
                  info["death"]["hurt"] + 2, info["death"]["gone"] + 3, info["after"]["shot_starts"], info["flash"]["first"],
                  info["pit"]["walk_ends"] + 4, info["pit"]["lob"]["throw"] + 8):
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
