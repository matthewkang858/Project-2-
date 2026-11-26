"""PILLAGERS, THE PATROL CAPTAIN AND HIS LOOT, for film five "Leg Day" (beats 15-21). New module; edits no other file.

Everything is transcribed from the Java Edition 26.x client classes (named beside each number below) and drawn with
the game's own files through engine.mcassets: entity/illager/pillager.png, item/crossbow_standby / _pulling_0..2 /
_arrow, entity/banner/banner_base + base + the pattern textures, item/ominous_bottle, entity/projectiles/arrow.png.
Blender axes as everywhere: +X east, +Y north, +Z up, 1 block = 1 unit, characters face -Y at yaw 0, 24 fps (the game
runs 20 ticks per second: 1 tick = 1.2 frames). Frames are film frames.

PUBLIC API
  make_pillager(name, captain=False, crossbow=True, loaded=False, collection=None) -> Pillager
      IllagerModel box for box at 0.9375 (1.99 tall, Steve 1.875), nose, tunic; the hat and the crossed arms are
      not drawn (the game hides them for a pillager). Crossbow in the right hand; captain=True wears the ominous
      banner on its head; loaded=True starts with a loaded crossbow.
  add_pillager(st, name="pillager", captain=False, **kw) -> Pillager      the same, registered in a Stage's st.cast
  add_patrol(st, count=5, prefix="pillager", captain=True, **kw) -> [Pillager]   prefix_1 (the captain) .. prefix_N
  march(pillagers, path, frame, spacing=2.0, speed=None, gait="planted", place=True, lead="r", first_step=1.0,
        stride=1.0) -> end frame
      A clean file along `path`: captain in front, the others `spacing` behind each other (their starts carried on
      straight behind path[0]), all at the patrol leader's 1.91 blocks/s, same lead foot and step: in step.
      place=True places them on `frame` (a cut: do not use it for pillagers already in the shot before).
  crush_patrol(pillagers, anvil_drops, at="head", camera=None, stage=None, knockback=None, spots=None, face=None,
               items=True, village=None, glow=None, seed=0, shots=None) -> {name: crushed_by dict}
      The whole file under a row of fixtures.release() anvils: each pillager gets the anvil whose box he is in on
      THAT anvil's landing frame (as the game finds him), then crushed_by. spots = the captain's [bottle, banner].
  crushed_by(pillager, drop, at="head", camera=None, knockback=None, max_back=None, items=True, spots=None,
             seed=0, village=None, glow=None, stage=None, face=None, shots=None, force=False)
      -> dict(frame, damage, lethal, gone, items, cell, fall, side)
      What an engine.fixtures falling anvil (a fall() / release() dict) does to the pillager under it: the
      damage (x 0.75 while the banner is on), then undead.die (lethal: red, tips over to HIS LEFT, poof, drops) or
      undead.hurt. at="head": the frame the anvil's underside passes 1.95 above his feet (the brief); at="land":
      the landing frame, when the game deals the damage (2-3 frames later). knockback=None is the game (a hop of
      1.99 away from the anvil's centre: falling_anvil is not in no_knockback); knockback=False keeps him where he
      stood. camera = the Shot filming the kill (the poof faces it; default: stage's shot holding the kill frame;
      a lethal hit with neither raises). stage=st puts the drops in st.cast AND st.use's them in the kill's shot.
      Raises ValueError when he is not inside the anvil's box (0.79 from the cell centre) on its landing frame
      (force=True: key it anyway). fall = the unit Vector the body tips toward, side = its compass word.
  anvil_damage(drop, pillager) -> health points that anvil takes off him
  drops(pillager, frame, items=None, spots=None, seed=0, stage=None, animate=240, face=None, collection=None,
        shots=None) -> [DroppedItem]
      The death drops ON the killing frame: a captain drops the ominous bottle, then the banner (which leaves his
      head on that frame); a plain pillager killed by an anvil drops nothing. Tossed from his feet with the game's
      (+-0.1, 0.2, +-0.1) blocks per tick, or with spots=[p, ...] the toss that brings each to rest exactly there.
      stage=st: st.cast + st.use(shot holding `frame`, or `shots`); later shots: st.use(s_next, *items).
  make_dropped_banner(name=None, collection=None, seed=0) / add_dropped_banner(st, name="ominous_banner", shot=None)
      -> engine.mobs.DroppedItem: the banner item lying in the world, 0.46 tall, upright, turning about its pole
  make_dropped_bottle(name=None, ...) / add_dropped_bottle(st, name="ominous_bottle", shot=None) -> DroppedItem
      add_*(st, shot=s) registers AND st.use's it in s (a Shot or a list); without shot= st.use it yourself.
  shoot_arrow(start, target, frame, collection=None, name="arrow", speed=1.6, stage=None, shots=None) -> Arrow
      an arrow from a point; stage=st: st.cast + st.use(shot holding `frame`, or `shots`)
  banner_mesh(form="head"|"ground", layers=OMINOUS_LAYERS, base="white") -> Mesh   the banner item model (shared)
  banner_sheet(layers, base) -> (key, HxWx4) the flag texture; banner_matrix(form) the composed transform
  pillager_sheet() -> (key, HxWx4); arrow_track(start, target, speed) -> points per tick; twins_of(c)
  proof_film(names, extra=None) -> (scene, film, stage, village, tiles)    the proof set (tools use it)
  Constants: PATROL_SPEED, FOLLOWER_SPEED, STROLL_SPEED, CHASE_SPEED, CHARGING_SPEED, HEALTH 24, PILLAGER_SIZE,
  PILLAGER_EYE, CHARGE_TICKS 25, CHARGE_FRAMES 30, ATTACK_DELAY_TICKS, ARROW_SPEED, OMINOUS_LAYERS, DYE, STATES.

  Pillager (engine.characters.Character: root / hips / body / head / arm_r / arm_l / leg_r / leg_l; .crossbows
            {state: object}, .banner (the head banner object or None), .captain, .species "pillager", .health)
      place(frame, pos, yaw=0.0)            a cut: upright, legs together, head forward; ends a flash or death
      show(frame, visible=True)             keyed visibility of rig, crossbow and banner (Stage.finish calls it)
      walk(frame, points, speed=None, run=False, from_current=False, gait="planted", lead=None, first_step=None,
           stride=None) -> end frame      1.91 blocks/s (run=True 5.40), crossbow held up all the way (see GAIT)
      look_at / track / face / idle / nod / shake / flinch      head limits 75 / 40 degrees; the crossbow follows
      charge(frame_start, frame_end=None) -> first loaded frame (frame + 32)          see CROSSBOW
      shoot(frame, target=None, stage=None, shots=None) -> Arrow | None     the crossbow is empty from `frame`;
                                            target = point / Character; stage=st: the arrow is cast and use'd
      hurt(frame, attacker=None, knockback=None, max_back=None) / die(frame, camera=<Shot>, ...) -> engine.undead's
      fall_direction(frame) -> Vector       the way the body tips if it dies on frame: his left
      take_banner(frame)                    the banner leaves his head ON frame (drops() calls it)
      queries: crossbow_at(f) ('standby' | 'pulling_0' | 'pulling_1' | 'pulling_2' | 'arrow' = loaded), pose_at(f)
               ('hold' | 'charge' | 'neutral'), wears_banner_at(f), item_point(f) (crossbow centre: a focus
               target), banner_top(f), items(), objects(), last_walk, last_charge, last_death
      kind is "villager" ON PURPOSE: IllagerModel's legs swing 1.4 x 0.5 like VillagerModel's and the box is
      0.6 x 1.95, so engine.undead's hurt / die flail and size the poof exactly as the game does for a pillager.
  Arrow  .object (tip along local +X) .frames (shot, hit) .hit .points; show(frame, visible) for a Stage

USING IT IN A FILM (st = films.lookdev.Stage; beats 15-21 of stories/redstoner.json). Stage.finish HIDES every
cast member a shot does not st.use: what this module makes for you is use'd when you pass stage= (and shot= /
shots=); anything you register yourself you must st.use yourself.
    patrol = illagers.add_patrol(st, 5, prefix="pillager")                # [captain, pillager_2 .. pillager_5]
    end = illagers.march(patrol, road_points, s.frame_start, gait="vanilla")    # beat 15 / 19: the file
    st.use(s, *patrol); st.hero(s, "captain", patrol[0])
    patrol[0].look_at(f_up, (x, y, 18.0), ease=6)                         # beat 19: the captain tips his head up
    falling = fixtures.release(anvils, f_release, world=v, chip=...)      # engine.fixtures: the twelve anvils
    res = illagers.crush_patrol(patrol, falling, camera=s, stage=st, knockback=False, village=v,
                                spots=[bottle_spot, banner_spot], face=cam_pos)
        # each pillager under the anvil that lands on HIM: red, tips over to his left (res[name]["side"]), poof;
        # the captain's bottle + banner drop and are st.use'd in s. The camera must be on the side they fall to.
    st.use(s_next, *res[patrol[0].name]["items"])                         # to keep those two in a later shot
    banner = illagers.add_dropped_banner(st, shot=s20); bottle = illagers.add_dropped_bottle(st, shot=s20)
    banner.place(f0, spot_a); bottle.place(f0, spot_b); banner.face(f0 + 20, cam); banner.animate(f0, f1) ...
        # beat 20 as a new shot with fresh items (or carry the dropped ones on with st.use as above)
    p.charge(f); arrow = p.shoot(f + 60, target=point_in_ground, stage=st)    # beats 16-17: use'd in f + 60's shot
    a = illagers.shoot_arrow(start, post_point, f_before, stage=st, shots=[s17])   # stuck before s17 starts
    Key every pillager in frame order (a later call replaces what was keyed after its frame).
    Single anvils: fixtures.strikes(falling, {p.name: p.pos_at(falling[0]["frame_land"]) ...}) -> crushed_by(p,
    hits[p.name]["drop"], camera=s, stage=st, ...): take positions on the LANDING frame (the file walks about
    3 blocks while an 18-block anvil falls).

WHAT THE GAME DOES (read from the classes)
  - MODEL: IllagerModel.createBodyLayer, ModelLayers.PILLAGER scaled 0.9375 (LayerDefinitions). Pillager.getArmPose:
    CROSSBOW_CHARGE while charging, else CROSSBOW_HOLD whenever it holds a crossbow (also while it walks: a pillager
    never swings its arms, it always aims), else ATTACKING / NEUTRAL; IllagerModel shows the crossed arms only in
    CROSSED, so a pillager never shows them. Box 0.6 x 1.95, eyes 0.85 x 1.95 = 1.6575, health 24.
  - CROSSBOW_HOLD (AnimationUtils.animateCrossbowHold): right arm xRot -pi/2 + 0.1 + head pitch, yRot -0.3 + head
    yaw; left arm xRot -1.5 + head pitch, yRot 0.6 + head yaw: the crossbow points where the head looks. Held by
    ItemInHandLayer with item/crossbow's third-person display (-90, 0, -60 degrees, translation 2 0.1 -3, x 0.9):
    flat, pointing forward at 1.27-1.42 above the feet, limbs across the chest, 0.97 block wide.
  - CROSSBOW_CHARGE (animateCrossbowCharge): right arm xRot -0.971, yRot -0.8 (crossbow down and in), left arm
    from (-0.971, 0.4) to (-pi/2, 0.85) over the charge. Charge = CrossbowItem.getChargeDuration = 25 ticks; the
    model is chosen by CrossbowPull = ticks / 25: pulling_0 below 0.58, pulling_1 from tick 15, pulling_2 at 25,
    crossbow_arrow when charged. charge(f): pulling_0 on f, pulling_1 on f + 18, pulling_2 on f + 30 (one tick),
    loaded and back in CROSSBOW_HOLD from f + 31.2 (frame f + 32). RangedCrossbowAttackGoal then waits 20 + 0..19
    ticks (24-47 frames) before it shoots (shoot() prints a line when it is sooner), shoots at 1.6 blocks per tick
    with inaccuracy 14 - 4 x difficulty, and starts charging again on the next tick if it still sees the target.
    It stands still to charge when the target is within 8 blocks; closing in it walks at 5.40 blocks/s with an
    empty crossbow and 1.35 charging or loaded.
  - THE PATROL (PatrollingMonster.LongDistancePatrolGoal(0.7, 0.595)): the leader (PatrolSpawner makes the first
    member spawned the patrol leader; PatrollingMonster.finalizeSpawn puts the ominous banner in a leader's head
    slot with drop chance 2.0; a pillager spawned other than by a patrol, an event or a structure becomes a leader
    with chance 0.06) walks at 0.595 = 1.91 blocks/s, every other member at 0.7 = 2.64 blocks/s toward the same
    point 10 blocks ahead: in the game they bunch up behind him rather than keep a file. march() keeps the file at
    the leader's pace (a film choice).
  - THE OMINOUS BANNER (Raid.getOminousBannerTemplate): a white banner with rhombus cyan, stripe_bottom light gray,
    stripe_center gray, border light gray, stripe_middle black, half_horizontal light gray, circle light gray,
    border black (DyeColor colours F9FFFE 9D9D97 474F52 1D1D21 169C9C). Drawn as the banner ITEM
    (BannerSpecialRenderer: standing BannerModel pole 2x42x2 + bar 20x2x2 on banner_base.png, BannerFlagModel flag
    20x40x1 tilted -0.45 degrees, each pattern texture tinted and layered; items/white_banner.json transformation
    T(0.5, 0, 0.5) S(2/3, -2/3, -2/3)). ON THE HEAD: CustomHeadLayer (translate 0 -0.25 0, rotate Y 180, scale
    0.625 -0.625 -0.625) + template_banner display.head (rotate Y 180, translate 0 16 7, scale 1.5): a banner pixel p
    sits at 0.625 p + (0, -6.5, 4.375) in the head's pixels: pole on the back of the head, flag 12.5 px wide (the
    head is 8) from 1 px inside the head top up to 34 px above the neck: the top at 3.40 above the feet, the front
    facing forward. ON THE GROUND (display.ground: translate 0 1 0, scale 0.25): 0.46 tall, upright, turning about
    its pole, 1/16 above the ground plus the item bob (ItemEntityRenderer: -minY + 1/16 = 0.125).
  - DEATH AND LOOT: a mob dies on the tick of the killing blow; LivingEntity.die -> dropAllDeathLoot at once (the
    body tips over for 20 more ticks): the loot table entities/pillager (VanillaEntityLoot: one ominous_bottle,
    amplifier 0-4, only when he is a captain without a raid; no player kill needed), then Mob.dropCustomDeathLoot:
    the banner (chance 2.0: always; it leaves the head), the crossbow only after a player's hit (chance 0.085):
    an anvil leaves no crossbow. Items appear at the feet with velocity (+-0.1, 0.2, +-0.1) per tick.
  - ANVILS (engine.fixtures; LivingEntity.hurtServer): damage min(floor(ceil(h - 1) x 2), 40) on landing, x 0.75
    with anything in the head slot (DAMAGES_HELMET): a pillager dies under 13 blocks or more, the captain with
    the banner on under 17 or more (13 blocks: 18 damage, he lives). The knock-back goes away from the falling
    block's position (random when he stands right under its centre).

GAIT (IllagerModel.setupAnim, LivingEntity.updateWalkAnimation)
    The game: legs cos(pos x 0.6662) x 1.4 x speed x 0.5 (half a zombie's swing), one leg cycle per 2.36 blocks:
    at the patrol pace the legs swing +-15 degrees once in 29.6 frames and the feet slide about 0.4 block a step.
    gait="vanilla" keys exactly that. gait="planted" (default, a film choice): the legs open as far as a humanoid's
    at that speed (1.4 x speed: +-30.6 degrees at the patrol pace) and the cadence keeps the sole on the ground in
    place (measured drift 0.002 block): a 0.72-block step every 9.0 frames, the hips dipping to keep both soles
    down; that is TWICE the game's swing, a more human stride. planted with stride=0.5 keeps the game's +-15
    degrees with planted soles (a 0.37-block step every 4.7 frames: a quick shuffle). lead / first_step / stride
    default to values from the name; march() gives the whole file the same ones.
    WHICH: gait="vanilla" wherever the soles cannot be judged against the ground (wide shots, long lenses, a file
    walking toward the lens: beat 15 on a long lens, the locked wide of beat 19): it is the pillagers' own short
    shuffle. "planted" for close and side-on tracking shots, where sliding feet read as skating.

CROSSBOW AND HEAD: the arms' channels are rebaked from the pose events and the head after every call that moves
the head (look_at, track, face, idle, nod, shake, flinch, place, walk, show): CROSSBOW_HOLD follows the head's
pitch and yaw, sampled every half frame while the head turns. The pose changes are cuts a quarter frame early.
Nothing else may key the arms.

MEASURED (`$BPY -m engine.illagers check`: 40 checks; proof stills out/test/illagers_*.png)
    1.992 tall, eyes 1.6575; banner top 3.399, 0.732 wide, pole bottom 1.787 (inside the head); dropped banner
    0.458 tall, hover 0.125; crossbow 1.27-1.42 high, pointing -Y (0.04, -0.99, -0.10); hold / charge arm angles
    equal to the formulas; crossbow models switch on frames f, f+18, f+30, f+32; arrow 1.6 blocks/tick, hits its
    point; planted step 9.0 frames, sole drift 0.0016; file gaps 2.000, all legs at the same angle; hurt: 6 red
    twins, crossbow and banner keep their colours, legs kick 0.70 rad; death flat at 13.5 ticks, everything gone
    on frame + 24; damage 18 / 24 / 22 / 24 for captain 13 / captain 17 / pillager 12 / pillager 13 blocks;
    drops on the killing frame in the game's order, resting within 0.006 of their spots; knock-back 1.99. The
    dead body lies to its left (neck 1.41 to the side of the feet). planted stride 0.5: swing 15.5 degrees, a step
    every 4.7 frames, drift 0.0023. crush_patrol on a file walking south under 18-block anvils (3.2 blocks walked
    between release and landing): each gets the anvil over him at landing, falls east, captain 25.5 / others 34.
    Through an unpatched films.lookdev Stage: drops shown from the kill frame in the kill shot (and in a later
    shot that use's them), arrows in their shot, add_dropped_*(shot=) only in that shot. crushed_by refuses a
    pillager outside the box and a kill with no camera before keying anything.
    tools/check_illagers_stamp.py: the same fingerprints in two processes; crossbow switch, banner removal, red
    flash and pose cut each change the fingerprint on their frame and not on the next.

NOT THE GAME (choices and limits)
    planted gait (the game's feet slide); the file keeps its spacing at the leader's pace; drops(spots=) lets items
    land where the director wants (beyond the game's 1.35-block toss a line is printed) and items that spawn inside
    a landed anvil are not pushed out as ItemEntity does (put spots beside the anvil); the arrow's flight is the
    lower gravity arc that hits the target exactly (no inaccuracy, no entity aim formula); one-tick limb twitch on a
    killing blow, sounds, the raid / Bad Omen, illager celebration, riding, vindicators / evokers: not built;
    the crossbow is drawn without enchantment glint (1 in 300 spawn enchanted).

GOTCHAS
  - Never key hide_render, the arms or the crossbow objects yourself: show / place / charge / shoot / take_banner.
  - Stage.finish hides whatever a shot does not st.use: pass stage= to crush_patrol / crushed_by / drops / shoot /
    shoot_arrow and shot= to add_dropped_banner / _bottle, or st.use the items and arrows yourself.
  - crushed_by with the game's knock-back flings a pillager about 2 blocks (over the anvil when he stands under its
    centre): pass knockback=False for the film's "flashes red and tips over" (out/test/illagers_death.png).
  - A dying pillager tips over to HIS LEFT (LivingEntityRenderer.setupRotations): EAST for a file walking south,
    WEST for one walking north. With knockback=False his legs stay under the anvil and the body lies out to that
    side: a camera on the other side sees only the anvils. Film the kill from res["side"], or march the file with
    the wall on its RIGHT hand so the bodies fall out onto the open road toward a road-side camera
    (out/test/illagers_crush.png: a file walking south filmed from the east).
  - A captain needs 17 blocks of drop (the story's shelf at 18 is right, 15 is NOT enough: he survives with 3).
  - With the golden sky (sun az 62) a file walking SOUTH toward a camera that looks north is backlit (faces in
    shade); the proof march walks north toward a camera looking south.
  - hold() is refused: a pillager holds only its crossbow.

Self-test:  $BPY -m engine.illagers [check] [lineup captain banner walk march crossbow death crush loot]
(no argument = check, 40 numeric checks, about 20 s; each still name renders out/test/illagers_<name>.png through the
village with a cobblestone strip on the exit road, the golden look and films.lookdev.Stage; two or three names per
call stay under the 300 s limit.)  $BPY -m tools.check_illagers_stamp  (run twice, compare the DIGEST line).
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
from . import undead

FPS = ch.FPS
TICK = FPS / 20.0                    # frames per game tick
_LOC, _ROT = "location", "rotation_euler"
_HIDE = ("hide_render", "hide_viewport")

# ---- EntityTypes.PILLAGER: sized(0.6F, 1.95F), no eyeHeight() -> EntityDimensions default 0.85 x height
PILLAGER_SIZE = (0.6, 1.95)
PILLAGER_EYE = 0.85 * 1.95                                         # 1.6575
# ---- LayerDefinitions: ModelLayers.PILLAGER = IllagerModel.createBodyLayer().apply(MeshTransformer.scaling(0.9375))
MODEL_SCALE = 0.9375
UNIT = MODEL_SCALE / 16.0
# ---- Pillager.createAttributes(): MOVEMENT_SPEED 0.35, MAX_HEALTH 24, ATTACK_DAMAGE 5, FOLLOW_RANGE 32
SPEED_ATTRIBUTE = 0.35
HEALTH = 24.0
FOLLOW_RANGE = 32.0
# ---- goal speed modifiers -> blocks per second (engine.mobs.mob_speed: 20 * (attribute * modifier)^2 / (1 - 0.546))
#      PatrollingMonster.registerGoals: LongDistancePatrolGoal(this, 0.7, 0.595): the LEADER (the captain, when he has
#      companions) walks at 0.595, every other member at 0.7. Pillager.registerGoals: RandomStrollGoal 0.6,
#      RangedCrossbowAttackGoal(this, 1.0, 8.0F): 1.0 while the crossbow is uncharged, 0.5 while charging / charged.
PATROL_SPEED = mobs.mob_speed(0.595, SPEED_ATTRIBUTE)               # 1.911 blocks / s: the patrol leader's pace
FOLLOWER_SPEED = mobs.mob_speed(0.7, SPEED_ATTRIBUTE)               # 2.644 blocks / s: the other members
STROLL_SPEED = mobs.mob_speed(0.6, SPEED_ATTRIBUTE)                 # 1.943 blocks / s
CHASE_SPEED = mobs.mob_speed(1.0, SPEED_ATTRIBUTE)                  # 5.396 blocks / s: closing in, crossbow empty
CHARGING_SPEED = mobs.mob_speed(0.5, SPEED_ATTRIBUTE)               # 1.349 blocks / s: closing in, charging / loaded
ATTACK_RANGE = 8.0                                                  # RangedCrossbowAttackGoal attackRadius
PATROL_LEADER_CHANCE = 0.06                                         # PatrollingMonster.finalizeSpawn: nextFloat() < 0.06
FILE_SPACING = 2.0                                                  # film choice: one pillager under every other anvil

# ---- Mob.getMaxHeadYRot() 75, getMaxHeadXRot() 40 (no illager class overrides them)
HEAD_YAW_MAX = math.radians(75.0)
HEAD_PITCH_MAX = math.radians(40.0)

# ---- IllagerModel.setupAnim (not riding): legs cos(pos * 0.6662 [+ pi]) * 1.4 * speed * 0.5, arms (when they are not
#      posed) cos(pos * 0.6662 [+ pi]) * 2 * speed * 0.5; LivingEntity.updateWalkAnimation: speed -> min(4 * blocks
#      per tick, 1), lerp 0.4, position += speed every tick
LEG_SWING = 0.7
ARM_SWING = 1.0
LIMB_RATE = 0.6662
ANIM_PER_BLOCK = 4.0
ANIM_LERP = 0.4
PLANTED_SWING = 1.4                  # film gait (see GAIT): the humanoid swing 1.4 * speed (HumanoidModel), soles planted
# ---- AnimationUtils.animateCrossbowHold(rightArm, leftArm, head, true): the arm pose CROSSBOW_HOLD
HOLD_MAIN = (-math.pi / 2.0 + 0.1, -0.3)       # holding (right) arm: xRot = -pi/2 + head.xRot + 0.1, yRot = -0.3 + head.yRot
HOLD_OFF = (-1.5, 0.6)                         # other (left) arm:     xRot = -1.5 + head.xRot,      yRot = 0.6 + head.yRot
# ---- AnimationUtils.animateCrossbowCharge(rightArm, leftArm, chargeDuration, ticksUsing, true): CROSSBOW_CHARGE
CHARGE_MAIN = (-0.97079635, -0.8)              # holding arm: xRot -0.9708, yRot -0.8
CHARGE_OFF_X = (-0.97079635, -math.pi / 2.0)   # other arm: xRot lerp(f, -0.9708, -pi/2), yRot lerp(f, 0.4, 0.85),
CHARGE_OFF_Y = (0.4, 0.85)                     #   f = clamp(ticksUsing, 0, duration) / duration
# ---- CrossbowItem.getChargeDuration: floor(1.25 s * 20) = 25 ticks (no Quick Charge); CrossbowPull = ticks / 25;
#      items/crossbow.json: pulling_0 below 0.58, pulling_1 from 0.58, pulling_2 from 1.0, crossbow_arrow when charged
CHARGE_TICKS = 25
CHARGE_FRAMES = CHARGE_TICKS * TICK                                  # 30
PULL_STEPS = (0.58, 1.0)
ATTACK_DELAY_TICKS = (20, 39)        # RangedCrossbowAttackGoal: CHARGED -> attackDelay = 20 + nextInt(20) -> shoot
# ---- Pillager.performRangedAttack(target, 1.6F) -> CrossbowItem.performShooting(.., velocity 1.6, inaccuracy
#      14 - difficulty * 4); AbstractArrow: gravity 0.05, air drag 0.99, rotation lerp 0.2 per tick; created at
#      the shooter's eye height - 0.1; on a block: stops 0.05 short of the hit point along its flight, shakeTime 7
ARROW_SPEED = 1.6
ARROW_GRAVITY = 0.05
ARROW_DRAG = 0.99
ARROW_TURN = 0.2
ARROW_EYE_DROP = 0.1
ARROW_BACK = 0.05
ARROW_SHAKE_TICKS = 7

# ---- Raid.getOminousBannerTemplate: a WHITE banner with eight pattern layers (BannerPatterns keys = texture names)
OMINOUS_LAYERS = (("rhombus", "cyan"), ("stripe_bottom", "light_gray"), ("stripe_center", "gray"),
                  ("border", "light_gray"), ("stripe_middle", "black"), ("half_horizontal", "light_gray"),
                  ("circle", "light_gray"), ("border", "black"))
DYE = {"white": 0xF9FFFE, "light_gray": 0x9D9D97, "gray": 0x474F52, "black": 0x1D1D21, "cyan": 0x169C9C}  # DyeColor textureDiffuseColor
# ---- BannerModel / BannerFlagModel.createBodyLayer(standing=true), 64 x 64; flag xRot = (-0.0125 + 0.01 cos(2 pi
#      phase)) * pi with phase 0 for an item (BannerRenderer.submitSpecial)
FLAG_XROT = (-0.0125 + 0.01) * math.pi
# ---- items/white_banner.json special-model transformation: translate (0.5, 0, 0.5), scale (2/3, -2/3, -2/3);
#      models/item/template_banner.json display.head: rotate Y 180, translate (0, 16, 7), scale 1.5; display.ground:
#      translate (0, 1, 0), scale 0.25; CustomHeadLayer.translateToHead: translate (0, -0.25, 0), rotate Y 180,
#      scale (0.625, -0.625, -0.625) after the head part's own transform. Composed (derived in banner_matrix):
#      a banner model pixel p lands in the HEAD part's pixel space at 0.625 p + (0, -6.5, 4.375), and on the ground
#      (item display space) at (x, y_up, z) = (p.x, -(p.y + 6), -p.z) / 96 blocks.
BANNER_HEAD_SCALE = 0.625
BANNER_HEAD_OFFSET = (0.0, -6.5, 4.375)
BANNER_GROUND_UNIT = 1.0 / 96.0
BANNER_GROUND_OFFSET = (0.0, 6.0, 0.0)
BANNER_DROP_CHANCE = 2.0             # PatrollingMonster.finalizeSpawn: setDropChance(HEAD, 2.0F): always dropped
# ---- VanillaEntityLoot: entities/pillager = one OMINOUS_BOTTLE (amplifier 0..4) when the pillager is a raider
#      CAPTAIN_WITHOUT_RAID; no killed_by_player condition. Mob.dropCustomDeathLoot: the crossbow (chance 0.085)
#      falls only after a player's hit; the banner (2.0) always. LivingEntity.dropAllDeathLoot: loot table first,
#      then equipment; Entity.spawnAtLocation: at the feet, ItemEntity velocity (+-0.1, 0.2, +-0.1) per tick
TOSS = (0.1, 0.2)

STATES = ("standby", "pulling_0", "pulling_1", "pulling_2", "arrow")
_SPRITE = {"standby": "crossbow_standby", "pulling_0": "crossbow_pulling_0", "pulling_1": "crossbow_pulling_1",
           "pulling_2": "crossbow_pulling_2", "arrow": "crossbow_arrow"}


def _note(text):
    print("[illagers] " + text)


def _rgb(hex_value):
    return ((hex_value >> 16) & 255, (hex_value >> 8) & 255, hex_value & 255)


# ----------------------------------------------------------------------------------------------------
# the model (pixels, the game's model space: x to the mob's left, y DOWN, z to its back, feet on y = 24)
# ----------------------------------------------------------------------------------------------------
def _illager_spec():
    """net.minecraft.client.model.monster.illager.IllagerModel.createBodyLayer() at 64 x 64, drawn at 0.9375.

    Left out, as the game draws a PILLAGER: the hat (texOffs 32, 0, box -4 -10 -4 8 12 8, grow 0.45) is made
    invisible in IllagerModel's constructor (hat.visible = false); the crossed 'arms' (texOffs 44 22: -8 -2 -2 4 8 4,
    texOffs 40 38: -4 2 -2 8 4 4, left_shoulder 44 22 mirrored 4 -2 -2 4 8 4; pose (0, 3, -1) xRot -0.75) are visible
    only in the arm pose CROSSED, which Pillager.getArmPose never returns (CROSSBOW_CHARGE, CROSSBOW_HOLD,
    ATTACKING or NEUTRAL), so a pillager always shows its two separate arms (right_arm / left_arm)."""
    C, P = ch._cube, ch._pose
    eye = 24.0 - PILLAGER_EYE / UNIT
    return dict(
        tex=(64, 64), scale=MODEL_SCALE, hip=12.0, top=-10.0, eye=eye, back=3.0, sleep_eye=PILLAGER_EYE,
        parts=[
            dict(name="body", parent="hips", pivot=(0, 12, 0), groups=[([P(0, -12, 0)], [
                C(16, 20, -4, 0, -3, 8, 12, 6),
                C(0, 38, -4, 0, -3, 8, 20, 6, grow=0.5)])]),                  # the tunic (mostly clear texels)
            dict(name="head", parent="body", pivot=(0, 0, 0), groups=[
                ([], [C(0, 0, -4, -10, -4, 8, 10, 8)]),
                ([P(0, -2, 0)], [C(24, 0, -1, -1, -6, 2, 4, 2)])]),          # nose
            dict(name="arm_r", parent="body", pivot=(-5, 2, 0), groups=[([], [C(40, 46, -3, -2, -2, 4, 12, 4)])]),
            dict(name="arm_l", parent="body", pivot=(5, 2, 0),
                 groups=[([], [C(40, 46, -1, -2, -2, 4, 12, 4, mirror=True)])]),
            dict(name="leg_r", parent="hips", pivot=(-2, 12, 0), groups=[([], [C(0, 22, -2, 0, -2, 4, 12, 4)])]),
            dict(name="leg_l", parent="hips", pivot=(2, 12, 0),
                 groups=[([], [C(0, 22, -2, 0, -2, 4, 12, 4, mirror=True)])]),
        ])


def pillager_sheet():
    """(key, HxWx4 uint8) entity/illager/pillager.png cut out at alpha 0.1 (PillagerRenderer.getTextureLocation)."""
    arr = ch._game_texture("entity/illager/pillager")
    sheet = np.zeros_like(arr)
    ch._over(sheet, arr)
    return "illager_pillager", sheet


# ----------------------------------------------------------------------------------------------------
# the ominous banner
# ----------------------------------------------------------------------------------------------------
def banner_sheet(layers=OMINOUS_LAYERS, base="white"):
    """(key, HxWx4 uint8) the flag texture as BannerRenderer.submitPatterns draws it: entity/banner/base tinted with
    the base colour, then each pattern texture entity/banner/<pattern> tinted with its dye, alpha-blended in order
    (the game draws them as layers over the same flag geometry: the same picture)."""
    def dye(name):
        return np.array(_rgb(DYE[name]), dtype=np.float32) / 255.0

    arr = mc.texture_array("entity/banner/base").astype(np.float32) / 255.0
    out = np.zeros_like(arr)
    out[..., :3] = arr[..., :3] * dye(base)
    out[..., 3] = arr[..., 3]
    for pattern, colour in layers:
        lay = mc.texture_array("entity/banner/" + pattern).astype(np.float32) / 255.0
        a = lay[..., 3:4]
        out[..., :3] = out[..., :3] * (1.0 - a) + lay[..., :3] * dye(colour) * a
        out[..., 3:4] = np.maximum(out[..., 3:4], a)
    key = "illager_banner_" + base + "_" + "_".join("%s-%s" % lc for lc in layers)
    key = "illager_banner_%08x" % (zlib.crc32(key.encode("utf-8")) & 0xFFFFFFFF)
    return key, np.clip(out * 255.0 + 0.5, 0, 255).astype(np.uint8)


def _banner_cubes():
    """[(part matrix in banner-model pixels, cube, which texture)] of BannerModel + BannerFlagModel (standing)."""
    C = ch._cube
    flag_pose = Matrix.Translation((0.0, -44.0, 0.0)) @ Matrix.Rotation(FLAG_XROT, 4, "X")
    return [(Matrix.Identity(4), C(44, 0, -1, -42, -1, 2, 42, 2), "pole"),          # pole
            (Matrix.Identity(4), C(0, 42, -10, -44, -1, 20, 2, 2), "pole"),         # bar
            (flag_pose, C(0, 0, -10, 0, -2, 20, 40, 1), "flag")]                     # flag


def _cubes_mesh(name, entries, unit):
    """One mesh from [(matrix px -> px, cube, sheet, material)]: every cube face unwrapped as ModelPart.Cube does,
    clear texels cut out of the geometry, model (x, y down, z back) -> Blender (x, z, -y) * unit."""
    verts, faces, uvs, slots, mats = [], [], [], [], []
    for m, c, sheet, mat in entries:
        if mat not in mats:
            mats.append(mat)
        slot = mats.index(mat)
        sh, sw = sheet.shape[:2]
        opaque = sheet[..., 3] >= ch.ALPHA_CUTOUT

        def to_local(p, m=m):
            q = m @ Vector(p)
            return Vector((q.x, q.z, -q.y)) * unit

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
            u_lo, u_hi = int(round(min(ua, ub))), int(round(max(ua, ub)))
            v_lo, v_hi = int(round(min(va, vd))), int(round(max(va, vd)))
            outward = sum(pts, Vector()) / 4.0 - centre
            for (c0, r0, c1, r1) in ch._rects(opaque[v_lo:v_hi, u_lo:u_hi]):
                c0, c1, r0, r1 = c0 + u_lo, c1 + u_lo, r0 + v_lo, r1 + v_lo
                corners = [(c0, r0), (c1, r0), (c1, r1), (c0, r1)]
                ps = [pts[0] + du * (cu - ua) + dv * (cv - va) for cu, cv in corners]
                e = 0.02
                tu = [(c0 + e, r0 + e), (c1 - e, r0 + e), (c1 - e, r1 - e), (c0 + e, r1 - e)]
                if (ps[1] - ps[0]).cross(ps[3] - ps[0]).dot(outward) < 0.0:
                    ps.reverse()
                    tu.reverse()
                n = len(verts)
                verts.extend(tuple(p) for p in ps)
                faces.append((n, n + 1, n + 2, n + 3))
                uvs.extend((tx / sw, 1.0 - ty / sh) for tx, ty in tu)
                slots.append(slot)
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    layer = me.uv_layers.new(name="UVMap")
    layer.data.foreach_set("uv", [x for uv in uvs for x in uv])
    for mat in mats:
        me.materials.append(mat)
    me.polygons.foreach_set("material_index", slots)
    me.update()
    return me


def banner_mesh(form="head", layers=OMINOUS_LAYERS, base="white"):
    """The banner as the game draws the banner ITEM (BannerSpecialRenderer: the standing BannerModel + flag), as a
    mesh in one of two frames (cached, shared):
      form 'head':   in the illager HEAD part's frame (origin = neck pivot, Blender axes, entity scale 0.9375): the
                     banner of the CustomHeadLayer, standing on the back of the head, 1.61 blocks tall, front forward;
      form 'ground': in an item entity's frame (origin = its point on the ground before the hover, Blender axes):
                     the 'ground' display, 0.46 block tall, pole on the spin axis."""
    key_f, flag = banner_sheet(layers, base)
    name = "illagers_banner_%s_%s" % (form, key_f[-8:])
    me = bpy.data.meshes.get(name)
    if me is not None:
        return me
    pole = mc.texture_array("entity/banner/banner_base")
    mat_flag = ch._sheet_material(key_f, flag)
    mat_pole = ch._sheet_material("illager_banner_pole", np.array(pole))
    if form == "head":
        m_form = Matrix.Translation(BANNER_HEAD_OFFSET) @ Matrix.Diagonal((BANNER_HEAD_SCALE,) * 3 + (1.0,))
        unit = UNIT
    elif form == "ground":
        m_form = Matrix.Translation(BANNER_GROUND_OFFSET)
        unit = BANNER_GROUND_UNIT
    else:
        raise ValueError("form %r: use 'head' or 'ground'" % (form,))
    entries = []
    for m, c, which in _banner_cubes():
        sheet, mat = (flag, mat_flag) if which == "flag" else (np.array(pole), mat_pole)
        entries.append((m_form @ m, c, sheet, mat))
    return _cubes_mesh(name, entries, unit)


def banner_matrix(form="head"):
    """The composed transform banner-model pixel -> target pixel as derived from the classes (see BANNER_HEAD_*),
    computed here step by step from the JSON numbers, for the self-test: returns (scale, offset) for 'head'."""
    def T(x, y, z):
        return Matrix.Translation((x, y, z))

    def S(x, y, z):
        return Matrix.Diagonal((x, y, z, 1.0))

    ry180 = Matrix.Rotation(math.pi, 4, "Y")
    local = T(0.5, 0.0, 0.5) @ S(2.0 / 3.0, -2.0 / 3.0, -2.0 / 3.0) @ S(1 / 16.0, 1 / 16.0, 1 / 16.0)   # px -> item space
    if form == "head":
        display = T(0.0, 16 / 16.0, 7 / 16.0) @ ry180 @ S(1.5, 1.5, 1.5) @ T(-0.5, -0.5, -0.5)
        layer = T(0.0, -0.25, 0.0) @ ry180 @ S(0.625, -0.625, -0.625)
        m = S(16.0, 16.0, 16.0) @ layer @ display @ local                       # -> head part, pixels (y down)
    else:
        display = T(0.0, 1 / 16.0, 0.0) @ S(0.25, 0.25, 0.25) @ T(-0.5, -0.5, -0.5)
        m = display @ local                                                     # -> item space, blocks (y up)
    return m


# ----------------------------------------------------------------------------------------------------
# shared item meshes
# ----------------------------------------------------------------------------------------------------
def _crossbow_mesh(state):
    """The flat crossbow sprite of one model state (shared mesh): standby, pulling_0..2, arrow (= loaded)."""
    name = "illagers_crossbow_" + state
    me = bpy.data.meshes.get(name)
    if me is not None:
        return me
    ob = mc.item_object(_SPRITE[state])
    me = ob.data
    me.name = name
    bpy.data.objects.remove(ob)
    return me


def _hand_matrix():
    """The crossbow in the right hand: ItemInHandLayer (rotate X -90, Y 180, translate (1, 2, -10) / 16) and the
    third-person display of models/item/crossbow.json (rotation -90 0 -60, translation 2 0.1 -3, scale 0.9)."""
    return undead.held_matrix(undead.item_display("crossbow"), MODEL_SCALE, False)


def _shot_of(stage, frame):
    """The shot of a films.lookdev Stage whose frames hold `frame` (None if no shot holds it yet)."""
    if stage is None:
        return None
    for s in stage.film.shots:
        if s.frame_start <= frame <= s.frame_end:
            return s
    return None


def _on_stage(stage, things, frame, shots=None, what="it"):
    """Register `things` in stage.cast and st.use them in `shots` (a Shot or a list of Shots; default: the shot
    holding `frame`), so that Stage.finish shows them there. Returns the shots used."""
    if stage is None or not things:
        return []
    for t in things:
        stage.cast[t.name] = t
    if shots is None:
        s = _shot_of(stage, frame)
        use = [s] if s is not None else []
        if not use:
            _note("frame %d is in no shot of the Stage yet: %s stays hidden unless you st.use(shot, ...) it"
                  % (int(frame), what))
    else:
        use = list(shots) if isinstance(shots, (list, tuple)) else [shots]
    for s in use:
        stage.use(s, *things)
    return use


def _at(events, frame, default=None):
    """Value of the last (frame, value) event at or before `frame` (frame None = from the start)."""
    value = default
    for f, v in sorted(events, key=lambda e: -1e18 if e[0] is None else e[0]):
        if f is None or f <= frame + 1e-6:
            value = v
    return value


def _write_keys(ob, path, index, keys):
    """Replace a channel by [(frame, value, interpolation)] (sorted, near-duplicates merged)."""
    keys = sorted(keys, key=lambda k: k[0])
    clean = []
    for k in keys:
        if clean and k[0] - clean[-1][0] < 0.011:
            clean[-1] = k
        else:
            clean.append(k)
    fc = ch._ensure(ob, path, index)
    kps = fc.keyframe_points
    while len(kps):
        kps.remove(kps[len(kps) - 1], fast=True)
    kps.add(len(clean))
    co = np.empty(2 * len(clean), dtype=np.float32)
    co[0::2] = [k[0] for k in clean]
    co[1::2] = [k[1] for k in clean]
    kps.foreach_set("co", co)
    for kp, k in zip(kps, clean):
        kp.interpolation = k[2]
    fc.update()
    if clean:
        getattr(ob, path)[index] = clean[0][1]


# ----------------------------------------------------------------------------------------------------
# the pillager
# ----------------------------------------------------------------------------------------------------
class Pillager(ch.Character):
    """A pillager: an engine.characters.Character with the illager's body, the crossbow poses, the patrol pace,
    and (captain=True) the ominous banner on its head."""

    def __init__(self, name, parts, spec, captain=False, crossbow=True, loaded=False, collection=None):
        # kind 'villager': the illager body plan IS the villager's (IllagerModel legs = VillagerModel legs: 1.4 *
        # 0.5 per walk speed, hit box 0.6 x 1.95), so engine.undead's hurt / die flail the legs and size the poof as
        # the game does for a pillager. .species says what it is.
        super().__init__(name, "villager", parts, spec, profession=None, child=False)
        self.species = "pillager"
        self.captain = bool(captain)
        self.size = PILLAGER_SIZE
        self.eye_height = PILLAGER_EYE
        self.walk_speed = PATROL_SPEED
        self.health = HEALTH
        self.last_walk = None
        self.last_charge = None
        self.last_death = None
        crc = zlib.crc32(name.encode("utf-8"))
        self._foot = 1 if (crc >> 12) & 1 else -1
        self._first_step = 0.35 + 0.65 * float((crc >> 13) % 1000) / 999.0
        self._stride = 0.92 + 0.16 * float((crc >> 5) % 1000) / 999.0
        self._phase0 = 2.0 * math.pi * float((crc >> 3) % 1000) / 1000.0
        self._age0 = float(crc % 4000) / 10.0
        self.crossbow = bool(crossbow)
        self._shown = [(None, True)]
        self._poses = [(None, "hold" if crossbow else "neutral")]
        self._xbow = [(None, "arrow" if loaded else "standby")]
        self._head_item = [(None, self.captain)]
        self._walks = []                 # (f0, f1, arm ratio) for the NEUTRAL arm swing
        self._shots = []
        self._charge_k = {}
        for arm in (self.arm_r, self.arm_l):
            self._set_rest(arm, _ROT, 1, 0.0)
        col = parts["root"].users_collection[0]
        self.crossbows = {}
        if crossbow:
            hand = _hand_matrix()
            for state in STATES:
                ob = bpy.data.objects.new("%s_crossbow_%s" % (name, state), _crossbow_mesh(state))
                col.objects.link(ob)
                ob.parent = self.arm_r
                ob.matrix_parent_inverse = Matrix.Identity(4)
                ob.matrix_basis = hand
                ob["mc_item"] = "crossbow"
                self.crossbows[state] = ob
        self.banner = None
        if captain:
            ob = bpy.data.objects.new(name + "_banner", banner_mesh("head"))
            col.objects.link(ob)
            ob.parent = self.head
            ob.matrix_parent_inverse = Matrix.Identity(4)
            ob["mc_item"] = "white_banner"
            self.banner = ob
        self._rekey()
        # engine.undead keeps hurt / die / poof / place in step with show() (it wraps show, _rekey and place). The
        # game draws held and worn items with NO_OVERLAY: give each item a "twin" that is the SAME mesh, so the red
        # flash leaves crossbow and banner in their own colours (undead makes red twins of the body parts only).
        st = undead._state(self)
        for ob in self.items():
            twin = bpy.data.objects.new(ob.name + "_hurt", ob.data)
            col.objects.link(twin)
            twin.parent = ob
            twin.matrix_parent_inverse = Matrix.Identity(4)
            twin.hide_render = twin.hide_viewport = True
            st["twins"][ob.name] = twin
        self._bake_arms()

    def __repr__(self):
        return "<Pillager %s%s>" % (self.name, " captain" if self.captain else "")

    # ------------------------------------------------------------------ queries
    def items(self):
        """The item objects: the five crossbow states (one shown at a time) and the captain's banner."""
        return list(self.crossbows.values()) + ([self.banner] if self.banner is not None else [])

    def objects(self):
        """All objects of the rig (root first), the crossbow states and the banner."""
        obs = [self.parts["root"]] + [o for k, o in self.parts.items() if k != "root"]
        return obs + self.items()

    def crossbow_at(self, frame):
        """The crossbow model shown at `frame`: 'standby', 'pulling_0', 'pulling_1', 'pulling_2' or 'arrow' (loaded)."""
        return _at(self._xbow, frame, "standby") if self.crossbow else None

    def pose_at(self, frame):
        """The arm pose at `frame`: 'hold' (CROSSBOW_HOLD), 'charge' (CROSSBOW_CHARGE) or 'neutral'."""
        return _at(self._poses, frame, "neutral")

    def wears_banner_at(self, frame):
        """True while the ominous banner is on its head."""
        return bool(_at(self._head_item, frame, False)) and self.banner is not None

    def item_point(self, frame):
        """World centre of the crossbow at `frame` (a focus / hero target)."""
        ob = self.crossbows.get(self.crossbow_at(frame) or "standby")
        if ob is None:
            return self.eye_point(frame)
        scene = bpy.context.scene
        cur, sub = scene.frame_current, scene.frame_subframe
        whole = int(math.floor(frame))
        scene.frame_set(whole, subframe=float(frame) - whole)
        p = ob.matrix_world.translation.copy()
        scene.frame_set(cur, subframe=sub)
        return p

    def banner_top(self, frame):
        """World point at the top of the head banner's bar at `frame` (None without a banner)."""
        if self.banner is None:
            return None
        scene = bpy.context.scene
        cur, sub = scene.frame_current, scene.frame_subframe
        whole = int(math.floor(frame))
        scene.frame_set(whole, subframe=float(frame) - whole)
        mw = self.banner.matrix_world
        p = max((mw @ v.co for v in self.banner.data.vertices), key=lambda q: q.z)
        scene.frame_set(cur, subframe=sub)
        return p

    # ------------------------------------------------------------------ visibility
    def _rekey(self):
        """Write every visibility key from the events: shown (show / Stage), which crossbow state, banner worn."""
        events = sorted({int(f) for f, _v in self._shown + self._xbow + self._head_item if f is not None})
        lead = (min(events[0], 1) - 1) if events else 0
        times = [lead] + [f for f in events if f > lead]

        def write(ob, visible):
            keys = [(t, 0.0 if visible(-1e9 if i == 0 else t) else 1.0) for i, t in enumerate(times)]
            for path in _HIDE:
                fx._write(ob, path, 0, [k[0] for k in keys], [k[1] for k in keys], "CONSTANT")
            ob.hide_render = ob.hide_viewport = keys[0][1] > 0.5

        def shown(f):
            return bool(_at(self._shown, f, True))

        for key, ob in self.parts.items():
            if ob.type == "MESH":
                write(ob, shown)
        for state, ob in self.crossbows.items():
            write(ob, lambda f, s=state: shown(f) and self.crossbow_at(f) == s)
        if self.banner is not None:
            write(self.banner, lambda f: shown(f) and bool(_at(self._head_item, f, False)))

    def show(self, frame, visible=True):
        """Key the visibility of the whole pillager (rig, crossbow, banner) from `frame` on (Stage.finish calls it)."""
        f = int(round(frame))
        self._shown = [k for k in self._shown if k[0] != f] + [(f, bool(visible))]
        self._rekey()
        self._bake_arms()

    def take_banner(self, frame):
        """The banner leaves its head ON `frame` (it was dropped: drops() does this for the captain)."""
        f = int(round(frame))
        self._head_item = [k for k in self._head_item if k[0] != f] + [(f, False)]
        self._rekey()

    # ------------------------------------------------------------------ arms
    def _head_times(self, a, b):
        """Frames in [a, b] where the arms must be keyed to follow the head: its keys, and every half frame
        between two keys that move it."""
        keys = []
        for index in (0, 2):
            fc = ch._find(self.head, _ROT, index)
            if fc is not None:
                keys += [(float(kp.co.x), kp.interpolation) for kp in fc.keyframe_points]
        keys.sort()
        times = {a, b}
        for (t0, i0), (t1, _i1) in zip(keys, keys[1:]):
            if t1 < a or t0 > b:
                continue
            times.add(min(max(t0, a), b))
            times.add(min(max(t1, a), b))
            if i0 != "CONSTANT" and t1 - t0 > 0.6:
                n = int(math.ceil((t1 - t0) / 0.5))
                for j in range(1, n):
                    t = t0 + (t1 - t0) * j / n
                    if a < t < b:
                        times.add(t)
        for t, _i in keys:
            if a <= t <= b:
                times.add(t)
        return sorted(times)

    def _arm_values(self, pose, t, start):
        """(right x, right z, left x, left z) Blender euler of the arms at `t` in `pose` (begun at `start`).
        Model (xRot, yRot) -> Blender euler (x, -yRot) on channels 0 and 2."""
        if pose == "hold":
            hx = ch._val(self.head, _ROT, 0, t)                          # = model head.xRot
            hy = -ch._val(self.head, _ROT, 2, t)                         # = model head.yRot
            return (HOLD_MAIN[0] + hx, -(HOLD_MAIN[1] + hy), HOLD_OFF[0] + hx, -(HOLD_OFF[1] + hy))
        if pose == "charge":
            k = self._charge_k.get(int(round(start)), 1.0)
            f = ch._clamp((t - start) / (TICK * k) / CHARGE_TICKS, 0.0, 1.0)
            ox = CHARGE_OFF_X[0] + (CHARGE_OFF_X[1] - CHARGE_OFF_X[0]) * f
            oy = CHARGE_OFF_Y[0] + (CHARGE_OFF_Y[1] - CHARGE_OFF_Y[0]) * f
            return (CHARGE_MAIN[0], -CHARGE_MAIN[1], ox, -oy)
        ratio = 0.0                                                      # neutral: the arms swing against the legs
        for f0, f1, r in self._walks:
            if f0 <= t <= f1 + 8:
                ratio = r
        if ratio == 0.0:
            return (0.0, 0.0, 0.0, 0.0)
        return (-ch._val(self.leg_r, _ROT, 0, t) * ratio, 0.0, -ch._val(self.leg_l, _ROT, 0, t) * ratio, 0.0)

    def _bake_arms(self):
        """Rewrite the arms' channels from the pose events and the head (CROSSBOW_HOLD follows the head's yaw and
        pitch; the game snaps from one pose to the next: those are cuts a quarter frame early)."""
        events = sorted(self._poses, key=lambda e: -1e18 if e[0] is None else e[0])
        head_first = None
        for index in (0, 2):
            fc = ch._find(self.head, _ROT, index)
            if fc is not None and len(fc.keyframe_points):
                t = float(fc.keyframe_points[0].co.x)
                head_first = t if head_first is None else min(head_first, t)
        first = min([e[0] for e in events if e[0] is not None] + [head_first if head_first is not None else 1.0, 1.0]) - 1.0
        chans = [[], [], [], []]
        for i, (f, pose) in enumerate(events):
            a = first if f is None else float(f) - ch.CUT_LEAD
            nxt = events[i + 1][0] if i + 1 < len(events) else None
            b = None if nxt is None else float(nxt) - ch.CUT_LEAD - 0.03
            start = first if f is None else float(f)
            if pose == "hold":
                end = b
                if end is None:
                    last = [a]
                    for index in (0, 2):
                        fc = ch._find(self.head, _ROT, index)
                        if fc is not None and len(fc.keyframe_points):
                            last.append(float(fc.keyframe_points[-1].co.x))
                    end = max(last)
                times = self._head_times(a, max(end, a))
            elif pose == "charge":
                kk = self._charge_k.get(int(round(start)), 1.0)
                end = b if b is not None else start + CHARGE_FRAMES * kk
                times = sorted({a, max(end, a)} | {start + j * TICK * kk for j in range(CHARGE_TICKS + 1)
                                                   if a < start + j * TICK * kk < end})
            else:
                end = b
                if end is None:
                    end = max([a] + [w[1] + 8 for w in self._walks])
                times = {a, max(end, a)}
                for w0, w1, _r in self._walks:
                    for leg in (self.leg_r, self.leg_l):
                        fc = ch._find(leg, _ROT, 0)
                        if fc is not None:
                            times |= {float(kp.co.x) for kp in fc.keyframe_points if a <= kp.co.x <= end and w0 - 1 <= kp.co.x <= w1 + 9}
                times = sorted(times)
            for j, t in enumerate(times):
                vals = self._arm_values(pose, t, start)
                interp = "CONSTANT" if (b is not None and j == len(times) - 1) else "LINEAR"
                for c in range(4):
                    chans[c].append((t, vals[c], interp))
        for c, (ob, index) in enumerate(((self.arm_r, 0), (self.arm_r, 2), (self.arm_l, 0), (self.arm_l, 2))):
            keys = chans[c]
            if keys:
                keys[-1] = (keys[-1][0], keys[-1][1], "CONSTANT")
            _write_keys(ob, _ROT, index, keys)

    # ------------------------------------------------------------------ placement and head
    def place(self, frame, pos, yaw=0.0, keep_pose=False):
        """Hard cut to a spot (use at shot cuts): upright, legs together, head forward, the crossbow pose of that
        moment. Ends a flash, a knock-back or a death in progress (engine.undead's cut)."""
        super().place(frame, pos, yaw, keep_pose=keep_pose)
        self._bake_arms()

    def _aim(self, target, frame):
        """Head (yaw, pitch-up) toward a target, clamped to the game's 75 degrees of yaw and 40 of pitch."""
        if target is None:
            return 0.0, 0.0
        d = self._point(target, frame) - self.eye_point(frame)
        yaw = ch._clamp(ch._wrap(math.atan2(d.x, -d.y) - self.yaw_at(frame)), -HEAD_YAW_MAX, HEAD_YAW_MAX)
        pitch = ch._clamp(math.atan2(d.z, math.hypot(d.x, d.y)), -HEAD_PITCH_MAX, HEAD_PITCH_MAX)
        return yaw, pitch

    def look_at(self, frame, target, ease=6):
        """Turn the head toward a point / Character / Object (75 / 40 degrees at most); the crossbow follows it."""
        out = super().look_at(frame, target, ease)
        self._bake_arms()
        return out

    def track(self, frame_start, frame_end, target, step=3, ease=6):
        """Keep the head (and the crossbow) on a moving target."""
        out = super().track(frame_start, frame_end, target, step, ease)
        self._bake_arms()
        return out

    def face(self, frame, target, ease=8, keep_head=False):
        """Turn the whole body toward a target (the head re-centres)."""
        out = super().face(frame, target, ease, keep_head)
        self._bake_arms()
        return out

    def nod(self, frame):
        """Two quick nods (14 frames); the crossbow follows the head."""
        out = super().nod(frame)
        self._bake_arms()
        return out

    def shake(self, frame):
        """A left-right head turn (the crossbow follows it)."""
        f = int(frame)
        ch._offsets(self.head, _ROT, 2, f, [(3, 0.38), (8, -0.38), (13, 0.24), (18, 0.0)],
                    -HEAD_YAW_MAX, HEAD_YAW_MAX)
        self._bake_arms()
        return f + 18

    def flinch(self, frame):
        """Startled hop and duck (12 frames); the crossbow follows the head."""
        out = super().flinch(frame)
        self._bake_arms()
        return out

    def idle(self, frame_start, frame_end, seed=0):
        """The head looks about now and then (LookAtPlayerGoal / LookAtMob: a new direction, held 1-2 s), the
        crossbow with it."""
        f0, f1 = int(frame_start), int(frame_end)
        if f1 - f0 < 20:
            return
        r = pix.rng(7919 * (int(seed) + 1) + 31)
        for index, spread, lo, hi in ((2, 0.9, -HEAD_YAW_MAX, HEAD_YAW_MAX), (0, 0.12, -HEAD_PITCH_MAX, HEAD_PITCH_MAX)):
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
                t += dur + int(r.integers(24, 48))
            keys += [(f1 - back, cur), (f1, base)]
            ch._segment(self.head, _ROT, index, keys)
        self._bake_arms()

    # ------------------------------------------------------------------ crossbow
    def _state_event(self, frame, state):
        f = int(math.ceil(frame - 1e-6))
        self._xbow = [k for k in self._xbow if k[0] is None or k[0] < f] + [(f, state)]

    def _pose_event(self, frame, pose, clear_after=True):
        f = int(math.ceil(frame - 1e-6))
        self._poses = [k for k in self._poses if k[0] is None or k[0] < f] + [(f, pose)]

    def charge(self, frame_start, frame_end=None):
        """Load the crossbow (RangedCrossbowAttackGoal CHARGING): from `frame_start` the arm pose CROSSBOW_CHARGE
        (crossbow drawn back, the other hand pulling the string: animateCrossbowCharge) and the models pulling_0
        (pull < 0.58), pulling_1 (from tick 15), pulling_2 (tick 25, one tick); loaded (crossbow_arrow) and back in
        CROSSBOW_HOLD from tick 26. The game's charge is 25 ticks = 30 frames; frame_end (the first loaded frame)
        stretches or squeezes it (a film cheat: printed). Returns the first frame it is loaded."""
        if not self.crossbow:
            raise ValueError("%s has no crossbow (make_pillager(..., crossbow=True))" % self.name)
        f0 = float(int(round(frame_start)))
        game_end = f0 + (CHARGE_TICKS + 1) * TICK
        k = 1.0
        if frame_end is not None and abs(float(frame_end) - game_end) > 0.6:
            k = (float(frame_end) - f0) / ((CHARGE_TICKS + 1) * TICK)
            _note("%s.charge(%d, %d): the game loads a crossbow in 26 ticks (%.1f frames); stretched x %.2f"
                  % (self.name, f0, frame_end, (CHARGE_TICKS + 1) * TICK, k))
        def at_tick(n):
            return f0 + n * TICK * k
        self._pose_event(f0, "charge")
        self._state_event(f0, "pulling_0")
        self._state_event(at_tick(math.ceil(PULL_STEPS[0] * CHARGE_TICKS)), "pulling_1")      # tick 15
        self._state_event(at_tick(CHARGE_TICKS), "pulling_2")                                    # tick 25
        loaded = at_tick(CHARGE_TICKS + 1)
        self._state_event(loaded, "arrow")
        self._pose_event(loaded, "hold")
        self._charge_k[int(f0)] = k
        self._rekey()
        self._bake_arms()
        self.last_charge = dict(start=int(f0), loaded=int(math.ceil(loaded - 1e-6)), stretch=k,
                                pulling_1=int(math.ceil(at_tick(15) - 1e-6)), pulling_2=int(math.ceil(at_tick(25) - 1e-6)),
                                earliest_shot=int(math.ceil(loaded + ATTACK_DELAY_TICKS[0] * TICK - 1e-6)))
        return self.last_charge["loaded"]

    def shoot(self, frame, target=None, camera=None, collection=None, name=None, stage=None, shots=None):
        """Fire (RangedCrossbowAttackGoal READY_TO_ATTACK -> performRangedAttack): from `frame` the crossbow is
        empty again (standby), still held up. target = a point (or a Character: its middle) gives an ARROW flying
        the game's arc to it and sticking there (see Arrow); returns the Arrow, or None without a target.
        stage = a films.lookdev Stage: the arrow is put in st.cast and st.use'd in `shots` (a Shot or a list;
        default: the shot holding `frame`); without stage= do both yourself or Stage.finish hides it.
        The game shoots 20-39 ticks (24-47 frames) after the crossbow is loaded: an earlier shot is printed."""
        f = int(round(frame))
        if self.crossbow_at(f - 1) != "arrow":
            _note("%s.shoot(%d): the crossbow is not loaded on frame %d (call charge() first)" % (self.name, f, f - 1))
        lc = self.last_charge
        if lc is not None and lc["loaded"] <= f < lc["earliest_shot"]:
            _note("%s.shoot(%d): the game waits at least 20 ticks after loading (frame %d)" % (self.name, f, lc["earliest_shot"]))
        self._state_event(f, "standby")
        self._rekey()
        self._shots.append(f)
        if target is None:
            return None
        start = self.pos_at(f) + Vector((0.0, 0.0, PILLAGER_EYE - ARROW_EYE_DROP))
        if isinstance(target, ch.Character):
            tp = target.pos_at(f) + Vector((0.0, 0.0, 0.5 * undead.body_box(target)[1]))
        else:
            tp = ch._vec3(target)
        return shoot_arrow(start, tp, f, collection=collection, name=name or "%s_arrow_%d" % (self.name, f),
                           stage=stage, shots=shots)

    # ------------------------------------------------------------------ locomotion
    def walk(self, frame, points, speed=None, run=False, from_current=False, gait="planted", lead=None,
             first_step=None, stride=None):
        """Travel along `points` at the patrol pace (PATROL_SPEED 1.91 blocks/s; run=True: CHASE_SPEED 5.40) with
        the crossbow held up (or the arms swinging, without one); returns the end frame. gait 'planted' (soles do
        not slide; the legs open as far as the humanoid walk opens them at that speed) or 'vanilla' (the
        IllagerModel's exact half-size leg swing: the feet slide, as in the game). lead='l'|'r', first_step
        0.2..1 and stride 0.5..1.2 choose the step (planted: stride 0.5 = the game's +-15 degrees with planted
        soles, a quick 4.7-frame step); by default they come from the name (march() puts a file in step)."""
        if gait not in ("planted", "vanilla"):
            raise ValueError("gait %r: use 'planted' or 'vanilla'" % (gait,))
        if lead not in (None, "l", "r"):
            raise ValueError("lead %r: use 'l', 'r' or None" % (lead,))
        if speed is None:
            speed = CHASE_SPEED if run else self.walk_speed
        speed = float(speed)
        f0 = int(round(frame))
        f1 = ch.Character.walk(self, f0, points, speed=speed, run=False, from_current=from_current)
        n = f1 - f0
        ch._segment(self.body, _ROT, 1, [(f0, None), (max(f1, f0 + 1), 0.0)])       # no waddle
        if n <= 0:
            return f1
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
            return float(np.interp(f0 + t, stamps, acc))

        leg = self.leg_len
        per_tick = total / n * TICK
        anim = min(ANIM_PER_BLOCK * per_tick, 1.0)
        if lead is not None:
            self._foot = 1 if lead == "r" else -1
        sign = 1.0 if self._foot > 0 else -1.0
        first = self._first_step if first_step is None else ch._clamp(float(first_step), 0.2, 1.0)
        longer = self._stride if stride is None else ch._clamp(float(stride), 0.5, 1.2)
        rest_z = self._rest(self.hips, _LOC, 2)
        if gait == "vanilla":
            rate = anim / per_tick * LIMB_RATE                          # leg phase in radians per block
            amp = LEG_SWING * anim
            cycle = 2.0 * math.pi / rate
            phase = 0.0 if first_step is not None and first >= 1.0 else self._phase0

            def env(t):
                return max(0.0, min(1.0 - (1.0 - ANIM_LERP) ** (t / TICK), 1.0 - (1.0 - ANIM_LERP) ** ((n - t) / TICK)))

            def angle(t):
                return sign * amp * env(t) * math.sin(rate * dist(t) + phase)

            step = min(1.0, cycle / (total / n) / 12.0)
            times = [i * step for i in range(int(math.floor(n / step)) + 1)] + [float(n)]
            mobs._sample(self.leg_r, _ROT, 0, f0, times, lambda t: -angle(t))
            mobs._sample(self.leg_l, _ROT, 0, f0, times, angle)
            ch._segment(self.hips, _LOC, 2, [(f0, None), (f1, rest_z)])
            swing, steps, ratio = amp, 0, ARM_SWING / LEG_SWING
        else:
            want = ch._clamp(PLANTED_SWING * anim, 0.3, 1.0) * longer
            steps = max(1, int(round(total / (2.0 * leg * math.sin(want)) + 1.0 - first)))
            reach = total / (2.0 * (steps - 1 + first))
            xs, ys = [0.0], [0.0]
            for j in range(steps):
                top = (first * reach if j == 0 else reach) * (1.0 if j % 2 == 0 else -1.0)
                xs.append(xs[-1] + abs(top - ys[-1]))
                ys.append(top)
            xs.append(total)
            ys.append(0.0)
            cap = math.sin(1.2)
            swing = math.asin(min(max(abs(y) for y in ys) / leg, cap))
            cycle = 4.0 * reach

            def angle(t):
                return sign * math.asin(ch._clamp(float(np.interp(dist(t), xs, ys)) / leg, -cap, cap))

            step = min(1.0, 2.0 * reach / (total / n) / 6.0)
            times = {i * step for i in range(int(math.floor(n / step)) + 1)} | {float(n)}
            times |= {float(np.interp(x, acc, stamps)) - f0 for x in xs[1:-1]}
            times = mobs._dedupe(times)
            mobs._sample(self.leg_r, _ROT, 0, f0, times, lambda t: -angle(t))
            mobs._sample(self.leg_l, _ROT, 0, f0, times, angle)
            mobs._sample(self.hips, _LOC, 2, f0, times, lambda t: rest_z - leg * (1.0 - math.cos(angle(t))), rest=rest_z)
            if steps % 2:
                self._foot = -self._foot
            ratio = ARM_SWING / PLANTED_SWING
        self._walks = [w for w in self._walks if w[1] < f0] + [(f0, f1, ratio)]
        self.last_walk = dict(gait=gait, frames=(f0, f1), blocks=total, speed=total / n * FPS, swing=swing,
                              cycle_blocks=cycle, cycle_frames=cycle / (total / n), lead="r" if sign > 0 else "l",
                              first_step=first, stride=longer, steps=steps)
        self._bake_arms()
        return f1

    def hold(self, obj, offset=None, rotation=None):
        """A pillager holds its crossbow (make_pillager(crossbow=False) for none): anything else is refused."""
        if obj is None:
            return None
        raise ValueError("%s: a pillager holds only its crossbow (built by make_pillager); hold() is not supported" % self.name)

    # ------------------------------------------------------------------ damage
    def hurt(self, frame, attacker=None, knockback=None, max_back=None, flash=True):
        """engine.undead.hurt: red for 12 frames (crossbow and banner keep their colours), legs kick; knock-back
        only with an attacker. Returns the end frame."""
        return undead.hurt(self, frame, attacker=attacker, knockback=knockback, max_back=max_back, flash=flash)

    def fall_direction(self, frame):
        """The way the body tips over when it dies on `frame`: its LEFT (LivingEntityRenderer.setupRotations turns
        the pose by 180 - bodyRot about Y, then rolls it about the model's Z: the top goes to the entity's left).
        Facing -Y (yaw 0) that is +X (east). A unit Vector on the ground."""
        yaw = self.yaw_at(frame)
        return Vector((math.cos(yaw), math.sin(yaw), 0.0))

    def die(self, frame, camera=None, attacker=None, knockback=None, max_back=None, poof=True, seed=0,
            village=None, glow=None):
        """engine.undead.die: red, tips over to its left (fall_direction), gone with the poof on frame + 24
        (returned). camera = the Shot that films it (the poof faces it): required in a film."""
        if poof and camera is None and bpy.context.scene.camera is None:
            raise ValueError("%s.die(%d): the poof faces the camera: pass camera=<the Shot that films it>" % (self.name, frame))
        gone = undead.die(self, frame, camera=camera, attacker=attacker, knockback=knockback, max_back=max_back,
                          poof=poof, seed=seed, village=village, glow=glow)
        self.last_death = dict(frame=int(round(frame)), gone=gone)
        return gone


def make_pillager(name, captain=False, crossbow=True, loaded=False, collection=None):
    """Build a pillager (1.99 tall, feet at the origin, facing -Y, crossbow held up); captain=True wears the
    ominous banner on its head; loaded=True starts with a loaded crossbow."""
    spec = _illager_spec()
    key, sheet = pillager_sheet()
    parts = ch._build_rig(name, spec, sheet, ch._sheet_material(key, sheet), ch._collection(collection))
    return Pillager(name, parts, spec, captain=captain, crossbow=crossbow, loaded=loaded, collection=collection)


def add_pillager(st, name="pillager", captain=False, **kw):
    """A pillager registered with a films.lookdev.Stage (st.cast[name]): then st.use(shot, p), st.hero(shot, label, p)."""
    p = st.cast.get(name)
    if p is None:
        p = st.cast[name] = make_pillager(name, captain=captain, **kw)
    return p


def add_patrol(st, count=5, prefix="pillager", captain=True, **kw):
    """`count` pillagers on the Stage, the first the captain: [captain, pillager_2, ...] (names prefix_1..N)."""
    out = []
    for i in range(int(count)):
        out.append(add_pillager(st, "%s_%d" % (prefix, i + 1), captain=(captain and i == 0), **kw))
    return out


# ----------------------------------------------------------------------------------------------------
# the patrol on the march
# ----------------------------------------------------------------------------------------------------
def _poly(points, z=None):
    pts = [ch._vec3(p) for p in points]
    if z is not None:
        pts = [Vector((p.x, p.y, z if len(points[0]) < 3 else p.z)) for p in pts]
    return pts


def _subpath(poly, s0, s1):
    """The piece of a polyline between arc lengths s0 and s1 (beyond its ends it is carried on straight)."""
    seg = [(a, b, (b - a).length) for a, b in zip(poly, poly[1:])]

    def point(s):
        if s <= 0.0:
            a, b, ln = seg[0]
            return a + (b - a).normalized() * s
        acc = 0.0
        for a, b, ln in seg:
            if s <= acc + ln:
                return a.lerp(b, (s - acc) / ln) if ln > 1e-9 else a.copy()
            acc += ln
        a, b, ln = seg[-1]
        return b + (b - a).normalized() * (s - acc)

    out = [point(s0)]
    acc = 0.0
    for a, b, ln in seg:
        acc += ln
        if s0 + 1e-6 < acc < s1 - 1e-6:
            out.append(b.copy())
    out.append(point(s1))
    return out


def march(pillagers, path, frame, spacing=FILE_SPACING, speed=None, gait="planted", place=True, lead="r",
          first_step=1.0, stride=1.0):
    """A patrol in a clean file along `path` (a polyline on the ground), from `frame`: the captain (or the first)
    in front walks the whole path, every other pillager `spacing` blocks behind the one before (their starts
    carried on straight behind the path's first point), all at the patrol leader's pace (PATROL_SPEED 1.91
    blocks/s; the game's followers would walk at 2.64 and bunch up behind him), all with the same lead foot and
    step: in step. place=True places each at its start on `frame` (a cut: no pre-roll for a pillager that is in
    the shot before). gait: 'vanilla' (the game's short +-15 degree swing, feet sliding) for wide and long-lens
    shots, 'planted' (default, +-31 degrees, soles fixed) for close and side-on tracking shots; see GAIT.
    Returns the frame they stop."""
    order = sorted(pillagers, key=lambda p: 0 if getattr(p, "captain", False) else 1)
    poly = [ch._vec3(p) for p in path]
    if len(poly) < 2:
        raise ValueError("march: the path needs two points or more")
    total = sum((b - a).length for a, b in zip(poly, poly[1:]))
    d0 = poly[1] - poly[0]
    yaw0 = math.atan2(d0.x, -d0.y)
    end = int(round(frame))
    for i, p in enumerate(order):
        back = i * float(spacing)
        route = _subpath(poly, -back, total - back)
        if place:
            p.place(frame, route[0], yaw0)
        end = p.walk(frame, route, speed=PATROL_SPEED if speed is None else speed, gait=gait, lead=lead,
                     first_step=first_step, stride=stride)
    return end


# ----------------------------------------------------------------------------------------------------
# dropped items: the banner (special model) and the ominous bottle
# ----------------------------------------------------------------------------------------------------
def make_dropped_banner(name=None, collection=None, seed=0):
    """The ominous banner as an item entity (engine.mobs.DroppedItem: place / drop / animate / face / show / pick_up),
    drawn as ItemEntityRenderer draws a banner: the banner model at the 'ground' display (0.46 block tall, upright,
    turning about its pole), lifted 1/16 above the ground plus the bob."""
    col = collection if collection is not None else ch._collection(None)
    base = name or "drop_ominous_banner"
    name, n = base, 1
    while bpy.data.objects.get(name + "_root") is not None:
        n += 1
        name = "%s_%d" % (base, n)
    root = bpy.data.objects.new(name + "_root", None)
    root.empty_display_size = 0.2
    col.objects.link(root)
    spinner = bpy.data.objects.new(name + "_spin", None)
    spinner.empty_display_size = 0.1
    col.objects.link(spinner)
    spinner.parent = root
    me = banner_mesh("ground")
    ob = bpy.data.objects.new(name + "_1", me)
    col.objects.link(ob)
    ob.parent = spinner
    ob.matrix_parent_inverse = Matrix.Identity(4)
    ob["mc_item"] = "white_banner"
    lo = min(v.co.z for v in me.vertices)
    hover = -lo + mobs.ITEM_MIN_HOVER                                    # ItemEntityRenderer: -minY + 0.0625
    phase = float(pix.rng(7 * (int(seed) + 1) + 3).uniform(0.0, 2.0 * math.pi))
    item = mobs.DroppedItem(name, "white_banner", "special", root, spinner, [ob], hover, phase)
    item._seed = int(seed)
    item.depth = max(v.co.y for v in me.vertices) - min(v.co.y for v in me.vertices)
    return item


def make_dropped_bottle(name=None, collection=None, seed=0):
    """The ominous bottle as an item entity (its flat sprite item/ominous_bottle at the generated 'ground' display)."""
    return mobs.make_dropped_item("ominous_bottle", collection=collection, seed=seed, name=name or "drop_ominous_bottle")


def add_dropped_banner(st, name="ominous_banner", shot=None, **kw):
    """make_dropped_banner registered with a films.lookdev.Stage (st.cast[name]) and, with shot= (a Shot or a list
    of Shots), st.use'd there; without shot= call st.use(shot, item) yourself or Stage.finish hides it."""
    it = st.cast.get(name)
    if it is None:
        it = st.cast[name] = make_dropped_banner(name, **kw)
    if shot is not None:
        _on_stage(st, [it], 0, shot)
    return it


def add_dropped_bottle(st, name="ominous_bottle", shot=None, **kw):
    """make_dropped_bottle registered with a films.lookdev.Stage (st.cast[name]) and, with shot=, st.use'd there."""
    it = st.cast.get(name)
    if it is None:
        it = st.cast[name] = make_dropped_bottle(name, **kw)
    if shot is not None:
        _on_stage(st, [it], 0, shot)
    return it


_TOSS_K = None


def _toss_reach():
    """Blocks an item travels horizontally per (block per tick) of its initial sideways speed (linear: the vertical
    motion alone decides when it is on the ground)."""
    global _TOSS_K
    if _TOSS_K is None:
        _TOSS_K = mobs.toss_track((1.0, 0.0, TOSS[1]))[-1][1][0]
    return _TOSS_K


def drops(pillager, frame, items=None, spots=None, seed=0, stage=None, animate=240, face=None, collection=None,
          shots=None):
    """What the pillager drops on dying on `frame` (LivingEntity.die -> dropAllDeathLoot, on the killing tick,
    before the body has tipped over): a CAPTAIN drops one ominous bottle (loot table) and then the banner from his
    head (drop chance 2.0), which is gone from his head on that frame; a plain pillager killed by an anvil drops
    nothing (its crossbow falls only after a player's hit). items = DroppedItems to use (default: built here, in
    that order: bottle, banner). Each is spawned at his feet with the game's toss (+-0.1, 0.2, +-0.1 blocks per
    tick, drawn from `seed`) or, with spots=[point, ...], with the sideways speed that brings it to rest exactly
    there (beyond the game's 0.14 per tick a line is printed). stage = a films.lookdev Stage: the items go into
    st.cast AND are st.use'd in `shots` (a Shot or a list; default: the shot holding `frame`), so they show from
    `frame` on in that shot; to keep them in a later shot, st.use(later_shot, *items). Without stage= do both
    yourself, or Stage.finish hides them. animate = frames of bob and spin keyed after landing (0: none); face =
    a camera position the sprites turn their flat side to as they land. Returns the list of DroppedItems (empty
    for a plain pillager)."""
    f = int(round(frame))
    if items is None:
        if not pillager.captain:
            return []
        items = [make_dropped_bottle(pillager.name + "_bottle", collection=collection, seed=seed),
                 make_dropped_banner(pillager.name + "_banner_drop", collection=collection, seed=seed + 1)]
    items = list(items)
    feet = pillager.pos_at(f)
    k = _toss_reach()
    out = []
    for i, it in enumerate(items):
        r = pix.rng(4099 * (int(seed) + 1) + 17 * i + 5)
        if spots is not None and i < len(spots) and spots[i] is not None:
            s = ch._vec3(spots[i], feet.z)
            vx, vy = (s.x - feet.x) / k, (s.y - feet.y) / k
            if math.hypot(vx, vy) > math.hypot(TOSS[0], TOSS[0]) + 1e-6:
                _note("drops: %s lands %.2f blocks from %s's feet; the game's toss reaches %.2f at most"
                      % (it.name, math.hypot(s.x - feet.x, s.y - feet.y), pillager.name, math.hypot(TOSS[0], TOSS[0]) * k))
        else:
            vx, vy = r.uniform(-TOSS[0], TOSS[0]), r.uniform(-TOSS[0], TOSS[0])
        landed = it.drop(f, feet, velocity=(vx, vy, TOSS[1]))
        if face is not None:
            it.face(landed, face)
        if animate:
            it.animate(f, landed + int(animate))
        out.append(it)
    _on_stage(stage, out, f, shots, "the drops of " + pillager.name)
    if pillager.captain and pillager.banner is not None:
        pillager.take_banner(f)
    return out


# ----------------------------------------------------------------------------------------------------
# crushed by a falling anvil (engine.fixtures)
# ----------------------------------------------------------------------------------------------------
def anvil_damage(drop, pillager):
    """Health points the anvil of `drop` (an engine.fixtures fall() dict) takes off this pillager: the anvil's
    damage, x 0.75 while something is worn on the head (LivingEntity.hurtServer: DAMAGES_HELMET)."""
    dmg = float(drop.get("damage", 0))
    f = drop["frame_land"]
    if pillager.wears_banner_at(f):
        dmg *= 0.75
    return dmg


ANVIL_REACH = 0.49 + PILLAGER_SIZE[0] / 2.0     # FallingBlockEntity box 0.98 wide (fixtures) + the pillager's 0.3


def _under(pillager, drop):
    """True when the pillager's box overlaps the falling block's box on its landing frame (causeFallDamage)."""
    p = pillager.pos_at(int(drop["frame_land"]))
    cx, cy = drop["cell"][0] + 0.5, drop["cell"][1] + 0.5
    top = drop.get("from_cell", (0, 0, 1e9))[2]
    return abs(p.x - cx) < ANVIL_REACH and abs(p.y - cy) < ANVIL_REACH and p.z < top


def _compass(v):
    if abs(v.x) >= abs(v.y):
        return "east" if v.x > 0 else "west"
    return "north" if v.y > 0 else "south"


def crushed_by(pillager, drop, at="head", camera=None, knockback=None, max_back=None, items=True, spots=None,
               seed=0, village=None, glow=None, stage=None, face=None, shots=None, force=False):
    """Key what an anvil from engine.fixtures (a fall() / release() dict) does to the pillager under it.

    at='head': on the frame the anvil's underside passes the top of his head (drop['frame_at'](feet + 1.95)), as
    the film brief asks; at='land': on the anvil's landing frame, which is when the game deals the damage
    (FallingBlockEntity.causeFallDamage), 2-3 frames later. The damage is the anvil's (fixtures: 13 blocks = 24),
    x 0.75 for the captain while the banner is on his head; a pillager has 24 health: it dies (undead.die: red,
    tipping over TO HIS LEFT, the poof on frame + 24, and with items=True the drops()), else it is hurt (red,
    legs kick). The game knocks a mob hit by a falling block away from the block's centre (falling_anvil is not
    in no_knockback): knockback=None does that, False keeps him on his spot (cleaner, not the game).
    camera = the Shot that films the kill (the poof faces it); default with stage=: the Stage's shot holding the
    kill frame. A lethal hit with neither raises ValueError. stage = a films.lookdev Stage: the drops are put in
    st.cast and st.use'd in `shots` (default: the shot holding the kill frame), see drops().
    The pillager must stand inside the anvil's box (0.79 from the cell centre) on the LANDING frame, as the game
    checks: else ValueError (force=True keys it anyway, a cheat; crush_patrol() picks the right anvil for you).
    Returns a dict: frame, damage, lethal, gone (or None), items, cell, fall (unit Vector: the way the body tips,
    his left on the kill frame), side ('east' | 'west' | 'north' | 'south': the same as a compass word)."""
    if at not in ("head", "land"):
        raise ValueError("at %r: use 'head' or 'land'" % (at,))
    land = int(drop["frame_land"])
    feet = pillager.pos_at(land)
    if at == "head":
        frame = int(math.ceil(drop["frame_at"](feet.z + PILLAGER_SIZE[1]) - 1e-6))
    else:
        frame = land
    cell = drop["cell"]
    centre = Vector((cell[0] + 0.5, cell[1] + 0.5, feet.z))
    if not _under(pillager, drop):
        msg = ("crushed_by: on the landing frame %d %s stands at (%.2f, %.2f), outside the anvil's box over cell %s "
               "(reach %.2f): the game would not hit him" % (land, pillager.name, feet.x, feet.y, tuple(cell), ANVIL_REACH))
        if not force:
            raise ValueError(msg + ". Pick the drop over him at its landing frame (illagers.crush_patrol does), "
                             "or pass force=True to key the hit anyway")
        _note(msg + " (force=True: keyed anyway)")
    dmg = anvil_damage(drop, pillager)
    lethal = dmg >= pillager.health
    if camera is None and stage is not None:
        camera = _shot_of(stage, frame)
    if lethal and camera is None:
        raise ValueError("crushed_by: %s dies on frame %d and his poof faces the camera: pass camera=<the Shot that "
                         "films it> (or stage=st with a shot holding that frame)" % (pillager.name, frame))
    left = pillager.fall_direction(frame)
    out = dict(frame=frame, damage=dmg, lethal=lethal, gone=None, items=[], cell=tuple(cell), fall=left,
               side=_compass(left))
    attacker = None if knockback is False else centre
    kb = False if knockback is False else knockback
    if lethal:
        out["gone"] = pillager.die(frame, camera=camera, attacker=attacker, knockback=kb, max_back=max_back,
                                   seed=seed, village=village, glow=glow)
        if items:
            out["items"] = drops(pillager, frame, spots=spots, seed=seed, stage=stage, face=face, shots=shots)
    else:
        _note("crushed_by: %s takes %.1f of %.0f health from that anvil and survives (%s)"
              % (pillager.name, dmg, pillager.health, "banner on: x 0.75" if pillager.wears_banner_at(frame) else "bare-headed"))
        pillager.hurt(frame, attacker=attacker, knockback=kb, max_back=max_back)
    return out


def crush_patrol(pillagers, anvil_drops, at="head", camera=None, stage=None, knockback=None, spots=None, face=None,
                 items=True, village=None, glow=None, seed=0, shots=None):
    """crushed_by for a whole patrol under a row of falling anvils (engine.fixtures release() / fall() dicts):
    each pillager gets the anvil whose box he stands in ON THAT ANVIL'S LANDING FRAME (the earliest to land, as
    FallingBlockEntity.causeFallDamage finds him), so a file that walks on while the anvils fall is matched
    right. spots = the captain's two drop spots [bottle, banner] (see drops()); the rest is crushed_by's.
    Pillagers no anvil lands on are printed and left out. Returns {name: crushed_by's dict}."""
    plan = []
    for p in pillagers:
        under = [d for d in anvil_drops if _under(p, d)]
        if not under:
            _note("crush_patrol: no anvil lands on %s (at %s on frame %d)" % (
                p.name, tuple(round(c, 2) for c in p.pos_at(int(anvil_drops[0]["frame_land"]))) if anvil_drops else "-",
                int(anvil_drops[0]["frame_land"]) if anvil_drops else 0))
            continue
        plan.append((p, min(under, key=lambda d: d.get("time_land", d["frame_land"]))))
    out = {}
    for i, (p, d) in enumerate(plan):                       # assign first, then key: a knock-back moves him after
        out[p.name] = crushed_by(p, d, at=at, camera=camera, knockback=knockback, items=items,
                                 spots=spots if p.captain else None, seed=seed + 7 * i, village=village, glow=glow,
                                 stage=stage, face=face, shots=shots)
    return out


# ----------------------------------------------------------------------------------------------------
# the arrow (ArrowModel + ArrowRenderer, entity/projectiles/arrow.png)
# ----------------------------------------------------------------------------------------------------
def _arrow_mesh():
    """ArrowModel.createBodyLayer (32 x 32, whole mesh scaled 0.9): the 'back' square (0 x 5 x 5 at x -11, turned
    45 degrees, scaled 0.8) and two crossed 16 x 4 sheets (texture scaled 1 x 0.8: 5 texel rows) along +X, the tip
    at +X. Built in Blender units with the arrow along local +X (16 px = 1 block)."""
    me = bpy.data.meshes.get("illagers_arrow")
    if me is not None:
        return me
    mat = mc.material("entity/projectiles/arrow", alpha="CLIP")
    s = 0.9 / 16.0
    verts, faces, uvs = [], [], []

    def quad(pts, uv):
        n = len(verts)
        verts.extend(pts)
        faces.append((n, n + 1, n + 2, n + 3))
        uvs.extend(uv)

    for ang in (math.pi / 4.0, 3.0 * math.pi / 4.0):                     # cross_1, cross_2: rotation about X
        c, sn = math.cos(ang), math.sin(ang)

        def rot(x, y):
            return (x * s, y * c * s, y * sn * s)                        # model (x, y, z=0) turned about X; Blender axes

        p = [rot(-12, -2), rot(4, -2), rot(4, 2), rot(-12, 2)]
        uv = [(0 / 32, 1 - 0 / 32), (16 / 32, 1 - 0 / 32), (16 / 32, 1 - 5 / 32), (0 / 32, 1 - 5 / 32)]
        quad(p, uv)
    k = 0.8 * s
    c, sn = math.cos(math.pi / 4.0), math.sin(math.pi / 4.0)
    sq = []
    for y, z in ((-2.5, -2.5), (2.5, -2.5), (2.5, 2.5), (-2.5, 2.5)):
        sq.append((-11 * s, (y * c - z * sn) * k, (y * sn + z * c) * k))
    uv = [(0 / 32, 1 - 5 / 32), (5 / 32, 1 - 5 / 32), (5 / 32, 1 - 10 / 32), (0 / 32, 1 - 10 / 32)]
    quad(sq, uv)
    me = bpy.data.meshes.new("illagers_arrow")
    me.from_pydata(verts, [], faces)
    layer = me.uv_layers.new(name="UVMap")
    layer.data.foreach_set("uv", [x for u in uvs for x in u])
    me.materials.append(mat)
    me.update()
    return me


class Arrow:
    """A shot arrow: .object (Blender object, tip along its local +X), .frames (shot, hit), .hit (Vector), .points."""

    def __init__(self, ob, frames, hit, points):
        self.object, self.frames, self.hit, self.points = ob, frames, hit, points
        self.name = ob.name

    def objects(self):
        """The arrow's one object."""
        return [self.object]

    def show(self, frame, visible=True):
        """Per-shot switch for a Stage (st.cast[a.name] = a): never shown before its shot frame."""
        self._shown = getattr(self, "_shown", []) + [(int(round(frame)), bool(visible))]
        f_shot = self.frames[0]
        frames = sorted({f for f, _v in self._shown} | {f_shot})
        keys = [(min(frames[0], 1) - 1, 1.0)]
        for f in frames:
            vis = bool(_at(self._shown, f, True)) and f >= f_shot
            keys.append((f, 0.0 if vis else 1.0))
        for path in _HIDE:
            fx._write(self.object, path, 0, [k[0] for k in keys], [k[1] for k in keys], "CONSTANT")
        self.object.hide_render = self.object.hide_viewport = True


def arrow_track(start, target, speed=ARROW_SPEED, max_ticks=200):
    """Points per tick of an arrow shot from `start` at `speed` blocks per tick that passes through `target` (the
    lower arc): AbstractArrow per tick: move, v *= 0.99, v.y -= 0.05. None if it does not reach."""
    s, t = Vector(start), Vector(target)
    flat = Vector((t.x - s.x, t.y - s.y, 0.0))
    reach = flat.length
    if reach < 1e-6:
        return None
    ahead = flat / reach

    def fly(pitch):
        vh, vz = speed * math.cos(pitch), speed * math.sin(pitch)
        d = z = 0.0
        pts = [(0.0, 0.0)]
        for _ in range(max_ticks):
            d2, z2 = d + vh, z + vz
            if d2 >= reach:
                u = (reach - d) / max(d2 - d, 1e-12)
                pts.append((reach, z + (z2 - z) * u))
                return pts, z + (z2 - z) * u - (t.z - s.z)
            pts.append((d2, z2))
            d, z = d2, z2
            vh *= ARROW_DRAG
            vz = vz * ARROW_DRAG - ARROW_GRAVITY
        return pts, None

    prev, best = None, None
    for i in range(-170, 171):
        pitch = math.radians(i * 0.5)
        _p, err = fly(pitch)
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
    return [s + ahead * d + Vector((0.0, 0.0, z)) for d, z in best]


def shoot_arrow(start, target, frame, collection=None, name="arrow", speed=ARROW_SPEED, stage=None, shots=None):
    """An arrow leaving `start` on `frame` at the game's 1.6 blocks per tick, flying the gravity arc to `target`,
    its nose turning toward its flight 20 % per tick (AbstractArrow lerpRotation), and sticking: it stops 0.05 short
    of the hit point along its flight, the tip in the block, and quivers for 7 ticks (ArrowModel: zRot -sin(3 s) s
    degrees). Hidden before `frame`. stage = a films.lookdev Stage: put in st.cast and st.use'd in `shots` (a Shot
    or a list; default: the shot holding `frame`; an arrow already stuck when a shot starts needs shots=[that
    shot]). Returns an Arrow."""
    pts = arrow_track(start, target, speed)
    if pts is None:
        raise ValueError("shoot_arrow: %.1f blocks per tick does not reach %s from %s" % (speed, tuple(target), tuple(start)))
    col = collection if collection is not None else ch._collection(None)
    ob = bpy.data.objects.new(name, _arrow_mesh())
    col.objects.link(ob)
    ob.rotation_mode = "XYZ"                                             # roll, then pitch (Y), then yaw (Z)
    f0 = float(int(round(frame)))
    dirs = [(b - a) for a, b in zip(pts, pts[1:])]

    def angles(d):
        return math.atan2(d.y, d.x), -math.atan2(d.z, math.hypot(d.x, d.y))

    yaw, pitch = angles(dirs[0])
    keys = []
    for k, p in enumerate(pts):
        if k > 0:
            ty, tp = angles(dirs[min(k - 1, len(dirs) - 1)])
            yaw += ch._wrap(ty - yaw) * ARROW_TURN if k > 1 else 0.0
            pitch += (tp - pitch) * ARROW_TURN if k > 1 else 0.0
        keys.append((f0 + k * TICK, p, yaw, pitch))
    hit_dir = dirs[-1].normalized()
    stuck = pts[-1] - hit_dir * ARROW_BACK
    t_hit = f0 + (len(pts) - 1) * TICK
    keys[-1] = (t_hit, stuck, keys[-1][2], keys[-1][3])
    for i in range(3):
        fx._write(ob, _LOC, i, [k[0] for k in keys], [k[1][i] for k in keys], "LINEAR")
    fx._write(ob, _ROT, 2, [k[0] for k in keys], [k[2] for k in keys], "LINEAR")
    # the quiver after the hit (shakeTime 7, drawn as shake = shakeTime - partialTick: the model's zRot += -sin(shake *
    # 3) * shake degrees, which ArrowRenderer applies after its pitch: a nod of the shaft about the hit point)
    pk = [(k[0], k[3]) for k in keys]
    pitch_hit = keys[-1][3]
    for j in range(1, 2 * ARROW_SHAKE_TICKS + 1):
        sh = ARROW_SHAKE_TICKS - j / 2.0
        pk.append((t_hit + j * TICK / 2.0, pitch_hit - math.radians(-math.sin(sh * 3.0) * sh)))
    pk[len(keys) - 1] = (t_hit, pitch_hit - math.radians(-math.sin(ARROW_SHAKE_TICKS * 3.0) * ARROW_SHAKE_TICKS))
    pk.insert(len(keys) - 1, (t_hit - 0.05, keys[-2][3] + (pitch_hit - keys[-2][3]) * (1.0 - 0.05 / TICK)))
    fx._write(ob, _ROT, 1, [k[0] for k in pk], [k[1] for k in pk], "LINEAR")
    for path in _HIDE:
        fx._write(ob, path, 0, [f0 - 1.0, f0], [1.0, 0.0], "CONSTANT")
    ob.hide_render = ob.hide_viewport = True
    arrow = Arrow(ob, (int(f0), int(math.ceil(t_hit - 1e-6))), pts[-1], pts)
    _on_stage(stage, [arrow], f0, shots, "arrow " + arrow.name)
    return arrow


# ----------------------------------------------------------------------------------------------------
# self-test
# ----------------------------------------------------------------------------------------------------
def _evaluate(scene, frame):
    whole = int(math.floor(frame))
    scene.frame_set(whole, subframe=float(frame) - whole)
    bpy.context.view_layer.update()


def _check():
    """Numbers only: model, speeds, poses, crossbow states, banner, gait, march, hurt / die, anvils, drops, arrow."""
    from . import fixtures, quick

    scene = quick.reset()
    quick.setup(scene)
    cam = quick.camera(scene, (0.0, -9.0, 1.5), (0.0, 0.0, 1.0))
    ok = []

    def expect(label, cond, detail=""):
        ok.append(bool(cond))
        print("%s %-66s %s" % ("ok  " if cond else "FAIL", label, detail))

    def near(a, b, tol):
        return abs(a - b) <= tol

    def rendered(ob):
        return not ob.hide_render

    # ---- model and speeds
    cap = make_pillager("t_captain", captain=True)
    p = make_pillager("t_pillager")
    cap.place(1, (0.0, 0.0, 0.0), 0.0)
    p.place(1, (3.0, 0.0, 0.0), 0.0)
    _evaluate(scene, 1)
    rig = [o for o in p.parts.values() if o.type == "MESH"]
    zs = [(o.matrix_world @ v.co).z for o in rig for v in o.data.vertices]
    expect("pillager 1.992 tall (34 px x 0.9375), eyes 1.6575, box 0.6 x 1.95", near(max(zs), 34 * UNIT, 1e-4) and near(min(zs), 0.0, 1e-4)
           and near(p.eye_height, 1.6575, 1e-9) and p.size == (0.6, 1.95), "%.4f" % max(zs))
    expect("no hat, no crossed arms (IllagerModel hides both for a pillager)", "arms" not in p.parts and p.arms is None
           and len(rig) == 6, str(sorted(k for k, o in p.parts.items() if o.type == "MESH")))
    expect("speeds: patrol leader 1.911, follower 2.644, stroll 1.943, chase 5.396, charging 1.349 blocks/s",
           near(PATROL_SPEED, 1.9105, 1e-3) and near(FOLLOWER_SPEED, 2.6443, 1e-3) and near(STROLL_SPEED, 1.9427, 1e-3)
           and near(CHASE_SPEED, 5.3965, 1e-3) and near(CHARGING_SPEED, 1.3491, 1e-3))

    # ---- the banner: transforms, size, colours, dropped form
    mh, mg = banner_matrix("head"), banner_matrix("ground")
    expect("head banner: model px -> head px = 0.625 p + (0, -6.5, 4.375) (from the JSON and the classes)",
           all(near(mh[i][i], 0.625, 1e-6) for i in range(3)) and near(mh[1][3], -6.5, 1e-6) and near(mh[2][3], 4.375, 1e-6)
           and near(mh[0][3], 0.0, 1e-6))
    expect("ground banner: (x, y_up, z) = (p.x, -p.y - 6, -p.z) / 96", near(mg[0][0], 1 / 96.0, 1e-7) and near(mg[1][1], -1 / 96.0, 1e-7)
           and near(mg[2][2], -1 / 96.0, 1e-7) and near(mg[1][3], -1 / 16.0, 1e-7))
    bz = [(cap.banner.matrix_world @ v.co) for v in cap.banner.data.vertices]
    top = max(v.z for v in bz)
    width = max(v.x for v in bz) - min(v.x for v in bz)
    expect("captain's banner: top 3.40 above the feet, 0.73 wide (20 px x 0.625 x 0.9375), on the back of the head",
           near(top, 1.40625 + (44 * 0.625 + 6.5) * UNIT, 2e-3) and near(width, 20 * 0.625 * UNIT, 1e-3)
           and min(v.y for v in bz) > 0.16, "top %.3f width %.3f y %.3f..%.3f" % (top, width, min(v.y for v in bz), max(v.y for v in bz)))
    key, flag = banner_sheet()
    border = flag[1, 1, :3].astype(int)
    black = np.array(_rgb(DYE["black"]))
    expect("flag texture: the last layer (black border) is black at the edge; base layer white tinted 0xF9FFFE",
           np.all(np.abs(border - black * mc.texture_array("entity/banner/border")[1, 1, 0] / 255.0) <= 2), str(border))
    db = make_dropped_banner("t_drop_banner")
    h = max(v.co.z for v in db.sprite.data.vertices) - min(v.co.z for v in db.sprite.data.vertices)
    expect("dropped banner: 0.458 tall (44 px / 96), hover 0.125 (-minY + 1/16)", near(h, 44 / 96.0, 1e-3) and near(db.hover, 0.125, 1e-6),
           "%.4f %.4f" % (h, db.hover))

    # ---- CROSSBOW_HOLD follows the head; CROSSBOW_CHARGE; the models by pull
    _evaluate(scene, 1)
    r = (p.arm_r.rotation_euler[0], p.arm_r.rotation_euler[2], p.arm_l.rotation_euler[0], p.arm_l.rotation_euler[2])
    expect("CROSSBOW_HOLD at rest: right (-pi/2 + 0.1, yRot -0.3), left (-1.5, yRot 0.6)",
           near(r[0], -math.pi / 2 + 0.1, 1e-5) and near(r[1], 0.3, 1e-5) and near(r[2], -1.5, 1e-5) and near(r[3], -0.6, 1e-5), str([round(x, 4) for x in r]))
    p.look_at(20, (3.0 + 4.0, -4.0, 3.0), ease=6)
    _evaluate(scene, 30)
    hx, hz = p.head.rotation_euler[0], p.head.rotation_euler[2]
    r = (p.arm_r.rotation_euler[0], p.arm_r.rotation_euler[2], p.arm_l.rotation_euler[0], p.arm_l.rotation_euler[2])
    expect("the crossbow follows the head (arm x = pose + head pitch, arm yaw = pose + head yaw)",
           abs(hz) > 0.3 and abs(hx) > 0.05 and near(r[0], -math.pi / 2 + 0.1 + hx, 1e-4) and near(r[1], 0.3 + hz, 1e-4)
           and near(r[2], -1.5 + hx, 1e-4) and near(r[3], -0.6 + hz, 1e-4), "head %.3f %.3f" % (hx, hz))
    _evaluate(scene, 22.5)
    hx, hz = p.head.rotation_euler[0], p.head.rotation_euler[2]
    expect("... also in the middle of the head turn (half-frame samples)", near(p.arm_r.rotation_euler[2], 0.3 + hz, 3e-3)
           and near(p.arm_r.rotation_euler[0], -math.pi / 2 + 0.1 + hx, 3e-3))
    xb = p.crossbows["standby"]
    tip = (xb.matrix_world.to_3x3() @ Vector((-1.0, 0.0, 1.0))).normalized()
    p2 = make_pillager("t_aim")
    p2.place(1, (6.0, 0.0, 0.0), 0.0)
    _evaluate(scene, 1)
    tip = (p2.crossbows["standby"].matrix_world.to_3x3() @ Vector((-1.0, 0.0, 1.0))).normalized()
    plane = (p2.crossbows["standby"].matrix_world.to_3x3() @ Vector((0.0, -1.0, 0.0))).normalized()
    expect("the crossbow points forward (-Y), lying flat (its face up), at chest height",
           tip.y < -0.98 and plane.z > 0.98 and 1.2 < p2.crossbows["standby"].matrix_world.translation.z < 1.5,
           "tip %s face %s" % (tuple(round(c, 2) for c in tip), tuple(round(c, 2) for c in plane)))
    loaded = p2.charge(40)
    states = {}
    for f in (39, 40, 57, 58, 69, 70, 71, 72):
        scene.frame_set(f)
        states[f] = [s_ for s_, ob in p2.crossbows.items() if rendered(ob)]
    expect("charge: pulling_0 from frame 40, pulling_1 at tick 15 (58), pulling_2 at tick 25 (70), loaded from tick 26 (72)",
           states[39] == ["standby"] and states[40] == ["pulling_0"] and states[57] == ["pulling_0"] and states[58] == ["pulling_1"]
           and states[69] == ["pulling_1"] and states[70] == ["pulling_2"] and states[71] == ["pulling_2"] and states[72] == ["arrow"]
           and loaded == 72, str(states))
    _evaluate(scene, 40 + 12.5 * TICK)
    f = 12.5 / 25.0
    r = (p2.arm_r.rotation_euler[0], p2.arm_r.rotation_euler[2], p2.arm_l.rotation_euler[0], p2.arm_l.rotation_euler[2])
    expect("CROSSBOW_CHARGE half way: right (-0.9708, yRot -0.8), left x lerp to -pi/2, yRot lerp 0.4 -> 0.85",
           near(r[0], -0.97079635, 1e-4) and near(r[1], 0.8, 1e-4) and near(r[2], -0.97079635 + (-math.pi / 2 + 0.97079635) * f, 2e-3)
           and near(r[3], -(0.4 + 0.45 * f), 2e-3), str([round(x, 4) for x in r]))
    _evaluate(scene, 73)
    expect("loaded: back in CROSSBOW_HOLD", near(p2.arm_r.rotation_euler[0], -math.pi / 2 + 0.1, 1e-4) and p2.pose_at(73) == "hold")
    arrow = p2.shoot(100, target=(6.5, -9.0, 0.0))
    scene.frame_set(99)
    s99 = [s_ for s_, ob in p2.crossbows.items() if rendered(ob)]
    scene.frame_set(100)
    s100 = [s_ for s_, ob in p2.crossbows.items() if rendered(ob)]
    first = (arrow.points[1] - arrow.points[0]).length
    expect("shoot: standby from the shot frame; the arrow leaves at 1.6 blocks per tick and reaches its target",
           s99 == ["arrow"] and s100 == ["standby"] and near(first, 1.6, 1e-6) and (arrow.hit - Vector((6.5, -9.0, 0.0))).length < 1e-3,
           "%d ticks, hit on frame %d" % (len(arrow.points) - 1, arrow.frames[1]))
    _evaluate(scene, arrow.frames[1] + 12)
    nose = arrow.object.matrix_world.to_3x3() @ Vector((1.0, 0.0, 0.0))
    tip_at = arrow.object.matrix_world @ Vector((3.6 / 16.0, 0.0, 0.0))
    expect("the arrow sticks: nose down into the ground, tip below the surface, 0.05 back along its flight",
           nose.z < -0.05 and tip_at.z < 0.0, "nose %s tip z %.3f" % (tuple(round(c, 2) for c in nose), tip_at.z))

    # ---- gait
    def sole(c, leg):
        return leg.matrix_world @ Vector((0.0, 0.0, -c.leg_len))

    for label, gait, stride in (("planted", "planted", None), ("vanilla", "vanilla", None), ("shuffle", "planted", 0.5)):
        w = make_pillager("t_walk_" + label)
        w.place(1, (0.0, 10.0, 0.0), math.radians(90))
        endw = w.walk(1, [(0.0, 10.0, 0.0), (9.0, 10.0, 0.0)], gait=gait, stride=stride)
        info = w.last_walk
        slide, before, carrying, anchor = 0.0, None, None, 0.0
        f = 1.0
        while f < endw:
            _evaluate(scene, f)
            pts = [sole(w, w.leg_l), sole(w, w.leg_r)]
            if before is not None:
                moved = [abs(pts[i].x - before[i].x) for i in (0, 1)]
                idx = 0 if moved[0] <= moved[1] else 1
                if gait == "vanilla" or moved[idx] <= 0.2 * moved[1 - idx]:
                    if idx != carrying:
                        carrying, anchor = idx, pts[idx].x
                    slide = max(slide, abs(pts[idx].x - anchor))
            before = pts
            f += 0.125
        if label == "shuffle":
            anim = min(4.0 * PATROL_SPEED / 20.0, 1.0)
            expect("planted, stride 0.5: the game's +-%.1f deg swing with planted soles, a step every %.1f frames"
                   % (math.degrees(0.7 * anim), info["cycle_frames"] / 2),
                   slide < 0.006 and near(info["swing"], 0.7 * anim, 0.02) and 4.0 <= info["cycle_frames"] / 2 <= 5.5,
                   "drift %.4f swing %.1f deg" % (slide, math.degrees(info["swing"])))
        elif gait == "planted":
            expect("planted gait: patrol pace, the sole on the ground does not slide, a step every %.1f frames" % (info["cycle_frames"] / 2),
                   slide < 0.006 and near(info["speed"], PATROL_SPEED, 0.03) and 7.0 <= info["cycle_frames"] / 2 <= 11.0,
                   "drift %.4f swing %.1f deg" % (slide, math.degrees(info["swing"])))
        else:
            anim = min(4.0 * PATROL_SPEED / 20.0, 1.0)
            expect("vanilla gait: IllagerModel legs +-0.7 x walk speed (%.1f deg), one cycle per 2.36 blocks, feet slide" % math.degrees(0.7 * anim),
                   near(info["swing"], 0.7 * anim, 0.01) and near(info["cycle_blocks"], 2.358, 0.01) and slide > 0.1, "slide %.2f" % slide)
        _evaluate(scene, endw + 8.0)
        expect("%s: legs neutral and hips at rest afterwards" % label, near(w.leg_l.rotation_euler[0], 0.0, 1e-4)
               and near(w.hips.location[2], w._rest(w.hips, _LOC, 2), 1e-5))

    # ---- no crossbow: NEUTRAL, the arms swing against the legs (IllagerModel: arm 1.0 x speed, leg 0.7 x speed;
    #      the planted gait opens the legs to the humanoid 1.4 x speed and keeps the game's arm amplitude)
    nb = make_pillager("t_unarmed", crossbow=False)
    nb.place(1, (0.0, 14.0, 0.0), math.radians(90))
    endn = nb.walk(1, [(0.0, 14.0, 0.0), (6.0, 14.0, 0.0)])
    errs = []
    for fr in (9.0, 13.5, 20.0, 31.25):
        _evaluate(scene, fr)
        errs.append(abs(nb.arm_r.rotation_euler[0] + nb.leg_r.rotation_euler[0] / 1.4))
    _evaluate(scene, endn + 12)
    expect("no crossbow (NEUTRAL): no crossbow objects, arms swing against the legs, at rest after the walk",
           not nb.items() and max(errs) < 2e-3 and abs(nb.arm_r.rotation_euler[0]) < 1e-4, "err %.4f" % max(errs))

    # ---- the file of five
    fl = [make_pillager("t_file_%d" % i, captain=(i == 2)) for i in range(5)]
    end = march(fl, [(20.0, 0.0, 0.0), (20.0, 20.0, 0.0)], 10, spacing=2.0)
    lead = fl[2]
    _evaluate(scene, 40.0)
    order = sorted(fl, key=lambda c: -c.pos_at(40.0).y)
    gaps = [order[i].pos_at(40.0).y - order[i + 1].pos_at(40.0).y for i in range(4)]
    legs = [round(c.leg_l.rotation_euler[0], 5) for c in fl]
    _evaluate(scene, 47.5)
    legs2 = [round(c.leg_l.rotation_euler[0], 5) for c in fl]
    expect("march: the captain leads, the file 2.0 apart, in step (same leg angle), all stop on one frame",
           order[0] is lead and all(near(g, 2.0, 1e-4) for g in gaps) and len(set(legs)) == 1 and len(set(legs2)) == 1
           and abs(legs2[0]) > 0.05 and all(c.last_walk["frames"][1] == end for c in fl),
           "gaps %s legs %.3f end %d" % ([round(g, 3) for g in gaps], legs2[0], end))
    expect("march: at the patrol leader's pace, facing along the road", near(lead.last_walk["speed"], PATROL_SPEED, 0.02)
           and near(lead.yaw_at(40.0) % (2 * math.pi), math.pi, 1e-4) and near(lead.pos_at(end).y, 20.0, 1e-4))

    # ---- hurt and death through engine.undead (any Character)
    hp = make_pillager("t_hurt", captain=True)
    hp.place(1, (30.0, 0.0, 0.0), 0.0)
    undead.hurt(hp, 20)
    st = hp.__dict__[undead._STATE]
    twins = st["twins"]
    rig_twins = [twins[o.name] for o in hp.parts.values() if o.type == "MESH"]
    item_twins = [twins[o.name] for o in hp.items()]
    expect("undead.hurt: a red twin for each of the 6 body parts; crossbow and banner twins are the same mesh (NO_OVERLAY)",
           len(rig_twins) == 6 and all(t.data is not o.data for t, o in zip(rig_twins, [o for o in hp.parts.values() if o.type == "MESH"]))
           and all(t.data is o.data for t, o in zip(item_twins, hp.items())))
    scene.frame_set(25)
    red = len([t for t in rig_twins if rendered(t)])
    body = len([o for o in hp.parts.values() if o.type == "MESH" and rendered(o)])
    xbow = len([o for o in [hp.crossbows["standby"], twins[hp.crossbows["standby"].name]] if rendered(o)])
    ban = len([o for o in [hp.banner, twins[hp.banner.name]] if rendered(o)])
    scene.frame_set(32)
    red_after = len([t for t in rig_twins if rendered(t)])
    expect("hurt: red frames 20-31, the crossbow and banner drawn once all along", red == 6 and body == 0 and xbow == 1 and ban == 1 and red_after == 0,
           "red %d body %d xbow %d banner %d" % (red, body, xbow, ban))
    _evaluate(scene, 20 + TICK)
    expect("hurt: the legs kick 0.7 rad within a tick (IllagerModel = the villager's 1.4 x 0.5)", near(abs(hp.leg_l.rotation_euler[0]), 0.7, 0.01),
           "%.3f" % hp.leg_l.rotation_euler[0])
    gone = undead.die(hp, 60, camera=cam)
    _evaluate(scene, 60 + 13.5 * TICK)
    tilt = math.degrees(hp.root.rotation_euler[1])
    scene.frame_set(gone)
    left = [o.name for o in hp.objects() if o.type == "MESH" and rendered(o)] + [t.name for t in twins.values() if rendered(t)]
    expect("undead.die: flat after 13.5 ticks, gone on frame + 24 with crossbow and banner", gone == 84 and near(tilt, 90.0, 0.5) and not left,
           "tilt %.1f left %s" % (tilt, left))
    _evaluate(scene, 60 + 13.5 * TICK)
    lay = hp.head.matrix_world.translation - hp.pos_at(60)
    expect("the body tips over to its LEFT (setupRotations): facing -Y it lies toward +X, as fall_direction says",
           lay.x > 1.0 and abs(lay.y) < 0.3 and (hp.fall_direction(60) - Vector((1.0, 0.0, 0.0))).length < 1e-6,
           "neck at %s from the feet" % (tuple(round(c, 2) for c in lay),))

    # ---- crushed by anvils (engine.fixtures) and the drops
    col = ch._collection(None)
    site = fixtures.site(col)
    for x in range(40, 52):
        site.world.set(x, 0, -1, "cobblestone")

    def anvil(x, height, frame=10):
        blk = fixtures.block(site, "anvil", (x, 0, height), {"facing": "north"})
        return fixtures.fall(blk, frame=frame, world=site)

    d13 = anvil(40, 13)
    d17 = anvil(42, 17)
    d12 = anvil(44, 12)
    d13b = anvil(46, 13)
    c13 = make_pillager("t_cap13", captain=True)
    c17 = make_pillager("t_cap17", captain=True)
    p12 = make_pillager("t_p12")
    p13 = make_pillager("t_p13")
    for c, x in ((c13, 40), (c17, 42), (p12, 44), (p13, 46)):
        c.place(1, (x + 0.5, 0.5, 0.0), 0.0)
    r13 = crushed_by(c13, d13, camera=cam)
    r17 = crushed_by(c17, d17, camera=cam, spots=[(42.5, -0.9, 0.0), (43.5, -0.9, 0.0)])
    r12 = crushed_by(p12, d12, camera=cam)
    r13b = crushed_by(p13, d13b, camera=cam, at="land")
    expect("damage: captain under 13 blocks 18 (banner x 0.75, lives), under 17: 24 (dies); pillager 12: 22 (lives), 13: 24 (dies)",
           r13["damage"] == 18 and not r13["lethal"] and r17["damage"] == 24 and r17["lethal"] and r12["damage"] == 22
           and not r12["lethal"] and r13b["damage"] == 24 and r13b["lethal"],
           "%s %s %s %s" % (r13["damage"], r17["damage"], r12["damage"], r13b["damage"]))
    expect("at='head' keys the blow when the anvil passes 1.95 (before it lands); at='land' on the landing frame",
           r17["frame"] < d17["frame_land"] and r13b["frame"] == d13b["frame_land"]
           and d17["frame_at"](0.0 + 1.95) <= r17["frame"] < d17["frame_at"](1.95) + 1.0,
           "head %d land %d" % (r17["frame"], d17["frame_land"]))
    items = r17["items"]
    fd = r17["frame"]
    scene.frame_set(fd - 1)
    on_head_before = rendered(c17.banner)
    drops_before = [rendered(it.sprite) for it in items]
    scene.frame_set(fd)
    on_head_after = rendered(c17.banner) or rendered(twins_of(c17)[c17.banner.name])
    drops_after = [rendered(it.sprite) for it in items]
    rests = [it.rest_pos for it in items]
    expect("captain killed: bottle then banner drop on the killing frame, the banner leaves his head then; nothing for a pillager",
           [it.item_id for it in items] == ["ominous_bottle", "white_banner"] and on_head_before and not on_head_after
           and drops_before == [False, False] and drops_after == [True, True] and r13b["items"] == [],
           "head %s -> %s, drops %s -> %s" % (on_head_before, on_head_after, drops_before, drops_after))
    expect("drops(spots=...): each comes to rest on its spot", (rests[0] - Vector((42.5, -0.9, 0.0))).length < 0.02
           and (rests[1] - Vector((43.5, -0.9, 0.0))).length < 0.02, str([tuple(round(c, 3) for c in r_) for r_ in rests]))
    moved = (c17.pos_at(fd + 20) - c17.pos_at(fd)).length
    expect("an anvil kill knocks him away from the anvil's centre (falling_anvil is not no_knockback)", moved > 1.0, "%.2f" % moved)

    # ---- refusals: not under the anvil on its landing frame; a lethal hit with no camera to face the poof
    d18 = anvil(48, 18)
    far = make_pillager("t_far")
    far.place(1, (50.5, 0.5, 0.0), 0.0)
    nocam = make_pillager("t_nocam")
    nocam.place(1, (48.5, 0.5, 0.0), 0.0)
    errs = []
    for who, kw in ((far, dict(camera=cam)), (nocam, dict(camera=None))):
        try:
            crushed_by(who, d18, **kw)
            errs.append(None)
        except ValueError as e:
            errs.append(str(e)[:40])
    untouched = all(c_.last_death is None and len(twins_of(c_)) == len(c_.items()) for c_ in (far, nocam))
    expect("crushed_by raises (keying nothing) for a pillager outside the anvil's box and for a kill with no camera",
           all(errs) and untouched, str(errs))

    # ---- through a films.lookdev Stage that nothing patches: a file walking SOUTH under 18-block anvils
    from films import lookdev

    from . import shots as shots_mod
    film = shots_mod.Film(scene, fps=24)
    sg = lookdev.Stage(scene, film, None, None)
    s_kill, s_loot, s_other = sg.shot("t_kill", 3.0), sg.shot("t_loot", 2.0), sg.shot("t_other", 1.0)
    for y in range(-8, 16):
        site.world.set(60, y, -1, "cobblestone")
    blocks = [fixtures.block(site, "anvil", (60, y, 18), {"facing": "east"}) for y in range(-6, 12)]
    file2 = [add_pillager(sg, "t_st_cap", captain=True), add_pillager(sg, "t_st_p")]
    march(file2, [(60.5, 9.3, 0.0), (60.5, -6.0, 0.0)], 1, spacing=2.0)
    rel = 5
    rdrops = fixtures.release(blocks, rel, world=site)
    land = rdrops[0]["frame_land"]
    kp = file2[0].pos_at(land - 3)
    res = crush_patrol(file2, rdrops, stage=sg, knockback=False,
                       spots=[(kp.x + 1.0, kp.y - 0.3, 0.0), (kp.x + 1.0, kp.y + 0.5, 0.0)])
    ok_cells = []
    for p_ in file2:
        rr = res.get(p_.name)
        c_y = rr["cell"][1] + 0.5 if rr else None
        ok_cells.append(rr is not None and abs(p_.pos_at(land).y - c_y) < ANVIL_REACH and abs(p_.pos_at(rel).y - c_y) > 1.5
                        and rr["side"] == "east" and rr["lethal"])
    expect("crush_patrol: each walker gets the anvil over him on the LANDING frame (not at release), falls east",
           all(ok_cells), "%s" % {n: (r_["cell"], r_["side"], r_["damage"]) for n, r_ in res.items()})
    loot = res["t_st_cap"]["items"]
    shooter = add_pillager(sg, "t_st_shooter", loaded=True)
    shooter.place(1, (64.5, 8.0, 0.0), 0.0)
    arrows = [shooter.shoot(20, target=(64.5, 3.0, 0.0), stage=sg),
              shoot_arrow((66.5, 8.0, 1.5), (66.5, 3.0, 0.0), 12, name="t_st_arrow", stage=sg)]
    ban = add_dropped_banner(sg, "t_st_banner", shot=s_loot)
    bot = add_dropped_bottle(sg, "t_st_bottle", shot=s_loot)
    ban.place(s_loot.frame_start, (68.5, 0.5, 0.0))
    bot.place(s_loot.frame_start, (69.5, 0.5, 0.0))
    sg.use(s_kill, *file2)
    sg.use(s_kill, shooter)
    sg.use(s_loot, *loot)                                                 # the dropped pair carried into the next shot
    sg.finish()
    kf = res["t_st_cap"]["frame"]
    seen = {}
    for fr in (kf - 1, kf, s_kill.frame_end, s_loot.frame_start + 10, s_other.frame_start + 5, 30):
        scene.frame_set(fr)
        seen[fr] = ([rendered(it.sprite) for it in loot], [rendered(a.object) for a in arrows],
                    [rendered(it.sprite) for it in (ban, bot)])
    expect("Stage: the drops show from the kill frame in the kill shot (and in the next, use'd), never elsewhere",
           seen[kf - 1][0] == [False, False] and seen[kf][0] == [True, True] and seen[s_kill.frame_end][0] == [True, True]
           and seen[s_loot.frame_start + 10][0] == [True, True] and seen[s_other.frame_start + 5][0] == [False, False],
           str({f_: v_[0] for f_, v_ in seen.items()}))
    expect("Stage: arrows (shoot / shoot_arrow with stage=) show in their shot; add_dropped_*(shot=) only in that shot",
           seen[s_kill.frame_end][1] == [True, True] and seen[s_loot.frame_start + 10][1] == [False, False]
           and seen[30][2] == [False, False] and seen[s_loot.frame_start + 10][2] == [True, True]
           and seen[s_other.frame_start + 5][2] == [False, False],
           str({f_: v_[1:] for f_, v_ in seen.items()}))
    ok_all = all(ok)
    print("check %s: %d of %d" % ("ok" if ok_all else "FAILED", sum(ok), len(ok)))
    return ok_all


def twins_of(c):
    """The engine.undead twins of a character ({object name: twin}), {} when it was never hurt."""
    return c.__dict__.get(undead._STATE, {}).get("twins", {})


# ----------------------------------------------------------------------------------------------------
# proof stills: the real village (a cobblestone strip on the exit road), the golden look, films.lookdev.Stage
# ----------------------------------------------------------------------------------------------------
STRIP = (-1, 1, 27, 47)              # cells x0..x1, y0..y1 of the proof set's cobblestone strip on the exit road
STILLS = ("lineup", "captain", "banner", "walk", "march", "crossbow", "death", "crush", "loot")


def _proof_hook(b):
    """The proof set: the exit road beyond the gate paved with cobblestone (top at z 0), an anvil and a chipped
    anvil beside the road (cells (1, 34) and (1, 37)) for the loot still."""
    x0, x1, y0, y1 = STRIP
    b.allow((x0 - 1, y0 - 1, x1 + 1, y1 + 1))
    for x in range(x0, x1 + 1):
        for y in range(y0, y1 + 1):
            g = b.ground(x + 0.5, y + 0.5)
            if g is None:
                continue
            b.clear_plants(x, y)
            b.w.set(x, y, int(round(g)) - 1, "cobblestone")
            b.reserved.add((x, y))
    for x in range(x1 + 1, x1 + 10):                                     # the meadow the cameras stand in: no tufts
        for y in range(y0 - 2, y1 + 9):
            b.clear_plants(x, y)
            b.reserved.add((x, y))
    b.w.set(1, 34, 0, "anvil", {"facing": "east"})
    b.w.set(1, 37, 0, "chipped_anvil", {"facing": "east"})


def _yaw_to(src, dst):
    return math.atan2(dst[0] - src[0], -(dst[1] - src[1]))


def _shots_for(name, st, v):
    """Key one proof still on the Stage; returns its tiles [(sheet name, label, frame, (w, h))]."""
    from . import fixtures, players

    tiles = []
    if name == "lineup":
        steve = players.add_player(st, "steve", "steve")
        p1, cap, p2 = add_pillager(st, "lp_1"), add_pillager(st, "lp_cap", captain=True), add_pillager(st, "lp_2")
        cam = (8.6, 31.1, 1.25)
        for label, turn in (("front", 0.0), ("side", 90.0), ("back", 180.0)):
            s = st.shot("lineup_" + label, 0.5)
            f = s.frame_start
            for c, y in zip((steve, p1, cap, p2), (32.75, 31.65, 30.55, 29.45)):
                pos = (0.5, y, 0.0)
                c.place(f, pos, _yaw_to(pos, cam) + math.radians(turn))
            st.use(s, steve, p1, cap, p2)
            s.lens(40, 5.6)
            s.move(cam, (0.5, 31.1, 1.45))
            s.focus((0.5, 31.1, 1.4))
            st.lights(s, 1.0)
            tiles.append(("illagers_lineup", label, f + 4, (360, 640)))
    elif name == "captain":
        cap = add_pillager(st, "cc_cap", captain=True)
        s = st.shot("captain", 0.5)
        f = s.frame_start
        cam = (4.6, 29.4, 1.85)
        pos = (0.5, 31.0, 0.0)
        cap.place(f, pos, _yaw_to(pos, cam) - math.radians(20))
        cap.look_at(f, (cam[0], cam[1], 1.6), ease=0)
        st.use(s, cap)
        s.lens(45, 4.0)
        s.move(cam, (0.5, 31.0, 2.05))
        s.focus(cap.head)
        st.lights(s, 1.0)
        tiles.append(("illagers_captain", "", f + 4, (540, 960)))
    elif name == "banner":
        cap = add_pillager(st, "bc_cap", captain=True)
        pos = (0.5, 31.0, 0.0)
        for label, cam in (("front", (3.3, 30.0, 2.55)), ("back", (-2.3, 32.0, 2.6))):
            s = st.shot("banner_" + label, 0.5)
            f = s.frame_start
            cap.place(f, pos, _yaw_to(pos, (3.3, 30.0)))
            st.use(s, cap)
            s.lens(50, 4.0)
            s.move(cam, (0.5, 31.15, 2.45))
            s.focus((0.5, 31.2, 2.5))
            st.lights(s, 1.0)
            tiles.append(("illagers_banner", label, f + 4, (360, 640)))
    elif name == "walk":
        w = add_pillager(st, "wk_p")
        s = st.shot("walk", 3.0)
        f = s.frame_start
        w.place(f, (0.5, 30.0, 0.0), math.pi)
        w.walk(f, [(0.5, 30.0, 0.0), (0.5, 36.0, 0.0)])
        st.use(s, w)
        s.lens(45, 5.6)
        s.move((6.2, 32.9, 1.05), (0.5, 32.9, 1.05))
        s.focus((0.5, 32.9, 1.0))
        st.lights(s, 1.0)
        for k in range(6):
            tiles.append(("illagers_walk", "", f + 30 + 3 * k, (270, 480)))
    elif name == "march":
        patrol = add_patrol(st, 5, prefix="mp")
        s = st.shot("march", 6.5)
        f = s.frame_start
        march(patrol, [(-0.5, 33.0, 0.0), (-0.5, 47.0, 0.0)], f)
        st.use(s, *patrol)
        s.lens(35, 4.0)
        s.move((2.3, 52.5, 0.45), (-0.4, 39.0, 1.45))
        s.focus(patrol[0].head)
        st.lights(s, 1.0)
        tiles.append(("illagers_march", "", f + 138, (540, 960)))
    elif name == "crossbow":
        c = add_pillager(st, "xb_p")
        s = st.shot("crossbow", 2.5)
        f = s.frame_start
        cam = (3.15, 29.1, 1.6)
        pos = (0.5, 31.5, 0.0)
        c.place(f, pos, _yaw_to(pos, (4.6, 33.4)))
        c.look_at(f, (4.6, 33.0, 1.2), ease=0)
        loaded = c.charge(f + 4)
        st.use(s, c)
        s.lens(38, 4.0)
        s.move(cam, (0.95, 31.45, 1.3))
        s.focus((0.9, 31.4, 1.3))
        st.lights(s, 1.0)
        for label, fr in (("pulling_0", f + 10), ("pulling_1", f + 26), ("loaded", loaded + 4)):
            tiles.append(("illagers_crossbow", label, fr, (270, 480)))
        a = add_pillager(st, "xb_shooter", loaded=True)
        s2 = st.shot("arrow", 1.5)
        f2 = s2.frame_start
        a.place(f2, pos, _yaw_to(pos, (3.4, 33.2)))
        a.look_at(f2, (3.0, 33.0, 0.0), ease=0)
        arrow = a.shoot(f2 + 6, target=(2.6, 32.9, 0.0), stage=st)          # cast + use'd in s2 by stage=
        st.use(s2, a)
        s2.lens(28, 5.6)
        s2.move((5.3, 28.4, 1.0), (1.6, 32.3, 0.65))
        s2.focus((2.0, 32.5, 0.5))
        st.lights(s2, 1.0)
        tiles.append(("illagers_crossbow", "shot", arrow.frames[1] + 3, (270, 480)))
        print("arrow: shot %d, hit %d, %d ticks" % (f2 + 6, arrow.frames[1], len(arrow.points) - 1))
    elif name == "death":
        cap = add_pillager(st, "dt_cap", captain=True)
        s = st.shot("death", 4.0)
        f = s.frame_start
        cam = (5.2, 27.3, 1.0)
        pos = (1.72, 29.32, 0.0)                                         # inside the anvil's reach (0.79), off its centre
        cap.place(f, pos, _yaw_to(pos, cam) + math.radians(30))
        blk = fixtures.block(v, "anvil", (1, 29, 17), {"facing": "east"})
        st.cast[blk.name] = blk
        drop = fixtures.fall(blk, frame=f + 4, world=v)
        cap.look_at(f + 20, (1.5, 29.5, 6.0), ease=6)                    # the captain tips its head up
        res = crushed_by(cap, drop, knockback=False, spots=[(2.6, 28.65, 0.0), (2.4, 30.3, 0.0)], stage=st,
                         face=cam, village=v)                           # camera and the drops' use come from stage=
        st.use(s, cap, blk)
        print("death: falls %s (%s)" % (res["side"], tuple(round(c, 2) for c in res["fall"])))
        s.lens(32, 4.0)
        s.move(cam, (1.6, 29.6, 1.05))
        s.focus((1.5, 29.5, 1.0))
        st.lights(s, 1.0)
        hit = res["frame"]
        for label, fr in (("hit", hit), ("tipping", hit + 7), ("flat", hit + 18), ("poof", res["gone"] + 5)):
            tiles.append(("illagers_death", label, fr, (270, 480)))
        print("death: anvil lands %d, hit %d, gone %d, damage %.0f" % (drop["frame_land"], hit, res["gone"], res["damage"]))
    elif name == "crush":
        # beat 19 in small: the file of five walks SOUTH under eleven 18-block anvils, crush_patrol, nothing patched
        # by hand (the drops and the poof camera come from stage=); filmed from the EAST, the side they fall to
        patrol = add_patrol(st, 5, prefix="cr")
        s = st.shot("crush", 4.5)
        f = s.frame_start
        blocks = [fixtures.block(v, "anvil", (0, y, 18), {"facing": "east"}) for y in range(30, 41)]
        rdrops = fixtures.release(blocks, f + 10, world=v)
        land = rdrops[0]["frame_land"]
        y0 = 31.5 + PATROL_SPEED / FPS * (land - f)                       # the captain over cell y 31 on landing
        march(patrol, [(0.5, y0, 0.0), (0.5, 22.0, 0.0)], f, gait="vanilla")
        patrol[0].look_at(f + 14, (0.5, 30.0, 18.0), ease=6)              # the captain tips his head up
        cam = (4.4, 27.0, 0.8)
        kp = patrol[0].pos_at(land - 3)
        res = crush_patrol(patrol, rdrops, stage=st, knockback=False, village=v, face=cam,
                           spots=[(kp.x + 1.05, kp.y - 0.35, 0.0), (kp.x + 1.05, kp.y + 0.45, 0.0)])
        for blk in blocks:
            st.cast[blk.name] = blk
        st.use(s, *patrol)
        st.use(s, *blocks)
        s.lens(24, 4.0)
        s.move(cam, (0.4, 34.5, 1.3))
        s.focus((0.5, 33.5, 1.0))
        st.lights(s, 1.0)
        r0 = res[patrol[0].name]
        for label, fr in (("hit", r0["frame"] + 1), ("tipping", r0["frame"] + 9), ("poof", r0["gone"] + 4)):
            tiles.append(("illagers_crush", label, fr, (270, 480)))
        print("crush: release %d, land %d; %s" % (f + 10, land, ", ".join("%s cell %s %s %.1f" % (
            n, r_["cell"][:2], r_["side"], r_["damage"]) for n, r_ in res.items())))
    elif name == "loot":
        s = st.shot("loot", 3.0)
        ban = add_dropped_banner(st, "lt_banner", shot=s)
        bot = add_dropped_bottle(st, "lt_bottle", shot=s)
        f = s.frame_start
        cam = (4.3, 34.8, 0.62)
        ban.place(f, (1.40, 35.95, 0.0))
        bot.place(f, (1.78, 35.55, 0.0))
        ban.face(f + 20, cam)
        bot.face(f + 20, cam)
        ban.animate(f, s.frame_end + 40)
        bot.animate(f, s.frame_end + 40)
        s.lens(55, 3.2)
        s.move(cam, (1.55, 35.75, 0.28))
        s.focus((1.6, 35.75, 0.25))
        st.lights(s, 1.0)
        s2 = st.shot("loot_wide", 1.0)
        st.use(s2, ban, bot)
        s2.lens(30, 4.0)
        s2.move((5.6, 33.2, 0.95), (1.55, 35.9, 0.3))
        s2.focus((1.6, 35.75, 0.25))
        st.lights(s2, 1.0)
        tiles.append(("illagers_loot", "wide", s2.frame_start + 6, (360, 640)))
        tiles.append(("illagers_loot", "a", f + 20, (360, 640)))
        tiles.append(("illagers_loot", "b", f + 50, (360, 640)))
    else:
        raise ValueError("unknown still %r (use %s)" % (name, ", ".join(STILLS)))
    return tiles


def proof_film(names, extra=None):
    """The proof set as a film: (scene, film, stage, village, tiles) with the stills `names` keyed (and extra(st, v),
    a function adding more shots, -> more tiles). Used by the self-test and tools/check_illagers_stamp.py."""
    from films import lookdev

    from . import look, quick, shots, village

    scene = quick.reset()
    look.setup_render(scene, res=(540, 960), samples=16, threads=2, motion_blur=True)
    v = village.build_village(scene, seed=1, edit=_proof_hook)
    sky = look.set_time(scene, "golden", sun_azimuth=62.0, sun_elevation=27.0)
    look.setup_compositor(scene, bloom=1.0, grade="warm")
    film = shots.Film(scene, fps=24)
    st = lookdev.Stage(scene, film, v, sky)
    tiles = []
    for name in names:
        tiles += _shots_for(name, st, v)
    if extra is not None:
        tiles += extra(st, v) or []
    st.finish()
    return scene, film, st, v, tiles


def _stills(names):
    """Render every tile of the stills `names`; write out/test/illagers_<name>.png (tiles side by side)."""
    import os

    from PIL import Image

    from . import quick

    scene, film, st, v, tiles = proof_film(names)
    paths = {}
    for i, (sheet, label, frame, res) in enumerate(tiles):
        scene.render.resolution_x, scene.render.resolution_y = res
        film.goto(frame)
        path = os.path.join(quick.TEST_DIR, "%s%s.png" % (sheet, "_" + label if label else ("_%d" % i)))
        if len([t for t in tiles if t[0] == sheet]) == 1:
            path = os.path.join(quick.TEST_DIR, sheet + ".png")
        scene.render.filepath = path
        bpy.ops.render.render(write_still=True)
        print("wrote", path, "frame", frame)
        paths.setdefault(sheet, []).append(path)
    for sheet, ps in paths.items():
        if len(ps) < 2:
            continue
        ims = [Image.open(q).convert("RGB") for q in ps]
        h = max(im.height for im in ims)
        out = Image.new("RGB", (sum(im.width for im in ims) + 4 * (len(ims) - 1), h), (20, 20, 24))
        x = 0
        for im in ims:
            out.paste(im, (x, 0))
            x += im.width + 4
        path = os.path.join(quick.TEST_DIR, sheet + ".png")
        out.save(path)
        for q in ps:
            os.remove(q)
        print("wrote", path)


if __name__ == "__main__":
    _which = [a for a in sys.argv[1:]]
    if not _which or "check" in _which:
        if not _check():
            sys.exit(1)
    _names = [a for a in _which if a in STILLS]
    _bad = [a for a in _which if a not in STILLS and a != "check"]
    if _bad:
        raise SystemExit("unknown self-test part(s) %s: use check or %s" % (", ".join(_bad), ", ".join(STILLS)))
    if _names:
        _stills(_names)
