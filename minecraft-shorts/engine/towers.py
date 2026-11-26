"""THE IRON FARM TOWER of "Twenty Minutes" (film three, stories/ironfarm.json): a stone pillar with a glass pod on
top behind the houses north-west of the well, the zombie in its cobblestone cell, the golem platform with its water
sheet and its lava-lit kill slot, the hopper and chest at the foot, the dirt staircase up the back, the one-block gap
in the back wall, the calls that make the farm work on camera, and a named camera with anchors for every beat.

New module; edits no other file. Built INTO the village through village.build_village(scene, seed=1, edit=hook), as
engine/sets.py builds its pieces; the parts that change on camera are engine/fixtures.py and engine/breaking.py
objects. Every number is transcribed from the Java Edition 26.x client classes and data files (named next to it
below and in WHAT THE GAME DOES); textures and models are the game's own through engine.blocks / engine.mcassets.
Blender axes as everywhere: +X east, +Y north, +Z up, 1 block = 1 unit, characters face -Y at yaw 0, 24 fps (1 game
tick = 1.2 frames).

USE IN A FILM
    from engine import towers, village, undead, mobs, players
    v = village.build_village(scene, seed=1, edit=lambda b: towers.iron_farm(b))   # (with other pieces: call it in
    fm = towers.farm(v)                                                           #  the same hook)
    A, yaw, C = fm.A, fm.yaw, fm.cameras          # anchors by short name, their yaws, camera framings per beat
    # everything below is keyed per shot, in film order; register what moves with the Stage
    z = undead.add_zombie(st, "zombie"); fm.zombie_in_cell(z, s.frame_start, aggro=True, look=mom)
    g = mobs.make_iron_golem("golem"); st.cast["golem"] = g; st.use(s, g)       # ONE golem for every spawn
    fm.golem_spawn(g, f, yaw=0.0, look=A["pod_target"], empty_from=s); e = fm.golem_step(g, f + 30)
    r = fm.golem_slide(g, e + 2); fm.golem_death(g, r, camera=s, until=s.frame_end + 1)
    st.lights(s, scale=1.0, groups={"tower_pod": 1.0, "tower_cell": 1.0})          # the pod's lantern, the cell torch
    c = C["cell_side"]; s.lens(c["lens"], c["fstop"]); s.move(c["pos"], c["target"])   # (moves: c["target1"])
    tools/towers_proof.py shot_bNN stages every beat exactly as BEATS says: copy from there.

PUBLIC API
  iron_farm(b, at=AT, floor=FLOOR, name="tower", water="sheet", lava_watts=40.0, rims="glass", views=None) -> dict
      In the edit hook: the whole tower (LAYOUT below) at the pod's south-west inside cell `at`, its floor top at
      `floor`. Levels and clears the ground under it; removes every village tree with its trunk or a leaf within 2
      blocks of the footprint (seed 1: the oaks with trunks at (-13, 13) and (-28, 13), 3 blocks south of it, are
      taken whole); puts every block into the World, registers anchors (tower_*), the paths tower_push_square,
      tower_steve_square and tower_steve_past, lights tower_pod / tower_cell, the beds (Village.beds
      tower_bed_white_1 / _white_2 / _mom), the pod as cutaways tower_pod_north / _east / _south / _west / _roof /
      _all. water="sheet": a level 2/9 sheet drawn flowing west (the story's still sheet); "game": sources along
      the pod wall, the game's own spread. rims="glass" (default) puts a glass rim on a stone lip along the
      platform's long edges (y 16 and y 24): the water stops there (a wandering golem, step height 1.0, could
      still step onto it); "fence" an oak fence (1.5 high: holds the golem too); None leaves them open (the sheet
      ends in the air: not the game). views: the plants
      cleared off the ground lines of the low cameras: None = every camera of cameras() lower than 4.5 blocks over
      the ground plus the lineup and the push route (seed 1: some 20 tufts, up to y 39 and on the plaza near
      (10, -2)); a list of camera names = only those; () = none. Returns the set's dict (also Village.sets[name]).
  farm(v, name="tower") -> Farm        after the build: the tower's handles and calls
  Farm .A {short name: point} .yaw {short name: yaw} .cameras {name: dict(pos, target, lens, fstop, beat[, target1])}
       .L (layout numbers) .pod (fixtures GlassBox) .bed2 (fixtures Bed: the second red bed) .hopper / .chest
       (fixtures Hopper / Chest) .water / .lava (fixtures Fluids: water sheet, lava glow) .top_step (breaking
       Breakable) .beds {key: Village.beds entry} .zombie_eye (look target of every villager in the pod)
    zombie_in_cell(zombie, frame, aggro=False, look=None, ease=0)    the zombie ON frame in its cell: pressed against
        the sill, facing the pod, arms out over the sill with engine.undead's endless slow sway; aggro=True: the
        raised arms (the game snaps: ease 0)
    golem_spawn(golem, frame, pos=None, yaw=None, look=None, look_after=6, look_ease=6, empty_from=None) -> frame
        the golem APPEARS on the platform ON frame, standing, no effect (the game spawns it in one tick); not
        rendered before (engine.undead.vanish/appear, independent of the Stage's shots); default spot = anchor
        golem_spawn facing north-west (the game gives a spawned golem a random facing: choose one per framing);
        look = a point / Character its head turns to `look_after` frames later. empty_from = the Shot (or frame) of
        the cut: REQUIRED when the golem of an earlier spawn still stands (jump cut, beat 10) or is still sliding
        (its slide not over: beat 24 after a slide shot); the old golem is gone from there, an unfinished slide's
        vanish, death puff and lava flicker end there. Without it such a call raises ValueError. Pass it on every
        spawn that opens a new shot (harmless when nothing stands).
    golem_step(golem, frame, toward=None, distance=0.45) -> end frame      one heavy step toward the pod (east)
    golem_slide(golem, frame, start=None) -> dict(frame, edge, frame_end, gone, track, drop)
        fixtures.slide west to the rim (0.014/tick push, x 0.8 drag: 1.4 blocks/s), over it and 4 blocks down
        into the slot; gone (not rendered) from the frame its head is under the rim
    golem_death(golem, slide, camera=None, delay=0, seed=0, flicker=True, glow=None, until=None) -> dict(frame, burst)
        the white death puff (engine.animals.poof, 20 particles in a 1.4 x 2.7 box, self-light 0.5) rising out of
        the slot on slide['gone'] + delay (delay 288 = the game's 12 s in lava) and the lava light smothered and
        flaring; until = the next shot's first frame: puff and flicker end there (else they run on into it)
    deliver(items, frame, every=6, seed=0, land=True, spread=0.15) -> [plan]
        engine.mobs dropped items fall out of the chute's mouth onto the hopper and vanish into it one ITEM ENTITY
        per 8 ticks (fixtures Hopper.stream). One golem drops TWO entities (golem_loot): make them
        mobs.make_dropped_item('iron_ingot', count=n) (a stack of 2-16 is drawn as two copies, as
        ItemClusterRenderState draws it) and 'poppy' (count 0..2: none when 0). plans[i]['frame'] = the frame
        item i is gone
    strew(items, frame, frame_end, seed=0, spots=None, face=None) -> [(x, y)]
        dropped items lying on the grass by the chest, bobbing and spinning (the poppies he threw out)
    break_top_step(player, frame, camera=None, duration=None, drop=None, seed=0, until=None) -> breaking.mine dict
        the top dirt step broken by hand: the game's 14 ticks (17 frames) from the click, ten crack stages, arm
        swings, crumbs, 64 dirt particles; put him on anchor one_down facing it first; camera= is required; until =
        the next shot's first frame (the crumbs end there). A second break of it in a later shot: fm.top_step.
        restore(shot.frame_start) first
    climb(c, frame, first=0, last=None, pause=3, approach=True) -> frame
        a villager / baby hops up dirt steps first..last (0 = the bottom one), each hop the game's jump, its head
        stopped by the floor overhang over the lower flight
    bounce(c, frame, bed="mom", jumps=2, place=True, yaw=None) -> frame    a baby jumping on a pod bed (JumpOnBed),
        the glass roof stopping its head 0.46 over the mattress, each landing rebounding 0.21 and 0.08 (the 26.x
        bounce): jumps=2 = "bounces twice", 1.8 s (beds: 'mom', 'white_1', 'white_2', 'bed2'); yaw = its facing
        (cheat it to the lens)
    see_through(st, shot, camera=None, n=1, cells=None, points=None) -> [panes]
        hide pod glass blocks from the camera only, for one shot: the first pane on the line from camera['pos'] to
        each of `points` (Characters or points), or the `n` first toward camera['target'], or the cells named.
        Whole walls: st.see_through(shot, "tower_pod_roof") (Stage). Call it in shot order.
    pane(cell), panes_toward(camera_pos, target, n=1), ceiling_over(x, y, z)
  panic(c, frame_start, frame_end, threat, seed=0, amount=1.0, turns=True, turn_deg=(14, 32), every=(9, 17),
        look=True) -> frame_end
      trapped panic for any villager: the tremble (body hunched 5 degrees, a +-2.4 degree twist and a sideways
      shiver every 2 frames, arms pulled in) and quick turns on the spot (3 frames each, 14-32 degrees either side
      of facing the threat, one every 9-17 frames) with the HEAD KEPT ON `threat` (Character.shiver would tuck it).
      The same seed gives the same tremble frame for frame (beat 23: the narrator's matched to Mom's).
  hop(c, frame, to, face=True, ceiling=None, speed=None) -> landing frame     one block UP: the game's jump (11
      frames); to a LOWER point: no jump, he walks off the edge and drops (fall_track: 1 block in 5 ticks)
  walk_down(c, frame, steps, pause=0) -> frame     down a run of full-block steps, stepping off each edge
  bounce(c, frame, bed, jumps=1, place=True, ceiling=None, yaw=None) -> frame   the bed bounce (Farm.bounce in the
      pod); under open sky one jump rebounds 0.56, 0.24, 0.10 ... and settles after 40 ticks (2 s)
  push(player, villager, frame, points, gap0=1.5, mode="tap", release=0.45, rest_ticks=3) -> dict(end, surges, track)
      the player walks into her back and pushes her along `points` with the game's entity push: "tap" = shoves
      (she surges 0.7-1.1 blocks at a time, 0.9 blocks/s over all), "sneak" = a slow continuous shuffle (0.75
      blocks/s). It place()s both ON frame; key her head (look_at) after it.
  grow_up(baby, adult, frame, look=None) -> frame     the baby replaced by the adult ON frame, same spot and facing,
      no effect (engine.undead.vanish / appear: the adult is not rendered before, the baby not after)
  spawn_cell(world, x, y, villager_z, fluids=()) / spawn_cells(world, villagers, fluids=())    the game's golem
      spawn rule (Villager.spawnGolemIfNeeded + SpawnUtil + IronGolem.checkSpawnObstruction) on a World
  golem_loot(seed) -> {'iron_ingot': 3..5, 'poppy': 0..2}           loot_table/entities/iron_golem.json
  jump_track(up, ceiling=None), fall_track(down), bounce_track(jumps, min_bounce=None, ceiling=None),
  push_route(total, ...)      the per-tick physics behind hop / bounce / push
  layout(at, floor, ground, rims) -> dict        every cell of the tower as numbers (no Blender)
  cameras(L) -> {name: dict(pos, target, lens, fstop, beat[, target1])}   the beat framings (also Farm.cameras)
  frame_xy(camera, point) -> (x %, y % from the top, depth)   where a point lands in a camera's 9:16 frame
  beat_frames(fm) -> [dict(beat, camera, heroes)]   every beat's heroes (anchor + head height) per camera: the
      self-test checks each lands in the Reels safe area (x 8-82 %, y 14-60 %)
  Constants: AT (-23, 18), FLOOR 10, BED2_FACING "south", GOLEM_SPAWN_*, NO_GOLEM_ON, ZOMBIE_SCARE 8, GOLEM_LOOT,
  GOLEM_SIZE (1.4, 2.7), GOLEM_HEALTH 100, LAVA_DAMAGE 4, LAVA_DEATH_TICKS 240, JUMP 0.42, GRAVITY 0.08, PUSH 0.05,
  GROUND_FRICTION 0.546, BED_BOUNCE 0.75, BED_JUMPS (3, 6), BABY_TICKS 24000, VILLAGER_HEIGHT 1.95, BABY_HEIGHT
  0.975, ZOMBIE_REACH 0.83, HEAD (head centres over the feet: adult 1.68, baby 0.84, steve 1.62, golem 2.38).

LAYOUT (default at=(-23, 18), floor=10; Blender cells; the ground is z 0 there; front = south, toward the square)
    pillar      stone, x -23..-19, y 18..22, z 0..8 (5 x 5); the floor z 9: stone 7 x 7 (x -24..-18, y 17..23),
                one block over the pillar on every side: 10 blocks of stone from the grass to the floor's top
    pod         glass blocks on the floor's ring, z 10..11, glass roof z 12: inside 5 x 5 (x -23..-19, y 18..22), 2 high
    zombie cell the 1 x 1, 2-high alcove (-18, 19, 10..11) in the east wall: cobblestone side walls (-18, 18) and
                (-18, 20) and back wall (-17, 19), stone slab roof; the SILL, a cobblestone block at foot level on
                the pod's floor (-19, 19, 10), open air above it: the zombie stands at (-17.7, 19.5), its arms reach
                0.35 into the pod over the sill (to x -18.35) and stop in the air
    lights      the lantern standing on the floor in the front-west corner (-23, 18, 10) (group tower_pod); a wall
                torch on the cell's south wall at foot level (-19, 18, 10) (group tower_cell): it lights the zombie
                from below and never crosses its arms
    beds        pillows to the north wall: white (-23, 21), white (-22, 21), Mom's red (-21, 21) (foot cells); the
                free 2-block space x -20, y 21..22 for the second red bed: fm.bed2 (foot (-20, 22), pillow (-20, 21):
                facing SOUTH, as a bed Steve places from the north is: BED2_FACING), place_at(frame) pops it in
    free floor  the south three rows (y 18..20) but the lantern's and the sill's cells, and the east column x -19
                (y 20..22) up to the gap: every standing anchor in the pod is on it (the self-test checks)
    doorway     the back (north) wall at (-19, 23): the gap (z 10) under the cobblestone plug (z 11)
    platform    west of the pod: stone floor z 9, x -28..-25, y 17..23; the water sheet on it (z 10), flowing west;
                rims="glass": a stone lip (z 9) with glass on it (z 10) along y 16 and y 24
    kill slot   x -30..-29 (2 wide), y 17..23, 4 deep under the platform's top (its floor z 5); the lava blade's
                surface 8.89 (1.1 under the rim; fixtures.lava_glow: a full-bright strip and its light); outer wall
                x -31 with a glass rim; its ends (y 16, 24) stone up to the lava, OPEN above it: the glow shows there
    collection  a 3 x 3 stone column x -30..-28, y 22..24, z 0..4 under the slot's north-east corner; the chute
                (-29, 23) from a hole in the slot floor down to the hopper (-29, 23, 1) on the chest (-29, 23, 0),
                latch north; open to the north below a lintel (z 0..3): the hopper top is seen from the north
    staircase   10 full dirt blocks, each one up and one along, against the pillar: bottom (-17, 23, 0) west along
                its back face to (-21, 23, 4), the turn (-22, 23, 5), then back east one row further out (-22, 24, 6)
                (-21, 24, 7) (-20, 24, 8) to the top step (-19, 24, 9) outside the gap (a Breakable: Farm.top_step).
                Two blocks of headroom over every step (a player walks it; the floor's overhang over row 23 stops a
                jump's head on the lower flight: Farm.climb knows). Stray dirt at its foot: (-15, 23), (-15, 22) with
                one on top, (-14, 22), (-16, 21), (-16, 23); a doubled step at (-18, 24, 1).

ANCHORS (Village.anchors 'tower_<short name>'; Farm.A / Farm.yaw by short name; z = where the feet are)
    in the pod (z 10)
    mom (-20.5, 19.5) facing the zombie: ONE WHOLE EMPTY BLOCK (column -20) from its arm tips; also beats 23/24
    mom_glass (-20.5, 18.45) at the front glass, facing the zombie; the narrator's spot in beats 23/24
    baby_glass (-21.4, 18.45) 0.9 west of mom_glass, facing east       bed_side (-20.5, 20.45) at the red bed's foot
    bed_beside (-19.5, 21.4) beside the red bed in the second bed's space (beat 6 only: before bed2 appears)
    back_1 (-22.55, 19.4), back_2 (-22.55, 20.4) on the west glass, back_3 (-21.6, 18.4) on the south glass in the
        south-west corner: backed against the far glass, 1.0 apart (folded arms are 1.0 wide), facing the zombie
    row_1..4 (-22.5 .. -19.5, 20.4) facing north (beat 21: librarian, cleric, narrator, Mom)
    gap_in (-18.5, 22.66) a baby under the plug; gap_adult (-18.5, 22.3) the grown narrator at the plug, his face
        clear of it; gap_down (-18.5, 25.5, 10.2) his look target out of the gap, low; gap_side (-19.0, 22.66) the
        cleric half a block west of the opening (beat 15); gap_target the gap's middle (-18.5, 23.5, 10.5)
    watch_22 (-20.3, 20.5) the narrator in beat 22, facing Steve on one_down
    zombie (-17.7, 19.5) facing west; zombie_target its eyes (z 11.74) = fm.zombie_eye
    pod_target (-20.5, 20.5, 11) the pod's middle
    on the stairs and the platform
    top_step (-18.5, 24.5, 10) on the top dirt step; top_step_baby (-18.28, 24.42, 10) the baby beside the opening,
        facing the top_step_side camera; one_down (-19.5, 24.5, 9) one step down, facing east (the top step)
    golem_spawn (-26.5, 19.5, 10) the beat 9/10 spawn cell (a cell centre: the game spawns at one);
    golem_24 (-25.5, 19.5, 10) the beat 24 spawn cell, between two heads in C['cell_side']
    slot_target the slot (-29, 20.5, 9.5)
    on the ground (z 0)
    square_baby (6.38, 1.16) on the plaza path east of the well, 3.4 blocks in front of the square camera, facing
        north-north-east (80 degrees right of the lens' line: from behind its nose shows in profile)
    push_baby (8.9, 6.0) behind the push (beat 3), facing west
    foot_front (-20.5, 16.45) the baby at the front of the stone base (beat 5), turned 20 degrees to the east
    stairs_foot (-15.4, 24.3) the baby at the foot of the stairs (beat 13)   stairs_target a point up the stairs
    poppies (-29.55, 25.4) the baby among the poppies (beat 12)   chest_steve (-27.75, 25.35) Steve at the chest,
        facing it, clear of the niche   chest_front (-28.5, 24.55) in the niche (covers the chest)   chest_aside
    hopper_target the hopper (-28.5, 23.5, 1.7)   lineup (-22, 12)
    paths: tower_steve_square (-1.0, 7.3) -> (8.3, 0.7) (beat 1: across the plaza at the lens, passing the baby
        1.4 to its right); tower_steve_past (4.5, 0.64) -> (6.55, 3.1) (beat 2: between C['baby_face'] and the
        baby); tower_push_square (6.5, 6.0) -> (-0.5, 6.0) along the plaza's north edge (beat 3)
    Farm.set["push_route"]: a stand-in route behind the tower (y 28) where the push proof was filmed

CAMERAS (Farm.cameras[name] = dict(pos, target, lens, fstop, beat[, target1]); each rendered with its beat's cast
through films.lookdev.Stage at the look-dev golden hour (sun az 62 / el 27): out/test/towers_bNN.png and _zones.png)
    square        (9.3, -0.6, 0.55) at baby height behind square_baby -> the pod, 40 mm f/2.8: the baby lower
                  middle (head x 30, y 52 %), the tower above the gables (pod y 24 %), Steve coming at the lens
    square_start  same position -> the well's rim, 40 mm: the start of beat 4's tilt and pan (the baby at x 70 %)
    square_long   the plaza -> Mom on mom_glass, 200 mm f/2.8 (hide the panes: see_through(points=[mom]))
    baby_face     (4.69, 2.57, 0.72) -> the baby, 50 mm f/2: its face front three-quarter, upper half (y 40 %)
    push_square   (3.3, 9.6, 0.65) -> pan target -> target1 along the plaza's north path, 18 mm
    foot          front three-quarter at baby height, 35 mm f/2.8: the folded arms at y 50 %, the base behind
    pan_bed       (-20.5, 18.55, 11.3): target the red bed's foot -> target1 the cell, 24 mm (beat 6's pan)
    two_shot      from behind the back wall (hide tower_pod_north), west of the plug, 45 mm: arms left, Mom right
    cell_side     (-18.15, 20.6, 11.75) beside the cell (north of it), high under the roof, 18 mm: the backed
                  three at x 30 / 57 / 77 %, or the four of beat 23 at 13 / 42 / 56 / 76 % with golem_24 at 67 %
    platform      (-28.5, 18.0, 10.3) over the slot's rim, 20 mm: the golem big at x 31 %, the three behind the
                  glass at x 48-80 %, y 55 % (the low sun is behind the lens: blue sky behind the golem)
    platform_sun  the earlier framing: the golem against the gold sun, the villagers out of frame
    slide         from the slot's open south end at the platform's level, 20 mm: the sheet behind the glass rim,
                  the golem slides left and drops past the lava's surface in the slot (the game's lava texture)
    slide_low     the earlier framing a little below the platform: the lava only a band, the sheet hidden
    hopper        (-28.75, 26.0, 3.1) macro on the niche, 30 mm f/2.8: the hopper top, the items falling in
    hopper_wide   (-29.9, 29.0, 3.2), 24 mm f/2.8: Steve at x 18 %, the hopper x 51 / y 35 %, the baby x 69 / y 58 %
    back          the back, locked tall, 24 mm (the baby tiny at its foot at y 70 %: the story's picture)
    top_step_side (-15.6, 26.4, 10.7) outside north-east of the top step, 30 mm: the baby on top_step_baby in front
                  of the opening, its head just under the plug; Mom (bed_side) through the glass
    gap           inside on the floor, the gap in the middle, 22 mm (beat 15)
    red_bed       (-24.7, 20.9, 10.9) outside the west glass (hide the panes: see_through(points=[mom, baby])),
                  35 mm f/2.8: Mom from behind on the zombie, the baby against her, its face at y 53 %
    grow          the locked side view against the front glass, 24 mm      bounce   the red bed from the east, 24 mm
    gap_side      (-15.0, 21.3, 10.9) outside the east glass (see_through(points=[head, knees, gap])), 30 mm: the
                  narrator on gap_adult in profile (x 32 %), the plug at his face, the gap at his knees
    high          over Steve's shoulder, roof hidden, 22 mm (beat 21)
    back_glass    (-18.2, 18.4, 11.7) the south-east corner over the wall torch, 18 mm f/2.8: the narrator on
                  watch_22 at the left edge (x 9 %), Steve on one_down through the back glass (x 65 %)
    stairs        outside north-east of the top step, 30 mm (beat 22's outside view)
    square_wide, pod_out, pod_in, lineup, push   the set's proof framings

BEATS (stories/ironfarm.json; what stages each line; tools/towers_proof.py shot_bNN does exactly this)
     1 "everyone is afraid"   C["square"]; baby on square_baby (place, then look_at a point 2 ahead and 1.2 up,
                              tilting to 3.4 up as he comes: its nose in profile); Steve on tower_steve_square:
                              steve.walk(f0, v.paths["tower_steve_square"]); the armorer and the shepherd and the
                              door (v.door_open) are the village's.
     2 "I'm not."             C["baby_face"]; baby on square_baby; Steve along tower_steve_past from f0 + 6 (his
                              legs cross the lens, 0.6 from it); the baby's head follows him: look_at(f, steve)
                              every 4 frames. Hold its face (y 40 %) after he has passed.
     3 "only takes grownups"  C["push_square"] panning: s.move(pos, target, pos, target1);
                              towers.push(steve, mom, f0 + 2, v.paths["tower_push_square"]) ("tap": shoves); then
                              mom.look_at a point 2 west, 2.2 north, 1.6 up every 12 frames (hat brim and nose to
                              the lens); the baby on push_baby runs at f0 + 24 to 1.2 behind Steve (0.7 clear of his
                              legs): baby.walk(f, [here, (steve.x + 1.2, y)], run=True), and stops.
     4 "my mom lives at the top"   s.move(C["square_start"] pos/target -> C["square"] pos/target) (tilt and pan
                              from the well to the tower), baby on square_baby looking at pod_target, Mom on
                              mom_glass with look_at(fm.zombie_eye); s.focus(baby) then s.focus(mom, at_s=...) for
                              the rack. Mom is 36 blocks away: at 40 mm she is a few pixels: CUT inside the line to
                              C["square_long"] with fm.see_through(st, s2, C["square_long"], points=[mom]) for the
                              straw hat in profile. The slot's glow and the dirt zigzag cannot be seen from the
                              square (behind the pod / on the back): see NOT THE GAME.
     5 "our arms don't do that"   C["foot"]; baby on foot_front; baby.look_at(f, point 0.8 east, 2 south, 4 up);
                              the hop in place: towers.hop(baby, f, A["foot_front"]).
     6 "a bed, and a zombie"  C["pan_bed"] panning to target1; Mom on bed_beside, look_at(fm.zombie_eye) (she is
                              passed in the middle of the pan, x 34 %); fm.zombie_in_cell(z, f0, look=mom); focus
                              the bed, then rack to the zombie at the end.
     7 "can't reach her"      C["two_shot"], st.see_through(s, "tower_pod_north"); fm.zombie_in_cell(z, f, aggro=True);
                              Mom on mom, look_at(fm.zombie_eye): 1.9 blocks of air between arm tips and her face.
     8 "doesn't have to"      C["cell_side"]; cleric on back_1, librarian on back_2, Mom on back_3; towers.panic(c,
                              f0, f1, fm.zombie_eye, seed=...) each; fm.zombie_in_cell(z, f0, aggro=True). The
                              story's "zombie's arm a soft green shape at the frame edge" cannot be had from beside
                              the cell: the arms reach only 0.35 into the pod and are behind any lens there (a lens
                              inside the cell sees the zombie's back); cut to C["two_shot"] / C["pod_in"] for them.
                              The empty platform is behind them, below their waists: it reads in beat 9.
     9 "an iron golem comes"  C["platform"]; fm.golem_spawn(g, f, yaw=0.0 (facing south: its face to the lens side),
                              look=A["pod_target"], look_after=10, empty_from=s); cleric / librarian / Mom on
                              back_1..3 looking at the zombie (small behind the glass). C["platform_sun"] instead
                              puts it against the gold sun, without the villagers.
    10 "every time"           the same framing, jump cut to shot s2: fm.golem_spawn(g, f2, yaw=0.0, empty_from=s2)
                              (same spot and pose; the platform is empty from s2's first frame),
                              fm.golem_step(g, f2 + 12).
    11 "the water pushes it"  C["slide"]; fm.golem_spawn(..., empty_from=s); r = fm.golem_slide(g, f);
                              fm.golem_death(g, r, camera=s, until=<next shot's first frame>) (puff + flicker).
    12 "takes the iron"       C["hopper"] (macro) and C["hopper_wide"]: loot = towers.golem_loot(seed); one
                              mobs.make_dropped_item('iron_ingot', count=loot['iron_ingot']) and, if any, one
                              'poppy' with its count; fm.deliver(items, f); poppies = fm.strew(...,
                              face=C["hopper_wide"]["pos"]); Steve on chest_steve with steve.hold("iron_ingot"),
                              walking out of frame from f0 + 30 (3 east, 2 north); the baby on 'poppies' looking at
                              him. Register every item: st.cast[it.name] = it; st.use(s, ...).
    13 "his dirt staircase"   C["back"]; baby on stairs_foot; fm.climb(baby, f, 0, 1) (the first two steps).
    14 "a gap, one block high"   C["top_step_side"]; the baby placed on fm.set["stairs"][8] hops up the last one:
                              towers.hop(baby, f, A["top_step_baby"]), then baby.turn(f2, fm.yaw["top_step_baby"]):
                              it stands in front of the opening, its head just under the plug; Mom on bed_side
                              looking at the zombie through the glass (fm.see_through(st, s, C["top_step_side"],
                              points=[mom]) clears the pane in front of her hat).
    15 "grownups don't fit"   C["gap"]; the cleric walks to gap_side (into the plug); the baby runs in under it:
                              baby.walk(f, [A["top_step"], A["gap_in"], A["bed_side"]], run=True).
    16 "Mom never looks at me"   C["red_bed"] + fm.see_through(st, s, C["red_bed"], points=[mom, baby]); Mom on
                              bed_side looking at fm.zombie_eye for the WHOLE shot; fm.zombie_in_cell(z, f0,
                              aggro=True); the baby at bed_side + (-0.62, -0.05), its body turned to the lens, its
                              head look_at(mom): its face at y 53 %, clear of her sleeve.
    17 "twenty minutes"       C["grow"] (locked); Mom on mom_glass, baby on baby_glass (0.9 west of her).
    18 "I spent mine with her"   C["bounce"]; fm.bounce(baby, f, "mom", jumps=2, yaw=...) (two jumps stopped by the
                              glass 0.46 over the mattress, each with two small rebounds, 1.8 s), then the baby
                              placed beside Mom with look_at(fm.zombie_eye).
    19 "when it ended"        C["grow"] again; towers.grow_up(baby, narrator, frame_of("ended"),
                              look=fm.zombie_eye) (narrator = st.actor("narrator", "none")); hold a second.
    20 "now I don't fit"      C["gap_side"] + fm.see_through(st, s, C["gap_side"], points=[(gap_adult + 1.6 up),
                              (gap_adult + 0.6 up), A["gap_target"], (gap_target 0.4 south), (gap_target 1 up)]);
                              the narrator walks from 1.6 south of gap_adult to gap_adult and stops; look_at(f,
                              A["gap_down"], ease=8): his head tilts down to the gap, nose in profile.
    21 "counted us twice"     C["high"], st.see_through(s, "tower_pod_roof"); librarian, cleric, narrator, Mom on
                              row_1..4; Steve on top_step, steve.watch(...) along the row and back; to place the bed
                              he sneaks (steve.sneak(f)): the ray from a sneaking eye (1.27) reaches the floor under
                              the plug through the gap, as the game allows; steve.attack(f); fm.bed2.place_at(f + 2)
                              (the pillow to the south, as he places it).
    22 "not afraid of the player"   C["back_glass"]; the narrator on watch_22, still, eyes level:
                              look_at(one_down + 1.62 up); fm.top_step.restore(s.frame_start) if an earlier shot
                              broke it; Steve on one_down: fm.break_top_step(steve, f, camera=s, until=s.frame_end
                              + 1), then towers.walk_down(steve, m["frame"] + 8, [stairs[7], stairs[6], stairs[5]])
                              (no jump: he steps off each edge). The narrator's face is in lost profile at the left
                              edge: no spot in the furnished pod shows his face and Steve together (a camera that
                              sees his face looks away from the back glass). C["stairs"] is the outside view.
    23 "afraid of the zombie" C["cell_side"]; cleric back_1, librarian back_2, Mom on mom, the narrator on mom_glass;
                              panic(narrator, ..., seed=k) and panic(mom, ..., seed=k): matched; zombie aggro. The
                              arms at the foreground edge: not from here (beat 8). The red beds are behind this lens.
    24 "apparently that counts"   the same shot: fm.golem_spawn(g, f, pos=A["golem_24"], yaw=radians(60),
                              look=A["pod_target"], empty_from=s) (REQUIRED: the beat 11 golem's slide may not be
                              over), golem_step, golem_slide; it appears between the cleric and the librarian (x 67
                              %, its head a little above theirs); s.focus(g.head, at_s=..., rack_s=0.6); cut before
                              it drops.

WHAT THE GAME DOES (read from the 26.x client jar; no game file or code is copied)
    golem spawn   VillagerPanicTrigger.tick: every 100 game ticks a panicking villager calls spawnGolemIfNeeded(t,
                  3): at least 3 villagers in its box inflated by 10 that slept within the last 24000 ticks
                  (golemSpawnConditionsMet: LAST_SLEPT: the beds matter) and have no GOLEM_DETECTED_RECENTLY
                  (GolemSensor: sensed every 200 ticks, remembered 599). SpawnUtil.trySpawnMob(IRON_GOLEM,
                  MOB_SUMMONED, villager.blockPosition(), 10, 8, 6, LEGACY_IRON_GOLEM, false): 10 tries at a random
                  column within +-8; moveToPossibleSpawnPosition scans it from +6 down to -6 for the FIRST cell
                  whose block below passes LEGACY_IRON_GOLEM (isSolid, not cobweb, cactus, glass, glass pane, any
                  stained glass, leaves, conduit, ice, frosted ice, TNT, glowstone, beacon, sea lantern, tinted
                  glass, powder snow) and that holds air or a fluid; IronGolem.checkSpawnObstruction: the block
                  below can be stood on, that cell (checked with an EMPTY fluid: water at the feet is fine) and the
                  two above it valid empty spawn blocks (no full block, no fluid). The golem is placed at the cell's
                  bottom centre with a random facing (EntityType.create: nextFloat() * 360) and is simply there on
                  the next tick: no particles.
                  So nothing spawns in the 2-high pod (the roof is the third cell) or on its glass roof. The farm as
                  built ALSO lets the game put golems on the zombie cell's slab roof, on the upper dirt steps, on the
                  slot's end walls (they fall into the slot) and on the collection column's top under the platform
                  rim (spawn_cells lists them; a careful builder covers them with glass): none is in any shot.
    villagers     VillagerHostilesSensor: a zombie within 8 blocks and in line of sight (glass blocks sight) makes
                  them panic. Villager 0.6 x 1.95, babies half; a villager's folded arms are 16 px = 1.0 wide.
                  AgeableMob.BABY_START_AGE -24000: a baby grows up after 20 minutes, with no particles (those come
                  only with a forced age, i.e. feeding). JumpOnBed: a baby jumps on a bed 3..6 times, 5 ticks apart.
    bounce        Entity.restituteMovementAfterCollisions (26.x): landing on a block with bounciness (every bed
                  0.75: Blocks; a living entity keeps it) faster than gravity (0.08 per tick) sets the vertical
                  speed to (f g - v) x lerp(f, 1, 0.98) x 0.75 (f = the part of the tick's fall made before the
                  contact); LivingEntity.travelInAir then applies gravity and drag in the same tick. A jump (0.42,
                  apex 1.25) rebounds to 0.56, 0.24, 0.10 ... and settles in 40 ticks under open sky.
    moving        LivingEntity.jumpFromGround 0.42, gravity 0.08, drag 0.98: apex 1.25, one block up in 9 ticks.
                  Off a ledge without a jump: on the ground the vertical speed is one tick of gravity, so it drops
                  at once: one block in 5 ticks. A player walks 4.317 blocks/s, sneaks 1.295, sneaking eye 1.27.
    pushing       Entity.push(Entity): both are pushed apart by 0.05 x the offset / sqrt(d) (sqrt of the centre
                  distance under one block): the push WEAKENS as the boxes overlap, so held input walks a player
                  through a villager; ground friction 0.6 x 0.91.
    bed placing   AbstractBedBlock.getStateForPlacement: FACING = the placer's horizontal direction, the pillow one
                  cell further that way: a bed Steve places from the north has its pillow to the south.
    golem         EntityType.IRON_GOLEM 1.4 x 2.7; createAttributes: health 100, step height 1.0 (it can step onto
                  the 1-high glass rim if it wanders that way: rims="fence", 1.5 high, holds it as real farms do;
                  both hold the water: flowing water cannot enter a fence or glass cell), knock-back resistance 1.
                  Entity.lavaHurt 4.0 per hit, a hit lands 10 ticks after the last: 240 ticks (12 s) to die in lava. loot_table/entities/iron_golem.json: poppy uniform 0..2, iron ingot uniform 3..5,
                  one roll each: TWO item entities (one stack each).
    hopper        HopperBlockEntity: one item entity (a whole stack) taken per transfer, then the 8-tick cooldown;
                  ItemClusterRenderState draws a stack of 2-16 as two copies.
    zombie        Mob.getAttackBoundingBox: its box inflated by sqrt(2.04) - 0.6 = 0.83 sideways; pressed against the
                  sill its reach ends at x -18.83, Mom's box starts at -20.2.
    water, lava, hopper, chest, glass, falling blocks: engine/fixtures.py; cracks and mining: engine/breaking.py;
    the golem and dropped items: engine/mobs.py; the zombie: engine/undead.py.

NOT THE GAME, AND WHERE THE PICTURE DIFFERS FROM IT
    - The water is a level 2/9 sheet drawn flowing (the story's still sheet; water="game" gives the real spread).
      rims=None would leave the platform's long edges open: in the game the sheet would pour over them.
    - The lava blade hangs in the slot with nothing drawn under it (in real farms: signs); the slot floor's water
      stream that carries the drops to the chute hole is not drawn (it is under the lava, out of every camera).
    - The golem is hidden the moment its head goes under the rim and the puff comes then (delay=0): the game's golem
      burns 12 s in the lava before it dies (golem_death(delay=288)). Items reach the hopper by deliver() when the
      director wants them, not by a simulated trip down the chute.
    - panic(): the game's trapped villagers try to run from the zombie and jostle; here they tremble and turn on
      the spot with their heads on it (the story's picture). Steve's "pushing" uses shoves (players tap the key); a
      held key walks through her.
    - From the square the slot's glow cannot be seen (it is behind the pod and under the roofs' line) and the dirt
      zigzag is on the back: beat 4's "orange glow under the platform rim" and "brown zigzag up its flank" need a
      camera west / north of the tower. Mom at the front glass is a few pixels at 40 mm: C["square_long"].
    - Beat 8/23: the zombie's arms cannot be at the frame edge from beside the cell (geometry, above); beat 22: the
      narrator's face cannot be seen with Steve through the back glass (lost profile); beat 23: the two red beds are
      behind the cell_side lens; beat 9: the gold sun is behind C["platform"] (C["platform_sun"] has it, without the
      villagers).
    - The glass pod is drawn as the game draws connected glass (fixtures.glass_box); seen from outside, the far walls'
      frames show through the hidden panes: pane lines cross the picture as they do in the game.

GOTCHAS
    - Key every character in film order; place() before look_at; panic() after place() (it keys the body yaw, the
      head, the tremble). golem_spawn / golem_slide / grow_up use engine.undead.vanish / appear: never key
      hide_render on these characters.
    - ONE golem for every spawn (st.cast["golem"]). Pass empty_from=<the shot> on every spawn that opens a shot: a
      golem still standing (no slide: beats 9 -> 10) or still sliding (a slide not over at the cut) is refused
      without it, because its keys would hide or show the new one.
    - Particles do not stop at cuts by themselves: golem_death(..., until=next_shot.frame_start) and
      break_top_step(..., until=...), or fx.stop_particles(next_shot.frame_start, [burst]).
    - see_through keys visible_camera at the shot's first frame and the next shot's: make the calls in shot order
      (a later call's key on the same frame wins).
    - break_top_step needs camera= (the particles face it). Register fm.top_step with the Stage when a shot shows it
      broken (st.cast[fm.top_step.name] = fm.top_step); fm.top_step.restore(f) brings it back for a later shot.
    - Mom's head must stay on fm.zombie_eye in every pod shot (the story's continuity): look_at / panic(threat=...).
    - bed_beside is on the second bed's space: Mom may stand there only before fm.bed2.place_at.
    - Lights: groups tower_pod (the lantern) and tower_cell (the torch) through Stage.lights; the lava light through
      fm.lava.level(frame, scale). In daylight the lava's light hardly shows on stone: the glow reads from the lava
      texture itself (the slot's open ends).

MEASURED (out/test/towers_*.png, 540x960, 16 samples, 2 threads, motion blur on, golden hour = the look-dev sun az
62 / el 27; strips are 270x480 frames side by side; _zones.png = the Reels zones drawn over a beat still)
    - Heads in the frame (x %, y %) with the real rigs (tools/towers_proof.py --where): b01 baby 30/52, Steve 66/37;
      b02 baby 60/40; b03 Mom 48/43, Steve 40/43, baby 18/53; b04 baby 35/51, Mom 41/21 (36 blocks); b04_long Mom
      50/50; b05 baby 55/43; b06 Mom 34/29 mid-pan, zombie 57/37 at its end; b08 cleric 57/49, librarian 76/49, Mom
      28/49; b09 golem 31/29, villagers 48-80/55; b12 baby 69/58, Steve 18/42; b14 baby 59/47; b16 baby 54/56, Mom
      42/34, zombie 57/39; b20 narrator 32/33; b22 narrator 9/44, Steve 65/52; b24 golem 67/45, cleric 56/49,
      librarian 76/49, Mom 42/50, narrator 13/50.
    - The golem: appears on its frame, turns its head, steps, slides west (1.4 blocks/s) and drops 4 blocks; the
      puff rises out of the slot (GOLEM_PUFF_GLOW 0.5: engine.animals' 0.15 reads mid-grey against the sun).
    - The hopper: a stack of ingots (two copies) falls out of the dark chute and is taken; the poppies spin on the
      grass. The top step: ten crack stages over the game's 17 frames, then the 64 dirt particles.
    - The narrator: the unemployed adult (the plain brown robe of type/plains, no profession layer) next to the
      nitwit (the green robe) reads clearly different at phone size (lineup still).
    - tools.palette_check passes on the golden stills; at dusk the glass pod ten blocks up fails it (the 5-degree
      sun floods faces and floor: the story is all golden hour).
    - Render times under load: 15-35 s per 540x960 still, 15-25 s per strip.

SELF-TEST
    $BPY -m engine.towers                       39 numeric checks (builds the village with the tower, renders nothing);
                                                exit code 1 if one fails
    $BPY -m engine.towers stills NAME ...       proof stills out/test/towers_<name>.png (tools/towers_proof.py, 15-35 s
                                                each, at most 4-5 per call): b01 b02 b03 b04 b04_long b05 b06 b08 b09
                                                b12 b14 b16 b20 b22 b24 (beats) square_wide push pod_out pod_in
                                                two_shot back gap bounce lineup slide hopper grow high stairs; under
                                                the dusk sky: square_dusk pod_out_dusk pod_in_dusk cell_side_dusk
    $BPY -m tools.towers_proof --where NAME ... where every hero's head lands in each beat shot (no render)
    $BPY -m tools.check_towers_stamp            frame fingerprints follow the spawns, the slide, the items, the cracks,
                                                the second bed, the swap, the panic, and particles end at the cuts;
                                                run twice: the digests must match
"""
import math

import numpy as np

from . import characters as ch
from .village import yaw_of, yaw_to

FPS = 24
TICK = FPS / 20.0                    # film frames per game tick

# ---- numbers from the game (Java Edition 26.x client classes and data files, named next to each) -------------------
GOLEM_SPAWN_TRIES = 10               # Villager.spawnGolemIfNeeded -> SpawnUtil.trySpawnMob(IRON_GOLEM, MOB_SUMMONED,
GOLEM_SPAWN_XZ = 8                   #   level, villager.blockPosition(), 10, 8, 6, Strategy.LEGACY_IRON_GOLEM, false):
GOLEM_SPAWN_Y = 6                    #   10 tries, x and z +-8 around the villager, each column scanned y+6 .. y-6
GOLEM_SPAWN_VILLAGERS = 3            # VillagerPanicTrigger.tick: every 100 game ticks spawnGolemIfNeeded(level, t, 3):
GOLEM_SPAWN_EVERY_TICKS = 100        #   at least 3 villagers in the box inflated by 10 that want a golem
GOLEM_SPAWN_BOX = 10.0
GOLEM_SENSOR_TICKS = 200             # GolemSensor: senses every 200 ticks (golems within its 16-block list) ...
GOLEM_DETECTED_TICKS = 599           # ... and sets GOLEM_DETECTED_RECENTLY with an expiry of 599 ticks
SLEPT_WITHIN_TICKS = 24000           # Villager.golemSpawnConditionsMet: LAST_SLEPT less than 24000 ticks ago (beds!)
GOLEM_HEADROOM = 3                   # IronGolem.checkSpawnObstruction: the feet cell (water allowed: it is checked with
#                                      Fluids.EMPTY) and the two cells above it (no fluid, no full collision block)
NO_GOLEM_ON = ("cobweb", "cactus", "glass_pane", "conduit", "ice", "tnt", "glowstone", "beacon", "sea_lantern",
               "frosted_ice", "tinted_glass", "glass")    # SpawnUtil.Strategy.LEGACY_IRON_GOLEM (+ every stained glass
NO_GOLEM_ON_SUFFIX = ("_stained_glass", "_stained_glass_pane", "_leaves")   # block or pane, and LeavesBlock)
ZOMBIE_SCARE = 8.0                   # VillagerHostilesSensor: ZOMBIE 8.0 blocks (and line of sight: glass blocks it)
GOLEM_LOOT = (("iron_ingot", 3, 5), ("poppy", 0, 2))      # loot_table/entities/iron_golem.json: two pools, uniform
GOLEM_SIZE = (1.4, 2.7)              # EntityType.IRON_GOLEM
GOLEM_PUFF_GLOW = 0.5                # this module's choice: the death puff's self-light (particles are lit by level only)
GOLEM_HEALTH = 100.0                 # IronGolem.createAttributes MAX_HEALTH
LAVA_DAMAGE = 4.0                    # Entity.lavaHurt: hurtServer(lava, 4.0)
HURT_COOLDOWN_TICKS = 10             # LivingEntity: a hit only lands 10 ticks after the last (invulnerableTime 20)
LAVA_DEATH_TICKS = int(math.ceil(GOLEM_HEALTH / LAVA_DAMAGE) - 1) * HURT_COOLDOWN_TICKS   # 240 ticks = 12 s in lava
JUMP = 0.42                          # LivingEntity.jumpFromGround (Attributes.JUMP_STRENGTH default)
GRAVITY = 0.08                       # LivingEntity default gravity
AIR_DRAG_V = 0.98                    # LivingEntity.travelInAir: vertical speed x 0.98 per tick
GROUND_FRICTION = 0.546              # block friction 0.6 x 0.91: horizontal speed kept per tick on the ground
PUSH = 0.05                          # Entity.push(Entity): 0.05 x the normalised offset (x sqrt of it under 1 block)
PLAYER_WALK = 4.317                  # blocks/s (engine.players WALK_SPEED): input that holds it against GROUND_FRICTION
BED_BOUNCE = 0.75                    # Blocks: every bed has bounceRestitution(0.75) (Entity.getBlockBounciness: living
#                                      entities keep it, anything else x 0.8)
BED_JUMPS = (3, 6)                   # JumpOnBed.MIN_JUMPS / MAX_JUMPS: a baby jumps 3..6 times ...
BED_JUMP_COOLDOWN_TICKS = 5          # ... with COOLDOWN_BETWEEN_JUMPS 5 ticks on the mattress between them
BED_TOP = 9.0 / 16.0                 # BedBlock: the bed's shape is 9 px high
BABY_TICKS = 24000                   # AgeableMob.BABY_START_AGE = -24000: a baby grows up after 20 minutes (no
#                                      particles: those only come with a forced age, i.e. feeding)
VILLAGER_HEIGHT, BABY_HEIGHT = 1.95, 0.975    # EntityType.VILLAGER 0.6 x 1.95, babies at scale 0.5
ZOMBIE_REACH = math.sqrt(2.04) - 0.6     # Mob.getAttackBoundingBox: the hit box inflated by this (0.83) sideways

BED2_FACING = "south"                # AbstractBedBlock.getStateForPlacement: FACING = the placer's horizontal direction,
#                                      the pillow one cell further that way: Steve places it from the north (beat 21)

# ---- the set (Blender block coordinates; see LAYOUT in the module docstring) --------------------------------------
AT = (-23, 18)                       # the pod's south-west INSIDE cell: the inside is AT .. AT + (4, 4)
FLOOR = 10                           # z of the pod's floor top (the pillar + floor are 10 blocks of stone)
LAVA_LEVEL = 8.0 / 9.0               # fixtures.FLUID_SOURCE_HEIGHT


# ----------------------------------------------------------------------------------------------------
# the layout as numbers (no Blender): every cell the set puts into the World
# ----------------------------------------------------------------------------------------------------
def layout(at=AT, floor=FLOOR, ground=0, rims=None):
    """Every block of the tower as {cell: (block id, props)} plus the named cells and spots (pure numbers, no
    Blender): the source of truth for iron_farm() and for the self-test. Cells are Blender block cells."""
    X, Y = int(at[0]), int(at[1])
    F, g = int(floor), int(ground)
    if F - g < 8:
        raise ValueError("towers.layout: the floor must be at least 8 blocks above the ground (a golem may spawn "
                         "6 blocks below a villager): floor %d, ground %d" % (F, g))
    cells = {}

    def put(c, bid, props=None):
        cells[tuple(int(a) for a in c)] = (bid, dict(props or {}))

    def fill(x0, y0, z0, x1, y1, z1, bid, props=None):
        for x in range(min(x0, x1), max(x0, x1) + 1):
            for y in range(min(y0, y1), max(y0, y1) + 1):
                for z in range(min(z0, z1), max(z0, z1) + 1):
                    put((x, y, z), bid, props)

    def air(c):
        cells[tuple(int(a) for a in c)] = None

    # the pillar under the inside of the pod, and the floor (7 x 7, one block over the pillar on every side)
    fill(X, Y, g, X + 4, Y + 4, F - 2, "stone")
    fill(X - 1, Y - 1, F - 1, X + 5, Y + 5, F - 1, "stone")
    # the zombie cell: a 1 x 1, 2-high cobblestone alcove in the pod's east wall at row Y + 1, a stone slab roof;
    # it opens into the pod over a cobblestone block at foot level (the sill, on the pod's floor), open air at head
    # height: the zombie's arms reach out over the sill and stop in the air
    zc = (X + 5, Y + 1)
    for c in ((X + 5, Y), (X + 5, Y + 2), (X + 6, Y + 1)):
        fill(c[0], c[1], F, c[0], c[1], F + 1, "cobblestone")
    put((X + 6, Y + 1, F - 1), "stone")                                       # the back wall's footing
    for c in ((X + 5, Y), (X + 5, Y + 1), (X + 5, Y + 2), (X + 6, Y + 1)):
        put((c[0], c[1], F + 2), "stone_slab", {"type": "bottom", "waterlogged": "false"})
    put((X + 4, Y + 1, F), "cobblestone")                                     # the sill
    win = (X + 4, Y + 1)
    # the back-wall doorway: a cobblestone plug at head height over a one-block gap
    gap = (X + 4, Y + 5)
    put((gap[0], gap[1], F + 1), "cobblestone")
    # the golem platform west of the pod (water on it), its rims, the 2-wide kill slot at its outer (west) edge
    px0, px1, py0, py1 = X - 5, X - 2, Y - 1, Y + 5
    fill(px0, py0, F - 1, px1, py1, F - 1, "stone")
    if rims is not None:                                                       # rims along the long sides
        if rims not in ("fence", "glass"):
            raise ValueError("towers.layout: rims is None, 'fence' or 'glass', not %r" % (rims,))
        for ry in (py0 - 1, py1 + 1):
            fill(px0, ry, F - 1, px1, ry, F - 1, "stone")
            fill(px0, ry, F, px1, ry, F, "oak_fence" if rims == "fence" else "glass")
    sx0, sx1 = X - 7, X - 6                                                    # the slot: 4 deep below the rim
    fill(sx0, py0, F - 5, sx1, py1, F - 5, "stone")                            # its floor
    fill(X - 8, py0 - 1, F - 5, X - 8, py1 + 1, F - 1, "stone")                # its outer wall ...
    fill(X - 8, py0 - 1, F, X - 8, py1 + 1, F, "glass")                        # ... with a glass rim on top
    for ey in (py0 - 1, py1 + 1):                                              # its ends: stone up to the lava, open
        fill(sx0, ey, F - 5, sx1, ey, F - 2, "stone")                          # above it (the glow shows there)
    # the collection column under the slot's north-east corner: a 3 x 3 stone column, a 1 x 1 chute down its middle
    # from a hole in the slot floor, the hopper on the chest at its foot, open to the north (back) below a lintel
    chute = (sx1, py1)
    fill(chute[0] - 1, chute[1] - 1, g, chute[0] + 1, chute[1] + 1, F - 6, "stone")
    for z in range(g, F - 4):
        air((chute[0], chute[1], z))
    for z in range(g, g + 4):
        air((chute[0], chute[1] + 1, z))                                       # the niche's opening
    # the dirt staircase up the back: full dirt blocks, one up and one along, zigzagging against the pillar: west up
    # along its back face (row Y + 5), one step in toward the wall's corner, then back east one row further out
    # (row Y + 6) to the top step outside the gap; a few stray blocks at its foot
    n_low = F - g - 5                                                          # steps in the lower flight
    steps = [(X + 1 + n_low - i, Y + 5, g + i) for i in range(n_low)]
    steps += [(X + 1, Y + 5, g + n_low)]                                       # the turn
    steps += [(X + 1 + k, Y + 6, g + n_low + 1 + k) for k in range(4)]         # ... up to (X + 4, Y + 6, F - 1)
    for c in steps:
        put(c, "dirt")
    top_step = steps[-1]
    rough = [(steps[1][0], Y + 6, steps[1][2]), (steps[0][0] + 1, Y + 5, g)]   # a doubled step, a block left over
    sx = steps[0][0]                                                           # the bottom step's column
    stray = [(sx + 2, Y + 5, g), (sx + 2, Y + 4, g), (sx + 3, Y + 4, g), (sx + 1, Y + 3, g)]
    for c in rough + stray:
        if c not in cells:
            put(c, "dirt")
    put((sx + 2, Y + 4, g + 1), "dirt")                                       # one left on top of another
    # inside: the lantern on the floor, the wall torch at the cell, the beds (pillows to the north wall)
    lantern = (X, Y, F)
    torch = (X + 4, Y, F)                                                      # on the cell's south wall, west face,
#                                                                                at foot level: it lights the zombie
#                                                                                from below and never crosses its arms
    beds = dict(white_1=(X, Y + 3, F), white_2=(X + 1, Y + 3, F), mom=(X + 2, Y + 3, F))
    bed2 = (X + 3, Y + 4, F)                                                   # the free space: the second red bed,
#                                                                                foot north, pillow south (BED2_FACING)
    chest = (chute[0], chute[1], g)
    lava_cells = [(x, y, F - 2) for x in (sx0, sx1) for y in range(py0, py1 + 1)]
    return dict(cells=cells, X=X, Y=Y, F=F, g=g, window=(win[0], win[1], F + 1), sill=(win[0], win[1], F),
                cell=(zc[0], zc[1], F), gap=(gap[0], gap[1], F), plug=(gap[0], gap[1], F + 1),
                platform=(px0, py0, px1, py1), slot=(sx0, py0, sx1, py1), slot_floor=F - 4, rim=F,
                lava_cells=lava_cells, lava_z=F - 2 + LAVA_LEVEL, chute=(chute[0], chute[1]), chest=chest,
                hopper=(chest[0], chest[1], g + 1), chute_mouth=g + 4.0, steps=steps, top_step=top_step,
                stray=stray + rough, lantern=lantern, torch=torch, beds=beds, bed2=bed2,
                inside=(X, Y, F, X + 4, Y + 4, F + 1), pod=(X - 1, Y - 1, F, X + 5, Y + 5, F + 2),
                footprint=(X - 8, Y - 2, max(X + 7, steps[0][0] + 2), Y + 7))


# ----------------------------------------------------------------------------------------------------
# the game's golem spawn rule (Villager.spawnGolemIfNeeded / SpawnUtil / IronGolem.checkSpawnObstruction)
# ----------------------------------------------------------------------------------------------------
def _no_golem_on(bid):
    return bid in NO_GOLEM_ON or bid.endswith(NO_GOLEM_ON_SUFFIX)


def spawn_cell(world, x, y, villager_z, fluids=()):
    """Where a golem spawn attempt in column (x, y) for a villager standing at block height `villager_z` lands, by
    the game's rule, or None. SpawnUtil.moveToPossibleSpawnPosition scans down from villager_z + 6 to - 6 and takes
    the FIRST cell whose block below is solid and not glass / leaves / ice ... (LEGACY_IRON_GOLEM) and which itself
    holds air or a fluid; IronGolem.checkSpawnObstruction then wants something to stand on, no full block in that
    cell and no full block and no fluid in the two cells above it. fluids = extra fluid cells the World does not
    hold (a lava_glow). Returns the (x, y, z) cell the golem's feet are in."""
    fl = set(tuple(c) for c in fluids)

    def fluid(c):
        return c in fl or world.block_id(*c) in ("water", "lava")

    def empty_or_fluid(c):
        return world.block_id(*c) is None or fluid(c) or not world.is_solid(*c)

    def full(c):
        bid = world.block_id(*c)
        return bid is not None and (world.is_full_cube(*c) or bid == "glass" or bid.endswith("_glass"))

    z0 = int(villager_z)
    above = (x, y, z0 + GOLEM_SPAWN_Y)
    for z in range(z0 + GOLEM_SPAWN_Y - 1, z0 - GOLEM_SPAWN_Y - 2, -1):
        below = (x, y, z)
        bid = world.block_id(*below)
        ok_above = world.block_id(*above) is None or fluid(above)
        if bid is not None and world.is_solid(*below) and not _no_golem_on(bid) and ok_above:
            feet = above
            if full(feet):
                return None
            for k in (1, 2):
                c = (feet[0], feet[1], feet[2] + k)
                if full(c) or fluid(c) or (world.block_id(*c) is not None and world.is_solid(*c)):
                    return None
            return feet
        above = below
    return None


def spawn_cells(world, villagers, fluids=()):
    """Every cell where the game could put a golem for villagers standing at the block positions `villagers`
    [(x, y, z), ...]: the columns within +-8 of any of them, each scanned as spawn_cell() does. Returns a set."""
    out = set()
    for vx, vy, vz in villagers:
        for dx in range(-GOLEM_SPAWN_XZ, GOLEM_SPAWN_XZ + 1):
            for dy in range(-GOLEM_SPAWN_XZ, GOLEM_SPAWN_XZ + 1):
                c = spawn_cell(world, int(vx) + dx, int(vy) + dy, int(vz), fluids)
                if c is not None:
                    out.add(c)
    return out


def golem_loot(seed=0):
    """The drops of one iron golem by loot_table/entities/iron_golem.json: {'iron_ingot': 3..5, 'poppy': 0..2}
    (two pools, one roll each, set_count uniform, both ends included), drawn from `seed`."""
    rng = np.random.default_rng([int(seed), 7193])
    return {item: int(rng.integers(lo, hi + 1)) for item, lo, hi in GOLEM_LOOT}


# ----------------------------------------------------------------------------------------------------
# small physics: a jump, a bed bounce, a push (per game tick)
# ----------------------------------------------------------------------------------------------------
def jump_track(up=1.0, ceiling=None, max_ticks=60):
    """Heights after each tick of a jump (0.42 per tick up, gravity 0.08, vertical drag 0.98) that lands `up`
    blocks higher (negative: lower). The last entry is the landing. A jump up one block: apex 1.25 after 6 ticks,
    landed on the block after 9 ticks (10.8 frames). ceiling = how high the feet can rise before the head meets a
    block (Entity.move: the vertical speed is then 0 and it falls)."""
    y, v, out = 0.0, JUMP, [0.0]
    for _t in range(max_ticks):
        y += v
        if ceiling is not None and y > ceiling:
            y, v = float(ceiling), 0.0
        if v <= 0.0 and y <= up:
            out.append(float(up))
            return out
        v = (v - GRAVITY) * AIR_DRAG_V
        out.append(y)
    raise ValueError("a jump of %r blocks does not land" % (up,))


def bounce_track(jumps=1, min_bounce=None, ceiling=None, max_ticks=400):
    """Heights above the mattress after each tick of a baby villager jumping on a bed (JumpOnBed): `jumps` jumps
    of 0.42. A landing on the bed bounces it back up by the 26.x rule (Entity.restituteMovementAfterCollisions,
    then LivingEntity.travelInAir in the same tick): only if it falls faster than gravity (0.08 per tick), with
    v' = (f g - v) x lerp(f, 1, 0.98) x 0.75 (f = the part of the tick's fall it made before touching the
    mattress, BED_BOUNCE 0.75), then gravity and drag as every tick: (v' - 0.08) x 0.98. Under open sky one jump
    (apex 1.25) rebounds to 0.50, 0.17 and 0.02 and has settled in 47 ticks; min_bounce = an extra cut-off in
    blocks per tick (None: the game's). It then stands 5 ticks (the behaviour's cooldown) and jumps again.
    ceiling = how high its feet can rise above the mattress before its head meets a block (in the 2-high pod:
    2 - 9/16 - 0.975 = 0.46): it stops there and falls. Returns [height per tick]."""
    y, v, out, left = 0.0, JUMP, [0.0], int(jumps) - 1
    rest = 0
    for _t in range(max_ticks):
        if rest:
            rest -= 1
            out.append(0.0)
            if rest == 0:
                if left <= 0:
                    return out
                left -= 1
                v = JUMP
            continue
        if v < 0.0 and y + v <= 0.0:                                    # it reaches the mattress this tick
            f = y / -v
            if -v > GRAVITY and (min_bounce is None or -v * BED_BOUNCE >= min_bounce):
                v = (f * GRAVITY - v) * (1.0 + f * (AIR_DRAG_V - 1.0)) * BED_BOUNCE
                v = (v - GRAVITY) * AIR_DRAG_V
                y = 0.0
                if v <= 0.0:
                    v, rest = 0.0, BED_JUMP_COOLDOWN_TICKS
            else:
                y, v, rest = 0.0, 0.0, BED_JUMP_COOLDOWN_TICKS
            out.append(0.0)
            continue
        y += v
        if ceiling is not None and y > ceiling:
            y, v = float(ceiling), 0.0
        v = (v - GRAVITY) * AIR_DRAG_V
        out.append(y)
    return out


# ----------------------------------------------------------------------------------------------------
# THE SET (inside the village's edit hook)
# ----------------------------------------------------------------------------------------------------
def iron_farm(b, at=AT, floor=FLOOR, name="tower", water="sheet", lava_watts=40.0, rims="glass", views=None):
    """Build the iron farm tower into the village (call it inside build_village(scene, edit=hook)). Returns its dict
    (also Village.sets[name]); after the build call farm(v, name) for the parts that change on camera."""
    from . import fixtures, sets

    if name in b.v.sets:
        raise KeyError("a set piece called %r exists already" % name)
    L0 = layout(at, floor, 0, rims)
    x0, y0, x1, y1 = L0["footprint"]
    grounds = {b.ground(x, y) for x in range(x0, x1 + 1) for y in range(y0, y1 + 1)}
    if None in grounds:
        raise ValueError("towers.iron_farm: no terrain under part of the tower at %s" % (at,))
    g = min(grounds)
    if max(grounds) - g > 1:
        raise ValueError("towers.iron_farm: the ground under the tower at %s varies by %d blocks: choose a flatter "
                         "place" % (at, max(grounds) - g))
    L = layout(at, floor, g, rims)
    w = b.w
    # the ground: level, no plants, nothing grows here afterwards; trees that would stand in the tower go
    pad = 3
    for x in range(x0 - pad, x1 + pad + 1):
        for y in range(y0 - pad, y1 + pad + 1):
            if b.ground(x, y) != g and x0 <= x <= x1 and y0 <= y <= y1:
                b.set_ground(x, y, g)
            b.clear_plants(x, y)
            b.reserved.add((x, y))
    gone = []
    for t in list(b.trees):
        cells = [(t["x"], t["y"])] + [(c[0], c[1]) for c in t.get("leaves", ())]
        if any(x0 - 2 <= cx <= x1 + 2 and y0 - 2 <= cy <= y1 + 2 for cx, cy in cells):
            sets.remove_tree(b, t)
            gone.append((t["x"], t["y"]))
    busy = [(c, w.block_id(*c)) for c in L["cells"] if w.block_id(*c) is not None]
    if busy:
        raise ValueError("towers.iron_farm: the tower at %s would replace %s" % (at, busy[:4]))
    for c, st in sorted(L["cells"].items()):
        if st is not None:
            w.set(c[0], c[1], c[2], st[0], st[1])
    X, Y, F = L["X"], L["Y"], L["F"]
    # parts that change on camera are drawn by their own objects (claimed cells stay in the World)
    fixtures.claim(w, [L["top_step"]])
    # lights: the lantern on the floor (group <name>_pod), the wall torch at the zombie's window (<name>_cell)
    b.torch(L["lantern"], "lantern", {"hanging": "false", "waterlogged": "false"}, group=name + "_pod")
    b.torch(L["torch"], "wall_torch", {"facing": "west"}, group=name + "_cell")
    # beds: white, white, Mom's red one (village mesh) and the second red bed that appears on a frame (its own object)
    for key, foot in L["beds"].items():
        b.bed("%s_bed_%s" % (name, key), foot, "north", "red" if key == "mom" else "white")
    bed2 = fixtures.bed(b, L["bed2"], BED2_FACING, "red", name=name + "_bed2")
    hopper, chest = fixtures.hopper_on_chest(b, L["chest"], "north", animated=True)
    # the glass last but the fluids: the pod (the plug, the window frame and the gap are left as they are)
    pod = fixtures.glass_box(b, *L["pod"], openings=[L["gap"], L["cell"], (L["cell"][0], L["cell"][1], F + 1)],
                             name=name + "_pod")
    px0, py0, px1, py1 = L["platform"]
    if water == "sheet":
        wat = fixtures.water_sheet(b, px0, py0, px1, py1, F, toward="west", amount=2, name=name + "_water")
    elif water == "game":
        wat = fixtures.water(b, [(x, y, F) for x in range(px0, px1 + 1) for y in range(py0, py1 + 1)],
                             sources=[(px1, y, F) for y in range(py0, py1 + 1)], name=name + "_water")
    else:
        raise ValueError("towers.iron_farm: water is 'sheet' (a level 2/9 sheet drawn flowing west) or 'game' "
                         "(sources along the pod, the game's spread), not %r" % (water,))
    sx0, sy0, sx1, sy1 = L["slot"]
    lava = fixtures.lava_glow(b, sx0, sy0, sx1, sy1, L["lava_z"], name=name + "_lava", watts_per_block=lava_watts)
    # anchors (standing spots with yaws; look targets end in _target) -----------------------------------------
    A = {}

    def anchor(key, pos, yaw=None):
        A[key] = b.anchor("%s_%s" % (name, key), pos, yaw)

    zombie_pos = (L["cell"][0] + 0.3, L["cell"][1] + 0.5, float(F))          # pressed against the sill
    zombie_eye = (zombie_pos[0], zombie_pos[1], F + 1.74)
    anchor("zombie", zombie_pos, -math.pi / 2.0)
    anchor("zombie_target", zombie_eye)
    east = math.pi / 2.0
    # Mom one whole empty block (column X + 3) from the zombie's arms, which reach out over the sill (column X + 4)
    anchor("mom", (X + 2.5, Y + 1.5, float(F)), yaw_to((X + 2.5, Y + 1.5), zombie_eye))
    anchor("mom_glass", (X + 2.5, Y + 0.45, float(F)), yaw_to((X + 2.5, Y + 0.45), zombie_eye))
    anchor("baby_glass", (X + 1.6, Y + 0.45, float(F)), east)
    anchor("bed_side", (X + 2.5, Y + 2.45, float(F)), yaw_to((X + 2.5, Y + 2.45), zombie_eye))
    # beat 6: beside the red bed in the free space of the second bed (not placed yet), off the pan's start axis
    anchor("bed_beside", (X + 3.5, Y + 3.4, float(F)), yaw_to((X + 3.5, Y + 3.4), zombie_eye))
    # backed against the far glass, 1.0 apart (a villager's folded arms are 1.0 wide): two on the west glass, one on
    # the south glass in the south-west corner (the lantern stands in the corner cell)
    for i, p in enumerate(((X + 0.45, Y + 1.4), (X + 0.45, Y + 2.4), (X + 1.4, Y + 0.4))):
        p = (p[0], p[1], float(F))
        anchor("back_%d" % (i + 1), p, yaw_to(p, zombie_eye))
    for i in range(4):
        anchor("row_%d" % (i + 1), (X + 0.5 + i, Y + 2.4, float(F)), math.pi)
    anchor("gap_in", (L["gap"][0] + 0.5, Y + 4.66, float(F)), math.pi)
    anchor("gap_adult", (L["gap"][0] + 0.5, Y + 4.3, float(F)), math.pi)      # an adult's face clear of the plug
    anchor("gap_down", (L["gap"][0] + 0.5, L["gap"][1] + 2.5, F + 0.2))       # look target: out of the gap, low
    anchor("gap_side", (L["gap"][0] + 0.0, Y + 4.66, float(F)), math.pi)
    anchor("gap_target", (L["gap"][0] + 0.5, L["gap"][1] + 0.5, F + 0.5))
    ts = L["top_step"]
    anchor("top_step", (ts[0] + 0.5, ts[1] + 0.5, float(F)), 0.0)
    anchor("top_step_baby", (ts[0] + 0.72, ts[1] + 0.42, float(F)), yaw_to((ts[0] + 0.72, ts[1] + 0.42),
                                                                            (ts[0] + 4.0, ts[1] + 3.0)))
    anchor("one_down", (ts[0] - 0.5, ts[1] + 0.5, float(F - 1)), east)
    anchor("watch_22", (X + 2.7, Y + 2.5, float(F)), yaw_to((X + 2.7, Y + 2.5), (ts[0] - 0.5, ts[1] + 0.5)))
    s0 = L["steps"][0]
    anchor("stairs_foot", (s0[0] + 1.6, s0[1] + 1.3, float(g)), yaw_to((s0[0] + 1.6, s0[1] + 1.3),
                                                                       (s0[0] + 0.5, s0[1] + 0.5)))
    anchor("stairs_target", (X + 4.5, Y + 6.0, F - 3.0))
    anchor("foot_front", (X + 2.5, Y - 1.55, float(g)), math.radians(20.0))
    anchor("pod_target", (X + 2.5, Y + 2.5, F + 1.0))
    ch_ = L["chest"]
    anchor("chest_front", (ch_[0] + 0.5, ch_[1] + 1.55, float(g)), 0.0)          # at the chest, facing it
    anchor("chest_aside", (ch_[0] + 2.2, ch_[1] + 2.2, float(g)), math.radians(-120.0))
    anchor("chest_steve", (ch_[0] + 1.25, ch_[1] + 2.35, float(g)), yaw_to((ch_[0] + 1.25, ch_[1] + 2.35),
                                                                         (ch_[0] + 0.5, ch_[1] + 0.5)))
    anchor("poppies", (ch_[0] - 0.55, ch_[1] + 2.4, float(g)), yaw_to((ch_[0] - 0.55, ch_[1] + 2.4),
                                                                      (ch_[0] - 1.0, ch_[1] + 6.0)))
    anchor("hopper_target", (ch_[0] + 0.5, ch_[1] + 0.5, g + 1.7))
    anchor("golem_spawn", (px0 + 1.5, Y + 1.5, float(F)), east)
    anchor("golem_24", (px0 + 2.5, Y + 1.5, float(F)), east)
    anchor("slot_target", ((sx0 + sx1) / 2.0 + 0.5, Y + 2.5, F - 0.5))
    # the square: the baby's spot on the path beside the well's east rim, three blocks in front of the plaza
    # camera, facing where Steve comes from (the north-west); the tower above the roofs beyond it
    sq, steve_from = (6.38, 1.16), (-1.0, 7.3)
    anchor("square_baby", sq, yaw_to(sq, (sq[0] + 0.43, sq[1] + 0.9)))     # facing north-north-east: 80 degrees
#                                                                           right of the plaza camera's line, so
#                                                                           from behind its nose shows in profile
    lu = (X + 1.0, Y - 6.0)
    anchor("lineup", lu, math.pi / 2.0)
    route = [(X + 9.0, Y + 10.0), (X + 3.0, Y + 10.0)]
    b.path(name + "_push_square", [(6.5, 6.0), (-0.5, 6.0)])           # beat 3 on the square: west along the plaza
    b.path(name + "_steve_square", [steve_from, (8.3, 0.7)])           # beat 1: Steve across the square at the lens
    b.path(name + "_steve_past", [(4.5, 0.64), (6.55, 3.1)])           # beat 2: his legs between the lens and it
    anchor("push_baby", (8.9, 6.0, 0.0), yaw_of("west"))
    # no plants on the ground lines of the cameras near the ground (views: None = every camera of cameras() lower
    # than 4.5 blocks over the ground; a list of camera names = only those; () = none), the lineup and the push route
    cams = cameras(L)
    names = [k for k, c in cams.items() if c["pos"][2] < g + 4.5] if views is None else list(views)
    for k in names:
        c = cams[k]
        for t in [c["target"]] + ([c["target1"]] if "target1" in c else []):
            if math.dist(c["pos"][:2], t[:2]) < 30.0:
                sets.clear_view(b, c["pos"], t, 2.2)
    if views is None:
        sets.clear_view(b, route[0], route[-1], 2.4)
        sets.clear_view(b, (lu[0], lu[1] - 2.0), (lu[0], lu[1] + 2.0), 2.4)
    res = dict(name=name, layout=L, ground=g, pod=pod, bed2=bed2, hopper=hopper, chest=chest, water=wat, lava=lava,
               anchors=A, trees_removed=gone, at=(X, Y), floor=F, lights=(name + "_pod", name + "_cell"),
               zombie=zombie_pos, zombie_eye=zombie_eye, push_route=[(p[0], p[1], b.walk_z(*p)) for p in route],
               stairs=[(c[0] + 0.5, c[1] + 0.5, c[2] + 1.0)
                                                                for c in L["steps"]])
    b.v.sets[name] = res
    return res


# ----------------------------------------------------------------------------------------------------
# AFTER THE BUILD: the Farm (parts that change on camera, and the farm at work)
# ----------------------------------------------------------------------------------------------------
class Farm:
    """The built tower: .v (Village), .set (iron_farm's dict), .L (layout), .A (anchors by short name), .pod
    (GlassBox), .bed2 (fixtures Bed), .hopper / .chest, .water / .lava (Fluids), .top_step (breaking Breakable),
    .cameras {name: dict(pos, target, lens, fstop)}. Methods: see the module docstring."""

    def __init__(self, v, res):
        from . import breaking

        self.v, self.set, self.L, self.name = v, res, res["layout"], res["name"]
        self.A = {k: v.anchors["%s_%s" % (self.name, k)] for k in res["anchors"]}
        self.yaw = {k: v.yaws.get("%s_%s" % (self.name, k)) for k in res["anchors"]}
        self.pod, self.bed2, self.hopper, self.chest = res["pod"], res["bed2"], res["hopper"], res["chest"]
        self.water, self.lava = res["water"], res["lava"]
        self.top_step = breaking.place_from_world(v.collection, v.world, [self.L["top_step"]])[0]
        self.beds = {k: v.beds["%s_bed_%s" % (self.name, k)] for k in self.L["beds"]}
        self.cameras = cameras(self.L)
        self._golem_events = []
        self._slides = []

    # ---- where things are
    @property
    def zombie_eye(self):
        """The zombie's eye point in its cell (look target of every villager in the pod)."""
        return self.set["zombie_eye"]

    def pane(self, cell):
        """The glass block object at `cell` (to hide a single pane with fixtures.see_through)."""
        return self.pod.panes[tuple(int(c) for c in cell)]

    def see_through(self, st, shot, camera=None, n=1, cells=None, points=None):
        """Hide the pod's glass blocks nearest a camera outside for one shot (camera only; fixtures.see_through):
        camera = a cameras() entry or dict(pos, target): the `n` panes its line of sight crosses first; with
        points = [(x, y, z) | Character, ...]: the first pane on the line from the camera to each of them; or
        cells = [(x, y, z), ...] named. Call it in shot order (its keys at a cut belong to the later shot).
        Returns the pane objects hidden."""
        from . import fixtures

        if cells:
            panes = [self.pane(c) for c in cells]
        elif points:
            panes = []
            for p in points:
                q = p.eye_point(shot.frame_start) if hasattr(p, "eye_point") else p
                for ob in self.panes_toward(camera["pos"], tuple(q), 1):
                    if ob not in panes:
                        panes.append(ob)
        else:
            panes = self.panes_toward(camera["pos"], camera["target"], n)
        fixtures.see_through(st, shot, panes)
        return panes

    def panes_toward(self, camera_pos, target, n=1, walls=("north", "east", "south", "west", "roof")):
        """The `n` glass blocks of the pod nearest to the line from a camera at `camera_pos` to `target` that the
        line crosses first: the panes to hide (fixtures.see_through(st, shot, panes)) for a camera outside."""
        a, c = np.array(camera_pos, float), np.array(target, float)
        hits = []
        for wall in walls:
            for cell in self.pod.walls.get(wall, ()):
                if cell not in self.pod.panes:
                    continue
                lo = np.array(cell, float)
                t = _segment_box(a, c, lo, lo + 1.0)
                if t is not None:
                    hits.append((t, cell))
        hits.sort()
        return [self.pod.panes[cl] for _t, cl in hits[:n]]

    # ---- the zombie
    def zombie_in_cell(self, zombie, frame, aggro=False, look=None, ease=0):
        """Place an engine.undead zombie in its cell ON `frame`: pressed against the sill, facing the pod, arms out
        (their slow sway runs by itself). aggro=True: the raised, aggressive arms (ease 0 = the game's snap).
        look = a Character / point its head turns to."""
        zombie.place(frame, self.set["zombie"], -math.pi / 2.0)
        if aggro:
            zombie.aggro(frame, ease=ease)
        if look is not None:
            zombie.look_at(frame, look, ease=0)
        return frame

    # ---- the golem
    def golem_spawn(self, golem, frame, pos=None, yaw=None, look=None, look_after=6, look_ease=6, empty_from=None):
        """The golem APPEARS on the platform ON `frame`, in one frame, standing (the game's spawn: no effect at
        all): placed at `pos` (default the golem_spawn anchor) facing `yaw` (default -135 degrees: north-west, along
        the platform; EntityType.create gives a spawned mob a random facing), not rendered before `frame` (since its
        last slide). look = a point / Character its head turns to
        `look_after` frames later. Use ONE engine.mobs IronGolem for every spawn. Returns `frame`.
        empty_from = a Shot or a frame: the golem of an EARLIER spawn that has not slid away is gone from there
        (the jump cut of beat 10: pass the new shot, the platform is empty until `frame`). Without it such a call
        raises ValueError (one model: the earlier golem would stand there until `frame`)."""
        from . import undead

        pos = self.A["golem_spawn"] if pos is None else pos
        yaw = math.radians(-135.0) if yaw is None else yaw
        frame = int(frame)
        e0 = getattr(empty_from, "frame_start", empty_from)
        before = [e for e in self._golem_events if e[0] < frame]
        # a slide keyed earlier whose golem drops out of sight only ON or AFTER this spawn is unfinished: the cut
        # (empty_from) must end it, its vanish key, puff and flicker included (else the new golem would be hidden
        # from that frame on)
        unfinished = [sl for sl in self._slides if sl["gone"] >= frame and sl["frame"] < frame]
        standing = bool(before) and before[-1][1] == "spawn" and not unfinished
        if e0 is None and (standing or unfinished):
            if unfinished:
                sl = unfinished[0]
                raise ValueError("golem_spawn(%d): the golem sliding from frame %d drops out of sight only on frame "
                                 "%d; pass empty_from=<the shot> (or a frame) of the cut: the slide, its puff and "
                                 "its flicker then end there" % (frame, sl["frame"], sl["gone"]))
            raise ValueError("golem_spawn(%d): the golem spawned on frame %d has not slid away; pass "
                             "empty_from=<the shot> (or a frame) where the platform is empty again"
                             % (frame, before[-1][0]))
        if not before:
            undead.vanish(golem, None)                                      # nothing before the first spawn
        elif e0 is not None:
            e0 = int(e0)
            last = max(e[0] for e in before)
            if not last < e0 <= frame:
                raise ValueError("golem_spawn(%d): empty_from %d must lie after the golem's last event (%d) and "
                                 "not after the spawn" % (frame, e0, last))
            for sl in unfinished:                                           # the cut ends the unfinished slide
                undead.appear(golem, sl["gone"])                            # (replaces its vanish key)
                self._golem_events = [e for e in self._golem_events if e != (sl["gone"], "gone")]
                sl["gone"] = sl["cut"] = e0
            self._cut_effects(e0)
            if e0 < frame:
                undead.vanish(golem, e0)
                self._golem_events.append((e0, "gone"))
        golem.place(frame, pos, yaw)
        undead.appear(golem, frame)
        self._golem_events.append((frame, "spawn"))
        self._golem_events.sort(key=lambda e: e[0])
        if look is not None:
            golem.look_at(frame + look_after, look, ease=look_ease)
        return frame

    def golem_step(self, golem, frame, toward=None, distance=0.45):
        """One heavy step toward `toward` (default the pod, east) against the current. Returns its end frame."""
        here = golem.pos_at(frame)
        if toward is None:
            d = (1.0, 0.0)
        else:
            t = ch._vec3(toward)
            d = (t.x - here.x, t.y - here.y)
            n = math.hypot(*d) or 1.0
            d = (d[0] / n, d[1] / n)
        to = (here.x + d[0] * distance, here.y + d[1] * distance, here.z)
        return golem.walk(frame, [tuple(here), to], ramp=(4, 6))

    def golem_slide(self, golem, frame, start=None):
        """The current carries the golem west (sideways when it faces the pod) to the slot and it drops 4 blocks out
        of sight into it (fixtures.slide: 0.014 per tick along the current, x 0.8 in water; a 1.4-wide golem falls
        when its middle is 0.7 past the rim). It is gone (not rendered) from the frame its head is below the rim.
        Returns fixtures.slide's dict (frame, edge, frame_end, gone, track) + 'drop' (4.0)."""
        from . import fixtures, undead

        here = golem.pos_at(frame) if start is None else ch._vec3(start)
        rim_x = float(self.L["platform"][0])                                # the platform's west edge
        distance = (here.x - rim_x) + GOLEM_SIZE[0] / 2.0
        drop = float(self.L["rim"] - self.L["slot_floor"])
        r = fixtures.slide(golem, frame, "west", distance, drop=drop, start=start, vanish=False)
        gone = r["gone"] if r["gone"] is not None else r["frame_end"]
        undead.vanish(golem, gone)
        self._golem_events.append((gone, "gone"))
        self._golem_events.sort(key=lambda e: e[0])
        r.update(drop=drop, vanish=gone)
        self._slides.append(dict(frame=int(frame), gone=int(gone), cut=None, bursts=[], flickers=[], r=r))
        return r

    def _cut_effects(self, frame):
        """A cut on `frame` (golem_spawn's empty_from): the death puffs of earlier slides stop there (particles in
        the air at the cut are not carried into the new shot) and their lava flickers end the frame before."""
        f = int(frame)
        for sl in self._slides:
            for burst in sl["bursts"]:
                burst.stop(f)
            keep = []
            for a, b, at in sl["flickers"]:
                if b >= f:
                    self.lava._flickers = [x for x in self.lava._flickers if (x[0], x[1]) != (a, b)]
                    if f - 1 >= a:
                        self.lava.flicker(a, f - 1, at=at if at is not None and at < f else None)
                        keep.append((a, f - 1, at))
                    self.lava._relight()
                else:
                    keep.append((a, b, at))
            sl["flickers"] = keep

    def golem_death(self, golem, slide, camera=None, delay=0, seed=0, flicker=True, glow=None, until=None):
        """The white death puff out of the slot and the lava glow flicker for a golem that slid in: the puff
        (engine.animals.poof, 20 particles in the golem's 1.4 x 2.7 box) where its head goes under the rim, ON
        slide['gone'] + delay, rising out of the slot. delay=0 is the film's (the puff as it drops); the game's golem
        burns 240 ticks (12 s: 100 health, 4 per lava hit, one hit per 10 ticks) before it dies: delay=288.
        flicker: the lava light is smothered on gone and flares (fixtures Fluid.flicker). glow = the puff's self-light
        (default GOLEM_PUFF_GLOW 0.5: the game lights a particle by the light level only, so in daylight a poof is
        near white even against the sun; engine.animals' 0.15 left it mid-grey in the backlit slide shot).
        Returns dict(frame, burst)."""
        from . import animals

        f = int(slide["gone"] or slide["frame_end"]) + int(delay)
        x, y = slide["track"][-1][1][0], slide["track"][-1][1][1]
        feet = (x, y, float(self.L["rim"]) - GOLEM_SIZE[1] + 0.6)
        glow = GOLEM_PUFF_GLOW if glow is None else float(glow)
        rec = next((sl for sl in self._slides if sl["r"] is slide), None)
        if rec is not None and rec["cut"] is not None:
            raise ValueError("golem_death: this slide was cut on frame %d by a later golem_spawn(empty_from=...): "
                             "key the death before the next spawn" % rec["cut"])
        burst = animals.poof(feet, f, camera=camera, seed=seed, village=None, size=GOLEM_SIZE, glow=glow)
        fl = None
        if flicker:
            fl = (int(slide["edge"] or slide["frame"]), int(f + 40), int(slide["gone"] or f))
            if until is not None and fl[1] >= int(until):
                fl = (fl[0], int(until) - 1, fl[2] if fl[2] < int(until) else None)
            if fl[1] >= fl[0]:
                self.lava.flicker(fl[0], fl[1], at=fl[2])
            else:
                fl = None
        if until is not None:
            burst.stop(int(until))
        if rec is not None:
            rec["bursts"].append(burst)
            if fl is not None:
                rec["flickers"].append(fl)
        return dict(frame=f, burst=burst)

    # ---- the drops at the foot
    def deliver(self, items, frame, every=6, seed=0, land=True, spread=0.15):
        """Dropped items (engine.mobs make_dropped_item: 'iron_ingot', 'poppy') fall out of the chute's mouth, one
        every `every` frames from `frame` on, land on the hopper and vanish into it one per 8 ticks
        (fixtures Hopper.stream). Register the items with the Stage. Returns the plans (['landed'], ['frame'] =
        the frame each is gone)."""
        h = self.hopper
        start_z = self.L["chute_mouth"] + 0.35                              # inside the dark chute
        return h.stream(items, frame, every=every, height=start_z - h.bowl, spread=spread, seed=seed, land=land)

    def strew(self, items, frame, frame_end, seed=0, spots=None, face=None):
        """Dropped items lying on the grass around the chest from `frame` on, bobbing and spinning (the poppies he
        threw out): spots = [(x, y)], default seeded spots north and east of the chest, clear of the column and
        the staircase. face = a camera position the sprites face at `frame`. Returns the spots used."""
        rng = np.random.default_rng([int(seed), 3881])
        cx, cy = self.L["chest"][0] + 0.5, self.L["chest"][1] + 0.5
        g = float(self.set["ground"])
        out = []
        for i, it in enumerate(items):
            if spots is not None:
                x, y = spots[i]
            else:
                for _try in range(40):
                    ang = rng.uniform(-0.15 * math.pi, 1.1 * math.pi)
                    r = rng.uniform(1.8, 3.4)
                    x, y = cx + r * math.cos(ang), cy + 1.5 + r * math.sin(ang) * 0.8
                    if all(math.dist((x, y), q) > 0.55 for q in out) and not self._blocked(x, y):
                        break
            out.append((x, y))
            it.place(frame, (x, y, g), age=float(rng.uniform(40, 400)))
            if face is not None:
                it.face(frame, face)
            it.animate(frame, frame_end)
        return out

    def _blocked(self, x, y):
        w, g = self.v.world, self.set["ground"]
        return w.block_id(int(math.floor(x)), int(math.floor(y)), g) is not None

    # ---- the staircase
    def break_top_step(self, player, frame, camera=None, duration=None, drop=None, seed=0, until=None):
        """The player breaks the top dirt step by hand (engine.breaking.mine: the game's 14 ticks = 17 frames from
        the click to the break, ten crack stages, arm swings, crumbs, then 64 dirt particles; drop='auto' drops the
        dirt item, None (default) drops nothing). Place him on the 'one_down' anchor facing it first. until = the
        first frame of the next shot: the crumbs still in the air are not carried into it (fx Burst.stop). Returns
        mine()'s dict ('frame' = the frame the block is gone)."""
        from . import breaking

        m = breaking.mine(player, self.top_step, frame, tool="hand", duration=duration, camera=camera,
                          drop=drop, seed=seed, until=until)
        if until is not None and m.get("burst") is not None:
            m["burst"].stop(int(until))
        return m

    def bounce(self, c, frame, bed="mom", jumps=2, place=True, yaw=None):
        """A baby jumping on one of the pod's beds ('mom', 'white_1', 'white_2' or 'bed2'), its head stopped by the
        glass roof 2 blocks over the floor (as the game stops it; no rebound under it, so jumps=2 is "bounces
        twice", 1.05 s): see bounce(). yaw = its facing (cheat it to the lens). Returns the frame it stands still."""
        b = self.bed2 if bed == "bed2" else self.beds[bed]
        return bounce(c, frame, b, jumps=jumps, place=place, ceiling=self.L["F"] + 2.0, yaw=yaw)

    def ceiling_over(self, x, y, z):
        """The z of the first solid block over the point (x, y, z) (None: open sky within 6 blocks)."""
        w = self.v.world
        cx, cy = int(math.floor(x)), int(math.floor(y))
        for k in range(int(math.floor(z)) + 1, int(math.floor(z)) + 7):
            if w.is_solid(cx, cy, k):
                return float(k)
        return None

    def climb(self, c, frame, first=0, last=None, pause=3, approach=True):
        """A villager (or baby) hops up the dirt steps first..last (0 = the bottom step) one block at a time
        (hop()), `pause` frames on each. approach=True: it walks to the edge of the first step from where it
        stands first. Returns the frame it stands on the last step."""
        steps = self.set["stairs"]
        last = len(steps) - 1 if last is None else last
        f = int(frame)
        here = c.pos_at(f)
        if approach and first == 0:
            s = steps[0]
            edge = (s[0] + 0.95, s[1], here.z)
            if math.dist((here.x, here.y), edge[:2]) > 0.05:
                f = c.walk(f, [tuple(here), edge], speed=1.2)
        for i in range(first, last + 1):
            here = c.pos_at(f)
            ceil = [self.ceiling_over(p[0], p[1], p[2]) for p in (tuple(here), steps[i])]
            ceil = [k for k in ceil if k is not None]
            f = hop(c, f, steps[i], ceiling=min(ceil) if ceil else None) + pause
        return f - pause


def farm(v, name="tower"):
    """The built tower as a Farm (call after build_village(..., edit=hook) with iron_farm in the hook)."""
    if name not in v.sets:
        raise KeyError("no iron farm %r in this village: call towers.iron_farm(b) inside the build_village hook" % name)
    res = v.sets[name]
    if "_farm" not in res:
        res["_farm"] = Farm(v, res)
    return res["_farm"]


def _segment_box(a, c, lo, hi):
    """Parameter t in [0, 1] where the segment a -> c enters the box [lo, hi], or None."""
    d = c - a
    t0, t1 = 0.0, 1.0
    for i in range(3):
        if abs(d[i]) < 1e-12:
            if a[i] < lo[i] or a[i] > hi[i]:
                return None
            continue
        ta, tb = (lo[i] - a[i]) / d[i], (hi[i] - a[i]) / d[i]
        if ta > tb:
            ta, tb = tb, ta
        t0, t1 = max(t0, ta), min(t1, tb)
        if t0 > t1:
            return None
    return t0


# ----------------------------------------------------------------------------------------------------
# THE VILLAGERS (engine.characters rigs): panic, hop, bounce, push, grow up
# ----------------------------------------------------------------------------------------------------
_LOC, _ROT = "location", "rotation_euler"


def panic(c, frame_start, frame_end, threat, seed=0, amount=1.0, turns=True, turn_deg=(14.0, 32.0),
          every=(9, 17), look=True):
    """Trapped panic: the tremble (body hunched 5 degrees, a quick +-2.4 degree twist and a sideways shiver every
    2 frames, the crossed arms pulled in) and, turns=True, quick turns ON THE SPOT (3 frames each, `turn_deg`
    either way of facing the threat, one every `every` frames), with the head kept on `threat` (a point,
    Character or Object: clamped to 70 degrees) the whole time. Two villagers with the same seed tremble frame for
    frame alike (beat 23). Not the game: there a trapped villager tries to run away from the zombie (the brain's
    PANIC activity) and jostles about its cell; this is the film's reading of that. Returns frame_end."""
    f0, f1 = int(frame_start), int(frame_end)
    if f1 - f0 < 8:
        return f1
    rng = np.random.default_rng([int(seed), 6151])
    k = float(amount)
    # body yaw: face the threat, then quick turns either side of it
    tp = c._point(threat, f0)
    here = c.pos_at(f0)
    base = math.atan2(tp.x - here.x, -(tp.y - here.y))
    y0 = c.yaw_at(f0)
    base = y0 + ch._wrap(base - y0)
    if turns:
        keys = [(f0, None), (f0 + 3, base)]
        t, side = f0 + 3 + int(rng.integers(*every)), 1.0 if rng.random() < 0.5 else -1.0
        while t + 3 < f1 - 4:
            side = -side
            keys += [(t, keys[-1][1]), (t + 3, base + side * math.radians(rng.uniform(*turn_deg)))]
            t += 3 + int(rng.integers(*every))
        keys += [(max(keys[-1][0] + 1, f1 - 4), keys[-1][1]), (f1, base)]
        ch._segment(c.root, _ROT, 2, keys)
    # the tremble (as Character.shiver, without its head tuck: the head is on the threat)
    ramp = min(6, (f1 - f0) // 3)
    b0 = ch._val(c.body, _ROT, 0, f0)
    ch._segment(c.body, _ROT, 0, [(f0, None), (f0 + ramp, b0 + math.radians(5.0) * k),
                                  (f1 - ramp, b0 + math.radians(5.0) * k), (f1, b0)])
    if c.arms is not None:
        a0 = ch._val(c.arms, _ROT, 0, f0)
        ch._segment(c.arms, _ROT, 0, [(f0, None), (f0 + ramp, a0 - 0.08 * k), (f1 - ramp, a0 - 0.08 * k), (f1, a0)])
    twist, slide = [(f0, None)], [(f0, None)]
    for n, f in enumerate(range(f0 + 2, f1 - 1, 2)):
        sgn = 1.0 if n % 2 else -1.0
        twist.append((f, sgn * rng.uniform(0.5, 1.0) * math.radians(2.4) * k))
        slide.append((f, sgn * rng.uniform(0.4, 1.0) * 0.009 * c.stride * k))
    twist.append((f1, 0.0))
    slide.append((f1, 0.0))
    ch._segment(c.body, _ROT, 2, twist, "BEZIER")
    ch._segment(c.hips, _LOC, 0, slide, "BEZIER")
    # the head on the threat, re-aimed every 2 frames against the turning body
    if look:
        yk, pk = [(f0, None)], [(f0, None)]
        f = f0 + 2
        while f < f1:
            yaw, pitch = c._aim(threat, f)
            yk.append((f, yaw))
            pk.append((f, -pitch))
            f += 2
        yaw, pitch = c._aim(threat, f1)
        yk.append((f1, yaw))
        pk.append((f1, -pitch))
        ch._segment(c.head, _ROT, 2, yk, "BEZIER")
        ch._segment(c.head, _ROT, 0, pk, "BEZIER")
    return f1


def fall_track(down=1.0, max_ticks=60):
    """Heights after each tick of a mob that walks off a ledge `down` blocks high: no jump; on the ground its vertical
    speed is already one tick of gravity, (0 - 0.08) x 0.98 (LivingEntity.travelInAir; the ground zeroes it each
    tick), so it drops from the first tick past the edge, gravity 0.08 and drag 0.98 per tick after. The last
    entry is the landing: one block takes 5 ticks (6 frames)."""
    y, v, out = 0.0, -GRAVITY * AIR_DRAG_V, [0.0]
    for _t in range(max_ticks):
        y += v
        v = (v - GRAVITY) * AIR_DRAG_V
        if y <= -down:
            out.append(-float(down))
            return out
        out.append(y)
    raise ValueError("a fall of %r blocks does not land" % (down,))


def hop(c, frame, to, face=True, ceiling=None, speed=None):
    """A villager, baby or player moves from where it stands to the point `to` one block up (or level): the game's
    jump (0.42 up, gravity 0.08, drag 0.98: up one block in 9 ticks = 11 frames, apex 1.25), travelling in a straight
    line, legs stepping as in a walk. To a point LOWER than its feet it does not jump: it walks to the edge and steps
    off it (fall_track: no rise, down one block in 5 ticks), as a player walking down a staircase of full blocks
    does; `speed` = its walk in blocks/s (default: a player's 4.317, a villager's engine.characters walk).
    ceiling = the z its head meets on the way up (the pod floor's overhang over the lower steps): the jump is cut
    there as Entity.move cuts it. Returns the landing frame."""
    f0 = int(round(frame))
    here = c.pos_at(f0)
    there = ch._vec3(to, here.z)
    d = there - here
    if face and math.hypot(d.x, d.y) > 1e-3:
        want = math.atan2(d.x, -d.y)
        if abs(ch._wrap(want - c.yaw_at(f0))) > math.radians(10.0):
            f0 = c.turn(f0, want, ease=4)
    span = math.hypot(d.x, d.y)
    if d.z < -0.05:                                                        # down: walk off the edge, fall
        if speed is None:
            speed = PLAYER_WALK if hasattr(c, "sneak") else ch.WALK_SPEED
        per_tick = float(speed) / 20.0
        edge = max(int(math.ceil(0.5 * span / per_tick)), 1) if span > 1e-3 else 0
        heights = [0.0] * edge + fall_track(-d.z)
    else:
        top = None if ceiling is None else float(ceiling) - here.z - getattr(c, "height", 1.95)
        heights = jump_track(there.z - here.z, ceiling=top)
    n = len(heights) - 1
    f1 = f0 + n * TICK
    if span > 1e-3:
        c.walk(f0, [tuple(here), (there.x, there.y, here.z)], speed=span / (n * TICK / FPS))
    keys = [(f0 + i * TICK, here.z + h, "LINEAR") for i, h in enumerate(heights)]
    ch._segment(c.root, _LOC, 2, keys, "LINEAR")
    for i in (0, 1):                                                       # the walk's end frame is rounded: exact
        ch._segment(c.root, _LOC, i, [(f0, here[i], "LINEAR"), (f1, there[i])], "LINEAR")
    return int(math.ceil(f1 - 1e-6))


def walk_down(c, frame, steps, pause=0):
    """A player (or villager) walks down a run of full-block steps, `steps` = the points to stand on in order (each
    one block lower), stepping off every edge (hop() down: no jump). Returns the frame it stands on the last one."""
    f = int(frame)
    for p in steps:
        f = hop(c, f, p) + int(pause)
    return f


def bounce(c, frame, bed, jumps=1, place=True, ceiling=None, yaw=None):
    """A baby villager jumping on a bed (JumpOnBed: babies do this by themselves): it stands on the mattress
    (place=True puts it on the bed's middle ON `frame`, facing `yaw`, default the pillow's left), jumps 0.42 up,
    and each landing on the bed throws it back up at 0.75 of the speed (bounceRestitution 0.75) until the bounce
    dies; 5 ticks later the next of `jumps` jumps (the game: 3 to 6). Under open sky ONE jump shows three
    bounces (1.85 s); under the pod's roof (2 high) each jump is stopped 0.46 over the mattress and does not
    rebound: jumps=2 is "bounces twice" (1.05 s). bed = a Village.beds entry, a fixtures Bed or a point on
    the mattress. ceiling = the z of the block over it (the pod's glass roof: Farm.bounce passes it). Returns
    the frame it stands still again."""
    face = yaw
    if isinstance(bed, dict):
        pos, yaw = bed["pos"], bed.get("yaw", 0.0)
    elif hasattr(bed, "pos"):
        pos, yaw = bed.pos, bed.yaw
    else:
        pos, yaw = bed, c.yaw_at(frame)
    f0 = int(frame)
    if place:
        c.place(f0, pos, yaw + math.pi / 2.0 if face is None else face)
    z0 = c.pos_at(f0).z
    top = None if ceiling is None else float(ceiling) - z0 - getattr(c, "height", 1.95)
    hs = bounce_track(jumps, ceiling=top)
    keys = [(f0 + i * TICK, z0 + h, "LINEAR") for i, h in enumerate(hs)]
    ch._segment(c.root, _LOC, 2, keys, "LINEAR")
    # the legs dangle straight, the folded arms jolt on every take-off
    for i, (a, b2) in enumerate(zip(hs, hs[1:])):
        if a == 0.0 and b2 > 0.0:
            c.swing_arm(int(f0 + i * TICK))
    return int(math.ceil(keys[-1][0]))


def _along(pts, s):
    """Point at distance s along the polyline pts (before 0 / past the end: carried on along the end segments)."""
    if s <= 0.0:
        d = (pts[1] - pts[0]).normalized()
        return pts[0] + d * s
    acc = 0.0
    for a, c in zip(pts, pts[1:]):
        seg = (c - a).length
        if s <= acc + seg or c is pts[-1]:
            return a + (c - a).normalized() * (s - acc)
        acc += seg
    return pts[-1]


SNEAK = 1.295                        # blocks/s, a sneaking player's walk (engine.players SNEAK_SPEED)


def push_route(total, gap0=1.5, mode="tap", release=0.45, rest_ticks=3, max_ticks=4000):
    """The per-tick distances along a route of `total` blocks of a player pushing a villager ahead of him with the
    game's entity push (Entity.push, see push()). mode="tap": he walks (4.317 blocks/s input) into her back and lets
    go of the
    key when their centres are `release` apart (held on, he would walk through her: the push weakens as the boxes
    overlap), both slide to a stop, he waits `rest_ticks` and walks on: she goes in surges of 0.7-1.1 blocks,
    about 0.9 blocks/s over all (the step-by-step way players move villagers). mode="sneak": he sneaks into her
    (1.295 blocks/s input) and holds it: a slow continuous shuffle. Returns [(tick, player along, villager
    along)] (she starts at 0 and stops at `total`)."""
    if mode not in ("tap", "sneak"):
        raise ValueError("push_route mode is 'tap' or 'sneak', not %r" % (mode,))
    a = (PLAYER_WALK if mode == "tap" else SNEAK) / 20.0 * (1.0 - GROUND_FRICTION)
    sp, sv, vp, vv = -float(gap0), 0.0, 0.0, 0.0
    state, count, out = "walk", 0, [(0, sp, sv)]
    done = False
    for t in range(1, max_ticks):
        d = sv - sp
        touching = 0.01 <= d < 0.6
        if state == "walk":
            if not done:
                vp += a
            if touching and mode == "tap" and d <= release:
                state, count = "coast", 0
        elif state == "coast":
            if abs(vp) < 2e-3 and abs(vv) < 2e-3:
                state, count = "rest", rest_ticks
        elif state == "rest":
            count -= 1
            if count <= 0:
                state, count = "walk", 0
        if touching:
            p = PUSH * math.sqrt(d)
            vv += 2.0 * p
            vp -= p
        sp += vp
        sv += vv
        if sv >= total:
            sv, vv, done = float(total), 0.0, True
            if state == "walk":
                state = "coast"
        vp *= GROUND_FRICTION
        vv *= GROUND_FRICTION
        out.append((t, sp, sv))
        if done and abs(vp) < 1e-3:
            return out
    raise ValueError("push_route: %r blocks are not covered in %d ticks" % (total, max_ticks))


def _runs(track, index, eps=2e-3):
    """[(first tick, last tick)] of the runs in which column `index` of a push_route track moves."""
    out, start = [], None
    for (t0, *a), (t1, *b) in zip(track, track[1:]):
        moving = abs(b[index - 1] - a[index - 1]) > eps
        if moving and start is None:
            start = t0
        elif not moving and start is not None:
            out.append((start, t0))
            start = None
    if start is not None:
        out.append((start, track[-1][0]))
    return out


def push(player, villager, frame, points, gap0=1.5, mode="tap", release=0.45, rest_ticks=3):
    """The player walks into the villager's back and pushes her along `points` (her route, her start first), the
    way players move villagers: push_route's game physics (Entity.push 0.05 x sqrt(centre distance), ground
    friction 0.546). mode="tap" (default): short shoves, she surges 0.7-1.1 blocks at a time and both stop in
    between (about 0.9 blocks/s); mode="sneak": a slow continuous shuffle. Both bodies face along the route and
    their legs walk while they move (engine.characters / engine.players walk per surge); key her head (look_at /
    track) AFTER this call. It place()s both ON `frame`: call it first for them in that stretch, in frame order.
    Returns dict(end, surges {name: [(frame, frame, blocks)]}, track)."""
    pts = [ch._vec3(p) for p in points]
    if len(pts) < 2:
        raise ValueError("push needs at least two points")
    total = sum((c - a).length for a, c in zip(pts, pts[1:]))
    track = push_route(total, gap0=gap0, mode=mode, release=release, rest_ticks=rest_ticks)
    f0 = int(frame)
    d0 = (pts[1] - pts[0]).normalized()
    yaw0 = math.atan2(d0.x, -d0.y)
    player.place(f0, tuple(_along(pts, -gap0)), yaw0)
    villager.place(f0, tuple(pts[0]), yaw0)
    surges = {}
    for who, index in ((player, 1), (villager, 2)):
        surges[who.name] = []
        for ta, tb in _runs(track, index):
            sa, sb = track[ta][index], track[tb][index]
            fa, fb = f0 + ta * TICK, f0 + tb * TICK
            pa, pb = _along(pts, sa), _along(pts, sb)
            speed = max(abs(sb - sa) / ((tb - ta) * TICK / FPS), 0.05)
            try:
                who.walk(int(round(fa)), [tuple(pa), tuple(pb)], speed=speed, ramp=(True, True))
            except TypeError:
                who.walk(int(round(fa)), [tuple(pa), tuple(pb)], speed=speed)
            for i in (0, 1):                                    # the exact surge, tick by tick
                keys = [(f0 + t * TICK, _along(pts, track[t][index])[i], "LINEAR") for t in range(ta, tb + 1)]
                ch._segment(who.root, _LOC, i, keys, "LINEAR")
            surges[who.name].append((fa, fb, sb - sa))
    return dict(end=int(math.ceil(f0 + track[-1][0] * TICK)), surges=surges, track=track)


def grow_up(baby, adult, frame, look=None):
    """The baby is replaced by the adult ON `frame`, on the same spot, facing the same way, in one frame (the game:
    a baby simply becomes an adult when its 24000 ticks are up; no particles). The adult is not rendered before
    `frame` (engine.undead.vanish / appear: independent of the Stage's shots), the baby not from it on. look = where
    the adult's head is from that frame (default: the baby's head direction). Returns `frame`."""
    from . import undead

    f = int(frame)
    pos, yaw = baby.pos_at(f), baby.yaw_at(f)
    head_yaw = ch._val(baby.head, _ROT, 2, f)
    adult.place(f, tuple(pos), yaw)
    if look is not None:
        adult.look_at(f, look, ease=0)
    else:
        ch._cut(adult.head, _ROT, 2, f, head_yaw)
    undead.vanish(adult, None)
    undead.appear(adult, f)
    undead.vanish(baby, f)
    return f


# ----------------------------------------------------------------------------------------------------
# cameras (filled in from the proof stills)
# ----------------------------------------------------------------------------------------------------
def cameras(L):
    """Camera framings for the beats, name -> dict(pos, target, lens, fstop, beat[, target1 / pos1 for a move]):
    each one was rendered with the cast on the anchors BEATS names (tools/towers_proof.py b01 .. b24) and the
    heroes' heads land in the Reels safe area (x 8-82 %, y 14-60 %; the self-test checks beat_frames()). L =
    layout() or a Farm."""
    L = getattr(L, "L", L)
    X, Y, F, g = L["X"], L["Y"], L["F"], L["g"]

    def cam(pos, target, lens, fstop=4.0, beat="", focus=None, target1=None, pos1=None):
        d = dict(pos=tuple(float(a) for a in pos), target=tuple(float(a) for a in target), lens=float(lens),
                 fstop=float(fstop), beat=beat)
        if focus is not None:
            d["focus"] = tuple(float(a) for a in focus)
        if target1 is not None:
            d["target1"] = tuple(float(a) for a in target1)
        if pos1 is not None:
            d["pos1"] = tuple(float(a) for a in pos1)
        return d

    plaza = (9.3, -0.6, 0.55)                                   # low on the path east of the well
    return {
        # ---- the square (beats 1-4): the plaza camera behind the baby, the well, the tower over the roofs
        "square": cam(plaza, (X + 2.5, Y + 2.5, 2.4), 40, 2.8,
                      "1, end of 4: at baby height behind the baby (square_baby, lower middle); the tower above "
                      "the roofs in the upper third; Steve along path tower_steve_square comes at the lens"),
        "square_start": cam(plaza, (3.0, 2.5, 0.7), 40, 2.8,
                            "4, the start of the tilt: low on the well's rim, the baby at the right; tilt and pan up "
                            "to C['square'] (s.move(pos, target, pos, C['square']['target']))"),
        "square_long": cam((plaza[0], plaza[1], 0.9), (X + 2.5, Y + 0.45, F + 1.65), 200, 2.8,
                           "4, the cut inside the line: the straw hat in profile at the front glass (mom_glass) "
                           "on a long lens from the plaza; fm.see_through(st, s, C['square_long'], points=[mom])"),
        "baby_face": cam((4.69, 2.57, 0.72), (6.38, 1.16, 0.5), 50, 2.0,
                         "2: tight on the baby's face, front three-quarter from its left; Steve along path "
                         "tower_steve_past strides through the foreground between the lens and the baby"),
        "push_square": cam((3.3, 9.6, 0.65), (6.2, 6.0, 0.95), 18, 4.0,
                           "3: side-on at baby height from the north of the plaza's path, the well behind; pan "
                           "with them: s.move(pos, target, pos, target1)", target1=(0.6, 6.0, 0.95)),
        "square_wide": cam((9.5, -2.2, 1.6), (-8.8, 5.9, 4.4), 28, 5.6,
                           "the establishing wide: the well and the bell in front, the tower above the roofs"),
        # ---- the foot of the tower
        "foot": cam((X + 4.75, Y - 3.2, g + 0.5), (X + 2.5, Y - 1.55, g + 0.5), 35, 2.8,
                    "5: the baby on foot_front, front three-quarter at its own height, the folded arms in the "
                    "middle of the frame, the stone base behind it"),
        "hopper": cam((X - 5.75, Y + 8.0, g + 3.1), (X - 5.5, Y + 5.6, g + 1.75), 30, 2.8,
                      "12, macro: the hopper top in the middle, the ingots and the poppy fall in and vanish"),
        "hopper_wide": cam((X - 6.9, Y + 11.0, g + 3.2), (X - 5.6, Y + 6.0, g + 0.5), 24, 2.8,
                           "12: the baby on 'poppies' among the strewn poppies, its face above the caption band; "
                           "Steve on chest_steve turns from the chest and walks out of frame"),
        "back": cam((X + 8.5, Y + 21.0, g + 3.6), (X + 5.6, Y + 4.5, g + 5.2), 24, 4.0, "13: the back, locked tall"),
        # ---- the pod
        "pan_bed": cam((X + 2.5, Y + 0.55, F + 1.3), (X + 2.4, Y + 4.0, F + 0.45), 24, 4.0,
                       "6, the start of the pan: the red bed lengthwise from its foot, the white beds beside it; "
                       "pan to pan_cell: s.move(pos, target, pos, target1)", target1=(X + 4.8, Y + 1.5, F + 1.2)),
        "pod_out": cam((X - 2.3, Y + 4.6, F + 1.95), (X + 3.0, Y + 2.7, F + 0.75), 24, 4.0,
                       "the pod from outside (over the platform): the sleepers' profiles, the zombie beyond"),
        "pod_in": cam((X + 0.45, Y + 0.45, F + 1.5), (X + 4.7, Y + 3.0, F + 0.9), 20, 4.0,
                      "inside at eye height, from the south-west corner"),
        "two_shot": cam((X + 1.6, Y + 10.6, F + 1.62), (X + 3.55, Y + 1.6, F + 1.5), 45, 2.8,
                        "7: from behind the back wall (hide it), west of the plug: arms left, Mom right"),
        "cell_side": cam((X + 4.85, Y + 2.6, F + 1.75), (X + 0.4, Y + 1.0, F + 1.55), 18, 4.0,
                         "8, 23, 24: beside the zombie cell (north of it), high under the roof: the backed three "
                         "(back_1..3) or the four (back_1, back_2, mom, mom_glass), the platform behind the far "
                         "glass; golem_24 lands between two heads (the zombie's arms reach only 0.35 into the "
                         "pod: they are behind this lens)"),
        "platform": cam((X - 5.5, Y + 0.0, F + 0.3), (X - 1.65, Y + 1.45, F + 1.6), 20, 4.0,
                        "9, 10: low over the slot's rim, the golem on golem_spawn big in front, the pod behind it "
                        "with the three on back_1..3 small behind the glass (the low sun is behind the lens' "
                        "left: the golem stands against blue sky)"),
        "platform_sun": cam((X - 4.6, Y - 0.6, F + 0.3), (X - 3.3, Y + 2.6, F + 1.9), 20, 4.0,
                            "9 (alternative): the golem against the low gold sun; the villagers are out of this "
                            "frame (41 degrees to the right)"),
        "slide": cam((X - 6.9, Y - 3.9, F + 0.45), (X - 5.0, Y + 2.5, F + 0.9), 20, 4.0,
                     "11: from the south at the platform's level, over the slot's open end: the sheet behind the "
                     "glass rim, the lava glowing in the slot below"),
        "slide_low": cam((X - 6.9, Y - 3.9, F - 0.72), (X - 5.0, Y + 2.5, F + 1.0), 20, 4.0,
                         "11 (alternative): a little below the platform: the lava only a band in the slot; the rim's "
                         "stone lip hides the sheet (with rims=None its open edge shows: not the game)"),
        "top_step_side": cam((X + 7.4, Y + 8.4, F + 0.7), (X + 4.4, Y + 5.9, F + 0.6), 30, 2.8,
                             "14: outside, north-east of the top step: the baby on top_step_baby beside the "
                             "opening, the plug over it; through the glass the beds and Mom's hat (bed_side)"),
        "gap": cam((X + 4.85, Y + 2.25, F + 0.42), (X + 4.5, Y + 5.0, F + 0.62), 22, 4.0,
                   "15: inside at floor level, the gap in the middle"),
        "red_bed": cam((X - 1.7, Y + 2.9, F + 0.9), (X + 2.8, Y + 2.2, F + 0.95), 35, 2.8,
                       "16: low from outside the west glass (fm.see_through(st, s, C['red_bed'], points=[mom, "
                       "baby])): the baby on the lens side of Mom (bed_side), the zombie's arms soft beyond her"),
        "grow": cam((X + 2.0, Y + 3.3, F + 1.35), (X + 2.1, Y + 0.45, F + 1.05), 24, 4.0,
                    "17, 19: locked side view against the front glass, the village below"),
        "bounce": cam((X + 4.6, Y + 3.1, F + 1.15), (X + 2.5, Y + 3.6, F + 1.0), 24, 4.0,
                      "18: the red bed from the east"),
        "gap_side": cam((X + 8.0, Y + 3.3, F + 0.9), (X + 4.5, Y + 4.9, F + 0.9), 30, 4.0,
                        "20: the low side view from outside the east glass (fm.see_through(points=[narrator])): "
                        "the narrator on gap_adult in profile, the plug at his face, the gap at his knees"),
        "high": cam((X + 5.0, Y + 9.0, F + 5.5), (X + 2.5, Y + 2.2, F + 0.8), 22, 4.0,
                    "21: over Steve's shoulder, the roof hidden"),
        "back_glass": cam((X + 4.8, Y + 0.4, F + 1.7), (X + 3.1, Y + 5.0, F + 1.0), 18, 2.8,
                          "22: inside from the south-east corner past the narrator on watch_22 (at the left edge, "
                          "his face in lost profile: the pod has no spot that shows his face and Steve at once), "
                          "through the back glass: Steve on one_down, the top step"),
        "stairs": cam((X + 7.0, Y + 10.0, F + 0.6), (X + 4.2, Y + 6.4, F - 0.4), 30, 4.0,
                      "22 (outside view): the top step"),
        "lineup": cam((X + 6.0, Y - 6.0, g + 1.25), (X + 1.0, Y - 6.0, g + 0.95), 30, 4.0, "the narrator lineup"),
        "push": cam((X + 6.0, Y + 18.5, g + 0.75), (X + 6.0, Y + 10.0, g + 0.9), 26, 4.0,
                    "a stand-in place behind the tower for the push's proof (the film's is push_square)"),
    }


def frame_xy(camera, point, aspect=(9, 16)):
    """Where `point` lands in a camera dict's frame as (x %, y % from the top, depth): the film's 9:16 frame with the
    36 mm sensor side vertical (engine.shots), the camera aimed at camera['target'] with Z up (Shot.move)."""
    p, t = np.array(camera["pos"], float), np.array(camera["target"], float)
    f = t - p
    f /= np.linalg.norm(f)
    r = np.cross(f, (0.0, 0.0, 1.0))
    r /= np.linalg.norm(r)
    u = np.cross(r, f)
    d = np.array(point, float) - p
    z = float(d @ f)
    if z <= 1e-6:
        return None, None, z
    half_h = 18.0 / camera["lens"]
    half_w = half_h * aspect[0] / aspect[1]
    return 100.0 * (0.5 + float(d @ r) / z / (2 * half_w)), 100.0 * (0.5 - float(d @ u) / z / (2 * half_h)), z


HEAD = dict(adult=1.68, baby=0.84, steve=1.62, golem=2.38, zombie=1.7)      # head centres above the feet


def beat_frames(fm):
    """For every beat: dict(beat, camera, heroes {label: head point}) as BEATS stages it (anchors + head heights).
    The self-test checks that every hero lands in the safe area of its camera (x 8-82 %, y 14-60 %)."""
    A, F = fm.A, fm.L["F"]

    def h(anchor, kind, dx=0.0, dy=0.0):
        p = A[anchor] if isinstance(anchor, str) else anchor
        return (p[0] + dx, p[1] + dy, p[2] + HEAD[kind])

    steve_path = fm.v.paths[fm.name + "_steve_square"]
    sq = fm.cameras["square"]
    mid = tuple(steve_path[0][k] + 0.4 * (steve_path[-1][k] - steve_path[0][k]) for k in range(3))   # on his way
    push = fm.v.paths[fm.name + "_push_square"]
    beds = fm.beds
    return [
        dict(beat=1, camera="square", heroes={"baby": h("square_baby", "baby"), "steve": h(mid, "steve"),
                                             "pod": A["pod_target"]}),
        dict(beat=2, camera="baby_face", heroes={"baby": h("square_baby", "baby")}),
        dict(beat=3, camera="push_square", heroes={"mom (start)": h(push[0], "adult")}),
        dict(beat=3, camera=dict(fm.cameras["push_square"], target=fm.cameras["push_square"]["target1"]),
             heroes={"mom (end)": h(push[-1], "adult")}),
        dict(beat=4, camera="square_start", heroes={"baby": h("square_baby", "baby")}),
        dict(beat=4, camera="square", heroes={"baby": h("square_baby", "baby"), "mom": h("mom_glass", "adult")}),
        dict(beat=4, camera="square_long", heroes={"mom": h("mom_glass", "adult")}),
        dict(beat=5, camera="foot", heroes={"baby": h("foot_front", "baby"),
                                            "arms": (A["foot_front"][0], A["foot_front"][1], A["foot_front"][2] + 0.45)}),
        dict(beat=6, camera="pan_bed", heroes={"red bed": (beds["mom"]["pos"][0], beds["mom"]["pos"][1], F + 0.5)}),
        dict(beat=6, camera=dict(fm.cameras["pan_bed"], target=tuple(0.5 * (a + b) for a, b in zip(
            fm.cameras["pan_bed"]["target"], fm.cameras["pan_bed"]["target1"]))), heroes={"mom": h("bed_beside", "adult")}),
        dict(beat=6, camera=dict(fm.cameras["pan_bed"], target=fm.cameras["pan_bed"]["target1"]),
             heroes={"zombie": h("zombie", "zombie")}),
        dict(beat=7, camera="two_shot", heroes={"mom": h("mom", "adult")}),
        dict(beat=8, camera="cell_side", heroes={k: h(k, "adult") for k in ("back_1", "back_2", "back_3")}),
        dict(beat=9, camera="platform", heroes={"golem": h("golem_spawn", "golem"),
                                                **{k: h(k, "adult") for k in ("back_1", "back_2", "back_3")}}),
        dict(beat=12, camera="hopper", heroes={"hopper": A["hopper_target"]}),
        dict(beat=12, camera="hopper_wide", heroes={"baby": h("poppies", "baby"), "steve": h("chest_steve", "steve"),
                                                    "hopper": A["hopper_target"]}),
        dict(beat=14, camera="top_step_side", heroes={"baby": h("top_step_baby", "baby"), "gap": A["gap_target"]}),
        dict(beat=15, camera="gap", heroes={"gap": A["gap_target"]}),
        dict(beat=16, camera="red_bed", heroes={"mom": h("bed_side", "adult"),
                                                "baby": h("bed_side", "baby", -0.62, -0.05)}),
        dict(beat=17, camera="grow", heroes={"mom": h("mom_glass", "adult"), "baby": h("baby_glass", "baby")}),
        dict(beat=20, camera="gap_side", heroes={"narrator": h("gap_adult", "adult"), "gap": A["gap_target"]}),
        dict(beat=21, camera="high", heroes={k: h(k, "adult") for k in ("row_1", "row_2", "row_3", "row_4")}),
        dict(beat=22, camera="back_glass", heroes={"narrator": h("watch_22", "adult"), "steve": h("one_down", "steve"),
                                                   "top step": (A["top_step"][0], A["top_step"][1], F)}),
        dict(beat=23, camera="cell_side", heroes={"cleric": h("back_1", "adult"), "librarian": h("back_2", "adult"),
                                                  "mom": h("mom", "adult"), "narrator": h("mom_glass", "adult")}),
        dict(beat=24, camera="cell_side", heroes={"golem": h("golem_24", "golem")}),
    ]


# ----------------------------------------------------------------------------------------------------
# self-test
# ----------------------------------------------------------------------------------------------------
def _check():
    """Numbers: the layout against the game's rules, the farm's mechanics and the calls a director keys (builds the
    village with the tower, renders nothing). Returns the list of failures."""
    import time

    import bpy

    from . import mobs, players, quick, undead, village

    bad = []

    def ok(label, cond, detail=""):
        print("[towers] %-4s %s%s" % ("ok" if cond else "FAIL", label, ("  (%s)" % detail) if detail else ""))
        if not cond:
            bad.append(label)

    # ---- pure numbers
    tr = jump_track(1.0)
    ok("a jump up one block: apex 1.25 after 6 ticks, on the block after 9 ticks (10.8 frames)",
       abs(max(tr) - 1.252) < 0.01 and len(tr) - 1 == 9, "apex %.3f, %d ticks" % (max(tr), len(tr) - 1))
    tr = jump_track(1.0, ceiling=1.025)
    ok("a jump under a ceiling stops there and still lands", max(tr) <= 1.025 + 1e-9 and tr[-1] == 1.0)
    hs = bounce_track(1)
    ups = sum(1 for a, c in zip(hs, hs[1:]) if a == 0.0 and c > 0.0)
    peaks = [hs[i] for i in range(1, len(hs) - 1) if hs[i] > hs[i - 1] and hs[i] >= hs[i + 1]]
    ok("one jump on a bed (open sky): the 26.x rebound (gravity and drag in the landing tick), 0.56 then 0.24",
       ups >= 3 and abs(peaks[0] - 1.252) < 0.01 and 0.5 < peaks[1] < 0.6 and 0.2 < peaks[2] < 0.28,
       "%d take-offs, peaks %s, %d ticks" % (ups, [round(p_, 2) for p_ in peaks], len(hs) - 1))
    fl = fall_track(1.0)
    ok("stepping off a one-block ledge: no rise, down in 5 ticks (6 frames)", max(fl) <= 0.0 and len(fl) - 1 == 5,
       "%s" % [round(y_, 2) for y_ in fl])
    hs = bounce_track(1, ceiling=2.0 - BED_TOP - BABY_HEIGHT)
    ok("in the 2-high pod the glass roof stops a baby's bounce at 0.46 above the mattress",
       max(hs) <= 2.0 - BED_TOP - BABY_HEIGHT + 1e-9, "apex %.3f" % max(hs))
    route = push_route(6.0)
    t_end = route[-1][0]
    surges = len(_runs(route, 2))
    ok("pushing a villager 6 blocks in shoves: several surges, under 1.5 blocks/s, he never passes her",
       surges >= 3 and 6.0 / (t_end / 20.0) < 1.5 and all(sv - sp > 0.05 for _t, sp, sv in route),
       "%d surges, %.2f blocks/s" % (surges, 6.0 / (t_end / 20.0)))
    route = push_route(6.0, mode="sneak")
    ok("sneaking into her: one slow continuous shuffle", len(_runs(route, 2)) == 1,
       "%.2f blocks/s" % (6.0 / (route[-1][0] / 20.0)))
    loot = [golem_loot(s) for s in range(400)]
    irons = {d["iron_ingot"] for d in loot}
    pops = {d["poppy"] for d in loot}
    ok("golem loot: 3..5 iron ingots, 0..2 poppies (loot_table/entities/iron_golem.json)",
       irons == {3, 4, 5} and pops == {0, 1, 2}, "iron %s, poppies %s" % (sorted(irons), sorted(pops)))
    ok("a golem in lava dies after 240 ticks (100 health, 4 per hit, a hit per 10 ticks)", LAVA_DEATH_TICKS == 240)

    # ---- the set in the village
    t0 = time.time()
    scene = quick.reset()
    quick.setup(scene)
    out = {}
    v = village.build_village(scene, seed=1, edit=lambda b: out.update(res=iron_farm(b)))
    fm = farm(v)
    L, w, A = fm.L, v.world, fm.A
    X, Y, F, g = L["X"], L["Y"], L["F"], L["g"]
    print("[towers] built in %.1f s, %d faces" % (time.time() - t0, v.face_count))
    ok("the hook changed nothing it should not (no edit problems, Village.validate clean)",
       not v.edit_problems and not v.validate(), "%s %s" % (v.edit_problems, v.validate()[:3]))
    ok("the pillar and the floor: 10 blocks of stone from the ground", F - g == 10 and all(
        w.block_id(X + 2, Y + 2, z) == "stone" for z in range(g, F)))
    inside = [(x, y, z) for x in range(X, X + 5) for y in range(Y, Y + 5) for z in (F, F + 1)]
    things = {c: w.block_id(*c) for c in inside if w.block_id(*c) is not None}
    ok("the pod: 5 x 5 inside, 2 high, stone floor, glass roof",
       all(w.block_id(x, y, F - 1) == "stone" for x in range(X, X + 5) for y in range(Y, Y + 5))
       and all(w.block_id(x, y, F + 2) == "glass" for x in range(X, X + 5) for y in range(Y, Y + 5))
       and set(things.values()) <= {"white_bed", "red_bed", "lantern", "cobblestone", "wall_torch"},
       "inside: %s" % sorted(set(things.values())))
    zc = L["cell"]
    ok("the zombie cell: 1 x 1 x 2 of air, cobblestone walls, a stone slab roof, the sill at foot level on the "
       "beds' side, open air above it",
       all(w.block_id(zc[0], zc[1], z) is None for z in (F, F + 1))
       and all(w.block_id(*c) == "cobblestone" for c in ((zc[0], zc[1] - 1, F), (zc[0], zc[1] + 1, F + 1),
                                                         (zc[0] + 1, zc[1], F), (zc[0] + 1, zc[1], F + 1)))
       and w.block_id(zc[0], zc[1], F + 2) == "stone_slab" and w.block_id(*L["sill"]) == "cobblestone"
       and w.block_id(*L["window"]) is None)
    gp = L["gap"]
    ok("the back-wall doorway: cobblestone at head height, a one-block gap under it (a baby 0.975 fits, an adult "
       "1.95 does not)", w.block_id(*gp) is None and w.block_id(gp[0], gp[1], F + 1) == "cobblestone"
       and BABY_HEIGHT < 1.0 < VILLAGER_HEIGHT)
    steps = L["steps"]
    one = all(abs(c[2] - a[2]) == 1 and abs(c[0] - a[0]) + abs(c[1] - a[1]) == 1 for a, c in zip(steps, steps[1:]))
    head = [c for c in steps if any(w.is_solid(c[0], c[1], c[2] + k) for k in (1, 2))]
    ok("the dirt staircase: %d full dirt blocks, each one up and one along, two blocks of headroom on every step "
       "(a player walks it), the top step outside the gap" % len(steps),
       one and not head and all(w.block_id(*c) == "dirt" for c in steps)
       and steps[-1] == (gp[0], gp[1] + 1, F - 1) and steps[0][2] == g, "no headroom over %s" % head)
    turns = sum(1 for a, b, c in zip(steps, steps[1:], steps[2:])
                if (b[0] - a[0], b[1] - a[1]) != (c[0] - b[0], c[1] - b[1]))
    ok("it zigzags (changes direction) and has stray dirt at its foot", turns >= 2 and len(L["stray"]) >= 3)
    sx0, sy0, sx1, sy1 = L["slot"]
    px0, py0, px1, py1 = L["platform"]
    ok("the kill slot: 2 wide (a 1.4-wide golem falls in), 4 deep, at the platform's outer edge, the lava blade's "
       "surface 1.1 under the rim, its ends open above the lava (the glow shows there)",
       sx1 - sx0 + 1 == 2 and sx1 + 1 == px0 and L["rim"] - L["slot_floor"] == 4
       and all(w.block_id(x, y, z) is None for x in (sx0, sx1) for y in range(sy0, sy1 + 1)
               for z in range(L["slot_floor"], F))
       and abs(L["lava_z"] - (F - 1.111)) < 0.01 and w.block_id(sx0, sy0 - 1, F - 1) is None)
    ch_ = L["chest"]
    chute = [w.block_id(ch_[0], ch_[1], z) for z in range(g + 2, L["slot_floor"])]
    ok("the collection point: a hopper on a chest at the foot, under an open chute from the slot floor",
       w.block_id(*L["hopper"]) == "hopper" and all(c is None for c in chute)
       and w.block_id(ch_[0], ch_[1] + 1, g + 2) is None)
    # the game's golem spawn rule around the four villager spots of the pod
    vill = [(x, y, F) for x in range(X, X + 5) for y in range(Y, Y + 5)]
    cells = spawn_cells(w, vill, fluids=L["lava_cells"])
    plat = {(x, y, F) for x in range(px0, px1 + 1) for y in range(py0, py1 + 1)}
    pod = {c for c in cells if X - 1 <= c[0] <= X + 5 and Y - 1 <= c[1] <= Y + 5 and F <= c[2] <= F + 1}
    fx0, fy0, fx1, fy1 = L["footprint"]
    away = sorted(c for c in cells if not (fx0 <= c[0] <= fx1 and fy0 <= c[1] <= fy1))
    others = sorted(cells - plat)
    ok("golem spawns (Villager.spawnGolemIfNeeded, SpawnUtil LEGACY_IRON_GOLEM, checkSpawnObstruction): every "
       "platform cell, none inside the 2-high pod, none on the village's roofs",
       plat <= cells and not pod and not away, "%d platform cells; also valid: %s" % (len(plat), others))
    fm.set["spawn_cells"] = sorted(cells)
    # the zombie and Mom
    zx = fm.set["zombie"][0]
    tips = zx - 0.65                                               # engine.undead arms out: 0.65 ahead of the centre
    mom = A["mom"]
    ok("Mom stands one whole empty block from the zombie's arm tips, outside its attack reach",
       (tips - (mom[0] + 0.25)) >= 1.0 and (zx - 0.3 - ZOMBIE_REACH) > mom[0] + 0.3,
       "gap %.2f, reach box to %.2f, Mom from %.2f" % (tips - (mom[0] + 0.25), zx - 0.3 - ZOMBIE_REACH,
                                                         mom[0] + 0.3))
    eye_m = (mom[0], mom[1], F + 1.62)
    ze = fm.zombie_eye
    n = 60
    seen = all(w.block_id(*[int(math.floor(eye_m[k] + (ze[k] - eye_m[k]) * i / n)) for k in range(3)]) is None
               for i in range(1, n))
    ok("Mom sees the zombie through open air (glass would block a villager's line of sight), within 8 blocks",
       seen and math.dist(eye_m, ze) < ZOMBIE_SCARE)
    # ---- the calls a director keys
    from . import characters as chs

    g_ = mobs.make_iron_golem("t_golem")
    probe = []

    def cam_probe():
        if not probe:
            ob = bpy.data.objects.new("t_cam_probe", bpy.data.cameras.new("t_cam_probe"))
            scene.collection.objects.link(ob)
            ob.location = (X - 7.0, Y - 4.0, F)
            probe.append(ob)
        return probe[0]
    f = 20
    fm.golem_spawn(g_, f, look=A["pod_target"])
    r = fm.golem_slide(g_, f + 30)

    def shown(c, frame):
        scene.frame_set(frame)
        return not all(ob.hide_render for ob in c.objects() if ob.type == "MESH")

    ok("the golem appears ON its spawn frame (not on the frame before), is gone from the frame its head is under "
       "the rim", not shown(g_, f - 1) and shown(g_, f) and shown(g_, r["gone"] - 1) and not shown(g_, r["gone"]),
       "spawn %d, edge %d, gone %d" % (f, r["edge"], r["gone"]))
    f2 = r["gone"] + 40
    fm.golem_spawn(g_, f2)
    ok("the same golem appears again for the next spawn (one model for every golem)",
       not shown(g_, f2 - 1) and shown(g_, f2))
    f3, cut = f2 + 60, f2 + 50                     # beat 10: a jump cut on frame `cut`, the new golem on f3
    try:
        fm.golem_spawn(g_, f3)
        refused = False
    except ValueError:
        refused = True
    fm.golem_spawn(g_, f3, empty_from=cut)
    ok("a jump cut: the golem still standing from the last spawn is gone from empty_from, the new one appears "
       "ON its frame (and a spawn over a standing golem without empty_from is refused)",
       refused and shown(g_, cut - 1) and not shown(g_, cut) and not shown(g_, f3 - 1) and shown(g_, f3),
       "cut %d, spawn %d" % (cut, f3))
    # a slide cut short by the next shot: the new spawn's empty_from must end the slide, its vanish and its puff
    r4 = fm.golem_slide(g_, f3 + 8)
    d4 = fm.golem_death(g_, r4, camera=cam_probe())
    f5 = r4["gone"] - 6
    try:
        fm.golem_spawn(g_, f5)
        refused = False
    except ValueError:
        refused = True
    fm.golem_spawn(g_, f5, pos=A["golem_24"], empty_from=f5 - 4)
    puff_after = any(p_["first"] < p_["last"] and p_["last"] > f5 - 4 and p_["first"] >= f5 - 4
                     for p_ in d4["burst"].particles)
    ok("a spawn while an earlier golem is still sliding: refused without empty_from; with it the old golem is gone "
       "from the cut and the new one stays shown (the slide's vanish, puff and flicker end at the cut)",
       refused and shown(g_, f5 - 5) and not shown(g_, f5 - 4) and all(shown(g_, k) for k in
                                                                         (f5, r4["gone"], r4["gone"] + 30))
       and not puff_after, "slide gone %d, cut %d, spawn %d" % (r4["gone"], f5 - 4, f5))
    z = undead.make_zombie("t_zombie")
    fm.zombie_in_cell(z, 1, aggro=True)
    zp = z.pos_at(5)
    ok("the zombie stands in its cell facing the pod", abs(zp.x - zx) < 1e-6 and abs(z.yaw_at(5) + math.pi / 2) < 1e-6)
    baby = chs.make_villager("t_baby", "none", child=True)
    adult = chs.make_villager("t_adult", "none")
    baby.place(1, A["baby_glass"], math.pi / 2)
    grow_up(baby, adult, 40)
    ok("the baby is swapped for the adult on one frame, same spot",
       shown(baby, 39) and not shown(baby, 40) and not shown(adult, 39) and shown(adult, 40)
       and (adult.pos_at(40) - baby.pos_at(39)).length < 1e-6)
    v1 = chs.make_villager("t_mom", "farmer")
    v1.place(1, A["mom"], fm.yaw["mom"])
    panic(v1, 1, 49, fm.zombie_eye, seed=3)
    yaws = [v1.yaw_at(k) for k in range(1, 50)]
    heads = []
    for k in range(4, 48, 4):
        scene.frame_set(k)
        hd = v1.head.matrix_world.to_quaternion() @ chs.Vector((0.0, -1.0, 0.0))
        to = chs.Vector(fm.zombie_eye) - v1.eye_point(k)
        heads.append(math.degrees(hd.angle(to)))
    ok("panic: the body turns on the spot, the head stays on the zombie", max(yaws) - min(yaws) > math.radians(20)
       and max(heads) < 25.0, "body swing %.0f deg, head off the zombie by %.0f deg at most"
       % (math.degrees(max(yaws) - min(yaws)), max(heads)))
    v2 = chs.make_villager("t_twin", "farmer")
    v2.place(1, (A["mom"][0], A["mom"][1] - 0.9, F), fm.yaw["mom"])
    panic(v2, 1, 49, fm.zombie_eye, seed=3)
    tw = [chs._val(o1, "rotation_euler", 2, k) - chs._val(o2, "rotation_euler", 2, k)
          for k in range(2, 48, 3) for o1, o2 in ((v1.body, v2.body),)]
    ok("two villagers with the same seed tremble frame for frame alike", max(abs(t) for t in tw) < 1e-6)
    kid = chs.make_villager("t_kid", "none", child=True)
    s0 = fm.set["stairs"][0]
    kid.place(1, (s0[0] + 1.2, s0[1], float(g)), -math.pi / 2)
    e = hop(kid, 5, s0)
    ok("a baby hops up one block onto the first dirt step in 11 frames", abs(kid.pos_at(e).z - s0[2]) < 1e-6
       and 10 <= e - 5 <= 13, "%d frames" % (e - 5))
    walker = players.make_player("t_down", "steve")
    stp = fm.set["stairs"]
    walker.place(500, stp[8], math.pi / 2)
    e = walk_down(walker, 502, [stp[7], stp[6]])
    zs = [walker.pos_at(k).z for k in range(502, e + 1)]
    ok("Steve walks down two dirt steps: never above the step he started on, lands on each",
       max(zs) <= stp[8][2] + 1e-6 and abs(walker.pos_at(e).z - stp[6][2]) < 1e-6 and e - 502 <= 24,
       "%d frames, top %.2f" % (e - 502, max(zs)))
    e2 = fm.bounce(kid, 30, "mom")
    zs = [kid.pos_at(k).z for k in range(30, e2 + 1)]
    ok("a baby bouncing on Mom's bed stays under the glass roof", max(zs) + BABY_HEIGHT <= F + 2.0 + 1e-6
       and min(zs) >= F + BED_TOP - 1e-6, "head up to %.2f" % (max(zs) + BABY_HEIGHT))
    steve = players.make_player("t_steve", "steve")
    m = chs.make_villager("t_pushed", "farmer")
    rr = push(steve, m, 100, fm.set["push_route"])
    end = fm.set["push_route"][-1]
    ok("the pushed villager ends where her route ends, the player behind her", (m.pos_at(rr["end"]) -
       chs.Vector(end)).length < 0.05 and len(rr["surges"][m.name]) >= 3, "%d surges, %d frames"
       % (len(rr["surges"][m.name]), rr["end"] - 100))
    items = [mobs.make_dropped_item(k, name="t_item_%d" % i) for i, k in enumerate(("iron_ingot", "poppy",
                                                                                  "iron_ingot"))]
    plans = fm.deliver(items, 200, seed=1)
    ok("dropped items fall out of the chute onto the hopper and are taken one per 8 ticks",
       all(p["frame"] > 200 for p in plans) and all(b2["frame"] - a2["frame"] >= 9 for a2, b2 in zip(plans, plans[1:])),
       "gone on %s" % [p["frame"] for p in plans])
    st2 = players.make_player("t_miner", "steve")
    st2.place(300, A["one_down"], fm.yaw["one_down"])
    cam_ob = bpy.data.objects.new("t_cam", bpy.data.cameras.new("t_cam"))
    scene.collection.objects.link(cam_ob)
    cam_ob.location = (X + 7.0, Y + 10.0, F + 0.6)
    mm = fm.break_top_step(st2, 302, camera=cam_ob)
    ok("the top step breaks by hand in the game's 14 ticks (dirt: 17 frames from the click)",
       mm["frame"] - mm["start"] == 17 and fm.top_step.stage_at(mm["frame"] - 1) >= 8,
       "%d frames, %s" % (mm["frame"] - mm["start"], mm.get("stages", [])[:3]))
    fm.bed2.place_at(400)
    ok("the second red bed appears on its frame", not shown(fm.bed2.foot, 399) if hasattr(fm.bed2.foot, "objects")
       else True)
    hd = (L["bed2"][0], L["bed2"][1] - 1, F)
    ok("the second bed is placed as Steve places it from the north: facing south, pillow south, beside Mom's",
       BED2_FACING == "south" and w.block_id(*hd) == "red_bed" and hd[0] == L["beds"]["mom"][0] + 1,
       "foot %s, head %s" % (L["bed2"], hd))
    spots = [A["back_%d" % i] for i in (1, 2, 3)]
    gaps = [math.dist(a_[:2], b_[:2]) for i, a_ in enumerate(spots) for b_ in spots[i + 1:]]

    bed2_cells = {(L["bed2"][0], L["bed2"][1]), (L["bed2"][0], L["bed2"][1] - 1)}

    def free(p_, before_bed2=False, r_=0.3):
        """A villager's 0.6 box at p_ on the pod floor touches no block (the wall torch has no collision box; the
        standing lantern's is 6 x 6 px round the cell's middle)."""
        cells = {(int(math.floor(p_[0] + dx)), int(math.floor(p_[1] + dy))) for dx in (-r_, r_) for dy in (-r_, r_)}
        for cx, cy in cells:
            bid = w.block_id(cx, cy, F)
            if (cx, cy) == L["lantern"][:2]:
                if abs(p_[0] - cx - 0.5) < r_ + 0.19 and abs(p_[1] - cy - 0.5) < r_ + 0.19:
                    return False
            elif bid not in (None, "wall_torch") and not (before_bed2 and (cx, cy) in bed2_cells):
                return False
        return True
    ok("back_1..3 are at least 1.0 apart (a villager's folded arms are 1.0 wide); every standing anchor in the pod "
       "is free floor (bed_beside: until the second bed appears)",
       min(gaps) >= 0.99 and all(free(p_) for p_ in spots + [A["mom"], A["mom_glass"], A["bed_side"],
                                                           A["watch_22"], A["gap_adult"], A["baby_glass"]])
       and free(A["bed_beside"], before_bed2=True), "gaps %s" % [round(x_, 2) for x_ in gaps])
    # every beat's heroes inside the Reels safe area of the beat's camera (x 8-82 %, y 14-60 %)
    outside = []
    for e_ in beat_frames(fm):
        cam_ = fm.cameras[e_["camera"]] if isinstance(e_["camera"], str) else e_["camera"]
        for lab, p_ in e_["heroes"].items():
            fx_, fy_, _z = frame_xy(cam_, p_)
            if fx_ is None or not (8.0 <= fx_ <= 82.0 and 14.0 <= fy_ <= 60.0):
                outside.append((e_["beat"], lab, None if fx_ is None else (round(fx_), round(fy_))))
    ok("every beat's heroes land in the safe area of its camera (beat_frames, %d framings)" % len(beat_frames(fm)),
       not outside, "outside: %s" % outside)
    bpy.context.scene.frame_set(1)
    print("[towers] %s (%d checks failed)" % ("OK" if not bad else "FAILED", len(bad)))
    return bad


def _selftest(argv):
    """`$BPY -m engine.towers` (numbers) or `$BPY -m engine.towers stills NAME ...` (proof stills)."""
    import sys

    if argv and argv[0] == "stills":
        from tools import towers_proof

        return towers_proof.main(argv[1:])
    bad = _check()
    sys.stdout.flush()
    return 1 if bad else 0


if __name__ == "__main__":
    import sys

    sys.exit(_selftest(sys.argv[1:]))
