"""THE NETHER: a look without a sky, and the bastion sets of film six "Six Seconds" (stories/piglin.json).

New module; edits no other file. The look's colours and distances are read from the Java Edition 26.3 client (named
next to each number below); the strengths are film choices, tuned by rendering and measured (MEASURED). Blocks are
the game's models and textures through engine.blocks; the bridge's legs and the treasure pile are the game's own
bastion structure templates with the game's processor rules. Blender axes as everywhere: +X east, +Y north, +Z up,
1 block = 1 unit, characters face -Y at yaw 0, 24 fps.

HOW A NETHER FILM DECLARES ITS LOOK (render.py and films.lookdev.Stage accept both)
    ONE NETHER SKY (film six as written: every location is the Nether):
        bas = nether.build_bastion(scene)                        # all three sets, one World
        sky = nether.set_nether(scene, biome="nether_wastes")    # world + compositor, in place of look.set_time
        st = nether.Stage(scene, film, bas, sky)                 # (films.lookdev.Stage(scene, film, bas, sky) too)
        ... no SKIES in the film module (or SKIES = {}).
      render.Session builds look.set_time / setup_compositor only when the film left scene.world None or no node
      group named look.COMP_GROUP: set_nether provides both, so render.py keeps the Nether (proved: `$BPY -m
      engine.nether cli` renders out/test/nether_proof_2.5.png through render.main --still --zones).
    SEVERAL NETHER SKIES (another biome's fog per "world", as render.py's SKIES):
        SKIES = {"home": dict(preset="nether", biome="nether_wastes"),
                 "bridge": dict(preset="nether", biome="crimson_forest", haze=1.2)}      # keys: SKY_KEYS
        def build(scene, sky=None): ... st = nether.Stage(scene, film, bas, skies=SKIES, sky=sky)
      nether.Stage is films.lookdev.Stage whose build_sky also knows preset "nether" (any other preset goes to
      look.set_time as before); everything else (sky_segments, sky_change, dip, lights) is the Stage's own. Proved
      in-process with render.Session(film, sky=...) for three skies (`$BPY -m engine.nether skies`); render.py's
      one-process-per-sky command line was NOT run on it (it needs a films/<name>.py on disk).
    Never call look.set_time after set_nether (it would replace the Nether's world and lamps).

PUBLIC API
    set_nether(scene, biome="nether_wastes", ambient=None, lift=None, under=None, under_color=None, haze=None,
               bloom=None, vignette=None, grade=None, fog_color=None, compositor=True) -> dict
        The Nether in place of look.set_time + look.setup_compositor. No sun, moon, stars or clouds. Camera rays
        see the biome's fog colour (the game clears to it: skybox "none"); every other ray sees the ambient fill
        (the game's #302821 at half its saturation, x NETHER_LOOK fill); four shadowless lamps from above (`lift`:
        the game's ambient is not occluded); four shadowless warm lamps 27 degrees below the horizon (`under`: the
        lava sea's glow on undersides and walls, in the game's block-light tint #FFD88C). The compositor
        (setup_compositor) mixes the game's fog over everything: none up to 10 blocks, the fog colour at 96,
        linear in the distance (Mist pass), then bloom, grade, vignette and look.py's highlight shoulder.
        ambient / lift / under / haze / bloom scale NETHER_LOOK (1 = as tuned; haze 0 = no fog). biome: a key of
        FOG_COLORS (a bastion stands in BASTION_BIOMES). Returns dict(world, fog_color, fill, under, lift,
        bounce=under, preset='nether', biome, sun=None, moon=None, key=None, ...): st.sky for a Stage.
    setup_compositor(scene, bloom=1.0, vignette=0.35, grade="nether", haze=1.0, fog_color=None)
        Only the compositor group look.COMP_GROUP (set_nether calls it).
    Stage(scene, film, v, sky=None, skies=None) -> films.lookdev.Stage that also builds preset "nether" skies.
    build_sky(scene, spec) / stage_class()       what that Stage uses
    build_bastion(scene, layout=None, sets=("home", "bridge", "treasure"), seed=6, name="bastion",
                  lantern_watts=None) -> Bastion
        The three sets in one World, 400 blocks apart (ORIGINS; the game's fog is total at 96, so no set sees
        another). layout = {"home" | "bridge" | "treasure": (x, y, z) set origin, "pit": (x, y) the pit's SW cell
        in home coordinates}; an unknown key raises KeyError. lantern_watts: each lantern's point light (default
        LANTERN_WATTS 200 W; Stage.lights scales it per shot). Build: 0.5-0.9 s, about 10,500 faces.
    Bastion (the Village-shaped handle films.lookdev.Stage and the engine modules expect)
        world, collection, anchors, yaws, paths, doors {} , lantern_lights, lights {group: [lights]}, cutaways,
        sets {set: dict(origin, bounds, lights=dict(near, radius), anchors, cameras)}, cameras {name: dict(pos,
        target, lens, fstop, beats, note, set)}, lava {name: fixtures Fluid | Light}, chests, pit_blocks, pit_last,
        pit_cells, pillar, whole, face_count, edit_problems
        ground(x, y) / set_lantern_energy(scale, groups) / only_lights_near(point, radius) / cutaway(name, hide,
        frame) / validate()                    as the Village's
        lights_for(set_name) -> dict(near, radius)      st.lights(s, 1.0, **bas.lights_for("home")): that set only
        pit_open(shot, keep=())                 the 2 x 2 pit is dug in this shot (see THE PIT)
        pit_state(frame) -> 'whole' | 'open' | 'digging'
    load_template(name, processor=None, seed=0, keep_lava=False) -> engine.structures.Template
        A bastion piece ("bridge/legs/leg_0", "treasure/bases/centers/center_0", ...) with its pool's processor
        rules applied (PIECES, PROCESSORS; degrade()); read from assets/mc/data/minecraft/structure/bastion/ when
        it exists, else from the client jar ($MC_CLIENT_JAR or JAR_CANDIDATES): template_source() says which.
    check_still(scene, image_path, heroes=()) -> report     the Nether palette checks (see CHECKS)
    fog_amount(distance) / lightmap(level, gamma=0.5)       the game's fog factor and Nether lightmap colour
    register_proof_film() / render_proofs(names) / render_maps()    the proofs (SELF-TEST)
    Constants: FOG_COLORS, BASTION_BIOMES, FOG_START 10, FOG_END 96, AMBIENT_LIGHT_COLOR "#302821",
    AMBIENT_LIGHT 0.1, SKY_LIGHT_FACTOR 0, CARDINAL_SHADE, BLOCK_LIGHT_TINT "#ffd88c", BLOCK_FACTOR 1.4,
    LIGHT_LEVEL, NETHER_LOOK, AO_DISTANCE 5, GRADES, SKY_KEYS, HOME, BRIDGE, TREASURE, ORIGINS, LANTERN_WATTS.

WHAT THE GAME DOES (read from the 26.3 jar; nothing is copied into the project)
    data/minecraft/dimension_type/the_nether.json: has_skylight false, has_ceiling true, skybox "none",
    ambient_light 0.1, attributes visual/ambient_light_color #302821 (the overworld: #0a0a0a), sky_light_factor 0,
    fog_start_distance 10, fog_end_distance 96, cardinal_light "nether". shaders/core/lightmap.fsh: colour =
    AmbientColor + block light mix(#FFD88C, white, 0.9 (2l - 1)^2) * l / (4 - 3l) * 1.4 (+ flicker), no sky term
    in the Nether: everything is lit by blocks (lava, lantern, fire, glowstone 15; torch 14; soul lantern 10;
    magma 3), and a block in no light sits at the ambient: lightmap(0) = (0.38, 0.31, 0.26) x texture at the
    default brightness. fog.glsl / AtmosphericFogEnvironment: fog = 0 up to 10 blocks, 1 at 96, linear over the
    spherical distance, in the biome's fog colour (worldgen/biome/*.json visual/fog_color: nether_wastes #330808,
    crimson_forest #330303, warped_forest #1a051a, soul_sand_valley #1b4745, basalt_deltas #685f70); a bastion
    stands in the first four (tags/worldgen/biome/has_structure/bastion_remnant.json). CardinalLighting.NETHER
    shades faces down 0.9, up 0.9, north / south 0.8, east / west 0.6 (overworld: down 0.5): undersides are not
    dark in the Nether. Bastion processors (worldgen/processor_list): bastion_generic_degradation turns 30 % of
    polished blackstone bricks cracked, 30 % of gold blocks cracked bricks, half the gilded blackstone plain, 1 %
    of blackstone gilded; rampart_degradation 40 % cracked; bridge 30 %; treasure_rooms 35 %.

THE SETS (cells and anchors in Blender coordinates; the home set's origin is (0, 0, 0), so its numbers are world
numbers; every floor is at z 0; bas.anchors["..."] / bas.yaws["..."] / bas.cameras["..."])
    HOME (one fixed layout, every home shot; built block by block in the bastion palette, the game's processors on
    walls and floor): a narrow deep courtyard, floor x 0..8, y -2..17, walls 10 high (north 12) with polished
    basalt columns and crenellations, a broken parapet on the open south edge over the void, the lava sea 29
    below (glow only). The north (far) wall: the GATEWAY x 3..5, 5 high, basalt jambs, chiseled lintel, arched
    corners; beyond it the ENTRANCE CORRIDOR y 21..32 (interior x 2..6, roofed at z 5) with lava channels along
    both walls and a lava wall closing it at y 33: the orange glow through the gateway, a silhouette's backlight
    and the corridor key light (fixtures lava at the game's block-light colour + an area light on the lava wall).
    The GUARD STAIR x 0..1 rises north along the west wall (y 6..9) to the LANDING x 0..2, y 10..17, standing
    height 4, right beside the gateway's west jamb. The GOLD WALL: 21 gold blocks in the east wall's inner face (x
    9, y 7..13, z 0..2), basalt-framed, with the one-block blackstone STEP in front of it (x 8, y 7..13, top z 1).
    The PIT: cells x 3..4, y 4..5, two deep, in a patch of plain blackstone (x 1..7, y 2..8: never gilded, never
    gold), floor z -2. Lanterns (light groups): home_landing (over the landing), home_gate (two, either side of the
    gateway, one over the landing's corner), home_gold (two, over the step), home_pit (low on the west wall).
    Anchors: home_landing (the brute on guard, in profile from the gate frame, yaw east), home_landing_edge (beat 1,
    facing the 'landing' camera), home_stair_foot, home_gateway (in the gateway facing out: beats 17 / 18),
    home_corridor, home_entry (a runner's start by the lava wall), home_gold_1..4 (y 7.6 / 9.2 / 10.8 / 12.4, x 7.3,
    yaw east: facing the gold), home_step_1..4_item (the step's top in front of each: an ingot for beat 21),
    home_gold_target, home_pit_center, home_pit_1..4 (the pit floor's four places), home_rim_w / _s / _e / _n
    (standing at the rim, facing it), home_pit_drop_1..3 (0.3 past the rim: piglins.Piglin.fall from there),
    home_boot_mark (the skid stops here, beat 5), home_flash (beat 16), home_center. Paths: home_run_in (lava wall
    -> gateway -> boot mark), home_to_rim, home_stair_up (to home_landing), home_pit_walk_1..3 (gold places ->
    drop points). Cameras: gate (beats 3 18 19 23: 22 mm from the south end, low), landing (1), ingot_row (2 21),
    boot (5), pit (6 20), rim_side (9 10), inside_gate (4), corridor (17), flash (16). Cutaways:
    home_corridor_roof, home_south_parapet (st.see_through / st.remove).
    THE PIT: its eight blackstone blocks are engine.breaking Breakables (bas.pit_blocks; NOT in the World), the
    set's mesh has the pit's walls behind them. Without a call every shot shows the floor whole.
        bas.pit_open(s)                                 # this shot: dug (beats 7-10, 20)
        bas.pit_open(s6, keep=[bas.pit_last.cell])      # beat 6: dug but its last block, which the film breaks:
        breaking.mine(runner, bas.pit_last, f, camera=s6)   # holding the iron pickaxe: 7 ticks, drops blackstone
      Every block is back on the shot's last frame + 1 unless the next shot opens the pit too; calls in any
      order give the same keys (tools/check_nether_stamp.py: only the dug shot's fingerprints change).
      PHYSICS: world=bas (piglins.barter / launch, mobs drops, breaking) sees the pit DUG; in shots where the
      floor is whole pass world=bas.whole, or an item dropped on the pit cells falls in.
      Checked (scratch test): the runner at home_rim_w mines bas.pit_last in 7 ticks; a piglin walking
      home_pit_walk_1 with ramp=(4, 0) and fall(end, -2.0) lands inside the pit; piglins.barter(lob=True) toward
      an explicit floor point beside the rim (e.g. home_rim_w + (-0.4, -0.6)) rests there. toward=<the runner>
      standing at the rim does NOT: its rest spot 0.45 m from his feet on the piglin's side lies over the open pit
      and the item is keyed floating there at z 0 (an engine.piglins issue, reported).
    BRIDGE (another bastion): a deck 5 wide (walkway x -1..1 of polished blackstone bricks, 30 % cracked as the
    game's bridge processor, low broken walls on the edges), y -8..44, between pairs of basalt pillars (y 2, 15,
    28, 41; x -4..-3 and 3..4) that rise from the lava sea 24 below (a lit lava glow) to 7 above the deck; the
    game's own bridge legs (bridge/legs/leg_0, leg_1) under it; ONE lantern on three chains from a beam over the
    deck (group bridge_lantern), 1 block above a brute's head at bridge_brute. The player's netherrack pillar:
    bas.pillar, three Breakables at (0, 19, 0..2) local, not in the World: register them per shot
    (for b in bas.pillar: st.cast[b.name] = b; then st.use(shot, *bas.pillar) from beat 13 on). Anchors:
    bridge_start, bridge_boot_mark, bridge_player (beat 12), bridge_brute (blocking, under his lantern, facing
    the runner), bridge_middle, bridge_pillar_foot (facing it), bridge_pillar_top (standing height 3),
    bridge_flash. Cameras: bridge_boot (11), bridge_shoulder (12), bridge_pillar (13), bridge_profile (14),
    bridge_top (15), bridge_flash (16), bridge_wide.
    TREASURE (a third bastion's corner): blackstone walls with basalt columns (treasure_rooms processor), the game's
    treasure-room centre treasure/bases/centers/center_0 (the gold pile with its chest) sunk one block, a heap of
    loose gold blocks right of the brute's place and a chest left of it (engine.fixtures chests), two lanterns
    (group treasure). Anchor treasure_flash; cameras treasure_flash (16), treasure_wide.
    THE FLASH CUTS (beat 16): home_flash / bridge_flash / treasure_flash with the cameras of the same names: the
    camera is always 5 blocks in front of the brute at 1.45, 35 mm, so he stays locked in the frame.
    LIGHT PER SHOT: st.lights(s, scale, groups={"home_gold": 1.5, ...}, **bas.lights_for("home")): lanterns of the
    other sets are off. The lava lights (bas.lava: fixtures Fluids with .lights, .level(frame, scale),
    .flicker(f0, f1, at=...); "home_lava_wall_light" is a plain area Light) are not touched by Stage.lights: the
    lava flicker of beat 18 is bas.lava["home_channels"].flicker(f0, f1).

MEASURED (540x960, 16 samples, motion blur and depth of field, through render.Session; check_still)
    gate (beat 3): gold rgb(170,135,39) hue 44 s 0.77; unlit blackstone 24-33 of 255; the brute on the landing x 34
    %, y 39 %; the piglins at x 66-73 %. landing (1): brute luminance 60 vs blackstone 31 (x 1.9). ingot_row (2 /
    21): gold hue 43, piglin skin rgb(120,76,52) hue 21 s 0.57 (texture hue 5-15, s 0.25-0.45: warmer and more
    saturated under the lanterns, still pink-tan), brute x 3.1. bridge (12): Steve's shirt hue 171 (palette_check
    floor 170: AT the limit), brute x 1.65. treasure (16): gold hue 45, brute x 2.45. bridge_wide: the brute 50
    blocks away is only x 1.47 (a tiny figure; give him his lantern up close-ups). At full saturation the game's
    ambient #302821 turned the shirt green (hue 166) and the lava lights at a shader-pack orange (1, 0.62, 0.32)
    made skin s 0.61: hence ambient_sat 0.5 and the game's own block-light tint for lava. A 540x960 still takes
    10-23 s on 2 threads of the shared machine.
    CHECKS: check_still adds "gold reads as gold" (lit gold_block hue 38-58, s >= 0.45), "brute separates from
    blackstone" (his median luminance >= 1.5 x the blackstone's in the frame, and >= 25), "piglin skin stays pink"
    (hue 0-30, s <= 0.62) to tools/palette_check's. Of palette_check's own checks only Steve's (pants, shirt) and
    the heroes' safe area apply in a bastion: "stone not magenta" has no cobblestone / stone / stone bricks to
    measure (and lava-lit stone fails it by design: fixtures' notes), "robe hue" and "face saturation" need
    villagers, "planks" oak, "plants lit like the ground" grass: none of them exists in the Nether.

NOT THE GAME
    The fog is a compositor mix over the Mist pass (the game fogs each vertex); the frame clears to the fog
    colour, as the game's. The ambient is half as saturated as #302821 and partly occluded (Fast GI, AO 5 blocks);
    the lift lamps put back a share without occlusion. The under-glow lamps are a film choice (the game has no
    lava-sea light at a distance). Lantern light falls off as smoothed inverse square, not the game's one level per
    block. Magma blocks do not glow (engine.blocks.EMISSIVE has no magma); none is used. The home courtyard,
    bridge deck, pillars and treasure walls are built block by block in the bastion palette (no vanilla piece has
    the story's fixed layout); the legs and the treasure pile are vanilla pieces.

SELF-TEST
    $BPY -m engine.nether                    numbers and invariants, no rendering (about 5 s; exit 1 on a failure)
    $BPY -m engine.nether gate landing ...   proof stills through render.Session -> out/test/nether_<name>.png,
                                             each measured by check_still; names: PROOFS (landing ingot_row gate
                                             gate_18 pit bridge bridge_wide treasure); `proofs` = all (about 2 min)
    $BPY -m engine.nether map                top-down maps with anchors and cameras: out/test/nether_map_<set>.png
    $BPY -m engine.nether cli                render.py's own command line on the proof film (--still 2.5 --zones)
    $BPY -m engine.nether skies              a three-biome SKIES film built sky by sky by render.Session
    $BPY -m tools.check_nether_stamp         fingerprints: equal in two processes; pit_open changes that shot only
"""
import math
import os
import types
import zipfile
import gzip

import bpy
import numpy as np
from mathutils import Vector

from . import look
from . import mcassets as mc
from . import props
from . import structures
from .blocks import World, new_collection, pos_hash

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ======================================================================================================
# THE GAME'S NETHER (read from the 26.3 client jar)
# ======================================================================================================
# data/minecraft/worldgen/biome/<biome>.json, attribute "minecraft:visual/fog_color"
FOG_COLORS = {
    "nether_wastes": "#330808",
    "crimson_forest": "#330303",
    "warped_forest": "#1a051a",
    "soul_sand_valley": "#1b4745",
    "basalt_deltas": "#685f70",
}
# data/minecraft/tags/worldgen/biome/has_structure/bastion_remnant.json: the biomes a bastion can stand in
BASTION_BIOMES = ("crimson_forest", "nether_wastes", "soul_sand_valley", "warped_forest")
# data/minecraft/dimension_type/the_nether.json
FOG_START = 10.0                 # attributes "minecraft:visual/fog_start_distance"
FOG_END = 96.0                   # attributes "minecraft:visual/fog_end_distance" (AtmosphericFogEnvironment.setupFog
#                                  also caps it at 96); fog.glsl linear_fog_value: 0 up to the start, 1 at the end,
#                                  linear between, over the SPHERICAL distance from the eye, mixed toward the fog colour
AMBIENT_LIGHT_COLOR = "#302821"  # attributes "minecraft:visual/ambient_light_color" (the overworld: #0a0a0a)
AMBIENT_LIGHT = 0.1              # "ambient_light" (kept by the dimension type; the 26.x lightmap uses the colour)
SKY_LIGHT_FACTOR = 0.0           # attributes "minecraft:visual/sky_light_factor": NO sky light reaches anything
HAS_SKYLIGHT, HAS_CEILING = False, True        # "has_skylight": false, "has_ceiling": true, "skybox": "none"
# net.minecraft.world.level.CardinalLighting.NETHER (the face shading of blocks: down, up, north, south, west, east);
# DEFAULT (overworld) is 0.5, 1.0, 0.8, 0.8, 0.6, 0.6: in the Nether an underside is NOT darker than a top
CARDINAL_SHADE = {"down": 0.9, "up": 0.9, "north": 0.8, "south": 0.8, "west": 0.6, "east": 0.6}
# shaders/core/lightmap.fsh + LightmapRenderStateExtractor.extract: colour = AmbientColor + SkyLightColor * sky *
# SkyFactor + mix(BlockLightTint, white, 0.9 * (2 l - 1)^2) * l / (4 - 3 l) * BlockFactor, BlockFactor = 1.4 + flicker
BLOCK_LIGHT_TINT = "#ffd88c"     # EnvironmentAttributes.BLOCK_LIGHT_TINT default (the Nether keeps it)
BLOCK_FACTOR = 1.4
# light levels (Blocks.*: lightLevel): what is a light in a bastion
LIGHT_LEVEL = {"lantern": 15, "lava": 15, "fire": 15, "glowstone": 15, "torch": 14, "soul_lantern": 10,
               "magma_block": 3}


def lightmap(block_level, gamma=0.5, ambient=AMBIENT_LIGHT_COLOR, factor=BLOCK_FACTOR):
    """The game's lightmap colour (display space, 0..1) for a block light level 0..15 in the Nether (no sky light):
    lightmap.fsh with the brightness slider `gamma` (0 = Moody, 0.5 = the default, 1 = Bright)."""
    amb = np.array([int(ambient[i:i + 2], 16) / 255.0 for i in (1, 3, 5)])
    tint = np.array([int(BLOCK_LIGHT_TINT[i:i + 2], 16) / 255.0 for i in (1, 3, 5)])
    lv = max(0, min(15, int(block_level))) / 15.0
    bright = lv / (4.0 - 3.0 * lv) * factor
    col = amb + (tint + (1.0 - tint) * 0.9 * (2.0 * lv - 1.0) ** 2) * bright
    col = np.clip(col, 0.0, 1.0)
    m = max(col.max(), 1e-9)
    inv = 1.0 - m
    not_gamma = col * ((1.0 - inv ** 4) / m)
    return col * (1.0 - gamma) + not_gamma * gamma


def fog_amount(distance, start=FOG_START, end=FOG_END):
    """How much of the fog colour the game mixes over something `distance` blocks from the eye (0..1)."""
    if distance <= start:
        return 0.0
    if distance >= end:
        return 1.0
    return (distance - start) / (end - start)


# ======================================================================================================
# THE LOOK: set_nether (the Nether's engine.look.set_time + setup_compositor)
# ======================================================================================================
# What the game gives (above) and what this look makes of it. The film choices are the strengths, tuned by rendering
# (MEASURED in the module docstring); the colours and distances are the game's.
NETHER_LOOK = dict(
    fill=5.0,                    # the ambient: AMBIENT_LIGHT_COLOR (scene-linear) x fill is what a surface open to
    #                              every side receives (world light, occluded within AO_DISTANCE, as Fast GI does)
    lift=0.30,                   # ... and this share of it again from four shadowless lamps (the game's ambient is
    #                              not occluded at all: the floor of a pit or a roofed corridor is not black)
    under=0.30,                  # the lava sea's glow from below: four shadowless lamps 27 degrees under the horizon
    under_color=(1.0, 0.847, 0.549),  # the game's block-light tint #FFD88C (lava light IS block light); an underside
    #                              receives `under`, a wall half of it, a floor nothing
    ambient_sat=0.5,             # the ambient colour's saturation kept (the game's #302821 is hue 30, s 0.31: at full
    #                              strength it turned Steve's teal shirt green and piglin pink orange; see MEASURED)
    haze=1.0,                    # x the game's fog: 0 up to FOG_START, the fog colour at FOG_END (linear)
    bloom=1.0, vignette=0.35, grade="nether",
)
AO_DISTANCE = 5.0                # reach of the Fast GI occlusion of the fill (the village look uses 8)
GRADES = dict(look.GRADES)
GRADES["nether"] = dict(lift=(1.0, 1.0, 1.0), gamma=(1.0, 1.0, 1.0), gain=(1.0, 1.0, 1.0), saturation=1.0)
SKY_KEYS = ("biome", "ambient", "lift", "under", "under_color", "haze", "bloom", "vignette", "grade", "fog_color")


def _lin(hex_str, mul=1.0):
    return look._lin(hex_str, mul)


def _nether_world(scene, name, fog_lin, fill_lin):
    """World: camera rays see the fog colour (the game clears the frame to it: skybox 'none'); every other ray sees
    the ambient fill. Mist = the game's linear fog distances; the 'sky' AOV look.py writes is kept (always 1)."""
    old = bpy.data.worlds.get(name)
    if old is not None:
        bpy.data.worlds.remove(old)
    world = bpy.data.worlds.new(name)
    world.use_nodes = True
    nt = world.node_tree
    nt.nodes.clear()
    N, L = nt.nodes.new, nt.links.new
    lp = N("ShaderNodeLightPath")
    pick = N("ShaderNodeMix")
    pick.data_type = "RGBA"
    pick.name = "nether_pick"
    pick.inputs[6].default_value = (*fill_lin, 1.0)
    pick.inputs[7].default_value = (*fog_lin, 1.0)
    L(lp.outputs["Is Camera Ray"], pick.inputs[0])
    bg = N("ShaderNodeBackground")
    bg.name = "look_background"
    bg.inputs["Strength"].default_value = 1.0
    L(pick.outputs[2], bg.inputs["Color"])
    out = N("ShaderNodeOutputWorld")
    L(bg.outputs[0], out.inputs["Surface"])
    aov = N("ShaderNodeOutputAOV")
    aov.name = "look_sky_aov"
    aov.aov_name = look.SKY_AOV
    aov.inputs["Value"].default_value = 1.0
    look._ensure_sky_aov(scene)
    try:
        world.cycles.sampling_method = "MANUAL"
        world.cycles.sample_map_resolution = 64          # a constant colour: nothing to importance-sample
    except (AttributeError, TypeError):
        pass
    world.light_settings.distance = AO_DISTANCE
    world.light_settings.ao_factor = 1.0
    ms = world.mist_settings
    ms.use_mist = True
    ms.start, ms.depth = FOG_START, FOG_END - FOG_START
    ms.falloff = "LINEAR"
    scene.world = world
    return world


def _shadowless_suns(col, name, color, strength, rise_deg):
    """Four shadowless sun lamps from the diagonals, `rise_deg` above (+) or below (-) the horizon: a face turned
    toward that half of the sky receives `strength` (look.py's ground-bounce trick)."""
    out = []
    rise = math.radians(abs(rise_deg))
    if strength <= 0:
        return out
    for i in range(4):
        data = bpy.data.lights.new("look_%s" % name, "SUN")
        data.color = tuple(color)
        data.energy = strength / (4.0 * math.sin(rise))
        data.angle = math.radians(40.0)
        data.use_shadow = False
        try:
            data.specular_factor = 0.0
        except (AttributeError, TypeError):
            pass
        ob = bpy.data.objects.new("look_%s_%d" % (name, i), data)
        a = math.radians(45.0 + 90.0 * i)
        z = math.sin(rise) * (1.0 if rise_deg > 0 else -1.0)
        source = Vector((math.cos(a) * math.cos(rise), math.sin(a) * math.cos(rise), z))
        ob.rotation_euler = source.to_track_quat("Z", "Y").to_euler()
        col.objects.link(ob)
        out.append(ob)
    return out


def set_nether(scene, biome="nether_wastes", ambient=None, lift=None, under=None, under_color=None, haze=None,
               bloom=None, vignette=None, grade=None, fog_color=None, compositor=True):
    """The Nether's look for a film, in place of engine.look.set_time + setup_compositor: no sun, moon, stars or
    clouds; the frame cleared to the biome's fog colour; the game's warm ambient light everywhere; a warm glow from
    below (the lava sea); the game's fog (none up to 10 blocks, the fog colour at 96) as a compositor haze; bloom,
    grade, vignette and look.py's highlight shoulder. biome: a key of FOG_COLORS (bastions stand in BASTION_BIOMES).
    ambient / lift / under / haze / bloom scale NETHER_LOOK (1.0 = as tuned); grade 'nether' | look.GRADES names;
    fog_color '#rrggbb' overrides the biome's. Returns a dict like set_time's (sun / moon / key are None)."""
    if biome not in FOG_COLORS:
        raise KeyError("biome %r: one of %s (a bastion stands in %s)" % (biome, sorted(FOG_COLORS), BASTION_BIOMES))
    P = dict(NETHER_LOOK)
    k_amb = 1.0 if ambient is None else float(ambient)
    k_lift = 1.0 if lift is None else float(lift)
    k_under = 1.0 if under is None else float(under)
    k_haze = 1.0 if haze is None else float(haze)
    fog_hex = fog_color or FOG_COLORS[biome]
    fog_lin = _lin(fog_hex)
    amb = np.array(_lin(AMBIENT_LIGHT_COLOR))
    lum = float(amb @ np.array([0.2126, 0.7152, 0.0722]))
    fill_lin = tuple(float(v) for v in (lum + (amb - lum) * P["ambient_sat"]) * P["fill"] * k_amb)
    col = look._clear_sky(scene)                     # (also removes a set_time sky built before)
    world = _nether_world(scene, "look_world_nether_" + biome, fog_lin, fill_lin)
    # a shadowless sun of irradiance S gives a facing surface albedo * S / pi: S = pi * fill * lift matches `lift`
    # of the fill's radiance (in the ambient colour, normalised to its red channel)
    amb_norm = tuple(c / fill_lin[0] for c in fill_lin)
    lift_lamps = _shadowless_suns(col, "nether_lift", amb_norm, math.pi * fill_lin[0] * P["lift"] * k_lift, 50.0)
    uc = tuple(under_color) if under_color is not None else P["under_color"]
    under_lamps = _shadowless_suns(col, "nether_under", uc, P["under"] * k_under, -27.0)
    for vl in scene.view_layers:
        vl.use_pass_mist = True
    scene["look_preset"] = "nether"
    scene["nether_biome"] = biome
    scene["look_haze_color"] = list(fog_lin)
    scene["look_haze_amount"] = float(k_haze * P["haze"])
    if compositor:
        setup_compositor(scene, bloom=P["bloom"] if bloom is None else bloom,
                         vignette=P["vignette"] if vignette is None else vignette,
                         grade=P["grade"] if grade is None else grade, haze=k_haze * P["haze"], fog_color=fog_lin)
    return {"sun": None, "moon": None, "key": None, "sun_sprite": None, "moon_sprite": None, "stars": None,
            "clouds": None, "world": world, "key_dir": Vector((0.0, 0.0, -1.0)), "preset": "nether", "biome": biome,
            "bounce": under_lamps, "under": under_lamps, "lift": lift_lamps, "fog_color": fog_lin, "fill": fill_lin}


def setup_compositor(scene, bloom=1.0, vignette=0.35, grade="nether", haze=1.0, fog_color=None):
    """The compositor group engine.look.COMP_GROUP for the Nether: the game's fog over everything (Mist pass with
    FOG_START / FOG_END, linear, in the fog colour) x haze, bloom, grade, vignette, look.py's highlight shoulder.
    render.py keeps it (it only builds look.setup_compositor when no group of that name exists)."""
    fog = tuple(fog_color) if fog_color is not None else tuple(scene.get("look_haze_color", _lin(FOG_COLORS["nether_wastes"])))
    r = scene.render
    r.use_compositing = True
    try:
        r.compositor_device = "CPU"
    except (AttributeError, TypeError):
        pass
    for vl in scene.view_layers:
        vl.use_pass_mist = True
    look._ensure_sky_aov(scene)
    old = bpy.data.node_groups.get(look.COMP_GROUP)
    if old is not None:
        bpy.data.node_groups.remove(old)
    tree = bpy.data.node_groups.new(look.COMP_GROUP, "CompositorNodeTree")
    tree.interface.new_socket(name="Image", in_out="OUTPUT", socket_type="NodeSocketColor")
    tree["look_haze_fixed"] = True
    N, L = tree.nodes.new, tree.links.new
    rl = N("CompositorNodeRLayers")
    rl.scene = scene
    image = rl.outputs["Image"]
    amount = N("ShaderNodeMath")
    amount.name = "look_haze_amount"
    amount.operation = "MULTIPLY"
    amount.use_clamp = True
    amount.inputs[1].default_value = float(haze)
    mist = rl.outputs.get("Mist")
    if mist is not None:
        L(mist, amount.inputs[0])
    else:
        amount.inputs[0].default_value = 0.0
    hz = N("ShaderNodeMix")
    hz.name = "look_haze"
    hz.data_type = "RGBA"
    hz.blend_type = "MIX"
    hz.inputs[7].default_value = (*fog, 1.0)
    L(amount.outputs[0], hz.inputs[0])
    L(image, hz.inputs[6])
    image = hz.outputs[2]
    if bloom > 0:
        gl = N("CompositorNodeGlare")
        gl.name = "look_bloom"
        for k, v in (("Type", "Bloom"), ("Quality", "High"), ("Threshold", 1.0), ("Smoothness", 0.5),
                     ("Clamp", True), ("Maximum", 12.0), ("Strength", min(1.0, 0.42 * bloom)), ("Saturation", 1.0),
                     ("Size", 0.62)):
            look._set_input(gl, k, v)
        L(image, gl.inputs["Image"])
        image = gl.outputs["Image"]
    g = GRADES[grade]
    cb = N("CompositorNodeColorBalance")
    cb.name = "look_grade"
    look._set_input(cb, "Type", "Lift/Gamma/Gain")
    look._set_input(cb, "Color Lift", (*g["lift"], 1.0))
    look._set_input(cb, "Color Gamma", (*g["gamma"], 1.0))
    look._set_input(cb, "Color Gain", (*g["gain"], 1.0))
    L(image, cb.inputs["Image"])
    hs = N("CompositorNodeHueSat")
    hs.name = "look_saturation"
    look._set_input(hs, "Saturation", g["saturation"])
    L(cb.outputs["Image"], hs.inputs["Image"])
    image = hs.outputs["Image"]
    if vignette > 0:
        ic = N("CompositorNodeImageCoordinates")
        L(rl.outputs["Image"], ic.inputs["Image"])
        ctr = N("ShaderNodeVectorMath")
        ctr.operation = "MULTIPLY_ADD"
        ctr.inputs[1].default_value = (1.4142, 1.4142, 0.0)
        ctr.inputs[2].default_value = (-0.7071, -0.7071, 0.0)
        L(ic.outputs["Normalized"], ctr.inputs[0])
        ln = N("ShaderNodeVectorMath")
        ln.operation = "LENGTH"
        L(ctr.outputs["Vector"], ln.inputs[0])
        vm = N("ShaderNodeMapRange")
        vm.name = "look_vignette"
        vm.interpolation_type = "SMOOTHSTEP"
        vm.inputs["From Min"].default_value = 0.30
        vm.inputs["From Max"].default_value = 1.05
        vm.inputs["To Min"].default_value = 1.0
        vm.inputs["To Max"].default_value = 1.0 - float(vignette)
        L(ln.outputs["Value"], vm.inputs["Value"])
        mul = N("ShaderNodeMix")
        mul.data_type = "RGBA"
        mul.blend_type = "MULTIPLY"
        mul.inputs[0].default_value = 1.0
        L(image, mul.inputs[6])
        L(vm.outputs["Result"], mul.inputs[7])
        image = mul.outputs[2]
    image = look._shoulder(tree, image)
    out = N("NodeGroupOutput")
    L(image, out.inputs[0])
    look._assign_compositor(scene, tree)
    return tree


# ---- films.lookdev.Stage with SKIES whose preset is "nether" ---------------------------------------------------
def build_sky(scene, spec):
    """Build one entry of a film's SKIES: preset 'nether' (keys: SKY_KEYS) through set_nether, any other preset
    through films.lookdev.Stage.build_sky (engine.look). Returns the sky dict."""
    spec = dict(spec)
    if spec.get("preset") != "nether":
        from films import lookdev
        return lookdev.Stage.build_sky(scene, spec)
    spec.pop("preset")
    kw = {k: spec.pop(k) for k in SKY_KEYS if k in spec}
    if spec:
        raise TypeError("unknown Nether sky setting(s) %s; known: preset, %s" % (sorted(spec), ", ".join(SKY_KEYS)))
    return set_nether(scene, **kw)


_STAGE_CLASS = None


def stage_class():
    """films.lookdev.Stage whose SKIES may hold Nether entries (preset 'nether'); otherwise exactly that Stage."""
    global _STAGE_CLASS
    if _STAGE_CLASS is None:
        from films import lookdev

        class NetherStage(lookdev.Stage):
            """films.lookdev.Stage that also builds SKIES entries with preset 'nether' (engine.nether.set_nether)."""

            @classmethod
            def build_sky(cls, scene, spec):
                return build_sky(scene, spec)

        _STAGE_CLASS = NetherStage
    return _STAGE_CLASS


def Stage(scene, film, v, sky=None, skies=None):
    """A films.lookdev.Stage that accepts Nether skies: Stage(scene, film, bastion, skies=SKIES, sky=sky) with
    SKIES = {"home": dict(preset="nether", biome="nether_wastes"), ...} (keys SKY_KEYS), or one sky built by
    set_nether and handed over: Stage(scene, film, bastion, sky_dict)."""
    return stage_class()(scene, film, v, sky=sky, skies=skies)


# ======================================================================================================
# THE GAME'S BASTION TEMPLATES (data/minecraft/structure/bastion/**.nbt) and processors
# ======================================================================================================
# The project's assets/mc holds only the village structures (tools/fetch_assets.py KEEP). The bastion pieces are read
# where they are: assets/mc/data/minecraft/structure/bastion/ if a later fetch extracts them there, else straight out
# of the official client jar ($MC_CLIENT_JAR, or the copy this project was built with). Nothing is copied.
BASTION_DIR = os.path.join(structures.STRUCT_DIR, "bastion")
JAR_CACHE = os.path.join(os.environ.get("XDG_CACHE_HOME") or os.path.expanduser("~/.cache"), "minecraft-shorts",
                         "client-26.3.jar")     # where `$BPY -m tools.nether_fetch_jar` puts the jar by default
JAR_CANDIDATES = (
    os.environ.get("MC_CLIENT_JAR") or "",
    JAR_CACHE,
    os.path.join(ROOT, "assets", "mc", "client.jar"),
    # the copy this module was written with (one session's scratchpad: gone in any later session)
    "/tmp/claude-0/-home-user-Project-2-/be90bb9d-3fc7-572c-941a-ff79c8b6ef48/scratchpad/mc/client.jar",
)
# data/minecraft/worldgen/processor_list/<name>.json: RuleProcessor rules (input block, probability, output); the
# first rule whose random test passes replaces the block. Rules whose output is air (1 in 10,000) are left out here:
# a set must not get a random hole.
PROCESSORS = {
    "bastion_generic_degradation": [
        ("polished_blackstone_bricks", 0.3, "cracked_polished_blackstone_bricks"),
        ("gold_block", 0.3, "cracked_polished_blackstone_bricks"),
        ("gilded_blackstone", 0.5, "blackstone"),
        ("blackstone", 0.01, "gilded_blackstone")],
    "bridge": [
        ("polished_blackstone_bricks", 0.3, "cracked_polished_blackstone_bricks")],
    "treasure_rooms": [
        ("polished_blackstone_bricks", 0.35, "cracked_polished_blackstone_bricks"),
        ("chiseled_polished_blackstone", 0.1, "cracked_polished_blackstone_bricks"),
        ("gilded_blackstone", 0.5, "blackstone"),
        ("blackstone", 0.01, "gilded_blackstone")],
    "rampart_degradation": [
        ("polished_blackstone_bricks", 0.4, "cracked_polished_blackstone_bricks"),
        ("blackstone", 0.01, "cracked_polished_blackstone_bricks"),
        ("gold_block", 0.3, "cracked_polished_blackstone_bricks"),
        ("gilded_blackstone", 0.5, "blackstone"),
        ("blackstone", 0.01, "gilded_blackstone")],
    "high_wall": [
        ("polished_blackstone_bricks", 0.5, "cracked_polished_blackstone_bricks"),
        ("polished_blackstone_bricks", 0.3, "blackstone"),
        ("gilded_blackstone", 0.5, "blackstone")],
}
# the template pool each piece used here comes from, with its processor list (worldgen/template_pool/bastion/...)
PIECES = {
    "bridge/legs/leg_0": "bastion_generic_degradation",          # bridge/legs.json
    "bridge/legs/leg_1": "bastion_generic_degradation",
    "treasure/bases/centers/center_0": "treasure_rooms",         # treasure/bases/centers.json
    "treasure/bases/centers/center_1": "treasure_rooms",
    "treasure/bases/centers/center_2": "treasure_rooms",
    "treasure/bases/centers/center_3": "treasure_rooms",
}


def degrade(block_id, rules, cell, seed=0):
    """The block a processor list turns `block_id` into at `cell` (the game's RuleProcessor: the first rule whose
    input matches and whose random draw for this position passes wins)."""
    if isinstance(rules, str):
        rules = PROCESSORS[rules]
    for k, (inp, prob, out) in enumerate(rules):
        if block_id != inp:
            continue
        r = pos_hash(cell[0], cell[1], cell[2], salt=seed * 131 + k + 7) / 4294967296.0
        if r < prob:
            return out
    return block_id


def template_source(quiet=True):
    """Where the bastion templates are read from: ('dir', path) or ('jar', path); raises FileNotFoundError naming
    the fix. quiet=False prints it (build_bastion does, on every build)."""
    found = None
    if os.path.isdir(BASTION_DIR):
        found = ("dir", BASTION_DIR)
    else:
        for p in JAR_CANDIDATES:
            if p and os.path.isfile(p):
                found = ("jar", p)
                break
    if found is None:
        raise FileNotFoundError(
            "engine.nether: the game's bastion structure templates are not available (the bridge legs and the "
            "treasure pile are built from them). Fix: `$BPY -m tools.nether_fetch_jar` (puts the official 26.3 client "
            "jar in %s, checked against Mojang's SHA-1), or export MC_CLIENT_JAR=<the 26.3 client jar>, or add "
            "'data/minecraft/structure/bastion/' to tools/fetch_assets.py KEEP and run it again (then %s is read)."
            % (JAR_CACHE, BASTION_DIR))
    if not quiet:
        print("[nether] bastion templates from the %s %s" % ("directory" if found[0] == "dir" else "client jar", found[1]))
    return found


_TEMPLATES = {}


def load_template(name, processor=None, seed=0, keep_lava=False):
    """A bastion piece ('bridge/legs/leg_0', ...) as an engine.structures.Template (Minecraft axes; jigsaw blocks
    replaced by their final_state, air dropped) with its pool's processor list applied (PIECES, or `processor`).
    Lava is dropped unless keep_lava (fixtures draws lava; engine.blocks' own lava renders salmon)."""
    key = (name, processor, seed, keep_lava)
    if key in _TEMPLATES:
        return _TEMPLATES[key]
    kind, where = template_source()
    if kind == "dir":
        data = structures.read_nbt_file(os.path.join(where, name + ".nbt"))
    else:
        with zipfile.ZipFile(where) as z:
            raw = z.read("data/minecraft/structure/bastion/%s.nbt" % name)
        data = structures._read_nbt(gzip.decompress(raw) if raw[:2] == b"\x1f\x8b" else raw)
    rules = processor if processor is not None else PIECES.get(name)
    blocks = []
    for b in data["blocks"]:
        st = data["palette"][b["state"]]
        bname = (st.get("Name") or st.get("id")).replace("minecraft:", "")
        bprops = dict(st.get("Properties") or st.get("properties") or {})
        if bname == "jigsaw":
            bname, bprops = structures.parse_state(b.get("nbt", {}).get("final_state", "minecraft:air"))
        if bname in ("air", "structure_void", "cave_air") or (bname == "lava" and not keep_lava):
            continue
        x, y, z = b["pos"]
        if rules:
            bname = degrade(bname, rules, (x, y, z), seed)
        blocks.append((x, y, z, bname, bprops))
    t = structures.Template(name, tuple(data["size"]), blocks, None)
    _TEMPLATES[key] = t
    return t


# ======================================================================================================
# THE SETS
# ======================================================================================================
# Where the three sets stand (Blender cells of each set's local origin). 400 blocks apart: the game's fog is total at
# 96, so no set can see another; Bastion.lights_for(set) gives the near / radius that keep each shot's lights local.
ORIGINS = {"home": (0, 0, 0), "bridge": (400, 0, 0), "treasure": (-400, 0, 0)}
SETS = ("home", "bridge", "treasure")
LANTERN = {"hanging": "true", "waterlogged": "false"}
STANDING = {"hanging": "false", "waterlogged": "false"}
CHAIN = {"axis": "y", "waterlogged": "false"}
UP = {"axis": "y"}
FLAME_GLOW_GROUPS = ("block_lantern", "block_fire")
LANTERN_WATTS = 200.0            # a bastion lantern's point light (engine.props' lantern; Stage.lights scales it per shot)
PIT_FILL_WATTS = 12.0            # the pit's own shadowless fill (Bastion.pit_fill), on only in pit_open shots: the
#                                  game's ambient reaches a pit's floor unoccluded (MEASURED in the module docstring)


def _key_light(ob, steps):
    """Key a light's energy (on its data, which the frame fingerprint reads) and its hide_render as CONSTANT steps
    [(frame, watts)], replacing what was keyed before."""
    from .breaking import _keys

    steps = sorted((int(f), float(e)) for f, e in steps)
    if not steps:
        return
    frames = [f for f, _e in steps]
    _keys(ob.data, "energy", frames, [e for _f, e in steps], "CONSTANT")
    _keys(ob, "hide_render", frames, [0.0 if e > 0.0 else 1.0 for _f, e in steps], "CONSTANT")
    now = bpy.context.scene.frame_current
    e = next((e for f, e in reversed(steps) if f <= now), steps[0][1])
    ob.data.energy, ob.hide_render = e, e <= 0.0


def _yaw(direction):
    """Yaw of a character facing a compass direction ('north' ...) or an (dx, dy) vector."""
    if isinstance(direction, str):
        direction = {"north": (0, 1), "south": (0, -1), "east": (1, 0), "west": (-1, 0)}[direction]
    return math.atan2(direction[0], -direction[1])


def yaw_to(src, dst):
    """Yaw that makes a character at src (facing -Y at yaw 0) face dst."""
    return math.atan2(dst[0] - src[0], -(dst[1] - src[1]))


def project(cam_pos, cam_target, lens, point, aspect=9.0 / 16.0):
    """Where `point` lands in the frame of a camera at cam_pos aimed at cam_target (engine.shots: 36 mm sensor side
    vertical, no roll): (u, v) with u 0..1 left to right, v 0..1 top to bottom; None if it is behind the camera."""
    C, T, P = Vector(cam_pos), Vector(cam_target), Vector(point)
    f = (T - C).normalized()
    r = f.cross(Vector((0.0, 0.0, 1.0))).normalized()
    up = r.cross(f)
    d = P - C
    z = d.dot(f)
    if z <= 1e-6:
        return None
    return (0.5 + d.dot(r) / z * lens / (36.0 * aspect), 0.5 - d.dot(up) / z * lens / 36.0)


def sight_blocked(world, a, b, step=0.04):
    """The first block on the straight line a -> b that hides what is behind it: (distance, cell, block id) or
    None. Full cubes block; a wall block blocks within its post / connections and below 14 px; slabs, stairs,
    lanterns and chains are counted as clear."""
    n = max(1, int(math.dist(a, b) / step))
    for i in range(1, n):
        t = i / float(n)
        q = [a[k] + (b[k] - a[k]) * t for k in range(3)]
        c = tuple(int(math.floor(v)) for v in q)
        bid = world.block_id(*c)
        if not bid:
            continue
        fx, fy, fz = q[0] - c[0], q[1] - c[1], q[2] - c[2]
        if world.is_full_cube(*c) or (bid.endswith("_wall") and fz < 0.875 and
                                      (0.25 <= fx <= 0.75 or 0.25 <= fy <= 0.75)):
            return (round(math.dist(a, q), 2), c, bid)
    return None


class Bastion:
    """The built sets, shaped like engine.village.Village where films.lookdev.Stage and the other engine modules
    look (world, collection, anchors, yaws, paths, doors, lantern_lights, lights, cutaways, sets, ground()), plus
    the pit (pit_blocks, pit_open), the netherrack pillar (pillar), the lava bodies (lava), camera suggestions
    (cameras) and the physics world of the whole floor (whole)."""

    def __init__(self):
        self.world = None
        self.collection = None
        self.anchors = {}            # name -> (x, y, z): standing spots (z = walking surface) and look targets
        self.yaws = {}               # anchor name -> the yaw a character standing there should have
        self.paths = {}              # name -> [(x, y, z), ...]
        self.doors = {}              # (no doors in a bastion; Stage and the village tools expect the dict)
        self.bell = None
        self.beds = {}
        self.lantern_lights = []     # every lantern / fire point light (Stage.lights steps them per shot)
        self.lights = {}             # group -> [light objects]
        self.cutaways = {}           # name -> [objects]: Stage.see_through / Stage.remove
        self.objects = []
        self.sets = {}               # set name -> dict(origin, bounds, cameras, anchors, lights=dict(near, radius))
        self.cameras = {}            # name -> dict(pos, target, lens, fstop, beats, note)
        self.lava = {}               # name -> engine.fixtures Fluid (lava bodies and glows: .lights, level, flicker)
        self.pit_blocks = {}         # cell -> engine.breaking Breakable (the home pit, 2 x 2 x 2)
        self.pit_last = None         # the Breakable the player breaks on camera (beat 6)
        self.pillar = []             # the bridge's three netherrack blocks (Breakables; register them per shot)
        self.chests = {}             # name -> engine.fixtures Chest
        self.whole = None            # .world = the World with the pit FILLED (physics for whole-floor shots)
        self.face_count = 0
        self.edit_problems = []
        self.removed_doors = set()
        self.regrounded = []
        self.buildings = {}
        self.layout = {}
        self._pit_spans = []         # [(frame_start, frame_end, keep cells)]
        self._pit_keys = {}          # Breakable name -> frames this module keyed in its history
        self.pit_fill = None         # the pit's own weak fill light (on only in pit_open shots)
        self._pillar_spans = []      # [(frame_start, frame_end)] the netherrack pillar stands
        self._pillar_keys = {}
        self._flicker_spans = []

    # ---- Village-like helpers
    def ground(self, x, y, z_from=40, z_to=-40):
        """Walking surface z of the column at (x, y) (top of the highest solid block; slabs / stairs as
        blocks.World.surface), or None."""
        return self.world.surface(int(math.floor(x)), int(math.floor(y)), z_from, z_to)

    def set_lantern_energy(self, scale=1.0, groups=None):
        """Scale every lantern light (or those of some groups) relative to its built-in energy; 0 hides it."""
        for group, lights in self.lights.items():
            if groups is None or group in groups:
                for ob in lights:
                    ob.data.energy = ob["base_energy"] * scale
                    ob.hide_render = scale <= 0.0

    def only_lights_near(self, point, radius=30.0):
        """Keep only the lights within `radius` of `point` in the render (no keys); returns those left on."""
        on = []
        for ob in self.lantern_lights:
            far = radius is not None and math.dist(ob.location, point) > radius
            ob.hide_render = far
            if not far:
                on.append(ob)
        return on

    def lights_for(self, set_name):
        """dict(near=..., radius=...) for films.lookdev.Stage.lights: only that set's lanterns are on."""
        return dict(self.sets[set_name]["lights"])

    def cutaway(self, name, hide=True, frame=None):
        """Hide (or show) a removable section; with `frame` the visibility is keyed (constant) from that frame on."""
        for ob in self.cutaways[name]:
            ob.hide_render = hide
            ob.hide_viewport = hide
            if frame is not None:
                ob.keyframe_insert("hide_render", frame=frame)
                ob.keyframe_insert("hide_viewport", frame=frame)

    # ---- the pit (home set)
    def pit_open(self, shot, keep=()):
        """In this shot (a Shot, or (frame_start, frame_end)) the 2 x 2 pit is DUG: its eight blocks are gone, except
        the cells in `keep` (a cell, or a list; e.g. [bastion.pit_last.cell]), which stay until the film breaks them
        (engine.breaking.mine / break_block). Every block is back from the shot's last frame + 1 unless the next shot
        opens the pit too. Without a pit_open call a shot shows the whole floor. Any call order gives the same keys."""
        if not self.pit_blocks:
            raise ValueError("this Bastion has no pit (build_bastion(sets=...) without 'home')")
        f0, f1 = (shot.frame_start, shot.frame_end) if hasattr(shot, "frame_start") else (int(shot[0]), int(shot[1]))
        if keep and isinstance(keep[0], (int, float)):
            keep = [keep]
        keep = {tuple(int(c) for c in k) for k in keep}
        bad = [k for k in keep if k not in self.pit_blocks]
        if bad:
            raise ValueError("keep: %s is not a pit cell (pit cells: %s)" % (bad[0], sorted(self.pit_blocks)))
        self._pit_spans = [s for s in self._pit_spans if s[0] != f0] + [(f0, f1, frozenset(keep))]
        self._pit_rekey()

    def pit_state(self, frame):
        """'whole' | 'open' | 'digging' (some blocks kept for an on-camera break) at a frame, from pit_open calls."""
        for f0, f1, keep in self._pit_spans:
            if f0 <= frame <= f1:
                return "digging" if keep else "open"
        return "whole"

    def _pit_rekey(self):
        spans = sorted(self._pit_spans)
        starts = {f0 for f0, _f1, _k in spans}
        for cell, blk in self.pit_blocks.items():
            for f in self._pit_keys.get(blk.name, ()):        # forget what this module keyed before
                blk._there.pop(f, None)
            events = {}
            for f0, f1, keep in spans:
                if cell not in keep:
                    events[f0] = False
                if f1 + 1 not in starts:
                    events[f1 + 1] = True
            for f, v in events.items():
                blk._there[f] = v
            self._pit_keys[blk.name] = set(events)
            blk._rekey()
        # the pit's fill light: on exactly in the dug shots (the game's ambient is not occluded: a pit is not black)
        fill = self.pit_fill
        if fill is not None:
            ends = {f1 + 1 for _f0, f1, _k in spans} - starts
            ev = sorted([(f0, True) for f0 in starts] + [(f, False) for f in ends])
            steps = [(f, fill["base_energy"] if on else 0.0) for f, on in ev]
            _key_light(fill, [(steps[0][0] - 1, 0.0)] + steps)

    def pit_drop(self, piglins, frame, stagger=12, place=True):
        """Beat 6 in one call: piglin k (1..3) stands on home_pit_approach_k (one block outside the rim, facing it)
        and, from `frame` + (k - 1) * stagger, walks the block to home_pit_drop_k and falls to the pit floor (the
        game's gravity: 2 blocks in 8.4 frames). place=False: they are already there. The pit must be open then
        (pit_open). Returns [(walk start, step-off frame, landing frame)]. MEASURED with the defaults: steps off 13
        frames after its start, lands 9 frames later (frame + 22 / 34 / 46 for the three)."""
        out = []
        for k, p in enumerate(piglins, 1):
            path = self.paths["home_pit_approach_%d" % k]
            if place:
                p.place(frame, path[0], self.yaws["home_pit_approach_%d" % k])
            start = int(frame + (k - 1) * stagger)
            end = p.walk(start, path, ramp=(4, 0))
            land = p.fall(end, self.anchors["home_pit_center"][2])
            out.append((start, end, land))
        return out

    # ---- the netherrack pillar (bridge set): NOT built unless a call says so
    def pillar_in(self, shot):
        """The player's three-block netherrack pillar stands in this shot (a Shot or (frame_start, frame_end)); gone
        again from the shot's last frame + 1 unless the next shot has it too. Any call order gives the same keys."""
        f0, f1 = (shot.frame_start, shot.frame_end) if hasattr(shot, "frame_start") else (int(shot[0]), int(shot[1]))
        self._pillar_spans = [s for s in self._pillar_spans if s[0] != f0] + [(f0, f1)]
        self._pillar_rekey()

    def pillar_from(self, frame):
        """The pillar stands from `frame` on (beat 13 on: it was built there), in every later shot."""
        self.pillar_in((int(frame), 10 ** 7))

    def _pillar_rekey(self):
        spans = sorted(self._pillar_spans)
        starts = {f0 for f0, _f1 in spans}
        for blk in self.pillar:
            for f in self._pillar_keys.get(blk.name, ()):
                blk._there.pop(f, None)
            events = {f0: True for f0, _f1 in spans}
            events.update({f1 + 1: False for _f0, f1 in spans if f1 + 1 not in starts})
            blk._there.update(events)
            self._pillar_keys[blk.name] = set(events)
            blk._rekey()

    # ---- the corridor's lava glow (beat 18: "nothing moves but the flicker of the lava glow")
    def lava_flicker(self, f0, f1, amount=0.25, seed=0):
        """The home corridor's lava light unrest on frames f0..f1: the channel lights AND the lava wall's area light
        (home_lava_wall_light) together, the same factor on the same frame (engine.fixtures' slow three-sine
        unrest, CONSTANT per frame, keyed on the lights' data so the frame fingerprints follow). amount 0.25 = +-25
        %. The lava's own surfaces glow as before (their texture animates): what flickers is the light they throw
        on the jambs, the corridor walls and floor and a figure in the gateway. MEASURED: see the module docstring."""
        ch = self.lava.get("home_channels")
        wall = self.lava.get("home_lava_wall_light")
        if ch is None or wall is None:
            raise ValueError("this Bastion has no home corridor (build_bastion(sets=...) without 'home')")
        ch.flicker(f0, f1, amount=amount, seed=seed)
        self._flicker_spans = [s for s in self._flicker_spans if (s[0], s[1]) != (int(f0), int(f1))]
        self._flicker_spans.append((int(f0), int(f1)))
        frames = sorted({f for a, b in self._flicker_spans for f in range(a, b + 2)})
        base = wall["base_energy"]
        _key_light(wall, [(frames[0] - 1, base)] + [(f, base * ch.light_factor(f)) for f in frames])

    # ---- checks
    def validate(self):
        """Problems with the sets (empty = all good): anchors inside blocks, paths blocked, lights buried."""
        out = []
        w = self.world
        for name, pts in self.paths.items():
            for a, b in zip(pts[:-1], pts[1:]):
                n = max(1, int(math.dist(a, b) / 0.2))
                for i in range(n + 1):
                    t = i / n
                    x, y, z = (a[k] + (b[k] - a[k]) * t for k in range(3))
                    cx, cy = int(math.floor(x)), int(math.floor(y))
                    for cz in (int(math.floor(z + 0.3)), int(math.floor(z + 1.5))):
                        bid = w.block_id(cx, cy, cz)
                        if bid and w.is_solid(cx, cy, cz) and not bid.endswith(("_stairs", "_slab")):
                            out.append("path %s blocked at %s by %s" % (name, (round(x, 2), round(y, 2), round(z, 2)), bid))
                            break
        for name, (x, y, z) in self.anchors.items():
            if name.endswith(("_target", "_center", "_cam", "_top_target", "_item")):
                continue
            cx, cy = int(math.floor(x)), int(math.floor(y))
            for cz in (int(math.floor(z + 0.2)), int(math.floor(z + 1.2))):
                bid = w.block_id(cx, cy, cz)
                if bid and w.is_solid(cx, cy, cz) and not bid.endswith(("_stairs", "_slab")):
                    out.append("anchor %s inside %s" % (name, bid))
        for ob in self.lantern_lights:
            c = tuple(int(math.floor(a)) for a in ob.location)
            if w.block_id(*c) not in (None, "lantern", "soul_lantern", "fire") and w.is_full_cube(*c):
                out.append("light %s buried in %s" % (ob.name, w.block_id(*c)))
        return out + self.check_cameras()

    def check_cameras(self):
        """Problems with the camera suggestions (empty = all good): a camera inside a block; an anchor it `sees`
        whose shins (z + 0.35) or head (z + 1.75) fall outside its 9:16 frame or behind a block (full cubes, and the
        walls' posts and connections)."""
        out = []
        w = self.world
        for name, c in sorted(self.cameras.items()):
            cell = tuple(int(math.floor(v)) for v in c["pos"])
            if w.is_solid(*cell) or w.is_full_cube(*cell):
                out.append("camera %s inside %s at %s" % (name, w.block_id(*cell), cell))
                continue
            for an in c.get("sees", ()):
                an, _sep, part = an.partition(":")
                p = self.anchors[an]
                for what, dz in (("shins", 0.35), ("head", 1.75)):
                    if part and what != part:
                        continue
                    q = (p[0], p[1], p[2] + dz)
                    uv = project(c["pos"], c["target"], c["lens"], q)
                    if uv is None or not (0.0 <= uv[0] <= 1.0 and 0.0 <= uv[1] <= 1.0):
                        out.append("camera %s: %s %s out of frame (%s)" % (
                            name, an, what, "behind" if uv is None else "u %.2f v %.2f" % uv))
                        continue
                    hit = sight_blocked(w, c["pos"], q)
                    if hit:
                        out.append("camera %s: %s %s hidden by %s at %s" % (name, an, what, hit[2], hit[1]))
        return out


class _Builder:
    """Puts one set's blocks into the shared World (with the bastion processors where the game would apply them),
    and collects its anchors, paths, cameras, lantern groups, cutaways and lava."""

    def __init__(self, bas, w, name, origin, seed):
        self.bas, self.w, self.name, self.o, self.seed = bas, w, name, tuple(origin), seed
        self.groups = {}             # world cell -> light group
        self.cut = {}                # cutaway name -> set of world cells
        self.lava = []               # (kind, kwargs) built after the blocks
        self.cells = set()
        self.anchors = {}

    def P(self, x, y, z=0.0):
        """Local set coordinates -> world (Blender) coordinates."""
        return (self.o[0] + x, self.o[1] + y, self.o[2] + z)

    def C(self, x, y, z):
        return (int(self.o[0] + x), int(self.o[1] + y), int(self.o[2] + z))

    def set(self, x, y, z, block, props=None, rules=None):
        c = self.C(x, y, z)
        if block is not None and rules:
            block = degrade(block, rules, c, self.seed)
        self.w.set(*c, block, props)
        if block is not None:
            self.cells.add(c)

    def fill(self, x0, y0, z0, x1, y1, z1, block, props=None, rules=None):
        for x in range(min(x0, x1), max(x0, x1) + 1):
            for y in range(min(y0, y1), max(y0, y1) + 1):
                for z in range(min(z0, z1), max(z0, z1) + 1):
                    self.set(x, y, z, block, props, rules)

    def get(self, x, y, z):
        return self.w.block_id(*self.C(x, y, z))

    def lantern(self, x, y, z, group, hanging=True, chain=0, bracket=None):
        """A lantern at local cell (x, y, z) (hanging under `chain` chain blocks and a `bracket` block above them, or
        standing). Every lantern becomes a point light in light group `group`."""
        self.set(x, y, z, "lantern", LANTERN if hanging else STANDING)
        for k in range(1, chain + 1):
            self.set(x, y, z + k, "iron_chain", CHAIN)
        if bracket:
            self.set(x, y, z + chain + 1, bracket)
        self.groups[self.C(x, y, z)] = group

    def cutaway(self, name, x0, y0, z0, x1, y1, z1):
        cells = self.cut.setdefault(name, set())
        for x in range(min(x0, x1), max(x0, x1) + 1):
            for y in range(min(y0, y1), max(y0, y1) + 1):
                for z in range(min(z0, z1), max(z0, z1) + 1):
                    cells.add(self.C(x, y, z))

    def anchor(self, name, x, y, z=0.0, yaw=None):
        p = self.P(x, y, z)
        self.bas.anchors[name] = p
        self.anchors[name] = p
        if yaw is not None:
            self.bas.yaws[name] = float(yaw)
        return p

    def path(self, name, pts):
        self.bas.paths[name] = [self.P(*p) for p in pts]

    def camera(self, name, pos, target, lens, fstop=None, beats=(), note="", cast=(), sees=(), pit=None,
               pillar=False, focus=None, lights=None):
        """A camera suggestion. cast = [(kind, anchor, look anchor or None), ...] (kind 'brute' | 'piglin' | 'steve'
        | 'ingot' | 'steve_crouch') is who stands where in its verification render (render_cams); sees = anchors
        whose feet and head must be in the frame and in the clear (_check ray-casts them); pit None | 'open' |
        'keep'; pillar: the netherrack pillar stands; lights: {group: scale} for st.lights."""
        self.bas.cameras[name] = dict(pos=self.P(*pos), target=self.P(*target), lens=float(lens), fstop=fstop,
                                      beats=tuple(beats), note=note, set=self.name, cast=tuple(cast),
                                      sees=tuple(sees), pit=pit, pillar=bool(pillar), focus=focus,
                                      lights=dict(lights or {}))

    def template(self, name, x, y, z, rot=0, keep=None):
        """Place a bastion piece with the min corner of its footprint at local cell (x, y, z)."""
        t = load_template(name, seed=self.seed)
        pl = self.w.place_template(t, self.C(x, y, z), rot, keep=keep)
        for bx, by, bz, _b, _p in pl.blocks:
            self.cells.add((bx, by, bz))
        self.bas.buildings["%s:%s" % (self.name, name)] = pl
        return pl


# ---- the home bastion courtyard (stories/piglin.json: ONE fixed layout for every shot) --------------------------
# Local cells (the set's origin is ORIGINS['home']); the courtyard floor's surface is z 0. The courtyard is narrow
# and deep (9 x 20) on purpose: a 9:16 frame from its near end holds the gateway, the landing and the gold wall.
HOME = dict(
    floor=(0, -2, 8, 17),        # courtyard floor cells x 0..8, y -2..17
    gateway=(3, 5, 4),           # opening x 3..5 through the north wall (y 18..20), z 0..4 (5 high), arched corners
    corridor=(21, 32),           # the entrance corridor beyond it: y 21..32, interior x 2..6, roof at z 5, lava
    #                              channels x 2 and x 6, a lava wall closing it at y 33 (the glow beyond the gateway)
    landing=(0, 10, 2, 17, 4),   # guard landing x 0..2, y 10..17, standing height z 4: against the west and north
    #                              walls, right beside the gateway's west jamb
    stair=(0, 1, 6, 9),          # guard stair x 0..1, four steps y 6..9 rising north along the west wall
    gold=(9, 9, 15, 2),          # gold blocks in the east wall's inner face: x 9, y 9..15, z 0..2 (7 x 3); far
    #                              enough up the courtyard that the 'gate' frame holds them with the landing
    step=8,                      # the one-block blackstone step in front of them: x 8, y 9..15 (top z 1)
    pit=(4, 6),                  # SW cell of the 2 x 2 pit: cells x 4..5, y 6..7, z -1 and -2 (its floor z -2);
    #                              2.5 blocks from the gold places, so the piglins' walk to it is short
    plain=(1, 2, 7, 9),          # plain blackstone floor patch around the pit (never gilded, never gold)
)


def _home(b, layout):
    PB, BS = "polished_blackstone_bricks", "blackstone"
    GEN, RAMP = "bastion_generic_degradation", "rampart_degradation"
    PBS = "polished_blackstone_brick_stairs"
    px, py = layout.get("pit", HOME["pit"])
    fx0, fy0, fx1, fy1 = HOME["floor"]
    if not (fx0 + 1 <= px <= fx1 - 3 and fy0 + 2 <= py <= 15):
        raise ValueError("layout['pit'] %s: the pit must lie in the courtyard floor, clear of its walls" % ((px, py),))
    x0p, y0p, x1p, y1p = HOME["plain"]
    x0p, y0p, x1p, y1p = min(x0p, px - 2), min(y0p, py - 2), max(x1p, px + 3), max(y1p, py + 3)
    EX = fx1 + 1                                              # the east wall's inner face (x 9)
    g0, g1, gh = HOME["gateway"]
    c0, c1 = HOME["corridor"]
    cw0, cw1 = g0 - 2, g1 + 2                                 # corridor walls (x 1 and x 7)
    # the platform: everything stands on blackstone four deep, over the void
    b.fill(-3, -3, -4, EX + 2, 20, -2, BS, rules=GEN)
    b.fill(cw0, 21, -4, cw1, c1 + 2, -2, BS, rules=GEN)
    # courtyard floor: polished blackstone bricks (30 % cracked: bastion_generic_degradation) with blackstone patches
    for x in range(fx0, fx1 + 1):
        for y in range(fy0, fy1 + 1):
            if x0p <= x <= x1p and y0p <= y <= y1p:
                continue
            kind = BS if (pos_hash(x, y, 0, 3) % 7 == 0 or pos_hash(x // 2, y // 3, 0, 4) % 5 == 0) else PB
            b.set(x, y, -1, kind, rules=GEN)
    b.fill(x0p, y0p, -4, x1p, y1p, -1, BS)                   # the pit's patch: plain blackstone, four deep
    # ---- walls: blackstone cores, polished blackstone brick inner faces (rampart_degradation: 40 % cracked)
    b.fill(-3, -3, -1, -1, 20, 9, BS, rules=GEN)              # west
    b.fill(EX, -3, -1, EX + 2, 20, 9, BS, rules=GEN)          # east
    b.fill(-3, 18, -1, EX + 2, 20, 11, BS, rules=GEN)         # north (far) wall
    for y in range(fy0, 18):
        for z in range(0, 10):
            b.set(-1, y, z, PB if z else PB, rules=RAMP if z else None)
            b.set(EX, y, z, PB, rules=RAMP if z else None)
    for x in range(fx0, fx1 + 1):
        for z in range(0, 12):
            b.set(x, 18, z, PB, rules=RAMP if z else None)
    for (x, y, top) in ((-1, -1, 9), (-1, 4, 9), (EX, -1, 9), (EX, 3, 9), (0, 18, 11), (fx1, 18, 11)):
        b.fill(x, y, 0, x, y, top, "polished_basalt", UP)    # the bastion's polished basalt columns
    for y in range(-3, 21):                                   # crenellations along the wall tops
        if y % 2 == 0:
            b.set(-1, y, 10, PB, rules=RAMP)
            b.set(-3, y, 10, BS, rules=GEN)
            b.set(EX, y, 10, PB, rules=RAMP)
            b.set(EX + 2, y, 10, BS, rules=GEN)
    for x in range(-3, EX + 3):
        if x % 2 == 0:
            b.set(x, 18, 12, PB, rules=RAMP)
            b.set(x, 20, 12, BS, rules=GEN)
    # ---- the gateway: polished basalt jambs, a chiseled lintel, upside-down stairs rounding the top corners
    b.fill(g0, 18, 0, g1, 20, gh, None)
    for y in (18, 19, 20):
        for x in range(g0, g1 + 1):
            b.set(x, y, -1, PB, rules=GEN)
    for x in (g0 - 1, g1 + 1):
        b.fill(x, 18, 0, x, 18, gh + 1, "polished_basalt", UP)
    for x in range(g0 - 1, g1 + 2):
        b.set(x, 18, gh + 1, "chiseled_polished_blackstone")
    b.set((g0 + g1) // 2, 18, gh + 2, "gilded_blackstone")
    for y in (18, 19, 20):
        b.set(g0, y, gh, PBS, {"facing": "west", "half": "top", "shape": "straight", "waterlogged": "false"})
        b.set(g1, y, gh, PBS, {"facing": "east", "half": "top", "shape": "straight", "waterlogged": "false"})
    # ---- the entrance corridor beyond it, lava channels along both walls and a lava wall at its end
    for x in (cw0, cw1):
        b.fill(x, c0, -1, x, c1 + 2, 6, BS, rules=GEN)
        for y in range(c0, c1 + 2):
            for z in range(0, 5):
                b.set(x, y, z, PB, rules=RAMP)
        for y in range(c0, c1 + 1, 4):                        # basalt ribs
            b.fill(x, y, 0, x, y, 4, "polished_basalt", UP)
    b.fill(cw0, c0, 5, cw1, c1 + 1, 6, BS, rules=GEN)        # roof
    for y in range(c0, c1 + 1):
        for x in range(g0, g1 + 1):
            b.set(x, y, -1, PB, rules=GEN)
    b.fill(cw0, c1 + 2, -1, cw1, c1 + 2, 6, BS, rules=GEN)    # behind the lava wall
    b.fill(cw0 + 1, c1 + 1, -1, cw1 - 1, c1 + 1, -1, BS)      # under it
    b.lava.append(("lava", dict(cells=[b.C(x, y, -1) for x in (cw0 + 1, cw1 - 1) for y in range(c0, c1 + 1)],
                                name="home_channels", watts_per_block=55.0)))
    b.lava.append(("lava", dict(cells=[b.C(x, c1 + 1, z) for x in range(cw0 + 1, cw1) for z in range(0, 5)],
                                name="home_lava_wall", light=False)))
    b.lava.append(("wall_light", dict(rect=(b.P(cw0 + 1, c1 + 1, 0), b.P(cw1, c1 + 1, 5)),
                                      name="home_lava_wall_light", watts=1100.0)))
    b.cutaway("home_corridor_roof", cw0, c0, 5, cw1, c1 + 1, 6)
    # ---- the guard stair along the west wall, and the landing beside the gateway
    sx0, sx1, sy0, sy1 = HOME["stair"]
    lx0, ly0, lx1, ly1, lz = HOME["landing"]
    for i, y in enumerate(range(sy0, sy1 + 1)):
        for x in range(sx0, sx1 + 1):
            if i:
                b.fill(x, y, 0, x, y, i - 1, PB, rules=RAMP)
            b.set(x, y, i, PBS, {"facing": "north", "half": "bottom", "shape": "straight", "waterlogged": "false"})
    b.fill(lx0, ly0, 0, lx1, ly1, lz - 1, BS, rules=GEN)
    for x in range(lx0, lx1 + 1):                             # its faces: bricks, a chiseled course under the top
        for z in range(0, lz - 1):
            b.set(x, ly0, z, PB, rules=RAMP)
        b.set(x, ly0, lz - 1, "chiseled_polished_blackstone" if x % 2 else PB)
    for y in range(ly0, ly1 + 1):
        for z in range(0, lz - 1):
            b.set(lx1, y, z, PB, rules=RAMP)
        b.set(lx1, y, lz - 1, "chiseled_polished_blackstone" if y % 2 else PB)
    for x in range(lx0, lx1):                                 # its walking surface
        for y in range(ly0 + 1, ly1 + 1):
            b.set(x, y, lz - 1, PB, rules=GEN)
    # ---- the gold wall in the east wall's inner face, framed, with its blackstone step
    gx, gy0, gy1, gz1 = HOME["gold"]
    b.fill(gx, gy0, 0, gx, gy1, gz1, "gold_block")
    for y in (gy0 - 1, gy1 + 1):
        b.fill(gx, y, 0, gx, y, gz1 + 1, "polished_basalt", UP)
    for y in range(gy0, gy1 + 1):
        b.set(gx, y, gz1 + 1, "chiseled_polished_blackstone")
    b.fill(HOME["step"], gy0, 0, HOME["step"], gy1, 0, BS)
    # ---- the south edge: a broken parapet over the void (the lava sea glows far below)
    for x in range(-3, EX + 3):
        b.set(x, -3, 0, PB, rules=RAMP)
        if pos_hash(x, -3, 1, 9) % 3:
            b.set(x, -3, 1, PB, rules=RAMP)
    b.cutaway("home_south_parapet", -3, -3, 0, EX + 2, -3, 1)
    # ---- lanterns (each group a light group of its own: Stage.lights(..., groups={...}) per shot)
    b.set(0, 13, 8, PB)                                       # landing: an arm out of the west wall
    b.lantern(1, 13, 6, "home_landing", chain=1, bracket=PB)
    b.lantern(g0 - 1, 17, 7, "home_gate", chain=1, bracket=PB)    # beside the gateway, over the landing's corner
    b.lantern(g1 + 1, 17, 6, "home_gate", chain=1, bracket=PB)
    for y in (gy0 + 1, gy1 - 1):                              # over the gold wall's step
        b.lantern(HOME["step"], y, 4, "home_gold", chain=1, bracket=PB)
    b.lantern(0, sy0 - 2, 3, "home_pit", chain=1, bracket=PB)    # low on the west wall south of the stair
    # the lava sea far below, south and north of the platform: a glow only, fogged by distance
    b.lava.append(("glow", dict(x0=-45, y0=-75, x1=55, y1=-4, z=-29.0 + 8.0 / 9.0, name="home_sea_south",
                                watts_per_block=0.6, max_watts=3500.0, animated=False)))
    b.lava.append(("glow", dict(x0=-30, y0=35, x1=40, y1=80, z=-29.0 + 8.0 / 9.0, name="home_sea_north",
                                watts_per_block=0.6, max_watts=2500.0, animated=False)))
    # ---- the pit's cells are NOT in the World (they are Breakables): physics sees the pit dug (Bastion.whole: not)
    b.pit = [b.C(x, y, z) for z in (-1, -2) for x in (px, px + 1) for y in (py, py + 1)]
    for c in b.pit:
        b.w.set(*c, None)
    # ---- anchors, paths, cameras
    pcx, pcy = px + 1.0, py + 1.0
    gc = (g0 + g1 + 1) / 2.0                                  # the gateway's centre line (x 4.5)
    E, W, N, S = _yaw("east"), _yaw("west"), _yaw("north"), _yaw("south")
    gys = [gy0 + 0.6 + 1.6 * k for k in range(4)]             # four places in front of the gold, 1.6 apart
    gxs = [EX - 1.7, EX - 2.7, EX - 1.7, EX - 1.7]            # home_gold_2 a block further back: seen from the
    #                                                           south end the three do not line up behind each other
    lnd = (lx1 + 0.7, ly1 + 0.45, float(lz))                  # the landing's north-east corner, by the gateway's jamb
    b.anchor("home_landing", *lnd, yaw=E)                     # the brute on guard: a profile in the 'gate' frame
    b.anchor("home_landing_look", g0 + 2.2, 17.9, lz + 0.6)   # what he watches: the gateway's mouth, 10 deg N of east
    cam_landing = (0.45, 16.6, 5.85)                         # eye level on the landing (any lower and its own edge
    #                                                           hides the piglins: ray-checked)
    edge = (lx1 + 0.65, 16.25, float(lz))
    b.anchor("home_landing_edge", *edge, yaw=yaw_to(edge[:2], cam_landing[:2]))       # beat 1, toward the lens
    b.anchor("home_landing_edge_look", cam_landing[0] + 0.1, cam_landing[1] + 0.7, cam_landing[2] - 0.2)  # past it
    b.anchor("home_stair_foot", 0.95, sy0 - 1.4, 0.0, N)
    b.anchor("home_gateway", gc, 19.0, 0.0, N)                        # in the gateway, facing out (beats 17, 18)
    b.anchor("home_gateway_target", gc, 19.0, 2.5)
    b.anchor("home_corridor", gc, 27.0, 0.0, S)
    b.anchor("home_entry", gc, c1 - 0.5, 0.0, S)                      # where a runner starts, by the lava wall
    for k, (x, y) in enumerate(zip(gxs, gys), 1):                     # in front of the gold, facing it
        b.anchor("home_gold_%d" % k, x, y, 0.0, E)
        b.anchor("home_step_%d_item" % k, HOME["step"] + 0.5, y, 1.0)
    b.anchor("home_gold_target", gx, (gy0 + gy1 + 1) / 2.0, 1.5)
    b.bas.yaws["home_gold_ne"] = _yaw((1.0, 1.0))                    # facing the gold diagonally (the ingot row)
    b.anchor("home_pit_center", pcx, pcy, -2.0)
    for k, (dx, dy) in enumerate(((-0.5, -0.5), (0.5, -0.5), (-0.5, 0.5), (0.5, 0.5)), 1):
        b.anchor("home_pit_%d" % k, pcx + dx, pcy + dy, -2.0)
    b.anchor("home_rim_w", px - 0.4, pcy, 0.0, E)
    b.anchor("home_rim_s", pcx, py - 0.4, 0.0, N)
    b.anchor("home_rim_e", px + 2.4, pcy, 0.0, W)
    b.anchor("home_rim_n", pcx, py + 2.4, 0.0, S)
    b.anchor("home_strike", px - 1.65, pcy, 0.0, E)                   # beat 9: the brute hits the player at rim_w
    drops = [(px + 1.7, py + 0.5, W), (px + 1.7, py + 1.5, W), (px + 0.5, py + 1.7, S)]
    for k, (x, y, yaw) in enumerate(drops, 1):                        # 0.3 past the rim: Piglin.fall from here
        b.anchor("home_pit_drop_%d" % k, x, y, 0.0, yaw)
        dx, dy = (1.0, 0.0) if yaw == W else (0.0, 1.0)
        b.anchor("home_pit_approach_%d" % k, x + dx, y + dy, 0.0, yaw)   # one block back from the drop
        b.path("home_pit_approach_%d" % k, [(x + dx, y + dy, 0.0), (x, y, 0.0)])
    b.path("home_pit_walk_1", [(gxs[0], gys[0], 0.0), (px + 2.7, py + 0.5, 0.0), (px + 1.7, py + 0.5, 0.0)])
    b.path("home_pit_walk_2", [(gxs[1], gys[1], 0.0), (px + 2.7, py + 1.5, 0.0), (px + 1.7, py + 1.5, 0.0)])
    b.path("home_pit_walk_3", [(gxs[2], gys[2], 0.0), (px + 0.5, py + 2.7, 0.0), (px + 0.5, py + 1.7, 0.0)])
    boot = (px + 1.2, py + 2.9)
    b.anchor("home_boot_mark", boot[0], boot[1], 0.0, S)              # the runner's skid stops here (beat 5)
    b.anchor("home_flash", gc, 14.5, 0.0, S)                          # beat 16: the gateway behind him
    b.anchor("home_center", gc, 8.0, 0.0)
    b.path("home_run_in", [(gc, c1 - 0.5, 0.0), (gc, 19.0, 0.0), (gc, 12.0, 0.0), (boot[0], boot[1], 0.0)])
    b.path("home_run_past", [(gc, c1 - 0.5, 0.0), (gc, 19.0, 0.0), (gc + 1.9, 9.0, 0.0), (gc + 2.1, 0.5, 0.0)])
    b.path("home_to_rim", [(boot[0], boot[1], 0.0), (px - 0.4, py + 2.6, 0.0), (px - 0.4, pcy, 0.0)])
    b.path("home_stair_up", [(0.95, sy0 - 1.4, 0.0), (0.95, float(sy0), 0.0), (0.95, float(sy0 + lz), float(lz)),
                             (1.4, float(sy0 + lz) + 1.5, float(lz)), lnd])
    G = [("piglin", "home_gold_%d" % k, "home_gold_target") for k in (1, 2, 3)]
    b.camera("gate", (5.2, 1.0, 1.8), (5.94, 18.0, 2.6), 30, 4.0, beats=(3, 18, 19, 23),
             note="static wide, low, from the courtyard's near part: the gateway and the corridor's glow high in the "
                  "middle, the brute on the landing at the upper left in profile facing the gateway, the piglins at "
                  "the gold wall nearer and lower on the right",
             cast=[("brute", "home_landing", "home_landing_look")] + G,
             sees=("home_landing", "home_gold_1", "home_gold_2", "home_gold_3", "home_gateway"),
             focus="home_center")
    b.camera("landing", cam_landing, (5.59, 13.98, 4.2), 22, 2.8, beats=(1,),
             note="at eye level on the landing, across it to the south-east: the brute at home_landing_edge big at "
                  "frame left looking just past the lens, the piglins at the gold wall far behind and below him",
             cast=[("brute", "home_landing_edge", "home_landing_edge_look")] + G,
             sees=("home_landing_edge", "home_gold_1:head", "home_gold_2:head", "home_gold_3:head"),
             focus="home_landing_edge")
    NE = _yaw((1.0, 1.0))
    b.camera("ingot_row", (EX - 4.0, gys[3] + 2.6, 1.65), (EX - 1.4, gys[0] + 1.6, 1.45), 40, 2.0, beats=(2, 21),
             note="at snout height from the north-west, along the gold wall: piglins at home_gold_3 and home_gold_1 "
                  "turned to the gold diagonally (yaw home_gold_ne) admiring, left hands and ingots toward the lens, "
                  "the gold wall behind them; the brute at home_gold_4 is the dark shape at the left edge (beat 21: "
                  "head down at the ingot on the step, home_step_4_item)",
             cast=[("piglin_admire", "home_gold_3", None, NE), ("piglin_admire", "home_gold_1", None, NE),
                   ("brute", "home_gold_4", "home_step_4_item"), ("ingot", "home_step_4_item", None)],
             sees=("home_gold_1", "home_gold_3"), focus="home_gold_3")
    b.camera("boot", (px - 0.8, py + 0.6, 0.25), (EX - 1.63, gys[0] + 1.32, 0.5), 50, 2.0, beats=(5,),
             note="on the floor at the pit's south-west corner (floor whole), across at the gold wall: the boots "
                  "stop at home_boot_mark mid-frame, the three piglins behind them",
             cast=[("steve", "home_boot_mark", None)] + [("piglin", "home_gold_%d" % k, "home_boot_mark")
                                                          for k in (1, 2, 3)],
             sees=("home_boot_mark:shins", "home_gold_1", "home_gold_2", "home_gold_3"), focus="home_boot_mark")
    b.camera("pit", (px - 1.9, py - 2.6, 5.4), (pcx + 0.4, pcy + 0.5, -1.2), 28, 4.0, beats=(6, 20),
             note="high three-quarter from the south-west on the pit, the gold wall beyond",
             cast=[("steve", "home_rim_w", "home_pit_center")] + [("piglin", "home_pit_%d" % k, "home_rim_w")
                                                                    for k in (2, 3, 4)] + [("ingot", "home_pit_1", None)],
             sees=("home_rim_w", "home_pit_2:head", "home_pit_3:head", "home_pit_4:head"), pit="keep",
             focus="home_pit_center",
             lights={"home_pit": 2.0})
    b.camera("rim_side", (px - 0.4, py - 5.2, 1.45), (px - 0.2, pcy + 0.6, 1.0), 35, 3.0, beats=(9, 10),
             note="side-on medium from the south at the west rim: the player in profile facing the pit, the brute "
                  "at home_strike behind him (from frame left), the pit at the right",
             cast=[("steve", "home_rim_w", None), ("brute", "home_strike", "home_rim_w")],
             sees=("home_rim_w", "home_strike"), pit="open", focus="home_rim_w")
    b.camera("inside_gate", (gc + 0.4, 13.2, 0.3), (g0 + 0.6, 18.5, 2.5), 24, 4.0, beats=(4,),
             note="ground level inside the gateway, looking out at the corridor: the runner comes at the lens through "
                  "the gateway, the brute on the landing small at the upper left",
             cast=[("steve", "home_gateway", None, S), ("brute", "home_landing", "home_gateway")],
             sees=("home_landing:head", "home_gateway"), focus="home_gateway")
    b.camera("corridor", (g0 + 0.6, 25.5, 1.55), (gc - 0.6, 19.0, 1.45), 35, 2.4, beats=(17,),
             note="from the entrance corridor: the brute in the gateway facing out past the lens at frame left, his "
                  "brothers soft at the gold through the gateway",
             cast=[("brute", "home_gateway", None)] + G, sees=("home_gateway",), focus="home_gateway")
    b.camera("flash", (gc, 9.5, 1.45), (gc, 14.5, 1.3), 35, 2.8, beats=(16,),
             note="the brute at home_flash, the gateway behind him; the same offset as bridge / treasure 'flash'",
             cast=[("brute", "home_flash", None)], sees=("home_flash",), focus="home_flash")
    b.set_lights = dict(near=b.P(gc, 12.0, 2.0), radius=30.0)
    b.bounds = (b.o[0] - 3, b.o[1] - 3, b.o[0] + EX + 2, b.o[1] + c1 + 2)


# ---- the second bastion's bridge --------------------------------------------------------------------------
BRIDGE = dict(
    deck=(-2, -8, 2, 44),        # deck cells x -2..2 (walkway -1..1, low walls on the edges), y -8..44, surface z 0
    pillars=(2, 15, 28, 41),     # basalt pillar pairs (2 deep from these y) at x -4..-3 and 3..4, z -24..6
    lantern=(0, 16, 3),          # the one lantern, on a chain from the beam between the y 15..16 pillars
    netherrack=(0, 19),          # the player's three-block netherrack pillar (Breakables), cells z 0..2
    legs=((9, "bridge/legs/leg_0"), (23, "bridge/legs/leg_1"), (35, "bridge/legs/leg_0")),   # the game's own legs
    sea=-24.0,                   # the lava sea's floor level (its surface 8/9 above)
    open_edges=((16, 21), (3, 5)),   # y ranges with no edge wall (side views of the pillar; the boot camera's spot)
    under_lanterns=((-2, 7), (2, 7), (-2, 33), (2, 33)),   # lanterns on a chain under the deck's edges, as the
    #                              game's own bridge piece (bridge/bridge_pieces/bridge) hangs them
)


def _bridge(b, layout):
    PB, BS = "polished_blackstone_bricks", "blackstone"
    x0, y0, x1, y1 = BRIDGE["deck"]
    gaps = BRIDGE["open_edges"]

    def gap(x, y):
        return any(a <= y <= c for a, c in gaps[:1]) or (x == 2 and gaps[1][0] <= y <= gaps[1][1])

    for x in range(x0, x1 + 1):
        for y in range(y0, y1 + 1):
            b.set(x, y, -1, PB if abs(x) <= 1 else BS, rules="bridge" if abs(x) <= 1 else None)
            b.set(x, y, -2, BS)
            if abs(x) == 2 and not gap(x, y):
                if y % 6 == 0:                                # a basalt post every six blocks (the game's bridge
                    b.set(x, y, 0, "polished_basalt", UP)     # piece bands its parapets with basalt)
                elif pos_hash(x, y, 0, 11) % 4:
                    b.set(x, y, 0, "polished_blackstone_brick_wall")
    for y in range(y0, y1 + 1, 2):                            # a lip under the deck's edges
        for x in (x0, x1):
            b.set(x, y, -3, "blackstone_slab", {"type": "top", "waterlogged": "false"})
    for py in BRIDGE["pillars"]:
        for xa in (-4, 3):
            for x in (xa, xa + 1):
                for y in (py, py + 1):
                    for z in range(-24, 7):
                        if z % 7 == 3:                        # polished blackstone brick bands
                            b.set(x, y, z, PB, rules="bridge")
                        elif z >= 4:
                            b.set(x, y, z, "polished_basalt", UP)
                        else:
                            b.set(x, y, z, "basalt", UP)
                    b.set(x, y, 7, PB, rules="bridge")
            b.set(xa, py, 8, "gold_block")                    # gold on the pillar heads, as on the game's bridge piece
            b.set(xa + 1, py + 1, 8, "gilded_blackstone")
        for x in (-2, 2):                                     # brackets joining pillar and deck
            for y in (py, py + 1):
                b.set(x, y, -3, PB)
    lx, ly, lz = BRIDGE["lantern"]
    b.fill(-2, ly, 7, 2, ly, 7, PB, rules="bridge")           # the beam the lantern hangs from
    b.lantern(lx, ly, lz, "bridge_lantern", chain=3)
    for ux, uy in BRIDGE["under_lanterns"]:
        b.lantern(ux, uy, -4, "bridge_under", chain=1)        # hanging from the deck's underside (z -2)
    for yl, piece in BRIDGE["legs"]:
        b.template(piece, -1, yl, -24)
    b.lava.append(("glow", dict(x0=-45, y0=-45, x1=45, y1=90, z=BRIDGE["sea"] + 8.0 / 9.0, name="bridge_sea",
                                watts_per_block=4.0, max_watts=40000.0, animated=False)))
    nx, ny = BRIDGE["netherrack"]
    b.pillar = [b.C(nx, ny, z) for z in (0, 1, 2)]
    S, N = _yaw("south"), _yaw("north")
    b.anchor("bridge_start", 0.5, -6.0, 0.0, N)
    b.anchor("bridge_boot_mark", 0.5, 6.5, 0.0, N)
    b.anchor("bridge_player", 0.5, 10.6, 0.0, N)
    b.anchor("bridge_player_look", lx + 0.5, ly + 0.5, 1.75)          # the brute's face
    b.anchor("bridge_brute", lx + 0.5, ly + 0.5, 0.0, S)              # under his lantern, blocking the bridge
    b.anchor("bridge_brute_look", 0.5, 10.6, 1.55)                    # the player's face at bridge_player
    b.anchor("bridge_middle", 0.5, 18.0, 0.0)
    b.anchor("bridge_pillar_foot", nx + 0.5, ny - 0.75, 0.0, N)       # at the netherrack pillar's foot, facing it
    b.anchor("bridge_pillar_top", nx + 0.5, ny + 0.5, 3.0, S)         # standing (crouching) on top of it
    b.anchor("bridge_pillar_top_target", nx + 0.5, ny + 0.5, 4.4)
    b.anchor("bridge_flash", lx + 0.5, ly + 0.5, 0.0, S)
    b.path("bridge_run_in", [(0.5, -6.0, 0.0), (0.5, 6.5, 0.0)])
    PIL = [("steve_crouch", "bridge_pillar_top", None), ("brute", "bridge_pillar_foot", "bridge_pillar_top_target")]
    b.camera("bridge_boot", (2.6, 4.3, 0.25), (-1.4, 8.4, 0.85), 50, 2.0, beats=(11,),
             note="the boot shot on the deck, matched to home 'boot': on the floor at the east edge (no wall there), "
                  "40 mm across the walkway; the legs come in from frame left and stop at bridge_boot_mark mid-frame",
             cast=[("steve", "bridge_boot_mark", None)], sees=("bridge_boot_mark:shins",), focus="bridge_boot_mark")
    b.camera("bridge_shoulder", (1.15, 8.7, 1.95), (0.5, 16.5, 1.35), 50, 2.6, beats=(12,),
             note="over the player's shoulder at bridge_player: the brute blocking under his lantern",
             cast=[("steve", "bridge_player", "bridge_player_look"), ("brute", "bridge_brute", "bridge_brute_look")],
             sees=("bridge_brute",), focus="bridge_brute")
    b.camera("bridge_pillar", (9.0, ny - 0.1, 2.2), (0.5, ny - 0.1, 0.9), 30, 4.0, beats=(13,),
             note="side-on from the east over the void (no edge wall there): the player crouched on the pillar "
                  "top high in the safe zone, the brute at its foot looking up",
             cast=PIL, sees=("bridge_pillar_foot", "bridge_pillar_top"), pillar=True, focus="bridge_pillar_foot")
    b.camera("bridge_profile", (5.8, ny - 0.75, 1.3), (0.5, ny - 0.75, 0.4), 35, 2.4, beats=(14,),
             note="the brute in profile at the pillar's foot, head up, his feet above 60 % of the frame height",
             cast=PIL[1:], sees=("bridge_pillar_foot",), pillar=True, focus="bridge_pillar_foot")
    b.camera("bridge_top", (nx + 2.3, ny + 2.4, 5.4), (nx + 0.2, ny - 1.6, 0.3), 30, 3.0, beats=(15,),
             note="high, just behind the player on the pillar top, down on the brute's upturned face",
             cast=[("steve_crouch", "bridge_pillar_top", None),
                   ("brute", "bridge_pillar_foot", (nx + 0.5, ny + 0.6, 4.6))],
             sees=("bridge_pillar_foot",), pillar=True, focus="bridge_pillar_foot")
    b.camera("bridge_flash", (lx + 0.5, ly - 4.5, 1.45), (lx + 0.5, ly + 0.5, 1.3), 35, 2.8, beats=(16,),
             note="the brute at bridge_flash; the same offset as home / treasure 'flash'",
             cast=[("brute", "bridge_flash", None)], sees=("bridge_flash",), focus="bridge_flash")
    b.camera("bridge_wide", (13.0, 3.5, 2.5), (-1.0, 21.0, -6.0), 24, 5.0, beats=(),
             note="the whole bridge, its pillars and the lava far below",
             cast=[("brute", "bridge_brute", None)], focus="bridge_brute")
    b.set_lights = dict(near=b.P(0.5, 16.5, 2.0), radius=30.0)
    b.bounds = (b.o[0] - 5, b.o[1] + y0, b.o[0] + 5, b.o[1] + y1)


# ---- the third bastion's treasure corner ---------------------------------------------------------------------
TREASURE = dict(
    floor=(-4, -4, 12, 12),      # floor cells, surface z 0
    piece=("treasure/bases/centers/center_0", 1, 5),   # the game's treasure-room centre: gold pile + chest on top
    heap=((5, 3, 0), (6, 3, 0), (6, 4, 0), (5, 4, 0), (6, 4, 1), (5, 4, 1), (7, 4, 0)),   # loose gold blocks
    #                              (right of the brute in the 'flash' frame)
    chest=((2, 3, 0), "south"),  # a chest on the floor (left of the brute in the 'flash' frame)
)


def _treasure(b, layout):
    PB, BS = "polished_blackstone_bricks", "blackstone"
    TR = "treasure_rooms"
    fx0, fy0, fx1, fy1 = TREASURE["floor"]
    b.fill(fx0 - 2, fy0, -3, fx1, fy1 + 2, -2, BS, rules=TR)
    for x in range(fx0, fx1 + 1):
        for y in range(fy0, fy1 + 1):
            b.set(x, y, -1, PB if pos_hash(x, y, 0, 13) % 6 else BS, rules=TR)
    b.fill(fx0 - 2, fy0, -1, fx0 - 1, fy1 + 2, 9, BS, rules=TR)          # west wall
    b.fill(fx0 - 2, fy1 + 1, -1, fx1, fy1 + 2, 9, BS, rules=TR)          # north wall
    for y in range(fy0, fy1 + 1):
        for z in range(0, 10):
            b.set(fx0 - 1, y, z, PB, rules=TR)
    for x in range(fx0 - 1, fx1 + 1):
        for z in range(0, 10):
            b.set(x, fy1 + 1, z, PB, rules=TR)
    for (x, y) in ((fx0 - 1, 0), (fx0 - 1, 7), (2, fy1 + 1), (9, fy1 + 1), (fx0 - 1, fy1 + 1)):
        b.fill(x, y, 0, x, y, 9, "polished_basalt", UP)
    for y in range(fy0, fy1 + 2):                                        # gilded blackstone in the wall heads
        if y % 3 == 0:
            b.set(fx0 - 1, y, 9, "gilded_blackstone")
    name, ox, oy = TREASURE["piece"]
    pl = b.template(name, ox, oy, -1)                          # sunk one block into the floor
    b.chest_cells = [(bx, by, bz, p) for bx, by, bz, bid, p in pl.blocks if bid == "chest"]
    for bx, by, bz, _p in b.chest_cells:
        b.w.set(bx, by, bz, None)
    for c in TREASURE["heap"]:
        b.set(*c, "gold_block")
    (cx, cy, cz), cf = TREASURE["chest"]
    b.chest_cells.append((b.o[0] + cx, b.o[1] + cy, b.o[2] + cz, {"facing": cf}))
    b.lantern(4, fy1, 7, "treasure", chain=1, bracket=PB)
    b.lantern(fx0, 3, 6, "treasure", chain=1, bracket=PB)
    b.cutaway("treasure_west_wall", fx0 - 2, fy0, 0, fx0 - 1, fy1 + 2, 9)
    S = _yaw("south")
    b.anchor("treasure_flash", 4.0, 0.8, 0.0, S)
    b.anchor("treasure_pile_target", ox + 3.5, oy + 4.0, 3.0)
    b.camera("treasure_flash", (4.0, -4.2, 1.45), (4.0, 0.8, 1.3), 35, 2.8, beats=(16,),
             note="the brute at treasure_flash, the gold pile and the chest behind; same offset as the others",
             cast=[("brute", "treasure_flash", None)], sees=("treasure_flash",), focus="treasure_flash")
    b.camera("treasure_wide", (11.0, -3.5, 3.0), (3.0, 7.0, 1.5), 24, 5.0, note="the corner",
             cast=[("brute", "treasure_flash", None)], sees=("treasure_flash",), focus="treasure_flash")
    b.set_lights = dict(near=b.P(4.0, 5.0, 2.0), radius=24.0)
    b.bounds = (b.o[0] + fx0 - 2, b.o[1] + fy0, b.o[0] + fx1, b.o[1] + fy1 + 2)


SET_BUILDERS = {"home": _home, "bridge": _bridge, "treasure": _treasure}


def _wall_light(collection, lo, hi, watts, name, color):
    """An area light over a vertical lava face (lo, hi = opposite corners in world space, the face lying in a plane
    of constant y), shining toward -Y, smoothed falloff like engine.fixtures' lava lights."""
    from . import fixtures

    data = bpy.data.lights.new(name, "AREA")
    data.shape = "RECTANGLE"
    data.size, data.size_y = abs(hi[0] - lo[0]), abs(hi[2] - lo[2])
    data.color = color
    data.energy = float(watts)
    try:
        data.spread = math.pi
    except (AttributeError, TypeError):
        pass
    fixtures._smooth_falloff(data, fixtures.LAVA_SMOOTH)
    ob = bpy.data.objects.new(name, data)
    ob.location = ((lo[0] + hi[0]) / 2.0, lo[1] - 0.02, (lo[2] + hi[2]) / 2.0)
    ob.rotation_euler = (-math.pi / 2.0, 0.0, 0.0)              # the light's -Z turned to -Y
    ob.visible_camera = False
    ob.visible_glossy = False
    ob["mc_light"] = "lava"
    ob["base_energy"] = data.energy
    collection.objects.link(ob)
    return ob


def build_bastion(scene, layout=None, sets=SETS, seed=6, name="bastion", lantern_watts=None):
    """Build the bastion sets of "Six Seconds" into `scene` and return a Bastion (a Village-like handle for
    films.lookdev.Stage). sets: any of 'home', 'bridge', 'treasure'. layout: {'home' | 'bridge' | 'treasure':
    (x, y, z) set origin, 'pit': (x, y) the pit's south-west cell in home coordinates}. lantern_watts: the point
    light of a lantern (default LANTERN_WATTS, 200 W)."""
    from . import breaking, fixtures

    layout = dict(layout or {})
    unknown = sorted(set(layout) - (set(SETS) | {"pit"}))
    if unknown:
        raise KeyError("build_bastion layout: unknown key(s) %s (known: %s, pit)" % (unknown, ", ".join(SETS)))
    sets = tuple(sets)
    if any(s not in SETS for s in sets):
        raise KeyError("build_bastion sets: %s (known: %s)" % (sets, SETS))
    if "bridge" in sets or "treasure" in sets:
        template_source(quiet=False)                          # say where the game's bastion pieces come from
    bas = Bastion()
    w = World()
    coll = new_collection(scene, name)
    bas.world, bas.collection = w, coll
    bas.layout = dict(layout)
    builders = {}
    for s in sets:
        b = _Builder(bas, w, s, layout.get(s, ORIGINS[s]), seed)
        SET_BUILDERS[s](b, layout)
        builders[s] = b
    # fluids, chests: before the mesh (they claim their cells)
    warm = fixtures.LAVA_LIGHT_COLOR                      # the game's one block-light colour, #FFD88C
    for s, b in builders.items():
        for kind, kw in b.lava:
            kw = dict(kw)
            nm = kw.pop("name")
            if kind == "lava":
                fl = fixtures.lava(bas, kw.pop("cells"), name=nm, color=warm, **kw)
                bas.lava[nm] = fl
            elif kind == "glow":
                fl = fixtures.lava_glow(bas, kw.pop("x0") + b.o[0], kw.pop("y0") + b.o[1], kw.pop("x1") + b.o[0],
                                        kw.pop("y1") + b.o[1], kw.pop("z") + b.o[2], name=nm, color=warm, **kw)
                bas.lava[nm] = fl
            elif kind == "wall_light":
                lo, hi = kw["rect"]
                bas.lava[nm] = _wall_light(coll, lo, hi, kw["watts"], nm, warm)
        for i, (bx, by, bz, p) in enumerate(getattr(b, "chest_cells", ())):
            ch = fixtures.chest(bas, (bx, by, bz), p.get("facing", "south"), animated=True, name="%s_chest_%d" % (s, i))
            bas.chests[ch.name] = ch
    # the mesh, the cutaway sections on their own
    taken = set()
    cut = {}
    for b in builders.values():
        for cname, cells in b.cut.items():
            cut[cname] = {c for c in cells if c in w.blocks}
            taken |= cut[cname]
    bas.objects = w.build(coll, name, skip=taken)
    total = w.last_face_count
    for cname, cells in cut.items():
        sub = World()
        sub._states, sub._state_ids = w._states, w._state_ids
        for c in cells:
            sub.blocks[c] = w.blocks[c]
        bas.cutaways[cname] = sub.build(coll, cname)
        total += sub.last_face_count
    bas.face_count = total
    for ob in coll.objects:
        if ob.type == "MESH" and any(k in ob.name for k in FLAME_GLOW_GROUPS):
            ob.visible_shadow = False                         # a flame must not shadow its own light
    # breakable blocks: the pit (home), the netherrack pillar (bridge)
    for s, b in builders.items():
        for c in getattr(b, "pit", ()):
            blk = breaking.place_block(coll, "blackstone", c, world=bas, name="home_pit_%d_%d_%d" % c)
            bas.pit_blocks[c] = blk
        for c in getattr(b, "pillar", ()):
            blk = breaking.place_block(coll, "netherrack", c, world=bas, name="bridge_pillar_%d" % (c[2] - b.o[2]))
            blk._there0 = False                               # NOT built until pillar_in / pillar_from says so
            blk._rekey()
            bas.pillar.append(blk)
    if bas.pit_blocks:
        top = [c for c in bas.pit_blocks if c[2] == max(k[2] for k in bas.pit_blocks)]
        bottom = [c for c in bas.pit_blocks if c[2] == min(k[2] for k in bas.pit_blocks)]
        # the last block of the dig: a bottom block on the rim_w side (the player digs from the west rim)
        last = min(bottom, key=lambda c: (c[0], c[1]))
        bas.pit_last = bas.pit_blocks[last]
        bas.pit_cells = dict(top=sorted(top), bottom=sorted(bottom), last=last)
        # the pit's fill: a weak shadowless warm point light just under the rim, on only while the pit is dug
        cx = sum(c[0] for c in bas.pit_blocks) / len(bas.pit_blocks) + 0.5
        cy = sum(c[1] for c in bas.pit_blocks) / len(bas.pit_blocks) + 0.5
        data = bpy.data.lights.new("light_home_pit_fill", "POINT")
        data.color = fixtures.LAVA_LIGHT_COLOR
        data.energy = 0.0
        data.shadow_soft_size = 0.6
        data.use_shadow = False
        try:
            data.specular_factor = 0.0
        except (AttributeError, TypeError):
            pass
        ob = bpy.data.objects.new("light_home_pit_fill", data)
        ob.location = (cx, cy, max(k[2] for k in bas.pit_blocks) + 0.35)
        ob.hide_render = True
        ob["group"] = "home_pit_fill"
        ob["base_energy"] = PIT_FILL_WATTS
        coll.objects.link(ob)
        bas.pit_fill = ob                                     # (not a lantern: Stage.lights leaves it alone)
    # lights: one point light per lantern block, in its builder's group
    watts = LANTERN_WATTS if lantern_watts is None else float(lantern_watts)
    for s, b in builders.items():
        for cell, group in sorted(b.groups.items()):
            st = w.get(*cell)
            if st is None or st[0] != "lantern":
                continue
            ob = props.make_light("lantern", coll)
            ob.location = props.flame_position(cell, "lantern", st[1])
            ob.data.energy = watts
            ob["base_energy"] = watts
            ob["group"] = group
            ob.name = "light_%s_%d" % (group, len(bas.lights.get(group, [])))
            bas.lights.setdefault(group, []).append(ob)
            bas.lantern_lights.append(ob)
        bas.sets[s] = dict(origin=b.o, bounds=b.bounds, lights=b.set_lights,
                           anchors=sorted(b.anchors), cameras=sorted(k for k, c in bas.cameras.items() if c["set"] == s))
    # the floor as physics sees it in the shots where the pit is not dug
    whole = World()
    whole._states, whole._state_ids = w._states, w._state_ids
    whole.blocks = dict(w.blocks)
    for c in bas.pit_blocks:
        whole.set(*c, "blackstone")
    bas.whole = types.SimpleNamespace(world=whole, collection=coll, anchors=bas.anchors)
    bas.edit_problems = bas.validate()
    if bas.edit_problems:
        print("[nether] build_bastion problems:\n  " + "\n  ".join(bas.edit_problems[:20]))
    return bas


# ======================================================================================================
# PROOF FILM (rendered through render.py's Session: `$BPY -m engine.nether <still> ...`)
# ======================================================================================================
PROOF_FILM = "nether_proof"      # the film name the self-test registers (films.nether_proof, in memory only)


def _cam(s, bas, name, lens=None, fstop=None, focus=None, pos=None, target=None):
    c = bas.cameras[name]
    s.lens(lens or c["lens"], fstop if fstop is not None else (c["fstop"] or 4.0))
    s.move(pos or c["pos"], target or c["target"])
    if focus is not None:
        s.focus(focus)


def _proof_build(scene):
    """The proof stills as a small film on films.lookdev.Stage (each shot one still; see PROOFS)."""
    from engine import piglins, players, shots

    scene.render.resolution_x, scene.render.resolution_y = 540, 960
    scene.cycles.samples = 16
    bas = build_bastion(scene)
    sky = set_nether(scene, biome="nether_wastes")
    film = shots.Film(scene, fps=24)
    st = Stage(scene, film, bas, sky)
    A, Y = bas.anchors, bas.yaws
    brute = piglins.add_piglin(st, "brute", "brute")
    pigs = [piglins.add_piglin(st, "pig_%d" % k, weapon=("crossbow" if k == 3 else "default")) for k in (1, 2, 3, 4)]
    runner = players.add_player(st, "runner", "steve")
    players.equip(runner, boots="golden")
    runner.hold("iron_pickaxe")
    ingot = piglins.add_item(st, "gold_ingot", name="step_ingot")
    boots = piglins.add_item(st, "golden_boots", name="drop_boots")
    pit_ingot = piglins.add_item(st, "gold_ingot", name="pit_ingot")
    home = bas.lights_for("home")
    for blk in bas.pillar:                                  # the netherrack pillar exists from beat 13 on
        st.cast[blk.name] = blk

    def at_gold(s, who, ks):
        for p, k in zip(who, ks):
            p.place(s.frame_start, A["home_gold_%d" % k], Y["home_gold_%d" % k])
            p.look_at(s.frame_start, A["home_gold_target"], ease=0)
            p.flop_ears(s.frame_start, s.frame_end + 1)

    # 1. landing (beat 1): the brute at frame left on the landing, three piglins far below at the gold wall
    s = st.shot("landing", 1.0)
    brute.place(s.frame_start, A["home_landing_edge"], Y["home_landing_edge"])
    brute.look_at(s.frame_start, Vector(bas.cameras["landing"]["pos"]) + Vector((0.6, 0.0, -0.2)), ease=0)
    brute.flop_ears(s.frame_start, s.frame_end + 1)
    at_gold(s, pigs[:3], (1, 2, 3))
    _cam(s, bas, "landing", fstop=3.2, focus=brute.head)
    st.use(s, brute, *pigs[:3])
    st.hero(s, "brute", brute)
    st.lights(s, 1.0, **home)
    # 2. ingot row (beats 2 / 21): two piglins admiring, the brute beside them over the ingot on the step
    s = st.shot("ingot_row", 1.0)
    for p, k in zip(pigs[1:3], (2, 3)):
        p.place(s.frame_start, A["home_gold_%d" % k], Y["home_gold_%d" % k])
        p.admire(s.frame_start, "gold_ingot")
    brute.place(s.frame_start, A["home_gold_4"], Y["home_gold_4"])
    ingot.place(s.frame_start, A["home_step_4_item"])
    ingot.animate(s.frame_start, s.frame_end + 1)
    brute.look_at(s.frame_start, Vector(A["home_step_4_item"]) + Vector((0, 0, 0.15)), ease=0)
    brute.flop_ears(s.frame_start, s.frame_end + 1)
    _cam(s, bas, "ingot_row", focus=pigs[2].item_point(s.frame_start + 12, "off"))
    st.use(s, brute, pigs[1], pigs[2], ingot)
    st.hero(s, "piglin", pigs[1])
    st.hero(s, "piglin 2", pigs[2])
    st.lights(s, 1.0, **home)
    # 3. gate frame (beat 3): the brute on the landing in profile, the piglins at the gold
    s = st.shot("gate", 1.0)
    brute.place(s.frame_start, A["home_landing"], Y["home_landing"])
    brute.look_at(s.frame_start, Vector(A["home_gateway"]) + Vector((0, 0, 1.6)), ease=0)
    brute.flop_ears(s.frame_start, s.frame_end + 1)
    at_gold(s, pigs[:3], (1, 2, 3))
    _cam(s, bas, "gate", focus=A["home_center"])
    st.use(s, brute, *pigs[:3])
    st.hero(s, "brute", brute)
    st.lights(s, 1.0, **home)
    # 4. gate frame (beat 18): the landing empty, the brute small in the gateway, back to us
    s = st.shot("gate_18", 1.0)
    brute.place(s.frame_start, A["home_gateway"], Y["home_gateway"])
    brute.flop_ears(s.frame_start, s.frame_end + 1)
    at_gold(s, pigs[:3], (1, 2, 3))
    _cam(s, bas, "gate", focus=A["home_center"])
    st.use(s, brute, *pigs[:3])
    st.lights(s, 1.0, **home)
    # 5. pit (beat 6): the pit dug but its last block, piglins in it, the runner at the west rim
    s = st.shot("pit", 1.0)
    bas.pit_open(s, keep=[bas.pit_last.cell])
    for p, k in zip(pigs[1:4], (2, 3, 4)):
        p.place(s.frame_start, A["home_pit_%d" % k], yaw_to(A["home_pit_%d" % k], A["home_rim_w"]))
        p.look_at(s.frame_start, Vector(A["home_rim_w"]) + Vector((0, 0, 1.6)), ease=0)
        p.flop_ears(s.frame_start, s.frame_end + 1)
    runner.place(s.frame_start, A["home_rim_w"], Y["home_rim_w"])
    runner.look_at(s.frame_start, bas.pit_last.center, ease=0)
    pit_ingot.place(s.frame_start, Vector(A["home_pit_1"]) + Vector((0.1, 0.1, 0.0)))
    pit_ingot.animate(s.frame_start, s.frame_end + 1)
    _cam(s, bas, "pit", focus=A["home_pit_center"])
    st.use(s, runner, *pigs[1:4], pit_ingot)
    st.hero(s, "piglin", pigs[2])
    st.lights(s, 1.0, groups={"home_pit": 2.5}, **home)
    # 6. bridge (beat 12): over the runner's shoulder, the brute blocking the bridge under his lantern
    s = st.shot("bridge", 1.0)
    runner.place(s.frame_start, A["bridge_player"], Y["bridge_player"])
    runner.look_at(s.frame_start, Vector(A["bridge_brute"]) + Vector((0, 0, 1.7)), ease=0)
    brute.place(s.frame_start, A["bridge_brute"], Y["bridge_brute"])
    brute.look_at(s.frame_start, runner.head, ease=0)
    brute.flop_ears(s.frame_start, s.frame_end + 1)
    _cam(s, bas, "bridge_shoulder", focus=brute.head)
    st.use(s, runner, brute)
    st.hero(s, "brute", brute)
    st.lights(s, 1.0, **bas.lights_for("bridge"))
    # 7. the bridge wide: pillars, the brute, the lava glow far below
    s = st.shot("bridge_wide", 1.0)
    brute.place(s.frame_start, A["bridge_brute"], Y["bridge_brute"])
    brute.flop_ears(s.frame_start, s.frame_end + 1)
    _cam(s, bas, "bridge_wide", focus=brute.head)
    st.use(s, brute, *bas.pillar)                           # with the netherrack pillar (beats 13-15)
    st.lights(s, 1.0, **bas.lights_for("bridge"))
    # 8. treasure corner (beat 16): the brute locked in frame, a puff beside him, golden boots at his feet
    s = st.shot("treasure", 1.0)
    brute.place(s.frame_start, A["treasure_flash"], Y["treasure_flash"])
    brute.flop_ears(s.frame_start, s.frame_end + 1)
    spot = Vector(A["treasure_flash"]) + Vector((1.2, -0.2, 0.0))
    piglins.poof(spot, s.frame_start - 8, camera=s, size=(0.6, 1.8), seed=3)
    boots.place(s.frame_start, Vector(A["treasure_flash"]) + Vector((0.55, -0.75, 0.0)))
    boots.animate(s.frame_start, s.frame_end + 1)
    _cam(s, bas, "treasure_flash", focus=brute.head)
    st.use(s, brute, boots)
    st.hero(s, "brute", brute)
    st.lights(s, 1.6, **bas.lights_for("treasure"))
    st.finish()
    return {"film": film, "captions": [], "stage": st, "bastion": bas}


# still name -> (shot, seconds into the shot)
PROOFS = {"landing": ("landing", 0.5), "ingot_row": ("ingot_row", 0.5), "gate": ("gate", 0.5),
          "gate_18": ("gate_18", 0.5), "pit": ("pit", 0.5), "bridge": ("bridge", 0.5),
          "bridge_wide": ("bridge_wide", 0.5), "treasure": ("treasure", 0.5)}


def register_proof_film():
    """Make the proof film importable as films.nether_proof (in memory: no file is written) for render.py."""
    import sys

    mod = types.ModuleType("films." + PROOF_FILM)
    mod.__file__ = os.path.abspath(__file__)
    mod.build = _proof_build
    sys.modules["films." + PROOF_FILM] = mod
    return mod


# ---- every camera suggestion rendered once, with the cast its note describes (`$BPY -m engine.nether cams`) ----
CAMS_FILM = "nether_cams"
_CAMS = []                       # the camera names the cams film is built with (set by render_cams)


def _stage_cam(st, s, bas, name, pool):
    """Stage camera suggestion `name` in shot s as its note describes: its cast at their anchors, its lens, aim and
    focus, its pit / pillar state, its set's lights. pool = {kind: [actors]}. Returns the actors used."""
    from engine import piglins  # noqa: F401  (pool members are piglins / players / items)

    c = bas.cameras[name]
    A, Y = bas.anchors, bas.yaws
    used, vis = {}, []
    for entry in c["cast"]:
        kind, where, look = entry[:3]
        k = "steve" if kind.startswith("steve") else "piglin" if kind.startswith("piglin") else kind
        ob = pool[k][used.get(k, 0)]
        used[k] = used.get(k, 0) + 1
        p = A[where] if isinstance(where, str) else where
        if k == "ingot":
            ob.place(s.frame_start, p)
            ob.animate(s.frame_start, s.frame_end + 1)
        else:
            yaw = entry[3] if len(entry) > 3 else (Y.get(where, 0.0) if isinstance(where, str) else 0.0)
            ob.place(s.frame_start, p, yaw)
            if look is not None:
                ob.look_at(s.frame_start, Vector(A[look] if isinstance(look, str) else look), ease=0)
            if kind == "steve_crouch":
                ob.sneak(s.frame_start)
            if kind == "piglin_admire":
                ob.admire(s.frame_start, "gold_ingot")
            if k != "steve":
                ob.flop_ears(s.frame_start, s.frame_end + 1)
        vis.append(ob)
    if c["pit"]:
        bas.pit_open(s, keep=[bas.pit_last.cell] if c["pit"] == "keep" else ())
    if c["pillar"]:
        bas.pillar_in(s)
    s.lens(c["lens"], c["fstop"] or 4.0)
    s.move(c["pos"], c["target"])
    f = c.get("focus")
    s.focus(A[f] if isinstance(f, str) else (f or c["target"]))
    st.use(s, *vis)
    st.lights(s, 1.0, groups=c["lights"] or None, **bas.lights_for(c["set"]))
    return vis


def _cams_build(scene):
    """One one-second shot per camera in _CAMS, staged by _stage_cam."""
    from engine import piglins, players, shots

    scene.render.resolution_x, scene.render.resolution_y = 540, 960
    scene.cycles.samples = 16
    bas = build_bastion(scene)
    sky = set_nether(scene, biome="nether_wastes")
    film = shots.Film(scene, fps=24)
    st = Stage(scene, film, bas, sky)
    pool = {"brute": [piglins.add_piglin(st, "brute", "brute")],
            "piglin": [piglins.add_piglin(st, "pig_%d" % k, weapon=("crossbow" if k == 3 else "default"))
                       for k in (1, 2, 3, 4)],
            "steve": [players.add_player(st, "runner", "steve")],
            "ingot": [piglins.add_item(st, "gold_ingot", name="ingot_%d" % k) for k in (1, 2)]}
    players.equip(pool["steve"][0], boots="golden")
    pool["steve"][0].hold("iron_pickaxe")
    for name in _CAMS:
        s = st.shot(name, 1.0)
        _stage_cam(st, s, bas, name, pool)
    st.finish()
    return {"film": film, "captions": [], "stage": st, "bastion": bas}


def render_cams(names=None, res=(270, 480), samples=12):
    """Render every camera suggestion (or `names`) once through render.Session with the cast its note describes:
    out/test/nether_cam_<name>.png (frame 12 of its shot), and a contact sheet out/test/nether_cams_sheet.png.
    Returns the paths."""
    import sys

    import render as R
    from PIL import Image, ImageDraw

    global _CAMS
    tag = "_" + names[0] if names else ""
    if not names:
        bpy.ops.wm.read_factory_settings(use_empty=True)
        names = sorted(build_bastion(bpy.context.scene).cameras)
    _CAMS = list(names)
    mod = types.ModuleType("films." + CAMS_FILM)
    mod.__file__ = os.path.abspath(__file__)
    mod.build = _cams_build
    sys.modules["films." + CAMS_FILM] = mod
    ses = R.Session(CAMS_FILM)
    ses.configure(tuple(res), samples, 2, None)
    paths = []
    for name in _CAMS:
        s = next(x for x in ses.film.shots if x.name == name)
        path = os.path.join(ROOT, "out", "test", "nether_cam_%s.png" % name)
        ses.render_frame(s.frame_start + 12, path)
        print("[nether] camera %s -> %s" % (name, path), flush=True)
        paths.append(path)
    ims = [Image.open(p).convert("RGB") for p in paths]
    cols = min(6, len(ims))
    rows = (len(ims) + cols - 1) // cols
    W, H = ims[0].size
    sheet = Image.new("RGB", (cols * (W + 6), rows * (H + 22)), (20, 20, 20))
    d = ImageDraw.Draw(sheet)
    for i, (im, n) in enumerate(zip(ims, _CAMS)):
        x, y = (i % cols) * (W + 6), (i // cols) * (H + 22)
        sheet.paste(im, (x, y + 20))
        beats = ses.result["bastion"].cameras[n]["beats"]
        d.text((x + 4, y + 4), "%s %s" % (n, "beats " + " ".join(map(str, beats)) if beats else ""), fill=(255, 230, 90))
    sheet_path = os.path.join(ROOT, "out", "test", "nether_cams_sheet%s.png" % tag)
    sheet.save(sheet_path)
    print("[nether] sheet ->", sheet_path)
    return paths



# ======================================================================================================
# CHECKS ON A RENDERED STILL (the Nether's own palette rules; tools/palette_check.py does the rest)
# ======================================================================================================
GOLD_HUE = (38.0, 58.0)          # gold_block.png's lit texels are hue 45-52: under the lanterns it must stay gold,
#                                  not orange (< 38) nor lemon (> 58)
GOLD_MIN_SAT = 0.45              # ... and not washed to cream or white
BRUTE_SEPARATION = 1.5           # the brute's median luminance over the blackstone's in the same frame
SKIN_HUE = (0.0, 30.0)           # piglin skin (texture hue 5-15): pink, never orange-red


def _lum(rgb):
    return 0.2126 * rgb[..., 0] + 0.7152 * rgb[..., 1] + 0.0722 * rgb[..., 2]


def check_still(scene, image_path, heroes=(), report=True):
    """Measure a rendered Nether still against the game textures under each pixel (tools.palette_check.probe):
    gold reads as gold, the brute separates from blackstone, piglin skin stays pink; plus palette_check's own
    checks that apply in a bastion (Steve's clothes, the heroes' safe area). Returns palette_check's report with the
    Nether checks added (report['failed'] lists every failure)."""
    import colorsys

    from PIL import Image
    from tools import palette_check as pc

    rec = pc.probe(scene)
    rep = pc.evaluate(rec, image_path, heroes=heroes)
    img = np.asarray(Image.open(image_path).convert("RGB")).astype(np.float32)
    gx, gy = rec["grid"]
    h, w = img.shape[:2]
    mat, alb = rec["material"], rec["albedo"]
    js, is_ = np.mgrid[0:gy, 0:gx]
    ys = np.clip(((js + 0.5) / gy * h).astype(int), 0, h - 1)
    xs = np.clip(((is_ + 0.5) / gx * w).astype(int), 0, w - 1)
    pix = img[ys, xs]

    def cls(pred):
        m = np.array([[pred(s) for s in row] for row in mat])
        return pc._interior(m)

    def hsv(c):
        hh, ss, vv = colorsys.rgb_to_hsv(*[float(v) / 255.0 for v in c])
        return hh * 360.0, ss, vv

    checks, colours = rep["checks"], rep["colours"]

    def add(name, ok, text):
        checks.append((name, bool(ok), text))

    gold = cls(lambda s: s == "mc/block/gold_block")
    stone = cls(lambda s: "blackstone" in s or "basalt" in s)
    brute = cls(lambda s: s == "cast_piglin_brute")
    skin_tex = np.zeros(mat.shape, bool)
    for j in range(gy):
        for i in range(gx):
            if mat[j, i] == "cast_piglin_piglin" and not np.isnan(alb[j, i, 0]):
                hh, ss, vv = colorsys.rgb_to_hsv(*alb[j, i])
                skin_tex[j, i] = (hh * 360 < 25 or hh * 360 > 350) and 0.2 < ss < 0.55 and vv > 0.6
    skin = pc._interior(skin_tex)
    if gold.sum() >= pc.MIN_PIXELS:
        c = pix[gold]
        lit = c[c.max(axis=1) > 60]
        if len(lit) >= pc.MIN_PIXELS:
            m = np.median(lit, axis=0)
            hh, ss, vv = hsv(m)
            colours["gold"] = tuple(int(v) for v in m)
            add("gold reads as gold", GOLD_HUE[0] <= hh <= GOLD_HUE[1] and ss >= GOLD_MIN_SAT,
                "lit gold rgb(%d,%d,%d): hue %.0f (%g..%g), s %.2f (>= %.2f)" % (m[0], m[1], m[2], hh, GOLD_HUE[0],
                                                                                GOLD_HUE[1], ss, GOLD_MIN_SAT))
    if stone.sum() >= pc.MIN_PIXELS:
        colours["blackstone"] = tuple(int(v) for v in np.median(pix[stone], axis=0))
    if brute.sum() >= pc.MIN_PIXELS and stone.sum() >= pc.MIN_PIXELS:
        lb, ls = float(np.median(_lum(pix[brute]))), float(np.median(_lum(pix[stone])))
        colours["brute"] = tuple(int(v) for v in np.median(pix[brute], axis=0))
        add("brute separates from blackstone", lb >= BRUTE_SEPARATION * max(ls, 1.0) and lb >= 25.0,
            "brute luminance %.0f vs blackstone %.0f: x%.2f (>= %.1f, and >= 25)" % (lb, ls, lb / max(ls, 1.0),
                                                                                  BRUTE_SEPARATION))
    if skin.sum() >= pc.MIN_PIXELS:
        c = pix[skin]
        lit = c[c.max(axis=1) > 50]
        if len(lit) >= pc.MIN_PIXELS:
            m = np.median(lit, axis=0)
            hh, ss, vv = hsv(m)
            colours["piglin skin"] = tuple(int(v) for v in m)
            add("piglin skin stays pink", (SKIN_HUE[0] <= hh <= SKIN_HUE[1] or hh >= 350) and ss <= 0.62,
                "lit piglin skin rgb(%d,%d,%d): hue %.0f (0..30), s %.2f (<= 0.62; texture 0.25-0.45)"
                % (m[0], m[1], m[2], hh, ss))
    rep["failed"] = [c for c in checks if not c[1]]
    if report:
        pc.print_report(os.path.basename(image_path)[:-4], rep)
        print("[check] colours: %s" % {k: v for k, v in colours.items()})
    return rep


# ======================================================================================================
# SELF-TEST
# ======================================================================================================
REQUIRED_ANCHORS = (
    ["home_landing", "home_landing_edge", "home_gateway", "home_corridor", "home_entry", "home_boot_mark",
     "home_flash", "home_pit_center", "home_rim_w", "home_rim_s", "home_rim_e", "home_rim_n", "home_stair_foot"]
    + ["home_gold_%d" % k for k in (1, 2, 3, 4)] + ["home_step_%d_item" % k for k in (1, 2, 3, 4)]
    + ["home_pit_%d" % k for k in (1, 2, 3, 4)] + ["home_pit_drop_%d" % k for k in (1, 2, 3)]
    + ["bridge_start", "bridge_boot_mark", "bridge_player", "bridge_brute", "bridge_middle", "bridge_pillar_foot",
       "bridge_pillar_top", "bridge_flash", "treasure_flash"])


def _check():
    """Numbers and invariants (no rendering). Returns the number of failures."""
    fails = []

    def ok(cond, text):
        print("[nether] %-4s %s" % ("ok" if cond else "FAIL", text))
        if not cond:
            fails.append(text)

    # the game's numbers
    ok(fog_amount(10.0) == 0.0 and fog_amount(96.0) == 1.0 and abs(fog_amount(53.0) - 0.5) < 1e-9,
       "fog: 0 at 10 blocks, 0.5 at 53, 1 at 96 (the_nether.json fog_start / fog_end, fog.glsl linear)")
    l0 = lightmap(0)
    ok(np.allclose(l0, (0.377, 0.315, 0.259), atol=0.01), "lightmap level 0 at default brightness: %s (the ambient "
       "#302821 through lightmap.fsh's notGamma mix 0.5)" % np.round(l0, 3))
    ok(lightmap(15)[0] == 1.0, "lightmap level 15 clips to white")
    ok(set(BASTION_BIOMES) <= set(FOG_COLORS), "every bastion biome has its fog colour")
    ok(degrade("polished_blackstone_bricks", "bridge", (1, 2, 3)) in ("polished_blackstone_bricks",
                                                                      "cracked_polished_blackstone_bricks"),
       "processor rules give the game's outputs")
    n = 20000
    cracked = sum(degrade("polished_blackstone_bricks", "bastion_generic_degradation", (i, i * 7, i % 13)) !=
                  "polished_blackstone_bricks" for i in range(n)) / n
    ok(abs(cracked - 0.3) < 0.02, "bastion_generic_degradation cracks %.3f of polished blackstone bricks (0.3)" % cracked)
    kind, where = template_source()
    leg = load_template("bridge/legs/leg_0")
    ok(leg.size == (3, 22, 3) and len(leg.blocks) > 100, "bastion template bridge/legs/leg_0 from %s: size %s, %d blocks"
       % (kind, leg.size, len(leg.blocks)))
    # a build
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    look.setup_render(scene, res=(270, 480), samples=4, threads=2, motion_blur=False)
    import time
    t = time.time()
    bas = build_bastion(scene)
    sky = set_nether(scene)
    ok(True, "build_bastion + set_nether in %.1f s: %d faces, %d lantern lights, %d lava bodies / lights"
       % (time.time() - t, bas.face_count, len(bas.lantern_lights), len(bas.lava)))
    ok(not bas.edit_problems, "validate(): %s" % (bas.edit_problems or "no problems"))
    missing = [a for a in REQUIRED_ANCHORS if a not in bas.anchors]
    ok(not missing, "anchors present (%d)%s" % (len(REQUIRED_ANCHORS), " missing %s" % missing if missing else ""))
    w = bas.world
    gx, gy0, gy1, gz1 = HOME["gold"]
    golds = [w.block_id(gx, y, z) for y in range(gy0, gy1 + 1) for z in range(0, gz1 + 1)]
    ok(all(g == "gold_block" for g in golds), "gold wall: %d gold blocks at x %d, y %d..%d" % (len(golds), gx, gy0, gy1))
    ok(all(w.block_id(HOME["step"], y, 0) == "blackstone" for y in range(gy0, gy1 + 1)), "the step is blackstone")
    pit = sorted(bas.pit_blocks)
    ok(len(pit) == 8 and all(w.block_id(*c) is None for c in pit) and
       all(bas.whole.world.block_id(*c) == "blackstone" for c in pit),
       "pit: 8 Breakables, absent from the World (physics: dug), present in Bastion.whole")
    px, py = HOME["pit"]
    around = [(x, y, z) for z in (-1, -2) for x in range(px - 1, px + 3) for y in range(py - 1, py + 3)
              if not (px <= x <= px + 1 and py <= y <= py + 1)] + [(x, y, -3) for x in (px, px + 1) for y in (py, py + 1)]
    ok(all(w.block_id(*c) == "blackstone" for c in around), "the pit's walls and floor are plain blackstone")
    x0p, y0p, x1p, y1p = HOME["plain"]
    patch = {w.block_id(x, y, -1) for x in range(x0p, x1p + 1) for y in range(y0p, y1p + 1)} - {None}
    ok(patch == {"blackstone"}, "the floor round the pit is plain blackstone (%s)" % sorted(patch))
    ok(bas.pit_last is not None and bas.pit_last.cell[2] == -2, "pit_last %s is a bottom block" % (bas.pit_last.cell,))
    bas.pit_open((50, 70), keep=[bas.pit_last.cell])
    bas.pit_open((71, 90))
    other = next(b for c, b in bas.pit_blocks.items() if c != bas.pit_last.cell)
    ok(other.there_at(49) and not other.there_at(50) and not other.there_at(80) and other.there_at(91),
       "pit_open: a block is there before, gone during two consecutive pit shots, back after")
    ok(bas.pit_last.there_at(60) and not bas.pit_last.there_at(75) and bas.pit_last.there_at(91),
       "pit_open(keep=...): the kept block stays for its on-camera break")
    ok(bas.pit_state(60) == "digging" and bas.pit_state(80) == "open" and bas.pit_state(95) == "whole", "pit_state")
    groups = sorted(bas.lights)
    ok({"home_landing", "home_gate", "home_gold", "home_pit", "bridge_lantern", "treasure"} <= set(groups),
       "light groups %s" % groups)
    lanterns = [c for c, sid in w.blocks.items() if w._states[sid][0] == "lantern"]
    ok(len(lanterns) == len(bas.lantern_lights), "every lantern block has its light (%d)" % len(lanterns))
    ok(len(bas.pillar) == 3 and all(w.block_id(*b.cell) is None for b in bas.pillar),
       "netherrack pillar: 3 Breakables (not in the World)")
    ok(scene.world.mist_settings.start == FOG_START and abs(scene.world.mist_settings.depth - (FOG_END - FOG_START)) < 1e-6
       and scene.world.mist_settings.falloff == "LINEAR", "mist = the game's fog distances, linear")
    ok(not [o for o in scene.objects if o.type == "LIGHT" and o.data.type == "SUN" and o.data.use_shadow],
       "no sun or moon: every sun lamp is a shadowless fill")
    ok(bpy.data.node_groups.get(look.COMP_GROUP) is not None and scene.world is not None,
       "compositor group '%s' and world present (render.Session keeps them)" % look.COMP_GROUP)
    for name, c in bas.cameras.items():
        if c["set"] in bas.sets and math.dist(c["pos"], c["target"]) < 0.5:
            ok(False, "camera %s has no direction" % name)
    print("[nether] check: %d failure(s)" % len(fails))
    return len(fails)


def render_proofs(names, res=(540, 960), samples=16, check=True):
    """Render proof stills (PROOFS) through render.py's Session: out/test/nether_<name>.png. Returns failures."""
    import time

    import render as R

    register_proof_film()
    ses = R.Session(PROOF_FILM)
    ses.configure(tuple(res), samples, 2, None)
    failed = 0
    for n in names:
        shot, sec = PROOFS[n]
        s = next(x for x in ses.film.shots if x.name == shot)
        f = s.frame_start + int(round(sec * 24))
        path = os.path.join(ROOT, "out", "test", "nether_%s.png" % n)
        t = time.time()
        ses.render_frame(f, path)
        print("[nether] %s: frame %d -> %s  %.1fs" % (n, f, path, time.time() - t), flush=True)
        if check:
            rep = check_still(ses.scene, path, heroes=ses.result["stage"].heroes.get(shot, ()))
            failed += len(rep["failed"])
    return failed


def render_maps(sets=SETS, res=(540, 960)):
    """Top-down orthographic map of each set with its anchors and camera suggestions marked:
    out/test/nether_map_<set>.png (flat light, no haze: a plan, not a picture)."""
    from PIL import Image, ImageDraw

    out = []
    for set_name in sets:
        bpy.ops.wm.read_factory_settings(use_empty=True)
        scene = bpy.context.scene
        look.setup_render(scene, res=res, samples=8, threads=2, motion_blur=False)
        bas = build_bastion(scene)
        set_nether(scene, haze=0.0, bloom=0.0, vignette=0.0, ambient=3.0)
        x0, y0, x1, y1 = bas.sets[set_name]["bounds"]
        cx, cy = (x0 + x1 + 1) / 2.0, (y0 + y1 + 1) / 2.0
        aspect = res[0] / float(res[1])
        scale = max(y1 - y0 + 3, (x1 - x0 + 3) / aspect)
        cam = bpy.data.cameras.new("map")
        cam.type = "ORTHO"
        cam.ortho_scale = scale
        cam.clip_start, cam.clip_end = 0.1, 200.0
        ob = bpy.data.objects.new("map", cam)
        ob.location = (cx, cy, 40.0)
        scene.collection.objects.link(ob)
        scene.camera = ob
        sun = bpy.data.lights.new("map_sun", "SUN")
        sun.energy, sun.angle, sun.use_shadow = 3.0, math.radians(30), True
        so = bpy.data.objects.new("map_sun", sun)
        so.rotation_euler = (math.radians(25), math.radians(15), 0.0)
        scene.collection.objects.link(so)
        for p in bas.pit_blocks.values():
            p.object.hide_render = True                       # the map shows the pit dug
        for cname in ("home_corridor_roof",):
            if cname in bas.cutaways:
                bas.cutaway(cname, hide=True)                 # ... and the corridor without its roof
        path = os.path.join(ROOT, "out", "test", "nether_map_%s.png" % set_name)
        scene.render.filepath = path
        bpy.ops.render.render(write_still=True)
        im = Image.open(path).convert("RGB")
        d = ImageDraw.Draw(im)
        W, H = im.size

        def uv(p):
            return (W * (0.5 + (p[0] - cx) / (scale * aspect)), H * (0.5 - (p[1] - cy) / scale))

        for name, p in sorted(bas.anchors.items()):
            if not name.startswith(set_name):
                continue
            u, v = uv(p)
            d.rectangle((u - 3, v - 3, u + 3, v + 3), fill=(80, 220, 255))
            d.text((u + 5, v - 6), name[len(set_name) + 1:], fill=(80, 220, 255))
        for name, c in sorted(bas.cameras.items()):
            if c["set"] != set_name:
                continue
            u, v = uv(c["pos"])
            tu, tv = uv(c["target"])
            k = 26.0 / max(1e-6, math.hypot(tu - u, tv - v))
            d.line((u, v, u + (tu - u) * k, v + (tv - v) * k), fill=(255, 230, 90), width=2)
            d.ellipse((u - 4, v - 4, u + 4, v + 4), outline=(255, 230, 90), width=2)
            d.text((u + 6, v + 2), "cam " + name, fill=(255, 230, 90))
        d.text((8, 8), "%s  (x %d..%d, y %d..%d; +Y = north up)" % (set_name, x0, x1, y0, y1), fill=(255, 255, 255))
        im.save(path)
        print("[nether] map", set_name, "->", path)
        out.append(path)
    return out


SKIES_PROOF = {"wastes": dict(preset="nether", biome="nether_wastes"),
               "crimson": dict(preset="nether", biome="crimson_forest", haze=1.2),
               "soul": dict(preset="nether", biome="soul_sand_valley")}


def _skies_build(scene, sky=None):
    """A three-sky Nether film (one shot per sky, the same gate frame) built with nether.Stage(skies=..., sky=...)."""
    from engine import piglins, shots

    scene.render.resolution_x, scene.render.resolution_y = 540, 960
    scene.cycles.samples = 16
    bas = build_bastion(scene, sets=("home",))
    film = shots.Film(scene, fps=24)
    st = Stage(scene, film, bas, skies=SKIES_PROOF, sky=sky)
    brute = piglins.add_piglin(st, "brute", "brute")
    for name in SKIES_PROOF:
        s = st.shot("gate_" + name, 1.0, sky=name)
        brute.place(s.frame_start, bas.anchors["home_landing"], bas.yaws["home_landing"])
        _cam(s, bas, "gate", focus=bas.anchors["home_center"])
        st.use(s, brute)
        st.lights(s, 1.0, **bas.lights_for("home"))
    st.finish()
    return {"film": film, "captions": [], "stage": st}


def _skies_proof():
    """render.Session builds each sky of a Nether film with SKIES in-process (as render.py's sky processes do) and
    renders its frame: out/test/nether_sky_<sky>.png. Returns failures."""
    import sys

    import render as R

    mod = types.ModuleType("films.nether_skies")
    mod.__file__ = os.path.abspath(__file__)
    mod.SKIES = SKIES_PROOF
    mod.build = _skies_build
    sys.modules["films.nether_skies"] = mod
    fails = 0
    for k, name in enumerate(SKIES_PROOF):
        ses = R.Session("nether_skies", sky=name)
        f = 1 + 24 * k + 12
        ok = ses.sky_of(f) == name and ses.owns(f)
        try:
            ses.require(1 + 24 * ((k + 1) % len(SKIES_PROOF)) + 12)
            refused = False
        except R.SkyError:
            refused = True
        print("[nether] sky %s: table %s, owns its frame %s, refuses another sky's frame %s"
              % (name, ses.segments, ok, refused))
        fails += (not ok) + (not refused)
        ses.configure((540, 960), 16, 2, None)
        ses.render_frame(f, os.path.join(ROOT, "out", "test", "nether_sky_%s.png" % name))
    return fails


if __name__ == "__main__":
    import sys

    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    code = 0
    if not args or "check" in args:
        code += _check()
    if "cams" in args:                                      # cams [camera names]: every suggestion rendered once
        render_cams([a for a in args if a not in ("cams", "check")] or None)
        sys.exit(1 if code else 0)
    if "map" in args:
        render_maps()
    if "cli" in args:                                       # the render.py command line itself, on the proof film
        import render as R
        register_proof_film()
        code += R.main([PROOF_FILM, "--still", "2.5", "--zones"]) or 0
    if "skies" in args:
        code += _skies_proof()
    want = [a for a in args if a in PROOFS]
    if "proofs" in args:
        want = list(PROOFS)
    if want:
        code += render_proofs(want)
    sys.exit(1 if code else 0)
