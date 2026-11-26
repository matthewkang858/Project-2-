"""Frame fingerprints (engine/stamp.py) of the Nether proof film (engine/nether.py): the same digests in two separate
processes; and each of the module's per-shot switches changes exactly that shot's fingerprints:
Bastion.pit_open (the pit dug, its fill light on), Bastion.pillar_in (the netherrack pillar built),
Bastion.lava_flicker (the corridor's lava light), each applied to one shot on top of the previous.

    $BPY -m tools.check_nether_stamp            # runs two child processes and compares; exit code 1 on a failure
"""
import json
import os
import subprocess
import sys

# proof film shots (24 frames each): landing 1-24, ingot_row 25-48, gate 49-72, gate_18 73-96, pit 97-120,
# bridge 121-144, bridge_wide 145-168, treasure 169-192
FRAMES = (13, 37, 61, 62, 72, 73, 85, 109, 110, 133, 144, 145, 157, 181)


def digests():
    """Build the proof film and fingerprint FRAMES; then apply the switches one after the other, fingerprinting each."""
    import bpy  # noqa: F401

    import render as R
    from engine import nether, stamp

    nether.register_proof_film()
    ses = R.Session(nether.PROOF_FILM)
    ses.configure((540, 960), 16, 2, None)
    bas = ses.result["bastion"]
    shot = {s.name: s for s in ses.film.shots}

    def fps():
        fp = stamp.Fingerprinter(ses.scene, ses.film)
        return {f: fp.frame(f)["fp"] for f in FRAMES}

    steps = [("before", None, fps())]
    for label, name, apply in (("pit_open", "gate", lambda s: bas.pit_open(s)),
                               ("pillar_in", "bridge", lambda s: bas.pillar_in(s)),
                               ("lava_flicker", "gate", lambda s: bas.lava_flicker(s.frame_start, s.frame_end))):
        s = shot[name]
        apply(s)
        steps.append((label, [s.frame_start, s.frame_end], fps()))
    order = list(FRAMES)
    reverse = stamp.Fingerprinter(ses.scene, ses.film)
    backwards = {f: reverse.frame(f)["fp"] for f in reversed(order)}
    return {"steps": steps, "backwards": backwards}


def main():
    if "--child" in sys.argv:
        print("DIGESTS " + json.dumps(digests()))
        return 0
    env = dict(os.environ)
    runs = []
    procs = [subprocess.Popen([sys.executable, "-m", "tools.check_nether_stamp", "--child"], stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE, text=True, env=env) for _k in range(2)]     # two at once
    for pr in procs:
        so, se = pr.communicate(timeout=280)
        line = [ln for ln in so.splitlines() if ln.startswith("DIGESTS ")]
        if not line:
            print(so[-2000:], se[-2000:])
            return 1
        runs.append(json.loads(line[0][8:]))
    a, b = runs
    fails = 0

    def ok(cond, text):
        nonlocal fails
        print("[stamp] %-4s %s" % ("ok" if cond else "FAIL", text))
        fails += not cond

    for (la, _sa, da), (_lb, _sb, db) in zip(a["steps"], b["steps"]):
        ok(da == db, "%-12s the same fingerprints in two processes (%d frames)" % (la, len(FRAMES)))
    last = a["steps"][-1][2]
    ok(a["backwards"] == last, "fingerprinting the frames in reverse order gives the same digests")
    for (_lp, _sp, prev), (label, (f0, f1), cur) in zip(a["steps"][:-1], a["steps"][1:]):
        changed = sorted(int(f) for f in prev if prev[f] != cur[f])
        ok(changed and all(f0 <= f <= f1 for f in changed), "%s on frames %d-%d changed frames %s and no other"
           % (label, f0, f1, changed))
    first = a["steps"][0][2]
    ok(len(set(first.values())) >= len(FRAMES) - 2, "frames of different shots have different fingerprints (%d of %d "
       "distinct)" % (len(set(first.values())), len(FRAMES)))
    print("[stamp] %d failure(s)" % fails)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
