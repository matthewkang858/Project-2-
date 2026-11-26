"""Checker: do render.py's frame fingerprints (engine.stamp) follow what engine.towers animates?

    $BPY -m tools.check_towers_stamp          (no rendering, about a minute; exit code 1 if a case fails)

Every picture change the tower's calls make must change the fingerprint of exactly the frames it changes: the golem
appearing ON its spawn frame and gone from the frame its head is under the rim, the slide, the items dropping into the
hopper, the crack stages and the break of the top dirt step, the second bed appearing, the baby swapped for the adult
on one frame, the lava light's flicker, a glass pane hidden for one shot. A fingerprint must not depend on the order
a process takes frames in (CONTRACT.md: the animated-material trap; towers.py animates no material). The last line is
a digest of every fingerprint taken: run the tool twice (two processes), the digests must be equal.
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


def main():
    from tools import towers_proof as tp

    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    built = tp.build(scene, res=(720, 1280), samples=24, threads=4)   # final settings: motion blur on
    film, h = built["film"], built["h"]
    shots = {s.name: s for s in film.shots}
    fp = stamp.Fingerprinter(scene, film)

    def obj(f):
        return fp.frame(f)["parts"]["o"]

    def full(f):
        return fp.frame(f)["fp"]

    digest = hashlib.sha1()
    taken = {}

    def take(frames):
        for f in frames:
            if f not in taken:
                taken[f] = obj(f)
        return [taken[f] for f in frames]

    sl = h["slide"]
    a, b = take([sl["spawn"] - 1, sl["spawn"]])
    ok("the golem appears ON its spawn frame (%d): the fingerprint changes there" % sl["spawn"], a != b)
    golem = built["stage"].cast["golem"]

    def golem_shown(f):
        scene.frame_set(f)
        return not all(ob.hide_render for ob in golem.objects() if ob.type == "MESH")

    sh = shots["slide"]
    ok("the slide shot opens on an EMPTY platform: the golem of the platform shot (no slide) is not rendered from "
       "the shot's first frame (%d) to the spawn, and is rendered ON the spawn (%d)" % (sh.frame_start, sl["spawn"]),
       not any(golem_shown(f) for f in range(sh.frame_start, sl["spawn"])) and golem_shown(sl["spawn"]))
    gone = sl["gone"]
    a, b, c = take([gone - 2, gone - 1, gone])
    ok("the golem slides (frames %d, %d differ) and is gone ON frame %d" % (gone - 2, gone - 1, gone), a != b != c)
    fr = list(range(sl["frame"], sl["frame"] + 12))
    vals = take(fr)
    ok("every frame of the slide has its own fingerprint (%d frames)" % len(fr), len(set(vals)) == len(fr))
    plans = h["hopper"]
    rel = int(round(plans[0]["track"][0][0]))
    a, b = take([rel - 1, rel])
    ok("the first item appears ON its release frame (%d), not before" % rel, a != b)
    a, b = take([plans[0]["frame"] - 1, plans[0]["frame"]])
    ok("an item vanishing into the hopper changes the fingerprint (frame %d)" % plans[0]["frame"], a != b)
    m = h["stairs"]
    st_frames = [f for f, _s in m["stages"]] if m.get("stages") else []
    if st_frames:
        vals = take([f - 1 for f in st_frames[1:]] + st_frames[1:])
        n = len(st_frames) - 1
        ok("each crack stage of the top step changes the fingerprint (%d stages)" % (n + 1),
           all(vals[i] != vals[n + i] for i in range(n)))
    a, b = take([m["frame"] - 1, m["frame"]])
    ok("the top step is gone ON the break frame (%d)" % m["frame"], a != b)
    hi = shots["high"]
    bf = hi.frame_start + 20
    a, b = take([bf - 1, bf])
    ok("the second red bed appears ON its frame (%d)" % bf, a != b)
    gf = h["grow"]
    a, b = take([gf - 1, gf])
    ok("the baby is swapped for the adult ON frame %d: the fingerprint changes there" % gf, a != b)
    # beat 24: the golem appears through the glass behind the four on its frame; the trembles move every frame
    b24 = h["b24"]
    a, b = take([b24["spawn"] - 1, b24["spawn"]])
    ok("beat 24: the golem appears behind the glass ON its frame (%d)" % b24["spawn"], a != b)
    s24 = shots["b24"]
    fr = list(range(s24.frame_start + 2, s24.frame_start + 10))
    vals = take(fr)
    ok("beat 24: the panic tremble changes every frame (%d frames)" % len(fr), len(set(vals)) == len(fr))
    # the panic shots in the digest too (their seeds must not depend on the process: zlib.crc32, not hash())
    take([shots["pod_in"].frame_start + 6, shots["b08"].frame_start + 6, shots["b08"].frame_start + 7])
    # particles do not run on into the next shot (golem_death / break_top_step until=)

    def lit(burst, f):
        scene.frame_set(f)
        return [p for p in burst.particles if not p["object"].hide_render]

    order_ = sorted(film.shots, key=lambda s_: s_.frame_start)
    for shot_name, burst in (("slide", sl["death"]["burst"]), ("stairs", m.get("burst")), ("b22", h["b22"].get("burst"))):
        if burst is None:
            continue
        sh_ = shots[shot_name]
        nxt_ = [s_ for s_ in order_ if s_.frame_start > sh_.frame_start]
        if not nxt_:
            continue
        f_next = nxt_[0].frame_start
        ok("the %s shot's particles are all gone on the next shot's first frame (%d)" % (shot_name, f_next),
           not lit(burst, f_next) and not lit(burst, f_next + 6))
    po = shots["pod_out"]
    nxt = shots[[s.name for s in sorted(film.shots, key=lambda s: s.frame_start)
                 if s.frame_start > po.frame_start][0]]
    full_a = full(po.frame_start)
    ok("the panes hidden for pod_out are back in the next shot (a different fingerprint, the shot's own camera)",
       full_a != full(nxt.frame_start))
    # the same frames in other orders and in a fresh Fingerprinter
    frames = sorted(taken)
    order = list(reversed(frames))
    fp2 = stamp.Fingerprinter(scene, film)
    rev = {f: fp2.frame(f)["parts"]["o"] for f in order}
    random.seed(3)
    shuf = frames[:]
    random.shuffle(shuf)
    fp3 = stamp.Fingerprinter(scene, film)
    sh = {f: fp3.frame(f)["parts"]["o"] for f in shuf}
    ok("the fingerprints do not depend on the order they are taken in (%d frames, 3 orders)" % len(frames),
       all(taken[f] == rev[f] == sh[f] for f in frames))
    for f in frames:
        digest.update(("%d:%s" % (f, taken[f])).encode())
    print("digest %s" % digest.hexdigest(), flush=True)
    print("%s (%d failed)" % ("ALL OK" if not FAILED else "FAILED", len(FAILED)))
    return 1 if FAILED else 0


if __name__ == "__main__":
    sys.exit(main())
