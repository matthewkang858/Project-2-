"""Render CLI. One Blender process builds the film once, then does everything that was asked for (a film with
several skies: one such process per sky, see "Several skies in one film" below).

    BPY=/path/to/python-with-bpy ;  cd <project root>
    $BPY -m render <film> --still 1.5                 # out/test/<film>_1.5.png      (540x960, 16 samples, 2 threads)
    $BPY -m render <film> --still 0.5,2,7.25 --res 720x1280 --samples 24 --captioned
    $BPY -m render <film> --sheet 12                  # out/test/<film>_sheet.png    (contact sheet WITH captions)
    $BPY -m render <film> --frames all --max-seconds 240      # FINAL frames: out/frames/<film>/f_####.png
                                                              #   (720x1280, 24 samples, 4 threads), resumable
    $BPY -m render <film> --encode                    # out/<film>.mp4  1080x1920 H.264 yuv420p crf 16 +faststart
                                                      #   + the film's narration when narration/<film>.wav exists
                                                      #   (--audio FILE: another sound file; --no-audio: silent)
    $BPY -m render <film> --frames all --step 4 --res 360x640 --samples 8 --encode --allow-holds
                                                      # PREVIEW: out/preview/<film>/360x640_8spp_step4/ and
                                                      #   out/preview/<film>_360x640_8spp_step4.mp4
    $BPY -m render <film> --still 1.5 --zones         # also <name>_zones.png: Reels UI zones, caption band, safe area
    $BPY -m render <film> --save-blend                # out/blend/<film>.blend with textures packed, final settings
    $BPY -m render <film> --frames all --rerender-stale   # after an engine edit: render the stale frames again
    $BPY -m render <film> --restamp all               # after an engine edit that changed no picture: keep the frames
    $BPY -m render <film> --prune-stale               # delete PNGs that are not part of the film any more

A film is films/<film>.py exposing build(scene) -> {"film": engine.shots.Film, "captions": [(word, t0, t1), ...]}
(optional: "narration", "stage", "fades": see "Dips to black"; a film with several skies: build(scene, sky=None)).
Frame numbers start at 1 (frame 1 = second 0). Several actions can be combined in one call; they run in the
order still, sheet, frames, save-blend, encode.

Final and preview frames never share a directory: any --res / --samples / --step that differs from the final
settings, and --no-motion-blur, selects a preview directory named after those settings, for --frames and for
--encode alike.

Resuming is safe AND cheap, because a frame on disk is judged by what it shows, not by which files were touched.
Every rendered frame is stamped in meta.json with
  s   the render settings (resolution, samples, motion blur),
  e   a hash of the ENGINE sources that can change a pixel (engine/*.py without captions / post / stamp; never the
      film script, render.py or tools/), and
  fp  the scene fingerprint of that frame (engine/stamp.py): a hash of everything Cycles is given for it: look and
      render settings, the shot camera, every visible object with its mesh, materials, textures and motion, every
      light that is on.
A frame is skipped while its PNG has the requested size and all three are current. So:
  - editing a caption, the caption timing, a comment or a docstring in a FILM script makes nothing stale; editing one
    shot makes that shot's frames stale (they are rendered again, the others are kept); changing the sky, the
    grade or the set makes everything stale. No flag is needed for any of this.
  - editing an ENGINE file while finals exist stops the next --frames run with exit code 3 and a list of the files
    that changed, before anything is rendered (a chunked final render must not silently start again at frame 1
    because somebody touched a docstring). Then either
        --restamp all          accept the frames whose scene fingerprint is unchanged (the edit altered no
                               picture): they are stamped with the current engine hash, nothing is rendered; or
        --rerender-stale       render every stale frame again.
    --restamp takes A-B, a single frame, 'all' or a shot name; --restamp-changed also accepts frames whose
    fingerprint differs or that carry no stamp (you assert the picture is the same).
  - --prune-stale deletes the PNGs in the film's frame directory that are not valid any more (older versions,
    frames beyond the film's end), so the directory holds only the film.
--encode refuses to run while frames are missing or stale (exit code 2: a crashed chunk must not become a
stutter), unless --allow-holds says the gaps are deliberate (step previews). --encode alone reuses meta.json (no
rebuild) when none of the sources it lists has changed; after a caption edit it rebuilds the film (seconds),
finds every fingerprint unchanged and encodes the frames that are there.
Exit codes: 0 done, 1 nothing to do, 2 encode refused, 3 stopped because engine sources changed under final frames,
4 encode of a long film not finished yet (run the same command again).

Sound. A narrated film (engine/narration.py: a NARRATION literal in the film module, spoken by tools/narrate.py into
narration/<film>.wav + .json) needs no flag: --encode muxes narration/<film>.wav whenever that file exists (AAC
192 kb/s, 48 kHz, dual mono, from t = 0, exactly as long as the picture; the picture itself is encoded as without
sound and its stream is copied). Automatic, because a flag can be forgotten or point at an old file, and the
narration is what the film's captions and cuts were timed from: before muxing, --encode checks that the json was
spoken from the film's current NARRATION, that the wav is the one the json describes and that the film is not
shorter than its last word, and refuses (exit code 2) otherwise. The narration files count as sources of the film:
speak the text again and the next --encode rebuilds the film, so captions and audio cannot drift apart.
A film without narration/<film>.wav is encoded silent, exactly as before.

Long films. Encoding costs 0.13 s per frame here, 0.26 s when the machine is shared (PNG read, Lanczos, caption,
x264): a one-minute film is 190 to 380 s of it, and nothing would be left of a command killed at 300 s. So a film
longer than 20 s (engine.post.SEGMENT_OVER frames) is encoded in parts of 10 s (engine.post.encode_parts): each
part is kept on disk, a part whose frames and captions are unchanged is never encoded twice, no new part is
started later than 170 s after the command began (--max-seconds lowers that), and when all parts exist they are joined
with a stream copy and the narration is muxed under the whole film. Until then --encode ends with exit code 4:
run the same command again (a minute takes one call on an idle machine, two or three on a busy one). Films of
20 s or less are encoded in one pass, exactly as before.

Dips to black. A film may return "fades": [(t0, t1, g0, g1), ...], ramps of the PICTURE's gain in film seconds
(0 = black, 1 = untouched; engine/post.py has the exact rule). films.lookdev.Stage writes them from frame numbers:
st.dip(frame, out=3, hold=0, back=3) is black ON `frame` (the first frame of a shot), fading out over the 3
frames before it and back in over the 3 after it; st.fade(frame0, frame1, g0, g1) is one ramp (render.py takes
st.fades when the film returns its Stage and no "fades"). They are applied at ENCODE time, after the upscale and
before the caption is drawn (the caption stays at full strength: the narrator talks through a dip), in --encode,
--sheet and --still --captioned alike. They live in meta.json, never in a frame's stamp: adding, moving or removing
a dip makes --encode rebuild the film (seconds), find every frame unchanged and encode again; nothing is rendered.
A film without fades has the meta.json and the mp4 it always had, bit for bit.

Several skies in one film (day and night in ONE module, one frame directory, one narration, one mp4).

  The film's side (the worked example is films/_multisky_demo.py; the recipe is at films.lookdev.Stage):
      SKIES = {"gold":  dict(preset="golden", az=62.0, el=27.0, bloom=1.0, grade="warm"),
               "night": dict(preset="night", az=176.0, el=21.0, bloom=1.3, grade="cool")}     # at module level
      def build(scene, sky=None):
          st = Stage(scene, film, v, skies=SKIES, sky=sky)     # builds the ACTIVE sky (None: the first of SKIES)
          s = st.shot("door_night", seconds, sky="night")      # every shot names its sky (default: the one before)
          st.sky_change(frame, "gold")                         # a sky change INSIDE the shot that owns `frame`
          return {"film": film, "captions": ..., "narration": nar, "stage": st}
  A build has ONE sky: look.set_time makes one world, one key light, one set of sky sprites, and the compositor
  one grade. The timeline, every actor and every key are the same in every build; a frame is the film's picture
  only when it is rendered in the build whose active sky is its own. render.py reads the sky table from the Stage
  (stage.sky_name, stage.sky_segments(); or "sky" and "sky_segments" = [(first frame, last frame, sky), ...] in
  the returned dict) and takes the rest on itself:

  * ONE PROCESS PER SKY. `render <film> ...` for such a film builds nothing itself. It works out which skies have
    work and runs each as `render <film> <the same arguments> --sky NAME`: a fresh Blender process that builds the
    film with that sky and does that sky's share of every action. (Why a process and not a second build in the
    same one: `tools.multisky_check inprocess` found second builds in one process identical to fresh ones on
    every film it could try (11 builds of 5 films: 220 fingerprints, 11 rendered frames), but engine modules
    keep module-level state between builds, five of them were being rewritten while this was made, and such a
    proof holds only for the code of its day. A fresh process is how every frame so far was rendered and
    judged, needs no proof, and costs 0.6 s per sky: Blender's start and the film's imports.)
  * WHICH FILMS: a film whose module has a non-empty SKIES. render.py reads that from the SOURCE in a millisecond
    (declares_skies: an assignment at module level, a named import, `from x import *`; project modules are
    followed), but what DECIDES is the imported module: a film whose SKIES no source line shows is handed over to
    the sky-by-sky path after its first build (every command then builds once more than needed, and says so), and
    `SKIES = {}` is a film with one sky, rendered as any other. So the two can never disagree about a film.
  * THE WRONG SKY IS IMPOSSIBLE, not merely avoided: a Session owns only the frames tagged with its sky.
    Session.fingerprint / render_frame and Stamps.status / fp / mark raise SkyError for any other frame, so no
    code path, present or future, can render, stamp, re-stamp or judge a frame in another sky's build. Every stamp
    records the sky it was rendered under ('sky').
  * A SKY'S NAME IS A LABEL, ITS FINGERPRINT THE PROOF. What a sky is (world, key light, sun / moon, stars, clouds,
    haze, grade) is part of every frame's scene fingerprint. A PNG whose fingerprint is what its own sky's build
    expects now is valid under whatever name it was rendered: renaming a key of SKIES (night -> night_a) costs
    one build per sky and no frame; the stamps are relabelled. A PNG whose fingerprint differs and whose stamp
    names another sky (its shot was re-tagged, a sky_change moved) is stale with the reason "rendered under
    another sky (87-95: was 'gold', now 'night')" (status 'sky'); --restamp-changed never accepts such a frame.
  * ONE FRAME DIRECTORY, ONE meta.json: out/frames/<film>/ (previews: one directory per variant, as always).
    Each sky's process writes its own frames' stamps and expectations and carries the other skies' through. The
    other skies' EXPECTATIONS survive only while no source changed since they were written; after an edit their
    frames count as 'not judged' until their own sky's build has looked at them. meta.json describes the whole
    timeline (shots with their sky, 'sky_segments', 'skies'), so --encode sees one complete film.
  * NO BUILD WITHOUT WORK: while no source changed since meta.json was written, the frames' judgments in it are
    still true, and the command builds only the skies that have a frame to render. Measured on the village with a
    one-minute film (films/_multisky_minute.py: 1,440 frames, two skies, five segments): a chunk that renders in
    one sky spends 3.0 s outside its frames (0.2 s this process, 0.6 s Blender and the film's imports, 1.5 to
    1.7 s the build), the chunk in which one sky is finished and the next begins 5.2 s; inside the frame loop
    each frame costs its fingerprint (16 to 20 ms) and one meta.json write (14 ms at 1,440 stamps, 403 KB); the
    call that finds nothing left builds nothing and takes 0.5 s. After an edit, both skies are built and all
    1,440 frames judged in 32 s.
  * AFTER AN EDIT (any source of the film changed since meta.json was written) the sky table on disk is the film
    BEFORE the edit: wrong exactly where the timeline or SKIES were changed (a new shot's name, frames beyond the
    old end, a renamed sky). Nothing is planned from it. The first process builds the sky that table suggests if
    the film still has one of that name (else the film's first), does its share of everything asked for and
    reports the film's real table; the other skies follow from that. Every sky with requested frames is built
    once, judges its frames (16 to 50 ms a frame) and renders what changed. A brand-new frame directory (the
    first chunk of a final render) starts the same way.
  * WHAT IT PRINTS (--frames): per sky "[render] sky 'night': 628 frames requested, 120 already done, 508 to
    render at ..." (or "... none to render at ..."), its frames, and at the very end ONE line for the whole film:
        [render] frames: 1440 requested, 1440 already done, 0 to render at 720x1280, 24 samples, 4 threads (2 skies: ...)
        [render] frames: 1440 requested, 1380 already done, 60 rendered in this run, 0 to render at ...
        [render] frames: 1440 requested, 932 done (60 in this run), 508 left at ... (sky 'night': 508); re-run ...
    The words " 0 to render" appear only in that line and only when every requested frame of every sky is a valid
    frame as the build of its OWN sky judged it: a loop that waits for them cannot stop early. Exit codes are
    the same as for any film (0, 2, 3, 4). Before each sky's process starts: "[render] sky 'night': a process of
    its own for frames" (the actions it has), or after an edit "[render] sky 'gold': a process of its own, to
    learn the film's sky table and do its share". A film rendered from its first chunk to its last says
    " 0 to render" in the chunk that renders its last frame; the next call builds nothing.
  * THE FILM SCRIPT MAY BE EDITED WHILE A CHUNK RENDERS, as for any film. The sky processes of one command then
    built different sources (each report names the files its build read and their hash; a file whose hash is not
    what a process built from was edited during the command, also when the edit adds an import): every frame
    that was rendered is right and stamped, the command says "a source file of the film changed while this
    command ran" instead of the film's account and ends with exit code 0 (2 with --encode, which is not
    attempted); the next call judges every sky again. Only when no file changed and two skies' builds still read
    different files or made different timelines is that the film's fault (SkyError).
  * --max-seconds is the whole command's rendering time: when one sky is finished the next one is built and gets
    what is left; a sky is not started for rendering once the time is used up.
  * EXIT CODE 3 (engine sources changed under existing frames) looks at EVERY sky's frames before any sky renders:
    a sky's process checks the stamps of the other skies' requested frames too (a stamp names its engine
    sources, no build is needed for that) and stops. The other skies are then built only to report which of their
    frames show an unchanged scene (--restamp all keeps those). --restamp / --prune-stale combined with --frames
    are finished for every sky before any frame is checked or rendered (each sky is then built twice).
  * --still S and --sheet N: each sky's process renders its own stills and tiles; the sheet is put together at the
    end. After an edit the first process builds the sky the old table gives second S; if the frame is another
    sky's now, that sky is built next (one build more, never a wrong picture). --frames takes all, A-B, a single
    frame or a shot name as always; a shot with a sky change inside is split between its two skies.
    --restamp, --restamp-changed, --rerender-stale, --prune-stale, --force work per sky; --save-blend writes one
    file per sky: out/blend/<film>.<sky>.blend.
  * --sky NAME by hand does one sky's share only (it never encodes and never says "0 to render").
  * A SKY CHANGE INSIDE A SHOT is not a cut: the scene does not change at that frame at all (one shot, one camera,
    one baked path, actors mid-motion). The frames before it are rendered in one build and the frames from it on
    in the other. So the camera cannot jump and motion blur is that of an uncut shot (tools/multisky_check.py
    proves both on rendered frames).
  * WHAT COSTS WHAT: an edit to one shot re-renders that shot's frames, in its sky's build; an edit to the VALUES
    of one entry of SKIES re-renders exactly that sky's frames; re-tagging a shot or moving a sky_change
    re-renders the frames whose sky changed; renaming a sky, a caption or a dip re-render nothing (every sky is
    built once to see that: about 3 s each, plus 16 to 50 ms per frame to judge).
  * The film must not make anything but the sky depend on build()'s `sky` argument (no shot, actor, light key,
    caption, render setting or import inside `if sky == ...`). render.py notices: a timeline that differs between
    two skies' builds of the same sources raises SkyError. A film may set its own final resolution and samples in
    build(), as any film may; they must be the same in every build.
  * TOOLS that render single frames of a film (noise checks, timing studies): render.Session(name) builds the
    FIRST sky and refuses the other skies' frames. Use render.session_for(name, frame) (or seconds=...): the
    Session of that frame's sky; render.sky_table(name) is the film's sky table without a build in this process.
  * Temporary files: the sky processes' reports and sheet tiles live in out/test/render_sky_*/ while a command
    runs. A terminated command (timeout) removes its own; what a killed one (SIGKILL) left is removed by the next
    command for a film with several skies (the directory holds its command's process id and start time: a
    directory whose process is gone, a zombie or another process by now is removed, a running command's is not).
    A killed sky process never leaves a partial frame: a PNG is written as f_####_part.png and renamed once
    complete (a _part file left by a kill is not a frame and is overwritten by the next render of that frame).
"""
import argparse
import ast
import hashlib
import importlib
import json
import os
import subprocess
import sys
import tempfile
import time
import types

ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

ENCODE_SECONDS = 170.0           # --encode of a long film: no new part is started later than this after the
                                 #   command began (--max-seconds overrides it)
STILL_RES, STILL_SAMPLES, STILL_THREADS = (540, 960), 16, 2
SHEET_RES, SHEET_SAMPLES = (270, 480), 8
FINAL_RES, FINAL_SAMPLES, FINAL_THREADS = (720, 1280), 24, 4


def _parse_res(text):
    w, h = text.lower().split("x")
    return int(w), int(h)


def _parse_args(argv):
    ap = argparse.ArgumentParser(prog="render", description="Build a film once and render stills / frames / sheet / mp4.")
    ap.add_argument("film", help="module name under films/, e.g. _demo")
    ap.add_argument("--still", action="append", default=[], metavar="S",
                    help="render the frame at second S to out/test/<film>_<S>.png (comma-separate or repeat for several)")
    ap.add_argument("--frames", metavar="A-B", help="frame numbers to render (inclusive), a single frame, or 'all'")
    ap.add_argument("--step", type=int, default=1,
                    help="with --frames: render only every K-th frame (a preview: own directory; encode it with "
                         "the same --step and --allow-holds)")
    ap.add_argument("--sheet", type=int, metavar="N", help="contact sheet of N evenly spaced low-res frames with captions")
    ap.add_argument("--encode", action="store_true", help="frames -> out/<film>.mp4 (1080x1920, captions, H.264)")
    ap.add_argument("--save-blend", action="store_true", help="write out/blend/<film>.blend with textures packed")
    ap.add_argument("--res", type=_parse_res, metavar="WxH", help="override the render resolution")
    ap.add_argument("--samples", type=int, help="override the Cycles sample count")
    ap.add_argument("--threads", type=int, help="render threads (default 2 for stills / sheet, 4 for frames)")
    ap.add_argument("--force", action="store_true", help="re-render frames that already exist")
    ap.add_argument("--captioned", action="store_true",
                    help="with --still: also save <name>_cap.png, upscaled to 1080x1920 with its caption")
    ap.add_argument("--max-seconds", type=float, default=0.0,
                    help="with --frames: stop starting new frames after this many seconds (resume by re-running); "
                         "with --encode of a film longer than 20 s: stop starting new parts this long after the "
                         "command began (170 at most; exit code 4 until the last part is written)")
    ap.add_argument("--no-motion-blur", action="store_true", help="disable motion blur (faster look-dev stills)")
    ap.add_argument("--audio", metavar="FILE",
                    help="with --encode: mux this audio file instead of the film's narration (AAC 192k 48 kHz stereo, "
                         "padded or cut to the video)")
    ap.add_argument("--no-audio", action="store_true",
                    help="with --encode: a silent mp4 even when narration/<film>.wav exists")
    ap.add_argument("--allow-holds", action="store_true",
                    help="with --encode: hold the previous frame over missing frames instead of failing")
    ap.add_argument("--zones", action="store_true",
                    help="with --still: also save <name>_zones.png with the Reels UI zones, caption band and safe area")
    ap.add_argument("--rerender-stale", action="store_true",
                    help="with --frames: also render again the frames that are stale because ENGINE sources changed "
                         "(without it such a run stops with exit code 3 before rendering anything)")
    ap.add_argument("--restamp", metavar="A-B|all|SHOT",
                    help="accept existing frames without rendering: frames whose scene fingerprint is unchanged get "
                         "the current engine stamp (after an engine edit that altered no picture)")
    ap.add_argument("--restamp-changed", action="store_true",
                    help="with --restamp: also accept frames whose fingerprint differs or that have no stamp "
                         "(you assert the picture is the same)")
    ap.add_argument("--prune-stale", action="store_true",
                    help="delete the PNGs in the film's frame directory that are not valid frames of the film any more")
    ap.add_argument("--sky", metavar="NAME",
                    help="a film with several skies: do only this sky's share of the work, in this process (this is "
                         "how render.py runs each sky itself; no --encode and no contact sheet come out of such a call)")
    ap.add_argument("--sky-report", metavar="FILE", help=argparse.SUPPRESS)     # internal: what a sky's process did
    ap.add_argument("--sky-skip", default="", metavar="ACTIONS", help=argparse.SUPPRESS)   # internal: actions left out
    ap.add_argument("--sky-guess", action="store_true", help=argparse.SUPPRESS)  # internal: --sky is from an old table
    return ap.parse_args(argv)


def variant_of(res, samples, step, motion_blur=True):
    """None for the final settings, else the preview directory name for these settings ('360x640_8spp_step4');
    motion blur switched off is a preview too ('..._nomb')."""
    res = tuple(res or FINAL_RES)
    samples = samples or FINAL_SAMPLES
    step = max(1, step or 1)
    if res == tuple(FINAL_RES) and samples == FINAL_SAMPLES and step == 1 and motion_blur:
        return None
    return "%dx%d_%dspp%s%s" % (res[0], res[1], samples, "_step%d" % step if step > 1 else "",
                                "" if motion_blur else "_nomb")


# project files that cannot change a rendered pixel: captions are composited at encode time, post / stamp / render
# only do bookkeeping (what they set on the scene is measured by the fingerprint), tools only inspect
# (engine/narration.py only reads times: what a film does with them is measured by the fingerprint)
NON_PIXEL = ("engine/captions.py", "engine/post.py", "engine/stamp.py", "engine/narration.py", "render.py")


def narration_files(name):
    """Project-relative paths of a film's narration files that exist (narration/<film>.json, .wav): they are
    sources of the film (its captions, cuts and length come from them)."""
    out = []
    for ext in (".json", ".wav"):
        rel = "narration/%s%s" % (name, ext)
        if os.path.exists(os.path.join(ROOT, rel)):
            out.append(rel)
    return out


def project_sources():
    """Project-relative paths of every .py file of this project that is loaded right now (the film script, the
    engine modules and whatever else they import): what the film as a whole (frames AND captions) depends on."""
    out = set()
    for mod in list(sys.modules.values()):
        f = getattr(mod, "__file__", None)
        if f and f.endswith(".py"):
            f = os.path.abspath(f)
            if f.startswith(ROOT + os.sep) and os.sep + "assets" + os.sep not in f:
                out.add(os.path.relpath(f, ROOT).replace(os.sep, "/"))
    out.add("render.py")
    return sorted(out)


def engine_sources():
    """The loaded project files whose code can change a pixel: everything except film scripts (films/: what they
    build is measured frame by frame by the scene fingerprint), tools/ and NON_PIXEL."""
    return [p for p in project_sources()
            if not p.startswith(("films/", "tools/")) and p not in NON_PIXEL]


def file_hash(rel):
    """Short sha1 of one project file ('<missing>' when it is gone)."""
    try:
        with open(os.path.join(ROOT, rel), "rb") as f:
            return hashlib.sha1(f.read()).hexdigest()[:12]
    except OSError:
        return "<missing>"


def source_hash(paths):
    """sha1 over the contents of project files (missing files hash as their name only)."""
    h = hashlib.sha1()
    for rel in sorted(paths):
        h.update(rel.encode())
        try:
            with open(os.path.join(ROOT, rel), "rb") as f:
                h.update(f.read())
        except OSError:
            h.update(b"<missing>")
    return h.hexdigest()


class SkyError(RuntimeError):
    """A frame was about to be rendered, stamped or judged in the build of another sky, or a film's sky table is
    not usable. Never caught inside render.py: a wrong sky must stop the command."""


def _module_statements(body):
    """Every statement that runs when a module is imported: its body and the bodies of the if / try / with / for /
    while / match statements in it (not those of functions and classes)."""
    for node in body:
        yield node
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            continue
        for field in ("body", "orelse", "finalbody"):
            sub = getattr(node, field, None)
            if isinstance(sub, list):
                yield from _module_statements(sub)
        for sub in list(getattr(node, "handlers", None) or []) + list(getattr(node, "cases", None) or []):
            yield from _module_statements(sub.body)


def _module_file(module, level, importer):
    """The project file an import statement in `importer` names ('films.x' -> films/x.py), or None when it is not
    a file of this project."""
    base = ROOT
    if level:
        base = os.path.dirname(importer)
        for _ in range(level - 1):
            base = os.path.dirname(base)
    rel = os.path.join(*module.split(".")) if module else ""
    for cand in (os.path.join(base, rel + ".py"), os.path.join(base, rel, "__init__.py")):
        cand = os.path.abspath(cand)
        if rel and os.path.isfile(cand) and cand.startswith(ROOT + os.sep):
            return cand
    return None


def _empty_literal(node):
    """True for the expressions `{}`, `None` and `dict()`: a SKIES bound to one of them declares no sky."""
    return (isinstance(node, ast.Dict) and not node.keys) or (isinstance(node, ast.Constant) and node.value is None) \
        or (isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "dict"
            and not node.args and not node.keywords)


def _source_binds(path, name, seen):
    """True when the Python source at `path` binds `name` to something other than an empty literal while it is
    imported: an assignment, or an import (named or star) that brings the name in; imports of project modules are
    followed. Read with `ast`: nothing is imported."""
    if path in seen or len(seen) > 64:
        return False
    seen.add(path)
    try:
        with open(path, encoding="utf-8") as f:
            tree = ast.parse(f.read(), path)
    except (OSError, SyntaxError, ValueError):
        return False                               # (building the film reports what is wrong with it)
    for node in _module_statements(tree.body):
        if isinstance(node, ast.Import):
            if any((a.asname or a.name) == name for a in node.names):
                return True
        elif isinstance(node, ast.ImportFrom):
            for a in node.names:
                if a.name != "*" and (a.asname or a.name) != name:
                    continue
                target = _module_file(node.module, node.level, path)
                if a.name == "*":
                    if target is not None and _source_binds(target, name, seen):
                        return True
                elif target is None or _source_binds(target, a.name, seen) \
                        or _module_file((node.module or "") + "." + a.name, node.level, path) is not None:
                    return True
        else:
            targets = node.targets if isinstance(node, ast.Assign) else \
                [node.target] if isinstance(node, (ast.AnnAssign, ast.AugAssign)) else []
            for t in targets:
                plain = isinstance(t, ast.Name) and t.id == name
                if plain and not isinstance(node, ast.AugAssign) and (node.value is None or _empty_literal(node.value)):
                    continue                       # `SKIES = {}`, `SKIES: dict`: no sky declared by this line
                if any(isinstance(x, ast.Name) and x.id == name for x in ast.walk(t)):
                    return True                    # (also `SKIES["night"] = ...` and `A, SKIES = ...`)
    return False


def declares_skies(name):
    """True when the source of films/<name>.py binds the name SKIES (to more than an empty literal) as the module is
    imported: an assignment at module level (also inside an if / try there) or an import that brings the name in,
    named or `from x import *` (project modules are followed). Such a film has several skies and is rendered sky by
    sky. Read with `ast`: nothing is imported, no Blender, a millisecond.

    This is only the FAST way to know. What decides is the imported module (Session.skies): a film whose SKIES no
    source line shows is handed over to the sky-by-sky path after its first build (_main_one), and a film whose
    source binds SKIES to something that turns out empty is rendered as the one-sky film it is."""
    return _source_binds(os.path.join(ROOT, "films", name + ".py"), "SKIES", set())


def _check_segments(segments, skies, frame_start, frame_end, where):
    """A film's sky table as [(first frame, last frame, sky), ...]: checked to cover frame_start..frame_end without a
    gap or an overlap, with known sky names."""
    try:
        segs = [(int(a), int(b), str(sky)) for a, b, sky in segments]
    except (TypeError, ValueError):
        raise SkyError("%s: the sky table must be [(first frame, last frame, sky name), ...], not %r"
                       % (where, segments)) from None
    if not segs:
        raise SkyError("%s: the sky table is empty" % where)
    edges = [frame_start] + [b + 1 for _a, b, _s in segs]
    if any(a != e or b < a for (a, b, _s), e in zip(segs, edges)) or segs[-1][1] != frame_end:
        raise SkyError("%s: the sky table %s does not cover the frames %d-%d exactly once"
                       % (where, segs, frame_start, frame_end))
    unknown = sorted({sky for _a, _b, sky in segs if sky not in skies})
    if unknown:
        raise SkyError("%s: the sky table names %s, SKIES has %s" % (where, unknown, sorted(skies)))
    return segs


def _sky_at(segments, frame):
    """Sky name of a frame in a table of (first, last, sky) segments; None outside the film."""
    for a, b, sky in segments:
        if a <= frame <= b:
            return sky
    return None


class Timeline:
    """The timeline of a film with several skies as meta.json (or a sky process's report) holds it: enough to turn
    seconds, shot names and frame ranges into frame numbers and a frame number into its sky, without building."""

    def __init__(self, data):
        self.fps = int(data["fps"])
        self.frame_start, self.frame_end = int(data["frame_start"]), int(data["frame_end"])
        self.shots = [types.SimpleNamespace(name=d["name"], frame_start=int(d["frame_start"]),
                                            frame_end=int(d["frame_end"])) for d in data.get("shots", [])]
        self.segments = [(int(a), int(b), str(sky)) for a, b, sky in data["sky_segments"]]
        self.captions = [(str(w), float(a), float(b)) for (w, a, b) in data.get("captions", [])]
        self.fades = [list(r) for r in data.get("fades", [])]
        self.base = data.get("base")
        self.skies = []                                           # in the order in which they first appear
        for _a, _b, sky in self.segments:
            if sky not in self.skies:
                self.skies.append(sky)

    def frame(self, seconds):
        """Frame number at a film time in seconds (second 0 = frame 1), as engine.shots.Film.frame."""
        return int(round(float(seconds) * self.fps)) + 1

    def seconds(self, frame):
        """Film time in seconds of a frame number."""
        return (frame - 1) / float(self.fps)

    def sky_of(self, frame):
        """Sky name of a frame (None outside the film)."""
        return _sky_at(self.segments, frame)

    def describe(self):
        """'gold 1-72, night 73-130, gold 131-216'."""
        return ", ".join("%s %d-%d" % (sky, a, b) for a, b, sky in self.segments)


class Session:
    """A built film inside the current Blender process. A film with several skies (a module-level SKIES) is built
    with ONE of them active (`sky`; default: its first): such a session fingerprints and renders only the frames
    that are tagged with that sky and raises SkyError for any other frame."""

    def __init__(self, name, sky=None, guess=False):
        """sky: the sky to build of a film with several (None: its first). guess=True: `sky` comes from an older
        sky table; if the film has no such sky (any more) its first sky is built, and a film with one sky is built
        as it is."""
        import bpy

        from engine import look, post

        self.bpy = bpy
        self.name = name
        t = time.time()
        bpy.ops.wm.read_factory_settings(use_empty=True)
        self.scene = bpy.context.scene
        look.setup_render(self.scene, res=FINAL_RES, samples=FINAL_SAMPLES, threads=FINAL_THREADS)
        module = importlib.import_module("films." + name)
        self.skies = dict(getattr(module, "SKIES", None) or {}) or None     # {name: settings}, or None: one sky
        self.sky = None                                                     # the sky this build has (None: one sky)
        self.segments = None                                                # [(first frame, last frame, sky), ...]
        if self.skies:
            if guess and sky not in self.skies:
                sky = None
            self.sky = sky or next(iter(self.skies))
            if self.sky not in self.skies:
                raise SkyError("film '%s' has no sky %r (SKIES: %s)" % (name, sky, ", ".join(self.skies)))
            result = module.build(self.scene, sky=self.sky)
        elif sky and not guess:
            raise SkyError("film '%s' has one sky (no SKIES in films/%s.py): it cannot be built as sky %r"
                           % (name, name, sky))
        else:
            result = module.build(self.scene)
        self.result = result                     # whatever else the film returned (look-dev: its Stage)
        self.film = result["film"]
        self.captions = [(str(w), float(a), float(b)) for (w, a, b) in result.get("captions", [])]
        scene = self.scene = self.film.scene
        if not scene.get("look_setup"):          # the film replaced the scene: apply the render settings again
            look.setup_render(scene, res=FINAL_RES, samples=FINAL_SAMPLES, threads=FINAL_THREADS)
        if scene.world is None:
            look.set_time(scene, "golden")
        if bpy.data.node_groups.get(look.COMP_GROUP) is None:
            look.setup_compositor(scene)
        if not any(m.name.startswith("shot_") for m in scene.timeline_markers):
            self.film.finalize()
        self.base = (scene.render.resolution_x, scene.render.resolution_y, scene.cycles.samples, scene.render.threads)
        self.base_motion_blur = bool(scene.render.use_motion_blur)
        self._fp = None
        stage = result.get("stage")
        # dips to black: picture-gain ramps for the encoder (engine/post.py), never part of a frame's stamp
        self.fades = post.check_fades(result["fades"] if "fades" in result else getattr(stage, "fades", None))
        if self.skies:
            where = "films/%s.py" % name
            active = result.get("sky", getattr(stage, "sky_name", None))
            if active != self.sky:
                raise SkyError("%s was asked to build sky %r but reports %r as its active sky: hand build()'s `sky` "
                               "argument on (Stage(scene, film, v, skies=SKIES, sky=sky))" % (where, self.sky, active))
            table = result.get("sky_segments")
            if table is None and hasattr(stage, "sky_segments"):
                table = stage.sky_segments()
            if table is None:
                raise SkyError("%s declares SKIES but returns no sky table: return the Stage as 'stage' (shots tagged "
                               "with Stage.shot(name, seconds, sky=...)) or 'sky_segments'" % where)
            self.segments = _check_segments(table, self.skies, self.film.frame_start, self.film.frame_end, where)
        print(f"[render] built '{name}'{' [sky %s]' % self.sky if self.sky else ''} in {time.time() - t:.1f}s: "
              f"frames {self.film.frame_start}-{self.film.frame_end} "
              f"({self.film.duration:.2f} s at {self.film.fps} fps), {len(self.film.shots)} shots, "
              f"{len(self.captions)} caption words, {self._face_count()} faces")

    def _face_count(self):
        return sum(len(o.data.polygons) for o in self.scene.objects if o.type == "MESH")

    def sky_of(self, frame):
        """Name of the sky a frame is tagged with (None: a film with one sky, or a frame outside the film)."""
        return _sky_at(self.segments, frame) if self.segments else None

    def owns(self, frame):
        """True when this build may fingerprint and render the frame: always for a film with one sky, else only
        when the frame is tagged with the sky this session was built with."""
        return self.skies is None or self.sky_of(frame) == self.sky

    def require(self, frame, what="handle"):
        """Raise SkyError unless this build owns the frame (see owns)."""
        if not self.owns(frame):
            raise SkyError("frame %s of '%s' is filmed under sky %r: it cannot be %s in the build of sky %r (use "
                           "render.session_for(%r, %s), or render.Session(%r, sky=%r))"
                           % (frame, self.name, self.sky_of(frame), what, self.sky, self.name, frame, self.name,
                              self.sky_of(frame)))

    def meta(self):
        """Everything post needs to encode without Blender, plus what the frames depend on."""
        f = self.film
        # (a module that builds one part of a narrated film returns the whole film's Narration as "narration")
        nar = self.result.get("narration")
        spoken = set(narration_files(self.name)) | set(narration_files(getattr(nar, "film", None) or self.name))
        sources = sorted(set(project_sources()) | spoken)
        meta = {
            "film": self.name, "fps": f.fps, "frame_start": f.frame_start, "frame_end": f.frame_end,
            "captions": [list(c) for c in self.captions],
            "shots": [{"name": s.name, "frame_start": s.frame_start, "frame_end": s.frame_end} for s in f.shots],
            "sources": sources, "source_hash": source_hash(sources),
        }
        if self.fades:                           # (a film without fades has the meta.json it always had)
            meta["fades"] = [list(r) for r in self.fades]
        if self.skies:
            # the whole film's sky table, the same from every sky's build: what a process without Blender needs to
            # know which sky a frame belongs to and with which settings its frames are stamped
            for d in meta["shots"]:
                d["sky"] = self.sky_of(d["frame_start"])
            meta["skies"] = json.loads(json.dumps(self.skies, default=str))
            meta["sky_segments"] = [list(seg) for seg in self.segments]
            meta["base"] = [self.base[0], self.base[1], self.base[2], int(self.base_motion_blur)]
        return meta

    def settings_key(self):
        """The render settings a frame is stamped with: '720x1280|24spp|mb1'."""
        r, c = self.scene.render, self.scene.cycles
        return "%dx%d|%dspp|mb%d" % (r.resolution_x, r.resolution_y, c.samples, int(r.use_motion_blur))

    def engine_files(self):
        """{project path: short hash} of the loaded sources that can change a pixel (see engine_sources)."""
        return {p: file_hash(p) for p in engine_sources()}

    def fingerprint(self, frame):
        """Scene fingerprint of a frame at the current settings: {'fp': hex, 'parts': {...}} (engine/stamp.py).
        Only for frames of this build's own sky (SkyError otherwise)."""
        from engine import stamp

        self.require(frame, "fingerprinted")
        if self._fp is None:
            self._fp = stamp.Fingerprinter(self.scene, self.film)
        return self._fp.frame(frame)

    def configure(self, res=None, samples=None, threads=None, motion_blur=None):
        """Set resolution / samples / threads for the next renders (None = keep the film's own value)."""
        r = self.scene.render
        r.resolution_x, r.resolution_y = res or self.base[:2]
        r.resolution_percentage = 100
        self.scene.cycles.samples = samples or self.base[2]
        self.scene.cycles.adaptive_min_samples = max(4, self.scene.cycles.samples // 3)
        r.threads_mode = "FIXED"
        r.threads = threads or self.base[3]
        if motion_blur is not None:
            r.use_motion_blur = motion_blur
        if self._fp is not None:
            self._fp.reset()                      # the settings are part of every fingerprint

    def render_frame(self, frame, path):
        """Render one frame number to a PNG path (atomic: written under a temporary name first). Only for frames
        of this build's own sky (SkyError otherwise)."""
        scene = self.scene
        self.require(frame, "rendered")
        self.film.goto(frame)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        tmp = path[:-4] + "_part"
        scene.render.filepath = tmp
        scene.render.use_file_extension = True
        self.bpy.ops.render.render(write_still=True)
        os.replace(tmp + ".png", path)
        return path


def _ranges(frames):
    """[1, 2, 3, 7, 9, 10] -> '1-3, 7, 9-10'."""
    out, frames = [], sorted(frames)
    i = 0
    while i < len(frames):
        j = i
        while j + 1 < len(frames) and frames[j + 1] == frames[j] + 1:
            j += 1
        out.append(str(frames[i]) if i == j else "%d-%d" % (frames[i], frames[j]))
        i = j + 1
    return ", ".join(out)


class Stamps:
    """The frame bookkeeping of one frame directory (final, or one preview variant) for a built film: which PNGs on
    disk are still frames of the film, and why the others are not (see the module docstring).

    For a film with several skies the directory and its meta.json are shared by all of them, and this object is the
    book of ONE sky's build: it judges, stamps and expects fingerprints only for the frames its session owns
    (SkyError for any other frame) and carries the other skies' stamps and expectations through untouched. Their
    expectations ('current') are kept only while no source changed since they were written; otherwise they are
    dropped, and those frames count as not judged until their own sky's build has judged them again."""

    def __init__(self, ses, name, variant):
        from engine import post, stamp

        self.ses, self.name, self.variant = ses, name, variant
        self.post, self.stamp = post, stamp
        old = post.read_meta(name, variant) or {}
        self.frames = {k: v for k, v in old.get("frames", {}).items() if isinstance(v, dict)}
        self.engines = {k: v for k, v in old.get("engines", {}).items() if isinstance(v, dict)}
        r = ses.scene.render
        self.size = (r.resolution_x, r.resolution_y)
        self.s = ses.settings_key()
        self.files = ses.engine_files()
        self.e = hashlib.sha1(repr(sorted(self.files.items())).encode()).hexdigest()[:12]
        self.engines[self.e] = self.files
        self.meta = ses.meta()
        cur = old.get("current") or {}
        # the fingerprints of the last run are still right when no source at all changed since (the build is
        # deterministic): a chunked render then spends nothing on re-checking the frames it already has
        trusted = (old.get("source_hash") == self.meta["source_hash"] and cur.get("s") == self.s
                   and cur.get("e") == self.e and cur.get("v") == stamp.VERSION)
        self.cur_fp = dict(cur.get("fp", {})) if trusted else {}
        if trusted and ses.skies:
            # no source changed since another build wrote this meta.json: that build (whatever its sky) must have
            # produced the same film. If it did not, the film's build() makes something depend on the active sky.
            for key in ("fps", "frame_start", "frame_end", "shots", "sky_segments", "captions", "fades"):
                mine = json.loads(json.dumps(self.meta.get(key)))
                if old.get(key) != mine:
                    raise SkyError(
                        "film '%s': the build of sky %r gives another %r than the build that wrote %s did, although "
                        "no source file changed. The timeline, the captions and the fades must be the same whichever "
                        "sky is active: only Stage(..., sky=sky) may depend on build()'s `sky` argument."
                        % (name, ses.sky, key, os.path.join(post.frames_dir(name, variant), "meta.json")))
        self.on_disk = set(post.existing_frames(name, variant))
        self._status = {}

    def fp(self, frame):
        """Current scene fingerprint of a frame (computed once; only for frames of this build's own sky)."""
        self.ses.require(frame, "fingerprinted")
        k = str(frame)
        if k not in self.cur_fp:
            self.cur_fp[k] = self.ses.fingerprint(frame)["fp"]
        return self.cur_fp[k]

    def status(self, frame):
        """'valid' | 'missing' | 'unstamped' | 'size' | 'settings' | 'scene' | 'engine' | 'engine+scene' | 'sky'.
        'engine' = rendered with other engine sources but the scene fingerprint is unchanged (re-stampable);
        'scene' = this frame's own content changed (film edit); 'engine+scene' = both; 'sky' = a changed scene whose
        stamp names another sky: the PNG was rendered under another sky (the shot was tagged with another sky
        since). What a sky IS (world, key light, sky sprites, stars, clouds, haze, grade) is in the fingerprint; its
        NAME in SKIES is a label: a stamp whose fingerprint is current is valid under whatever name it was rendered
        (a renamed sky costs nothing) and gets this build's name. Only for frames of this build's own sky."""
        self.ses.require(frame, "judged")
        st = self._status.get(frame)
        if st is None:
            st = self._status[frame] = self._judge(frame)
        return st

    def _judge(self, frame):
        from PIL import Image

        if frame not in self.on_disk:
            return "missing"
        rec = self.frames.get(str(frame))
        if rec is None:
            return "unstamped"
        try:
            with Image.open(self.post.frame_path(self.name, frame, self.variant)) as im:
                if tuple(im.size) != tuple(self.size):
                    return "size"
        except OSError:
            return "missing"
        if rec.get("s") != self.s:
            return "settings"
        same = rec.get("fp") == self.fp(frame)
        if rec.get("e") != self.e:                    # (whatever the stamp's sky: other_engine() must agree with this)
            return "engine" if same else "engine+scene"
        if not same:
            return "sky" if self.foreign(frame) else "scene"
        if rec.get("sky") != self.ses.sky:
            # the picture is this build's, proven by its fingerprint: an older stamp without a sky, or the sky was
            # renamed in SKIES since (in a film that has one sky now, the label goes)
            if self.ses.sky is None:
                rec.pop("sky", None)
            else:
                rec["sky"] = self.ses.sky
        return "valid"

    def foreign(self, frame):
        """The sky a frame's stamp names when that is another one than this build's (None otherwise). Such a PNG
        is this frame's picture only if its fingerprint says so (status 'valid' / 'engine'); it is never accepted
        on the director's word (--restamp-changed)."""
        sky = (self.frames.get(str(frame)) or {}).get("sky")
        return sky if sky is not None and sky != self.ses.sky else None

    def other_engine(self, frame):
        """True when a frame's PNG (of ANY sky) was rendered with these settings but other engine sources: what
        stops --frames with exit code 3. It needs no fingerprint and no build of the frame's own sky: the stamp
        names the engine sources, and they are the same files whichever sky is active."""
        from PIL import Image

        rec = self.frames.get(str(frame))
        if frame not in self.on_disk or rec is None or rec.get("s") != self.s or rec.get("e") == self.e:
            return False
        try:
            with Image.open(self.post.frame_path(self.name, frame, self.variant)) as im:
                return tuple(im.size) == tuple(self.size)
        except OSError:
            return False

    def mark(self, frame, fingerprint=None):
        """Stamp a frame as rendered (or accepted) with the current settings, engine and fingerprint (and, in a
        film with several skies, the sky it was rendered under: only this build's own)."""
        self.ses.require(frame, "stamped")
        d = fingerprint or self.ses.fingerprint(frame)
        self.cur_fp[str(frame)] = d["fp"]
        self.frames[str(frame)] = {"s": self.s, "e": self.e, "fp": d["fp"], "parts": d["parts"]}
        if self.ses.sky is not None:
            self.frames[str(frame)]["sky"] = self.ses.sky
        self.on_disk.add(frame)
        self._status[frame] = "valid"

    def changed_files(self, frames):
        """Engine files that differ between the sources the given frames were rendered with and the current ones."""
        out = set()
        for f in frames:
            was = self.engines.get((self.frames.get(str(f)) or {}).get("e"))
            if was is None:
                out.add("(unknown: no record of those sources)")
                continue
            out.update(p for p in set(was) | set(self.files) if was.get(p) != self.files.get(p))
        return sorted(out)

    def why_scene(self, frames):
        """What changed in the scene of the given stale frames ('camera, lights'), from their stored parts."""
        seen = []
        for f in frames:
            old = (self.frames.get(str(f)) or {}).get("parts")
            w = self.stamp.explain(old, self.ses.fingerprint(f)["parts"])
            if w not in seen:
                seen.append(w)
        return "; ".join(seen)

    def shots_of(self, frames):
        """Names of the shots that own the given frames, in film order."""
        names = []
        for f in sorted(frames):
            n = self.ses.film.shot_at(f).name
            if n not in names:
                names.append(n)
        return ", ".join(names)

    def save(self):
        """Write meta.json: film data for the encoder, every stamp, and the CURRENT expectation per frame, which is
        what post.valid_frames() compares the stamps with (so post needs no Blender)."""
        r = self.ses.scene.render
        used = {rec.get("e") for rec in self.frames.values()} | {self.e}
        meta = dict(self.meta)
        meta.update(res=[r.resolution_x, r.resolution_y], samples=self.ses.scene.cycles.samples, variant=self.variant,
                    frames=self.frames, engines={k: v for k, v in self.engines.items() if k in used},
                    current={"v": self.stamp.VERSION, "s": self.s, "e": self.e, "fp": self.cur_fp})
        self.post.write_meta(self.name, meta, self.variant)


def _frame_list(spec, film, step):
    """Frame numbers for 'all', 'A-B', a single frame or a shot name (clamped to the film, every step-th)."""
    spec = spec.strip()
    shot = next((s for s in film.shots if s.name == spec), None)
    if spec.lower() == "all":
        a, b = film.frame_start, film.frame_end
    elif shot is not None:
        a, b = shot.frame_start, shot.frame_end
    elif "-" in spec:
        a, b = (int(x) for x in spec.split("-", 1))
    else:
        a = b = int(spec)
    a, b = max(a, film.frame_start), min(b, film.frame_end)
    return list(range(a, b + 1, max(1, step)))


def _meta_is_fresh(name, variant=None):
    """True when meta.json exists and none of the source files it lists (film script, engine modules, ...) changed
    since it was written: --encode alone may then reuse it without rebuilding the film."""
    from engine import post

    meta = post.read_meta(name, variant)
    if not meta or not meta.get("sources") or not meta.get("source_hash"):
        return False
    if any(rel not in meta["sources"] for rel in narration_files(name)):
        return False                              # a narration was spoken after this meta was written
    return source_hash(meta["sources"]) == meta["source_hash"]


SKY_ACTIONS = ("still", "sheet", "restamp", "prune", "frames", "blend", "encode")


def _encode_action(args, name, variant, started):
    """--encode: the frames of meta.json -> mp4 (+ narration). Returns the exit code (0, 2 refused, 4 not finished)."""
    from engine import post

    meta = post.read_meta(name, variant)
    audio = None if args.no_audio else args.audio
    if audio is None and not args.no_audio:
        # the film's own narration, if it has one: checked against the film's text before it is used
        from engine import narration

        audio, problem = narration.encode_check(name)
        if audio is not None and problem is None:
            nar = narration.load(name, fps=meta["fps"])
            n = meta["frame_end"] - meta["frame_start"] + 1
            if nar.words and nar.words[-1].end > n / float(meta["fps"]) + 1e-6:
                problem = ("the film is %d frames (%.2f s) long but its narration's last word ends at %.2f s: "
                           "build the film to nar.frames (%d)" % (n, n / float(meta["fps"]), nar.words[-1].end, nar.frames))
        if problem:
            print("[render] encode refused:", problem)
            return 2
    fades = meta.get("fades") or None            # dips to black: picture-gain ramps (engine/post.py)
    try:
        if meta["frame_end"] - meta["frame_start"] + 1 > post.SEGMENT_OVER:
            # a long film: in parts, resumable (see "Long films" in the module docstring)
            mp4 = post.encode_parts(name, captions=[tuple(c) for c in meta["captions"]], fps=meta["fps"],
                                    frame_start=meta["frame_start"], frame_end=meta["frame_end"], audio=audio,
                                    variant=variant, allow_holds=args.allow_holds,
                                    deadline=started + min(args.max_seconds or ENCODE_SECONDS, ENCODE_SECONDS),
                                    first_always=not args.frames,   # (a call that rendered frames first has
                                    fades=fades)                    #  no time left to owe a part)
            if mp4 is None:
                print("[render] encode not finished: run the same command again (exit code 4)")
                return 4
        else:
            mp4 = post.encode(name, captions=[tuple(c) for c in meta["captions"]], fps=meta["fps"],
                              frame_start=meta["frame_start"], frame_end=meta["frame_end"], audio=audio,
                              variant=variant, allow_holds=args.allow_holds, fades=fades)
    except RuntimeError as e:
        print("[render] encode refused:", e)
        return 2
    print("[render] video:", post.probe(mp4))
    if audio:
        print("[render] audio:", post.probe_audio(mp4))
    return 0


def _sheet_frames(film, n):
    """The frame numbers of a contact sheet of n evenly spaced tiles."""
    total = film.frame_end - film.frame_start + 1
    return [film.frame_start + min(total - 1, int((i + 0.5) * total / n)) for i in range(n)]


def _still_frame(film, s):
    """Frame number of --still S (clamped to the film)."""
    return min(film.frame_end, max(film.frame_start, film.frame(float(s))))


def main(argv=None):
    """Entry point of `python -m render`."""
    started = time.time()
    argv = list(sys.argv[1:] if argv is None else argv)
    args = _parse_args(argv)
    if args.sky is None and declares_skies(args.film):
        return _main_skies(args, argv, started)          # several skies: one process per sky, see the docstring
    return _main_one(args, started, argv)


def _main_one(args, started, argv=()):
    """One process, one build: a film with one sky, or (--sky) one sky's share of a film with several."""
    from PIL import Image

    from engine import captions as cap
    from engine import post

    name = args.film
    worker = args.sky is not None                 # this process does ONE sky of a film with several
    skip = {a for a in args.sky_skip.split(",") if a}
    stills = [s.strip() for chunk in args.still for s in chunk.split(",") if s.strip()]
    # final frames and previews never share a directory (see the module docstring)
    variant = variant_of(args.res, args.samples, args.step, not args.no_motion_blur)
    needs_build = bool(stills or args.frames or args.sheet or args.save_blend or args.restamp or args.prune_stale
                       or worker or (args.encode and not _meta_is_fresh(name, variant)))
    if not (needs_build or args.encode):
        print("nothing to do: give --still, --frames, --sheet, --encode, --restamp, --prune-stale or --save-blend")
        return 1
    if not needs_build and (post.read_meta(name, variant) or {}).get("sky_segments"):
        # --encode alone, no source changed since a build with several skies wrote this meta.json: the film HAS
        # several skies (whatever its source shows), and its frames are judged sky by sky
        return _main_skies(args, list(argv), started)

    ses = None
    one_sky = False                               # asked for as a sky's process, found to be a film with one sky
    if needs_build:
        ses = Session(name, sky=args.sky or None, guess=args.sky_guess)
        if worker and not ses.skies:
            if args.sky and not args.sky_guess:
                raise SkyError("--sky: films/%s.py has no SKIES (a film with one sky is rendered without --sky)" % name)
            # the source binds the name SKIES, the module has none (it is empty): a film with one sky. What decides
            # is the module: this process does the whole job, exactly as for any film with one sky
            worker, skip, one_sky = False, set(), True
        elif not worker and ses.skies:
            # no line of the source showed it (declares_skies), the imported module has SKIES: several skies after
            # all. What decides is the module: the film is rendered sky by sky, one process each
            print(f"[render] films/{name}.py has SKIES ({', '.join(ses.skies)}), though no line of its source binds that "
                  f"name: rendered sky by sky all the same. (Write `SKIES = ...` or `from x import SKIES` at module "
                  f"level and no command builds the film this one extra time.)", flush=True)
            ses.bpy.ops.wm.read_factory_settings(use_empty=True)        # (this build is not used: free it)
            return _main_skies(args, list(argv), started)
    mb = False if args.no_motion_blur else None
    test_dir = os.path.join(post.OUT, "test")
    sky = ses.sky if ses is not None else None
    tag = "sky '%s': " % sky if worker else ""
    # what this sky's process did, for the process that runs the skies one after the other (_main_skies)
    report = {"sky": sky, "code": 0, "stills_done": [], "stills_other": {}, "sheet": None, "frames": None,
              "one_sky": one_sky}
    if worker:
        report["timeline"] = ses.meta()

    def finish(code):
        report["code"] = code
        if args.sky_report:
            with open(args.sky_report + ".part", "w", encoding="utf-8") as fh:
                json.dump(report, fh)
            os.replace(args.sky_report + ".part", args.sky_report)
        return code

    # ---- stills
    if stills and "still" not in skip:
        ses.configure(args.res or STILL_RES, args.samples or STILL_SAMPLES, args.threads or STILL_THREADS, mb)
        for s in stills:
            frame = _still_frame(ses.film, s)
            if not ses.owns(frame):               # another sky's frame: that sky's process renders it
                report["stills_other"][s] = ses.sky_of(frame)
                if not args.sky_report:
                    print(f"[render] {tag}still {s}s = frame {frame} is filmed under sky '{ses.sky_of(frame)}': not rendered here")
                continue
            path = os.path.join(test_dir, f"{name}_{s}.png")
            t = time.time()
            ses.render_frame(frame, path)
            shot = ses.film.shot_at(frame)
            print(f"[render] still {s}s = frame {frame} (shot '{shot.name}'{', sky ' + sky if sky else ''}) -> {path}  "
                  f"{time.time() - t:.1f}s")
            report["stills_done"].append(s)
            if args.captioned:
                word = cap.caption_at(ses.captions, ses.film.seconds(frame))
                with Image.open(path) as im:
                    capped = post.finish_frame(im, word, gain=post.fade_gain(ses.fades, ses.film.seconds(frame)))
                capped.save(path[:-4] + "_cap.png")
                print(f"[render]   caption {word!r} -> {path[:-4]}_cap.png")
            if args.zones:
                with Image.open(path) as im:
                    post.draw_zones(im).save(path[:-4] + "_zones.png")
                print(f"[render]   zones -> {path[:-4]}_zones.png")

    # ---- contact sheet
    if args.sheet and "sheet" not in skip:
        n = max(1, args.sheet)
        ses.configure(args.res or SHEET_RES, args.samples or SHEET_SAMPLES, args.threads or STILL_THREADS, mb)
        tiles, labels, words, gains = [], [], [], []
        tmp = os.path.join(test_dir, f"{name}_sheet_tile.png")
        t0 = time.time()
        kept = {}                                 # a sky's process keeps its tiles; the sheet is put together later
        for i, frame in enumerate(_sheet_frames(ses.film, n)):
            sec = ses.film.seconds(frame)
            labels.append("%.2fs %s" % (sec, ses.film.shot_at(frame).name))
            words.append(cap.caption_at(ses.captions, sec))
            gains.append(post.fade_gain(ses.fades, sec))
            if not ses.owns(frame):
                continue
            if worker and args.sky_report:
                tmp = "%s.tile_%03d.png" % (args.sky_report, i)
                kept[str(i)] = tmp
            ses.render_frame(frame, tmp)
            with Image.open(tmp) as im:
                tiles.append(im.convert("RGB"))
            print(f"[render] {tag}sheet tile {i + 1}/{n}: frame {frame}  ({time.time() - t0:.1f}s elapsed)")
        if worker:
            report["sheet"] = {"n": n, "labels": labels, "words": words, "gains": gains, "tiles": kept}
            if not args.sky_report:
                if os.path.exists(tmp):
                    os.remove(tmp)
                print(f"[render] {tag}{len(tiles)} of the {n} sheet tiles are this sky's; the sheet itself is made by "
                      f"the command without --sky")
        else:
            if os.path.exists(tmp):
                os.remove(tmp)
            path = post.contact_sheet(tiles, labels, words, os.path.join(test_dir, f"{name}_sheet.png"),
                                      gains=gains if ses.fades else None)
            print(f"[render] sheet -> {path}")

    # ---- frames
    book = None
    do_frames = bool(args.frames) and "frames" not in skip
    do_restamp = bool(args.restamp) and "restamp" not in skip
    do_prune = args.prune_stale and "prune" not in skip
    do_judge = args.encode and ses is not None and "encode" not in skip
    if do_frames or do_restamp or do_prune or do_judge:
        ses.configure(args.res, args.samples, args.threads or FINAL_THREADS, mb)
        r = ses.scene.render
        book = Stamps(ses, name, variant)
        where = "%s (%s)" % (post.frames_dir(name, variant), "FINAL" if variant is None else "preview " + variant)

    if do_restamp:
        # accept frames without rendering: by default only those whose picture is provably the same (same settings,
        # same scene fingerprint, other engine sources); --restamp-changed accepts whatever PNG of the right size is there
        targets = [f for f in _frame_list(args.restamp, ses.film, args.step) if ses.owns(f)]
        take, refuse, alien = [], [], {}
        for f in targets:
            st = book.status(f)
            was = book.foreign(f)
            if st == "engine" or (args.restamp_changed and not was and st in ("engine+scene", "scene", "unstamped", "settings")):
                take.append(f)                    # ('engine': the fingerprint proves the picture, under any sky name)
            elif was and st not in ("valid", "missing"):
                alien.setdefault(was, []).append(f)       # another sky's picture: never kept on the director's word
            elif st not in ("valid", "missing"):
                refuse.append(f)
        for f in take:
            book.mark(f)
        print(f"[render] {tag}restamp -> {where}: {len(take)} frames re-stamped without rendering"
              + (f" ({_ranges(take)})" if take else "")
              + (f"; {len(refuse)} NOT accepted, their scene changed or they have no usable stamp ({_ranges(refuse)}): "
                 f"render them, or pass --restamp-changed to keep them anyway" if refuse else "")
              + (f"; {sum(len(v) for v in alien.values())} NOT accepted, rendered under another sky ("
                 + "; ".join(f"{_ranges(v)}: was '{k}'" for k, v in alien.items())
                 + f", now '{ses.sky}'): they are not these frames' picture, render them" if alien else ""))
        book.save()

    if do_prune:
        f_end = ses.film.frame_end
        # (a sky's process leaves the other skies' frames alone; PNGs beyond the film belong to no sky and go)
        gone = [f for f in sorted(book.on_disk) if f > f_end or f < ses.film.frame_start
                or (ses.owns(f) and book.status(f) != "valid")]
        for f in gone:
            try:
                os.remove(post.frame_path(name, f, variant))
            except OSError:
                pass
            book.frames.pop(str(f), None)
            book.cur_fp.pop(str(f), None)
            book.on_disk.discard(f)
            book._status.pop(f, None)
        kept_n = len(book.on_disk) if not worker else sum(1 for f in book.on_disk if ses.owns(f))
        print(f"[render] {tag}prune -> {where}: {len(gone)} stale PNGs deleted" + (f" ({_ranges(gone)})" if gone else "")
              + f", {kept_n} valid frames kept")
        book.save()

    if do_frames:
        wanted = _frame_list(args.frames, ses.film, args.step)
        frames = [f for f in wanted if ses.owns(f)]          # (all of them in a film with one sky)
        status = {f: book.status(f) for f in frames}
        by_engine = [f for f in frames if status[f] in ("engine", "engine+scene")]
        by_scene = [f for f in frames if status[f] == "scene"]
        other = [f for f in frames if status[f] in ("unstamped", "size", "settings")]
        by_sky = {}                                          # {the sky their PNG was rendered under: frames}
        for f in frames:
            if status[f] == "sky":
                by_sky.setdefault(book.foreign(f), []).append(f)
        todo = [f for f in frames if args.force or status[f] != "valid"]
        # frames of the OTHER skies that were rendered with other engine sources stop this sky too: nothing of the
        # film is rendered before every sky's frames were looked at (their stamps name the engine; see other_engine)
        elsewhere = {}
        for f in wanted:
            if not ses.owns(f) and book.other_engine(f):
                elsewhere.setdefault(ses.sky_of(f), []).append(f)
        report["frames"] = {"requested": len(frames), "done_before": len(frames) - len(todo), "rendered": 0,
                            "left": len(todo), "seconds": 0.0, "engine_stop": False,
                            "elsewhere": {k: len(v) for k, v in elsewhere.items()},
                            "res": [r.resolution_x, r.resolution_y], "samples": ses.scene.cycles.samples,
                            "threads": r.threads}
        print(f"[render] {tag}frames -> {where}")
        if (by_engine or elsewhere) and not (args.rerender_stale or args.force):
            same = [f for f in by_engine if status[f] == "engine"]
            diff = [f for f in by_engine if status[f] == "engine+scene"]
            if by_engine:
                print(f"[render] {tag}STOPPED, nothing rendered: {len(by_engine)} of the {len(frames)} requested frames were "
                      f"rendered with other engine sources. Changed since: {', '.join(book.changed_files(by_engine))}")
            else:
                print(f"[render] {tag}STOPPED, nothing rendered: frames of another sky were rendered with other engine "
                      f"sources (" + "; ".join("sky '%s': %d (%s)" % (k, len(v), _ranges(v)) for k, v in elsewhere.items())
                      + "). Changed since: " + ", ".join(book.changed_files([f for v in elsewhere.values() for f in v])))
            if same:
                print(f"[render]   {len(same)} of them show an unchanged scene ({_ranges(same)}): the edit altered no "
                      f"picture there; keep them with  --restamp {args.frames}")
            if diff:
                print(f"[render]   {len(diff)} have a changed scene ({_ranges(diff)}; shots: {book.shots_of(diff)}; "
                      f"changed: {book.why_scene(diff[:1] + diff[-1:])})")
            print("[render]   --rerender-stale renders all of them again. (exit code 3)")
            book.save()
            report["frames"]["engine_stop"] = True
            return finish(3)
        if worker:
            # (never the words "0 to render" here: they are the whole FILM's, said by the process that ran every sky)
            print(f"[render] {tag}{len(frames)} frames requested, {len(frames) - len(todo)} already done, "
                  + (f"{len(todo)} to render" if todo else "none to render")
                  + f" at {r.resolution_x}x{r.resolution_y}, {ses.scene.cycles.samples} samples, {r.threads} threads")
        else:
            print(f"[render] frames: {len(frames)} requested, {len(frames) - len(todo)} already done, {len(todo)} to render "
                  f"at {r.resolution_x}x{r.resolution_y}, {ses.scene.cycles.samples} samples, {r.threads} threads")
        if by_scene:
            print(f"[render]   {len(by_scene)} stale: their scene changed ({_ranges(by_scene)}; shots: "
                  f"{book.shots_of(by_scene)}; changed: {book.why_scene(by_scene[:1] + by_scene[-1:])})")
        if by_engine:
            print(f"[render]   {len(by_engine)} stale: engine sources changed "
                  f"({', '.join(book.changed_files(by_engine))}); rendered again (--rerender-stale)")
        if other:
            print(f"[render]   {len(other)} stale: other settings, another size or no stamp ({_ranges(other)})")
        if by_sky:
            # (a name SKIES no longer has: the sky was renamed AND its frames' scene differs, e.g. a value of the
            #  sky changed too; the fingerprint parts say what)
            print(f"[render]   {sum(len(v) for v in by_sky.values())} stale: rendered under another sky ("
                  + "; ".join(f"{_ranges(v)}: was '{k}'" + ("" if k in ses.skies else ", a name SKIES no longer has")
                              for k, v in by_sky.items()) + f", now '{ses.sky}'; changed: "
                  + book.why_scene([f for v in by_sky.values() for f in (v[0], v[-1])]) + ")")
        book.save()
        t0 = time.time()
        done = 0
        for f in todo:
            if args.max_seconds and done and time.time() - t0 > args.max_seconds:
                print(f"[render] {tag}stopping after {time.time() - t0:.0f}s (--max-seconds); {len(todo) - done} frames left, "
                      f"re-run the same command to resume")
                break
            t = time.time()
            fingerprint = ses.fingerprint(f)                 # what this frame shows, taken as it is rendered
            ses.render_frame(f, post.frame_path(name, f, variant))
            book.mark(f, fingerprint)
            book.save()                                      # stamped only once the PNG is complete
            done += 1
            avg = (time.time() - t0) / done
            print(f"[render] frame {f:4d}  {time.time() - t:5.1f}s  ({done}/{len(todo)}, avg {avg:.1f}s, "
                  f"ETA {avg * (len(todo) - done) / 60.0:.1f} min)", flush=True)
        if done:
            print(f"[render] {tag}{done} frames in {time.time() - t0:.1f}s = {(time.time() - t0) / done:.2f} s/frame")
        report["frames"].update(rendered=done, left=len(todo) - done, seconds=time.time() - t0)

    if book is not None and do_judge:
        # the encoder trusts meta.json: judge every frame of the film against the scene as it is built now
        every = [f for f in range(ses.film.frame_start, ses.film.frame_end + 1) if ses.owns(f)]
        states = [book.status(f) for f in every]
        book.save()
        n_engine = sum(st in ("engine", "engine+scene") for st in states)
        if n_engine:
            keep = states.count("engine")
            print(f"[render] {tag}encode: {n_engine} frames on disk were rendered with other engine sources "
                  f"({', '.join(book.changed_files(every))}); "
                  f"{keep} of them show an unchanged scene and can be kept with --restamp all")

    # ---- blend
    if args.save_blend and "blend" not in skip:
        bpy = ses.bpy
        path = os.path.join(post.OUT, "blend", name + (".%s" % sky if worker else "") + ".blend")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        # the file carries the FINAL render settings, whatever --still / --sheet / --frames used before in this call
        ses.configure(None, None, FINAL_THREADS, ses.base_motion_blur)
        first = ses.film.frame_start if not worker else next(a for a, _b, k in ses.segments if k == sky)
        ses.film.goto(first)
        try:
            bpy.ops.file.pack_all()
        except RuntimeError as e:
            print("[render] pack_all:", e)
        try:
            bpy.context.preferences.filepaths.save_version = 0     # no <film>.blend1 backup beside it
        except (AttributeError, TypeError):
            pass
        bpy.ops.wm.save_as_mainfile(filepath=path, compress=True)
        if os.path.exists(path + "1"):
            os.remove(path + "1")
        r = ses.scene.render
        print(f"[render] blend -> {path} ({os.path.getsize(path) / 1e6:.1f} MB; {r.resolution_x}x{r.resolution_y}, "
              f"{ses.scene.cycles.samples} samples)")

    # ---- encode
    if worker:
        if args.encode and not args.sky_report:
            print(f"[render] {tag}this sky's frames are judged; the film is encoded by the command without --sky")
        return finish(0)
    if args.encode:
        return finish(_encode_action(args, name, variant, started))
    return finish(0)


# --------------------------------------------------------------------------------------------------------------
# a film with several skies: one process per sky
# --------------------------------------------------------------------------------------------------------------

class Plan:
    """What meta.json says about the frames of a film with several skies, read WITHOUT building anything.

    usable = no source file of the film changed since a sky's build wrote it, and it was written for the settings of
    this call: the sky table is then the film's, and what it holds about a frame is that frame's judgment against
    its own sky's build (only such a build can write it: see Stamps). status(frame):
      'valid'     the PNG is there, has the right size, and its stamp is what its own sky's build expects now
      'unjudged'  there is a PNG with a stamp, but no build of its sky has judged it since the sources changed
                  (or its stamp still carries another sky's name: its sky's build relabels or rejects it)
      'stale'     judged, and not the film any more (or no stamp, or another size)
      'missing'   no PNG
    A Plan is only ever asked while the sky table is the film's own (see _main_skies: never a table from before
    an edit)."""

    def __init__(self, name, variant, args):
        from engine import post

        self.name, self.variant, self.post = name, variant, post
        self.meta = post.read_meta(name, variant) or {}
        self.table = Timeline(self.meta) if self.meta.get("sky_segments") else None
        self.cur = self.meta.get("current") or {}
        base = self.meta.get("base")
        self.s = self.size = None
        if base:
            w, h = args.res or base[:2]
            self.size = (int(w), int(h))
            self.s = "%dx%d|%dspp|mb%d" % (w, h, args.samples or base[2], 0 if args.no_motion_blur else int(base[3]))
        self.fresh = bool(self.table) and _meta_is_fresh(name, variant)
        self.usable = self.fresh and self.s is not None and self.cur.get("s") == self.s
        self.on_disk = set(post.existing_frames(name, variant))
        self._seen = {}

    def status(self, frame):
        """'valid' | 'unjudged' | 'stale' | 'missing' (see the class docstring; only meaningful while usable)."""
        st = self._seen.get(frame)
        if st is None:
            st = self._seen[frame] = self._status(frame)
        return st

    def _status(self, frame):
        from PIL import Image

        if frame not in self.on_disk:
            return "missing"
        rec = self.meta.get("frames", {}).get(str(frame))
        if not isinstance(rec, dict):
            return "stale"
        expect = self.cur.get("fp", {}).get(str(frame))
        if expect is None:
            return "unjudged"
        if rec.get("s") != self.s or rec.get("e") != self.cur.get("e") or rec.get("fp") != expect:
            return "stale"
        if rec.get("sky") != self.table.sky_of(frame):
            return "unjudged"                         # (its own sky's build would have relabelled it)
        try:
            with Image.open(self.post.frame_path(self.name, frame, self.variant)) as im:
                return "valid" if tuple(im.size) == tuple(self.size) else "stale"
        except OSError:
            return "missing"


def _any_table(name, variant):
    """(Timeline, exact) from whichever meta.json of the film holds a sky table: this variant's, the final frames'
    or another preview's. exact = True when no source changed since it was written (the table IS the film's).
    Otherwise it is the table of the film BEFORE an edit: wrong exactly where the director changed the timeline or
    SKIES. Nothing is planned from such a table; it only says which sky the first process should try to build
    (Session(..., guess=True)), and that process reports the film's real table."""
    from engine import post

    seen, hint = [variant, None], None
    prev = os.path.join(post.OUT, "preview", name)
    if os.path.isdir(prev):
        seen += sorted(d for d in os.listdir(prev) if os.path.isdir(os.path.join(prev, d)))
    for v in seen:
        meta = post.read_meta(name, v)
        if not meta or not meta.get("sky_segments"):
            continue
        try:
            table = Timeline(meta)
        except (KeyError, TypeError, ValueError):
            continue
        if _meta_is_fresh(name, v):
            return table, True
        hint = hint or table
    return hint, False


def _die_with_parent():
    """In a sky's process, before it starts: be terminated when the process that started it dies (Linux)."""
    try:
        import ctypes
        import signal

        ctypes.CDLL("libc.so.6", use_errno=True).prctl(1, signal.SIGTERM)       # PR_SET_PDEATHSIG
    except Exception:                                                            # noqa: BLE001 - best effort
        pass


TMP_PREFIX = "render_sky_"


def _proc_start(pid):
    """(state, start time) of a process from /proc/<pid>/stat, or None when there is no such process."""
    try:
        with open("/proc/%d/stat" % pid, encoding="ascii", errors="replace") as fh:
            rest = fh.read().rsplit(")", 1)[1].split()
        return rest[0], rest[19]                  # (fields 3 and 22 of proc(5): state, starttime)
    except (OSError, IndexError):
        return None


def _alive(pid, start=None):
    """True while the process that wrote a temporary directory is still running: not gone, not a zombie that
    nobody has reaped yet (a process killed outright whose parent died with it), and not another process that
    was given the same number since (`start` = its start time as written in the directory)."""
    if pid <= 0:
        return False
    if os.path.isdir("/proc/self"):
        st = _proc_start(pid)
        return st is not None and st[0] != "Z" and (start is None or st[1] == start)
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except OSError:
        return True
    return True


def _sky_tmp():
    """A directory out/test/render_sky_*/ for the reports and contact-sheet tiles of the sky processes of ONE
    command (where the contact sheet's tile has always been written; out/test is not in the repository). It holds
    the command's process id, so that the directories of commands that were killed outright (SIGKILL: no clean-up
    runs) can be told from those of commands still running: they are removed here."""
    from engine import post

    root = os.path.join(post.OUT, "test")
    os.makedirs(root, exist_ok=True)
    for d in sorted(os.listdir(root)):
        old = os.path.join(root, d)
        if not (d.startswith(TMP_PREFIX) and os.path.isdir(old)):
            continue
        try:
            with open(os.path.join(old, "pid"), encoding="utf-8") as fh:
                words = fh.read().split()
            dead = not _alive(int(words[0]), words[1] if len(words) > 1 else None)
        except (OSError, ValueError, IndexError):
            try:                                  # (no pid file yet, or one from older code)
                dead = time.time() - os.path.getmtime(old) > 600.0
            except OSError:
                dead = False
        if dead:
            _sky_tmp_remove(old)
    tmp = tempfile.mkdtemp(prefix=TMP_PREFIX, dir=root)
    st = _proc_start(os.getpid())
    with open(os.path.join(tmp, "pid"), "w", encoding="utf-8") as fh:
        fh.write("%d %s" % (os.getpid(), st[1] if st else ""))
    return tmp


def _sky_tmp_remove(tmp):
    """Remove such a directory: only the files this module writes there, then the directory if it is empty."""
    try:
        for fn in os.listdir(tmp):
            if fn == "pid" or (fn.startswith("sky_") and fn.endswith((".json", ".json.part", ".png"))):
                os.remove(os.path.join(tmp, fn))
        os.rmdir(tmp)
    except OSError:
        pass


def _run_sky(argv, sky, rep_path, guess=False, skip=(), max_seconds=None):
    """`render <argv> --sky SKY` in a fresh process. Returns (its report or None, its exit code)."""
    cmd = [sys.executable, "-m", "render"] + list(argv) + ["--sky", sky, "--sky-report", rep_path]
    if guess:
        cmd.append("--sky-guess")
    if skip:
        cmd += ["--sky-skip", ",".join(sorted(skip))]
    if max_seconds is not None:
        cmd += ["--max-seconds", "%.1f" % max_seconds]
    sys.stdout.flush()
    env = dict(os.environ, PYTHONUNBUFFERED="1")
    code = subprocess.call(cmd, cwd=ROOT, env=env, preexec_fn=_die_with_parent)
    sys.stdout.flush()
    try:
        with open(rep_path, encoding="utf-8") as fh:
            return json.load(fh), code
    except (OSError, ValueError):
        return None, code


def sky_table(name):
    """The sky table of a film with several skies, as a Timeline (sky_of(frame), frame(seconds), segments, skies,
    shots), WITHOUT building the film in this process: read from a meta.json of the film while no source changed
    since it was written, else reported by a process that builds the film once. None for a film with one sky."""
    table, exact = _any_table(name, None)
    if exact:
        return table
    if not declares_skies(name):
        return None
    tmp = _sky_tmp()
    try:
        rep, code = _run_sky([name], "", os.path.join(tmp, "sky_0.json"), guess=True)
    finally:
        _sky_tmp_remove(tmp)
    if rep is None:
        raise SkyError("film '%s' could not be built to learn its sky table (exit code %d)" % (name, code))
    return None if rep.get("one_sky") else Timeline(rep["timeline"])


def session_for(name, frame=None, seconds=None):
    """A Session that can fingerprint and render the given frame (or film second): for a film with several skies
    the build of THAT frame's sky, for any other film Session(name). For tools that render single frames of a film
    (noise checks, timing studies): `ses = render.session_for(film, f); ses.configure(...); ses.render_frame(f, path)`.
    frame=None and seconds=None: the film's first frame."""
    table = sky_table(name)
    if table is None:
        return Session(name)
    f = int(frame) if frame is not None else table.frame(seconds) if seconds is not None else table.frame_start
    return Session(name, sky=table.sky_of(min(max(f, table.frame_start), table.frame_end)))


def _main_skies(args, argv, started):
    """A film with several skies. This process builds nothing: it works out which skies have work, runs each of them
    in a process of its own (`render <film> <the same arguments> --sky NAME`: a fresh Blender per sky, built exactly
    as a film with one sky is built), and does itself only what needs no Blender: the plan, the contact sheet, the
    summary and the encode. See "Several skies in one film" in the module docstring."""
    from PIL import Image

    from engine import post

    name = args.film
    stills = [s.strip() for chunk in args.still for s in chunk.split(",") if s.strip()]
    variant = variant_of(args.res, args.samples, args.step, not args.no_motion_blur)
    if not (stills or args.frames or args.sheet or args.save_blend or args.restamp or args.prune_stale or args.encode):
        print("nothing to do: give --still, --frames, --sheet, --encode, --restamp, --prune-stale or --save-blend")
        return 1
    where = "%s (%s)" % (post.frames_dir(name, variant), "FINAL" if variant is None else "preview " + variant)
    booked = bool(args.frames or args.restamp or args.prune_stale or args.encode)   # actions that use meta.json
    state = {"table": None, "exact": False, "spent": 0.0, "rendered": 0, "stopped": False, "tiles": {},
             "sheet": None, "left_out": [], "stills_done": [], "frame_info": None, "ran": [], "judged": [],
             "stopped_skies": set(), "did": set(), "sources": []}
    # exact = the table is the film's as it is now. A table from before an edit is never planned from: see one_pass
    state["table"], state["exact"] = _any_table(name, variant)
    # the reports and contact-sheet tiles of the sky processes live in out/test/render_sky_*/ for the length of this
    # command; a terminated command (timeout) still cleans up after itself and takes its sky process with it, and
    # what a killed one (SIGKILL) left is removed by the next command
    tmp = _sky_tmp()

    def _terminated(signum, _frame):
        raise SystemExit(128 + signum)

    try:
        import signal

        old_term = signal.signal(signal.SIGTERM, _terminated)
    except ValueError:                                   # (not the main thread: no handler, no clean-up on a kill)
        old_term = None

    def plan():
        return Plan(name, variant, args)

    def needs(skip):
        """{sky: set of actions} that still need a process of that sky, from the sky table and, while usable,
        meta.json's frame judgments. A plan only while the table is exact; on a table from before an edit it is
        no more than guess() makes of it."""
        table, p = state["table"], plan()
        known = p.usable
        out = {}

        def add(sky, action):
            if sky is not None and action not in skip:
                out.setdefault(sky, set()).add(action)

        for s in stills:
            if s not in state["stills_done"]:
                add(table.sky_of(_still_frame(table, s)), "still")
        if args.sheet:
            for i, f in enumerate(_sheet_frames(table, max(1, args.sheet))):
                if str(i) not in state["tiles"]:
                    add(table.sky_of(f), "sheet")
        if args.restamp:
            for f in _frame_list(args.restamp, table, args.step):
                if not known or p.status(f) in ("unjudged", "stale"):
                    add(table.sky_of(f), "restamp")
        if args.prune_stale:
            for f in sorted(p.on_disk):
                if table.sky_of(f) is None:
                    add(table.skies[0], "prune")              # beyond the film: any sky's process deletes it
                elif not known or p.status(f) != "valid":
                    add(table.sky_of(f), "prune")
        if args.frames:
            for f in _frame_list(args.frames, table, args.step):
                if args.force or not known or p.status(f) != "valid":
                    add(table.sky_of(f), "frames")
        if args.save_blend:
            for sky in table.skies:
                add(sky, "blend")
        if args.encode:
            for f in range(table.frame_start, table.frame_end + 1):
                if not known or p.status(f) == "unjudged":
                    add(table.sky_of(f), "encode")
        return out

    def guess(skip):
        """The sky in which a table from before an edit would have work first ("" when it cannot say). Only a
        preference for the first process: a new shot name, a longer film or a renamed sky make such a table wrong,
        so whatever goes wrong while reading it means "no preference", and the process that is started checks the
        name against the film as it is now."""
        try:
            todo = needs(skip)
            return next((k for k in state["table"].skies + sorted(todo) if k in todo), "")
        except Exception:                                    # noqa: BLE001 - an old table may fail in any way
            return ""

    def run(sky, skip, guessed=False):
        """One sky in its own process. Returns its report (None when it died)."""
        rep, code = _run_sky(argv, sky, os.path.join(tmp, "sky_%d.json" % len(state["ran"])), guess=guessed, skip=skip,
                             max_seconds=max(0.1, args.max_seconds - state["spent"]) if args.max_seconds else None)
        if rep is None:
            print(f"[render] the process of sky '{sky or '(first)'}' ended with exit code {code} and no report")
        return rep, code

    def one_pass(skip):
        """Run every sky that has work for the actions not in `skip`. Returns an exit code to stop with, or None."""
        ran = []
        while True:
            guessed = not state["exact"]
            if guessed:
                # No table, or one from before an edit. NOTHING is planned from it: the first process builds the
                # sky such a table suggests if the film still has it (else the film's first sky), does that sky's
                # share of everything that was asked for, and reports the film's real table.
                sky, why = guess(skip) if state["table"] is not None else "", {"(to learn the film's sky table)"}
            else:
                todo = {k: v for k, v in needs(skip).items() if k not in ran}
                if state["stopped"]:
                    # the engine check stopped the frames: only skies with such frames still report on theirs
                    todo = {k: v - {"frames"} | ({"frames"} if k in state["stopped_skies"] else set())
                            for k, v in todo.items()}
                    todo = {k: v for k, v in todo.items() if v}
                out_of_time = bool(args.max_seconds) and state["spent"] >= args.max_seconds
                if out_of_time:
                    for k in [k for k, v in todo.items() if v == {"frames"}]:
                        state["left_out"].append(k)
                        del todo[k]
                if not todo:
                    return None
                sky = next(k for k in state["table"].skies + sorted(todo) if k in todo)
                why = todo[sky]
            sub_skip = set(skip)
            if state["table"] is not None and bool(args.max_seconds) and state["spent"] >= args.max_seconds:
                sub_skip.add("frames")
            if guessed:
                print(f"[render] sky '{sky or '(first)'}': a process of its own, to learn the film's sky table and do "
                      f"its share" + ("" if state["table"] is None else
                                      " (a source changed since the table on disk was written: that one only suggests "
                                      "which sky to build first)"), flush=True)
            else:
                print(f"[render] sky '{sky}': a process of its own for " + ", ".join(sorted(why)), flush=True)
            rep, code = run(sky, sub_skip, guessed)
            if rep is None:
                return code if code > 0 else 1
            if rep.get("one_sky"):
                return code                       # a film with ONE sky after all: that process did the whole job
            # (the first sky of a film whose table was unknown does its share of everything that was asked for)
            asked = {a for a, on in (("still", stills), ("sheet", args.sheet), ("restamp", args.restamp),
                                     ("prune", args.prune_stale), ("frames", args.frames), ("blend", args.save_blend),
                                     ("encode", args.encode)) if on}
            state["did"] |= ((set(why) & set(SKY_ACTIONS)) or asked) - sub_skip
            ran.append(rep["sky"])
            state["ran"].append(rep["sky"])
            state["table"], state["exact"] = Timeline(rep["timeline"]), True
            state["sources"].append((rep["sky"], list(rep["timeline"]["sources"]), rep["timeline"]["source_hash"]))
            state["stills_done"] += rep.get("stills_done", [])
            if rep.get("sheet"):
                state["sheet"] = rep["sheet"]
                state["tiles"].update(rep["sheet"]["tiles"])
            fr = rep.get("frames")
            if fr:
                state["judged"].append(rep["sky"])
                state["spent"] += fr["seconds"]
                state["rendered"] += fr["rendered"]
                state["frame_info"] = fr
                if fr["engine_stop"]:
                    state["stopped"] = True
                    state["stopped_skies"].update(fr["elsewhere"])
            if code not in (0, 3):
                print(f"[render] the process of sky '{rep['sky']}' failed (exit code {code})")
                return code if code > 0 else 1
            if sky not in ("", rep["sky"]) and not guessed:
                raise SkyError("asked for sky %r, the process built %r" % (sky, rep["sky"]))

    def edited():
        """True when a file that one of this command's sky processes built from has changed since that process read
        it: somebody edited the film (or anything it loads) while the command ran, which is allowed at any time.
        (Two processes that loaded different files from UNCHANGED sources are not an edit: that is a film whose
        build depends on the active sky, and the account below says so.)"""
        return any(source_hash(files) != h for _sky, files, h in state["sources"])

    try:
        first = {"frames", "blend", "encode"} if (args.restamp or args.prune_stale) and \
            (args.frames or args.save_blend or args.encode) else set()
        passes = [first, {"still", "sheet", "restamp", "prune"}] if first else [set()]
        # (re-stamping and pruning are finished for EVERY sky before any sky's frames are checked and rendered)
        for skip in passes:
            code = one_pass(skip)
            if code is not None:
                return code
            if state["stopped"]:
                break
        table = state["table"]
        for flag, action, what in ((args.restamp, "restamp", "re-stamp"), (args.prune_stale, "prune", "prune")):
            if flag and action not in state["did"] and not state["stopped"]:
                print(f"[render] {action} -> {where}: nothing to {what}, every frame concerned is a valid frame of the "
                      f"film (no sky was built for it)")

        # ---- contact sheet: the tiles of all skies, put together here
        if args.sheet and state["sheet"]:
            sh = state["sheet"]
            tiles = []
            for i in range(sh["n"]):
                with Image.open(state["tiles"][str(i)]) as im:
                    tiles.append(im.convert("RGB"))
            path = post.contact_sheet(tiles, sh["labels"], sh["words"], os.path.join(post.OUT, "test", f"{name}_sheet.png"),
                                      gains=sh["gains"] if table.fades else None)
            print(f"[render] sheet -> {path}")

        # ---- frames: the whole film's account. The words "0 to render" are said here and only here, and only
        #      when every requested frame of every sky is a valid frame as its OWN sky's build judged it.
        if args.frames:
            p = plan()
            wanted = _frame_list(args.frames, table, args.step)
            if state["stopped"]:
                print(f"[render] frames -> {where}: STOPPED by frames rendered with other engine sources, nothing "
                      f"rendered in any sky (see above; --restamp {args.frames}, or --rerender-stale). (exit code 3)")
                return 3
            if not p.fresh or edited():
                # (somebody edited a file of the film between two sky processes, or after the last one: every frame
                #  that was rendered is right and stamped; what one sky judged before the edit is judged again)
                print(f"[render] frames -> {where}: a source file of the film changed while this command ran; "
                      f"the frames it rendered are kept, but nothing can be said about the whole film until the "
                      f"command is run again" + (" (not encoded: exit code 2)" if args.encode else ""))
                return 2 if args.encode else 0
            if not p.usable:
                raise SkyError("film '%s': %s holds stamps for the settings %r, this command asks for %r: the film's "
                               "own render settings must not depend on the active sky"
                               % (name, where, p.cur.get("s"), p.s))
            valid = [f for f in wanted if p.status(f) == "valid"]
            left = {}
            for f in wanted:
                if p.status(f) != "valid":
                    left.setdefault(table.sky_of(f), []).append(f)
            for sky in state["judged"]:
                lost = [f for f in left.get(sky, []) if p.status(f) == "unjudged"]
                if lost:
                    raise SkyError("film '%s': the judgment of sky %r (frames %s) did not survive the build of the next "
                                   "sky: the builds of different skies load different project files or settings. Import "
                                   "everything at the top of the film module, never depending on the active sky."
                                   % (name, sky, _ranges(lost)))
            info = state["frame_info"]
            size = "%dx%d, %d samples, %d threads" % (
                (info["res"][0], info["res"][1], info["samples"], info["threads"]) if info else
                (p.size[0], p.size[1], args.samples or table.base[2], args.threads or FINAL_THREADS))
            skies_note = "%d sk%s: %s" % (len(table.skies), "y" if len(table.skies) == 1 else "ies", ", ".join(table.skies))
            n_left = len(wanted) - len(valid)
            if n_left == 0:
                now = f"{state['rendered']} rendered in this run, " if state["rendered"] else ""
                print(f"[render] frames: {len(wanted)} requested, {len(valid) - state['rendered']} already done, {now}"
                      f"0 to render at {size} ({skies_note}; every frame judged in the build of its own sky)")
            else:
                parts = []
                for sky in table.skies:
                    fs = left.get(sky)
                    if fs:
                        unj = sum(p.status(f) == "unjudged" for f in fs)
                        parts.append("sky '%s': %d%s" % (sky, len(fs), " (%d of them not judged yet)" % unj if unj else ""))
                print(f"[render] frames: {len(wanted)} requested, {len(valid)} done ({state['rendered']} in this run), "
                      f"{n_left} left at {size} ({'; '.join(parts)}); re-run the same command to resume")

        if stills and len(set(state["stills_done"])) < len(set(stills)):
            print("[render] stills not rendered:", ", ".join(s for s in stills if s not in state["stills_done"]))

        # ---- encode: one complete film in meta.json, the encoder is the one every film uses
        if args.encode:
            if edited():
                print("[render] encode refused: a source file of the film changed while this command ran; run it again")
                return 2
            return _encode_action(args, name, variant, started)
        return 0
    finally:
        if old_term is not None:
            signal.signal(signal.SIGTERM, old_term)
        _sky_tmp_remove(tmp)


if __name__ == "__main__":
    sys.exit(main())
