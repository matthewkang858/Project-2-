"""Six Seconds, sequence BRIDGE: the second bastion, in another world. The boot shot again, the brute blocking the
bridge, the pillar: beats 11, 12, 13, 14, 15 (shots br11_boots, br12_blocks, br13_pillar, br14_zero, br15_wait), sky
"soul" (soul_sand_valley: the fog and the void of this world are TEAL; the lead's choice, films/sixseconds.py
SKIES). One function per shot; the contract is in films/sixseconds_common.py (tags "br...", C.actor, C.item, C.rest,
C.cam, C.rack, C.lights, C.pillar, st.use / st.hero).

STATUS: SHOT by the bridge director (Nov 26) from the lead's stubs, then FIXED after the review (Nov 26: br11's
boots light and focus drift, br13's perch, the runner's look down, the brute's cheated look in br13 / br14, #2 thrown
in br14, br15's camera). Each shot's docstring has its NOW and MEASURED lines; the stills are out/test/br_<shot>_
<frame>[_zones].png (540x960, 16 samples), the palette checks out/test/sixseconds_pal_<shot>_<frame>.png, the motion
out/test/sixseconds_bridge_motion.mp4 (668-998 at 24 fps, 270x480, 9 samples: br13-br15 every frame, br11 and br12
at step 2 with each frame held twice).
THE SEQUENCE NOW
  br11  THE BOOT FRAMING (shared camera, unchanged): out of black the empty bridge comes INTO focus (the focus pulls
        from the boot mark to the far pillars in 24 frames, sharp on "different", then drifts on to the second pillar
        pair until the legs come in: the shared camera's handheld is a pixel, so the focus is the picture's life);
        the legs sprint in from the left on "bastion" with the focus racking to the mark, the boots stop by 714 and
        hold (the game's idle) to the cut, lit by their own fill "br_boots" (as bright as pt05's)
  br12  over the runner's shoulder (soft, his head glancing), a slow push down the bridge to the brute blocking it
        under his lantern, dead still (ears only), his face sharp throughout; his own film-local key "br_key"
  br13  the pillar tableau side-on from the east over the lava: the runner crouched on the netherrack pillar's north-
        east corner (EDGE13), looking steeply down at the brute below, who looks up at him (cheated 28 degrees to
        the lens); the runner drops gold on "threw": it falls broad side past the brute's snout on "gold" and lands
        at his feet on "at"
  br14  the brute side-on against the teal void, head up (the same cheated look); the runner, off screen, drops the
        second ingot: it falls into the frame, past his snout on "at" and lands on "it"; the third (tossed up, out of
        frame) drops in behind his head and lands on "seconds"; his head never moves (ears only)
  br15  above and behind the runner on the pillar: the back of his head and shoulders the big shape at the upper
        right, crouch-spamming from the first frame, the pillar's face dropping from his boots to the deck; below
        him the brute's face turned up into the lens, dead still, the three ingots at his feet; the runner's head
        snaps left and right on "he can't" and comes back to the brute before the cut
TOOLS: tools/sixseconds_bridge_probe.py (the bridge director's own: "ingots": the thrown ingots' throw / landing
  frames, rest points against the shared spots, their clearance of the pillar and of the brute's head and body;
  "fly": each ingot's place in the frame and its angle to the lens, frame by frame; "clip": every vertex of each
  ingot's sprite against every box of the brute at quarter frames; "gap": br15's screen gap between the runner's
  silhouette and the brute's head).

THE PLACE (engine/nether.py BRIDGE, origin (400, 0, 0); out/test/nether_map_bridge.png): a deck 5 wide (walkway
x 399..401 of polished blackstone bricks, low broken brick walls on the edges, no edge wall at y 16..21 beside the
pillar nor at x 402, y 3..5, the boot camera's spot), y -8..44, between pairs of basalt pillars (y 2, 15, 28, 41)
with gold caps, rising from the lava sea 24 below (a lit lava glow: seen from deck level only over the edge, from
the pillar's height and side-on: br13, br15); ONE lantern on chains over bridge_brute (group bridge_lantern), four
under the deck's edges (bridge_under). Anchors: bridge_boot_mark (400.5, 6.5), bridge_player (400.5, 10.6) facing
north, bridge_brute (400.5, 16.5) facing south, bridge_pillar_foot (400.5, 18.25), bridge_pillar_top (400.5, 19.5, 3)
facing south, bridge_pillar_top_target (his head); this film's six_pillar_brute (401.0, 18.25) facing north (THE
BRUTE'S PLACE AT THE PILLAR in br13, br14 and br15) and six_bridge_ingot_1..3 = six_pillar_brute + (0.75, -0.1),
(0.6, -0.4), (0.45, -0.65) (films/sixseconds_set.py PILLAR_BRUTE_SHIFT, PILLAR_INGOTS); path bridge_run_in.
THE NETHERRACK PILLAR (C.bas.pillar: three Breakables at (400, 19, 0..2)) stands only where C.pillar(s) says: br13,
br14, br15; br11, br12 and the flash sequence's fl16_bridge have none.
SHARED (films/sixseconds_common.py): CAMS["bridge_boot"] for br11 with BOOT_FRAME: THE BOOT FRAMING of pt05 (home)
  repeated on this set: 50 mm f/2, 3.8 blocks from the boots, the boots in the same place at the same size (x
  27-71 %, y 42-59 %: measured on both sets); its FOCUS is free (the stub holds it far, then racks). Keep the skid ON
  bridge_boot_mark. PLACES "bridge_boot_mark", "bridge_player", "bridge_brute", "pillar_brute" (the same in all three
  pillar shots, with the ingots at six_bridge_ingot_k: move them together or not at all), "pillar_top".
THE LEAD'S REVIEW PASS, what changed here and why (each measured; the stills are named in the shots):
  * br11: the runner stopped only on 726-728 of the old timeline, after "same boots", and the empty bridge was a dark
    blur (f/2 focused 3.8 blocks off). Now he sprints from behind the lens from 683, enters the frame's left edge on
    "bastion" (699), the boots stop by about 716 and hold to the cut; the focus holds the pillars far, racks to the
    boots as his legs come in.
  * br13-br15: the brute stood on pillar_foot in br13 / br14 and 0.5 east of it in br15 (the pillar cut his face from
    bridge_top), standing ON one of the br14 ingots across the cut, and every ingot lay behind his body or in the
    caption band from br15's camera (the story check). Now: one place for all three (six_pillar_brute, the br15
    one), the ingots on his east side (seen from the east cameras of br13 / br14 and from br15's), br15's camera
    aimed 1.5 block lower (BR15_CAM).
  * the runner's hand is set on the first frame of every shot (pickaxe in br11 / br12, gold in br13 / br15).
THE WORLD'S RULES that bite here: the runner wears the golden boots; the brute keeps the golden axe, never raised
  here (he waits); the pillar only where C.pillar allows; the ingots he ignores are dropped items (C.item / C.rest)
  lying or landing on explicit floor points; nothing from an engine call that is not registered (ENGINE SIDE DOORS).
  The bridge director keeps every SHARED camera and place: bridge_boot (focus only), bridge_boot_mark, pillar_brute
  and the three ingot spots (each thrown ingot comes to REST on its spot, to the millimetre). pillar_top is NOT the
  runner's place any more (only this sequence used it): he crouches at the pillar top's north-east corner, EDGE13 in
  br13 and EDGE in br15 (see EDGE). bridge_player / bridge_brute (br12) unchanged.
TAGS TAKEN: runner_br (br11, br12, br13, br15), brute_br (br12-br15), gold_ingot_br_ingot1..3 (br13-br15: one entity
  each from its throw to the end of br15); fills br_boots (br11 only), br_key (br12 only).
PREVIEW samples of this sequence: 9.
"""
import math

from mathutils import Vector

from engine import piglins

# br11: the runner sprints in from behind the lens (at speed, unseen: the lens is at y 2.9) on RUN_FROM, so that the
# bridge is EMPTY for a beat out of black, his legs enter from the frame's left on "bastion" and the boots stop on the
# mark before "same boots" (the story check: the first stub stopped them only on 726-728, after the words)
BR11_RUN_FROM = (400.5, 0.0, 0.0)
BR11_RUN_START = 681
# br11's focus: out of black it opens on the empty boot mark (where the boots will stop) and pulls out to the far
# bridge (the pillars, the lantern over bridge_brute) in BR11_OPEN frames: the new world comes into focus, and the
# picture moves from its first frame (the shared camera's handheld, 0.004, is a pixel); then held far, and racked
# back to the boots as the legs come in (the shared camera's focus is free)
BR11_NEAR = (400.5, 6.5, 0.2)
BR11_FAR = (400.5, 15.0, 1.6)
BR11_OPEN = 24                 # the first pillar pair sharp on 692 ("different" 691); 14 left 682-698 frozen
# then the focus drifts on to the second pillar pair (y 28) until the legs come in on "bastion": the empty bridge
# never holds still (the shared camera's handheld is a pixel)
BR11_FAR2 = (400.5, 28.5, 1.8)
BR11_RACK = 10
# br11: the boots' own fill (film-local, shadowless, this shot only), low beside the mark: "same boots" as bright as
# pt05's (gold 0.264 -> 0.343 mean luminance on the boots, pt05 0.336; the reviewer's measure)
BR11_BOOTS = dict(pos=(401.3, 5.0, 0.8), watts=40.0)

# br12: over the runner's shoulder (engine/nether.py bridge_shoulder) with a slow push down the bridge
BR12_CAM = dict(pos=(401.15, 8.7, 1.95), target=(400.5, 16.5, 1.35), lens=50.0, fstop=2.6,
                pos1=(401.1, 9.1, 1.93), handheld=0.006)
BR12_LANTERN = 1.0             # the brute's lantern (group bridge_lantern) in br12
# br12: the brute's own key (film-local, shadowless, this shot only): in front of him and above his eyes, so that
# under the teal fill of this sky he separates from the blackstone (nether.check_still: 1.5 x)
BR12_KEY = dict(pos=(400.55, 15.2, 2.4), watts=120.0)

# THE PILLAR (br13-br15): the runner crouches on the netherrack pillar's top block (x 400..401, y 19..20, top z 3)
# at its NORTH-EAST corner, sneaking (the game holds a sneaking player on an edge while his box overlaps the block:
# here 0.1 over the east face), looking down at the brute 1.5-1.7 block south of him. Not pillar_top (the middle of
# the top): from there the game's drop (look x 0.3 + 0.1 up) toward the brute's ingot spots fell onto the pillar's own
# top or through his head. tools/sixseconds_bridge_probe ingots (the gap from the item's centre to the brute's head
# boxes on every tick of the flight, his head cheated as below): #1 (from EDGE13) 0.41, #2 (from EDGE) 0.27; a dropped
# ingot's opaque half-width is 0.22, so the exact test is the sprite's own vertices against his boxes (probe
# clip): #1 clears everything by 0.08; #2's north edge passes 0.06 into the BACK of his right arm for 2 frames
# (909-911), behind the arm's outer face from br14's lens; spot 3 lies right behind his head from anywhere on the
# pillar (the best direct drop of 182 positions scanned passes 0.13 from it), so #3 is a lob (0.03 into the tip of his
# right ear for half a frame, 928). EDGE: br15's place, and where #2 and #3 are thrown from.
EDGE = (401.1, 19.8, 3.0)
# br13's perch: the same corner 0.25 further south, so that the golden boots stand OVER the top (their box ends at y
# 19.97; from EDGE only 13 % of their footprint was over the netherrack and, side-on from the east, the boot hung past
# the pillar's edge below its top line: he read as floating beside the corner). The rest of the x overhang lies along
# br13's lens axis. br15 keeps EDGE (from its lens, EDGE13 put his head against the brute's)
EDGE13 = (401.1, 19.55, 3.0)
CROUCH_EYE = 1.27              # a crouching player's eye height (the game's crouching pose: 1.27)
# br13 / br14: the brute's look CHEATED this many degrees toward the east lenses (CONTRACT, "After four finished
# films": a face in strict profile that looks beyond itself shows the lens a blank cheek). His look target is the
# runner's eyes turned about his own eye: the same pitch (up 40), the head turned 28 toward the lens: an eye, the
# snout and a tusk read. The runner is off screen in br14 and above him in br13, so it never reads as a missed look
CHEAT_DEG = 28.0
# THE GOLD HE THROWS: three ingots, ONE entity each from the throw to the end of br15, coming to rest exactly on the
# shared spots six_bridge_ingot_1..3. Each is the game's drop (Player.drop: look x 0.3 + 0.1 up, the jitter left
# out) with the look solved so that it rests on its spot: #1 dropped on "threw" (br13: past his snout on "gold",
# down on "at"); #2 dropped off screen as br14 starts (899), into br14's frame from the top on 905, past his snout on
# "at" (909-910), down on "it" (913; until the review it was dropped on br13's "me" and passed his snout on br14's
# first two frames, before the eye had found him); #3 tossed up (a lob, out of frame) on 900, falling into br14's
# frame behind his head, down on "seconds"
INGOT_SPOTS = ("six_bridge_ingot_1", "six_bridge_ingot_2", "six_bridge_ingot_3")
INGOT_LOBS = (False, False, True)
# where the runner stands when he throws each one: #1 on screen in br13 (EDGE13); #2 and #3 off screen in br14 from
# EDGE, where br15 finds him (a sneaking shuffle of 0.25 in the 34 frames between; from EDGE13 #2 passed 0.18 from his
# cheated head instead of 0.27, and its centre ran inside his right arm's box)
INGOT_FROM = (EDGE13, EDGE, EDGE)
# which shot's lens each one faces broad side, and when (frames from touching the deck: in the fall past his snout)
INGOT_FACE = (("br13_pillar", -6), ("br14_zero", -3), ("br14_zero", -5))
# br13: side-on from the east over the void (engine/nether.py bridge_pillar pulled back 1.2 and re-aimed: the whole
# tableau inside y 14-60 %), 28 mm, a slow drift north
BR13_CAM = dict(pos=(410.2, 18.7, 2.2), target=(400.5, 18.9, 1.0), lens=28.0, fstop=4.0, pos1=(410.1, 18.95, 2.2),
                handheld=0.008)
# br14: the brute side-on from the east (engine/nether.py bridge_profile, 0.5 further back and aimed 0.2 lower: his
# head and the ingots inside y 14-60 %), his head against the teal void; a slow drift north. His look is cheated 28
# toward this lens (CHEAT_DEG: 57 -> 53 degrees off his nose; strict profile, 82-86, showed a blank cheek and ear).
# A three-quarter view by moving the CAMERA (50-62 degrees) was rendered (out/test/brvar2_br14_zero_900_v0 / _v1.png):
# it put a basalt pillar behind his pitched-up head; the cheat keeps the teal void behind it
BR14_CAM = dict(pos=(406.3, 18.3, 1.35), target=(400.5, 18.25, 0.2), lens=35.0, fstop=2.4, pos1=(406.3, 18.7, 1.35),
                handheld=0.006)
# br15: above and behind the runner on the pillar (engine/nether.py bridge_top re-placed: 1.8 above his eyes, 1.4
# behind him and 2.2 east), looking down along the pillar's height at the brute: the back of his head and his
# shoulders the big shape at the upper right, the netherrack pillar's face dropping from his boots to the deck, the
# brute's upturned face below-left of him (34 degrees off the lens), the three ingots at his feet; a slow push down
# the line of sight (0.3, ease_out). The review's two cameras: the first pass's (2.4 above his head, 24 mm) flattened
# the pillar into its top face (two figures side by side, the face 65-69 px, the ingots edge-on slivers) and let the
# runner's head cover the brute's ear on "he can't"; (402.8, 21.3, 6.3) at 26 mm fixed the height and the face but
# laid the runner's arm over the brute's right ear in every standing frame of the spam (113-155 px overlap, probe
# gap). 0.5 further east and aimed 0.3 to the right: a gap of 31-48 px between the runner's whole silhouette and
# the brute's head on every frame 953-998
BR15_CAM = dict(pos=(403.3, 21.2, 6.3), target=(400.7, 18.55, 0.5), lens=26.0, fstop=3.0,
                pos1=(403.187, 21.085, 6.047), handheld=0.006)
CAMS_BY_SHOT = {"br13_pillar": BR13_CAM, "br14_zero": BR14_CAM, "br15_wait": BR15_CAM}
# br15: the crouch spam (Player.sneak on / off: the game snaps the pose), frames between toggles, repeated
SPAM = (3, 4, 3, 3, 4)
# br15: the head snaps on "he can't": degrees left (+) / right (-) of his line to the brute, each held a few frames
SNAPS = ((42, 5), (-40, 5), (35, 4), (-44, 5), (0, 6))


def _runner_eyes(edge=EDGE):
    """The crouched runner's eyes on the pillar's edge (EDGE: br15; EDGE13: br13, br14)."""
    return Vector((edge[0], edge[1], edge[2] + CROUCH_EYE))


def _cheat(eye, deg=CHEAT_DEG, edge=EDGE13):
    """The brute's look target in br13 / br14: the runner's eyes at `edge` turned `deg` degrees in yaw about the
    brute's eye `eye`, toward +X (the east lenses' side), at the same pitch."""
    d = _runner_eyes(edge) - eye
    a = math.atan2(d.y, d.x) - math.radians(deg)
    flat = math.hypot(d.x, d.y)
    return eye + Vector((math.cos(a) * flat, math.sin(a) * flat, d.z))


def _look_down(runner, brute, frame, edge):
    """The crouched runner's head pitched down at the brute's eyes PAST the engine's 35-degree limit
    (characters.HEAD_PITCH_MAX; a player in the game looks up to 90 down): after look_at, before any arm swing (the
    swing reads the head's pitch). Returns the pitch in degrees."""
    d = Vector(brute.eye_point(frame)) - _runner_eyes(edge)
    down = math.atan2(-d.z, math.hypot(d.x, d.y))
    runner.head.rotation_euler[0] = down             # the rig's head x rotation: + = down
    runner.head.keyframe_insert("rotation_euler", index=0, frame=frame)
    return math.degrees(down)


def _drop_toward(C, origin, target, lob=False):
    """The game's drop of an item by a player (Player.drop / LivingEntity.createItemStackToDrop: look x 0.3, plus
    0.1 up; the jitter left out) from `origin` (his eyes - 0.3), with the look pitch solved by bisection so that the
    item entity (piglins.item_track: gravity 0.04, drag 0.98, the deck's blocks) comes to REST at `target`: looking
    down at it, or (lob=True) looking up, so that it arcs over whatever stands between. Returns (velocity per tick,
    track [(tick, (x, y, z))], pitch in radians)."""
    o, t = Vector(origin), Vector(target)
    flat = Vector((t.x - o.x, t.y - o.y))
    dist = flat.length
    u = flat / dist

    def toss(pitch):
        v = (u.x * piglins.PLAYER_DROP_SPEED * math.cos(pitch), u.y * piglins.PLAYER_DROP_SPEED * math.cos(pitch),
             piglins.PLAYER_DROP_SPEED * math.sin(pitch) + piglins.PLAYER_DROP_UP)
        track = piglins.item_track(o, v, world=C.bas)
        end = Vector(track[-1][1])
        return Vector((end.x - o.x, end.y - o.y)).dot(u), v, track

    # looking down, a steeper look falls shorter; looking up past the longest throw, a steeper look falls shorter too
    lo, hi = (0.8, 1.5) if lob else (-1.55, 0.6)
    for _ in range(40):
        mid = 0.5 * (lo + hi)
        got, v, track = toss(mid)
        if (got < dist) != lob:
            lo = mid
        else:
            hi = mid
    return v, track, mid


def _landing(track):
    """The first tick on which a thrown item touches the floor it comes to rest on."""
    rest_z = track[-1][1][2]
    for tick, p in track:
        if p[2] <= rest_z + 1e-3:
            return tick
    return track[-1][0]


def _ingots(C):
    """THE GOLD HE THROWS (br13, br14, br15): three item entities, keyed once (the first pillar shot to ask), each
    lying on its shared spot six_bridge_ingot_k from its landing to the end of br15 (st.use per shot). Returns
    [dict(item, throw, land, still, spot, track)] in throw order; C.memo["br_ingots"]."""
    got = C.memo.get("br_ingots")
    if got is not None:
        return got
    last = C.T["br15_wait"].frame_end
    out = []
    for k, (spot, lob, edge) in enumerate(zip(INGOT_SPOTS, INGOT_LOBS, INGOT_FROM), 1):
        origin = Vector((edge[0], edge[1], edge[2] + CROUCH_EYE - piglins.THROW_BELOW_EYE))
        v, track, pitch = _drop_toward(C, origin, C.P(spot), lob=lob)
        land = _landing(track) * piglins.TICK
        if k == 1:
            throw = C.T["br13_pillar"].at("threw") - 2       # the swing's top on "threw", the ingot away
        elif k == 2:
            throw = int(round(C.T["br14_zero"].at("it") - land))   # out of frame; past his snout on "at", down on "it"
        else:
            throw = int(round(C.T["br14_zero"].at("seconds") - land))   # out of frame; lands on "seconds"
        it = C.item("gold_ingot", "br_ingot%d" % k)
        still = piglins.launch(it, throw, origin, v, world=C.bas)
        # its spin phased so that it falls BROAD SIDE to the lens that sees it fall (edge-on, the stub's phase, it
        # was a sliver a pixel wide in br13's preview)
        lens, mid = INGOT_FACE[k - 1]
        it.animate(throw, last + 1, phase=C.broadside(it, CAMS_BY_SHOT[lens]["pos"], throw + land + mid))
        out.append(dict(item=it, throw=throw, land=throw + land, still=still, spot=spot, track=track, pitch=pitch))
    C.memo["br_ingots"] = out
    return out


def _crouch_spam(runner, f0, f1):
    """The game's crouch spam: the sneak key tapped, the pose snapping down and up every SPAM frames, from f0 (down)
    to 3 frames before the cut (left down)."""
    on, f, i = True, f0, 0
    while f < f1 - 3:
        runner.sneak(f, on)
        f += SPAM[i % len(SPAM)]
        on = not on
        i += 1
    if on and f <= f1:                                # the last toggle stood him up: down again for the end
        runner.sneak(f, True)


def _head_snaps(runner, brute, f0, f1):
    """Impatience: the head snapping left and right of his line to the brute (SNAPS: degrees, frames held) from f0,
    each turn in 2 frames (a mouse flick), back on the brute by f1."""
    f = f0
    for deg, hold in SNAPS:
        if f + 2 + hold > f1 - 2:                     # no time left for another look away: back on the brute
            deg = 0
        eye = runner.eye_point(f)
        d = Vector(brute.pos_at(f)) - eye
        a = math.atan2(d.y, d.x) + math.radians(deg)
        flat = math.hypot(d.x, d.y)
        tgt = eye + Vector((math.cos(a) * flat, math.sin(a) * flat, d.z))
        runner.look_at(f, tgt if deg else brute, ease=2)
        f += 2 + hold
        if not deg:
            break


def br11_boots(st, s, C, nar):
    """BEAT 11  "New world, different bastion, same boots."   frames 668-740 (73 f, 3.04 s), sky soul. OUT OF BLACK:
    the frames before 668 are the reset's black ("ended" held on it); the picture comes up in silence, 9 frames before
    the first word. Words: New 677, world 682, different 691, bastion 699, same 714, boots 721 (ends 732).

    STORY: Out of black, the boot shot again on a different set: a long blackstone bridge between basalt pillars over
    an orange lava glow, empty for one beat. Then the same legs sprint in and skid to a stop, golden boots mid-frame,
    exactly as before.
    Location: second bastion bridge, another world. Cast: the player (legs and boots). Effects: cut up from black,
    blackstone bridge, basalt pillars, gilded blackstone, lava glow far below, golden boots, skid stop, boot shot
    framing matched to sentence five.

    MUST BE SEEN, ON WHICH WORD
      668 .. 698      the EMPTY bridge: the teal void, basalt pillars with gold caps, sharp (focus far), already moving
                      (the handheld drift at least) under "New world, different"
      "bastion" 699   the legs sprint in from the frame's LEFT edge (from behind the lens: he passes 1.15 west of it)
      by about 716    the skid done: the boots stopped on bridge_boot_mark where BOOT_FRAME says (as in pt05), and
                      held to the cut (about 25 frames: pt05 holds them 22) under "same boots" (714-732)
    SHARED: CAMS["bridge_boot"] exactly (its focus is free), BOOT_FRAME; PLACES "bridge_boot_mark".
    KNOWN (the set builder): THE LAVA CANNOT BE SEEN from deck level here (24 below, under the deck's edge): "over an
      orange lava glow" is shown by br13 and br15.
    NOW: CAMS["bridge_boot"] exactly (position, aim, lens, f/2, handheld 0.004 and seed: the shared boot framing);
      only its focus is this shot's. 668: the picture comes up out of black focused on the empty boot mark (the near
      deck sharp, the bridge soft) and the focus PULLS OUT to the far pillars (BR11_FAR, 15 blocks) over 24 frames:
      the new world comes into focus under "New world, different", sharp on 692, the first frame already moving (the
      shared handheld is a pixel); then it drifts on to the second pillar pair (BR11_FAR2, y 28.5) until the legs come
      in on 699: the empty bridge never holds still (the review: with the 14-frame pull, 682-698 was a still picture).
      The runner waits behind the lens at BR11_RUN_FROM (400.5, 0.0) and sprints
      from 681 (BR11_RUN_START: at speed, ramp out = the game's skid) to bridge_boot_mark, passing 1.15 west of the
      lens; the focus racks to the mark over 10 frames from "bastion" (699) as his legs come in from the frame's left
      (feet in frame from 703, body from about 697); the feet stop on 714 ("same"), the boots held in BOOT_FRAME to
      the cut with the game's idle (weight shift, arm bob: the hips move the boots by a pixel). Iron pickaxe in his
      hand. The boots' own fill BR11_BOOTS "br_boots" (film-local, shadowless, 40 W, low beside the mark, this shot
      only): "same boots" as bright as pt05's. Hero: the boots (C.boots_of).
    MEASURED (bridge director; tools.sixseconds_geo --sky soul br11_boots:714 / :725 / :740 --boots runner_br --track
      runner_br:695-716; stills out/test/br_br11_boots_668 / _682 / _705 / _725[_zones].png at 540x960, 16 samples
      (all with the fix pass's focus and boots light); motion out/test/sixseconds_bridge_motion.mp4, step 2 here):
      feet x -58 % on 699, enter the frame on 703 (x 8 %), on the mark (6.49 of 6.50) on 714; the boots' box x
      23.4-71.3 % on 714 (the trailing leg still swinging down), x 27.7-69.8 %, y 42.7-58.5 % on 725 and the same on
      740: inside BOOT_FRAME (x 27-71, y 42-59), as pt05's (x 27.7-70.1 %, y 43.1-58.9 % on its 318). 668: a soft
      teal-and-stone picture, the deck at the mark nearest to sharp; 682: the pull half way, the basalt pillars with
      their gold caps coming sharp against the teal void; 705: his leg entering soft at the left, the gold boot
      catching the light; 725: the boots sharp mid-frame, the shirt and trousers above, his hands at the frame's
      edges. THE BOOTS' GOLD (mean luminance of the gold pixels inside BOOT_FRAME, hue 30-62, s > 0.4): 0.334 on 725
      with br_boots (0.264 without it, the review's measure), pt05's 318: 0.332; the frame 0.139 (pt05 0.159), the
      deck below the boots 0.102 (pt05 0.107). Palette 725 (out/test/sixseconds_pal_br11_boots_725.png): shirt hue
      174, pants min channel 22, the boots 100 % inside the safe area (x 28-69 %, y 43-56 %): all pass.
      His back is to the lens here (he runs north, toward br12's brute); in pt05 he faces it (he came from the
      gateway): each is right for its neighbours.
    NEIGHBOURS: before, pt10_smoke (black from "ended"); after, br12_blocks.
    """
    f0, f1 = s.frame_start, s.frame_end
    runner = C.actor("runner", "br")
    mark = C.P("bridge_boot_mark")
    a = BR11_RUN_FROM
    C.put(runner, f0, a, toward=mark)
    runner.hold("iron_pickaxe", frame=f0)
    stop = runner.walk(BR11_RUN_START, [a, mark], sprint=True, ramp=(False, True))
    runner.idle(stop + 1, f1 + 1)                     # the boots held: the game's weight shift and arm bob
    st.use(s, runner)
    C.cam(s, "bridge_boot", focus=Vector(BR11_NEAR))
    C.rack(s, Vector(BR11_FAR), f0, BR11_OPEN)        # out of black: the new world comes into focus
    legs = C.at(s, "bastion")
    C.rack(s, Vector(BR11_FAR2), f0 + BR11_OPEN, legs - f0 - BR11_OPEN)   # and drifts on down the bridge
    C.rack(s, Vector(mark) + Vector((0.0, 0.0, 0.2)), legs, BR11_RACK)   # as the legs come in
    st.hero(s, "boots", *C.boots_of(runner))
    C.lights(s, "bridge")
    C.fill("br_boots", BR11_BOOTS["pos"], BR11_BOOTS["watts"], [s])


def br12_blocks(st, s, C, nar):
    """BEAT 12  "Every world has a bastion, and every bastion has me."   frames 741-834 (94 f, 3.92 s), sky soul.
    Words: Every 743, world 750, has 759, a 764, bastion 765, and 790, every 794, bastion 801, has 816, me 822
    (ends 827).

    STORY: Over the player's shoulder, third person: his back and shoulder fill the near edge of the frame. Down the
    bridge the brute stands square in the middle of it, blocking it, axe at his side, perfectly still, already facing
    him, under his own lantern.
    Cast: piglin brute, the player (back, foreground). Effects: golden axe, bridge with lava glow below, lantern on a
    chain as the brute's key light.

    MUST BE SEEN, ON WHICH WORD
      frame 741       the runner's back and shoulder at the near edge (soft), the brute down the bridge, still
      "has me" 816-827   the brute's face sharp under his lantern (focus on him from the start, or a rack to him on
                      "every bastion" 794)
    NOW: BR12_CAM = engine/nether.py's bridge_shoulder (50 mm f/2.6, over the runner's right shoulder at
      bridge_player, 1.95 high) with a slow push of 0.4 block down the bridge (ease_out: at speed on 741, settling by
      the cut) and a 0.006 handheld. The runner at bridge_player facing north, his head on the brute's face, alive
      (Player.idle: weight shift, glances): a soft dark head and teal shoulder at the lower left. The brute at
      bridge_brute under his lantern, facing him, his head on the runner's face from the first frame, DEAD STILL (no
      idle: the ears only), the golden axe low at his side. Focus on the brute's head the whole shot (sharp on "has
      me"). Light: the set's lanterns (bridge) and the brute's own key BR12_KEY "br_key" (film-local, shadowless,
      120 W, 1.3 block in front of him and 0.6 above his eyes, this shot only). Hero: the brute.
    MEASURED (bridge director; geo br12_blocks:741 / :834; stills out/test/br_br12_blocks_820[_zones].png (with
      br_key) and _745 (before it); palette out/test/sixseconds_pal_br12_blocks_820.png; motion, step 2): the brute's
      eyes x 49.8 %, y 42.3 % on 741 and x 50.1 %, y 41.8 % on 834, head x 33-66 % (ears), y 38-48 %, face 107 -> 112
      px, 5 degrees off the lens (he looks straight at the runner, just beside the lens); the runner's head at the
      lower left edge (x -57..23 %, y 44-84 %), soft. His legs are in the caption band (the caption sits on his
      trousers; his face and belt are above it). Palette 820 WITHOUT the key: x 1.40 the blackstone (43 vs 30: FAIL,
      the push and the framing showed more of his dark tunic than the lead's 1.52); WITH br_key: x 2.03 (68 vs 33),
      gold hue 48 (s 0.64), shirt hue 174, the brute 100 % inside the safe area (x 40-60 %, y 38-47 %): every check
      passes. The lantern hangs at the top edge (y 0-17 %).
    NEIGHBOURS: before, br11_boots; after, br13_pillar.
    """
    f0, f1 = s.frame_start, s.frame_end
    runner = C.actor("runner", "br")
    brute = C.actor("brute", "br")
    C.put(brute, f0, "bridge_brute")
    C.put(runner, f0, "bridge_player")
    runner.hold("iron_pickaxe", frame=f0)
    runner.look_at(f0, Vector(C.P("bridge_player_look")), ease=0)
    runner.idle(f0, f1 + 1)                           # soft at the near edge: the weight shift, glances
    brute.look_at(f0, Vector(C.P("bridge_brute_look")), ease=0)
    brute.flop_ears(f0, f1 + 1)                       # perfectly still: the ears only
    st.use(s, runner, brute)
    C.cam(s, None, focus=brute.head, **BR12_CAM)
    st.hero(s, "brute", brute)
    C.lights(s, "bridge", groups={"bridge_lantern": BR12_LANTERN})
    C.fill("br_key", BR12_KEY["pos"], BR12_KEY["watts"], [s])


def br13_pillar(st, s, C, nar):
    """BEAT 13  "He hid on a pillar and threw gold at me."   frames 835-897 (63 f, 2.62 s), sky soul.
    Words: He 837, hid 840, on 844, a 847, pillar 849, and 864, threw 867, gold 874, at 883, me 886 (ends 892).

    STORY: Tall static composition made for the vertical frame, all of it between 14 and 60 percent of the height:
    the player crouches on top of a three-block netherrack pillar at the top of that zone. Directly below, the brute
    stands at its foot looking straight up. The player tosses a gold ingot and it drops the whole height of the
    pillar, past the brute's snout.
    Cast: the player (crouched on the pillar), piglin brute. Effects: three-block netherrack pillar, crouch pose, gold
    ingot tossed down (long fall), brute head pitched up, golden axe.

    MUST BE SEEN, ON WHICH WORD
      frame 835       the pillar with the runner crouched on top, the brute at its foot looking up
      "threw gold" 867-883   the toss (Player.throw or swing_arm + piglins.throw_item / launch to
                      six_bridge_ingot_1: the ingot that lies there in br14) and the ingot's fall past the brute's
                      snout, inside y 14-60 %
    SHARED: PLACES "pillar_brute" (the brute's place in all three pillar shots), "pillar_top", six_bridge_ingot_1..3.
    RISK (story): "a face pitched straight up is the underside of a snout from most angles, and the tall tableau
      makes both figures small. Fallback: keep the brute in strict side profile for 13 and 14 and shorten the pillar
      to two blocks in frame by cropping its base behind him." (a piglin's pitch stops at 40 degrees)
    NOW: BR13_CAM: engine/nether.py's bridge_pillar pulled back to 9.2 blocks east over the void, 28 mm f/4, aimed
      at z 1.0, a slow drift north (0.25 block) and a 0.008 handheld: the whole tableau inside y 14-60 %, the lava sea
      at the bottom edge, his lantern at the left. C.pillar(s). The runner crouched (sneaking) at EDGE13, the pillar
      top's north-east corner 0.25 south of EDGE (his golden boots over the top, not over the air), gold in his hand,
      his head pitched 62 degrees DOWN onto the brute's eyes (_look_down: past the engine's 35-degree limit; the game's
      player looks down to 90, and the drops leave at 56-62 down); the brute at pillar_brute (shared), facing north,
      his head up at the runner's eyes (the game's 40 degrees) CHEATED 28 degrees toward this lens (_cheat), DEAD
      STILL (ears only). THE GOLD (_ingots): the runner drops #1 on 865 (his arm swing's top on "threw" 867): the
      game's drop, broad side to this lens as it falls; past the brute's snout on "gold" (873-875), on the deck at
      six_bridge_ingot_1 on 878, still on 886. "threw gold at me" is that one throw: #2 and #3 are dropped off screen
      in br14 (no match on action at the cut any more). Hero: the brute.
    MEASURED (bridge director; geo br13_pillar:835 / :873 / :897 --boots runner_br; probe tools.sixseconds_bridge_probe
      ingots / fly br13_pillar:863-897; motion out/test/sixseconds_bridge_motion.mp4, every frame; still
      out/test/br_br13_pillar_873[_zones].png: the ingot broad side beside his snout, the boot standing on the pillar
      top's corner): the runner's head x 52-62 %, y 19.3-26.3 %, 43 px, pitch -62; his boots x 61-67 %, y 31-35 %; the
      brute's head x 31-46 %, y 41-48 %, 51 px, 53-55 degrees off the lens (the cheat: 82 before), pitched up 40; the
      three ingot spots y 58-60 %: the tableau spans y 19-60 %. Ingot #1 in flight x 60 -> 40 %, y 23 -> 58 %, 1-13
      degrees off broad side, its centre 0.41 from the brute's head boxes at its nearest (874.6), clear of the pillar;
      its sprite's vertices clear his whole body by 0.08 (probe clip: every vertex against every box of his, at
      quarter frames). #2 and #3 stay hidden in his hand through the shot (probe). Faces are small (51 / 43 px at 540
      wide): it is the wide of the three. Palette 873 (out/test/sixseconds_pal_br13_pillar_873.png): brute x 2.45 the
      blackstone (54 vs 22), 100 % in the safe area (x 33-44 %, y 42-47 %): all pass.
    NEIGHBOURS: before, br12_blocks; after, br14_zero.
    """
    f0, f1 = s.frame_start, s.frame_end
    C.pillar(s)
    runner = C.actor("runner", "br")
    brute = C.actor("brute", "br")
    C.put(runner, f0, EDGE13, toward="pillar_brute")
    C.put(brute, f0, "pillar_brute")
    runner.hold("gold_ingot", frame=f0)
    runner.sneak(f0)
    runner.look_at(f0, brute, ease=0)                 # down at the brute (the engine's head stops at 35 ...)
    _look_down(runner, brute, f0, EDGE13)             # ... the game's does not: on his eyes, before the swing
    brute.look_at(f0, _cheat(Vector(brute.eye_point(f0))), ease=0)   # up at him (40), cheated 28 to the lens
    brute.flop_ears(f0, f1 + 1)
    ingots = _ingots(C)
    for g in ingots:
        if f0 <= g["throw"] <= f1:
            runner.attack(g["throw"])                 # the drop's arm swing
        st.use(s, g["item"])
    st.use(s, runner, brute)
    C.cam(s, None, focus=brute.head, **BR13_CAM)
    st.hero(s, "brute", brute)
    C.lights(s, "bridge")


def br14_zero(st, s, C, nar):
    """BEAT 14  "I looked at it for zero seconds."   frames 898-952 (55 f, 2.29 s), sky soul.
    Words: I 900, looked 904, at 910, it 913, for 917, zero 921, seconds 931 (ends 944).

    STORY: Side-on medium on the brute in clean profile, head tilted up at the pillar top, feet no lower than 60
    percent of the frame height. The ingot falls past his snout and lands spinning at his feet. A second lands beside
    it. His head never dips.
    Cast: piglin brute. Effects: two gold ingots landing and spinning, golden axe, foot of the netherrack pillar at
    frame edge.

    MUST BE SEEN, ON WHICH WORD
      frame 898       the first ingot falling past his snout (in the air on the first frame: launched before the
                      shot, or the one of br13 continuing: a new item entity per shot)
      "it" 913        it lands spinning at his feet (six_bridge_ingot_1); "zero" 921 the second lands beside it
                      (six_bridge_ingot_2); his head NEVER dips (no idle glances: ears only)
    SHARED: PLACES "pillar_brute", six_bridge_ingot_1..3 (br15 shows all three where br14 leaves two).
    NOW: BR14_CAM: engine/nether.py's bridge_profile 0.5 further back (5.3 blocks east of him) and aimed 0.2 lower,
      35 mm f/2.4, a slow drift north (0.4 block) and a 0.006 handheld; his head against the teal void, the pillar's
      foot at the right edge. C.pillar(s). The brute at pillar_brute, his head up at the runner's eyes (40, the game's
      limit) CHEATED 28 degrees toward this lens (_cheat, as in br13: 57 -> 53 degrees off his nose instead of the
      strict profile's 86 -> 82, which showed the lens a blank cheek and ear), DEAD STILL (no idle: ears only) from
      the first frame to the last. THE GOLD (_ingots, one entity each since its throw): #1 lies at six_bridge_ingot_1
      (landed in br13); the runner, off screen above (back at EDGE, where br15 finds him), drops #2 on 899: it falls
      into the frame from the top on 905, past his snout on "at" (909-910), broad side to this lens (0-8 degrees off),
      and lands at six_bridge_ingot_2 on "it" (913.4), the only thing moving in the picture then (#3 is out of frame
      until 925); he tosses #3 up on 900 (the game's drop with the look 70 degrees UP, the only clean way onto spot 3,
      which lies behind his head from the pillar): it drops into the frame from the top on 925, past the back of his
      head on 927-928, landing at six_bridge_ingot_3 on 931 ("seconds"). Hero: the brute.
    MEASURED (bridge director; geo br14_zero:898 / :913 / :952; probe ingots, clip and fly br14_zero:898-934;
      motion, every frame; stills out/test/br_br14_zero_909 / _931[_zones].png: #2 a gold streak across his snout;
      three ingots down): his eyes x 49.9 -> 48.6 %, y 22.3 %, head x 29-62 %, y 15.8-31 %, 114 px, 57 -> 53 degrees
      off the lens, pitched up 40 (an eye, the ear, the side of the snout and a tusk read; the reviewer's 40-degree
      variant showed both eyes); his feet y 55 %; the ingots at rest x 33-46 %, y 51-54 %: everything inside y 14-60 %.
      #2: hidden in his hand to 898, in frame from 905 (y -2 % -> 5 % on 906), beside his snout 909 (x 59 %, y 27 %),
      down 913 (x 42 %, y 54 %); its centre 0.27 from his head boxes at its nearest (908.6; 0.16 before the cheat and
      the retime); its sprite's north edge 0.06 into the BACK of his right arm's box on 909.25-911.5 (the arm's outer
      face is between it and this lens: it reads as passing behind the arm's edge; the shipped version had the same
      0.064 at 898-900). #3: in frame from 925, centre 0.06 from his head boxes on 927.6 (lens side), its sprite 0.025
      into the tip of his right ear's box on 927.75-928.25 (half a frame, falling at 0.5 block a frame); 0-9 degrees
      off broad side. Tried and not used: a three-quarter view by moving the camera (50-62 degrees off;
      out/test/brvar2_br14_zero_900_v0 / _v1.png): a basalt pillar behind his pitched-up head. Palette 913
      (out/test/sixseconds_pal_br14_zero_913.png): brute x 2.69 the blackstone (47 vs 17), 100 % in the safe area
      (x 30-59 %, y 17-31 %): all pass.
    NEIGHBOURS: before, br13_pillar; after, br15_wait.
    """
    f0, f1 = s.frame_start, s.frame_end
    brute = C.actor("brute", "br")
    C.pillar(s)
    C.put(brute, f0, "pillar_brute")
    brute.look_at(f0, _cheat(Vector(brute.eye_point(f0))), ease=0)   # as br13: up 40, cheated 28 to the lens
    brute.flop_ears(f0, f1 + 1)                       # his head never dips: the ears only
    st.use(s, brute)
    for g in _ingots(C):
        st.use(s, g["item"])
    C.cam(s, None, focus=brute.head, **BR14_CAM)
    st.hero(s, "brute", brute)
    C.lights(s, "bridge")


def br15_wait(st, s, C, nar):
    """BEAT 15  "I can wait, and he can't."   frames 953-998 (46 f, 1.92 s), sky soul.
    Words: I 955, can 958, wait 963, and 972, he 975, can't 978 (ends 990); the flash cuts start on 999, 10 frames
    before "I ended".

    STORY: High angle from just behind the player on the pillar top, third person: his back and head are the big
    foreground shape in the lower part of the frame, sneak-bobbing up and down and snapping left and right. Above his
    shoulder, far below on the bridge, the brute's upturned face, perfectly still, three ingots turning ignored at
    his feet. Slow push down toward the brute.
    Cast: the player (back, sneak-bobbing), piglin brute. Effects: sneak-bob (crouch spam) animation, head snaps left
    and right, three gold ingots spinning on the bridge, slow push in.

    MUST BE SEEN, ON WHICH WORD
      frame 953       the runner already sneak-bobbing (Player.sneak on / off every 3-4 frames: the game's crouch
                      spam), the push already moving
      "I can wait" 955-972   the brute's upturned face perfectly still (no idle), three ingots at his feet
      "he can't" 975-990     the runner's head snapping left and right (look_at with ease 0..2)
    SHARED: PLACES "pillar_brute", six_bridge_ingot_1..3.
    NOW: BR15_CAM: above and behind the runner (1.8 above his eyes, 1.4 behind him, 2.2 east), 26 mm f/3, looking down
      along the pillar's height at the brute (aim 0.5 above the deck, 0.3 north-west of him), a slow push of 0.3 down
      the line of sight (ease_out: at speed on 953) and a 0.006 handheld. C.pillar(s). The runner crouched at EDGE,
      gold in his hand, CROUCH-SPAMMING from the first frame (_crouch_spam: Player.sneak off / on every 3-4 frames,
      the game's snap; down from 993 to the cut), his head on the brute; on "he can't" (975) his head SNAPS left and
      right of his line to the brute (_head_snaps: 42 / -40 / 35 degrees, each turn 2 frames, held 4-5) and is back
      on the brute from 994. The brute at pillar_brute, his face turned up at the runner (not cheated here: this lens
      is on the runner's side), 34 degrees off the lens: DEAD STILL (ears only). The three ingots lying at his feet,
      the same entities as in br14 (turning). Hero: the brute.
    MEASURED (bridge director; geo br15_wait:953 / :963 / :977 / :984 / :998 --pts the spots; probe gap (each
      mesh box of the runner, armour and held ingot included, projected and filled, against the brute's head with
      its ears) on every frame 953-998; motion out/test/sixseconds_bridge_motion.mp4 (953-998, every frame); stills
      out/test/br_br15_wait_963 / _980[_zones].png): the brute's eyes x 40.6 -> 40.0 %, y 41.3 -> 40.8 %, head x
      27-49 %, y 35.5-46 %, face 75 -> 79 px, never blocked, 34 degrees off the lens (his upturned face reads: eyes,
      snout, tusks, the gold belt); the ingot spots x 28-31 %, y 51-56 %, none hidden by a body (one ingot partly over
      the next); the runner: the back of his head and his shoulders at the upper right (head x 54.5-96 %, y 2-32 %,
      126 degrees off the lens at rest, 84 / 165 during the snaps), his golden boots on the pillar's top and the
      netherrack face dropping from them to the deck below: the height reads. Between the runner's whole silhouette
      and the brute's head: 31-48 px on every frame (the first pass's camera: 10-16 px, and his head over the brute's
      ear on 977; the review's (402.8, 21.3, 6.3): his arm over the brute's right ear, 113-155 px of overlap, in every
      standing frame). COST: in the standing frames of the spam the top of his head reaches y 2-6 % (under the top
      icons; the back of a head, not a face; 20-25 % of his silhouette above y 14 %), and 14-26 % of it is beyond x
      82 %. The story's "his head in the lower part of the frame" is not met: from a lens that puts it below the
      brute's (straight above him, z 7+) his head hides the brute (geo: blocked by runner_br_head from (401.1, 20.8,
      7.0)). Lava in the bottom-left and top corners, outside the safe area. Palette 963
      (out/test/sixseconds_pal_br15_wait_963.png): brute x 2.70 the blackstone (50 vs 18), shirt hue 172, pants min
      channel 21, the brute 100 % inside the safe area (x 30-48 %, y 36-45 %): all pass.
    NEIGHBOURS: before, br14_zero; after, fl16_bridge (the flash cut in this world: the brute, a puff, the boots).
    """
    f0, f1 = s.frame_start, s.frame_end
    C.pillar(s)
    runner = C.actor("runner", "br")
    brute = C.actor("brute", "br")
    C.put(runner, f0, EDGE, toward="pillar_brute")
    C.put(brute, f0, "pillar_brute")
    runner.hold("gold_ingot", frame=f0)
    runner.look_at(f0, brute, ease=0)
    _crouch_spam(runner, f0, f1)
    _head_snaps(runner, brute, C.at(s, "he"), f1 - 4)
    brute.look_at(f0, _runner_eyes(), ease=0)         # perfectly still: the ears only
    brute.flop_ears(f0, f1 + 1)
    for g in _ingots(C):
        st.use(s, g["item"])
    st.use(s, runner, brute)
    C.cam(s, None, focus=brute.head, **BR15_CAM)
    st.hero(s, "brute", brute)
    C.lights(s, "bridge")
