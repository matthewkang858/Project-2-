"""The Nitwit: a 13 s vertical short at golden hour (role DIRECTOR / ANIMATOR).

    "Everyone here has a job. I don't. He never trades with me. He never locked me in a box.
     I'm the only one still free."

    $BPY -m render nitwit --sheet 12                                  # contact sheet with captions
    $BPY -m render nitwit --still 8.7 --zones --captioned             # one frame, with the Reels zones
    $BPY -m render nitwit --frames all --max-seconds 240              # FINAL frames (resumable)

The timeline is planned from the captions outward: captions.autotime gives every word its time, the cuts sit where
a sentence's first word starts (so the pause after a sentence is the last breath of its picture and no word
straddles a cut), and every action that a word names is keyed from that word's frame (Plan.word).

    shot       words                          picture
    villager   Everyone here has              the farmer walks past the big house's wall (reference 2)
    smith      a job.                         the weaponsmith at his grindstone, the forge behind him
    nitwit     I don't.                       the nitwit alone at the village edge; his head sinks on "don't"
    trade      He never trades with me.       Steve holds an emerald out to the farmer; on "me" the focus pulls to
                                              the nitwit, who has been watching from the wheat behind them
    hall       He never locked me in a box.   the trading hall: the camera rides along the counter and ends on the
                                              nearest caged face on "box"
    meadow     I'm the only one still free.   the nitwit walks out the exit road into the meadow, toward the sun;
                                              the camera lets him go and comes to rest

The set-ups (camera, lens, light, staging) are the reviewed ones of films/lookdev.py; this file adds the timing,
the animation and the camera moves. Stage, yaw_to and up are imported from there, never copied.
"""
import math

from engine import captions, look, props, shots, village
from films.lookdev import Stage, up, yaw_to

FPS = 24
TITLE = "The Nitwit"
SCRIPT = ("Everyone here has a job. I don't. He never trades with me. He never locked me in a box. "
          "I'm the only one still free.")
# 9 frames a word, 12 more at the end of a sentence; every cut is a multiple of 3 frames. The last word ends at
# 12.125 s and the film holds 0.875 s more on the last picture: 13.0 s = 312 frames.
TIMING = dict(start=0.25, per_word=0.375, comma=0.125, period=0.5)
HOLD = 0.875
SKY = dict(preset="golden", az=62.0, el=27.0)              # the sky of the golden look-dev film: one sun for all shots
LAVA_GLOW = 1.0                                            # emission of the forge's lava in this film (the set has 3.0)


class Plan:
    """The captions and what follows from them: where the cuts are and on which frame each word appears."""

    def __init__(self):
        self.caps = captions.autotime(SCRIPT, **TIMING)
        tokens = SCRIPT.split()
        assert len(tokens) == len(self.caps)
        self.words = [w.lower() for w, _, _ in self.caps]
        self.sentences = [0] + [i + 1 for i, t in enumerate(tokens[:-1]) if t.endswith((".", "!", "?"))]
        self.end = self.cut_time(self.caps[-1][2] + HOLD)

    @staticmethod
    def cut_time(t):
        """The first frame boundary at or after t seconds (a cut there never splits the word that starts at t)."""
        return math.ceil(t * FPS - 1e-6) / FPS

    def start(self, index):
        """Film time at which caption word number `index` appears, on the frame grid."""
        return self.cut_time(self.caps[index][1])

    def index(self, word, nth=0):
        """Caption index of the nth occurrence of `word`."""
        hits = [i for i, w in enumerate(self.words) if w == word.lower()]
        return hits[nth]

    def frame(self, word, nth=0):
        """Frame number on which the nth occurrence of `word` appears."""
        return int(round(self.start(self.index(word, nth)) * FPS)) + 1


# ----------------------------------------------------------------------------------------------------
# "Everyone here has" / "a job."
# ----------------------------------------------------------------------------------------------------

def shot_villager(st, s, plan):
    """The farmer on his way along the north wall of the big house, in full sun: medium shot from ahead of him,
    the camera walking with him (look-dev set-up 'villager', reference 2). Half way he glances at the fields."""
    v, A = st.v, st.v.anchors
    f0 = s.frame_start
    farmer = st.actor("ada", "farmer")
    a, b = (2.6, 22.95, 0.0), (9.6, 22.95, 0.0)
    # The camera rides 2 blocks ahead of him at y = 26, and there are grass tufts in that row at x = 5.5 and 8.5: one
    # block from the lens either of them covers him. So he strolls (1.3 blocks a second, the step length is the same)
    # and the pre-roll is chosen so that the camera stays between them, x 6.7 to 8.1, for the whole shot. (He is new
    # to the film, so he may start before it; 33 frames have him in full stride at the cut.)
    farmer.place(f0 - 33, a, yaw_to(a, b))
    farmer.walk(f0 - 33, [a, b], speed=1.3)
    here = farmer.pos_at(f0 + 20)
    farmer.look_at(f0 + 8, (here.x + 4.0, here.y + 1.6, 1.5), ease=12)      # 20 degrees to his left, and held
    st.use(s, farmer)
    s.lens(42, 2.8)
    s.follow(farmer.root, (2.3, 3.0, 0.80), (2.0, 3.15, 0.80), look_offset=(-0.08, 0.0, 1.16))
    s.focus(farmer.head)
    s.handheld(0.012, seed=11)
    st.hero(s, "farmer", farmer)
    st.lights(s, scale=1.0, near=A["exit_gate"], radius=10.0)


def shot_smith(st, s, plan):
    """The weaponsmith at his grindstone under the forge roof: seen from the steps in front of the porch, a little
    below his eyes, the grindstone big and soft in the foreground, the forge wall and the lava's glow behind him.
    He is bent over the stone and works it: the folded arms jolt, the head dips with each stroke."""
    v, A = st.v, st.v.anchors
    f0, f1 = s.frame_start, s.frame_end
    smith = st.actor("sam", "weaponsmith")
    spot, stone = A["smithy_work"], A["smithy_station"]
    smith.place(f0 - 12, spot, v.yaws["smithy_work"])
    smith.look_at(f0 - 12, (stone[0], stone[1] - 0.9, stone[2] + 0.3), ease=0)   # eyes on the far rim of the stone
    for f in (f0 - 6, f0 + 6, f0 + 18):                      # a stroke every half second, one across the cut
        smith.swing_arm(f)
    st.use(s, smith)
    s.lens(40, 2.8)
    s.move((19.57, 3.50, 2.05), (18.52, 6.5, 2.30), (19.36, 3.92, 2.09))      # a slow push, half a block
    s.focus(smith.head)
    s.handheld(0.01, seed=41)
    st.hero(s, "smith", smith)
    # The forge's lava is an emissive surface and lit the whole porch a saturated orange (cobblestone G/R 0.89, under
    # the 0.92 of tools/palette_check): the look keeps block light pale so that textures stay on the game's palette,
    # and the torches follow that rule. So the lava still glows for the camera but no longer lights diffuse surfaces
    # (it is seen in no other shot); the pale torch on the house wall, east of the porch, is the warm key instead.
    for ob in v.objects:
        if "lava" in ob.name:
            for mat in ob.data.materials:
                for node in mat.node_tree.nodes:
                    if node.type == "BSDF_PRINCIPLED":
                        node.inputs["Emission Strength"].default_value = LAVA_GLOW
    st.lights(s, scale=1.0, groups={"smithy": 1.6}, near=spot, radius=14.0)


# ----------------------------------------------------------------------------------------------------
# "I don't."
# ----------------------------------------------------------------------------------------------------

def shot_nitwit(st, s, plan):
    """The nitwit alone at the village edge, sharp; a librarian and a mason busy with each other, out of focus
    behind him (look-dev set-up 'nitwit'). He is looking over at the village; on "don't" his head sinks."""
    v, A = st.v, st.v.anchors
    f0, f1 = s.frame_start, s.frame_end
    nit = st.actor("nitwit", "nitwit")
    spot = A["nitwit_idle"]
    cam = (6.3, 34.2, 1.5)
    yaw = yaw_to(spot, (cam[0] + 2.4, cam[1], 0))
    nit.place(f0, spot, yaw)
    nit.look_at(f0, (cam[0] + 3.6, cam[1], 1.3), ease=0)
    nit.idle(f0, f1 + 1, seed=4)
    fd = plan.frame("don't")
    ahead = (spot[0] + 3.0 * math.sin(yaw), spot[1] - 3.0 * math.cos(yaw), 0.45)
    nit.look_at(fd + 1, ahead, ease=11)                      # ... down at the grass in front of his feet, and held
    bo, cy = st.actor("bo", "librarian"), st.actor("cy", "mason")
    pb, pc = (12.02, 25.13, 0.0), (13.04, 26.92, 0.0)        # about 5 blocks behind him, either side of his head
    bo.place(f0, pb, yaw_to(pb, pc))
    cy.place(f0, pc, yaw_to(pc, pb))
    bo.idle(f0, f1 + 1, seed=8)
    cy.nod(f0 + 4)
    bo.nod(f0 + 17)
    st.use(s, nit, bo, cy)
    s.lens(66, 2.6)
    s.move(cam, up(spot, 1.34), (cam[0] + 0.25, cam[1] + 0.1, cam[2]))
    s.focus(nit.head)
    s.handheld(0.01, seed=13)
    st.hero(s, "nitwit", nit)
    st.lights(s, scale=1.0, near=spot, radius=14.0)          # (daylight: far torches only cost render time)


# ----------------------------------------------------------------------------------------------------
# "He never trades with me."
# ----------------------------------------------------------------------------------------------------

def shot_trade(st, s, plan):
    """Steve holds an emerald out to the farmer, who stands in his wheat beside his composter; over Steve's shoulder
    (look-dev set-up 'trade'). The arm comes up with the emerald, the farmer looks at it and nods. The camera slides
    to the right all the while, which brings the nitwit out from behind the farmer's head: he stands on the path
    through the wheat and watches. On "me" the focus pulls to him and he looks down."""
    v, A = st.v, st.v.anchors
    f0, f1 = s.frame_start, s.frame_end
    farmer = st.actor("ada", "farmer")
    steve = st.actor("steve", "steve")
    nit = st.actor("nitwit", "nitwit")
    if steve.held is None:
        steve.hold(props.make_item("emerald", v.collection))
    fpos = A["farm_work"]
    spos = (fpos[0] + 1.0, fpos[1], 1.0)                     # on the farm's log frame, east of the farmer
    npos = (-16.5, -9.2, 1.0)                                # on the log path between the two fields, 6 blocks behind
    steve.place(f0, spos, yaw_to(spos, fpos))
    farmer.place(f0, fpos, yaw_to(fpos, spos))               # (everybody is placed before anybody looks at anybody)
    nit.place(f0, npos, yaw_to(npos, spos))                  # (he was in the previous shot: nothing keyed before f0)
    steve.look_at(f0, farmer, ease=0)
    steve.idle(f0, f1 + 1, seed=2)
    steve.raise_arm(f0 + 1, angle=55, ease=9)                # the hand comes up and stops between them, at his chest
    farmer.look_at(f0, steve, ease=0)
    farmer.idle(f0, f1 + 1, seed=6)
    # (the farmer keeps his eyes on Steve: a nod, or a look down at the emerald, and a camera at his eye height
    # sees nothing of him but the straw hat)
    farmer.swing_arm(plan.frame("trades") + 2)               # the little jolt of a villager who takes the offer
    nit.look_at(f0, steve, ease=0)
    f_me = plan.frame("me", 0)
    nit.look_at(f_me + 7, (npos[0] + 2.2, npos[1] + 1.6, 1.3), ease=11)     # nobody holds anything out to him
    st.use(s, farmer, steve, nit)
    s.lens(50, 3.4)
    right = (-0.662, 0.749)                                  # the camera's right, in the ground plane
    cam0, aim0 = (-8.50, -2.90, 2.56), (-11.25, -5.33, 2.16)
    k, p = 0.50, 0.15                                        # half a block to the right and 0.2 down: the farmer's
    cam1 = (cam0[0] + k * right[0], cam0[1] + k * right[1], cam0[2] - 0.20)   # hat brim rises clear of the nitwit
    aim1 = (aim0[0] + p * right[0], aim0[1] + p * right[1], aim0[2])
    s.move(cam0, aim0, cam1, aim1)
    s.focus(farmer.head)
    s.focus(nit.head, at_s=plan.start(plan.index("me", 0)) - 0.125, rack_s=0.4)
    s.handheld(0.01, seed=17)
    st.hero(s, "emerald", steve.held)
    st.hero(s, "farmer", farmer)
    st.hero(s, "nitwit", nit)
    st.lights(s, scale=1.0, near=fpos, radius=20.0)


# ----------------------------------------------------------------------------------------------------
# "He never locked me in a box."
# ----------------------------------------------------------------------------------------------------

def shot_hall(st, s, plan):
    """The trading hall: villagers shut in a row of 1x1 cells behind their job blocks (look-dev set-up 'hall'). The
    camera rides east along the counter, a hand from the cell fronts at their eye height, 25 degrees off the row,
    and arrives 2.65 blocks short of the toolsmith as "box" comes up: his face a third of the frame, clear in
    its window. Every head follows the camera."""
    v, A = st.v, st.v.anchors
    f0, f1 = s.frame_start, s.frame_end
    first = 3                                                  # the nearest of the faces: cell 3 (the toolsmith)
    near = A["cell_%d" % first]
    front = near[1] + 1.30                                     # y of the cell fronts (the villagers stand 1.3 behind)
    cam0 = (near[0] - 4.15, front + 0.26, 1.62)                # one and a half blocks back: passing cell 2
    cam1 = (near[0] - 2.65, front + 0.26, 1.62)                # where the look-dev still was taken
    s.lens(38, 3.4)
    aim = (3.62, -1.70, 1.47 - 1.62)                           # 25 degrees off the row, just below eye height
    s.move(cam0, tuple(c + d for c, d in zip(cam0, aim)), cam1, tuple(c + d for c, d in zip(cam1, aim)),
           ease="ease_out")
    cells = []
    for i, prof in enumerate(v.cell_professions, 1):
        c = st.actor("cell%d" % i, prof, level=3)
        c.place(f0, A["cell_%d" % i], v.yaws["cell_%d" % i])
        c.look_at(f0, cam0, ease=0)                          # they all watch whoever walks down the aisle ...
        c.idle(f0, f1 + 1, seed=20 + i)                      # (breathing arms, weight shifts)
        c.track(f0, f1 + 1, s.camera, step=6, ease=6)        # ... and their heads follow him
        cells.append(c)
    st.use(s, *cells)
    s.focus(cells[first - 1].head)
    s.handheld(0.006, seed=19)
    for i in (first - 1, first):
        st.hero(s, "cell %d" % (i + 1), cells[i])
    st.lights(s, scale=0.0, groups={"hall": 0.8}, inside="hall")


# ----------------------------------------------------------------------------------------------------
# "I'm the only one still free."
# ----------------------------------------------------------------------------------------------------

def shot_meadow(st, s, plan):
    """The nitwit walks out the exit road into the open meadow, toward the sun (look-dev set-up 'meadow'). The camera
    walks low behind him on his left, then slows and lets him go: it has stopped as the film ends and he is still
    walking. He looks out over the meadow as he goes (his profile against the sky) and up at the sky on "free"."""
    v, A = st.v, st.v.anchors
    f0, f1 = s.frame_start, s.frame_end
    nit = st.actor("nitwit", "nitwit")
    road = [(0.5, 25.5, -0.06), (0.6, 31.0, -0.06), (0.4, 38.0, -0.06), (0.5, 46.0, 0.0)]
    nit.place(f0 - 40, road[0], yaw_to(road[0], road[1]))    # (he is not in the hall shot: the pre-roll is hidden)
    nit.walk(f0 - 40, road)
    here = nit.pos_at(f0)
    nit.look_at(f0 - 1, (here.x - 5.0, here.y + 1.2, 1.2), ease=0)          # over the meadow to his left, eyes level
    f_free = plan.frame("free")
    there = nit.pos_at(f_free + 6)
    nit.look_at(f_free - 8, (there.x - 6.0, there.y + 0.9, 4.2), ease=14)   # ... and up, at the open sky; held
    st.use(s, nit)
    s.lens(28, 3.2)
    # on the plant-free verge west of the road (village.CAMERA_LANE). The offset grows as time squared by 0.8 x the
    # shot's length x his speed: the camera starts at his pace and is standing still on the last frame.
    back = 0.5 * 1.6 * (s.end_s - s.start_s)
    # (aimed a quarter block lower than the look-dev still: he stands 5 % higher in the frame and the caption lies
    # across his legs and his shadow, not across the green robe)
    s.follow(nit.root, (-2.62, -3.12, 0.78), (-2.95, -3.12 - back, 0.72), look_offset=(0.50, 0.30, 1.52),
             ease="ease_in")
    s.focus(nit.head)
    s.handheld(0.012, seed=23)
    st.hero(s, "nitwit", nit)
    st.lights(s, scale=1.0, near=A["exit_gate"], radius=14.0)


SHOTS = (
    # name, builder, index of the caption word the shot starts on
    ("villager", shot_villager, "everyone"),
    ("smith", shot_smith, "a"),
    ("nitwit", shot_nitwit, "i"),
    ("trade", shot_trade, "he"),
    ("hall", shot_hall, ("he", 1)),
    ("meadow", shot_meadow, "i'm"),
)


def build(scene):
    """Build "The Nitwit" into `scene`; returns what render.py expects (plus the Stage, for the checks)."""
    plan = Plan()
    v = village.build_village(scene, seed=1)
    sky = look.set_time(scene, SKY["preset"], sun_azimuth=SKY["az"], sun_elevation=SKY["el"])
    look.setup_compositor(scene, bloom=1.0, grade="warm")
    film = shots.Film(scene, fps=FPS)
    st = Stage(scene, film, v, sky)
    starts = []
    for name, _fn, word in SHOTS:
        word, nth = word if isinstance(word, tuple) else (word, 0)
        i = plan.index(word, nth)
        assert i in plan.sentences or name == "smith", "the cut to '%s' is not at the start of a sentence" % name
        starts.append(plan.start(i))
    starts[0] = 0.0
    ends = starts[1:] + [plan.end]
    for (name, fn, _word), t0, t1 in zip(SHOTS, starts, ends):
        fn(st, st.shot(name, t1 - t0), plan)
    st.finish()
    return {"film": film, "captions": plan.caps, "stage": st, "title": TITLE}
