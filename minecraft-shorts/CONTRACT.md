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
# mcassets.py — the only place that reads assets/mc
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

# props.py — separately animatable things, built from the same real models/textures
make_bell(attachment="floor", facing="north") -> Object     # pivot at the hinge; rotate about local X to swing (bell body uses entity/bell/bell_body.png)
make_door(block_id="oak_door", hinge="left") -> Object      # hinge pivot; rotate about Z to open; both halves
make_item(item_id) -> Object                                # same as mcassets.item_object
make_light(kind="torch"|"lantern") -> Object                # warm point light sized for that block

# village.py
def build_village(scene, seed=1) -> Village: ...
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
   side by side, each with its workstation block in front, trapdoors/slabs keeping the villager in, lanterns),
   with an aisle a camera can dolly along. Anchors `cell_1..6`, `hall_aisle_start`, `hall_aisle_end`.
5. **Lights**: vanilla `plains_lamp_1` posts and the buildings' own torches; a few player-placed lanterns are fine.
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
    def look_at(self, frame, target, ease=6): ...                # turn head (clamped) toward a world point
    def face(self, frame, target, ease=8): ...                   # turn whole body toward a world point
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
def autotime(script: str, start=0.3, per_word=0.36, comma=0.12, period=0.45) -> list[tuple[str, float, float]]: ...
def draw_caption(word: str, size=(1080, 1920)) -> PIL.Image: ...   # RGBA overlay
#   glyphs cut from the bitmap font with their real variable widths and 1-px spacing, scaled by an integer factor with
#   nearest-neighbour; white text with the game's drop shadow (dark grey, offset one font pixel down-right), plus a thin
#   dark outline for legibility; centred, baseline about 61% down the frame; a 6-letter word spans about 45% of the width.

# render.py (CLI, run as `$BPY -m render <film> ...`); a film module is films/<film>.py exposing
#   build(scene) -> {"film": Film, "captions": [(word, t0, t1), ...]}
#   --still S            render the frame at second S to out/test/<film>_<S>.png (fast: --res/--samples overridable)
#   --frames A-B --step K   render frames to out/frames/<film>/f_####.png, skipping files that already exist (resumable)
#   --sheet N            contact sheet of N evenly spaced low-res frames WITH captions -> out/test/<film>_sheet.png
#   --encode             upscale to 1080x1920, composite captions, H.264 yuv420p crf 16 +faststart -> out/<film>.mp4
#   --save-blend         write out/blend/<film>.blend with textures packed
```
