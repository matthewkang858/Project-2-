"""Proofs for films with several skies (render.py "Several skies in one film"), on films/_multisky_demo.py.

    $BPY -m tools.multisky_check inprocess     # is a SECOND build in one Blender process the same as a fresh process?
    $BPY -m tools.multisky_check inprocess oneword poppy_night bell      # ... for other films, built in turn, twice
    $BPY -m tools.multisky_check change        # the sky change inside a shot: camera path and motion blur
    $BPY -m tools.multisky_check cuts MP4      # frames either side of every sky cut, the change and the dip, from the mp4

inprocess   Builds gold, night and gold again in ONE process (render.Session three times) and, for 20 frames of each
            sky spread over the film, compares the scene fingerprint with the one a FRESH process gives; renders one
            frame per sky in both ways and compares the pixels. This is the evidence render.py's choice rests on
            (one process per sky); the result is printed, exit code 0 either way.
change      The demo's last shot changes sky at a frame F. Two proof films hold the same shot WITHOUT the change
            (films/_multisky_uncut_night.py, _multisky_uncut_gold.py). Renders F-2 .. F+1 of all three (each in the
            build of the frame's own sky) and checks: the demo's frames before F are pixel-identical to the uncut
            night shot's, the frames from F on to the uncut golden shot's; the camera's world matrix at the shutter's
            open, middle and close is the same in every build and moves on steadily across F. Writes the strip
            out/test/multisky_change.png (look at it). Exit code 1 if a check fails.
cuts        Decodes the frames either side of every sky boundary and through every dip from an encoded mp4 and
            writes out/test/multisky_cuts_<n>.png strips, with the mean brightness of the picture and of the
            caption band per frame (a dip darkens the picture, never the caption).

Every build happens in a process of its own (this tool starts itself again with `_work`), except the three builds
`inprocess` is about. Renders are previews: 360x640, 8 samples, 2 threads.
"""
import json
import os
import subprocess
import sys
import tempfile
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

FILM = "_multisky_demo"
UNCUT = "_multisky_uncut_%s"            # the same film without the sky change inside its last shot
RES, SAMPLES, THREADS = (360, 640), 8, 2
OUT = os.path.join(ROOT, "out", "test")


def _spread(frames, n):
    """n frames spread evenly over a list of frames."""
    if len(frames) <= n:
        return list(frames)
    return [frames[int((i + 0.5) * len(frames) / n)] for i in range(n)]


def _measure(ses, frames, render, out_dir, tag):
    """Fingerprints of `frames` and the rendered PNGs of `render` on a built Session."""
    ses.configure(RES, SAMPLES, THREADS, None)
    rec = {"sky": ses.sky, "fp": {}, "png": {}, "cam": {}}
    for f in frames:
        d = ses.fingerprint(f)
        rec["fp"][str(f)] = {"fp": d["fp"], "parts": d["parts"]}
    for f in render:
        path = os.path.join(out_dir, "%s_f%04d.png" % (tag, f))
        ses.render_frame(f, path)
        rec["png"][str(f)] = path
        cam, mats = ses.film.camera_at(f), []
        for sub in (0.0, 0.25, 0.5):                      # the shutter: open, middle, close
            ses.scene.frame_set(int(f), subframe=sub)
            mats.append([round(x, 6) for row in cam.matrix_world for x in row])
        ses.scene.frame_set(int(f))
        rec["cam"][str(f)] = {"name": cam.name, "mats": mats}
    return rec


def _work(argv):
    """Internal: one build in this process. argv = film sky out.json n_spread frame [frame ...]"""
    import render as R

    film, sky, out, n = argv[0], argv[1], argv[2], int(argv[3])
    render = [int(x) for x in argv[4:]]
    t = time.time()
    ses = R.Session(film, sky=sky or None)
    built = time.time() - t
    own = [f for f in range(ses.film.frame_start, ses.film.frame_end + 1) if ses.owns(f)]
    rec = _measure(ses, _spread(own, n), [f for f in render if ses.owns(f)], os.path.dirname(out),
                   "%s_%s_fresh" % (film, sky))
    rec["build_seconds"] = built
    rec["segments"] = ses.segments
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(rec, fh)
    return 0


def _fresh(film, sky, tmp, n, render):
    """Run _work in a fresh process and return its record."""
    out = os.path.join(tmp, "%s_%s.json" % (film, sky))
    cmd = [sys.executable, "-m", "tools.multisky_check", "_work", film, sky, out, str(n)] + [str(f) for f in render]
    subprocess.check_call(cmd, cwd=ROOT, stdout=subprocess.DEVNULL)
    with open(out, encoding="utf-8") as fh:
        return json.load(fh)


def _pixels(a, b):
    """(identical?, largest channel difference, share of differing pixels) of two PNG files."""
    import numpy as np
    from PIL import Image

    x = np.asarray(Image.open(a).convert("RGB")).astype(np.int16)
    y = np.asarray(Image.open(b).convert("RGB")).astype(np.int16)
    if x.shape != y.shape:
        return False, 255, 1.0
    d = np.abs(x - y)
    return bool(d.max() == 0), int(d.max()), float((d.max(axis=2) > 0).mean())


def _cleanup(tmp):
    """Remove a temporary directory this tool made (its files, then itself)."""
    for fn in os.listdir(tmp):
        os.remove(os.path.join(tmp, fn))
    os.rmdir(tmp)


def inprocess(films=()):
    """Second builds in one process against fresh processes (see the module docstring). films: other film modules
    to build one after the other, twice round, instead of the demo's gold, night, gold. Returns 0."""
    tmp = tempfile.mkdtemp(prefix="multisky_inprocess_", dir=OUT)
    try:
        return _inprocess(films, tmp)
    finally:
        _cleanup(tmp)


def _inprocess(films, tmp):
    import render as R

    t0 = time.time()
    if films:
        jobs = [(f, "") for f in films] * 2
        probe = {}
    else:
        jobs = [(FILM, "gold"), (FILM, "night"), (FILM, "gold")]
        probe = {(FILM, "gold"): 30, (FILM, "night"): 60}     # the rendered frame (both have the farmer in them)
    fresh = {}
    for job in jobs:
        if job not in fresh:
            if job not in probe:                              # a first pass to learn a frame in the middle of the film
                first = _fresh(job[0], job[1], tmp, 20, [])
                probe[job] = sorted(int(k) for k in first["fp"])[10]
            fresh[job] = _fresh(job[0], job[1], tmp, 20, [probe[job]])
            print("[inprocess] fresh process: %s%s built in %.1f s, %d frames fingerprinted, frame %d rendered"
                  % (job[0], " [%s]" % job[1] if job[1] else "", fresh[job]["build_seconds"], len(fresh[job]["fp"]),
                     probe[job]), flush=True)
    bad = 0
    for n, job in enumerate(jobs, 1):
        film, sky = job
        t = time.time()
        ses = R.Session(film, sky=sky or None)
        built = time.time() - t
        frames = [int(k) for k in fresh[job]["fp"]]
        rec = _measure(ses, frames, [probe[job]], tmp, "%s_%s_build%d" % (film, sky, n))
        diff = [f for f in frames if rec["fp"][str(f)]["fp"] != fresh[job]["fp"][str(f)]["fp"]]
        parts = sorted({p for f in diff for p in "gcol"
                        if rec["fp"][str(f)]["parts"][p] != fresh[job]["fp"][str(f)]["parts"][p]})
        same, worst, share = _pixels(rec["png"][str(probe[job])], fresh[job]["png"][str(probe[job])])
        bad += bool(diff) or not same
        print("[inprocess] build %d in this process (%s%s, %.1f s): %d of %d fingerprints equal to the fresh process's%s; "
              "frame %d rendered: %s"
              % (n, film, " [%s]" % sky if sky else "", built, len(frames) - len(diff), len(frames),
                 " (differing parts: %s; frames %s)" % ("".join(parts), R._ranges(diff)) if diff else "",
                 probe[job], "pixel-identical" if same else
                 "DIFFERENT (largest channel difference %d, %.2f %% of the pixels)" % (worst, 100 * share)), flush=True)
    print("[inprocess] %s (%.0f s)" % (
        "every build in this one process gave the fresh process's fingerprints and pixels" if not bad else
        "%d of %d builds in this one process are NOT the same as a fresh process" % (bad, len(jobs)), time.time() - t0))
    return 0


def change():
    """The sky change inside the demo's last shot (see the module docstring). Returns the number of failed checks."""
    tmp = tempfile.mkdtemp(prefix="multisky_change_", dir=OUT)
    try:
        return _change(tmp)
    finally:
        _cleanup(tmp)


def _change(tmp):
    import numpy as np
    from PIL import Image

    # where the change is: ask a fresh build (any sky) for the table
    demo = {"gold": _fresh(FILM, "gold", tmp, 1, [])}
    segs = demo["gold"]["segments"]
    F = segs[-1][0]                                           # first frame of the last (golden) segment
    assert segs[-2][2] == "night" and segs[-1][2] == "gold", segs
    frames = [F - 2, F - 1, F, F + 1]
    recs = {}
    for film, sky in ((FILM, "night"), (FILM, "gold"), (UNCUT % "night", "night"), (UNCUT % "gold", "gold")):
        recs[(film, sky)] = _fresh(film, sky, tmp, 1, frames)
    fails = 0

    def check(ok, text):
        nonlocal fails
        fails += not ok
        print("%-4s %s" % ("OK" if ok else "FAIL", text))

    check(sorted(recs[(FILM, "night")]["png"]) == [str(F - 2), str(F - 1)] and
          sorted(recs[(FILM, "gold")]["png"]) == [str(F), str(F + 1)],
          "the demo changes sky at frame %d: its night build owns %d and %d, its golden build %d and %d"
          % (F, F - 2, F - 1, F, F + 1))
    for f in frames:
        sky = "night" if f < F else "gold"
        same, worst, share = _pixels(recs[(FILM, sky)]["png"][str(f)], recs[(UNCUT % sky, sky)]["png"][str(f)])
        check(same, "frame %d of the demo (%s) is pixel-identical to frame %d of the same shot WITHOUT a sky change (%s)%s"
              % (f, sky, f, sky, "" if same else ": largest difference %d, %.2f %% of the pixels" % (worst, 100 * share)))
    # the camera: one object, the same world matrix in every build, moving on steadily across the change
    cams = {}
    for key, rec in recs.items():
        for f, c in rec["cam"].items():
            cams.setdefault(int(f), []).append((key, c))
    names = {c["name"] for v in cams.values() for _k, c in v}
    check(len(names) == 1, "one camera films all four frames in every build: %s" % sorted(names))
    worst = 0.0
    for f, lst in cams.items():
        ref = np.array(lst[0][1]["mats"])
        for _key, c in lst[1:]:
            worst = max(worst, float(np.abs(np.array(c["mats"]) - ref).max()))
    check(worst < 1e-6, "its world matrix at shutter open / middle / close is the same in the night build, the golden "
          "build and both uncut films (largest difference %.1e)" % worst)
    pos = {f: np.array(lst[0][1]["mats"])[:, [3, 7, 11]] for f, lst in cams.items()}       # translation at 3 sub-times
    steps = [float(np.linalg.norm(pos[b][0] - pos[a][0])) for a, b in zip(frames, frames[1:])]
    blur = [float(np.linalg.norm(pos[f][2] - pos[f][0])) for f in frames]
    check(max(steps) - min(steps) < 0.25 * max(steps) + 1e-4,
          "the camera moves %s blocks from frame to frame (%d>%d, %d>%d, %d>%d): no jump across the change"
          % (", ".join("%.4f" % s for s in steps), frames[0], frames[1], frames[1], frames[2], frames[2], frames[3]))
    check(all(abs(b - 0.5 * s) < 0.2 * s + 1e-4 for b, s in zip(blur, steps + steps[-1:])),
          "during each frame's exposure (half a frame) it moves %s blocks: half a step, as in any uncut shot"
          % ", ".join("%.4f" % b for b in blur))
    # the strip to look at: F-2, F-1 (night) | F, F+1 (gold), and the walker's region enlarged underneath
    ims = [Image.open(recs[(FILM, "night" if f < F else "gold")]["png"][str(f)]).convert("RGB") for f in frames]
    w, h = ims[0].size
    box = (int(w * 0.25), int(h * 0.55), int(w * 0.75), int(h * 0.95))
    zoom = [im.crop(box).resize((w, int(w * (box[3] - box[1]) / (box[2] - box[0]))), Image.LANCZOS) for im in ims]
    sheet = Image.new("RGB", (4 * w + 18, h + 6 + zoom[0].size[1]), (20, 20, 24))
    for i, (im, z) in enumerate(zip(ims, zoom)):
        sheet.paste(im, (i * (w + 6), 0))
        sheet.paste(z, (i * (w + 6), h + 6))
    path = os.path.join(OUT, "multisky_change.png")
    sheet.save(path)
    print("[change] frames %s (night, night | gold, gold) and their lower middle enlarged -> %s" % (frames, path))
    return fails


def cuts(mp4, film=FILM, res=RES, samples=SAMPLES):
    """Strips of the frames around every sky boundary and every dip of an encoded film (see the module docstring)."""
    import numpy as np
    from PIL import Image

    import render as R
    from engine import captions as cap
    from engine import post

    variant = R.variant_of(res, samples, 1)
    meta = post.read_meta(film, variant)
    tl = R.Timeline(meta)
    raw = subprocess.check_output(["ffmpeg", "-v", "error", "-i", mp4, "-map", "0:v:0", "-vf", "scale=270:480",
                                   "-f", "rawvideo", "-pix_fmt", "rgb24", "-"])
    video = np.frombuffer(raw, dtype=np.uint8).reshape(-1, 480, 270, 3)
    print("[cuts] %s: %d frames decoded; skies: %s" % (mp4, len(video), tl.describe()))
    spots = []
    for (a, b, sky), (a2, _b2, sky2) in zip(tl.segments, tl.segments[1:]):
        inside = tl.shots and any(s.frame_start < a2 <= s.frame_end for s in tl.shots)
        spots.append(("%s -> %s at frame %d%s" % (sky, sky2, a2, " (INSIDE a shot)" if inside else " (a cut)"),
                      [a2 - 2, a2 - 1, a2, a2 + 1]))
    fades = post.check_fades(meta.get("fades"))
    if fades:
        fs = [f for f in range(tl.frame_start, tl.frame_end + 1) if post.fade_gain(fades, tl.seconds(f)) < 1.0]
        spots.append(("dip to black, frames %s" % R._ranges(fs), [fs[0] - 1] + fs + [fs[-1] + 1]))
    band = slice(int(480 * cap.CAPTION_BAND[0]), int(480 * cap.CAPTION_BAND[1]))
    paths = []
    for n, (label, frames) in enumerate(spots, 1):
        frames = [f for f in frames if tl.frame_start <= f <= tl.frame_end]
        strip = Image.new("RGB", (len(frames) * 276 - 6, 480), (20, 20, 24))
        notes = []
        for i, f in enumerate(frames):
            pic = video[f - tl.frame_start]
            strip.paste(Image.fromarray(pic), (i * 276, 0))
            gain = post.fade_gain(fades, tl.seconds(f))
            word = cap.caption_at(tl.captions, tl.seconds(f))
            notes.append("%d[%s%s] picture %.0f, caption band max %d%s"
                         % (f, tl.sky_of(f), "" if gain >= 1 else " gain %.2f" % gain, pic[:200].mean(),
                            pic[band].max(), " (%r)" % word if word else ""))
        path = os.path.join(OUT, "multisky_cuts_%d.png" % n)
        strip.save(path)
        paths.append(path)
        print("[cuts] %d. %s -> %s\n         %s" % (n, label, path, "\n         ".join(notes)))
    return 0


if __name__ == "__main__":
    what = sys.argv[1] if len(sys.argv) > 1 else ""
    if what == "_work":
        sys.exit(_work(sys.argv[2:]))
    if what == "inprocess":
        sys.exit(inprocess(sys.argv[2:]))
    if what == "change":
        sys.exit(1 if change() else 0)
    if what == "cuts" and len(sys.argv) > 2:
        sys.exit(cuts(sys.argv[2]))
    print(__doc__)
    sys.exit(2)
