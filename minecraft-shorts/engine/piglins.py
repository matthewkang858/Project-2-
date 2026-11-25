"""PIGLINS, BABY PIGLINS and PIGLIN BRUTES, with bartering, hurt, death and the poof, for the film "In this
bastion, I'm the only one who doesn't like gold". New module; edits no other file.

Everything is transcribed from the Java Edition 26.x client classes (named next to each number below) and drawn with
the game's own textures through engine.mcassets: entity/piglin/piglin.png, piglin_brute.png, piglin_baby.png, the
item sprites, entity/equipment/humanoid[_leggings]/gold.png, particle/generic_0..7.png. Blender axes as everywhere:
+X east, +Y north, +Z up, 1 block = 1 unit, characters face -Y at yaw 0, 24 fps (the game runs 20 ticks per second:
1 tick = 1.2 frames).

PUBLIC API
    make_piglin(name, kind="piglin" | "brute", baby=False, weapon="default", armor=(), collection=None, seed=None)
        -> Piglin. Box for box from AdultPiglinModel / BabyPiglinModel (head with snout and tusks, two ear parts,
        body, arms, legs, the jacket / sleeve / pants boxes the brute's texture fills). Adults are 2.0 tall (Steve
        1.875, a villager 1.99), 1.0 wide over the arms, eyes at 1.79; a baby is 0.94 tall with a head 0.56 wide
        and eyes at 0.78. weapon 'default' = golden_sword (piglin), golden_axe (brute), nothing (baby); 'crossbow',
        any flat item id, or None. armor = any of 'helmet', 'chestplate', 'leggings', 'boots' (golden; adult
        piglins only; the ears stick out under the helmet as in the game).
    add_piglin(st, name, kind="piglin", baby=False, **kw) -> Piglin     the same, registered with a films.lookdev.Stage
    add_item(st, item_id, name=None, **kw) -> engine.mobs.DroppedItem   'gold_ingot', 'ender_pearl': on the Stage too
    Piglin (a subclass of engine.characters.Character: root / hips / body / head / ear_l / ear_r / arm_l / arm_r /
            leg_l / leg_r; .variant 'piglin' | 'brute', .baby, .weapon = the object in its hand, .armor)
        place(frame, pos, yaw=0.0)             hard cut to a spot: upright, alive, neutral pose (use at shot cuts)
        show(frame, visible=True)              keyed visibility of the whole piglin, weapon and armor included
        walk(frame, points, speed=None, run=False, from_current=False, gait="planted", swing=None, ramp=4,
             corner=0.5, dip=None) -> end frame
                                               1.94 blocks/s, run=True 5.40 (a baby 2.80 / 7.77): see GAIT. For
                                               level ground and stairs: a drop in `points` raises ValueError
        fall(frame, to_z, forward=None, speed=None) -> landing frame
                                               drop to a lower floor as the game's gravity does (two blocks in
                                               8.4 frames): into a pit, off a ledge; see FALLING
        look_at(frame, target, ease=6) / track(f0, f1, target)     head, clamped to the game's 75 / 40 degrees
        face(frame, target, ease=8) / turn(frame, yaw, ease=8)     turn the whole body on the spot
        idle(frame_start, frame_end, seed=0)   head glances, weight shifts, the game's arm bob, the ears' slow flop
        flop_ears(frame_start, frame_end)      only the ears of a piglin standing still (see EARS)
        hold(item, frame=None, hand="main")    an item id in the right (or 'off' = left) hand as ItemInHandLayer
                                               draws it; None empties the hand; with a frame it changes then
        admire(frame, item="gold_ingot", ticks=119, ease=0, keep=False) -> end frame
                                               the ADMIRING_ITEM pose with the item in the left hand (see BARTER)
        stop_admiring(frame)                   end it early (a hit does that: the ingot is lost)
        aggro(frame, on=True, ease=0)          weapon held high (arm xRot -1.8): a piglin / brute that has a target
        attack(frame) -> end frame             the melee swing, 7.2 frames (see FIGHTING)
        swing_arm(frame, side="r") -> end      the plain humanoid arm swing (the off hand's when it throws)
        aim_crossbow(frame, on=True, ease=0)   the charged crossbow held up (CROSSBOW_HOLD); weapon='crossbow'
        dance(frame_start, frame_end)          the celebration dance of PiglinModel (arms out at 70 +- 10 degrees,
                                               head, arms and body bobbing once in 11.3 frames, ears swinging)
        hurt(frame, source=None, knockback=0.4, max_back=None) -> frame it stands still again
        die(frame, source=None, knockback=0.4, max_back=None, camera=None, poof_particles=True, seed=0,
            village=None, glow=None, first=None, until=None) -> frame it is gone              (see HURT AND DEATH)
        queries: aggro_at / admiring_at / dancing_at / aiming_at / hurt_at / gone_at(frame), item_at(frame, hand),
                 item_object(key, hand), item_point(frame, hand) (world centre of the held item: focus / hero
                 target), ear_angles(age, walk_pos, walk_speed), age(frame), last_walk, last_fall, last_death
        nod / shake / flinch / raise_arm / lie_down / pos_at / yaw_at / eye_point: inherited, unchanged
    barter(piglin, ingot_item, frame, result_item="ender_pearl", toward=None, admire_ticks=119, count=1,
           world=None, floor=None, seed=0, animate=240, face=None, ease=0, lob=False) -> dict of beats  (see BARTER)
    throw_item(item, frame, thrower, aim, world=None, floor=None, seed=0) -> frame it lies still
        a PLAYER throws a DroppedItem (the gold ingot) toward a point, as the game's Q key does
    pickup(item, frame, taker) -> first frame it is gone      the game's 3-tick flight of an item to who takes it
    launch(item, frame, start, velocity, world=None, floor=None) -> frame it lies still    any item entity flight
    lob_velocity(start, target, world=None, floor=None) -> velocity for launch(): the arc that clears the blocks
        and brings an item to REST at `target` (a cheat, not the game's throw; barter(lob=True) uses it)
    in_reach(piglin, item, frame) -> bool     does the item lie where the piglin can take it
    poof(pos, frame, camera=None, size=(0.6, 1.95), count=20, seed=0, glow=None, village=None, first=None,
         until=None) -> engine.fx Burst
        the white puffs of ANY mob's death (die() calls it): pass the mob's (width, height) as size. With a Shot
        as camera they are seen in that shot only (see HURT AND DEATH)
    knock_track(strength=0.4, max_back=None) / fall_track(drop, speed=0) / air_track(velocity, height, ...) /
        item_track(start, velocity, world, floor): the game's physics as lists per tick; hand_matrix /
        item_display: the transcribed ItemInHandLayer + ItemTransform
    Constants: WALK_SPEED 1.943, CHASE_SPEED 5.396, BABY_WALK_SPEED 2.797, BABY_RUN_SPEED 7.771 (blocks/s),
    ADMIRE_TICKS 119, SWING_TICKS 6, MELEE_COOLDOWN_TICKS 20, MELEE_REACH 1.43, HURT_FRAMES 12, DEATH_FRAMES 24,
    HIT_COOLDOWN_TICKS 10, SAFE_FALL 3.0, POOF_GLOW 0.25, PLAYER_DROP_DELAY_TICKS 40, HEALTH, ATTACK_DAMAGE,
    MODEL_HEIGHT 2.0, BABY_MODEL_HEIGHT 0.9375, TICK 1.2.

USING THEM IN A FILM (films.lookdev.Stage; tools/check_piglins_film.py is this as a running six-shot film)
    brute = piglins.add_piglin(st, "brute", "brute"); pig = piglins.add_piglin(st, "pig", armor=("helmet",))
    ingot = piglins.add_item(st, "gold_ingot"); pearl = piglins.add_item(st, "ender_pearl", count=3)
    st.use(s, steve, pig, brute, ingot, pearl); st.hero(s, "pig", pig)       # hero = its head
    pig.place(f0, hole_floor, yaw); pig.look_at(f0, steve, ease=0); pig.flop_ears(f0, f0 + 60)
    steve.swing_arm(f0 + 8)
    landed = piglins.throw_item(ingot, f0 + 8, steve, aim_point, world=w)   # w = the blocks.World / Village
    ingot.animate(f0 + 8, landed + 60)                                       # bob and spin (engine.mobs)
    take = max(landed + 2, f0 + 8 + 48)                                      # nobody can take it for 40 ticks
    beats = piglins.barter(pig, ingot, take, pearl, toward=steve, admire_ticks=30, world=w, face=camera_pos)
    brute.aggro(f1); end = brute.walk(f1, path, run=True); hit = brute.attack(end); steve.flinch(end)
    back = victim.hurt(f2, source=steve); gone = victim.die(back + 6, source=steve, camera=s)   # s = the Shot
    end = pig.walk(f3, [a, past_the_rim], ramp=(4, 0)); land = pig.fall(end, pit_floor_z)        # into the pit
    KEY A PIGLIN IN FRAME ORDER, shot after shot, like every Character: a later call replaces the keys after its
    frame. place() first in every shot; it ends whatever pose, flash or death was going on. The game SNAPS into
    and out of its poses (admire, weapon high, dance, crossbow): ease=0 keys them as hard cuts a quarter frame
    early, which the films' 0.5-frame shutter never smears; pass ease=3..6 to see the arm travel instead.
    Nothing here animates a material: every change is object keys (location, rotation, visibility), which
    engine/stamp.py fingerprints correctly (checked: the same film gives the same fingerprints in two processes).

GAIT (HumanoidModel.setupAnim, LivingEntity.updateWalkAnimation, WalkAnimationState)
    The game: legs = +-cos(p * 0.6662) * 1.4 * s, arms = -+cos(p * 0.6662) * s, where s = min(4 * blocks moved per
    tick, 1) and p grows by s every tick (a baby's p counts three times). One leg cycle is therefore ALWAYS 2.36
    blocks (a baby 0.79) and the swing grows with the speed: a strolling piglin (0.35 x 0.6 squared over 1 - 0.546
    = 1.94 blocks/s) swings its legs +-31 degrees once in 29 frames and its feet slide 0.40 block per step; when
    it chases (5.40 blocks/s) the legs do the splits, +-80 degrees. gait="vanilla" keys exactly that (checked
    against the formula: 0.003 rad), no hip movement.
    gait="planted" (default; this module's choice, as engine.mobs has it for the golem): the legs open as far as
    the game opens them at that speed (1.4 * s, at most 1.1 rad; or `swing`), and the cadence follows from the leg
    length so that the standing sole stays where it was put: measured stray 0.0001-0.001 block, the sole 0.0003
    off the ground. The hips dip by leg * (1 - cos(angle)) for that (0.10 block walking). Numbers: walk 1.94
    blocks/s = +-30 degrees, a 0.75-block step every 9.8 frames; run=True 5.4 blocks/s = +-51..53 degrees, a step
    every 5.5-6.2 frames, half the dip (dip=1 is exact but bounces 0.3 block); a baby at 2.8 blocks/s +-45
    degrees, a step every 3.2 frames (its 4-px legs flicker, as in the game). A slow heavy walk: speed=1.2,
    swing=0.5. A baby faster than about 5 blocks/s would need steps shorter than 2.5 frames: they are capped and
    last_walk["slides"] says so. Arms swing against the legs with the game's amplitude for the speed, except an
    arm a pose holds (weapon high, admire, crossbow). Corners of `points` are rounded with arcs of `corner`
    blocks (stray round a right angle: 0.013); corner=0 turns on the spot. Each walk starts and ends with the feet
    together; ramp = frames of acceleration / braking (the game takes about 4).
    walk() is for LEVEL GROUND AND STAIRS (height follows the polyline): a leg steeper than one block per block
    raises ValueError, because it would glide down the drop with its legs walking. A drop is fall().

FALLING (LivingEntity.travelInAir, knockback; Attributes.SAFE_FALL_DISTANCE)
    fall(frame, to_z): from `frame` the piglin is in the air: -0.0784 blocks in the first tick, then vz = (vz -
    0.08) * 0.98 per tick, keyed tick by tick: 1 block takes 5 ticks (6 frames), 2 blocks 7 ticks (8.4 frames:
    0.08, 0.23, 0.46, 0.77, 1.15, 1.59, 2.0 down), 3 blocks 9 ticks, 4 blocks 10. Returns the landing frame.
    INTO A PIT: the game drops a mob when its 0.6-wide box has left the block, so walk until the centre is 0.3
    block PAST the rim, without braking, and fall from the walk's end frame:
        end = pig.walk(f, [start, rim + 0.3 beyond], ramp=(4, 0)); land = pig.fall(end, floor_z)
    It then carries its speed out over the pit as the game does (its last step, 0.546 of it, then 0.91 per tick):
    0.43 block from a stroll over a 2-block drop (it lands 0.73 from the rim), 1.10 from a chase; forward= sets
    that drift yourself (1 x 1 hole: forward=0.2, or it would end inside the far wall). A walk that brakes
    (default ramp) or a piglin that stands (its floor is dug away) falls straight down. In the air the legs and
    arms go on with the game's walk animation (+-19 degrees after a stroll) and settle 10 frames after landing;
    fall() can also be called in the middle of a walk. Three piglins one after another: start their walks a
    beat apart and give each its own landing spot (their boxes are 0.6 wide: a 2 x 2 pit holds four).
    Two blocks do not hurt; more than SAFE_FALL 3 blocks costs health in the game (call hurt(landing)).
    A hit while it is in the air (hurt / die with a source) pushes it sideways and does not lift it again.

EARS (AbstractPiglinModel.setupAnim)
    left ear zRot = -(30 deg + cos(1.2 * q) * a), right ear = 30 deg + cos(q) * a, q = ageInTicks * 0.1 +
    walkAnimationPos * 0.5, a = 0.08 + 0.4 * walkAnimationSpeed rad (a baby: 5 degrees on ear boxes turned 35).
    Standing: +-4.6 degrees, the right ear once in 75 frames, the left in 63. Walking: +-13.5 degrees; chasing:
    +-27.5 (measured 2.5 to 57.5 degrees), once in about 12 frames. Hit: they fly with the limbs. walk(), idle(),
    hurt() and dance() key the ears; a piglin that only stands (no idle) needs flop_ears(f0, f1), or its ears hold
    still. The phase comes from make_piglin's seed (default: the name), so no two piglins flop in step.

WHAT THEY HOLD (ItemInHandLayer.submitArmWithItem, ItemTransform.apply, HumanoidMobRenderer.getArmPose)
    The item's flat sprite (engine.mcassets.item_object) with the third-person display of its own model:
    item/handheld for sword and axe (they point forward and 10 degrees down from a hanging arm: a mob's arm takes
    no item pose, unlike the player's), item/crossbow for the crossbow (unloaded: it hangs down along the arm, its
    face forward; aim_crossbow() swaps in the loaded sprite, crossbow_arrow), item/generated for ingot and pearl
    (flat on the hand). NOT built: the crossbow's charging animation (pulling_0..2), the golden spear (26.x: 1 in
    10 sword piglins), shields, enchantment glint. Armor is the humanoid armor mesh at the piglin's deformations
    (1.02 outer, 0.5 leggings) with the game's golden equipment textures; it is never tinted by a hit (the game
    draws armor and held items with NO_OVERLAY).

BARTER (PiglinAi, StopHoldingItemIfNoLongerAdmiring, BehaviorUtils.throwItem, ItemPickupParticle)
    barter() keys what the game does, in this order, and returns dict(pickup, taken, admire=(first, end), throw,
    landed, item, rest):
    pickup  = `frame`: the ingot must lie within 1.43 blocks of the piglin's centre along x and y, at its own
              height (in_reach; ValueError otherwise). It flies to the piglin's middle in 3 ticks and is gone on
              `taken` = frame + 4, and from `frame` on the ingot is already in the piglin's left hand.
    admire  = the pose for 119 ticks = 143 frames (admire_ticks: a director may shorten it): head bowed 28.6
              degrees, left arm raised (xRot -0.9, yRot 0.5), the ingot flat on the hand 1.26 above the feet and
              0.59 in front (out/test/piglins_admire.png). The piglin stands still. Do not idle() it meanwhile.
    throw   = the end of the pose: the off hand swings and the result leaves from 0.3 below the eyes (1.49 up) at
              0.3 blocks per tick toward the point one block above `toward`'s feet; on a flat floor with the
              player 4 blocks away it lands 3.2 blocks from the piglin 23 frames later (`landed`, at `rest`).
    FROM A HOLE (item physics against the set, world=): a piglin on the floor of a 1 x 1 hole TWO deep throws the
    pearls out over the rim only if the player stands within about 1.6 blocks of the hole's centre (they land on
    the rim 1.0-1.35 from the centre, at his feet); from 2 blocks or more they hit the wall and fall back in. And
    the player's ingot must fall INTO the hole (the piglin cannot take what lies on the rim, 2 blocks above its
    feet): standing 1.2-1.6 from the centre and aiming half a block below the rim does it.
    FROM A 2 x 2 PIT two deep, with the game's throw: a piglin in the half of the pit NEXT to the player gets its
    result out only while he stands within 1.2 blocks of the pit's edge (it rests 0.5-0.9 from the edge, at his
    boots); from 1.5 blocks or more it hits the wall and falls back. A piglin in the FAR half never gets one out.
    barter(..., lob=True) is the way round that: the result is lobbed on the flattest arc that clears the rim
    (0.29-0.49 blocks per tick, the game's is 0.3; apex 0.2-0.9 above the floor outside) and comes to REST 0.45
    block from the player's feet, or exactly at `toward` when that is a point; rests are within 0.04 of the aim.
    Several results thrown to one player: give each barter another seed (0 = on the piglin's side of his feet,
    1 / 2 = 55 degrees to either side, ...), or two sprites lie in one spot. For any other launch:
    piglins.launch(item, frame, start, piglins.lob_velocity(start, target, world=w), world=w).
    The result can be any item or BLOCK id. The game's table (gameplay/piglin_bartering, weights of 469): 40 each
    'gravel', 'blackstone', 'obsidian', 'crying_obsidian', 'soul_sand', 'nether_brick', 'leather', 'fire_charge',
    'spectral_arrow'; 20 'string', 'quartz'; 10 'ender_pearl' (count 2-4), 'iron_nugget', 'dried_ghast'; rarer
    potions, 'iron_boots', 'book'. So a pearl is 1 result in 47 and gravel 1 in 12. One piglin can barter again
    and again: call barter() once per ingot, each from the throw frame of the one before (+2 frames).
    Facts for the script (all read from the classes):
    - the currency is the gold INGOT only (PiglinAi.BARTERING_ITEM); one ingot = one draw from the loot table
      gameplay/piglin_bartering: ender pearls have weight 10 of 469 (2.1 %, 2-4 pearls). Runners throw stacks.
    - a thrown ingot cannot be taken for 40 ticks (2 s); a piglin WALKS to gold it sees within 9 blocks at chase
      speed, takes it, and stands still admiring for 119 ticks (5.95 s) before it throws the result.
    - a hit while it admires ends it: the ingot is gone, nothing comes back, and for 400 ticks (20 s) after a
      player's hit it will not admire at all. hurt() and die() end the pose the same way.
    - piglins attack a player who wears NO golden armor piece on sight (NEAREST_TARGETABLE_PLAYER_NOT_WEARING_
      GOLD): the runner wears golden boots (or any golden piece). Opening a chest or mining gold nearby angers
      them all the same. Soul fire (torch, lantern, campfire) within 8 blocks drives them away.
    - BABY piglins never attack (PiglinAi.initIdleActivity: StartAttacking only for adults), run about faster than
      the adults (speed x 1.2), ride baby hoglins, DO take a gold ingot that lies near them and admire it the same
      119 ticks, and then KEEP it: PiglinAi.stopHoldingOffHandItem moves it to their main hand and throws nothing
      back (barter() with a baby does exactly that; right-clicking a baby with an ingot does nothing). Hit, they
      flee for 100 ticks. They carry no weapon and no armor.
    - BRUTES do not barter, do not admire and pick up no gold: PiglinBrute.wantsToPickUp is false for everything
      but a golden axe and PiglinBruteAi has only the activities core, idle and fight (barter() raises for a
      brute). They attack EVERY player they see within 12 blocks, golden armor or not (findNearestValidAttack
      Target takes NEAREST_VISIBLE_ATTACKABLE_PLAYER), always carry a golden axe, wear no armor, have 50 health
      (a piglin 16) and 7 attack damage before the axe (a piglin 5), never dance, never flee, and have no babies.
    - piglins dance (15 s, CELEBRATION_TIME 300) only after a hoglin hunt, with a chance of 1 in 10.
    - any piglin or brute that stays in the Overworld shakes and turns into a zombified piglin after 300 ticks.

FIGHTING (PiglinModel.setupAnim / setupAttackAnimation, AnimationUtils.swingWeaponDown, MeleeAttack)
    A piglin or brute with an attack target carries its weapon high (aggro(): arm xRot -1.8), also while it runs
    at CHASE_SPEED. attack(frame): the arm comes down to hanging and goes back up in 6 ticks = 7.2 frames (lowest
    3.6 frames in), the other arm swings back; before and after, the weapon is high. The game deals the damage on
    the tick the swing STARTS and only when the attacker's box is within 0.83 of the victim's (centres 1.43
    apart at most), once per 20 ticks (24 frames): victim.hurt(frame, source=attacker) on the same frame.
    Steve is an engine.characters Character: his reaction is flinch() (this module gives hurt() only to piglins).

HURT AND DEATH (LivingEntity.handleDamageEvent / knockback / travelInAir / tickDeath / makePoofParticles,
                LivingEntityRenderer.setupRotations, OverlayTexture, shaders/core/entity.fsh, ExplodeParticle)
    hurt(frame, source): for 10 ticks = 12 frames the skin is 0.698 x texture + 0.302 x pure red (a second set of
    meshes with the tinted texture, switched by visibility keys); the limbs fling (the game sets the walk
    animation's speed to 1.5: up to +-80 degrees, decaying); and with a source it is knocked 0.4 blocks per tick
    away from it and up: 0.96 block high after 5 ticks, back on the ground after 10 ticks (12 frames) 1.8 blocks
    away, at rest after 16 ticks 1.99 away. source=None (fire, a fall) or knockback=0: flash and fling only (use
    that in a 1 x 1 hole). max_back = blocks to a wall behind it.
    TWO HITS: the game ignores a hit that comes less than 10 ticks (12 frames) after the last one (no flash, no
    knock-back: LivingEntity.hurtServer, damageCooldownTime), so the fastest kill in two blows is hurt(f),
    die(f + 12). A sooner second hurt() or die() is keyed all the same and treated as the game treats a mob in
    the air: no second lift, the new push sideways, and it comes down on the floor it left.
    die(frame, ...): red for the whole 20 ticks, knocked back like a hit, the body tips over onto its LEFT side:
    angle = 90 degrees * sqrt((t - 1) * 0.08), flat after 13.5 ticks (16.2 frames), lying half sunk in the floor
    as in the game; on frame + 24 it is gone, weapon and armor too, and poof() starts there: 20 white puffs in its
    bounding box, 0.2-1.4 blocks wide (most under 0.6), drifting up, each running once through the sprites
    generic_7 .. generic_0 and drawn for 19-83 ticks (the last is gone at most 100 frames later). Puffs are
    camera-facing quads lit by the set plus self-light POOF_GLOW 0.25 (glow=): cream-white with the game's grey
    variation under the warm lamps of a bastion (measured 232 / 222 / 208 of 255, 0.3 % of the pixels clipped;
    engine.fx's 0.6 burns out to flat white there) and a light grey-white in flat daylight (193). Lower it in a
    set that is darker still. camera = the Shot that films the death. Bloodless: nothing else is drawn.
    PUFFS AND CUTS: a burst lasts up to 100 frames, longer than most shots, and Stage.finish() does not know it.
    So with camera=<Shot>, die() and poof() show the puffs IN THAT SHOT ONLY: none before its first frame, none
    after its last (the next shot, another place, starts clean; a snap to black is clean too).
      - a puff that is already in the air on the first frame of a flash cut: piglins.poof(spot, shot.frame_start
        - 8, camera=shot, size=(0.6, 1.8)) (a player's box): the eight frames before the cut are not shown.
      - the same scene goes on in the next shot from another angle: die(..., camera=shot, until=next.frame_end
        + 1), or until=False for no limit; first= works the same way on the other side.
      - camera=<Film or camera object>: no limit unless first / until say so. last_death["burst"].stop(frame)
        and engine.fx.stop_particles(frame) end a burst afterwards.
    NOT built: the experience orbs (5 for a piglin, 20 for a brute, when a player made the kill), the one-tick
    twitch of the limbs on the killing blow, sounds. A piglin's and a brute's loot tables are empty (data/
    minecraft/loot_table/entities/piglin.json): at most its own weapon or armor falls, which this module does
    not draw.

Self-test:  $BPY -m engine.piglins [check lineup turn armor ears walk admire barter swing dance hurt death fall lob
bastion] (no argument = everything, about 12 minutes: give one or two names per call to stay under the 300 s
limit; `check` is numbers only, 4 s). Stills: out/test/piglins_*.png. tools/check_piglins_film.py renders the
same things through films.lookdev.Stage and engine.look.setup_render (motion blur, depth of field).
"""
import bisect
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
DEG = math.pi / 180.0
_LOC, _ROT = "location", "rotation_euler"

# ---- net.minecraft.world.entity.EntityTypes.PIGLIN / PIGLIN_BRUTE: sized(0.6f, 1.95f).eyeHeight(1.79f);
#      Piglin.BABY_DIMENSIONS = EntityDimensions.scalable(0.49f, 0.98f).withEyeHeight(0.78f)
PIGLIN_WIDTH, PIGLIN_HEIGHT, PIGLIN_EYE = 0.6, 1.95, 1.79
BABY_WIDTH, BABY_HEIGHT, BABY_EYE = 0.49, 0.98, 0.78
MODEL_HEIGHT = 32.0 / 16.0           # AdultPiglinModel: head top (model y -8) above the feet (y 24), drawn at scale 1
BABY_MODEL_HEIGHT = 15.0 / 16.0      # BabyPiglinModel: head top (y 9) above the feet
MODEL_WIDTH = 16.0 / 16.0            # over the arms (model x -8 .. 8); the head is 10 px wide

# ---- net.minecraft.world.entity.Mob: getMaxHeadYRot() 75, getMaxHeadXRot() 40 (no piglin class overrides them)
HEAD_YAW_MAX = math.radians(75.0)
HEAD_PITCH_MAX = math.radians(40.0)

# ---- Piglin.createAttributes / PiglinBrute.createAttributes: MOVEMENT_SPEED 0.35 (both); Piglin.SPEED_MODIFIER_BABY
#      0.2 ADD_MULTIPLIED_BASE. PiglinAi / PiglinBruteAi: SPEED_MULTIPLIER_WHEN_IDLING 0.6 (RandomStroll.stroll(0.6)),
#      1.0 toward an attack target (SetWalkTargetFromAttackTargetIfTargetOutOfReach.create(1.0f)), toward a wanted
#      item (GoToWantedItem.create(.., 1.0f, true, 9)), when avoiding and retreating.
#      Blocks per second = 20 * (attribute * modifier)^2 / (1 - 0.546), engine.mobs.mob_speed.
SPEED_ATTRIBUTE = 0.35
BABY_SPEED_ATTRIBUTE = 0.35 * 1.2
WALK_SPEED = mobs.mob_speed(0.6, SPEED_ATTRIBUTE)                  # 1.943 blocks / s: strolling
CHASE_SPEED = mobs.mob_speed(1.0, SPEED_ATTRIBUTE)                 # 5.396 blocks / s: attacking, going for gold
BABY_WALK_SPEED = mobs.mob_speed(0.6, BABY_SPEED_ATTRIBUTE)        # 2.797 blocks / s
BABY_RUN_SPEED = mobs.mob_speed(1.0, BABY_SPEED_ATTRIBUTE)         # 7.771 blocks / s: fleeing, going for gold
HEALTH = {"piglin": 16, "brute": 50}                               # MAX_HEALTH
ATTACK_DAMAGE = {"piglin": 5, "brute": 7}                          # ATTACK_DAMAGE (before the weapon's own damage)

# ---- HumanoidModel.setupAnim / LivingEntity.updateWalkAnimation / WalkAnimationState
LIMB_FREQ = 0.6662                   # legs and arms: cos(walkAnimationPos * 0.6662 [+ pi])
LEG_SWING = 1.4                      # ... * 1.4 * walkAnimationSpeed (legs)
ARM_SWING = 1.0                      # ... * 2.0 * 0.5 * walkAnimationSpeed (arms, opposite to the leg of their side)
ANIM_PER_BLOCK = 4.0                 # walkAnimationSpeed -> min(4 * blocks per tick, 1); position += speed per tick
ANIM_SMOOTH = 0.4                    # WalkAnimationState.update(target, 0.4, ..): speed += (target - speed) * 0.4
BABY_ANIM_SCALE = 3.0                # ... update(.., isBaby() ? 3.0f : 1.0f): a baby's position counts three times
VANILLA_CYCLE = 2.0 * math.pi / LIMB_FREQ / ANIM_PER_BLOCK        # 2.358 blocks per leg cycle below 5 blocks / s
BOB_Z, BOB_Z_RATE, BOB_X, BOB_X_RATE = 0.05, 0.09, 0.05, 0.067     # AnimationUtils.bobModelPart (the idle arm bob)

# ---- AbstractPiglinModel.setupAnim: the ears
ADULT_EAR_DEGREES = 30.0             # AdultPiglinModel.getDefaultEarAngleInDegrees
BABY_EAR_DEGREES = 5.0               # BabyPiglinModel (its ear boxes are themselves turned 0.6109 rad = 35 degrees)
EAR_AGE_RATE = 0.1                   # phase = ageInTicks * 0.1 + walkAnimationPos * 0.5
EAR_WALK_RATE = 0.5
EAR_LEFT_RATE = 1.2                  # left ear: cos(phase * 1.2), right ear: cos(phase)
EAR_FLOP = 0.08                      # amplitude = 0.08 + walkAnimationSpeed * 0.4 radians
EAR_FLOP_WALK = 0.4

# ---- PiglinModel.setupAnim / PiglinArmPose
ADMIRE_HEAD_PITCH = 0.5              # ADMIRING_ITEM: head.xRot = 0.5 (28.6 degrees down), head.yRot = 0
ADMIRE_ARM_PITCH = -0.9              # the off-hand arm: xRot = -0.9, yRot = +0.5 (left arm) / -0.5 (right arm)
ADMIRE_ARM_YAW = 0.5
HOLD_HIGH = -1.8                     # ATTACKING_WITH_MELEE_WEAPON while not swinging: main arm xRot = -1.8
DANCE_PERIOD = 60.0                  # DANCING: t = ageInTicks / 60, see Piglin.dance
CROSSBOW_HOLD = dict(main=(-math.pi / 2.0 + 0.1, -0.3), off=(-1.5, 0.6))   # AnimationUtils.animateCrossbowHold

# ---- AnimationUtils.swingWeaponDown (the melee swing of ATTACKING_WITH_MELEE_WEAPON) / SwingAnimation.DEFAULT
SWING_TICKS = 6                      # SwingAnimation.DEFAULT = (WHACK, 6 ticks); axes and swords use the default
SWING_MAIN = (-1.8849558, 0.15, 0.09, 2.2)     # main arm xRot = -1.885 + cos(age * 0.09) * 0.15 + f * 2.2 - g * 0.4
SWING_OFF = (0.0, 0.5, 0.19, 1.2)              # other arm xRot = cos(age * 0.19) * 0.5 + f * 1.2 - g * 0.4
SWING_ARM_YAW = 0.15707964           # main arm yRot +0.157 (right) and the other arm -0.157
MELEE_COOLDOWN_TICKS = 20            # MeleeAttack.create(20): one swing a second; the hit lands as the swing starts
MELEE_REACH = 0.3 + (math.sqrt(2.04) - 0.6) + 0.3      # Mob.isWithinMeleeAttackRange: boxes 0.83 apart at most

# ---- PiglinAi / BehaviorUtils.throwItem / ItemPickupParticle / LivingEntity.createItemStackToDrop
ADMIRE_TICKS = 119                   # PiglinAi.ADMIRE_DURATION: the ADMIRING_ITEM memory expires after 119 ticks
PICKUP_TICKS = 3                     # ItemPickupParticle.LIFE_TIME: the item flies to its taker in 3 ticks, t squared
PICKUP_REACH = 1.0                   # Mob.ITEM_PICKUP_REACH (1, 0, 1): boxes inflated one block sideways
THROW_SPEED = 0.3                    # BehaviorUtils.throwItem: normalize(target - position) * 0.3 blocks per tick
THROW_BELOW_EYE = 0.3                # ... spawned at eye height - 0.3 (LivingEntity.createItemStackToDrop too)
THROW_TARGET_UP = 1.0                # PiglinAi.throwItemsTowardPlayer: target = the player's position + (0, 1, 0)
PLAYER_DROP_SPEED = 0.3              # LivingEntity.createItemStackToDrop: look vector * 0.3 + 0.1 up, tiny jitter
PLAYER_DROP_UP = 0.1
PLAYER_DROP_DELAY_TICKS = 40         # ... setPickUpDelay(40): nobody can take a thrown item for 2 seconds
BARTER_DELAY_TICKS = 10              # ItemEntity.setDefaultPickUpDelay(): the barter result, half a second
ITEM_BOX = 0.25                      # EntityTypes.ITEM: sized(0.25f, 0.25f)
ITEM_GRAVITY, ITEM_DRAG = mobs.ITEM_GRAVITY, mobs.ITEM_DRAG

# ---- LivingEntity.handleDamageEvent / knockback / travelInAir / tickDeath / makePoofParticles, LivingEntityRenderer
HURT_TICKS = 10                      # hurtDuration = hurtTime = 10: the red overlay (hasRedOverlay = hurtTime > 0)
HURT_FRAMES = int(round(HURT_TICKS * TICK))            # 12
HURT_COLOUR = (1.0, 0.0, 0.0)        # OverlayTexture: red rows = 0xB2FF0000 (ARGB)
HURT_MIX = 0xB2 / 255.0              # entity.fsh: color.rgb = mix(overlay.rgb, color.rgb, overlay.a): 0.698 texture
HURT_ANIM_SPEED = 1.5                # handleDamageEvent: walkAnimation.setSpeed(1.5f): the limbs fling
KNOCKBACK = 0.4                      # LivingEntity.hurtServer: knockback(0.4, dx, dz) away from the attacker
KNOCK_UP_MAX = 0.4                   # ... vertical = min(0.4, vy / 2 + strength) when on the ground
REST_FALL = -0.0784                  # the vertical speed of a mob standing still: (0 - 0.08) * 0.98
GRAVITY = 0.08                       # LivingEntity.getDefaultGravity, blocks per tick^2
AIR_DRAG = 0.91                      # travelInAir: horizontal speed * 0.91 in the air, * 0.6 * 0.91 on the ground
GROUND_DRAG = mobs.GROUND_DRAG
DEATH_TICKS = 20                     # tickDeath: removed (entity event 60) when deathTime reaches 20
DEATH_FRAMES = int(round(DEATH_TICKS * TICK))          # 24
DEATH_FLIP = math.radians(90.0)      # LivingEntityRenderer.getFlipDegrees; setupRotations: Z rotation of
DEATH_RATE = 1.6 / 20.0              #   sqrt((deathTime - 1) / 20 * 1.6) * 90 degrees, capped at 1: flat at 13.5 ticks
POOF_COUNT = 20                      # makePoofParticles: 20 x ParticleTypes.POOF
POOF_SPRITES = tuple("particle/generic_%d" % i for i in range(7, -1, -1))     # particles/poof.json, in that order
POOF_GRAVITY = -0.1                  # ExplodeParticle: gravity -0.1 (it rises 0.004 blocks per tick^2), friction 0.9
POOF_FRICTION = 0.9
POOF_GLOW = 0.25                     # this module's choice: self-light of a puff (the game draws a particle at the
#                                      light level of its place; engine.fx's 0.6 burns out in a dim bastion)
FLY_SPEED = 0.02                     # LivingEntity.getFlyingSpeed: in the air the AI's input counts 0.02 (ground: speed)
SAFE_FALL = 3.0                      # Attributes.SAFE_FALL_DISTANCE: a fall hurts from more than 3 blocks
HIT_COOLDOWN_TICKS = 10              # LivingEntity.hurtServer: damageCooldownTime = 20, and a hit while it is above 10
#                                      gives no flash and no knock-back: 10 ticks (12 frames) between two hits

# ---- ItemInHandLayer.submitArmWithItem: translate(+-a / 16, b / 16, c / 16) after rotate X -90, rotate Y 180
HAND_OFFSET = (1.0, 2.0, -10.0)
BABY_HAND_OFFSET = (0.0, 1.0, -4.5)  # useBabyOffset
# ---- LayerDefinitions: PiglinModel.createArmorMeshSet(INNER_ARMOR_DEFORMATION 0.5, new CubeDeformation(1.02))
ARMOR_OUTER = 1.02
ARMOR_INNER = 0.5
ARMOR_LEG = -0.1                     # HumanoidModel.createBaseArmorMesh: the legs' boxes .extend(-0.1)
ARMOR_TEXTURES = {"helmet": "entity/equipment/humanoid/gold", "chestplate": "entity/equipment/humanoid/gold",
                  "leggings": "entity/equipment/humanoid_leggings/gold", "boots": "entity/equipment/humanoid/gold"}
TEXTURES = {("piglin", False): "entity/piglin/piglin", ("brute", False): "entity/piglin/piglin_brute",
            ("piglin", True): "entity/piglin/piglin_baby"}        # PiglinRenderer.getTextureLocation
WEAPONS = {"piglin": "golden_sword", "brute": "golden_axe"}        # Piglin.createSpawnWeapon (half of them: a
#                                                                    crossbow; 1 in 10 of the others a golden spear),
#                                                                    PiglinBrute.populateDefaultEquipmentSlots
_SPRITES = {"crossbow": "crossbow_standby", "crossbow_loaded": "crossbow_arrow"}    # item key -> item texture
_MODELS = {"crossbow": "crossbow", "crossbow_loaded": "crossbow_arrow"}             # item key -> item model

# ---- this module's choices (the planted gait and the rounded corners, as engine.mobs has them for the golem)
PLANTED_MAX = 1.1                    # radians: the widest leg swing of the planted gait (the game's 1.4 is a split)
PLANTED_MIN = 0.12
MIN_STEP_FRAMES = 2.5                # no step is keyed shorter than this (a baby at full speed): its feet then slide
CORNER_RADIUS = 0.5                  # blocks: walk() rounds the corners of its polyline
SHARP_TURN_FRAMES = 8.0
EAR_BLEND = 6.0                      # frames over which ears that stood still join the game's flop again
STAIR_SLOPE = 1.0                    # walk(): the steepest leg it takes (stairs: a block up per block); beyond: fall()
LOB_SHORT = 0.45                     # barter(lob=True): the result comes to rest this far from the player's feet
LOB_LOFT_TICKS = 2                   # ... on an arc two ticks longer than the flattest that clears the blocks


# ----------------------------------------------------------------------------------------------------
# the models
# ----------------------------------------------------------------------------------------------------
def _piglin_spec():
    """net.minecraft.client.model.monster.piglin.AdultPiglinModel.createBodyLayer(): PlayerModel.createMesh(NONE,
    false) (body, arms, legs and their jacket / sleeve / pants boxes) with the head of AbstractPiglinModel.addHead
    (head, snout, two tusks, two ears) and no hat; LayerDefinition 64 x 64. LayerDefinitions puts no MeshTransformer
    on it and PiglinRenderer has no scale(): drawn at scale 1 (32 px = 2 blocks to the top of the head)."""
    C, P = ch._cube, ch._pose
    return dict(
        tex=(64, 64), scale=1.0, hip=12.0, top=-8.0, eye=24.0 - PIGLIN_EYE * 16.0, back=2.0, sleep_eye=PIGLIN_EYE,
        parts=[
            dict(name="body", parent="hips", pivot=(0, 12, 0), groups=[([P(0, -12, 0)], [
                C(16, 16, -4, 0, -2, 8, 12, 4),
                C(16, 32, -4, 0, -2, 8, 12, 4, grow=0.25)])]),              # jacket
            # head 10 x 8 x 8, snout 4 x 4 x 1, left tusk (2, 4) and right tusk (2, 0) 1 x 2 x 1
            dict(name="head", parent="body", pivot=(0, 0, 0), groups=[([], [
                C(0, 0, -5, -8, -4, 10, 8, 8),
                C(31, 1, -2, -4, -5, 4, 4, 1),
                C(2, 4, 2, -2, -5, 1, 2, 1),
                C(2, 0, -3, -2, -5, 1, 2, 1)])]),
            # ears: PartPose.offsetAndRotation(+-4.5, -6, 0, 0, 0, -+0.5235988); 1 x 5 x 4
            dict(name="ear_l", parent="head", pivot=(4.5, -6, 0), rot=(0, 0, -ADULT_EAR_DEGREES * DEG),
                 groups=[([], [C(51, 6, 0, 0, -2, 1, 5, 4)])]),
            dict(name="ear_r", parent="head", pivot=(-4.5, -6, 0), rot=(0, 0, ADULT_EAR_DEGREES * DEG),
                 groups=[([], [C(39, 6, -1, 0, -2, 1, 5, 4)])]),
            dict(name="arm_r", parent="body", pivot=(-5, 2, 0), groups=[([], [
                C(40, 16, -3, -2, -2, 4, 12, 4),
                C(40, 32, -3, -2, -2, 4, 12, 4, grow=0.25)])]),             # right_sleeve
            dict(name="arm_l", parent="body", pivot=(5, 2, 0), groups=[([], [
                C(32, 48, -1, -2, -2, 4, 12, 4),
                C(48, 48, -1, -2, -2, 4, 12, 4, grow=0.25)])]),             # left_sleeve
            # (the legs overlap by 0.2 px at the centre line, as the player's: xclip trims each at x = 0)
            dict(name="leg_r", parent="hips", pivot=(-1.9, 12, 0), xclip=(None, 1.9), groups=[([], [
                C(0, 16, -2, 0, -2, 4, 12, 4),
                C(0, 32, -2, 0, -2, 4, 12, 4, grow=0.25)])]),               # right_pants
            dict(name="leg_l", parent="hips", pivot=(1.9, 12, 0), xclip=(-1.9, None), groups=[([], [
                C(16, 48, -2, 0, -2, 4, 12, 4),
                C(0, 48, -2, 0, -2, 4, 12, 4, grow=0.25)])]),               # left_pants
        ])


def _baby_spec():
    """net.minecraft.client.model.monster.piglin.BabyPiglinModel.createBodyLayer() (26.x has its own baby model and
    texture, 64 x 64, drawn unscaled): no tusks, no overlay boxes, ears on an extra joint."""
    C, P = ch._cube, ch._pose
    turn = 0.6109
    return dict(
        tex=(64, 64), scale=1.0, hip=20.0, top=9.0, eye=24.0 - BABY_EYE * 16.0, back=1.5, sleep_eye=BABY_EYE,
        parts=[
            # body: PartPose.offset(0, 18, -0.5); 6 x 5 x 3
            dict(name="body", parent="hips", pivot=(0, 20, 0), groups=[([P(0, -2, -0.5)], [
                C(0, 13, -3, -3, -1, 6, 5, 3)])]),
            # head: PartPose.offset(0, 15, 0); snout 3 x 3 x 1 and head 9 x 6 x 7
            dict(name="head", parent="body", pivot=(0, 15, 0), groups=[([], [
                C(21, 30, -1.5, -3, -4.5, 3, 3, 1),
                C(0, 0, -4.5, -6, -3.5, 9, 6, 7)])]),
            # ears: PartPose.offset(+-4.2, -4, 0) with the box on offsetAndRotation(+-1, 1.75, 0, 0, 0, -+0.6109)
            dict(name="ear_l", parent="head", pivot=(4.2, 11, 0), rot=(0, 0, -BABY_EAR_DEGREES * DEG),
                 groups=[([P(1, 1.75, 0, rz=-turn)], [C(0, 21, -0.5, -3, -2, 1, 6, 4)])]),
            dict(name="ear_r", parent="head", pivot=(-4.2, 11, 0), rot=(0, 0, BABY_EAR_DEGREES * DEG),
                 groups=[([P(-1, 1.75, 0, rz=turn)], [C(18, 13, -0.5, -3, -2, 1, 6, 4)])]),
            dict(name="arm_l", parent="body", pivot=(4, 15, 0), groups=[([], [C(28, 13, -1, 0, -1.5, 2, 5, 3)])]),
            dict(name="arm_r", parent="body", pivot=(-4, 15, 0), groups=[([], [C(10, 30, -1, 0, -1.5, 2, 5, 3)])]),
            dict(name="leg_r", parent="hips", pivot=(-1.5, 20, 0), groups=[([], [C(22, 23, -1.5, 0, -1.5, 3, 4, 3)])]),
            dict(name="leg_l", parent="hips", pivot=(1.5, 20, 0), groups=[([], [C(10, 23, -1.5, 0, -1.5, 3, 4, 3)])]),
        ])


def _armor_parts(piece):
    """[(rig part, part spec)] of one golden armor piece: the boxes of HumanoidModel.createBaseArmorMesh (the plain
    humanoid mesh with the legs .extend(-0.1)) at the piglin's deformations, 1.02 for helmet, chestplate and boots
    and 0.5 for the leggings, kept per slot as ADULT_ARMOR_PARTS_PER_SLOT says (texture 64 x 32)."""
    C, P = ch._cube, ch._pose
    o, i = ARMOR_OUTER, ARMOR_INNER
    if piece == "helmet":
        return [("head", dict(groups=[([], [C(0, 0, -4, -8, -4, 8, 8, 8, grow=o),
                                            C(32, 0, -4, -8, -4, 8, 8, 8, grow=o + 0.5)])]))]
    if piece == "chestplate":
        return [("body", dict(groups=[([P(0, -12, 0)], [C(16, 16, -4, 0, -2, 8, 12, 4, grow=o)])])),
                ("arm_r", dict(groups=[([], [C(40, 16, -3, -2, -2, 4, 12, 4, grow=o)])])),
                ("arm_l", dict(groups=[([], [C(40, 16, -1, -2, -2, 4, 12, 4, grow=o, mirror=True)])]))]
    if piece in ("leggings", "boots"):
        g = (i if piece == "leggings" else o) + ARMOR_LEG
        legs = [("leg_r", dict(xclip=(None, 1.9), groups=[([], [C(0, 16, -2, 0, -2, 4, 12, 4, grow=g)])])),
                ("leg_l", dict(xclip=(-1.9, None), groups=[([], [C(0, 16, -2, 0, -2, 4, 12, 4, grow=g, mirror=True)])]))]
        if piece == "leggings":
            legs.insert(0, ("body", dict(groups=[([P(0, -12, 0)], [C(16, 16, -4, 0, -2, 8, 12, 4, grow=i)])])))
        return legs
    raise ValueError("armor piece %r: use 'helmet', 'chestplate', 'leggings' or 'boots'" % (piece,))


def hurt_tint(sheet):
    """A texture sheet with the game's hurt overlay mixed in: 0.698 x texel + 0.302 x pure red, in display values
    (entity.fsh: mix(overlayColor.rgb, color.rgb, overlayColor.a) with OverlayTexture's 0xB2FF0000)."""
    out = np.array(sheet, dtype=np.uint8, copy=True)
    rgb = out[..., :3].astype(np.float32) * HURT_MIX + np.array(HURT_COLOUR, dtype=np.float32) * 255.0 * (1.0 - HURT_MIX)
    out[..., :3] = np.clip(np.rint(rgb), 0, 255).astype(np.uint8)
    return out


def piglin_sheet(kind="piglin", baby=False, hurt=False):
    """(key, HxWx4 uint8) the game's piglin texture (cut out at alpha 0.1); hurt=True: with the red hurt overlay."""
    base = ch._game_texture(TEXTURES[(kind, bool(baby))])
    sheet = np.zeros_like(base)
    ch._over(sheet, base)
    key = "piglin_%s%s" % (kind, "_baby" if baby else "")
    if hurt:
        return key + "_hurt", hurt_tint(sheet)
    return key, sheet


def armor_sheet(piece):
    """(key, HxWx4 uint8) the golden equipment texture a piece is drawn with (entity/equipment/humanoid[_leggings])."""
    path = ARMOR_TEXTURES[piece]
    base = ch._game_texture(path)
    sheet = np.zeros_like(base)
    ch._over(sheet, base)
    return "armor_" + path.split("/")[-2] + "_gold", sheet


# ----------------------------------------------------------------------------------------------------
# held items (ItemInHandLayer + ItemTransform)
# ----------------------------------------------------------------------------------------------------
def item_display(model_id, side="r"):
    """(rotation degrees, translation in 1/16 block, scale) of an item model's third-person display for the right
    ('r') or left ('l') hand: the nearest model of its parent chain that defines the context wins, and a model
    chain without 'thirdperson_lefthand' uses the right hand's (ItemTransforms.Deserializer)."""
    chain = mobs._model_chain("item/" + model_id)
    contexts = ("thirdperson_lefthand", "thirdperson_righthand") if side == "l" else ("thirdperson_righthand",)
    for ctx in contexts:
        for raw in chain:
            d = raw.get("display", {}).get(ctx)
            if d is not None:
                return (tuple(float(c) for c in d.get("rotation", (0, 0, 0))),
                        tuple(float(c) for c in d.get("translation", (0, 0, 0))),
                        tuple(float(c) for c in d.get("scale", (1, 1, 1))))
    return ((0.0, 0.0, 0.0), (0.0, 0.0, 0.0), (1.0, 1.0, 1.0))


def hand_matrix(side, display, baby=False):
    """Parent-space matrix (the arm's rig frame) of a flat item sprite as engine.mcassets.item_object builds it
    (origin at its centre, in its XZ plane, front -Y, 16 px = 1 unit).

    ItemInHandLayer.submitArmWithItem: after ModelPart.translateAndRotate(arm): rotate X -90, rotate Y 180,
    translate(+-1 / 16, 2 / 16, -10 / 16) (a baby: (0, 1 / 16, -4.5 / 16)), then ItemTransform.apply(leftHand):
    translate(+-tx, ty, tz) / 16, rotationXYZ(rx, +-ry, +-rz), scale (the lower signs for the left hand)."""
    s = -1.0 if side == "l" else 1.0
    a, b, c = BABY_HAND_OFFSET if baby else HAND_OFFSET
    rot, trans, scale = display
    shown = (Matrix.Translation((s * trans[0] / 16.0, trans[1] / 16.0, trans[2] / 16.0))
             @ Matrix.Rotation(math.radians(rot[0]), 4, "X") @ Matrix.Rotation(math.radians(s * rot[1]), 4, "Y")
             @ Matrix.Rotation(math.radians(s * rot[2]), 4, "Z") @ Matrix.Diagonal((scale[0], scale[1], scale[2], 1.0)))
    chain = (Matrix.Rotation(math.radians(-90.0), 4, "X") @ Matrix.Rotation(math.radians(180.0), 4, "Y")
             @ Matrix.Translation((s * a / 16.0, b / 16.0, c / 16.0)) @ shown)
    return ch._AXES @ chain @ ch._AXES


# ----------------------------------------------------------------------------------------------------
# physics the game runs for what happens around a piglin
# ----------------------------------------------------------------------------------------------------
def air_track(velocity, height=0.0, on_ground=True, push=(0.0, 0.0), wall=None, land_only=False, max_ticks=200):
    """LivingEntity.travelInAir tick by tick for a mob `height` blocks above the floor it comes down on.

    velocity = its (vx, vy, vz) in blocks per tick when the first tick begins; on_ground = whether it stood on
    something in the tick before (the drag of a tick comes from the state before its move: 0.546 on the ground,
    0.91 in the air; vertically (vz - 0.08) * 0.98). push = what its AI adds to (vx, vy) per tick while it is in the
    air (0.02 x its forward input). wall = (ux, uy, blocks): it gets no farther than that along the unit direction.
    land_only: stop on the tick it lands (a fall); otherwise go on until it lies still (the slide after a hop).
    Returns [(tick, dx, dy, height, (vx, vy, vz) after the tick, on the ground after the tick)]."""
    vx, vy, vz = (float(c) for c in velocity)
    x = y = 0.0
    z = max(0.0, float(height))
    ground = bool(on_ground)
    out = [(0, 0.0, 0.0, z, (vx, vy, vz), ground)]
    for tick in range(1, max_ticks + 1):
        drag = GROUND_DRAG if ground else AIR_DRAG
        if not ground:
            vx, vy = vx + push[0], vy + push[1]
        nx, ny = x + vx, y + vy
        if wall is not None:
            over = nx * wall[0] + ny * wall[1] - float(wall[2])
            if over > 0.0:
                nx, ny = nx - wall[0] * over, ny - wall[1] * over
                into = vx * wall[0] + vy * wall[1]
                vx, vy = vx - wall[0] * into, vy - wall[1] * into
        nz = z + vz
        if nz <= 0.0:
            nz, vz, ground = 0.0, 0.0, True
        else:
            ground = False
        x, y, z = nx, ny, nz
        vz = (vz - GRAVITY) * 0.98
        vx, vy = vx * drag, vy * drag
        if math.hypot(vx, vy) < 0.003:                                   # LivingEntity.aiStep zeroes what is slower
            vx = vy = 0.0
        out.append((tick, x, y, z, (vx, vy, vz), ground))
        if ground and (land_only or (vx == 0.0 and vy == 0.0)):
            break
    return out


def knock_track(strength=KNOCKBACK, max_back=None, max_ticks=80):
    """[(tick, blocks back, blocks up)] of a mob that stood on the ground and was hit: LivingEntity.knockback
    (horizontal speed `strength` away from the attacker, vertical min(0.4, -0.0784 / 2 + strength)) followed by
    LivingEntity.travelInAir tick by tick (gravity 0.08, vertical drag 0.98, horizontal drag 0.546 on the ground and
    0.91 in the air, taken from the state before each move). max_back = a wall that far behind it."""
    up = min(KNOCK_UP_MAX, REST_FALL / 2.0 + float(strength))
    wall = None if max_back is None else (1.0, 0.0, float(max_back))
    return [(tick, x, z) for tick, x, _y, z, _v, _g in air_track((float(strength), 0.0, up), wall=wall, max_ticks=max_ticks)]


def fall_track(drop, speed=0.0):
    """[(tick, blocks forward, blocks fallen)] of a mob that has just walked off an edge at `speed` blocks per
    second and comes down `drop` blocks lower (LivingEntity.travelInAir: it leaves with the -0.0784 blocks per tick
    of a standing mob, then vz = (vz - 0.08) * 0.98; forward it keeps its last step, then 0.546 of it, 0.91 per
    tick, plus the 0.02 x input its AI still pushes with). One block takes 5 ticks, two 7, three 9, four 10."""
    step = max(0.0, float(speed)) / 20.0
    push = FLY_SPEED * math.sqrt(step * (1.0 - GROUND_DRAG))             # input = attribute x modifier, speed = input^2 / 0.454
    track = air_track((step, 0.0, REST_FALL), float(drop), True, push=(push, 0.0), land_only=True)
    return [(tick, x, float(drop) - z) for tick, x, _y, z, _v, _g in track]


def _solids(world):
    """engine.fx's collision boxes for a Village, a blocks.World or None."""
    if world is None:
        return None
    from . import fx

    if isinstance(world, fx._Solids):
        return world
    if hasattr(world, "world"):
        return fx._Solids(world)

    class _Set:
        pass

    holder = _Set()
    holder.world = world
    return fx._Solids(holder)


def item_track(start, velocity, world=None, floor=None, max_ticks=400):
    """ItemEntity.tick() from the entity position `start` with `velocity` (blocks per tick, Blender axes) until the
    item lies still: [(tick, (x, y, z))]. Per tick: gravity 0.04, move, speed * 0.98 (horizontally * 0.6 * 0.98 on
    the ground). world = a Village or blocks.World: the item (a 0.25 block box) collides with its blocks;
    floor = the height of a flat floor as well (default: none with a world, so that an item can lie in a pit
    below 0; height 0 when there is no world)."""
    solids = _solids(world)
    if floor is None and solids is None:
        floor = 0.0
    p = [float(c) for c in start]
    v = [float(c) for c in velocity]
    out = [(0, tuple(p))]
    for tick in range(1, max_ticks + 1):
        v[2] -= ITEM_GRAVITY
        want = (v[0], v[1], v[2])
        got = list(solids.collide(p, want, ITEM_BOX)) if solids is not None else list(want)
        if floor is not None and p[2] + got[2] < floor:
            got[2] = floor - p[2]
        p = [p[i] + got[i] for i in range(3)]
        on_ground = want[2] < 0.0 and abs(got[2] - want[2]) > 1e-9
        for i in (0, 1):
            if abs(got[i] - want[i]) > 1e-9:
                v[i] = 0.0
        if abs(got[2] - want[2]) > 1e-9:
            v[2] = 0.0
        drag = ITEM_DRAG * (0.6 if on_ground else 1.0)
        v = [v[0] * drag, v[1] * drag, v[2] * ITEM_DRAG]
        if on_ground and v[2] < 0.0:
            v[2] *= -0.5
        out.append((tick, tuple(p)))
        if on_ground and v[0] * v[0] + v[1] * v[1] < 1e-5:
            break
    return out


def launch(item, frame, start, velocity, world=None, floor=None):
    """An engine.mobs DroppedItem flies as the game's item entity does: spawned at the entity position `start` on
    `frame` with `velocity` (blocks per TICK); returns the frame it lies still (see item_track for world / floor:
    the blocks of `world`, or a flat floor at height `floor`, 0 by default when there is no world).
    It is a new entity (age 0, hidden before `frame`); call item.animate(frame, last) afterwards for bob and spin."""
    f0 = int(round(frame))
    start = ch._vec3(start)
    track = item_track(start, velocity, world=world, floor=floor)
    item.drop(f0, start, velocity=(0.0, 0.0, 0.0))                       # the bookkeeping of a new entity
    for i in range(3):
        keys = [(f0, start[i], "LINEAR")] + [(f0 + tick * TICK, p[i], "LINEAR") for tick, p in track[1:]]
        ch._segment(item.root, _LOC, i, keys, "LINEAR")
    item.rest_pos = Vector(track[-1][1])
    return int(math.ceil(f0 + track[-1][0] * TICK - 1e-6))


def lob_velocity(start, target, world=None, floor=None, loft=LOB_LOFT_TICKS, max_ticks=70):
    """The velocity (blocks per tick) that lobs an item entity from `start` so that it comes to REST at `target`:
    the flattest arc of ItemEntity.tick (gravity 0.04, drag 0.98) that clears the blocks of `world`, flown `loft`
    ticks longer for some air over the rim. Not the game's throw (that is 0.3 blocks per tick straight at the
    player, and from a pit it mostly hits the wall): a director's cheat for launch() and barter(lob=True).
    floor = the height of a flat floor when there is no world (default: the target's). ValueError if no arc fits."""
    start, target = ch._vec3(start), ch._vec3(target)
    if floor is None and world is None:
        floor = target.z
    flat = Vector((target.x - start.x, target.y - start.y))
    dist = flat.length
    u = flat / dist if dist > 1e-6 else Vector((0.0, -1.0))
    k = ITEM_DRAG

    def aimed(n):
        """The velocity that rests the item at the target after an arc of n ticks, or None if something is in its way."""
        geo = (1.0 - k ** n) / (1.0 - k)
        fallen = ITEM_GRAVITY / (1.0 - k) * (n - k * geo)                # what gravity takes off the height in n ticks
        reach = dist
        for _try in range(6):
            vh = reach / geo
            v = (u.x * vh, u.y * vh, (target.z - start.z + fallen) / geo)
            rest = Vector(item_track(start, v, world=world, floor=floor)[-1][1])
            miss = Vector((rest.x - target.x, rest.y - target.y))
            if abs(rest.z - target.z) > 0.06 or miss.length > max(1.0, 0.6 * dist):
                return None                                              # it hit a wall, or lies on another level
            if miss.length < 0.04:
                return v
            reach -= miss.dot(u)                                         # (it slides on after it lands: aim short)
            if reach < 0.02:
                return None
        return None

    for n in range(5, int(max_ticks) + 1):
        v = aimed(n)
        if v is not None:
            return aimed(n + int(loft)) or v
    raise ValueError("no arc of an item from (%.2f, %.2f, %.2f) comes to rest at (%.2f, %.2f, %.2f): is the target "
                     "on a floor, with air above it?" % (start.x, start.y, start.z, target.x, target.y, target.z))


def _feet(who, frame):
    """Feet position of a Character at `frame`, or the point itself."""
    if isinstance(who, ch.Character):
        return who.pos_at(frame)
    if isinstance(who, bpy.types.Object):
        return Vector(who.matrix_world.translation)
    return ch._vec3(who)


def throw_item(item, frame, thrower, aim, world=None, floor=None, seed=0):
    """A player throws (drops) an item toward the point / Character `aim`: LivingEntity.createItemStackToDrop.

    The item appears 0.3 below the thrower's eyes with the look vector * 0.3 + 0.1 up (blocks per tick, plus the
    game's small jitter drawn from `seed`) and flies as an item entity; returns the frame it lies still. A piglin
    cannot take it before frame + 48 (pick-up delay 40 ticks). The arm swing is thrower.swing_arm(frame)."""
    f0 = int(round(frame))
    feet = _feet(thrower, f0)
    eye = getattr(thrower, "eye_height", 1.62)
    target = aim.eye_point(f0) if isinstance(aim, ch.Character) else ch._vec3(aim)
    look = target - (feet + Vector((0.0, 0.0, eye)))
    look = look.normalized() if look.length > 1e-6 else Vector((0.0, -1.0, 0.0))
    r = pix.rng(3571 * (int(seed) + 1) + 23)
    ang, jit = r.uniform(0.0, 2.0 * math.pi), 0.02 * r.random()
    v = (look.x * PLAYER_DROP_SPEED + math.cos(ang) * jit, look.y * PLAYER_DROP_SPEED + math.sin(ang) * jit,
         look.z * PLAYER_DROP_SPEED + PLAYER_DROP_UP + (r.random() - r.random()) * 0.1)
    if floor is None and world is None:
        floor = feet.z
    return launch(item, f0, feet + Vector((0.0, 0.0, eye - THROW_BELOW_EYE)), v, world=world, floor=floor)


def pickup(item, frame, taker):
    """The game's pick-up: from `frame` the dropped item flies to the middle of its taker (halfway between feet and
    eyes) in 3 ticks, along t squared, frozen as it was (ItemPickupParticle), then it is gone. Returns the first
    frame on which it is gone (frame + 4)."""
    f0 = int(round(frame))
    a = item.pos_at(f0)
    feet = _feet(taker, f0)
    target = Vector((feet.x, feet.y, feet.z + getattr(taker, "eye_height", PIGLIN_EYE) / 2.0))
    for ob, path, index in ((item.spinner, _ROT, 2), (item.spinner, _LOC, 2)):
        if ch._find(ob, path, index) is not None:                        # the particle shows the state of that tick
            ch._cut(ob, path, index, f0, ch._val(ob, path, index, f0))
    n = PICKUP_TICKS * TICK
    steps = 12
    for i in range(3):
        keys = [(f0, a[i], "LINEAR")]
        keys += [(f0 + n * k / steps, a[i] + (target[i] - a[i]) * (k / steps) ** 2, "LINEAR") for k in range(1, steps + 1)]
        ch._segment(item.root, _LOC, i, keys, "LINEAR")
    gone = int(math.ceil(f0 + n - 1e-6))
    item.pick_up(gone)
    return gone


def _shot_span(camera):
    """(first frame, frame after the last) of a Shot passed as `camera`, or (None, None) for a Film / camera / None."""
    a, b = getattr(camera, "frame_start", None), getattr(camera, "frame_end", None)
    if a is None or b is None or not hasattr(camera, "camera"):
        return None, None
    return int(a), int(b) + 1


def poof(pos, frame, camera=None, size=(PIGLIN_WIDTH, PIGLIN_HEIGHT), count=POOF_COUNT, seed=0, glow=None,
         village=None, collection=None, first=None, until=None):
    """The white puffs of a mob that has just died (entity event 60, LivingEntity.makePoofParticles): `count` (20)
    ParticleTypes.POOF in the bounding box `size` = (width, height) standing on the feet point `pos`, from `frame`.

    ExplodeParticle: each puff starts with a speed of a few hundredths of a block per tick, rises (gravity -0.1)
    and slows (friction 0.9), is 0.2 to 1.4 blocks wide, is drawn for 19 to 83 ticks and runs through the sprites
    particle/generic_7 .. generic_0 (particles/poof.json) once, at 0.7 to 1.0 of white. Drawn with engine.fx:
    camera-facing quads lit like an up-facing surface plus `glow` self-light (default POOF_GLOW 0.25: cream-white
    in a dim set; fx.SPRITE_GLOW 0.6 burns out there). camera = the Shot (or Film, or camera object) that films it;
    village = a Village to collide with.
    A burst lasts up to 100 frames, longer than most shots. With a SHOT as camera it is therefore seen in that shot
    only: nothing of it shows before the shot's first frame or after its last. So a `frame` before the shot starts
    puts puffs that are already in the air on the first frame of a flash cut (frame = shot.frame_start - 8).
    first / until = other limits (nothing shows before `first`, nothing from `until` on); False = no limit on that
    side (the same scene goes on in the next shot from another angle: until=next_shot.frame_end + 1 or False).
    With a Film or a camera object there is no limit unless you give one. Returns an fx.Burst (.stop(frame) ends
    it early, fx.stop_particles(frame) ends every burst)."""
    from . import fx                                                     # (only here: engine.fx stays optional)

    frame = int(frame)
    feet = _feet(pos, frame)
    rng = fx._rng(seed, frame, 60, int(round(feet.x * 16.0)), int(round(feet.y * 16.0)))
    col = fx._collection(collection)
    cams = fx._camera_arg(camera)
    burst = fx.Burst("poof", frame)
    solids = fx._Solids(village) if village is not None else None
    glow = POOF_GLOW if glow is None else float(glow)
    shot_first, shot_after = _shot_span(camera)
    lo = shot_first if first is None else (None if first is False else int(first))
    hi = shot_after if until is None else (None if until is False else int(until))
    w, h = size
    top = len(POOF_SPRITES) - 1                                          # SpriteSet.get: age * (n - 1) / lifetime
    for i in range(int(count)):
        va = rng.normal(0.0, 1.0, 3) * 0.02                              # nextGaussian() * 0.02 per axis
        p = (feet.x + w * (2.0 * rng.random() - 1.0) - va[0] * 10.0,     # getRandomX(1.0) - xa * 10
             feet.y + w * (2.0 * rng.random() - 1.0) - va[1] * 10.0,
             feet.z + h * rng.random() - va[2] * 10.0)                   # getRandomY() - ya * 10
        v = va + (rng.random(3) * 2.0 - 1.0) * 0.05
        grey = rng.random() * 0.3 + 0.7
        quad = 0.1 * (rng.random() * rng.random() * 6.0 + 1.0)
        life = int(16.0 / (rng.random() * 0.8 + 0.2)) + 2
        # Particle.tick: `age++ >= lifetime` removes it, so it moves `lifetime` times and is drawn lifetime + 1 ticks
        path = fx._simulate(p, v, life, 0.04 * POOF_GRAVITY, POOF_FRICTION, solids, 0.2, rng)
        n = len(path) - 1
        ages = {}
        for age in range(n + 1):                                         # the sprite it wears at each age
            ages.setdefault(age * top // life, []).append(age)
        spans = []
        for k, span in sorted(ages.items()):
            a = int(math.ceil(frame + span[0] * TICK - 1e-6))
            b = int(math.ceil(frame + (span[-1] + 1) * TICK - 1e-6))
            a = a if lo is None else max(a, lo)                          # seen in its shot only (see the docstring)
            b = b if hi is None else min(b, hi)
            if b > a:
                spans.append((k, a, b))
        if not spans:                                                    # all of this puff's life is outside the limits
            continue
        carrier = bpy.data.objects.new("fx_poof_%d_%d" % (frame, i), None)
        carrier.empty_display_size = 0.05
        col.objects.link(carrier)
        frames = [float(frame)] + [frame + (k + 1) * TICK for k in range(n + 1)]
        pts = [path[0]] + list(path)                                     # drawn one tick behind, as the game lerps
        for axis in range(3):
            fx._write(carrier, _LOC, axis, frames, [q[axis] for q in pts], "LINEAR")
        carrier.location = path[0]
        carrier.scale = (quad, quad, quad)
        fx._face_camera(carrier, cams)
        level = round(grey * 20.0) / 20.0                                # (a material per 0.05 of grey)
        for k, shown, hidden in spans:                                   # visible on the frames shown .. hidden - 1
            mat = fx._particle_material(POOF_SPRITES[k], colour=level ** 2.2, glow=glow)
            mname = "fx_quad_%s*%g%s" % (POOF_SPRITES[k].split("/")[-1], level, "+%g" % glow if glow else "")
            mesh = bpy.data.meshes.get(mname) or fx._quad_mesh(mname, (0.0, 1.0, 0.0, 1.0), mat)
            ob = bpy.data.objects.new("fx_poof_%d_%d_%d" % (frame, i, k), mesh)
            col.objects.link(ob)
            ob.parent = carrier
            for attr in ("hide_render", "hide_viewport"):
                fx._write(ob, attr, 0, [shown - 1, shown, hidden], [1.0, 0.0, 1.0], "CONSTANT")
            ob.hide_render = ob.hide_viewport = True
            ob.visible_shadow = False
            burst.objects.append(ob)
            burst.particles.append({"object": ob, "pos": path, "lifetime": n, "size": quad, "spawn": float(frame),
                                    "first": shown, "last": hidden, "carrier": carrier, "grey": grey, "stage": k})
            burst.frame_end = max(burst.frame_end, hidden - 1)
    return burst


# ----------------------------------------------------------------------------------------------------
# the piglin
# ----------------------------------------------------------------------------------------------------
class Piglin(ch.Character):
    """A piglin, baby piglin or piglin brute as an engine.characters.Character (see the module docstring)."""

    def __init__(self, name, parts, spec, variant="piglin", baby=False, seed=None, collection=None):
        super().__init__(name, "piglin", parts, spec, child=baby)
        self.variant, self.baby = variant, bool(baby)
        self.collection = collection
        self.ear_l, self.ear_r = parts["ear_l"], parts["ear_r"]
        self.width = BABY_WIDTH if baby else PIGLIN_WIDTH               # the game's hit box
        self.box_height = BABY_HEIGHT if baby else PIGLIN_HEIGHT
        self.walk_speed = BABY_WALK_SPEED if baby else WALK_SPEED
        self.run_speed = BABY_RUN_SPEED if baby else CHASE_SPEED
        self.anim_scale = BABY_ANIM_SCALE if baby else 1.0
        self.leg_offset = abs(next(p["pivot"][0] for p in spec["parts"] if p["name"] == "leg_l")) * self.unit
        self._ear_default = (BABY_EAR_DEGREES if baby else ADULT_EAR_DEGREES) * DEG
        if seed is None:
            seed = sum(ord(c) * (i + 1) for i, c in enumerate(name))
        r = pix.rng(5113 * (int(seed) % 100003 + 1) + 17)
        self._age0 = float(r.uniform(0.0, 2000.0))                       # ageInTicks on frame 1 (the ears' phase)
        self._walk_events = [(-1e9, float(r.uniform(0.0, 9.0)))]         # (frame, walkAnimation position from then on)
        for ear in (self.ear_l, self.ear_r):
            self._pose.append((ear, _ROT, 1, float(ear.rotation_euler[1])))
        for ob in (self.body, self.head, self.arm_l, self.arm_r):
            for i in range(3):
                self._pose.append((ob, _LOC, i, float(ob.location[i])))
        self._skin = []                    # (mesh object, its red twin)
        self._armor = []                   # armor meshes (never tinted: the game draws them with NO_OVERLAY)
        self._items = {"r": {}, "l": {}}   # hand -> {item key: object}
        self._hand = {"r": [], "l": []}    # hand -> [(frame, item key | None)]
        self._hand0 = {"r": None, "l": None}
        self._shown, self._flash, self._gone = [], [], []
        self._aggro, self._admires, self._dances, self._aims = [], [], [], []
        self._admire_head = {}             # (first, end) of an admire -> the head's (pitch, yaw) before it
        self.armor = ()
        self._air = None                   # the hop or fall it is in: dict(frame, floor, track of air_track)
        self.last_walk = None
        self.last_fall = None
        self.last_death = None

    def __repr__(self):
        return "<Piglin %s %s%s>" % (self.name, self.variant, " baby" if self.baby else "")

    # ------------------------------------------------------------------ queries
    def objects(self):
        """All objects of the rig (root first): parts, their red twins, armor and every item made for its hands."""
        obs = [self.parts["root"]] + [o for k, o in self.parts.items() if k != "root"]
        obs += [twin for _ob, twin in self._skin] + list(self._armor)
        obs += list(self._items["r"].values()) + list(self._items["l"].values())
        return obs

    def age(self, frame):
        """The entity's ageInTicks at `frame` (the phase of the ears, of the arm bob and of the dance)."""
        return (float(frame) - 1.0) / TICK + self._age0

    def _walk_pos_at(self, frame):
        """walkAnimation.position (game units, unscaled) the legs stand at when nothing moves them at `frame`."""
        pos = self._walk_events[0][1]
        for f, p in sorted(self._walk_events):
            if f <= frame + 1e-6:
                pos = p
        return pos

    def aggro_at(self, frame):
        """True while the weapon is held high at `frame` (ATTACKING_WITH_MELEE_WEAPON)."""
        return bool(mobs._state_at(self._aggro, frame, False))

    def aiming_at(self, frame):
        """True while the crossbow is held up at `frame` (CROSSBOW_HOLD)."""
        return bool(mobs._state_at(self._aims, frame, False))

    def admiring_at(self, frame):
        """True while it admires an item at `frame`."""
        return any(a <= frame < b for a, b in self._admires)

    def dancing_at(self, frame):
        """True while it dances at `frame`."""
        return any(a <= frame < b for a, b in self._dances)

    def gone_at(self, frame):
        """True from the frame a die() removed it (until a later place())."""
        return bool(mobs._state_at(self._gone, frame, False))

    def hurt_at(self, frame):
        """True while the red hurt overlay is on at `frame`."""
        return any(a <= frame < b for a, b in self._flash)

    def item_at(self, frame, hand="main"):
        """Key of the item in the main / off hand at `frame` ('golden_axe', 'gold_ingot', ...), or None."""
        side = "l" if hand in ("off", "l") else "r"
        return mobs._state_at(self._hand[side], frame, self._hand0[side])

    def item_object(self, key, hand="main"):
        """The object of an item this piglin has held or will hold (a focus / hero target), or None."""
        return self._items["l" if hand in ("off", "l") else "r"].get(key)

    @property
    def weapon(self):
        """The object in the main hand at rest (sword, axe, crossbow), or None."""
        return self._items["r"].get(self._hand0["r"])

    def _posed_arms(self, frame):
        """The arms whose pitch a pose holds at `frame` (the walk and the hurt fling leave them alone)."""
        held = set()
        if self.admiring_at(frame):
            held.add("l")
        if self.aggro_at(frame):
            held.add("r")
        if self.aiming_at(frame):
            held |= {"l", "r"}
        return held

    def _aim(self, target, frame):
        """Head (yaw, pitch-up) toward a target, clamped to the game's limits for mobs (75 / 40 degrees)."""
        if target is None:
            return 0.0, 0.0
        d = self._point(target, frame) - self.eye_point(frame)
        yaw = ch._clamp(ch._wrap(math.atan2(d.x, -d.y) - self.yaw_at(frame)), -HEAD_YAW_MAX, HEAD_YAW_MAX)
        pitch = ch._clamp(math.atan2(d.z, math.hypot(d.x, d.y)), -HEAD_PITCH_MAX, HEAD_PITCH_MAX)
        return yaw, pitch

    # ------------------------------------------------------------------ visibility
    def _sync(self):
        """Rewrite every visibility key: a part shows while the piglin is shown, not gone and not flashing red, its
        red twin while it flashes; armor while shown; an item while it is the one in its hand."""
        frames = {f for f, _v in self._shown} | {f for f, _v in self._gone}
        for a, b in self._flash:
            frames |= {a, b}
        for side in ("r", "l"):
            frames |= {f for f, _k in self._hand[side]}
        frames = sorted(frames)

        def there(f):
            return bool(mobs._state_at(self._shown, f, True)) and not self.gone_at(f)

        for ob, twin in self._skin:
            mobs._visibility_curve(ob, [(f, there(f) and not self.hurt_at(f)) for f in frames], before=True)
            mobs._visibility_curve(twin, [(f, there(f) and self.hurt_at(f)) for f in frames], before=False)
        for ob in self._armor:
            mobs._visibility_curve(ob, [(f, there(f)) for f in frames], before=True)
        for side in ("r", "l"):
            for key, ob in self._items[side].items():
                events = [(f, there(f) and mobs._state_at(self._hand[side], f, self._hand0[side]) == key) for f in frames]
                mobs._visibility_curve(ob, events, before=self._hand0[side] == key)

    def show(self, frame, visible=True):
        """Key render (and viewport) visibility of the whole piglin from `frame` on (items and armor included)."""
        self._shown.append((int(round(frame)), bool(visible)))
        self._sync()

    # ------------------------------------------------------------------ placement
    def place(self, frame, pos, yaw=0.0, keep_pose=False):
        """Hard-set position and yaw from `frame` on: upright, alive, neutral pose, weapon lowered (use at shot cuts)."""
        super().place(frame, pos, yaw, keep_pose=keep_pose)
        self._air = None
        if keep_pose:
            return
        f = int(round(frame))
        if ch._find(self.root, _ROT, 1) is not None:
            ch._cut(self.root, _ROT, 1, frame, 0.0)                     # the tip-over of a death
        if self.gone_at(f):
            self._gone.append((f, False))
        for spans in (self._flash, self._admires, self._dances):         # what was going on ends at the cut
            spans[:] = [(a, f) if a < f < b else (a, b) for a, b in spans]
        if self.aggro_at(f):
            self._aggro.append((f, False))
        if self.aiming_at(f):
            self._aims.append((f, False))
        for side in ("r", "l"):
            if mobs._state_at(self._hand[side], f, self._hand0[side]) != self._hand0[side]:
                self._hand[side].append((f, self._hand0[side]))
        self._sync()

    # ------------------------------------------------------------------ items
    def _item(self, key, side):
        """The sprite object of item `key` for one hand, made on first use (hidden until it is that hand's item)."""
        store = self._items[side]
        if key not in store:
            ob = mc.item_object(_SPRITES.get(key, key))
            col = self.collection if self.collection is not None else ch._collection(None)
            col.objects.link(ob)
            ob.name = "%s_%s_%s" % (self.name, key, side)
            ob.parent = self.arm_l if side == "l" else self.arm_r
            ob.matrix_parent_inverse = Matrix.Identity(4)
            ob.matrix_basis = hand_matrix(side, item_display(_MODELS.get(key, key), side), self.baby)
            ob["mc_item"] = key
            ob.hide_render = ob.hide_viewport = True
            store[key] = ob
        return store[key]

    def hold(self, item, frame=None, hand="main"):
        """Put an item in the main (right) or off (left) hand exactly as ItemInHandLayer draws it; None empties it.

        item = an item id ('golden_axe', 'golden_sword', 'crossbow', 'gold_ingot', ...): the flat sprite of
        engine.mcassets.item_object with the third-person display of the item's own model (item/handheld for tools
        and weapons, item/generated for the rest, the crossbow's own); or such a sprite object made elsewhere
        (engine.props.make_item). frame=None: what it holds from the start;
        with a frame the hand changes on that frame. A mob's arm does not change its pose for an item
        (HumanoidMobRenderer.getArmPose is EMPTY). Returns the item's object."""
        side = "l" if hand in ("off", "l") else "r"
        if isinstance(item, bpy.types.Object):                           # a sprite made elsewhere (props.make_item)
            key = item.name
            if key not in self._items[side]:
                model = str(item.get("mc_item", key[5:] if key.startswith("item_") else key)).split(".")[0]
                item.parent = self.arm_l if side == "l" else self.arm_r
                item.matrix_parent_inverse = Matrix.Identity(4)
                item.matrix_basis = hand_matrix(side, item_display(model, side), self.baby)
                self._items[side][key] = item
        else:
            key = None if item is None else str(item).replace("minecraft:", "")
        ob = None if key is None else self._item(key, side)
        if frame is None:
            self._hand0[side] = key
            if side == "r":
                self.held = None                                         # (Character.objects() must not list it twice)
        else:
            self._hand[side].append((int(round(frame)), key))
        self._sync()
        return ob

    def item_point(self, frame, hand="main"):
        """World position of the centre of the item in a hand at `frame` (None if the hand is empty)."""
        key = self.item_at(frame, hand)
        if key is None:
            return None
        ob = self.item_object(key, hand)
        scene = bpy.context.scene
        cur, sub = scene.frame_current, scene.frame_subframe
        whole = int(math.floor(frame))
        scene.frame_set(whole, subframe=float(frame) - whole)
        point = ob.matrix_world.translation.copy()
        scene.frame_set(cur, subframe=sub)
        return point

    # ------------------------------------------------------------------ ears
    def ear_angles(self, age, walk_pos=0.0, walk_speed=0.0):
        """(left, right) ear zRot in radians from AbstractPiglinModel.setupAnim: -+(default + cos(phase [* 1.2]) *
        (0.08 + 0.4 * walkAnimationSpeed)), phase = ageInTicks * 0.1 + walkAnimationPos * 0.5."""
        t = age * EAR_AGE_RATE + walk_pos * EAR_WALK_RATE
        amp = EAR_FLOP + walk_speed * EAR_FLOP_WALK
        return (-self._ear_default - math.cos(t * EAR_LEFT_RATE) * amp, self._ear_default + math.cos(t) * amp)

    def _key_ears(self, f0, f1, walk=None, step=1.0):
        """Key both ears over [f0, f1] from the game's formula; walk(frame) -> (walkAnimationPos, speed) or None."""
        f0, f1 = float(f0), float(f1)
        if f1 <= f0 + 1e-6:
            return
        rest = self._walk_pos_at(f0) * self.anim_scale
        now = (ch._val(self.ear_l, _ROT, 1, f0), ch._val(self.ear_r, _ROT, 1, f0))
        ts = [f0 + k * step for k in range(int(math.floor((f1 - f0) / step - 1e-9)) + 1)] + [f1]
        keys = ([], [])
        for f in mobs._dedupe(ts):
            pos, speed = walk(f) if walk is not None else (rest, 0.0)
            want = self.ear_angles(self.age(f), pos, speed)
            mix = mobs._ease((f - f0) / EAR_BLEND)                       # ears that stood still join in smoothly
            for side in (0, 1):
                keys[side].append((f, now[side] + (want[side] - now[side]) * mix, "LINEAR"))
        ch._segment(self.ear_l, _ROT, 1, keys[0], "LINEAR")
        ch._segment(self.ear_r, _ROT, 1, keys[1], "LINEAR")

    def flop_ears(self, frame_start, frame_end):
        """The ears' slow flop of a piglin that stands still (+-0.08 rad, once in 63 ticks the right ear, 52 the
        left). walk(), idle(), hurt() and dance() key the ears themselves; between them the ears hold still."""
        self._key_ears(frame_start, frame_end, step=3.0)

    # ------------------------------------------------------------------ locomotion
    def walk(self, frame, points, speed=None, run=False, from_current=False, gait="planted", swing=None, ramp=4,
             corner=CORNER_RADIUS, dip=None):
        """Travel along the polyline `points` (1.94 blocks/s, 5.40 with run=True; a baby 2.80 / 7.77); returns the end frame.

        gait "planted": the legs open as far as the game opens them at that speed (1.4 * min(speed / 5, 1) rad, at
        most 1.1; or `swing`) and the cadence follows, so the foot on the ground stays where it was put; the hips
        dip with the stride. gait "vanilla": exactly the game (one leg cycle per 2.36 blocks at any speed, no dip:
        the feet slide). Arms swing against the legs as in the game unless a pose holds them; the ears flop with
        the walk. ramp = frames of acceleration and of braking, or (start, end). corner = radius of the arc that
        rounds each corner of `points` (0 = sharp, turned on the spot). dip = how much of the exact dip the hips
        make (planted gait; default 1 walking: the sole stays on the ground; 0.5 with run=True, where the full dip
        would be a bounce of 0.3 block four times a second: the standing sole then floats up to 0.15 at each end
        of a step). For LEVEL ground and stairs: a leg of `points` steeper than one block per block raises
        ValueError (it would glide down the drop): walk past the edge, then fall()."""
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
        for a, b in zip(path, path[1:]):
            if abs(b.z - a.z) > STAIR_SLOPE * math.hypot(b.x - a.x, b.y - a.y) + 1e-6:
                raise ValueError("%s.walk: the leg from (%.2f, %.2f, %.2f) to (%.2f, %.2f, %.2f) is steeper than stairs. "
                                 "walk() is for level ground and stairs (it would glide down a drop): walk to 0.3 "
                                 "past the edge with ramp=(4, 0), then fall(end_frame, to_z)"
                                 % (self.name, a.x, a.y, a.z, b.x, b.y, b.z))
        teleport = (path[0] - here).length > 1e-4
        self._air = None
        if len(path) < 2:
            if teleport:
                for i in range(3):
                    ch._cut(self.root, _LOC, i, f0, path[0][i], hold_rest=False)
            return f0
        on_cut = teleport or ch._cut_at(self.root, _LOC, 0, f0)
        route = mobs._Route(path, 0.0 if corner is None else float(corner), yaw_now)
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

        ramp_times = {0.0, float(n)}
        if r_in > 0.0:
            ramp_times |= {float(t) for t in range(0, int(math.ceil(r_in)) + 1)} | {r_in}
        if r_out > 0.0:
            ramp_times |= {float(t) for t in range(int(math.floor(n - r_out)), n + 1)} | {n - r_out}
        ramp_times = {t for t in ramp_times if 0.0 <= t <= n}
        bounds = [when(d) for d in route.breaks]
        bounds[0], bounds[-1] = 0.0, float(n)

        # heading: along the arcs it follows the tangent; a sharp vertex is turned on the spot, eased and centred
        # on the vertex; a piglin that does not face its first leg turns into it while it sets off
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
                y += turn * (mobs._ease((t - ta) / (tb - ta)) if tb > ta else float(t >= ta))
            if first_frames > 0.0:
                y += first * (1.0 - mobs._ease(t / first_frames))
            return y

        turning = set()                                                  # frames at which the heading changes
        for ta, tb in arcs + [(ta, tb) for ta, tb, _turn in sharp] + ([(0.0, first_frames)] if first_frames > 0.0 else []):
            turning |= mobs._frames_in(ta, tb)
        turning = {t for t in turning if 0.0 <= t <= n}
        curve = set()                                                    # frames at which the position is on an arc
        for ta, tb in arcs:
            curve |= mobs._frames_in(ta, tb)

        if teleport:
            for i in range(3):
                ch._cut(self.root, _LOC, i, f0, path[0][i], hold_rest=False)
        if on_cut:
            ch._cut(self.root, _ROT, 2, f0, heading0, hold_rest=False)  # starting on a cut: already facing its way
        ch._segment(self.root, _ROT, 2, [(f0 + t, yaw(t), "LINEAR") for t in mobs._dedupe(turning | {0.0, float(n)})],
                    "LINEAR")
        travel = ramp_times | set(bounds) | {t for t in curve if 0.0 <= t <= n}
        shift = None

        # the game's walk animation for this motion (legs of the vanilla gait; the ears of both gaits):
        # walkAnimationSpeed = min(4 * blocks per tick, 1), position += speed every tick
        v_tick = cruise * TICK
        s_cruise = min(ANIM_PER_BLOCK * v_tick, 1.0)
        grid = np.linspace(0.0, float(n), int(n) * 8 + 1)
        s_grid = np.minimum(ANIM_PER_BLOCK * v_tick * np.array([rate(t) for t in grid]), 1.0)
        p0 = self._walk_pos_at(f0)
        p_grid = p0 + np.concatenate(([0.0], np.cumsum((s_grid[1:] + s_grid[:-1]) * 0.5 * np.diff(grid)))) / TICK
        self._walk_events.append((float(f1), float(p_grid[-1])))

        def anim(t):
            """(walkAnimationPos as the model sees it, walkAnimationSpeed) t frames into the walk."""
            return float(np.interp(t, grid, p_grid)) * self.anim_scale, float(np.interp(t, grid, s_grid))

        L = self.leg_len
        posed = self._posed_arms(f0)
        rest_z = self._rest(self.hips, _LOC, 2)
        stances, slides = [], False
        if gait == "vanilla":
            cycle = 2.0 * math.pi / LIMB_FREQ / max(s_cruise * self.anim_scale, 1e-6) * TICK      # frames
            dt = 1.0 / min(6, max(1, int(math.ceil(24.0 / cycle))))
            times = ramp_times | {k * dt for k in range(int(n / dt) + 1)}

            def leg(sign):
                return lambda t: sign * math.cos(anim(t)[0] * LIMB_FREQ) * LEG_SWING * anim(t)[1]

            mobs._sample(self.leg_r, _ROT, 0, f0, times, leg(1.0))
            mobs._sample(self.leg_l, _ROT, 0, f0, times, leg(-1.0))
            for arm, side, sign in ((self.arm_r, "r", -1.0), (self.arm_l, "l", 1.0)):
                if side not in posed:
                    base = self._rest(arm, _ROT, 0)
                    mobs._sample(arm, _ROT, 0, f0, times,
                                 lambda t, sign=sign, base=base: base + sign * math.cos(anim(t)[0] * LIMB_FREQ) * ARM_SWING * anim(t)[1],
                                 rest=base)
            if ch._find(self.hips, _LOC, 2) is not None:
                ch._ease(self.hips, _LOC, 2, f0, f0 + 2, rest_z)
            shown_swing, steps, step_frames = LEG_SWING * s_cruise, None, cycle / 2.0
        else:
            want = float(swing) if swing is not None else ch._clamp(LEG_SWING * s_cruise, PLANTED_MIN, PLANTED_MAX)
            step = 2.0 * L * math.sin(ch._clamp(want, 0.05, 1.3))
            steps = max(1, int(round(total / step)))
            if total / steps > 2.0 * L * math.sin(min(max(want, PLANTED_MAX) + 0.1, 1.3)):
                steps += 1                                               # (rounding down would overstretch the legs)
            most = max(1, int(n / MIN_STEP_FRAMES))
            if steps > most:                                             # faster than a frame can show: they slide
                steps, slides = most, True
            reach = L * math.sin(1.3)
            leg_swing = math.asin(ch._clamp(total / steps / (2.0 * L), 0.0, math.sin(1.3)))
            slides = slides or total / steps / 2.0 > reach + 1e-9
            first_stance = "r" if self._foot > 0 else "l"                # (the leg that goes back first)
            if steps % 2:
                self._foot = -self._foot
            yaw0 = yaw(0.0)
            side_of = {"r": -self.leg_offset, "l": self.leg_offset}      # to the piglin's left

            def lane(leg, t):
                """Ground passed under that leg's side of the body, along its heading."""
                return dist(t) - side_of[leg] * (yaw(t) - yaw0)

            marks = [0.0] + [when((k - 0.5) * total / steps) for k in range(1, steps + 1)] + [float(n)]
            last = len(marks) - 2
            stance = [first_stance if j % 2 == 0 else ("l" if first_stance == "r" else "r") for j in range(last + 1)]
            gone = [lane(stance[j], marks[j + 1]) - lane(stance[j], marks[j]) for j in range(last + 1)]
            y_in = [0.0 if j == 0 else (gone[j] if j == last else gone[j] / 2.0) for j in range(last + 1)]
            y_out = [y_in[j] - gone[j] for j in range(last + 1)]

            def index(t):
                return min(max(bisect.bisect_right(marks, t) - 1, 0), last)

            def foot(leg, t):
                """How far that sole is in front of its hip."""
                j = index(t)
                if stance[j] == leg:
                    return y_in[j] - (lane(leg, t) - lane(leg, marks[j]))
                a = y_out[j - 1] if j > 0 else 0.0
                b = y_in[j + 1] if j < last else 0.0
                span = dist(marks[j + 1]) - dist(marks[j])
                return a + (b - a) * ((dist(t) - dist(marks[j])) / span if span > 1e-9 else 1.0)

            def leg_angle(leg, t):
                return -math.asin(ch._clamp(foot(leg, t), -reach, reach) / L)

            sink = (0.5 if run else 1.0) if dip is None else float(dip)

            def hip(t):
                """The hips dip so that the sole of the standing leg stays on the ground."""
                return rest_z - sink * L * (1.0 - math.cos(leg_angle(stance[index(t)], t)))

            step_frames = n / float(steps)
            dt = 1.0 / min(6, max(1, int(math.ceil(16.0 / step_frames))))     # keys on every frame and between
            times = ramp_times | set(marks) | turning | {k * dt for k in range(int(n / dt) + 1)}
            travel |= {t for t in times if t < r_in + 1e-6 or t > n - r_out - 1e-6}      # (the ramps are curves)
            mobs._sample(self.leg_r, _ROT, 0, f0, times, lambda t: leg_angle("r", t))
            mobs._sample(self.leg_l, _ROT, 0, f0, times, lambda t: leg_angle("l", t))
            mobs._sample(self.hips, _LOC, 2, f0, times, hip, rest=rest_z)
            k_arm = ARM_SWING * s_cruise / max(leg_swing, 1e-6)          # the game's arm swing for this speed
            for arm, side in ((self.arm_r, "r"), (self.arm_l, "l")):
                if side not in posed:
                    base = self._rest(arm, _ROT, 0)
                    mobs._sample(arm, _ROT, 0, f0, times,
                                 lambda t, side=side, base=base: base - leg_angle(side, t) * k_arm, rest=base)
            shown_swing = leg_swing
            stances = [(f0 + marks[j], f0 + marks[j + 1], stance[j]) for j in range(last + 1)]

            # Round an arc the body would turn about its own middle, which drags the planted sole sideways. The
            # body is moved the other way instead: it pivots over the foot that carries it; what is left over at
            # the end of the arcs is given back evenly along the whole walk (as engine.mobs does for the golem).
            if arcs:
                gridt = set(marks)
                for ta, tb in arcs:
                    cuts = max(1, int(math.ceil((tb - ta) * 4.0)))
                    gridt |= {ta + (tb - ta) * k / cuts for k in range(cuts + 1)}
                gridt = mobs._dedupe([t for t in gridt if 0.0 <= t <= n], eps=1e-6)
                table, e = [(0.0, 0.0, 0.0)], Vector((0.0, 0.0))
                for ta, tb in zip(gridt, gridt[1:]):
                    turn = route.turned(dist(tb)) - route.turned(dist(ta))
                    if abs(turn) > 1e-12:
                        tm = 0.5 * (ta + tb)
                        ym = yaw(tm)
                        e = e - Vector((math.cos(ym), math.sin(ym))) * (foot(stance[index(tm)], tm) * turn)
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
            at = route.point(dist(t))
            if shift is not None:
                dx, dy = shift(t)
                at.x, at.y = at.x + dx, at.y + dy
            return at

        travel = mobs._dedupe(travel)
        spots = [spot(t) for t in travel]
        for i in range(3):
            ch._segment(self.root, _LOC, i, [(f0 + t, q[i], "LINEAR") for t, q in zip(travel, spots)], "LINEAR")
        self._key_ears(f0, f1, walk=lambda f: anim(f - f0), step=1.0)
        self.last_walk = dict(gait=gait, frames=(f0, f1), blocks=total, speed=cruise * FPS, swing=shown_swing,
                              steps=steps, step_frames=step_frames, stance=stances, slides=slides,
                              anim_speed=s_cruise, ramp=(r_in, r_out),
                              corners=[(round(rad, 3), round(math.degrees(turn), 1)) for _d0, _d1, turn, rad in route.arcs],
                              sharp=[round(math.degrees(turn), 1) for _d, turn in route.sharp])
        return f1

    def _stop_walk(self, frame, travel=False):
        """Let go of what a walk still running at `frame` would do to the hips and the heading (travel=True: to
        its position too: it comes to a stop within two frames)."""
        if travel and ch._find(self.root, _LOC, 0) is not None:
            stop = self.pos_at(frame + 1)
            for i in range(3):
                ch._ease(self.root, _LOC, i, frame, frame + 2, stop[i])
        rest_z = self._rest(self.hips, _LOC, 2)
        if ch._find(self.hips, _LOC, 2) is not None:
            ch._ease(self.hips, _LOC, 2, frame, frame + 2, rest_z)
        if ch._find(self.root, _ROT, 2) is not None:
            ch._ease(self.root, _ROT, 2, frame, frame + 1, self.yaw_at(frame))

    # ------------------------------------------------------------------ idle + poses
    def idle(self, frame_start, frame_end, seed=0):
        """Alive while it stands: head glances, weight shifts, the game's arm bob and the slow flop of the ears."""
        super().idle(frame_start, frame_end, seed)
        self.flop_ears(frame_start, frame_end)

    def admire(self, frame, item="gold_ingot", ticks=ADMIRE_TICKS, ease=0, keep=False):
        """The ADMIRING_ITEM pose from `frame` for `ticks` game ticks (the game: 119 = 5.95 s); returns the end frame.

        The item sits in the off (left) hand as ItemInHandLayer draws it, the left arm is raised (xRot -0.9, yRot
        0.5: the hand in front of the chest), the head is bowed 0.5 rad (28.6 degrees) and looks straight ahead,
        at the item. The game snaps into and out of the pose (ease=0); ease = frames to ease it instead. At the
        end the arm drops, the head goes back to where it looked, the item is gone (keep=True leaves it in the
        hand). Do not idle() / look_at() during the pose: the head belongs to it."""
        f0 = int(round(frame))
        f1 = f0 + max(1, int(round(float(ticks) * TICK)))
        e = max(0, int(ease))
        head = (ch._val(self.head, _ROT, 0, f0), ch._val(self.head, _ROT, 2, f0))
        ch._ease(self.head, _ROT, 0, f0, f0 + e, ADMIRE_HEAD_PITCH)
        ch._ease(self.head, _ROT, 2, f0, f0 + e, 0.0)
        ch._ease(self.arm_l, _ROT, 0, f0, f0 + e, ADMIRE_ARM_PITCH)
        ch._ease(self.arm_l, _ROT, 2, f0, f0 + e, -ADMIRE_ARM_YAW)       # (model yRot +0.5 = rig euler z -0.5)
        ch._ease(self.head, _ROT, 0, f1, f1 + e, head[0])
        ch._ease(self.head, _ROT, 2, f1, f1 + e, head[1])
        ch._ease(self.arm_l, _ROT, 0, f1, f1 + e, self._rest(self.arm_l, _ROT, 0))
        ch._ease(self.arm_l, _ROT, 2, f1, f1 + e, 0.0)
        key = str(item).replace("minecraft:", "")
        self._item(key, "l")
        self._hand["l"].append((f0, key))
        if not keep:
            self._hand["l"].append((f1 + e, None))
        self._admires.append((f0, f1))
        self._admire_head[(f0, f1)] = head
        self._sync()
        return f1

    def stop_admiring(self, frame):
        """End an admire() early on `frame`: the arm drops, the item is gone and nothing is given back. That is
        what a hit does (PiglinAi.wasHurtBy -> stopHoldingOffHandItem(.., false)); hurt() and die() call it."""
        f0 = int(round(frame))
        hit = [(a, b) for a, b in self._admires if a <= f0 < b]
        if not hit:
            return False
        back = self._admire_head.get(hit[0], (0.0, 0.0))                 # (the head looks where it looked before)
        ch._cut(self.head, _ROT, 0, f0, back[0])
        ch._cut(self.head, _ROT, 2, f0, back[1])
        ch._cut(self.arm_l, _ROT, 0, f0, self._rest(self.arm_l, _ROT, 0))
        ch._cut(self.arm_l, _ROT, 2, f0, 0.0)
        self._admires = [(a, f0) if (a, b) in hit else (a, b) for a, b in self._admires]
        self._hand["l"].append((f0, None))
        self._sync()
        return True

    def aggro(self, frame, on=True, ease=0):
        """Hold the weapon high (ATTACKING_WITH_MELEE_WEAPON: main arm xRot -1.8) from `frame`; on=False lowers it.

        That is how a piglin or brute that has an attack target carries its sword or axe, also while it runs.
        ease=0 = the game's snap."""
        f0 = int(round(frame))
        value = HOLD_HIGH if on else self._rest(self.arm_r, _ROT, 0)
        ch._ease(self.arm_r, _ROT, 0, f0, f0 + max(0, int(ease)), value)
        self._aggro.append((f0, bool(on)))
        return f0 + max(0, int(ease))

    def attack(self, frame):
        """The melee swing of a piglin or brute (AnimationUtils.swingWeaponDown, 6 ticks = 7.2 frames); returns the end frame.

        The weapon arm comes down from over the head to hanging (lowest 3.6 frames in) and goes back up, the other
        arm swings along; before and after, the weapon is held high (aggro() is switched on at `frame` if it was
        not). The game deals the damage on the tick the swing STARTS: victim.hurt(frame, source=attacker). One swing
        per 20 ticks (24 frames) at most, from 1.43 blocks away or closer."""
        f0 = int(round(frame))
        if not self.aggro_at(f0):
            self.aggro(f0)
        n = SWING_TICKS * TICK
        back = {(arm, i): ch._val(arm, _ROT, i, f0) for arm in (self.arm_r, self.arm_l) for i in range(3)}
        back[(self.arm_r, 0)] = HOLD_HIGH
        chans = {key: [(float(f0), None, "LINEAR")] for key in back}
        steps = SWING_TICKS * 4
        for k in range(1, steps + 1):
            t = k / float(steps)
            f = f0 + n * t
            age = self.age(f)
            down = math.sin(t * math.pi)
            ease = math.sin((1.0 - (1.0 - t) * (1.0 - t)) * math.pi)
            for arm, sign, (base, wob, rate, reach) in ((self.arm_r, 1.0, SWING_MAIN), (self.arm_l, -1.0, SWING_OFF)):
                x = base + math.cos(age * rate) * wob + down * reach - ease * 0.4
                x += 2.0 * sign * math.sin(age * BOB_X_RATE) * BOB_X                     # bobArms, applied twice
                z = 2.0 * sign * (math.cos(age * BOB_Z_RATE) * BOB_Z + BOB_Z)
                chans[(arm, 0)].append((f, x, "LINEAR"))
                chans[(arm, 1)].append((f, z, "LINEAR"))                                 # model zRot
                chans[(arm, 2)].append((f, -sign * SWING_ARM_YAW, "LINEAR"))             # model yRot +-0.157
        for (arm, i), keys in chans.items():
            keys.append((f0 + n + 0.3, back[(arm, i)]))
            ch._segment(arm, _ROT, i, keys, "LINEAR")
        return int(math.ceil(f0 + n + 0.3))

    def swing_arm(self, frame, side="r"):
        """The plain humanoid swing of one arm (HumanoidModel.setupAttackAnimation, WHACK, 6 ticks = 7.2 frames):
        what the off hand does when it throws the barter result (side='l'). Additive: leave 8 frames between two."""
        arm = self.arm_l if side == "l" else self.arm_r
        sgn = -1.0 if side == "l" else 1.0
        n = SWING_TICKS * TICK
        pitch = ch._val(self.head, _ROT, 0, frame)
        steps = 12
        twist, ax, ay, az, quirk = [], [], [], [], []
        for k in range(1, steps):
            t = k / float(steps)
            f = n * t
            body = math.sin(math.sqrt(t) * 2.0 * math.pi) * 0.2 * sgn    # body.yRot (mirrored for the left arm)
            g = math.sin((1.0 - (1.0 - t) ** 4) * math.pi)               # Ease.outQuart
            h = math.sin(t * math.pi) * -(pitch - 0.7) * 0.75
            twist.append((f, -body))
            ax.append((f, -(g * 1.2 + h) + (body if side == "l" else 0.0)))
            az.append((f, -2.0 * body))
            ay.append((f, -0.4 * math.sin(t * math.pi)))
            quirk.append((f, body))                                      # leftArm.xRot += body.yRot, whoever swings
        chans = [(self.body, 2, twist), (arm, 0, ax), (arm, 2, az), (arm, 1, ay), (self.head, 2, [(f, -v) for f, v in twist])]
        if side != "l":
            chans.append((self.arm_l, 0, quirk))
        for ob, index, offs in chans:
            ch._offsets(ob, _ROT, index, frame, offs + [(n, 0.0)], -1.95, 1.95, interp="BEZIER")
        return int(math.ceil(frame + n))

    def aim_crossbow(self, frame, on=True, ease=0):
        """Hold the charged crossbow up (CROSSBOW_HOLD, AnimationUtils.animateCrossbowHold) from `frame`; on=False
        lowers it and the crossbow is the unloaded one again. The arms take the head's direction of that frame
        (main arm xRot -pi/2 + 0.1, yRot -0.3; other arm -1.5 and +0.6, each plus the head's): call it again
        after the head has turned. Needs a piglin made with weapon='crossbow'."""
        if "crossbow" not in self._items["r"]:
            raise ValueError("%s has no crossbow: make_piglin(..., weapon='crossbow')" % self.name)
        f0 = int(round(frame))
        f1 = f0 + max(0, int(ease))
        if on:
            hx, hz = ch._val(self.head, _ROT, 0, f1), ch._val(self.head, _ROT, 2, f1)
            (mx, my), (ox, oy) = CROSSBOW_HOLD["main"], CROSSBOW_HOLD["off"]
            ch._ease(self.arm_r, _ROT, 0, f0, f1, mx + hx)
            ch._ease(self.arm_r, _ROT, 2, f0, f1, -my + hz)
            ch._ease(self.arm_l, _ROT, 0, f0, f1, ox + hx)
            ch._ease(self.arm_l, _ROT, 2, f0, f1, -oy + hz)
            self._item("crossbow_loaded", "r")
            self._hand["r"].append((f0, "crossbow_loaded"))
        else:
            for arm in (self.arm_r, self.arm_l):
                ch._ease(arm, _ROT, 0, f0, f1, self._rest(arm, _ROT, 0))
                ch._ease(arm, _ROT, 2, f0, f1, 0.0)
            self._hand["r"].append((f1, "crossbow"))
        self._aims.append((f0, bool(on)))
        self._sync()
        return f1

    def dance(self, frame_start, frame_end):
        """The DANCING pose of PiglinModel.setupAnim from frame_start to frame_end (the celebration after a hoglin
        hunt; a brute never dances): with t = ageInTicks / 60 the arms are held out sideways at 70 + 10 * cos(40 t)
        degrees, head, arms and body bob with sin(40 t) (once in 9.4 ticks), the head sways +-1 px with sin(10 t)
        and the ears swing +-10 degrees about their 30 with sin / cos(30 t). The game snaps in and out."""
        f0, f1 = int(round(frame_start)), int(round(frame_end))
        if f1 <= f0:
            return f0
        u = self.unit
        rest = {key: self._rest(*key) for key in ((self.body, _LOC, 2), (self.head, _LOC, 0), (self.head, _LOC, 2),
                                                  (self.arm_r, _LOC, 2), (self.arm_l, _LOC, 2), (self.arm_r, _ROT, 1),
                                                  (self.arm_l, _ROT, 1), (self.ear_r, _ROT, 1), (self.ear_l, _ROT, 1))}
        chans = {key: [] for key in rest}
        for f in range(f0, f1):
            t = self.age(f) / DANCE_PERIOD
            bob = math.sin(t * 40.0)
            body = bob * 0.35                                            # body.y += (pixels, down)
            arm = (70.0 + math.cos(t * 40.0) * 10.0) * DEG
            values = {
                (self.body, _LOC, 2): -body * u,
                (self.head, _LOC, 0): math.sin(t * 10.0) * u,            # head.x +=
                (self.head, _LOC, 2): -(bob + 0.4 - body) * u,           # head.y += (the head hangs on the rig's body)
                (self.arm_r, _LOC, 2): -(bob * 0.5 - 0.5 - body) * u,
                (self.arm_l, _LOC, 2): -(bob * 0.5 + 0.5 - body) * u,
                (self.arm_r, _ROT, 1): arm,                              # zRot (absolute: no arm bob while dancing)
                (self.arm_l, _ROT, 1): -arm,
                (self.ear_r, _ROT, 1): 30.0 * DEG + DEG * math.sin(t * 30.0) * 10.0,
                (self.ear_l, _ROT, 1): -30.0 * DEG - DEG * math.cos(t * 30.0) * 10.0,
            }
            for key, value in values.items():
                base = rest[key] if key[1] == _LOC else 0.0
                chans[key].append((f, base + value, "LINEAR"))
        for (ob, path, index), keys in chans.items():
            ch._cut(ob, path, index, f0, keys[0][1])
            if len(keys) > 1:
                ch._segment(ob, path, index, keys, "LINEAR")
            ch._cut(ob, path, index, f1, rest[(ob, path, index)])
        self._dances.append((f0, f1))
        return f1

    # ------------------------------------------------------------------ hurt + death
    def _air_state(self, frame):
        """(floor height, (vx, vy, vz), on the ground) of the hop or fall that is still going on at `frame`, or None
        when it stands on the ground it was last put on."""
        air = self._air
        if air is None or frame < air["frame"] - 1e-6:
            return None
        k = int(math.floor((frame - air["frame"]) / TICK + 1e-6))
        if k >= len(air["track"]) - 1:
            return None                                                  # over: it lies still (or has landed)
        _tick, _dx, _dy, _h, vel, ground = air["track"][k]
        return air["floor"], vel, ground

    def _key_air(self, f0, here, floor, track, scale=1.0):
        """Key an air_track on the root from the position `here` (LINEAR from tick to tick, as the game lerps) and
        remember it; returns the blocks moved sideways in each tick."""
        pts = [(tick, here.x + dx * scale, here.y + dy * scale, floor + h) for tick, dx, dy, h, _v, _g in track]
        for i in range(3):
            keys = [(f0, here[i], "LINEAR")] + [(f0 + pt[0] * TICK, pt[1 + i], "LINEAR") for pt in pts[1:]]
            ch._segment(self.root, _LOC, i, keys, "LINEAR")
        self._air = dict(frame=f0, floor=floor, track=track)
        return [math.hypot(b[1] - a[1], b[2] - a[2]) for a, b in zip(pts, pts[1:])]

    def _knock(self, f0, source, strength, max_back):
        """Key the knock-back of a hit at f0 on the root; returns the blocks moved in each tick ([] = none).

        LivingEntity.knockback: sideways it gets half of what it had plus `strength` away from the source; only a mob
        ON THE GROUND is lifted (min(0.4, vy / 2 + strength)). One that is still in the air from an earlier hit, or
        falling, keeps its vertical speed and comes down on the floor it left."""
        if source is None or not strength or strength <= 0.0:
            return []
        here = self.pos_at(f0)
        src = self._point(source, f0)
        away = Vector((here.x - src.x, here.y - src.y, 0.0))
        if away.length < 1e-6:
            yaw = self.yaw_at(f0)
            away = Vector((-math.sin(yaw), math.cos(yaw), 0.0))          # nobody to be pushed from: backwards
        away.normalize()
        state = self._air_state(f0)
        floor, vel, ground = (here.z, (0.0, 0.0, REST_FALL), True) if state is None else state
        floor = min(floor, here.z)
        up = min(KNOCK_UP_MAX, vel[2] / 2.0 + float(strength)) if ground else vel[2]
        wall = None if max_back is None else (away.x, away.y, float(max_back))
        track = air_track((vel[0] / 2.0 + away.x * strength, vel[1] / 2.0 + away.y * strength, up), here.z - floor,
                          ground, wall=wall)
        return self._key_air(f0, here, floor, track)

    def _fling(self, f0, moved, speed0=HURT_ANIM_SPEED, old0=0.0, pos0=None):
        """The limbs after a hit (LivingEntity.handleDamageEvent sets walkAnimation.speed to 1.5, then every tick
        speed += (min(4 * blocks moved, 1) - speed) * 0.4 and position += speed); returns the frame they rest.
        speed0 / old0 / pos0 = another start of the walk animation (a fall goes on from the walk's)."""
        speed, old, pos = [float(speed0)], [float(old0)], [self._walk_pos_at(f0) if pos0 is None else float(pos0)]
        while True:
            k = len(speed)
            target = min(ANIM_PER_BLOCK * moved[k - 1], 1.0) if k - 1 < len(moved) else 0.0
            s = speed[-1] + (target - speed[-1]) * ANIM_SMOOTH
            old.append(speed[-1])
            speed.append(s)
            pos.append(pos[-1] + s)
            if (k >= len(moved) and s < 0.01) or k > 240:
                break
        last = len(speed) - 1

        def state(t):
            """(walkAnimationPos, walkAnimationSpeed) as the renderer sees them t ticks after the hit."""
            k = min(int(math.floor(t + 1e-9)), last)
            part = min(max(t - k, 0.0), 1.0) if k < last else 1.0
            return ((pos[k] - speed[k] * (1.0 - part)) * self.anim_scale,
                    min(old[k] + (speed[k] - old[k]) * part, 1.0))

        end = f0 + (last + 1) * TICK
        ts = [f0 + 0.25 * TICK * k for k in range(4 * (last + 1) + 1)]
        posed = self._posed_arms(f0)
        chans = [(self.leg_r, 1.0, LEG_SWING, 0.0), (self.leg_l, -1.0, LEG_SWING, 0.0)]
        if "r" not in posed:
            chans.append((self.arm_r, -1.0, ARM_SWING, self._rest(self.arm_r, _ROT, 0)))
        if "l" not in posed:
            chans.append((self.arm_l, 1.0, ARM_SWING, self._rest(self.arm_l, _ROT, 0)))
        for ob, sign, amp, base in chans:
            keys = [(float(f0), None, "LINEAR")]
            for f in ts[1:]:
                p, s = state((f - f0) / TICK)
                keys.append((f, base + sign * math.cos(p * LIMB_FREQ) * amp * s, "LINEAR"))
            keys.append((end + 1.0, base))
            ch._segment(ob, _ROT, 0, keys, "LINEAR")
        self._walk_events.append((float(end), float(pos[-1])))
        self._key_ears(f0, end, walk=lambda f: state((f - f0) / TICK), step=0.6)
        return end + 1.0

    def fall(self, frame, to_z, forward=None, speed=None):
        """Drop from `frame` to a floor at height `to_z`, as the game's gravity does it; returns the landing frame.

        LivingEntity.travelInAir: it leaves with the -0.0784 blocks per tick of a standing mob, then every tick
        vz = (vz - 0.08) * 0.98: one block takes 5 ticks (6 frames), two 7 ticks (8.4 frames), three 9 (10.8).
        speed = how fast it walked off the edge, in blocks per second (default: the speed of a walk() that ends on
        `frame` WITHOUT braking, ramp=(4, 0), or that is still under way; otherwise 0: straight down, which is
        what a piglin does whose floor is dug away). It drifts on the way it faces: its last
        step, then 0.546 of it, then 0.91 per tick (0.43 block from a stroll over a two-block drop, 1.10 from a
        chase); forward = that drift in blocks if you want another (a wall in the way: forward=0.2).
        The legs and arms go on with the game's walk animation and settle about 10 frames after the landing.
        The game drops a mob when its 0.6-wide box has left the block: walk until its centre is 0.3 PAST the edge.
        A fall of more than 3 blocks hurts in the game (hurt(landing)); two blocks do nothing."""
        f0 = int(round(frame))
        here = self.pos_at(f0)
        drop = here.z - float(to_z)
        if drop <= 1e-6:
            raise ValueError("%s.fall: it stands at height %.2f on frame %d, to_z=%.2f is not below it" %
                             (self.name, here.z, f0, float(to_z)))
        if speed is None:                                                # the walk it is in, or that ends here unbraked
            w, speed = self.last_walk, 0.0
            if w is not None:
                (a, b), (r_in, r_out) = w["frames"], w["ramp"]
                if a + r_in <= f0 < b - r_out or (f0 == b and r_out <= 0.0):
                    speed = w["speed"]
        step = max(0.0, float(speed)) / 20.0                             # blocks per tick on the ground
        push = FLY_SPEED * math.sqrt(step * (1.0 - GROUND_DRAG))
        yaw = self.yaw_at(f0)
        u = Vector((math.sin(yaw), -math.cos(yaw)))
        track = air_track((u.x * step, u.y * step, REST_FALL), drop, True, push=(u.x * push, u.y * push), land_only=True)
        ticks = track[-1][0]
        drift = math.hypot(track[-1][1], track[-1][2])
        scale = 1.0
        if forward is not None:
            if drift > 1e-6:
                scale = float(forward) / drift
            else:                                                        # it stood still: an even drift
                track = [(t, u.x * forward * t / ticks, u.y * forward * t / ticks, h, v, g) for t, _x, _y, h, v, g in track]
            drift = float(forward)
        self._stop_walk(f0)
        moved = self._key_air(f0, here, float(to_z), track, scale)
        # the walk animation goes on from where the legs are (LivingEntity.calculateEntityAnimation counts the
        # horizontal move only): speed min(4 x blocks per tick, 1), and a phase that fits the legs' angle now
        s0 = min(ANIM_PER_BLOCK * step, 1.0)
        leg = ch._val(self.leg_r, _ROT, 0, f0)
        phase = self._walk_pos_at(f0) * self.anim_scale * LIMB_FREQ
        if s0 > 0.01 and abs(math.cos(phase) * LEG_SWING * s0 - leg) > 0.03:
            phase = math.acos(ch._clamp(leg / (LEG_SWING * s0), -1.0, 1.0))
        still = self._fling(f0, moved, speed0=s0, old0=s0, pos0=phase / LIMB_FREQ / self.anim_scale + s0)
        land = f0 + ticks * TICK
        self.last_fall = dict(frames=(f0, land), ticks=ticks, drop=drop, forward=drift, speed=float(speed), still=still)
        return int(math.ceil(land - 1e-6))

    def hurt(self, frame, source=None, knockback=KNOCKBACK, max_back=None):
        """The game's hurt on `frame`: red for 10 ticks (12 frames), the limbs fling, and with a `source` the knock-back hop.

        source = who hit it (a Character, an Object or a point): it is thrown KNOCKBACK 0.4 blocks per tick away
        from there and up (0.96 high, 2.0 blocks back, in the air for 10 ticks; knock_track has the numbers).
        source=None (fire, a fall) or knockback=0: no hop. max_back = blocks to a wall behind it. A walk that is
        still running is cut off. Weapon and armor do not turn red (the game draws them without the overlay).
        The game ignores a hit that comes less than 10 ticks (12 frames) after the last one. Here an earlier hit
        is keyed all the same, as the game treats a mob in the air: no second lift, it gets the new push and comes
        down on the floor it left (so it never ends up floating). Returns the frame on which it stands still again."""
        f0 = int(round(frame))
        self.stop_admiring(f0)
        self._flash.append((f0, f0 + HURT_FRAMES))
        moved = self._knock(f0, source, knockback, max_back)
        self._stop_walk(f0, travel=not moved and self._air_state(f0) is None)
        end = self._fling(f0, moved)
        self._sync()
        return int(math.ceil(max(end, f0 + HURT_FRAMES, f0 + len(moved) * TICK)))

    def die(self, frame, source=None, knockback=KNOCKBACK, max_back=None, camera=None, poof_particles=True, seed=0,
            village=None, glow=None, first=None, until=None):
        """The game's death from `frame`: red, the body tips over onto its left side (90 degrees after 13.5 ticks, on
        the square-root curve of LivingEntityRenderer.setupRotations), after 20 ticks (24 frames) it is gone and 20
        white poof particles rise where it lay. Bloodless, as the game is. Returns the frame it is gone.

        source / knockback / max_back: the knock-back of the last hit, as hurt(). The limbs hang straight (a dead
        mob's walk animation is stopped), a raised weapon stays raised. camera = the Shot (or Film / camera object)
        that films the poof (needed unless poof_particles=False). With a Shot the puffs are seen in that shot only
        (they would hang in the next one for up to 100 frames); first / until / glow: see poof(). The burst is
        last_death["burst"]. A later place() brings the piglin back."""
        f0 = int(round(frame))
        gone = f0 + DEATH_FRAMES
        self.stop_admiring(f0)
        self._flash.append((f0, gone))
        moved = self._knock(f0, source, knockback, max_back)
        self._stop_walk(f0, travel=not moved and self._air_state(f0) is None)
        posed = self._posed_arms(f0)
        for ob, side in ((self.leg_r, None), (self.leg_l, None), (self.arm_r, "r"), (self.arm_l, "l")):
            if side not in posed and ch._find(ob, _ROT, 0) is not None:
                ch._cut(ob, _ROT, 0, f0, self._rest(ob, _ROT, 0))
        flat = 1.0 + 1.0 / DEATH_RATE                                    # 13.5 ticks
        keys = [(float(f0), None, "LINEAR"), (f0 + TICK, 0.0, "LINEAR")]
        t = 1.25
        while t < flat:
            keys.append((f0 + t * TICK, DEATH_FLIP * math.sqrt((t - 1.0) * DEATH_RATE), "LINEAR"))
            t += 0.25
        keys.append((f0 + flat * TICK, DEATH_FLIP))
        ch._segment(self.root, _ROT, 1, keys, "LINEAR")
        self._gone.append((gone, True))
        self._sync()
        burst = None
        if poof_particles:
            burst = poof(self.pos_at(gone), gone, camera=camera, size=(self.width, self.box_height), seed=seed,
                         village=village, glow=glow, first=first, until=until)
        self.last_death = dict(frame=f0, flat=f0 + flat * TICK, gone=gone, burst=burst)
        return gone


# ----------------------------------------------------------------------------------------------------
# factories
# ----------------------------------------------------------------------------------------------------
def make_piglin(name, kind="piglin", baby=False, weapon="default", armor=(), collection=None, seed=None):
    """Build a piglin (kind='piglin'), a piglin brute (kind='brute') or a baby piglin (baby=True), feet at the
    origin, facing -Y, from the game's model classes and textures.

    weapon: 'default' = what the game gives it (piglin: 'golden_sword', brute: 'golden_axe', baby: nothing),
    'crossbow', any flat item id, or None. armor = golden pieces an adult piglin wears: any of 'helmet',
    'chestplate', 'leggings', 'boots' (the game: each with a chance of 1 in 10; brutes and babies none).
    seed = the phase of its ears and arm bob (default: from the name)."""
    kind = {"piglin_brute": "brute"}.get(kind, kind)
    if (kind, bool(baby)) not in TEXTURES:
        raise ValueError("no such piglin: kind=%r baby=%r (kinds 'piglin' and 'brute'; only piglins have babies)" % (kind, baby))
    spec = _baby_spec() if baby else _piglin_spec()
    key, sheet = piglin_sheet(kind, baby)
    col = ch._collection(collection)
    parts = ch._build_rig(name, spec, sheet, ch._sheet_material(key, sheet), col)
    p = Piglin(name, parts, spec, variant=kind, baby=baby, seed=seed, collection=col)
    red = ch._sheet_material(*piglin_sheet(kind, baby, hurt=True))
    for part_name, ob in parts.items():
        if ob.type != "MESH":
            continue
        me = ob.data.copy()
        me.name = ob.data.name + "_hurt"
        me.materials[0] = red
        twin = bpy.data.objects.new(ob.name + "_hurt", me)
        col.objects.link(twin)
        twin.parent = ob
        twin.matrix_parent_inverse = Matrix.Identity(4)
        twin.hide_render = twin.hide_viewport = True
        p._skin.append((ob, twin))
    if armor:
        if baby:
            raise ValueError("baby piglins wear no armor in the game (populateDefaultEquipmentSlots: adults only)")
        pieces = (armor,) if isinstance(armor, str) else tuple(armor)
        for piece in pieces:
            if piece not in ARMOR_TEXTURES:
                raise ValueError("armor piece %r: use 'helmet', 'chestplate', 'leggings' or 'boots'" % (piece,))
            akey, asheet = armor_sheet(piece)
            mat = ch._sheet_material(akey, asheet)
            for part_name, part in _armor_parts(piece):
                me = ch._part_mesh("%s_%s_%s" % (name, piece, part_name), part, asheet, p.unit, mat)
                ob = bpy.data.objects.new("%s_%s_%s" % (name, piece, part_name), me)
                col.objects.link(ob)
                ob.parent = parts[part_name]
                ob.matrix_parent_inverse = Matrix.Identity(4)
                p._armor.append(ob)
        p.armor = pieces
    if weapon == "default":
        weapon = None if baby else WEAPONS[kind]
    if weapon is not None:
        p.hold(weapon)
    p._sync()
    return p


def add_piglin(st, name, kind="piglin", baby=False, **kw):
    """The piglin called `name` on a films.lookdev.Stage (built on first use): Stage.actor builds villagers and
    Steve only, and Stage.finish() hides whatever is in st.cast outside its shots."""
    p = st.cast.get(name)
    if p is None:
        p = st.cast[name] = make_piglin(name, kind=kind, baby=baby, **kw)
    return p


def add_item(st, item_id, name=None, **kw):
    """A dropped item of engine.mobs ('gold_ingot', 'ender_pearl', ...) registered with the Stage the same way."""
    name = name or item_id
    it = st.cast.get(name)
    if it is None:
        it = st.cast[name] = mobs.make_dropped_item(item_id, name=name, **kw)
    return it


# ----------------------------------------------------------------------------------------------------
# bartering
# ----------------------------------------------------------------------------------------------------
def in_reach(piglin, item, frame):
    """True when the dropped item lies where the piglin can take it at `frame`: Mob.aiStep looks in its bounding
    box widened by one block on every side (not up or down)."""
    a, b = item.pos_at(frame), piglin.pos_at(frame)
    side = piglin.width / 2.0 + PICKUP_REACH + ITEM_BOX / 2.0
    return (abs(a.x - b.x) <= side + 1e-6 and abs(a.y - b.y) <= side + 1e-6
            and a.z < b.z + piglin.box_height and a.z + ITEM_BOX > b.z)


def _lob_spots(start, to, beside, seed=0):
    """Where a lobbed result may come to rest: the point `to` itself, or (beside=True: `to` is somebody's feet) the
    spots LOB_SHORT away from it, the one on the thrower's side first; `seed` turns the order (several results
    thrown to one player do not land on one spot)."""
    if not beside:
        return [to.copy()]
    back = Vector((start.x - to.x, start.y - to.y))
    back = back.normalized() if back.length > 1e-6 else Vector((0.0, 1.0))
    turns = [0.0, 55.0, -55.0, 110.0, -110.0, 180.0]
    turns = turns[int(seed) % len(turns):] + turns[:int(seed) % len(turns)]
    spots = []
    for deg in turns:
        c, sn = math.cos(math.radians(deg)), math.sin(math.radians(deg))
        spots.append(to + Vector((back.x * c - back.y * sn, back.x * sn + back.y * c, 0.0)) * LOB_SHORT)
    return spots


def barter(piglin, ingot_item, frame, result_item="ender_pearl", toward=None, admire_ticks=ADMIRE_TICKS, count=1,
           world=None, floor=None, seed=0, animate=240, face=None, ease=0, lob=False):
    """The whole exchange as keyed animation; returns the frames of its beats.

    piglin       an adult piglin (a baby admires the ingot and keeps it: nothing comes back; a brute refuses)
    ingot_item   the engine.mobs DroppedItem ('gold_ingot') lying within reach of the piglin on `frame` (None: the
                 ingot is simply in its hand on `frame`)
    frame        the frame the piglin takes it: the ingot flies to the piglin's middle in 3 ticks and is gone
                 (pickup), and on that same frame the piglin is in the ADMIRING_ITEM pose with the ingot in its
                 left hand, for `admire_ticks` game ticks (the game: 119 = 143 frames; a director may shorten it)
    result_item  what it throws back when the pose ends: an item id (a DroppedItem is made, `count` = stack size:
                 the game gives 2-4 ender pearls) or a DroppedItem (e.g. piglins.add_item(st, 'ender_pearl')).
                 It is thrown with the off-hand swing from 0.3 below the piglin's eyes at 0.3 blocks per tick
                 toward one block above `toward` (the player: a Character or its feet point; None = a spot nearby,
                 as the game does when it sees no player) and then lies there as a dropped item.
                 Any item or BLOCK id works ('gravel', 'obsidian', 'string', 'leather', 'iron_nugget', ...).
    world        a Village or blocks.World the thrown item collides with (the wall of a hole!); floor = the height
                 of a flat floor when there is no world (default: the piglin's feet)
    lob          False = the game's throw (above). True = a director's cheat for a piglin in a pit: the result is
                 lobbed on the flattest arc that clears the blocks of `world` and comes to rest 0.45 block from
                 `toward`'s feet (a Character: on the piglin's side first, `seed` picks another side) or exactly
                 at `toward` (a point). See lob_velocity; ValueError if no arc gets there.
    animate      frames of bob and spin keyed on the result after the throw; face = a camera position the result
                 shows its flat side to on the frame it lands.
    Returns dict(pickup, taken, admire=(first, end), throw, landed, item, rest): pickup = `frame`, taken = first
    frame the dropped ingot is gone, throw = admire end = the frame the result leaves the hand, landed = the frame
    it lies still at `rest`, item = the result's DroppedItem (register it with the Stage: st.cast[item.name])."""
    if piglin.variant == "brute":
        raise ValueError("a piglin brute does not barter: it picks up nothing but a golden axe and never admires "
                         "(PiglinBrute.wantsToPickUp, PiglinBruteAi has no ADMIRE_ITEM activity)")
    f0 = int(round(frame))
    feet = piglin.pos_at(f0)
    item_id, taken = "gold_ingot", f0
    if ingot_item is not None:
        if not in_reach(piglin, ingot_item, f0):
            a = ingot_item.pos_at(f0)
            raise ValueError("the %s at (%.2f, %.2f, %.2f) is out of %s's reach at frame %d: a piglin takes what "
                             "lies within %.2f blocks of its centre along x and y, at its own height"
                             % (ingot_item.item_id, a.x, a.y, a.z, piglin.name, f0,
                                piglin.width / 2.0 + PICKUP_REACH + ITEM_BOX / 2.0))
        item_id = ingot_item.item_id
        taken = pickup(ingot_item, f0, piglin)
    end = piglin.admire(f0, item_id, ticks=admire_ticks, ease=ease, keep=piglin.baby)
    out = dict(pickup=f0, taken=taken, admire=(f0, end), throw=None, landed=None, item=None, rest=None)
    if piglin.baby:
        # PiglinAi.stopHoldingOffHandItem, not an adult: the loved item goes to the main hand; nothing is thrown
        piglin._hand["l"].append((end, None))
        piglin.hold(item_id, frame=end)
        return out
    if result_item is None:
        return out
    if isinstance(result_item, str):
        result_item = mobs.make_dropped_item(result_item, count=count, seed=seed, collection=piglin.collection)
    piglin.swing_arm(end, side="l")
    if toward is None:                                                   # PiglinAi.getRandomNearbyPos
        r = pix.rng(2903 * (int(seed) + 1) + 5)
        ang, far = r.uniform(0.0, 2.0 * math.pi), r.uniform(1.0, 4.0)
        to = feet + Vector((math.cos(ang) * far, math.sin(ang) * far, 0.0))
    else:
        to = _feet(toward, end)
    aim = to + Vector((0.0, 0.0, THROW_TARGET_UP)) - feet
    aim = aim.normalized() if aim.length > 1e-6 else Vector((0.0, 0.0, 1.0))
    start = feet + Vector((0.0, 0.0, piglin.eye_height - THROW_BELOW_EYE))
    velocity = tuple(aim * THROW_SPEED)
    if lob:
        flat = to.z if (floor is None and world is None) else floor
        velocity = None
        for spot in _lob_spots(start, to, isinstance(toward, ch.Character), seed):
            try:
                velocity = lob_velocity(start, spot, world=world, floor=flat)
                break
            except ValueError:
                continue
        if velocity is None:
            raise ValueError("barter(lob=True): no arc from %s at (%.2f, %.2f, %.2f) comes to rest at or beside "
                             "(%.2f, %.2f, %.2f)" % (piglin.name, start.x, start.y, start.z, to.x, to.y, to.z))
        floor = flat
    if floor is None and world is None:
        floor = feet.z
    landed = launch(result_item, end, start, velocity, world=world, floor=floor)
    if face is not None:
        result_item.face(landed, face)
    result_item.animate(end, landed + max(0, int(animate)))
    out.update(throw=end, landed=landed, item=result_item, rest=result_item.rest_pos.copy())
    return out


# ----------------------------------------------------------------------------------------------------
# self-test
# ----------------------------------------------------------------------------------------------------
def _evaluate(scene, frame):
    whole = int(math.floor(frame))
    scene.frame_set(whole, subframe=float(frame) - whole)
    bpy.context.view_layer.update()


def _sole(p, leg):
    """World position of the centre of a sole (the scene must be evaluated at the frame wanted)."""
    ob = p.leg_l if leg == "l" else p.leg_r
    return ob.matrix_world @ Vector((0.0, 0.0, -p.leg_len))


def _foot_slip(scene, p):
    """(worst horizontal stray, worst height) of the standing sole over the stance phases of p.last_walk."""
    worst, high = 0.0, 0.0
    for fa, fb, leg in p.last_walk["stance"]:
        ref = None
        for k in range(9):
            _evaluate(scene, fa + (fb - fa) * k / 8.0)
            s = _sole(p, leg)
            ref = s.copy() if ref is None else ref
            worst = max(worst, math.hypot(s.x - ref.x, s.y - ref.y))
            high = max(high, abs(s.z - p.pos_at(fa).z))
    return worst, high


def _floor(scene, block="polished_blackstone_bricks", half=7):
    """A flat test floor of a real block (top at z = 0)."""
    from .blocks import World, new_collection

    w = World()
    w.fill(-half, -half, -1, half, half, -1, block)
    w.cull_below = -1
    w.build(new_collection(scene, "set"))
    return w


def _check():
    """Numbers only: sizes, speeds, the gaits, the ears, the poses, the barter's beats, hurt, death and poof."""
    from . import quick

    scene = quick.reset()
    quick.setup(scene)
    pg = make_piglin("probe")
    br = make_piglin("probe_brute", "brute")
    bb = make_piglin("probe_baby", baby=True)
    steve = ch.make_player("probe_steve")
    vil = ch.make_villager("probe_villager", "farmer")
    print("heights: piglin %.4f, brute %.4f, baby %.4f | Steve %.4f, villager %.4f" %
          (pg.height, br.height, bb.height, steve.height, vil.height))
    print("eyes: piglin %.3f, baby %.3f | legs %.4f / %.4f" % (pg.eye_height, bb.eye_height, pg.leg_len, bb.leg_len))
    assert abs(pg.height - MODEL_HEIGHT) < 1e-6 and abs(br.height - MODEL_HEIGHT) < 1e-6
    assert abs(bb.height - BABY_MODEL_HEIGHT) < 1e-6 and abs(pg.eye_height - PIGLIN_EYE) < 1e-6
    assert abs(bb.eye_height - BABY_EYE) < 1e-6 and abs(pg.leg_len - 0.75) < 1e-9 and abs(bb.leg_len - 0.25) < 1e-9
    for q, tall, wide in ((pg, 2.0, 1.0), (bb, 15.0 / 16.0, 10.0 / 16.0)):
        q.place(1, (0.0, 0.0, 0.0), 0.0)
        _evaluate(scene, 1)
        pts = [ob.matrix_world @ v.co for name, ob in q.parts.items() if ob.type == "MESH" and not name.startswith("ear")
               for v in ob.data.vertices]
        lo = [min(pt[i] for pt in pts) for i in range(3)]
        hi = [max(pt[i] for pt in pts) for i in range(3)]
        print("%s: boxes span x %.4f..%.4f, y %.4f..%.4f, z %.4f..%.4f" % (q.name, lo[0], hi[0], lo[1], hi[1], lo[2], hi[2]))
        assert abs(lo[2]) < 1e-6 and abs(hi[2] - tall) < 1e-6 and abs(hi[0] - lo[0] - wide) < 0.08   # (+ sleeves, arm splay)
    print("speeds (blocks/s): walk %.3f, chase %.3f, baby walk %.3f, baby run %.3f | vanilla cycle %.3f blocks" %
          (WALK_SPEED, CHASE_SPEED, BABY_WALK_SPEED, BABY_RUN_SPEED, VANILLA_CYCLE))
    assert abs(WALK_SPEED - 1.9427) < 1e-3 and abs(CHASE_SPEED - 5.3965) < 1e-3

    # ---- the planted gait: the standing foot stays where it was put
    for q, run, label in ((pg, False, "piglin walk"), (pg, True, "piglin chase"), (bb, False, "baby walk"), (br, False, "brute walk")):
        q.place(1, (0.0, 0.0, 0.0), 0.0)
        end = q.walk(1, [(0.0, 0.0, 0.0), (0.0, -6.0, 0.0)], run=run)
        w = q.last_walk
        slip, high = _foot_slip(scene, q)
        print("%s: %.2f blocks in %d frames (%.3f blocks/s), swing %.1f deg, %s steps of %.1f frames, slip %.4f, "
              "sole off the ground %.4f%s" % (label, w["blocks"], end - 1, w["speed"], math.degrees(w["swing"]), w["steps"],
                                              w["step_frames"], slip, high, " (SLIDES)" if w["slides"] else ""))
        assert abs(q.pos_at(end).y + 6.0) < 1e-6
        if not w["slides"]:
            assert slip < 0.006 and (high < 0.004 or run), (label, slip, high)
        _evaluate(scene, end + 8)
        assert abs(q.leg_l.rotation_euler.x) < 1e-6 and abs(q.hips.location.z - q._rest(q.hips, _LOC, 2)) < 1e-6
    # a corner: the sole may only turn on the spot
    pg.place(200, (0.0, 0.0, 0.0), 0.0)
    end = pg.walk(200, [(0.0, 0.0, 0.0), (0.0, -3.0, 0.0), (3.0, -3.0, 0.0)])
    slip, high = _foot_slip(scene, pg)
    print("corner: %s, slip %.4f, ends %s" % (pg.last_walk["corners"], slip, tuple(round(c, 3) for c in pg.pos_at(end))))
    assert slip < 0.05 and (pg.pos_at(end) - Vector((3.0, -3.0, 0.0))).length < 1e-6
    # the vanilla gait is the game's formula
    pv = make_piglin("probe_vanilla", weapon=None)
    pv.place(1, (4.0, 0.0, 0.0), 0.0)
    p_start = pv._walk_pos_at(1)
    end = pv.walk(1, [(4.0, 0.0, 0.0), (4.0, -8.0, 0.0)], gait="vanilla", ramp=0)
    worst = 0.0
    for f in np.arange(3.0, end - 2.0, 1.37):
        _evaluate(scene, f)
        s = min(4.0 * (pv.last_walk["speed"] / 20.0), 1.0)
        pos = p_start + s * (f - 1.0) / TICK
        worst = max(worst, abs(pv.leg_r.rotation_euler.x - math.cos(pos * LIMB_FREQ) * LEG_SWING * s),
                    abs(pv.leg_l.rotation_euler.x - math.cos(pos * LIMB_FREQ + math.pi) * LEG_SWING * s),
                    abs(pv.arm_r.rotation_euler.x - math.cos(pos * LIMB_FREQ + math.pi) * ARM_SWING * s),
                    abs(pv.ear_r.rotation_euler.y - pv.ear_angles(pv.age(f), pos, s)[1]) if f > 8 else 0.0)
    print("vanilla gait: worst deviation from the game's formula %.5f rad (legs +-%.1f deg, cycle %.1f frames)" %
          (worst, math.degrees(pv.last_walk["swing"]), 2 * pv.last_walk["step_frames"]))
    assert worst < 0.02

    # ---- ears at rest
    pg.place(400, (0.0, 0.0, 0.0), 0.0)
    pg.idle(400, 520, seed=1)
    for f in (420.0, 455.5, 500.0):
        _evaluate(scene, f)
        want = pg.ear_angles(pg.age(f), pg._walk_pos_at(f), 0.0)
        assert abs(pg.ear_l.rotation_euler.y - want[0]) < 2e-3 and abs(pg.ear_r.rotation_euler.y - want[1]) < 2e-3
        assert abs(abs(want[1]) - 30.0 * DEG) <= EAR_FLOP + 1e-9
    print("ears at rest follow -+(30 deg + cos(age * 0.1 [* 1.2]) * 0.08) within 0.002 rad")

    # ---- admire, the ingot in the hand, barter
    pg.place(600, (0.0, 0.0, 0.0), 0.0)
    ingot = mobs.make_dropped_item("gold_ingot", name="probe_ingot")
    ingot.place(590, (0.4, -0.9, 0.0))
    ingot.animate(590, 700)
    pearl = mobs.make_dropped_item("ender_pearl", name="probe_pearl")
    beats = barter(pg, ingot, 600, pearl, toward=(0.0, -4.0, 0.0))
    print("barter beats:", {k: (tuple(round(c, 3) for c in v) if isinstance(v, Vector) else v) for k, v in beats.items()
                            if k != "item"})
    assert beats["taken"] == 604 and beats["admire"] == (600, 743) and beats["throw"] == 743
    _evaluate(scene, 599)
    assert pg.item_object("gold_ingot", "off").hide_render and not ingot.sprite.hide_render
    scene.frame_set(599, subframe=ch.SHUTTER)
    assert abs(pg.head.rotation_euler.x) < 1e-6 and abs(pg.arm_l.rotation_euler.x) < 1e-6, "the snap shows a frame early"
    for f in (600, 650, 742):
        _evaluate(scene, f)
        assert abs(pg.head.rotation_euler.x - 0.5) < 1e-6 and abs(pg.head.rotation_euler.z) < 1e-6
        assert abs(pg.arm_l.rotation_euler.x + 0.9) < 1e-6 and abs(pg.arm_l.rotation_euler.z + 0.5) < 1e-6
        assert not pg.item_object("gold_ingot", "off").hide_render and pg.admiring_at(f)
    _evaluate(scene, 603)
    assert not ingot.sprite.hide_render
    mid = Vector((0.0, 0.0, PIGLIN_EYE / 2.0))
    want = Vector((0.4, -0.9, 0.0)).lerp(mid, (3.0 / 3.6) ** 2)
    assert (ingot.root.location - want).length < 1e-4, (tuple(ingot.root.location), tuple(want))
    _evaluate(scene, 604)
    assert ingot.sprite.hide_render
    # the ingot's place in the hand, computed a second way: the pose stack of ItemInHandLayer in model pixels
    _evaluate(scene, 650)
    rx = Matrix.Rotation(-0.9, 4, "X")
    ry = Matrix.Rotation(0.5, 4, "Y")
    rz = Matrix.Rotation(pg.arm_l.rotation_euler.y, 4, "Z")
    stack = (Matrix.Translation((5.0, 2.0, 0.0)) @ rz @ ry @ rx @ Matrix.Rotation(math.radians(-90.0), 4, "X")
             @ Matrix.Rotation(math.radians(180.0), 4, "Y") @ Matrix.Translation((-1.0, 2.0, -10.0))
             @ Matrix.Translation((0.0, 3.0, 1.0)))
    px = stack @ Vector((0.0, 0.0, 0.0))                                 # the sprite's centre in model pixels
    want = pg.body.matrix_world @ Vector((px.x / 16.0, px.z / 16.0, -(px.y - 12.0) / 16.0))
    got = pg.item_object("gold_ingot", "off").matrix_world.translation
    print("ingot in the left hand: model px (%.2f, %.2f, %.2f) = %.3f above the feet, %.3f in front, %.3f to its left"
          % (px.x, px.y, px.z, got.z, -got.y, got.x))
    assert (want - got).length < 1e-4, (tuple(want), tuple(got))
    assert abs(pg.item_object("gold_ingot", "off").matrix_world.to_scale().x - 0.55) < 1e-4
    _evaluate(scene, 743)
    assert pg.item_object("gold_ingot", "off").hide_render and not pearl.sprite.hide_render
    assert abs(pg.head.rotation_euler.x) < 1e-6 and (pearl.root.location - Vector((0.0, 0.0, PIGLIN_EYE - 0.3))).length < 1e-5
    _evaluate(scene, 743 + TICK)
    aim = Vector((0.0, -4.0, 1.0)).normalized() * THROW_SPEED
    step1 = pearl.root.location - Vector((0.0, 0.0, PIGLIN_EYE - 0.3))
    assert (step1 - Vector((aim.x, aim.y, aim.z - ITEM_GRAVITY))).length < 1e-5, tuple(step1)
    _evaluate(scene, beats["landed"])
    assert (pearl.root.location - beats["rest"]).length < 1e-5 and abs(pearl.root.location.z) < 1e-6
    print("pearl: leaves at %.3f blocks/tick toward 1 above the player, lands %.2f blocks away after %d frames" %
          (aim.length, math.hypot(beats["rest"].x, beats["rest"].y), beats["landed"] - beats["throw"]))
    try:
        barter(br, ingot, 900)
    except ValueError as err:
        print("a brute refuses:", str(err)[:60], "...")
    else:
        raise AssertionError("a brute must not barter")
    bb.place(900, (0.0, 0.0, 0.0), 0.0)
    kept = barter(bb, None, 900, admire_ticks=40)
    _evaluate(scene, kept["admire"][1] + 2)
    assert kept["throw"] is None and bb.item_at(kept["admire"][1] + 2) == "gold_ingot"
    assert not bb.item_object("gold_ingot", "main").hide_render and bb.item_object("gold_ingot", "off").hide_render
    print("a baby keeps the ingot: in its main hand from frame", kept["admire"][1])

    from . import props
    gem = props.make_item("emerald")
    if gem.name not in scene.collection.all_objects:
        scene.collection.objects.link(gem)
    got = bb.hold(gem, frame=990)
    _evaluate(scene, 990)
    assert got is gem and gem.parent is bb.arm_r and not gem.hide_render and bb.item_object("gold_ingot", "main").hide_render
    _evaluate(scene, 989)
    assert gem.hide_render

    # ---- weapon held high, the swing
    br.place(1000, (0.0, 0.0, 0.0), 0.0)
    br.aggro(1000)
    end = br.attack(1010)
    _evaluate(scene, 1005)
    assert abs(br.arm_r.rotation_euler.x - HOLD_HIGH) < 1e-6
    f = 1010 + SWING_TICKS * TICK * 0.5
    _evaluate(scene, f)
    age = br.age(f)
    want = (-1.8849558 + math.cos(age * 0.09) * 0.15 + 2.2 - 0.4 * math.sin(0.75 * math.pi) + 2.0 * math.sin(age * 0.067) * 0.05)
    print("axe swing: arm %.3f rad at mid swing (formula %.3f), ends frame %d, held at %.1f" %
          (br.arm_r.rotation_euler.x, want, end, HOLD_HIGH))
    assert abs(br.arm_r.rotation_euler.x - want) < 2e-3 and abs(br.arm_r.rotation_euler.z + SWING_ARM_YAW) < 1e-6
    _evaluate(scene, end + 1)
    assert abs(br.arm_r.rotation_euler.x - HOLD_HIGH) < 1e-6 and abs(br.arm_l.rotation_euler.x) < 1e-6
    assert abs(br.arm_r.rotation_euler.z) < 1e-6 and br.aggro_at(end + 1)

    # ---- dance
    pg.place(1100, (0.0, 0.0, 0.0), 0.0)
    pg.dance(1100, 1160)
    f = 1130
    _evaluate(scene, f)
    t = pg.age(f) / 60.0
    assert abs(pg.arm_r.rotation_euler.y - (70.0 + math.cos(t * 40.0) * 10.0) * DEG) < 1e-6
    assert abs(pg.arm_l.rotation_euler.y + pg.arm_r.rotation_euler.y) < 1e-6
    head_y = (pg.head.matrix_world.translation.z - 1.5) * -16.0          # model pixels the head pivot moved down
    assert abs(head_y - (math.sin(t * 40.0) + 0.4)) < 1e-4, head_y
    assert abs(pg.ear_r.rotation_euler.y - (30.0 + math.sin(t * 30.0) * 10.0) * DEG) < 1e-6
    _evaluate(scene, 1160)
    assert abs(pg.arm_r.rotation_euler.y - ch.ARM_SPLAY) < 1e-6 and abs(pg.head.location.x) < 1e-9
    print("dance: arms at 70 +- 10 degrees, the head bobs %.1f px: as PiglinModel.setupAnim" % 2.0)

    # ---- hurt
    track = knock_track()
    apex = max(t[2] for t in track)
    air = next(t[0] for t in track[1:] if t[2] == 0.0)
    print("knock-back: %.2f blocks back, %.2f high, lands after %d ticks, rests after %d" % (track[-1][1], apex, air, track[-1][0]))
    assert abs(apex - 0.965) < 0.01 and air == 10 and abs(track[-1][1] - 1.99) < 0.03
    pg.place(1200, (0.0, 0.0, 0.0), 0.0)
    end = pg.hurt(1210, source=(0.0, -2.0, 1.0))
    for f, red in ((1209, False), (1210, True), (1221, True), (1222, False)):
        _evaluate(scene, f)
        for ob, twin in pg._skin:
            assert bool(twin.hide_render) != red and bool(ob.hide_render) == red, (f, ob.name)
        assert not pg.weapon.hide_render
    _evaluate(scene, 1210 + 5 * TICK)
    assert abs(pg.root.location.z - apex) < 1e-4 and pg.root.location.y > 1.0
    _evaluate(scene, 1210 + 2.5 * TICK)
    assert max(abs(pg.leg_r.rotation_euler.x), abs(pg.leg_l.rotation_euler.x)) > 0.3, "the legs must fling"
    assert abs(pg.leg_r.rotation_euler.x + pg.leg_l.rotation_euler.x) < 1e-6
    _evaluate(scene, end)
    assert abs(pg.root.location.z) < 1e-6 and abs(pg.leg_r.rotation_euler.x) < 1e-6
    print("hurt: red on frames 1210-1221, lands %.2f blocks back, stands still on frame %d" % (pg.root.location.y, end))
    pg.place(1250, (0.0, 0.0, 0.0), 0.0)
    pg.admire(1250)
    pg.hurt(1260)                                                       # (no source: no hop)
    for f, on in ((1259, True), (1260, False), (1300, False), (1250 + 143, False)):
        _evaluate(scene, f)
        assert pg.admiring_at(f) == on and bool(pg.item_object("gold_ingot", "off").hide_render) != on, f
        assert (abs(pg.arm_l.rotation_euler.z + 0.5) < 1e-6) == on and abs(pg.root.location.z) < 1e-9
    print("a hit ends the admiring: the ingot is gone, nothing is thrown (PiglinAi.wasHurtBy)")
    pg.place(1450, (0.0, 0.0, 0.0), 0.0)
    pg.walk(1450, [(0.0, 0.0, 0.0), (0.0, -8.0, 0.0)])
    end = pg.hurt(1470)                                                 # burnt while walking: it stops where it is
    at = pg.pos_at(1472)
    _evaluate(scene, end + 3)
    assert (pg.root.location - at).length < 1e-6 and -2.5 < at.y < -1.0 and abs(pg.leg_l.rotation_euler.x) < 1e-6
    assert abs(pg.hips.location.z - pg._rest(pg.hips, _LOC, 2)) < 1e-6
    rgb = piglin_sheet("piglin")[1][20, 20, :3].astype(float)
    red = piglin_sheet("piglin", hurt=True)[1][20, 20, :3].astype(float)
    assert np.all(np.abs(red - (rgb * HURT_MIX + np.array([255.0, 0.0, 0.0]) * (1.0 - HURT_MIX))) <= 0.5)

    # ---- death and poof
    cam = quick.camera(scene, (6.0, -8.0, 2.0), (0.0, 0.0, 1.0))
    br.place(1300, (2.0, 0.0, 0.0), 0.0)
    gone = br.die(1310, camera=cam)
    assert gone == 1334
    for f, want in ((1310, 0.0), (1310 + TICK, 0.0), (1310 + 5 * TICK, 90.0 * math.sqrt(4 * 0.08)), (1310 + 13.5 * TICK, 90.0),
                    (1333, 90.0)):
        _evaluate(scene, f)
        assert abs(math.degrees(br.root.rotation_euler.y) - want) < 0.6, (f, math.degrees(br.root.rotation_euler.y), want)
        assert not br._skin[0][1].hide_render and br._skin[0][0].hide_render, "red while it dies"
    _evaluate(scene, 1320)
    assert br.head.matrix_world.translation.x > 2.5, "it falls onto its LEFT side (+X at yaw 0)"
    _evaluate(scene, 1334)
    assert all(ob.hide_render for ob in br.objects() if ob.type == "MESH"), "gone after 20 ticks, axe and all"
    burst = br.last_death["burst"]
    born = {id(p["carrier"]) for p in burst.particles}
    seen = [p for p in burst.particles if p["first"] <= 1334 < p["last"]]
    assert len(born) == POOF_COUNT and len(seen) == POOF_COUNT and all(p["stage"] == 0 for p in seen)
    sizes = sorted(2.0 * p["size"] for p in seen)
    lives = sorted({id(p["carrier"]): p["lifetime"] + 1 for p in burst.particles}.values())
    print("poof: %d puffs %.2f-%.2f blocks wide, drawn for %d-%d ticks, the last gone on frame %d" %
          (len(born), sizes[0], sizes[-1], lives[0], lives[-1], burst.frame_end + 1))
    assert 0.2 <= sizes[0] and sizes[-1] <= 1.4 and 19 <= lives[0] and lives[-1] <= 83
    for carrier in born:                                                 # every puff wears all 8 sprites, in order,
        mine = sorted((p["first"], p["last"], p["stage"]) for p in burst.particles if id(p["carrier"]) == carrier)
        assert [m[2] for m in mine] == sorted(m[2] for m in mine) and mine[-1][2] == len(POOF_SPRITES) - 1
        assert all(a[1] == b[0] for a, b in zip(mine, mine[1:])), "one sprite at a time, without a gap"
    rise = [p["pos"][-1][2] - p["pos"][0][2] for p in seen]
    assert min(rise) > -0.2 and max(rise) > 0.3, "the puffs rise"
    br.place(1400, (2.0, 0.0, 0.0), 0.0)
    _evaluate(scene, 1400)
    assert not br._skin[0][0].hide_render and abs(br.root.rotation_euler.y) < 1e-6 and not br.weapon.hide_render

    # ---- a second hit while it is still in the air: no second lift, and down on the floor it left
    for gap in (6, 10):
        v = make_piglin("probe_twice_%d" % gap, weapon=None)
        v.place(1500, (0.0, 0.0, 0.0), 0.0)
        v.hurt(1510, source=(0.0, -1.4, 0.0))
        up = v.pos_at(1510 + gap).z
        gone = v.die(1510 + gap, source=(0.0, -1.4, 0.0), poof_particles=False)
        top = max(v.pos_at(1510 + gap + 0.5 * k).z for k in range(48))
        assert up > 0.4 and top <= up + 1e-6 and abs(v.pos_at(gone - 1).z) < 1e-6, (gap, up, top, v.pos_at(gone - 1).z)
    v = make_piglin("probe_twice", weapon=None)
    v.place(1500, (0.0, 0.0, 0.0), 0.0)
    v.hurt(1510, source=(0.0, -1.4, 0.0))
    v.hurt(1518, source=(0.0, -1.4, 0.0))
    assert max(v.pos_at(1518 + 0.5 * k).z for k in range(60)) <= v.pos_at(1518).z + 1e-6 and abs(v.pos_at(1560).z) < 1e-6
    v.place(1600, (0.0, 0.0, 0.0), 0.0)
    v.hurt(1610, source=(0.0, -1.4, 0.0))
    v.hurt(1616)                                                         # burnt in the air: the hop goes on
    assert v.pos_at(1617).z > 0.5 and abs(v.pos_at(1640).z) < 1e-6 and abs(v.pos_at(1640).y - 1.99) < 0.03
    v.place(1700, (0.0, 0.0, 0.0), 0.0)
    v.hurt(1710, source=(0.0, -1.4, 0.0))
    v.hurt(1722, source=(0.0, -1.4, 0.0))                                # 10 ticks later it is on the ground: lifted again
    assert abs(max(v.pos_at(1722 + 0.5 * k).z for k in range(30)) - apex) < 0.01
    print("two hits within 12 frames: the second does not lift it, it lands on the floor it left")

    # ---- falling
    assert [fall_track(d)[-1][0] for d in (1.0, 2.0, 3.0, 4.0)] == [5, 7, 9, 10]
    down = [z for _t, _x, z in fall_track(2.0)]
    assert abs(down[1] - 0.0784) < 1e-6 and abs(down[2] - 0.23363) < 1e-4 and abs(down[6] - 1.5926) < 1e-3
    pf = make_piglin("probe_faller")
    pf.place(1800, (0.0, 0.0, 0.0), 0.0)
    try:
        pf.walk(1800, [(0.0, 0.0, 0.0), (0.0, -1.5, 0.0), (0.0, -2.2, -2.0)])
    except ValueError as err:
        print("walk() down a drop raises:", str(err)[:74], "...")
    else:
        raise AssertionError("walk() must not glide down a drop")
    pf.walk(1800, [(0.0, 0.0, 0.0), (0.0, -1.0, 0.0), (0.0, -2.0, -1.0)])   # stairs are fine
    pf.place(1900, (0.0, 0.0, 0.0), 0.0)
    end = pf.walk(1900, [(0.0, 0.0, 0.0), (0.0, -2.3, 0.0)], ramp=(4, 0))
    land = pf.fall(end, -2.0)
    lf = pf.last_fall
    for k in range(8):
        _evaluate(scene, end + k * TICK)
        assert abs(pf.root.location.z + down[k]) < 1e-5, (k, pf.root.location.z, down[k])
    assert lf["ticks"] == 7 and land == int(math.ceil(end + 7 * TICK)) and abs(lf["forward"] - 0.43) < 0.02
    _evaluate(scene, end - 0.02)
    before = (pf.leg_r.rotation_euler.x, pf.arm_l.rotation_euler.x, pf.root.location.y)
    _evaluate(scene, end + 0.02)
    assert abs(pf.leg_r.rotation_euler.x - before[0]) < 0.02 and abs(pf.arm_l.rotation_euler.x - before[1]) < 0.02
    assert pf.root.location.y < before[2], "it goes on forward over the edge"
    _evaluate(scene, end + 5 * TICK)
    assert abs(pf.leg_r.rotation_euler.x + pf.leg_l.rotation_euler.x) < 1e-6 and 0.2 < abs(pf.leg_r.rotation_euler.x) < 0.5
    _evaluate(scene, lf["still"] + 1)
    assert abs(pf.leg_r.rotation_euler.x) < 1e-6 and abs(pf.root.location.z + 2.0) < 1e-9
    assert abs(pf.root.location.y + 2.3 + lf["forward"]) < 1e-6
    pf.place(2000, (0.0, 0.0, 0.0), 0.0)
    land0 = pf.fall(2010, -2.0)                                          # its floor is dug away: straight down
    assert land0 == 2019 and (pf.pos_at(land0) - Vector((0.0, 0.0, -2.0))).length < 1e-9
    pf.hurt(2040, source=(0.0, -1.0, -2.0))                              # and a hit down there hops from that floor
    assert abs(pf.pos_at(2070).z + 2.0) < 1e-6 and abs(max(pf.pos_at(2040 + 0.5 * k).z for k in range(30)) + 2.0 - apex) < 0.01
    print("fall: 2 blocks in %d ticks (%.1f frames), 1 / 3 / 4 blocks in 5 / 9 / 10; from a stroll it drifts %.2f; "
          "legs +-%.0f degrees in the air, still on frame +%d" %
          (lf["ticks"], lf["ticks"] * TICK, lf["forward"], math.degrees(0.33), round(lf["still"] - end)))

    # ---- a result lobbed out of a 2 x 2 pit two deep (the game's throw falls back in)
    from .blocks import World

    pit = World()
    pit.fill(-5, -5, -3, 6, 6, -1, "blackstone")
    for x in (0, 1):
        for y in (0, 1):
            for z in (-2, -1):
                pit.set(x, y, z, None)
    pf.place(2100, (1.0, 1.5, -2.0), 0.0)                                # in the far half of the pit
    thrown = barter(pf, None, 2100, "gravel", toward=(1.0, -1.2, 0.0), admire_ticks=10, world=pit)
    pf.place(2200, (1.0, 1.5, -2.0), 0.0)
    lobbed = barter(pf, None, 2200, "ender_pearl", toward=(1.0, -1.2, 0.0), admire_ticks=10, world=pit, lob=True, count=2)
    assert thrown["rest"].z < -1.9 and (lobbed["rest"] - Vector((1.0, -1.2, 0.0))).length < 0.06
    assert thrown["item"].item_id == "gravel"
    pf.place(2300, (0.5, 0.5, -2.0), 0.0)
    steve.place(2300, (1.0, -1.2, 0.0), math.pi)
    rests = []
    for seed in range(3):
        b = barter(pf, None, 2300 + 30 * seed, "obsidian", toward=steve, admire_ticks=10, world=pit, lob=True, seed=seed)
        rests.append(b["rest"])
        assert abs(b["rest"].z) < 1e-6 and abs(math.hypot(b["rest"].x - 1.0, b["rest"].y + 1.2) - LOB_SHORT) < 0.06
    assert min((a - b).length for i, a in enumerate(rests) for b in rests[i + 1:]) > 0.3
    print("lob: from the far half of a 2 x 2 pit the game's throw rests at %s, lob=True at %s; three seeds rest %s" %
          (tuple(round(c, 2) for c in thrown["rest"]), tuple(round(c, 2) for c in lobbed["rest"]),
           [tuple(round(c, 2) for c in r[:2]) for r in rests]))

    # ---- on a Stage
    from . import shots
    from films import lookdev

    film = shots.Film(scene)
    st = lookdev.Stage(scene, film, None, None)
    s1, s2, s3 = st.shot("one", 1.5), st.shot("two", 1.0), st.shot("three", 1.0)
    for s in (s1, s2, s3):
        s.move((4.0, -6.0, 1.6), (0.0, 0.0, 1.0))
    sp = add_piglin(st, "stage_brute", "brute")
    si = add_item(st, "gold_ingot", "stage_ingot")
    sv = add_piglin(st, "stage_victim")
    assert add_piglin(st, "stage_brute") is sp
    sp.place(s2.frame_start, (0.0, 0.0, 0.0), 0.0)
    si.place(s2.frame_start, (1.0, 0.0, 0.0))
    sv.place(s1.frame_start, (0.0, 0.0, 0.0), 0.0)
    gone = sv.die(s1.frame_start + 4, camera=s1)                         # the puffs would last far into shot two
    cut = sv.last_death["burst"]
    early = poof((1.0, 0.0, 0.0), s2.frame_start - 8, camera=s2, size=(0.6, 1.8))    # in the air as shot two opens
    on = poof((1.0, 0.0, 0.0), s2.frame_start + 4, camera=s2, until=s3.frame_start + 6)
    free = poof((1.0, 0.0, 0.0), s2.frame_start + 4, camera=s2, until=False)
    st.use(s1, sv)
    st.use(s2, sp, si)
    st.hero(s2, "brute", sp)
    st.finish()

    def puffs(b, f):
        _evaluate(scene, f)
        return sum(1 for ob in b.objects if not ob.hide_render)

    _evaluate(scene, s1.frame_start)
    assert sp.head.hide_render and sp.weapon.hide_render and si.sprite.hide_render
    _evaluate(scene, s2.frame_start)
    assert not sp.head.hide_render and not sp.weapon.hide_render and not si.sprite.hide_render
    assert gone == s1.frame_start + 28 and puffs(cut, gone) == POOF_COUNT and puffs(cut, s1.frame_end) > 10
    assert all(puffs(cut, f) == 0 for f in range(s2.frame_start, s3.frame_end + 1)) and cut.frame_end == s1.frame_end
    assert puffs(early, s2.frame_start - 1) == 0 and puffs(early, s2.frame_start) == POOF_COUNT
    assert puffs(early, s2.frame_end) > 0 and puffs(early, s3.frame_start) == 0
    assert puffs(on, s3.frame_start + 5) > 0 and puffs(on, s3.frame_start + 6) == 0 and puffs(free, s3.frame_end) > 0
    assert all("+%g" % POOF_GLOW in ob.data.materials[0].name for ob in cut.objects)
    print("Stage: add_piglin / add_item register with st.cast; hidden outside their shots")
    print("poof with camera=<Shot>: %d puffs on the shot's last frame, none on the next shot's first; started 8 frames "
          "before a cut: none before it, %d on its first frame" % (puffs(cut, s1.frame_end), puffs(early, s2.frame_start)))
    print("check ok")


def _selftest(which):
    import os

    from . import quick

    def want(name):
        return not which or name in which

    def stage(preset="day", res=(540, 960), blur=False, block="polished_blackstone_bricks", half=7):
        scene = quick.reset()
        quick.setup(scene, res=res)
        sun = quick.light(scene, preset)
        if blur:                                                         # the films' shutter (look.setup_render)
            scene.render.use_motion_blur = True
            scene.render.motion_blur_shutter = 0.5
            scene.render.motion_blur_position = "START"
        stage.sun = sun
        stage.world = _floor(scene, block, half)
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

    def stills(scene, name, frames, **kw):
        paths = []
        for i, f in enumerate(frames):
            _evaluate(scene, f)
            paths.append(quick.render(scene, "%s_%d" % (name, i + 1)))
            print("wrote", paths[-1], "(frame %s)" % f)
        sheet(name, paths, **kw)

    if want("check"):
        _check()

    if want("lineup"):
        scene = stage(res=(960, 540))
        cast = [make_piglin("piglin"), make_piglin("brute", "brute"), make_piglin("baby", baby=True),
                ch.make_player("steve"), ch.make_villager("farmer", "farmer"),
                make_piglin("archer", weapon="crossbow", armor=("helmet",))]
        for i, c in enumerate(cast):
            c.place(1, ((i - 2.5) * 1.25, 0.0, 0.0), 0.0)
        cam = (1.2, -9.5, 1.5)
        for c in cast:
            c.look_at(1, cam, ease=0)
        _evaluate(scene, 1)
        quick.camera(scene, cam, (0.0, 0.0, 0.98), lens=40)
        print("wrote", quick.render(scene, "piglins_lineup"))

    if want("turn"):
        paths = []
        for kind, kw in (("piglin", {}), ("brute", {"kind": "brute"}), ("baby", {"baby": True})):
            scene = stage(res=(960, 540))
            tall = BABY_MODEL_HEIGHT if kind == "baby" else MODEL_HEIGHT
            gap = 0.85 * tall
            for i, deg in enumerate((0, 90, 180, 45)):                   # front, side, back, three-quarter
                p = make_piglin("%s_%d" % (kind, deg), **kw)
                p.place(1, ((i - 1.5) * gap, 0.0, 0.0), math.radians(deg))
            _evaluate(scene, 1)
            quick.camera(scene, (0.25 * tall, -3.6 * tall, 0.62 * tall), (0.0, 0.0, 0.5 * tall), lens=40)
            paths.append(quick.render(scene, "piglins_turn_" + kind))
            print("wrote", paths[-1])
        sheet("piglins_turn", paths, height=360)

    if want("armor"):
        sets = ((), ("helmet",), ("helmet", "chestplate"), ("helmet", "chestplate", "leggings", "boots"))
        paths = []
        for view, (deg, cam_y) in enumerate(((25, -7.2), (205, -7.2))):
            scene = stage(res=(960, 540))
            for i, armor in enumerate(sets):
                p = make_piglin("armor_%d" % i, armor=armor, weapon="crossbow" if i == 1 else "default")
                p.place(1, ((i - 1.5) * 1.7, 0.0, 0.0), math.radians(deg))
            _evaluate(scene, 1)
            quick.camera(scene, (0.5, cam_y, 1.25), (0.0, 0.0, 1.0), lens=40)
            paths.append(quick.render(scene, "piglins_armor_%d" % (view + 1)))
            print("wrote", paths[-1])
        sheet("piglins_armor", paths, height=360)

    if want("ears"):
        scene = stage(res=(480, 480))
        p = make_piglin("ears", weapon=None)
        p.place(1, (0.0, 0.0, 0.0), 0.0)
        end = p.walk(1, [(0.0, 0.0, 0.0), (0.0, -14.0, 0.0)], run=True)
        best = {}                                                        # the right ear farthest in and farthest out
        for f in range(12, end - 8):
            _evaluate(scene, f)
            a = p.ear_r.rotation_euler.y
            if "hi" not in best or a > best["hi"][1]:
                best["hi"] = (f, a)
            if "lo" not in best or a < best["lo"][1]:
                best["lo"] = (f, a)
        print("ears while chasing: right ear %.1f .. %.1f degrees (frames %d, %d)" %
              (math.degrees(best["lo"][1]), math.degrees(best["hi"][1]), best["lo"][0], best["hi"][0]))
        p2 = make_piglin("ears_still", weapon=None)
        p2.place(1, (3.0, 0.0, 0.0), 0.0)
        p2.flop_ears(1, 200)
        paths = []
        for i, (q, f) in enumerate(((p, best["lo"][0]), (p, best["hi"][0]), (p2, 30), (p2, 62))):
            _evaluate(scene, f)
            head = q.head.matrix_world.translation
            quick.camera(scene, (head.x + 0.5, head.y - 3.0, head.z + 0.55), (head.x, head.y, head.z + 0.22), lens=70)
            paths.append(quick.render(scene, "piglins_ears_%d" % (i + 1)))
            print("wrote", paths[-1], "(frame %d: ears %.1f / %.1f degrees)" %
                  (f, math.degrees(q.ear_l.rotation_euler.y), math.degrees(q.ear_r.rotation_euler.y)))
        sheet("piglins_ears", paths, height=360)

    if want("walk"):
        scene = stage(res=(480, 480), blur=False)
        p = make_piglin("walker")
        b = make_piglin("stroller", "brute")
        k = make_piglin("kid", baby=True)
        p.place(1, (-4.0, 0.0, 0.0), math.radians(90))
        end = p.walk(1, [(-4.0, 0.0, 0.0), (6.0, 0.0, 0.0)])
        b.place(1, (-4.6, 1.4, 0.0), math.radians(90))
        b.walk(1, [(-4.6, 1.4, 0.0), (6.0, 1.4, 0.0)], speed=1.2, swing=0.5)
        k.place(1, (-3.0, -1.0, 0.0), math.radians(90))
        k.walk(1, [(-3.0, -1.0, 0.0), (6.0, -1.0, 0.0)], speed=1.9)
        off = Vector((0.6, -6.5, 0.9))
        cam = quick.camera(scene, p.pos_at(1) + off, p.pos_at(1) + Vector((0.3, 0.0, 0.95)), lens=38)
        for i in range(3):
            ch._segment(cam, _LOC, i, [(1, (p.pos_at(1) + off)[i]), (end, (p.pos_at(end) + off)[i])], "LINEAR")
        w = p.last_walk
        sf = w["step_frames"]
        f0 = w["stance"][3][0]
        print("walk: %.2f blocks/s, swing %.1f degrees, a step every %.1f frames" % (w["speed"], math.degrees(w["swing"]), sf))
        stills(scene, "piglins_walk", [round(f0), round(f0 + sf / 2.0), round(f0 + sf), round(f0 + 1.5 * sf)])

    if want("admire"):
        scene = stage()
        p = make_piglin("admirer")
        p.place(1, (0.0, 0.0, 0.0), 0.0)
        p.admire(1)
        _evaluate(scene, 10)
        at = p.item_point(10, "off")
        print("admire: ingot centre", tuple(round(c, 3) for c in at), "| head pitch %.1f degrees" %
              math.degrees(p.head.rotation_euler.x))
        quick.camera(scene, (0.95, -2.5, 0.85), (0.03, -0.3, 1.42), lens=34)
        print("wrote", quick.render(scene, "piglins_admire"))

    if want("barter"):
        scene = stage(res=(640, 480))
        p = make_piglin("trader")
        steve = ch.make_player("steve")
        p.place(1, (0.0, 0.0, 0.0), 0.0)
        steve.place(1, (0.0, -3.6, 0.0), math.radians(180))
        steve.look_at(1, p, ease=0)
        p.look_at(1, steve, ease=0)
        ingot = mobs.make_dropped_item("gold_ingot")
        pearl = mobs.make_dropped_item("ender_pearl", count=3)
        cam_at = (6.2, -1.9, 1.35)
        steve.swing_arm(4)
        landed = throw_item(ingot, 4, steve, (0.0, -0.4, 1.2), seed=3)
        ingot.face(landed + 2, cam_at)
        ingot.animate(4, 80)
        take = max(landed + 6, 4 + int(PLAYER_DROP_DELAY_TICKS * TICK))
        beats = barter(p, ingot, take, pearl, toward=steve, admire_ticks=40, face=cam_at)
        print("barter (proof): ingot thrown on frame 4, lands %d at %s, beats %s" %
              (landed, tuple(round(c, 2) for c in ingot.rest_pos), {k: v for k, v in beats.items() if k not in ("item", "rest")}))
        quick.camera(scene, cam_at, (0.0, -1.9, 0.95), lens=30)
        stills(scene, "piglins_barter", [11, beats["pickup"] + 2, beats["pickup"] + 20, beats["throw"] + 5,
                                         beats["landed"] + 6], height=300)

    if want("swing"):
        scene = stage(res=(480, 640), blur=False)
        b = make_piglin("brute", "brute")
        steve = ch.make_player("steve")
        b.place(1, (0.0, 0.0, 0.0), math.radians(30))
        steve.place(1, (0.55, -1.25, 0.0), 0.0)
        steve.face(1, b, ease=0)
        b.look_at(1, steve, ease=0)
        b.aggro(1)
        b.attack(20)
        n = SWING_TICKS * TICK
        quick.camera(scene, (-3.3, -3.4, 1.5), (0.2, -0.5, 1.15), lens=34)
        stills(scene, "piglins_swing", [18, 20 + round(n * 0.3), 20 + round(n * 0.5), 20 + round(n * 0.85)], height=480)

    if want("dance"):
        scene = stage(res=(480, 640))
        p = make_piglin("dancer", weapon=None)
        p.place(1, (0.0, 0.0, 0.0), math.radians(15))
        p.dance(1, 80)
        quick.camera(scene, (0.6, -4.6, 1.3), (0.0, 0.0, 1.1), lens=36)
        period = 2.0 * math.pi / 40.0 * DANCE_PERIOD * TICK              # one bob: 11.3 frames
        stills(scene, "piglins_dance", [20, 20 + round(period / 3.0), 20 + round(2.0 * period / 3.0)], height=480)

    if want("hurt"):
        scene = stage(res=(640, 480))
        p = make_piglin("victim")
        steve = ch.make_player("steve")
        p.place(1, (0.0, 0.0, 0.0), math.radians(-90))
        steve.place(1, (-1.5, 0.0, 0.0), math.radians(90))
        steve.swing_arm(8)
        end = p.hurt(10, source=steve)
        print("hurt (proof): hit on frame 10, still again on frame", end)
        quick.camera(scene, (0.6, -7.0, 1.3), (0.6, 0.0, 1.2), lens=30)
        stills(scene, "piglins_hurt", [9, 11, 13, 16, 20, 23], height=300)

    if want("death"):
        scene = stage(res=(480, 640))
        p = make_piglin("dying", "brute")
        p.place(1, (0.0, 0.0, 0.0), math.radians(20))
        cam = quick.camera(scene, (1.0, -5.2, 1.5), (0.3, 0.0, 0.8), lens=30)
        gone = p.die(10, camera=cam, seed=4)
        print("death (proof): dies on frame 10, flat on frame %.1f, gone on frame %d" % (p.last_death["flat"], gone))
        stills(scene, "piglins_death", [14, 24, gone - 1, gone + 1, gone + 12, gone + 36], height=420)

    def pit_stage(res=(540, 720)):
        """A bastion floor with a pit 2 x 2 and two deep in plain blackstone (cells x 0..1, y 0..1), dim red air,
        warm lamps (one low in the pit), the films' shutter; returns (scene, World)."""
        from . import props
        from .blocks import World, new_collection

        scene = quick.reset()
        quick.setup(scene, res=res)
        scene.render.use_motion_blur = True
        scene.render.motion_blur_shutter = 0.5
        scene.render.motion_blur_position = "START"
        world = bpy.data.worlds.new("nether")
        world.use_nodes = True
        bg = world.node_tree.nodes["Background"]
        bg.inputs[0].default_value = (0.30, 0.09, 0.05, 1.0)
        bg.inputs[1].default_value = 0.35
        scene.world = world
        r = pix.rng(41)
        kinds = ["polished_blackstone_bricks"] * 6 + ["cracked_polished_blackstone_bricks"] * 2 + ["gilded_blackstone"]
        w = World()
        for x in range(-7, 9):
            for y in range(-6, 9):
                near = -2 <= x <= 3 and -2 <= y <= 3                     # the pit is dug in plain blackstone
                for z in (-3, -2, -1):
                    w.set(x, y, z, "blackstone" if near or z < -1 else kinds[int(r.integers(0, len(kinds)))])
        for x in (0, 1):
            for y in (0, 1):
                for z in (-2, -1):
                    w.set(x, y, z, None)
        for x in range(-7, 9):
            for z in range(0, 4):
                w.set(x, 8, z, "gold_block" if 0 <= x <= 2 and z < 2 else "polished_blackstone_bricks")
        w.cull_below = -3
        w.build(new_collection(scene, "set"))
        lights = new_collection(scene, "lights")
        for pos, energy in (((-3.0, -3.0, 4.0), 700.0), ((5.0, 3.0, 3.4), 420.0), ((1.0, 5.5, 3.0), 320.0), ((1.0, 1.0, 0.6), 90.0),
                            ((1.0, 1.0, -0.9), 22.0)):
            lamp = props.make_light("lantern", lights)
            lamp.location = pos
            lamp.data.energy = energy
        return scene, w

    if want("fall"):
        scene, w = pit_stage()
        a, b, c = make_piglin("first"), make_piglin("second", armor=("helmet",)), make_piglin("third", weapon="crossbow")
        a.place(1, (-3.0, 0.5, 0.0), math.radians(90))
        b.place(1, (-3.0, 1.5, 0.0), math.radians(90))
        c.place(1, (1.5, 5.4, 0.0), 0.0)
        end_a = a.walk(1, [(-3.0, 0.5, 0.0), (0.3, 0.5, 0.0)], ramp=(4, 0))          # 0.3 past the rim, no braking
        land_a = a.fall(end_a, -2.0)
        end_b = b.walk(15, [(-3.0, 1.5, 0.0), (0.3, 1.5, 0.0)], ramp=(4, 0))
        land_b = b.fall(end_b, -2.0)
        end_c = c.walk(24, [(1.5, 5.4, 0.0), (1.5, 1.7, 0.0)], ramp=(4, 0))
        land_c = c.fall(end_c, -2.0)
        for q, land in ((a, land_a), (b, land_b), (c, land_c)):
            q.look_at(land + 6, (1.0, -1.2, 1.6), ease=8)
            q.flop_ears(q.last_fall["still"], land_c + 60)
        print("fall (proof): first leaves the rim on frame %d and lands on %d at %s; second %d -> %d; third %d -> %d" %
              (end_a, land_a, tuple(round(v, 2) for v in a.pos_at(land_a)), end_b, land_b, end_c, land_c))
        quick.camera(scene, (5.6, -4.6, 5.4), (0.7, 1.0, -0.7), lens=30)
        stills(scene, "piglins_fall", [end_a - 3, end_a + 3, end_a + 7, end_b + 5, end_c + 5, land_c + 14], height=400)

    if want("lob"):
        scene, w = pit_stage()
        steve = ch.make_player("steve")
        steve.place(1, (1.0, -1.2, 0.0), math.pi)
        steve.look_at(1, (1.0, 1.0, -1.0), ease=0)
        near, far = make_piglin("near"), make_piglin("far", armor=("helmet",))
        near.place(1, (0.6, 0.5, -2.0), 0.0)
        far.place(1, (1.3, 1.5, -2.0), 0.0)
        cam_at = (-3.4, -2.6, 3.4)
        for q in (near, far):
            q.look_at(1, steve, ease=0)
        thrown = barter(near, None, 1, "gravel", toward=steve, admire_ticks=14, world=w, face=cam_at)        # the game's throw
        lobbed = barter(far, None, 1, "ender_pearl", toward=steve, admire_ticks=20, world=w, lob=True, count=2,
                        face=cam_at, seed=1)
        print("lob (proof): the game's throw from the near half leaves on frame %d and rests at %s; lob=True from the far "
              "half leaves on %d and rests at %s on frame %d" %
              (thrown["throw"], tuple(round(v, 2) for v in thrown["rest"]), lobbed["throw"],
               tuple(round(v, 2) for v in lobbed["rest"]), lobbed["landed"]))
        quick.camera(scene, cam_at, (0.9, 0.0, -0.3), lens=30)
        t = lobbed["throw"]
        stills(scene, "piglins_lob", [t - 3, t + 5, t + 11, t + 15, lobbed["landed"] + 8], height=400)

    if want("bastion"):
        from . import props
        from .blocks import World, new_collection

        scene = quick.reset()
        quick.setup(scene, res=(540, 960))
        world = bpy.data.worlds.new("nether")
        world.use_nodes = True
        bg = world.node_tree.nodes["Background"]
        bg.inputs[0].default_value = (0.30, 0.09, 0.05, 1.0)             # the Nether's dull red, dim
        bg.inputs[1].default_value = 0.35
        scene.world = world
        r = pix.rng(77)
        w = World()
        floor_kinds = ["polished_blackstone_bricks"] * 6 + ["cracked_polished_blackstone_bricks"] * 2 + ["blackstone"] * 2 + ["gilded_blackstone"]
        for x in range(-6, 7):
            for y in range(-5, 8):
                for z in (-3, -2, -1):
                    w.set(x, y, z, floor_kinds[int(r.integers(0, len(floor_kinds)))] if z == -1 else "blackstone")
        hole = (0, 0)
        for z in (-2, -1):
            w.set(hole[0], hole[1], z, None)
        for x, y in ((-3, 4), (3, 4)):                                   # basalt pillars, a wall behind
            for z in range(0, 4):
                w.set(x, y, z, "basalt", {"axis": "y"})
        for x in range(-6, 7):
            for z in range(0, 5):
                kind = "polished_blackstone_bricks" if (x + z) % 5 else "gilded_blackstone"
                w.set(x, 6, z, kind)
        w.set(-2, 3, 0, "gold_block")
        w.set(-2, 4, 0, "gold_block")
        w.set(-2, 4, 1, "gold_block")
        w.set(2, 3, 0, "chiseled_polished_blackstone")
        w.cull_below = -3
        w.build(new_collection(scene, "set"))
        lights = new_collection(scene, "lights")
        for pos, energy in (((-2.6, -2.4, 3.2), 520.0), ((3.2, 1.0, 2.6), 260.0), ((0.5, 0.5, 2.4), 160.0), ((0.5, 0.5, -0.4), 14.0)):
            lamp = props.make_light("lantern", lights)
            lamp.location = pos
            lamp.data.energy = energy
        centre = (hole[0] + 0.5, hole[1] + 0.5)
        trapped = make_piglin("trapped", armor=("helmet",))
        trapped.place(1, (centre[0], centre[1], -2.0), math.radians(-20))
        watchers = [make_piglin("watch_n"), make_piglin("watch_e", weapon="crossbow"), make_piglin("watch_w", "brute")]
        spots = [((centre[0] + 0.1, centre[1] + 1.3, 0.0)), ((centre[0] + 1.25, centre[1] + 0.35, 0.0)),
                 ((centre[0] - 1.25, centre[1] + 0.3, 0.0))]
        cam = (centre[0] + 2.0, centre[1] - 6.2, 5.6)
        trapped.look_at(1, cam, ease=0)
        for wt, at in zip(watchers, spots):
            wt.place(1, at, 0.0)
            wt.face(1, (centre[0], centre[1], 0.0), ease=0)
            wt.look_at(1, trapped, ease=0)
        _evaluate(scene, 1)
        quick.camera(scene, cam, (centre[0], centre[1] + 0.45, 0.55), lens=27)
        print("wrote", quick.render(scene, "piglins_bastion"))


if __name__ == "__main__":
    _selftest(set(sys.argv[1:]))
