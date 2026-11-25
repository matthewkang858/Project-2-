"""Checker: do render.py's frame fingerprints (engine.stamp) follow what engine.redstone animates?

    $BPY -m tools.check_redstone_stamp          (no rendering, about a minute; exit code 1 if a case fails)

A re-render keeps every frame whose fingerprint is unchanged, so every change redstone.py makes to a picture must
change the fingerprint of exactly the frames it changes: a lever's handle, a dust line's power level, a lamp (its
model AND its light), a repeater, a piston's head and the blocks it moves (sampled over the exposure: motion blur).
redstone.py swaps objects and keys transforms; it animates no material value (the known trap, see CONTRACT.md),
so a fingerprint must not depend on the order a process takes frames in, nor on the process: the tool runs itself
a second time in a child process and compares the digests of every fingerprint.
"""
import hashlib
import os
import subprocess
import sys

import bpy

from engine import look, redstone, stamp

FAILED = []


def ok(label, cond, detail=""):
    """Print one case; remember it when it failed."""
    if not cond:
        FAILED.append(label)
    print("%-4s %s%s" % ("OK" if cond else "FAIL", label, ("  [%s]" % detail) if detail else ""), flush=True)


def fresh():
    """An empty scene with the FINAL render settings (motion blur on: fingerprints sample the shutter)."""
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    look.setup_render(scene, res=(720, 1280), samples=24, threads=4)
    return scene


def shot(proof, name):
    s = next(s for s in proof["film"].shots if s.name == name)
    return list(range(s.frame_start, s.frame_end + 1))


def prints(proof, frames, order=None):
    """{frame: objects+lights+camera digest} taken in `order` (default: ascending)."""
    fp = stamp.Fingerprinter(proof["film"].scene, proof["film"])
    got = {}
    for f in (order or frames):
        p = fp.frame(f)["parts"]
        got[f] = p["o"] + p["l"] + p["c"]
    return got


def runs(frames):
    out = []
    for f in sorted(frames):
        if out and f == out[-1][1] + 1:
            out[-1][1] = f
        else:
            out.append([f, f])
    return ["%d-%d" % (a, b) if a != b else "%d" % a for a, b in out]


def digest_of(proof, frames):
    a = prints(proof, frames)
    h = hashlib.sha1()
    for f in frames:
        h.update(a[f].encode())
    return h.hexdigest()[:16], a


def main(argv):
    names = ("bench", "lever", "column", "row", "door")
    base = redstone.build_proof(fresh())
    frames = [f for n in names for f in shot(base, n)]
    if "--child" in argv:
        print("DIGEST", digest_of(base, frames)[0], flush=True)
        return 0
    dig, a = digest_of(base, frames)
    b = prints(base, frames, order=list(reversed(frames)))
    c = prints(base, frames, order=frames[len(frames) // 2:] + frames[:len(frames) // 2])
    ok("fingerprints do not depend on the order a process takes the frames in (%d frames, 3 orders)" % len(frames),
       a == b == c)

    # the row: static before the lever, then lever + dust + 4 pistons + 4 planks on the flip frame, static after
    fr = shot(base, "row")
    f0 = fr[0]
    flip = f0 + 6
    same_before = len({a[f] for f in fr if f < flip}) == 1
    moving = [f for f in fr if a[f] != a[f - 1]] if fr[0] - 1 in a else None
    changed = [f for f in fr[1:] if a[f] != a[f - 1]]
    ok("row: nothing changes before the lever (frames %d-%d), the flip frame changes (lever, dust dark, pistons "
       "start), frames change while the planks move, nothing after the move" % (f0, flip - 1),
       same_before and changed == [flip, flip + 1, flip + 2, flip + 3], "changed %s" % runs(changed))
    _ = moving

    # the column: the same for an upward push of twelve blocks
    fc = shot(base, "column")
    f0 = fc[0]
    changed = [f for f in fc[1:] if a[f] != a[f - 1]]
    ok("column: frame-to-frame changes exactly on the lever's frame and the frames exposed while the 12 blocks rise",
       changed == [f0 + 6, f0 + 7, f0 + 8, f0 + 9], "changed %s" % runs(changed))

    # the door: opens at +8, closes at +30
    fd = shot(base, "door")
    f0 = fd[0]
    changed = [f for f in fd[1:] if a[f] != a[f - 1]]
    want = [f0 + 8, f0 + 9, f0 + 10, f0 + 11, f0 + 30, f0 + 31, f0 + 32, f0 + 33]
    ok("door: changes exactly while the two blocks and the heads move (open at +8, close at +30)",
       changed == want, "changed %s, expected %s" % (runs(changed), runs(want)))

    # the same proof built again: identical
    again = prints(redstone.build_proof(fresh()), frames)
    ok("the same proof built again in this process: identical fingerprints", again == a,
       "differ on %s" % runs([f for f in frames if again[f] != a[f]]))

    # one lamp that does not light: the bench frames from the lamp's frame on change, and only those
    p = redstone.build_proof(fresh())
    lamp = p["parts"]["bench_lamp"]
    on = min(f for f in shot(p, "bench") if lamp.lit_at(f))
    lamp.set(on, False)
    got = prints(p, frames)
    changed = [f for f in frames if got[f] != a[f]]
    want = [f for f in frames if f >= on]
    ok("a lamp kept dark from frame %d: exactly the frames from there on change (its model, and its light, which is "
       "a rendered light in every later shot)" % on,
       changed == want, "changed %s" % runs(changed))

    # one dust block keyed to another power for one frame
    p = redstone.build_proof(fresh())
    w = p["parts"]["row_wire"]
    fr0 = shot(p, "row")[0]
    w.set_levels(fr0 + 2, {w.cells[-1]: 3})
    w.set_levels(fr0 + 3, {w.cells[-1]: w.level_at(w.cells[-1], fr0 + 1)})
    got = prints(p, frames)
    changed = [f for f in frames if got[f] != a[f]]
    ok("one dust block at power 3 instead of 12 on frame %d: that frame and no other" % (fr0 + 2),
       changed == [fr0 + 2], "changed %s" % runs(changed))

    # the column's piston one frame later
    p = redstone.build_proof(fresh())
    cp = p["parts"]["column_piston"]
    f0 = shot(p, "column")[0]
    t_old = min(cp.moves)
    cp.cancel(t_old)
    cp.extend(t_old + 1.0)
    got = prints(p, frames)
    changed = [f for f in frames if got[f] != a[f]]
    ok("the column's extension one frame later: only the frames whose exposure sees a different travel change",
       changed and min(changed) >= f0 + 6 and max(changed) <= f0 + 10, "changed %s" % runs(changed))

    # a second process
    env = dict(os.environ)
    res = subprocess.run([sys.executable, "-m", "tools.check_redstone_stamp", "--child"], capture_output=True,
                         text=True, env=env, cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                         timeout=200)
    child = [ln.split()[1] for ln in res.stdout.splitlines() if ln.startswith("DIGEST")]
    ok("the same digest of every fingerprint in a separate process", child == [dig],
       "this %s, child %s" % (dig, child or res.stderr[-300:]))
    print("[check_redstone_stamp] %d failed%s" % (len(FAILED), ": " + "; ".join(FAILED) if FAILED else ""))
    print("[check_redstone_stamp] digest of all fingerprints: %s" % dig)
    return 1 if FAILED else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
