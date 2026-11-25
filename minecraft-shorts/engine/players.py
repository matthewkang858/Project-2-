"""PLAYERS: every default skin (both skin layers), ARMOR, held items, the player's own animations, and HEROBRINE.

New module; edits no other file. Geometry and numbers are transcribed from the Java Edition 26.x client classes
(named next to each number); textures and item / block models are the game's own, read through engine.mcassets.
Blender axes as everywhere: +X east, +Y north, +Z up, 1 block = 1 unit, characters face -Y at yaw 0, 24 fps (the
game runs 20 ticks per second: 1 tick = 1.2 frames).

PUBLIC API
    make_player(name, skin="steve", slim=None, glow=None, collection=None) -> Player
        skin: steve alex ari efe kai makena noor sunny zuri (textures/entity/player/wide|slim/<skin>.png), or
        "herobrine" (Steve with blank white eyes, built in memory). slim=True = the 3-pixel-arm model with the
        slim texture (every skin ships both; default: alex slim, the others wide). Both skin layers, box for box
        (HumanoidModel.createMesh + PlayerModel.createMesh): hat +0.5, jacket / sleeves / trouser legs +0.25.
        glow = emission of Herobrine's eyes (default HEROBRINE_GLOW 3.0; 0 = plain white texels).
        1.875 tall as drawn (32 px at the renderer's 0.9375), hit box 0.6 x 1.8, eyes 1.61.
    add_player(st, name, skin="steve", **kw) -> Player     build once and register with a films.lookdev.Stage
                                                           (st.cast[name]); then st.use(shot, p), st.hero(shot, "x", p)
    cast_town(st, count=6, seed=0, skins=None, items=True, names=None) -> [Player]
        `count` different players for "a village of players": one skin each (all nine before any repeats), an
        everyday item in some hands, each with its own idle seed in p.idle_seed (call p.idle(f0, f1) per shot).
    equip(player, material=None, helmet=..., chestplate=..., leggings=..., boots=..., enchanted=False, frame=None,
          glint_strength=1.5) -> [Object]
        Armor as HumanoidArmorLayer draws it. equip(p, "diamond") = the full set; equip(p, boots="golden") = one
        piece; a keyword set to None takes that piece off. materials: leather chainmail iron golden diamond
        netherite (also copper; turtle_scute as helmet). enchanted=True adds the armor glint (see GLINT below).
        frame=None: worn for the whole film; frame=f: from that frame on (CONSTANT keys). Also Player.equip(...).
    SKINS, ARMOR_MATERIALS, WALK_SPEED 4.317, SPRINT_SPEED 5.612, SNEAK_SPEED 1.295, SPRINT_JUMP_SPEED (7.13,
    simulated), JUMP_HEIGHT 1.252, JUMP_TICKS 12, HEROBRINE_GLOW, HURT_TICKS 10, DEATH_TICKS 20.

Player (a subclass of engine.characters.Character: root / hips / body / head / arm_l / arm_r / leg_l / leg_r, plus
        .torso, the body box; `body` itself is an empty carrier so that a crouch tilts the torso only)
    place(frame, pos, yaw=0.0)             hard cut to a spot: neutral standing pose, upright, not crouching
    show(frame, visible=True)              keyed visibility of rig, armor and held items (Stage.finish calls it)
    hold(item, hand="right", frame=None, enchanted=False, potion_color=None) -> Object | None
        item = an item id ("diamond_sword", "iron_pickaxe", "netherite_axe", "stone_shovel", "golden_hoe", "bow",
        "shield", "torch", "redstone_torch", "bucket", "milk_bucket", "cooked_chicken", "steak", "golden_apple",
        "splash_potion", "ender_pearl", "gold_ingot", "emerald", "music_disc_13", "goat_horn", "totem",
        and block items held as blocks: "note_block", "tnt", "redstone_lamp", "anvil", "dirt" ...), an Object made
        by props.make_item, or None (empty hand). Placed by ItemInHandLayer + the model's own
        display.thirdperson_righthand / _lefthand transform; the hand's arm is carried 18 degrees forward (ArmPose
        ITEM). frame=None: for the whole film; frame=f: from that frame on. Returns the item object (focus target).
    item(hand="right") / item_point(hand, frame)      the object in a hand / its world centre at a frame
    walk(frame, points, speed=None, run=False, from_current=False, sprint=None, ramp=True) -> end frame
        The game's gait along a polyline (legs cos(0.6662 p) * 1.4 * s, arms * 1.0, no body bob): speed None =
        WALK_SPEED (SPRINT_SPEED with run / sprint=True, SNEAK_SPEED while sneaking). ramp=True = the game's
        acceleration and slide to a halt (ground friction 0.546 per tick); ramp=(False, True) starts in full
        stride (walking into frame), (True, False) leaves at full speed. Slow walks are fine: speed=1.6.
    sprint_jump(frame, points, from_current=False) -> end frame
        Bunny-hopping along the polyline: 12-tick hops 1.252 high (jump velocity 0.42, gravity 0.08, drag 0.98),
        4.28 blocks each at SPRINT_JUMP_SPEED; a whole number of hops, so the speed is adjusted by a few percent.
    jump(frame) -> landing frame           one jump on the spot (14.4 frames)
    sneak(frame, on=True)                  the crouch pose from `frame` on (a snap, as in the game); walk() then
                                           defaults to SNEAK_SPEED (the game's feet slide while sneaking: so here)
    attack(frame) / swing(frame)           one arm swing (6 ticks; engine.fx.arm_swings: absolute keys)
    mine(frame_start, frame_end)           the mining swing held for a span (restarts every 4 ticks; fx.mining_swings)
    eat(frame_start, frame_end=None, hand="right") / drink(...) -> end frame
        Item to the mouth with the 4-tick bob, 32 ticks (38 frames) by default. NOT in the game's third person
        (ArmPose has no eating pose: other players just hold the food): a film gesture built from the first-person
        timing of FirstPersonHandsAndItemsRenderer.applyEatTransform. The bob starts after 20 % of the time.
    block(frame_start, frame_end, hand="left")        shield raised (ArmPose BLOCK + models/item/shield_blocking)
    draw_bow(frame_start, frame_end, hand="right") -> dict(frame, origin, direction)
        ArmPose BOW_AND_ARROW, bow_pulling_0 / _1 (13 ticks) / _2 (18 ticks); released ON frame_end: the dict is
        where and which way the arrow leaves (eye height - 0.1, along the look).
    throw(frame, hand="right", kind="ender_pearl") -> dict(frame, origin, direction, speed, hand)
        The arm swing of a throw; the projectile is another module's: it leaves ON `frame` from `origin` (eye
        height - 0.1, where the game spawns it) along `direction` at `speed` blocks per tick (pearl 1.5; splash
        potion 0.5, pitched 20 degrees up); dict["hand"] = where the hand is at that frame.
    toot(frame_start, frame_end, hand="right")        goat horn held to the mouth (ArmPose TOOT_HORN + the
                                                      tooting_goat_horn model); a horn call lasts 7 s (168 frames)
    sleep(frame, bed_pos, yaw)             = Character.lie_down (flat on the back on a bed, as the game draws it)
    hurt(frame, from_point=None, knockback=0.4) -> end frame
        Red flash for 10 ticks (12 frames; the entity overlay: 30 % red over the SKIN, not over armor or items)
        and, with from_point, the game's knock-back away from it (0.4 blocks per tick, a hop 0.96 high, lands
        1.9 blocks back after 10 ticks). from_point=None: flash only.
    die(frame, poof=True) -> dict(frame, point)
        Red, tips over onto his left side to 90 degrees (sqrt curve, flat after 13.5 ticks), gone after 20 ticks
        (24 frames): dict = the frame he vanishes on and the middle of the body, for the 20 white 'poof' particles
        (engine.fx has no 'poof' kind: see NOT DONE). A later place() stands him up in his own colours again
        (it calls revive(frame)); show(frame, True) brings him back.
    idle(frame_start, frame_end, seed=None) Character.idle (head glances, weight shifts, the slow arm sway);
                                           seed None = the player's own idle_seed. A no-op while .still is True.
    still                                  True = no idle sway and no arm swing while walking, arms dead straight
                                           (make_player("herobrine") sets it). stand_still(frame) cuts to that pose.
    watch(frame_start, frame_end, target, step=2, body=False)
        The head stays on a (moving) target for the whole span, re-aimed every `step` frames, eased; body=True
        also turns the whole figure on the spot when the target leaves the head's 70 degrees. Herobrine's stare.
    crouching_at(frame), holding_at(hand, frame), armor_at(slot, frame), eye_point(frame) (crouch-aware),
    look_vector(frame) (unit vector along the head's look), revive(frame) (end the red overlay)
    look_at / track / face / turn / nod / shake / flinch / raise_arm / lie_down / pos_at / yaw_at: inherited.

USING THEM IN A FILM (st = films.lookdev.Stage)
    hb = players.add_player(st, "herobrine", "herobrine")          # still, eyes glowing
    hb.place(f0, spot, yaw); hb.watch(f0, s.frame_end, kid)         # he only turns his head
    hero = players.add_player(st, "player", "steve"); players.equip(hero, "diamond"); hero.hold("diamond_sword")
    town = players.cast_town(st, 7, seed=3)                         # 7 different players, some carrying things
    for p in town: p.place(f0, ...); p.idle(f0, s.frame_end + 1)
    st.use(s, hb, hero, *town); st.hero(s, "herobrine", hb)
    Key each player in frame order, like every Character. place() first in every shot, then hold / sneak / pose,
    then walk; a posed arm (block, bow, horn, eat, raise_arm) keeps its pose through a walk that starts later.

WHAT THE GAME DOES (read from the classes)
  model      HumanoidModel.createMesh: head 8x8x8 at (0,0), hat (32,0) +0.5, body 8x12x4 (16,16), right arm
             4x12x4 (40,16) pivot (-5,2,0), right leg (0,16) pivot (-1.9,12,0); PlayerModel.createMesh: left arm
             (32,48), left leg (16,48), jacket (16,32), sleeves (40,32)/(48,48), pants (0,32)/(0,48), all +0.25;
             slim: arms 3 wide, same pivots. AvatarRenderer.scale 0.9375. (Here: sleeves +0.27 and pants +0.23,
             so that no two overlay faces are coplanar: Cycles has no draw order to settle a depth tie.)
  armor      HumanoidModel.createArmorMeshSet(inner 0.5, outer 1.0), 64x32 sheets: helmet = head +1.0, chestplate =
             body +1.0 and 4-wide arms +1.0, leggings = body +0.5 and legs +0.4 (textures/entity/equipment/
             humanoid_leggings), boots = legs +0.9; everything else from equipment/humanoid. (Here: arms +1.03 and
             helmet +1.06 for the same no-coplanar reason; the two legs are cropped at the centre line, where the
             game lets them overlap.) Armor is drawn without the hurt overlay; leather = leather.png tinted
             #A06540 + leather_overlay.png.
  walk       HumanoidModel.setupAnim: right leg cos(0.6662 p) 1.4 s, left leg opposite, arms cos(...) 2 s 0.5,
             opposite to their legs; LivingEntity.calculateEntityAnimation: target s = min(4 * blocks per tick, 1),
             s += (target - s) 0.4 each tick, p += s. A full cycle is 9.43 units of p: 2.36 blocks at any speed up
             to 5 blocks/s. Walking 4.317 blocks/s: s 0.863, legs +-69 degrees, 0.55 s per cycle, the planted foot
             slides 11 %; sprinting 5.612: s 1, +-80 degrees, 0.47 s and 2.65 blocks per cycle (5 % slide);
             sneaking 1.295: s 0.26, +-21 degrees, 1.8 s per cycle (the feet slide most of the way: that is the
             game). No body bob in third person. A hand that holds an item swings half as far.
             Speeds: movement speed 0.1 x 0.98 input over (1 - 0.546) = 0.2159 blocks/tick = 4.317/s; sprint x 1.3.
  jump       LivingEntity.jumpFromGround: vy = 0.42 (+0.2 forward when sprinting), then vy = (vy - 0.08) 0.98:
             peak 1.2522 after 6 ticks, back on the ground on tick 12.
  crouch     body.xRot 0.5, arms.xRot +0.4, legs z +4, head y +4.2, body and arms y +3.2 (pixels), and
             AvatarRenderer.getRenderOffset y -2/16: the whole model, feet included, sinks 2 px into the ground.
  arm poses  ITEM x*0.5 - pi/10; BLOCK x*0.5 - 0.9425 + clamp(head pitch, -1.396, 0.436), yaw -+30 degrees +
             clamp(head yaw, +-30); BOW both arms -pi/2 + head pitch, yaw -0.1 / +0.5 + head yaw; TOOT_HORN
             clamp(head pitch, +-1.2) - 1.4835, yaw head -+ 0.5236. Idle: AnimationUtils.bobArms (+-0.05 rad).
  held item  ItemInHandLayer: arm, rotate X -90, Y 180, translate (+-1, 2, -10)/16, then ItemTransform.apply:
             translate, rotate X Y Z, scale (left hand: x translation and Y, Z rotations negated). handheld tools
             rotation (0,-90,55) scale 0.85; flat items scale 0.55; blocks rotation (75,45,0) scale 0.375.
             Shield: ShieldModel plate 12x22x1 + handle 2x6x6, entity/shield/shield_base_nopattern.png.
  hurt/death OverlayTexture: hurt = (255,0,0) at 1 - 178/255 = 30 % over the entity texture for hurtTime 10 ticks
             and while dying; LivingEntityRenderer.setupRotations: roll = sqrt((deathTime - 1) / 20 * 1.6) * 90
             degrees; LivingEntity.makePoofParticles: 20 'poof' on removal at tick 20; knockback(0.4): horizontal
             speed 0.4, vy = min(0.4, vy / 2 + 0.4).

GLINT (optional, enchanted=True)
    Armor: engine.fx.glint on each armor box with misc/enchanted_glint_armor.png and the armor texturing of
    TextureTransform (scale 0.16, 10 degrees, same scroll): ONE broad purple band that drifts over the suit (it
    crosses a chestplate in about a second and is off the armor about half of the time), added as emission so
    the armor keeps its own colours. The armor glint texture is dim (mean 0.07 / 0.03 / 0.18): at the game's own
    strength the band adds about 10 of 255 to the blue of netherite; equip(glint_strength=1.5) is the default
    here, 2.0 is unmistakable, 1.0 is the game. Held flat items: fx.glint as it is (much stronger: the item
    glint texture is five times brighter). Both animate a material: see the stamp note in CONTRACT.md
    (films/oneword.py stamp_every_frame) before a chunked final render.

NOT DONE / NOT THE GAME
  - 'poof' particles of a death: engine.fx has no such kind; die() returns the frame and the point for them.
  - Eating and drinking have no third-person arm animation in Java Edition; eat() / drink() are this module's.
  - Projectiles (arrow, pearl, potion), food crumbs and potion splashes are not drawn here: draw_bow() / throw()
    return frame, origin and direction for whoever draws them.
  - attack() and mine() swing the RIGHT arm (engine.fx); block / toot / eat / hold work for either hand.
  - Not built: capes, elytra, armor trims, dyed leather other than the default brown, shield banners, crossbow /
    trident / spyglass / brush poses, swimming and crawling, riding.
  - Corners of a walk are turned on the spot over about 5 frames (the game snaps the body yaw even faster).

GOTCHAS
  - Items and armor are separate objects parented to the rig; their visibility is the player's AND their own
    timeline, rewritten on every show() / hold() / equip() (never key hide_render on them yourself).
  - The hurt flash is keyed on Object.color (alpha) of the six body parts and read by the skin material through
    Object Info: nothing else may use those objects' colour. engine.stamp does not hash Object.color, so the torso
    is also keyed 0.03 % larger while the flash is on: a frame's fingerprint then changes with the flash
    (measured) and render.py re-renders exactly the frames a new or moved hurt() touches.
  - walk() is the game's gait: +-69 degree legs at 4.3 blocks/s. For a calm stroll pass speed=1.4..1.8
    (+-25 degrees). A walk of 20 blocks takes 120 frames: 111 at speed plus the game's start and slide to a halt.
  - cast_town() names its players after their skins ("steve", "alex", ...): pass names=[...] if the film already
    has a st.actor("steve", "steve"), which is the old engine.characters Steve and not a Player.
  - Flat items (food, ingots, buckets, the horn) lie FLAT on the hand in third person, as in the game: from eye
    height they are seen edge-on; tools and swords point forward out of the fist; blocks sit above the fist.
  - Herobrine's eyes: 2 x 1 texels each, 0.117 block wide per eye. From 18 blocks they are 2-3 px at 720 wide on
    a 35 mm lens; the glow makes them bloom (HEROBRINE_GLOW 3.0; raise to 6-8 for a wide night shot).
"""
import math
import sys

import bpy
import numpy as np
from mathutils import Matrix, Vector

from . import characters as ch
from . import mcassets as mc
from . import pix
from .characters import (CUT_LEAD, FPS, HEAD_YAW_MAX, ITEM_ARM_PITCH, MODEL_SCALE, Character, _clamp, _cut, _ensure,
                         _find, _put, _segment, _val, _vec3, _wrap)

_LOC, _ROT = "location", "rotation_euler"
TICK = FPS / 20.0                       # film frames per game tick
SKINS = ("steve", "alex", "ari", "efe", "kai", "makena", "noor", "sunny", "zuri")
SLIM_BY_DEFAULT = ("alex",)
HEROBRINE_EYES = ((9, 12), (10, 12), (13, 12), (14, 12))      # (u, v) texels of steve.png: the two eyes, 2 x 1 each
HEROBRINE_GLOW = 3.0
ARMOR_MATERIALS = ("leather", "chainmail", "iron", "golden", "diamond", "netherite", "copper", "turtle_scute")
_ARMOR_TEXTURE = {"golden": "gold", "gold": "gold", "chain": "chainmail", "turtle": "turtle_scute"}
LEATHER_COLOR = (0xA0, 0x65, 0x40)      # DyedItemColor.LEATHER_COLOR
ARMOR_SLOTS = ("helmet", "chestplate", "leggings", "boots")
ARMOR_PIECES = {"turtle_scute": ("helmet",)}                 # materials that are not a full set (no leggings sheet)
WALK_SPEED = 4.317                      # 0.1 * 0.98 / (1 - 0.546) blocks per tick * 20
SPRINT_SPEED = 5.612                    # x 1.3
SNEAK_SPEED = 1.295                     # x 0.3 (Attributes.SNEAKING_SPEED)
GROUND_FRICTION = 0.6 * 0.91            # horizontal speed kept per tick on ordinary blocks
JUMP_VELOCITY = 0.42                    # LivingEntity.BASE_JUMP_POWER
GRAVITY = 0.08                          # LivingEntity.DEFAULT_BASE_GRAVITY
HURT_TICKS = 10                         # LivingEntity.HURT_DURATION_TICKS
DEATH_TICKS = 20                        # LivingEntity.DEATH_DURATION
HURT_MIX = 1.0 - 178.0 / 255.0          # OverlayTexture: 0xB2FF0000, colour = mix(red, texture, alpha)
EAT_TICKS = 32                          # Consumable.DEFAULT_CONSUME_SECONDS 1.6
CROUCH = dict(torso_x=0.5, arm_x=0.4, leg_back=4.0, head_down=4.2, body_down=3.2, offset=2.0 / 16.0)
TORSO_TIE = 1.004                       # make_player: the torso is 0.008 px deeper than the arms (their fronts tie)
CROUCH_HEAD_TIE = 0.995                 # sneak(): the head is 0.02 px narrower than the torso it sinks into
POTION_COLOR = (0x38, 0x5D, 0xC6)       # items/splash_potion.json: default tint -13083194
ITEM_ALIASES = {"steak": "cooked_beef", "totem": "totem_of_undying", "pearl": "ender_pearl", "milk": "milk_bucket",
                "music_disc": "music_disc_13", "disc": "music_disc_13", "horn": "goat_horn", "potion": "splash_potion",
                "chicken": "cooked_chicken", "apple": "golden_apple"}


def _jump_arc():
    """Height above the ground after each tick of a jump (LivingEntity.jumpFromGround + travel)."""
    y, vy, out = 0.0, JUMP_VELOCITY, [0.0]
    while True:
        y += vy
        vy = (vy - GRAVITY) * 0.98
        if y <= 0.0:
            out.append(0.0)
            return out
        out.append(y)


JUMP_ARC = _jump_arc()                  # 13 values: ticks 0..12
JUMP_TICKS = len(JUMP_ARC) - 1
JUMP_HEIGHT = max(JUMP_ARC)


SPRINT_JUMP_BOOST = 0.2                 # LivingEntity.jumpFromGround: added along the look while sprinting
SPRINT_ACCEL = 0.13 * 0.98              # ground acceleration per tick while sprinting (speed 0.1 x 1.3, input 0.98)
AIR_ACCEL = 0.026 * 0.98                # Player.getFlyingSpeed while sprinting: 0.025999999
AIR_FRICTION = 0.91


def _hop(v):
    """One sprint-jump from the horizontal speed `v` carried into it (blocks per tick, after friction): the
    distance covered in each of its 12 ticks (the take-off tick on the ground with the jump boost, 11 in the
    air) and the speed carried out of it."""
    out = []
    for t in range(JUMP_TICKS):
        v += SPRINT_JUMP_BOOST + SPRINT_ACCEL if t == 0 else AIR_ACCEL
        out.append(v)
        v *= GROUND_FRICTION if t == 0 else AIR_FRICTION
    return out, v


def _steady_hop():
    """(per-tick distances, carried speed) of a sprint-jump in the steady state of bunny-hopping."""
    steps, v = [], 0.0
    for _i in range(40):
        steps, v = _hop(v)
    return steps, v


HOP_STEPS, HOP_CARRY = _steady_hop()    # 0.609 blocks on the take-off tick, 0.30 .. 0.36 in the air
SPRINT_JUMP_SPEED = sum(HOP_STEPS) / JUMP_TICKS * 20.0      # blocks per second, averaged over a hop (7.13)


def _frame_ceil(x):
    """The first whole frame at or after x (safe against float noise in sums of 1.2-frame ticks)."""
    return int(math.ceil(x - 1e-6))


def _ramps(ramp):
    return (bool(ramp), bool(ramp)) if isinstance(ramp, (bool, int)) else (bool(ramp[0]), bool(ramp[1]))


# ----------------------------------------------------------------------------------------------------
# skins and their material
# ----------------------------------------------------------------------------------------------------
def skin_sheet(skin="steve", slim=False):
    """(key, HxWx4 uint8 sheet, glow mask or None) of a default skin; 'herobrine' = steve.png with white eyes."""
    src = "steve" if skin == "herobrine" else skin
    if src not in SKINS:
        raise ValueError("unknown skin %r (use one of %s, herobrine)" % (skin, ", ".join(SKINS)))
    arr = ch._game_texture("entity/player/%s/%s" % ("slim" if slim else "wide", src))
    sheet = np.zeros_like(arr)
    ch._over(sheet, arr)
    mask = None
    if skin == "herobrine":
        mask = np.zeros_like(sheet)
        mask[..., 3] = 255
        for u, v in HEROBRINE_EYES:
            sheet[v, u] = (255, 255, 255, 255)
            mask[v, u, :3] = 255
    return "%s_%s" % (skin, "slim" if slim else "wide"), sheet, mask


def _socket(sockets, name, kind=None):
    for s in sockets:
        if s.name == name and (kind is None or s.type == kind):
            return s
    raise KeyError(name)


def _skin_material(key, sheet, mask=None, glow=0.0):
    """The skin: Closest pixels, the hurt overlay driven by Object.color alpha, optional emission where mask is set."""
    # 'cast_player' in the name is what tools/palette_check.py recognises as Steve (shirt hue, trousers not crushed)
    name = "%s_%s%s" % ("cast_player" if key.startswith(("steve", "herobrine")) else "player_skin", key,
                        "_glow%g" % glow if mask is not None and glow > 0 else "")
    mat = bpy.data.materials.get(name)
    if mat is not None and mat.get("player_sheet") == key:
        return mat
    mat = pix.pixel_material(name, ch._memory_image(name, sheet), alpha="OPAQUE", roughness=0.95)
    nt = mat.node_tree
    N, L = nt.nodes.new, nt.links.new
    bsdf = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
    tex = next(n for n in nt.nodes if n.type == "TEX_IMAGE")
    info = N("ShaderNodeObjectInfo")
    inv = N("ShaderNodeMath")                              # hurt = (1 - Object.color alpha) * HURT_MIX
    inv.operation = "SUBTRACT"
    inv.inputs[0].default_value = 1.0
    L(_socket(info.outputs, "Alpha"), inv.inputs[1])
    fac = N("ShaderNodeMath")
    fac.operation = "MULTIPLY"
    fac.inputs[1].default_value = HURT_MIX
    L(inv.outputs[0], fac.inputs[0])
    disp = N("ShaderNodeGamma")                            # the game mixes display values
    disp.inputs["Gamma"].default_value = 1.0 / 2.2
    L(tex.outputs["Color"], disp.inputs["Color"])
    mix = N("ShaderNodeMix")
    mix.data_type = "RGBA"
    mix.blend_type = "MIX"
    L(fac.outputs[0], _socket(mix.inputs, "Factor", "VALUE"))
    L(disp.outputs[0], _socket(mix.inputs, "A", "RGBA"))
    _socket(mix.inputs, "B", "RGBA").default_value = (1.0, 0.0, 0.0, 1.0)
    lin = N("ShaderNodeGamma")
    lin.inputs["Gamma"].default_value = 2.2
    L(_socket(mix.outputs, "Result", "RGBA"), lin.inputs["Color"])
    L(lin.outputs[0], bsdf.inputs["Base Color"])
    if mask is not None and glow > 0:
        mname = name + "_mask"
        mimg = ch._memory_image(mname, mask)
        mimg.colorspace_settings.name = "Non-Color"
        mt = N("ShaderNodeTexImage")
        mt.image = mimg
        mt.interpolation = "Closest"
        mul = N("ShaderNodeMath")
        mul.operation = "MULTIPLY"
        mul.inputs[1].default_value = float(glow)
        L(mt.outputs["Color"], mul.inputs[0])
        bsdf.inputs["Emission Color"].default_value = (1.0, 1.0, 1.0, 1.0)
        L(mul.outputs[0], bsdf.inputs["Emission Strength"])
    mat["player_sheet"] = key
    return mat


# ----------------------------------------------------------------------------------------------------
# the model
# ----------------------------------------------------------------------------------------------------
def _player_spec(slim=False):
    """HumanoidModel.createMesh + PlayerModel.createMesh(slim) for characters._build_rig. `body` is an empty
    carrier at the hip (head, arms and torso hang on it); `torso` holds the body box and pivots at the neck, where
    the game's body part pivots, so the crouch tilts it without tilting head and arms."""
    c = ch._cube
    aw, rx = (3, -2) if slim else (4, -3)
    return dict(
        tex=(64, 64), scale=MODEL_SCALE, hip=12.0, top=-8.0, eye=-3.5, back=2.0, sleep_eye=1.62,
        parts=[
            dict(name="body", parent="hips", pivot=(0, 12, 0), groups=[]),
            dict(name="torso", parent="body", pivot=(0, 0, 0), groups=[([], [
                c(16, 16, -4, 0, -2, 8, 12, 4), c(16, 32, -4, 0, -2, 8, 12, 4, grow=0.25)])]),
            dict(name="head", parent="body", pivot=(0, 0, 0), groups=[([], [
                c(0, 0, -4, -8, -4, 8, 8, 8), c(32, 0, -4, -8, -4, 8, 8, 8, grow=0.5)])]),
            dict(name="arm_r", parent="body", pivot=(-5, 2, 0), groups=[([], [
                c(40, 16, rx, -2, -2, aw, 12, 4), c(40, 32, rx, -2, -2, aw, 12, 4, grow=0.27)])]),
            dict(name="arm_l", parent="body", pivot=(5, 2, 0), groups=[([], [
                c(32, 48, -1, -2, -2, aw, 12, 4), c(48, 48, -1, -2, -2, aw, 12, 4, grow=0.27)])]),
            dict(name="leg_r", parent="hips", pivot=(-1.9, 12, 0), xclip=(None, 1.9), groups=[([], [
                c(0, 16, -2, 0, -2, 4, 12, 4), c(0, 32, -2, 0, -2, 4, 12, 4, grow=0.23)])]),
            dict(name="leg_l", parent="hips", pivot=(1.9, 12, 0), xclip=(-1.9, None), groups=[([], [
                c(16, 48, -2, 0, -2, 4, 12, 4), c(0, 48, -2, 0, -2, 4, 12, 4, grow=0.23)])]),
        ])


LEG_ARMOR_STAGGER = 0.03               # px: the left leg's armor box is this much larger than the right leg's


# armor boxes per slot: (rig part, cubes, x crop in part pixels), HumanoidModel.createBaseArmorMesh
def _armor_parts(slot):
    """The leg boxes are the game's WHOLE boxes: they reach 0.5 px (leggings) and 1.0 px (boots) past the centre
    line, into the other leg, exactly as in the game. Cropping them at the centre line put their inner face on the
    leg's own inner face (a depth tie that the trousers won: hollow boots). The left leg's box is LEG_ARMOR_STAGGER
    larger, so the two legs' fronts, backs, tops and soles are never coplanar where they overlap; the left one
    shows there, as in the game, which draws the left leg last."""
    c = ch._cube
    if slot == "helmet":
        return [("head", [c(0, 0, -4, -8, -4, 8, 8, 8, grow=1.06)], (None, None))]
    if slot == "chestplate":
        return [("torso", [c(16, 16, -4, 0, -2, 8, 12, 4, grow=1.0)], (None, None)),
                ("arm_r", [c(40, 16, -3, -2, -2, 4, 12, 4, grow=1.03)], (None, None)),
                ("arm_l", [c(40, 16, -1, -2, -2, 4, 12, 4, grow=1.03, mirror=True)], (None, None))]
    grow = 0.4 if slot == "leggings" else 0.9
    parts = [("leg_r", [c(0, 16, -2, 0, -2, 4, 12, 4, grow=grow)], (None, None)),
             ("leg_l", [c(0, 16, -2, 0, -2, 4, 12, 4, grow=grow + LEG_ARMOR_STAGGER, mirror=True)], (None, None))]
    if slot == "leggings":
        parts.insert(0, ("torso", [c(16, 16, -4, 0, -2, 8, 12, 4, grow=0.5)], (None, None)))
    return parts


def _box_mesh(name, cubes, sheet, to_local, material, clip=(None, None), clip_scale=1.0):
    """Mesh of entity boxes (ModelPart.Cube unwrap, as characters._part_mesh) with clear texels cut out and the
    geometry CROPPED to lo <= local x <= hi (clip, in the units of to_local / clip_scale): texels keep their size."""
    sh, sw = sheet.shape[:2]
    opaque = sheet[..., 3] >= ch.ALPHA_CUTOUT
    lo, hi = (None if k is None else k * clip_scale for k in clip)
    verts, faces, uvs = [], [], []
    for c in cubes:
        x, y, z = c["pos"]
        w, h, d = c["size"]
        centre = to_local((x + w / 2.0, y + h / 2.0, z + d / 2.0))
        for quad in ch._cube_faces(c):
            pts = [to_local(p) for p, _uv in quad]
            tex = [uv for _p, uv in quad]
            ua, va = tex[0]
            b = next(i for i in (1, 3) if tex[i][1] == va)
            dd = 4 - b
            ub, vd = tex[b][0], tex[dd][1]
            if ua == ub or va == vd:
                continue
            du, dv = (pts[b] - pts[0]) / (ub - ua), (pts[dd] - pts[0]) / (vd - va)
            flat = abs(du.x) < 1e-9 and abs(dv.x) < 1e-9             # a face square to the x axis
            shift = 0.0
            if flat:
                if hi is not None and pts[0].x > hi:
                    shift = hi - pts[0].x
                if lo is not None and pts[0].x < lo:
                    shift = lo - pts[0].x
            u_lo, u_hi = int(round(min(ua, ub))), int(round(max(ua, ub)))
            v_lo, v_hi = int(round(min(va, vd))), int(round(max(va, vd)))
            if u_lo < 0 or v_lo < 0 or u_hi > sw or v_hi > sh:
                continue
            outward = sum(pts, Vector()) / 4.0 - centre
            for (c0, r0, c1, r1) in ch._rects(opaque[v_lo:v_hi, u_lo:u_hi]):
                box = [c0 + u_lo, r0 + v_lo, c1 + u_lo, r1 + v_lo]   # texel rectangle, float after cropping
                if not flat:
                    k, g, base = (0, du.x, pts[0].x - du.x * ua - dv.x * va) if abs(du.x) > 1e-9 else \
                                 (1, dv.x, pts[0].x - du.x * ua - dv.x * va)
                    for limit, upper in ((lo, False), (hi, True)):    # x = base + g * coordinate
                        if limit is None:
                            continue
                        t = (limit - base) / g
                        if (g > 0) == upper:
                            box[k + 2] = min(box[k + 2], t)
                        else:
                            box[k] = max(box[k], t)
                    if box[k + 2] - box[k] < 1e-4:
                        continue
                a0, b0, a1, b1 = box
                corners = [(a0, b0), (a1, b0), (a1, b1), (a0, b1)]
                ps = [pts[0] + du * (cu - ua) + dv * (cv - va) + Vector((shift, 0.0, 0.0)) for cu, cv in corners]
                e = 0.02
                tu = [(a0 + e, b0 + e), (a1 - e, b0 + e), (a1 - e, b1 - e), (a0 + e, b1 - e)]
                if (ps[1] - ps[0]).cross(ps[3] - ps[0]).dot(outward) < 0.0:
                    ps.reverse()
                    tu.reverse()
                n = len(verts)
                verts.extend(tuple(p) for p in ps)
                faces.append((n, n + 1, n + 2, n + 3))
                uvs.extend((tx / sw, 1.0 - ty / sh) for tx, ty in tu)
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    layer = me.uv_layers.new(name="UVMap")
    if uvs:
        layer.data.foreach_set("uv", [x for uv in uvs for x in uv])
    me.materials.append(material)
    me.update()
    return me


def armor_sheet(material, leggings=False):
    """(key, HxWx4 uint8) of textures/entity/equipment/humanoid[_leggings]/<material>.png (leather: dyed + overlay)."""
    tex = _ARMOR_TEXTURE.get(material, material)
    folder = "entity/equipment/humanoid_leggings" if leggings else "entity/equipment/humanoid"
    arr = ch._game_texture("%s/%s" % (folder, tex))
    sheet = np.zeros_like(arr)
    if tex == "leather":
        dyed = arr.astype(np.float32)
        dyed[..., :3] *= np.array(LEATHER_COLOR, dtype=np.float32) / 255.0
        ch._over(sheet, np.clip(dyed, 0, 255).astype(np.uint8))
        ch._over(sheet, ch._game_texture(folder + "/leather_overlay"))
    else:
        ch._over(sheet, arr)
    return "%s%s" % (tex, "_leggings" if leggings else ""), sheet


def _armor_material(key, sheet):
    name = "player_armor_" + key
    mat = bpy.data.materials.get(name)
    if mat is not None and mat.get("player_sheet") == key:
        return mat
    mat = pix.pixel_material(name, ch._memory_image(name, sheet), alpha="OPAQUE", roughness=0.9)
    mat["player_sheet"] = key
    return mat


def _armor_glint(ob, strength=1.0, light=0.75):
    """engine.fx.glint on an armor box, switched to the armor glint texture and TextureTransform's armor scale."""
    from . import fx

    mat = fx.glint(ob, frame_start=1, strength=strength, light=light)
    nt = mat.node_tree
    name = "players/enchanted_glint_armor"
    img = bpy.data.images.get(name)
    if img is None:
        img = mc.image_from_array(name, np.array(mc.texture_array("misc/enchanted_glint_armor"), dtype=np.uint8))
        img.colorspace_settings.name = "Non-Color"
    nt.nodes["fx_glint"].image = img
    nt.nodes["fx_glint_scroll"].inputs["Scale"].default_value = (0.16, 0.16, 1.0)   # armor_entity_glint_texturing
    return mat


# ----------------------------------------------------------------------------------------------------
# held items
# ----------------------------------------------------------------------------------------------------
def _display(chain, context, fallback=None):
    """display.<context> of a model chain as (rotation degrees, translation / 16, scale); nearest model wins."""
    for raw in chain:
        g = raw.get("display", {}).get(context)
        if g is not None:
            return (tuple(float(v) for v in g.get("rotation", (0, 0, 0))),
                    tuple(float(v) for v in g.get("translation", (0, 0, 0))),
                    tuple(float(v) for v in g.get("scale", (1, 1, 1))))
    if fallback is not None:
        return _display(chain, fallback)
    return ((0.0, 0.0, 0.0), (0.0, 0.0, 0.0), (1.0, 1.0, 1.0))


def hand_matrix(display, left=False, scale=MODEL_SCALE, slim=False):
    """Parent-space matrix (the arm part's frame) of a held item: ItemInHandLayer.submitArmWithItem followed by
    ItemTransform.apply(leftHand). The item's mesh must be centred on the middle of its 16 x 16 x 16 item cube with
    item x along Blender x, item up (y) along Blender z and its front (item +z) toward Blender -y, as
    props.make_item and mcassets.quads_object(origin=(8, 8, 8)) build them. display = (rotation, translation, scale)."""
    rot, trans, sc = display
    s = -1.0 if left else 1.0
    R = Matrix.Rotation
    chain = (R(math.radians(-90.0), 4, "X") @ R(math.radians(180.0), 4, "Y")
             @ Matrix.Translation((s / 16.0, 2.0 / 16.0, -10.0 / 16.0))
             @ Matrix.Translation((s * trans[0] / 16.0, trans[1] / 16.0, trans[2] / 16.0))
             @ R(math.radians(rot[0]), 4, "X") @ R(math.radians(s * rot[1]), 4, "Y") @ R(math.radians(s * rot[2]), 4, "Z")
             @ Matrix.Diagonal((sc[0], sc[1], sc[2], 1.0)))
    if slim:                                               # PlayerModel.translateToHand: the slim arm half a pixel in
        chain = Matrix.Translation((0.5 * s / 16.0, 0.0, 0.0)) @ chain
    return Matrix.Diagonal((scale, scale, scale, 1.0)) @ ch._AXES @ chain @ ch._AXES


def _sprite_object(name, arr, material):
    """Flat item from an RGBA array: one pixel thick, 16 px = 1 unit, centred, in the local XZ plane, front -Y
    (the same mesh engine.mcassets.item_object builds, for sprites that are composed in memory)."""
    h, w = arr.shape[:2]
    solid = arr[..., 3] >= 128
    mb = mc.MeshBuilder()
    s = 1.0 / 16.0
    t = s / 2.0
    su, sv = 16.0 / w, 16.0 / h
    for r in range(h):
        for c in range(w):
            if not solid[r, c]:
                continue
            x0, x1 = (c - w / 2.0) * s, (c + 1 - w / 2.0) * s
            z1, z0 = (h / 2.0 - r) * s, (h / 2.0 - r - 1) * s
            e = 0.02
            uv = [((c + e) * su, (r + e) * sv), ((c + e) * su, (r + 1 - e) * sv), ((c + 1 - e) * su, (r + 1 - e) * sv),
                  ((c + 1 - e) * su, (r + e) * sv)]
            mb.add("m", [(x0, -t, z1), (x0, -t, z0), (x1, -t, z0), (x1, -t, z1)], uv)
            mb.add("m", [(x1, t, z1), (x1, t, z0), (x0, t, z0), (x0, t, z1)], [uv[3], uv[2], uv[1], uv[0]])
            if c == 0 or not solid[r, c - 1]:
                mb.add("m", [(x0, t, z1), (x0, t, z0), (x0, -t, z0), (x0, -t, z1)], uv)
            if c == w - 1 or not solid[r, c + 1]:
                mb.add("m", [(x1, -t, z1), (x1, -t, z0), (x1, t, z0), (x1, t, z1)], uv)
            if r == 0 or not solid[r - 1, c]:
                mb.add("m", [(x0, t, z1), (x0, -t, z1), (x1, -t, z1), (x1, t, z1)], uv)
            if r == h - 1 or not solid[r + 1, c]:
                mb.add("m", [(x0, -t, z0), (x0, t, z0), (x1, t, z0), (x1, -t, z0)], uv)
    me = mb.mesh("m", name)
    me.materials.append(material)
    return bpy.data.objects.new(name, me)


def _potion_object(item_id, color):
    """A potion bottle: layer0 (item/potion_overlay, tinted with the potion colour) under layer1 (the bottle)."""
    chain = _model_chain("item/" + item_id)
    texs = chain[0].get("textures", {})
    over = np.array(mc.texture_array(texs["layer0"].replace("minecraft:", "")), dtype=np.float32)
    over[..., :3] *= np.array(color, dtype=np.float32) / 255.0
    arr = np.zeros(over.shape, dtype=np.uint8)
    ch._over(arr, np.clip(over, 0, 255).astype(np.uint8))
    ch._over(arr, np.array(mc.texture_array(texs["layer1"].replace("minecraft:", "")), dtype=np.uint8))
    name = "item_%s_%02x%02x%02x" % ((item_id,) + tuple(color))
    mat = bpy.data.materials.get(name)
    if mat is None:
        mat = pix.pixel_material(name, mc.image_from_array(name, arr), alpha="OPAQUE")
    return _sprite_object(name, arr, mat)


def _shield_object():
    """ShieldModel (plate 12 x 22 x 1 at (0, 0), handle 2 x 6 x 6 at (26, 0), 64 x 64) in item coordinates: the
    special renderer draws it from the item cube's CORNER, flipped by the transformation scale (1, -1, -1) of
    items/shield.json."""
    arr = ch._game_texture("entity/shield/shield_base_nopattern")
    sheet = np.zeros_like(arr)
    ch._over(sheet, arr)
    name = "item_shield"
    mat = bpy.data.materials.get("player_shield")
    if mat is None:
        mat = pix.pixel_material("player_shield", ch._memory_image("player_shield", sheet), alpha="OPAQUE")
    cubes = [ch._cube(0, 0, -6, -11, -2, 12, 22, 1), ch._cube(26, 0, -1, -3, -1, 2, 6, 6)]
    me = _box_mesh(name, cubes, sheet, lambda p: Vector(((p[0] - 8.0) / 16.0, (p[2] + 8.0) / 16.0, (-p[1] - 8.0) / 16.0)), mat)
    return bpy.data.objects.new(name, me)


def _model_chain(name):
    from . import mobs

    return mobs._model_chain(name)


def _build_item(item_id, variant=None, potion_color=None):
    """(Object, model chain) of a held item. variant = another model of the same item (bow_pulling_1,
    tooting_goat_horn, shield_blocking): its sprite and its display transforms."""
    item_id = ITEM_ALIASES.get(item_id, item_id).replace("minecraft:", "")
    model = variant or item_id
    if item_id == "shield":
        return _shield_object(), _model_chain("item/" + model)
    chain = _model_chain("item/" + model)
    if any(raw.get("builtin") == "builtin/generated" for raw in chain):
        if "layer1" in chain[0].get("textures", {}) and "potion" in item_id:
            return _potion_object(model, potion_color or POTION_COLOR), chain
        return mc.item_object(model), chain
    if mc.has_blockstate(item_id):
        from .blocks import block_material

        def material_for(q):
            return block_material(q.texture, mc.block_tint(item_id, q.tintindex), shade=getattr(q, "shade", None))

        quads = mc.bake_block(item_id)
        if not quads:                                           # chest, bed, banner, skull ...: no block model
            raise ValueError("%r is drawn by an entity model in the game (no item or block model to hold): "
                             "players.hold cannot build it" % (item_id,))
        ob = mc.quads_object("item_" + item_id, quads, material_for, None, origin=(8.0, 8.0, 8.0))
        return ob, _model_chain("block/" + item_id)
    raise ValueError("no item model and no block called %r" % (item_id,))


class _Attached:
    """One object riding on the rig (an armor box, a held item variant) with its own on / off timeline."""

    def __init__(self, ob, on=None):
        self.ob = ob
        self.steps = [(None, True)] if on is None else [(None, False), (int(on), True)]

    def set(self, frame, on):
        if frame is None:
            self.steps = [(None, bool(on))]
        else:
            self.steps = [s for s in self.steps if s[0] is None or s[0] < frame] + [(int(frame), bool(on))]

    def at(self, frame):
        state = False
        for f, on in self.steps:
            if f is None or f <= frame:
                state = on
        return state


class _Held:
    """What one hand holds over a span: the item's objects by variant ('' = as carried)."""

    def __init__(self, item_id, side, start):
        self.item_id, self.side, self.start, self.end = item_id, side, start, None
        self.variants = {}                # variant name -> _Attached
        self.chain = None
        self.enchanted = False
        self.potion_color = None

    def active(self, frame):
        return (self.start is None or self.start <= frame) and (self.end is None or frame < self.end)


# ----------------------------------------------------------------------------------------------------
# the player
# ----------------------------------------------------------------------------------------------------
class Player(Character):
    """A player on the game's player model: see the module docstring for the API."""

    def __init__(self, name, parts, spec, skin, slim, collection):
        super().__init__(name, "player", parts, spec)
        self.skin, self.slim, self.collection = skin, slim, collection
        self.torso = parts["torso"]
        self.still = False
        self.idle_seed = sum(ord(c) for c in name) % 97
        self._vis = []                    # [(frame, visible)] from show()
        self._attached = []               # every _Attached (armor boxes and item variants)
        self._hands = {"r": [], "l": []}  # side -> [_Held] in time order
        self._armor = {s: [] for s in ARMOR_SLOTS}     # slot -> [(frame or None, material or None, [_Attached])]
        self._crouch = []                 # [(frame, bool)]
        self._gait = None                 # the last move's limb cycle: dict(f0, ps, ss, end, carry); None after a cut
        self._phase = 0.0                 # walk-cycle position p where the last move left it
        self._red = []                    # [(start, end or None)]: spans of the red hurt / death overlay
        self.size = (0.6, 1.8)            # the hit box (EntityType.PLAYER): what engine.animals.poof fills
        for ob in (self.torso,):
            for i in range(3):
                self._pose.append((ob, _ROT, i, 0.0))
        for ob in (self.body, self.head, self.arm_l, self.arm_r, self.leg_l, self.leg_r):
            for i in range(3):
                self._pose.append((ob, _LOC, i, float(ob.location[i])))
        self._pose.append((self.head, "scale", 0, 1.0))        # narrowed a hair while crouching (CROUCH_HEAD_TIE)
        self.meshes = [parts[k] for k in ("torso", "head", "arm_r", "arm_l", "leg_r", "leg_l")]

    def __repr__(self):
        return "<Player %s %s%s>" % (self.name, self.skin, " slim" if self.slim else "")

    # ------------------------------------------------------------------ state queries
    def crouching_at(self, frame):
        """True while the sneak pose is on at `frame`."""
        state = False
        for f, on in self._crouch:
            if f <= frame + 1e-6:
                state = on
        return state

    def _held_at(self, side, frame):
        for h in reversed(self._hands[side]):
            if h.active(frame):
                return h
        return None

    def holding_at(self, hand, frame):
        """Item id in a hand at `frame`, or None."""
        h = self._held_at(_side(hand), frame)
        return h.item_id if h else None

    def armor_at(self, slot, frame):
        """Material of the armor piece worn in `slot` at `frame`, or None."""
        cur = None
        for f, material, _atts in self._armor[slot]:
            if f is None or f <= frame:
                cur = material
        return cur

    def item(self, hand="right", frame=None):
        """The object held in a hand (as carried), or None."""
        hs = self._hands[_side(hand)]
        h = (hs[-1] if hs else None) if frame is None else self._held_at(_side(hand), frame)
        return h.variants[""].ob if h and "" in h.variants else None

    def item_point(self, hand, frame):
        """World centre of the item cube of the hand's item at `frame` (the hand's grip if it is empty)."""
        side = _side(hand)
        arm = self.arm_r if side == "r" else self.arm_l
        h = self._held_at(side, frame)
        scene = bpy.context.scene
        cur, sub = scene.frame_current, scene.frame_subframe
        whole = int(math.floor(frame))
        scene.frame_set(whole, subframe=float(frame) - whole)
        if h is not None:
            shown = [a.ob for a in h.variants.values() if not a.ob.hide_render] or [h.variants[""].ob]
            point = shown[0].matrix_world.translation.copy()
        else:
            point = arm.matrix_world @ Vector(((-1.0 if side == "r" else 1.0) * self.unit, -2.0 * self.unit, -10.0 * self.unit))
        scene.frame_set(cur, subframe=sub)
        return point

    def eye_point(self, frame):
        """World point between the eyes at `frame`: standing, crouching, jumping, or lying after lie_down."""
        p = super().eye_point(frame)
        lying = None
        for f, point in self._lying:
            if f <= frame + 1e-6:
                lying = point
        if lying is not None:
            return p
        for ob in (self.hips, self.body, self.head):
            p.z += _val(ob, _LOC, 2, frame) - self._rest(ob, _LOC, 2)
        return p

    def _arm(self, side):
        return self.arm_r if side == "r" else self.arm_l

    def _arm_base(self, side, frame):
        """Rest pitch of an arm at `frame`: ArmPose ITEM while the hand holds something, +0.4 while crouching."""
        base = ITEM_ARM_PITCH if self._held_at(side, frame) is not None else 0.0
        return base + (CROUCH["arm_x"] if self.crouching_at(frame) else 0.0)

    def _rebase(self, side, frame, old):
        """After a change of state on `frame`: move an arm that hangs at its old rest pitch to the new one."""
        arm = self._arm(side)
        new = self._arm_base(side, frame if frame is not None else 0)
        if frame is None:
            if abs(float(arm.rotation_euler[0]) - old) < 1e-6:
                self._set_rest(arm, _ROT, 0, new)
        elif abs(_val(arm, _ROT, 0, frame) - old) < 1e-4 and abs(new - old) > 1e-9:
            _cut(arm, _ROT, 0, frame, new)

    # ------------------------------------------------------------------ visibility
    def objects(self):
        """The rig's own objects (root first); armor and items are handled by their timelines."""
        return [self.parts["root"]] + [o for k, o in self.parts.items() if k != "root"]

    def _visible_at(self, frame):
        state = True
        for f, on in self._vis:
            if f <= frame:
                state = on
        return state

    def show(self, frame, visible=True):
        """Key render (and viewport) visibility of the rig, its armor and what it holds from `frame` on."""
        self._vis = sorted([v for v in self._vis if v[0] != frame] + [(int(frame), bool(visible))])
        super().show(frame, visible)
        self._refresh()

    def _refresh(self):
        """Rewrite the visibility of every attached object: the player's timeline AND the object's own."""
        own = [f for f, _on in self._vis]
        for att in self._attached:
            frames = sorted(set(own) | {f for f, _on in att.steps if f is not None})
            ob = att.ob
            for path in ("hide_render", "hide_viewport"):
                fc = _find(ob, path, 0)
                if fc is not None:
                    fc.keyframe_points.clear()
                first = att.at(-10 ** 9) and (self._visible_at(-10 ** 9))
                setattr(ob, path, not first)
                if not frames:
                    continue
                fc = _ensure(ob, path, 0)
                _put(fc, min(frames[0], 1) - 1, 0.0 if first else 1.0, "CONSTANT")
                for f in frames:
                    on = att.at(f) and self._visible_at(f)
                    _put(fc, f, 0.0 if on else 1.0, "CONSTANT")
                fc.update()

    def _attach(self, ob, part, matrix=None, on=None):
        if ob.name not in self.collection.objects:
            self.collection.objects.link(ob)
        ob.parent = self.parts[part]
        ob.matrix_parent_inverse = Matrix.Identity(4)
        ob.matrix_basis = matrix if matrix is not None else Matrix.Identity(4)
        att = _Attached(ob, on)
        self._attached.append(att)
        return att

    # ------------------------------------------------------------------ placement
    def place(self, frame, pos, yaw=0.0, keep_pose=False):
        """Hard-set position and yaw from `frame` on: neutral standing pose, upright, not crouching (shot cuts)."""
        super().place(frame, pos, yaw, keep_pose=keep_pose)
        if keep_pose:
            return
        if _find(self.root, _ROT, 1) is not None:
            _cut(self.root, _ROT, 1, frame, 0.0)
        if self._red_at(frame):
            self.revive(frame)                                  # placed again after a blow or dying: his own colours
        if self.crouching_at(frame):
            self._crouch = [c for c in self._crouch if c[0] < frame] + [(frame, False)]
        for side in "rl":
            arm, base = self._arm(side), self._arm_base(side, frame)
            if abs(base - self._rest(arm, _ROT, 0)) > 1e-9:
                _cut(arm, _ROT, 0, frame, base)
        self._gait = None

    def stand_still(self, frame):
        """Cut to the dead-still pose on `frame`: everything at rest, arms hanging perfectly straight."""
        self._reset_pose(frame)
        for arm in (self.arm_r, self.arm_l):
            _cut(arm, _ROT, 1, frame, 0.0)

    sleep = Character.lie_down

    # ------------------------------------------------------------------ held items
    def hold(self, item, hand="right", frame=None, enchanted=False, potion_color=None, like=None):
        """Put an item (id, props.make_item object or None) in a hand, for good or from `frame` on; returns its object.
        An Object is held with the transform of a flat item (item/generated) unless like="iron_sword" names the
        item whose third-person transform it should take."""
        side = _side(hand)
        old = self._arm_base(side, frame if frame is not None else 0)
        for h in self._hands[side]:
            if h.end is None and (frame is None or h.active(frame) or (h.start is not None and h.start >= frame)):
                h.end = frame if frame is not None else -10 ** 9
                for att in h.variants.values():
                    att.set(frame, False)
        ob = None
        if item is not None:
            h = _Held(item if isinstance(item, str) else "object", side, frame)
            h.enchanted, h.potion_color = enchanted, potion_color
            if isinstance(item, str):
                h.item_id = ITEM_ALIASES.get(item, item).replace("minecraft:", "")
                ob = self._variant(h, "")
            else:
                ob = item
                h.chain = _model_chain("item/" + (ITEM_ALIASES.get(like, like).replace("minecraft:", "") if like
                                                  else "generated"))
                h.variants[""] = self._attach(ob, "arm_" + side, self._item_matrix(h.chain, side), on=frame)
                if enchanted:
                    self._glint(ob)
            self._hands[side].append(h)
        self._rebase(side, frame, old)
        self._refresh()
        return ob

    def _item_matrix(self, chain, side):
        left = side == "l"
        display = _display(chain, "thirdperson_lefthand" if left else "thirdperson_righthand",
                           fallback="thirdperson_righthand")
        return hand_matrix(display, left=left, scale=self.model_scale, slim=self.slim)

    def _glint(self, ob):
        from . import fx

        if ob.data.materials and any(n.type == "BSDF_PRINCIPLED" for n in ob.data.materials[0].node_tree.nodes):
            fx.glint(ob, frame_start=1)

    def _variant(self, held, variant):
        """The object of a held item's model variant (built on first use, hidden until switched to)."""
        if variant in held.variants:
            return held.variants[variant].ob
        ob, chain = _build_item(held.item_id, variant or None, held.potion_color)
        if not variant:
            held.chain = chain
        ob.name = "%s_%s_%s" % (self.name, variant or held.item_id, held.side)
        att = self._attach(ob, "arm_" + held.side, self._item_matrix(chain, held.side), on=held.start)
        if variant:
            att.set(None, False)
        if held.enchanted:
            self._glint(ob)
        held.variants[variant] = att
        return ob

    def _use_variant(self, side, variant, frame_start, frame_end):
        """Show another model of the hand's item on [frame_start, frame_end) (bow pulling, horn tooting, shield up)."""
        held = self._held_at(side, frame_start)
        if held is None or held.item_id == "object":
            return
        self._variant(held, variant)
        for name, att in held.variants.items():
            if name == variant:
                att.set(int(frame_start), True)
                att.steps.append((int(frame_end), False))
            elif att.at(frame_start):
                att.set(int(frame_start), False)
                att.steps.append((int(frame_end), True))
        self._refresh()

    # ------------------------------------------------------------------ armor
    def equip(self, material=None, enchanted=False, frame=None, **pieces):
        """Wear armor: see players.equip."""
        return equip(self, material, enchanted=enchanted, frame=frame, **pieces)

    # ------------------------------------------------------------------ locomotion
    def _path(self, f0, points, from_current):
        here = self.pos_at(f0)
        pts = [_vec3(p, here.z) for p in points]
        if from_current:
            pts.insert(0, here.copy())
        path = pts[:1]
        for p in pts[1:]:
            if (p - path[-1]).length > 1e-5:
                path.append(p)
        if (path[0] - here).length > 1e-4:
            for i in range(3):
                _cut(self.root, _LOC, i, f0, path[0][i], hold_rest=False)
            return path, True
        return path, False

    def _yaw_keys(self, f0, path, times, teleport, turn=5.0):
        """Body yaw along a polyline: already facing the first leg on a cut, short eased turns at the corners."""
        yaw_now = self.yaw_at(f0)
        yaws, prev = [], yaw_now
        for a, b in zip(path, path[1:]):
            d = b - a
            if math.hypot(d.x, d.y) > 1e-5:
                prev = prev + _wrap(math.atan2(d.x, -d.y) - prev)
            yaws.append(prev)
        if teleport or ch._cut_at(self.root, _LOC, 0, f0):
            _cut(self.root, _ROT, 2, f0, yaws[0], hold_rest=False)
            yaw_now = yaws[0]
        f1 = times[-1]
        ykeys = [(float(f0), yaw_now, "LINEAR")]
        t_free = float(f0)
        if abs(yaws[0] - yaw_now) > 1e-4:
            d = min(turn * _clamp(abs(yaws[0] - yaw_now) / (math.pi / 2), 0.6, 2.0), 0.6 * (times[1] - f0))
            ykeys = [(float(f0), yaw_now, "SMOOTH"), (f0 + d, yaws[0], "LINEAR")]
            t_free = f0 + d
        for i in range(1, len(yaws)):
            if abs(yaws[i] - yaws[i - 1]) < 1e-4:
                continue
            h = min(turn / 2.0, 0.45 * (times[i] - times[i - 1]), 0.45 * (times[i + 1] - times[i]))
            ts = max(times[i] - h, t_free)
            if ts <= ykeys[-1][0] + 1e-3:
                ykeys[-1] = (ykeys[-1][0], ykeys[-1][1], "SMOOTH")
            else:
                ykeys.append((ts, yaws[i - 1], "SMOOTH"))
            ykeys.append((times[i] + h, yaws[i], "LINEAR"))
            t_free = times[i] + h
        if f1 > ykeys[-1][0] + 1e-3:
            ykeys.append((float(f1), yaws[-1]))
        if len(ykeys) > 1:
            _segment(self.root, _ROT, 2, ykeys)

    def _travel(self, f0, path, cum):
        """Key the root along `path`: cum[k] = distance covered after tick k. Returns the frame of each vertex."""
        seg = [(b - a).length for a, b in zip(path, path[1:])]
        marks = [0.0]
        for length in seg:
            marks.append(marks[-1] + length)
        marks[-1] = cum[-1]

        def when(s):
            """Frame at which distance s is reached."""
            for k in range(1, len(cum)):
                if s <= cum[k] + 1e-9:
                    step = cum[k] - cum[k - 1]
                    return f0 + (k - 1 + ((s - cum[k - 1]) / step if step > 1e-12 else 0.0)) * TICK
            return f0 + (len(cum) - 1) * TICK

        def where(s):
            for i, length in enumerate(seg):
                if s <= marks[i + 1] + 1e-9 or i == len(seg) - 1:
                    return path[i].lerp(path[i + 1], _clamp((s - marks[i]) / length, 0.0, 1.0))
            return path[-1]

        times = [when(m) for m in marks]
        stamps = {round(t, 4): m for t, m in zip(times, marks)}
        for k in range(len(cum)):                       # a key per tick where the speed changes
            a = cum[k] - cum[k - 1] if k else None
            b = cum[k + 1] - cum[k] if k + 1 < len(cum) else None
            if a is None or b is None or abs(a - b) > 1e-7:
                stamps.setdefault(round(f0 + k * TICK, 4), cum[k])
        order = sorted(stamps)
        for i in range(3):
            _segment(self.root, _LOC, i, [(t, where(stamps[t])[i]) for t in order], "LINEAR")
        return times

    def _gait_at(self, frame):
        """(p, s) of the limb cycle the last move keyed at `frame`; None when it has no keys there (or after a cut)."""
        g = self._gait
        if g is None:
            return None
        ps, ss = g["ps"], g["ss"]
        t = (frame - g["f0"]) / TICK
        if t < -1e-6 or t > len(ps) - 1 + 1e-6:
            return None
        k = max(0, min(int(t), len(ps) - 2))
        a = _clamp(t - k, 0.0, 1.0)
        return ps[k] + (ps[k + 1] - ps[k]) * a, ss[k] + (ss[k + 1] - ss[k]) * a

    def _start(self, frame):
        """(start frame, speed carried in) of a move asked for on `frame`. A move asked for on the frame the last
        one returned, while that one ended AT SPEED (ramp out False), starts where its travel really ended (a
        fraction of a frame earlier: ticks are 1.2 frames) with the speed it had, so nothing halts at the join."""
        f0 = int(round(frame))
        g = self._gait
        if g is not None and g["carry"] > 0.0 and -1e-6 <= f0 - g["end"] < 1.0 - 1e-6:
            return g["end"], g["carry"]
        return f0, 0.0

    def _limbs(self, f0, steps, in_stride=False, carry=0.0, tail=14):
        """The walk cycle from per-tick distances (LivingEntity.calculateEntityAnimation + HumanoidModel.setupAnim).
        A move that starts while the last one's cycle is still keyed goes on from that cycle's position and
        speed (no jump in the legs); otherwise it starts at rest, or in full stride with in_stride."""
        state = self._gait_at(f0)
        if state is not None:
            p, s = state
        else:
            p, s = self._phase, (min(4.0 * steps[0], 1.0) if in_stride and steps else 0.0)
        c0 = math.cos(0.6662 * p) * s if state is not None else 0.0     # where the running cycle has the limbs now
        ps, ss = [p], [s]
        for d in list(steps) + [0.0] * tail:
            s += (min(4.0 * d, 1.0) - s) * 0.4
            p += s
            ps.append(p)
            ss.append(s)
        n = int(math.ceil((len(ps) - 1) * TICK - 1e-6))
        keys = {k: [] for k in ("leg_r", "leg_l", "arm_r", "arm_l")}
        base = {side: self._arm_base(side, f0) for side in "rl"}
        half = {side: 0.5 if self._held_at(side, f0) is not None else 1.0 for side in "rl"}
        for j in range(n + 1):
            t = min(j / TICK, len(ps) - 1.0)
            k = min(int(t), len(ps) - 2)
            a = t - k
            pj, sj = ps[k] + (ps[k + 1] - ps[k]) * a, ss[k] + (ss[k + 1] - ss[k]) * a
            c = math.cos(0.6662 * pj) * sj
            keys["leg_r"].append((f0 + j, 1.4 * c, "LINEAR"))
            keys["leg_l"].append((f0 + j, -1.4 * c, "LINEAR"))
            keys["arm_r"].append((f0 + j, base["r"] - c * half["r"], "LINEAR"))
            keys["arm_l"].append((f0 + j, base["l"] + c * half["l"], "LINEAR"))
        for name in ("leg_r", "leg_l"):
            keys[name][-1] = (keys[name][-1][0], 0.0, "LINEAR")
            _segment(self.parts[name], _ROT, 0, keys[name], "LINEAR")
        for side in "rl":
            arm = self._arm(side)
            swung = base[side] + (-1.0 if side == "r" else 1.0) * c0 * half[side]
            if self.still or abs(_val(arm, _ROT, 0, f0) - swung) > 0.2:
                continue                                        # a posed arm keeps its pose
            ks = keys["arm_" + side]
            ks[-1] = (ks[-1][0], base[side], "LINEAR")
            _segment(arm, _ROT, 0, ks, "LINEAR")
        self._gait = dict(f0=f0, ps=ps, ss=ss, end=f0 + len(steps) * TICK, carry=float(carry))
        self._phase = ps[-1]
        return f0 + n

    def walk(self, frame, points, speed=None, run=False, from_current=False, sprint=None, ramp=True):
        """Travel along the polyline `points` with the game's gait (blocks/s: 4.317, sprint 5.612, sneak 1.295); returns the end frame."""
        f0, carry = self._start(frame)
        sprint = run if sprint is None else sprint
        if speed is None:
            speed = SNEAK_SPEED if self.crouching_at(f0) else (SPRINT_SPEED if sprint else WALK_SPEED)
        ramp_in, ramp_out = _ramps(ramp)
        path, teleport = self._path(f0, points, from_current)
        if len(path) < 2:
            return _frame_ceil(f0)
        total = sum((b - a).length for a, b in zip(path, path[1:]))
        v, g = speed / 20.0, GROUND_FRICTION
        steps, acc, d = [], 0.0, (carry / g if ramp_in else v)      # ramp in: from rest, or from the speed carried in
        while len(steps) < 100000:
            d = g * d + (1.0 - g) * v if ramp_in else v
            tail = d * g / (1.0 - g) if ramp_out else 0.0
            if acc + d + tail >= total:
                break
            steps.append(d)
            acc += d
        steps.append(d)
        acc += d
        moving = len(steps)
        while ramp_out and d > 0.004:                           # input released: slide to a halt
            d *= g
            steps.append(d)
            acc += d
        k = total / acc
        steps = [x * k for x in steps]
        cum = [0.0]
        for x in steps:
            cum.append(cum[-1] + x)
        times = self._travel(f0, path, cum)
        self._yaw_keys(f0, path, times, teleport)
        self._limbs(f0, steps, in_stride=not ramp_in, carry=0.0 if ramp_out else steps[moving - 1] * g)
        return _frame_ceil(f0 + (len(cum) - 1) * TICK)

    def sprint_jump(self, frame, points, from_current=False, ramp=True):
        """Bunny-hop along the polyline (12-tick hops 1.25 high, 4.28 blocks each at 7.13 blocks/s); returns the end frame."""
        f0, carry = self._start(frame)
        ramp_in, ramp_out = _ramps(ramp)
        path, teleport = self._path(f0, points, from_current)
        if len(path) < 2:
            return _frame_ceil(f0)
        total = sum((b - a).length for a, b in zip(path, path[1:]))
        g = GROUND_FRICTION
        v = carry if ramp_in else HOP_CARRY                     # ramp in: the first hop from rest (or the speed carried in)
        steps, best = [], None
        while len(steps) < 100000:                              # whole hops: the number that comes closest to the path
            hop, v = _hop(v)
            steps = steps + hop
            reach = sum(steps) + (v / (1.0 - g) if ramp_out else 0.0)
            if best is not None and abs(reach - total) >= abs(best[2] - total):
                break
            best = (steps, v, reach)
            if reach >= total:
                break
        steps, v, _reach = best
        air = len(steps)
        d = v
        while ramp_out and d > 0.004:                           # landed, input released: the slide to a halt
            steps.append(d)
            d *= g
        k = total / sum(steps)
        steps = [x * k for x in steps]
        cum = [0.0]
        for x in steps:
            cum.append(cum[-1] + x)
        times = self._travel(f0, path, cum)
        self._yaw_keys(f0, path, times, teleport, turn=4.0)
        seg = [(b - a).length for a, b in zip(path, path[1:])]

        def ground(s):
            for i, length in enumerate(seg):
                if s <= length or i == len(seg) - 1:
                    return path[i].z + (path[i + 1].z - path[i].z) * _clamp(s / length, 0.0, 1.0)
                s -= length

        zk = [(f0 + i * TICK, ground(cum[i]) + (JUMP_ARC[i % JUMP_TICKS] if i < air else 0.0), "LINEAR")
              for i in range(len(cum))]
        _segment(self.root, _LOC, 2, zk, "LINEAR")
        self._limbs(f0, steps, in_stride=not ramp_in, carry=0.0 if ramp_out else v * k)
        return _frame_ceil(f0 + (len(cum) - 1) * TICK)

    def jump(self, frame):
        """One jump on the spot (1.25 blocks, 12 ticks); returns the landing frame."""
        f0 = int(round(frame))
        z = self.pos_at(f0).z
        _segment(self.root, _LOC, 2, [(f0 + k * TICK, z + y, "LINEAR") for k, y in enumerate(JUMP_ARC)], "LINEAR")
        return int(math.ceil(f0 + JUMP_TICKS * TICK))

    def sneak(self, frame, on=True):
        """The crouch pose from `frame` on (HumanoidModel.setupAnim isCrouching + the renderer's 2 px offset)."""
        if self.crouching_at(frame) == bool(on):
            return frame
        old = {side: self._arm_base(side, frame) for side in "rl"}
        self._crouch = [c for c in self._crouch if c[0] < frame] + [(frame, bool(on))]
        u, k = self.unit, 1.0 if on else 0.0
        _cut(self.torso, _ROT, 0, frame, CROUCH["torso_x"] * k)
        # the head sinks 1 px into the torso, which is exactly as wide: their sides would tie; the torso wins
        _cut(self.head, "scale", 0, frame, CROUCH_HEAD_TIE if on else 1.0)
        for ob, index, delta in ((self.hips, 2, -CROUCH["offset"]), (self.body, 2, -CROUCH["body_down"] * u),
                                 (self.head, 2, -(CROUCH["head_down"] - CROUCH["body_down"]) * u),
                                 (self.leg_l, 1, CROUCH["leg_back"] * u), (self.leg_r, 1, CROUCH["leg_back"] * u)):
            _cut(ob, _LOC, index, frame, self._rest(ob, _LOC, index) + delta * k)
        for side in "rl":
            self._rebase(side, frame, old[side])
        return frame

    # ------------------------------------------------------------------ arm swings (engine.fx plays the game's rule)
    def attack(self, frame, hand="right"):
        """One arm swing requested on `frame` (hit, use, place, throw): 6 ticks, highest after 2.4 frames."""
        from . import fx

        if _side(hand) == "l":
            self._swing_left([frame])
        else:
            fx.arm_swings(self, [frame])
        return int(math.ceil(frame + 6 * TICK + 1))

    swing = attack

    def _swing_left(self, frames):
        """engine.fx.arm_swings for the LEFT arm (HumanoidModel.setupAttackAnimation with attackArm LEFT: the body
        turns the other way, the left arm takes the swing; its zRot term is NOT mirrored in the game). One run of
        swings by the game's rule (fx._swing_run), absolute LINEAR keys back to the pose at the first request."""
        from . import fx

        reqs = sorted(float(f) for f in frames)
        f0 = reqs[0]
        _starts, shown, _end = fx._swing_run([int(round((f - f0) / TICK)) for f in reqs])
        while len(shown) > 1 and shown[-1][0] in (0.0, 1.0) and shown[-1][1] in (0.0, 1.0):
            shown.pop()
        # (object, euler index, pose terms -> offset): rig x = xRot, rig z = -yRot, rig y = zRot
        chans = ((self.body, 2, lambda b, x, y, z: b),          # body.yRot = -turn
                 (self.head, 2, lambda b, x, y, z: -b),         # the head stays where it looks
                 (self.arm_l, 0, lambda b, x, y, z: x - b),     # leftArm.xRot += body.yRot, then -= g * 1.2 + h
                 (self.arm_l, 2, lambda b, x, y, z: y),         # leftArm.yRot += body.yRot * 2
                 (self.arm_l, 1, lambda b, x, y, z: z))         # leftArm.zRot += sin(t * pi) * -0.4
        rest = [_val(ob, _ROT, index, f0) for ob, index, _fn in chans]
        times, poses = [], []
        for k, (a, b) in enumerate(shown):
            for j in range(fx._SWING_KEYS):
                u = j / float(fx._SWING_KEYS)
                f = f0 + (k + u) * TICK
                times.append(f)
                poses.append(fx._swing_pose(a + (b - a) * u, _val(self.head, _ROT, 0, f)))
        f_end = f0 + len(shown) * TICK
        for (ob, index, fn), r in zip(chans, rest):
            keys = [(times[0], None)]
            for f, pose in zip(times[1:], poses[1:]):
                keys.append((f, _clamp(r + fn(*pose), -fx._SWING_LIMIT, fx._SWING_LIMIT)))
            keys.append((f_end, r))
            _segment(ob, _ROT, index, keys, "LINEAR")
        return f_end

    def mine(self, frame_start, frame_end):
        """The mining swing held from frame_start to frame_end (a new swing every 4 ticks)."""
        from . import fx

        return fx.mining_swings(self, frame_start, frame_end)

    # ------------------------------------------------------------------ use poses
    def _head(self, frame):
        """(pitch, yaw) of the head in the game's signs (xRot positive = down, yRot = -rig z)."""
        return _val(self.head, _ROT, 0, frame), -_val(self.head, _ROT, 2, frame)

    def _pose_arm(self, side, f0, f1, fn, ease=3, crouch=True):
        """Hold an arm in a head-following pose on [f0, f1]: fn(pitch, yaw, frame) -> (xRot, yRot) in game terms.
        crouch: add the 0.4 rad that HumanoidModel.setupAnim gives both arms AFTER their pose while sneaking."""
        arm = self._arm(side)
        f0, f1 = int(f0), int(f1)
        back_x = self._arm_base(side, f1 + ease)
        xk, zk = [(f0, None, "SMOOTH")], [(f0, None, "SMOOTH")]

        def low(f):
            return CROUCH["arm_x"] if crouch and self.crouching_at(f) else 0.0

        for f in range(f0 + ease, f1 + 1):
            x, y = fn(*self._head(f), f)
            xk.append((f, x + low(f), "LINEAR"))
            zk.append((f, -y, "LINEAR"))
        if ease == 0:
            x, y = fn(*self._head(f0), f0)
            _cut(arm, _ROT, 0, f0, x + low(f0))
            _cut(arm, _ROT, 2, f0, -y)
            xk, zk = xk[1:], zk[1:]
            xk.append((f1 + 1 - CUT_LEAD, back_x))
            zk.append((f1 + 1 - CUT_LEAD, 0.0))
        else:
            xk[-1] = xk[-1][:2] + ("SMOOTH",)
            zk[-1] = zk[-1][:2] + ("SMOOTH",)
            xk.append((f1 + ease, back_x))
            zk.append((f1 + ease, 0.0))
        if len(xk) > 1:
            _segment(arm, _ROT, 0, xk, "LINEAR")
            _segment(arm, _ROT, 2, zk, "LINEAR")
        return f1 + ease

    def block(self, frame_start, frame_end, hand="left", ease=3):
        """Raise the shield of `hand` from frame_start to frame_end (ArmPose BLOCK, shield_blocking model)."""
        side = _side(hand)
        sgn = -1.0 if side == "r" else 1.0

        def fn(pitch, yaw, _f):                                 # poseBlockingArm: walk swing * 0.5 - 0.9424779 + ...
            return (-0.9424779 + _clamp(pitch, -1.3962634, 0.43633232),       # (the swing of a held pose is 0 here)
                    sgn * math.radians(30.0) + _clamp(yaw, -math.pi / 6, math.pi / 6))

        if self.holding_at(side, frame_start) == "shield":
            self._use_variant(side, "shield_blocking", frame_start + ease, frame_end + 1)
        return self._pose_arm(side, frame_start, frame_end, fn, ease)

    def draw_bow(self, frame_start, frame_end, hand="right", ease=3):
        """Draw the bow of `hand` from frame_start, loose the arrow ON frame_end; returns dict(frame, origin, direction)."""
        side = _side(hand)
        other = "l" if side == "r" else "r"
        sgn = 1.0 if side == "r" else -1.0
        self._pose_arm(side, frame_start, frame_end, lambda p, y, _f: (-math.pi / 2 + p, -0.1 * sgn + y), ease)
        self._pose_arm(other, frame_start, frame_end, lambda p, y, _f: (-math.pi / 2 + p, 0.5 * sgn + y), ease)
        if self.holding_at(side, frame_start) == "bow":
            f0 = int(frame_start) + ease
            marks = [f0, f0 + int(round(13 * TICK)), f0 + int(round(18 * TICK)), int(frame_end)]
            for i, name in enumerate(("bow_pulling_0", "bow_pulling_1", "bow_pulling_2")):
                if marks[i] < marks[i + 1] and marks[i] < frame_end:
                    self._use_variant(side, name, marks[i], min(marks[i + 1], int(frame_end)))
        return dict(frame=int(frame_end), origin=self.eye_point(frame_end) - Vector((0.0, 0.0, 0.1)),
                    direction=self.look_vector(frame_end))

    def toot(self, frame_start, frame_end, hand="right", ease=3):
        """Hold the goat horn of `hand` to the mouth from frame_start to frame_end (ArmPose TOOT_HORN)."""
        side = _side(hand)
        sgn = -1.0 if side == "r" else 1.0
        if self.holding_at(side, frame_start) == "goat_horn":
            self._use_variant(side, "tooting_goat_horn", frame_start + ease, frame_end + 1)
        return self._pose_arm(side, frame_start, frame_end,
                              lambda p, y, _f: (_clamp(p, -1.2, 1.2) - 1.4835298, y + sgn * 0.5235988), ease)

    def eat(self, frame_start, frame_end=None, hand="right", ease=4):
        """Bring the hand's item to the mouth and bob it every 4 ticks (a film gesture: see the module docstring)."""
        side = _side(hand)
        sgn = -1.0 if side == "r" else 1.0
        f0 = int(frame_start)
        f1 = int(frame_end) if frame_end is not None else int(round(f0 + EAT_TICKS * TICK)) - ease
        span = max(1.0, f1 + ease - f0)

        def fn(pitch, yaw, f):
            done = (f - f0) / span
            bob = abs(math.cos((f - f0) / TICK / 4.0 * math.pi)) * 0.16 if done > 0.2 else 0.0
            return (-1.75 + 0.5 * pitch - bob, yaw + sgn * 0.52)

        return self._pose_arm(side, f0, f1, fn, ease, crouch=False)    # the hand goes to the mouth, crouching or not

    drink = eat

    def look_vector(self, frame):
        """Unit vector along the head's look at `frame`."""
        pitch, yaw = self._head(frame)
        a = self.yaw_at(frame) - yaw
        return Vector((math.sin(a) * math.cos(pitch), -math.cos(a) * math.cos(pitch), -math.sin(pitch)))

    def throw(self, frame, hand="right", kind="ender_pearl"):
        """Throw with an arm swing; returns where the projectile leaves on `frame` (it is another module's to draw)."""
        self.attack(frame, hand)
        d = self.look_vector(frame)
        speed = 1.5
        if "potion" in kind:                                    # ThrowablePotionItem: 0.5 blocks per tick, pitched -20
            speed = 0.5
            flat = math.hypot(d.x, d.y)
            pitch = math.atan2(d.z, flat) + math.radians(20.0)
            d = Vector((d.x / max(flat, 1e-9) * math.cos(pitch), d.y / max(flat, 1e-9) * math.cos(pitch), math.sin(pitch)))
        return dict(frame=int(frame), origin=self.eye_point(frame) - Vector((0.0, 0.0, 0.1)), direction=d,
                    speed=speed, hand=self.item_point(hand, frame))

    # ------------------------------------------------------------------ hurt and death
    def _red_at(self, frame):
        """True while the red hurt / death overlay is on at `frame`."""
        return any(a <= frame and (b is None or frame < b) for a, b in self._red)

    def _flash(self, frame_start, frame_end):
        """The red hurt overlay on the skin from frame_start to frame_end (None = for good)."""
        self._red.append((int(frame_start), None if frame_end is None else int(frame_end)))
        self._write_red()

    def _write_red(self):
        """Rewrite the overlay keys from the spans in self._red (their union: a death that starts inside a hurt
        flash, or a blow that lands on the dying, never switches the red off early)."""
        marks = sorted({a for a, _b in self._red} | {b for _a, b in self._red if b is not None})
        # engine.stamp does not hash Object.color; it does hash matrices. The torso is 0.03 % larger while the
        # overlay is on (0.2 mm), so that a frame's fingerprint changes with the flash and render.py re-renders it.
        curves = [(ob, "color", 3, 1.0, 0.0) for ob in self.meshes] + [(self.torso, "scale", i, 1.0, 1.0003) for i in range(3)]
        for ob, path, index, off, on in curves:
            fc = _find(ob, path, index)
            if fc is None and not marks:
                continue
            fc = _ensure(ob, path, index)
            fc.keyframe_points.clear()
            if marks:
                _put(fc, min(marks[0], 1) - 1, off, "CONSTANT")
                for f in marks:
                    _put(fc, f, on if self._red_at(f) else off, "CONSTANT")
            else:
                getattr(ob, path)[index] = off
            fc.update()

    def hurt(self, frame, from_point=None, knockback=0.4):
        """Red flash for 10 ticks and (with from_point) the game's knock-back away from it; returns the end frame."""
        f0 = int(round(frame))
        end = f0 + int(round(HURT_TICKS * TICK))
        self._flash(f0, end)
        if from_point is None or knockback <= 0:
            return end
        here = self.pos_at(f0)
        d = here - self._point(from_point, f0)
        d.z = 0.0
        if d.length < 1e-6:
            d = Vector((math.sin(self.yaw_at(f0)), -math.cos(self.yaw_at(f0)), 0.0)) * -1.0
        d.normalize()
        x = y = 0.0
        vh, vy, air = float(knockback), min(0.4, -0.0784 / 2.0 + knockback), False
        keys = [(f0, 0.0, 0.0)]
        for k in range(1, 60):
            x += vh
            y += vy
            vh *= 0.91 if air else GROUND_FRICTION
            vy = (vy - GRAVITY) * 0.98
            air = y > 0.0
            if not air:
                y, vy = 0.0, -0.0784
            keys.append((f0 + k * TICK, x, y))
            if not air and vh < 0.003:
                break
        for i in range(3):
            ks = [(f, here[i] + d[i] * x + (y if i == 2 else 0.0), "LINEAR") for f, x, y in keys]
            _segment(self.root, _LOC, i, ks, "LINEAR")
        return max(end, int(math.ceil(keys[-1][0])))

    def _halt(self, f0):
        """A move still running at f0 ends there: the root stays where it is and the limbs hang straight
        (LivingEntityRenderer.extractRenderState: the walk animation of a dead entity is 0)."""
        state = self._gait_at(f0)
        if state is None:
            return
        g = self._gait
        if f0 < g["end"] - 1e-6:
            for i in range(3):
                _segment(self.root, _LOC, i, [(f0, None)])
            _segment(self.root, _ROT, 2, [(f0, None)])
        c0 = math.cos(0.6662 * state[0]) * state[1]
        for side in "rl":
            arm, base = self._arm(side), self._arm_base(side, f0)
            half = 0.5 if self._held_at(side, f0) is not None else 1.0
            if abs(_val(arm, _ROT, 0, f0) - (base + (-1.0 if side == "r" else 1.0) * c0 * half)) <= 0.2:
                _cut(arm, _ROT, 0, f0, base)                    # it was swinging with the walk, not posed
        for leg in (self.leg_r, self.leg_l):
            _cut(leg, _ROT, 0, f0, 0.0)
        self._gait = None

    def die(self, frame, from_point=None, knockback=0.4, poof=True, camera=None, seed=0, village=None):
        """Die on `frame`: red, tipping onto the left side, gone 20 ticks later. from_point = where the killing blow
        comes from (its knock-back, as hurt()). camera = the Shot / Film / camera object: the 20 white poof
        particles are then drawn by engine.animals.poof. Returns dict(frame, feet, size, point, poof, burst)."""
        f0 = int(round(frame))
        gone = f0 + int(round(DEATH_TICKS * TICK))
        self._halt(f0)
        if from_point is not None:
            self.hurt(f0, from_point, knockback)                # the killing blow knocks him back like any other
        self._flash(f0, None)
        keys = [(f0, None, "LINEAR")]
        f = f0 + TICK
        while f < gone:                                         # LivingEntityRenderer.setupRotations
            t = (f - f0) / TICK
            keys.append((f, math.radians(90.0) * min(1.0, math.sqrt(max(0.0, (t - 1.0) / 20.0 * 1.6))), "LINEAR"))
            f += 0.3 if t < 3.0 else 1.0
        keys.append((gone, math.radians(90.0)))
        _segment(self.root, _ROT, 1, keys, "LINEAR")
        self.show(gone, False)
        yaw, feet = self.yaw_at(gone), self.pos_at(gone)
        left = Vector((math.cos(yaw), math.sin(yaw), 0.0))      # the character's left: where the body comes to lie
        info = dict(frame=gone, feet=feet, size=self.size, point=feet + left * 0.9 + Vector((0.0, 0.0, 0.3)),
                    poof=poof, burst=None)
        if poof and camera is not None:                         # LivingEntity.makePoofParticles, around the hit box
            from . import animals

            info["burst"] = animals.poof(feet, gone, camera=camera, seed=seed, village=village, size=self.size)
        return info

    def revive(self, frame):
        """End the hurt / death colouring from `frame` on (place() calls it and stands the body up)."""
        f = int(frame)
        self._red = [(a, f if (b is None or b > f) else b) for a, b in self._red if a < f]
        self._write_red()

    # ------------------------------------------------------------------ idle, stillness, the stare
    def idle(self, frame_start, frame_end, seed=None):
        """Alive while waiting (Character.idle with this player's own seed); nothing at all while .still is True."""
        if self.still:
            return
        super().idle(frame_start, frame_end, self.idle_seed if seed is None else seed)

    def watch(self, frame_start, frame_end, target, step=2, body=False, ease=8, snap=None):
        """Keep the head on a (moving) target for the whole span; body=True also turns the figure on the spot.
        snap: the head is ON the target on frame_start itself (a hard cut) instead of turning to it over `ease`
        frames. Default None = snap when the player was placed on frame_start (the first frame of his shot)."""
        f0, f1 = int(frame_start), int(frame_end)
        if snap is None:
            snap = ch._cut_at(self.root, _LOC, 0, f0)
        if body:
            pos = self.pos_at(f0)
            yaw = self.yaw_at(f0)

            def turned(f, yaw):
                """Body yaw that leaves the target within reach of the head (it turns only as far as it must)."""
                d = self._point(target, f) - pos
                want = yaw + _wrap(math.atan2(d.x, -d.y) - yaw)
                if abs(want - yaw) > HEAD_YAW_MAX * 0.8:
                    yaw = want - math.copysign(HEAD_YAW_MAX * 0.8, want - yaw)
                return yaw

            if snap:
                yaw = turned(f0, yaw)
                _cut(self.root, _ROT, 2, f0, yaw, hold_rest=False)
            yk = [(f0, None)]
            for f in list(range(f0 + (max(1, int(step) * 3) if snap else ease), f1, max(1, int(step) * 3))) + [f1]:
                yaw = turned(f, yaw)
                yk.append((f, yaw))
            _segment(self.root, _ROT, 2, yk, "BEZIER")
        if snap:
            self.look_at(f0, target, ease=0)
        return self.track(f0, f1, target, step=step, ease=max(1, int(step)) if snap else ease)


def _side(hand):
    return "l" if str(hand).lower().startswith("l") else "r"


# ----------------------------------------------------------------------------------------------------
# factories
# ----------------------------------------------------------------------------------------------------
def make_player(name="player", skin="steve", slim=None, glow=None, collection=None):
    """Build a player (feet at the origin, facing -Y) in one of the nine default skins, or as 'herobrine'."""
    skin = skin.lower()
    if slim is None:
        slim = skin in SLIM_BY_DEFAULT
    key, sheet, mask = skin_sheet(skin, slim)
    if glow is None:
        glow = HEROBRINE_GLOW if skin == "herobrine" else 0.0
    spec = _player_spec(slim)
    col = ch._collection(collection)
    parts = ch._build_rig(name, spec, sheet, _skin_material(key, sheet, mask, glow), col)
    # The torso is exactly as deep as the arms, and the arms rest 0.05 rad splayed: a sliver of each arm's front
    # and back lies IN the torso's front and back plane (a depth tie). The torso is drawn 0.4 % deeper (0.008 px)
    # and wins it. (The jacket overlay moves with it to 2.259 px; the sleeves stay at 2.27.)
    for v in parts["torso"].data.vertices:
        v.co.y *= TORSO_TIE
    p = Player(name, parts, spec, skin, slim, col)
    if skin == "herobrine":
        p.still = True
        for arm in (p.arm_r, p.arm_l):
            p._set_rest(arm, _ROT, 1, 0.0)
    return p


def add_player(st, name, skin="steve", **kw):
    """A player registered with a films.lookdev.Stage (built on first use), like poppy_common.add_golem."""
    p = st.cast.get(name)
    if p is None:
        p = st.cast[name] = make_player(name, skin, **kw)
    return p


TOWN_ITEMS = (None, "iron_pickaxe", None, "torch", "bucket", None, "iron_axe", "cooked_chicken", None, "stone_hoe",
              "iron_shovel", None, "bow", "emerald")


def cast_town(st, count=6, seed=0, skins=None, items=True, names=None):
    """`count` different players for a town of players: distinct skins, own idle seeds, an item in some hands."""
    r = pix.rng(9001 + int(seed))
    order = list(skins) if skins else [SKINS[i] for i in r.permutation(len(SKINS))]
    picks = [TOWN_ITEMS[i] for i in r.permutation(len(TOWN_ITEMS))]
    out = []
    for i in range(count):
        skin = order[i % len(order)]
        name = names[i] if names else "%s%s" % (skin, "" if i < len(order) else str(i // len(order) + 1))
        other = st.cast.get(name) if st is not None else None
        if other is not None and not isinstance(other, Player):
            if names:                                           # an explicit name that is somebody else: say so
                raise ValueError("cast_town: %r is already in the cast and is not a players.Player (%r)" % (name, other))
            name = "player_" + name                             # st.actor("steve", "steve") is the old characters Steve
        fresh = (st.cast.get(name) if st is not None else None) is None
        p = add_player(st, name, skin, slim=(None if i < len(order) else skin not in SLIM_BY_DEFAULT)) \
            if st is not None else make_player(name, skin)
        if fresh:
            p.idle_seed = int(r.integers(0, 1000))
            if items and picks[i % len(picks)]:
                p.hold(picks[i % len(picks)])
        out.append(p)
    return out


_KEEP = object()


def equip(player, material=None, helmet=_KEEP, chestplate=_KEEP, leggings=_KEEP, boots=_KEEP, enchanted=False,
          frame=None, glint_strength=1.5):
    """Armor on a Player: equip(p, "diamond") = full set, equip(p, boots="golden") = one piece, piece=None = off.
    glint_strength scales the game's glint alpha for enchanted=True (1.0 = the game's own, faint; 2.0 = strong)."""
    want = dict(helmet=helmet, chestplate=chestplate, leggings=leggings, boots=boots)
    made = []
    for slot in ARMOR_SLOTS:
        m = want[slot]
        if m is _KEEP:
            if material is None:
                continue
            m = material
        if m in (None, False, "none", ""):
            m = None
        elif _ARMOR_TEXTURE.get(m, m) not in ("leather", "chainmail", "iron", "gold", "diamond", "netherite", "copper",
                                             "turtle_scute"):
            raise ValueError("unknown armor material %r (use one of %s)" % (m, ", ".join(ARMOR_MATERIALS)))
        elif slot not in ARMOR_PIECES.get(_ARMOR_TEXTURE.get(m, m), ARMOR_SLOTS):
            if want[slot] is _KEEP:
                continue                                        # equip(p, "turtle_scute"): the set is its helmet
            raise ValueError("there is no %s %s in the game (%s is only a %s)" % (
                m, slot, m, " / ".join(ARMOR_PIECES[_ARMOR_TEXTURE.get(m, m)])))
        for _f, _m, atts in player._armor[slot]:                # whatever was worn in this slot goes
            for att in atts:
                if att.steps[-1][1]:
                    att.set(frame, False)
        atts = []
        if m is not None:
            key, sheet = armor_sheet(m, leggings=slot == "leggings")
            mat = _armor_material(key, sheet)
            u = player.unit
            for part, cubes, clip in _armor_parts(slot):
                me = _box_mesh("%s_%s_%s" % (player.name, slot, part), cubes, sheet,
                               lambda p: Vector((p[0], p[2], -p[1])) * u, mat, clip, clip_scale=u)
                ob = bpy.data.objects.new(me.name, me)
                atts.append(player._attach(ob, part, on=frame))
                if enchanted:
                    _armor_glint(ob, strength=glint_strength)
                made.append(ob)
        player._armor[slot].append((frame, m, atts))
    player._refresh()
    return made


def _selftest(argv):
    from tools import players_proof

    return players_proof.main(argv)


if __name__ == "__main__":
    sys.exit(_selftest(sys.argv[1:]))
