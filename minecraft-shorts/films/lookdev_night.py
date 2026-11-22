"""Look-dev film 'night' (see films/lookdev.py): $BPY -m render lookdev_night --still 0.5"""
from . import lookdev


def build(scene):
    """Build the 'night' look-dev film."""
    return lookdev.build_film(scene, "lookdev_night")
