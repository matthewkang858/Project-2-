"""Independent checker's film probe of engine/piglins.py: six shots on a floor of real bastion blocks, through
films.lookdev.Stage, engine.look.setup_render (motion blur, shutter 0.5) and engine.look.setup_compositor, with
depth of field. 540x960, 16 samples, 2 threads.

Run:  $BPY -m tools.check_piglins_probe_film <shot>:<offset> ...     (offset from the shot's first frame)
Stills: out/test/check_piglins_probe_<shot>_<offset>.png
"""
import math
import os
import sys
import time

import bpy
from mathutils import Vector


def build(scene):
    from engine import look, piglins, props, shots
    from engine.blocks import World, new_collection
    from films.lookdev import Stage

    look.setup_render(scene, res=(540, 960), samples=16, threads=2, motion_blur=True)
    world = bpy.data.worlds.new("probe_nether")
    world.use_nodes = True
    bg = world.node_tree.nodes["Background"]
    bg.inputs[0].default_value = (0.30, 0.10, 0.06, 1.0)
    bg.inputs[1].default_value = 0.5
    scene.world = world
    look.setup_compositor(scene, bloom=1.0, vignette=0.35, grade="warm", haze=0.0)

    w = World()
    kinds = ["polished_blackstone_bricks"] * 4 + ["cracked_polished_blackstone_bricks", "blackstone", "gilded_blackstone", "polished_blackstone"]
    for x in range(-12, 13):
        for y in range(-12, 13):
            w.set(x, y, -1, kinds[(x * 5 + y * 11 + x * y) % len(kinds)])
    for x in range(-12, 13):
        for z in range(0, 5):
            w.set(x, 12, z, "polished_blackstone_bricks" if (x + z) % 5 else "gilded_blackstone")
    w.set(-6, 10, 0, "gold_block")
    for z in range(0, 4):
        w.set(6, 10, z, "basalt", {"axis": "y"})
    w.cull_below = -1
    w.build(new_collection(scene, "set"))
    lamps = new_collection(scene, "lamps")
    for pos, energy in (((-4.0, -4.0, 4.0), 700.0), ((5.0, 3.0, 3.5), 420.0), ((0.0, 6.0, 3.5), 380.0), ((-7.0, 5.0, 3.0), 300.0),
                        ((7.0, -5.0, 3.5), 380.0)):
        lamp = props.make_light("lantern", lamps)
        lamp.location = pos
        lamp.data.energy = energy

    film = shots.Film(scene, fps=24)
    st = Stage(scene, film, None, None)
    info = {}
    steve = st.actor("steve", "steve")
    pig = piglins.add_piglin(st, "pig")
    brute = piglins.add_piglin(st, "brute", "brute")
    kid = piglins.add_piglin(st, "kid", baby=True)
    knight = piglins.add_piglin(st, "knight", weapon="crossbow", armor=("helmet", "chestplate", "leggings", "boots"))
    helm = piglins.add_piglin(st, "helm", armor=("helmet",))
    pig2 = piglins.add_piglin(st, "pig2")
    brute2 = piglins.add_piglin(st, "brute2", "brute")
    ingot = piglins.add_item(st, "gold_ingot")
    pearl = piglins.add_item(st, "ender_pearl", count=3)

    # ---- 1. walk: side-on medium shot, feet in frame
    s = st.shot("walk", 3.0)
    f0 = s.frame_start
    pig.place(f0, (-3.0, 0.0, 0.0), 0.0)
    e1 = pig.walk(f0, [(-3.0, 0.0, 0.0), (3.0, 0.0, 0.0)])
    brute.place(f0, (-3.5, 1.2, 0.0), 0.0)
    brute.walk(f0, [(-3.5, 1.2, 0.0), (1.0, 1.2, 0.0)], speed=1.2, swing=0.5)
    kid.place(f0, (-1.5, -0.9, 0.0), 0.0)
    kid.walk(f0 + 6, [(-1.5, -0.9, 0.0), (3.5, -0.9, 0.0)])
    s.lens(40, 2.8)
    s.move((-0.5, -5.2, 0.7), (-0.5, 0.0, 0.95), (0.8, -5.2, 0.7), (0.8, 0.0, 0.95))
    s.focus(pig.head)
    st.use(s, pig, brute, kid)
    st.hero(s, "pig", pig)
    info["walk"] = dict(pig=pig.last_walk["frames"], steps=pig.last_walk["steps"])

    # ---- 2. barter on flat ground, close on the piglin over Steve's shoulder
    s = st.shot("barter", 5.0)
    f0 = s.frame_start
    pp = Vector((0.0, 2.0, 0.0))
    sp = Vector((0.4, -1.6, 0.0))
    pig.place(f0, pp, 0.0)
    steve.place(f0, sp, math.pi)
    pig.look_at(f0, steve, ease=0)
    pig.idle(f0, f0 + 60, seed=4)
    steve.look_at(f0, pig, ease=0)
    throw = f0 + 6
    steve.swing_arm(throw)
    landed = piglins.throw_item(ingot, throw, steve, pp + Vector((0.0, 0.0, 0.6)), world=w, seed=2)
    ingot.animate(throw, landed + 80)
    take = max(landed + 2, throw + 48)
    ok = piglins.in_reach(pig, ingot, take)
    cam = Vector((1.5, -3.4, 1.75))
    beats = piglins.barter(pig, ingot, take, pearl, toward=steve, admire_ticks=30, world=w, face=cam)
    s.lens(45, 2.8)
    s.move(cam, pp + Vector((0.0, 0.0, 1.25)))
    s.focus(pig.head)
    st.use(s, pig, steve, ingot, pearl)
    st.hero(s, "pig", pig)
    info["barter"] = dict(throw=throw, landed=landed, in_reach=ok, ingot=tuple(round(c, 2) for c in ingot.rest_pos),
                          beats={k: (tuple(round(c, 2) for c in v) if isinstance(v, Vector) else v) for k, v in beats.items() if k != "item"})

    # ---- 3. chase: the brute runs at Steve and swings twice; Steve flinches
    s = st.shot("chase", 3.0)
    f0 = s.frame_start
    sp = Vector((4.0, -2.0, 0.0))
    steve.place(f0, sp, math.radians(-90))
    brute.place(f0, sp + Vector((-7.0, 0.0, 0.0)), math.radians(90))
    brute.aggro(f0)
    brute.look_at(f0, steve, ease=0)
    end = brute.walk(f0, [sp + Vector((-7.0, 0.0, 0.0)), sp + Vector((-1.3, 0.0, 0.0))], run=True, ramp=(0, 3))
    hit1 = brute.attack(end)
    steve.flinch(end)
    hit2 = brute.attack(end + 24)
    steve.flinch(end + 24)
    s.lens(32, 2.8)
    s.move(sp + Vector((-3.0, -5.5, 1.0)), sp + Vector((-2.5, 0.0, 1.0)), sp + Vector((-1.0, -4.5, 1.2)), sp + Vector((-0.8, 0.0, 1.1)))
    s.focus(brute.head)
    st.use(s, brute, steve)
    st.hero(s, "brute", brute)
    info["chase"] = dict(run=brute.last_walk["frames"], steps=brute.last_walk["steps"], swing1=(end, hit1), swing2=(end + 24, hit2))

    # ---- 4. death: hurt with the hop, then killed; close
    s = st.shot("death", 5.0)
    f0 = s.frame_start
    vp = Vector((-3.0, 3.0, 0.0))
    pig2.place(f0, vp, math.radians(-90))                      # faces -X, toward Steve
    steve.place(f0, vp + Vector((-1.4, 0.0, 0.0)), math.radians(90))
    pig2.idle(f0, f0 + 8, seed=1)
    steve.swing_arm(f0 + 6)
    back = pig2.hurt(f0 + 8, source=steve)
    steve.walk(f0 + 14, [vp + Vector((-1.4, 0.0, 0.0)), vp + Vector((0.55, 0.0, 0.0))], speed=2.4)
    steve.swing_arm(back + 4)
    gone = pig2.die(back + 6, source=steve, camera=s, seed=5, glow=0.25)
    s.lens(28, 2.8)
    s.move(vp + Vector((1.8, -6.0, 1.3)), vp + Vector((1.8, 0.0, 1.0)))
    s.focus(pig2.head)
    st.use(s, pig2, steve)
    st.hero(s, "pig2", pig2)
    info["death"] = dict(hurt=f0 + 8, still=back, dies=back + 6, gone=gone, poof_end=pig2.last_death["burst"].frame_end)

    # ---- 5. wide: everybody at once
    s = st.shot("wide", 2.0)
    f0 = s.frame_start
    spots = [(-4.0, 2.0), (-2.4, 3.0), (-0.8, 2.2), (0.9, 3.2), (2.5, 2.0), (4.0, 3.0), (1.6, 0.6)]
    crew = [pig, brute, knight, helm, pig2, brute2, kid]
    for q, (x, y) in zip(crew, spots):
        q.place(f0, (x, y, 0.0), 0.0)
    pig.dance(f0, s.frame_end + 1)
    helm.dance(f0, s.frame_end + 1)
    brute.idle(f0, s.frame_end + 1, seed=1)
    brute2.aggro(f0)
    brute2.idle(f0, s.frame_end + 1, seed=2)
    knight.look_at(f0, (0.0, -8.0, 1.6), ease=0)
    knight.aim_crossbow(f0)
    knight.flop_ears(f0, s.frame_end + 1)
    pig2.idle(f0, s.frame_end + 1, seed=7)
    kid.walk(f0, [(1.6, 0.6, 0.0), (-3.0, 0.4, 0.0)], run=False)
    s.lens(24, 4.0)
    s.move((0.0, -7.0, 1.6), (0.0, 2.5, 1.0))
    s.focus(knight.head)
    st.use(s, *crew)
    st.hero(s, "knight", knight)

    # ---- 6. faces: long lens on the helmet and the brute, heads turning
    s = st.shot("faces", 1.5)
    f0 = s.frame_start
    helm.place(f0, (-0.5, 0.0, 0.0), 0.0)
    brute.place(f0, (0.55, 0.3, 0.0), 0.0)
    helm.look_at(f0, (-3.0, -4.0, 1.6), ease=0)
    helm.look_at(f0 + 6, (3.0, -4.0, 1.3), ease=14)
    brute.look_at(f0, (0.0, -5.0, 1.7), ease=0)
    brute.idle(f0, s.frame_end + 1, seed=5)
    helm.flop_ears(f0, s.frame_end + 1)
    s.lens(85, 4.0)
    s.move((0.6, -5.5, 1.75), (0.05, 0.0, 1.62))
    s.focus(helm.head)
    st.use(s, helm, brute)
    st.hero(s, "helm", helm)

    st.finish()
    return film, st, info


def main(argv):
    from engine import quick

    scene = quick.reset()
    t0 = time.time()
    film, st, info = build(scene)
    print("built in %.1f s; shots:" % (time.time() - t0), [(s.name, s.frame_start, s.frame_end) for s in film.shots])
    for name, data in info.items():
        print(" ", name, data)
    for arg in argv:
        name, off = arg.split(":")
        shot = next(s for s in film.shots if s.name == name)
        frame = shot.frame_start + int(off)
        film.goto(frame)
        bpy.context.view_layer.update()
        path = os.path.join(quick.TEST_DIR, "check_piglins_probe_%s_%s.png" % (name, off))
        scene.render.filepath = path
        t1 = time.time()
        bpy.ops.render.render(write_still=True)
        print("wrote %s (frame %d) in %.0f s" % (path, frame, time.time() - t1))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
