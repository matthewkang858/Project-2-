"""THE SETS OF "TWENTY MINUTES" (stories/ironfarm.json): a film-local set module, built INTO the seed-1 village through
village.build_village(edit=...) exactly as engine/sets.py builds hello_set. Nothing in engine/ is changed: the whole
iron farm is engine/towers.py's (built for this film); this file wraps it, adds what the beats need beyond it (beat
1's flight into house_c, the window cameras of beats 8 / 23 / 24, a platform camera with the sun for beats 9 / 10 /
24p, the reverse of beat 22, film-only anchors), and proves one camera per beat with a still.

    from films import twentyminutes_set as TS
    v = TS.build_set(scene)              # = village.build_village(scene, seed=1, edit=TS.twentyminutes_set)
    P = TS.make_parts(v)                 # P.farm (towers.Farm: every call of the farm at work), P.pod, P.bed2, P.hopper,
                                         #   P.chest, P.water, P.lava, P.top_step, P.door (house_c's)
    D = TS.data(v)                       # anchors, paths, parts, cutaways, lights, cameras (the beat's camera first)
    TS.SKIES                             # the one sky every still was made under (copy into films/twentyminutes.py)
    TS.CAMERAS["b08w"]                   # dict(pos, target, lens, fstop[, pos1, target1, ease], what, sky, from_)
    TS.BEAT_CAMERAS[8]                   # ["b08w", "b08"]: the suggested camera of beat 8 first, then alternatives

    $BPY -m films.twentyminutes_set                      # THE SELF-TEST (numbers, about 60 s under load): builds the set,
                                                         #   stages every beat, checks anchors / cameras / heroes
    $BPY -m films.twentyminutes_set b09: b11:strip       # stills out/test/twentyminutes_set_<beat>_<what>.png (+ _zones);
                                                         #   'bNN:' = its main frame, 'bNN:tag' = a tagged frame, 'bNN'
                                                         #   = every frame it names; ONE build (10-15 s) per command,
                                                         #   then 80-140 s per 540x960 / 16-sample still on this machine
                                                         #   under load (one or two per command under `timeout 290`)
    $BPY -m films.twentyminutes_set b09 --dry            # no render: where every hero lands in the frame, what hides it
    $BPY -m films.twentyminutes_set b09: --palette       # + tools/palette_check on the still (slow: 60+ s more)

THE SKY (one for the whole film, as the story asks: "golden hour, sun about 27 degrees up ... a Minecraft day is twenty
minutes, so the sun is truly back in the same place when the narrator grows up")
    gold  dict(preset="golden", az=62.0, el=27.0, bloom=1.0, grade="warm")   (Blender azimuth: degrees counter-clockwise
          from east: the sun stands in the north-north-east). Every still of this file and every proof of engine/towers.py
          was made under it. Why this sun: the pod's villagers face EAST (the zombie's cell) and are lit by it through the
          glass in every pod shot; the plaza camera looks north-west at the tower with the sun about 85 degrees off its axis
          (side light); the back of the tower (the dirt zigzag, beat 13) faces it; and from the platform camera of beats 9 /
          10 / 24p the sun stands at the upper left behind the golem's head: "huge against the gold sky". From inside the
          pod looking south (beats 17 / 19) it is behind the lens: the village below is lit, the faces front-lit (flat:
          accepted, the frame is about the two heights). Not tested: any other sky (the story has one).

WHERE EVERY BEAT IS FILMED (Blender blocks: +X east, +Y north, +Z up; ground z 0; the pod's floor top z 10)
    THE SQUARE (beats 1-4): the plaza east of the well (the well x -3..2, y -3..2); the camera low on the path east of it
      at (9.3, -0.6), looking north-west over the well at the tower above the roofs (house_c left, house_e right).
    THE FOOT OF THE TOWER (5 at its front, 12 at the collection niche on its north-west, 13 at the back staircase).
    THE POD (6-8, 14-24): inside x -23..-19, y 18..22, z 10..11 (2 high), glass ring x -24..-18, y 17..23, glass roof z 12;
      the zombie cell (-18, 19) in the east wall (the sill (-19, 19, 10) on the pod's floor, open window above it); the
      gap (-19, 23, 10) under the cobblestone plug (-19, 23, 11) in the back (north) wall; beds along the north row (white
      (-23, 21..22), white (-22, 21..22), Mom's red (-21, 21..22), the second red bed (-20, 21..22) from beat 21).
    THE PLATFORM (9-11, 24p): west of the pod, x -28..-25, y 17..23 at z 9 with the water sheet on it; the kill slot x
      -30..-29 (lava 1.1 under the rim); glass rims on y 16 / 24.
    THE STAIRCASE (13, 14, 21, 22): ten dirt blocks up the back from (-17, 23, 0) to the top step (-19, 24, 9).

THE HOOK (twentyminutes_set(b)): towers.iron_farm(b) with its defaults (at (-23, 18), floor 10, glass rims, the water
    sheet), the film's anchors 'tm_*' and paths 'tm_*' (ANCHORS, PATHS, DOOR_PATHS below), and the plants cleared off the
    ground lines of the film's low cameras and paths. Village.sets['twentyminutes'] = dict(farm (towers' dict),
    cameras, anchors, paths). The village with the tower is 77,337 faces.

THE PARTS (make_parts(v); towers' own objects: register what a shot shows with the Stage, st.cast[p.name] = p; st.use)
    P.farm      towers.Farm: zombie_in_cell, golem_spawn / golem_step / golem_slide / golem_death, deliver, strew,
                break_top_step, climb, bounce, see_through (its docstring is the manual; tools/towers_proof.py and the
                stage_bNN functions below are worked examples)
    P.pod       fixtures GlassBox; cutaways tower_pod_north / _east / _south / _west / _roof / _all (Stage.see_through);
                single panes: P.farm.see_through(st, s, camera, points=[...]) or pod_panes() below (several per line)
    P.bed2      the second red bed (fixtures Bed, foot (-20, 22), pillow (-20, 21), facing south as Steve places it):
                REGISTER IT (st.cast[P.bed2.name] = P.bed2) and st.use it in beat 21 and every shot after (built
                unregistered it is in EVERY shot from frame 1: fixtures.bed without frame= is there from the start);
                P.bed2.place_at(f) in beat 21 makes it appear on f
    P.top_step  the breakable top dirt step (-19, 24, 9) (engine.breaking): do NOT register it with the Stage unless
                you st.use it in every shot that shows it (beats 13, 14, 15, 20, 21, 22): registered, it is hidden in
                every other shot and the baby of beat 14 floats (that is tools/towers_proof.py's b14 still); unregistered
                it is there until break_top_step removes it (beat 22) and gone after, which is the film's order
    P.hopper, P.chest, P.water, P.lava   fixtures; lava: P.lava.level(f, scale), the flicker comes with golem_death
    P.door      house_c's door (beat 1): v.door_open("house_c", f) / v.door_open("house_c", f, open=False)
    LIGHTS      Stage.lights(s, scale=1.0, groups=POD_LIGHTS) in every shot (POD_LIGHTS: the pod's lantern
                'tower_pod' and the cell's wall torch 'tower_cell' at 1.0); the plaza's torches at their own level.

ANCHORS (Village.anchors; towers' as 'tower_<short>' = P.farm.A[short] with P.farm.yaw[short]; the film's as 'tm_<name>')
    towers' (see engine/towers.py ANCHORS for all): mom (-20.5, 19.5), mom_glass (-20.5, 18.45), baby_glass (-21.4,
    18.45), bed_side (-20.5, 20.45), bed_beside (-19.5, 21.4: before bed2 only), back_1 (-22.55, 19.4), back_2 (-22.55,
    20.4), back_3 (-21.6, 18.4), row_1..4 (-22.5 .. -19.5, 20.4), gap_in (-18.5, 22.66), gap_adult (-18.5, 22.3), gap_side
    (-19.0, 22.66), gap_down / gap_target, watch_22 (-20.3, 20.5), zombie (-17.7, 19.5) + P.farm.zombie_eye (z 11.74),
    top_step (-18.5, 24.5, 10), top_step_baby (-18.28, 24.42, 10), one_down (-19.5, 24.5, 9), golem_spawn (-26.5,
    19.5, 10), golem_24 (-25.5, 19.5, 10), square_baby (6.38, 1.16), push_baby (8.9, 6.0), foot_front (-20.5, 16.45),
    stairs_foot (-15.4, 24.3), poppies (-29.55, 25.4), chest_steve (-27.75, 25.35), pod_target, hopper_target,
    stairs_target, slot_target. Paths tower_steve_square, tower_steve_past, tower_push_square.
    the film's (ANCHORS / PATHS / DOOR_PATHS below): tm_baby_square (= square_baby), tm_armorer_from (-5.8, 7.9),
    tm_shepherd_from (-4.9, 8.8), tm_house_c_door_target (-10.0, 6.5, 2.0); tm_narrator_23 (-20.55, 19.7), tm_mom_23
    (-20.55, 18.7), tm_librarian_23 (-21.8, 18.75) (beat 23 from the window); tm_watch_22_out (-20.6, 20.45) (beat 22
    from outside). Paths tm_steve_square (= tower_steve_square), tm_steve_past (= tower_steve_past), tm_flee_armorer /
    tm_flee_shepherd (from their spots into house_c through its door: the last nodes are the village's own
    square_to_house_c: the oak-stairs step (-10, 6), the door cell (-11, 6), (-11.9, 6.5, 1.0) inside).

THE CAMERAS (CAMERAS; BEAT_CAMERAS[beat] = the suggested key first). Every one was rendered with its beat staged by
    stage_<key> below (the film's cast on the anchors, acting as the story says, in film order in one build) at 540x960,
    16 samples, motion blur, under SKIES["gold"], with the Reels zones drawn: out/test/twentyminutes_set_<key>_<what>
    [_<tag>].png and _zones.png, and LOOKED AT. "x / y" = where a head lands (% of the frame, from the top-left) on the
    still's frame (where(): Blender's projection of the eye point).
    b01   plaza (9.3, -0.6, 0.75) -> (-21.85, 18.65, 1.0), 40 mm f/2.8 (towers 'square' raised 0.2 and panned 3.6 degrees
          left so house_c's door is in): the baby lower middle in profile from behind (x 48 / y 56), Steve coming at the
          lens on the right (73 / 41), the armorer and the shepherd running into house_c (13 / 45, 23 / 46: their heads
          and shoulders over the well's base), the door (10 / 44) shuts behind the second (tag 'door', frame 55), the
          tower above the roofs (the pod's front y 17 %). Stills _afraid, _afraid_door.
    b02   towers 'baby_face' (4.69, 2.57, 0.72) -> the baby, 50 mm f/2: its face front three-quarter, the upper half
          (50 / 44), the plaza soft. Steve's legs cross the lens on tm_steve_past from frame f0 + 6 (they are in the
          frame only for about 4 frames at 50 mm: time the walk to the word). Still _imnot.
    b03   towers 'push_square' (3.3, 9.6, 0.65) 18 mm, panning LINEAR from (6.2, 6.0, 0.95) to (3.0, 6.0, 0.95) over 3.5 s
          (towers' target1 (0.6, 6.0) outran the push, 0.9 blocks/s); Steve shoving Mom (44 / 43: hat brim and nose to
          the lens); the baby runs in from the left edge. Still _push.
    b04   the tilt: towers 'square_start' (-> (3.0, 2.5, 0.7)) to b01's framing exactly ((-21.85, 18.65, 1.0) from z
          0.75), 40 mm: the well's east side and the baby, then the tower above the roofs over the baby's head; Mom at
          the glass is a few pixels. Still _tilt_b (the end). TANGENT (fixed after the reviews of the film's plan): the
          plaza lamp post at (-7, 9) stood right behind the baby's head (its torches stuck out of the head's top); the
          lead measured that moving the baby 0.25 to the lens' right does NOT clear it (the lamp at x 53 % stays inside
          the head's box, x 35-82 %), so the hook now TAKES THE LAMP POST OUT (LAMP_OUT, _take_out: this film's village
          has no lamp there; its two torches and their light go with it). The stills of b01 / b04 predate this. The
          film's own tilt and plaza framings are in films/twentyminutes_common.py CAMS "tilt" / "plaza" (lens z 0.55).
    b04_long  the story's own fallback, the cut inside the line: towers 'square_long' 200 mm f/2.8 from the plaza; every
          pane between the lens and Mom's head, face and shoulders hidden (pod_panes(n=3): a grazing line crosses two
          or three); the straw hat, the face and the nose in profile at 50 / 51, the far walls' frames behind her (it
          reads as glass), her face clear of pane lines. Still _hat.
    b05   towers 'foot', 35 mm: the baby at the tower's front, front three-quarter, the folded arms in the middle (y 52),
          head far up, the stone base behind. Still _arms.
    b06   towers 'pan_bed' 24 mm: _bed_a the red bed lengthwise from its foot, the white beds beside it, Mom's hat at
          the right edge; _bed_b the zombie filling the window over the sill, arms out, under the slab.
    b07   towers 'two_shot' 45 mm (tower_pod_north hidden from the camera): the green arms out of the window at the left,
          the sill, one empty block, Mom in profile at the right (76 / 49), her red bed in the foreground. Still _reach.
    b08w  SUGGESTED (the story's 'arm at the frame edge', which towers called impossible from beside the cell): the lens
          in the pod's east column just north of the window, (-18.05, 20.15, 11.38) -> (-22.6, 19.3, 11.3), 18 mm f/2.8,
          0.13 from the zombie's right arm (arms forward, NOT aggro: raised they leave the frame): that arm is a dark
          green blur down the left edge (pixels (46, 68, 37)); Mom (back_3) 20 %, the cleric (back_1) 46 %, the
          librarian (back_2) 66 %, all at y 47-48 %, faces toward the lens, trembling; the lantern, the sill blurred
          along the bottom, a red bed at the right edge. Still _window. (b08 = towers 'cell_side': the three at 30 / 57 /
          78 %, no arm.)
    b09   NEW: over the slot's south end at the platform's level, (-29.3, 17.3, 10.35) -> (-24.3, 20.55, 11.45), 16 mm
          f/4: the golem big in the middle (43 / 35) with the low sun and its gold halo at the upper left behind it
          ("huge against the gold sky"), its head turned to the pod; the three small behind the west glass (61-86 %, y
          50 %), the water sheet at foot level, the lava's orange at the bottom-left corner. Still _golem.
    b10   b09's framing exactly (the jump cut): _again_empty = the platform empty on f0 + 4 (the glass pod with the
          three in it, the sun, the sheet); _again = the new golem (spawned f0 + 5) after its heavy step toward the pod
          (48 / 37): it has turned its back to us to step east (the story's "one step toward the pod").
    b11   towers 'slide' 20 mm (from the slot's open south end): the golem, facing the pod (yaw +90), slides west and
          drops into the slot (gone 9 frames after the rim), the white puff rises, the sun in the frame; the lava is
          seen as the game draws it (a surface in the slot), the water as a pale sheet behind the glass rim. Stills
          _slide (at the edge) and _slide_strip (spawned / at the edge / dropping / the puff).
    b12   towers 'hopper_wide' re-aimed 0.35 lower (target z 0.15): the hopper in the middle with an ingot on it
          (51 / 31), the chest below, Steve with his ingot at the left (18 / 39), the baby among the poppies at the right
          with its face above the caption band (65 / 56). Still _iron.
    b13   towers 'back' at 20 mm aimed 2.2 lower ((-17.4, 22.5, 3.0)): the dirt zigzag up the back, the stray dirt, the
          pod on top; the baby tiny at the foot ABOVE the caption band (39 / 59; at 24 mm it was at 70 %). Still _stairs.
    b14   towers 'top_step_side' 26 mm: the baby on the top step beside the opening, its head just under the plug
          (58 / 49), the beds through the glass, Mom's hat a shape at the left edge (the plug hides the rest of her from
          here). The top step is there under it (unregistered: see THE PARTS). Still _gap.
    b15   towers 'gap' 22 mm (inside at floor level): the cleric against the plug at the left (24 / 24), the baby
          running in under the plug (51 / 50), daylight through the gap. Still _fit.
    b16   towers 'red_bed' 35 mm from outside the west glass (panes hidden): Mom from behind on the zombie, the baby
          pressed against her on the lens side looking up (47 / 58), the zombie's head and arms soft in the window
          beyond. Still _mom.
    b17   towers 'grow' position (-21.0, 21.3, 11.35), re-aimed at (-21.05, 18.45, 10.75), 20 mm, locked: Mom in
          profile at the front glass (30 / 33), the baby at her folded arms (62 / 52), the lantern glowing at the right
          edge, the village's roofs small and golden below through the front glass. Still _twenty. (towers' 24 mm aim
          left the baby's head 59 % inside the safe area: x 60-88 %, y 50-65 %.)
    b18   towers 'bounce' 24 mm: the baby on Mom's red bed facing the lens mid-bounce (71 / 43, motion-blurred: it is in
          the air), her hat at the left edge. Still _bounce.
    b19   b17's framing exactly: _ended_strip = frame f - 1 (the baby at Mom's arms) and f (the grown narrator in the
          plain brown robe, same spot, same facing, his head level with hers; Mom does not move): it reads as the same
          villager grown; _ended = six frames after the swap (540x960).
    b20   towers 'gap_side' 30 mm from outside the east glass (panes hidden): the narrator at the plug (28 / 34), his
          head tilted down to the gap, nose in profile, daylight through the gap at his knees. Still _nofit.
    b21   towers 'high' aimed 0.5 lower (target z 10.3), 22 mm, the roof hidden: Mom, the narrator, the cleric, the
          librarian in a row (38 / 51 / 63 / 75 %, y 40-44 %), the two red beds side by side in the middle (the second
          at y 58 %), the back of Steve's head at the bottom. Still _count (frame f0 + 76, after the bed appeared).
    b22o  SUGGESTED (NEW, the reverse from outside; the story's three-quarter face cannot share a frame with Steve from
          inside): (-17.6, 28.0, 10.3) -> (-19.71, 23.47, 10.21), 35 mm f/2.8; Steve big on one_down swinging at the
          top step (61 / 41), the narrator on tm_watch_22_out facing him through the back glass (40 / 33), his face
          frontal and clean: every pane in front of it hidden (pod_panes, two per line over 12 points round his face;
          with one hidden a pane frame crossed his brows). Still _step_out. (b22 = towers 'back_glass': the narrator
          a lost-profile blur at the left edge (9 %), Steve small through the back glass (63 / 52).)
    b23w  SUGGESTED: b08w's camera position, aimed 0.35 more south: the zombie's arm the dark green blur at the left
          edge; Mom (26 %) and the narrator (57 %) side by side, same height, trembling alike, both staring at the
          lens' side; the librarian between them behind (41 %), the cleric on back_2 (79 %); a red bed at the right edge.
          Still _window. (b23 = towers 'cell_side' with towers' spots: the narrator at 13 %, no arm, the beds behind
          the lens.)
    b24p  SUGGESTED for the word "counts" (the story's own fallback: "cut on that word to the low-angle platform
          framing of line 9 with the grown narrator now among the shapes behind the glass"): b09's camera, the golem
          big against the sun (43 / 35), the four small behind the west glass (narrator on back_2 61 %, Mom on back_1
          72 %, the cleric on 'mom' 77 %, the librarian on bed_side 69 %, y 50-52 %). Still _platform.
    b24w  b23w's shot held: the golem spawned on golem_spawn lands at x 66 % / y 43 %, which is the right edge of the
          narrator's head: on the still it is NOT visible (hidden behind him). Its head cannot be above theirs from
          this low lens (it would need the lens above z 11.6). Use b24w only up to "counts", then cut to b24p; or move
          the spawn: a golem whose head shows in the gap between the narrator and the cleric needs x ~70 %, i.e. y
          19.84 at x -26.5 (not a cell centre: the game spawns at one). Still _window.
    b24   towers 'cell_side' (the golem on golem_24 between the cleric and the librarian, 67 / 44, its head a little
          above theirs, small behind the glass as the story's risk expects); continues b23. Still _counts.

LIMITS THAT REMAIN (geometry or the game; the fallbacks applied are named)
    - Beat 1: the low plaza camera sees the well's base between it and the two who flee: only their heads and
      shoulders show over it. (The lamp post at (-7, 9) that stood behind the baby's head is taken out: see b04.)
    - Beat 2: "his shadow crosses its face": under this sun (north-north-east) Steve's shadow falls south-west, away
      from the baby, whichever side of the lens he passes. Not had.
    - Beat 4: the orange glow under the platform rim and the dirt zigzag cannot be seen from the square (the slot is
      behind the pod's west side, the stairs on its back; the slot's lava sits 0.1 under its end walls' tops): the
      story's fallback (cut inside the line to the long lens: b04_long) is applied for Mom; the glow and the zigzag
      are seen in beats 9-11 and 13 instead.
    - Beats 8 / 23: the zombie's arm reads as a blur only (it is 0.1-0.4 from the lens); with aggro arms (raised) it
      leaves the frame: keep the zombie's arms forward (zombie_in_cell(aggro=False)) in the window shots.
    - Beat 22: a three-quarter face and Steve through the back glass in one frame: impossible inside; b22o is the
      reverse (his face frontal through the glass behind Steve).
    - Beat 23: "the two red beds below them": the beds are north of the four, never below them from a camera beside
      the cell (one red bed shows at the right edge of b23w).
    - Beat 24: the golem's head above theirs needs a lens above z 11.6 (the cell_side height, where the arm is lost);
      from the window it is hidden behind the narrator (b24w); applied: the story's own fallback, the cut on "counts"
      to the platform framing (b24p). b24 (cell_side) keeps the "same shot, held" if beat 23 is b23.
    - Beat 11: the lava is seen as a surface in the slot (the game's still lava texture, full-bright), not "a glow
      only": it reads as Minecraft and the drop into it reads.

GOTCHAS FOUND ON THE STILLS
    - towers.push keys the WHOLE route at 0.9 blocks/s: keys past the shot's end override the next shot's place() (the
      full tower_push_square, 7 blocks / 7.6 s, put Mom back on the plaza behind the baby in beat 4). Push only as far
      as the shot lasts (stage_b03: 0.85 blocks per second of shot).
    - P.bed2 and P.top_step: see THE PARTS (register bed2, do not register the top step).
    - The window cameras (b08w / b23w / b24w) stand 0.13 from the zombie's right arm: keep its arms forward
      (aggro=False), raised arms leave the frame; the arm blur is dark green (46, 68, 37) on b08w's left edge.
    - The golem of beat 11 must face the pod (yaw +90 degrees) as it slides: facing the slot it reads as walking in.

PALETTE (tools/palette_check against the stills as rendered, scratch script; not part of the self-test)
    b01, b12, b17, b23w pass every rule they have pixels for (stone G/R 0.94-0.99, robes hue 12-15, villager skin
    s 0.44-0.47, Steve's shirt hue 176-179, his trousers not clipped, plants 0.85 of the grass). b09 FAILS "stone not
    magenta" at G/R 0.90: the platform's stone lip in the low sun beside its gold halo, rgb(203, 183, 155): warm, B under
    G, not magenta (the rule tests G/R only: fixtures' notes; legday_set's dusk still has the same). b17's baby head
    was 59 % inside the safe area: the grow camera was re-aimed (20 mm, target z 10.75) and re-rendered.

NOT VERIFIED / LEFT TO THE DIRECTORS: no motion was rendered except b11's and b19's strips (the walks, the push, the
    climb, the bounce, the slide timing are towers' numbers); tools/palette_check was not run on these stills (towers'
    own golden stills pass it); nothing was rendered at final settings through render.py; the timing of every action
    against the words is the directors' (the stage functions use fixed offsets); Steve's and the villagers' looks are
    single choices made for the stills.
"""
import math
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from engine import sets, towers, village   # noqa: E402

# ------------------------------------------------------------------------------------------------------------------
# the sky the set was lit and scouted under (degrees counter-clockwise from east; see the docstring, THE SKY)
# ------------------------------------------------------------------------------------------------------------------
SKIES = {
    "gold": dict(preset="golden", az=62.0, el=27.0, bloom=1.0, grade="warm"),
}

FARM = "tower"                       # the iron farm's name (anchors 'tower_<short>', cutaways 'tower_pod_<wall>')
POD_LIGHTS = {"tower_pod": 1.0, "tower_cell": 1.0}      # the pod's lantern and the cell's wall torch (Stage.lights)

# ------------------------------------------------------------------------------------------------------------------
# the film's own places (registered as anchors 'tm_<name>' by the hook; 2D = on the ground there, 3D = exactly there)
# ------------------------------------------------------------------------------------------------------------------
L0 = towers.layout()                 # the tower's cells as numbers (the default at / floor: the film's)
X, Y, F = L0["X"], L0["Y"], L0["F"]  # (-23, 18, 10): the pod's south-west inside cell and its floor top

BABY_SQUARE = (6.38, 1.16)           # beats 1, 2, 4: towers' square_baby (the baby on the plaza path east of the well,
#                                      3.4 blocks in front of the plaza camera, facing north-north-east: its nose in
#                                      profile from behind); kept: with the camera panned for house_c's door it is in
#                                      the frame's lower middle (x 49 %) and Steve comes at the lens on its right
ANCHORS = {
    # ---- the square (beats 1-4)
    "baby_square": (BABY_SQUARE, 64.5),                     # facing north-north-east (its nose in profile from behind)
    "armorer_from": ((-5.8, 7.9), 160.0),                   # beat 1: the two adults who hurry into house_c
    "shepherd_from": ((-4.9, 8.8), 160.0),
    "house_c_door_target": ((-10.0, 6.5, 2.0), None),       # the door that shuts behind the second (house_c, east face)
    # ---- beats 23 / 24 from the window (b23w, b24w): the narrator and Mom side by side across the lens, 1.0 apart
    #      (folded arms are 1.0 wide), both facing the zombie's eyes; the librarian between and behind them, the
    #      cleric on towers' back_2
    "narrator_23": ((X + 2.45, Y + 1.7, float(F)), None),           # (-20.55, 19.7); they face the zombie's eyes
    "mom_23": ((X + 2.45, Y + 0.7, float(F)), None),
    "librarian_23": ((X + 1.2, Y + 0.75, float(F)), None),
    # ---- beat 22 from outside (b22o): the narrator 0.3 west of towers' watch_22, so that from the north-east the
    #      line to his face passes the back glass 0.6 west of the plug's column (from watch_22 the plug cut his face)
    "watch_22_out": ((X + 2.4, Y + 2.45, float(F)), None),
}
PATHS = {
    # beat 1: Steve across the plaza at the lens (towers' tower_steve_square, kept), passing the baby on its right
    "steve_square": [(-1.0, 7.3), (8.3, 0.7)],        # towers' tower_steve_square: at the lens on the frame's right
#                                                     (x 72-80 %), passing the baby 1.4 to its right, out of frame right
    # beat 2: Steve's legs between the lens and the baby (towers' tower_steve_past moved with the baby)
    "steve_past": [(4.5, 0.64), (6.55, 3.1)],        # towers' tower_steve_past
}
# beat 1: the armorer and the shepherd hurry from the plaza's north-west corner into house_c, whose door faces east
# (the last five nodes are the village's own square_to_house_c: the dirt path, the oak-stairs step at (-10, 6), the
# door cell (-11, 6), just inside)
HOUSE_C_IN = [(-7.5, 6.5, -0.0625), (-8.5, 6.5, -0.0625), (-9.0, 6.5, 0.0), (-10.0, 6.5, 1.0), (-10.5, 6.5, 1.0),
              (-11.9, 6.5, 1.0)]
DOOR_PATHS = {
    "flee_armorer": [(-5.8, 7.9), (-6.6, 6.9)],
    "flee_shepherd": [(-4.9, 8.8), (-6.2, 7.3)],
}
FLEE_DOOR = "house_c"


def _yaw_deg(compass_ccw_from_east):
    """Yaw of a character facing a direction given in degrees counter-clockwise from east (characters face -Y at
    yaw 0)."""
    a = math.radians(compass_ccw_from_east)
    return math.atan2(math.cos(a), -math.sin(a))


# ------------------------------------------------------------------------------------------------------------------
# A SUGGESTED CAMERA FOR EVERY BEAT: dict(pos, target, lens, fstop[, pos1, target1], what, sky, from_=towers camera or
# None). Filled from the renders (see the docstring, THE CAMERAS); every one is rendered by `$BPY -m
# films.twentyminutes_set bNN` to out/test/twentyminutes_set_<beat>_<what>.png (+ _zones.png).
# ------------------------------------------------------------------------------------------------------------------
TC = towers.cameras(L0)
POD_FRONT = (X + 2.5, Y - 0.5, F + 1.5)      # the middle of the pod's front glass (a hero point seen from the square)


def _tc(name, **over):
    c = {k: v for k, v in TC[name].items() if k != "beat"}
    c.update(over)
    c["from_"] = name
    return c


PLAZA = TC["square"]["pos"]
CAMERAS = {
    "b01": _tc("square", pos=(PLAZA[0], PLAZA[1], 0.75), target=(-21.85, 18.65, 1.0), what="afraid"),
    "b02": _tc("baby_face", what="imnot"),
    "b03": _tc("push_square", target1=(3.0, 6.0, 0.95), what="push", ease="linear"),
    "b04": _tc("square_start", pos=(PLAZA[0], PLAZA[1], 0.75), pos1=(PLAZA[0], PLAZA[1], 0.75),
               target1=(-21.85, 18.65, 1.0), what="tilt"),             # ends on b01's framing exactly
    "b04_long": _tc("square_long", what="hat"),
    "b05": _tc("foot", what="arms"),
    "b06": _tc("pan_bed", what="bed"),
    "b07": _tc("two_shot", what="reach"),
    "b08": _tc("cell_side", what="scared"),
    "b08w": dict(pos=(X + 4.95, Y + 2.15, F + 1.38), target=(X + 0.4, Y + 1.3, F + 1.3), lens=18.0, fstop=2.8,
                 what="window", from_=None),
    "b09": dict(pos=(X - 6.3, Y - 0.7, F + 0.35), target=(X - 1.3, Y + 2.55, F + 1.45), lens=16.0, fstop=4.0,
                what="golem", from_=None),
    "b10": dict(pos=(X - 6.3, Y - 0.7, F + 0.35), target=(X - 1.3, Y + 2.55, F + 1.45), lens=16.0, fstop=4.0,
                what="again", from_=None),
    "b11": _tc("slide", what="slide"),
    "b12": _tc("hopper_wide", target=(X - 5.6, Y + 6.0, 0.15), what="iron"),
    "b13": _tc("back", target=(X + 5.6, Y + 4.5, 3.0), lens=20.0, what="stairs"),
    "b14": _tc("top_step_side", what="gap"),
    "b15": _tc("gap", what="fit"),
    "b16": _tc("red_bed", what="mom"),
    "b17": _tc("grow", target=(X + 1.95, Y + 0.45, F + 0.75), lens=20.0, what="twenty"),
    "b18": _tc("bounce", what="bounce"),
    "b19": _tc("grow", target=(X + 1.95, Y + 0.45, F + 0.75), lens=20.0, what="ended"),
    "b20": _tc("gap_side", what="nofit"),
    "b21": _tc("high", target=(X + 2.5, Y + 2.2, F + 0.3), what="count"),
    "b22": _tc("back_glass", what="step"),
    "b22o": dict(pos=(X + 5.4, Y + 10.0, F + 0.3), target=(X + 3.29, Y + 5.47, F + 0.21), lens=35.0, fstop=2.8,
                 what="step_out", from_=None),
    "b23": _tc("cell_side", what="afraid"),
    "b23w": dict(pos=(X + 4.95, Y + 2.15, F + 1.38), target=(X + 0.4, Y + 0.95, F + 1.3), lens=18.0, fstop=2.8,
                 what="window", from_=None),
    "b24": _tc("cell_side", what="counts"),
    "b24w": dict(pos=(X + 4.95, Y + 2.15, F + 1.38), target=(X + 0.4, Y + 0.95, F + 1.3), lens=18.0, fstop=2.8,
                 what="window", from_=None),
    "b24p": dict(pos=(X - 6.3, Y - 0.7, F + 0.35), target=(X - 1.3, Y + 2.55, F + 1.45), lens=16.0, fstop=4.0,
                 what="platform", from_=None),
}
for _k, _c in CAMERAS.items():
    _c.setdefault("sky", "gold")
BEATS = ["b01", "b02", "b03", "b04", "b04_long", "b05", "b06", "b07", "b08", "b08w", "b09", "b10", "b11", "b12",
         "b13", "b14", "b15", "b16", "b17", "b18", "b19", "b20", "b21", "b22", "b22o", "b23", "b23w", "b24",
         "b24w", "b24p"]


# ------------------------------------------------------------------------------------------------------------------
# the hook
# ------------------------------------------------------------------------------------------------------------------
def twentyminutes_set(b):
    """THE HOOK PIECE of "Twenty Minutes": engine/towers.py's iron farm (the whole tower, defaults), the film's own
    anchors and paths (beat 1's flight into house_c, beat 2's moved baby spot) and the plants cleared off the ground
    lines of the film's low cameras. Call it inside village.build_village(scene, seed=1, edit=...). Returns the dict
    stored as Village.sets['twentyminutes'] (farm = towers' dict, cameras, anchors, paths)."""
    sets._new_name(b, "twentyminutes")
    farm = towers.iron_farm(b, name=FARM)
    for name, (p, deg) in ANCHORS.items():
        b.anchor("tm_" + name, p, None if deg is None else _yaw_deg(deg))
    for name, pts in PATHS.items():
        sets.ground_path(b, "tm_" + name, pts)
    for name, pts in DOOR_PATHS.items():
        b.path("tm_" + name, [(x, y, b.walk_z(x, y)) for x, y in pts] + list(HOUSE_C_IN))
    # no tuft between a low camera of this film and its subject (towers cleared its own cameras' lines)
    for k, c in CAMERAS.items():
        g = b.ground(c["pos"][0], c["pos"][1])
        if g is not None and c["pos"][2] < g + 4.5:
            for t in [c["target"]] + ([c["target1"]] if "target1" in c else []):
                if math.dist(c["pos"][:2], t[:2]) < 30.0:
                    sets.clear_view(b, c["pos"], t, 2.2)
    for name, pts in list(PATHS.items()) + list(DOOR_PATHS.items()):
        sets.clear_view(b, pts[0], pts[-1], 1.4)
    # the plaza lamp post at (-7, 9) (village LAMPS, a vanilla plains_lamp_1) stands exactly behind the baby's head in
    # the plaza framing of beats 1 and 4 (its torches stuck out of the head's top: a tangent both reviews of the plan
    # and the set's own b04 still found; no place of the baby or the lens clears it while the head stays above the
    # caption band): this film's village has no lamp there (its two torches and their light go with it)
    _take_out(b, LAMP_OUT)
    res = dict(farm=farm, cameras={k: dict(v) for k, v in CAMERAS.items()}, anchors=dict(ANCHORS),
               paths=dict({k: list(v) for k, v in PATHS.items()}, **{k: list(v) for k, v in DOOR_PATHS.items()}))
    b.v.sets["twentyminutes"] = res
    return res


LAMP_OUT = (-7, 9)                     # the plaza lamp post this film's village does not have (the hook takes it out)


def _take_out(b, column, height=6):
    """Remove everything standing on the ground in the 3 x 3 columns around `column` (a plains_lamp_1 is placed with
    its corner at (x - 1, y - 1)): blocks from the ground's top up `height` cells. The builder drops the lights of the
    torches that go (Village _after_edit)."""
    x0, y0 = column
    b.allow((x0 - 1, y0 - 1, x0 + 1, y0 + 1))
    gone = []
    for x in range(x0 - 1, x0 + 2):
        for y in range(y0 - 1, y0 + 2):
            g = b.ground(x + 0.5, y + 0.5)
            if g is None:
                continue
            for z in range(int(round(g)), int(round(g)) + height):
                if b.w.block_id(x, y, z) is not None:
                    gone.append((x, y, z, b.w.block_id(x, y, z)))
                    b.w.set(x, y, z, None)
    return gone


def build_set(scene):
    """The village of "Twenty Minutes": seed 1 with the iron farm built in. Returns the Village."""
    return village.build_village(scene, seed=1, edit=twentyminutes_set)


# the suggested camera of every beat first, then the alternatives that were rendered (see the docstring, STILLS)
BEAT_CAMERAS = {1: ["b01"], 2: ["b02"], 3: ["b03"], 4: ["b04", "b04_long"], 5: ["b05"], 6: ["b06"], 7: ["b07"],
                8: ["b08w", "b08"], 9: ["b09"], 10: ["b10"], 11: ["b11"], 12: ["b12"], 13: ["b13"], 14: ["b14"],
                15: ["b15"], 16: ["b16"], 17: ["b17"], 18: ["b18"], 19: ["b19"], 20: ["b20"], 21: ["b21"],
                22: ["b22o", "b22"], 23: ["b23w", "b23"], 24: ["b24p", "b24", "b24w"]}
# beats 8 / 23 / 24 are one camera position in the story ("This camera position returns for the last two lines"):
# b08w -> b23w -> b24w (held: the golem appears partly behind the narrator) cut on "counts" to b24p (the story's own
# fallback), or b08 -> b23 -> b24 (towers' cell_side: the golem between two heads, small; no zombie arm)


def data(v):
    """Everything a film's common module needs after build_set, as data:
      anchors   {name: ((x, y, z), yaw or None)}: towers' ('tower_<short>') and the film's ('tm_<name>')
      paths     {name: [(x, y, z), ...]}: towers' and the film's
      parts     make_parts(v) (the farm and its fixtures, house_c's door)
      cutaways  the pod's camera cutaways (Stage.see_through / remove): tower_pod_north / _east / _south / _west /
                _roof / _all
      lights    dict(pod=POD_LIGHTS): the groups for Stage.lights in every shot
      cameras   {beat number: [camera dict, ...]} in BEAT_CAMERAS order (each dict carries its key as 'key')
      skies     SKIES"""
    names = [k for k in v.anchors if k.startswith(FARM + "_") or k.startswith("tm_")]
    anchors = {k: (tuple(v.anchors[k]), v.yaws.get(k)) for k in sorted(names)}
    paths = {k: [tuple(p) for p in pts] for k, pts in v.paths.items() if k.startswith((FARM + "_", "tm_"))}
    cams = {b_: [dict(CAMERAS[k], key=k) for k in keys] for b_, keys in BEAT_CAMERAS.items()}
    cut = sorted(k for k in v.cutaways if k.startswith(FARM + "_pod_"))
    return dict(anchors=anchors, paths=paths, parts=make_parts(v), cutaways=cut, lights=dict(pod=dict(POD_LIGHTS)),
                cameras=cams, skies=dict(SKIES))


class Parts(dict):
    """The film's parts (a dict with attribute access): see make_parts()."""

    def __getattr__(self, k):
        try:
            return self[k]
        except KeyError:
            raise AttributeError(k)


def make_parts(v):
    """The parts that change on camera, after build_village (engine/towers.py Farm and its fixtures):
      farm        towers.Farm (calls: zombie_in_cell, golem_spawn / step / slide / death, deliver, strew,
                  break_top_step, climb, bounce, see_through; .A / .yaw / .cameras / .L)
      pod         fixtures GlassBox (cutaways tower_pod_north / _east / _south / _west / _roof / _all; .panes)
      bed2        fixtures Bed: the second red bed, foot (-20, 22), pillow (-20, 21); place_at(frame)
      hopper, chest   fixtures Hopper / Chest at the foot (-29, 23, 1) / (-29, 23, 0)
      water, lava     fixtures Fluids: the sheet on the platform, the glow strip in the slot (level / flicker)
      top_step    engine.breaking Breakable (-19, 24, 9): break_top_step / restore
      door        house_c's door (beat 1): v.door_open(FLEE_DOOR, f) / v.door_open(FLEE_DOOR, f, open=False)"""
    fm = towers.farm(v, FARM)
    return Parts(farm=fm, pod=fm.pod, bed2=fm.bed2, hopper=fm.hopper, chest=fm.chest, water=fm.water, lava=fm.lava,
                 top_step=fm.top_step, door=v.doors[FLEE_DOOR])


# ------------------------------------------------------------------------------------------------------------------
# scouting: ONE build per command with every beat staged in film order (the film's own state: the golem's spawns,
# the second bed, the broken step, the swap), each beat a shot of its own; the stills named are rendered from it
# ------------------------------------------------------------------------------------------------------------------
TEST_DIR = os.path.join(ROOT, "out", "test")
SECONDS = dict(b01=3.0, b02=2.0, b03=3.5, b04=3.0, b04_long=1.5, b05=2.5, b06=3.0, b07=2.0, b08=2.0, b08w=2.0,
               b09=2.5, b10=2.0, b11=4.0, b12=3.0, b13=2.5, b14=2.5, b15=2.5, b16=2.5, b17=2.5, b18=2.5, b19=3.0,
               b20=2.5, b21=4.0, b22=3.5, b22o=3.5, b23=2.5, b23w=2.5, b24=4.0, b24w=4.0, b24p=3.0)


class Scout:
    """One scene: the set, its parts, a Stage with SKIES (sky = the active one), a Film, every beat staged."""

    def __init__(self, sky="gold", res=(540, 960), samples=16, threads=2, beats=None):
        import bpy
        from engine import look, shots
        from films import lookdev as L
        self.bpy = bpy
        bpy.ops.wm.read_factory_settings(use_empty=True)
        self.scene = bpy.context.scene
        look.setup_render(self.scene, res=res, samples=samples, threads=threads)
        t = time.time()
        self.v = build_set(self.scene)
        self.P = make_parts(self.v)
        self.fm = self.P.farm
        self.A = self.fm.A
        self.film = shots.Film(self.scene, fps=24)
        self.st = L.Stage(self.scene, self.film, self.v, skies=SKIES, sky=sky)
        self.sky = sky
        self.shots, self.frames, self.heroes, self.memo = {}, {}, {}, {}
        # the second bed is in the shots that use it only (b21 places it on its frame)
        self.st.cast[self.P.bed2.name] = self.P.bed2
        for b_ in (beats or BEATS):
            s = self.st.shot(b_, SECONDS[b_], sky=CAMERAS[b_]["sky"])
            self.shots[b_] = s
            out = STAGES[b_](self, s)
            frames, heroes = out
            self.frames[b_] = frames if isinstance(frames, list) else [(frames, "")]
            self.heroes[b_] = heroes
        self.st.finish()
        print("[twentyminutes_set] built and staged %d beats in %.1f s" % (len(self.shots), time.time() - t),
              flush=True)

    # ---- the cast (one instance per name; each shot place()s whom it uses on its first frame)
    def actor(self, name, profession, child=False):
        return self.st.actor(name, profession, child=True) if child else self.st.actor(name, profession)

    def player(self, name="steve"):
        from engine import players
        p = self.st.cast.get(name)
        return p if p is not None else players.add_player(self.st, name, "steve")

    def zombie(self, f0, aggro=False, look=None):
        from engine import undead
        z = self.st.cast.get("zombie") or undead.add_zombie(self.st, "zombie")
        self.fm.zombie_in_cell(z, f0, aggro=aggro, look=look)
        return z

    def golem(self):
        from engine import mobs
        g = self.st.cast.get("golem")
        if g is None:
            g = self.st.cast["golem"] = mobs.make_iron_golem("golem")
        return g

    def put(self, c, f, anchor, yaw=None):
        """place() c on a towers anchor (short name) or a 'tm_' / village anchor, facing its yaw (or `yaw`)."""
        if anchor in self.A:
            p, y = self.A[anchor], self.fm.yaw.get(anchor)
        else:
            p, y = self.v.anchors[anchor], self.v.yaws.get(anchor)
        c.place(f, p, y if yaw is None else yaw)
        return p

    # ---- camera and light
    def cam(self, s, key, focus=None, moved=True, ease=None):
        c = CAMERAS[key]
        ease = ease or c.get("ease", "ease_out")
        s.lens(c["lens"], c.get("fstop", 4.0))
        if moved and ("target1" in c or "pos1" in c):
            s.move(c["pos"], c["target"], c.get("pos1", c["pos"]), c.get("target1", c["target"]), ease=ease)
        else:
            s.move(c["pos"], c["target"])
        s.focus(focus if focus is not None else c["target"])
        return c

    def lights(self, s, pod=True):
        self.st.lights(s, scale=1.0, groups=POD_LIGHTS if pod else None)

    # ---- rendering
    def render(self, frame, name, zones=True, res=None):
        """Render `frame` to out/test/<name>.png (+ _zones.png). Returns the path."""
        from PIL import Image
        from engine import post
        os.makedirs(TEST_DIR, exist_ok=True)
        path = os.path.join(TEST_DIR, name + ".png")
        r = self.scene.render
        full = (r.resolution_x, r.resolution_y)
        if res:
            r.resolution_x, r.resolution_y = res
        self.film.goto(frame)
        r.filepath = path[:-4] + "_part"
        r.use_file_extension = True
        t = time.time()
        self.bpy.ops.render.render(write_still=True)
        os.replace(path[:-4] + "_part.png", path)
        r.resolution_x, r.resolution_y = full
        if zones:
            with Image.open(path) as im:
                post.draw_zones(im.convert("RGB")).save(path[:-4] + "_zones.png")
        print("[twentyminutes_set] %s (frame %d, sky %s) %.1f s" % (path, frame, self.sky, time.time() - t),
              flush=True)
        return path


def _head(c, f):
    return tuple(c.eye_point(f))


def _stand(p, dz):
    return (p[0], p[1], p[2] + dz)


# ---- beats 1-4: the square ---------------------------------------------------------------------------------------
def stage_b01(sc, s):
    """Beat 1 "In this village, everyone is afraid of the player.": the plaza camera (towers 'square', panned 4
    degrees left so house_c's door is in the frame); the baby on tm_baby_square in profile from behind, its big head
    tilting up as he comes; Steve along tm_steve_square at the lens; the armorer and the shepherd run into house_c,
    whose door opens for the first and shuts behind the second."""
    f0, v = s.frame_start, sc.v
    baby = sc.actor("baby", "none", child=True)
    bp = sc.put(baby, f0, "tm_baby_square")
    by = v.yaws["tm_baby_square"]
    steve = sc.player()
    path = v.paths["tm_steve_square"]
    steve.place(f0, path[0], village.yaw_to(path[0], path[1]))
    steve.walk(f0, path)
    ahead = (bp[0] + 2.0 * math.sin(by), bp[1] - 2.0 * math.cos(by))
    baby.look_at(f0, (ahead[0], ahead[1], bp[2] + 1.2), ease=0)
    baby.look_at(f0 + 30, (ahead[0], ahead[1], bp[2] + 3.4), ease=24)
    arm, she = sc.actor("armorer", "armorer"), sc.actor("shepherd", "shepherd")
    ends = []
    for c, key, delay in ((arm, "tm_flee_armorer", 0), (she, "tm_flee_shepherd", 5)):
        pts = v.paths[key]
        c.place(f0, pts[0], village.yaw_to(pts[0], pts[1]))
        ends.append(c.walk(f0 + delay, pts, run=True))
    v.door_open(FLEE_DOOR, ends[0] - 12, open=True, frames=5)
    v.door_open(FLEE_DOOR, ends[1] + 1, open=False, frames=5)
    sc.memo["b01_door"] = (ends[0] - 12, ends[1] + 1)
    sc.st.use(s, baby, steve, arm, she)
    sc.st.hero(s, "baby", baby)
    sc.cam(s, "b01", focus=baby.head)
    sc.lights(s)
    f = f0 + 22
    return [(f, ""), (ends[1] + 4, "door")], {"baby": _head(baby, f), "steve": _head(steve, f), "pod": POD_FRONT,
                       "door": v.anchors["tm_house_c_door_target"], "armorer": _head(arm, f),
                       "shepherd": _head(she, f)}


def stage_b02(sc, s):
    """Beat 2 "I'm not.": tight on the baby's face (towers 'baby_face' moved with the baby); Steve's legs stride
    through the foreground along tm_steve_past; its head follows him."""
    f0, v = s.frame_start, sc.v
    baby = sc.actor("baby", "none", child=True)
    sc.put(baby, f0, "tm_baby_square")
    steve = sc.player()
    path = v.paths["tm_steve_past"]
    steve.place(f0, path[0], village.yaw_to(path[0], path[1]))
    steve.walk(f0 + 6, path)
    baby.look_at(f0, steve, ease=0)
    for f in range(f0 + 4, s.frame_end + 1, 4):
        baby.look_at(f, steve, ease=3)
    sc.st.use(s, baby, steve)
    sc.st.hero(s, "baby", baby)
    sc.cam(s, "b02", focus=baby.head)
    sc.lights(s)
    f = f0 + 14
    return [(f, "")], {"baby": _head(baby, f)}


def stage_b03(sc, s):
    """Beat 3 "He only takes grownups.": towers 'push_square' panning with them; Steve shoves Mom (farmer, straw
    hat) west along tower_push_square (towers.push 'tap'); her head turned to give hat brim and nose; the baby on
    push_baby runs three steps after them and stops 1.2 behind Steve."""
    from engine import towers as T
    f0, v = s.frame_start, sc.v
    steve, mom = sc.player(), sc.actor("mom", "farmer")
    # ONLY AS FAR AS THE SHOT LASTS: towers.push keys the whole route (0.9 blocks/s), and keys past the shot's end
    # override the next shot's place() (the full tower_push_square, 7 blocks / 7.6 s, put Mom back on the plaza
    # behind the baby in beat 4); 3.5 s of shoving is 3.0 blocks
    r0 = v.paths["%s_push_square" % FARM][0]
    route = [r0, (r0[0] - 0.85 * SECONDS["b03"], r0[1], r0[2])]
    T.push(steve, mom, f0 + 2, route)
    for f in range(f0 + 2, s.frame_end + 1, 12):
        p = mom.pos_at(f)
        mom.look_at(f, (p.x - 2.0, p.y + 2.2, p.z + 1.6), ease=4)
    baby = sc.actor("baby", "none", child=True)
    sc.put(baby, f0, "push_baby")
    fb = f0 + 24
    here, his = baby.pos_at(fb), steve.pos_at(fb + 10)
    baby.walk(fb, [tuple(here), (max(his.x + 1.2, here.x - 1.6), here.y, here.z)], run=True)
    baby.look_at(fb, mom, ease=4)
    sc.st.use(s, steve, mom, baby)
    sc.st.hero(s, "mom", mom)
    sc.cam(s, "b03", focus=mom.head)
    sc.lights(s)
    f = f0 + 40
    return [(f, "")], {"mom": _head(mom, f), "steve": _head(steve, f), "baby": _head(baby, f)}


def stage_b04(sc, s):
    """Beat 4 "My mom lives at the top of his glass tower now.": over the baby's shoulder the tilt from the well
    (towers 'square_start') up to the tower (b01's framing); the baby looks up at the pod; Mom at the front glass
    (mom_glass) on the zombie; the focus racks from the baby to the pod. (The cut inside the line: b04_long.)"""
    f0 = s.frame_start
    baby = sc.actor("baby", "none", child=True)
    sc.put(baby, f0, "tm_baby_square")
    baby.look_at(f0, sc.A["pod_target"], ease=0)
    mom = sc.actor("mom", "farmer")
    sc.put(mom, f0, "mom_glass")
    mom.look_at(f0, sc.fm.zombie_eye, ease=0)
    z = sc.zombie(f0, look=mom)
    sc.st.use(s, baby, mom, z)
    c = CAMERAS["b04"]
    s.lens(c["lens"], c["fstop"])
    s.move(c["pos"], c["target"], c["pos1"], c["target1"])
    s.focus(baby.head)
    s.focus(mom.head, at_s=2.0, rack_s=0.6)
    sc.st.hero(s, "baby", baby)
    sc.lights(s)
    return [(f0 + 3, "a"), (s.frame_end - 3, "b")], {"baby": _head(baby, s.frame_end - 3),
                                                     "pod": POD_FRONT, "mom": _head(mom, f0)}


def pod_panes(sc, cam_pos, points, n=3):
    """The pod's glass blocks on the lines from a camera outside to each point, up to `n` per line (the panes a
    camera at a grazing angle looks through before it reaches the point)."""
    out = []
    for p in points:
        for ob in sc.fm.panes_toward(cam_pos, tuple(p), n):
            if ob not in out:
                out.append(ob)
    return out


def stage_b04_long(sc, s):
    """Beat 4, the cut inside the line (the story's fallback for 'Mom at the top of the tower'): towers
    'square_long', 200 mm from the plaza: the straw hat in profile at the front glass; every pane between the lens
    and her head, face and shoulders hidden from the camera (the frames behind her stay: it reads as glass)."""
    from engine import fixtures
    f0 = s.frame_start
    mom = sc.actor("mom", "farmer")
    mp = sc.put(mom, f0, "mom_glass")
    mom.look_at(f0, sc.fm.zombie_eye, ease=0)
    z = sc.zombie(f0, look=mom)
    sc.st.use(s, mom, z)
    c = sc.cam(s, "b04_long", focus=mom.head)
    pts = [_stand(mp, dz) for dz in (1.0, 1.35, 1.62, 1.95, 2.1)]
    pts += [(mp[0] + dx, mp[1], mp[2] + 1.6) for dx in (-0.3, 0.3)]
    fixtures.see_through(sc.st, s, pod_panes(sc, c["pos"], pts, n=3))
    sc.st.hero(s, "mom", mom)
    sc.lights(s)
    f = f0 + 12
    return [(f, "")], {"mom": _head(mom, f)}


# ---- beat 5: the foot of the tower -------------------------------------------------------------------------------
def stage_b05(sc, s):
    """Beat 5 "I would wave, but our arms don't do that.": towers 'foot'; the baby on foot_front, head far up, one
    small hop in place (towers.hop) at +34; the folded arms in the middle of the frame."""
    from engine import towers as T
    f0 = s.frame_start
    baby = sc.actor("baby", "none", child=True)
    up = sc.put(baby, f0, "foot_front")
    baby.look_at(f0, (up[0] + 0.8, up[1] - 2.0, up[2] + 4.0), ease=0)
    T.hop(baby, f0 + 34, sc.A["foot_front"])
    sc.st.use(s, baby)
    sc.st.hero(s, "baby", baby)
    sc.cam(s, "b05", focus=baby.head)
    sc.lights(s)
    f = f0 + 28
    return [(f, "")], {"baby": _head(baby, f), "arms": _stand(up, 0.45)}


# ---- the pod -----------------------------------------------------------------------------------------------------
def stage_b06(sc, s):
    """Beat 6 "He gave her a bed, and a zombie in a box.": towers 'pan_bed' from the red bed's foot to the cell; Mom
    on bed_beside on the zombie; the focus racks from the bed to the zombie."""
    f0 = s.frame_start
    mom = sc.actor("mom", "farmer")
    sc.put(mom, f0, "bed_beside")
    mom.look_at(f0, sc.fm.zombie_eye, ease=0)
    z = sc.zombie(f0, look=mom)
    sc.st.use(s, mom, z)
    sc.cam(s, "b06", focus=sc.fm.beds["mom"]["pos"])
    s.focus(z.head, at_s=1.8, rack_s=0.8)
    sc.st.hero(s, "mom", mom)
    sc.lights(s)
    return [(f0 + 2, "a"), (s.frame_end - 2, "b")], {"mom": _head(mom, f0 + 30), "zombie": _head(z, s.frame_end),
                                                      "red bed": _stand(sc.fm.beds["mom"]["pos"], 0.0)}


def stage_b07(sc, s):
    """Beat 7 "The zombie can't reach her.": towers 'two_shot' from behind the back wall (tower_pod_north hidden
    from the camera): the arms out of the window (aggro), one empty block, Mom's face on 'mom'."""
    f0 = s.frame_start
    mom = sc.actor("mom", "farmer")
    sc.put(mom, f0, "mom")
    mom.look_at(f0, sc.fm.zombie_eye, ease=0)
    z = sc.zombie(f0, aggro=True, look=mom)
    sc.st.use(s, mom, z)
    sc.st.see_through(s, FARM + "_pod_north")
    sc.cam(s, "b07", focus=mom.head)
    sc.st.hero(s, "mom", mom)
    sc.lights(s)
    f = f0 + 12
    return [(f, "")], {"mom": _head(mom, f), "arms": (sc.fm.set["zombie"][0] - 0.55, sc.fm.set["zombie"][1], F + 1.4)}


def _backed(sc, s, who, seeds=None, panic=True):
    """Villagers on towers anchors, trembling (towers.panic) with their heads on the zombie."""
    from engine import towers as T
    f0 = s.frame_start
    cast = []
    for name, prof, spot in who:
        c = sc.actor(name, prof)
        sc.put(c, f0, spot)
        cast.append(c)
    for c in cast:
        if panic:
            T.panic(c, f0, s.frame_end, sc.fm.zombie_eye, seed=(seeds or {}).get(c.name, len(c.name) * 7 + 3))
        else:
            c.look_at(f0, sc.fm.zombie_eye, ease=0)
    return cast


THREE = (("cleric", "cleric", "back_1"), ("librarian", "librarian", "back_2"), ("mom", "farmer", "back_3"))


def stage_b08(sc, s, key="b08", aggro=True):
    """Beat 8 "It doesn't have to.": Mom, the cleric and the librarian backed against the far glass (back_3, back_1,
    back_2), trembling, heads on the zombie; the empty platform beyond the west glass."""
    f0 = s.frame_start
    cast = _backed(sc, s, THREE)
    z = sc.zombie(f0, aggro=aggro, look=cast[2])
    sc.st.use(s, z, *cast)
    sc.st.hero(s, "mom", cast[2])
    sc.cam(s, key, focus=cast[0].head)
    sc.lights(s)
    f = f0 + 30
    return [(f, "")], {"cleric": _head(cast[0], f), "librarian": _head(cast[1], f), "mom": _head(cast[2], f)}


def stage_b08w(sc, s):
    """Beat 8, the zombie's-eye alternative: the lens in the cell's window over the sill, between the zombie's
    outstretched arms (not raised: forward, swaying): an arm at the frame edge, the three faces toward the lens."""
    return stage_b08(sc, s, key="b08w", aggro=False)


def stage_b09(sc, s):
    """Beat 9 "When we get scared, an iron golem comes to save us.": a low wide lens over the slot's south end
    looking north-east: the golem appears on golem_spawn in front of the low sun (the gold sky behind its head),
    turns its head to the pod; the three small behind the glass on back_1..3."""
    f0 = s.frame_start
    g = sc.golem()
    sc.fm.golem_spawn(g, f0 + 6, yaw=0.0, look=sc.A["pod_target"], look_after=10, empty_from=s)
    cast = _backed(sc, s, THREE)
    sc.st.use(s, g, *cast)
    sc.st.hero(s, "golem", g)
    sc.cam(s, "b09", focus=g.head)
    sc.lights(s)
    f = f0 + 30
    return [(f, "")], {"golem": _head(g, f), "cleric": _head(cast[0], f), "librarian": _head(cast[1], f),
                       "mom": _head(cast[2], f)}


def stage_b10(sc, s):
    """Beat 10 "It comes every time.": the same framing, a jump cut: the platform empty, a new golem on the same
    block in the same pose, one heavy step toward the pod."""
    f0 = s.frame_start
    g = sc.golem()
    sc.fm.golem_spawn(g, f0 + 5, yaw=0.0, look=sc.A["pod_target"], look_after=4, empty_from=s)
    e = sc.fm.golem_step(g, f0 + 18)
    cast = _backed(sc, s, THREE)
    sc.st.use(s, g, *cast)
    sc.st.hero(s, "golem", g)
    sc.cam(s, "b10", focus=g.head)
    sc.lights(s)
    sc.memo["b10_step"] = e
    return [(f0 + 30, ""), (f0 + 4, "empty")], {"golem": _head(g, f0 + 30)}


def stage_b11(sc, s):
    """Beat 11 "The water pushes it into the lava.": towers 'slide' (from the slot's open south end at the
    platform's level): the golem slides west and drops into the slot; the puff and the glow's flicker."""
    f0 = s.frame_start
    g = sc.golem()
    sc.fm.golem_spawn(g, f0, yaw=math.radians(90.0), look=sc.A["pod_target"], look_after=0, empty_from=s)
    r = sc.fm.golem_slide(g, f0 + 6)
    d = sc.fm.golem_death(g, r, camera=s, until=s.frame_end + 1)
    sc.st.use(s, g)
    sc.st.hero(s, "golem", g)
    sc.cam(s, "b11", focus=sc.A["golem_spawn"])
    sc.lights(s, pod=False)
    sc.memo["b11"] = dict(r, death=d)
    edge, gone = r["edge"], r["gone"]
    return [(edge + 2, ""), (f0 + 2, "s1"), (edge - 6, "s2"), (gone - 3, "s3"), (gone + 5, "s4")], {
        "golem": _head(g, edge + 2), "slot": sc.A["slot_target"]}


def stage_b12(sc, s):
    """Beat 12 "He takes the iron and leaves the poppies.": towers 'hopper_wide': a stack of ingots and a poppy fall
    out of the chute onto the hopper and vanish; Steve on chest_steve with an ingot turns and walks out of frame;
    poppies spin on the grass; the baby among them."""
    from engine import mobs
    f0, st = s.frame_start, sc.st
    items = [mobs.make_dropped_item("iron_ingot", name="tm_iron", seed=1, count=3),
             mobs.make_dropped_item("poppy", name="tm_poppy", seed=2)]
    for it in items:
        st.cast[it.name] = it
    plans = sc.fm.deliver(items, f0 + 4, every=6, seed=2)
    lying = []
    for i in range(4):
        it = mobs.make_dropped_item("poppy", name="tm_lying_%d" % i, seed=10 + i)
        st.cast[it.name] = it
        lying.append(it)
    cam = CAMERAS["b12"]
    sc.fm.strew(lying, f0, s.frame_end + 1, seed=3, face=cam["pos"])
    steve = sc.player("steve_iron")
    steve.hold("iron_ingot")
    sc.put(steve, f0, "chest_steve")
    p = steve.pos_at(f0)
    steve.walk(f0 + 30, [tuple(p), (p.x + 3.0, p.y + 2.0, p.z)])
    baby = sc.actor("baby", "none", child=True)
    sc.put(baby, f0, "poppies")
    baby.look_at(f0, steve, ease=0)
    st.use(s, steve, baby, *(items + lying))
    st.hero(s, "baby", baby)
    sc.cam(s, "b12", focus=baby.head)
    sc.lights(s)
    f = min(int(round(plans[0]["landed"])) + 1, s.frame_end) if plans[0].get("landed") else f0 + 16
    return [(f, "")], {"baby": _head(baby, f), "steve": _head(steve, f), "hopper": sc.A["hopper_target"]}


def stage_b13(sc, s):
    """Beat 13 "He never took down his dirt staircase.": towers 'back' (locked tall): the dirt zigzag, the stray
    dirt; the baby tiny at the foot looks up, then hops up the first two steps (fm.climb)."""
    f0 = s.frame_start
    baby = sc.actor("baby", "none", child=True)
    sc.put(baby, f0, "stairs_foot")
    baby.look_at(f0, sc.A["stairs_target"], ease=0)
    e = sc.fm.climb(baby, f0 + 12, 0, 1)
    sc.st.use(s, baby)
    sc.st.hero(s, "baby", baby)
    sc.cam(s, "b13", focus=baby.head)
    sc.lights(s)
    sc.memo["b13_climb"] = e
    return [(f0 + 6, ""), (min(e + 2, s.frame_end), "up")], {"baby": _head(baby, f0 + 6),
                                                             "pod": (X + 2.5, Y + 5.0, F + 1.5)}


def stage_b14(sc, s):
    """Beat 14 "At the top there's a gap, one block high.": towers 'top_step_side': the baby on the ninth step hops
    up the last one onto top_step_baby beside the opening, its head just under the plug; Mom on 'mom' through the
    glass (the pane in front of her hidden)."""
    from engine import towers as T
    f0 = s.frame_start
    baby = sc.actor("baby", "none", child=True)
    baby.place(f0, sc.fm.set["stairs"][8], sc.fm.yaw["top_step"])
    e = T.hop(baby, f0 + 8, sc.A["top_step_baby"])
    baby.turn(e + 2, sc.fm.yaw["top_step_baby"], ease=6)
    mom = sc.actor("mom", "farmer")
    sc.put(mom, f0, "mom")
    mom.look_at(f0, sc.fm.zombie_eye, ease=0)
    z = sc.zombie(f0, look=mom)
    sc.st.use(s, baby, mom, z)
    c = sc.cam(s, "b14", focus=baby.head)
    sc.fm.see_through(sc.st, s, c, points=[mom])
    sc.st.hero(s, "baby", baby)
    sc.lights(s)
    f = f0 + 36
    return [(f, "")], {"baby": _head(baby, f), "gap": sc.A["gap_target"], "mom": _head(mom, f)}


def stage_b15(sc, s):
    """Beat 15 "Grownups don't fit, but I do.": towers 'gap' (inside at floor level, the gap in the middle): the
    cleric walks into the plug and stops on gap_side, half a block west of the opening; the baby runs in from the
    top step under the plug, past his robe."""
    f0 = s.frame_start
    cl = sc.actor("cleric", "cleric")
    gs = sc.A["gap_side"]
    start = (gs[0], gs[1] - 1.7, gs[2])
    cl.place(f0, start, sc.fm.yaw["gap_side"] + math.pi)
    cl.walk(f0 + 2, [start, gs])
    baby = sc.actor("baby", "none", child=True)
    ts = sc.A["top_step"]
    baby.place(f0, (ts[0], ts[1] + 0.4, ts[2]), math.pi)
    e = baby.walk(f0 + 16, [(ts[0], ts[1] + 0.4, ts[2]), sc.A["gap_in"], sc.A["bed_side"]], run=True)
    sc.st.use(s, cl, baby)
    sc.st.hero(s, "baby", baby)
    sc.cam(s, "b15", focus=sc.A["gap_target"])
    sc.lights(s)
    # the frame the baby is in the gap (its feet at y 23.0 .. 24.0)
    fg = f0 + 16
    while fg < e and baby.pos_at(fg).y > 23.4:
        fg += 1
    return [(fg, "")], {"baby": _head(baby, fg), "cleric": _head(cl, fg), "gap": sc.A["gap_target"]}


def stage_b16(sc, s):
    """Beat 16 "Mom never looks at me, only at the zombie.": towers 'red_bed' from outside the west glass (the panes
    on the lines hidden): Mom on bed_side on the zombie; the baby pressed against her on the lens side, its body
    turned to the lens, looking up at her."""
    f0 = s.frame_start
    mom = sc.actor("mom", "farmer")
    sc.put(mom, f0, "bed_side")
    mom.look_at(f0, sc.fm.zombie_eye, ease=0)
    z = sc.zombie(f0, aggro=True, look=mom)
    baby = sc.actor("baby", "none", child=True)
    bs = sc.A["bed_side"]
    bp = (bs[0] - 0.62, bs[1] - 0.05, bs[2])
    cam = CAMERAS["b16"]
    baby.place(f0, bp, village.yaw_to(bp, (0.5 * cam["pos"][0] + 0.5 * bs[0], 0.5 * cam["pos"][1] + 0.5 * bs[1])))
    baby.look_at(f0, mom, ease=0)
    sc.st.use(s, mom, baby, z)
    c = sc.cam(s, "b16", focus=baby.head)
    sc.fm.see_through(sc.st, s, c, points=[mom, baby])
    sc.st.hero(s, "baby", baby)
    sc.lights(s)
    f = f0 + 20
    return [(f, "")], {"baby": _head(baby, f), "mom": _head(mom, f), "zombie": _head(z, f)}


def _grow_cast(sc, s):
    f0 = s.frame_start
    mom = sc.actor("mom", "farmer")
    sc.put(mom, f0, "mom_glass")
    mom.look_at(f0, sc.fm.zombie_eye, ease=0)
    z = sc.zombie(f0, look=mom)
    return mom, z


def stage_b17(sc, s):
    """Beat 17 "Childhood here lasts twenty minutes.": towers 'grow', locked: Mom in profile at the front glass on
    the zombie, the baby 0.9 west of her along the glass (its head level with her folded arms), the village far
    below through the front glass."""
    f0 = s.frame_start
    mom, z = _grow_cast(sc, s)
    baby = sc.actor("baby", "none", child=True)
    sc.put(baby, f0, "baby_glass")
    baby.look_at(f0, sc.fm.zombie_eye, ease=0)
    sc.st.use(s, mom, baby, z)
    sc.st.hero(s, "mom", mom)
    sc.st.hero(s, "baby", baby)
    sc.cam(s, "b17", focus=mom.head)
    sc.lights(s)
    f = f0 + 24
    return [(f, "")], {"mom": _head(mom, f), "baby": _head(baby, f)}


def stage_b18(sc, s):
    """Beat 18 "I spent mine with her.": towers 'bounce': the baby bounces twice on Mom's red bed (fm.bounce: the
    glass roof stops each jump), its face cheated to the lens; Mom on bed_side on the zombie."""
    f0 = s.frame_start
    baby = sc.actor("baby", "none", child=True)
    cam = CAMERAS["b18"]
    bp, mp = sc.fm.beds["mom"]["pos"], sc.A["bed_side"]
    toward = (0.65 * cam["pos"][0] + 0.35 * mp[0], 0.65 * cam["pos"][1] + 0.35 * mp[1])
    e = sc.fm.bounce(baby, f0 + 2, "mom", jumps=2, yaw=village.yaw_to(bp, toward))
    mom = sc.actor("mom", "farmer")
    sc.put(mom, f0, "bed_side")
    mom.look_at(f0, sc.fm.zombie_eye, ease=0)
    z = sc.zombie(f0, look=mom)
    sc.st.use(s, baby, mom, z)
    sc.st.hero(s, "baby", baby)
    sc.cam(s, "b18", focus=baby.head)
    sc.lights(s)
    sc.memo["b18_bounce"] = (f0 + 2, e)
    f = f0 + 8
    return [(f, "")], {"baby": _head(baby, f), "mom": _head(mom, f)}


def stage_b19(sc, s):
    """Beat 19 "I was still inside when it ended.": the locked 'grow' framing again: the baby at Mom's folded arms
    snaps in ONE frame to the grown narrator (unemployed: the plain brown robe), same spot, same facing, head level
    with hers (towers.grow_up); Mom does not turn."""
    from engine import towers as T
    f0 = s.frame_start
    mom, z = _grow_cast(sc, s)
    baby = sc.actor("baby", "none", child=True)
    sc.put(baby, f0, "baby_glass")
    baby.look_at(f0, sc.fm.zombie_eye, ease=0)
    adult = sc.actor("narrator", "none")
    f = f0 + 30
    T.grow_up(baby, adult, f, look=sc.fm.zombie_eye)
    sc.st.use(s, mom, baby, adult, z)
    sc.st.hero(s, "mom", mom)
    sc.st.hero(s, "narrator", adult)
    sc.cam(s, "b19", focus=mom.head)
    sc.lights(s)
    sc.memo["b19_swap"] = f
    return [(f + 6, ""), (f - 1, "s1"), (f, "s2")], {"mom": _head(mom, f + 6), "narrator": _head(adult, f + 6)}


def stage_b20(sc, s):
    """Beat 20 "Now I don't fit.": towers 'gap_side' from outside the east glass (the panes on the lines hidden):
    the narrator walks into the plug, stops on gap_adult, his head tilts down to the gap (gap_down)."""
    f0 = s.frame_start
    nar = sc.actor("narrator", "none")
    ga = sc.A["gap_adult"]
    nar.place(f0, (ga[0], ga[1] - 1.6, ga[2]), sc.fm.yaw["gap_adult"])
    e = nar.walk(f0 + 4, [(ga[0], ga[1] - 1.6, ga[2]), ga])
    nar.look_at(e + 4, sc.A["gap_down"], ease=8)
    sc.st.use(s, nar)
    c = sc.cam(s, "b20", focus=nar.head)
    gt = sc.A["gap_target"]
    sc.fm.see_through(sc.st, s, c, points=[(ga[0], ga[1], ga[2] + 1.6), (ga[0], ga[1], ga[2] + 0.6), gt,
                                           (gt[0], gt[1] - 0.4, gt[2]), (gt[0], gt[1], gt[2] + 1.0)])
    sc.st.hero(s, "narrator", nar)
    sc.lights(s)
    f = f0 + 40
    return [(f, "")], {"narrator": _head(nar, f), "gap": gt}


ROW = (("librarian", "librarian"), ("cleric", "cleric"), ("narrator", "none"), ("mom", "farmer"))


def stage_b21(sc, s):
    """Beat 21 "He counted us twice, then brought one more bed.": towers 'high' over Steve's shoulder (the roof hidden
    from the camera): librarian, cleric, the narrator, Mom on row_1..4; the librarian and the cleric look away, Mom
    on the zombie, the narrator up at him; he looks along the row and back, sneaks, swings: the second red bed is
    there (fm.bed2.place_at)."""
    f0 = s.frame_start
    steve = sc.player()
    sc.put(steve, f0, "top_step")
    cast = []
    for i, (n, prof) in enumerate(ROW):
        c = sc.actor(n, prof)
        sc.put(c, f0, "row_%d" % (i + 1))
        cast.append(c)
    for c in cast[:2]:
        p = c.pos_at(f0)
        c.look_at(f0, (p.x - 3.0, p.y - 1.0, F + 1.6), ease=0)
    cast[2].look_at(f0, steve, ease=0)
    cast[3].look_at(f0, sc.fm.zombie_eye, ease=0)
    steve.watch(f0, f0 + 40, cast[0])
    steve.watch(f0 + 41, f0 + 60, cast[3])
    steve.sneak(f0 + 64)
    steve.attack(f0 + 68)
    sc.P.bed2.place_at(f0 + 70)
    sc.st.use(s, steve, sc.P.bed2, *cast)
    sc.st.see_through(s, FARM + "_pod_roof")
    sc.cam(s, "b21", focus=cast[2].head)
    for c in cast:
        sc.st.hero(s, c.name, c)
    sc.lights(s)
    f = f0 + 76
    out = {c.name: _head(c, f) for c in cast}
    out["bed2"] = sc.P.bed2.pos
    return [(f, ""), (f0 + 66, "before")], out


def _watch22(sc, s, key, spot="watch_22"):
    from engine import towers as T
    f0 = s.frame_start
    sc.P.top_step.restore(f0)
    nar = sc.actor("narrator", "none")
    sc.put(nar, f0, spot) if spot in sc.A else nar.place(f0, sc.v.anchors[spot],
                                                          village.yaw_to(sc.v.anchors[spot], sc.A["one_down"]))
    steve = sc.player()
    sc.put(steve, f0, "one_down")
    steve.look_at(f0, sc.P.top_step.center, ease=0)
    od = sc.A["one_down"]
    nar.look_at(f0, (od[0], od[1], F + 1.62), ease=0)       # eyes level
    m = sc.fm.break_top_step(steve, f0 + 6, camera=s, until=s.frame_end + 1)
    st_ = sc.fm.set["stairs"]
    T.walk_down(steve, m["frame"] + 8, [st_[7], st_[6], st_[5]])
    sc.st.use(s, nar, steve, sc.P.bed2)
    return nar, steve, m


def stage_b22(sc, s):
    """Beat 22 "I'm still not afraid of the player.": towers 'back_glass' (inside, the south-east corner): the
    narrator on watch_22 at the left edge (lost profile), still, eyes level; through the back glass Steve one step
    down breaks the top step by hand and walks down out of sight."""
    nar, steve, m = _watch22(sc, s, "b22")
    sc.cam(s, "b22", focus=steve.head)
    sc.st.hero(s, "narrator", nar)
    sc.lights(s)
    f = s.frame_start + 14
    return [(f, "")], {"narrator": _head(nar, f), "steve": _head(steve, f), "top step": sc.P.top_step.center}


def stage_b22o(sc, s):
    """Beat 22, the reverse from outside (the story's 'three-quarter face' cannot share a frame with Steve from
    inside): north-east of the stairs, Steve big on one_down breaking the top step, the narrator's face behind the
    back glass, watching, eyes level (the panes between the lens and his face hidden)."""
    nar, steve, m = _watch22(sc, s, "b22o", spot="tm_watch_22_out")
    c = sc.cam(s, "b22o", focus=nar.head)
    from engine import fixtures
    e = nar.eye_point(s.frame_start)
    pts = [(e[0] + dx, e[1], e[2] + dz) for dx in (-0.3, 0.0, 0.3) for dz in (-0.45, -0.2, 0.0, 0.25)]
    fixtures.see_through(sc.st, s, pod_panes(sc, c["pos"], pts, n=2))    # every pane in front of his face (a pane
    #                                                                        frame crossed his brows with one hidden)
    sc.st.hero(s, "narrator", nar)
    sc.st.hero(s, "steve", steve)
    sc.lights(s)
    f = s.frame_start + 14
    return [(f, "")], {"narrator": _head(nar, f), "steve": _head(steve, f), "top step": sc.P.top_step.center}


FOUR = (("cleric", "cleric", "back_1"), ("librarian", "librarian", "back_2"), ("mom", "farmer", "mom"),
        ("narrator", "none", "mom_glass"))


def stage_b23(sc, s, key="b23"):
    """Beat 23 "I'm afraid of the zombie.": cleric back_1, librarian back_2, Mom on 'mom', the narrator on
    mom_glass; the narrator's tremble matched frame for frame to Mom's (towers.panic, the same seed); zombie aggro;
    the two red beds."""
    f0 = s.frame_start
    cast = _backed(sc, s, FOUR, seeds={"mom": 7, "narrator": 7})
    z = sc.zombie(f0, aggro=(key != "b23w"), look=cast[2])
    sc.st.use(s, z, sc.P.bed2, *cast)
    sc.st.hero(s, "narrator", cast[3])
    sc.cam(s, key, focus=cast[3].head)
    sc.lights(s)
    f = f0 + 20
    return [(f, "")], {"narrator": _head(cast[3], f), "mom": _head(cast[2], f), "cleric": _head(cast[0], f),
                       "librarian": _head(cast[1], f)}


def _four_window(sc, s):
    """The four of beats 23 / 24 seen from the window camera, trembling (Mom's and the narrator's alike)."""
    from engine import towers as T
    f0 = s.frame_start
    cast = []
    for name, prof, spot in (("cleric", "cleric", "back_2"), ("librarian", "librarian", "tm_librarian_23"),
                             ("mom", "farmer", "tm_mom_23"), ("narrator", "none", "tm_narrator_23")):
        c = sc.actor(name, prof)
        p = sc.v.anchors[spot] if spot.startswith("tm_") else sc.A[spot]
        c.place(f0, p, village.yaw_to(p, sc.fm.zombie_eye))
        cast.append(c)
    for c in cast:
        T.panic(c, f0, s.frame_end, sc.fm.zombie_eye, seed=7 if c.name in ("mom", "narrator") else len(c.name))
    z = sc.zombie(f0, aggro=False, look=cast[2])
    return cast, z


def stage_b23w(sc, s):
    """Beat 23 from beside the window (b08w's camera position): the zombie's arm a dark green blur at the left edge;
    the narrator (tm_narrator_23) and Mom (tm_mom_23) side by side in front, 1.0 apart, trembling alike (the same
    panic seed), both staring at the zombie's eyes (just over the lens); the librarian (tm_librarian_23) between
    and behind them, the cleric on back_2."""
    f0 = s.frame_start
    cast, z = _four_window(sc, s)
    sc.st.use(s, z, sc.P.bed2, *cast)
    sc.st.hero(s, "narrator", cast[3])
    sc.st.hero(s, "mom", cast[2])
    sc.cam(s, "b23w", focus=cast[3].head)
    sc.lights(s)
    f = f0 + 20
    return [(f, "")], {"narrator": _head(cast[3], f), "mom": _head(cast[2], f), "cleric": _head(cast[0], f),
                       "librarian": _head(cast[1], f)}


def stage_b24(sc, s):
    """Beat 24 "Apparently that counts.": b23's shot held: behind the four, through the glass, a golem appears on
    golem_24, turns its head to the pod, steps, begins to slide; the focus racks to it."""
    f0 = s.frame_start
    cast = _backed(sc, s, FOUR, seeds={"mom": 7, "narrator": 7})
    z = sc.zombie(f0, aggro=True, look=cast[2])
    g = sc.golem()
    fs = f0 + 18
    sc.fm.golem_spawn(g, fs, pos=sc.A["golem_24"], yaw=math.radians(60.0), look=sc.A["pod_target"], look_after=6,
                      empty_from=s)
    e = sc.fm.golem_step(g, fs + 26)
    sc.fm.golem_slide(g, e + 4)
    sc.st.use(s, z, g, sc.P.bed2, *cast)
    sc.st.hero(s, "narrator", cast[3])
    sc.st.hero(s, "golem", g)
    sc.cam(s, "b24", focus=cast[2].head)
    s.focus(g.head, at_s=(fs + 30 - f0) / 24.0, rack_s=0.6)
    sc.lights(s)
    f = fs + 40
    return [(f, ""), (fs - 1, "before")], {"golem": _head(g, f), "narrator": _head(cast[3], f),
                                            "mom": _head(cast[2], f)}


def stage_b24w(sc, s):
    """Beat 24 as b23w's shot held: behind the four, through the west glass, the golem appears on golem_spawn in the
    gap between the narrator and the cleric, turns its head to the pod, steps, begins to slide; the focus racks to
    it."""
    f0 = s.frame_start
    cast, z = _four_window(sc, s)
    g = sc.golem()
    fs = f0 + 18
    sc.fm.golem_spawn(g, fs, yaw=math.radians(90.0), look=sc.A["pod_target"], look_after=6, empty_from=s)
    e = sc.fm.golem_step(g, fs + 26)
    sc.fm.golem_slide(g, e + 4)
    sc.st.use(s, z, g, sc.P.bed2, *cast)
    sc.st.hero(s, "narrator", cast[3])
    sc.st.hero(s, "golem", g)
    sc.cam(s, "b24w", focus=cast[3].head)
    s.focus(g.head, at_s=(fs + 30 - f0) / 24.0, rack_s=0.6)
    sc.lights(s)
    f = fs + 40
    return [(f, ""), (fs - 1, "before")], {"golem": _head(g, f), "narrator": _head(cast[3], f),
                                            "mom": _head(cast[2], f)}


def stage_b24p(sc, s):
    """Beat 24, the story's own fallback ('cut on that word to the low-angle platform framing of line 9 with the
    grown narrator now among the shapes behind the glass'): b09's camera; the golem appears on golem_spawn in front
    of the sun, turns its head to the pod, steps; the four behind the glass (back_1, back_2, mom, mom_glass)."""
    f0 = s.frame_start
    g = sc.golem()
    sc.fm.golem_spawn(g, f0 + 6, yaw=0.0, look=sc.A["pod_target"], look_after=10, empty_from=s)
    sc.fm.golem_step(g, f0 + 30)
    cast = _backed(sc, s, (("cleric", "cleric", "mom"), ("librarian", "librarian", "bed_side"),
                           ("mom", "farmer", "back_1"), ("narrator", "none", "back_2")), seeds={"mom": 7, "narrator": 7})
    z = sc.zombie(f0, aggro=True, look=cast[2])
    sc.st.use(s, g, z, sc.P.bed2, *cast)
    sc.st.hero(s, "golem", g)
    sc.cam(s, "b24p", focus=g.head)
    sc.lights(s)
    f = f0 + 26
    return [(f, "")], {"golem": _head(g, f), "narrator": _head(cast[3], f), "mom": _head(cast[2], f),
                       "cleric": _head(cast[0], f), "librarian": _head(cast[1], f)}


STAGES = {b_: globals()["stage_" + b_] for b_ in BEATS}


# ------------------------------------------------------------------------------------------------------------------
# measuring: where a point lands in the frame, what blocks the line to it
# ------------------------------------------------------------------------------------------------------------------
THIN = ("_fence", "_fence_gate", "lantern", "torch", "_bed", "_pane", "_door", "_wall", "_slab", "_stairs")


def ray_block(world, a, b, step=0.04, glass=False):
    """The first block on the segment a -> b (cells of both ends excluded): (cell, block id), or None. Thin blocks
    (fences, lanterns, torches, beds, panes, doors, slabs, stairs) are skipped, and glass unless glass=True."""
    ax, ay, az = a
    bx, by, bz = b
    n = max(2, int(math.dist(a, b) / step))
    end = tuple(int(math.floor(c)) for c in b)
    start = tuple(int(math.floor(c)) for c in a)
    for i in range(1, n):
        t = i / float(n)
        c = (int(math.floor(ax + (bx - ax) * t)), int(math.floor(ay + (by - ay) * t)),
             int(math.floor(az + (bz - az) * t)))
        if c in (start, end):
            continue
        bid = world.block_id(*c)
        if bid is None or not world.is_solid(*c):
            continue
        if bid == "glass" and not glass:
            continue
        if bid.endswith(THIN):
            continue
        return c, bid
    return None


def project(scene, cam, point):
    """(x %, y % from the top) of a world point in the camera's frame, and whether it is in front of the lens."""
    from bpy_extras.object_utils import world_to_camera_view
    from mathutils import Vector
    co = world_to_camera_view(scene, cam, Vector(point))
    return 100.0 * co.x, 100.0 * (1.0 - co.y), co.z > 0.0


def where(sc, beat, frame):
    """Print where each hero point of `beat` lands in its camera's frame on `frame` and what blocks it."""
    sc.film.goto(frame)
    cam = sc.scene.camera
    cp = tuple(cam.matrix_world.translation)
    cell = tuple(int(math.floor(c)) for c in cp)
    if sc.v.world.is_solid(*cell):
        print("[twentyminutes_set]   !!! the camera of %s is inside %s at %s" % (beat, sc.v.world.block_id(*cell),
                                                                              cell))
    for label, p in sc.heroes[beat].items():
        p = tuple(p)
        x, y, front = project(sc.scene, cam, p)
        flag = "" if (8 <= x <= 82 and 14 <= y <= 60 and front) else "   (outside the safe area)"
        hit = ray_block(sc.v.world, cp, p)
        if hit:
            flag += "   (hidden by %s at %s)" % (hit[1], hit[0])
        else:
            gl = ray_block(sc.v.world, cp, p, glass=True)
            if gl:
                flag += "   (through glass at %s)" % (gl[0],)
        print("[twentyminutes_set]   %-12s x %5.1f %%  y %5.1f %%%s" % (label, x, y, flag), flush=True)


def stills(names, res=(540, 960), samples=16, dry=False, palette=False, strip_res=(270, 480)):
    """Build once, stage every beat, render the named stills: 'b09' renders every frame b09 asks for (its tagged
    extra frames too); 'b09:' only its main frame. Strips (b11's s1..s4) are rendered at strip_res side by side."""
    from PIL import Image, ImageDraw
    sc = Scout(res=res, samples=samples)
    paths = []
    for name in names:
        beat, _, only = name.partition(":")
        spec = CAMERAS[beat]
        base = "twentyminutes_set_%s_%s" % (beat, spec["what"])
        frames = sc.frames[beat]
        is_strip = lambda t: t.startswith("s") and t[1:].isdigit()
        if ":" in name:                       # 'b04:' the main frame, 'b04:b' the frame tagged b, 'b11:strip'
            frames = frames[:1] if only == "" else [(f, t) for f, t in frames if t == only or
                                                    (only == "strip" and is_strip(t))]
        strip = [(f, t) for f, t in frames if is_strip(t)]
        single = [(f, t) for f, t in frames if (f, t) not in strip]
        for f, tag in single:
            print("[twentyminutes_set] %s%s frame %d (shot %d-%d):" % (beat, (" " + tag) if tag else "", f,
                                                                     sc.shots[beat].frame_start,
                                                                     sc.shots[beat].frame_end), flush=True)
            where(sc, beat, f)
            if dry:
                continue
            path = sc.render(f, base + ("_" + tag if tag else ""))
            paths.append(path)
            if palette and not tag:
                from tools import palette_check
                sc.film.goto(f)
                heroes = [ob for _l, obs in sc.st.heroes.get(beat, []) for ob in obs]
                rep = palette_check.evaluate(palette_check.probe(sc.scene), path, heroes=heroes)
                palette_check.print_report("%s@%d" % (beat, f), rep)
        if strip and not dry:
            tiles = []
            for f, tag in strip:
                p = sc.render(f, base + "_tmp_%s" % tag, zones=False, res=strip_res)
                with Image.open(p) as im:
                    tiles.append((f, im.convert("RGB")))
                os.remove(p)
            W, H = strip_res
            sheet = Image.new("RGB", (W * len(tiles), H + 22), (20, 20, 20))
            d = ImageDraw.Draw(sheet)
            for i, (f, im) in enumerate(tiles):
                sheet.paste(im, (i * W, 22))
                d.text((i * W + 6, 5), "frame %d" % f, fill=(255, 255, 255))
            path = os.path.join(TEST_DIR, base + "_strip.png")
            sheet.save(path)
            paths.append(path)
            print("[twentyminutes_set] strip %s" % path, flush=True)
    return paths


# ------------------------------------------------------------------------------------------------------------------
# the self-test: $BPY -m films.twentyminutes_set
# ------------------------------------------------------------------------------------------------------------------
BABY_SPOTS = ("tm_baby_square", "push_baby", "foot_front", "baby_glass", "gap_in", "top_step_baby", "stairs_foot",
              "poppies")
GOLEM_SPOTS = ("golem_spawn", "golem_24")


def _solid_at(w, x, y, z):
    """Is the point (x, y, z) inside a solid block (bottom slabs and stairs: their lower half only)?"""
    c = (int(math.floor(x)), int(math.floor(y)), int(math.floor(z)))
    if not w.is_solid(*c):
        return False
    bid, props = w.get(*c)
    if bid.endswith("_slab") and (props or {}).get("type", "bottom") == "bottom":
        return z - c[2] < 0.5 - 1e-6
    if bid.endswith("_stairs") and z - c[2] >= 0.5:
        return False
    return True


def part_cells(fm):
    """{cell: what}: cells a moving or appearing part fills at some time (no camera may sit there)."""
    L = fm.L
    out = {tuple(L["bed2"]): "second bed (foot)", (L["bed2"][0], L["bed2"][1] - 1, L["F"]): "second bed (pillow)",
           tuple(L["top_step"]): "top step", tuple(L["cell"]): "zombie", (L["cell"][0], L["cell"][1], L["F"] + 1):
           "zombie (head)"}
    for k in GOLEM_SPOTS:
        p = fm.A[k]
        for dz in (0, 1, 2):
            out[(int(math.floor(p[0])), int(math.floor(p[1])), int(p[2]) + dz)] = "golem (%s)" % k
    return out


def check(verbose=True):
    """Build the set and stage every beat (no render): the hook's own checks (Village.validate, edit problems),
    every anchor the beats stand on (solid under the feet, the body free for its height: adult 1.95, baby 0.975,
    golem 2.7), every camera (pos and pos1 outside every block and every part's cell), and every beat's heroes
    (inside the Reels safe area of its camera on its frame, not hidden by an opaque block). Returns the failures;
    the known limits (see the docstring) are printed as notes, not failures."""
    bad, notes = [], []
    t = time.time()
    sc = Scout(res=(270, 480), samples=1)
    v, fm, w = sc.v, sc.fm, sc.v.world
    say = print if verbose else (lambda *a: None)
    say("[twentyminutes_set] built and staged in %.1f s: %d faces" % (time.time() - t, v.face_count))
    for p in v.edit_problems:
        bad.append("hook: %s" % (p,))
    for p in v.validate():
        bad.append("village: " + p)
    # anchors: towers' standing spots and the film's own
    names = [k for k in fm.A if not k.endswith("_target") and k not in ("zombie", "gap_down", "pod_target")]
    names = ["tower_" + k for k in names] + ["tm_" + k for k in ANCHORS if not k.endswith("_target")]
    n_ok = 0
    for name in names:
        short = name.split("_", 1)[1] if name.startswith("tower_") else name
        x, y, z = v.anchors[name]
        h = 0.975 if (short in BABY_SPOTS or name in BABY_SPOTS) else (2.7 if short in GOLEM_SPOTS else 1.95)
        under = _solid_at(w, x, y, z - 0.05)
        # bed_beside stands in the second bed's cells: valid only BEFORE P.bed2.place_at (beat 6), so bed2 is ignored
        free_ok = ("water",) + (("red_bed",) if short == "bed_beside" else ())
        body = [zz for zz in (z + 0.3, z + 0.5 * h, z + h - 0.1) if _solid_at(w, x, y, zz)
                and w.block_id(int(math.floor(x)), int(math.floor(y)), int(math.floor(zz))) not in free_ok]
        if not under or body:
            bad.append("anchor %s at %s: %s" % (name, tuple(round(c, 2) for c in (x, y, z)),
                                               "nothing solid under it" if not under else "inside a block"))
        else:
            n_ok += 1
    say("[twentyminutes_set] anchors standing on solid ground with the body free: %d of %d" % (n_ok, len(names)))
    # cameras
    parts = part_cells(fm)
    for key, c in CAMERAS.items():
        for k in ("pos", "pos1"):
            if k not in c:
                continue
            cell = tuple(int(math.floor(a)) for a in c[k])
            if _solid_at(w, *c[k]):
                bad.append("camera %s %s %s is inside %s" % (key, k, c[k], w.block_id(*cell)))
            elif cell in parts:
                bad.append("camera %s %s %s is inside the part %s" % (key, k, c[k], parts[cell]))
    say("[twentyminutes_set] cameras checked: %d (pos and pos1)" % len(CAMERAS))
    # heroes in the safe area, not hidden (at each beat's main frame)
    for beat in BEATS:
        f = sc.frames[beat][0][0]
        sc.film.goto(f)
        cam = sc.scene.camera
        cp = tuple(cam.matrix_world.translation)
        for label, p in sc.heroes[beat].items():
            x, y, front = project(sc.scene, cam, tuple(p))
            hit = ray_block(w, cp, tuple(p))
            msg = "%s %s: x %.0f %%, y %.0f %%%s" % (beat, label, x, y, ("; hidden by %s at %s" % (hit[1], hit[0]))
                                                       if hit else "")
            if not (front and 8 <= x <= 82 and 14 <= y <= 60) or hit:
                (notes if (beat, label) in KNOWN else bad).append(msg)
    for n in notes:
        say("[twentyminutes_set] note (known limit) " + n)
    for b_ in bad:
        print("[twentyminutes_set] FAIL " + b_)
    print("[twentyminutes_set] check %s (%d failures, %d notes)" % ("ok" if not bad else "FAILED", len(bad),
                                                                    len(notes)))
    return bad


# (beat, hero label) pairs measured outside the safe area or behind a block ON PURPOSE (seen on the stills): printed
# as notes by check(), not failures
KNOWN = {("b03", "baby"),            # the baby runs in from the left edge (18 mm: 1.2 blocks behind Steve is 30 %)
         ("b06", "mom"), ("b06", "zombie"),     # the pan's two ends: Mom is passed in the middle of the pan
         ("b09", "mom"),             # a background shape behind the glass at the right edge (x 86 %)
         ("b11", "slot"),            # the slot is the bottom of the frame (the golem drops into it)
         ("b14", "mom"),             # behind the plug from here; only her hat shows at the left edge (story: a shape)
         ("b18", "mom"),             # not in this framing (the bed and the baby are)
         ("b22", "top step"),        # below the floor line from inside: Steve's swings show, the step does not
         ("b22o", "top step")}       # low in the frame (y 62-70 %): the crack reads on its top face


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args or args[0] == "check":
        sys.exit(1 if check() else 0)
    dry, palette = "--dry" in args, "--palette" in args
    res, samples, names = (540, 960), 16, []
    it = iter(a for a in args if a not in ("--dry", "--palette"))
    for a in it:
        if a == "--res":
            res = tuple(int(c) for c in next(it).split("x"))
        elif a == "--samples":
            samples = int(next(it))
        else:
            names.append(a)
    unknown = [n for n in names if n.partition(":")[0] not in CAMERAS]
    if unknown:
        print("unknown beats %s; known: %s" % (unknown, " ".join(BEATS)))
        sys.exit(2)
    stills(names, res=res, samples=samples, dry=dry, palette=palette)
