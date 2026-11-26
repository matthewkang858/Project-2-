"""UNDERGROUND: the player's trading hall of "Two Apples" (film two, stories/underground.json), under the village
square, lit by the game's own BLOCK LIGHT. New module; edits no other file.

Everything is built into the village through village.build_village(..., edit=hook) like engine/sets.py's pieces
(one World, one mesh, the village's checks), from the game's own blocks; numbers are transcribed from the 26.3
client jar (the class or file is named beside each constant). Blender axes: +X east, +Y north, +Z up, 1 block =
1 unit, the square's ground at z 0, characters face -Y at yaw 0, 24 fps (1 game tick = 1.2 frames).

    from engine import underground as U
    v, ug = U.build_village(scene, seed=1)          # the village WITH the set (hook + finish); edit= adds yours
    A, C = v.anchors, U.CAMERAS                     # A["ug_cell_dad"], C["b12_cell"] = dict(pos, target, lens, fstop)
    st = Stage(scene, film, v, skies=SKIES, sky=sky)   # SKIES: "dusk" for the square / house, "under" below (see SKY)
    ug.register(st)                                 # the lever in st.cast: st.use(s, ug.lever) where it is seen

PUBLIC API
  build_village(scene, seed=1, bed_colors=None, edit=None, **kw) -> (Village, UndergroundSet)
      village.build_village with underground_set in its hook (your own `edit` runs first), then finish(v).
  underground_set(b, name="underground", bed=BED, bed_color="red", rim=True) -> dict      IN A HOOK of your own;
      then call finish(v) after build_village. The stair mouth, stairwell, hall, cells, piston wall, zombie box,
      lights, dad's red bed (house_a_bed_2), the baked light; anchors, paths. Village.sets["underground"].
  finish(v) -> UndergroundSet     meshes the cutaways and the doorway's two copies, gives the baked faces their
      emission, builds the piston door and the lever (engine.redstone kit), lights them like the wall they sit in,
      adds the hall's fill.
  UndergroundSet (ug)
      ug.door        engine.redstone PistonDoor: two stone blocks at DOOR (dad's back wall), sticky pistons west of
                     them (hidden in the back wall behind the 2-wide pier). ug.door.open(f) / close(f) -> end time
                     (2 ticks = 2.4 frames), ug.door.is_open(t).
      ug.lever       engine.redstone Lever, on the north face of the end pier (LEVER), off.
      ug.open_wall(frame, player=None, reach=True, look=True, relight=None, repeater=0, sync="game")
                     -> dict(flip, open, open_end, hand): the lever flipped on `frame` (by `player`:
                     redstone.flip_by, his swing starts on frame; sync="hand" moves the lever on the frame his hand
                     is nearest it, `hand`), the wall opening 2 ticks later (a hidden inverter: a redstone torch
                     behind the pier) + 2 ticks per step of a hidden repeater (repeater=4: 12 frames after the flip).
                     relight=(st, shot): light_doorway in that shot from r["open"] (beat 24).
      ug.close_wall(frame, lever=True) -> end frame          the lever back 2 ticks before, the wall shut on frame.
      ug.light_doorway(st, shot, frame) -> frame    in ONE shot, from `frame` on: the doorway's floor and ceiling
                     and the box's inside drawn with the light the game gives them once the wall is open (door
                     cells 9-10, box 8-9) instead of the box's darkness, which every other frame keeps (two meshed
                     copies, ug.doorway["dark"] / ["lit"], swapped by hide_render keys: in the stamp).
      ug.parts = [door, lever]; ug.register(st, door=False, lever=True) puts the lever (and with door=True the door)
                     in st.cast: a registered part is hidden in every shot that does not st.use it. st.use(s,
                     ug.lever) (or *ug.parts) in every shot that sees the end pier's north face; leave it out of a
                     shot that sees through "ug_end_pier" (it would float). The door is unregistered by default: it
                     is always there and only moves when opened (registered and forgotten, it would leave a hole).
      ug.brightness_at(point) -> 0..1 the game's brightness there (its block / sky light through the lightmap).
      ug.env         the BlockLight environment (levels(cell) -> (block, sky), block_at, level_at).
      ug.anchors / ug.cameras / ug.cutaways / ug.doorway
  Cutaways (Village.cutaways: st.see_through(shot, name) = invisible to the camera only, st.remove = gone):
      "ug_ceiling"   everything above the hall from x -9 to 20, y -17 to -10 (z F+3 .. -2): beat 7 looks down
                     into the cells; the camera sits INSIDE it (z -7 .. -1.2), never above z -1 (the square's ground).
      "ug_caps"      the stone caps over the four job cells (F+2): beat 7 (with "ug_ceiling").
      "ug_end_wall"  the end wall beside dad's cell and behind it (x 15, y -15..-14): beats 13, 19, 24.
      "ug_end_pier"  the end pier in front of it (x 15, y -13; the lever hangs on it): beats 13, 16, 19.
      "ug_box_side"  the box's east wall above the slot (x 15, y -16, z F+1, F+2): beat 24.
      "ug_slot"      the slot's iron bars (x 15, y -16, z F): beat 24 when the bars would cross the lens.
      Faces that only a cutaway reveals are lit as if it were gone (the game's light through the open space).
      A see-through cutaway still casts shadows (Stage.see_through).
  Mechanics (frames are film frames):
      push(player, villager, frame, path, world, taps=(4, 4), steps_down=1, gap=0.9, legs=False) -> dict
          the player walks into the villager and pushes him along `path` with the game's entity push until he
          drops down `steps_down` steps; both are placed on `frame`. Returns end, drops (landing frames), speed ...
      hurt_in_cell(villager, frame, attacker=None, max_back=CELL_MAX_BACK) -> dict(end, peak, landed)
          a blow in his capped cell (beats 10, 11): undead.hurt's red flash and leg kick, and the knock-back as the
          game plays it under the cap: up 0.05 for one tick (cell_track), at most 0.05 toward the job block.
      infect_in_cell(villager, zombie_villager, frame, attacker=None) -> dict(end, peak)    undead.infect with the
          same capped jolt on the zombie villager (beat 12).
      cell_track(strength=0.4, max_back=0.05, room=0.05) -> [(forward, up)] per tick      the capped knock-back.
      bed_bounce(child, frame, spot, jumps=6, mode="game", settle=True) -> dict(end, takeoffs, landings, peaks,
          track)      JumpOnBed as the brain plays it (mode "game": `jumps` jump() calls, the ones that fall in the
          air are spent: 3 give ONE jump and the bed's bounces, 6 give two jumps 36 frames apart; jumps=(6, 6)
          runs the behaviour twice back to back); mode "regular" (NOT THE GAME): a jump every 14.4 frames.
      jump_loop(player, frame_start, frame_end) -> take-off frames      the player jumping on the spot, held.
      swap_hidden(child, adult, camera, frame_start, frame_end, world, then=None, speed=None) -> dict(frame, hidden)
          the child replaced by the grown-up on a frame where the well hides it from `camera` (a point or f -> point).
      hidden_frames(world, camera, character, f0, f1) -> frames on which the character is hidden by blocks.
      hands_in_slot(zv, frame, slot=SLOT, lateral=0.0, face="away") -> dict      the baby zombie villager against the
          slot's bars, facing out, the two tiny hands between the bars (in the bars' two gaps), fingertips in the
          pane; face="away" turns his big head down and away (HIDE_FACE_LOOK): beat 8, the face must never read.
      shade_face(v, zv) -> collection     keeps the baby's head and robe out of the corner torch's point light
          (Blender light linking, static for the film; his hands still catch it). Call it once, for beat 8.
      hold_then_move(shot, frame_move, pos0, target0, pos1, target1, frame_end=None, ease="smooth") -> shot
          a camera that holds until frame_move, then moves (Shot.move eases over the whole shot). Call it INSTEAD
          of s.move (it re-times the Shot's own curve; a later s.move keeps that timing).
      cheat(target, head, camera, k=0.35) -> point   a look target turned part of the way to the lens.
      bounce(st, shot, pos, energy=35, color=..., start=None, kind="fill", name=None) -> light   a film-local light
          for ONE shot (hidden elsewhere, so it is in no other frame's stamp): COUNTER_BOUNCE (beat 13),
          DOORWAY_GLOW / DOORWAY_WATTS with kind="torch", start=r["open"] (beat 24: the light that falls into the
          box when the wall opens), SLOT_STRIP / SLOT_STRIP_WATTS kind="torch" (beat 24: the strip through the bars).
  The light (see THE GAME'S LIGHT): lightmap_rgb(block, sky, ...), face_light(block, sky) -> (D, E), flood(opaque,
      sources), env(b) -> BlockLight, relight_object(ob, env, cell=None, levels=None) (a separate object lit like a
      World face: what finish() does to the door and the lever; use it for any prop placed in the hall).
  Constants: F (hall floor -10), CELL_X, PROFESSION, JOB, DOOR, LEVER, BOX, SLOT, LIGHTS, LIGHT_GROUPS, CAMERAS,
      CELL_HEADROOM, CELL_MAX_BACK, STEVE_PAST, SLOT_FACE, SLOT_STRIP(_WATTS), APPLE_POINT, HIDE_FACE_LOOK, WARMTH,
      EMIT, POINT_COLOR, FILL_SHARE, BOX_SEALED, DOOR_KEEPS_DARK, PUSH_STRENGTH, VILLAGER_PUSHES, BED_RESTITUTION,
      COUNTER_BOUNCE, DOORWAY_GLOW, DOORWAY_WATTS, WINDOW_PIER, RELIT_CELLS ...

THE SET (seed 1; the well's stone is x -3..2, y -3..2)
  mouth      2 wide (x 4..5) beside the well's east side, open over y 0..-3, the rim turned to grass (x 3..6,
             y -4..1; the plaza's path cells there are grass now). ug_lip (4.85, 1.42, 0) is the lip.
  stairwell  ten stone stairs facing north, x 4..5, y 0..-9 (step k: top -k, front half -k-0.5), 3 high, its
             ceiling stepping down (the square's ground over step 4, then the lining). Walls and ceiling lined in
             stone from just under the grass (z -2), mixed at -7, deepslate below (from about step 6). Wall torches
             at y -2, -3 (just under the rim: the glow from below), -6, -9; the landing y -10 (floor F = -10) with a
             torch (ug_foot).
  aisle      east-west, y -12..-11 (2 wide: y -12 .. -10), x -8..19, deepslate walls and ceiling, deepslate-brick
             floor; west of the stair foot (x -8..3) it has no torch and falls off into the dark. A torch over the
             farmer / fletcher (x 9), the hanging lantern over the aisle's north half (10, -11), a torch facing dad's
             cell (x 14); the back corner x 16..19, y -17..-13 (4 wide, one block past the slot) with its one torch
             on its east wall (19, -14, F+1), 4 blocks from the slot.
  cells      stone, one block wide and TWO high under a stone cap at F+2 (the classic trading-hall cell: the cap
             stops the knock-back hop after 0.05; the caps over the job cells are "ug_caps"), facing north into the
             aisle: farmer x 7 (composter), fletcher x 9 (fletching table), cleric x 11 (brewing stand), [2-wide pier
             x 12..13], dad x 14 (lectern), end pier x 15. The front row (y -13) is one long counter from x 7 to 14:
             stone or a job block at the floor, a window at face height (F+1), iron bars above (F+2), over the pier
             too (WINDOW_PIER); iron bars between the first three cells (F, F+1); every bars block connected from its
             real neighbours (IronBarsBlock.attachsTo). Villagers at ug_cell_<name> (y -13.3, against the job
             block; dad 0.18 west of centre: DAD_OFFSET; ug_cell_dad_mid is the centre, for a head turned west).
  piston wall  dad's back wall (14, -15, F and F+1): two stone blocks on sticky pistons at x 12, heads at x 13.
  lever      wall lever on the end pier's north face, (15, -12, F+1); Steve at ug_lever_stand (a block north of
             it, facing south).
  zombie box (14, -16), 1 x 1 x 2 inside, stone, smooth stone lid at F+2, its only opening the slot of iron bars
             at floor level in its east wall (15, -16, F) facing the back corner. The open piston wall joins it to
             dad's cell: the doorway behind dad IS the box.
  bedroom    house_a (the roomiest vanilla house), bed house_a_bed_2 dyed red, its own wall torches and windows.
  Anchors: ug_lip, ug_lip_target, ug_mouth_target, ug_push_start, ug_push_player, ug_stair_top, ug_stair_foot,
    ug_cell_<farmer|fletcher|cleric|dad> (+ _station), ug_cell_dad_mid, ug_aisle_<name> (in front of the cell),
    ug_lever_stand, ug_lever_target, ug_counter_steve (beat 13), ug_door_target, ug_box, ug_slot_hands,
    ug_slot_target, ug_corner, ug_leg_north, ug_aisle_west_end, ug_aisle_center, ug_jump_spot (beat 16, x 12.3),
    ug_follow_start / ug_follow_end (beat 18). Paths: ug_down (square -> stairs -> aisle, with the steps'
    heights), ug_aisle (stair foot -> dad's cell), ug_leg (past the end pier to the slot), ug_push (to the lip),
    ug_round_well (beat 20); U.STEVE_PAST (beat 8). Yaws in v.yaws[anchor].
  Light groups (Stage.lights groups=): ug_mouth, ug_stairs, ug_foot, ug_hall, ug_dad, ug_corner (one point light
    per torch / lantern, colour POINT_COLOR); "ug_hall" also holds the hall's cool shadowless fill, in two halves
    (over the aisle, and in the leg east of dad's cell), on only with inside="ug_hall".

SKY (a multi-sky film: films/_multisky_demo.py)
    SKIES = {"dusk":  dict(preset="dusk", az=187.0, el=5.0, bloom=1.3, grade="warm"),
             "under": dict(preset="dusk", az=187.0, el=5.0, key=0.0, ambient=0.0, bloom=1.3, grade="neutral",
                           haze=0.0)}
  "under" is the same dusk with no sun, no sky fill, no bounce lamps and no distance haze: below the ground the
  only light is the baked block light and the torches. Nothing in the set depends on the sky. Torches below:
  Stage.lights(s, scale=0.0, groups={g: 0.7 for g in U.LIGHT_GROUPS}, inside="ug_hall") (0.7 keeps torch-lit stone
  near the game's brightness, MEASURED); for the box and slot shots leave inside out (the fill passes through
  walls and would light the box). The proof film (tools/underground_proof.py `_under`) does exactly this.

BEATS (camera = U.CAMERAS[name]: pos, target, lens, fstop (+ pos0 / target0 or pos1 / target1 for a move); every
one was rendered through films.lookdev.Stage and the SKIES above and looked at: out/test/underground_<still>.png;
the recipes are the proof film's, tools/underground_proof.py shot_<still>)
   1 mouth      dusk, 3.5 s. b01_mouth: steve placed at (5, 6.5, 0) on the shot's first frame, steve.walk(f0,
                [(5, 6.5, 0)] + v.paths["ug_down"][1:10], speed=players.WALK_SPEED); s.move(C["pos0"], steve.head,
                C["pos"], C["target"]) (the aim rides on his head, eases onto the glowing hole, the camera pushes
                in). MEASURED: his head is in the picture on frames 0..60 of the shot and in the Reels safe area on
                0..53; he is in profile at the lip on frame 36 (still "mouth"). Lights: st.lights(s, scale=1.3,
                groups={g: 1.0 for g in U.LIGHT_GROUPS}, near=A["ug_mouth_target"], radius=22).
   2 lip        dusk. b02_lip: the child at A["ug_lip"] (yaw v.yaws["ug_lip"]: south), look_at(U.cheat(
                A["ug_lip_target"], A["ug_lip"], cam pos, 0.35), ease=0); the glow from below is ug_mouth.
   3 push       dusk. b03_push (side-on from the east, low; the well behind them): r = U.push(steve, dad, f,
                v.paths["ug_push"] + [(5.0, -2.0, 0.0)], v.world); dad.look_at(f, (cam x, cam y - 0.6, 1.4),
                ease=0) held to the end; the child at C["b03_push"]["kid"] facing dad (look_at dad, ease=0) is the
                soft head in the bottom right corner. From ug_push_start dad drops down the first step 59 frames
                after f (MEASURED, 1.16 blocks/s in nudges). Sheet: underground_push_sheet.png.
   4 bed        dusk. b04_bed (aimed high enough for the 1.25-block jump: the head at its top stays in the safe
                area): kid placed on v.beds[U.BED]["foot"] (yaw bed yaw + pi), U.bed_bounce(kid, f, foot, jumps=6)
                (the game: a jump, the bed's bounces, a second jump 36 frames later; jumps=(6, 6) for more); lights
                scale 1.2, groups={"house_a": 1.5}, near=A["house_a_center"], radius=14, inside="house_a". Sheet:
                underground_bed_sheet.png.
   5 bed wide   dusk. b05_bed_wide: the kid standing on the foot facing the door, look_at the lens; locked off.
   6 stairwell  dusk (the top of the flight has sky light). b06_stairwell: kid placed at v.paths["ug_down"][1],
                kid.walk(f, path[1:], speed=4.4, run=True); kid.track(f, f_end, (4.1, -5.5, -4.4), step=2, ease=4)
                (his head follows the west wall's torch as he passes it at y -5.6: still "stairwell"); lights
                scale 0 with every ug group at 1.0. Tiny in the frame, as the story asks: his turned head shows
                the side of his face, the nose is a few pixels.
   7 down       under. st.see_through(s, "ug_ceiling") AND (s, "ug_caps"); b07_down: from above the aisle 70
                degrees down into the pockets (the frame's up is south), s.move(pos0, target0, pos, target) from
                over the farmer to over dad (stills "down_start", "down"); dad.look_at(f, C["b07_down"]["pos"],
                ease=0) (his face up at us); the box's smooth stone lid behind his cell, the lever on the end pier.
                Others look_at up(A["ug_aisle_<name>"], 1.4). Fallback (story risks): the counter ride from 0.7.
   8 slot       under, 2.5 s. b08_slot (on the floor against the back corner's east wall, square on to the slot
                3.75 away): steve placed at U.STEVE_PAST[0] (yaw north), steve.walk(f, U.STEVE_PAST,
                speed=players.WALK_SPEED): he walks south to north, frame left to right, 2.15 from the lens; focus
                s.focus(C["b08_slot"]["boot"]); zv = undead.add_zombie_villager(st, name, "none", baby=True);
                U.hands_in_slot(zv, f) (face="away") and U.shade_face(st.v, zv): the hands catch the corner torch,
                his head is a dark green shape, the face never reads (stills "slot_boots", "slot_hands"). Lights as
                below, NO inside. His boots are sharpest with the legs together (the proof still picks that frame).
   9 lever      under, 2.5 s. Steve at A["ug_lever_stand"] (yaw v.yaws: south; out of the frame but for his right
                arm); r = ug.open_wall(f + 10, player=steve, repeater=4, sync="hand"); b09_lever:
                U.hold_then_move(s, r["flip"] + 2, C["pos"], C["target0"], C["pos"], C["target"],
                frame_end=r["open"] - 1) (held on the lever while his arm swings in from the left and flips it,
                then a pan right onto the back wall past dad); s.focus(A["ug_lever_target"]); s.focus(
                A["ug_door_target"], at_s=film.seconds(r["flip"] + 3), rack_s=0.4). The wall jerks aside 12
                frames after the flip, when the pan has arrived; the doorway black beside his robe; dad faces
                front. Sheet: underground_lever_sheet.png; still "lever" is the end.
  10 hit        under. b10_cell_side (low, east of the cell axis, the lectern in the bottom third): the strip of
                black doorway shows left of his robe (stills "cell_shut" / "cell_open"). U.hurt_in_cell(dad, f,
                attacker=A["ug_door_target"]) (the cap stops the hop: a jolt of 0.05 for one tick, 0.05 forward
                against the lectern; the attacker is not in the shot).
  11 portrait   under. b11_portrait (40 mm): the second blow U.hurt_in_cell(dad, f + 14, ...) (12 frames or more
                after the first; an earlier one is ignored, as the game ignores it). MEASURED: through the blows his
                head stays at 45-52 % of the frame height, the jolt moves it 2.2 %. Sheet: underground_hit_sheet.png.
  12 turn       under. b12_cell (frontal, symmetric; still "cell"; dead ahead he hides the doorway):
                U.infect_in_cell(dad, zv_dad, f, attacker=A["ug_door_target"]) (zv_dad = undead.add_zombie_villager(
                st, ..., "librarian")); zv_dad.aggro(f, ease=0) for the arms out. Head moves 1.0 % of the frame.
  13 potion     under. b13_counter (20 mm, side-on from the east): st.see_through(s, "ug_end_pier") and
                (s, "ug_end_wall"); the lever NOT used (hidden); Steve at A["ug_counter_steve"] (yaw there);
                undead.throw_potion(steve, zv_dad, f, camera=s); steve.hold("golden_apple") before his place,
                raise_arm. Lights: the ug_dad torch x 1.8 (extra=[((14.5, -10.6, F + 1.9), 1.8)]) and
                U.bounce(st, s, U.COUNTER_BOUNCE): without it his trousers are crushed (palette check, MEASURED).
  14 apple      under. b14_apple: Steve at A["ug_aisle_dad"], steve.hold("golden_apple"), raise_arm(f, 55):
                C["target"] = U.APPLE_POINT is the apple then (MEASURED); if he moves aim and focus at
                steve.item_point("right", f) (C["target_from"]). 50 mm, f/1.8.
  15 drift      under. b15_drift (pos0 -> pos): the wall open (ug.door.open), undead.cure(zv_dad, dad, f, ...,
                shake=3) starting, focus on (14.6, -15.0, F + 1); on the last word ug.close_wall(f).
  16 wide       under. b16_aisle (20 mm, from the aisle's east end, through st.see_through(s, "ug_end_pier"); the
                lever not used): zombie dad in his window on the left shaking with yellow swirls, the cleric,
                fletcher and farmer in theirs, Steve at A["ug_jump_spot"] (yaw v.yaws[...]) with U.jump_loop(steve,
                f0, f1); the lantern hangs well right of him even at the top of a jump (still "aisle" is a peak).
  17 trade      under. b17_ots: Steve at A["ug_aisle_dad"] holding the emerald up (raise_arm 55), dad holds out the
                book (engine.fx hold_out), Nausea swirls from cure(). From beat 18 on dad stands at ug_cell_dad_mid.
  18 follow     under. b18_portrait (from in front, a little above his eyes): dad at A["ug_cell_dad_mid"],
                dad.look_at(f, steve, ease=0) then dad.track(f, f1, steve, step=2) as Steve walks
                A["ug_follow_start"] -> A["ug_follow_end"] (under the lens): his face turns into profile, the big
                nose toward the stair foot, and holds at the 70-degree stop.
  19 behind     under, 2 s. b19_endwall: st.see_through(s, "ug_end_wall") AND (s, "ug_end_pier") (the lever not
                used); dad at ug_cell_dad_mid, dad.look_at(f, C["b19_endwall"]["look"], ease=0) (up the aisle, 20
                degrees west of north: from this camera his profile, MEASURED 93 degrees off the lens); s.move(
                C["pos0"], C["target0"], C["pos"], C["target"]): the slide off his face onto the piston wall behind
                his back (still "endwall" is the start). b19_alt: from the aisle north-west, his face to the lens.
  20 grow up    dusk. b20_well (south-east: the well, the glowing mouth in front of it): two children run
                v.paths["ug_round_well"], 0.7 block apart in time; r = U.swap_hidden(child, adult,
                C["b20_well"]["pos"], f0, f1, v.world, then=[(3.6, 1.8, 0)], speed=1.6): MEASURED at 4.4 blocks/s
                the child is hidden for about 80 frames behind the well's stone, the swap lands in its middle.
  21 slot       under. b08_slot again, no hands (still "slot": black inside); focus on U.SLOT_FACE, s.move(pos,
                target, pos1, target1) (the slow push in); Steve's legs pass as in beat 8 (the slot ends at his
                waist).
  22 foot       under. b22_foot: the child at A["ug_stair_foot"] (yaw south), look_at the lens; the zombie from the
                dark west aisle (A["ug_aisle_west_end"] + 6 east), z.aggro(f); the rim light is the ug_foot torch.
  23 kill       under. b23_kill: steve.hold("iron_sword"), steve.attack(f); undead.die(z, f, camera=s,
                attacker=steve) (the rotten flesh: engine.mobs make_dropped_item).
  24 box        under, 3 s. b24_box (stills "box", "box_open", sheet underground_box_sheet.png):
                st.see_through(s, "ug_box_side"), (s, "ug_end_wall"), (s, "ug_slot"); zv at A["ug_box"] (yaw
                v.yaws: north), zv.look_at(f, U.cheat(A["ug_door_target"], up(A["ug_box"], 0.8), cam pos, 0.7),
                ease=0) (three-quarter to us); dad at A["ug_cell_dad"]; U.bounce(st, s, U.SLOT_STRIP,
                energy=U.SLOT_STRIP_WATTS, color=U.POINT_COLOR, kind="torch", name=...) (the strip of torchlight
                through the bars, the whole shot); lights 0.7, NO inside, extra=[((14.5, -10.6, F + 1.9), 2.5)].
                Hold a second, then r = ug.open_wall(f_open, relight=(st, s)) (the lever flips off screen; the
                doorway's floor, ceiling and the box come up lit) and U.bounce(st, s, U.DOORWAY_GLOW,
                energy=U.DOORWAY_WATTS, color=U.POINT_COLOR, start=r["open"], kind="torch") (the warm light on his
                face). His step: run = r["open_end"] + 6; zv.look_at(run - 3, up(A["ug_cell_dad"], 1.5), ease=3);
                zv.walk(run, [A["ug_box"], (14.6, -14.9, F)]); the pan RIGHT (north) with it:
                U.hold_then_move(s, run, C["pos"], C["target"], C["pos1"], C["target1"], frame_end=run + 16) onto
                dad's back and book hat; s.focus(zv.head) then s.focus(dad.head, at_s=film.seconds(run + 4)).

THE GAME'S LIGHT, AND WHAT IS BAKED
  The game draws a block face with the light of the cell it faces (Smooth Lighting off here: one value per face).
  BLOCK light: every emitter's cell gets its level (LIGHT_EMISSION: torch / wall torch 14, lantern 15 ...), every
  neighbour one less, through anything that is not an opaque full cube (BlockLightEngine.propagateIncrease, level
  - max(1, getLightDampening): iron bars pass it with dampening 0, CrossCollisionBlock.propagatesSkylightDown);
  SKY light likewise from 15 down open columns (the stairwell's mouth). LIGHTMAP (lightmap.fsh): ambient #0a0a0a +
  sky + mix(#FFD88C, white, 0.9 (2 l - 1)^2) * l / (4 - 3 l) * 1.4, clamped, then half-way to notGamma (Brightness
  50 %): level 0 = 0.094, 4 = 0.33, 7 = 0.52, 11 = 0.79, 14 = 1.0 (warm in the middle levels, white near the
  source). Face shade CardinalLighting: up 1.0, down 0.5, north / south 0.8, east / west 0.6. A face here is
  drawn: texel x D (grey, baked into the texture: it dims whatever scene light falls on it) + texel x E (emission:
  the game's lightmap colour x the face shade, x EMIT). So without any scene light the set looks like the game;
  the torches' real point lights (shadows, glow, bloom) come on top.

MEASURED (on the stills of this version)
  The aisle with every point light off (still "falloff": the bake alone), tools.underground_proof measure()
  (ray-cast pixels, displayed / texel against the game's lightmap x cardinal shade; levels with hundreds of samples
  are the reliable ones): level 9 walls 0.34 / game 0.39 (291 samples); 10 walls 0.46 / 0.43 (315), floor 0.63 /
  0.72 (323); 11 walls 0.62 / 0.63 (853), floor 0.65 / 0.79 (1063); 12 walls 0.70 / 0.69 (399), floor 0.73 / 0.87
  (1040): the game's falloff within 10-20 %. The dark end (levels 0-4, few samples) renders 0.24-0.39 against
  0.05-0.32: the bounce of the lit faces (Fast GI) that the game does not have.
  The black doorway (stills "cell_shut" / "cell_open", the b10 camera, torches 0.7): the 8900 pixels that change
  when the wall opens have mean 76 / 255 shut and 11 / 255 open; the lit wall beside them 83.
  Bake: dad's cell block light 11 (brightness 0.79), the box 0 (sealed; the game: about 6), the aisle's west end
  1, the mouth's rim 10 under open sky; the lit doorway copy: door cells 9-10, box 8-9. Push: 1.16 block/s, the
  player never passes him (closest 0.38 between centres); with the key HELD he walks through him. Bed (game):
  3 calls = one jump of 1.252 and the bounces 0.556, 0.238, 0.104, 0.042; 6 calls = take-offs 36 frames apart.
  Jump loop: take-offs every 14-15 frames, 1.252 high. Cell blows: a jolt of 0.050 up for one tick; dad's head
  moves 2.2 % of the frame height in b11, 1.0-1.3 % in b10 / b12. Hands: fingertips 0.5 px into the 2 px pane.
  Every proof still passes tools/palette_check (stone G/R, Steve's trousers >= 12, robes, skin) and its hero's
  safe-area check.

NOT THE GAME
  - WARMTH 0.4: the block-light tint is 40 % of the way from white to #FFD88C. The game's own tint makes lit
    stone G/R 0.87-0.90 at levels 6-12, under the palette rule's 0.92 (tools/palette_check): a film choice.
  - POINT_COLOR (1, 0.92, 0.80) for this set's torches (the game's light near a source), paler than the village's
    props.TORCH_COLOR, which pushed villager skin over the palette's 0.52.
  - BOX_SEALED: the slot's bars count as opaque in the bake, so the box is black inside. The game lets light
    through iron bars at full strength (dampening 0, one level per step): the box would be at about level 6 from
    the corner torch, plainly lit. DOOR_KEEPS_DARK: the doorway keeps the box's darkness when it opens (the game
    re-lights it within a tick), except in the shot that calls light_doorway (beat 24). Both are what the story
    needs (a black slot, a black doorway from the aisle); the torches' point lights still reach in.
  - shade_face: the baby's head and robe get no light from the corner torch (light linking); the game draws a mob
    at the block light of its cell, the same from every side.
  - Characters are not baked: they are lit by the point lights, the fill and what the glowing faces around them
    bounce (the game draws a mob at the block light of its position, from every side alike).
  - Smooth lighting and ambient occlusion are not reproduced (flat per face); slabs / stairs pass light.
  - The game's 50 % Brightness lifts dark levels a lot (level 4 = 0.33); "Moody" would be lightmap_rgb(gamma=0).
  - push(): the player's taps (4 ticks pressed, 4 released) are a film choice; held, the game lets him walk
    through the villager.
  - bed_bounce(mode="regular") and jumps=(6, 6) (the behaviour run twice back to back) are film choices; the
    default is the game's JumpOnBed.
  - jump_loop keys the open-air jump (1.252); under the aisle's 3-high ceiling the game stops the head at the
    ceiling (1.20, one tick earlier down): his head top is 0.05 inside the ceiling for about 2 frames, unseen
    from below.
  - The hall's design (2-high cells with caps, a counter with a window over the 2-wide pier, the end pier with
    the lever, the hidden inverter and repeater, the 4-wide back corner) is ours: a player-built hall in the
    classic style, not a structure of the game.

GOTCHAS
  - films/lookdev.py Stage.see_through / remove key the cutaway VISIBLE again on the film's first frame every time
    they are called: a see-through shot that starts on the film's first frame loses its see-through as soon as a
    later shot sees through the same cutaway. Never open the film on such a shot (the proof film has a one-frame
    lead-in for this), or key visible_camera yourself.
  - Dad's cell is a 1-wide, 2-high pocket 0.3 behind the counter, between the 2-wide pier and the end pier: his
    face is seen from the aisle within about 45 degrees of frontal (on the west through the window over the pier,
    ug_cell_dad's DAD_OFFSET helps that), from straight above with the caps off (beat 7), or through a cutaway
    (ug_end_wall, ug_end_pier). The doorway behind him shows as a strip beside his robe from b09, b10_cell_side,
    b15_drift; dead ahead he hides it.
  - Use hurt_in_cell / infect_in_cell for a villager in his cell, not undead.hurt with an attacker: that is the
    open-air hop (0.96 up) and puts his head into the cap. During the 12 red frames Stage.hero finds his head
    hidden (undead's flash twins): take stills before or after a blow.
  - Cutaways see-through still cast shadows: a character behind ug_end_pier is in its shadow (beat 13: the extra
    on the ug_dad torch and U.bounce). The lever hangs on ug_end_pier: with ug.register(st) leave it out of a shot
    that sees through the pier (beats 13, 16, 19) and st.use it everywhere else it is seen.
  - The fill is shadowless and passes walls: never inside="ug_hall" in a box or slot shot (it would light the box).
  - Every under-ground shot that sees the back wall must find the door shut unless it opens it: ug.door.close(f)
    after a shot that opened it (the proof film does it in _shut()).
  - hold_then_move replaces the Shot's easing: call it once per shot instead of s.move (a later s.move keeps its
    hold), and s.focus after it.
  - shade_face is set on the corner torch for the whole film (not keyed): fine for this story (the box shots light
    the baby with SLOT_STRIP / DOORWAY_GLOW); it is in the frame stamp.
  - Proof characters are new per shot (the proof film pre-rolls walks); in a film keep the rule of CONTRACT.md:
    nobody keyed before a shot starts if he is in the shot before it (push() and bed_bounce() place on `frame`).
  - render.Session imports films.<name>: tools/underground_proof.py registers itself as films._underground_proof.

Self-test:  $BPY -m engine.underground              numeric checks (tools/underground_check.py, about 10 s: light
                                                    model, flood fill, the set, the bars, camera sight lines with
                                                    the unused cutaways solid, the cell jolt through b10-b12,
                                                    mechanics)
            $BPY -m engine.underground NAME ...     proof stills out/test/underground_<name>.png (540x960, 16 spp,
                                                    2 threads; 3-4 per call): mouth lip push well bed bed_wide
                                                    stairwell down down_start cell cell_open cell_shut lever hit
                                                    aisle endwall endwall_alt slot slot_hands slot_boots box
                                                    box_open foot falloff portrait counter apple drift ots follow
                                                    kill; sheets push_sheet bed_sheet lever_sheet hit_sheet
                                                    box_sheet (cell_open + cell_shut together print the doorway
                                                    measurement; aisle and falloff print measure(); mouth and
                                                    slot_boots print the hero's frames in the picture)
            $BPY -m tools.check_underground_stamp   frame fingerprints (15 cases, two processes, about 2 min)
"""
import math

import bpy
import numpy as np
from mathutils import Vector

from . import blocks as _blocks
from . import mcassets as mc
from . import sets
from .village import yaw_of, yaw_to

FPS = 24
TICK = FPS / 20.0                      # film frames per game tick (1.2)

# =====================================================================================================================
# THE GAME'S LIGHT (transcribed from the 26.3 client jar; no game file is copied)
# =====================================================================================================================
# lightmap.fsh (assets/minecraft/shaders/core): block_level = floor(u * 16) / 15, sky_level likewise;
#   brightness(l) = l / (4 - 3 l); colour = max(AmbientColor, NightVision) + SkyLightColor * brightness(sky) * SkyFactor
#   + mix(BlockLightTint, white, 0.9 * (2 l - 1)^2) * brightness(block) * BlockFactor; clamp 0..1; then
#   mix(colour, notGamma(colour), BrightnessFactor) with notGamma(c) = c * (1 - (1 - max(c))^4) / max(c).
BLOCK_FACTOR = 1.4                     # LightmapRenderStateExtractor.extract: blockFactor = blockLightFlicker + 1.4F
                                       # (tick(): flicker += (r1 - r2) * r3 * r4 * 0.1, then * 0.9: it averages 0)
BLOCK_LIGHT_TINT = (255, 216, 140)     # EnvironmentAttributes.BLOCK_LIGHT_TINT default ARGB.vector3fFromRGB24(-10100)
                                       # = #FFD88C (no dimension or timeline overrides it in the overworld)
AMBIENT_LIGHT = 10.0 / 255.0           # data/minecraft/dimension_type/overworld.json visual/ambient_light_color #0a0a0a
GAMMA = 0.5                            # Options.gamma default (the Brightness slider at 50 %, "Moody" = 0)
# timeline/day.json at the film's dusk (sun 5 degrees up = DimensionType celestial angle ~0.236 = tick ~12480):
# visual/sky_light_factor keyframes 11270 -> 1.0, 13140 -> 0.24; visual/sky_light_color #ffffff -> #7a7aff
DUSK_TICK = 12480
DUSK_SKY_FACTOR = 1.0 - (DUSK_TICK - 11270) / (13140.0 - 11270.0) * (1.0 - 0.24)          # 0.508
_k = (DUSK_TICK - 11270) / (13140.0 - 11270.0)
DUSK_SKY_COLOR = (1.0 - _k * (1.0 - 0x7a / 255.0), 1.0 - _k * (1.0 - 0x7a / 255.0), 1.0)   # (0.66, 0.66, 1.0)
del _k
# CardinalLighting.DEFAULT (down, up, north, south, west, east) = (0.5, 1.0, 0.8, 0.8, 0.6, 0.6): the shade the game
# multiplies into a block face by its direction (Blender: north = +Y, east = +X)
CARDINAL = {"down": 0.5, "up": 1.0, "north": 0.8, "south": 0.8, "west": 0.6, "east": 0.6}
# Blocks static init, the lightLevel of each block (lambdas read in the bytecode): TORCH lambda$static$71 -> 14,
# WALL_TORCH lambda$static$73 -> 14, LANTERN lambda$static$324 -> 15 (both hanging states), GLOWSTONE
# lambda$static$155 -> 15, LAVA lambda$static$15 -> 15, REDSTONE_TORCH / REDSTONE_WALL_TORCH litBlockEmission(7)
LIGHT_EMISSION = {"torch": 14, "wall_torch": 14, "lantern": 15, "glowstone": 15, "lava": 15, "redstone_torch": 7,
                  "redstone_wall_torch": 7}
# BlockLightEngine.propagateIncrease: a neighbour gets level - LightEngine.getOpacity(state) = level -
# max(1, getLightDampening()); BlockBehaviour.getLightDampening = 15 for isSolidRender (opaque full cubes), 0 for
# propagatesSkylightDown, else 1; so: minus one per block step through anything that is not an opaque full cube,
# stopped by opaque full cubes. (shapeOccludes of slabs / stairs is not modelled: they pass light here.)
# SkyLightEngine: 15 straight down through open columns, then the same minus one per step.
OCCLUDING = ("dirt_path", "farmland")  # not full cubes, but useShapeForLightOcclusion with a full bottom face: the
                                       # light of the sky does not go down through the plaza's path blocks

# ---- film choices (NOT the game; see NOT THE GAME in the docstring)
WARMTH = 0.4                           # the block-light tint used: 40 % of the way from white to #FFD88C (palette)
EMIT = 1.0                             # baked light drawn as emission x this (1 = the game's brightness exactly)
DOOR_KEEPS_DARK = True                 # the doorway is baked as the box behind it: the open doorway stays black
                                       # (except in a shot that calls ug.light_doorway: beat 24)
BOX_SEALED = True                      # the slot's bars count as opaque in the bake: the box is black inside (the
                                       # game: iron bars pass light at full strength - CrossCollisionBlock.
                                       # propagatesSkylightDown = !waterlogged, so getLightDampening 0 and one level
                                       # per step - and the box would be at about level 6 from the corner torch)
POINT_COLOR = (1.0, 0.92, 0.80)        # the set's torch / lantern point lights: the game's block light near its
                                       # source (lightmap level 13: (1, 0.92, 0.78)), paler than the village's
                                       # props.TORCH_COLOR (1, 0.88, 0.72), which pushes villager skin over 0.52
FILL_SHARE = 0.30                      # the hall's weak cool shadowless fill (group ug_hall, Stage.lights(inside=
                                       # "ug_hall")): this share of the hall torches' watts, as the village's rooms

# =====================================================================================================================
# THE SET (Blender cells; ground z = 0; the hall floor's walking surface is z = F)
# =====================================================================================================================
F = -10                                # hall floor walking surface (floor blocks at F - 1, air F .. F + 2, ceiling F + 3)
MOUTH_X = (4, 5)                       # the stair's two columns, east of the well (the well's stone is x -3 .. 2)
STEPS = 10                             # stone stairs at y = 0 .. -9 (step k: block z = -1 - k, top -k / -k - 0.5)
HEADROOM = 3                           # air above every step (the stairwell is 3 high, its ceiling steps down)
LANDING_Y = -10                        # the landing at the foot of the stairs (floor F)
AISLE_Y = (-12, -11)
AISLE_X = (-8, 19)                     # the aisle runs east-west; x -8 .. 3 is its unlit west stretch
LEG_X = (16, 19)                       # the aisle turns south past the end of the cell row into the back corner,
LEG_Y = (-17, -13)                     # 4 wide and one block past the slot (beat 8: the camera on the floor at its
                                       # east wall sees the slot square on, Steve's path 2 blocks from the lens)
FRONT_Y, CELL_Y, BACK_Y, BOX_Y = -13, -14, -15, -16
CELL_X = {"farmer": 7, "fletcher": 9, "cleric": 11, "dad": 14}
JOB = {"farmer": ("composter", {"level": "0"}), "fletcher": ("fletching_table", {}),
       "cleric": ("brewing_stand", {"has_bottle_0": "false", "has_bottle_1": "false", "has_bottle_2": "false"}),
       "dad": ("lectern", {"facing": "north", "has_book": "false", "powered": "false"})}
PROFESSION = {"farmer": "farmer", "fletcher": "fletcher", "cleric": "cleric", "dad": "librarian"}
END_X = 15                             # the end wall of the cell row (its front pier holds the lever)
WINDOW_PIER = (12, 13)                 # the 2-wide pier between the cleric and dad: solid behind (it hides the
                                       # pistons), but its front row is counter like the rest (stone, a window at
                                       # face height, bars): a solid front here hid every face beyond it from an
                                       # oblique camera in the aisle (beat 16)
BOX = (14, BOX_Y)                      # the zombie box: one cell behind dad's, 2 high, smooth stone lid
SLOT = (15, BOX_Y, F)                  # its only opening: iron bars at floor level in its east wall
DOOR = [(14, BACK_Y, F), (14, BACK_Y, F + 1)]       # dad's back wall: two stone blocks on sticky pistons ...
DOOR_SIDE = "west"                     # ... that slide sideways (west) into the back wall behind the 2-wide pier
DAD_OFFSET = -0.18                     # dad stands toward the west side of his cell (his box 0.6 wide in a 1-wide
                                       # cell): a strip of the doorway shows beside his robe from the east
LEVER = (15, -12, F + 1)               # a wall lever on the north face of the end pier (15, -13, F + 1)
ROCK = (-11, -19, F - 2, 20, 3, -2)    # the solid earth around all of it (x0, y0, z0, x1, y1, z1)
HOUSE = "house_a"                      # dad's house (the roomiest vanilla house: two beds, torches, windows)
BED = "house_a_bed_2"                  # dad's bed, dyed red
STAIR = {"facing": "north", "half": "bottom", "shape": "straight", "waterlogged": "false"}
BARS_NS = {"north": "true", "south": "true", "east": "false", "west": "false", "waterlogged": "false"}
BARS_EW = {"north": "false", "south": "false", "east": "true", "west": "true", "waterlogged": "false"}
# IronBarsBlock.attachsTo(state, sturdy): a side connects to a neighbour that is iron bars (or a wall), or whose
# facing side is sturdy (a full face: stone, deepslate, a fletching table, a composter's full sides), unless it is one
# of isExceptionForConnection's blocks (leaves, pumpkins, melons, shulker boxes, barrier). _connect_bars sets every
# bars block of the layout from its real neighbours (a lectern or a brewing stand is not sturdy; air is not).
BARS_STURDY = ("stone", "deepslate", "smooth_stone", "deepslate_bricks", "fletching_table", "composter", "dirt",
               "grass_block")
CELL_HEADROOM = 2                      # every cell is 2 high under a stone cap at F + 2 (the classic trading-hall cell:
                                       # a villager 1.95 tall fits, and the cap stops the knock-back hop after 0.05;
                                       # the caps over the four job cells are the cutaway "ug_caps", beat 7 removes
                                       # them)
CELL_MAX_BACK = 0.05                   # room in front of a villager at ug_cell_* before the job block stops him
# (cell, block, props, light group): every light of the set, with its point light (village.build b.torch)
LIGHTS = [
    ((4, -2, -1), "wall_torch", {"facing": "east"}, "ug_mouth"),     # just under the rim: the glow from below
    ((5, -3, -2), "wall_torch", {"facing": "west"}, "ug_mouth"),
    ((4, -6, -5), "wall_torch", {"facing": "east"}, "ug_stairs"),
    ((5, -9, -8), "wall_torch", {"facing": "west"}, "ug_stairs"),
    ((5, LANDING_Y, F + 1), "wall_torch", {"facing": "west"}, "ug_foot"),        # the foot: beat 22's rim light
    ((9, -11, F + 1), "wall_torch", {"facing": "south"}, "ug_hall"),             # facing the farmer / fletcher
    ((14, -11, F + 1), "wall_torch", {"facing": "south"}, "ug_dad"),             # facing dad's cell
    ((10, -11, F + 2), "lantern", {"hanging": "true"}, "ug_hall"),               # the one hanging lantern, over
    # the aisle's north half: from b16 it hangs well right of Steve's jump (over its south half it sat on his hair)
    ((19, -14, F + 1), "wall_torch", {"facing": "west"}, "ug_corner"),           # the back corner's one torch, on
    # the leg's east wall 4 blocks from the slot (the story: "one torch well away from the slot so the inside stays
    # black"); shade_face() keeps the baby's head and robe out of its light (the hands catch it)
]
LIGHT_GROUPS = ("ug_mouth", "ug_stairs", "ug_foot", "ug_hall", "ug_dad", "ug_corner")


def _rock(x, y, z):
    """What the earth is at a depth: dirt under the grass, then stone, deepslate from z -8 (z -7 is mixed)."""
    if z >= -4:
        return "dirt", None
    if z >= -6:
        return "stone", None
    if z == -7 and _blocks.pos_hash(x, y, z, 11) % 3:
        return "stone", None
    return "deepslate", {"axis": "y"}


# =====================================================================================================================
# light: the lightmap and the flood fill
# =====================================================================================================================

def _bright(level):
    """lightmap.fsh get_brightness for a level 0..15."""
    b = max(0.0, min(15.0, float(level))) / 15.0
    return b / (4.0 - 3.0 * b)


def lightmap_rgb(block=0, sky=0, sky_factor=1.0, sky_color=(1.0, 1.0, 1.0), tint=BLOCK_LIGHT_TINT, gamma=GAMMA,
                 ambient=AMBIENT_LIGHT, block_factor=BLOCK_FACTOR):
    """The colour (r, g, b) 0..1 the game multiplies into a texel at block light `block` and sky light `sky`
    (lightmap.fsh with the overworld's ambient #0a0a0a, BlockFactor 1.4, the Brightness option `gamma`)."""
    bl = max(0, min(15, int(block))) / 15.0
    c = [ambient] * 3
    sb = _bright(sky) * float(sky_factor)
    mixf = 0.9 * (2.0 * bl - 1.0) ** 2
    bb = _bright(block) * block_factor
    for i in range(3):
        t = tint[i] / 255.0
        c[i] += sky_color[i] * sb + (t + (1.0 - t) * mixf) * bb
        c[i] = min(1.0, max(0.0, c[i]))
    m = max(c)
    if m <= 0.0:
        return (0.0, 0.0, 0.0)
    scaled = 1.0 - (1.0 - m) ** 4
    return tuple(ci + (ci * scaled / m - ci) * gamma for ci in c)


def film_tint(warmth=WARMTH):
    """The block-light tint the set is baked with: #FFD88C pulled toward white (warmth 1 = the game's own)."""
    return tuple(255.0 - warmth * (255.0 - t) for t in BLOCK_LIGHT_TINT)


def _srgb_to_lin(c):
    c = max(0.0, float(c))
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def face_light(block, sky, warmth=WARMTH, emit=EMIT):
    """(D, E) for a face that looks into a cell with these levels: D = the grey factor (0..1, sRGB) baked into the
    texture (it dims whatever scene light reaches the face), E = (r, g, b) 0..1 sRGB the face shows by itself
    (the game's light drawn as emission, without the face's cardinal shade). Underground (sky 0) E is the game's
    whole lightmap colour; where the sky reaches, the scene's sky lights the face and E is only what block light
    adds on top of it at the film's dusk."""
    block, sky = int(block), int(sky)
    tint = film_tint(warmth)
    D = max(lightmap_rgb(block, sky, 1.0, (1, 1, 1), tint))
    if sky <= 0:
        E = lightmap_rgb(block, 0, 1.0, (1, 1, 1), tint)
    else:
        with_block = lightmap_rgb(block, sky, DUSK_SKY_FACTOR, DUSK_SKY_COLOR, tint)
        sky_only = lightmap_rgb(0, sky, DUSK_SKY_FACTOR, DUSK_SKY_COLOR, tint)
        floor = lightmap_rgb(0, 0)
        base = sky_only if sky >= 15 else tuple(s - f for s, f in zip(sky_only, floor))
        E = tuple(max(0.0, a - b) for a, b in zip(with_block, base))
        if block <= 0 and sky >= 15:
            E = (0.0, 0.0, 0.0)
    return D, tuple(emit * e for e in E)


def _dilate(m):
    out = np.zeros_like(m)
    out[1:] |= m[:-1]
    out[:-1] |= m[1:]
    out[:, 1:] |= m[:, :-1]
    out[:, :-1] |= m[:, 1:]
    out[:, :, 1:] |= m[:, :, :-1]
    out[:, :, :-1] |= m[:, :, 1:]
    return out


def flood(opaque, sources):
    """The game's light flood fill on a grid: sources (level array, 0 = none) spread minus one per step into every
    cell that is not opaque (BlockLightEngine / SkyLightEngine propagateIncrease). Returns the level array."""
    level = sources.astype(np.int16).copy()
    clear = ~opaque
    for lv in range(14, 0, -1):
        src = level == lv + 1
        if not src.any():
            continue
        grow = _dilate(src) & clear & (level < lv)
        level[grow] = lv
    return level


class BlockLight(sets.Environment):
    """engine.sets' Environment (biome colours, baked SKY light) with the game's BLOCK light as well, for the cells
    of one set piece (`owned`): every block face there is drawn with the lightmap of the cell it looks into, as the
    game draws it with Smooth Lighting off. The grey brightness D is baked into the texture (it dims the scene's
    own light: sky fill, bounce lamps, the torches' point lights), the colour E of the game's light is added as
    emission (see face_light). Faces of cells outside `owned` are left to engine.sets (unchanged village).
    One per World: underground.env(b)."""

    def __init__(self, world):
        super().__init__(world)
        self.sky = {}               # cell -> sky light 0..15 (absent: 15), for owned cells
        self.block = {}             # cell -> block light 0..15 (absent: 0)
        self.solid = set()          # cells opaque for light when the bake ran (absent from the World later or not)
        self.owned = set()          # cells whose faces are relit
        self.keep = {}              # cell -> (block, sky) forced for faces that look INTO that cell (door cells)
        self.warmth = WARMTH
        self.emit = EMIT
        self.registry = {}          # material key -> emission multiplier (r, g, b) linear, relative to the texture
        self._used = {}             # material key -> its (D, E) signature
        self._relit_cache = {}
        self._normals = {}
        self.cut, self.block_cut = set(), {}

    # ---- the bake
    def bake(self, box, emitters, owned, opaque_extra=(), cut=()):
        """Compute sky and block light in the box (x0, y0, z0, x1, y1, z1) of cells: `emitters` {cell: level},
        `owned` the cells whose faces will be relit, `opaque_extra` cells that count as opaque although nothing is
        in the World there (the piston door, closed). Returns (cells with block light, cells darker than sky 15)."""
        w = self.w
        x0, y0, z0, x1, y1, z1 = box
        nx, ny, nz = x1 - x0 + 1, y1 - y0 + 1, z1 - z0 + 1
        opaque = np.zeros((nx, ny, nz), dtype=bool)
        extra = set(opaque_extra)
        for (x, y, z), sid in w.blocks.items():
            if x0 <= x <= x1 and y0 <= y <= y1 and z0 <= z <= z1 and (
                    w.is_full_cube(x, y, z) or w._states[sid][0] in OCCLUDING):
                opaque[x - x0, y - y0, z - z0] = True
        for (x, y, z) in extra:
            if x0 <= x <= x1 and y0 <= y <= y1 and z0 <= z <= z1:
                opaque[x - x0, y - y0, z - z0] = True
        # sky: open where nothing opaque is above, up to the highest block of the column in the whole World
        tops = {}
        for (x, y, z) in w.blocks:
            if x0 <= x <= x1 and y0 <= y <= y1 and z > z1 and w.is_full_cube(x, y, z):
                tops[(x, y)] = max(tops.get((x, y), -999), z)
        blocked = np.logical_or.accumulate(opaque[:, :, ::-1], axis=2)[:, :, ::-1]
        for (x, y), _z in tops.items():
            blocked[x - x0, y - y0, :] = True
        sky_src = np.where(~blocked & ~opaque, 15, 0)
        sky = flood(opaque, sky_src)
        src = np.zeros((nx, ny, nz), dtype=np.int16)
        for (x, y, z), lv in emitters.items():
            src[x - x0, y - y0, z - z0] = max(int(lv), src[x - x0, y - y0, z - z0])
        blk = flood(opaque, src)
        # the same block light with the cutaway cells taken out: what a face that only a cutaway reveals shows
        self.block_cut = {}
        self.cut = set(cut)
        if self.cut:
            op2 = opaque.copy()
            for (x, y, z) in self.cut:
                if x0 <= x <= x1 and y0 <= y <= y1 and z0 <= z <= z1:
                    op2[x - x0, y - y0, z - z0] = False
            blk2 = flood(op2, src)
            for (x, y, z) in self.cut:
                if x0 <= x <= x1 and y0 <= y <= y1 and z0 <= z <= z1:
                    lv = int(blk2[x - x0, y - y0, z - z0])
                    if lv > 0:
                        self.block_cut[(x, y, z)] = lv
        self.sky.clear()
        self.block.clear()
        self.solid = set()
        for i, j, k in np.argwhere(opaque):
            self.solid.add((int(i) + x0, int(j) + y0, int(k) + z0))
        for i, j, k in np.argwhere(~opaque & (sky < 15)):
            self.sky[(int(i) + x0, int(j) + y0, int(k) + z0)] = int(sky[i, j, k])
        for i, j, k in np.argwhere(~opaque & (blk > 0)):
            self.block[(int(i) + x0, int(j) + y0, int(k) + z0)] = int(blk[i, j, k])
        self.box = box
        self.owned = set(owned)
        for c in self.owned:
            self.columns.add((c[0], c[1]))
        self._cache.clear()
        self._relit_cache.clear()
        return len(self.block), len(self.sky)

    def levels(self, cell):
        """(block, sky) of a cell; an opaque cell answers with its brightest open neighbour (a face that looks into
        it is only seen when a cutaway removes it)."""
        cell = tuple(cell)
        if cell in self.keep:
            return self.keep[cell]
        if cell in self.cut:                               # only seen when the cutaway is see-through / removed
            return self.block_cut.get(cell, 0), 0
        if cell not in self.solid:
            return self.block.get(cell, 0), self.sky.get(cell, 15)
        best = None
        for _d, o in self._offsets:
            n = (cell[0] + o[0], cell[1] + o[1], cell[2] + o[2])
            if n in self.solid:
                continue
            lv = (self.block.get(n, 0), self.sky.get(n, 15))
            if best is None or _rank(lv) > _rank(best):
                best = lv
        return best if best is not None else (0, 0)

    def level_at(self, x, y, z):
        """Sky light 0..15 at a point (as engine.sets: 15 = open sky)."""
        c = (int(math.floor(x)), int(math.floor(y)), int(math.floor(z)))
        return self.sky.get(c, 15) if c not in self.solid else 0

    def block_at(self, x, y, z):
        """Block light 0..15 at a point."""
        return self.block.get((int(math.floor(x)), int(math.floor(y)), int(math.floor(z))), 0)

    def brightness_at(self, point):
        """The game's brightness (max channel of the lightmap, 0..1) at a point, at the film's dusk."""
        c = (int(math.floor(point[0])), int(math.floor(point[1])), int(math.floor(point[2])))
        b, s = self.levels(c)
        return max(lightmap_rgb(b, s, DUSK_SKY_FACTOR, DUSK_SKY_COLOR))

    # ---- what World.build gets
    def state_at(self, pos):
        return self.relit(self._inner, pos)

    def relit(self, inner, pos):
        """The state World.build draws at pos: relit with the baked light for owned cells."""
        if pos not in self.owned:
            return sets.Environment.state_at(self, pos) if inner is self._inner else inner(pos)
        st = inner(pos)
        if st is None:
            return None
        if any(q[2][0] in _blocks.EMISSIVE for q in st.quads):
            return st                                      # torches and lanterns glow by themselves
        own = self.levels(pos) if pos not in self.solid else None
        sig = []
        for pts, uvs, key, cull, off, mask in st.quads:
            if cull is not None:
                n = (pos[0] + off[0], pos[1] + off[1], pos[2] + off[2])
                lv = self.levels(n)
                d = cull
            else:
                lv = own if own is not None else self.levels(pos)
                d = self._normal_dir(pts)
            sig.append((lv, d))
        sig = tuple(sig)
        ck = (id(st), sig)
        hit = self._relit_cache.get(ck)
        if hit is None:
            hit = self._relit_cache[ck] = self._relight(st, sig)
        return hit

    def _normal_dir(self, pts):
        key = tuple(tuple(round(c, 4) for c in p) for p in pts[:3])
        d = self._normals.get(key)
        if d is None:
            a, b, c = (Vector(p) for p in pts[:3])
            n = (b - a).cross(c - a)
            if n.length < 1e-9:
                d = "up"
            else:
                n.normalize()
                ax = max(range(3), key=lambda i: abs(n[i]))
                d = (("west", "east"), ("south", "north"), ("down", "up"))[ax][1 if n[ax] > 0 else 0]
            self._normals[key] = d
        return d

    def _relight(self, st, sig):
        out = sets._LitState()
        out.cover, out.block_id = st.cover, st.block_id
        out.quads = []
        for (pts, uvs, key, cull, off, mask), (lv, d) in zip(st.quads, sig):
            tex, tint, ov, ov_tint, shade = key
            b, s = lv
            if b <= 0 and s >= 15:
                out.quads.append((pts, uvs, key, cull, off, mask))
                continue
            D, E = face_light(b, s, self.warmth, self.emit)
            if shade is not None:                          # cut-out plants (two-sided material): dimmed only
                E = (0.0, 0.0, 0.0)
            cs = CARDINAL.get(d, 0.8)
            E = tuple(e * cs for e in E)
            base = tint if tint is not None else (255, 255, 255)
            t2 = tuple(int(round(c * D)) for c in base)
            ov2 = None if ov_tint is None else tuple(int(round(c * D)) for c in ov_tint)
            if ov is not None and ov2 is None:
                ov2 = tuple(int(round(255 * D)) for _ in range(3))
            Dl = max(_srgb_to_lin(D), 1e-4)
            er = tuple(round(_srgb_to_lin(e) / Dl, 4) for e in E)
            if max(er) < 1e-3 and D >= 0.999:
                out.quads.append((pts, uvs, key, cull, off, mask))
                continue
            sig_de = (round(D, 4), er)
            k2 = self._unique((tex, t2, ov, ov2, shade), sig_de, base, key)
            if max(er) >= 1e-3:
                self.registry[k2] = er
            out.quads.append((pts, uvs, k2, cull, off, mask))
        return out

    def _unique(self, key, sig_de, base, orig):
        """A material key of our own for this (D, E): never the plain village key, never another face's."""
        tex, t2, ov, ov2, shade = key
        k = 0
        while True:
            cand = (tex, t2, ov, ov2, shade)
            if cand != tuple(orig) and t2 != tuple(base):
                got = self._used.get(cand)
                if got is None:
                    self._used[cand] = sig_de
                    return cand
                if got == sig_de:
                    return cand
            k += 1
            ch_ = k % 3
            step = (k + 2) // 3
            t2 = tuple(max(0, min(255, c + (-step if i == ch_ else 0))) for i, c in enumerate(key[1]))


def _rank(lv):
    b, s = lv
    return max(lightmap_rgb(b, s, DUSK_SKY_FACTOR, DUSK_SKY_COLOR))


def env(b):
    """The BlockLight environment of the builder's World (made on first use; an engine.sets Environment made
    earlier is turned into one, keeping what it baked)."""
    e = getattr(b.w, "sets_environment", None)
    if isinstance(e, BlockLight):
        return e
    if e is None:
        e = b.w.sets_environment = BlockLight(b.w)
        return e
    e.__class__ = BlockLight                                       # keep its sky bake and biome columns
    for name, val in (("sky", {}), ("block", {}), ("solid", set()), ("owned", set()), ("keep", {}),
                      ("warmth", WARMTH), ("emit", EMIT), ("registry", {}), ("_used", {}), ("_relit_cache", {}),
                      ("_normals", {}), ("cut", set()), ("block_cut", {})):
        setattr(e, name, val)
    return e


# =====================================================================================================================
# the set, built into the village through build_village(edit=hook)
# =====================================================================================================================

def _cells_of(x0, y0, z0, x1, y1, z1):
    return [(x, y, z) for x in range(x0, x1 + 1) for y in range(y0, y1 + 1) for z in range(z0, z1 + 1)]


def door_cells():
    """The cells the piston door needs empty in the World: door blocks, piston heads, piston bases."""
    from . import redstone

    return redstone.door_cells(DOOR, DOOR_SIDE)


def layout():
    """{cell: (block_id, props) | None (air)} of everything this set puts under the square (the ROCK box) and the
    cells left empty for the piston door. Pure data: no World, no Blender."""
    x0, y0, z0, x1, y1, z1 = ROCK
    L = {}
    for c in _cells_of(x0, y0, z0, x1, y1, z1):
        L[c] = _rock(*c)

    def air(x, y, z):
        L[(x, y, z)] = None

    def put(x, y, z, bid, props=None):
        L[(x, y, z)] = (bid, props)

    # the stairwell: two wide, ten stone stairs down to the south, three blocks of headroom over every step
    for k in range(STEPS):
        y = -k
        for x in MOUTH_X:
            if -1 - k >= z0:
                put(x, y, -1 - k, "stone_stairs", dict(STAIR))
            for z in range(-k, -k + HEADROOM):
                if z0 <= z <= z1:
                    air(x, y, z)
    for x in MOUTH_X:                                        # the landing at the foot
        for z in range(F, F + 3):
            air(x, LANDING_Y, z)
        put(x, LANDING_Y, F - 1, "deepslate_bricks")
    # the aisle (east-west), its unlit west stretch, and the leg south to the back corner
    for x in range(AISLE_X[0], AISLE_X[1] + 1):
        for y in range(AISLE_Y[0], AISLE_Y[1] + 1):
            for z in range(F, F + 3):
                air(x, y, z)
            put(x, y, F - 1, "deepslate_bricks")
    for x in range(LEG_X[0], LEG_X[1] + 1):
        for y in range(LEG_Y[0], LEG_Y[1] + 1):
            for z in range(F, F + 3):
                air(x, y, z)
            put(x, y, F - 1, "deepslate_bricks")
    # the cell block, in stone (the piston door's blocks are stone): floor, front row, cells, back wall, box
    for x in range(6, END_X + 1):
        for y in range(BOX_Y - 1, FRONT_Y + 1):
            put(x, y, F - 1, "stone")
    jobs = {x: n for n, x in CELL_X.items()}
    for x in range(6, END_X + 1):
        # front row (job blocks, windows over them, a row of bars at the top)
        if x in jobs:
            bid, p = JOB[jobs[x]]
            put(x, FRONT_Y, F, bid, dict(p))
            air(x, FRONT_Y, F + 1)
            put(x, FRONT_Y, F + 2, "iron_bars", dict(BARS_EW))
        elif x in (8, 10) + WINDOW_PIER:
            put(x, FRONT_Y, F, "stone")                      # the counter runs on: a window at face height over
            air(x, FRONT_Y, F + 1)                           # every pier from the farmer to dad, so the four faces
            put(x, FRONT_Y, F + 2, "iron_bars", dict(BARS_EW))   # are seen from either end of the aisle
        else:
            for z in range(F, F + 3):
                put(x, FRONT_Y, z, "stone")
        # cell row: one-block cells two high under a stone cap (CELL_HEADROOM; the caps over the job cells are the
        # cutaway "ug_caps"), iron bars between the first three, a solid pier before dad's
        for z in range(F, F + 3):
            if z >= F + CELL_HEADROOM:
                put(x, CELL_Y, z, "stone")
            elif x in jobs:
                air(x, CELL_Y, z)
            elif x in (8, 10):
                put(x, CELL_Y, z, "iron_bars", dict(BARS_NS))
            else:
                put(x, CELL_Y, z, "stone")
        # back wall
        for z in range(F, F + 3):
            put(x, BACK_Y, z, "stone")
    for c in door_cells():
        air(*c)
    # the zombie box behind dad's cell: 1 x 1 x 2 inside, a smooth stone lid, the slot of bars in its east wall
    bx, by = BOX
    for z in (F, F + 1):
        air(bx, by, z)
        put(bx - 1, by, z, "stone")
        put(bx, by - 1, z, "stone")
        put(bx + 1, by - 1, z, "stone")
        put(bx - 1, by - 1, z, "stone")
    put(bx, by, F + 2, "smooth_stone")
    put(*SLOT, "iron_bars", dict(BARS_NS))
    put(SLOT[0], SLOT[1], F + 1, "stone")
    put(SLOT[0], SLOT[1], F + 2, "stone")
    air(*LEVER)                                              # (the aisle is air there anyway: the lever's cell)
    _line_stairwell(L)
    _connect_bars(L)
    return L


def _line_stairwell(L):
    """The stairwell's walls and ceiling lined in stone where the earth is dirt (the story: "stone turning to
    deepslate"): every rock cell that touches the stairwell's air is stone down to z -6, mixed at -7, deepslate
    below (as _rock), never dirt (the grass rim at z -1 is the village's ground and stays)."""
    open_ = [c for c, s in L.items() if s is None and MOUTH_X[0] <= c[0] <= MOUTH_X[1] and LANDING_Y <= c[1] <= 0]
    for (x, y, z) in open_:
        for dx, dy, dz in ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1)):
            n = (x + dx, y + dy, z + dz)
            s = L.get(n)
            if s is not None and s[0] == "dirt":
                L[n] = ("stone", None)


def _connect_bars(L):
    """Every iron bars block of the layout connected as the game connects it (IronBarsBlock.attachsTo): to bars on
    that side, or to a block whose face there is sturdy (BARS_STURDY); not to air, a lectern or a brewing stand."""
    dirs = {"north": (0, 1), "south": (0, -1), "east": (1, 0), "west": (-1, 0)}
    for (x, y, z), s in list(L.items()):
        if s is None or s[0] != "iron_bars":
            continue
        props = {"waterlogged": "false"}
        for name, (dx, dy) in dirs.items():
            n = L.get((x + dx, y + dy, z))
            props[name] = "true" if n is not None and (n[0] == "iron_bars" or n[0] in BARS_STURDY) else "false"
        L[(x, y, z)] = ("iron_bars", props)


def _hole():
    """The stair's opening in the square: the ground blocks taken out (steps 0..3 have open sky above)."""
    out = []
    for k in range(STEPS):
        if -k + HEADROOM - 1 >= -1:                          # the step's headroom reaches the ground layer
            for x in MOUTH_X:
                out.append((x, -k))
    return out


CUTAWAYS = {
    # name: cells (solid ones only are kept); see_through for the camera, remove for the light too
    "ug_ceiling": lambda: _cells_of(AISLE_X[0] - 1, BOX_Y - 1, F + 3, LEG_X[1] + 1, LANDING_Y, ROCK[5]),
    "ug_end_wall": lambda: _cells_of(END_X, BACK_Y, F, END_X, CELL_Y, F + 2),
    "ug_end_pier": lambda: _cells_of(END_X, FRONT_Y, F, END_X, FRONT_Y, F + 2),       # (holds the lever)
    "ug_box_side": lambda: [(SLOT[0], SLOT[1], F + 1), (SLOT[0], SLOT[1], F + 2)],
    "ug_slot": lambda: [SLOT],
    "ug_caps": lambda: [(x, CELL_Y, F + CELL_HEADROOM) for x in sorted(CELL_X.values())],   # beat 7
}
# The cells whose faces look into the doorway and into the box: meshed twice by finish(), once dark (the box's
# darkness, DOOR_KEEPS_DARK / BOX_SEALED: every aisle-side shot) and once lit as the game re-lights them when the
# wall is open (ug.light_doorway / open_wall(relight=...): beat 24 only), so the open doorway's floor and ceiling
# are not black under the warm light that falls on the baby
DOORWAY_FLOOR = (DOOR[0][0], DOOR[0][1], F - 1)
DOORWAY_TOP = (DOOR[0][0], DOOR[0][1], F + 2)
BOX_SHELL = [(BOX[0], BOX[1], F - 1), (BOX[0], BOX[1], F + 2), (BOX[0] - 1, BOX[1], F), (BOX[0] - 1, BOX[1], F + 1),
             (BOX[0], BOX[1] - 1, F), (BOX[0], BOX[1] - 1, F + 1)]
RELIT_CELLS = [DOORWAY_FLOOR, DOORWAY_TOP] + BOX_SHELL


def underground_set(b, name="underground", bed=BED, bed_color="red", rim=True):
    """IN THE HOOK (build_village(edit=...)): the stair mouth beside the well, the stairwell, the hall, the cells,
    dad's cell with its piston wall, the zombie box, dad's red bed; the lights; the game's light baked into every
    face of it. Returns the set's dict (also Village.sets[name]); call finish(v) after build_village."""
    sets._new_name(b, name)
    w = b.w
    x0, y0, z0, x1, y1, z1 = ROCK
    # 1. the ground under the square must be empty where the set goes
    taken = [c for c in w.blocks if x0 <= c[0] <= x1 and y0 <= c[1] <= y1 and z0 <= c[2] <= z1]
    if taken:
        raise ValueError("underground_set: the earth under the square is not empty at %s (%s)"
                         % (taken[0], w.block_id(*taken[0])))
    L = layout()
    for c, st in L.items():
        if st is not None:
            w.set(c[0], c[1], c[2], st[0], st[1])
    # 2. the mouth: the ground layer opened over steps 0..3, step 0 in the ground layer itself, grass round the rim
    mx0, mx1 = MOUTH_X
    b.allow((mx0 - 3, -5, mx1 + 3, 3))                       # the well's template edge and the plaza's path
    hole = set(_hole())
    for (x, y) in hole:
        if y == 0:
            w.set(x, y, -1, "stone_stairs", dict(STAIR))
        else:
            w.set(x, y, -1, None)
        for z in range(0, 3):
            if w.block_id(x, y, z) is not None:
                w.set(x, y, z, None)
    rim_cells = []
    if rim:
        for x in range(mx0 - 1, mx1 + 2):
            for y in range(-4, 2):
                if (x, y) in hole:
                    continue
                bid = w.block_id(x, y, -1)
                if bid in ("dirt_path", "grass_block"):
                    w.set(x, y, -1, "grass_block", {"snowy": "false"})
                    b.path_cells.discard((x, y))
                    rim_cells.append((x, y))
                b.clear_plants(x, y)
    for x in range(mx0 - 3, mx1 + 4):
        for y in range(-6, 4):
            b.reserved.add((x, y))
    b.show_undersides(mx0, LANDING_Y, mx1, 0)               # the ground's underside is the stairwell's ceiling
    # 3. lights (each its own point light, groups ug_*)
    for cell, bid, props, group in LIGHTS:
        b.torch(cell, bid, dict(props), group=group)
    # 4. dad's bed, red
    if bed is not None and bed_color:
        info = b.v.beds.get(bed)
        if info is None:
            raise KeyError("underground_set: the village has no bed %r" % bed)
        house = bed.rsplit("_bed_", 1)[0]
        b.allow(house)
        for part in ("foot", "head"):
            c = tuple(int(math.floor(v)) for v in info[part])
            c = (c[0], c[1], int(math.floor(info[part][2] - 0.5)))
            st = w.get(*c)
            if st is None or not st[0].endswith("_bed"):
                raise ValueError("underground_set: no bed block at %s" % (c,))
            w.set(c[0], c[1], c[2], bed_color + "_bed", dict(st[1]))
    # 5. the game's light, baked (the piston door counts as shut; the cutaways are still in the World)
    e = env(b)
    owned = set(c for c in L)
    for x in range(mx0 - 2, mx1 + 3):
        for y in range(LANDING_Y - 1, 3):
            owned.add((x, y, -1))
    for x, y in hole:
        owned.add((x, y, -1))
    emitters = {cell: LIGHT_EMISSION[bid] for cell, bid, _p, _g in LIGHTS}
    extra = list(door_cells()) + ([SLOT] if BOX_SEALED else [])
    cut_cells = [c for cells in CUTAWAYS.values() for c in cells() if c in w.blocks]
    nb, ns = e.bake((x0, y0, z0, x1, y1, 4), emitters, owned, opaque_extra=extra, cut=cut_cells)
    box_light = e.levels((BOX[0], BOX[1], F))
    if DOOR_KEEPS_DARK:
        for c in DOOR:
            e.keep[c] = box_light
    # 6. cutaways: kept out of the village mesh, meshed on their own by finish()
    cut = {}
    for cname, cells in CUTAWAYS.items():
        got = {}
        for c in cells():
            sid = w.blocks.get(c)
            if sid is not None:
                got[c] = sid
        cut[cname] = got
    for got in cut.values():
        for c in got:
            del w.blocks[c]
    # ... and the doorway's / the box's own faces, meshed twice (dark and lit) by finish()
    relit = {}
    for c in RELIT_CELLS:
        sid = w.blocks.pop(c, None)
        if sid is not None:
            relit[c] = sid
    # the levels of the door cells and the box once the wall is open (the game's flood fill with the door cells
    # clear; the slot still sealed when BOX_SEALED): what the lit copy is baked with
    open_keep = _open_levels(e)
    # 7. anchors, paths, cameras
    res = _register(b, name)
    res.update(cut=cut, rim=rim_cells, hole=sorted(hole), counts=dict(blocks=sum(1 for s in L.values() if s),
                                                                         lit_cells=nb, dark_cells=ns),
               box_light=box_light, env=e, relit=relit, open_keep=open_keep)
    b.v.sets[name] = res
    return res


def _open_levels(e):
    """{cell: (block, 0)} of the door cells and the box with the wall open: the bake's block light flooded on
    through the open door cells (minus one per step, BlockLightEngine), the slot still sealed when BOX_SEALED."""
    inside = [tuple(c) for c in DOOR] + [(BOX[0], BOX[1], F), (BOX[0], BOX[1], F + 1)]
    lv = {c: 0 for c in inside}
    for _ in range(6):
        for c in inside:
            best = 0
            for _d, o in e._offsets:
                n = (c[0] + o[0], c[1] + o[1], c[2] + o[2])
                if n in lv:
                    best = max(best, lv[n])
                elif n not in e.solid:
                    best = max(best, e.block.get(n, 0))
            lv[c] = max(lv[c], best - 1)
    return {c: (v, 0) for c, v in lv.items()}


def _register(b, name):
    """Anchors (standing spots on the walking surface; *_target / *_cam are look targets / camera spots), paths."""
    v = b.v
    A = {}

    def anchor(key, pos, yaw=None):
        A[key] = tuple(float(c) for c in pos)
        v.anchors[key] = A[key]
        if yaw is not None:
            v.yaws[key] = float(yaw)

    mx = (MOUTH_X[0] + MOUTH_X[1] + 1) / 2.0                 # the middle of the stair's width (x 5.0)

    def gz(x, y):
        z = b.walk_z(x, y)
        return 0.0 if z is None else float(z)
    anchor("ug_lip", (mx - 0.15, 1.42, gz(mx - 0.15, 1.42)), yaw_of("south"))                  # the baby at the lip (beat 2)
    anchor("ug_lip_target", (mx, -1.5, -1.2))                                  # ... staring down into it
    anchor("ug_mouth_target", (mx, -1.0, 0.2))                                 # the glowing hole
    anchor("ug_push_start", (mx, 3.4, gz(mx, 3.4)), yaw_of("south"))                   # dad, before the push (beat 3)
    anchor("ug_push_player", (mx, 4.3, gz(mx, 4.3)), yaw_of("south"))
    anchor("ug_stair_top", (mx, 0.75, 0.0), yaw_of("south"))
    anchor("ug_stair_foot", (mx, LANDING_Y + 0.45, float(F)), yaw_of("south"))  # where the steps meet the hall
    for n, x in CELL_X.items():
        off = DAD_OFFSET if n == "dad" else 0.0
        anchor("ug_cell_%s" % n, (x + 0.5 + off, FRONT_Y - 0.30, float(F)), yaw_of("north"))
        anchor("ug_cell_%s_station" % n, (x + 0.5, FRONT_Y + 0.5, F + 0.5))
        anchor("ug_aisle_%s" % n, (x + 0.5, AISLE_Y[0] + 0.85, float(F)), yaw_of("south"))   # in front of the cell
    # dad in the middle of his cell: for the beats where he turns his head west (17-19); at ug_cell_dad (DAD_OFFSET,
    # for the strip of black doorway beside his robe) a head turned to its stop puts his nose into the pier
    anchor("ug_cell_dad_mid", (CELL_X["dad"] + 0.5, FRONT_Y - 0.30, float(F)), yaw_of("north"))
    anchor("ug_lever_target", (LEVER[0] + 0.5, LEVER[1] + 0.3, LEVER[2] + 0.45))
    # Steve flips the lever standing a block north of it, facing south (beat 9: out of the b09 frame, which looks
    # past his right side; only his right arm swings in from the left edge across the lever)
    anchor("ug_lever_stand", (LEVER[0] + 0.55, LEVER[1] + 1.05, float(F)), yaw_of("south"))
    anchor("ug_counter_steve", (15.0, AISLE_Y[0] + 0.3, float(F)), yaw_to((15.0, -11.7), (14.32, -13.3)))  # beat 13
    anchor("ug_door_target", (DOOR[0][0] + 0.5, DOOR[0][1] + 0.5, F + 1.0))
    anchor("ug_box", (BOX[0] + 0.5, BOX[1] + 0.5, float(F)), yaw_of("north"))    # inside the box, facing the door
    anchor("ug_slot_target", (SLOT[0] + 0.5, SLOT[1] + 0.5, F + 0.5))
    anchor("ug_slot_hands", (SLOT[0] + 0.19, SLOT[1] + 0.5, float(F)), yaw_of("east"))   # see hands_in_slot()
    anchor("ug_corner", (LEG_X[1] + 0.35, LEG_Y[0] + 0.45, float(F)), yaw_of("west"))   # the back corner
    anchor("ug_leg_north", (LEG_X[0] + 0.55, AISLE_Y[0] + 0.6, float(F)), yaw_of("south"))
    anchor("ug_aisle_west_end", (AISLE_X[0] + 0.6, AISLE_Y[0] + 1.0, float(F)), yaw_of("east"))
    anchor("ug_aisle_center", (10.5, AISLE_Y[0] + 1.0, float(F)))
    # beat 18: Steve walks away from dad up the aisle (under the b18 camera's line to dad: no occlusion)
    anchor("ug_follow_start", (14.5, AISLE_Y[0] + 0.6, float(F)), yaw_of("west"))
    anchor("ug_follow_end", (7.2, AISLE_Y[0] + 0.6, float(F)), yaw_of("west"))
    anchor("ug_jump_spot", (12.3, AISLE_Y[0] + 0.65, float(F)), yaw_to((0, 0), (1, 1)))   # Steve's jump
    #                                         loop (beat 16): mid-aisle in front of the cleric, facing north-east
    # paths (with their own heights: stairs)
    down = [(mx, 4.0, gz(mx, 4.0)), (mx, 1.0, gz(mx, 1.0))]
    for k in range(STEPS):
        down.append((mx, -k + 0.25, -k * 1.0))
        down.append((mx, -k - 0.25, -k - 0.5))
    down += [(mx, LANDING_Y + 0.5, float(F)), (mx, AISLE_Y[1] + 0.5, float(F))]
    v.paths["ug_down"] = _dedupe(down)                       # from the square down the stairs into the aisle
    v.paths["ug_aisle"] = [(mx, AISLE_Y[1] + 0.5, float(F)), (mx + 0.4, AISLE_Y[0] + 0.9, float(F)),
                           (14.5, AISLE_Y[0] + 0.9, float(F))]                 # stair foot to dad's cell
    v.paths["ug_leg"] = [(13.5, AISLE_Y[0] + 0.6, float(F)), (LEG_X[0] + 0.6, AISLE_Y[0] + 0.6, float(F)),
                         (LEG_X[0] + 0.6, LEG_Y[0] + 0.5, float(F))]          # past the end pier to the slot
    v.paths["ug_push"] = [(mx, 3.4, gz(mx, 3.4)), (mx, 1.0, gz(mx, 1.0))]
    # two children chasing round the well (beat 20): from its west side round its north side (hidden from the
    # b20_well camera behind the well's stone) to the glowing mouth
    v.paths["ug_round_well"] = [(x, y, gz(x, y)) for x, y in ((-5.4, -4.6), (-5.6, 3.9), (0.0, 4.4), (3.3, 3.5),
                                                              (3.5, 1.9))]                      # dad pushed to the lip (push())
    return dict(anchors=A, paths=["ug_down", "ug_aisle", "ug_leg", "ug_push", "ug_round_well"])


def _dedupe(pts):
    out = []
    for p in pts:
        if not out or math.dist(out[-1], p) > 1e-6:
            out.append(tuple(float(c) for c in p))
    return out


# =====================================================================================================================
# after build_village: cutaways, emission materials, the redstone parts
# =====================================================================================================================

def _emissive(base, er):
    """A copy of a block material whose texels also EMIT texel x er (linear multiplier): the baked light."""
    import hashlib

    key = "|ug%.4f,%.4f,%.4f" % tuple(er)
    name = base.name + key
    if len(name) > 63:
        name = base.name[:40] + "|ug" + hashlib.md5((base.name + key).encode()).hexdigest()[:14]
    mat = bpy.data.materials.get(name)
    if mat is not None:
        return mat
    mat = base.copy()
    mat.name = name
    nt = mat.node_tree
    tex = next(n for n in nt.nodes if n.type == "TEX_IMAGE")
    bsdf = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
    for link in list(nt.links):
        if link.to_node is bsdf and link.to_socket.name in ("Emission Color", "Emission Strength"):
            nt.links.remove(link)
    vm = nt.nodes.new("ShaderNodeVectorMath")
    vm.operation = "MULTIPLY"
    vm.location = (-250, -320)
    nt.links.new(tex.outputs["Color"], vm.inputs[0])
    vm.inputs[1].default_value = tuple(float(c) for c in er)
    nt.links.new(vm.outputs[0], bsdf.inputs["Emission Color"])
    bsdf.inputs["Emission Strength"].default_value = 1.0
    try:
        mat.cycles.emission_sampling = "NONE"        # seen and bounced, not sampled as a light: the torches light
    except (AttributeError, TypeError):
        pass
    mat["ug_emission"] = list(er)
    return mat


def _material_for(e, tex, tint, b, s, direction, shade=None):
    """The (tinted, emissive) block material a face with these light levels gets, as World.build would draw it."""
    D, E = face_light(b, s, e.warmth, e.emit)
    cs = CARDINAL.get(direction, 0.8)
    base = tint if tint is not None else (255, 255, 255)
    t2 = tuple(int(round(c * D)) for c in base)
    Dl = max(_srgb_to_lin(D), 1e-4)
    er = tuple(round(_srgb_to_lin(x * cs) / Dl, 4) for x in E)
    mat = _blocks.block_material(tex, None if t2 == (255, 255, 255) else t2, None, None, shade)
    return _emissive(mat, er) if max(er) >= 1e-3 else mat


def _dir_of(normal):
    ax = max(range(3), key=lambda i: abs(normal[i]))
    return (("west", "east"), ("south", "north"), ("down", "up"))[ax][1 if normal[ax] > 0 else 0]


def relight_object(ob, e, cell=None, levels=None):
    """Give a separate object (a redstone part, a prop) the baked light of the set: every face its texture's
    material tinted and emitting as a World face looking into `cell` would (levels(direction) -> (block, sky)
    picks per face direction instead). The mesh is copied first."""
    if ob.type != "MESH" or not ob.data.materials:
        return ob
    me = ob.data = ob.data.copy()
    rot = ob.matrix_world.to_3x3()
    cache = {}
    new_slots = []
    for poly in me.polygons:
        mat = me.materials[poly.material_index]
        tex = mat.get("mc_texture") if mat is not None else None
        if not tex or tex in _blocks.EMISSIVE:
            continue
        n = rot @ poly.normal
        d = _dir_of(n)
        lv = levels(d) if levels is not None else e.levels(cell)
        key = (mat.name, d, lv)
        m2 = cache.get(key)
        if m2 is None:
            m2 = cache[key] = _material_for(e, tex, None, lv[0], lv[1], d, mat.get("mc_shade"))
        if m2.name not in [m.name for m in me.materials]:
            me.materials.append(m2)
            new_slots.append(m2)
        poly.material_index = [m.name for m in me.materials].index(m2.name)
    return ob


class UndergroundSet:
    """What finish(v) returns: the built set with its parts. See the module docstring (PUBLIC API)."""

    def __init__(self, v, res, kit, door, lever):
        self.v, self.res, self.kit, self.door, self.lever = v, res, kit, door, lever
        self.env = res["env"]
        self.anchors = res["anchors"]
        self.cameras = cameras()
        self.cutaways = list(CUTAWAYS)
        self.parts = [door, lever]

    # ---- the wall
    def open_wall(self, frame, player=None, reach=True, look=True, relight=None, repeater=0, sync="game"):
        """The lever is flipped on `frame` (by `player` if given: his swing starts on frame) and dad's back wall
        opens: the hidden inverter (a redstone torch behind the pier, 2 ticks) un-powers the sticky pistons,
        which pull the two stone blocks west into the wall in 2 ticks. repeater=1..4: a hidden repeater at that
        delay before the torch (RepeaterBlock: 2 ticks per step; 4 = 8 ticks more: the wall moves 12 frames after
        the click, time for beat 9's pan and focus pull). sync="hand": the lever moves on the frame his hand is
        nearest its handle (redstone.flip_by; a film choice for the close-up, beat 9) instead of the tick after the
        click. relight=(st, shot): in that shot the doorway's floor and ceiling and the box's inside are lit as the
        game re-lights them from the frame the wall starts to move (light_doorway; beat 24, seen from the box).
        Returns dict(flip, open, open_end, hand) frames (hand: his hand nearest the handle, with a player)."""
        from . import redstone

        if player is not None:
            t = redstone.flip_by(player, self.lever, frame, look=look, reach=reach, sync=sync)
        else:
            t = self.lever.flip(frame)
        t_open = redstone.at(t, redstone.TORCH_TOGGLE_TICKS + redstone.REPEATER_TICKS_PER_DELAY * int(repeater))
        end = self.door.open(t_open)
        r = dict(flip=redstone.frame_of(t), open=redstone.frame_of(t_open), open_end=redstone.frame_of(end),
                 hand=(self.lever.reach_info or {}).get("frame") if player is not None else None)
        if relight is not None:
            self.light_doorway(relight[0], relight[1], r["open"])
        return r

    def light_doorway(self, st, shot, frame):
        """In ONE shot, from `frame` (a frame inside it) to its end: the doorway's floor and ceiling and the box's
        inside drawn with the light the game gives them once the wall is open (the door cells at dad's cell minus
        one, the box one less), instead of the box's darkness (DOOR_KEEPS_DARK / BOX_SEALED), which every other
        frame keeps. Object visibility (hide_render keys, in the frame's stamp). Beat 24 from inside the box; never
        an aisle-side shot (the doorway must read black from the aisle)."""
        f = max(int(shot.frame_start), int(math.ceil(frame)))
        nxt = shot.frame_end + 1
        for ob in self.doorway["lit"]:
            st.key(ob, "hide_render", st.film.frame_start, True)
            st.key(ob, "hide_render", f, False)
            st.key(ob, "hide_render", nxt, True)
        for ob in self.doorway["dark"]:
            st.key(ob, "hide_render", st.film.frame_start, False)
            st.key(ob, "hide_render", f, True)
            st.key(ob, "hide_render", nxt, False)
        return f

    def close_wall(self, frame, lever=True):
        """The pistons push the wall shut on `frame` (and the lever goes back first, 2 ticks earlier, if lever)."""
        from . import redstone

        if lever:
            self.lever.flip(int(math.floor(frame - redstone.TORCH_TOGGLE_TICKS * TICK)))
        end = self.door.close(frame)
        return redstone.frame_of(end)

    def brightness_at(self, point):
        """The game's brightness 0..1 at a point of the set (the lightmap of its block and sky light)."""
        return self.env.brightness_at(point)

    def register(self, st, door=False, lever=True):
        """Put the lever (and with door=True the piston door too) in st.cast: a registered part is hidden in every
        shot that does not st.use it, so then st.use(shot, ug.lever) (or *ug.parts) in every shot that sees the end
        pier's north face, and leave it out of a shot that sees through "ug_end_pier" (it would float). The door is
        left out by default: registered and forgotten in one hall shot, dad's back wall would open a hole into the
        box; unregistered it is simply always there (it only moves when opened)."""
        for p, want in ((self.door, door), (self.lever, lever)):
            if want:
                st.cast[p.name] = p


def finish(v, name="underground"):
    """AFTER build_village: mesh the cutaways (Village.cutaways: ug_ceiling, ug_end_wall, ug_box_side, ug_slot),
    give the baked faces their emission, build the piston door and the lever (engine.redstone) and light them
    like the wall they sit in. Returns an UndergroundSet."""
    from . import redstone

    res = v.sets[name]
    e = res["env"]
    w = v.world
    coll = v.collection
    relit = res.get("relit", {})
    full = dict(relit)

    def submesh(got, oname, keep=None):
        sub = _blocks.World()
        sub._states, sub._state_ids, sub._baked, sub._variants = w._states, w._state_ids, w._baked, w._variants
        sub.blocks = dict(got)
        hidden = set()
        for c in got:
            for d in mc.DIRS:
                o = mc.DIR_BLENDER[d]
                n = (c[0] + o[0], c[1] + o[1], c[2] + o[2])
                if (n in w.blocks and w.is_full_cube(*n)) or (n in full and n not in got):
                    hidden.add((c, d))
        sub.hidden_sides = hidden
        inner = sub._state_at
        saved = dict(e.keep)
        if keep:
            e.keep.update(keep)
        try:
            sub._state_at = (lambda pos, inner=inner: e.relit(inner, pos))
            objs = sub.build(coll, oname)
        finally:
            e.keep.clear()
            e.keep.update(saved)
        v.face_count += sub.last_face_count
        return objs

    for cname, got in res["cut"].items():
        v.cutaways[cname] = submesh(got, cname)
    # the doorway's floor and ceiling and the box's inside, dark (always) and lit (ug.light_doorway, beat 24)
    doorway = dict(dark=submesh(relit, "ug_doorway_dark") if relit else [],
                   lit=submesh(relit, "ug_doorway_lit", keep=res.get("open_keep")) if relit else [])
    for ob in doorway["lit"]:
        ob.hide_render = True                                # until light_doorway() keys it on in a shot
    for ob in doorway["dark"] + doorway["lit"]:
        v.objects.append(ob)
    swaps = {}
    for key, er in e.registry.items():
        base = _blocks.block_material(*key)
        swaps[base.name] = (base, er)
    obs = list(v.objects) + [o for n in CUTAWAYS for o in v.cutaways.get(n, [])]
    for ob in obs:
        if ob.type != "MESH":
            continue
        me = ob.data
        for i, m in enumerate(me.materials):
            if m is not None and m.name in swaps:
                me.materials[i] = _emissive(*swaps[m.name])
    k = redstone.kit(v)
    door = k.piston_door(DOOR, DOOR_SIDE, block="stone", closed=True, name="ug_door")
    lever = k.lever(LEVER, "wall", facing="north", powered=False, name="ug_lever")
    box = e.levels((BOX[0], BOX[1], F))
    for i, blk in enumerate(door.blocks):
        c = DOOR[i]

        def lv(d, c=c):
            if d == "south":
                return box
            o = mc.DIR_BLENDER[d]
            return e.levels((c[0] + o[0], c[1] + o[1], c[2] + o[2]))
        relight_object(blk.object, e, levels=lv)
    for ob in lever.objects:
        relight_object(ob, e, cell=LEVER)
    for g in LIGHT_GROUPS:
        for ob in v.lights.get(g, []):
            if ob.get("mc_light") != "fill":
                ob.data.color = POINT_COLOR
    _fill(v)
    ug = UndergroundSet(v, res, k, door, lever)
    ug.doorway = doorway
    res["set"] = ug
    return ug


def _fill(v):
    """The hall's weak, cool, shadowless fill near its ceiling, in light group ug_hall (on only for a shot whose
    Stage.lights says inside="ug_hall"; it passes through walls, so never for the box shots)."""
    from . import props

    if any(ob.get("mc_light") == "fill" for ob in v.lights.get("ug_hall", [])):
        return
    watts = sum(ob["base_energy"] for g in ("ug_hall", "ug_dad", "ug_foot", "ug_corner") for ob in v.lights.get(g, []))
    # two halves: one over the aisle in front of the cells, one in the leg east of dad's cell (shadowless: it
    # reaches his east side through the end wall, which beat 19 films)
    for i, pos in enumerate(((12.5, AISLE_Y[0] - 0.4, F + 2.6), (LEG_X[0] + 0.6, CELL_Y + 0.5, F + 2.4))):
        ob = props.make_light("fill", v.collection)
        ob.location = pos
        ob.data.energy *= 0.5 * FILL_SHARE * watts / props.LIGHT_ENERGY["fill"]
        ob["base_energy"] = ob.data.energy
        ob["group"] = "ug_hall"
        ob.name = "light_ug_hall_fill_%d" % i
        v.lights.setdefault("ug_hall", []).append(ob)
        v.lantern_lights.append(ob)


def build_village(scene, seed=1, bed_colors=None, edit=None, **kw):
    """village.build_village with this set in its hook (plus `edit`, another film hook, called first), then
    finish(): returns (Village, UndergroundSet). kw go to underground_set."""
    from . import village

    def hook(b):
        if edit is not None:
            edit(b)
        underground_set(b, **kw)

    v = village.build_village(scene, seed=seed, bed_colors=bed_colors, edit=hook)
    return v, finish(v)


def cameras():
    """Suggested cameras per beat: name -> dict(pos, target, lens, fstop, note). Filled in below (CAMERAS)."""
    return {k: dict(v) for k, v in CAMERAS.items()}


def bounce(st, shot, pos, energy=35.0, color=(1.0, 0.95, 0.88), name=None, start=None, kind="fill"):
    """A film-local SHADOWLESS fill for one shot only (hidden in every other frame: hidden objects are not in a
    frame's stamp), for a face or a pair of trousers on the dark side of the torches (as films/nitwit.py
    SMITH_BOUNCE). Beat 13: bounce(st, s, U.COUNTER_BOUNCE) lifts Steve's side that faces the lens. Beat 24:
    bounce(st, s, U.DOORWAY_GLOW, energy=DOORWAY_WATTS, color=POINT_COLOR, start=r["open"], kind="torch") is the
    light that falls in when the wall opens (it comes on at `start`, a frame inside the shot; kind "torch" = a
    shadowed point light with the torches' near field, "fill" = shadowless, at most W / 4 near it). Returns it."""
    from . import props

    ob = props.make_light(kind, st.v.collection)
    ob.name = name or "ug_bounce_%s" % shot.name
    ob.location = tuple(pos)
    ob.data.color = tuple(color)
    ob.data.energy = float(energy)
    on = shot.frame_start if start is None else int(math.ceil(start))
    for f, hidden in ((st.film.frame_start, True), (on, False), (shot.frame_end + 1, True)):
        st.key(ob, "hide_render", f, hidden)
    return ob


COUNTER_BOUNCE = (16.9, -11.5, F + 1.3)   # beat 13: east of Steve at the counter, between him and the b13 camera
DOORWAY_GLOW = (14.75, -14.9, F + 1.6)    # beat 24: high in the open doorway (kind "torch"): the light of
DOORWAY_WATTS = 60.0                      # dad's cell falling into the box (the game re-lights the
                                          # box to about level 9 within a tick of the wall opening)
SLOT_FACE = (SLOT[0] + 0.6, SLOT[1] + 0.5, F + 0.45)   # the slot's bars seen from the leg (a focus point, beat 21)
SLOT_STRIP = (16.55, -15.5, F + 0.3)      # beat 24: the strip of torchlight through the slot's bars, low outside it
SLOT_STRIP_WATTS = 6.0                    # (kind "torch": a shadowed point, the bars' shadows fall on the box floor)
# beat 8 / 21: Steve walks out of the back corner past the slot, north to the aisle, under the b08 camera's line
STEVE_PAST = [(17.6, -16.65, float(F)), (17.6, -12.2, float(F))]
HIDE_FACE_LOOK = (SLOT[0] - 0.6, SLOT[1] - 0.9, F - 0.6)   # beat 8: where the baby in the box looks (down, south)
APPLE_POINT = (14.145, -11.75, F + 1.23)  # beat 14: the golden apple in Steve's right hand at ug_aisle_dad, raise_arm 55
                                          # (MEASURED: players item_point("right", f) on that pose)


def cheat(target, head, camera, k=0.35):
    """A look target turned part of the way toward the lens (a child in profile that looks at something beyond
    itself shows a blank cheek: films/poppy_day.py _to_lens): k = 0 the target itself, 1 the camera."""
    t, h, c = Vector(target), Vector(head), Vector(camera)
    d0 = t - h
    d1 = (c - h).normalized() * d0.length
    return tuple(h + d0.lerp(d1, k))


# name -> dict(pos, target, lens, fstop, beat, note): the framings of the proof stills (each rendered and looked at:
# out/test/underground_<still>.png). A start, not a rule.
CAMERAS = {
    "b01_mouth": dict(beat=1, still="mouth", pos0=(9.0, -2.2, 0.92), target0=(5.0, 5.0, 1.6), pos=(7.9, -1.6, 0.88),
                      target=(4.9, -1.1, -0.1), lens=28.0, fstop=3.2,
                      aim_from="steve.head",
                      note="child's eye height east of the mouth: s.move(pos0, steve.head, pos, target) - the aim "
                           "rides on his head (aim_from; target0 is where it starts) as he crosses in profile from "
                           "the north and eases onto the glowing hole while the camera pushes in (the well and the "
                           "sunset behind); BEATS gives his frames in the picture"),
    "b02_lip": dict(beat=2, still="lip", pos=(5.75, -0.85, 0.82), target=(4.85, 1.42, 0.52), lens=50.0, fstop=2.0,
                    note="over the hole, three-quarter front on the child at the lip; repeated by b24_box"),
    "b03_push": dict(beat=3, still="push", pos=(9.0, 1.0, 1.05), target=(5.0, 0.7, 1.0), lens=28.0, fstop=3.2,
                     kid=(8.1, 1.45, 0.0), note="side-on and low from the east (the well behind them): dad turned "
                                               "back to the lens, Steve at his back; the child at `kid` (facing "
                                               "west, watching) is the soft head in the bottom right corner"),
    "b04_bed": dict(beat=4, still="bed", pos=(16.45, -9.85, 1.85), target=(19.9, -9.5, 3.15), lens=24.0, fstop=2.6,
                    note="beside the foot of the red bed, low; the bed fills the bottom third, room above him for "
                         "the 1.25-block jump"),
    "b05_bed_wide": dict(beat=5, still="bed_wide", pos=(11.4, -8.7, 2.25), target=(18.6, -9.6, 2.0), lens=30.0,
                         fstop=3.2, note="by the door, locked off: he stands on the bed facing it"),
    "b06_stairwell": dict(beat=6, still="stairwell", pos=(5.0, -0.7, 1.45), target=(5.0, -6.0, -6.2), lens=26.0,
                          fstop=4.0, note="high behind at the top of the flight"),
    "b07_down": dict(beat=7, still="down", pos=(14.5, -11.8, -4.3), target=(14.45, -13.4, -8.6), lens=26.0,
                     fstop=4.0, pos0=(7.8, -11.3, -2.6), target0=(7.8, -13.5, -8.6),
                     note="the ceiling and the caps off (st.see_through 'ug_ceiling', 'ug_caps'): from above the "
                          "aisle, 70 degrees down into "
                          "the pockets (the frame's up is south), sliding east and down from the farmer's pocket "
                          "(pos0) to dad's (pos): hats in the pockets, dad looks up, the box's lid behind his cell, "
                          "the lever on the end pier"),
    "b08_slot": dict(beat=8, still="slot_boots", pos=(19.75, -15.3, F + 0.2), target=(16.0, -15.5, F + 0.45),
                     lens=35.0, fstop=2.0, boot=(17.6, -15.42, F + 0.12), pos1=(18.6, -15.4, F + 0.24),
                     target1=(16.0, -15.5, F + 0.45),
                     note="on the floor against the corner's east wall, square on to the slot 3.75 away: Steve's boots "
                          "cross 2.15 from the lens (path U.STEVE_PAST, south to north, frame left to right), the "
                          "slot soft 1.6 beyond them; beat 21: the same, focus on the slot (U.SLOT_FACE), push in to "
                          "pos1 / target1"),
    "b09_lever": dict(beat=9, still="lever", pos=(14.45, -10.3, F + 1.35), target0=(15.55, -12.0, F + 1.35),
                      target=(14.8, -14.0, F + 0.95), lens=32.0, fstop=2.0,
                      note="from the aisle in front of dad's window, close on the lever (Steve's arm reaches in from "
                           "the left), then hold_then_move pans right onto the back wall past dad's shoulder while "
                           "the focus pulls to it: the wall jerks aside, the doorway black beside his robe"),
    "b10_cell_side": dict(beat=10, still="cell_open", pos=(15.25, -10.3, -9.35), target=(14.3, -14.6, -8.8),
                          lens=28.0, fstop=2.8, note="low and a little to one side: the black doorway beside his robe"),
    "b11_portrait": dict(beat=11, still="portrait", pos=(15.05, -11.25, -8.3), target=(14.32, -13.25, -8.55),
                         lens=40.0, fstop=2.0, note="tight three-quarter portrait from the aisle, east of his axis"),
    "b13_counter": dict(beat=13, still="counter", pos=(17.9, -12.3, -8.45), target=(14.0, -12.5, -8.7), lens=20.0,
                        fstop=2.8, note="side-on along the counter from the east, through the see-through end pier "
                                        "('ug_end_pier'; register the lever with the Stage and leave it out of the shot):"
                                        " Steve right, zombie dad left behind the lectern"),
    "b14_apple": dict(beat=14, still="apple", pos=(13.55, -10.55, -8.3), target=APPLE_POINT, lens=50.0, fstop=1.8,
                      target_from="steve.item_point('right', f)",
                      note="beside Steve's right hand (he faces south: his right is west), close on the golden apple in "
                           "his raised hand: `target` is where it is with Steve at ug_aisle_dad and raise_arm(f, 55); "
                           "use target_from (the apple itself) for focus and aim if he moves"),
    "b15_drift": dict(beat=15, still="drift", pos=(14.6, -11.5, -8.45), target=(14.72, -15.0, -9.1), lens=32.0,
                      fstop=2.4, pos0=(14.75, -10.5, -8.3), note="drift past his shoulder toward the black doorway"),
    "b17_ots": dict(beat=17, still="ots", pos=(14.0, -10.35, -8.05), target=(14.32, -13.3, -8.55), lens=35.0,
                    fstop=2.8, note="over Steve's shoulder at the counter: the emerald up, the book coming"),
    "b18_portrait": dict(beat=18, still="follow", pos=(14.1, -10.4, -7.7), target=(14.32, -13.3, -8.45), lens=50.0,
                         fstop=2.0, note="portrait of dad from in front, a little above his eyes: as his head "
                                         "follows Steve (walking away west along ug_follow_start -> ug_follow_end, "
                                         "under the lens) to its 70-degree stop, his face turns into profile, the "
                                         "big nose pointing up the aisle. (His cell is a 1-wide pocket 0.3 behind "
                                         "the counter with the pier on his west: a face turned west is seen from "
                                         "the front only)"),
    "b23_kill": dict(beat=23, still="kill", pos=(8.3, -11.75, -9.0), target=(4.6, -10.9, -9.0), lens=24.0, fstop=2.8,
                     note="the stair foot wider: one swing, the zombie tips over by the steps"),
    "b12_cell": dict(beat=12, still="cell", pos=(14.5, -10.25, -8.75), target=(14.5, -14.0, -9.0), lens=26.0,
                     fstop=3.2, note="frontal, symmetrical, the whole cell; also beats 10-11 a little to one side"),
    "b16_aisle": dict(beat=16, still="aisle", pos=(17.5, -10.5, -8.4), target=(9.19, -13.94, -9.1), lens=20.0,
                      fstop=4.0, note="wide down the aisle from its east end, through the see-through end pier "
                                      "('ug_end_pier'; the lever out of the shot): zombie dad in his window on the "
                                      "left, the cleric, fletcher and farmer in theirs, Steve jumping at "
                                      "ug_jump_spot, the aisle falling off into the dark beyond the stair foot"),
    "b19_endwall": dict(beat=19, still="endwall", pos0=(16.9, -12.55, F + 0.95), target0=(14.5, -13.2, F + 1.55),
                        pos=(16.95, -13.4, F + 0.9), target=(14.5, -14.0, F + 1.0), lens=32.0, fstop=2.4,
                        look=(13.4, -10.3, F + 1.6),
                        note="through the see-through end wall AND end pier ('ug_end_wall', 'ug_end_pier': leave "
                             "the lever out of the shot) from the north-east, lower than his face: dad at "
                             "ug_cell_dad_mid gazing up the aisle 20 degrees west of north (`look`) is in profile; "
                             "slide (pos0 -> pos) off his face onto the piston wall behind his back"),
    "b19_alt": dict(beat=19, still="endwall_alt", pos=(13.95, -10.55, -9.05), target=(14.6, -13.8, -8.6), lens=32.0,
                    fstop=2.4, note="from the aisle west of the cell, low: his face turned up the aisle toward the "
                                    "lens, the piston wall beside his back"),
    "b20_well": dict(beat=20, still="well", pos=(8.3, -5.4, 0.9), target=(0.0, 0.5, 0.8), lens=26.0, fstop=4.0,
                     note="the square at dusk from the south-east: the well, the glowing mouth in front of it"),
    "b22_foot": dict(beat=22, still="foot", pos=(8.8, -11.95, -9.25), target=(4.3, -10.15, -9.05), lens=24.0,
                     fstop=2.8, note="the stair foot, the child three-quarter front, the dark aisle behind"),
    "b24_box": dict(beat=24, still="box", pos=(16.9, -15.55, -9.33), target=(14.5, -15.45, -9.4), lens=35.0,
                    fstop=2.0, pos1=(16.9, -15.45, -9.25), target1=(14.4, -13.75, F + 1.15),
                    note="inside the box through its see-through side ('ug_box_side', 'ug_slot', 'ug_end_wall' for "
                         "the pan to dad); the pan goes RIGHT (north) to pos1 / target1, dad's back and book hat"),
}


# =====================================================================================================================
# small mechanics the beats need (frames are film frames; 1 tick = 1.2 frames)
# =====================================================================================================================
# Entity.push(Entity): d = absMax(dx, dz) between the centres; if d >= 0.01: (dx, dz) / sqrt(d) * min(1, 1 / sqrt(d))
#   * 0.05 is pushed into the other entity and the opposite into this one (LivingEntity.pushEntities -> doPush ->
#   push, every tick, for boxes that overlap). LivingEntity.aiStep calls pushEntities unconditionally, and the
#   server runs it for BOTH: the villager's own (doPush(player) -> player.push(villager)) and the ServerPlayer's
#   (doPush -> villager.push(player); ServerPlayer.doTick -> Player.tick), so the villager is pushed twice a tick.
#   The player is moved by his client, where EntitySelector.pushableBy lets nothing but the local player be pushed:
#   once a tick (the client-side villager's pushEntities).
PUSH_STRENGTH = 0.05
PUSH_MIN_D = 0.01
VILLAGER_PUSHES = 2                   # pushes per tick the villager takes (server), the player takes 1 (client)
ENTITY_WIDTH = {"player": 0.6, "villager": 0.6, "baby": 0.3}   # EntityType sizes (baby villager: scale 0.5)
GROUND_DRAG = 0.6 * 0.91              # Block.friction 0.6 x 0.91: horizontal speed kept per tick on the ground
AIR_DRAG = 0.91                       # ... in the air
WALK_INPUT = 0.1 * 0.98               # movement speed 0.1 x forward input 0.98 (the player's acceleration per tick)
GRAVITY = 0.08                        # LivingEntity.DEFAULT_BASE_GRAVITY
VERTICAL_DRAG = 0.98
STEP_UP = 0.6                         # Entity.maxUpStep
JUMP_POWER = 0.42                     # LivingEntity.BASE_JUMP_POWER (Attributes.JUMP_STRENGTH): babies alike
# BedBlock: Blocks lambda$static$44 (every coloured bed): Properties.bounceRestitution(0.75F),
# fallDistanceReduction(0.5F). Entity.restituteMovementAfterCollisions: on landing with -vy > gravity, vy becomes
# (f * g - vy) * lerp(f, 1, airDrag) * restitution (f = the part of the tick's move made before the hit); living
# entities take the full 0.75 (getBlockBounciness: x 0.8 only for non-living ones). Sneaking suppresses it.
BED_RESTITUTION = 0.75
# JumpOnBed (the baby villager's play behaviour), read in the bytecode: start() sets remainingJumps = 3 +
# nextInt(4) and the cooldown 0; tick(): while the cooldown is > 0 it only counts down (also in the air); else, if
# onBedSurface (Mob.blockPosition() - the cell of its FEET - is a bed: the feet less than 7/16 above the mattress),
# it calls JumpControl.jump(), remainingJumps -= 1 and the cooldown = 5. That call is a jump only if the mob is
# onGround on that tick (LivingEntity.aiStep: jumping && onGround && noJumpDelay == 0 -> jumpFromGround, vy =
# max(0.42, vy); a tick without jumping sets noJumpDelay 0), so the calls that fall while it is in the air are
# spent for nothing: from rest, 3 calls give ONE jump and the bed's bounces, 6 calls give two (36 frames apart).
BED_JUMPS = (3, 6)
BED_JUMP_COOLDOWN = 5
NO_JUMP_DELAY = 10
BED_SURFACE = 1.0 - 9.0 / 16.0        # feet below this above the mattress: blockPosition is still the bed's cell


def cell_track(strength=0.4, max_back=CELL_MAX_BACK, room=CELL_HEADROOM - 1.95, max_ticks=40):
    """[(blocks forward, blocks up)] after each tick of a knock-back inside a capped cell: undead.knockback_track's
    motion (LivingEntity.knockback: vy = min(0.4, -0.0784 / 2 + strength), then move, vy = (vy - 0.08) * 0.98)
    with the cap `room` blocks above the head: Entity.move stops the rise there and restituteMovementAfterCollisions
    sets vy to 0 for a collision above (a living entity has no bounciness), so he drops back the next tick; the job
    block stops him `max_back` ahead. In a 2-high cell a villager (1.95) rises 0.05 for one tick: a jolt."""
    from . import undead

    vh = float(strength)
    vy = min(0.4, undead.REST_VY / 2.0 + float(strength))
    x = y = 0.0
    ground = True
    out = []
    for _ in range(max_ticks):
        drag = undead.GROUND_DRAG if ground else undead.AIR_DRAG
        x += vh
        y += vy
        if max_back is not None and x > max_back:
            x, vh = float(max_back), 0.0
        if room is not None and y > room:
            y, vy = float(room), 0.0
        ground = False
        if y <= 0.0:
            y, vy, ground = 0.0, 0.0, True
        out.append((x, y))
        vy = (vy - undead.GRAVITY) * undead.AIR_DRAG_Y
        vh *= drag
        if ground and abs(vh) < 0.003:
            break
    return out


def _cell_hop(c, frame, attacker, max_back, headroom, strength):
    """Key the capped knock-back of cell_track on c's root from `frame` (the series' room ahead is shared by the
    blows that follow while he has not been placed or walked since: c._ug_cell)."""
    from . import characters as ch
    from . import undead

    f0 = float(frame)
    here = c.pos_at(f0)
    away = undead._away(c, f0, attacker)
    ser = getattr(c, "_ug_cell", None)
    used = 0.0
    if ser is not None and (ser["last"] - here).length < 2e-3:
        used = max(0.0, (here - ser["anchor"]).dot(away))
        anchor = ser["anchor"]
    else:
        anchor = here.copy()
    height = undead.body_box(c)[1]
    track = cell_track(strength, max(0.0, max_back - used), max(0.0, headroom - height))
    for i in range(3):
        keys = [(f0, None, "LINEAR")]
        for k, (back, up) in enumerate(track):
            keys.append((f0 + (k + 1) * TICK, here[i] + away[i] * back + (up if i == 2 else 0.0), "LINEAR"))
        ch._segment(c.root, "location", i, keys, "LINEAR")
    last = here + away * track[-1][0] if track else here
    c._ug_cell = dict(anchor=anchor, last=last.copy())
    return dict(track=track, end=int(math.ceil(f0 + len(track) * TICK)),
                peak=max((u for _b, u in track), default=0.0))


def hurt_in_cell(character, frame, attacker=None, max_back=CELL_MAX_BACK, headroom=CELL_HEADROOM, flash=True):
    """A blow to a villager standing in his capped cell (beats 10, 11): undead.hurt's red flash and leg kick, and
    the knock-back as the game plays it under the cap (cell_track: up 0.05 for one tick, at most max_back toward
    the job block): the small jolt the story asks for, the face stays in the window. A blow less than 12 frames
    after the last one is ignored, as undead.hurt ignores it. Returns dict(end, peak, landed)."""
    from . import undead

    f0 = int(round(frame))
    end = undead.hurt(character, f0, attacker=attacker, knockback=False, flash=flash)
    landed = any(b["frame"] == f0 for b in undead._state(character)["blows"])
    if not landed:
        return dict(end=end, peak=0.0, landed=False)
    hop = _cell_hop(character, f0, attacker, max_back, headroom, undead.KNOCKBACK if attacker is not None else 0.0)
    return dict(end=max(end, hop["end"]), peak=hop["peak"], landed=True)


def infect_in_cell(villager, zombie_villager, frame, attacker=None, max_back=CELL_MAX_BACK, headroom=CELL_HEADROOM):
    """undead.infect in the capped cell (beat 12): the villager replaced on `frame` by the zombie villager, who
    takes the killing blow's jolt under the cap (cell_track). Returns dict(end, peak)."""
    from . import undead

    f0 = int(round(frame))
    end = undead.infect(villager, zombie_villager, f0, attacker=attacker, knockback=False)
    ser = getattr(villager, "_ug_cell", None)
    if ser is not None:
        zombie_villager._ug_cell = dict(ser)
    hop = _cell_hop(zombie_villager, f0, attacker, max_back, headroom,
                    undead.KNOCKBACK if attacker is not None else 0.0)
    return dict(end=max(end, hop["end"]), peak=hop["peak"])


def hold_then_move(shot, frame_move, pos0, target0, pos1, target1, frame_end=None, ease="smooth"):
    """A camera that HOLDS pos0 / target0 until `frame_move`, then moves to pos1 / target1 by `frame_end` (default:
    the shot's end) and holds there: Shot.move eases over the whole shot, this re-times its curve (the Shot's own
    _bake keys it, also when Film.finalize re-bakes; handheld() still works on top). Beat 24: hold a full second,
    then pan with his first step. Returns the shot."""
    from . import shots as _shots

    f_m = float(frame_move)
    f_e = float(shot.frame_end + 1 if frame_end is None else frame_end)
    e = _shots.EASES[ease]

    def u(frame, f_m=f_m, f_e=f_e):
        if frame <= f_m:
            return 0.0
        return min(1.0, (frame - f_m) / max(1.0, f_e - f_m))
    shot._u = (lambda frame, u=u, e=e: e(u(frame)))   # an instance attribute: Shot._bake reads self._u(frame)
    shot.move(pos0, target0, pos1, target1, ease="linear")
    return shot


def _top_at(world, x, y, z_max):
    """Height of the walking surface under the point (x, y): the top of the highest solid block whose top is at
    most z_max (stairs by their two halves, bottom slabs, path blocks 15/16)."""
    cx, cy = int(math.floor(x)), int(math.floor(y))
    fx, fy = x - cx, y - cy
    for z in range(int(math.floor(z_max)), int(math.floor(z_max)) - 24, -1):
        st = world.get(cx, cy, z)
        if st is None or not world.is_solid(cx, cy, z):
            continue
        bid, p = st
        top = z + 1.0
        if bid.endswith("_stairs") and p.get("half", "bottom") == "bottom":
            face = p.get("facing", "north")
            high = {"north": fy >= 0.5, "south": fy < 0.5, "east": fx >= 0.5, "west": fx < 0.5}[face]
            top = z + (1.0 if high else 0.5)
        elif bid.endswith("_slab") and p.get("type", "bottom") == "bottom":
            top = z + 0.5
        elif bid in ("dirt_path", "farmland"):
            top = z + 15.0 / 16.0
        if top <= z_max + 1e-6:
            return top
    return None


def _support(world, x, y, z_now, half, along):
    """The highest surface under an entity's square footprint (it stands on whatever is under any part of it)."""
    best = None
    ax, ay = along
    px, py = -ay, ax
    for u in (-half + 0.01, 0.0, half - 0.01):
        for w_ in (-half + 0.01, 0.0, half - 0.01):
            t = _top_at(world, x + ax * u + px * w_, y + ay * u + py * w_, z_now + STEP_UP)
            if t is not None and (best is None or t > best):
                best = t
    return best


def push(player, villager, frame, path, world, taps=(4, 4), steps_down=1, gap=0.9, legs=False, tail=6,
         max_ticks=600, stop_margin=0.32):
    """THE PLAYER WALKS INTO A VILLAGER and pushes him along `path` ((x, y[, z]) points; the villager starts at
    path[0], the player `gap` blocks behind him) until he has dropped down `steps_down` steps (the stair's two
    half steps count as one each), with the game's entity push (Entity.push: 0.05 * sqrt(d) per tick while the two
    boxes overlap, d = the distance of the centres) and friction. The push is weakest when they overlap most, so a
    player who holds the walk key walks THROUGH a villager in about a second: players push villagers along by
    tapping it, which is what `taps` = (ticks pressed, ticks released) does (4, 4: about 1.1 blocks/s, in small
    nudges; None = held). The player stops at the lip (he never follows him down). Both are placed on `frame`;
    the villager slides with no walk cycle (legs=True: the game's leg wave from the distance he moves, which the
    game does draw for a pushed mob). Returns dict(end, landed, drops, villager, player) with per-tick tracks."""
    from . import characters as ch

    f0 = int(round(frame))
    pts = [Vector((p[0], p[1], 0.0)) for p in path]
    seg = [(b - a).length for a, b in zip(pts, pts[1:])]
    total = sum(seg)
    dirv = (pts[-1] - pts[0]).normalized()
    along = (dirv.x, dirv.y)

    def at(s):
        for i, length in enumerate(seg):
            if s <= length or i == len(seg) - 1:
                return pts[i].lerp(pts[i + 1], max(0.0, s / length) if length > 1e-9 else 0.0)
            s -= length
        return pts[-1]

    def xy(s):
        if s < 0:
            return pts[0] + dirv * s
        if s > total:
            return pts[-1] + dirv * (s - total)
        return at(s)

    zv = _support(world, pts[0].x, pts[0].y, 2.0, 0.3, along) or 0.0
    zp0 = _support(world, xy(-gap).x, xy(-gap).y, 2.0, 0.3, along) or 0.0
    sv, vv, vz, z, sp, vp = 0.0, 0.0, 0.0, zv, -gap, 0.0
    ground = True
    drops, landed_tick = [], None
    stop_s = None
    vtrack, ptrack = [(sv, z)], [sp]
    t = 0
    while t < max_ticks:
        pressed = taps is None or (t % (taps[0] + taps[1])) < taps[0]
        if len(drops) >= steps_down or (stop_s is not None and sp >= stop_s):
            pressed = False
        # the player: input, move, friction (he stays on the square)
        if pressed:
            vp += WALK_INPUT
        sp += vp
        if stop_s is not None and sp > stop_s:
            sp, vp = stop_s, 0.0
        vp *= GROUND_DRAG
        # the villager: move, fall, friction
        sv += vv
        q = xy(sv)
        sup = _support(world, q.x, q.y, z, 0.3, along)
        if ground and (sup is None or sup < z - 1e-6):
            ground, vz = False, 0.0
        if not ground:
            z_new = z + vz
            if sup is not None and z_new <= sup:
                z, vz, ground = sup, 0.0, True
                drops.append(t)
                landed_tick = t
            else:
                z = z_new
                vz = (vz - GRAVITY) * VERTICAL_DRAG
        elif sup is not None and sup > z:
            z = sup                                          # stepping up (not on this path)
        vv *= GROUND_DRAG if ground else AIR_DRAG
        # the push (after travel), while the two boxes overlap
        dx = sv - sp
        if abs(dx) < 0.5 * (ENTITY_WIDTH["player"] + ENTITY_WIDTH["villager"]) and z < zp0 + 1.8:
            d = abs(dx)
            if d >= PUSH_MIN_D:
                r = math.sqrt(d)
                p = (dx / r) * min(1.0, 1.0 / r) * PUSH_STRENGTH
                vv += VILLAGER_PUSHES * p
                vp -= p
        if stop_s is None:
            lip = _first_drop(world, xy, zp0, along)
            stop_s = lip - stop_margin if lip is not None else total + 10.0
        vtrack.append((sv, z))
        ptrack.append(sp)
        t += 1
        if len(drops) >= steps_down and ground and abs(vv) < 2e-3 and abs(vp) < 2e-3:
            break
    for _ in range(tail):
        vtrack.append(vtrack[-1])
        ptrack.append(ptrack[-1])
    # keys: the villager's feet per tick (LINEAR), the player through his own gait (engine.players)
    yaw = math.atan2(dirv.x, -dirv.y)
    villager.place(f0, (pts[0].x, pts[0].y, zv), yaw)
    for i in range(3):
        keys = []
        for k, (s, zz) in enumerate(vtrack):
            q = xy(s)
            keys.append((f0 + k * TICK, (q.x, q.y, zz)[i], "LINEAR"))
        ch._segment(villager.root, "location", i, keys, "LINEAR")
    if legs:
        _leg_wave(villager, f0, [b[0] - a[0] for a, b in zip(vtrack, vtrack[1:])], scale=0.5)
    start = xy(-gap)
    player.place(f0, (start.x, start.y, zp0), yaw)
    steps = [b - a for a, b in zip(ptrack, ptrack[1:])]
    _drive_player(player, f0, [Vector((xy(s).x, xy(s).y, zp0)) for s in ptrack], steps)
    end = int(math.ceil(f0 + (len(vtrack) - 1) * TICK))
    return dict(end=end, landed=None if landed_tick is None else int(math.ceil(f0 + landed_tick * TICK)),
                drops=[int(math.ceil(f0 + d * TICK)) for d in drops], villager=vtrack, player=ptrack,
                speed=(vtrack[-1][0] - vtrack[0][0]) / max(1e-9, (len(vtrack) - 1) / 20.0))


def _first_drop(world, xy, z, along):
    """Distance along the push line where the ground first drops by half a block or more (the lip)."""
    prev = None
    s = 0.0
    while s < 40.0:
        q = xy(s)
        top = _top_at(world, q.x, q.y, z + 0.1)
        if prev is not None and (top is None or top < prev - 0.4):
            return s
        prev = top if top is not None else prev
        s += 0.05
    return None


def _leg_wave(c, f0, steps, scale=0.5):
    """The game's walk-animation legs from per-tick distances (calculateEntityAnimation, HumanoidModel /
    VillagerModel legs cos(0.6662 p) * 1.4 * s * scale)."""
    from . import characters as ch

    p, s = 0.0, 0.0
    kr, kl = [], []
    for k, d in enumerate(list(steps) + [0.0] * 12):
        s += (min(4.0 * abs(d), 1.0) - s) * 0.4
        p += s
        a = math.cos(0.6662 * p) * 1.4 * s * scale
        kr.append((f0 + k * TICK, a, "LINEAR"))
        kl.append((f0 + k * TICK, -a, "LINEAR"))
    ch._segment(c.leg_r, "rotation_euler", 0, kr, "LINEAR")
    ch._segment(c.leg_l, "rotation_euler", 0, kl, "LINEAR")


def _drive_player(player, f0, positions, steps):
    """Key a player (engine.players.Player) along per-tick positions with his own gait (legs from the distances)."""
    path = []
    for q in positions:
        if not path or (q - path[-1]).length > 1e-6:
            path.append(q.copy())
    if len(path) < 2:
        return
    cum = [0.0]
    for d in steps:
        cum.append(cum[-1] + abs(d))
    if hasattr(player, "_travel") and hasattr(player, "_limbs"):
        total = sum((b - a).length for a, b in zip(path, path[1:]))
        k = total / cum[-1] if cum[-1] > 1e-9 else 1.0
        cum = [c * k for c in cum]
        times = player._travel(f0, path, cum)
        player._yaw_keys(f0, path, times, False)
        player._limbs(f0, [abs(d) * k for d in steps])
    else:
        player.walk(f0, [positions[0], positions[-1]], speed=max(0.3, cum[-1] / max(1e-6, len(steps) / 20.0)))


def _bed_ticks(jumps, mode="game", settle=True):
    """Per-tick heights above the mattress of a baby villager on a bed, and the take-off / landing ticks.
    mode "game": JumpOnBed as the brain runs it (see BED_JUMPS: `jumps` calls of jump(), the ones that fall while
    he is in the air spent for nothing; a list = that many runs of the behaviour back to back, each starting the
    tick after the bed has settled). mode "regular" (NOT THE GAME, the earlier film choice): `jumps` full jumps,
    each the tick after the last landing. Landings on the bed bounce (Entity.restituteMovementAfterCollisions,
    restitution 0.75, -vy > gravity)."""
    runs = list(jumps) if isinstance(jumps, (list, tuple)) else [int(jumps)]
    z, vy, ground = 0.0, -GRAVITY * VERTICAL_DRAG, True
    track, takeoffs, landings, peaks = [0.0], [], [], []
    top, t, njd = 0.0, 0, 0
    for n in runs:
        left, cool, quiet = int(n), 0, 0
        while t < 2000:
            if njd > 0:
                njd -= 1
            jumping = False
            if left > 0:
                if mode == "game":
                    if cool > 0:
                        cool -= 1
                    elif z < BED_SURFACE:                     # onBedSurface: the feet still in the bed's cell
                        jumping, left, cool = True, left - 1, BED_JUMP_COOLDOWN
                elif ground:
                    jumping, left = True, left - 1
            if jumping:
                if ground and (njd == 0 or mode != "game"):
                    vy = max(JUMP_POWER, vy)
                    njd = NO_JUMP_DELAY
                    takeoffs.append(t)
            else:
                njd = 0
            z_new = z + vy
            if vy < 0.0 and z_new <= 0.0:                    # lands on the mattress
                frac = z / -vy
                bounce = -vy > GRAVITY and (settle or left > 0)
                vy = ((frac * GRAVITY - vy) * (1.0 + frac * (VERTICAL_DRAG - 1.0)) * BED_RESTITUTION
                      if bounce else 0.0)
                if top > 1e-3:
                    landings.append(t)
                    peaks.append(round(top, 3))
                z, ground, top = 0.0, True, 0.0
            else:
                z, ground = z_new, False
                top = max(top, z)
            vy = (vy - GRAVITY) * VERTICAL_DRAG               # LivingEntity.travelInAir: gravity, then drag
            track.append(z)
            t += 1
            quiet = quiet + 1 if (ground and z == 0.0 and vy < 0.0 and -vy <= GRAVITY) else 0
            if left <= 0 and quiet >= 2:
                break
    return dict(track=track, takeoffs=takeoffs, landings=landings, peaks=peaks)


def bed_bounce(child, frame, spot, jumps=6, mode="game", settle=True):
    """A baby villager jumping on a bed. mode "game" (default): JumpOnBed as the brain plays it: `jumps` = the
    behaviour's jump() calls (the game draws 3 to 6; the ones that fall while he is in the air are wasted, so 3
    give one 1.25-block jump and the bed's bounces 0.56, 0.24, 0.10, 0.04; 6 give a second jump 36 frames after
    the first); a list (6, 6, ...) runs the behaviour again right after the bed has settled (a film choice: the
    game picks its play behaviours at random). mode "regular" (NOT THE GAME): `jumps` full jumps each the tick
    after the last landing (every 14.4 frames), then the bounces. `spot` = (x, y, z) on the mattress (z = its
    top: the Village bed anchors). Placed on `frame` facing the way he faces there; no leg motion (the game draws
    no walk animation for a vertical move). Returns dict(end, takeoffs, landings, peaks, track) in frames."""
    from . import characters as ch

    f0 = int(round(frame))
    base = float(spot[2])
    r = _bed_ticks(jumps, mode, settle)
    yaw = child.yaw_at(f0)
    child.place(f0, (spot[0], spot[1], base), yaw)
    ch._segment(child.root, "location", 2, [(f0 + k * TICK, base + zz, "LINEAR") for k, zz in enumerate(r["track"])],
                "LINEAR")
    fr = lambda ticks: [int(math.ceil(f0 + x * TICK)) for x in ticks]
    return dict(end=int(math.ceil(f0 + (len(r["track"]) - 1) * TICK)), takeoffs=fr(r["takeoffs"]),
                landings=fr(r["landings"]), peaks=r["peaks"], track=[base + z for z in r["track"]])


def jump_loop(player, frame_start, frame_end):
    """The player jumping on the spot again and again (space held: a new jump the tick he lands, every 12 ticks
    = 14.4 frames; engine.players Player.jump). Returns the take-off frames."""
    out = []
    t = float(frame_start)
    period = 12 * TICK
    while t + period <= frame_end + 1e-6:
        out.append(int(round(t)))
        player.jump(t)
        t += period
    return out


def hidden_frames(world, camera, character, frame_start, frame_end, points=(0.25, 0.55, 0.85), step=0.08):
    """Frames on which every sample point of the character (heights as fractions of its height, on its centre
    line) is hidden from the camera by solid blocks of the World. camera = a point or a callable frame -> point."""
    import bpy as _bpy

    out = []
    h = getattr(character, "height", 1.0)
    for f in range(int(frame_start), int(frame_end) + 1):
        cam = Vector(camera(f) if callable(camera) else camera)
        feet = character.pos_at(f)
        hidden = True
        for frac in points:
            p = feet + Vector((0.0, 0.0, h * frac))
            d = p - cam
            n = max(1, int(d.length / step))
            blocked = False
            for i in range(1, n):
                q = cam + d * (i / n)
                c = (int(math.floor(q.x)), int(math.floor(q.y)), int(math.floor(q.z)))
                if world.is_solid(*c) and world.is_full_cube(*c):
                    blocked = True
                    break
            if not blocked:
                hidden = False
                break
        if hidden:
            out.append(f)
    return out


def swap_hidden(child, adult, camera, frame_start, frame_end, world, then=None, speed=None):
    """Beat 20: the child is swapped for the grown-up villager on a frame where it is hidden from the camera
    (by the well): the middle of the longest run of hidden frames between frame_start and frame_end. The adult is
    not there before that frame (engine.undead vanish / appear, independent of the Stage's shows), stands where the
    child was, facing the same way, and walks on along `then` (points) at `speed` (None: the child's own walk
    ends there and the adult's stroll is Character.walk's default). Returns dict(frame, hidden)."""
    from . import undead

    hid = hidden_frames(world, camera, child, frame_start, frame_end)
    if not hid:
        raise ValueError("swap_hidden: the child is never hidden from that camera between frames %d and %d"
                         % (frame_start, frame_end))
    runs, cur = [], [hid[0]]
    for f in hid[1:]:
        if f == cur[-1] + 1:
            cur.append(f)
        else:
            runs.append(cur)
            cur = [f]
    runs.append(cur)
    best = max(runs, key=len)
    f = best[len(best) // 2]
    undead.vanish(adult, frame_start)
    undead.vanish(child, f)
    pos, yaw = child.pos_at(f), child.yaw_at(f)
    adult.place(f, pos, yaw)
    undead.appear(adult, f)
    if then:
        adult.walk(f, [pos] + list(then), speed=speed)
    return dict(frame=f, hidden=(best[0], best[-1]), runs=[(r[0], r[-1]) for r in runs])


def shade_face(v, zv, groups=("ug_corner",)):
    """Keep the baby zombie villager's head and robe out of the corner torch's point light (Blender light linking:
    the light's receiver collection EXCLUDES them; his arms and hands still catch it), so in beat 8 his face never
    reads behind the bars while the hands do. Static for the whole film (light linking is set on the light, not
    keyed): in beat 24 the box is lit by U.SLOT_STRIP / U.DOORWAY_GLOW, which are not linked. NOT THE GAME: the game
    draws a mob at the block light of its cell, the same from every side."""
    keep = set()
    for arm in (zv.arm_r, zv.arm_l):
        if arm is not None:
            keep.add(arm.name)
            keep.update(o.name for o in arm.children_recursive)
    coll = bpy.data.collections.get("ug_face_shade") or bpy.data.collections.new("ug_face_shade")
    for ob in [zv.root] + list(zv.root.children_recursive):
        if ob.type != "MESH" or ob.name in keep:
            continue
        if ob.name not in coll.objects:
            coll.objects.link(ob)
    for co in coll.collection_objects:
        co.light_linking.link_state = "EXCLUDE"
    for g in groups:
        for light in v.lights.get(g, []):
            if light.get("mc_light") != "fill":
                light.light_linking.receiver_collection = coll
    return coll


def hands_in_slot(zv, frame, slot=SLOT, lateral=0.0, face="away"):
    """The baby zombie villager inside the box with his tiny hands resting between the iron bars of the slot: he
    stands against the bars (his box touches the pane, as the game's collision allows), facing out, arms out (the
    zombie's own -80 degrees, toed in, with their slow bob); the two 2-px hands land in the bars' two gaps (texels
    4-6 and 9-11 of iron_bars.png) with the fingertips in the pane. His big head is as far forward as his hands
    (the face 0.22 ahead of his centre, the hands 0.29): face="away" (beat 8, the face must never read) turns it
    down and away toward the box's back corner (look_at, the head's 75 / 40 degree stops), so the camera in the
    leg sees the top and back of a green head and the torch from the north-east catches the hands, not the face;
    face=None leaves him looking out. Places him on `frame`; returns the hand tips."""
    import bpy as _bpy

    from . import undead

    sx, sy, sz = slot
    pane_x = sx + 0.5                                         # the pane of a north-south bars block: x 7..9 px
    yaw = yaw_of("east")
    y = sy + 0.5 + lateral
    zv.place(frame, (sx + 0.0, y, float(sz)), yaw)
    scene = _bpy.context.scene
    scene.frame_set(int(frame))
    dg = _bpy.context.evaluated_depsgraph_get()
    tips = []
    for arm in (zv.arm_r, zv.arm_l):
        ev = arm.evaluated_get(dg)
        xs = [(ev.matrix_world @ Vector(c)).x for c in ev.bound_box]
        tips.append(max(xs))
    reach = max(tips) - (sx + 0.0)
    x = pane_x + 1.0 / 32.0 - reach                           # fingertips 0.5 px into the 2-px pane
    body_back = x - undead.BABY_SIZE[0] / 2.0
    zv.place(frame, (x, y, float(sz)), yaw)
    if face == "away":
        zv.look_at(frame, HIDE_FACE_LOOK, ease=0)
    return dict(x=x, reach=reach, tip_x=x + reach, body_back=body_back, pane=(pane_x - 1 / 16.0, pane_x + 1 / 16.0))


# =====================================================================================================================
# self-test
# =====================================================================================================================

def _selftest(names):
    """No names: numeric checks (no rendering). Names: proof stills (tools/underground_proof.py)."""
    if names and names != ["check"]:
        from tools import underground_proof

        return underground_proof.main(names)
    from tools import underground_check

    return underground_check.main()


if __name__ == "__main__":
    import sys

    sys.exit(_selftest(sys.argv[1:]))
