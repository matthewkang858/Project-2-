"""Checker: frame fingerprints (engine/stamp.py) of the probe film tools/check_underground_probe.py against what
actually changes in the scene, frame by frame (transforms and visibility of every renderable object, light energy
and colour, the camera's lens and focus). A frame whose scene changed but whose fingerprint did not is a MISS (a
stale frame would be kept); the reverse is only a needless re-render.

    $BPY -m tools.check_underground_stampprobe [SKY]          (default: under)
    $BPY -m tools.check_underground_stampprobe under --child  (prints the digest only)
"""
import hashlib
import subprocess
import sys

import bpy


def state(scene):
    dg = bpy.context.evaluated_depsgraph_get()
    out = []
    for ob in scene.objects:
        if ob.hide_render:
            continue
        if ob.type not in ("MESH", "LIGHT", "CAMERA", "CURVE"):
            continue
        ev = ob.evaluated_get(dg)
        m = tuple(round(v, 5) for row in ev.matrix_world for v in row)
        extra = ()
        if ob.type == "LIGHT":
            extra = (round(ob.data.energy, 4), tuple(round(c, 4) for c in ob.data.color))
        if ob.type == "CAMERA":
            extra = (round(ob.data.lens, 3), round(ob.data.dof.focus_distance, 4), ob.data.dof.aperture_fstop)
        out.append((ob.name, ob.visible_camera, m, extra))
    return tuple(sorted(out, key=lambda t: t[0]))


def main(argv):
    sys.modules.setdefault("films._check_underground_probe", __import__("tools.check_underground_probe",
                                                                         fromlist=["x"]))
    import render as R
    from engine import stamp

    sky = argv[0] if argv and not argv[0].startswith("-") else "under"
    ses = R.Session("_check_underground_probe", sky=sky)
    film = ses.film
    scene = ses.scene
    fp = stamp.Fingerprinter(scene, film)
    names = [s.name for s in film.shots if ses.stage.sky_at(s.frame_start) == sky] if hasattr(ses, "stage") else []
    if not names:
        st = ses.result["stage"]
        names = [s.name for s in film.shots if st.sky_at(s.frame_start) == sky]
    frames = [f for s in film.shots if s.name in names for f in range(s.frame_start, s.frame_end + 1)]
    prints = {}
    for f in frames:
        p = fp.frame(f)["parts"]
        prints[f] = p["o"] + p["l"] + p["c"]
    h = hashlib.sha1()
    for f in frames:
        h.update(prints[f].encode())
    dig = h.hexdigest()[:16]
    if "--child" in argv:
        print("DIGEST", dig, flush=True)
        return 0
    misses, extras = {}, {}
    for s in film.shots:
        if s.name not in names:
            continue
        prev_state = None
        for f in range(s.frame_start, s.frame_end + 1):
            scene.frame_set(f)
            stt = state(scene)
            if prev_state is not None:
                sc = stt != prev_state
                fc = prints[f] != prints[f - 1]
                if sc and not fc:
                    diff = [a[0] for a, b in zip(stt, prev_state) if a != b][:4] if len(stt) == len(prev_state) else \
                        ["(object set changed)"]
                    misses.setdefault(s.name, []).append((f, diff))
                if fc and not sc:
                    extras.setdefault(s.name, []).append(f)
            prev_state = stt
    for n in names:
        s = next(x for x in film.shots if x.name == n)
        ch = [f for f in range(s.frame_start + 1, s.frame_end + 1) if prints[f] != prints[f - 1]]
        print("[stamp] %-4s frames %d-%d: fingerprint changes on %d frames %s" % (
            n, s.frame_start, s.frame_end, len(ch), (ch[:12] + ["..."] if len(ch) > 12 else ch)))
        if misses.get(n):
            print("        MISSED (scene changed, fingerprint did not): %s" % misses[n][:8])
        if extras.get(n):
            print("        needless (fingerprint changed, no transform / visibility / light change): %s"
                  % extras[n][:12])
    out = subprocess.run([sys.executable, "-m", "tools.check_underground_stampprobe", sky, "--child"],
                         capture_output=True, text=True, timeout=250)
    line = [ln for ln in out.stdout.splitlines() if ln.startswith("DIGEST")]
    print("[stamp] digest here %s, child process %s" % (dig, line[0].split()[1] if line else out.stderr[-300:]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
