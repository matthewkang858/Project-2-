"""Six Seconds: print the shot plan with its frames and words, and prove the captions (no scene is built).

    $BPY -m tools.sixseconds_timeline            # the table
    $BPY -m tools.sixseconds_timeline --json     # the same as JSON (for the orchestrator)
    $BPY -m tools.sixseconds_timeline --check    # captions: every word once, none across a cut, none too short; the
                                                 # black of the reset / snaps / end; the stare; exit 1 if not
(run with the Blender python: films/sixseconds.py imports the engine)
"""
import json
import sys

from engine import narration, post
from films import sixseconds as F
from films import sixseconds_common as SC


def rows():
    """(Narration, [ShotInfo]) of the committed voice."""
    nar = narration.load("sixseconds", F.NARRATION, fps=F.FPS)
    return nar, F.timeline(nar)


def fades(plan, fps=24):
    """The encoder's picture-gain ramps the film will return (Stage.dip for every black span), in film seconds."""
    out = []
    for r in plan:
        if r.black is not None:
            a, b = r.black
            hold = b - a + 1
            out.append(((a - 1) / float(fps), (a - 1 + hold) / float(fps), 0.0, 0.0))
    return out


def check(nar, plan):
    """The caption list against the cuts; returns a list of problems (empty = all good) and the caption frames."""
    cuts = [r.frame_start for r in plan[1:]]
    frames = nar.caption_frames(cuts=cuts)
    problems = []
    shown = [w for w in nar.words if w.caption]
    if len(frames) != len(shown):
        problems.append("captions %d, words %d" % (len(frames), len(shown)))
    for (cap, a, b), w in zip(frames, shown):
        if cap != w.caption:
            problems.append("caption %r is not word %r" % (cap, w.caption))
        if b - a + 1 < 2:
            problems.append("caption %r is on for %d frame(s) (%d-%d)" % (cap, b - a + 1, a, b))
        row = next(r for r in plan if r.frame_start <= w.frame <= r.frame_end)
        if a < row.frame_start or b > row.frame_end:
            problems.append("caption %r (%d-%d) leaves its shot %s (%d-%d)" % (cap, a, b, row.name, row.frame_start,
                                                                           row.frame_end))
        butts = w.index + 1 < len(nar.words) and nar.words[w.index + 1].frame == row.frame_end + 1
        if w.frame_end > row.frame_end + (1 if butts else 0):       # running speech: a word may end inside the
            problems.append("word %r is still spoken on %d, after the end of %s (%d)"      # frame the next word,
                            % (w.text, w.frame_end, row.name, row.frame_end))            # and the next shot, start in
        if a > w.frame:
            problems.append("caption %r appears on %d, after its word starts (%d)" % (cap, a, w.frame))
    for (c0, a0, b0), (c1, a1, b1) in zip(frames, frames[1:]):
        if a1 <= b0:
            problems.append("captions %r and %r overlap (%d-%d, %d-%d)" % (c0, c1, a0, b0, a1, b1))
    if plan[-1].frame_end != nar.frames:
        problems.append("the plan ends on %d, the narration on %d" % (plan[-1].frame_end, nar.frames))
    try:
        narration.prove(nar)
    except AssertionError as e:
        problems.append("narration.prove: %s" % e)
    # the black: exactly where the plan says, and the caption of the reset held on it
    fd = fades(plan, nar.fps)
    for r in plan:
        for f in range(r.frame_start, r.frame_end + 1):
            g = post.fade_gain(fd, (f - 1) / float(nar.fps))
            black = r.black is not None and r.black[0] <= f <= r.black[1]
            if (g == 0.0) != black or (not black and g != 1.0):
                problems.append("frame %d of %s has picture gain %.2f" % (f, r.name, g))
    reset = next(r for r in plan if r.name == "pt10_smoke")
    word = F.RESETS["pt10_smoke"]
    cap = next((c for c in frames if c[0] == word and reset.frame_start <= c[1] <= reset.frame_end), None)
    if cap is None or cap[1] != reset.black[0] or cap[2] != reset.frame_end:
        problems.append("the reset's caption %r is not held on the whole black %s: %s" % (word, reset.black, cap))
    # the six-second stare
    by = {r.name: r for r in plan}
    stare = by["rw23_nothing"].frame_start - by["rw21_stare"].frame_start
    if stare != SC.STARE_FRAMES:
        problems.append("the stare is %d frames, not %d" % (stare, SC.STARE_FRAMES))
    # shot lengths: 1.2 to 5 s unless the plan gives a reason (the flash cuts)
    for r in plan:
        if not 1.2 <= r.seconds <= 5.0 and r.sequence != "flash":
            problems.append("shot %s is %.2f s (1.2 - 5 s without a reason)" % (r.name, r.seconds))
    return problems, frames


def main(argv):
    """Print the plan (see the module docstring)."""
    nar, plan = rows()
    if "--json" in argv:
        print(json.dumps([dict(shot=r.name, beat=r.beat, sequence=r.sequence, sky=r.sky, black=r.black,
                               frame_start=r.frame_start, frame_end=r.frame_end, frames=r.frames,
                               seconds=round(r.seconds, 3), words=r.words) for r in plan], indent=1))
        return 0
    print("Six Seconds: %d frames = %.2f s, %d shots, %d words, skies %s"
          % (nar.frames, nar.duration, len(plan), len(nar.words), ", ".join(F.SKIES)))
    for r in plan:
        note = ""
        if r.black is not None:
            note = "   [black %d-%d]" % r.black
        print("%-14s beat %2d  %-6s %-6s  %4d-%4d  %3d f  %.2f s%s" % (r.name, r.beat, r.sequence, r.sky,
                                                                      r.frame_start, r.frame_end, r.frames,
                                                                      r.seconds, note))
        print("      " + "  ".join("%s %d" % (w, f) for w, f in r.words))
    problems, frames = check(nar, plan)
    short = min(b - a + 1 for _c, a, b in frames)
    by = {r.name: r for r in plan}
    print("stare: rw21 %d + rw22 %d = %d frames" % (by["rw21_stare"].frames, by["rw22_six"].frames,
                                                   by["rw21_stare"].frames + by["rw22_six"].frames))
    print("captions: %d words, shortest on screen %d frames; %s" % (len(frames), short,
                                                                   "all checks passed" if not problems else "PROBLEMS:"))
    for p in problems:
        print("   " + p)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
