"""Two Apples, sequence CURE: the potion, the one golden apple, the wall that shuts, the five minutes, the trade, and
dad who never looks behind him. Beats 13-19 (shots cu13_potion, cu14_apple, cu15_two, cu16_shakes, cu17_emerald,
cu18_saved, cu19_behind), sky "under". One function per shot; the contract is in films/twoapples_common.py (tags
"cu...", C.actor, C.cam, C.lights, st.use / st.hero).

THE PLACE: the hall in front of dad's cell and down the aisle (films/twoapples_turn.py docstring, THE PLACE; the
  set's "THE HALL"). Anchors: ug_cell_dad (dad, 0.18 west of the cell's middle), ug_cell_dad_mid (cu18, cu19: a head
  turned west to its stop puts his nose into the pier from ug_cell_dad), ug_counter_steve (cu13: Steve at the counter
  east of dad), ug_aisle_dad (Steve in front of dad's cell: cu14, cu17), ug_jump_spot (12.3, -11.35: cu16),
  ug_follow_start (14.5, -11.4) -> ug_follow_end (7.2, -11.4) (cu18: Steve walks away up the aisle), ug_door_target.
THE SKY: "under". LIGHT: C.lights(s, "hall") (+ boost "dad13" in cu13, "dad17" in cu17; lever=False in cu13, cu16,
  cu19: they see through "ug_end_pier", the lever would float), C.glow(s, "counter_bounce") and C.glow(s, "dad_side")
  in cu13 (the see-through pier and wall still cast shadows: without them Steve's trousers clip), "dad_side" in cu19.
THE WALL PLAN: OPEN in cu13 and cu14 (the doorway black behind zombie dad); cu15 SHUTS IT on its last word, "two"
  (C.wall_shut(frame, who=s.name): the pistons push the wall shut over the dark; the only shot here that moves it);
  shut in cu16-cu19.
DAD: the zombie villager (C.actor("zdad", "cu"), arms out: C.cells(..., dad_role="zdad") aggro's him) from cu13 to
  the swap inside cu17; there undead.cure(zdad, dad, ...) replaces him "between one frame and the next" with the
  villager (C.actor("dad", "cu")): no burst, only the dark purple Nausea swirls. From then on the villager: cu17 after
  the swap, cu18 and cu19 at ug_cell_dad_mid, his head turned up the aisle to its stop and HELD there.
SWIRLS (engine/undead.py; the game's colours): weakness dark grey (the splash potion's burst, cu13), strength YELLOW
  (the cure: the first ones rise in cu15, streaming in cu16, up to the swap in cu17), nausea dark purple (after the
  swap: cu17, the last ones in cu18). Swirls are emitted per shot, facing that shot's camera (camera=s); particles in
  the air live on into the next shot of this sequence (no time jump between them).
ITEMS: the splash potion is thrown by undead.throw_potion (no bottle in his hand: the engine's note); the golden apple
  in Steve's hand (Player.hold("golden_apple")) in cu13 and cu14, GONE in cu15; the emerald (Player.hold("emerald"))
  in cu17; dad's enchanted book on his crossed arms (C.book, with its glint and its end frame) in cu17; the book in
  Steve's hand (Player.hold("enchanted_book", enchanted=True) + C.stamp_glint) as he walks away in cu18.
THE STORY'S RULES: "He only ever brings one": one apple, no montage of repeats (a second cure adds no discount since
  1.20.2: the other three cells make "always" true). "Dad shakes for five minutes": the cure shake enlarged (shake=3)
  so it reads in a wide. Zombie dad does not react to the potion or the apple.
TAGS: zdad_cu, dad_cu, farmer_cu, fletcher_cu, cleric_cu (C.cells(s, "cu"): placed on each shot's first frame),
  steve_cu13 ... steve_cu18 (one Steve per shot: each holds another item). A new twin: any further "cu..." tag.
SHARED: none of the cameras (each is its shot's own; the stubs use the set's b13-b19).
"""
from engine import players, undead
from engine import underground as U
from films import twoapples_common as TC


def cu13_potion(st, s, C, nar):
    """BEAT 13  "The player throws a potion and feeds him a golden apple."
    frames 781-868 (88 f, 3.67 s), sky under, the wall open. Words: The 783, player 785, throws 793, a 802, potion
    803, and 823, feeds 826, him 835, a 839, golden 841, apple 853. The last word is spoken until 863; after it 5
    frames to the cut.

    STORY: Side-on along the counter. One casual arm swing from Steve: a splash potion crosses the counter and breaks
    on zombie dad in a burst of dark grey swirls. Steve's other hand comes up into frame holding a golden apple toward
    the green face. Zombie dad does not react.
    Cast: Steve (the player), Dad as zombie villager (librarian). Effects: splash potion of weakness, thrown; dark grey
    splash burst and bottle shards; golden apple in Steve's raised hand.

    MUST BE SEEN, ON WHICH WORD
      frame 1         zombie dad (arms out) behind the lectern, Steve at the counter; the doorway still open
      "throws a potion"   the swing and the bottle across the counter; the dark grey burst on zombie dad
      "golden apple"  Steve's OTHER hand up with the apple toward the green face; zombie dad does not react
    SHARED: none (the set's b13: side-on along the counter from the east, 20 mm f/2.8, see-through "ug_end_pier" +
      "ug_end_wall": C.cam keys them; the lever left out: C.lights(..., lever=False)). Cast: C.cells(s, "cu",
      dad_role="zdad"), C.actor("steve", "cu13") at ug_counter_steve.
    NEIGHBOURS: before, tu12_green (the swap, the turn sequence); after, cu14_apple (close on the apple).
    MEASURED (the set's still out/test/twoapples_set_b13_potion.png, 3 frames before the impact): zombie dad left
      (x 28 / y 44), Steve right (x 76 / y 45) with the apple, the splash in the air between them. COUNTER_BOUNCE at
      70 W (the engine's 35 W clipped his trousers at the hall's light: min channel 11 against 12; now 16) and
      DAD_SIDE_FILL. Somewhat cramped (the set builder's note).
    STUB NOW: the throw THROW_LEAD frames before "throws"; the apple in the left hand raised from "golden". Heroes:
      zombie dad, Steve.
    """
    f0 = s.frame_start
    cells = C.cells(s, "cu", dad_role="zdad")
    zdad = cells["dad"]
    steve = C.actor("steve", "cu13")
    C.put(steve, f0, "ug_counter_steve", toward="ug_cell_dad")
    steve.hold("golden_apple", hand="left")
    st.use(s, steve)
    hit = undead.throw_potion(steve, zdad, max(f0 + 1, C.at(s, "throws") - THROW_LEAD), camera=s)
    C.memo["cu_hit"] = int(hit)
    steve.raise_arm(C.at(s, "golden") - 4, angle=55.0, ease=8, side="l")
    C.cam(s, "set:b13", focus=zdad.head)
    st.hero(s, "zombie dad", zdad)
    st.hero(s, "steve", steve)
    C.lights(s, "hall", lever=False, boost="dad13")
    C.glow(s, "counter_bounce")
    C.glow(s, "dad_side")


THROW_LEAD = 3         # cu13: the throw starts this many frames before "throws"


def cu14_apple(st, s, C, nar):
    """BEAT 14  "He only ever brings one."
    frames 869-916 (48 f, 2.00 s), sky under, the wall open. Words: He 871, only 875, ever 887, brings 894, one 903.
    The last word is spoken until 910; after it 6 frames to the cut.

    STORY: Close on the single golden apple in Steve's hand, torchlit, the brightest thing in the frame. The green face
    is soft behind it.
    Cast: Steve (the player, hand), Dad as zombie villager (librarian). Effects: golden apple close-up, long lens,
    shallow focus.

    MUST BE SEEN, ON WHICH WORD
      the whole shot  ONE golden apple in his raised hand, sharp, the brightest thing in the frame (a small thing is
                      seen only if it is what is in focus); the green face soft behind it
      "one"           the apple held still (the word lands on it)
    SHARED: none (the set's b14: beside Steve's right hand, 50 mm f/1.8, aimed and focused on the apple:
      steve.item_point("right", f)). Cast: C.cells(s, "cu", dad_role="zdad"), C.actor("steve", "cu14") at ug_aisle_dad.
    NEIGHBOURS: before, cu13_potion; after, cu15_two (the apple gone, the drift to the doorway).
    RISKS (story): if beat 15's inner thought plays flat, hold on the apple leaving Steve's hand here and let "I always
      hope he'll bring two" run over his empty open palm (that would change cu15: the director of this sequence owns
      both).
    MEASURED (the set's still out/test/twoapples_set_b14_apple.png): the apple centred (x 50 / y 50) and the brightest
      thing in the frame; the green face soft at the top-right edge (a little higher aim shows more of it, the apple
      then sinks toward the caption band).
    STUB NOW: the set's staging, a slow push toward the apple (APPLE_PUSH) so frame 1 moves. Hero: the apple (Steve's
      right hand; the apple is his held item).
    """
    f0, f1 = s.frame_start, s.frame_end
    cells = C.cells(s, "cu", dad_role="zdad")
    steve = C.actor("steve", "cu14")
    C.put(steve, f0, "ug_aisle_dad")
    steve.hold("golden_apple")
    steve.raise_arm(f0, angle=55.0, ease=0)
    st.use(s, steve)
    apple = tuple(steve.item_point("right", f0 + 6))
    cam = C.camera_spec("set:b14")
    pos1 = tuple(p + APPLE_PUSH * (a - p) for p, a in zip(cam["pos"], apple))
    C.cam(s, "set:b14", target=apple, pos1=pos1, target1=apple, focus=apple)
    st.hero(s, "apple", *(o for o in (steve.arm_r,) if o is not None))
    st.hero(s, "zombie dad", cells["dad"])
    C.lights(s, "hall")


APPLE_PUSH = 0.08      # cu14: the camera moves this share of the way to the apple over the shot


def cu15_two(st, s, C, nar):
    """BEAT 15  "I always hope he'll bring two."
    frames 917-971 (55 f, 2.29 s), sky under, the wall open -> shut. Words: I 919, always 922, hope 932, he'll 938,
    bring 942, two 948. The last word is spoken until 958; after it 13 frames to the cut.

    STORY: The apple is gone from Steve's hand, which drops out of frame. The first yellow swirls rise off zombie dad.
    The camera drifts past his shoulder toward the black doorway behind him. Nothing comes out of it. On the last word
    the pistons push the wall shut over the dark.
    Cast: Dad as zombie villager (librarian), Steve (the player, hand). Effects: slow drift toward the dark doorway,
    sticky pistons closing the wall, yellow Strength swirls starting, nothing visible in the doorway.

    MUST BE SEEN, ON WHICH WORD
      frame 1         the drift already moving (ease_out); Steve's empty hand dropping out of frame (NOT IN THE STUB:
                      Steve at ug_aisle_dad stands where this camera passes; he needs a spot beside the lens path)
      "hope"          the first yellow swirls off zombie dad; the black doorway beside / behind him, nothing in it
      "two"           THE WALL SHUTS (C.wall_shut on "two": the pistons push the two blocks back over the dark)
    THE WALL: THIS SHOT SHUTS IT (films/twoapples.py WALL), on its last word.
    SHARED: none (the set's b15: past his shoulder toward the doorway, 32 mm f/2.4, a drift pos0 -> pos, focus on the
      doorway (14.6, -15.0, F+1)). Cast: C.cells(s, "cu", dad_role="zdad").
    NEIGHBOURS: before, cu14_apple; after, cu16_shakes (wide down the aisle).
    MEASURED (the set's still out/test/twoapples_set_b15_drift.png): the black doorway x 60 / y 50 beside the
      zombie's face (x 81 / y 24: near the icon column's edge), the first yellow swirls.
    STUB NOW: the set's staging; swirls from frame 1; the wall shut on "two". Hero: zombie dad.
    """
    f0, f1 = s.frame_start, s.frame_end
    cells = C.cells(s, "cu", dad_role="zdad")
    zdad = cells["dad"]
    undead.effect_swirls(zdad, f0, f1, effect="strength", camera=s)
    C.wall_shut(C.at(s, "two"), who=s.name)
    C.cam(s, "set:b15", focus=(14.6, -15.0, TC.F + 1.0))
    st.hero(s, "zombie dad", zdad)
    C.lights(s, "hall")


def cu16_shakes(st, s, C, nar):
    """BEAT 16  "Dad shakes for five minutes."
    frames 972-1022 (51 f, 2.12 s), sky under, the wall shut. Words: Dad 974, shakes 981, for 990, five 994, minutes
    1003. The last word is spoken until 1014; after it 8 frames to the cut.

    STORY: Wide down the aisle. Zombie dad shakes in his cell on the left, yellow swirls streaming up off him. In the
    middle of the aisle Steve jumps on the spot, again and again, looking at nothing. Farmer, fletcher and cleric
    stare straight ahead out of their cells.
    Cast: Dad as zombie villager, Steve, Farmer, Fletcher, Cleric. Effects: zombie villager cure shake, enlarged about
    three times so it reads in a wide; yellow swirl particles; Steve jump loop.

    MUST BE SEEN, ON WHICH WORD
      frame 1         Steve already in the air (the jump loop starts before the shot: a new twin), zombie dad shaking
                      with yellow swirls in his window on the left
      "shakes"        the shake reads (undead.shake 3.0: enlarged on purpose, the story's choice)
      "five minutes"  the three others staring straight ahead; the aisle falling off into the dark
    SHARED: none (the set's b16: wide from the aisle's east end, 20 mm f/4, see-through "ug_end_pier": the lever left
      out). Cast: C.cells(s, "cu", dad_role="zdad"), C.actor("steve", "cu16") at ug_jump_spot.
    NEIGHBOURS: before, cu15_two (the wall shut); after, cu17_emerald (the swap, the trade).
    RISKS (story): the game's cure shake is a fine tremble that vanishes in a wide: enlarged here; if it still does
      not read, move in to a medium shot of dad with Steve jumping soft in the background. jump_loop keys the
      open-air jump: his head clips 0.05 into the aisle's ceiling for about 2 frames at each top (not looked at yet).
    MEASURED (the set's still out/test/twoapples_set_b16_aisle.png, the top of a jump): zombie dad with yellow swirls
      at the left (x 16 / y 44), the three in their windows, Steve at the top of a jump (x 74 / y 31), the lantern
      right of him, the aisle falling into darkness; Steve's trousers 36: ok.
    STUB NOW: the set's staging. Heroes: zombie dad, Steve.
    """
    f0, f1 = s.frame_start, s.frame_end
    cells = C.cells(s, "cu", dad_role="zdad")
    zdad = cells["dad"]
    undead.shake(zdad, f0, f1, 3.0)
    undead.effect_swirls(zdad, f0, f1, effect="strength", camera=s)
    steve = C.actor("steve", "cu16")
    C.put(steve, f0 - JUMP_PRE, "ug_jump_spot")
    U.jump_loop(steve, f0 - JUMP_PRE, f1)
    st.use(s, steve)
    C.cam(s, "set:b16", focus=steve.head)
    st.hero(s, "zombie dad", zdad)
    st.hero(s, "steve", steve)
    C.lights(s, "hall", lever=False)


JUMP_PRE = 6           # cu16: the jump loop begins this many frames before the shot


def cu17_emerald(st, s, C, nar):
    """BEAT 17  "Then he's dad again, and Mending costs one emerald."
    frames 1023-1103 (81 f, 3.38 s), sky under, the wall shut. Words: Then 1025, he's 1027, dad 1031, again 1039, and
    1054, Mending 1057, costs 1068, one 1078, emerald 1084. The last word is spoken until 1097; after it 6 frames to
    the cut.

    STORY: Over Steve's shoulder at the counter. Between one frame and the next the shaking stops and the librarian
    stands there again: pink skin, same hat, no burst, only dark purple swirls drifting off him. Steve holds up a single
    emerald. Dad's arm comes up at once, holding out an enchanted book with its glint.
    Cast: Dad as zombie villager, Dad (librarian), Steve. Effects: instant zombie villager to villager swap, no effect;
    dark purple Nausea swirls; one emerald held so it reads from behind; enchanted book with glint.

    MUST BE SEEN, ON WHICH WORD
      frame 1         zombie dad shaking with yellow swirls, over Steve's shoulder
      "dad"           THE SWAP on this word: undead.cure(zdad, dad, frame 1, swap) (no burst; the shake stops; the
                      nausea swirls begin)
      "Mending"       Steve holds up the emerald (big, LOW in the frame, readable from behind: flat items lie along
                      the hand; raise_arm 55 puts it below the caption band, 80 put it in the band and hid the book)
      "costs" .. "emerald"   dad holds out the enchanted book on his crossed arms, its glint; his face above it
    SHARED: none (the set's b17: over Steve's shoulder at ug_aisle_dad, 35 mm f/2.8). Cast: C.cells(s, "cu",
      dad_role="zdad"), C.actor("dad", "cu") (from the swap), C.actor("steve", "cu17").
    NEIGHBOURS: before, cu16_shakes; after, cu18_saved (the portrait: his head follows Steve).
    RISKS (story): this packs the end of the cure and the trade into one shot. The story's fallback (two shots under
      the sentence, the swap on "dad again", the emerald and book on "one emerald") is NOT available: the plan has one
      shot here (the cure sequence already has seven). The word Mending only reads in the caption; the picture says
      book for one emerald, which is enough.
    MEASURED (the set's still out/test/twoapples_set_b17_trade.png): the emerald big and low (x 49 / y 80, below the
      caption band), dad with the glinting book (x 50 / y 45). palette: "robe hue" fails on a few near-black robe
      pixels (rgb 24, 16, 19: hue undefined there); the face s 0.47.
    MEASURED BY THE LEAD (out/test/twoapples_scout_cu17_emerald_1092_zones.png, on "emerald"): dad cured, the
      glinting book on his arms (its top at y 55-65 %: touching the caption band), the emerald big and low (y 70-90 %),
      dad's eyes x 50 / y 45, 11 degrees off the lens; the zombie villager is gone from the swap on (geo at 1090).
    STUB NOW: the swap on "dad", the emerald raised from "Mending", the book from "costs" to the end; the nausea swirls
      from the swap to the end of THIS shot (cu18 emits its own, facing its camera). Heroes: dad, the emerald.
    """
    f0, f1 = s.frame_start, s.frame_end
    cells = C.cells(s, "cu", dad_role="zdad")
    zdad = cells["dad"]
    dad = C.actor("dad", "cu")
    steve = C.actor("steve", "cu17")
    C.put(steve, f0, "ug_aisle_dad")
    steve.hold("emerald")
    st.use(s, steve, dad)
    swap = C.at(s, "dad")
    cure = undead.cure(zdad, dad, f0, swap, camera=s, player=None, shake=1.0, nausea=f1 - swap + 1)
    C.memo["cu_cure"] = cure
    dad.look_at(swap, steve, ease=0)
    steve.raise_arm(C.at(s, "mending") - 4, angle=EMERALD_RAISE, ease=6)
    C.book(dad, C.at(s, "costs"), f1 + 1)
    C.cam(s, "set:b17", focus=zdad.head)
    C.rack(s, dad, swap, frames=4)
    st.hero(s, "dad", dad)
    C.lights(s, "hall", boost="dad17")


EMERALD_RAISE = 55.0   # cu17: Steve's arm (degrees): the emerald low in the frame (the set builder's measure)


def cu18_saved(st, s, C, nar):
    """BEAT 18  "Dad thinks the player saved him."
    frames 1104-1154 (51 f, 2.12 s), sky under, the wall shut. Words: Dad 1106, thinks 1115, the 1121, player 1122,
    saved 1131, him 1141. The last word is spoken until 1147; after it 7 frames to the cut.

    STORY: Portrait of dad. His head follows Steve walking away up the aisle with the book until it reaches its stop,
    and stays turned that way. The book's glint goes soft in the distance.
    Cast: Dad (librarian), Steve (the player, walking away, out of focus). Effects: head follow to the seventy-degree
    stop and hold, enchanted book in Steve's hand, last purple swirls.

    MUST BE SEEN, ON WHICH WORD
      frame 1         dad's face, his head already turning after Steve (who walks from frame 1, under the lens)
      "saved"         his head at its stop (70 degrees), turned up the aisle, HELD to the last frame
      the whole shot  the last purple swirls
    SHARED: place ug_cell_dad_mid (here and cu19: a head turned west to its stop). Camera: the set's b18 (from in front,
      a little above his eyes, 50 mm f/2.0). Cast: C.cells(s, "cu", dad_at="ug_cell_dad_mid"), C.actor("steve", "cu18")
      walking ug_follow_start -> ug_follow_end with the book.
    NEIGHBOURS: before, cu17_emerald; after, cu19_behind (the same cell from the side, through the end wall).
    KNOWN LIMIT (the set builder; the story's own): the book's glint in the distance and dad's face are not in one
      frame (Steve walks under the lens). Left out, as the story allows.
    MEASURED (the set's still out/test/twoapples_set_b18_follow.png, near the end): his face turned to profile at the
      stop (x 35 / y 47). Check his head against the 26-degrees-beyond-profile rule with tools/twoapples_geo: a head
      at its stop must still show the nose to this lens.
    STUB NOW: the set's staging. Hero: dad.
    """
    f0, f1 = s.frame_start, s.frame_end
    A = C.A
    steve = C.actor("steve", "cu18")
    a, b = A["ug_follow_start"], A["ug_follow_end"]
    steve.place(f0, a, TC.yaw_to(a, b))
    steve.hold("enchanted_book", enchanted=True)
    C.stamp_glint(steve)
    steve.walk(f0, [a, b], speed=players.WALK_SPEED)
    st.use(s, steve)
    cells = C.cells(s, "cu", dad_at="ug_cell_dad_mid", look=lambda n: steve if n == "dad"
                    else TC.up(A["ug_aisle_%s" % n], TC.LOOK_FRONT_DZ))
    dad = cells["dad"]
    dad.track(f0, f1, steve, step=2, ease=4)
    undead.effect_swirls(dad, f0, f1, effect="nausea", camera=s)
    C.cam(s, "set:b18", focus=dad.head)
    st.hero(s, "dad", dad)
    C.lights(s, "hall")


def cu19_behind(st, s, C, nar):
    """BEAT 19  "He never looks behind him."
    frames 1155-1209 (55 f, 2.29 s), sky under, the wall shut. Words: He 1157, never 1160, looks 1167, behind 1174,
    him 1186. The last word is spoken until 1192; after it 17 frames to the cut.

    STORY: Same cell from the side and lower, through the end wall, so the wall behind him is in the picture. Dad still
    gazes up the aisle. The camera slides slowly off his face onto the stone directly behind his back, the seam of the
    piston wall, and holds there.
    Cast: Dad (librarian). Effects: see-through end wall for the camera, slow lateral slide and focus pull to the wall,
    visible seam in the back wall.

    MUST BE SEEN, ON WHICH WORD
      frame 1         dad in profile gazing up the aisle (his head at its stop, as cu18 left it); the slide moving
      "looks"         the camera sliding off his face
      "behind him" .. end   the stone behind his back: the seam between the piston wall's two blocks (PLACES "seam"),
                      in focus, HELD (the pause after the line is 0.85 s: the story turns)
    THE WALL: shut (WALL): the seam is the closed door; nothing moves.
    SHARED: place ug_cell_dad_mid. Camera: the set's b19 (through the see-through "ug_end_wall" + "ug_end_pier" from the
      north-east, lower than his face, 32 mm f/2.4, the slide pos0 -> pos; the lever left out). Cast: C.cells(s, "cu",
      dad_at="ug_cell_dad_mid") with dad looking at the camera spec's "look" point (up the aisle).
    NEIGHBOURS: before, cu18_saved; after, sq20_grow (the square at dusk: the only daylight in the second half).
    MEASURED (the set's stills out/test/twoapples_set_b19_behind_start.png, _b19_behind.png): profile at the start
      (x 44 / y 48); the slide ends on the piston wall's stone (seam x 50 / y 50), dad at the right edge. Dark; the
      palette's "robe hue" fails on near-black pixels of his shaded side (DAD_SIDE_FILL 10 W lifts it a little).
    STUB NOW: the set's staging; the focus racks from his head to the seam on "behind". Hero: dad.
    """
    cam = C.camera_spec("set:b19")
    cells = C.cells(s, "cu", dad_at="ug_cell_dad_mid", look=lambda n: cam["look"] if n == "dad"
                    else TC.up(C.A["ug_aisle_%s" % n], TC.LOOK_FRONT_DZ))
    dad = cells["dad"]
    C.cam(s, "set:b19", focus=dad.head)
    C.rack(s, C.P("seam"), C.at(s, "behind") - 2, frames=14)
    st.hero(s, "dad", dad)
    C.lights(s, "hall", lever=False)
    C.glow(s, "dad_side")
