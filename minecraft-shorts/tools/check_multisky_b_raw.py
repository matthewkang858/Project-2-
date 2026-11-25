"""Checker B: raw rendered frames of a frame directory side by side (nearest-neighbour upscaled).

    $BPY -m tools.check_multisky_b_raw DIR OUT.png SCALE F1,F2,...
"""
import sys

from PIL import Image, ImageDraw


def main(argv):
    d, out, scale = argv[0], argv[1], float(argv[2])
    fs = [int(x) for x in argv[3].split(",")]
    ims = [Image.open("%s/f_%04d.png" % (d, f)).convert("RGB") for f in fs]
    w, h = int(ims[0].size[0] * scale), int(ims[0].size[1] * scale)
    sheet = Image.new("RGB", (len(fs) * (w + 4), h + 16), (30, 30, 34))
    dr = ImageDraw.Draw(sheet)
    for i, (f, im) in enumerate(zip(fs, ims)):
        sheet.paste(im.resize((w, h), Image.NEAREST if scale >= 1 else Image.LANCZOS), (i * (w + 4), 16))
        dr.text((i * (w + 4) + 3, 2), "f%d" % f, fill=(255, 255, 255))
    sheet.save(out)
    print("->", out, sheet.size)


if __name__ == "__main__":
    main(sys.argv[1:])
