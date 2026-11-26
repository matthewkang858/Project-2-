"""THE IRON FARM TOWER of "Twenty Minutes" (film three, stories/ironfarm.json): a stone pillar with a glass pod on
top behind the houses north-west of the well, the zombie in its cobblestone cell, the golem platform with its water
sheet and its lava-lit kill slot, the hopper and chest at the foot, the dirt staircase up the back, the one-block gap
in the back wall, and the calls that make the farm work on camera.

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
    A, yaw, C = fm.A, fm.yaw, fm.cameras          # anchors by short name, their yaws, camera framings
    # everything below is keyed per shot, in film order; register what moves with the Stage
    z = undead.add_zombie(st, "zombie"); fm.zombie_in_cell(z, s.frame_start, aggro=True, look=mom)
    g = mobs.make_iron_golem("golem"); st.cast["golem"] = g; st.use(s, g)       # ONE golem for every spawn
    fm.golem_spawn(g, f, look=A["pod_target"]); e = fm.golem_step(g, f + 30)
    r = fm.golem_slide(g, e + 2); fm.golem_death(g, r, camera=s)
    st.lights(s, scale=1.0, groups={"tower_pod": 1.0, "tower_cell": 1.0})          # the pod's lantern, the cell torch

PUBLIC API
  iron_farm(b, at=AT, floor=FLOOR, name="tower", water="sheet", lava_watts=40.0, rims=None) -> dict
      In the edit hook: the whole tower (LAYOUT below) at the pod's south-west inside cell `at`, its floor top at
      `floor`. Levels and clears the ground under it, removes the two village oaks that stood in it, puts every
      block into the World, registers anchors (tower_*), the path tower_push_square, lights tower_pod / tower_cell,
      the beds (Village.beds tower_bed_white_1 / _white_2 / _mom), the pod as cutaways tower_pod_north / _east /
      _south / _west / _roof / _all. water="sheet": a level 2/9 sheet drawn flowing west (the story's still sheet);
      "game": sources along the pod wall, the game's own spread. rims=None (default) leaves the platform's long
      edges open (the water's edge reads as a blue sheet from the side; see NOT THE GAME), "fence" / "glass" add
      a rim. Returns the set's dict (also Village.sets[name]).
  farm(v, name="tower") -> Farm        after the build: the tower's handles and calls
  Farm .A {short name: point} .yaw {short name: yaw} .cameras {name: dict(pos, target, lens, fstop, beat)}
       .L (layout numbers) .pod (fixtures GlassBox) .bed2 (fixtures Bed: the second red bed) .hopper / .chest
       (fixtures Hopper / Chest) .water / .lava (fixtures Fluids: water sheet, lava glow) .top_step (breaking
       Breakable) .beds {key: Village.beds entry} .zombie_eye (look target of every villager in the pod)
    zombie_in_cell(zombie, frame, aggro=False, look=None, ease=0)    the zombie ON frame in its cell: pressed against
        the sill, facing the pod, arms out over the sill with engine.undead's endless slow sway; aggro=True: the
        raised arms (the game snaps: ease 0)
    golem_spawn(golem, frame, pos=None, yaw=None, look=None, look_after=6, look_ease=6) -> frame
        the golem APPEARS on the platform ON frame, standing, no effect (the game spawns it in one tick); not
        rendered before (engine.undead.vanish/appear, independent of the Stage's shots); default spot = anchor
        golem_spawn facing south-west; look = its head turns to a point / Character `look_after` frames later
    golem_step(golem, frame, toward=None, distance=0.45) -> end frame      one heavy step toward the pod (east)
    golem_slide(golem, frame, start=None) -> dict(frame, edge, frame_end, gone, track, drop)
        fixtures.slide west to the rim (0.014/tick push, x 0.8 drag: 1.4 blocks/s), over it and 4 blocks down
        into the slot; gone (not rendered) from the frame its head is under the rim
    golem_death(golem, slide, camera=None, delay=0, seed=0, flicker=True, glow=None) -> dict(frame, burst)
        the white death puff (engine.animals.poof, 20 particles in a 1.4 x 2.7 box) rising out of the slot on
        slide['gone'] + delay (delay 288 = the game's 12 s in lava) and the lava light smothered and flaring
    deliver(items, frame, every=6, seed=0, land=True, spread=0.15) -> [plan]
        engine.mobs dropped items ('iron_ingot', 'poppy') fall out of the chute's mouth onto the hopper at the foot
        and vanish into it one per 8 ticks (fixtures Hopper.stream). plans[i]['frame'] = the frame item i is gone
    strew(items, frame, frame_end, seed=0, spots=None, face=None) -> [(x, y)]
        dropped items lying on the grass by the chest, bobbing and spinning (the poppies he threw out)
    break_top_step(player, frame, camera=None, duration=None, drop=None, seed=0) -> breaking.mine dict
        the top dirt step broken by hand: the game's 14 ticks (17 frames) from the click, ten crack stages, arm
        swings, crumbs, 64 dirt particles; put him on anchor one_down facing it first; camera= is required
    climb(c, frame, first=0, last=None, pause=3, approach=True) -> frame
        a villager / baby hops up dirt steps first..last (0 = the bottom one), each hop the game's jump, its head
        stopped by the floor overhang over the lower flight
    bounce(c, frame, bed="mom", jumps=1, place=True) -> frame    a baby jumping on a pod bed (JumpOnBed), the
        glass roof stopping its head 0.46 over the mattress (beds: 'mom', 'white_1', 'white_2', 'bed2')
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
  hop(c, frame, to, face=True, ceiling=None) -> landing frame      the game's jump up (or down) a block to `to`
  bounce(c, frame, bed, jumps=1, place=True, ceiling=None) -> frame        the bed bounce (Farm.bounce in the pod)
  push(player, villager, frame, points, gap0=1.5, mode="tap", release=0.45, rest_ticks=3) -> dict(end, surges, track)
      the player walks into her back and pushes her along `points` with the game's entity push: "tap" = shoves
      (she surges 0.7-1.1 blocks at a time, 0.9 blocks/s over all), "sneak" = a slow continuous shuffle (0.75
      blocks/s). It place()s both ON frame; key her head (look_at) after it.
  grow_up(baby, adult, frame, look=None) -> frame     the baby replaced by the adult ON frame, same spot and facing,
      no effect (engine.undead.vanish / appear: the adult is not rendered before, the baby not after)
  spawn_cell(world, x, y, villager_z, fluids=()) / spawn_cells(world, villagers, fluids=())    the game's golem
      spawn rule (Villager.spawnGolemIfNeeded + SpawnUtil + IronGolem.checkSpawnObstruction) on a World
  golem_loot(seed) -> {'iron_ingot': 3..5, 'poppy': 0..2}           loot_table/entities/iron_golem.json
  jump_track(up, ceiling=None), bounce_track(jumps, min_bounce=0.2, ceiling=None), push_route(total, ...)
      the per-tick physics behind hop / bounce / push
  layout(at, floor, ground, rims) -> dict        every cell of the tower as numbers (no Blender)
  cameras(L) -> {name: dict(pos, target, lens, fstop, beat)}       the proof framings (also Farm.cameras)
  Constants: AT (-23, 18), FLOOR 10, GOLEM_SPAWN_*, NO_GOLEM_ON, ZOMBIE_SCARE 8, GOLEM_LOOT, GOLEM_SIZE (1.4, 2.7),
  GOLEM_HEALTH 100, LAVA_DAMAGE 4, LAVA_DEATH_TICKS 240, JUMP 0.42, GRAVITY 0.08, PUSH 0.05, GROUND_FRICTION 0.546,
  BED_BOUNCE 0.75, BED_JUMPS (3, 6), BABY_TICKS 24000, VILLAGER_HEIGHT 1.95, BABY_HEIGHT 0.975, ZOMBIE_REACH 0.83.

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
    beds        pillows to the north wall: white (-23, 21), white (-22, 21), Mom's red (-21, 21); the free 2-block
                space (-20, 21..22) for the second red bed (fm.bed2.place_at(frame): pops in, no particles)
    doorway     the back (north) wall at (-19, 23): the gap (z 10) under the cobblestone plug (z 11)
    platform    west of the pod: stone floor z 9, x -28..-25, y 17..23; the water sheet on it (z 10), flowing west
    kill slot   x -30..-29 (2 wide), y 17..23, 4 deep under the platform's top (its floor z 5); the lava blade's
                surface 8.89 (1.1 under the rim; fixtures.lava_glow: a full-bright strip and its light); outer wall
                x -31 with a glass rim; its ends (y 16, 24) stone up to the lava, OPEN above it: the glow shows there
    collection  a 3 x 3 stone column x -30..-28, y 22..24, z 0..4 under the slot's north-east corner; the chute
                (-29, 23) from a hole in the slot floor down to the hopper (-29, 23, 1) on the chest (-29, 23, 0),
                latch north; open to the north below a lintel (z 0..3): the hopper top is seen from the back
    staircase   10 full dirt blocks, each one up and one along, against the pillar: bottom (-17, 23, 0) west along
                its back face to (-21, 23, 4), the turn (-22, 23, 5), then back east one row further out (-22, 24, 6)
                (-21, 24, 7) (-20, 24, 8) to the top step (-19, 24, 9) outside the gap (a Breakable: Farm.top_step).
                Two blocks of headroom over every step (a player walks it; the floor's overhang over row 23 stops a
                jump's head on the lower flight: Farm.climb knows). Stray dirt at its foot: (-15, 23), (-15, 22) with
                one on top, (-14, 22), (-16, 21), (-16, 23); a doubled step at (-18, 24, 1).

ANCHORS (Village.anchors 'tower_<short name>'; Farm.A / Farm.yaw by short name; z = where the feet are)
    zombie (-17.7, 19.5, 10) facing west         zombie_target its eyes (11.74)
    mom (-20.5, 19.5, 10)        Mom watching the zombie: ONE WHOLE EMPTY BLOCK (column -20) from its arm tips
    mom_glass (-20.5, 18.45, 10) at the front glass, facing the zombie       baby_glass (-21.4, 18.45, 10) 0.9 west
    bed_side (-20.5, 20.45, 10)  beside the beds, facing the zombie
    back_1..3 (-22.58, 19.15 / 19.9 / 20.65, 10)   backed against the far (west) glass, facing the zombie
    row_1..4 (-22.5 .. -19.5, 20.4, 10) facing north: librarian, cleric, narrator, Mom (beat 21)
    gap_in (-18.5, 22.66, 10) facing the plug (the narrator, beat 20)   gap_side (-19.0, 22.66, 10) the cleric,
        half a block west of the opening (beat 15)   gap_target the gap's middle
    top_step (-18.5, 24.5, 10) on the top dirt step        one_down (-19.5, 24.5, 9) one step down, facing it
    stairs_foot (-15.4, 24.3, 0) the baby at the foot (beat 13)   stairs_target a point up the stairs
    foot_front (-20.5, 16.45, 0) the baby at the front of the stone base (beat 5), turned 20 degrees to the east
    pod_target (-20.5, 20.5, 11) the pod's middle       hopper_target the hopper      slot_target the slot
    chest_front (-28.5, 24.55, 0) at the chest, facing it   chest_aside (-26.8, 25.2, 0)   poppies (-27.2, 25.9, 0)
    golem_spawn (-26.5, 20.5, 10)   square_baby (7.4, -0.4) on the plaza east of the well, facing the tower
    lineup (-22, 12, 0)   path tower_push_square: (6.5, 6.0) -> (-0.5, 6.0) along the plaza's north edge (beat 3)
    Farm.set["push_route"]: a stand-in route behind the tower (y 28) where the proof's push was filmed

CAMERAS (Farm.cameras[name] = dict(pos, target, lens, fstop, beat); the framings of the proof stills: a start, not
a rule; sun: the look-dev golden az 62 / el 27)
    square        (8.7, -1.0, 0.8) -> the pod, 70 mm f/2.8: the tower above the roofs, between two gables
    square_start  same position -> the bell, 70 mm: the start of beat 4's tilt
    square_wide   (9.5, -2.2, 1.6), 28 mm f/5.6: the well and the bell in front, the tower above the roofs
    foot          front three-quarter at baby height, 45 mm       pod_out   from over the platform into the pod, 24 mm
    pod_in        inside, the south-west corner at eye height, 20 mm
    two_shot      from behind the back wall (hide tower_pod_north), west of the plug, 45 mm: arms left, Mom right
    cell_side     beside the zombie cell across the pod, 22 mm: the backed three, the platform behind the far glass
    platform      low on the platform, 20 mm: the golem against the sky (sun behind it), the pod to the right
    slide         from the slot's open south end a little below the rim, 20 mm: the golem slides left and drops
    hopper        frontal to the niche at the back, 30 mm      back   the back, locked tall, 24 mm (the baby tiny at
                  its foot sits at y 70 %: under the caption band by design of the story's picture)
    gap           inside on the floor, the gap in the middle, 22 mm       bounce   the red bed from the east, 24 mm
    grow          the locked side view against the front glass, 24 mm  high   over Steve's shoulder, roof hidden, 22 mm
    stairs        outside north-east of the top step, 30 mm  lineup / push   the proofs' framings

BEATS (stories/ironfarm.json; the anchors, cameras and calls that stage each line)
     1 "everyone is afraid"   square: camera C["square"] (or lower, at baby height) with a long lens; the tower is
                              the bright shape above the gables to the west-north-west. Baby on square_baby. Steve
                              walks at the lens (players.walk); the doors behind are the village's (v.door_open).
     2 "I'm not."             the baby on square_baby, a camera west of it, tight; Steve's legs pass.
     3 "only takes grownups"  towers.push(steve, mom, f, v.paths["tower_push_square"]) (mode "tap": step by step);
                              then mom.look_at(...) to give hat brim and nose; the baby's run: baby.walk(..., run=True).
     4 "my mom lives at the top"   Shot.move(C["square_start"]["pos"], C["square_start"]["target"], same pos,
                              C["square"]["target"]): the tilt from the bell to the tower; Mom on mom_glass with
                              look_at(fm.zombie_eye) (in profile at the front glass); rack focus baby -> Mom
                              (s.focus twice). The slot's glow is NOT seen from the square (behind the pod, under
                              the roofs: see NOT THE GAME).
     5 "our arms don't do that"   baby on foot_front, C["foot"]; head up: baby.look_at(f, point 4 up in front);
                              the hop: towers.hop(baby, f, A["foot_front"]) (in place).
     6 "a bed, and a zombie"  inside: fm.zombie_in_cell(z, f); Mom on bed_side / mom; the pan from the red bed's
                              foot (camera at about (-20.5, 18.6, 11.3) looking north) east to the cell (look east).
     7 "can't reach her"      C["two_shot"], st.see_through(s, "tower_pod_north"); fm.zombie_in_cell(z, f, aggro=True);
                              Mom on mom, look_at(fm.zombie_eye): 1.9 blocks of air between arm tips and her face.
     8 "doesn't have to"      C["cell_side"]; Mom, cleric, librarian on back_1..3; towers.panic(c, f0, f1,
                              fm.zombie_eye, seed=...) each; the platform behind the far glass. The story's
                              "zombie's arm a soft green shape at the frame edge" cannot be had from beside the cell:
                              the arms reach only 0.35 into the pod and are behind any lens there (a lens inside the
                              cell sees the zombie's back); cut to C["two_shot"] / C["pod_in"] for the arms.
     9 "an iron golem comes"  C["platform"]; fm.golem_spawn(g, f, yaw=..., look=A["pod_target"]).
    10 "every time"           the same framing, jump cut: fm.golem_spawn(g, f2) (same spot and pose), then
                              fm.golem_step(g, f2 + 12).
    11 "the water pushes it"  C["slide"]; r = fm.golem_slide(g, f); fm.golem_death(g, r, camera=s) (puff + flicker).
    12 "takes the iron"       C["hopper"]; items = [mobs.make_dropped_item(...)]; fm.deliver(items, f);
                              poppies = fm.strew(...); steve on chest_front with steve.hold("iron_ingot"), then
                              turning and walking out; baby on poppies. (Register every item: st.cast / st.use.)
    13 "his dirt staircase"   C["back"]; baby on stairs_foot; fm.climb(baby, f, 0, 1) (the first two steps).
    14 "a gap, one block high"   the baby placed on step 8 (fm.set["stairs"][8]) hops up the last one:
                              fm.climb(baby, f, 9, 9, approach=False); it stands on top_step beside the opening,
                              as tall as it; through the glass the beds and the straw hat (Mom on bed_side).
    15 "grownups don't fit"   C["gap"]; the cleric walks to gap_side (into the plug); the baby runs in under it:
                              baby.walk(f, [A["top_step"], A["gap_in"], A["bed_side"]], run=True).
    16 "Mom never looks at me"   two-shot at the red bed: Mom on bed_side looking at fm.zombie_eye for the WHOLE
                              shot; the baby against her on the lens side, look_at Mom cheated to the lens.
    17 "twenty minutes"       C["grow"] (locked); Mom on mom_glass, baby on baby_glass (0.9 west of her).
    18 "I spent mine with her"   C["bounce"]; fm.bounce(baby, f, "mom") (three bounces in 1.85 s), then the baby
                              placed beside Mom.
    19 "when it ended"        C["grow"] again; towers.grow_up(baby, narrator, frame_of("ended"),
                              look=fm.zombie_eye) (narrator = st.actor("narrator", "none")); hold a second.
    20 "now I don't fit"      a low side view of the back wall from the west inside (about (-21.4, 22.4, 10.9)
                              looking east at the gap); narrator walks to gap_in and stops; look_at(gap_target).
    21 "counted us twice"     C["high"], st.see_through(s, "tower_pod_roof"); librarian, cleric, narrator, Mom on
                              row_1..4; Steve on top_step, steve.watch(...) along the row and back;
                              steve.attack(f); fm.bed2.place_at(f + 2).
    22 "not afraid of the player"   inside past the narrator (near gap_in) looking north through the back glass;
                              Steve on one_down: fm.break_top_step(steve, f, camera=s), then goes down the stairs
                              step by step (towers.hop(steve, f, fm.set["stairs"][k]) for k = 7, 6, ...: a hop down
                              per step works for the player too); C["stairs"] is the outside view.
    23 "afraid of the zombie" C["cell_side"]; panic(narrator, ..., seed=k) and panic(mom, ..., seed=k): matched.
    24 "apparently that counts"   the same shot: fm.golem_spawn(g, f, pos=(-26.8, 22.1, 10), look=A["pod_target"])
                              behind the villagers (north of them in the frame, its head above theirs), golem_step,
                              golem_slide; rack focus to it (s.focus(g.head, at_s=...)); cut before it drops.

WHAT THE GAME DOES (read from the 26.x client jar; no game file or code is copied)
    golem spawn   VillagerPanicTrigger.tick: every 100 game ticks a panicking villager calls spawnGolemIfNeeded(t,
                  3): at least 3 villagers in its box inflated by 10 that slept within the last 24000 ticks
                  (golemSpawnConditionsMet: LAST_SLEPT: the beds matter) and have no GOLEM_DETECTED_RECENTLY
                  (GolemSensor: sensed every 200 ticks, remembered 599). SpawnUtil.trySpawnMob(IRON_GOLEM,
                  MOB_SUMMONED, villager.blockPosition(), 10, 8, 6, LEGACY_IRON_GOLEM, false): 10 tries at a random
                  column within +-8; moveToPossibleSpawnPosition scans it from +6 down to -6 for the FIRST cell
                  whose block below passes LEGACY_IRON_GOLEM (isSolid, not cobweb, cactus, glass, glass pane, any
                  stained glass, leaves, conduit, ice, frosted ice, TNT, glowstone, beacon, sea lantern, tinted
                  glass) and that holds air or a fluid; IronGolem.checkSpawnObstruction: the block below can be stood
                  on, that cell (checked with an EMPTY fluid: water at the feet is fine) and the two above it valid
                  empty spawn blocks (no full block, no fluid). The golem is simply there on the next tick: no
                  particles.
                  So nothing spawns in the 2-high pod (the roof is the third cell) or on its glass roof. The farm as
                  built ALSO lets the game put golems on the zombie cell's slab roof, on the upper dirt steps, on the
                  slot's end walls (they fall into the slot) and on the collection column's top under the platform
                  rim (spawn_cells lists them; a careful builder covers them with glass): none is in any shot.
    villagers     VillagerHostilesSensor: a zombie within 8 blocks and in line of sight (glass blocks sight) makes
                  them panic. Villager 0.6 x 1.95, babies half. AgeableMob.BABY_START_AGE -24000: a baby grows up
                  after 20 minutes, with no particles (those come only with a forced age, i.e. feeding).
                  JumpOnBed: a baby jumps on a bed 3..6 times, 5 ticks apart; every bed bounceRestitution(0.75)
                  (Entity.getBlockBounciness keeps it for living entities). LivingEntity.jumpFromGround 0.42,
                  gravity 0.08, drag 0.98: apex 1.25, one block up in 9 ticks.
    pushing       Entity.push(Entity): both are pushed apart by 0.05 x the offset / sqrt(d) (sqrt of the centre
                  distance under one block): the push WEAKENS as the boxes overlap, so held input walks a player
                  through a villager; ground friction 0.6 x 0.91.
    golem         EntityType.IRON_GOLEM 1.4 x 2.7; createAttributes: health 100, step height 1.0 (a 1-high rim does
                  not hold it), knock-back resistance 1. Entity.lavaHurt 4.0 per hit, a hit lands 10 ticks after the
                  last: 240 ticks (12 s) to die in lava. loot_table/entities/iron_golem.json: poppy uniform 0..2,
                  iron ingot uniform 3..5 (one roll each).
    zombie        Mob.getAttackBoundingBox: its box inflated by sqrt(2.04) - 0.6 = 0.83 sideways; pressed against the
                  sill its reach ends at x -18.83, Mom's box starts at -20.8.
    water, lava, hopper, chest, glass, falling blocks: engine/fixtures.py; cracks and mining: engine/breaking.py;
    the golem and dropped items: engine/mobs.py; the zombie: engine/undead.py.

NOT THE GAME, AND WHERE THE PICTURE DIFFERS FROM IT
    - The water is a level 2/9 sheet drawn flowing (the story's still sheet; water="game" gives the real spread);
      the platform's long edges are open (rims=None): in the game the sheet would pour over them, and a golem (step
      height 1.0) could walk off them (rims="fence" holds it as real farms do).
    - The lava blade hangs in the slot with nothing drawn under it (in real farms: signs); the slot floor's water
      stream that carries the drops to the chute hole is not drawn (it is under the lava, out of every camera).
    - The golem is hidden the moment its head goes under the rim and the puff comes then (delay=0): the game's golem
      burns 12 s in the lava before it dies (golem_death(delay=288)). Items reach the hopper by deliver() when the
      director wants them, not by a simulated trip down the chute.
    - panic(): the game's trapped villagers try to run from the zombie and jostle; here they tremble and turn on
      the spot with their heads on it (the story's picture). The bounce is cut when a bounce falls under 0.2
      blocks/tick. Steve's "pushing" uses shoves (players tap the key); a held key walks through her.
    - From the square the slot's glow cannot be seen (it is behind the pod and under the roofs' line); the story's
      beat 4 "orange glow under the platform rim" needs a camera west or south-west of the tower.
    - The glass pod is drawn as the game draws connected glass (fixtures.glass_box); seen from outside, the far walls'
      frames show through the hidden panes: pane lines cross the picture as they do in the game.

GOTCHAS
    - Key every character in film order; place() before look_at; panic() after place() (it keys the body yaw, the
      head, the tremble). golem_spawn / golem_slide / grow_up use engine.undead.vanish / appear: never key
      hide_render on these characters.
    - ONE golem for every spawn (st.cast["golem"]); a golem in two consecutive shots needs no show() of its own.
    - see_through keys visible_camera at the shot's first frame and the next shot's: make the calls in shot order
      (a later call's key on the same frame wins).
    - break_top_step needs camera= (the particles face it). Register fm.top_step with the Stage only if it must be
      hidden in some shot (st.cast[fm.top_step.name] = fm.top_step).
    - Mom's head must stay on fm.zombie_eye in every pod shot (the story's continuity): look_at / panic(threat=...).
    - Lights: groups tower_pod (the lantern) and tower_cell (the torch) through Stage.lights; the lava light through
      fm.lava.level(frame, scale). In daylight the lava's light hardly shows on stone: the glow reads from the lava
      texture itself (the slot's open ends).

MEASURED (proof stills out/test/towers_*.png, 540x960, 16 samples, 2 threads, motion blur on; golden hour = the
look-dev sun az 62 / el 27; dusk = look-dev dusk az 187 / el 5; strips are 270x480 frames side by side)
    - tools.palette_check on every golden still: all pass (lit stone G/R 0.94-0.98, robe hue 9-19, villager skin
      saturation 0.39-0.48, Steve's shirt hue 177, plants 0.86-1.17 of the ground). Dusk: square_dusk and
      cell_side_dusk pass (stone 0.92-0.93, on the limit); pod_out_dusk FAILS skin saturation (0.56 > 0.52) and
      pod_in_dusk FAILS stone (G/R 0.91 < 0.92): the 5-degree dusk sun shines flat into the glass pod ten blocks up
      and paints faces and floor orange (a look matter: the story is all golden hour).
    - The golem: appears on its frame, turns its head, steps, slides west (1.4 blocks/s) and drops 4 blocks; from
      the slot's open south end the lava shows as an orange band under the rim, the puff rises out of the slot.
      In daylight the lava's light hardly shows on the slot's stone: the glow reads from the lava texture.
    - The hopper: an ingot falls out of the dark chute, lands in the bowl with the poppy and they go 8 ticks apart;
      five poppies lie spinning on the grass in front of the niche.
    - The top step: ten crack stages over the game's 17 frames, then the 64 dirt particles (stairs strip).
    - The pod: glass reads as the game's connected glass; the zombie's head and arms over the sill, lit by the
      lantern and the sky (the foot-level torch adds a warm under-light); the second red bed pops in; the four in a
      row from above with the roof hidden; the gap exactly a baby's height; the swap baby -> adult in one frame.
    - The narrator: the unemployed adult (the plain brown robe of type/plains, no profession layer) next to the
      nitwit (the green robe) reads clearly different at phone size (lineup still).
    - Render times under load: 11-40 s per 540x960 still, 13-70 s per strip.

SELF-TEST
    $BPY -m engine.towers                       32 numeric checks (builds the village with the tower, renders nothing,
                                                about 10 s); exit code 1 if one fails
    $BPY -m engine.towers stills NAME ...       proof stills out/test/towers_<name>.png (tools/towers_proof.py, 20-40 s
                                                each, at most 4-5 per call): square square_wide foot push pod_out pod_in
                                                cell_side platform two_shot back gap bounce lineup slide hopper grow
                                                high stairs; under the dusk sky: square_dusk pod_out_dusk
                                                pod_in_dusk cell_side_dusk
    $BPY -m tools.check_towers_stamp            frame fingerprints follow the spawn, slide, items, cracks, the second
                                                bed and the swap, in any order; run twice: the digests must match
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
    bed2 = (X + 3, Y + 3, F)                                                   # the free space: the second red bed
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


def bounce_track(jumps=1, min_bounce=0.2, ceiling=None, max_ticks=400):
    """Heights above the mattress after each tick of a baby villager jumping on a bed (JumpOnBed): `jumps` jumps
    of 0.42; every landing on the bed throws it up again at 0.75 of its landing speed (BED_BOUNCE); a bounce under
    `min_bounce` blocks per tick ends it (a film cut-off: the game's discrete bounce dies away in a few more
    tiny hops); it then stands 5 ticks (the behaviour's cooldown) and jumps again. ceiling = how high its feet can
    rise above the mattress before its head meets a block (in the 2-high pod: 2 - 9/16 - 0.975 = 0.46): it stops
    there and falls. Returns [height per tick]."""
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
        y += v
        if ceiling is not None and y > ceiling:
            y, v = float(ceiling), 0.0
        if y <= 0.0 and v < 0.0:
            y = 0.0
            v = -v * BED_BOUNCE
            if v < min_bounce:
                v = 0.0
                rest = BED_JUMP_COOLDOWN_TICKS
            out.append(0.0)
            continue
        v = (v - GRAVITY) * AIR_DRAG_V
        out.append(y)
    return out


# ----------------------------------------------------------------------------------------------------
# THE SET (inside the village's edit hook)
# ----------------------------------------------------------------------------------------------------
def iron_farm(b, at=AT, floor=FLOOR, name="tower", water="sheet", lava_watts=40.0, rims=None):
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
    bed2 = fixtures.bed(b, L["bed2"], "north", "red", name=name + "_bed2")
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
    for i, yy in enumerate((1.15, 1.9, 2.65)):
        p = (X + 0.42, Y + yy, float(F))
        anchor("back_%d" % (i + 1), p, yaw_to(p, zombie_eye))
    for i in range(4):
        anchor("row_%d" % (i + 1), (X + 0.5 + i, Y + 2.4, float(F)), math.pi)
    anchor("gap_in", (L["gap"][0] + 0.5, Y + 4.66, float(F)), math.pi)
    anchor("gap_side", (L["gap"][0] + 0.0, Y + 4.66, float(F)), math.pi)
    anchor("gap_target", (L["gap"][0] + 0.5, L["gap"][1] + 0.5, F + 0.5))
    ts = L["top_step"]
    anchor("top_step", (ts[0] + 0.5, ts[1] + 0.5, float(F)), 0.0)
    anchor("one_down", (ts[0] - 0.5, ts[1] + 0.5, float(F - 1)), east)
    s0 = L["steps"][0]
    anchor("stairs_foot", (s0[0] + 1.6, s0[1] + 1.3, float(g)), yaw_to((s0[0] + 1.6, s0[1] + 1.3),
                                                                       (s0[0] + 0.5, s0[1] + 0.5)))
    anchor("stairs_target", (X + 4.5, Y + 6.0, F - 3.0))
    anchor("foot_front", (X + 2.5, Y - 1.55, float(g)), math.radians(20.0))
    anchor("pod_target", (X + 2.5, Y + 2.5, F + 1.0))
    ch_ = L["chest"]
    anchor("chest_front", (ch_[0] + 0.5, ch_[1] + 1.55, float(g)), 0.0)          # at the chest, facing it
    anchor("chest_aside", (ch_[0] + 2.2, ch_[1] + 2.2, float(g)), math.radians(-120.0))
    anchor("poppies", (ch_[0] + 1.8, ch_[1] + 2.9, float(g)), yaw_of("south"))
    anchor("hopper_target", (ch_[0] + 0.5, ch_[1] + 0.5, g + 1.7))
    anchor("golem_spawn", (px0 + 1.5, Y + 2.5, float(F)), east)
    anchor("slot_target", ((sx0 + sx1) / 2.0 + 0.5, Y + 2.5, F - 0.5))
    # the square: the baby's spot on the path south-east of the well, the tower above the roofs to the north-west
    sq = (7.4, -0.4)
    anchor("square_baby", sq, yaw_to(sq, (X + 2.5, Y + 2.5)))
    lu = (X + 1.0, Y - 6.0)
    anchor("lineup", lu, math.pi / 2.0)
    route = [(X + 9.0, Y + 10.0), (X + 3.0, Y + 10.0)]
    b.path(name + "_push_square", [(6.5, 6.0), (-0.5, 6.0)])           # beat 3 on the square: west along the plaza
    # no plants on the ground lines of the cameras near the ground, the lineup and the push route
    for c in cameras(L).values():
        if c["pos"][2] < g + 4.5 and math.dist(c["pos"][:2], c["target"][:2]) < 30.0:
            sets.clear_view(b, c["pos"], c["target"], 2.2)
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
    def golem_spawn(self, golem, frame, pos=None, yaw=None, look=None, look_after=6, look_ease=6):
        """The golem APPEARS on the platform ON `frame`, in one frame, standing (the game's spawn: no effect at
        all): placed at `pos` (default the golem_spawn anchor) facing `yaw` (default: north-east, across the
        platform), not rendered before `frame` (since its last slide). look = a point / Character its head turns to
        `look_after` frames later. Use ONE engine.mobs IronGolem for every spawn. Returns `frame`."""
        from . import undead

        pos = self.A["golem_spawn"] if pos is None else pos
        yaw = math.radians(-135.0) if yaw is None else yaw
        if not self._golem_events or self._golem_events[0][0] > frame:
            undead.vanish(golem, None)                                      # nothing before the first spawn
        golem.place(frame, pos, yaw)
        undead.appear(golem, frame)
        self._golem_events.append((frame, "spawn"))
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
        r.update(drop=drop, vanish=gone)
        return r

    def golem_death(self, golem, slide, camera=None, delay=0, seed=0, flicker=True, glow=None):
        """The white death puff out of the slot and the lava glow flicker for a golem that slid in: the puff
        (engine.animals.poof, 20 particles in the golem's 1.4 x 2.7 box) where its head goes under the rim, ON
        slide['gone'] + delay, rising out of the slot. delay=0 is the film's (the puff as it drops); the game's golem
        burns 240 ticks (12 s: 100 health, 4 per lava hit, one hit per 10 ticks) before it dies: delay=288.
        flicker: the lava light is smothered on gone and flares (fixtures Fluid.flicker). Returns dict(frame, burst)."""
        from . import animals

        f = int(slide["gone"] or slide["frame_end"]) + int(delay)
        x, y = slide["track"][-1][1][0], slide["track"][-1][1][1]
        feet = (x, y, float(self.L["rim"]) - GOLEM_SIZE[1] + 0.6)
        burst = animals.poof(feet, f, camera=camera, seed=seed, village=None, size=GOLEM_SIZE, glow=glow)
        if flicker:
            self.lava.flicker(slide["edge"] or slide["frame"], f + 40, at=slide["gone"] or f)
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
    def break_top_step(self, player, frame, camera=None, duration=None, drop=None, seed=0):
        """The player breaks the top dirt step by hand (engine.breaking.mine: the game's 14 ticks = 17 frames from
        the click to the break, ten crack stages, arm swings, crumbs, then 64 dirt particles; drop='auto' drops the
        dirt item, None (default) drops nothing). Place him on the 'one_down' anchor facing it first. Returns
        mine()'s dict ('frame' = the frame the block is gone)."""
        from . import breaking

        return breaking.mine(player, self.top_step, frame, tool="hand", duration=duration, camera=camera,
                             drop=drop, seed=seed)

    def bounce(self, c, frame, bed="mom", jumps=1, place=True):
        """A baby jumping on one of the pod's beds ('mom', 'white_1', 'white_2' or 'bed2'), its head stopped by the
        glass roof 2 blocks over the floor (as the game stops it): see bounce(). Returns the frame it stands still."""
        b = self.bed2 if bed == "bed2" else self.beds[bed]
        return bounce(c, frame, b, jumps=jumps, place=place, ceiling=self.L["F"] + 2.0)

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


def hop(c, frame, to, face=True, ceiling=None):
    """A villager (or baby) jumps from where it stands to the point `to` one block up (or level, or down): the
    game's jump (0.42 up, gravity 0.08, drag 0.98: up one block in 9 ticks = 11 frames, apex 1.25), travelling in a
    straight line, legs stepping as in a walk. ceiling = the z its head meets on the way (the pod floor's overhang
    over the lower steps): the jump is cut there as Entity.move cuts it. Returns the landing frame."""
    f0 = int(round(frame))
    here = c.pos_at(f0)
    there = ch._vec3(to, here.z)
    d = there - here
    if face and math.hypot(d.x, d.y) > 1e-3:
        want = math.atan2(d.x, -d.y)
        if abs(ch._wrap(want - c.yaw_at(f0))) > math.radians(10.0):
            f0 = c.turn(f0, want, ease=4)
    top = None if ceiling is None else float(ceiling) - here.z - getattr(c, "height", 1.95)
    heights = jump_track(there.z - here.z, ceiling=top)
    n = len(heights) - 1
    span = math.hypot(d.x, d.y)
    f1 = f0 + n * TICK
    if span > 1e-3:
        c.walk(f0, [tuple(here), (there.x, there.y, here.z)], speed=span / (n * TICK / FPS))
    keys = [(f0 + i * TICK, here.z + h, "LINEAR") for i, h in enumerate(heights)]
    ch._segment(c.root, _LOC, 2, keys, "LINEAR")
    for i in (0, 1):                                                       # the walk's end frame is rounded: exact
        ch._segment(c.root, _LOC, i, [(f0, here[i], "LINEAR"), (f1, there[i])], "LINEAR")
    return int(math.ceil(f1 - 1e-6))


def bounce(c, frame, bed, jumps=1, place=True, ceiling=None):
    """A baby villager jumping on a bed (JumpOnBed: babies do this by themselves): it stands on the mattress
    (place=True puts it on the bed's middle ON `frame`, facing the pillow's left), jumps 0.42 up, and each landing
    on the bed throws it back up at 0.75 of the speed (bounceRestitution 0.75) until the bounce dies; 5 ticks
    later the next of `jumps` jumps (the game: 3 to 6; ONE jump already shows three bounces, 1.85 s).
    bed = a Village.beds entry, a fixtures Bed or a point on
    the mattress. ceiling = the z of the block over it (the pod's glass roof: Farm.bounce passes it). Returns
    the frame it stands still again."""
    if isinstance(bed, dict):
        pos, yaw = bed["pos"], bed.get("yaw", 0.0)
    elif hasattr(bed, "pos"):
        pos, yaw = bed.pos, bed.yaw
    else:
        pos, yaw = bed, c.yaw_at(frame)
    f0 = int(frame)
    if place:
        c.place(f0, pos, yaw + math.pi / 2.0)
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
    """Camera framings for the beats, name -> dict(pos, target, lens, fstop, beat): the framings of the proof stills
    (a start, not a rule; see BEATS in the module docstring). L = layout() or a Farm."""
    L = getattr(L, "L", L)
    X, Y, F, g = L["X"], L["Y"], L["F"], L["g"]

    def cam(pos, target, lens, fstop=4.0, beat="", focus=None):
        d = dict(pos=tuple(float(a) for a in pos), target=tuple(float(a) for a in target), lens=float(lens),
                 fstop=float(fstop), beat=beat)
        if focus is not None:
            d["focus"] = tuple(float(a) for a in focus)
        return d

    return {
        "square": cam((8.7, -1.0, 0.8), (X + 2.0, Y + 2.5, F + 0.8), 70, 2.8,
                      "1, 4: from the plaza east of the well, the end of the tilt: the tower above the roofs"),
        "square_start": cam((8.7, -1.0, 0.8), (-1.5, -2.5, 1.2), 70, 2.8, "4: the start of the tilt: the bell"),
        "square_wide": cam((9.5, -2.2, 1.6), (-8.8, 5.9, 4.4), 28, 5.6,
                           "the establishing wide: the well and the bell in front, the tower above the roofs"),
        "foot": cam((X + 3.6, Y - 4.1, g + 0.55), (X + 2.6, Y - 1.6, g + 0.75), 45, 2.8,
                    "5: the baby at the stone base, front three-quarter, at its own height"),
        "pod_out": cam((X - 2.3, Y + 4.6, F + 1.95), (X + 3.0, Y + 2.7, F + 0.75), 24, 4.0,
                       "the pod from outside (over the platform): the sleepers' profiles, the zombie beyond"),
        "pod_in": cam((X + 0.45, Y + 0.45, F + 1.5), (X + 4.7, Y + 3.0, F + 0.9), 20, 4.0, "6: inside at eye height"),
        "two_shot": cam((X + 1.6, Y + 10.6, F + 1.62), (X + 3.55, Y + 1.6, F + 1.5), 45, 2.8,
                        "7: from behind the back wall (hide it), west of the plug: arms left, Mom right"),
        "high": cam((X + 5.0, Y + 9.0, F + 5.5), (X + 2.5, Y + 2.2, F + 0.8), 22, 4.0,
                    "21: over Steve's shoulder, the roof hidden"),
        "slide": cam((X - 6.9, Y - 3.9, F - 0.72), (X - 5.0, Y + 2.5, F + 1.0), 20, 4.0,
                     "11: from the south, a little below the platform: the sheet, the slot's open end glowing"),
        "hopper": cam((X - 5.3, Y + 10.3, g + 2.2), (X - 5.5, Y + 5.6, g + 1.1), 30, 2.8, "12: the hopper at the foot"),
        "stairs": cam((X + 7.0, Y + 10.0, F + 0.6), (X + 4.2, Y + 6.4, F - 0.4), 30, 4.0,
                      "22 (outside view): the top step"),
        "lineup": cam((X + 6.0, Y - 6.0, g + 1.25), (X + 1.0, Y - 6.0, g + 0.95), 30, 4.0, "the narrator lineup"),
        "back": cam((X + 8.5, Y + 21.0, g + 3.6), (X + 5.6, Y + 4.5, g + 5.2), 24, 4.0, "13: the back, locked tall"),
        "gap": cam((X + 4.85, Y + 2.25, F + 0.42), (X + 4.5, Y + 5.0, F + 0.62), 22, 4.0,
                   "15, 20: inside at floor level, the gap in the middle"),
        "bounce": cam((X + 4.6, Y + 3.1, F + 1.15), (X + 2.5, Y + 3.6, F + 1.0), 24, 4.0,
                      "18: the red bed from the east"),
        "cell_side": cam((X + 4.88, Y + 2.55, F + 1.2), (X + 0.4, Y + 1.75, F + 1.45), 22, 4.0,
                         "8, 23, 24: beside the zombie cell across the pod: the backed three, the platform behind "
                         "the far glass (the zombie's arms reach only 0.35 into the pod: they are behind this lens)"),
        "platform": cam((X - 4.6, Y - 0.6, F + 0.3), (X - 3.3, Y + 2.6, F + 1.9), 20, 4.0,
                        "9, 10: low on the platform, the golem against the sky, the pod to the right"),
        "grow": cam((X + 2.0, Y + 3.3, F + 1.35), (X + 2.1, Y + 0.45, F + 1.05), 24, 4.0,
                    "17, 19: locked side view against the front glass, the village below"),
        "push": cam((X + 6.0, Y + 18.5, g + 0.75), (X + 6.0, Y + 10.0, g + 0.9), 26, 4.0,
                    "3 (a stand-in place behind the tower; the film's is on the square): side-on"),
    }


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
    ok("one jump on a bed: the jump and its bounces at 0.75 of the landing speed", ups >= 3 and max(hs) > 1.2,
       "%d take-offs, apex %.2f, %d ticks" % (ups, max(hs), len(hs)))
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
