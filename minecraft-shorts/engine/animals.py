"""COWS and CHICKENS (adults and the 26.x babies) for the farm films: pens, feeding, milking, eggs. New module;
edits no other file.

Everything is transcribed from the Java Edition 26.x client classes (named next to each number below) and drawn with
the game's own textures through engine.mcassets: entity/cow/cow_temperate[_baby].png and
entity/chicken/chicken_temperate[_baby].png (the temperate variants, the defaults; the game also has cold and warm
ones, not built here). Blender axes as everywhere: +X east, +Y north, +Z up, 1 block = 1 unit, animals face -Y at
yaw 0, 24 fps (the game runs 20 ticks per second: 1 tick = 1.2 frames).

PUBLIC API  (frames are film frames; "camera" = the Shot that films it, a Film, or a camera object: particles face it)

  make_cow(name="cow", baby=False) / make_chicken(name="chicken", baby=False) -> Animal
      Box for box from CowModel / BabyCowModel / AdultChickenModel / BabyChickenModel (horns, muzzle, udder, comb,
      beak, wattle, wings, flat feet). Babies are the game's own baby MODELS (26.x), not shrunken adults.
  add_cow(st, name, baby=False) / add_chicken(st, name, baby=False)
      The same, registered with a films.lookdev.Stage (st.cast[name]); then st.use(shot, cow), st.hero(shot, "cow", cow).

  Animal (a subclass of engine.characters.Character: root / hips / body / head / legs / wings)
      place(frame, pos, yaw=0.0)            hard cut to a spot: upright, neutral, alive again (use at shot cuts)
      show(frame, visible=True)             keyed visibility (Stage.finish calls it)
      walk(frame, points, speed=None, run=False, from_current=False, gait="planted", swing=None, corner=None,
           bob=None) -> end frame           along a polyline at the game's strolling speed (cow 1.76 blocks/s,
                                            chicken 2.75; run=True: the panic speed, cow 7.05, chicken 5.40). It
                                            gets up to speed and stops by itself (2-frame time constant; the end
                                            frame is 10 frames after the last push), turns on the spot first if
                                            it faces another way, and rounds corners (radius cow 1, hen 0.5).
                                            gait="planted": soles on the ground do not slide (see GAIT);
                                            gait="vanilla": the game's exact leg wave (the feet slide).
      turn(frame, yaw, ease=None) / face(frame, target, ease=None) -> end frame
                                            turn on the spot (10 frames for 45 degrees or more) with stepping legs
      look_at(frame, target, ease=6) / track(f0, f1, target)
                                            the head, clamped to the game's 75 degrees of yaw and 40 of pitch.
                                            target = point / Character / Object (a held item: track(f0, f1, wheat)).
                                            A CHICK HAS NO HEAD PART: look_at turns its whole body, track does nothing
      idle(frame_start, frame_end, seed=0, watch=None, rate=1.0)
                                            standing: the head turns to look somewhere for 1-2 s and comes back, at
                                            10 degrees per tick (RandomLookAroundGoal); watch = a Character it also
                                            looks at for 2-4 s while he is within 6 blocks (LookAtPlayerGoal)
      hurt(frame, attacker=None, knockback=True, max_back=None) -> frame it stands again
                                            red for 12 frames, thrown 0.96 up and 2.0 back (away from attacker: a
                                            Character or point), legs flailing; a hen flaps and lands after 20
                                            frames, 2.35 back. max_back = room behind it in blocks (a fence).
                                            Then let it run: walk(end, [...], run=True)  (PanicGoal: within 5 blocks)
      die(frame, camera=None, attacker=None, knockback=True, max_back=None, poof=True, seed=0, village=None)
                                            -> frame + 24, the frame it is GONE: red and knocked back from `frame`,
                                            tips over to its left (flat after 16 frames), then vanishes and 20 white
                                            poof particles rise where it stood. Stays gone until its next place()
      hop(frame, to=None) / fall(frame, to) -> landing frame
                                            a jump (apex 1.25: up one block and 1 forward in 11 frames) / stepping
                                            off an edge. A chicken flaps and sinks at 2.3 blocks/s (2 blocks: 24 frames)
      Chicken.flap(frame_start, frame_end)  only the wings, as while airborne (hop / fall / hurt call it themselves)
      eye_point(frame) / mouth_point(frame) middle of the head (what others look at and cameras focus on) / a point
                                            just in front of the muzzle or beak (hold the food out to there)
      size (hit box w, h), width, walk_speed, tempt_speed, run_speed, food (item ids), baby, species, kind,
      last_walk (dict: frames, blocks, steps, swing, cycle_frames, stance ...), bursts (its particle bursts)
      nod / shake / shiver / flinch (a small hop): inherited; swing_arm / raise_arm do nothing; hold / lie_down raise

  wander(animals, frame_start, frame_end, area, seed=0, place=True, speed=None, gait="planted", clearance=None,
         activity=1.0, watch=None, z=0.0) -> {name: [("stand" | "walk", first frame, last frame, target), ...]}
      A PEN IN ONE CALL: every animal alternates standing, looking around and short straight walks inside the
      rectangle area = (x0, y0, x1, y1), each with its own timing. place=True puts them on free spots at
      frame_start; place=False goes on from where they stand. No body leaves the rectangle or comes closer than
      its own width (cow 0.75, hen 0.5; clearance=) to another body or the edge, also while both move.
  pen_area(x0, y0, x1, y1) -> area      the free rectangle inside a ring of fence blocks on those cells
  make_pen(scene, x0, y0, x1, y1, z=0, gates=[(x, y)], fence="oak_fence", ground=None, name="pen") -> dict
      Real fence and fence-gate blocks on the ring of cells, as their own little World (the village is not edited);
      ["area"] is what wander() wants. ground="grass_block" lays a floor under it (not needed on the village's meadow).
  pen_report(animals, f0, f1, area) -> (smallest gap between two bodies, smallest distance to the edge)

  follow(animal, leader, frame_start, frame_end, stop=2.5, speed=None, look="eyes") -> frame it has come to rest
      TemptGoal: the animal walks after a player holding its food whenever he is further than 2.5 blocks, at up to
      its tempted speed (2.75 blocks/s), and keeps its head on him. look="eyes" is the game (his eyes), look=<the
      item object> or "item" (leader.held) looks at the food instead. Also a calf after its mother:
      follow(calf, cow, f0, f1, stop=3.0)  (FollowParentGoal: closer than 3 blocks it stays). Key the leader first.
  hand_item(player, item, frame_start, frame_end=None) -> Object
      'wheat' (cows), 'wheat_seeds' (chickens), 'bucket' ... in Steve's right hand for those frames only, with the
      game's item arm pose. Unlike Character.hold it is keyed, so the next shot can show an empty hand.
  love(animal, frame, camera, frame_end=None, seed=0) -> [Burst]
      Fed: 7 hearts on `frame`, then one every 12 frames until frame_end (default 3 s; the game 30 s).
  milk(player, frame, frame_start, frame_end=None) -> (bucket, milk_bucket)
      Item 'bucket' in his hand from frame_start, his arm swings, and from `frame` it is item 'milk_bucket'.
  lay_egg(chicken, frame, seed=0, until=None, stage=None) -> engine.mobs DroppedItem
      Item 'egg' pops out at her feet (hops 0.38 up, lands after 11 frames, lies still 0.3-0.9 block away after
      18; egg.rest_pos says where), then bobs and spins. Hens lay every 5-10 minutes in the game.
  drop_loot(animal, frame, items=None, seed=0, stage=None) -> [DroppedItem]
      On the frame of the killing blow: cow 'beef' x 2 + 'leather', chicken 'chicken' + 'feather' (babies nothing).
  poof(target, frame, camera, seed=0, size=None, count=20) -> Burst       only the death cloud, for anything
  knockback_track / air_track / death_angle / hurt_sheet / animal_sheet: the numbers and textures behind the above.
  Constants: COW_WALK, COW_TEMPT, COW_PANIC, CHICKEN_WALK, CHICKEN_PANIC, CHICK_FOLLOW, COW_FOOD, CHICKEN_FOOD,
  EGG_ITEM, BUCKET_ITEM, MILK_ITEM, TEMPT_STOP, HURT_FRAMES, DEATH_FRAMES, LOOT, FACTS.

USING THEM IN A FILM (st = films.lookdev.Stage, s = st.shot(...), v = the Village)
    pen = animals.make_pen(scene, 3, 27, 12, 36, gates=[(7, 27)])        # once; 10 x 10 cells, 8.75 x 8.75 inside
    cows = [animals.add_cow(st, "cow%d" % i) for i in range(4)] + [animals.add_cow(st, "calf", baby=True)]
    animals.wander(cows, s.frame_start, s.frame_end + 1, pen["area"], seed=3); st.use(s, *cows)
    steve.place(f0, spot, yaw); wheat = animals.hand_item(steve, "wheat", f0, s.frame_end + 1)
    end = animals.follow(daisy, steve, f0, f0 + 50, look=wheat)           # she walks up and stops 2.3 blocks away
    steve.swing_arm(end + 6); animals.love(daisy, end + 8, camera=s, frame_end=s.frame_end + 1)
    bucket, full = animals.milk(steve, f0 + 20, f0, s.frame_end + 1)      # in the next shot, after his place()
    egg = animals.lay_egg(hen, f0 + 14, stage=st); st.use(s, egg)
    up = hen.hurt(f, attacker=steve, max_back=0.9); hen.walk(up, [hen.pos_at(up), away], run=True)
    gone = hen.die(f2, camera=s, attacker=steve); animals.drop_loot(hen, f2, stage=st)
  Rules:
    - Key every animal in frame order, place() before everything else in a shot. A call replaces what the animal
      was doing from its frame on (a hurt() in mid-walk stops the walk there).
    - wander() only knows the animals in its list. Steve, a cow that follows him or a hen that gets hit in the same
      pen must stay out of the others' way: give wander() a sub-rectangle of the pen. A walk that began before
      frame_end runs on (up to 65 frames): in the next shot place() them or wander(..., place=False).
    - Particles (hearts, poof) are world objects with their own lifetimes (hearts 20 frames, poof up to 99, half of
      it gone after 45): a cut that jumps in time needs engine.fx.stop_particles(first frame of the new shot).
    - hand_item() / milk() after the player's place(); place() him again only at their frame_end. A held item is a
      flat sprite along the hand: edge-on from his side, readable from behind his shoulder and from above.
    - A walk that opens a shot in stride: place() and walk() 12+ frames before the cut (only if the animal is not
      in the shot before: its place() would cut that shot's action short).
    - The red flash is a second set of meshes (built on the first hurt / die); never key hide_render on an animal's
      parts yourself: use show(). st.hero(shot, "hen", hen) is its head (a chick: its body).
    - make_pen stands the fence on the village's ground as it is: grass tufts and flowers of the meadow stay and
      poke through a rail here and there; a camera low behind a rail has the fence across the lower half.

SIZES (blocks; hit box in brackets)
    cow      1.5625 to the horn tips, back 1.375, 0.75 wide, nose 0.94 in front of its feet, rump 0.625 behind
             [0.9 x 1.4]; eyes 1.25 up.     calf   1.0 to the horn tips, back 0.75, 0.5 wide, 1.06 long [0.45 x 0.7]
    chicken  0.94 to the top of the head, back 0.69, 0.5 wide over the wings, beak 0.5 in front, tail 0.25 behind
             [0.4 x 0.7].                    chick  0.375 tall, 0.25 wide, 0.31 long [0.3 x 0.4]
    Steve is 1.875, a villager 1.99, a fence 1.0 as drawn (1.5 as an obstacle): a cow looks over it, a hen is
    hidden by the rails from a low camera. In a 10 x 10 cell pen five cows and a calf have room; 8 x 9 cells hold
    six hens and two chicks easily.

GAIT (QuadrupedModel.setupAnim, ChickenModel.setupAnim, LivingEntity.updateWalkAnimation, WalkAnimationState)
    The game: legs cos(p * 0.6662 [+ pi]) * 1.4 * s, pairs right hind + left front and left hind + right front
    (a hen: right, left); s approaches min(4 * blocks moved per tick, 1) and p grows by s every tick (three times
    as fast for a baby). So a strolling cow swings +-28 degrees once per 2.36 blocks (32 frames) while such a step
    covers 0.71 block: every sole slides 0.47 block per step. gait="vanilla" is exactly that, no bob.
    gait="planted" keeps pairs, speed and (about) the game's swing for that speed, and shortens the cycle to what
    the legs can cover: cow 18 frames, calf 9, hen 7, chick 3 (their legs are 5 and 2 pixels long: a blur at the
    game's speed in either gait, as in the game; speed=1.2 calms a hen in a close shot). A sole on the ground
    strays under 0.005 block (measured, also round corners and in turns on the spot, where the legs lean
    sideways a little to stay put); the swinging pair passes it in the middle of the step. The body sinks up to
    0.08 block with every step of a cow so that the standing soles stay ON the ground (bob=1); a hen sinks only
    0.03 and a chick not at all (their feet lift 0.05 / 0.03 block at the ends of a step instead: at 4 steps a
    second a full bob would make the body tremble).
    These, the rounded corners and the stepping turn are the module's only departures from the game.
    Chicken legs are flat in the game (a 1-pixel shank on the back of the leg box, a 3 x 3 foot plate): seen
    exactly from the side the shank is edge-on and vanishes; a chick's wings are 1-pixel horizontal plates.

WHAT THE GAME DOES (read from the classes; FACTS has the short list)
  - AbstractCow / Chicken goals: PanicGoal (speed x 2.0 / 1.4), BreedGoal, TemptGoal (x 1.25 with wheat / x 1.0 with
    seeds: wheat_seeds, melon, pumpkin, beetroot, torchflower seeds, pitcher pod), FollowParentGoal (x 1.25 / 1.1),
    WaterAvoidingRandomStrollGoal (x 1.0, up to 10 blocks, about once in 6 s), LookAtPlayerGoal (6 blocks),
    RandomLookAroundGoal. Movement speed attribute 0.2 / 0.25; blocks per second = 20 * (attribute * modifier)^2 /
    0.454. Babies move as fast as adults. Health: cow 10, chicken 4.
  - TemptGoal looks at the PLAYER'S EYES, not at the item, comes no closer than 2.5 blocks, and a tempted animal
    does nothing else. Feeding (use the food on it): hearts (entity event 18), in love for 30 s.
  - Milking: use a bucket on an adult cow: the bucket becomes a milk bucket at once; no particles, no animation
    on the cow. A calf cannot be milked.
  - A hen lays an egg every 5 to 10 minutes; chicks and hens ridden by a baby zombie do not.
  - A chicken flaps only while it is off the ground ((sin(flap) + 1) * flapSpeed: 0-115 degrees, 5.7 beats/s) and
    then falls at 2.3 blocks/s; on the ground its wings are still. No pecking animation exists.
  - Hurt: hurtTime 10 ticks of red overlay (every texel 70 % itself + 30 % red), knockback(0.4) away from the
    attacker, walk animation speed set to 1.5 (the flailing legs), then PanicGoal: it runs to a random spot
    within 5 blocks at its panic speed, again and again for about 2 s.
  - Death: deathTime counts 20 ticks; LivingEntityRenderer tips the body about its feet, 90 degrees *
    sqrt((t - 1) * 0.08), red all the while, legs straight; on tick 20 it is removed and 20 'poof' particles
    (generic_7 ... generic_0, white-grey, 0.2-1.4 wide) appear in its upright hit box and rise. The loot pops out
    on tick 0. Nothing else: no blood, no sound-dependent effect.

MEASURED IN THE PROOFS (out/test/animals_*.png, check_animals_*.png)
  - walk: cow 1 block in 24 frames, 2 in 38, 4 in 65 (always + 10 frames of rolling out); hen 1 in 19, 4 in 45.
    A cow turns 90 degrees in 10 frames with two steps.
  - hearts 0.3-0.6 block wide, start up to 0.9 beside the animal and 0.5-1.9 above its feet, rise 0.65.
  - poof: 20 puffs, the last gone 24-99 frames after the death (median 45), rising to 2 blocks (a few to 3.8).
  - cameras that worked: pen from outside, 4.3 above the ground, 24 mm, 5-9 blocks away (landscape proofs); a cow
    two-shot in profile 50 mm from 6.6 blocks; over Steve's left shoulder at the coming cow 26 mm f/3.2; the
    bucket from behind his right shoulder and above 24 mm; hens through a fence from 1.3 high need the lens above
    the top rail (1.0).

Self-test:  $BPY -m engine.animals [check lineup views walk flap wheat egg hurt die pen]
    (no argument = check: 46 numeric checks, 4 s; give one or two picture names per call to stay under 300 s;
    also views_cow / views_calf / views_chicken / views_chick, walk_calf, walk_chick, walk_cow_vanilla,
    walk_chicken_vanilla, pen_cow, pen_chicken). Stills: out/test/animals_*.png.
    $BPY -m tools.check_animals_film [shot:offset ...]   a four-shot farm film through films.lookdev.Stage and
    engine.look (13 checks; stills out/test/check_animals_*.png).
"""
import bisect
import heapq
import math
import sys

import bpy
import numpy as np
from mathutils import Matrix, Vector

from . import characters as ch
from . import mcassets as mc
from . import mobs
from . import pix

FPS = ch.FPS
TICK = FPS / 20.0                    # frames per game tick
_LOC, _ROT = "location", "rotation_euler"

# ---- net.minecraft.world.entity.EntityTypes: COW sized(0.9f, 1.4f) eyeHeight(1.3f); CHICKEN sized(0.4f, 0.7f)
#      eyeHeight(0.644f). Cow.BABY_DIMENSIONS scalable(0.45f, 0.7f) eye 0.69f; Chicken.BABY_DIMENSIONS
#      scalable(0.3f, 0.4f) eye 0.28125f
COW_SIZE, COW_EYE = (0.9, 1.4), 1.3
CALF_SIZE, CALF_EYE = (0.45, 0.7), 0.69
CHICKEN_SIZE, CHICKEN_EYE = (0.4, 0.7), 0.644
CHICK_SIZE, CHICK_EYE = (0.3, 0.4), 0.28125

# ---- AbstractCow.createAttributes: MAX_HEALTH 10, MOVEMENT_SPEED 0.2; Chicken.createAttributes: MAX_HEALTH 4,
#      MOVEMENT_SPEED 0.25. registerGoals (both): PanicGoal (cow 2.0, chicken 1.4), BreedGoal 1.0, TemptGoal (cow
#      1.25 with ItemTags.COW_FOOD, chicken 1.0 with ItemTags.CHICKEN_FOOD), FollowParentGoal (cow 1.25, chicken
#      1.1), WaterAvoidingRandomStrollGoal 1.0, LookAtPlayerGoal(Player, 6.0), RandomLookAroundGoal.
#      Blocks per second = mobs.mob_speed(goal modifier, attribute): 20 * (attribute * modifier)^2 / (1 - 0.546).
COW_ATTRIBUTE, CHICKEN_ATTRIBUTE = 0.2, 0.25
COW_WALK = mobs.mob_speed(1.0, COW_ATTRIBUTE)            # 1.762 blocks / s: strolling
COW_TEMPT = mobs.mob_speed(1.25, COW_ATTRIBUTE)          # 2.753: after wheat, and a calf after its mother
COW_PANIC = mobs.mob_speed(2.0, COW_ATTRIBUTE)           # 7.048: after it was hit
CHICKEN_WALK = mobs.mob_speed(1.0, CHICKEN_ATTRIBUTE)    # 2.753: strolling, and after seeds
CHICKEN_TEMPT = mobs.mob_speed(1.0, CHICKEN_ATTRIBUTE)
CHICKEN_PANIC = mobs.mob_speed(1.4, CHICKEN_ATTRIBUTE)   # 5.396
CHICK_FOLLOW = mobs.mob_speed(1.1, CHICKEN_ATTRIBUTE)    # 3.331: a chick after its mother
COW_FOOD = ("wheat",)                                    # data/minecraft/tags/item/cow_food.json
CHICKEN_FOOD = ("wheat_seeds", "melon_seeds", "pumpkin_seeds", "beetroot_seeds", "torchflower_seeds", "pitcher_pod")
EGG_ITEM = "egg"                                         # loot_table/gameplay/chicken_lay.json, temperate variant
EGG_TICKS = (6000, 12000)                                # Chicken: eggTime = random.nextInt(6000) + 6000
BUCKET_ITEM, MILK_ITEM = "bucket", "milk_bucket"         # AbstractCow.mobInteract: Items.BUCKET -> Items.MILK_BUCKET
TEMPT_STOP = 2.5                                         # TemptGoal.DEFAULT_STOP_DISTANCE
TEMPT_RANGE = 10.0                                       # Attributes.TEMPT_RANGE default
LOOK_AT_PLAYER = 6.0                                     # LookAtPlayerGoal(this, Player.class, 6.0F)
LOVE_TICKS = 600                                         # Animal.setInLove: inLove = 600
LOVE_HEARTS = 7                                          # Animal.handleEntityEvent(18): 7 heart particles
LOVE_EVERY = 10                                          # Animal.aiStep: one more heart whenever inLove % 10 == 0
LOVE_LIFT = 0.5                                          # ... at getRandomY() + 0.5

# ---- Mob.getMaxHeadYRot() 75, getMaxHeadXRot() 40, getHeadRotSpeed() 10 (degrees, degrees per tick; LookControl)
HEAD_YAW_MAX = math.radians(75.0)
HEAD_PITCH_MAX = math.radians(40.0)
HEAD_SPEED = math.radians(10.0) / TICK                   # radians per frame
LOOK_TICKS = (20, 40)                                    # RandomLookAroundGoal: 20 + nextInt(20) ticks, chance 0.02 a tick
WATCH_TICKS = (40, 80)                                   # LookAtPlayerGoal: 40 + nextInt(40) ticks, chance 0.02 a tick

# ---- QuadrupedModel.setupAnim / ChickenModel.setupAnim / LivingEntity.updateWalkAnimation / WalkAnimationState
LEG_SWING = 1.4                      # leg xRot = cos(pos * 0.6662 [+ pi]) * 1.4 * walkAnimationSpeed
LEG_RATE = 0.6662
ANIM_PER_BLOCK = 4.0                 # target speed = min(4 * blocks moved in the tick, 1) ...
ANIM_LERP = 0.4                      # ... approached by 0.4 of the difference every tick; position += speed
BABY_ANIM_SCALE = 3.0                # positionScale 3 for babies: their legs cycle three times as fast
VANILLA_CYCLE = 2.0 * math.pi / LEG_RATE / ANIM_PER_BLOCK    # 2.358 blocks of travel per leg cycle (babies: a third)
GROUND_DRAG = 0.6 * 0.91             # LivingEntity.travelInAir on the ground: block friction 0.6 * 0.91 per tick
AIR_DRAG = 0.91
SPEED_TAU = -TICK / math.log(GROUND_DRAG)     # 1.98 frames: time constant of a mob's getting up to speed / stopping
BRAKE_TAUS = 5.0                     # a walk is over this many time constants after its last push
TURN_FRAMES = 10                     # LivingEntity.tickHeadTurn: yBodyRot closes 0.3 of the gap per tick (95 % in 8.4)

# ---- Chicken.aiStep / ChickenModel.setupAnim
FLAP_UP, FLAP_DOWN = 4.0 * 0.3, -1.0 * 0.3    # flapSpeed += (onGround ? -1 : 4) * 0.3, clamped to 0..1
FLAP_DECAY = 0.9                     # flapping = 1 while in the air, then *= 0.9; flap += flapping * 2 every tick
FLAP_STEP = 2.0                      # so in the air the wings beat once every 2 pi / 1.8 = 3.49 ticks = 4.19 frames
CHICKEN_FALL = 0.6                   # in the air and falling: vertical speed *= 0.6 every tick (2.28 blocks / s)

# ---- LivingEntity: handleDamageEvent, knockback, tickDeath, makePoofParticles; LivingEntityRenderer.setupRotations
HURT_TICKS = 10                      # hurtDuration = hurtTime = 10: the red overlay
HURT_FRAMES = int(round(HURT_TICKS * TICK))              # 12
HURT_ANIM_SPEED = 1.5                # walkAnimation.setSpeed(1.5F): the legs flail
OVERLAY_KEEP = 178.0 / 255.0         # OverlayTexture rows 0-7: 0xB2FF0000; entity.fsh: mix(overlay.rgb, colour, overlay.a)
KNOCKBACK = 0.4                      # LivingEntity.hurtServer: knockback(0.4F, dx, dz)
REST_VY = -0.0784                    # vertical speed of a mob standing on the ground: (0 - 0.08) * 0.98
GRAVITY = 0.08
JUMP = 0.42                          # Attributes.JUMP_STRENGTH default: LivingEntity.jumpFromGround
DEATH_TICKS = 20                     # LivingEntity.tickDeath: ++deathTime >= 20 -> entity event 60, remove
DEATH_FRAMES = int(round(DEATH_TICKS * TICK))            # 24
DEATH_FLIP = 90.0                    # getFlipDegrees(); angle = 90 * min(1, sqrt((deathTime - 1) / 20 * 1.6))
POOF_COUNT = 20                      # LivingEntity.makePoofParticles: 20 x ParticleTypes.POOF
POOF_SPRITES = tuple("generic_%d" % i for i in range(7, -1, -1))     # assets/minecraft/particles/poof.json
POOF_GLOW = 0.15                     # this module's choice: self-light of the white puffs (0 = lit by the set only)
GROUND_EPS = 0.004                   # the flat feet of a chicken lie IN the ground plane: lifted this much (no z-fight)

FACTS = {
    "cow model": "CowModel.createBaseCowModel, 64x64 entity/cow/cow_temperate: 25 px to the horn tips, 22 to the back, 25 long",
    "calf model": "BabyCowModel.createBodyLayer, 64x64 entity/cow/cow_temperate_baby: 16 px to the horn tips, drawn unscaled",
    "chicken model": "AdultChickenModel.createBaseChickenModel, 64x32 entity/chicken/chicken_temperate: 15 px tall",
    "chick model": "BabyChickenModel.createBodyLayer, 16x16 entity/chicken/chicken_temperate_baby: 6 px tall, no head part",
    "speeds": "cow 1.76 / 2.75 (wheat) / 7.05 (panic) blocks/s; chicken 2.75 / 2.75 (seeds) / 5.40",
    "legs": "cos(pos * 0.6662 [+ pi]) * 1.4 * speed; pairs: right hind + left front, left hind + right front",
    "wings": "(sin(flap) + 1) * flapSpeed radians, only in the air: 0..2 rad, one beat per 4.19 frames",
    "hurt": "red overlay 10 ticks, knock-back 0.4: 0.96 up, 2.0 back, 10 ticks in the air (a chicken 16, 2.35 back), legs flail",
    "love": "fed its food: 7 hearts (event 18), then one every 10 ticks for 600 ticks; TemptGoal stops 2.5 blocks from the player",
    "items": "cow food wheat; chicken food wheat_seeds (and other seeds); bucket -> milk_bucket; egg; loot beef, leather / chicken, feather",
    "death": "tips to its left over ticks 1-13.5, gone on tick 20 with 20 poof particles around the upright hit box",
}


# ----------------------------------------------------------------------------------------------------
# the models (pixels, the game's model space: x to the animal's left, y DOWN, z to its back; feet on y = 24)
# ----------------------------------------------------------------------------------------------------
def _cow_spec():
    """net.minecraft.client.model.animal.cow.CowModel.createBaseCowModel(): LayerDefinition 64 x 64, drawn unscaled
    (CowRenderer extends MobRenderer: no scale(); LayerDefinitions puts no MeshTransformer on ModelLayers.COW)."""
    C, P = ch._cube, ch._pose
    leg = dict(u=0, v=16, x=-2, y=0, z=-2, w=4, h=12, d=4)
    return dict(
        tex=(64, 64), scale=1.0, hip=12.0, top=-1.0, eye=24.0 - COW_EYE * 16.0, back=5.0, sleep_eye=COW_EYE,
        parts=[
            # body: PartPose.offsetAndRotation(0, 5, 2, pi / 2, 0, 0); the trunk and the udder
            dict(name="body", parent="hips", pivot=(0, 12, 0), groups=[([P(0, 5.0 - 12.0, 2.0, rx=math.pi / 2.0)], [
                C(18, 4, -6, -10, -7, 12, 18, 10),
                C(52, 0, -2, 2, -8, 4, 6, 1)])]),
            # head: PartPose.offset(0, 4, -8); head, muzzle, right_horn, left_horn
            dict(name="head", parent="body", pivot=(0, 4, -8), groups=[([], [
                C(0, 0, -4, -4, -6, 8, 8, 6),
                C(1, 33, -3, 1, -7, 6, 3, 1),
                C(22, 0, -5, -5, -5, 1, 3, 1),
                C(22, 0, 4, -5, -5, 1, 3, 1)])]),
            # legs 4 x 12 x 4 at texOffs(0, 16); the left ones from the .mirror() builder
            dict(name="leg_r", parent="hips", pivot=(-4, 12, -5), groups=[([], [C(**leg)])]),          # right_front_leg
            dict(name="leg_l", parent="hips", pivot=(4, 12, -5), groups=[([], [C(mirror=True, **leg)])]),   # left_front_leg
            dict(name="leg_hr", parent="hips", pivot=(-4, 12, 7), groups=[([], [C(**leg)])]),          # right_hind_leg
            dict(name="leg_hl", parent="hips", pivot=(4, 12, 7), groups=[([], [C(mirror=True, **leg)])]),   # left_hind_leg
        ])


def _calf_spec():
    """net.minecraft.client.model.animal.cow.BabyCowModel.createBodyLayer(): the dedicated baby model of 26.x
    (ModelLayers.COW_BABY), 64 x 64, drawn unscaled with the variant's baby texture."""
    C, P = ch._cube, ch._pose
    return dict(
        tex=(64, 64), scale=1.0, hip=18.0, top=8.0, eye=24.0 - CALF_EYE * 16.0, back=3.0, sleep_eye=CALF_EYE,
        parts=[
            # body: PartPose.offset(3, 19, -5), not rotated
            dict(name="body", parent="hips", pivot=(0, 18, 0), groups=[([P(3.0, 19.0 - 18.0, -5.0)], [
                C(0, 0, -7, -7, -1, 8, 6, 12)])]),
            # head: PartPose.offset(0, 13.569, -5.1667); head, left horn, right horn (mirrored), muzzle
            dict(name="head", parent="body", pivot=(0, 13.569, -5.1667), groups=[([], [
                C(0, 18, -3, -4.569, -4.8333, 6, 6, 5),
                C(8, 29, 3, -5.569, -3.8333, 1, 2, 1),
                C(4, 29, -4, -5.569, -3.8333, 1, 2, 1, mirror=True),
                C(12, 29, -2, -1.569, -5.8333, 4, 3, 1)])]),
            dict(name="leg_r", parent="hips", pivot=(-2.5, 18, -3.5), groups=[([], [C(22, 18, -1.5, 0, -1.5, 3, 6, 3)])]),
            dict(name="leg_l", parent="hips", pivot=(2.5, 18, -3.5), groups=[([], [C(34, 18, -1.5, 0, -1.5, 3, 6, 3)])]),
            dict(name="leg_hr", parent="hips", pivot=(-2.5, 18, 3.5), groups=[([], [C(22, 27, -1.5, 0, -1.5, 3, 6, 3)])]),
            dict(name="leg_hl", parent="hips", pivot=(2.5, 18, 3.5), groups=[([], [C(34, 27, -1.5, 0, -1.5, 3, 6, 3)])]),
        ])


def _chicken_spec():
    """net.minecraft.client.model.animal.chicken.AdultChickenModel.createBaseChickenModel(): 64 x 32, unscaled.
    The beak and the wattle ('red_thing') are children of the head at PartPose.ZERO."""
    C, P = ch._cube, ch._pose
    return dict(
        tex=(64, 32), scale=1.0, hip=19.0, top=9.0, eye=24.0 - CHICKEN_EYE * 16.0, back=3.0, sleep_eye=CHICKEN_EYE,
        parts=[
            # body: PartPose.offsetAndRotation(0, 16, 0, pi / 2, 0, 0)
            dict(name="body", parent="hips", pivot=(0, 19, 0), groups=[([P(0, 16.0 - 19.0, 0, rx=math.pi / 2.0)], [
                C(0, 9, -3, -4, -3, 6, 8, 6)])]),
            # head: PartPose.offset(0, 15, -4); head, beak, red_thing
            dict(name="head", parent="body", pivot=(0, 15, -4), groups=[([], [
                C(0, 0, -2, -6, -2, 4, 6, 3),
                C(14, 0, -2, -4, -4, 4, 2, 2),
                # (the wattle's underside lies IN the head's underside for 2 x 1 px: the game draws the wattle last
                #  and so on top; 1/100 px of growth does the same here instead of z-fighting)
                C(14, 4, -1, -2, -3, 2, 2, 2, grow=0.01)])]),
            # legs: one builder, 3 x 5 x 3 at texOffs(26, 0): only the foot (underside) and a 1 px shank have texels
            dict(name="leg_r", parent="hips", pivot=(-2, 19, 1), groups=[([], [C(26, 0, -1, 0, -3, 3, 5, 3)])]),
            dict(name="leg_l", parent="hips", pivot=(1, 19, 1), groups=[([], [C(26, 0, -1, 0, -3, 3, 5, 3)])]),
            dict(name="wing_r", parent="body", pivot=(-4, 13, 0), groups=[([], [C(24, 13, 0, 0, -3, 1, 4, 6)])]),
            dict(name="wing_l", parent="body", pivot=(4, 13, 0), groups=[([], [C(24, 13, -1, 0, -3, 1, 4, 6)])]),
        ])


def _chick_spec():
    """net.minecraft.client.model.animal.chicken.BabyChickenModel.createBodyLayer(): the dedicated baby model of
    26.x (ModelLayers.CHICKEN_BABY), 16 x 16, unscaled. No head part: body + beak are one box group; legs and
    wings are zero-thickness boxes. The class calls the part on the +x side 'right_wing' and the one on the -x
    side 'left_wing' (the opposite of the adult): transcribed as it is, so wing_l here is the game's right_wing."""
    C, P = ch._cube, ch._pose
    return dict(
        tex=(16, 16), scale=1.0, hip=22.0, top=18.0, eye=24.0 - CHICK_EYE * 16.0, back=2.0, sleep_eye=CHICK_EYE,
        parts=[
            # body: PartPose.offset(0, 20.25, -1.25); the 4 x 4 x 4 body and the beak
            dict(name="body", parent="hips", pivot=(0, 22, 0), groups=[([P(0, 20.25 - 22.0, -1.25)], [
                C(0, 0, -2, -2.25, -0.75, 4, 4, 4),
                C(10, 8, -1, -0.25, -1.75, 2, 1, 1)])]),
            dict(name="leg_l", parent="hips", pivot=(1, 22, 0.5), groups=[([], [
                C(2, 2, -0.5, 0, 0, 1, 2, 0),
                C(0, 1, -0.5, 2, -1, 1, 0, 1)])]),
            dict(name="leg_r", parent="hips", pivot=(-1, 22, 0.5), groups=[([], [
                C(0, 2, -0.5, 0, 0, 1, 2, 0),
                C(0, 0, -0.5, 2, -1, 1, 0, 1)])]),
            dict(name="wing_l", parent="body", pivot=(2, 20, 0), groups=[([], [C(6, 8, 0, 0, -1, 1, 0, 2)])]),    # 'right_wing'
            dict(name="wing_r", parent="body", pivot=(-2, 20, 0), groups=[([], [C(4, 8, -1, 0, -1, 1, 0, 2)])]),  # 'left_wing'
        ])


# what the rest of the module needs to know about each of the four rigs (pixels unless noted)
_KINDS = {
    "cow": dict(spec=_cow_spec, texture="entity/cow/cow_temperate", size=COW_SIZE, eye=COW_EYE,
                walk=COW_WALK, tempt=COW_TEMPT, panic=COW_PANIC, food=COW_FOOD, fall=1.0,
                neck=(8.0, 20.0), face=(11.0, 20.0),           # head pivot / middle of the head: (in front, above the feet)
                width=0.75, circles=((0.50, 0.45), (-0.22, 0.45)),   # blocks: body width, (forward, radius) cover circles
                swing=(0.30, 0.90), corner=1.0, stroll=(1.2, 3.2), bob=1.0),
    "calf": dict(spec=_calf_spec, texture="entity/cow/cow_temperate_baby", size=CALF_SIZE, eye=CALF_EYE,
                 walk=COW_WALK, tempt=COW_TEMPT, panic=COW_PANIC, food=COW_FOOD, fall=1.0,
                 neck=(5.1667, 10.431), face=(7.5, 12.0),
                 width=0.5, circles=((0.33, 0.30), (-0.08, 0.30)),
                 swing=(0.35, 0.90), corner=0.6, stroll=(0.8, 2.6), bob=1.0),
    "chicken": dict(spec=_chicken_spec, texture="entity/chicken/chicken_temperate", size=CHICKEN_SIZE, eye=CHICKEN_EYE,
                    walk=CHICKEN_WALK, tempt=CHICKEN_TEMPT, panic=CHICKEN_PANIC, food=CHICKEN_FOOD, fall=CHICKEN_FALL,
                    neck=(4.0, 9.0), face=(4.5, 12.0),
                    width=0.5, circles=((0.12, 0.38),),
                    swing=(0.35, 0.90), corner=0.5, stroll=(0.8, 2.6), bob=0.35),
    "chick": dict(spec=_chick_spec, texture="entity/chicken/chicken_temperate_baby", size=CHICK_SIZE, eye=CHICK_EYE,
                  walk=CHICKEN_WALK, tempt=CHICK_FOLLOW, panic=CHICKEN_PANIC, food=CHICKEN_FOOD, fall=CHICKEN_FALL,
                  neck=(0.0, 4.0), face=(1.0, 4.0),
                  width=0.25, circles=((0.0, 0.20),),
                  swing=(0.60, 1.00), corner=0.3, stroll=(0.5, 1.8), bob=0.0),
}


def animal_sheet(texture):
    """(key, HxWx4 uint8) an entity texture with its alpha cut at 0.1, as the game's cut-out render type draws it."""
    arr = ch._game_texture(texture)
    sheet = np.zeros_like(arr)
    ch._over(sheet, arr)
    return texture.replace("entity/", "").replace("/", "_"), sheet


def hurt_sheet(sheet):
    """The sheet as the game draws a hurt or dying mob: every texel 178/255 of itself + 77/255 of pure red
    (OverlayTexture row 3 = 0xB2FF0000, mixed in by core/entity.fsh before the light is applied)."""
    out = sheet.copy()
    rgb = out[..., :3].astype(np.float32) * OVERLAY_KEEP
    rgb[..., 0] += 255.0 * (1.0 - OVERLAY_KEEP)
    out[..., :3] = np.clip(np.rint(rgb), 0, 255).astype(np.uint8)
    return out


# ----------------------------------------------------------------------------------------------------
# key helpers
# ----------------------------------------------------------------------------------------------------
def _run(ob, path, index, frames, values):
    """One LINEAR segment through (frames, values) on a channel, held (CONSTANT) after its last key. values[0] None
    = the channel's value at frames[0]. A run of equal values is written as its two ends. Bulk write: a key per
    frame costs nothing."""
    vals = list(values)
    v0 = ch._begin(ob, path, index, frames[0], frames[-1])
    if vals[0] is None:
        vals[0] = v0
    if len(frames) > 2 and all(abs(v - vals[0]) < 1e-9 for v in vals):
        frames, vals = [frames[0], frames[-1]], [vals[0], vals[-1]]
    fc = ch._ensure(ob, path, index)
    ch._put(fc, frames[0], vals[0], "LINEAR" if len(frames) > 1 else "CONSTANT")
    k = len(frames) - 1
    if k > 0:
        kps = fc.keyframe_points
        m = len(kps)
        kps.add(k)
        for i in range(k):
            kp = kps[m + i]
            kp.co = (float(frames[i + 1]), float(vals[i + 1]))
            kp.interpolation = "LINEAR"
        kps[m + k - 1].interpolation = "CONSTANT"
    fc.update()
    return vals[0]


def _smooth(x):
    """Sine ease in-out of x clamped to 0..1."""
    return 0.5 - 0.5 * math.cos(math.pi * ch._clamp(x, 0.0, 1.0))


def knockback_track(strength=KNOCKBACK, max_back=None, fall=1.0, max_ticks=200):
    """LivingEntity.knockback + travelInAir from a standing start: [(blocks back, blocks up)] after tick 0, 1, 2 ...
    until the mob lies still. Speed (strength, min(0.4, -0.0784 / 2 + strength)); every tick: move, then
    vertical speed = (v - 0.08) * 0.98 and horizontal speed * 0.546 (it stood on the ground when the tick began)
    or * 0.91 (in the air). fall = Chicken.aiStep's 0.6 on a falling chicken. max_back = room behind it."""
    if strength <= 0.0:
        return [(0.0, 0.0)]
    vx, vy = float(strength), min(0.4, REST_VY / 2.0 + strength)
    x = y = 0.0
    on_ground = True
    out = [(0.0, 0.0)]
    for _tick in range(max_ticks):
        drag = GROUND_DRAG if on_ground else AIR_DRAG
        x += vx
        if max_back is not None and x > max_back:
            x, vx = float(max_back), 0.0
        y += vy
        on_ground = y <= 0.0
        if on_ground:
            y, vy = 0.0, 0.0
        vy = (vy - GRAVITY) * 0.98
        vx *= drag
        if not on_ground and vy < 0.0:
            vy *= fall
        if abs(vx) < 0.003:                                               # LivingEntity.aiStep
            vx = 0.0
        out.append((x, y))
        if on_ground and vx == 0.0:
            break
    return out


def air_track(vy, drop=0.0, fall=1.0, max_ticks=400):
    """Heights after tick 0, 1, 2 ... of a mob that leaves the ground with vertical speed `vy` (0.42 = a jump,
    0 = it walked off an edge) and lands `drop` blocks lower (negative = higher); the last entry is the landing."""
    y, out = 0.0, [0.0]
    for _tick in range(max_ticks):
        y += vy
        if vy <= 0.0 and y <= -drop:
            out.append(-float(drop))
            break
        vy = (vy - GRAVITY) * 0.98
        if vy < 0.0:
            vy *= fall
        out.append(y)
    return out


def death_angle(ticks):
    """LivingEntityRenderer.setupRotations: degrees the body has tipped `ticks` after the killing blow."""
    if ticks <= 1.0:
        return 0.0
    return DEATH_FLIP * min(1.0, math.sqrt((ticks - 1.0) / 20.0 * 1.6))


# ----------------------------------------------------------------------------------------------------
# the animal
# ----------------------------------------------------------------------------------------------------
class Animal(ch.Character):
    """A cow, calf, chicken or chick as an engine.characters.Character with the game's gait, head and reactions."""

    def __init__(self, name, kind, parts, spec, sheet_key, sheet):
        info = _KINDS[kind]
        self.has_head = "head" in parts
        if not self.has_head:                                            # the chick: its 'head' is its body
            parts = dict(parts, head=parts["body"])
        super().__init__(name, kind, parts, spec, child=kind in ("calf", "chick"))
        if not self.has_head:
            self.parts = {k: v for k, v in self.parts.items() if k != "head"}
        self.baby = self.child
        self.species = "cow" if kind in ("cow", "calf") else "chicken"
        self.info = info
        self.size = info["size"]                                         # the game's hit box (width, height)
        self.width = info["width"]                                       # the body as drawn, across
        self.walk_speed, self.tempt_speed, self.run_speed = info["walk"], info["tempt"], info["panic"]
        self.food = info["food"]
        self.corner = info["corner"]
        self.eye_height = info["eye"]
        unit = self.unit
        pivots = {p["name"]: p["pivot"] for p in spec["parts"]}
        self.legs = {n: parts[n] for n in ("leg_l", "leg_r", "leg_hl", "leg_hr") if n in parts}
        # hip of every leg in the root's frame (blocks): x to the animal's left, y to its BACK (it faces -Y)
        self._hip = {n: (pivots[n][0] * unit, pivots[n][2] * unit) for n in self.legs}
        self.turn_radius = sum(math.hypot(*h) for h in self._hip.values()) / len(self._hip)
        if "leg_hr" in self.legs:                                        # QuadrupedModel.setupAnim: the diagonal pairs
            self.gait_groups = (("leg_hr", "leg_l"), ("leg_hl", "leg_r"))
        else:                                                            # ChickenModel.setupAnim: right leg, left leg
            self.gait_groups = (("leg_r",), ("leg_l",))
        self.wing_l, self.wing_r = parts.get("wing_l"), parts.get("wing_r")
        for ob in list(self.legs.values()) + [w for w in (self.wing_l, self.wing_r) if w is not None]:
            if ob not in (self.leg_l, self.leg_r):
                for i in range(3):
                    self._pose.append((ob, _ROT, i, float(ob.rotation_euler[i])))
        self._sheet = (sheet_key, sheet)
        self._twins = {}                   # part name -> the red twin of that part (built on the first hurt / die)
        self._shown, self._flash, self._gone = [], [], []
        self._foot = 0                     # which pair steps first on the next planted walk
        self._walk_pos = 0.0               # the game's walkAnimation.position (gait="vanilla" and hurt carry it)
        self._flap = 0.0                   # Chicken.flap
        self.last_walk = None
        self.bursts = []

    def __repr__(self):
        return "<Animal %s %s>" % (self.name, self.kind)

    # ------------------------------------------------------------------ queries
    def _forward(self, frame, ahead, up):
        """World point `ahead` blocks in front of the feet and `up` above them at `frame`."""
        p, yaw = self.pos_at(frame), self.yaw_at(frame)
        return Vector((p.x + math.sin(yaw) * ahead, p.y - math.cos(yaw) * ahead, p.z + up))

    def eye_point(self, frame):
        """World point in the middle of the head at `frame` (a chick: of its body): look and focus target."""
        ahead, up = self.info["face"]
        return self._forward(frame, ahead * self.unit, up * self.unit)

    def neck_point(self, frame):
        """World point of the head's pivot at `frame`: where its own look starts."""
        ahead, up = self.info["neck"]
        return self._forward(frame, ahead * self.unit, up * self.unit)

    def mouth_point(self, frame):
        """World point just in front of the muzzle / beak at `frame` (where a hand with food is held out to)."""
        ahead, up = self.info["face"]
        return self._forward(frame, (ahead + 5.0) * self.unit, (up - 2.0) * self.unit)

    def _aim(self, target, frame):
        """Head (yaw, pitch-up) toward a target, clamped to the game's 75 / 40 degrees (Mob.getMaxHeadYRot / XRot)."""
        if target is None:
            return 0.0, 0.0
        d = self._point(target, frame) - self.neck_point(frame)
        yaw = ch._clamp(ch._wrap(math.atan2(d.x, -d.y) - self.yaw_at(frame)), -HEAD_YAW_MAX, HEAD_YAW_MAX)
        pitch = ch._clamp(math.atan2(d.z, math.hypot(d.x, d.y)), -HEAD_PITCH_MAX, HEAD_PITCH_MAX)
        return yaw, pitch

    def body_points(self, pos, yaw):
        """[(x, y, radius)] the circles that cover the body standing at `pos` with `yaw` (wander's footprint)."""
        s, c = math.sin(yaw), -math.cos(yaw)
        return [(pos[0] + s * ahead, pos[1] + c * ahead, r) for ahead, r in self.info["circles"]]

    def mesh_parts(self):
        """The mesh objects of the rig (no empties, no red twins)."""
        return [ob for ob in self.parts.values() if ob.type == "MESH"]

    # ------------------------------------------------------------------ visibility (shots x hurt flash x death)
    def _ensure_twins(self):
        """The red copy of every part, parented to it: shown instead of the part while the hurt overlay is on."""
        if self._twins:
            return
        key, sheet = self._sheet
        mat = ch._sheet_material(key + "_hurt", hurt_sheet(sheet))
        col = self.root.users_collection[0]
        for name, ob in self.parts.items():
            if ob.type != "MESH":
                continue
            me = ob.data.copy()
            me.name = ob.data.name + "_hurt"
            me.materials[0] = mat
            twin = bpy.data.objects.new(ob.name + "_hurt", me)
            col.objects.link(twin)
            twin.parent = ob
            twin.matrix_parent_inverse = Matrix.Identity(4)
            twin.hide_render = twin.hide_viewport = True
            self._twins[name] = twin

    def _sync(self):
        """Rewrite the visibility keys: a part is rendered while the animal is shown (show(), a Stage's shots), is
        not dead and gone, and does not flash red; its red twin while it is shown, there, and flashes."""
        frames = sorted({f for f, _v in self._shown} | {f for f, _v in self._gone} | {f for ab in self._flash for f in ab})

        def state(f):
            """(the parts are rendered, the red twins are rendered) at frame f."""
            there = bool(mobs._state_at(self._shown, f, True)) and not bool(mobs._state_at(self._gone, f, False))
            red = any(a <= f < b for a, b in self._flash)
            return there and not red, there and red

        for ob in self.mesh_parts():
            mobs._visibility_curve(ob, [(f, state(f)[0]) for f in frames], before=True)
        for twin in self._twins.values():
            mobs._visibility_curve(twin, [(f, state(f)[1]) for f in frames], before=False)

    def show(self, frame, visible=True):
        """Key render visibility of the whole animal from `frame` on (Stage.finish does this per shot)."""
        self._shown.append((int(round(frame)), bool(visible)))
        self._sync()

    def gone_at(self, frame):
        """True when the animal has died and vanished by `frame` (until its next place())."""
        return bool(mobs._state_at(self._gone, frame, False))

    # ------------------------------------------------------------------ placement
    def place(self, frame, pos, yaw=0.0, keep_pose=False):
        """Hard-set position and yaw from `frame` on: upright, neutral pose, alive again (use at shot cuts)."""
        super().place(frame, pos, yaw, keep_pose=keep_pose)
        f = int(round(frame))
        if not keep_pose:
            for i in (0, 1):
                if ch._find(self.root, _ROT, i) is not None:
                    ch._cut(self.root, _ROT, i, frame, 0.0)             # the tip of a death
        changed = False
        if self.gone_at(f):
            self._gone.append((f, False))
            changed = True
        cut = [(a, min(b, f)) if a < f < b else (a, b) for a, b in self._flash]
        if cut != self._flash:
            self._flash, changed = cut, True
        if changed:
            self._sync()

    def _halt(self, frame):
        """Stop whatever runs at `frame` (a walk, a turn, a look) where it is: every channel holds its value."""
        chans = [(self.root, _LOC, i) for i in range(3)] + [(self.root, _ROT, i) for i in range(3)]
        chans += [(o, p, i) for o, p, i, _rest in self._pose]
        for ob, path, i in chans:
            fc = ch._find(ob, path, i)
            if fc is None or not len(fc.keyframe_points):
                continue
            v = ch._begin(ob, path, i, frame, frame)
            ch._put(fc, frame, v, "CONSTANT")
            fc.update()

    # ------------------------------------------------------------------ locomotion
    def walk(self, frame, points, speed=None, run=False, from_current=False, gait="planted", swing=None, corner=None,
             bob=None):
        """Travel along the polyline `points` at the game's speed (run=True: its panic speed); returns the end frame.

        The animal gets up to speed and stops as a mob does (time constant 2 frames) and takes the corners on
        arcs of radius `corner` (default: its own, a cow 1 block). gait "planted" (default): the game's leg pairs
        and swing for that speed, but the cycle is shortened so that the soles on the ground stay where they were
        put, and the body sinks a little as the legs open. gait "vanilla": exactly the game's leg wave (one cycle
        per 2.36 blocks, babies 0.79: the feet slide) and no bob. swing = planted leg swing in radians. bob = how
        much of that sinking the body does (cow 1: its soles stay on the ground; hen 0.35, chick 0: their steps are
        so quick that the body would tremble, so the foot lifts under a pixel at the ends of a step instead).
        A walk that does not start on a cut and faces another way first turns on the spot (turn()).
        """
        if gait not in ("planted", "vanilla"):
            raise ValueError("gait %r: use 'planted' or 'vanilla'" % (gait,))
        if speed is None:
            speed = self.run_speed if run else self.walk_speed
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
        if teleport:
            for i in range(3):
                ch._cut(self.root, _LOC, i, f0, path[0][i], hold_rest=False)
        if len(path) < 2:
            return f0
        on_cut = teleport or ch._cut_at(self.root, _LOC, 0, f0)
        radius = self.corner if corner is None else float(corner)
        route = mobs._Route(path, radius, yaw_now)
        if route.sharp and len(path) > 2:                               # a corner that cannot be rounded: stop, turn, go on
            end = f0
            for a, b in zip(path, path[1:]):
                end = self.walk(end, [a, b], speed=speed, gait=gait, swing=swing, corner=corner, bob=bob)
            return end
        heading0 = route.headings[0]
        if on_cut:
            ch._cut(self.root, _ROT, 2, f0, heading0, hold_rest=False)  # starting on a cut: already facing its way
        elif abs(heading0 - yaw_now) > 0.03:
            f0 = self.turn(f0, heading0, gait=gait)
        total = route.total
        per_frame = max(float(speed), 1e-3) / FPS
        push = total / per_frame                                         # frames for which it is driven
        n = max(2, int(math.ceil(push + BRAKE_TAUS * SPEED_TAU)))
        tau = SPEED_TAU
        v_end = per_frame * (1.0 - math.exp(-push / tau))
        d_end = per_frame * (push - tau * (1.0 - math.exp(-push / tau)))

        def dist(t):
            """Blocks covered t frames into the walk: v' = (cruise - v) / tau while pushed, then v' = -v / tau."""
            if t <= push:
                return per_frame * (t - tau * (1.0 - math.exp(-t / tau)))
            return d_end + v_end * tau * (1.0 - math.exp(-(t - push) / tau))

        frames = [float(f0 + k) for k in range(n + 1)]
        ds = [min(dist(float(k)), total) for k in range(n + 1)]
        ds[-1] = total
        spots = [route.point(d) for d in ds]
        yaws = [heading0 + route.turned(d) for d in ds]
        self._travel(frames, spots, yaws, gait=gait, swing=swing, bob=bob)
        self.last_walk.update(speed=float(speed), blocks=total, frames=(f0, f0 + n),
                              corners=[(round(rad, 3), round(math.degrees(turn), 1)) for _a, _b, turn, rad in route.arcs])
        return f0 + n

    def _travel(self, frames, spots, yaws, gait="planted", swing=None, bob=None):
        """Key a root trajectory (a position and a yaw per entry of `frames`) and the legs that carry it."""
        fts = np.array(frames, dtype=np.float64)
        xs = np.array([p[0] for p in spots], dtype=np.float64)
        ys = np.array([p[1] for p in spots], dtype=np.float64)
        zs = np.array([p[2] for p in spots], dtype=np.float64)
        yw = np.array(yaws, dtype=np.float64)
        frames = [float(f) for f in frames]
        for i, arr in enumerate((xs, ys, zs)):
            _run(self.root, _LOC, i, frames, arr.tolist())
        _run(self.root, _ROT, 2, frames, yw.tolist())
        moved = np.hypot(np.diff(xs), np.diff(ys))
        dist = np.concatenate([[0.0], np.cumsum(moved)])
        # the stride parameter: ground passed under the feet, by travelling and by turning
        s = np.concatenate([[0.0], np.cumsum(moved + np.abs(np.diff(yw)) * self.turn_radius)])
        s = s + np.arange(len(s)) * 1e-9                                 # strictly increasing: np.interp needs it
        total = float(s[-1])
        self.last_walk = dict(gait=gait, frames=(frames[0], frames[-1]), blocks=float(dist[-1]), steps=0, swing=0.0,
                              stance=[], cycle_frames=None)
        if total < 0.05 or not gait:
            return
        if gait == "vanilla":
            if dist[-1] > 1e-3:
                self._legs_vanilla(frames, fts, dist)
            return
        L = self.leg_len
        peak = float(np.max(moved / np.maximum(np.diff(fts), 1e-9))) if len(fts) > 1 else 0.0     # blocks per frame
        lo, hi = self.info["swing"]
        if swing is None:
            swing = ch._clamp(LEG_SWING * min(ANIM_PER_BLOCK * peak * TICK, 1.0), lo, hi)       # the game's, bounded
        step = 2.0 * L * math.sin(ch._clamp(float(swing), 0.05, 1.3))
        steps = max(1, int(math.ceil(total / step - 0.15)))             # rather one step more than a lunge
        turning = dist[-1] < 1e-3
        if turning:
            if total < 0.3 * step:
                return                                                   # a small turn: the feet stay
            steps = max(2, steps + steps % 2)                            # both pairs step
        step = total / steps
        marks_s = [0.0] + [(k + 0.5) * step for k in range(steps)] + [total]
        marks = [float(t) for t in np.interp(marks_s, s, fts)]
        marks[0], marks[-1] = frames[0], frames[-1]
        last = len(marks) - 2
        groups, first = self.gait_groups, self._foot
        self._foot = (first + steps) % 2

        def pose(t):
            """(x, y, yaw) of the root at time t."""
            return float(np.interp(t, fts, xs)), float(np.interp(t, fts, ys)), float(np.interp(t, fts, yw))

        def hip(leg, t):
            """World (x, y) of a leg's hip at time t."""
            px, py, yaw = pose(t)
            hx, hy = self._hip[leg]
            c, sn = math.cos(yaw), math.sin(yaw)
            return px + c * hx - sn * hy, py + sn * hx + c * hy

        plant = {}                                                       # (leg, interval) -> where its sole stands
        for j in range(last + 1):
            for leg in groups[(first + j) % 2]:
                a, b = hip(leg, marks[j]), hip(leg, marks[j + 1])
                plant[(leg, j)] = a if j == 0 else (b if j == last else ((a[0] + b[0]) / 2.0, (a[1] + b[1]) / 2.0))

        def planted(leg, j, t):
            """(to its left, forward) of the sole planted in interval j, from the leg's hip, at time t."""
            px, py = plant[(leg, j)]
            hx, hy = hip(leg, t)
            yaw = pose(t)[2]
            dx, dy = px - hx, py - hy
            c, sn = math.cos(yaw), math.sin(yaw)
            return c * dx + sn * dy, -(-sn * dx + c * dy)

        def sole(leg, t):
            """((to its left, forward) of the leg's sole from its hip at time t, is it standing on it)."""
            j = min(max(bisect.bisect_right(marks, t) - 1, 0), last)
            if leg in groups[(first + j) % 2]:
                return planted(leg, j, t), True
            a = planted(leg, j - 1, marks[j]) if j > 0 else (0.0, 0.0)
            b = planted(leg, j + 1, marks[j + 1]) if j < last else (0.0, 0.0)
            sa, sb = marks_s[j], marks_s[j + 1]
            u = ch._clamp((float(np.interp(t, fts, s)) - sa) / (sb - sa), 0.0, 1.0) if sb > sa else 1.0
            return (a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u), False

        # a key on every frame, on every change of the standing pair, and five more inside every step (short legs
        # take a step in under two frames: linear keys a frame apart would let their soles float)
        inner = {a + (b - a) * q / 6.0 for a, b in zip(marks, marks[1:]) for q in range(1, 6)}
        times = mobs._dedupe(set(frames) | set(marks) | inner, eps=0.011)
        reach = math.sin(1.35)
        pitch = {leg: [] for leg in self.legs}
        roll = {leg: [] for leg in self.legs}
        drop = []
        for t in times:
            sink = []
            for leg in self.legs:
                (side, fore), stance = sole(leg, t)
                th = -math.asin(ch._clamp(fore / L, -reach, reach))
                ph = -math.asin(ch._clamp(side / (L * math.cos(th)), -0.7, 0.7))
                pitch[leg].append(th)
                roll[leg].append(ph)
                if stance:
                    sink.append(L * (1.0 - math.cos(th) * math.cos(ph)))
            drop.append(sum(sink) / len(sink) if sink else 0.0)
        for leg, ob in self.legs.items():
            _run(ob, _ROT, 0, times, [None] + pitch[leg][1:])
            if max(abs(v) for v in roll[leg]) > 1e-4 or ch._find(ob, _ROT, 1) is not None:
                _run(ob, _ROT, 1, times, [None] + roll[leg][1:])
        rest_z = self._rest(self.hips, _LOC, 2)
        bob = self.info["bob"] if bob is None else float(bob)
        if bob > 0.0 or ch._find(self.hips, _LOC, 2) is not None:
            _run(self.hips, _LOC, 2, times, [None] + [rest_z - bob * d for d in drop[1:]])
        per_frame = float(dist[-1]) / max(frames[-1] - frames[0], 1e-9)
        self.last_walk.update(steps=steps, swing=math.asin(ch._clamp(step / (2.0 * L), 0.0, 1.0)),
                              stance=[(marks[j], marks[j + 1], groups[(first + j) % 2]) for j in range(last + 1)],
                              cycle_blocks=2.0 * step, cycle_frames=(2.0 * step / peak) if peak > 1e-9 else None,
                              mean_speed=per_frame * FPS, bob=bob, sink=max(drop) if drop else 0.0)

    def _legs_vanilla(self, frames, fts, dist):
        """The game's own leg wave for a keyed trajectory: WalkAnimationState ticked along the distance covered."""
        f0, f1 = frames[0], frames[-1]
        scale = BABY_ANIM_SCALE if self.baby else 1.0
        speed, pos, prev = 0.0, self._walk_pos, 0.0
        times, vals, peak = [f0], [None], 0.0
        for k in range(1, 6000):
            t = f0 + k * TICK
            d = float(np.interp(min(t, f1), fts, dist))
            speed += (min(ANIM_PER_BLOCK * (d - prev), 1.0) - speed) * ANIM_LERP
            prev = d
            pos += speed
            peak = max(peak, speed)
            times.append(t)
            vals.append(math.cos(pos * scale * LEG_RATE) * LEG_SWING * min(speed, 1.0))
            if t >= f1 and speed < 0.004:
                break
        vals[-1] = 0.0
        self._walk_pos = pos
        a, b = self.gait_groups
        for leg in a:
            _run(self.legs[leg], _ROT, 0, times, vals)
        for leg in b:
            _run(self.legs[leg], _ROT, 0, times, [None] + [-v for v in vals[1:]])
        self.last_walk.update(swing=LEG_SWING * min(peak, 1.0), cycle_blocks=VANILLA_CYCLE / scale)

    def turn(self, frame, yaw, ease=None, gait="planted"):
        """Turn the body on the spot to an absolute yaw (radians, 0 faces -Y) the short way round; returns the end
        frame. gait "planted": the leg pairs step round with it; "vanilla": the legs stand still, as in the game."""
        f0 = int(round(frame))
        yaw0 = self.yaw_at(f0)
        d = ch._wrap(yaw - yaw0)
        if abs(d) < 1e-4:
            return f0
        n = int(ease) if ease is not None else max(4, int(round(TURN_FRAMES * min(1.0, abs(d) / 0.8))))
        if n <= 0:
            ch._cut(self.root, _ROT, 2, f0, yaw0 + d)
            return f0
        here = self.pos_at(f0)
        frames = [float(f0 + k) for k in range(n + 1)]
        self._travel(frames, [here] * (n + 1), [yaw0 + d * _smooth(k / float(n)) for k in range(n + 1)],
                     gait="planted" if gait == "planted" else None)
        return f0 + n

    def face(self, frame, target, ease=None, keep_head=False, gait="planted"):
        """Turn the whole body toward a world point / Character / Object (the head re-centres); returns the end frame."""
        f0 = int(round(frame))
        pos = self.pos_at(f0)
        d = self._point(target, f0 + (TURN_FRAMES if ease is None else max(0, int(ease)))) - pos
        if math.hypot(d.x, d.y) < 1e-5:
            return f0
        end = self.turn(f0, math.atan2(d.x, -d.y), ease=ease, gait=gait)
        if self.has_head and not keep_head and abs(ch._val(self.head, _ROT, 2, f0)) > 1e-3:
            ch._ease(self.head, _ROT, 2, f0, max(end, f0 + 1), 0.0)
        return end

    # ------------------------------------------------------------------ looking
    def look_at(self, frame, target, ease=6):
        """Turn the head toward a point / Character / Object over `ease` frames, clamped to 75 / 40 degrees; None =
        straight ahead. A chick has no head: it turns its whole body, as it does in the game."""
        if self.has_head:
            return super().look_at(frame, target, ease)
        if target is None:
            return frame
        return self.face(frame, target, ease=max(0, int(ease)))

    def track(self, frame_start, frame_end, target, step=3, ease=6):
        """Keep the head on a (moving) target from frame_start to frame_end (a chick: nothing, it has no head)."""
        if self.has_head:
            return super().track(frame_start, frame_end, target, step=step, ease=ease)
        return int(frame_end)

    def idle(self, frame_start, frame_end, seed=0, watch=None, rate=1.0):
        """Alive while standing from frame_start to frame_end: the head turns to look somewhere for 1-2 s and comes
        back (RandomLookAroundGoal), at the game's 10 degrees per tick. watch = a Character / point it also looks
        at now and then for 2-4 s (LookAtPlayerGoal, within 6 blocks). rate = how often (1 = the game's). A chick
        has no head: it turns a little on the spot instead."""
        f0, f1 = int(frame_start), int(frame_end)
        if f1 - f0 < 14:
            return
        r = pix.rng(5381 * (int(seed) + 1) + 17)
        if not self.has_head:
            t = f0 + int(r.integers(4, 40))
            while t + TURN_FRAMES + 6 < f1:
                t = self.turn(t, self.yaw_at(t) + float(r.uniform(-1.0, 1.0)))
                t += int(r.integers(24, 90) / max(rate, 0.05))
            return
        base_y = ch._val(self.head, _ROT, 2, f0)
        base_p = ch._val(self.head, _ROT, 0, f0)
        yk, pk = [(f0, None, "LINEAR")], [(f0, None, "LINEAR")]
        cur_y, cur_p = base_y, base_p
        t = f0 + float(r.integers(2, 26))
        while True:
            watching = watch is not None and (self._point(watch, t) - self.pos_at(t)).length <= LOOK_AT_PLAYER \
                and r.random() < 0.5
            if watching:
                hold = float(r.integers(*WATCH_TICKS)) * TICK
                ty, tp = self._aim(watch, t)
                tp = -tp
            else:
                hold = float(r.integers(*LOOK_TICKS)) * TICK
                ty, tp = float(r.uniform(math.radians(20.0), HEAD_YAW_MAX)) * (1.0 if r.random() < 0.5 else -1.0), 0.0
            dur = max(2.0, abs(ty - cur_y) / HEAD_SPEED)
            home = max(2.0, abs(ty - base_y) / HEAD_SPEED)
            if t + dur + hold + home > f1 - 1:
                break
            yk += [(t, cur_y, "LINEAR"), (t + dur, ty, "LINEAR"), (t + dur + hold, ty, "LINEAR"), (t + dur + hold + home, base_y, "LINEAR")]
            pk += [(t, cur_p, "LINEAR"), (t + dur, tp, "LINEAR"), (t + dur + hold, tp, "LINEAR"), (t + dur + hold + home, base_p, "LINEAR")]
            cur_y, cur_p = base_y, base_p
            t += dur + hold + home + float(ch._clamp(r.exponential(50.0), 6.0, 160.0)) * TICK / max(rate, 0.05)
        if len(yk) > 1:
            yk.append((f1, base_y))
            pk.append((f1, base_p))
            ch._segment(self.head, _ROT, 2, yk, "LINEAR")
            if any(abs(k[1] - base_p) > 1e-6 for k in pk[1:]):
                ch._segment(self.head, _ROT, 0, pk, "LINEAR")

    # ------------------------------------------------------------------ gestures that an animal does not have
    def flinch(self, frame):
        """Startled: a small hop on the spot (8 frames); returns the end frame."""
        ch._offsets(self.hips, _LOC, 2, frame, [(2, 0.08 * self.leg_len / 0.75), (5, 0.0), (8, 0.0)])
        return frame + 8

    def swing_arm(self, frame):
        """An animal has no arm to swing: nothing happens. Returns `frame`."""
        return frame

    def raise_arm(self, frame, angle=65.0, ease=8, side="r"):
        """An animal has no arm to raise: nothing happens. Returns `frame`."""
        return frame

    def hold(self, obj, offset=None, rotation=None):
        """Animals hold nothing in the game: raises."""
        if obj is None:
            return None
        raise ValueError("%s cannot hold an item (give it to the player: steve.hold(props.make_item('wheat')))" % self.name)

    def lie_down(self, frame, bed_pos, yaw, lift=0.125):
        """Animals do not sleep in beds: raises."""
        raise ValueError("%s cannot lie down in a bed" % self.name)

    # ------------------------------------------------------------------ in the air
    def _airborne(self, f0, f1):
        """What a species does while it is off the ground between two frames (chickens flap)."""

    def hop(self, frame, to=None, speed=None):
        """Jump (LivingEntity.jumpFromGround: 0.42 blocks per tick up, apex 1.25) from where it stands to the point
        `to`, which may lie up to a block higher or any amount lower; to=None: straight up and down. The body
        travels in a straight line while it is in the air. A chicken flaps and comes down slowly. Returns the
        landing frame."""
        f0 = int(round(frame))
        here = self.pos_at(f0)
        there = here.copy() if to is None else ch._vec3(to, here.z)
        d = there - here
        if math.hypot(d.x, d.y) > 1e-4:
            f0 = self.turn(f0, math.atan2(d.x, -d.y))
        heights = air_track(JUMP, drop=here.z - there.z, fall=self.info["fall"])
        return self._fly(f0, here, there, heights)

    def fall(self, frame, to):
        """Step off an edge at `frame` and come down on the point `to` (lower than where it stands): the game's
        fall, 0.08 blocks per tick^2 with 2 % drag; a chicken sinks at 2.3 blocks/s with its wings beating.
        Returns the landing frame."""
        f0 = int(round(frame))
        here = self.pos_at(f0)
        there = ch._vec3(to, here.z)
        return self._fly(f0, here, there, air_track(0.0, drop=here.z - there.z, fall=self.info["fall"]))

    def _fly(self, f0, here, there, heights):
        self._halt(f0)
        n = len(heights) - 1
        frames = [f0 + k * TICK for k in range(n + 1)]
        for i in (0, 1):
            _run(self.root, _LOC, i, frames, [here[i] + (there[i] - here[i]) * k / float(n) for k in range(n + 1)])
        _run(self.root, _LOC, 2, frames, [here.z + h for h in heights[:-1]] + [there.z])
        self._airborne(f0, frames[-1])
        return int(math.ceil(frames[-1]))

    # ------------------------------------------------------------------ hurt and death
    def _away(self, frame, attacker):
        """Unit vector (x, y) a blow from `attacker` (Character / point / None = from the front) throws it."""
        here = self.pos_at(frame)
        if attacker is not None:
            a = attacker.pos_at(frame) if isinstance(attacker, ch.Character) else ch._vec3(attacker)
            d = Vector((here.x - a.x, here.y - a.y))
            if d.length > 1e-4:
                return d.normalized()
        yaw = self.yaw_at(frame)
        return Vector((-math.sin(yaw), math.cos(yaw)))

    def _knock(self, f0, attacker, knockback, max_back, flail):
        """The knock-back hop from frame f0 and (flail) the legs of a mob that was hit; returns (landing, rest) frames."""
        strength = KNOCKBACK * (float(knockback) if not isinstance(knockback, bool) else (1.0 if knockback else 0.0))
        track = knockback_track(strength, max_back, fall=self.info["fall"])
        here, away = self.pos_at(f0), self._away(f0, attacker)
        n = len(track) - 1
        landing = rest = float(f0)
        if n > 0:
            frames = [f0 + k * TICK for k in range(n + 1)]
            _run(self.root, _LOC, 0, frames, [here.x + away.x * b for b, _u in track])
            _run(self.root, _LOC, 1, frames, [here.y + away.y * b for b, _u in track])
            _run(self.root, _LOC, 2, frames, [here.z + u for _b, u in track])
            air = [k for k in range(n + 1) if track[k][1] > 0.0]
            landing = f0 + (max(air) + 1) * TICK if air else float(f0)
            rest = frames[-1]
            if air:
                self._airborne(f0, landing)
        if flail:
            # LivingEntity.handleDamageEvent: walkAnimation.setSpeed(1.5); then the usual update every tick
            scale = BABY_ANIM_SCALE if self.baby else 1.0
            speed, pos, prev = HURT_ANIM_SPEED, self._walk_pos, 0.0
            times, vals = [float(f0), f0 + TICK], [None, math.cos(pos * scale * LEG_RATE) * LEG_SWING]
            for k in range(1, 400):
                back = track[min(k, n)][0]
                speed += (min(ANIM_PER_BLOCK * (back - prev), 1.0) - speed) * ANIM_LERP
                prev = back
                pos += speed
                times.append(f0 + (k + 1) * TICK)
                vals.append(math.cos(pos * scale * LEG_RATE) * LEG_SWING * min(speed, 1.0))
                if k >= n and speed < 0.004:
                    break
            vals[-1] = 0.0
            self._walk_pos = pos
            a, b = self.gait_groups
            for leg in a:
                _run(self.legs[leg], _ROT, 0, times, vals)
            for leg in b:
                _run(self.legs[leg], _ROT, 0, times, [None] + [-v for v in vals[1:]])
            rest = max(rest, times[-1])
        return landing, rest

    def hurt(self, frame, attacker=None, knockback=True, max_back=None, flash=True):
        """The game's hurt on `frame`: red for 10 ticks (12 frames), the knock-back hop away from `attacker` (a
        Character or a point; None = straight back): 0.96 block up, 2.0 back, on the ground again after 10 ticks
        (a chicken floats down with beating wings: 16 ticks, 2.35 back), and the legs flailing as the game's walk
        animation does when a mob is hit. knockback=False: only the flash; a number scales the blow. max_back =
        blocks of room behind it (a fence). A walk that is running stops here. Returns the frame it stands again."""
        f0 = int(round(frame))
        self._halt(f0)
        if flash:
            self._ensure_twins()
            self._flash.append((f0, f0 + HURT_FRAMES))
            self._sync()
        landing, _rest = self._knock(f0, attacker, knockback, max_back, flail=True)
        return int(math.ceil(max(landing, f0 + 1)))

    def die(self, frame, camera=None, attacker=None, knockback=True, max_back=None, poof=True, seed=0, village=None,
            glow=None):
        """The game's death on `frame`: red from then on, knocked back like any blow, legs straight, and from one
        tick later the body tips over to its LEFT about its feet (90 degrees * sqrt((tick - 1) * 0.08): flat after
        13.5 ticks). On tick 20 (frame + 24, the return value) it is gone and the 20 white poof particles appear
        around its upright hit box and rise (camera = the Shot that films it, a Film or a camera object; they face
        it). Bloodless. It stays gone until its next place()."""
        f0 = int(round(frame))
        gone = f0 + DEATH_FRAMES
        # LivingEntityRenderer.extractRenderState: a dead mob's walk animation is 0 (a hard cut, before the halt:
        # the halt then holds the straight legs)
        for ob in self.legs.values():
            for i in (0, 1):
                if ch._find(ob, _ROT, i) is not None or i == 0:
                    ch._cut(ob, _ROT, i, f0, 0.0)
        if ch._find(self.hips, _LOC, 2) is not None:
            ch._cut(self.hips, _LOC, 2, f0, self._rest(self.hips, _LOC, 2))
        self._halt(f0)
        self._ensure_twins()
        self._flash.append((f0, gone))
        self._gone.append((gone, True))
        self._sync()
        self._knock(f0, attacker, knockback, max_back, flail=False)
        ticks = [1.0, 1.02, 1.08, 1.2, 1.4, 1.7] + [2.0 + 0.5 * k for k in range(24)]
        _run(self.root, _ROT, 1, [float(f0)] + [f0 + t * TICK for t in ticks],
             [0.0] + [math.radians(death_angle(t)) for t in ticks])
        if poof:
            self.bursts.append(_cloud(self.pos_at(gone), gone, camera=camera, seed=seed, village=village, glow=glow,
                                      size=self.size))
        return gone


class Cow(Animal):
    """The vanilla cow / calf."""


class Chicken(Animal):
    """The vanilla chicken / chick: flaps whenever it is in the air."""

    def flap(self, frame_start, frame_end):
        """Beat the wings as the game does while the chicken is off the ground from frame_start to frame_end:
        (sin(flap) + 1) * flapSpeed radians (0 to 115 degrees), flap advancing 1.8 radians a tick (one beat per
        4.19 frames); once it lands the wings fold within 4 ticks. hop(), fall() and hurt() call this themselves.
        Returns the frame the wings are folded again."""
        if self.wing_r is None:
            return int(frame_end)
        f0, f1 = float(frame_start), float(frame_end)
        speed, flapping, phase = 0.0, 1.0, self._flap
        states = [(phase, speed)]
        for k in range(1, 4000):
            in_air = f0 + (k - 1) * TICK < f1 - 1e-6
            speed = ch._clamp(speed + (FLAP_UP if in_air else FLAP_DOWN), 0.0, 1.0)
            if in_air:
                flapping = 1.0
            flapping *= FLAP_DECAY
            phase += flapping * FLAP_STEP
            states.append((phase, speed))
            if not in_air and speed <= 0.0:
                break
        self._flap = phase % (2.0 * math.pi)
        times, vals = [], []
        for k, ((p0, s0), (p1, s1)) in enumerate(zip(states, states[1:])):
            for q in range(4):                                           # the renderer lerps flap and flapSpeed
                u = q / 4.0
                times.append(f0 + (k + u) * TICK)
                vals.append((math.sin(p0 + (p1 - p0) * u) + 1.0) * (s0 + (s1 - s0) * u))
        end = f0 + (len(states) - 1) * TICK
        times.append(end)
        vals.append(0.0)
        # adult: rightWing.zRot = +f, leftWing.zRot = -f. The chick's 'right_wing' is the part on its LEFT (wing_l here)
        sign = -1.0 if self.baby else 1.0
        _run(self.wing_r, _ROT, 1, times, [None] + [sign * v for v in vals[1:]])
        _run(self.wing_l, _ROT, 1, times, [None] + [-sign * v for v in vals[1:]])
        return int(math.ceil(end))

    def _airborne(self, f0, f1):
        self.flap(f0, f1)


# ----------------------------------------------------------------------------------------------------
# factories
# ----------------------------------------------------------------------------------------------------
def _make(name, kind, collection=None):
    info = _KINDS[kind]
    spec = info["spec"]()
    key, sheet = animal_sheet(info["texture"])
    col = ch._collection(collection)
    parts = ch._build_rig(name, spec, sheet, ch._sheet_material(key, sheet), col)
    if kind in ("chicken", "chick"):
        parts["hips"].location.z += GROUND_EPS
    cls = Cow if kind in ("cow", "calf") else Chicken
    return cls(name, kind, parts, spec, key, sheet)


def make_cow(name="cow", baby=False, collection=None):
    """Build the vanilla cow (CowModel; 1.56 tall to the horn tips, 1.56 long) or, baby=True, the calf of 26.x
    (BabyCowModel, 1.0 tall), feet at the origin, facing -Y, with entity/cow/cow_temperate[_baby].png."""
    return _make(name, "calf" if baby else "cow", collection)


def make_chicken(name="chicken", baby=False, collection=None):
    """Build the vanilla chicken (AdultChickenModel; 0.94 tall) or, baby=True, the chick of 26.x (BabyChickenModel,
    0.375 tall), feet at the origin, facing -Y, with entity/chicken/chicken_temperate[_baby].png."""
    return _make(name, "chick" if baby else "chicken", collection)


def add_cow(st, name="cow", baby=False):
    """A cow (baby=True: a calf) registered with a films.lookdev.Stage: st.use(shot, cow), st.hero(shot, "cow", cow)."""
    c = st.cast.get(name)
    if c is None:
        c = st.cast[name] = make_cow(name, baby=baby)
    return c


def add_chicken(st, name="chicken", baby=False):
    """A chicken (baby=True: a chick) registered with a films.lookdev.Stage."""
    c = st.cast.get(name)
    if c is None:
        c = st.cast[name] = make_chicken(name, baby=baby)
    return c


# ----------------------------------------------------------------------------------------------------
# particles: the death poof and the hearts
# ----------------------------------------------------------------------------------------------------
def _puff_mesh(sprite, grey, glow):
    """One poof sprite as a mesh in the local XY plane (-1..1, the game's particle quad): only its opaque texels,
    cut out of the geometry, so that a cloud of forty overlapping puffs costs no transparent bounces (a ray through
    more cut-out layers than look.setup_render allows, 12, renders black). Normals as engine.fx gives its quads:
    along local +Y, the camera's up once the quad copies its rotation, so a puff is lit like an up-facing surface."""
    from . import fx

    name = "animals_poof_%s_%g_%g" % (sprite, grey, glow)
    me = bpy.data.meshes.get(name)
    if me is not None:
        return me
    arr = np.array(mc.texture_array("particle/" + sprite), dtype=np.uint8)
    h, w = arr.shape[:2]
    verts, faces, uvs = [], [], []
    e = 0.02
    for c0, r0, c1, r1 in ch._rects(arr[..., 3] >= ch.ALPHA_CUTOUT):
        x0, x1, y0, y1 = -1.0 + 2.0 * c0 / w, -1.0 + 2.0 * c1 / w, 1.0 - 2.0 * r1 / h, 1.0 - 2.0 * r0 / h
        n = len(verts)
        verts += [(x0, y0, 0.0), (x1, y0, 0.0), (x1, y1, 0.0), (x0, y1, 0.0)]
        faces.append((n, n + 1, n + 2, n + 3))
        uvs += [((c0 + e) / w, 1.0 - (r1 - e) / h), ((c1 - e) / w, 1.0 - (r1 - e) / h),
                ((c1 - e) / w, 1.0 - (r0 + e) / h), ((c0 + e) / w, 1.0 - (r0 + e) / h)]
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    layer = me.uv_layers.new(name="UVMap")
    layer.data.foreach_set("uv", [c for uv in uvs for c in uv])
    me.materials.append(fx._particle_material("particle/" + sprite, colour=grey ** 2.2, glow=glow))
    me.polygons.foreach_set("use_smooth", [True] * len(faces))
    me.normals_split_custom_set([(0.0, 1.0, 0.0)] * (4 * len(faces)))
    me.update()
    return me


def _lit_from_behind(objects):
    """Particle quads carry normals a quarter turn off their plane, and Cycles then moves the start of their shadow
    rays along the quad (shadow terminator geometry offset, 0.1 by default): a quad that touches the ground with
    the sun behind it starts those rays under the ground and renders in shadow, slate blue. Switched off here."""
    for ob in objects:
        ob.shadow_terminator_geometry_offset = 0.0


def poof(target, frame, camera=None, seed=0, village=None, glow=None, size=None, count=POOF_COUNT, collection=None):
    """The white cloud a mob leaves when it dies (entity event 60, LivingEntity.makePoofParticles): `count` (20)
    'poof' particles around the hit box `size` = (width, height) standing at `target` (a Character: its feet at
    `frame`, or a feet point), appearing ON `frame`. Each is the game's ExplodeParticle: it starts within +-width
    of the middle and anywhere up the height, drifts at up to 0.07 blocks per tick, rises (gravity -0.1, friction
    0.9), is 0.2 to 1.4 blocks wide, lives 18 to 82 ticks and runs through the sprites generic_7 ... generic_0
    as it ages. camera = the Shot / Film / camera object the quads face. glow = self-light (default POOF_GLOW).
    village = the Village: the puffs then stop at its blocks. Returns an engine.fx Burst."""
    from . import fx

    frame = int(frame)
    if isinstance(target, ch.Character):
        if size is None:
            size = getattr(target, "size", fx.VILLAGER_SIZE)
        feet = target.pos_at(frame)
    else:
        feet = ch._vec3(target)
    w, h = size if size is not None else fx.VILLAGER_SIZE
    glow = POOF_GLOW if glow is None else float(glow)
    rng = fx._rng(seed, frame, 60, int(feet.x * 16), int(feet.y * 16))
    burst = fx.Burst("poof", frame)
    cams = fx._camera_arg(camera)
    col = fx._collection(collection)
    solids = fx._Solids(village) if village is not None else None
    n_sprites = len(POOF_SPRITES)
    for i in range(int(count)):
        va = rng.normal(0.0, 1.0, 3) * 0.02                              # nextGaussian() * 0.02 per axis
        p = np.array([feet.x + w * (2.0 * rng.random() - 1.0), feet.y + w * (2.0 * rng.random() - 1.0),
                      feet.z + h * rng.random()]) - va * 10.0            # getRandomX(1) - d * 10, getRandomY() - e * 10
        v = va + (rng.random(3) * 2.0 - 1.0) * 0.05                      # ExplodeParticle: xd = xa + (r * 2 - 1) * 0.05
        grey = round((rng.random() * 0.3 + 0.7) * 10.0) / 10.0           # rCol = gCol = bCol = r * 0.3 + 0.7
        quad = 0.1 * (rng.random() * rng.random() * 6.0 + 1.0)           # quadSize
        life = int(16.0 / (rng.random() * 0.8 + 0.2)) + 2                # lifetime
        path = fx._simulate(p, v, life, -0.1 * 0.04, 0.9, solids, 0.2, rng)
        n = len(path) - 1
        for k in range(n_sprites):                                       # SpriteSet.get(age, lifetime): age * 7 / lifetime
            a0 = -(-k * life // (n_sprites - 1))
            a1 = min(n, -(-(k + 1) * life // (n_sprites - 1)) - 1)
            if a1 < a0:
                continue
            first = int(math.ceil(frame + a0 * TICK - 1e-6))
            last = int(math.ceil(frame + (a1 + 1) * TICK - 1e-6))
            if a0 == 0:
                first = frame
            if last <= first:
                continue
            ob = fx._particle_object(burst, "poof_%d_%d_%d" % (frame, i, k), _puff_mesh(POOF_SPRITES[k], grey, glow),
                                     path, float(frame), quad, cams, col)
            for path_name in ("hide_render", "hide_viewport"):
                fx._write(ob, path_name, 0, [first - 1, first, last], [1.0, 0.0, 1.0], "CONSTANT")
            burst.particles[-1].update(first=first, last=last)
    burst.frame_end = max([burst.frame] + [q["last"] - 1 for q in burst.particles])
    _lit_from_behind(burst.objects)
    return burst


_cloud = poof                           # (Animal.die has a parameter called poof)


def love(animal, frame, camera=None, frame_end=None, seed=0, glow=None, village=None):
    """The hearts of an animal that was just fed its food (Animal.setInLove): 7 heart particles ON `frame` (entity
    event 18), then one more every 10 ticks while it is in love: until frame_end (default: 3 s; the game: 600
    ticks = 30 s). They start within +-width of it, 0.5 above a random height of its hit box, and rise.
    Returns the list of engine.fx Bursts (also kept in animal.bursts). The player's hand: steve.swing_arm(frame - 2)."""
    from . import fx

    f0 = int(round(frame))
    f1 = f0 + 72 if frame_end is None else int(frame_end)
    out = []

    def hearts(f, count, salt):
        """`count` heart particles around the animal on frame f."""
        at = animal.pos_at(f) - Vector((0.0, 0.0, 1.0 - LOVE_LIFT))     # fx.emit lifts by 1.0, an animal's hearts by 0.5
        out.append(fx.emit("heart", at, f, camera=camera, count=count, seed=seed * 131 + salt, glow=glow,
                           size=animal.size, village=village))
        _lit_from_behind(out[-1].objects)

    hearts(f0, LOVE_HEARTS, 0)
    k = 1
    while f0 + k * LOVE_EVERY * TICK < f1:
        hearts(int(round(f0 + k * LOVE_EVERY * TICK)), 1, k)
        k += 1
    animal.bursts.extend(out)
    return out


# ----------------------------------------------------------------------------------------------------
# helpers for the farm: eggs, milk, following food, a pen and the life in it
# ----------------------------------------------------------------------------------------------------
def lay_egg(chicken, frame, seed=0, until=None, stage=None, name=None):
    """A hen lays an egg on `frame` (Chicken.aiStep: every 6000-11999 ticks; item 'egg'): an item entity appears
    at her feet with the game's toss (hops 0.38, lands after 9 ticks, lies still 0.3-0.9 block away, at most 1.3,
    after 15), then bobs and spins until `until` (default: 20 s). stage = a films.lookdev.Stage to register it with (then st.use(shot, egg)).
    Returns the engine.mobs DroppedItem (.sprite is the focus / hero target, .rest_pos where it lies)."""
    f0 = int(round(frame))
    egg = mobs.make_dropped_item(EGG_ITEM, seed=seed, name=name or ("%s_egg_%d" % (chicken.name, f0)))
    egg.drop(f0, chicken.pos_at(f0), seed=seed)
    egg.animate(f0, f0 + 480 if until is None else until)
    if stage is not None:
        stage.cast[egg.name] = egg
    return egg


LOOT = {"cow": (("beef", 2), ("leather", 1)), "chicken": (("chicken", 1), ("feather", 1)), "calf": (), "chick": ()}


def drop_loot(animal, frame, items=None, seed=0, until=None, stage=None):
    """What a killed animal leaves, as item entities tossed up from where it stands ON the frame of the killing
    blow (LivingEntity.die drops the loot at once, while the body still tips over). items = [(item id, count), ...];
    default: the loot tables' typical roll: cow ('beef', 2) and ('leather', 1) (the game: 1-3 beef, 0-2 leather),
    chicken ('chicken', 1) and ('feather', 1) (1 raw chicken, 0-2 feathers), babies nothing. An animal that burns
    drops 'cooked_beef' / 'cooked_chicken'. They bob and spin until `until` (default 20 s). stage = a Stage to
    register them with. Returns the list of engine.mobs DroppedItems."""
    f0 = int(round(frame))
    out = []
    for i, (item_id, count) in enumerate(LOOT[animal.kind] if items is None else items):
        it = mobs.make_dropped_item(item_id, count=count, seed=seed * 17 + i, name="%s_%s_%d" % (animal.name, item_id, f0))
        it.drop(f0, animal.pos_at(f0), seed=seed * 17 + i)
        it.animate(f0, f0 + 480 if until is None else until)
        if stage is not None:
            stage.cast[it.name] = it
        out.append(it)
    return out


def hand_item(player, item, frame_start, frame_end=None, collection=None):
    """An item in the player's right hand for the frames [frame_start, frame_end): 'wheat', 'wheat_seeds', 'bucket'
    ... (an item id) or an object from engine.props.make_item. It sits exactly where Character.hold puts an item
    and the arm is carried in the game's item pose for those frames, but it is NOT player.held: its visibility is
    its own, so one Steve can hold wheat in one shot and nothing in the next (Character.hold cannot be keyed).
    Call it AFTER the player's place() for that shot, and place() him again only at or after frame_end.
    Returns the item object: a focus / hero target, and follow(..., look=<it>)."""
    from . import fx, props

    if getattr(player, "arm_r", None) is None:
        raise ValueError("hand_item() needs the player (a Character with arms)")
    f0 = int(round(frame_start))
    col = collection if collection is not None else fx._collection()
    ob = props.make_item(item, col) if isinstance(item, str) else item
    ob.parent = player.arm_r
    ob.matrix_parent_inverse = Matrix.Identity(4)
    ob.matrix_basis = ch._held_matrix("hand", player.model_scale)
    keys = [(min(f0, 1) - 1, 1.0), (f0, 0.0)] + ([(int(round(frame_end)), 1.0)] if frame_end is not None else [])
    for path in ("hide_render", "hide_viewport"):
        fx._write(ob, path, 0, [k[0] for k in keys], [k[1] for k in keys], "CONSTANT")
    ob.hide_render = ob.hide_viewport = True
    ch._cut(player.arm_r, _ROT, 0, f0, ch.ITEM_ARM_PITCH)               # ArmPose.ITEM: 18 degrees forward
    if frame_end is not None:
        rest = player._rest(player.arm_r, _ROT, 0)
        if abs(ch._val(player.arm_r, _ROT, 0, int(round(frame_end))) - ch.ITEM_ARM_PITCH) < 1e-6:
            ch._cut(player.arm_r, _ROT, 0, int(round(frame_end)), rest)
    return ob


def milk(player, frame, frame_start, frame_end=None, collection=None):
    """The milking beat: the player holds an empty 'bucket' from frame_start, uses it on the cow on `frame` (his
    arm swings, furthest forward on `frame`) and from that frame on it is a 'milk_bucket' (AbstractCow.mobInteract:
    adult cows only, no particles), until frame_end. Two hand_item()s and Character.swing_arm: call it AFTER the
    player's place() and look_at() for that shot. Returns (bucket, milk_bucket)."""
    f = int(round(frame))
    bucket = hand_item(player, BUCKET_ITEM, frame_start, f, collection)
    full = hand_item(player, MILK_ITEM, f, frame_end, collection)
    ch._cut(player.arm_r, _ROT, 0, int(round(frame_start)), ch.ITEM_ARM_PITCH)
    player.swing_arm(f - 2)
    return bucket, full


def follow(animal, leader, frame_start, frame_end, stop=TEMPT_STOP, speed=None, look="eyes", gait="planted",
           swing=None, bob=None):
    """The animal follows a player who holds its food (TemptGoal): whenever `leader` (a Character) is further than
    `stop` (2.5 blocks) it walks toward him, never faster than its tempted speed (cow 2.75 blocks/s, chicken
    2.75) and no faster than he walks away, and it keeps looking at him. look = "eyes": at his eyes, which is
    what the game does; "item": at the item in his hand (leader.held); or any point / Object. Key the leader's
    walk first. After frame_end the leader counts as standing where he is then; returns the frame the animal has
    come to rest (>= frame_end)."""
    f0, f1 = int(round(frame_start)), int(round(frame_end))
    vmax = (animal.tempt_speed if speed is None else float(speed)) / FPS
    gain = 1.0 - math.exp(-1.0 / SPEED_TAU)
    turn = 1.0 - 0.7 ** (1.0 / TICK)                                     # LivingEntity.tickHeadTurn: 0.3 of the gap a tick
    p = animal.pos_at(f0)
    yaw = animal.yaw_at(f0)
    v = 0.0
    frames, spots, yaws = [float(f0)], [p.copy()], [yaw]
    f = f0
    while True:
        f += 1
        lead = leader.pos_at(min(f, f1))
        d = Vector((lead.x - p.x, lead.y - p.y))
        gap = d.length
        want = min(max(gap - stop, 0.0), vmax)
        v += (want - v) * gain
        if v < 2e-4:
            v = 0.0
        if v > 0.0 and gap > 1e-6:
            p = Vector((p.x + d.x / gap * v, p.y + d.y / gap * v, p.z))
            yaw += ch._wrap(math.atan2(d.x, -d.y) - yaw) * turn
        frames.append(float(f))
        spots.append(p.copy())
        yaws.append(yaw)
        if f >= f1 and v == 0.0:
            break
        if f > f1 + 72:
            break
    animal._travel(frames, spots, yaws, gait=gait, swing=swing, bob=bob)
    end = int(frames[-1])
    if look is not None:
        target = leader if look == "eyes" else (leader.held if look == "item" else look)
        if target is None:
            raise ValueError("follow(look='item'): %s holds nothing (leader.hold(props.make_item('wheat')))" % leader.name)
        animal.track(f0, end, target)
    return end


def pen_area(x0, y0, x1, y1):
    """The free rectangle (x0, y0, x1, y1) inside a ring of fence blocks on the cells x0..x1, y0..y1: the rails
    are 4 px thick in the middle of their cells, so the inside starts 0.625 into the first cell."""
    xa, xb, ya, yb = min(x0, x1), max(x0, x1), min(y0, y1), max(y0, y1)
    return (xa + 0.625, ya + 0.625, xb + 0.375, yb + 0.375)


def make_pen(scene, x0, y0, x1, y1, z=0, gates=(), fence="oak_fence", ground=None, name="pen", open_gates=False):
    """A fenced pen of the game's own fence blocks: posts and rails on the ring of cells x0..x1, y0..y1 at height
    z (they stand ON the blocks at z - 1), with a fence gate in every cell of `gates` [(x, y), ...] (closed unless
    open_gates). ground = a block id ('grass_block') to lay a floor at z - 1 under it and one block around (leave
    None on the village's own ground). Built as its own little World into the collection `name`; the village is
    not touched. Returns dict(world, objects, area = pen_area(...), cells = the ring, gates)."""
    from .blocks import World, new_collection

    xa, xb, ya, yb = min(x0, x1), max(x0, x1), min(y0, y1), max(y0, y1)
    w = World()
    gate_id = fence.replace("_fence", "_fence_gate")
    gates = [tuple(g) for g in gates]
    ring = [(x, y) for x in range(xa, xb + 1) for y in range(ya, yb + 1) if x in (xa, xb) or y in (ya, yb)]
    for x, y in ring:
        if (x, y) in gates:
            facing = "south" if y == ya else ("north" if y == yb else ("west" if x == xa else "east"))
            w.set(x, y, z, gate_id, {"facing": facing, "open": "true" if open_gates else "false", "in_wall": "false",
                                     "powered": "false"})
        else:
            w.set(x, y, z, fence)
    if ground:
        w.fill(xa - 1, ya - 1, z - 1, xb + 1, yb + 1, z - 1, ground)
        w.cull_below = z - 1
    objs = w.build(new_collection(scene, name), name=name)
    return dict(world=w, objects=objs, area=pen_area(xa, ya, xb, yb), cells=ring, gates=gates)


def _gap(a, pa, ya, b, pb, yb):
    """Smallest distance between the bodies of two animals standing at (pa, yaw ya) and (pb, yaw yb)."""
    return min(math.hypot(xa - xb, ya_ - yb_) - ra - rb
               for xa, ya_, ra in a.body_points(pa, ya) for xb, yb_, rb in b.body_points(pb, yb))


def _inside(animal, pos, yaw, area, margin):
    """True when the body of an animal standing at `pos` keeps `margin` from every side of the rectangle `area`."""
    x0, y0, x1, y1 = area
    return all(x0 + r + margin <= x <= x1 - r - margin and y0 + r + margin <= y <= y1 - r - margin
               for x, y, r in animal.body_points(pos, yaw))


def wander(animals, frame_start, frame_end, area, seed=0, place=True, speed=None, gait="planted", clearance=None,
           activity=1.0, watch=None, z=0.0):
    """Background life for a pen: every animal alternates standing, looking around and short straight walks inside
    the rectangle area = (x0, y0, x1, y1) from frame_start to frame_end, each with its own timing.

    place=True (default) first puts them on random free spots at frame_start (hard cut; z = the ground there);
    place=False starts from where they stand. Nobody leaves the rectangle and no body comes closer than
    `clearance` (default: its own body width; cow 0.75, chicken 0.5) to another body or to the edge, also while
    both move: every walk is checked against what the others do at the same time before it is keyed. Walks are
    1.2-3.2 blocks for a cow, 0.8-2.6 for a chicken, at the game's strolling speed (speed= overrides, blocks/s),
    after a turn on the spot. activity scales how restless they are (1 = a walk every 3-4 s each); watch = a
    Character they look at now and then while he is within 6 blocks. For a fenced pen pass pen_area(...) of the
    fence ring (or the 'area' make_pen returns). Returns {name: [(kind, first frame, last frame, target), ...]}
    with kind 'stand' | 'walk'. Deterministic for a seed."""
    f0, f1 = int(round(frame_start)), int(round(frame_end))
    animals = list(animals)
    area = (min(area[0], area[2]), min(area[1], area[3]), max(area[0], area[2]), max(area[1], area[3]))
    room = {a.name: (a.width if clearance is None else float(clearance)) for a in animals}
    rngs = {a.name: pix.rng(9173 * (int(seed) + 1) + 31 * i + 7) for i, a in enumerate(animals)}
    samples = {}                           # name -> {frame: (x, y, yaw)} of what is keyed; later frames: the last one
    ends = {}
    events = {a.name: [] for a in animals}

    def pose(a, f):
        """(x, y, yaw) of an animal on frame f as keyed so far (after its last key: where it stopped)."""
        rec = samples[a.name]
        return rec.get(int(f)) or rec[ends[a.name]]

    def record(a, fa, fb):
        """Remember where the keys put an animal on the frames fa..fb."""
        rec = samples.setdefault(a.name, {})
        for f in range(int(fa), int(fb) + 1):
            p = a.pos_at(f)
            rec[f] = (p.x, p.y, a.yaw_at(f))
        ends[a.name] = int(fb)

    def clear(a, f, pos, yaw):
        """Is the body at (pos, yaw) on frame f inside the area and clear of everybody else there then?"""
        if not _inside(a, pos, yaw, area, room[a.name]):
            return False
        for b in animals:
            if b is a or b.name not in samples:
                continue
            x, y, byaw = pose(b, f)
            if _gap(a, pos, yaw, b, (x, y), byaw) < max(room[a.name], room[b.name]):
                return False
        return True

    # ---- where they start
    if place:
        placer = pix.rng(4057 * (int(seed) + 1) + 3)
        for a in animals:
            found = []                                                   # of a few free spots, the one with most room
            for attempt in range(4000):
                pos = (float(placer.uniform(area[0], area[2])), float(placer.uniform(area[1], area[3])))
                yaw = float(placer.uniform(-math.pi, math.pi))
                if clear(a, f0, pos, yaw):
                    others = [pose(b, f0) for b in animals if b is not a and b.name in samples]
                    found.append((min([math.hypot(pos[0] - o[0], pos[1] - o[1]) for o in others] or [0.0]), pos, yaw))
                    if len(found) >= 6:
                        break
            if not found:
                raise ValueError("wander: no room for %s in %s (%d animals): a bigger area or a smaller clearance"
                                 % (a.name, tuple(round(c, 2) for c in area), len(animals)))
            _room, pos, yaw = max(found, key=lambda c: c[0])
            a.place(f0, (pos[0], pos[1], z), yaw)
            record(a, f0, f0)
    else:
        for a in animals:
            record(a, f0, f0)

    # ---- what they do, in the order of the frames at which each is free again
    queue = [(f0, i) for i in range(len(animals))]
    heapq.heapify(queue)
    while queue:
        t, i = heapq.heappop(queue)
        a = animals[i]
        r = rngs[a.name]
        if t >= f1 - 6:
            continue
        first = not events[a.name]
        here = a.pos_at(t)
        x, y, yaw = here.x, here.y, a.yaw_at(t)
        go = None
        if not first and r.random() < ch._clamp(0.8 * activity, 0.0, 1.0):
            lo, hi = a.info["stroll"]
            v = a.walk_speed if speed is None else float(speed)
            for _try in range(60):                                       # ahead first, then anywhere, then shorter
                length = float(r.uniform(lo, hi)) * (1.0 if _try < 40 else 0.6)
                heading = yaw + float(r.uniform(-1.0, 1.0)) * (math.pi if _try >= 15 else 1.6)
                target = (x + math.sin(heading) * length, y - math.cos(heading) * length)
                turn_frames = 0 if abs(ch._wrap(heading - yaw)) < 0.03 else max(4, int(round(TURN_FRAMES * min(1.0, abs(ch._wrap(heading - yaw)) / 0.8))))
                walk_frames = int(math.ceil(length / v * FPS + BRAKE_TAUS * SPEED_TAU))
                ok = True
                for k in range(0, turn_frames + walk_frames + 1, 2):
                    if k <= turn_frames:
                        u = _smooth(k / float(turn_frames)) if turn_frames else 1.0
                        here, hyaw = (x, y), yaw + ch._wrap(heading - yaw) * u
                    else:
                        u = min(1.0, (k - turn_frames) * v / FPS / length)
                        here, hyaw = (x + (target[0] - x) * u, y + (target[1] - y) * u), heading
                    if not clear(a, t + k, here, hyaw):
                        ok = False
                        break
                if ok:
                    go = target
                    break
        if go is not None:
            end = a.walk(t, [(x, y, z), (go[0], go[1], z)], speed=speed, gait=gait)
            record(a, t, end)
            events[a.name].append(("walk", t, end, (round(go[0], 3), round(go[1], 3))))
            pause = int(r.integers(8, 40))
            if end + pause < f1 - 14 and pause >= 14:
                a.idle(end, end + pause, seed=int(r.integers(0, 1 << 30)), watch=watch)
            heapq.heappush(queue, (end + pause, i))
        else:
            dur = int(r.integers(6, 50) if first else r.integers(24, 80) / max(activity, 0.05))
            end = min(t + dur, f1)
            if end - t >= 14:
                a.idle(t, end, seed=int(r.integers(0, 1 << 30)), watch=watch)
            record(a, t, end)
            events[a.name].append(("stand", t, end, None))
            heapq.heappush(queue, (end, i))
    return events


def pen_report(animals, frame_start, frame_end, area, step=1):
    """Measure a pen after it was keyed: (smallest gap between two bodies, smallest distance of a body from the
    edge of `area`) over the frames, in blocks (negative = overlap / outside). For tests and for directors."""
    gap, edge = 1e9, 1e9
    x0, y0, x1, y1 = (min(area[0], area[2]), min(area[1], area[3]), max(area[0], area[2]), max(area[1], area[3]))
    for f in range(int(frame_start), int(frame_end) + 1, int(step)):
        poses = [(a, a.pos_at(f), a.yaw_at(f)) for a in animals if not a.gone_at(f)]
        for i, (a, pa, ya) in enumerate(poses):
            for x, y, r in a.body_points(pa, ya):
                edge = min(edge, x - r - x0, x1 - x - r, y - r - y0, y1 - y - r)
            for b, pb, yb in poses[i + 1:]:
                gap = min(gap, _gap(a, pa, ya, b, pb, yb))
    return gap, edge


# ----------------------------------------------------------------------------------------------------
# self-test
# ----------------------------------------------------------------------------------------------------
def _evaluate(scene, frame):
    whole = int(math.floor(frame))
    scene.frame_set(whole, subframe=float(frame) - whole)
    bpy.context.view_layer.update()


def _bounds(animal):
    lo, hi = Vector((1e9,) * 3), Vector((-1e9,) * 3)
    for ob in animal.mesh_parts():
        for v in ob.data.vertices:
            p = ob.matrix_world @ v.co
            lo = Vector(map(min, lo, p))
            hi = Vector(map(max, hi, p))
    return lo, hi


def _sole_stray(scene, animal, step=0.25):
    """How far a sole that is on the ground strays from where its step put it, over the last walk / turn / follow
    (world space, on the evaluated rig): the largest distance, in blocks."""
    worst = 0.0
    for ta, tb, legs in animal.last_walk["stance"]:
        start = {}
        for t in np.arange(ta, tb + 1e-6, step):
            _evaluate(scene, float(t))
            for leg in legs:
                p = (animal.legs[leg].matrix_world @ Vector((0.0, 0.0, -animal.leg_len))).copy()
                if leg not in start:
                    start[leg] = p
                worst = max(worst, (p.xy - start[leg].xy).length)
    return worst


def _sole_lift(scene, animal, ground=0.0, step=0.25):
    """Largest height of a stance sole above / below the ground over the last planted walk."""
    worst = 0.0
    for ta, tb, legs in animal.last_walk["stance"]:
        for t in np.arange(ta, tb + 1e-6, step):
            _evaluate(scene, float(t))
            for leg in legs:
                p = animal.legs[leg].matrix_world @ Vector((0.0, 0.0, -animal.leg_len))
                worst = max(worst, abs(p.z - ground))
    return worst


def _check():
    """Numbers only: sizes, speeds, the two gaits, head limits, wings, hurt, death, the pen."""
    from . import quick

    scene = quick.reset()
    ok = []

    def expect(label, cond, detail=""):
        ok.append(bool(cond))
        print("%s %s%s" % ("ok  " if cond else "FAIL", label, (": " + detail) if detail else ""))

    cow, calf = make_cow("cow"), make_cow("calf", baby=True)
    hen, chick = make_chicken("hen"), make_chicken("chick", baby=True)
    for a, x in ((cow, 0.0), (calf, 2.0), (hen, 4.0), (chick, 6.0)):
        a.place(1, (x, 0.0, 0.0), 0.0)
    _evaluate(scene, 1)

    # ---- sizes, straight from the vertices (pixels)
    want = {"cow": ((-6, 6), (-15, 10), (0, 25)), "calf": ((-4, 4), (-11, 6), (0, 16)),
            "hen": ((-4, 4), (-8, 4), (0, 15)), "chick": ((-3, 3), (-3, 2), (0, 6))}
    for a, x in ((cow, 0.0), (calf, 2.0), (hen, 4.0), (chick, 6.0)):
        lo, hi = _bounds(a)
        eps = GROUND_EPS if a.species == "chicken" else 0.0
        got = ((round((lo.x - x) * 16, 2), round((hi.x - x) * 16, 2)), (round(lo.y * 16, 2), round(hi.y * 16, 2)),
               (round((lo.z - eps) * 16, 2), round((hi.z - eps) * 16, 2)))
        faces = sum(len(o.data.polygons) for o in a.mesh_parts())
        expect("%s bounds px x %s y %s z %s (%d faces)" % (a.name, got[0], got[1], got[2], faces),
               all(abs(g - w) < 0.02 for gs, ws in zip(got, want[a.name]) for g, w in zip(gs, ws)), "want %s" % (want[a.name],))
    expect("speeds cow %.3f / %.3f / %.3f, chicken %.3f / %.3f, chick after hen %.3f" % (
        COW_WALK, COW_TEMPT, COW_PANIC, CHICKEN_WALK, CHICKEN_PANIC, CHICK_FOLLOW),
        abs(COW_WALK - 1.7621) < 1e-3 and abs(COW_TEMPT - 2.7533) < 1e-3 and abs(COW_PANIC - 7.0485) < 1e-3
        and abs(CHICKEN_WALK - 2.7533) < 1e-3 and abs(CHICKEN_PANIC - 5.3965) < 1e-3)

    # ---- planted gait: soles stay where they are put, on the ground; the walk ends neutral and on its target
    for a, y in ((cow, 4.0), (calf, 6.0), (hen, 8.0), (chick, 10.0)):
        a.place(10, (0.0, y, 0.0), math.radians(90))
        end = a.walk(10, [(0.0, y, 0.0), (6.0, y, 0.0)])
        info = dict(a.last_walk)
        stray = _sole_stray(scene, a)
        lift = _sole_lift(scene, a, ground=GROUND_EPS if a.species == "chicken" else 0.0)
        _evaluate(scene, end)
        at = a.root.matrix_world.translation
        legs0 = max(abs(ob.rotation_euler.x) for ob in a.legs.values())
        may = (1.0 - info["bob"]) * a.leg_len * (1.0 - math.cos(info["swing"])) + 0.004
        expect("%s planted walk: 6 blocks in %d frames (%.2f blocks/s cruise), %d steps of +-%.1f deg, cycle %.1f frames; "
               "sole strays %.4f over the ground, lifts %.4f (bob %.2f: body sinks %.3f)" % (
                   a.name, end - 10, info["speed"], info["steps"], math.degrees(info["swing"]), info["cycle_frames"],
                   stray, lift, info["bob"], info["bob"] * info["sink"]),
               stray < 0.012 and lift < may and abs(at.x - 6.0) < 1e-4 and legs0 < 1e-6
               and abs(a.hips.location.z - a._rest(a.hips, _LOC, 2)) < 1e-6)
        mid = 10 + (end - 10) // 2
        v = (a.pos_at(mid + 1) - a.pos_at(mid)).length * FPS
        expect("%s cruises at %.3f blocks/s" % (a.name, v), abs(v - a.walk_speed) < 0.01)

    # ---- vanilla gait: the game's wave along the distance covered
    for a, y in ((cow, 14.0), (hen, 16.0), (calf, 18.0)):
        a.place(300, (0.0, y, 0.0), math.radians(90))
        a._walk_pos = 0.0
        end = a.walk(300, [(0.0, y, 0.0), (20.0, y, 0.0)], gait="vanilla")
        per_tick = a.walk_speed / 20.0
        amp = LEG_SWING * min(ANIM_PER_BLOCK * per_tick, 1.0)
        f_a, f_b = 300 + 30, end - 20
        vals = [ch._val(a.legs[a.gait_groups[0][0]], _ROT, 0, f) for f in np.arange(f_a, f_b, 0.25)]
        opp = [ch._val(a.legs[a.gait_groups[1][0]], _ROT, 0, f) for f in np.arange(f_a, f_b, 0.25)]
        ups = [i for i in range(1, len(vals)) if vals[i - 1] < 0.0 <= vals[i]]
        period = (ups[-1] - ups[0]) / (len(ups) - 1) * 0.25 if len(ups) > 1 else 0.0
        want_period = VANILLA_CYCLE / (BABY_ANIM_SCALE if a.baby else 1.0) / a.walk_speed * FPS
        expect("%s vanilla gait: swing +-%.1f deg (game %.1f), cycle %.1f frames (game %.1f), pairs opposed" % (
            a.name, math.degrees(max(vals)), math.degrees(amp), period, want_period),
            abs(max(vals) - amp) < 0.02 and abs(period - want_period) < 0.6
            and max(abs(p + q) for p, q in zip(vals, opp)) < 1e-6)
        _evaluate(scene, end + 30)
        expect("%s vanilla walk settles" % a.name, max(abs(ob.rotation_euler.x) for ob in a.legs.values()) < 1e-6)

    # ---- a corner, a turn on the spot
    cow.place(600, (0.0, 30.0, 0.0), 0.0)
    end = cow.walk(600, [(0.0, 30.0, 0.0), (0.0, 26.0, 0.0), (5.0, 26.0, 0.0)])
    stray = _sole_stray(scene, cow)
    _evaluate(scene, end)
    expect("cow round a corner: arcs %s, sole strays %.4f, ends facing east" % (cow.last_walk["corners"], stray),
           stray < 0.03 and abs(cow.root.rotation_euler.z - math.radians(90)) < 1e-5
           and (cow.root.location - Vector((5.0, 26.0, 0.0))).length < 1e-4)
    end2 = cow.turn(end + 10, math.radians(-90))
    stray = _sole_stray(scene, cow)
    expect("cow turns 180 degrees on the spot in %d frames with %d steps: sole strays %.4f" % (
        end2 - end - 10, cow.last_walk["steps"], stray), stray < 0.03 and cow.last_walk["steps"] >= 2)

    # ---- head limits and the chick's look
    cow.place(700, (0.0, 40.0, 0.0), 0.0)
    cow.look_at(700, (-30.0, 41.0, 60.0), ease=0)
    _evaluate(scene, 700)
    expect("cow head clamps at 75 / 40 degrees", abs(abs(cow.head.rotation_euler.z) - HEAD_YAW_MAX) < 1e-5
           and abs(abs(cow.head.rotation_euler.x) - HEAD_PITCH_MAX) < 1e-5)
    chick.place(700, (3.0, 40.0, 0.0), 0.0)
    e = chick.look_at(700, (9.0, 40.0, 0.2), ease=8)
    _evaluate(scene, e)
    expect("a chick looks with its whole body", abs(ch._wrap(chick.root.rotation_euler.z - math.radians(90))) < 1e-4)
    cow.look_at(705, None, ease=0)
    cow.idle(710, 900, seed=3)
    yk = [k for k in ch.read_keys(cow.head, _ROT, 2) if k[0] >= 710]
    rates = [abs(b[1] - a[1]) / (b[0] - a[0]) for a, b in zip(yk, yk[1:]) if b[0] > a[0] and abs(b[1] - a[1]) > 1e-6]
    expect("cow idle: %d head keys, turning at %.1f deg/tick at most, within 75 degrees" % (
        len(yk), math.degrees(max(rates)) * TICK if rates else 0.0),
        rates and max(rates) <= HEAD_SPEED * 1.01 and max(abs(k[1]) for k in yk) <= HEAD_YAW_MAX + 1e-6
        and yk[-1][2] == "CONSTANT")

    # ---- wings
    hen.place(1000, (0.0, 50.0, 1.0), 0.0)
    land = hen.fall(1000, (0.0, 50.0, 0.0))
    big = 0.0
    for f in np.arange(1000.0, land, 0.2):
        big = max(big, ch._val(hen.wing_r, _ROT, 1, f))
        assert abs(ch._val(hen.wing_r, _ROT, 1, f) + ch._val(hen.wing_l, _ROT, 1, f)) < 1e-9, "the wings mirror each other"
    v_term = (hen.pos_at(land - 3).z - hen.pos_at(land - 2).z) * FPS
    _evaluate(scene, land + 8)
    expect("hen falls 1 block in %d frames at %.2f blocks/s, wings to %.0f deg, folded after landing" % (
        land - 1000, v_term, math.degrees(big)),
        1.9 < big <= 2.0 + 1e-6 and 2.0 < v_term < 2.4 and abs(hen.wing_r.rotation_euler.y) < 1e-6
        and abs(hen.root.location.z) < 1e-6)
    cow.place(1000, (5.0, 50.0, 0.0), 0.0)
    land_c = cow.hop(1000, (5.0, 49.0, 1.0))
    apex = max(cow.pos_at(f).z for f in np.arange(1000.0, land_c + 1, 0.2))
    expect("cow hops up a block: apex %.3f, lands after %d frames at z = %.2f" % (apex, land_c - 1000, cow.pos_at(land_c).z),
           abs(apex - 1.2492) < 0.01 and abs(cow.pos_at(land_c).z - 1.0) < 1e-6)

    # ---- hurt
    track = knockback_track()
    apex = max(u for _b, u in track)
    air = max(k for k, (_b, u) in enumerate(track) if u > 0.0) + 1
    expect("knock-back: %.3f up, %.3f back, on the ground after %d ticks, still after %d" % (
        apex, track[-1][0], air, len(track) - 1), abs(apex - 0.9648) < 2e-3 and air == 10 and 1.8 < track[-1][0] < 2.1)
    ctrack = knockback_track(fall=CHICKEN_FALL)
    cair = max(k for k, (_b, u) in enumerate(ctrack) if u > 0.0) + 1
    expect("... a chicken: %.3f back, on the ground after %d ticks" % (ctrack[-1][0], cair), cair > air)
    cow.place(1200, (0.0, 60.0, 0.0), 0.0)
    cow.walk(1200, [(0.0, 60.0, 0.0), (0.0, 50.0, 0.0)])
    steve_pos = (0.0, 54.0, 0.0)
    e = cow.hurt(1230, attacker=steve_pos)
    shown = {}
    for f in (1229, 1230, 1235, 1241, 1242, 1260):
        _evaluate(scene, f)
        shown[f] = (not cow.body.hide_render, not cow._twins["body"].hide_render)
    expect("cow hurt at 1230: red twin on frames 1230-1241 only %s" % (shown,),
           shown[1229] == (True, False) and shown[1230] == (False, True) and shown[1241] == (False, True)
           and shown[1242] == (True, False))
    p0, p1 = cow.pos_at(1230), cow.pos_at(e + 12)
    top = max(cow.pos_at(f).z for f in np.arange(1230.0, e + 1, 0.2))
    flail = max(abs(ch._val(cow.leg_l, _ROT, 0, f)) for f in np.arange(1230.0, e, 0.2))
    expect("... thrown %.2f blocks away from the attacker (to +y), %.2f up, legs flail to %.0f deg, stands at frame %d" % (
        p1.y - p0.y, top, math.degrees(flail), e),
        1.8 < p1.y - p0.y < 2.1 and abs(p1.x - p0.x) < 1e-6 and abs(top - 0.9648) < 0.01 and flail > 1.2
        and e == 1242)
    _evaluate(scene, e + 40)
    expect("... and comes to rest with straight legs", max(abs(ob.rotation_euler.x) for ob in cow.legs.values()) < 1e-6
           and abs(cow.root.location.z) < 1e-6)
    twin = cow._twins["body"].data.materials[0]
    base = cow.body.data.materials[0]
    img_a = np.array(base.node_tree.nodes["Image Texture"].image.pixels[:]).reshape(-1, 4)
    img_b = np.array(twin.node_tree.nodes["Image Texture"].image.pixels[:]).reshape(-1, 4)
    want_rgb = img_a[:, :3] * OVERLAY_KEEP + np.array([1.0 - OVERLAY_KEEP, 0.0, 0.0])
    expect("hurt texture = 0.698 x texel + 0.302 x red", float(np.max(np.abs(img_b[:, :3] - want_rgb))) < 0.004)

    # ---- death
    expect("death angle: 0 at tick 1, %.1f at 5, 90 from tick 13.5" % death_angle(5.0),
           death_angle(1.0) == 0.0 and abs(death_angle(5.0) - 90 * math.sqrt(0.32)) < 1e-9
           and abs(death_angle(13.5) - 90.0) < 1e-9 and death_angle(13.4) < 90.0)
    cam = quick.camera(scene, (6.0, 60.0, 2.0), (0.0, 64.0, 0.5))
    hen.place(1400, (4.0, 64.0, 0.0), 0.0)
    gone = hen.die(1400, camera=cam, attacker=(4.0, 62.0, 0.0), seed=4)
    burst = hen.bursts[-1]
    states = {}
    for f in (1399, 1400, 1412, 1423, 1424, 1430):
        _evaluate(scene, f)
        states[f] = (not hen.body.hide_render, not hen._twins["body"].hide_render,
                     round(math.degrees(hen.root.rotation_euler.y), 1))
    expect("hen dies at 1400: red and tipping, gone on %d %s" % (gone, states),
           gone == 1424 and states[1399][:2] == (True, False) and states[1400][:2] == (False, True)
           and states[1423][:2] == (False, True) and states[1424][:2] == (False, False) and states[1423][2] == 90.0
           and abs(states[1412][2] - death_angle(10.0)) < 0.2)
    ids = {q["object"].name.rsplit("_", 1)[0] for q in burst.particles}
    _evaluate(scene, gone)
    live = [q for q in burst.particles if q["first"] <= gone < q["last"]]
    zs = [q["object"].matrix_world.translation.z for q in live]
    sizes = [q["size"] * 2 for q in live]
    _evaluate(scene, gone + 30)
    later = [q for q in burst.particles if q["first"] <= gone + 30 < q["last"]]
    rise = [q["object"].matrix_world.translation.z for q in later]
    expect("poof: %d particles (%d stage quads), %d on the first frame all showing generic_7, 0.2-1.4 wide (%.2f-%.2f), "
           "start height %.2f-%.2f, still %d after 30 frames, risen to %.2f-%.2f; last gone after frame %d" % (
               len(ids), len(burst.particles), len(live), min(sizes), max(sizes), min(zs), max(zs), len(later),
               min(rise) if rise else 0.0, max(rise) if rise else 0.0, burst.frame_end),
           len(ids) == POOF_COUNT and len(live) == POOF_COUNT
           and all("generic_7" in q["object"].data.name for q in live)
           and 0.2 <= min(sizes) and max(sizes) <= 1.4 and len(later) < len(live) and min(rise) > min(zs))
    hen.place(1500, (4.0, 64.0, 0.0), 0.0)
    _evaluate(scene, 1500)
    expect("place() after a death: upright and there again", not hen.body.hide_render and hen._twins["body"].hide_render
           and abs(hen.root.rotation_euler.y) < 1e-9)
    hen.show(1510, False)
    hen.show(1520, True)
    _evaluate(scene, 1515)
    hidden = hen.body.hide_render
    _evaluate(scene, 1520)
    expect("show() still works", hidden and not hen.body.hide_render)

    # ---- egg, hearts, milk
    hen.place(1600, (0.0, 70.0, 0.0), 0.0)
    egg = lay_egg(hen, 1610, seed=2)
    _evaluate(scene, 1609)
    before = egg.sprite.hide_render
    _evaluate(scene, 1640)
    expect("egg: hidden before frame 1610, lies %.2f from the hen at frame 1640" % (
        (egg.root.matrix_world.translation.xy - Vector((0.0, 70.0))).length),
        before and not egg.sprite.hide_render and (egg.root.matrix_world.translation.xy - Vector((0.0, 70.0))).length < 0.6)
    loot = drop_loot(hen, 1650, seed=1)
    _evaluate(scene, 1700)
    expect("loot of a chicken: %s, lying %s from her" % ([(it.item_id, len(it.copies)) for it in loot],
           [round((it.root.matrix_world.translation.xy - hen.pos_at(1650).xy).length, 2) for it in loot]),
           [it.item_id for it in loot] == ["chicken", "feather"] and all(not it.sprite.hide_render for it in loot)
           and not drop_loot(chick, 1650))
    bursts = love(cow, 1700, camera=cam, frame_end=1760, seed=1)
    expect("love: %d bursts, %d + %s hearts" % (len(bursts), len(bursts[0].objects), [len(b.objects) for b in bursts[1:]]),
           len(bursts[0].objects) == LOVE_HEARTS and all(len(b.objects) == 1 for b in bursts[1:]) and len(bursts) == 5)
    steve = ch.make_player("steve")
    steve.place(1800, (1.0, 80.0, 0.0), 0.0)
    b_empty, b_full = milk(steve, 1810, 1800, 1860)
    vis = {}
    for f in (1799, 1800, 1809, 1810, 1859, 1860):
        _evaluate(scene, f)
        vis[f] = (not b_empty.hide_render, not b_full.hide_render)
    expect("milk: bucket 1800-1809, milk bucket 1810-1859 %s" % (vis,),
           vis[1799] == (False, False) and vis[1800] == (True, False) and vis[1809] == (True, False)
           and vis[1810] == (False, True) and vis[1859] == (False, True) and vis[1860] == (False, False))

    # ---- follow
    cow.place(2000, (0.0, 90.0, 0.0), math.radians(180))
    steve.hold(None)
    steve.place(2000, (0.0, 93.0, 0.0), 0.0)
    walk_end = steve.walk(2010, [(0.0, 93.0, 0.0), (0.0, 101.0, 0.0)])
    end = follow(cow, steve, 2000, walk_end + 10)
    gaps = [(steve.pos_at(f) - cow.pos_at(f)).length for f in range(2000, end + 1)]
    vmax = max((cow.pos_at(f + 1) - cow.pos_at(f)).length * FPS for f in range(2000, end))
    stray = _sole_stray(scene, cow)
    _evaluate(scene, 2060)
    hy = cow.head.rotation_euler.x
    expect("follow: gap %.2f-%.2f blocks, ends %.2f behind at frame %d, top speed %.2f, sole strays %.4f, head up %.0f deg" % (
        min(gaps), max(gaps), gaps[-1], end, vmax, stray, -math.degrees(hy)),
        2.3 < gaps[-1] < 2.7 and max(gaps) < 3.6 and vmax <= COW_TEMPT + 0.02 and stray < 0.03 and hy < 0.0)

    # ---- a pen
    for kind, n, cells in (("cow", 5, (0, 0, 9, 8)), ("chicken", 6, (20, 0, 26, 6))):
        herd = [make_cow("pc%d" % i) if kind == "cow" else make_chicken("ph%d" % i) for i in range(n)]
        area = pen_area(*cells)
        events = wander(herd, 2500, 2740, area, seed=5)
        gap, edge = pen_report(herd, 2500, 2740 + 40, area)
        walks = sum(1 for ev in events.values() for e in ev if e[0] == "walk")
        expect("pen of %d %ss in %s for 10 s: %d walks, smallest gap between bodies %.2f, from the fence %.2f" % (
            n, kind, tuple(round(c, 2) for c in area), walks, gap, edge),
            walks >= n and gap >= herd[0].width - 0.02 and edge >= herd[0].width - 0.02)
        again = wander([make_cow("qc%d" % i) if kind == "cow" else make_chicken("qh%d" % i) for i in range(n)],
                       2500, 2740, area, seed=5)
        expect("... the same seed gives the same pen", [e[1:] for ev in events.values() for e in ev]
               == [e[1:] for ev in again.values() for e in ev])
    print("check:", "all %d passed" % len(ok) if all(ok) else "%d of %d FAILED" % (ok.count(False), len(ok)))
    return all(ok)


def _tile(name, paths, cols=2, pad=4):
    """The stills side by side in one picture, `cols` to a row -> out/test/<name>.png."""
    import os

    from PIL import Image

    from . import quick

    ims = [Image.open(q).convert("RGB") for q in paths]
    w, h = ims[0].size
    rows = (len(ims) + cols - 1) // cols
    out = Image.new("RGB", (cols * w + pad * (cols - 1), rows * h + pad * (rows - 1)), (20, 20, 24))
    for i, im in enumerate(ims):
        out.paste(im, ((i % cols) * (w + pad), (i // cols) * (h + pad)))
    path = os.path.join(quick.TEST_DIR, name + ".png")
    out.save(path)
    print("wrote", path)
    return path


VIEWS = (("front", 0.0), ("side", 90.0), ("back", 180.0), ("threequarter", -40.0))
_MAKERS = {"cow": lambda n: make_cow(n), "calf": lambda n: make_cow(n, baby=True),
           "chicken": lambda n: make_chicken(n), "chick": lambda n: make_chicken(n, baby=True)}


def _selftest(which):
    from . import quick

    def want(name):
        return name in which

    def stage(preset="day", res=(540, 960), blur=False, sun=-25.0, **kw):
        scene = quick.reset()
        quick.setup(scene, res=res)
        lamp = quick.light(scene, preset)
        lamp.rotation_euler[2] = math.radians(sun)
        if preset == "day":
            lamp.data.energy = 3.2
        if blur:                                                         # the films' shutter (look.setup_render)
            scene.render.use_motion_blur = True
            scene.render.motion_blur_shutter = 0.5
            scene.render.motion_blur_position = "START"
        stage.world = mobs._set(scene, **kw)
        return scene

    if want("lineup"):
        scene = stage(res=(960, 540), wall=((-5, 2, 5, 2), ("stone_bricks", "oak_planks", "stone_bricks")))
        steve, farmer = ch.make_player("steve"), ch.make_villager("farmer", "farmer")
        kid = ch.make_villager("kid", "none", child=True)
        cast = [(steve, -3.3), (farmer, -2.4), (make_cow("cow"), -0.9), (make_cow("calf", baby=True), 0.7),
                (make_chicken("hen"), 1.75), (make_chicken("chick", baby=True), 2.45), (kid, 3.15)]
        for c, x in cast:
            c.place(1, (x, 0.0, 0.0), math.radians(-55.0 if isinstance(c, Animal) else -20.0))
        scene.frame_set(1)
        quick.camera(scene, (0.0, -8.6, 1.25), (-0.05, 0.0, 0.95), lens=50)
        print("wrote", quick.render(scene, "animals_lineup"))

    for kind in ("cow", "calf", "chicken", "chick"):
        if not (want("views") or want("views_" + kind)):
            continue
        scene = stage(res=(432, 432))
        a = _MAKERS[kind]("a")
        tall = a.height
        stills = []
        for n, (label, yaw) in enumerate(VIEWS):
            a.place(n + 1, (0.0, 0.0, 0.0), math.radians(yaw))
            scene.frame_set(n + 1)
            d = max(tall, 0.5) * 3.7
            quick.camera(scene, (0.0, -d, tall * 0.62), (0.0, 0.0, tall * 0.45), lens=50)
            stills.append(quick.render(scene, "animals_%s_%s" % (kind, label)))
        _tile("animals_%s_views" % kind, stills)

    for kind, gait in (("cow", "planted"), ("chicken", "planted"), ("calf", "planted"), ("chick", "planted"),
                       ("cow", "vanilla"), ("chicken", "vanilla")):
        tag = "walk_%s%s" % (kind, "" if gait == "planted" else "_vanilla")
        if not (want(tag) or (want("walk") and gait == "planted" and kind in ("cow", "chicken"))):
            continue
        scene = stage(res=(480, 480), blur=True, sun=-150.0)
        a = _MAKERS[kind]("a")
        a.place(1, (-6.0, 0.0, 0.0), math.radians(90))
        end = a.walk(1, [(-6.0, 0.0, 0.0), (8.0, 0.0, 0.0)], gait=gait)
        info = a.last_walk
        cyc = info.get("cycle_frames") or info["cycle_blocks"] / a.walk_speed * FPS
        print(tag, "ends at frame", end, {k: (round(v, 3) if isinstance(v, float) else v) for k, v in info.items() if k != "stance"})
        stills = []
        for i in range(4):
            f = int(round(16 + i * max(cyc, 4.0) / 4.0)) if cyc >= 8 else 16 + i
            scene.frame_set(f)
            here = a.pos_at(f)
            d = max(a.height, 0.5) * 3.4
            quick.camera(scene, (here.x + 0.25 * d, -d, a.height * 0.55), (here.x, 0.0, a.height * 0.42), lens=50)
            stills.append(quick.render(scene, "animals_%s_%d" % (tag, i + 1)))
            print("   frame", f, "legs", {n: round(math.degrees(ob.rotation_euler.x), 1) for n, ob in a.legs.items()},
                  "hips", round(a.hips.location.z - a._rest(a.hips, _LOC, 2), 4))
        _tile("animals_%s_sheet" % tag, stills, cols=4)

    if want("flap"):
        # a hen steps off a two-block pillar and comes down with beating wings
        scene = stage(res=(432, 768), blur=True, sun=-150.0, wall=((0, 1, 0, 1), ("oak_planks", "oak_planks")))
        hen = make_chicken("hen")
        hen.place(1, (0.5, 1.5, 2.0), 0.0)
        hen.walk(1, [(0.5, 1.5, 2.0), (0.5, 0.95, 2.0)])
        f0 = 12
        land = hen.fall(f0, (0.5, -0.9, 0.0))
        cam = quick.camera(scene, (-3.3, -4.3, 1.25), (0.45, 0.2, 1.15), lens=50)
        print("hen leaves the pillar at frame", f0, "and lands at", land)
        stills = []
        for i, f in enumerate((f0 + 3, f0 + 8, f0 + 13, f0 + 18)):
            scene.frame_set(f)
            stills.append(quick.render(scene, "animals_flap_%d" % (i + 1)))
            print("   frame", f, "z %.2f" % hen.root.location.z, "wings %.0f / %.0f deg" % (
                math.degrees(hen.wing_r.rotation_euler.y), math.degrees(hen.wing_l.rotation_euler.y)))
        _tile("animals_flap_sheet", stills, cols=4)

    def beside(p, q, dist, height, aim=0.8, shift=0.0):
        """Camera position and target for two things at p and q seen from the side (the side nearer to -Y)."""
        p, q = Vector((p[0], p[1])), Vector((q[0], q[1]))
        mid, d = (p + q) / 2.0, (q - p).normalized()
        n = Vector((d.y, -d.x))
        if n.y > 0.0:
            n = -n
        mid = mid + d * shift
        return (mid.x + n.x * dist, mid.y + n.y * dist, height), (mid.x, mid.y, aim)

    if want("wheat"):
        from . import props

        for tag, look in (("", "item"), ("_eyes", "eyes")):
            scene = stage(res=(960, 540), sun=-140.0)
            steve = ch.make_player("steve")
            steve.hold(props.make_item("wheat"))
            cow, calf = make_cow("cow"), make_cow("calf", baby=True)
            steve.place(1, (1.6, -3.0, 0.0), math.radians(-100))
            cow.place(1, (-3.6, -2.4, 0.0), math.radians(100))
            calf.place(1, (-4.6, -1.2, 0.0), math.radians(110))
            steve.raise_arm(1, 40, ease=0)
            steve.look_at(1, cow, ease=0)
            end = follow(cow, steve, 1, 60, look=look)
            follow(calf, cow, 1, end, stop=1.7, look="eyes")
            scene.frame_set(end)
            gap = (steve.pos_at(end) - cow.pos_at(end)).length
            print("wheat%s: cow rests at frame %d, %.2f blocks from Steve, head yaw %.0f pitch %.0f deg; calf %.2f behind" % (
                tag, end, gap, math.degrees(cow.head.rotation_euler.z), -math.degrees(cow.head.rotation_euler.x),
                (calf.pos_at(end) - cow.pos_at(end)).length))
            pos, aim = beside(cow.pos_at(end), steve.pos_at(end), 6.6, 1.35, aim=0.95, shift=-0.35)
            cam = quick.camera(scene, pos, aim, lens=50)
            if look == "eyes":
                love(cow, end - 8, camera=cam, seed=3)
                scene.frame_set(end)
            print("wrote", quick.render(scene, "animals_wheat" + tag))

    if want("egg"):
        scene = stage(res=(960, 540), sun=-140.0, blur=True)
        hen, chick = make_chicken("hen"), make_chicken("chick", baby=True)
        hen.place(1, (0.0, 0.0, 0.0), math.radians(-65))
        egg = lay_egg(hen, 4, seed=7)
        rest = egg.rest_pos
        away = Vector((-rest.x, -rest.y, 0.0)).normalized()
        hen.walk(18, [(0.0, 0.0, 0.0), tuple(away * 0.55)], speed=1.2)
        chick.place(1, tuple(rest + Vector((away.y, -away.x, 0.0)) * 0.55 + away * 0.25), 0.0)
        chick.look_at(30, rest, ease=6)
        hen.look_at(36, rest + Vector((0.0, 0.0, 0.25)), ease=5)
        pos, aim = beside(hen.pos_at(48), rest, 3.1, 0.55, aim=0.4)
        egg.face(48, pos)
        egg.animate(4, 200)
        scene.frame_set(48)
        print("egg rests at", tuple(round(c, 2) for c in rest), "hen at", tuple(round(c, 2) for c in hen.pos_at(48)),
              "egg centre %.2f above the ground" % egg.sprite.matrix_world.translation.z)
        quick.camera(scene, pos, aim, lens=50)
        print("wrote", quick.render(scene, "animals_egg"))

    if want("hurt"):
        scene = stage(res=(432, 768), blur=True, sun=-140.0)
        steve, cow = ch.make_player("steve"), make_cow("cow")
        steve.place(1, (1.9, -0.2, 0.0), math.radians(-90))
        cow.place(1, (0.0, 0.0, 0.0), math.radians(20))
        steve.look_at(1, cow, ease=0)
        steve.swing_arm(8)
        end = cow.hurt(10, attacker=steve)
        quick.camera(scene, (-0.4, -7.6, 1.5), (-0.7, 0.0, 1.05), lens=42)
        stills = []
        for i, f in enumerate((9, 11, 15, 20, 26)):
            scene.frame_set(f)
            stills.append(quick.render(scene, "animals_hurt_%d" % (i + 1)))
            print("   frame", f, "cow at", tuple(round(c, 2) for c in cow.root.location), "red", not cow._twins["body"].hide_render,
                  "legs", [round(math.degrees(ob.rotation_euler.x)) for ob in cow.legs.values()])
        _tile("animals_hurt_sheet", stills, cols=5)
        print("cow stands again at frame", end)

    if want("die"):
        scene = stage(res=(432, 768), blur=True, sun=-140.0)
        steve, cow, hen = ch.make_player("steve"), make_cow("cow"), make_chicken("hen")
        steve.place(1, (1.9, -0.6, 0.0), math.radians(-90))
        cow.place(1, (0.0, 0.0, 0.0), math.radians(20))
        hen.place(1, (0.2, -1.5, 0.0), math.radians(-30))
        steve.look_at(1, cow, ease=0)
        cam = quick.camera(scene, (-0.6, -8.4, 1.7), (-0.8, 0.0, 1.0), lens=42)
        steve.swing_arm(8)
        gone = cow.die(10, camera=cam, attacker=steve, max_back=1.0, seed=2)
        hen.die(10, camera=cam, attacker=steve, max_back=1.0, seed=5)
        stills = []
        for i, f in enumerate((13, 18, 25, 33, gone, gone + 8, gone + 22)):
            scene.frame_set(f)
            stills.append(quick.render(scene, "animals_die_%d" % (i + 1)))
            live = [q for b in cow.bursts + hen.bursts for q in b.particles if q["first"] <= f < q["last"]]
            print("   frame", f, "cow tipped %.0f deg" % math.degrees(cow.root.rotation_euler.y), "red",
                  not cow._twins["body"].hide_render, "puffs", len(live))
        _tile("animals_die_sheet", stills[:4], cols=4)
        _tile("animals_poof_sheet", stills[4:], cols=3)

    if want("pen") or want("pen_cow") or want("pen_chicken"):
        _pen_test([k for k in ("cow", "chicken") if want("pen") or want("pen_" + k)])


PENS = {    # fence ring (cells), gate cell, camera, target, lens, wander seed: in the meadow north of the village
    "cow": dict(cells=(3, 27, 12, 36), gate=(7, 27), cam=(9.3, 22.7, 4.3), aim=(7.8, 31.2, 0.3), lens=24, seed=11),
    "chicken": dict(cells=(-12, 28, -5, 36), gate=(-9, 28), cam=(-7.4, 23.3, 3.3), aim=(-8.5, 31.8, 0.0), lens=26, seed=4),
}


def _pen_test(kinds, frames=(30, 102), res=(960, 540)):
    """Two fenced pens in the meadow of the real village under engine.look's daylight: five cows and a calf, six
    hens and two chicks, each brought to life by ONE wander() call; stills at two moments three seconds apart."""
    import os

    from . import look, quick, village

    scene = quick.reset()
    look.setup_render(scene, res=res, samples=16, threads=2, motion_blur=True)
    v = village.build_village(scene, seed=1)
    look.set_time(scene, "day", sun_azimuth=205.0, sun_elevation=46.0)
    look.setup_compositor(scene, bloom=1.0, grade="warm")
    v.set_lantern_energy(0.0)
    herds = {}
    for kind in kinds:
        cfg = PENS[kind]
        pen = make_pen(scene, *cfg["cells"], gates=[cfg["gate"]], name="pen_" + kind)
        if kind == "cow":
            herd = [make_cow("cow%d" % i) for i in range(5)] + [make_cow("calf", baby=True)]
        else:
            herd = [make_chicken("hen%d" % i) for i in range(6)] + [make_chicken("chick%d" % i, baby=True) for i in range(2)]
        events = wander(herd, 1, frames[-1] + 30, pen["area"], seed=cfg["seed"])
        gap, edge = pen_report(herd, 1, frames[-1] + 30, pen["area"])
        print("%s pen %s, inside %s: %d animals, %d walks in %d frames; smallest gap between bodies %.2f, from the fence %.2f"
              % (kind, cfg["cells"], tuple(round(c, 2) for c in pen["area"]), len(herd),
                 sum(1 for ev in events.values() for e in ev if e[0] == "walk"), frames[-1] + 30, gap, edge))
        for name, ev in events.items():
            print("   %-7s %s" % (name, " ".join("%s %d-%d" % (e[0], e[1], e[2]) for e in ev)))
        herds[kind] = herd
    for kind in kinds:
        cfg = PENS[kind]
        quick.camera(scene, cfg["cam"], cfg["aim"], lens=cfg["lens"])
        for n, f in enumerate(frames):
            scene.frame_set(f)
            moving = [a.name for a in herds[kind] if (a.pos_at(f + 1) - a.pos_at(f)).length > 1e-4]
            path = os.path.join(quick.TEST_DIR, "animals_pen_%s_%d.png" % (kind, n + 1))
            scene.render.filepath = path
            bpy.ops.render.render(write_still=True)
            print("wrote", path, "frame", f, "| walking:", ", ".join(moving) or "-")


if __name__ == "__main__":
    which = set(sys.argv[1:])
    if not which or "check" in which:
        if not _check():
            sys.exit(1)
    _selftest(which - {"check"})
