"""Self-test of render.py on a film with several skies: every flag, every exit code, the words the render loop waits
for, and the wrong-sky lock. Drives the real command line on films/_multisky_demo.py at thumbnail size.

    $BPY -m tools.multisky_selftest              # all parts (about 4 minutes on a busy machine: run the parts)
    $BPY -m tools.multisky_selftest chunks       # a chunked render to the end; "0 to render" only when it IS the end
    $BPY -m tools.multisky_selftest engine       # exit code 3 across skies, --restamp, --rerender-stale
    $BPY -m tools.multisky_selftest stale        # --prune-stale, a re-tagged shot's frame, --force, a wrong guess
    $BPY -m tools.multisky_selftest lock         # the wrong-sky lock: SkyError from Session and Stamps, and for a
                                                 #   film whose builds differ in more than the sky (_multisky_bad)
    $BPY -m tools.multisky_selftest encode       # --encode --allow-holds, --sheet, --still, --save-blend
    $BPY -m tools.multisky_selftest edits        # a director's edits: a new shot by name, a longer film, a renamed
                                                 #   sky (also into a new frame directory), a re-tagged shot
    $BPY -m tools.multisky_selftest detect       # SKIES through a star import, SKIES no source line shows, an empty
                                                 #   SKIES: the imported module decides whether a film has several skies
    $BPY -m tools.multisky_selftest midrun       # the film script edited while a chunk renders

Frames go to the preview variant 180x320_4spp_step8 of the demo (26 frames: 16 golden, 10 night; 11 more of the
last shot) and nowhere else; 'engine', 'stale' and 'encode' need the frames 'chunks' renders (they run it first when
frames are missing). 'edits', 'detect' and 'midrun' write their own films (tools/multisky_editfilm.py: a bare set, a
frame in 0.15 s), rewrite them between commands and remove them at the end.
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
        code, out, secs = run(["--frames", "all", "--max-seconds", "4"] + SMALL)
        calls += 1
        outs.append(out)
        if code != 0:
            return check(False, "chunk %d ended with exit code %d:\n%s" % (calls, code, out[-1500:]))
        if DONE in out:
            break
        said_early = said_early or any(DONE in ln for ln in out.splitlines())
    m = meta()
    n_png = len(mtimes())
    check(DONE in outs[-1] and not said_early and calls >= 2,
          "a chunked render (--max-seconds 4) needed %d calls; only the last one said '%s'" % (calls, DONE.strip()))
    check(n_png == 26 and len(m["frames"]) == 26 and all(rec.get("sky") == sky_of(m, int(f)) for f, rec in m["frames"].items()),
          "26 frames in ONE directory (%s), every stamp records the sky of its frame (%d golden, %d night)"
          % (os.path.relpath(DIR, ROOT), sum(r["sky"] == "gold" for r in m["frames"].values()),
             sum(r["sky"] == "night" for r in m["frames"].values())))
    first = builds(outs[0])
    out_of_time = bool(lines(outs[0], "sky 'gold': stopping after"))
    check(first[:1] == ["gold"] and (first == ["gold"]) == out_of_time,
          "the first call built the film's first sky (%s) and, its time used up inside it, no other" % first)
    two = [builds(o) for o in outs if len(builds(o)) == 2]
    check(len(two) <= 1 and all(len(builds(o)) <= 2 for o in outs),
          "skies built per call: %s (two only in the call in which the first sky ran out of frames)" % [builds(o) for o in outs])
    per_sky = lines("\n".join(outs), "sky '", "frames requested")
    check(per_sky and not any(DONE in ln for ln in per_sky), "no per-sky line says '%s' (%d such lines, e.g. %r)"
          % (DONE.strip(), len(per_sky), per_sky[-1][9:]))
    # the call after the end: nothing is built, and it is fast
    code, out, secs = run(["--frames", "all", "--max-seconds", "4"] + SMALL)
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
    # a golden frame whose PNG was rendered under the night sky (its shot was re-tagged since): the stamp names the
    # other sky and carries that render's fingerprint
    def retag(m):
        m["frames"]["25"]["sky"] = "night"
        m["frames"]["25"]["fp"] = "d" * 16
    rewrite(retag)
    code, out, _ = run(["--restamp", "25", "--restamp-changed"] + SMALL)
    check(code == 0 and len(lines(out, "0 frames re-stamped", "1 NOT accepted, rendered under another sky", "was 'night'")) == 1,
          "a PNG rendered under another sky is not accepted even by --restamp-changed: %r"
          % (lines(out, "NOT accepted") or [out[-200:]])[-1][-110:])
    before = mtimes()
    code, out, _ = run(["--frames", "all"] + SMALL)
    after = mtimes()
    check(code == 0 and [n for n in after if after[n] != before[n]] == ["f_0025.png"] and builds(out) == ["gold"]
          and len(lines(out, "1 stale: rendered under another sky (25: was 'night', now 'gold')")) == 1,
          "... it is rendered again, in its own sky's build (gold), nothing else is, and the reason is named")
    # a golden frame whose stamp carries a name the sky had before it was renamed, and this build's fingerprint: the
    # NAME is a label, the fingerprint is the proof. Kept, relabelled, nothing rendered.
    rewrite(lambda m: m["frames"]["33"].__setitem__("sky", "sunset"))
    before = mtimes()
    code, out, _ = run(["--frames", "all"] + SMALL)
    check(code == 0 and mtimes() == before and builds(out) == ["gold"] and DONE in out and meta()["frames"]["33"]["sky"] == "gold",
          "a stamp under a sky's OLD name with the current fingerprint is kept and relabelled (gold built once, nothing rendered)")
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
    # a film whose builds differ in more than the sky (films/_multisky_bad.py: a caption) is refused, not rendered
    bad = "_multisky_bad"
    bdir = os.path.join(ROOT, "out", "preview", bad, VARIANT)
    code, out, _ = run(["--frames", "41-49"] + SMALL, film=bad)
    made = sorted(os.listdir(bdir)) if os.path.isdir(bdir) else []
    check(code not in (0, 3) and "SkyError" in out and "another 'captions'" in out and DONE not in out
          and "f_0049.png" not in made,
          "a film whose night build has other captions than its golden build stops with SkyError (exit code %d); the "
          "night frame 49 was not rendered (written: %s)" % (code, made))
    for n in made:
        os.remove(os.path.join(bdir, n))
    if os.path.isdir(bdir):
        os.rmdir(bdir)
        if not os.listdir(os.path.dirname(bdir)):
            os.rmdir(os.path.dirname(bdir))
    code, out, _ = run(["--frames", "all", "--sky", "night"] + SMALL)
    check(code == 0 and DONE not in out and len(lines(out, "sky 'night':", "frames requested")) == 1,
          "--sky night by hand does the night's share only and never says '%s': %r"
          % (DONE.strip(), (lines(out, "sky 'night':", "frames requested") or [""])[0][9:]))
    # tools that render single frames: render.session_for builds the sky of the frame they ask for
    code = r'''
import render as R
t = R.sky_table("%s")
print("TABLE", t.describe())
ses = R.session_for("%s", 50)
print("FOR", ses.sky, ses.owns(50), ses.fingerprint(50)["fp"][:6] != "")
print("ONE", R.sky_table("bell"))
''' % (FILM, FILM)
    p = subprocess.run([sys.executable, "-W", "ignore", "-c", code], cwd=ROOT, stdout=subprocess.PIPE,
                       stderr=subprocess.STDOUT, text=True)
    check("FOR night True True" in p.stdout and "TABLE gold 1-42, night 43-82" in p.stdout and "ONE None" in p.stdout,
          "render.session_for(film, 50) builds the sky of frame 50 (night); render.sky_table: %s"
          % next((ln[6:] for ln in p.stdout.splitlines() if ln.startswith("TABLE")), p.stdout[-300:]))
    # what a command killed with SIGKILL leaves in out/test is removed by the next command; a running command's is not
    test = os.path.join(ROOT, "out", "test")
    gone = subprocess.Popen([sys.executable, "-c", "pass"])
    gone.wait()
    dead, alive = os.path.join(test, "render_sky_selftest_dead"), os.path.join(test, "render_sky_selftest_alive")
    for d, pid in ((dead, gone.pid), (alive, os.getpid())):
        os.makedirs(d, exist_ok=True)
        for fn, text in (("pid", str(pid)), ("sky_0.json", "{}")):
            with open(os.path.join(d, fn), "w", encoding="utf-8") as fh:
                fh.write(text)
    code, out, _ = run(["--frames", "1"] + SMALL)
    left = sorted(d for d in os.listdir(test) if d.startswith("render_sky_"))
    check(code == 0 and left == ["render_sky_selftest_alive"],
          "the temporary directory of a killed command is removed by the next one, a running command's is kept (%s)" % left)
    for fn in ("pid", "sky_0.json"):
        if os.path.exists(os.path.join(alive, fn)):
            os.remove(os.path.join(alive, fn))
    if os.path.isdir(alive):
        os.rmdir(alive)


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


# --------------------------------------------------------------------------------------------------------------
# a director's edits, played on the film tools/multisky_editfilm.py writes (a bare set: a frame in 0.15 s)
# --------------------------------------------------------------------------------------------------------------

TINY = ["--res", "90x160", "--samples", "1", "--threads", "1"]
TINY_VARIANT = "90x160_1spp"


def edit_dir(film=None, variant=TINY_VARIANT):
    from tools import multisky_editfilm as E

    return os.path.join(ROOT, "out", "preview", film or E.FILM, variant)


def edit_meta(film=None, variant=TINY_VARIANT):
    with open(os.path.join(edit_dir(film, variant), "meta.json"), encoding="utf-8") as fh:
        return json.load(fh)


def edit_mtimes(film=None, variant=TINY_VARIANT):
    d = edit_dir(film, variant)
    return {n: os.stat(os.path.join(d, n)).st_mtime_ns for n in sorted(os.listdir(d)) if n.endswith(".png")} \
        if os.path.isdir(d) else {}


def rendered(before, after):
    """Frame numbers whose PNG is new or was written again."""
    return [int(n[2:6]) for n in sorted(after) if after[n] != before.get(n)]


def stamp_skies(m):
    """'gold 1-6, night 7-12, ...' from the stamps of a meta.json (what each PNG was rendered under)."""
    runs = []
    for f in sorted(int(k) for k in m["frames"]):
        sky = m["frames"][str(f)].get("sky")
        if runs and runs[-1][0] == sky and runs[-1][2] == f - 1:
            runs[-1][2] = f
        else:
            runs.append([sky, f, f])
    return ", ".join("%s %d-%d" % (sky, a, b) for sky, a, b in runs)


def no_crash(out):
    return "Traceback" not in out and "Error" not in out.replace("WARNING CUEW initialization failed: Error", "")


def base_film():
    """The base edit film, rendered completely (30 frames: gold 1-6, night 7-12, gold 13-18, night 19-24, gold 25-30)."""
    from tools import multisky_editfilm as E

    E.remove_all()
    E.write()
    code, out, secs = run(["--frames", "all"] + TINY, film=E.FILM)
    ok = code == 0 and DONE in out and len(edit_mtimes()) == 30
    check(ok, "the edit film from nothing: 30 frames, stamps %s (%.0f s)" % (stamp_skies(edit_meta()) if ok else out[-600:], secs))
    return E


def part_edits():
    """After an edit the last build's sky table is wrong exactly where the director changed the film: a new shot
    by name, a range beyond the old end, a renamed sky (also in a frame directory that is new), a re-tagged shot."""
    E = base_film()
    F = E.FILM
    # ---- a new shot, asked for by name
    shots = E.SHOTS + [("e", 6, "night")]
    E.write(shots=shots)
    before = edit_mtimes()
    code, out, _ = run(["--frames", "e"] + TINY, film=F)
    check(code == 0 and no_crash(out) and rendered(before, edit_mtimes()) == list(range(31, 37)) and DONE in out
          and "6 requested" in out,
          "a new shot asked for by name (--frames e): exit code %d, rendered %s: %r"
          % (code, _r(rendered(before, edit_mtimes())), (lines(out, "frames:") or [out[-300:]])[-1][9:]))
    # ---- a longer film, asked for by a range beyond the old end
    shots = shots + [("f", 6, "gold")]
    E.write(shots=shots)
    before = edit_mtimes()
    code, out, _ = run(["--frames", "37-42"] + TINY, film=F)
    check(code == 0 and no_crash(out) and rendered(before, edit_mtimes()) == list(range(37, 43)) and DONE in out,
          "a range beyond the old end (--frames 37-42): exit code %d, rendered %s: %r"
          % (code, _r(rendered(before, edit_mtimes())), (lines(out, "frames:") or [out[-300:]])[-1][9:]))
    code, out, _ = run(["--restamp", "all"] + TINY, film=F)
    check(code == 0 and no_crash(out) and ("0 frames re-stamped" in out or "nothing to re-stamp" in out),
          "--restamp all on the longer film: nothing to do, said truthfully")
    # ---- the first sky renamed (same values): nothing is rendered, deleted or refused; the stamps are relabelled
    sun = {"sun": E.SKIES["gold"], "night": E.SKIES["night"]}
    ren = lambda t, a, b: [(n, k, b if s == a else s) for n, k, s in t]                        # noqa: E731
    shots = ren(shots, "gold", "sun")
    E.write(skies=sun, shots=shots, change=(25, "sun"))
    before = edit_mtimes()
    code, out, _ = run(["--restamp", "all", "--restamp-changed"] + TINY, film=F)
    check(code == 0 and no_crash(out) and "NOT accepted" not in out,
          "sky 'gold' renamed to 'sun': --restamp all --restamp-changed refuses nothing (exit code %d)" % code)
    code, out, _ = run(["--prune-stale"] + TINY, film=F)
    check(code == 0 and no_crash(out) and len(edit_mtimes()) == 42, "... --prune-stale deletes nothing (%d PNGs)" % len(edit_mtimes()))
    code, out, _ = run(["--frames", "all"] + TINY, film=F)
    m = edit_meta()
    check(code == 0 and no_crash(out) and edit_mtimes() == before and DONE in out
          and {r.get("sky") for r in m["frames"].values()} == {"sun", "night"},
          "... --frames all renders nothing; the stamps now read %s" % stamp_skies(m))
    code, out, _ = run(["--encode"] + TINY, film=F)
    check(code == 0 and "'frames': 42" in out, "... and --encode makes the film (exit code %d)" % code)
    # ---- both skies renamed, and a frame directory that does not exist yet (how a final render starts)
    both = {"sun": E.SKIES["gold"], "moon": E.SKIES["night"]}
    shots = ren(shots, "night", "moon")
    E.write(skies=both, shots=shots, change=(25, "sun"))
    other = ["--res", "72x128", "--samples", "1", "--threads", "1"]
    code, out, _ = run(["--frames", "all"] + other, film=F)
    check(code == 0 and no_crash(out) and DONE in out and len(edit_mtimes(variant="72x128_1spp")) == 42,
          "both skies renamed, a NEW frame directory: exit code %d, %d frames, stamps %s"
          % (code, len(edit_mtimes(variant="72x128_1spp")),
             stamp_skies(edit_meta(variant="72x128_1spp")) if code == 0 else out[-400:]))
    code, out, _ = run(["--frames", "all"] + TINY, film=F)
    check(code == 0 and no_crash(out) and edit_mtimes() == before and DONE in out,
          "... and the old directory: nothing rendered, stamps %s" % stamp_skies(edit_meta()))
    code, out, _ = run(["--still", "0.3", "--res", "90x160", "--samples", "1"], film=F)
    check(code == 0 and no_crash(out) and "sky moon" in out, "... --still 0.3 (frame 8, sky 'moon') works too")
    still = os.path.join(ROOT, "out", "test", F + "_0.3.png")
    if os.path.exists(still):
        os.remove(still)
    # ---- a shot re-tagged (c: sun -> moon): exactly its frames, refused by --restamp-changed, named by their reason
    shots = [(n, k, "moon" if n == "c" else s) for n, k, s in shots]
    E.write(skies=both, shots=shots, change=(25, "sun"))
    code, out, _ = run(["--restamp", "all", "--restamp-changed"] + TINY, film=F)
    check(code == 0 and len(lines(out, "sky 'moon': restamp", "6 NOT accepted", "another sky", "13-18")) == 1,
          "shot 'c' re-tagged sun -> moon: --restamp-changed does not accept its 6 PNGs: %r"
          % (lines(out, "NOT accepted") or [out[-300:]])[-1][9:])
    code, out, _ = run(["--encode"] + TINY, film=F)
    check(code == 2, "... --encode refuses the film (exit code %d)" % code)
    before = edit_mtimes()
    code, out, _ = run(["--frames", "all"] + TINY, film=F)
    why = lines(out, "stale: rendered under another sky")
    check(code == 0 and rendered(before, edit_mtimes()) == list(range(13, 19)) and DONE in out and len(why) == 1
          and "was 'sun'" in why[0],
          "... --frames all renders exactly %s again and says why: %r" % (_r(rendered(before, edit_mtimes())), (why or [""])[0][9:]))
    E.remove_all()


def part_detect():
    """Whether a film has several skies is decided by the film as it IMPORTS, whatever its source looks like."""
    from tools import multisky_editfilm as E

    E.remove_all()
    E.write()
    # ---- SKIES through a star import
    E.write_star()
    star = E.OTHERS[0]
    code, out, _ = run(["--frames", "all"] + TINY, film=star)
    check(code == 0 and no_crash(out) and DONE in out and len(edit_mtimes(star)) == 30 and "30 requested" in out
          and sorted(builds(out)) == ["gold", "night"],
          "SKIES through `from films.x import *`: both skies rendered, %d of 30 frames: %r"
          % (len(edit_mtimes(star)), (lines(out, "frames:") or [out[-300:]])[-1][9:]))
    # ---- SKIES that no source line binds: seen once the module is imported
    E.write_hidden()
    hid = E.OTHERS[1]
    code, out, _ = run(["--frames", "all", "--max-seconds", "1"] + TINY, film=hid)
    n1 = len(edit_mtimes(hid))
    check(code == 0 and no_crash(out) and (DONE in out) == (n1 == 30) and 0 < n1,
          "SKIES not visible in the source, first chunk (--max-seconds 1): %d of 30 frames, '%s' %s"
          % (n1, DONE.strip(), "said" if DONE in out else "not said"))
    calls = 1
    while DONE not in out and calls < 12 and code == 0:
        code, out, _ = run(["--frames", "all", "--max-seconds", "1"] + TINY, film=hid)
        calls += 1
    m = edit_meta(hid) if code == 0 else {"frames": {}}
    check(code == 0 and len(edit_mtimes(hid)) == 30 and DONE in out
          and all(rec.get("sky") == sky_of(m, int(f)) for f, rec in m["frames"].items()),
          "... finished after %d calls: 30 frames, stamps %s" % (calls, stamp_skies(m)))
    code, out, _ = run(["--encode"] + TINY, film=hid)
    check(code == 0 and "'frames': 30" in out, "... --encode alone (exit code %d)" % code)
    # ---- one sky, and the name SKIES all the same
    for write, film, how in ((E.write_empty, E.OTHERS[2], "`SKIES = {}`"), (E.write_none, E.OTHERS[3], "a SKIES that is empty at run time")):
        write()
        code, out, _ = run(["--frames", "all"] + TINY, film=film)
        code2, out2, _ = run(["--frames", "all"] + TINY, film=film)
        check(code == 0 and no_crash(out) and len(edit_mtimes(film)) == 4 and "frames: 4 requested, 0 already done, 4 to render" in out
              and code2 == 0 and "frames: 4 requested, 4 already done, 0 to render" in out2,
              "a film with one sky and %s is rendered as one sky (exit codes %d, %d; %d of 4 frames)"
              % (how, code, code2, len(edit_mtimes(film))))
    E.remove_all()


def part_midrun():
    """The film script is edited while a chunk is rendering: no error, nothing wrong, the next call finishes."""
    import threading

    from tools import multisky_editfilm as E

    E.remove_all()
    E.write(shots=[("a", 30, "gold"), ("b", 6, "night")], change=None)
    first = os.path.join(edit_dir(), "f_0003.png")
    box = {}

    def go():
        box["r"] = run(["--frames", "all"] + TINY, film=E.FILM)

    th = threading.Thread(target=go)
    th.start()
    t0 = time.time()
    while not os.path.exists(first) and time.time() - t0 < 60:
        time.sleep(0.05)
    with open(E.path(), "a", encoding="utf-8") as fh:
        fh.write("# a comment the director added while the first sky was rendering\n")
    th.join()
    code, out, _ = box["r"]
    n = len(edit_mtimes())
    check(code == 0 and no_crash(out) and DONE not in out and n == 36
          and len(lines(out, "changed while this command ran")) == 1,
          "the film script edited while the first sky rendered: exit code %d, no error, %d of 36 frames, '%s' not said: %r"
          % (code, n, DONE.strip(), (lines(out, "changed while") or [out[-400:]])[-1][9:140]))
    before = edit_mtimes()
    code, out, _ = run(["--frames", "all"] + TINY, film=E.FILM)
    check(code == 0 and DONE in out and edit_mtimes() == before,
          "... the next call judges every frame again, renders nothing and says %r" % (lines(out, "frames:") or [""])[-1][9:90])
    E.remove_all()


def _r(frames):
    import render as R

    return R._ranges(frames) or "nothing"


PARTS = {"chunks": part_chunks, "engine": part_engine, "stale": part_stale, "lock": part_lock, "encode": part_encode,
         "edits": part_edits, "detect": part_detect, "midrun": part_midrun}

if __name__ == "__main__":
    wanted = sys.argv[1:] or list(PARTS)
    t0 = time.time()
    for name in wanted:
        print("---- %s" % name, flush=True)
        PARTS[name]()
    bad = [t for ok, t in RESULTS if not ok]
    print("[multisky_selftest] %d checks, %d failed (%.0f s)" % (len(RESULTS), len(bad), time.time() - t0))
    sys.exit(len(bad))
