"""Self-test of render.py on a film with several skies: every flag, every exit code, the words the render loop waits
for, and the wrong-sky lock. Drives the real command line on films/_multisky_demo.py at thumbnail size.

    $BPY -m tools.multisky_selftest              # all parts (about 4 minutes on a busy machine: run the parts)
    $BPY -m tools.multisky_selftest chunks       # a chunked render to the end; "0 to render" only when it IS the end
    $BPY -m tools.multisky_selftest engine       # exit code 3 across skies, --restamp, --rerender-stale
    $BPY -m tools.multisky_selftest stale        # --prune-stale, a re-tagged shot's frame, --force, a wrong guess
    $BPY -m tools.multisky_selftest lock         # the wrong-sky lock: SkyError from Session and Stamps
    $BPY -m tools.multisky_selftest encode       # --encode --allow-holds, --sheet, --still, --save-blend

Frames go to the preview variant 180x320_4spp_step8 of the demo (26 frames: 16 golden, 10 night; 11 more of the
last shot) and nowhere else; 'engine', 'stale' and 'encode' need the frames 'chunks' renders (they run it first when frames are missing).
Engine edits are SIMULATED by rewriting stamps in that variant's meta.json (no engine file is touched), exactly as
tools/contract_check.py does for a film with one sky. Prints one line per check; exit code = number of failures.
"""
import json
import os
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

FILM = "_multisky_demo"
SMALL = ["--step", "8", "--res", "180x320", "--samples", "4", "--threads", "2"]
VARIANT = "180x320_4spp_step8"
DIR = os.path.join(ROOT, "out", "preview", FILM, VARIANT)
META = os.path.join(DIR, "meta.json")
DONE = " 0 to render"                         # what the render loop waits for
RESULTS = []


def check(ok, text):
    """Record and print one check."""
    RESULTS.append((bool(ok), text))
    print("%-4s %s" % ("OK" if ok else "FAIL", text), flush=True)
    return bool(ok)


def run(args, film=FILM):
    """`render <film> args`: (exit code, output, seconds)."""
    t = time.time()
    p = subprocess.run([sys.executable, "-W", "ignore", "-m", "render", film] + args, cwd=ROOT,
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    return p.returncode, p.stdout, time.time() - t


def lines(out, *needles):
    """The [render] lines of an output that contain every needle."""
    return [ln for ln in out.splitlines() if ln.startswith("[render]") and all(n in ln for n in needles)]


def meta():
    with open(META, encoding="utf-8") as fh:
        return json.load(fh)


def rewrite(fn):
    """Change the variant's meta.json in place (a simulated engine edit / re-tag); returns what fn returns."""
    m = meta()
    out = fn(m)
    with open(META, "w", encoding="utf-8") as fh:
        json.dump(m, fh, indent=1)
    return out


def sky_of(m, f):
    return next(s for a, b, s in m["sky_segments"] if a <= f <= b)


def mtimes():
    return {n: os.stat(os.path.join(DIR, n)).st_mtime_ns for n in sorted(os.listdir(DIR)) if n.endswith(".png")}


def builds(out):
    """Skies built in an output, in order."""
    return [ln.split("[sky ")[1].split("]")[0] for ln in out.splitlines() if "[render] built" in ln and "[sky " in ln]


def part_chunks(fresh=True):
    """A chunked render from nothing to the end."""
    if fresh and os.path.isdir(DIR):
        for n in sorted(os.listdir(DIR)):                      # this test's own variant directory, file by file
            os.remove(os.path.join(DIR, n))
    calls, said_early, outs = 0, False, []
    while calls < 12:
        code, out, secs = run(["--frames", "all", "--max-seconds", "9"] + SMALL)
        calls += 1
        outs.append(out)
        if code != 0:
            return check(False, "chunk %d ended with exit code %d:\n%s" % (calls, code, out[-1500:]))
        if DONE in out:
            break
        said_early = said_early or any(DONE in ln for ln in out.splitlines())
    m = meta()
    n_png = len(mtimes())
    check(DONE in outs[-1] and not said_early and calls >= 3,
          "a chunked render (--max-seconds 9) needed %d calls; only the last one said '%s'" % (calls, DONE.strip()))
    check(n_png == 26 and len(m["frames"]) == 26 and all(rec.get("sky") == sky_of(m, int(f)) for f, rec in m["frames"].items()),
          "26 frames in ONE directory (%s), every stamp records the sky of its frame (%d golden, %d night)"
          % (os.path.relpath(DIR, ROOT), sum(r["sky"] == "gold" for r in m["frames"].values()),
             sum(r["sky"] == "night" for r in m["frames"].values())))
    first = builds(outs[0])
    check(first == ["gold"], "the first call built the film's first sky only (%s) and stopped on time" % first)
    two = [builds(o) for o in outs if len(builds(o)) == 2]
    check(len(two) <= 1 and all(len(builds(o)) <= 2 for o in outs),
          "skies built per call: %s (two only in the call in which the first sky ran out of frames)" % [builds(o) for o in outs])
    per_sky = lines("\n".join(outs), "sky '", "frames requested")
    check(per_sky and not any(DONE in ln for ln in per_sky), "no per-sky line says '%s' (%d such lines, e.g. %r)"
          % (DONE.strip(), len(per_sky), per_sky[-1][9:]))
    # the call after the end: nothing is built, and it is fast
    code, out, secs = run(["--frames", "all", "--max-seconds", "9"] + SMALL)
    check(code == 0 and DONE in out and not builds(out) and "built" not in out,
          "the call after the last frame builds nothing and says %r (%.1f s)" % (lines(out, "frames:")[-1][9:], secs))
    # one shot by name: a shot with a sky change inside is split between its two skies (with --step 8 these are the
    # frames 126, 134 ... 206: counted from the shot's first frame, so eleven other frames than --frames all gave)
    code, out, secs = run(["--frames", "street"] + SMALL)
    m = meta()
    mine = [str(f) for f in range(126, 207, 8)]
    check(code == 0 and DONE in out and "11 requested" in out and sorted(builds(out)) == ["gold", "night"]
          and [m["frames"][f]["sky"] for f in mine] == ["night"] * 5 + ["gold"] * 6,
          "--frames street (a shot with a sky change inside): 5 frames from the night build, 6 from the golden one: %r"
          % lines(out, "frames:")[-1][9:])
    code, out, secs = run(["--frames", "street"] + SMALL)
    check(code == 0 and DONE in out and not builds(out), "... and again: nothing built, %r" % lines(out, "frames:")[-1][9:95])
    return True


def need_frames():
    if not os.path.exists(META) or len(mtimes()) < 26 or DONE not in run(["--frames", "all"] + SMALL)[1]:
        part_chunks(fresh=False)


def part_engine():
    """Frames rendered with other engine sources: exit code 3 before ANY sky renders; --restamp; --rerender-stale."""
    need_frames()

    def tamper(m):
        # a golden frame (17) and a night frame (57) as if rendered with other engine sources, scene unchanged;
        # a night frame (137) with other engine sources AND another scene; a golden frame (201) deleted
        old_e = "0" * 12
        m["engines"][old_e] = dict(m["engines"][m["current"]["e"]], **{"engine/look.py": "000000000000"})
        for f in ("17", "57", "137"):
            m["frames"][f]["e"] = old_e
        m["frames"]["137"]["fp"] = "f" * 16
        m["frames"]["137"]["parts"]["c"] = "f" * 16
    rewrite(tamper)
    os.remove(os.path.join(DIR, "f_0201.png"))
    before = mtimes()
    code, out, _ = run(["--frames", "all"] + SMALL)
    stopped = lines(out, "STOPPED")
    check(code == 3 and mtimes() == before and DONE not in out and "f_0201.png" not in mtimes(),
          "exit code 3, nothing rendered in any sky (the missing golden frame 201 was NOT rendered), no '%s'" % DONE.strip())
    check(any("sky 'gold': STOPPED" in ln for ln in stopped) and any("sky 'night': STOPPED" in ln for ln in stopped)
          and "engine/look.py" in out and builds(out) == ["gold", "night"],
          "both skies were built and report their own frames: %s" % [ln[9:95] for ln in stopped])
    check(len(lines(out, "show an unchanged scene (17)")) == 1 and len(lines(out, "show an unchanged scene (57)")) == 1
          and len(lines(out, "have a changed scene (137", "camera")) == 1,
          "gold: 17 unchanged; night: 57 unchanged, 137 changed (camera)")
    code, out, _ = run(["--restamp", "all"] + SMALL)
    check(code == 0 and len(lines(out, "sky 'gold': restamp", "1 frames re-stamped", "(17)")) == 1
          and len(lines(out, "sky 'night': restamp", "1 frames re-stamped", "(57)", "1 NOT accepted", "(137)")) == 1,
          "--restamp all: each sky re-stamps its own unchanged frame (17, 57) and refuses 137")
    code, out, _ = run(["--frames", "all"] + SMALL)
    check(code == 3 and mtimes() == before and len(lines(out, "sky 'gold': STOPPED", "another sky")) == 1,
          "still exit code 3: the golden sky is stopped by the NIGHT frame 137 (%r)"
          % (lines(out, "sky 'gold': STOPPED") or [""])[0][9:120])
    code, out, _ = run(["--frames", "all", "--rerender-stale"] + SMALL)
    after = mtimes()
    changed = sorted(n for n in after if after[n] != before.get(n))
    check(code == 0 and changed == ["f_0137.png", "f_0201.png"] and DONE in out and "2 rendered in this run" in out,
          "--rerender-stale renders exactly 137 (night) and 201 (gold): %r" % lines(out, "frames:")[-1][9:])
    m = meta()
    check(all(r["e"] == m["current"]["e"] for r in m["frames"].values()), "every stamp carries the current engine again")


def part_stale():
    """--prune-stale, a frame rendered under another sky than its shot now has, --force, a wrong guess of the sky."""
    need_frames()
    rewrite(lambda m: m["frames"]["145"].__setitem__("fp", "e" * 16))        # a night frame whose scene "changed"
    open(os.path.join(DIR, "f_0999.png"), "wb").write(open(os.path.join(DIR, "f_0001.png"), "rb").read())
    before = mtimes()
    code, out, _ = run(["--prune-stale"] + SMALL)
    after = mtimes()
    check(code == 0 and sorted(set(before) - set(after)) == ["f_0145.png", "f_0999.png"]
          and len(lines(out, "sky 'night': prune", "(145)")) == 1,
          "--prune-stale deletes the stale night frame 145 and the PNG beyond the film (999), nothing else")
    code, out, _ = run(["--frames", "all"] + SMALL)
    check(code == 0 and builds(out) == ["night"] and "1 rendered in this run" in out and DONE in out,
          "the next --frames builds the night sky only and renders that one frame: %r" % lines(out, "frames:")[-1][9:])
    # a golden frame whose stamp says it was rendered under the night sky (the shot was re-tagged since)
    rewrite(lambda m: m["frames"]["25"].__setitem__("sky", "night"))
    code, out, _ = run(["--restamp", "25", "--restamp-changed"] + SMALL)
    check(code == 0 and len(lines(out, "0 frames re-stamped", "1 NOT accepted")) == 1,
          "a PNG rendered under another sky is not accepted even by --restamp-changed")
    before = mtimes()
    code, out, _ = run(["--frames", "all"] + SMALL)
    after = mtimes()
    check(code == 0 and [n for n in after if after[n] != before[n]] == ["f_0025.png"] and builds(out) == ["gold"],
          "... it is rendered again, in its own sky's build (gold), and nothing else is")
    before = mtimes()
    code, out, _ = run(["--frames", "41-49", "--force"] + SMALL)
    after = mtimes()
    check(code == 0 and sorted(n for n in after if after[n] != before[n]) == ["f_0041.png", "f_0049.png"]
          and builds(out) == ["gold", "night"],
          "--frames 41-49 --force (a range across the sky cut at 43): 41 in the golden build, 49 in the night build")
    # a stale table that points at the wrong sky: the build corrects the guess, the picture is never wrong.
    # (On the proof film _multisky_uncut_gold, which has no other meta.json a right table could be read from.)
    other = "_multisky_uncut_gold"
    odir = os.path.join(ROOT, "out", "preview", other, VARIANT)
    code, out, _ = run(["--frames", "1"] + SMALL, film=other)
    ometa = os.path.join(odir, "meta.json")
    ok = code == 0 and os.path.exists(ometa)
    if ok:
        with open(ometa, encoding="utf-8") as fh:
            m = json.load(fh)
        m["source_hash"] = "stale"                                              # "a source changed since" ...
        m["sky_segments"] = [[1, 206, "night"]]                                 # ... and the old table is wrong
        with open(ometa, "w", encoding="utf-8") as fh:
            json.dump(m, fh, indent=1)
        path = os.path.join(ROOT, "out", "test", other + "_0.5.png")
        if os.path.exists(path):
            os.remove(path)
        code, out, _ = run(["--still", "0.5", "--res", "180x320", "--samples", "4", "--step", "8"], film=other)
        ok = code == 0 and builds(out) == ["night", "gold"] and os.path.exists(path) and "sky gold" in out
        for n in (path, os.path.join(odir, "f_0001.png"), ometa):
            if os.path.exists(n):
                os.remove(n)
        os.rmdir(odir)
        if not os.listdir(os.path.dirname(odir)):
            os.rmdir(os.path.dirname(odir))
    check(ok, "--still 0.5 with a WRONG guess (the last build's table says night): night is built, finds the frame is "
              "not its own, gold renders it (builds: %s)" % builds(out))
    code, out, _ = run(["--frames", "all"] + SMALL)
    check(code == 0 and DONE in out and not builds(out), "the demo's frames are all still valid afterwards, nothing built")


def part_lock():
    """The wrong-sky lock itself, inside one build: Session and Stamps refuse every frame of another sky."""
    code = r'''
import render as R
ses = R.Session("%s", sky="gold")
ses.configure((180, 320), 4, 2, None)
book = R.Stamps(ses, "%s", "%s")
night = next(a for a, b, s in ses.segments if s == "night")
gold = next(a for a, b, s in ses.segments if s == "gold")
hits = []
for name, fn in (("Session.fingerprint", lambda: ses.fingerprint(night)),
                 ("Session.render_frame", lambda: ses.render_frame(night, "/nonexistent/x.png")),
                 ("Stamps.status", lambda: book.status(night)), ("Stamps.fp", lambda: book.fp(night)),
                 ("Stamps.mark", lambda: book.mark(night)),
                 ("Stamps.mark with a fingerprint", lambda: book.mark(night, ses.fingerprint(gold)))):
    try:
        fn()
        hits.append(name + ": NOT REFUSED")
    except R.SkyError as e:
        hits.append(name + ": SkyError")
print("LOCK", hits)
print("OWN", book.status(gold), ses.owns(gold), ses.owns(night), ses.sky_of(night))
try:
    R.Session("%s", sky="noon")
except R.SkyError as e:
    print("UNKNOWN SkyError")
try:
    R.Session("bell", sky="gold")
except R.SkyError as e:
    print("ONESKY SkyError")
''' % (FILM, FILM, VARIANT, FILM)
    p = subprocess.run([sys.executable, "-W", "ignore", "-c", code], cwd=ROOT, stdout=subprocess.PIPE,
                       stderr=subprocess.STDOUT, text=True)
    out = p.stdout
    lock = next((ln for ln in out.splitlines() if ln.startswith("LOCK")), "")
    check(lock.count("SkyError") == 6 and "NOT REFUSED" not in lock,
          "in the golden build a night frame cannot be fingerprinted, rendered, judged or stamped: %s" % lock[5:])
    check("OWN valid True False night" in out or "OWN missing True False night" in out,
          "... while its own frames work as always (%s)" % next((ln for ln in out.splitlines() if ln.startswith("OWN")), out[-300:]))
    check("UNKNOWN SkyError" in out and "ONESKY SkyError" in out,
          "an unknown sky name, and a sky for a film with one sky, are refused")
    code, out, _ = run(["--frames", "all", "--sky", "night"] + SMALL)
    check(code == 0 and DONE not in out and len(lines(out, "sky 'night':", "frames requested")) == 1,
          "--sky night by hand does the night's share only and never says '%s': %r"
          % (DONE.strip(), (lines(out, "sky 'night':", "frames requested") or [""])[0][9:]))


def part_encode():
    """--encode, --sheet, --still --captioned (the dip), --save-blend."""
    need_frames()
    mp4 = os.path.join(ROOT, "out", "preview", "%s_%s.mp4" % (FILM, VARIANT))
    if os.path.exists(mp4):
        os.remove(mp4)
    code, out, secs = run(["--encode", "--allow-holds"] + SMALL)
    check(code == 0 and os.path.exists(mp4) and not builds(out) and "faded" in out and "'frames': 206" in out,
          "--encode --allow-holds: one film of 206 frames with sound, nothing built (%.0f s): %s"
          % (secs, (lines(out, "audio:") or lines(out, "video:") or [""])[0][9:]))
    code, out, _ = run(["--encode"] + SMALL)
    check(code == 2 and "encode refused" in out, "--encode without --allow-holds refuses the step preview (exit code 2)")
    sheet = os.path.join(ROOT, "out", "test", FILM + "_sheet.png")
    t = os.path.getmtime(sheet) if os.path.exists(sheet) else 0
    code, out, _ = run(["--sheet", "5", "--res", "108x192", "--samples", "2"])
    check(code == 0 and os.path.getmtime(sheet) > t and sorted(builds(out)) == ["gold", "night"],
          "--sheet 5: tiles from both skies' builds, one sheet")
    cap = os.path.join(ROOT, "out", "test", FILM + "_3.5_cap.png")
    if os.path.exists(cap):
        os.remove(cap)
    code, out, _ = run(["--still", "3.5", "--captioned", "--res", "108x192", "--samples", "2"])
    ok, note = code == 0 and os.path.exists(cap), out[-300:]
    if ok:
        from PIL import Image

        from engine import captions

        im = Image.open(cap).convert("L")
        w, h = im.size
        top = im.crop((0, 0, w, int(h * 0.5))).getextrema()[1]
        band = im.crop((0, int(h * captions.CAPTION_BAND[0]), w, int(h * captions.CAPTION_BAND[1]))).getextrema()[1]
        plain = Image.open(cap[:-8] + ".png").convert("L")
        full = plain.crop((0, 0, plain.size[0], plain.size[1] // 2)).getextrema()[1]
        ok = top <= 0.67 * full + 4 and band >= 250 and "'Then'" in out
        note = "the picture's brightest pixel %d of 255 (the plain still: %d; gain 2/3), the caption 'Then' %d" % (top, full, band)
    check(ok, "--still 3.5 --captioned (frame 85, inside the dip): the picture is darkened, its caption is not (%s)" % note)
    blends = [os.path.join(ROOT, "out", "blend", "%s.%s.blend" % (FILM, sky)) for sky in ("gold", "night")]
    for b in blends:
        if os.path.exists(b):
            os.remove(b)
    code, out, _ = run(["--save-blend"])
    check(code == 0 and all(os.path.exists(b) for b in blends) and out.count("720x1280, 24 samples") == 2,
          "--save-blend: one file per sky with the final settings (%s)"
          % ", ".join("%s %.0f MB" % (os.path.basename(b), os.path.getsize(b) / 1e6) for b in blends if os.path.exists(b)))
    for b in blends:                                             # (two 30 MB files nobody needs after the check)
        if os.path.exists(b):
            os.remove(b)


PARTS = {"chunks": part_chunks, "engine": part_engine, "stale": part_stale, "lock": part_lock, "encode": part_encode}

if __name__ == "__main__":
    wanted = sys.argv[1:] or list(PARTS)
    t0 = time.time()
    for name in wanted:
        print("---- %s" % name, flush=True)
        PARTS[name]()
    bad = [t for ok, t in RESULTS if not ok]
    print("[multisky_selftest] %d checks, %d failed (%.0f s)" % (len(RESULTS), len(bad), time.time() - t0))
    sys.exit(len(bad))
