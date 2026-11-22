"""Render CLI. One Blender process builds the film once, then does everything that was asked for.

    BPY=/path/to/python-with-bpy ;  cd <project root>
    $BPY -m render <film> --still 1.5                 # out/test/<film>_1.5.png      (540x960, 16 samples, 2 threads)
    $BPY -m render <film> --still 0.5,2,7.25 --res 720x1280 --samples 24 --captioned
    $BPY -m render <film> --sheet 12                  # out/test/<film>_sheet.png    (contact sheet WITH captions)
    $BPY -m render <film> --frames all --max-seconds 240      # FINAL frames: out/frames/<film>/f_####.png
                                                              #   (720x1280, 24 samples, 4 threads), resumable
    $BPY -m render <film> --encode [--audio a.wav]    # out/<film>.mp4  1080x1920 H.264 yuv420p crf 16 +faststart
    $BPY -m render <film> --frames all --step 4 --res 360x640 --samples 8 --encode --allow-holds
                                                      # PREVIEW: out/preview/<film>/360x640_8spp_step4/ and
                                                      #   out/preview/<film>_360x640_8spp_step4.mp4
    $BPY -m render <film> --still 1.5 --zones         # also <name>_zones.png: Reels UI zones, caption band, safe area
    $BPY -m render <film> --save-blend                # out/blend/<film>.blend with textures packed, final settings
    $BPY -m render <film> --frames all --rerender-stale   # after an engine edit: render the stale frames again
    $BPY -m render <film> --restamp all               # after an engine edit that changed no picture: keep the frames
    $BPY -m render <film> --prune-stale               # delete PNGs that are not part of the film any more

A film is films/<film>.py exposing build(scene) -> {"film": engine.shots.Film, "captions": [(word, t0, t1), ...]}.
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
Exit codes: 0 done, 1 nothing to do, 2 encode refused, 3 stopped because engine sources changed under final frames.
"""
import argparse
import hashlib
import importlib
import os
import sys
import time

ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

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
                    help="with --frames: stop starting new frames after this many seconds (resume by re-running)")
    ap.add_argument("--no-motion-blur", action="store_true", help="disable motion blur (faster look-dev stills)")
    ap.add_argument("--audio", metavar="FILE", help="with --encode: mux this audio file (AAC 192k, cut to the video)")
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
NON_PIXEL = ("engine/captions.py", "engine/post.py", "engine/stamp.py", "render.py")


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


class Session:
    """A built film inside the current Blender process."""

    def __init__(self, name):
        import bpy

        from engine import look

        self.bpy = bpy
        self.name = name
        t = time.time()
        bpy.ops.wm.read_factory_settings(use_empty=True)
        self.scene = bpy.context.scene
        look.setup_render(self.scene, res=FINAL_RES, samples=FINAL_SAMPLES, threads=FINAL_THREADS)
        module = importlib.import_module("films." + name)
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
        print(f"[render] built '{name}' in {time.time() - t:.1f}s: frames {self.film.frame_start}-{self.film.frame_end} "
              f"({self.film.duration:.2f} s at {self.film.fps} fps), {len(self.film.shots)} shots, "
              f"{len(self.captions)} caption words, {self._face_count()} faces")

    def _face_count(self):
        return sum(len(o.data.polygons) for o in self.scene.objects if o.type == "MESH")

    def meta(self):
        """Everything post needs to encode without Blender, plus what the frames depend on."""
        f = self.film
        sources = project_sources()
        return {
            "film": self.name, "fps": f.fps, "frame_start": f.frame_start, "frame_end": f.frame_end,
            "captions": [list(c) for c in self.captions],
            "shots": [{"name": s.name, "frame_start": s.frame_start, "frame_end": s.frame_end} for s in f.shots],
            "sources": sources, "source_hash": source_hash(sources),
        }

    def settings_key(self):
        """The render settings a frame is stamped with: '720x1280|24spp|mb1'."""
        r, c = self.scene.render, self.scene.cycles
        return "%dx%d|%dspp|mb%d" % (r.resolution_x, r.resolution_y, c.samples, int(r.use_motion_blur))

    def engine_files(self):
        """{project path: short hash} of the loaded sources that can change a pixel (see engine_sources)."""
        return {p: file_hash(p) for p in engine_sources()}

    def fingerprint(self, frame):
        """Scene fingerprint of a frame at the current settings: {'fp': hex, 'parts': {...}} (engine/stamp.py)."""
        from engine import stamp

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
        """Render one frame number to a PNG path (atomic: written under a temporary name first)."""
        scene = self.scene
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
    disk are still frames of the film, and why the others are not (see the module docstring)."""

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
        self.on_disk = set(post.existing_frames(name, variant))
        self._status = {}

    def fp(self, frame):
        """Current scene fingerprint of a frame (computed once)."""
        k = str(frame)
        if k not in self.cur_fp:
            self.cur_fp[k] = self.ses.fingerprint(frame)["fp"]
        return self.cur_fp[k]

    def status(self, frame):
        """'valid' | 'missing' | 'unstamped' | 'size' | 'settings' | 'scene' | 'engine' | 'engine+scene'.
        'engine' = rendered with other engine sources but the scene fingerprint is unchanged (re-stampable);
        'scene' = this frame's own content changed (film edit); 'engine+scene' = both."""
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
        if rec.get("e") != self.e:
            return "engine" if same else "engine+scene"
        return "valid" if same else "scene"

    def mark(self, frame, fingerprint=None):
        """Stamp a frame as rendered (or accepted) with the current settings, engine and fingerprint."""
        d = fingerprint or self.ses.fingerprint(frame)
        self.cur_fp[str(frame)] = d["fp"]
        self.frames[str(frame)] = {"s": self.s, "e": self.e, "fp": d["fp"], "parts": d["parts"]}
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
    return source_hash(meta["sources"]) == meta["source_hash"]


def main(argv=None):
    """Entry point of `python -m render`."""
    args = _parse_args(sys.argv[1:] if argv is None else argv)
    from PIL import Image

    from engine import captions as cap
    from engine import post

    name = args.film
    stills = [s.strip() for chunk in args.still for s in chunk.split(",") if s.strip()]
    # final frames and previews never share a directory (see the module docstring)
    variant = variant_of(args.res, args.samples, args.step, not args.no_motion_blur)
    needs_build = bool(stills or args.frames or args.sheet or args.save_blend or args.restamp or args.prune_stale
                       or (args.encode and not _meta_is_fresh(name, variant)))
    if not (needs_build or args.encode):
        print("nothing to do: give --still, --frames, --sheet, --encode, --restamp, --prune-stale or --save-blend")
        return 1

    ses = None
    if needs_build:
        ses = Session(name)
    mb = False if args.no_motion_blur else None
    test_dir = os.path.join(post.OUT, "test")

    # ---- stills
    if stills:
        ses.configure(args.res or STILL_RES, args.samples or STILL_SAMPLES, args.threads or STILL_THREADS, mb)
        for s in stills:
            frame = min(ses.film.frame_end, max(ses.film.frame_start, ses.film.frame(float(s))))
            path = os.path.join(test_dir, f"{name}_{s}.png")
            t = time.time()
            ses.render_frame(frame, path)
            shot = ses.film.shot_at(frame)
            print(f"[render] still {s}s = frame {frame} (shot '{shot.name}') -> {path}  {time.time() - t:.1f}s")
            if args.captioned:
                word = cap.caption_at(ses.captions, ses.film.seconds(frame))
                with Image.open(path) as im:
                    capped = post.finish_frame(im, word)
                capped.save(path[:-4] + "_cap.png")
                print(f"[render]   caption {word!r} -> {path[:-4]}_cap.png")
            if args.zones:
                with Image.open(path) as im:
                    post.draw_zones(im).save(path[:-4] + "_zones.png")
                print(f"[render]   zones -> {path[:-4]}_zones.png")

    # ---- contact sheet
    if args.sheet:
        n = max(1, args.sheet)
        ses.configure(args.res or SHEET_RES, args.samples or SHEET_SAMPLES, args.threads or STILL_THREADS, mb)
        total = ses.film.frame_end - ses.film.frame_start + 1
        tiles, labels, words = [], [], []
        tmp = os.path.join(test_dir, f"{name}_sheet_tile.png")
        t0 = time.time()
        for i in range(n):
            frame = ses.film.frame_start + min(total - 1, int((i + 0.5) * total / n))
            ses.render_frame(frame, tmp)
            with Image.open(tmp) as im:
                tiles.append(im.convert("RGB"))
            sec = ses.film.seconds(frame)
            labels.append("%.2fs %s" % (sec, ses.film.shot_at(frame).name))
            words.append(cap.caption_at(ses.captions, sec))
            print(f"[render] sheet tile {i + 1}/{n}: frame {frame}  ({time.time() - t0:.1f}s elapsed)")
        if os.path.exists(tmp):
            os.remove(tmp)
        path = post.contact_sheet(tiles, labels, words, os.path.join(test_dir, f"{name}_sheet.png"))
        print(f"[render] sheet -> {path}")

    # ---- frames
    book = None
    if args.frames or args.restamp or args.prune_stale or (args.encode and ses is not None):
        ses.configure(args.res, args.samples, args.threads or FINAL_THREADS, mb)
        r = ses.scene.render
        book = Stamps(ses, name, variant)
        where = "%s (%s)" % (post.frames_dir(name, variant), "FINAL" if variant is None else "preview " + variant)

    if args.restamp:
        # accept frames without rendering: by default only those whose picture is provably the same (same settings,
        # same scene fingerprint, other engine sources); --restamp-changed accepts whatever PNG of the right size is there
        targets = _frame_list(args.restamp, ses.film, args.step)
        take, refuse = [], []
        for f in targets:
            st = book.status(f)
            if st == "engine" or (args.restamp_changed and st in ("engine+scene", "scene", "unstamped", "settings")):
                take.append(f)
            elif st not in ("valid", "missing"):
                refuse.append(f)
        for f in take:
            book.mark(f)
        print(f"[render] restamp -> {where}: {len(take)} frames re-stamped without rendering"
              + (f" ({_ranges(take)})" if take else "")
              + (f"; {len(refuse)} NOT accepted, their scene changed or they have no usable stamp ({_ranges(refuse)}): "
                 f"render them, or pass --restamp-changed to keep them anyway" if refuse else ""))
        book.save()

    if args.prune_stale:
        f_end = ses.film.frame_end
        gone = [f for f in sorted(book.on_disk) if f > f_end or f < ses.film.frame_start or book.status(f) != "valid"]
        for f in gone:
            try:
                os.remove(post.frame_path(name, f, variant))
            except OSError:
                pass
            book.frames.pop(str(f), None)
            book.cur_fp.pop(str(f), None)
            book.on_disk.discard(f)
            book._status.pop(f, None)
        print(f"[render] prune -> {where}: {len(gone)} stale PNGs deleted" + (f" ({_ranges(gone)})" if gone else "")
              + f", {len(book.on_disk)} valid frames kept")
        book.save()

    if args.frames:
        frames = _frame_list(args.frames, ses.film, args.step)
        status = {f: book.status(f) for f in frames}
        by_engine = [f for f in frames if status[f] in ("engine", "engine+scene")]
        by_scene = [f for f in frames if status[f] == "scene"]
        other = [f for f in frames if status[f] in ("unstamped", "size", "settings")]
        todo = [f for f in frames if args.force or status[f] != "valid"]
        print(f"[render] frames -> {where}")
        if by_engine and not (args.rerender_stale or args.force):
            same = [f for f in by_engine if status[f] == "engine"]
            diff = [f for f in by_engine if status[f] == "engine+scene"]
            print(f"[render] STOPPED, nothing rendered: {len(by_engine)} of the {len(frames)} requested frames were "
                  f"rendered with other engine sources. Changed since: {', '.join(book.changed_files(by_engine))}")
            if same:
                print(f"[render]   {len(same)} of them show an unchanged scene ({_ranges(same)}): the edit altered no "
                      f"picture there; keep them with  --restamp {args.frames}")
            if diff:
                print(f"[render]   {len(diff)} have a changed scene ({_ranges(diff)}; shots: {book.shots_of(diff)}; "
                      f"changed: {book.why_scene(diff[:1] + diff[-1:])})")
            print("[render]   --rerender-stale renders all of them again. (exit code 3)")
            book.save()
            return 3
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
        book.save()
        t0 = time.time()
        done = 0
        for f in todo:
            if args.max_seconds and done and time.time() - t0 > args.max_seconds:
                print(f"[render] stopping after {time.time() - t0:.0f}s (--max-seconds); {len(todo) - done} frames left, "
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
            print(f"[render] {done} frames in {time.time() - t0:.1f}s = {(time.time() - t0) / done:.2f} s/frame")

    if book is not None and args.encode:
        # the encoder trusts meta.json: judge every frame of the film against the scene as it is built now
        states = [book.status(f) for f in range(ses.film.frame_start, ses.film.frame_end + 1)]
        book.save()
        n_engine = sum(st in ("engine", "engine+scene") for st in states)
        if n_engine:
            keep = states.count("engine")
            print(f"[render] encode: {n_engine} frames on disk were rendered with other engine sources "
                  f"({', '.join(book.changed_files(range(ses.film.frame_start, ses.film.frame_end + 1)))}); "
                  f"{keep} of them show an unchanged scene and can be kept with --restamp all")

    # ---- blend
    if args.save_blend:
        bpy = ses.bpy
        path = os.path.join(post.OUT, "blend", name + ".blend")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        # the file carries the FINAL render settings, whatever --still / --sheet / --frames used before in this call
        ses.configure(None, None, FINAL_THREADS, ses.base_motion_blur)
        ses.film.goto(ses.film.frame_start)
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
    if args.encode:
        meta = post.read_meta(name, variant)
        try:
            mp4 = post.encode(name, captions=[tuple(c) for c in meta["captions"]], fps=meta["fps"],
                              frame_start=meta["frame_start"], frame_end=meta["frame_end"], audio=args.audio,
                              variant=variant, allow_holds=args.allow_holds)
        except RuntimeError as e:
            print("[render] encode refused:", e)
            return 2
        print("[render] video:", post.probe(mp4))
    return 0


if __name__ == "__main__":
    sys.exit(main())
