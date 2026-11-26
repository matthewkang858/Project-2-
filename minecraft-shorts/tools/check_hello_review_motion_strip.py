"""Review probe (motion lens): a labelled strip of consecutive preview frames, optionally cropped and enlarged.

    python3 tools/check_hello_review_motion_strip.py OUT.png FIRST LAST [--step N] [--crop x0,y0,x1,y1]
            [--scale S] [--cols C] [--src DIR]

Crop in source pixels (360x640). Each tile is labelled with its frame number.
"""
import argparse
import os

from PIL import Image, ImageDraw


def main():
    p = argparse.ArgumentParser()
    p.add_argument("out")
    p.add_argument("first", type=int)
    p.add_argument("last", type=int)
    p.add_argument("--step", type=int, default=1)
    p.add_argument("--crop", default=None)
    p.add_argument("--scale", type=float, default=1.0)
    p.add_argument("--cols", type=int, default=8)
    p.add_argument("--src", default="out/preview/hello/360x640_8spp")
    p.add_argument("--frames", default=None, help="comma list instead of first..last")
    a = p.parse_args()
    frames = [int(x) for x in a.frames.split(",")] if a.frames else list(range(a.first, a.last + 1, a.step))
    tiles = []
    for f in frames:
        im = Image.open(os.path.join(a.src, "f_%04d.png" % f)).convert("RGB")
        if a.crop:
            x0, y0, x1, y1 = [int(v) for v in a.crop.split(",")]
            im = im.crop((x0, y0, x1, y1))
        if a.scale != 1.0:
            im = im.resize((int(im.width * a.scale), int(im.height * a.scale)), Image.NEAREST)
        d = ImageDraw.Draw(im)
        d.rectangle((0, 0, 44, 14), fill=(0, 0, 0))
        d.text((2, 1), str(f), fill=(255, 255, 0))
        tiles.append(im)
    w, h = tiles[0].size
    cols = min(a.cols, len(tiles))
    rows = (len(tiles) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * w + (cols - 1) * 2, rows * h + (rows - 1) * 2), (255, 0, 255))
    for i, t in enumerate(tiles):
        sheet.paste(t, ((i % cols) * (w + 2), (i // cols) * (h + 2)))
    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    sheet.save(a.out)
    print(a.out, sheet.size)


if __name__ == "__main__":
    main()
