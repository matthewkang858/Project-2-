"""Checker probe: the chip state of the day anvils on the road (rd20) against the dusk set and the held anvils.

    $BPY -m tools.check_legday_story_chips
"""
import sys


def main(argv):
    import render
    ses = render.Session("legday", sky="gold")
    C = ses.result["context"]
    st = ses.result["stage"]
    day = [(a.name, a.state_at(1100), a.state_at(1300)) for a in C.anvils]
    dusk = [(a.name, a.state_at(1400), a.state_at(1560)) for a in C.anvils_dusk]
    print("day anvils (before rd19, on the road in rd20):")
    for d in day:
        print("  ", d)
    print("chipped on the road: %d of 12" % sum(1 for _n, a, b in day if a != b))
    print("dusk anvils (cl22, tp24):", sorted(set((b, c) for _n, b, c in dusk)))
    for name in ("steve_cl3", "kai_cl3", "zuri_cl3", "ari_cl3", "steve_cl4", "kai_cl4", "steve_tp2"):
        c = st.cast.get(name)
        held = getattr(c, "held", None) or getattr(c, "_held", None)
        print("  held by %s: %r" % (name, held if held is not None else [k for k in vars(c) if "hold" in k or "item" in k]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
