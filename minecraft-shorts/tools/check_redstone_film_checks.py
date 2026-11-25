"""Numeric / robustness checks for tools/check_redstone_film.py (independent check of engine/redstone.py)."""
import math
import subprocess
import sys

import bpy
from mathutils import Vector

from engine import blocks, redstone
from tools import check_redstone_film as F

RESULTS = []


def ok(label, cond, detail=""):
    RESULTS.append((label, bool(cond)))
    print("%-4s %s%s" % ("OK" if cond else "FAIL", label, ("  [%s]" % detail) if detail else ""), flush=True)


def rendered(ob):
    return not ob.hide_render


def shot_of(film, name):
    return next(s for s in film.shots if s.name == name)


def import_untouched():
    code = ("import bpy\n"
            "bpy.ops.wm.read_factory_settings(use_empty=True)\n"
            "def snap():\n"
            "    return {k: len(getattr(bpy.data, k)) for k in ('objects','collections','materials','images','meshes',"
            "'lights','actions','node_groups','worlds','scenes','texts')}\n"
            "a = snap()\n"
            "import engine.redstone\n"
            "b = snap()\n"
            "print('SNAP', a == b, a, b)\n")
    r = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, timeout=120,
                       cwd="/home/user/Project-2-/minecraft-shorts")
    line = [x for x in r.stdout.splitlines() if x.startswith("SNAP")]
    ok("importing engine.redstone leaves bpy.data untouched", line and line[0].startswith("SNAP True"),
       line[0][:200] if line else r.stderr[-300:])


def visibility(out):
    film, P, k = out["film"], out["parts"], out["k"]
    scene = film.scene
    mids = {s.name: (s.frame_start + s.frame_end) // 2 for s in film.shots}
    groups = {
        "door": [P["lever"], P["door"]],
        "row": [P["row"], P["p12"], P["rlever"], P["wire"]],
        "bench": [P["torch"], P["wire2"], P["rep"], P["lamp"], P["pis"]],
    }
    bad = []
    for home, parts in groups.items():
        for p in parts:
            obs = p.objects if hasattr(p, "objects") else (
                [o for q in p.pistons for o in q.objects] + [b.object for b in p.blocks])
            for sname, f in mids.items():
                scene.frame_set(f)
                vis = [o.name for o in obs if rendered(o)]
                want = sname == home or (home == "bench" and sname == "close")
                if want and not vis:
                    bad.append(("nothing of %s visible in its shot %s" % (p.name, sname)))
                if not want and vis:
                    bad.append(("%s visible in shot %s: %s" % (p.name, sname, vis[:3])))
    ok("registered parts (incl. lights) are visible only in their own shots", not bad, "; ".join(bad[:6]))
    # lamp light exactly while the lit look is rendered
    lamp = P["lamp"]
    on_ob = lamp.looks.looks[True][0]
    mism = []
    for f in range(film.frame_start, film.frame_end + 1):
        scene.frame_set(f)
        if rendered(lamp.light) != rendered(on_ob):
            mism.append(f)
    ok("lamp: its light is rendered on exactly the frames its lit model is", not mism, str(mism[:10]))
    tor = P["torch"]
    mism = []
    for f in range(film.frame_start, film.frame_end + 1):
        scene.frame_set(f)
        lit = [o for o in tor.looks.looks[True]]
        if rendered(tor.light) != any(rendered(o) for o in lit):
            mism.append(f)
    ok("redstone torch: its light is rendered exactly while its lit model is", not mism, str(mism[:10]))
    # held torch light follows the item and the player's visibility
    efe = P["efe"]
    item = efe.item("right")
    L = bpy.data.objects.get(item.get("redstone_glow_light", "")) if item is not None else None
    mism = []
    for f in range(film.frame_start, film.frame_end + 1):
        scene.frame_set(f)
        if L is None or rendered(L) != rendered(item):
            mism.append(f)
    ok("held torch light follows the held item on every frame", not mism, str(mism[:8]))


def contact(out):
    """From the EVALUATED objects at sub-frames: pushed / pulled blocks touch the head plate; the head drawn on each
    frame keeps its arm inside the base for the whole exposure."""
    film, P = out["film"], out["parts"]
    scene = film.scene
    probs = []
    cases = []
    row = P["row"]
    for p, b in list(zip(row.pistons, row.blocks)) + [(P["p12"], P["plank12"])]:
        cases.append((p, b, "row"))
    door = P["door"]
    for p, b in zip(door.pistons, door.blocks):
        cases.append((p, b, "door"))
    for p, b, label in cases:
        s = shot_of(film, label)
        for f in range(s.frame_start, s.frame_end + 1):
            look = p.looks.at(f)
            for k in range(5):
                sub = 0.5 * k / 4.0
                scene.frame_set(f, subframe=sub)
                head = p.head_long if look == "L" else p.head_short
                hl = Vector(head.matrix_world.translation)
                bl = Vector(b.object.matrix_world.translation)
                d = p.dir
                pos = d.dot(Vector((1, 1, 1))) > 0
                far = lambda c: Vector(c).dot(d) + (1.0 if pos else 0.0)       # the face of a cell toward d
                near = lambda c: Vector(c).dot(d) + (0.0 if pos else -1.0)     # the face of a cell away from d
                front = far(hl)
                back_of_block = near(bl)
                if look in ("S", "L"):
                    base0 = near(p.cell)                                     # the back of the base
                    plate_back = front - 0.25
                    arm_back = plate_back - (1.0 if look == "L" else 0.75)
                    if arm_back < base0 - 1e-4 or arm_back > base0 + 0.75 + 1e-4:
                        probs.append("%s f%d+%.3f look %s arm_back %.3f base %.3f..%.3f" % (
                            p.name, f, sub, look, arm_back, base0, base0 + 0.75))
                    gap = back_of_block - front
                    if b.object.hide_render:
                        continue
                    if abs(gap) > 1e-4 and abs(gap) < 0.999:
                        probs.append("%s f%d+%.3f block gap %.4f" % (p.name, f, sub, gap))
                    if gap < -1e-4:
                        probs.append("%s f%d+%.3f block overlaps head %.4f" % (p.name, f, sub, gap))
        scene.frame_set(film.frame_start)
    ok("evaluated objects: pushed / pulled blocks touch the plate, arms stay inside the base (5 samples per "
       "exposure, 12 row pistons + 2 door pistons)", not probs, "; ".join(probs[:5]))


def api(out):
    k, P, st = out["k"], out["parts"], out["st"]
    ok("kit(v) twice returns the same kit", redstone.kit(out["v"]) is k)
    miss = [type(x).__name__ for x in (P["row"], P["anvils"][0], P["door"], P["wire"], P["lever"])
            if not hasattr(x, "objects")]
    ok("every builder's return has .objects (docstring: 'every builder returns a part with .name, .show, "
       ".objects')", not miss, "missing on %s" % miss)
    # two rows / doors made without names
    w = blocks.World()
    w.fill(0, 0, -1, 40, 40, -1, "stone")
    k2 = redstone.kit(w)
    r1 = k2.piston_row([(x, 2, 0) for x in range(2, 6)], "north")
    r2 = k2.piston_row([(x, 10, 0) for x in range(2, 6)], "north")
    d1 = k2.piston_door([(20, 5, 0)], "east")
    d2 = k2.piston_door([(20, 15, 0)], "east")
    ok("two piston_rows / piston_doors made with the default name get distinct .name (st.cast is keyed by it)",
       r1.name != r2.name and d1.name != d2.name and r1.pistons[0].name != r2.pistons[0].name,
       "rows %r %r, pistons %r %r, doors %r %r" % (r1.name, r2.name, r1.pistons[0].name, r2.pistons[0].name,
                                                    d1.name, d2.name))
    # sky_light=0 (an underground set): parts are not black
    k3 = redstone.kit(blocks.World(), sky_light=0)
    dim = k3._dim(None)
    from engine import sets
    ok("kit(sky_light=0) dims parts as engine.sets bakes level 0 (LIGHT_FLOOR: x%.2f)" % sets.lightmap(
        sets.LIGHT_FLOOR), dim is not None and abs(dim - sets.lightmap(sets.LIGHT_FLOOR)) < 0.02,
       "parts get x%.3f" % dim)
    # 13 blocks
    k4 = redstone.kit(blocks.World())
    col = [k4.block("iron_block", (0, 0, z)) for z in range(1, 14)]
    p = k4.piston((0, 0, 0), "up")
    try:
        p.extend(5.0)
        ok("13 blocks: RedstoneError", False)
    except redstone.RedstoneError as e:
        ok("13 blocks: RedstoneError with a clear message", "12" in str(e), str(e)[:120])
    # frame 1
    k5 = redstone.kit(blocks.World())
    p5 = k5.piston((0, 5, 0), "north", sticky=True)
    b5 = k5.block("stone", (0, 6, 0))
    p5.extend(1.0)
    lv = k5.lever((3, 3, 0), "floor", "north")
    lv.flip(1)
    wr = k5.wire([(5, 5, 0), (6, 5, 0)], source=(4, 5, 0))
    wr.power(1, source=(4, 5, 0))
    ok("frame 1: piston extend(1), lever flip(1), wire power(1) work (looks at 0/1/2: %s, lever 0/1: %s/%s, "
       "dust 0/1: %s/%s)" % ([p5.look_at_frame(f) for f in (0, 1, 2)], lv.state_at(0), lv.state_at(1),
                            wr.level_at((5, 5, 0), 0), wr.level_at((5, 5, 0), 1)),
       [p5.look_at_frame(f) for f in (0, 1, 2)] == ["R", "S", "L"] and lv.state_at(1) and not lv.state_at(0))


def timing(out):
    P = out["parts"]
    d = out["door"]
    b = out["bench"]
    r = out["row"]
    ok("door: lever changes the frame after the click (flip %d, click %d), door opens on it" % (d["flip"], d["click"]),
       d["flip"] == d["click"] + 1 or d["flip"] == d["click"] + 2)
    lamp, pis, rep, wire2, torch = P["lamp"], P["pis"], P["rep"], P["wire2"], P["torch"]
    fl = [f for f in range(out["film"].frame_start, out["film"].frame_end) if lamp.lit_at(f)]
    fr = [f for f in range(out["film"].frame_start, out["film"].frame_end) if rep.looks.at(f)]
    fp = [f for f in range(out["film"].frame_start, out["film"].frame_end) if pis.look_at_frame(f) != "R"]
    ft = [f for f in range(out["film"].frame_start, out["film"].frame_end) if torch.looks.at(f) is True]
    print("   bench: plant", b["plant"], "torch from", ft[:1], "dust", wire2.level_at(BENCH_DUST0, b["plant"]),
          "repeater from", fr[:1], "lamp from", fl[:1], "piston from", fp[:1])
    ok("bench: torch on the frame after the click, repeater/lamp/piston 2 ticks later (same frame), in order",
       ft and fr and fl and fp and fr[0] == fl[0] == fp[0] and fr[0] - ft[0] in (2, 3))
    print("   row: flip", r["flip"], "end", r["end"], "dust dark at", r["flip"],
          P["wire"].level_at(F.DUST[0], r["flip"]), P["wire"].level_at(F.DUST[0], r["flip"] - 1))


BENCH_DUST0 = F.BENCH["dust"][0]


def stamp_vs_redstone(out):
    """Every frame where a redstone object's rendered state (visibility / matrices over the shutter) changes from
    the previous frame must change the stamp fingerprint."""
    from engine import stamp

    film = out["film"]
    scene = film.scene
    k = out["k"]
    rs_obs = [o for o in scene.objects if o.get("mc_redstone") or o.get("mc_light") == "redstone"
              or any(o is m.object for m in k.movables)]
    fp = stamp.Fingerprinter(scene, film)
    prev_rec, prev_fp, miss = None, None, []
    for f in range(film.frame_start, film.frame_end + 1):
        rec = []
        for t in (f, f + 0.25, f + 0.5):
            whole = math.floor(t)
            scene.frame_set(int(whole), subframe=t - whole)
            rec.append(tuple((o.name, rendered(o) if t == f else None, tuple(round(x, 4) for x in
                                                                             o.matrix_world.translation))
                             for o in rs_obs if rendered(o)))
        scene.frame_set(f)
        p = fp.frame(f)["fp"]
        if prev_rec is not None and rec != prev_rec and p == prev_fp:
            miss.append(f)
        prev_rec, prev_fp = rec, p
    ok("stamp: every frame on which a redstone object's picture changes has a new fingerprint (%d objects)"
       % len(rs_obs), not miss, str(miss[:10]))


def main(argv):
    import_untouched()
    scene = F.fresh((720, 1280), 24)
    out = F.build(scene)
    ok("film builds through the hook with no problems", not out["v"].edit_problems, str(out["v"].edit_problems))
    api(out)
    timing(out)
    visibility(out)
    contact(out)
    stamp_vs_redstone(out)
    bad = [l for l, c in RESULTS if not c]
    print("[check_redstone_film] %d checks, %d failed" % (len(RESULTS), len(bad)))
    for l in bad:
        print("   FAILED:", l)
