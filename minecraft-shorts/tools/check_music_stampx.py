"""Checker probe for engine/music.py (independent checker): frame fingerprints of the probe film's night shots
(tools/check_music_probe.py) for the cases tools/check_music_stamp.py does not take: Jukebox.insert (the disc leaves
the hand, the first note), present() raising the arm, a note particle crossing a cut, the clap in beat 24.

    $BPY -m tools.check_music_stampx        (run twice: the digest must be equal)
"""
import hashlib
import sys

import bpy

from engine import stamp


def main():
    from tools import check_music_probe as pr

    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    b = pr.build(scene, "night")
    film, P = b["film"], b["players"]
    sh = {s.name: s for s in film.shots}
    fp = stamp.Fingerprinter(scene, film)
    got = {}

    def o(f):
        if f not in got:
            got[f] = fp.frame(f)["parts"]["o"]
        return got[f]

    s20 = sh["b20"]
    f0 = s20.frame_start
    ins = f0 + 44
    seq = [o(f) for f in range(f0, f0 + 8)]
    print("present() arm raise f%d..f%d: %d distinct of 8" % (f0, f0 + 7, len(set(seq))))
    scene.frame_set(ins + 1)
    held1 = P["steve"].holding_at("right", ins + 1)
    scene.frame_set(ins + 2)
    held2 = P["steve"].holding_at("right", ins + 2)
    print("insert at f%d: holding at +1 %r, at +2 %r" % (ins, held1, held2))
    print("insert: fingerprints f%d..f%d differ pairwise: %s" % (
        ins - 1, ins + 3, [o(f) != o(f + 1) for f in range(ins - 1, ins + 3)]))
    s24 = sh["b24"]
    c = s24.frame_start + 30
    print("b24 clap frames c-1, c, c+2: %s" % ([o(c - 1) != o(c), o(c) != o(c + 2)],))
    # a quiet stretch of b22 (nobody moves; the jukebox plays: notes every 24 frames)
    s22 = sh["b22"]
    q = [o(f) for f in range(s22.frame_start, s22.frame_start + 30)]
    print("b22 30 frames: %d distinct fingerprints" % len(set(q)))
    d = hashlib.sha1()
    for f in sorted(got):
        d.update(("%d:%s" % (f, got[f])).encode())
    print("digest %s (%d frames)" % (d.hexdigest(), len(got)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
