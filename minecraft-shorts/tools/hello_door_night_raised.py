"""The Hello, door_night sequence: its shots under the shared cameras the director asked the lead for, IN MEMORY
(no project file is changed): CAMS "door_front" = the wider candidate that shows the night sky, and CAMS "beside"
raised to z 1.9 (target z 1.5) with the motion review's start. Then either the door_night probe or stills.

    $BPY -m tools.hello_door_night_raised probe dn02_fight 94,98-106
    $BPY -m tools.hello_door_night_raised render dn19_beside,dn19_beside 1217,1249 [--res 270x480 --samples 8]
Stills go to out/test/check_hello_door_night_raised_<shot>_<frame>.png. Prefix with `nice -n 5 timeout 290`.
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

DOOR_FRONT = dict(pos=(4.0, -11.2, 0.75), target=(10.0, -7.2, 1.9), lens=40.0, fstop=4.0)
BESIDE = dict(pos=(4.8, -4.05, 1.9), target=(9.9, -8.03, 1.5), pos1=(6.31, -2.39, 1.9), target1=(9.3, -6.45, 1.5))


def main(argv):
    """See the module docstring."""
    import bpy  # noqa: F401  (mathutils for hello_common)
    from films import hello_common as HC
    HC.CAMS["door_front"] = dict(DOOR_FRONT)
    beside = dict(HC.CAMS["beside"])
    beside.update(BESIDE)
    HC.CAMS["beside"] = beside
    if argv[0] == "probe":
        from tools import hello_door_night_probe
        return hello_door_night_probe.main(argv[1:3])
    from tools import hello_shots
    rest = argv[3:] or ["--res", "270x480", "--samples", "8"]
    return hello_shots.main(["render", "--shots", argv[1], "--frame", argv[2], "--threads", "2",
                             "--name", "check_hello_door_night_raised"] + rest)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
