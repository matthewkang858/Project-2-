"""Proof still for engine/sets.py under the night sky (films/_sets_proof.py has the golden-hour ones and the
driver: `$BPY -m engine.sets night` -> out/test/sets_night.png). The look-dev night: moon azimuth 176, elevation 21."""
from films import _sets_proof

SKY = dict(preset="night", az=176.0, el=21.0, bloom=1.3, grade="cool")


def build(scene):
    """`$BPY -m render _sets_proof_night ...`: the forest edge at night."""
    return _sets_proof.build_film(scene, _sets_proof.NIGHT, SKY)
