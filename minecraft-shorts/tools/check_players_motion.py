"""Independent checker probe for engine/players.py: motion numbers and robustness (no rendering).

    $BPY -m tools.check_players_motion
"""
import math
import sys

import bpy
from mathutils import Vector

bpy.ops.wm.read_factory_settings(use_empty=True)
from engine import characters as ch                   # noqa: E402
from engine import players as pl                      # noqa: E402

scene = bpy.context.scene
U = 0.9375 / 16.0
FAIL = []
ROT, LOC = "rotation_euler", "location"


def bad(msg):
    FAIL.append(msg)
    print("  !!", msg)


def ev(ob, path, i, f):
    return ch._val(ob, path, i, f)


def series(ob, path, i, f0, f1, step=1.0):
    out = []
    f = f0
    while f <= f1 + 1e-9:
        out.append((f, ev(ob, path, i, f)))
        f += step
    return out


def max_jump(vals):
    """Largest frame-to-frame change and where."""
    best = (0.0, None)
    for (fa, a), (fb, b) in zip(vals, vals[1:]):
        if abs(b - a) > best[0]:
            best = (abs(b - a), fb)
    return best


# ---------------------------------------------------------------- my own simulation of the game's numbers
def game_walk(v_target_per_tick, ticks):
    """Per-tick displacement: v += 0.098 * k; move; v *= 0.546 (LivingEntity.travel on ordinary ground)."""
    acc = v_target_per_tick * (1 - 0.546)
    v, out = 0.0, []
    for _ in range(ticks):
        v += acc
        out.append(v)
        v *= 0.546
    return out


print("== game constants (my own arithmetic)")
walk = 0.1 * 0.98 / (1 - 0.6 * 0.91) * 20
print("  walk %.4f  sprint %.4f  sneak %.4f blocks/s" % (walk, walk * 1.3, walk * 0.3))
y, vy, arc = 0.0, 0.42, [0.0]
while True:
    y += vy
    vy = (vy - 0.08) * 0.98
    if y <= 0:
        arc.append(0.0)
        break
    arc.append(y)
print("  jump: %d ticks, peak %.4f" % (len(arc) - 1, max(arc)))
if len(arc) - 1 != pl.JUMP_TICKS or abs(max(arc) - pl.JUMP_HEIGHT) > 1e-6:
    bad("jump arc differs")
for name, mine, theirs in (("WALK", walk, pl.WALK_SPEED), ("SPRINT", walk * 1.3, pl.SPRINT_SPEED), ("SNEAK", walk * 0.3, pl.SNEAK_SPEED)):
    if abs(mine - theirs) > 0.003:
        bad("%s speed %.4f vs %.4f" % (name, theirs, mine))
# sprint-jump, simulated with the game's order: jump adds 0.2, ground accel 0.1274, friction 0.546 on the take-off
# tick; 0.02548 and 0.91 in the air
v = 0.2806
for hop in range(60):
    d = 0.0
    for t in range(12):
        if t == 0:
            v += 0.2 + 0.1 * 1.3 * 0.98
            d += v
            v *= 0.546
        else:
            v += 0.02 * 1.3 * 0.98
            d += v
            v *= 0.91
print("  sprint-jump: %.4f blocks per hop, %.4f blocks/s (module %.4f)" % (d, d / 12 * 20, pl.SPRINT_JUMP_SPEED))

# ---------------------------------------------------------------- 1. walk
print("\n== walk 20 blocks at the default speed")
p = pl.make_player("w", "steve")
p.place(10, (0, 0, 0), math.radians(90))            # facing +X
end = p.walk(10, [(0, 0, 0), (20, 0, 0)])
xs = series(p.root, LOC, 0, 10, end + 20)
sp = [(f, (b - a) * 24) for (f, a), (_g, b) in zip(xs, xs[1:])]
print("  end frame %d (%.2f s); x at end %.3f; top speed %.3f; speeds first 8 frames %s" % (
    end, (end - 10) / 24, ev(p.root, LOC, 0, end), max(s for _f, s in sp), [round(s, 2) for _f, s in sp[:8]]))
mine = game_walk(pl.WALK_SPEED / 20, 8)
print("  game: displacement per tick while starting: %s (x20 = %s blocks/s)" % ([round(m, 3) for m in mine], [round(m * 20, 2) for m in mine]))
legs = series(p.leg_r, ROT, 0, 10, end + 20)
arms_r = series(p.arm_r, ROT, 0, 10, end + 20)
arms_l = series(p.arm_l, ROT, 0, 10, end + 20)
legl = series(p.leg_l, ROT, 0, 10, end + 20)
print("  leg_r peak %.3f rad (game 1.4 * %.3f = %.3f); arm peak %.3f (game %.3f)" % (
    max(abs(v) for _f, v in legs), min(4 * pl.WALK_SPEED / 20, 1), 1.4 * min(4 * pl.WALK_SPEED / 20, 1),
    max(abs(v) for _f, v in arms_r), min(4 * pl.WALK_SPEED / 20, 1)))
# phase: the game's rightLeg = +cos, leftArm = +cos, rightArm = -cos, leftLeg = -cos
mid = 60
a, b, c, d = ev(p.leg_r, ROT, 0, mid), ev(p.arm_l, ROT, 0, mid), ev(p.arm_r, ROT, 0, mid), ev(p.leg_l, ROT, 0, mid)
print("  frame %d: leg_r %.3f arm_l %.3f arm_r %.3f leg_l %.3f" % (mid, a, b, c, d))
if not (a * b > 0 and a * c < 0 and a * d < 0):
    bad("limb phases are not the game's (right leg with left arm)")
# period
zero = [f for (f, v0), (_g, v1) in zip(legs, legs[1:]) if v0 < 0 <= v1 and 30 < f < 100]
if len(zero) > 2:
    per = (zero[-1] - zero[0]) / (len(zero) - 1)
    print("  cycle %.2f frames (game: 2 pi / 0.6662 / 0.863 ticks = %.2f frames)" % (per, 2 * math.pi / 0.6662 / (4 * pl.WALK_SPEED / 20) * 1.2))
print("  legs after the walk: frame %d %.4f, frame %d %.4f; largest frame-to-frame leg change %.3f rad at %s" % (
    end, ev(p.leg_r, ROT, 0, end), end + 18, ev(p.leg_r, ROT, 0, end + 18), *max_jump(legs)))
# foot sense: with rig +x rotation of a leg, does the foot go FORWARD (toward -Y local)?
q = pl.make_player("sign", "steve")
q.place(1, (0, 0, 0), 0.0)
q.leg_r.rotation_euler[0] = 0.5
q.arm_r.rotation_euler[0] = -0.5
bpy.context.view_layer.update()
foot = q.leg_r.matrix_world @ Vector((0, 0, -12 * U))
hand = q.arm_r.matrix_world @ Vector((0, 0, -10 * U))
print("  rig sign: leg x +0.5 puts the foot at y %.3f (game: +xRot = foot BACK = +y here); arm x -0.5 puts the hand at y %.3f (game: forward = -y)" % (foot.y, hand.y))

# ---------------------------------------------------------------- 2. chained walks (a director's usual pattern)
print("\n== chained moves inside one shot")
c1 = pl.make_player("c1", "alex")
c1.place(1, (0, 3, 0), math.radians(90))
e1 = c1.walk(1, [(0, 3, 0), (6, 3, 0)], ramp=(True, False))
e2 = c1.walk(e1, [(6, 3, 0), (14, 3, 0)], sprint=True, ramp=(False, True), from_current=False)
legs = series(c1.leg_r, ROT, 0, 1, e2 + 20)
xs = series(c1.root, LOC, 0, 1, e2 + 5)
jl, fl = max_jump(legs)
jx, fx_ = max_jump(xs)
print("  walk(ramp=(True, False)) to frame %d, then walk(sprint, ramp=(False, True)) to %d" % (e1, e2))
print("  leg_r around the join: %s" % [(int(f), round(v, 2)) for f, v in legs if e1 - 3 <= f <= e1 + 3])
print("  largest leg change %.2f rad at frame %s; largest root step %.3f blocks at frame %s (sprint step %.3f)" % (jl, fl, jx, fx_, 5.612 / 24))
per_frame_max = 0.6662 * 1.0 / 1.2 * 1.4      # the fastest the game's leg can turn per film frame (rad)
if jl > per_frame_max * 1.25:
    bad("chained walk -> sprint: the legs pop %.2f rad in one frame at frame %s (the game's fastest swing is %.2f rad per frame)" % (jl, fl, per_frame_max))

c2 = pl.make_player("c2", "kai")
c2.place(1, (0, 6, 0), math.radians(90))
e1 = c2.walk(1, [(0, 6, 0), (6, 6, 0)], sprint=True, ramp=(True, False))
e2 = c2.sprint_jump(e1, [(6, 6, 0), (6 + 4.2767 * 3, 6, 0)])
legs = series(c2.leg_r, ROT, 0, 1, e2 + 20)
jl, fl = max_jump(legs)
zs = series(c2.root, LOC, 2, 1, e2 + 5)
print("  sprint to frame %d then sprint_jump to %d: largest leg change %.2f rad at frame %s; leg_r around the join %s" % (
    e1, e2, jl, fl, [(int(f), round(v, 2)) for f, v in legs if e1 - 3 <= f <= e1 + 3]))
if jl > per_frame_max * 1.25:
    bad("sprint -> sprint_jump: the legs pop %.2f rad in one frame at frame %s" % (jl, fl))
print("  after the last hop: z at end %.3f; legs at end+1 %.3f, end+10 %.3f, end+20 %.3f; root x speed last frames %s" % (
    ev(c2.root, LOC, 2, e2), ev(c2.leg_r, ROT, 0, e2 + 1), ev(c2.leg_r, ROT, 0, e2 + 10), ev(c2.leg_r, ROT, 0, e2 + 20),
    [round((ev(c2.root, LOC, 0, f + 1) - ev(c2.root, LOC, 0, f)) * 24, 2) for f in range(e2 - 3, e2 + 2)]))

c3 = pl.make_player("c3", "noor")
c3.place(1, (0, 9, 0), math.radians(90))
e1 = c3.walk(1, [(0, 9, 0), (5, 9, 0)])
e2 = c3.walk(e1, [(5, 9, 0), (5, 14, 0)], from_current=True)
legs = series(c3.leg_r, ROT, 0, 1, e2 + 20)
jl, fl = max_jump(legs)
yaws = series(c3.root, ROT, 2, 1, e2)
jy, fy = max_jump(yaws)
print("  walk, stop, walk again from the same frame %d: largest leg change %.2f rad at frame %s; largest yaw step %.1f deg at %s" % (
    e1, jl, fl, math.degrees(jy), fy))
if jl > per_frame_max * 1.25:
    bad("walk -> walk: the legs pop %.2f rad at frame %s" % (jl, fl))

# a polyline with a corner
c4 = pl.make_player("c4", "ari")
c4.place(1, (0, 12, 0), math.radians(90))
e = c4.walk(1, [(0, 12, 0), (5, 12, 0), (5, 17, 0)])
yaws = series(c4.root, ROT, 2, 1, e)
jy, fy = max_jump(yaws)
print("  corner of 90 deg at walking speed: largest yaw step %.1f deg/frame at frame %s" % (math.degrees(jy), fy))

# ---------------------------------------------------------------- 3. sprint_jump numbers
print("\n== sprint_jump")
j = pl.make_player("j", "efe")
j.place(1, (0, 20, 0), math.radians(90))
e = j.sprint_jump(1, [(0, 20, 0), (4.2767 * 4, 20, 0)])
zs = series(j.root, LOC, 2, 1, e)
xs = series(j.root, LOC, 0, 1, e)
print("  4 hops: %d frames (4 * 14.4 = 57.6); peak %.4f; speed %.3f blocks/s; z on tick marks %s" % (
    e - 1, max(v for _f, v in zs), (xs[-1][1] - xs[0][1]) / ((e - 1) / 24), [round(ev(j.root, LOC, 2, 1 + k * 1.2), 3) for k in range(13)]))
# uneven ground: does sprint_jump follow path z?
j2 = pl.make_player("j2", "efe")
j2.place(1, (0, 23, 0), math.radians(90))
e = j2.sprint_jump(1, [(0, 23, 0), (8.55, 23, 1.0)])
print("  onto ground 1 block higher: end z %.3f (wanted 1.0), lowest z %.3f" % (ev(j2.root, LOC, 2, e), min(v for _f, v in series(j2.root, LOC, 2, 1, e))))

# ---------------------------------------------------------------- 4. cuts (Character.place semantics)
print("\n== cuts")
k = pl.make_player("k", "sunny")
pl.equip(k, "iron")
k.hold("iron_sword")
k.place(1, (0, 30, 0), math.radians(90))
e = k.walk(1, [(0, 30, 0), (30, 30, 0)])
k.place(73, (50, 40, 0), 0.0)                        # cut while the walk is still running
for f in (72.0, 72.5, 72.74, 72.76, 73.0):
    print("  frame %.2f root x %.3f  leg_r %.3f  yaw %.2f" % (f, ev(k.root, LOC, 0, f), ev(k.leg_r, ROT, 0, f), ev(k.root, ROT, 2, f)))
if abs(ev(k.root, LOC, 0, 72.5) - ev(k.root, LOC, 0, 72.0)) < 0.05:
    bad("the walk freezes before the cut")
if abs(ev(k.root, LOC, 0, 73.0) - 50) > 1e-6 or abs(ev(k.leg_r, ROT, 0, 73.0)) > 1e-6 or abs(ev(k.root, LOC, 0, 72.5) - 50) < 1:
    bad("place() at a cut: wrong position / pose on the cut frame, or it reaches back to 72.5")
# place twice on the same frame
k.place(73, (60, 41, 0), 1.0)
print("  placed again on 73: x %.2f y %.2f yaw %.2f; x at 72.5 %.2f" % (ev(k.root, LOC, 0, 73), ev(k.root, LOC, 1, 73), ev(k.root, ROT, 2, 73), ev(k.root, LOC, 0, 72.5)))
if abs(ev(k.root, LOC, 0, 73) - 60) > 1e-6:
    bad("place() twice on one frame keeps the first position")
# frame 1 calls
f1 = pl.make_player("f1", "zuri")
f1.place(1, (0, 50, 0), 0.0)
f1.hold("bow", frame=1)
f1.equip(boots="golden", frame=1)
f1.sneak(1)
f1.hurt(1)
scene.frame_set(1)
bpy.context.view_layer.update()
vis = {a.ob.name: not a.ob.hide_render for a in f1._attached}
print("  everything called on frame 1: visible on frame 1 %s; crouching %s; flash alpha %.1f; arm_r x %.3f (ITEM -0.314 + crouch 0.4 = 0.086)" % (
    vis, f1.crouching_at(1), f1.torso.color[3], f1.arm_r.rotation_euler.x))
if not all(vis.values()) or f1.torso.color[3] > 0.5:
    bad("frame-1 calls do not show on frame 1")
scene.frame_set(0)
print("  on frame 0: item visible %s" % {a.ob.name: not a.ob.hide_render for a in f1._attached})

# ---------------------------------------------------------------- 5. hold / equip twice, visibility over shots
print("\n== hold / equip twice, show()")
h = pl.make_player("h", "makena")
h.place(1, (0, 60, 0), 0.0)
a = h.hold("iron_sword")
b = h.hold("diamond_sword")
m1 = pl.equip(h, "diamond")
m2 = pl.equip(h, "iron")
h.show(1, False)
h.show(49, True)
h.hold(None, frame=80)
h.equip(helmet=None, frame=90)
rows = []
for f in (1, 48, 49, 79, 80, 95):
    scene.frame_set(f)
    rows.append((f, not a.hide_render, not b.hide_render, sum(not o.hide_render for o in m1), sum(not o.hide_render for o in m2),
                 not h.torso.hide_render))
print("  frame, first sword, second sword, diamond boxes, iron boxes, body:")
for r in rows:
    print("   ", r)
want = [(1, False, False, 0, 0, False), (48, False, False, 0, 0, False), (49, False, True, 0, 9, True),
        (79, False, True, 0, 9, True), (80, False, False, 0, 9, True), (95, False, False, 0, 8, True)]
if rows != want:
    bad("visibility of items / armor over show(), hold() and equip(): %s" % (rows,))
print("  objects parented to the rig: %d (old swords and armor stay as hidden objects)" % len(h._attached))

# an item given as an Object, then shown again by a later shot (the known Character.hold issue)
from engine import props                              # noqa: E402

o = pl.make_player("o", "ari")
o.place(1, (0, 70, 0), 0.0)
em = props.make_item("emerald")
o.hold(em)
o.hold(None, frame=30)
o.show(1, True)
o.show(40, False)
o.show(60, True)
got = []
for f in (10, 30, 45, 60, 61):
    scene.frame_set(f)
    got.append((f, not em.hide_render))
print("  emerald object dropped at 30, player shown again at 60:", got)
if got != [(10, True), (30, False), (45, False), (60, False), (61, False)]:
    bad("a dropped item comes back at the next show()")

# ---------------------------------------------------------------- 6. hurt / die timings against the classes
print("\n== hurt / death")
d = pl.make_player("d", "noor")
d.place(1, (0, 80, 0), 0.0)
e = d.hurt(20, from_point=(0, 78, 0))
print("  hurt(20): flash keys %s -> %d frames (10 ticks = 12); end %d" % (ch.read_keys(d.torso, "color", 3), 12, e))
x = yv = 0.0
vh, vv, air = 0.4, min(0.4, -0.0784 / 2 + 0.4), False
peak = 0.0
for t in range(1, 40):
    x += vh
    yv += vv
    vh *= 0.91 if air else 0.546
    vv = (vv - 0.08) * 0.98
    air = yv > 0
    peak = max(peak, yv)
    if not air:
        yv, vv = 0.0, -0.0784
        if vh < 0.003:
            break
print("  my knock-back: %.3f blocks, peak %.3f, %d ticks; module: %.3f blocks, peak %.3f" % (
    x, peak, t, ev(d.root, LOC, 1, e + 30) - 80, max(v for _f, v in series(d.root, LOC, 2, 20, e + 5, 0.3))))
d.place(100, (0, 80, 0), 0.0)
info = d.die(100)
roll = [(f, math.degrees(ev(d.root, ROT, 1, f))) for f in (100, 101.2, 102.4, 106, 112, 116.2, 118, 123)]
mine = [(f, 90 * min(1.0, math.sqrt(max(0.0, ((f - 100) / 1.2 - 1) / 20 * 1.6)))) for f, _v in roll]
print("  death roll (deg) module %s" % [(f, round(v, 1)) for f, v in roll])
print("             game   %s ; vanishes on %d (20 ticks = 24 frames)" % ([(f, round(v, 1)) for f, v in mine], info["frame"]))
if max(abs(a[1] - b[1]) for a, b in zip(roll, mine)) > 3.0:
    bad("death roll differs from LivingEntityRenderer.setupRotations")
scene.frame_set(info["frame"] - 1)
v0 = not d.torso.hide_render
scene.frame_set(info["frame"])
print("  visible on the last frame %s, on the vanish frame %s; where the body lies: left of a yaw-0 player = +x: point %s" % (
    v0, not d.torso.hide_render, tuple(round(c, 2) for c in info["point"])))
d.place(200, (0, 80, 0), 0.0)
d.show(200, True)
scene.frame_set(200)
bpy.context.view_layer.update()
print("  placed again at 200: roll %.2f, colour alpha %.1f, visible %s, torso scale %.4f" % (
    d.root.rotation_euler.y, d.torso.color[3], not d.torso.hide_render, d.torso.scale.x))

# ---------------------------------------------------------------- 7. crouch
print("\n== crouch")
s = pl.make_player("s", "steve")
s.place(1, (0, 90, 0), 0.0)
scene.frame_set(1)
bpy.context.view_layer.update()
head0 = s.head.matrix_world.translation.copy()
arm0 = s.arm_r.matrix_world.translation.copy()
leg0 = s.leg_r.matrix_world.translation.copy()
s.sneak(10)
scene.frame_set(10)
bpy.context.view_layer.update()
dh = (s.head.matrix_world.translation - head0) / U
da = (s.arm_r.matrix_world.translation - arm0) / U
dl = (s.leg_r.matrix_world.translation - leg0) / U
off = 2.0 / 16.0 / U
print("  head pivot moved (px) %s  want (0, 0, %.2f)" % (tuple(round(c, 2) for c in dh), -4.2 - off))
print("  arm pivot moved  (px) %s  want (0, 0, %.2f)" % (tuple(round(c, 2) for c in da), -3.2 - off))
print("  leg pivot moved  (px) %s  want (0, +4, %.2f)" % (tuple(round(c, 2) for c in dl), -off))
print("  torso tilt %.3f (0.5), arm x %.3f (0.4)" % (s.torso.rotation_euler.x, s.arm_r.rotation_euler.x))
# which way does the torso lean? its top (the neck) must stay and the hip end go BACK (+y)
hip_end = s.torso.matrix_world @ Vector((0, 0, -12 * U))
print("  torso's lower end is at y %.3f relative to the feet %.3f (game: body.xRot +0.5 swings the hips back, legs z +4)" % (
    hip_end.y - 90, s.leg_r.matrix_world.translation.y - 90))
for name, got, want in (("head", dh, (0, 0, -4.2 - off)), ("arm", da, (0, 0, -3.2 - off)), ("leg", dl, (0, 4, -off))):
    if max(abs(got[i] - want[i]) for i in range(3)) > 0.02:
        bad("crouch: %s pivot moved %s px, the class says %s" % (name, tuple(round(c, 2) for c in got), want))
s.sneak(30, False)
scene.frame_set(30)
bpy.context.view_layer.update()
print("  stood up at 30: head back %s" % ((s.head.matrix_world.translation - head0).length < 1e-6))

# ---------------------------------------------------------------- 8. herobrine stillness + watch
print("\n== herobrine")
hb = pl.make_player("hb", "herobrine")
hb.place(1, (0, 100, 0), 0.0)
hb.idle(1, 240)
kid = ch.make_villager("kid", "none", child=True)
kid.place(1, (-8, 94, 0), math.radians(90))
kid.walk(1, [(-8, 94, 0), (8, 94, 0)], speed=1.6)
hb.watch(1, 240, kid)
keyed = []
for name in ("body", "torso", "arm_r", "arm_l", "leg_r", "leg_l", "hips", "root"):
    for path in (ROT, LOC):
        for i in range(3):
            ks = ch.read_keys(hb.parts[name], path, i)
            if len({round(v, 5) for _f, v, _i in ks}) > 1:
                keyed.append((name, path, i))
print("  channels that MOVE other than the head: %s" % keyed)
hy = series(hb.head, ROT, 2, 1, 240)
hp = series(hb.head, ROT, 0, 1, 240)
print("  head yaw %.0f..%.0f deg, largest step %.2f deg/frame at %s; pitch %.0f..%.0f" % (
    math.degrees(min(v for _f, v in hy)), math.degrees(max(v for _f, v in hy)), math.degrees(max_jump(hy)[0]), max_jump(hy)[1],
    math.degrees(min(v for _f, v in hp)), math.degrees(max(v for _f, v in hp))))
# does the head really point at the child? compare look_vector with the direction to the child's eyes
worst = 0.0
for f in (30, 80, 120, 160, 220):
    to = kid.eye_point(f) - hb.eye_point(f)
    ang = math.degrees(hb.look_vector(f).angle(to))
    worst = max(worst, ang)
print("  look_vector vs direction to the child at 5 frames: worst %.1f deg off" % worst)
if keyed:
    bad("herobrine moves something besides his head: %s" % keyed)
if worst > 6:
    bad("watch(): the head is up to %.1f degrees off its target" % worst)
print("  arms rest splay: %s (plain player %s)" % (tuple(round(a, 3) for a in hb.arm_r.rotation_euler), tuple(round(a, 3) for a in s.arm_r.rotation_euler)))
print("  glow material:", hb.torso.data.materials[0].name)
hb2 = pl.make_player("hb2", "herobrine", glow=7.0)
print("  second herobrine with glow 7:", hb2.head.data.materials[0].name, "| first still", hb.head.data.materials[0].name)

# ---------------------------------------------------------------- 9. use poses vs the classes
print("\n== arm poses (rig x = xRot, rig z = -yRot)")
u = pl.make_player("u", "steve")
u.place(1, (0, 110, 0), 0.0)
u.hold("shield", hand="left")
u.hold("bow")
u.block(10, 40)
print("  block (left, standing, head level): arm_l x %.4f (game 0 * 0.5 - 0.9425 = -0.9425), yRot %.4f (game +0.5236)" % (
    ev(u.arm_l, ROT, 0, 25), -ev(u.arm_l, ROT, 2, 25)))
info = u.draw_bow(60, 100)
print("  bow: arm_r x %.4f yRot %.4f (game -1.5708, -0.1); arm_l x %.4f yRot %.4f (game -1.5708, +0.5)" % (
    ev(u.arm_r, ROT, 0, 80), -ev(u.arm_r, ROT, 2, 80), ev(u.arm_l, ROT, 0, 80), -ev(u.arm_l, ROT, 2, 80)))
vis = {}
for f in (59, 64, 80, 86, 99, 100, 101, 110):
    scene.frame_set(f)
    vis[f] = [n or "bow" for n, a in u._hands["r"][-1].variants.items() if not a.ob.hide_render]
print("  bow model per frame:", vis, " (game: pulling_0 from use start, _1 at 65 %% = 13 ticks, _2 at 90 %% = 18 ticks)")
print("  release:", {kk: (tuple(round(c, 2) for c in vv) if hasattr(vv, "__len__") else vv) for kk, vv in info.items()})
t = pl.make_player("t", "ari")
t.place(1, (0, 120, 0), 0.0)
t.hold("goat_horn")
t.toot(10, 60)
print("  toot: arm_r x %.4f yRot %.4f (game -1.4835, -0.5236)" % (ev(t.arm_r, ROT, 0, 30), -ev(t.arm_r, ROT, 2, 30)))
# posed arm through a walk
w2 = pl.make_player("w2", "steve")
w2.place(1, (0, 130, 0), math.radians(90))
w2.hold("shield", hand="left")
w2.block(1, 80, ease=0)
w2.walk(1, [(0, 130, 0), (8, 130, 0)])
print("  blocking while walking: arm_l x at 20/40 %.3f %.3f; arm_r swings %.3f..%.3f" % (
    ev(w2.arm_l, ROT, 0, 20), ev(w2.arm_l, ROT, 0, 40), min(v for _f, v in series(w2.arm_r, ROT, 0, 1, 50)), max(v for _f, v in series(w2.arm_r, ROT, 0, 1, 50))))

print("\nFAILED:" if FAIL else "\nall motion checks passed")
for f in FAIL:
    print("  -", f)
sys.exit(1 if FAIL else 0)
