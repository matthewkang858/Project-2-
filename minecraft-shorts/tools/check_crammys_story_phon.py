"""Checker probe: phonemes of candidate respellings (nothing written)."""
import sys
sys.path.insert(0, 'tools'); sys.path.insert(0, '.')
import narrate
e = narrate.Engines()
for t in ["Zuri", "Zoo-ree", "Zoori", "Zooree", "Zuree", "Zoo-ri", "Zooey", "Crammys", "Crammy", "Kai", "Noor", "Sunny", "Vocals", "Best Vocals", "disc eleven"]:
    print("%-14s %s" % (t, e.phonemes(t, "am_michael")))
