"""The vanilla IRON GOLEM and DROPPED ITEMS (item entities), for the film "Poppy". New module; edits no other file.

Everything is transcribed from the Java Edition 26.x client classes (named next to each number below) and drawn with
the game's own textures through engine.mcassets. Blender axes as everywhere: +X east, +Y north, +Z up, 1 block = 1
unit, characters face -Y at yaw 0, 24 fps (the game runs 20 ticks per second: 1 tick = 1.2 frames).

PUBLIC API
    make_iron_golem(name="golem", collection=None, crack=None) -> IronGolem
        The golem, box for box (IronGolemModel.createBodyLayer, 128x128 entity/iron_golem/iron_golem.png, vines and
        all). 2.6875 tall (head top), 1.625 wide over the arms, body 1.125 wide; the game's hit box is 1.4 x 2.7.
    IronGolem (a subclass of engine.characters.Character: root / hips / body / head / arm_l / arm_r / leg_l / leg_r)
        place(frame, pos, yaw=0.0)             hard cut to a spot, neutral pose, flower gone (use at shot cuts)
        show(frame, visible=True)              keyed visibility of the rig (the poppy only shows while offered)
        walk(frame, points, speed=None, run=False, from_current=False, gait="planted", swing=None, ramp=8,
             corner=1.0) -> end frame          the golem gait: legs and opposite arms on the game's triangle wave,
                                               the +-6.5 degree side-to-side roll of IronGolemRenderer; default
                                               speed WALK_SPEED = 0.99 blocks/s (run=True: CHASE_SPEED 2.23).
                                               gait="planted" (default): feet do not slide; gait="vanilla": the
                                               game's exact amplitudes and period (its feet slide, see GAIT below).
                                               ramp = frames of acceleration and of braking, or (start, end):
                                               ramp=(0, 8) is in full stride on its first frame.
                                               corner = radius of the arc that rounds every corner of `points`
                                               (see CORNERS below); corner=0 = sharp vertices, turned on the spot
        look_at(frame, target, ease=6)         head toward a point / Character / Object, clamped to the game's
        track(f0, f1, target)                  75 degrees of yaw and 40 of pitch (Mob.getMaxHeadYRot / XRot)
        face(frame, target, ease=8) / turn(frame, yaw, ease=8)     turn the whole body (on the spot)
        idle(frame_start, frame_end, seed=0)   slow head turns only (a golem at rest moves nothing else)
        offer_flower(frame, on=True, ease=8, ticks=400, grow=None) -> end frame
                                               the game's offer pose: right arm to -0.8 rad with the +-0.025 rad
                                               wobble (period 70 ticks), left arm straight down, and the POPPY in
                                               the hand exactly as IronGolemFlowerLayer draws it (the real block
                                               model at half size, pointing forward out of the fist). on=False lowers
                                               the arm. ease=0 = the game's snap: arm and poppy are simply there on
                                               `frame` (use it right after place() when a shot opens on the pose).
                                               With an eased raise the poppy grows out of the fist during its first
                                               `grow` frames (4), with an eased lowering it rides the arm down and
                                               shrinks back into the fist during the last 4: nothing pops on screen
        step_crumbs(frame_start, frame_end, camera, village=None, block="dirt_path", seed=0, glow=0.0) -> fx Burst
                                               the crumbs of the ground a MOVING golem kicks up in the game (about
                                               four a second, see CRUMBS below). Call it after the walk is keyed;
                                               camera = the Shot (or camera object, or Film) that films it
        attack(frame) / swing_arm(frame)       both arms thrown up and back down (10 ticks), the game's attack
        crack(level)                           None | "low" | "medium" | "high": the crackiness overlay textures
        flower                                 the poppy Object (child of arm_r; origin = base of its stem): a good
                                               focus / hero target. flower_point(frame) = world position of the bloom
        offering_at(frame) / flower_at(frame)  is the offer pose on / is the poppy there at `frame`
        hold(obj)                              any other object in the fist, where the poppy sits; hold(None)
        last_walk                              dict of the last walk(): frames, blocks, speed, swing, cycle_frames,
                                               corners [(radius, degrees)], sharp [degrees], path [(x, y, z) ...]
        nod / shake / flinch / shiver / raise_arm / lie_down / pos_at / yaw_at / eye_point: inherited, unchanged
    make_dropped_item(item_id, collection=None, count=1, seed=0, name=None) -> DroppedItem
        An item entity as ItemEntityRenderer draws it. "poppy", "iron_ingot", "emerald" ...: the item's flat sprite
        (the same extruded sprite engine.props.make_item builds) at the 'ground' display transform of
        models/item/generated.json (half size, standing UPRIGHT, never lying flat); block items ("iron_block") are
        the block model at quarter size. count = stack size (the game draws 1 copy for 1, 2 for 2-16, 3 for 17-32 ...).
    DroppedItem
        place(frame, pos, age=40.0)            resting at ground point `pos` from `frame` on (hard cut)
        drop(frame, pos, velocity=None, seed=None, rest=False) -> landing frame
                                               spawned at `pos` at `frame` with the game's little toss (0.2 blocks
                                               per tick up, up to 0.1 sideways: hops 0.38 high, lands after 9 ticks);
                                               rest=True makes `pos` the spot where it comes to REST instead
        animate(frame_start, frame_end, phase=None)
                                               the game's bob (0 to 0.2 blocks, period 62.8 ticks = 75.4 frames) and
                                               spin (1 radian per second, one turn in 6.28 s = 151 frames)
        face(frame, target)                    choose the phase so the sprite shows its flat side to `target` (a
                                               camera position) at `frame`; call it BEFORE animate()
        pick_up(frame)                         gone from `frame` on (a later drop() brings it back)
        show(frame, visible=True)              keyed visibility (never visible before its first drop()); .root is
                                               the Empty at the entity position (on the ground), .sprite the first
                                               copy (focus / hero target), .name, .rest_pos (where it lies still)
        age_at(frame)                          every place() / drop() is a new entity whose age (bob, spin) counts
                                               from its own frame, in whatever order the shots are keyed
    clearance(village, points, width=1.4, height=2.7, step=0.25) -> list of hits
        Where a box of the golem's size, moved along a polyline, would touch a block of the set (empty = it fits).
    rounded(points, radius=1.0, step=0.25) -> points
        The line walk(points) really follows, corners cut by its arcs: clearance(village, mobs.rounded(points)).
    Constants: WALK_SPEED, CHASE_SPEED, GOLEM_HEIGHT, GOLEM_WIDTH, MODEL_HEIGHT, MODEL_WIDTH, OFFER_ARM_PITCH,
    CORNER_RADIUS.

USING THEM IN A FILM (films.lookdev.Stage)
    golem = mobs.make_iron_golem("golem"); st.cast["golem"] = golem      # so Stage.finish() hides it outside its shots
    st.use(shot, golem); st.hero(shot, "golem", golem)                   # hero = its head
    poppy = mobs.make_dropped_item("poppy"); st.cast[poppy.name] = poppy; st.use(shot, poppy)
    st.hero(shot, "poppy", poppy.sprite)
    Call place() before anything else in a shot, then offer_flower(f, ease=0) / look_at(f, kid, ease=0).
    KEY A GOLEM IN FRAME ORDER, shot after shot, like every Character: a later call replaces the keys after its
    frame. walk() refuses (ValueError naming the frame) to run through an offer_flower() that was keyed before it
    for a later frame: it would leave the poppy in a swinging fist. Walk first, then offer_flower() DURING the
    walk: the arms then hold the pose while the legs go on (and after offer_flower(on=False) they hang still until
    the next walk()). DroppedItem.drop() refuses the same way to toss through a place() / drop() / pick_up()
    already keyed for a frame of its toss.
    A walk that opens a shot in stride: either pre-roll it (place() and walk() 20+ frames before the cut), which
    is only possible when the golem is NOT in the shot before (its place() would cut that shot short: use a second
    make_iron_golem for one of the two shots), or start it on the cut with ramp=(0, 8).
    Crumbs: burst = golem.step_crumbs(s.frame_start, s.frame_end + 1, camera=s, village=v) after the walk of shot s.
    They belong to the shot they are made for: none is left on frame_end, and they need no entry in st.cast.

GAIT (IronGolemModel.setupAnim + IronGolemRenderer.setupRotations + LivingEntity.updateWalkAnimation)
    The game: wave(p) = Mth.triangleWave(p, 13); right leg -1.5 * wave * s, left leg +1.5 * wave * s, right arm
    (-0.2 + 1.5 * wave) * s, left arm (-0.2 - 1.5 * wave) * s, body roll 6.5 degrees * triangleWave(p + 6, 13) about
    the feet, where s = min(4 * blocks moved per tick, 1) and p grows by s every tick. So one leg cycle is ALWAYS
    3.25 blocks of travel and the swing grows with speed. A strolling golem (speed attribute 0.25 x goal modifier
    0.6, squared, over 1 - 0.546 friction = 0.0496 blocks per tick = 0.99 blocks/s) has s = 0.198: legs and arms
    swing +-17 degrees once every 3.28 s while it covers 3.25 blocks, i.e. its feet SLIDE 1.15 blocks per step. The
    game's feet only stop sliding at s = 1 (5 blocks/s, +-86 degrees), a speed no golem reaches.
    gait="vanilla" reproduces exactly that (use it for wide shots, or when the feet are out of frame).
    gait="planted" keeps the game's wave shape, roll, arm formula and walking speed, but opens the legs to `swing`
    (default 0.5 rad = 28.6 degrees; 0.75 with run=True) and shortens the cycle to 4 * leg * sin(swing) blocks
    (1.56 blocks, 1.57 s at 0.99 blocks/s: one heavy step every 0.79 s) so that the foot on the ground stays where
    it was put (along the walk: 0.0003 block per step; the wave is bent by at most 0.4 degrees for that). The arms
    keep the game's own swing for the speed (+-17 degrees at a stroll). That, and the rounded corners, are the only
    departures from the game in this module. Neither gait moves the hips up and down: the game has no bob, the
    roll is its whole "weight" (the roll alone moves a planted sole 0.02 block sideways and 0.03 up and down).

CORNERS (this module's choice; the game turns a mob on the spot while it slides on)
    walk() rounds each corner of its polyline with an arc of radius `corner` (1 block): the body follows the
    tangent, so a 90 degree turn takes 1.57 blocks = two steps. In the planted gait the inner foot takes a shorter
    step than the outer one (72 % / 128 % of a straight step on a 1-block arc) and the body pivots over the foot
    that carries it, so the planted sole only turns on the spot: measured, its centre strays 0.037 block round a
    right angle (0.022 on a straight; 0.40 before the corners were rounded; 0.02-0.05 on the village's own paths).
    The line cuts a right-angle corner by 0.41 block on the inside and the body sways up to 0.1 block off it
    (0.06 at one right angle): check clearance(v, mobs.rounded(points)), or last_walk["path"] afterwards. The walk
    is 0.43 block shorter per right angle than its polyline.
    A corner whose legs are too short for the radius gets a tighter arc; a U-turn, a leg too short for an arc of
    0.08 block, or corner=0 leave a sharp vertex, turned on the spot over 10 frames: there, in turn() / face(),
    and when a walk starts facing another way than its first leg (it turns into it while setting off), the
    planted feet DO skate (0.29 block for a right angle). Keep those out of foot-level shots or cut on the turn;
    start walks with place(frame, pos, yaw) facing the way they go.

CRUMBS (Entity.baseTick -> IronGolem.canSpawnSprintParticle, Entity.spawnSprintParticle, TerrainParticle)
    A golem that moves (horizontal speed squared over 2.5e-7 per tick) spawns, on one tick in five, ONE block
    particle of the block 0.2 under its feet: anywhere in its 1.4 x 1.4 footprint, 0.1 above its feet, thrown up
    with velocity argument (-4 vx, 1.5, -4 vz). That is about four crumbs a second, two in the air on average
    (0 to 4, now and then more): dark squares 0.1-0.2 block wide showing a quarter of the block's particle texture
    at 0.6 of its colour (a dirt path: block/dirt_path_side; a grass block: plain dirt, not tinted green), hopping
    0.3-0.7 block (median 0.46) and gone after 4-40 ticks (median 7 = 0.35 s). A standing golem makes none.
    step_crumbs() spawns exactly that from the keyed motion and draws it with engine.fx's terrain particles
    (camera-facing quads that take the light of the set: in the golem's own shadow they are nearly black, under a
    lamp at night they are faint; glow=0.2 lifts them if they must read). seed picks another draw. Nothing calls
    it for you: a walk without step_crumbs() has no crumbs. (Not transcribed: the game clamps a crumb's start into
    the supporting block's column when the golem straddles two blocks.)

FLOWER (IronGolemFlowerLayer.submit, IronGolemRenderer.extractRenderState)
    Blocks.POPPY's block model (the cross of two planes, block/poppy) drawn with: right arm pose, translate(-1.1875,
    1.0625, -0.9375), translate(0.5), scale(0.5), rotate X -90 degrees, translate(-0.5). In arm pixels that puts
    the stem's base at (-11, 25, -3): the middle of the fist's FRONT face, 2.5 px above the end of the arm, and the
    half-size flower points straight out of the arm's front. With the arm at -0.8 rad it points forward and up at 45
    degrees: stem base 0.97 above the ground, 1.24 in front of the golem's centre and 0.69 to its right; the bloom
    1.16 high and 1.43 in front. A baby villager is 1.0 tall with its eyes at 0.66: stand the child 2.1-2.6 blocks
    in front of the golem (0.6 to the golem's right), let it look_at(golem.flower_point(frame)) and the golem
    look_at(child): the proof stills out/test/mobs_offer_1/2.png use (-0.62, -2.15) for a golem at the origin.
    In the game the golem only offers by day (OfferFlowerGoal.canUse: isBrightOutside), for 400 ticks = 20 s, to a
    villager child within 6 blocks, looking at it (LookControl, 30 degrees per tick), and the arm SNAPS up and
    down with the flower (ease=0). An eased raise is a film choice: with the arm hanging, the poppy sprouts
    forward out of the fist at shin height (stem base 0.375 above the ground, 0.19 in front of the golem's centre)
    and is full size after 4 frames, while the arm has only begun to lift (out/test/mobs_raise_sheet.png,
    mobs_lower_sheet.png). flower_point() is where the bloom is (or will be) for the arm's pose at that frame,
    whether the poppy is grown or not: aim a child's look at golem.flower_point(end frame of the raise).

DROPPED ITEMS (ItemEntityRenderer.submit, ItemEntity.getSpin / tick, ItemTransform.apply, ItemModelGenerator)
    height of the sprite's CENTRE above the ground = 0.3125 + 0.1 + 0.1 * sin(age / 10 + phase) (age in ticks):
    its lower edge floats 1 to 4.2 pixels above the ground; rotation about the vertical = age / 20 + phase radians.
    A dropped flower or ingot never lies down in Java Edition. The iron golem's loot table drops 0-2 poppies and
    3-5 iron ingots at its feet (count=2 draws two copies 0.047 apart with a small random offset).

WHERE IT FITS (clearance() on engine.village seed 1; hit box 1.4 x 2.7, over the arms 1.625 wide)
    Streets are 3 blocks wide and nothing overhangs them below 3 blocks, so the golem walks every street: paths
    exit_road, nitwit_leaves, street_east, street_south, street_west are clear for the hit box, with their corners
    rounded too, and so is the square around the well. Lamp posts (plains_lamp_1: three fence posts, a block at
    z 3-4, four wall torches that reach down to z 3.19): the golem's head (2.63 above the ground on a path) passes
    UNDER the torches with 0.57 to spare; keep its centre 0.94 from a post's centre and nothing touches
    (out/test/mobs_village.png: the west street's north lane, y = 1.3, right under the lamp at (-17, 2)).
    Adjust: square_loop as drawn brushes the lamp posts at (7, -3) and (-8, -6): keep x between -7.0 and 6.2 on
    the ring. street_east: the arms brush the hay bales at (12..13, -2): walk y >= 0.3. street_west: stop at
    x >= -23.8 (the library's steps). street_south: stop at y >= -25 (the hall's entrance is 1 block wide).
    It does NOT fit: through any door (every square_to_house_* path, all *_door_in anchors: doors are 1 x 2),
    the trading-hall entrance and cells, farm_work / library_work / smithy_work (a workstation is in the way).
    Anchors it stands on freely: square_n/e/s/w, square_1..8, bell_ringer, exit_gate, meadow_far, nitwit_idle,
    every *_door_out, trade_*, hall_aisle_* (inside the hall, where it could never have walked in).

Self-test:  $BPY -m engine.mobs [check lineup turn walk walk_vanilla offer raise corner crumbs items crack village fit]
(no argument = check lineup turn walk offer items crack village; give one or two names per call to stay under the
300 s limit). Stills: out/test/mobs_*.png.
"""
import bisect
import math
import sys

import bpy
import numpy as np
from mathutils import Matrix, Vector

from . import characters as ch
from . import mcassets as mc
from . import pix

FPS = ch.FPS
TICK = FPS / 20.0                    # frames per game tick
_LOC, _ROT = "location", "rotation_euler"

# ---- net.minecraft.world.entity.EntityTypes.IRON_GOLEM: sized(1.4f, 2.7f), default eye height 0.85 * height
GOLEM_WIDTH = 1.4
GOLEM_HEIGHT = 2.7
GOLEM_EYE_HEIGHT = 0.85 * GOLEM_HEIGHT           # 2.295
MODEL_HEIGHT = 43.0 / 16.0                       # head top (model y -19) above the feet (model y 24)
MODEL_WIDTH = 26.0 / 16.0                        # over the arms (model x -13 .. 13)
LEG_LENGTH = 13.0 / 16.0                         # leg pivot (y 11) to the sole (y 24)

# ---- net.minecraft.world.entity.Mob: getMaxHeadYRot() 75, getMaxHeadXRot() 40 (IronGolem does not override them)
HEAD_YAW_MAX = math.radians(75.0)
HEAD_PITCH_MAX = math.radians(40.0)

# ---- IronGolem.createAttributes(): MOVEMENT_SPEED 0.25; registerGoals(): GolemRandomStrollInVillageGoal 0.6,
#      MoveBackToVillageGoal 0.6, MoveTowardsTargetGoal 0.9, MeleeAttackGoal 1.0.
#      Mob.setSpeed(s) also sets the forward input to s, Entity.getInputVector scales the input by the speed, and
#      LivingEntity.travelInAir multiplies the velocity by 0.6 (block friction) * 0.91 every tick:
#      blocks per tick = s * s / (1 - 0.546), s = attribute * goal modifier.
SPEED_ATTRIBUTE = 0.25
GROUND_DRAG = 0.6 * 0.91


def mob_speed(modifier, attribute=SPEED_ATTRIBUTE):
    """Blocks per SECOND a land mob reaches with this goal speed modifier (the game's quadratic mob speed)."""
    s = attribute * modifier
    return 20.0 * s * s / (1.0 - GROUND_DRAG)


WALK_SPEED = mob_speed(0.6)          # 0.991 blocks / s: strolling through the village, walking back to it
CHASE_SPEED = mob_speed(0.9)         # 2.230 blocks / s: toward a target (melee itself: mob_speed(1.0) = 2.753)

# ---- IronGolemModel.setupAnim / IronGolemRenderer.setupRotations / LivingEntity.updateWalkAnimation
WAVE_PERIOD = 13.0                   # Mth.triangleWave(walkAnimationPos, 13)
LIMB_SWING = 1.5                     # radians at walkAnimationSpeed 1 (legs, and arms around their -0.2 offset)
ARM_OFFSET = -0.2                    # arms: (-0.2 +- 1.5 * wave) * walkAnimationSpeed
ROLL_DEGREES = 6.5                   # body roll about the feet: 6.5 * triangleWave(pos + 6, 13) degrees
ROLL_SHIFT = 6.0
ANIM_PER_BLOCK = 4.0                 # walkAnimationSpeed = min(4 * blocks per tick, 1); pos += speed every tick
VANILLA_CYCLE = WAVE_PERIOD / ANIM_PER_BLOCK     # 3.25 blocks of travel per leg cycle, at any speed below 5 blocks/s
PLANTED_SWING = 0.5                  # radians: leg swing of the planted gait at walking speed (this module's choice)
PLANTED_SWING_RUN = 0.75
LEG_OFFSET = 4.5 / 16.0              # each sole's centre is 4.5 px beside the centre line (leg boxes x -7.5..-1.5 / 1.5..7.5)
CORNER_RADIUS = 1.0                  # blocks: walk() rounds the corners of its polyline with arcs (this module's choice)
MIN_CORNER = 0.08                    # a corner that can only be rounded tighter than this stays a sharp vertex
SHARP_TURN_FRAMES = 10.0             # ... and is turned on the spot, eased over this many frames
FLOWER_GROW = 4                      # frames the poppy takes to grow out of / shrink into the fist on an eased offer
FLOWER_TINY = 1e-3                   # its scale factor at the first / last instant of that
# ---- Entity.baseTick -> IronGolem.canSpawnSprintParticle / Entity.spawnSprintParticle (see IronGolem.step_crumbs)
CRUMB_CHANCE = 5                     # random.nextInt(5) == 0, every tick the golem moves
CRUMB_MIN_SPEED_SQR = 2.5e-7         # getDeltaMovement().horizontalDistanceSqr() must exceed this
CRUMB_LIFT = 0.1                     # spawned at entity y + 0.1, x and z + (random - 0.5) * width (1.4)
CRUMB_ON_BLOCK = 0.2                 # of the block 0.2 under the feet (Entity.getOnPosLegacy)
CRUMB_KICK = (-4.0, 1.5)             # particle velocity argument: (-4 * vx, 1.5, -4 * vz)
OFFER_ARM_PITCH = -0.8               # right arm while offerFlowerTick > 0: -0.8 + 0.025 * triangleWave(tick, 70)
OFFER_WOBBLE = 0.025
OFFER_PERIOD = 70.0                  # ticks
OFFER_TICKS = 400                    # OfferFlowerGoal.OFFER_TICKS / IronGolem.offerFlower: 20 seconds
ATTACK_TICKS = 10                    # IronGolem.handleEntityEvent(4): attackAnimationTick = 10
GOLEM_TEXTURE = "entity/iron_golem/iron_golem"
CRACK_TEXTURES = {                   # IronGolemCrackinessLayer; Crackiness.GOLEM: health below 75 / 50 / 25 %
    "low": "entity/iron_golem/iron_golem_crackiness_low",
    "medium": "entity/iron_golem/iron_golem_crackiness_medium",
    "high": "entity/iron_golem/iron_golem_crackiness_high",
}
WAIST = 8.0                          # rig only: the body part pivots at the top of the legs (the game never bends it)

# ---- ItemEntityRenderer / ItemEntity / ItemClusterRenderState
ITEM_MIN_HOVER = 0.0625              # ItemEntityRenderer.ITEM_MIN_HOVER_HEIGHT
ITEM_BOB = 0.1                       # sin(age / 10 + bobOffs) * 0.1 + 0.1
ITEM_BOB_TICKS = 10.0
ITEM_SPIN_TICKS = 20.0               # ItemEntity.getSpin: age / 20 + bobOffs radians
ITEM_FLAT_DEPTH = 0.0625             # FLAT_ITEM_DEPTH_THRESHOLD: thinner models are stacked along their depth
ITEM_STACK_GAP = 1.5                 # ... 1.5 * depth apart, each further copy shifted by up to 0.15 * 0.5 in x and y
ITEM_BUNDLE = 0.15                   # ITEM_BUNDLE_OFFSET_SCALE (3-D items: every further copy up to +-0.15 in x, y, z)
ITEM_GRAVITY = 0.04                  # ItemEntity.getDefaultGravity, per tick^2
ITEM_DRAG = 0.98                     # Entity.getAirDrag; on the ground the horizontal drag is 0.6 * 0.98
ITEM_TOSS = (0.1, 0.2)               # new ItemEntity(level, x, y, z, stack): velocity (+-0.1, 0.2, +-0.1) per tick


def triangle_wave(x, period):
    """net.minecraft.util.Mth.triangleWave: (|x % period - period / 2| - period / 4) / (period / 4), +1 at x = 0."""
    return (abs(math.fmod(x, period) - period * 0.5) - period * 0.25) / (period * 0.25)


def _wave(p):
    """The walk wave of the golem at animation position p (p may be any real number)."""
    return triangle_wave(p % WAVE_PERIOD, WAVE_PERIOD)


# ----------------------------------------------------------------------------------------------------
# the model
# ----------------------------------------------------------------------------------------------------
def _golem_spec():
    """net.minecraft.client.model.animal.golem.IronGolemModel.createBodyLayer(): LayerDefinition 128 x 128, drawn at
    scale 1 (IronGolemRenderer has no scale()). Pixels, model space: x to the golem's left, y down, z to its back."""
    C, P = ch._cube, ch._pose
    return dict(
        tex=(128, 128), scale=1.0, hip=11.0, top=-19.0, eye=24.0 - GOLEM_EYE_HEIGHT * 16.0, back=5.0,
        sleep_eye=GOLEM_EYE_HEIGHT,
        parts=[
            # body: PartPose.offset(0, -7, 0); the torso and the waist (CubeDeformation 0.5)
            dict(name="body", parent="hips", pivot=(0, WAIST, 0), groups=[([P(0, -7.0 - WAIST, 0)], [
                C(0, 40, -9, -2, -6, 18, 12, 11),
                C(0, 70, -4.5, 10, -3, 9, 5, 6, grow=0.5)])]),
            # head: PartPose.offset(0, -7, -2); the head and the nose
            dict(name="head", parent="body", pivot=(0, -7, -2), groups=[([], [
                C(0, 0, -4, -12, -5.5, 8, 10, 8),
                C(24, 0, -1, -5, -7.5, 2, 4, 2)])]),
            # arms: PartPose.offset(0, -7, 0) both; 4 x 30 x 6
            dict(name="arm_r", parent="body", pivot=(0, -7, 0), groups=[([], [C(60, 21, -13, -2.5, -3, 4, 30, 6)])]),
            dict(name="arm_l", parent="body", pivot=(0, -7, 0), groups=[([], [C(60, 58, 9, -2.5, -3, 4, 30, 6)])]),
            # legs: PartPose.offset(-4, 11, 0) and (5, 11, 0); 6 x 16 x 5, the left one .mirror()
            dict(name="leg_r", parent="hips", pivot=(-4, 11, 0), groups=[([], [C(37, 0, -3.5, -3, -3, 6, 16, 5)])]),
            dict(name="leg_l", parent="hips", pivot=(5, 11, 0),
                 groups=[([], [C(60, 0, -3.5, -3, -3, 6, 16, 5, mirror=True)])]),
        ])


def golem_sheet(crack=None):
    """(key, HxWx4 uint8) iron_golem.png with an optional crackiness layer drawn over it the way the game does
    (IronGolemCrackinessLayer: the same model again with a cut-out texture, texels with alpha >= 0.1 replace)."""
    base = ch._game_texture(GOLEM_TEXTURE)
    sheet = np.zeros_like(base)
    ch._over(sheet, base)
    if crack is None or crack == "none":
        return "iron_golem", sheet
    if crack not in CRACK_TEXTURES:
        raise ValueError("crack level %r: use None, 'low', 'medium' or 'high'" % (crack,))
    ch._over(sheet, ch._game_texture(CRACK_TEXTURES[crack]))
    return "iron_golem_crack_" + crack, sheet


def _flower_matrix():
    """Parent-space matrix (the right arm's rig frame) of the poppy, from IronGolemFlowerLayer.submit.

    After ModelPart.translateAndRotate(rightArm) the layer does translate(-1.1875, 1.0625, -0.9375),
    translate(0.5, 0.5, 0.5), scale(0.5), rotate X -90 degrees, translate(-0.5, -0.5, -0.5) and submits the block
    model, whose vertices are in the block's own 0..1 cube (x east, y up, z south). The poppy object is built with
    its origin at the base of the stem (block point 0.5, 0, 0.5) in Blender block axes (x, -z, y)."""
    layer = (Matrix.Translation((-1.1875, 1.0625, -0.9375)) @ Matrix.Translation((0.5, 0.5, 0.5))
             @ Matrix.Diagonal((0.5, 0.5, 0.5, 1.0)) @ Matrix.Rotation(math.radians(-90.0), 4, "X")
             @ Matrix.Translation((-0.5, -0.5, -0.5)))
    # object local (x, y, z) -> block point (x + 0.5, z, -y + 0.5); ch._AXES is exactly (x, y, z) -> (x, z, -y)
    to_block = Matrix.Translation((0.5, 0.0, 0.5)) @ ch._AXES
    return ch._AXES @ layer @ to_block


def _make_flower(name, collection):
    """The poppy the golem holds: the game's block model of Blocks.POPPY (models/block/poppy.json: block/cross with
    block/poppy), origin at the base of the stem, lit like every plant of the set."""
    from .blocks import block_material

    def material_for(q):
        return block_material(q.texture, mc.block_tint("poppy", q.tintindex), shade=getattr(q, "shade", None))

    ob = mc.quads_object(name + "_flower", mc.bake_block("poppy"), material_for, collection, origin=(8.0, 0.0, 8.0))
    ob["mc_block"] = "poppy"
    return ob


# ----------------------------------------------------------------------------------------------------
# small key helpers (on top of engine.characters' segment model)
# ----------------------------------------------------------------------------------------------------
def _dedupe(times, eps=0.02):
    """Sorted times with near-duplicates removed (keyframe_points.insert merges keys closer than 0.01); the first
    and the last time always survive."""
    out = []
    for t in sorted(times):
        if not out or t - out[-1] > eps:
            out.append(t)
        elif len(out) > 1:
            out[-1] = t                                                  # keep the later one: the end must stay the end
    return out


def _ease(x):
    """Sine ease in-out of x clamped to 0..1 (the shape of engine.characters' SMOOTH keys)."""
    return 0.5 - 0.5 * math.cos(math.pi * ch._clamp(x, 0.0, 1.0))


def _frames_in(ta, tb):
    """The two ends of a time window and every whole frame between them."""
    return {float(ta), float(tb)} | {float(t) for t in range(int(math.ceil(ta)), int(math.floor(tb)) + 1)}


class _Route:
    """A walking route: the polyline `path` (Vectors) with its horizontal corners rounded by arcs of `radius`.

    pieces = [(d0, d1, 'line', (p, q)) | (d0, d1, 'arc', (centre xy, R, p, q, turn))] along the distance d;
    a corner that cannot be rounded (radius 0, a U-turn, legs too short for an arc of MIN_CORNER) stays a sharp
    vertex, listed in `sharp` as (distance, turn in radians). headings = the yaw of every polyline segment,
    unwrapped from `yaw_now` so that every turn takes the short way round. z follows the polyline."""

    def __init__(self, path, radius, yaw_now=0.0):
        m = len(path) - 1
        prev, self.headings, flat = float(yaw_now), [], []
        for a, b in zip(path, path[1:]):
            d = b - a
            h = math.hypot(d.x, d.y)
            if h > 1e-5:
                prev = prev + ch._wrap(math.atan2(d.x, -d.y) - prev)
            self.headings.append(prev)
            flat.append(h)
        hd = self.headings
        cut = [0.0] * (m + 1)                                            # tangent length the arc takes off both legs
        for i in range(1, m):
            turn = hd[i] - hd[i - 1]
            if radius <= 0.0 or abs(turn) < 1e-3 or flat[i - 1] < 1e-5 or flat[i] < 1e-5:
                continue
            room = min(flat[i - 1] * (1.0 if i == 1 else 0.5), flat[i] * (1.0 if i == m - 1 else 0.5))
            tan = math.tan(min(abs(turn), math.pi - 1e-6) / 2.0)
            tl = min(radius * tan, room)
            if tl / tan >= MIN_CORNER:
                cut[i] = tl
        self.pieces, self.sharp, d = [], [], 0.0
        for i in range(m):
            a, b = path[i], path[i + 1]
            p = a.lerp(b, cut[i] / flat[i]) if cut[i] > 0.0 else a
            q = b.lerp(a, cut[i + 1] / flat[i]) if cut[i + 1] > 0.0 else b
            length = (q - p).length
            if length > 1e-9:
                self.pieces.append((d, d + length, "line", (p.copy(), q.copy())))
                d += length
            if i + 1 >= m:
                break
            turn = hd[i + 1] - hd[i]
            if cut[i + 1] > 0.0:
                nxt = path[i + 1].lerp(path[i + 2], cut[i + 1] / flat[i + 1])
                rad = cut[i + 1] / math.tan(abs(turn) / 2.0)
                u = Vector((math.sin(hd[i]), -math.cos(hd[i])))          # the way it is facing
                centre = Vector((q.x, q.y)) + Vector((-u.y, u.x)) * (rad if turn > 0.0 else -rad)
                length = math.hypot(rad * abs(turn), nxt.z - q.z)
                self.pieces.append((d, d + length, "arc", (centre, rad, q.copy(), nxt.copy(), turn)))
                d += length
            elif abs(turn) > 1e-4:
                self.sharp.append((d, turn))
        self.total = d
        self.breaks = [0.0] + [piece[1] for piece in self.pieces]
        self.arcs = [(d0, d1, data[4], data[1]) for d0, d1, kind, data in self.pieces if kind == "arc"]

    def point(self, d):
        """Position after d blocks."""
        d = ch._clamp(d, 0.0, self.total)
        i = min(max(bisect.bisect_right(self.breaks, d) - 1, 0), len(self.pieces) - 1)
        d0, d1, kind, data = self.pieces[i]
        s = (d - d0) / (d1 - d0)
        if kind == "line":
            return data[0].lerp(data[1], s)
        centre, _rad, p, q, turn = data
        r0 = Vector((p.x, p.y)) - centre
        c, sn = math.cos(turn * s), math.sin(turn * s)
        return Vector((centre.x + c * r0.x - sn * r0.y, centre.y + sn * r0.x + c * r0.y, p.z + (q.z - p.z) * s))

    def turned(self, d):
        """Radians turned on the arcs within the first d blocks (sharp vertices not included)."""
        return sum(turn * ch._clamp((d - d0) / (d1 - d0), 0.0, 1.0) for d0, d1, turn, _rad in self.arcs)


def rounded(points, radius=CORNER_RADIUS, step=0.25):
    """The line walk(points, corner=radius) really follows (corners cut by arcs), sampled every `step` blocks: feed it to clearance()."""
    pts = [ch._vec3(p) for p in points]
    path = pts[:1]
    for p in pts[1:]:
        if (p - path[-1]).length > 1e-5:
            path.append(p)
    if len(path) < 2:
        return [tuple(p) for p in path]
    route = _Route(path, 0.0 if radius is None else float(radius))
    n = max(1, int(math.ceil(route.total / step)))
    return [tuple(route.point(route.total * i / n)) for i in range(n + 1)]


def _sample(ob, path, index, f0, times, fn, rest=0.0, settle=6.0):
    """One LINEAR segment on a channel: a key at f0 + t for every t in `times` with value fn(t). The first key is
    the channel's current value; if the last value is not `rest`, the channel eases there over `settle` frames."""
    ts = _dedupe(times)
    keys = [(f0 + t, None if i == 0 else fn(t), "LINEAR") for i, t in enumerate(ts)]
    if len(keys) < 2:
        return
    if abs(fn(ts[-1]) - rest) > 1e-6:
        keys[-1] = (keys[-1][0], keys[-1][1], "SMOOTH")
        keys.append((f0 + ts[-1] + settle, rest, "LINEAR"))
    ch._segment(ob, path, index, keys, "LINEAR")


def _visibility_curve(ob, events, before):
    """Rewrite an object's hide_render / hide_viewport keys from [(frame, visible)] (CONSTANT, integer frames)."""
    events = sorted(events)
    for path in ("hide_render", "hide_viewport"):
        fc = ch._ensure(ob, path, 0)
        fc.keyframe_points.clear()
        if not events:
            setattr(ob, path, not before)
            continue
        ch._put(fc, min(events[0][0], 1) - 1, 0.0 if before else 1.0, "CONSTANT")
        for frame, visible in events:
            ch._put(fc, frame, 0.0 if visible else 1.0, "CONSTANT")
        fc.update()
        setattr(ob, path, not before)


def _state_at(events, frame, default):
    """Value of the last (frame, value) event at or before `frame`."""
    value = default
    for f, v in sorted(events, key=lambda e: e[0]):
        if f <= frame + 1e-6:
            value = v
    return value


class _CrumbBlock:
    """Stand-in for an engine.fx Block: all its terrain particles ask for is a name and the particle texture."""

    def __init__(self, name, particle_texture):
        self.name, self.particle_texture = name, particle_texture


class _Floor:
    """Stand-in for engine.fx's collision boxes when there is no Village: a flat floor at height z."""

    def __init__(self, z):
        self.z = float(z)

    def collide(self, pos, move, width):
        """The part of `move` a particle at `pos` can make without sinking under the floor."""
        if pos[2] + move[2] < self.z:
            return [move[0], move[1], self.z - pos[2]]
        return move


# ----------------------------------------------------------------------------------------------------
# the golem
# ----------------------------------------------------------------------------------------------------
class IronGolem(ch.Character):
    """The vanilla iron golem as an engine.characters.Character with its own gait, flower and head limits."""

    def __init__(self, name, parts, spec, flower=None, crack_level=None):
        super().__init__(name, "golem", parts, spec)
        # Character gives arm rigs the player's resting splay (AnimationUtils.bobArms); the golem's arms hang straight
        self._set_rest(self.arm_r, _ROT, 1, 0.0)
        self._set_rest(self.arm_l, _ROT, 1, 0.0)
        self.flower = flower
        self.crack_level = crack_level
        self.width = MODEL_WIDTH
        self._walk_pos = 0.0               # the game's walkAnimation.position (gait="vanilla" carries it along)
        self._offers = []                  # (frame, bool): the offer POSE (what walk() and place() ask about)
        self._blooms = []                  # (frame, bool, frames): the poppy is there / gone, grown / shrunk over `frames`
        self._shown = []                   # (frame, bool)
        self._crumb_blocks = {}
        self.last_walk = None
        self._flower_basis = _flower_matrix()
        if flower is not None:
            flower.parent = self.arm_r
            flower.matrix_parent_inverse = Matrix.Identity(4)
            flower.matrix_basis = self._flower_basis
            flower.hide_render = flower.hide_viewport = True
            self._flower_scale = tuple(flower.scale)

    def __repr__(self):
        return "<IronGolem %s>" % self.name

    # ------------------------------------------------------------------ queries
    def offering_at(self, frame):
        """True while the flower is offered at `frame`."""
        return bool(_state_at(self._offers, frame, False))

    def flower_point(self, frame):
        """World position of the poppy's bloom (the top of the flower) at `frame`."""
        scene = bpy.context.scene
        cur, sub = scene.frame_current, scene.frame_subframe
        whole = int(math.floor(frame))
        scene.frame_set(whole, subframe=float(frame) - whole)
        # (from the arm, not from the flower object: its scale is keyed while it grows out of the fist)
        point = self.arm_r.matrix_world @ (self._flower_basis @ Vector((0.0, 0.0, 8.5 / 16.0)))   # rows 5-9 of block/poppy
        scene.frame_set(cur, subframe=sub)
        return point

    def flower_at(self, frame):
        """True while the poppy exists at `frame` (it outlives the pose by the frames an eased lowering takes)."""
        state = False
        for f, on, _grow in sorted(self._blooms, key=lambda e: e[0]):
            if f <= frame + 1e-6:
                state = on
        return state

    def _aim(self, target, frame):
        """Head (yaw, pitch-up) toward a target, clamped to the game's limits for mobs (75 / 40 degrees)."""
        if target is None:
            return 0.0, 0.0
        d = self._point(target, frame) - self.eye_point(frame)
        yaw = ch._clamp(ch._wrap(math.atan2(d.x, -d.y) - self.yaw_at(frame)), -HEAD_YAW_MAX, HEAD_YAW_MAX)
        pitch = ch._clamp(math.atan2(d.z, math.hypot(d.x, d.y)), -HEAD_PITCH_MAX, HEAD_PITCH_MAX)
        return yaw, pitch

    # ------------------------------------------------------------------ visibility
    def _sync_flower(self):
        """The poppy is rendered while the golem is shown AND the flower is there; rewrites its visibility and scale keys."""
        if self.flower is None:
            return
        blooms = sorted(self._blooms, key=lambda e: e[0])
        frames = sorted({f for f, _on, _grow in blooms} | {f for f, _v in self._shown})
        events = [(f, bool(_state_at(self._shown, f, True)) and self.flower_at(f)) for f in frames]
        _visibility_curve(self.flower, events, before=False)
        # scale: an eased raise lets it grow out of the fist, an eased lowering lets it shrink back into it
        keys, state, grown = [], False, -1e9
        for f, on, grow in blooms:
            if on and not state:
                if grow > 0:
                    keys += [(f, FLOWER_TINY, "LINEAR"), (f + grow, 1.0, "CONSTANT")]
                else:
                    keys.append((f, 1.0, "CONSTANT"))
                grown = f + grow
            elif state and not on:
                grow = min(grow, int(math.floor(f - grown)))
                if grow > 0:
                    keys += [(f - grow, 1.0, "LINEAR"), (f, FLOWER_TINY, "CONSTANT")]
            state = on
        for i in range(3):
            fc = ch._find(self.flower, "scale", i)
            if fc is None and not keys:
                continue                                                 # never offered with an ease: no curve at all
            fc = fc or ch._ensure(self.flower, "scale", i)
            fc.keyframe_points.clear()
            for f, factor, interp in keys:
                ch._put(fc, f, factor * self._flower_scale[i], interp)
            fc.update()
            self.flower.scale[i] = self._flower_scale[i]

    def show(self, frame, visible=True):
        """Key render visibility of the whole golem from `frame` on (the poppy shows only while it is offered)."""
        super().show(frame, visible)
        self._shown.append((frame, bool(visible)))
        self._sync_flower()

    # ------------------------------------------------------------------ placement
    def place(self, frame, pos, yaw=0.0, keep_pose=False):
        """Hard-set position and yaw from `frame` on: upright, neutral pose, no flower (use at shot cuts)."""
        super().place(frame, pos, yaw, keep_pose=keep_pose)
        if not keep_pose:
            if ch._find(self.root, _ROT, 1) is not None:
                ch._cut(self.root, _ROT, 1, frame, 0.0)                 # the walk's roll
            if self.offering_at(frame) or self.flower_at(frame):
                self._offers.append((frame, False))
                self._blooms.append((frame, False, 0))
                self._sync_flower()

    # ------------------------------------------------------------------ locomotion
    def walk(self, frame, points, speed=None, run=False, from_current=False, gait="planted", swing=None, ramp=8,
             corner=CORNER_RADIUS):
        """Travel along the polyline `points` with the golem's gait (0.99 blocks/s, 2.23 with run=True); returns the end frame.

        gait "planted": the game's wave, roll and arm swing, legs opened to `swing` rad (0.5; 0.75 running) and the
        cycle shortened so the feet do not slide. gait "vanilla": exactly the game (legs +-1.5 * min(speed / 5, 1)
        rad, one cycle per 3.25 blocks; the feet slide). `ramp` = frames of acceleration at the start and of braking
        at the end, or a pair (start, end); the stride follows the distance covered, so the feet stay planted
        through both. ramp=(0, 8) starts at full speed with the legs passing each other: a walk that opens a shot
        in stride without a pre-roll. `corner` = radius in blocks of the arc that rounds each corner of the
        polyline (the body turns along it and every foot takes the step its own side of the curve needs);
        corner=0 keeps the vertices sharp and turns on the spot over 10 frames (the planted feet then skate).
        """
        if gait not in ("planted", "vanilla"):
            raise ValueError("gait %r: use 'planted' or 'vanilla'" % (gait,))
        if speed is None:
            speed = CHASE_SPEED if run else WALK_SPEED
        f0 = int(round(frame))
        here = self.pos_at(f0)
        yaw_now = self.yaw_at(f0)
        pts = [ch._vec3(p, here.z) for p in points]
        if from_current:
            pts.insert(0, here.copy())
        path = pts[:1]
        for p in pts[1:]:
            if (p - path[-1]).length > 1e-5:
                path.append(p)
        teleport = (path[0] - here).length > 1e-4
        if len(path) < 2:
            if teleport:
                for i in range(3):
                    ch._cut(self.root, _LOC, i, f0, path[0][i], hold_rest=False)
            return f0
        on_cut = teleport or ch._cut_at(self.root, _LOC, 0, f0)
        route = _Route(path, 0.0 if corner is None else float(corner), yaw_now)
        total = route.total
        heading0 = route.headings[0]

        # speed profile: `r_in` frames of constant acceleration, cruise, `r_out` frames of braking
        cruise = max(float(speed), 1e-3) / FPS                          # blocks per frame
        r_in, r_out = (ramp if isinstance(ramp, (tuple, list)) else (ramp, ramp))
        r_in = max(0.0, min(float(r_in), total / cruise))
        r_out = max(0.0, min(float(r_out), total / cruise))
        n = max(2, int(round(total / cruise + (r_in + r_out) / 2.0)))
        if r_in + r_out > n:
            r_in, r_out = r_in * n / (r_in + r_out), r_out * n / (r_in + r_out)
        cruise = total / (n - (r_in + r_out) / 2.0)
        f1 = f0 + n

        # an offer keyed earlier for a LATER frame of this walk: its arm keys are about to be overwritten
        if not self.offering_at(f0):
            clash = sorted(f for f, on in self._offers if on and f0 < f <= f1 + 6)   # (+ the frames the arms take to settle)
            if clash:
                raise ValueError("%s.walk over frames %d-%d runs through the flower offer already keyed at frame %d: "
                                 "its arm swing would replace the offer pose and leave the poppy in a swinging fist. "
                                 "Key a golem in frame order (walk first, then offer_flower during it), end this "
                                 "walk before frame %d, or use a second golem for the other shot."
                                 % (self.name, f0, f1, clash[0], clash[0]))

        def dist(t):
            """Blocks covered t frames into the walk."""
            if r_in > 0.0 and t < r_in:
                return cruise * t * t / (2.0 * r_in)
            if r_out > 0.0 and t > n - r_out:
                return total - cruise * (n - t) ** 2 / (2.0 * r_out)
            return cruise * (t - r_in / 2.0)

        def rate(t):
            """Speed t frames into the walk as a fraction of the cruising speed."""
            up = t / r_in if r_in > 0.0 else 1.0
            down = (n - t) / r_out if r_out > 0.0 else 1.0
            return ch._clamp(min(up, down), 0.0, 1.0)

        def when(d):
            """Frames into the walk at which `d` blocks are covered."""
            d = ch._clamp(d, 0.0, total)
            if r_in > 0.0 and d < cruise * r_in / 2.0:
                return math.sqrt(2.0 * r_in * d / cruise)
            if r_out > 0.0 and d > total - cruise * r_out / 2.0:
                return n - math.sqrt(2.0 * r_out * (total - d) / cruise)
            return d / cruise + r_in / 2.0

        ramp_times = {0.0, 1.0, n - 1.0, float(n)}                      # (the limbs join their curve within a frame)
        if r_in > 0.0:
            ramp_times |= {float(t) for t in range(0, int(math.ceil(r_in)) + 1)} | {r_in}
        if r_out > 0.0:
            ramp_times |= {float(t) for t in range(int(math.floor(n - r_out)), n + 1)} | {n - r_out}
        ramp_times = {t for t in ramp_times if 0.0 <= t <= n}
        bounds = [when(d) for d in route.breaks]
        bounds[0], bounds[-1] = 0.0, float(n)

        # heading: along the arcs it follows the tangent; a sharp vertex is turned on the spot, eased and centred
        # on the vertex; a golem that does not face its first leg turns into it while it sets off
        arcs = [(when(d0), when(d1)) for d0, d1, _turn, _rad in route.arcs]
        sharp = []
        for d, turn in route.sharp:
            t = when(d)
            before = max([x for x in bounds if x < t - 1e-6], default=0.0)
            after = min([x for x in bounds if x > t + 1e-6], default=float(n))
            h = min(SHARP_TURN_FRAMES / 2.0, 0.45 * (t - before), 0.45 * (after - t))
            sharp.append((t - h, t + h, turn))
        first, first_frames = 0.0, 0.0
        if not on_cut and abs(yaw_now - heading0) > 1e-4:
            first = yaw_now - heading0
            first_frames = SHARP_TURN_FRAMES * ch._clamp(abs(first) / (math.pi / 2), 0.6, 2.0)
            first_frames = min(first_frames, 0.6 * when(min((path[1] - path[0]).length, total)))

        def yaw(t):
            """Body yaw t frames into the walk."""
            y = heading0 + route.turned(dist(t))
            for ta, tb, turn in sharp:
                y += turn * (_ease((t - ta) / (tb - ta)) if tb > ta else float(t >= ta))
            if first_frames > 0.0:
                y += first * (1.0 - _ease(t / first_frames))
            return y

        turning = set()                                                  # frames at which the heading changes
        for ta, tb in arcs + [(ta, tb) for ta, tb, _turn in sharp] + ([(0.0, first_frames)] if first_frames > 0.0 else []):
            turning |= _frames_in(ta, tb)
        turning = {t for t in turning if 0.0 <= t <= n}
        curve = set()                                                    # frames at which the position is on an arc
        for ta, tb in arcs:
            curve |= _frames_in(ta, tb)

        if teleport:
            for i in range(3):
                ch._cut(self.root, _LOC, i, f0, path[0][i], hold_rest=False)
        if on_cut:
            ch._cut(self.root, _ROT, 2, f0, heading0, hold_rest=False)  # starting on a cut: already facing its way

        ch._segment(self.root, _ROT, 2, [(f0 + t, yaw(t), "LINEAR") for t in _dedupe(turning | {0.0, float(n)})], "LINEAR")
        travel = ramp_times | set(bounds) | {t for t in curve if 0.0 <= t <= n}
        shift = None                                                     # planted gait: see below

        # the gait: animation position as a function of the distance covered
        if gait == "vanilla":
            per_block = ANIM_PER_BLOCK                                   # 13 units per 3.25 blocks
            p0 = self._walk_pos
            self._walk_pos = (p0 + per_block * total) % WAVE_PERIOD
            leg_swing = None
        else:
            want = float(swing) if swing is not None else (PLANTED_SWING_RUN if run else PLANTED_SWING)
            step = 2.0 * LEG_LENGTH * math.sin(ch._clamp(want, 0.05, 1.3))
            steps = max(1, int(round(total / step)))
            leg_swing = math.asin(ch._clamp(total / steps / (2.0 * LEG_LENGTH), 0.0, math.sin(1.3)))
            per_block = (WAVE_PERIOD / 2.0) * steps / total
            p0 = WAVE_PERIOD * (0.25 if self._foot > 0 else 0.75)        # a zero crossing: both legs together
            first_stance = "r" if self._foot > 0 else "l"                # (the leg that goes back first)
            if steps % 2:
                self._foot = -self._foot

        def pos(t):
            return p0 + per_block * dist(t)

        def crossings(offset, spacing=WAVE_PERIOD / 2.0):
            """Times at which pos + offset passes a multiple of `spacing` (6.5: where the wave turns round)."""
            out = set()
            k = math.ceil((p0 + offset) / spacing - 1e-9)
            while True:
                d = (k * spacing - offset - p0) / per_block
                if d > total + 1e-9:
                    break
                if d >= 0.0:
                    out.add(when(d))
                k += 1
            return out

        leg_times = ramp_times | crossings(0.0)
        if gait == "vanilla":
            def anim(t):
                """LivingEntity.updateWalkAnimation: walkAnimationSpeed = min(4 * blocks per tick, 1)."""
                return min(rate(t) * cruise * FPS / 5.0, 1.0)

            _sample(self.leg_r, _ROT, 0, f0, leg_times, lambda t: -LIMB_SWING * anim(t) * _wave(pos(t)))
            _sample(self.leg_l, _ROT, 0, f0, leg_times, lambda t: LIMB_SWING * anim(t) * _wave(pos(t)))
            shown_swing = LIMB_SWING * anim(n / 2.0)
        else:
            # Planted: the foot on the ground stays where it was put. Between two turning points of the wave one
            # leg is the stance leg; the ground under ITS side of the body passes at the body's speed minus
            # (yaw rate x its 4.5 px offset from the centre line), so in a curve the inner foot takes a shorter
            # step than the outer one. Its sole is held still against that; the other leg swings from where its
            # last step ended to where its next one starts. On a straight this is the game's wave with the angle
            # bent by at most 0.4 degrees (leg * sin(angle) = half a step * wave).
            yaw0 = yaw(0.0)
            side = {"r": -LEG_OFFSET, "l": LEG_OFFSET}                   # to the golem's left

            def lane(leg, t):
                """Ground passed under that leg's side of the body, along its heading."""
                return dist(t) - side[leg] * (yaw(t) - yaw0)

            marks = [0.0] + [when((k - 0.5) * total / steps) for k in range(1, steps + 1)] + [float(n)]
            last = len(marks) - 2
            stance = [first_stance if j % 2 == 0 else ("l" if first_stance == "r" else "r") for j in range(last + 1)]
            gone = [lane(stance[j], marks[j + 1]) - lane(stance[j], marks[j]) for j in range(last + 1)]
            y_in = [0.0 if j == 0 else (gone[j] if j == last else gone[j] / 2.0) for j in range(last + 1)]
            y_out = [y_in[j] - gone[j] for j in range(last + 1)]
            reach = LEG_LENGTH * math.sin(1.3)

            def foot(leg, t):
                """How far that sole is in front of its hip."""
                j = min(max(bisect.bisect_right(marks, t) - 1, 0), last)
                if stance[j] == leg:
                    return y_in[j] - (lane(leg, t) - lane(leg, marks[j]))
                a = y_out[j - 1] if j > 0 else 0.0
                b = y_in[j + 1] if j < last else 0.0
                span = dist(marks[j + 1]) - dist(marks[j])
                return a + (b - a) * ((dist(t) - dist(marks[j])) / span if span > 1e-9 else 1.0)

            def leg_angle(leg, t):
                return -math.asin(ch._clamp(foot(leg, t), -reach, reach) / LEG_LENGTH)

            stride_times = leg_times | crossings(0.0, WAVE_PERIOD / 16.0) | turning
            _sample(self.leg_r, _ROT, 0, f0, stride_times, lambda t: leg_angle("r", t))
            _sample(self.leg_l, _ROT, 0, f0, stride_times, lambda t: leg_angle("l", t))
            shown_swing = leg_swing

            # Round an arc the body would turn about its own middle, which drags the planted sole sideways by
            # (yaw rate x how far the sole is in front of the hip). The body is moved the other way instead: it
            # pivots over the foot that carries it (never more than 0.1 block off the arc). What is left over at
            # the end of the arcs is given back evenly along the whole walk (millimetres per step).
            if arcs:
                grid = set(marks)
                for ta, tb in arcs:
                    grid |= {ta, tb} | {ta + (tb - ta) * k / max(1, int(math.ceil((tb - ta) * 4.0)))
                                        for k in range(int(math.ceil((tb - ta) * 4.0)) + 1)}
                grid = _dedupe([t for t in grid if 0.0 <= t <= n], eps=1e-6)
                table, e = [(0.0, 0.0, 0.0)], Vector((0.0, 0.0))
                for ta, tb in zip(grid, grid[1:]):
                    turn = route.turned(dist(tb)) - route.turned(dist(ta))
                    if abs(turn) > 1e-12:
                        tm = 0.5 * (ta + tb)
                        j = min(max(bisect.bisect_right(marks, tm) - 1, 0), last)
                        ym = yaw(tm)
                        e = e - Vector((math.cos(ym), math.sin(ym))) * (foot(stance[j], tm) * turn)
                    table.append((tb, e.x, e.y))
                if table[-1][0] < n:
                    table.append((float(n), e.x, e.y))
                stamps = [row[0] for row in table]

                def shift(t):
                    """Sideways shift of the body t frames into the walk (x, y)."""
                    k = min(max(bisect.bisect_right(stamps, t) - 1, 0), len(table) - 2)
                    (ta, xa, ya), (tb, xb, yb) = table[k], table[k + 1]
                    u = ch._clamp((t - ta) / (tb - ta), 0.0, 1.0) if tb > ta else 1.0
                    back = dist(t) / total
                    return (xa + (xb - xa) * u - e.x * back, ya + (yb - ya) * u - e.y * back)

                travel |= {t for t in marks if any(ta - 1e-6 <= t <= tb + 1e-6 for ta, tb in arcs)}

        # travel: LINEAR keys, exact on the straights, a key per frame round the arcs
        def spot(t):
            here = route.point(dist(t))
            if shift is not None:
                dx, dy = shift(t)
                here.x, here.y = here.x + dx, here.y + dy
            return here

        travel = _dedupe(travel)
        spots = [spot(t) for t in travel]
        for i in range(3):
            ch._segment(self.root, _LOC, i, [(f0 + t, q[i], "LINEAR") for t, q in zip(travel, spots)], "LINEAR")

        roll = math.radians(ROLL_DEGREES)
        _sample(self.root, _ROT, 1, f0, ramp_times | crossings(ROLL_SHIFT),
                lambda t: roll * rate(t) * _wave(pos(t) + ROLL_SHIFT))
        if not self.offering_at(f0):                                    # (the offer pose keeps both arms, as in game)
            def anim_speed(t):
                return min(rate(t) * cruise * FPS / 5.0, 1.0)

            _sample(self.arm_r, _ROT, 0, f0, leg_times, lambda t: (ARM_OFFSET + LIMB_SWING * _wave(pos(t))) * anim_speed(t))
            _sample(self.arm_l, _ROT, 0, f0, leg_times, lambda t: (ARM_OFFSET - LIMB_SWING * _wave(pos(t))) * anim_speed(t))
        self.last_walk = dict(gait=gait, frames=(f0, f1), blocks=total, speed=cruise * FPS,
                              swing=shown_swing, cycle_blocks=WAVE_PERIOD / per_block,
                              cycle_frames=WAVE_PERIOD / per_block / cruise,
                              corners=[(round(rad, 3), round(math.degrees(turn), 1)) for _d0, _d1, turn, rad in route.arcs],
                              sharp=[round(math.degrees(turn), 1) for _d, turn in route.sharp],
                              path=[tuple(round(c, 4) for c in route.point(total * i / max(1, int(math.ceil(total / 0.25)))))
                                    for i in range(max(1, int(math.ceil(total / 0.25))) + 1)])
        return f1

    # ------------------------------------------------------------------ idle + gestures
    def idle(self, frame_start, frame_end, seed=0):
        """Slow head turns between frame_start and frame_end (RandomLookAroundGoal); nothing else moves (seeded)."""
        f0, f1 = int(frame_start), int(frame_end)
        if f1 - f0 < 24:
            return
        r = pix.rng(6151 * (int(seed) + 1) + 3)
        for index, spread, lo, hi in ((2, 0.9, -HEAD_YAW_MAX, HEAD_YAW_MAX), (0, 0.12, -HEAD_PITCH_MAX, HEAD_PITCH_MAX)):
            base = ch._val(self.head, _ROT, index, f0)
            keys, cur = [(f0, None)], base
            t = f0 + int(r.integers(8, 30))
            back = min(16, (f1 - f0) // 3)
            while True:
                dur = int(r.integers(12, 22))                           # a golem turns its head slowly
                if t + dur > f1 - back - 2:
                    break
                tgt = base if r.random() < 0.25 else ch._clamp(base + r.uniform(-spread, spread), lo, hi)
                keys += [(t, cur), (t + dur, tgt)]
                cur = tgt
                t += dur + int(r.integers(30, 80))
            keys += [(f1 - back, cur), (f1, base)]
            ch._segment(self.head, _ROT, index, keys)

    def offer_flower(self, frame, on=True, ease=8, ticks=OFFER_TICKS, grow=None):
        """Raise the right arm into the game's offer pose, poppy in hand (on=False: lower it); returns the end frame.

        The arm eases over `ease` frames (0 = the game's snap, keyed as a hard cut) and then keeps the game's
        +-0.025 rad wobble for `ticks` game ticks (400 = the 20 s an offer lasts in the game). With ease=0 the
        poppy is simply there / gone on `frame`, as in the game. With an eased raise it grows out of the fist over
        the first `grow` frames (default 4), and with an eased lowering it rides the arm down and shrinks back into
        the fist over the last `grow` frames: no flower pops in or out of an arm that is on screen.
        """
        f0 = int(round(frame))
        f1 = f0 + max(0, int(ease))
        grow = min(f1 - f0, FLOWER_GROW if grow is None else max(0, int(grow)))
        if on:
            def pitch(f):
                """IronGolemModel.setupAnim: the offer tick counts down from 400."""
                tick = OFFER_TICKS - (f - f0) / TICK
                return OFFER_ARM_PITCH + OFFER_WOBBLE * triangle_wave(tick % OFFER_PERIOD, OFFER_PERIOD)

            end = f0 + max(float(ticks), 1.0) * TICK
            turns = []
            k = math.floor(OFFER_TICKS / (OFFER_PERIOD / 2.0))
            while True:                                                  # the wave turns round at tick = k * 35
                f = f0 + (OFFER_TICKS - k * OFFER_PERIOD / 2.0) * TICK
                if f >= end:
                    break
                if f > f1 + 0.02:
                    turns.append(f)
                k -= 1
            if f1 <= f0:
                ch._cut(self.arm_r, _ROT, 0, f0, pitch(f0))
                ch._cut(self.arm_l, _ROT, 0, f0, 0.0)
                keys = [(f0, pitch(f0), "LINEAR")]
            else:
                keys = [(f0, None, "SMOOTH"), (f1, pitch(f1), "LINEAR")]
                ch._ease(self.arm_l, _ROT, 0, f0, f1, 0.0)
            keys += [(f, pitch(f), "LINEAR") for f in turns]
            if end > keys[-1][0] + 0.02:
                keys.append((end, pitch(end)))
            if len(keys) >= 2:
                ch._segment(self.arm_r, _ROT, 0, keys)
            self._blooms.append((f0, True, grow))
        else:
            ch._ease(self.arm_r, _ROT, 0, f0, f1, self._rest(self.arm_r, _ROT, 0))
            self._blooms.append((f1, False, grow))                      # gone once the arm is down
        self._offers.append((f0, bool(on)))
        self._sync_flower()
        return f1

    def step_crumbs(self, frame_start, frame_end, camera, village=None, block="dirt_path", seed=0, glow=0.0,
                    collection=None):
        """The crumbs of the ground a moving golem kicks up, for the frames [frame_start, frame_end); returns an engine.fx Burst.

        Entity.baseTick -> IronGolem.canSpawnSprintParticle / Entity.spawnSprintParticle: on every game tick on
        which the golem moves, with a chance of 1 in 5, ONE block particle of the block under its feet, somewhere
        in its 1.4-wide footprint, 0.1 above its feet, thrown up (velocity argument (-4 vx, 1.5, -4 vz)): about
        four a second, each a 0.1-0.2 block square showing a quarter of the block's particle texture at 0.6 of its
        colour, falling back and gone after 4-40 ticks (the game's TerrainParticle, drawn by engine.fx).
        Call it AFTER the walk is keyed: it reads the keyed motion. camera = the Shot that films it (or its camera
        object, or the Film): the squares face the camera. village = the Village: the block is then read from the
        set under the golem at each tick and the crumbs land on the set; without it they are crumbs of `block`
        and land on the height of the golem's feet. No crumb is left on frame_end: pass the first frame after the
        shot, or the frame the golem leaves the picture.
        """
        from . import fx                                                 # (only here: engine.fx stays optional)

        missing = [n for n in ("Burst", "_camera_arg", "_collection", "_Solids", "_terrain_particle") if not hasattr(fx, n)]
        if missing:
            raise RuntimeError("IronGolem.step_crumbs draws its particles with engine.fx, which no longer has %s"
                               % ", ".join(missing))
        f0, f1 = float(frame_start), float(frame_end)
        last = int(math.ceil(f1 - 1e-6))
        burst = fx.Burst("golem_crumbs", int(math.ceil(f0 - 1e-6)))
        cams = fx._camera_arg(camera)
        col = fx._collection(collection)
        world = getattr(village, "world", None)
        solids = fx._Solids(village) if world is not None else None
        key = [int(seed) & 0x7FFFFFFF, 20011, int(round(f0 * 4.0)) & 0x7FFFFFFF]
        dice = np.random.default_rng(key)
        tick = -1
        while True:
            tick += 1
            f = f0 + tick * TICK
            if math.ceil(f - 1e-6) >= last:                              # (it would first be seen on frame_end)
                break
            lucky = int(dice.integers(0, CRUMB_CHANCE)) == 0
            here, before = self.pos_at(f), self.pos_at(f - TICK)
            v = (here - before) * GROUND_DRAG                           # what getDeltaMovement holds between two ticks
            if not lucky or v.x * v.x + v.y * v.y <= CRUMB_MIN_SPEED_SQR:
                continue
            r = np.random.default_rng(key + [tick])
            at = (here.x + (r.random() - 0.5) * GOLEM_WIDTH, here.y + (r.random() - 0.5) * GOLEM_WIDTH, here.z + CRUMB_LIFT)
            if world is not None:
                state = world.get(int(math.floor(here.x)), int(math.floor(here.y)), int(math.floor(here.z - CRUMB_ON_BLOCK)))
                if state is None:
                    continue                                             # nothing under it: no particle
                crumb = self._crumb_block(state[0], state[1])
            else:
                crumb = self._crumb_block(block, None)
            ground = solids if solids is not None else _Floor(here.z)
            fx._terrain_particle(burst, crumb, r, at, (CRUMB_KICK[0] * v.x, CRUMB_KICK[0] * v.y, CRUMB_KICK[1]), f,
                                 cams, col, ground, glow)
        for part in burst.particles:                                     # nothing outlives frame_end
            if part["last"] > last:
                for path in ("hide_render", "hide_viewport"):
                    fc = ch._ensure(part["object"], path, 0)
                    ch._put(fc, last, 1.0, "CONSTANT")
                    fc.update()
                part["last"] = last
        burst.frame_end = max([burst.frame] + [part["last"] - 1 for part in burst.particles])
        return burst

    def _crumb_block(self, block_id, props):
        """What engine.fx needs to know of a block to draw its particles: a name and (particle texture, tint)."""
        block_id = block_id.replace("minecraft:", "")
        if block_id not in self._crumb_blocks:
            tex = None
            try:
                parts = mc.resolve_blockstate(block_id, dict(props or {}))
                tex = mc.load_model(parts[0].model).textures.get("particle")
            except Exception:                                           # noqa: BLE001 - odd models: the block's own texture
                tex = None
            if not tex or tex.startswith("#"):
                tex = "block/" + block_id
            # TerrainParticle: colour 0.6 x BlockTintSource.colorAsTerrainParticle; BlockTintSources.grassBlock()
            # answers -1 (white) there, so a grass block's crumbs are plain dirt, not biome green
            tint = None if block_id == "grass_block" else mc.block_tint(block_id, 0)
            self._crumb_blocks[block_id] = _CrumbBlock("%s_%s" % (self.name, block_id), (mc._norm(tex), tint))
        return self._crumb_blocks[block_id]

    def attack(self, frame):
        """The game's attack: both arms thrown up over the head and back (10 ticks = 12 frames); returns the end frame.

        IronGolemModel.setupAnim: both arms -2 + 1.5 * triangleWave(attackTicksRemaining, 10), ticks 10 -> 0."""
        f0 = int(round(frame))
        n = ATTACK_TICKS * TICK                                         # 12 frames

        def pitch(f):
            """-0.5 at tick 10, -3.5 at tick 5, -0.5 at tick 0 (the game snaps to and from -0.5; here 1 frame each way)."""
            return -2.0 + 1.5 * triangle_wave(ATTACK_TICKS - (f - f0) / TICK, 10.0)

        for arm in (self.arm_r, self.arm_l):
            back = ch._val(arm, _ROT, 0, f0)
            ch._segment(arm, _ROT, 0, [(f0, None, "LINEAR"), (f0 + 1.0, pitch(f0 + 1.0), "LINEAR"),
                                       (f0 + n / 2.0, -3.5, "LINEAR"), (f0 + n - 1.0, pitch(f0 + n - 1.0), "LINEAR"),
                                       (f0 + n + 1.0, back)], "LINEAR")
        return int(math.ceil(f0 + n + 1.0))

    def swing_arm(self, frame):
        """Same as attack(): the golem has no other arm gesture in the game."""
        return self.attack(frame)

    def hold(self, obj, offset=None, rotation=None):
        """Put an object where the game puts the poppy (origin on the front of the right fist, half size); hold(None) lets go.

        The object's local +Z points straight out of the arm's front, its +X to the golem's left."""
        if self.held is not None and self.held is not obj:
            self.held.parent = None
            self.held = None
        if obj is None:
            return None
        obj.parent = self.arm_r
        obj.matrix_parent_inverse = Matrix.Identity(4)
        obj.matrix_basis = _flower_matrix()
        if offset is not None:
            obj.location = offset
        if rotation is not None:
            obj.rotation_euler = rotation
        self.held = obj
        return obj

    def crack(self, level=None):
        """Wear the game's crackiness overlay: None | 'low' | 'medium' | 'high' (health under 75 / 50 / 25 %); not keyable."""
        key, sheet = golem_sheet(level)
        mat = ch._sheet_material(key, sheet)
        for name, ob in self.parts.items():
            if ob.type == "MESH" and ob.data.materials:
                ob.data.materials[0] = mat
        self.crack_level = None if level in (None, "none") else level
        return mat


def make_iron_golem(name="golem", collection=None, crack=None):
    """Build the vanilla iron golem (2.69 tall, feet at the origin, facing -Y), its poppy hidden until offer_flower()."""
    spec = _golem_spec()
    key, sheet = golem_sheet(crack)
    col = ch._collection(collection)
    parts = ch._build_rig(name, spec, sheet, ch._sheet_material(key, sheet), col)
    return IronGolem(name, parts, spec, flower=_make_flower(name, col), crack_level=crack)


# ----------------------------------------------------------------------------------------------------
# dropped items
# ----------------------------------------------------------------------------------------------------
def _model_chain(name):
    """The raw JSON of a model and of its parents, child first (read through engine.mcassets)."""
    out = []
    cur = name
    while cur:
        cur = cur.replace("minecraft:", "")
        if cur.startswith("builtin/"):
            out.append({"builtin": cur})
            break
        try:
            raw = mc._raw_model(cur)
        except OSError:
            break
        out.append(raw)
        cur = raw.get("parent")
    return out


def _ground_display(chain):
    """display.ground of a model chain: (rotation degrees, translation in 1/16 block, scale); the nearest model that
    defines the context wins (the game's ItemTransforms resolution)."""
    for raw in chain:
        g = raw.get("display", {}).get("ground")
        if g is not None:
            return (tuple(float(c) for c in g.get("rotation", (0, 0, 0))),
                    tuple(float(c) for c in g.get("translation", (0, 0, 0))),
                    tuple(float(c) for c in g.get("scale", (1, 1, 1))))
    return ((0.0, 0.0, 0.0), (0.0, 0.0, 0.0), (1.0, 1.0, 1.0))


def _item_kind(item_id):
    """('flat', chain) for an item drawn as an extruded sprite (parent builtin/generated), else ('block', chain)."""
    chain = _model_chain("item/" + item_id)
    if any(raw.get("builtin") == "builtin/generated" for raw in chain):
        return "flat", chain
    if mc.has_blockstate(item_id):
        return "block", _model_chain("block/" + item_id)
    raise ValueError("no flat item model and no block called %r" % (item_id,))


def rendered_amount(count):
    """ItemClusterRenderState.getRenderedAmount: how many copies the game draws for a stack of `count`."""
    if count <= 1:
        return 1
    if count <= 16:
        return 2
    if count <= 32:
        return 3
    if count <= 48:
        return 4
    return 5


def _display_matrix(display):
    """ItemTransform.apply in Blender axes: translate(translation / 16), rotate X Y Z, scale. The model is centred
    on its own middle first (the game's translate(-0.5, -0.5, -0.5); the meshes here are built centred)."""
    rot, trans, scale = display
    m = (Matrix.Translation(tuple(c / 16.0 for c in trans))
         @ Matrix.Rotation(math.radians(rot[0]), 4, "X") @ Matrix.Rotation(math.radians(rot[1]), 4, "Y")
         @ Matrix.Rotation(math.radians(rot[2]), 4, "Z") @ Matrix.Diagonal((scale[0], scale[1], scale[2], 1.0)))
    to_mc = Matrix(((1, 0, 0, 0), (0, 0, 1, 0), (0, -1, 0, 0), (0, 0, 0, 1)))       # Blender (x, y, z) -> MC (x, z, -y)
    return to_mc.inverted() @ m @ to_mc


class DroppedItem:
    """An item entity: `root` (Empty on the ground), under it `spinner` (bob + spin) and the copies of the item model."""

    def __init__(self, name, item_id, kind, root, spinner, copies, hover, phase):
        self.name, self.item_id, self.kind = name, item_id, kind
        self.root, self.spinner, self.copies = root, spinner, copies
        self.sprite = copies[0]
        self.hover = hover                 # ItemEntityRenderer: -bounding box minY + 0.0625
        self.phase = phase                 # ItemEntity.bobOffs (radians)
        self.born = 1.0                    # frame at which the entity's age is 0 (of the place() / drop() keyed last)
        self.rest_pos = None
        self._shown = []                   # (frame, bool) from show()
        self._exists = []                  # (frame, bool, 'place' | 'drop' | 'pick_up')
        self._births = []                  # (frame, born): which entity age counts from which frame on
        spinner.location = (0.0, 0.0, hover + ITEM_BOB)
        spinner.rotation_euler = (0.0, 0.0, phase)

    def __repr__(self):
        return "<DroppedItem %s x%d>" % (self.item_id, len(self.copies))

    # ------------------------------------------------------------------ queries
    def objects(self):
        """All objects of the item (root first)."""
        return [self.root, self.spinner] + list(self.copies)

    def born_at(self, frame):
        """The frame at which the entity lying there at `frame` had age 0 (every place() / drop() is a new entity)."""
        births = sorted(self._births)
        born = births[0][1] if births else self.born
        for f, b in births:
            if f <= frame + 1e-6:
                born = b
        return born

    def age_at(self, frame):
        """The entity's age in game ticks at `frame`."""
        return (frame - self.born_at(frame)) / TICK

    def bob_at(self, frame, phase=None):
        """Height the game lifts the item at `frame`, above its lowest position: 0.1 * sin(age / 10 + phase) + 0.1."""
        phase = self.phase if phase is None else phase
        return ITEM_BOB * math.sin(self.age_at(frame) / ITEM_BOB_TICKS + phase) + ITEM_BOB

    def spin_at(self, frame, phase=None):
        """Rotation about the vertical at `frame` in radians: age / 20 + phase (0 = the sprite's front faces -Y)."""
        phase = self.phase if phase is None else phase
        return self.age_at(frame) / ITEM_SPIN_TICKS + phase

    def pos_at(self, frame):
        """Keyed position of the entity (the point on the ground under the item) at `frame`."""
        return Vector([ch._val(self.root, _LOC, i, frame) for i in range(3)])

    # ------------------------------------------------------------------ placement
    def place(self, frame, pos, age=40.0):
        """Rest at ground point `pos` (z = the surface: -1/16 on a dirt path) from `frame` on, `age` ticks old (hard cut)."""
        p = ch._vec3(pos)
        for i in range(3):
            ch._cut(self.root, _LOC, i, frame, p[i], hold_rest=False)
        self.born = float(frame) - float(age) * TICK
        self.rest_pos = p.copy()
        self._births.append((float(frame), self.born))
        self._exists.append((int(round(frame)), True, "place"))
        self._sync()
        return frame

    def drop(self, frame, pos, velocity=None, seed=None, rest=False):
        """Spawn the item at ground point `pos` at `frame` with the game's toss; returns the frame it lies still.

        velocity = (east, north, up) in blocks per TICK; default: the game's (+-0.1, +-0.1, 0.2) drawn from `seed`.
        rest=True: `pos` is where the item comes to rest (the spawn point is moved back by the toss). The item is
        hidden before `frame`. Call animate(frame, last_frame) afterwards for the bob and the spin.
        """
        p = ch._vec3(pos)
        if velocity is None:
            r = pix.rng(977 * (int(self._seed if seed is None else seed) + 1) + 11)
            velocity = (r.uniform(-ITEM_TOSS[0], ITEM_TOSS[0]), r.uniform(-ITEM_TOSS[0], ITEM_TOSS[0]), ITEM_TOSS[1])
        track = toss_track(velocity)
        end = Vector(track[-1][1])
        start = Vector((p.x - end.x, p.y - end.y, p.z)) if rest else p
        f0 = int(round(frame))
        still = f0 + track[-1][0] * TICK
        clash = sorted(f for f, _there, _kind in self._exists if f0 < f <= still)
        if clash:
            raise ValueError("%s.drop at frame %d is still in the air at frame %d, where a place() / drop() / "
                             "pick_up() is already keyed: its toss would wipe that out. Key an item's drops in "
                             "frame order." % (self.name, f0, clash[0]))
        for i in range(3):
            ch._cut(self.root, _LOC, i, f0, start[i], hold_rest=False)
            keys = [(f0, start[i], "LINEAR")] + [(f0 + tick * TICK, start[i] + off[i], "LINEAR") for tick, off in track[1:]]
            if len(keys) >= 2:
                ch._segment(self.root, _LOC, i, keys, "LINEAR")
        self.born = float(f0)
        self.rest_pos = start + end
        self._births.append((float(f0), self.born))
        self._exists.append((f0, True, "drop"))
        self._sync()
        return int(math.ceil(still))

    def pick_up(self, frame):
        """The item is gone from `frame` on (somebody picked it up); a later drop() brings it back."""
        self._exists.append((int(round(frame)), False, "pick_up"))
        self._sync()

    def face(self, frame, target):
        """Choose the phase so the sprite's flat side faces the point `target` at `frame`; call it before animate()."""
        t = ch._vec3(target)
        here = self.pos_at(frame)
        want = math.atan2(t.x - here.x, -(t.y - here.y))
        self.phase = (want - self.age_at(frame) / ITEM_SPIN_TICKS) % (2.0 * math.pi)
        self.spinner.rotation_euler[2] = self.phase
        return self.phase

    def animate(self, frame_start, frame_end, phase=None):
        """Key the game's bob and spin from frame_start to frame_end (the age counts from drop() / place())."""
        if phase is not None:
            self.phase = float(phase)
        f0, f1 = float(frame_start), float(frame_end)
        if f1 <= f0:
            return
        # a place() / drop() inside the range starts a new entity: its age, and so the bob and the spin, jump there
        cuts = [f0] + sorted({f for f, _born in self._births if f0 + 0.5 < f < f1 - 0.5}) + [f1]
        for a, b in zip(cuts, cuts[1:]):
            last = b - 0.5 if b < f1 else b                              # (the next cut is keyed 0.25 before b)

            def spin(f, born=self.born_at(a)):
                return (f - born) / TICK / ITEM_SPIN_TICKS + self.phase

            def lift(f, born=self.born_at(a)):
                return self.hover + ITEM_BOB * math.sin((f - born) / TICK / ITEM_BOB_TICKS + self.phase) + ITEM_BOB

            ch._cut(self.spinner, _ROT, 2, a, spin(a), hold_rest=False)
            ch._segment(self.spinner, _ROT, 2, [(a, spin(a), "LINEAR"), (last, spin(last))], "LINEAR")
            ch._cut(self.spinner, _LOC, 2, a, lift(a), hold_rest=False)
            keys = [(a, lift(a), "LINEAR")]                              # a key per frame: 1e-4 off the sine at most
            f = a + 1.0
            while f < last - 0.5:
                keys.append((f, lift(f), "LINEAR"))
                f += 1.0
            keys.append((last, lift(last)))
            ch._segment(self.spinner, _LOC, 2, keys, "LINEAR")

    def _sync(self):
        """Rendered while it is shown (show(), e.g. by a Stage per shot) AND exists (after its drop(), before pick_up())."""
        exists = sorted(self._exists)
        before = not (exists and exists[0][2] == "drop")                # dropped first: not there before the drop
        exists = [(f, v) for f, v, _kind in exists]
        frames = sorted({f for f, _v in self._shown} | {f for f, _v in exists})
        events = [(f, bool(_state_at(self._shown, f, True)) and bool(_state_at(exists, f, before))) for f in frames]
        for ob in self.copies:
            _visibility_curve(ob, events, before=before)

    def show(self, frame, visible=True):
        """Key render (and viewport) visibility of the item from `frame` on (an item is never visible before its drop())."""
        self._shown.append((int(round(frame)), bool(visible)))
        self._sync()


def toss_track(velocity, max_ticks=200):
    """ItemEntity.tick() from a spawn on the ground: [(tick, (east, north, up) offset)] until the item lies still.

    Per tick: gravity 0.04 off the vertical speed, move (the ground stops it), then horizontal speed * 0.98 in the
    air or * 0.6 * 0.98 on the ground and vertical speed * 0.98."""
    vx, vy, vz = (float(c) for c in velocity)
    x = y = z = 0.0
    out = [(0, (0.0, 0.0, 0.0))]
    for tick in range(1, max_ticks + 1):
        vz -= ITEM_GRAVITY
        x, y, z = x + vx, y + vy, z + vz
        on_ground = z <= 0.0
        if on_ground:
            z, vz = 0.0, 0.0
        f = ITEM_DRAG * (0.6 if on_ground else 1.0)
        vx, vy, vz = vx * f, vy * f, vz * ITEM_DRAG
        out.append((tick, (x, y, z)))
        if on_ground and vx * vx + vy * vy < 1e-5:
            break
    return out


def make_dropped_item(item_id, collection=None, count=1, seed=0, name=None):
    """Build a dropped item ('poppy', 'iron_ingot', ... or a block id) as the game's item entity draws it; see DroppedItem."""
    item_id = item_id.replace("minecraft:", "")
    kind, chain = _item_kind(item_id)
    display = _ground_display(chain)
    col = collection if collection is not None else ch._collection(None)
    base = name or ("drop_" + item_id)
    name, n = base, 1
    while bpy.data.objects.get(name + "_root") is not None:              # several drops of the same item
        n += 1
        name = "%s_%d" % (base, n)
    root = bpy.data.objects.new(name + "_root", None)
    root.empty_display_size = 0.2
    col.objects.link(root)
    spinner = bpy.data.objects.new(name + "_spin", None)
    spinner.empty_display_size = 0.1
    col.objects.link(spinner)
    spinner.parent = root

    if kind == "flat":
        first = mc.item_object(item_id)
        # ItemModelGenerator: the sprite fills the 16 x 16 model square, 1 pixel thick (z 7.5 .. 8.5)
        extent = [(-0.5, -1.0 / 32.0, -0.5), (0.5, 1.0 / 32.0, 0.5)]
    else:
        from .blocks import block_material

        def material_for(q):
            return block_material(q.texture, mc.block_tint(item_id, q.tintindex), shade=getattr(q, "shade", None))

        quads = mc.bake_block(item_id)
        first = mc.quads_object("item_" + item_id, quads, material_for, None, origin=(8.0, 8.0, 8.0))
        pts = [((p[0] - 8.0) / 16.0, -(p[2] - 8.0) / 16.0, (p[1] - 8.0) / 16.0) for q in quads for p in q.pts]
        extent = [tuple(min(p[i] for p in pts) for i in range(3)), tuple(max(p[i] for p in pts) for i in range(3))]
    shown = _display_matrix(display)
    corners = [shown @ Vector((extent[a][0], extent[b][1], extent[c][2])) for a in (0, 1) for b in (0, 1) for c in (0, 1)]
    min_up = min(c.z for c in corners)
    depth = max(c.y for c in corners) - min(c.y for c in corners)        # AABB.getZsize of the displayed model
    hover = -min_up + ITEM_MIN_HOVER

    copies = rendered_amount(int(count))
    r = pix.rng(1543 * (int(seed) + 1) + 29)
    offsets = [Vector((0.0, 0.0, 0.0))]
    if depth > ITEM_FLAT_DEPTH:                                          # 3-D model: the further copies are scattered
        for _i in range(1, copies):
            offsets.append(Vector(tuple(r.uniform(-1.0, 1.0) * ITEM_BUNDLE for _k in range(3))))
    else:                                                                # flat: stacked along the depth (MC z = -Y)
        gap = depth * ITEM_STACK_GAP
        offsets[0] = Vector((0.0, gap * (copies - 1) / 2.0, 0.0))
        for i in range(1, copies):
            jx, jz = (r.uniform(-1.0, 1.0) * ITEM_BUNDLE * 0.5 for _k in range(2))
            offsets.append(Vector((jx, gap * (copies - 1) / 2.0 - gap * i, jz)))
    obs = []
    for i, off in enumerate(offsets):
        ob = first if i == 0 else bpy.data.objects.new(first.name, first.data)
        ob.name = "%s_%d" % (name, i + 1)
        col.objects.link(ob)
        ob.parent = spinner
        ob.matrix_parent_inverse = Matrix.Identity(4)
        ob.matrix_basis = Matrix.Translation(off) @ shown
        ob["mc_item"] = item_id
        obs.append(ob)
    phase = float(pix.rng(7 * (int(seed) + 1) + 3).uniform(0.0, 2.0 * math.pi))    # ItemEntity.bobOffs = random * 2 pi
    item = DroppedItem(name, item_id, kind, root, spinner, obs, hover, phase)
    item._seed = int(seed)
    item.depth = depth
    return item


# ----------------------------------------------------------------------------------------------------
# does it fit? (the golem is 1.4 x 2.7 in the game, 1.625 wide over its arms in the picture)
# ----------------------------------------------------------------------------------------------------
_BOXES = {}
_SEE_THROUGH = ("short_grass", "tall_grass", "fern", "large_fern", "poppy", "dandelion", "oxeye_daisy", "cornflower",
                "azure_bluet", "allium", "wheat", "carrots", "potatoes", "beetroots")


def _block_box(block_id, props):
    """Bounding box of a block state's model in block units (Blender axes): ((x0, y0, z0), (x1, y1, z1))."""
    key = (block_id, tuple(sorted((props or {}).items())))
    if key not in _BOXES:
        pts = [mc.to_blender(p) for q in mc.bake_block(block_id, dict(props or {})) for p in q.pts]
        if not pts:
            _BOXES[key] = None
        else:
            _BOXES[key] = (tuple(min(p[i] for p in pts) for i in range(3)), tuple(max(p[i] for p in pts) for i in range(3)))
    return _BOXES[key]


def clearance(village, points, width=GOLEM_WIDTH, height=GOLEM_HEIGHT, step=0.25, foot=0.55):
    """Where a width x width x height box moved along the polyline `points` touches the set: [(x, y, z, block id)].

    `village` is a Village (or a blocks.World). Blocks whose model reaches into the box count, torches and lanterns
    included (the golem's head would go through them); plants and crops do not, and nothing lower than `foot`
    above the walking surface does (path blocks, slabs, the step of a door). Empty list = the golem fits."""
    w = getattr(village, "world", village)
    half = width / 2.0
    hits, seen = [], set()
    pts = [tuple(float(c) for c in p) for p in points]
    if len(pts) == 1:
        pts = pts * 2
    for a, b in zip(pts[:-1], pts[1:]):
        n = max(1, int(math.dist(a, b) / step))
        for i in range(n + 1):
            t = i / n
            x, y, z = (a[k] + (b[k] - a[k]) * t for k in range(3))
            lo = (x - half, y - half, z + foot)
            hi = (x + half, y + half, z + height)
            for cx in range(int(math.floor(lo[0])), int(math.floor(hi[0])) + 1):
                for cy in range(int(math.floor(lo[1])), int(math.floor(hi[1])) + 1):
                    for cz in range(int(math.floor(lo[2])), int(math.floor(hi[2])) + 1):
                        st = w.get(cx, cy, cz)
                        if st is None or st[0] in _SEE_THROUGH or (cx, cy, cz) in seen:
                            continue
                        box = _block_box(st[0], st[1])
                        if box is None:
                            continue
                        cell = (cx, cy, cz)
                        if all(cell[k] + box[0][k] < hi[k] - 1e-6 and cell[k] + box[1][k] > lo[k] + 1e-6 for k in range(3)):
                            seen.add(cell)
                            hits.append((cx, cy, cz, st[0]))
    return hits


# ----------------------------------------------------------------------------------------------------
# self-test
# ----------------------------------------------------------------------------------------------------
def _set(scene, path=None, wall=None, half=14, paths=()):
    """A little set from the real block models: grass, optionally a dirt-path strip (x range), further dirt-path
    rectangles `paths` = [(x0, y0, x1, y1)] and a block wall."""
    from .blocks import World, new_collection

    w = World()
    w.fill(-half, -half, -1, half, half, -1, "grass_block")
    if path is not None:
        w.fill(path[0], -half, -1, path[1], half, -1, "dirt_path")
    for x0, y0, x1, y1 in paths:
        w.fill(x0, y0, -1, x1, y1, -1, "dirt_path")
    if wall is not None:                                                 # one block kind per 1-block layer: a height scale
        (x0, y0, x1, y1), layers = wall
        for z, block in enumerate(layers):
            w.fill(x0, y0, z, x1, y1, z, block)
    w.cull_below = -1
    coll = new_collection(scene, "set")
    w.build(coll)
    return w


def _evaluate(scene, frame):
    whole = int(math.floor(frame))
    scene.frame_set(whole, subframe=float(frame) - whole)
    bpy.context.view_layer.update()


def _check():
    """Numbers only: the model's size, the gait, the offer pose, the flower's place, the item's bob and spin."""
    from . import quick

    scene = quick.reset()
    g = make_iron_golem("probe")
    scene.frame_set(1)
    bpy.context.view_layer.update()

    # ---- size, straight from the vertices
    lo, hi = Vector((1e9,) * 3), Vector((-1e9,) * 3)
    for ob in g.parts.values():
        if ob.type != "MESH":
            continue
        for v in ob.data.vertices:
            p = ob.matrix_world @ v.co
            lo = Vector(map(min, lo, p))
            hi = Vector(map(max, hi, p))
    print("golem bounds x %.4f..%.4f  y %.4f..%.4f  z %.4f..%.4f" % (lo.x, hi.x, lo.y, hi.y, lo.z, hi.z))
    assert abs(hi.z - MODEL_HEIGHT) < 1e-4 and abs(lo.z) < 1e-4, "golem must stand 43 px tall on z = 0"
    assert abs(hi.x - 13 / 16) < 1e-4 and abs(lo.x + 13 / 16) < 1e-4, "golem must be 26 px wide over the arms"
    assert abs(lo.y + 7.5 / 16 - (-2 / 16)) < 1e-4, "nose tip must be 9.5 px in front of the centre line"
    assert abs(g.height - MODEL_HEIGHT) < 1e-6 and abs(g.eye_height - GOLEM_EYE_HEIGHT) < 1e-6
    faces = sum(len(o.data.polygons) for o in g.parts.values() if o.type == "MESH")
    print("golem faces", faces, "| walk speed %.4f  chase %.4f blocks/s" % (WALK_SPEED, CHASE_SPEED))
    assert abs(WALK_SPEED - 0.9912) < 1e-3 and abs(CHASE_SPEED - 2.2302) < 1e-3
    assert g.arm_r.rotation_euler[1] == 0.0 and g.arm_l.rotation_euler[1] == 0.0

    # ---- triangle wave
    assert triangle_wave(0.0, 13.0) == 1.0 and abs(triangle_wave(3.25, 13.0)) < 1e-9 and triangle_wave(6.5, 13.0) == -1.0

    # ---- vanilla gait: the game's own numbers at the game's walking speed
    g.place(1, (0.0, 0.0, 0.0), math.radians(-90))                      # walking toward -X ... yaw -90 faces -X
    end = g.walk(1, [(0.0, 0.0, 0.0), (-13.0, 0.0, 0.0)], gait="vanilla", ramp=0)
    info = g.last_walk
    print("vanilla walk:", _brief_walk(info))
    s = WALK_SPEED / 5.0
    assert abs(info["swing"] - 1.5 * s) < 1e-3 and abs(info["cycle_blocks"] - 3.25) < 1e-9
    assert abs(info["cycle_frames"] - 13.0 / s * TICK) < 0.5, "one cycle = 13 / s ticks"
    worst = 0.0
    for f in np.arange(2.0, end, 0.37):                                 # (frame 1 -> 2: the limbs join the curve)
        _evaluate(scene, f)
        d = -g.root.location.x
        p = ANIM_PER_BLOCK * d
        want = (-1.5 * s * _wave(p), 1.5 * s * _wave(p), (-0.2 + 1.5 * _wave(p)) * s, (-0.2 - 1.5 * _wave(p)) * s,
                math.radians(6.5) * _wave(p + 6.0))
        got = (g.leg_r.rotation_euler.x, g.leg_l.rotation_euler.x, g.arm_r.rotation_euler.x, g.arm_l.rotation_euler.x,
               g.root.rotation_euler.y)
        worst = max(worst, max(abs(a - b) for a, b in zip(want, got)))
        assert abs(d - WALK_SPEED * (f - 1.0) / FPS) < 0.02
    print("vanilla gait: worst deviation from IronGolemModel.setupAnim %.5f rad over %d frames" % (worst, end - 1))
    assert worst < 2e-3
    slip, _range = _foot_slip(g, 1, end)
    print("vanilla gait: stance foot slides %.3f blocks per step (the game's own slide: 1.625 - 2 * leg * sin(swing) = %.3f)"
          % (slip, 1.625 - 2.0 * LEG_LENGTH * math.sin(info["swing"])))
    assert abs(slip - (1.625 - 2.0 * LEG_LENGTH * math.sin(info["swing"]))) < 0.03

    # ---- planted gait: the feet stay where they are put
    g2 = make_iron_golem("probe2")
    g2.place(1, (0.0, 3.0, 0.0), math.radians(-90))
    end2 = g2.walk(1, [(0.0, 3.0, 0.0), (-9.0, 3.0, 0.0)])
    info = g2.last_walk
    print("planted walk:", _brief_walk(info))
    assert abs(info["speed"] - WALK_SPEED) < 0.03 and abs(info["swing"] - PLANTED_SWING) < 0.06
    slip2, range2 = _foot_slip(g2, 1, end2)
    print("planted gait: stance foot ends a step %.4f blocks from where it was put, never more than %.4f away"
          % (slip2, range2))
    assert slip2 < 0.005 and range2 < 0.01, "planted feet must not slide"
    for ob, idx in ((g2.leg_r, 0), (g2.leg_l, 0), (g2.arm_r, 0), (g2.arm_l, 0)):
        keys = ch.read_keys(ob, _ROT, idx)
        assert keys[-1][2] == "CONSTANT" and abs(keys[-1][1]) < 1e-6, "limbs must end the walk neutral and hold"
    roll = ch.read_keys(g2.root, _ROT, 1)
    assert max(abs(k[1]) for k in roll) <= math.radians(6.5) + 1e-5 and abs(roll[-1][1]) < 1e-6
    assert max(abs(k[1]) for k in roll) > math.radians(6.0)
    _evaluate(scene, end2 + 5)
    assert abs(g2.root.location.x + 9.0) < 1e-4 and abs(g2.root.rotation_euler.y) < 1e-6
    first = ch.read_keys(g2.root, _LOC, 0)[0]
    assert first[2] == "CONSTANT" and abs(first[0] - (1 - ch.CUT_LEAD)) < 1e-6, "place() is a CONSTANT key CUT_LEAD early"
    g2.place(end2 + 20, (5.0, 5.0, 0.0), 0.0)
    _evaluate(scene, end2 + 20)
    assert abs(g2.root.rotation_euler.y) < 1e-9 and abs(g2.leg_l.rotation_euler.x) < 1e-9

    # ---- head limits
    g3 = make_iron_golem("probe3")
    g3.place(1, (0.0, -6.0, 0.0), 0.0)
    g3.look_at(1, (-10.0, -5.0, 30.0), ease=0)
    _evaluate(scene, 1)
    assert abs(abs(g3.head.rotation_euler.z) - HEAD_YAW_MAX) < 1e-5 and abs(abs(g3.head.rotation_euler.x) - HEAD_PITCH_MAX) < 1e-5

    # ---- flower offer
    f1 = g3.offer_flower(10, ease=8)
    g3.offer_flower(100, on=False, ease=8)
    hidden, size = {}, {}
    for f in (1, 9, 10, 11, 12, 14, 18, 60, 99, 100, 104, 106, 107, 107.49, 108, 110):
        _evaluate(scene, f)
        hidden[f] = bool(g3.flower.hide_render)
        size[f] = round(g3.flower.scale[0] / 0.5, 3)
    print("flower hidden by frame:", hidden)
    print("flower size by frame (1 = the game's half-size block):", size)
    assert hidden[9] and not hidden[10] and not hidden[99] and not hidden[107] and hidden[108]
    # an eased raise: the poppy grows out of the fist over FLOWER_GROW frames, an eased lowering takes it back in
    assert size[10] <= 0.002 and abs(size[12] - 0.5) < 0.01 and size[14] == 1.0 and size[60] == 1.0 and size[104] == 1.0
    assert abs(size[106] - 0.5) < 0.01 and size[107.49] < 0.14, "it must be all but gone when the last exposure closes"
    assert g3.offering_at(50) and not g3.offering_at(100) and g3.flower_at(107) and not g3.flower_at(108)
    _evaluate(scene, 10)
    seen = (g3.flower.matrix_world @ Vector((0.0, 0.0, 9.0 / 16.0)) - g3.flower.matrix_world.translation).length
    assert seen < 0.001, "on the first frame of an eased raise the poppy must still be inside the fist (%.4f)" % seen
    bloom = g3.flower_point(10)                                         # (the bloom's place does not shrink with it)
    assert (bloom - g3.flower.matrix_world.translation).length > 0.25
    _evaluate(scene, f1)
    tick = OFFER_TICKS - (f1 - 10) / TICK
    want = OFFER_ARM_PITCH + OFFER_WOBBLE * triangle_wave(tick % 70.0, 70.0)
    assert abs(g3.arm_r.rotation_euler.x - want) < 1e-5 and abs(g3.arm_l.rotation_euler.x) < 1e-6
    worst = 0.0
    for f in np.arange(f1, 99.0, 0.61):
        _evaluate(scene, f)
        tick = OFFER_TICKS - (f - 10) / TICK
        worst = max(worst, abs(g3.arm_r.rotation_euler.x - (OFFER_ARM_PITCH + OFFER_WOBBLE * triangle_wave(tick % 70.0, 70.0))))
    print("offer pose: worst deviation from -0.8 + 0.025 * triangleWave(tick, 70): %.6f rad" % worst)
    assert worst < 1e-4
    _evaluate(scene, 110)
    assert abs(g3.arm_r.rotation_euler.x) < 1e-6
    # the flower's place, computed a second way: straight from the layer's numbers in arm pixels
    # (block point (bx, by, bz) -> arm pixels (-11 + 8 (bx - 0.5), 25 + 8 (bz - 0.5), -3 - 8 by))
    _evaluate(scene, 60)
    arm = g3.arm_r.matrix_world
    for block, _note in (((0.5, 0.0, 0.5), "stem base"), ((0.5, 1.0, 0.5), "top"), ((1.0, 0.5, 0.0), "corner")):
        px = (-11.0 + 8.0 * (block[0] - 0.5), 25.0 + 8.0 * (block[2] - 0.5), -3.0 - 8.0 * block[1])
        want = arm @ Vector((px[0] / 16.0, px[2] / 16.0, -px[1] / 16.0))
        local = Vector((block[0] - 0.5, -(block[2] - 0.5), block[1]))
        got = g3.flower.matrix_world @ local
        assert (want - got).length < 1e-5, (block, tuple(want), tuple(got))
    base = g3.flower.matrix_world.translation
    tip = g3.flower_point(60)
    stem = (tip - base).normalized()
    print("flower at frame 60: stem base", tuple(round(c, 3) for c in base), "bloom", tuple(round(c, 3) for c in tip),
          "| points %.1f degrees above the horizon" % math.degrees(math.asin(stem.z)))
    # a show(False) hides the flower too, and showing the golem again does not bring a lowered flower back
    g3.offer_flower(130, ease=0)
    g3.show(140, False)
    g3.show(150, True)
    g3.place(160, (0.0, -6.0, 0.0), 0.0)
    for f, want in ((129, True), (130, False), (140, True), (150, False), (160, True)):
        _evaluate(scene, f)
        assert bool(g3.flower.hide_render) == want, ("flower visibility", f)
    _evaluate(scene, 130)
    assert abs(g3.arm_r.rotation_euler.x - (OFFER_ARM_PITCH + OFFER_WOBBLE * triangle_wave(400 % 70, 70.0))) < 1e-6
    assert abs(g3.flower.scale[0] - 0.5) < 1e-6, "ease=0 is the game's snap: the poppy is there at full size"
    scene.frame_set(129, subframe=ch.SHUTTER)
    assert abs(g3.arm_r.rotation_euler.x) < 1e-6, "a snapped pose must not show in the exposure of the frame before"

    # ---- keyed out of order: a walk that would run through an offer keyed earlier in the script must say so
    g5 = make_iron_golem("probe5")
    g5.place(50, (20.0, 0.0, 0.0), 0.0)
    g5.offer_flower(50, ease=0)
    g5.place(40, (20.0, 6.0, 0.0), 0.0)
    try:
        g5.walk(40, [(20.0, 6.0, 0.0), (20.0, 1.0, 0.0)])
    except ValueError as err:
        print("walk through an earlier-keyed offer is refused:", str(err)[:96], "...")
    else:
        raise AssertionError("a walk keyed through an offer must raise")
    _evaluate(scene, 60)
    assert abs(g5.arm_r.rotation_euler.x - OFFER_ARM_PITCH) < 0.03 and not g5.flower.hide_render, "the refused walk changed nothing"
    assert (g5.root.location - Vector((20.0, 0.0, 0.0))).length < 1e-6
    # ... while the offer DURING a walk (walk keyed first) holds the arm in the pose, flower in hand
    g6 = make_iron_golem("probe6")
    g6.place(40, (24.0, 6.0, 0.0), 0.0)
    e6 = g6.walk(40, [(24.0, 6.0, 0.0), (24.0, 1.0, 0.0)])
    g6.offer_flower(60, ease=8)
    for f in (70, 100, e6 - 2):
        _evaluate(scene, f)
        assert abs(g6.arm_r.rotation_euler.x - OFFER_ARM_PITCH) < 0.03 and abs(g6.arm_l.rotation_euler.x) < 1e-6
        assert not g6.flower.hide_render and abs(g6.leg_l.rotation_euler.x) + abs(g6.leg_r.rotation_euler.x) > 0.0
    e7 = g6.walk(e6, [(24.0, 1.0, 0.0), (24.0, -3.0, 0.0)])            # a second walk while offering: arms stay
    _evaluate(scene, (e6 + e7) // 2)
    assert abs(g6.arm_r.rotation_euler.x - OFFER_ARM_PITCH) < 0.03 and not g6.flower.hide_render

    # ---- attack
    e = g3.attack(200)
    _evaluate(scene, 200 + 5 * TICK)
    assert abs(g3.arm_r.rotation_euler.x + 3.5) < 1e-5 and abs(g3.arm_l.rotation_euler.x + 3.5) < 1e-5
    _evaluate(scene, e)
    assert abs(g3.arm_r.rotation_euler.x) < 1e-6

    # ---- dropped items
    for item_id in ("poppy", "iron_ingot"):
        it = make_dropped_item(item_id, seed=3)
        assert it.kind == "flat" and abs(it.hover - 0.1875) < 1e-9, (item_id, it.kind, it.hover)
        it.place(1, (2.0, 2.0, -0.0625), age=0.0)
        it.animate(1, 200)
        worst_bob = worst_spin = 0.0
        lowest = 9.0
        for f in np.arange(1.0, 200.0, 0.5):
            _evaluate(scene, f)
            age = (f - 1.0) / TICK
            bob = 0.1 * math.sin(age / 10.0 + it.phase) + 0.1
            centre = it.sprite.matrix_world.translation.z - (-0.0625)
            worst_bob = max(worst_bob, abs(centre - (0.3125 + bob)))
            worst_spin = max(worst_spin, abs(it.spinner.rotation_euler.z - (age / 20.0 + it.phase)))
            zs = [(it.sprite.matrix_world @ v.co).z for v in it.sprite.data.vertices]
            lowest = min(lowest, min(zs) - (-0.0625))
        print("%s: bob error %.6f, spin error %.6f, lowest texel %.4f above the ground, scale %s"
              % (item_id, worst_bob, worst_spin, lowest, tuple(round(c, 3) for c in it.sprite.matrix_world.to_scale())))
        assert worst_bob < 5e-4 and worst_spin < 1e-5 and lowest >= 0.0625 - 1e-4
    track = toss_track((0.05, 0.0, 0.2))
    apex = max(off[2] for _t, off in track)
    land = next(t for t, off in track[1:] if off[2] == 0.0)
    print("toss: apex %.4f blocks, lands at tick %d, rests %.3f from the spawn point after %d ticks"
          % (apex, land, track[-1][1][0], track[-1][0]))
    assert abs(apex - 0.3842) < 2e-3 and land == 9
    it = make_dropped_item("poppy", seed=5, count=2)
    assert len(it.copies) == 2 and abs(it.depth - 1.0 / 32.0) < 1e-9
    rest = it.drop(20, (4.0, 4.0, 0.0), rest=True)
    it.animate(20, 120)
    _evaluate(scene, rest)
    assert (it.root.location - Vector((4.0, 4.0, 0.0))).length < 1e-4
    _evaluate(scene, 19)
    assert it.sprite.hide_render
    _evaluate(scene, 20)
    assert not it.sprite.hide_render
    it.face(60, (4.0, -6.0, 1.0))
    it.animate(20, 120)
    _evaluate(scene, 60)
    normal = it.sprite.matrix_world.to_3x3() @ Vector((0.0, -1.0, 0.0))
    assert normal.normalized().y < -0.999, "face() must turn the sprite's front to the target"
    it2 = make_dropped_item("iron_ingot", name="twice")
    it2.place(10, (6.0, 6.0, 0.0))
    it2.pick_up(40)
    it2.drop(80, (7.0, 7.0, 0.0))
    for f, hidden in ((5, False), (10, False), (39, False), (40, True), (79, True), (80, False)):
        _evaluate(scene, f)
        assert bool(it2.sprite.hide_render) == hidden, ("item visibility", f)
    blk = make_dropped_item("iron_block")
    assert blk.kind == "block" and abs(blk.hover) < 1e-9 and abs(blk.sprite.matrix_basis.to_scale().x - 0.25) < 1e-6
    # shots keyed out of order: every place() / drop() is its own entity, whatever the order of the calls
    it3 = make_dropped_item("poppy", name="order")
    it3.place(100, (8.0, 8.0, 0.0), age=30.0)
    it3.drop(20, (9.0, 9.0, 0.0), velocity=(0.0, 0.0, 0.2))
    assert abs(it3.age_at(110) - (30.0 + 10.0 / TICK)) < 1e-6 and abs(it3.age_at(26) - 5.0) < 1e-6
    it3.animate(20, 160)
    for f in (30.0, 99.0, 100.0, 130.0):
        _evaluate(scene, f)
        age = it3.age_at(f)
        assert abs(it3.spinner.rotation_euler.z - (age / 20.0 + it3.phase)) < 1e-4, ("spin across a second entity", f)
        assert abs(it3.spinner.location.z - (it3.hover + 0.1 * math.sin(age / 10.0 + it3.phase) + 0.1)) < 5e-4
    assert (it3.pos_at(100) - Vector((8.0, 8.0, 0.0))).length < 1e-6 and (it3.pos_at(60) - Vector((9.0, 9.0, 0.0))).length < 1e-6
    try:
        it3.drop(90, (8.0, 9.0, 0.0))
    except ValueError as err:
        print("a toss that would wipe out a later place() is refused:", str(err)[:80], "...")
    else:
        raise AssertionError("a drop whose toss runs into a keyed place() must raise")

    # ---- a walk round a corner, a run, an idle
    g4 = make_iron_golem("probe4")
    g4.place(300, (0.0, 20.0, 0.0), 0.0)
    e4 = g4.walk(300, [(0.0, 20.0, 0.0), (0.0, 16.0, 0.0), (5.0, 16.0, 0.0)])
    _evaluate(scene, e4)
    assert (g4.root.location - Vector((5.0, 16.0, 0.0))).length < 1e-5
    assert abs(g4.root.rotation_euler.z - math.radians(90)) < 1e-5 and abs(g4.root.rotation_euler.y) < 1e-6
    assert abs(g4.leg_l.rotation_euler.x) < 1e-6 and abs(g4.arm_r.rotation_euler.x) < 1e-6
    turn = [k for k in ch.read_keys(g4.root, _ROT, 2) if 300 < k[0] < e4]
    info = g4.last_walk
    print("corner: %.2f blocks in %d frames, arcs (radius, degrees) %s, the turn is keyed over frames %.1f-%.1f"
          % (info["blocks"], e4 - 300, info["corners"], turn[0][0], turn[-1][0]))
    assert info["corners"] == [(1.0, 90.0)] and not info["sharp"] and abs(info["blocks"] - (9.0 - 2.0 + math.pi / 2)) < 1e-6
    stray, off = _sole_stray(scene, g4, 300, e4), 0.0
    line = [Vector(q) for q in rounded([(0.0, 20.0, 0.0), (0.0, 16.0, 0.0), (5.0, 16.0, 0.0)], step=0.02)]
    for f in range(300, e4 + 1):
        here = g4.pos_at(f)
        off = max(off, min((here - q).length for q in line))
    print("corner: the planted sole strays at most %.4f block over the ground (it turns on the spot); the body stays "
          "within %.3f block of the rounded line" % (stray, off))
    assert stray < 0.06 and off < 0.12
    assert max(abs(k[1]) for k in ch.read_keys(g4.leg_l, _ROT, 0) + ch.read_keys(g4.leg_r, _ROT, 0)) < 0.75
    # corner=0: the old sharp vertex, turned on the spot over 10 frames (the feet skate there, as documented)
    g7 = make_iron_golem("probe7")
    g7.place(300, (10.0, 20.0, 0.0), 0.0)
    e7 = g7.walk(300, [(10.0, 20.0, 0.0), (10.0, 16.0, 0.0), (15.0, 16.0, 0.0)], corner=0)
    assert g7.last_walk["sharp"] == [90.0] and not g7.last_walk["corners"] and abs(g7.last_walk["blocks"] - 9.0) < 1e-9
    assert (g7.pos_at(300 + round(4.0 / 9.0 * (e7 - 300))) - Vector((10.0, 16.0, 0.0))).length < 0.06, "it passes through the vertex"
    print("corner=0: sharp vertex, sole strays %.3f block" % _sole_stray(scene, g7, 300, e7))
    # a U-turn and a corner between two short legs cannot be rounded: they stay sharp instead of failing
    g7.place(600, (10.0, 20.0, 0.0), 0.0)
    e7 = g7.walk(600, [(10.0, 20.0, 0.0), (10.0, 17.0, 0.0), (10.0, 20.0, 0.0), (10.1, 20.0, 0.0), (10.1, 19.0, 0.0)])
    _evaluate(scene, e7)
    assert (g7.root.location - Vector((10.1, 19.0, 0.0))).length < 1e-5 and abs(ch._wrap(g7.root.rotation_euler.z)) < 1e-5
    print("u-turn path: arcs", g7.last_walk["corners"], "sharp", g7.last_walk["sharp"])
    # ramp=(0, 8): in stride from the first frame, braking at the end
    g7.place(900, (10.0, 20.0, 0.0), 0.0)
    e7 = g7.walk(900, [(10.0, 20.0, 0.0), (10.0, 14.0, 0.0)], ramp=(0, 8))
    first_step = (g7.pos_at(901) - g7.pos_at(900)).length * FPS
    last_step = (g7.pos_at(e7) - g7.pos_at(e7 - 1)).length * FPS
    slip7, range7 = _foot_slip(g7, 900, e7)
    print("ramp=(0, 8): %.3f blocks/s on the first frame, %.3f on the last; slip %.4f / %.4f" % (first_step, last_step, slip7, range7))
    assert abs(first_step - g7.last_walk["speed"]) < 1e-3 and last_step < 0.1 and slip7 < 0.005 and range7 < 0.01
    # a path that climbs: z follows the polyline, also round the arc
    g7.place(1200, (10.0, 20.0, 0.0), 0.0)
    e7 = g7.walk(1200, [(10.0, 20.0, 0.0), (10.0, 16.0, 0.5), (14.0, 16.0, 1.0)])
    zs = [g7.pos_at(f).z for f in range(1200, e7 + 1)]
    assert all(b >= a - 1e-6 for a, b in zip(zs, zs[1:])) and abs(zs[-1] - 1.0) < 1e-6 and abs(zs[0]) < 1e-6
    e5 = g4.walk(e4, [(5.0, 16.0, 0.0), (17.0, 16.0, 0.0)], run=True)
    info = g4.last_walk
    slip5, range5 = _foot_slip(g4, e4, e5)
    print("run:", _brief_walk(info), "slip %.4f / %.4f" % (slip5, range5))
    assert abs(info["speed"] - CHASE_SPEED) < 0.08 and slip5 < 0.005 and range5 < 0.01
    g4.idle(e5, e5 + 240, seed=4)
    yaws = [k[1] for k in ch.read_keys(g4.head, _ROT, 2)]
    assert len(yaws) > 4 and max(abs(a) for a in yaws) <= HEAD_YAW_MAX + 1e-6 and abs(yaws[-1]) < 1e-6

    # ---- the crumbs a walking golem kicks up (Entity.spawnSprintParticle), through engine.fx
    cam = bpy.data.objects.new("probe_cam", bpy.data.cameras.new("probe_cam"))
    scene.collection.objects.link(cam)
    burst = g4.step_crumbs(300, e5 + 60, cam, seed=2)                   # the corner walk, the run, and 60 frames at rest
    ticks = int((e5 - 300) / TICK)
    spawns = [part["spawn"] for part in burst.particles]
    print("crumbs: %d in %d ticks of walking (the game: 1 in %d), none after frame %d; lifetimes %d-%d ticks, sizes %.3f-%.3f"
          % (len(spawns), ticks, CRUMB_CHANCE, e5, min(p["lifetime"] for p in burst.particles),
             max(p["lifetime"] for p in burst.particles), 2 * min(p["size"] for p in burst.particles),
             2 * max(p["size"] for p in burst.particles)))
    assert abs(len(spawns) - ticks / CRUMB_CHANCE) < 3.0 * math.sqrt(ticks * 0.2 * 0.8), "about one tick in five"
    assert max(spawns) <= e5 + TICK, "a golem at rest kicks up nothing"
    for part in burst.particles:
        here = g4.pos_at(part["spawn"])
        start = Vector(part["pos"][0])
        assert abs(start.x - here.x) <= GOLEM_WIDTH / 2 + 1e-6 and abs(start.y - here.y) <= GOLEM_WIDTH / 2 + 1e-6
        assert abs(start.z - (here.z + CRUMB_LIFT)) < 1e-6 and min(q[2] for q in part["pos"]) >= here.z - 1e-6
    clipped = g4.step_crumbs(300, 340, cam, seed=3)
    assert clipped.objects and clipped.frame_end <= 339
    for f in (339, 340, 341, 360):
        _evaluate(scene, f)
        shown = sum(1 for ob in clipped.objects if not ob.hide_render)
        assert (f < 340) or shown == 0, "no crumb may outlive frame_end"
    # a dirt path's particle texture is its side (template_cube_bottom_top_indented: particle = #side); a grass
    # block's is plain dirt, and it is NOT tinted green (BlockTintSources.grassBlock().colorAsTerrainParticle = -1)
    assert clipped.objects[0].data.materials[0]["mc_texture"] == "block/dirt_path_side"
    assert g4._crumb_block("grass_block", None).particle_texture == ("block/dirt", None)

    # ---- with films.lookdev.Stage: hidden outside its shots, the poppy only while offered, the item only once dropped
    from films.lookdev import Stage

    from . import shots

    class _NoSet:
        lantern_lights, cutaways = [], {}

    film = shots.Film(scene, fps=24)
    st = Stage(scene, film, _NoSet(), None)
    s1, s2, s3 = st.shot("patrol", 1.0), st.shot("empty", 1.0), st.shot("found", 1.0)
    gs = make_iron_golem("stage_golem")
    st.cast["stage_golem"] = gs
    drop = make_dropped_item("poppy", name="stage_poppy")
    st.cast[drop.name] = drop
    gs.place(s1.frame_start, (0.0, 30.0, 0.0), 0.0)
    gs.offer_flower(s1.frame_start, ease=0)
    st.use(s1, gs)
    drop.drop(s3.frame_start + 6, (0.0, 31.0, 0.0), rest=True)
    drop.animate(s3.frame_start + 6, s3.frame_end + 1)
    st.use(s2, drop)                                                    # declared, but it is not dropped yet
    st.use(s3, drop)
    st.hero(s1, "golem", gs)
    st.hero(s3, "poppy", drop.sprite)
    st.finish()
    seen = {}
    for f in (s1.frame_start, s1.frame_end, s2.frame_start, s3.frame_start, s3.frame_start + 5, s3.frame_start + 6, s3.frame_end):
        _evaluate(scene, f)
        seen[f] = (not gs.head.hide_render, not gs.flower.hide_render, not drop.sprite.hide_render)
    print("stage (golem, its poppy, dropped poppy) visible by frame:", seen)
    assert seen[s1.frame_start] == (True, True, False) and seen[s1.frame_end] == (True, True, False)
    assert seen[s2.frame_start] == (False, False, False) and seen[s3.frame_start + 5] == (False, False, False)
    assert seen[s3.frame_start + 6] == (False, False, True) and seen[s3.frame_end] == (False, False, True)
    scene.frame_set(1)
    print("check ok")


def _brief_walk(info):
    """last_walk without its long 'path' entry, floats rounded (for printing)."""
    return {k: (round(v, 4) if isinstance(v, float) else v) for k, v in info.items() if k != "path"}


def _sole_stray(scene, golem, f0, f1, step=0.25):
    """How far the sole that is on the ground strays over it, in world space on the evaluated rig (roll, ramps and
    corners included): the largest distance of a stance sole's centre from where its step began."""
    centres = {}
    for name, leg in (("l", golem.leg_l), ("r", golem.leg_r)):
        low = min(v.co.z for v in leg.data.vertices)
        pts = [v.co for v in leg.data.vertices if v.co.z < low + 1e-5]
        centres[name] = sum(pts, Vector()) / len(pts)
    rows = []
    for f in np.arange(float(f0), float(f1) + 1e-6, step):
        _evaluate(scene, f)
        rows.append({name: (leg.matrix_world @ centres[name]).xy.copy() for name, leg in (("l", golem.leg_l), ("r", golem.leg_r))})
    worst, stance, start = 0.0, None, None
    for a, b in zip(rows, rows[1:]):
        moved = {name: (b[name] - a[name]).length for name in ("l", "r")}
        if moved["l"] + moved["r"] < 1e-7:
            continue
        now = "l" if moved["l"] < moved["r"] else "r"
        if now != stance:
            stance, start = now, a[now]
        worst = max(worst, (b[now] - start).length)
    return worst


def _foot_slip(golem, f0, f1, step=0.02):
    """How far the stance foot (the one moving backward against the body) travels over the ground on a straight
    walk, read from the keys: (median blocks per step, largest back-and-forth range within one step).
    Along the walk a sole is at (distance covered) - leg * sin(leg angle); the roll does not move it that way."""
    start = golem.pos_at(f0)
    prev, stance, track, steps = None, None, [], []
    for f in np.arange(float(f0), float(f1) + 1e-6, step):
        body = (golem.pos_at(f) - start).length
        feet = {n: body - LEG_LENGTH * math.sin(ch._val(ob, _ROT, 0, f)) for n, ob in (("l", golem.leg_l), ("r", golem.leg_r))}
        if prev is not None:
            rel = {n: (feet[n] - body) - (prev[0][n] - prev[1]) for n in feet}
            if abs(rel["l"] - rel["r"]) > 1e-9:
                now = min(rel, key=rel.get)                             # moving backward relative to the body
                if now != stance:
                    if len(track) > 4:
                        steps.append(track)
                    stance, track = now, [prev[0][now]]
                track.append(feet[now])
        prev = (feet, body)
    if len(track) > 4:
        steps.append(track)
    steps = steps[1:-1] if len(steps) > 3 else steps                    # whole steps only
    net = sorted(abs(t[-1] - t[0]) for t in steps)
    return net[len(net) // 2], max(max(t) - min(t) for t in steps)


def _selftest(which):
    import os

    from . import quick

    def want(name):
        return (not which and name not in ("walk_vanilla", "raise", "corner", "crumbs")) or name in which

    def stage(preset="golden", res=(540, 960), blur=False, **kw):
        scene = quick.reset()
        quick.setup(scene, res=res)
        sun = quick.light(scene, preset)
        if preset == "day":
            sun.data.energy = 2.6                                        # the iron is nearly white: keep its texels
        if blur:                                                         # the films' shutter (look.setup_render)
            scene.render.use_motion_blur = True
            scene.render.motion_blur_shutter = 0.5
            scene.render.motion_blur_position = "START"
        stage.world = _set(scene, **kw)
        return scene

    def sheet(name, paths, height=480):
        """The stills side by side in one picture (for a quick look at a sequence)."""
        from PIL import Image

        ims = [Image.open(q).convert("RGB") for q in paths]
        ims = [im.resize((int(im.width * height / im.height), height), Image.LANCZOS) for im in ims]
        out = Image.new("RGB", (sum(im.width for im in ims) + 4 * (len(ims) - 1), height), (20, 20, 24))
        x = 0
        for im in ims:
            out.paste(im, (x, 0))
            x += im.width + 4
        path = os.path.join(quick.TEST_DIR, name + ".png")
        out.save(path)
        print("wrote", path)

    if want("check"):
        _check()

    if want("lineup"):
        scene = stage("day", wall=((-4, 2, 7, 2), ("stone_bricks", "oak_planks", "stone_bricks", "oak_planks")))
        g = make_iron_golem("golem")
        v = ch.make_villager("farmer", "farmer")
        k = ch.make_villager("kid", "none", child=True)
        s = ch.make_player("steve")
        g.place(1, (0.0, 0.0, 0.0), 0.0)
        v.place(1, (1.5, 0.0, 0.0), 0.0)
        k.place(1, (2.45, 0.0, 0.0), 0.0)
        s.place(1, (3.4, 0.0, 0.0), 0.0)
        scene.frame_set(1)
        scene.objects["quick_sun"].rotation_euler[2] = math.radians(-25)
        quick.camera(scene, (1.2, -17.0, 1.9), (1.55, 0.0, 1.6), lens=40)
        print("wrote", quick.render(scene, "mobs_lineup"))

    if want("turn"):
        scene = stage("day")
        g = make_iron_golem("golem")
        for n, (label, yaw, sun) in enumerate((("front", 0, -20), ("side", 90, -20), ("back", 180, -20),
                                               ("threequarter", -40, -30))):
            g.place(n + 1, (0.0, 0.0, 0.0), math.radians(yaw))
            scene.frame_set(n + 1)
            scene.objects["quick_sun"].rotation_euler[2] = math.radians(sun)
            quick.camera(scene, (0.0, -7.2, 1.45), (0.0, 0.0, 1.38), lens=50)
            print("wrote", quick.render(scene, "mobs_golem_" + label))

    if want("walk") or want("walk_vanilla"):
        for gait in (("planted",) if want("walk") else ()) + (("vanilla",) if want("walk_vanilla") else ()):
            scene = stage("day", path=(-8, 8))
            g = make_iron_golem("golem")
            g.place(1, (-6.0, 0.0, -0.0625), math.radians(90))
            end = g.walk(1, [(-6.0, 0.0, -0.0625), (7.0, 0.0, -0.0625)], gait=gait)
            info = g.last_walk
            print(gait, "walk ends at frame", end, _brief_walk(info))
            cyc = info["cycle_frames"]
            start = 12 + cyc                                             # past the acceleration
            scene.render.use_motion_blur = True
            scene.render.motion_blur_shutter = 0.5
            scene.render.motion_blur_position = "START"
            tag, stills = ("" if gait == "planted" else "_vanilla"), []
            for i in range(4):
                f = int(round(start + i * cyc / 4.0))
                scene.frame_set(f)
                here = g.pos_at(f)
                quick.camera(scene, (here.x + 1.4, -9.6, 1.2), (here.x, 0.0, 1.3), lens=50)
                stills.append(quick.render(scene, "mobs_walk%s_%d" % (tag, i + 1)))
                print("wrote", stills[-1], "frame", f)
            sheet("mobs_walk%s_sheet" % tag, stills)

    if want("offer"):
        scene = stage()
        g = make_iron_golem("golem")
        k = ch.make_villager("kid", "none", child=True)
        g.place(1, (0.0, 0.0, 0.0), 0.0)
        k.place(1, (-0.62, -2.15, 0.0), math.radians(180))
        g.offer_flower(1, ease=0)
        g.look_at(1, k, ease=0)
        k.look_at(1, g.flower_point(1), ease=0)
        scene.frame_set(1)
        scene.objects["quick_sun"].rotation_euler[2] = math.radians(-35)
        quick.camera(scene, (-8.4, -1.25, 1.1), (0.0, -1.0, 1.38), lens=36, fstop=5.6)     # both in profile
        print("wrote", quick.render(scene, "mobs_offer_1"))
        quick.camera(scene, (3.0, -7.3, 0.85), (-0.5, -1.2, 1.38), lens=42, fstop=5.6)     # from the golem's front left
        print("wrote", quick.render(scene, "mobs_offer_2"))

    if want("raise"):
        # the arm goes up and comes down ON SCREEN: the poppy grows out of the fist and goes back into it
        scene = stage(res=(360, 640), blur=True)
        g = make_iron_golem("golem")
        k = ch.make_villager("kid", "none", child=True)
        g.place(1, (0.0, 0.0, 0.0), 0.0)
        k.place(1, (-0.62, -2.15, 0.0), math.radians(180))
        g.look_at(1, k, ease=0)
        k.look_at(1, g, ease=0)
        up = g.offer_flower(10, ease=10)
        k.look_at(12, g.flower_point(up), ease=8)
        down = g.offer_flower(60, on=False, ease=10)
        scene.objects["quick_sun"].rotation_euler[2] = math.radians(-35)
        quick.camera(scene, (-3.3, -4.6, 0.9), (-0.55, -0.9, 0.98), lens=50)
        stills = []
        for label, frames in (("raise", (9, 10, 11, 12, 14, 17, 20)), ("lower", (60, 64, 66, 67, 68, 69, 70))):
            for i, f in enumerate(frames):
                scene.frame_set(f)
                stills.append(quick.render(scene, "mobs_%s_%d" % (label, i + 1)))
                print("wrote", stills[-1], "frame", f, "arm %.3f rad, poppy size %.3f, hidden %s"
                      % (g.arm_r.rotation_euler.x, g.flower.scale[0] / 0.5, g.flower.hide_render))
        sheet("mobs_raise_sheet", stills[:7])
        sheet("mobs_lower_sheet", stills[7:])
        print("offer raised over frames 10-%d, lowered over 60-%d" % (up, down))

    if want("corner") or want("crumbs"):
        import types

        z = -0.0625
        for name in [n for n in ("corner", "crumbs") if want(n)]:
            if name == "corner":
                # round a street corner on planted feet, the camera low on the outside of the bend
                scene = stage("day", res=(360, 640), blur=True, paths=((-1, -1, 1, 9), (-1, -1, 9, 1)))
                g = make_iron_golem("golem")
                route = [(0.5, 7.5, z), (0.5, 0.5, z), (8.0, 0.5, z)]
                g.place(1, route[0], 0.0)
                end = g.walk(1, route)
                cam = quick.camera(scene, (-2.3, -2.6, 0.45), (0.9, 1.3, 0.95), lens=30)
                arc = [k[0] for k in ch.read_keys(g.root, _ROT, 2) if 1e-3 < k[1] < math.radians(90.0) - 1e-3]
                frames = [int(round(arc[0] - 6 + (arc[-1] - arc[0] + 12) * i / 7.0)) for i in range(8)]
            else:
                # a straight stroll past a low camera that looks at the feet
                scene = stage("day", blur=True, path=(-1, 1))
                g = make_iron_golem("golem")
                route = [(0.5, 7.0, z), (0.5, -5.0, z)]
                g.place(1, route[0], 0.0)
                end = g.walk(1, route)
                cam = quick.camera(scene, (-2.6, -1.4, 0.3), (0.45, 0.6, 0.5), lens=32)
                frames = [f for f in range(1, end) if 1.6 > g.pos_at(f).y > -0.4][::14][:4]
            burst = g.step_crumbs(1, end + 1, cam, village=types.SimpleNamespace(world=stage.world), seed=5)
            print(name, "walk", _brief_walk(g.last_walk), "|", burst)
            scene.objects["quick_sun"].rotation_euler[2] = math.radians(-140 if name == "corner" else -120)
            stills = []
            for i, f in enumerate(frames):
                scene.frame_set(f)
                live = [ob for ob in burst.objects if not ob.hide_render]
                stills.append(quick.render(scene, "mobs_%s_%d" % (name, i + 1)))
                print("wrote", stills[-1], "frame", f, "yaw %.0f, legs %.2f / %.2f rad, %d crumbs in the air"
                      % (math.degrees(g.root.rotation_euler.z), g.leg_l.rotation_euler.x, g.leg_r.rotation_euler.x, len(live)))
            sheet("mobs_%s_sheet" % name, stills, height=640 if name == "crumbs" else 480)

    if want("items"):
        scene = stage(path=(-1, 1))
        poppy = make_dropped_item("poppy", seed=1)
        ingot = make_dropped_item("iron_ingot", seed=2, count=4)
        z = -0.0625
        poppy.drop(4, (-0.35, 0.0, z), velocity=(0.03, -0.02, 0.2))
        ingot.drop(4, (0.32, 0.3, z), velocity=(0.004, 0.03, 0.2))
        poppy.animate(4, 150)
        ingot.animate(4, 150)
        scene.render.use_motion_blur = True
        scene.render.motion_blur_shutter = 0.5
        scene.render.motion_blur_position = "START"
        scene.objects["quick_sun"].rotation_euler[2] = math.radians(-30)
        quick.camera(scene, (0.7, -4.9, 0.8), (0.02, 0.1, 0.42), lens=50, fstop=5.6)
        for n, f in enumerate((9, 40, 78)):
            scene.frame_set(f)
            print("wrote", quick.render(scene, "mobs_items_%d" % (n + 1)), "frame", f,
                  "poppy spin %.0f deg, lift %.3f" % (math.degrees(poppy.spin_at(f)) % 360.0, poppy.bob_at(f)))

    if want("crack"):
        scene = stage("day")
        for n, level in enumerate((None, "low", "medium", "high")):
            g = make_iron_golem("golem_%d" % n, crack=level)
            g.place(1, (-1.0 + (n % 2) * 2.0, (n // 2) * 2.0, (n // 2) * 3.0), 0.0)   # none, low / medium, high
        scene.frame_set(1)
        _set_box(scene, (-3.0, 1.0, 0.0), (3.0, 3.5, 3.0))
        scene.objects["quick_sun"].rotation_euler[2] = math.radians(-20)
        quick.camera(scene, (0.0, -13.5, 3.0), (0.0, 1.0, 2.95), lens=45)
        print("wrote", quick.render(scene, "mobs_crack"))

    if want("village") or want("fit"):
        _village_test(render=want("village"))


def _set_box(scene, lo, hi):
    """A stone-brick riser for the crack still (stand-in box with the real texture, as engine.characters' tests)."""
    return ch._test_box("mobs_riser", lo, hi, ch._test_material("mobs_riser", "block/stone_bricks"))


def _village_test(render=True):
    """The golem in the real village at night (engine.village + engine.look), and where it fits."""
    import os

    from . import look, quick, village

    scene = quick.reset()
    look.setup_render(scene, res=(540, 960), samples=16, threads=2, motion_blur=True)     # the films' shutter and DOF
    v = village.build_village(scene, seed=1)
    print("village built:", v.face_count, "faces")

    # ---- where does a 1.4 x 2.7 golem fit?
    for name in sorted(v.paths):
        game = clearance(v, v.paths[name])
        model = clearance(v, v.paths[name], width=MODEL_WIDTH, height=MODEL_HEIGHT)
        print("path %-18s hit box: %-28s arms: %s" % (name, _brief(game), _brief(model)))
        line = rounded(v.paths[name])                                    # what walk() really follows (corner radius 1)
        if len(v.paths[name]) > 2:
            print("     %-18s hit box: %-28s arms: %s" % ("... corners rounded", _brief(clearance(v, line)),
                                                         _brief(clearance(v, line, width=MODEL_WIDTH, height=MODEL_HEIGHT))))
    fits, tight, blocked = [], [], []
    for name in sorted(v.anchors):
        if name.endswith(("_station", "_station_2", "_cam", "_cam_beds", "_door", "_target", "_center")) \
                or "_bed_" in name or name in ("bell", "well") or name.startswith("bell_lamp_"):
            continue
        game = clearance(v, [v.anchors[name]])
        model = clearance(v, [v.anchors[name]], width=MODEL_WIDTH, height=MODEL_HEIGHT)
        (blocked if game else (tight if model else fits)).append(name)
        if game:
            print("anchor %-18s blocked by %s" % (name, _brief(game)))
    print("anchors the golem fits:", ", ".join(fits))
    print("anchors that fit the hit box but not the arms:", ", ".join(tight) or "-")
    print("anchors it does not fit:", ", ".join(blocked) or "-")
    if not render:
        return

    look.set_time(scene, "night", sun_azimuth=176.0, sun_elevation=21.0)
    look.setup_compositor(scene, bloom=1.3, grade="cool")
    v.set_lantern_energy(1.3)
    for ob in v.lantern_lights:                                         # room fills belong to interior shots only
        if ob.get("mc_light") == "fill":
            ob.hide_render = True
    g = make_iron_golem("golem")
    z = -0.0625                                                         # the surface of a dirt path

    def still(name, frame, cam, target, lens, focus, walk_from):
        scene.frame_set(frame)
        here = g.pos_at(frame)
        print(name, "golem at", tuple(round(c, 2) for c in here), "frame", frame, "| hit box:",
              _brief(clearance(v, [here])), "| arms:", _brief(clearance(v, [here], width=MODEL_WIDTH, height=MODEL_HEIGHT)))
        c = quick.camera(scene, cam, target, lens=lens, fstop=2.8)
        c.data.dof.focus_distance = (Vector(cam) - Vector(focus)).length
        for seed in range(12):                                           # the crumbs of the real path under it:
            burst = g.step_crumbs(walk_from, frame + 1, c, village=v, seed=seed)
            live = [q["object"] for q in burst.particles if q["first"] <= frame < q["last"]]
            if len(live) >= 3:                                           # (a draw with a few of them on this frame)
                break
            for ob in burst.objects:
                bpy.data.objects.remove(ob, do_unlink=True)
        scene.frame_set(frame)
        print(name, burst, "seed", seed, "|", len(live), "in the air on this frame:",
              [tuple(round(q, 2) for q in ob.matrix_world.translation) for ob in live],
              "| texture", sorted({ob.data.materials[0]["mc_texture"] for ob in burst.objects}))
        path = os.path.join(quick.TEST_DIR, name + ".png")
        scene.render.filepath = path
        bpy.ops.render.render(write_still=True)
        print("wrote", path)

    # 1. the west street: house_d behind, the farm across the road, and the lamp post at (-17, 2), whose south
    #    torch hangs over the road's north lane. The golem walks east along that lane, right under it.
    lane = [(-23.0, 1.3, z), (-9.5, 1.3, z)]
    print("west street, north lane: hit box", _brief(clearance(v, lane)), "| arms",
          _brief(clearance(v, lane, width=MODEL_WIDTH, height=MODEL_HEIGHT)))
    g.place(1, lane[0], math.radians(90))
    g.walk(1, lane)
    f = next(k for k in range(1, 400) if g.pos_at(k).x >= -16.55)
    g.look_at(f - 10, (-12.5, -2.6, 1.2), ease=8)
    farmer = ch.make_villager("farmer", "farmer")
    farmer.place(1, (-8.0, -0.7, z), math.radians(-90))
    farmer.walk(1, [(-8.0, -0.7, z), (-20.0, -0.7, z)], speed=0.55)
    farmer.look_at(f - 10, g, ease=6)
    still("mobs_village", f, (-12.3, -2.75, 0.8), (-16.85, 1.75, 1.92), 28, (-16.5, 1.3, 1.9), 1)

    # 2. the exit road between house_e and house_f, seen from the square, the two lamp posts of the gate beyond
    road = [(0.5, 22.5, z), (0.5, 9.0, z)]
    print("exit road between house_e and house_f: hit box", _brief(clearance(v, road)), "| arms",
          _brief(clearance(v, road, width=MODEL_WIDTH, height=MODEL_HEIGHT)))
    g.place(500, road[0], math.radians(180))
    g.walk(500, road)
    f = next(k for k in range(500, 900) if g.pos_at(k).y <= 15.6)
    farmer.show(500, False)
    still("mobs_village_road", f, (0.9, 7.4, 0.9), (0.4, 15.6, 1.75), 24, (0.5, 15.6, 1.9), 500)


def _brief(hits):
    if not hits:
        return "clear"
    kinds = sorted({h[3] for h in hits})
    return "%d hits (%s) first at %s" % (len(hits), ", ".join(kinds), hits[0][:3])


if __name__ == "__main__":
    _selftest(set(sys.argv[1:]))
