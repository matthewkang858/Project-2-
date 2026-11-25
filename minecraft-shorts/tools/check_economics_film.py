"""Checker probe for tools/render_economics.py: the recommended change used the way a film director will use it.
This module poses as films/check_economics_probe.py: its build() is a finished film's build() plus the three lines
of the recommendation. It is then run through render.main() itself (not through Session directly), with post.OUT
pointed at out/test/check_economics_out so that no real film directory is touched.

    $BPY -m tools.check_economics_film nitwit 185-188      # render those frames as FINAL frames of the probe film
    $BPY -m tools.check_economics_film nitwit 185-188 again # the same command once more: must render nothing
"""
import importlib
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NAME = "check_economics_probe"
BASE = sys.argv[1] if len(sys.argv) > 1 else "nitwit"


def build(scene):
    """The finished film, plus the recommendation's three lines 'in build(scene), before the return'."""
    out = importlib.import_module("films." + BASE).build(scene)
    scene.render.resolution_x, scene.render.resolution_y = 540, 960
    scene.cycles.samples = 16
    return out


def main(argv):
    import render as R
    from engine import post
    from tools import render_economics as E

    frames = argv[1]
    sys.modules["films." + NAME] = sys.modules[__name__]
    post.OUT = os.path.join(ROOT, "out", "test", "check_economics_out")
    code = R.main([NAME, "--frames", frames, "--threads", "2", "--max-seconds", "200"])
    print("[check] render.main exit code", code)
    d = post.frames_dir(NAME)
    meta = post.read_meta(NAME) or {}
    print("[check] frames dir", os.path.relpath(d, ROOT), "| variant_of(None, None, 1) =", R.variant_of(None, None, 1, True),
          "| variant_of((540, 960), 16, 1) =", R.variant_of((540, 960), 16, 1, True))
    a, b = [int(x) for x in frames.split("-")]
    shot = {"nitwit": "hall", "poppy_night": "night"}.get(BASE)
    from PIL import Image

    for f in range(a, b + 1):
        p = post.frame_path(NAME, f)
        if not os.path.exists(p):
            print("[check] frame", f, "missing")
            continue
        with Image.open(p) as im:
            size = im.size
        st = (meta.get("frames", {}).get(str(f)) or {})
        line = "[check] frame %d: %dx%d stamp s=%s" % (f, size[0], size[1], st.get("s"))
        if shot:
            q = E.seq_frame_path(shot, "r540s16", f)
            if q:
                line += " | == the study's stored E frame %s: %s" % (os.path.basename(q), E.same_pixels(p, q))
        print(line)
    print("[check] meta res/samples:", meta.get("res"), meta.get("samples"), "variant", meta.get("variant"))
    if len(argv) > 2 and argv[2] == "encode":
        mp4 = os.path.join(ROOT, "out", "test", "check_economics_probe_%s.mp4" % BASE)
        post.encode(NAME, captions=[tuple(c) for c in meta["captions"]], fps=meta["fps"], frame_start=a, frame_end=b,
                    out_path=mp4, time_origin=meta["frame_start"])
        print("[check] encoded", mp4)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
