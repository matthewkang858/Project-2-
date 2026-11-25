"""REDSTONE PARTS THAT WORK ON CAMERA: lever, piston and sticky piston, redstone dust, repeater, redstone lamp,
redstone torch (placed and held), redstone block, and the game's timings to play a small circuit in order.

New module; edits no other file. Shapes are the game's own block models and blockstates (engine.mcassets), textures
through engine.blocks' materials; numbers are transcribed from the 26.x client classes (named next to each constant
and listed below). Blender axes as everywhere: +X east, +Y north, +Z up, 1 block = 1 unit, 24 fps, 1 game tick =
1.2 frames. "frame" = a film frame; a few calls take a film TIME t (a float: ticks fall between frames).

WHAT IS AN OBJECT AND WHAT IS STATIC
  Every part this module makes is its own object (parts change during a film, and dust needs its tint, which the
  World's mesh does not give it). What never changes goes into the village through the hook: the stone a lever or
  wall torch hangs on, the block under a lamp, a wall, a floor (bench()). A cell a part occupies (or a block a
  piston moves into) must be EMPTY in the set's World: the kit refuses a taken cell (RedstoneError, naming it).
  A redstone block / lamp that never changes may also be plain b.w.set(...) in the hook (an unlit lamp; a lit
  lamp in the World glows but gives no light: use kit.lamp). Dust is never World blocks (mcassets gives it no tint).

PUBLIC API (k = redstone.kit(v) after build_village; EVERY builder returns a part with .name (unique in the kit),
            .show(frame, visible) and .objects; register parts with the Stage like characters: st.cast[p.name] = p;
            st.use(shot, p); for Stage.hero pass the objects: st.hero(shot, "door", *p.objects))
  IN THE HOOK (build_village(edit=...))
    bench(b, x0, y0, x1, y1, block="smooth_stone", level=None) -> dict(z, cells)   a level stone floor for parts
        (the grass top replaced, plants cleared, columns reserved); parts then stand in cells at z = dict["z"].
    carve(b, cells) -> {cell: state}          take cells out of the World (they become parts / moving blocks)
    door_cells(cells, side) -> [cells]        every cell a piston_door needs empty (door, head, piston cells)
  THE KIT
    kit(where, collection=None, sky_light=None) -> Kit      one per set (the Village or a blocks.World); the same kit
        comes back for the same set. sky_light (kit-wide, or per part: sky_light=...) = the set's sky-light level
        baked into the part's colours EXACTLY as engine.sets draws a World cell at that level: sets.lightmap of
        Environment._step (levels in pairs below 11, NOTHING DARKER THAN sets.LIGHT_FLOOR = 3: 0.137; levels 0-3
        are alike, never black), with the set's Brightness gamma. sky_light="auto" reads the level engine.sets
        baked around the part's cell (sets.env(b).bake_sky_light in the hook): a door block then gets the very
        tint of the baked wall beside it. None: no dimming. Lit lamps, lit torches and lit dust never dim.
    k.block(block_id, cell, props=None, frame=None, sky_light=None) -> movable block (an engine.breaking Breakable:
        .breakable .object .objects .cell_at(t)); what pistons push and pull. frame = placed ON that frame.
    k.lever(cell, face="floor"|"wall"|"ceiling", facing, powered=False) -> Lever
    k.piston(cell, facing, sticky=False, extended=False) -> Piston      facing: north east south west up down
    k.wire(cells, power=0 | {cell: level}, dots=(), source=None) -> Wire     dust lying IN these cells
    k.repeater(cell, toward, delay=1, powered=False) -> Repeater       toward = where the signal goes
    k.lamp(cell, lit=False, watts=None) -> Lamp      .light = its point light (LAMP_WATTS; LAMP_KEY_WATTS as a key)
    k.torch(cell, wall=None, lit=True, frame=None, watts=None) -> Torch  wall = the side a wall torch leans out to
    k.piston_door(cells, side, block="stone", closed=True) -> PistonDoor       ONE CALL for the door of "Two Apples"
    k.piston_row(cells, facing, carry="oak_planks", extended=True, sticky=True) -> PistonRow     ONE CALL for the
        twelve pistons of "Leg Day": each with `carry` on its arm (2 out extended, 1 out retracted)
    k.extend_all(pistons, frame) / k.retract_all(pistons, frame) -> end time       any set of pistons on one tick
    k.ride(thing, on, frame_start=None, frame_end=None)   thing (a block, Breakable, Object or Character) moves with
        the movable block `on` (see NOT THE GAME); k.show(frame, visible) every part of the kit
  LEVER
    .flip(frame, ease=0) / .set(frame, powered, ease=0) -> frame    the game swaps two models (no in-between frame):
        drawn from `frame` on (keyed at frame - 0.25: frame - 1's exposure is untouched). ease=2: a 2-frame swing
        ending ON frame (a film choice, off by default).
    .state_at(frame)   .hand_point(frame=None, along=0.8) -> the point on the handle a hand must reach (1.0 = tip)
    .stand(distance=0.58, side=None, lateral=0.22, along=0.5) -> ((x, y, z), yaw)     where a player stands so his
        right hand, at the far end of an engine.players attack() swing (SWING_REACH, measured), is at the handle
    flip_by(player, lever, frame, sync="game"|"hand", look=True, ease=0, look_from=None, reach=False) -> frame
        the lever changes on. The swing (players attack) starts ON frame (the click); sync="game": the lever
        changes the frame after (LEVER_SHOW_TICKS); sync="hand": on the frame his hand is nearest the handle.
        look=True turns his head to the handle from 6 frames before the click, but never from before his last
        place() (no pre-roll into the previous shot; look_from= sets the start). reach=True (film choice): his arm
        is lifted / turned during that swing (delta_rotation_euler x / z of his right arm, at most REACH_LIMIT 40
        degrees each, solved on the evaluated rig) so the fist touches the middle of the handle (MEASURED: the plain
        swing misses a wall lever in the block above the floor by 0.42 block; with reach=True 37 degrees, the fist
        centre 0.13 from the handle: the 0.25-wide fist touches it). lever.reach_info = what was measured.
        Without reach: a lever whose handle middle is about 1.3 above his feet meets the swing (a FLOOR lever on
        top of a 1-block pier), a wall lever in the block above the floor does not.
  PISTON
    .extend(t, push="auto", ride=()) -> t + 2.4   the head and the blocks in front travel 1 block in 2 ticks, linear;
        push="auto" = the kit's movable blocks in a line from the cell in front (or a list of them / of cells);
        13 or more -> RedstoneError, nothing moves; a block of the set's mesh in the way -> RedstoneError.
    .retract(t, pull="auto") -> t + 2.4           a sticky piston pulls the block in front of its head (None: not)
    .cancel(t)        take back the move starting at t (and its blocks' moves)
    .place(frame, player=None)   not there before `frame` (beat 13: placed on a powered spot it fires at once:
                      p.place(f, player=efe); p.extend(f) shows the slime face on frame f, the bare arm out by f + 3)
    .travel(t) (0 in .. 1 out)  .extended_at(t)  .look_at_frame(f) ('R' block / 'S' short head / 'L' long head)
    .head_point(t)    arm_inside(piston, frame) -> bool (the check that no head pokes out or leaves a gap)
  PISTON DOOR / ROW
    door.open(frame) / door.close(frame) -> end time; door.is_open(t); door.pistons, door.blocks, door.objects
    door.power(t) CLOSES it, door.unpower(t) OPENS it (powered pistons extend, as in the game) -> t
    row.retract(frame) / row.extend(frame) -> end time; row.power(t) / row.unpower(t) -> t (circuit steps);
    row.extended_at(t); row.pistons, row.blocks, row.objects.   Leg Day beats 18-19 in one line:
        t = lever.flip(f); redstone.unsignal(t, wire, row)   (the line dark and all twelve retracting on f)
  WIRE (redstone dust)
    .power(frame, source=None, level=15, ripple=0) -> frame   lit from `source` (default its source cell; a cell
        BESIDE the line = a lever / torch there): level - 1 per block of dust. ripple=N: block by block away from
        the source over N frames (a film choice; the game lights the line in one tick).
    .unpower(frame)   the whole line dark on one frame (the game: within one tick)
    .set_levels(frame, {cell: level}) .level_at(cell, frame) .levels(frame, source, level) .distances(source)
    .states  {cell: {'north': 'side'|'up'|'none', ...}} as the game connects it; dust_shape(state) names it
    wire_color(power) -> (r, g, b)   WIRE_COLORS: the game's table (power 0 (76, 0, 0) .. 15 (255, 50, 0))
    dust_tint(power), dust_albedo(power)   what the module draws dust with (see NOT THE GAME)
  REPEATER / LAMP / TORCH
    repeater.set(frame, powered)   .delay_ticks (= 2 x delay)
    lamp.set(frame, lit)   lamp.lit_at(frame)   lamp.light (keyed on exactly while lit; scale .light.data.energy)
    torch.set(frame, lit)  torch.remove(frame)  torch.plant(frame, player=None, hand="right", consume=False) ->
        frame it appears on: with a player his swing starts ON frame and the torch is there the frame after; it is
        not there before (a torch that is planted is made with k.torch(cell) and plant()ed)
    hold_torch(player, hand="right", frame=None, glow=True, watts=30) -> item    engine.players hold("redstone_torch")
        with its head glowing and a small light that is on exactly while the item is (a driver on its visibility);
        watts=HELD_TORCH_KEY_WATTS (120) when the held torch is the key on his face (beat 24)
  PLAYING A CIRCUIT ("powered from frame f")
    signal(frame, *steps) -> time   each step's input is powered when the step before it puts out its signal:
        a step = a part (wire, lever, lamp, piston, repeater, torch, ROW, DOOR) or a tuple of parts powered
        together. part.power(t) -> the time its output changes: wire 0, lever 0, lamp on 0, piston / row / door 0
        (+ 2 ticks of travel), repeater 2 x delay ticks, torch (an inverter: powered = goes OUT) 2 ticks.
    unsignal(frame, *steps) -> time  the same switched off (lamp off 4 ticks late, repeaters keep their delay)
    at(frame, ticks) -> film time    frame_of(t) -> the first whole frame that draws a change at time t
    Example (beat 7 of "Leg Day"):  torch = k.torch(c0); wire = k.wire(cells, source=c0)
        t = torch.plant(f, player=efe); redstone.signal(t, wire, repeater, (lamp, piston))
  PROOF AND MEASUREMENT
    proof_set(b, dark=False) / build_proof(scene, sky=None, dark_door=False) -> dict   the proof film in the real
        village (AREAS lists where); SKIES = golden (the look-dev sun) / dusk / night
    PROOFS = sheet_a sheet_b close dust bench lever column row door door_dark lights   (see SELF-TEST)
    palette_check(skies) -> failures    power-15 dust colour measured in the finished look (see MEASURED)
    light_study('floor' | 'lamp' | 'held')   the light measurements below, printed

WHAT THE GAME DOES (read from the classes; the constants at the top carry the class names)
  piston   checkIfExtend sends the block event in the same tick power arrives (start delay 0). The move is a
           PistonMovingBlockEntity: progress += 0.5 per tick, drawn at lerp(progressO, progress, partial tick):
           1 block in 2 ticks (2.4 frames), linear, for the head and every pushed / pulled block alike. The client
           makes its own moving block entity when the block event packet arrives (Minecraft.runTick: runAllTasks
           before tick()) and ticks it in that same tick (Level.tickBlockEntities adds pending tickers first), so
           the head moves in the tick the lamp beside it lights: the module starts both on the same tick. Pushing:
           the base becomes the extended model (piston_base) at once and the head (piston_head) slides out of it;
           retracting: the block entity draws the base AND the head. PistonHeadRenderer draws the head SHORT
           (piston_head_short: a 12 px arm) while it is 0.5 block or less out, the long one (16 px arm, 4 px into
           the base) beyond: the arm always ends inside the base. Push limit 12 (PistonStructureResolver
           .MAX_PUSH_DEPTH: 13 and it does not move at all). A sticky piston pulls the one block in front of its
           head. A normal piston leaves it.
  sticky   sticky_piston / piston_head_sticky: the face is block/piston_top_sticky (the slime-green one).
  lever    LeverBlock.pull sets the new state in the tick of the click; its blockstate swaps model lever <->
           lever_on (the handle element at -45 / +45 degrees about the base's X axis): no in-between. The client
           shows the server's change (the click itself only cycles a copy on the client): ~1 tick later.
  dust     redstone_wire multipart: dot + side0 / side_alt0 (line0) + side_alt1 / side1 (line1) + up pieces,
           chosen by getConnectionState: connections from getConnectingSide (dust, a repeater along its axis, any
           signal source; climbing 'up' a block side when the block above the dust is not a conductor; down past
           an edge), an unconnected dust is a cross unless right-clicked (dot), connections on one axis only run
           across the whole block. Tint: RedstoneWireBlock COLORS (f = power/15; r = 0.6 f + 0.4 (0.3 at 0),
           g = clamp(0.7 f^2 - 0.5), b = clamp(0.6 f^2 - 0.7); floor(x 255) in single precision), applied by
           BlockTintSources$10. Power falls one per block. Not a light source.
  repeater RepeaterBlock.getDelay = DELAY x 2 ticks, both ways; FACING is its INPUT side (toward is the other).
  lamp     RedstoneLampBlock: lit in the same tick, unlit 4 ticks after it loses power; light level 15.
  torch    RedstoneTorchBlock: light 7; TOGGLE_DELAY 2 ticks (inverter). The lit model (template_redstone_torch)
           puts a 3x3x3 px halo of single red texels around the 2x2 px head whose faces all point INWARD; blocks are
           drawn with back-face culling (RenderPipelines: the terrain pipelines keep the default cull), so from any
           side the near halo face is not drawn: the pink-white core shows inside a red frame. The module culls
           the same faces (Backfacing -> Transparent on the lit torch and repeater torches).
  falling  FallingBlock.getDelayAfterPlace = 2: an anvil whose plank is pulled away starts to fall 2 ticks after
           (for engine/fixtures.py; this module leaves it hanging).

MEASURED (`$BPY -m engine.redstone`: 34 numeric checks + 6 in the village; stills out/test/redstone_*.png)
  Piston: for moves starting at any phase of a frame, every frame's head (short / long) stays inside the base over
  the whole exposure and the moved block touches the head plate at every sampled moment (no gap, no overlap).
  extend(10.0): frames 8-9 the block model, 10 the short head, 11+ the long one; the head is 0.10 out at the
  middle of frame 10's exposure and 0.52 at frame 11's.
  Lever: the module's handle rotation lands within 1e-7 px of the game's other model for all 12 placements.
  Dust colour (palette_check, the dust pixels found by rendering with and without the dust, edges dropped, the
  brighter half): power 15 in the finished golden look (222, 77, 44) hue 11.1 degrees, saturation 0.80; at dusk
  (179, 60, 32) hue 11.4, saturation 0.82 (the game in daylight: (255, 50, 0) x texel, hue 11.8). Before the
  look's grade saturation step: (222, 65, 12) saturation 0.95. The first version drew (245, 126, 115) salmon.
  Saturation above about 0.81 is out of reach for ANY bright pixel in the look: its grade (look.GRADES warm /
  cool, saturation 0.97 in linear HSV) lifts every colour's smallest channel to 3 % of its largest.
  Light (light_study 'floor', night, the floor 1 / 2 / 3 blocks in front of each source, its light alone): lamp
  x1.11 / 1.10 / 1.17 of a village torch (the game: 1.11 / 1.11 / 1.12), redstone torch x0.33 / 0.30 / 0.29 (the
  game 0.38 / 0.34 / 0.29). Our point lights fall off as W / (d^2 + 1): from 1 to 3 blocks the torch-lit floor
  drops x10, the game's light (lightmap 13 -> 11) x1.25. ('lamp') golden hour, the narrator 2.7 blocks from a lit
  lamp, turned to it: his face x1.46 with LAMP_WATTS (reads), x2.93 with LAMP_KEY_WATTS (548 W); ('held') dusk,
  facing the lens, held redstone torch: face x1.19 at 30 W, x1.78 at HELD_TORCH_KEY_WATTS (120), x2.95 at 300 W.
  Door (redstone_door_strip): seen from above the aisle the opened doorway is a black square beside his hat
  (the stone face there 39 -> 27 of 255 when it opens). door_dark (engine.sets' sky light baked, parts "auto"):
  the door blocks get exactly the wall's tint (0.137, checked in the self-test), and so does everything else in
  the sealed box: closed and open measure alike (4 of 255) - see NOT THE GAME for what that means for film two.
  Render times (2 threads, 16 samples, loaded machine): a 960x540 sheet 11-13 s, a 360x640 strip tile 3-10 s.
  Fingerprints (`$BPY -m tools.check_redstone_stamp`): order-independent, identical in a second process, and
  changing on exactly the frames a lever / dust level / lamp / piston move changes (motion blur sampled).

NOT THE GAME, AND WHERE THE PICTURE DIFFERS FROM IT
  - Lit dust glows a little (DUST_GLOW 0.4 x power/15) and is drawn with a damped diffuse colour (dust_albedo:
    power 15 x DUST_ALBEDO 0.35, nothing under the knee): the look's sunlit floor is 1.24 x its texture, so the
    game's full red would sit over the highlight shoulder. dust_tint() raises the green of power 13-15 (15: (255,
    76, 0) instead of (255, 50, 0)) so that after the look's grade the DISPLAYED hue is the game's; power 0-12
    (no green in the game) is the game's colour. Dust is one opaque cut-out face per piece, lit like an up-facing
    surface, with its pieces DUST_LAYER_PX (0.05 px) apart (coplanar quads lose to a ray tracer) and without the
    never-seen faces against the block it lies on; the overlay texture is empty in this version and left out.
  - Lit torch heads glow (TORCH_GLOW: the pale core 0.8, the red 0.5, the stick 0.12) and their bright red
    texels' diffuse is x TORCH_RED_ALBEDO 0.55 (as the dust: no salmon in sun); the lit repeater's red line glows
    (REPEATER_GLOW). The held torch has the same material, no halo (it is the item sprite) and a light.
  - Light: LAMP_WATTS 137 / REDSTONE_TORCH_WATTS 50 match the game's brightness ratios to a torch (MEASURED), not
    its flat falloff. Redstone torch light is tinted (1.0, 0.62, 0.5): the game has one block-light colour. The
    lamp's own faces do not block its light (shadow linking). In the game a held torch lights nothing (shader
    packs add hand-held light): hold_torch's light is that film choice.
  - Underground (film two): engine.sets bakes sky light only, so a sealed hall is drawn at 0.137 everywhere,
    torch-lit walls too (the game takes the brighter of sky and block light). Parts follow that bake exactly, so
    the door is no black slab, but the black doorway does not read against a wall that dark: light the back wall
    with the film's own torches (as the proof's day strip does, torches x3) or do not bake that wall.
  - kit.ride() carries blocks and characters with a moved block: the game drops an anvil whose support moves,
    and carries entities only on an upward push. flip_by(sync="hand"), reach=True and plant() timing follow the
    arm, not the server tick. Pushed blocks keep their Breakable's .cell / .center at the original cell: use
    cell_at(t).
  - Not built: particles (the lever's and the dust's red specks, the torch's smoke), sounds, comparators,
    observers, slime / honey blocks, quasi-connectivity, locked repeaters, torch burnout, block placement
    animation (a planted torch is there on its frame), falling anvils (engine/fixtures.py).

GOTCHAS
  - Make parts AFTER build_village, cells left empty in the hook; make the parts a wire touches (levers, torches,
    repeaters, other dust) BEFORE the wire (its shapes are fixed when it is made).
  - Visibility of every part is keyed by the module (and Stage.finish through .show): never key hide_render on a
    part's objects yourself. Stage.lights does not touch this module's lights (they are not village lights).
  - Calls may come in any order; a piston refuses overlapping moves (RedstoneError): cancel(t) first to re-time.
  - Visibility changes land on whole frames (frame_of); moves are keyed at their exact (fractional) times.
  - Names: a second default-named row / door / part gets _2, _3 ... (Stage keys st.cast by name).
  - flip_by(reach=True) keys delta_rotation_euler on the player's right arm: do not key it yourself there.
  - A film that imports engine.redstone has this file in its engine hash: freeze it while finals render.

SELF-TEST
    $BPY -m engine.redstone                    numeric checks + the proof film in the village (about 40 s)
    $BPY -m engine.redstone quick              numeric checks only
    $BPY -m engine.redstone stills NAME ...    proof stills out/test/redstone_<name>.png: sheet_a sheet_b close
                                               dust lights (stills) and bench lever column row door door_dark
                                               (strips of tiles redstone_<name>_f<frame>.png + _strip.png); two or
                                               three names per call stay under the 300 s limit
    $BPY -m engine.redstone palette [golden dusk night]   the dust colour check (renders; about 60 s for two)
    $BPY -m engine.redstone study floor | lamp | held      the light measurements (renders, 40-90 s each)
    $BPY -m tools.check_redstone_stamp         frame fingerprints (two processes; about a minute)
"""
import math
import os

import bpy
import numpy as np
from mathutils import Matrix, Vector

from . import blocks as _blocks
from . import mcassets as mc
from . import props as _props

FPS = 24
TICK = FPS / 20.0                    # film frames per game tick (1.2)

# ---- numbers transcribed from the 26.x client classes ------------------------------------------------------------
PISTON_TICKS = 2                     # PistonMovingBlockEntity.TICKS_TO_EXTEND; tick(): progress += 0.5F per tick
PISTON_STEP = 0.5                    # blocks the head and every moved block travel per tick (progress 0 -> 0.5 -> 1)
PISTON_FRAMES = PISTON_TICKS * TICK  # 2.4 film frames from the start of a move to its end
PISTON_START_TICKS = 0               # PistonBaseBlock.checkIfExtend: level.blockEvent(...) runs in the same tick
SHORT_ARM_UNTIL = 0.5                # PistonHeadRenderer.extractRenderState: the head is drawn with SHORT=true while
                                     # it is 0.5 block or less out of the base (progress <= 0.5 extending, >= 0.5
                                     # retracting), with the long arm beyond
PUSH_LIMIT = 12                      # PistonStructureResolver.MAX_PUSH_DEPTH
PLATFORM_PX = 4                      # PistonBaseBlock.PLATFORM_THICKNESS: the head plate, 4 pixels
REPEATER_TICKS_PER_DELAY = 2         # RepeaterBlock.getDelay: DELAY * 2 (on and off; DiodeBlock.checkTickOnNeighbor)
LAMP_ON_TICKS = 0                    # RedstoneLampBlock.neighborChanged: lit at once (setBlock in the same call)
LAMP_OFF_TICKS = 4                   # ... scheduleTick(pos, this, 4) when it loses power, then tick() turns it off
TORCH_TOGGLE_TICKS = 2               # RedstoneTorchBlock.TOGGLE_DELAY (the torch is an inverter)
WIRE_TICKS = 0                       # RedstoneWireBlock: a whole line updates in the tick its source changes
LEVER_TICKS = 0                      # LeverBlock.pull: setBlock in the tick of the click (no delay)
SWING_REACH = (0.58, 0.22, 1.25)     # MEASURED on engine.players attack(): the hand's far point of the swing is 0.58
                                     # in front of the feet, 0.22 to the right, 1.1-1.35 up (2.5-4 frames after the
                                     # swing starts)
LEVER_SHOW_TICKS = 1                 # the client draws the new lever after the server's block update (LeverBlock
                                     # .useWithoutItem only cycles a copy on the client): about one tick after the click
FALL_DELAY_TICKS = 2                 # FallingBlock.getDelayAfterPlace: an anvil starts falling 2 ticks after its
                                     # support has gone (for whoever drops the anvils: engine/fixtures.py)
LIGHT_LEVEL = {"redstone_lamp": 15, "redstone_torch": 7}     # Blocks: litBlockEmission(15) / litBlockEmission(7)
LIGHT_LEVEL_TORCH = 14               # the wall torch the village is lit with (game value; its lambda not traced here)
# RedstoneWireBlock COLORS (static init): f = power / 15; r = f * 0.6 + (0.4 if f > 0 else 0.3);
# g = clamp(f^2 * 0.7 - 0.5, 0, 1); b = clamp(f^2 * 0.6 - 0.7, 0, 1); ARGB.colorFromFloat -> floor(x * 255)
# (single precision). BlockTintSources$10 multiplies it into tintindex 0 of the dust models.


def _wire_colors():
    out = []
    for i in range(16):
        f = np.float32(i) / np.float32(15.0)
        r = f * np.float32(0.6) + (np.float32(0.4) if f > 0 else np.float32(0.3))
        g = min(max(f * f * np.float32(0.7) - np.float32(0.5), 0.0), 1.0)
        b = min(max(f * f * np.float32(0.6) - np.float32(0.7), 0.0), 1.0)
        out.append(tuple(int(math.floor(np.float32(c) * np.float32(255.0))) for c in (r, g, b)))
    return tuple(out)


WIRE_COLORS = _wire_colors()        # power 0..15 -> (r, g, b) 0..255: 0 = (76, 0, 0), 1 = (112, 0, 0), 15 = (255, 50, 0)

# ---- film choices (NOT the game; each one stated in the docstring) ----------------------------------------------
DUST_GLOW = 0.4                      # emission of lit dust at power 15 (x power / 15): a shader pack's subtle glow
DUST_ALBEDO = 0.35                   # diffuse colour of power-15 dust x this (linear; weaker dust less, see dust_albedo):
DUST_ALBEDO_KNEE = 0.3               # the look's sunlit floor is 1.24 x its texture, the shoulder starts at 0.76 and a
                                     # fully saturated red above it drifts to salmon pink (the look's highlight
                                     # shoulder + sRGB); dust whose tint red is under KNEE (linear) keeps its colour
TORCH_GLOW = (0.8, 0.5, 0.12)        # lit redstone torch texels: (the pale core, the bright red, the rest: the stick);
                                     # pale = HSV value > 0.65 and saturation < 0.6, red = value > 0.65, saturation >= 0.6
TORCH_RED_ALBEDO = 0.55              # diffuse colour of the bright red torch / repeater texels x this (as DUST_ALBEDO)
REPEATER_GLOW = (0.0, 0.8, 0.0)      # lit repeater top (repeater_on): its bright red texels glow, nothing else
LAMP_WATTS = 137.0                   # MEASURED (light_study 'floor', night): the floor 1 / 2 / 3 blocks in front of a lit
                                     # lamp gets 1.11 / 1.10 / 1.17 x what a village torch's gets, the game's ratio of
                                     # light 15 to 14 there 1.11-1.12 (lightmap.fsh); the computed 122 W gave 0.93-0.99
REDSTONE_TORCH_WATTS = 50.0          # MEASURED the same way: 0.33 / 0.30 / 0.29 x the torch at 1 / 2 / 3 blocks, the
                                     # game's light 7 against 14: 0.38 / 0.34 / 0.29 (the computed 37 W gave 0.25 x)
REDSTONE_TORCH_COLOR = (1.0, 0.62, 0.5)   # the game has one block-light colour; a shader pack tints it by the source
LAMP_RADIUS = 0.45                   # soft-shadow radius of the lamp's light (it is a glowing cube, not a flame)
HELD_TORCH_WATTS = 30.0              # the redstone torch in a hand (a little less: it is half a block from a face)
HELD_TORCH_KEY_WATTS = 120.0         # MEASURED (light_study 'held', dusk): a held torch as the KEY on a face facing the
                                     # lens (beat 24): the face x1.78 (30 W: x1.19, 300 W: x2.95)
LAMP_KEY_WATTS = 4.0 * LAMP_WATTS    # MEASURED (light_study 'lamp', golden hour, the face 2.7 blocks off turned to the
                                     # lamp): LAMP_WATTS x1.46 (reads), x4 = 548 W x2.93, x8 x4.03

HORIZONTAL = ("north", "east", "south", "west")
DIRS6 = ("north", "east", "south", "west", "up", "down")
OPPOSITE = {"north": "south", "south": "north", "east": "west", "west": "east", "up": "down", "down": "up"}
VEC = {k: Vector(v) for k, v in mc.DIR_BLENDER.items()}      # Blender unit steps: north = +Y, up = +Z


def _cell(c):
    return tuple(int(math.floor(float(v) + 1e-6)) for v in c)


def _add(c, d, k=1):
    v = VEC[d]
    return (c[0] + int(v.x) * k, c[1] + int(v.y) * k, c[2] + int(v.z) * k)


def at(frame, ticks):
    """The film time `ticks` game ticks after `frame` (1 tick = 1.2 frames; may be fractional)."""
    return float(frame) + float(ticks) * TICK


def frame_of(t):
    """The first whole frame that DRAWS a state that changes at film time t: the frame whose exposure middle
    (f + 0.25, the shutter is open over [f, f + 0.5]) is at or after t."""
    return int(math.ceil(float(t) - 0.25 - 1e-6))


# ----------------------------------------------------------------------------------------------------
# keyframe plumbing
# ----------------------------------------------------------------------------------------------------
def _fcurve(idb, path, index=0):
    """F-curve idb.<path>[index], creating action, slot and curve as needed (Blender 5 layered actions)."""
    ad = idb.animation_data or idb.animation_data_create()
    if ad.action is None:
        ad.action = bpy.data.actions.new(idb.name + "_rs")
    return ad.action.fcurve_ensure_for_datablock(idb, path, index=index)


def _keys(idb, path, frames, values, interp="CONSTANT", index=0):
    """Replace a channel by the given keys (all with one interpolation mode)."""
    fc = _fcurve(idb, path, index)
    kps = fc.keyframe_points
    while len(kps):
        kps.remove(kps[len(kps) - 1], fast=True)
    n = len(frames)
    if n:
        kps.add(n)
        co = np.empty(2 * n, dtype=np.float32)
        co[0::2] = frames
        co[1::2] = values
        kps.foreach_set("co", co)
        for kp in kps:
            kp.interpolation = interp
            kp.handle_left_type = kp.handle_right_type = "VECTOR"
    fc.update()
    return fc


def _at(history, frame, default):
    """Value of a {frame: value} history at `frame` (the latest entry at or before it)."""
    best, out = None, default
    for f, v in history.items():
        if f <= frame + 1e-9 and (best is None or f > best):
            best, out = f, v
    return out


class _Looks:
    """Visibility of a part's alternative models: exactly one look (a list of objects) is rendered at a time,
    chosen per whole frame from a history; plus the Stage's per-shot visibility. Keys are rewritten from the
    whole history every time, so calls can come in any order."""

    def __init__(self, looks, initial):
        self.looks = dict(looks)        # look -> [Object]
        self.initial = initial
        self.hist = {}                  # whole frame -> look
        self.shown = {}                 # whole frame -> bool
        self.extra = []                 # objects that follow the part's shown state only (lights follow `lit`)
        self.rekey()

    def add(self, look, objects):
        self.looks[look] = list(objects)

    def set(self, frame, look):
        self.hist[int(frame)] = look

    def at(self, frame):
        return _at(self.hist, frame, self.initial)

    def show(self, frame, visible=True):
        self.shown[int(frame)] = bool(visible)
        self.rekey()

    def clear(self, frame_start, frame_end):
        for f in [f for f in self.hist if frame_start <= f < frame_end]:
            del self.hist[f]

    def rekey(self):
        frames = sorted(set(self.hist) | set(self.shown))
        times = [(frames[0] if frames else 1) - 1] + frames
        states = [(self.initial, True)] + [(self.at(f), _at(self.shown, f, True)) for f in frames]
        now = bpy.context.scene.frame_current
        cur, shown_now = self.at(now), _at(self.shown, now, True)
        member = {}                     # object -> the looks it belongs to (a piston's base is in two of them)
        for look, obs in self.looks.items():
            for ob in obs:
                member.setdefault(ob.name, (ob, set()))[1].add(look)
        for ob, looks in member.values():
            vals = [0.0 if (shown and c in looks) else 1.0 for c, shown in states]
            for path in ("hide_render", "hide_viewport"):
                _keys(ob, path, times, vals)
            ob.hide_render = ob.hide_viewport = not (shown_now and cur in looks)


class _Track:
    """Location keys of one object rebuilt from its rest location and a list of straight moves
    (t0, t1, delta): value(t) = rest + sum(clamp((t - t0) / (t1 - t0), 0, 1) * delta)."""

    def __init__(self, ob):
        self.ob = ob
        self.rest = Vector(ob.location)
        self.moves = {}                 # key -> (t0, t1, delta)

    def offset(self, t):
        o = Vector((0.0, 0.0, 0.0))
        for t0, t1, d in self.moves.values():
            u = 1.0 if t >= t1 else (0.0 if t <= t0 else (t - t0) / (t1 - t0))
            o += d * u
        return o

    def rekey(self):
        if not self.moves:
            for i in range(3):
                _keys(self.ob, "location", [], [], index=i)
            self.ob.location = self.rest
            return
        times = sorted({t for t0, t1, _d in self.moves.values() for t in (t0, t1)})
        for i in range(3):
            _keys(self.ob, "location", times, [self.rest[i] + self.offset(t)[i] for t in times], "LINEAR", index=i)
        self.ob.location = self.rest + self.offset(bpy.context.scene.frame_current)


# ----------------------------------------------------------------------------------------------------
# materials and models
# ----------------------------------------------------------------------------------------------------
def lightmap(level):
    """The game's brightness 0..1 for a light level (lightmap.fsh at the default Brightness, as engine.sets)."""
    b = max(0.0, min(15.0, float(level))) / 15.0
    f = b / (4.0 - 3.0 * b)
    return f + (1.0 - (1.0 - f) ** 4 - f) * 0.5


def _material(texture, tint=None, shade=None, glow=None, dim=None):
    """The material of a part's face. No glow and no dim: exactly engine.blocks' material for that texture (the set's
    own). glow = (strength, above, base): an emissive copy (mcassets.material). dim = a sky-light brightness 0..1
    multiplied in like a tint (engine.sets' baked sky light), for parts in a dark set."""
    if dim is not None and dim < 0.999:
        t = tint or (255, 255, 255)
        tint = tuple(int(round(c * dim)) for c in t)
    if glow is None:
        return _blocks.block_material(texture, tint, None, None, shade)
    strength, above, base = (tuple(glow) + (None, 0.0))[:3]
    mat = mc.material(texture, tint=tint, emission=strength, emit_above=above, emit_base=base or 0.0, shade=shade)
    mat.cycles.emission_sampling = "NONE"          # the glow is seen; the light comes from the part's point light
    return mat


def _styled(texture, tint=None, shade=None, dim=None, albedo=None, red_albedo=None, glow=None, cull=False):
    """A part's material: engine.blocks' material for the texture (the set's own, tint and dim multiplied in like a
    tint) with the module's film choices on a copy of it:
      albedo       the diffuse colour x this (linear), every texel (dust: DUST_ALBEDO through dust_albedo())
      red_albedo   the diffuse colour of the bright saturated texels only (value > 0.65, saturation >= 0.6) x this
      glow         (pale, red, rest): emission (the texel's own colour) of the bright pale texels (value > 0.65,
                   saturation < 0.6: the torch's core), the bright red texels, and every other texel
      cull         back faces transparent: the game draws blocks with back-face culling (RenderPipelines: the
                   terrain pipelines keep the default cull), which the lit torch's inward-facing halo relies on
    The emission is seen, not sampled as a light (the part's point light lights the scene)."""
    if dim is not None and dim < 0.999:
        t = tint or (255, 255, 255)
        tint = tuple(int(round(c * dim)) for c in t)
    base = _blocks.block_material(texture, tint, None, None, shade)
    return _restyle(base, albedo, red_albedo, glow, cull)


def _restyle(base, albedo=None, red_albedo=None, glow=None, cull=False):
    """A copy of a Principled game-texture material with _styled()'s film choices (cached by name)."""
    if albedo is None and red_albedo is None and glow is None and not cull:
        return base
    key = "|rs%s%s%s%s" % ("a%.3g" % albedo if albedo is not None else "",
                           "r%.3g" % red_albedo if red_albedo is not None else "",
                           "g%.3g,%.3g,%.3g" % tuple(glow) if glow is not None else "", "c" if cull else "")
    name = base.name + key
    if len(name) > 63:
        import hashlib

        name = base.name[:44] + "|" + hashlib.md5((base.name + key).encode()).hexdigest()[:12]
    mat = bpy.data.materials.get(name)
    if mat is not None:
        return mat
    nt0 = base.node_tree
    if nt0 is None or not any(n.type == "BSDF_PRINCIPLED" for n in nt0.nodes):
        return base                                  # (an 'up_thin' two-sided material: never a redstone part)
    mat = base.copy()
    mat.name = name
    nt = mat.node_tree
    N, L = nt.nodes.new, nt.links.new
    tex = next(n for n in nt.nodes if n.type == "TEX_IMAGE")
    bsdf = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
    outn = next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL")

    def math(op, a, b):
        n = N("ShaderNodeMath")
        n.operation = op
        for i, v in enumerate((a, b)):
            if isinstance(v, (int, float)):
                n.inputs[i].default_value = float(v)
            else:
                L(v, n.inputs[i])
        return n.outputs[0]

    hsv = N("ShaderNodeSeparateColor")
    hsv.mode = "HSV"
    L(tex.outputs["Color"], hsv.inputs[0])
    bright = math("GREATER_THAN", hsv.outputs[2], 0.65)
    satur = math("GREATER_THAN", hsv.outputs[1], 0.5999)
    red = math("MULTIPLY", bright, satur)
    pale = math("MULTIPLY", bright, math("SUBTRACT", 1.0, satur))
    if albedo is not None or red_albedo is not None:
        fac = float(albedo if albedo is not None else 1.0)
        if red_albedo is not None:
            fac = math("MULTIPLY", math("ADD", math("MULTIPLY", red, float(red_albedo) - 1.0), 1.0), fac)
        sc = N("ShaderNodeVectorMath")
        sc.operation = "SCALE"
        L(tex.outputs["Color"], sc.inputs[0])
        if isinstance(fac, float):
            sc.inputs["Scale"].default_value = fac
        else:
            L(fac, sc.inputs["Scale"])
        L(sc.outputs["Vector"], bsdf.inputs["Base Color"])
    if glow is not None:
        g_pale, g_red, g_rest = (float(v) for v in glow)
        strength = math("ADD", math("ADD", math("MULTIPLY", red, g_red - g_rest), math("MULTIPLY", pale,
                                                                                         g_pale - g_rest)), g_rest)
        L(tex.outputs["Color"], bsdf.inputs["Emission Color"])
        L(strength, bsdf.inputs["Emission Strength"])
        mat.cycles.emission_sampling = "NONE"
    if cull:
        link = outn.inputs["Surface"].links[0]
        src = link.from_socket
        nt.links.remove(link)
        geo = N("ShaderNodeNewGeometry")
        clear = N("ShaderNodeBsdfTransparent")
        mix = N("ShaderNodeMixShader")
        L(geo.outputs["Backfacing"], mix.inputs[0])
        L(src, mix.inputs[1])
        L(clear.outputs[0], mix.inputs[2])
        L(mix.outputs[0], outn.inputs["Surface"])
    mat["mc_redstone_style"] = key
    return mat


DUST_HUE_REF = 0.6                   # the linear brightness at which dust_tint() matches the displayed hue (it varies
                                     # by under 1 degree over 0.3 .. 0.9)


def _linear_to_srgb(c):
    c = max(0.0, float(c))
    return c * 12.92 if c <= 0.0031308 else 1.055 * c ** (1.0 / 2.4) - 0.055


def _grade_saturation():
    """The saturation of the look's grade (engine.look GRADES 'warm' / 'cool': 0.97)."""
    from . import look

    return float(min(g["saturation"] for k, g in look.GRADES.items() if k in ("warm", "cool")))


def dust_tint(level):
    """The colour (0..255) dust of a power level is drawn with: the game's (wire_color) with its green raised so that,
    after the look's grade, the DISPLAYED hue is the game's. The grade's saturation step (0.97, in linear HSV: the
    smallest channel of every colour rises to 3 % of the largest) lifts the blue of power-15 dust from 12 to 44 in
    sRGB and turned its hue from the game's 11.8 degrees to a crimson 5.7 (measured: palette_check). Dust whose game
    colour has no green (power 12 and below) is unchanged; red stays the game's."""
    r0, g0, _b0 = wire_color(level)
    if g0 <= 0:
        return wire_color(level)
    s = _grade_saturation()
    hue = g0 / float(r0)                                   # the game's sRGB hue ratio (g - b) / (r - b), b = 0
    v = DUST_HUE_REF
    b2 = _linear_to_srgb((1.0 - s) * v)                    # the displayed blue after the grade
    r2 = _linear_to_srgb(v)
    g2 = b2 + hue * (r2 - b2)                              # the displayed green the game's hue needs
    g_lin = (_srgb_to_linear(g2) - (1.0 - s) * v) / s      # ... before the grade
    x = max(0.0, g_lin / v)                                # green / red in linear light
    g = _linear_to_srgb(x * _srgb_to_linear(r0 / 255.0)) * 255.0
    return (r0, int(round(min(255.0, g))), 0)


def dust_albedo(level):
    """The factor on the diffuse colour of dust at a power level: the linear red of the game's colour is kept up to
    DUST_ALBEDO_KNEE and compressed linearly above it, down to DUST_ALBEDO x at power 15 (so the diffuse red it
    leaves still rises with the power; see DUST_ALBEDO)."""
    r = _srgb_to_linear(wire_color(level)[0] / 255.0)
    r15 = _srgb_to_linear(wire_color(15)[0] / 255.0)
    top = max(DUST_ALBEDO * r15, DUST_ALBEDO_KNEE)
    if r <= DUST_ALBEDO_KNEE or r15 <= DUST_ALBEDO_KNEE:
        return 1.0
    return (DUST_ALBEDO_KNEE + (r - DUST_ALBEDO_KNEE) * (top - DUST_ALBEDO_KNEE) / (r15 - DUST_ALBEDO_KNEE)) / r


def _srgb_to_linear(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def _quads(block_id, props):
    """Every baked Quad of a block state (the game's models, blockstate rotations, uvlock)."""
    return mc.bake_block(block_id, props, 0)


def _object(kit, name, quads, mat_for, location, collection=None):
    """One mesh object from baked quads; origin = the min corner of the cell the quads were baked for."""
    base, k = name, 1
    while bpy.data.objects.get(name) is not None:
        k += 1
        name = "%s_%d" % (base, k)
    ob = mc.quads_object(name, quads, mat_for, collection or kit.collection, origin=(0.0, 0.0, 16.0))
    ob.location = Vector(location)
    ob["mc_redstone"] = base
    return ob


def _plain(block_id, dim=None, style_for=None):
    """quad -> material as engine.blocks gives it (tint by the block's tintindex), dimmed on request; style_for(q)
    -> None or the film-choice keywords of _styled() for that quad (a styled quad is never dimmed: it glows)."""
    def f(q):
        st = style_for(q) if style_for else None
        tint = mc.block_tint(block_id, q.tintindex)
        if st:
            return _styled(q.texture, tint, getattr(q, "shade", None), **st)
        return _material(q.texture, tint, getattr(q, "shade", None), None, dim)
    return f


def _lit_style(q):
    """The film choices of a LIT torch or repeater face (None: the face is drawn as the set draws it)."""
    if q.texture == "block/redstone_torch":
        return dict(red_albedo=TORCH_RED_ALBEDO, glow=TORCH_GLOW, cull=True)
    if q.texture == "block/repeater_on":
        return dict(red_albedo=TORCH_RED_ALBEDO, glow=REPEATER_GLOW)
    return None


# ----------------------------------------------------------------------------------------------------
# the kit: one per set (Village or World), holds the parts and answers "what is in this cell"
# ----------------------------------------------------------------------------------------------------
class RedstoneError(ValueError):
    """A request the game would not carry out (13 blocks pushed, a cell taken, a piston extended twice ...)."""


def kit(where, collection=None, sky_light=None):
    """The redstone kit of a set: where = the Village (or a blocks.World). The same kit comes back for the same set.
    collection: where the parts go (default: a collection 'redstone' in the scene). sky_light = default sky light
    level (0..15) baked into the colours of every part (None: none; for parts in a dark set, see engine.sets)."""
    k = getattr(where, "_redstone_kit", None)
    if k is not None and k._alive():
        if sky_light is not None:
            k.sky_light = sky_light
        return k
    k = Kit(where, collection, sky_light)
    try:
        where._redstone_kit = k
    except AttributeError:
        pass
    return k


class Kit:
    """The parts of one set. Build parts with its methods (see the module docstring)."""

    def __init__(self, where, collection=None, sky_light=None):
        self.where = where
        self.world = getattr(where, "world", where) if where is not None else None
        if collection is None:
            collection = _blocks.new_collection(bpy.context.scene, "redstone")
        self.collection = collection
        self.sky_light = sky_light
        self.parts = []                 # every part, in creation order
        self.static = {}                # cell -> part that sits there (lever, torch, repeater, lamp, piston base, wire)
        self.movables = []              # _Movable blocks (moved by pistons)
        self.tracks = {}                # object name -> _Track
        self.rides = []                 # (thing, on, frame_start, frame_end)

    def _alive(self):
        try:
            return bool(self.collection.name) and self.collection.name in bpy.data.collections
        except ReferenceError:
            return False

    def _dim(self, sky_light, cell=None):
        """The brightness a part is drawn with for a sky-light level, EXACTLY as engine.sets draws a World cell at
        that level (sets.lightmap of Environment._step: levels below 11 in pairs, nothing under LIGHT_FLOOR = 3,
        the Environment's Brightness gamma), so a part and the baked wall beside it get the same factor.
        sky_light="auto": the set's own baked level (the brightest empty cell beside the part's cell; 15 where the
        set has no Environment). None: no dimming."""
        level = self.sky_light if sky_light is None else sky_light
        if level is None:
            return None
        from . import sets

        env = getattr(self.world, "sets_environment", None)
        if level == "auto":
            level = self.auto_level(cell) if cell is not None else 15
        gamma = getattr(env, "gamma", sets.LIGHT_GAMMA)
        f = sets.lightmap(sets.Environment._step(int(round(float(level)))), gamma)
        return None if f >= 0.999 else f

    def auto_level(self, cell):
        """The sky light engine.sets baked around a cell: the brightest of the cell and its six neighbours that are
        not full blocks in the World (a part's visible faces look into them); 15 where nothing was baked."""
        env = getattr(self.world, "sets_environment", None)
        if env is None or cell is None:
            return 15
        c = _cell(cell)
        if c not in env.light:                      # lit (15) or never baked: as the World draws it there
            return 15
        best = env.light[c]
        for d in DIRS6:                             # a cell that was solid at the bake has no entry: not counted
            n = _add(c, d)
            if n in env.light and not (self.world is not None and self.world.is_full_cube(*n)):
                best = max(best, env.light[n])
        return best

    # ---- what is where ----------------------------------------------------------------------------------
    def world_block(self, cell):
        """(block_id, props) the set's World holds at a cell (None: air)."""
        if self.world is None or not hasattr(self.world, "get"):
            return None
        return self.world.get(*cell)

    def movable_at(self, cell, t):
        """The kit's movable block in `cell` at film time t (None)."""
        for m in self.movables:
            if m.there(t) and m.cell_at(t) == tuple(cell):
                return m
        return None

    def occupied(self, cell, t, ignore=()):
        """What fills a cell at time t: 'world', a part, a movable, or None."""
        if self.world_block(cell) is not None:
            return "world"
        p = self.static.get(tuple(cell))
        if p is not None and p not in ignore:
            return p
        m = self.movable_at(cell, t)
        if m is not None and m not in ignore:
            return m
        return None

    def _claim(self, cell, part, allow_world=False):
        cell = _cell(cell)
        if not allow_world and self.world_block(cell) is not None:
            raise RedstoneError("redstone: cell %s holds %s in the set's World: leave it empty in the hook "
                                "(redstone.carve(b, cells)), the part is drawn as its own object"
                                % (cell, self.world_block(cell)[0]))
        other = self.static.get(cell)
        if other is not None and other is not part:
            raise RedstoneError("redstone: cell %s is taken by %s" % (cell, other))
        self.static[cell] = part
        return cell

    def track(self, ob):
        t = self.tracks.get(ob.name)
        if t is None:
            t = self.tracks[ob.name] = _Track(ob)
        return t

    def unique_name(self, base):
        """`base`, or base_2, base_3 ... when a part of this kit already has that name (Stage keys st.cast by
        name: two parts with one name would leave one of them unmanaged at the cuts)."""
        names = getattr(self, "_names", None)
        if names is None:
            names = self._names = set()
        name, k = base, 1
        while name in names:
            k += 1
            name = "%s_%d" % (base, k)
        names.add(name)
        return name

    # ---- parts ------------------------------------------------------------------------------------------
    def block(self, block_id, cell, props=None, frame=None, name=None, sky_light=None):
        """A movable block of its own (engine.breaking.place_block: a Breakable) that pistons push and pull."""
        from . import breaking

        cell = _cell(cell)
        if self.world_block(cell) is not None:
            raise RedstoneError("redstone.block: cell %s holds %s in the set's World: carve it in the hook"
                                % (cell, self.world_block(cell)[0]))
        b = breaking.place_block(self.collection, block_id, cell, props, world=self.world, name=name, frame=frame)
        dim = self._dim(sky_light, cell)
        if dim is not None:
            me = b.object.data = b.object.data.copy()
            for i, m in enumerate(list(me.materials)):
                tex = m.get("mc_texture")
                if tex:
                    me.materials[i] = _material(tex, None, m.get("mc_shade"), None, dim)
        m = _Movable(self, b, cell)
        self.movables.append(m)
        return m

    def lever(self, cell, face="floor", facing="north", powered=False, name=None, sky_light=None):
        """A lever (face floor / wall / ceiling; facing as the game's: for a wall lever the side it sticks out to)."""
        return Lever(self, cell, face, facing, powered, name, sky_light)

    def piston(self, cell, facing="north", sticky=False, extended=False, name=None, sky_light=None):
        """A piston / sticky piston in any of the six facings (the side its head comes out of)."""
        return Piston(self, cell, facing, sticky, extended, name, sky_light)

    def wire(self, cells, power=0, dots=(), source=None, name=None, sky_light=None):
        """A line of redstone dust over `cells` (each the cell the dust lies IN, on top of the block below)."""
        return Wire(self, cells, power, dots, source, name, sky_light)

    def repeater(self, cell, toward="north", delay=1, powered=False, name=None, sky_light=None):
        """A repeater whose signal travels `toward` (the game's FACING is the opposite side: its input)."""
        return Repeater(self, cell, toward, delay, powered, name, sky_light)

    def lamp(self, cell, lit=False, name=None, sky_light=None, watts=None):
        """A redstone lamp (off / on); on = its own point light (LAMP_WATTS)."""
        return Lamp(self, cell, lit, name, sky_light, watts)

    def torch(self, cell, wall=None, lit=True, frame=None, name=None, sky_light=None, watts=None):
        """A redstone torch standing in `cell` (wall=None) or on a wall (wall = the side it leans out to, the
        game's FACING of redstone_wall_torch); frame = the frame it appears on (None: there from the start)."""
        return Torch(self, cell, wall, lit, frame, name, sky_light, watts)

    def piston_door(self, cells, side, block="stone", closed=True, name="piston_door", sky_light=None):
        """A door of blocks pulled sideways into a wall by sticky pistons (one per door cell): see PistonDoor."""
        return PistonDoor(self, cells, side, block, closed, name, sky_light)

    def piston_row(self, cells, facing, carry="oak_planks", extended=True, sticky=True, name="piston_row",
                   sky_light=None):
        """Pistons in a row, each carrying one block on its arm: see PistonRow."""
        return PistonRow(self, cells, facing, carry, extended, sticky, name, sky_light)

    def ride(self, thing, on, frame_start=None, frame_end=None):
        """`thing` (a movable block, a Breakable, an Object, a Character) moves with the movable block `on` for
        every move of `on` that starts in [frame_start, frame_end). NOT the game for blocks (an anvil on a plank
        that is pushed away falls) nor for anything on a sideways push (entities ride only an upward push)."""
        self.rides.append((thing, on, frame_start, frame_end))
        on.riders_changed()

    def extend_all(self, pistons, frame):
        """Every piston extends on `frame` (one tick), each pushing what is in front of it. Returns the end time."""
        return max([p.extend(frame) for p in pistons] or [float(frame)])

    def retract_all(self, pistons, frame):
        """Every piston retracts on `frame`, the sticky ones pulling their blocks. Returns the end time."""
        return max([p.retract(frame) for p in pistons] or [float(frame)])

    def show(self, frame, visible=True):
        """Per-shot visibility of every part of the kit."""
        for p in self.parts:
            p.show(frame, visible)
        for m in self.movables:
            m.show(frame, visible)

    # ---- the dust's view of the world (RedstoneWireBlock.getConnectingSide) -----------------------------------
    def _is_wire(self, cell):
        p = self.static.get(tuple(cell))
        return isinstance(p, Wire)

    def _conductor(self, cell):
        """isRedstoneConductor: an opaque full cube (stone, planks, lamps, pistons are; glass, slabs, parts are not)."""
        p = self.static.get(tuple(cell))
        if p is not None:
            return isinstance(p, Lamp)          # pistons, levers, torches, repeaters, dust: never conductors
        if self.movable_at(cell, 0.0) is not None:
            return self.movable_at(cell, 0.0).full_cube
        w = self.world
        return bool(w is not None and hasattr(w, "is_full_cube") and w.is_full_cube(*cell))

    def _sturdy(self, cell, face):
        """isFaceSturdy: the face of the block in `cell` covers the whole side (full cubes; a slab's flat side)."""
        if self._conductor(cell):
            return True
        p = self.static.get(tuple(cell))
        if isinstance(p, Piston) and not p.extended0 and p.cell == tuple(cell):
            return True                         # a retracted piston is a full cube (not a conductor)
        st = self.world_block(cell)
        if st is None:
            return False
        bid, props = st
        if bid.endswith("_slab"):
            t = props.get("type", "bottom")
            return t == "double" or (face == "up" and t == "top") or (face == "down" and t == "bottom")
        return False

    def _connects(self, cell, direction):
        """shouldRedstoneWireConnectTo of what is in `cell`, seen from a wire `direction` away (None: above/below)."""
        p = self.static.get(tuple(cell))
        if isinstance(p, Wire):
            return True
        if isinstance(p, Repeater):
            return direction is not None and direction in (p.facing, OPPOSITE[p.facing])
        if isinstance(p, (Lever, Torch)):
            return direction is not None
        m = self.movable_at(cell, 0.0)
        if m is not None and m.block_id == "redstone_block":
            return direction is not None
        st = self.world_block(cell)
        if st is not None and st[0] in ("redstone_block", "lever", "redstone_torch", "redstone_wall_torch"):
            return direction is not None
        return False

    def _side(self, cell, d, climb):
        """RedstoneWireBlock.getConnectingSide(level, pos, dir, canClimbUp) -> 'up' | 'side' | 'none'."""
        n = _add(cell, d)
        if climb and self._sturdy(n, "up") and self._connects(_add(n, "up"), None):
            return "up" if self._sturdy(n, OPPOSITE[d]) else "side"
        if self._connects(n, d) or (not self._conductor(n) and self._connects(_add(n, "down"), None)):
            return "side"
        return "none"

    def wire_state(self, cell, dot=False):
        """The connections the game gives a dust in `cell` (getConnectionState after getMissingConnections):
        {'north': 'side' | 'up' | 'none', ...}. An unconnected dust is a cross, or a dot when dot=True (the
        player's right click); a dust with connections on one axis only runs across the whole block."""
        climb = not self._conductor(_add(cell, "up"))
        s = {d: self._side(cell, d, climb) for d in HORIZONTAL}
        if all(v == "none" for v in s.values()) and dot:
            return s
        n, e, so, w = (s[d] != "none" for d in HORIZONTAL)
        ns_not, ew_not = not n and not so, not e and not w
        if not w and ns_not:
            s["west"] = "side"
        if not e and ns_not:
            s["east"] = "side"
        if not n and ew_not:
            s["north"] = "side"
        if not so and ew_not:
            s["south"] = "side"
        return s


class _Part:
    """Common to every part: name, cell, looks, show()."""

    kind = "part"

    def __init__(self, kit_, cell, name):
        self.kit = kit_
        self.cell = _cell(cell)
        base = name or "%s_%d_%d_%d" % (self.kind, self.cell[0], self.cell[1], self.cell[2])
        self.name = kit_.unique_name(base)
        self.looks = None
        self.lights = []
        kit_.parts.append(self)

    def __repr__(self):
        return "<redstone.%s %s at %s>" % (type(self).__name__, self.name, self.cell)

    def show(self, frame, visible=True):
        """Per-shot visibility (films.lookdev.Stage.finish calls it for everything in st.cast)."""
        if self.looks is not None:
            self.looks.show(frame, visible)
        self._rekey_lights()

    def _rekey_lights(self):
        pass

    @property
    def objects(self):
        out = []
        if self.looks is not None:
            for obs in self.looks.looks.values():
                out.extend(obs)
        return out + list(self.lights)

    @property
    def center(self):
        return Vector((self.cell[0] + 0.5, self.cell[1] + 0.5, self.cell[2] + 0.5))


class _Movable:
    """A block that pistons move: a Breakable (engine.breaking.place_block) with the kit's move record."""

    def __init__(self, kit_, breakable, cell):
        self.kit, self.breakable, self.cell0 = kit_, breakable, tuple(cell)
        self.block_id = breakable.block_id
        self.full_cube = bool(getattr(breakable, "full_cube", True))
        self.name = breakable.name
        self.object = breakable.object
        self.moves = {}                 # t0 -> (t1, step direction)

    def __repr__(self):
        return "<redstone block %s at %s>" % (self.block_id, self.cell0)

    def there(self, t):
        return self.breakable.there_at(t) if hasattr(self.breakable, "there_at") else True

    def cell_at(self, t):
        """The cell the block is in (or moving into) at film time t."""
        c = self.cell0
        for t0, (t1, d) in sorted(self.moves.items()):
            if t0 <= t + 1e-9:
                c = _add(c, d)
        return c

    def move(self, t0, d):
        self.moves[float(t0)] = (float(t0) + PISTON_FRAMES, d)
        self._rekey()

    def unmove(self, t0):
        self.moves.pop(float(t0), None)
        self._rekey()

    def riders_changed(self):
        self._rekey()

    def _rekey(self):
        tr = self.kit.track(self.object)
        tr.moves = {("self", t0): (t0, t1, VEC[d].copy()) for t0, (t1, d) in self.moves.items()}
        tr.rekey()
        for thing, on, fs, fe in self.kit.rides:
            if on is self:
                _ride_rekey(self.kit, thing, self, fs, fe)

    def show(self, frame, visible=True):
        """Per-shot visibility (the Breakable's)."""
        self.breakable.show(frame, visible)

    @property
    def objects(self):
        """[the block's object] (for Stage.hero)."""
        return [self.object]

    @property
    def center(self):
        return Vector(self.object.location) + Vector((0.5, 0.5, 0.5))


def _thing_object(thing):
    """The Object that carries a thing's position: a movable / Breakable's .object, a Character's .root, an Object."""
    if isinstance(thing, _Movable):
        return thing.object, False
    if hasattr(thing, "root") and hasattr(thing, "head"):
        return thing.root, True
    if hasattr(thing, "object") and isinstance(getattr(thing, "object"), bpy.types.Object):
        return thing.object, False
    return thing, False


def _ride_rekey(kit_, thing, on, fs, fe):
    """Give a rider the moves of the block it stands on (only those starting in [fs, fe))."""
    ob, character = _thing_object(thing)
    moves = [(t0, t1, VEC[d].copy()) for t0, (t1, d) in on.moves.items()
             if (fs is None or t0 >= fs) and (fe is None or t0 < fe)]
    if not character:
        tr = kit_.track(ob)
        for k in [k for k in tr.moves if k[0] == ("ride", on.name)]:
            del tr.moves[k]
        for t0, t1, d in moves:
            tr.moves[(("ride", on.name), t0)] = (t0, t1, d)
        tr.rekey()
        return
    done = ob.get("_rs_ridden", [])
    for t0, t1, d in moves:
        key = "%s@%.3f" % (on.name, t0)
        if key in done:
            continue
        _shift_character(ob, t0, t1, d)
        done = list(done) + [key]
    ob["_rs_ridden"] = done


def _shift_character(root, t0, t1, d):
    """A character's root carried by delta d over [t0, t1]: every location key after t0 moves by d, and two keys
    make the carry itself (a character keyed later than this call is not carried: ride after keying him)."""
    for i in range(3):
        if abs(d[i]) < 1e-9:
            continue
        fc = _fcurve(root, "location", i)
        v0 = fc.evaluate(t0) if len(fc.keyframe_points) else root.location[i]
        v1 = (fc.evaluate(t1) if len(fc.keyframe_points) else root.location[i]) + d[i]
        for kp in fc.keyframe_points:
            if kp.co.x > t0 + 1e-6:
                kp.co.y += d[i]
                kp.handle_left.y += d[i]
                kp.handle_right.y += d[i]
        for t, v in ((t0, v0), (t1, v1)):
            kp = fc.keyframe_points.insert(t, v)
            kp.interpolation = "LINEAR"
        fc.update()


# ----------------------------------------------------------------------------------------------------
# lever
# ----------------------------------------------------------------------------------------------------
class Lever(_Part):
    """A lever (LeverBlock): the cobblestone base and the handle, which the game swaps between two models (no
    in-between frames). flip / set; hand_point() is where a hand must reach, stand() where to stand."""

    kind = "lever"

    def __init__(self, kit_, cell, face="floor", facing="north", powered=False, name=None, sky_light=None):
        super().__init__(kit_, cell, name)
        if face not in ("floor", "wall", "ceiling") or facing not in HORIZONTAL:
            raise RedstoneError("lever: face floor | wall | ceiling, facing north | east | south | west")
        kit_._claim(self.cell, self)
        self.face, self.facing, self.powered0 = face, facing, bool(powered)
        self.hist = {}                  # frame -> (powered, ease frames)
        dim = kit_._dim(sky_light, self.cell)
        props = {"face": face, "facing": facing, "powered": "true"}
        part = mc.resolve_blockstate("lever", props)[0]          # powered=true: model block/lever (handle at -45)
        self.part = part
        quads = mc.bake_part(part)
        base_q = [q for q in quads if q.texture != "block/lever"]
        hand_q = [q for q in quads if q.texture == "block/lever"]
        mat = _plain("lever", dim)
        self.base = _object(kit_, self.name + "_base", base_q, mat, self.cell)
        # the handle pivots on the model point (8, 1, 8) about the model's X axis (lever.json element rotation),
        # carried through the blockstate rotation: build it around that point
        piv_m = mc.rotate_point((8.0, 1.0, 8.0), part.x, part.y)
        ax_m = Vector(mc.rotate_point((16.0, 1.0, 8.0), part.x, part.y)) - Vector(piv_m)
        piv_b = Vector(mc.to_blender(piv_m))
        ax_b = Vector((ax_m[0], -ax_m[2], ax_m[1])).normalized()
        shifted = []
        for q in hand_q:
            pts = [(p[0] - piv_m[0], p[1] - piv_m[1], p[2] - piv_m[2] + 16.0) for p in q.pts]
            shifted.append(mc.Quad(pts, q.uvs, q.texture, q.tintindex, q.overlay, None, None, q.thin,
                                   getattr(q, "shade", None)))
        self.handle = _object(kit_, self.name + "_handle", shifted, mat, Vector(self.cell) + piv_b)
        self.handle.rotation_mode = "AXIS_ANGLE"
        self.pivot = Vector(self.cell) + piv_b
        self.axis = ax_b
        # which way +90 degrees turns the 'lever' handle into the 'lever_on' handle (checked against the bake)
        off = mc.bake_part(mc.resolve_blockstate("lever", dict(props, powered="false"))[0])
        want = np.mean([mc.to_blender(p) for q in off if q.texture == "block/lever" for p in q.pts], axis=0)
        here = np.mean([mc.to_blender(p) for q in hand_q for p in q.pts], axis=0)
        best = None
        for sign in (1.0, -1.0):
            R = Matrix.Rotation(sign * math.pi / 2, 3, ax_b)
            got = R @ (Vector(here) - piv_b) + piv_b
            err = (got - Vector(want)).length
            if best is None or err < best[0]:
                best = (err, sign)
        self.off_angle = best[1] * math.pi / 2       # handle angle of the UNPOWERED model
        self.check_error = best[0]
        pts = sorted((Vector(mc.to_blender(p)) - piv_b for q in hand_q for p in q.pts), key=lambda v: -v.length)
        self.tip = sum(pts[:4], Vector()) / 4.0      # pivot -> the middle of the handle's top face (powered model)
        self._rekey()

    def angle(self, powered):
        return 0.0 if powered else self.off_angle

    def state_at(self, frame):
        """Powered at `frame` (the state drawn on that frame)."""
        return bool(_at({f: v[0] for f, v in self.hist.items()}, frame, self.powered0))

    def set(self, frame, powered, ease=0):
        """The lever is in state `powered` from `frame` on. ease=0: the game's model swap; ease=2: the handle swings
        over 2 frames ending ON frame (a film ease). Returns frame (LEVER_TICKS = 0: what it drives changes now)."""
        self.hist[int(round(frame))] = (bool(powered), int(ease))
        self._rekey()
        return float(frame)

    def flip(self, frame, ease=0):
        """Toggle on `frame` (see set). Returns frame."""
        return self.set(frame, not self.state_at(frame - 1), ease)

    def power(self, t):
        """(chain helper) a lever is a source: switches on at t. Returns t."""
        return self.set(frame_of(t), True)

    def unpower(self, t):
        return self.set(frame_of(t), False)

    def _rekey(self):
        frames = sorted(self.hist)
        times, vals = [], []
        cur = self.angle(self.powered0)
        times.append(float((frames[0] if frames else 1) - 1))
        vals.append(cur)
        for f in frames:
            on, ease = self.hist[f]
            a = self.angle(on)
            if ease > 0:
                times.append(float(f - ease))
                vals.append(cur)
            else:
                times.append(float(f) - 0.25)     # a step keyed inside (f - 0.5, f]: drawn from frame f, no smear
                vals.append(cur)
            times.append(float(f))
            vals.append(a)
            cur = a
        fc = _keys(self.handle, "rotation_axis_angle", times, vals, "LINEAR", index=0)
        for i in range(3):
            _keys(self.handle, "rotation_axis_angle", [times[0]], [self.axis[i]], "CONSTANT", index=i + 1)
        self.handle.rotation_axis_angle = (fc.evaluate(bpy.context.scene.frame_current),) + tuple(self.axis)

    def hand_point(self, frame=None, along=0.8):
        """World point on the handle `along` of the way from its pivot to its tip (1.0 = the tip) at `frame`
        (default: the current state): where a hand that flips it must be."""
        on = self.state_at(frame if frame is not None else bpy.context.scene.frame_current)
        v = Matrix.Rotation(self.angle(on), 3, self.axis) @ (self.tip * along)
        return self.pivot + v

    def stand(self, distance=SWING_REACH[0], side=None, lateral=SWING_REACH[1], along=0.5):
        """((x, y, z), yaw) where a player stands so that his right hand, at the far end of an arm swing
        (engine.players attack: SWING_REACH, measured), is at hand_point(along=along): `distance` blocks in front
        of the lever (wall lever: on the side it sticks out to; floor / ceiling: side=, default its facing),
        turned to it, the lever `lateral` blocks to his right. z = the top of the solid block under that spot
        (searched from the lever's height down). The swing passes 1.1-1.35 above his feet: a wall lever in the
        block above the floor (handle 1.15-1.85 high) meets it; anything else is a near miss (as in the game,
        where the hand never touches the lever)."""
        front = side or self.facing
        f = VEC[front]
        hp = self.hand_point(None, along)
        yaw = math.atan2(-f.x, f.y)                     # facing back toward the lever (-Y at yaw 0)
        look = Vector((-f.x, -f.y, 0.0))
        right = Vector((look.y, -look.x, 0.0))
        p = Vector((hp.x, hp.y, 0.0)) + Vector((f.x, f.y, 0.0)) * distance - right * lateral
        z = self._floor(p)
        return (p.x, p.y, z), yaw

    def _floor(self, p):
        w = self.kit.world
        x, y = int(math.floor(p.x)), int(math.floor(p.y))
        z0 = self.cell[2] + (1 if self.face == "ceiling" else 0)
        if w is not None and hasattr(w, "is_solid"):
            for z in range(z0, z0 - 8, -1):
                if w.is_solid(x, y, z):
                    st = w.get(x, y, z)
                    if st and st[0].endswith("_slab") and st[1].get("type", "bottom") == "bottom":
                        return z + 0.5
                    if st and st[0] in ("dirt_path", "farmland"):
                        return z + 15.0 / 16.0
                    return float(z + 1)
        return float(self.cell[2])

    @property
    def objects(self):
        return [self.base, self.handle]

    def show(self, frame, visible=True):
        for ob in (self.base, self.handle):
            _vis_key(ob, frame, visible)


def _vis_key(ob, frame, visible):
    """One CONSTANT visibility key (render and viewport) on an object."""
    for path in ("hide_render", "hide_viewport"):
        setattr(ob, path, not visible)
        ob.keyframe_insert(path, frame=int(frame))
        fc = _fcurve(ob, path)
        for kp in fc.keyframe_points:
            kp.interpolation = "CONSTANT"


def _part_matrix(part):
    """The blockstate rotation of a ModelPart as a 3x3 matrix in Blender axes (acting on directions)."""
    o = Vector(mc.to_blender(mc.rotate_point((8.0, 8.0, 8.0), part.x, part.y)))
    cols = []
    for p in ((24.0, 8.0, 8.0), (8.0, 8.0, -8.0), (8.0, 24.0, 8.0)):      # Blender +X, +Y (MC -z), +Z (MC +y)
        cols.append(Vector(mc.to_blender(mc.rotate_point(p, part.x, part.y))) - o)
    return Matrix((cols[0], cols[1], cols[2])).transposed()


REACH_LIMIT = math.radians(40.0)     # flip_by(reach=True): the most the film reach raises the arm


def _root_fcurves(ob):
    ad = ob.animation_data
    if ad is None or ad.action is None:
        return []
    fcs = getattr(ad.action, "fcurves", None)
    if fcs is not None:
        return list(fcs)
    out = []
    for layer in getattr(ad.action, "layers", []):
        for strip in layer.strips:
            for bag in getattr(strip, "channelbags", []):
                out.extend(bag.fcurves)
    return out


def flip_by(player, lever, frame, sync="game", look=True, ease=0, look_from=None, reach=False):
    """A player flips a lever: his arm swing (engine.players attack) starts ON `frame` (the click) and the lever
    changes LEVER_SHOW_TICKS later (sync="game": the frame after), or on the frame his hand is nearest the handle
    (sync="hand": a film choice that reads in a close-up). look=True turns his head to the handle over the frames
    before the click: from look_from (default: 6 frames before, but never before his last place(): no pre-roll
    into the shot before; a click on the very frame he is placed gets no turn: place him looking at it).
    reach=True (a film choice): his arm is lifted during the swing (delta_rotation_euler of the right arm, at most
    REACH_LIMIT) so his hand passes through the middle of the handle on the frame it is nearest; the plain swing
    passes up to 0.42 block below a wall lever in the block above the floor. Call after his place() / walk.
    Returns the frame the lever changes on."""
    hp = lever.hand_point(frame - 1, 0.5)
    if look:
        start = frame - 6 if look_from is None else int(look_from)
        if look_from is None:
            cut = _last_cut_any(player, frame)
            if cut is not None:
                start = max(start, cut)
        if frame - start >= 1:
            player.look_at(start, hp, ease=frame - start)
    player.attack(frame)
    best = None
    for f in range(int(frame), int(frame) + 10):
        d = (Vector(player.item_point("right", f)) - hp).length
        if best is None or d < best[0]:
            best = (d, f)
    lever.reach_info = dict(natural=best[0], frame=best[1], reached=None, angle=0.0)
    if reach:
        ang = _reach(player, hp, frame, best[1])
        lever.reach_info.update(angle=ang, reached=(Vector(player.item_point("right", best[1])) - hp).length)
    if sync == "hand":
        f_flip = best[1]
    else:
        f_flip = frame_of(at(frame, LEVER_SHOW_TICKS))
    lever.flip(f_flip, ease)
    return f_flip


def _last_cut_any(player, frame):
    best = None
    for fc in _root_fcurves(player.root):
        if fc.data_path != "location":
            continue
        for kp in fc.keyframe_points:
            f = kp.co.x + 0.25
            if kp.interpolation == "CONSTANT" and abs(f - round(f)) < 1e-3 and round(f) <= frame + 1e-6:
                best = int(round(f)) if best is None else max(best, int(round(f)))
    return best


def _reach(player, target, frame, f_near):
    """Lift / turn the right arm (delta_rotation_euler x and z, outside the swing's own keys: at most REACH_LIMIT
    each) during the swing that starts on `frame`, so the hand reaches `target` on f_near: keyed 0 -> angle -> 0
    (smooth), solved numerically on the evaluated rig. Returns the combined angle (radians)."""
    arm = player.arm_r
    end = frame + 6 * TICK + 1.0
    keeps = []
    for i in (0, 2):
        fc0 = _fcurve(arm, "delta_rotation_euler", i)
        keeps.append([(kp.co.x, kp.co.y) for kp in fc0.keyframe_points
                      if not (frame - 0.01 <= kp.co.x <= end + 0.01)])

    def put(ax, az):
        for keep, i, a in ((keeps[0], 0, ax), (keeps[1], 2, az)):
            ks = sorted(keep + [(float(frame), 0.0), (float(f_near), a), (end, 0.0)])
            fc = _keys(arm, "delta_rotation_euler", [k[0] for k in ks], [k[1] for k in ks], "BEZIER", index=i)
            for kp in fc.keyframe_points:
                kp.handle_left_type = kp.handle_right_type = "AUTO_CLAMPED"
            fc.update()

    def miss(ax, az):
        put(ax, az)
        return (Vector(player.item_point("right", f_near)) - Vector(target)).length

    best = (miss(0.0, 0.0), 0.0, 0.0)
    step = math.radians(16.0)
    while step > math.radians(0.5):
        moved = False
        for dx, dz in ((step, 0.0), (-step, 0.0), (0.0, step), (0.0, -step)):
            ax = max(-REACH_LIMIT, min(REACH_LIMIT, best[1] + dx))
            az = max(-REACH_LIMIT, min(REACH_LIMIT, best[2] + dz))
            d = miss(ax, az)
            if d < best[0] - 1e-5:
                best, moved = (d, ax, az), True
                break
        if not moved:
            step *= 0.5
    put(best[1], best[2])
    return math.hypot(best[1], best[2])


# ----------------------------------------------------------------------------------------------------
# piston
# ----------------------------------------------------------------------------------------------------
class Piston(_Part):
    """A piston or sticky piston (PistonBaseBlock + PistonMovingBlockEntity + PistonHeadRenderer).

    Looks: 'R' the retracted block model (piston / sticky_piston, extended=false); 'S' the extended base
    (piston_base) with the head drawn SHORT (piston_head short=true); 'L' the base with the long head. The head
    objects move; the look is chosen per frame from the head's travel over that frame's exposure."""

    kind = "piston"

    def __init__(self, kit_, cell, facing="north", sticky=False, extended=False, name=None, sky_light=None):
        super().__init__(kit_, cell, name)
        if facing not in DIRS6:
            raise RedstoneError("piston: facing is one of %s" % (DIRS6,))
        self.facing, self.sticky, self.extended0 = facing, bool(sticky), bool(extended)
        self.dir = VEC[facing].copy()
        self.head_cell = _add(self.cell, facing)
        kit_._claim(self.cell, self)
        if extended:
            kit_._claim(self.head_cell, self)
        dim = kit_._dim(sky_light, self.cell)
        bid = "sticky_piston" if sticky else "piston"
        mat = _plain(bid, dim)
        self.retracted_ob = _object(kit_, self.name + "_block", _quads(bid, {"facing": facing, "extended": "false"}),
                                    mat, self.cell)
        self.base_ob = _object(kit_, self.name + "_base", _quads(bid, {"facing": facing, "extended": "true"}),
                               mat, self.cell)
        typ = "sticky" if sticky else "normal"
        self.head_long = _object(kit_, self.name + "_head", _quads("piston_head", {
            "facing": facing, "short": "false", "type": typ}), mat, self.head_cell)
        self.head_short = _object(kit_, self.name + "_head_short", _quads("piston_head", {
            "facing": facing, "short": "true", "type": typ}), mat, self.head_cell)
        self.looks = _Looks({"R": [self.retracted_ob], "S": [self.base_ob, self.head_short],
                             "L": [self.base_ob, self.head_long]}, "L" if extended else "R")
        self.moves = {}                 # t0 -> 'extend' | 'retract'
        self.pushed = {}                # t0 -> [movables]
        self.placed = None              # the frame it is placed on (None: there from the start)
        self._rekey()

    # ---- state over time
    def travel(self, t):
        """How far the head is out of the base at film time t (0 = retracted, 1 = extended): linear over the
        2 ticks of a move (progress += 0.5 per tick, rendered with the partial tick)."""
        d = 1.0 if self.extended0 else 0.0
        for t0, kind in sorted(self.moves.items()):
            if t < t0:
                break
            u = min(1.0, (t - t0) / PISTON_FRAMES)
            d = u if kind == "extend" else 1.0 - u
        return d

    def extended_at(self, t):
        """True when the piston is (becoming) extended at time t (its last move started was an extension)."""
        st = self.extended0
        for t0, kind in sorted(self.moves.items()):
            if t0 <= t + 1e-9:
                st = kind == "extend"
        return st

    def look_at_frame(self, f):
        """The look drawn on whole frame f (exposure [f, f + 0.5])."""
        ds = [self.travel(f + k * 0.125) for k in range(5)]
        if max(ds) <= 1e-6:
            return "R"
        return "S" if self.travel(f + 0.25) <= SHORT_ARM_UNTIL + 1e-9 else "L"

    def place(self, frame, player=None, hand="right"):
        """Not there before whole frame `frame` (a player's swing starts ON frame - 1 when given: the block is
        there the frame after the click). A piston placed where it is powered extends in the same tick
        (PistonBaseBlock.onPlace -> checkIfExtend): p.place(f); p.extend(f). Returns frame."""
        f = int(frame)
        if player is not None:
            player.attack(f - 1, hand)
        self.placed = f
        self._rekey()
        return float(f)

    def _rekey(self):
        self.looks.hist.clear()
        self.looks.initial = None if self.placed is not None else ("L" if self.extended0 else "R")
        if self.placed is not None:
            self.looks.set(self.placed, self.look_at_frame(self.placed))
        if self.moves:
            lo = int(math.floor(min(self.moves))) - 2
            hi = int(math.ceil(max(self.moves) + PISTON_FRAMES)) + 2
            prev = self.looks.at(lo - 1)
            for f in range(lo, hi + 1):
                if self.placed is not None and f < self.placed:
                    continue
                lk = self.look_at_frame(f)
                if lk != prev:
                    self.looks.set(f, lk)
                    prev = lk
        self.looks.rekey()
        times = sorted({t for t0 in self.moves for t in (t0, t0 + PISTON_FRAMES)})
        for ob in (self.head_long, self.head_short):
            tr = self.kit.track(ob)
            tr.rest = Vector(self.head_cell)
            tr.moves = {}
            for t0, kind in self.moves.items():
                d = self.dir.copy() * (1.0 if kind == "extend" else -1.0)
                tr.moves[t0] = (t0, t0 + PISTON_FRAMES, d)
            # the head rests extended; when the piston starts retracted, its head sits one block back
            if not self.extended0:
                tr.rest = Vector(self.cell)
            tr.rekey()
        _ = times

    def _check_time(self, t0, kind):
        for t, k in self.moves.items():
            if abs(t - t0) < 1e-9:
                continue
            if abs(t - t0) < PISTON_FRAMES - 1e-6:
                raise RedstoneError("%s: a %s at %.2f overlaps the %s at %.2f (a move takes 2 ticks = %.1f frames)"
                                    % (self.name, kind, t0, k, t, PISTON_FRAMES))
        if self.extended_at(t0 - 1e-6) == (kind == "extend"):
            raise RedstoneError("%s: cannot %s at %.2f, it is already %s" % (
                self.name, kind, t0, "extended" if kind == "extend" else "retracted"))

    # ---- moves
    def extend(self, t, push="auto", ride=()):
        """Extend at film time t (the tick the piston is powered; PISTON_START_TICKS = 0). The head and every block
        in front of it travel one block in 2 ticks (2.4 frames), linear. push="auto": the kit's movable blocks in a
        line from the cell in front (at most PUSH_LIMIT = 12, else RedstoneError and nothing moves); push=[...] the
        same blocks given (movables, Breakables or cells, checked against the line). ride = things carried
        (kit.ride for one move). Returns the time the move ends (t + 2.4)."""
        t = float(t)
        old = self.pushed.pop(t, None)
        if old is not None:
            for m in old:
                m.unmove(t)
            self.moves.pop(t, None)
        self._check_time(t, "extend")
        line = self._line(t, push)
        end = _add(self.cell, self.facing, len(line) + 1)
        what = self.kit.occupied(end, t, ignore=line)
        if what is not None and not (isinstance(what, _Part) and what is self):
            raise RedstoneError("%s: cannot extend at %.2f: %s is in the way at %s (only the kit's movable blocks "
                                "are pushed)" % (self.name, t, what if what != "world" else "a block of the set",
                                                 end))
        self.moves[t] = "extend"
        self.pushed[t] = line
        for m in line:
            m.move(t, self.facing)
        for thing in ride:
            ob, character = _thing_object(thing)
            if character:
                _shift_character(ob, t, t + PISTON_FRAMES, self.dir.copy())
            else:
                tr = self.kit.track(ob)
                tr.moves[("ride", self.name, t)] = (t, t + PISTON_FRAMES, self.dir.copy())
                tr.rekey()
        self._rekey()
        return t + PISTON_FRAMES

    def retract(self, t, pull="auto"):
        """Retract at film time t: the head comes back in 2 ticks; a sticky piston pulls the block in front of its
        head with it (pull="auto": the kit's movable block there, if any; None: nothing). Returns t + 2.4."""
        t = float(t)
        old = self.pushed.pop(t, None)
        if old is not None:
            for m in old:
                m.unmove(t)
            self.moves.pop(t, None)
        self._check_time(t, "retract")
        pulled = []
        if self.sticky and pull is not None:
            front = _add(self.cell, self.facing, 2)
            if pull == "auto":
                m = self.kit.movable_at(front, t)
                pulled = [m] if m is not None else []
            else:
                m = _as_movable(self.kit, pull, t)
                if m.cell_at(t) != front:
                    raise RedstoneError("%s: a sticky piston pulls the block at %s, not %s" % (self.name, front,
                                                                                               m.cell_at(t)))
                pulled = [m]
        self.moves[t] = "retract"
        self.pushed[t] = pulled
        for m in pulled:
            m.move(t, OPPOSITE[self.facing])
        self._rekey()
        return t + PISTON_FRAMES

    def cancel(self, t):
        """Take back the move that starts at film time t (and the moves of the blocks it pushed or pulled)."""
        t = float(t)
        for m in self.pushed.pop(t, []):
            m.unmove(t)
        self.moves.pop(t, None)
        self._rekey()

    def _line(self, t, push):
        if push is None:
            push = []
        if push == "auto":
            line, c = [], _add(self.cell, self.facing)
            while True:
                m = self.kit.movable_at(c, t)
                if m is None:
                    break
                line.append(m)
                c = _add(c, self.facing)
                if len(line) > PUSH_LIMIT:
                    break
            if self.kit.world_block(_add(self.cell, self.facing)) is not None:
                raise RedstoneError("%s: the block in front of it at %s is part of the set's mesh: carve it in the "
                                    "hook and make it kit.block(...)" % (self.name, _add(self.cell, self.facing)))
        else:
            line = [_as_movable(self.kit, p, t) for p in push]
            for k, m in enumerate(line):
                want = _add(self.cell, self.facing, k + 1)
                if m.cell_at(t) != want:
                    raise RedstoneError("%s: pushed block %d is at %s, the line needs it at %s" % (
                        self.name, k + 1, m.cell_at(t), want))
        if len(line) > PUSH_LIMIT:
            raise RedstoneError("%s: %d blocks in front of it at %.2f: the game pushes at most %d "
                                "(PistonStructureResolver.MAX_PUSH_DEPTH) and the piston does not extend at all"
                                % (self.name, len(line), t, PUSH_LIMIT))
        return line

    def power(self, t):
        """(chain helper) powered at t: extends at t (no start delay). Returns t (what powers on from it)."""
        if not self.extended_at(t):
            self.extend(t)
        return float(t)

    def unpower(self, t):
        if self.extended_at(t):
            self.retract(t)
        return float(t)

    @property
    def objects(self):
        return [self.retracted_ob, self.base_ob, self.head_long, self.head_short]

    def head_point(self, t):
        """World centre of the head plate's face at time t."""
        return Vector(self.cell) + Vector((0.5, 0.5, 0.5)) + self.dir * (self.travel(t) + 0.5)


def _as_movable(kit_, p, t):
    if isinstance(p, _Movable):
        return p
    for m in kit_.movables:
        if m.breakable is p or m.object is p:
            return m
    if isinstance(p, (tuple, list)) and len(p) == 3:
        m = kit_.movable_at(_cell(p), t)
        if m is None:
            raise RedstoneError("redstone: no movable block at %s (make it with kit.block(...))" % (tuple(p),))
        return m
    if hasattr(p, "object") or isinstance(p, bpy.types.Object):       # a foreign Breakable or plain object
        b = p if hasattr(p, "object") else _Foreign(p)
        cell = _cell(b.object.location)
        m = _Movable(kit_, b, cell)
        kit_.movables.append(m)
        return m
    raise RedstoneError("redstone: %r cannot be pushed" % (p,))


class _Foreign:
    """A plain Object given to a piston: what _Movable needs of it."""

    def __init__(self, ob):
        self.object, self.name = ob, ob.name
        self.block_id = ob.get("mc_block", "object")
        self.full_cube = True

    def show(self, frame, visible=True):
        _vis_key(self.object, frame, visible)


class PistonDoor:
    """Door blocks (stacked or side by side) that sticky pistons pull sideways into a wall: for every door cell c a
    sticky piston at c + 2 * side facing back toward c, its head cell c + side inside the wall. closed=True: the
    pistons stand extended holding the blocks in the door cells (the doorway is shut). open(f) pulls them into
    the wall, close(f) pushes them back. The door cells, the head cells and the piston cells must be empty in the
    set's World (redstone.door_cells(cells, side) lists them for the hook)."""

    def __init__(self, kit_, cells, side, block="stone", closed=True, name="piston_door", sky_light=None):
        if side not in DIRS6:
            raise RedstoneError("piston_door: side is one of %s" % (DIRS6,))
        name = kit_.unique_name(name)
        self.kit, self.name, self.side = kit_, name, side
        self.cells = [_cell(c) for c in cells]
        self.pistons, self.blocks = [], []
        for i, c in enumerate(self.cells):
            p = kit_.piston(_add(c, side, 2), OPPOSITE[side], sticky=True, extended=closed,
                            name="%s_piston_%d" % (name, i), sky_light=sky_light)
            b = kit_.block(block, c if closed else _add(c, side), name="%s_block_%d" % (name, i),
                           sky_light=sky_light)
            self.pistons.append(p)
            self.blocks.append(b)
        kit_.parts.append(self)

    def open(self, frame):
        """The pistons retract on `frame`, pulling the blocks into the wall. Returns the end time."""
        return self.kit.retract_all(self.pistons, frame)

    def close(self, frame):
        """The pistons extend on `frame`, pushing the blocks back into the doorway. Returns the end time."""
        return self.kit.extend_all(self.pistons, frame)

    def is_open(self, t):
        """True while the door is (being) opened at film time t."""
        return not self.pistons[0].extended_at(t)

    def power(self, t):
        """(circuit step) powered pistons extend: the door CLOSES at t (as in the game: a door that opens on a lever
        has its pistons wired through an inverter, or call open()). Returns t."""
        if self.is_open(t):
            self.close(t)
        return float(t)

    def unpower(self, t):
        """(circuit step) the pistons lose power and retract: the door OPENS at t. Returns t."""
        if not self.is_open(t):
            self.open(t)
        return float(t)

    def show(self, frame, visible=True):
        for p in self.pistons:
            p.show(frame, visible)
        for b in self.blocks:
            b.show(frame, visible)

    @property
    def objects(self):
        return [o for p in self.pistons for o in p.objects] + [b.object for b in self.blocks]


def door_cells(cells, side):
    """Every cell a piston_door needs empty in the World: the door cells, the head cells, the piston cells."""
    out = []
    for c in cells:
        c = _cell(c)
        out += [c, _add(c, side), _add(c, side, 2)]
    return out


class PistonRow:
    """Pistons side by side, each with one block on its arm (extended: at cell + 2 * facing; retracted: at
    cell + facing). retract(f) / extend(f) move all of them on the same tick."""

    def __init__(self, kit_, cells, facing, carry="oak_planks", extended=True, sticky=True, name="piston_row",
                 sky_light=None):
        name = kit_.unique_name(name)
        self.kit, self.name = kit_, name
        self.pistons, self.blocks = [], []
        for i, c in enumerate(cells):
            c = _cell(c)
            p = kit_.piston(c, facing, sticky=sticky, extended=extended, name="%s_%d" % (name, i),
                            sky_light=sky_light)
            self.pistons.append(p)
            if carry:
                b = kit_.block(carry, _add(c, facing, 2 if extended else 1), name="%s_%s_%d" % (name, carry, i),
                               sky_light=sky_light)
                self.blocks.append(b)
        kit_.parts.append(self)

    def retract(self, frame):
        """Every piston retracts on `frame` (the sticky ones pull their blocks one block in). Returns end time."""
        return self.kit.retract_all(self.pistons, frame)

    def extend(self, frame):
        """Every piston extends on `frame`, pushing its block out. Returns the end time."""
        return self.kit.extend_all(self.pistons, frame)

    def extended_at(self, t):
        """True while the row is (being) extended at film time t (its first piston)."""
        return self.pistons[0].extended_at(t) if self.pistons else False

    def power(self, t):
        """(circuit step) every piston powered at t extends (those already out stay). Returns t."""
        for p in self.pistons:
            p.power(t)
        return float(t)

    def unpower(self, t):
        """(circuit step) every piston loses power at t and retracts, the sticky ones pulling their blocks."""
        for p in self.pistons:
            p.unpower(t)
        return float(t)

    def show(self, frame, visible=True):
        """Per-shot visibility of the pistons and their blocks."""
        for p in self.pistons:
            p.show(frame, visible)
        for b in self.blocks:
            b.show(frame, visible)

    @property
    def objects(self):
        """Every object of the row (for Stage.hero)."""
        return [o for p in self.pistons for o in p.objects] + [b.object for b in self.blocks]


# ----------------------------------------------------------------------------------------------------
# redstone dust
# ----------------------------------------------------------------------------------------------------
def wire_color(power):
    """The colour the game tints dust with at a power level 0..15 (RedstoneWireBlock COLORS), 0..255."""
    return WIRE_COLORS[max(0, min(15, int(power)))]


def dust_shape(state):
    """The name of the shape a dust state is drawn as: dot, cross, line, corner, t, end ... (for checks)."""
    con = [d for d in HORIZONTAL if state[d] != "none"]
    ups = [d for d in HORIZONTAL if state[d] == "up"]
    n = len(con)
    if n == 0:
        name = "dot"
    elif n == 4:
        name = "cross"
    elif n == 3:
        name = "t"
    elif n == 2:
        name = "line" if OPPOSITE[con[0]] == con[1] else "corner"
    else:
        name = "end"
    return name + ("+up:" + ",".join(ups) if ups else "")


DUST_LAYER_PX = 0.05                 # the dust models stack coplanar quads (dot + four half lines at y 0.25): each
                                     # multipart piece is lifted this much above the one before it (Cycles skips a
                                     # coplanar quad behind a cut-out texel: arms vanished under the dot's square)


def dust_quads(props):
    """The quads of a redstone_wire state, as the game draws it, made safe for a ray tracer: the multipart pieces in
    their order, each flat piece DUST_LAYER_PX above the previous one, the downward twins of the flat pieces
    dropped (dust always lies on a block: they are never seen). The pieces that climb a wall are kept as they are."""
    out = []
    for k, part in enumerate(mc.resolve_blockstate("redstone_wire", props)):
        for q in mc.bake_part(part):
            d = q.facing
            if q.thin and d in mc.DIR_VEC:
                axis = 1 if d in ("down", "up") else (2 if d in ("north", "south") else 0)
                edge = 16.0 if d in ("up", "south", "east") else 0.0
                if abs(q.pts[0][axis] - edge) < 1.0:
                    continue                                   # the twin facing the block it lies on: never seen
            pts = q.pts
            if len({round(p[1], 4) for p in q.pts}) == 1:      # a flat piece (y 0.25 + the thin offset)
                pts = [(p[0], p[1] + k * DUST_LAYER_PX, p[2]) for p in q.pts]
            # one opaque cut-out face lit like an up-facing surface (shade 'up': up normals, a plain material).
            # NOT engine.mcassets' two-sided 'up_thin' material: that one lets the ray through to the twin it
            # expects behind it, and with the twin gone the floor showed through and turned the dust pink.
            out.append(mc.Quad(pts, q.uvs, q.texture, q.tintindex, q.overlay, q.cull, q.facing, False, "up"))
    return out


class Wire(_Part):
    """Redstone dust over a set of cells: the game's shape in each cell (redstone_wire multipart from the
    connections), tinted by its power level, one object per (cell, level) shown when that level is keyed."""

    kind = "wire"

    def __init__(self, kit_, cells, power=0, dots=(), source=None, name=None, sky_light=None):
        cells = [_cell(c) for c in cells]
        if not cells:
            raise RedstoneError("wire: no cells")
        super().__init__(kit_, cells[0], name)
        self.cells = cells
        for c in cells:
            kit_._claim(c, self)
        self.dots = {_cell(c) for c in dots}
        self.source = _cell(source) if source is not None else cells[0]
        self.dim = kit_._dim(sky_light, self.cell)
        self.states = {c: kit_.wire_state(c, c in self.dots) for c in cells}
        self.looks_by_cell = {}
        self.hist = {c: {} for c in cells}           # cell -> {frame: level}
        p0 = power if isinstance(power, dict) else {c: int(power) for c in cells}
        self.level0 = {c: int(p0.get(c, 0)) for c in cells}
        for c in cells:
            self._ensure(c, self.level0[c])
        self.links = self._links()
        self._rekey_all()

    def _links(self):
        """Which dust cells the game treats as connected: a neighbour at the same height, one block up a side
        ('up') or one block down past the edge of the block it lies on ('side' toward a dust below)."""
        out = {c: set() for c in self.cells}
        cs = set(self.cells)
        for c in self.cells:
            for d in HORIZONTAL:
                s = self.states[c][d]
                if s == "none":
                    continue
                n = _add(c, d)
                cands = [n] + ([_add(n, "up")] if s == "up" else [_add(n, "down")])
                for cand in cands:
                    if cand in cs:
                        out[c].add(cand)
                        out[cand].add(c)
        return out

    def _ensure(self, c, level):
        lk = self.looks_by_cell.get(c)
        if lk is None:
            lk = self.looks_by_cell[c] = _Looks({}, self.level0.get(c, 0) if hasattr(self, "level0") else level)
        if level not in lk.looks:
            props = dict(self.states[c])
            props["power"] = str(level)
            quads = dust_quads(props)
            tint = dust_tint(level)
            g = DUST_GLOW * level / 15.0
            a = dust_albedo(level)
            style = {}
            if level > 0 and g > 0:
                style["glow"] = (g, g, g)
            if a < 0.999:
                style["albedo"] = a

            def mat(q, tint=tint, style=style):
                if style:                                  # lit dust is never dimmed by a dark set: it glows
                    return _styled(q.texture, tint, getattr(q, "shade", None), **style)
                return _material(q.texture, tint, getattr(q, "shade", None), None, self.dim)

            ob = _object(self.kit, "%s_%d_%d_%d_p%d" % (self.name, c[0], c[1], c[2], level), quads, mat, c)
            ob.visible_shadow = False                  # dust is a flat overlay: it casts no shadow worth tracing
            lk.add(level, [ob])
        return lk

    def _rekey_all(self):
        for c in self.cells:
            lk = self._ensure(c, self.level0[c])
            for f, lev in self.hist[c].items():
                self._ensure(c, lev)
            lk.hist = dict(self.hist[c])
            lk.rekey()

    def distances(self, source=None):
        """Steps along the dust from the source cell to every cell (None: not connected)."""
        src = _cell(source) if source is not None else self.source
        if src not in self.links:
            # a source BESIDE the line (a lever, a torch): the dust cells next to it are 0 steps away
            starts = [c for c in self.cells if sum(abs(a - b) for a, b in zip(c, src)) == 1]
        else:
            starts = [src]
        dist = {c: None for c in self.cells}
        todo = list(starts)
        for c in starts:
            dist[c] = 0
        while todo:
            c = todo.pop(0)
            for n in self.links[c]:
                if dist[n] is None:
                    dist[n] = dist[c] + 1
                    todo.append(n)
        return dist

    def levels(self, frame, source=None, level=15):
        """{cell: power} the game gives the line at `frame` from that source: level - steps (>= 0)."""
        dist = self.distances(source)
        return {c: (max(0, int(level) - d) if d is not None else 0) for c, d in dist.items()}

    def set_levels(self, frame, levels):
        """Key explicit power levels {cell: 0..15} from `frame` on."""
        f = int(frame)
        for c, lev in levels.items():
            c = _cell(c)
            if c not in self.hist:
                raise RedstoneError("%s: %s is not one of its cells" % (self.name, c))
            self.hist[c][f] = max(0, min(15, int(lev)))
        self._rekey_all()

    def power(self, frame, source=None, level=15, ripple=0):
        """The line lit from `source` (default: the wire's source cell; a cell beside the line = a lever / torch
        there) at power `level`, falling by one per block of dust. All on one frame (the game: one tick), or
        ripple=N: block by block away from the source over N frames (a film choice). Returns frame."""
        f0 = frame_of(frame)
        dist = self.distances(source)
        far = max([d for d in dist.values() if d is not None] or [0])
        for c, d in dist.items():
            lev = max(0, int(level) - d) if d is not None else 0
            f = f0
            if ripple and far and d is not None:
                f = f0 + int(round(float(ripple) * d / float(far)))
            for ff in [k for k in self.hist[c] if f0 <= k < f]:      # a ripple: nothing stale before its turn
                del self.hist[c][ff]
            self.hist[c][f] = lev
        self._rekey_all()
        return float(frame)

    def unpower(self, frame):
        """The whole line dark (power 0) on one frame, as the game updates it within one tick. Returns frame."""
        f = frame_of(frame)
        for c in self.cells:
            self.hist[c][f] = 0
        self._rekey_all()
        return float(frame)

    def level_at(self, cell, frame):
        c = _cell(cell)
        return _at(self.hist[c], frame, self.level0[c])

    def show(self, frame, visible=True):
        for lk in self.looks_by_cell.values():
            lk.show(frame, visible)

    @property
    def objects(self):
        return [o for lk in self.looks_by_cell.values() for obs in lk.looks.values() for o in obs]


# ----------------------------------------------------------------------------------------------------
# repeater, lamp, torch
# ----------------------------------------------------------------------------------------------------
class Repeater(_Part):
    """A repeater (RepeaterBlock) with its delay 1..4, unlit / lit (models repeater_<n>tick[_on])."""

    kind = "repeater"

    def __init__(self, kit_, cell, toward="north", delay=1, powered=False, name=None, sky_light=None):
        super().__init__(kit_, cell, name)
        if toward not in HORIZONTAL or int(delay) not in (1, 2, 3, 4):
            raise RedstoneError("repeater: toward north | east | south | west, delay 1..4")
        kit_._claim(self.cell, self)
        self.toward, self.delay = toward, int(delay)
        self.facing = OPPOSITE[toward]                      # the game's FACING: the input side
        dim = kit_._dim(sky_light, self.cell)
        obs = {}
        for on in (False, True):
            props = {"facing": self.facing, "delay": str(self.delay), "locked": "false",
                     "powered": "true" if on else "false"}
            obs[on] = _object(kit_, "%s_%s" % (self.name, "on" if on else "off"), _quads("repeater", props),
                              _plain("repeater", dim, _lit_style if on else None), self.cell)
        self.looks = _Looks({False: [obs[False]], True: [obs[True]]}, bool(powered))

    @property
    def delay_ticks(self):
        return REPEATER_TICKS_PER_DELAY * self.delay

    def set(self, frame, powered):
        """Lit / unlit from whole frame `frame` on."""
        self.looks.set(int(frame), bool(powered))
        self.looks.rekey()

    def power(self, t):
        """Its input powered at film time t: the output (and the lit model) comes delay x 2 ticks later. Returns
        that time."""
        t1 = at(t, self.delay_ticks)
        self.set(frame_of(t1), True)
        return t1

    def unpower(self, t):
        t1 = at(t, self.delay_ticks)
        self.set(frame_of(t1), False)
        return t1


def _point_light(kit_, name, location, watts, color, radius):
    ob = _props.make_light("lantern", kit_.collection)
    ob.name = name
    ob.data.name = name
    ob.data.energy = watts
    ob.data.color = color
    ob.data.shadow_soft_size = radius
    ob["base_energy"] = watts
    ob["mc_light"] = "redstone"
    ob.location = location
    return ob


class _Lit(_Part):
    """A part with a lit look and a point light that is on exactly while the lit look is shown."""

    def _rekey_lights(self):
        lk = self.looks
        frames = sorted(set(lk.hist) | set(lk.shown))
        times = [(frames[0] if frames else 1) - 1] + frames
        states = [(lk.initial, True)] + [(lk.at(f), _at(lk.shown, f, True)) for f in frames]
        now = bpy.context.scene.frame_current
        for L in self.lights:
            vals = [0.0 if (shown and self._lit_look(c)) else 1.0 for c, shown in states]
            for path in ("hide_render", "hide_viewport"):
                _keys(L, path, times, vals)
            L.hide_render = L.hide_viewport = not (_at(lk.shown, now, True) and self._lit_look(lk.at(now)))

    def _lit_look(self, look):
        return bool(look)


class Lamp(_Lit):
    """A redstone lamp (RedstoneLampBlock): off / on; on is a light source (LAMP_WATTS at its centre; the lamp's
    own faces do not block it: shadow linking)."""

    kind = "lamp"

    def __init__(self, kit_, cell, lit=False, name=None, sky_light=None, watts=None):
        super().__init__(kit_, cell, name)
        kit_._claim(self.cell, self)
        dim = kit_._dim(sky_light, self.cell)
        off = _object(kit_, self.name + "_off", _quads("redstone_lamp", {"lit": "false"}), _plain("redstone_lamp", dim),
                      self.cell)
        on = _object(kit_, self.name + "_on", _quads("redstone_lamp", {"lit": "true"}), _plain("redstone_lamp"),
                     self.cell)
        self.looks = _Looks({False: [off], True: [on]}, bool(lit))
        L = _point_light(kit_, self.name + "_light", self.center, LAMP_WATTS if watts is None else watts,
                         _props.TORCH_COLOR, LAMP_RADIUS)
        blk = bpy.data.collections.new(self.name + "_blockers")
        blk.objects.link(on)
        blk.objects.link(off)
        L.light_linking.blocker_collection = blk
        for co in blk.collection_objects:
            co.light_linking.link_state = "EXCLUDE"
        self.lights = [L]
        self.light = L
        self._rekey_lights()

    def set(self, frame, lit):
        """On / off from whole frame `frame` on (the light with it)."""
        self.looks.set(int(frame), bool(lit))
        self.looks.rekey()
        self._rekey_lights()

    def power(self, t):
        """Powered at t: lit at once (LAMP_ON_TICKS = 0). Returns t."""
        self.set(frame_of(t), True)
        return float(t)

    def unpower(self, t):
        """Unpowered at t: dark LAMP_OFF_TICKS = 4 ticks later (4.8 frames). Returns that time."""
        t1 = at(t, LAMP_OFF_TICKS)
        self.set(frame_of(t1), False)
        return t1

    def lit_at(self, frame):
        return bool(self.looks.at(frame))


class Torch(_Lit):
    """A redstone torch (standing or on a wall), lit / unlit, with its weak light (REDSTONE_TORCH_WATTS)."""

    kind = "torch"

    def __init__(self, kit_, cell, wall=None, lit=True, frame=None, name=None, sky_light=None, watts=None):
        super().__init__(kit_, cell, name)
        if wall is not None and wall not in HORIZONTAL:
            raise RedstoneError("torch: wall = north | east | south | west (the side it leans out to) or None")
        kit_._claim(self.cell, self)
        self.wall = wall
        dim = kit_._dim(sky_light, self.cell)
        bid = "redstone_torch" if wall is None else "redstone_wall_torch"
        looks = {}
        for on in (False, True):
            props = {"lit": "true" if on else "false"}
            if wall:
                props["facing"] = wall
            quads = _quads(bid, props)
            looks[on] = [_object(kit_, "%s_%s" % (self.name, "lit" if on else "unlit"), quads,
                                 _plain(bid, None if on else dim, _lit_style if on else None), self.cell)]
            if on:
                top = max(p[1] for q in quads for p in q.pts)
                pts = [mc.to_blender(p) for q in quads for p in q.pts if p[1] >= top - 3.0]
                self.head = Vector(self.cell) + Vector(np.mean(pts, axis=0))
        looks[None] = []
        self.looks = _Looks(looks, None if frame is not None else bool(lit))
        for ob in looks[True]:
            ob.visible_shadow = False                    # the flame's halo must not shadow its own light
        L = _point_light(kit_, self.name + "_light", self.head, REDSTONE_TORCH_WATTS if watts is None else watts,
                         REDSTONE_TORCH_COLOR, 0.15)
        self.lights = [L]
        self.light = L
        if frame is not None:
            self.looks.set(int(frame), bool(lit))
        self.looks.rekey()
        self._rekey_lights()

    def _lit_look(self, look):
        return look is True

    def set(self, frame, lit):
        """Lit / unlit from whole frame `frame` on."""
        self.looks.set(int(frame), bool(lit))
        self.looks.rekey()
        self._rekey_lights()

    def remove(self, frame):
        """Gone from `frame` on (broken / picked up)."""
        self.looks.set(int(frame), None)
        self.looks.rekey()
        self._rekey_lights()

    def plant(self, frame, player=None, hand="right", consume=False):
        """Placed: with a player, his arm swing starts ON `frame` (engine.players attack) and the torch appears ON
        the frame after (the game predicts the placement in the tick of the click); without one, it appears ON
        `frame`. consume=True empties his hand from that frame. Returns the frame it appears on (the time its
        signal starts: chain on from it)."""
        f = int(frame)
        self.looks.initial = None                    # not there before it is planted
        if player is not None:
            player.attack(f, hand)
            f += 1
            if consume:
                player.hold(None, hand, frame=f)
        self.looks.set(f, True)
        self.looks.rekey()
        self._rekey_lights()
        return float(f)

    def power(self, t):
        """(chain helper) the block it stands on powered at t: the torch goes OUT 2 ticks later (an inverter).
        Returns that time."""
        t1 = at(t, TORCH_TOGGLE_TICKS)
        self.set(frame_of(t1), False)
        return t1

    def unpower(self, t):
        t1 = at(t, TORCH_TOGGLE_TICKS)
        self.set(frame_of(t1), True)
        return t1


def hold_torch(player, hand="right", frame=None, glow=True, watts=HELD_TORCH_WATTS):
    """engine.players hold("redstone_torch") with its glow: the head texels emissive (TORCH_GLOW) and a small
    point light at the torch head that is on exactly while the item is shown. Returns the item object."""
    ob = player.hold("redstone_torch", hand, frame=frame)
    if ob is None or not glow:
        return ob
    ob.data = ob.data.copy()
    mats = list(ob.data.materials)
    for i, m in enumerate(mats):                  # the sprite's own materials (front / back / edges) restyled
        if m is None:
            continue
        if m.get("mc_texture", "") == "block/redstone_torch":
            ob.data.materials[i] = _restyle(m, red_albedo=TORCH_RED_ALBEDO, glow=TORCH_GLOW)
    if watts:
        L = _props.make_light("torch", ob.users_collection[0] if ob.users_collection else None)
        L.name = ob.name + "_glow"
        L.data.energy = watts
        L.data.color = REDSTONE_TORCH_COLOR
        L.data.shadow_soft_size = 0.1
        L["base_energy"] = watts
        L["mc_light"] = "redstone"
        L.parent = ob
        L.location = (0.0, 0.0, 0.1)            # the torch head: sprite rows 4..8 lie above the sprite centre
        for path in ("hide_render", "hide_viewport"):
            fc = L.driver_add(path)
            drv = fc.driver
            drv.type = "SCRIPTED"
            var = drv.variables.new()
            var.name = "h"
            var.type = "SINGLE_PROP"
            var.targets[0].id = ob
            var.targets[0].data_path = path
            drv.expression = "h"
        ob["redstone_glow_light"] = L.name
    return ob


# ----------------------------------------------------------------------------------------------------
# sequencing: "powered from frame f"
# ----------------------------------------------------------------------------------------------------
def signal(frame, *steps):
    """Play a small circuit in the game's order: each step's input is powered when the step before it puts out its
    signal. A step is a part (wire, repeater, lamp, piston, torch, lever) or a tuple of parts powered together.
    Returns the time the last step puts out its signal.
        t = torch.plant(f, player=efe); redstone.signal(t, wire, repeater, (lamp, piston))"""
    t = float(frame)
    for step in steps:
        if isinstance(step, (tuple, list)):
            t = max(p.power(t) for p in step)
        else:
            t = step.power(t)
    return t


def unsignal(frame, *steps):
    """The same circuit switched off (repeaters keep their delay, lamps go out 4 ticks late)."""
    t = float(frame)
    for step in steps:
        if isinstance(step, (tuple, list)):
            t = max(p.unpower(t) for p in step)
        else:
            t = step.unpower(t)
    return t


# ----------------------------------------------------------------------------------------------------
# hook-time helpers (inside build_village(edit=...))
# ----------------------------------------------------------------------------------------------------
def carve(b, cells):
    """Inside the village hook: take these cells out of the World (they become parts drawn as their own objects).
    Returns {cell: (block_id, props) | None} of what was there."""
    w = getattr(b, "w", b)
    out = {}
    for c in cells:
        c = _cell(c)
        out[c] = w.get(*c)
        w.set(c[0], c[1], c[2], None)
    return out


def bench(b, x0, y0, x1, y1, block="smooth_stone", name="redstone_bench", level=None):
    """Inside the village hook: a level stone floor for redstone parts (the grass top of every column replaced by
    `block`, plants cleared, the columns reserved). Returns dict(z = the floor's top = the z of the cells the
    parts stand in, cells, name)."""
    zs = [b.ground(x, y) for x in range(x0, x1 + 1) for y in range(y0, y1 + 1)]
    zs = [z for z in zs if z is not None]
    z = int(round(level if level is not None else max(set(zs), key=zs.count)))
    cells = []
    for x in range(x0, x1 + 1):
        for y in range(y0, y1 + 1):
            if b.ground(x, y) != z:
                b.set_ground(x, y, z)
            b.clear_plants(x, y)
            b.w.set(x, y, z - 1, block)
            cells.append((x, y, z - 1))
            b.reserved.add((x, y))
    res = dict(z=z, cells=cells, name=name, box=(x0, y0, x1, y1))
    b.v.sets[name] = res
    return res



# ----------------------------------------------------------------------------------------------------
# PROOF: the parts in the real village, through the real look (golden hour, the look-dev sun)
# ----------------------------------------------------------------------------------------------------
SKY = dict(preset="golden", az=62.0, el=27.0, bloom=1.0, grade="warm")
# where the proof areas sit (Blender cells; z 0 = the first cell above the levelled ground). Clear grass north-east
# of house_f and along the meadow east of the exit road (out of every finished film's frame).
AREAS = {
    "sheet_a": (9, 22, 16, 28),      # pistons and levers
    "sheet_b": (17, 22, 25, 31),     # repeaters, lamps, torches, redstone block
    "dust": (3, 31, 12, 40),         # dust shapes and the 16 power levels
    "bench": (17, 16, 24, 21),       # beat 7 of "Leg Day": torch, dust, repeater, lamp, piston
    "lever": (5, 23, 8, 26),         # a stone pier with a wall lever, flipped by a player
    "column": (30, 12, 34, 16),      # beat 9: an upward piston under twelve iron blocks
    "door": (4, 42, 10, 49),         # "Two Apples": the one-block cell whose back wall opens on sticky pistons
    "row": (11, 41, 22, 52),         # beats 13 / 19: sticky pistons in a wall top with planks and anvils
    "lights": (36, 13, 44, 19),      # night: a village torch, a redstone lamp and a redstone torch side by side
}
DOOR = dict(cells=[(7, 47, 0), (7, 47, 1)], side="east", cell=(7, 46), villager=(7.5, 46.45, 0.0), lever=(8, 45, 1),
            cam=(8.3, 44.0, 3.0), target=(7.45, 47.4, 0.9), focus=(7.5, 47.0, 1.0),
            roof=[(x, y, 2) for x in range(5, 10) for y in range(43, 46)] + [(7, 46, 2)])
HELD = dict(player=(18.5, 20.5, 0.0), cam=(18.4, 15.9, 1.4), target=(18.45, 20.5, 1.05))
LIGHTS = dict(torch=(37, 18, 0), lamp=(40, 18, 0), rtorch=(43, 18, 0), wall_y=19)
COLUMN = dict(piston=(32, 14, 0), lever=(33, 14, 0), blocks=12)
ROW = dict(cells=[(x, 43, 3) for x in (14, 15, 16, 17)], facing="north", lever=(13, 42, 4),
           dust=[(x, 42, 4) for x in (14, 15, 16, 17)])
BENCH = dict(torch=(19, 18, 0), dust=[(20, 18, 0), (21, 18, 0)], repeater=(22, 18, 0), lamp=(23, 18, 1),
             block=(23, 18, 0), piston=(23, 17, 0), piston_facing="south", player=(20.6, 19.55, 0.0))
LEVER = dict(pier=(7, 24), lever=(7, 25, 1), facing="north")
PALETTE = dict(cam=(5.5, 35.0, 2.2), target=(5.5, 36.5, 0.0))
SKIES = {"golden": SKY,                                                  # the look-dev golden hour
         "dusk": dict(preset="dusk", az=187.0, el=5.0, bloom=1.3, grade="warm"),       # films/lookdev 'lookdev_dusk'
         "night": dict(preset="night", az=176.0, el=21.0, bloom=1.3, grade="cool")}    # films/_multisky_demo
CLOSE = dict(dust=[(x, 23, 0) for x in (22, 23, 24, 25)], repeater=(25, 24, 0), torch=(24, 24, 0),
             cam=(25.1, 25.9, 1.05), target=(25.0, 23.9, 0.35), focus=(24.6, 24.45, 0.55))


def proof_set(b, dark=False):
    """The village hook of the proof: stone floors and the static blocks the parts stand on, in AREAS. dark=True: the
    door's box gets engine.sets' baked sky light (the dark variant)."""
    for name in ("sheet_a", "sheet_b", "dust", "bench", "column", "row", "lights"):
        x0, y0, x1, y1 = AREAS[name]
        bench(b, x0, y0, x1, y1, name="redstone_" + name, level=0)
    w = b.w
    for x0, y0, x1, y1 in AREAS.values():                    # no tufts between the proof cameras and the parts
        for x in range(x0 - 4, x1 + 5):
            for y in range(y0 - 4, y1 + 7):
                if b.ground(x, y) is not None:
                    b.clear_plants(x, y)
    # sheet A: blocks for the wall and ceiling levers
    for x in (12, 13):
        w.set(x, 22, 0, "stone")
    for x in (10, 11):
        w.set(x, 23, 2, "stone")
    # sheet B: blocks for the wall torches
    for x in (20, 21):
        w.fill(x, 23, 0, x, 23, 1, "stone")
    # dust: the block a dust climbs
    w.set(7, 35, 0, "stone")
    # bench: the block under the lamp (the repeater powers it, it powers the lamp and the piston)
    w.set(BENCH["block"][0], BENCH["block"][1], BENCH["block"][2], "stone")
    # the lever pier
    for x0, y0, x1, y1 in (AREAS["lever"],):
        for x in range(x0, x1 + 1):
            for y in range(y0, y1 + 1):
                b.clear_plants(x, y)
                b.reserved.add((x, y))
    w.fill(LEVER["pier"][0], LEVER["pier"][1], 0, LEVER["pier"][0], LEVER["pier"][1], 1, "stone")
    # the row: a 2-thick stone wall 4 high, the pistons' course left open (they are parts), dust on the back
    w.fill(13, 42, 0, 18, 43, 3, "stone")
    for c in ROW["cells"]:
        w.set(c[0], c[1], c[2], None)
    # the lights bench (night): a village torch, a lamp and a redstone torch standing on the floor, a wall behind
    x0, y0, x1, y1 = AREAS["lights"]
    w.fill(x0, LIGHTS["wall_y"], 0, x1, LIGHTS["wall_y"], 1, "stone")
    b.torch(LIGHTS["torch"], "torch", {}, group="rs_lights")
    # the door: a closed stone box with the aisle, the cell, the door cells, the pistons' wall and the box behind
    x0, y0, x1, y1 = AREAS["door"]
    for x in range(x0, x1 + 1):
        for y in range(y0, y1 + 1):
            b.clear_plants(x, y)
            b.reserved.add((x, y))
    w.fill(x0, y0, -1, x1, y1, 2, "stone")
    hollow = [(x, y, z) for x in range(5, 10) for y in range(43, 46) for z in (0, 1)]           # the aisle
    hollow += [(7, 46, z) for z in (0, 1)] + [(7, 48, z) for z in (0, 1)]                        # cell, box
    hollow += door_cells(DOOR["cells"], DOOR["side"]) + [DOOR["lever"]]
    for c in hollow:
        w.set(c[0], c[1], c[2], None)
    b.torch((7, 43, 1), "wall_torch", {"facing": "north"}, group="rs_door")      # behind the camera, into the cell
    b.torch((5, 44, 1), "wall_torch", {"facing": "east"}, group="rs_door")
    b.allow(AREAS["door"])
    if dark:                                     # the game's sky light baked in (engine.sets): the box is sealed
        from . import sets

        sets.env(b).bake_sky_light(b.ground, x0, y0, x1, y1)
    for c in DOOR["roof"]:                       # the roof over the aisle and the cell is off for the camera (dark:
        w.set(c[0], c[1], c[2], None)            # after the bake that counted it, and rebuilt camera-invisible)
    b.v.sets["redstone_proof"] = dict(areas=AREAS)
    return b.v.sets["redstone_proof"]


def build_proof(scene, sky=None, dark_door=False):
    """The proof film: one shot per proof (see PROOFS), every part built in the village by proof_set + a Kit.
    sky: a SKIES name or entry (default the golden hour); dark_door: the door's box with engine.sets' baked sky
    light and the door's parts at sky_light="auto". Returns dict(film, stage, village, kit, shots, frames: {still
    name: frame or [frames]}, parts)."""
    from films import lookdev

    from . import look, players, shots, village

    if isinstance(sky, str):
        sky = SKIES[sky]
    cfg = dict(SKY, **(sky or {}))
    v = village.build_village(scene, seed=1, edit=lambda b: proof_set(b, dark=dark_door))
    skyobj = look.set_time(scene, cfg["preset"], sun_azimuth=cfg["az"], sun_elevation=cfg["el"])
    look.setup_compositor(scene, bloom=cfg["bloom"], grade=cfg["grade"])
    film = shots.Film(scene, fps=FPS)
    st = lookdev.Stage(scene, film, v, skyobj)
    k = kit(v)
    out = dict(film=film, stage=st, village=v, kit=k, shots={}, frames={}, parts={})
    P = out["parts"]

    def cam(s, pos, target, lens, fstop=5.6, focus=None):
        s.lens(lens, fstop)
        s.move(pos, target)
        s.focus(focus if focus is not None else target)

    # ---- sheet A: pistons and levers (camera from the north: the faces the parts turn north catch the sun)
    k.piston((15, 27, 0), "north")
    k.piston((13, 27, 0), "north", sticky=True)
    k.piston((11, 27, 0), "up", sticky=True)
    k.piston((16, 25, 0), "west", extended=True)
    k.piston((13, 25, 0), "west", sticky=True, extended=True)
    k.piston((10, 25, 0), "up", extended=True)
    P["lever_floor_off"] = k.lever((15, 23, 0), "floor", "north")
    P["lever_floor_on"] = k.lever((14, 23, 0), "floor", "north", powered=True)
    P["lever_wall_off"] = k.lever((13, 23, 0), "wall", "north")
    P["lever_wall_on"] = k.lever((12, 23, 0), "wall", "north", powered=True)
    P["lever_ceiling_off"] = k.lever((11, 23, 1), "ceiling", "north")
    P["lever_ceiling_on"] = k.lever((10, 23, 1), "ceiling", "north", powered=True)
    s = st.shot("sheet_a", 0.5)
    cam(s, (12.9, 31.4, 5.2), (12.9, 25.3, 0.4), 25, 11.0)
    out["frames"]["sheet_a"] = s.frame_start + 2
    st.lights(s, scale=1.0, near=(12.5, 25.0, 1.0), radius=6.0)

    # ---- sheet B: repeaters, lamps, torches, redstone block
    for i, d in enumerate((1, 2, 3, 4)):
        k.repeater((24 - i, 28, 0), "south", delay=d)
    k.repeater((19, 28, 0), "south", delay=1, powered=True)
    k.repeater((18, 28, 0), "south", delay=4, powered=True)
    k.lamp((24, 26, 0))
    k.lamp((22, 26, 0), lit=True)
    k.block("redstone_block", (20, 26, 0))
    k.torch((24, 24, 0), lit=True)
    k.torch((23, 24, 0), lit=False)
    k.torch((21, 24, 1), wall="north", lit=True)
    k.torch((20, 24, 1), wall="north", lit=False)
    s = st.shot("sheet_b", 0.5)
    cam(s, (21.1, 32.5, 5.0), (21.1, 26.3, 0.4), 25, 11.0)
    out["frames"]["sheet_b"] = s.frame_start + 2

    # ---- close: the lit torch (its halo), a lit repeater and power-15 dust, close enough to count texels
    P["close_dust"] = k.wire(CLOSE["dust"], power=15)
    P["close_repeater"] = k.repeater(CLOSE["repeater"], "west", delay=2, powered=True)
    s = st.shot("close", 0.5)
    cam(s, CLOSE["cam"], CLOSE["target"], 30, 5.6, focus=CLOSE["focus"])
    out["frames"]["close"] = s.frame_start + 2

    # ---- dust: shapes, and the 16 power levels along a U from a lever
    u = [(x, 40, 0) for x in range(4, 12)] + [(11, 39, 0)] + [(x, 38, 0) for x in range(11, 3, -1)]
    P["lever_dust"] = k.lever((3, 40, 0), "floor", "west", powered=True)
    P["dust_u"] = wu = k.wire(u, source=(3, 40, 0))
    wu.power(1, source=(3, 40, 0))
    P["dust_cross"] = k.wire([(4, 36, 0)], power=15)
    P["dust_dot"] = k.wire([(6, 36, 0)], power=15, dots=[(6, 36, 0)])
    P["dust_t"] = k.wire([(9, 35, 0), (10, 35, 0), (11, 35, 0), (10, 36, 0)], power=15)
    P["dust_corner"] = k.wire([(4, 34, 0), (5, 34, 0), (5, 35, 0)], power=9)
    P["dust_climb"] = k.wire([(7, 34, 0), (7, 35, 1)], power=15)
    s = st.shot("dust", 0.5)
    cam(s, (7.6, 28.8, 9.4), (7.6, 36.0, 0.1), 30, 8.0)
    out["frames"]["dust"] = s.frame_start + 2
    s = st.shot("palette", 0.5)                      # power-15 dust close (the cross and the dot): palette_check()
    cam(s, PALETTE["cam"], PALETTE["target"], 24, 8.0)
    out["frames"]["palette"] = s.frame_start + 2
    out["palette_parts"] = [P["dust_cross"], P["dust_dot"]]

    # ---- bench: beat 7 (the narrator plants the torch; the line, the repeater, the lamp, the piston)
    s = st.shot("bench", 1.0)
    f0 = s.frame_start
    efe = players.add_player(st, "efe", "efe", slim=True)
    efe.place(f0, BENCH["player"], 0.0)
    hold_torch(efe, "right")
    torch = P["bench_torch"] = k.torch(BENCH["torch"])                        # not there until plant()
    wire = P["bench_wire"] = k.wire(BENCH["dust"], source=BENCH["torch"])
    rep = P["bench_repeater"] = k.repeater(BENCH["repeater"], "east", delay=1)
    lamp = P["bench_lamp"] = k.lamp(BENCH["lamp"])
    pis = P["bench_piston"] = k.piston(BENCH["piston"], BENCH["piston_facing"])
    efe.look_at(f0, Vector(BENCH["torch"]) + Vector((0.5, 0.5, 0.3)), ease=0)
    t = torch.plant(f0 + 4, player=efe)
    end = signal(t, wire, rep, (lamp, pis))
    out["bench_times"] = dict(click=f0 + 4, torch=t, repeater_out=at(t, rep.delay_ticks), end=end)
    efe.look_at(f0 + 9, lamp.center, ease=6)
    st.use(s, efe)
    cam(s, (21.5, 14.6, 1.3), (21.5, 18.9, 1.0), 24, 3.2, focus=efe.head)
    st.hero(s, "narrator", efe)
    out["frames"]["bench"] = [f0 + 3, f0 + 5, f0 + 7, f0 + 8, f0 + 9, f0 + 13]

    # ---- held: the narrator facing the lens with the redstone torch in his hand (beat 24's key light)
    s = st.shot("held", 0.5)
    f0 = s.frame_start
    efe.place(f0, HELD["player"], 0.0)
    efe.look_at(f0, None, ease=0)
    st.use(s, efe)
    cam(s, HELD["cam"], HELD["target"], 50, 2.8, focus=efe.head)
    out["frames"]["held"] = f0 + 2

    # ---- the lever, flipped by a player's hand
    s = st.shot("lever", 0.75)
    f0 = s.frame_start
    lev = P["lever_pier"] = k.lever(LEVER["lever"], "wall", LEVER["facing"])
    steve = players.add_player(st, "steve", "steve")
    pos, yaw = lev.stand()
    steve.place(f0, pos, yaw)
    steve.look_at(f0, lev.hand_point(f0, 0.5), ease=0)
    ff = flip_by(steve, lev, f0 + 4, sync="hand", look=False, reach=True)
    out["lever_flip"] = ff
    out["lever_reach"] = min(((Vector(steve.item_point("right", f / 2.0)) - lev.hand_point(f0, 0.5)).length, f / 2.0)
                             for f in range(2 * f0 + 8, 2 * f0 + 28))
    st.use(s, steve)
    cam(s, (5.0, 28.3, 2.2), (7.45, 25.7, 1.45), 30, 4.0, focus=lev.hand_point(f0))
    out["frames"]["lever"] = [f0 + 3, ff - 1, ff, f0 + 14]

    # ---- the column: an upward piston and twelve iron blocks; the narrator's lever beside it
    s = st.shot("column", 1.0)
    f0 = s.frame_start
    cp = P["column_piston"] = k.piston(COLUMN["piston"], "up")
    x, y, z = COLUMN["piston"]
    P["column_blocks"] = [k.block("iron_block", (x, y, z + i)) for i in range(1, COLUMN["blocks"] + 1)]
    cl = P["column_lever"] = k.lever(COLUMN["lever"], "floor", "east")
    t = cl.flip(f0 + 6)
    cp.power(t)
    cam(s, (36.6, 8.4, 0.55), (32.4, 14.4, 6.6), 18, 8.0, focus=(32.5, 14.5, 4.0))
    out["frames"]["column"] = [f0 + 5, f0 + 6, f0 + 7, f0 + 10]

    # ---- the row: four sticky pistons in a wall top, planks on their arms, anvils on the planks
    s = st.shot("row", 1.0)
    f0 = s.frame_start
    row = P["row"] = k.piston_row(ROW["cells"], ROW["facing"], carry="oak_planks", extended=True)
    P["row_anvils"] = [k.block("anvil", (c[0], c[1] + 2, c[2] + 1), {"facing": "west"}) for c in ROW["cells"]]
    rl = P["row_lever"] = k.lever(ROW["lever"], "floor", "east", powered=True)
    rw = P["row_wire"] = k.wire(ROW["dust"], source=ROW["lever"])
    rw.power(1, source=ROW["lever"])
    t = rl.flip(f0 + 6)
    rw.unpower(t)
    row.retract(t)
    cam(s, (20.6, 50.4, 6.2), (15.4, 43.6, 3.5), 24, 8.0)
    out["frames"]["row"] = [f0 + 5, f0 + 7, f0 + 10]

    # ---- the door of "Two Apples": the librarian in his cell, the back wall opening behind him, seen from above
    #      the aisle (the roof over the aisle and the cell is off; dark_door: it is there for light and shadow but
    #      invisible to the camera, the box sealed and its sky light baked as engine.sets does)
    s = st.shot("door", 2.0)
    f0 = s.frame_start
    dl = "auto" if dark_door else None
    if dark_door:
        for c in DOOR["roof"]:
            k.block("stone", c, sky_light=dl).object.visible_camera = False
    door = P["door"] = k.piston_door(DOOR["cells"], DOOR["side"], block="stone", closed=True, sky_light=dl)
    lev = P["door_lever"] = k.lever(DOOR["lever"], "wall", "south", sky_light=dl)
    dad = st.actor("dad", "librarian")
    dad.place(f0, DOOR["villager"], 0.0)
    door.open(lev.flip(f0 + 8))
    door.close(lev.flip(f0 + 30))
    st.use(s, dad)
    cam(s, DOOR["cam"], DOOR["target"], 24, 4.0, focus=DOOR["focus"])
    st.lights(s, scale=1.0, groups={"rs_door": 3.0}, near=(7.5, 45.0, 1.0), radius=4.0)
    out["frames"]["door"] = [f0 + 7, f0 + 9, f0 + 12, f0 + 29, f0 + 31, f0 + 34]
    out["frames"]["door_dark"] = [f0 + 7, f0 + 12, f0 + 34]
    out["door_parts"] = dict(door=door, lever=lev)

    # ---- lights (night): a village torch, a redstone lamp and a redstone torch on the floor, side by side
    s = st.shot("lights", 0.5)
    f0 = s.frame_start
    P["lights_lamp"] = k.lamp(LIGHTS["lamp"], lit=True)
    P["lights_rtorch"] = k.torch(LIGHTS["rtorch"], lit=True)
    cam(s, (40.5, 10.6, 3.6), (40.5, 16.6, 0.2), 30, 8.0)
    st.lights(s, scale=1.0, groups={"rs_lights": 1.0}, near=(40.5, 17.0, 0.5), radius=6.0)
    out["frames"]["lights"] = f0 + 2
    st.finish()
    return out


PROOFS = ("sheet_a", "sheet_b", "close", "dust", "bench", "lever", "column", "row", "door", "door_dark", "lights")
STRIP_RES = {"bench": (640, 360), "row": (640, 360), "door": (360, 640), "column": (360, 640),
             "lever": (360, 640), "door_dark": (360, 640)}     # strip tiles: landscape for subjects along a line
PROOF_BUILD = {"door_dark": dict(dark_door=True), "lights": dict(sky="night")}    # stills that need their own build
LANDSCAPE = ("sheet_a", "sheet_b", "lights")
SHEET_RES = (960, 540)               # the two part sheets are landscape (the same pixels as a 540x960 still)


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


def _render(scene, film, frame, name, res=None):
    import os
    import time

    t = time.time()
    if res is not None:
        scene.render.resolution_x, scene.render.resolution_y = res
    film.goto(frame)
    path = os.path.join(_out_dir(), "redstone_%s.png" % name)
    scene.render.filepath = path
    bpy.ops.render.render(write_still=True)
    print("[redstone] %-22s frame %4d -> %s  %.1f s" % (name, frame, path, time.time() - t), flush=True)
    return path


def _sheet(paths, name, cols, labels=None):
    import os

    from PIL import Image, ImageDraw

    tiles = [Image.open(p).convert("RGB") for p in paths]
    w, h = tiles[0].size
    rows = (len(tiles) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * w, rows * h), (0, 0, 0))
    d = ImageDraw.Draw(sheet)
    for i, im in enumerate(tiles):
        x, y = (i % cols) * w, (i // cols) * h
        sheet.paste(im, (x, y))
        if labels:
            d.rectangle([x, y, x + 7 * len(labels[i]) + 6, y + 14], fill=(0, 0, 0))
            d.text((x + 3, y + 1), labels[i], fill=(255, 255, 255))
    path = os.path.join(_out_dir(), "redstone_%s.png" % name)
    sheet.save(path)
    print("[redstone] sheet %s (%dx%d)" % (path, sheet.size[0], sheet.size[1]), flush=True)
    return path


def _stills(names, samples=16):
    """Render the proof stills named (PROOFS): single stills at 540x960 (LANDSCAPE ones 960x540), strips as tiles at
    STRIP_RES; the names of PROOF_BUILD get a build of their own."""
    groups = {}
    for name in names:
        cfg = PROOF_BUILD.get(name, {})
        groups.setdefault(tuple(sorted(cfg.items())), []).append(name)
    paths = []
    for cfg, group in groups.items():
        scene = _fresh(samples=samples)
        out = build_proof(scene, **dict(cfg))
        film = out["film"]
        for name in group:
            fr = out["frames"][name]
            if isinstance(fr, int):
                paths.append(_render(scene, film, fr, name, res=SHEET_RES if name in LANDSCAPE else (540, 960)))
                continue
            tiles = [_render(scene, film, f, "%s_f%d" % (name, f), res=STRIP_RES[name]) for f in fr]
            labels = ["frame %d" % f for f in fr]
            w, h = STRIP_RES[name]
            paths.append(_sheet(tiles, name + "_strip", 3 if w > h else len(tiles), labels))
    return paths


def _pixel(scene, point):
    """(x, y) pixel of a world point in the scene camera's render (top-left origin)."""
    from bpy_extras.object_utils import world_to_camera_view

    co = world_to_camera_view(scene, scene.camera, Vector(point))
    r = scene.render
    return int(round(co.x * r.resolution_x)), int(round((1.0 - co.y) * r.resolution_y))


def _lum(img, xy, half=3):
    """Median linear luminance of a (2 half + 1)^2 pixel box of an sRGB image array."""
    x, y = xy
    box = img[max(0, y - half):y + half + 1, max(0, x - half):x + half + 1].reshape(-1, 3) / 255.0
    lin = np.where(box <= 0.04045, box / 12.92, ((box + 0.055) / 1.055) ** 2.4)
    return float(np.median(lin @ np.array([0.2126, 0.7152, 0.0722])))


def _light_off(obs, off=True):
    """Take lights out of the lighting (ray visibility; their keyed energy / visibility stay as they are)."""
    for L in obs:
        for a in ("visible_diffuse", "visible_glossy", "visible_transmission", "visible_volume_scatter"):
            setattr(L, a, not off)


def light_study(which="floor", res=(640, 360)):
    """MEASURED light of the module's sources (renders, prints a table; see the docstring's MEASURED):
    'floor'  night, LIGHTS bench: the floor 1, 2, 3 blocks in front of a village torch, a lit lamp and a redstone
             torch, each light alone minus all off, against the game's ratios (lightmap of the levels there);
    'lamp'   golden hour, the bench of beat 7: the narrator's face with the lamp at LAMP_WATTS x 1 / 4 / 8;
    'held'   dusk, the same bench: his face with the held redstone torch at 30 / 120 / 300 W."""
    from PIL import Image

    scene = _fresh(res=res, samples=16)
    sky = {"floor": "night", "lamp": "golden", "held": "dusk"}[which]
    out = build_proof(scene, sky=sky)
    film, P = out["film"], out["parts"]
    path = lambda n: "%s/redstone_study_%s.png" % (_out_dir(), n)       # noqa: E731

    def shot(name, frame):
        _render(scene, film, frame, "study_" + name)
        return np.asarray(Image.open(path(name)).convert("RGB")).astype(np.float64)

    rows = []
    if which == "floor":
        f = out["frames"]["lights"]
        film.goto(f)
        torch_light = min((o for o in out["village"].lantern_lights if o.get("group") == "rs_lights"),
                          key=lambda o: (o.location - Vector(LIGHTS["torch"]) - Vector((0.5, 0.5, 0.5))).length)
        srcs = {"torch": (torch_light, LIGHTS["torch"], 14), "lamp": (P["lights_lamp"].light, LIGHTS["lamp"], 15),
                "redstone torch": (P["lights_rtorch"].light, LIGHTS["rtorch"], 7)}
        allL = [v[0] for v in srcs.values()]
        _light_off(allL)
        base = shot("off", f)
        got = {}
        for name, (L, cell, level) in srcs.items():
            _light_off([L], False)
            img = shot(name.replace(" ", "_"), f)
            _light_off([L])
            got[name] = []
            for d in (1, 2, 3):
                xy = _pixel(scene, (cell[0] + 0.5, cell[1] + 0.5 - d, 0.0))
                got[name].append(max(1e-6, _lum(img, xy) - _lum(base, xy)))
        _light_off(allL, False)
        for name, (L, cell, level) in srcs.items():
            for i, d in enumerate((1, 2, 3)):
                game = lightmap(level - d) / lightmap(14 - d)
                rows.append("%-15s floor %d block(s) out: +%.4f (linear luminance), x%.2f the torch's; the game x%.2f "
                            "(light %d against %d)" % (name, d, got[name][i], got[name][i] / got["torch"][i], game,
                                                      level - d, 14 - d))
        os.remove(path("off"))
    else:
        f = out["frames"]["bench"][-1] if which == "lamp" else out["frames"]["held"]
        film.goto(f)
        efe = out["stage"].cast["efe"]
        eye = Vector(efe.eye_point(f))
        cheek = eye + Vector((0.0, 0.0, -0.12))
        if which == "lamp":
            L = P["bench_lamp"].light
            levels = [LAMP_WATTS * k for k in (1.0, 4.0, 8.0)]
        else:
            item = efe.item("right")
            L = bpy.data.objects.get(item.get("redstone_glow_light", ""))
            levels = [30.0, 120.0, 300.0]
        base_e = L.data.energy
        _light_off([L])
        base = shot(which + "_off", f)
        xy = _pixel(scene, cheek)
        b0 = _lum(base, xy, 2)
        _light_off([L], False)
        for wt in levels:
            L.data.energy = wt
            img = shot("%s_%dW" % (which, wt), f)
            v1 = _lum(img, xy, 2)
            rows.append("%-5s %5.0f W: the face (pixel %s) %.4f -> %.4f linear, x%.2f" % (which, wt, xy, b0, v1,
                                                                                         v1 / max(b0, 1e-6)))
        L.data.energy = base_e
    for r in rows:
        print("[redstone study] " + r, flush=True)
    return rows


PALETTE_HUE = (8.0, 15.0)          # power-15 dust as the game draws it in daylight: (255, 50, 0) x the texel, hue
PALETTE_SAT = 0.85                   # 11.8 degrees, saturation 1.0 (the check's bounds, as the review asked)
PALETTE_SAT_LOOK = 0.76              # in the finished look: its grade (saturation 0.97 in linear HSV) lets no bright
                                     # pixel keep more than about 0.81 (min channel >= 3 % of max in linear light)


def _hsv(rgb):
    import colorsys

    h, s, v = colorsys.rgb_to_hsv(*(float(c) / 255.0 for c in rgb))
    return h * 360.0 if h < 0.5 else h * 360.0 - 360.0, s, v


def palette_check(skies=("golden", "dusk"), res=(360, 640)):
    """Render the 'palette' close-up of power-15 dust in each sky twice (with the dust, and with the dust invisible
    to the camera), take the pixels the dust covers (changed, eroded by one pixel: no edge pixel mixed with the
    floor), and check the median of their brighter half: hue PALETTE_HUE, saturation >= PALETTE_SAT. Writes
    out/test/redstone_palette_<sky>.png. Returns the number of failures."""
    import os

    from PIL import Image

    fails = 0
    for sky in skies:
        scene = _fresh(res=res, samples=16)
        out = build_proof(scene, sky=SKIES[sky])
        f = out["frames"]["palette"]
        path = _render(scene, out["film"], f, "palette_" + sky)
        tree = getattr(scene, "compositing_node_group", None)
        sat = tree.nodes.get("look_saturation") if tree is not None else None
        if sat is not None:
            sat.mute = True
        nograde = _render(scene, out["film"], f, "palette_%s_nosat" % sky)
        if sat is not None:
            sat.mute = False
        for part in out["palette_parts"]:
            for ob in part.objects:
                ob.visible_camera = False
        bare = _render(scene, out["film"], f, "palette_%s_nodust" % sky)
        a = np.asarray(Image.open(path).convert("RGB")).astype(np.float64)
        c = np.asarray(Image.open(nograde).convert("RGB")).astype(np.float64)
        b = np.asarray(Image.open(bare).convert("RGB")).astype(np.float64)
        os.remove(bare)
        os.remove(nograde)
        m = np.abs(a - b).sum(axis=2) > 60.0
        core = m.copy()
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            core &= np.roll(np.roll(m, dy, axis=0), dx, axis=1)
        if core.sum() < 50:
            print("FAIL palette %s: only %d dust pixels" % (sky, core.sum()))
            fails += 1
            continue
        res_ = []
        for img in (a, c):
            px = img[core]
            top = px[px[:, 0] >= np.median(px[:, 0])]
            med = np.median(top, axis=0)
            res_.append((tuple(int(round(v)) for v in med),) + _hsv(med))
        (col, h, s, v), (col2, h2, s2, _v2) = res_
        good = PALETTE_HUE[0] <= h <= PALETTE_HUE[1] and s2 >= PALETTE_SAT and s >= PALETTE_SAT_LOOK
        fails += 0 if good else 1
        print("%-4s palette %-6s power-15 dust (%d px, brighter half): in the look %s hue %.1f (%g-%g) saturation %.2f "
              "(>= %.2f, the grade's ceiling); before the grade's saturation step %s hue %.1f saturation %.2f (>= %.2f)"
              % ("OK" if good else "FAIL", sky, core.sum(), col, h, PALETTE_HUE[0], PALETTE_HUE[1], s,
                 PALETTE_SAT_LOOK, col2, h2, s2, PALETTE_SAT), flush=True)
    return fails


# ----------------------------------------------------------------------------------------------------
# self-test (numbers; no rendering)
# ----------------------------------------------------------------------------------------------------
def arm_inside(piston, frame, samples=9):
    """True when, at every moment of whole frame `frame`'s exposure [f, f + 0.5], the head drawn on that frame
    neither pokes out of the back of the base nor leaves a gap at its inner face (and no head shows while the
    retracted model is drawn while the head is out)."""
    look = piston.look_at_frame(frame)
    for k in range(samples):
        d = piston.travel(frame + 0.5 * k / (samples - 1))
        if look == "R":
            if d > 1e-6:
                return False
            continue
        arm_end = d - (1.0 if look == "S" else 1.25)      # head plate front at d, arm 16 (short) / 20 (long) px
        if arm_end < -1.0 - 1e-6 or arm_end > -PLATFORM_PX / 16.0 + 1e-6:
            return False
    return True


def _check():
    """Numeric checks of the module; returns the number of failures."""
    from . import quick

    failed = []

    def ok(label, cond, detail=""):
        if not cond:
            failed.append(label)
        print("%-4s %s%s" % ("OK" if cond else "FAIL", label, ("  [%s]" % detail) if detail else ""), flush=True)

    ok("dust colours (RedstoneWireBlock COLORS, float32): power 0 (76, 0, 0), 1 (112, 0, 0), 15 (255, 50, 0)",
       WIRE_COLORS[0] == (76, 0, 0) and WIRE_COLORS[1] == (112, 0, 0) and WIRE_COLORS[15] == (255, 50, 0),
       "%s %s %s" % (WIRE_COLORS[0], WIRE_COLORS[1], WIRE_COLORS[15]))
    ok("dust colours rise with power", all(WIRE_COLORS[i][0] < WIRE_COLORS[i + 1][0] for i in range(15)))
    ok("a piston move takes 2 ticks = 2.4 frames, 0.5 block per tick", PISTON_FRAMES == 2.4 and PISTON_STEP == 0.5)
    ok("delays in frames: repeater 1..4 = 2.4 / 4.8 / 7.2 / 9.6, lamp off 4.8, torch 2.4",
       [round(at(0, REPEATER_TICKS_PER_DELAY * d), 3) for d in (1, 2, 3, 4)] == [2.4, 4.8, 7.2, 9.6]
       and round(at(0, LAMP_OFF_TICKS), 3) == 4.8 and round(at(0, TORCH_TOGGLE_TICKS), 3) == 2.4)
    ok("frame_of: a change at t is drawn from the first frame whose exposure middle is at or after t",
       [frame_of(t) for t in (10.0, 10.25, 10.26, 12.4, 14.8)] == [10, 10, 11, 13, 15])

    scene = quick.reset()
    w = _blocks.World()
    w.fill(-2, -2, -1, 40, 40, -1, "smooth_stone")
    k = kit(w)

    # ---- piston: travel, looks, the arm inside the base over every exposure, pushed blocks in contact
    worst = []
    for i, frac in enumerate((0.0, 0.3, 0.6, 0.9)):
        p = k.piston((2 * i, 0, 0), "north", sticky=True)
        b = k.block("stone", (2 * i, 1, 0))
        t0 = 10.0 + frac
        p.extend(t0)
        p.retract(t0 + 12.0)
        for f in range(8, 30):
            if not arm_inside(p, f):
                worst.append((frac, f, p.look_at_frame(f)))
        # the pushed block touches the head plate at every sampled moment (no gap, no overlap)
        trb = k.track(b.object)
        for s in range(0, 61):
            t = t0 - 1.0 + s * 0.25
            plate = p.cell[1] + 1.0 + p.travel(t)
            block_back = trb.rest[1] + trb.offset(t)[1]
            if abs(plate - block_back) > 1e-6:
                worst.append(("gap", frac, t, plate, block_back))
    ok("piston (4 start phases, extend + sticky retract): on every frame the head drawn stays inside the base "
       "over the whole exposure, and the pulled / pushed block touches the head plate at every moment",
       not worst, str(worst[:3]))
    p = k.piston((0, 10, 0), "up")
    ok("looks around an extension at t=10: frames 8-9 retracted model, 10 short head, 11+ long head",
       [p.look_at_frame(f) for f in range(8, 14)] == ["R", "R", "R", "R", "R", "R"])
    p.extend(10.0)
    ok("... after extend(10.0)", [p.look_at_frame(f) for f in range(8, 14)] == ["R", "R", "S", "L", "L", "L"],
       str([p.look_at_frame(f) for f in range(8, 14)]))
    col = [k.block("iron_block", (0, 12, z)) for z in range(1, 13)]
    p2 = k.piston((0, 12, 0), "up")
    end = p2.extend(20.0)
    zs = [round(k.track(m.object).offset(end)[2], 6) for m in col]
    ok("upward piston pushes the 12 iron blocks one block up, all on the same 2.4 frames", zs == [1.0] * 12 and
       abs(end - 22.4) < 1e-9 and abs(k.track(col[-1].object).offset(21.2)[2] - 0.5) < 1e-6, str(zs[:3]))
    col13 = [k.block("iron_block", (2, 12, z)) for z in range(1, 14)]
    p3 = k.piston((2, 12, 0), "up")
    try:
        p3.extend(20.0)
        ok("13 blocks: RedstoneError (the game's push limit is 12)", False)
    except RedstoneError as e:
        ok("13 blocks: RedstoneError (the game's push limit is 12) and nothing moved",
           not any(m.moves for m in col13) and not p3.moves, str(e)[:60])
    w.set(4, 12, 2, "stone")
    p4 = k.piston((4, 12, 0), "up")
    k.block("stone", (4, 12, 1))
    try:
        p4.extend(5.0)
        ok("a block of the set's own mesh in the way: RedstoneError", False)
    except RedstoneError:
        ok("a block of the set's own mesh in the way: RedstoneError", True)
    try:
        p.extend(30.0)
        ok("extending an extended piston: RedstoneError", False)
    except RedstoneError:
        ok("extending an extended piston: RedstoneError", True)
    pp = k.piston((10, 10, 0), "north", sticky=True)
    pp.place(20)
    pp.extend(20.0)
    ok("a piston placed on frame 20 and fired at once: absent before, the slime face (short head) on 20, the arm "
       "out after", [pp.looks.at(f) for f in (18, 19, 20, 21, 23)] == [None, None, "S", "L", "L"],
       str([pp.looks.at(f) for f in (18, 19, 20, 21, 23)]))
    # a normal piston leaves the block; a sticky one pulls it
    pn = k.piston((6, 10, 0), "east")
    bn = k.block("stone", (7, 10, 0))
    pn.extend(5.0)
    pn.retract(15.0)
    ok("a normal piston pushes and leaves its block 2 out", bn.cell_at(30.0) == (8, 10, 0))
    # the door and the row: one call each
    door = k.piston_door([(20, 5, 0), (20, 5, 1)], "east", closed=True)
    door.open(40.0)
    opened = [b.cell_at(43.0) for b in door.blocks]
    door.close(60.0)
    shut = [b.cell_at(63.0) for b in door.blocks]
    ok("piston door: open() pulls both blocks one block into the wall, close() pushes them back",
       opened == [(21, 5, 0), (21, 5, 1)] and shut == [(20, 5, 0), (20, 5, 1)], "%s %s" % (opened, shut))
    row = k.piston_row([(x, 20, 3) for x in range(20, 32)], "north", carry="oak_planks")
    row.retract(50.0)
    ok("12 sticky pistons in one call: every plank pulled from 2 out to 1 out on the same tick",
       all(b.cell_at(53.0) == (20 + i, 21, 3) for i, b in enumerate(row.blocks))
       and all(abs(k.track(b.object).offset(51.2)[1] + 0.5) < 1e-6 for b in row.blocks))
    # riders
    anvil = k.block("anvil", (20, 22, 4), {"facing": "west"})
    row.blocks[0].riders_changed()
    k.ride(anvil, row.blocks[0])
    ok("kit.ride: an anvil registered on a plank moves with it (a film choice; the game drops it)",
       abs(k.track(anvil.object).offset(53.0)[1] + 1.0) < 1e-6)

    # ---- lever
    errs = []
    for face in ("floor", "wall", "ceiling"):
        for i, f in enumerate(HORIZONTAL):
            lv = k.lever((30 + 2 * i, 30 + ("floor", "wall", "ceiling").index(face) * 2, 1), face, f)
            errs.append(lv.check_error)
    ok("lever: the handle turned by the module lands exactly on the game's other model (12 placements)",
       max(errs) < 1e-4, "max %.2e" % max(errs))
    lv = k.lever((38, 38, 0), "floor", "north")
    lv.flip(20)
    fc = _fcurve(lv.handle, "rotation_axis_angle", 0)
    vals = [round(fc.evaluate(t), 6) for t in (19.0, 19.25, 19.5, 20.0, 20.25, 20.5)]
    ok("lever flip on frame 20: frame 19's exposure all old, frame 20's all new (no in-between, no smear)",
       vals[:3] == [round(lv.off_angle, 6)] * 3 and vals[3:] == [0.0] * 3, str(vals))
    lv.set(30, False, ease=2)
    ok("lever ease=2: the handle swings over frames 28-30", abs(fc.evaluate(29.0) - lv.off_angle / 2) < 1e-6)

    # ---- dust
    sh = {}
    k2 = kit(_blocks.World())
    k2.world.fill(0, 0, -1, 20, 20, -1, "stone")
    k2.world.set(10, 2, 0, "stone")
    k2.lever((0, 0, 0), "floor", "north")
    cases = {"cross": [(5, 5, 0)], "dot": [(8, 5, 0)], "line": [(1, 8, 0), (2, 8, 0), (3, 8, 0)],
             "corner": [(1, 12, 0), (2, 12, 0), (2, 13, 0)], "t": [(6, 12, 0), (7, 12, 0), (8, 12, 0), (7, 13, 0)],
             "climb": [(9, 2, 0), (10, 2, 1)], "lever": [(1, 0, 0)]}
    for name, cells in cases.items():
        wr = k2.wire(cells, dots=cells if name == "dot" else ())
        sh[name] = [dust_shape(wr.states[c]) for c in cells]
    want = {"cross": ["cross"], "dot": ["dot"], "line": ["line", "line", "line"],
            "corner": ["line", "corner", "line"], "t": ["line", "t", "line", "line"],
            "climb": ["line+up:east", "line"], "lever": ["line"]}
    ok("dust shapes chosen as the game does (unconnected = cross, right-clicked = dot, one connection runs "
       "across, corner, T, climbing a block side, toward a lever)", sh == want, str(sh))
    lw = k2.wire([(x, 16, 0) for x in range(1, 19)], source=(0, 16, 0))
    lw.power(10, source=(0, 16, 0))
    lv16 = [lw.level_at((x, 16, 0), 10) for x in range(1, 19)]
    ok("power falls by one per block from the source: 15 .. 0, then 0", lv16 == list(range(15, -1, -1)) + [0, 0],
       str(lv16))
    lw.unpower(20)
    ok("unpower: the whole line dark on one frame", all(lw.level_at(c, 20) == 0 for c in lw.cells)
       and all(lw.level_at(c, 19) == lv16[i] for i, c in enumerate(lw.cells)))
    lw.power(30, source=(0, 16, 0), ripple=8)
    rip = [min(f for f in lw.hist[c] if f >= 30) for c in lw.cells]
    ok("ripple=8: the line lights block by block away from the source, the last block 8 frames after the first",
       rip[0] == 30 and rip[-1] == 38 and all(a <= b for a, b in zip(rip, rip[1:])), str(rip))

    # ---- sequencing
    k3 = kit(_blocks.World())
    k3.world.fill(0, 0, -1, 10, 10, -1, "stone")
    k3.world.set(6, 0, 0, "stone")
    tch = k3.torch((1, 0, 0))
    wr = k3.wire([(2, 0, 0), (3, 0, 0)], source=(1, 0, 0))
    rep = k3.repeater((4, 0, 0), "east", delay=2)
    lamp = k3.lamp((5, 0, 0))
    pis = k3.piston((5, 1, 0), "north")
    t = tch.plant(10)
    end = signal(t, wr, rep, (lamp, pis))
    ok("signal(): torch planted on frame 10 lights the dust at once, the repeater (delay 2) puts out 4 ticks later "
       "(14.8: drawn from frame 15), the lamp is lit and the piston starts on that tick",
       t == 10.0 and abs(end - 14.8) < 1e-9 and lamp.lit_at(15) and not lamp.lit_at(14)
       and wr.level_at((2, 0, 0), 10) == 15 and wr.level_at((3, 0, 0), 10) == 14
       and pis.look_at_frame(15) == "S" and pis.look_at_frame(14) == "R", "end %.2f" % end)
    off = unsignal(30, wr, rep, lamp)
    ok("unsignal(): the lamp goes out 4 ticks after the repeater (30 + 4.8 + 4.8 = 39.6 -> frame 40)",
       abs(off - 39.6) < 1e-9 and lamp.lit_at(39) and not lamp.lit_at(40))
    ok("the lamp's light is on exactly while it is lit, and its own faces do not block it",
       lamp.light.light_linking.blocker_collection is not None
       and all(co.light_linking.link_state == "EXCLUDE"
               for co in lamp.light.light_linking.blocker_collection.collection_objects))
    # ---- API: names, circuit steps on rows / doors, objects
    k4 = kit(_blocks.World())
    k4.world.fill(0, 0, -1, 30, 30, -1, "stone")
    r1 = k4.piston_row([(x, 2, 0) for x in range(0, 3)], "north")
    r2 = k4.piston_row([(x, 6, 0) for x in range(0, 3)], "north")
    d1 = k4.piston_door([(10, 2, 0), (10, 2, 1)], "east")
    d2 = k4.piston_door([(10, 8, 0), (10, 8, 1)], "east")
    ok("two rows / doors with the default name get different names (Stage keys st.cast by name)",
       r1.name != r2.name and d1.name != d2.name and len({p.name for p in r1.pistons + r2.pistons}) == 6,
       "%s %s %s %s" % (r1.name, r2.name, d1.name, d2.name))
    wr4 = k4.wire([(x, 0, 0) for x in range(0, 3)], power=15)
    try:
        t_end = unsignal(30.0, wr4, r1)
        sig_ok = (abs(t_end - 30.0) < 1e-9 and not r1.extended_at(31.0) and wr4.level_at((0, 0, 0), 30) == 0
                  and abs(signal(50.0, r1) - 50.0) < 1e-9 and r1.extended_at(51.0))
    except AttributeError as e:
        sig_ok = False
        print("   ", e)
    d1.unpower(40.0)
    ok("rows and doors are circuit steps: unsignal(t, wire, row) retracts the row on t; signal(t, row) extends it; "
       "door.unpower(t) opens it (powered pistons extend: power closes)", sig_ok and d1.is_open(41.0))
    ok("every builder has .objects (row, door, block)", len(r1.objects) == 3 * 4 + 3 and len(d1.objects) == 2 * 4 + 2
       and k4.block("stone", (20, 20, 0)).objects[0].name.startswith("block_stone"))

    # ---- sky light: the same factor engine.sets draws a World cell with (floored at LIGHT_FLOOR)
    from . import sets

    k5 = kit(_blocks.World(), sky_light=0)
    f0_ = k5._dim(0)
    ok("kit(sky_light=0): parts get sets.lightmap(LIGHT_FLOOR = 3) = %.3f, not black (levels 0..3 alike; 9 and 10 "
       "alike as sets pairs them)" % f0_, abs(f0_ - sets.lightmap(3)) < 1e-9 and k5._dim(1) == f0_
       and k5._dim(3) == f0_ and abs(k5._dim(10) - sets.lightmap(9)) < 1e-9 and k5._dim(15) is None)
    w6 = _blocks.World()
    w6.fill(0, 0, -1, 6, 6, 3, "stone")
    for c in [(x, 3, z) for x in range(1, 4) for z in (0, 1)] + [(2, 4, 0), (2, 4, 1)]:
        w6.set(c[0], c[1], c[2], None)                 # an aisle (y 3) and a door cell behind it (2, 4)
    env6 = w6.sets_environment = sets.Environment(w6)           # (what sets.env(b) does in a hook)
    for c in [(x, 3, z) for x in range(1, 4) for z in (0, 1)] + [(2, 4, 0), (2, 4, 1)]:
        env6.light[c] = 0
        env6.columns.add((c[0], c[1]))
    env6.columns |= {(x, y) for x in range(0, 7) for y in range(0, 7)}
    wall = w6._state_at((1, 4, 0))                    # the wall beside the door: its face into the aisle
    wall_tint = [q[2][1] for q in wall.quads if q[3] == "south"]
    k6 = kit(w6)
    blk = k6.block("stone", (2, 4, 0), sky_light="auto")
    tints = {m.name.split("#")[-1][:6] for m in blk.object.data.materials}
    want = "%02x%02x%02x" % tuple(wall_tint[0]) if wall_tint and wall_tint[0] else None
    ok("a door block at sky_light='auto' next to a wall engine.sets baked dark gets the identical tint (%s)" % want,
       want is not None and tints == {want}, "%s vs %s" % (tints, want))

    # ---- dust colour film choices
    ok("dust_tint: the game's red, green raised only where the game has green (power 13-15), so the DISPLAYED hue "
       "is the game's after the look's grade (15: %s)" % (dust_tint(15),),
       all(dust_tint(l)[0] == wire_color(l)[0] and dust_tint(l)[2] == 0 for l in range(16))
       and all(dust_tint(l) == wire_color(l) for l in range(13)) and dust_tint(15)[1] > wire_color(15)[1])
    ok("dust_albedo: 1 up to the knee, DUST_ALBEDO at 15, and the diffuse red it leaves never falls with power",
       dust_albedo(0) == 1.0 and abs(dust_albedo(15) - DUST_ALBEDO) < 1e-9 and all(
           dust_albedo(l) * _srgb_to_linear(wire_color(l)[0] / 255.0) <= dust_albedo(l + 1)
           * _srgb_to_linear(wire_color(l + 1)[0] / 255.0) + 1e-9 for l in range(15)))
    print("[redstone] %d failed%s" % (len(failed), ": " + "; ".join(failed) if failed else ""))
    return len(failed)


def _check_village():
    """The proof film in the real village: the hook is accepted, the parts build, the lever is in reach, the
    held torch's light follows the item."""
    failed = []

    def ok(label, cond, detail=""):
        if not cond:
            failed.append(label)
        print("%-4s %s%s" % ("OK" if cond else "FAIL", label, ("  [%s]" % detail) if detail else ""), flush=True)

    scene = _fresh()
    out = build_proof(scene)
    v = out["village"]
    ok("the proof set goes through the village hook with no problem and validates", not v.edit_problems
       and not v.validate(), "%s %s" % (v.edit_problems, v.validate()))
    reach, f = out["lever_reach"]
    info = out["parts"]["lever_pier"].reach_info
    ok("a player at lever.stand(): the plain swing passes %.2f block from the handle's middle (the swing tops out "
       "1.33 above his feet); flip_by(reach=True) lifts the arm %.0f degrees and the fist (0.25 wide) touches it (%.2f "
       "from its centre; over the "
       "whole swing at half frames %.2f at frame %g)" % (info["natural"], math.degrees(info["angle"]),
                                                          info["reached"], reach, f),
       info["natural"] < 0.45 and info["reached"] is not None and info["reached"] < 0.15 and reach < 0.15)
    st = out["stage"]
    sh = {x.name: x for x in out["film"].shots}
    steve = st.cast["steve"]
    f_lever = sh["lever"].frame_start
    before = {(fc.data_path, fc.array_index, kp.co.x) for fc in _root_fcurves(steve.head) for kp in fc.keyframe_points}
    lev2 = out["kit"].lever((5, 23, 0), "floor", "north")
    flip_by(steve, lev2, f_lever + 2, look=True)          # a click 2 frames after he is placed
    new_keys = sorted(k[2] for fc in _root_fcurves(steve.head) for kp in fc.keyframe_points
                      for k in [(fc.data_path, fc.array_index, kp.co.x)] if k not in before)
    ok("flip_by 2 frames after the player's place(): his head turn starts on the place() frame, not 6 frames "
       "before (no pre-roll into the shot before)", new_keys and min(new_keys) >= f_lever - 1e-6,
       "new head keys %s, placed on %d" % ([round(x, 2) for x in new_keys[:4]], f_lever))
    lt = out["parts"]["lights_rtorch"]
    mats = [m for ob in lt.looks.looks[True] for m in ob.data.materials]
    ok("lit torch: its torch faces are drawn with back-face culling (Backfacing -> Transparent) and the glow",
       any(m.node_tree and any(n.type == "NEW_GEOMETRY" for n in m.node_tree.nodes) for m in mats)
       and all(m.get("mc_redstone_style") for m in mats if m.get("mc_texture") == "block/redstone_torch"),
       str([m.name for m in mats]))
    dm = [m for ob in out["parts"]["dust_cross"].objects for m in ob.data.materials]
    ok("dust: one opaque cut-out face per piece (a Principled material, not the two-sided 'up_thin' one that let the "
       "floor show through)", dm and all(any(n.type == "BSDF_PRINCIPLED" for n in m.node_tree.nodes) for m in dm),
       str([m.name for m in dm]))
    efe = out["stage"].cast["efe"]
    item = efe.item("right")
    L = bpy.data.objects.get(item.get("redstone_glow_light", "")) if item is not None else None
    states = []
    for fr, want_shown in ((out["shots"].get("x", 0) or out["frames"]["bench"][0], True),
                           (out["frames"]["sheet_a"], False)):
        scene.frame_set(fr)
        states.append((item.hide_render, L.hide_render if L else None))
    ok("held redstone torch: its light is on in its shot and off where the player is hidden (driver)",
       L is not None and all(a == b for a, b in states) and states[0][0] is False and states[1][0] is True,
       str(states))
    print("[redstone village] %d failed" % len(failed))
    return len(failed)


def _main(argv):
    if argv and argv[0] == "stills":
        names = argv[1:] or list(PROOFS)
        bad = [n for n in names if n not in PROOFS]
        if bad:
            print("unknown still(s) %s; names: %s" % (bad, ", ".join(PROOFS)))
            return 2
        _stills(names)
        return 0
    if argv and argv[0] == "study":
        for w in argv[1:] or ("floor",):
            light_study(w)
        return 0
    if argv and argv[0] == "palette":
        return 1 if palette_check(tuple(argv[1:]) or ("golden", "dusk")) else 0
    n = _check()
    if not argv or argv[0] != "quick":
        n += _check_village()
    return 1 if n else 0


if __name__ == "__main__":
    import sys

    sys.exit(_main(sys.argv[1:]))
