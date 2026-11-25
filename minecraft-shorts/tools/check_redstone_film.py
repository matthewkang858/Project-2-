"""Independent check of engine/redstone.py: a film-like build written from the module docstring alone.

    $BPY -m tools.check_redstone_film checks            numeric / robustness checks (no rendering)
    $BPY -m tools.check_redstone_film render NAME ...   render frames 540x960, 16 spp, 2 threads, motion blur
                                                        -> out/test/check_redstone_<NAME>.png
    $BPY -m tools.check_redstone_film digest            print the digest of every frame fingerprint (for 2 processes)

Shots (one film, golden look-dev sky, village built with an edit hook):
  door   "Two Apples" beats 9 / 15: Steve flips a wall lever on the front pier of a one-block cell, the two stone
         blocks behind the librarian slide east into the end wall on sticky pistons, later they push shut.
  row    "Leg Day" beats 13 / 18 / 19: 12 sticky pistons in the top course of a wall, planks and anvils, a lit dust
         line behind them to one lever; the 12th piston placed in shot; the lever flipped, all retract.
  bench  "Leg Day" beat 7: efe plants a redstone torch, dust, repeater, lamp, piston (signal()).
  close  the planted torch and the repeater, close.
"""
import math
import os
import sys

import bpy
from mathutils import Vector

from engine import look, players, redstone, shots, village
from films import lookdev as L

SKY = dict(preset="golden", az=62.0, el=27.0, bloom=1.0, grade="warm")

DOOR_BOX = (4, 42, 10, 49)
DOOR_CELLS = [(7, 47, 0), (7, 47, 1)]
DOOR_LEVER = (6, 45, 1)                       # wall lever, sticking out south from the pier (6, 46, 1)
WALL = (22, 44, 35, 45)                       # z 0..3
PCELLS = [(x, 45, 3) for x in range(23, 35)]  # 12 sticky pistons facing north (the 12th is placed in shot)
DUST = [(x, 44, 4) for x in range(23, 35)]
RLEVER = (22, 44, 4)
BENCH = dict(torch=(13, 32, 0), dust=[(14, 32, 0), (15, 32, 0)], rep=(16, 32, 0), block=(17, 32, 0),
             lamp=(17, 32, 1), piston=(17, 31, 0))


def hook(b):
    w = b.w
    # ---- the door: a closed stone box, aisle south, cell, door cells, pistons in the east end wall, box north
    x0, y0, x1, y1 = DOOR_BOX
    for x in range(x0 - 1, x1 + 2):
        for y in range(y0 - 1, y1 + 2):
            b.clear_plants(x, y)
            b.reserved.add((x, y))
    w.fill(x0, y0, -1, x1, y1, 2, "stone")
    hollow = [(x, y, z) for x in range(5, 10) for y in range(43, 46) for z in (0, 1)]
    hollow += [(7, 46, z) for z in (0, 1)] + [(7, 48, z) for z in (0, 1)]
    hollow += redstone.door_cells(DOOR_CELLS, "east") + [DOOR_LEVER]
    hollow += [(x, y, 2) for x in range(5, 10) for y in range(43, 47)]     # roof off over aisle + cell (camera)
    redstone.carve(b, hollow)
    b.torch((5, 43, 1), "wall_torch", {"facing": "north"}, group="probe_door")
    b.torch((9, 43, 1), "wall_torch", {"facing": "north"}, group="probe_door")
    b.allow(DOOR_BOX)
    # ---- the wall with the piston course, and the road below it
    for x in range(20, 39):
        for y in range(42, 54):
            b.set_ground(x, y, 0)
            b.clear_plants(x, y)
            b.reserved.add((x, y))
    for x in range(20, 39):
        for y in range(46, 50):
            w.set(x, y, -1, "cobblestone")
    w.fill(WALL[0], WALL[1], 0, WALL[2], WALL[3], 3, "stone")
    redstone.carve(b, PCELLS)
    # ---- the bench of beat 7
    redstone.bench(b, 11, 29, 19, 35, level=0)
    w.set(*BENCH["block"], "stone")


def build(scene):
    if os.environ.get("RS_DUST_GLOW") is not None:            # probe: the module's film choice switched
        redstone.DUST_GLOW = float(os.environ["RS_DUST_GLOW"])
    v = village.build_village(scene, seed=1, edit=hook)
    if os.environ.get("RS_SKY") == "dusk":                     # probe: the dusk of beats 22 / 24
        SKY.update(preset="dusk", el=5.0, az=170.0, grade="warm", bloom=1.2)
    sky = look.set_time(scene, SKY["preset"], sun_azimuth=SKY["az"], sun_elevation=SKY["el"])
    look.setup_compositor(scene, bloom=SKY["bloom"], grade=SKY["grade"])
    film = shots.Film(scene, fps=24)
    st = L.Stage(scene, film, v, sky)
    k = redstone.kit(v)
    out = dict(film=film, st=st, v=v, k=k, frames={}, parts={})
    P = out["parts"]

    # ================= door (3 s) =================
    s = st.shot("door", 3.0)
    f0 = s.frame_start
    steve = players.add_player(st, "steve", "steve")
    dad = st.actor("dad", "librarian")
    dad.place(f0, (7.5, 46.45, 0.0), 0.0)
    lever = k.lever(DOOR_LEVER, "wall", "south")
    door = k.piston_door(DOOR_CELLS, "east", block="stone", closed=True)
    pos, yaw = lever.stand()
    steve.place(f0, pos, yaw)
    ff = redstone.flip_by(steve, lever, f0 + 10)
    t_open_end = door.open(ff)
    lever.flip(f0 + 50)
    door.close(f0 + 50)
    for p in (lever, door):
        st.cast[p.name] = p
    st.use(s, steve, dad, lever, door)
    s.lens(24, 4.0)
    s.move((8.3, 44.0, 3.0), (7.45, 47.4, 0.9))
    s.focus((7.5, 47.0, 1.0))
    st.lights(s, scale=1.0, groups={"probe_door": 1.4}, near=(7.5, 45.0, 1.0), radius=5.0)
    P.update(lever=lever, door=door, steve=steve, dad=dad)
    out["door"] = dict(click=f0 + 10, flip=ff, open_end=t_open_end, close=f0 + 50)
    out["frames"]["door"] = [f0 + 9, ff, ff + 1, ff + 6, f0 + 51]

    # ================= row (3 s) =================
    s = st.shot("row", 3.0)
    f0 = s.frame_start
    row = k.piston_row(PCELLS[:11], "north", carry="oak_planks", extended=True)
    p12 = k.piston(PCELLS[11], "north", sticky=True)
    anvils = [k.block("anvil", (c[0], c[1] + 2, c[2] + 1), {"facing": "west"}) for c in PCELLS[:11]]
    rlever = k.lever(RLEVER, "floor", "east", powered=True)
    wire = k.wire(DUST, source=RLEVER)
    wire.power(f0, source=RLEVER)
    steve.place(f0, (35.4, 45.5, 4.0), math.radians(60))
    p12.place(f0 + 8, player=steve)
    p12.extend(f0 + 8)
    plank12 = k.block("oak_planks", (34, 47, 3), frame=f0 + 16)
    anvil12 = k.block("anvil", (34, 47, 4), {"facing": "west"}, frame=f0 + 24)
    t = rlever.flip(f0 + 40)
    t_end = redstone.unsignal(t, wire, tuple(row.pistons) + (p12,))
    for p in [row, p12, rlever, wire, plank12, anvil12] + anvils:
        st.cast[p.name] = p
    st.use(s, steve, row, p12, rlever, wire, plank12, anvil12, *anvils)
    s.lens(20, 5.6)
    s.move((37.6, 50.6, 0.7), (27.0, 46.4, 3.6))
    s.focus((33.0, 46.5, 3.5))
    P.update(row=row, p12=p12, anvils=anvils, rlever=rlever, wire=wire, plank12=plank12, anvil12=anvil12)
    out["row"] = dict(place=f0 + 8, flip=t, end=t_end)
    out["frames"]["row"] = [f0 + 7, f0 + 8, f0 + 9, f0 + 41, f0 + 42, f0 + 46]

    # ================= bench (2 s) =================
    s = st.shot("bench", 2.0)
    f0 = s.frame_start
    efe = players.add_player(st, "efe", "efe", slim=True)
    efe.place(f0, (14.6, 33.55, 0.0), 0.0)
    redstone.hold_torch(efe, "right")
    torch = k.torch(BENCH["torch"])
    wire2 = k.wire(BENCH["dust"], source=BENCH["torch"])
    rep = k.repeater(BENCH["rep"], "east", delay=1)
    lamp = k.lamp(BENCH["lamp"])
    pis = k.piston(BENCH["piston"], "south")
    efe.look_at(f0, Vector(BENCH["torch"]) + Vector((0.5, 0.5, 0.3)), ease=0)
    tp = torch.plant(f0 + 6, player=efe)
    t_end = redstone.signal(tp, wire2, rep, (lamp, pis))
    efe.look_at(f0 + 12, lamp.center, ease=6)
    bench_parts = [torch, wire2, rep, lamp, pis]
    for p in bench_parts:
        st.cast[p.name] = p
    st.use(s, efe, *bench_parts)
    s.lens(20, 3.2)
    s.move((15.6, 27.8, 1.3), (15.6, 33.0, 0.9))
    s.focus(efe.head)
    P.update(efe=efe, torch=torch, wire2=wire2, rep=rep, lamp=lamp, pis=pis)
    out["bench"] = dict(plant=tp, end=t_end)
    out["frames"]["bench"] = [f0 + 6, f0 + 7, f0 + 9, f0 + 10, f0 + 20]

    # ================= close (0.75 s) =================
    s = st.shot("close", 0.75)
    f0 = s.frame_start
    st.use(s, *bench_parts)
    s.lens(50, 5.6)
    s.move((14.1, 31.0, 0.85), (13.75, 32.5, 0.5))
    s.focus((13.5, 32.5, 0.5))
    out["frames"]["close"] = [f0 + 4]
    if os.environ.get("RS_HALO_FIX"):                       # probe: the game's back-face culling on the lit halo
        for part in (torch, rep):
            for ob in part.looks.looks[True]:
                ob.data = ob.data.copy()
                for i, m in enumerate(list(ob.data.materials)):
                    m2 = m.copy()
                    nt = m2.node_tree
                    outn = next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL")
                    link = outn.inputs["Surface"].links[0]
                    src = link.from_socket
                    nt.links.remove(link)
                    mix = nt.nodes.new("ShaderNodeMixShader")
                    geo = nt.nodes.new("ShaderNodeNewGeometry")
                    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
                    nt.links.new(geo.outputs["Backfacing"], mix.inputs[0])
                    nt.links.new(src, mix.inputs[1])
                    nt.links.new(tr.outputs[0], mix.inputs[2])
                    nt.links.new(mix.outputs[0], outn.inputs["Surface"])
                    ob.data.materials[i] = m2
    st.finish()
    return out


def fresh(res=(540, 960), samples=16):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    look.setup_render(scene, res=res, samples=samples, threads=2, motion_blur=True)
    return scene


def render(names):
    import time

    scene = fresh()
    out = build(scene)
    film = out["film"]
    d = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "out", "test")
    for name in names:
        shot, _, idx = name.partition(":")
        frames = out["frames"][shot] if not idx else [out["frames"][shot][int(i)] for i in idx.split(",")]
        for f in frames:
            t = time.time()
            film.goto(f)
            path = os.path.join(d, "check_redstone_%s_f%d%s.png" % (shot, f, os.environ.get("RS_TAG", "")))
            scene.render.filepath = path
            bpy.ops.render.render(write_still=True)
            print("[check_redstone_film] %s frame %d -> %s %.1f s" % (shot, f, path, time.time() - t), flush=True)


def digest():
    import hashlib

    from engine import stamp

    scene = fresh((720, 1280), 24)
    out = build(scene)
    film = out["film"]
    fp = stamp.Fingerprinter(scene, film)
    h = hashlib.sha256()
    prints = {}
    for f in range(film.frame_start, film.frame_end + 1):
        prints[f] = fp.frame(f)["fp"]
        h.update(("%d:%s;" % (f, prints[f])).encode())
    print("DIGEST", h.hexdigest()[:16])
    return out, prints


if __name__ == "__main__":
    a = sys.argv[1:]
    if a and a[0] == "render":
        render(a[1:])
    elif a and a[0] == "digest":
        digest()
    else:
        from tools import check_redstone_film_checks as C

        C.main(a[1:])
