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
                                            A BLOW THAT MEETS IT IN THE AIR (the game allows the next hit 12 frames
                                            after the last: a hen is then still floating down; also in a hop or a
                                            fall) does not lift it again, as in the game: it keeps its height and
                                            vertical speed, takes half its horizontal speed plus the new push (a
                                            hen: 4.5 blocks in all), and lands on the ground it left, when it would
                                            have landed anyway. Any frame is a valid frame for the next blow.
      die(frame, camera=None, attacker=None, knockback=True, max_back=None, poof=True, seed=0, village=None)
                                            -> frame + 24, the frame it is GONE: red and knocked back from `frame`,
                                            tips over to its left (flat after 16 frames), then vanishes and 20 white
                                            poof particles rise where it lay. Stays gone until its next place().
                                            A killing blow in the air: it tips over while it comes down.
      hop(frame, to=None) / fall(frame, to) -> landing frame
                                            a jump (apex 1.25: up one block and 1 forward in 11 frames) / stepping
                                            off an edge. A chicken flaps and sinks at 2.3 blocks/s (2 blocks: 24
                                            frames). Out of a walk too (no need to stop): the stride fades into the
                                            game's walk wave for the ground covered, the legs are straight again
                                            when it lands, and walk(landing frame, ...) goes on
      Chicken.flap(frame_start, frame_end)  only the wings, as while airborne (hop / fall / hurt call it themselves)
      eye_point(frame) / mouth_point(frame) middle of the head (what others look at and cameras focus on) / a point
                                            just in front of the muzzle or beak (hold the food out to there)
      size (hit box w, h), width, walk_speed, tempt_speed, run_speed, food (item ids), baby, species, kind,
      last_walk (dict: frames, blocks, steps, swing, cycle_frames, stance ...), bursts (its particle bursts)
      nod / shake / shiver / flinch (a small hop): inherited; swing_arm / raise_arm do nothing; hold / lie_down raise

  pen_set(b, x0, y0, x1, y1, gates=[(x, y)], fence="oak_fence", name="pen", clear="all") -> dict   THE PEN OF A FILM
      Real fence and fence-gate blocks on the ring of cells, built INTO the village: call it in the hook of
      village.build_village(scene, seed=1, edit=lambda b: animals.pen_set(b, 3, 27, 12, 36, gates=[(7, 27)],
      name="cow_pen")). The meadow's plants are removed where the fence stands (in the game a fence replaces the
      plant) and, clear="all", inside (tall grass hides a hen); the ground is levelled if it is not. Afterwards
      v.sets["cow_pen"] = dict(area, z, cells, gates, inside): wander(herd, f0, f1, pen["area"], z=pen["z"]).
      Anchors <name>_center and <name>_gate (one block outside the gate, facing in).
  make_pen(scene, x0, y0, x1, y1, z=0, gates=[(x, y)], fence="oak_fence", ground=None, name="pen") -> dict
      The same ring as a separate little World on top of whatever is there: FOR TESTS AND BARE FLOORS
      (ground="grass_block" lays one). On the village's meadow the plants of the ring cells would stand inside the
      posts and rails: films use pen_set.
  pen_area(x0, y0, x1, y1) -> area      the free rectangle inside a ring of fence blocks on those cells
  wander(animals, frame_start, frame_end, area, seed=0, place=True, speed=None, gait="planted", clearance=None,
         activity=1.0, watch=None, z=0.0, avoid=()) -> {name: [("stand" | "walk" | "turn", first, last, target), ...]}
      A PEN IN ONE CALL: every animal alternates standing, looking around and short straight walks inside the
      rectangle area = (x0, y0, x1, y1), each with its own timing. place=True puts them on free spots at
      frame_start; place=False goes on from where they stand (a walk that is still running ends first: call it
      shot after shot). No body leaves the rectangle or comes closer than its own width (cow 0.75, hen 0.5;
      clearance=) to another body or the edge, on any frame, whoever of two stops first (measured over 80 seeds x
      10 s for both proof pens, and a minute: tools/check_animals_pens.py). An animal rests only where it can
      turn on the spot (feet 1.70 from the edge for a cow, 1.00 for a hen), so none is boxed in at the fence; one
      that is hemmed in by the others takes a step or two or turns to face another way ("turn").
      avoid = who else is in the pen and was keyed BEFORE this call (the player, the cow that follows him, the hen
      that is hit; or fixed (x, y, radius) circles): the herd keeps its clearance from them on every frame and
      never stops where they will pass later. Key the heroes first, wander() last.
  pen_report(animals, f0, f1, area) -> (smallest gap between two bodies, smallest distance to the edge)

  follow(animals, leader, frame_start, frame_end, stop=2.5, speed=None, look="eyes", clearance=None, avoid=())
      -> frame the last of them has come to rest
      TemptGoal: the animal (or a LIST of them: a herd) walks after a player holding its food whenever he is
      further than 2.5 blocks, at up to its tempted speed (2.75 blocks/s), and keeps its head on him. look="eyes"
      is the game (his eyes), look=<the item object> or "item" (leader.held) looks at the food instead.
      A herd in ONE call fans out behind him and comes to rest in an arc, side by side, each facing him (three cows
      35 degrees and 1.45 blocks apart, four hens 24 degrees and 1.0; six cows or eight hens fill the half circle
      behind him at stop 2.5). A call per animal works too: each later one knows those keyed before it for the same
      leader (while their follows overlap in time) and takes the next free place on one side. Bodies never come
      closer than 0.15 block (clearance=; the game's Entity.push keeps the hit boxes apart): they bear off round
      one another and round anything in avoid=[...] (Animals / Characters keyed before, (x, y, radius)); a
      leader who walks into them moves them aside. Also a calf after its mother: follow(calf, cow, f0, f1,
      stop=3.0)  (FollowParentGoal). Key the leader's walk first. Start with the animal roughly facing him (or
      face() it first): one that has its back to him swings round at the game's rate, 46 degrees in a frame.
  hand_item(player, item, frame_start, frame_end) -> Object
      'wheat' (cows), 'wheat_seeds' (chickens), 'bucket' ... in Steve's right hand for the frames [frame_start,
      frame_end), with the game's item arm pose. Unlike Character.hold it is keyed, so the next shot can show an
      empty hand. frame_end is REQUIRED (the shot's frame_end + 1; None raises). The item is also hidden whenever
      the player is (Stage.finish), and a later hand_item() for him takes over from its frame_start.
  love(animal, frame, camera, frame_end=None, seed=0) -> [Burst]
      Fed: 7 hearts on `frame`, then one every 12 frames until frame_end (default 3 s; the game 30 s).
  milk(player, frame, frame_start, frame_end) -> (bucket, milk_bucket)
      Item 'bucket' in his hand from frame_start, his arm swings, and from `frame` it is item 'milk_bucket' until
      frame_end (required, as for hand_item).
  lay_egg(chicken, frame, seed=0, until=None, stage=None, shot=None) -> engine.mobs DroppedItem
      Item 'egg' pops out at her feet (hops 0.38 up, lands after 11 frames, lies still 0.3-0.9 block away after
      18; egg.rest_pos says where), then bobs and spins. Hens lay every 5-10 minutes in the game.
      In a Stage film: stage=st, shot=s (a Stage hides whatever no shot uses; shot= is st.use(s, egg)).
  drop_loot(animal, frame, items=None, seed=0, stage=None, shot=None) -> [DroppedItem]
      On the frame of the killing blow: cow 'beef' x 2 + 'leather', chicken 'chicken' + 'feather' (babies nothing).
      In a Stage film: stage=st, shot=s, as for the egg.
  poof(target, frame, camera, seed=0, size=None, count=20) -> Burst       only the death cloud, for anything
  knock_flight / knockback_track / air_track / walk_distances / death_angle / hurt_sheet / animal_sheet: the
  numbers and textures behind the above.
  Constants: COW_WALK, COW_TEMPT, COW_PANIC, CHICKEN_WALK, CHICKEN_PANIC, CHICK_FOLLOW, COW_FOOD, CHICKEN_FOOD,
  EGG_ITEM, BUCKET_ITEM, MILK_ITEM, TEMPT_STOP, FOLLOW_ROOM, HURT_FRAMES, DEATH_FRAMES, LOOT, FACTS.

USING THEM IN A FILM (st = films.lookdev.Stage, s = st.shot(...), v = the Village)
    def edit(b): animals.pen_set(b, 3, 27, 12, 36, gates=[(7, 27)], name="cow_pen")     # 10 x 10 cells, 8.75 inside
    v = village.build_village(scene, seed=1, edit=edit); pen = v.sets["cow_pen"]
    cows = [animals.add_cow(st, "cow%d" % i) for i in range(4)] + [animals.add_cow(st, "calf", baby=True)]
    steve.place(f0, spot, yaw); wheat = animals.hand_item(steve, "wheat", f0, s.frame_end + 1)
    end = animals.follow(daisy, steve, f0, f0 + 50, look=wheat)           # she walks up and stops 2.3 blocks away
    end = animals.follow([daisy, bessie, clover], steve, f0, walk_end + 20, look=wheat)   # or a herd after his walk
    steve.swing_arm(end + 6); animals.love(daisy, end + 8, camera=s, frame_end=s.frame_end + 1)
    animals.wander(cows, s.frame_start, s.frame_end + 1, pen["area"], seed=3, z=pen["z"], avoid=[steve, daisy])
    st.use(s, steve, daisy, *cows)                                        # (the herd last: it keeps out of their way)
    bucket, full = animals.milk(steve, f0 + 20, f0, s.frame_end + 1)      # in the next shot, after his place()
    egg = animals.lay_egg(hen, f0 + 14, stage=st, shot=s)
    up = hen.hurt(f, attacker=steve, max_back=0.9); hen.walk(up, [hen.pos_at(up), away], run=True)
    hen.hurt(f, attacker=steve); gone = hen.die(f + 12, camera=s, attacker=steve)   # the game's two quick blows
    loot = animals.drop_loot(hen, f + 12, stage=st, shot=s)
  Rules:
    - Key every animal in frame order, place() before everything else in a shot. A call replaces what the animal
      was doing from its frame on (a hurt(), hop() or fall() in mid-walk ends the walk there, cleanly).
    - wander() only knows the animals in its list and what is in avoid=. Key Steve, a cow that follows him or a
      hen that gets hit first and pass them as avoid=[...]; the herd then stays out of their way for the whole
      call. follow() likewise: pass standing animals it must walk round as avoid=[...].
    - Particles (hearts, poof) are world objects with their own lifetimes (hearts 20 frames, poof up to 99, half of
      it gone after 45): a cut that jumps in time needs engine.fx.stop_particles(first frame of the new shot).
    - hand_item() / milk() after the player's place(); place() him again only at their frame_end. A held item is a
      flat sprite along the hand: edge-on from his side, readable from behind his shoulder and from above.
    - A walk that opens a shot in stride: place() and walk() 12+ frames before the cut (only if the animal is not
      in the shot before: its place() would cut that shot's action short).
    - The red flash is a second set of meshes (built on the first hurt / die); never key hide_render on an animal's
      parts yourself: use show(). st.hero(shot, "hen", hen) is its head (a chick: its body).
    - A camera low behind a rail has the fence across the lower half: hens need the lens above the top rail.

SIZES (blocks; hit box in brackets)
    cow      1.5625 to the horn tips, back 1.375, 0.75 wide, nose 0.94 in front of its feet, rump 0.625 behind
             [0.9 x 1.4]; eyes 1.25 up.     calf   1.0 to the horn tips, back 0.75, 0.5 wide, 1.06 long [0.45 x 0.7]
    chicken  0.94 to the top of the head, back 0.69, 0.5 wide over the wings, beak 0.5 in front, tail 0.25 behind
             [0.4 x 0.7].                    chick  0.375 tall, 0.25 wide, 0.31 long [0.3 x 0.4]
    Steve is 1.875, a villager 1.99, a fence 1.0 as drawn (1.5 as an obstacle): a cow looks over it, a hen is
    hidden by the rails from a low camera. PEN SIZES: 10 x 10 cells for five cows and a calf (six cows still all
    walk, 6 to 24 times a minute each); 8 x 9 cells for six hens and two chicks. A cow needs an area at least
    3.4 blocks wide to turn in (a hen 2.0): in a narrower lane they keep the clearance but mostly stand.

GAIT (QuadrupedModel.setupAnim, ChickenModel.setupAnim, LivingEntity.updateWalkAnimation, WalkAnimationState)
    The game: legs cos(p * 0.6662 [+ pi]) * 1.4 * s, pairs right hind + left front and left hind + right front
    (a hen: right, left); s approaches min(4 * blocks moved per tick, 1) and p grows by s every tick (three times
    as fast for a baby). So a strolling cow swings +-28 degrees once per 2.36 blocks (32 frames) while such a step
    covers 0.71 block: every sole slides 0.47 block per step. gait="vanilla" is exactly that, no bob.
    gait="planted" keeps pairs, speed and (about) the game's swing for that speed, and shortens the cycle to what
    the legs can cover: cow 18 frames, calf 9, hen 7, chick 3 (their legs are 5 and 2 pixels long: a blur at the
    game's speed in either gait, as in the game; speed=1.2 calms a hen in a close shot). A sole on the ground
    strays under 0.005 block (measured, also round corners and in turns on the spot, where the legs lean
    sideways a little to stay put; up to 0.03 in a herd of six that jostles for room); the swinging pair passes
    it in the middle of the step, at ground height: the legs are rigid, there is no knee to lift a hoof with.
    The body sinks up to 0.08 block with every step of a cow so that the standing soles stay ON the ground
    (bob=1); a hen sinks only 0.03 and a chick not at all (their feet lift 0.05 / 0.03 block at the ends of a
    step instead: at 4 steps a second a full bob would make the body tremble).
    These, the rounded corners, the stepping turn and a landing with straight legs (the game lets the wave run on
    for half a second after a hop) are the module's only departures from the game.
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
    within 5 blocks at its panic speed, again and again for about 2 s. A mob can be hit again 10 ticks after a
    hit (LivingEntity.hurtServer: damageCooldownTime = 20, a hit counts once it is 10 or less). knockback(): horizontal speed =
    half the current + 0.4 away; vertical = min(0.4, half the current + 0.4) ONLY if it stands on the ground: a
    blow in the air leaves the vertical speed alone. A fist does 1 damage: a hen (4) dies of the fourth blow, a
    sword kills her with the first.
  - Death: deathTime counts 20 ticks; LivingEntityRenderer tips the body about its feet, 90 degrees *
    sqrt((t - 1) * 0.08), red all the while, legs straight; on tick 20 it is removed and 20 'poof' particles
    (generic_7 ... generic_0, white-grey, 0.2-1.4 wide) appear in its upright hit box and rise. The loot pops out
    on tick 0. Nothing else: no blood, no sound-dependent effect.
  - Entity.push: mobs whose hit boxes overlap are pushed apart (0.05 blocks per tick each): a herd after one
    player stands side by side round him, never inside one another.

MEASURED IN THE PROOFS (out/test/animals_*.png, check_animals_*.png)
  - walk: cow 1 block in 24 frames, 2 in 38, 4 in 65 (always + 10 frames of rolling out); hen 1 in 19, 4 in 45.
    A cow turns 90 degrees in 10 frames with two steps.
  - a hen hit on frame f and again on f + 12: 0.58 up at the second blow, on the ground on f + 20 either way,
    4.5 blocks from where she stood (one blow: 2.35). Killed by the second blow: gone on f + 36, the poof at
    ground level 4.5 blocks away.
  - follow: Steve walks 7-9 blocks at 1.6 blocks/s, three cows trail him in a fan and stand 20 frames after he
    stops, 2.4 blocks from him.
  - hearts 0.3-0.6 block wide, start up to 0.9 beside the animal and 0.5-1.9 above its feet, rise 0.65.
  - poof: 20 puffs, the last gone 24-99 frames after the death (median 45), rising to 2 blocks (a few to 3.8).
  - cameras that worked: pen from outside, 4.3 above the ground, 24 mm, 5-9 blocks away (landscape proofs); a cow
    two-shot in profile 50 mm from 6.6 blocks; over Steve's left shoulder at the coming cow 26 mm f/3.2; the
    bucket from behind his right shoulder and above 24 mm; a herd after Steve from 6 blocks to his side and 4.6
    up, 30 mm; hens through a fence from 1.3 high need the lens above the top rail (1.0).

Self-test:  $BPY -m engine.animals [check lineup views walk flap hop wheat herd egg hurt hurt2 die pen]
    (no argument = check: 72 numeric checks, about 40 s; give one or two picture names per call to stay under
    300 s; also views_cow / views_calf / views_chicken / views_chick, walk_calf, walk_chick, walk_cow_vanilla,
    walk_chicken_vanilla, pen_cow, pen_chicken). Stills: out/test/animals_*.png.
    $BPY -m tools.check_animals_film [shot:offset ...]   a four-shot farm film through films.lookdev.Stage and
    engine.look (16 checks; stills out/test/check_animals_*.png).
    $BPY -m tools.check_animals_pens [seeds]             wander() under stress: every pair of bodies against the
    clearance it was promised, over many seeds, a minute-long pen, avoid=, a narrow lane (numbers only).
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
FOLLOW_ROOM = 0.15                                       # blocks two followers' bodies keep apart: the game's Entity.push
#                                                          parts the 0.9-wide cow hit boxes, the bodies are 0.75 wide
PLAYER_RADIUS = 0.3                                      # half the player's hit box (EntityTypes.PLAYER sized(0.6, 1.8))

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
    "second blow": "possible 10 ticks after a hit (damageCooldownTime 20, counts at <= 10); in the air: no lift, half the horizontal speed + 0.4",
    "herd": "Entity.push parts overlapping hit boxes by 0.05 blocks per tick each: followers stand side by side round the player",
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


def knock_flight(strength=KNOCKBACK, away=(1.0, 0.0), height=0.0, velocity=(0.0, 0.0, REST_VY), max_back=None,
                 fall=1.0, max_ticks=200):
    """LivingEntity.knockback + travelInAir: the mob's state after tick 0, 1, 2 ... as (x, y, height above the
    ground, vx, vy, vz), blocks and blocks per tick, x / y from where the blow met it, until it lies still.

    The blow (LivingEntity.knockback): horizontal speed = half of what it had + strength along `away` (a unit
    vector); vertical speed = min(0.4, half of what it had + strength) if it stands ON THE GROUND, and UNCHANGED
    if it is in the air (height > 0: a second blow does not lift it again). Every tick: move, then vertical speed =
    (v - 0.08) * 0.98 and horizontal speed * 0.546 (it was on the ground when the tick began) or * 0.91 (in the
    air). fall = Chicken.aiStep's 0.6 on a falling chicken. max_back = room behind it, along `away`.
    strength 0 = no blow: the flight it is in just goes on."""
    ax, ay = float(away[0]), float(away[1])
    vx, vy, vz = (float(c) for c in velocity)
    h = max(float(height), 0.0)
    on_ground = h <= 1e-9
    if strength > 0.0:
        vx, vy = vx / 2.0 + ax * strength, vy / 2.0 + ay * strength
        if on_ground:
            vz = min(0.4, vz / 2.0 + strength)
    elif on_ground and math.hypot(vx, vy) < 0.003:
        return [(0.0, 0.0, 0.0, 0.0, 0.0, vz)]
    x = y = 0.0
    out = [(x, y, h, vx, vy, vz)]
    for _tick in range(max_ticks):
        drag = GROUND_DRAG if on_ground else AIR_DRAG
        x += vx
        y += vy
        if max_back is not None:
            over = x * ax + y * ay - float(max_back)
            if over > 0.0:
                along = vx * ax + vy * ay
                x, y, vx, vy = x - ax * over, y - ay * over, vx - ax * along, vy - ay * along
        h += vz
        on_ground = h <= 0.0
        if on_ground:
            h, vz = 0.0, 0.0
        vz = (vz - GRAVITY) * 0.98
        vx *= drag
        vy *= drag
        if not on_ground and vz < 0.0:
            vz *= fall
        if math.hypot(vx, vy) < 0.003:                                    # LivingEntity.aiStep
            vx = vy = 0.0
        out.append((x, y, h, vx, vy, vz))
        if on_ground and vx == 0.0 and vy == 0.0:
            break
    return out


def knockback_track(strength=KNOCKBACK, max_back=None, fall=1.0, max_ticks=200, height=0.0, velocity=None):
    """knock_flight() seen from the side: [(blocks back, blocks up)] after tick 0, 1, 2 ... until the mob lies
    still. From a standing start: 0.96 up, 2.0 back, on the ground after 10 ticks. height / velocity = (back, up)
    blocks per tick: the blow meets it in the air (it is not lifted again, see knock_flight)."""
    vel = (0.0, 0.0, REST_VY) if velocity is None else (float(velocity[0]), 0.0, float(velocity[1]))
    return [(s[0], s[2]) for s in knock_flight(strength, (1.0, 0.0), height, vel, max_back, fall, max_ticks)]


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


def walk_distances(total, speed):
    """Blocks covered after 0, 1, 2 ... frames of a walk of `total` blocks at `speed` blocks/s, as Animal.walk keys
    it: the mob is driven for total / speed seconds, v' = (cruise - v) / tau, then rolls out, v' = -v / tau (tau =
    2 frames: the ground's friction 0.546 per tick), and is on its target BRAKE_TAUS * tau frames later."""
    per_frame = max(float(speed), 1e-3) / FPS
    push = total / per_frame                                             # frames for which it is driven
    n = max(2, int(math.ceil(push + BRAKE_TAUS * SPEED_TAU)))
    tau = SPEED_TAU
    v_end = per_frame * (1.0 - math.exp(-push / tau))
    d_end = per_frame * (push - tau * (1.0 - math.exp(-push / tau)))

    def dist(t):
        if t <= push:
            return per_frame * (t - tau * (1.0 - math.exp(-t / tau)))
        return d_end + v_end * tau * (1.0 - math.exp(-(t - push) / tau))

    ds = [min(dist(float(k)), total) for k in range(n + 1)]
    ds[-1] = total
    return ds


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
        self._flap_run = None              # (first frame, [(flap, flapSpeed, flapping) per tick]) of the last flap()
        self._air = None                   # the flight it is in (a knock-back, hop or fall): see _air_state
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
        self._air = None
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
        ds = walk_distances(total, speed)
        n = len(ds) - 1
        frames = [float(f0 + k) for k in range(n + 1)]
        spots = [route.point(d) for d in ds]
        yaws = [heading0 + route.turned(d) for d in ds]
        self._travel(frames, spots, yaws, gait=gait, swing=swing, bob=bob)
        self.last_walk.update(speed=float(speed), blocks=total, frames=(f0, f0 + n),
                              corners=[(round(rad, 3), round(math.degrees(turn), 1)) for _a, _b, turn, rad in route.arcs])
        return f0 + n

    def _travel(self, frames, spots, yaws, gait="planted", swing=None, bob=None):
        """Key a root trajectory (a position and a yaw per entry of `frames`) and the legs that carry it."""
        self._air = None
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

    def _legs_vanilla(self, frames, fts, dist, speed0=0.0, blend=0.0, cap=1.0, land=0.0):
        """The game's own leg wave for a keyed trajectory: WalkAnimationState ticked along the distance covered.
        speed0 = the animation speed it starts with; blend = frames over which the pose the legs are in fades into
        the wave (a hop or a fall out of a planted stride); cap = the largest animation speed (the game: 1);
        land = frames before the end over which the wave dies away, so that the legs are straight when the
        trajectory ends (a landing: in the game the wave runs on for half a second while the feet stand)."""
        f0, f1 = frames[0], frames[-1]
        scale = BABY_ANIM_SCALE if self.baby else 1.0
        speed, pos, prev = float(speed0), self._walk_pos, 0.0
        times, vals, peak = [f0], [None], 0.0
        for k in range(1, 6000):
            t = f0 + k * TICK
            if land > 0.0 and t >= f1 - 1e-6:
                times.append(f1)
                vals.append(0.0)
                break
            d = float(np.interp(min(t, f1), fts, dist))
            speed += (min(ANIM_PER_BLOCK * (d - prev), cap) - speed) * ANIM_LERP
            prev = d
            pos += speed
            peak = max(peak, speed)
            times.append(t)
            vals.append(math.cos(pos * scale * LEG_RATE) * LEG_SWING * min(speed, 1.0)
                        * (_smooth((f1 - t) / land) if land > 0.0 else 1.0))
            if t >= f1 and speed < 0.004:
                break
        vals[-1] = 0.0
        self._walk_pos = pos
        a, b = self.gait_groups
        for sign, group in ((1.0, a), (-1.0, b)):
            for leg in group:
                ob = self.legs[leg]
                mine = [None] + [sign * v for v in vals[1:]]
                if blend > 0.0:
                    now = ch._val(ob, _ROT, 0, f0)
                    for i in range(1, len(mine)):
                        u = _smooth((times[i] - f0) / blend)
                        mine[i] = now + (mine[i] - now) * u
                _run(ob, _ROT, 0, times, mine)
        if self.last_walk is not None:
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

    def _air_state(self, frame):
        """(height above the ground it will come down on, (vx, vy, vz) in blocks per tick, that ground's z) while a
        knock-back, hop or fall keyed earlier still carries the animal at `frame`; None when it stands or walks."""
        air = self._air
        if air is None or not (air["f0"] - 1e-6 <= frame < air["rest"] - 1e-6):
            return None
        states = air["states"]
        k = min(max(int((frame - air["f0"]) / TICK + 1e-6), 0), len(states) - 1)
        z = self.pos_at(frame).z
        ground = air["ground"]
        if air.get("ground0") is not None and (k < 0.5 * (len(states) - 1) or z < ground - 1e-6):
            ground = air["ground0"]                                      # a hop UP: still over the ground it left
        return max(z - ground, 0.0), states[k][3:6], ground

    def _settle(self, f0, legs=True, frames=3):
        """Out of a planted stride: over `frames` frames the body comes back up to its rest height and the legs'
        sideways lean (and, legs=True, their swing) goes to zero. Nothing is keyed where nothing is off."""
        steps = [float(f0 + k) for k in range(frames + 1)]

        def ease(ob, path, i, rest):
            if ch._find(ob, path, i) is None:
                return
            now = ch._val(ob, path, i, f0)
            if abs(now - rest) > 1e-6:
                _run(ob, path, i, steps, [None] + [now + (rest - now) * _smooth(k / float(frames)) for k in range(1, frames + 1)])

        ease(self.hips, _LOC, 2, self._rest(self.hips, _LOC, 2))
        for ob in self.legs.values():
            ease(ob, _ROT, 1, 0.0)
            if legs:
                ease(ob, _ROT, 0, 0.0)

    def _fly(self, f0, here, there, heights):
        """Key a flight from `here` to `there` with a height per tick; returns the landing frame."""
        before = self.pos_at(f0 - TICK)
        self._halt(f0)
        n = len(heights) - 1
        frames = [f0 + k * TICK for k in range(n + 1)]
        for i in (0, 1):
            _run(self.root, _LOC, i, frames, [here[i] + (there[i] - here[i]) * k / float(n) for k in range(n + 1)])
        zs = [here.z + h for h in heights[:-1]] + [there.z]
        _run(self.root, _LOC, 2, frames, zs)
        # the legs: as the game, the walk animation goes on with the ground covered (LivingEntity.calculateEntityAnimation
        # counts the horizontal move, also in the air); a planted stride fades into it, the body comes back up
        span = math.hypot(there.x - here.x, there.y - here.y)
        self._settle(f0, legs=span <= 0.05)
        if span > 0.05:
            # (a hop keyed longer than the game's, which covers what a walk does in that time, would throw the legs
            #  out to 80 degrees: in the air they swing no wider than at one and a half times its walking pace)
            cap = min(1.0, 1.5 * ANIM_PER_BLOCK * self.walk_speed / 20.0)
            speed0 = min(ANIM_PER_BLOCK * math.hypot(here.x - before.x, here.y - before.y), cap)
            self._legs_vanilla(frames, np.array(frames), np.array([span * k / float(n) for k in range(n + 1)]),
                               speed0=speed0, blend=3.0, cap=cap, land=4.0)
        step = ((there.x - here.x) / float(n), (there.y - here.y) / float(n))
        states = [((there.x - here.x) * k / float(n), (there.y - here.y) * k / float(n), zs[k] - there.z, step[0], step[1],
                   zs[min(k + 1, n)] - zs[k]) for k in range(n + 1)]
        self._air = dict(f0=float(f0), land=frames[-1], rest=frames[-1], states=states, ground=float(there.z),
                         ground0=float(here.z) if there.z > here.z + 1e-6 else None)
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

    def _knock(self, f0, attacker, knockback, max_back, flail, state=None):
        """The knock-back from frame f0 and (flail) the legs of a mob that was hit; returns (landing, rest) frames.
        state = its _air_state at f0, read BEFORE the halt: a blow that meets it in the air does not lift it again
        (LivingEntity.knockback), it flies on from the height and with the speed it has and comes down on the
        ground it left."""
        strength = KNOCKBACK * (float(knockback) if not isinstance(knockback, bool) else (1.0 if knockback else 0.0))
        here, away = self.pos_at(f0), self._away(f0, attacker)
        height, velocity, ground = state if state is not None else (0.0, (0.0, 0.0, REST_VY), here.z)
        track = knock_flight(strength, (away.x, away.y), height, velocity, max_back, fall=self.info["fall"])
        n = len(track) - 1
        landing = rest = float(f0)
        if n > 0:
            frames = [f0 + k * TICK for k in range(n + 1)]
            _run(self.root, _LOC, 0, frames, [here.x + q[0] for q in track])
            _run(self.root, _LOC, 1, frames, [here.y + q[1] for q in track])
            _run(self.root, _LOC, 2, frames, [here.z] + [ground + q[2] for q in track[1:]])
            air = [k for k in range(n + 1) if track[k][2] > 0.0]
            landing = f0 + (max(air) + 1) * TICK if air else float(f0)
            rest = frames[-1]
            self._air = dict(f0=float(f0), land=landing, rest=rest, states=track, ground=float(ground), ground0=None)
            if air:
                self._airborne(f0, landing)
        if flail:
            self._settle(f0, legs=False)
            # LivingEntity.handleDamageEvent: walkAnimation.setSpeed(1.5); then the usual update every tick
            scale = BABY_ANIM_SCALE if self.baby else 1.0
            speed, pos = HURT_ANIM_SPEED, self._walk_pos
            times, vals = [float(f0), f0 + TICK], [None, math.cos(pos * scale * LEG_RATE) * LEG_SWING]
            for k in range(1, 400):
                q0, q1 = track[min(k - 1, n)], track[min(k, n)]
                speed += (min(ANIM_PER_BLOCK * math.hypot(q1[0] - q0[0], q1[1] - q0[1]), 1.0) - speed) * ANIM_LERP
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
        blocks of room behind it (a fence). A walk that is running stops here. A blow that meets it IN THE AIR (the
        second hit on a hen, which the game allows 10 ticks = 12 frames after the first while she floats for 20;
        or in a hop or a fall) does not lift it again: it keeps its height and vertical speed, takes half its
        horizontal speed plus the new push, and comes down on the ground it left. Returns the frame it stands
        again."""
        f0 = int(round(frame))
        state = self._air_state(f0)
        self._halt(f0)
        if flash:
            self._ensure_twins()
            self._flash.append((f0, f0 + HURT_FRAMES))
            self._sync()
        landing, _rest = self._knock(f0, attacker, knockback, max_back, flail=True, state=state)
        return int(math.ceil(max(landing, f0 + 1)))

    def die(self, frame, camera=None, attacker=None, knockback=True, max_back=None, poof=True, seed=0, village=None,
            glow=None):
        """The game's death on `frame`: red from then on, knocked back like any blow, legs straight, and from one
        tick later the body tips over to its LEFT about its feet (90 degrees * sqrt((tick - 1) * 0.08): flat after
        13.5 ticks). On tick 20 (frame + 24, the return value) it is gone and the 20 white poof particles appear
        around its upright hit box and rise (camera = the Shot that films it, a Film or a camera object; they face
        it). Bloodless. It stays gone until its next place(). A killing blow that meets it in the air (see hurt())
        lets the body tip over while it comes down; the poof starts where the body is on the last frame."""
        f0 = int(round(frame))
        gone = f0 + DEATH_FRAMES
        state = self._air_state(f0)
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
        self._knock(f0, attacker, knockback, max_back, flail=False, state=state)
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
        if self._flap_run is not None:                                   # still beating from the flight before:
            g0, old = self._flap_run                                     # carry on from where the wings are
            if g0 - 1e-6 <= f0 < g0 + (len(old) - 1) * TICK:
                phase, speed, flapping = old[int((f0 - g0) / TICK + 1e-6)]
        states = [(phase, speed, flapping)]
        for k in range(1, 4000):
            in_air = f0 + (k - 1) * TICK < f1 - 1e-6
            speed = ch._clamp(speed + (FLAP_UP if in_air else FLAP_DOWN), 0.0, 1.0)
            if in_air:
                flapping = 1.0
            flapping *= FLAP_DECAY
            phase += flapping * FLAP_STEP
            states.append((phase, speed, flapping))
            if not in_air and speed <= 0.0:
                break
        self._flap = phase % (2.0 * math.pi)
        self._flap_run = (f0, states)
        times, vals = [], []
        for k, ((p0, s0, _a), (p1, s1, _b)) in enumerate(zip(states, states[1:])):
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
def _cast(stage, shot, things):
    """Register dropped items with a films.lookdev.Stage and, given the shot, declare them visible in it."""
    if stage is None:
        if shot is not None:
            raise ValueError("shot= needs stage=: the Stage that owns the shot")
        return
    for it in things:
        stage.cast[it.name] = it
    if shot is not None:
        stage.use(shot, *things)


def lay_egg(chicken, frame, seed=0, until=None, stage=None, shot=None, name=None):
    """A hen lays an egg on `frame` (Chicken.aiStep: every 6000-11999 ticks; item 'egg'): an item entity appears
    at her feet with the game's toss (hops 0.38, lands after 9 ticks, lies still 0.3-0.9 block away, at most 1.3,
    after 15), then bobs and spins until `until` (default: 20 s). In a Stage film pass stage=st AND shot=s: a
    Stage hides every cast member that no shot uses, so an egg registered with stage= alone is never seen (the
    same as st.use(s, egg) afterwards; for more shots st.use(other_shot, egg)).
    Returns the engine.mobs DroppedItem (.sprite is the focus / hero target, .rest_pos where it lies)."""
    f0 = int(round(frame))
    egg = mobs.make_dropped_item(EGG_ITEM, seed=seed, name=name or ("%s_egg_%d" % (chicken.name, f0)))
    egg.drop(f0, chicken.pos_at(f0), seed=seed)
    egg.animate(f0, f0 + 480 if until is None else until)
    _cast(stage, shot, [egg])
    return egg


LOOT = {"cow": (("beef", 2), ("leather", 1)), "chicken": (("chicken", 1), ("feather", 1)), "calf": (), "chick": ()}


def drop_loot(animal, frame, items=None, seed=0, until=None, stage=None, shot=None):
    """What a killed animal leaves, as item entities tossed up from where it stands ON the frame of the killing
    blow (LivingEntity.die drops the loot at once, while the body still tips over). items = [(item id, count), ...];
    default: the loot tables' typical roll: cow ('beef', 2) and ('leather', 1) (the game: 1-3 beef, 0-2 leather),
    chicken ('chicken', 1) and ('feather', 1) (1 raw chicken, 0-2 feathers), babies nothing. An animal that burns
    drops 'cooked_beef' / 'cooked_chicken'. They bob and spin until `until` (default 20 s). In a Stage film pass
    stage=st AND shot=s (or st.use(s, *loot) afterwards): a Stage hides every cast member that no shot uses, so
    loot registered with stage= alone is never seen. Returns the list of engine.mobs DroppedItems."""
    f0 = int(round(frame))
    out = []
    for i, (item_id, count) in enumerate(LOOT[animal.kind] if items is None else items):
        it = mobs.make_dropped_item(item_id, count=count, seed=seed * 17 + i, name="%s_%s_%d" % (animal.name, item_id, f0))
        it.drop(f0, animal.pos_at(f0), seed=seed * 17 + i)
        it.animate(f0, f0 + 480 if until is None else until)
        out.append(it)
    _cast(stage, shot, out)
    return out


def _sync_hand(player):
    """Rewrite the visibility of the player's hand items: each is rendered on its own frames, and only while the
    player's arm is (Character.show, which a Stage calls for every shot, does not know these items)."""
    arm = player.arm_r
    fc = ch._find(arm, "hide_render", 0)
    keyed = fc is not None and len(fc.keyframe_points) > 0
    cuts = sorted({int(round(kp.co.x)) for kp in fc.keyframe_points}) if keyed else []

    def shown(f):
        return fc.evaluate(f) < 0.5 if keyed else not arm.hide_render

    for ob, a, b in player.__dict__.get("_hand_items", ()):
        if b <= a:
            mobs._visibility_curve(ob, [(a, False)], before=False)
            continue
        frames = [a] + [c for c in cuts if a < c < b] + [b]
        mobs._visibility_curve(ob, [(f, f < b and shown(f)) for f in frames], before=False)


def hand_item(player, item, frame_start, frame_end=None, collection=None):
    """An item in the player's right hand for the frames [frame_start, frame_end): 'wheat', 'wheat_seeds', 'bucket'
    ... (an item id) or an object from engine.props.make_item. It sits exactly where Character.hold puts an item
    and the arm is carried in the game's item pose for those frames, but it is NOT player.held: its visibility is
    its own, so one Steve can hold wheat in one shot and nothing in the next (Character.hold cannot be keyed).
    frame_end is REQUIRED (None raises): the shot's frame_end + 1. An item without an end would stay in the film.
    The item is also hidden whenever the player is (player.show(), which Stage.finish calls), and a later
    hand_item() for the same player takes over from its frame_start: a hand holds one thing.
    Call it AFTER the player's place() for that shot, and place() him again only at or after frame_end.
    Returns the item object: a focus / hero target, and follow(..., look=<it>)."""
    from . import fx, props

    if getattr(player, "arm_r", None) is None:
        raise ValueError("hand_item() needs the player (a Character with arms)")
    if frame_end is None:
        raise ValueError("hand_item(): frame_end is required: pass the shot's frame_end + 1 (an item without an end "
                         "would stay in the film, also in shots the player is not in)")
    f0, f1 = int(round(frame_start)), int(round(frame_end))
    if f1 <= f0:
        raise ValueError("hand_item(): frame_end %d is not after frame_start %d" % (f1, f0))
    col = collection if collection is not None else fx._collection()
    ob = props.make_item(item, col) if isinstance(item, str) else item
    ob.parent = player.arm_r
    ob.matrix_parent_inverse = Matrix.Identity(4)
    ob.matrix_basis = ch._held_matrix("hand", player.model_scale)
    ob.hide_render = ob.hide_viewport = True
    held = player.__dict__.setdefault("_hand_items", [])                 # [[object, first frame, end frame]]
    for rec in held:
        if rec[1] < f0 < rec[2]:
            rec[2] = f0                                                  # what he held until now ends here
    held.append([ob, f0, f1])
    if "_hand_show" not in player.__dict__:                              # from now on show() takes the items along
        inner = player.show

        def show(frame, visible=True):
            """Character.show, and the hand items of engine.animals.hand_item with it."""
            out = inner(frame, visible)
            _sync_hand(player)
            return out

        player._hand_show = inner
        player.show = show
    _sync_hand(player)
    ch._cut(player.arm_r, _ROT, 0, f0, ch.ITEM_ARM_PITCH)               # ArmPose.ITEM: 18 degrees forward
    rest = player._rest(player.arm_r, _ROT, 0)
    if abs(ch._val(player.arm_r, _ROT, 0, f1) - ch.ITEM_ARM_PITCH) < 1e-6:
        ch._cut(player.arm_r, _ROT, 0, f1, rest)
    return ob


def milk(player, frame, frame_start, frame_end=None, collection=None):
    """The milking beat: the player holds an empty 'bucket' from frame_start, uses it on the cow on `frame` (his
    arm swings, furthest forward on `frame`) and from that frame on it is a 'milk_bucket' (AbstractCow.mobInteract:
    adult cows only, no particles), until frame_end (REQUIRED: the shot's frame_end + 1, see hand_item). Two
    hand_item()s and Character.swing_arm: call it AFTER the player's place() and look_at() for that shot.
    Returns (bucket, milk_bucket)."""
    f = int(round(frame))
    if frame_end is None:
        raise ValueError("milk(): frame_end is required: pass the shot's frame_end + 1")
    if not int(round(frame_start)) < f < int(round(frame_end)):
        raise ValueError("milk(): the use frame %d must lie between frame_start and frame_end" % f)
    bucket = hand_item(player, BUCKET_ITEM, frame_start, f, collection)
    full = hand_item(player, MILK_ITEM, f, frame_end, collection)
    ch._cut(player.arm_r, _ROT, 0, int(round(frame_start)), ch.ITEM_ARM_PITCH)
    player.swing_arm(f - 2)
    return bucket, full


def _circles(thing, frame):
    """[(x, y, radius)] the circles that cover something standing in an animal's way at `frame`: an Animal's body
    (nothing once it is dead and gone), any other Character (0.3 round its feet: the player's hit box is 0.6 wide)
    or a fixed (x, y, radius)."""
    if isinstance(thing, Animal):
        if thing.gone_at(frame):
            return []
        return thing.body_points(thing.pos_at(frame), thing.yaw_at(frame))
    if isinstance(thing, ch.Character):
        q = thing.pos_at(frame)
        return [(q.x, q.y, PLAYER_RADIUS)]
    x, y, r = thing
    return [(float(x), float(y), float(r))]


def _apart(ca, cb):
    """(gap, ux, uy): the smallest distance between two sets of circles and the unit vector from the first set to
    the second at the pair that is closest (gap None when a set is empty)."""
    best = (None, 1.0, 0.0)
    for xa, ya, ra in ca:
        for xb, yb, rb in cb:
            d = math.hypot(xb - xa, yb - ya)
            g = d - ra - rb
            if best[0] is None or g < best[0]:
                best = (g, (xb - xa) / d, (yb - ya) / d) if d > 1e-9 else (g, 1.0, 0.0)
    return best


def _slot_angle(a, b, stop, room):
    """Radians two animals need between them on a circle of radius `stop` round the one they follow, both facing
    him, for their bodies to keep `room` blocks apart (bisection on _gap; pi when the circle is too small)."""
    def gap(t):
        return _gap(a, (stop, 0.0), -math.pi / 2.0, b, (stop * math.cos(t), stop * math.sin(t)),
                    math.atan2(-math.cos(t), math.sin(t)))

    lo, hi = 0.0, math.pi
    if gap(hi) < room:
        return math.pi
    for _i in range(30):
        mid = (lo + hi) / 2.0
        if gap(mid) < room:
            lo = mid
        else:
            hi = mid
    return hi


def _isotonic(vals):
    """The non-decreasing sequence nearest to `vals` (least squares; pool adjacent violators)."""
    blocks = []
    for v in vals:
        blocks.append([float(v), 1])
        while len(blocks) > 1 and blocks[-2][0] / blocks[-2][1] > blocks[-1][0] / blocks[-1][1]:
            t, c = blocks.pop()
            blocks[-1][0] += t
            blocks[-1][1] += c
    return [t / c for t, c in blocks for _i in range(c)]


def follow(animals, leader, frame_start, frame_end, stop=TEMPT_STOP, speed=None, look="eyes", gait="planted",
           swing=None, bob=None, clearance=None, avoid=()):
    """An animal, or a LIST of them, follows a player who holds their food (TemptGoal): whenever `leader` (a
    Character) is further than `stop` (2.5 blocks) it walks toward him, never faster than its tempted speed (cow
    2.75 blocks/s, chicken 2.75) and no faster than he walks away, and it keeps looking at him. look = "eyes": at
    his eyes, which is what the game does; "item": at the item in his hand (leader.held); or any point / Object.

    A HERD: pass all of them in one call (or call it once per animal: a later call knows the animals of the earlier
    calls for the same leader and walks round them; the earlier ones keep their paths). Each gets its own place
    on the stop circle, side by side in the order they stood round him at frame_start, so they fan out behind him
    as they walk and come to rest in an arc facing him (three cows: 31 degrees apart, 1.35 blocks from centre to
    centre). As the game's Entity.push does, no two bodies come closer than `clearance` (default 0.15 block: the
    game's 0.9-wide cow hit boxes keep the 0.75-wide bodies that far apart): one that would is moved aside. The
    same holds for everything in `avoid` (Animals / Characters keyed before this call, or (x, y, radius)) and for
    the leader himself if he walks into them. Seven cows or nine hens fill the half circle behind a player at
    stop 2.5: more of them need a second call with a larger stop.

    Key the leader's walk first. After frame_end the leader counts as standing where he is then. Returns the frame
    the last of them has come to rest (>= frame_end)."""
    herd = [animals] if isinstance(animals, ch.Character) else list(animals)
    f0, f1 = int(round(frame_start)), int(round(frame_end))
    if not herd:
        return f1
    n = len(herd)
    room = FOLLOW_ROOM if clearance is None else float(clearance)
    vmax = [(a.tempt_speed if speed is None else float(speed)) / FPS for a in herd]
    gain = 1.0 - math.exp(-1.0 / SPEED_TAU)
    turn = 1.0 - 0.7 ** (1.0 / TICK)                                     # LivingEntity.tickHeadTurn: 0.3 of the gap a tick
    P = [a.pos_at(f0) for a in herd]
    Y = [a.yaw_at(f0) for a in herd]
    V = [0.0] * n
    D = [None] * n                                                       # the way each is going (kept while it brakes)
    round_ = [{} for _i in range(n)]                                     # which way round each passes what is in its way
    known = leader.__dict__.setdefault("_followers", [])                 # [(animal, first frame, last frame, stop)]
    earlier = []
    for rec in known:                                                    # calls that overlap this one in time
        if rec[2] >= f0 - 24 and rec[1] <= f1 and all(rec[0] is not q for q in herd) \
                and all(rec[0] is not e[0] for e in earlier):
            earlier.append(rec)
    solid = [e[0] for e in earlier] + [o for o in avoid if all(o is not q for q in herd) and all(o is not e[0] for e in earlier)]

    def bearing(q, lead):
        return math.atan2(q.y - lead.y, q.x - lead.x)

    lead = leader.pos_at(f0)
    raw = [bearing(q, lead) for q in P]
    ref = math.atan2(sum(math.sin(t) for t in raw), sum(math.cos(t) for t in raw))
    B = [ref + ch._wrap(t - ref) for t in raw]                           # unwrapped, followed from frame to frame
    order = sorted(range(n), key=lambda i: B[i])
    offs = [0.0]
    for k in range(n - 1):
        offs.append(offs[-1] + _slot_angle(herd[order[k]], herd[order[k + 1]], stop - 0.1, room + 0.05))
    span = 2.0 * math.pi - (_slot_angle(herd[order[-1]], herd[order[0]], stop - 0.1, room + 0.05) if n > 1 else 0.0)
    if offs[-1] > span > 0.0:                                            # more than the circle holds: squeeze (and push)
        offs = [o * span / offs[-1] for o in offs]
    EB = [ref + ch._wrap(bearing(e[0].pos_at(f0), lead) - ref) for e in earlier]
    side = [[1.0 if ch._wrap(EB[j] - B[i]) >= 0.0 else -1.0 for j in range(len(earlier))] for i in range(n)]
    eneed = [[_slot_angle(herd[i], earlier[j][0], stop - 0.1, room + 0.05) for j in range(len(earlier))] for i in range(n)]

    frames, spots, yaws = [float(f0)], [[q.copy() for q in P]], [list(Y)]
    f = f0
    while True:
        f += 1
        lead = leader.pos_at(min(f, f1))
        for i in range(n):
            B[i] += ch._wrap(bearing(P[i], lead) - B[i])
        flat = _isotonic([B[order[k]] - offs[k] for k in range(n)])
        theta = [0.0] * n
        for k in range(n):
            theta[order[k]] = flat[k] + offs[k]
        active = []
        for j, (other, a0, a1, its_stop) in enumerate(earlier):
            q = other.pos_at(f)
            EB[j] += ch._wrap(bearing(q, lead) - EB[j])
            active.append(a0 <= f <= a1 or math.hypot(q.x - lead.x, q.y - lead.y) < its_stop + 1.0)
        blocks = [(_circles(o, f), room) for o in solid] + [(_circles(leader, f), 0.0)]
        for i in range(n):
            lo, hi = -1e9, 1e9
            for j in range(len(earlier)):
                if not active[j]:
                    continue
                rel = ch._wrap(EB[j] - B[i])
                if side[i][j] * rel < 0.0 and abs(rel) > math.pi / 2.0:
                    rel += side[i][j] * 2.0 * math.pi
                if side[i][j] > 0.0:
                    hi = min(hi, B[i] + rel - eneed[i][j])
                else:
                    lo = max(lo, B[i] + rel + eneed[i][j])
            theta[i] = (lo + hi) / 2.0 if lo > hi else ch._clamp(theta[i], lo, hi)
            q = P[i]
            to_lead = Vector((lead.x - q.x, lead.y - q.y))
            to_slot = Vector((lead.x + stop * math.cos(theta[i]) - q.x, lead.y + stop * math.sin(theta[i]) - q.y))
            far = to_slot.length
            driven = to_lead.length > stop
            want = min(far, vmax[i]) if driven else 0.0
            if driven and far > 0.05:                                    # (closer than that it rolls out as it goes)
                way = to_slot / far
                if D[i] is not None and way.dot(D[i]) < 0.0:
                    V[i] = 0.0                                           # its place is behind it now: stop, then go back
                D[i] = way
            V[i] += (want - V[i]) * gain
            if V[i] < 2e-4:
                V[i] = 0.0
            if V[i] > 0.0 and D[i] is not None:
                go = D[i]
                mine = herd[i].body_points(q, Y[i])
                for k, (circles, keep) in enumerate(blocks[:-1]):        # something in its way: it bears off and goes
                    g, ux, uy = _apart(mine, circles)                    # round it, always the same way round
                    if g is None or g >= keep + 0.6 or D[i].x * ux + D[i].y * uy <= 0.0:
                        round_[i].pop(k, None)
                        continue
                    if k not in round_[i]:                               # the side its way leans to, seen from the middle
                        cx = sum(c[0] for c in circles) / len(circles) - sum(c[0] for c in mine) / len(mine)
                        cy = sum(c[1] for c in circles) / len(circles) - sum(c[1] for c in mine) / len(mine)
                        round_[i][k] = 1.0 if D[i].x * -cy + D[i].y * cx >= 0.0 else -1.0
                    w = ch._clamp((keep + 0.6 - g) / 0.45, 0.0, 1.0)
                    bent = go * (1.0 - w) + Vector((-uy, ux)) * (round_[i][k] * w)
                    if bent.length > 1e-6:
                        go = bent.normalized()
                P[i] = Vector((q.x + go.x * V[i], q.y + go.y * V[i], q.z))
                at_him, at_slot = math.atan2(to_lead.x, -to_lead.y), math.atan2(go.x, -go.y)
                # it faces the way it goes; over the last block (and while it trails him) it turns to him
                aim = at_him + ch._wrap(at_slot - at_him) * (1.0 if round_[i] else ch._clamp(far, 0.0, 1.0))
                Y[i] += ch._wrap(aim - Y[i]) * turn
        # Entity.push: bodies that would overlap are moved apart (half each; all of it if the other was keyed before)
        for _pass in range(4):
            cover = [herd[i].body_points(P[i], Y[i]) for i in range(n)]
            moved = False
            for i in range(n):
                for j in range(i + 1, n):
                    g, ux, uy = _apart(cover[i], cover[j])
                    if g is not None and g < room - 1e-6:
                        d = (room - g) / 2.0
                        P[i] = Vector((P[i].x - ux * d, P[i].y - uy * d, P[i].z))
                        P[j] = Vector((P[j].x + ux * d, P[j].y + uy * d, P[j].z))
                        cover[i], cover[j] = herd[i].body_points(P[i], Y[i]), herd[j].body_points(P[j], Y[j])
                        moved = True
                for circles, keep in blocks:
                    g, ux, uy = _apart(cover[i], circles)
                    if g is not None and g < keep - 1e-6:
                        P[i] = Vector((P[i].x - ux * (keep - g), P[i].y - uy * (keep - g), P[i].z))
                        cover[i] = herd[i].body_points(P[i], Y[i])
                        moved = True
            if not moved:
                break
        frames.append(float(f))
        spots.append([q.copy() for q in P])
        yaws.append(list(Y))
        if f >= f1 and all(v == 0.0 for v in V):
            break
        if f > f1 + 72:
            break
    # an animal that is held up (no room at its place) pushes on without moving: the walk ends when all stand still
    last = len(frames) - 1
    while last > 0 and frames[last - 1] >= f1 and all(
            (spots[last - 1][i] - spots[-1][i]).length < 1e-4 and abs(yaws[last - 1][i] - yaws[-1][i]) < 1e-4 for i in range(n)):
        last -= 1
    frames = frames[:last + 1]
    end = int(frames[-1])
    for i, a in enumerate(herd):
        a._travel(frames, [spots[k][i] for k in range(last + 1)], [yaws[k][i] for k in range(last + 1)],
                  gait=gait, swing=swing, bob=bob)
        if look is not None:
            target = leader if look == "eyes" else (leader.held if look == "item" else look)
            if target is None:
                raise ValueError("follow(look='item'): %s holds nothing (leader.hold(props.make_item('wheat')))" % leader.name)
            a.track(f0, end, target)
        known.append((a, f0, end, float(stop)))
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
    not touched. FOR TESTS AND BARE FLOORS: on the village's meadow the plants of the ring cells stay and stand
    inside posts and rails, which the game cannot show; a film's pen is pen_set(), built into the village.
    Returns dict(world, objects, area = pen_area(...), cells = the ring, gates)."""
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


def pen_set(b, x0, y0, x1, y1, gates=(), fence="oak_fence", name="pen", clear="all", open_gates=False, level=True):
    """THE PEN OF A FILM: the same ring of fence and gate blocks as make_pen, but built INTO the village, so the
    meadow's grass tufts and flowers are gone where the fence stands (in the game a fence replaces the plant).
    Call it inside the village's edit hook:

        def edit(b):                                   # b = the village builder (engine/village.py: FILM SETS)
            animals.pen_set(b, 3, 27, 12, 36, gates=[(7, 27)], name="cow_pen")
        v = village.build_village(scene, seed=1, edit=edit)
        area, z = v.sets["cow_pen"]["area"], v.sets["cow_pen"]["z"]       # for wander(..., area, z=z)

    clear = "all" (default): no plants on the ring or inside it (tall grass hides a hen; a tuft is as tall as a
    chick) | "ring": only where the fence stands | "tall": the ring, and the two-block tall grass inside.
    The ring and the inside are reserved (nothing is sown there later). level=True re-levels the pen's columns
    to the height most of them have (the meadow north of the village is flat up to y 52; a pen across one of its
    steps would otherwise have a fence on two levels); level=False raises if they differ.
    Registers the anchors <name>_center (a look target in the middle, at the ground) and, per gate,
    <name>_gate (<name>_gate_2 ...): a standing spot one block outside the gate, facing in.
    Returns (and stores as Village.sets[name]) dict(area, z, cells, gates, inside = the cells inside the ring)."""
    xa, xb, ya, yb = min(x0, x1), max(x0, x1), min(y0, y1), max(y0, y1)
    if xb - xa < 2 or yb - ya < 2:
        raise ValueError("pen_set: the ring %s leaves no room inside" % ((xa, ya, xb, yb),))
    cols = [(x, y) for x in range(xa, xb + 1) for y in range(ya, yb + 1)]
    heights = [b.ground(x, y) for x, y in cols]
    if any(h is None for h in heights):
        raise ValueError("pen_set %r: no terrain under part of %s (b.extend_terrain first)" % (name, (xa, ya, xb, yb)))
    z = max(set(heights), key=heights.count)
    if len(set(heights)) > 1:
        if not level:
            raise ValueError("pen_set %r: the ground under %s is not level (%s)" % (name, (xa, ya, xb, yb), sorted(set(heights))))
        for (x, y), h in zip(cols, heights):
            if h != z:
                b.set_ground(x, y, z)
    gates = [tuple(g) for g in gates]
    ring = [c for c in cols if c[0] in (xa, xb) or c[1] in (ya, yb)]
    inside = [c for c in cols if c not in ring]
    for g in gates:
        if g not in ring:
            raise ValueError("pen_set %r: the gate %s is not on the ring" % (name, (g,)))
    gate_id = fence.replace("_fence", "_fence_gate")
    for x, y in cols:
        on_ring = (x, y) in ring
        if on_ring or clear == "all":
            b.clear_plants(x, y)
        elif clear == "tall" and b.w.block_id(x, y, z) == "tall_grass":
            b.clear_plants(x, y)
        b.reserved.add((x, y))
        if not on_ring:
            continue
        if (x, y) in gates:
            facing = "south" if y == ya else ("north" if y == yb else ("west" if x == xa else "east"))
            b.w.set(x, y, z, gate_id, {"facing": facing, "open": "true" if open_gates else "false", "in_wall": "false",
                                       "powered": "false"})
        else:
            b.w.set(x, y, z, fence)
    res = dict(area=pen_area(xa, ya, xb, yb), z=float(z), cells=ring, gates=gates, inside=inside, name=name)
    b.v.anchors[name + "_center"] = ((xa + xb + 1) / 2.0, (ya + yb + 1) / 2.0, float(z))
    for k, (gx, gy) in enumerate(gates):
        out = (0, -1) if gy == ya else ((0, 1) if gy == yb else ((-1, 0) if gx == xa else (1, 0)))
        spot = (gx + 0.5 + out[0], gy + 0.5 + out[1])
        b.anchor(name + "_gate" + ("" if k == 0 else "_%d" % (k + 1)), spot, yaw=math.atan2(-out[0], out[1]), replace=True)
    b.v.sets[name] = res
    return res


def _gap(a, pa, ya, b, pb, yb):
    """Smallest distance between the bodies of two animals standing at (pa, yaw ya) and (pb, yaw yb)."""
    return min(math.hypot(xa - xb, ya_ - yb_) - ra - rb
               for xa, ya_, ra in a.body_points(pa, ya) for xb, yb_, rb in b.body_points(pb, yb))


def _inside(animal, pos, yaw, area, margin):
    """True when the body of an animal standing at `pos` keeps `margin` from every side of the rectangle `area`."""
    x0, y0, x1, y1 = area
    return all(x0 + r + margin <= x <= x1 - r - margin and y0 + r + margin <= y <= y1 - r - margin
               for x, y, r in animal.body_points(pos, yaw))


def _reach(animal):
    """Radius round an animal's feet that its body stays inside however it turns on the spot."""
    return max(abs(ahead) + r for ahead, r in animal.info["circles"])


def _settles(animal, frame, limit=240):
    """The first frame >= `frame` from which the keyed position and yaw of an animal no longer change (a walk that
    began earlier runs on until then)."""
    last = float(frame)
    for path, i in ((_LOC, 0), (_LOC, 1), (_ROT, 2)):
        fc = ch._find(animal.root, path, i)
        if fc is None:
            continue
        for kp in fc.keyframe_points:
            if frame < kp.co.x <= frame + limit:
                last = max(last, kp.co.x)
    return int(math.ceil(last - 1e-6))


def wander(animals, frame_start, frame_end, area, seed=0, place=True, speed=None, gait="planted", clearance=None,
           activity=1.0, watch=None, z=0.0, avoid=()):
    """Background life for a pen: every animal alternates standing, looking around and short straight walks inside
    the rectangle area = (x0, y0, x1, y1) from frame_start to frame_end, each with its own timing.

    place=True (default) first puts them on random free spots at frame_start (hard cut; z = the ground there);
    place=False starts from where they stand, inside the area (one that is still walking finishes that walk
    first). Nobody leaves the rectangle and no body comes closer than `clearance` (default: its own body width;
    cow 0.75, chicken 0.5; for a pair the larger of the two) to another body or to the edge, also while both
    move and whichever of them stops first: every turn, walk and the stand after it is checked frame by frame
    against what the others are keyed to do before it is keyed itself. An animal comes to rest only where it can
    turn on the spot whichever way it faces (its feet at least its reach + clearance from the edge: cow 1.70,
    calf 1.13, hen 1.00, chick 0.45), so none is ever boxed in against a fence; an area too narrow for that (a cow
    needs 3.4 blocks, a hen 2.0) falls back to bodies that only keep the clearance, and may then stand for long.
    Walks are 1.2-3.2 blocks for a cow, 0.8-2.6 for a chicken, at the game's strolling speed (speed= overrides,
    blocks/s), after a turn on the spot. activity scales how restless they are (1 = a walk every 3-4 s each);
    watch = a Character they look at now and then while he is within 6 blocks. avoid = what else stands or moves
    in the area and was keyed BEFORE this call: the player, a cow that follows him, a hen that is hit ...
    (Characters / Animals: their keyed positions frame by frame; or fixed (x, y, radius) circles, a trough): the
    herd keeps its clearance from them too. For a fenced pen pass pen_area(...) of the fence ring (or the 'area'
    make_pen / pen_set return). Returns {name: [(kind, first frame, last frame, target), ...]} with kind 'stand'
    | 'walk'. Deterministic for a seed. pen_report() measures the result."""
    f0, f1 = int(round(frame_start)), int(round(frame_end))
    animals = list(animals)
    avoid = [o for o in avoid if all(o is not a for a in animals)]
    area = (min(area[0], area[2]), min(area[1], area[3]), max(area[0], area[2]), max(area[1], area[3]))
    room = {a.name: (a.width if clearance is None else float(clearance)) for a in animals}
    rngs = {a.name: pix.rng(9173 * (int(seed) + 1) + 31 * i + 7) for i, a in enumerate(animals)}
    samples = {}                           # name -> {frame: (x, y, yaw)} of what is keyed; later frames: the last one
    ends = {}
    events = {a.name: [] for a in animals}
    zone = {}                              # name -> where its feet may come to rest, or None (the area is too narrow)
    for a in animals:
        m = _reach(a) + room[a.name]
        zone[a.name] = (area[0] + m, area[1] + m, area[2] - m, area[3] - m) \
            if area[2] - area[0] > 2.0 * m and area[3] - area[1] > 2.0 * m else None
    # what stands or moves in the area besides the herd: per thing [(frame, circles)] whenever its circles change
    tracks = []
    for o in avoid:
        line, was = [], None
        for f in range(f0, f1 + 73):
            now = _circles(o, f)
            key = [tuple(round(c, 4) for c in q) for q in now]
            if key != was:
                line.append((f, now))
                was = key
        tracks.append(([q[0] for q in line], line))

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

    def rests(a, pos, yaw):
        """May the animal come to rest at (pos, yaw) as far as the edge goes?"""
        zn = zone[a.name]
        if zn is None:
            return _inside(a, pos, yaw, area, room[a.name])
        return zn[0] <= pos[0] <= zn[2] and zn[1] <= pos[1] <= zn[3]

    def others(a, f, pos, yaw, disc=False):
        """Is the body at (pos, yaw) on frame f clear of everybody and everything else there then? disc=True: the
        whole circle it sweeps when it turns on the spot there."""
        mine = [(pos[0], pos[1], _reach(a))] if disc else a.body_points(pos, yaw)
        for b in animals:
            if b is a or b.name not in samples:
                continue
            x, y, byaw = pose(b, f)
            if _apart(mine, b.body_points((x, y), byaw))[0] < max(room[a.name], room[b.name]):
                return False
        for stamps, line in tracks:
            g = _apart(mine, line[max(bisect.bisect_right(stamps, f) - 1, 0)][1])[0]
            if g is not None and g < room[a.name]:
                return False
        return True

    def stays(a, f, pos, yaw):
        """May the animal stand at (pos, yaw) from frame f on: nothing in `avoid` comes by there later in the call
        (it would stand in the player's way: a standing animal does not step aside)."""
        mine = a.body_points(pos, yaw)
        for stamps, line in tracks:
            for _f, circles in line[max(bisect.bisect_right(stamps, f) - 1, 0):]:
                g = _apart(mine, circles)[0]
                if g is not None and g < room[a.name]:
                    return False
        return True

    def clear(a, f, pos, yaw):
        """Is the body at (pos, yaw) on frame f inside the area and clear of everybody else there then?"""
        return rests(a, pos, yaw) and others(a, f, pos, yaw)

    def passes(a, t, x, y, yaw, heading, target, length, v, home):
        """Can the animal turn on the spot to `heading` and (length > 0) walk to `target`, starting on frame t,
        and stand there, with what everybody else is keyed to do? The schedule is the one Animal.walk keys."""
        swing = ch._wrap(heading - yaw)
        turn_frames = 0 if abs(swing) <= (0.03 if length > 0.0 else 1e-4) else \
            max(4, int(round(TURN_FRAMES * min(1.0, abs(swing) / 0.8))))
        ds = walk_distances(length, v) if length > 0.0 else [0.0]
        last = turn_frames + len(ds) - 1
        if not stays(a, t + last, target, heading):
            return False
        for k in range(0, max(last, max(ends.values()) - t) + 1):       # ... and while the others finish their walks
            if k <= turn_frames:
                spot, hyaw = (x, y), yaw + swing * (_smooth(k / float(turn_frames)) if turn_frames else 1.0)
            elif k < last:
                u = ds[k - turn_frames] / length
                spot, hyaw = (x + (target[0] - x) * u, y + (target[1] - y) * u), heading
            else:
                spot, hyaw = target, heading
            edge = rests(a, spot, hyaw) if home else _inside(a, spot, hyaw, area, 0.0)
            if not edge or not others(a, t + k, spot, hyaw):
                return False
        return True

    # ---- where they start
    queue = []
    if place:
        placer = pix.rng(4057 * (int(seed) + 1) + 3)
        for i, a in enumerate(animals):
            zn = zone[a.name] or area
            found = []                                                   # of a few free spots, the one with most room
            for attempt in range(4000):
                pos = (float(placer.uniform(zn[0], zn[2])), float(placer.uniform(zn[1], zn[3])))
                yaw = float(placer.uniform(-math.pi, math.pi))
                if clear(a, f0, pos, yaw) and stays(a, f0, pos, yaw):
                    near = [pose(b, f0) for b in animals if b is not a and b.name in samples]
                    found.append((min([math.hypot(pos[0] - o[0], pos[1] - o[1]) for o in near] or [0.0]), pos, yaw))
                    if len(found) >= 6:
                        break
            if not found:
                raise ValueError("wander: no room for %s in %s (%d animals): a bigger area or a smaller clearance"
                                 % (a.name, tuple(round(c, 2) for c in area), len(animals)))
            _room, pos, yaw = max(found, key=lambda c: c[0])
            a.place(f0, (pos[0], pos[1], z), yaw)
            record(a, f0, f0)
            queue.append((f0, i))
    else:
        for i, a in enumerate(animals):
            free = max(f0, min(_settles(a, f0), f1))                     # a walk that is still running: let it end
            record(a, f0, free)
            queue.append((free, i))

    # ---- what they do, in the order of the frames at which each is free again
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
        go = spin = None
        keen = not first and r.random() < ch._clamp(0.8 * activity, 0.0, 1.0)
        if keen:
            lo, hi = a.info["stroll"]
            v = a.walk_speed if speed is None else float(speed)
            # one that stands where it may not rest (place=False, put there by the director) may leave from there
            home = rests(a, (x, y), yaw) or not _inside(a, (x, y), yaw, area, 0.0)
            plans = []                             # (heading, length, must it end where it can turn freely)
            for _try in range(60):                 # ahead first, then anywhere, then shorter
                plans.append((yaw + float(r.uniform(-1.0, 1.0)) * (math.pi if _try >= 15 else 1.6),
                              float(r.uniform(lo, hi)) * (1.0 if _try < 40 else 0.6), _try < 30))
            turn0 = float(r.uniform(0.0, math.pi / 6.0))
            for length in (lo, 0.6 * lo, 0.35 * lo):                     # then every way round, down to a step or two
                plans.append((yaw, length, False))
                plans += [(yaw + turn0 + k * math.pi / 6.0, length, False) for k in range(12)]
            for heading, length, roomy in plans:
                target = (x + math.sin(heading) * length, y - math.cos(heading) * length)
                if not rests(a, target, heading):
                    continue
                if roomy and not others(a, max(ends.values()), target, heading, disc=True):
                    continue
                if passes(a, t, x, y, yaw, heading, target, length, v, home):
                    go = target
                    break
            if go is None:                         # hemmed in: at least turn to face another way, if there is room
                for k in range(1, 12):
                    heading = yaw + ch._wrap(turn0 + k * math.pi / 6.0)
                    if passes(a, t, x, y, yaw, heading, (x, y), 0.0, v, home):
                        spin = heading
                        break
        if go is not None or spin is not None:
            if go is not None:
                end = a.walk(t, [(x, y, z), (go[0], go[1], z)], speed=speed, gait=gait)
                events[a.name].append(("walk", t, end, (round(go[0], 3), round(go[1], 3))))
            else:
                end = a.turn(t, spin, gait=gait)
                events[a.name].append(("turn", t, end, None))
            record(a, t, end)
            pause = int(r.integers(8, 40))
            if end + pause < f1 - 14 and pause >= 14:
                a.idle(end, end + pause, seed=int(r.integers(0, 1 << 30)), watch=watch)
            heapq.heappush(queue, (end + pause, i))
        else:
            if first:
                dur = int(r.integers(6, 50))
            elif keen:                             # it wanted to go and found no way: it tries again sooner
                dur = int(r.integers(12, 36))
            else:
                dur = int(r.integers(24, 80) / max(activity, 0.05))
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

    # ---- a blow that meets it in the air (LivingEntity.knockback: no second lift; half its speed + the push)
    q = knock_flight(0.4, (0.0, 1.0), height=0.58, velocity=(0.0, 0.05, -0.11))
    expect("knock_flight in the air: vertical speed unchanged (%.3f), horizontal %.3f = 0.05 / 2 + 0.4" % (q[0][5], q[0][4]),
           q[0][5] == -0.11 and abs(q[0][4] - 0.425) < 1e-12 and q[-1][2] == 0.0)
    hen.place(3000, (0.0, 100.0, 0.0), 0.0)
    up1 = hen.hurt(3010, attacker=(0.0, 98.0, 0.0))
    once = hen.pos_at(up1 + 40).y
    z_hit = hen.pos_at(3022).z
    up2 = hen.hurt(3022, attacker=(0.0, 98.0, 0.0))
    top = max(hen.pos_at(f).z for f in np.arange(3022.0, up2 + 1, 0.2))
    drops = all(hen.pos_at(f + 0.5).z <= hen.pos_at(f).z + 1e-9 for f in np.arange(3022.0, up2 + 1, 0.5))
    _evaluate(scene, 3028)
    red = not hen._twins["body"].hide_render
    expect("hen hit at 3010 and again at 3022 (the game's earliest second hit), %.2f up: not lifted again (top %.2f), "
           "sinks all the way, lands at frame %d (alone: %d), z %.3f there and %.3f 100 frames on; thrown %.2f in all "
           "(one blow: %.2f); red again; wings still beating" % (
               z_hit, top, up2, up1, hen.pos_at(up2).z, hen.pos_at(up2 + 100).z, hen.pos_at(up2 + 40).y - 100.0, once - 100.0),
           z_hit > 0.4 and top <= z_hit + 1e-9 and drops and abs(hen.pos_at(up2).z) < 1e-9
           and abs(hen.pos_at(up2 + 100).z) < 1e-9 and hen.pos_at(up2 + 40).y > once + 1.0 and red
           and hen._flap_run[1][0][1] == 1.0)
    hen.place(3100, (0.0, 100.0, 0.0), 0.0)
    hen.hurt(3110, attacker=(0.0, 98.0, 0.0))
    gone = hen.die(3122, camera=cam, attacker=(0.0, 98.0, 0.0), seed=1)
    _evaluate(scene, gone)
    puffs = [q_["object"].matrix_world.translation.z for q_ in hen.bursts[-1].particles if q_["first"] <= gone < q_["last"]]
    expect("hen hit at 3110 and killed in the air at 3122: the body comes down while it tips (z %.2f at 3122, %.3f at %d), "
           "the poof starts %.2f to %.2f above the ground" % (hen.pos_at(3122).z, hen.pos_at(gone - 1).z, gone - 1,
                                                              min(puffs), max(puffs)),
           hen.pos_at(3122).z > 0.4 and abs(hen.pos_at(gone - 1).z) < 1e-9 and min(puffs) > -0.5 and max(puffs) < 1.3)
    cow.place(3200, (5.0, 100.0, 0.0), 0.0)
    cow.hurt(3210, attacker=(5.0, 98.0, 0.0))
    e = cow.hurt(3216, attacker=(5.0, 98.0, 0.0))
    top = max(cow.pos_at(f).z for f in np.arange(3210.0, e + 1, 0.2))
    expect("cow hit at 3210 and again 6 frames later (faster than the game allows): peak %.3f, stands at z %.3f" % (
        top, cow.pos_at(e + 40).z), abs(top - 0.9648) < 0.01 and abs(cow.pos_at(e + 40).z) < 1e-9)
    e = cow.hurt(e, attacker=(5.0, 98.0, 0.0))
    top = max(cow.pos_at(f).z for f in np.arange(e - 12.0, e + 1, 0.2))
    expect("... and once more on the frame it stands again: lifted like a first blow (%.3f), still sliding, so thrown "
           "a little further" % top, abs(top - 0.9648) < 0.01 and abs(cow.pos_at(e + 40).z) < 1e-9)
    hen.place(3300, (0.0, 110.0, 3.0), 0.0)
    land = hen.fall(3300, (0.0, 108.5, 0.0))
    e = hen.hurt(3310, attacker=(0.0, 112.0, 0.0))
    expect("hen hit while it falls from a pillar (%.2f up at 3310; alone it would land at %d): lands at %d on the ground "
           "below (z %.3f)" % (hen.pos_at(3310).z, land, e, hen.pos_at(e + 30).z),
           hen.pos_at(3310).z > 1.0 and abs(hen.pos_at(e + 30).z) < 1e-9 and e > 3312)
    for at, want_z in ((3, 0.0), (8, 1.0)):
        cow.place(3400, (5.0, 110.0, 0.0), 0.0)
        cow.hop(3400, (5.0, 109.0, 1.0))
        e = cow.hurt(3400 + at, attacker=(5.0, 112.0, 0.0), knockback=0.2)
        expect("cow hit %d frames into a hop up a block: comes down at z = %.0f (%.3f)" % (at, want_z, cow.pos_at(e + 30).z),
               abs(cow.pos_at(e + 30).z - want_z) < 1e-9)

    # ---- out of a stride: a hop, a fall, a blow in the middle of a planted walk leave no stride pose behind
    for a_, what in ((cow, "hop"), (cow, "fall"), (cow, "hurt"), (hen, "hop"), (hen, "fall"), (hen, "hurt"), (calf, "hurt")):
        a_.place(3500, (0.0, 120.0, 1.0), math.radians(90))
        a_.walk(3500, [(0.0, 120.0, 1.0), (8.0, 120.0, 1.0)])
        rest_z = a_._rest(a_.hips, _LOC, 2)
        wide = max(np.arange(3515.0, 3540.0, 0.25), key=lambda f: abs(ch._val(a_.leg_l, _ROT, 0, f)))
        f_hit = int(round(wide))
        open_ = abs(ch._val(a_.leg_l, _ROT, 0, f_hit))
        here = a_.pos_at(f_hit)
        if what == "hop":
            e = a_.hop(f_hit, (here.x + 1.0, here.y, 1.0))
        elif what == "fall":
            e = a_.fall(f_hit, (here.x + 1.0, here.y, 0.0))
        else:
            e = a_.hurt(f_hit, attacker=(here.x - 2.0, here.y, 1.0))
        _evaluate(scene, e + 30)
        legs0 = max(max(abs(ob.rotation_euler.x), abs(ob.rotation_euler.y)) for ob in a_.legs.values())
        _evaluate(scene, f_hit + 4)
        soon = abs(a_.hips.location.z - rest_z)
        _evaluate(scene, e + 30)
        expect("%s %s on frame %d of a walk (legs %.0f deg open): 30 frames after it lands legs %.4f rad, body %.4f off "
               "its rest height (%.4f after 4 frames)" % (a_.name, what, f_hit, math.degrees(open_), legs0,
                                                          abs(a_.hips.location.z - rest_z), soon),
               legs0 < 1e-6 and abs(a_.hips.location.z - rest_z) < 1e-6 and soon < 1e-6)

    # ---- a herd after one leader: one call for all (a fan on both sides), or a call each (they walk round each other)
    for kind, n_, mk, joint in (("cow", 3, make_cow, True), ("cow", 3, make_cow, False), ("chicken", 4, make_chicken, True),
                                ("chicken", 4, make_chicken, False), ("cow", 6, make_cow, True)):
        steve.place(4000, (0.0, 200.0, 0.0), 0.0)
        steve.__dict__.pop("_followers", None)
        herd = [mk("f%s%d%d" % (kind[0], n_, i) + ("j" if joint else "s")) for i in range(n_)]
        for i, a_ in enumerate(herd):
            a_.place(4000, ((i - (n_ - 1) / 2.0) * (1.8 if kind == "cow" else 1.0), 204.0 + 0.4 * (i % 2), 0.0), 0.0)
        w_end = steve.walk(4010, [(0.0, 200.0, 0.0), (0.0, 191.0, 0.0)])
        if joint:
            end = follow(herd, steve, 4000, w_end + 20)
        else:
            end = max(follow(a_, steve, 4000, w_end + 20) for a_ in herd)
        gap = min(_gap(a_, a_.pos_at(f), a_.yaw_at(f), b_, b_.pos_at(f), b_.yaw_at(f))
                  for f in range(4000, end + 30) for i, a_ in enumerate(herd) for b_ in herd[i + 1:])
        away = [(a_.pos_at(end) - steve.pos_at(end)).length for a_ in herd]
        xs = sorted(a_.pos_at(end).x for a_ in herd)
        facing = max(abs(ch._wrap(a_.yaw_at(end) - math.atan2(steve.pos_at(end).x - a_.pos_at(end).x,
                                                              -(steve.pos_at(end).y - a_.pos_at(end).y)))) for a_ in herd)
        stray = max(_sole_stray(scene, a_) for a_ in (herd[0], herd[-1]))
        still = max((a_.pos_at(end + 20) - a_.pos_at(end)).length for a_ in herd)
        expect("%d %ss follow Steve 9 blocks, %s: bodies never closer than %.3f (promised %.2f); at rest (frame %d) "
               "%.2f-%.2f from him, x %s, facing him within %.0f deg; soles stray %.4f" % (
                   n_, kind, "one call" if joint else "a call each", gap, FOLLOW_ROOM, end, min(away), max(away),
                   [round(x_, 2) for x_ in xs], math.degrees(facing), stray),
               gap >= FOLLOW_ROOM - 2e-3 and 2.2 < min(away) and max(away) < 2.8 and facing < math.radians(25) and stray < 0.05
               and still < 1e-6 and (not joint or abs(xs[0] + xs[-1]) < 0.3))
    steve.__dict__.pop("_followers", None)
    steve.place(4500, (0.0, 200.0, 0.0), 0.0)
    w_end = steve.walk(4510, [(0.0, 200.0, 0.0), (0.0, 192.0, 0.0)])
    cow.place(4500, (0.3, 204.0, 0.0), 0.0)
    calf.place(4500, (0.0, 197.0, 0.0), math.radians(90))                # stands in her way and stays there
    end = follow(cow, steve, 4500, w_end + 20, avoid=[calf])
    gap = min(_gap(cow, cow.pos_at(f), cow.yaw_at(f), calf, calf.pos_at(f), calf.yaw_at(f)) for f in range(4500, end + 1))
    expect("follow(avoid=[a calf standing in her way]): she walks round it, never closer than %.3f, and ends %.2f from Steve"
           % (gap, (cow.pos_at(end) - steve.pos_at(end)).length),
           gap >= FOLLOW_ROOM - 2e-3 and 2.2 < (cow.pos_at(end) - steve.pos_at(end)).length < 2.8)

    # ---- hand items end, and go when the player goes; loot and eggs are used in their shot
    steve.place(5000, (0.0, 300.0, 0.0), 0.0)
    try:
        hand_item(steve, "wheat", 5000, None)
        refused = False
    except ValueError:
        refused = True
    wheat = hand_item(steve, "wheat", 5000, 5100)
    steve.show(5040, False)
    steve.show(5060, True)
    seeds_ = hand_item(steve, "wheat_seeds", 5080, 5100)
    vis = {}
    for f in (4999, 5000, 5039, 5040, 5059, 5060, 5079, 5080, 5099, 5100):
        _evaluate(scene, f)
        vis[f] = (not wheat.hide_render, not seeds_.hide_render)
    expect("hand_item: no frame_end is refused; wheat 5000-5079 but not while Steve is hidden (5040-5059), then the "
           "seeds take over until 5100 %s" % (vis,),
           refused and [vis[f] for f in sorted(vis)] == [(False, False), (True, False), (True, False), (False, False),
                                                         (False, False), (True, False), (True, False), (False, True),
                                                         (False, True), (False, False)])

    class _Stage:                                                        # what lay_egg / drop_loot need of a Stage
        def __init__(self):
            self.cast, self.used = {}, []

        def use(self, shot, *things):
            self.used += [(shot, t.name) for t in things]

    st_ = _Stage()
    hen.place(5200, (0.0, 310.0, 0.0), 0.0)
    loot = drop_loot(hen, 5210, stage=st_, shot="s")
    egg2 = lay_egg(hen, 5205, stage=st_, shot="s")
    expect("drop_loot / lay_egg(stage=st, shot=s): registered and used in the shot %s" % (st_.used,),
           sorted(st_.cast) == sorted(it.name for it in loot + [egg2]) and len(st_.used) == 3)

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
        more = wander(herd, 2740, 2980, area, seed=6, place=False)       # walks of the first call are still running
        gap, edge = pen_report(herd, 2500, 2980 + 60, area)
        walks = [sum(1 for e in events[a_.name] + more[a_.name] if e[0] == "walk") for a_ in herd]
        expect("... and 10 s more with place=False: gap %.2f, from the fence %.2f, walks per animal %s" % (gap, edge, walks),
               gap >= herd[0].width - 1e-3 and edge >= herd[0].width - 1e-3 and min(walks) >= 1)
    herd = [make_cow("ac%d" % i) for i in range(4)]
    area = pen_area(40, 0, 49, 9)
    steve.place(6000, (44.4, 2.0, 0.0), math.pi)
    s_end = steve.walk(6020, [(44.4, 2.0, 0.0), (44.4, 6.0, 0.0)])
    cow.place(6000, (42.5, 1.9, 0.0), math.pi)
    follow(cow, steve, 6000, s_end + 10)
    events = wander(herd, 6000, 6240, area, seed=2, avoid=[steve, cow])
    near = min(_apart(a_.body_points(a_.pos_at(f), a_.yaw_at(f)), _circles(o, f))[0]
               for f in range(6000, 6300) for a_ in herd for o in (steve, cow))
    expect("wander(avoid=[Steve walking through the pen, the cow that follows him]): the herd keeps %.2f from both "
           "(promised %.2f), %d walks" % (near, herd[0].width, sum(1 for ev in events.values() for e in ev if e[0] == "walk")),
           near >= herd[0].width - 1e-3)
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
        quick.camera(scene, (-0.6, -7.6, 1.5), (-0.75, 0.0, 1.05), lens=25)
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
        cam = quick.camera(scene, (-0.4, -8.4, 1.7), (-0.35, 0.0, 1.0), lens=27)
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

    if want("hurt2"):
        # the ordinary way a hen is hit in the game: the second blow lands 12 frames after the first, while she still
        # floats down (20 frames in the air); she is not lifted again. Second sheet: that blow kills her in the air.
        for tag, kill in (("hurt2", False), ("die2", True)):
            scene = stage(res=(640, 360), blur=True, sun=-140.0)
            steve, hen = ch.make_player("steve"), make_chicken("hen")
            steve.place(1, (1.5, -0.1, 0.0), math.radians(-90))
            hen.place(1, (0.0, 0.0, 0.0), math.radians(-70))
            steve.look_at(1, hen, ease=0)
            cam = quick.camera(scene, (-2.2, -9.4, 1.6), (-2.0, 0.0, 0.85), lens=35)
            steve.swing_arm(8)
            up1 = hen.hurt(10, attacker=steve)
            steve.walk(11, [(1.5, -0.1, 0.0), (0.1, -0.1, 0.0)], speed=4.3)
            steve.track(11, 60, hen)
            steve.swing_arm(20)
            if kill:
                end = hen.die(22, camera=cam, attacker=steve, seed=3)
                frames = (21, 23, 28, 34, 44, end + 3)
            else:
                end = hen.hurt(22, attacker=steve)
                frames = (9, 13, 21, 23, 27, end + 1)
            print(tag, "first blow 10 (alone she would stand at %d), second blow 22, %s %d" % (
                up1, "gone at" if kill else "stands at", end))
            stills = []
            for i, f in enumerate(frames):
                scene.frame_set(f)
                stills.append(quick.render(scene, "animals_%s_%d" % (tag, i + 1)))
                print("   frame", f, "hen at", tuple(round(c, 2) for c in hen.root.location), "red",
                      not hen._twins["body"].hide_render, "tipped %.0f deg" % math.degrees(hen.root.rotation_euler.y),
                      "wings %.0f deg" % math.degrees(hen.wing_r.rotation_euler.y))
            _tile("animals_%s_sheet" % tag, stills, cols=3)

    if want("hop"):
        # out of a planted stride: a cow walks up to a step and hops onto it without stopping; the legs fade into the
        # game's wave, the body comes back up, and it walks on
        scene = stage(res=(640, 360), blur=True, sun=-150.0, wall=((1, -2, 8, 2), ("grass_block",)))
        cow = make_cow("cow")
        cow.place(1, (-5.0, 0.0, 0.0), math.radians(90))
        cow.walk(1, [(-5.0, 0.0, 0.0), (2.0, 0.0, 0.0)])
        f_hop = next(f for f in range(1, 200) if cow.pos_at(f).x >= -0.45)
        here = cow.pos_at(f_hop)
        land = cow.hop(f_hop, (here.x + 1.9, 0.0, 1.0))
        end = cow.walk(land, [tuple(cow.pos_at(land)), (6.0, 0.0, 1.0)])
        print("cow hops on frame", f_hop, "from x %.2f" % here.x, "lands at", land, "walks on until", end)
        stills = []
        for i, f in enumerate((f_hop - 2, f_hop + 3, f_hop + 7, land, land + 4, land + 14)):
            scene.frame_set(f)
            at = cow.pos_at(f)
            quick.camera(scene, (0.4, -8.2, 1.5), (0.4, 0.0, 1.0), lens=35)
            stills.append(quick.render(scene, "animals_hop_%d" % (i + 1)))
            print("   frame", f, "cow at", tuple(round(c, 2) for c in at), "legs",
                  [round(math.degrees(ob.rotation_euler.x)) for ob in cow.legs.values()],
                  "hips %.3f" % (cow.hips.location.z - cow._rest(cow.hips, _LOC, 2)))
        _tile("animals_hop_sheet", stills, cols=3)

    if want("herd"):
        # "a player may hold wheat or seeds and they follow": three cows after Steve in ONE follow() call (a fan on
        # both sides), and four hens after seeds with a call each (each walks round those keyed before it)
        for tag, kind, joint in (("cows", "cow", True), ("hens", "chicken", False)):
            scene = stage(res=(960, 540), sun=-140.0, blur=True)
            steve = ch.make_player("steve")
            steve.place(1, (0.0, 3.0, 0.0), 0.0)
            food = hand_item(steve, "wheat" if kind == "cow" else "wheat_seeds", 1, 400)
            n = 3 if kind == "cow" else 4
            herd = [(make_cow if kind == "cow" else make_chicken)("%s%d" % (kind, i)) for i in range(n)]
            for i, a in enumerate(herd):
                a.place(1, ((i - (n - 1) / 2.0) * (1.8 if kind == "cow" else 1.0), 7.0 + 0.4 * (i % 2), 0.0), 0.0)
            steve.raise_arm(1, 30, ease=0)
            w_end = steve.walk(10, [(0.0, 3.0, 0.0), (0.0, -4.0, 0.0)])
            if joint:
                end = follow(herd, steve, 1, w_end + 20, look=food)
            else:
                end = max(follow(a, steve, 1, w_end + 20, look=food) for a in herd)
            steve.face(w_end + 2, herd[n // 2])
            gap = min(_gap(a, a.pos_at(f), a.yaw_at(f), b, b.pos_at(f), b.yaw_at(f))
                      for f in range(1, end + 1) for i, a in enumerate(herd) for b in herd[i + 1:])
            print("herd of %d %ss (%s): Steve stops at frame %d, they rest at %d; bodies never closer than %.2f; they end at %s"
                  % (n, kind, "one call" if joint else "a call each", w_end, end, gap,
                     [tuple(round(c, 2) for c in a.pos_at(end).xy) for a in herd]))
            for i, f in enumerate((w_end - 30, end + 12)):
                scene.frame_set(f)
                mid = steve.pos_at(f)
                if kind == "cow":
                    quick.camera(scene, (mid.x + 6.2, mid.y - 4.6, 4.6), (mid.x, mid.y + 1.6, 0.6), lens=30)
                else:                                                    # from above: the fan and the room between them
                    quick.camera(scene, (mid.x - 2.6, mid.y - 5.4, 5.6), (mid.x + 0.9, mid.y + 1.1, 0.3), lens=38)
                print("wrote", quick.render(scene, "animals_herd_%s_%d" % (tag, i + 1)))

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

    def edit(b):
        """The pens, built into the village (engine/village.py: FILM SETS)."""
        for kind in kinds:
            pen_set(b, *PENS[kind]["cells"], gates=[PENS[kind]["gate"]], name="pen_" + kind)

    v = village.build_village(scene, seed=1, edit=edit)
    look.set_time(scene, "day", sun_azimuth=205.0, sun_elevation=46.0)
    look.setup_compositor(scene, bloom=1.0, grade="warm")
    v.set_lantern_energy(0.0)
    herds = {}
    for kind in kinds:
        cfg = PENS[kind]
        pen = v.sets["pen_" + kind]
        if kind == "cow":
            herd = [make_cow("cow%d" % i) for i in range(5)] + [make_cow("calf", baby=True)]
        else:
            herd = [make_chicken("hen%d" % i) for i in range(6)] + [make_chicken("chick%d" % i, baby=True) for i in range(2)]
        events = wander(herd, 1, frames[-1] + 30, pen["area"], seed=cfg["seed"], z=pen["z"])
        gap, edge = pen_report(herd, 1, frames[-1] + 30, pen["area"])
        print("%s pen %s, inside %s: %d animals, %d walks in %d frames; smallest gap between bodies %.2f, from the fence %.2f"
              % (kind, cfg["cells"], tuple(round(c, 2) for c in pen["area"]), len(herd),
                 sum(1 for ev in events.values() for e in ev if e[0] == "walk"), frames[-1] + 30, gap, edge))
        for name, ev in events.items():
            print("   %-7s %s" % (name, " ".join("%s %d-%d" % (e[0], e[1], e[2]) for e in ev)))
        ring = [c for c in pen["cells"] + pen["inside"] if v.world.block_id(c[0], c[1], int(pen["z"])) in
                ("short_grass", "tall_grass", "poppy", "dandelion", "oxeye_daisy", "cornflower")]
        print("   plants left on the ring or inside: %d" % len(ring))
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
