"""The Hello, sequence DOOR NIGHT: the front of the child's house at night. Beats 2, 18, 19 (shots dn02_fight,
dn18_knock, dn19_beside), sky "night". One function per shot; the contract is in films/hello_common.py (tags
"dn...", C.actor, C.cam, C.lights, st.use / st.hero).

THE PLACE (house_a's west front, seen from the plaza; hello_common's docstring has it block by block)
  door cell (10, -8), one oak step at (9, -8) (high half x 9.5..10 at z 1.0), wall torches at (9, -7, 2) and
  (9, -9, 2): flames at (9.71, -6.5, 2.89) and (9.71, -8.5, 2.89), level with a zombie's head, one block either
  side of it (tangents). North of the door one block of wall and the corner log (the corner is at (10, -5));
  south of it the wall runs on for six blocks, with the one-pane window at (10, -11, 2).
  C.door = the door prop; C.door_torches = its two lights (already one light per torch).
  C.P("step") = where the zombie stands; C.P("watch_door") = (8.9, -5.4): the watcher, two blocks along the wall
  from the zombie, at the corner of the house, facing HC.WATCH_YAW (toward the door). C.watcher(s, "dn") puts him
  there. He stands on exactly this spot, facing exactly this way, in dg15_c and dg20 to dg22.
THE CAMERA of beats 2 and 18 is CAMS["door_front"], exactly, in both (47 mm from (4.4, -10.4, 0.75), 27 degrees off
  the door's axis on the side of its free edge: the cracks and the shudder show past the zombie; straight on, the
  zombie hides them: engine/breaking.py, "THE ZOMBIE HIDES THE CRACKS"). Frame left = north. Beat 19 cuts to
  CAMS["beside"] (from the north-west: both backs): see dn19_beside.
THE LIGHT: C.lights(s, "night_door"): every torch at the look-dev night level 1.3, both door torches x 2 as the
  key; the moon stands in the west behind the camera and gives the wall a cool fill. Scouted:
  out/test/hello_scout_door_night*.png. Do not raise the torches further without tools/palette_check (lit
  cobblestone beside them is at the palette limit).
THE KNOCKING: engine.breaking.bang_on_door(zombie, C.door, f0, f1, **KNOCK, world=C.v, camera=s, glow=0.2),
  called in film order; dn19 continues dn18's with place=False and phase=r["phase"] (breaking notes). Particles
  need camera=s; at night crumbs need glow=0.2 to read. A swing must already be under way on the first frame of
  dn02 and dn18: _zombie_preroll places the zombie a few frames before the shot (it is in neither shot before:
  sq01, in17) and starts one swing there; bang_on_door then goes on with place=False and first= the next swing.
  Only the zombie (hidden outside its shots) is keyed before a shot; the door is keyed from the shot's first
  frame on. Blows: every 16 frames, the door jolts 0.25 rad for a frame (shudder 8) and drops 3 crumbs.
THE FIGHT (dn02): Steve sprints in, turns to the zombie, one swing on "zombie"; undead.hurt gives the red flash
  and the legs' flail, _shove the travel (the game's knock-back under the eaves: no hop into them, off the step).

    $BPY -m tools.hello_door_night_probe dn02_fight 72-144:2      per-frame heads in the frame, crack stage, door
"""
import math

from engine import breaking, undead
from films import hello_common as HC

KNOCK = dict(attempt=44, every=16, half="both", along=-0.3, shudder=8, crumbs=3)   # the staging that reads (breaking
#                                                       notes), plus a few wood crumbs per blow (story: "wood crumbs")
DN02_LEAD = 4          # beat 2: the zombie's pre-rolled swing starts 4 frames before the shot (under way on 72)
DN02_PHASE = 0.3       # beat 2: cracks at stage 3 on the first frame, stage 7 when Steve's blow ends the attempt
DN18_LEAD = 1          # beat 18: the swing starts on 1100: blows then land on 1105, 1121, 1137 ("knocked" 1138),
#                        1153 ("door"), 1169 ("sunrise" 1170), 1185, and go on in beat 19 (1201, 1217, 1233, 1249)
DN18_PHASE = 0.591     # beat 18: cracks at stage 5 on 1101; reset 1119-1120 (between two blows: a reset ON a blow
#                        read as the blow mending the door); stage 9 from 1161 ("until" 1162); reset 1165-1166; the
#                        blow of 1169 ("sunrise" 1170) starts the next attempt on a clean door
STEVE_FROM = (8.3, -11.7)      # beat 2: Steve's run starts beyond the right edge of door_front
STEVE_TO = (8.75, -8.4)        # ... and ends here, 1.5 blocks south-west of the zombie: turned to it (north-east)
#                                his sword arm is on the lens's side (from fight_to, facing north, it was behind him)
STEVE_GO = 68          # ... on this frame (pre-roll), at sprint speed, sliding to a halt
KNOCKBACK = 1.75       # the knock-back of Steve's blow: a sprint hit's (the game's hurt knock-back 0.4, then the
#                        sprint's extra level 0.5 on half of it: 0.2 + 0.5 = 0.7 = 1.75 x 0.4). It clears both the
#                        door_front of now (out of frame from 99) and the wider candidate the lead may adopt (from 104)
DN19_ALONG = 0.5       # dn19: on the cut the zombie moves this far along the door toward its free edge (to y -7.7,
#                        still on the step and in front of the door, 0.2 from PLACES "step") ...
DN19_TURN = 0.45       # ... and turns its body this far (26 deg) away from him: from CAMS "beside" its forearm no
#                        longer comes down on his crown, and the cracked door shows between their two backs
BESIDE_RAISED_Z = 1.5  # dn19: once CAMS "beside" stands this high (asked of the lead: z 1.9, target z 1.5) the fist
#                        clears his head and the focus racks to the zombie on "watched"; below it, focus stays on him
OUT = (5.5, -7.6)      # beat 2: where Steve looks out over the plaza once the zombie is gone (29 deg off the lens)
LOOK_LEFT = (6.0, -5.0, 1.6)   # ... and the small head turn to the left (north, where the zombie went)


EAVES_Z = 3.0          # the underside of house_a's eaves (oak stairs at x 9, z 3, y -11..-5) above the step
STEP_EDGE = -7.0       # the step's north edge (cell (9, -8)): the zombie is on it while any of its 0.6 is south of it
HOLD = 1               # _shove: the hit zombie stays put for one frame before it flies (the client interpolates a
#                        mob's position over 3 ticks, so it lingers about a tick in the hurt colour): the blow's frame
#                        is a sharp red zombie on the step, not a smear (motion blur opens at the frame for half a frame)
SWING_LEAD = 2         # dn02: Steve's swing starts 2 frames before the blow, so his arm is up (highest 2.4 frames in)
#                        on the flash frame: the client starts the swing on the click, the hurt arrives a tick later


def _shove(C, z, frame, k):
    """The knock-back of Steve's blow as the game plays it HERE: straight north along the wall (his blow comes
    from the south; the wall stops any push into it), with a ceiling. undead.hurt's hop (0.96 up) would put the
    zombie's head 0.9 block into the eaves above the step (their underside is 1.05 above its head), so this
    replaces its travel keys with the same LivingEntity physics (knockback speed 0.4 x k, vertical min(0.4, ...),
    then per tick: move, gravity 0.08, drag 0.98 / 0.91 in the air, 0.546 on the ground) with two collisions:
    the eaves (the head stops under them) and the step (it drops to the grass once it is off it). The red flash
    and the legs' flail stay undead.hurt's. Returns the frame it is at rest."""
    from engine import characters as ch
    p0 = z.pos_at(frame)
    height = undead.ZOMBIE_SIZE[1]
    vh = undead.KNOCKBACK * float(k)
    vy = min(0.4, undead.REST_VY / 2.0 + vh)
    d, h, ground = 0.0, p0.z, True
    track = []
    for _ in range(60):
        d += vh
        y = p0.y + d
        floor = p0.z if y - 0.3 < STEP_EDGE else C.stand((p0.x, y))[2]
        h_new = h + vy
        if y - 0.3 < -4.0 and h_new + height > EAVES_Z:        # under the eaves: the head stops there
            h_new, vy = EAVES_Z - height, 0.0
        ground = h_new <= floor + 1e-6
        if ground:
            h_new, vy = floor, 0.0
        h = h_new
        track.append((y, h))
        vy = (vy - undead.GRAVITY) * undead.AIR_DRAG_Y
        vh *= undead.GROUND_DRAG if ground else undead.AIR_DRAG
        if ground and vh < 0.003:
            break
    for i, values in ((1, [y for y, _h in track]), (2, [h for _y, h in track])):
        keys = ([(frame, None, "LINEAR"), (frame + HOLD, (p0.y, p0.z)[i - 1], "LINEAR")]
                + [(frame + HOLD + (n + 1) * undead.TICK, v, "LINEAR") for n, v in enumerate(values)])
        ch._segment(z.root, "location", i, keys, "LINEAR")
    return int(math.ceil(frame + HOLD + len(track) * undead.TICK))


def _zombie_preroll(C, z, f0, lead):
    """The zombie already on the step and in mid-swing on frame f0 (pre-roll: it must be in no shot before):
    placed on bang_on_door's own stand point a little before f0, arms raised, one swing started `lead` frames
    before f0; its blow lands just after f0 and shudders the door (breaking.shudder; the wood crumbs of this one
    blow are not drawn). Only the zombie is keyed before f0 (hidden there by st.use); the door is keyed from f0
    on. The knocking of the shot then goes on with first = KNOCK["every"] - lead. Returns the stand point."""
    k = f0 - lead
    stand, yaw = breaking.stand_point(C.door, along=KNOCK["along"], world=C.v, frame=k - 2)
    z.place(k - 2, stand, yaw)
    z.aggro(k - 2, True, ease=0)
    z.attack(k)
    breaking.shudder(C.door, int(round(k + breaking.HIT_DELAY)), KNOCK["shudder"])
    return stand


def dn02_fight(st, s, C, nar):
    """BEAT 2  "He fought every zombie that knocked on our door."   frames 72-144 (73 f, 3.04 s), sky night.
    Words: He 74, fought 76, every 85, zombie 94, that 108, knocked 113, on 122, our 124, door 128.

    STORY: Night. Low from the plaza, a tight vertical frame on the child's oak door with about one block of wall
    either side, the two wall torches beside the door as the key light. A zombie on the step hits the door with
    both arms out. Steve steps in from the right and swings once: the zombie flashes red and is knocked back out
    of frame to the left. Steve ends planted in front of the door, sword up. No kill is shown. This exact framing
    returns in beat 18. About 3 seconds.
    Cast: Steve (iron chestplate, leggings, boots, no helmet, iron sword), zombie. Effects: one sword swing, red
    hurt flash and one knock-back, oak door, two wall torches as key light.

    MUST BE SEEN, ON WHICH WORD
      from frame 72   the zombie is already knocking (a swing under way on the first frame, the door shuddering)
      "fought" 76 .. "every" 85    Steve comes into frame from the right (the south), already at speed on frame 72
                      (pre-roll: C.actor("steve_iron", "dn") is in no shot before)
      "zombie" 94     the swing lands: steve.attack(frame), undead.hurt(zombie, frame, attacker=steve): red flash
                      (12 frames) and the knock-back hop away from Steve, i.e. NORTH along the wall = out of frame
                      LEFT (1.99 blocks in 19 frames: check that it leaves the frame; knockback=2.0 doubles it). End
                      the knocking (bang_on_door's frame_end) on the blow.
      "knocked" 113 .. 144    Steve planted square in front of the door, sword in hand, the zombie gone; a small
                      head turn after it to the left keeps him alive to frame 144
    SHARED: CAMS["door_front"] unchanged (beat 18 must match it frame for frame in framing); PLACES "step".
      Cast: C.actor("zombie", "dn"), C.actor("steve_iron", "dn").
    NEIGHBOURS: before, sq01_guard (golden square, Steve and the child at the bell); after, in03_bed (Steve asleep
      in the red bed). Hard cuts both sides; nothing of this shot continues.
    RISKS (story): with no kill shown the fight must read from ONE swing: the red flash, a hop that carries the
      zombie fully out of frame, and Steve ending square in front of the door. Watch the two wall torches at head
      height for tangents with the zombie's and Steve's heads. A zombie has 20 health: it must not die. The zombie
      leaving frame left rhymes with the watcher being found on the left in beat 19.

    WHAT IT DOES NOW
      66-72   pre-roll (_zombie_preroll, DN02_LEAD 4): the zombie on the step, arms raised, a swing started on 68;
              its blow lands on 73 (the door jolts). bang_on_door from 72 to the blow: the next swing 84 (blow 89,
              jolt + crumbs), cracks stage 3 on 72 climbing to 7; cleared on 94 when the zombie is knocked off.
      68-91   Steve (pre-roll) sprints from STEVE_FROM (8.3, -11.7) to STEVE_TO (8.75, -8.4) and slides to a halt
              (still from about 86); his body comes in at the right edge on 76 ("fought"), fully in by 82.
      88-93   he turns his body to the zombie (north-east): his sword arm is then on the lens's side (from
              "fight_to", facing north, the whole swing was hidden behind his back: rendered). His swing starts
              on 92 (SWING_LEAD 2: the game starts the swing on the click, the hurt comes a tick later): on 94 the
              arm is up (-90 deg) and the sword stands above his right shoulder; its tip shows there to 101.
      94      "zombie": undead.hurt (red flash 94-105, legs flail). The travel is _shove: the zombie holds on the
              step for one frame (HOLD: 94 is a sharp, red zombie with its arms up, on the word), then goes north
              along the wall at a sprint hit's knock-back (KNOCKBACK 1.75, the game's value), stopped under the
              eaves (undead's hop would put its head 0.9 block into them), dropping off the step; it starts on 95
              (sharp in its first half), a smear on 96-97 (head x 2-27 % on 96), its head off the left edge from
              98, out of frame entirely from 99, at rest on the grass past the house's corner at (9.7, -3.32) from
              110, never seen again. No death. (With the wider door_front the lead may adopt, its whole body is
              out from 103: tools/hello_door_night_raised.py probe; 1.25 would leave it lying at the left edge.)
      102-112 his head follows it to the left; 113 ("knocked") .. 123 he turns to face out over the plaza (OUT,
              29 deg off the lens): planted before the door, the iron sword in his right hand at the frame's left;
              130 ("door" + 2) a small head turn to the left, after it; held to 144.
      camera  door_front exactly, handheld 0.008; focus on the door, racked to Steve's head from "that" (108).
    MEASURED (tools/hello_door_night_probe, render): zombie head x 19-44 %, y 17-31 % until the blow; Steve's
      head x 42-77 %, y 35-51 % from 84 to the end (from behind 150 deg while he swings; 36-38 deg off the lens
      when faced out, 72 deg after the head turn); palette_check dn02@90 passes (stone G/R 0.99, heroes 100 %).
      The sword lies across the caption band (y 60-72 %, x 5-35 %) once he faces out: the caption sits on it.
    """
    f0, f1 = s.frame_start, s.frame_end
    z = C.actor("zombie", "dn")
    steve = C.actor("steve_iron", "dn")
    blow = C.at(s, "zombie")                                   # 94: the sword lands on the word
    stand = _zombie_preroll(C, z, f0, DN02_LEAD)               # (pre-roll: zombie_dn is in no shot before)
    r = breaking.bang_on_door(z, C.door, f0, blow, place=False, first=KNOCK["every"] - DN02_LEAD, phase=DN02_PHASE,
                              world=C.v, camera=s, glow=0.2, **KNOCK)
    # Steve: pre-rolled (steve_iron_dn is in no shot before), sprinting in from beyond the right edge
    start, end = C.stand(STEVE_FROM), C.stand(STEVE_TO)
    steve.place(STEVE_GO - 2, start, HC.yaw_to(start, end))
    e = steve.walk(STEVE_GO, [start, end], sprint=True, ramp=(False, True))
    steve.face(blow - 6, z, ease=5)                            # squares up to it: his sword side to the lens
    steve.attack(blow - SWING_LEAD)                            # arm up on the flash frame (94), not 2 frames later
    undead.hurt(z, blow, attacker=(stand[0], stand[1] - 1.3, stand[2]), knockback=KNOCKBACK)
    rest = _shove(C, z, blow, KNOCKBACK)
    steve.track(blow + 8, blow + 18, z, step=3, ease=4)        # looks after it (once his swing is over: the
    #                                                            swing keys his head too, fx.arm_swings)
    out = steve.face(C.at(s, "knocked"), OUT, ease=10)        # planted before the door, facing out, sword in hand
    steve.look_at(C.at(s, "door") + 2, LOOK_LEFT, ease=10)    # a small turn of the head after it, to the left
    C.memo.setdefault("dn_log", []).append(           # (printed by tools/hello_door_night_probe)
        "dn02 steve walk %d-%d, blow %d, zombie at rest %d, faced out %d; knocks %s hits %s stages %s" % (
            STEVE_GO, e, blow, rest, out, r["knocks"], r["hits"], r["stages"]))
    st.use(s, z, steve)
    C.cam(s, "door_front", focus=C.P("door"))
    s.focus(steve.head, at_s=(C.at(s, "that") - 1) / 24.0, rack_s=0.5)
    st.hero(s, "zombie", z)
    st.hero(s, "steve", steve)
    C.lights(s, "night_door", near="door", radius=24.0)


def dn18_knock(st, s, C, nar):
    """BEAT 18  "Last night a zombie knocked on our door until sunrise."   frames 1101-1192 (92 f, 3.83 s), sky
    night. Words: Last 1103, night 1111, a 1123, zombie 1125, knocked 1138, on 1147, our 1149, door 1153, until 1162,
    sunrise 1170.

    STORY: The exact framing of beat 2. A zombie stands on the step hitting the oak door, the door shudders with
    each blow, and the break cracks climb and reset without ever finishing. The right side of the frame, where
    Steve stepped in, stays empty for the whole line. About 3.2 seconds.
    Cast: zombie. Effects: zombie arm swings on the door, door shudder, crack overlay on the door that never
    completes, two wall torches as key light.

    MUST BE SEEN, ON WHICH WORD
      frame 1101      a swing already under way; cracks already part of the way up (start with phase > 0)
      "knocked" 1138  a blow lands on or within two frames of the word (hits = swing frame + about 5)
      "until" 1162 .. "sunrise" 1170    the cracks reach their last stage and RESET to a clean door: it holds
      the whole shot  the right third of the frame EMPTY (nobody comes): the same frame as beat 2, where Steve
                      came in there. The camera is CAMS["door_front"], unchanged: only the handheld lives.
    SHARED: CAMS["door_front"]; the knocking continues into dn19_beside: leave the bang_on_door result in
      C.memo["dn_bang"] (the stub does). The same zombie instance as beat 2 is fine (not a consecutive shot).
    NEIGHBOURS: before, in17_window (inside, the child at the west window, him out on the plaza); after,
      dn19_beside: the zombie, the cracks and the rhythm carry over the cut.
    RISKS (story): knocking has to read with the sound off, and a pedant knows a Hard-mode zombie breaks the door.
      Fallback: exaggerated arm swings (every=16), wood crumbs on each hit (crumbs=, glow=0.2), cracks that climb
      and visibly reset so it is clear this door holds. Keep the empty right side wide enough that Steve's absence
      is felt against beat 2. The watcher is NOT in this shot (not in st.use): dn19 reveals him.

    WHAT IT DOES NOW
      1098-1100  pre-roll (_zombie_preroll, DN18_LEAD 1; zombie_dn is not in in17): the zombie placed on the step,
              arms raised, a swing started on 1100: it is under way on 1101 and lands on 1105 (the door jolts).
      1101-1192  bang_on_door(place=False, first=15, phase DN18_PHASE 0.591): swings 1116, 1132, 1148, 1164, 1180;
              blows (jolt 0.25 rad + 3 crumbs) 1121, 1137 ("knocked" 1138), 1153 ("door"), 1169 ("sunrise"
              1170), 1185. Cracks: stage 5 on 1101, 9 on 1115, reset 1119-1120 (between blows), climbing again,
              9 from 1161 ("until" 1162), reset 1165-1166, stage 0 from 1167: the blow on 1169 hits a clean door
              (stage 5 at the cut). The rhythm and the cracks go on in dn19 (C.memo["dn_bang"]).
      camera  door_front exactly as dn02 (handheld 0.008), focus on the door. Nobody else: the right third (the
              cobblestone wall and the south torch, where Steve came in) stays empty.
    MEASURED (tools/hello_door_night_probe, render): the zombie's head x 19-44 %, y 17-31 % the whole shot; the
      door at x 33-60 %; nothing at x > 62 % but the wall and its torch. palette_check dn18@1150 passes (stone
      G/R 0.99, hero 100 % inside).
    """
    f0, f1 = s.frame_start, s.frame_end
    z = C.actor("zombie", "dn")
    _zombie_preroll(C, z, f0, DN18_LEAD)                       # (pre-roll: zombie_dn is not in in17_window)
    r = breaking.bang_on_door(z, C.door, f0, f1 + 1, place=False, first=KNOCK["every"] - DN18_LEAD,
                              phase=DN18_PHASE, world=C.v, camera=s, glow=0.2, **KNOCK)
    C.memo["dn_bang"] = r
    C.memo.setdefault("dn_log", []).append("dn18 knocks %s hits %s stages %s resets %s phase out %.3f next %.1f" % (
        r["knocks"], r["hits"], r["stages"], r["resets"], r["phase"], r["next_knock"]))
    st.use(s, z)
    C.cam(s, "door_front", focus=C.P("door"))
    st.hero(s, "zombie", z)
    C.lights(s, "night_door", near="door", radius=24.0)


def dn19_beside(st, s, C, nar):
    """BEAT 19  "He stood beside it and watched."   frames 1193-1257 (65 f, 2.71 s), sky night.
    Words: He 1195, stood 1198, beside 1205, it 1216, and 1219, watched 1222. The pause after it is 1.0 s: from
    about frame 1237 the picture holds in silence.

    STORY: The camera drifts about a block and a half to the left, off the zombie. He was standing just outside
    the frame the whole time, two blocks along the wall from the zombie, seen from behind, facing the door. The
    zombie keeps hitting the door and never turns toward him. Torch light on the wall in front of them, their two
    backs to us. About 2.5 seconds.
    Cast: the watcher (from behind), zombie. Effects: slow drift left to reveal him, zombie arm swings continue,
    zombie never targets him.

    THE STAGING (decided on stills): he faces the door (HC.WATCH_YAW; he must, for the two-shot of beats 4 and 22),
      so from the plaza camera of beat 18 (south-west) he would be seen from the front. This shot therefore takes
      the story's own fallback ("cut to a wider shot ... with both of them from behind"): there is a cut anyway
      (dn18 -> dn19 on the sentence), and CAMS["beside"] looks at the door from the north-west, the zombie centred
      and him just outside the left edge; the camera drifts a block and a half to the left and he comes in.
    MUST BE SEEN, ON WHICH WORD
      frame 1193      the zombie at the door, knocking (the rhythm and cracks of dn18 continue), the drift begun
      "stood" 1198 .. "beside" 1205     his shoulder and back come into frame from the left
      "watched" 1222  both backs in frame: he, dead still, facing the door; the zombie still swinging
      1237 .. 1257    hold: the only things that move are the zombie's arms and the door
    HIS FACE IS NEVER SEEN: from behind only (the plain "watcher" skin, about 15 to 40 degrees off his back). He
      does not move at all: placed once, no idle (C.actor("watcher", ...) is built dead still).
    SHARED: PLACES "watch_door" + HC.WATCH_YAW (C.watcher(s, "dn")), CAMS "beside". The knocking:
      bang_on_door(..., place=False, phase=C.memo["dn_bang"]["phase"]).
    NEIGHBOURS: before, dn18_knock; after, dg20_walkup: the same door in golden morning, a piece of rotten flesh
      where the zombie stood, he on the same spot, facing the same way.
    RISKS (story): the reveal needs him just outside the frame; the north torch flame (9.71, -6.5, 2.89) is above
      and right of his head from this side: check for a tangent. The mirror image is not available (south of the
      door he would stand at the child's window).
    SCOUTED (out/test/hello_scout_night_dn19_beside_1196.png, _1250.png): the reveal works (his teal shoulder at the
      left edge on the first frame, their two backs by the end), but at the end he is too large and the zombie's
      head sits right above his: a longer lens from further back, or a smaller drift (CAMS "beside" is shared:
      not changed here, reported).

    WHAT IT DOES NOW
      him     C.watcher(s, "dn"): on watch_door facing WATCH_YAW, placed once on 1193, nothing keyed: dead still.
      zombie  on the cut (1193, between two swings: the last of dn18 landed on 1185) it is re-placed DN19_ALONG
              0.5 along the door toward its free edge, (9.7, -7.2) -> (9.7, -7.7): still on the step and in front
              of the door, 0.2 from PLACES "step"; and its body turned DN19_TURN 0.45 rad (26 deg) away from him,
              so its arms point away from the lens. A cheat across a 70-degree change of camera: dn18's transform
              holds through 1192.5 (the shutter of its last frame), the jump is after it. With the shared camera
              as it is, the forearm came down onto the crown of his head on every blow and their heads stacked
              ("behind him", not "beside it"); now the arm ends clear of his head on "it" (1217), only its fist
              meets the top-right corner of his head on 1233 and 1249, and on "watched" (1222) the two backs stand
              side by side with the cracked door between them. bang_on_door(place=False, phase from dn18) carries
              the rhythm over the cut: swings 1196, 1212, 1228, 1244, blows 1201, 1217, 1233, 1249; cracks stage 5
              on 1193 (as on 1192), 9 on 1207, reset 1211-1212, climbing to 9 on 1253, clean again on 1257. It
              never turns to him.
      camera  CAMS "beside" unchanged, its drift with ease_out (at speed on 1193); focus on him (his back sharp,
              the zombie soft) the whole shot: a sharp fist meeting the corner of his soft head would read as a
              blow on him. If the lead raises CAMS "beside" as asked (z >= BESIDE_RAISED_Z), the focus racks to
              the zombie on "watched" (1221, 0.6 s) by itself: tested in memory with z 1.9 / target z 1.5 and the
              motion review's start (tools/hello_door_night_raised.py): the fist ends clear above his head on 1217,
              1233 and 1249, the zombie sharp from 1233.
    MEASURED (tools.hello_geo, tools/hello_door_night_probe, render): his head x -30..10 % on 1193 (a sliver of
      his hair and his teal shoulder are at the left edge on the first frame: the shared camera and place give
      that), -23..16 % on "stood", -14..24 % on "beside", 2..39 % on "watched", 13..47 % (y 33-50 %) from 1240;
      143-165 deg off his nose throughout: the back of his head, no eye. The zombie's head x 44-78 %, y 14-30 %
      (148-162 deg off the lens, never toward him); a gap of 5 % or more between the two heads. The north torch
      flame stays clear above his head; the south one sits at the soft zombie's right shoulder (x 77-82 %) from
      about 1215. palette_check dn19@1222 passes (stone G/R 1.00, his shirt hue 183, zombie 100 % / him 84 %
      inside the safe area).
    """
    f0, f1 = s.frame_start, s.frame_end
    z = C.actor("zombie", "dn")
    him = C.watcher(s, "dn")                   # on watch_door, facing HC.WATCH_YAW, dead still (st.use done)
    p, yaw = z.pos_at(f0), z.yaw_at(f0)        # on the cut (between two swings): along the door to its free edge,
    z.place(f0, (p[0], p[1] - DN19_ALONG, p[2]), yaw - DN19_TURN)   # its body turned away from him
    z.aggro(f0, True, ease=0)
    r = C.memo.get("dn_bang", {})
    r2 = breaking.bang_on_door(z, C.door, f0, f1 + 1, phase=r.get("phase", 0.0), place=False, world=C.v, camera=s,
                               glow=0.2, **KNOCK)
    C.memo.setdefault("dn_log", []).append("dn19 knocks %s hits %s stages %s" % (r2["knocks"], r2["hits"],
                                                                              r2["stages"]))
    st.use(s, z)
    w = C.P("watch_door")
    C.cam(s, "beside", focus=(w[0], w[1], 1.5))     # on his back the whole shot (no rack to the zombie: with the
    #   shared camera its fist still meets the top-right corner of his head on 1233 and 1249; kept soft behind his
    #   sharp head it reads as behind him, sharp it would read as a blow on him; the raised camera is the lead's)
    if HC.CAMS["beside"]["pos"][2] >= BESIDE_RAISED_Z:     # the raised camera asked of the lead: the fist ends
        s.focus(z.head, at_s=(C.at(s, "watched") - 1) / 24.0, rack_s=0.6)    # clear of his head: the thing he
    #                                                          watches is sharp on "watched" (the motion review)
    st.hero(s, "zombie", z)
    st.hero(s, "watcher", him)
    C.lights(s, "night_door", near="door", radius=24.0)
