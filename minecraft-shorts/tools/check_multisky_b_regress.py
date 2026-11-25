"""Checker B, read-only: judge every final frame of a finished film against the film as it builds NOW.

    $BPY -m tools.check_multisky_b_regress <film> [variant]

Builds the film through render.Session (one sky: build(scene)), opens the frame directory's book (render.Stamps)
and prints the status of every frame. NOTHING is written: no Stamps.save(), no render, no restamp. Also compares
each stored stamp's 'fp' with the fingerprint of the current build directly (independent of Stamps._judge).
"""
import collections
import json
import sys
import time


def main(argv):
    """Judge a film's frames read-only; exit code 1 if any frame's scene fingerprint changed."""
    import render as R
    from engine import post

    name = argv[0]
    variant = argv[1] if len(argv) > 1 else None
    t = time.time()
    ses = R.Session(name)
    build_s = time.time() - t
    meta = post.read_meta(name, variant) or {}
    if variant:
        w, h = (int(x) for x in variant.split("_")[0].split("x"))
        samples = int(variant.split("_")[1].replace("spp", ""))
        ses.configure((w, h), samples, R.FINAL_THREADS, None)
    else:
        ses.configure(None, None, R.FINAL_THREADS, None)        # what render.py does before --frames
    book = R.Stamps(ses, name, variant)
    t = time.time()
    frames = list(range(ses.film.frame_start, ses.film.frame_end + 1))
    states = collections.Counter()
    bad = []
    direct_diff = []
    for f in frames:
        st = book.status(f)
        states[st] += 1
        if st in ("scene", "engine+scene"):
            bad.append(f)
        rec = (meta.get("frames") or {}).get(str(f))
        if rec is not None and rec.get("fp") != ses.fingerprint(f)["fp"]:
            direct_diff.append(f)
    judge_s = time.time() - t
    out = {"film": name, "variant": variant, "sky": ses.sky, "skies": bool(ses.skies), "frames": len(frames),
           "meta_range": [meta.get("frame_start"), meta.get("frame_end")],
           "film_range": [ses.film.frame_start, ses.film.frame_end],
           "on_disk": len(book.on_disk), "status": dict(states), "scene_changed": R._ranges(bad),
           "fp_differs_direct": R._ranges(direct_diff), "settings_key": book.s,
           "meta_has_fades": "fades" in meta, "session_fades": ses.fades,
           "captions_equal_meta": [list(c) for c in ses.captions] == meta.get("captions"),
           "shots_equal_meta": [{"name": s.name, "frame_start": s.frame_start, "frame_end": s.frame_end}
                                for s in ses.film.shots] == meta.get("shots"),
           "new_meta_keys": sorted(set(ses.meta()) - set(meta)), "build_s": round(build_s, 2),
           "judge_s": round(judge_s, 2), "ms_per_frame": round(1000.0 * judge_s / max(1, len(frames)), 1)}
    print("CHECK_B_REGRESS " + json.dumps(out))
    return 1 if (bad or direct_diff) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
