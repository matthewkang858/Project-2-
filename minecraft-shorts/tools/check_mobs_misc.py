"""Independent checker: the parts of engine/mobs.py its author only checked by numbers (attack, hold, block items,
bigger stacks, a short walk, a cut straight into the offer), on the quick test stage with motion blur.
Run:  $BPY -m tools.check_mobs_misc"""
import math
import sys


def main():
    import bpy
    from engine import characters as ch
    from engine import mobs, quick

    scene = quick.reset()
    quick.setup(scene)
    sun = quick.light(scene, "day")
    sun.data.energy = 2.6
    mobs._set(scene, path=(-3, 3))
    scene.render.use_motion_blur = True
    scene.render.motion_blur_shutter = 0.5
    scene.render.motion_blur_position = "START"
    z = -0.0625

    # A: attack, three moments (tick 8, tick 5 = arms highest, tick 2)
    g = mobs.make_iron_golem("a")
    g.place(1, (-1.2, 0, z), math.radians(-35))
    end = g.attack(10)
    # B: a golem holding something else (an iron ingot item) through hold(), arm raised by offer_flower's pose
    h = mobs.make_iron_golem("b")
    h.place(1, (1.6, 0.8, z), math.radians(30))
    ingot = mobs.mc.item_object("iron_ingot")
    ch._collection(None).objects.link(ingot) if not ingot.users_collection else None
    h.hold(ingot)
    h.raise_arm(1, angle=46, ease=0)
    # C: block item, stacks of 20 poppies (3 copies) and 64 ingots (5 copies)
    blk = mobs.make_dropped_item("iron_block")
    blk.place(1, (-0.3, -2.2, z))
    blk.animate(1, 60)
    pop = mobs.make_dropped_item("poppy", count=20, seed=4)
    pop.place(1, (0.5, -2.4, z))
    pop.face(12, (0.4, -7.5, 1.0))
    pop.animate(1, 60)
    ing = mobs.make_dropped_item("iron_ingot", count=64, seed=6)
    ing.place(1, (1.3, -2.2, z))
    ing.face(12, (2.4, -6.5, 1.0))
    ing.animate(1, 60)
    print("attack ends", end, "| copies: poppy", len(pop.copies), "ingot", len(ing.copies), "block", len(blk.copies),
          "| block hover %.4f depth %.3f" % (blk.hover, blk.depth))
    quick.camera(scene, (0.4, -7.5, 1.5), (0.2, -0.6, 1.25), lens=32)
    for f in (10 + 2, 10 + 6, 10 + 10):
        scene.frame_set(f)
        print("frame", f, "arm_r %.3f arm_l %.3f" % (g.arm_r.rotation_euler.x, g.arm_l.rotation_euler.x))
        print("wrote", quick.render(scene, "check_mobs_misc_%d" % f))
    return 0


if __name__ == "__main__":
    sys.exit(main())
