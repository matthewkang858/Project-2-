"""Tiny helper: paste stills side by side into one image for a quick look. python3 -m tools.sheet out.png a.png b.png ..."""
import sys

from PIL import Image


def sheet(out, paths, height=640):
    """Save the images at `paths` side by side, each scaled to `height`, as `out`."""
    ims = []
    for p in paths:
        im = Image.open(p).convert("RGB")
        ims.append(im.resize((int(im.width * height / im.height), height), Image.LANCZOS))
    s = Image.new("RGB", (sum(i.width for i in ims) + 4 * (len(ims) - 1), height), (20, 20, 24))
    x = 0
    for im in ims:
        s.paste(im, (x, 0))
        x += im.width + 4
    s.save(out)
    return out


if __name__ == "__main__":
    print(sheet(sys.argv[1], sys.argv[2:]))
