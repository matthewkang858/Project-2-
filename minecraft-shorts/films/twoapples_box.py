"""Two Apples, sequence BOX: everything the twist rests on. The slot of the zombie box seen from the floor of the back
corner (twice: with the hands, then black), the flashback at the foot of the stairs (the zombie finds the child; the
last blow), and the inside of the box. Beats 8, 21, 22, 23, 24 (shots bx08_slot, bx21_small, bx22_found, bx23_kill,
bx24_kept), sky "under". One function per shot; the contract is in films/twoapples_common.py (tags "bx...", C.actor,
C.cam, C.lights, st.use / st.hero). bx08 is cut in between tu07 and tu09 (the order of the film).

THE PLACES (films/twoapples_set.py "THE BACK CORNER AND THE BOX", "THE HALL"):
  THE BACK CORNER: the leg x 16..19, y -17..-13, 4 wide, one block past the slot, its one torch on the east wall
  (19, -14, F+1), 4 blocks from the slot. THE ZOMBIE BOX (14, -16): 1 x 1 x 2 inside, stone, a smooth stone lid at
  F+2, its only opening the SLOT of iron bars at floor level in its east wall (15, -16, F), black inside (BOX_SEALED:
  the game would light it to about level 6 through the bars; a film choice the story needs). The open piston wall
  joins it to dad's cell: the doorway behind dad IS the box. Steve's walk past the slot: U.STEVE_PAST ((17.6, -16.65)
  -> (17.6, -12.2), south to north, frame left to right, 2.15 from the lens). U.SLOT_FACE: the slot's bars (a focus
  point). ug_box / ta_box_baby (14.5, -15.5, F): inside the box (ta_box_baby turned 20 degrees from the door toward
  the bx24 lens). THE STAIR FOOT: ug_stair_foot (5, -9.55, F), where the steps meet the hall; the aisle west of it
  (x -8..4) has no torch and falls off into the dark; ta_zombie_out (2.4, -11, F) the zombie stepping out of it;
  ta_kill_steve (5, -10.3, F) / ta_kill_zombie (3.65, -11.45, F) for the last blow (1.4 blocks apart).
THE SKY: "under". LIGHT: C.lights(s, "box") everywhere here (the hall's fill OFF: it passes walls and would light the
  box and the dark west aisle); bx08 boost "corner" (the corner torch x 1.8 on the hands); bx24 boost "dad24" and
  C.glow(s, "slot_strip") (the whole shot: his only light while the wall is shut) + C.glow(s, "doorway_glow",
  start=r["open"]) (the warm light that falls in when the wall opens).
THE WALL PLAN: shut in bx08 (the slot only), bx21, bx22, bx23; bx24 OPENS it from inside the box (C.wall_open(frame,
  who=s.name, relight=(st, s)): the lever flips off screen; the doorway's floor and ceiling and the box come up lit in
  this shot only).
THE TWIST (films/twoapples_common.py contract): the baby zombie villager in bx08 is a soft green shape and two tiny
  hands, his FACE NEVER READS (U.hands_in_slot(face="away") turns his head down and away; U.shade_face keeps his head
  and robe out of the corner torch, static for the film; focus on the boots); bx21 shows the slot black and EMPTY;
  bx22 shows the child as an ordinary villager for the last time; the first time his green face reads is bx24, framed
  as the child in sq02 (CAMS "box" = the mirror of CAMS "lip"). Story risk: if the small green figure in the dark box
  does not read as the narrator, the ending is lost: match sq02's framing exactly, let the opening wall light him
  fully, hold the full second before he moves.
TAGS: steve_bx08, steve_bx21, steve_bx23, zchild_bx (bx08: shade_face is set on him), zchild_bx24 (bx24: a separate
  model, not shade-linked), child_bx (bx22), zombie_bx22, zombie_bx23, rotten_flesh_bx (bx23), dad_bx (bx24).
  A new twin: any further "bx..." tag.
SHARED: CAMS["slot"] (bx08: CAMS["slot_locked"], focus on its "boot" point; bx21: CAMS["slot"] with the push, focus
  U.SLOT_FACE); CAMS["box"] (bx24, the mirror of sq02's CAMS["lip"]: keep lens, stop, distance, eye height and the
  screen direction of the look).
"""
from engine import players, undead
from engine import underground as U
from films import twoapples_common as TC


def _steve_past(C, s, tag, start):
    """Steve walking U.STEVE_PAST (south to north past the slot, under the slot camera's line) from `start` (a twin
    may start before the shot). Returns him (st.use'd)."""
    steve = C.actor("steve", tag)
    path = U.STEVE_PAST
    steve.place(start, path[0], TC.yaw_to(path[0], path[1]))
    steve.walk(start, path, speed=players.WALK_SPEED)
    C.st.use(s, steve)
    return steve


def _legs(steve):
    """Steve's legs (what the slot shots are about)."""
    return [o for o in (getattr(steve, "leg_l", None), getattr(steve, "leg_r", None)) if o is not None]


def bx08_slot(st, s, C, nar):
    """BEAT 8  "The player keeps one zombie down here."
    frames 490-550 (61 f, 2.54 s), sky under, the wall shut. Words: The 492, player 493, keeps 502, one 509, zombie
    516, down 526, here 534. The last word is spoken until 540; after it 10 frames to the cut.

    STORY: The back corner of the hall, camera on the floor, focus on Steve's boots as his legs walk past. Behind them,
    soft, the sealed stone box: its only opening is a slot of iron bars at floor level, one block high, black inside.
    In the black something green shifts, and two tiny hands rest between the bars at the height of Steve's knees.
    Steve does not look down.
    Cast: Steve (the player, legs only), Baby zombie villager (a soft green shape and two hands, face never readable).
    Effects: sealed stone box with a floor-level iron bar slot, one torch well away from the slot so the inside stays
    black, the focus held on the boots, the slot defocused.

    MUST BE SEEN, ON WHICH WORD
      frame 1         Steve's legs already walking (a twin pre-rolled STEVE_PRE frames), the slot soft behind
      "player"        the boots crossing the lens's line, SHARP (legs-together frames: walking legs smear in motion
                      blur), the slot black and soft behind them
      "one zombie"    in the black a green shape shifts; the two tiny hands between the bars (the corner torch on them)
      NEVER           his face (it must not read: the twist); Steve looking down
    SHARED: CAMS["slot_locked"] (= CAMS["slot"] without its push; bx21 uses the push), focus on its "boot" point. Cast:
      C.actor("steve", "bx08"), C.actor("zchild", "bx") with U.hands_in_slot(zv, frame 1) + U.shade_face(C.v, zv).
    NEIGHBOURS: before, tu07_hall (dad looks up at us); after, tu09_lever (the lever: the turn sequence).
    RISKS (story): a soft green shape behind low bars has to say zombie without showing a face or a size. If it reads
      as nothing, bring the green head one step closer to the torch strip while keeping it out of focus. If it gives
      the twist away, show the slot black and empty of everything but the two hands. Do not use a full-size zombie
      arm: it would be a lie on second viewing.
    MEASURED (the set's stills out/test/twoapples_set_b08_slot_boots.png, _slot_boots_hands.png): his leg near the lens
      on the legs-together frame, the slot soft behind (x 51 / y 51); 16 frames later two green hands between the bars
      (a few green pixels), the head a dark green shape; CORNER_KEY x 1.8; trousers ok.
    MEASURED BY THE LEAD (out/test/twoapples_scout_s40_bx08_slot_516_zones.png, on "zombie"): Steve has passed; the
      slot soft at the frame's middle, a dark green head shape and a green hand between the bars; the face does not
      read (his head 78 degrees off the lens, turned down, out of the corner torch). By the path (not rendered) Steve's
      boots cross the lens's line about frame 495, 1.25 blocks into his walk from 488, around "player" (493): pick the
      legs-together frames there.
    STUB NOW: the set's staging; his head shifts a little at "zombie" (still turned away). Heroes: Steve's legs, the
      hands.
    """
    f0 = s.frame_start
    steve = _steve_past(C, s, "bx08", f0 - STEVE_PRE)
    zv = C.actor("zchild", "bx")
    U.hands_in_slot(zv, f0)
    U.shade_face(C.v, zv)
    hx, hy, hz = U.HIDE_FACE_LOOK
    zv.look_at(C.at(s, "zombie") - 4, (hx + 0.15, hy - 0.25, hz), ease=10)
    st.use(s, zv)
    cam = TC.CAMS["slot_locked"]
    C.cam(s, "slot_locked", focus=cam["boot"], handheld=0.004)
    st.hero(s, "boots", *_legs(steve))
    C.lights(s, "box", boost="corner")


STEVE_PRE = 2          # bx08: Steve starts walking this many frames before the shot


def bx21_small(st, s, C, nar):
    """BEAT 21  "I'm still small."
    frames 1278-1318 (41 f, 1.71 s), sky under, the wall shut. Words: I'm 1280, still 1284, small 1292. The last word
    is spoken until 1304; after it 14 frames to the cut.

    STORY: The back corner again, camera on the floor. The slot of iron bars at floor level, black inside, no hands this
    time. Steve's legs walk past: the whole slot ends at his waist. Slow push in on the bars.
    Cast: Steve (the player, legs only). Effects: floor-level iron bar slot, slow push in, black interior.

    MUST BE SEEN, ON WHICH WORD
      frame 1         the push already moving (ease_out), the slot black and EMPTY (no hands, no green)
      "still"         Steve's legs passing between the lens and the slot: the slot ends at his waist
      "small" .. end  the bars, black inside, the push in
    SHARED: CAMS["slot"] (the same camera as bx08, with its push to pos1), focus U.SLOT_FACE. Cast:
      C.actor("steve", "bx21").
    NEIGHBOURS: before, sq20_grow (the square at dusk); after, bx22_found (the flashback at the stair foot).
    MEASURED (the set's still out/test/twoapples_set_b21_slot.png): the black slot (x 51 / y 51), legs passing,
      trousers ok (15).
    STUB NOW: the set's staging; Steve's walk begins on frame 1 + STEVE_DELAY (his crossing on "still"). Heroes: the
      slot (its bars are the hero: Steve's legs as the moving thing).
    """
    f0 = s.frame_start
    steve = _steve_past(C, s, "bx21", f0 + STEVE_DELAY)
    C.cam(s, "slot", focus=U.SLOT_FACE, handheld=0.004)
    st.hero(s, "legs", *_legs(steve))
    C.lights(s, "box")


STEVE_DELAY = 2        # bx21: Steve's walk begins this many frames after the shot's first


def bx22_found(st, s, C, nar):
    """BEAT 22  "The night I came down, the zombie found me first."
    frames 1319-1401 (83 f, 3.46 s), sky under, the wall shut. Words: The 1321, night 1323, I 1329, came 1333, down
    1340, the 1357, zombie 1359, found 1370, me 1378, first 1381. The last word is spoken until 1393; after it 8
    frames to the cut.

    STORY: Flashback at the foot of the stairs. The baby villager, still an ordinary villager, stops where the steps
    meet the hall, three-quarter front. In the dark aisle behind him a full-size zombie steps out, arms raised,
    rim-lit by one torch. He turns his big head toward it. Cut before it reaches him.
    Cast: Baby villager (narrator), Zombie (adult). Effects: torch rim light on the zombie, zombie arms raised,
    walking, cut before contact.

    MUST BE SEEN, ON WHICH WORD
      frame 1         the child at the stair foot, three-quarter front (an ordinary villager: the flashback); the
                      zombie already walking out of the dark (pre-rolled: in no shot before)
      "came down"     the child stops where the steps meet the hall
      "zombie"        the zombie stepping out, arms raised, rim-lit by the stair foot's torch against the black aisle
      "found me first"  the child's big head turns toward it (cheated toward the lens: never the blank box); CUT
                      before it reaches him (the last frames: the zombie still 1.5 blocks or more away)
    SHARED: none (the set's b22: 24 mm f/2.8 from the east along the aisle). Places: ug_stair_foot, ta_zombie_out.
      Cast: C.actor("child", "bx"), C.actor("zombie", "bx22").
    NEIGHBOURS: before, bx21_small; after, bx23_kill ("Same spot": the last blow).
    RISKS (story): a dark mob on a dark set: the adult zombie needs a torch rim light or it disappears into the
      deepslate (the stair foot's torch, ug_foot, is his rim). If the loose zombie raises the question of why it is
      out, stage it stepping out of the open piston doorway at the end of the aisle.
    MEASURED (the set's still out/test/twoapples_set_b22_foot.png): the child three-quarter (x 72 / y 54); the zombie
      with arms raised against the dark west aisle (x 22 / y 42).
    MEASURED BY THE LEAD (tools/twoapples_geo): the stub's zombie reaches ta_zombie_out 11 frames into the shot and
      STANDS there for the rest of it (eyes x 22 / y 42 from 1340 to 1395: the story wants him stepping out toward the
      child, cut before contact: stretch his walk over the shot); the child's eyes x 72 / y 54 (37 px), looking into the
      lens on 1340, 65 degrees off it once turned to the zombie (1395).
    STUB NOW: the zombie walks out from ZOMBIE_FROM to ta_zombie_out (pre-rolled), aggro; the child looks at the lens,
      then turns his head to the zombie (C.cheat, max_off 65) on "zombie". Heroes: the child, the zombie.
    """
    f0, f1 = s.frame_start, s.frame_end
    kid = C.actor("child", "bx")
    C.put(kid, f0, "ug_stair_foot")
    cam = C.camera_spec("set:b22")
    kid.look_at(f0, C.to_lens(kid, f0, (cam["pos"][0], cam["pos"][1], kid.eye_point(f0).z), cam["pos"], 30.0),
                ease=0)
    z = C.actor("zombie", "bx22")
    a, b = ZOMBIE_FROM, C.P("zombie_out")
    fz = f0 - ZOMBIE_PRE
    z.place(fz, a, TC.yaw_to(a, b))
    z.aggro(fz, ease=0)
    z.walk(fz, [a, b])
    turn = C.at(s, "zombie")
    kid.look_at(turn - 2, C.cheat(kid, turn, z.eye_point(turn), cam["pos"], max_off=65.0), ease=8)
    st.use(s, kid, z)
    C.cam(s, "set:b22", focus=kid.head)
    st.hero(s, "child", kid)
    st.hero(s, "zombie", z)
    C.lights(s, "box")


ZOMBIE_FROM = (0.4, -11.1, float(TC.F))      # bx22: the zombie starts in the dark west aisle ...
ZOMBIE_PRE = 10                              # ... this many frames before the shot


def bx23_kill(st, s, C, nar):
    """BEAT 23  "The player only needs one zombie."
    frames 1402-1464 (63 f, 2.62 s), sky under, the wall shut. Words: The 1404, player 1405, only 1416, needs 1425,
    one 1432, zombie 1438. The last word is spoken until 1450; after it 14 frames to the cut.

    STORY: Same spot. Steve with an iron sword: one swing, the last blow. The big zombie flashes red, is knocked back,
    tips over sideways and is gone in a white puff a second later. A piece of rotten flesh spins on the floor. Steve
    lowers the sword and looks down at something small at his feet, below the frame.
    Cast: Steve (the player), Zombie (adult). Effects: iron sword, single swing; the game's death: red, knock-back, tip
    over, white poof; rotten flesh as a spinning dropped item; Steve's head tilting down.

    MUST BE SEEN, ON WHICH WORD
      frame 1         Steve with the iron sword facing the zombie (arms raised), 1.4 blocks apart, already moving
      "only needs"    ONE swing (the last blow: a zombie has 20 health, an iron sword does 6; never a fight)
      "one zombie"    red, knocked back, tipping over sideways (undead.die: 25/51/72/90 degrees at 2/5/9/13.5 ticks)
      after it        the white puff (24 frames after the blow), the rotten flesh spinning on the floor, Steve lowering
                      the sword and looking DOWN at something small at his feet, below the frame (never shown)
    SHARED: places ta_kill_steve, ta_kill_zombie (the stair foot: "Same spot" as bx22). Camera: the set's b23 (24 mm
      f/2.8, the stair foot wider). Cast: C.actor("steve", "bx23"), C.actor("zombie", "bx23"),
      C.item("rotten_flesh", "bx").
    NEIGHBOURS: before, bx22_found; after, bx24_kept (inside the box).
    MEASURED (the set's still out/test/twoapples_set_b23_kill.png, 12 frames after the blow): Steve with the sword
      (x 73 / y 39); the zombie red and tipping over.
    STUB NOW: the blow on "needs"; the flesh dropped at the poof; Steve's head down from "zombie". Heroes: Steve, the
      zombie.
    """
    f0, f1 = s.frame_start, s.frame_end
    steve = C.actor("steve", "bx23")
    z = C.actor("zombie", "bx23")
    C.put(steve, f0, "ta_kill_steve")
    steve.hold("iron_sword")
    C.put(z, f0, "ta_kill_zombie")
    z.aggro(f0, ease=0)
    blow = C.at(s, "needs")
    steve.attack(blow)
    undead.die(z, blow, camera=s, attacker=steve)
    poof = blow + undead.DEATH_FRAMES
    flesh = C.item("rotten_flesh", "bx")
    if poof < f1 - 2:
        feet = z.pos_at(poof)
        flesh.drop(poof, (feet.x, feet.y, float(TC.F)), rest=True)
        flesh.animate(poof, f1 + 1)
        st.use(s, flesh)
    sp = steve.pos_at(f0)
    steve.look_at(min(f1 - 6, poof + 2), (sp.x - 0.3, sp.y - 0.9, sp.z + 0.1), ease=10)
    st.use(s, steve, z)
    C.cam(s, "set:b23", focus=steve.head)
    st.hero(s, "steve", steve)
    C.lights(s, "box")


def bx24_kept(st, s, C, nar):
    """BEAT 24  "He kept the smaller one."
    frames 1465-1557 (93 f, 3.88 s), sky under, the wall shut -> open. Words: He 1467, kept 1471, the 1477, smaller
    1480, one 1493. The last word is spoken until 1502; after it 55 frames to the cut (the last 6 frames of the film
    are black: END_BLACK).

    STORY: Inside the box for the first time, seen through its see-through side wall from his own eye height: the
    camera of beat nineteen moved to the other side of the wall. A baby zombie villager, framed where the baby villager
    stood in beat two: the same big head, now green, the same brown robe, small arms out, lit only by the strip of
    torchlight from the floor-level bars. Hold a full second. The wall in front of him pulls aside and warm light falls
    across his face. He runs, and a short pan with his first step brings dad's back and book hat into frame beyond the
    doorway. Cut to black.
    Cast: Baby zombie villager (narrator), Dad (librarian, from behind). Effects: see-through box wall for the camera,
    sticky pistons opening the wall, light falling across him as it opens, baby zombie run start, short pan, cut to
    black.

    MUST BE SEEN, ON WHICH WORD
      frame 1 .. "smaller"  the baby zombie villager framed EXACTLY as the child in sq02 (CAMS "box" = the mirror of
                      "lip": head x 50 / y 46, three-quarter, looking down to frame right), lit from below by the slot's
                      strip; a full second of hold (the handheld's float is the only motion)
      "one"           the wall pulls aside (C.wall_open with relight: the doorway and the box come up lit), the warm
                      light falls across his face
      after the line  his run (the first step), the short pan RIGHT (north) to dad's back and book hat beyond the
                      doorway; dad facing front (his back to us)
      the last 6 frames  black (films/twoapples.py END_BLACK: the encoder's "cut to black"); nothing important in the
                      3 frames before them
    THE WALL: THIS SHOT OPENS IT (films/twoapples.py WALL), from inside: the lever flips off screen.
    SHARED: CAMS["box"] exactly (the mirror of CAMS["lip"]: 50 mm f/2.0, 2.4 blocks, eye height; see-through
      "ug_box_side", "ug_end_wall", "ug_slot": C.cam_hold keys them); the pan with C.cam_hold (U.hold_then_move) from
      his first step. Places: ta_box_baby, ug_cell_dad. Cast: C.actor("zchild", "bx24"), C.actor("dad", "bx").
    NEIGHBOURS: before, bx23_kill; after, nothing: the end in black, the Reel loops to sq01 (Steve at the mouth).
    RISKS (story): this is the reveal. If the small green figure in the dark box does not read as the narrator, match
      sq02's framing exactly, let the opening wall light him fully, hold the full second before he moves. If the pan
      cannot show dad's back as well, drop it: the light across his face and the run are enough (beat 19 already
      showed what is on the other side of that wall).
    MEASURED (the set's stills out/test/twoapples_set_b24_box.png, _b24_box_open.png): the hold mirrors sq02 (head
      x 50 / y 46 against x 50 / y 44), lit from below by the slot strip; the open still: warm light across his face.
      THE PAN TO DAD'S BACK WAS NOT RENDERED from this camera (the set builder's open issue): look at it first.
    MEASURED BY THE LEAD (tools/twoapples_geo, out/test/twoapples_scout_*bx24_kept_*.png, tools/twoapples_palette):
      THE MIRROR HOLDS: on 1480 his eyes x 50.0 / y 46.2, head 130 px, 32 degrees off the lens; sq02's child on 110 x 49.4
      / y 44.0, 138 px, 27 degrees off (side by side: the same place in the frame, the same size, the same look down to
      frame right). THE HOLD WAS BLACK with the engine's 6 W strip (face box p95 luma 16 of 255:
      out/test/twoapples_scout_bx24_kept_1480.png): the lead set GLOWS slot_strip to 120 W and doorway_glow to 180 W
      (films/twoapples_common.py SLOT_STRIP_WATTS / DOORWAY_WATTS): the green face, red eyes and robe read in the hold
      (p95 69; out/test/twoapples_scout_s120_bx24_kept_1480.png), fully lit once the wall opens (p95 130, 1500:
      _s120_bx24_kept_1500.png); tools/twoapples_palette 1484 1500: hero 'baby' 93 / 96 % inside the safe area, no
      failure. THE PAN IS A PROBLEM: on 1511 (the sheet tile) the frame is grey mush (pan + focus rack + his run); at
      the end (1545, out/test/twoapples_scout_bx24_kept_1545_zones.png) dad's back fills the right edge (eyes x 73 /
      y 36, head top at y 10 %, into the icon column) and the baby has left the frame at the left (x -92 %): aim the pan's
      end between his last step and dad (both in the frame), or drop the pan as the story allows.
    STUB NOW: the set's staging: hold, the wall opens HOLD frames in, his run 6 frames after it is open, the pan over
      16 frames, the focus racks to dad. Hero: the baby zombie villager.
    """
    f0, f1 = s.frame_start, s.frame_end
    A = C.A
    zv = C.actor("zchild", "bx24")
    C.put(zv, f0, "ta_box_baby")
    cam = TC.CAMS["box"]
    zv.look_at(f0, U.cheat(C.P("box_look"), TC.up(A["ug_box"], 0.6), cam["pos"], 0.5), ease=0)
    dad = C.actor("dad", "bx")
    C.put(dad, f0, "ug_cell_dad")
    dad.look_at(f0, TC.up(A["ug_aisle_dad"], TC.LOOK_FRONT_DZ), ease=0)
    st.use(s, zv, dad)
    r = C.wall_open(f0 + HOLD, who=s.name, relight=(st, s))
    opened, open_end = (r["open"], r["open_end"]) if r else (f0 + HOLD + 3, f0 + HOLD + 6)
    run = open_end + 6
    zv.look_at(run - 3, TC.up(A["ug_cell_dad"], 1.5), ease=3)
    zv.walk(run, [A["ug_box"], (14.6, -14.9, float(TC.F))])
    C.cam_hold(s, "box", run, frame_end=run + 16, focus=zv.head)
    C.rack(s, dad, run + 4, frames=12)
    st.hero(s, "baby", zv)
    C.lights(s, "box", boost="dad24")
    C.glow(s, "slot_strip")
    C.glow(s, "doorway_glow", start=opened)


HOLD = 26              # bx24: the wall is flipped open this many frames into the shot (a full second of hold)
