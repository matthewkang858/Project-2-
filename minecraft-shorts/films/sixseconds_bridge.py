"""Six Seconds, sequence BRIDGE: the second bastion, in another world. The boot shot again, the brute blocking the
bridge, the pillar: beats 11, 12, 13, 14, 15 (shots br11_boots, br12_blocks, br13_pillar, br14_zero, br15_wait), sky
"soul" (soul_sand_valley: the fog and the void of this world are TEAL; the lead's choice, films/sixseconds.py
SKIES). One function per shot; the contract is in films/sixseconds_common.py (tags "br...", C.actor, C.item, C.rest,
C.cam, C.rack, C.lights, C.pillar, st.use / st.hero).

STATUS: STUBS by the lead director, revised in the lead's review pass (two independent checks). Each function puts
the shot's camera on its place and its cast roughly where the story wants them; the docstrings say what each shot
must become. Everything may be rewritten except what SHARED names.

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
TAGS TAKEN by the stubs: runner_br (br11, br12, br13, br15), brute_br (br12-br15), gold_ingot_br14_k, _br15_k.
PREVIEW samples of this sequence: 9.
"""
import math

from mathutils import Vector

from engine import piglins

# br11: the runner sprints in from behind the lens (at speed, unseen: the lens is at y 2.9) on RUN_FROM, so that the
# bridge is EMPTY for a beat out of black, his legs enter from the frame's left on "bastion" and the boots stop on the
# mark before "same boots" (the story check: the first stub stopped them only on 726-728, after the words)
BR11_RUN_FROM = (400.5, 0.0, 0.0)
BR11_RUN_START = 683
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

# THE PILLAR (br13-br15): the runner crouches on the netherrack pillar's top block (x 400..401, y 19..20, top z 3)
# at its SOUTH-EAST corner, over the brute: sneaking holds a player on an edge, his box still on the block (centre
# 0.25 / 0.2 in from the east / south faces). From the middle of the top (pillar_top) a dropped ingot lands on the
# pillar itself (the game's drop is look x 0.3 + 0.1 up: looking down, it falls at his feet), and his body hid the
# brute from br15's camera.
EDGE = (401.1, 19.95, 3.0)
CROUCH_EYE = 1.27              # a crouching player's eye height (the game's crouching pose: 1.27)
# the gold he throws: three ingots, ONE entity each from the throw to the end of br15, resting on the shared spots
# six_bridge_ingot_1..3. The throws are the game's drop (Player.drop: look x 0.3 + 0.1 up, no jitter), the look
# solved so that each comes to rest on its spot: #1 on "threw" (br13), #2 on "me" (br13: in the air over the cut,
# falling past his snout on br14's first frame), #3 out of frame in br14, landing on "zero"
INGOT_SPOTS = ("six_bridge_ingot_1", "six_bridge_ingot_2", "six_bridge_ingot_3")
INGOT_LOBS = (False, False, True)
# br13: side-on from the east over the void (engine/nether.py bridge_pillar, re-aimed): the whole tableau inside
# y 14-60 %
BR13_CAM = dict(pos=(410.2, 18.7, 2.2), target=(400.5, 18.9, 1.0), lens=28.0, fstop=4.0, pos1=(410.1, 18.95, 2.2),
                handheld=0.008)
# br14: the brute in profile from the east (engine/nether.py bridge_profile, re-aimed)
BR14_CAM = dict(pos=(406.3, 18.05, 1.35), target=(400.5, 18.2, 0.25), lens=35.0, fstop=2.4, pos1=(406.3, 18.35, 1.35),
                handheld=0.006)
# br15: high behind the runner on the pillar (engine/nether.py bridge_top, re-placed)
BR15_CAM = dict(pos=(401.85, 20.7, 7.35), target=(401.0, 18.65, 0.1), lens=26.0, fstop=3.0, pos1=(401.8, 20.5, 7.0),
                handheld=0.006)
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
        it.animate(throw, last + 1)
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
    NOW (stub): the runner waits behind the lens at BR11_RUN_FROM (400.5, 0.0), sprints from 683 at speed (sprint,
      ramp out: the skid) to the mark; the focus holds BR11_FAR (the pillars 15 blocks off) and racks to the mark over
      10 frames from "bastion" + 2 (C.rack). Hero: the boots.
    MEASURED (the lead's review pass; tools.sixseconds_geo --sky soul br11_boots:716 / :725 --boots runner_br, the
      probe of his track; stills out/test/sixseconds_scout_br11_boots_685.png (the empty bridge, focus far: the
      basalt pillars and their gold caps against the teal void read), _703.png (his leg entering, soft), _725_zones.png
      (the boots stopped)): he is behind the lens to about 696, his body enters the frame's left edge on 699-702, the
      feet come to rest by about 716-718 (6.24 on 714, 6.47 on 718, 6.50 on 722); boots x 27.7-69.8 %, y 42.7-58.6 %
      on 725 (pt05 on 318: x 27.7-70.1 %, y 43.1-58.9 %): THE BOOT FRAMING holds. Palette 725: shirt hue 171, pants
      min channel 14, boots 100 % inside the safe area. His back is to the lens here (he runs north, toward br12's
      brute); in pt05 he faces it (he came from the gateway): each is right for its neighbours.
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
    C.rack(s, Vector(mark) + Vector((0.0, 0.0, 0.2)), C.at(s, "bastion") + 2, BR11_RACK)
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
    NOW (stub): engine/nether.py's bridge_shoulder (50 mm f/2.6 over the runner's shoulder at bridge_player), the
      runner at bridge_player looking at the brute (iron pickaxe), the brute at bridge_brute facing him, dead still.
      Hero: the brute.
    MEASURED (out/test/sixseconds_set_b12_bridge_shoulder.png under nether_wastes; out/test/
      sixseconds_scout_sky_b12_bridge_shoulder_soul_sand_valley.png under this film's sky): brute x 40-59 %, y
      39-47 %, 1.74 x the blackstone; the teal void behind him.
      UNDER THIS FILM'S SKY "soul" (the lead: tools.sixseconds_palette --sky soul on the old timeline's 780, still
      out/test/sixseconds_pal_br12_blocks_780.png; out/test/sixseconds_scout_br12_blocks_815_zones.png): brute x
      1.52 the blackstone (46 vs 30: AT the 1.5 limit; 1.74 under nether_wastes), gold hue 46, shirt hue 171. Give
      him more of his lantern (C.lights(s, "bridge", groups={"bridge_lantern": k}) with k up to about 1.5, measured)
      or a film-local key C.fill("br_key", ...) before anything else; re-measure. (Not changed by the review pass:
      the frames named in those stills are the old timeline's, 7 frames earlier.)
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
    NOW (stub): engine/nether.py's bridge_pillar (30 mm f/4, side-on from the east over the void), C.pillar(s), the
      runner crouched on pillar_top with an ingot in his hand, the brute at pillar_brute looking up at the top. Hero:
      the brute.
    MEASURED after the review pass (tools.sixseconds_geo --sky soul br13_pillar:840 / :870): brute eyes x 38 %,
      y 41.6 %, head x 27-44 %, y 38-47 %, 63 px, in profile (107 degrees off the lens), pitched to the game's 40;
      the runner's head x 56-66 %, y 12.4-18.7 %: its top is UNDER the Reels top icons (y < 13-14 %): aim the camera
      a little higher or pull back (the story wants the whole tableau inside y 14-60 %); the ingot spots
      six_bridge_ingot_1..3 x 35 / 29.5 / 25 %, y 60-61 % (on the caption band's top edge: the same tilt fixes both).
      Earlier (set still b13, the brute on pillar_foot): 2.84 x the blackstone; under the teal fog his teal shirt
      separates from the void by brightness only: check it at 360x640.
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
    NOW (stub): engine/nether.py's bridge_profile (35 mm f/2.4 from 5.3 blocks), C.pillar(s), the brute at
      pillar_brute looking up, two ingots already lying at his feet. Hero: the brute.
    MEASURED after the review pass (tools.sixseconds_geo --sky soul br14_zero:913): brute in profile (112 degrees off
      the lens), head x 29-63 %, y 15.5-32.7 %, 125 px, pitched up 40; the ingot spots six_bridge_ingot_1 / _2 / _3 at
      x 46 / 34 / 25 %, y 61.7 / 60.7 / 59.8 %: ON the caption band's top edge (his feet are at y 60 %): aim the
      camera a little lower (about 0.3 block) so the feet and the ingots sit at y 55-58 %. Earlier (set still b14,
      the brute on pillar_foot): 2.69 x the blackstone; the pillar at the right edge.
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
    NOW (stub): BR15_CAM (engine/nether.py's bridge_top, 30 mm f/3 high behind the runner on the pillar, aimed 1.5
      block lower), C.pillar(s), the runner crouched on pillar_top (gold in his hand), the brute at pillar_brute
      looking up at him, three ingots lying at his feet. Hero: the brute.
    MEASURED after the review pass (tools.sixseconds_geo --sky soul br15_wait:963 / :968 --pts the ingots;
      tools.sixseconds_palette --sky soul 968; still out/test/sixseconds_scout_br15_wait_968_zones.png): brute eyes
      x 40.5 %, y 37 %, head x 23-52 %, y 30-43 %, 102 px, NOT blocked (43 degrees off the lens, pitched up 40: the
      upturned face reads); the three ingots x 25-27 %, y 48.6 / 51.7 / 55.5 %, none hidden (the story check had all
      three blocked or in the caption band: fixed); brute x 3.25 the blackstone, shirt hue 174, pants min channel
      16: all pass. The runner's back is the big shape on the RIGHT (x 50-100 %, from the top to about y 60 %); his
      head sits at the top right corner (x 72-122 %, y -15..13 %: outside the frame and under the top icons), not
      "in the lower part of the frame" as the story has it: from any camera above and behind him the brute is BELOW
      him in the frame unless the lens looks nearly straight down (measured: from (400.7, 20.6, 6.5) his arm hides
      the brute's eyes; from (401.2, 21.0, 6.3) 28 mm the brute is clear, 88 px, his head at the right edge). The
      director chooses; keep the brute's eyes and the three ingots clear (geo --pts) and inside y 14-60 %.
      Earlier MEASURED PROBLEM (fixed): with the brute ON pillar_foot (400.5, 18.25) the pillar's top block cut his
      face in half from bridge_top (his eyes behind bridge_pillar_2, 3.7 blocks from the lens).
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
