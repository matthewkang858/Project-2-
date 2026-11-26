"""CREEPER, SKELETON, BOW AND ARROWS for "The Crammys" (stories/crammys.json, beats 9-24). New module; edits no
other file.

Everything is transcribed from the Java Edition 26.x client classes (named next to each number) and drawn with the
game's own textures through engine.mcassets / engine.characters. Blender axes as everywhere: +X east, +Y north, +Z
up, 1 block = 1 unit, characters face -Y at yaw 0, 24 fps (the game runs 20 ticks per second: 1 tick = 1.2 frames).
"camera" = the Shot that films it (or a Film, or a camera object): particles face it, exactly as in engine.fx.

PUBLIC API
  make_creeper(name, collection=None) -> Creeper            CreeperModel at full size: 1.625 to the top of the head
  make_skeleton(name, left_handed=False, collection=None) -> Skeleton     SkeletonModel, 2.0 tall, bow in hand
  add_creeper(st, name="creeper") / add_skeleton(st, name="skeleton", **kw)   the same, registered with a
      films.lookdev.Stage (st.cast[name]); then st.use(shot, c), st.hero(shot, "creeper", c). Hidden outside their
      shots by Stage.finish() like every cast member; everything hanging on them follows.

  Creeper (an engine.characters.Character: root / swell / hips / body / head / leg_r / leg_l / leg_fr / leg_fl)
      place(frame, pos, yaw=0.0, keep_pose=False)
                                            a cut: upright, legs together, NOT swollen (keep_pose=True keeps a fuse
                                            that runs across the cut)
      walk(frame, points, speed=None, from_current=False, swing=None) -> end frame
                                            the game's four-legged wave: diagonal pairs swing together,
                                            1.4 s cos(0.6662 p), s = min(4 x blocks per tick, 1). speed None =
                                            CREEPER_SPEED 2.75 blocks/s (chasing: legs +-44 degrees, a cycle every
                                            2.36 blocks / 20.6 frames); CREEPER_STROLL 1.76 (+-28). The feet slide, as
                                            in the game. swing = the leg amplitude in DEGREES instead of the game's
                                            (a film choice). .last_walk = the numbers
      step(frame, toward, blocks=0.5, frames=14, swing=44.2) -> end frame
                                            ONE SLOW STEP (beat 10): the body glides half a block toward `toward` (a
                                            point or a Character) in 14 frames while one diagonal pair swings out to
                                            +-44 degrees and back (sin over the step), the other pair the other way;
                                            at 44 degrees the feet travel about the half block the body does. A film
                                            move: the game's leg wave at 0.8 blocks/s is only +-13 degrees
      look_at / track / face / turn / idle  as every Character; head clamped to the mob's 75 / 40 degrees
      fuse(frame_start, frame_end=None) -> frame
                                            THE SWELL from frame_start (the first swell tick): 1.4 x wider and 1.1 x
                                            taller at full swell, wobbling, with FIVE white flashes of 3-4 frames
                                            (frames +4..6, +11..13, +17..20, +24..26, +31..33: 35 %, 35 %, 35-40 %,
                                            50-55 %, 65-70 % white). frame_end=None: the whole fuse; returns the frame
                                            it EXPLODES on (frame_start + 35 = 29 ticks): call explode(that frame) for
                                            the game's ending; nothing explodes by itself. frame_end=f: aborted on f
                                            (the target got 7 blocks away): shrinks back at the same rate; returns the
                                            frame it is back to normal. Several calls chain.
      explode(frame, camera=None, village=None, victims=(), blocks=None, griefing=True, seed=0, glow=None,
              smoke_glow=None, latency=False) -> centre (Vector: its feet)
                                            gone ON `frame`, the explosion's particles from that same frame (see
                                            explosion(); latency=True keeps the game's empty tick before them), and
                                            every Character in `victims` within 6 blocks is pushed away from the centre
                                            with the game's (1 - d / 6) blocks per tick (Player.hurt / undead.hurt
                                            with attacker=centre). .last_explosion = dict(frame, centre, burst,
                                            blocks, pushed)
      hurt(frame, attacker=None, knockback=None, max_back=None) -> end frame
                                            undead.hurt: red 12 frames (the red hides the white flash, as in the
                                            game), legs kick, hop only with an attacker. The fuse goes on
      die(frame, camera=None, attacker=None, knockback=None, glow=0.25, village=None, ...) -> gone frame
                                            undead.die: red, tips onto its left side still swollen (the swell freezes),
                                            gone with 20 poof puffs on frame + 24
      swelling_at(frame) (0 .. 1.036), white_at(frame) (the white mixed in, 0 .. 0.70), size (0.6, 1.7)

  Skeleton (an engine.undead.Undead: place, walk (planted / vanilla gait, lead / stride from its name), idle,
            look_at, track, face, hurt, die ... as a zombie, with the humanoid arms and its bow)
      walk(frame, points, ...) -> end       2.75 blocks/s; the arms swing against the legs (HumanoidModel:
                                            arm = -leg / 1.4) while it is not aiming; aiming, they stay on target
      aim(frame, target=None, ease=3)       RAISE: both arms up in the BOW_AND_ARROW pose (-90 degrees + head
                                            pitch, the bow arm 0.1 rad in, the other 0.5), head on the target. The
                                            game snaps (ease=0); 3 frames is a film choice
      draw(frame_start, release=None, target=None, ease=3) -> dict(frame, origin, direction, target)
                                            DRAW / HOLD / RELEASE: turns to the target (30 degrees a tick), raises the
                                            bow if it is not up, the bow item shows bow_pulling_0, _1 from 13 ticks
                                            (frame_start + 16), _2 from 18 ticks (+22), and the plain bow again ON
                                            `release` (default: the game's 20 ticks = frame_start + 24; any later
                                            release holds the full draw). dict: where and which way the arrow leaves.
                                            A DRAWN BOW ALWAYS HAS ITS ARMS UP (the game draws BOW_AND_ARROW the whole
                                            time a skeleton has a target): a place() cut or a lower() inside a draw
                                            (or a cut ON its release frame) turns into a snap up, and a draw that
                                            starts on a cut snaps up with the cut, whatever order they are keyed in.
                                            A draw running across a cut goes on (its arrow is already keyed). The
                                            arms stay up after the release until lower()
      shoot(frame_start, target, release=None, part=None, **fire_kw) -> Flight   draw() + fire(): the whole shot
                                            (part=None: a free spot facing the skeleton, see fire())
      lower(frame, ease=3)                  LOWER: arms back down (the game: the target is lost)
      bow_at(frame) -> 'bow' | 'bow_pulling_0' | '_1' | '_2';  aiming_at(frame) -> 0..1;  .bows (the four item
      objects, never key them);  left_handed=True: bow in the LEFT hand (1 skeleton in 20 in the game), mirrored.
      Its arms are rewritten from legs, head and aim after every call of this class (look_at / track / idle /
      face / walk / hurt / die / aim / draw / lower / place).

  fire(start, target, frame, speed=None, part=None, camera=None, hurt=True, knockback=None, until=None, aim=None,
       spread=0.0, seed=0, scale=1.0, stick=None, kill=False, at=None, game_id=None, max_back=None, align=False,
       lead=True, village=None, collection=None) -> Flight
      An arrow loosed ON `frame` flying the game's path tick by tick (AbstractArrow.tick: rotation turned 20 % of
      the way to the motion (it never tumbles), move, speed x 0.99, 0.05 down). start = a Skeleton (from its eyes
      - 0.1 at 1.6 blocks/tick = 32 blocks/s), any Character (eyes - 0.1; a player's full draw 3.0) or a point.
      target = a Character: aimed as AbstractSkeleton.performRangedAttack aims (at 1/3 of its height + 0.2 x the
      distance up, at where it is on `frame`); the arrow flies until it enters the hit box grown by 0.3 and is
      gone on that frame (the Flight's int). A MOVING target the game's aim would miss: lead=True (default) aims
      at where it will be when the arrow arrives (a few rounds of flight time -> position) and prints a note;
      lead=False, or a target that cannot be reached: the arrow MISSES as the game's would, flies on and sticks in
      the ground past it (village= for the terrain, else the plane of the target's feet), Flight.missed = True,
      nobody is hurt. Never raises for a Character target. Then, by the game's rule, a PLAYER keeps it stuck in
      `part` (see hit(); part=None = the film's pick: the free AUTO_SPOT whose shaft faces the shooter best, so
      two shots never share a spot; stick=True keeps it in anybody, stick=False in nobody) and the target is hurt
      along the arrow (knockback in blocks/tick: the game 0.4 = a mob hops about 2 blocks; 0.1 = "rocks back half
      a step", 0.3 blocks; max_back = at most this far, mobs only; hurt=False: no flash); kill=True: that arrow
      kills it (die(), poof with camera=). aim="exact" aims at the chest exactly. align=True: the stuck shaft
      points back along the flight (see hit()). target = a point (the ground, a fence post's face): a path exactly
      through it (ValueError if the speed cannot reach it); the arrow STAYS there (0.05 short, tail shaking 7
      ticks) until `until` (None: the end of the film). spread=1 adds the game's random spread (Normal: 6 x
      0.0172) seeded by `seed`. scale = a fatter arrow (1.25 for wides; a film choice).
      Flight: an int (the impact frame) with .arrow (the flying / block-stuck object), .stuck (the arrow in the
      body or the block, or None), .hit (Vector), .frames (loosed, impact), .points (per tick), .velocity
      (blocks/tick at the impact), .direction, .ticks (flight time), .target, .missed, .spot (the SPOTS name it
      stuck in, or None), .point_at(frame).
  hit(character, frame, part="chest", at=None, until=None, scale=1.0, hurt=True, knockback=None, direction=None,
      attacker=None, game_id=None, index=None, max_back=None, align=False) -> Object
      An arrow STUCK in a character from `frame` on, riding its body part through every later walk, sprint,
      crouch, pose, hurt and death (gone with the body). part = a spot (SPOTS, table below), or a part (head,
      body, arm_r, arm_l, leg_r, leg_l) with at=(fx, fy, fz) = where inside its cube (0..1 each; fz 0 = front,
      1 = back), or part=None for the game's own pseudo-random spot of the index-th arrow of entity `game_id`
      (default: one from the name). Players (engine.players), villagers (the crossed arms take the shoulders)
      and undead all work; the game draws stuck arrows on players only. until=None = to the end of the film (the
      film's choice): the game removes them one by one (stuck_arrow_lifetime(2) = frames 672 and 1368 after the
      first hit). hurt / knockback / max_back / direction / attacker as fire(): Player.hurt for players,
      undead.hurt for everyone else. Prints a note when the arrow lands within half a pixel of another one (it
      would read as ONE arrow) and when its spot faces away from `direction` (an arrow from behind sticking out
      of his chest). align=True (needs direction): same entry point, but the shaft points back along the flight
      (a film option; the game ignores where an arrow came from).
      SPOTS: where the shaft sticks OUT, in his own terms (StuckInBodyLayer points the tip at -(2 f - 1), so the
      direction belongs to the spot, never to the flight; spot_direction(name) gives (right, up, forward)):
          chest       body   out of the front, up and to HIS RIGHT     (right +0.37, up +0.45, forward +0.82)
          chest_l     body   out of the front, up and to his left      (-0.41, +0.41, +0.82)
          belly       body   out of the front, a little DOWN           (-0.11, -0.44, +0.89)
          back        body   out of the back, up and to his left       (-0.26, +0.43, -0.86)
          back_low    body   out of the back, down and to his right    (+0.26, -0.43, -0.86)
          shoulder_r  arm_r  top of the right shoulder: mostly UP, then forward   (+0.10, +0.74, +0.66)
          shoulder_l  arm_l  top of the left shoulder: mostly UP, then forward    (-0.10, +0.74, +0.66)
          head        head   out of the face, to his left              (-0.45, +0.23, +0.86)
          thigh_r / thigh_l  out of the front of the thigh, up         (0.00, +0.58, +0.81)
      RULE: choose a spot on the shooter's side (front spots when he faces the shooter, back / back_low from
      behind; the right shoulder when the shooter is on his right), or let fire(part=None) choose.
  stick(point, direction, frame, until=None, shake=True, scale=1.0, collection=None) -> Object
      An arrow stuck in a block from `frame` on: 0.05 short of `point` along `direction` (the way it flew), the
      tail shaking for 7 ticks (ArrowModel: root zRot -sin(3 shake) shake degrees).
  explosion(centre, frame, camera=None, radius=3.0, village=None, blocks=None, griefing=True, seed=0, glow=None,
            smoke_glow=None, latency=False) -> fx.Burst (.blocks, .block_particles)
      The client's explosion: from `frame` (latency=True: 1 tick after it, as the client, whose emitter spawns on
      its next particle tick: two film frames without creeper and blast) the emitter spawns 6 'explosion' puffs a tick for 8 ticks
      (48, 2.25-4 blocks wide, grey 0.4-1.0, full bright (glow 1.0), 6-9 ticks each) within +-4 blocks, and on the
      same tick min(blocks, 512) 'poof' / 'smoke' particles fly out of the blast sphere (only from air). blocks=None
      = explosion_blocks(): every position the game's rays reach, AIR INCLUDED (open flat meadow: 331-343 ->
      about 160 particles above ground). griefing=False (mobGriefing off): one 2-block 'explosion' puff instead of
      the 48. glow / smoke_glow: self-light of the puffs / of poof and smoke (default 1.0 / 0.25 at night).
  explosion_blocks(centre, radius=3.0, village=None, seed=0) -> int; blast_push(centre, character, frame) -> dict
  refresh(character)                        recompute what hangs on a character (stuck arrows, the bow models, the
                                            white shells) from its show() timeline, undead's vanish / death and red
                                            flashes. Automatic on show / place and in this module's calls; Stage.
                                            finish() calls show() last, so a film never needs it.
  arrow_object(name, scale=1.0), arrow_track(start, velocity, ticks), game_arrow_spot(entity_id, index),
  stuck_matrix(character, part, f, scale, tip=None), stuck_arrow_lifetime(count), spot_direction(spot),
  swell_scale(s), white_level(s), JavaRandom(seed): the numbers behind the above.
  Constants: CREEPER_SIZE, CREEPER_SPEED, CREEPER_STROLL, FUSE_TICKS, FUSE_RANGE (3), FUSE_ABORT_RANGE (7),
  EXPLOSION_RADIUS, SKELETON_SIZE, SKELETON_EYE, SKELETON_SPEED, BOW_DRAW_TICKS, BOW_PULL_TICKS,
  ATTACK_INTERVAL_TICKS, ARROW_SPEED, ARROW_GRAVITY, ARROW_DRAG, SPOTS, AUTO_SPOTS, FACTS.

THE CRAMMYS, beat by beat (st = films.lookdev.Stage, s = the shot, f0 / f1 its first / last frame; key each
character in frame order and PLACE FIRST in every shot; tools/check_hostiles_crammys.py is this recipe built and
rendered: out/test/hostiles_beat15_recipe*.png, hostiles_beat13_recipe.png, hostiles_step_recipe.png)
    cr = hostiles.add_creeper(st, "creeper"); sk = hostiles.add_skeleton(st, "skeleton")
    steve = players.add_player(st, "steve", "steve")
    10  cr.place(f0, spot, yaw); cr.look_at(f0, steve, ease=0)
        cr.step(f0 + 30, steve)                                 # ONE slow step: half a block, legs out to 44 deg
    11  sk.place(f0, under_oak, yaw); sk.look_at(f0 + 4, lens_point, ease=8); sk.aim(f0 + 16)   # skull, raise
    12  sk.place(f0, ...); sk.aim(f0, steve, ease=0); sk.draw(f0, release=f1 + 1, target=steve)   # drawn and held
    13  sk.place(f0, ...); sk.aim(f0, steve, ease=0)
        fl = sk.shoot(f0, steve, part="chest", knockback=0.1)    # 24-frame draw, loosed on f0 + 24, sticks ~3 later;
                                                                 # he rocks back 0.3 blocks
    14  sk.shoot(fl.frames[0] + 1, steve, part="shoulder_r", knockback=0.1)   # drawn again at once: 24 frames later
        # (the game, Normal: 72 frames between arrows). shoulder_r = the shoulder on the skeleton's side when it
        # stands on his right, as beat 12 stages it (shoulder_l if it stands on his left; part=None picks for you)
    15  cr.place(f0, ...); steve.place(f0, ...); sk.place(f0, ...); sk.aim(f0, cr, ease=0)
        cr.face(f0 + 1, steve, ease=6); cr.look_at(f0 + 1, steve, ease=4)   # it turns after him ...
        end = cr.fuse(f0)                                       # ... and swells; it would explode on end = f0 + 35
        a = sk.shoot(f0 - 24, cr, knockback=0.1)                # arrow 1 loosed ON f0, lands about f0 + 3: red
        k = sk.shoot(a.frames[0] + 1, cr, release=a.frames[0] + 20, kill=True, knockback=0.1, camera=s)
                                                                # arrow 2 lands 20 frames after arrow 1, about f0 + 23,
        sk.lower(int(k) + 12)                                   # before `end` (tips over swollen, poof on k + 24)
        knockback=0.1 is NOT optional here: the game's 0.4 throws the creeper about 2 blocks (hopping 1 block up)
        along the arrow, straight into and through Steve standing on the far side (characters do not collide).
        With 0.1 it rocks back 0.3 blocks per arrow (or use max_back=). Two arrows in one fuse need both draws back
        to back (the game's skeleton, 72 frames between arrows, could not do it in a 35-frame fuse); release= gives
        the story's 20 frames between the hits (a 16-frame second draw: pulling_0, then _1 from +16).
    16+ nothing to do: the two arrows stay in Steve through every later shot, walk, sprint and pose.
    A cut that jumps in time: fx.stop_particles(first frame) (the poof and the explosion are fx.Bursts).

WHAT THE GAME DOES (read from the classes)
  creeper   CreeperModel.createBodyLayer: head 8x8x8 and body 8x12x4 on a pivot 18 px up, four 4x6x4 legs at
            (+-2, 18, +-4), creeper.png 64x32; setupAnim: right hind and left front = cos(p 0.6662 + pi) 1.4 s,
            the other pair cos(p 0.6662) 1.4 s. Creeper: speed attribute 0.25 (MeleeAttackGoal 1.0, stroll 0.8);
            SwellGoal: swells when its target is within 3 blocks, stops beyond 7 (swellDir -1: 1 a tick back);
            maxSwell 30: swell + 1 a tick, explodes on reaching 30, radius 3 at its FEET (x 2 when powered).
            CreeperRenderer.scale: s = swell / 28 (lerped per partial tick), w = 1 + sin(100 s) s 0.01,
            q = clamp(s)^4: xz x (1 + 0.4 q) w, y x (1 + 0.1 q) / w, about the feet; getWhiteOverlayProgress = 0
            when (int)(10 s) is even, else clamp(s, 0.5, 1); OverlayTexture: white mixed in at u / 15 x 0.75,
            u = (int)(15 progress); a red overlay (hurt, dying) uses the red rows: no white then. Creeper.tick
            swells only while alive: a dying creeper keeps its size.
  explosion ServerLevel.explode -> ServerExplosion: rays from the 16^3 grid surface, strength 3 x (0.7..1.3),
            0.3 steps, -0.225 a step and -(resistance + 0.3) x 0.3 in a block; every position a ray reaches
            counts, air too (blockCount). ClientboundExplodePacket -> EXPLOSION_EMITTER (radius >= 2 and block
            damage) or EXPLOSION, and Level.DEFAULT_EXPLOSION_BLOCK_PARTICLES (poof x 0.5 / smoke x 1.0, speed 1,
            equal weights) through ClientExplosionTracker (512 a tick at most). hurtEntities: within 2 r, pushed
            (1 - d / 2r) x exposure along centre -> eyes.
  skeleton  SkeletonModel.createBodyLayer: the humanoid head and body, 2x12x2 arms (pivots +-5) and legs (+-2),
            skeleton.png 64x32; translateToHand: the hand 1 px nearer the body. EntityTypes: 0.6 x 1.99, eyes 1.74;
            speed 0.25. AbstractSkeletonRenderer.getArmPose: BOW_AND_ARROW on the main arm while aggressive with a
            bow (the WHOLE time it has a target, not only while drawing); HumanoidModel.poseRightArm: right yRot
            = -0.1 + head yRot, left yRot = 0.1 + head yRot + 0.4, both xRot = -pi/2 + head xRot; bobModelPart on
            top. RangedBowAttackGoal: startUsingItem, release at 20 ticks (BowItem.getPowerForTime(20) = 1),
            then attackIntervalMin (Normal 40, Hard 20): one arrow every 60 ticks (72 frames) on Normal, 40 (48)
            on Hard, within 15 blocks. items/bow.json: using_item -> use_duration x 0.05: < 0.65 bow_pulling_0,
            >= 0.65 _1, >= 0.9 _2; not using: item/bow.
  arrow     ArrowModel: two crossed 16x4 quads (texture rows x 0.8) at 45 / 135 degrees about the shaft and a 5x5
            nock square at -11, all x 0.9: 0.9 block long, the point 0.225 ahead of the entity position;
            entity/projectiles/arrow.png, culled (each side of a quad shows its own half of the texture).
            performRangedAttack: shoot(dx, dy + 0.2 dist, dz, 1.6, 14 - 4 difficulty) from eyes - 0.1;
            AbstractArrow.tick as above; onHitBlock: 0.05 back, shakeTime 7; a LivingEntity hit: +1 arrow count
            and the arrow entity is gone. ArrowLayer (AvatarRenderer only: no mob shows stuck arrows) =
            StuckInBodyLayer IN_CUBE: a generator seeded with the entity id picks, per arrow, one of head, body,
            left arm, right arm, left leg, right leg, a point f inside its cube, and points the arrow's TIP along
            -(2 f - 1): into the body, shaft and feathers out; no hurt tint. LivingEntity.tick: one arrow goes
            after 20 x (30 - count) ticks (two arrows: 28 s, then 29 s more).

WHERE IT DIFFERS FROM THE GAME (on purpose or not modelled)
  - The flying arrow is drawn where the game's arrow IS at each tick and reaches the body; the game draws an
    entity one tick late and removes a hitting arrow on the tick it hits, up to 1.6 blocks short of the body.
  - Arrow hits are the director's: hit() puts the arrow where `part` says (fire(part=None): a free spot facing
    the shooter); the game picks a random spot, unrelated to where it hit (game_id= reproduces the game's pick
    exactly). align=True turns the shaft back along the flight, which the game never does.
  - fire() LEADS a moving target (lead=True); the game's skeleton aims at where the target is now, and its
    arrow misses anything crossing the line of fire fast enough (lead=False shows that miss).
  - aim() eases 3 frames, the game snaps; draw(release=) may hold longer or loose sooner than the skeleton's
    20 ticks.
  - explode() starts the particles ON the explosion frame; the client spawns them on its next particle tick
    (latency=True: two film frames show neither the creeper nor the blast).
  - Creeper.step() is a film move (one diagonal-pair swing of 44 degrees over half a block); the game would
    show a +-13 degree shuffle with sliding feet at that speed.
  - A creeper killed while swelling keeps a steady size (the game alternates between two adjacent swell values
    every tick: a 1.4 % jitter); the poof fills (0.6, 1.625), the drawn height, not the 1.7 hit box.
  - explode(): the exposure of victims is 1 (no blocks in the way); the push goes through undead.hurt /
    Player.hurt with attacker=centre (horizontal hop 0.36 up) instead of the game's push along centre -> eyes.
    No crater: the terrain stays (the block particles still come only from air).
  - Not built: charged creepers, strays / bogged / wither skeletons, skeleton strafing and melee, tipped arrows,
    the arrow's pick-up, item drops (bones, arrows, gunpowder, music discs: engine.mobs.make_dropped_item).

GOTCHAS
  - Never key hide_render on anything this module hangs on a character (stuck arrows, the bow models, the
    creeper's white shells): it follows the character's show(), death and red flash.
  - The white flash is a set of shells 0.01 px outside the creeper (no animated material: stamp-safe); the swell
    is the scale of the `swell` empty, keyed every quarter frame (the wobble lasts about 2 frames).
  - Arrows are thin: the shaft is 0.045 block wide. At phone size they read from 3-4 blocks; scale=1.25 for wides.
  - Particles are world objects (fx.Burst): a cut that jumps in time needs fx.stop_particles(first frame).
  - KNOCK-BACK IGNORES EVERYBODY ELSE: hurt / die / an arrow's knock-back move a character through other
    characters (they do not collide here; in the game they would shove each other). The game's arrow
    knock-back (0.4) hops a mob about 2 blocks along the arrow and 1 block up: a mob shot toward someone
    standing behind it lands in or beyond them. Pass knockback=0.1 (0.3 blocks) or max_back=, and stage the
    camera on the side the knock-back does not go.
  - Order of calls: place() first in every shot, then aim / draw / shoot (a place() keyed AFTER a draw resets
    the head to straight ahead from the cut; the arms stay up while the bow is drawn either way).
  - A stuck arrow's shaft direction belongs to its spot (table under hit()), not to the flight: an arrow from
    behind with part="chest" sticks out of his chest (hit() prints a note). Use a spot on the shooter's side,
    part=None, or align=True.

PROOFS AND CHECKS
  $BPY -m engine.hostiles                    59 numeric checks (a few seconds; exit 1 if one fails)
  $BPY -m engine.hostiles <proof> [...]      out/test/hostiles_<proof>*.png, 20-60 s each on a quiet machine:
      lineup_front lineup_side lineup_back (day, next to Steve), walk, fuse, explode, draw, flight, stuck, stuck_b,
      ground, death, moving (night, the real village, look and Stage; sheets are 270x480 or 360x640 per frame)
  $BPY -m tools.check_hostiles_stamp         render.py fingerprints follow the swell, white flash, bow models,
                                             stuck arrows and the explosion; run twice: the digests must match
  $BPY -m tools.check_hostiles_crammys info | still F.. | sheet NAME F.. | fp
                                             the beat recipe above as a two-sky Stage film through render.py
"""
import math
import os
import sys

import bpy
import numpy as np
from mathutils import Matrix, Vector

from . import characters as ch
from . import fx
from . import mcassets as mc
from . import mobs
from . import undead

FPS = ch.FPS
TICK = FPS / 20.0                    # frames per game tick
_LOC, _ROT = "location", "rotation_euler"

# ----------------------------------------------------------------------------------------------------
# numbers from the game (class or file named on each)
# ----------------------------------------------------------------------------------------------------
# ---- EntityTypes.CREEPER sized(0.6F, 1.7F); Creeper.createAttributes MOVEMENT_SPEED 0.25; registerGoals:
#      MeleeAttackGoal(1.0), WaterAvoidingRandomStrollGoal(0.8), SwellGoal
CREEPER_SIZE = (0.6, 1.7)
CREEPER_SPEED = mobs.mob_speed(1.0, 0.25)          # 2.753 blocks / s (chasing)
CREEPER_STROLL = mobs.mob_speed(0.8, 0.25)         # 1.762 blocks / s
FUSE_TICKS = 30                      # Creeper.DEFAULT_MAX_SWELL
SWELL_DIV = FUSE_TICKS - 2           # Creeper.getSwelling: lerp(oldSwell, swell) / (maxSwell - 2)
FUSE_RANGE = 3.0                     # SwellGoal.canUse: distanceToSqr < 9
FUSE_ABORT_RANGE = 7.0               # SwellGoal.tick: distanceToSqr > 49 -> swellDir -1
EXPLOSION_RADIUS = 3.0               # Creeper.DEFAULT_EXPLOSION_RADIUS (x 2 when powered)
SWELL_XZ, SWELL_Y, SWELL_WOBBLE = 0.4, 0.1, 100.0  # CreeperRenderer.scale
WHITE_MAX = 0.75                     # OverlayTexture: white rows alpha = 1 - u / 15 * 0.75

# ---- EntityTypes.SKELETON sized(0.6F, 1.99F).eyeHeight(1.74F); AbstractSkeleton: MOVEMENT_SPEED 0.25,
#      RangedBowAttackGoal(this, 1.0, 20, 15.0F), getAttackInterval 40, getHardAttackInterval 20
SKELETON_SIZE = (0.6, 1.99)
SKELETON_EYE = 1.74
SKELETON_SPEED = mobs.mob_speed(1.0, 0.25)         # 2.753 blocks / s
BOW_DRAW_TICKS = 20                  # RangedBowAttackGoal.tick: getTicksUsingItem() >= 20 -> release
BOW_PULL_TICKS = (13, 18)            # items/bow.json: use_duration x 0.05 >= 0.65 -> pulling_1, >= 0.9 -> pulling_2
BOW_VARIANTS = ("bow", "bow_pulling_0", "bow_pulling_1", "bow_pulling_2")
ATTACK_INTERVAL_TICKS = {"easy": 40, "normal": 40, "hard": 20}
SKELETON_ATTACK_RANGE = 15.0         # RangedBowAttackGoal attackRadius
BOW_ARM_IN, BOW_ARM_OFF = 0.1, 0.4   # HumanoidModel.poseRightArm BOW_AND_ARROW: -0.1 + head.yRot / 0.1 + head.yRot + 0.4
HAND_SHIFT = 1.0                     # SkeletonModel.translateToHand: arm.x += +-1 (px) before translateAndRotate

# ---- arrows: AbstractSkeleton.performRangedAttack, Projectile.shoot, AbstractArrow, ArrowModel, ArrowRenderer
ARROW_SPEED = 1.6                    # blocks per tick (32 blocks / s) from a skeleton
PLAYER_ARROW_SPEED = 3.0             # BowItem: power 1.0 x 3.0 (a fully drawn player bow)
ARROW_AIM_LIFT = 0.2                 # dy + horizontal distance * 0.2F
ARROW_AIM_HEIGHT = 1.0 / 3.0         # target.getY(0.3333333333333333)
ARROW_SPAWN_DROP = 0.1               # AbstractArrow(type, owner, ...): owner.getEyeY() - 0.1
ARROW_INACCURACY = {"easy": 10.0, "normal": 6.0, "hard": 2.0}     # RangedAttackMob: 14 - difficulty id * 4
ARROW_SPREAD = 0.0172275             # Projectile.getMovementToShoot: triangle(0, 0.0172275 * inaccuracy)
ARROW_GRAVITY = 0.05                 # AbstractArrow.getDefaultGravity
ARROW_DRAG = 0.99                    # AbstractArrow.getAirDrag (0.6 in water)
ARROW_ROT_LERP = 0.2                 # Projectile.lerpRotation
ARROW_HIT_MARGIN = 0.3               # ProjectileUtil.getEntityHitResult: target box inflated by 0.3
ARROW_BLOCK_BACKOFF = 0.05           # AbstractArrow.onHitBlock: position moved back 0.05 along the motion
ARROW_SHAKE_TICKS = 7                # AbstractArrow.onHitBlock: shakeTime = 7
ARROW_KNOCKBACK = 0.4                # LivingEntity.hurtServer: knockback(0.4, ...) along the arrow's motion
ARROW_MODEL_SCALE = 0.9              # ArrowModel.createBodyLayer: MeshDefinition.transformed(p -> p.scaled(0.9F))
ARROW_SIZE = (0.5, 0.5)              # EntityTypes.ARROW
PLAYER_ARROW_PARTS = ("head", "body", "arm_l", "arm_r", "leg_l", "leg_r")   # PlayerModel.bodyParts order

# ---- explosion particles: HugeExplosionSeedParticle, HugeExplosionParticle, ClientExplosionTracker,
#      Level.DEFAULT_EXPLOSION_BLOCK_PARTICLES, ExplodeParticle (poof), SmokeParticle / BaseAshSmokeParticle
EMITTER_TICKS, EMITTER_PER_TICK, EMITTER_SPREAD = 8, 6, 4.0
BLOCK_PARTICLES_MAX = 512
EXPLOSION_SPRITES = tuple("explosion_%d" % i for i in range(16))      # particles/explosion.json (client jar)
GENERIC_SPRITES = tuple("generic_%d" % i for i in range(7, -1, -1))   # particles/poof.json and smoke.json
POOF_GLOW = 0.25                     # self-light of poof / smoke at night (piglins.POOF_GLOW; fx's 0.6 burns white)
RESISTANCE = {"air": None, "grass_block": 0.6, "dirt": 0.5, "dirt_path": 0.65, "coarse_dirt": 0.5, "farmland": 0.6,
              "stone": 6.0, "cobblestone": 6.0, "mossy_cobblestone": 6.0, "stone_bricks": 6.0, "gravel": 0.6,
              "sand": 0.5, "oak_planks": 3.0, "oak_log": 2.0, "oak_fence": 3.0, "oak_leaves": 0.2, "glass": 0.3,
              "short_grass": 0.0, "tall_grass": 0.0, "poppy": 0.0, "dandelion": 0.0, "torch": 0.0}

FACTS = {
    "creeper_speed_blocks_per_s": CREEPER_SPEED, "creeper_stroll_blocks_per_s": CREEPER_STROLL,
    "fuse_ticks_to_explosion": FUSE_TICKS - 1, "fuse_frames_to_explosion": int(math.ceil((FUSE_TICKS - 1) * TICK)),
    "fuse_starts_within_blocks": FUSE_RANGE, "fuse_aborts_beyond_blocks": FUSE_ABORT_RANGE,
    "explosion_radius": EXPLOSION_RADIUS, "skeleton_speed_blocks_per_s": SKELETON_SPEED,
    "bow_draw_ticks": BOW_DRAW_TICKS, "skeleton_shot_every_ticks": {k: v + BOW_DRAW_TICKS for k, v in
                                                                     ATTACK_INTERVAL_TICKS.items()},
    "arrow_speed_blocks_per_s": ARROW_SPEED * 20.0, "stuck_arrow_first_removed_after_ticks_with_2": 20 * (30 - 2),
}


def _note(text):
    print("[hostiles] " + text)


# ----------------------------------------------------------------------------------------------------
# Java's random (SingleThreadedRandomSource / BitRandomSource): the stuck-arrow placement is seeded per entity id
# ----------------------------------------------------------------------------------------------------
class JavaRandom:
    """java.util.Random's LCG as net.minecraft.world.level.levelgen.SingleThreadedRandomSource implements it."""

    MULT, MASK = 0x5DEECE66D, (1 << 48) - 1

    def __init__(self, seed):
        self.seed = (int(seed) ^ self.MULT) & self.MASK

    def next(self, bits):
        """next(bits): the top `bits` bits of the new state."""
        self.seed = (self.seed * self.MULT + 0xB) & self.MASK
        r = self.seed >> (48 - bits)
        return r - (1 << 32) if r >= (1 << 31) else r

    def next_int(self, bound):
        """nextInt(bound) of BitRandomSource."""
        if bound & (bound - 1) == 0:
            return (bound * self.next(31)) >> 31
        while True:
            bits = self.next(31)
            val = bits % bound
            if bits - val + (bound - 1) < (1 << 31):
                return val

    def next_float(self):
        """nextFloat(): next(24) * 5.9604645E-8."""
        return self.next(24) * 5.9604645e-08


def game_arrow_spot(entity_id, index):
    """(part, (f1, f2, f3)) of stuck arrow number `index` (0 = the first) on the player with entity id `entity_id`,
    exactly as StuckInBodyLayer.submit draws it (RandomSource.createThreadLocalInstance(id); per arrow:
    PlayerModel.getRandomBodyPart = nextInt(6), getRandomCube = nextInt(1), three nextFloat)."""
    r = JavaRandom(entity_id)
    out = None
    for _i in range(int(index) + 1):
        part = PLAYER_ARROW_PARTS[r.next_int(6)]
        r.next_int(1)
        out = (part, (r.next_float(), r.next_float(), r.next_float()))
    return out


def stuck_arrow_lifetime(count, first_frame=0):
    """Frames (from the first hit) on which the game removes the stuck arrows of a character hit `count` times
    in quick succession: LivingEntity.tick sets removeArrowTime = 20 * (30 - n) when it runs out, one arrow goes
    each time (the one drawn last)."""
    out, t, n = [], 0, int(count)
    while n > 0:
        t += 20 * (30 - n)
        out.append(int(round(first_frame + t * TICK)))
        n -= 1
    return out


# ----------------------------------------------------------------------------------------------------
# models (pixels, the game's model space: x to the mob's left, y DOWN, z to its back, feet on y = 24)
# ----------------------------------------------------------------------------------------------------
LEG_CLIP = 0.02                      # px: the creeper's touching legs are trimmed apart (no coplanar faces)
SHELL_GROW = 0.01                    # px: the white-flash shells sit this far outside the body


def _creeper_spec(grow=0.0, clip=True):
    """net.minecraft.client.model.monster.creeper.CreeperModel.createBodyLayer(NONE), 64 x 32 (unscaled)."""
    C = ch._cube
    c = 2.0 - LEG_CLIP

    def leg(name, x, z):
        part = dict(name=name, parent="hips", pivot=(x, 18, z), groups=[([], [C(0, 16, -2, 0, -2, 4, 6, 4, grow=grow)])])
        if clip:
            part["xclip"] = (None, c) if x < 0 else (-c, None)
        return part

    return dict(
        tex=(64, 32), scale=1.0, hip=18.0, top=-2.0, eye=24.0 - 0.85 * CREEPER_SIZE[1] * 16.0, back=2.0,
        sleep_eye=0.85 * CREEPER_SIZE[1],
        parts=[
            dict(name="body", parent="hips", pivot=(0, 6, 0), groups=[([], [C(16, 16, -4, 0, -2, 8, 12, 4, grow=grow)])]),
            dict(name="head", parent="body", pivot=(0, 6, 0), groups=[([], [C(0, 0, -4, -8, -4, 8, 8, 8, grow=grow)])]),
            leg("leg_r", -2, 4),           # right_hind_leg
            leg("leg_l", 2, 4),            # left_hind_leg
            leg("leg_fr", -2, -4),         # right_front_leg
            leg("leg_fl", 2, -4),          # left_front_leg
        ])


def _skeleton_spec():
    """net.minecraft.client.model.monster.skeleton.SkeletonModel.createBodyLayer(): HumanoidModel.createMesh(NONE, 0)
    with createDefaultSkeletonMesh's arms and legs, 64 x 32 (AbstractSkeletonRenderer has no scale)."""
    C = ch._cube
    return dict(
        tex=(64, 32), scale=1.0, hip=12.0, top=-8.0, eye=24.0 - SKELETON_EYE * 16.0, back=2.0, sleep_eye=SKELETON_EYE,
        parts=[
            dict(name="body", parent="hips", pivot=(0, 12, 0), groups=[([ch._pose(0, -12, 0)], [
                C(16, 16, -4, 0, -2, 8, 12, 4)])]),
            dict(name="head", parent="body", pivot=(0, 0, 0), groups=[([], [
                C(0, 0, -4, -8, -4, 8, 8, 8),
                C(32, 0, -4, -8, -4, 8, 8, 8, grow=0.5)])]),               # hat (empty in skeleton.png)
            dict(name="arm_r", parent="body", pivot=(-5, 2, 0), groups=[([], [C(40, 16, -1, -2, -1, 2, 12, 2)])]),
            dict(name="arm_l", parent="body", pivot=(5, 2, 0), groups=[([], [C(40, 16, -1, -2, -1, 2, 12, 2, mirror=True)])]),
            dict(name="leg_r", parent="hips", pivot=(-2, 12, 0), groups=[([], [C(0, 16, -1, 0, -1, 2, 12, 2)])]),
            dict(name="leg_l", parent="hips", pivot=(2, 12, 0), groups=[([], [C(0, 16, -1, 0, -1, 2, 12, 2, mirror=True)])]),
        ])


def _sheet(path):
    """(key, HxWx4 uint8) of an entity texture, cut out at alpha 0.1 as the game's cut-out render types do."""
    arr = ch._game_texture(path)
    sheet = np.zeros_like(arr)
    ch._over(sheet, arr)
    return "hostiles_" + path.split("/")[-1], sheet


# ----------------------------------------------------------------------------------------------------
# what hangs on a character: stuck arrows, bow variants, white shells (visibility follows the character)
# ----------------------------------------------------------------------------------------------------
_BOOK = "_hostiles_book"


def _book(c):
    """This module's bookkeeping on a character (made on first use; wraps its show / place so that everything
    hanging on it follows its visibility). undead's own wrappers are installed first, so these are the outer ones."""
    st = c.__dict__.get(_BOOK)
    if st is None:
        undead._state(c)
        st = c.__dict__[_BOOK] = dict(followers=[], arrows=[])
        for name in ("show", "place"):
            inner = getattr(c, name)

            def wrapper(*args, _inner=inner, **kwargs):
                out = _inner(*args, **kwargs)
                refresh(c)
                return out

            wrapper.__doc__ = inner.__doc__
            c.__dict__[name] = wrapper
    return st


def _follow(c, ob, rule, edges, red=False):
    """Hang `ob` on character c: rendered when c is shown and there (and, red=True, not flashing red) and
    rule(frame) is true. edges = the frames where rule changes."""
    st = _book(c)
    st["followers"].append(dict(object=ob, rule=rule, edges=set(int(e) for e in edges), red=red))
    ob.hide_render = ob.hide_viewport = True
    refresh(c)


def _curve_value(keys, f, default):
    value = default
    if keys is None:
        return default
    for kf, kv in keys:
        if kf <= f + 1e-6:
            value = kv > 0.5
    return value


def refresh(c):
    """Recompute the visibility of every stuck arrow, bow variant and white shell this module hangs on `c` from
    its show() timeline, undead's vanish / death (presence) and red flashes. Returns the number of objects."""
    st = c.__dict__.get(_BOOK)
    if not st:
        return 0
    ust = c.__dict__.get(undead._STATE)
    root_keys = undead._hide_curve(c.root)
    root_hidden = bool(c.root.hide_render)
    base = set()
    if root_keys:
        base |= {int(round(k[0])) for k in root_keys}
    if ust:
        base |= {int(f) for f, _on, _w in ust["presence"] if f is not None}
    for fo in st["followers"]:
        edges = set(base) | fo["edges"]
        if fo["red"] and ust:
            edges |= {int(f) for a, b in ust["flashes"] for f in (a, b)}
        if not edges:
            edges = {1}
        frames = sorted(edges)
        frames = [min(frames[0], 1) - 1] + frames

        def hidden(f, fo=fo):
            shown = not _curve_value(root_keys, f, root_hidden)
            there = undead._present(ust, f) if ust else True
            red = bool(fo["red"] and ust and undead._flashing(ust, f))
            return not (shown and there and not red and fo["rule"](f))

        undead._set_hide(fo["object"], [(f, hidden(f)) for f in frames])
    return len(st["followers"])


# ----------------------------------------------------------------------------------------------------
# small keyframe helpers
# ----------------------------------------------------------------------------------------------------
def _copy_channel(src, dst, path, index):
    """Make dst.<path>[index] an exact copy of src's (keys, interpolation, handles)."""
    fs = ch._find(src, path, index)
    fd = ch._find(dst, path, index)
    if fd is not None:
        fd.keyframe_points.clear()
    if fs is None or not len(fs.keyframe_points):
        getattr(dst, path)[index] = getattr(src, path)[index]
        if fd is not None:
            fd.update()
        return
    fd = ch._ensure(dst, path, index)
    n = len(fs.keyframe_points)
    fd.keyframe_points.add(n)
    for a, b in zip(fs.keyframe_points, fd.keyframe_points):
        b.co = a.co
        b.interpolation = a.interpolation
        b.easing = a.easing
        b.handle_left_type, b.handle_right_type = a.handle_left_type, a.handle_right_type
        b.handle_left, b.handle_right = a.handle_left, a.handle_right
    fd.update()


def _add_bob(ob, sgn, age0):
    """AnimationUtils.bobModelPart as F-curve modifiers (the same that engine.undead puts on its arms)."""
    m = ch._ensure(ob, _ROT, 1).modifiers.new("FNGENERATOR")
    m.function_type, m.use_additive = "COS", True
    m.amplitude, m.value_offset = sgn * undead.BOB_AMOUNT, sgn * undead.BOB_AMOUNT
    m.phase_multiplier, m.phase_offset = undead.BOB_Z_RATE / TICK, undead.BOB_Z_RATE * age0
    m = ch._ensure(ob, _ROT, 0).modifiers.new("FNGENERATOR")
    m.function_type, m.use_additive = "SIN", True
    m.amplitude, m.value_offset = sgn * undead.BOB_AMOUNT, 0.0
    m.phase_multiplier, m.phase_offset = undead.BOB_X_RATE / TICK, undead.BOB_X_RATE * age0


def _mob_aim(c, target, frame):
    """Head (yaw, pitch-up) toward a target, clamped to the mob limits (Mob.getMaxHeadYRot 75 / XRot 40)."""
    if target is None:
        return 0.0, 0.0
    d = c._point(target, frame) - c.eye_point(frame)
    yaw = ch._clamp(ch._wrap(math.atan2(d.x, -d.y) - c.yaw_at(frame)), -undead.HEAD_YAW_MAX, undead.HEAD_YAW_MAX)
    pitch = ch._clamp(math.atan2(d.z, math.hypot(d.x, d.y)), -undead.HEAD_PITCH_MAX, undead.HEAD_PITCH_MAX)
    return yaw, pitch


# ----------------------------------------------------------------------------------------------------
# the creeper
# ----------------------------------------------------------------------------------------------------
def swell_scale(s):
    """(xz, y) scale of CreeperRenderer.scale for swelling s (= swell / 28)."""
    w = 1.0 + math.sin(s * SWELL_WOBBLE) * s * 0.01
    q = ch._clamp(s, 0.0, 1.0) ** 4
    return (1.0 + q * SWELL_XZ) * w, (1.0 + q * SWELL_Y) / w


def white_level(s):
    """OverlayTexture u of CreeperRenderer.getWhiteOverlayProgress for swelling s (0 = no white, 7..15)."""
    if int(s * 10.0) % 2 == 0:
        return 0
    return int(ch._clamp(s, 0.5, 1.0) * 15.0)


def white_fraction(u):
    """How much white the shader mixes in for overlay column u (entity.fsh: mix(overlay, colour, overlay.a))."""
    if u <= 0:
        return 0.0
    alpha = int((1.0 - u / 15.0 * WHITE_MAX) * 255.0) / 255.0
    return 1.0 - alpha


class Creeper(ch.Character):
    """The creeper: a Character with four legs, the swell and the white flash (see the module docstring)."""

    def __init__(self, name, parts, spec, sheet, collection):
        super().__init__(name, "creeper", parts, spec)
        self.spec, self._sheet, self.collection = spec, sheet, collection
        self.leg_fr, self.leg_fl = parts["leg_fr"], parts["leg_fl"]
        self.swell = parts["swell"]
        self.size = CREEPER_SIZE
        self.walk_speed = CREEPER_SPEED
        self.last_walk = None
        self.last_explosion = None
        self._events = []                # (frame, kind): 'up' | 'down' | 'reset' | 'freeze'
        self._shells = {}                # overlay column u -> [shell objects]
        self._white_edges = set()
        _book(self)

    def __repr__(self):
        return "<Creeper %s>" % self.name

    # ------------------------------------------------------------------ legs
    def _sync_legs(self):
        """The front legs copy the hind legs of the other side (CreeperModel: right hind = left front)."""
        _copy_channel(self.leg_l, self.leg_fr, _ROT, 0)
        _copy_channel(self.leg_r, self.leg_fl, _ROT, 0)

    def _aim(self, target, frame):
        return _mob_aim(self, target, frame)

    def place(self, frame, pos, yaw=0.0, keep_pose=False):
        """Hard cut to a spot: upright, legs together, not swollen (whatever was keyed before ends here)."""
        super().place(frame, pos, yaw, keep_pose=keep_pose)
        if not keep_pose:
            self._events = [e for e in self._events if not (e[0] == int(frame) and e[1] == "reset")]
            self._events.append((int(frame), "reset"))
            self._apply_swell()
        self._sync_legs()

    def step(self, frame, toward, blocks=0.5, frames=14, swing=None):
        """ONE slow step toward `toward` (a point or a Character): the body glides `blocks` forward over
        `frames` while one diagonal pair swings out to +-`swing` and back (sin over the step), the other pair
        the opposite way. swing (degrees) None = 44, the game's leg angle at chasing speed (then the feet travel
        about the half block the body does). The game has no such move: at 0.8 blocks/s its leg wave is only
        +-13 degrees and the feet slide. Returns the end frame."""
        f0, n = int(round(frame)), max(4, int(frames))
        here = self.pos_at(f0)
        aim = self._point(toward, f0) if not isinstance(toward, (tuple, list, Vector)) else ch._vec3(toward)
        d = Vector((aim.x - here.x, aim.y - here.y, 0.0))
        if d.length < 1e-6:
            d = Vector((math.sin(self.yaw_at(f0)), -math.cos(self.yaw_at(f0)), 0.0))
        to = here + d.normalized() * float(blocks)
        f1 = ch.Character.walk(self, f0, [here, to], speed=float(blocks) / (n / FPS), run=False)
        amp = math.radians(44.2 if swing is None else float(swing))
        n = f1 - f0
        times = [i * 0.5 for i in range(2 * n + 1)]
        mobs._sample(self.leg_r, _ROT, 0, f0, times, lambda t: -amp * math.sin(math.pi * t / n))
        mobs._sample(self.leg_l, _ROT, 0, f0, times, lambda t: amp * math.sin(math.pi * t / n))
        self._sync_legs()
        self.last_walk = dict(frames=(f0, f1), blocks=float(blocks), speed=float(blocks) / n * FPS, swing=amp,
                              cycle_blocks=2.0 * float(blocks), cycle_frames=2.0 * n)
        refresh(self)
        return f1

    def walk(self, frame, points, speed=None, run=False, from_current=False, swing=None):
        """Travel along `points` at the game's creeper speed with the game's four-legged leg wave; returns the
        end frame (see the module docstring). swing = the leg amplitude in degrees instead of the game's
        1.4 x the walk-animation speed (a film choice)."""
        speed = self.walk_speed if speed is None else float(speed)
        f0 = int(round(frame))
        f1 = ch.Character.walk(self, f0, points, speed=speed, run=False, from_current=from_current)
        n = f1 - f0
        if n <= 0:
            self._sync_legs()
            return f1
        fcx = ch._find(self.root, _LOC, 0)
        stamps = sorted({float(f0), float(f1)} | {float(kp.co.x) for kp in fcx.keyframe_points if f0 < kp.co.x < f1})
        spots = [self.pos_at(t) for t in stamps]
        acc = [0.0]
        for a, b in zip(spots, spots[1:]):
            acc.append(acc[-1] + (b - a).length)
        total = acc[-1]
        rest_z = self._rest(self.hips, _LOC, 2)
        ch._segment(self.body, _ROT, 1, [(f0, None), (f1, 0.0)])          # (no waddle: the model has none)
        ch._segment(self.hips, _LOC, 2, [(f0, None), (f1, rest_z)])
        if total < 1e-6:
            self._sync_legs()
            return f1
        per_tick = total / n * TICK
        anim = min(undead.ANIM_PER_BLOCK * per_tick, 1.0)                # LivingEntity.updateWalkAnimation
        rate = anim / per_tick * undead.LEG_RATE                         # leg phase per block
        amp = undead.LEG_SWING * anim if swing is None else math.radians(float(swing))

        def dist(t):
            return float(np.interp(f0 + t, stamps, acc))

        def env(t):
            """The 0.4 lerp of the walk-animation speed at the start, mirrored at the end."""
            k = 1.0 - undead.ANIM_LERP
            return max(0.0, min(1.0 - k ** (t / TICK), 1.0 - k ** ((n - t) / TICK)))

        def c(t):
            return amp * env(t) * math.cos(rate * dist(t))

        step = min(1.0, (2.0 * math.pi / rate) / (total / n) / 12.0)
        times = [i * step for i in range(int(math.floor(n / step)) + 1)] + [float(n)]
        mobs._sample(self.leg_r, _ROT, 0, f0, times, lambda t: -c(t))     # right hind: cos(p + pi)
        mobs._sample(self.leg_l, _ROT, 0, f0, times, c)                   # left hind: cos(p)
        self._sync_legs()
        self.last_walk = dict(frames=(f0, f1), blocks=total, speed=total / n * FPS, swing=amp,
                              cycle_blocks=2.0 * math.pi / rate, cycle_frames=2.0 * math.pi / rate / (total / n))
        refresh(self)
        return f1

    def idle(self, frame_start, frame_end, seed=0):
        """The head looks around now and then (RandomLookAroundGoal), as undead's idle."""
        undead.Undead.idle(self, frame_start, frame_end, seed)

    def face(self, frame, target, ease=8, keep_head=False):
        """Turn the whole body toward a target (Character.face); the front legs follow the shuffle."""
        out = super().face(frame, target, ease=ease, keep_head=keep_head)
        self._sync_legs()
        return out

    # ------------------------------------------------------------------ the swell
    def swell_ticks(self, t):
        """The swell counter (0..29, lerped per partial tick as Creeper.getSwelling does) at time t (frames)."""
        s, d, last, frozen = 0.0, 0, None, False
        for fe, kind in sorted(self._events):
            if fe > t + 1e-9:
                break
            if last is not None and not frozen:
                s = ch._clamp(s + d * (fe - last) / TICK, 0.0, FUSE_TICKS - 1.0)
            last = fe
            if kind == "reset":
                s, d, frozen = 0.0, 0, False
            elif kind == "freeze":
                frozen, d = True, 0
            elif not frozen:
                d = 1 if kind == "up" else -1
        if last is not None and not frozen:
            s = ch._clamp(s + d * (t - last) / TICK, 0.0, FUSE_TICKS - 1.0)
        return s

    def swelling_at(self, frame):
        """getSwelling at `frame`: swell / 28 (1.0 = full size, 1.036 just before the explosion)."""
        return self.swell_ticks(frame) / SWELL_DIV

    def white_at(self, frame):
        """How much white is mixed into the texture at `frame` (0 while red: the red rows win)."""
        ust = self.__dict__.get(undead._STATE)
        if ust and undead._flashing(ust, frame):
            return 0.0
        return white_fraction(white_level(self.swelling_at(frame)))

    def _shell_set(self, u):
        """The white shells for overlay column u (built on first use, parented to the parts)."""
        if u in self._shells:
            return self._shells[u]
        w = white_fraction(u)
        sheet = self._sheet.copy()
        rgb = sheet[..., :3].astype(np.float32)
        sheet[..., :3] = np.clip(np.round(rgb * (1.0 - w) + 255.0 * w), 0, 255).astype(np.uint8)
        key = "hostiles_creeper_white%02d" % u
        mat = ch._sheet_material(key, sheet)
        spec = _creeper_spec(grow=SHELL_GROW, clip=False)
        unit = spec["scale"] / 16.0
        obs = []
        for part in spec["parts"]:
            host = self.parts[part["name"]]
            me = ch._part_mesh("%s_white%02d_%s" % (self.name, u, part["name"]), part, sheet, unit, mat)
            ob = bpy.data.objects.new(me.name, me)
            self.collection.objects.link(ob)
            ob.parent = host
            ob.matrix_parent_inverse = Matrix.Identity(4)
            obs.append(ob)
            _follow(self, ob, lambda f, u=u: white_level(self.swelling_at(f)) == u, (), red=True)
        self._shells[u] = obs
        return obs

    def _apply_swell(self):
        """Key the swell empty's scale (every quarter frame while it changes) and the white shells' frames."""
        if not self._events:
            return
        frames = sorted(e[0] for e in self._events)
        lo, hi = frames[0] - 1, frames[-1] + int(math.ceil(FUSE_TICKS * TICK)) + 2
        times, values = [], []
        prev = None
        t = float(lo)
        while t <= hi + 1e-9:
            s = self.swelling_at(t)
            sxz, sy = swell_scale(s)
            v = (sxz, sxz, sy)
            if prev is None or any(abs(a - b) > 1e-7 for a, b in zip(v, prev)) or t >= hi - 1e-9:
                times.append(t)
                values.append(v)
            elif times[-1] != t - 0.25:                    # hold: one key where a constant run starts
                times.append(t)
                values.append(v)
            prev = v
            t += 0.25
        for i in range(3):
            fx._write(self.swell, "scale", i, times, [v[i] for v in values], "LINEAR")
        # the white levels on whole frames (the frame shows the state at its start)
        levels = {}
        edges = set()
        last = None
        for f in range(int(lo), int(hi) + 1):
            u = white_level(self.swelling_at(f))
            if u:
                levels.setdefault(u, []).append(f)
            if u != last:
                edges.add(f)
            last = u
        for u in levels:
            self._shell_set(u)
        for u, obs in self._shells.items():
            for ob in obs:
                for fo in self.__dict__[_BOOK]["followers"]:
                    if fo["object"] is ob:
                        fo["edges"] = set(edges)
        refresh(self)

    def fuse(self, frame_start, frame_end=None):
        """Start the swell on frame_start; frame_end = where it is aborted (it shrinks back). Returns the frame it
        explodes on (frame_end None) or the frame it is back to normal size."""
        f0 = int(round(frame_start))
        self._events = [e for e in self._events if not (e[0] == f0 and e[1] in ("up", "down"))] + [(f0, "up")]
        if frame_end is not None:
            f1 = int(round(frame_end))
            if f1 <= f0:
                raise ValueError("fuse: frame_end must come after frame_start")
            self._events.append((f1, "down"))
        self._apply_swell()
        if frame_end is None:                                        # swell reaches 30 on the 30th tick
            return f0 + int(math.ceil((FUSE_TICKS - 1) * TICK - 1e-9))
        s = self.swell_ticks(f1)
        return int(math.ceil(f1 + s * TICK))

    def hurt(self, frame, attacker=None, knockback=None, max_back=None, flash=True):
        """undead.hurt for the creeper: red 12 frames (no white meanwhile), legs kick, hop only with an attacker."""
        end = undead.hurt(self, frame, attacker=attacker, knockback=knockback, max_back=max_back, flash=flash)
        self._sync_legs()
        refresh(self)
        return end

    def die(self, frame, camera=None, glow=POOF_GLOW, **kw):
        """undead.die for the creeper: red, tips over still swollen, gone with the poof on frame + 24."""
        gone = undead.die(self, frame, camera=camera, glow=glow, **kw)
        f0 = int(round(frame))
        self._events = [e for e in self._events if e[1] != "freeze" or e[0] < f0] + [(f0, "freeze")]
        self._apply_swell()
        self._sync_legs()
        refresh(self)
        return gone

    def explode(self, frame, camera=None, village=None, victims=(), blocks=None, griefing=True, seed=0, glow=None,
                smoke_glow=None, collection=None, latency=False):
        """The creeper is gone ON `frame` and the explosion's particles fly (see explosion(): latency=False, the
        film's default, starts them on `frame` too; True keeps the game's one empty tick); characters in
        `victims` are pushed away from the centre. Returns the centre (its feet)."""
        f0 = int(round(frame))
        centre = self.pos_at(f0)
        self._events = [e for e in self._events if e[1] != "freeze" or e[0] < f0] + [(f0, "freeze")]
        self._apply_swell()
        undead.vanish(self, f0, why="exploded")
        burst = explosion(centre, f0, camera=camera, radius=EXPLOSION_RADIUS, village=village, blocks=blocks,
                          griefing=griefing, seed=seed, glow=glow, smoke_glow=smoke_glow, collection=collection,
                          latency=latency)
        pushed = []
        for v in victims:
            info = blast_push(centre, v, f0, radius=EXPLOSION_RADIUS)
            if info is None:
                continue
            impact = info["impact"]
            if _is_player(v):
                v.hurt(f0, from_point=centre, knockback=impact)
            else:
                undead.hurt(v, f0, attacker=centre, knockback=impact / undead.KNOCKBACK)
            refresh(v)
            pushed.append((v.name, round(impact, 3)))
        refresh(self)
        self.last_explosion = dict(frame=f0, centre=centre, burst=burst, blocks=burst.blocks, pushed=pushed)
        return centre


def make_creeper(name, collection=None):
    """Build the vanilla creeper (feet at the origin, facing -Y)."""
    key, sheet = _sheet("entity/creeper/creeper")
    spec = _creeper_spec()
    col = ch._collection(collection)
    parts = ch._build_rig(name, spec, sheet, ch._sheet_material(key, sheet), col)
    swell = bpy.data.objects.new(name + "_swell", None)              # the scale of CreeperRenderer.scale
    swell.empty_display_size = 0.2
    col.objects.link(swell)
    swell.parent = parts["root"]
    parts["hips"].parent = swell
    parts["hips"].matrix_parent_inverse = Matrix.Identity(4)
    parts["swell"] = swell
    return Creeper(name, parts, spec, sheet, col)


def add_creeper(st, name="creeper", **kw):
    """A creeper registered with a films.lookdev.Stage (st.cast[name])."""
    c = st.cast.get(name)
    if c is None:
        c = st.cast[name] = make_creeper(name, **kw)
    return c


# ----------------------------------------------------------------------------------------------------
# the skeleton
# ----------------------------------------------------------------------------------------------------
class Skeleton(undead.Undead):
    """The skeleton with its bow: an undead.Undead with the humanoid arm swing and the BOW_AND_ARROW poses."""

    def __init__(self, name, parts, spec, hands, bows, left_handed=False):
        self.spec, self.hands, self.bows, self.left_handed = spec, hands, bows, bool(left_handed)
        self._draws = []                 # (start, release)
        super().__init__(name, parts, spec, kind="skeleton", variant="skeleton")
        self.size = SKELETON_SIZE
        self.walk_speed = SKELETON_SPEED
        for arm in (self.arm_r, self.arm_l):                         # HumanoidModel: arms hang (EMPTY pose)
            self._set_rest(arm, _ROT, 0, 0.0)
            self._set_rest(arm, _ROT, 2, 0.0)
        for side, sgn in (("r", 1.0), ("l", -1.0)):
            _add_bob(self.hands[side], sgn, self._age0)
        for variant, ob in self.bows.items():
            _follow(self, ob, lambda f, v=variant: self.bow_at(f) == v, ())
        self._bake_arms()

    def __repr__(self):
        return "<Skeleton %s%s>" % (self.name, " left-handed" if self.left_handed else "")

    # ------------------------------------------------------------------ arms
    def _aggro_events(self):
        """The aim / lower events as the arms play them: A DRAWN BOW ALWAYS HAS ITS ARMS UP (the game draws
        BOW_AND_ARROW the whole time the skeleton has a target, and it has one while it draws). Inside a draw
        (start < frame < release) every lower and every place() cut becomes a snap up (ease 0); on the release
        frame a cut does too (an explicit lower(release) is kept); a draw that starts on a cut frame snaps up."""
        cuts = set(getattr(self, "_cuts", ()))
        ev = {}
        for e in sorted(self._aggro):
            ev[e[0]] = e
        for s, r in self._draws:
            for fr, (_f, on, ease) in list(ev.items()):
                if on:
                    if fr == s and s in cuts and ease > 0:
                        ev[fr] = (fr, True, 0)
                elif s < fr < r or (fr == r and fr in cuts):
                    ev[fr] = (fr, True, 0)
        return sorted(ev.values())

    def aiming_at(self, t):
        """0..1: how far the arms are in the bow pose at time t (aim / lower events, with their ease; a drawn bow
        always has its arms up, see _aggro_events)."""
        w = 0.0
        for start, on, ease in self._aggro_events():
            target = 1.0 if on else 0.0
            if ease <= 0:
                if t >= start - ch.CUT_LEAD - 1e-9:
                    w = target
            elif t >= start + ease:
                w = target
            elif t > start:
                w += (target - w) * mobs._ease((t - start) / float(ease))
        return w

    def arm_base(self, frame):
        """(Undead's name for it) the right arm's pitch without swing and bob."""
        return self._arm_values(frame)[0]

    def _arm_values(self, t):
        """Rig (x, z) of the right arm and of the left arm at time t, without the bob."""
        w = self.aiming_at(t)
        lr = ch._val(self.leg_r, _ROT, 0, t)
        ll = ch._val(self.leg_l, _ROT, 0, t)
        wxr, wxl = -lr / undead.LEG_SWING, -ll / undead.LEG_SWING       # HumanoidModel: arm = cos(p + pi) s, leg 1.4 s
        if w <= 0.0:
            return wxr, 0.0, wxl, 0.0
        hx = ch._val(self.head, _ROT, 0, t)                              # model head xRot
        hz = ch._val(self.head, _ROT, 2, t)                              # = -model head yRot
        px = -math.pi / 2.0 + hx
        if self.left_handed:                                             # poseLeftArm BOW_AND_ARROW, mirrored
            zr, zl = BOW_ARM_IN + BOW_ARM_OFF + hz, -BOW_ARM_IN + hz
        else:
            zr, zl = BOW_ARM_IN + hz, -(BOW_ARM_IN + BOW_ARM_OFF) + hz
        return (wxr + (px - wxr) * w, zr * w, wxl + (px - wxl) * w, zl * w)

    def _bake_arms(self):
        """Rewrite the arms (and the hands that carry the bow) from legs, head and aim events; the bob is an
        F-curve modifier on top."""
        if not hasattr(self, "hands") or not hasattr(self, "_aggro"):
            return
        times = set()
        for ob in (self.leg_r, self.leg_l):
            fc = ch._find(ob, _ROT, 0)
            if fc is not None:
                times |= {float(kp.co.x) for kp in fc.keyframe_points}
        end = 1.0
        for ob, path in ((self.head, _ROT), (self.root, _LOC), (self.root, _ROT), (self.leg_r, _ROT)):
            for i in range(3):
                fc = ch._find(ob, path, i)
                if fc is not None and len(fc.keyframe_points):
                    end = max(end, float(fc.keyframe_points[-1].co.x))
        for _s, r in self._draws:
            end = max(end, r + 2.0)
        events = self._aggro_events()
        for start, on, ease in events:
            end = max(end, float(start + ease) + 1.0)
            if ease <= 0:
                times |= {start - ch.CUT_LEAD - 0.03, start - ch.CUT_LEAD}
            else:
                times |= {float(start + i) for i in range(int(ease) + 1)}
        aim_on = sorted(f for f, on, _e in events if on)
        if aim_on:
            hfc = [ch._find(self.head, _ROT, i) for i in (0, 2)]
            hkeys = {float(kp.co.x) for fc in hfc if fc is not None for kp in fc.keyframe_points}
            for f in range(int(aim_on[0]) - 1, int(end) + 2):
                if self.aiming_at(f) > 0.0 or self.aiming_at(f + 1) > 0.0:
                    times.add(float(f))
            times |= {t for t in hkeys if self.aiming_at(t) > 0.0}
        times.add(min(times | {1.0}) - 1.0)
        frames = []
        for t in sorted(times):
            if not frames or t - frames[-1] > 0.011:
                frames.append(t)
        vals = [self._arm_values(t) for t in frames]
        for arm, hand, ix, iz in ((self.arm_r, self.hands["r"], 0, 1), (self.arm_l, self.hands["l"], 2, 3)):
            for ob in (arm, hand):
                fx._write(ob, _ROT, 0, frames, [v[ix] for v in vals], "LINEAR")
                fx._write(ob, _ROT, 1, frames[:1], [0.0], "LINEAR")
                fx._write(ob, _ROT, 2, frames, [v[iz] for v in vals], "LINEAR")

    def aggro(self, frame, on=True, ease=3):
        """Raise (on) or lower the bow arms from `frame` over `ease` frames (the game snaps: ease=0)."""
        frame, ease = int(round(frame)), max(0, int(ease))
        self._aggro = [e for e in self._aggro if e[0] != frame] + [(frame, bool(on), ease)]
        self._bake_arms()
        return frame + ease

    def aim(self, frame, target=None, ease=3):
        """RAISE: arms up in the bow pose from `frame` (over `ease` frames), head on `target` (if given)."""
        f0 = int(round(frame))
        if target is not None:
            self.look_at(f0, target, ease=ease)
        return self.aggro(f0, True, ease)

    def lower(self, frame, ease=3):
        """LOWER: arms back down from `frame` (the skeleton has lost its target)."""
        return self.aggro(frame, False, ease)

    def raise_arm(self, frame, angle=None, ease=3, side="r"):
        """The skeleton has one raised pose: aim(frame)."""
        return self.aim(frame, None, ease)

    def attack(self, frame, target=None, **hurt_kw):
        """A skeleton with a bow never swings it: use draw() / shoot()."""
        raise ValueError("a skeleton holding a bow shoots (Skeleton.draw / shoot); it has no melee swing")

    def hold(self, obj, offset=None, rotation=None, item=None):
        """The skeleton's bow is built in (Skeleton.bows); other items are not supported."""
        if obj is None:
            return None
        raise ValueError("Skeleton.hold: the skeleton holds its own bow (see Skeleton.bows)")

    def bow_at(self, frame):
        """Which bow model is drawn at `frame` (items/bow.json: by use duration while drawing, else 'bow')."""
        for start, release in self._draws:
            if start <= frame + 1e-9 < release:
                ticks = int(math.floor((frame - start) / TICK + 1e-6))
                if ticks >= BOW_PULL_TICKS[1]:
                    return "bow_pulling_2"
                if ticks >= BOW_PULL_TICKS[0]:
                    return "bow_pulling_1"
                return "bow_pulling_0"
        return "bow"

    def _bow_edges(self):
        edges = set()
        for start, release in self._draws:
            edges |= {start, release}
            for k in BOW_PULL_TICKS:
                edges.add(int(math.ceil(start + k * TICK - 1e-6)))
        return edges

    def draw(self, frame_start, release=None, target=None, ease=3):
        """Draw the bow from frame_start and loose ON `release` (default: 20 ticks = 24 frames later, as the game);
        turns to `target` and keeps the head on it. Returns dict(frame, origin, direction, target)."""
        f0 = int(round(frame_start))
        f1 = f0 + int(round(BOW_DRAW_TICKS * TICK)) if release is None else int(round(release))
        if f1 <= f0:
            raise ValueError("draw: release must come after frame_start")
        if target is not None:
            here = self.pos_at(f0)
            aim = self._point(target, f0)
            want = math.atan2(aim.x - here.x, -(aim.y - here.y))
            turn = abs(ch._wrap(want - self.yaw_at(f0)))
            if turn > math.radians(8.0):                                 # Mob.lookAt(target, 30, 30): 30 degrees a tick
                self.face(f0, target, ease=max(2, int(math.ceil(turn / math.radians(30.0) * TICK))), keep_head=True)
            self.track(f0, f1 + 1, target, step=2, ease=max(1, ease))
        if self.aiming_at(f0 + ease) < 1.0:
            self._aggro = [e for e in self._aggro if e[0] != f0] + [(f0, True, max(0, int(ease)))]
        self._draws = sorted([d for d in self._draws if d[0] != f0] + [(f0, f1)])
        self._bake_arms()
        for fo in self.__dict__[_BOOK]["followers"]:
            if fo["object"] in self.bows.values():
                fo["edges"] = self._bow_edges()
        refresh(self)
        origin = self.pos_at(f1) + Vector((0.0, 0.0, SKELETON_EYE - ARROW_SPAWN_DROP))
        aim = self._point(target, f1) if target is not None else origin + self._look_vector(f1)
        d = aim - origin
        return dict(frame=f1, origin=origin, direction=d.normalized() if d.length > 1e-9 else Vector((0, -1, 0)),
                    target=target)

    def _look_vector(self, frame):
        yaw = self.yaw_at(frame) + ch._val(self.head, _ROT, 2, frame)
        pitch = -ch._val(self.head, _ROT, 0, frame)
        return Vector((-math.sin(yaw) * math.cos(pitch), math.cos(yaw) * math.cos(pitch), math.sin(pitch)))

    def shoot(self, frame_start, target, release=None, part=None, **fire_kw):
        """draw(frame_start, release, target) and fire(self, target, release, part=part, **fire_kw): the whole shot.
        Returns the Flight (an int: the impact frame)."""
        d = self.draw(frame_start, release=release, target=target)
        return fire(self, target, d["frame"], part=part, **fire_kw)

    # ------------------------------------------------------------------ the head (the bow arms follow it)
    def _rebake(self, out):
        if any(on for _f, on, _e in self._aggro):
            self._bake_arms()
        return out

    def look_at(self, frame, target, ease=6):
        """Character.look_at; while it aims, the bow arms follow the head."""
        return self._rebake(super().look_at(frame, target, ease=ease))

    def track(self, frame_start, frame_end, target, step=3, ease=6):
        """Character.track; while it aims, the bow arms follow the head."""
        return self._rebake(super().track(frame_start, frame_end, target, step=step, ease=ease))

    def idle(self, frame_start, frame_end, seed=0):
        """Undead.idle (the head looks around); while it aims, the bow arms follow the head."""
        return self._rebake(super().idle(frame_start, frame_end, seed=seed))

    def face(self, frame, target, ease=8, keep_head=False):
        """Character.face (the whole body turns); the arms are rewritten with it."""
        return self._rebake(super().face(frame, target, ease=ease, keep_head=keep_head))

    # ------------------------------------------------------------------ motion and damage
    def walk(self, frame, points, speed=None, run=False, from_current=False, gait="planted", lead=None,
             first_step=None, stride=None):
        """Undead.walk at the skeleton's speed (2.75 blocks/s); the arms swing against the legs unless it aims."""
        f1 = super().walk(frame, points, speed=speed, run=run, from_current=from_current, gait=gait, lead=lead,
                          first_step=first_step, stride=stride)
        self._bake_arms()
        refresh(self)
        return f1

    def place(self, frame, pos, yaw=0.0, keep_pose=False):
        """Hard cut (Undead.place): arms down, not aiming, head straight. A draw running across the cut (or
        loosing ON it) goes on: its arrow is already keyed, so the bow keeps its stage and the arms are up from
        the cut (see _aggro_events); call order does not matter for that."""
        super().place(frame, pos, yaw, keep_pose=keep_pose)
        self._bake_arms()

    def hurt(self, frame, attacker=None, knockback=None, max_back=None, flash=True):
        """undead.hurt (red 12 frames, kicks, hop with an attacker); the arms flail with the legs unless aiming."""
        end = undead.hurt(self, frame, attacker=attacker, knockback=knockback, max_back=max_back, flash=flash)
        self._bake_arms()
        refresh(self)
        return end

    def die(self, frame, camera=None, glow=POOF_GLOW, **kw):
        """undead.die: tips over (keeping its bow pose while it was aiming), gone with the poof on frame + 24."""
        gone = undead.die(self, frame, camera=camera, glow=glow, **kw)
        self._bake_arms()
        refresh(self)
        return gone


def make_skeleton(name, left_handed=False, collection=None):
    """Build the vanilla skeleton with its bow (feet at the origin, facing -Y); left_handed = bow in the left hand."""
    from . import players

    key, sheet = _sheet("entity/skeleton/skeleton")
    spec = _skeleton_spec()
    col = ch._collection(collection)
    parts = ch._build_rig(name, spec, sheet, ch._sheet_material(key, sheet), col)
    unit = spec["scale"] / 16.0
    hands = {}
    for side, pivot in (("r", (-5.0 + HAND_SHIFT, 2.0, 0.0)), ("l", (5.0 - HAND_SHIFT, 2.0, 0.0))):
        e = bpy.data.objects.new("%s_hand_%s" % (name, side), None)  # SkeletonModel.translateToHand
        e.empty_display_size = 0.05
        col.objects.link(e)
        e.parent = parts["body"]
        e.location = (pivot[0] * unit, pivot[2] * unit, -(pivot[1] - 12.0) * unit)
        e.rotation_mode = "XZY"
        hands[side] = e
    side = "l" if left_handed else "r"
    chain = mobs._model_chain("item/bow")
    display = players._display(chain, "thirdperson_lefthand" if left_handed else "thirdperson_righthand",
                               fallback="thirdperson_righthand")
    matrix = players.hand_matrix(display, left=left_handed, scale=spec["scale"], slim=False)
    bows = {}
    for variant in BOW_VARIANTS:
        ob = mc.item_object(variant, collection=col)
        ob.name = "%s_%s" % (name, variant)
        ob.parent = hands[side]
        ob.matrix_parent_inverse = Matrix.Identity(4)
        ob.matrix_basis = matrix
        bows[variant] = ob
    return Skeleton(name, parts, spec, hands, bows, left_handed)


def add_skeleton(st, name="skeleton", **kw):
    """A skeleton registered with a films.lookdev.Stage (st.cast[name])."""
    c = st.cast.get(name)
    if c is None:
        c = st.cast[name] = make_skeleton(name, **kw)
    return c


# ----------------------------------------------------------------------------------------------------
# the arrow
# ----------------------------------------------------------------------------------------------------
ARROW_TEXTURE = "entity/projectiles/arrow"
_W = Matrix(((1, 0, 0), (0, 0, -1), (0, 1, 0)))      # Minecraft (x east, y up, z south) -> Blender (x, -z, y)


def _arrow_mesh():
    """ArrowModel.createBodyLayer as a mesh: model pixels x 0.9 / 16 in Blender axes (tip along +X), only the
    opaque texels of entity/projectiles/arrow.png; the two sides of each zero-thickness quad 0.01 px apart so
    each shows its own half of the texture (the game draws them culled)."""
    name = "hostiles_arrow"
    me = bpy.data.meshes.get(name)
    if me is not None:
        return me
    arr = ch._game_texture(ARROW_TEXTURE)
    th, tw = arr.shape[:2]
    opaque = arr[..., 3] >= ch.ALPHA_CUTOUT
    eps = 0.005
    verts, faces, uvs = [], [], []

    def face(block, origin, eu, ev, normal, xf):
        """Quads over the opaque texels of block (c0, r0, c1, r1); texel (c, r) corner = origin + (c - c0) eu +
        (r - r0) ev in model px, then xf; normal = the face's outward normal before xf."""
        c0, r0, c1, r1 = block
        o, eu, ev = Vector(origin), Vector(eu), Vector(ev)
        nrm = (xf.to_3x3() @ Vector(normal))
        for (a0, b0, a1, b1) in ch._rects(opaque[r0:r1, c0:c1]):
            corners = [(a0, b0), (a1, b0), (a1, b1), (a0, b1)]
            pts = [xf @ (o + eu * a + ev * b) for a, b in corners]
            e = 0.02
            tex = [(c0 + a0 + e, r0 + b0 + e), (c0 + a1 - e, r0 + b0 + e), (c0 + a1 - e, r0 + b1 - e),
                   (c0 + a0 + e, r0 + b1 - e)]
            if (pts[1] - pts[0]).cross(pts[3] - pts[0]).dot(nrm) < 0.0:
                pts.reverse()
                tex.reverse()
            n = len(verts)
            for p in pts:
                q = _W @ (p * ARROW_MODEL_SCALE / 16.0)
                verts.append(tuple(q))
            faces.append((n, n + 1, n + 2, n + 3))
            uvs.extend((u / tw, 1.0 - v / th) for u, v in tex)

    for a in (math.pi / 4.0, 3.0 * math.pi / 4.0):                     # cross_1, cross_2: PartPose.rotation(a, 0, 0)
        xf = Matrix.Rotation(a, 4, "X")
        face((0, 0, 16, 5), (-12.0, -2.0, -eps), (1, 0, 0), (0, 0.8, 0), (0, 0, -1), xf)     # NORTH, rows x 0.8
        face((16, 0, 32, 5), (4.0, -2.0, eps), (-1, 0, 0), (0, 0.8, 0), (0, 0, 1), xf)      # SOUTH (mirrored half)
    xf = Matrix.Translation((-11.0, 0.0, 0.0)) @ Matrix.Rotation(math.pi / 4.0, 4, "X") @ Matrix.Diagonal((0.8, 0.8, 0.8, 1.0))
    face((0, 5, 5, 10), (-eps, -2.5, 2.5), (0, 0, -1), (0, 1, 0), (-1, 0, 0), xf)          # back: WEST
    face((5, 5, 10, 10), (eps, -2.5, -2.5), (0, 0, 1), (0, 1, 0), (1, 0, 0), xf)           # back: EAST
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    layer = me.uv_layers.new(name="UVMap")
    layer.data.foreach_set("uv", [x for uv in uvs for x in uv])
    me.materials.append(mc.material(ARROW_TEXTURE, alpha="OPAQUE"))
    me.update()
    return me


def arrow_object(name="arrow", scale=1.0, collection=None):
    """A bare arrow object (ArrowModel mesh, point along local +X, 0.9 block long at scale 1)."""
    ob = bpy.data.objects.new(name, _arrow_mesh())
    fx._collection(collection).objects.link(ob)
    ob.scale = (scale, scale, scale)
    ob.rotation_mode = "XYZ"
    return ob


def _mc_rot(v):
    """(yRot, xRot) in degrees of a Blender velocity, as Projectile.updateRotation computes them."""
    return (math.degrees(math.atan2(v.x, -v.y)), math.degrees(math.atan2(v.z, math.hypot(v.x, v.y))))


def _lerp_rot(old, new):
    """Projectile.lerpRotation: the short way round, 20 % of it."""
    while new - old < -180.0:
        old -= 360.0
    while new - old >= 180.0:
        old += 360.0
    return old + (new - old) * ARROW_ROT_LERP


def arrow_track(start, velocity, ticks=100):
    """[(point, yRot, xRot)] after 0..ticks ticks of AbstractArrow.tick in the air (no collisions): rotation
    lerped toward the velocity, move, speed x 0.99, 0.05 down. velocity in blocks per tick (Blender axes)."""
    p, v = Vector(start), Vector(velocity)
    yaw, pitch = _mc_rot(v)
    out = [(p.copy(), yaw, pitch)]
    for _k in range(int(ticks)):
        ty, tp = _mc_rot(v)
        pitch, yaw = _lerp_rot(pitch, tp), _lerp_rot(yaw, ty)
        p = p + v
        v = v * ARROW_DRAG
        v.z -= ARROW_GRAVITY
        out.append((p.copy(), yaw, pitch))
    return out


def _euler(yaw, pitch, extra=0.0):
    """rotation_euler of the arrow object for the game's yRot / xRot (degrees) and the shake (degrees)."""
    return (0.0, -math.radians(pitch + extra), math.radians(yaw) - math.pi / 2.0)


def _shake(t_ticks):
    """ArrowModel.setupAnim: the extra root zRot (degrees) shake ticks after a block hit (shake = 7 - t)."""
    s = ARROW_SHAKE_TICKS - t_ticks
    if s <= 0.0:
        return 0.0
    return -math.sin(s * 3.0) * s


def _segment_box(a, b, lo, hi):
    """Fraction (0..1) along a -> b where it enters the box lo..hi, or None."""
    t0, t1 = 0.0, 1.0
    for i in range(3):
        d = b[i] - a[i]
        if abs(d) < 1e-12:
            if a[i] < lo[i] or a[i] > hi[i]:
                return None
            continue
        u0, u1 = (lo[i] - a[i]) / d, (hi[i] - a[i]) / d
        t0, t1 = max(t0, min(u0, u1)), min(t1, max(u0, u1))
        if t0 > t1:
            return None
    return t0


def _box_of(c, frame, margin=ARROW_HIT_MARGIN):
    """The game's hit box of a character at `frame`, grown by `margin` (corners lo, hi)."""
    w, h = getattr(c, "size", None) or undead.body_box(c)
    p = c.pos_at(frame)
    m = w / 2.0 + margin
    return Vector((p.x - m, p.y - m, p.z - margin)), Vector((p.x + m, p.y + m, p.z + h + margin))


def _is_player(c):
    from . import players

    return isinstance(c, players.Player)


def _start_point(start, frame):
    """(origin, default speed) of an arrow loosed by `start` at `frame`."""
    if isinstance(start, Skeleton):
        return start.pos_at(frame) + Vector((0.0, 0.0, SKELETON_EYE - ARROW_SPAWN_DROP)), ARROW_SPEED
    if isinstance(start, ch.Character):
        return start.eye_point(frame) - Vector((0.0, 0.0, ARROW_SPAWN_DROP)), (
            PLAYER_ARROW_SPEED if _is_player(start) else ARROW_SPEED)
    return ch._vec3(start), ARROW_SPEED


def _solve_pitch(origin, point, speed, max_ticks=200):
    """Launch direction (unit Vector) at `speed` whose game path passes through `point` (the lower arc), or None."""
    o, t = Vector(origin), Vector(point)
    flat = Vector((t.x - o.x, t.y - o.y, 0.0))
    reach = flat.length
    if reach < 1e-6:
        return (t - o).normalized() if (t - o).length > 1e-9 else Vector((0.0, -1.0, 0.0))
    ahead = flat / reach
    dz = t.z - o.z

    def err(pitch):
        vh, vz = speed * math.cos(pitch), speed * math.sin(pitch)
        d = z = 0.0
        for _k in range(max_ticks):
            d2, z2 = d + vh, z + vz
            if d2 >= reach:
                u = (reach - d) / max(d2 - d, 1e-12)
                return z + (z2 - z) * u - dz
            d, z = d2, z2
            vh *= ARROW_DRAG
            vz = vz * ARROW_DRAG - ARROW_GRAVITY
            if z < dz - 50.0:
                break
        return None

    prev = None
    for i in range(-170, 171):
        p = math.radians(i * 0.5)
        e = err(p)
        if e is not None and prev is not None and prev[1] is not None and prev[1] < 0.0 <= e:
            lo, hi = prev[0], p
            for _k in range(50):
                mid = 0.5 * (lo + hi)
                em = err(mid)
                if em is None or em < 0.0:
                    lo = mid
                else:
                    hi = mid
            return Vector((ahead.x * math.cos(hi), ahead.y * math.cos(hi), math.sin(hi)))
        prev = (p, e)
    return None


class Flight(int):
    """The impact frame of an arrow, with .arrow .stuck .hit .frames .points .velocity .direction .ticks .target;
    point_at(frame) = where the flying arrow is at a (fractional) frame."""

    def point_at(self, frame):
        """The arrow's position at `frame` (as keyed: linear between the game's ticks)."""
        times, locs = self._keys
        f = float(frame)
        if f <= times[0]:
            return locs[0].copy()
        for i in range(1, len(times)):
            if f <= times[i]:
                u = (f - times[i - 1]) / max(times[i] - times[i - 1], 1e-9)
                return locs[i - 1].lerp(locs[i], u)
        return locs[-1].copy()


def _ticks_to_reach(origin, direction, speed, point):
    """Game ticks (fractional) an arrow launched along `direction` takes to cover the horizontal distance to
    `point` (the horizontal speed only decays: x 0.99 a tick), or None when it never gets there."""
    d = math.hypot(point[0] - origin[0], point[1] - origin[1])
    vh = speed * math.hypot(direction[0], direction[1])
    if vh < 1e-9:
        return None
    q = 1.0 - d * (1.0 - ARROW_DRAG) / vh                        # d(t) = vh (1 - 0.99^t) / 0.01
    if q <= 0.0:
        return None
    return math.log(q) / math.log(ARROW_DRAG)


def _ground_fn(village, plane):
    """ground(x, y) -> the terrain top (village.ground) or the plane z when there is no village / no terrain."""
    if village is None:
        return lambda x, y: plane

    def g(x, y):
        z = village.ground(x, y)
        return plane if z is None else z

    return g


def fire(start, target, frame, speed=None, part=None, camera=None, hurt=True, knockback=None, until=None, aim=None,
         spread=0.0, seed=0, scale=1.0, collection=None, at=None, game_id=None, stick=None, kill=False, max_back=None,
         align=False, lead=True, village=None):
    """Loose an arrow ON `frame` from `start` at `target` (see the module docstring). Returns a Flight."""
    f0 = int(round(frame))
    origin, default_speed = _start_point(start, f0)
    speed = default_speed if speed is None else float(speed)
    is_char = isinstance(target, ch.Character)
    jit = Vector((0.0, 0.0, 0.0))
    if spread:
        rng = np.random.default_rng([int(seed) & 0x7FFFFFFF, f0])
        jit = Vector((rng.random(3) - rng.random(3)) * ARROW_SPREAD * float(spread))   # RandomSource.triangle
    if is_char:
        tp = target.pos_at(f0)
        _w, h = getattr(target, "size", None) or undead.body_box(target)
        if aim == "exact":
            direction = None
        else:                                                    # AbstractSkeleton.performRangedAttack
            dx, dy = tp.x - origin.x, tp.y - origin.y
            dist = math.hypot(dx, dy)
            dz = (tp.z + h * ARROW_AIM_HEIGHT) - origin.z
            direction = Vector((dx, dy, dz + dist * ARROW_AIM_LIFT)).normalized()
        aim_point = tp + Vector((0.0, 0.0, h * 0.62))
    else:
        aim_point = ch._vec3(target)
        direction = None
    if direction is None:
        direction = _solve_pitch(origin, aim_point, speed)
        if direction is None:
            raise ValueError("fire: %.2f blocks per tick does not reach %s" % (speed, tuple(round(c, 2) for c in aim_point)))
    if spread:
        direction = (direction + jit).normalized()

    def simulate(dirn, ground=None):
        """(points, velocity, what): what = 'target', 'ground' (with ground=fn) or None (flew on)."""
        p, v = origin.copy(), dirn * speed
        yaw, pitch = _mc_rot(v)
        pts = [(0.0, p.copy(), yaw, pitch)]
        for k in range(200):
            ty, tpch = _mc_rot(v)
            pitch, yaw = _lerp_rot(pitch, tpch), _lerp_rot(yaw, ty)
            a, b = p, p + v
            if is_char and ground is None:
                lo, hi = _box_of(target, f0 + (k + 0.5) * TICK)
                u = _segment_box(a, b, lo, hi)
                if u is not None:
                    return pts + [(k + u, a.lerp(b, u), yaw, pitch)], v.copy(), "target"
            elif ground is not None:
                ga, gb = ground(a.x, a.y), ground(b.x, b.y)
                if a.z >= ga and b.z < gb:
                    u = (a.z - ga) / max((a.z - ga) - (b.z - gb), 1e-12)
                    return pts + [(k + u, a.lerp(b, u), yaw, pitch)], v.copy(), "ground"
            else:
                seg = b - a
                rel = aim_point - a
                if seg.length > 1e-9:
                    q = ch._clamp(rel.dot(seg) / seg.length_squared, 0.0, 1.0)
                    if (a + seg * q - aim_point).length < 0.05 and (q < 1.0 or (aim_point - b).length < 0.05):
                        return pts + [(k + q, aim_point.copy(), yaw, pitch)], v.copy(), "target"
            p = b
            v = v * ARROW_DRAG
            v.z -= ARROW_GRAVITY
            pts.append((k + 1.0, p.copy(), yaw, pitch))
            if p.z < min(origin.z, aim_point.z) - 30.0:
                break
        return pts, v, None

    first_dir = direction
    pts, vel, what = simulate(direction)
    missed = False
    if what is None and is_char and lead:
        # the target moves: aim where it will be when the arrow gets there (the game's skeleton does not lead;
        # its arrow would miss), a few rounds of time-of-flight -> predicted position -> exact path through it
        t_fly = _ticks_to_reach(origin, direction, speed, aim_point) or 0.0
        for _round in range(6):
            fa = f0 + t_fly * TICK
            pred = target.pos_at(fa) + Vector((0.0, 0.0, h * 0.62))
            dn = _solve_pitch(origin, pred, speed)
            if dn is None:
                break
            dn = (dn + jit).normalized() if spread else dn
            pts, vel, what = simulate(dn)
            if what is not None:
                direction = dn
                _note("fire: %s moves; the arrow is led to where it is on frame %.1f (the game's skeleton aims at "
                      "where it is now and would miss)" % (target.name, fa))
                break
            t_new = _ticks_to_reach(origin, dn, speed, pred)
            if t_new is None or abs(t_new - t_fly) < 1e-3:
                break
            t_fly = t_new
    if what is None and is_char:
        # a real miss: the game's arrow flies on past the target and sticks in the ground
        g = _ground_fn(village, target.pos_at(f0).z)
        direction = first_dir
        pts, vel, what = simulate(direction, ground=g)
        missed = True
        _note("fire: the arrow at %s on frame %d misses: it flies on and %s" % (
            target.name, f0, "sticks in the ground" if what == "ground" else "is lost"))
        if what is None:
            pts.append((pts[-1][0] + 1.0, pts[-1][1] + vel, pts[-1][2], pts[-1][3]))
    if what is None and not is_char:
        raise ValueError("fire: the arrow never reaches its target")
    t_hit = pts[-1][0]
    impact = int(math.ceil(f0 + t_hit * TICK - 1e-6))
    hit_point = pts[-1][1]
    ob = arrow_object("arrow_%d" % f0, scale=scale, collection=collection)
    frames = [f0 + t * TICK for t, _p, _y, _x in pts]
    stuck = None
    rots = [(y, x) for _t, _p, y, x in pts]
    for i in range(1, len(rots)):                                # continuous yaw for the keys
        while rots[i][0] - rots[i - 1][0] > 180.0:
            rots[i] = (rots[i][0] - 360.0, rots[i][1])
        while rots[i][0] - rots[i - 1][0] < -180.0:
            rots[i] = (rots[i][0] + 360.0, rots[i][1])
    locs = [p for _t, p, _y, _x in pts]
    in_body = is_char and not missed
    if not in_body and what is not None:                         # stuck in the block: 0.05 short, shaking
        back = vel.normalized() * ARROW_BLOCK_BACKOFF
        locs[-1] = hit_point - back
        fend = frames[-1]
        yaw, pitch = rots[-1]
        n = int(ARROW_SHAKE_TICKS * TICK * 4)
        for j in range(1, n + 1):
            t = j * 0.25
            frames.append(fend + t)
            locs.append(locs[-1])
            rots.append((yaw, pitch + _shake(t / TICK)))
        stuck = ob
    for i in range(3):
        fx._write(ob, _LOC, i, frames, [p[i] for p in locs], "LINEAR")
    eul = [_euler(y, x) for y, x in rots]
    for i in (1, 2):
        fx._write(ob, _ROT, i, frames, [e[i] for e in eul], "LINEAR")
    vis = [(f0 - 1, True), (f0, False)]
    if in_body or what is None:
        vis.append((impact, True))
    elif until is not None:
        vis.append((int(until), True))
    undead._set_hide(ob, vis)
    out = Flight(impact)
    out.arrow, out.hit, out.frames, out.velocity = ob, hit_point, (f0, impact), vel
    out.points = locs
    out._keys = (list(frames), [Vector(p) for p in locs])
    out.direction = vel.normalized()
    out.ticks = t_hit
    out.target = target
    out.missed = missed
    out.spot = None
    if in_body:
        keep = _is_player(target) if stick is None else bool(stick)  # the game draws stuck arrows on players only
        if keep:
            stuck = hit(target, impact, part=part, at=at, until=until, scale=scale, hurt=hurt and not kill,
                        knockback=knockback, direction=vel, attacker=start, game_id=game_id, max_back=max_back,
                        align=align, auto=part is None and game_id is None)
            out.spot = _book(target)["arrows"][-1]["spot"]
        if kill:
            _arrow_hurt(target, impact, knockback, vel, start, kill=True, camera=camera, max_back=max_back)
        elif hurt and not keep:
            _arrow_hurt(target, impact, knockback, vel, start, max_back=max_back)
    out.stuck = stuck
    return out


def stick(point, direction, frame, until=None, shake=True, scale=1.0, collection=None):
    """An arrow stuck in a block from `frame` on: its entity position 0.05 short of `point` along `direction`
    (the way it flew), the tail shaking for 7 ticks. Returns the object."""
    f0 = int(round(frame))
    d = Vector(direction).normalized()
    yaw, pitch = _mc_rot(d)
    ob = arrow_object("arrow_stuck_%d" % f0, scale=scale, collection=collection)
    p = ch._vec3(point) - d * ARROW_BLOCK_BACKOFF
    ob.location = p
    ob.rotation_euler = _euler(yaw, pitch)
    if shake:
        frames = [f0 + j * 0.25 for j in range(int(ARROW_SHAKE_TICKS * TICK * 4) + 1)]
        eul = [_euler(yaw, pitch, _shake((f - f0) / TICK)) for f in frames]
        fx._write(ob, _ROT, 1, frames, [e[1] for e in eul], "LINEAR")
    vis = [(f0 - 1, True), (f0, False)]
    if until is not None:
        vis.append((int(until), True))
    undead._set_hide(ob, vis)
    return ob


# ----------------------------------------------------------------------------------------------------
# arrows stuck in a character (StuckInBodyLayer, IN_CUBE)
# ----------------------------------------------------------------------------------------------------
SPOTS = {                            # film spots: (part, (f1, f2, f3) in its cube); f3 small = front, large = back
    "chest": ("body", (0.32, 0.28, 0.10)),
    "chest_l": ("body", (0.70, 0.30, 0.10)),
    "belly": ("body", (0.55, 0.70, 0.10)),
    "back": ("body", (0.62, 0.30, 0.90)),
    "back_low": ("body", (0.38, 0.70, 0.90)),
    "shoulder_r": ("arm_r", (0.45, 0.14, 0.18)),
    "shoulder_l": ("arm_l", (0.55, 0.14, 0.18)),
    "head": ("head", (0.70, 0.40, 0.12)),
    "thigh_r": ("leg_r", (0.50, 0.25, 0.15)),
    "thigh_l": ("leg_l", (0.50, 0.25, 0.15)),
}
AUTO_SPOTS = ("chest", "back", "chest_l", "back_low", "belly", "shoulder_r", "shoulder_l")   # fire(part=None) picks


def spot_direction(spot):
    """(right, up, forward) unit vector, in the character's own terms, of the way the shaft of an arrow stuck in
    `spot` (a SPOTS name, or (part, (f1, f2, f3))) sticks OUT of the body: StuckInBodyLayer points the tip along
    -(2 f - 1), whatever way the arrow came from."""
    _part, f = SPOTS[spot] if isinstance(spot, str) else spot
    out = Vector([2.0 * v - 1.0 for v in f])                         # model space: x = its left, y = down, z = back
    out = Vector((-out.x, -out.y, -out.z))
    return out.normalized() if out.length > 1e-9 else Vector((0.0, 0.0, 1.0))


def _spot_world(c, spot, frame):
    """The shaft direction of `spot` in world axes at `frame` (body yaw only; limbs taken as hanging)."""
    r, u, fw = spot_direction(spot)
    yaw = c.yaw_at(frame)
    fwd = Vector((math.sin(yaw), -math.cos(yaw), 0.0))
    right = Vector((fwd.y, -fwd.x, 0.0))                             # facing -Y (yaw 0): right is -X
    return (right * r + fwd * fw + Vector((0.0, 0.0, u))).normalized()


def _auto_spot(c, frame, direction, used):
    """The film's pick for fire(part=None): the spot (AUTO_SPOTS) facing the shooter best that this character
    does not carry yet (when all are taken: the best one again); chest and back are slightly preferred (0.05 a
    place down the AUTO_SPOTS list)."""
    back = -Vector(direction).normalized() if direction is not None and Vector(direction).length > 1e-9 else None
    best = []
    for i, name in enumerate(AUTO_SPOTS):
        score = (_spot_world(c, name, frame).dot(back) if back is not None else 0.0) - 0.05 * i
        best.append((score, name))
    best.sort(reverse=True)
    for _s, name in best:
        if name not in used:
            return name
    _note("fire: every spot of %s already has an arrow: %s again" % (c.name, best[0][1]))
    return best[0][1]


def _world_matrix(ob, frame):
    """ob.matrix_world on `frame` (the scene is set there and back)."""
    scene = bpy.context.scene
    old, sub = scene.frame_current, scene.frame_subframe
    scene.frame_set(int(frame))
    m = ob.matrix_world.copy()
    scene.frame_set(old, subframe=sub)
    return m


def _spec_of(c):
    """The model spec a character was built from (for the cube boxes the game's layer picks from)."""
    s = getattr(c, "spec", None)
    if s is not None:
        return s
    from . import players

    if isinstance(c, players.Player):
        return players._player_spec(c.slim)
    if isinstance(c, undead.Undead):
        if c.kind == "zombie_villager":
            return undead._baby_zombie_villager_spec() if c.baby else undead._zombie_villager_spec()
        if c.baby:
            return undead._baby_zombie_spec()
        return undead._zombie_spec(undead.HUSK_SCALE if c.variant == "husk" else 1.0)
    if c.kind == "villager":
        return ch._baby_villager_spec() if c.child else ch._villager_spec()
    if c.kind == "player":
        return ch._player_spec()
    return None


def _part_name(c, part):
    """The rig part (object name key) holding the game's part `part` for this character."""
    if part == "body" and "torso" in c.parts:
        return "torso"
    if part in ("arm_r", "arm_l") and part not in c.parts and "arms" in c.parts:
        return "arms"
    if part not in c.parts:
        raise ValueError("%s has no part %r (parts: %s)" % (c.name, part, ", ".join(sorted(c.parts))))
    return part


def _part_box(c, name):
    """(lo, hi) of the FIRST cube of a rig part in model px relative to the part's pivot (its object origin)."""
    spec = _spec_of(c)
    if spec is not None:
        for part in spec["parts"]:
            if part["name"] != name:
                continue
            for chain, cubes in part["groups"]:
                if not cubes:
                    continue
                m = Matrix.Identity(4)
                for pose in chain:
                    m = m @ ch._pose_matrix(pose)
                cb = cubes[0]
                (x, y, z), (w, h, d) = cb["pos"], cb["size"]
                pts = [m @ Vector((x + i * w, y + j * h, z + k * d)) for i in (0, 1) for j in (0, 1) for k in (0, 1)]
                lo = Vector([min(p[i] for p in pts) for i in range(3)])
                hi = Vector([max(p[i] for p in pts) for i in range(3)])
                return lo, hi
    ob = c.parts[name]                                               # fallback: the mesh's bounding box
    unit = c.unit
    corners = [Vector(v) for v in ob.bound_box]
    model = [Vector((p.x, -p.z, p.y)) / unit for p in corners]       # Blender local (x, z, -y) * unit -> model
    lo = Vector([min(p[i] for p in model) for i in range(3)])
    hi = Vector([max(p[i] for p in model) for i in range(3)])
    return lo, hi


def stuck_matrix(c, part, f, scale=1.0, tip=None):
    """(part object, matrix_basis) of an arrow stuck at (f1, f2, f3) in the cube of `part` of character c, exactly
    as StuckInBodyLayer.submit / submitStuckItem place it (IN_CUBE): point = lerp(f, cube min, max), the arrow's
    point along -(2 f - 1), the model's own scale (0.9375 for a player). tip = another direction for the point
    (model space: x = its left, y = down, z = its back), e.g. along the flight (hit(align=True))."""
    name = _part_name(c, part)
    lo, hi = _part_box(c, name)
    p = Vector([lo[i] + (hi[i] - lo[i]) * f[i] for i in range(3)])
    d = Vector([-(2.0 * f[i] - 1.0) for i in range(3)]) if tip is None else Vector(tip)
    h = math.hypot(d.x, d.z)
    yaw = math.atan2(d.x, d.z)
    pitch = math.atan2(d.y, h)
    rm = Matrix.Rotation(yaw - math.pi / 2.0, 3, "Y") @ Matrix.Rotation(pitch, 3, "Z")   # PoseStack YP, ZP
    A = ch._AXES.to_3x3()
    rot = A @ rm @ _W.inverted()
    unit = c.unit
    loc = (A @ p) * unit
    m = Matrix.Translation(loc) @ (rot * (c.model_scale * float(scale))).to_4x4()
    return c.parts[name], m


def hit(character, frame, part="chest", at=None, until=None, scale=1.0, hurt=True, knockback=None, direction=None,
        attacker=None, game_id=None, index=None, max_back=None, align=False, auto=False):
    """An arrow stuck in `character` from `frame` on, riding its body part (see the module docstring). Returns
    the arrow object."""
    c = character
    f0 = int(round(frame))
    st = _book(c)
    spot = part if isinstance(part, str) else None
    if auto:                                                     # fire(part=None): a free spot facing the shooter
        part = spot = _auto_spot(c, f0, direction, {a.get("spot") for a in st["arrows"]})
    if game_id is not None or part is None:
        n = len(st["arrows"]) if index is None else int(index)
        gid = int(game_id if game_id is not None else 1 + (sum(ord(ch_) for ch_ in c.name) % 997))
        part, f = game_arrow_spot(gid, n)
        spot = None
    elif at is not None:
        f = tuple(float(v) for v in at)
        spot = None
    elif part in SPOTS:
        part, f = SPOTS[part]
    else:
        f = (0.5, 0.3, 0.1)
        spot = None
    tip = None
    host = c.parts[_part_name(c, part)]
    if align and direction is not None and Vector(direction).length > 1e-9:
        # the shaft back along the flight (a film option; the game ignores where the arrow came from)
        m3 = _world_matrix(host, f0).to_3x3().normalized()
        local = m3.inverted() @ Vector(direction).normalized()
        tip = ch._AXES.to_3x3().transposed() @ local                     # Blender local -> model space
    host, m = stuck_matrix(c, part, f, scale, tip=tip)
    unit = c.unit
    for other in st["arrows"]:
        ob2 = other["object"]
        if ob2.parent is host and (ob2.matrix_basis.translation - m.translation).length < 0.5 * unit * c.model_scale \
                and (other["until"] is None or other["until"] > f0):
            _note("hit(%s, %d): this arrow is within half a pixel of %s (same spot %r): it will look like ONE arrow;"
                  " give another part= / at=" % (c.name, f0, ob2.name, spot or part))
    if spot is not None and direction is not None and not align and Vector(direction).length > 1e-9:
        facing = _spot_world(c, spot, f0).dot(-Vector(direction).normalized())
        if facing < -0.2:
            _note("hit(%s, %d): spot %r faces away from the shooter (the shaft points %.0f degrees off the way the "
                  "arrow came): choose a spot on the shooter's side, part=None, or align=True" % (
                      c.name, f0, spot, math.degrees(math.acos(ch._clamp(facing, -1.0, 1.0)))))
    ob = bpy.data.objects.new("%s_arrow%d" % (c.name, len(st["arrows"]) + 1), _arrow_mesh())
    col = c.root.users_collection[0] if c.root.users_collection else ch._collection(None)
    col.objects.link(ob)
    ob.parent = host
    ob.matrix_parent_inverse = Matrix.Identity(4)
    ob.matrix_basis = m
    st["arrows"].append(dict(object=ob, frame=f0, part=part, at=f, until=until, spot=spot))
    end = None if until is None else int(until)
    _follow(c, ob, lambda fr: fr >= f0 and (end is None or fr < end), (f0,) + (() if end is None else (end,)))
    if hurt:
        _arrow_hurt(c, f0, knockback, direction, attacker, max_back=max_back)
    return ob


def _arrow_hurt(c, frame, knockback=None, direction=None, attacker=None, kill=False, camera=None, max_back=None):
    """The hit of an arrow: red flash and the knock-back along the arrow's motion (LivingEntity.hurtServer ->
    knockback(0.4) for a projectile: Projectile.calculateHorizontalHurtKnockbackDirection); kill=True: the
    killing arrow (die with the same push). max_back = at most this far back (undead.hurt's wall; not players)."""
    f0 = int(round(frame))
    if max_back is not None and _is_player(c):
        _note("max_back is not available for a player (players.Player.hurt): use knockback= (0.1 = half a step)")
    k = ARROW_KNOCKBACK if knockback is None else float(knockback)
    here = c.pos_at(f0)
    if direction is not None:
        dv = Vector((direction[0], direction[1], 0.0))
    elif attacker is not None:
        src = attacker.pos_at(f0) if isinstance(attacker, ch.Character) else ch._vec3(attacker)
        dv = Vector((here.x - src.x, here.y - src.y, 0.0))
    else:
        dv = Vector((0.0, 0.0, 0.0))
    if dv.length > 1e-6:
        src = here - dv.normalized()                              # knock-back along the arrow's motion
    else:
        src, k = None, 0.0
    kb = k / undead.KNOCKBACK if src is not None else False
    if kill:
        if _is_player(c):
            c.die(f0, from_point=src, knockback=k, camera=camera)
        elif isinstance(c, (Creeper, Skeleton)):
            c.die(f0, camera=camera, attacker=src, knockback=kb, max_back=max_back)
        else:
            undead.die(c, f0, camera=camera, attacker=src, knockback=kb, max_back=max_back, glow=POOF_GLOW)
    elif _is_player(c):
        c.hurt(f0, from_point=src, knockback=k)
    elif isinstance(c, (Creeper, Skeleton)):
        c.hurt(f0, attacker=src, knockback=kb, max_back=max_back)
    else:
        undead.hurt(c, f0, attacker=src, knockback=kb, max_back=max_back)
    refresh(c)


# ----------------------------------------------------------------------------------------------------
# the explosion
# ----------------------------------------------------------------------------------------------------
def _resistance_fn(village, centre):
    """resistance(cell) -> None (air) or the block's blast resistance; below the terrain surface it is dirt."""
    world = village.world if village is not None else None
    ground = math.floor(centre.z + 1e-6)

    def res(cell):
        if world is not None:
            got = world.get(*cell)
            if got is not None:
                return RESISTANCE.get(got[0], 3.0)
            g = village.ground(cell[0] + 0.5, cell[1] + 0.5)
            if g is not None and cell[2] < math.floor(g + 1e-6):
                return RESISTANCE["dirt"]
            return None
        return RESISTANCE["dirt"] if cell[2] < ground else None

    return res


def explosion_blocks(centre, radius=EXPLOSION_RADIUS, village=None, seed=0):
    """The number of block positions the explosion's rays reach (ServerExplosion.calculateExplodedPositions: the
    packet's blockCount, AIR INCLUDED). centre = the explosion's centre (a creeper's feet)."""
    c = Vector(centre)
    res = _resistance_fn(village, c)
    rng = np.random.default_rng([int(seed) & 0x7FFFFFFF, 3301])
    found = set()
    for i in range(16):
        for j in range(16):
            for k in range(16):
                if not (i in (0, 15) or j in (0, 15) or k in (0, 15)):
                    continue
                d = Vector((i / 15.0 * 2.0 - 1.0, j / 15.0 * 2.0 - 1.0, k / 15.0 * 2.0 - 1.0)).normalized()
                f = radius * (0.7 + float(rng.random()) * 0.6)
                p = c.copy()
                while f > 0.0:
                    cell = (int(math.floor(p.x)), int(math.floor(p.y)), int(math.floor(p.z)))
                    r = res(cell)
                    if r is not None:
                        f -= (r + 0.3) * 0.3
                    if f > 0.0:
                        found.add(cell)
                    p += d * 0.30000001192092896
                    f -= 0.22500001
    return len(found)


def blast_push(centre, c, frame, radius=EXPLOSION_RADIUS):
    """dict(impact, direction, distance) of ServerExplosion.hurtEntities for character c (exposure taken as 1),
    or None when it is farther than 2 r."""
    p = c.pos_at(frame)
    dist = (p - Vector(centre)).length / (2.0 * radius)
    if dist > 1.0:
        return None
    eye = c.eye_point(frame)
    d = eye - Vector(centre)
    d = d.normalized() if d.length > 1e-9 else Vector((0.0, 0.0, 1.0))
    return dict(impact=(1.0 - dist), direction=d, distance=dist * 2.0 * radius)


def explosion(centre, frame, camera=None, radius=EXPLOSION_RADIUS, village=None, blocks=None, griefing=True, seed=0,
              glow=None, smoke_glow=None, collection=None, latency=False):
    """The particles of an explosion at `centre` on `frame` (see the module docstring). Returns an fx.Burst with
    .blocks (the block count used). latency=True: the first particles one tick (1.2 frames) after `frame`, as the
    client spawns them on its next particle tick; False (default): on `frame` itself, so that no film frame shows
    neither the creeper nor the blast."""
    f0 = int(round(frame))
    c = Vector(centre)
    n_blocks = explosion_blocks(c, radius, village, seed) if blocks is None else int(blocks)
    burst = fx.Burst("explosion", f0)
    burst.blocks = n_blocks
    cams = fx._camera_arg(camera)
    col = fx._collection(collection)
    glow = 1.0 if glow is None else float(glow)
    smoke_glow = POOF_GLOW if smoke_glow is None else float(smoke_glow)
    rng = np.random.default_rng([int(seed) & 0x7FFFFFFF, 4409, f0])
    big = radius >= 2.0 and griefing                                 # ServerExplosion.isSmall
    first = f0 + (TICK if latency else 0.0)                          # the game: spawned on the next particle tick
    puffs = []
    if big:                                                          # HugeExplosionSeedParticle: 8 ticks x 6
        for age in range(EMITTER_TICKS):
            for _i in range(EMITTER_PER_TICK):
                p = c + Vector([(rng.random() - rng.random()) * EMITTER_SPREAD for _a in range(3)])
                puffs.append((first + age * TICK, p, age / float(EMITTER_TICKS)))
    else:
        puffs.append((first, c.copy(), 1.0))
    for k, (spawn, p, xa) in enumerate(puffs):                        # HugeExplosionParticle
        life = 6 + int(rng.integers(0, 4))
        grey = undead._grey(float(rng.random()) * 0.6 + 0.4)
        quad = 2.0 * (1.0 - xa * 0.5)
        undead._sprite_particle(burst, "hostiles_boom_%d_%d" % (f0, k), EXPLOSION_SPRITES, grey, glow,
                                [tuple(p)] * life, spawn, quad, cams, col)
    res = _resistance_fn(village, c)
    solids = fx._Solids(village) if village is not None else mobs._Floor(math.floor(c.z + 1e-6))
    count = min(n_blocks, BLOCK_PARTICLES_MAX)
    made = 0
    for k in range(count):                                           # ClientExplosionTracker.addParticle
        d = Vector([rng.random() * 2.0 - 1.0 for _a in range(3)])
        if d.length < 1e-9:
            continue
        d.normalize()
        dist = float(rng.random()) ** (1.0 / 3.0) * radius
        at = c + d * dist
        if res((int(math.floor(at.x)), int(math.floor(at.y)), int(math.floor(at.z)))) is not None:
            continue                                                 # only where there is air
        speed = 0.5 / (dist / radius + 0.1) * float(rng.random()) * float(rng.random()) + 0.3
        poof = rng.random() < 0.5
        p = c + d * dist * (0.5 if poof else 1.0)
        va = d * speed
        if poof:                                                     # ExplodeParticle
            v = np.array(va) + (rng.random(3) * 2.0 - 1.0) * 0.05
            grey = undead._grey(float(rng.random()) * 0.3 + 0.7)
            quad = 0.1 * (float(rng.random()) * float(rng.random()) * 6.0 + 1.0)
            life = int(16.0 / (float(rng.random()) * 0.8 + 0.2)) + 2
            path = fx._simulate(np.array(p), v, life, -0.1 * 0.04, 0.9, solids, 0.2, rng)
            g = smoke_glow
        else:                                                        # SmokeParticle (BaseAshSmokeParticle)
            v = fx._base_velocity(rng, (0.0, 0.0, 0.0)) * 0.1 + np.array(va)
            grey = undead._grey(float(rng.random()) * 0.3)
            quad = 0.1 * (float(rng.random()) * 0.5 + 0.5) * 2.0 * 0.75
            life = max(1, int(8.0 / (float(rng.random()) * 0.8 + 0.2)))
            path = fx._simulate(np.array(p), v, life, -0.1 * 0.04, 0.96, solids, 0.1, rng)
            g = smoke_glow
        undead._sprite_particle(burst, "hostiles_blast_%d_%d" % (f0, k), GENERIC_SPRITES, grey, g, path, first, quad,
                                cams, col)
        made += 1
    burst.block_particles = made
    for ob in burst.objects:
        ob.shadow_terminator_geometry_offset = 0.0
    return burst


# ----------------------------------------------------------------------------------------------------
# self-test
# ----------------------------------------------------------------------------------------------------
def _check():
    """Numeric checks of the models, timings and keys (no rendering). Returns True when all pass."""
    from . import players

    fails = []

    def expect(label, cond, detail=""):
        print("%-4s %s%s" % ("ok" if cond else "FAIL", label, ("  [%s]" % detail) if detail else ""))
        if not cond:
            fails.append(label)

    def near(a, b, tol):
        return abs(a - b) <= tol

    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.frame_start, scene.frame_end = 1, 400
    cam = bpy.data.objects.new("check_cam", bpy.data.cameras.new("check_cam"))
    scene.collection.objects.link(cam)
    scene.camera = cam

    def at(ob, f):
        scene.frame_set(int(f), subframe=float(f) - int(f))
        return ob.matrix_world.copy()

    # ---- the creeper
    cr = make_creeper("cr")
    cr.place(1, (0.0, 0.0, 0.0), 0.0)
    scene.frame_set(1)
    tops = [max((ob.matrix_world @ Vector(v)).z for v in ob.bound_box) for ob in cr.objects() if ob.type == "MESH"]
    expect("creeper height 26 px = 1.625", near(max(tops), 1.625, 1e-4), "%.4f" % max(tops))
    xs = [(ob.matrix_world @ Vector(v)).x for ob in cr.objects() if ob.type == "MESH" for v in ob.bound_box]
    ys = [(ob.matrix_world @ Vector(v)).y for ob in cr.objects() if ob.type == "MESH" for v in ob.bound_box]
    expect("creeper 8 px wide (0.5), 12 px nose to tail (legs at +-6 px)", near(max(xs) - min(xs), 0.5, 1e-3)
           and near(max(ys) - min(ys), 0.75, 1e-3), "%.3f x %.3f" % (max(xs) - min(xs), max(ys) - min(ys)))
    boom = cr.fuse(10)
    expect("full fuse: explodes 29 ticks after the first swell tick (frame 10 + 35)", boom == 45, str(boom))
    expect("swelling 0 at the start, 1.0 after 28 ticks (33.6 frames), 28.75 / 28 at frame 44.5",
           near(cr.swelling_at(10), 0, 1e-9) and near(cr.swelling_at(10 + 28 * TICK), 1.0, 1e-6)
           and near(cr.swelling_at(44.5), 28.75 / 28.0, 1e-6), "%.4f" % cr.swelling_at(44.5))
    flashes = [f for f in range(10, 46) if white_level(cr.swelling_at(f))]
    runs = []
    for f in flashes:
        if runs and f == runs[-1][1] + 1:
            runs[-1][1] = f
        else:
            runs.append([f, f])
    expect("five white flashes while it swells (s in 0.1-0.2, 0.3-0.4, ... 0.9-1.0)", len(runs) == 5,
           " ".join("%d-%d" % tuple(r) for r in runs))
    levels = [round(cr.white_at(r[0]), 3) for r in runs]
    expect("the flashes get whiter: 35 % -> 65-70 % white", levels[0] < 0.36 and levels[-1] > 0.6, str(levels))
    sxz, sy = swell_scale(1.0)
    expect("full swell: 1.4 x wide, 1.1 x tall (with the wobble)", near(sxz / (1 + math.sin(100) * 0.01), 1.4, 1e-6)
           and near(sy * (1 + math.sin(100) * 0.01), 1.1, 1e-6), "%.4f %.4f" % (sxz, sy))
    m = at(cr.swell, 43.5)
    want = swell_scale(cr.swelling_at(43.5))
    expect("the swell empty carries CreeperRenderer.scale (frame 43.5)", near(m.to_scale().x, want[0], 1e-5)
           and near(m.to_scale().z, want[1], 1e-5), "%.4f %.4f" % (m.to_scale().x, m.to_scale().z))
    shells = sum(len(v) for v in cr._shells.values())
    expect("white shells built for the levels used, 6 parts each", shells == 6 * len(cr._shells) and len(cr._shells) >= 4,
           "%d levels" % len(cr._shells))
    vis = []
    for f in range(10, 46):
        scene.frame_set(f)
        if any(not o.hide_render for obs in cr._shells.values() for o in obs):
            vis.append(f)
    expect("a shell is rendered on exactly the white frames", vis == flashes, "%s vs %s" % (vis[:6], flashes[:6]))
    cr2 = make_creeper("cr2")
    cr2.place(1, (3.0, 0.0, 0.0), 0.0)
    back = cr2.fuse(10, 22)
    expect("aborted fuse: shrinks back at the same rate (back to 0 on frame 34)", back == 34 and near(cr2.swelling_at(34), 0.0, 1e-9)
           and near(cr2.swelling_at(22), 10.0 / 28.0, 1e-6), "%d %.4f" % (back, cr2.swelling_at(22)))
    end = cr2.walk(40, [(3.0, 0.0, 0.0), (3.0, -6.0, 0.0)])
    lw = cr2.last_walk
    expect("walk: 2.75 blocks/s, legs +-44 degrees, a cycle every 2.36 blocks", near(lw["speed"], 2.753, 0.06)
           and near(math.degrees(lw["swing"]), 44.2, 1.0) and near(lw["cycle_blocks"], 2.358, 0.01),
           "%.2f b/s %.1f deg %.3f blocks" % (lw["speed"], math.degrees(lw["swing"]), lw["cycle_blocks"]))
    f = 40 + (end - 40) // 2
    lr, ll = ch._val(cr2.leg_r, _ROT, 0, f), ch._val(cr2.leg_l, _ROT, 0, f)
    fr, fl = ch._val(cr2.leg_fr, _ROT, 0, f), ch._val(cr2.leg_fl, _ROT, 0, f)
    expect("diagonal pairs move together (right hind = left front, left hind = right front)", near(lr, fl, 1e-6)
           and near(ll, fr, 1e-6) and near(lr, -ll, 1e-6) and abs(lr) > 0.05, "%.3f %.3f %.3f %.3f" % (lr, ll, fr, fl))
    cr3 = make_creeper("cr3")
    cr3.place(1, (6.0, 0.0, 0.0), 0.0)
    cr3.fuse(10)
    cr3.hurt(20)
    gone = cr3.die(32)
    expect("dying creeper: gone on frame + 24, its swell frozen from the killing blow",
           gone == 56 and near(cr3.swelling_at(50), cr3.swelling_at(32), 1e-9), "%d" % gone)
    expect("no white while it is red (hurt or dying)", cr3.white_at(21) == 0.0 and cr3.white_at(40) == 0.0)
    scene.frame_set(25)
    expect("red frame: no white shell rendered", all(o.hide_render for obs in cr3._shells.values() for o in obs))
    scene.frame_set(60)
    expect("after the death: nothing of it rendered", all(o.hide_render for o in cr3.objects() if o.type == "MESH")
           and all(o.hide_render for obs in cr3._shells.values() for o in obs))

    # ---- the skeleton
    sk = make_skeleton("sk")
    sk.place(1, (0.0, 6.0, 0.0), math.pi)
    scene.frame_set(1)
    tops = [max((ob.matrix_world @ Vector(v)).z for v in ob.bound_box) for ob in sk.objects() if ob.type == "MESH" and len(ob.data.polygons)]
    expect("skeleton 32 px = 2.0 tall", near(max(tops), 2.0, 1e-4), "%.4f" % max(tops))
    target = Vector((0.0, 0.0, 1.0))
    d = sk.draw(20, target=target)
    expect("draw: released 20 ticks = 24 frames later", d["frame"] == 44, str(d["frame"]))
    stages = [sk.bow_at(f) for f in range(18, 47)]
    expect("bow models: bow, pulling_0 (16 frames), pulling_1 (from 13 ticks), pulling_2 (from 18 ticks), bow",
           sk.bow_at(19) == "bow" and sk.bow_at(20) == "bow_pulling_0" and sk.bow_at(35) == "bow_pulling_0"
           and sk.bow_at(36) == "bow_pulling_1" and sk.bow_at(41) == "bow_pulling_1" and sk.bow_at(42) == "bow_pulling_2"
           and sk.bow_at(43) == "bow_pulling_2" and sk.bow_at(44) == "bow", " ".join(s[-1] if s != "bow" else "b" for s in stages))
    scene.frame_set(38)
    shown = [k for k, o in sk.bows.items() if not o.hide_render]
    expect("exactly one bow model rendered (frame 38: pulling_1)", shown == ["bow_pulling_1"], str(shown))
    hx = ch._val(sk.head, _ROT, 0, 40)
    expect("bow pose: both arms at -90 degrees + head pitch (bob aside)",
           near(sk._arm_values(40)[0], -math.pi / 2 + hx, 1e-6) and near(sk._arm_values(40)[2], -math.pi / 2 + hx, 1e-6),
           "%.3f" % sk._arm_values(40)[0])
    expect("bow arm turned 0.1 rad in, the other 0.5 (HumanoidModel.poseRightArm)",
           near(sk._arm_values(40)[1] - ch._val(sk.head, _ROT, 2, 40), 0.1, 1e-6)
           and near(sk._arm_values(40)[3] - ch._val(sk.head, _ROT, 2, 40), -0.5, 1e-6))
    mh, ma = at(sk.hands["r"], 40), at(sk.arm_r, 40)
    expect("the bow hand turns with the arm, its pivot 1 px nearer the body", (mh.to_quaternion().rotation_difference(
        ma.to_quaternion()).angle < 1e-4) and near((mh.translation - ma.translation).length, 1.0 / 16.0, 1e-4))
    skl = make_skeleton("skl", left_handed=True)
    skl.place(1, (3.0, 6.0, 0.0), math.pi)
    skl.draw(20, target=target)
    vr = skl._arm_values(40)
    hz = ch._val(skl.head, _ROT, 2, 40)
    expect("left-handed skeleton: the bow in the left hand, the pose mirrored (left 0.1 in, right 0.5)",
           skl.bows["bow"].parent is skl.hands["l"] and near(vr[3] - hz, -0.1, 1e-6) and near(vr[1] - hz, 0.5, 1e-6)
           and skl.bow_at(42) == "bow_pulling_2", "%.3f %.3f" % (vr[1] - hz, vr[3] - hz))
    sk.lower(60)
    expect("lower: arms back down", near(sk.aiming_at(70), 0.0, 1e-9) and abs(sk._arm_values(70)[0]) < 1e-6)
    e = sk.walk(80, [(0.0, 6.0, 0.0), (0.0, 12.0, 0.0)])
    mid = 80 + (e - 80) // 2
    expect("walking (not aiming): arms swing against the legs, arm = -leg / 1.4",
           near(sk._arm_values(mid)[0], -ch._val(sk.leg_r, _ROT, 0, mid) / 1.4, 1e-6) and abs(sk._arm_values(mid)[0]) > 0.05)

    # ---- arrows in flight
    tr = arrow_track((0.0, 0.0, 1.64), (0.0, -ARROW_SPEED, 0.0), 10)
    expect("arrow: 1.6 blocks the first tick, x 0.99 and 0.05 down per tick after", near((tr[1][0] - tr[0][0]).length, 1.6, 1e-6)
           and near(tr[2][0].y - tr[1][0].y, -1.6 * 0.99, 1e-6) and near(tr[2][0].z - tr[1][0].z, -0.05, 1e-6))
    expect("a flat shot drops 0.05 x 45 = 2.2 blocks... in 10 ticks: %.3f" % (1.64 - tr[10][0].z), near(1.64 - tr[10][0].z, sum(
        sum(0.05 * 0.99 ** j for j in range(k)) for k in range(10)), 1e-6))
    expect("the arrow turns only 20 % a tick toward its motion (tick 1 pitch 0 -> -0.36 deg)",
           near(tr[2][2], 0.2 * math.degrees(math.atan2(-0.05, 1.6 * 0.99)), 1e-6), "%.3f" % tr[2][2])
    steve = players.make_player("steve_t", "steve")
    steve.place(1, (0.0, 0.0, 0.0), math.pi)
    sk2 = make_skeleton("sk2")
    sk2.place(1, (0.0, 8.0, 0.0), math.pi)
    fl = sk2.shoot(100, steve, part="chest", knockback=0.0)
    expect("skeleton shot at 8 blocks: released 24 frames after the draw, hits ~4 frames later", fl.frames[0] == 124
           and 3 <= fl - 124 <= 6, "%s" % (fl.frames,))
    expect("the flying arrow vanishes on the impact frame, the stuck one appears", (lambda: (scene.frame_set(int(fl)), (
        fl.arrow.hide_render and not fl.stuck.hide_render))[1])())
    scene.frame_set(int(fl) - 1)
    expect("... and not before", not fl.arrow.hide_render and fl.stuck.hide_render)
    torso = steve.parts["torso"]
    m0 = at(fl.stuck, int(fl) + 1).copy()
    t0 = at(torso, int(fl) + 1).copy()
    steve.walk(140, [(0.0, 0.0, 0.0), (4.0, 0.0, 0.0)])
    steve.sneak(160)
    for f in (150, 165):
        mt = at(torso, f)
        ma = at(fl.stuck, f)
        rel0, rel1 = t0.inverted() @ m0, mt.inverted() @ ma
        expect("stuck arrow rides the torso (frame %d): same place relative to it" % f,
               (rel0.translation - rel1.translation).length < 1e-5)
    lo, hi = _part_box(steve, "torso")
    expect("player body cube for the arrow: 8 x 12 x 4 px", near(hi.x - lo.x, 8, 1e-6) and near(hi.y - lo.y, 12, 1e-6)
           and near(hi.z - lo.z, 4, 1e-6))
    sp = game_arrow_spot(42, 0)
    expect("the game's spot for entity 42, arrow 0: one of the six parts, inside its cube", sp[0] in PLAYER_ARROW_PARTS
           and all(0.0 <= v < 1.0 for v in sp[1]), str(sp))
    # reference: java.util.Random (JDK 21; the same LCG, seed scramble, nextInt(bound) and nextFloat as the game's
    # SingleThreadedRandomSource / BitRandomSource) with the layer's call sequence nextInt(6), nextInt(1), 3 x nextFloat
    ref = {1: [(3, (0.4100808, 0.4074398, 0.2077148)), (4, (0.6588672, 0.9677559, 0.7107396))],
           42: [(2, (0.6832234, 0.0479393, 0.3087194)), (1, (0.7077106, 0.6655489, 0.0913246))],
           98765: [(5, (0.5596295, 0.4030691, 0.0502020)), (5, (0.0766267, 0.8811804, 0.3261892))]}
    good = all(game_arrow_spot(gid, i)[0] == PLAYER_ARROW_PARTS[pi] and all(near(a, b, 1e-6) for a, b in
               zip(game_arrow_spot(gid, i)[1], fs)) for gid, rows in ref.items() for i, (pi, fs) in enumerate(rows))
    expect("game_arrow_spot = java.util.Random's sequence for ids 1, 42, 98765 (arrows 0 and 1)", good)
    expect("JavaRandom(42): nextInt() -1170105035, nextFloat() 0.7275637 (java.util.Random)",
           JavaRandom(42).next(32) == -1170105035 and near(JavaRandom(42).next_float(), 0.7275637, 1e-7))
    expect("stuck arrows: the game removes 2 after 560 + 580 ticks", stuck_arrow_lifetime(2) == [672, 1368],
           str(stuck_arrow_lifetime(2)))
    fl2 = fire((0.0, 20.0, 1.6), (2.0, 14.0, 0.0), 200)
    expect("arrow into the ground: stops 0.05 short of the point, stays", (fl2.points[-1] - Vector((2.0, 14.0, 0.0))).length < 0.06
           and fl2.stuck is fl2.arrow)
    # ---- explosion
    nb = explosion_blocks(Vector((0.0, 0.0, 0.0)), 3.0)
    expect("creeper on open flat ground: the rays reach 150-350 positions (air included)", 150 <= nb <= 350, str(nb))
    steve2 = players.make_player("steve_b", "steve")
    steve2.place(1, (2.0, 0.0, 0.0), 0.0)
    info = blast_push(Vector((0.0, 0.0, 0.0)), steve2, 1)
    expect("a player 2 blocks from a creeper is pushed 0.67 blocks/tick", near(info["impact"], 1.0 - 2.0 / 6.0, 1e-6))
    # ---- arrows on other characters; the game's rule for mobs; a killing arrow
    vil = ch.make_villager("vil", "farmer")
    vil.place(1, (8.0, 0.0, 0.0), 0.0)
    va = hit(vil, 5, "chest", hurt=False)
    vs = hit(vil, 5, "shoulder_r", hurt=False)
    m0, b0 = at(va, 6).copy(), at(vil.body, 6).copy()
    vil.walk(10, [(8.0, 0.0, 0.0), (8.0, -4.0, 0.0)])
    m1, b1 = at(va, 20).copy(), at(vil.body, 20).copy()
    expect("arrows stick in a villager too (body, and the crossed arms for a shoulder) and ride the body",
           vs.parent is vil.parts["arms"] and ((b0.inverted() @ m0).translation - (b1.inverted() @ m1).translation).length < 1e-5)
    zb = undead.make_zombie("zb")
    zb.place(1, (10.0, 0.0, 0.0), 0.0)
    za = hit(zb, 5, "back", hurt=False)
    expect("... and in a zombie (its own model's body cube)", za.parent is zb.body)
    cr4 = make_creeper("cr4")
    cr4.place(1, (0.0, -12.0, 0.0), 0.0)
    sk3 = make_skeleton("sk3")
    sk3.place(1, (0.0, -4.0, 0.0), 0.0)
    f1 = sk3.shoot(10, cr4)
    c4 = cr4.__dict__[_BOOK]
    expect("an arrow into a creeper: no arrow stays (players only), the creeper flashes red on the impact",
           f1.stuck is None and not c4["arrows"] and undead._flashing(cr4.__dict__[undead._STATE], int(f1)))
    f2 = sk3.shoot(int(f1) + 26, cr4, kill=True)
    gone4 = [d["gone"] for d in cr4.__dict__[undead._STATE]["deaths"]]
    expect("kill=True: the second arrow kills it (gone 24 frames after the impact)", gone4 == [int(f2) + 24], str(gone4))
    # ---- review fixes: a draw across a cut, moving targets, auto spots, align, max_back, step, explosion latency
    for order in ("place first", "draw first"):
        skc = make_skeleton("skc_" + order.split()[0])
        skc.place(1, (30.0, 8.0, 0.0), math.pi)
        tgt = Vector((30.0, 0.0, 1.0))
        if order == "place first":
            skc.place(101, (30.0, 8.0, 0.0), math.pi)
            skc.draw(77, target=tgt)
        else:
            skc.draw(77, target=tgt)
            skc.place(101, (30.0, 8.0, 0.0), math.pi)
        skc.draw(102, target=tgt)
        expect("a draw loosing ON a cut (%s): arms up on the cut and after, bow stages go on" % order,
               all(near(skc.aiming_at(f), 1.0, 1e-9) for f in range(100, 106)) and skc.bow_at(100) == "bow_pulling_2"
               and skc.bow_at(101) == "bow" and skc.bow_at(102) == "bow_pulling_0",
               " ".join("%.2f" % skc.aiming_at(f) for f in range(100, 106)))
    skd = make_skeleton("skd")
    skd.place(1, (34.0, 8.0, 0.0), math.pi)
    skd.place(60, (34.0, 8.0, 0.0), math.pi)
    skd.draw(60, target=Vector((34.0, 0.0, 1.0)))
    skd.lower(84)
    expect("a draw starting on a cut snaps up with it; an explicit lower(release) is kept",
           near(skd.aiming_at(60), 1.0, 1e-9) and near(skd.aiming_at(90), 0.0, 1e-9))
    walker = players.make_player("walker", "steve")
    walker.place(1, (40.0, 0.0, 0.0), math.pi / 2.0)
    walker.walk(1, [(40.0, 0.0, 0.0), (52.0, 0.0, 0.0)], speed=4.3)
    skw = make_skeleton("skw")
    skw.place(1, (45.0, 10.0, 0.0), math.pi)
    flw = skw.shoot(10, walker, knockback=0.0)
    lo, hi = _box_of(walker, flw.frames[1])
    inside = all(lo[i] - 0.05 <= flw.hit[i] <= hi[i] + 0.05 for i in range(3))
    expect("a player walking across the line of fire at 4.3 blocks/s is hit (the arrow leads him), no exception",
           not flw.missed and flw.stuck is not None and inside, "impact %d hit %s" % (int(flw), tuple(round(c, 2) for c in flw.hit)))
    flm = fire(skw, walker, 40, lead=False, knockback=0.0)
    expect("lead=False at the walker: the game's miss, the arrow sticks in the ground past him, nobody hurt",
           flm.missed and flm.stuck is flm.arrow and near(flm.hit.z, 0.0, 1e-6)
           and len(walker.__dict__[_BOOK]["arrows"]) == 1, "%s" % (tuple(round(c, 2) for c in flm.hit),))
    pa = players.make_player("pa", "steve")
    pa.place(1, (60.0, 0.0, 0.0), 0.0)                               # facing -Y, the shooter in front of him
    ska = make_skeleton("ska")
    ska.place(1, (60.0, -8.0, 0.0), 0.0)
    ska.look_at(1, pa, ease=0)
    a1, a2 = ska.shoot(10, pa, knockback=0.0), ska.shoot(40, pa, knockback=0.0)
    pb = players.make_player("pb", "steve")
    pb.place(1, (64.0, 0.0, 0.0), math.pi)                           # facing +Y: the shooter behind him
    a3 = fire(ska, pb, 20, knockback=0.0)
    expect("part=None: a free spot facing the shooter each time (front: %s, %s; from behind: %s)" % (
        a1.spot, a2.spot, a3.spot), a1.spot != a2.spot and a1.spot in ("chest", "chest_l", "belly")
        and a2.spot in ("chest", "chest_l", "belly") and a3.spot in ("back", "back_low"))
    scene.frame_set(int(a1) + 1)
    shaft = -(a1.stuck.matrix_world.to_3x3() @ Vector((1.0, 0.0, 0.0))).normalized()
    want = _spot_world(pa, a1.spot, int(a1) + 1)
    expect("spot_direction (the docstring's table) is the way the stuck shaft really points (%s)" % a1.spot,
           shaft.angle(want) < math.radians(2.0), "%.1f deg" % math.degrees(shaft.angle(want)))
    al = fire(ska, pa, 70, part="shoulder_l", align=True, knockback=0.0)
    scene.frame_set(int(al) + 1)
    tipd = (al.stuck.matrix_world.to_3x3() @ Vector((1.0, 0.0, 0.0))).normalized()
    expect("align=True: the shaft lies along the flight (tip forward)", tipd.angle(al.direction) < math.radians(2.0),
           "%.1f deg" % math.degrees(tipd.angle(al.direction)))
    crk = make_creeper("crk")
    crk.place(1, (70.0, 0.0, 0.0), 0.0)
    skk = make_skeleton("skk")
    skk.place(1, (70.0, -8.0, 0.0), 0.0)
    fk = skk.shoot(10, crk)                                          # the game's 0.4
    back0 = (crk.pos_at(int(fk) + 20) - crk.pos_at(int(fk))).length
    crk2 = make_creeper("crk2")
    crk2.place(1, (74.0, 0.0, 0.0), 0.0)
    skk2 = make_skeleton("skk2")
    skk2.place(1, (74.0, -8.0, 0.0), 0.0)
    fk2 = skk2.shoot(10, crk2, knockback=0.1)
    back1 = (crk2.pos_at(int(fk2) + 20) - crk2.pos_at(int(fk2))).length
    crk3 = make_creeper("crk3")
    crk3.place(1, (78.0, 0.0, 0.0), 0.0)
    skk3 = make_skeleton("skk3")
    skk3.place(1, (78.0, -8.0, 0.0), 0.0)
    fk3 = skk3.shoot(10, crk3, max_back=0.5)
    back2 = (crk3.pos_at(int(fk3) + 20) - crk3.pos_at(int(fk3))).length
    expect("arrow knock-back on a mob: the game's 0.4 = %.2f blocks, knockback=0.1 = %.2f, max_back=0.5 = %.2f"
           % (back0, back1, back2), back0 > 1.2 and back1 < 0.5 and back2 <= 0.5 + 1e-3)
    crs = make_creeper("crs")
    crs.place(1, (82.0, 0.0, 0.0), 0.0)
    e_ = crs.step(10, (82.0, -5.0, 0.0))
    peak = max(abs(ch._val(crs.leg_r, _ROT, 0, f)) for f in range(10, e_ + 1))
    expect("Creeper.step: half a block in 14 frames, legs out to 44 degrees and together again",
           e_ == 24 and near((crs.pos_at(e_) - crs.pos_at(10)).length, 0.5, 1e-3) and near(math.degrees(peak), 44.2, 1.0)
           and abs(ch._val(crs.leg_r, _ROT, 0, e_)) < 1e-6, "end %d peak %.1f" % (e_, math.degrees(peak)))
    crx = make_creeper("crx")
    crx.place(1, (90.0, 0.0, 0.0), 0.0)
    bx = crx.fuse(5)
    crx.explode(bx, camera=cam, blocks=20, seed=2)
    cry = make_creeper("cry")
    cry.place(1, (96.0, 0.0, 0.0), 0.0)
    by = cry.fuse(5)
    cry.explode(by, camera=cam, blocks=20, seed=2, latency=True)

    def puffs_on(c, f):
        scene.frame_set(f)
        return sum(1 for o in c.last_explosion["burst"].objects if not o.hide_render)

    expect("explode(): the first puffs on the explosion frame itself (latency=True: one tick later, as the game)",
           puffs_on(crx, bx) > 0 and puffs_on(cry, by) == 0 and puffs_on(cry, by + 2) > 0,
           "%d / %d / %d" % (puffs_on(crx, bx), puffs_on(cry, by), puffs_on(cry, by + 2)))
    # ---- a Stage: hidden outside its shots, the arrows with it
    from films import lookdev

    from . import shots

    film = shots.Film(scene, fps=24)
    sa, sb = film.shot("a", 20.0, 22.0), film.shot("b", 22.0, 24.0)       # frames 481-528, 529-576
    stg = lookdev.Stage(scene, film, None, None)
    stg.in_shot.update({"a": set(), "b": set()})
    c5, p5 = add_creeper(stg, "c5"), players.add_player(stg, "p5", "steve")
    c5.place(sa.frame_start, (20.0, 0.0, 0.0), 0.0)
    p5.place(sa.frame_start, (22.0, 0.0, 0.0), 0.0)
    c5.fuse(sa.frame_start + 2)
    a5 = hit(p5, sa.frame_start + 4, "chest", hurt=False)
    stg.use(sa, c5)
    stg.use(sb, p5)
    stg.finish()
    scene.frame_set(sa.frame_start + 8)
    in_a = (not c5.head.hide_render, a5.hide_render, p5.torso.hide_render)
    scene.frame_set(sb.frame_start + 2)
    in_b = (c5.head.hide_render, not a5.hide_render, not p5.torso.hide_render,
            all(o.hide_render for obs in c5._shells.values() for o in obs))
    expect("Stage: the creeper only in its shot (and its white shells), the arrow only where Steve is", all(in_a)
           and all(in_b), "%s %s" % (in_a, in_b))
    print("hostiles check: %d failed" % len(fails))
    return not fails


PROOFS = ("lineup_front", "lineup_side", "lineup_back", "walk", "fuse", "explode", "draw", "flight", "stuck",
          "stuck_b", "ground", "death", "moving")
MEADOW = dict(y=36.0)                # the open meadow north of the exit gate (flat, z = 0)


CLEAR = (-1, 28, 10, 45)               # proof-local set dressing: no grass tufts on these meadow columns


def _stage(name, preset="night", res=(540, 960), samples=16, seconds=4.0, sun=(176.0, 21.0), clear=CLEAR,
           blocks=()):
    """The real village, look and Stage for one proof shot: (scene, village, film, stage, shot). clear = a
    rectangle of meadow columns whose grass tufts and flowers are taken out (through build_village's edit hook)."""
    from films import lookdev

    from . import look, quick, shots, village

    def edit(b):
        if clear:
            for x in range(clear[0], clear[2] + 1):
                for y in range(clear[1], clear[3] + 1):
                    b.clear_plants(x, y)
        for x, y, block in blocks:                                   # e.g. a lone fence post on the meadow
            b.w.set(x, y, int(b.surface_z(x, y)), block)                 # (surface_z = the top of the terrain)

    scene = quick.reset()
    look.setup_render(scene, res=res, samples=samples, threads=2, motion_blur=True)
    v = village.build_village(scene, seed=1, edit=edit if clear else None)
    sky = look.set_time(scene, preset, sun_azimuth=sun[0], sun_elevation=sun[1])
    if preset == "night":
        look.setup_compositor(scene, bloom=1.3, grade="cool")
    else:
        look.setup_compositor(scene, bloom=1.0, grade="warm")
    film = shots.Film(scene, fps=24)
    st = lookdev.Stage(scene, film, v, sky)
    s = st.shot(name, seconds)
    st.lights(s, scale=1.3 if preset == "night" else 1.0)
    return scene, v, film, st, s


def _ground(v, x, y):
    g = v.ground(x, y)
    return Vector((x, y, 0.0 if g is None else g))


def _render(scene, film, frame, name):
    """Render one frame of the proof film to out/test/<name>.png."""
    from . import quick

    os.makedirs(quick.TEST_DIR, exist_ok=True)
    film.goto(int(frame))
    path = os.path.join(quick.TEST_DIR, name + ".png")
    scene.render.filepath = path
    bpy.ops.render.render(write_still=True)
    print("wrote", path, "frame", frame, flush=True)
    return path


def _sheet_png(name, paths, labels=None, cols=None):
    """The stills side by side (cols per row) in out/test/<name>.png, each labelled."""
    from PIL import Image, ImageDraw

    from . import quick

    ims = [Image.open(q).convert("RGB") for q in paths]
    w, h = ims[0].size
    cols = cols or len(ims)
    rows = (len(ims) + cols - 1) // cols
    out = Image.new("RGB", (cols * w + (cols - 1) * 4, rows * h + (rows - 1) * 4), (20, 20, 24))
    d = ImageDraw.Draw(out)
    for i, im in enumerate(ims):
        x, y = (i % cols) * (w + 4), (i // cols) * (h + 4)
        out.paste(im, (x, y))
        if labels:
            d.rectangle((x, y, x + 8 * len(labels[i]) + 8, y + 16), fill=(0, 0, 0))
            d.text((x + 4, y + 2), labels[i], fill=(255, 255, 255))
    path = os.path.join(quick.TEST_DIR, name + ".png")
    out.save(path)
    print("wrote", path, flush=True)
    return path


def _lineup(view):
    """Creeper, Steve and the skeleton side by side on the meadow by day (front, side or back)."""
    from . import players

    sun = {"front": (235.0, 38.0), "side": (215.0, 38.0), "back": (40.0, 38.0)}[view]
    scene, v, film, st, s = _stage("hostiles_lineup_" + view, "day", sun=sun, seconds=1.0)
    f0 = s.frame_start
    y = MEADOW["y"]
    cr = add_creeper(st, "creeper")
    steve = players.add_player(st, "steve", "steve")
    sk = add_skeleton(st, "skeleton")
    yaw = math.pi / 2.0 if view == "side" else 0.0              # side: they face east, the lens sees their right
    for c, x in ((cr, 2.1), (steve, 3.4), (sk, 4.7)):
        c.place(f0, _ground(v, x, y), yaw)
    mid = _ground(v, 3.4, y)
    if view in ("front", "side"):
        cam, look_at = mid + Vector((0.3, -5.6, 1.05)), mid + Vector((0.0, 0.0, 0.95))
    else:
        cam, look_at = mid + Vector((-0.3, 5.6, 1.05)), mid + Vector((0.0, 0.0, 0.95))
    s.lens(30, 5.6)
    s.move(tuple(cam), tuple(look_at))
    s.focus(tuple(look_at))
    st.use(s, cr, steve, sk)
    st.finish()
    return _render(scene, film, f0 + 2, "hostiles_lineup_" + view)


def _proof_lineup_front():
    _lineup("front")


def _proof_lineup_side():
    _lineup("side")


def _proof_lineup_back():
    _lineup("back")


def _proof_walk():
    """The creeper walking across the night meadow: six frames over one leg cycle."""
    scene, v, film, st, s = _stage("hostiles_walk", res=(270, 480), seconds=3.0)
    f0 = s.frame_start
    y = MEADOW["y"]
    cr = add_creeper(st, "creeper")
    a, b = _ground(v, 9.0, y), _ground(v, 1.0, y)
    cr.place(f0, a, math.pi / 2.0)
    end = cr.walk(f0, [a, b])
    print("walk:", cr.last_walk, "end", end)
    s.lens(35, 4.0)
    s.follow(cr.root, (-1.7, -3.0, 0.65), look_offset=(0.0, 0.0, 0.75))    # the camera tracks ahead of it
    s.focus(cr.head)
    st.use(s, cr)
    st.finish()
    frames = [f0 + 24 + 4 * i for i in range(6)]
    paths = [_render(scene, film, f, "hostiles_walk_%d" % (i + 1)) for i, f in enumerate(frames)]
    _sheet_png("hostiles_walk_sheet", paths, ["f%d" % f for f in frames], cols=6)


def _fuse_set(name, res, seconds=4.0):
    from . import players

    scene, v, film, st, s = _stage(name, res=res, seconds=seconds)
    f0 = s.frame_start
    y = MEADOW["y"]
    cr = add_creeper(st, "creeper")
    steve = players.add_player(st, "steve", "steve")
    cr.place(f0, _ground(v, 4.0, y), math.radians(-60.0))
    steve.place(f0, _ground(v, 6.2, y - 1.3), math.radians(120.0))
    cr.look_at(f0, steve, ease=0)
    steve.look_at(f0, cr, ease=0)
    return scene, v, film, st, s, cr, steve


def _proof_fuse():
    """Swell and white flash: six frames of the fuse (start, flashes 1, 3, 4, 5, between)."""
    scene, v, film, st, s, cr, steve = _fuse_set("hostiles_fuse", (270, 480))
    f0 = s.frame_start + 4
    boom = cr.fuse(f0)
    here = cr.pos_at(f0)
    s.lens(35, 4.0)
    s.move(tuple(here + Vector((-2.2, -3.4, 0.55))), tuple(here + Vector((0.3, 0.0, 0.85))))
    s.focus(cr.head)
    st.use(s, cr, steve)
    st.finish()
    offs = [0, 5, 9, 18, 25, 32]
    frames = [f0 + o for o in offs]
    labels = ["f+%d s%.2f w%.2f" % (o, cr.swelling_at(f0 + o), cr.white_at(f0 + o)) for o in offs]
    print("fuse: explodes on", boom, labels)
    paths = [_render(scene, film, f, "hostiles_fuse_%d" % (i + 1)) for i, f in enumerate(frames)]
    _sheet_png("hostiles_fuse_sheet", paths, labels, cols=6)


def _proof_explode():
    """The explosion: the creeper gone and the game's particles, three frames; Steve knocked away."""
    scene, v, film, st, s, cr, steve = _fuse_set("hostiles_explode", (360, 640))
    f0 = s.frame_start + 2
    boom = cr.fuse(f0)
    centre = cr.explode(boom, camera=s, village=v, victims=[steve], seed=3)
    print("explode:", boom, cr.last_explosion["blocks"], "block positions,", cr.last_explosion["burst"].block_particles,
          "block particles,", len(cr.last_explosion["burst"].objects), "objects; pushed", cr.last_explosion["pushed"])
    s.lens(28, 5.6)
    s.move(tuple(centre + Vector((-3.6, -6.2, 1.1))), tuple(centre + Vector((0.6, 0.0, 1.2))))
    s.focus(tuple(centre + Vector((0.0, 0.0, 1.0))))
    st.use(s, cr, steve)
    st.finish()
    offs = [-1, 0, 6]                    # the last frame with the creeper, the first puffs ON boom, the blast
    paths = [_render(scene, film, boom + o, "hostiles_explode_%d" % (i + 1)) for i, o in enumerate(offs)]
    _sheet_png("hostiles_explode_sheet", paths, ["boom%+d" % o for o in offs], cols=3)


def _proof_draw():
    """The skeleton: bow lowered, raised, drawn (pulling 0, 1, 2), released (arrow away), lowered again."""
    from . import players

    scene, v, film, st, s = _stage("hostiles_draw", res=(270, 480), seconds=3.0)
    f0 = s.frame_start
    y = MEADOW["y"]
    sk = add_skeleton(st, "skeleton")
    steve = players.add_player(st, "steve", "steve")
    here, there = _ground(v, 5.5, y + 1.0), _ground(v, 1.0, y - 5.0)
    fwd = Vector((there.x - here.x, there.y - here.y, 0.0)).normalized()
    sk.place(f0, here, math.atan2(fwd.x, -fwd.y))
    steve.place(f0, there, math.atan2(-fwd.x, fwd.y))
    steve.look_at(f0, sk, ease=0)
    sk.look_at(f0, steve, ease=0)
    sk.aim(f0 + 6, steve)
    d0 = f0 + 12
    fl = sk.shoot(d0, steve, part="chest", knockback=0.1)
    sk.lower(fl.frames[0] + 14)
    right = Vector((fwd.y, -fwd.x, 0.0))                             # the skeleton's right: the bow side
    s.lens(32, 4.0)
    s.move(tuple(here + right * 2.9 + fwd * 0.9 + Vector((0.0, 0.0, 1.35))),
           tuple(here + fwd * 0.35 + Vector((0.0, 0.0, 1.3))))
    s.focus(sk.head)
    st.use(s, sk, steve)
    st.finish()
    rel = fl.frames[0]
    frames = [f0 + 3, d0 + 4, d0 + 17, d0 + 22, rel + 1, rel + 22]
    labels = ["%s f%d" % (sk.bow_at(f).replace("bow_pulling_", "pull") if sk.aiming_at(f) else "down", f) for f in frames]
    print("draw:", labels, "release", rel, "impact", int(fl))
    paths = [_render(scene, film, f, "hostiles_draw_%d" % (i + 1)) for i, f in enumerate(frames)]
    _sheet_png("hostiles_draw_sheet", paths, labels, cols=6)


def _proof_flight():
    """An arrow in flight with the film's motion blur: over the skeleton's shoulder, and in profile."""
    from . import players

    scene, v, film, st, s = _stage("hostiles_flight", res=(540, 960), seconds=3.0)
    f0 = s.frame_start
    y = MEADOW["y"]
    sk = add_skeleton(st, "skeleton")
    steve = players.add_player(st, "steve", "steve")
    a, b = _ground(v, 4.0, y + 5.0), _ground(v, 4.0, y - 4.0)
    sk.place(f0, a, 0.0)                                             # facing south, at Steve
    steve.place(f0, b, math.pi)                                      # facing north, at the skeleton
    steve.look_at(f0, sk, ease=0)
    sk.aim(f0, steve, ease=0)
    fl = sk.shoot(f0 + 4, steve, part="chest", knockback=0.1)
    rel, imp = fl.frames
    st.use(s, sk, steve)
    # over the skeleton's left shoulder, down the line of fire: the arrow flies away toward Steve
    mid = rel + 2
    s.lens(32, 5.6)
    s.move(tuple(a + Vector((0.62, 1.25, 1.95))), tuple(b + Vector((-0.2, 0.0, 1.25))))
    s.focus(tuple(fl.point_at(mid + 0.25)))
    st.finish()
    print("flight: release", rel, "impact", imp, "rendered", mid, mid + 1)
    _render(scene, film, mid, "hostiles_flight")
    # in profile, 4.3 blocks from the path: the arrow and its streak are a third of the frame wide
    pt = fl.point_at(mid + 1.25)
    s.lens(35, 5.6)
    s.move(tuple(pt + Vector((-4.3, 0.0, 0.1))), tuple(pt + Vector((0.0, 0.0, -0.1))))
    s.focus(tuple(pt))
    _render(scene, film, mid + 1, "hostiles_flight_side")


def _stuck(view):
    """Steve walking with an arrow in his chest and one in his back: three frames from one angle."""
    from . import players

    scene, v, film, st, s = _stage("hostiles_stuck_" + view, res=(360, 640), seconds=3.0)
    f0 = s.frame_start
    y = MEADOW["y"]
    steve = players.add_player(st, "steve", "steve")
    a, b = _ground(v, 6.0, y + 2.0), _ground(v, 1.0, y - 3.0)
    steve.place(f0, a, 0.0)
    hit(steve, f0, "chest", hurt=False)
    hit(steve, f0, "back", hurt=False)
    steve.walk(f0, [a, b], speed=2.0)
    here = steve.pos_at(f0 + 30)
    if view == "a":
        s.move(tuple(here + Vector((-2.6, -2.4, 1.25))), tuple(here + Vector((0.0, 0.0, 1.05))))
    else:
        s.move(tuple(here + Vector((2.8, 2.2, 1.35))), tuple(here + Vector((0.0, 0.0, 1.05))))
    s.lens(35, 5.6)
    s.focus(steve.head)
    st.use(s, steve)
    st.finish()
    frames = [f0 + 22, f0 + 30, f0 + 38]
    paths = [_render(scene, film, f, "hostiles_stuck_%s%d" % (view, i + 1)) for i, f in enumerate(frames)]
    _sheet_png("hostiles_stuck_%s_sheet" % view, paths, ["f%d" % f for f in frames], cols=3)


def _proof_stuck():
    _stuck("a")


def _proof_stuck_b():
    _stuck("b")


def _proof_ground():
    """Arrows stuck in the ground and in a fence post: the 7-tick shake of the tail, then still."""
    post = (5, 37)
    scene, v, film, st, s = _stage("hostiles_ground", res=(360, 640), seconds=3.0, blocks=[(post[0], post[1], "oak_fence")])
    f0 = s.frame_start
    sk = add_skeleton(st, "skeleton")
    a = _ground(v, 9.5, 44.0)
    sk.place(f0, a, math.radians(150.0))
    pz = v.ground(post[0] + 0.5, post[1] + 0.5)
    hit_post = Vector((post[0] + 0.5, post[1] + 10.0 / 16.0, pz + 0.7))      # the post's north face (6..10 px)
    hit_dirt = _ground(v, 4.3, 38.9)
    fl1 = sk.shoot(f0 + 2, hit_post)
    fl2 = fire(sk, hit_dirt, fl1.frames[0] + 6)
    print("ground: post impact", int(fl1), "ground impact", int(fl2))
    s.lens(35, 5.6)
    mid = (hit_post + hit_dirt) * 0.5
    s.move(tuple(mid + Vector((-3.3, -1.1, 0.75))), tuple(mid + Vector((0.2, 0.1, 0.35))))
    s.focus(tuple(mid + Vector((0.0, 0.0, 0.3))))
    st.use(s, sk)
    st.finish()
    frames = [int(fl1) + 1, int(fl2) + 2, int(fl2) + 24]
    paths = [_render(scene, film, f, "hostiles_ground_%d" % (i + 1)) for i, f in enumerate(frames)]
    _sheet_png("hostiles_ground_sheet", paths, ["f%d" % f for f in frames], cols=3)


def _proof_moving():
    """A moving target: Steve sprints across the line of fire; the first arrow (lead=False, the game's aim at
    where he is on the release) misses behind him and sticks in the ground; the second is led and sticks in him
    (part=None: the free spot facing the skeleton) while he runs on."""
    from . import players

    scene, v, film, st, s = _stage("hostiles_moving", res=(360, 640), seconds=2.0, clear=(-3, 22, 15, 45))
    s2 = st.shot("hostiles_moving_b", 1.0)                           # frames 49-72: the camera runs with him
    st.lights(s2, scale=1.3)
    f0 = s.frame_start
    y = MEADOW["y"]
    sk = add_skeleton(st, "skeleton")
    steve = players.add_player(st, "steve", "steve")
    a, b = _ground(v, -2.0, y - 1.0), _ground(v, 14.0, y - 1.0)
    here = _ground(v, 6.0, y + 7.0)
    steve.place(f0, a, -math.pi / 2.0)                               # facing east, sprinting east
    steve.walk(f0, [a, b], sprint=True, ramp=(False, False))
    sk.place(f0, here, 0.0)
    sk.aim(f0, steve, ease=0)
    fl1 = sk.shoot(f0 + 2, steve, lead=False, village=v)
    fl2 = sk.shoot(fl1.frames[0] + 1, steve, knockback=0.1, village=v)
    print("moving: first", fl1.frames, "missed", fl1.missed, "ground at", tuple(round(c, 2) for c in fl1.hit),
          "| second", fl2.frames, "missed", fl2.missed, fl2.spot)
    g = fl1.hit                                                      # shot 1: low, at the missed arrow
    s.lens(35, 5.6)
    s.move(tuple(g + Vector((1.3, -2.2, 0.55))), tuple(g + Vector((-0.1, 0.0, 0.25))))
    s.focus(tuple(g))
    s2.lens(30, 5.6)
    s2.follow(steve.root, (-2.2, -5.2, 1.25), look_offset=(0.6, 2.0, 0.9))
    s2.focus(steve.head)
    st.use(s, sk, steve)
    st.use(s2, sk, steve)
    st.finish()
    frames = [int(fl1) + 3, int(fl2) - 1, int(fl2) + 4]
    labels = ["missed f%d" % frames[0], "flight f%d" % frames[1], "%s f%d" % (fl2.spot, frames[2])]
    paths = [_render(scene, film, f, "hostiles_moving_%d" % (i + 1)) for i, f in enumerate(frames)]
    _sheet_png("hostiles_moving_sheet", paths, labels, cols=3)


def _proof_death():
    """Hurt and death of both mobs: red flash (over the creeper's swell), tipping over, the poof."""
    scene, v, film, st, s = _stage("hostiles_death", res=(270, 480), seconds=4.0)
    f0 = s.frame_start
    y = MEADOW["y"]
    cr = add_creeper(st, "creeper")
    sk = add_skeleton(st, "skeleton")
    a, b = _ground(v, 3.0, y), _ground(v, 5.2, y + 0.6)
    cr.place(f0, a, math.radians(-20.0))
    sk.place(f0, b, math.radians(-30.0))
    sk.aim(f0, (2.0, y - 6.0, 1.2), ease=0)
    cr.fuse(f0 + 2)
    shooter = (3.6, y - 6.0, 0.0)                                    # the blows come from the lens side
    cr.hurt(f0 + 12, attacker=shooter)
    sk.hurt(f0 + 16, attacker=shooter)
    gc = cr.die(f0 + 28, camera=s, attacker=shooter, village=v)
    gs = sk.die(f0 + 34, camera=s, village=v)
    mid = (a + b) * 0.5 + Vector((0.0, 1.6, 0.0))
    s.lens(30, 5.6)
    s.move(tuple(mid + Vector((-1.0, -7.0, 1.1))), tuple(mid + Vector((0.0, 0.0, 0.8))))
    s.focus(tuple(mid + Vector((0.0, 0.0, 0.9))))
    st.use(s, cr, sk)
    st.finish()
    frames = [f0 + 14, f0 + 18, f0 + 33, f0 + 44, gc + 3, gs + 6]
    labels = ["red", "red", "tip", "tip", "poof", "poof"]
    print("death: creeper gone", gc, "skeleton gone", gs)
    paths = [_render(scene, film, f, "hostiles_death_%d" % (i + 1)) for i, f in enumerate(frames)]
    _sheet_png("hostiles_death_sheet", paths, ["%s f%d" % (l_, f) for l_, f in zip(labels, frames)], cols=6)


def _proofs(names):
    """Render the proof stills by name (see PROOFS)."""
    for name in names:
        if name not in PROOFS:
            raise SystemExit("unknown proof %r (known: %s)" % (name, ", ".join(PROOFS)))
    for name in names:
        globals()["_proof_" + name]()


if __name__ == "__main__":
    which = set(sys.argv[1:])
    if not which or "check" in which:  # noqa: SIM102
        if not _check():
            sys.exit(1)
    rest = [w for w in sys.argv[1:] if w != "check"]
    if rest:
        _proofs(rest)
