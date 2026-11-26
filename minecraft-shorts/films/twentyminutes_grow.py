"""Twenty Minutes, sequence GROW: Mom and the baby in the pod: never looked at, twenty minutes, the bounce on her bed,
growing up in one frame, and the player counting them and bringing one more bed. Beats 16, 17, 18, 19, 21 (shots
gr16_mom, gr17_twenty, gr18_bounce, gr19_ended, gr21_count), sky "gold". One function per shot; the contract is in
films/twentyminutes_common.py (tags "gr...", C.actor, C.cam, C.lights, st.use / st.hero).

THE PLACE: the pod (films/twentyminutes_cell.py's docstring has the whole layout). Places by towers' short names:
  mom_glass (-20.5, 18.45) at the front glass facing the zombie, baby_glass (-21.4, 18.45) 0.9 west of her, bed_side
  (-20.5, 20.45) at the red bed's foot, row_1..4 (-22.5 .. -19.5, 20.4) facing north (librarian, cleric, the narrator,
  Mom), top_step (-18.5, 24.5, 10) (Steve in gr21, outside the gap). Mom's red bed: C.fm.beds["mom"]; fm.bounce(baby,
  f, "mom", jumps=2, yaw=...) bounces a baby on it (the glass roof stops each jump 0.46 over the mattress).
THE SECOND RED BED: the film shows P_.bed2 from gr21 on (films/twentyminutes.py BED2_FROM): gr21 makes it appear ON
  Steve's swing with C.bed2_at(frame) (once; without it the film puts it on the word "bed" and prints a warning).
GROWING UP: towers.grow_up(baby, narrator, frame, look=C.zombie_eye): the baby replaced by the grown narrator (the
  unemployed adult, the plain brown robe) ON frame, same spot, same facing, no effect (undead.vanish / appear: the
  baby_gr instance is not rendered from that frame on in ANY shot; narrator_gr not before it). Mom does not turn.
THE SCOUTING STILLS: out/test/twentyminutes_set_b16_mom.png, _b17_twenty.png, _b18_bounce.png, _b19_ended.png,
  _b19_ended_strip.png, _b21_count.png (+ _zones.png each).
MOM'S HEAD IS ON THE ZOMBIE IN EVERY FRAME (C.on_zombie). The baby looks at HER (gr16), where she looks (gr17-gr19).
LIGHT: C.lights(s, "tower") (the lantern is the warm key of gr18: "warm lantern light on both").
TAGS TAKEN (twins): mom_gr, zombie_gr, baby_gr (gr16-gr19), narrator_gr (gr19, gr21), steve_gr, cleric_gr,
  librarian_gr (gr21). New: gr2, gr3 ...
PREVIEWS through render.py: --samples 10 (PREVIEW_SAMPLES["grow"]).
"""
from engine import towers
from films import twentyminutes_common as TC


def gr16_mom(st, s, C, nar):
    """BEAT 16  "Mom never looks at me, only at the zombie."   frames 955-1033 (79 f, 3.29 s), sky gold.
    Words: Mom 957, never 965, looks 972, at 978, me 981, only 994, at 1002, the 1004, zombie 1007. The voice ends
    on 1019 (the pause after the line is 0.70 s).
    Before: gp15_fit; after: gr17_twenty.

    STORY: Two-shot at the red bed. The baby stands on the lens side of Mom, pressed against her, big head tilted up at
    her and cheated toward the lens, its face clear of her sleeve. Her head stays turned away, on the zombie, whose
    arms reach from the window, soft in the background.
    Cast: baby villager (narrator), Mom (farmer villager), zombie (background). Effects: red bed, zombie cell window,
    lantern light.

    MUST BE SEEN, ON WHICH WORD
      frame 1           Mom from behind on the zombie, the baby against her on the lens side looking up at her
      "never looks"     her head on the zombie, turned away (never toward the baby or the lens)
      "zombie"          the zombie's arms in the window, soft in the background
    SHARED: none (the set's camera b16 = towers' red_bed, 35 mm f/2.8 from OUTSIDE the west glass; the panes on the
      lines to both hidden).
    NEIGHBOURS: before, gp15_fit (the baby ran in under the plug); after, gr17_twenty.
    RISKS (story "MOM NEVER LOOKS AT ME"): her head on the zombie in every pod shot; if a shot forces her to face the
      lens, frame her from behind the straw hat.
    MEASURED (the set builder, still _mom at f0 + 20): Mom from behind on the zombie, the baby pressed against her on the
      lens side looking up (47 / 58 %), the zombie soft in the window beyond.
    NOW (stub = the set's stage_b16): camera "set:b16", focus on the baby; Mom on bed_side on the zombie (aggro: raised
      arms); the baby 0.62 west of her, its body turned half to the lens, its head on her. Hero: the baby.
    """
    f0 = s.frame_start
    mom = C.actor("mom", "gr")
    C.put(mom, f0, "bed_side")
    C.on_zombie(mom, f0)
    C.zombie(s, "gr", aggro=True, look=mom)
    baby = C.actor("baby", "gr")
    bs = C.A["bed_side"]
    bp = (bs[0] - 0.62, bs[1] - 0.05, bs[2])
    cam = TC.TS.CAMERAS["b16"]
    baby.place(f0, bp, TC.yaw_to(bp, (0.5 * cam["pos"][0] + 0.5 * bs[0], 0.5 * cam["pos"][1] + 0.5 * bs[1])))
    baby.look_at(f0, mom, ease=0)
    st.use(s, mom, baby)
    c = C.cam(s, "set:b16", focus=baby.head)
    C.fm.see_through(st, s, c, points=[mom, baby])
    st.hero(s, "baby", baby)
    C.lights(s, "tower")


def gr17_twenty(st, s, C, nar):
    """BEAT 17  "Childhood here lasts twenty minutes."   frames 1034-1091 (58 f, 2.42 s), sky gold.
    Words: Childhood 1036, here 1048, lasts 1054, twenty 1063, minutes 1071. The voice ends on 1082 (the pause after
    the line is 0.50 s).
    Before: gr16_mom; after: gr18_bounce.

    STORY: Locked-off side view against the front glass, the village and the well small and golden far below. Mom in
    profile. The baby stands 0.9 block from her along the glass, and the top of its head is level with her folded arms.
    Nothing moves but the zombie's arms at the frame edge. This exact framing returns two lines later.
    Cast: baby villager (narrator), Mom (farmer villager), zombie (frame edge). Effects: locked camera, reused for the
    growing-up shot; village seen far below through the front glass.

    MUST BE SEEN, ON WHICH WORD
      frame 1           the locked framing (the handheld only), Mom in profile, the baby 0.9 from her
      "twenty minutes"  the top of the baby's head level with her folded arms: Mom is the height ruler
    SHARED: CAMS "grow" (= gr19's EXACTLY: the same handheld seed in both), towers' mom_glass and baby_glass.
    NEIGHBOURS: before, gr16_mom; after, gr18_bounce.
    MEASURED (the set builder, still _twenty at f0 + 24, re-aimed at 20 mm): Mom in profile (30 / 33 %), the baby at her
      arms (62 / 52 %), the lantern glowing at the right edge, the village's roofs small and golden below. The zombie's
      arms are not in that frame (the story's "at the frame edge"): say so if you find them.
    NOW (stub = the set's stage_b17): CAMS "grow" with the seed shared with gr19, focus on Mom; Mom on mom_glass on the
      zombie; the baby on baby_glass looking where she looks (the zombie). Heroes: Mom, the baby.
    """
    f0 = s.frame_start
    mom = C.actor("mom", "gr")
    C.put(mom, f0, "mom_glass")
    C.on_zombie(mom, f0)
    C.zombie(s, "gr", look=mom)
    baby = C.actor("baby", "gr")
    C.put(baby, f0, "baby_glass")
    C.on_zombie(baby, f0)
    st.use(s, mom, baby)
    C.cam(s, "grow", focus=mom.head, handheld=0.004, seed=GROW_SEED)
    st.hero(s, "mom", mom)
    st.hero(s, "baby", baby)
    C.lights(s, "tower")


GROW_SEED = 17                         # the handheld of CAMS "grow" in gr17 AND gr19 (the same drift: the same frame)


def gr18_bounce(st, s, C, nar):
    """BEAT 18  "I spent mine with her."   frames 1092-1142 (51 f, 2.12 s), sky gold.
    Words: I 1094, spent 1097, mine 1105, with 1114, her 1119. The voice ends on 1124 (the pause after the line is
    0.90 s).
    Before: gr17_twenty; after: gr19_ended.

    STORY: Closer. The baby bounces twice on Mom's red bed, as baby villagers do, then stands beside her and turns its
    head to look where she looks. Warm lantern light on both.
    Cast: baby villager (narrator), Mom (farmer villager). Effects: baby bouncing on the red bed, lantern as key light.

    MUST BE SEEN, ON WHICH WORD
      frame 1           the baby already in the air (the bounce starts ON f0: it is in gr17 before, so no pre-roll)
      "spent"           the two bounces (fm.bounce jumps=2, about 1.05 s under the glass roof)
      "her"             then beside her, its head turned to look where she looks (the zombie)
    SHARED: none (the set's camera b18 = towers' bounce, 24 mm, the red bed from the east).
    NEIGHBOURS: before, gr17_twenty; after, gr19_ended (CAMS "grow" again).
    MEASURED (the set builder, still _bounce at f0 + 8): the baby mid-bounce facing the lens (71 / 43 %, motion-blurred:
      it is in the air), Mom's hat at the left edge.
    NOW (stub = the set's stage_b18, from f0): camera "set:b18", focus on the baby; fm.bounce(baby, f0, "mom", jumps=2,
      yaw cheated toward the lens); Mom on bed_side on the zombie. (The stand beside her after the bounce is not
      staged.) Hero: the baby.
    """
    f0 = s.frame_start
    baby = C.actor("baby", "gr")
    cam = TC.TS.CAMERAS["b18"]
    bp, mp = C.fm.beds["mom"]["pos"], C.A["bed_side"]
    toward = (0.65 * cam["pos"][0] + 0.35 * mp[0], 0.65 * cam["pos"][1] + 0.35 * mp[1])
    C.fm.bounce(baby, f0, "mom", jumps=2, yaw=TC.yaw_to(bp, toward))
    mom = C.actor("mom", "gr")
    C.put(mom, f0, "bed_side")
    C.on_zombie(mom, f0)
    C.zombie(s, "gr", look=mom)
    st.use(s, baby, mom)
    C.cam(s, "set:b18", focus=baby.head)
    st.hero(s, "baby", baby)
    C.lights(s, "tower")


def gr19_ended(st, s, C, nar):
    """BEAT 19  "I was still inside when it ended."   frames 1143-1209 (67 f, 2.79 s), sky gold.
    Words: I 1145, was 1148, still 1150, inside 1157, when 1173, it 1175, ended 1178. The voice ends on 1188 (the
    pause after the line is 1.00 s).
    Before: gr18_bounce; after: gp20_nofit.

    STORY: The locked framing again. The baby stands at Mom's folded arms. On the last word it snaps in a single frame to
    a full-size villager in a plain brown robe, head level with hers, as in the game, with no puff. Mom does not turn.
    Hold one second.
    Cast: baby villager (narrator), grown narrator (unemployed adult villager, plain brown robe), Mom (farmer villager).
    Effects: single-frame swap from baby to adult on the same spot, identical framing to the twenty minutes shot.

    MUST BE SEEN, ON WHICH WORD
      frame 1 .. "ended" - 1   the baby at Mom's arms (at least 12 frames before the swap: the story's risk)
      "ended"           THE SWAP, in one frame, on the word: the grown narrator, same spot, same facing, his head level
                        with hers; Mom does not move
      to the end        held (a second and more: the pause after the line is 1.0 s)
    SHARED: CAMS "grow" (= gr17's EXACTLY, the same handheld seed GROW_SEED).
    NEIGHBOURS: before, gr18_bounce; after, gp20_nofit (he cannot get out).
    RISKS (story "GROWING UP"): a one-frame swap can look like a glitch or a jump cut. Fallback (applied): the camera
      locked on exactly the twenty-minutes framing with Mom as the height ruler, twelve frames held before and a second
      after, the snap timed to the word "ended". If it still does not read: a small white puff (not vanilla) is the
      story's last resort: say so, do not add it.
    MEASURED (the set builder, _ended_strip: the frame before and the frame of the swap): it reads as the same villager
      grown, head level with Mom's, same pose.
    NOW (stub = the set's stage_b19 on the word): CAMS "grow" with GROW_SEED, focus on Mom; Mom on mom_glass on the
      zombie; the baby on baby_glass on the zombie; towers.grow_up on "ended" (look = the zombie). Heroes: Mom, the
      narrator.
    """
    f0 = s.frame_start
    mom = C.actor("mom", "gr")
    C.put(mom, f0, "mom_glass")
    C.on_zombie(mom, f0)
    C.zombie(s, "gr", look=mom)
    baby = C.actor("baby", "gr")
    C.put(baby, f0, "baby_glass")
    C.on_zombie(baby, f0)
    him = C.actor("narrator", "gr")
    towers.grow_up(baby, him, C.at(s, "ended"), look=C.zombie_eye)
    st.use(s, mom, baby, him)
    C.cam(s, "grow", focus=mom.head, handheld=0.004, seed=GROW_SEED)
    st.hero(s, "mom", mom)
    st.hero(s, "narrator", him)
    C.lights(s, "tower")


def gr21_count(st, s, C, nar):
    """BEAT 21  "He counted us twice, then brought one more bed."   frames 1256-1337 (82 f, 3.42 s), sky gold.
    Words: He 1258, counted 1260, us 1269, twice 1272, then 1292, brought 1298, one 1305, more 1311, bed 1316. The
    voice ends on 1326 (the pause after the line is 0.60 s).
    Before: gp20_nofit; after: gp22_step.

    STORY: High over Steve's shoulder, the glass roof hidden to the camera, wide lens tilted down. Four villagers in a row
    face him, their faces in the upper third: librarian, cleric, the narrator, Mom. The librarian and the cleric turn
    their heads away, Mom's is on the zombie, and only the narrator looks straight up at him. His head moves along the
    row, and back again. His arm swings and a second red bed appears beside Mom's in the middle of the frame, above the
    caption band.
    Cast: Steve (the player), grown narrator, Mom, cleric, librarian. Effects: Steve's head panning along the row and
    back, arm swing, second red bed placed beside Mom's (pops in, no particles), glass roof hidden to the camera.

    MUST BE SEEN, ON WHICH WORD
      frame 1           the four in a row, Steve's head already turning (steve.watch along the row)
      "counted" .. "twice"   his head along the row and back (twice: the story's count)
      "bed"             he sneaks (from a sneaking eye the ray to the bed's cell passes under the plug: towers),
                        swings, and THE SECOND RED BED APPEARS beside Mom's, mid-frame above the caption band:
                        C.bed2_at(frame) on the swing (the film shows P_.bed2 in this shot and every one after)
    SHARED: the second bed (C.bed2_at here, nowhere else).
    NEIGHBOURS: before, gp20_nofit; after, gp22_step (he breaks the top step).
    RISKS (story "HE COUNTED US TWICE"): two actions in one shot of about four seconds, the count shown as the back of
      Steve's head turning. Fallbacks: cut on the comma (a front view of Steve's head panning along the row and back,
      then the bed): NOT taken, the plan has one shot here (a front view of his face from inside is behind the plug:
      he stands on top_step right behind it); or drop the count to a single slow sweep.
    MEASURED (the set builder, still _count at f0 + 76): the four in a row (38-75 %, y 40-44 %), the two red beds side
      by side in the middle (the second at y 58 %), the back of Steve's head at the bottom.
    NOW (stub = the set's stage_b21, on the words): camera "set:b21" (towers' high, roof hidden), focus on the narrator;
      the four on row_1..4; the librarian and the cleric look away, Mom on the zombie, the narrator up at Steve; Steve
      on top_step watches the librarian to "twice", Mom to "then", sneaks on "brought", swings 4 frames later, the bed
      appears 2 frames after the swing. Heroes: the four.
    """
    f0 = s.frame_start
    steve = C.actor("steve", "gr")
    C.put(steve, f0, "top_step")
    row = []
    for i, role in enumerate(("librarian", "cleric", "narrator", "mom")):
        c = C.actor(role, "gr")
        C.put(c, f0, "row_%d" % (i + 1))
        row.append(c)
    for c in row[:2]:
        p = c.pos_at(f0)
        c.look_at(f0, (p.x - 3.0, p.y - 1.0, TC.F + 1.6), ease=0)
    row[2].look_at(f0, steve, ease=0)
    C.on_zombie(row[3], f0)
    t1, t2 = C.at(s, "twice"), C.at(s, "brought")
    steve.watch(f0, t1, row[0])
    steve.watch(t1 + 1, t2 - 1, row[3])
    steve.sneak(t2)
    steve.attack(t2 + 4)
    C.bed2_at(t2 + 6)
    st.use(s, steve, *row)
    st.see_through(s, "tower_pod_roof")
    C.cam(s, "set:b21", focus=row[2].head)
    for c in row:
        st.hero(s, c.name, c)
    C.lights(s, "tower")
