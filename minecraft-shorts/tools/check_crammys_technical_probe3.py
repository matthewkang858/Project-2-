"""Checker's probe 3: the disc in Steve's hand after the jb20 insert; the toot/hold order. Prints only."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


def main():
    import render
    from tools.check_crammys_technical_probe import hidden
    ses = render.Session("crammys", sky="night")
    st, C = ses.result["stage"], ses.result["context"]
    p = st.cast["steve_jb"]
    for h in p._hands["r"]:
        for vn, at in h.variants.items():
            if h.start == 1201:
                print("[probe3] jb20 disc %s start %s end %s; visible at %s" % (
                    at.ob.name, h.start, h.end, [(f, not hidden(at.ob, f)) for f in (1240, 1248, 1249, 1250, 1252,
                                                                                      1258, 1264, 1265)]))
    print("[probe3] insert frame", C.insert_frame(), "song spans", C.bd.jukebox.spans[-6:] if hasattr(
        C.bd.jukebox, "spans") else None)
    a = st.cast["alex_gd"]
    for h in a._hands["r"]:
        for vn, at in h.variants.items():
            print("[probe3] alex_gd %s %s start %s end %s visible 414/415/416/417: %s" % (
                h.item_id, at.ob.name, h.start, h.end, [not hidden(at.ob, f) for f in (414, 415, 416, 417)]))


main()
