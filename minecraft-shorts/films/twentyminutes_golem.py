"""Twenty Minutes, sequence GOLEM: the golem platform beside the pod, the kill slot with its lava, the hopper and the
chest at the foot of the tower, and the last golem. Beats 9, 10, 11, 12 and the end of 24 (shots gm09_golem,
gm10_again, gm11_lava, gm12_iron, gm24_counts), sky "gold". One function per shot; the contract is in
films/twentyminutes_common.py (tags "gm...", C.actor, C.golem, C.item, C.cam, C.lights, st.use / st.hero).

THE PLACE (engine/towers.py LAYOUT): the platform west of the pod, stone floor z 9, x -28..-25, y 17..23, the still
  water sheet on it (z 10, drawn flowing west), glass rims on stone lips along y 16 and y 24; the kill slot x -30..-29
  west of it, 4 deep, the lava blade's surface 1.1 under the rim (full-bright, its light P_.lava: level / flicker, not
  Stage.lights); the collection column under the slot's north-east corner, the chute down to the hopper (-29, 23, 1) on
  the chest (-29, 23, 0), open to the north (the hopper top is seen from the north). Anchors (C.A / C.P):
  golem_spawn (-26.5, 19.5, 10) (a cell centre: the game spawns at one), golem_24 (-25.5, 19.5, 10), slot_target,
  pod_target (the golem's look), hopper_target, poppies (-29.55, 25.4) (the baby), chest_steve (-27.75, 25.35).
THE GOLEM: C.golem() is THE golem, one for every spawn (engine/towers.py keeps the spawn / slide history on the farm);
  only this sequence uses it. Every spawn that opens a shot passes empty_from=s (C.fm.golem_spawn(..., empty_from=s));
  C.fm.golem_step, golem_slide (1.4 blocks/s west, then 4 down; gone from r["gone"]), golem_death(g, r, camera=s,
  until=s.frame_end + 1) (the white puff, glow 0.5, and the lava flicker; they end at the cut). It appears ON its frame
  with no effect (the game spawns it in one tick).
THE SCOUTING STILLS: out/test/twentyminutes_set_b09_golem.png, _b10_again_empty.png, _b10_again.png, _b11_slide.png,
  _b11_slide_strip.png, _b12_iron.png, _b24p_platform.png (+ _zones.png each); the lead's twentyminutes_scout_*.png.
  LOOK AT b09: the golem against the low sun reads PALE and low in contrast (the sun's halo is behind it; its lit side
  faces away): a film-local fill on its face side (C.fill("gm_...", ...)) or a few degrees of pan away from the sun's
  core may be needed (CAMS "platform" is YOURS: change it once, for gm09, gm10 and gm24 alike); palette_check's stone
  rule fails there at G/R 0.90 (warm sunlit stone, not magenta: accepted).
THIS SEQUENCE OWNS (the contract, amended): CAMS "platform" (gm09 = gm10 = gm24: redefine it ONCE as a constant here
  if you must, the same handheld seed in all three: the jump cut gm09 -> gm10 needs the identical framing). THREE and
  FOUR are NOT yours (ce08 and ce23 see the same people from the window).
THE ZOMBIE is in its cell in gm09, gm10 and gm24 (C.zombie(s, "gm")): from the platform its eyes project at about
  x 82 / y 52 %, between the villagers behind two glass walls (the technical review: without it the window showed empty).
LIGHT: C.lights(s, "tower").
THE PEOPLE BEHIND THE GLASS: gm09 / gm10 THREE (as in ce08: they tremble); gm24 FOUR (as in ce23), trembling, Mom's and
  the narrator's tremble matched (PANIC_SEED). Their heads stay on the zombie (C.pod does it).
TAGS TAKEN (twins): cleric_gm, librarian_gm, mom_gm, zombie_gm (gm09, gm10, gm24), narrator_gm (gm24), steve_gm,
  baby_gm (gm12), iron_ingot_gm, poppy_gm, poppy_gml0..3 (gm12). New: gm2, gm3 ...
PREVIEWS through render.py: --samples 7 (PREVIEW_SAMPLES["golem"]).
"""
import math

from engine import towers
from films import twentyminutes_common as TC


def gm09_golem(st, s, C, nar):
    """BEAT 9  "When we get scared, an iron golem comes to save us."   frames 504-591 (88 f, 3.67 s), sky gold.
    Words: When 506, we 509, get 511, scared 516, an 535, iron 538, golem 549, comes 560, to 568, save 571, us 579.
    The voice ends on 585 (the pause after the line is 0.35 s).
    Before: ce08_scared; after: gm10_again.

    STORY: Low angle on the stone platform beside the pod, still shallow water at foot level. An iron golem appears out
    of nothing in one frame, huge against the gold sky. It turns its head toward the pod, where the three villagers are
    small shapes behind the glass.
    Cast: iron golem, Mom, cleric and librarian as background shapes. Effects: golem pop-in (appears in a single frame),
    still water sheet on the platform.

    MUST BE SEEN, ON WHICH WORD
      frame 1           the empty platform, the water sheet, the three trembling behind the glass (something moving)
      "golem"           it APPEARS in one frame (on the word or just before it), huge against the gold sky
      "save"            its head turned to the pod, the three small behind the glass
    OWNED: CAMS "platform" (= gm10's and gm24's, exactly). SHARED ACROSS SEQUENCES (frozen): THREE (as ce08).
    NEIGHBOURS: before, ce08_scared (the fear, from the window); after, gm10_again (THE JUMP CUT: the same framing).
    MEASURED (the set builder, still _golem at f0 + 30, spawned on f0 + 6): the golem big at x 43 / y 35 % with the low
      sun and its gold halo at the upper left behind it, its head to the pod; the three small behind the west glass
      (x 61-86 %, y 50 %); the water sheet at foot level; the lava's orange at the bottom-left corner; the bottom 40 %
      of the frame is the platform's stone lip (the caption sits on it). The golem reads pale against the sun (above).
    MEASURED (the lead's probe, as built): the golem hidden 504-546, visible from 547 ("golem" 549) at golem_spawn;
      its head box x 39-57 / y 27-40 % (547), 40-58 / 29-42 (591); THREE's heads on the zombie within 2.8 degrees.
    NOW (stub): CAMS "platform", focus on the golem's spawn point; THREE trembling; the zombie in its cell; the golem
      spawned 2 frames before "golem", facing south (yaw 0), its head turned to the pod 10 frames later. Hero: the
      golem.
    """
    f0 = s.frame_start
    g = C.golem()
    who = C.pod(s, "gm", TC.THREE, panic=True)
    C.zombie(s, "gm", look=None)
    C.fm.golem_spawn(g, C.at(s, "golem") - 2, yaw=0.0, look=C.A["pod_target"], look_after=10, empty_from=s)
    st.use(s, g)
    C.cam(s, "platform", focus=C.A["golem_spawn"])
    st.hero(s, "golem", g)
    C.lights(s, "tower")


def gm10_again(st, s, C, nar):
    """BEAT 10  "It comes every time."   frames 592-639 (48 f, 2.00 s), sky gold.
    Words: It 594, comes 597, every 607, time 614. The voice ends on 627 (the pause after the line is 0.65 s).
    Before: gm09_golem; after: gm11_lava.

    STORY: Same framing, jump cut. The platform is empty. A new golem appears on the same block in the same pose and
    takes one step toward the pod.
    Cast: iron golem. Effects: golem pop-in, repeated; jump cut on an identical framing.

    MUST BE SEEN, ON WHICH WORD
      frame 1 .. "comes"   THE SAME FRAMING, the platform EMPTY (golem_spawn(..., empty_from=s)) for 15 frames
                        (592-606) while "It comes" is spoken: the empty platform must REGISTER (both reviews: spawned
                        on "comes" - 2 it was empty 3 frames, 125 ms on an identical framing: the same golem blinking)
      "every"           the new golem appears on the same block, in the same pose (607)
      "time"            its one heavy step toward the pod (C.fm.golem_step from "time" + 2 = 616, done by about 628,
                        11 frames of stillness before the cut)
    OWNED: CAMS "platform" (= gm09's: the jump cut needs the identical framing; keep the same handheld seed too).
      SHARED ACROSS SEQUENCES (frozen): THREE behind the glass.
    NEIGHBOURS: before, gm09_golem; after, gm11_lava (the slide, from the slot's end).
    MEASURED (the set builder, stills _again_empty at f0 + 4, _again after the step): the empty platform with the pod
      and the villagers; the new golem stepping toward the pod (its back to the lens: it steps east).
    MEASURED (the lead's probe, as built): the golem hidden 592-606, visible from 607 at (-26.50, 19.50), the step
      east to -26.05 by 639; head box x 41-59 / y 29-41 % (615), 40-55 / 33-43 (639). The camera moves 0.0008 block
      across the gm09 -> gm10 cut (the technical review).
    NOW (stub): CAMS "platform" with gm09's handheld seed; THREE trembling; the zombie in its cell; the golem spawned ON
      "every", the step from "time" + 2. C.memo["gm_golem_at"] = where it stands at the end (gm11 does not need it:
      it starts its slide where its drop lands on time). Hero: the golem.
    """
    f0 = s.frame_start
    g = C.golem()
    C.pod(s, "gm", TC.THREE, panic=True)
    C.zombie(s, "gm", look=None)
    C.fm.golem_spawn(g, C.at(s, "every"), yaw=0.0, look=C.A["pod_target"], look_after=4, empty_from=s)
    e = C.fm.golem_step(g, C.at(s, "time") + 2)
    C.memo["gm_golem_at"] = tuple(g.pos_at(min(e, s.frame_end)))
    st.use(s, g)
    C.cam(s, "platform", focus=C.A["golem_spawn"], seed=sum(ord(ch) for ch in "gm09_golem") % 89)
    st.hero(s, "golem", g)
    C.lights(s, "tower")


def gm11_lava(st, s, C, nar):
    """BEAT 11  "The water pushes it into the lava."   frames 640-707 (68 f, 2.83 s), sky gold.
    Words: The 642, water 645, pushes 655, it 665, into 669, the 673, lava 676. The voice ends on 687 (the pause
    after the line is 0.95 s).
    Before: gm10_again; after: gm12_iron.

    STORY: From the side and a little below, so the water is a still blue sheet and the lava only an orange glow in a
    slot at the platform's edge. The golem, still facing the pod, slides sideways and drops out of sight into the slot.
    A white puff rises and the glow flickers.
    Cast: iron golem. Effects: golem sideways slide and drop, white death puff, lava glow flicker (light only, no
    visible flowing lava), still water sheet.

    MUST BE SEEN, ON WHICH WORD
      frame 1           the golem already sliding (the slide starts ON f0), facing the pod (yaw +90 degrees: facing
                        the slot it reads as walking in)
      "pushes"          the sideways slide
      "lava"            over the rim and down out of sight (gone about 9 frames after the rim), the white puff rising,
                        the glow's flicker; the puff and the flicker end at the cut (until=)
    SHARED: none (the set's camera b11 = towers' slide, from the slot's open south end at the platform's level).
    NEIGHBOURS: before, gm10_again (the golem stepped toward the pod); after, gm12_iron (its iron in the hopper).
    FALLBACK APPLIED (story risk "WATER AND LAVA"): no visible flow, the still sheet, the sideways slide, the puff after
      it drops. The lava is SEEN as the game draws it (its still surface in the slot, full-bright) rather than as a
      glow only (towers' 'slide' camera at the platform's level; 'slide_low' hides the water sheet instead).
    MEASURED (the set builder, stills _slide / _slide_strip, spawn on f0, slide from f0 + 6): gone 9 frames after the
      rim; the white puff; the sun in the frame; the golem reads pale against it (as in gm09).
    NOW (stub): camera "set:b11", focus on the golem's start; the golem placed ON f0 (golem_spawn with empty_from:
      the same golem, carried on by the current between the shots) facing the pod, sliding from f0, from the x on
      golem_spawn's line that puts its head under the rim 6 frames after "lava" (_slide_start: from golem_spawn
      itself it dropped 11 frames before the cut, the lead's geo probe); golem_death with until=the next shot.
      Measured: edge 673, gone 682 ("lava" 676), the puff to the cut 707; the lead's still
      out/test/twentyminutes_scout_gm11_lava_686.png: the white puff rising out of the slot. The probe (as built):
      x -27.10 on f0, over the rim at 674 (z 9.87), the head under it at 682, the puff and the flicker to 707; head box
      x 66-79 % (f0), 41-56 (673). Hero: the golem.
    """
    f0 = s.frame_start
    g = C.golem()
    at = _slide_start(C, C.at(s, "lava") + 6 - f0)
    C.fm.golem_spawn(g, f0, pos=at, yaw=math.radians(90.0), look=C.A["pod_target"], look_after=0, empty_from=s)
    r = C.fm.golem_slide(g, f0)
    C.fm.golem_death(g, r, camera=s, until=s.frame_end + 1)
    C.memo["gm_slide"] = r
    st.use(s, g)
    C.cam(s, "set:b11", focus=at)
    st.hero(s, "golem", g)
    C.lights(s, "tower")


def _slide_start(C, frames):
    """Where the golem must stand (on golem_spawn's line, x between it and the rim) for its head to be gone under the
    rim `frames` frames after the slide starts (fixtures.slide_track: from rest, 1.4 blocks/s at full speed, 0.7
    past the rim it falls; gone when its head is below the rim). From golem_spawn itself the drop came 56 frames
    after the start, 11 frames before the cut: no time for the puff (the lead's geo probe, gm11_lava:690)."""
    from engine import fixtures
    sp = C.A["golem_spawn"]
    rim = float(C.fm.L["platform"][0])
    drop = float(C.fm.L["rim"] - C.fm.L["slot_floor"])
    best = None
    for k in range(0, 31):
        x = sp[0] - 0.05 * k
        track = fixtures.slide_track(x - rim + towers.GOLEM_SIZE[0] / 2.0, drop=drop)
        gone = next((t for t, _a, d in track if d >= towers.GOLEM_SIZE[1]), track[-1][0]) * towers.TICK
        if best is None or abs(gone - frames) < best[0]:
            best = (abs(gone - frames), x)
    return (best[1], sp[1], sp[2])


def gm12_iron(st, s, C, nar):
    """BEAT 12  "He takes the iron and leaves the poppies."   frames 708-771 (64 f, 2.67 s), sky gold.
    Words: He 710, takes 712, the 721, iron 724, and 737, leaves 740, the 748, poppies 749. The voice ends on 764
    (the pause after the line is 0.40 s).
    Before: gm11_lava; after: gp13_stairs.

    STORY: Close and shallow at the foot of the tower, the hopper in the middle of the frame. Three iron ingots and a
    poppy land on the hopper and vanish into it. Steve turns from the chest with an iron ingot in his hand and walks
    out of frame. Poppies lie spinning on the grass all around the chest. The baby stands among them, its face above
    the caption band.
    Cast: Steve (the player), baby villager (narrator). Effects: hopper and chest, iron ingots as dropped items, iron
    ingot held in Steve's hand, poppies as spinning dropped items, items vanishing into the hopper.

    MUST BE SEEN, ON WHICH WORD
      frame 1           the hopper mid-frame, the poppies spinning on the grass (already moving), Steve at the chest
      "iron"            the ingots (a stack of three, drawn as two copies as the game draws it) land on the hopper and
                        vanish into it (C.fm.deliver: one item entity per 8 ticks)
      "poppies"         a poppy lands and vanishes too; Steve with his ingot turns and walks out; the baby among the
                        lying poppies, its face above the caption band
    SHARED: none (the set's camera b12 = towers' hopper_wide re-aimed lower).
    NEIGHBOURS: before, gm11_lava (the puff out of the slot); after, gp13_stairs (the back of the tower).
    RISKS (story "IRON AND POPPIES"): ingots and a poppy are tiny in a medium shot. Fallback: a macro on the hopper with
      Steve only as a hand and boots, three poppies large on the grass in the foreground (towers' 'hopper' camera,
      30 mm f/2.8 from (-28.75, 26.0, 3.1): "set:" has no such key, its values are in engine/towers.py cameras()).
    MEASURED (the set builder, still _iron): the hopper mid-frame with an ingot on it (51 / 31 %), Steve with his ingot
      (18 / 39 %), the baby among the poppies with its face above the caption band (65 / 56 %). The lead's probe (as
      built after the technical review, which found the poppy gone by 740, before "poppies" 749): the ingots (one
      entity of 3) visible 709-726, LANDED ON 724 ("iron"), gone 727; the poppy visible 732-752, LANDED 747, lying in
      the bowl through "poppies" (749), gone 753 (C.memo["gm_deliver"]); the four lying poppies 708-771. The baby's
      head box x 57-80 / y 48-61 % (its chin on the caption band's top edge). The items are tiny at this distance:
      the story's fallback (the macro) stands.
    NOW (stub = the set's stage_b12): camera "set:b12", focus on the baby; three ingots (one entity) released 15
      frames before "iron" so they land on it, then the hopper held busy to "poppies" + 3 and one poppy released 17
      frames before "poppies" (TWO item entities, as the game's loot: golem_loot gives 3-5 ingots and 0-2 poppies);
      four poppies strewn on the grass, facing the lens; Steve on chest_steve holding an ingot, walking out 3 east /
      2 north from f0 + 30; the baby on 'poppies' looking at him. Hero: the baby.
    """
    f0, f1 = s.frame_start, s.frame_end
    ingots = C.item("iron_ingot", "gm", count=3, seed=1)
    poppy = C.item("poppy", "gm", count=1, seed=2)
    # the ingots fall out of the chute (15 frames to the bowl) and land ON "iron"; the poppy lands just before
    # "poppies" and lies in the bowl until 3 frames after the word (the hopper's pause, Hopper.busy), then vanishes
    # (the technical review: released 6 frames after the ingots it was gone by 740, before "poppies" 749; released
    # later into an idle hopper it was taken in the air on 748). The plans' (landed, gone) are in C.memo["gm_deliver"].
    plans = C.fm.deliver([ingots], C.at(s, "iron") - 15, seed=2)
    C.fm.hopper.busy(C.at(s, "poppies") + 3, ticks=0)
    plans += C.fm.deliver([poppy], C.at(s, "poppies") - 17, seed=3, land=False)
    C.memo["gm_deliver"] = [(p.get("landed"), p.get("frame")) for p in plans]
    lying = [C.item("poppy", "gml%d" % i, seed=10 + i) for i in range(4)]
    cam = TC.TS.CAMERAS["b12"]
    C.fm.strew(lying, f0, f1 + 1, seed=3, face=cam["pos"])
    steve = C.actor("steve", "gm")
    C.put(steve, f0, "chest_steve")
    steve.hold("iron_ingot")
    p = steve.pos_at(f0)
    steve.walk(f0 + 30, [tuple(p), (p.x + 3.0, p.y + 2.0, p.z)])
    baby = C.actor("baby", "gm")
    C.put(baby, f0, "poppies")
    baby.look_at(f0, steve, ease=0)
    st.use(s, steve, baby, ingots, poppy, *lying)
    C.cam(s, "set:b12", focus=baby.head)
    st.hero(s, "baby", baby)
    C.lights(s, "tower")


def gm24_counts(st, s, C, nar):
    """BEAT 24  "counts." (of: Apparently that counts.)   frames 1473-1542 (70 f, 2.92 s), sky gold.
    Words: counts 1473. The last word ends on 1487; the film holds to 1542; the last 6 frames (1537-1542) are black
    (END_BLACK).
    Before: ce23_afraid; after: the end.

    STORY (beat 24 from "counts", the story's own fallback: "cut on that word to the low-angle platform framing of line 9
    with the grown narrator now among the shapes behind the glass"): Behind the four villagers, through the glass, an
    iron golem appears out of nothing on the platform, its head above theirs, turns its head to the pod, takes one step
    and begins to slide toward the orange glow. Rack focus to it on the last word. Hold two seconds, then cut to black
    before it reaches the edge.
    Cast: grown narrator, Mom, cleric, librarian (behind the glass), iron golem. Effects: golem pop-in, golem slide
    toward the lava glow, rack focus, cut to black.

    MUST BE SEEN, ON WHICH WORD
      frame 1 ("counts" is spoken in the first frames)   CAMS "platform": the empty platform, the four trembling behind
                        the glass (where they stood in ce23: FOUR), the narrator among them
      1483 (f0 + 10)    the golem APPEARS out of nothing on golem_spawn, huge against the sun, after 10 EMPTY frames
                        (the story review: a pop-in 4 frames after a cut to a framing last seen 37 s before reads as
                        "it was there"; the viewer needs 5-8 frames to take the framing in); it turns its head to the
                        pod, takes one step, begins to slide toward the slot; keep the step off the readable frames
                        (mid-step it is a pale motion-blurred shape: the 1500 still)
      the end           the last 6 frames are black (films/twentyminutes.py END_BLACK, the encoder's): the golem must
                        not reach the rim before that (it slides 1.4 blocks/s; from golem_spawn the rim is 1.5 + 0.7
                        blocks away)
    OWNED: CAMS "platform" (gm09's framing: the story's fallback asks for exactly it). SHARED ACROSS SEQUENCES (frozen):
      FOUR (as in ce23), PANIC_SEED.
    NEIGHBOURS: before, ce23_afraid (the window shot held through "Apparently that"); after: the end (black, the Reel
      loops to frame 1).
    MEASURED (the set builder's b24p still, with OTHER places for the four: mom, bed_side, back_1, back_2): the golem
      big against the sun (43 / 35 %), the four small behind the west glass (61-77 %, y 50-52 %). With FOUR (ce23's
      places) the lead's scout stills out/test/twentyminutes_scout_gm24_counts_1490.png (+ _zones): the golem sharp
      against the sun (45 / 36 %), the four at x 61-85 % seen from BEHIND (shapes; Mom at 85 % in the icon column and
      behind the librarian's head); _1500.png: mid-step the golem is a pale motion-blurred shape.
      The lead's probe (as built): hidden 1473-1482, visible from 1483 at -26.50, the step east to -26.17 by 1511, the
      slide west from about 1514: x -26.83 at 1538, -27.06 at 1542 (the rim falls at -28.7: it never reaches it);
      head box x 42-54 / y 31-42 % (1507), 26-44 / 27-40 (1542); FOUR's heads on the zombie within 3.0 degrees.
    NOW (stub): CAMS "platform" with gm09's handheld seed, focus on the golem; FOUR trembling; the zombie in its cell;
      the golem spawned on f0 + 10 (empty_from=s: the gm11 golem is long gone), its head to the pod 6 frames later,
      one step at f0 + 28, the slide from the step's end (cut before the rim by the end of the film). Hero: the golem.
    """
    f0, f1 = s.frame_start, s.frame_end
    g = C.golem()
    C.pod(s, "gm", TC.FOUR, panic=True)
    C.zombie(s, "gm", look=None)
    fs = f0 + 10
    C.fm.golem_spawn(g, fs, yaw=0.0, look=C.A["pod_target"], look_after=6, empty_from=s)
    e = C.fm.golem_step(g, fs + 18)
    C.fm.golem_slide(g, e + 3)
    st.use(s, g)
    C.cam(s, "platform", focus=g.head, seed=sum(ord(ch) for ch in "gm09_golem") % 89)
    st.hero(s, "golem", g)
    C.lights(s, "tower")
