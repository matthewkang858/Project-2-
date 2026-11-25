"""BLOCK BREAKING AND A ZOMBIE AT THE DOOR: the ten crack stages on doors and blocks, breakable blocks with the game's
particles and drops, mining by a player with the game's timing, and the zombie that bangs on a wooden door.

New module; edits no other file. Numbers are transcribed from the Java Edition 26.x client classes (named next to
each number, and collected in FACTS); textures and models are the game's own, through engine.mcassets / engine.blocks.
Blender axes as everywhere: +X east, +Y north, +Z up, 1 block = 1 unit, characters face -Y at yaw 0, 24 fps (the
game runs 20 ticks per second: 1 tick = 1.2 frames). "camera" = the Shot that films it, a Film, or a camera object
(particles face it, exactly as in engine.fx).

PUBLIC API (frames are film frames)

  THE CRACKS
  crack(target, frame, stage, half="upper")
      destroy_stage_<stage>.png (0..9) over the target from `frame` on; stage -1 = no cracks. target = a door prop
      (Village.doors["house_a"], engine.props.make_door) or a Breakable. On a door the cracks follow the door's own
      thin slab and sit on ONE half: half="upper" is the game's (DoorInteractGoal attacks the block above the
      zombie's feet), "lower" and "both" are film choices.
  crack_progress(target, frame_start, frame_end, first=0, last=9, clear=True, half="upper") -> [(frame, stage)]
      The stages first..last spread evenly over [frame_start, frame_end); clear=True removes them ON frame_end.
  stage_at(target, frame) -> int            the keyed stage (-1 = none)
  remove(target, frame) / restore(target, frame)
      The door or block is not rendered from `frame` on / is there again, uncracked (no effect, no particles).
  visible_texels(door, stage, eye, frame=None, half="upper") -> (seen, drawn)
      How many of that stage's crack texels on the door's front a camera at point `eye` sees past whoever stands
      in front of it (ray casts). Use it before a render: see MEASURED for why.

  A BLOCK THAT CAN BE BROKEN
  place_block(collection, block_id, cell, props=None, world=None, name=None, frame=None) -> Breakable
      One block as its own object, with the model, random variant, texture and tint engine.blocks would give it at
      that cell. world = the set's blocks.World or the Village: break particles and drops then land on the set.
      frame=None: there from the start; frame=f: placed ON f (not rendered before).
  place_from_world(collection, world, cells) -> [Breakable]     the same for cells a set left out of its mesh
  Breakable    .object (origin = the cell's min corner; key .object.location to move it) .cell .center .top
               .block_id .props .shape .particle_texture .name;  .crack(frame, stage) .stage_at(frame)
               .show(frame, visible) (the Stage's per-shot visibility: st.cast[b.name] = b; st.use(shot, b))
               .remove(frame) .restore(frame) .there_at(frame)
  break_block(block, frame, camera=None, drop=None, tool="hand", seed=0, glow=0.0, particles=True, until=None)
      -> dict(frame, burst, item, drop)
      The block is gone ON `frame` and the game's break particles fly (ClientLevel.addDestroyBlockEffect: 64 for a
      full cube; a grass block's are plain dirt, NOT tinted green). drop: None = nothing, "auto" = what the game
      drops for `tool` (drops()), or an item id: an engine.mobs dropped item pops out of the middle of the block
      with the game's toss, falls to the floor under the cell and bobs and spins until `until` (default frame +
      120). dict["item"] is the engine.mobs DroppedItem (item.pick_up(frame): the game lets a player take it
      PICKUP_DELAY_TICKS = 10 ticks = 12 frames after it appeared; register it with the Stage like any other).
  break_ticks(block_id, tool="hand", exact=True, hardness=None, efficiency=0, haste=0, on_ground=True,
              in_water=False) -> int
      Game ticks from the click to the break (0 = it breaks on the click), by BlockBehaviour.getDestroyProgress
      and Player.getDestroySpeed. exact=False is the textbook formula: stone by hand 150 ticks = 7.5 s, dirt 15 =
      0.75 s, netherrack 40 = 2 s. exact=True (default) adds the per-tick progress in single precision as the
      client does: dirt 15, but stone 151 (7.55 s) and netherrack 41, because the 150th / 40th float sum is
      0.9999993 / 0.9999996. Golden pickaxe on netherrack: 0. break_seconds / break_frames: the same in seconds /
      film frames (stone by hand 181 frames). TIMES lists both counts for 22 block-and-tool pairs.
  drops(block_id, tool="hand") -> item id | None      stone by hand None, with a pickaxe "cobblestone"; dirt "dirt".
  mine(player, block, frame_start, tool="auto", duration=None, camera=None, drop="auto", seed=0, glow=0.0,
       crumbs=True, swing=True, until=None) -> dict(start, frame, ticks, frames, stages, swings, burst, item,
                                                    instant, tool, drop)
      The player's mining arm (engine.fx.mining_swings: a swing every 4 ticks = 4.8 frames) while the cracks climb,
      then the break on dict["frame"] with particles and the drop. duration=None: the game's time for block and
      tool; duration=48: the same ten stages in 48 frames (11 swings instead of 38: a 7.5 s fist-mining read in
      2 s). tool="auto" = what the player holds in the right hand (engine.players), else the bare hand. crumbs =
      the one small crumb per tick that flies off the face being hit. Call it AFTER the player's place() /
      look_at(); works with engine.players and engine.characters players.
  dig(player, blocks, frame_start, tool="auto", duration=None, **mine_kw) -> [dict, ...]
      Several blocks one after the other with the button held: the next block is started 6 ticks after a break
      (MultiPlayerGameMode's 5-tick cooldown), 1 tick after an instant one; one unbroken run of arm swings.

  THE ZOMBIE AT THE DOOR
  door_info(door) -> dict(cell, upper, floor, normal, along, front, center, width, thickness, hinge, yaw, height)
      Where a door prop is when closed: `normal` points out of its FRONT (the side its slab is flush with: for the
      village houses the street side), `along` from the hinge to the free edge, `center` = middle of the front
      face at floor level.
  stand_point(door, side="front", gap=None, along=0.0) -> ((x, y, z), yaw)
      Where a mob pressed against the door stands: gap = distance of its centre from the door's face (default 0.3:
      a zombie's hit box is 0.6 wide and the goal needs it to be walking INTO the door), along = sideways shift
      toward the free edge (negative: toward the hinge).
  bang_on_door(zombie, door, frame_start, frame_end, attempt=None, phase=0.0, pause=2, every=None, first=2,
               seed=None, half="upper", arms="raised", place=True, side="front", gap=None, along=0.0,
               shudder=0.0, hit_delay=HIT_DELAY, break_door=False, camera=None, crumbs=0, glow=0.0, drop=False,
               world=None)
      -> dict(stand, yaw, knocks, hits, stages, resets, frame, burst, item, phase, attempt)
      BreakDoorGoal on film: the zombie (engine.undead) stands against the door, an arm swing starts on every
      frame of `knocks`, the cracks climb 0..9 over `attempt` frames (default the game's 240 ticks = 288 frames),
      and when an attempt ends without the door breaking they are cleared for `pause` frames and start over, for as
      long as asked. phase = how far the first attempt already is at frame_start (0..1); dict["phase"] is the value
      to pass to the next call when a later shot continues the knocking (with place=False). every = frames between
      swings (default 31.2, the game's average; 16 reads as hammering); seed=1 draws the game's irregular rhythm
      instead (a draw can stay silent for seconds: look at dict["knocks"]). arms "raised" = the -120 degrees of a
      zombie that has a target (it has: whoever is behind the door), "out" = -80 degrees. hits = knocks +
      HIT_DELAY (5 frames): the frame the chop is at its lowest.
      shudder > 0: the door jolts on each hit (see shudder()). crumbs=N: N small crumbs off the door per hit (a
      film garnish). break_door=True: the door breaks (Hard difficulty): with attempt=None the one attempt is
      timed to end ON frame_end, the door is gone on that frame and the particles fly (the game's: 32, of the
      LOWER half only, see below; break_door="both" for both halves, 64); drop=True also drops the oak_door item.
      world = the Village, for the particles to land on.
  shudder(door, frame, amount=1.0) -> end frame
      NOT the game (a door does not move when hit): the free edge swings SHUDDER_PIXELS (0.5 texture pixel) x amount
      inward about the hinge on `frame`, rebounds 45 %, and is at rest 3 frames later. See MEASURED for what reads.
  break_door(door, frame, camera=None, halves=("lower",), seed=0, glow=0.0, drop=False, until=None, world=None)
      -> dict(frame, burst, item)          the door is gone ON `frame`, with break particles of the halves named.
  door_torches(village, name="house_a") -> [lights]
      The village merges the two wall torches beside a door into ONE point light half way between them: at
      house_a that is inside the head of a zombie at the door. This gives each torch its own light (same total
      energy, same light group, known to Stage.lights) and switches the merged one off. Call it once, before
      Stage.lights, in every film with somebody on the doorstep at night.
  Constants: TICK, DOOR_BREAK_TICKS, DOOR_KNOCK_ODDS, DOOR_SWING_MEAN_FRAMES, HIT_DELAY, SHUDDER_PIXELS,
  DESTROY_COOLDOWN_TICKS, PICKUP_DELAY_TICKS, TOOL_SPEED, BLOCKS (id -> hardness, tool class, needs the tool for
  drops, tier), TIMES, FACTS, DOOR_CAM / FILM_STAGING (the proof cameras and staging for house_a's door).

USING IT IN A FILM (st = films.lookdev.Stage, v = the Village, s = a shot)
    door = v.doors["house_a"]; breaking.door_torches(v, "house_a")          # once, before st.lights
    z = undead.add_zombie(st, "zombie"); st.use(s, z)
    r = breaking.bang_on_door(z, door, s.frame_start, s.frame_end + 1, attempt=48, phase=0.35, every=16,
                              half="both", along=-0.3, shudder=4)
    # next shot, the same knocking from elsewhere:
    breaking.bang_on_door(z, door, s2.frame_start, s2.frame_end + 1, attempt=48, phase=r["phase"], every=16,
                          half="both", along=-0.3, shudder=4, place=False)
    # the morning after: flesh = mobs.make_dropped_item("rotten_flesh"); flesh.place(f, breaking.stand_point(door)[0])
    rock = breaking.place_block(v.collection, "stone", (-3, 31, 0), world=v); st.cast[rock.name] = rock; st.use(s, rock)
    steve.place(f0, (-2.5, 30.15, 0.0), math.pi); steve.look_at(f0, rock.center, ease=0)
    m = breaking.mine(steve, rock, f0 + 6, duration=48, camera=s)           # breaks on m["frame"], drops nothing
    A HOLE IN A FLOOR (the set leaves the cells out of its mesh and breakable blocks fill them; top block first):
        a set of its own:  cells = [(x, y, 0), (x, y, -1)];  w.build(coll, "floor", skip=cells)
                           blocks = breaking.place_from_world(coll, w, cells)
        in the village:    inside the build_village(edit=hook) hook: st = {c: b.w.get(*c) for c in cells}, then
                           b.w.set(x, y, z, None) for each cell, and dirt set under and around them (the village's
                           terrain is ONE block thick: under the grass there is nothing); after the build
                           blocks = [breaking.place_block(v.collection, st[c][0], c, st[c][1], world=v)
                                     for c in cells]
        breaking.dig(player, blocks, f0, tool="golden_pickaxe", camera=s)
    A cell skipped by build() stays in w, so the set draws its neighbours' faces toward it; particles and drops
    treat a cell as solid only while its block is there. An item lying on a block that is broken later does not
    fall: pick_up() it. A block that is already part of the built Village's meshes can only be taken out with
    engine.fx.extract_block (its cracks are fx.Block.crack: an animated material, see the stamp note in
    CONTRACT.md).

WHAT THE GAME DOES (read from the classes; FACTS has the numbers)
  cracks    LevelRenderer.submitBlockDestroyAnimation draws the block's OWN model parts again (so on a door only
            its 3-pixel slab) through SheetedDecalTextureGenerator with render type "crumbling": the texture
            coordinate is the block-local position projected along the face direction (one destroy_stage texel per
            block pixel, aligned to the block's pixel grid, texture scale 1), texels under alpha 0.1 discarded,
            blend (DST_COLOR, SRC_COLOR) = 2 x crack x what is drawn there, depth test with a bias (factor 1,
            units 10) and no depth write. The crack texture has two greys: 61 (darkens to 48 %) and 155 (brightens
            by 22 %); it is never white lines. Over a cut-out texel (the door's window) the crack multiplies
            whatever is seen through the hole. An optional "OIT" graphics mode uses destroy_oit_stage_N.png instead.
  mining    progress per tick = speed / hardness / (30 with the right tool for drops, else 100); speed = the
            tool's (wood 2, stone 4, copper 5, iron 6, diamond 8, netherite 9, gold 12) on blocks of its class,
            else 1; + efficiency^2 + 1; x (1 + 0.2 haste); / 5 off the ground; x 0.2 under water. The tick of the
            click shows nothing, each later tick adds progress and shows stage (int)(progress x 10); the block
            breaks on the tick progress reaches 1, then nothing can be hit for 5 ticks. Progress >= 1 per tick
            breaks on the click (golden pickaxe on netherrack), with no pause after it. The arm swings on every
            tick of mining, cooldown included. Drops: Block.popResource (middle of the block +- 0.25, the item
            entity's own toss).
  the door  BreakDoorGoal (Zombie, priority 1, only for the zombies that "can break doors": chance 0.1 x the local
            difficulty's special multiplier at spawn, and only while the difficulty is HARD: on Easy and Normal a
            26.x zombie does not touch a door at all). breakTime counts 240 ticks = 12 s; stage =
            (int)(breakTime / 240 x 10) on the UPPER door block; each tick 1 chance in 20 of the knock sound
            (level event 1019) and, if no swing is running, an arm swing (so one every 26 ticks on average); at
            240 the upper block is removed WITHOUT particles (the 2001 event is sent with the air that is there
            by then), the lower half then breaks with its own 32 particles and drops the door item. The attempt
            is abandoned, cracks cleared, when the zombie is 2 blocks from the door block's centre, the door opens
            or the difficulty changes. The door never moves. The zombie stands where it was walking into the
            door: hit box 0.6 wide touching it, so its centre is 0.3 from the face and its arms (0.65 past the
            centre) reach THROUGH the door. Its arms are raised (ZombieAttackGoal: it has a target).
            "Knocks all night, the cracks climb and reset, the door holds" is how players remember older versions
            on Easy and Normal (before about 1.14: from memory, not read from classes here); it is what
            bang_on_door without break_door films.

MEASURED (`$BPY -m engine.breaking` asserts the numbers; stills out/test/breaking_*.png)
  house_a's door: cells (10, -8, 1) and (10, -8, 2), slab x 10.0 .. 10.1875 flush with the west wall face, front =
  west = the plaza, hinge on the north side. Zombie stand point (9.7, -7.5, 1.0), yaw +90 degrees: on the top of
  the door step. The two wall torches are at (9.71, -6.5 / -8.5, 2.89): level with a zombie's head, one block
  either side of it (tangents!).
  THE ZOMBIE HIDES THE CRACKS. From straight behind (DOOR_CAM["plaza"]), a zombie in the game's place with raised
  arms leaves a third of the upper half's face and half of the lower half's visible (32 % / 50 % of the texels on
  one frame). On the proof stills the lens sees 0 of the 18 crack texels of stage 2, 5 of 55 of stage 5, 45 of
  145 of stage 9 (breaking_zombie_s2/5/9.png: the game's own picture, and until stage 9 it does not read: the
  cracks start in the middle of the block, behind his head). What reads (breaking_zombie_film_s*.png):
  half="both", the zombie 0.3 toward the hinge (along=-0.3) and the camera 27 degrees off the door's axis on the
  side of its free edge (DOOR_CAM["side"]): 17 of 36 texels at stage 2, 70 of 110 at stage 5, 164 of 290 at
  stage 9. A camera on the hinge side with the zombie toward the free edge shows as many cracks but hides the
  edge that shudders.
  Arm swing started on frame f: the arms move from f + 1.2, are lowest at f + 5.4 and back at f + 9.
  Shudder (breaking_blow_*.png, six frames around a hit at the 540x960 pixel density): amount 1.5 (0.75 pixel of
  travel, the "fraction of a pixel") cannot be told from no shudder; amount 4 (2 pixels, 7 degrees) is a faint
  blur on the free edge; amount 8 (4 pixels, 14 degrees) smears the whole door for three frames and opens a slit
  at the jamb: a kick that reads. What carries the knocking at any amount is the arm swing and the cracks.
  A 540x960 still of the doorstep at night takes 50-80 s at 16 samples on 2 threads of a loaded machine.

NOT THE GAME, AND WHERE THE PICTURE DIFFERS FROM IT
  - The cracks are not a second layer of geometry: each stage is a copy of the door / block whose own material is
    multiplied by the crack texel (x (2c)^2.2 in scene-linear light: 0.20 and 1.54), and exactly one copy is
    rendered at a time. So nothing can z-fight at any distance or shutter, and engine.stamp sees a stage change as
    another object (no animated material: fingerprints are the same in every process and in any frame order).
    The game multiplies the finished pixel in display space; here the texture colour is multiplied before
    lighting: the same for diffuse light, while the small specular term stays uncracked, the exponent 2.2 stands
    in for the sRGB curve (a dark texel is 0.20 here, 0.20-0.26 in the game depending on how bright the pixel is)
    and the result is clipped at albedo 1 instead of at display white. The game also fogs the crack colour with
    distance; here haze is the look's. Over the door's window holes a crack texel is a tinted transparent surface.
    Compared with the game by reading its code and textures, not side by side with a screenshot.
  - shudder(), arms eased or not, attempt / phase / every, half "lower" / "both", along and duration: film choices.
  - Break particles and mining crumbs are engine.fx's terrain particles (camera-facing quads, lit by the set; at
    night pass glow=0.2 if they must read). Mining crumbs do not collide with the block being mined.
  - Not built: the door's two halves breaking separately (both vanish on the same frame), sounds, falling blocks
    (a Breakable is its own object: key .object.location), cracks on engine.fx.extract_block blocks, random
    offsets of plants, fluids, chests, item pick-up flight, swords and shears as tools (they mine like a hand).

GOTCHAS
  - Never key hide_render on a cracked door, a Breakable or their children: use crack / remove / restore / show.
    Any number of calls in any frame order is fine (the visibility keys are rewritten from the whole history).
  - A cracked door is rendered through its cracked copies (children of the door object, which is hidden
    meanwhile): aim cameras and focus at the door object itself or at a point; it still carries the transform.
  - Key the zombie in frame order (place, then bang_on_door), like every Character; bang_on_door owns its arms.
  - Particles need camera= (the Shot) or a scene camera; a cut that jumps in time needs fx.stop_particles(frame).
  - The crack stages and the door's absence are CONSTANT keys on integer frames (safe with the 0.5-frame shutter).
  - A film that imports engine.breaking has this file in its engine hash: freeze it while finals render.

SELF-TEST
    $BPY -m engine.breaking                    37 numeric checks, no rendering (5 s; exit code 1 if one fails)
    $BPY -m engine.breaking stills NAME ...    proof stills out/test/breaking_<name>*.png; names: PROOFS (one or
                                               two names per call stay under the 300 s limit)
    $BPY -m tools.check_breaking_stamp         frame fingerprints: sensitive to every stage, the same in any order
"""
import math
import types

import bpy
import numpy as np
from mathutils import Matrix, Vector

from . import blocks as _blocks
from . import fx
from . import mcassets as mc

FPS = 24
TICK = FPS / 20.0                    # frames per game tick
CRACK_UV = "breaking_crack"          # the mesh UV layer that carries the game's decal projection

# ---- BreakDoorGoal / DoorInteractGoal / Zombie
DOOR_BREAK_TICKS = 240               # BreakDoorGoal.DEFAULT_DOOR_BREAK_TIME (getDoorBreakTime = max(240, own))
DOOR_KNOCK_ODDS = 20                 # BreakDoorGoal.tick: random.nextInt(20) == 0 -> level event 1019 + swing
DOOR_GIVE_UP_DISTANCE = 2.0          # canContinueToUse: doorPos.closerToCenterThan(mob.position(), 2.0)
DOOR_START_DISTANCE = 1.5            # DoorInteractGoal.canUse: distanceToSqr(door x, mob y, door z) <= 2.25
ZOMBIE_WIDTH = 0.6                   # EntityType.ZOMBIE hit box; DoorInteractGoal.canUse needs horizontalCollision
ZOMBIE_SWING_TICKS = 6               # LivingEntity swing; a new one only when none is running (!isSwinging())
DOOR_SWING_MEAN_FRAMES = (DOOR_KNOCK_ODDS + ZOMBIE_SWING_TICKS) * TICK    # 31.2: a draw every tick once it is over
HIT_DELAY = 4 * TICK                 # frames from the start of a swing to the "blow": the arms at the end of the chop
SHUDDER_PIXELS = 0.5                 # film choice: travel of the door's free edge on a blow, in texture pixels
SHUDDER_SHAPE = (1.0, -0.45, 0.2, 0.0)   # the door's angle on the blow frame and the three frames after it
# ---- MultiPlayerGameMode / BlockBehaviour.getDestroyProgress / Player.getDestroySpeed / ToolMaterial
DESTROY_COOLDOWN_TICKS = 5           # MultiPlayerGameMode.DEFAULT_DESTROY_COOLDOWN_TICKS (destroyDelay after a break)
CORRECT_TOOL_DIVISOR = 30.0          # getDestroyProgress: speed / hardness / 30 with the right tool for drops ...
WRONG_TOOL_DIVISOR = 100.0           # ... / 100 without
TOOL_SPEED = {"wooden": 2.0, "stone": 4.0, "copper": 5.0, "iron": 6.0, "diamond": 8.0, "netherite": 9.0,
              "golden": 12.0}        # ToolMaterial WOOD .. GOLD: speed
TOOL_TIER = {"wooden": 0, "golden": 0, "stone": 1, "copper": 1, "iron": 2, "diamond": 3, "netherite": 4}
# ---- crumbling (RenderPipelines.CRUMBLING, core/rendertype_crumbling.fsh, SheetedDecalTextureGenerator)
CRACK_ALPHA_CUT = 0.1                # if (color.a < 0.1) discard
CRACK_DEPTH_BIAS = (1.0, 10.0)       # DepthStencilState(GREATER_THAN_OR_EQUAL, no write, bias factor 1, constant 10)
CRACK_GAMMA = 2.2                    # 2 x crack x pixel in display space = x (2 crack)^2.2 in scene-linear light
# ---- Block.popResource / ItemEntity
DROP_SPREAD = 0.25                   # spawn at the block centre +- 0.25 on each axis, minus half the item's height
DROP_ITEM_HEIGHT = 0.25              # EntityType.ITEM: 0.25 x 0.25
DROP_TOSS = (0.1, 0.2)               # new ItemEntity(level, x, y, z, stack): velocity (+-0.1, 0.2, +-0.1) per tick
PICKUP_DELAY_TICKS = 10              # ItemEntity.setDefaultPickUpDelay (popResource calls it): then a player takes it
ITEM_GRAVITY, ITEM_DRAG = 0.04, 0.98

# Blocks: strength(hardness[, resistance]) and requiresCorrectToolForDrops() from net.minecraft.world.level.block
# .Blocks; tool class from data/minecraft/tags/block/mineable/<class>.json; tier from needs_stone / _iron /
# _diamond_tool.json (wood and gold tools 0, stone and copper 1, iron 2, diamond 3, netherite 4).
# id -> (hardness, tool class | None, needs that tool for drops, lowest tier that drops)
BLOCKS = {
    "stone": (1.5, "pickaxe", True, 0), "cobblestone": (2.0, "pickaxe", True, 0),
    "mossy_cobblestone": (2.0, "pickaxe", True, 0), "stone_bricks": (1.5, "pickaxe", True, 0),
    "smooth_stone": (2.0, "pickaxe", True, 0), "andesite": (1.5, "pickaxe", True, 0),
    "granite": (1.5, "pickaxe", True, 0), "diorite": (1.5, "pickaxe", True, 0), "tuff": (1.5, "pickaxe", True, 0),
    "deepslate": (3.0, "pickaxe", True, 0), "sandstone": (0.8, "pickaxe", True, 0),
    "bricks": (2.0, "pickaxe", True, 0), "netherrack": (0.4, "pickaxe", True, 0),
    "nether_bricks": (2.0, "pickaxe", True, 0), "basalt": (1.25, "pickaxe", True, 0),
    "blackstone": (1.5, "pickaxe", True, 0), "gilded_blackstone": (1.5, "pickaxe", True, 0),
    "polished_blackstone": (2.0, "pickaxe", True, 0), "polished_blackstone_bricks": (1.5, "pickaxe", True, 0),
    "cracked_polished_blackstone_bricks": (1.5, "pickaxe", True, 0), "magma_block": (0.5, "pickaxe", True, 0),
    "end_stone": (3.0, "pickaxe", True, 0), "obsidian": (50.0, "pickaxe", True, 3),
    "ancient_debris": (30.0, "pickaxe", True, 3), "netherite_block": (50.0, "pickaxe", True, 3),
    "coal_ore": (3.0, "pickaxe", True, 0), "iron_ore": (3.0, "pickaxe", True, 1),
    "gold_ore": (3.0, "pickaxe", True, 2), "diamond_ore": (3.0, "pickaxe", True, 2),
    "nether_gold_ore": (3.0, "pickaxe", True, 0), "iron_block": (5.0, "pickaxe", True, 1),
    "gold_block": (3.0, "pickaxe", True, 2), "diamond_block": (5.0, "pickaxe", True, 2),
    "anvil": (5.0, "pickaxe", True, 0), "furnace": (3.5, "pickaxe", True, 0), "iron_bars": (5.0, "pickaxe", True, 0),
    "ice": (0.5, "pickaxe", False, 0),
    "dirt": (0.5, "shovel", False, 0), "coarse_dirt": (0.5, "shovel", False, 0),
    "grass_block": (0.6, "shovel", False, 0), "dirt_path": (0.65, "shovel", False, 0),
    "farmland": (0.6, "shovel", False, 0), "sand": (0.5, "shovel", False, 0), "gravel": (0.6, "shovel", False, 0),
    "clay": (0.6, "shovel", False, 0), "soul_sand": (0.5, "shovel", False, 0),
    "snow_block": (0.2, "shovel", True, 0),
    "oak_planks": (2.0, "axe", False, 0), "oak_log": (2.0, "axe", False, 0),
    "stripped_oak_log": (2.0, "axe", False, 0), "oak_door": (3.0, "axe", False, 0),
    "oak_fence": (2.0, "axe", False, 0), "crafting_table": (2.5, "axe", False, 0), "chest": (2.5, "axe", False, 0),
    "bookshelf": (1.5, "axe", False, 0), "lectern": (2.5, "axe", False, 0), "composter": (0.6, "axe", False, 0),
    "pumpkin": (1.0, "axe", False, 0), "melon": (1.0, "axe", False, 0),
    "oak_leaves": (0.2, "hoe", False, 0), "hay_block": (0.5, "hoe", False, 0),
    "glass": (0.3, None, False, 0), "glowstone": (0.3, None, False, 0),
    "tnt": (0.0, None, False, 0),            # instabreak()
    "bedrock": (-1.0, None, False, 0),       # strength(-1): getDestroyProgress returns 0
}
# data/minecraft/loot_table/blocks/<id>.json without silk touch, where it is not the block itself (None = nothing)
_DROPS = {
    "stone": "cobblestone", "deepslate": "cobbled_deepslate", "grass_block": "dirt", "dirt_path": "dirt",
    "farmland": "dirt", "glass": None, "ice": None, "oak_leaves": None, "glowstone": "glowstone_dust",
    "coal_ore": "coal", "iron_ore": "raw_iron", "gold_ore": "raw_gold", "diamond_ore": "diamond",
    "nether_gold_ore": "gold_nugget", "clay": "clay_ball", "melon": "melon_slice", "snow_block": "snowball",
    "bookshelf": "book", "bedrock": None,
}

FACTS = {
    "door_break_ticks": DOOR_BREAK_TICKS, "door_break_seconds": DOOR_BREAK_TICKS / 20.0,
    "door_break_frames": DOOR_BREAK_TICKS * TICK, "door_knock_odds_per_tick": 1.0 / DOOR_KNOCK_ODDS,
    "door_knock_mean_frames": DOOR_KNOCK_ODDS * TICK, "door_cracked_half": "upper",
    "door_break_difficulty": "hard", "door_break_chance_max": 0.1, "door_give_up_distance": DOOR_GIVE_UP_DISTANCE,
    "door_break_particles": 32, "door_break_particles_half": "lower",
    "zombie_gap": ZOMBIE_WIDTH / 2.0, "zombie_swing_ticks": ZOMBIE_SWING_TICKS,
    "destroy_cooldown_ticks": DESTROY_COOLDOWN_TICKS, "crack_stages": 10, "crack_alpha_cut": CRACK_ALPHA_CUT,
    "crack_blend": "DST_COLOR, SRC_COLOR", "crack_depth_bias": CRACK_DEPTH_BIAS, "crack_texture_scale": 1.0,
    "crack_greys": (61, 155), "drop_spread": DROP_SPREAD, "drop_toss": DROP_TOSS,
}


# ----------------------------------------------------------------------------------------------------
# keyframe plumbing
# ----------------------------------------------------------------------------------------------------
def _alive(idb):
    """True for a datablock reference that still exists (False after the scene it lived in was reset)."""
    try:
        return idb is not None and bool(idb.name)
    except ReferenceError:
        return False


def _fcurve(idb, path, index=0):
    """F-curve idb.<path>[index], creating action, slot and curve as needed (Blender 5 layered actions)."""
    ad = idb.animation_data or idb.animation_data_create()
    if ad.action is None:
        ad.action = bpy.data.actions.new(idb.name + "_brk")
    return ad.action.fcurve_ensure_for_datablock(idb, path, index=index)


def _keys(idb, path, frames, values, interp="CONSTANT", index=0):
    """Replace a channel by the given keys (all with one interpolation mode)."""
    fc = _fcurve(idb, path, index)
    kps = fc.keyframe_points
    while len(kps):
        kps.remove(kps[len(kps) - 1], fast=True)
    n = len(frames)
    kps.add(n)
    co = np.empty(2 * n, dtype=np.float32)
    co[0::2] = frames
    co[1::2] = values
    kps.foreach_set("co", co)
    for kp in kps:
        kp.interpolation = interp
    fc.update()
    return fc


def _at(history, frame, default):
    """Value of a {frame: value} history at `frame` (the latest entry at or before it)."""
    best, out = None, default
    for f, v in history.items():
        if f <= frame + 1e-9 and (best is None or f > best):
            best, out = f, v
    return out


# ----------------------------------------------------------------------------------------------------
# the crack: destroy_stage_N as a multiplier on the block's own material
# ----------------------------------------------------------------------------------------------------
def crack_factors(stage):
    """destroy_stage_<stage>.png as the game blends it: (16x16x3 float multipliers in scene-linear light, 16x16
    bool mask of the texels that are drawn). 2 x crack x pixel in display space; texels under alpha 0.1 discarded."""
    a = np.asarray(mc.texture_array("block/destroy_stage_%d" % int(stage)), dtype=np.float32) / 255.0
    if a.shape[:2] != (16, 16):
        raise ValueError("breaking: destroy_stage_%d is not 16x16" % stage)
    mask = a[..., 3] >= CRACK_ALPHA_CUT
    mul = np.ones((16, 16, 3), dtype=np.float32)
    mul[mask] = np.power(2.0 * a[..., :3][mask], CRACK_GAMMA)
    return mul, mask


def _crack_image(stage):
    """The multipliers of one stage as a 16x16 Non-Color float image (1.0 where no crack texel is drawn)."""
    name = "brk/crack_%d" % stage
    img = bpy.data.images.get(name)
    if img is not None:
        return img
    mul, _mask = crack_factors(stage)
    arr = np.ones((16, 16, 4), dtype=np.float32)
    arr[..., :3] = mul
    img = bpy.data.images.new(name, 16, 16, alpha=True, float_buffer=True)
    img.colorspace_settings.name = "Non-Color"
    img.alpha_mode = "STRAIGHT"
    img.pixels.foreach_set(np.flipud(arr).ravel())
    img.pack()
    return img


def _crack_material(base, stage):
    """`base` (any block material) with its texture colour multiplied by the crack of `stage`, looked up through
    the mesh's CRACK_UV layer. Where the base texture is cut out (alpha), a crack texel becomes a tinted
    transparent surface: it multiplies what is seen through the hole, as the game's blend does. Cached by name."""
    name = "%s|crack%d" % (base.name, stage)
    mat = bpy.data.materials.get(name)
    if mat is not None:
        return mat
    mat = base.copy()
    mat.name = name
    nt = mat.node_tree
    N, L = nt.nodes.new, nt.links.new
    own = [n for n in nt.nodes if n.type == "TEX_IMAGE"]
    uv = N("ShaderNodeUVMap")
    uv.uv_map = CRACK_UV
    tex = N("ShaderNodeTexImage")
    tex.name = "brk_crack"
    tex.image = _crack_image(stage)
    tex.interpolation = "Closest"
    tex.extension = "REPEAT"                                  # the game's crumbling texture repeats too
    L(uv.outputs[0], tex.inputs[0])
    pairs = [(ln.from_socket, ln.to_socket) for ln in nt.links
             if ln.from_node in own and ln.from_socket.name == "Color"]
    for src, to in pairs:
        mul = N("ShaderNodeMix")
        mul.data_type = "RGBA"
        mul.blend_type = "MULTIPLY"
        mul.clamp_result = True                               # the frame buffer clips at white
        mul.inputs[0].default_value = 1.0
        L(src, mul.inputs[6])
        L(tex.outputs["Color"], mul.inputs[7])
        L(mul.outputs[2], to)
    alpha = [ln for ln in nt.links if ln.to_node.type == "BSDF_PRINCIPLED" and ln.to_socket.name == "Alpha"]
    out = next((n for n in nt.nodes if n.type == "OUTPUT_MATERIAL" and n.is_active_output), None)
    if alpha and out is not None and out.inputs["Surface"].is_linked:
        opaque = alpha[0].from_socket                         # 1 where the block texture is drawn
        surface = out.inputs["Surface"].links[0].from_socket

        def math_node(op, a, b=None):
            m = N("ShaderNodeMath")
            m.operation = op
            for i, v in enumerate((a, b)):
                if v is None:
                    continue
                if isinstance(v, float):
                    m.inputs[i].default_value = v
                else:
                    L(v, m.inputs[i])
            return m.outputs[0]

        sep = N("ShaderNodeSeparateColor")
        L(tex.outputs["Color"], sep.inputs[0])
        drawn = math_node("GREATER_THAN", math_node("ABSOLUTE", math_node("SUBTRACT", sep.outputs[0], 1.0)), 0.02)
        hole = math_node("SUBTRACT", 1.0, opaque)
        fac = math_node("MULTIPLY", drawn, hole)
        through = N("ShaderNodeBsdfTransparent")
        L(tex.outputs["Color"], through.inputs["Color"])
        mix = N("ShaderNodeMixShader")
        L(fac, mix.inputs[0])
        L(surface, mix.inputs[1])
        L(through.outputs[0], mix.inputs[2])
        L(mix.outputs[0], out.inputs["Surface"])
    mat["brk_crack"] = int(stage)
    return mat


def decal_uv(direction, p):
    """SheetedDecalTextureGenerator: the crack texture coordinate (u, v with v DOWN) of the block-local point p
    (Minecraft axes, 0..1) on a face whose nearest axis is `direction`: the position rotated Y 180, X -90, then
    Direction.getRotation(); u = -x', v = -y'; texture scale 1 (one texel per block pixel), wrap = repeat."""
    x, y, z = p
    if direction == "up":
        return (x, z)
    if direction == "down":
        return (x, 1.0 - z)
    if direction == "north":
        return (1.0 - x, 1.0 - y)
    if direction == "south":
        return (x, 1.0 - y)
    if direction == "west":
        return (1.0 - z, 1.0 - y)
    return (z, 1.0 - y)


def nearest_direction(n):
    """Direction.getApproximateNearest of a normal given in BLENDER axes (returns the Minecraft direction name)."""
    m = (n[0], n[2], -n[1])
    best, name = -1e9, "up"
    for d in ("down", "up", "north", "south", "west", "east"):
        v = mc.DIR_VEC[d]
        dot = m[0] * v[0] + m[1] * v[1] + m[2] * v[2]
        if dot > best + 1e-6:
            best, name = dot, d
    return name


def _snap(v):
    """Round a block-local coordinate to 1/4096 (float noise must not move a vertex off the texel grid)."""
    return round(float(v) * 4096.0) / 4096.0


def _cracked_mesh(src, name, stage, to_block, select=None):
    """Copy of mesh `src` for one crack stage: a CRACK_UV layer with the decal projection and the crack material on
    the selected polygons. to_block(poly, co) -> (block-local point in BLENDER axes, normal in Blender axes) for a
    vertex of that polygon; select(poly) -> bool (default: every polygon)."""
    me = src.copy()
    me.name = name
    layer = me.uv_layers.get(CRACK_UV) or me.uv_layers.new(name=CRACK_UV, do_init=False)
    first = me.uv_layers[0]
    first.active_render = True                               # the block texture keeps using the first layer
    uv = np.zeros(len(me.loops) * 2, dtype=np.float32)
    chosen = []
    for poly in me.polygons:
        if select is not None and not select(poly):
            continue
        chosen.append(poly.index)
        for li in poly.loop_indices:
            co = me.vertices[me.loops[li].vertex_index].co
            b, n = to_block(poly, co)
            u, v = decal_uv(nearest_direction(n), (_snap(b[0]), _snap(b[2]), _snap(1.0 - b[1])))
            uv[2 * li], uv[2 * li + 1] = u, 1.0 - v
    layer.data.foreach_set("uv", uv)
    by_slot = {}
    for pi in chosen:
        by_slot.setdefault(me.polygons[pi].material_index, []).append(pi)
    for slot, polys in by_slot.items():
        base = me.materials[slot]
        if base is None:
            continue
        cracked = _crack_material(base, stage)
        users = sum(1 for p in me.polygons if p.material_index == slot)
        if users == len(polys):
            me.materials[slot] = cracked
        else:                                                 # only some faces of that texture: a slot of their own
            me.materials.append(cracked)
            new = len(me.materials) - 1
            for pi in polys:
                me.polygons[pi].material_index = new
    me.update()
    return me


class _Target:
    """Something that can be cracked and broken: its uncracked object, one cracked copy per stage (built on first
    use, children of the object), and the history every visibility key is rewritten from."""

    def __init__(self, ob, name):
        self.object, self.name = ob, name
        self.variants = {}             # look -> Object  (look = stage, or (stage, half) for a door)
        self.patches = []              # objects rendered only while the target is gone
        self._looks = {}               # frame -> look | None
        self._there = {}               # frame -> bool
        self._shown = {}               # frame -> bool   (the Stage's per-shot visibility)
        self._there0 = True

    def _make_variant(self, look):
        raise NotImplementedError

    def _child(self, name, mesh):
        """A cracked copy as a child of the object: it sits exactly on it and follows whatever moves it."""
        ob = bpy.data.objects.new(name, mesh)
        for col in (self.object.users_collection or [bpy.context.scene.collection]):
            col.objects.link(ob)
        ob.parent = self.object
        for flag in ("visible_camera", "visible_diffuse", "visible_glossy", "visible_transmission",
                     "visible_volume_scatter", "visible_shadow"):
            setattr(ob, flag, getattr(self.object, flag))
        for key in self.object.keys():
            if key.startswith("mc_"):
                ob[key] = self.object[key]
        ob.hide_render = ob.hide_viewport = True
        return ob

    def _look(self, stage, half=None):
        return int(stage)

    def crack(self, frame, stage, half="upper"):
        """Show crack stage 0..9 from `frame` on (-1 = none)."""
        stage = int(max(-1, min(9, stage)))
        look = None if stage < 0 else self._look(stage, half)
        if look is not None and look not in self.variants:
            self.variants[look] = self._make_variant(look)
        self._looks[int(round(frame))] = look
        self._rekey()

    def stage_at(self, frame):
        """The keyed crack stage at `frame` (-1 = none)."""
        look = _at(self._looks, frame, None)
        return -1 if look is None else (look[0] if isinstance(look, tuple) else look)

    def there_at(self, frame):
        """False from the frame it was removed / broken on (until it is restored)."""
        return bool(_at(self._there, frame, self._there0))

    def show(self, frame, visible=True):
        """Per-shot visibility (Stage.finish calls it for everything in st.cast): rendered when shown AND there."""
        self._shown[int(round(frame))] = bool(visible)
        self._rekey()

    def remove(self, frame):
        """Not rendered from `frame` on; the cracks are cleared with it."""
        f = int(round(frame))
        self._there[f] = False
        self._looks[f] = None
        self._rekey()

    def restore(self, frame):
        """There again from `frame` on, uncracked."""
        f = int(round(frame))
        self._there[f] = True
        self._looks[f] = None
        self._rekey()

    def _rekey(self):
        """Rewrite the visibility keys of the object, its cracked copies and its patches from the history."""
        frames = sorted(set(self._looks) | set(self._there) | set(self._shown))
        if not frames:
            return
        times = [frames[0] - 1] + frames
        states = [(None, self._there0, True)]
        states += [(_at(self._looks, f, None), _at(self._there, f, self._there0), _at(self._shown, f, True))
                   for f in frames]
        now = bpy.context.scene.frame_current
        for ob, look in [(self.object, None)] + [(o, k) for k, o in self.variants.items()]:
            vals = [0.0 if (there and shown and cur == look) else 1.0 for cur, there, shown in states]
            for path in ("hide_render", "hide_viewport"):
                _keys(ob, path, times, vals)
            cur, there, shown = (_at(self._looks, now, None), _at(self._there, now, self._there0),
                                 _at(self._shown, now, True))
            ob.hide_render = ob.hide_viewport = not (there and shown and cur == look)
        for ob in self.patches:
            vals = [0.0 if (shown and not there) else 1.0 for _cur, there, shown in states]
            for path in ("hide_render", "hide_viewport"):
                _keys(ob, path, times, vals)

    @property
    def objects(self):
        """Every mesh object of this target (the uncracked one first)."""
        return [self.object] + list(self.variants.values())


# ----------------------------------------------------------------------------------------------------
# doors
# ----------------------------------------------------------------------------------------------------
def _closed_matrix(door):
    """World matrix of a door prop when it is shut (whatever it is doing now)."""
    yaw = float(door.get("closed_yaw", door.rotation_euler[2]))
    return Matrix.Translation(Vector(door.location)) @ Matrix.Rotation(yaw, 4, "Z"), yaw


def door_info(door):
    """Where a door prop (engine.props.make_door, Village.doors[...]) is when shut. dict: cell / upper = the Blender
    cells of its two halves, floor = z of its foot, normal = unit vector out of its FRONT (the side the 3-pixel
    slab is flush with), along = unit vector from the hinge to the free edge, center = middle of the front face at
    floor level, front = that face's coordinate along the normal, width, thickness, hinge (the pivot point), yaw."""
    me = door.data
    co = np.empty(len(me.vertices) * 3, dtype=np.float64)
    me.vertices.foreach_get("co", co)
    co = co.reshape(-1, 3)
    lo, hi = co.min(axis=0), co.max(axis=0)
    M, yaw = _closed_matrix(door)
    R = M.to_3x3()
    free = lo[1] if abs(lo[1]) > abs(hi[1]) else hi[1]
    normal = (R @ Vector((-1.0, 0.0, 0.0))).normalized()
    along = (R @ Vector((0.0, 1.0 if free > 0 else -1.0, 0.0))).normalized()
    center = M @ Vector((lo[0], (lo[1] + hi[1]) / 2.0, lo[2]))
    mid = M @ Vector(((lo[0] + hi[0]) / 2.0, (lo[1] + hi[1]) / 2.0, lo[2] + 0.5))
    cell = (int(math.floor(mid.x)), int(math.floor(mid.y)), int(math.floor(mid.z + 1e-6)))
    return {"cell": cell, "upper": (cell[0], cell[1], cell[2] + 1), "floor": float(center.z), "normal": normal,
            "along": along, "center": center, "front": float(center.dot(normal)), "width": float(hi[1] - lo[1]),
            "thickness": float(hi[0] - lo[0]), "hinge": M @ Vector((0.0, 0.0, 0.0)), "yaw": yaw,
            "height": float(hi[2] - lo[2]), "local": (tuple(lo), tuple(hi))}


def stand_point(door, side="front", gap=None, along=0.0):
    """((x, y, z), yaw) of a mob that stands pressed against the shut door, facing it. gap = distance of its
    centre from the door's face (default 0.3 = half a zombie's 0.6 hit box, where DoorInteractGoal finds it);
    side "front" = the side the slab is flush with, "back" = the other; along = shift toward the free edge."""
    info = door_info(door)
    gap = ZOMBIE_WIDTH / 2.0 if gap is None else float(gap)
    n = info["normal"]
    p = info["center"] + info["along"] * float(along)
    if side == "back":
        p = p - n * info["thickness"]
        n = -n
    elif side != "front":
        raise ValueError("breaking.stand_point: side is 'front' or 'back'")
    p = p + n * gap
    return (float(p.x), float(p.y), info["floor"]), math.atan2(-n.x, n.y)


class DoorCracks(_Target):
    """The crack state of one door prop (made by the first crack() / remove() on it)."""

    def __init__(self, door):
        super().__init__(door, door.name)
        self.info = door_info(door)
        self.block_id = str(door.get("mc_block", "oak_door"))

    def _look(self, stage, half=None):
        half = "upper" if half is None else half
        if half not in ("upper", "lower", "both"):
            raise ValueError("breaking.crack: half is 'upper' (the game), 'lower' or 'both'")
        return (int(stage), half)

    def _make_variant(self, look):
        stage, half = look
        door, info = self.object, self.info
        M, _yaw = _closed_matrix(door)
        R = M.to_3x3()
        cell = info["cell"]
        z_split = info["local"][0][2] + 1.0                     # local z where the upper block starts

        def is_upper(poly):
            return max(door.data.vertices[i].co.z for i in poly.vertices) > z_split + 1e-4

        def select(poly):
            return half == "both" or (half == "upper") == is_upper(poly)

        def to_block(poly, co):
            w = M @ co
            dz = 1.0 if is_upper(poly) else 0.0
            return (w.x - cell[0], w.y - cell[1], w.z - cell[2] - dz), R @ poly.normal

        name = "brk_%s_s%d%s" % (door.name, stage, half[0])
        return self._child(name, _cracked_mesh(door.data, name, stage, to_block, select))

    def half_box(self, half):
        """Blender block-local box (x0, y0, z0, x1, y1, z1) of one half's slab inside its cell."""
        M, _yaw = _closed_matrix(self.object)
        lo, hi = self.info["local"]
        pts = [M @ Vector((x, y, 0.0)) for x in (lo[0], hi[0]) for y in (lo[1], hi[1])]
        cell = self.info["cell"]
        xs = [_snap(p.x - cell[0]) for p in pts]
        ys = [_snap(p.y - cell[1]) for p in pts]
        return (min(xs), min(ys), 0.0, max(xs), max(ys), 1.0)


_DOORS = {}


def _door(door):
    """The DoorCracks of a door prop (one per door object; forgotten when its scene is reset)."""
    for key in [k for k, t in _DOORS.items() if not _alive(t.object)]:
        del _DOORS[key]
    t = _DOORS.get(door.as_pointer())
    if t is None or t.object != door:
        t = _DOORS[door.as_pointer()] = DoorCracks(door)
    return t


def _target(target):
    if isinstance(target, _Target):
        return target
    if isinstance(target, bpy.types.Object) and target.type == "MESH":
        return _door(target)
    raise TypeError("breaking: target is a door prop (Village.doors[...]) or a Breakable from place_block, not %r"
                    % (target,))


def crack(target, frame, stage, half="upper"):
    """destroy_stage_<stage> (0..9) over a door prop or a Breakable from `frame` on; -1 removes the cracks.
    half (doors only): "upper" = the block the game's zombie attacks, "lower", or "both"."""
    _target(target).crack(frame, stage, half)


def crack_progress(target, frame_start, frame_end, first=0, last=9, clear=True, half="upper"):
    """The stages first..last spread evenly over [frame_start, frame_end), each from the integer frame it starts
    on; clear=True removes the cracks ON frame_end (False: the last stage stays). Returns [(frame, stage), ...]."""
    f0, f1 = int(round(frame_start)), int(round(frame_end))
    if f1 <= f0:
        raise ValueError("breaking.crack_progress: frame_end must be after frame_start")
    t = _target(target)
    n = int(last) - int(first) + 1
    out, cur = [], None
    for f in range(f0, f1):
        stage = int(first) + min(n - 1, int(n * (f - f0) / float(f1 - f0)))
        if stage != cur:
            t.crack(f, stage, half)
            out.append((f, stage))
            cur = stage
    if clear:
        t.crack(f1, -1, half)
        out.append((f1, -1))
    return out


def stage_at(target, frame):
    """The crack stage keyed on a door or Breakable at `frame` (-1 = none)."""
    return _target(target).stage_at(frame)


def remove(target, frame):
    """The door or block is not rendered from `frame` on (no particles: see break_block / break_door)."""
    _target(target).remove(frame)


def restore(target, frame):
    """The door or block is there again from `frame` on, uncracked."""
    _target(target).restore(frame)


# ----------------------------------------------------------------------------------------------------
# a block of its own
# ----------------------------------------------------------------------------------------------------
_BLOCKS_PLACED = []


def _live_blocks():
    _BLOCKS_PLACED[:] = [b for b in _BLOCKS_PLACED if _alive(b.object)]
    return _BLOCKS_PLACED


class _SolidView:
    """What engine.fx's particle collision asks a World, with the breakable blocks as they are at one frame: a
    cell whose Breakable is gone is air, one whose Breakable is there is that block."""

    def __init__(self, world, frame):
        self.world, self.frame = world, frame
        self.own = {b.cell: b for b in _live_blocks() if b.world is world or world is None or b.world is None}
        self.blocks = self

    def __contains__(self, cell):
        b = self.own.get(cell)
        if b is not None:
            return b.there_at(self.frame)
        return self.world is not None and cell in self.world.blocks

    def get(self, x, y, z):
        """(block id, props) at a cell, or None (World.get)."""
        b = self.own.get((x, y, z))
        if b is not None:
            return (b.block_id, b.props) if b.there_at(self.frame) else None
        return self.world.get(x, y, z) if self.world is not None else None

    def is_full_cube(self, x, y, z):
        """True when the cell holds a full cube right now (World.is_full_cube)."""
        b = self.own.get((x, y, z))
        if b is not None:
            return b.there_at(self.frame) and b.full_cube
        return self.world is not None and self.world.is_full_cube(x, y, z)

    def solid(self, cell):
        """True when a dropped item cannot enter the cell."""
        return cell in self and self.is_full_cube(*cell)

    def top_of(self, cell):
        """Height (0..1) of the surface an item lands on in that cell, or None when it falls through it."""
        if cell not in self:
            return None
        if self.is_full_cube(*cell):
            return 1.0
        bid, props = self.get(*cell)
        if bid in ("dirt_path", "farmland"):
            return 15.0 / 16.0
        if bid.endswith("_slab"):
            return 0.5 if props.get("type", "bottom") == "bottom" else 1.0
        return None


class _FxBlock:
    """The handful of attributes engine.fx's terrain particles read from a block (fx.Block), for one burst."""

    def __init__(self, name, cell, shape, particle_texture, world, frame):
        self.name, self.cell, self.shape, self.particle_texture = name, tuple(cell), list(shape), particle_texture
        self.center = Vector((cell[0] + 0.5, cell[1] + 0.5, cell[2] + 0.5))
        self.village = types.SimpleNamespace(world=_SolidView(world, frame))

    def show(self, frame, visible=True):
        """(fx.break_block keys the block it is given; the Breakable keys itself.)"""

    def crack(self, frame, stage):
        """(see show)"""


def _material_for(block_id):
    """Quad -> the material engine.blocks gives that face (tint, grass side overlay, shade-up plants)."""
    def f(q):
        tint = mc.block_tint(block_id, q.tintindex)
        ov = ov_tint = None
        if q.overlay is not None:
            ov, ov_tint = q.overlay[0], mc.block_tint(block_id, q.overlay[1])
        return _blocks.block_material(q.texture, tint, ov, ov_tint, getattr(q, "shade", None))
    return f


class Breakable(_Target):
    """One block as its own object (place_block): crack it, break it, put it back. See the module docstring."""

    def __init__(self, ob, block_id, props, cell, world):
        super().__init__(ob, ob.name)
        self.block_id, self.props, self.cell, self.world = block_id, dict(props), tuple(cell), world
        self.center = Vector((cell[0] + 0.5, cell[1] + 0.5, cell[2] + 0.5))
        self.top = cell[2] + max(v.co.z for v in ob.data.vertices)
        # the game's outline boxes, Blender block-local: what the break particles fill
        self.shape = [(b[0] / 16.0, 1.0 - b[5] / 16.0, b[1] / 16.0, b[3] / 16.0, 1.0 - b[2] / 16.0, b[4] / 16.0)
                      for b in fx.block_shape(block_id, props)]
        tex = None
        try:
            tex = mc.load_model(mc.resolve_blockstate(block_id, props)[0].model).textures.get("particle")
        except Exception:                                    # noqa: BLE001 - odd models: a face texture instead
            tex = None
        if not tex or tex.startswith("#"):
            tex = ob.data.materials[0].get("mc_texture", "block/" + block_id)
        # TerrainParticle: BlockTintSource.colorAsTerrainParticle, which is WHITE for the grass block's tint
        # source (its crumbs are plain dirt) and the world tint for everything else (leaves, grass plants)
        tint = None if block_id == "grass_block" else mc.block_tint(block_id, 0)
        self.particle_texture = (tex.replace("minecraft:", ""), tint)
        probe = _blocks.World()
        probe.set(0, 0, 0, block_id, props)
        self.full_cube = bool(probe.is_full_cube(0, 0, 0))

    def __repr__(self):
        return "<breaking.Breakable %s at %s>" % (self.block_id, (self.cell,))

    def _make_variant(self, look):
        def to_block(poly, co):
            return (co.x, co.y, co.z), poly.normal

        name = "%s_s%d" % (self.name, look)
        return self._child(name, _cracked_mesh(self.object.data, name, look, to_block))


def place_block(collection, block_id, cell, props=None, world=None, name=None, frame=None):
    """One block of its own at Blender cell `cell`, built from the game's model for that state exactly as
    engine.blocks would draw it there (same random variant, texture, tint); all of its faces are drawn.
    world = the set's blocks.World (or the Village): where its particles and drops land. frame = the frame it is
    placed ON (None: there from the start). Returns a Breakable."""
    block_id = block_id.replace("minecraft:", "")
    props = {k: (str(v).lower() if isinstance(v, bool) else str(v)) for k, v in (props or {}).items()}
    cell = tuple(int(math.floor(float(c) + 1e-6)) for c in cell)
    if not mc.has_blockstate(block_id) or block_id in ("water", "lava"):
        raise ValueError("breaking.place_block: %r has no block model (fluids, chests and the like are not built)"
                         % block_id)
    world = getattr(world, "world", world)
    nv = mc.variant_count(block_id, props)
    variant = _blocks.pos_hash(*cell) % nv if nv > 1 else 0   # as blocks.World._state_at picks it
    quads = mc.bake_block(block_id, props, variant)
    if not quads:
        raise ValueError("breaking.place_block: %r has no faces" % block_id)
    base = name or "block_%s_%d_%d_%d" % (block_id, cell[0], cell[1], cell[2])
    name, k = base, 1
    while bpy.data.objects.get(name) is not None:
        k += 1
        name = "%s_%d" % (base, k)
    ob = mc.quads_object(name, quads, _material_for(block_id), collection, origin=(0.0, 0.0, 16.0))
    ob.location = (float(cell[0]), float(cell[1]), float(cell[2]))
    ob["mc_block"] = block_id
    block = Breakable(ob, block_id, props, cell, world)
    if frame is not None:
        block._there0 = False
        block._there[int(round(frame))] = True
        block._rekey()
    _live_blocks().append(block)
    return block


def place_from_world(collection, world, cells, **kw):
    """Breakable blocks for the cells a set left out of its mesh (world.build(coll, name, skip=cells)): each with
    the state the World holds at that cell. Returns them in the order of `cells`."""
    w = getattr(world, "world", world)
    out = []
    for c in cells:
        st = w.get(*c)
        if st is None:
            raise ValueError("breaking.place_from_world: no block at %s" % (c,))
        out.append(place_block(collection, st[0], c, st[1], world=w, **kw))
    return out


# ----------------------------------------------------------------------------------------------------
# particles and drops
# ----------------------------------------------------------------------------------------------------
def _burst(name, cell, shape, particle_texture, world, frame, camera, seed, glow, f0=None, hit_from=None):
    """The game's break particles of `shape` ON `frame` (plus the mining crumbs since f0 when hit_from is given),
    through engine.fx.break_block on a stand-in block. Returns the fx.Burst."""
    stand_in = _FxBlock(name, cell, shape, particle_texture, world, frame)
    start = int(frame) - 1 if f0 is None else min(int(f0), int(frame) - 1)
    return fx.break_block(stand_in, start, int(frame), camera=camera, hit_from=hit_from, seed=seed,
                          particles=True, glow=glow)


def drop_track(velocity, height, blocked=None, start=(0.0, 0.0), max_ticks=200):
    """ItemEntity.tick() for an item spawned `height` above the floor it lands on: [(tick, (east, north, up))],
    up measured from that floor, until it lies still. Per tick: gravity 0.04, move, speed x 0.98 (x 0.6 more for
    the horizontal part on the ground). blocked(x, y) -> True where a wall stands (the item stops against it)."""
    vx, vy, vz = (float(c) for c in velocity)
    x, y, z = float(start[0]), float(start[1]), float(height)
    out = [(0, (x, y, z))]
    for tick in range(1, max_ticks + 1):
        vz -= ITEM_GRAVITY
        nx, ny = x + vx, y + vy
        if blocked is not None:
            if blocked(nx, y):
                nx, vx = x, 0.0
            if blocked(nx, ny):
                ny, vy = y, 0.0
        x, y, z = nx, ny, z + vz
        on_ground = z <= 0.0
        if on_ground:
            z, vz = 0.0, 0.0
        f = ITEM_DRAG * (0.6 if on_ground else 1.0)
        vx, vy, vz = vx * f, vy * f, vz * ITEM_DRAG
        out.append((tick, (x, y, z)))
        if on_ground and vx * vx + vy * vy < 1e-5:
            break
    return out


def _drop_item(item_id, cell, frame, world, seed=0, collection=None, until=None, floor=None):
    """Block.popResource: an engine.mobs dropped item spawned ON `frame` in the middle of `cell` (+- 0.25, minus
    half its height) with ItemEntity's toss; it falls to `floor` (default the cell's) and bobs until `until`."""
    from . import mobs

    frame = int(round(frame))
    r = np.random.default_rng([int(seed) & 0x7FFFFFFF, 7607, cell[0] & 0xFFFF, cell[1] & 0xFFFF, cell[2] & 0xFFFF])
    spawn = [cell[i] + 0.5 + r.uniform(-DROP_SPREAD, DROP_SPREAD) for i in range(3)]
    spawn[2] -= DROP_ITEM_HEIGHT / 2.0
    vel = (r.uniform(-DROP_TOSS[0], DROP_TOSS[0]), r.uniform(-DROP_TOSS[0], DROP_TOSS[0]), DROP_TOSS[1])
    view = _SolidView(world, frame)
    if floor is None:
        floor = float(cell[2])
        if world is not None:                                 # what the item lands on: the first top under it
            for z in range(cell[2] - 1, cell[2] - 17, -1):
                top = view.top_of((cell[0], cell[1], z))
                if top is not None:
                    floor = z + top
                    break
    floor = float(floor)
    half = DROP_ITEM_HEIGHT / 2.0

    def blocked(x, y):
        for sx in (-half, half):
            for sy in (-half, half):
                c = (int(math.floor(x + sx)), int(math.floor(y + sy)), int(math.floor(floor + 1e-6)))
                if view.solid(c):
                    return True
        return False

    track = drop_track(vel, spawn[2] - floor, blocked, start=(spawn[0], spawn[1]))
    item = mobs.make_dropped_item(item_id, collection=collection, seed=seed)
    item.drop(frame, (spawn[0], spawn[1], floor), velocity=vel)       # visibility, age and bookkeeping
    frames = [frame - 1.0] + [frame + t * TICK for t, _p in track]
    for i in range(3):
        vals = [(p[i] if i < 2 else p[2] + floor) for _t, p in track]
        _keys(item.root, "location", frames, [vals[0]] + vals, "LINEAR", index=i)
    end = track[-1][1]
    item.rest_pos = Vector((end[0], end[1], end[2] + floor))
    landed = next((t for t, p in track if p[2] <= 0.0), track[-1][0])
    until = frame + 120 if until is None else int(until)
    if until > frame:
        item.animate(frame, until)
    item.spawn_point = tuple(spawn)
    item.land_frame = int(math.ceil(frame + landed * TICK))
    return item


def _tool(tool):
    """(material, class) of a tool id: 'golden_pickaxe' -> ('golden', 'pickaxe'); the hand -> (None, None)."""
    if tool in (None, "", "hand", "fist"):
        return None, None
    t = str(tool).replace("minecraft:", "")
    for cls in ("pickaxe", "axe", "shovel", "hoe"):
        if t.endswith("_" + cls):
            mat = t[:-len(cls) - 1]
            mat = {"wood": "wooden", "gold": "golden"}.get(mat, mat)
            if mat in TOOL_SPEED:
                return mat, cls
    return None, None                                         # swords, shears and everything else mine like a hand


def _block_entry(block_id, hardness=None):
    block_id = block_id.replace("minecraft:", "")
    if block_id in BLOCKS:
        h, cls, needs, tier = BLOCKS[block_id]
        return (h if hardness is None else float(hardness)), cls, needs, tier
    if hardness is None:
        raise KeyError("breaking: no hardness on record for %r: pass hardness= (Blocks.<ID>: strength(...)) or add "
                       "it to breaking.BLOCKS" % block_id)
    return float(hardness), None, False, 0


def correct_tool(block_id, tool="hand", hardness=None):
    """Player.hasCorrectToolForDrops: True when the block needs no tool, or `tool` is of its class and tier."""
    _h, cls, needs, tier = _block_entry(block_id, 1.0 if hardness is None and block_id not in BLOCKS else hardness)
    if not needs:
        return True
    mat, tcls = _tool(tool)
    return tcls is not None and tcls == cls and TOOL_TIER[mat] >= tier


def destroy_progress(block_id, tool="hand", hardness=None, efficiency=0, haste=0, on_ground=True, in_water=False):
    """BlockBehaviour.getDestroyProgress: the fraction of the block one tick of mining removes (float32, as the
    client computes it); 0 for an unbreakable block, >= 1 breaks on the click."""
    h, cls, _needs, _tier = _block_entry(block_id, hardness)
    if h < 0.0:
        return np.float32(0.0)
    mat, tcls = _tool(tool)
    speed = np.float32(TOOL_SPEED[mat] if (tcls is not None and tcls == cls) else 1.0)   # ItemStack.getDestroySpeed
    if speed > 1.0 and efficiency:
        speed = np.float32(speed + efficiency * efficiency + 1)           # Attributes.MINING_EFFICIENCY
    if haste:
        speed = np.float32(speed * np.float32(1.0 + haste * 0.2))         # MobEffectUtil.getDigSpeedAmplification
    if in_water:
        speed = np.float32(speed * np.float32(0.2))                       # Attributes.SUBMERGED_MINING_SPEED
    if not on_ground:
        speed = np.float32(speed / np.float32(5.0))
    if h == 0.0:
        return np.float32(np.inf)
    div = CORRECT_TOOL_DIVISOR if correct_tool(block_id, tool, hardness) else WRONG_TOOL_DIVISOR
    return np.float32(np.float32(speed / np.float32(h)) / np.float32(div))


def progress_track(block_id, tool="hand", exact=True, **kw):
    """MultiPlayerGameMode.continueDestroyBlock tick by tick: [destroyProgress after tick 1, 2, ...] up to the
    tick it reaches 1 (empty = the block breaks on the click). exact=True adds in single precision, as the client
    does (`destroyProgress += ...` on a float field): for stone by hand the 150th sum is 0.9999993 and the block
    breaks on tick 151. exact=False is the textbook formula in exact arithmetic (150)."""
    d = destroy_progress(block_id, tool, **kw)
    if d <= 0.0:
        raise ValueError("breaking: %r cannot be broken (hardness -1)" % block_id)
    out = []
    if d >= 1.0:
        return out
    if not exact:
        h, cls, _needs, _tier = _block_entry(block_id, kw.get("hardness"))
        per = float(d)
        n = int(math.ceil(round(1.0 / per, 3) - 1e-9))
        return [min(1.0, (k + 1) / (1.0 / per)) if k < n - 1 else 1.0 for k in range(n)]
    p = np.float32(0.0)
    while p < 1.0 and len(out) < 200000:
        p = np.float32(p + d)
        out.append(float(p))
    return out


def break_ticks(block_id, tool="hand", exact=True, **kw):
    """Game ticks from the click to the break (0 = the block breaks on the click). exact=True: as the client's
    single-precision sum gives it (stone by hand 151); exact=False: the formula hardness x 1.5 (x 5 without the
    right tool) / tool speed seconds, rounded up to a tick (150). kw: hardness, efficiency, haste, on_ground,
    in_water."""
    return len(progress_track(block_id, tool, exact=exact, **kw))


def break_seconds(block_id, tool="hand", exact=True, **kw):
    """Seconds the game needs to mine the block (see break_ticks)."""
    return break_ticks(block_id, tool, exact=exact, **kw) / 20.0


def break_frames(block_id, tool="hand", exact=True, **kw):
    """Film frames the game needs to mine the block (ticks x 1.2, rounded)."""
    return int(round(break_ticks(block_id, tool, exact=exact, **kw) * TICK))


def drops(block_id, tool="hand"):
    """The item a block leaves when broken with `tool` and no enchantment (None = nothing): its loot table's plain
    entry, and nothing at all when it needs a tool that `tool` is not."""
    block_id = block_id.replace("minecraft:", "")
    if block_id in BLOCKS and not correct_tool(block_id, tool):
        return None
    return _DROPS.get(block_id, block_id)


TIMES = {            # (block, tool) -> (ticks by the formula, ticks as the client's float sum gives them)
    ("stone", "hand"): (150, 151), ("stone", "wooden_pickaxe"): (23, 23), ("stone", "iron_pickaxe"): (8, 8),
    ("stone", "golden_pickaxe"): (4, 4), ("cobblestone", "hand"): (200, 201), ("dirt", "hand"): (15, 15),
    ("dirt", "iron_shovel"): (3, 3), ("grass_block", "hand"): (18, 18), ("netherrack", "hand"): (40, 41),
    ("netherrack", "wooden_pickaxe"): (6, 6), ("netherrack", "golden_pickaxe"): (0, 0),
    ("oak_planks", "hand"): (60, 61), ("oak_door", "hand"): (90, 90), ("oak_log", "iron_axe"): (10, 10),
    ("obsidian", "diamond_pickaxe"): (188, 188), ("obsidian", "hand"): (5000, 5001),
    ("blackstone", "golden_pickaxe"): (4, 4), ("polished_blackstone_bricks", "hand"): (150, 151),
    ("gilded_blackstone", "golden_pickaxe"): (4, 4), ("anvil", "hand"): (500, 501), ("sand", "hand"): (15, 15),
    ("tnt", "hand"): (0, 0),
}


def break_block(block, frame, camera=None, drop=None, tool="hand", seed=0, glow=0.0, particles=True, until=None,
                _f0=None, _hit_from=None):
    """Break a Breakable ON `frame`: it is gone, the game's particles fly, and with drop= an item pops out.
    drop: None | "auto" (drops(block.block_id, tool)) | an item id. Returns dict(frame, burst, item, drop)."""
    if not isinstance(block, Breakable):
        raise TypeError("breaking.break_block takes a Breakable (place_block); for a door use break_door")
    f = int(round(frame))
    block.remove(f)
    burst = None
    if particles:
        burst = _burst(block.name, block.cell, block.shape, block.particle_texture, block.world, f, camera, seed,
                       glow, f0=_f0, hit_from=_hit_from)
    item_id = drops(block.block_id, tool) if drop == "auto" else drop
    item = None
    if item_id:
        cols = block.object.users_collection
        item = _drop_item(item_id, block.cell, f, block.world, seed=seed, collection=cols[0] if cols else None,
                          until=until)
    return {"frame": f, "burst": burst, "item": item, "drop": item_id}


# ----------------------------------------------------------------------------------------------------
# mining
# ----------------------------------------------------------------------------------------------------
def _held(player, frame):
    fn = getattr(player, "holding_at", None)
    if fn is None:
        return "hand"
    try:
        return fn("right", frame) or "hand"
    except Exception:                                        # noqa: BLE001 - another rig: the bare hand
        return "hand"


def mine(player, block, frame_start, tool="auto", duration=None, camera=None, drop="auto", seed=0, glow=0.0,
         crumbs=True, swing=True, until=None, **speed_kw):
    """A player mines a Breakable from `frame_start` (see the module docstring). Returns dict: start, frame (the
    break), ticks (the game's), frames (as filmed), stages [(frame, stage)], swings [frames], burst, item, drop,
    instant, tool. speed_kw: hardness, efficiency, haste, on_ground, in_water."""
    if not isinstance(block, Breakable):
        raise TypeError("breaking.mine takes a Breakable (place_block)")
    f0 = int(round(frame_start))
    if tool == "auto":
        tool = _held(player, f0)
    track = progress_track(block.block_id, tool, **speed_kw)
    ticks = len(track)
    stages = []
    if ticks == 0:                                            # broken on the click
        fb, n = f0, 0
    else:
        n = int(round(ticks * TICK)) if duration is None else int(round(duration))
        if n < 1:
            raise ValueError("breaking.mine: duration must be at least one frame")
        fb = f0 + n
        cur = -1
        block.crack(f0, -1)                                   # the tick of the click shows nothing yet
        for f in range(f0 + 1, fb):
            if duration is None:
                k = int(math.floor((f - f0) / TICK + 1e-6))   # the last tick that has happened by this frame
                stage = -1 if k < 1 else min(9, int(track[min(k, ticks) - 1] * 10.0))
            else:
                stage = min(9, int(10.0 * (f - f0) / float(n)))
            if stage != cur:
                block.crack(f, stage)
                stages.append((f, stage))
                cur = stage
    swings = []
    if swing and player is not None:
        swings = fx.arm_swings(player, [float(f0)]) if n == 0 else fx.mining_swings(player, f0, fb)
    res = break_block(block, fb, camera=camera, drop=drop, tool=tool, seed=seed, glow=glow, until=until,
                      _f0=f0 if (crumbs and n > 0 and player is not None) else None,
                      _hit_from=player if (crumbs and n > 0) else None)
    res.update({"start": f0, "ticks": ticks, "frames": n, "stages": stages, "swings": swings, "instant": n == 0,
                "tool": tool})
    return res


def dig(player, blocks, frame_start, tool="auto", duration=None, **mine_kw):
    """Mine several Breakables one after the other with the button held (a hole: top block first). The next block
    is started DESTROY_COOLDOWN_TICKS + 1 ticks after a break (1 tick after an instant one); the arm swings without
    a pause from the first click to the last break. duration = frames per block (None: the game's). Returns the
    list of mine() dicts."""
    f = float(frame_start)
    out = []
    mine_kw = dict(mine_kw)
    mine_kw.pop("swing", None)
    for b in blocks:
        r = mine(player, b, int(round(f)), tool=tool, duration=duration, swing=False, **mine_kw)
        out.append(r)
        f = r["frame"] + (1 if r["instant"] else DESTROY_COOLDOWN_TICKS + 1) * TICK
    if out and player is not None:
        sw = fx.mining_swings(player, out[0]["start"], max(out[-1]["frame"], out[0]["start"] + 1))
        for r in out:
            r["swings"] = sw
    return out


# ----------------------------------------------------------------------------------------------------
# the door: shudder, break, torches
# ----------------------------------------------------------------------------------------------------
def shudder(door, frame, amount=1.0):
    """A film gesture, not the game: the door jolts on a blow. Its free edge swings SHUDDER_PIXELS x amount (in
    texture pixels) inward about the hinge ON `frame`, rebounds 45 %, and is at rest again 3 frames later. Keys go
    on top of whatever the door's rotation is doing (LINEAR, on whole frames). Returns the frame it is at rest."""
    info = door_info(door)
    f = int(round(frame))
    theta = float(amount) * SHUDDER_PIXELS / 16.0 / max(info["width"], 1e-6)
    theta *= 1.0 if float(door.get("open_angle", 1.0)) >= 0.0 else -1.0
    fc = _fcurve(door, "rotation_euler", 2)
    kps = fc.keyframe_points
    if not len(kps):
        kp = kps.insert(float(f - 1), float(door.rotation_euler[2]))
        kp.interpolation = "LINEAR"
    after = "LINEAR"
    for kp in kps:
        if kp.co.x <= f - 1 + 1e-6:
            after = kp.interpolation
    times = [f - 1] + [f + i for i in range(len(SHUDDER_SHAPE))]
    base = [float(fc.evaluate(t)) for t in times]
    for i, t in enumerate(times):
        off = 0.0 if i == 0 else SHUDDER_SHAPE[i - 1] * theta
        kp = kps.insert(float(t), base[i] + off)
        kp.interpolation = "LINEAR" if i < len(times) - 1 else after
    fc.update()
    return times[-1]


def break_door(door, frame, camera=None, halves=("lower",), seed=0, glow=0.0, drop=False, until=None,
               world=None):
    """The door is gone ON `frame`. halves = which halves throw break particles: ("lower",) is the game when a
    zombie breaks it (32 crumbs of oak_door_bottom; the upper block is removed without any), ("lower", "upper")
    is what a player's axe would give. drop=True: the oak_door item. world = the Village / World the crumbs land
    on. Returns dict(frame, burst, item)."""
    t = _door(door)
    f = int(round(frame))
    t.remove(f)
    world = getattr(world, "world", world)
    burst = None
    for half in halves:
        cell = t.info["cell"] if half == "lower" else t.info["upper"]
        tex = "block/%s_%s" % (t.block_id, "bottom" if half == "lower" else "top")
        b = _burst("%s_%s" % (door.name, half), cell, [t.half_box(half)], (tex, None), world, f, camera,
                   seed + (0 if half == "lower" else 1), glow)
        burst = b if burst is None else burst.extend(b)
    item = None
    if drop:
        cols = door.users_collection
        item = _drop_item(t.block_id, t.info["cell"], f, world, seed=seed, collection=cols[0] if cols else None,
                          until=until, floor=t.info["floor"])
    return {"frame": f, "burst": burst, "item": item}


def door_torches(village, name="house_a"):
    """Give the wall torches beside a village door one point light each, in place of the single light the village
    merges them into (half way between them: inside the head of whoever stands on the doorstep). Same total energy
    and light group; the new lights are in village.lantern_lights / village.lights, so Stage.lights scales them.
    Returns the new lights (an empty list when there is nothing to split)."""
    from . import props

    door = village.doors[name]
    done = door.get("brk_torches")
    if done:
        return [bpy.data.objects[n] for n in done if n in bpy.data.objects]
    info = door_info(door)
    w = village.world
    n, a, c = info["normal"], info["along"], info["center"]
    flames = []
    for dz in range(0, 4):
        for da in (-2, -1, 1, 2):
            for dn in (0, 1):
                p = c + a * da + n * (dn + 0.5)
                cell = (int(math.floor(p.x)), int(math.floor(p.y)), info["cell"][2] + dz)
                st = w.get(*cell)
                if st is not None and st[0] == "wall_torch":
                    flames.append(Vector(props.flame_position(cell, "wall_torch", st[1])))
    uniq = []
    for p in flames:
        if all((p - q).length > 0.05 for q in uniq):
            uniq.append(p)
    if len(uniq) < 2:
        return []
    mean = sum(uniq, Vector()) / len(uniq)
    merged = [L for L in village.lantern_lights
              if L.get("mc_light") == "torch" and (Vector(L.location) - mean).length < 0.6]
    if not merged:
        return []
    old = merged[0]
    group = old.get("group", "")
    new = []
    for i, p in enumerate(uniq):
        ob = props.make_light("torch", village.collection)
        ob.location = p
        ob.data.energy = float(old["base_energy"]) / len(uniq)
        ob["base_energy"] = ob.data.energy
        ob["group"] = group
        ob.name = "light_%s_door_%d" % (name, i)
        new.append(ob)
    idx = village.lantern_lights.index(old)
    village.lantern_lights[idx:idx + 1] = new
    if group in village.lights and old in village.lights[group]:
        j = village.lights[group].index(old)
        village.lights[group][j:j + 1] = new
    old.hide_render = old.hide_viewport = True
    old.data.energy = 0.0
    door["brk_torches"] = [ob.name for ob in new]
    return new


# ----------------------------------------------------------------------------------------------------
# the zombie at the door
# ----------------------------------------------------------------------------------------------------
def knock_frames(frame_start, frame_end, every=None, first=2, seed=None):
    """Frames on which a door-breaking mob starts an arm swing in [frame_start, frame_end): every `every` frames
    from frame_start + first (default DOOR_SWING_MEAN_FRAMES, the game's average), or with seed= the game's own
    draw (each tick 1 chance in DOOR_KNOCK_ODDS, and no new swing while one of 6 ticks is running)."""
    f0, f1 = float(frame_start), float(frame_end)
    out = []
    every = DOOR_SWING_MEAN_FRAMES if every is None else every
    if seed is None:
        f = f0 + float(first)
        while f < f1 - 1e-6:
            out.append(int(round(f)))
            f += max(float(every), 1.0)
        return sorted(set(out))
    r = np.random.default_rng([int(seed) & 0x7FFFFFFF, 1019])
    ticks = int(math.floor((f1 - f0) / TICK + 1e-6))
    busy = -10 ** 9
    for t in range(ticks):
        if r.integers(0, DOOR_KNOCK_ODDS) == 0 and t - busy > ZOMBIE_SWING_TICKS:
            out.append(int(round(f0 + t * TICK)))
            busy = t
    return sorted(set(out))


def bang_on_door(zombie, door, frame_start, frame_end, attempt=None, phase=0.0, pause=2, every=None, first=2,
                 seed=None, half="upper", arms="raised", place=True, side="front", gap=None, along=0.0,
                 shudder=0.0, hit_delay=HIT_DELAY, break_door=False, camera=None, crumbs=0, glow=0.0, drop=False,
                 world=None):
    """A zombie bangs on a wooden door from frame_start until frame_end (see the module docstring for every
    argument). Returns dict: stand, yaw, knocks (frames a swing starts), hits (frames of the blows), stages
    [(frame, stage)], resets (frames the cracks were cleared), frame (the door broke on it, or None), burst, item,
    phase (pass it on to continue in the next shot), attempt."""
    f0, f1 = int(round(frame_start)), int(round(frame_end))
    if f1 <= f0:
        raise ValueError("breaking.bang_on_door: frame_end must be after frame_start")
    if not 0.0 <= phase < 1.0:
        raise ValueError("breaking.bang_on_door: phase is 0 <= phase < 1")
    game = DOOR_BREAK_TICKS * TICK
    fb = None
    if break_door:
        if attempt is None:
            attempt = (f1 - f0) / (1.0 - phase)
        fb = f0 + int(math.ceil((1.0 - phase) * attempt - 1e-6))
        if fb > f1:
            raise ValueError("breaking.bang_on_door: with attempt=%g and phase=%g the door breaks on frame %d, "
                             "after frame_end %d" % (attempt, phase, fb, f1))
    attempt = game if attempt is None else float(attempt)
    if attempt < 10.0:
        raise ValueError("breaking.bang_on_door: an attempt has ten stages: give it at least 10 frames")
    pos, yaw = stand_point(door, side=side, gap=gap, along=along)
    if place:
        zombie.place(f0, pos, yaw)
    if arms == "raised":
        zombie.aggro(f0, True, ease=0 if place else 3)
    elif arms != "out":
        raise ValueError("breaking.bang_on_door: arms is 'raised' or 'out'")
    last = f1 if fb is None else fb
    knocks = [k for k in knock_frames(f0, last, every=every, first=first, seed=seed) if k < last]
    for k in knocks:
        zombie.attack(k)
    hits = [int(round(k + hit_delay)) for k in knocks]
    hits = [h for h in hits if h < last]
    # the cracks: (int)(breakTime / doorBreakTime * 10) on the attacked block, cleared when an attempt is over
    t = _door(door)
    cycle = attempt + max(0, int(pause))
    stages, resets, cur = [], [], None
    for f in range(f0, last):
        c = (phase * attempt + (f - f0)) % cycle if fb is None else phase * attempt + (f - f0)
        stage = min(9, int(10.0 * c / attempt)) if c < attempt else -1
        if stage != cur:
            t.crack(f, stage, half)
            stages.append((f, stage))
            if stage == -1 and cur is not None:
                resets.append(f)
            cur = stage
    burst, item = None, None
    if shudder:
        for h in hits:
            globals()["shudder"](door, h, amount=float(shudder))
    if crumbs:
        box = t.half_box("upper" if half != "lower" else "lower")
        cell = t.info["upper"] if half != "lower" else t.info["cell"]
        tex = "block/%s_%s" % (t.block_id, "top" if half != "lower" else "bottom")
        for i, h in enumerate(hits):                          # a film garnish: the game shows none for a mob
            stand_in = _FxBlock("%s_knock%d" % (door.name, i), cell, [box], (tex, None),
                                getattr(world, "world", world), h)
            b = fx._hit_particles(stand_in, h, h + int(crumbs) * TICK + 1e-3, Vector(pos) + Vector((0, 0, 1.5)),
                                  camera, seed if seed is not None else i, glow)
            burst = b if burst is None else burst.extend(b)
    if fb is not None:
        halves = ("lower", "upper") if break_door == "both" else ("lower",)
        res = globals()["break_door"](door, fb, camera=camera, halves=halves, seed=seed or 0, glow=glow, drop=drop,
                                      world=world)
        burst = res["burst"] if burst is None else burst.extend(res["burst"])
        item = res["item"]
        phase_end = 0.0
    else:
        t.crack(f1, -1, half)                                 # the mob stops: destroyBlockProgress(-1)
        stages.append((f1, -1))
        c = (phase * attempt + (f1 - f0)) % cycle
        phase_end = c / attempt if c < attempt else 0.0
    return {"stand": pos, "yaw": yaw, "knocks": knocks, "hits": hits, "stages": stages, "resets": resets,
            "frame": fb, "burst": burst, "item": item, "phase": phase_end, "attempt": attempt}


def crack_texels(door, stage, half="upper"):
    """World points of the centres of the crack texels of `stage` that are drawn on the FRONT face of a door's
    half ("both": the same pattern on each block): what a camera on the door's front has to see of it."""
    t = _door(door)
    info = t.info
    _mul, mask = crack_factors(stage)
    n = info["normal"]
    direction = nearest_direction(n)
    out = []
    for h in (("lower", "upper") if half == "both" else (half,)):
        cell = info["cell"] if h == "lower" else info["upper"]
        box = t.half_box(h)
        for r in range(16):
            for c in range(16):
                if not mask[r, c]:
                    continue
                u, v = (c + 0.5) / 16.0, (r + 0.5) / 16.0
                if direction in ("west", "east"):             # decal_uv inverted for a wall face
                    zm = 1.0 - u if direction == "west" else u
                    bx = box[0] if n.x < 0 else box[3]
                    b = (bx, 1.0 - zm, 1.0 - v)
                else:
                    xm = 1.0 - u if direction == "north" else u
                    by = box[4] if n.y > 0 else box[1]
                    b = (xm, by, 1.0 - v)
                out.append(Vector((cell[0] + b[0], cell[1] + b[1], cell[2] + b[2])))
    return out


def visible_texels(door, stage, eye, frame=None, half="upper"):
    """(seen, drawn): how many of a stage's crack texels on the door's front a camera at world point `eye` sees
    past whatever stands in front of the door at `frame` (default: the current frame). Ray casts on the scene as
    it is rendered then; the door itself does not count as an obstacle."""
    scene = bpy.context.scene
    if frame is not None:
        scene.frame_set(int(frame))
    deps = bpy.context.evaluated_depsgraph_get()
    eye = Vector(eye)
    pts = crack_texels(door, stage, half)
    seen = 0
    for p in pts:
        d = p - eye
        dist = d.length
        hit, _loc, _nrm, _idx, _ob, _mat = scene.ray_cast(deps, eye, d / dist, distance=dist - 0.02)
        seen += 0 if hit else 1
    return seen, len(pts)


# ----------------------------------------------------------------------------------------------------
# self-test: the proof films
# ----------------------------------------------------------------------------------------------------
NIGHT = dict(preset="night", az=176.0, el=21.0, bloom=1.3, grade="cool")      # the look-dev night (poppy_night)
DAY = dict(preset="golden", az=215.0, el=27.0, bloom=1.0, grade="warm")       # a low sun on house_a's west front
MEADOW = dict(preset="golden", az=62.0, el=27.0, bloom=1.0, grade="warm")     # the look-dev golden hour
TORCHES = 1.3
DOOR_CAM = {          # name -> (position, target, lens): house_a's door from the plaza
    "close": ((7.85, -7.5, 2.0), (10.0, -7.5, 2.0), 30.0),          # 2 blocks: the door fills the frame
    "plaza": ((3.4, -7.5, 0.75), (10.0, -7.5, 1.45), 47.0),         # story beat 18: low, a block of wall either side
    "side": ((4.4, -10.4, 0.75), (10.0, -7.6, 1.5), 47.0),          # the same from the free-edge side, 27 degrees off
    "far": ((-2.0, -6.9, 1.7), (10.0, -7.5, 2.0), 110.0),           # 12 blocks
}


def build_door_proof(scene, sky="night", shudder=1.5, half="upper", along=0.0, every=16.0, with_zombie=True,
                     break_at_end=False):
    """The door proof film on the real village: shot "sheet" (frames 1-12: clean, stages 0..9, clean; close
    camera), shot "bang" (96 frames: a zombie at house_a's door, attempts of 40 frames) and shot "far" (the same
    knocking from 12 blocks, optionally ending with the door broken). Returns a dict of everything built."""
    from films import lookdev

    from . import look, shots, undead, village

    v = village.build_village(scene, seed=1)
    cfg = NIGHT if sky == "night" else DAY
    skyobj = look.set_time(scene, cfg["preset"], sun_azimuth=cfg["az"], sun_elevation=cfg["el"])
    look.setup_compositor(scene, bloom=cfg["bloom"], grade=cfg["grade"])
    film = shots.Film(scene, fps=FPS)
    st = lookdev.Stage(scene, film, v, skyobj)
    door = v.doors["house_a"]
    lights = door_torches(v, "house_a")
    z = undead.add_zombie(st, "zombie") if with_zombie else None
    out = {"film": film, "stage": st, "village": v, "door": door, "zombie": z, "lights": lights, "shots": {}}

    def cam(s, name, fstop=4.0):
        pos, target, lens = DOOR_CAM[name]
        s.lens(lens, fstop)
        s.move(pos, target)
        s.focus((10.0, -7.5, 2.0))
        s.handheld(0.012, seed=len(out["shots"]) + 5)       # a film camera is never dead still: motion blur is on

    s = st.shot("sheet", 12 / float(FPS))
    cam(s, "close", fstop=5.6)
    for i in range(10):
        crack(door, s.frame_start + 1 + i, i, half)
    crack(door, s.frame_start + 11, -1, half)
    st.lights(s, scale=TORCHES)
    out["shots"]["sheet"] = s

    s = st.shot("bang", 96 / float(FPS))
    cam(s, "plaza")
    if z is not None:
        r = bang_on_door(z, door, s.frame_start, s.frame_end + 1, attempt=40, pause=2, every=every, first=4,
                         half=half, shudder=shudder, along=along, camera=s, world=v)
        st.use(s, z)
        out["bang"] = r
    st.lights(s, scale=TORCHES)
    out["shots"]["bang"] = s

    s = st.shot("far", 48 / float(FPS))
    cam(s, "far", fstop=4.0)
    if z is not None:
        end = s.frame_end - 13 if break_at_end else s.frame_end + 1      # (the door breaks 14 frames before the end)
        r2 = bang_on_door(z, door, s.frame_start, end, attempt=None if break_at_end else 40, pause=2, every=every,
                          first=4, half=half, shudder=shudder, along=along, camera=s, world=v, phase=0.55,
                          place=False, break_door=break_at_end and "both", drop=break_at_end)
        st.use(s, z)
        out["far"] = r2
    else:
        crack(door, s.frame_start, 6, half)
    st.lights(s, scale=TORCHES)
    out["shots"]["far"] = s
    st.finish()
    return out


MINE_SPOT = (-3, 31, 0)        # a grass cell of the plant-free verge beside the exit road (village.CAMERA_LANE)


def build_mine_proof(scene, duration=48):
    """The mining proof film in the meadow: a stone block on the grass fist-mined by a player (compressed to
    `duration` frames, drops nothing), then a dirt block mined in the game's own 18 frames with its drop."""
    from films import lookdev

    from . import look, players, shots, village

    v = village.build_village(scene, seed=1)
    cfg = MEADOW
    skyobj = look.set_time(scene, cfg["preset"], sun_azimuth=cfg["az"], sun_elevation=cfg["el"])
    look.setup_compositor(scene, bloom=cfg["bloom"], grade=cfg["grade"])
    film = shots.Film(scene, fps=FPS)
    st = lookdev.Stage(scene, film, v, skyobj)
    cx, cy, cz = MINE_SPOT
    ground = v.world.top(cx, cy)
    cz = (ground + 1) if ground is not None else cz
    stone = place_block(v.collection, "stone", (cx, cy, cz), world=v)
    steve = players.add_player(st, "miner", "steve")
    st.cast[stone.name] = stone                  # so that Stage.finish() hides it outside the shots that use it
    stand = (cx + 0.5, cy - 0.85, float(cz))
    out = {"film": film, "stage": st, "village": v, "stone": stone, "player": steve, "shots": {}}

    s = st.shot("stone", (duration + 30) / float(FPS))
    s.lens(40, 4.0)
    s.move((cx + 4.2, cy - 2.1, cz + 0.95), (cx + 0.45, cy - 0.3, cz + 0.8))
    s.focus(stone.center)
    steve.place(s.frame_start, stand, lookdev.yaw_to(stand, stone.center))
    steve.look_at(s.frame_start, stone.center, ease=0)
    out["stone_mine"] = mine(steve, stone, s.frame_start + 6, duration=duration, camera=s)
    st.use(s, steve, stone)
    st.lights(s, scale=0.0)
    out["shots"]["stone"] = s

    s = st.shot("dirt", 72 / float(FPS))
    dirt = out["dirt"] = place_block(v.collection, "dirt", (cx, cy, cz), world=v, name="proof_dirt",
                                     frame=s.frame_start)       # placed on the cut: it is not there before
    s.lens(40, 4.0)
    s.move((cx + 4.2, cy - 2.1, cz + 0.95), (cx + 0.45, cy - 0.3, cz + 0.8))
    s.focus(dirt.center)
    steve.place(s.frame_start, stand, lookdev.yaw_to(stand, dirt.center))
    steve.look_at(s.frame_start, dirt.center, ease=0)
    out["dirt_mine"] = mine(steve, dirt, s.frame_start + 8, camera=s, seed=0, until=s.frame_end + 1)
    item = out["dirt_mine"]["item"]
    if item is not None:
        st.cast[item.name] = item
        st.use(s, item)
    st.use(s, steve)
    st.lights(s, scale=0.0)
    out["shots"]["dirt"] = s
    st.finish()
    return out


PROOFS = ("stages_night", "stages_day", "zombie", "zombie_film", "blow_plain", "blow_shudder", "blow_shudder4",
          "blow_shudder8", "zfight_night", "zfight_day", "mine", "dirt", "doorbreak", "flesh")
FILM_STAGING = dict(half="both", along=-0.3)     # what makes the cracks readable past the zombie (see MEASURED)


def _out_dir():
    import os

    path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "out", "test")
    os.makedirs(path, exist_ok=True)
    return path


def _fresh(res=(540, 960), samples=16, motion_blur=True):
    from . import look

    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    look.setup_render(scene, res=res, samples=min(samples, 16), threads=2, motion_blur=motion_blur)
    scene.cycles.adaptive_min_samples = max(4, scene.cycles.samples // 3)
    return scene


def _render(scene, film, frame, name, res=None, border=None):
    """One proof still; border = (x0, x1, y0, y1) fractions of the frame (y from the bottom) renders that part
    only, at the frame's pixel density."""
    import os
    import time

    t = time.time()
    if res is not None:
        scene.render.resolution_x, scene.render.resolution_y = res
    r = scene.render
    r.use_border = r.use_crop_to_border = border is not None
    if border is not None:
        r.border_min_x, r.border_max_x, r.border_min_y, r.border_max_y = border
    film.goto(frame)
    path = os.path.join(_out_dir(), "breaking_%s.png" % name)
    scene.render.filepath = path
    bpy.ops.render.render(write_still=True)
    print("[breaking] %-22s frame %3d -> %s  %.1f s" % (name, frame, path, time.time() - t), flush=True)
    return path


def _sheet(paths, name, cols, labels=None):
    """Paste stills into one sheet (the tiles stay on disk next to it)."""
    import os

    from PIL import Image, ImageDraw

    tiles = [Image.open(p).convert("RGB") for p in paths]
    w, h = tiles[0].size
    rows = (len(tiles) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * w, rows * h), (0, 0, 0))
    for i, im in enumerate(tiles):
        sheet.paste(im, ((i % cols) * w, (i // cols) * h))
        if labels:
            d = ImageDraw.Draw(sheet)
            d.rectangle([(i % cols) * w, (i // cols) * h, (i % cols) * w + 8 * len(labels[i]) + 6,
                         (i // cols) * h + 14], fill=(0, 0, 0))
            d.text(((i % cols) * w + 3, (i // cols) * h + 1), labels[i], fill=(255, 255, 255))
    path = os.path.join(_out_dir(), "breaking_%s.png" % name)
    sheet.save(path)
    print("[breaking] sheet %s (%dx%d)" % (path, sheet.size[0], sheet.size[1]), flush=True)
    return path


def _stills(names):
    """Render the proof stills named (see PROOFS); each name is one call's worth under the 300 s limit."""
    import os

    for name in names:
        if name in ("stages_night", "stages_day"):
            scene = _fresh(res=(270, 480), motion_blur=False)
            p = build_door_proof(scene, sky=name.split("_")[1], with_zombie=False)
            f0 = p["shots"]["sheet"].frame_start
            paths = [_render(scene, p["film"], f0 + 1 + i, "%s_%d" % (name, i)) for i in range(10)]
            _sheet(paths, name, 5, ["stage %d" % i for i in range(10)])
            for q in paths:
                os.remove(q)
        elif name in ("zombie", "zombie_film"):
            # "zombie" = the game's staging (upper half, centred) from straight behind; "zombie_film" = both
            # halves cracked, the zombie 0.3 toward the hinge, the camera on the side of the door's free edge
            scene = _fresh()
            p = build_door_proof(scene, sky="night", **(FILM_STAGING if name == "zombie_film" else {}))
            s = p["shots"]["bang"]
            if name == "zombie_film":
                pos, target, lens = DOOR_CAM["side"]
                s.lens(lens, 4.0)
                s.move(pos, target)
                p["film"].finalize()
            r = p["bang"]
            eye = DOOR_CAM["side" if name == "zombie_film" else "plaza"][0]
            for want in (2, 5, 9):
                # a frame of that stage on which the arms are in mid-swing (2-4 frames after a swing starts)
                frames = [f for f in range(s.frame_start, s.frame_end + 1) if stage_at(p["door"], f) == want]
                mid = [f for f in frames if any(2 <= f - k <= 4 for k in r["knocks"])]
                f = (mid or frames)[0]
                seen, drawn = visible_texels(p["door"], want, eye, frame=f,
                                             half="both" if name == "zombie_film" else "upper")
                print("[breaking] %s stage %d, frame %d: the lens sees %d of the %d crack texels on the door's front"
                      % (name, want, f, seen, drawn), flush=True)
                _render(scene, p["film"], f, "%s_s%d" % (name, want))
        elif name in ("blow_plain", "blow_shudder", "blow_shudder4", "blow_shudder8"):
            # six consecutive frames around one blow: the middle of the 540x960 frame (270x480 px a tile)
            scene = _fresh(res=(540, 960))
            amount = {"blow_plain": 0.0, "blow_shudder": 1.5, "blow_shudder4": 4.0, "blow_shudder8": 8.0}[name]
            p = build_door_proof(scene, sky="night", shudder=amount, **FILM_STAGING)
            s = p["shots"]["bang"]
            pos, target, lens = DOOR_CAM["side"]
            s.lens(lens, 4.0)
            s.move(pos, target)
            p["film"].finalize()
            hit = p["bang"]["hits"][1]                          # (a blow that no reset of the cracks falls on)
            paths = [_render(scene, p["film"], hit - 2 + i, "%s_%d" % (name, i), border=(0.24, 0.74, 0.36, 0.86))
                     for i in range(6)]
            _sheet(paths, name, 6, ["blow %+d" % (i - 2) for i in range(6)])
            for q in paths:
                os.remove(q)
        elif name in ("zfight_night", "zfight_day"):
            scene = _fresh()
            p = build_door_proof(scene, sky=name.split("_")[1], with_zombie=False)
            _render(scene, p["film"], p["shots"]["sheet"].frame_start + 7, name + "_near")
            _render(scene, p["film"], p["shots"]["far"].frame_start + 2, name + "_far")
        elif name == "doorbreak":
            scene = _fresh(res=(270, 480))
            p = build_door_proof(scene, sky="night", break_at_end=True)
            fb = p["far"]["frame"]
            s = p["shots"]["far"]
            pos, target, lens = DOOR_CAM["plaza"]
            s.lens(lens, 4.0)
            s.move(pos, target)
            p["film"].finalize()
            paths = [_render(scene, p["film"], fb + d, "%s_%d" % (name, i)) for i, d in enumerate((-1, 0, 2, 5, 10))]
            _sheet(paths, name, 5, ["break %+d" % d for d in (-1, 0, 2, 5, 10)])
            for q in paths:
                os.remove(q)
        elif name == "flesh":
            # the morning after: one piece of rotten flesh where the zombie stood (engine.mobs, placed by hand)
            from . import mobs

            scene = _fresh()
            p = build_door_proof(scene, sky="day", with_zombie=False)
            s = p["shots"]["bang"]
            item = mobs.make_dropped_item("rotten_flesh")
            item.place(s.frame_start, stand_point(p["door"])[0])
            item.face(s.frame_start + 10, DOOR_CAM["plaza"][0])
            item.animate(s.frame_start, s.frame_end + 1)
            item.show(s.frame_start, True)
            _render(scene, p["film"], s.frame_start + 10, name)
        elif name == "mine":
            scene = _fresh(res=(405, 720))
            p = build_mine_proof(scene)
            m = p["stone_mine"]
            frames = []
            for want in (1, 4, 6, 9):
                frames.append(next(f for f, st_ in m["stages"] if st_ == want) + 1)
            frames.append(m["frame"] + 1)
            paths = [_render(scene, p["film"], f, "mine_%d" % i) for i, f in enumerate(frames)]
            _sheet(paths, "mine", 5, ["stage 1", "stage 4", "stage 6", "stage 9", "broken +1"])
        elif name == "dirt":
            scene = _fresh(res=(405, 720))
            p = build_mine_proof(scene)
            m = p["dirt_mine"]
            deltas = (-1, 0, 2, 6, 30)
            paths = [_render(scene, p["film"], m["frame"] + d, "dirt_%d" % i) for i, d in enumerate(deltas)]
            _sheet(paths, "dirt", 5, ["break %+d" % d for d in deltas])
        else:
            raise SystemExit("breaking: unknown proof %r (one of %s)" % (name, ", ".join(PROOFS)))
    return 0


def _check():
    """Numeric checks of the module on small built scenes (no rendering). Returns the number that failed."""
    bad = []

    def ok(label, cond, detail=""):
        if not cond:
            bad.append(label)
        print("%-4s %s%s" % ("OK" if cond else "FAIL", label, ("  [%s]" % detail) if detail else ""))

    # 1. timing
    got = {k: (break_ticks(*k, exact=False), break_ticks(*k)) for k in TIMES}
    ok("break_ticks reproduces TIMES: by the formula stone by hand 150 ticks = 7.5 s, dirt 15 = 0.75 s, netherrack "
       "40 = 2 s, golden pickaxe 0; as the client adds floats: stone 151, netherrack 41",
       got == TIMES, ", ".join("%s/%s %s" % (k[0], k[1], v) for k, v in got.items() if TIMES[k] != v))
    ok("seconds = hardness x 1.5 with the right tool, x 5 without, / tool speed (within a tick)",
       all(abs(break_seconds(b, t) - h * (1.5 if c else 5.0) / s) <= 0.0501 for b, t, h, c, s in (
           ("stone", "hand", 1.5, False, 1.0), ("dirt", "hand", 0.5, True, 1.0),
           ("netherrack", "hand", 0.4, False, 1.0),
           ("stone", "iron_pickaxe", 1.5, True, 6.0), ("oak_planks", "hand", 2.0, True, 1.0),
           ("obsidian", "diamond_pickaxe", 50.0, True, 8.0))))
    ok("drops: stone by hand nothing, with a pickaxe cobblestone; dirt dirt; grass block dirt; netherrack by hand "
       "nothing", (drops("stone"), drops("stone", "wooden_pickaxe"), drops("dirt"), drops("grass_block"),
                   drops("netherrack"), drops("netherrack", "golden_pickaxe"), drops("obsidian", "iron_pickaxe"))
       == (None, "cobblestone", "dirt", "dirt", None, "netherrack", None))
    tr = progress_track("stone", "hand")
    st10 = [int(p * 10.0) for p in tr]
    firsts = [st10.index(s) + 1 for s in range(10)]
    ok("stone by hand: stage (int)(progress x 10) from tick 1, a new stage every 15 ticks, stage 9 until the break",
       firsts[0] == 1 and all(14 <= b - a <= 16 for a, b in zip(firsts, firsts[1:])) and max(st10[:-1]) == 9
       and st10 == sorted(st10), "first tick of each stage %s" % firsts)
    # 2. the crack textures
    counts = []
    for s in range(10):
        mul, mask = crack_factors(s)
        counts.append(int(mask.sum()))
        vals = sorted({round(float(x), 3) for x in mul[mask][:, 0]})
        if s == 9:
            ok("crack texels are two multipliers, 0.20 (dark) and 1.54 (light), never white lines",
               len(vals) == 2 and abs(vals[0] - 0.1975) < 2e-3 and abs(vals[1] - 1.537) < 2e-3, str(vals))
    ok("each stage draws more texels than the one before (4 ... 145 of 256)",
       counts == sorted(counts) and counts[0] == 4 and counts[-1] == 145, str(counts))

    # 3. a village door
    from . import shots, stamp, undead, village
    from .characters import _val

    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    v = village.build_village(scene, seed=1)
    film = shots.Film(scene, fps=FPS)
    s = film.shot("check", 0.0, 900 / 24.0)
    s.move((3.4, -7.5, 0.75), (10.0, -7.5, 1.72))
    film.finalize()                                           # (also gives the particles a scene camera)
    door = v.doors["house_a"]
    info = door_info(door)
    ok("house_a's door: cells (10, -8, 1) / (10, -8, 2), front = west, slab x 10.0 .. 10.1875",
       info["cell"] == (10, -8, 1) and info["upper"] == (10, -8, 2) and abs(info["normal"].x + 1.0) < 1e-6
       and abs(info["front"] + 10.0) < 1e-4 and abs(info["thickness"] - 0.1875) < 1e-4,
       "cell %s normal %s thickness %.4f" % (info["cell"], tuple(round(c, 3) for c in info["normal"]),
                                             info["thickness"]))
    pos, yaw = stand_point(door)
    ok("zombie stand point (9.7, -7.5, 1.0), yaw +90 degrees (facing east, into the door)",
       max(abs(a - b) for a, b in zip(pos, (9.7, -7.5, 1.0))) < 1e-4 and abs(yaw - math.pi / 2) < 1e-6,
       "%s yaw %.1f" % (tuple(round(c, 3) for c in pos), math.degrees(yaw)))
    crack(door, 10, 4)
    crack(door, 20, 7, half="both")
    crack(door, 30, -1)
    t = _door(door)
    var = t.variants[(4, "upper")]
    me = var.data
    uvl = me.uv_layers[CRACK_UV].data
    on_grid, spans = True, {}
    cracked = [i for i, m in enumerate(me.materials) if m is not None and "|crack" in m.name]
    bpy.context.view_layer.update()
    for poly in me.polygons:
        us = [uvl[li].uv[0] * 16.0 for li in poly.loop_indices]
        vs = [uvl[li].uv[1] * 16.0 for li in poly.loop_indices]
        if poly.material_index in cracked:
            on_grid &= all(abs(u - round(u)) < 1e-4 for u in us + vs)
            spans[nearest_direction(var.matrix_world.to_3x3() @ poly.normal)] = (round(max(us) - min(us), 3),
                                                                                round(max(vs) - min(vs), 3))
    ok("door stage 4, upper half: every cracked face corner is on the 16x16 texel grid; the front face spans "
       "16 x 16 texels, the edges 3 texels", on_grid and spans.get("west") == (16.0, 16.0)
       and spans.get("north", (0, 0))[0] == 3.0, str(spans))
    n_lower = sum(1 for p in me.polygons if p.material_index in cracked and p.center.z < 1.0)
    n_upper = sum(1 for p in me.polygons if p.material_index in cracked and p.center.z > 1.0)
    ok("half='upper' cracks only the upper block's faces (the game), half='both' all of them",
       n_lower == 0 and n_upper >= 5 and all("|crack" in m.name for m in t.variants[(7, "both")].data.materials),
       "upper %d lower %d" % (n_upper, n_lower))

    def visible(f):
        scene.frame_set(f)
        return [o.name for o in t.objects if not o.hide_render]

    seen = [visible(f) for f in (5, 10, 19, 20, 29, 30)]
    both = t.variants[(7, "both")].name
    ok("exactly one copy of the door is rendered on every frame: plain, stage 4, stage 7, plain",
       seen == [[door.name], [var.name], [var.name], [both], [both], [door.name]], str(seen))
    ok("stage_at reads the keys back", [stage_at(door, f) for f in (9, 10, 25, 31)] == [-1, 4, 7, -1])
    ok("the cracked copies are children of the door (they follow its hinge) and no material is animated",
       all(o.parent == door for o in t.variants.values())
       and all(m.node_tree.animation_data is None for o in t.objects for m in o.data.materials))
    # 4. the frame fingerprint (nothing else moves on these frames)
    fa, fb_ = stamp.Fingerprinter(scene, film), stamp.Fingerprinter(scene, film)
    frames = [8, 9, 10, 11, 19, 20, 29, 30, 31]
    one = {f: fa.frame(f)["parts"]["o"] for f in frames}
    two = {f: fb_.frame(f)["parts"]["o"] for f in reversed(frames)}
    ok("stamp: a fingerprint changes exactly where the crack stage does (9|10, 19|20, 29|30) and nowhere else",
       one[8] == one[9] and one[9] != one[10] and one[10] == one[11] and one[19] != one[20] and one[29] != one[30]
       and one[30] == one[31] and one[31] == one[8] and one[10] != one[20])
    ok("stamp: the same fingerprints whichever frame a process looks at first", one == two)
    # 5. the zombie at the door
    lights = door_torches(v, "house_a")
    ok("door_torches: two lights at the wall torches (9.71, -6.5 / -8.5, 2.89), the merged one off",
       len(lights) == 2 and sorted(round(L.location.y, 2) for L in lights) == [-8.5, -6.5]
       and all(abs(L.location.x - 9.7125) < 1e-3 and abs(L.location.z - 2.8875) < 1e-3 for L in lights)
       and abs(sum(L["base_energy"] for L in lights) - 159.5) < 1e-3
       and all(L in v.lantern_lights for L in lights), str([tuple(round(c, 3) for c in L.location) for L in lights]))
    z = undead.make_zombie("check_zombie")
    r = bang_on_door(z, door, 101, 221, attempt=40, pause=2, every=16, first=4, shudder=1.0)
    seq = [st_ for _f, st_ in r["stages"]]
    ok("bang_on_door: stages 0..9 in 4-frame steps, cleared for 2 frames, again, and cleared at the end",
       seq[:11] == list(range(10)) + [-1] and seq[11] == 0 and seq[-1] == -1
       and [f for f, _s in r["stages"][:11]] == [101 + 4 * i for i in range(10)] + [141] and r["resets"][0] == 141,
       str(r["stages"][:13]))
    ok("... a swing every 16 frames from frame 105; the zombie's arms are raised and chop on each",
       r["knocks"] == list(range(105, 221, 16)) and abs(z.arm_base(150) - undead.ARMS_RAISED) < 1e-6
       and z.swing_value(105 + 4) > 0.2 and z.swing_value(105 + 12) == 0.0, str(r["knocks"]))
    ok("... phase to continue with: the attempt is %d %% done at frame_end" % round(100 * r["phase"]),
       abs(r["phase"] - ((221 - 101) % 42) / 40.0) < 1e-6, "%.3f" % r["phase"])
    h = r["hits"][0]
    ang = [_val(door, "rotation_euler", 2, f) - float(door["closed_yaw"]) for f in (h - 1, h, h + 1, h + 2, h + 3)]
    want = SHUDDER_PIXELS / 16.0
    ok("shudder: the free edge moves 0.5 pixel inward on the blow, rebounds, at rest after 3 frames",
       abs(ang[0]) < 1e-7 and abs(ang[1] - want) < 1e-6 and ang[2] < 0 and abs(ang[4]) < 1e-7
       and h == int(round(105 + HIT_DELAY)), "angles %s" % [round(a, 4) for a in ang])
    r2 = bang_on_door(z, door, 301, 421, phase=0.5, break_door=True, place=False, drop=True, world=v)
    ok("break_door=True: one attempt timed to end ON frame_end; the door and its copies are gone from that frame",
       r2["frame"] == 421 and abs(r2["attempt"] - 240.0) < 1e-6 and r2["stages"][0] == (301, 5)
       and visible(420) != [] and visible(421) == [], "break %s, visible at 420: %s" % (r2["frame"], visible(420)))
    ok("... 32 particles, all of the LOWER half's slab (the game), showing oak_door_bottom; the oak_door item drops",
       len(r2["burst"].particles) == 32
       and all(10.0 - 1e-6 <= p["pos"][0][0] <= 10.1875 + 1e-6 and 1.0 <= p["pos"][0][2] <= 2.0
               for p in r2["burst"].particles)
       and r2["item"] is not None and "oak_door_bottom" in r2["burst"].objects[0].data.materials[0].name,
       "%d particles" % len(r2["burst"].particles))
    # 6. a block of its own
    cell = (-3, 31, v.world.top(-3, 31) + 1)
    rock = place_block(v.collection, "stone", cell, world=v)
    turf = place_block(v.collection, "grass_block", (cell[0] + 2, cell[1], cell[2]), {"snowy": "false"}, world=v)
    ok("place_block: a stone cube of 6 faces at its cell; a grass block has its 3 textures",
       len(rock.object.data.polygons) == 6 and tuple(rock.object.location) == tuple(float(c) for c in cell)
       and len(turf.object.data.materials) == 3 and rock.full_cube,
       "%d faces, %d materials" % (len(rock.object.data.polygons), len(turf.object.data.materials)))
    ok("break particles: stone shows block/stone; a grass block's are plain dirt, not tinted",
       rock.particle_texture == ("block/stone", None) and turf.particle_texture == ("block/dirt", None),
       "%s %s" % (rock.particle_texture, turf.particle_texture))
    from . import players

    steve = players.make_player("check_miner", "steve")
    steve.place(500, (cell[0] + 0.5, cell[1] - 0.9, float(cell[2])), 0.0)
    m = mine(steve, rock, 510, duration=48)
    ok("mine(duration=48): ten stages in 48 frames, the first on the frame after the click, broken on 558",
       [st_ for _f, st_ in m["stages"]] == list(range(10)) and m["stages"][0][0] == 511 and m["frame"] == 558
       and m["ticks"] == 151 and m["drop"] is None and m["item"] is None, str(m["stages"]))
    ok("... 11 arm swings 4.8 frames apart (the game's 151 ticks would be 38), 64 break particles + 40 crumbs",
       len(m["swings"]) == 11 and abs(m["swings"][1] - m["swings"][0] - 4.8) < 1e-6
       and len(m["burst"].particles) == 64 + 40, "%d swings, %d particles" % (len(m["swings"]),
                                                                              len(m["burst"].particles)))
    scene.frame_set(557)
    before = [o.name for o in rock.objects if not o.hide_render]
    scene.frame_set(558)
    after = [o.name for o in rock.objects if not o.hide_render]
    ok("... stage 9 is what is rendered on the last frame, nothing on the break frame",
       before == [rock.variants[9].name] and after == [], "%s -> %s" % (before, after))
    m2 = mine(steve, turf, 600, seed=5)
    it = m2["item"]
    ok("grass block by hand: the game's 18 ticks = 22 frames, drops dirt from the middle of the block",
       m2["ticks"] == 18 and m2["frames"] == 22 and m2["drop"] == "dirt" and it is not None
       and all(abs(it.spawn_point[i] - (turf.cell[i] + 0.5)) <= 0.25 + (0.125 if i == 2 else 0) for i in range(3)),
       "ticks %d, spawn %s" % (m2["ticks"], tuple(round(c, 2) for c in it.spawn_point) if it else None))
    under = v.world.get(turf.cell[0], turf.cell[1], turf.cell[2] - 1)[0]
    want_z = turf.cell[2] - (1.0 / 16.0 if under == "dirt_path" else 0.0)
    ok("... the item falls onto the %s under it (z %.4f) and comes to rest inside 1.5 blocks" % (under, want_z),
       it is not None and abs(it.rest_pos.z - want_z) < 1e-6
       and (it.rest_pos.xy - turf.center.xy).length < 1.5 and it.land_frame > m2["frame"],
       "rest %s, lands on frame %s" % (tuple(round(c, 2) for c in it.rest_pos), it.land_frame) if it else "")
    hole = [place_block(v.collection, "netherrack", (cell[0] + 5, cell[1], cell[2] + 1 - i), world=v) for i in range(2)]
    d = dig(steve, hole, 700, tool="golden_pickaxe")
    pair = [place_block(v.collection, "stone", (cell[0] + 7, cell[1], cell[2] + 1 - i), world=v) for i in range(2)]
    d2 = dig(steve, pair, 800, tool="hand", duration=24)
    ok("dig: golden pickaxe on netherrack breaks on the click, the next block one tick later; by hand the next "
       "block starts 6 ticks after the break", [x["instant"] for x in d] == [True, True] and d[0]["frame"] == 700
       and d[1]["frame"] == 701 and d2[0]["frame"] == 824 and d2[1]["start"] == 831 and d2[1]["frame"] == 855,
       "%s / %s" % ([x["frame"] for x in d], [(x["start"], x["frame"]) for x in d2]))
    view = _SolidView(v.world, 825)
    ok("particles and drops see a broken block's cell as air and an unbroken one as solid",
       not view.solid(pair[0].cell) and view.solid(pair[1].cell) and view.solid((cell[0], cell[1], cell[2] - 1)))
    # 7. every door of the village (four facings, both hinges), on a frame nothing else uses
    worst, facings = 0.0, set()
    for dname, d in sorted(v.doors.items()):
        if d == door:
            continue
        di = door_info(d)
        facings.add((nearest_direction(di["normal"]), d.get("hinge")))
        crack(d, 2000, 9)
        dv = _door(d).variants[(9, "upper")]
        duv = dv.data.uv_layers[CRACK_UV].data
        dcr = [i for i, m_ in enumerate(dv.data.materials) if m_ is not None and "|crack" in m_.name]
        for poly in dv.data.polygons:
            if poly.material_index in dcr:
                for li in poly.loop_indices:
                    worst = max(worst, max(abs(c * 16.0 - round(c * 16.0)) for c in duv[li].uv))
        pts = crack_texels(d, 9)
        up = di["upper"]
        for q in pts:
            off = abs((q - di["center"]).dot(di["normal"]))            # on the front face
            inside = all(up[i] - 1e-6 <= q[i] <= up[i] + 1 + 1e-6 for i in range(3))
            worst = max(worst, off, 0.0 if inside else 1.0)
        sp, _syaw = stand_point(d)
        worst = max(worst, abs((Vector(sp) - di["center"]).dot(di["normal"]) - 0.3))
        crack(d, 2000, -1)
    ok("every other door of the village (%d doors, %s): crack corners on the texel grid, the 145 texels of stage 9 "
       "on the front face of the upper block, stand point 0.3 in front" % (len(v.doors) - 1, sorted(facings)),
       worst < 1e-4 and len(facings) >= 3, "largest deviation %.2e" % worst)
    # 8. the rest of the API
    slab = place_block(v.collection, "oak_planks", (cell[0] + 9, cell[1], cell[2]), world=v, frame=950)
    cp = crack_progress(slab, 960, 990, first=3, last=8)
    ok("crack_progress: stages 3..8 in equal steps over 30 frames, cleared on the last; a block placed on frame "
       "950 is not there before", cp == [(960 + 5 * i, 3 + i) for i in range(6)] + [(990, -1)]
       and not slab.there_at(949) and slab.there_at(950) and stage_at(slab, 989) == 8 and stage_at(slab, 990) == -1,
       str(cp))
    rnd = knock_frames(1, 24001, seed=7)
    gaps = [b - a for a, b in zip(rnd, rnd[1:])]
    ok("knock_frames(seed=): the game's draw, 1 tick in 20 once a swing is over: a swing every 1.3 s on average",
       650 < len(rnd) < 880 and min(gaps) >= 8 and abs(DOOR_SWING_MEAN_FRAMES - 31.2) < 1e-9,
       "%d swings in 1000 s (26 ticks apart on average: 769), shortest gap %d frames" % (len(rnd), min(gaps)))
    restore(door, 1000)
    rc = bang_on_door(z, door, 1001, 1049, attempt=24, every=12, first=0, crumbs=2, place=False, world=v)
    ok("restore() brings the broken door back; crumbs=2 gives two small crumbs per blow off the door's front",
       visible(1000) == [door.name] and len(rc["burst"].particles) == 2 * len(rc["hits"])
       and all(p["pos"][0][0] < 10.0 for p in rc["burst"].particles),
       "%d crumbs for %d blows" % (len(rc["burst"].particles), len(rc["hits"])))
    bd = break_door(door, 1100, halves=("lower", "upper"), world=v)
    ok("break_door(halves both): 64 particles, half of them oak_door_top",
       len(bd["burst"].particles) == 64
       and sum(1 for o in bd["burst"].objects if "oak_door_top" in o.data.materials[0].name) == 32)
    w = _blocks.World()
    w.fill(40, 40, -2, 42, 42, -1, "netherrack")
    cells = [(41, 41, -1), (41, 41, -2)]
    floor_objs = w.build(v.collection, "check_floor", skip=cells)
    pit = place_from_world(v.collection, w, cells)
    d3 = dig(steve, pit, 1200, tool="wooden_pickaxe")
    rests = [x["item"].rest_pos for x in d3]
    ok("a hole in a floor (World.build(skip=cells) + place_from_world + dig): 6 ticks a block with a wooden pickaxe, "
       "each drops netherrack, and both items stay inside the 1 x 1 hole (on the lower block, then on its floor)",
       len(floor_objs) >= 1 and [x["ticks"] for x in d3] == [6, 6] and [x["drop"] for x in d3] == ["netherrack"] * 2
       and all(41.12 <= r.x <= 41.88 and 41.12 <= r.y <= 41.88 for r in rests)
       and abs(rests[0].z + 1.0) < 1e-6 and abs(rests[1].z + 2.0) < 1e-6,
       "rest %s" % [tuple(round(c, 2) for c in r) for r in rests])
    print("[breaking] numeric checks: %d failed%s" % (len(bad), ": " + "; ".join(bad) if bad else ""))
    return len(bad)


def _selftest(argv):
    """`$BPY -m engine.breaking` = numeric checks; `$BPY -m engine.breaking stills NAME ...` renders proof stills."""
    if "stills" in argv:
        return _stills([a for a in argv if a != "stills"] or list(PROOFS))
    return _check()


if __name__ == "__main__":
    import sys

    sys.exit(1 if _selftest(sys.argv[1:]) else 0)
