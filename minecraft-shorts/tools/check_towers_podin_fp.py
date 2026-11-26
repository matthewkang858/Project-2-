"""Checker probe (engine/towers.py review): the pod_in proof shot's fingerprint in this process."""
import bpy
from engine import stamp
from tools import towers_proof as tp
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
b = tp.build(scene, res=(720, 1280), samples=24, threads=4)
s = [x for x in b["film"].shots if x.name == "pod_in"][0]
fp = stamp.Fingerprinter(scene, b["film"])
print("pod_in frame %d fp %s" % (s.frame_start + 10, fp.frame(s.frame_start + 10)["fp"]))
