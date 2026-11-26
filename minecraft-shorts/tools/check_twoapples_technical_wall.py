"""Checker's probe: can tu09's wall open on "opens" with the flip on "lever" through C.wall_open (repeater > 4)?

    $BPY -m tools.check_twoapples_technical_wall [REPEATER]
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


def main(argv):
    import bpy  # noqa: F401  (mathutils)
    rep = int(argv[0]) if argv else 13
    from films import twoapples_common as TC
    orig = TC.TwoApples.wall_open

    def patched(self, frame, who="", **kw):
        if who == "tu09_lever":
            kw["repeater"] = rep
        return orig(self, frame, who=who, **kw)
    TC.TwoApples.wall_open = patched
    import render
    ses = render.Session("twoapples", sky="under")
    C = ses.result["context"]
    print("[wall] repeater", rep, "memo", C.memo.get("tu_lever"), "log", C.wall_log)
    for f in (566, 590, 596, 598, 600, 602, 604, 623, 948, 955):
        print("  f%d open=%s" % (f, C.ug.door.is_open(f)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
