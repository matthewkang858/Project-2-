"""Checker: close-ups of the undead rigs (UV / layer check), the untested sit() / hold() / flee(), a baby infection.
Run:  $BPY -m tools.check_undead_close close|sit|baby"""
import math
import sys

import bpy


def stage(blur=False):
    from engine import mobs, quick
    scene = quick.reset()
    quick.setup(scene, res=(540, 960))
    sun = quick.light(scene, "day")
    sun.data.energy = 3.0
    if blur:
        scene.render.use_motion_blur = True
        scene.render.motion_blur_shutter = 0.5
        scene.render.motion_blur_position = "START"
    mobs._set(scene, wall=((-5, 2, 5, 2), ("stone_bricks", "oak_planks", "stone_bricks", "oak_planks")))
    return scene


def main(which):
    from engine import characters as ch
    from engine import props, quick
    from engine import undead as U

    if which == "close":
        scene = stage()
        row = [U.make_zombie("b", baby=True), U.make_zombie_villager("bv", baby=True), U.make_zombie("bb", baby=True),
               U.make_zombie_villager("bvb", baby=True)]
        yaws = [20, -25, 160, 200]
        for i, c in enumerate(row):
            c.place(1, ((i - 1.5) * 0.9, 0.0, 0.0), math.radians(yaws[i]))
        up = [U.make_zombie_villager("f", "farmer"), U.make_zombie_villager("fb", "farmer"), U.make_zombie("z")]
        for i, (c, yaw) in enumerate(zip(up, (25, 205, 180))):
            c.place(1, ((i - 1) * 1.25, 0.6, 1.0), math.radians(yaw))
        ch._test_box("step", (-2.5, 0.2, 0.0), (2.5, 2.0, 1.0), ch._test_material("step", "block/stone_bricks"))
        scene.objects["quick_sun"].rotation_euler[2] = math.radians(-20)
        quick.camera(scene, (0.2, -6.2, 1.9), (0.0, 0.3, 1.45), lens=30)
        scene.frame_set(1)
        print("wrote", quick.render(scene, "check_undead_close"))
    elif which == "sit":
        scene = stage()
        z = U.make_zombie("z")
        z.place(1, (-1.0, 0.0, -0.45), math.radians(-30))
        z.sit(1, True)
        ch._test_box("boat", (-1.6, -0.6, 0.0), (-0.4, 0.6, 0.25), ch._test_material("boat", "block/oak_planks"))
        h = U.make_zombie("h")
        shovel = props.make_item("iron_shovel")
        h.hold(shovel)
        h.place(1, (0.6, 0.0, 0.0), math.radians(35))
        hb = U.make_zombie("hb", baby=True)
        sw = props.make_item("iron_sword")
        hb.hold(sw)
        hb.place(1, (1.7, -0.4, 0.0), math.radians(35))
        scene.objects["quick_sun"].rotation_euler[2] = math.radians(-20)
        quick.camera(scene, (0.4, -6.5, 1.5), (0.2, 0.0, 0.95), lens=30)
        scene.frame_set(1)
        print("wrote", quick.render(scene, "check_undead_sit_hold"))
        for leg in (z.leg_r, z.leg_l):
            print(leg.name, [round(math.degrees(a), 1) for a in leg.rotation_euler])
    elif which == "baby":
        scene = stage(blur=True)
        z = U.make_zombie("z")
        kid = ch.make_villager("kid", "none", child=True)
        kz = U.make_zombie_villager("kid_z", baby=True)
        z.place(1, (-1.0, 0.0, 0.0), math.radians(90))
        kid.place(1, (0.2, 0.0, 0.0), math.radians(-90))
        z.aggro(1, True, ease=0)
        z.look_at(1, kid, ease=0)
        z.attack(10, target=kid, max_back=0.3)
        z.attack(34)
        end = U.infect(kid, kz, 34, attacker=z, max_back=0.3)
        fl = ch.make_villager("runner", "farmer")
        fl.place(1, (1.2, 0.9, 0.0), math.radians(-90))
        fe = U.flee(fl, 12, z, distance=3.0)
        print("flee ends", fe, "at", tuple(round(q, 2) for q in fl.pos_at(fe)), "infect end", end,
              "kid at 34", tuple(round(q, 2) for q in kid.pos_at(33)), "kz at", tuple(round(q, 2) for q in kz.pos_at(34)))
        quick.camera(scene, (0.3, -7.0, 1.3), (0.3, 0.0, 0.9), lens=32)
        for f in (9, 13, 33, 37, 60):
            scene.frame_set(f)
            print("wrote", quick.render(scene, "check_undead_baby_%d" % f))


if __name__ == "__main__":
    main(sys.argv[1])
