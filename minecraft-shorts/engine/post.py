"""Post: frame bookkeeping, caption compositing, contact sheets and the H.264 encode (PIL + ffmpeg, no Blender).

FINAL frames (720x1280, 24 samples, every frame) live in out/frames/<film>/f_####.png (#### = frame number, frame
1 = second 0). Anything rendered with other settings is a PREVIEW and lives apart, in
out/preview/<film>/<W>x<H>_<N>spp[_stepK]/ (a `variant`), so a cheap preview can never end up inside a final film.
Next to the frames sits meta.json, which render.py writes after building a film: fps, frame range, captions, shot
list, the render settings, a hash of the sources that built the film, for every rendered frame its stamp (settings,
engine-source hash, scene fingerprint: see render.py and engine/stamp.py) and, under 'current', what each frame
should carry now. A frame counts only while its stamp is the current one.
"""
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


def finish_frame(img, word=None, size=FINAL_SIZE):
    """Upscale a rendered frame and draw the caption word on it (None = no caption)."""
    return cap.composite(upscale(img, size), word)


def contact_sheet(tiles, labels, words, path, columns=None, gap=6):
    """Grid of small frames with their caption drawn in and a label (time / shot) above each; saves a PNG."""
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
        sheet.paste(cap.composite(tile, word), (x, y + head))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    sheet.save(path)
    return path


def encode(film, captions=None, fps=None, frame_start=None, frame_end=None, out_path=None, size=FINAL_SIZE,
           crf=16, audio=None, preset="medium", variant=None, allow_holds=False):
    """Upscale every frame to 1080x1920 (Lanczos), composite its caption AFTER the upscale and pipe to ffmpeg
    (H.264 yuv420p, +faststart). Returns the mp4 path.

    Only frames that are valid for the film's current signature count (see valid_frames). A frame that is missing
    from the range is an ERROR: a crashed render chunk must not turn into a stutter in the delivered film. Pass
    allow_holds=True for a deliberate --step preview: missing frames then hold the previous rendered frame, so the
    timing stays right. Frames of mixed pixel sizes are always an error.
    captions / fps / range default to the film's meta.json.
    """
    meta = read_meta(film, variant) or {}
    captions = meta.get("captions", []) if captions is None else captions
    fps = int(fps or meta.get("fps", 24))
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
    if out_path is None:
        out_path = os.path.join(OUT, film + ".mp4") if not variant else \
            os.path.join(OUT, "preview", "%s_%s.mp4" % (film, variant))
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg is None:
        raise RuntimeError("ffmpeg not found on PATH")

    cmd = [ffmpeg, "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
           "-s", "%dx%d" % tuple(size), "-r", str(fps), "-i", "-"]
    if audio:
        cmd += ["-i", audio]
    cmd += ["-vf", "scale=out_color_matrix=bt709:out_range=tv,format=yuv420p",
            "-c:v", "libx264", "-preset", preset, "-crf", str(crf), "-pix_fmt", "yuv420p",
            "-profile:v", "high", "-r", str(fps),
            "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", "-color_range", "tv"]
    if audio:
        cmd += ["-c:a", "aac", "-b:a", "192k", "-shortest"]
    else:
        cmd += ["-an"]
    cmd += ["-movflags", "+faststart", out_path]

    first = have[0]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    t0 = time.time()
    src_frame, base = None, None
    missing = 0
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
            word = cap.caption_at(captions, (f - frame_start) / float(fps))
            out = cap.composite(base.copy(), word) if word else base
            proc.stdin.write(out.tobytes())
    finally:
        proc.stdin.close()
        code = proc.wait()
    if code != 0:
        raise RuntimeError("ffmpeg failed with exit code %d" % code)
    n = frame_end - frame_start + 1
    print(f"[encode] {out_path}: {n} frames ({n / fps:.2f} s) at {fps} fps, {size[0]}x{size[1]}, "
          f"{missing} held, {time.time() - t0:.1f}s")
    return out_path


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
