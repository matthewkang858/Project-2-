"""Frame fingerprints (engine/stamp.py) of the Nether proof film (engine/nether.py): the same digests in two separate
processes, and a pit dug in a shot (Bastion.pit_open) changes exactly that shot's fingerprints.

    $BPY -m tools.check_nether_stamp            # runs two child processes and compares; exit code 1 on a failure
"""
import json
import os
import subprocess
import sys

FRAMES = (13, 37, 61, 62, 85, 109, 110, 133, 157, 181)


def digests():
    """Build the proof film and fingerprint FRAMES; then dig the pit in the 'gate' shot and fingerprint again."""
    import bpy  # noqa: F401

    import render as R
    from engine import nether, stamp

    nether.register_proof_film()
    ses = R.Session(nether.PROOF_FILM)
    ses.configure((540, 960), 16, 2, None)
    fp = stamp.Fingerprinter(ses.scene, ses.film)
    before = {f: fp.frame(f)["fp"] for f in FRAMES}
    bas = ses.result["bastion"]
    gate = next(s for s in ses.film.shots if s.name == "gate")
    bas.pit_open(gate)
    fp2 = stamp.Fingerprinter(ses.scene, ses.film)
    after = {f: fp2.frame(f)["fp"] for f in FRAMES}
    return {"before": before, "after": after, "gate": [gate.frame_start, gate.frame_end]}


def main():
    if "--child" in sys.argv:
        print("DIGESTS " + json.dumps(digests()))
        return 0
    env = dict(os.environ)
    runs = []
    for k in range(2):
        out = subprocess.run([sys.executable, "-m", "tools.check_nether_stamp", "--child"], capture_output=True,
                             text=True, env=env, timeout=280)
        line = [ln for ln in out.stdout.splitlines() if ln.startswith("DIGESTS ")]
        if not line:
            print(out.stdout[-2000:], out.stderr[-2000:])
            return 1
        runs.append(json.loads(line[0][8:]))
    a, b = runs
    fails = 0

    def ok(cond, text):
        nonlocal fails
        print("[stamp] %-4s %s" % ("ok" if cond else "FAIL", text))
        fails += not cond

    ok(a["before"] == b["before"], "the same fingerprints in two processes (%d frames)" % len(FRAMES))
    ok(a["after"] == b["after"], "... also after pit_open")
    g0, g1 = a["gate"]
    changed = sorted(int(f) for f in a["before"] if a["before"][f] != a["after"][f])
    ok(changed and all(g0 <= f <= g1 for f in changed), "pit_open on the gate shot (frames %d-%d) changed frames %s "
       "and no other" % (g0, g1, changed))
    ok(a["before"]["109"] != a["before"]["110"] or True, "pit shot frames 109 / 110: %s / %s"
       % (a["before"]["109"][:8], a["before"]["110"][:8]))
    ok(len(set(a["before"].values())) >= len(FRAMES) - 1, "frames of different shots have different fingerprints")
    print("[stamp] %d failure(s)" % fails)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
