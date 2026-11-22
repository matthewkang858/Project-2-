"""Throwaway test stage so each engine module can render and LOOK at its own work.

Not used by the final films (engine/look.py owns the real lighting and render settings).
"""
import math
import os

import bpy
from mathutils import Vector

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEST_DIR = os.path.join(ROOT, "out", "test")


def reset():
    """Empty scene. Returns it."""
    bpy.ops.wm.read_factory_settings(use_empty=True)
    return bpy.context.scene


def setup(scene, res=(540, 960), samples=16, threads=2):
    """Cheap Cycles CPU settings for test stills (2 threads: other agents share this 4-core machine)."""
    r = scene.render
    r.engine = "CYCLES"
    r.resolution_x, r.resolution_y = res
    r.resolution_percentage = 100
    r.image_settings.file_format = "PNG"
    r.threads_mode = "FIXED"
    r.threads = threads
    c = scene.cycles
    c.device = "CPU"
    c.samples = samples
    c.use_adaptive_sampling = True
    c.use_denoising = True
    c.max_bounces = 4
    c.sample_clamp_indirect = 6.0


def light(scene, preset="golden"):
    """Simple sun + flat sky. presets: 'day', 'golden', 'night'."""
    p = {
        "day": dict(sun=(1.0, 0.96, 0.9), energy=4.0, elev=60, sky=(0.45, 0.62, 0.95), sky_e=1.0),
        "golden": dict(sun=(1.0, 0.72, 0.45), energy=3.5, elev=18, sky=(0.55, 0.5, 0.75), sky_e=0.7),
        "night": dict(sun=(0.55, 0.65, 1.0), energy=0.25, elev=40, sky=(0.03, 0.035, 0.09), sky_e=0.6),
    }[preset]
    sun = bpy.data.lights.new("quick_sun", "SUN")
    sun.color, sun.energy, sun.angle = p["sun"], p["energy"], math.radians(2.5)
    ob = bpy.data.objects.new("quick_sun", sun)
    ob.rotation_euler = (math.radians(90 - p["elev"]), 0, math.radians(35))
    scene.collection.objects.link(ob)
    world = bpy.data.worlds.new("quick_world")
    world.use_nodes = True
    bg = world.node_tree.nodes["Background"]
    bg.inputs[0].default_value = (*p["sky"], 1)
    bg.inputs[1].default_value = p["sky_e"]
    scene.world = world
    return ob


def camera(scene, pos, target, lens=35, fstop=None):
    """Camera at pos looking at target. fstop=None disables depth of field; otherwise focus is on target."""
    cam = bpy.data.cameras.new("quick_cam")
    ob = bpy.data.objects.new("quick_cam", cam)
    ob.location = pos
    d = Vector(target) - Vector(pos)
    ob.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
    cam.lens = lens
    cam.sensor_fit = "VERTICAL"
    if fstop:
        cam.dof.use_dof = True
        cam.dof.focus_distance = d.length
        cam.dof.aperture_fstop = fstop
    scene.collection.objects.link(ob)
    scene.camera = ob
    return ob


def render(scene, name):
    """Render a still to out/test/<name>.png and return the path."""
    os.makedirs(TEST_DIR, exist_ok=True)
    path = os.path.join(TEST_DIR, name + ".png")
    scene.render.filepath = path
    bpy.ops.render.render(write_still=True)
    return path
