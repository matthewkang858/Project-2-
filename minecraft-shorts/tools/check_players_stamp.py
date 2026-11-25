"""Checker probe: do render.py's frame fingerprints (engine.stamp) work with players, and do they change where a
hurt flash, an armor change or a held-item change changes the picture?

    $BPY -m tools.check_players_stamp
"""
import bpy

from engine import stamp
from engine import players as pl
from tools import check_players_film as film_probe

FRAMES = [1, 20, 36, 37, 45, 46, 50, 57, 58, 59, 60, 70, 72]


def prints(mutate=None):
    scene, (a, b), cast = film_probe.build()
    if mutate:
        mutate(cast, b)
    fp = stamp.Fingerprinter(scene, film_probe.build.film)
    return {f: fp.frame(f)["parts"]["o"] for f in FRAMES}


base = prints()
again = prints()
print("same build twice, identical fingerprints:", base == again)


def later_hurt(cast, b):
    cast["ari"].hurt(b.frame_start + 20)            # ari flashes red on frames 57..68 (no knock-back)


def boots(cast, b):
    cast["hero"].equip(boots=None, frame=b.frame_start + 10)


def torch(cast, b):
    cast["hero"].hold(None, frame=b.frame_start + 20)


for label, fn, want in (("extra hurt flash on ari 57..68", later_hurt, [57, 58, 59, 60]),
                        ("hero's boots off from 47", boots, [50, 57, 58, 59, 60, 70, 72]),
                        ("hero drops the torch at 57", torch, [57, 58, 59, 60, 70, 72])):
    got = prints(fn)
    changed = [f for f in FRAMES if got[f] != base[f]]
    print("%-34s changed frames %s  (expected %s)  %s" % (label, changed, want, "ok" if changed == want else "DIFFERENT"))
