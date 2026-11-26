"""The Crammys: print the shot plan with its frames and words, and prove the captions (no scene is built).

    $BPY -m tools.crammys_timeline            # the table
    $BPY -m tools.crammys_timeline --json     # the same as JSON (for the orchestrator)
    $BPY -m tools.crammys_timeline --check    # captions: every word once, none across a cut, none too short; exit 1 if not
(run with the Blender python: films/crammys.py imports the engine)
"""
import json
import sys

from engine import narration
from films import crammys


def rows():
    """(Narration, [ShotInfo]) of the committed voice."""
    nar = narration.load("crammys", crammys.NARRATION, fps=crammys.FPS)
    return nar, crammys.timeline(nar)


def check(nar, plan):
    """The caption list against the cuts; returns a list of problems (empty = all good)."""
    cuts = crammys.caption_cuts(nar, plan)          # the plan's cuts and every sentence's own cut
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
            problems.append("caption %r (%d-%d) leaves its shot %s (%d-%d)" % (cap, a, b, row.name, row.frame_start, row.frame_end))
        butts = w.index + 1 < len(nar.words) and nar.words[w.index + 1].frame == row.frame_end + 1
        if w.frame_end > row.frame_end + (1 if butts else 0):       # (running speech: a word may end inside the
            problems.append("word %r is still spoken on %d, after the end of %s (%d)" % (w.text, w.frame_end, row.name, row.frame_end))   # frame the next word, and the next shot, starts in)
        if a > w.frame:
            problems.append("caption %r appears on %d, after its word starts (%d)" % (cap, a, w.frame))
    for (c0, a0, b0), (c1, a1, b1) in zip(frames, frames[1:]):
        if a1 <= b0:
            problems.append("captions %r and %r overlap (%d-%d, %d-%d)" % (c0, c1, a0, b0, a1, b1))
    if plan[-1].frame_end != nar.frames:
        problems.append("the plan ends on %d, the narration on %d" % (plan[-1].frame_end, nar.frames))
    try:
        narration.prove(nar, cuts=cuts)
    except AssertionError as e:
        problems.append("narration.prove: %s" % e)
    return problems, frames


def main(argv):
    """Print the plan (see the module docstring)."""
    nar, plan = rows()
    if "--json" in argv:
        print(json.dumps([dict(shot=r.name, beat=r.beat, beats=list(r.beats), sequence=r.sequence, sky=r.sky, sky_change=r.change,
                               sky_after=r.sky_after, dip=r.dip, frame_start=r.frame_start, frame_end=r.frame_end,
                               frames=r.frames, seconds=round(r.seconds, 3), words=r.words) for r in plan], indent=1))
        return 0
    print("The Crammys: %d frames = %.2f s, %d shots, %d words" % (nar.frames, nar.duration, len(plan), len(nar.words)))
    for r in plan:
        note = ""
        if r.change is not None:
            note = "   [night %d-%d, %s from %d = %d frames]" % (r.frame_start, r.change - 1, r.sky_after, r.change,
                                                              r.frame_end - r.change + 1)
        if r.dip:
            note += "   [dip to black on %d]" % r.frame_start
        beats = "+".join(str(b) for b in r.beats)
        print("%-19s beat %-6s %-8s %-5s %4d-%4d  %3d f  %.2f s%s" % (
            r.name, beats, r.sequence, r.sky, r.frame_start, r.frame_end, r.frames, r.seconds, note))
        print("      " + "  ".join("%s %d" % (w, f) for w, f in r.words))
    problems, frames = check(nar, plan)
    short = min(b - a + 1 for _c, a, b in frames)
    print("captions: %d words, shortest on screen %d frames; %s" % (len(frames), short,
                                                                   "all checks passed" if not problems else "PROBLEMS:"))
    for p in problems:
        print("   " + p)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
