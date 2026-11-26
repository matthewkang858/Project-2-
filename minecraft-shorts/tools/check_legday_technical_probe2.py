"""Independent checker probe 2 for "Leg Day": animated materials (stamp cache), meshes using them, render settings,
camera clip, motion blur, and the twelfth anvil / piston / plank details.

    $BPY -m tools.check_legday_technical_probe2 [--sky gold|dusk]
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


def main(argv):
    sky = argv[argv.index("--sky") + 1] if "--sky" in argv else "gold"
    import render
    ses = render.Session("legday", sky=sky)
    import bpy
    from engine import shots as sh
    scene, st, C = ses.scene, ses.result["stage"], ses.result["context"]
    print("[probe2] res %dx%d %d%% samples %d motion_blur %s seed %s anim_seed %s" % (
        scene.render.resolution_x, scene.render.resolution_y, scene.render.resolution_percentage,
        scene.cycles.samples, scene.render.use_motion_blur, scene.cycles.seed, scene.cycles.use_animated_seed))
    dyn_mats = []
    for m in bpy.data.materials:
        if sh.fcurves_of(m) or (m.node_tree is not None and sh.fcurves_of(m.node_tree)):
            dyn_mats.append(m)
    dyn_nt = [nt for nt in bpy.data.node_groups if sh.fcurves_of(nt)]
    print("[probe2] animated materials: %d %s" % (len(dyn_mats), [m.name for m in dyn_mats][:20]))
    print("[probe2] animated node groups: %d %s" % (len(dyn_nt), [n.name for n in dyn_nt][:10]))
    users = {}
    for ob in bpy.data.objects:
        if ob.type != "MESH":
            continue
        for slot in ob.material_slots:
            if slot.material in dyn_mats:
                users.setdefault(slot.material.name, []).append(ob.name)
    marked = 0
    for mname, obs in users.items():
        for on in obs:
            ob = bpy.data.objects[on]
            if "stamp_every_frame" in ob.data:
                marked += 1
        print("   %-40s used by %d meshes e.g. %s (stamp_every_frame on %d)" % (
            mname, len(obs), obs[:3], sum(1 for on in obs if "stamp_every_frame" in bpy.data.objects[on].data)))
    # which shots see the users (visible at the shot's mid frame)
    for s in sorted(ses.film.shots, key=lambda s: s.frame_start):
        scene.frame_set((s.frame_start + s.frame_end) // 2)
        vis = [on for obs in users.values() for on in obs if not bpy.data.objects[on].hide_render]
        if vis:
            print("   visible in %-15s %d e.g. %s" % (s.name, len(vis), vis[:3]))
    cam = scene.camera
    print("[probe2] camera %s clip %.3f..%.1f" % (cam.name, cam.data.clip_start, cam.data.clip_end))
    # the held anvils and torches: visible in their shots
    for name in ("steve_cl", "kai_cl", "zuri_cl", "ari_cl", "steve_cl3", "efe_sq", "efe_tp4", "efe_rd", "efe_pn",
                 "steve_tp", "steve_tp2", "zuri_pn", "kai_pn"):
        c = st.cast.get(name)
        if c is None:
            print("   no", name)
            continue
        shots_in = [s for s in ses.film.shots if name in st.in_shot.get(s.name, ())]
        for s in shots_in:
            f = s.frame_start + 2
            scene.frame_set(f)
            held = [o for o in c.objects() if o not in (c.root,) and ("held" in o.name or "item" in o.name or
                                                                      "anvil" in o.name or "torch" in o.name or
                                                                      "bucket" in o.name or "chicken" in o.name)]
            print("   %-10s %-15s f%d held: %s" % (name, s.name, f, [(o.name, not o.hide_render) for o in held][:4]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
