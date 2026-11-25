"""Post: frame bookkeeping, caption compositing, contact sheets and the H.264 encode (PIL + ffmpeg, no Blender).

FINAL frames (720x1280, 24 samples, every frame) live in out/frames/<film>/f_####.png (#### = frame number, frame
1 = second 0). Anything rendered with other settings is a PREVIEW and lives apart, in
out/preview/<film>/<W>x<H>_<N>spp[_stepK]/ (a `variant`), so a cheap preview can never end up inside a final film.
Next to the frames sits meta.json, which render.py writes after building a film: fps, frame range, captions, shot
list, the render settings, a hash of the sources that built the film, for every rendered frame its stamp (settings,
engine-source hash, scene fingerprint: see render.py and engine/stamp.py) and, under 'current', what each frame
should carry now. A frame counts only while its stamp is the current one.

Sound: encode(audio=...) first writes the silent film exactly as a film without sound is written, then mux_audio()
puts the audio under it WITHOUT re-encoding the picture (the video stream is copied bit for bit): AAC 192 kb/s,
48 kHz, stereo (a mono narration becomes dual mono), starting at t = 0 and padded or cut to the exact length of the
picture, +faststart. A narrated film gets its audio automatically (render.py --encode finds narration/<film>.wav,
see engine/narration.py); mux_audio(video, wav) alone puts a narration under an already joined film.

Long films: encode_parts() writes a film in parts of SEGMENT_FRAMES frames, each by encode() itself, and joins them
with a stream copy. A part that is already on disk for the same frames, captions and settings is not encoded again,
and a `deadline` stops the work between two parts, so a one-minute film (0.13 to 0.26 s per frame here: 190 to
380 s for 1440 frames) survives a command time limit: run the same command again and it continues. render.py
--encode uses it for every film longer than SEGMENT_OVER frames; shorter films are written in one pass exactly
as before.

Fades (dips to black): a film may carry "fades" in meta.json, a list of picture-gain RAMPS in film seconds,
    [t0, t1, g0, g1]      the gain of the picture goes linearly from g0 at t0 to g1 at t1 (0 = black, 1 = untouched)
A ramp acts on the frames whose time t (frame number f shows t = (f - first frame) / fps, the clock of the captions)
lies in t0 <= t < t1; outside every ramp the gain is 1; where ramps overlap their gains multiply. A dip to black
with a hold is three ramps (1 -> 0, 0 -> 0, 0 -> 1); films.lookdev.Stage.dip() writes them from frame numbers.
The gain is applied to the delivered PICTURE (after the upscale, on the 8-bit display values: gain 0.5 halves
every channel) and BEFORE the caption is drawn: the caption stays at full strength, the narrator talks through a
dip. encode(), encode_parts(), contact_sheet() and finish_frame() all do it the same way (fade_gain + apply_gain).
Fades are no part of a frame's stamp: changing one re-encodes (in parts: only the parts it touches) and re-renders
nothing. A frame with gain 1 is passed on untouched, so a film without fades is encoded bit for bit as before.
"""
import hashlib
import json
import os
import re
import shutil
import subprocess
import time

from PIL import Image

from . import captions as cap

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "out")
FINAL_SIZE = (1080, 1920)
AUDIO_RATE, AUDIO_BITRATE = 48000, "192k"
# A mono narration is delivered as dual mono: the same samples, at full level, left and right. BS.1770 adds the two
# channels' power, so the STEREO programme measures 3.01 LU above the mono file: tools/narrate.py therefore makes
# narration/<film>.wav at -19 LUFS (true peak under -2 dBTP) and the mp4 measures -16 LUFS with its true peak under
# -1.5 dBTP. (The wav was first made at -16 LUFS and lowered 3.01 dB here: the same programme, but the limiter in
# narrate.py had to take 3 dB more off every peak to get there.)
DUAL_MONO_GAIN_DB = 0.0
# Encoding costs 0.13 s per 1080x1920 frame on this machine when it is idle and 0.26 s when four agents share it
# (measured: 275 frames of a finished film in 72 s), most of it single-threaded Python (PNG read, Lanczos, caption).
SEGMENT_FRAMES = 240          # encode_parts(): frames per part (10 s at 24 fps: 31 to 62 s of work)
SEGMENT_OVER = 480            # render.py --encode: a film longer than this many frames (20 s) is encoded in parts

# Where a Reels viewer actually sees the picture, as fractions of the 9:16 video (x0, y0, x1, y1), measured on the
# reference screenshots (1179x2556 phone, video height-filled down to y = 2333, so the sides are cropped):
UI_ZONES = {
    "side crop L": (0.0, 0.0, 0.05, 1.0),            # tall phones cut about 5 % off each side
    "side crop R": (0.95, 0.0, 1.0, 1.0),
    "top icons": (0.0, 0.0, 1.0, 0.13),              # back arrow, camera, status bar
    "icon column": (0.84, 0.45, 0.95, 0.95),         # like / comment / share / save
    "name + description": (0.0, 0.87, 0.95, 1.0),
}
CAPTION_ZONE = (0.10, cap.CAPTION_BAND[0], 0.90, cap.CAPTION_BAND[1])
# Composition rule for every shot: faces and hero props inside SAFE_AREA; nothing essential in the caption band
# (y 62-72 %) or below 86 %.
SAFE_AREA = {"x": (0.08, 0.82), "y": (0.14, 0.60)}


def draw_zones(img):
    """Debug overlay: a copy of the frame with the Reels interface zones (red), the caption band (yellow) and the
    safe area for faces and hero props (green outline) drawn on it."""
    from PIL import ImageDraw

    base = img.convert("RGBA")
    w, h = base.size
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)

    def box(z):
        return [int(z[0] * w), int(z[1] * h), int(z[2] * w) - 1, int(z[3] * h) - 1]

    for z in UI_ZONES.values():
        d.rectangle(box(z), fill=(255, 40, 40, 48), outline=(255, 60, 60, 160))
    d.rectangle(box(CAPTION_ZONE), fill=(255, 220, 0, 48), outline=(255, 220, 0, 220))
    (x0, x1), (y0, y1) = SAFE_AREA["x"], SAFE_AREA["y"]
    for k in range(max(2, w // 240)):
        d.rectangle([int(x0 * w) + k, int(y0 * h) + k, int(x1 * w) - 1 - k, int(y1 * h) - 1 - k], outline=(60, 255, 90, 230))
    return Image.alpha_composite(base, layer).convert("RGB")


def check_fades(fades):
    """Normalise a film's fades to [[t0, t1, g0, g1], ...] (floats, sorted by t0); [] for None. Raises ValueError
    for anything that is not a list of 4-number ramps with t1 > t0 and gains inside 0..1."""
    out = []
    for ramp in fades or ():
        try:
            t0, t1, g0, g1 = (float(x) for x in ramp)
        except (TypeError, ValueError):
            raise ValueError("a fade is a ramp (t0, t1, g0, g1) in film seconds, not %r" % (ramp,)) from None
        if not (t1 > t0 and 0.0 <= g0 <= 1.0 and 0.0 <= g1 <= 1.0):
            raise ValueError("fade %r: needs t1 > t0 and both gains inside 0..1" % (ramp,))
        out.append([t0, t1, g0, g1])
    return sorted(out)


def fade_gain(fades, t):
    """Picture gain at film second t for a list of ramps [t0, t1, g0, g1] (see the module docstring): 1.0 outside
    every ramp, the product where ramps overlap. (A nanosecond of slack keeps a time that was computed as
    frame / fps on the right side of a ramp's ends.)"""
    g = 1.0
    for t0, t1, g0, g1 in fades or ():
        if t0 - 1e-9 <= t < t1 - 1e-9:
            g *= g0 + (g1 - g0) * min(1.0, max(0.0, (t - t0) / (t1 - t0)))
    return min(1.0, max(0.0, g))


def apply_gain(img, gain):
    """The picture times `gain` on its display values (RGB, 8 bit); gain >= 1 returns the image itself, untouched."""
    if gain >= 1.0:
        return img
    lut = [int(i * max(0.0, gain) + 0.5) for i in range(256)]
    return img.convert("RGB").point(lut * 3)


def frames_dir(film, variant=None):
    """Directory holding a film's rendered frames: the final ones, or a preview `variant` ('360x640_8spp_step4')."""
    if variant:
        return os.path.join(OUT, "preview", film, variant)
    return os.path.join(OUT, "frames", film)


def frame_path(film, frame, variant=None):
    """Path of one rendered frame (frame number, 1-based)."""
    return os.path.join(frames_dir(film, variant), "f_%04d.png" % int(frame))


def existing_frames(film, variant=None):
    """Sorted frame numbers that have a PNG on disk (valid or not: see valid_frames)."""
    d = frames_dir(film, variant)
    if not os.path.isdir(d):
        return []
    out = []
    for name in os.listdir(d):
        m = re.fullmatch(r"f_(\d{4,})\.png", name)
        if m:
            out.append(int(m.group(1)))
    return sorted(out)


def valid_frames(film, variant=None, signature=None, size=None):
    """Frame numbers whose PNG exists AND whose stamp in meta.json is the current one AND, when `size` is given, has
    exactly that pixel size. render.py stamps every frame with {s: settings, e: engine hash, fp: scene fingerprint}
    and stores what each frame should carry NOW under meta['current'] each time it builds the film; a frame is valid
    while the two agree. Frames from older renders, other settings or an edited shot are not valid: they are
    rendered again on resume and refused by encode(). (A meta without 'current' but with one 'signature' string is
    the simple form used by this module's self-test: stamp == signature.)"""
    meta = read_meta(film, variant) or {}
    stamped = meta.get("frames", {})
    cur = meta.get("current")
    signature = signature or meta.get("signature")
    out = []
    for f in existing_frames(film, variant):
        rec = stamped.get(str(f))
        if cur is not None:
            if not (isinstance(rec, dict) and rec.get("s") == cur.get("s") and rec.get("e") == cur.get("e")
                    and rec.get("fp") is not None and rec.get("fp") == cur.get("fp", {}).get(str(f))):
                continue
        elif signature is None or rec != signature:
            continue
        if size is not None:
            try:
                with Image.open(frame_path(film, f, variant)) as im:
                    if tuple(im.size) != tuple(size):
                        continue
            except OSError:
                continue
        out.append(f)
    return out


def write_meta(film, meta, variant=None):
    """Store fps / frame range / captions / shots / settings / frame signatures for a film next to its frames."""
    os.makedirs(frames_dir(film, variant), exist_ok=True)
    path = os.path.join(frames_dir(film, variant), "meta.json")
    tmp = path + ".part"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=1)
    os.replace(tmp, path)
    return path


def read_meta(film, variant=None):
    """The stored meta dict, or None."""
    path = os.path.join(frames_dir(film, variant), "meta.json")
    if not os.path.exists(path):
        return None
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except ValueError:
        return None


def upscale(img, size=FINAL_SIZE):
    """Render frame -> delivery size with Lanczos (720x1280 -> 1080x1920)."""
    img = img.convert("RGB")
    return img if img.size == tuple(size) else img.resize(tuple(size), Image.LANCZOS)


def finish_frame(img, word=None, size=FINAL_SIZE, gain=1.0):
    """Upscale a rendered frame and draw the caption word on it (None = no caption). gain < 1 darkens the picture
    first (a fade: fade_gain(fades, t)); the caption is drawn at full strength on top."""
    return cap.composite(apply_gain(upscale(img, size), gain), word)


def contact_sheet(tiles, labels, words, path, columns=None, gap=6, gains=None):
    """Grid of small frames with their caption drawn in and a label (time / shot) above each; saves a PNG.
    gains = one picture gain per tile (a film's fades at that tile's time); None = all untouched."""
    n = len(tiles)
    if n == 0:
        raise ValueError("no tiles")
    columns = columns or min(n, 6)
    rows = (n + columns - 1) // columns
    tw, th = tiles[0].size
    head = 22
    sheet = Image.new("RGB", (columns * tw + (columns + 1) * gap, rows * (th + head) + (rows + 1) * gap), (18, 18, 22))
    for i, (tile, label, word) in enumerate(zip(tiles, labels, words)):
        x = gap + (i % columns) * (tw + gap)
        y = gap + (i // columns) * (th + head + gap)
        lab = cap.label(label, scale=2)
        sheet.paste(lab, (x, y + 1), lab)
        if gains is not None and gains[i] < 1.0:
            tile = apply_gain(tile, gains[i])
        sheet.paste(cap.composite(tile, word), (x, y + head))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    sheet.save(path)
    return path


def usable_frames(film, variant=None, frame_start=None, frame_end=None, allow_holds=False):
    """The frames an encode of [frame_start, frame_end] (default: the film's range in meta.json) may use:
    (valid frame numbers on disk, frame_start, frame_end). Raises RuntimeError when there are none, when frames of
    the range are missing or stale and allow_holds is False, or when the frames have mixed pixel sizes."""
    meta = read_meta(film, variant) or {}
    stamped = meta.get("current") is not None or meta.get("signature")
    have = valid_frames(film, variant) if stamped else existing_frames(film, variant)
    if not have:
        raise RuntimeError("no valid frames in %s (render them with: python -m render %s --frames all)"
                           % (frames_dir(film, variant), film))
    frame_start = int(frame_start or meta.get("frame_start", have[0]))
    frame_end = int(frame_end or meta.get("frame_end", have[-1]))
    have_set = set(have)
    wanted = range(frame_start, frame_end + 1)
    missing_frames = [f for f in wanted if f not in have_set]
    stale = [f for f in existing_frames(film, variant) if f not in have_set and frame_start <= f <= frame_end]
    if missing_frames and not allow_holds:
        raise RuntimeError(
            "%s: %d of %d frames are missing or stale (first: %s; %d stale files from an older render or other "
            "settings). Render them (python -m render %s --frames all) or pass --allow-holds to hold the previous "
            "frame over each gap." % (frames_dir(film, variant), len(missing_frames), len(wanted),
                                      missing_frames[:8], len(stale), film))
    sizes = {}
    for f in have:
        if frame_start <= f <= frame_end:
            with Image.open(frame_path(film, f, variant)) as im:
                sizes.setdefault(tuple(im.size), []).append(f)
    if len(sizes) > 1:
        raise RuntimeError("%s: frames of mixed sizes %s - re-render so that every frame has one size"
                           % (frames_dir(film, variant), {k: len(v) for k, v in sizes.items()}))
    return have, frame_start, frame_end


def encode(film, captions=None, fps=None, frame_start=None, frame_end=None, out_path=None, size=FINAL_SIZE,
           crf=16, audio=None, preset="medium", variant=None, allow_holds=False, time_origin=None, fades=None):
    """Upscale every frame to 1080x1920 (Lanczos), composite its caption AFTER the upscale and pipe to ffmpeg
    (H.264 yuv420p, +faststart). Returns the mp4 path. audio=FILE adds sound with mux_audio() (the picture is
    encoded exactly as without it; AAC 192k 48 kHz stereo from t = 0, as long as the picture).
    time_origin = the frame number at which the captions' clock reads 0 (default frame_start; encode_parts() passes
    the film's first frame for every part).
    fades = picture-gain ramps [t0, t1, g0, g1] on that same clock (default: the film's meta.json; see the module
    docstring): the picture is darkened after the upscale and before its caption is drawn.

    Only frames that are valid for the film's current signature count (see valid_frames). A frame that is missing
    from the range is an ERROR: a crashed render chunk must not turn into a stutter in the delivered film. Pass
    allow_holds=True for a deliberate --step preview: missing frames then hold the previous rendered frame, so the
    timing stays right. Frames of mixed pixel sizes are always an error.
    captions / fps / range default to the film's meta.json.
    """
    meta = read_meta(film, variant) or {}
    captions = meta.get("captions", []) if captions is None else captions
    fades = check_fades(meta.get("fades") if fades is None else fades)
    fps = int(fps or meta.get("fps", 24))
    have, frame_start, frame_end = usable_frames(film, variant, frame_start, frame_end, allow_holds)
    have_set = set(have)
    wanted = range(frame_start, frame_end + 1)
    origin = frame_start if time_origin is None else int(time_origin)
    if out_path is None:
        out_path = os.path.join(OUT, film + ".mp4") if not variant else \
            os.path.join(OUT, "preview", "%s_%s.mp4" % (film, variant))
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg is None:
        raise RuntimeError("ffmpeg not found on PATH")

    if audio and not os.path.exists(audio):
        raise RuntimeError("audio file %s does not exist" % audio)
    # the picture is always encoded on its own, by the same command whether or not sound follows: with audio it
    # goes to a temporary file first and mux_audio() copies its video stream, untouched, beside the sound
    video_path = out_path if not audio else out_path[:-4] + ".video_only.mp4"
    cmd = [ffmpeg, "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
           "-s", "%dx%d" % tuple(size), "-r", str(fps), "-i", "-"]
    cmd += ["-vf", "scale=out_color_matrix=bt709:out_range=tv,format=yuv420p",
            "-c:v", "libx264", "-preset", preset, "-crf", str(crf), "-pix_fmt", "yuv420p",
            "-profile:v", "high", "-r", str(fps),
            "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", "-color_range", "tv"]
    cmd += ["-an"]
    cmd += ["-movflags", "+faststart", video_path]

    first = have[0]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    t0 = time.time()
    src_frame, base = None, None
    missing = faded = 0
    try:
        for f in wanted:
            use = f
            if f not in have_set:
                missing += 1
                earlier = [h for h in have if h <= f]
                use = earlier[-1] if earlier else first
            if use != src_frame:
                with Image.open(frame_path(film, use, variant)) as im:
                    base = upscale(im, size)
                src_frame = use
            word = cap.caption_at(captions, (f - origin) / float(fps))
            pic = base
            if fades:
                gain = fade_gain(fades, (f - origin) / float(fps))
                if gain < 1.0:                                   # the picture only: the caption goes on top of it
                    pic = apply_gain(base, gain)
                    faded += 1
            out = cap.composite(pic.copy(), word) if word else pic
            proc.stdin.write(out.tobytes())
    finally:
        proc.stdin.close()
        code = proc.wait()
    if code != 0:
        raise RuntimeError("ffmpeg failed with exit code %d" % code)
    n = frame_end - frame_start + 1
    sound = ""
    if audio:
        try:
            info = mux_audio(video_path, audio, out_path)
        finally:
            if os.path.exists(video_path):
                os.remove(video_path)
        sound = ", sound %s (%s %d Hz %d ch, %.3f s)" % (os.path.relpath(audio, ROOT) if os.path.isabs(audio) else audio,
                                                        info["codec"], info["sample_rate"], info["channels"],
                                                        info["duration"])
    print(f"[encode] {out_path}: {n} frames ({n / fps:.2f} s) at {fps} fps, {size[0]}x{size[1]}, "
          f"{missing} held{', %d faded' % faded if fades else ''}{sound}, {time.time() - t0:.1f}s")
    return out_path


def _part_key(film, variant, a, b, origin, fps, size, crf, preset, captions, have, fades=()):
    """What a part of a film depends on: its frame files (name, size, modification time; with holds also the frame
    held into it), the captions visible in it, the fades that reach into it and the encoder settings. Same key =
    same bytes, not encoded again."""
    have_in = [f for f in have if a <= f <= b]
    earlier = [f for f in have if f < a]
    used = ([earlier[-1]] if earlier and (not have_in or have_in[0] > a) else []) + have_in
    stats = []
    for f in used:
        st = os.stat(frame_path(film, f, variant))
        stats.append([f, st.st_size, st.st_mtime_ns])
    t0, t1 = (a - origin) / float(fps), (b + 1 - origin) / float(fps)
    caps = [[str(c[0]), float(c[1]), float(c[2])] for c in captions if c[1] < t1 and c[2] > t0]
    what = [a, b, origin, fps, list(size), crf, preset, caps, stats]
    ramps = [list(r) for r in fades or () if r[0] < t1 and r[1] > t0]
    if ramps:                                                    # (a part without fades keeps the key it always had)
        what.append({"fades": ramps})
    blob = json.dumps(what, sort_keys=True)
    return hashlib.sha1(blob.encode("utf-8")).hexdigest()


def encode_parts(film, captions=None, fps=None, frame_start=None, frame_end=None, out_path=None, size=FINAL_SIZE,
                 crf=16, audio=None, preset="medium", variant=None, allow_holds=False, segment=SEGMENT_FRAMES,
                 deadline=None, first_always=True, fades=None):
    """encode() for a long film, in parts that survive an interrupted command. The range is cut into parts of
    `segment` frames; each is written by encode() (same settings, captions on the film's clock) to
    <out>.part_<a>-<b>.mp4 and recorded in <out>.parts.json with a key of everything it depends on; a part whose
    key is unchanged is not encoded again. When all parts exist they are joined with a stream copy (+faststart),
    the frame count is checked, `audio` is put under the whole film with mux_audio() and the parts are deleted.
    `deadline` (a time.time() value): no new part is started after it, except the first of this call (so that
    every call makes progress; first_always=False drops the exception, for a call that has already spent its time
    on something else). fades: as for encode() (a changed fade re-encodes only the parts it reaches into).
    Returns the mp4 path, or None when parts are still missing (call again with the same arguments)."""
    meta = read_meta(film, variant) or {}
    captions = meta.get("captions", []) if captions is None else captions
    fades = check_fades(meta.get("fades") if fades is None else fades)
    fps = int(fps or meta.get("fps", 24))
    have, frame_start, frame_end = usable_frames(film, variant, frame_start, frame_end, allow_holds)
    if audio and not os.path.exists(audio):
        raise RuntimeError("audio file %s does not exist" % audio)
    if out_path is None:
        out_path = os.path.join(OUT, film + ".mp4") if not variant else \
            os.path.join(OUT, "preview", "%s_%s.mp4" % (film, variant))
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg is None:
        raise RuntimeError("ffmpeg not found on PATH")
    stem = out_path[:-4]
    book_path = stem + ".parts.json"
    try:
        with open(book_path, encoding="utf-8") as f:
            book = json.load(f)
    except (OSError, ValueError):
        book = {}
    ranges = [(a, min(frame_end, a + int(segment) - 1)) for a in range(frame_start, frame_end + 1, int(segment))]
    names = {"%s.part_%04d-%04d.mp4" % (os.path.basename(stem), a, b) for a, b in ranges}
    for name in list(book):                                   # parts of another cut of the film: gone
        if name not in names:
            old = os.path.join(os.path.dirname(out_path), name)
            if os.path.exists(old):
                os.remove(old)
            del book[name]
    t0, made, todo, parts = time.time(), 0, 0, []
    for a, b in ranges:
        part = "%s.part_%04d-%04d.mp4" % (stem, a, b)
        name = os.path.basename(part)
        key = _part_key(film, variant, a, b, frame_start, fps, size, crf, preset, captions, have, fades)
        parts.append(part)
        if book.get(name) == key and os.path.exists(part):
            continue
        if deadline is not None and (made or not first_always) and time.time() > deadline:
            todo += 1
            continue
        book.pop(name, None)
        encode(film, captions=captions, fps=fps, frame_start=a, frame_end=b, out_path=part, size=size, crf=crf,
               preset=preset, variant=variant, allow_holds=allow_holds, time_origin=frame_start, fades=fades)
        book[name] = key
        with open(book_path + ".tmp", "w", encoding="utf-8") as f:
            json.dump(book, f, indent=1)
        os.replace(book_path + ".tmp", book_path)
        made += 1
    if todo:
        print("[encode] %s: %d of %d parts written (%d in this call, %.0f s); %d left: run the same command again"
              % (out_path, len(ranges) - todo, len(ranges), made, time.time() - t0, todo))
        return None
    n = frame_end - frame_start + 1
    listing = stem + ".parts.txt"
    with open(listing, "w", encoding="utf-8") as f:
        for part in parts:
            f.write("file '%s'\n" % os.path.abspath(part).replace("'", "'\\''"))
    video_path = out_path if not audio else stem + ".video_only.mp4"
    code = subprocess.call([ffmpeg, "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", listing,
                            "-c", "copy", "-an", "-movflags", "+faststart", video_path])
    if code != 0:
        raise RuntimeError("ffmpeg (joining the parts) failed with exit code %d" % code)
    joined = probe(video_path)
    if joined["frames"] != n or abs(joined["duration"] - n / float(fps)) > 0.5 / fps:
        raise RuntimeError("the joined film has %s frames in %.3f s, expected %d in %.3f s"
                           % (joined["frames"], joined["duration"], n, n / float(fps)))
    sound = ""
    if audio:
        try:
            info = mux_audio(video_path, audio, out_path)
        finally:
            if os.path.exists(video_path):
                os.remove(video_path)
        sound = ", sound %s (%s %d Hz %d ch, %.3f s)" % (os.path.relpath(audio, ROOT) if os.path.isabs(audio) else audio,
                                                        info["codec"], info["sample_rate"], info["channels"],
                                                        info["duration"])
    for path in parts + [listing, book_path]:
        if os.path.exists(path):
            os.remove(path)
    print("[encode] %s: %d frames (%.2f s) at %d fps in %d parts (%d encoded in this call)%s, %.1fs"
          % (out_path, n, n / float(fps), fps, len(ranges), made, sound, time.time() - t0))
    return out_path


def video_md5(path):
    """md5 of a file's video stream as stored (packets copied, nothing decoded): equal before and after mux_audio."""
    out = subprocess.check_output([shutil.which("ffmpeg"), "-v", "error", "-i", path, "-map", "0:v:0", "-c", "copy",
                                   "-f", "md5", "-"])
    return out.decode().strip().split("=")[-1]


def probe_audio(path):
    """ffprobe summary of the first audio stream: {'codec', 'sample_rate', 'channels', 'duration', 'start_time',
    'bit_rate'}, or None when the file has no sound."""
    out = subprocess.check_output([
        shutil.which("ffprobe"), "-v", "error", "-select_streams", "a:0", "-show_entries",
        "stream=codec_name,sample_rate,channels,duration,start_time,bit_rate", "-of", "json", path])
    streams = json.loads(out).get("streams", [])
    if not streams:
        return None
    a = streams[0]
    return {"codec": a.get("codec_name"), "sample_rate": int(a.get("sample_rate", 0)), "channels": int(a.get("channels", 0)),
            "duration": float(a.get("duration", 0.0) or 0.0), "start_time": float(a.get("start_time", 0.0) or 0.0),
            "bit_rate": int(a.get("bit_rate", 0) or 0)}


def mux_audio(video, audio, out_path=None, gain_db=None):
    """Put `audio` under the finished film `video` (an mp4): the video stream is COPIED (not one bit of the picture
    changes: video_md5 is the same before and after), the audio becomes AAC 192 kb/s 48 kHz stereo, starts at t = 0
    and is padded with silence or cut to exactly the length of the picture; the mp4 is written +faststart.
    A mono file (a narration) becomes dual mono with DUAL_MONO_GAIN_DB on each channel (gain_db overrides it); a
    stereo file is used as it is. out_path None replaces `video` itself. Returns probe_audio() of the result."""
    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg is None:
        raise RuntimeError("ffmpeg not found on PATH")
    v = probe(video)
    if not v["frames"] or not v["fps"]:
        raise RuntimeError("%s has no video frames" % video)
    src = probe_audio(audio)
    if src is None:
        raise RuntimeError("%s has no audio stream" % audio)
    samples = int(round(v["frames"] / v["fps"] * AUDIO_RATE))        # 24 fps: exactly 2000 samples per frame
    codec = ["-c:a", "aac", "-b:a", AUDIO_BITRATE]
    if src["channels"] == 1:
        k = 10.0 ** ((DUAL_MONO_GAIN_DB if gain_db is None else gain_db) / 20.0)
        layout = "pan=stereo|c0=%.6f*c0|c1=%.6f*c0" % (k, k)
        # Dual mono must come out of the decoder as two IDENTICAL channels. The encoder is told to code mid / side
        # (the side channel of two equal channels is exactly zero) and to use neither intensity stereo nor
        # perceptual noise substitution, which fills quiet bands with noise that differs left and right.
        # Measured on a 62 s narration, max |L - R| after decoding: defaults -40 dB, without PNS -53 dB,
        # M/S forced with intensity stereo left on -20 dB, all three as here 0 (bit-identical).
        codec += ["-aac_pns", "0", "-aac_is", "0", "-aac_ms", "1"]
    else:
        layout = "aformat=channel_layouts=stereo" + ("" if not gain_db else ",volume=%.3fdB" % gain_db)
    chain = "[1:a:0]aresample=%d,%s,apad=whole_len=%d,atrim=end_sample=%d[a]" % (AUDIO_RATE, layout, samples, samples)
    final = out_path or video
    tmp = final[:-4] + ".mux_part.mp4"
    before = video_md5(video)
    cmd = [ffmpeg, "-y", "-loglevel", "error", "-i", video, "-i", audio, "-filter_complex", chain,
           "-map", "0:v:0", "-map", "[a]", "-c:v", "copy"] + codec + [
           "-ar", str(AUDIO_RATE), "-ac", "2", "-movflags", "+faststart", tmp]
    code = subprocess.call(cmd)
    if code != 0:
        if os.path.exists(tmp):
            os.remove(tmp)
        raise RuntimeError("ffmpeg (audio mux) failed with exit code %d" % code)
    if video_md5(tmp) != before:
        os.remove(tmp)
        raise RuntimeError("the video stream changed while muxing audio into %s" % video)
    os.replace(tmp, final)
    return probe_audio(final)


def probe(path):
    """ffprobe summary of a video file: {'width', 'height', 'fps', 'pix_fmt', 'codec', 'duration', 'frames'}."""
    ffprobe = shutil.which("ffprobe")
    if ffprobe is None:
        raise RuntimeError("ffprobe not found on PATH")
    out = subprocess.check_output([
        ffprobe, "-v", "error", "-select_streams", "v:0", "-count_frames", "-show_entries",
        "stream=width,height,r_frame_rate,pix_fmt,codec_name,duration,nb_read_frames", "-of", "json", path])
    s = json.loads(out)["streams"][0]
    num, den = s["r_frame_rate"].split("/")
    return {"width": s["width"], "height": s["height"], "fps": float(num) / float(den), "pix_fmt": s["pix_fmt"],
            "codec": s["codec_name"], "duration": float(s.get("duration", 0.0)),
            "frames": int(s.get("nb_read_frames", 0))}


if __name__ == "__main__":
    # self-test without Blender: fake frames -> sheet + mp4 -> ffprobe
    import numpy as np

    film = "_posttest"
    os.makedirs(frames_dir(film), exist_ok=True)
    caps = cap.autotime("The real Minecraft font, word by word.", start=0.0, per_word=0.25, comma=0.1, period=0.2)
    tex = os.path.join(ROOT, "assets", "mc", "assets", "minecraft", "textures", "block")
    names = ["oak_planks", "cobblestone", "stone_bricks", "grass_block_top"]
    tiles = []
    for f in range(1, 37, 2):                                     # every 2nd frame only: tests the hold logic
        t = Image.open(os.path.join(tex, names[(f // 9) % len(names)] + ".png")).convert("RGB")
        arr = np.asarray(t.resize((720, 720), Image.NEAREST))
        arr = np.roll(arr, f * 6, axis=1)
        frame = Image.new("RGB", (720, 1280), (90, 120, 200))
        frame.paste(Image.fromarray(arr), (0, 560))
        frame.save(frame_path(film, f))
        if f % 6 == 1:
            tiles.append(frame.resize((180, 320), Image.LANCZOS))
    write_meta(film, {"fps": 24, "frame_start": 1, "frame_end": 36, "captions": caps, "signature": "selftest",
                      "frames": {str(f): "selftest" for f in range(1, 37, 2)}})
    words = [cap.caption_at(caps, (f - 1) / 24.0) for f in range(1, 37, 6)]
    print("wrote", contact_sheet(tiles, ["%.2fs" % ((f - 1) / 24.0) for f in range(1, 37, 6)], words,
                                 os.path.join(OUT, "test", "post_sheet.png")))
    try:
        encode(film, out_path=os.path.join(OUT, "test", "post_test.mp4"))
        raise SystemExit("encode() must refuse a film with missing frames")
    except RuntimeError as e:
        print("refused as it should:", str(e)[:90], "...")
    mp4 = encode(film, out_path=os.path.join(OUT, "test", "post_test.mp4"), allow_holds=True)
    print(probe(mp4))
    # sound: a one-second mono tone under the 1.5 s film. The picture must not change by one bit, the audio must be
    # AAC 48 kHz stereo from t = 0 and as long as the picture (the missing half second is silence)
    tone = os.path.join(OUT, "test", "post_test_tone.wav")
    subprocess.check_call([shutil.which("ffmpeg"), "-y", "-loglevel", "error", "-f", "lavfi", "-i",
                           "sine=frequency=440:duration=1.0:sample_rate=24000", "-ac", "1", tone])
    with_sound = os.path.join(OUT, "test", "post_test_sound.mp4")
    info = mux_audio(mp4, tone, with_sound)
    assert video_md5(with_sound) == video_md5(mp4), "mux_audio changed the picture"
    assert (info["codec"], info["sample_rate"], info["channels"]) == ("aac", 48000, 2), info
    assert abs(info["duration"] - 1.5) < 0.002 and abs(info["start_time"]) < 1e-6, info
    silent = encode(film, out_path=os.path.join(OUT, "test", "post_test_again.mp4"), allow_holds=True, audio=tone)
    assert video_md5(silent) == video_md5(mp4) and probe_audio(silent)["channels"] == 2
    print("sound:", info, "- picture stream identical with and without it")
    # a long film in parts: three parts of 12 frames, the command "interrupted" after every part (a deadline in the
    # past allows one part per call). The result must be the same film as the one-pass encode: frame count, length,
    # every decoded picture with its caption (not the same bits: each part starts its own GOP), sound from t = 0
    parted = os.path.join(OUT, "test", "post_test_parts.mp4")
    calls = 0
    while encode_parts(film, out_path=parted, allow_holds=True, audio=tone, segment=12, deadline=0.0) is None:
        calls += 1
        assert calls < 5 and os.path.exists(parted[:-4] + ".parts.json")
    assert calls == 2, calls                                      # two unfinished calls, the third joins
    one, many = probe(mp4), probe(parted)
    assert many["frames"] == one["frames"] == 36 and abs(many["duration"] - one["duration"]) < 1e-3, (one, many)

    def decoded(path):
        raw = subprocess.check_output([shutil.which("ffmpeg"), "-v", "error", "-i", path, "-map", "0:v:0", "-vf",
                                       "scale=270:480", "-f", "rawvideo", "-pix_fmt", "gray", "-"])
        return np.frombuffer(raw, dtype=np.uint8).reshape(-1, 480, 270).astype(np.float32)

    a, b = decoded(mp4), decoded(parted)
    worst = float(np.abs(a - b).mean(axis=(1, 2)).max())
    assert a.shape == b.shape and worst < 1.5, (a.shape, b.shape, worst)
    sound = probe_audio(parted)
    assert sound["channels"] == 2 and abs(sound["duration"] - 1.5) < 0.002 and abs(sound["start_time"]) < 1e-6, sound
    left = [n for n in os.listdir(os.path.join(OUT, "test")) if n.startswith("post_test_parts.") and n != "post_test_parts.mp4"]
    assert not left, left
    print("parts: 3 parts over 3 calls -> %d frames, %.3f s, largest mean picture difference to the one-pass film "
          "%.2f of 255, sound %s" % (many["frames"], many["duration"], worst, sound))
    # fades: a dip to black around frame 19 (black ON it, three frames out, two held, three back). The picture goes
    # dark, the caption on top of it does not; a film without fades is the same file as before, bit for bit
    t = lambda f: (f - 1) / 24.0                                  # noqa: E731
    dip = [(t(16), t(19), 1.0, 0.0), (t(19), t(21), 0.0, 0.0), (t(21), t(24), 0.0, 1.0)]
    gains = [round(fade_gain(check_fades(dip), t(f)), 4) for f in range(15, 26)]
    assert gains == [1.0, 1.0, 0.6667, 0.3333, 0.0, 0.0, 0.0, 0.3333, 0.6667, 1.0, 1.0], gains
    plain = encode(film, out_path=os.path.join(OUT, "test", "post_test_nofade.mp4"), allow_holds=True, fades=[])
    assert video_md5(plain) == video_md5(mp4), "an empty fade list changed the encode"
    dipped = encode(film, out_path=os.path.join(OUT, "test", "post_test_fade.mp4"), allow_holds=True, fades=dip)
    c = decoded(dipped)
    word19 = cap.caption_at(caps, t(19))
    band = slice(int(480 * cap.CAPTION_BAND[0]), int(480 * cap.CAPTION_BAND[1]))
    sky = slice(0, 100)                                            # the top of the fake frame: flat blue, no caption
    assert word19 and c[18, sky].mean() < 20.0 and a[18, sky].mean() > 80.0, (word19, c[18, sky].mean(), a[18, sky].mean())
    assert c[18, band].max() > 200.0, c[18, band].max()            # the caption is still white on the black frame
    assert abs(c[14, sky].mean() - a[14, sky].mean()) < 1.0 and abs(c[24, sky].mean() - a[24, sky].mean()) < 1.0
    ratio = float(c[16, sky].mean() / a[16, sky].mean())           # frame 17: gain 2/3 (limited-range video: about)
    assert 0.55 < ratio < 0.78, ratio
    calls = 0
    part_fade = os.path.join(OUT, "test", "post_test_parts_fade.mp4")
    while encode_parts(film, out_path=part_fade, allow_holds=True, segment=12, deadline=0.0, fades=dip) is None:
        calls += 1
        assert calls < 5
    d = decoded(part_fade)
    assert d.shape == c.shape and float(np.abs(d - c).mean(axis=(1, 2)).max()) < 1.5
    k0 = _part_key(film, None, 1, 12, 1, 24, FINAL_SIZE, 16, "medium", caps, [1, 3, 5, 7, 9, 11])
    assert k0 == _part_key(film, None, 1, 12, 1, 24, FINAL_SIZE, 16, "medium", caps, [1, 3, 5, 7, 9, 11], check_fades(dip)), \
        "a fade outside a part changed its key"
    assert _part_key(film, None, 13, 24, 1, 24, FINAL_SIZE, 16, "medium", caps, [13, 15], check_fades(dip)) != \
        _part_key(film, None, 13, 24, 1, 24, FINAL_SIZE, 16, "medium", caps, [13, 15])
    Image.fromarray(np.concatenate([c[i] for i in (15, 16, 17, 18, 20, 21, 22, 23)], axis=1).astype(np.uint8)).save(
        os.path.join(OUT, "test", "post_fade_strip.png"))
    print("fades: gains of frames 15-25 %s; frame 19 picture %.1f of 255 (was %.1f), its caption %r still at %.0f; "
          "frame 17 at %.2f of its brightness; no fades = the same file; in parts the same pictures"
          % (gains, c[18, sky].mean(), a[18, sky].mean(), word19, c[18, band].max(), ratio))
