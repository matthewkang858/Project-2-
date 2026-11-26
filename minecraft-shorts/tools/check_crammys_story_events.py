"""Checker probe: log the stub's arrow, fuse, death and look events (md13, md15) during one build. No render."""
import os, sys, math
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from engine import hostiles, characters as ch
log = []
_shoot = hostiles.Skeleton.shoot
def shoot(self, frame_start, target, release=None, part=None, **kw):
    fl = _shoot(self, frame_start, target, release=release, part=part, **kw)
    log.append("shoot %s draw %s release %s -> impact %d on %s kill=%s frames0=%s" % (
        self.name, frame_start, release, int(fl), getattr(target, 'name', target), kw.get('kill'), fl.frames[:1]))
    return fl
hostiles.Skeleton.shoot = shoot
_fuse = hostiles.Creeper.fuse
def fuse(self, f0, f1=None):
    r = _fuse(self, f0, f1); log.append("fuse %s from %s -> explodes %s" % (self.name, f0, r)); return r
hostiles.Creeper.fuse = fuse
_look = ch.Character.look_at
def look_at(self, frame, target, *a, **kw):
    if self.name in ("steve_md",) and 900 <= frame <= 1000:
        log.append("look_at %s f%s ease=%s" % (self.name, frame, kw.get('ease', a[0] if a else None)))
    return _look(self, frame, target, *a, **kw)
ch.Character.look_at = look_at
_lower = hostiles.Skeleton.lower
def lower(self, frame, ease=3):
    log.append("lower %s f%s" % (self.name, frame)); return _lower(self, frame, ease)
hostiles.Skeleton.lower = lower
import render
ses = render.Session("crammys", sky="night")
C = ses.result["context"]
print("\n".join(log))
print("md_kill", C.memo.get("md_kill"), "disc land", getattr(C.memo.get("md_disc"), "land_frame", None))
