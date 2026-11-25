"""The Hello, sequence DOOR GOLD: the front of the child's house in golden light (morning, and late gold in beat
15). Beats 4, 5, 15, 20, 21, 22 (shots dg04_hello, dg05_nod, dg15_a, dg15_b, dg15_c, dg20_walkup, dg21_crouch,
dg22_eyes), sky "gold". One function per shot; the contract is in films/hello_common.py (tags "dg...", C.actor,
C.cam, C.lights, st.use / st.hero).

THE PLACE (house_a's west front, hello_common's docstring): door cell (10, -8), the oak step at (9, -8) (high half
  x 9.5..10 at z 1.0, low half x 9..9.5 at z 0.5), wall torches either side at head height; north of the door one
  block of wall and the corner log: the house's north-west corner is at (10, -5).
  PLACES: "watch_door" (8.9, -5.4) = his spot, facing HC.WATCH_YAW (toward "watch_face" (9.75, -7.2): the door);
  "hello_child" (9.25, -6.41) = the child at his feet, between him and the door; "step", "step_child", "door_in",
  "run_off", "watch_far" (8.3, 11.5), "watch_mid" (8.4, 5.2).
THE SKY: "gold" = sun at azimuth 215 (west-south-west), elevation 24: it lights the west front of the house and
  the plaza before it. He faces the door, so in the doorstep two-shot the sun is behind him and his face is in
  his own shade: C.doorstep_fill(s) is the film-local shadowless fill on his face, the SAME light at the SAME
  strength in dg04 and dg22. Decided on stills: with the fill (out/test/hello_scout_twoshot_dg04_hello_226.png,
  _dg22_eyes_1475.png) the face is lit and the indigo eye pixel reads blue; without it
  (hello_scout_twoshot_nofill_*.png) the face is a stop darker and the iris dark purple.
THE TWO-SHOT (CAMS["two_shot"], 40 mm f/2.4 from (8.8, -8.4, 1.35) aimed at (8.9, -5.4, 1.0), 3 blocks south of
  him), MEASURED ON RENDERS (out/test/hello_scout_gold_dg04_hello_226_zones.png, _dg22_eyes_1480_zones.png): his eyes
  at y 36 % standing (head top 16 %) and y 49 % crouched (chin 56 %, clear of the caption band 62-72 %), x 50 %, face
  178 px wide; a house front and its roofline behind him (the fixed line the crouch reads against); the child's head
  a soft pink block at the lower right (x 56-100 %, y 52-96 %). No lamp post within a third of the frame of his head.
  (Aimed at z 1.2 at first, the crouched chin was IN the caption band: "blue" and "eyes" drawn on his chin.)
  palette_check dg22@1480: every check passes (hero watcher x 33-77 %, y 32-56 %, 100 % inside the safe area).
THE TWO SHOTS THAT MUST MATCH: dg04_hello and dg22_eyes use CAMS["two_shot"] EXACTLY through _two_shot() (no
  override; the same handheld seed TWO_SHOT_SEED in both, since C.cam would otherwise derive it from the shot
  name), the same fill, the same light levels, Steve in dg04 and the watcher in dg22 on "watch_door" facing
  WATCH_YAW, the child on "hello_child". The roofline behind his head is what makes the crouch read: keep it.
HIS FACE: never readable before dg22 (dg15: out of focus, small or turned away; dg20: cropped at the shoulders;
  dg21: cropped at the chin, three-quarter from behind). In dg22 the white eyes must be unmistakable.
LIGHT: C.lights(s, "gold", near="door", radius=16).
"""
import math

from engine import breaking
from films import hello_common as HC

TWO_SHOT_SEED = 7          # the handheld of dg04 and dg22: the same seed, so the two frames match

# beat 15: ONE locked frame for the three jump cuts (CAMS "house_fronts" moved: lower and half a block further
# back, so the eaves of house_a sit in the top UI strip instead of across the top right)
FRONTS = dict(pos=(8.75, -15.0, 1.6), target=(9.7, 4.0, 1.4), lens=55.0, fstop=2.8)
FRONTS_SEED = 15
# beat 5: over his LEFT shoulder (the empty hand: the sword arm is on the other side), looking down at the child
NOD_CAM = dict(pos=(9.75, -4.3, 1.1), target=(9.2, -6.5, 0.3), lens=32.0, fstop=2.4,
               pos1=(9.73, -4.4, 1.09), target1=(9.2, -6.5, 0.3))
NOD_RUN = [(8.85, -7.0), (8.75, -8.0), (8.4, -11.2)]    # beat 5: the child runs off along the plaza, straight
#                                                         away from the lens, past the step's west face
# beat 20: low, close behind his right hip (north-west of him), looking past him at the door
WALK_CAM = dict(pos=(7.4, -4.7, 0.35), target=(9.6, -7.15, 0.45), lens=32.0, fstop=2.4,
                pos1=(7.48, -4.78, 0.36), target1=(9.6, -7.15, 0.45))
# beat 21: behind his right shoulder line, cropped at his chin, down on the child
CROUCH_CAM = dict(pos=(7.7, -5.0, 1.4), target=(9.0, -6.2, 0.7), lens=40.0, fstop=2.4,
                  pos1=(7.76, -5.1, 1.39), target1=(9.02, -6.22, 0.7))


def _head_point(c, frame, yaw_deg, pitch_deg=0.0, dist=3.0):
    """A look target that turns c's head `yaw_deg` from its body (+ = to its left) and `pitch_deg` up, at `frame`
    (the body standing still): for head turns that must read the same in every shot of one locked frame."""
    eye = c.eye_point(frame)
    yaw = c.yaw_at(frame) + math.radians(yaw_deg)
    return (eye.x + math.sin(yaw) * dist, eye.y - math.cos(yaw) * dist,
            eye.z + math.tan(math.radians(pitch_deg)) * dist)


def _two_shot(s, C):
    """The camera of beats 4 and 22, exactly, with its fill (call it in both)."""
    C.cam(s, "two_shot", seed=TWO_SHOT_SEED, handheld=0.004)
    C.doorstep_fill(s)


def dg04_hello(st, s, C, nar):
    """BEAT 4  "Every morning he crouched at me, twice."   frames 211-271 (61 f, 2.54 s), sky gold.
    MEASURED (stub): standing eyes y 36 %, crouched 49 % (see the module docstring); the child's head x 56-100 %:
    its nose shows only if its body is turned a little to the lens (three-quarter from behind).
    Words: Every 213, morning 219, he 227, crouched 230, at 241, me 244, twice 248. The pause after it is 0.45 s.

    STORY: Golden morning on the plaza at the foot of the doorstep. Steve has stepped outside and stands two blocks
    from the door, facing it, no helmet. The child has come down the step and stands at his feet. Close two-shot
    from child height, camera with its back to the door looking out: the child low in the foreground, three-quarter
    from behind with its nose showing, Steve's face filling the upper part of the frame, pitched down at the child,
    the white and dark blue eye pixels clearly readable, a roofline across the plaza as a fixed line behind his
    head. He drops into the sneak pose and stands again, twice, quickly. The last shot of the film uses this
    camera exactly. About 3 seconds.
    Cast: Steve, baby villager (narrator). Effects: player sneak pose, two quick crouches (six frames down and six
    up), fixed roofline behind his head so the drop reads, film-local neutral fill on his face, the same one as in
    beat 22.

    MUST BE SEEN, ON WHICH WORD
      frame 211       his head already moving (looking down at the child: Player.watch(f0, f1, child) snaps on f0)
      "morning" 219   his face: white and dark blue eye pixels readable
      "crouched" 230 .. "twice" 248   the two crouches (C.crouch_twice(steve, frame)): the second one ON "twice"
                      or just before it reads best (e.g. first down on 236, second down on 248); each drop moves
                      his eyes from y 36 % to 49 % against the roofline
      the whole shot  the child low in the foreground, nose showing (three-quarter from behind)
    SHARED: CAMS["two_shot"] + C.doorstep_fill(s) (via _two_shot), PLACES "watch_door" + HC.WATCH_YAW, "hello_child":
      EXACTLY as in dg22. Cast: C.actor("steve_iron", "dg"), C.actor("child", "dg").
    NEIGHBOURS: before, in03_bed (the room turned gold on "ended"); after, dg05_nod (reverse angle: the child nods
      and runs off).
    RISKS (story): blue eyes: the iris texel is #523d89, the trousers' indigo; under warm light it can read purple or
      dark: the near-neutral fill, the face at least a third of the frame wide. The sneak pose is a drop of a third
      of a block plus a lean and can vanish at phone size: the fixed roofline, six frames down and six up.
    STUB: Steve on watch_door looking at the child, two crouches from "crouched", the child looking up at him.
    """
    f0, f1 = s.frame_start, s.frame_end
    steve = C.actor("steve_iron", "dg")
    kid = C.actor("child", "dg")
    C.put(steve, f0, "watch_door", yaw=HC.WATCH_YAW)
    C.put(kid, f0, "hello_child", toward="watch_door")
    down = C.at(s, "twice") - 12                      # first crouch inside "crouched", the second ON "twice"
    steve.idle(f0, down - 1)                          # the game's idle arm bob and weight shift until the crouch
    steve.look_at(f0, C.P("watch_face"), ease=0)      # on the cut he still looks at the door ...
    steve.watch(f0, f1, kid, snap=False, ease=8)      # ... and his head comes down to the child by "morning"
    up = C.crouch_twice(steve, down)
    steve.idle(up + 1, f1 + 1)                        # alive again once he is up for good ...
    steve.track(up + 1, f1, kid, step=2, ease=1)      # ... but his head stays on the child (idle glances it away)
    kid.look_at(f0, steve, ease=0)
    kid.track(f0, f1, steve, step=2, ease=1)          # its head follows his eyes down and up
    st.use(s, steve, kid)
    _two_shot(s, C)
    s.focus(steve.head)
    st.hero(s, "steve", steve)
    C.lights(s, "gold", near="door", radius=16.0)


def dg05_nod(st, s, C, nar):
    """BEAT 5  "That meant hello."   frames 272-318 (47 f, 1.96 s), sky gold.
    Words: That 274, meant 279, hello 284. The pause after it is 1.0 s (about 290-318: the run off; the story turns).

    STORY: Reverse angle from beside Steve's hip, his arm and iron leg at the edge of the frame. The baby villager
    looks straight up at him and nods twice in answer, the only hello a villager can do, then turns and runs off
    along the plaza with its big head bobbing. About 2 seconds.
    Cast: baby villager (narrator), Steve (hip and arm only). Effects: baby villager nod twice (existing nod), baby
    villager run.

    MUST BE SEEN, ON WHICH WORD
      frame 272       the child looking straight up (the head tipped back, toward the lens side)
      "hello" 284     the two nods (C.hello_nod: 14 frames)
      about 298 .. 318    it turns and runs off along the plaza, head bobbing (Character.walk(run=True))
      the whole shot  his iron leg and arm at the frame edge, soft; nothing of his face
    SHARED: PLACES "watch_door", "hello_child", "run_off". Cast: C.actor("steve_iron", "dg") and
      C.actor("child", "dg") (both in dg04, the shot before: place them on f0, key nothing before it).
    NEIGHBOURS: before, dg04_hello; after, me06_leave (the gate: one day he walks into the woods). Hard cuts.
    MEASURED (stub, tools.hello_geo, projection and ray casts): on "hello" (284) the child's eyes x 47 %, y 53 %,
      but Steve's right arm is between the lens and its face (ray hits steve_iron_dg_arm_r 0.6 from the lens); by
      310 the child has run past the lens (x 231 %).
    STUB: the camera at his hip looks down at the child; it nods on "hello" and runs off toward run_off.
    """
    f0, f1 = s.frame_start, s.frame_end
    steve = C.actor("steve_iron", "dg")
    kid = C.actor("child", "dg")
    C.put(steve, f0, "watch_door", yaw=HC.WATCH_YAW)
    here = C.put(kid, f0, "hello_child", toward="watch_door")
    steve.idle(f0, f1 + 1)                            # his arm at the edge of the frame: the idle arm bob
    steve.watch(f0, f1, kid)
    kid.look_at(f0, steve, ease=0)                    # straight up at his face (and so up at the lens)
    end = C.hello_nod(kid, C.at(s, "hello"))
    kid.look_at(end - 2, None, ease=4)                # head level again, then away along the plaza
    kid.walk(end + 1, [here] + [C.stand(p) for p in NOD_RUN], run=True)
    st.use(s, steve, kid)
    C.cam(s, "two_shot", focus=kid.head, handheld=0.006, **NOD_CAM)
    st.hero(s, "child", kid)
    C.lights(s, "gold", near="door", radius=16.0)


AWAY, LOOK = (12.0, -8.0), (-70.0, 3.0)      # beat 15: the child's head (yaw from its body, pitch): to the lens
#                                             side and a little down (its face), and turned to its right as far as a
#                                             head goes (screen left, where he stands: its nose in profile)


def _fronts(st, s, C, place, turns):
    """Beat 15, one of its three jump cuts: the locked frame along the house fronts, the child on the step facing
    the lens, him at `place` in profile. turns = [(frame, AWAY or LOOK, ease)]: the child's head, from f0 (the
    first entry is its pose on the cut)."""
    f0 = s.frame_start
    kid = C.actor("child", "dg")
    p = HC.PLACES[place]
    C.watcher(s, "dg", place=place, yaw=HC.yaw_to(p, (p[0] + 1.0, p[1] + 0.3)))   # facing the fronts: profile
    C.put(kid, f0, "step_child", toward=FRONTS["pos"])
    for frame, (yaw, pitch), ease in turns:
        kid.look_at(frame, _head_point(kid, frame, yaw, pitch), ease=ease)
    st.use(s, kid)
    C.cam(s, "house_fronts", focus=kid.head, seed=FRONTS_SEED, handheld=0.002, **FRONTS)
    st.hero(s, "child", kid)
    C.lights(s, "gold", near="door", radius=16.0)


def dg15_a(st, s, C, nar):
    """BEAT 15, first jump  "Every time I look,"   frames 915-946 (32 f, 1.33 s), sky gold.
    Words: Every 917, time 924, I 932, look 936.

    MEASURED (stub, CAMS "house_fronts" 60 mm from (8.85, -14.6, 2.2)): the child's head x 58-82 %, y 46-58 % (seen
    from behind as staged: turn it), him at watch_far eyes x 28 %, y 46 % (face 31 px, profile), at watch_mid x 28 %,
    y 47 % (44 px), at watch_door x 37 %, y 54 % (about 120 px, profile: no eyes); all three clear of every block.
    Rendered: out/test/hello_scout_gold_dg15_a_936_zones.png (him small at house_f's corner, x 28 %), _dg15_c_975_
    zones.png (him at the corner, profile, no eyes). The underside of house_a's eaves crosses the top right of the
    frame (the lens stands just west of them): keep it as a frame or lower the lens.

    STORY (all of beat 15, "Every time I look, he is one house closer."): Late gold at the child's door. The baby
    villager, sharp in the lower foreground on the step, turns its head to look along the house fronts: he stands
    small and soft beyond the next house. The child looks away and back, jump cut in the same frame: he is at the
    next house, same pose. Once more: he is at the corner of the child's own house. About 3 seconds.
    Cast: baby villager (narrator), the watcher (background, out of focus). Effects: two jump cuts in a locked frame,
    each covered by the child's head turn, focus stays on the child.

    THE THREE SHOTS: dg15_a (he is at "watch_far", beyond the next house, at house_f's corner; the first plan's spot
      was inside house_f's wall and showed no figure), dg15_b (at "watch_mid", the next house),
      dg15_c (at "watch_door", the corner of the child's own house: where he stands in beats 19-22). ONE locked
      frame for all three (CAMS "house_fronts" is a start; it is not shared with another sequence); the cuts are on
      word boundaries (b before "he", c before "closer"); dg15_b is 0.88 s: short on purpose, the jumps quicken.
    MUST BE SEEN, ON WHICH WORD
      "look" 936      the child's head turned up the house fronts toward him (cheated toward the lens)
      each cut        the child's head turning AWAY just before it and BACK just after it (cover the jump)
      "closer" 968    him at the corner of the house, much bigger, still out of focus: his face NOT readable
    SHARED: PLACES "watch_door" + HC.WATCH_YAW in dg15_c (or his facing there may differ, see below), "step_child".
      Cast: C.actor("child", "dg"), C.actor("watcher", "dg") (the same instances in a, b, c: each placed on f0).
    NEIGHBOURS: before, me14_pyramid (the meadow); after, in16_empty (night, his bed empty). Hard cuts.
    RISKS (story): jump cuts in a locked frame can look like a render error: cover each jump with the child's head
      turning away and back, or cut to a one-second close-up of the child between the positions (not available:
      the cuts are fixed; use the head turn). HIS FACE: in all three he stands IN PROFILE, facing the house fronts
      (east): "same pose", and the camera from the south never sees his eyes. Scouted: facing the door (WATCH_YAW)
      at "watch_door" his face was frontal and readable at 4.6 blocks (out/test/hello_scout_gold_dg15_c_985.png,
      rendered before this change): never that. He turns to WATCH_YAW between beat 15 and beat 19 (other days).
      The camera is yours to change (it is not shared); keep the three places (they are shared with nobody either,
      but "watch_door" is his place in beats 19-22).
    STUB: the child on the step, him at watch_far, the locked frame.
    """
    f0 = s.frame_start
    _fronts(st, s, C, "watch_far", [(f0, AWAY, 0), (C.at(s, "time") + 2, LOOK, 6), (C.at(s, "look") + 4, AWAY, 6)])


def dg15_b(st, s, C, nar):
    """BEAT 15, second jump  "he is one house"   frames 947-967 (21 f, 0.88 s), sky gold.
    Words: he 949, is 951, one 954, house 961. (See dg15_a for the beat.) Him at "watch_mid" (the next house)."""
    f0 = s.frame_start
    _fronts(st, s, C, "watch_mid", [(f0, AWAY, 0), (f0 + 1, LOOK, 5), (C.at(s, "house"), AWAY, 6)])


def dg15_c(st, s, C, nar):
    """BEAT 15, third jump  "closer."   frames 968-997 (30 f, 1.25 s), sky gold.
    Words: closer 968. The pause after it is 0.8 s (to 997): he is at our corner; hold. (See dg15_a for the beat.)
    Him at "watch_door" (the corner of the child's own house: his place in beats 19-22)."""
    f0 = s.frame_start
    _fronts(st, s, C, "watch_door", [(f0, AWAY, 0), (f0 + 1, LOOK, 5)])


def dg20_walkup(st, s, C, nar):
    """BEAT 20  "So this morning I walked up to him and waited for my hello."   frames 1258-1357 (100 f, 4.17 s),
    sky gold. Words: So 1260, this 1264, morning 1270, I 1280, walked 1284, up 1293, to 1297, him 1300, and 1312,
    waited 1315, for 1324, my 1328, hello 1334. The pause after it is 0.5 s.

    STORY: Golden morning at the same door. One piece of rotten flesh spins on the step where the zombie stood. He has
    not moved from his spot. The door opens and the baby villager comes out, down the step, walking not running,
    up to him. Side-on long lens along the house wall: the child stops at his feet, tips its head all the way back
    and nods twice. He is cropped at the shoulders by the top of the frame. About 4.2 seconds.
    Cast: baby villager (narrator), the watcher (cropped at the shoulders). Effects: rotten flesh dropped item,
    spinning; door opening; nod twice.

    MUST BE SEEN, ON WHICH WORD
      frame 1258      the rotten flesh already spinning on the step (C.item("rotten_flesh", "dg"): place on f0 at
                      C.P("step"), animate(f0, f1 + 1)); he stands on watch_door (dead still)
      "morning" 1270  the door opens (C.v.door_open("house_a", frame, open=True)); the child steps out
      "walked" 1284 .. "him" 1300   it walks (not runs) down the step and up to him: the step's high half is z 1.0,
                      its low half z 0.5, the path -0.06 (give the walk those heights)
      "waited" 1315 .. "hello" 1334   it stops on "hello_child", head tipped all the way back, two nods
      the whole shot  he is cropped at the shoulders by the top of the frame: NO face
    SHARED: PLACES "watch_door" + HC.WATCH_YAW (he has not moved since dn19), "hello_child", "step", "door_in". Cast:
      C.actor("child", "dg2") (a twin: the "dg" child is placed elsewhere in dg15, fine either way),
      C.actor("watcher", "dg"), C.item("rotten_flesh", "dg").
    NEIGHBOURS: before, dn19_beside (night: their two backs, the zombie knocking); after, dg21_crouch (the same
      place: he crouches over the child). Hard cuts.
    SCOUTED: a camera from the south looking north along the wall (70 mm from (9.0, -12.6)) showed his face
      frontally (hello_scout_gold_dg20_walkup_1335.png): he faces the door. Side-on from the plaza (west), looking
      at the wall, he is seen from behind his right shoulder and the frame top crops him at the shoulders.
    MEASURED (stub, tools.hello_geo, projection and ray casts): at 1290 the walking child is outside the frame
      (eyes x 106 %, y 14 %), at "hello" 1334 its eyes x 65 %, y 35 %; his head is IN the frame at the top left (x
      0-30 %, y 0-17 %, 105 degrees off his nose: no eyes, but not cropped at the shoulders as the beat wants). At
      50 mm, 5 blocks away the frame is about 2 blocks wide: it cannot hold the door (y -7.5) and him (y -5.4)
      both; go wider or further than 7 blocks.
    STUB: the flesh spins on the step, the door opens, the child walks from door_in to hello_child and nods; a low
      side-on camera from the plaza looking east at the wall, the frame top at his shoulders.
    """
    f0, f1 = s.frame_start, s.frame_end
    him = C.watcher(s, "dg", place="watch_door")
    kid = C.actor("child", "dg2")
    flesh = C.item("rotten_flesh", "dg")
    step = C.P("step")
    flesh.place(f0, step)
    flesh.animate(f0, f1 + 1)
    breaking.crack(C.door, f0, -1, half="both")      # morning: whatever the night's knocking left is gone
    opens = C.at(s, "morning") - 2
    C.v.door_open("house_a", opens, open=True, frames=6)
    here = C.P("hello_child")
    start = (11.45, -7.42, 1.0)                       # inside, behind the shut door
    kid.place(f0, start, HC.yaw_to(start, (9.6, -7.3)))
    # out of the door (beside the flesh, not through it), onto the step's high half (z 1.0), down to its low half
    # (z 0.5), off its north edge to the ground and up to his feet: walking, not running
    route = [start, (10.0, -7.33, 1.0), (9.58, -7.24, 1.0), (9.47, -7.22, 0.5), (9.32, -7.1, 0.5),
             (9.28, -6.96, here[2]), here]
    end = kid.walk(opens + 1, route, speed=2.1)
    kid.look_at(end, him, ease=8)                     # the head tipped all the way back
    C.hello_nod(kid, max(end + 10, C.at(s, "hello")))
    st.use(s, kid, flesh)
    C.cam(s, "two_shot", focus=step, handheld=0.006, **WALK_CAM)
    s.focus(kid.head, at_s=(opens + 6 - 1) / 24.0, rack_s=0.4)   # from the spinning flesh to the child coming out
    st.hero(s, "flesh", flesh.sprite)
    st.hero(s, "child", kid)
    C.lights(s, "gold", near="door", radius=16.0)


def dg21_crouch(st, s, C, nar):
    """BEAT 21  "He crouched, once, and he stayed down."   frames 1358-1447 (90 f, 3.75 s), sky gold.
    Words: He 1360, crouched 1363, once 1374, and 1388, he 1390, stayed 1393, down 1401 (spoken a tenth slower than
    the rest of the film: speed 0.9; "down" ends on 1414). Then 1.5 s of silence (1415-1447): the story's "one
    second of silence"; nothing moves but the handheld.

    STORY: The same place, camera a little behind his shoulder line, the frame cropped at his chin. He sinks slowly
    into the sneak pose: the torso leans forward and his head comes down into the picture from above, seen
    three-quarter from behind, pitched down at the child. He is still taller than the child, so he ends leaning
    over it. He holds there. Neither of them moves. One second of silence. About 3.5 seconds.
    Cast: the watcher (three-quarter from behind), baby villager (narrator). Effects: player sneak pose, one slow
    crouch over a full second, held, no music.

    MUST BE SEEN, ON WHICH WORD
      "crouched" 1363 .. "once" 1374   the slow crouch begins (C.crouch_slow(him, frame, frames=24): the game snaps
                      this pose; the slow sink is the one deliberate untruth, it is his)
      "down" 1401     he is down, leaning over the child; his head entered the frame from above, three-quarter from
                      behind: the back and side of his head, never his eyes
      1415 .. 1447    the silence: hold; the child's head tipped up at him
    SHARED: PLACES "watch_door" + HC.WATCH_YAW, "hello_child". Cast: C.actor("watcher", "dg") (in dg20, the shot
      before: place on f0), C.actor("child", "dg2") (likewise).
    NEIGHBOURS: before, dg20_walkup; after, dg22_eyes (the two-shot of beat 4: the white eyes). Hard cuts.
    RISKS (story): the sneak pose can vanish at phone size: crop at his chin so the head ENTERS the picture as he
      sinks. A sneaking player is still taller than a baby villager: he leans over it, his head does not come level.
    MEASURED (stub, tools.hello_geo, projection and ray casts): at "down" 1401 the child's eyes x 49 %, y 53 %
      (face 236 px, 28 degrees off the lens); his head x -89..37 %, y 10-66 %, 128 degrees off his nose (from
      behind: no eyes).
    STUB: he crouches slowly from "once"; the child looks up; a camera behind his left shoulder looking down.
    """
    f0, f1 = s.frame_start, s.frame_end
    him = C.watcher(s, "dg", place="watch_door")
    kid = C.actor("child", "dg2")
    C.put(kid, f0, "hello_child", toward="watch_door")
    C.crouch_slow(him, C.at(s, "crouched") + 2, frames=28)    # sinks while "crouched, once" is spoken; down on
    #                                                           "stayed"; then nothing moves through the silence
    him.watch(f0, f1, kid)                            # his head on the child (the only part of him that turns)
    kid.look_at(f0, him, ease=0)
    kid.track(f0, f1, him, step=3, ease=1)            # its head follows his face down
    st.use(s, kid)
    C.cam(s, "two_shot", focus=kid.head, handheld=0.004, **CROUCH_CAM)
    st.hero(s, "child", kid)
    C.lights(s, "gold", near="door", radius=16.0)


def dg22_eyes(st, s, C, nar):
    """BEAT 22  "The player had blue eyes."   frames 1448-1544 (97 f, 4.04 s), sky gold. The film's last shot.
    Words: The 1450, player 1453, had 1463, blue 1467, eyes 1475 (speed 0.9, like beat 21; "eyes" ends on 1489).
    Then the hold on the white eyes, 1490-1538 (2.0 s), and the CUT TO BLACK: the encoder blacks out the last six
    frames, 1539-1544 (films/hello.py END_BLACK); the Reel then loops to frame 1.

    STORY: The camera of beat 4, exactly, the same roofline behind his head. His face, turned down to the child and
    the lens, fills the upper part of the frame: where the blue was, both pixels of each eye are blank white,
    faintly glowing. He stays down. Hold two seconds on the two of them, the child's big head below the white eyes,
    then cut to black. About 4 seconds.
    Cast: the watcher (face, first time seen), baby villager (narrator). Effects: white-eyed Steve skin, eyes
    slightly emissive in this shot only, same camera and same fill light as beat 4, two-second hold, then cut to
    black.

    MUST BE SEEN, ON WHICH WORD
      frame 1448      already down (C.crouch_held on f0), his face to the child and the lens; the white eyes
      "blue" 1467 .. "eyes" 1475   the white eyes unmistakable (HC.EYE_GLOW; out/test/hello_scout_gold_dg22_eyes_1480)
      1490 .. 1538    hold; nothing moves but the handheld and, at most, a tiny head settle; 1539-1544 black
    SHARED: _two_shot (CAMS["two_shot"] + the doorstep fill: EXACTLY dg04's), "watch_door" + HC.WATCH_YAW,
      "hello_child". Cast: C.actor("watcher_eyes", "dg") (the white-eyed skin: THIS SHOT ONLY),
      C.actor("child", "dg2") (in dg21: place on f0).
    NEIGHBOURS: before, dg21_crouch; after, nothing (the film ends on frame 1544, black from 1539).
    RISKS (story): never trim the second of silence before this line or the two-second hold after it (kept: 1.5 s
      pause; the tail is 2.3 s, of which the last 0.25 s is black).
    STUB: the white-eyed watcher crouched on watch_door, looking down at the child, the two-shot camera.
    """
    f0, f1 = s.frame_start, s.frame_end
    him = C.watcher(s, "dg", place="watch_door", role="watcher_eyes")
    kid = C.actor("child", "dg2")
    C.put(kid, f0, "hello_child", toward="watch_door")
    C.crouch_held(him, f0)
    kid.look_at(f0, him, ease=0)
    him.watch(f0, f1, kid)
    st.use(s, kid)
    _two_shot(s, C)
    s.focus(him.head)
    st.hero(s, "watcher", him)
    C.lights(s, "gold", near="door", radius=16.0)
