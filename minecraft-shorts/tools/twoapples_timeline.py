"""Two Apples: print the shot plan with its frames and words, and prove the captions (no scene is built).

    $BPY -m tools.twoapples_timeline            # the table
    $BPY -m tools.twoapples_timeline --json     # the same as JSON (for the orchestrator)
    $BPY -m tools.twoapples_timeline --check    # captions: every word once, none across a cut, none too short;
                                                #   the plan ends on nar.frames; exit 1 if not
(run with the Blender python: films/twoapples.py imports the engine; nothing is built or written)
"""
import json
import sys

from engine import narration
from films import twoapples as TA


def rows():
    """(Narration, [ShotInfo]) of the committed voice."""
    nar = narration.load("twoapples", TA.NARRATION, fps=TA.FPS)
    return nar, TA.timeline(nar)


def check(nar, plan):
    """The caption list against the cuts; returns (problems, caption frames). Empty problems = all good."""
    cuts = TA.caption_cuts(nar, plan)
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
        if w.frame_end > row.frame_end + (1 if butts else 0):       # (running speech: a word may end inside the
            problems.append("word %r is still spoken on %d, after the end of %s (%d)" % (    # frame the next word,
                w.text, w.frame_end, row.name, row.frame_end))                             # and shot, starts in)
        if a > w.frame:
            problems.append("caption %r appears on %d, after its word starts (%d)" % (cap, a, w.frame))
    for (c0, a0, b0), (c1, a1, b1) in zip(frames, frames[1:]):
        if a1 <= b0:
            problems.append("captions %r and %r overlap (%d-%d, %d-%d)" % (c0, c1, a0, b0, a1, b1))
    if plan[-1].frame_end != nar.frames:
        problems.append("the plan ends on %d, the narration on %d" % (plan[-1].frame_end, nar.frames))
    for r in plan:
        if not (TA.MIN_SHOT <= r.seconds <= TA.MAX_SHOT) and r.name not in TA.LENGTH_REASONS:
            problems.append("shot %s is %.2f s (outside %.1f-%.1f s) with no reason in LENGTH_REASONS"
                            % (r.name, r.seconds, TA.MIN_SHOT, TA.MAX_SHOT))
    try:
        narration.prove(nar, cuts=cuts)
    except AssertionError as e:
        problems.append("narration.prove: %s" % e)
    return problems, frames


def main(argv):
    """Print the plan (see the module docstring)."""
    nar, plan = rows()
    if "--json" in argv:
        print(json.dumps([dict(shot=r.name, beat=r.beat, sequence=r.sequence, sky=r.sky, dip=r.dip,
                               frame_start=r.frame_start, frame_end=r.frame_end, frames=r.frames,
                               seconds=round(r.seconds, 3), words=r.words, wall=r.wall) for r in plan], indent=1))
        return 0
    print("Two Apples: %d frames = %.2f s, %d shots, %d words" % (nar.frames, nar.duration, len(plan), len(nar.words)))
    for r in plan:
        note = ""
        if r.dip:
            note += "   [dip to black on %d]" % r.frame_start
        if r.wall:
            note += "   [wall: %s]" % r.wall
        print("%-14s beat %2d  %-8s %-5s  %4d-%4d  %3d f  %.2f s%s" % (r.name, r.beat, r.sequence, r.sky,
                                                                     r.frame_start, r.frame_end, r.frames, r.seconds,
                                                                     note))
        print("      " + "  ".join("%s %d" % (w, f) for w, f in r.words))
    problems, frames = check(nar, plan)
    short = min(b - a + 1 for _c, a, b in frames)
    print("captions: %d words, shortest on screen %d frames; film %d frames = nar.frames %d; %s" % (
        len(frames), short, plan[-1].frame_end, nar.frames, "all checks passed" if not problems else "PROBLEMS:"))
    for p in problems:
        print("   " + p)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
