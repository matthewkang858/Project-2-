"""Independent checker's third probe of films/sixseconds (no render): the runner's crouch on the pillar, what the
runner holds, the gt19 runner against the piglins at the gold, the part that jumps on the gt18 -> gt19 match cut.
$BPY -m tools.check_sixseconds_technical_probe3
"""
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


def main():
    import render
    ses = render.Session("sixseconds", sky="soul")
    st = ses.result["stage"]
    scene = ses.scene
    rb = st.cast["runner_br"]
    print("runner_br _crouch list:", getattr(rb, "_crouch", None))
    for f in (828, 830, 870, 890, 946, 950, 970, 990):
        scene.frame_set(f)
        print("  f%d crouching_at=%s torso rot x=%.3f head z=%.3f root z=%.3f" % (
            f, rb.crouching_at(f), rb.torso.rotation_euler[0], rb.head.matrix_world.translation[2],
            rb.root.matrix_world.translation[2]))
    rp = st.cast["runner_pt"]
    for f in (290, 400, 440, 520, 575, 1300):
        print("  runner_pt f%d right hand: %s" % (f, rp.holding_at("right", f)))
    for f in (700, 760, 830, 960):
        print("  runner_br f%d right hand: %s" % (f, rb.holding_at("right", f)))
    rg = st.cast["runner_gt"]
    pigs = [st.cast[n] for n in ("piglin_gt1", "piglin_gt2", "piglin_xbow_gt3")]
    worst = []
    for f in range(1173, 1283):
        scene.frame_set(f)
        r = rg.root.matrix_world.translation
        for p in pigs:
            q = p.root.matrix_world.translation
            d = math.hypot(r[0] - q[0], r[1] - q[1])
            worst.append((round(d, 2), f, p.name, (round(r[0], 2), round(r[1], 2)), (round(q[0], 2), round(q[1], 2))))
    worst.sort()
    print("gt19 runner vs gold piglins, closest approaches (hit boxes touch below 0.6):", worst[:5])
    # match cut: which parts of piglin_gt1 jump 1172 -> 1173
    c = st.cast["piglin_gt1"]
    obs = [c.root] + list(c.root.children_recursive)
    scene.frame_set(1172)
    a = {o.name: o.matrix_world.to_euler() for o in obs}
    scene.frame_set(1173)
    jumps = sorted(((max(abs(x - y) for x, y in zip(a[o.name], o.matrix_world.to_euler())), o.name) for o in obs),
                   reverse=True)[:5]
    print("match cut piglin_gt1 biggest part rotation changes 1172->1173:", [(round(d, 4), n) for d, n in jumps])
    scene.frame_set(1171)
    a = {o.name: o.matrix_world.to_euler() for o in obs}
    scene.frame_set(1172)
    jumps = sorted(((max(abs(x - y) for x, y in zip(a[o.name], o.matrix_world.to_euler())), o.name) for o in obs),
                   reverse=True)[:3]
    print("   for comparison 1171->1172:", [(round(d, 4), n) for d, n in jumps])


if __name__ == "__main__":
    main()
