"""Checker: do render.py's frame fingerprints (engine.stamp) follow what engine.breaking animates?

    $BPY -m tools.check_breaking_stamp          (no rendering, 1-2 minutes; exit code 1 if a case fails)

A re-render keeps every frame whose fingerprint is unchanged, so each thing breaking.py animates must change the
fingerprint of exactly the frames whose picture it changes: a crack stage, the half that is cracked, the door's
shudder, a door or block that is gone, a block mined at another moment. Making the film's bang_on_door calls
again must change nothing (the shudder is rewritten from a record of the blows). A fingerprint must not depend on the
frame a process happens to look at first (the known trap of animated materials, see CONTRACT.md): breaking.py
swaps objects instead of animating a material, and this proves it on the proof films of engine.breaking.
The last line is a digest of every fingerprint taken: run the tool twice, the two digests must be equal.
"""
import hashlib
import sys

import bpy

from engine import breaking, look, stamp

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


def prints(proof, frames, order=None):
    """{frame: fingerprint of the objects part} taken in `order` (default: ascending)."""
    fp = stamp.Fingerprinter(proof["film"].scene, proof["film"])
    got = {}
    for f in (order or frames):
        got[f] = fp.frame(f)["parts"]["o"]
    return got


def door_curve(door, frames):
    """The door's angle at every half frame of `frames` (what the shudder keys)."""
    fc = door.animation_data.action.fcurve_ensure_for_datablock(door, "rotation_euler", index=2)
    return [round(fc.evaluate(f / 2.0), 6) for f in range(2 * frames[0], 2 * frames[-1] + 1)]


def runs(frames):
    """[(first, last), ...] of the consecutive runs in a list of frames (for printing)."""
    out = []
    for f in sorted(frames):
        if out and f == out[-1][1] + 1:
            out[-1][1] = f
        else:
            out.append([f, f])
    return ["%d-%d" % (a, b) if a != b else "%d" % a for a, b in out]


def main():
    digest = hashlib.sha1()

    # ---- the door film: sheet (frames 1-12), bang (13-108), far (109-156)
    base = breaking.build_door_proof(fresh(), sky="night", shudder=1.5)
    film = base["film"]
    frames = list(range(film.frame_start, film.frame_end + 1))
    a = prints(base, frames)
    b = prints(base, frames, order=list(reversed(frames)))
    c = prints(base, frames, order=frames[60:] + frames[:60])
    ok("door film: the fingerprints do not depend on the order a process takes them in (%d frames, 3 orders)"
       % len(frames), a == b == c)
    for f in frames:
        digest.update(a[f].encode())
    sheet = base["shots"]["sheet"]
    fs = list(range(sheet.frame_start, sheet.frame_end + 1))
    distinct = len({a[f] for f in fs})
    ok("sheet shot (nothing moves but the stage): clean, ten stages, clean = 11 different fingerprints in 12 frames",
       distinct == 11 and a[fs[0]] == a[fs[-1]], "%d distinct" % distinct)
    stages = {f: breaking.stage_at(base["door"], f) for f in frames}
    hits = base["bang"]["hits"] + base["far"]["hits"]
    door_was = door_curve(base["door"], frames)               # (base is gone once the next scene is built)

    again = prints(breaking.build_door_proof(fresh(), sky="night", shudder=1.5), frames)
    ok("the same film built again in this process: identical fingerprints", again == a,
       "differ on %s" % runs([f for f in frames if again[f] != a[f]]))

    plain = prints(breaking.build_door_proof(fresh(), sky="night", shudder=0.0), frames)
    changed = [f for f in frames if plain[f] != a[f]]
    want = sorted({f for h in hits for f in (h - 1, h, h + 1, h + 2)} & set(frames))
    ok("shudder off: exactly the frames exposed while the door moves change (blow - 1 .. blow + 2, %d blows)"
       % len(hits), changed == want, "changed %s, expected %s" % (runs(changed), runs(want)))

    both = prints(breaking.build_door_proof(fresh(), sky="night", shudder=1.5, half="both"), frames)
    changed = [f for f in frames if both[f] != a[f]]
    want = [f for f in frames if stages[f] >= 0]
    ok("half='both' instead of 'upper': exactly the frames with cracks on the door change (%d of %d)"
       % (len(want), len(frames)), changed == want, "changed %s, expected %s" % (runs(changed), runs(want)))

    p = breaking.build_door_proof(fresh(), sky="night", shudder=1.5)
    bang = p["shots"]["bang"]
    f5 = next(f for f in range(bang.frame_start, bang.frame_end) if breaking.stage_at(p["door"], f) == 5)
    nxt = next(f for f in range(f5, bang.frame_end + 2) if breaking.stage_at(p["door"], f) != 5)
    breaking.crack(p["door"], f5, 8)                          # one stage keyed differently: frames f5 .. nxt - 1
    got = prints(p, frames)
    changed = [f for f in frames if got[f] != a[f]]
    ok("one stage keyed differently (5 -> 8 on frames %d-%d): those frames and no others" % (f5, nxt - 1),
       changed == list(range(f5, nxt)), "changed %s" % runs(changed))

    p = breaking.build_door_proof(fresh(), sky="night", shudder=1.5)
    bang = p["shots"]["bang"]
    far = p["shots"]["far"]
    for _again in range(2):                                   # the film's own two calls, made a second and third time
        breaking.bang_on_door(p["zombie"], p["door"], bang.frame_start, bang.frame_end + 1, attempt=40, pause=2,
                              every=16.0, first=4, half="upper", shudder=1.5, along=0.0, camera=bang,
                              world=p["village"])
        breaking.bang_on_door(p["zombie"], p["door"], far.frame_start, far.frame_end + 1, attempt=40, pause=2,
                              every=16.0, first=4, half="upper", shudder=1.5, along=0.0, camera=far,
                              world=p["village"], phase=0.55, place=False)
    got = prints(p, frames)
    door_now = door_curve(p["door"], frames)
    changed = [f for f in frames if got[f] != a[f]]
    ok("both bang_on_door calls of the film made twice more (shudder on): the door's curve and its cracks are "
       "unchanged, and no frame's fingerprint changes", not changed and door_now == door_was
       and [breaking.stage_at(p["door"], f) for f in frames] == [stages[f] for f in frames],
       "changed %s" % runs(changed))

    p = breaking.build_door_proof(fresh(), sky="night", shudder=1.5, break_at_end=True)
    got = prints(p, frames)
    fb = p["far"]["frame"]
    far = base["shots"]["far"]
    changed = [f for f in frames if got[f] != a[f]]
    ok("the door breaking on frame %d: nothing before the far shot changes, every frame from the break on does"
       % fb, changed and changed[0] >= far.frame_start and set(range(fb, film.frame_end + 1)) <= set(changed),
       "changed %s" % runs(changed))

    # ---- the mining film: stone (6 + 48 frames + rest), dirt
    m = breaking.build_mine_proof(fresh())
    mf = m["film"]
    frames = list(range(mf.frame_start, mf.frame_end + 1))
    a = prints(m, frames)
    b = prints(m, frames, order=list(reversed(frames)))
    ok("mining film: order-independent fingerprints (%d frames)" % len(frames), a == b)
    for f in frames:
        digest.update(a[f].encode())
    m2 = breaking.build_mine_proof(fresh())
    f6 = next(f for f, s in m2["stone_mine"]["stages"] if s == 6)
    f7 = next(f for f, s in m2["stone_mine"]["stages"] if s == 7)
    breaking.crack(m2["stone"], f6, 2)
    got = prints(m2, frames)
    changed = [f for f in frames if got[f] != a[f]]
    ok("a stone block's stage keyed differently on frames %d-%d: those frames and no others" % (f6, f7 - 1),
       changed == list(range(f6, f7)), "changed %s" % runs(changed))
    m3 = breaking.build_mine_proof(fresh())
    fb = m3["dirt_mine"]["frame"]
    breaking.restore(m3["dirt"], fb + 10)                     # the dirt block is back ten frames after it broke
    got = prints(m3, frames)
    changed = [f for f in frames if got[f] != a[f]]
    ok("a broken block put back on frame %d: every frame from there on changes, none before" % (fb + 10),
       changed == list(range(fb + 10, mf.frame_end + 1)), "changed %s" % runs(changed))
    print("[check_breaking_stamp] %d failed%s" % (len(FAILED), ": " + "; ".join(FAILED) if FAILED else ""))
    print("[check_breaking_stamp] digest of all fingerprints: %s (run twice: it must not change)"
          % digest.hexdigest()[:16])
    return 1 if FAILED else 0


if __name__ == "__main__":
    sys.exit(main())
