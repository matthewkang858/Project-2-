"""Two Apples, sequence TURN: the trading hall in front of dad's cell; the look down into the cells, the lever, the
three blows that turn dad. Beats 7, 9, 10, 11, 12 (shots tu07_hall, tu09_lever, tu10_hug, tu11_hard, tu12_green), sky
"under". One function per shot; the contract is in films/twoapples_common.py (tags "tu...", C.actor, C.cam, C.lights,
st.use / st.hero). bx08_slot (the box sequence) is cut in between tu07 and tu09.

THE PLACE (films/twoapples_set.py "THE HALL", engine/underground.py "THE SET"): the aisle x -8..19, y -12..-11 (2
  wide), deepslate walls and ceiling, deepslate-brick floor (F = -10); the cells face north into it from y -14, ONE
  BLOCK WIDE AND TWO HIGH under a stone cap at F+2, the front row (y -13) one long counter: a job block at the floor, a
  window at face height (F+1), iron bars above (F+2): farmer x 7 (composter), fletcher x 9 (fletching table), cleric
  x 11 (brewing stand), the 2-wide pier x 12..13 (a window over it too), DAD x 14 (lectern), the end pier x 15 with
  the LEVER on its north face (15, -12, F+1). Dad's back wall = the piston door (14, -15, F / F+1): two stone blocks
  that slide west into the wall; behind it the zombie box. Torches: over the farmer / fletcher (9, -11, F+1), the
  hanging lantern (10, -11, F+2), the dad torch (14, -11, F+1) facing his cell, the stair foot (5, -10, F+1).
  Anchors: ug_cell_<farmer|fletcher|cleric|dad> (dad 0.18 west of his cell's middle: a strip of the doorway shows
  beside his robe from the east), ug_aisle_<name> (in front of each cell), ug_lever_stand (a block north of the lever,
  facing south), ug_lever_target, ug_door_target (the middle of the doorway).
THE SKY: "under" (no sun, no sky fill: the baked block light at 0.45 of the game's and the torches).
LIGHT: C.lights(s, "hall") (it st.use's the lever: every shot here sees the end pier's north face or does not care);
  tu07 also C.glow(s, "down_fill") (the pockets with the ceiling off).
THE WALL PLAN: shut on tu07's frames; tu09 OPENS it (C.wall_open with Steve's flip: the only shot here that moves
  it); open in tu10, tu11, tu12 (the black doorway beside dad's robe: the attacker is never in the picture).
DAD: a villager (C.actor("dad", "tu")) to tu12's last blow, where U.infect_in_cell swaps him for the zombie villager
  (C.actor("zdad", "tu")) on that frame, no effect, arms out (aggro). His head stays FRONT (the story: "Dad keeps
  facing front", "Dad's eyes stay front", "still looking straight ahead"): only tu07 tips it up at the lens.
  Blows in his capped cell: U.hurt_in_cell / U.infect_in_cell only (undead.hurt with an attacker hops through the
  cap); a blow under 12 frames after the last is dropped (the game's cool-down); during the 12 red frames
  Stage.hero finds his head hidden (stills before or after a blow).
TAGS: dad_tu, zdad_tu, farmer_tu, fletcher_tu, cleric_tu (C.cells(s, "tu"): placed on each shot's first frame),
  steve_tu09. A new twin: any further "tu..." tag.
SHARED: none of the cameras (each is its shot's own; the stubs use the set's b07, b09, b10, b11, b12).
"""
from engine import underground as U
from films import twoapples_common as TC


def tu07_hall(st, s, C, nar):
    """BEAT 7  "It's a trading hall, and dad has the last tiny room."
    frames 402-489 (88 f, 3.67 s), sky under, the wall shut. Words: It's 404, a 407, trading 409, hall 418, and 434,
    dad 437, has 446, the 450, last 452, tiny 461, room 473. The last word is spoken until 482; after it 7 frames to
    the cut.

    STORY: A new angle on the hall, not the counter ride of the earlier films: the ceiling is off for the camera and we
    look steeply down along the row. Each cell is a one-block pocket with a hat in it: the farmer's straw hat, the
    fletcher's feathered cap, the cleric's bare head, each behind his job block. The camera slides to the last pocket:
    the red book hat. Dad alone tips his head back and looks up at us. Behind his cell sits one more square of stone,
    sealed with a lid. A lever is on the front pier of his cell. No narrator in frame from here on.
    Cast: Farmer, Fletcher, Cleric, Dad (librarian). Effects: ceiling removed for the camera, one-block cells with
    piers and iron bars, composter, fletching table, brewing stand, lectern, hanging lantern, lever on the pier of
    dad's cell, sealed stone box behind dad's cell, dad's head pitched up to its stop.

    MUST BE SEEN, ON WHICH WORD
      frame 1         the camera already sliding (ease_out: at speed), over the farmer's pocket: the straw hat
      "trading hall"  the hats in their pockets, the job blocks
      "dad"           the red book hat coming into the frame
      "last tiny room" dad tips his head back and looks up at us; the box's smooth stone lid behind his cell; the lever
    SHARED: none (the set's b07, see-through "ug_ceiling" + "ug_caps": C.cam keys them). Cast: C.cells(s, "tu").
    NEIGHBOURS: before, ev06_stairs (the stairwell at dusk); after, bx08_slot (the back corner, the floor).
    RISKS (story): the look down may read as a model (wall tops, bars from above, the dark beyond the set; faces under
      hats except dad's). Fallback: the proven ride along the counter, but from a child's eye height, about 0.7 block
      above the floor, looking up at the faces over their job blocks. The set builder's note: a low camera west of
      x 6.5 loses the farmer's window behind the front row's solid pier at x 6: such a ride starts east of it. NOT
      BUILT; a 45-degree look from above the aisle was tried and dropped (the front row's top bars cross every face).
    MEASURED (the set's stills out/test/twoapples_set_b07_down_start.png, _b07_down.png): hats in the pockets; dad's
      face looks up at us at the end (x 54 / y 50), the box lid and the lever (x 35 / y 74: under the caption band).
      DOWN_FILL (120 W) lifts the pockets (the start still was rendered before it: darker). It still reads partly as a
      cutaway model (weak pass).
    STUB NOW: the set's staging; dad's head front, then up at the lens's end position from "last". Hero: dad.
    """
    A = C.A
    cells = C.cells(s, "tu")
    dad = cells["dad"]
    dad.look_at(C.at(s, "last") - DAD_LOOK_LEAD, TU07_RIDE["pos1"], ease=10)     # he looks down at the child
    C.cam_keys(s, None, [(s.frame_start + d, u) for d, u in TU07_KEYS], handheld=0.004, **TU07_RIDE)
    C.rack(s, dad, C.at(s, "dad"), frames=12)          # the windows sharp on the ride, then dad from "dad"
    st.hero(s, "dad", dad)
    C.lights(s, "hall")


# tu07: THE COUNTER RIDE AT A CHILD'S EYE HEIGHT (the story's fallback, the lead's choice: the look down read as a
# cutaway model in every look at it). East along the aisle 0.75 above the floor, looking up through the windows at
# the faces over their job blocks; from east of the solid pier at x 6 (the set builder's note) to dad's window.
TU07_RIDE = dict(pos=(6.9, -11.0, TC.F + 0.75), target=(8.6, -13.6, TC.F + 1.45),
                 pos1=(13.05, -11.05, TC.F + 0.78), target1=(14.25, -13.4, TC.F + 1.5), lens=24.0, fstop=2.8)
TU07_KEYS = ((0, 0.0), (35, 0.62), (50, 0.86), (68, 0.985), (87, 1.0))   # (frames into the shot, share of the ride)
DAD_LOOK_LEAD = 4      # tu07: dad's head turns down to the lens this many frames before "last"


def tu09_lever(st, s, C, nar):
    """BEAT 9  "He pulls a lever, and dad's wall opens."
    frames 551-623 (73 f, 3.04 s), sky under, the wall shut -> open. Words: He 553, pulls 556, a 563, lever 566, and
    579, dad's 583, wall 594, opens 602. The last word is spoken until 615; after it 8 frames to the cut.

    STORY: At the front of dad's cell. Close on Steve's hand flipping the lever on the stone pier. Focus pulls past
    dad's shoulder to the back of the cell: the two stone blocks behind him jerk aside on sticky pistons and a black
    doorway stands open. Dad keeps facing front.
    Cast: Steve (the player, hand and arm), Dad (librarian). Effects: lever switching, two sticky pistons pulling two
    wall blocks sideways into the end wall, rack focus, black doorway behind dad.

    MUST BE SEEN, ON WHICH WORD
      frame 1         close on the lever (the handheld; Steve's arm comes in from the left for the swing)
      "lever"         the lever flips (sync="hand": on the frame his hand is nearest its handle); the swing starts
                      SWING_LEAD frames before the word, so that the wall (12 frames after the flip) opens on about
                      "wall" (with the swing on "pulls" it opened 1.3 s before "opens" was said)
      "dad's wall"    the pan right past dad's shoulder onto the back wall, the focus pulling there
      "opens"         the wall jerks aside (12 frames after the flip: repeater 4), the doorway BLACK beside his robe;
                      dad facing front
    THE WALL: THIS SHOT OPENS IT (films/twoapples.py WALL): C.wall_open(frame, who=s.name, player=steve, repeater=4,
      sync="hand"); it stays open to cu15.
    SHARED: none (the set's b09: C.cam_hold holds on the lever until the flip, then pans to the wall by the opening).
      Places: ug_lever_stand (Steve, facing south: out of the frame but for his right arm), ug_lever_target,
      ug_door_target. Cast: C.cells(s, "tu"), C.actor("steve", "tu09").
    NEIGHBOURS: before, bx08_slot (the slot, the hands); after, tu10_hug (dad hit from behind).
    NOTES (engine): redstone.flip_by(reach=True): the hand still misses the handle by 0.25-0.31 (it reads in motion:
      the swing smears across the lever); the wall opens 12 frames after the flip, when the pan has arrived; the
      doorway is black on the open frames (DOOR_KEEPS_DARK: mean 11 / 255 against the wall's 83).
    MEASURED (the set's stills out/test/twoapples_set_b09_lever_hand.png, _b09_lever.png): Steve's arm on the lever
      (x 39 / y 45); at the end the doorway open and black beside dad's robe (dad x 72 / y 32). Skin s 0.47.
    MEASURED BY THE LEAD (out/test/twoapples_scout_tu09_lever_592_zones.png, on "wall"): the pan has arrived, the
      doorway stands open and BLACK at the left of dad's robe, dad frontal (eyes x 72 / y 32 at 602, 147 px, 2 degrees
      off the lens); Steve is out of the frame (his arm is in it only around the flip).
    STUB NOW: the swing starts SWING_LEAD frames before "lever". Hero: dad.
    """
    f0 = s.frame_start
    A = C.A
    cells = C.cells(s, "tu")
    steve = C.actor("steve", "tu09")
    C.put(steve, f0, "ug_lever_stand")
    st.use(s, steve)
    swing = max(f0, C.at(s, "lever") - SWING_LEAD)
    r = C.wall_open(swing, who=s.name, player=steve, repeater=WALL_DELAY, sync="hand")
    C.memo["tu_lever"] = r
    opened = r["open"] if r else swing + 36
    pan = C.at(s, "dad's")
    C.cam_hold(s, "set:b09", pan, frame_end=opened - 1, focus=A["ug_lever_target"])
    C.rack(s, A["ug_door_target"], pan, frames=12)
    st.hero(s, "dad", cells["dad"])
    C.lights(s, "hall")


SWING_LEAD = 4         # tu09: Steve's swing starts this many frames before "lever" (the flip lands on it)
WALL_DELAY = 14        # tu09: the hidden repeater delay in redstone ticks (engine.underground open_wall `repeater`:
#                        2 game ticks a step; 14 = a chain of four repeaters at 4 + 4 + 4 + 2 behind the pier, legal
#                        in the game): the pistons move on "opens", 36 frames after the flip on "lever" (with 4 they
#                        moved on "and", 25 frames before "opens", after a 9-frame whip pan: the technical check)


def tu10_hug(st, s, C, nar):
    """BEAT 10  "The zombie runs in and hugs him."
    frames 624-675 (52 f, 2.17 s), sky under, the wall open. Words: The 626, zombie 628, runs 640, in 649, and 654,
    hugs 656, him 665. The last word is spoken until 669; after it 6 frames to the cut.

    STORY: From the aisle, low and a little to one side, the lectern filling the bottom third. Dad is hit from behind:
    he flashes red and hops forward against the lectern, the short hop of a mob struck in a one-block cell. The
    attacker is not in the picture at all: beside his robe there is only the black doorway. Dad's eyes stay front.
    Cast: Dad (librarian). Effects: red hurt flash, short knock-back hop toward the lectern, lectern as foreground,
    attacker not rendered in this shot.

    MUST BE SEEN, ON WHICH WORD
      frame 1 .. "runs in"   dad facing front, the BLACK doorway beside his robe (the wall is open: WALL)
      "hugs"          the blow: red for 12 frames, the jolt (0.05 up for one tick under the cap, 0.05 forward against
                      the lectern: U.hurt_in_cell); his eyes stay front
      NEVER           the attacker (not built, not in the shot); a hop through the cap
    SHARED: none (the set's b10: low and east of the cell axis, 28 mm f/2.8). Cast: C.cells(s, "tu").
    NEIGHBOURS: before, tu09_lever; after, tu11_hard (the portrait, the second blow).
    RISKS (story): the black doorway must stay black at phone size; the attacker is simply not rendered.
    MEASURED (the set's still out/test/twoapples_set_b10_hit.png, just before the blow): dad x 61 / y 36, the black
      doorway beside him x 44 / y 53, the lectern in the bottom third. The engine: dad's head moves 1.0-1.3 % of the
      frame height in the jolt.
    STUB NOW: the blow on "hugs". A slow push would give frame 1 its life: the stub has the handheld. Hero: dad.
    """
    cells = C.cells(s, "tu")
    dad = cells["dad"]
    U.hurt_in_cell(dad, C.at(s, "hugs"), attacker=C.A["ug_door_target"])
    C.cam(s, "set:b10", focus=dad.head, handheld=0.008)
    st.hero(s, "dad", dad)
    C.lights(s, "hall")


def tu11_hard(st, s, C, nar):
    """BEAT 11  "On Hard, we always turn."
    frames 676-725 (50 f, 2.08 s), sky under, the wall open. Words: On 678, Hard 682, we 694, always 696, turn 706.
    The last word is spoken until 717; after it 8 frames to the cut.

    STORY: Tight three-quarter portrait of dad: big nose, brow, book hat. A second blow: the red flash again, a small
    jolt. His colours come back. He is still looking straight ahead. He does not fall and there is no smoke.
    Cast: Dad (librarian). Effects: second red hurt flash, portrait lens, shallow focus.

    MUST BE SEEN, ON WHICH WORD
      frame 1         the portrait (nose, brow, book hat), the black doorway behind his head
      "Hard"          the second blow: red, the jolt (U.hurt_in_cell, 12+ frames after tu10's)
      "turn"          his own colours back; still looking straight ahead
    SHARED: none (the set's b11: 40 mm f/2.0 from the aisle east of his axis). Cast: C.cells(s, "tu").
    NEIGHBOURS: before, tu10_hug; after, tu12_green (the third blow: the swap).
    RISKS (story): "On Hard" heard aloud is two short syllables (only the capital in the caption says difficulty);
      the narration is committed as written.
    MEASURED (the set's still out/test/twoapples_set_b11_portrait.png): tight portrait x 48 / y 42, the black doorway
      behind his head; the engine: the jolt moves his head 2.2 % of the frame height (45-52 %).
    STUB NOW: the blow on "Hard". Hero: dad.
    """
    cells = C.cells(s, "tu")
    dad = cells["dad"]
    U.hurt_in_cell(dad, C.at(s, "hard"), attacker=C.A["ug_door_target"])
    C.cam(s, "set:b11", focus=dad.head, handheld=0.006)
    st.hero(s, "dad", dad)
    C.lights(s, "hall")


def tu12_green(st, s, C, nar):
    """BEAT 12  "Dad goes green under his hat."
    frames 726-780 (55 f, 2.29 s), sky under, the wall open. Words: Dad 728, goes 736, green 743, under 752, his 757,
    hat 760. The last word is spoken until 769; after it 11 frames to the cut.

    STORY: Frontal, symmetrical, locked off on the whole cell. One more jolt, and on that frame dad is simply replaced
    where he stands, exactly as in the game: a zombie villager in the very same book hat and robe, green face, arms out
    over the lectern, finishing the little hop. No particles. The black doorway is still open behind him. Hold on the
    hat.
    Cast: Dad (librarian), Dad as zombie villager (librarian). Effects: instant villager to zombie villager swap on
    the blow, no effect, arms-forward zombie pose, locked-off camera.

    MUST BE SEEN, ON WHICH WORD
      frame 1 .. "goes"   dad (the villager) frontal in the whole cell
      "green"         the swap ON the blow frame: U.infect_in_cell(dad, zdad, frame) and zdad.aggro(frame, ease=0):
                      green face, arms out over the lectern, the jolt finished by the zombie villager
      "hat" .. end    hold on the hat (the pause after the line is 0.6 s); the doorway still open behind him (a strip
                      at his side: dead ahead he hides most of it)
    SHARED: none (the set's b12: frontal, 26 mm f/3.2, locked off: handheld only). Cast: C.cells(s, "tu"),
      C.actor("zdad", "tu").
    NEIGHBOURS: before, tu11_hard; after, cu13_potion (the cure sequence: zombie dad from its first frame).
    RISKS (story): a viewer who does not play may take the instant swap for a glitch. Fallback: make the swap on the
      cut from beat 11 to beat 12 (this shot would then open on zombie dad, finishing the hop).
    MEASURED (the set's still out/test/twoapples_set_b12_turn.png, after the swap): frontal and centred; zombie dad
      with arms out over the lectern (x 58 / y 33); the engine: his head moves 1.0 % of the frame in the jolt.
    STUB NOW: the swap on "green". Heroes: dad, then zombie dad (st.hero for both; the palette check reads the one
      visible on its frame).
    """
    cells = C.cells(s, "tu")
    dad = cells["dad"]
    zdad = C.actor("zdad", "tu")
    f = C.at(s, "green")
    U.infect_in_cell(dad, zdad, f, attacker=C.A["ug_door_target"])
    zdad.aggro(f, ease=0)
    st.use(s, zdad)
    C.cam(s, "set:b12", focus=dad.head, handheld=0.004)
    st.hero(s, "dad", dad)                         # the villager until "green" (hidden from the swap)
    st.hero(s, "zombie dad", zdad)                 # the zombie villager from the swap (hidden before it)
    C.lights(s, "hall")
