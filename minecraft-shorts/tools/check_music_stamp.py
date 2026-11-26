"""Checker: do render.py's frame fingerprints (engine.stamp) follow what engine.music animates?

    $BPY -m tools.check_music_stamp          (no rendering, about a minute; exit code 1 if a case fails)

Built with the proof shots of tools/music_proof.py at the final settings (motion blur on), once per sky. Every picture
change the module's calls make must change the fingerprint of the frames it changes: a note particle appearing ON its
spawn frame and gone after its 6 ticks, a jukebox note, the ejected disc appearing ON its eject tick (not before),
the dropped disc and the totem turning (every frame differs), the last lantern and its light appearing ON the frame
Alex places it, the applause (crouch frames differ from standing ones). A fingerprint must not depend on the order a
process takes frames in (CONTRACT.md: the animated-material trap; music.py animates no material). The last line is a
digest of every fingerprint taken: run the tool twice (two processes), the digests must be equal.
"""
import hashlib
import random
import sys

import bpy

from engine import stamp

FAILED = []


def ok(label, cond, detail=""):
    """Print one case; remember it when it failed."""
    if not cond:
        FAILED.append(label)
    print("%-4s %s%s" % ("OK" if cond else "FAIL", label, ("  [%s]" % detail) if detail else ""), flush=True)


def _orders(scene, film, taken):
    """The same frames in reverse and shuffled order, each in a fresh Fingerprinter: equal to `taken`?"""
    frames = sorted(taken)
    fp2 = stamp.Fingerprinter(scene, film)
    rev = {f: fp2.frame(f)["parts"]["o"] for f in reversed(frames)}
    random.seed(3)
    shuf = frames[:]
    random.shuffle(shuf)
    fp3 = stamp.Fingerprinter(scene, film)
    sh = {f: fp3.frame(f)["parts"]["o"] for f in shuf}
    return all(taken[f] == rev[f] == sh[f] for f in frames), len(frames)


def _sky(sky, names, digest):
    from tools import music_proof as mp

    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    built = mp.build(scene, sky, res=(540, 960), samples=16, threads=4, only=names)
    film, h, st = built["film"], built["h"], built["stage"]
    shots = {s.name: s for s in film.shots}
    fp = stamp.Fingerprinter(scene, film)
    taken = {}

    def take(frames):
        for f in frames:
            if f not in taken:
                taken[f] = fp.frame(f)["parts"]["o"]
        return [taken[f] for f in frames]

    def full(f):
        return fp.frame(f)["fp"]

    if sky == "gold":
        s = shots["notes_zuri"]
        f = s.frame_start + 1 + 2                    # tap on f0 + 1, its note one tick later: spawn f0 + 2.2 -> f0 + 3
        a, b = take([f - 1, f])
        ok("a tapped note block's note appears ON frame %d (one tick after the swing)" % f, a != b)
        end = f + 8                                  # gone ON spawn + 7 ticks: f0 + 11
        a, b, c = take([end - 2, end - 1, end])
        ok("the note rises (frames %d, %d differ) and is gone from frame %d" % (end - 2, end - 1, end),
           a != b and b != c)
        s = shots["b5"]
        lp = h["b5_place"]
        a, b = take([lp - 1, lp])
        ok("the last lantern (block and light) appears ON frame %d, where Alex places it" % lp, a != b)
        ll = st.cast.get("music_last_lantern")
        s = shots["totem"]
        fr = list(range(s.frame_start + 2, s.frame_start + 14))
        vals = take(fr)
        ok("the totem on the pedestal turns: every frame has its own fingerprint (%d frames)" % len(fr),
           len(set(vals)) == len(fr))
        del ll
    else:
        s = shots["jukebox"]
        f0 = s.frame_start
        item = h["jukebox_item"]
        born = int(round(item.born_at(item.land_frame)))
        a, b = take([born - 1, born])
        ok("the ejected disc appears ON its eject tick (frame %d), not before" % born, a != b)
        scene.frame_set(born - 1)
        hidden = all(ob.hide_render for ob in item.copies)
        ok("the disc item is not rendered on the frame before its eject", hidden)
        fr = list(range(item.land_frame + 2, item.land_frame + 12))
        vals = take(fr)
        ok("the disc lying on the jukebox bobs and turns: every frame differs (%d frames)" % len(fr),
           len(set(vals)) == len(fr))
        a, b = take([f0 + 23, f0 + 24])
        ok("the jukebox's second note appears ON frame %d (20 ticks after the first)" % (f0 + 24), a != b)
        s = shots["clap"]
        c0 = s.frame_start + 2                       # Zuri crouches ON c0, stands ON c0 + 2
        a, b, c = take([c0 - 1, c0, c0 + 2])
        ok("the applause: the crouch ON frame %d and the stand ON %d change the fingerprint" % (c0, c0 + 2),
           a != b and b != c)
        nxt = sorted(film.shots, key=lambda x: x.frame_start)
        ok("each proof shot has its own camera in the frame fingerprint",
           len({full(x.frame_start) for x in nxt}) == len(nxt))
    same, n = _orders(scene, film, taken)
    ok("%s: the fingerprints do not depend on the order they are taken in (%d frames, 3 orders)" % (sky, n), same)
    for f in sorted(taken):
        digest.update(("%s:%d:%s" % (sky, f, taken[f])).encode())


def main():
    digest = hashlib.sha1()
    _sky("gold", ["notes_zuri", "b5", "totem"], digest)
    _sky("night", ["jukebox", "clap"], digest)
    print("digest %s" % digest.hexdigest(), flush=True)
    print("%s (%d failed)" % ("ALL OK" if not FAILED else "FAILED", len(FAILED)))
    return 1 if FAILED else 0


if __name__ == "__main__":
    sys.exit(main())
