"""Checker: palette / safe-area check (tools/palette_check) of The Hello stub frames at final quality, plus a
captioned version.   $BPY -m tools.check_hello_technical_palette <sky> F[,F...]
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main(argv):
    import render
    from PIL import Image

    from engine import captions, post
    from tools import palette_check
    sky, frames = argv[0], [int(v) for v in argv[1].split(",")]
    ses = render.Session("hello", sky=sky)
    st = ses.result["stage"]
    ses.configure((540, 960), 16, 2, True)
    for f in frames:
        shot = next(s for s in ses.film.shots if s.frame_start <= f <= s.frame_end)
        path = os.path.join(ROOT, "out", "test", "check_hello_technical_pal_%s_%d.png" % (shot.name, f))
        ses.render_frame(f, path)
        rec = palette_check.probe(ses.scene)
        rep = palette_check.evaluate(rec, path, heroes=st.heroes.get(shot.name, ()))
        palette_check.print_report("%s@%d" % (shot.name, f), rep)
        word = captions.caption_at(ses.captions, ses.film.seconds(f))
        with Image.open(path) as im:
            post.finish_frame(im, word).save(path[:-4] + "_captioned.png")
        print("[pal] caption %r -> %s_captioned.png" % (word, path[:-4]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
