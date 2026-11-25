"""Checker probe for tools/render_economics.py: a shot type the study did not render, the DARK INTERIOR with four
small faces (The Bell, shot 'interior', frames 117-124), at the recommended setting E (540x960 at 16 samples),
rendered the way render.py renders a film (Session.configure once, then Session.render_frame), plus one frame with
another noise seed. The reference frames are the finished film's own (out/frames/bell/f_####.png).

    $BPY -m tools.check_economics_interior E        # 8 consecutive frames at E + frame 120 with seed 1 (resumable)
    $BPY -m tools.check_economics_interior REF      # frame 120 at the current final with seed 1 (the noise floor)
    $BPY -m tools.check_economics_interior analyse  # numbers, encoded clips and sheets (no rendering)
"""
import json
import os
import shutil
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEST = os.path.join(ROOT, "out", "test")
FILM, FRAMES, MID = "bell", list(range(117, 125)), 120


def path(mode, frame, seed=0):
    return os.path.join(TEST, "check_economics_int_%s_%04d%s.png" % (mode, frame, "_s%d" % seed if seed else ""))


def ref(frame):
    return os.path.join(ROOT, "out", "frames", FILM, "f_%04d.png" % frame)


def render(mode):
    import render as R

    t0 = time.time()
    ses = R.Session(FILM)
    if mode == "E":
        ses.configure((540, 960), 16, 2, None)
        jobs = [(f, 0) for f in FRAMES] + [(MID, 1)]
    else:
        ses.configure(None, None, 2, None)
        jobs = [(MID, 1)]
    r, c = ses.scene.render, ses.scene.cycles
    print("[check] %s: %dx%d, %d samples, min %d" % (mode, r.resolution_x, r.resolution_y, c.samples, c.adaptive_min_samples), flush=True)
    for f, seed in jobs:
        p = path(mode, f, seed)
        if os.path.exists(p):
            continue
        if time.time() - t0 > 215:
            print("[check] budget used, run again", flush=True)
            break
        c.seed = seed
        t, cpu = time.time(), time.process_time()
        ses.render_frame(f, p)
        print("[check] %s frame %d seed %d: %.1f s wall, %.1f cpu-s, load %.1f" % (
            mode, f, seed, time.time() - t, time.process_time() - cpu, os.getloadavg()[0]), flush=True)
    c.seed = 0
    return 0


def encode(name, paths, mp4, word="Hello"):
    """engine.post.encode on a list of PNGs (the method of the study's _encode_frames, in a directory of my own)."""
    from engine import post

    film = "check_economics_" + name
    old = post.OUT
    post.OUT = os.path.join(TEST, "check_economics_out")
    try:
        d = post.frames_dir(film)
        os.makedirs(d, exist_ok=True)
        for i, p in enumerate(paths):
            shutil.copyfile(p, post.frame_path(film, i + 1))
        n = len(paths)
        post.write_meta(film, {"fps": 24, "frame_start": 1, "frame_end": n, "captions": [[word, 0.0, n / 24.0]],
                               "signature": "x", "frames": {str(i + 1): "x" for i in range(n)}})
        post.encode(film, out_path=mp4)
    finally:
        post.OUT = old
    return mp4


def analyse():
    import numpy as np
    from PIL import Image

    from tools import render_economics as E
    from tools import check_economics_temporal as T

    out = {}
    # ---- stills: frame 120 against the film's frame; floor = the current final with another seed
    R0 = E.deliver(ref(MID))
    rows = {"E": path("E", MID), "E seed1": path("E", MID, 1), "REF seed1 (floor)": path("REF", MID, 1)}
    for k, p in rows.items():
        if os.path.exists(p):
            c = E.compare(R0, E.deliver(p))
            out[k] = c
            print("[check] still %-18s ssim %.4f  phone ssim %.4f  phone p99 %.1f  sharp x%.3f" % (
                k, c["ssim"], c["phone_ssim"], c["phone_p99"], c["sharp"]))
    # ---- two seeds of one frame (what boils when nothing moves), as delivered, flat and dark areas
    for k, a, b in (("REF", ref(MID), path("REF", MID, 1)), ("E", path("E", MID), path("E", MID, 1))):
        if os.path.exists(a) and os.path.exists(b):
            ua, ub = np.asarray(E.deliver(a)).astype(np.float32), np.asarray(E.deliver(b)).astype(np.float32)
            d = np.abs(ua - ub).max(axis=2)
            lum = E.luma(ua)
            gy, gx = np.gradient(lum)
            flat = np.hypot(gx, gy) < 2.5
            dark = lum < 40
            print("[check] two seeds %-4s upscaled: mean %.2f p99 %.1f | flat %.2f p99 %.1f | dark (%.0f %%) %.2f p99 %.1f | >6 levels %.2f %%" % (
                k, d.mean(), np.percentile(d, 99), d[flat].mean(), np.percentile(d[flat], 99), 100 * dark.mean(),
                d[dark].mean(), np.percentile(d[dark], 99), 100 * (d > 6).mean()))
            mp4 = os.path.join(TEST, "check_economics_int_%s_boil.mp4" % k)
            encode("int_%s_boil" % k, [a, b] * 4, mp4)
            fr = T.decode(mp4, 1080, 1920).astype(np.float32)
            pr = np.abs(fr[1:] - fr[:-1]).max(axis=3)
            print("[check] two seeds %-4s ENCODED:  mean %.2f p99 %.1f | flat %.2f p99 %.1f | dark %.2f p99 %.1f" % (
                k, pr.mean(), np.percentile(pr, 99), pr[:, flat].mean(), np.percentile(pr[:, flat], 99),
                pr[:, dark].mean(), np.percentile(pr[:, dark], 99)))
    # ---- 8 consecutive frames, encoded as a film is
    have = [path("E", f) for f in FRAMES]
    if all(os.path.exists(p) for p in have):
        a = encode("int_REF", [ref(f) for f in FRAMES], os.path.join(TEST, "check_economics_int_REF.mp4"))
        b = encode("int_E", have, os.path.join(TEST, "check_economics_int_E.mp4"))
        T.main(["--files", "REF=" + a, "E=" + b])
        # sheet: the four faces at 1:1 of the delivered frame, three consecutive encoded frames, REF above E
        fa, fb = T.decode(a, 1080, 1920), T.decode(b, 1080, 1920)
        box = (0, 230, 560, 720)
        sheet = Image.new("RGB", (3 * 560 + 16, 2 * 490 + 8), (60, 0, 60))
        for row, fr in enumerate((fa, fb)):
            for i in range(3):
                sheet.paste(Image.fromarray(fr[2 + i]).crop(box), (i * 568, row * 498))
        sheet.save(os.path.join(TEST, "check_economics_int_faces.png"))
        # blind pair of frame 120 at phone size, order from os.urandom, key in a file
        ra, rb = Image.fromarray(fa[3]).resize((540, 960), Image.LANCZOS), Image.fromarray(fb[3]).resize((540, 960), Image.LANCZOS)
        where = "L" if os.urandom(1)[0] & 1 else "R"
        pair = Image.new("RGB", (1088, 960), (60, 0, 60))
        pair.paste(ra if where == "L" else rb, (0, 0))
        pair.paste(rb if where == "L" else ra, (548, 0))
        pair.save(os.path.join(TEST, "check_economics_int_blind.png"))
        with open(os.path.join(TEST, "check_economics_int_blind_key.json"), "w") as f:
            json.dump({"reference": where}, f)
    return 0


if __name__ == "__main__":
    arg = sys.argv[1] if len(sys.argv) > 1 else "analyse"
    sys.exit(analyse() if arg == "analyse" else render(arg))
