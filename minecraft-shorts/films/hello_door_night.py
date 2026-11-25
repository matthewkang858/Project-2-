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
THE KNOCKING: engine.breaking.bang_on_door(zombie, C.door, f0, f1 + 1, **KNOCK, world=C.v, camera=s, glow=0.2),
  called in film order; the next shot continues it with place=False and phase=r["phase"] (breaking notes).
  Particles need camera=s; at night crumbs need glow=0.2 to read.
"""
from engine import breaking, undead
from films import hello_common as HC

KNOCK = dict(attempt=44, every=16, half="both", along=-0.3, shudder=8, crumbs=3)   # the staging that reads (breaking
#                                                       notes), plus a few wood crumbs per blow (story: "wood crumbs")


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
    SHARED: CAMS["door_front"] unchanged (beat 18 must match it frame for frame in framing); PLACES "step",
      "fight_from", "fight_to". Cast: C.actor("zombie", "dn"), C.actor("steve_iron", "dn").
    NEIGHBOURS: before, sq01_guard (golden square, Steve and the child at the bell); after, in03_bed (Steve asleep
      in the red bed). Hard cuts both sides; nothing of this shot continues.
    RISKS (story): with no kill shown the fight must read from ONE swing: the red flash, a hop that carries the
      zombie fully out of frame, and Steve ending square in front of the door. Watch the two wall torches at head
      height for tangents with the zombie's and Steve's heads. A zombie has 20 health: it must not die. The zombie
      leaving frame left rhymes with the watcher being found on the left in beat 19.
    SCOUTED (out/test/hello_scout_night_dn02_fight_100.png): the door between its two torches, warm key, the zombie
      knocking with arms out; the stub's Steve stands with his back to the lens in front of the zombie.
    STUB: the zombie knocks through the whole shot, Steve stands at "fight_to"; no fight is staged yet.
    """
    f0, f1 = s.frame_start, s.frame_end
    z = C.actor("zombie", "dn")
    steve = C.actor("steve_iron", "dn")
    breaking.bang_on_door(z, C.door, f0, f1 + 1, world=C.v, camera=s, glow=0.2, **KNOCK)
    C.put(steve, f0, "fight_to", toward="step")
    steve.idle(f0, f1 + 1)
    st.use(s, z, steve)
    C.cam(s, "door_front", focus=C.P("door"))
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
    SCOUTED (out/test/hello_scout_night_dn18_knock_1150.png): the cracks show on the door past the zombie, the
      right of the frame empty.
    STUB: the knocking with the recommended staging for the whole shot.
    """
    f0, f1 = s.frame_start, s.frame_end
    z = C.actor("zombie", "dn")
    r = breaking.bang_on_door(z, C.door, f0, f1 + 1, phase=0.35, world=C.v, camera=s, glow=0.2, **KNOCK)
    C.memo["dn_bang"] = r
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
      head sits right above his: a longer lens from further back, or a smaller drift.
    STUB: he stands on "watch_door" facing the door, the zombie knocks on, CAMS "beside" with its drift.
    """
    f0, f1 = s.frame_start, s.frame_end
    z = C.actor("zombie", "dn")
    C.watcher(s, "dn")                         # on watch_door, facing HC.WATCH_YAW, dead still (st.use done)
    r = C.memo.get("dn_bang", {})
    breaking.bang_on_door(z, C.door, f0, f1 + 1, phase=r.get("phase", 0.0), place=False, world=C.v, camera=s,
                          glow=0.2, **KNOCK)
    st.use(s, z)
    w = C.P("watch_door")
    C.cam(s, "beside", focus=(w[0], w[1], 1.5))
    st.hero(s, "zombie", z)
    C.lights(s, "night_door", near="door", radius=24.0)
