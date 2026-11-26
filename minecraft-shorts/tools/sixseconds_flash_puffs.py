"""Six Seconds, sequence FLASH: render candidate puffs of one flash cut side by side (scouting; writes no meta.json).

    $BPY -m tools.sixseconds_flash_puffs --sky soul fl16_bridge 999,1010 123:10,72:8,17:8 [--res 270x480 --samples 8]

One build of the sky; for each candidate SEED:OFFSET the shot's own puff (the one films/sixseconds_flash.py made,
from PUFF) is deleted and engine.piglins.poof is called again exactly as C.puff does (the shot's six_flash_puff_<world>
anchor, frame = first frame - OFFSET, camera = the shot, size = a player's box, that seed); the frame is rendered to
out/test/sixseconds_flash_puff_<shot>_<seed>_<offset>_<frame>.png and all of them are put side by side (one row per
frame), with the Reels zones, in out/test/sixseconds_flash_puffs_<shot>_<frames>.png. Candidates come from
tools/sixseconds_flash_probe.py puffs.
"""
import argparse
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


def main(argv):
    ap = argparse.ArgumentParser(prog="tools.sixseconds_flash_puffs")
    ap.add_argument("--sky", default="wastes")
    ap.add_argument("--res", default="270x480")
    ap.add_argument("--samples", type=int, default=8)
    ap.add_argument("--threads", type=int, default=2)
    ap.add_argument("shot")
    ap.add_argument("frames", help="FRAME[,FRAME...]: one row of the sheet per frame")
    ap.add_argument("candidates", help="SEED:OFFSET,SEED:OFFSET,...")
    a = ap.parse_args(argv)
    import bpy
    from mathutils import Vector
    from PIL import Image

    import render
    from engine import piglins, post
    from films import sixseconds_flash as FL
    ses = render.Session("sixseconds", sky=a.sky)
    res = tuple(int(v) for v in a.res.split("x"))
    ses.configure(res, a.samples, a.threads, True)
    C = ses.result["context"]
    s = C.shots[a.shot]
    world = FL.WORLDS[a.shot][0]
    spot = Vector(C.P("six_flash_puff_%s" % world))
    seed0, off0 = FL.PUFF[a.shot]
    made = ["fx_poof_%d_" % (s.frame_start - off0)]
    out = os.path.join(ROOT, "out", "test")
    frames = [int(v) for v in a.frames.split(",")]
    rows = {f: [] for f in frames}
    for cand in a.candidates.split(","):
        seed, off = (int(v) for v in cand.split(":"))
        for prefix in made:
            for ob in [o for o in bpy.data.objects if o.name.startswith(prefix)]:
                bpy.data.objects.remove(ob, do_unlink=True)
        piglins.poof(spot, s.frame_start - off, camera=s, size=(0.6, 1.8), seed=seed)
        made = ["fx_poof_%d_" % (s.frame_start - off)]
        for f in frames:
            path = os.path.join(out, "sixseconds_flash_puff_%s_%d_%d_%d.png" % (a.shot, seed, off, f))
            t = time.time()
            ses.render_frame(f, path)
            print("[flash_puffs] %s seed %d off %d frame %d -> %s  %.1f s" % (a.shot, seed, off, f, path,
                                                                            time.time() - t), flush=True)
            with Image.open(path) as im:
                rows[f].append(post.draw_zones(im.convert("RGB")).convert("RGB"))
    w, h = rows[frames[0]][0].size
    sheet = Image.new("RGB", (w * len(rows[frames[0]]), h * len(frames)))
    for j, f in enumerate(frames):
        for i, t in enumerate(rows[f]):
            sheet.paste(t, (i * w, j * h))
    dest = os.path.join(out, "sixseconds_flash_puffs_%s_%s.png" % (a.shot, "_".join(str(f) for f in frames)))
    sheet.save(dest)
    print("[flash_puffs] sheet -> %s (%s)" % (dest, a.candidates))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
