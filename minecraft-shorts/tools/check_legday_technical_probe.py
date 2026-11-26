"""Independent checker probe for "Leg Day" (numbers on a build, nothing rendered).

    $BPY -m tools.check_legday_technical_probe [--sky gold|dusk]

Visibility of every cast member (and every object under it) per shot, objects with keyed visibility that are not
cast, twins sharing objects, cameras inside blocks / part cells, lines of sight to heroes, body positions of every
character inside blocks, the world state of the anvil wall on all twelve cells.
"""
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


def _objs(c):
    o = getattr(c, "objects", None)
    if o is None:
        obs = [c] if hasattr(c, "hide_render") else []
    else:
        obs = list(o() if callable(o) else o)
    out = []
    seen = set()
    for ob in obs:
        for x in [ob] + list(getattr(ob, "children_recursive", [])):
            if x.name not in seen:
                seen.add(x.name)
                out.append(x)
    return out


def main(argv):
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--sky", default="gold")
    args = ap.parse_args(argv)
    import render
    ses = render.Session("legday", sky=args.sky)
    import bpy
    from films import legday_set as LS
    scene, st, C = ses.scene, ses.result["stage"], ses.result["context"]
    shots = sorted(ses.film.shots, key=lambda s: s.frame_start)
    W = C.v.world
    parts = LS.part_cells()

    def vis(ob):
        return not ob.hide_render

    # ---------------- 1. twins: distinct objects
    owner = {}
    shared = []
    for name, c in st.cast.items():
        for ob in _objs(c):
            if ob.name in owner and owner[ob.name] != name:
                shared.append((ob.name, owner[ob.name], name))
            owner[ob.name] = name
    print("[probe] cast members %d, objects %d, shared objects: %s" % (len(st.cast), len(owner), shared[:10] or "none"))

    # appear exceptions
    appear = {C.anvils[11].name: (C.T["tp14_why"].at("why"), "tp14_why"),
              C.anvils_dusk[11].name: (C.T["tp24_reloading"].at("call"), "tp24_reloading")}

    # ---------------- 2. visibility per shot
    leaks, missing = [], []
    animated_noncast = {}
    for ob in bpy.data.objects:
        if ob.name in owner:
            continue
        ad = ob.animation_data
        from engine import shots as _sh
        if ad and any(fc.data_path == "hide_render" for fc in _sh.fcurves_of(ob)):
            animated_noncast[ob.name] = ob
        elif ad and ad.drivers and any(d.data_path == "hide_render" for d in ad.drivers):
            animated_noncast[ob.name] = ob
    noncast_seen = {}
    for s in shots:
        inn = st.in_shot.get(s.name, set())
        for f in sorted({s.frame_start, s.frame_start + 1, (s.frame_start + s.frame_end) // 2, s.frame_end}):
            scene.frame_set(f)
            for name, c in st.cast.items():
                obs = [o for o in _objs(c) if o.type == "MESH"]
                if not obs:
                    continue
                want = name in inn
                if name in appear:
                    fa, sh = appear[name]
                    if s.name == sh:
                        want = f >= fa
                anyvis = any(vis(o) for o in obs)
                if anyvis and not want:
                    leaks.append((s.name, f, name, [o.name for o in obs if vis(o)][:3]))
                rootvis = vis(obs[0])
                if want and not anyvis:
                    missing.append((s.name, f, name))
            for nm, ob in animated_noncast.items():
                if ob.type in ("MESH", "LIGHT") and vis(ob):
                    noncast_seen.setdefault(nm, set()).add(s.name)
    print("[probe] cast leaks (visible outside their shots): %d" % len(leaks))
    for x in leaks[:40]:
        print("   LEAK", x)
    print("[probe] cast missing (in st.use but nothing visible): %d" % len(missing))
    for x in missing[:40]:
        print("   MISSING", x)
    # non-cast objects with keyed visibility: in which shots are they visible
    groups = {}
    for nm, sh in noncast_seen.items():
        key = tuple(sorted(sh, key=lambda n: C.T[n].frame_start))
        groups.setdefault(key, []).append(nm)
    print("[probe] non-cast objects with keyed visibility, by the shots they are visible in:")
    for key, names in sorted(groups.items(), key=lambda kv: (len(kv[0]), kv[0])):
        print("   %-60s %3d objs e.g. %s" % (",".join(key)[:60] if len(key) < 23 else "ALL %d" % len(key), len(names),
                                             ", ".join(sorted(names)[:4])))

    # ---------------- 3. cameras: inside blocks / parts; heroes blocked
    print("[probe] cameras")
    cam = scene.camera
    for s in shots:
        for f in (s.frame_start, (s.frame_start + s.frame_end) // 2, s.frame_end):
            ses.film.goto(f) if hasattr(ses.film, "goto") else scene.frame_set(f)
            cam = scene.camera
            p = cam.matrix_world.translation
            cell = tuple(int(math.floor(v)) for v in p)
            bad = []
            if LS._solid_at(W, *p):
                bad.append("inside %s" % W.block_id(*cell))
            if cell in parts:
                bad.append("in part cell %s" % parts[cell])
            # nearest solid within 0.25 (near clip)
            for dx in (-0.25, 0.25):
                for dy in (-0.25, 0.25):
                    for dz in (-0.25, 0.25):
                        if LS._solid_at(W, p.x + dx, p.y + dy, p.z + dz) and "near" not in " ".join(bad):
                            bad.append("near a block (0.25)")
            heroes = st.heroes.get(s.name, [])
            blocked = []
            for label, obs in heroes:
                for ob in obs[:6]:
                    tgt = ob.matrix_world.translation
                    hit = LS.ray_block(W, p, tgt)
                    if hit:
                        blocked.append("%s by %s@%s" % (label, hit[1], hit[0]))
                        break
            if bad or blocked or f == s.frame_start:
                print("   %-15s f%4d cam (%.2f, %.2f, %.2f) %s %s" % (s.name, f, p.x, p.y, p.z, "; ".join(bad),
                                                                     ("BLOCKED " + "; ".join(blocked)) if blocked else ""))

    # ---------------- 4. bodies inside blocks (characters in their shots)
    print("[probe] bodies inside solid blocks / part cells")
    nbad = 0
    summ = {}
    for s in shots:
        inn = st.in_shot.get(s.name, set())
        for f in range(s.frame_start, s.frame_end + 1, 3):
            scene.frame_set(f)
            for name in inn:
                c = st.cast[name]
                root = getattr(c, "root", None)
                if root is None:
                    continue
                p = root.matrix_world.translation
                for h in (0.15, 0.9, 1.5):
                    if h > 0.5 and not name.split("_")[0] in ("steve", "kai", "zuri", "ari", "efe", "patrol"):
                        continue
                    q = (p.x, p.y, p.z + h)
                    if LS._solid_at(W, *q):
                        cellq = tuple(int(math.floor(v)) for v in q)
                        summ.setdefault((s.name, name, W.block_id(*cellq), h), []).append(f)
                        nbad += 1
                        if nbad < 40:
                            cell = tuple(int(math.floor(v)) for v in q)
                            print("   %-15s f%4d %-24s at h %.2f (%.2f,%.2f,%.2f) inside %s" % (
                                s.name, f, name, h, q[0], q[1], q[2], W.block_id(*cell)))
                        break
                # floating: nothing solid under the feet (players only)
    print("[probe] %d body-in-block samples" % nbad)
    for k, fs in sorted(summ.items(), key=lambda kv: kv[1][0]):
        print("   SUMMARY %-15s %-28s %-16s h %.2f frames %d-%d (%d samples)" % (k[0], k[1], k[2], k[3], fs[0], fs[-1], len(fs)))

    # ---------------- 5. the wall: all twelve planks / pistons / anvils
    print("[probe] the wall")
    T = C.T
    def xs(blocks, f):
        scene.frame_set(f)
        out = []
        for b in blocks:
            o = b.objects if isinstance(b.objects, list) else b.objects()
            o = [x for x in o if x.type == "MESH"]
            out.append("%.2f%s" % (o[0].matrix_world.translation.x, "" if vis(o[0]) else "h"))
        return out
    for f in (1, 818, 820, 823, 845, 1168, 1169, 1170, 1171, 1172, 1173, 1209, 1368, 1369, 1370, 1371, 1372, 1490):
        print("   f%4d planks x %s" % (f, " ".join(xs(C.row.blocks, f))))
    def heads(f):
        scene.frame_set(f)
        out = []
        for p in C.row.pistons:
            o = p.objects if isinstance(p.objects, list) else p.objects()
            o = [x for x in o if x.type == "MESH"]
            vv = [x for x in o if vis(x)]
            out.append("%d/%d" % (len(vv), len(o)))
        return out
    for f in (1, 818, 819, 820, 822, 1168, 1172, 1369, 1371):
        print("   f%4d piston meshes visible %s" % (f, " ".join(heads(f))))
    for nm, blocks in (("day", C.anvils), ("dusk", C.anvils_dusk)):
        for f in (1, 800, 877, 1168, 1170, 1171, 1172, 1190, 1209, 1210, 1211, 1260, 1368, 1371, 1404, 1495):
            scene.frame_set(f)
            row = []
            for b in blocks:
                o = [x for x in b.objects() if x.type == "MESH"]
                v = [x for x in o if vis(x)]
                if v:
                    row.append("%.1f" % v[0].matrix_world.translation.z)
                else:
                    row.append("-")
            print("   %s f%4d anvil z %s" % (nm, f, " ".join(row)))
    for f in (1, 818, 1107, 1108, 1109, 1368, 1369, 1371, 1490):
        lev = [C.wire.level_at((LS.DUST_X, y, LS.TOP_Z + 1), f) for y in (LS.DUST_Y[0], LS.DUST_Y[6], LS.DUST_Y[-1])]
        print("   f%4d lever %s dust %s" % (f, C.lever.state_at(f), lev))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
