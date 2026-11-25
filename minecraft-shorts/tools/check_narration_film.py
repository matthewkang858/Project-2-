"""Checker's probe (Blender): the narrated demo built through render.Session and rendered at 540x960 with motion
blur on both sides of each cut, with the caption the encoder would draw. Output: out/test/check_narration_film_*.png

    $BPY -m tools.check_narration_film            # repeat until it says 'all frames there'
"""
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
T0 = time.time()
import render                                                        # noqa: E402
from engine import captions as cap                                   # noqa: E402
from PIL import Image                                                # noqa: E402

NAME = "_narrated_demo"
OUT = os.path.join(ROOT, "out", "test")


def main():
    ses = render.Session(NAME)
    nar = ses.result["narration"]
    film = ses.film
    shots = [(s.name, s.frame_start, s.frame_end) for s in film.shots]
    print("shots:", shots)
    print("cuts :", [s.cut for s in nar.sentences], "film frames", film.frame_start, film.frame_end, "narration frames", nar.frames)
    assert [s[1] for s in shots] == [1] + [s.cut for s in nar.sentences[1:]], "shots do not start on the sentence cuts"
    assert film.frame_end == nar.frames
    markers = sorted((m.frame, m.name, m.camera.name if m.camera else None) for m in ses.scene.timeline_markers)
    print("markers:", markers)
    cuts = [s.cut for s in nar.sentences[1:]]
    frames = []
    for c in cuts:
        frames += [c - 1, c, c + 2]
    frames += [nar.at("nobody") + 5]
    ses.configure((540, 960), 12, 2, True)
    r = ses.scene.render
    print("motion blur:", r.use_motion_blur, "shutter", r.motion_blur_shutter, "| built in %.0f s" % (time.time() - T0))
    left = 0
    for f in frames:
        path = os.path.join(OUT, "check_narration_film_%03d.png" % f)
        if os.path.exists(path):
            continue
        if time.time() - T0 > 200:
            left += 1
            continue
        t = time.time()
        raw = os.path.join(OUT, "check_narration_film_raw.png")
        ses.render_frame(f, raw)
        word = cap.caption_at(ses.captions, (f - film.frame_start) / float(film.fps))
        img = Image.open(raw).convert("RGB")
        (cap.composite(img, word) if word else img).save(path)
        print("frame %d (%s) caption %r in %.0f s" % (f, film.shot_at(f).name, word, time.time() - t), flush=True)
    if left:
        print("%d frames left: run again" % left)
        return
    tiles = [Image.open(os.path.join(OUT, "check_narration_film_%03d.png" % f)).resize((270, 480), Image.LANCZOS) for f in frames]
    sheet = Image.new("RGB", (len(tiles) * 274 + 4, 480 + 30), (20, 20, 24))
    for i, (t, f) in enumerate(zip(tiles, frames)):
        sheet.paste(t, (4 + i * 274, 26))
        lab = cap.label("f%d %s" % (f, film.shot_at(f).name), scale=2)
        sheet.paste(lab, (6 + i * 274, 3), lab)
    sheet.save(os.path.join(OUT, "check_narration_film_sheet.png"))
    print("all frames there ->", "out/test/check_narration_film_sheet.png", frames)


if __name__ == "__main__":
    main()
