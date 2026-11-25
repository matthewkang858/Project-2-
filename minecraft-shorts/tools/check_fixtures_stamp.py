"""Checker: do render.py's frame fingerprints (engine.stamp) follow what engine.fixtures animates?

    $BPY -m tools.check_fixtures_stamp            (no rendering, about a minute; exit code 1 if a case fails)

A re-render keeps every frame whose fingerprint is unchanged, so each thing fixtures.py animates must change the
fingerprint of exactly the frames whose picture it changes, and nothing else may:
  - the water's animated texture (one object per image, shown in turn: no animated material),
  - the lava's light flicker (keyed light energy),
  - a chest lid opening (keyed rotation, sampled over the shutter),
  - an anvil falling and landing chipped (keyed location, then another object on the landing frame),
  - items taken by a hopper (engine.mobs DroppedItems keyed by Hopper.stream).
Each case is a small scene of its own (a stone floor and the one thing, final render settings: motion blur on).
Fingerprints must not depend on the order a process takes the frames in, and the same scene built in another
PROCESS must give the same digest (the known trap of animated materials, CONTRACT.md): the tool runs itself again
in a child process and compares the digests.
"""
import hashlib
import json
import math
import os
import subprocess
import sys

import bpy

from engine import blocks, fixtures, look, shots, stamp

FAILED = []
FRAMES = list(range(1, 97))


def ok(label, cond, detail=""):
    """Print one case; remember it when it failed."""
    if not cond:
        FAILED.append(label)
    print("%-4s %s%s" % ("OK" if cond else "FAIL", label, ("  [%s]" % detail) if detail else ""), flush=True)


def runs(frames):
    """'3-7, 9' for printing."""
    out = []
    for f in sorted(frames):
        if out and f == out[-1][1] + 1:
            out[-1][1] = f
        else:
            out.append([f, f])
    return ", ".join("%d-%d" % (a, b) if a != b else "%d" % a for a, b in out)


def scene_with(case):
    """A fresh scene with the final render settings, a floor, a camera shot over FRAMES and the case's thing."""
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    look.setup_render(scene, res=(720, 1280), samples=24, threads=4)
    coll = blocks.new_collection(scene, "set")
    st = fixtures.site(coll)
    st.world.fill(-4, -4, -1, 8, 8, -1, "stone")
    film = shots.Film(scene, fps=24)
    sh = film.shot("all", 0.0, len(FRAMES) / 24.0)
    sh.lens(35, 4.0)
    sh.move((2.0, -8.0, 4.0), (2.0, 2.0, 0.5))
    thing = case(st)
    st.world.build(coll, "floor")
    film.finalize()
    return scene, film, thing


def prints(scene, film, order=None, part="o"):
    """{frame: digest of one part} taken in `order` (default ascending)."""
    fp = stamp.Fingerprinter(scene, film)
    return {f: fp.frame(f)["parts"][part] for f in (order or FRAMES)}


def changed(d):
    """Frames whose digest differs from the frame before."""
    return [f for f in FRAMES[1:] if d[f] != d[f - 1]]


def sampled(fn, f):
    """A value at the three shutter samples of frame f (START position, shutter 0.5)."""
    return tuple(round(fn(t), 4) for t in (f, f + 0.25, f + 0.5))


# ---- the cases -------------------------------------------------------------------------------------
def case_water(st):
    return fixtures.water_sheet(st, 0, 0, 3, 3, 0, toward=None, amount=8, name="w")


def case_lava(st):
    lv = fixtures.lava(st, [(x, 0, 0) for x in range(4)], name="lv")
    lv.flicker(30, 80, at=40)
    return lv


def case_chest(st):
    c = fixtures.chest(st, (1, 1, 0), "south")
    c.open(20)
    c.close(60)
    return c


def case_anvil(st):
    a = fixtures.block(st, "anvil", (2, 2, 9), {"facing": "north"})
    return fixtures.fall(a, frame=20, world=st, chip=True)


def case_hopper(st):
    from engine import mobs

    st.world.set(2, 2, 0, "chest", {"facing": "south"})
    h = fixtures.hopper(st, (2, 2, 1))
    items = [mobs.make_dropped_item(i, name="it%d" % n, seed=n) for n, i in enumerate(("iron_ingot", "poppy"))]
    return h.stream(items, 10, every=6, height=2.0, seed=1)


def main(child=False):
    digest = hashlib.sha1()

    # water: the 'o' part changes exactly where the shown image changes, and only there
    scene, film, w = scene_with(case_water)
    a = prints(scene, film)
    b = prints(scene, film, order=list(reversed(FRAMES)))
    want = set()
    for tex in ("block/water_still", "block/water_flow"):          # the top is still, the sides show water_flow
        _count, order, time = fixtures.animation_of(tex)
        period, shown = fixtures.texture_schedule(order, time)
        want |= {f for f in FRAMES[1:] if shown[(f - 1) % period] != shown[(f - 2) % period]}
    want = sorted(want)
    _count, order, time = fixtures.animation_of("block/water_still")
    period, shown = fixtures.texture_schedule(order, time)
    ok("water: the fingerprint changes on the frames an image of water_still (top) or water_flow (sides) changes "
       "(%d of %d)" % (len(want), len(FRAMES)), changed(a) == want,
       "changed %s, expected %s" % (runs(changed(a)), runs(want)))
    ok("water: the same fingerprints taken in reverse order", a == b)
    ok("water: two frames showing the same image have the same fingerprint (frames 1 and 2 show image 0)",
       a[1] == a[2] and shown[0] == shown[1])
    digest.update(json.dumps(a, sort_keys=True).encode())

    # lava flicker: the lights part changes on the flicker frames only; objects only with the texture
    scene, film, lv = scene_with(case_lava)
    la = prints(scene, film, part="l")
    lb = prints(scene, film, order=FRAMES[50:] + FRAMES[:50], part="l")
    want = [f for f in FRAMES[1:] if abs(lv.light_factor(f) - lv.light_factor(f - 1)) > 1e-6]
    ok("lava: the lights part changes exactly on the frames the flicker changes the energy (%s)" % runs(want),
       changed(la) == want, "changed %s" % runs(changed(la)))
    ok("lava: the same light fingerprints in another order", la == lb)
    digest.update(json.dumps(la, sort_keys=True).encode())

    # chest: open(20) / close(60): the lid's matrix over the shutter
    scene, film, c = scene_with(case_chest)
    ca = prints(scene, film)
    fc = c.lid.animation_data.action.fcurve_ensure_for_datablock(c.lid, "rotation_euler", index=0)
    want = [f for f in FRAMES[1:] if sampled(fc.evaluate, f) != sampled(fc.evaluate, f - 1)]
    ok("chest: the fingerprint changes on the frames the lid moves (%s) and on no other" % runs(want),
       changed(ca) == want, "changed %s" % runs(changed(ca)))
    digest.update(json.dumps(ca, sort_keys=True).encode())

    # anvil: hangs 2 ticks, falls, lands chipped
    scene, film, d = scene_with(case_anvil)
    aa = prints(scene, film)
    blk = d["block"]
    ob = blk.object
    zc = ob.animation_data.action.fcurve_ensure_for_datablock(ob, "location", index=2)
    moving = [f for f in FRAMES[1:] if sampled(zc.evaluate, f) != sampled(zc.evaluate, f - 1)]
    want = sorted(set(moving) | {d["frame_land"]})
    ok("anvil: the fingerprint changes while it falls (%s) and on the frame it is the chipped anvil (%d)"
       % (runs(moving), d["frame_land"]), changed(aa) == want, "changed %s" % runs(changed(aa)))
    ok("anvil: from the landing on nothing changes", all(aa[f] == aa[d["frame_land"]] for f in FRAMES
                                                         if f >= d["frame_land"]))
    digest.update(json.dumps(aa, sort_keys=True).encode())

    # hopper: items appear, fall, lie, are taken
    scene, film, plans = scene_with(case_hopper)
    ha = prints(scene, film)
    hb = prints(scene, film, order=list(reversed(FRAMES)))
    gone = [p["frame"] for p in plans]
    ok("hopper: a fingerprint change on each frame an item is taken (%s)" % gone,
       all(ha[f] != ha[f - 1] for f in gone))
    last = max(gone)
    ok("hopper: after the last take the fingerprint stays the same", all(ha[f] == ha[last] for f in FRAMES if f >= last))
    ok("hopper: the same fingerprints in reverse order", ha == hb)
    digest.update(json.dumps(ha, sort_keys=True).encode())

    print("DIGEST %s" % digest.hexdigest(), flush=True)
    if not child:
        env = dict(os.environ)
        out = subprocess.run([sys.executable, "-m", "tools.check_fixtures_stamp", "--child"], capture_output=True,
                             text=True, env=env, cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                             timeout=250)
        other = [ln.split()[1] for ln in out.stdout.splitlines() if ln.startswith("DIGEST ")]
        ok("the same scenes built in another process give the same fingerprints",
           bool(other) and other[0] == digest.hexdigest(), "%s vs %s" % (digest.hexdigest()[:12],
                                                                          other[0][:12] if other else out.stderr[-300:]))
    print("[check_fixtures_stamp] %d failed%s" % (len(FAILED), (": " + "; ".join(FAILED)) if FAILED else ""))
    return 1 if FAILED else 0


if __name__ == "__main__":
    sys.exit(main(child="--child" in sys.argv[1:]))
