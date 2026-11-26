"""Two Apples, sequence EVENING: dad's bedroom at dusk and the stairwell down to the hall. Beats 4, 5 and 6 (shots
ev04_bed, ev05_stop, ev06_stairs), sky "dusk". One function per shot; the contract is in films/twoapples_common.py
(tags "ev...", C.actor, C.cam, C.lights, st.use / st.hero).

THE PLACES (films/twoapples_set.py "DAD'S HOUSE" and "THE STAIRWELL"):
  DAD'S HOUSE = house_a (the roomiest vanilla house). Its bed wing x 15..19, y -13..-9 (floor z 1): dad's bed
  house_a_bed_2 dyed RED at (18..19, -10), pillow east; the white bed_1 south of it at y -12; the wall torch between
  the pillows (19, -11, 2) is the key; the window in the north wall right behind the red bed (17..18, -8, 2) and the
  gable pane over the bed wall (20, -11, 4) show the indigo dusk; the oak door (10, -8) at the far west end of the
  house (the lens side in ev05; never opened in this film). Anchors: ta_kid_bed_foot (18.5, -9.5, 1.56) facing west
  (on the red bed's foot, the mattress top), ta_kid_bed_door (the same spot, facing the door), house_a_center.
  THE STAIRWELL: ten stone stairs x 4..5 from y 0 down to y -9, stone walls turning to deepslate, wall torches at
  y -2, -3, -6, -9, the landing y -10 (deepslate bricks, floor F = -10). Path ug_down (with the steps' heights).
THE SKY: "dusk" (the window and the gable pane show the indigo; nothing else of the sky is seen).
LIGHT: ev04, ev05 C.lights(s, "room") + C.glow(s, "room_cool") (house_a's torches x 1.5, its own fill OFF: with it the
  room was a flat evenly lit box; the weak cool fill keeps the child's skin under the palette's 0.52); ev06
  C.lights(s, "stairs") (no village light, every underground torch at 1).
TAGS: child_ev (ev04, ev05: placed on each shot's first frame; ev04 may pre-roll it: in no shot before), child_ev6
  (ev06: pre-rolled, a twin: child_ev is in ev05). A new twin: any further "ev..." tag.
SHARED: none of the cameras (each is its shot's own; the stubs use the set's b04, b05, b06).
"""
import math

from engine import underground as U
from films import twoapples_common as TC


def ev04_bed(st, s, C, nar):
    """BEAT 4  "That evening, I jumped on dad's bed."
    frames 229-292 (64 f, 2.67 s), sky dusk, the wall shut. Words: That 231, evening 235, I 247, jumped 251, on 261,
    dad's 265, bed 275. The last word is spoken until 284; after it 8 frames to the cut.

    STORY: Inside the house, one wall torch, indigo dusk in the window. The baby villager bounces up and down on the
    red bed, seen lengthwise from beside its foot. The pillow end is empty. Low camera, the bed fills the bottom third.
    Cast: Baby villager (narrator). Effects: red hero bed (the existing house bed), bounce animation, wall torch,
    window with dusk sky.

    MUST BE SEEN, ON WHICH WORD
      frame 1         the child already in the air (the bounce pre-rolled: child_ev is in no shot before), the red
                      bed lengthwise with its EMPTY pillow, the indigo window
      "jumped"        a jump at its top, his head in the safe area (y 14-60 %)
      "dad's bed"     the empty pillow end readable (dad's)
    SHARED: none (the set's b04: low beyond the red bed's foot looking along it to the pillow, 22 mm f/2.6).
      Place: ta_kid_bed_foot. Cast: C.actor("child", "ev").
    NEIGHBOURS: before, sq03_push (the square at dusk, dad going down); after, ev05_stop (the same room, wider, he
      has stopped).
    NOTES (engine/underground.py bed_bounce): the game's JumpOnBed: jumps=6 = two jumps 36 frames apart with the bed's
      little bounces between; jumps=(6, 6) runs it twice (a film choice). He looks at the lens in the set's still:
      the director chooses (a jump that looks at the lens is a child playing to us; at the pillow it is dad's empty
      place).
    MEASURED (the set's still out/test/twoapples_set_b04_bed.png: the top of the first jump): head x 49 / y 24, the bed
      (red blanket, the empty pillow at its far end) fills the bottom third, the wall torch right of him, the gable
      pane with the indigo dusk top right (x 74 / y 24). Skin s 0.50 (it needed ROOM_COOL: 0.53 without it), stone
      G/R 0.93.
    STUB NOW: the set's staging, the bounce begun BOUNCE_PRE frames before the shot. Hero: the child.
    """
    f0 = s.frame_start
    kid = C.actor("child", "ev")
    spot = C.A["ta_kid_bed_foot"]
    fb = f0 - BOUNCE_PRE
    C.put(kid, fb, "ta_kid_bed_foot")
    U.bed_bounce(kid, fb, spot, jumps=6)
    cam = C.camera_spec("set:b04")
    kid.look_at(fb, cam["pos"], ease=0)
    st.use(s, kid)
    C.cam(s, "set:b04", focus=kid.head, handheld=0.006)
    st.hero(s, "child", kid)
    C.lights(s, "room")
    C.glow(s, "room_cool")


BOUNCE_PRE = 6         # ev04: the bounce begins this many frames before the shot (he is in the air on frame 1)


def ev05_stop(st, s, C, nar):
    """BEAT 5  "Nobody told me to stop."
    frames 293-350 (58 f, 2.42 s), sky dusk, the wall shut. Words: Nobody 295, told 308, me 315, to 318, stop 321. The
    last word is spoken until 334; after it 16 frames to the cut.

    STORY: Same room, wider and locked off, the closed door on the lens side so his face is three-quarter to us. He has
    stopped. He stands on the bed, very small, facing the door. Nothing moves. Hold.
    Cast: Baby villager (narrator). Effects: closed oak door, locked-off camera, stillness.

    MUST BE SEEN, ON WHICH WORD
      the whole shot  the child small on the red bed's foot, three-quarter to the lens, facing the closed door (behind
                      the lens's left); NOTHING MOVES (the story's hold; the only life is the handheld's slow float:
                      the rule "something moving on frame 1" is met by the camera alone here, on purpose)
      "stop" .. end   the hold (the pause after the line is 0.8 s: the story turns, he goes down)
    SHARED: none (the set's b05: locked off from the west wing's south-west corner, 26 mm f/3.2). Place:
      ta_kid_bed_door (the same spot as ev04, facing the door). Cast: C.actor("child", "ev") (in ev04 before: placed
      on frame 1, the cut ends the bounce).
    NEIGHBOURS: before, ev04_bed; after, ev06_stairs (he runs down).
    MEASURED (the set's still out/test/twoapples_set_b05_still.png): wide and torch-lit; the child small and
      three-quarter, facing the door (head x 48 / y 48, 38 degrees off the lens), the bed-wall torch beside him, the
      north window and the gable pane indigo. Stone G/R 0.94.
    STUB NOW: the set's staging, locked, handheld 0.004. Hero: the child.
    """
    f0 = s.frame_start
    kid = C.actor("child", "ev")
    C.put(kid, f0, "ta_kid_bed_door")
    kid.look_at(f0, C.P("door_in"), ease=0)
    st.use(s, kid)
    C.cam(s, "set:b05", focus=kid.head, handheld=0.004)
    st.hero(s, "child", kid)
    C.lights(s, "room")
    C.glow(s, "room_cool")


def ev06_stairs(st, s, C, nar):
    """BEAT 6  "So I went down to find him."
    frames 351-401 (51 f, 2.12 s), sky dusk, the wall shut. Words: So 353, I 359, went 363, down 368, to 374, find
    377, him 386. The last word is spoken until 392; after it 9 frames to the cut.

    STORY: Inside the stairwell: one long straight flight, stone turning to deepslate, wall torches. The baby villager
    runs down away from the camera, big head bobbing, tiny in the frame, seen from high behind, his head cheated toward
    a wall torch so the nose reads. This is the last time we see him as a villager until the flashback in beat
    twenty-two.
    Cast: Baby villager (narrator). Effects: stairwell with wall torches, stone to deepslate transition, baby run cycle.

    MUST BE SEEN, ON WHICH WORD
      frame 1         the child already running down (a twin, pre-rolled: child_ev is in ev05 before)
      "went down"     the head turned to the west wall's torch as he passes it (the nose reads: side of the face)
      "find him"      tiny near the deepslate landing; the flight with its torches
    SHARED: none (the set's b06: high behind at the top of the flight, 26 mm f/4). Path ug_down from its 2nd point.
      Cast: C.actor("child", "ev6").
    NEIGHBOURS: before, ev05_stop (the bedroom); after, tu07_hall (the hall from above, under the ground: the light
      changes to "under").
    NOTES: the sky is "dusk" here (the set's still): the flight's top has sky light from the mouth.
    MEASURED (the set's still out/test/twoapples_set_b06_stairwell.png, passing the torch): tiny (head x 50 / y 48),
      his head turned to the torch; stone walls, four torches, the deepslate landing at the bottom; skin s 0.48. The
      nose is a few pixels at 540x960 (engine note).
    MEASURED BY THE LEAD (tools/twoapples_geo on the stub; the sheet tile out/test/twoapples_shots_sheet.png): ug_down
      starts at y 1.0, BEHIND the lens (y -0.7): with a 4-frame pre-roll his head was a blurred block under the camera
      on frame 1 (y 54-71 %, in the caption band; out/test/twoapples_scout_ev06_stairs_358_zones.png). With RUN_PRE 28:
      head y 49-60 % on frame 351 (4.4 blocks away, from behind: 161 degrees off the lens), eyes y 49 % on "down" (368,
      23 px), 44 % at the end (401, 13 px, 13 blocks: on the landing). His head turned to the torch is 110-115
      degrees off the lens: at the edge of the blank-box limit (116): cheat the torch look further toward the lens.
    STUB NOW: the set's staging pre-rolled RUN_PRE frames (run 4.4 blocks/s), his head tracking the torch. Hero: the
      child.
    """
    f0, f1 = s.frame_start, s.frame_end
    kid = C.actor("child", "ev6")
    path = C.paths["ug_down"]
    fr = f0 - RUN_PRE
    kid.place(fr, path[1], math.pi)
    kid.walk(fr, path[1:], speed=4.4, run=True)
    torch = (U.LIGHTS[2][0][0] + 0.1, U.LIGHTS[2][0][1] + 0.5, U.LIGHTS[2][0][2] + 0.6)
    kid.look_at(fr, torch, ease=0)
    kid.track(fr, f1, torch, step=2, ease=4)
    st.use(s, kid)
    C.cam(s, "set:b06", focus=kid.head, handheld=0.006)
    st.hero(s, "child", kid)
    C.lights(s, "stairs")


RUN_PRE = 28           # ev06: the run begins this many frames before the shot (he starts at ug_down[1], y 1.0, BEHIND
#                        the lens at y -0.7: with 4 frames his head was a blurred block under the camera on frame 1)
