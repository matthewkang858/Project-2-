"""Checker probe for tools/render_economics.py: my own blind pairs of the reference against a candidate, many
trials. For each study shot, four regions (around the study's face / texels / thin / defocus crop centres) of the
delivered 1080x1920 frame, shown at SCALE (phone = 540x960, insta = 720x1280, full = 1080x1920), reference and
candidate side by side in an order drawn from os.urandom. The key goes to out/test/check_economics_blind_key_*.json
and is read only after judging. Unlabelled sheets: out/test/check_economics_blind_<scale>_<shot>.png (pairs
numbered 1-4 by position: top-left, top-right, bottom-left, bottom-right; within a pair: L | R).

    $BPY -m tools.check_economics_blind phone|insta|full [VARIANT]
"""
import json
import os
import sys

from PIL import Image

from tools import render_economics as E

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "out", "test")
SCALES = {"phone": (540, 960), "insta": (720, 1280), "full": (1080, 1920)}
TILE = {"phone": (264, 392), "insta": (352, 472), "full": (352, 472)}


def main(argv):
    scale = argv[0]
    variant = argv[1] if len(argv) > 1 else "r540s16"
    size = SCALES[scale]
    tw, th = TILE[scale]
    key = {}
    for shot in ("dusk", "hall", "sun", "night", "face"):
        rp, vp = E.ref_path(shot), E.variant_path(shot, variant)
        ref = E.deliver(rp).resize(size, Image.LANCZOS) if size != E.DELIVERY else E.deliver(rp)
        cand = E.deliver(vp).resize(size, Image.LANCZOS) if size != E.DELIVERY else E.deliver(vp)
        sheet = Image.new("RGB", (4 * tw + 3 * 8 + 24, 2 * th + 24), (60, 0, 60))
        for i, cn in enumerate(("face", "texels", "thin", "defocus")):
            cx, cy = E.CROPS[shot][cn]
            x = int(min(max(cx * size[0] - tw / 2, 0), size[0] - tw))
            y = int(min(max(cy * size[1] - th / 2, 0), size[1] - th))
            a, b = ref.crop((x, y, x + tw, y + th)), cand.crop((x, y, x + tw, y + th))
            where = "L" if os.urandom(1)[0] & 1 else "R"           # where the REFERENCE is
            key["%s_%d_%s" % (shot, i + 1, cn)] = where
            pair = (a, b) if where == "L" else (b, a)
            px = (i % 2) * (2 * tw + 8 + 24)
            py = (i // 2) * (th + 24)
            sheet.paste(pair[0], (px, py))
            sheet.paste(pair[1], (px + tw + 8, py))
        sheet.save(os.path.join(OUT, "check_economics_blind_%s_%s_%s.png" % (scale, variant, shot)))
    with open(os.path.join(OUT, "check_economics_blind_key_%s_%s.json" % (scale, variant)), "w", encoding="utf-8") as f:
        json.dump(key, f, indent=1, sort_keys=True)
    print("wrote 5 sheets and the key (not printed)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
