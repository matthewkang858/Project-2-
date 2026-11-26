"""Checker: do render.py's frame fingerprints (engine.stamp) follow what engine.hostiles animates?

    $BPY -m tools.check_hostiles_stamp          (no rendering, about a minute; exit code 1 if a case fails)

A re-render keeps every frame whose fingerprint is unchanged, so everything engine.hostiles animates must change the
fingerprint of exactly the frames whose picture it changes: the creeper's swell and white flash (shells switched by
visibility, not an animated material), the skeleton's bow models, a stuck arrow appearing, an arrow in flight, the
explosion. A fingerprint must not depend on the order a process takes them in (the animated-material trap of
CONTRACT.md). The last line is a digest of every fingerprint taken: run the tool twice, the digests must be equal.
"""
import hashlib
import math
import sys

import bpy

from engine import hostiles, look, players, shots, stamp

FAILED = []


def ok(label, cond, detail=""):
    """Print one case; remember it when it failed."""
    if not cond:
        FAILED.append(label)
    print("%-4s %s%s" % ("OK" if cond else "FAIL", label, ("  [%s]" % detail) if detail else ""), flush=True)


def runs(frames):
    """'a-b' runs of a list of frames (for printing)."""
    out = []
    for f in sorted(frames):
        if out and f == out[-1][1] + 1:
            out[-1][1] = f
        else:
            out.append([f, f])
    return " ".join("%d-%d" % (a, b) if a != b else "%d" % a for a, b in out)


def build(variant=None):
    """A two-shot film with everything the module animates; `variant` changes one thing. Returns a dict."""
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    look.setup_render(scene, res=(540, 960), samples=16, threads=2, motion_blur=True)
    sun = bpy.data.objects.new("sun", bpy.data.lights.new("sun", "SUN"))
    scene.collection.objects.link(sun)
    film = shots.Film(scene, fps=24)
    s1 = film.shot("meadow", 0.0, 4.0)                   # frames 1-96
    s2 = film.shot("boom", 4.0, 6.0)                     # frames 97-144
    for s in (s1, s2):
        s.lens(35, 4.0)
        s.move((2.0, -8.0, 1.5), (2.0, 0.0, 1.0))
    cr = hostiles.make_creeper("cr")
    sk = hostiles.make_skeleton("sk")
    steve = players.make_player("steve", "steve")
    cr.place(1, (0.0, 0.0, 0.0), 0.0)
    sk.place(1, (4.0, 6.0, 0.0), math.pi)
    steve.place(1, (3.0, -1.0, 0.0), 0.0)
    cr.fuse(10, 60 if variant == "abort" else None)
    cr.hurt(30, attacker=sk)
    if variant != "nodeath":
        cr.die(40, camera=s1)
    release = 52 if variant == "release" else None
    sk.aim(4, steve)
    sk.shoot(20, steve, release=release, part="chest", knockback=0.1)
    if variant == "third":
        hostiles.hit(steve, 70, "back", hurt=False)
    hostiles.fire(sk, (1.0, 2.0, 0.0), 80)
    boom = hostiles.make_creeper("boom")
    boom.place(97, (-1.0, 4.0, 0.0), 0.0)
    end = boom.fuse(98)
    boom.explode(end, camera=s2, blocks=40, seed=1, latency=(variant == "latency"))
    film.finalize()
    if variant == "noshell":                             # the white shells forced hidden: only flash frames may change
        for obs in list(cr._shells.values()) + list(boom._shells.values()):
            for ob in obs:
                ob.animation_data_clear()
                ob.hide_render = ob.hide_viewport = True
    return dict(scene=scene, film=film, cr=cr, sk=sk, steve=steve, boom=boom, explodes=end)


def prints(b, frames, order=None):
    """{frame: objects part of the fingerprint} taken in `order` (default ascending)."""
    fp = stamp.Fingerprinter(b["scene"], b["film"])
    return {f: fp.frame(f)["parts"]["o"] for f in (order or frames)}


def main():
    digest = hashlib.sha1()
    base = build()
    frames = list(range(base["film"].frame_start, base["film"].frame_end + 1))
    a = prints(base, frames)
    r = prints(base, frames, order=list(reversed(frames)))
    m = prints(base, frames, order=frames[70:] + frames[:70])
    ok("fingerprints do not depend on the order they are taken in (%d frames, 3 orders)" % len(frames), a == r == m)
    for f in frames:
        digest.update(a[f].encode())
    cr, sk = base["cr"], base["sk"]
    white = [f for f in frames if cr.white_at(f) > 0.0] + [f for f in frames if base["boom"].white_at(f) > 0.0]
    bowf = {f: sk.bow_at(f) for f in frames}
    boom = base["explodes"]

    again = prints(build(), frames)
    ok("the same film built again: identical fingerprints", again == a, runs([f for f in frames if again[f] != a[f]]))

    ns = prints(build("noshell"), frames)
    changed = [f for f in frames if ns[f] != a[f]]
    ok("white shells hidden: exactly the white-flash frames change (%d)" % len(white), changed == sorted(white),
       "changed %s, white %s" % (runs(changed), runs(white)))

    ab = prints(build("abort"), frames)
    changed = [f for f in frames if ab[f] != a[f]]
    ok("fuse aborted on frame 60 (the creeper is dead from 40 on and gone on 64): no frame changes",
       changed == [], runs(changed))

    nd = prints(build("nodeath"), frames)
    changed = [f for f in frames if nd[f] != a[f]]
    ok("no death: the frames from the killing blow (40) on change, none before", changed and min(changed) == 40,
       runs(changed))

    rl = prints(build("release"), frames)
    b2 = build("release")
    bow2 = {f: b2["sk"].bow_at(f) for f in frames}
    changed = [f for f in frames if rl[f] != a[f]]
    ok("release 8 frames later (52 instead of 44): nothing before frame 44 changes, frame 44 does",
       changed and min(changed) == 44 and 44 in changed and bow2[44] != bowf[44], runs(changed))

    th = prints(build("third"), frames)
    changed = [f for f in frames if th[f] != a[f]]
    ok("a third arrow stuck in Steve on frame 70: exactly frames 70 to the end change (he is in both shots)",
       changed == list(range(70, frames[-1] + 1)), runs(changed))

    lt = prints(build("latency"), frames)
    changed = [f for f in frames if lt[f] != a[f]]
    ok("explode(latency=True), the game's empty tick: nothing before the explosion frame changes, it does",
       changed and min(changed) == boom, runs(changed))

    seq = [f for f in range(boom - 2, boom + 12)]
    distinct = len({a[f] for f in seq})
    ok("explosion: every frame from boom - 2 to boom + 11 has its own fingerprint", distinct == len(seq),
       "%d of %d" % (distinct, len(seq)))
    print("digest", digest.hexdigest())
    print("%d failed" % len(FAILED))
    return 1 if FAILED else 0


if __name__ == "__main__":
    sys.exit(main())
