"""The Hello, square sequence: join the preview frames of the square's shots into one mp4, and build contact strips
of chosen frames to look at (the director's motion check; no Blender needed).

    python3 tools/hello_square_motion.py mp4 [--dir out/preview/hello/270x480_5spp] [--fps 24]
        -> out/test/hello_square_motion.mp4 (sq01 1-71, sq09 541-604, sq10 605-672, sq11 673-718, in film order,
           every frame that exists in --dir; a missing frame is reported and the previous one is held)
    python3 tools/hello_square_motion.py strip F1 F2 ... [--dir ...] [--name NAME] [--cols 8] [--scale 1.0]
        -> out/test/hello_square_strip_<NAME>.png: the frames side by side, each labelled with its number
Run from the project root. Writes only those two kinds of files.
"""
import argparse
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHOTS = (("sq01_guard", 1, 71), ("sq09_watches", 541, 604), ("sq10_grownups", 605, 672), ("sq11_stare", 673, 718))


def _frame(d, f):
    return os.path.join(d, "f_%04d.png" % f)


def cmd_mp4(args):
    """Join every square frame into one mp4 (24 fps, or args.fps)."""
    d = os.path.join(ROOT, args.dir)
    tmp = tempfile.mkdtemp(prefix="sq_motion_")
    n, last, missing = 0, None, []
    try:
        for _name, a, b in SHOTS:
            for f in range(a, b + 1, args.step):
                src = _frame(d, f)
                if not os.path.exists(src):
                    missing.append(f)
                    src = last
                if src is None:
                    continue
                n += 1
                shutil.copyfile(src, os.path.join(tmp, "i_%05d.png" % n))
                last = src
        out = os.path.join(ROOT, "out", "test", args.out)
        cmd = ["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(args.fps), "-i", os.path.join(tmp, "i_%05d.png"),
               "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", out]
        subprocess.run(cmd, check=True)
        print("[motion] %d frames -> %s  (missing, held: %s)" % (n, out, missing[:20] if missing else "none"))
    finally:
        for name in os.listdir(tmp):
            os.remove(os.path.join(tmp, name))
        os.rmdir(tmp)
    return 0


def cmd_strip(args):
    """Frames side by side with their numbers."""
    from PIL import Image, ImageDraw
    d = os.path.join(ROOT, args.dir)
    ims = []
    for f in args.frames:
        p = _frame(d, f)
        if not os.path.exists(p):
            print("[motion] no frame %d" % f)
            continue
        im = Image.open(p).convert("RGB")
        if args.scale != 1.0:
            im = im.resize((int(im.width * args.scale), int(im.height * args.scale)))
        dr = ImageDraw.Draw(im)
        dr.rectangle((0, 0, 44, 14), fill=(0, 0, 0))
        dr.text((3, 2), str(f), fill=(255, 255, 0))
        ims.append(im)
    if not ims:
        return 1
    cols = min(args.cols, len(ims))
    rows = (len(ims) + cols - 1) // cols
    w, h = ims[0].size
    sheet = Image.new("RGB", (cols * w + (cols - 1) * 2, rows * h + (rows - 1) * 2), (20, 20, 20))
    for i, im in enumerate(ims):
        sheet.paste(im, ((i % cols) * (w + 2), (i // cols) * (h + 2)))
    out = os.path.join(ROOT, "out", "test", "hello_square_strip_%s.png" % args.name)
    sheet.save(out)
    print("[motion] %d frames -> %s" % (len(ims), out))
    return 0


def main(argv):
    """See the module docstring."""
    ap = argparse.ArgumentParser(prog="tools.hello_square_motion")
    ap.add_argument("cmd", choices=("mp4", "strip"))
    ap.add_argument("frames", nargs="*", type=int)
    ap.add_argument("--dir", default=os.path.join("out", "preview", "hello", "270x480_5spp"))
    ap.add_argument("--fps", type=int, default=24)
    ap.add_argument("--step", type=int, default=1)
    ap.add_argument("--out", default="hello_square_motion.mp4")
    ap.add_argument("--name", default="x")
    ap.add_argument("--cols", type=int, default=8)
    ap.add_argument("--scale", type=float, default=1.0)
    args = ap.parse_args(argv)
    return {"mp4": cmd_mp4, "strip": cmd_strip}[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
