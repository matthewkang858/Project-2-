"""Independent checker: a small film made with engine/mobs.py the way a director would (docstring only), in the
real village through the real look (night, motion blur, depth of field), 540x960 / 16 samples / 2 threads.

Run:  $BPY -m tools.check_mobs_film <shot>:<offset> [<shot>:<offset> ...]      e.g. patrol:0 patrol:36
Stills: out/test/check_mobs_<shot>_<offset>.png
"""
import math
import os
import sys
import time

import bpy
from mathutils import Vector


def build(scene):
    from engine import characters as ch
    from engine import look, mobs, shots, village
    from films.lookdev import Stage

    look.setup_render(scene, res=(540, 960), samples=16, threads=2, motion_blur=True)
    v = village.build_village(scene, seed=1)
    sky = look.set_time(scene, "night", sun_azimuth=176.0, sun_elevation=21.0)
    look.setup_compositor(scene, bloom=1.3, grade="cool")
    film = shots.Film(scene, fps=24)
    st = Stage(scene, film, v, sky)
    z = -0.0625

    golem = mobs.make_iron_golem("golem")
    st.cast["golem"] = golem
    kid = st.actor("kid", "none", child=True)
    poppy = mobs.make_dropped_item("poppy")
    st.cast[poppy.name] = poppy
    ingot = mobs.make_dropped_item("iron_ingot", count=4, seed=3)
    st.cast[ingot.name] = ingot
    info = {}

    # ---- 1. patrol: down the exit road toward the square, between the gate lamps; low camera beside the road
    s = st.shot("patrol", 3.0)
    f0 = s.frame_start
    road = [(0.5, 27.0, z), (0.5, 12.0, z)]
    print("patrol clearance:", mobs.clearance(v, road, width=mobs.MODEL_WIDTH, height=mobs.MODEL_HEIGHT))
    pre = 24                                                    # the docstring's pre-roll; the film starts at frame 1
    golem.place(f0 - pre, road[0], math.pi)
    end = golem.walk(f0 - pre, road)
    golem.look_at(f0 + 30, (3.0, 19.0, 1.0), ease=10)
    s.lens(30, 2.8)
    s.move((1.7, 19.4, 0.3), (0.45, 24.6, 1.2))               # static, low, on the road: a planted foot must stay put
    s.focus(golem.head)
    st.use(s, golem)
    st.hero(s, "golem", golem)
    st.lights(s, scale=1.3)
    info["patrol"] = dict(walk=golem.last_walk, end=end)

    # ---- 2. offer: on the square in front of the bell lamps; the arm goes up DURING the shot
    s = st.shot("offer", 3.0)
    f0 = s.frame_start
    gp = Vector((0.5, -8.2, z))
    golem.place(f0, gp, math.pi)                               # facing +Y (the bell lamps light its front)
    kp = (gp.x + 0.62, gp.y + 2.15, z)                         # 2.15 in front, 0.62 to ITS right (+X when facing +Y)
    kid.place(f0, kp, 0.0)
    golem.look_at(f0, kid, ease=0)
    kid.look_at(f0, golem, ease=0)
    up = golem.offer_flower(f0 + 12, ease=10)
    kid.look_at(f0 + 16, golem.flower_point(up + 2), ease=8)
    s.lens(40, 2.8)
    s.move((7.4, -7.6, 0.95), (0.9, -7.2, 1.25), (7.0, -7.4, 0.95))
    s.focus(golem.flower)
    st.use(s, golem, kid)
    st.hero(s, "flower", golem.flower)
    st.lights(s, scale=1.2, groups={"bell_e": 2.4, "bell_w": 1.6})
    info["offer"] = dict(up=up)

    # ---- 3. empty: the same spot, nobody
    s = st.shot("empty", 1.0)
    s.lens(40, 2.8)
    s.move((7.4, -7.6, 0.95), (0.9, -7.2, 1.25))
    s.focus((0.9, -7.2, 1.0))
    st.lights(s, scale=1.2, groups={"bell_e": 2.4, "bell_w": 1.6})

    # ---- 4. found: the poppy drops where the golem stood; three villagers around it; then a close-up
    s = st.shot("found", 3.0)
    f0 = s.frame_start
    spot = (gp.x + 0.3, gp.y + 1.2, z)
    cam = Vector((2.4, -9.9, 0.42))
    rest = poppy.drop(f0 + 4, spot, rest=True)
    poppy.face(f0 + 40, cam)
    poppy.animate(f0 + 4, s.frame_end + 1)
    ingot.drop(f0 + 4, (spot[0] - 0.55, spot[1] + 0.25, z), rest=True, seed=5)
    ingot.animate(f0 + 4, s.frame_end + 1)
    folk = []
    for i, (name, prof, off, yaw) in enumerate((("ada", "farmer", (-1.3, 0.9), -2.2), ("bo", "librarian", (0.2, 1.7), 3.1),
                                                 ("cy", "shepherd", (1.5, 0.7), 2.1))):
        c = st.actor(name, prof)
        c.place(f0, (spot[0] + off[0], spot[1] + off[1], z), yaw)
        c.face(f0, spot, ease=0)
        c.look_at(f0 + 14, poppy.sprite, ease=8)
        folk.append(c)
    s.lens(45, 2.8)
    s.move(cam, (spot[0], spot[1], 0.35), cam + Vector((-0.25, 0.1, 0.0)))
    s.focus(poppy.sprite)
    st.use(s, poppy, ingot, *folk)
    st.hero(s, "poppy", poppy.sprite)
    st.lights(s, scale=1.2, groups={"bell_e": 2.4, "bell_w": 1.6})
    info["found"] = dict(rest=rest)

    # ---- 5. close: macro on the fist and the poppy (z-fighting? texture filtering? shading of the cross planes)
    s = st.shot("close", 1.0)
    f0 = s.frame_start
    golem.place(f0, gp, math.pi)
    golem.offer_flower(f0, ease=0)
    golem.look_at(f0, kid, ease=0)
    bloom = golem.flower_point(f0)
    s.lens(70, 2.8)
    s.move((bloom.x + 1.5, bloom.y + 0.9, bloom.z + 0.25), (bloom.x - 0.1, bloom.y - 0.25, bloom.z + 0.1))
    s.focus(golem.flower)
    st.use(s, golem)
    st.hero(s, "flower", golem.flower)
    st.lights(s, scale=1.2, groups={"bell_e": 2.4, "bell_w": 1.6})

    # ---- 6. wide: two golems far down the exit road (a second instance; the game's own gait; a run)
    s = st.shot("wide", 3.0)
    f0 = s.frame_start
    # (the golem of the previous shot must not be pre-rolled into this one: CONTRACT, "no pre-roll" rule -> new instances)
    second = mobs.make_iron_golem("golem2")
    third = mobs.make_iron_golem("golem3", crack="medium")
    st.cast["golem2"] = second
    st.cast["golem3"] = third
    second.place(f0 - 30, (0.2, 30.0, z), 0.0)
    second.walk(f0 - 30, [(0.2, 30.0, z), (0.2, 14.0, z)], gait="vanilla")
    third.place(f0 - 30, (1.2, 44.0, z), 0.0)
    third.walk(f0 - 30, [(1.2, 44.0, z), (1.2, 24.0, z)], run=True)
    s.lens(35, 2.8)
    s.move((0.6, 7.2, 1.3), (0.5, 22.0, 1.6))
    s.focus(second.head)
    st.use(s, second, third)
    st.hero(s, "golem", second)
    st.lights(s, scale=1.3)

    st.finish()
    return film, st, dict(golem=golem, kid=kid, poppy=poppy, ingot=ingot, info=info, v=v)


def main(argv):
    from engine import quick

    scene = quick.reset()
    t0 = time.time()
    film, st, cast = build(scene)
    print("built in %.1f s; shots:" % (time.time() - t0),
          [(s.name, s.frame_start, s.frame_end) for s in film.shots], cast["info"])
    golem, poppy, ingot = cast["golem"], cast["poppy"], cast["ingot"]
    for arg in argv:
        name, off = arg.split(":")
        shot = next(s for s in film.shots if s.name == name)
        frame = shot.frame_start + int(off) if int(off) >= 0 else shot.frame_end + 1 + int(off)
        film.goto(frame)
        bpy.context.view_layer.update()
        print("%s frame %d: golem hidden %s at %s yaw %.0f roll %.1f | arm_r %.3f flower hidden %s | poppy hidden %s root %s | ingot hidden %s"
              % (arg, frame, golem.head.hide_render, tuple(round(c, 2) for c in golem.root.matrix_world.translation),
                 math.degrees(golem.root.rotation_euler.z), math.degrees(golem.root.rotation_euler.y),
                 golem.arm_r.rotation_euler.x, golem.flower.hide_render, poppy.sprite.hide_render,
                 tuple(round(c, 2) for c in poppy.root.matrix_world.translation), ingot.sprite.hide_render))
        path = os.path.join(quick.TEST_DIR, "check_mobs_%s_%s.png" % (name, off.replace("-", "m")))
        scene.render.filepath = path
        t1 = time.time()
        bpy.ops.render.render(write_still=True)
        print("wrote %s in %.0f s" % (path, time.time() - t1))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
