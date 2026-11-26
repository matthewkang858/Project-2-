"""Six Seconds, sequence BRIDGE: the second bastion, in another world. The boot shot again, the brute blocking the
bridge, the pillar: beats 11, 12, 13, 14, 15 (shots br11_boots, br12_blocks, br13_pillar, br14_zero, br15_wait), sky
"soul" (soul_sand_valley: the fog and the void of this world are TEAL; the lead's choice, films/sixseconds.py
SKIES). One function per shot; the contract is in films/sixseconds_common.py (tags "br...", C.actor, C.item, C.rest,
C.cam, C.rack, C.lights, C.pillar, st.use / st.hero).

STATUS: SHOT by the bridge director (Nov 26) from the lead's stubs. Each shot's docstring has its NOW and MEASURED
lines; the stills are out/test/br_<shot>_<frame>[_zones].png (540x960, 16 samples), the palette checks out/test/
sixseconds_pal_<shot>_<frame>.png, the motion out/test/sixseconds_bridge_motion.mp4 (668-998 at 24 fps, 270x480,
9 samples: br13-br15 every frame, br11 and br12 at step 2 with each frame held twice).
THE SEQUENCE NOW
  br11  THE BOOT FRAMING (shared camera, unchanged): out of black the empty bridge comes INTO focus (the focus pulls
        from the boot mark to the far pillars in 14 frames: the shared camera's handheld is a pixel, so the pull is
        the first frame's life), held on the far pillars under "New world, different"; the legs sprint in from
        the left on "bastion" with the focus racking to the mark, the boots stop by 714 and hold (the game's idle)
        to the cut
  br12  over the runner's shoulder (soft, his head glancing), a slow push down the bridge to the brute blocking it
        under his lantern, dead still (ears only), his face sharp throughout; his own film-local key "br_key"
  br13  the pillar tableau side-on from the east over the lava: the runner crouched on the netherrack pillar's north-
        east corner, the brute below looking up at him; the runner drops gold on "threw" (it falls broad side
        past the brute's snout on "gold" and lands at his feet on "at"), and a second on "me" that is still falling
        at the cut
  br14  the brute in profile against the teal void, head up: the second ingot falls past his snout from the first
        frame and lands on "I"; the third (tossed up, out of frame) drops in behind his head and lands on "seconds";
        his head never moves (ears only)
  br15  high above and behind the runner: his head and back the big shape at the lower right, crouch-spamming from
        the first frame; below him the brute's face turned up into the lens, dead still, the three ingots beside him;
        the runner's head snaps left and right on "he can't" and comes back to the brute before the cut
TOOLS: tools/sixseconds_bridge_probe.py (the bridge director's own: the thrown ingots' throw / landing frames, rest
  points against the shared spots, their clearance of the pillar and of the brute's head and body; each ingot's place
  in the frame and its angle to the lens, frame by frame).

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
  runner's place any more (only this sequence used it): he crouches at EDGE, the pillar top's north-east corner (see
  EDGE). bridge_player / bridge_brute (br12) unchanged.
TAGS TAKEN: runner_br (br11, br12, br13, br15), brute_br (br12-br15), gold_ingot_br_ingot1..3 (br13-br15: one entity
  each from its throw to the end of br15); fill br_key (br12 only).
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
BR11_OPEN = 14
BR11_RACK = 10

# br12: over the runner's shoulder (engine/nether.py bridge_shoulder) with a slow push down the bridge
BR12_CAM = dict(pos=(401.15, 8.7, 1.95), target=(400.5, 16.5, 1.35), lens=50.0, fstop=2.6,
                pos1=(401.1, 9.1, 1.93), handheld=0.006)
BR12_LANTERN = 1.0             # the brute's lantern (group bridge_lantern) in br12
# br12: the brute's own key (film-local, shadowless, this shot only): in front of him and above his eyes, so that
# under the teal fill of this sky he separates from the blackstone (nether.check_still: 1.5 x)
BR12_KEY = dict(pos=(400.55, 15.2, 2.4), watts=120.0)

# THE PILLAR (br13-br15): the runner crouches on the netherrack pillar's top block (x 400..401, y 19..20, top z 3)
# at its NORTH-EAST corner, sneaking (the game holds a sneaking player on an edge while his box overlaps the block:
# here 0.1 over the east face), looking down at the brute 1.7 block south of him. Not pillar_top (the middle of the
# top): from there the game's drop (look x 0.3 + 0.1 up) toward the brute's ingot spots fell onto the pillar's own
# top or through his head. From this corner (tools/sixseconds_bridge_probe ingots, the gap from the item's centre to
# the brute's head boxes on every tick of the flight): #1 0.39, #2 0.18 (a dropped ingot's opaque half-width is
# 0.22: it grazes his snout for a frame at the cut, falling at 0.4 block a frame); spot 3 lies right behind his head
# from anywhere on the pillar (the best direct drop of 182 positions scanned passes 0.13 from it), so #3 is a lob.
EDGE = (401.1, 19.8, 3.0)
CROUCH_EYE = 1.27              # a crouching player's eye height (the game's crouching pose: 1.27)
# THE GOLD HE THROWS: three ingots, ONE entity each from the throw to the end of br15, coming to rest exactly on the
# shared spots six_bridge_ingot_1..3. Each is the game's drop (Player.drop: look x 0.3 + 0.1 up, the jitter left
# out) with the look solved so that it rests on its spot: #1 dropped on "threw" (br13: past his snout on "gold",
# down on "at"), #2 on "me" (br13: in the air over the cut, past his snout on br14's first frames, down on "I"),
# #3 tossed up (a lob, out of frame) as br14 starts, falling into br14's frame behind his head, down on "seconds"
INGOT_SPOTS = ("six_bridge_ingot_1", "six_bridge_ingot_2", "six_bridge_ingot_3")
INGOT_LOBS = (False, False, True)
# which shot's lens each one faces broad side, and when (frames from touching the deck: in the fall past his snout)
INGOT_FACE = (("br13_pillar", -6), ("br14_zero", -3), ("br14_zero", -5))
# br13: side-on from the east over the void (engine/nether.py bridge_pillar pulled back 1.2 and re-aimed: the whole
# tableau inside y 14-60 %), 28 mm, a slow drift north
BR13_CAM = dict(pos=(410.2, 18.7, 2.2), target=(400.5, 18.9, 1.0), lens=28.0, fstop=4.0, pos1=(410.1, 18.95, 2.2),
                handheld=0.008)
# br14: the brute in profile from the east (engine/nether.py bridge_profile, 0.5 further back and aimed 0.2 lower:
# his head and the ingots inside y 14-60 %), his head against the teal void; a slow drift north (86 -> 82 degrees
# off his nose). A three-quarter view (50-62 degrees) was rendered (out/test/brvar2_br14_zero_900_v0 / _v1.png): his
# pitched-up head then shows the underside of the snout against a basalt pillar; the profile reads better
BR14_CAM = dict(pos=(406.3, 18.3, 1.35), target=(400.5, 18.25, 0.2), lens=35.0, fstop=2.4, pos1=(406.3, 18.7, 1.35),
                handheld=0.006)
# br15: high above and behind the runner on the pillar, looking steeply down past his left shoulder (engine/nether.py
# bridge_top re-placed: 2.4 above his head, 0.9 behind him and 1.15 east): his head and back the big shape at the
# right, the brute's face below him turned up INTO the lens (23 degrees off), the three ingots beside him; a slow
# push down. 1.15 east, not 0.75: from 0.75 his head, rising out of each crouch, covered the brute's right cheek
# (the first preview, 956-959)
BR15_CAM = dict(pos=(402.25, 20.7, 7.35), target=(400.9, 18.6, 0.1), lens=24.0, fstop=3.0, pos1=(402.2, 20.5, 7.0),
                handheld=0.006)
CAMS_BY_SHOT = {"br13_pillar": BR13_CAM, "br14_zero": BR14_CAM, "br15_wait": BR15_CAM}
# br15: the crouch spam (Player.sneak on / off: the game snaps the pose), frames between toggles, repeated
SPAM = (3, 4, 3, 3, 4)
# br15: the head snaps on "he can't": degrees left (+) / right (-) of his line to the brute, each held a few frames
SNAPS = ((42, 5), (-40, 5), (35, 4), (-44, 5), (0, 6))


def _runner_eyes():
    """The crouched runner's eyes on the pillar's edge: what the brute stares at in br13-br15."""
    return Vector((EDGE[0], EDGE[1], EDGE[2] + CROUCH_EYE))


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
    origin = Vector((EDGE[0], EDGE[1], EDGE[2] + CROUCH_EYE - piglins.THROW_BELOW_EYE))
    out = []
    for k, (spot, lob) in enumerate(zip(INGOT_SPOTS, INGOT_LOBS), 1):
        v, track, pitch = _drop_toward(C, origin, C.P(spot), lob=lob)
        land = _landing(track) * piglins.TICK
        if k == 1:
            throw = C.T["br13_pillar"].at("threw") - 2       # the swing's top on "threw", the ingot away
        elif k == 2:
            throw = C.T["br13_pillar"].at("me") + 2          # in the air over the cut into br14
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
      deck sharp, the bridge soft) and the focus PULLS OUT to the far pillars (BR11_FAR, 15 blocks) over 14 frames:
      the new world comes into focus by 682 ("world"), the first frame already moving (the shared handheld is a
      pixel). Held far under "different". The runner waits behind the lens at BR11_RUN_FROM (400.5, 0.0) and sprints
      from 681 (BR11_RUN_START: at speed, ramp out = the game's skid) to bridge_boot_mark, passing 1.15 west of the
      lens; the focus racks to the mark over 10 frames from "bastion" (699) as his legs come in from the frame's left
      (feet in frame from 703, body from about 697); the feet stop on 714 ("same"), the boots held in BOOT_FRAME to
      the cut with the game's idle (weight shift, arm bob: the hips move the boots by a pixel). Iron pickaxe in his
      hand. Hero: the boots (C.boots_of).
    MEASURED (bridge director; tools.sixseconds_geo --sky soul br11_boots:714 / :725 / :740 --boots runner_br --track
      runner_br:695-716; stills out/test/br_br11_boots_682 / _705 / _725[_zones].png at 540x960, 16 samples, and
      _668 (rendered before the run moved 2 frames earlier: on 668 he is behind the lens either way); motion
      out/test/sixseconds_bridge_motion.mp4, step 2 here):
      feet x -58 % on 699, enter the frame on 703 (x 8 %), on the mark (6.49 of 6.50) on 714; the boots' box x
      23.4-71.3 % on 714 (the trailing leg still swinging down), x 27.7-69.8 %, y 42.7-58.5 % on 725 and the same on
      740: inside BOOT_FRAME (x 27-71, y 42-59), as pt05's (x 27.7-70.1 %, y 43.1-58.9 % on its 318). 668: a soft
      teal-and-stone picture; 682: the basalt pillars with their gold caps sharp against the teal void; 705: his leg
      entering soft at the left, the gold boot catching the light; 725: the boots sharp mid-frame, the shirt and
      trousers above, his hands at the frame's edges. Palette 725 (out/test/sixseconds_pal_br11_boots_725.png): shirt
      hue 171, pants min channel 14, the boots 100 % inside the safe area (x 28-69 %, y 43-56 %): all pass.
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
    C.rack(s, Vector(mark) + Vector((0.0, 0.0, 0.2)), C.at(s, "bastion"), BR11_RACK)   # as the legs come in
    st.hero(s, "boots", *C.boots_of(runner))
    C.lights(s, "bridge")


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
      at the bottom edge, his lantern at the left. C.pillar(s). The runner crouched (sneaking) at EDGE, the pillar
      top's north-east corner, gold in his hand, his head on the brute (35 degrees down, this engine's player limit);
      the brute at pillar_brute (shared), facing north, his head up at the runner's eyes (the game's 40 degrees), DEAD
      STILL (ears only). THE GOLD (_ingots): the runner drops #1 on 865 (his arm swing's top on "threw" 867): the
      game's drop, broad side to this lens as it falls; past the brute's snout on "gold" (873-875), on the deck at
      six_bridge_ingot_1 on 878, still on 887; he drops #2 on "me" + 2 (888): still in the air at the cut (past his
      snout on br14's first frames: a match on action). Hero: the brute.
    MEASURED (bridge director; geo br13_pillar:835 / :873 / :897 --pts the spots and the runner's head top; probe
      tools.sixseconds_bridge_probe ingots / fly br13_pillar:865-881; motion out/test/sixseconds_bridge_motion.mp4,
      every frame; still out/test/br_br13_pillar_873[_zones].png: the ingot broad side beside his snout): the runner's
      head x 57-68 %, y 18.4-25.7 %, its top point y 19 % (the stub: 12.4 %, under the top icons); the brute's head x
      31-44 %, y 41-48 %, 51 px, 82 degrees off the lens (profile, pitched up 40); the three ingot spots x 30-38 %, y
      58.8-59.5 % (the stub: 60-61 %): the tableau spans y 18-60 %. Ingot #1 in flight x 64 -> 40 %, y 23 -> 58 %,
      1-12 degrees off broad side (the stub's phase had it edge-on, a one-pixel sliver), its centre 0.33 from the
      brute's head boxes at its nearest (875, z 1.45), clear of the pillar. Faces are small (51 / 43 px at 540 wide):
      it is the wide of the three. Palette 873 (out/test/sixseconds_pal_br13_pillar_873.png): brute x 2.42 the
      blackstone (53 vs 22), 100 % in the safe area: all pass.
    NEIGHBOURS: before, br12_blocks; after, br14_zero.
    """
    f0, f1 = s.frame_start, s.frame_end
    C.pillar(s)
    runner = C.actor("runner", "br")
    brute = C.actor("brute", "br")
    C.put(runner, f0, EDGE, toward="pillar_brute")
    C.put(brute, f0, "pillar_brute")
    runner.hold("gold_ingot", frame=f0)
    runner.sneak(f0)
    runner.look_at(f0, brute, ease=0)                 # down at the brute (a player's head stops at 35 here)
    brute.look_at(f0, _runner_eyes(), ease=0)         # up at him: the game's 40 degrees
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
      35 mm f/2.4, a slow drift north (0.4 block: 86 -> 82 degrees off his nose) and a 0.006 handheld; his head against
      the teal void, the pillar's foot at the right edge. C.pillar(s). The brute at pillar_brute, his head up at the
      runner's eyes, DEAD STILL (no idle: ears only) from the first frame to the last. THE GOLD (_ingots, one entity
      each since its throw): #1 lies at six_bridge_ingot_1 (landed in br13); #2 (dropped on br13's "me") falls past
      his snout on 897-899, broad side to this lens, and lands at six_bridge_ingot_2 on 902 ("I" 900, "looked" 904);
      #3 is tossed up as the shot starts (900, the runner out of frame: the game's drop with the look 70 degrees UP,
      the only clean way onto spot 3, which lies behind his head from the pillar) and drops into the frame from the
      top on 925, past the back of his head on 927-928, landing at six_bridge_ingot_3 on 931 ("seconds"). Hero: the
      brute.
    MEASURED (bridge director; geo br14_zero:898 / :913 / :952 --pts; probe fly br14_zero:897-933; motion, every
      frame; stills out/test/br_br14_zero_899 / _931[_zones].png: #2 beside his snout; three ingots down): his head x
      29-58 %, y 15.5-31 %, 114 px, 82-86 degrees off the lens, pitched up 40; his feet y 55 %; the ingot spots x
      25-46 %, y 55-57 % (the stub: 60-62 %, on the caption band): everything inside y 14-60 %. #2 at 898 x 64 %, y 19
      % (beside his snout), 4-7 degrees off broad side to 900; its centre 0.16 from his head boxes at 897.6 (the cut;
      a dropped ingot's opaque half-width is 0.22: a graze of a frame, at 0.4 block a frame, in front of his snout,
      not seen as a touch in the preview). #3: 0.09 from his head boxes on 927.6, on the lens side of the back of his
      head (drawn in front of it, falling at 0.5 block a frame). Tried and not used: a three-quarter view (50-62
      degrees off; out/test/brvar2_br14_zero_900_v0 / _v1.png): the pitched-up head shows the underside of the snout
      against a basalt pillar. Palette 913 (out/test/sixseconds_pal_br14_zero_913.png): brute x 3.09 the blackstone
      (53 vs 17), 100 % in the safe area (x 31-56 %, y 17-31 %): all pass.
    NEIGHBOURS: before, br13_pillar; after, br15_wait.
    """
    f0, f1 = s.frame_start, s.frame_end
    brute = C.actor("brute", "br")
    C.pillar(s)
    C.stand(s, brute, "pillar_brute", look=_runner_eyes(), idle=False)
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
    NOW: BR15_CAM: high above and behind the runner (2.4 above his head, 0.9 behind him, 1.15 east), 24 mm f/3,
      looking steeply down past his left shoulder at the brute (aim 0.1 above the deck beside him), a slow push down
      (0.4 block, ease_out: at speed on 953) and a 0.006 handheld. C.pillar(s). The runner crouched at EDGE (as br13),
      gold in his hand, CROUCH-SPAMMING from the first frame (_crouch_spam: Player.sneak off / on every 3-4 frames,
      the game's snap; down from 993 to the cut), his head on the brute; on "he can't" (975) his head SNAPS left and
      right of his line to the brute (_head_snaps: 42 / -40 / 35 degrees, each turn 2 frames, held 4-5) and is back
      on the brute from 994. The brute at pillar_brute, his face turned up at the runner, which is nearly INTO this
      lens (23 degrees off): DEAD STILL (ears only). The three ingots lying beside him, the same entities as in br14
      (turning). Hero: the brute.
    MEASURED (bridge director; geo br15_wait:953 / :957 / :977 / :984 / :998 --pts; motion out/test/
      sixseconds_bridge_motion.mp4 (953-998, every frame); still out/test/br_br15_wait_963[_zones].png):
      the brute's eyes x 44.2-44.7 %, y 41.2-41.6 %, head x 34-53 %, y 36-46 %, face 65 -> 69 px, never blocked,
      23-24 degrees off the lens (his upturned face reads: eyes, snout, tusks); the runner's head x 50-87 %, y 29-51 %
      (the top and back of his head, his teal shoulders and golden boots below it at the right; 132 degrees off the
      lens at rest, 86 / 167 during the snaps: his ear and cheek turn into view); his head box touches the brute's
      head box (x 52-53 %) only in the standing frames of the spam; the three ingots x 34-35 %, y 45.6-50.9 % (a column
      beside the brute, each partly over the next from this height), none hidden by a body. The lava sea at the
      lower left and upper right corners. The first camera of this pass (0.75 east, 26 mm: the brute's head x 36-56 %,
      the runner's x 49-79 %) let his rising head cover the brute's right cheek in the preview (956-959): moved.
      The story's "his head in the lower part of the frame" is met only in part: his head sits BESIDE the brute's (y
      29-51 % against 36-46 %), not below it; from a lens that puts it clearly below (straight above him, z 7+) his
      head hides the brute (geo: blocked by runner_br_head from (401.1, 20.8, 7.0)).
      Palette 963 (out/test/sixseconds_pal_br15_wait_963.png, this camera): brute x 2.99 the blackstone (56 vs 19),
      shirt hue 175, the brute 100 % inside the safe area (x 35-51 %, y 36-45 %): all pass. Stills
      out/test/br_br15_wait_963 / _980[_zones].png (980: a head snap, his ear turned into view, the brute clear).
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
