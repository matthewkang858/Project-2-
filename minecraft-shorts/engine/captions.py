"""Word-by-word captions in the REAL Minecraft font (no Blender needed, PIL + numpy only).

Glyphs are cut from the game's own bitmap font: `font/include/default.json` names the bitmap provider for
`textures/font/ascii.png` (16 rows of 16 characters, 8x8 cells, ascent 7) and `font/include/space.json` gives the
advance of the space. Glyph widths are measured exactly like the game does (last non-empty column of the cell,
+1 font pixel between glyphs). The word is drawn white with the game's drop shadow (text colour x 0.25, one font
pixel down-right) and a thin dark outline, scaled by an integer factor with nearest-neighbour.

    words = autotime("When the bell rings, we run home.")     # [(word, t0, t1), ...]
    overlay = draw_caption("bell")                             # RGBA, 1080x1920, composite over the frame
"""
import functools
import json
import os
import re

import numpy as np
from PIL import Image, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MC = os.path.join(ROOT, "assets", "mc", "assets", "minecraft")
TEST_DIR = os.path.join(ROOT, "out", "test")

SHADOW_FACTOR = 0.25          # the game draws the shadow in the text colour multiplied by 0.25
# Position and size were measured on the reference reel IN VIDEO COORDINATES. The screenshots are 1179x2556 phone
# screens on which the 9:16 video is height-filled down to y = 2333 (so about 5 % of each side is cropped away and one
# video pixel at 1080x1920 is 1.215 screen pixels): the caption's baseline sits at 1618 / 2333 = 69.4 % of the video
# height (glyph tops at 63.3 %), and one font pixel is 20.4 screen px = 16.8 video px.
BASELINE = 0.69               # baseline position, fraction of the frame height from the top
SCALE_1080 = 17               # screen pixels per font pixel on a 1080-wide frame (6-letter 'sleeps' = 32 font px = 50 %)
CAPTION_BAND = (0.62, 0.72)   # the part of the frame height a caption covers (glyph tops .. shadow under descenders)
# Longer words get a smaller integer scale so they never exceed this share of the width. 0.68 keeps a centred word
# inside x 16-84 %: the Reels icon column starts at 84 % (engine/post.py UI_ZONES) and the widest caption of the
# reference ('forgets') ends at about 80 %. Of both scripts only 'Everyone' (47 font px) is affected: scale 15.
MAX_WIDTH = 0.68
OUTLINE_1080 = 3              # outline thickness in screen pixels on a 1080-wide frame
PUNCT = ".,!?;:"              # trailing characters that are stripped from the displayed word


class Font:
    """One bitmap font provider: boolean glyph masks, advances, cell height and ascent."""

    def __init__(self, glyphs, advances, height, ascent):
        self.glyphs, self.advances, self.height, self.ascent = glyphs, advances, height, ascent

    def text_width(self, text):
        """Width of `text` in font pixels (advances summed, without the trailing 1-px gap)."""
        if not text:
            return 0
        w = sum(self.advances.get(ch, self.advances["?"]) for ch in text)
        last = text[-1]
        return w - (1 if last in self.glyphs else 0)

    def mask(self, text):
        """Boolean array (height, text_width) with the glyph pixels of `text`, exactly as the game lays them out."""
        w = max(1, self.text_width(text))
        out = np.zeros((self.height, w), dtype=bool)
        x = 0
        for ch in text:
            if ch not in self.advances:
                ch = "?"
            g = self.glyphs.get(ch)
            if g is not None:
                gw = min(g.shape[1], w - x)
                out[:, x:x + gw] |= g[:, :gw]
            x += self.advances[ch]
        return out


def _texture_rgba(rel):
    """Game texture (path under textures/, with or without .png) as HxWx4 uint8, read through engine.mcassets when
    Blender is available (mcassets imports bpy) and straight from the same file otherwise (captions need no Blender)."""
    try:
        from . import mcassets

        return np.array(mcassets.texture_array(rel))
    except ImportError:
        rel = rel if rel.endswith(".png") else rel + ".png"
        return np.array(Image.open(os.path.join(MC, "textures", rel)).convert("RGBA"))


@functools.lru_cache(maxsize=None)
def load_font():
    """Read the default font's ascii.png provider (layout from font/include/default.json) and the space advance."""
    with open(os.path.join(MC, "font", "include", "default.json"), encoding="utf-8") as f:
        providers = json.load(f)["providers"]
    prov = next(p for p in providers if p.get("type") == "bitmap" and p.get("file", "").endswith("font/ascii.png"))
    rows = prov["chars"]
    height = int(prov.get("height", 8))
    ascent = int(prov["ascent"])
    png = prov["file"].split(":", 1)[-1]
    img = _texture_rgba(png)
    cell_w = img.shape[1] // len(rows[0])
    cell_h = img.shape[0] // len(rows)
    scale = height / cell_h
    glyphs, advances = {}, {}
    for r, row in enumerate(rows):
        for c, ch in enumerate(row):
            if ch == "\x00":
                continue
            cell = img[r * cell_h:(r + 1) * cell_h, c * cell_w:(c + 1) * cell_w, 3] != 0
            cols = np.flatnonzero(cell.any(axis=0))
            actual = int(cols[-1]) + 1 if len(cols) else 0          # the game's getActualGlyphWidth
            if cell_h != height:                                    # not the case for ascii.png (8 px cells)
                cell = np.array(Image.fromarray(cell).resize((max(1, round(cell_w * scale)), height), Image.NEAREST))
            glyphs[ch] = cell[:, :max(1, int(0.5 + actual * scale))]
            advances[ch] = int(0.5 + actual * scale) + 1            # glyph width + 1 px gap, as in BitmapProvider
    with open(os.path.join(MC, "font", "include", "space.json"), encoding="utf-8") as f:
        for p in json.load(f)["providers"]:
            if p.get("type") == "space":
                for ch, adv in p["advances"].items():
                    advances[ch] = int(adv)
                    glyphs.pop(ch, None)
    return Font(glyphs, advances, height, ascent)


def display_word(token):
    """What is shown for a script token: trailing punctuation removed, apostrophes kept ('rings,' -> 'rings')."""
    w = token.replace("’", "'").strip()
    w = w.rstrip(PUNCT + "\"")
    return w.lstrip("\"")


def autotime(script, start=0.3, per_word=0.36, comma=0.12, period=0.45, end=None):
    """Split a script into one-word captions [(word, t0, t1), ...]; words are contiguous and hold through pauses.

    Every word is shown for `per_word` seconds; a word followed by , ; : holds `comma` seconds longer and a word
    that ends a sentence (. ! ?) holds `period` seconds longer, so the next word starts exactly when it ends.
    end=T stretches (or squeezes) per_word, comma and period by one common factor so that the last word ends at T
    seconds: with the defaults "The Bell" (20 words) would be over at 8.97 s, short of a 10-14 s film; pass the
    film's own length, e.g. autotime(script, end=11.5), or give the timing explicitly.
    """
    if end is not None:
        plain = autotime(script, start=0.0, per_word=per_word, comma=comma, period=period)
        if plain and plain[-1][2] > 0 and float(end) > float(start):
            k = (float(end) - float(start)) / plain[-1][2]
            per_word, comma, period = per_word * k, comma * k, period * k
    out = []
    t = float(start)
    for token in script.split():
        word = display_word(token)
        if not word:
            continue
        stripped = token.rstrip("\"'’")
        pause = 0.0
        if stripped.endswith((".", "!", "?")):
            pause = period
        elif stripped.endswith((",", ";", ":")):
            pause = comma
        t1 = t + per_word + pause
        out.append((word, round(t, 4), round(t1, 4)))
        t = t1
    return out


def caption_at(captions, t):
    """The word visible at time t (seconds) or None."""
    for word, t0, t1 in captions:
        if t0 <= t < t1:
            return word
    return None


def pick_scale(word, width=1080, scale=None):
    """Integer screen pixels per font pixel for `word` on a frame `width` wide (shrinks for long words)."""
    font = load_font()
    if scale is None:
        scale = max(1, int(round(SCALE_1080 * width / 1080.0)))
    limit = MAX_WIDTH * width
    while scale > 1 and font.text_width(word) * scale > limit:
        scale -= 1
    return scale


def render_text(text, scale, color=(255, 255, 255), shadow=True, outline=0, outline_color=(12, 12, 14),
                outline_alpha=235):
    """RGBA image of `text` in the Minecraft font at integer `scale`; returns (image, (x_text, y_top)).

    The image has a margin for the shadow and outline; (x_text, y_top) is where the top-left of the glyph cell
    sits inside it, so the baseline is at y_top + ascent * scale.
    """
    font = load_font()
    m = font.mask(text)
    h, w = m.shape
    pad = outline + 1
    W, H = (w + 1) * scale + 2 * pad, (h + 1) * scale + 2 * pad
    big = np.kron(m, np.ones((scale, scale), dtype=bool))
    text_mask = np.zeros((H, W), dtype=bool)
    text_mask[pad:pad + h * scale, pad:pad + w * scale] = big
    shadow_mask = np.zeros((H, W), dtype=bool)
    if shadow:
        shadow_mask[pad + scale:pad + (h + 1) * scale, pad + scale:pad + (w + 1) * scale] = big
    out = np.zeros((H, W, 4), dtype=np.uint8)
    if outline > 0:
        solid = Image.fromarray(((text_mask | shadow_mask) * 255).astype(np.uint8))
        grown = np.array(solid.filter(ImageFilter.MaxFilter(2 * outline + 1))) > 0
        out[grown] = (*outline_color, outline_alpha)
    if shadow:
        out[shadow_mask] = (*[int(c * SHADOW_FACTOR) for c in color], 255)
    out[text_mask] = (*color, 255)
    return Image.fromarray(out, "RGBA"), (pad, pad)


@functools.lru_cache(maxsize=256)
def _caption_cached(word, size, baseline, scale):
    font = load_font()
    W, H = size
    s = pick_scale(word, W, scale)
    outline = max(1, int(round(OUTLINE_1080 * s / SCALE_1080)))
    img, (ox, oy) = render_text(word, s, outline=outline)
    text_w = font.text_width(word) * s
    x = int(round((W - text_w) / 2.0)) - ox
    y = int(round(H * baseline)) - font.ascent * s - oy
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    layer.paste(img, (x, y))
    return layer


def draw_caption(word, size=(1080, 1920), baseline=BASELINE, scale=None):
    """Full-frame RGBA overlay with `word` centred, baseline 69 % down, in the real Minecraft font with shadow + outline."""
    return _caption_cached(word, tuple(size), float(baseline), scale).copy()


def composite(frame, word, baseline=BASELINE, scale=None):
    """Return `frame` (PIL image, any mode) as RGB with the caption `word` drawn on it (None/'' = unchanged)."""
    rgb = frame.convert("RGB")
    if not word:
        return rgb
    layer = _caption_cached(word, rgb.size, float(baseline), scale)
    box = layer.getbbox()
    if box is None:
        return rgb
    rgb.paste(layer.crop(box), box[:2], layer.crop(box))
    return rgb


def label(text, scale=2, color=(255, 255, 255)):
    """Small RGBA label in the Minecraft font with drop shadow (used by the contact sheet)."""
    return render_text(text, scale, color=color, shadow=True, outline=1)[0]


def _busy_background(size, names, gain, seed):
    """Stand-in footage: a patchwork of real block textures, upscaled, for judging legibility."""
    rng = np.random.default_rng(seed)
    W, H = size
    tile = 120
    bg = Image.new("RGB", size)
    tex = []
    for n in names:
        p = os.path.join(MC, "textures", "block", n + ".png")
        if os.path.exists(p):
            t = Image.open(p).convert("RGB").crop((0, 0, 16, 16)).resize((tile, tile), Image.NEAREST)
            tex.append(t)
    for y in range(0, H, tile):
        band = (y // (tile * 3)) % len(tex)
        for x in range(0, W, tile):
            t = tex[(band + int(rng.integers(0, 2))) % len(tex)]
            bg.paste(t, (x, y))
    arr = np.asarray(bg).astype(np.float32) * gain
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGB")


if __name__ == "__main__":
    os.makedirs(TEST_DIR, exist_ok=True)
    font = load_font()
    print("font: height", font.height, "ascent", font.ascent, "glyphs", len(font.glyphs), "space advance", font.advances[" "])
    for w in ("sleeps", "bed", "forgets", "Everyone", "don't", "I'm", "rings,", "il.,'"):
        s = pick_scale(w)
        print(f"  {w!r:12s} width {font.text_width(w):3d} font px, scale {s:2d}, {100 * font.text_width(w) * s / 1080:.1f} % of 1080")
    script = "When the bell rings, we run home. We count who made it. He rings it because he likes the sound."
    for c in autotime(script):
        print("  ", c)
    fitted = autotime(script, end=11.5)
    assert abs(fitted[-1][2] - 11.5) < 1e-3 and all(abs(a[2] - b[1]) < 1e-3 for a, b in zip(fitted, fitted[1:]))
    print("   end=11.5 ->", fitted[0], "...", fitted[-1], "shortest word %.2f s" % min(c[2] - c[1] for c in fitted))
    words = ["bell", "rings,", "sound.", "Everyone", "don't", "I'm"]
    lines = [0.16, 0.30, 0.44, BASELINE, 0.82, 0.93]
    sets = {
        "dark": (["deepslate_bricks", "dark_oak_planks", "obsidian", "spruce_log", "blackstone", "mossy_cobblestone"], 0.55),
        "bright": (["birch_planks", "sand", "white_wool", "quartz_block_side", "snow", "oak_planks", "grass_block_top"], 1.25),
    }
    for name, (texs, gain) in sets.items():
        frame = _busy_background((1080, 1920), texs, gain, seed=3)
        for w, b in zip(words, lines):
            frame = composite(frame, w, baseline=b)
        path = os.path.join(TEST_DIR, f"captions_test_{name}.png")
        frame.save(path)
        print("wrote", path)
