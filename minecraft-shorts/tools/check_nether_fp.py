"""Reviewer's stamp probe of engine/nether.py: a static film (no characters, static gate camera) whose only changes
are the module's own animation: the pit dug in one shot, the lava flicker in another, the pit dug with a kept block
that is mined on camera. Frames whose picture cannot differ must share a fingerprint; frames that differ must not;
the digests must be the same in two separate processes.

    $BPY -m tools.check_nether_fp            (runs two children, compares)
"""
import json
import os
import subprocess
import sys
import types

FILM = "check_nether_fp"
INFO = {}


def build(scene):
    from engine import breaking, nether, shots

    bas = nether.build_bastion(scene)
    sky = nether.set_nether(scene)
    film = shots.Film(scene, fps=24)
    st = nether.Stage(scene, film, bas, sky)
    c = bas.cameras["gate"]
    spans = {}
    for name, sec in (("A_whole", 0.5), ("B_dug", 0.5), ("C_whole", 0.5), ("D_flicker", 1.0), ("E_dig", 1.0),
                      ("F_whole", 0.5)):
        s = st.shot(name, sec)
        s.lens(c["lens"], c["fstop"])
        s.move(c["pos"], c["target"])
        s.focus(bas.anchors["home_center"])
        st.lights(s, 1.0, **bas.lights_for("home"))
        spans[name] = (s.frame_start, s.frame_end)
        if name == "B_dug":
            bas.pit_open(s)
        if name == "D_flicker":
            bas.lava["home_channels"].flicker(s.frame_start + 4, s.frame_start + 16)
        if name == "E_dig":
            bas.pit_open(s, keep=[bas.pit_last.cell])
            INFO["mine"] = breaking.mine(None, bas.pit_last, s.frame_start + 6, tool="iron_pickaxe", camera=s,
                                         drop=None, crumbs=False)["frame"]
    st.finish()
    INFO["spans"] = spans
    return {"film": film, "captions": [], "stage": st}


def child():
    import render as R
    from engine import stamp

    mod = types.ModuleType("films." + FILM)
    mod.__file__ = os.path.abspath(__file__)
    mod.build = build
    sys.modules["films." + FILM] = mod
    ses = R.Session(FILM)
    ses.configure((540, 960), 16, 2, None)
    fp = stamp.Fingerprinter(ses.scene, ses.film)
    order = list(range(ses.film.frame_start, ses.film.frame_end + 1))
    if "--reverse" in sys.argv:
        order = order[::-1]
    elif "--middle" in sys.argv:
        order = order[60:] + order[:60]
    out = {f: fp.frame(f)["fp"] for f in order}
    print("FP " + json.dumps({"fp": out, "spans": INFO["spans"], "mine": INFO["mine"]}))


def main():
    if "--child" in sys.argv:
        child()
        return 0
    runs = []
    for extra in ([], ["--reverse"], ["--middle"]):
        r = subprocess.run([sys.executable, "-m", "tools.check_nether_fp", "--child"] + extra, capture_output=True,
                           text=True, timeout=280)
        line = [ln for ln in r.stdout.splitlines() if ln.startswith("FP ")]
        if not line:
            print(r.stdout[-3000:], r.stderr[-3000:])
            return 1
        runs.append(json.loads(line[0][3:]))
    a, b, c = runs
    print("same digests in two processes:", a["fp"] == b["fp"], a["fp"] == c["fp"])
    diff = sorted(int(k) for k in a["fp"] if a["fp"][k] != b["fp"][k] or a["fp"][k] != c["fp"][k])
    print("frames whose digest depends on the fingerprinting order:", diff)
    fp = {int(k): v for k, v in a["fp"].items()}
    sp = a["spans"]
    print("spans", sp, "mine break frame", a["mine"])
    # group consecutive equal fingerprints
    groups = []
    for f in sorted(fp):
        if groups and groups[-1][2] == fp[f]:
            groups[-1][1] = f
        else:
            groups.append([f, f, fp[f]])
    for g0, g1, h in groups:
        print("  frames %3d-%3d  %s" % (g0, g1, h[:10]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
