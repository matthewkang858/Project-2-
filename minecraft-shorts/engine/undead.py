"""ZOMBIES, ZOMBIE VILLAGERS, and the INFECT-AND-CURE sequence. New module; edits no other file.

Everything is transcribed from the Java Edition 26.x client classes (named next to each number) and drawn with the
game's own textures through engine.mcassets. Blender axes as everywhere: +X east, +Y north, +Z up, 1 block = 1
unit, characters face -Y at yaw 0, 24 fps (the game runs 20 ticks per second: 1 tick = 1.2 frames).

PUBLIC API  (frames are film frames; "camera" = the Shot that films it, a Film, or a camera object: particles
             face it, exactly as in engine.fx)

  make_zombie(name, baby=False, variant="zombie", collection=None) -> Undead
      The vanilla zombie (HumanoidModel.createMesh: 2.0 tall, Steve is 1.875) with entity/zombie/zombie.png, arms
      held out in front. baby=True is the game's own baby model (BabyZombieModel, 0.94 tall, zombie_baby.png).
      variant="husk": the same model with husk.png at the game's 1.0625 scale (2.125 tall).
  make_zombie_villager(name, profession="none", biome="plains", baby=False, level=None, collection=None) -> Undead
      ZombieVillagerModel (villager head with nose and hat rim, zombie arms; 2.125 tall, a villager is 1.99) with
      zombie_villager.png + type/<biome> + profession/<p> + profession_level/<badge>, layered exactly as the
      villager's (VillagerProfessionLayer): a zombified farmer wears the farmer's straw hat. profession = any of
      engine.characters.villager_professions(); level 1..5 = badge (None = 1, stone). baby=True is
      BabyZombieVillagerModel with zombie_villager_baby.png + baby/<biome> (babies show no profession; 1.0 tall).
  add_zombie(st, name="zombie", **kw) / add_zombie_villager(st, name="zombie_villager", profession="none", **kw)
      The same, registered with a films.lookdev.Stage (st.cast[name]): then st.use(shot, z), st.hero(shot, "zombie", z).

  Undead (a subclass of engine.characters.Character: root / hips / body / head / arm_l / arm_r / leg_l / leg_r)
      place(frame, pos, yaw=0.0)            hard cut to a spot: upright, neutral legs, arms out (use at shot cuts)
      show(frame, visible=True)             keyed visibility (Stage.finish calls it)
      walk(frame, points, speed=None, run=False, from_current=False, gait="planted") -> end frame
                                            the game's speed (WALK_SPEED 2.33 blocks/s, babies BABY_SPEED 5.24:
                                            zombies have ONE speed, run= changes nothing). gait="planted": the
                                            sole on the ground does not slide; gait="vanilla": the game's exact
                                            leg wave (its feet slide, see GAIT). The arms stay out and do not swing
      look_at / track / face / turn         as every Character; the head is clamped to the game's 75 degrees of
                                            yaw and 40 of pitch (Mob.getMaxHeadYRot / XRot)
      idle(frame_start, frame_end, seed=0)  the head turns to look around (RandomLookAroundGoal); the arms' slow
                                            bob needs no call: it never stops, wherever the zombie stands (a cell,
                                            a boat, a street), also while it walks or attacks
      aggro(frame, on=True, ease=3)         arms from the resting -80 degrees up to the "aggressive" -120 degrees
                                            (on=False: back down). The game snaps (ease=0); 3 frames is a film choice
      attack(frame, target=None, **hurt_kw) -> end frame
                                            the swing (both arms chop down 53 degrees and back in 6 ticks, the body
                                            twists 0.2 rad). With target= a Character it is hurt ON `frame`: in
                                            the game damage, red flash and knock-back come on the tick the swing
                                            STARTS. swing_arm(frame) is the same without a target
      hurt(frame, attacker=None, knockback=True, max_back=None) -> end frame      see hurt() below
      die(frame, camera=None, attacker=None, ...) -> the first frame it is gone   see die() below
      sit(frame, on=True)                   the legs of a passenger (boat, minecart): -81 degrees forward, splayed
      hold(obj)                             an item in the right hand (the player's hand placement); hold(None)
      size (hit box width, height), walk_speed, last_walk (dict of the last walk), baby, variant, profession
      nod / shake / flinch / shiver / lie_down / pos_at / yaw_at / eye_point: inherited, unchanged

  hurt(character, frame, attacker=None, knockback=True, max_back=None, flash=True) -> end frame
      The game's hurt for ANY Character (zombie, villager, fx job villager, Steve, golem): the red tint for 10
      ticks = 12 frames (OverlayTexture: every texel 70 % itself + 30 % pure red), the knock-back hop away from
      `attacker` (a Character or a point; None = straight back): 0.96 block up, 1.9 blocks back, on the ground
      again after 10 ticks, and the legs flailing as the game's walk animation does when a mob is hit.
      max_back = blocks of room behind it (a wall, a 1x1 cell: 0.2); knockback=False: the flash alone;
      knockback=0.5: half the strength. A golem only flashes (knock-back resistance 1).
  die(character, frame, camera=None, attacker=None, knockback=True, max_back=None, poof=True, seed=0,
      village=None, glow=None) -> gone frame
      The game's death for ANY Character: red from `frame` on, knocked back, legs straight, and one tick later
      the body tips over to its LEFT about its feet: 90 degrees * sqrt((tick - 1) * 0.08), flat after 13.5 ticks.
      On tick 20 (frame + 24 = the return value) it is gone and the 20 white 'poof' particles appear around its
      UPRIGHT hit box (not along the lying body) and rise. Bloodless, nothing else. It stays gone until its
      next place(). A mob that dies in mid-walk stops there.
  poof(target, frame, camera=None, seed=0, village=None, glow=None, size=None, count=20) -> fx.Burst
      Only the cloud (entity event 60): target = a Character (its feet at `frame`) or a feet point.
  vanish(character, frame) / appear(character, frame)
      Not there / there again from `frame` on, with no effect at all (independent of show(), which Stage.finish
      uses for the shots: a character is rendered when it is shown AND there).

  infect(villager, zombie_villager, frame, attacker=None, knockback=True, max_back=None) -> end frame
      THE INFECTION, as the client shows it (Zombie.killedEntity -> Mob.convertTo): on the tick of the killing
      blow the villager is simply replaced, where it stands and facing the way it faced, by the zombie villager.
      No body tips over, no poof, no particles at all (level event 1026 is only the sound), and the red flash of
      that last blow is never drawn: the zombie villager appears in its normal colours and takes the blow's
      knock-back hop (it inherits the velocity). Key the earlier blows with zombie.attack(f, target=villager) (one
      a second), then infect() on the frame of the last one together with zombie.attack(frame).
      The zombie villager is not rendered before `frame`, whatever Stage.use says; the villager not after it.
  throw_potion(start, target, frame, camera=None, effect="weakness", village=None, seed=0, count=100, glow=None,
               speed=None) -> impact frame
      A splash potion thrown at `frame` from `start` (a point, or the player Character who throws it: the game
      releases it 0.1 under the eyes and his arm swings) to `target` (a point, or a Character: it breaks on the
      hit box). The bottle flies the game's arc (0.5 block per tick = 10 blocks/s, gravity 0.05, drag 0.99), drawn
      as ThrownItemRenderer does: the splash-potion sprite, its liquid in the effect's colour, half a block wide,
      always facing the camera. On the returned frame it is gone and the splash appears (level event 2002): 8
      shards of the bottle's sprite and 100 swirl particles in the potion's colour (Weakness: dark grey 0x484D48)
      spreading along the ground (2 blocks in the median, a few as far as 7) and rising. The return value is an
      int with attributes .bottle
      (Object), .burst (fx.Burst), .hit (Vector), .speed (blocks per tick used), .frames (throw, impact).
  effect_swirls(character, frame_start, frame_end, effect="strength", camera=None, seed=0, glow=None,
                size=None) -> fx.Burst
      The swirls every mob with a potion effect gives off (LivingEntity.tickEffects): one 'entity_effect'
      particle on one tick in four, somewhere in its hit box, rising slowly, in the effect's colour.
      effect = "weakness" | "strength" | "nausea" | (r, g, b).
  cure(zombie_villager, villager, frame_start, frame_end, camera=None, player=None, weakness_from=None,
       nausea=240, seed=0, glow=None, shake=1.0) -> dict
      THE CURE. frame_start = the golden apple is used on him: player (a Character, standing still by then: his
      walk has ended) swings his arm and the apple in his hand is consumed. Until frame_end the zombie villager
      SHAKES (the renderer's +-1.26 degrees of yaw, a new value every tick: a fine tremble, shake=3 shows at any
      size) and gives off Strength swirls (yellow 0xFFC700); on frame_end the villager stands
      in his place (no particles: level event 1027 is a sound) and gives off Nausea swirls (dark purple
      0x551D4A) for `nausea` frames (the game: 200 ticks = 240 frames). weakness_from = the impact frame of the
      potion: Weakness swirls from then until the apple. Any duration works (the game takes 3 to 5 minutes:
      3600-6000 ticks): six seconds in one shot, or cure(zv, v, f, f + 30) before a time cut and
      effect_swirls(...) / shake(...) in the shot after it.
  shake(zombie_villager, frame_start, frame_end, amount=1.0)        only the conversion shake
  flee(villager, frame, threat, distance=6.0, speed=VILLAGER_PANIC_SPEED) -> end frame
      A villager runs straight away from a zombie (Character.walk(run=True) at the game's panic speed).
  knockback_track(strength=0.4, max_back=None) -> [(blocks back, blocks up) after each tick]
  zombie_sheet(baby, variant) / zombie_villager_sheet(profession, biome, level, baby) -> (key, HxWx4 uint8)
  Constants: WALK_SPEED, BABY_SPEED, VILLAGER_WALK_SPEED, VILLAGER_PANIC_SPEED, ZOMBIE_SIZE, BABY_SIZE,
  ARMS_OUT, ARMS_RAISED, HURT_FRAMES, DEATH_FRAMES, CONVERSION_TICKS, EFFECT_COLOURS, POTION_SPEED, FACTS.

USING THEM IN A FILM (st = films.lookdev.Stage)
    z = undead.add_zombie(st, "zombie"); st.use(s, z); st.hero(s, "zombie", z)
    z.place(f0, spot, yaw); z.idle(f0, f1 + 1); z.aggro(f0 + 12); end = z.walk(f0 + 12, [spot, near_villager])
    z.attack(end, target=villager)                       # arm swing; the villager flashes red and hops back
    zv = undead.add_zombie_villager(st, "zv", "farmer"); st.use(s, zv)
    undead.infect(villager, zv, end + 24, attacker=z); z.attack(end + 24)
    hit = undead.throw_potion(steve, zv, f, camera=s)    # hit = the impact frame
    steve.hold(props.make_item("golden_apple")) BEFORE his place(); undead.cure(zv, villager, hit + 20, hit + 164,
                                                                                camera=s, player=steve, weakness_from=hit)
    gone = z.die(f, camera=s, attacker=steve)            # tips over, poof on `gone`
    Key every character in frame order. A cut that jumps in time: fx.stop_particles(first frame of the new shot).
    The red flash, vanish / appear and death are kept in step with show() by wrapping the character's own show /
    place / _rekey: a character is rendered when shown AND there, and its red twin instead while it flashes.

GAIT (HumanoidModel.setupAnim, LivingEntity.updateWalkAnimation)
    The game: legs +-1.4 * s * cos(0.6662 * p), s = min(4 * blocks per tick, 1), p grows by s every tick (three
    times as fast for a baby). An adult (0.1165 block per tick) swings +-37 degrees once every 2.36 blocks
    (1.01 s) while a planted compass step of that swing covers 0.91 block, so each foot slides about 0.3 block
    per step. gait="vanilla" is exactly that, without any bob (use it when the feet are out of frame).
    gait="planted" keeps the swing and the speed and shortens the cycle to 1.82 blocks (0.78 s): the sole on the
    ground stays where it was put, the other leg passes it, and the hips sink by leg * (1 - cos(swing)) so both
    soles stay on the ground (0.15 block for an adult: a film choice, the game has no bob). A baby (0.262 block
    per tick) has legs of 4 pixels: its steps are 1.9 frames long in either gait, a blur at 24 fps, as in the
    game (planted: +-57 degrees instead of the game's +-80). Turns (walk corners, face, turn) are made on the
    spot, where planted feet skate: start walks facing the way they go. Character.walk is linear (no ease in or
    out), so a zombie is at full speed on its first frame.

WHAT THE GAME DOES (read from the classes; FACTS has the numbers)
  - arms: AnimationUtils.animateZombieArms replaces the walking arm swing: both arms -80 degrees (pi / 2.25),
    toed in 0.1 rad; "aggressive" -120 degrees (pi / 1.5). ZombieAttackGoal raises them when the zombie has had
    a target for 5 ticks and drops them for the 10 ticks after every blow. Always on top: the slow bob
    (AnimationUtils.bobModelPart: +-0.05 rad, 3.5 s and 4.7 s periods).
  - a zombie hits once a second (MeleeAttackGoal, 20 ticks) for 3 damage (difficulty only scales what PLAYERS
    take): a villager (20 health) is dead after 7 blows. Normal: half of them become zombie villagers; Hard: all;
    Easy: none (they just die: undead.die, with the poof).
  - zombies walk at 2.33 blocks/s whether strolling or chasing; babies at 5.24 (attribute x 1.5, speed is
    quadratic). A panicking villager makes 6.2 blocks/s, a walking one 2.75: no zombie catches a villager that
    has room to run. Villagers notice a zombie within 8 blocks. Zombies see 35 blocks.
  - doors: only on Hard, and only some zombies: 240 ticks (12 s) of banging with the crack stages on the door.
  - zombies burn in daylight: stage them at night, underground or under a roof (no fire is built here).

MEASURED (`$BPY -m engine.undead check` prints and asserts these; proof stills out/test/undead_*.png)
    zombie 2.0 tall, 0.5 wide over the body and 1.0 over the arms, eyes 1.74; baby 0.94 tall, eyes 0.775;
    zombie villager 2.125 tall (hat rim 1.0 wide), eyes 1.74; baby zombie villager 1.0 tall, eyes 0.67; husk 2.125.
    Arms out: the arm ends 0.62 in front of the centre line, 1.27 above the ground (raised: 0.54 in front, 1.69
    high, beside the face). Stand a victim 1.2-1.3 blocks from the zombie: the hands then stop just short of it.
    Planted walk: 1.8 blocks and 18.6 frames per cycle, the carrying sole drifts under 0.002 block per step
    (baby: 0.008); vanilla walk: 2.36 blocks per cycle, each sole slides about 0.3 block per step.
    Knock-back: 0.4, 0.62, 0.82, 1.0, 1.16 ... blocks back after 1, 2, 3, 4, 5 ticks, highest (0.965) on tick 5,
    down on tick 10, at rest 1.99 blocks back after 16 ticks = 19 frames; the legs are still 5 frames later.
    Death: 0 / 25 / 51 / 72 / 90 degrees at 1 / 2 / 5 / 9 / 13.5 ticks; lying flat, half the body is in the ground.
    A thrown potion reaches a chest 4.5 blocks away and the ground 5.5 blocks away (15 ticks, apex 2.2) at the
    game's 0.5 block per tick; 3.5 blocks take 8 ticks = 10 frames. Farther than that throw_potion raises the
    speed until it arrives and prints a line saying so (the value is in .speed).
    The splash's swirls travel 0.5-7 blocks (median 2) in their 8-40 ticks; effect swirls rise 0.3-1.8 blocks.

GOTCHAS
  - hurt / die / infect / cure change what is rendered through extra "twin" meshes (the red copy) and their own
    visibility keys: never key hide_render on these characters yourself, use show / vanish / appear.
  - A hit interrupts a walk (the knock-back takes over the root). Key the next walk from_current=True.
  - attack(), aggro() and the bob own the arm channels (absolute keys, rewritten on every call): raise_arm() maps
    to aggro(), Character.swing_arm is attack(). Nothing else may key the arms.
  - Particles are world objects with their own lifetimes (poof up to 82 ticks, swirls 8-40): a cut to another
    angle keeps them, a cut in time needs fx.stop_particles. A splash is about 800 objects (100 particles x 8
    sprite stages): count=40 is plenty for a background splash.
  - While a character flashes red its own meshes are hidden and the twins are rendered: a composition check on
    the head object (Stage.hero) should look at a frame outside the 12 frames of a flash. An item shown with
    fx.hold_out is not part of the character: end its window yourself when the villager is infected.
  - Not built: burning, drowned / giant, armour and held-item poses of zombies, door breaking (use fx.break_block
    crack stages on a door if a film needs it), the Weakness effect's own behaviour.

Self-test:  $BPY -m engine.undead [check lineup lineup2 turn walk walk_vanilla attack hurt death infect cure cure2
                                    items hall hall_bars street night_fx]
(no argument = check: 72 numeric checks of the keyframes, no rendering, 10 s; exit code 1 if one fails. Each other
name renders its proof stills out/test/undead_<name>*.png: one name per call stays under the 300 s limit.)
"""
import math
import sys
import zlib

import bpy
import numpy as np
from mathutils import Matrix, Vector

from . import characters as ch
from . import fx
from . import mcassets as mc
from . import mobs
from . import pix

FPS = ch.FPS
TICK = FPS / 20.0                    # frames per game tick
_LOC, _ROT = "location", "rotation_euler"

# ---- EntityTypes.ZOMBIE / ZOMBIE_VILLAGER: sized(0.6F, 1.95F).eyeHeight(1.74F); Zombie.BABY_DIMENSIONS /
#      ZombieVillager.BABY_DIMENSIONS: scalable(0.49F, 0.98F) with eye heights 0.775 / 0.67
ZOMBIE_SIZE = (0.6, 1.95)
ZOMBIE_EYE = 1.74
BABY_SIZE = (0.49, 0.98)
BABY_ZOMBIE_EYE = 0.775
BABY_ZOMBIE_VILLAGER_EYE = 0.67
HUSK_SCALE = 1.0625                  # LayerDefinitions: ModelLayers.HUSK = the zombie mesh, MeshTransformer.scaling(1.0625)

# ---- Zombie.createAttributes(): MOVEMENT_SPEED 0.23, ATTACK_DAMAGE 3, ARMOR 2, FOLLOW_RANGE 35.
#      Zombie.addBehaviourGoals(): ZombieAttackGoal 1.0, MoveThroughVillageGoal 1.0, WaterAvoidingRandomStrollGoal
#      1.0: one speed for everything. Zombie.SPEED_MODIFIER_BABY: +0.5 ADD_MULTIPLIED_BASE.
#      Mob.setSpeed sets the forward input to the speed too, so blocks per tick = s * s / (1 - 0.546)
#      (engine.mobs.mob_speed; LivingEntity.aiStep scales the input by 0.98 BEFORE the AI sets it again).
SPEED_ATTRIBUTE = 0.23
BABY_SPEED_FACTOR = 1.5
WALK_SPEED = mobs.mob_speed(1.0, SPEED_ATTRIBUTE)                          # 2.330 blocks / s
BABY_SPEED = mobs.mob_speed(1.0, SPEED_ATTRIBUTE * BABY_SPEED_FACTOR)      # 5.243 blocks / s
# ---- Villager.createAttributes(): MOVEMENT_SPEED 0.5; Villager brain speed 0.5; VillagerGoalPackages.getPanicPackage:
#      speed * 1.5 away from NEAREST_HOSTILE / HURT_BY_ENTITY (6 blocks); VillagerHostilesSensor: zombies within 8
VILLAGER_WALK_SPEED = mobs.mob_speed(0.5, 0.5)                             # 2.753 blocks / s
VILLAGER_PANIC_SPEED = mobs.mob_speed(0.75, 0.5)                           # 6.195 blocks / s
VILLAGER_SEES_ZOMBIE = 8.0
ZOMBIE_FOLLOW_RANGE = 35.0
ATTACK_INTERVAL_TICKS = 20           # MeleeAttackGoal.attackInterval
ATTACK_DAMAGE = 3.0                  # to any mob; only Player.hurtServer scales it (Easy 2.5, Hard 4.5)
DOOR_BREAK_TICKS = 240               # BreakDoorGoal.DEFAULT_DOOR_BREAK_TIME (Hard only)

# ---- Mob.getMaxHeadYRot() 75, getMaxHeadXRot() 40 (Zombie does not override them)
HEAD_YAW_MAX = math.radians(75.0)
HEAD_PITCH_MAX = math.radians(40.0)

# ---- AnimationUtils.animateZombieArms / bobModelPart, HumanoidModel.setupAnim / setupAttackAnimation
ARMS_OUT = -math.pi / 2.25           # arm xRot of a zombie that is not "aggressive": -80 degrees
ARMS_RAISED = -math.pi / 1.5         # ... and of one that is: -120 degrees
ARM_TOE = 0.1                        # yRot: right arm -0.1, left arm +0.1 (toed in)
SWING_DOWN = 1.2                     # xRot += sin(a * pi) * 1.2 - sin((1 - (1 - a)^2) * pi) * 0.4 during the swing
SWING_BACK = 0.4
SWING_TOE = 0.6                      # yRot: 0.1 - sin(a * pi) * 0.6
BODY_TWIST = 0.2                     # body.yRot = sin(sqrt(a) * 2 pi) * 0.2
BOB_AMOUNT = 0.05                    # zRot += +-(cos(age * 0.09) * 0.05 + 0.05), xRot += +-sin(age * 0.067) * 0.05
BOB_Z_RATE = 0.09
BOB_X_RATE = 0.067
LEG_SWING = 1.4                      # leg xRot = cos(pos * 0.6662 [+ pi]) * 1.4 * walkAnimationSpeed
LEG_RATE = 0.6662
VILLAGER_LEG = 0.5                   # VillagerModel: the same wave * 0.5
ANIM_PER_BLOCK = 4.0                 # LivingEntity.updateWalkAnimation: target = min(4 * blocks moved, 1), lerp 0.4
ANIM_LERP = 0.4
BABY_ANIM_SCALE = 3.0                # ... and positionScale 3 for babies
HURT_ANIM_SPEED = 1.5                # LivingEntity.handleDamageEvent: walkAnimation.setSpeed(1.5F)
SIT_LEG = (-1.4137167, 0.31415927, 0.07853982)    # HumanoidModel.setupAnim, isPassenger: leg xRot, yRot, zRot

# ---- LivingEntity.handleDamageEvent / animateHurt, LivingEntityRenderer, OverlayTexture
HURT_TICKS = 10                      # hurtDuration = hurtTime = 10
HURT_FRAMES = int(round(HURT_TICKS * TICK))        # 12
OVERLAY_KEEP = 178.0 / 255.0         # OverlayTexture: rows 0-7 = 0xB2FF0000; entity.fsh: mix(overlay.rgb, colour, overlay.a)
OVERLAY_RGB = (1.0, 0.0, 0.0)
DEATH_TICKS = 20                     # LivingEntity.tickDeath: ++deathTime >= 20 -> entity event 60, remove
DEATH_FRAMES = int(round(DEATH_TICKS * TICK))      # 24
DEATH_FLIP = 90.0                    # LivingEntityRenderer.getFlipDegrees; angle = 90 * min(1, sqrt((t - 1) / 20 * 1.6))
POOF_COUNT = 20                      # LivingEntity.makePoofParticles
SHAKE_DEGREES = math.pi * 0.4        # LivingEntityRenderer.setupRotations: bodyRot += cos(floor(age) * 3.25) * pi * 0.4
SHAKE_RATE = 3.25

# ---- LivingEntity.knockback / travelInAir
KNOCKBACK = 0.4                      # LivingEntity.hurtServer: knockback(0.4F, dx, dz)
REST_VY = -0.0784                    # the vertical speed of a mob standing on the ground ((0 - 0.08) * 0.98)
GRAVITY = 0.08
AIR_DRAG_Y = 0.98
AIR_DRAG = 0.91
GROUND_DRAG = 0.6 * 0.91

# ---- ZombieVillager.mobInteract / startConverting / finishConversion, MobEffects
CONVERSION_TICKS = (3600, 6000)      # random.nextInt(2401) + 3600: three to five minutes
NAUSEA_TICKS = 200                   # finishConversion: MobEffectInstance(NAUSEA, 200, 0)
EFFECT_COLOURS = {"weakness": (72, 77, 72), "strength": (255, 199, 0), "nausea": (85, 29, 74)}   # 4738376, 16762624, 5578058
EFFECT_CHANCE = 4                    # LivingEntity.tickEffects: random.nextInt(4) == 0 every tick (visible, not ambient)
EFFECT_SPRITES = tuple("effect_%d" % i for i in range(7, -1, -1))     # particles/entity_effect.json and effect.json
POOF_SPRITES = tuple("generic_%d" % i for i in range(7, -1, -1))      # particles/poof.json

# ---- ThrowablePotionItem.use, AbstractThrownPotion, ThrowableProjectile.tick, ThrownItemRenderer, LevelEventHandler
POTION_SPEED = 0.5                   # PROJECTILE_SHOOT_POWER, blocks per tick (thrown 20 degrees above the look direction)
POTION_GRAVITY = 0.05                # AbstractThrownPotion.getDefaultGravity
POTION_DRAG = 0.99                   # ThrowableProjectile.getAirDrag; per tick: v.y -= g, v *= drag, pos += v
POTION_EYE_DROP = 0.1                # thrown from getEyeY() - 0.1
PLAYER_EYE = 1.62
POTION_MARGIN = 0.3                  # ProjectileUtil: the target's hit box grown by 0.3
SPLASH_SHARDS = 8                    # LevelEventHandler.potionSplashParticles: 8 item particles + 100 spell particles
SPLASH_COUNT = 100
SPLASH_RANGE = 4.0                   # AbstractThrownPotion.SPLASH_RANGE: mobs within 4 blocks get the effect
ITEM_GROUND = (0.125, 0.5)           # models/item/generated.json display.ground: translation [0, 2, 0], scale 0.5

FACTS = {
    "zombie_speed_blocks_per_s": WALK_SPEED, "baby_zombie_speed_blocks_per_s": BABY_SPEED,
    "villager_walk_blocks_per_s": VILLAGER_WALK_SPEED, "villager_panic_blocks_per_s": VILLAGER_PANIC_SPEED,
    "villager_notices_zombie_within_blocks": VILLAGER_SEES_ZOMBIE, "zombie_follow_range_blocks": ZOMBIE_FOLLOW_RANGE,
    "attack_interval_ticks": ATTACK_INTERVAL_TICKS, "attack_damage": ATTACK_DAMAGE, "villager_health": 20.0,
    "blows_to_kill_a_villager": 7,
    "infection_chance": {"easy": 0.0, "normal": 0.5, "hard": 1.0},
    "arms_raised_after_ticks_with_target": 5, "arms_dropped_ticks_after_a_blow": 10,
    "door_break_ticks_hard_only": DOOR_BREAK_TICKS, "hurt_ticks": HURT_TICKS, "death_ticks": DEATH_TICKS,
    "conversion_ticks": CONVERSION_TICKS, "nausea_ticks_after_cure": NAUSEA_TICKS,
    "effect_particles_per_second": 20.0 / EFFECT_CHANCE, "potion_speed_blocks_per_tick": POTION_SPEED,
    "splash_range_blocks": SPLASH_RANGE,
}


# ----------------------------------------------------------------------------------------------------
# the models (pixels, the game's model space: x to the mob's left, y DOWN, z to its back, feet on y = 24)
# ----------------------------------------------------------------------------------------------------
def _zombie_spec(scale=1.0):
    """net.minecraft.client.model.HumanoidModel.createMesh(CubeDeformation.NONE, 0) at 64 x 64: ModelLayers.ZOMBIE
    (no MeshTransformer; AbstractZombieRenderer has no scale(), so a zombie is drawn at full model size: 2.0)."""
    C = ch._cube
    eye = 24.0 - ZOMBIE_EYE * 16.0
    return dict(
        tex=(64, 64), scale=scale, hip=12.0, top=-8.0, eye=eye, back=2.0, sleep_eye=ZOMBIE_EYE,
        parts=[
            dict(name="body", parent="hips", pivot=(0, 12, 0), groups=[([ch._pose(0, -12, 0)], [
                C(16, 16, -4, 0, -2, 8, 12, 4)])]),
            dict(name="head", parent="body", pivot=(0, 0, 0), groups=[([], [
                C(0, 0, -4, -8, -4, 8, 8, 8),
                C(32, 0, -4, -8, -4, 8, 8, 8, grow=0.5)])]),               # hat
            dict(name="arm_r", parent="body", pivot=(-5, 2, 0), groups=[([], [C(40, 16, -3, -2, -2, 4, 12, 4)])]),
            dict(name="arm_l", parent="body", pivot=(5, 2, 0),
                 groups=[([], [C(40, 16, -1, -2, -2, 4, 12, 4, mirror=True)])]),
            # the vanilla legs overlap by 0.2 px at the centre line; xclip trims each at x = 0 (no coplanar faces)
            dict(name="leg_r", parent="hips", pivot=(-1.9, 12, 0), xclip=(None, 1.9),
                 groups=[([], [C(0, 16, -2, 0, -2, 4, 12, 4)])]),
            dict(name="leg_l", parent="hips", pivot=(1.9, 12, 0), xclip=(-1.9, None),
                 groups=[([], [C(0, 16, -2, 0, -2, 4, 12, 4, mirror=True)])]),
        ])


def _baby_zombie_spec():
    """net.minecraft.client.model.monster.zombie.BabyZombieModel.createBodyLayer(NONE): ModelLayers.ZOMBIE_BABY."""
    C = ch._cube
    return dict(
        tex=(64, 64), scale=1.0, hip=20.0, top=9.0, eye=24.0 - BABY_ZOMBIE_EYE * 16.0, back=1.0,
        sleep_eye=BABY_ZOMBIE_EYE,
        parts=[
            dict(name="body", parent="hips", pivot=(0, 20, 0), groups=[([ch._pose(0, 17.5 - 20.0, 0)], [
                C(16, 16, -2, -2.5, -1, 4, 5, 2)])]),
            dict(name="head", parent="body", pivot=(0, 15.25, 0), groups=[([], [
                C(3, 3, -3, -6.25, -3, 6, 6, 6),
                C(35, 3, -3, -6.15, -3, 6, 6, 6, grow=0.25)])]),
            dict(name="arm_r", parent="body", pivot=(-3, 15.5, 0), groups=[([], [C(36, 16, -1, -0.5, -1, 2, 5, 2)])]),
            dict(name="arm_l", parent="body", pivot=(3, 15.5, 0), groups=[([], [C(28, 16, -1, -0.5, -1, 2, 5, 2)])]),
            dict(name="leg_r", parent="hips", pivot=(-1, 20, 0), groups=[([], [C(8, 16, -1, 0, -1, 2, 4, 2)])]),
            dict(name="leg_l", parent="hips", pivot=(1, 20, 0), groups=[([], [C(0, 16, -1, 0, -1, 2, 4, 2)])]),
        ])


def _zombie_villager_spec():
    """net.minecraft.client.model.monster.zombie.ZombieVillagerModel.createBodyLayer(): ModelLayers.ZOMBIE_VILLAGER
    (64 x 64, unscaled: 2.125 tall where the villager, drawn at 0.9375, is 1.99)."""
    C = ch._cube
    return dict(
        tex=(64, 64), scale=1.0, hip=12.0, top=-10.0, eye=24.0 - ZOMBIE_EYE * 16.0, back=3.0, sleep_eye=ZOMBIE_EYE,
        parts=[
            dict(name="body", parent="hips", pivot=(0, 12, 0), groups=[([ch._pose(0, -12, 0)], [
                C(16, 20, -4, 0, -3, 8, 12, 6),
                C(0, 38, -4, 0, -3, 8, 20, 6, grow=0.05)])]),               # the robe
            dict(name="head", parent="body", pivot=(0, 0, 0), groups=[
                ([], [C(0, 0, -4, -10, -4, 8, 10, 8),                       # head
                      C(24, 0, -1, -3, -6, 2, 4, 2),                        # nose
                      C(32, 0, -4, -10, -4, 8, 10, 8, grow=0.5)]),          # hat
                ([ch._pose(rx=-math.pi / 2.0)], [C(30, 47, -8, -8, -6, 16, 16, 1, two_sided=True)])]),   # hat_rim
            dict(name="arm_r", parent="body", pivot=(-5, 2, 0), groups=[([], [C(44, 22, -3, -2, -2, 4, 12, 4)])]),
            dict(name="arm_l", parent="body", pivot=(5, 2, 0),
                 groups=[([], [C(44, 22, -1, -2, -2, 4, 12, 4, mirror=True)])]),
            dict(name="leg_r", parent="hips", pivot=(-2, 12, 0), groups=[([], [C(0, 22, -2, 0, -2, 4, 12, 4)])]),
            dict(name="leg_l", parent="hips", pivot=(2, 12, 0),
                 groups=[([], [C(0, 22, -2, 0, -2, 4, 12, 4, mirror=True)])]),
        ])


def _baby_zombie_villager_spec():
    """net.minecraft.client.model.monster.zombie.BabyZombieVillagerModel.createBodyLayer()."""
    C, P = ch._cube, ch._pose
    return dict(
        tex=(64, 64), scale=1.0, hip=21.5, top=8.0, eye=24.0 - BABY_ZOMBIE_VILLAGER_EYE * 16.0, back=1.5,
        sleep_eye=BABY_ZOMBIE_VILLAGER_EYE,
        parts=[
            dict(name="body", parent="hips", pivot=(0, 21.5, 0), groups=[([P(0, 18.75 - 21.5, 0)], [
                C(0, 15, -2, -2.75, -1.5, 4, 5, 3),
                C(16, 22, -2, -2.75, -1.5, 4, 6, 3, grow=0.1)])]),          # the robe
            dict(name="head", parent="body", pivot=(0, 16, 0), groups=[
                ([], [C(0, 0, -4, -8, -3.5, 8, 8, 7)]),
                ([P(0, -4, 0)], [C(0, 31, -4, -4, -3.5, 8, 8, 7, grow=0.3)]),                 # hat
                ([P(0, -4.5, 0)], [C(0, 46, -7, -0.5, -6, 14, 1, 12, two_sided=True)]),       # hat_rim
                ([P(0, -1, -4)], [C(23, 0, -1, -1, -0.5, 2, 2, 1)])]),                        # nose
            dict(name="arm_r", parent="body", pivot=(-3, 15.5, 0), groups=[([], [C(24, 15, -1, -0.5, -1, 2, 5, 2)])]),
            dict(name="arm_l", parent="body", pivot=(3, 15.5, 0), groups=[([], [C(16, 15, -1, -0.5, -1, 2, 5, 2)])]),
            dict(name="leg_r", parent="hips", pivot=(-1, 21.5, 0), groups=[([], [C(8, 23, -1, -0.5, -1, 2, 3, 2)])]),
            dict(name="leg_l", parent="hips", pivot=(1, 21.5, 0), groups=[([], [C(0, 23, -1, -0.5, -1, 2, 3, 2)])]),
        ])


def zombie_sheet(baby=False, variant="zombie"):
    """(key, HxWx4 uint8) entity/zombie/<zombie|husk>[_baby].png, alpha cut at 0.1 (AbstractZombieRenderer)."""
    if variant not in ("zombie", "husk"):
        raise ValueError("variant %r: use 'zombie' or 'husk'" % (variant,))
    path = "entity/zombie/%s%s" % (variant, "_baby" if baby else "")
    arr = ch._game_texture(path)
    sheet = np.zeros_like(arr)
    ch._over(sheet, arr)
    return "undead_%s%s" % (variant, "_baby" if baby else ""), sheet


def zombie_villager_sheet(profession="none", biome="plains", level=1, baby=False):
    """(key, HxWx4 uint8) the zombie villager's texture layers composited as VillagerProfessionLayer draws them
    for ZombieVillagerRenderer (path prefix 'zombie_villager').

    Adult: zombie_villager.png, then type/<biome>.png (without its head parts when the profession's hat hides the
    type hat: profession hat 'full', or 'partial' over a 'full' type hat), then profession/<p>.png, then the badge
    profession_level/<stone|iron|gold|emerald|diamond>.png (not for 'none' and 'nitwit').
    Baby: zombie_villager_baby.png, then baby/<biome>.png (babies show no profession)."""
    root = "entity/zombie_villager/"
    if baby:
        sheet = np.zeros_like(ch._game_texture(root + "zombie_villager_baby"))
        ch._over(sheet, ch._game_texture(root + "zombie_villager_baby"))
        ch._over(sheet, ch._game_texture(root + "baby/%s" % biome))
        return "undead_zv_baby_%s" % biome, sheet
    badge = ch.LEVEL_BADGES[int(ch._clamp(1 if level is None else level, 1, len(ch.LEVEL_BADGES))) - 1]
    has_badge = profession not in ("none", "nitwit")
    key = "undead_zv_%s_%s%s" % (biome, profession, "_" + badge if has_badge else "")
    sheet = np.zeros_like(ch._game_texture(root + "zombie_villager"))
    ch._over(sheet, ch._game_texture(root + "zombie_villager"))
    type_hat = ch._hat_rule(root + "type/%s" % biome)
    prof_hat = ch._hat_rule(root + "profession/%s" % profession) if profession != "none" else "none"
    type_hat_shown = prof_hat == "none" or (prof_hat == "partial" and type_hat != "full")
    skip = ()
    if not type_hat_shown:                                  # the type layer is drawn with the NO_HAT model: no head at all
        head = next(p for p in _zombie_villager_spec()["parts"] if p["name"] == "head")
        skip = [ch._cube_uv_rect(c) for _chain, cubes in head["groups"] for c in cubes]
    ch._over(sheet, ch._game_texture(root + "type/%s" % biome), skip)
    if profession != "none":
        ch._over(sheet, ch._game_texture(root + "profession/%s" % profession))
        if has_badge:
            ch._over(sheet, ch._game_texture(root + "profession_level/%s" % badge))
    return key, sheet


# ----------------------------------------------------------------------------------------------------
# who is rendered: shown (Character.show) AND there (vanish / appear / death), and the red twin while it flashes
# ----------------------------------------------------------------------------------------------------
_STATE = "_undead_state"


def _hide_curve(ob):
    """The keys of an object's hide_render curve as [(frame, value)], or None when it has none."""
    fc = ch._find(ob, "hide_render", 0)
    if fc is None or not len(fc.keyframe_points):
        return None
    return [(float(kp.co.x), float(kp.co.y)) for kp in fc.keyframe_points]


def _set_hide(ob, keys):
    """Replace an object's visibility keys by [(frame, hidden)] (CONSTANT); None = no keys at all."""
    for path in ("hide_render", "hide_viewport"):
        if keys is None or isinstance(keys, bool):
            fc = ch._find(ob, path, 0)
            if fc is not None:
                kps = fc.keyframe_points
                while len(kps):
                    kps.remove(kps[len(kps) - 1], fast=True)
                fc.update()
            if isinstance(keys, bool):
                setattr(ob, path, keys)
        else:
            fx._write(ob, path, 0, [k[0] for k in keys], [1.0 if k[1] else 0.0 for k in keys], "CONSTANT")
            setattr(ob, path, bool(keys[0][1]))


def _managed(c):
    """The objects of a character whose visibility this module combines: its meshes and its held item (not the
    iron golem's poppy, whose visibility engine.mobs rewrites on its own)."""
    flower = getattr(c, "flower", None)
    return [ob for ob in c.objects() if ob.type == "MESH" and ob is not flower]


def _state(c):
    """The bookkeeping of one character (made on first use; wraps its show / place / _rekey once)."""
    st = c.__dict__.get(_STATE)
    if st is None:
        st = c.__dict__[_STATE] = dict(flashes=[], presence=[], base={}, twins={}, depth=0, tipped=False)
        _save(c)
        for name in ("show", "_rekey", "hold"):
            if hasattr(c, name):
                _wrap(c, name)
        if not isinstance(c, Undead):
            _wrap(c, "place", after=lambda *a, **k: _on_place(c, a[0] if a else k["frame"]))
    return st


def _wrap(c, name, after=None):
    """Shadow a bound method of the character by one that keeps this module's visibility keys in step with it."""
    inner = getattr(c, name)

    def wrapper(*args, **kwargs):
        st = c.__dict__[_STATE]
        outer = st["depth"] == 0
        if outer:
            _restore(c)
        st["depth"] += 1
        try:
            out = inner(*args, **kwargs)
        finally:
            st["depth"] -= 1
            if outer:
                _save(c)
        if after is not None:
            after(*args, **kwargs)
        if outer:
            _apply(c)
        return out

    wrapper.__doc__ = inner.__doc__
    c.__dict__[name] = wrapper


def _save(c):
    """Remember the visibility keys as the character's own code left them."""
    st = c.__dict__[_STATE]
    for ob in _managed(c):
        keys = _hide_curve(ob)
        st["base"][ob.name] = keys if keys is not None else bool(ob.hide_render)


def _restore(c):
    """Put the character's own visibility keys back (this module's combination is laid over them by _apply)."""
    st = c.__dict__[_STATE]
    for ob in _managed(c):
        if ob.name in st["base"]:
            _set_hide(ob, st["base"][ob.name])


def _present(st, frame):
    """Is the character there at `frame` (vanish / appear / death)?"""
    there = True
    for f, on, _why in st["presence"]:
        if f is None or f <= frame + 1e-6:
            there = on
    return there


def _flashing(st, frame):
    return any(a <= frame + 1e-6 < b for a, b in st["flashes"])


def _apply(c):
    """Write the combined visibility: a mesh is rendered when shown AND there AND not flashing; its red twin when
    shown AND there AND flashing."""
    st = c.__dict__[_STATE]
    if not st["flashes"] and not st["presence"]:
        return
    edges = {float(f) for a, b in st["flashes"] for f in (a, b)} | {float(f) for f, _on, _w in st["presence"] if f is not None}
    for ob in _managed(c):
        base = st["base"].get(ob.name)
        if base is None:
            base = st["base"][ob.name] = bool(ob.hide_render)
        frames = sorted(edges | ({k[0] for k in base} if isinstance(base, list) else set()))
        if not frames:
            continue

        def hidden(f, base=base):
            if isinstance(base, bool):
                return base
            value = base[0][1]
            for kf, kv in base:
                if kf <= f + 1e-6:
                    value = kv
            return value > 0.5

        lead = min(frames[0], 1.0) - 1.0
        times = [lead] + frames
        twin = st["twins"].get(ob.name)
        _set_hide(ob, [(f, hidden(f) or not _present(st, f) or (twin is not None and _flashing(st, f))) for f in times])
        if twin is not None:
            _set_hide(twin, [(f, hidden(f) or not _present(st, f) or not _flashing(st, f)) for f in times])


def _presence(c, frame, on, why):
    st = _state(c)
    _restore(c)
    frame = None if frame is None else int(frame)
    st["presence"] = [e for e in st["presence"] if e[0] != frame] + [(frame, bool(on), why)]
    st["presence"].sort(key=lambda e: -1e18 if e[0] is None else e[0])
    _apply(c)


def vanish(character, frame, why="vanish"):
    """Not rendered from `frame` on (no effect of any kind), until appear() / the next place() after a death."""
    _presence(character, frame, False, why)


def appear(character, frame):
    """There again from `frame` on (undoes vanish, an infection or a death)."""
    _presence(character, frame, True, "appear")


def _on_place(c, frame):
    """A place() after a death: the character is there again, upright."""
    st = c.__dict__.get(_STATE)
    if st is None:
        return
    last = None
    for e in st["presence"]:
        if e[0] is None or e[0] <= frame + 1e-6:
            last = e
    if last is not None and not last[1] and last[2] == "dead":
        st["presence"] = [e for e in st["presence"] if e[0] != int(frame)] + [(int(frame), True, "placed")]
        st["presence"].sort(key=lambda e: -1e18 if e[0] is None else e[0])
    if st["tipped"] and ch._find(c.root, _ROT, 1) is not None:
        ch._cut(c.root, _ROT, 1, frame, 0.0)


def _hurt_image(img):
    """The image with the game's red hurt overlay mixed in: every texel 70 % itself + 30 % red, in display values."""
    name = "undead_hurt/" + img.name
    out = bpy.data.images.get(name)
    if out is not None and tuple(out.size) == tuple(img.size):
        return out
    w, h = img.size
    buf = np.empty(w * h * 4, dtype=np.float32)
    img.pixels.foreach_get(buf)
    px = buf.reshape(-1, 4)
    for i in range(3):
        px[:, i] = px[:, i] * OVERLAY_KEEP + OVERLAY_RGB[i] * (1.0 - OVERLAY_KEEP)
    if out is not None:
        bpy.data.images.remove(out)
    out = bpy.data.images.new(name, w, h, alpha=True)
    out.alpha_mode = img.alpha_mode
    out.colorspace_settings.name = img.colorspace_settings.name
    out.pixels.foreach_set(px.ravel())
    try:
        out.pack()
    except RuntimeError:
        pass
    return out


def _hurt_material(mat):
    """A copy of a character material whose textures carry the red overlay."""
    name = mat.name + "~hurt"
    out = bpy.data.materials.get(name)
    if out is not None:
        return out
    out = mat.copy()
    out.name = name
    if out.node_tree is not None:
        for node in out.node_tree.nodes:
            if node.type == "TEX_IMAGE" and node.image is not None:
                node.image = _hurt_image(node.image)
    return out


def _twins(c):
    """Make the red twin of every mesh of the character that has none yet (parented one to one, hidden)."""
    st = _state(c)
    for ob in _managed(c):
        if ob.name in st["twins"] or ob is c.held:
            continue
        me = ob.data.copy()
        me.name = ob.data.name + "_hurt"
        for i, m in enumerate(me.materials):
            if m is not None:
                me.materials[i] = _hurt_material(m)
        twin = bpy.data.objects.new(ob.name + "_hurt", me)
        (ob.users_collection[0] if ob.users_collection else ch._collection(None)).objects.link(twin)
        twin.parent = ob
        twin.matrix_parent_inverse = Matrix.Identity(4)
        twin.hide_render = twin.hide_viewport = True
        st["twins"][ob.name] = twin
    return st


def _flash(c, f0, f1):
    """Red from frame f0 to f1 (exclusive)."""
    st = _twins(c)
    _restore(c)
    st["flashes"].append((int(f0), int(f1)))
    _apply(c)


def body_box(character):
    """(width, height) of a character's hit box in the game."""
    if isinstance(character, Undead):
        return character.size
    if character.kind == "villager":
        return (0.3, 0.975) if character.child else (0.6, 1.95)        # EntityTypes.VILLAGER, babies at half scale
    if character.kind == "player":
        return (0.6, 1.8)
    if character.kind == "golem":
        return (mobs.GOLEM_WIDTH, mobs.GOLEM_HEIGHT)
    return (0.6, float(character.height))


# ----------------------------------------------------------------------------------------------------
# knock-back, hurt, death
# ----------------------------------------------------------------------------------------------------
def knockback_track(strength=KNOCKBACK, max_back=None, max_ticks=80):
    """[(blocks back, blocks up)] after each game tick of a knock-back on level ground.

    LivingEntity.knockback: horizontal speed = strength away from the attacker, vertical = min(0.4, vy / 2 +
    strength) = 0.3608 for a mob standing on the ground; then LivingEntity.travelInAir every tick: move, vy =
    (vy - 0.08) * 0.98, horizontal speed * 0.546 on the ground and * 0.91 in the air. max_back = room behind."""
    vh = float(strength)
    vy = min(0.4, REST_VY / 2.0 + float(strength))
    x = y = 0.0
    ground = True
    out = []
    for _ in range(max_ticks):
        drag = GROUND_DRAG if ground else AIR_DRAG
        x += vh
        y += vy
        if max_back is not None and x > max_back:
            x, vh = float(max_back), 0.0
        ground = False
        if y <= 0.0:
            y, vy, ground = 0.0, 0.0, True
        out.append((x, y))
        vy = (vy - GRAVITY) * AIR_DRAG_Y
        vh *= drag
        if ground and abs(vh) < 0.003:
            break
    return out


def _away(c, frame, attacker):
    """Unit vector from the attacker to the character (None: straight back from the way it faces)."""
    here = c.pos_at(frame)
    if attacker is not None:
        src = attacker.pos_at(frame) if isinstance(attacker, ch.Character) else ch._vec3(attacker, here.z)
        d = Vector((here.x - src.x, here.y - src.y, 0.0))
        if d.length > 1e-4:
            return d.normalized()
    yaw = c.yaw_at(frame)
    return Vector((-math.sin(yaw), math.cos(yaw), 0.0))


def _leg_coefficient(c):
    """Leg swing in radians at walk-animation speed 1, or None for rigs whose legs follow another formula."""
    if c.kind == "villager":
        return LEG_SWING * VILLAGER_LEG
    if c.kind == "golem":
        return None
    return LEG_SWING


def _interrupt(c, frame, freeze=False):
    """A blow ends whatever walk was running: bob, lean, sway and swinging arms ease back to rest in 3 frames
    (the legs are keyed by the caller); freeze=True also stops the travel where it is."""
    chans = [(c.hips, _LOC, 2), (c.hips, _LOC, 0), (c.body, _ROT, 0), (c.body, _ROT, 1)]
    if c.arms is not None:
        chans.append((c.arms, _ROT, 0))
    elif not isinstance(c, Undead) and c.arm_r is not None and c.kind == "player":
        chans += [(c.arm_r, _ROT, 0), (c.arm_l, _ROT, 0)]
    for ob, path, index in chans:
        if ch._find(ob, path, index) is not None:
            ch._segment(ob, path, index, [(frame, None), (frame + 3, c._rest(ob, path, index))])
    if freeze:
        for i in range(3):
            if ch._find(c.root, _LOC, i) is not None:
                ch._segment(c.root, _LOC, i, [(frame, None, "LINEAR"), (frame + 1, ch._val(c.root, _LOC, i, frame))], "LINEAR")


def _knock(c, frame, attacker, strength, max_back, anim_speed):
    """Key the knock-back hop and the legs' flail from `frame` on; returns the frame it has come to rest."""
    f0 = float(frame)
    track = knockback_track(strength, max_back) if strength > 0.0 else []
    here = c.pos_at(f0)
    away = _away(c, f0, attacker)
    if track:
        _interrupt(c, f0)
        for i in range(3):
            keys = [(f0, None, "LINEAR")]
            for k, (back, up) in enumerate(track):
                keys.append((f0 + (k + 1) * TICK, here[i] + away[i] * back + (up if i == 2 else 0.0), "LINEAR"))
            ch._segment(c.root, _LOC, i, keys, "LINEAR")
    end = f0 + len(track) * TICK
    coef = _leg_coefficient(c)
    if coef is None or anim_speed is None:
        return int(math.ceil(end))
    # LivingEntity.updateWalkAnimation after handleDamageEvent set the speed to 1.5: the legs kick apart and
    # run on while the mob flies back, then settle
    scale = BABY_ANIM_SCALE if c.child else 1.0
    s_old, s, p = 0.0, float(anim_speed), 0.0
    sign = 1.0 if getattr(c, "_foot", 1) > 0 else -1.0
    keys_r = [(f0, None, "LINEAR")]
    keys_l = [(f0, None, "LINEAR")]
    moved_before = 0.0
    k = 0
    while k < 200:
        for j in (1, 2, 3, 4):                                  # the client draws between the last two tick states
            u = j / 4.0
            shown = min(s_old + (s - s_old) * u, 1.0)
            ang = coef * shown * math.cos((p - s * (1.0 - u)) * scale * LEG_RATE)
            t = f0 + (k + u) * TICK
            keys_r.append((t, sign * ang, "LINEAR"))
            keys_l.append((t, -sign * ang, "LINEAR"))
        back = track[k][0] if k < len(track) else (track[-1][0] if track else 0.0)
        target = min(ANIM_PER_BLOCK * (back - moved_before), 1.0)
        moved_before = back
        s_old, s = s, s + (target - s) * ANIM_LERP
        p += s
        k += 1
        if k >= len(track) and s < 0.02:
            break
    t_end = f0 + (k + 1) * TICK
    keys_r.append((t_end, 0.0))
    keys_l.append((t_end, 0.0))
    ch._segment(c.leg_r, _ROT, 0, keys_r, "LINEAR")
    ch._segment(c.leg_l, _ROT, 0, keys_l, "LINEAR")
    return int(math.ceil(max(end, t_end)))


def _strength(knockback, c):
    if c.kind == "golem":                                       # IronGolem: KNOCKBACK_RESISTANCE 1.0
        return 0.0
    if knockback is True:
        return KNOCKBACK
    if not knockback:
        return 0.0
    return KNOCKBACK * float(knockback)


def hurt(character, frame, attacker=None, knockback=True, max_back=None, flash=True):
    """The game's hurt for any Character on `frame`: red for 12 frames, the knock-back hop away from `attacker`
    (0.96 up, 1.9 back; max_back = room behind it; knockback=False: none), flailing legs. Returns the end frame."""
    f0 = int(round(frame))
    if flash:
        _flash(character, f0, f0 + HURT_FRAMES)
    end = _knock(character, f0, attacker, _strength(knockback, character), max_back, HURT_ANIM_SPEED)
    return max(end, f0 + HURT_FRAMES)


def _stage_runs(first, last, spawn, life, n):
    """[(sprite index, frame from, frame to)] of a particle whose sprite follows its age (SpriteSet.get(age, lifetime))."""
    runs = []
    for f in range(first, last):
        age = min(life, max(0, int(math.floor((f - spawn) / TICK + 1e-9))))
        i = min(n - 1, age * (n - 1) // max(life, 1))
        if runs and runs[-1][0] == i:
            runs[-1][2] = f + 1
        else:
            runs.append([i, f, f + 1])
    return runs


def _sprite_particle(burst, name, sprites, tint, glow, positions, spawn, size, cams, col):
    """One particle whose sprite changes with its age (setSpriteFromAge): the first stage is the moving quad,
    the later stages are quads parented to it, each rendered on its own frames."""
    life = len(positions) - 1

    def mesh_for(i):
        mat = fx._particle_material("particle/" + sprites[i], tint=tint, glow=glow)
        mname = "undead_quad/" + mat.name
        return bpy.data.meshes.get(mname) or fx._quad_mesh(mname, (0.0, 1.0, 0.0, 1.0), mat)

    parent = fx._particle_object(burst, name, mesh_for(0), positions, spawn, size, cams, col)
    rec = burst.particles[-1]
    runs = _stage_runs(rec["first"], rec["last"], spawn, life, len(sprites))
    if not runs:
        return parent
    i0, a0, b0 = runs[0]
    if i0 != 0:
        parent.data = mesh_for(i0)
    for path in ("hide_render", "hide_viewport"):
        fx._write(parent, path, 0, [a0 - 1, a0, b0], [1.0, 0.0, 1.0], "CONSTANT")
    whole_last = rec["last"]
    rec["last"] = b0
    for i, a, b in runs[1:]:
        ob = bpy.data.objects.new("%s_s%d" % (name, i), mesh_for(i))
        col.objects.link(ob)
        ob.parent = parent
        ob.matrix_parent_inverse = Matrix.Identity(4)
        for path in ("hide_render", "hide_viewport"):
            fx._write(ob, path, 0, [a - 1, a, b], [1.0, 0.0, 1.0], "CONSTANT")
        ob.hide_render = ob.hide_viewport = True
        ob.visible_shadow = False
        burst.objects.append(ob)
        burst.particles.append({"object": ob, "pos": positions, "lifetime": life, "size": size, "spawn": spawn,
                                "first": a, "last": b, "stage": i})
    burst.frame_end = max(burst.frame_end, whole_last - 1)
    return parent


def _grey(v):
    """A grey tint (0..1) in steps of 0.05, as 0-255 integers (a material per step, not per particle)."""
    g = int(round(ch._clamp(round(v * 20.0) / 20.0, 0.0, 1.0) * 255.0))
    return (g, g, g)


def poof(target, frame, camera=None, seed=0, village=None, glow=None, size=None, count=POOF_COUNT, collection=None):
    """The white cloud a mob leaves when its body vanishes (entity event 60, LivingEntity.makePoofParticles):
    20 'poof' particles (ExplodeParticle: sprites generic_7 .. generic_0 by age, grey 0.7-1.0, quads 0.2 to 1.4
    wide, 18-82 ticks) anywhere in a box twice the width of the hit box around where it stood, rising at up to 0.7
    block/s. target = a Character (its feet at `frame`) or the feet point; size = (width, height) of the hit box.
    Returns an engine.fx Burst."""
    frame = int(frame)
    feet = fx._point(target, frame)
    w, h = size if size is not None else (body_box(target) if isinstance(target, ch.Character) else ZOMBIE_SIZE)
    rng = fx._rng(seed, frame, 6011, int(feet.x * 16), int(feet.y * 16))
    burst = fx.Burst("poof", frame)
    cams = fx._camera_arg(camera)
    col = fx._collection(collection)
    solids = fx._Solids(village) if village is not None else None
    glow = fx.SPRITE_GLOW if glow is None else float(glow)
    for i in range(int(count)):
        va = rng.normal(0.0, 1.0, 3) * 0.02                      # nextGaussian() * 0.02 per axis
        p = np.array([feet.x + w * (2.0 * rng.random() - 1.0) - va[0] * 10.0,       # getRandomX(1.0) - vx * 10
                      feet.y + w * (2.0 * rng.random() - 1.0) - va[1] * 10.0,
                      feet.z + h * rng.random() - va[2] * 10.0])                    # getRandomY() - vy * 10
        v = va + (rng.random(3) * 2.0 - 1.0) * 0.05              # ExplodeParticle: xd = xa + (random * 2 - 1) * 0.05
        grey = rng.random() * 0.3 + 0.7
        quad = 0.1 * (rng.random() * rng.random() * 6.0 + 1.0)
        life = int(16.0 / (rng.random() * 0.8 + 0.2)) + 2
        path = fx._simulate(p, v, life, -0.1 * 0.04, 0.9, solids, 0.2, rng)       # gravity -0.1: it rises
        _sprite_particle(burst, "undead_poof_%d_%d" % (frame, i), POOF_SPRITES, _grey(grey), glow, path,
                         float(frame), quad, cams, col)
    return burst


def death_angle(ticks):
    """Degrees the body has tipped `ticks` after the killing blow (LivingEntityRenderer.setupRotations)."""
    if ticks <= 1.0:
        return 0.0
    return DEATH_FLIP * min(1.0, math.sqrt((ticks - 1.0) / 20.0 * 1.6))


def die(character, frame, camera=None, attacker=None, knockback=True, max_back=None, poof=True, seed=0,
        village=None, glow=None):
    """The game's death for any Character, killed on `frame`: red, knocked back, legs straight, tipping over to its
    left about its feet (flat after 13.5 ticks), gone on frame + 24 with the poof cloud where it stood. Returns that
    frame. The character stays gone until its next place()."""
    c = character
    f0 = int(round(frame))
    gone = f0 + DEATH_FRAMES
    st = _twins(c)
    _restore(c)
    st["flashes"].append((f0, gone))                             # hasRedOverlay = hurtTime > 0 || deathTime > 0
    st["presence"] = [e for e in st["presence"] if e[0] != gone] + [(gone, False, "dead")]
    st["presence"].sort(key=lambda e: -1e18 if e[0] is None else e[0])
    st["tipped"] = True
    _apply(c)
    _interrupt(c, f0, freeze=True)                               # whatever it was doing ends here
    _knock(c, f0, attacker, _strength(knockback, c), max_back, None)
    for leg in (c.leg_l, c.leg_r):                               # a dead mob's walk animation is stopped: legs straight
        if abs(ch._val(leg, _ROT, 0, f0)) > 1e-4 or ch._find(leg, _ROT, 0) is not None:
            ch._segment(leg, _ROT, 0, [(f0, None, "LINEAR"), (f0 + TICK, 0.0)], "LINEAR")
    ticks = [1.0, 1.25, 1.5, 2.0, 2.5, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0, 13.0, 13.5]
    keys = [(f0 + TICK, None, "LINEAR")] + [(f0 + t * TICK, math.radians(death_angle(t)), "LINEAR") for t in ticks[1:]]
    ch._segment(c.root, _ROT, 1, keys, "LINEAR")
    ch._cut(c.root, _ROT, 1, gone, 0.0)                          # (hidden from this frame on: upright for its next use)
    if poof:
        globals()["poof"](c.pos_at(gone - 0.5), gone, camera=camera, seed=seed, village=village, glow=glow,
                          size=body_box(c))
    return gone


# ----------------------------------------------------------------------------------------------------
# the zombie
# ----------------------------------------------------------------------------------------------------
_SWING = None


def _swing_shown():
    """Per game tick the two swing-animation values the client draws between (LivingEntity$SwingState, 6 ticks)."""
    global _SWING
    if _SWING is None:
        _SWING = fx._swing_run([0])[1]
    return _SWING


class Undead(ch.Character):
    """A zombie or zombie villager: an engine.characters.Character with the game's zombie arms, gait and limits."""

    def __init__(self, name, parts, spec, kind="zombie", profession=None, baby=False, variant="zombie", biome=None):
        super().__init__(name, kind, parts, spec, profession=profession, child=baby)
        self.baby, self.variant, self.biome = bool(baby), variant, biome
        self.size = BABY_SIZE if baby else ZOMBIE_SIZE                  # (the husk's hit box is the zombie's)
        self.walk_speed = BABY_SPEED if baby else WALK_SPEED
        self.last_walk = None
        self._aggro = []                 # (frame, on, ease)
        self._attacks = []               # frames on which a swing starts
        self._age0 = float(zlib.crc32(name.encode("utf-8")) % 4000) / 10.0     # ticks: every zombie bobs on its own
        # AnimationUtils.animateZombieArms: the rest pose (model x, y, z rotation = rig euler x, -z, y)
        for arm, sgn in ((self.arm_r, 1.0), (self.arm_l, -1.0)):
            self._set_rest(arm, _ROT, 0, ARMS_OUT)
            self._set_rest(arm, _ROT, 1, 0.0)
            self._set_rest(arm, _ROT, 2, sgn * ARM_TOE)
        self._bake_arms()
        for arm, sgn in ((self.arm_r, 1.0), (self.arm_l, -1.0)):               # AnimationUtils.bobModelPart
            m = ch._ensure(arm, _ROT, 1).modifiers.new("FNGENERATOR")
            m.function_type, m.use_additive = "COS", True
            m.amplitude, m.value_offset = sgn * BOB_AMOUNT, sgn * BOB_AMOUNT
            m.phase_multiplier, m.phase_offset = BOB_Z_RATE / TICK, BOB_Z_RATE * self._age0
            m = ch._ensure(arm, _ROT, 0).modifiers.new("FNGENERATOR")
            m.function_type, m.use_additive = "SIN", True
            m.amplitude, m.value_offset = sgn * BOB_AMOUNT, 0.0
            m.phase_multiplier, m.phase_offset = BOB_X_RATE / TICK, BOB_X_RATE * self._age0
        _state(self)

    def __repr__(self):
        what = "zombie villager %s" % self.profession if self.kind == "zombie_villager" else self.variant
        return "<Undead %s %s%s>" % (self.name, what, " baby" if self.baby else "")

    # ------------------------------------------------------------------ arms
    def swing_value(self, frame):
        """The attack animation value (0..1) at `frame`."""
        shown = _swing_shown()
        for start in sorted(self._attacks, reverse=True):
            t = (frame - start) / TICK
            if 0.0 <= t < len(shown):
                a, b = shown[int(t)]
                return a + (b - a) * (t - int(t))
            if t >= 0.0:
                break
        return 0.0

    def arm_base(self, frame):
        """The arms' pitch without swing and bob at `frame`: ARMS_OUT, or ARMS_RAISED while aggro() is on."""
        value = ARMS_OUT
        for start, on, ease in sorted(self._aggro):
            target = ARMS_RAISED if on else ARMS_OUT
            if ease <= 0:
                if frame >= start - ch.CUT_LEAD - 1e-9:
                    value = target
            elif frame >= start + ease:
                value = target
            elif frame > start:
                value += (target - value) * mobs._ease((frame - start) / float(ease))
        return value

    def arm_bob(self, frame):
        """(x, z) of AnimationUtils.bobModelPart for the right arm at `frame` (the left arm has the opposite)."""
        age = frame / TICK + self._age0
        return (math.sin(age * BOB_X_RATE) * BOB_AMOUNT, math.cos(age * BOB_Z_RATE) * BOB_AMOUNT + BOB_AMOUNT)

    def arm_pose(self, frame):
        """The right arm's model rotation (xRot, yRot, zRot) at `frame`, bob included (the left arm: x - 2 * bob x,
        -yRot, -zRot)."""
        a = self.swing_value(frame)
        f7 = math.sin(a * math.pi)
        f8 = math.sin((1.0 - (1.0 - a) ** 2) * math.pi)
        bx, bz = self.arm_bob(frame)
        return (self.arm_base(frame) + f7 * SWING_DOWN - f8 * SWING_BACK + bx, -(ARM_TOE - f7 * SWING_TOE), bz)

    def _bake_arms(self):
        """Rewrite the arms' keys from the aggro and attack events (the bob is an F-curve modifier on top)."""
        times = set()
        for start, _on, ease in self._aggro:
            if ease <= 0:
                times |= {start - ch.CUT_LEAD - 0.03, start - ch.CUT_LEAD}
            else:
                times |= {float(start + i) for i in range(int(ease) + 1)} | {float(start + ease)}
        shown = _swing_shown()
        for start in self._attacks:
            times |= {start + j * TICK / 4.0 for j in range(4 * len(shown) + 1)}
        times.add(min(times | {1.0}) - 1.0)
        frames = []
        for t in sorted(times):
            if not frames or t - frames[-1] > 0.011:
                frames.append(t)
        pitch, toe = [], []
        for t in frames:
            a = self.swing_value(t)
            f7 = math.sin(a * math.pi)
            f8 = math.sin((1.0 - (1.0 - a) ** 2) * math.pi)
            pitch.append(self.arm_base(t) + f7 * SWING_DOWN - f8 * SWING_BACK)
            toe.append(ARM_TOE - f7 * SWING_TOE)
        for arm, sgn in ((self.arm_r, 1.0), (self.arm_l, -1.0)):
            fx._write(arm, _ROT, 0, frames, pitch, "LINEAR")
            fx._write(arm, _ROT, 1, frames[:1], [0.0], "LINEAR")
            fx._write(arm, _ROT, 2, frames, [sgn * v for v in toe], "LINEAR")

    def aggro(self, frame, on=True, ease=3):
        """Raise the arms to the game's "aggressive" -120 degrees (on=False: back to -80) over `ease` frames; the
        game snaps (ease=0). ZombieAttackGoal: up once it has had a target for 5 ticks, down for the 10 ticks after
        every blow. Returns the end frame."""
        frame, ease = int(round(frame)), max(0, int(ease))
        self._aggro = [e for e in self._aggro if e[0] != frame] + [(frame, bool(on), ease)]
        self._bake_arms()
        return frame + ease

    def raise_arm(self, frame, angle=None, ease=3, side="r"):
        """Zombie arms have two poses: this is aggro(frame, True, ease)."""
        return self.aggro(frame, True, ease)

    def attack(self, frame, target=None, **hurt_kw):
        """The melee swing started on `frame` (HumanoidModel.setupAttackAnimation + animateZombieArms: both arms
        chop down and back in 6 ticks, the body twists). target = a Character: it is hurt on this very frame, as in
        the game (hurt_kw: knockback=, max_back=, flash=). Returns the frame the swing is over."""
        f0 = int(round(frame))
        self._attacks = sorted(set(self._attacks) | {f0})
        self._bake_arms()
        shown = _swing_shown()
        twist = []
        for j in range(1, 4 * len(shown)):
            t = j / 4.0
            a, b = shown[int(t)]
            v = a + (b - a) * (t - int(t))
            twist.append((t * TICK, -math.sin(math.sqrt(max(v, 0.0)) * 2.0 * math.pi) * BODY_TWIST if 0.0 < v < 1.0 else 0.0))
        end = len(shown) * TICK
        ch._offsets(self.body, _ROT, 2, f0, twist + [(end, 0.0)], interp="LINEAR")
        ch._offsets(self.head, _ROT, 2, f0, [(t, -v) for t, v in twist] + [(end, 0.0)], interp="LINEAR")
        if target is not None:
            hurt(target, f0, attacker=self, **hurt_kw)
        return int(math.ceil(f0 + end))

    def swing_arm(self, frame):
        """The same as attack(frame): a zombie has no other arm gesture."""
        return self.attack(frame)

    # ------------------------------------------------------------------ placement
    def place(self, frame, pos, yaw=0.0, keep_pose=False):
        """Hard-set position and yaw from `frame` on: upright, neutral legs, arms out (use at shot cuts)."""
        super().place(frame, pos, yaw, keep_pose=keep_pose)
        _on_place(self, frame)                                          # (after a death: there again, upright)
        self._bake_arms()
        st = self.__dict__.get(_STATE)
        if st is not None and st["depth"] == 0:
            _restore(self)
            _apply(self)

    def _aim(self, target, frame):
        """Head (yaw, pitch-up) toward a target, clamped to the game's limits for mobs (75 / 40 degrees)."""
        if target is None:
            return 0.0, 0.0
        d = self._point(target, frame) - self.eye_point(frame)
        yaw = ch._clamp(ch._wrap(math.atan2(d.x, -d.y) - self.yaw_at(frame)), -HEAD_YAW_MAX, HEAD_YAW_MAX)
        pitch = ch._clamp(math.atan2(d.z, math.hypot(d.x, d.y)), -HEAD_PITCH_MAX, HEAD_PITCH_MAX)
        return yaw, pitch

    # ------------------------------------------------------------------ locomotion
    def walk(self, frame, points, speed=None, run=False, from_current=False, gait="planted"):
        """Travel along the polyline `points` at the game's zombie speed (2.33 blocks/s, babies 5.24); returns the end frame.

        gait "planted": the game's swing for the speed, the cycle shortened so that the sole on the ground does not
        slide, hips sinking with the spread of the legs. gait "vanilla": exactly the game's leg wave (the feet
        slide, no bob). The arms stay out. run= is accepted and ignored: a zombie has one speed."""
        if gait not in ("planted", "vanilla"):
            raise ValueError("gait %r: use 'planted' or 'vanilla'" % (gait,))
        speed = self.walk_speed if speed is None else float(speed)
        f0 = int(round(frame))
        f1 = ch.Character.walk(self, f0, points, speed=speed, run=False, from_current=from_current)
        n = f1 - f0
        if n <= 0:
            return f1
        # Character.walk travels linearly between the vertices of the polyline: the distance covered at any time
        fcx = ch._find(self.root, _LOC, 0)
        stamps = sorted({float(f0), float(f1)} | {float(kp.co.x) for kp in fcx.keyframe_points if f0 < kp.co.x < f1})
        spots = [self.pos_at(t) for t in stamps]
        acc = [0.0]
        for a, b in zip(spots, spots[1:]):
            acc.append(acc[-1] + (b - a).length)
        total = acc[-1]
        if total < 1e-6:
            return f1

        def dist(t):
            """Blocks covered t frames into the walk."""
            return float(np.interp(f0 + t, stamps, acc))

        leg = self.leg_len
        per_tick = total / n * TICK                                     # blocks per game tick, as really keyed
        anim = min(ANIM_PER_BLOCK * per_tick, 1.0)                      # LivingEntity.updateWalkAnimation
        scale = BABY_ANIM_SCALE if self.baby else 1.0
        sign = 1.0 if self._foot > 0 else -1.0
        rest_z = self._rest(self.hips, _LOC, 2)
        ch._segment(self.body, _ROT, 1, [(f0, None), (f1, 0.0)])        # (no waddle: a zombie does not sway)
        if gait == "vanilla":
            rate = anim * scale / per_tick * LEG_RATE                   # leg phase in radians per block
            amp = LEG_SWING * anim
            cycle = 2.0 * math.pi / rate

            def env(t):
                """The 0.4 lerp of the walk-animation speed at the start, mirrored at the end."""
                return max(0.0, min(1.0 - (1.0 - ANIM_LERP) ** (t / TICK), 1.0 - (1.0 - ANIM_LERP) ** ((n - t) / TICK)))

            def angle(t):
                return sign * amp * env(t) * math.sin(rate * dist(t))

            step = min(1.0, cycle / (total / n) / 12.0)
            times = [i * step for i in range(int(math.floor(n / step)) + 1)] + [float(n)]
            mobs._sample(self.leg_r, _ROT, 0, f0, times, lambda t: -angle(t))
            mobs._sample(self.leg_l, _ROT, 0, f0, times, angle)
            ch._segment(self.hips, _LOC, 2, [(f0, None), (f1, rest_z)])
            swing = amp
        else:
            want = ch._clamp(LEG_SWING * anim, 0.3, 1.0)
            steps = max(1, int(round(total / (2.0 * leg * math.sin(want)))))
            half = total / steps                                        # one step: the stance sole from front to back
            swing = math.asin(min(half / (2.0 * leg), math.sin(1.2)))
            cycle = 2.0 * half

            def angle(t):
                """The stance sole stays put: leg * sin(angle) is linear in the distance covered."""
                tri = (2.0 / math.pi) * math.asin(math.sin(math.pi * dist(t) / half))
                return sign * math.asin(ch._clamp(tri * math.sin(swing), -1.0, 1.0))

            step = min(1.0, half / (total / n) / 6.0)
            times = {i * step for i in range(int(math.floor(n / step)) + 1)} | {float(n)}
            times |= {float(np.interp((m + 0.5) * half, acc, stamps)) - f0 for m in range(steps)}   # the turning points
            times = mobs._dedupe(times)
            mobs._sample(self.leg_r, _ROT, 0, f0, times, lambda t: -angle(t))
            mobs._sample(self.leg_l, _ROT, 0, f0, times, angle)
            mobs._sample(self.hips, _LOC, 2, f0, times, lambda t: rest_z - leg * (1.0 - math.cos(angle(t))), rest=rest_z)
            if steps % 2:
                self._foot = -self._foot
        self.last_walk = dict(gait=gait, frames=(f0, f1), blocks=total, speed=total / n * FPS, swing=swing,
                              cycle_blocks=cycle, cycle_frames=cycle / (total / n))
        return f1

    # ------------------------------------------------------------------ idle + gestures
    def idle(self, frame_start, frame_end, seed=0):
        """The head turns to look around between frame_start and frame_end (RandomLookAroundGoal: a new direction
        now and then, held for 1-2 s; seeded). The arms' bob is always on and needs no call."""
        f0, f1 = int(frame_start), int(frame_end)
        if f1 - f0 < 20:
            return
        r = pix.rng(5381 * (int(seed) + 1) + 17)
        for index, spread, lo, hi in ((2, 1.0, -HEAD_YAW_MAX, HEAD_YAW_MAX), (0, 0.10, -HEAD_PITCH_MAX, HEAD_PITCH_MAX)):
            base = ch._val(self.head, _ROT, index, f0)
            keys, cur = [(f0, None)], base
            back = min(12, (f1 - f0) // 3)
            t = f0 + int(r.integers(6, 30))
            while True:
                dur = int(r.integers(7, 13))
                if t + dur > f1 - back - 2:
                    break
                tgt = base if r.random() < 0.3 else ch._clamp(base + r.uniform(-spread, spread), lo, hi)
                keys += [(t, cur), (t + dur, tgt)]
                cur = tgt
                t += dur + int(r.integers(24, 48))                      # lookTime = 20 + nextInt(20) ticks
            keys += [(f1 - back, cur), (f1, base)]
            ch._segment(self.head, _ROT, index, keys)

    def flinch(self, frame):
        """Startled hop then duck and recover (12 frames); the arms keep their pose. Returns the end frame."""
        k = self.stride
        ch._offsets(self.hips, _LOC, 2, frame, [(2, 0.11 * k), (5, -0.04 * k), (12, 0.0)])
        ch._offsets(self.body, _ROT, 0, frame, [(2, -0.10), (5, 0.13), (12, 0.0)])
        ch._offsets(self.head, _ROT, 0, frame, [(2, -0.26), (5, 0.20), (12, 0.0)])
        ch._offsets(self.leg_l, _ROT, 0, frame, [(2, 0.16), (5, -0.10), (12, 0.0)])
        ch._offsets(self.leg_r, _ROT, 0, frame, [(2, 0.16), (5, 0.12), (12, 0.0)])
        return frame + 12

    def sit(self, frame, on=True):
        """The legs of a passenger (HumanoidModel.setupAnim, isPassenger: in a boat or a minecart) from `frame`
        on: both -81 degrees forward and splayed; on=False: standing again. Lower the zombie yourself."""
        x, y, z = SIT_LEG
        for leg, sgn in ((self.leg_r, 1.0), (self.leg_l, -1.0)):
            for index, value in ((0, x), (1, sgn * z), (2, -sgn * y)):
                ch._cut(leg, _ROT, index, frame, value if on else 0.0)

    def hold(self, obj, offset=None, rotation=None):
        """An item sprite (engine.props.make_item) in the right hand, placed as ItemInHandLayer does; hold(None)."""
        if self.held is not None and self.held is not obj:
            self.held.parent = None
            self.held = None
        if obj is None:
            return None
        obj.parent = self.arm_r
        obj.matrix_parent_inverse = Matrix.Identity(4)
        obj.matrix_basis = ch._held_matrix("hand", self.model_scale * (0.5 if self.baby else 1.0))
        if offset is not None:
            obj.location = offset
        if rotation is not None:
            obj.rotation_euler = rotation
        self.held = obj
        return obj

    def hurt(self, frame, attacker=None, knockback=True, max_back=None, flash=True):
        """The game's hurt on `frame` (see undead.hurt): red for 12 frames, knock-back hop, flailing legs."""
        return hurt(self, frame, attacker=attacker, knockback=knockback, max_back=max_back, flash=flash)

    def die(self, frame, camera=None, **kw):
        """The game's death (see undead.die): tips over to 90 degrees, gone with a poof on frame + 24 (returned)."""
        return die(self, frame, camera=camera, **kw)


def make_zombie(name, baby=False, variant="zombie", collection=None):
    """Build the vanilla zombie (2.0 tall, feet at the origin, facing -Y, arms out); baby=True the baby model;
    variant='husk' the husk (its texture, 1.0625 scale)."""
    key, sheet = zombie_sheet(baby, variant)
    spec = _baby_zombie_spec() if baby else _zombie_spec(HUSK_SCALE if variant == "husk" else 1.0)
    parts = ch._build_rig(name, spec, sheet, ch._sheet_material(key, sheet), ch._collection(collection))
    return Undead(name, parts, spec, kind="zombie", baby=baby, variant=variant)


def make_zombie_villager(name, profession="none", biome="plains", baby=False, level=None, collection=None):
    """Build a zombie villager wearing the game's zombie-villager textures for `profession` and `biome` (level
    1..5 = badge; None = 1). baby=True the baby model (babies show no profession)."""
    profession = ch.PROFESSION_ALIASES.get(profession, profession)
    if profession not in ch.villager_professions():
        raise ValueError("unknown profession %r (use one of %s)" % (profession, ", ".join(ch.villager_professions())))
    key, sheet = zombie_villager_sheet(profession, biome, level, baby)
    spec = _baby_zombie_villager_spec() if baby else _zombie_villager_spec()
    parts = ch._build_rig(name, spec, sheet, ch._sheet_material(key, sheet), ch._collection(collection),
                          ch._sheet_material_two_sided(key, sheet))
    return Undead(name, parts, spec, kind="zombie_villager", profession=profession, baby=baby,
                  variant="zombie_villager", biome=biome)


def add_zombie(st, name="zombie", **kw):
    """A zombie registered with a films.lookdev.Stage (Stage.actor builds villagers and Steve only)."""
    z = st.cast.get(name)
    if z is None:
        z = st.cast[name] = make_zombie(name, **kw)
    return z


def add_zombie_villager(st, name="zombie_villager", profession="none", **kw):
    """A zombie villager registered with a films.lookdev.Stage."""
    z = st.cast.get(name)
    if z is None:
        z = st.cast[name] = make_zombie_villager(name, profession, **kw)
    return z


def flee(villager, frame, threat, distance=6.0, speed=VILLAGER_PANIC_SPEED):
    """A villager runs `distance` blocks straight away from `threat` (a Character or a point) at the game's panic
    speed (6.2 blocks/s; VillagerGoalPackages.getPanicPackage: SetWalkTargetAwayFrom, 6 blocks). Returns the end frame."""
    here = villager.pos_at(frame)
    away = _away(villager, frame, threat)
    return villager.walk(frame, [here, here + away * float(distance)], speed=speed, run=True)


# ----------------------------------------------------------------------------------------------------
# infection
# ----------------------------------------------------------------------------------------------------
def infect(villager, zombie_villager, frame, attacker=None, knockback=True, max_back=None):
    """The villager dies to a zombie on `frame` and is replaced on the spot by `zombie_villager` (same place, same
    yaw; no flash, no tipping body, no particles: Zombie.killedEntity -> Mob.convertTo). The zombie villager takes
    the killing blow's knock-back hop away from `attacker` (it inherits the velocity). Returns the end frame."""
    f0 = int(round(frame))
    pos, yaw = villager.pos_at(f0), villager.yaw_at(f0)
    vanish(villager, f0, why="replaced")
    st = _state(zombie_villager)
    st["presence"] = [e for e in st["presence"] if e[0] is not None and e[0] > f0]
    zombie_villager.place(f0, pos, yaw)
    _presence(zombie_villager, None, False, "unborn")
    _presence(zombie_villager, f0, True, "born")
    end = f0
    strength = _strength(knockback, zombie_villager) if (attacker is not None or knockback is not True) else 0.0
    if strength > 0.0:
        end = _knock(zombie_villager, f0, attacker, strength, max_back, 0.0)
    return end


# ----------------------------------------------------------------------------------------------------
# potion effects: swirls, the thrown splash potion
# ----------------------------------------------------------------------------------------------------
def _colour(effect):
    if isinstance(effect, str):
        if effect not in EFFECT_COLOURS:
            raise ValueError("effect %r: use one of %s or an (r, g, b)" % (effect, ", ".join(sorted(EFFECT_COLOURS))))
        return EFFECT_COLOURS[effect]
    return tuple(int(c) for c in effect[:3])


def _spell_velocity(rng, up):
    """SpellParticle's constructor: Particle(x, y, z, 0.5 - random, ya, 0.5 - random), then yd *= 0.2."""
    v = fx._base_velocity(rng, (0.5 - rng.random(), 0.5 - rng.random(), up))
    v[2] *= 0.2
    return v


def effect_swirls(character, frame_start, frame_end, effect="strength", camera=None, seed=0, glow=None, size=None,
                  collection=None):
    """The swirls of a mob with a potion effect between frame_start and frame_end (LivingEntity.tickEffects): on
    one tick in four ONE 'entity_effect' particle (SpellParticle: sprites effect_7 .. effect_0 by age, quads
    0.15-0.30 wide, 8-40 ticks) somewhere in its hit box, drifting up, in the effect's colour.
    effect = 'weakness' | 'strength' | 'nausea' | (r, g, b). Returns an engine.fx Burst."""
    tint = _colour(effect)
    f0, f1 = float(frame_start), float(frame_end)
    burst = fx.Burst("entity_effect", int(math.ceil(f0 - 1e-6)))
    cams = fx._camera_arg(camera)
    col = fx._collection(collection)
    glow = fx.SPRITE_GLOW if glow is None else float(glow)
    w, h = size if size is not None else body_box(character)
    key = [int(seed) & 0x7FFFFFFF, 7307, int(round(f0 * 4.0)) & 0x7FFFFFFF]
    dice = np.random.default_rng(key)
    tick = -1
    while True:
        tick += 1
        f = f0 + tick * TICK
        if f >= f1 - 1e-6:
            break
        if int(dice.integers(0, EFFECT_CHANCE)) != 0:
            continue
        rng = np.random.default_rng(key + [tick])
        feet = fx._point(character, f)
        p = np.array([feet.x + w * (2.0 * rng.random() - 1.0) * 0.5,     # getRandomX(0.5)
                      feet.y + w * (2.0 * rng.random() - 1.0) * 0.5,
                      feet.z + h * rng.random()])                        # getRandomY()
        v = _spell_velocity(rng, 1.0)                                    # addParticle(..., 1.0, 1.0, 1.0)
        quad = 0.1 * (rng.random() * 0.5 + 0.5) * 2.0 * 0.75
        life = int(8.0 / (rng.random() * 0.8 + 0.2))
        path = fx._simulate(p, v, life, -0.1 * 0.04, 0.96, None, 0.2, rng)
        _sprite_particle(burst, "undead_swirl_%d_%d" % (int(f0), tick), EFFECT_SPRITES, tint, glow, path, f, quad,
                         cams, col)
    return burst


def _sprite_object(name, arr, material, collection):
    """A flat item sprite extruded one pixel thick from an HxWx4 array (as engine.mcassets.item_object builds
    them): 16 px = 1 unit, origin at the sprite centre, sprite in the local XZ plane, front -Y."""
    h, w = arr.shape[:2]
    solid = arr[..., 3] >= 128
    mb = mc.MeshBuilder()
    s = 1.0 / 16.0
    t = s / 2.0
    su, sv = 16.0 / w, 16.0 / h
    e = 0.02
    for r in range(h):
        for c in range(w):
            if not solid[r, c]:
                continue
            x0, x1 = (c - w / 2.0) * s, (c + 1 - w / 2.0) * s
            z1, z0 = (h / 2.0 - r) * s, (h / 2.0 - r - 1) * s
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
    ob = bpy.data.objects.new(name, me)
    collection.objects.link(ob)
    return ob


def make_splash_potion(effect="weakness", collection=None, name=None):
    """The splash-potion item sprite as the game colours it (models/item/splash_potion.json: layer0
    item/potion_overlay tinted with the potion's colour, layer1 item/splash_potion over it); as engine.props.make_item."""
    tint = _colour(effect)
    arr = mc.composed_array("item/potion_overlay", tint=tint, overlay="item/splash_potion")
    mat = mc.material("item/potion_overlay", tint=tint, overlay="item/splash_potion", alpha="OPAQUE")
    return _sprite_object(name or "splash_potion_%02x%02x%02x" % tint, arr, mat, fx._collection(collection))


def potion_track(start, target, speed=POTION_SPEED, box=None, max_ticks=200):
    """The flight of a thrown potion from `start` to `target` (ThrowableProjectile.tick: v.y -= 0.05, v *= 0.99,
    pos += v): the lower of the two arcs of that speed that pass through `target`. box = (lo, hi) corners of a
    hit box it breaks on first. Returns (points after 0..n ticks, the last one = where it breaks) or None when the
    speed does not reach."""
    s, t = Vector(start), Vector(target)
    flat = Vector((t.x - s.x, t.y - s.y, 0.0))
    reach = flat.length
    if reach < 1e-6:
        return [s.copy(), t.copy()]
    ahead = flat / reach

    def fly(pitch):
        """Points per tick, and the height error where the arc crosses the target's distance (None: it never does)."""
        vh, vz = speed * math.cos(pitch), speed * math.sin(pitch)
        d = z = 0.0
        pts = [(0.0, 0.0)]
        for _ in range(max_ticks):
            vz -= POTION_GRAVITY
            vh *= POTION_DRAG
            vz *= POTION_DRAG
            d2, z2 = d + vh, z + vz
            if d2 >= reach:
                u = (reach - d) / max(d2 - d, 1e-12)
                pts.append((reach, z + (z2 - z) * u))
                return pts, z + (z2 - z) * u - (t.z - s.z)
            pts.append((d2, z2))
            d, z = d2, z2
            if z < (t.z - s.z) - 30.0:
                break
        return pts, None

    prev, best = None, None
    for i in range(-178, 179):                                           # half-degree steps from straight down up
        pitch = math.radians(i * 0.5)
        _pts, err = fly(pitch)
        if err is not None and prev is not None and prev[1] is not None and prev[1] < 0.0 <= err:
            lo, hi = prev[0], pitch
            for _ in range(40):
                mid = 0.5 * (lo + hi)
                e = fly(mid)[1]
                if e is None or e < 0.0:
                    lo = mid
                else:
                    hi = mid
            best = fly(hi)[0]
            break
        prev = (pitch, err)
    if best is None:
        return None
    pts = [s + ahead * d + Vector((0.0, 0.0, z)) for d, z in best]
    if box is not None:                                                  # it breaks where it enters the hit box
        lo, hi = Vector(box[0]), Vector(box[1])
        for k in range(len(pts) - 1):
            a, b = pts[k], pts[k + 1]
            t0, t1 = 0.0, 1.0
            for i in range(3):
                d = b[i] - a[i]
                if abs(d) < 1e-12:
                    if a[i] < lo[i] or a[i] > hi[i]:
                        t0, t1 = 1.0, 0.0
                        break
                    continue
                u0, u1 = (lo[i] - a[i]) / d, (hi[i] - a[i]) / d
                t0, t1 = max(t0, min(u0, u1)), min(t1, max(u0, u1))
            if t0 <= t1:
                return pts[:k + 1] + [a.lerp(b, t0)]
    return pts


class PotionThrow(int):
    """The impact frame of a thrown potion, with .bottle (Object), .burst (fx.Burst), .hit (Vector), .speed
    (blocks per tick) and .frames (throw frame, impact frame)."""


def splash(point, frame, camera=None, effect="weakness", village=None, seed=0, count=SPLASH_COUNT, glow=None,
           collection=None):
    """A splash potion breaks at `point` on `frame` (level event 2002, LevelEventHandler.potionSplashParticles),
    centred as the game centres it on the bottom of the block the bottle was in: 8 shards of the splash-potion
    sprite (BreakingItemParticle) and `count` (the game: 100) 'effect' swirls in the potion's colour x 0.75-1.0,
    starting within 0.4 block, flying out along the ground at up to 4 times their speed and rising.
    Returns an engine.fx Burst."""
    frame = int(frame)
    tint = _colour(effect)
    p0 = fx._point(point, frame)
    centre = Vector((math.floor(p0.x) + 0.5, math.floor(p0.y) + 0.5, math.floor(p0.z + 1e-6)))    # Vec3.atBottomCenterOf
    burst = fx.Burst("potion_splash", frame)
    cams = fx._camera_arg(camera)
    col = fx._collection(collection)
    solids = fx._Solids(village) if village is not None else mobs._Floor(centre.z)
    glow = fx.SPRITE_GLOW if glow is None else float(glow)
    rng = fx._rng(seed, frame, 2002, int(centre.x), int(centre.y))
    for i in range(SPLASH_SHARDS):                                       # ItemParticleOption(ITEM, SPLASH_POTION)
        va = (rng.normal() * 0.15, rng.normal() * 0.15, rng.random() * 0.2)
        v = fx._base_velocity(rng, (0.0, 0.0, 0.0)) * 0.1 + np.array(va)
        life = int(4.0 / (rng.random() * 0.9 + 0.1))
        quad = 0.1 * (rng.random() * 0.5 + 0.5) * 2.0 / 2.0
        uo, vo = rng.random() * 3.0, rng.random() * 3.0
        layer = ("item/splash_potion", "item/potion_overlay")[int(rng.integers(0, 2))]
        mat = fx._particle_material(layer, glow=glow)
        mesh = fx._quad_mesh("undead_shard_%d_%d" % (frame, i), ((uo + 1.0) / 4.0, uo / 4.0, vo / 4.0, (vo + 1.0) / 4.0), mat)
        path = fx._simulate(tuple(centre), v, life, 0.04, 0.98, solids, 0.2, rng)
        fx._particle_object(burst, "undead_shard_%d_%d" % (frame, i), mesh, path, float(frame), quad, cams, col)
    for i in range(int(count)):
        power = rng.random() * 4.0
        angle = rng.random() * math.pi * 2.0
        xa, za = math.cos(angle) * power, math.sin(angle) * power
        ya = 0.01 + rng.random() * 0.5
        shade = 0.75 + rng.random() * 0.25
        shade = 0.78125 + 0.0625 * min(3, int((shade - 0.75) / 0.0625))  # four shades: a material each, not a hundred
        p = np.array([centre.x + xa * 0.1, centre.y + za * 0.1, centre.z + 0.3])
        v = _spell_velocity(rng, ya)
        v[0] *= power                                                    # Particle.setPower
        v[1] *= power
        v[2] = (v[2] - 0.1) * power + 0.1
        quad = 0.1 * (rng.random() * 0.5 + 0.5) * 2.0 * 0.75
        life = int(8.0 / (rng.random() * 0.8 + 0.2))
        path = fx._simulate(p, v, life, -0.1 * 0.04, 0.96, None, 0.2, rng)
        _sprite_particle(burst, "undead_splash_%d_%d" % (frame, i), EFFECT_SPRITES,
                         tuple(int(round(c * shade)) for c in tint), glow, path, float(frame), quad, cams, col)
    return burst


def throw_potion(start, target, frame, camera=None, effect="weakness", village=None, seed=0, count=SPLASH_COUNT,
                 glow=None, speed=None, collection=None):
    """Throw a splash potion on `frame` from `start` to `target`; returns the impact frame (see the module docstring).

    start = a point, or the player Character who throws (released 0.1 under his eyes; his arm swings); target = a
    point, or a Character (aimed at its chest, breaking on its hit box). speed = blocks per tick (None: the game's
    0.5, raised step by step if that does not reach)."""
    f0 = int(round(frame))
    cams = fx._camera_arg(camera)
    col = fx._collection(collection)
    if isinstance(start, ch.Character):
        feet = start.pos_at(f0)
        eye = PLAYER_EYE if start.kind == "player" else start.eye_height
        s = Vector((feet.x, feet.y, feet.z + eye - POTION_EYE_DROP))
        if start.arm_r is not None and not isinstance(start, Undead):
            fx.arm_swings(start, [f0])
    else:
        s = ch._vec3(start)
    box = None
    if isinstance(target, ch.Character):
        feet = target.pos_at(f0)
        w, h = body_box(target)
        t = Vector((feet.x, feet.y, feet.z + 0.6 * h))
        m = POTION_MARGIN
        box = ((feet.x - w / 2 - m, feet.y - w / 2 - m, feet.z - m), (feet.x + w / 2 + m, feet.y + w / 2 + m, feet.z + h + m))
    else:
        t = ch._vec3(target)
    used = POTION_SPEED if speed is None else float(speed)
    pts = potion_track(s, t, used, box)
    while pts is None and speed is None and used < 4.0:
        used *= 1.1
        pts = potion_track(s, t, used, box)
    if used != POTION_SPEED and speed is None:
        print("[undead] throw_potion at frame %d: the game's 0.5 block per tick does not reach %.1f blocks; thrown at %.2f"
              % (f0, math.hypot(t.x - s.x, t.y - s.y), used))
    if pts is None:
        raise ValueError("throw_potion: %.2f blocks per tick does not reach %s from %s" % (used, tuple(t), tuple(s)))
    n = len(pts) - 1
    impact = int(math.ceil(f0 + n * TICK - 1e-6))
    # ThrownItemRenderer: the item at its 'ground' display transform (half size, centre 2 px up), turned to the camera
    carrier = bpy.data.objects.new("undead_potion_%d" % f0, None)
    carrier.empty_display_size = 0.1
    col.objects.link(carrier)
    times = [f0 + k * TICK for k in range(n + 1)]
    for i in range(3):
        fx._write(carrier, _LOC, i, times, [p[i] for p in pts], "LINEAR")
    carrier.location = pts[0]
    fx._face_camera(carrier, cams)
    bottle = make_splash_potion(effect, collection=col, name="undead_potion_%d_sprite" % f0)
    bottle.parent = carrier
    bottle.matrix_parent_inverse = Matrix.Identity(4)
    bottle.location = (0.0, ITEM_GROUND[0], 0.0)
    bottle.rotation_euler = (math.radians(-90.0), 0.0, 0.0)             # sprite up = camera up, its front to the lens
    bottle.scale = (ITEM_GROUND[1],) * 3
    for path in ("hide_render", "hide_viewport"):
        fx._write(bottle, path, 0, [f0 - 1, f0, impact], [1.0, 0.0, 1.0], "CONSTANT")
    bottle.hide_render = bottle.hide_viewport = True
    bottle.visible_shadow = False
    burst = splash(pts[-1], impact, camera=camera, effect=effect, village=village, seed=seed, count=count, glow=glow,
                   collection=col)
    out = PotionThrow(impact)
    out.bottle, out.carrier, out.burst, out.hit, out.speed, out.frames, out.points = bottle, carrier, burst, pts[-1], used, (f0, impact), pts
    return out


# ----------------------------------------------------------------------------------------------------
# the cure
# ----------------------------------------------------------------------------------------------------
def shake(zombie_villager, frame_start, frame_end, amount=1.0):
    """The shaking of a converting zombie villager between frame_start and frame_end
    (LivingEntityRenderer.setupRotations, isShaking: body yaw += cos(floor(age) * 3.25) * pi * 0.4 degrees, a new
    value every game tick: +-1.26 degrees, swelling and fading over 29 ticks). amount scales it."""
    c = zombie_villager
    f0, f1 = float(frame_start), float(frame_end)
    age = int(round(f0 / TICK + getattr(c, "_age0", 0.0)))
    keys = [(f0, None, "CONSTANT")]
    k = 0
    while f0 + k * TICK < f1 - 1e-6:
        keys.append((f0 + k * TICK + (0.02 if k == 0 else 0.0),
                     math.radians(math.cos((age + k) * SHAKE_RATE) * SHAKE_DEGREES) * float(amount), "CONSTANT"))
        k += 1
    keys.append((f1, 0.0))
    ch._segment(c.hips, _ROT, 2, keys, "CONSTANT")
    return int(math.ceil(f1))


def _consume(obj, frame):
    """A held item is used up on `frame` (its scale steps to nothing: Character.show cannot bring it back)."""
    for i in range(3):
        fx._step(obj, "scale", int(frame), 0.0005, index=i)


def cure(zombie_villager, villager, frame_start, frame_end, camera=None, player=None, weakness_from=None,
         nausea=int(NAUSEA_TICKS * TICK), seed=0, glow=None, shake=1.0):
    """The cure (see the module docstring): golden apple on frame_start (player swings, the apple is consumed),
    the zombie villager shakes and gives off Strength swirls until frame_end, where the villager takes its place
    and gives off Nausea swirls for `nausea` frames. Returns {'strength', 'nausea', 'weakness': Bursts,
    'frame_end', 'nausea_end'}."""
    zv, f0, f1 = zombie_villager, int(round(frame_start)), int(round(frame_end))
    if f1 <= f0:
        raise ValueError("cure: frame_end must come after frame_start")
    out = {"frame_start": f0, "frame_end": f1, "nausea_end": f1 + int(nausea), "weakness": None}
    if player is not None:
        if getattr(player, "arm_r", None) is not None and not isinstance(player, Undead):
            fx.arm_swings(player, [f0])                                  # InteractionResult.SUCCESS_SERVER: the hand swings
        if player.held is not None:
            _consume(player.held, f0)
    if weakness_from is not None and weakness_from < f0:
        out["weakness"] = effect_swirls(zv, weakness_from, f0, "weakness", camera=camera, seed=seed + 1, glow=glow)
    if shake:
        globals()["shake"](zv, f0, f1, amount=float(shake))
    out["strength"] = effect_swirls(zv, f0, f1, "strength", camera=camera, seed=seed, glow=glow)
    pos, yaw = zv.pos_at(f1), zv.yaw_at(f1)
    vanish(zv, f1, why="replaced")
    known = bool(villager.__dict__.get(_STATE, {}).get("presence"))
    villager.place(f1, pos, yaw)
    if not known:
        _presence(villager, None, False, "unborn")
    _presence(villager, f1, True, "cured")
    out["nausea"] = effect_swirls(villager, f1, f1 + int(nausea), "nausea", camera=camera, seed=seed + 2, glow=glow) \
        if nausea > 0 else None
    return out


# ----------------------------------------------------------------------------------------------------
# self-test
# ----------------------------------------------------------------------------------------------------
def _evaluate(scene, frame):
    whole = int(math.floor(frame))
    scene.frame_set(whole, subframe=float(frame) - whole)
    bpy.context.view_layer.update()


def _rendered(ob):
    return not ob.hide_render


def _check():
    """Numbers only: sizes, arms, gait, hurt, death, infection, cure, potion."""
    from . import quick

    scene = quick.reset()
    quick.setup(scene)
    cam = quick.camera(scene, (0.0, -8.0, 1.5), (0.0, 0.0, 1.0))
    ok = []

    def expect(label, cond, detail=""):
        ok.append(bool(cond))
        print("%s %-58s %s" % ("ok  " if cond else "FAIL", label, detail))

    def near(a, b, tol):
        return abs(a - b) <= tol

    # ---- sizes and speeds
    z = make_zombie("z")
    b = make_zombie("zb", baby=True)
    zv = make_zombie_villager("zv", "farmer")
    bv = make_zombie_villager("zvb", baby=True)
    hk = make_zombie("husk", variant="husk")
    expect("zombie 2.0 tall, eyes 1.74", near(z.height, 2.0, 1e-6) and near(z.eye_height, 1.74, 1e-6), "%.4f %.4f" % (z.height, z.eye_height))
    expect("baby zombie 0.9375 tall, eyes 0.775", near(b.height, 0.9375, 1e-6) and near(b.eye_height, 0.775, 1e-6), "%.4f" % b.height)
    expect("zombie villager 2.125 tall", near(zv.height, 2.125, 1e-6), "%.4f" % zv.height)
    expect("baby zombie villager 1.0 tall, eyes 0.67", near(bv.height, 1.0, 1e-6) and near(bv.eye_height, 0.67, 1e-6))
    expect("husk 2.125 tall", near(hk.height, 2.125, 1e-6), "%.4f" % hk.height)
    expect("speeds 2.330 / 5.243 / panic 6.195 / villager walk 2.753",
           near(WALK_SPEED, 2.3304, 2e-3) and near(BABY_SPEED, 5.2434, 2e-3) and near(VILLAGER_PANIC_SPEED, 6.195, 2e-3)
           and near(VILLAGER_WALK_SPEED, 2.753, 2e-3), "%.4f %.4f %.4f %.4f" % (WALK_SPEED, BABY_SPEED, VILLAGER_PANIC_SPEED, VILLAGER_WALK_SPEED))
    for c in (z, b, zv, bv):
        c.place(1, (0.0, 0.0, 0.0), 0.0)
    scene.frame_set(1)
    bpy.context.view_layer.update()
    lo = min((ob.matrix_world @ Vector(v.co)).z for ob in (z.leg_l, z.leg_r) for v in ob.data.vertices)
    hi = max((z.head.matrix_world @ Vector(v.co)).z for v in z.head.data.vertices)
    expect("zombie mesh stands on the ground, head box top at 2.0 (+ hat layer)", near(lo, 0.0, 1e-4) and hi <= 2.0 + 0.5 / 16 + 1e-4, "%.4f .. %.4f" % (lo, hi))

    # ---- arms: rest pose, bob, aggro, attack
    for f in (1.0, 37.0, 80.5):
        _evaluate(scene, f)
        want = z.arm_pose(f)
        got = (z.arm_r.rotation_euler[0], -z.arm_r.rotation_euler[2], z.arm_r.rotation_euler[1])
        left = (z.arm_l.rotation_euler[0], -z.arm_l.rotation_euler[2], z.arm_l.rotation_euler[1])
        bx = z.arm_bob(f)[0]
        expect("arms at frame %g follow animateZombieArms + bobModelPart" % f,
               all(near(a, w, 1e-4) for a, w in zip(got, want))
               and near(left[0], want[0] - 2 * bx, 1e-4) and near(left[1], -want[1], 1e-4) and near(left[2], -want[2], 1e-4),
               "right %s" % (tuple(round(v, 4) for v in got),))
    expect("rest pitch -80 degrees, raised -120", near(math.degrees(ARMS_OUT), -80.0, 1e-6) and near(math.degrees(ARMS_RAISED), -120.0, 1e-6))
    _evaluate(scene, 1.0)
    hand = z.arm_r.matrix_world @ Vector((-1.0 / 16.0, 0.0, -10.0 / 16.0))
    print("     hand (arms out) %s" % (tuple(round(v, 3) for v in hand),))
    z.aggro(20, True, ease=3)
    z.aggro(60, False, ease=0)
    end = z.attack(30)
    for f, want in ((19.0, ARMS_OUT), (23.0, ARMS_RAISED), (29.9, ARMS_RAISED), (59.0, ARMS_RAISED), (60.0, ARMS_OUT), (60.5, ARMS_OUT)):
        _evaluate(scene, f)
        expect("aggro: base pitch at frame %g" % f, near(z.arm_r.rotation_euler[0] - z.arm_bob(f)[0], want, 1e-3),
               "%.4f" % (z.arm_r.rotation_euler[0] - z.arm_bob(f)[0]))
    mid = 30 + 4.0 * TICK                                               # animation value 0.5: one tick late, as the client
    _evaluate(scene, mid)
    a = z.swing_value(mid)
    want = ARMS_RAISED + math.sin(a * math.pi) * SWING_DOWN - math.sin((1 - (1 - a) ** 2) * math.pi) * SWING_BACK
    expect("attack: animation value 0.5 four ticks in, arms chop down", near(a, 0.5, 1e-6) and near(z.arm_r.rotation_euler[0] - z.arm_bob(mid)[0], want, 2e-3)
           and near(want - ARMS_RAISED, 1.2 - 0.4 * math.sin(0.75 * math.pi), 1e-6), "a=%.3f pitch %.3f end %d" % (a, want, end))
    _evaluate(scene, end + 0.5)
    expect("attack: arms and body back at rest afterwards", near(z.arm_r.rotation_euler[0] - z.arm_bob(end + 0.5)[0], ARMS_RAISED, 1e-3)
           and near(z.body.rotation_euler[2], 0.0, 1e-5) and near(z.head.rotation_euler[2], 0.0, 1e-5))

    # ---- gait
    def sole(c, leg):
        return leg.matrix_world @ Vector((0.0, 0.0, -c.leg_len))

    for label, who, gait in (("adult planted", make_zombie("w1"), "planted"), ("adult vanilla", make_zombie("w2"), "vanilla"),
                             ("baby planted", make_zombie("w3", baby=True), "planted"),
                             ("zombie villager planted", make_zombie_villager("w4", "librarian"), "planted")):
        who.place(1, (0.0, 0.0, 0.0), math.radians(90))
        endw = who.walk(1, [(0.0, 0.0, 0.0), (9.0, 0.0, 0.0)], gait=gait)
        info = who.last_walk
        slide, low, lift = 0.0, 1e9, 0.0
        before, carrying, anchor = None, None, 0.0
        f = 1.0 + info["cycle_frames"]
        while f < endw - info["cycle_frames"]:
            _evaluate(scene, f)
            pts = [sole(who, who.leg_l), sole(who, who.leg_r)]
            if before is not None:
                moved = [abs(pts[i].x - before[i].x) for i in (0, 1)]
                idx = 0 if moved[0] <= moved[1] else 1                  # the sole that stays behind carries
                if gait == "vanilla" or moved[idx] <= 0.2 * moved[1 - idx]:    # (not the sample in which they swap)
                    if idx != carrying:
                        carrying, anchor = idx, pts[idx].x
                    slide = max(slide, abs(pts[idx].x - anchor))
                    low, lift = min(low, pts[idx].z), max(lift, pts[idx].z)
            before = pts
            f += 0.125
        print("     %-24s end %d speed %.3f swing %.1f deg cycle %.3f blocks %.2f frames | stance sole drifts %.4f, height %.4f..%.4f"
              % (label, endw, info["speed"], math.degrees(info["swing"]), info["cycle_blocks"], info["cycle_frames"], slide, low, lift))
        if gait == "planted":
            tol = 0.012 if who.baby else 0.004                         # (a baby's step lasts under two frames)
            expect("%s: the sole on the ground does not slide" % label, slide < tol and abs(low) < 0.006 and lift < 0.006, "%.4f" % slide)
        else:
            expect("vanilla gait: +-37 degrees, one cycle per 2.36 blocks, feet slide",
                   near(math.degrees(info["swing"]), 37.4, 0.3) and near(info["cycle_blocks"], 2.358, 0.01) and slide > 0.1, "%.3f" % slide)
        expect("%s: walks at the game's speed" % label, near(info["speed"], who.walk_speed, 0.03), "%.3f" % info["speed"])
        _evaluate(scene, endw + 8.0)
        expect("%s: legs neutral and hips at rest after the walk" % label, near(who.leg_l.rotation_euler[0], 0.0, 1e-4)
               and near(who.hips.location[2], who._rest(who.hips, _LOC, 2), 1e-5))

    # ---- hurt: flash, knock-back, twin
    track = knockback_track()
    apex = max(u for _b, u in track)
    air = next(k for k, (_b, u) in enumerate(track) if k > 0 and u == 0.0) + 1
    expect("knock-back: 0.96 up, on the ground after 10 ticks, 1.9 back", near(apex, 0.965, 0.01) and air == 10 and near(track[-1][0], 1.9, 0.1),
           "apex %.3f, lands on tick %d, back %.3f" % (apex, air, track[-1][0]))
    v = ch.make_villager("victim", "farmer")
    v.place(1, (0.0, -1.0, 0.0), 0.0)
    v.show(1, True)
    hz = make_zombie("hitter")
    hz.place(1, (0.0, -2.2, 0.0), math.radians(180))
    hz.attack(40, target=v)
    twins = v.__dict__[_STATE]["twins"]
    expect("hurt: every mesh of the villager has a red twin", len(twins) == len([o for o in v.objects() if o.type == "MESH"]) and len(twins) >= 5, str(len(twins)))
    states = {}
    for f in (39, 40, 51, 52):
        scene.frame_set(f)
        states[f] = (all(_rendered(o) for o in v.objects() if o.type == "MESH"), all(_rendered(t) for t in twins.values()),
                     any(_rendered(t) for t in twins.values()))
    expect("hurt: red twin on frames 40-51 only, the villager itself hidden meanwhile",
           states[39][0] and not states[39][2] and not states[40][0] and states[40][1] and not states[51][0] and states[51][1]
           and states[52][0] and not states[52][2], str(states))
    img = next(n.image for n in next(iter(twins.values())).data.materials[0].node_tree.nodes if n.type == "TEX_IMAGE")
    src = bpy.data.images[img.name[len("undead_hurt/"):]]
    p_red, p_src = np.array(img.pixels[:4]), np.array(src.pixels[:4])
    idx = int(np.argmax(np.array(src.pixels[:]).reshape(-1, 4)[:, 3] > 0.5))
    p_red, p_src = np.array(img.pixels[idx * 4:idx * 4 + 4]), np.array(src.pixels[idx * 4:idx * 4 + 4])
    expect("hurt: texel = 0.698 * texel + 0.302 * red", near(p_red[0], p_src[0] * OVERLAY_KEEP + 1 - OVERLAY_KEEP, 2e-3)
           and near(p_red[1], p_src[1] * OVERLAY_KEEP, 2e-3) and near(p_red[2], p_src[2] * OVERLAY_KEEP, 2e-3), "%s -> %s" % (p_src[:3].round(3), p_red[:3].round(3)))
    top, far = 0.0, 0.0
    for k in range(0, 40):
        p = v.pos_at(40 + k * 0.5)
        top, far = max(top, p.z), max(far, p.y + 1.0)
    expect("hurt: the villager hops 0.96 up and 1.9 away from the zombie (+Y)", near(top, 0.965, 0.01) and near(far, 1.9, 0.1) and near(v.pos_at(80).x, 0.0, 1e-6), "%.3f %.3f" % (top, far))
    _evaluate(scene, 40 + TICK)
    expect("hurt: the legs kick apart within a tick (0.7 rad for a villager)", near(abs(v.leg_l.rotation_euler[0]), 0.7, 0.01)
           and near(v.leg_l.rotation_euler[0], -v.leg_r.rotation_euler[0], 1e-6), "%.3f" % v.leg_l.rotation_euler[0])
    _evaluate(scene, 90.0)
    expect("hurt: legs at rest again afterwards", near(v.leg_l.rotation_euler[0], 0.0, 1e-4))
    v.show(100, False)                                                   # the film hides him for the next shot ...
    v.show(140, True)
    scene.frame_set(45)
    red_45 = all(_rendered(t) for t in twins.values())
    scene.frame_set(100)
    off_100 = not any(_rendered(o) for o in v.objects() if o.type == "MESH") and not any(_rendered(t) for t in twins.values())
    scene.frame_set(140)
    on_140 = all(_rendered(o) for o in v.objects() if o.type == "MESH")
    expect("show() after hurt(): flash kept, hidden and shown as the film says", red_45 and off_100 and on_140)

    wv = ch.make_villager("walking", "none")
    wv.place(1, (20.0, 0.0, 0.0), math.radians(90))
    endw = wv.walk(1, [(20.0, 0.0, 0.0), (30.0, 0.0, 0.0)])
    at = wv.pos_at(30)
    hurt(wv, 30, attacker=(at.x + 1.0, 0.0, 0.0))
    _evaluate(scene, 80.0)
    expect("a blow ends a walk: knocked back 1.99 and staying there, bob and legs at rest",
           near(wv.pos_at(endw).x, at.x - 1.99, 0.02) and near(wv.hips.location[2], wv._rest(wv.hips, _LOC, 2), 1e-5)
           and near(wv.leg_l.rotation_euler[0], 0.0, 1e-4), "%.2f -> %.2f (the walk would have reached 30)" % (at.x, wv.pos_at(endw).x))
    wz = make_zombie("walking_z")
    wz.place(1, (20.0, 3.0, 0.0), math.radians(90))
    endw = wz.walk(1, [(20.0, 3.0, 0.0), (30.0, 3.0, 0.0)])
    at = wz.pos_at(30)
    wz.die(30, camera=cam, knockback=False, poof=False)
    expect("death in mid-walk without knock-back: it stops where it was", (wz.pos_at(50) - at).length < 1e-4, "%.3f" % (wz.pos_at(50) - at).length)

    st2 = ch.make_player("steve_hit")
    st2.place(1, (24.0, -4.0, 0.0), 0.0)
    e1 = hurt(st2, 20, attacker=(24.0, -5.0, 0.0))
    gm = mobs.make_iron_golem("golem_hit")
    gm.place(1, (28.0, -4.0, 0.0), 0.0)
    gm.show(1, True)
    e2 = hurt(gm, 20, attacker=(28.0, -6.0, 0.0))
    g_gone = die(gm, 60, camera=cam, attacker=(28.0, -6.0, 0.0), seed=9)
    scene.frame_set(25)
    red = [o for o in list(st2.__dict__[_STATE]["twins"].values()) + list(gm.__dict__[_STATE]["twins"].values()) if _rendered(o)]
    expect("hurt works on Steve and on the iron golem (which is not knocked back)", len(red) == 12 and st2.pos_at(40).y > -2.2
           and (gm.pos_at(59) - gm.pos_at(1)).length < 1e-6 and e1 >= 32 and e2 == 32 and g_gone == 84, "%d red parts" % len(red))

    # ---- death
    dz = make_zombie("dying")
    dz.place(1, (4.0, 0.0, 0.0), 0.0)
    dz.show(1, True)
    gone = dz.die(50, camera=cam, attacker=(4.0, -3.0, 0.0))
    expect("death: gone 24 frames after the blow", gone == 74)
    for t, want in ((1.0, 0.0), (2.0, 25.46), (5.0, 50.91), (9.0, 72.0), (13.5, 90.0), (19.0, 90.0)):
        _evaluate(scene, 50 + t * TICK)
        expect("death: %.1f degrees after %g ticks" % (want, t), near(math.degrees(dz.root.rotation_euler[1]), want, 0.6),
               "%.2f" % math.degrees(dz.root.rotation_euler[1]))
    _evaluate(scene, 50 + 14 * TICK)
    head = dz.head.matrix_world.translation
    expect("death: it falls to its LEFT (+X for yaw 0), head at ground level", head.x - dz.pos_at(67).x > 1.3 and abs(head.z - dz.pos_at(67).z) < 0.1, "%s" % (tuple(round(c, 2) for c in head),))
    dt = dz.__dict__[_STATE]["twins"]
    scene.frame_set(60)
    red = all(_rendered(t) for t in dt.values()) and not any(_rendered(o) for o in dz.objects() if o.type == "MESH")
    scene.frame_set(74)
    none = not any(_rendered(t) for t in dt.values()) and not any(_rendered(o) for o in dz.objects() if o.type == "MESH")
    expect("death: red while it lies, nothing left on frame 74", red and none)
    bursts = [bu for bu in fx._BURSTS if bu.kind == "poof"]
    parents = [p for p in bursts[-1].particles if "stage" not in p]
    scene.frame_set(74)
    live = [p for p in bursts[-1].particles if p["first"] <= 74 < p["last"]]
    expect("death: 20 poof particles appear on frame 74", len(parents) == POOF_COUNT and len(live) == POOF_COUNT, "%d parents, %d on 74" % (len(parents), len(live)))
    rise = [p["pos"][-1][2] - p["pos"][0][2] for p in parents]
    widths = [2 * p["size"] for p in parents]
    lifes = [p["lifetime"] for p in parents]
    expect("poof: rises, quads 0.2-1.4 wide, 18-82 ticks", min(rise) > 0.0 and 0.2 <= min(widths) and max(widths) <= 1.4 and 18 <= min(lifes) and max(lifes) <= 82,
           "rise %.2f..%.2f width %.2f..%.2f life %d..%d" % (min(rise), max(rise), min(widths), max(widths), min(lifes), max(lifes)))
    dz.place(200, (4.0, 0.0, 0.0), 0.0)
    scene.frame_set(200)
    expect("death: the next place() brings it back upright", all(_rendered(o) for o in dz.objects() if o.type == "MESH") and near(dz.root.rotation_euler[1], 0.0, 1e-6))
    scene.frame_set(150)
    expect("death: ... and not before", not any(_rendered(o) for o in dz.objects() if o.type == "MESH"))

    # ---- infection
    iv = fx.make_job_villager("job", ("farmer", "none"))
    iv.place(1, (8.0, 0.0, 0.0), math.radians(30))
    iv.show(1, True)
    izv = make_zombie_villager("job_z", "farmer")
    izv.show(1, True)
    iz = make_zombie("biter")
    iz.place(1, (8.0, -1.2, 0.0), math.radians(180))
    iz.attack(300, target=iv)
    here = iv.pos_at(324)
    iz.attack(324)
    endi = infect(iv, izv, 324, attacker=iz)

    def shown(c):
        return [o for o in c.objects() if o.type == "MESH" and _rendered(o)]

    scene.frame_set(323)
    before = (len(shown(iv)), len(shown(izv)))
    scene.frame_set(324)
    after = (len(shown(iv)), len(shown(izv)))
    reds = [t for t in list(iv.__dict__[_STATE]["twins"].values()) + list(izv.__dict__[_STATE]["twins"].values()) if _rendered(t)]
    expect("infection: villager until 323, zombie villager from 324, nothing red", before[0] > 0 and before[1] == 0 and after[0] == 0 and after[1] >= 6 and not reds, "%s %s" % (before, after))
    expect("infection: same place and yaw", (izv.pos_at(324) - here).length < 1e-6 and near(izv.yaw_at(324), iv.yaw_at(324), 1e-6))
    expect("infection: the zombie villager takes the knock-back hop", max(izv.pos_at(324 + k).z for k in range(14)) > 0.9 and izv.pos_at(endi).y > here.y + 1.5, "end %d" % endi)
    expect("infection: no particles of any kind", not [bu for bu in fx._BURSTS if bu.frame in (323, 324, 325)])
    expect("infection: a zombified farmer is a farmer", izv.profession == "farmer")

    # ---- potion and cure
    steve = ch.make_player("steve")
    steve.place(1, (8.0, -3.5, 0.0), 0.0)
    izv.place(400, (8.0, 0.0, 0.0), math.radians(180))
    hit = throw_potion(steve, izv, 410, camera=cam, seed=3)
    pts = hit.points
    v0 = (pts[1] - pts[0])
    expect("potion: leaves 1.52 above the feet at 0.5 block per tick (after the first tick's gravity and drag)",
           near(pts[0].z, 1.52, 1e-6) and near(hit.speed, 0.5, 1e-9) and near(v0.length, 0.5 * 0.99, 0.03), "%.3f %.3f" % (pts[0].z, v0.length))
    expect("potion: breaks on the hit box, %d ticks later" % (len(pts) - 1), abs(hit.hit.y - (0.0 - 0.6)) < 0.02 and isinstance(hit, int) and hit == int(math.ceil(410 + (len(pts) - 1) * TICK - 1e-6)), "frame %d at %s" % (hit, tuple(round(c, 2) for c in hit.hit)))
    kinds = [p for p in hit.burst.particles if "stage" not in p]
    scene.frame_set(int(hit))
    live = [p for p in hit.burst.particles if p["first"] <= int(hit) < p["last"]]
    expect("splash: 8 shards + 100 swirls appear on the impact frame", len(kinds) == SPLASH_SHARDS + SPLASH_COUNT and len(live) == SPLASH_SHARDS + SPLASH_COUNT, "%d / %d" % (len(kinds), len(live)))
    tints = sorted({ob.data.materials[0].name.split("#")[1][:6] for ob in hit.burst.objects if "#" in ob.data.materials[0].name})
    expect("splash: Weakness grey 0x484D48 in four shades", len(tints) == 4 and all(int(tn[0:2], 16) < 0x49 and abs(int(tn[2:4], 16) - int(tn[0:2], 16)) <= 6 for tn in tints), str(tints))
    scene.frame_set(int(hit) - 1)
    b_on = _rendered(hit.bottle)
    scene.frame_set(int(hit))
    expect("potion: the bottle is there until the impact frame", b_on and not _rendered(hit.bottle))
    reach = [(Vector(p["pos"][-1]) - Vector(p["pos"][0])).length for p in kinds[SPLASH_SHARDS:]]
    print("     splash swirls travel %.2f..%.2f blocks (median %.2f)" % (min(reach), max(reach), sorted(reach)[len(reach) // 2]))
    apple = bpy.data.objects.new("apple", None)
    scene.collection.objects.link(apple)
    steve.hold(apple)
    res = cure(izv, iv, 440, 560, camera=cam, player=steve, weakness_from=int(hit), seed=1)
    scene.frame_set(439)
    a_before = apple.scale[0]
    scene.frame_set(440)
    expect("cure: the apple is consumed on the frame it is used", a_before > 0.4 and apple.scale[0] < 0.01, "%.3f -> %.4f" % (a_before, apple.scale[0]))
    far = potion_track((0.0, 0.0, 1.52), (5.0, 0.0, 0.0)), potion_track((0.0, 0.0, 1.52), (6.5, 0.0, 0.0))
    reach, d = 0.0, 3.0
    while potion_track((0.0, 0.0, 1.52), (d, 0.0, 0.0)) is not None:
        reach, d = d, d + 0.05
    expect("potion: the game's throw reaches the ground 5 blocks away, not 6.5", far[0] is not None and far[1] is None, "furthest %.2f blocks" % reach)
    vals = []
    for k in range(0, 12):
        _evaluate(scene, 440 + k * TICK + 0.5)
        vals.append(math.degrees(izv.hips.rotation_euler[2]))
    age = int(round(440 / TICK + izv._age0))
    expect("cure: the shake is cos(floor(age) * 3.25) * 1.26 degrees, new every tick",
           all(near(vv, math.cos((age + k) * 3.25) * 1.2566, 1e-3) for k, vv in enumerate(vals)), str([round(vv, 2) for vv in vals[:6]]))
    scene.frame_set(559)
    b4 = (len(shown(izv)), len(shown(iv)))
    scene.frame_set(560)
    af = (len(shown(izv)), len(shown(iv)))
    expect("cure: zombie villager until 559, the villager from 560, same place", b4[0] >= 6 and b4[1] == 0 and af[0] == 0 and af[1] >= 5
           and (iv.pos_at(560) - izv.pos_at(559)).length < 1e-6 and near(izv.hips.rotation_euler[2], 0.0, 1e-9), "%s %s" % (b4, af))
    n_s = len([p for p in res["strength"].particles if "stage" not in p])
    n_n = len([p for p in res["nausea"].particles if "stage" not in p])
    n_w = len([p for p in res["weakness"].particles if "stage" not in p])
    expect("cure: about one swirl every 4 ticks (strength %d in 100 ticks, nausea %d in 200, weakness %d)" % (n_s, n_n, n_w),
           15 <= n_s <= 36 and 34 <= n_n <= 68 and n_w >= 1)
    cols = {name: sorted({ob.data.materials[0].name.split("#")[1][:6] for ob in res[name].objects}) for name in ("strength", "nausea", "weakness")}
    expect("cure: Strength ffc700, Nausea 551d4a, Weakness 484d48", cols == {"strength": ["ffc700"], "nausea": ["551d4a"], "weakness": ["484d48"]}, str(cols))
    ups = [p["pos"][-1][2] - p["pos"][0][2] for p in res["strength"].particles if "stage" not in p]
    expect("swirls rise", min(ups) > 0.0, "%.2f..%.2f blocks" % (min(ups), max(ups)))
    print("check: %d of %d passed" % (sum(ok), len(ok)))
    return all(ok)


def _selftest(which):
    import os

    from . import quick

    def want(name):
        return (not which and name == "check") or name in which

    def stage(preset="day", blur=False, **kw):
        scene = quick.reset()
        quick.setup(scene, res=(540, 960))
        sun = quick.light(scene, preset)
        if preset == "day":
            sun.data.energy = 3.0
        if blur:                                                         # the films' shutter (look.setup_render)
            scene.render.use_motion_blur = True
            scene.render.motion_blur_shutter = 0.5
            scene.render.motion_blur_position = "START"
        mobs._set(scene, **kw)
        return scene

    def sheet(name, paths, height=480):
        """The stills side by side in one picture."""
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

    def shoot(scene, name, frame):
        scene.frame_set(int(frame))
        path = quick.render(scene, name)
        print("wrote", path, "frame", frame)
        return path

    if want("check"):
        if not _check():
            sys.exit(1)

    wall = ((-5, 2, 5, 2), ("stone_bricks", "oak_planks", "stone_bricks", "oak_planks"))

    if want("lineup"):
        scene = stage("day", wall=((-5, 3, 5, 3), ("stone_bricks", "oak_planks", "stone_bricks", "oak_planks", "stone_bricks")))
        ch._test_box("undead_step", (-3.2, 1.0, 0.0), (3.2, 3.0, 2.25), ch._test_material("undead_step", "block/stone_bricks"))
        front = [make_zombie("zombie"), ch.make_player("steve"), ch.make_villager("villager", "none"),
                 make_zombie("baby_zombie", baby=True), ch.make_villager("kid", "none", child=True)]
        back = [make_zombie_villager("zv_none", "none"), make_zombie_villager("zv_farmer", "farmer"),
                ch.make_villager("farmer", "farmer"), make_zombie_villager("zv_librarian", "librarian"),
                make_zombie_villager("zv_baby", baby=True)]
        for i, c in enumerate(front):
            c.place(1, ((i - 2) * 1.1, 0.0, 0.0), 0.0)
        for i, c in enumerate(back):
            c.place(1, ((i - 2) * 1.1, 1.7, 2.25), 0.0)
        scene.objects["quick_sun"].rotation_euler[2] = math.radians(-25)
        quick.camera(scene, (0.5, -17.5, 3.2), (0.0, 0.8, 2.2), lens=41)
        shoot(scene, "undead_lineup", 1)

    if want("lineup2"):                                                  # husk and the other biomes, closer
        scene = stage("day", wall=wall)
        cast = [make_zombie("zombie"), make_zombie("husk", variant="husk"), make_zombie_villager("zv_desert", "cleric", biome="desert"),
                make_zombie_villager("zv_snow", "butcher", biome="snow"), make_zombie_villager("zv_swamp", "nitwit", biome="swamp")]
        for i, c in enumerate(cast):
            c.place(1, ((i - 2) * 1.1, 0.0, 0.0), 0.0)
        scene.objects["quick_sun"].rotation_euler[2] = math.radians(-25)
        quick.camera(scene, (0.4, -14.0, 1.7), (0.0, 0.0, 1.2), lens=32)
        shoot(scene, "undead_lineup_more", 1)

    if want("turn"):
        scene = stage("day", wall=((-5, 4, 5, 4), ("stone_bricks", "oak_planks", "stone_bricks", "oak_planks", "stone_bricks")))
        ch._test_box("undead_step", (-3.2, 1.6, 0.0), (3.2, 4.0, 2.3), ch._test_material("undead_step", "block/stone_bricks"))
        for i, (yaw, pos) in enumerate(((0, (-0.9, 0.0, 0.0)), (-40, (0.9, 0.0, 0.0)), (90, (-0.9, 2.4, 2.3)), (180, (0.9, 2.4, 2.3)))):
            z = make_zombie("turn%d" % i)
            z.place(1, pos, math.radians(yaw))
        scene.objects["quick_sun"].rotation_euler[2] = math.radians(-30)
        quick.camera(scene, (0.2, -10.5, 2.9), (0.0, 1.0, 2.2), lens=50)
        shoot(scene, "undead_zombie_turn", 1)

    if want("walk") or want("walk_vanilla"):
        for gait in (("planted",) if want("walk") else ()) + (("vanilla",) if want("walk_vanilla") else ()):
            scene = stage("day", blur=True, path=(-8, 8), wall=((-8, 3, 8, 3), ("stone_bricks", "oak_planks", "stone_bricks")))
            z = make_zombie("walker")
            z.place(1, (-6.0, 0.0, -0.0625), math.radians(90))
            end = z.walk(1, [(-6.0, 0.0, -0.0625), (7.0, 0.0, -0.0625)], gait=gait)
            z.idle(1, end, seed=2)
            info = z.last_walk
            print(gait, "walk ends at frame", end, {k: (round(v, 3) if isinstance(v, float) else v) for k, v in info.items()})
            cyc = info["cycle_frames"]
            stills = []
            for i in range(4):
                f = int(round(8 + cyc + i * cyc / 4.0))
                here = z.pos_at(f)
                quick.camera(scene, (here.x + 0.9, -6.4, 1.05), (here.x, 0.0, 1.0), lens=50)
                stills.append(shoot(scene, "undead_walk%s_%d" % ("" if gait == "planted" else "_vanilla", i + 1), f))
            sheet("undead_walk%s_sheet" % ("" if gait == "planted" else "_vanilla"), stills)

    if want("attack"):
        scene = stage("day", blur=True, wall=wall)
        z = make_zombie("zombie")
        v = ch.make_villager("farmer", "farmer")
        z.place(1, (-1.25, 0.0, 0.0), math.radians(90))
        v.place(1, (0.05, 0.0, 0.0), math.radians(-90))
        z.aggro(1, True, ease=0)
        z.look_at(1, v, ease=0)
        v.look_at(1, z, ease=0)
        end = z.attack(20, target=v)
        z.aggro(20, False)
        quick.camera(scene, (0.5, -9.5, 1.6), (0.4, 0.0, 1.3), lens=27)
        stills = [shoot(scene, "undead_attack_%d" % (i + 1), f) for i, f in enumerate((19, 22, 25, 30))]
        sheet("undead_attack_sheet", stills)
        print("attack ends on", end)

    if want("hurt"):
        scene = stage("day", blur=True, wall=wall)
        z = make_zombie("zombie")
        s = ch.make_player("steve")
        z.place(1, (-0.3, 0.0, 0.0), math.radians(-90))
        s.place(1, (-1.5, 0.0, 0.0), math.radians(90))
        s.look_at(1, z, ease=0)
        fx.arm_swings(s, [18])
        end = z.hurt(20, attacker=s)
        quick.camera(scene, (0.3, -9.5, 1.6), (0.2, 0.0, 1.3), lens=27)
        stills = [shoot(scene, "undead_hurt_%d" % (i + 1), f) for i, f in enumerate((19, 22, 27, 34))]
        sheet("undead_hurt_sheet", stills)
        print("hurt ends on", end)

    if want("death"):
        scene = stage("day", blur=True, wall=wall)
        z = make_zombie("zombie")
        s = ch.make_player("steve")
        z.place(1, (-0.6, 0.0, 0.0), math.radians(-60))
        s.place(1, (-1.9, -0.5, 0.0), math.radians(70))
        s.look_at(1, z, ease=0)
        cam = quick.camera(scene, (0.1, -9.5, 1.9), (0.0, 0.0, 1.15), lens=27)
        fx.arm_swings(s, [18])
        gone = z.die(20, camera=cam, attacker=s, seed=4)
        stills = [shoot(scene, "undead_death_%d" % (i + 1), f) for i, f in enumerate((23, 28, 38, gone, gone + 14))]
        sheet("undead_death_sheet", stills)
        print("gone on", gone)

    if want("infect"):
        scene = stage("day", blur=True, wall=wall)
        z = make_zombie("zombie")
        v = ch.make_villager("farmer", "farmer")
        zv = make_zombie_villager("farmer_z", "farmer")
        z.place(1, (-1.1, 0.0, 0.0), math.radians(90))
        v.place(1, (0.2, 0.0, 0.0), math.radians(-90))
        z.aggro(1, True, ease=0)
        z.look_at(1, v, ease=0)
        z.attack(30)
        end = infect(v, zv, 30, attacker=z, max_back=0.8)
        quick.camera(scene, (0.3, -7.6, 1.6), (0.2, 0.0, 1.25), lens=32)
        stills = [shoot(scene, "undead_infect_%d" % (i + 1), f) for i, f in enumerate((29, 30, 34, end + 2))]
        sheet("undead_infect_sheet", stills)

    if want("cure") or want("cure2"):
        scene = stage("day", blur=True, wall=wall)
        steve = ch.make_player("steve")
        zv = make_zombie_villager("farmer_z", "farmer")
        v = ch.make_villager("farmer", "farmer")
        from . import props

        apple = props.make_item("golden_apple", ch._collection(None))
        steve.hold(apple)
        steve.place(1, (-2.6, 0.0, 0.0), math.radians(90))
        zv.place(1, (1.2, 0.0, 0.0), math.radians(-90))
        steve.look_at(1, zv, ease=0)
        zv.look_at(1, steve, ease=0)
        zv.idle(1, 200, seed=1)
        cam = quick.camera(scene, (-0.6, -9.5, 1.6), (-0.6, 0.0, 1.3), lens=25)
        hit = throw_potion(steve, zv, 10, camera=cam, seed=5)
        use = steve.walk(int(hit) + 6, [steve.pos_at(int(hit)), (0.25, 0.0, 0.0)], speed=2.4) + 4   # (he stands when he uses it)
        res = cure(zv, v, use, use + 72, camera=cam, player=steve, weakness_from=int(hit), seed=2)
        print("throw 10, impact", int(hit), "apple", use, "cured", res["frame_end"], "points", len(hit.points))
        if want("cure"):
            frames = (10 + int((int(hit) - 10) * 0.6), int(hit) + 1, int(hit) + 5, use + 3)
            stills = [shoot(scene, "undead_cure_%d" % (i + 1), f) for i, f in enumerate(frames)]
            sheet("undead_cure_sheet_a", stills)
        if want("cure2"):
            quick.camera(scene, (0.75, -6.5, 1.6), (0.75, 0.0, 1.3), lens=40)     # closer, the same direction
            frames = (use + 14, use + 38, use + 66, res["frame_end"] + 30)
            stills = [shoot(scene, "undead_cure_%d" % (i + 5), f) for i, f in enumerate(frames)]
            sheet("undead_cure_sheet_b", stills)

    if want("items"):                                                    # the bottle and what is thrown at whom, close
        scene = stage("day", wall=wall)
        from . import props

        for i, eff in enumerate(("weakness", "strength", (56, 93, 198))):
            ob = make_splash_potion(eff)
            ob.location = (-0.9 + i * 0.6, 0.0, 1.3)
            ob.scale = (0.5, 0.5, 0.5)
        apple = props.make_item("golden_apple", ch._collection(None))
        apple.location = (0.9, 0.0, 1.3)
        apple.scale = (0.5, 0.5, 0.5)
        quick.camera(scene, (0.0, -3.2, 1.3), (0.0, 0.0, 1.3), lens=19)
        shoot(scene, "undead_items", 1)

    if want("hall") or want("street") or want("hall_bars") or want("night_fx"):
        _village_stills(want("hall"), want("street"), want("hall_bars"), want("night_fx"))


def _village_stills(hall, street, hall_bars=False, night_fx=False):
    """A zombie in a trading-hall cell and on a village street at night, through the real set, look and Stage."""
    import os

    from films import lookdev

    from . import look, quick, shots, village

    for name, on in (("hall", hall), ("hall_bars", hall_bars), ("street", street), ("night_fx", night_fx)):
        if not on:
            continue
        scene = quick.reset()
        look.setup_render(scene, res=(540, 960), samples=16, threads=2, motion_blur=True)
        v = village.build_village(scene, seed=1)
        if name.startswith("hall"):
            sky = look.set_time(scene, "golden", sun_azimuth=62.0, sun_elevation=27.0)
            look.setup_compositor(scene, bloom=1.0, grade="warm")
        else:
            sky = look.set_time(scene, "night", sun_azimuth=176.0, sun_elevation=21.0)
            look.setup_compositor(scene, bloom=1.3, grade="cool")
        film = shots.Film(scene, fps=24)
        st = lookdev.Stage(scene, film, v, sky)
        s = st.shot(name, 2.0)
        f0, f1 = s.frame_start, s.frame_end
        z = add_zombie(st, "zombie")
        if name == "hall_bars":
            # the bars between two cells reach, at head height, from the back wall to the middle of the cell row
            # only: seen from over the counter, 15 degrees off the row, they stand across a zombie at the back
            A = v.anchors
            cell = A["cell_3"]
            spot = (cell[0], cell[1] - 0.50, cell[2])
            z.place(f0, spot, v.yaws["cell_3"])
            vic = st.actor("vic", "farmer", level=2)
            vic.place(f0, A["cell_4"], v.yaws["cell_4"])
            cam0 = (cell[0] - 4.20, cell[1] + 0.65, 1.62)
            z.look_at(f0, cam0, ease=0)
            z.idle(f0, f1 + 1, seed=3)
            vic.look_at(f0, z, ease=0)
            vic.shiver(f0, f1 + 1, seed=1)
            st.use(s, z, vic)
            s.lens(44, 3.4)
            s.move(cam0, (cell[0], spot[1], 1.60), (cam0[0] + 0.10, cam0[1], cam0[2]))
            s.focus(z.head)
            st.hero(s, "zombie", z)
            st.lights(s, scale=0.0, groups={"hall": 0.8}, inside="hall")
        elif name == "hall":
            A = v.anchors
            cell = A["cell_3"]
            spot = (cell[0], cell[1] - 0.40, cell[2])                    # back in his cell: the hands stay behind the job block
            z.place(f0, spot, v.yaws["cell_3"])
            lib = st.actor("lib", "librarian", level=2)
            lib.place(f0, A["cell_2"], v.yaws["cell_2"])
            # from along the counter, 30 degrees off the row: the iron bars between cell 2 and cell 3 stand
            # between the lens and the zombie
            cam0 = (cell[0] - 3.60, cell[1] + 1.56, 1.62)
            z.look_at(f0, cam0, ease=0)
            z.idle(f0, f1 + 1, seed=3)
            lib.look_at(f0, (cell[0] - 0.5, cell[1] + 2.0, 1.6), ease=0)
            lib.shiver(f0, f1 + 1, seed=1)
            st.use(s, z, lib)
            s.lens(46, 3.4)
            s.move(cam0, (cell[0] - 0.05, spot[1] + 0.05, 1.62), (cam0[0] + 0.12, cam0[1], cam0[2]))
            s.focus(z.head)
            st.hero(s, "zombie", z)
            st.lights(s, scale=0.0, groups={"hall": 0.8}, inside="hall")
        elif name == "night_fx":                                         # how the particles read under a lamp at night
            z.place(f0 - 14, (-16.4, 1.2, -0.0625), math.radians(135))
            gone = z.die(f0 - 12, camera=s, attacker=(-14.4, -0.8, 0.0), max_back=0.6, seed=2, village=v)
            zv = add_zombie_villager(st, "zv", "librarian")
            zv.place(f0, (-15.1, 0.2, -0.0625), math.radians(35))
            zv.look_at(f0, (-12.8, -2.7, 1.4), ease=0)
            effect_swirls(zv, f0 - 40, f1 + 1, "strength", camera=s, seed=4)
            shake(zv, f0, f1 + 1)
            st.use(s, z, zv)
            s.lens(30, 2.8)
            s.move((-12.8, -2.7, 0.9), (-15.9, 0.8, 1.35))
            s.focus(zv.head)
            st.hero(s, "zombie villager", zv)
            st.lights(s, scale=1.3)
            print("night_fx: the zombie is gone on frame", gone)
        else:
            lane = [(-21.5, 1.2, -0.0625), (-10.0, 1.2, -0.0625)]
            z.place(f0 - 40, lane[0], math.radians(90))
            z.walk(f0 - 40, lane)
            here = z.pos_at(f0 + 12)                                     # (arms out: raised, they hide the face from here)
            z.look_at(f0 - 40, (here.x + 3.6, here.y - 3.9, 1.5), ease=0)      # (his face to the lens)
            kid = add_zombie(st, "kid_zombie", baby=True)
            kid.place(f0, (-14.38, -0.18, -0.0625), math.radians(40))
            kid.look_at(f0, (here.x + 3.6, here.y - 3.9, 0.9), ease=0)
            st.use(s, z, kid)
            s.lens(30, 2.8)
            s.follow(z.root, (3.6, -3.9, 0.9), (3.75, -3.8, 0.9), look_offset=(-0.35, 0.3, 1.6))    # the camera backs away with him
            s.focus(z.head)
            st.hero(s, "zombie", z)
            st.lights(s, scale=1.3)
        st.finish()
        frame = f0 + (18 if name == "night_fx" else 12)
        film.goto(frame)
        path = os.path.join(quick.TEST_DIR, "undead_%s.png" % name)
        scene.render.filepath = path
        bpy.ops.render.render(write_still=True)
        print("wrote", path, "frame", frame, "zombie at", tuple(round(c, 2) for c in z.pos_at(frame)),
              "rendered parts:", len([o for o in z.objects() if o.type == "MESH" and not o.hide_render]))


if __name__ == "__main__":
    _selftest(set(sys.argv[1:]))
