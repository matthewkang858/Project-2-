"""Twenty Minutes, sequence CELL: inside the glass pod at the top of the tower, the zombie's side: the bed and the
zombie in a box, the arms that cannot reach, the fear (twice, from the same window camera). Beats 6, 7, 8 and 23 + the
start of 24 (shots ce06_bed, ce07_reach, ce08_scared, ce23_afraid), sky "gold". One function per shot; the contract
is in films/twentyminutes_common.py (tags "ce...", C.actor, C.cam, C.lights, st.use / st.hero).

THE PLACE (engine/towers.py LAYOUT; films/twentyminutes_set.py): the pod inside x -23..-19, y 18..22, z 10..11 (2 high
  under the glass roof z 12; glass ring x -24..-18, y 17..23). The zombie's cell (-18, 19) in the east wall: the sill
  (-19, 19, 10) on the pod's floor, open air above it, the zombie at (-17.7, 19.5) facing west, its eyes C.zombie_eye
  (z 11.74); its arms reach 0.35 into the pod and stop in the air (to x -18.35); Mom's place 'mom' (-20.5, 19.5) is ONE
  WHOLE EMPTY BLOCK from the arm tips ("The zombie can't reach her": the game's reach ends at x -18.83). The lantern
  (-23, 18, 10) in the front-west corner, the cell's wall torch (-19, 18, 10). Beds, pillows north: white (-23, 21),
  white (-22, 21), Mom's red (-21, 21); the second red bed (-20, 21..22) from gr21 on (the film shows it: you see it in
  ce23). Free floor: rows y 18..20 (but the lantern's and the sill's cells) and the column x -19, y 20..22.
  Places by towers' short names (C.P / C.put): mom, mom_glass, bed_side, bed_beside (before the second bed only),
  back_1 (-22.55, 19.4), back_2 (-22.55, 20.4), back_3 (-21.6, 18.4); the film's narrator_23, mom_23, librarian_23.
  Cutaways (camera only): st.see_through(s, "tower_pod_north" | "_east" | "_south" | "_west" | "_roof").
THE SCOUTING STILLS: out/test/twentyminutes_set_b06_bed_a.png, _b06_bed_b.png, _b07_reach.png, _b08w_window.png,
  _b23w_window.png, _b23_afraid.png, _b24w_window.png (+ _zones.png each).
LIGHT: C.lights(s, "tower") (the lantern and the cell's torch at 1.0; far village torches off).
MOM'S HEAD IS ON THE ZOMBIE IN EVERY FRAME (C.on_zombie / towers.panic with the zombie's eyes: C.pod does it).
TAGS TAKEN (twins): mom_ce, zombie_ce (every shot), cleric_ce, librarian_ce (ce08, ce23), narrator_ce (ce23). New: ce2..
PREVIEWS through render.py: --samples 6 (PREVIEW_SAMPLES["cell"]).
"""
from films import twentyminutes_common as TC


def ce06_bed(st, s, C, nar):
    """BEAT 6  "He gave her a bed, and a zombie in a box."   frames 339-411 (73 f, 3.04 s), sky gold.
    Words: He 341, gave 344, her 350, a 354, bed 356, and 372, a 375, zombie 377, in 388, a 391, box 392. The voice
    ends on 405 (the pause after the line is 0.35 s).
    Before: sq05_wave; after: ce07_reach.

    STORY: Inside the pod, under its low glass roof. Slow pan from Mom's red bed, seen lengthwise from its foot with two
    white beds beyond it, past Mom standing beside it, to the side wall: a one-block cobblestone cell under a stone
    slab, closed at foot level and open at head height. A zombie's head and outstretched arms fill the window, lit by a
    wall torch.
    Cast: Mom (farmer villager), zombie. Effects: red bed (Mom's), two white beds, cobblestone zombie cell with stone
    slab roof and an open window at head height (no glass), wall torch at the cell, lantern on the floor.

    MUST BE SEEN, ON WHICH WORD
      frame 1           the pan already moving (ease_out), the red bed lengthwise from its foot, the white beds beyond
      "bed"             the red bed (focus on it)
      "zombie" .. "box" the cell: the zombie's head and outstretched arms filling the window, the slab over it, the
                        torch below (the focus racked to it)
    SHARED: none. Mom on bed_beside (the second bed's space: allowed here only, before gr21).
    NEIGHBOURS: before, sq05_wave (the foot of the tower, outside); after, ce07_reach.
    MEASURED (the set builder, stills _bed_a at f0 + 2 / _bed_b at the end): the red bed lengthwise with the white beds,
      Mom's hat at the edge; at the end the zombie fills the window over the sill.
    NOW (stub = the set's stage_b06): camera "set:b06" (towers' pan_bed, 24 mm, panning to the cell), focus on the red
      bed, racked to the zombie on "zombie"; Mom on bed_beside, head on the zombie; the zombie, arms forward. Hero: Mom.
    """
    f0 = s.frame_start
    mom = C.actor("mom", "ce")
    C.put(mom, f0, "bed_beside")
    C.on_zombie(mom, f0)
    z = C.zombie(s, "ce", look=mom)
    st.use(s, mom)
    C.cam(s, "set:b06", focus=C.fm.beds["mom"]["pos"])
    C.rack(s, z, C.at(s, "zombie"), frames=16)
    st.hero(s, "mom", mom)
    C.lights(s, "tower")


def ce07_reach(st, s, C, nar):
    """BEAT 7  "The zombie can't reach her."   frames 412-455 (44 f, 1.83 s), sky gold.
    Words: The 414, zombie 416, can't 428, reach 435, her 442. The voice ends on 447 (the pause after the line is
    0.45 s).
    Before: ce06_bed; after: ce08_scared.

    STORY: Tight profile two-shot on a long lens. On the left the zombie's arms reach out of the window and stop in the
    air. One whole empty block further right, Mom's face, straw hat and nose, looking straight at it. Nothing between
    them but air.
    Cast: Mom (farmer villager), zombie. Effects: zombie arm sway (arms raised, aggressive pose), window sill of the
    cell at the frame edge.

    MUST BE SEEN, ON WHICH WORD
      frame 1           the arms swaying (they sway by themselves), Mom's profile
      "reach"           the arms stopped in the air, the one empty block of air, her face and nose
    SHARED: none (towers' two_shot from behind the back wall: tower_pod_north hidden from the camera).
    NEIGHBOURS: before, ce06_bed; after, ce08_scared (the window camera).
    MEASURED (the set builder, still _reach at f0 + 12): the green arms out of the window at the LEFT EDGE (a sliver:
      look at it at phone size), one empty block, Mom in profile at x 76 / y 49 %. The two-shot is at 45 mm f/2.8 from
      9 blocks: a longer lens from further back (the story's "long lens") would make the arms bigger: try it.
    NOW (stub = the set's stage_b07): camera "set:b07" (45 mm), focus on Mom; Mom on 'mom', head on the zombie; the
      zombie aggro (raised arms); the north wall seen through. Heroes: Mom.
    """
    f0 = s.frame_start
    mom = C.actor("mom", "ce")
    C.put(mom, f0, "mom")
    C.on_zombie(mom, f0)
    C.zombie(s, "ce", aggro=True, look=mom)
    st.use(s, mom)
    st.see_through(s, "tower_pod_north")
    C.cam(s, "set:b07", focus=mom.head)
    st.hero(s, "mom", mom)
    C.lights(s, "tower")


def ce08_scared(st, s, C, nar):
    """BEAT 8  "It doesn't have to."   frames 456-503 (48 f, 2.00 s), sky gold.
    Words: It 458, doesn't 461, have 468, to 475. The voice ends on 483 (the pause after the line is 0.95 s).
    Before: ce07_reach; after: gm09_golem.

    STORY: From beside the zombie cell, looking across the pod. Mom, a cleric and a librarian are backed against the far
    glass, three heads turned toward the lens side, where the zombie's arm is a soft green shape at the frame edge.
    They tremble and turn on the spot. Behind them, through the glass, the empty stone platform. This camera position
    returns for the last two lines.
    Cast: Mom (farmer villager), cleric villager, librarian villager, zombie (foreground, out of focus). Effects:
    villager panic tremble and quick turns, golem platform visible through the glass, empty.

    MUST BE SEEN, ON WHICH WORD
      frame 1           the three already trembling (towers.panic from f0), the arm blur at the left edge
      "have"            three faces toward the lens' side, trembling, turning on the spot, heads ON the zombie
      the whole shot    the platform empty behind them (it reads in gm09)
    SHARED: CAMS "window_08" (ce23's CAMS "window" position, lens and stop, aimed 0.35 further north), THREE (the same
      three places as gm09 / gm10, where they are seen from the platform), the zombie's arms FORWARD (aggro=False:
      raised arms leave this frame).
    NEIGHBOURS: before, ce07_reach; after, gm09_golem (the platform: the golem comes; the three behind the glass).
    FALLBACKS APPLIED: towers' "impossible" zombie arm at the frame edge is had: the lens 0.13 from the zombie's right
      arm (the set's b08w / b23w): a dark green blur down the left edge (pixels about (46, 68, 37)).
    MEASURED (the set builder, still b08w_window at f0 + 30, this aim): Mom 20 %, the cleric 46 %, the librarian 66 %,
      all y 47-48 %. (With CAMS "window", ce23's aim, tools.twentyminutes_geo ce08_scared:480 put their eyes at 32 /
      58 / 79 % and the librarian's head to x 84.5 %, into the icon column: that is why ce08 has its own aim.)
    NOW (stub): CAMS "window_08", focus on the cleric; THREE trembling (C.pod(..., panic=True)); the zombie, arms
      forward. Hero: Mom.
    """
    who = C.pod(s, "ce", TC.THREE, panic=True)
    C.zombie(s, "ce", aggro=False, look=who["mom"])
    C.cam(s, "window_08", focus=who["cleric"].head)
    st.hero(s, "mom", who["mom"])
    C.lights(s, "tower")


def ce23_afraid(st, s, C, nar):
    """BEAT 23+24  "I'm afraid of the zombie."  "Apparently that" (of: Apparently that counts.)   frames 1400-1472 (73
    f, 3.04 s), sky gold.
    Words: I'm 1402, afraid 1406, of 1417, the 1420, zombie 1421, Apparently 1453, that 1467.
    Before: gp22_step; after: gm24_counts.

    STORY (beat 23, and beat 24 up to "counts": "Same shot, held"): The camera from beside the zombie cell again. The
    narrator's head snaps round to the lens side. The zombie's arms reach from the window at the foreground edge. He
    trembles on the spot next to Mom: same height, same pose, both staring at it. The two red beds sit side by side
    below them. [24] Same shot, held. (The golem through the glass and the rack focus: the story's own fallback, the
    cut on "counts" to the platform framing, gm24_counts.)
    Cast: grown narrator, Mom (farmer villager), cleric villager, librarian villager, zombie (foreground edge).
    Effects: villager panic tremble, the narrator's matched to Mom's; two red beds side by side; zombie arm sway.

    MUST BE SEEN, ON WHICH WORD
      frame 1 .. "afraid"   the narrator's head SNAPS round to the lens' side (to the zombie): on f0 it is elsewhere
                        (where he looked in gp22: level, toward the back glass), then on the zombie in 2-3 frames
      "zombie"          the narrator and Mom side by side, same height, same pose, trembling ALIKE (PANIC_SEED: the
                        same tremble frame for frame), both staring at the zombie just over the lens
      "Apparently" .. "that"   the shot HELD (nothing new: the fear goes on); the cut on "counts" goes to gm24
    SHARED: CAMS "window" (= ce08's), FOUR (the same four places as gm24, where they are seen from the platform),
      PANIC_SEED, the zombie's arms forward; the second bed is in this shot (the film's BED2_FROM).
    NEIGHBOURS: before, gp22_step (the narrator watching Steve break the step, from outside); after, gm24_counts.
    KNOWN (the set builder): "the two red beds below them" cannot be had from beside the cell: the beds are north of
      the four; one red bed shows at the right edge of the window framing (both side by side are seen in gr21).
    MEASURED (the set builder, still b23w_window at f0 + 20): the arm blur at the left edge; Mom 26 %, the narrator
      57 %, the librarian between them behind (41 %), the cleric on back_2 (79 %); a red bed at the right edge.
    NOW (stub): CAMS "window", focus on the narrator; FOUR trembling (C.pod(..., panic=True): Mom and the narrator
      with PANIC_SEED); the zombie, arms forward. (The head snap is not staged yet.) Heroes: the narrator, Mom.
    """
    who = C.pod(s, "ce", TC.FOUR, panic=True)
    C.zombie(s, "ce", aggro=False, look=who["mom"])
    C.cam(s, "window", focus=who["narrator"].head)
    st.hero(s, "narrator", who["narrator"])
    st.hero(s, "mom", who["mom"])
    C.lights(s, "tower")
