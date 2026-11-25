"""Checker probe for tools/render_economics.py: an independent temporal measure on the study's ENCODED clips
(out/test/econ_seq_<shot>_<variant>.mp4), not the study's own code. For every clip: what ffprobe says, whether its
frames are the consecutive frames they claim to be, and the temporal residual after removing a per-pixel linear
trend over the 8 frames (so a slow camera drift counts as little), per pixel and per 16x16 block mean (blotchy
'boil' is low-frequency: block means catch what per-pixel numbers dilute), over the whole frame outside the
caption band, in dark pixels (luma < 40) and in flat pixels.

    $BPY -m tools.check_economics_temporal SHOT VARIANT [VARIANT ...]      # e.g. night base r540s16 r540s16_animseed
    $BPY -m tools.check_economics_temporal --files LABEL=path.mp4 [...]    # any clips of equal size, first = reference
"""
import json
import os
import subprocess
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEST = os.path.join(ROOT, "out", "test")


def probe(mp4):
    out = subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "v:0", "-count_frames", "-show_entries",
                                   "stream=codec_name,width,height,pix_fmt,r_frame_rate,nb_read_frames,bit_rate", "-of", "json", mp4])
    return json.loads(out)["streams"][0]


def decode(mp4, w, h):
    raw = subprocess.check_output(["ffmpeg", "-v", "error", "-i", mp4, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"])
    return np.frombuffer(raw, dtype=np.uint8).reshape(-1, h, w, 3)


def luma(a):
    a = a.astype(np.float32)
    return a[..., 0] * 0.2126 + a[..., 1] * 0.7152 + a[..., 2] * 0.0722


def detrended_sigma(stack):
    """Per-element standard deviation over time after removing a linear trend (N x ... array)."""
    n = stack.shape[0]
    t = np.arange(n, dtype=np.float32) - (n - 1) / 2.0
    mean = stack.mean(axis=0)
    slope = np.tensordot(t, stack - mean, axes=(0, 0)) / float((t * t).sum())
    resid = stack - mean - t.reshape((-1,) + (1,) * (stack.ndim - 1)) * slope
    return np.sqrt((resid ** 2).sum(axis=0) / (n - 2))


def blocks(lum, k=16):
    n, h, w = lum.shape
    return lum[:, :h // k * k, :w // k * k].reshape(n, h // k, k, w // k, k).mean(axis=(2, 4))


def measure(frames, masks):
    lum = luma(frames)
    px = detrended_sigma(lum)
    bl = detrended_sigma(blocks(lum))
    out = {}
    for name, (m, mb) in masks.items():
        out[name] = (float(px[m].mean()), float(np.percentile(px[m], 99)), float(bl[mb].mean()), float(np.percentile(bl[mb], 99)))
    return out


def main(argv):
    if argv[0] == "--files":
        clips = [a.split("=", 1) for a in argv[1:]]
    else:
        shot = argv[0]
        clips = [(v, os.path.join(TEST, "econ_seq_%s_%s.mp4" % (shot, v))) for v in argv[1:]]
    data = {}
    for label, path in clips:
        info = probe(path)
        fr = decode(path, info["width"], info["height"])
        data[label] = fr
        print("[check] %-22s %s %sx%s %s %s fps, %d frames decoded, %.0f kbit/s" % (
            label, info["codec_name"], info["width"], info["height"], info["pix_fmt"], info["r_frame_rate"], len(fr),
            float(info.get("bit_rate", 0)) / 1000.0))
    ref = data[clips[0][0]]
    n, h, w, _ = ref.shape
    lum = luma(ref)
    band = np.ones((h, w), dtype=bool)
    band[int(0.62 * h) - 8:int(0.72 * h) + 8] = False              # the caption band (engine.captions.CAPTION_BAND)
    gy, gx = np.gradient(lum, axis=(1, 2))
    flat = (np.hypot(gx, gy).max(axis=0) < 2.5) & band
    dark = (lum.max(axis=0) < 40.0) & band
    k = 16
    bb = lambda m: m[:h // k * k, :w // k * k].reshape(h // k, k, w // k, k).mean(axis=(1, 3)) > 0.9
    masks = {"all": (band, bb(band)), "flat": (flat, bb(flat)), "dark": (dark, bb(dark))}
    print("[check] masks: flat %.1f %% of the frame, dark %.1f %%; blocks flat %d, dark %d" % (
        100 * flat.mean(), 100 * dark.mean(), int(masks["flat"][1].sum()), int(masks["dark"][1].sum())))
    print("[check] detrended temporal sigma, levels of 255:   per pixel mean / p99   |   16x16 block means mean / p99")
    for label, _p in clips:
        m = measure(data[label], {k_: v for k_, v in masks.items() if v[1].any()})
        print("[check] %-22s " % label + "   ".join("%s %.2f / %.2f | %.3f / %.3f" % ((k_,) + v) for k_, v in m.items()))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
