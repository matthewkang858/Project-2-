"""Review probe (motion lens, round 2): a labelled strip of frames from a directory with any name pattern.

    python3 tools/check_hello_review_motion_r2strip.py OUT.png --frames 1,2,3 | --range A B [--step N]
            [--src DIR] [--pat m_%04d.png] [--crop x0,y0,x1,y1] [--scale S] [--cols C]

Crop in source pixels. Each tile is labelled with its frame number. Default source: the mp4 frames decoded at
360x640 into out/test/check_hello_review_motion_r2/mp4.
"""
import argparse
import os

from PIL import Image, ImageDraw


def main():
    p = argparse.ArgumentParser()
    p.add_argument("out")
    p.add_argument("--range", nargs=2, type=int, default=None)
    p.add_argument("--step", type=int, default=1)
    p.add_argument("--frames", default=None)
    p.add_argument("--src", default="out/test/check_hello_review_motion_r2/mp4")
    p.add_argument("--pat", default="m_%04d.png")
    p.add_argument("--crop", default=None)
    p.add_argument("--scale", type=float, default=1.0)
    p.add_argument("--cols", type=int, default=8)
    a = p.parse_args()
    if a.frames:
        frames = [int(x) for x in a.frames.split(",")]
    else:
        frames = list(range(a.range[0], a.range[1] + 1, a.step))
    tiles = []
    for f in frames:
        im = Image.open(os.path.join(a.src, a.pat % f)).convert("RGB")
        if a.crop:
            x0, y0, x1, y1 = [int(v) for v in a.crop.split(",")]
            im = im.crop((x0, y0, x1, y1))
        if a.scale != 1.0:
            im = im.resize((int(im.width * a.scale), int(im.height * a.scale)), Image.NEAREST)
        d = ImageDraw.Draw(im)
        d.rectangle((0, 0, 30, 11), fill=(0, 0, 0))
        d.text((2, 0), str(f), fill=(255, 255, 0))
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
