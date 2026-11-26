"""The Crammys: the lead's motion probe. One build of one sky, no render: where the cast IS on every frame of a span
(world position, where its eyes / chest / knees land in the frame, and whether the lens sees them), what the hands
hold and what is visible, and the house_e door. For timing a staging against the words before rendering a still.

    $BPY -m tools.crammys_probe track rd07_chased 509-564:3 [--who steve_rd,zombie_rd,kai_rd]
                                      [--cam "x,y,z>tx,ty,tz>lens"] [--sky night]
        per frame: the shot's cast (or --who): world (x, y, z), eyes / chest / knees as x % / y % of the frame and
        'ok' (the lens sees the point) or the first object in the way; the house_e door's angle (0 = shut).
    $BPY -m tools.crammys_probe hands [--sky night] [--who steve_jb,noor_gd] [--frames 1240,1250,1265]
        every held item of every player (or --who): its span, its variants' on/off steps and whether it renders on
        the frames given (hide_render evaluated; the player's own visibility included).
    $BPY -m tools.crammys_probe memo [--sky night]
        the event frames the shot functions left in C.memo (rd07's door, md12's stop, md13's hits, md15's kill ...)
    $BPY -m tools.crammys_probe notes [--sky night] [--span 1201-1562]
        the frames the jukebox's notes are born on (THE SONG and every play) and which shot each lands in.
Nothing is written. Prefix with `nice -n 15 timeout 290`.
"""
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


def _frames(spec):
    """'509-564:3' or '509,530,547' -> [frames]."""
    out = []
    for part in spec.split(","):
        part = part.strip()
        if "-" in part[1:]:
            rng, _, step = part.partition(":")
            a, b = rng.split("-")
            out.extend(range(int(a), int(b) + 1, int(step or 1)))
        elif part:
            out.append(int(part))
    return out


def _hidden(ob, f):
    """hide_render of ob at frame f (its F-curve, or its static value)."""
    ad = ob.animation_data
    if ad is not None and ad.action is not None:
        from engine import shots
        for fc in shots.fcurves_of(ob):
            if fc.data_path == "hide_render":
                return fc.evaluate(f) > 0.5
    return bool(ob.hide_render)


def cmd_track(args, ses):
    import bpy
    from bpy_extras.object_utils import world_to_camera_view
    from mathutils import Vector
    from tools.crammys_geo import first_hit, _own

    scene, st, C = ses.scene, ses.result["stage"], ses.result["context"]
    scene.render.resolution_x, scene.render.resolution_y = 540, 960
    s = {x.name: x for x in ses.film.shots}[args.shot]
    if args.cam:
        bits = args.cam.split(">")
        pos = tuple(float(v) for v in bits[0].split(","))
        tgt = tuple(float(v) for v in bits[1].split(","))
        if len(bits) > 2:
            s.lens(float(bits[2]), s._fstop)
        s.move(pos, tgt)
    names = [n.strip() for n in args.who.split(",")] if args.who else sorted(st.in_shot.get(s.name, ()))
    door = C.v._door_sets.get("house_e", [None])[0] if hasattr(C.v, "_door_sets") else None
    for f in _frames(args.frames):
        scene.frame_set(f)
        cam = s.camera
        scene.camera = cam
        dg = bpy.context.evaluated_depsgraph_get()
        cp = cam.matrix_world.translation.copy()
        line = "f%4d" % f
        if door is not None:
            line += "  door %5.1f" % math.degrees(door.rotation_euler[2] - door["closed_yaw"])
        print(line)
        for n in names:
            c = st.cast.get(n)
            if c is None or not hasattr(c, "pos_at"):
                continue
            p = c.pos_at(f)
            row = "   %-14s (%6.2f, %6.2f, %5.2f)" % (n, p.x, p.y, p.z)
            for label, dz in (("eyes", None), ("chest", 1.2), ("knees", 0.5)):
                if dz is None:
                    if not hasattr(c, "eye_point"):
                        continue
                    q = Vector(c.eye_point(f))
                else:
                    q = Vector((p.x, p.y, p.z + dz))
                co = world_to_camera_view(scene, cam, q)
                vis = first_hit(scene, dg, cp, q, own=_own(c)) or "ok"
                inside = 0.0 <= co.x <= 1.0 and 0.0 <= co.y <= 1.0 and co.z > 0
                row += "  %s %5.1f/%5.1f %s" % (label, co.x * 100, (1 - co.y) * 100,
                                                 vis if inside else "(off frame)")
            print(row)
            for side, held in (getattr(c, "_hands", None) or {}).items():
                for h in held:
                    for vn, att in h.variants.items():
                        if _hidden(att.ob, f):
                            continue
                        box = [world_to_camera_view(scene, cam, att.ob.matrix_world @ Vector(cn))
                               for cn in att.ob.bound_box]
                        xs, ys = [b.x * 100 for b in box], [(1 - b.y) * 100 for b in box]
                        q = att.ob.matrix_world @ (sum((Vector(cn) for cn in att.ob.bound_box), Vector()) / 8.0)
                        print("      holds %-22s x %5.1f..%5.1f y %5.1f..%5.1f  (%4.1f %% wide)  %s" % (
                            h.item_id + (":" + vn if vn else ""), min(xs), max(xs), min(ys), max(ys),
                            max(xs) - min(xs), first_hit(scene, dg, cp, q, own={att.ob.name}) or "ok"))
            book = c.__dict__.get("_hostiles_book") if hasattr(c, "__dict__") else None
            for k, rec in enumerate((book or {}).get("arrows", [])):
                ob = rec["object"]
                if _hidden(ob, f):
                    continue
                pts = [ob.matrix_world @ Vector(cn) for cn in ob.bound_box]
                lo = min(pts, key=lambda q: (q - ob.matrix_world.translation).length)
                hi = max(pts, key=lambda q: (q - ob.matrix_world.translation).length)
                out = []
                for label, q in (("root", ob.matrix_world.translation.copy()), ("far", hi)):
                    co = world_to_camera_view(scene, cam, q)
                    out.append("%s %5.1f/%5.1f %s" % (label, co.x * 100, (1 - co.y) * 100,
                                                      first_hit(scene, dg, cp, q, own={ob.name}) or "ok"))
                print("      arrow %d (%s)  %s" % (k, rec.get("part"), "  ".join(out)))
    return 0


def cmd_hands(args, ses):
    st = ses.result["stage"]
    frames = _frames(args.frames) if args.frames else []
    names = [n.strip() for n in args.who.split(",")] if args.who else sorted(st.cast)
    for n in names:
        p = st.cast.get(n)
        hands = getattr(p, "_hands", None)
        if not hands:
            continue
        for side, held in hands.items():
            for h in held:
                for vn, att in h.variants.items():
                    vis = ""
                    if frames:
                        vis = "  renders: " + " ".join("%d:%s" % (f, "Y" if not _hidden(att.ob, f) else "-")
                                                       for f in frames)
                    print("%-12s %s %-22s %-24s span %s-%s steps %s%s" % (
                        n, side, h.item_id, vn or "(carried)", h.start, h.end,
                        [(a, int(b)) for a, b in att.steps], vis))
    return 0


def cmd_notes(args, ses):
    C = ses.result["context"]
    a, b = (int(v) for v in args.span.split("-"))
    shots = sorted(ses.film.shots, key=lambda s: s.frame_start)
    jb = C.bd.jukebox
    seen = []
    for burst in getattr(jb, "bursts", []):
        for p in burst.particles:
            if a <= p["first"] <= b and p["last"] > p["first"]:
                seen.append((p["first"], p["last"]))
    for first, last in sorted(set(seen)):
        sh = [s.name for s in shots if s.frame_start <= first <= s.frame_end]
        print("note born %7.2f  gone %7.2f  in %s" % (first, last, sh[0] if sh else "-"))
    print("spans", [(round(x, 2), round(y, 2), d) for x, y, d in jb.spans])
    return 0


def cmd_memo(args, ses):
    """What the shot functions left in C.memo (frames of their events), one line each."""
    C = ses.result["context"]
    for k in sorted(C.memo):
        v = C.memo[k]
        print("%-14s %s" % (k, v if isinstance(v, (int, float, dict, tuple, list, str)) else repr(v)))
    return 0


def main(argv):
    import argparse
    ap = argparse.ArgumentParser(prog="tools.crammys_probe")
    ap.add_argument("cmd", choices=("track", "hands", "notes", "memo"))
    ap.add_argument("shot", nargs="?")
    ap.add_argument("frames", nargs="?")
    ap.add_argument("--sky", default="night")
    ap.add_argument("--who")
    ap.add_argument("--cam")
    ap.add_argument("--span", default="1201-1562")
    ap.add_argument("--frames", dest="hand_frames")
    args = ap.parse_args(argv)
    if args.cmd == "hands":
        args.frames = args.hand_frames
    import render
    ses = render.Session("crammys", sky=args.sky)
    return {"track": cmd_track, "hands": cmd_hands, "notes": cmd_notes, "memo": cmd_memo}[args.cmd](args, ses)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
