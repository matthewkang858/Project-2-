"""Reviewer's probe: the docstring's beat-15 recipe exactly as written (place first, then sk.shoot(f0 - 24, cr)),
and in the other order. Prints the skeleton's arm aim and bow model over the first frames of the shot.
    $BPY -m tools.check_hostiles_recipe"""
import math
import bpy
from engine import hostiles, players


def run(order):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
    bpy.context.scene.collection.objects.link(cam)
    cr = hostiles.make_creeper("cr")
    sk = hostiles.make_skeleton("sk")
    st = players.make_player("st", "steve")
    f0 = 101                                            # first frame of the beat-15 shot
    if order == "place first":
        cr.place(f0, (4.4, 40.2, 0.0), -math.pi / 2)
        sk.place(f0, (8.5, 40.0, 0.0), -math.pi / 2)
        st.place(f0, (2.2, 40.0, 0.0), 0.0)
        end = cr.fuse(f0)
        a = sk.shoot(f0 - 24, cr)
    else:
        sk.place(1, (8.5, 40.0, 0.0), -math.pi / 2)     # placed in an earlier shot
        cr.place(f0, (4.4, 40.2, 0.0), -math.pi / 2)
        st.place(f0, (2.2, 40.0, 0.0), 0.0)
        end = cr.fuse(f0)
        a = sk.shoot(f0 - 24, cr)
        sk.place(f0, (8.5, 40.0, 0.0), -math.pi / 2, keep_pose=True)
    k = sk.shoot(a.frames[0] + 1, cr, kill=True, camera=cam)
    sk.lower(int(k) + 12)
    print(order, "| arrow 1 loosed %d impact %d, arrow 2 loosed %d impact %d" % (a.frames + k.frames))
    for f in range(f0 - 2, f0 + 6):
        bpy.context.scene.frame_set(f)
        rx = sk.arm_r.matrix_world.to_euler()
        print("   frame %d: aiming %.2f, bow %-14s right arm pitch(rig x) %.2f" % (
            f, sk.aiming_at(f), sk.bow_at(f), sk.arm_r.rotation_euler.x))


run("place first")
run("shoot first, place keep_pose")
