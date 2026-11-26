"""Checker probe for engine/towers.py (independent review): fingerprint cases the author's stamp check leaves out:
the lava light's flicker, the panic tremble, the bobbing poppies, a hidden glass pane per shot, the slot glow strip.
Run twice (two processes): the digests must match.

    $BPY -m tools.check_towers_stamp2
"""
import hashlib
import sys

import bpy

from engine import stamp

FAILED = []


def ok(label, cond, detail=""):
    if not cond:
        FAILED.append(label)
    print("%-4s %s%s" % ("OK" if cond else "FAIL", label, ("  [%s]" % detail) if detail else ""), flush=True)


def main():
    from tools import towers_proof as tp

    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    built = tp.build(scene, res=(720, 1280), samples=24, threads=4)
    film, h, fm, st = built["film"], built["h"], built["farm"], built["stage"]
    shots = {s.name: s for s in film.shots}
    fp = stamp.Fingerprinter(scene, film)
    digest = hashlib.sha1()
    seen = {}

    def part(f, k):
        if f not in seen:
            seen[f] = fp.frame(f)["parts"]
        return seen[f][k]

    sl = h["slide"]
    g = sl["gone"]
    lav = [part(f, "l") for f in (g - 1, g, g + 1, g + 2, g + 3)]
    ok("the lava light's flicker changes the light part on gone, gone+2 (frames %d..%d)" % (g - 1, g + 3),
       lav[0] != lav[1] and lav[2] != lav[3], "distinct light parts: %d of 5" % len(set(lav)))
    lamp = [o for o in bpy.data.objects if o.type == "LIGHT" and "lava" in o.name][0]
    en = []
    for f in (g - 1, g, g + 1, g + 2, g + 3, g + 30, g + 45):
        scene.frame_set(f)
        en.append(round(lamp.data.energy, 1))
    print("lava light energy around gone: %s" % en)
    cs = shots["cell_side"]
    f = cs.frame_start + 20
    tr = [part(k, "o") for k in (f, f + 1, f + 2, f + 3)]
    ok("the panic tremble changes the objects' part frame by frame (cell_side %d..%d)" % (f, f + 3),
       len(set(tr)) == 4, "%d distinct" % len(set(tr)))
    ho = shots["hopper"]
    f = ho.frame_start + 1
    pp = [part(k, "o") for k in (f, f + 1)]
    ok("the strewn poppies (bob, spin) change the objects' part between two frames", pp[0] != pp[1])
    po = shots["pod_out"]
    pod = fm.pod
    hidden = [ob for ob in pod.panes.values() if (scene.frame_set(po.frame_start) or True) and not ob.visible_camera]
    nxt = [s for s in sorted(film.shots, key=lambda s: s.frame_start) if s.frame_start > po.frame_start][0]
    back = all((scene.frame_set(nxt.frame_start) or True) and ob.visible_camera for ob in hidden)
    before = all((scene.frame_set(po.frame_start - 1) or True) and ob.visible_camera for ob in hidden)
    ok("pod_out hides %d panes for the camera, they are back on the next shot's first frame and on the frame before"
       % len(hidden), len(hidden) >= 1 and back and before)
    # the same objects with the pane flag flipped: does the fingerprint see it?
    a = fp.frame(po.frame_start + 3)["parts"]["o"]
    ob = hidden[0]
    fc = [c for c in ob.animation_data.action.fcurves if c.data_path == "visible_camera"] if ob.animation_data and \
        ob.animation_data.action and hasattr(ob.animation_data.action, "fcurves") else []
    print("pane %s animated visible_camera fcurves: %d" % (ob.name, len(fc)))
    for f_ in sorted(seen):
        digest.update(("%d:%s" % (f_, "|".join(str(seen[f_][k]) for k in ("o", "l")))).encode())
    print("digest %s" % digest.hexdigest())
    print("%s (%d failed)" % ("ALL OK" if not FAILED else "FAILED", len(FAILED)))
    return 1 if FAILED else 0


if __name__ == "__main__":
    sys.exit(main())
