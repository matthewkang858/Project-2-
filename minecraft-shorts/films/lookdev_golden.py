"""Look-dev film 'golden' (see films/lookdev.py): $BPY -m render lookdev_golden --still 0.5"""
from . import lookdev


def build(scene):
    """Build the 'golden' look-dev film."""
    return lookdev.build_film(scene, "lookdev_golden")
