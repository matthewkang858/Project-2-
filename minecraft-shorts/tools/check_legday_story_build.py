"""Checker probe (story, words, time): build the film for one sky and compare the REAL shot table, captions and
fades with the plan and the lead's report.

    $BPY -m tools.check_legday_story_build [gold|dusk]
"""
import json
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "out", "test", "check_legday_story_build_%s.json")


def main(argv):
    sky = argv[0] if argv else "gold"
    import render
    from films import legday
    t = time.time()
    ses = render.Session("legday", sky=sky)
    print("[check] built %s in %.1f s; BROKEN: %s" % (sky, time.time() - t, list(legday.BROKEN)))
    nar = ses.result["narration"]
    rows = legday.timeline(nar)
    film = ses.film
    st = ses.result["stage"]
    C = ses.result["context"]
    scene = ses.scene
    print("scene frames %d-%d, nar.frames %d, res %dx%d, samples %d" % (
        scene.frame_start, scene.frame_end, nar.frames, scene.render.resolution_x, scene.render.resolution_y,
        scene.cycles.samples))
    bad = 0
    print("%-15s %9s %9s  sky(f0)  %s" % ("shot", "plan", "film", "same"))
    for r, s in zip(rows, film.shots):
        same = (r.name == s.name and r.frame_start == s.frame_start and r.frame_end == s.frame_end)
        if not same:
            bad += 1
        print("%-15s %4d-%4d %4d-%4d  %-6s %s" % (s.name, r.frame_start, r.frame_end, s.frame_start, s.frame_end,
                                                 st.sky_at(s.frame_start), "ok" if same else "DIFF"))
    print("shots plan %d film %d, mismatches %d" % (len(rows), len(film.shots), bad))
    # markers
    marks = sorted((m.frame, m.name) for m in scene.timeline_markers)
    print("markers:", marks[:40])
    # captions as returned by build() and as the session holds them
    caps = ses.captions
    fps = float(nar.fps)
    cuts = [s.frame_start for s in film.shots[1:]]

    def frames_of(t0, t1):
        # frame f shows [(f-1)/fps, f/fps); encoder shows caption on frame f if t0 <= (f-1)/fps < t1
        import math
        a = int(math.floor(t0 * fps + 1e-9)) + 1
        if (a - 1) / fps < t0 - 1e-9:
            a += 1
        b = int(math.ceil(t1 * fps - 1e-9))
        return a, b
    problems = []
    words = [w for w in nar.words if w.caption]
    if len(caps) != len(words):
        problems.append("captions %d words %d" % (len(caps), len(words)))
    for (c, t0, t1), w in zip(caps, words):
        a, b = frames_of(t0, t1)
        for cut in cuts:
            if a < cut <= b:
                problems.append("caption %r %d-%d straddles cut %d" % (c, a, b, cut))
        if c != w.caption:
            problems.append("caption %r != word %r" % (c, w.caption))
        if a > w.frame:
            problems.append("caption %r late: %d > %d" % (c, a, w.frame))
        if w.frame - a > 1:
            problems.append("caption %r early by %d frames" % (c, w.frame - a))
    print("caption problems:", problems or "none")
    # fades (dips to black)
    fades = ses.fades
    print("fades:", fades)
    try:
        from engine import post
        for f in list(range(1362, 1376)) + list(range(1558, 1568)):
            g = round(post.fade_gain(fades, (f - 1) / fps), 3)
            print("  frame %d gain %s  caption %r" % (f, g, [c for c, t0, t1 in caps if t0 <= (f - 1) / fps < t1]))
    except Exception as e:
        print("fade gain probe failed:", e)
    # what is shown on the last frames
    last = [c for c, t0, t1 in caps if t1 > (nar.frames - 30) / fps]
    print("captions in the last 30 frames:", [(c, round(t0 * fps + 1, 1), round(t1 * fps, 1)) for c, t0, t1 in caps
                                              if t1 > (nar.frames - 60) / fps])
    # camera on frame 1 of every shot: is it moving?
    cam = scene.camera
    print("camera movement at each shot's first frames (blocks/frame, deg/frame):")
    import math
    for s in film.shots:
        if st.sky_at(s.frame_start) != sky:
            continue
        ps = []
        for f in (s.frame_start, s.frame_start + 1, s.frame_end - 1, s.frame_end):
            scene.frame_set(f)
            c = scene.camera
            ps.append((c.matrix_world.translation.copy(), c.matrix_world.to_quaternion().copy()))
        d0 = (ps[1][0] - ps[0][0]).length
        a0 = math.degrees(ps[0][1].rotation_difference(ps[1][1]).angle)
        d1 = (ps[3][0] - ps[2][0]).length
        a1 = math.degrees(ps[2][1].rotation_difference(ps[3][1]).angle)
        print("  %-15s first %.4f / %.3f   last %.4f / %.3f  cam %s" % (s.name, d0, a0, d1, a1, scene.camera.name))
    json.dump({"sky": sky, "shots": [(s.name, s.frame_start, s.frame_end) for s in film.shots],
               "captions": caps, "fades": repr(fades), "problems": problems}, open(OUT % sky, "w"), indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
