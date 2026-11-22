"""How much would the denoised picture 'boil'? Render one frame of a film twice with different noise seeds at the
final settings and measure the difference (role FIXER; evidence for the temporal-stability question).

    $BPY -m tools.noise_check lookdev_dusk 73 49 [--samples 24]

The scene, camera and frame are identical in both renders, so whatever differs is noise that survived the denoiser:
exactly what crawls from frame to frame in the film. Prints mean / 99th percentile / max difference in 8-bit levels
and writes out/test/tmp_fix/noise_<film>_<frame>.png (render A | render B | difference x 12).
"""
import os
import sys

import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


def main(argv):
    """Entry point."""
    import render as R

    film = argv[0]
    samples = int(argv[argv.index("--samples") + 1]) if "--samples" in argv else R.FINAL_SAMPLES
    frames = [int(a) for a in argv[1:] if a.isdigit()]
    out_dir = os.path.join(ROOT, "out", "test", "tmp_fix")
    ses = R.Session(film)
    ses.configure(R.FINAL_RES, samples, R.FINAL_THREADS, None)
    worst = 0.0
    for f in frames:
        imgs = []
        for seed in (0, 1):
            ses.scene.cycles.seed = seed
            path = os.path.join(out_dir, "noise_%s_%d_seed%d.png" % (film, f, seed))
            ses.render_frame(f, path)
            imgs.append(np.asarray(Image.open(path).convert("RGB")).astype(np.float32))
        d = np.abs(imgs[0] - imgs[1]).max(axis=2)
        mean, p99, mx = float(d.mean()), float(np.percentile(d, 99)), float(d.max())
        frac = float((d > 6).mean())
        worst = max(worst, p99)
        sheet = np.concatenate([imgs[0], imgs[1], np.clip(np.repeat(d[..., None], 3, axis=2) * 12.0, 0, 255)], axis=1)
        path = os.path.join(out_dir, "noise_%s_%d.png" % (film, f))
        Image.fromarray(sheet.astype(np.uint8)).save(path)
        print("[noise] %s frame %d at %d samples: mean %.2f, 99th percentile %.1f, max %.0f levels; %.2f %% of pixels "
              "differ by more than 6 levels -> %s" % (film, f, samples, mean, p99, mx, 100 * frac, path), flush=True)
    ses.scene.cycles.seed = 0
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
