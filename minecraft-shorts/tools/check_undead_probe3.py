"""Checker: third numeric probe of engine/undead.py (trap death default, lockstep, arm yaw during the swing)."""
import math

import bpy
from mathutils import Vector


def main():
    from engine import quick
    scene = quick.reset()
    quick.setup(scene)
    cam = quick.camera(scene, (0.0, -8.0, 1.5), (0.0, 0.0, 1.0))
    from engine import undead as U

    z = U.make_zombie("trap")
    z.place(1, (0.0, 0.0, 0.0), 0.0)
    gone = z.die(20, camera=cam)                     # e.g. lava / fall / crusher: no attacker
    top = max(z.pos_at(20 + k * 0.5).z for k in range(48))
    print("die() without attacker (default): moves %.2f blocks back, hops %.2f up  [game for lava/fall/in_wall/cramming/explosion: no knock-back]"
          % ((z.pos_at(gone - 1) - z.pos_at(19)).length, top))

    a, b = U.make_zombie("horde_a"), U.make_zombie("horde_b")
    a.place(1, (2.0, 0.0, 0.0), 0.0)
    b.place(1, (3.5, 0.0, 0.0), 0.0)
    a.walk(1, [(2.0, 0.0, 0.0), (2.0, -8.0, 0.0)])
    b.walk(1, [(3.5, 0.0, 0.0), (3.5, -8.0, 0.0)])
    same = []
    for f in (5, 12, 20, 33, 47):
        scene.frame_set(f)
        same.append((round(a.leg_l.rotation_euler[0], 3), round(b.leg_l.rotation_euler[0], 3), round(a.hips.location[2], 3), round(b.hips.location[2], 3)))
    print("two zombies that start walking on the same frame: (leg a, leg b, hips a, hips b) =", same)

    s = U.make_zombie("swing")
    s.place(1, (8.0, 0.0, 0.0), 0.0)
    s.attack(50)
    rows = []
    for f in (50.0, 52.4, 53.6, 54.8, 56.0, 58.4):
        scene.frame_set(int(f), subframe=f - int(f))
        bpy.context.view_layer.update()
        m = s.arm_r.matrix_world.to_3x3()
        down = m @ Vector((0.0, 0.0, -1.0))          # the arm's long axis in the world
        yaw_arm = math.degrees(math.atan2(down.x, -down.y))          # 0 = pointing straight ahead (-Y)
        sv = s.swing_value(f)
        f7 = math.sin(sv * math.pi)
        want = math.degrees(-(0.1 - f7 * 0.6))                       # the game's rightArm.yRot, not carried by the body
        body = math.degrees(s.body.rotation_euler[2])
        rows.append((f, round(sv, 2), round(body, 1), round(yaw_arm, 1), round(want, 1)))
    print("attack: (frame, swing value, body twist deg, arm long-axis heading deg, game yRot deg) =")
    for r in rows:
        print("    ", r)


if __name__ == "__main__":
    main()
