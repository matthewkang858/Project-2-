# Minecraft village shorts — build contract (v2: real game assets)

Goal: two ~12 s vertical shorts (Instagram Reels) that are instantly recognisable as **Minecraft**, shot like a
cinematic "Minecraft with shaders" animation: real Minecraft textures, block models, villagers, Steve, font and
vanilla village buildings, rendered with Blender 5.3 Cycles on CPU, with word-by-word captions. Everything is
built by Python scripts from the extracted game files (no hand-made .blend files), so builds are reproducible.

## Hard rules

- **Use the real game files.** Everything visible comes from the official Minecraft: Java Edition 26.3 files
  extracted under `assets/mc/` (fetched by `tools/fetch_assets.py` from Mojang's own servers):
  - `assets/mc/assets/minecraft/textures/{block,entity,item,environment,font,colormap,...}`
  - `assets/mc/assets/minecraft/models/{block,item}/*.json`, `assets/mc/assets/minecraft/blockstates/*.json`
  - `assets/mc/data/minecraft/structure/village/**.nbt` (vanilla village buildings; read with `engine/structures.py`)
  Never substitute hand-drawn or procedural art for something that exists in the game files. If it looks
  "like a knockoff", it is wrong: compare against your memory of the real game and fix it.
- **Never commit or redistribute game files.** `assets/mc/` and `assets/tex/` are git-ignored; keep it that way.
  Do not download assets from anywhere else. Do not run git.
- Entity geometry (villager, player, bell body) is not in JSON. Build boxes at the exact vanilla dimensions and
  UV-map each face to the vanilla texture layout (standard box unwrap at the vanilla texture offsets), then
  verify by rendering and looking: faces, hats, robe overlays and sleeves must sit exactly as in the game.
- Blender is the pip module `bpy` 5.3.0. Run scripts from the project root as modules:
  `cd /home/user/Project-2-/minecraft-shorts && $BPY -m engine.blocks`
  where `BPY=/tmp/claude-0/-home-user-Project-2-/be90bb9d-3fc7-572c-941a-ff79c8b6ef48/scratchpad/bl/bin/python`.
  (numpy and pillow are installed there. There is no `blender` binary and no GPU.)
- Blender 5.x changed parts of the Python API. When a call fails, introspect (`dir()`, `bl_rna.properties`)
  instead of guessing. Known: compositor tree is `scene.compositing_node_group` (not `scene.node_tree`);
  `use_nodes` is deprecated but harmless; Principled inputs are `Specular IOR Level`, `Emission Color`,
  `Emission Strength`. EEVEE is NOT available here (no EGL) — Cycles CPU only.
- Prefer the data API (`bpy.data.*`, `bmesh`, `obj.keyframe_insert`) over `bpy.ops.*` (ops are fragile headless).
- The machine has 4 CPU cores shared by several agents. Test stills: 540x960, <=16 samples, 2 threads
  (`engine/quick.py` does this). Wrap every render command in `timeout 300`. Never launch a long render.
- **Look at what you render.** After each test render, open the PNG with the Read tool and judge it as a
  picture. Iterate until it looks right, not until it merely runs. To inspect a small texture PNG, upscale it
  first (nearest neighbour, e.g. x8) into out/test/ and Read that.
- Only edit the files you own (listed per role). `engine/pix.py`, `engine/quick.py`, `engine/structures.py`
  are finished and shared.

## History you must know

A first pass built `engine/blocks.py`, `engine/props.py`, `engine/village.py` and `engine/characters.py` with
original procedural pixel art. The architecture, rig/animation code and API are good; **the art is rejected**
(it must be real Minecraft). Reuse the code where it helps, replace every procedural texture and guessed
model with the real ones.

## Conventions

- Blender: Z up, 1 block = 1 unit, 1 texture pixel = 1/16 unit. Block (x, y, z) occupies [x,x+1]x[y,y+1]x[z,z+1].
  Minecraft coordinates (x east, y up, z south) map to Blender as **(x, -z, y)** (a pure rotation, no mirroring),
  so Minecraft north (-z) is Blender +Y. Ground surface is at Blender z = 0 in the village square.
- 24 fps. Final frames render at 720x1280 and are upscaled to 1080x1920 in post; captions are drawn at 1080x1920.
- Characters stand with feet at their root empty, facing **-Y** at yaw 0. Yaw is rotation about Z in radians.
- Motion blur: shutter 0.5 frame, opening ON the frame (`motion_blur_position = 'START'`), so frame f is exposed
  over [f, f+0.5]. Anything that jumps for frame f (a cut) must be keyed strictly inside **(f-0.5, f]**: integer-frame
  CONSTANT keys are fine (cameras, lights, visibility), and `characters` keys its cuts at f-0.25. A cut keyed at
  exactly f-0.5 is sampled by frame f-1 and turns the character into a ghost on the last frame before the cut.
- All textures use Closest filtering (`pix.pixel_material` or equivalent). Animated textures (.mcmeta strips):
  use the first frame. Biome tint: plains (grass about #91BD59, foliage about #77AB2F; or sample
  `textures/colormap/*.png` properly). Seed every random generator.
- Every public function has a one-line docstring. Every engine module has an `if __name__ == "__main__":`
  self-test that renders stills to `out/test/<module>_*.png` using `engine/quick.py`.
- Performance budget for a final frame: <= ~15 s at 720x1280, 24 samples, 4 threads. Keep the whole set
  under ~250k faces; cull hidden faces between full cubes; use point lights (not only emissive meshes) for
  torches and lanterns.

## Art direction (see the three reference screenshots given in your brief)

- The world is vanilla Minecraft; the photography is cinematic: low camera, long lens, strong shallow depth of
  field, motion blur, slow moves, like a shader-pack cinematic.
- Late-afternoon gold, dusk orange-to-purple, and moonlit night with warm torch/lantern light that blooms.
- Sky: vertical colour gradient, the real square sun / moon textures with a soft glow, small square stars at
  night, flat blocky clouds.
- Villagers are vanilla plains villagers with their real profession outfits; the nitwit wears the real green
  robe. The player is Steve (`textures/entity/player/wide/steve.png`).

## Module API (signatures are the contract; add helpers freely)

### `engine/pix.py`, `engine/quick.py` — DONE
`pix`: `rng(seed)`, `rgba('#rrggbb', a)`, `image_from_array(name, HxWx4 uint8) -> Image`,
`pixel_material(name, image, emission=0.0, alpha='OPAQUE'|'CLIP'|'BLEND', roughness=0.9) -> Material`,
`flat_material(name, (r,g,b,a), emission=0.0, roughness=0.9)`.
`quick` (test stage only): `reset() -> scene`, `setup(scene, res, samples, threads)`,
`light(scene, 'day'|'golden'|'night')`, `camera(scene, pos, target, lens, fstop)`, `render(scene, name) -> path`.

### `engine/structures.py` — DONE
`load_template('village/plains/houses/plains_small_house_1') -> Template` with `.size` (x, y, z in Minecraft
axes) and `.blocks = [(x, y, z, block_id, props_dict), ...]` (jigsaw blocks already replaced by their final
state; air and structure voids dropped). `list_templates('village/plains')`, `parse_state('oak_stairs[facing=east]')`.
Run `python3 -m engine.structures` to list every plains template with its size (no Blender needed).
Notes: vanilla plains buildings are lit with torches/wall torches; town centres (`town_centers/plains_meeting_point_1..3`,
`plains_fountain_01`) contain the bell; houses contain oak doors and white/yellow beds; `plains_lamp_1` is the lamp post.

### Role SET owns `engine/mcassets.py`, `engine/blocks.py`, `engine/props.py`, `engine/village.py`, `tools/`

```python
# mcassets.py — the only place that reads assets/mc (look, characters and captions go through texture_array /
#               texture_meta / list_textures; captions alone falls back to the same PNG when bpy is not importable)
texture(path) -> bpy.types.Image            # e.g. texture('block/oak_planks'), texture('entity/villager/villager'); first frame of animated strips
material(path, tint=None, alpha=..., emission=0.0) -> Material     # cached, Closest filtering
resolve_blockstate(block_id, props) -> list[ModelPart]             # variants AND multipart, with x/y rotations and uvlock
load_model('block/oak_stairs') -> resolved elements (parents merged, texture variables resolved, face uv/rotation/cullface/tintindex)
item_object(item_id) -> Object              # held item built from the item texture as a thin extruded sprite (e.g. 'emerald')

# blocks.py
class World:                                # block states in BLENDER grid coordinates
    def set(self, x, y, z, block_id, props=None): ...
    def get(self, x, y, z) -> tuple[str, dict] | None: ...
    def fill(self, x0, y0, z0, x1, y1, z1, block_id, props=None): ...          # inclusive
    def place_template(self, template, origin, rot=0): ...   # origin in Blender coords, rot in quarter turns; rotates facing/axis props too
    def is_solid(self, x, y, z) -> bool: ...
    def build(self, collection, name="world", skip=()) -> list[bpy.types.Object]: ...
        # real models for every block: cubes, stairs, slabs, fences, panes, doors, trapdoors, torches, lanterns, beds,
        # crops, cross plants, lectern, composter, bell frame ...; cullface between opaque full cubes; correct UVs,
        # per-face rotation and tint; cut-out alpha for plants/glass/doors. `skip` = positions built as separate props.
        # Elements with "shade_direction_override": "up" (cross plants, crops, torches, lanterns ...) are lit like
        # an up-facing surface from every side, as in the game (up normals + a two-sided material for the
        # zero-thickness ones): a backlit plant is grass-green, not black.

# props.py — separately animatable things, built from the same real models/textures
make_bell(attachment="floor", facing="north") -> Object     # pivot at the hinge; rotate about local X to swing (bell body uses entity/bell/bell_body.png)
make_door(block_id="oak_door", hinge="left") -> Object      # hinge pivot; rotate about Z to open; both halves
make_item(item_id) -> Object                                # same as mcassets.item_object
make_light(kind="torch"|"lantern") -> Object                # warm point light sized for that block (near field flattened:
                                                            #   the block a torch sits on keeps its texture); kind "fill" =
                                                            #   the weak cool shadowless room fill of filmed interiors

# village.py
def build_village(scene, seed=1, bed_colors=None) -> Village: ...   # bed_colors e.g. {"house_a_bed_2": "red"}: default = vanilla (white)
class Village:
    world: World
    collection: bpy.types.Collection
    anchors: dict[str, tuple[float, float, float]]      # named standing spots / look targets (Blender coords)
    paths: dict[str, list[tuple[float, float, float]]]  # named walkable polylines on the ground
    doors: dict[str, bpy.types.Object]
    bell: bpy.types.Object
    lantern_lights: list[bpy.types.Object]              # every torch/lantern Light object, so a film can scale energy
    def door_open(self, name, frame, open=True, frames=5): ...
    def ring_bell(self, frame, strength=1.0, swings=5): ...
```

Required set pieces (one continuous plains village, roughly 64 x 64 blocks, on gently uneven grass terrain
with vanilla-shaped oak trees, short grass, poppies and dandelions; every building is a vanilla template):
1. **Square**: a vanilla town centre with the bell (`plains_meeting_point_*`), dirt-path streets radiating from
   it (vanilla street templates or hand-laid `dirt_path`), houses facing it. Anchors `bell`, `bell_ringer`
   (where Steve stands to ring it), `square_n/e/s/w`.
2. **Six to eight vanilla houses** around the square and along the streets. `house_a` is the roomiest one with
   beds (choose by inspecting the templates) and is filmed inside: anchors `house_a_door_out`,
   `house_a_door_in`, `house_a_inside_1..3`, `house_a_bed_1..N`, `house_a_cam` (an interior corner a camera can
   sit in looking at the door; if the vanilla interior is too cramped for a camera, give the Village a
   `cutaway(name)` helper that hides one wall/roof section for interior shots). Paths `square_to_house_a`,
   `square_to_house_b`, `square_to_house_c` (running routes from the square to just inside each door).
3. **Workstations**: a vanilla farm with composter (`farm_work`), a vanilla library with lectern
   (`library_work`), a vanilla smith (tool smith / weaponsmith / armorer) (`smithy_work`). Each anchor is where
   a villager stands facing the station; also `<name>_station`.
4. **Trading hall**: a player-built structure in the classic survival style (stone bricks / oak, six 1x1 cells
   side by side, each with its workstation block in front, iron bars above it and between the cells keeping the
   villager in, hanging lanterns), with an aisle a camera can dolly along. Anchors `cell_1..6`,
   `hall_aisle_start`, `hall_aisle_end`.
5. **Lights**: vanilla `plains_lamp_1` posts and the buildings' own torches; a few player-placed lanterns are fine.
   Two of them are player-built lamps (cobblestone foot, two oak fence posts, a lantern) flanking the bell, two
   blocks to its south-west and south-east: light groups `bell_w` / `bell_e`, anchors `bell_lamp_w` / `bell_lamp_e`.
   The vanilla meeting point has no light on the bell's side; these are the key lights of both bell shots.
6. **Way out**: path `exit_road` from the square past the last house into an open meadow that rises slightly so
   the horizon is clean. Anchors `exit_gate`, `meadow_far`, `nitwit_idle` (a lonely spot at the village edge
   with the houses behind it).

### Role CAST owns `engine/characters.py`

```python
def make_villager(name, profession="farmer", child=False) -> Character: ...
    # real textures layered as in the game: entity/villager/villager.png + type/plains.png + profession/<p>.png
    # professions: every file in textures/entity/villager/profession (farmer, librarian, toolsmith, weaponsmith,
    #              armorer, cleric, shepherd, mason, fletcher, butcher, fisherman, cartographer, leatherworker, nitwit)
    #              plus "none" (unemployed: no profession layer)
def make_player(name="player", skin="steve") -> Character: ...       # entity/player/wide/<skin>.png, both skin layers
class Character:
    root: bpy.types.Object          # Empty at the feet; move/rotate this
    head: bpy.types.Object          # pivots at the neck
    height: float
    def place(self, frame, pos, yaw=0.0): ...                    # hard-set position (CONSTANT key) — use at shot cuts
    def walk(self, frame, points, speed=1.6, run=False) -> int: ...   # move along polyline with leg cycle + bob; returns end frame
    def look_at(self, frame, target, ease=6): ...                # turn head (clamped) toward a world point, a Character
    def face(self, frame, target, ease=8): ...                   # (its eyes) or an Object (evaluated AT that frame); same for face
    def idle(self, frame_start, frame_end, seed=0): ...          # small head turns, weight shifts
    def nod(self, frame); def shake(self, frame); def flinch(self, frame): ...
    def swing_arm(self, frame): ...                              # player: right-arm use swing; villager: small jolt
    def hold(self, obj | None): ...                              # player: item in right hand
    def lie_down(self, frame, bed_pos, yaw): ...                 # sleeping pose on a bed
    def show(self, frame, visible=True): ...                     # keyed render visibility
```
Villager run = the in-game panic run (fast leg swing, arms stay crossed), with a slight forward lean and head
bob for cinematic life. Animation is plain object keyframes on a parented box rig (no armatures needed).

### Role LOOK owns `engine/look.py`, `engine/shots.py`, `engine/captions.py`, `engine/post.py`, `render.py`

```python
# look.py
def setup_render(scene, res=(720, 1280), samples=24, fps=24, motion_blur=True, threads=4): ...
def set_time(scene, preset="golden", sun_azimuth=None) -> dict: ...   # 'day' | 'golden' | 'dusk' | 'night'
    # world sky gradient, real sun/moon textures (textures/environment/celestial) as a square with glow, stars (night),
    # blocky clouds, light haze; returns {'sun':…, 'moon':…}
def setup_compositor(scene, bloom=1.0, vignette=0.35, grade="warm"): ...   # glare/bloom, vignette, gentle grade

# shots.py
class Film:
    def __init__(self, scene, fps=24): ...
    def shot(self, name, start_s, end_s) -> Shot: ...       # consecutive shots, hard cuts
    def finalize(self): ...                                 # binds each shot camera to a timeline marker, sets frame range
class Shot:
    frame_start: int; frame_end: int; camera: bpy.types.Object
    def lens(self, mm, fstop=1.8): ...
    def move(self, pos0, target0, pos1=None, target1=None, ease="smooth"): ...   # camera pos + aim, start -> end
    def focus(self, target, at_s=None): ...                 # object or point; call twice with at_s for a rack focus
    def handheld(self, amount=0.02, seed=0): ...            # subtle drift

# captions.py — the real Minecraft font, read from textures/font/ascii.png (+ font/include/default.json for the layout)
def autotime(script: str, start=0.3, per_word=0.36, comma=0.12, period=0.45, end=None) -> list[tuple[str, float, float]]: ...
#   end=T scales the timing so the last word ends at T seconds (the defaults finish "The Bell" at 8.97 s: pass end=...)
def draw_caption(word: str, size=(1080, 1920)) -> PIL.Image: ...   # RGBA overlay
#   glyphs cut from the bitmap font with their real variable widths and 1-px spacing, scaled by an integer factor with
#   nearest-neighbour; white text with the game's drop shadow (dark grey, offset one font pixel down-right), plus a thin
#   dark outline for legibility; centred, baseline 69% down the frame (measured on the reference in VIDEO coordinates:
#   the phone screenshots crop the video), 17 px per font pixel at 1080 wide: a 6-letter word spans about 50% of the
#   width. captions.CAPTION_BAND = (0.62, 0.72) is the strip of the frame a caption covers. No word spans more than
#   68 % of the width (x 16-84 %, clear of the Reels icon column): 'Everyone' is drawn at 15 px per font pixel.

# render.py (CLI, run as `$BPY -m render <film> ...`); a film module is films/<film>.py exposing
#   build(scene) -> {"film": Film, "captions": [(word, t0, t1), ...]}
#   --still S            render the frame at second S to out/test/<film>_<S>.png (fast: --res/--samples overridable);
#                        --zones also writes <name>_zones.png (Reels UI zones, caption band, safe area)
#   --frames A-B --step K   render frames, resumable ('all', a single frame or a shot name work too). FINAL settings
#                        (720x1280, 24 samples, step 1, motion blur) write out/frames/<film>/f_####.png; any other
#                        --res/--samples/--step, or --no-motion-blur, is a PREVIEW and writes
#                        out/preview/<film>/<W>x<H>_<N>spp[_stepK][_nomb]/. Every frame is stamped in meta.json with
#                        the settings, a hash of the ENGINE sources and the frame's SCENE FINGERPRINT (engine/stamp.py:
#                        a hash of everything Cycles is given for that frame); a frame is skipped while all three are
#                        current. So a caption / timing / comment edit in a film script re-renders nothing, an edit to
#                        one shot re-renders that shot only, a change of sky or set re-renders everything.
#   --rerender-stale     An edit to an ENGINE file while frames exist STOPS --frames with exit code 3 and the list of
#   --restamp A-B|all|SHOT   changed files (a chunked final render must not quietly restart at frame 1). Then either
#   --restamp-changed    --restamp all (keep the frames whose fingerprint is unchanged: the edit altered no picture) or
#                        --frames ... --rerender-stale. --restamp-changed also keeps frames whose fingerprint differs.
#   --prune-stale        delete the PNGs of the frame directory that are not valid frames of the film any more
#   --sheet N            contact sheet of N evenly spaced low-res frames WITH captions -> out/test/<film>_sheet.png
#   --encode             upscale to 1080x1920 (Lanczos), composite captions after the upscale, H.264 yuv420p crf 16
#                        +faststart -> out/<film>.mp4 (previews: out/preview/<film>_<variant>.mp4). Exits 2 while
#                        frames are missing or stale; --allow-holds holds the previous frame instead (step previews).
#   --save-blend         write out/blend/<film>.blend with textures packed and the FINAL render settings (no .blend1)
```

## Integration notes (after look-dev and the fix pass on the real set; read before writing a film)

`films/lookdev.py` is the worked example: four small films (`lookdev_dusk`, `lookdev_golden`, `lookdev_bed`,
`lookdev_night`) built from the real village, cast and look. Copy its `Stage` helper into a film:
`Stage.shot(name, seconds)`, `actor(name, profession)`, `use(shot, *characters)` (everyone else is hidden for that
shot), `hero(shot, label, *things)` (what the shot is about: checked against the safe area), `lights(shot, scale,
groups, near, radius, extra)` (torch levels step at the cut; `extra` boosts one torch as a key light),
`see_through(shot, cutaway)` (wall invisible to the camera only), `remove(shot, cutaway)`, `finish()`.
`lights(..., inside="house_a")` names the room a shot is filmed in: only there is that room's fill light on.
`$BPY -m films.lookdev --captioned` re-renders the eleven reference stills `out/test/lookdev_<name>.png` and checks each
one (exit code 1 if a check fails); `$BPY -m tools.contract_check --cli` checks every name in this file and every
render.py flag; `$BPY -m tools.noise_check <film> <frame> ...` measures what would boil at final quality.

### The look (engine/look.py), and why

- **Colour pipeline: view transform 'Standard' + a highlight shoulder as the last compositor node.** The first
  choice, Khronos PBR Neutral, subtracts min(r, g, b) - 6.25 min^2 from every channel: under dim light the smallest
  channel of every colour goes to zero, which turned robes wine-red, planks orange and Steve's trousers from
  (67, 58, 143) to (48, 2, 144). Now a pixel below the shoulder (0.76) is texture x light and nothing else.
  Above it the drift to white is slow (`SHOULDER_DESATURATION` 0.06, Khronos has 0.15) and glowing texels are only
  2-4.5 x their texture (`blocks.EMISSIVE`: lantern 3, torch 4.5): a lantern's glow stays the game's orange-yellow
  with a pale core, where emission 7 through the faster drift rendered salmon pink. The third value of an EMISSIVE
  entry lights the rest of that block a little (the chain, the iron, the stick): its own point light sits inside
  the model and reaches none of its faces, while the game draws the block at light level 15.
- **Pale light, near-neutral fill.** Key colours are pale (golden `#ffe9cc`, dusk `#ffcda6`), the sky FILL is
  desaturated to 6-10 % and a touch cool (never violet: a violet fill is what makes browns magenta); the visible sky
  keeps its colour because camera rays see another map. Grades have no lift at all and saturation <= 1.
  `props.TORCH_COLOR` is (1.0, 0.88, 0.72); the orange of a torch comes from its glowing flame texels and their bloom.
- **Sky:** golden hour keeps the game's blue above ~15 degrees (peach only at the horizon), dusk is indigo at the
  zenith with orange and pink in the lowest 20 degrees. The golden-hour halo around the sun is MIXED in (preset key
  `halo`): blue -> neutral -> cream, hue 35-45 beside the sun; warm light ADDED to that blue came out lilac. Haze is mixed over geometry only (world AOV `sky` = sky
  coverage; the sky has its own horizon haze baked in). Stars are hard squares of varying brightness, kept under the
  bloom threshold. Cameras have a 4-blade aperture: defocused sun and torches stay square.
- Fast GI (direct light + one bounce + sky-tinted occlusion, reach 8 blocks), adaptive threshold 0.1, four
  shadowless "ground bounce" lamps per preset. Rooms that are filmed inside (house_a, hall, library) carry one weak
  cool shadowless fill light in their own light group (`Stage.lights` switches it on only for `inside=` that room). Torch / lantern lights use a smoothed falloff (`W / (d^2 + 1)`):
  the block a torch is mounted on is lit like a surface one block away and keeps its texture.
- **Every still is measured against the textures it was made from** (`tools/palette_check.py`, run by
  `films.lookdev`): lit stone G >= 0.92 R, robe hue 0-30 degrees, lit oak planks saturation <= 0.68, villager skin
  <= 0.52, Steve's trousers not crushed, his shirt still teal (its red channel is 0-2 in steve.png itself), plants
  as bright as the ground they stand on. If a look change breaks one of these, the look change is wrong.
  The interior passes two of them AT the limit (stone G/R 0.92, skin saturation 0.52): stone under nothing but
  torch light is 0.88, the room's fill brings it up. Raise house_a's torches above 1.5 only together with its fill
  (both are in the group `house_a`; never boost one torch alone with `extra` in there) and re-run the check.

### Composition rule (Reels)

On tall phones the 9:16 video is height-filled: about 5 % is cropped off each side, the icon column covers x 84-93 %
for y 45-95 %, name and description cover everything below y 87 %, the top icons everything above 13 %, and the
caption sits in y 62-72 % (`engine/post.py`: `UI_ZONES`, `CAPTION_ZONE`, `SAFE_AREA`; `--zones` draws them).
**Faces and hero props go inside x 8-82 %, y 14-60 %; nothing essential in y 62-72 % or below 86 %.** Big foreground
elements (the empty bed, a counter, a composter) may fill the bottom third: the caption then sits on them, as it
does on the bed in reference 3.

### Rules that each cost a wrong render

- One sky per BUILD: a film with several skies declares them in SKIES and tags its shots (see "Several skies in one
  film" below; this replaced "one sky per film"). Choose the sun for the shots: the village is dense, so a sun lower than
  about 20 degrees leaves almost everything at ground level in a building's shadow. The golden look-dev film uses
  azimuth 62, elevation 27; at dusk (elevation 5) faces need a torch as key (`Stage.lights(..., extra=...)`).
- At dusk a subject is as bright as its practical makes it. Bell close-up: west lamp x 2.4 as the key, east lamp
  off, everything behind the bell at 0.9, camera 20 degrees east of the bell's broad face and below its base: lit
  face 0.95 x texture, shade side 0.4, the dusk sky over the well's rim. Steve at the bell: seen from the south-east
  (the side of the arm that swings), east lamp x 2.6 as the key. Light a background at 1.6 and the subject is lost.
- A character that is in two consecutive shots must not be keyed before the second shot starts (no pre-roll): the
  `place()` cuts the first shot's walk short. `place()` everybody before any `look_at()` at them.
- Plain villagers from behind are a brown box under a pink box: stage for noses, brows, hats and crossed arms.
  A villager walking away can still give his profile: `look_at` a point 80 degrees or more to his side (the head
  stops at 70) and HOLD it to the last frame of the shot: at 55 degrees, seen from behind, the face is edge-on.
- A villager who looks DOWN at something held low hides his face under his hat from a camera above eye height.
- Flat items (emerald) lie along the hand as in the game: edge-on from the side, readable from behind or above.
  `raise_arm(angle=55)` puts it at the other's chest, clear of his face.
- A bed reads as a bed lengthwise from behind its pillow or from beside its foot; the vanilla white bed is white on
  white, so the look-dev films dye the one hero bed red (`bed_colors={"house_a_bed_2": "red"}`), as the client's
  references do. Everything else in the houses is the unmodified template.
- Trading hall: faces are half a block wide and two blocks apart, so from across the aisle three of them are never
  more than a fifth of the frame wide each. Ride along the counter instead: a quarter block off the cell fronts at
  eye height, 3 blocks short of the nearest face, looking 25 degrees off the row (38 mm f/3.4). The nearest face is
  28-30 % of the frame, clear in its window, the row lines up behind it, the bars stand above and between the
  faces (never across them: the pier fronts are open at face height), a lantern hangs in the upper left.
- Meadow: flat for 30 blocks beyond `exit_gate`, then 1-block rises about 11 blocks apart with wandering, overgrown
  edges, and five lone oaks. A camera on the exit road looking anywhere between north-west and north-east sees a
  clean horizon. The two verge columns west of the road (`village.CAMERA_LANE`, x -3..-2, y 22..58) carry no
  plants: a camera tracking somebody up the road rides there; a tuft one block from the lens hides him.
- Lenses that worked: bell 105 mm f/1.4, walking villager 42 mm f/2.8 from 3.7 blocks, portrait 66 mm f/2.6,
  over-the-shoulder trade 50 mm f/3.4, running group 24 mm f/2.8 from ground level, interior over the bed 26 mm
  f/2.6, hall 38 mm f/3.4, walking away into the sun 28 mm f/3.2 from 0.8 above the ground, bed 35 mm f/2.2,
  Steve at the bell 32 mm f/3.2 from 8 blocks.
- Rendering: 10-17 s per 720x1280 frame at 24 samples on 4 idle cores (worst: the hall, with defocused iron bars in
  front of the lens, and wide dusk shots with many torches). Render finals in chunks under the 300 s limit:
  `--frames all --max-seconds 240`, repeated until nothing is left; never mix previews into them (render.py keeps
  them apart). FREEZE the engine files while finals render: an engine edit stops the next chunk with exit code 3
  (see render.py); film-script edits are safe at any time and re-render only the frames they change.

### After four finished films (The Bell, The Nitwit, One Word, Poppy)

What a frame-by-frame check of the finished videos still found, although every film had passed two reviews on
previews and stills. Look for these BEFORE the final render:

- A face tucked against a neighbour: the child in the Bell's house shot stood between two adults and was a third
  hidden by an arm and a trouser leg. Ray-cast or look at every face in a group at phone size (360x640).
- Tangents: a wall torch's flame exactly on a hat, a hanging lantern on Steve's hair, and a slot of open sky between
  two far oak canopies that slid out beside a head as the camera moved, just where the focus pull sent the eye.
- One shot a stop darker than its neighbours (the smith under his porch roof). A view-exposure key cannot fix that:
  view settings are in the frame stamp's GLOBAL part, so every frame goes stale. Add a film-local, shadowless
  light keyed visible for that shot only (`SMITH_BOUNCE` in films/nitwit.py); hidden objects are not in a stamp.
- A child in strict profile that looks at something beyond itself shows the lens a blank cheek. Cheat its look
  targets about 21 degrees to the camera's side (`_to_lens` in films/poppy_day.py).
- A step of less than 7 frames is a hop that stops dead (`Character.walk` is linear, there is no ease: use a low
  speed). Two runners 0.2 block apart are one two-headed shape: stagger them by 0.7 block.
- Daylight with the sun behind the camera is flat, with no cast shadows in the picture. Stage each daylight camera
  so the sun is 60-120 degrees off the lens axis, or let a shadow edge cross the wall behind the subject.
- (History) Poppy, made before several skies per film existed, is two modules (films/poppy_night.py,
  films/poppy_day.py) encoded separately and joined with `ffmpeg -f concat`. New films use one module with SKIES.

Known engine issues, not fixed because engine files were frozen during the finals; the films work around them:

- `stamp.Fingerprinter` caches a mesh's digest together with its materials' digests. A mesh with an ANIMATED
  material (fx crack stages, the enchant glint) then gets a fingerprint that depends on which frame the process
  fingerprinted first, and good frames are declared stale. Work-around: `stamp_every_frame()` in films/oneword.py.
- `Character._cut` re-keying the same frame leaves a stale key; `Character.swing_arm` is additive;
  `Character.hold()` items become visible again at each shot start.
- `Stage.actor()` builds villagers and Steve only: the golem and dropped items go through `add_golem` / `add_item`
  in films/poppy_common.py. `Stage.hero` with an fx job villager needs `*villager.heads`.
- fx `Block` tints the break particles of grass blocks. The hall cell anchor puts the villager 0.22 too far forward
  for the book shot. Lit stone in the hall cell sits on the 0.92 G/R palette limit (0.914-0.926).
- The smithy has no fill light group; raising its torches alone turns the cobblestone orange.
- `tools.palette_check` has no command line (use its probe / evaluate). `render.py --still ... --sheet N` in one
  call renders the sheet at the still's resolution: run `--sheet` on its own.

## The one-minute narrated films (from November 25)

The client asked for one-minute films "with a real story" and a narrator. Scripts: SCRIPTS.md; shot lists:
SHOTLISTS.md; per story `stories/<slug>.json` (narration, beats with the picture for each sentence, locations, risks,
fallbacks). Every module below was built from the game's own classes and files, checked by an independent reviewer and
fixed; its module docstring is the reference, and its self-test is `$BPY -m engine.<module>` (narration: `$TTS
tools/narrate.py --selftest`).

| Module | What it gives a film |
| --- | --- |
| `engine/narration.py`, `tools/narrate.py`, `tools/narration_sync.py` | NARRATION literal in the film, spoken by Kokoro into `narration/<film>.wav` + `.json` (commit both); word frames, cuts from sentences, captions from the voice; `--encode` muxes the voice automatically. Template: `films/_narrated_demo.py`. |
| `engine/players.py` | The real player model, ten skins (Steve ... Zuri, and "herobrine" with glowing white eyes), armor of every material with glint, held items, walk / sprint / sprint-jump / sneak / attack / mine / hurt / die / watch. `players.add_player(st, name, skin)`. Use it instead of `st.actor(name, "steve")`. |
| `engine/undead.py` | Zombie, husk, zombie villager (all professions, babies), aggro arms, attack, infect, cure with splash potion and golden apple; `undead.hurt / die` (flash, knock-back only with an attacker) for ANY character. |
| `engine/piglins.py` | Piglin, brute, baby; admire, barter with lobbed results, axe swing, dance, fall, hurt, death poof. |
| `engine/animals.py` | Cow, calf, chicken, chick; wander in pens, follow, eat, milk, lay eggs, hurt, death; `pen_set` through the village hook. |
| `engine/sets.py` + `village.build_village(..., edit=hook)` | Film-specific blocks go INTO the village world before it is meshed and lit (torches become lights, paths and anchors follow). `hello_set`: dark oak forest wall, floating oak, bare oaks, sand pyramid, with anchors, paths and cameras. Docstring says how to add a set piece. |
| `engine/redstone.py` | Lever, piston and sticky piston (push limit 12, piston doors, rows of pistons carrying planks), redstone dust with power levels, repeater, lamp (a real light), redstone torch (placed and held), `signal / unsignal` sequencing with the game's delays. Parts go into empty cells left by the village hook; `redstone.kit(v)` after the build. |
| `engine/fixtures.py` | Chest (single and double, opening lid), hopper absorbing dropped items, still and flowing water, lava (surface, glow-only strip, real orange light, flicker), glass boxes with per-wall cutaways, falling blocks and anvils (the game's gravity, landing as blocks, chipping), extra beds that appear on a frame. |
| `engine/breaking.py` | The game's destroy-stage cracks on doors and single blocks, breakable / placeable blocks, mining with the game's timing (compressible), the zombie banging on a door (cracks climb and reset, optional shudder), `door_torches`. |
| `engine/hostiles.py` | Creeper (walk, one slow step, fuse with swell and white flashes, aborted fuse, explode with push on victims), skeleton with bow (aim, draw through the pulling stages, shoot; a drawn bow always has its arms up), arrows with the game's flight (moving targets are led; misses stick in the ground) that stay stuck in the body part they hit. Use `knockback=0.1` or `max_back` near other characters (no collision between characters). |
| `engine/illagers.py` | Pillagers with crossbows (charge, shoot), patrol `march` in file, the captain with the ominous banner on his head, the banner and the ominous bottle as dropped items, `crushed_by` falling anvils (engine/fixtures) with hurt, tip-over and poof. A captain with the banner needs an anvil from 17 blocks or more. |
| `engine/underground.py` | The game's BLOCK light baked into the blocks (torches, lanterns; sky light 0 underground), the trading hall of "Two Apples" under the square: stair mouth by the well, stairwell, cells with piers, bars and job blocks (2 high under stone caps), dad's end cell with the piston wall and lever, the zombie box with its floor-level slot; cutaways, anchors and a camera per beat; push, bed bounce (the game's JumpOnBed), jump loop, hurt / infect in a capped cell, lit doorway after the wall opens. |
| `engine/towers.py` | The iron farm of "Twenty Minutes" beside the well: pillar, glass pod with beds, zombie cell, water platform with the glowing slot, hopper and chest at the foot, dirt staircase with a breakable top step; golem spawn, slide, drop and death with its drops into the hopper; panic tremble that keeps the look, baby hop and swap; anchors and a camera per beat. |
| `engine/music.py` | The bandstand of "The Crammys" and the lane doorsteps; note blocks with the game's note particle colours per pitch and the instrument from the block below; jukebox with notes while it plays, disc insert and eject; discs (11, cat), goat horn, totem (spinning on the pedestal), held block items; `clap` (fast sneak); anchors and a camera per beat. |
| `engine/nether.py` | `set_nether` (no sky: fog colour, haze, bloom, grade) and `nether.Stage` (preset "nether" for SKIES), bastion sets from the game's own bastion structure templates (needs the client jar: `$BPY -m tools.nether_fetch_jar`), the home courtyard with gateway, guard stair, gold wall and a pit in two states, the bridge over a lava glow, the treasure corner; anchors and cameras per beat of "Six Seconds". |

**Final quality is set by each new film, in build()** (study: `tools/render_economics.py findings`, independently
checked): `scene.render.resolution_x, scene.render.resolution_y = 540, 960` and `scene.cycles.samples = 16`, upscaled
to 1080x1920 by the encoder. In blind pairs nobody could tell it from 720x1280 at 24 at phone size; it halves the render
time (about 3 h for 1,440 frames on four idle cores). Do NOT change `render.FINAL_RES / FINAL_SAMPLES` (that would make
every frame of the finished films stale), never pass `--res / --samples` for finals (that selects a preview directory),
and leave the noise seed alone (an animated seed boils dark defocused areas).

**Long films.** A film over 20 s is encoded in resumable 10 s parts: `--encode` returns exit 4 until it is done; run it
again. Render finals in chunks with `--frames all --max-seconds N` and resume on exit 3 with `--restamp all` when an
engine edit changed no picture.

### Several skies in one film, and dips to black (render.py, films/lookdev.py Stage, engine/post.py)

This REPLACES the rule "One sky per film (`look.set_time` once)" (Rules that each cost a wrong render, first bullet: keep its advice about sun elevation) and the bullet "A film with two skies is two modules (films/poppy_night.py, films/poppy_day.py) ..." (After four finished films). A film that alternates between skies is ONE module, one frame directory, one narration and one mp4. Template: `films/_multisky_demo.py`.

```python
SKIES = {"gold":  dict(preset="golden", az=62.0, el=27.0, bloom=1.0, grade="warm"),      # module level, the name SKIES
         "night": dict(preset="night", az=176.0, el=21.0, bloom=1.3, grade="cool")}      # az: degrees ccw from east
def build(scene, sky=None):                                  # render.py calls it once per sky that has work
    st = Stage(scene, film, v, skies=SKIES, sky=sky)         # builds the ACTIVE sky (None: the first) and its compositor
    s = st.shot("door_night", seconds, sky="night")          # every shot names its sky (default: the one in force before it)
    torches = dict(near=bed, radius=16.0, inside="house_a")
    st.lights(s, scale=1.7, **torches)
    st.sky_change(frame, "gold")                             # a sky change INSIDE a shot: same camera path, actors mid-motion
    st.lights(s, scale=1.0, at=frame, **torches)             # torch levels that step with it (repeat every argument)
    st.dip(frame, out=3, hold=0, back=3)                     # encoder: black ON `frame`, 3 frames out, 3 back; st.fade(f0, f1, g0, g1)
    return {"film": film, "captions": caps, "narration": nar, "stage": st}
```

- **One sky per build.** The timeline, every actor, key, torch level, caption and render setting must be the same in every build. Nothing but `Stage(..., sky=sky)` may depend on `sky`; render.py raises SkyError when two builds of unchanged sources disagree. Never key `st.sky[...]` per shot. Write SKIES as an assignment or a named import (a star import is followed). `SKIES = {}` is a one-sky film.
- **One process per sky.** render.py runs each sky in a fresh Blender process of its own (internal `--sky NAME`), and only the skies that have work. A Session owns only the frames tagged with its sky: `Session.fingerprint / render_frame` and `Stamps.status / fp / mark` raise SkyError for any other frame, and every stamp records its sky.
- **Names are labels, fingerprints the proof.** Renaming a SKIES key re-renders nothing. A PNG rendered under another sky than its shot now has is stale ("rendered under another sky ...") and is never kept by --restamp-changed.
- **Tools.** `render.Session(name)` builds the FIRST sky. `render.session_for(name, frame)` builds the sky of that frame, and `render.sky_table(name)` gives the table without a build. tools/noise_check.py reaches only the first sky until it uses session_for.
- **Flags.** All flags work unchanged; `--save-blend` writes `out/blend/<film>.<sky>.blend`.
- **What it prints.** Per sky: `[render] sky 'night': N frames requested, D already done, T to render ...` (or `none to render`). The LAST line is the film's: `[render] frames: N requested, D already done, [K rendered in this run, ]0 to render at ... (2 skies: ...)` or `... L left ... re-run the same command to resume`. The words ` 0 to render` appear only there, and only when every sky's frames are valid as judged in their own sky's build.
- **Edits and exit codes.** After an edit, the first sky's process learns the film's real table (a new shot, a longer film, a renamed sky and a new frame directory all work). Editing the film while a chunk renders is safe: the command keeps its frames, prints "a source file of the film changed while this command ran" and exits 0. Exit codes keep their meanings; exit 3 is decided over every sky's frames before any sky renders.
- **Costs** (village, 1,440-frame two-sky film):
  - 0.6 s plus a 1.5-2.7 s build per sky that has work;
  - 3 s outside the frames per chunk, 5 s in the chunk where the sky switches;
  - about 35 ms of bookkeeping per rendered frame;
  - no build when nothing is left (0.5 s);
  - after any source edit, both skies are built and all 1,440 frames judged in about 32 s.
  - An edit to one shot re-renders that shot; an edit to one SKIES value re-renders that sky's frames; captions, dips and sky names re-render nothing.
- **Fades.** A film may return `"fades": [(t0, t1, g0, g1), ...]`: picture-gain ramps in film seconds, active for t0 <= t < t1, gain 1 outside, overlapping ramps multiply. `post.encode / encode_parts / contact_sheet / finish_frame` apply them to the picture after the upscale and BEFORE the caption (the caption stays at full strength). They live in meta.json, never in a frame stamp: changing one re-encodes and never re-renders. A film without fades has the meta.json and mp4 it always had.
- **Checks:**
  - `$BPY -m tools.multisky_selftest [chunks|engine|stale|lock|encode|edits|detect|midrun]` (60 checks; run the parts separately);
  - `$BPY -m tools.multisky_check change | verify | inprocess | cuts MP4`;
  - `$BPY -m tools.multisky_judge <film> [--sky S] [--save|--compare F]`.
- **Known effect.** A frame's pixels depend slightly on which shots its process rendered before (Cycles persistent data with per-shot torch sets: mean 0.06-0.11 of 255). A chunk boundary inside a torch-lit shot changes the noise pattern there. This is true for every film.
