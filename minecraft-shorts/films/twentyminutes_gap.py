"""Twenty Minutes, sequence GAP: the dirt staircase up the back of the tower and the one-block gap in the pod's back
wall: the baby climbs in, the grown narrator cannot get out, the player breaks the top step. Beats 13, 14, 15, 20, 22
(shots gp13_stairs, gp14_gap, gp15_fit, gp20_nofit, gp22_step), sky "gold". One function per shot; the contract is
in films/twentyminutes_common.py (tags "gp...", C.actor, C.cam, C.lights, st.use / st.hero).

THE PLACE (engine/towers.py LAYOUT): ten full dirt blocks, one up and one along, against the pillar's back (north)
  face: the bottom (-17, 23, 0) west to (-21, 23, 4), the turn (-22, 23, 5), then back east one row further out
  (-22, 24, 6) (-21, 24, 7) (-20, 24, 8) to the TOP STEP (-19, 24, 9) outside the gap (C.fm.set["stairs"][0..9]);
  stray dirt at the foot. The doorway in the back wall at (-19, 23): the gap (z 10) under the cobblestone plug (z 11).
  Anchors (C.A / C.P): stairs_foot (-15.4, 24.3) the baby at the foot, stairs_target (a point up the stairs),
  top_step (-18.5, 24.5, 10) on the top step, top_step_baby (-18.28, 24.42, 10) the baby beside the opening,
  one_down (-19.5, 24.5, 9) one step down facing east (Steve breaks the top step from there), gap_in (-18.5, 22.66)
  a baby under the plug, gap_adult (-18.5, 22.3) the grown narrator at the plug, gap_down (-18.5, 25.5, 10.2) his
  look out of the gap, gap_side (-19.0, 22.66) the cleric half a block west of the opening, gap_target the gap's
  middle (-18.5, 23.5, 10.5); the film's watch_22_out (-20.6, 20.45, 10) (the narrator in gp22).
THE TOP STEP (P_.top_step, an engine.breaking Breakable): there in gp13-gp20, broken in gp22 by
  C.fm.break_top_step(steve, f, camera=s, until=s.frame_end + 1) (the game's 17 frames by hand, ten crack stages,
  crumbs, 64 dirt particles; Steve on one_down facing it first). NEVER register it with the Stage (registered, it is
  hidden in every shot that does not use it, and the baby of gp14 floats: tools/towers_proof.py's b14 still).
THE SCOUTING STILLS: out/test/twentyminutes_set_b13_stairs.png, _b14_gap.png, _b15_fit.png, _b20_nofit.png,
  _b22o_step_out.png, _b22_step.png (+ _zones.png each).
THE STORY'S RISK "THE GAP" (lines 14, 15, 20): the plot hangs on the viewer seeing that the opening is ONE block high.
  Fallback: the cleric beside the gap in line 14 as well (adult, baby and opening measured in one frame); cobblestone
  against glass for contrast; daylight through the gap in every interior shot of it.
GLASS (story risk): hide the pane nearest the lens on the lines to faces (C.panes / C.fm.see_through), keep glass
  behind the subjects, check each face at phone size.
LIGHT: C.lights(s, "tower").
TAGS TAKEN (twins): baby_gp (gp13, gp14, gp15), cleric_gp (gp15), narrator_gp (gp20, gp22), steve_gp (gp22), mom_gp
  (gp14, gp22), zombie_gp (gp14). New: gp2, gp3 ...
THIS SEQUENCE'S CAMERAS are the set's (no shared ones): move them freely. The top step is NOT yours alone (the film's
  order: it stands until gp22).
PREVIEWS through render.py: --samples 9 (PREVIEW_SAMPLES["gap"]).
"""
from engine import towers
from films import twentyminutes_common as TC


def gp13_stairs(st, s, C, nar):
    """BEAT 13  "He never took down his dirt staircase."   frames 772-833 (62 f, 2.58 s), sky gold.
    Words: He 774, never 776, took 783, down 789, his 795, dirt 799, staircase 807. The voice ends on 824 (the pause
    after the line is 0.50 s).
    Before: gm12_iron; after: gp14_gap.

    STORY: Locked tall frame of the back of the tower. A rough one-block-wide staircase of full dirt blocks zigzags up
    the clean stone and glass, stray dirt at its foot. The baby, tiny at the bottom, looks up it, then hops up the first
    two steps.
    Cast: baby villager (narrator). Effects: dirt block staircase, stray dirt blocks at the foot, baby hop up one block,
    twice.

    MUST BE SEEN, ON WHICH WORD
      frame 1           the zigzag up the back, the pod on top, the baby tiny at the foot looking up it (already moving:
                        a slow drift, or its head)
      "dirt staircase"  the baby hops up the first two steps (C.fm.climb(baby, f, 0, 1): the game's jump, 11 frames each)
    SHARED: none (the set's camera b13 = towers' back at 20 mm aimed lower).
    NEIGHBOURS: before, gm12_iron (the hopper at the foot); after, gp14_gap (the top of the stairs).
    MEASURED (the set builder, still _stairs at f0 + 6): the zigzag, the stray dirt, the pod on top; the baby tiny at the
      foot ABOVE the caption band (39 / 59 %; at 24 mm it was at 70 %, in the band). Story's "locked": a slow drift
      keeps it alive. The lead's probe: its head box x 36-41 / y 57-60 % to 802, 48-54 / 50-52 at 833 (up the steps):
      a head 5 % wide: a small thing, seen only if it is what is in focus.
    NOW (stub = the set's stage_b13): camera "set:b13", focus on the baby; the baby on stairs_foot looking up the
      stairs; the climb of steps 0-1 from "took". Hero: the baby.
    """
    f0 = s.frame_start
    baby = C.actor("baby", "gp")
    C.put(baby, f0, "stairs_foot")
    baby.look_at(f0, C.A["stairs_target"], ease=0)
    C.fm.climb(baby, C.at(s, "took"), 0, 1)
    st.use(s, baby)
    C.cam(s, "set:b13", focus=baby.head)
    st.hero(s, "baby", baby)
    C.lights(s, "tower")


def gp14_gap(st, s, C, nar):
    """BEAT 14  "At the top there's a gap, one block high."   frames 834-902 (69 f, 2.88 s), sky gold.
    Words: At 836, the 839, top 841, there's 850, a 854, gap 856, one 870, block 877, high 886. The voice ends on
    895 (the pause after the line is 0.40 s).
    Before: gp13_stairs; after: gp15_fit.

    STORY: Top of the dirt staircase at the pod's back wall. The two-block doorway is plugged with one cobblestone at
    head height, and the lower block is open. The baby hops up the last step and stands beside the opening, exactly as
    tall as it. Through the glass: beds and a straw hat.
    Cast: baby villager (narrator), Mom (farmer villager) as a shape through the glass. Effects: cobblestone plug at
    head height, one-block gap at floor level, top of the dirt staircase, baby hop up one block.

    MUST BE SEEN, ON WHICH WORD
      frame 1           the baby on the step below (already moving: it hops up the last step early in the shot)
      "gap"             the baby beside the opening, its head just under the plug: exactly as tall as the gap
      "one block high"  the plug, the gap, the baby, in one frame; beds and the straw hat through the glass
    SHARED: none (the set's camera b14 = towers' top_step_side, 26 mm f/2.8). Mom on 'mom', head on the zombie.
    NEIGHBOURS: before, gp13_stairs (the first two steps: a jump in time to the last); after, gp15_fit (inside).
    MEASURED (the set builder, still _gap at f0 + 36): the baby on the top step beside the opening, its head just under
      the plug (58 / 49 %), the beds through the glass; Mom is only a straw-hat shape at the left edge (the plug hides
      the rest of her from here). The lead's probe: ON f0 THE BABY (on the step below) IS IN THE CAPTION BAND AND THE
      ICON COLUMN (head box x 71-91 / y 59-70 %); from the hop on, x 48-69 / y 41-53 %. Mom's head on the zombie
      (0 degrees).
    NOW (stub = the set's stage_b14): camera "set:b14"; the baby placed on stairs[8], hopping up to top_step_baby at
      f0 + 8 and turning to its facing; Mom on 'mom' on the zombie; the zombie; the pane in front of Mom hidden.
      Hero: the baby.
    """
    f0 = s.frame_start
    baby = C.actor("baby", "gp")
    baby.place(f0, C.fm.set["stairs"][8], C.yaw("top_step"))
    e = towers.hop(baby, f0 + 8, C.A["top_step_baby"])
    baby.turn(e + 2, C.yaw("top_step_baby"), ease=6)
    mom = C.actor("mom", "gp")
    C.put(mom, f0, "mom")
    C.on_zombie(mom, f0, until=s.frame_end)
    C.zombie(s, "gp", look=mom)
    st.use(s, baby, mom)
    c = C.cam(s, "set:b14", focus=baby.head)
    C.fm.see_through(st, s, c, points=[mom])
    st.hero(s, "baby", baby)
    C.lights(s, "tower")


def gp15_fit(st, s, C, nar):
    """BEAT 15  "Grownups don't fit, but I do."   frames 903-954 (52 f, 2.17 s), sky gold.
    Words: Grownups 905, don't 916, fit 920, but 928, I 931, do 935. The voice ends on 944 (the pause after the line
    is 0.55 s).
    Before: gp14_gap; after: gr16_mom.

    STORY: Inside at floor level, the opening in the middle of the frame with daylight through it. The cleric walks into
    the cobblestone plug and stops, half a block to the side of the opening, twice its height. The baby runs in
    underneath, past his robe, without ducking.
    Cast: baby villager (narrator), cleric villager. Effects: one-block gap seen from inside, daylight through it,
    cobblestone plug.

    MUST BE SEEN, ON WHICH WORD
      frame 1           the cleric already walking at the plug (from inside), the gap with daylight
      "fit"             the cleric stopped against the plug, half a block west of the opening, twice the baby's height
      "do"              the baby running in under the plug, past his robe, without ducking
    SHARED: none (the set's camera b15 = towers' gap, 22 mm, inside on the floor).
    NEIGHBOURS: before, gp14_gap (outside); after, gr16_mom (the baby at Mom's side).
    MEASURED (the set builder, still _fit when the baby is in the gap): the cleric against the plug at the left (24 /
      24 %), the baby under the plug (51 / 50 %), daylight through the gap. The lead's probe: the baby's head box x
      49-61 / y 46-53 % (f0), 42-62 / 44-54 (928), out of the frame by the cut (it ran past the lens to bed_side).
    NOW (stub = the set's stage_b15): camera "set:b15", focus on the gap; the cleric walks from 1.7 south of gap_side to
      it from f0 + 2; the baby runs from the top step through gap_in to bed_side from "but" - 6. Hero: the baby.
    """
    f0 = s.frame_start
    cl = C.actor("cleric", "gp")
    gs = C.A["gap_side"]
    start = (gs[0], gs[1] - 1.7, gs[2])
    cl.place(f0, start, C.yaw("gap_side") + 3.14159265)
    cl.walk(f0 + 2, [start, gs])
    baby = C.actor("baby", "gp")
    ts = C.A["top_step"]
    baby.place(f0, (ts[0], ts[1] + 0.4, ts[2]), 3.14159265)
    baby.walk(max(f0 + 4, C.at(s, "but") - 6), [(ts[0], ts[1] + 0.4, ts[2]), C.A["gap_in"], C.A["bed_side"]],
              run=True)
    st.use(s, cl, baby)
    C.cam(s, "set:b15", focus=C.A["gap_target"])
    st.hero(s, "baby", baby)
    C.lights(s, "tower")


def gp20_nofit(st, s, C, nar):
    """BEAT 20  "Now I don't fit."   frames 1210-1255 (46 f, 1.92 s), sky gold.
    Words: Now 1212, I 1219, don't 1222, fit 1227. The voice ends on 1237 (the pause after the line is 0.85 s).
    Before: gr19_ended; after: gr21_count.

    STORY: Inside, low side view at the back wall, from far enough back that the opening sits in the middle of the
    frame and his head stays under the top icons. The grown narrator walks into the cobblestone plug and stops.
    Daylight comes through the opening at his knees. His head tilts down to it, nose in profile.
    Cast: grown narrator (unemployed adult villager). Effects: one-block gap at knee height, cobblestone plug, daylight
    through the gap onto the floor.

    MUST BE SEEN, ON WHICH WORD
      frame 1           the narrator already walking at the plug
      "fit"             he has stopped against the plug, the gap at his knees with daylight through it; his head tilts
                        down to it, nose in profile (gap_down)
    SHARED: none (the set's camera b20 = towers' gap_side, 30 mm, from OUTSIDE the east glass, panes on the lines to his
      head, knees and the gap hidden).
    NEIGHBOURS: before, gr19_ended (he has just grown up beside Mom); after, gr21_count (Steve counts them).
    MEASURED (the set builder, still _nofit at f0 + 40): the narrator at the plug (28 / 34 %), his head tilted down to
      the gap, daylight at his knees. The technical review: walking from 1.6 south he was OFF THE FRAME on f0 and cut
      by its left edge after "fit" (x 5-34 % at 1232). The stub now starts him 0.9 south (the lead's probe: head box
      x -25..6 % on f0 (entering at the left edge), 15-50 / 22-42 at 1232, 16-52 / 22-43 at the cut): he is in the
      frame before "fit" but still enters from the edge on frame 1.
    NOW (stub = the set's stage_b20): camera "set:b20" with the panes hidden; the narrator walks from 0.9 south of
      gap_adult to it from f0 + 2 (C.memo["gp_nofit_at"] = his arrival frame), then looks down to gap_down. Hero:
      the narrator.
    """
    f0 = s.frame_start
    him = C.actor("narrator", "gp")
    ga = C.A["gap_adult"]
    # (from 1.6 south he was out of the frame on f0 and still cut by its left edge after "fit": the technical review
    # and the lead's probe; from 0.9 south he is in at the edge on f0 and at the plug before "fit")
    him.place(f0, (ga[0], ga[1] - 0.9, ga[2]), C.yaw("gap_adult"))
    e = him.walk(f0 + 2, [(ga[0], ga[1] - 0.9, ga[2]), ga])
    C.memo["gp_nofit_at"] = e
    him.look_at(e + 2, C.A["gap_down"], ease=8)
    st.use(s, him)
    c = C.cam(s, "set:b20", focus=him.head)
    gt = C.A["gap_target"]
    C.fm.see_through(st, s, c, points=[(ga[0], ga[1], ga[2] + 1.6), (ga[0], ga[1], ga[2] + 0.6), gt,
                                       (gt[0], gt[1] - 0.4, gt[2]), (gt[0], gt[1], gt[2] + 1.0)])
    st.hero(s, "narrator", him)
    C.lights(s, "tower")


def gp22_step(st, s, C, nar):
    """BEAT 22  "I'm still not afraid of the player."   frames 1338-1399 (62 f, 2.58 s), sky gold.
    Words: I'm 1340, still 1344, not 1354, afraid 1360, of 1371, the 1374, player 1375. The voice ends on 1388 (the
    pause after the line is 0.60 s).
    Before: gr21_count; after: ce23_afraid.

    STORY: Past the narrator's three-quarter face, through the back glass. Steve stands one step down the dirt
    staircase, head and shoulders above the floor line. He swings at the top dirt step until it cracks and bursts into
    crumbs, then walks down out of sight. The narrator watches, perfectly still, eyes level.
    Cast: grown narrator, Steve (the player). Effects: dirt block breaking with crack stages and crumbs, at its real
    length by hand; top of the dirt staircase seen through glass; mining arm swings.

    MUST BE SEEN, ON WHICH WORD
      frame 1           Steve on one_down already swinging (the click on f0 or a few frames in)
      "afraid"          the cracks climbing the top step (17 frames by hand, ten stages)
      "player"          the step bursts into crumbs (64 particles; until= the next shot), Steve walks down out of sight;
                        the narrator's face behind the back glass, perfectly still, eyes level
    SHARED: none. FALLBACK APPLIED (the set builder): from inside, a three-quarter face and Steve through the back glass
      cannot share a frame (towers' back_glass gives a lost profile at the left edge: camera "set:b22"); the reverse
      from OUTSIDE ("set:b22o", 35 mm f/2.8 from the north-east): Steve big breaking the step in the foreground, the
      narrator's face FRONTAL behind the back glass (every pane in front of his face hidden: C.panes, 2 per line).
    NEIGHBOURS: before, gr21_count (the bed); after, ce23_afraid (the window camera: his head snaps to the zombie).
    MEASURED (the set builder, still _step_out at f0 + 14): Steve 61 / 41 %, the narrator's face 40 / 33 %, clean.
      The lead (after the technical review found Mom's place 'mom' clear in this frame beside his face, x 31 / y 34 %,
      with nobody there): MOM IS NOW IN THE STUB on 'mom', head on the zombie. tools.twentyminutes_geo gp22_step:1370:
      her head box x 20-44 / y 28-38 %, the narrator's 35-46 / 27-36 % IN FRONT of her (8.2 vs 9.1 blocks); the still
      out/test/twentyminutes_scout_gp22_step_1368_zones.png (270x480): his face frontal and clean, of her only a
      sliver of the straw hat's brim at the left of his head (the plug and he hide the rest). The probe: his head box
      x 34-46 / y 27-36 % all shot; Steve 38-73 / 32-49 %, gone by the cut.
    NOW (stub = the set's stage_b22o): camera "set:b22o", focus on the narrator; the narrator on watch_22_out facing
      one_down, eyes level; Steve on one_down looking at the step, break_top_step from f0 + 6 (until the next shot:
      cracks 1344-1360, gone from 1361), walking down three steps 8 frames after it breaks; Mom on 'mom' on the
      zombie. Heroes: the narrator, Steve.
    """
    f0 = s.frame_start
    him = C.actor("narrator", "gp")
    C.put(him, f0, "watch_22_out", toward="one_down")
    steve = C.actor("steve", "gp")
    C.put(steve, f0, "one_down")
    steve.look_at(f0, C.P_.top_step.center, ease=0)
    od = C.A["one_down"]
    him.look_at(f0, (od[0], od[1], TC.F + 1.62), ease=0)
    m = C.fm.break_top_step(steve, f0 + 6, camera=s, until=s.frame_end + 1)
    stairs = C.fm.set["stairs"]
    towers.walk_down(steve, m["frame"] + 8, [stairs[7], stairs[6], stairs[5]])
    # Mom is always at the zombie: her place 'mom' is in this frame beside his face (the technical review's
    # projection: x 31 / y 34, clear), so she is there, head on the zombie
    mom = C.actor("mom", "gp")
    C.put(mom, f0, "mom")
    C.on_zombie(mom, f0, until=s.frame_end)
    st.use(s, him, steve, mom)
    c = C.cam(s, "set:b22o", focus=him.head)
    e = him.eye_point(f0)
    C.panes(s, c["pos"], [(e[0] + dx, e[1], e[2] + dz) for dx in (-0.3, 0.0, 0.3) for dz in (-0.45, -0.2, 0.0, 0.25)],
            n=2)
    st.hero(s, "narrator", him)
    st.hero(s, "steve", steve)
    C.lights(s, "tower")
