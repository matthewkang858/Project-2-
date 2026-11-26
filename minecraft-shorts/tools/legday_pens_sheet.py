"""Leg Day, pens sequence: put stills side by side (the pens director's viewing aid).

    python3 tools/legday_pens_sheet.py OUT.png a.png b.png ... [--h 640]
Each image is scaled to the same height (default 640) and pasted left to right with a 6 px gap. Nothing else.
"""
import sys

from PIL import Image


def main(argv):
    h = 640
    if "--h" in argv:
        i = argv.index("--h")
        h = int(argv[i + 1])
        argv = argv[:i] + argv[i + 2:]
    out, paths = argv[0], argv[1:]
    ims = []
    for p in paths:
        im = Image.open(p).convert("RGB")
        ims.append(im.resize((round(im.width * h / im.height), h)))
    sheet = Image.new("RGB", (sum(i.width for i in ims) + 6 * (len(ims) - 1), h), (20, 20, 20))
    x = 0
    for im in ims:
        sheet.paste(im, (x, 0))
        x += im.width + 6
    sheet.save(out)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
