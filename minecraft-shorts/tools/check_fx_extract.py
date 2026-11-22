"""Checker's probe: fx.extract_block on other block kinds, and what the bmesh round trip does to the static meshes."""
import sys
import collections

import bpy
import numpy as np


def corner_normals(me):
    n = np.zeros(len(me.loops) * 3, dtype=np.float32)
    me.corner_normals.foreach_get("vector", n)
    return n.reshape(-1, 3)


def poly_table(ob):
    """{sorted corner key: (normals per corner sorted, uv sorted)} for every polygon of a mesh object."""
    me = ob.data
    cn = corner_normals(me)
    uv = me.uv_layers[0].data if me.uv_layers else None
    out = {}
    for p in me.polygons:
        key = tuple(sorted((round(me.vertices[v].co.x, 4), round(me.vertices[v].co.y, 4), round(me.vertices[v].co.z, 4))
                           for v in p.vertices))
        ns = tuple(sorted(tuple(np.round(cn[li], 3)) for li in p.loop_indices))
        us = tuple(sorted((round(uv[li].uv.x, 4), round(uv[li].uv.y, 4)) for li in p.loop_indices)) if uv else ()
        out.setdefault(key, []).append((ns, us, p.use_smooth))
    return out


def main():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    from engine import fx, village

    scene = bpy.context.scene
    v = village.build_village(scene, seed=1)
    w = v.world
    kinds = collections.defaultdict(list)
    for pos, st in w.blocks.items():
        bid = st[0] if isinstance(st, tuple) else w.block_id(*pos)
        kinds[bid].append(pos)
    print("block kinds in the village:", len(kinds))
    want = ["short_grass", "poppy", "wall_torch", "torch", "lantern", "oak_stairs", "glass_pane", "composter", "white_bed",
            "oak_door", "bell", "water", "oak_fence", "cobblestone", "grass_block", "oak_log", "iron_bars", "oak_trapdoor",
            "stonecutter", "blast_furnace", "smithing_table", "oak_leaves", "dirt_path", "wheat", "farmland", "oak_slab"]
    bad = 0
    for bid in want:
        if bid not in kinds:
            print("%-16s (not in the village)" % bid)
            continue
        cell = sorted(kinds[bid])[len(kinds[bid]) // 2]
        # snapshot the static meshes this block and its neighbours may share
        objs = [o for o in list(v.objects) + [o for g in v.cutaways.values() for o in g] if o.type == "MESH"]
        before = {o.name: (len(o.data.polygons), poly_table(o) if len(o.data.polygons) < 60000 else None) for o in objs}
        try:
            b = fx.extract_block(v, cell)
        except Exception as e:                                   # noqa: BLE001
            print("%-16s %s -> %s: %s" % (bid, cell, type(e).__name__, str(e)[:110]))
            continue
        # every static polygon that is still there must be unchanged (normals, uvs); count what went
        changed = lost = 0
        for o in objs:
            n0, t0 = before[o.name]
            if len(o.data.polygons) == n0:
                continue
            lost += n0 - len(o.data.polygons)
            if t0 is None:
                continue
            t1 = poly_table(o)
            for key, vals in t1.items():
                if sorted(t0.get(key, [])) != sorted(vals) and len(t0.get(key, [])) == len(vals):
                    changed += 1
        flag = "" if changed == 0 else "  <-- %d REMAINING STATIC FACES CHANGED (normals/uv)" % changed
        if changed:
            bad += 1
        print("%-16s %s faces %d/%d patch %d removed %d shape boxes %d top %.3f particle %s%s" % (
            bid, cell, b.stats["faces"], b.stats["model_faces"], b.stats["patch_faces"], lost, len(b.shape), b.top - cell[2],
            b.particle_texture, flag))
    print("[extract probe] %d kinds with damaged static meshes" % bad)
    return bad


if __name__ == "__main__":
    sys.exit(1 if main() else 0)
