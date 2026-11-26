"""MUSIC: the bandstand of "The Crammys" (film four, stories/crammys.json) on the village square, Kai's doorstep on the
lane, note blocks that are played, the jukebox (a disc in, its notes, a disc popped out), music discs 11 and cat, the
goat horn, the totem of undying, block items held in a hand and the players' applause. New module; edits no other
file. Numbers are transcribed from the Java Edition 26.x client jar (class or file named next to each constant);
textures and models are the game's own through engine.mcassets / engine.blocks / engine.mobs / engine.players.

USE IN A FILM (two skies: SKIES below; build everything in every build, as films/lookdev.py Stage asks)
    from engine import music, players, village
    v = village.build_village(scene, seed=1, edit=music.crammys_set)      # (combine with other set pieces in one hook)
    bd = music.band(v)                     # anchors bd.A / bd.yaw, cameras bd.cameras, notes, jukebox, last_lantern
    st = Stage(scene, film, v, skies=SKIES, sky=sky)
    zuri = players.add_player(st, "zuri", "zuri"); zuri.place(f0, bd.A["zuri"], bd.yaw["zuri"])
    bd.notes["zuri"].song(zuri, f0 + 4, count=4, every=8, camera=s)       # 4 taps, each one semitone up
    bd.lights(st, s, scale=1.0)            # golden hour; night: scale=1.3 (the proofs' level; palette check passes)

PUBLIC API
  crammys_set(b)                         the village hook: bandstand(b) + lane_set(b); returns both dicts
  bandstand(b, name="bandstand")         the stage on the WEST side of the square, facing west down the west street
      (the audience's and the cameras' side): a red wool platform one block high (x -8..-5, y -3..5, top z 1), a wall
      of blue / light blue wool with a yellow top behind it (x -4, three blocks above the floor), the front row of note
      blocks on the platform (x -8, from south to north: Sunny's on a PUMPKIN at y -2, a dressing one at -1, the gap
      at 0, Kai's on a GOLD BLOCK at 1, Zuri's on WHITE WOOL at 2, two dressing ones at 4 and 5: the base blocks
      replace the platform's wool, so they show in its front face under their note blocks), the jukebox centre stage
      right behind the gap (cell (-7, 0, 1): seen from the front through it), two lantern posts on the front corners
      (two oak fences + a lantern at (-8, -3) and (-8, 3)), two lanterns on the wall's top, and the trophy pedestal
      before the stage one block south of the centre line (an oak fence with a gold block, cell (-9, -1): on the
      centre line it hid the jukebox). The north post's lantern is NOT in the World: it is band.last_lantern, placed
      on camera in beat 5. Village paths that crossed the square there are re-routed round the stage; the anchors
      square_w / square_4 / square_6 move to free ground (dict['moved']). Lights: group 'bandstand'.
  lane_set(b, name="lane")               Kai's doorstep in front of house_f's door (x 4, y 16): his gold block with his
      note block on it at (1, 15) (south of the doorstep), a lantern on a post of two oak fences at (1, 17) (north
      of it: light group 'lane'), across the exit road from the narrator's door (house_e, x -4.5, y 15.5). Paths
      lane_home (up the road from the square side and in at house_e's door: beat 7) and lane_to_square (down the road
      from the north toward the square: beat 17).
  band(v) -> Band                        after the build:
      .A / .yaw        anchors (keys below; bandstand ones without the 'bandstand_' prefix, lane ones as lane_*)
      .cameras         cameras() for this set
      .notes           {'zuri', 'kai', 'sunny', 'row_1', 'row_2', 'row_3', 'lane'} -> NoteBlock
      .jukebox         Jukebox;   .last_lantern  LastLantern;   .pedestal_top  (x, y, 2.0) where the totem rests
      .totem(f0, f1, picked=None, face=None)   the totem of undying as a dropped item resting on the pedestal,
                       turning 1 rad/s and bobbing; picked = the frame it is taken (pedestal empty from then on);
                       face = a point its face turns to at f0. Returns the engine.mobs DroppedItem (st.cast[t.name] = t
                       and st.use(shot, t) where it must be hidden in other shots). Call it per shot it is seen in.
      .lights(st, shot, scale=1.0, stage=None, lane=None, at=None, **Stage.lights kw)   Stage.lights + the set's
                       lanterns: 'bandstand' x stage, 'lane' x lane (default scale), and the placed lantern
      .tap(who, player, frame, **kw)            = notes[who].tap(...)
  NoteBlock  .cell .base .instrument .note0 .point (where its note spawns) .center .top
      played(frame, note=None, camera=None, seed=0, glow=None)  what the game shows when the block is played ON
                       `frame`: ONE note particle, its colour from the note (note_colour). The block itself does not
                       move or change (NoteBlock has no block entity and no animation; triggerEvent only adds the
                       particle and plays the sound). A note block plays only with air above it (NoteBlock.playNote):
                       every note block of the set has. Returns the engine.fx Burst.
      tap(player, frame, use=True, camera=None, hand="right")   the player's arm swing ON frame (players attack),
                       the note one tick later; use=True = right-click (the note goes up one semitone first, 24 wraps
                       to 0: each tap a new colour), use=False = left-click (the same note). Returns the note.
      song(player, frame, count=4, every=8, ...)   a riff of taps; returns the notes.   note_at(frame)
  Jukebox    .cell .point .top .center
      play(f0, f1, disc="music_disc_11", camera=None, seed=0, first=True)   a note every 20 ticks (24 frames) at 1.2
                       above the block's base, colour value 0..3 of 24 at random (green, lime, yellow, orange); stops
                       by itself one second after the song (11: 71 s). Returns the note frames.
      insert(frame, player=None, disc="music_disc_11", hand="right", until=None, camera=None)   right-click with the
                       disc: the swing ON frame, the disc gone from the hand one tick later (the stack is consumed:
                       the game shows no disc going in, and has_record has the same block model), the song starts.
      eject(frame, player=None, disc="music_disc_cat", seed=0, land="top", until=None, camera=None)   right-click on
                       a playing jukebox (JukeboxBlockEntity.popOutTheItem): the swing ON frame; one tick later the
                       disc is an item at (0.5, 1.01, 0.5) +- 0.35 above the block with ItemEntity's toss (+-0.1, 0.2
                       up, +-0.1 per tick): it rises about half a block, falls back and lies on the jukebox, turning
                       and bobbing (land="top" picks the first seed from `seed` whose toss stays on the jukebox;
                       "any" takes `seed`). Later notes are cancelled; notes in the air live out their 6 ticks.
                       Returns the DroppedItem (.land_frame, .still_frame, .rest_pos, .seed, .spawn_point); register
                       it with the Stage (st.cast[item.name] = item; st.use(shot, item)) and item.pick_up(f) when
                       somebody takes it (the game: not before 10 ticks).
      stop(frame), playing_at(frame)
  LastLantern (band.last_lantern)  place(frame, player=None) the lantern block and its light appear ON frame with
      the placing swing; level(frame, scale); show(frame, visible) (a Stage cast member); objects().
  creeper_disc(feet, frame, disc="music_disc_11", seed=0, world=v, until=None, name=None, face=None) -> DroppedItem
      beat 16: the disc a creeper drops when a skeleton's arrow kills it (loot_table/entities/creeper.json: one of
      the 12 discs of #creeper_drop_music_discs), spawned ON the killing-blow frame at its feet with the item toss,
      landing on the terrain (world=v), then turning and bobbing; face = the point (the lens) it faces on landing.
  note_particle(pos, frame, note, camera=None, seed=0, glow=None)   one note particle anywhere (fx Burst)
  note_colour(note) -> (r, g, b) 0..1     note_pitch(note)     instrument(block_below, block_above=None)
  note_track(pos, rng) / note_rise()     the tick positions of a note / its 0.54-block rise
  item_track(world, spawn, velocity)     ItemEntity.tick from a spawn point in a World (landing on blocks)
  hold(player, item, hand="right", frame=None)   engine.players hold for this film's items: block items
      ('gold_block', 'pumpkin', 'note_block', 'white_wool', 'jukebox') drawn as the game draws a block in a hand
      (models/block/block.json display thirdperson_righthand: rotation (75, 45, 0), translation (0, 2.5, 0), scale
      0.375: a small tilted cube at the fist); flat items ('music_disc_11', 'music_disc_cat', 'goat_horn',
      'totem_of_undying', 'lantern') as sprites lying along the hand (item/generated: translation (0, 3, 1), scale
      0.55). players.hold accepts all of them (nothing had to be built here). KEY IT PER SHOT: hold(..., frame=f0)
      (a hold without frame is for the whole film: the last call wins in every shot), hold(None, frame=f0) to empty.
  present(player, f0, f1, target, hand="right", ease=6)   the arm held straight out at `target` (the lens) so a
      flat item shows the lens its face (beats 6, 20, 24); a film gesture (third-person players raise an arm only
      for bows, shields, the horn, the spyglass). Aimed from the shoulder at f0 (0.7 degrees off in the self-test).
  clap(player, frame, count=6, every=4, down=2)   the players' applause: fast crouches (players sneak snaps)
  hero_item(item_id, collection=None)    a flat item on its own (engine.mcassets.item_object), for close-ups
  cameras() -> {name: dict(pos, target, lens, fstop, focus, beat[, pos1, target1])}   (Shot.move / lens / focus)
  SKIES                                  the proofs' skies: gold = golden, sun az 240 el 27 (south-west: in front of
      the west-facing stage, 120 degrees off a camera looking east at it; the farm that way is low); night = the moon
      of tools/check_hostiles_crammys (az 176, el 21: from the west, the stage front is moonlit)
  Numbers: NOTES 25, NOTE_SPAWN, NOTE_LIFETIME 6, NOTE_FRICTION 0.66, NOTE_RISE 0.2, JUKEBOX_EVERY_TICKS 20,
  JUKEBOX_NOTES 4, EJECT_UP 1.01, EJECT_SPREAD 0.7, ITEM_TOSS, SONG_SECONDS, CREEPER_DISCS, INSTRUMENT_OF; the set:
  STAGE, HEROES, DRESSING_NOTES, HERO_NOTES (zuri 6, kai 10, sunny 0), JUKEBOX_CELL, PEDESTAL, POSTS, LANE.

ANCHORS (seed 1; stage floor z 1.0, ground -0.06 / 0.0)
  performers at their note blocks, facing them: zuri (-6.6, 2.85), kai (-6.6, 1.65), sunny (-6.6, -1.3); noor
  (-5.45, 2.45, facing west), alex (-5.5, 1.45); alex_post (-7.0, 3.25: beat 5, facing the north post's top);
  alex_eject (-5.6, 0.5: behind the jukebox, facing west); steve_center (-5.6, 1.25: beat 24, centre stage behind
  the jukebox, 0.75 north of its notes, which would rise in front of a face there); steve_jukebox (-6.5, 1.6: at
  the jukebox's north side, facing it); alex_beside (-5.6, 1.65, facing south); steve_wing (-6.4, 5.4: the wing,
  stage height); half_1..4 (beat 19: south of the jukebox, facing the wing); flank_n1..3 / flank_s1..3 (beats
  22-24: north / south of the jukebox, facing it: three-quarter faces from the front); three_sunny / three_steve /
  three_noor (beat 18: a row across the south half, facing the jukebox). On the ground: steve_front (-11.2, -0.3:
  beat 1), steve_kai (-9.65, 0.05: beat 3), steve_foot (-9.75, -1.15: beat 4), steve_watch (-9.6, -2.3: beat 8),
  line_1..5 (x -10.2, y 2.3 .. -2.7, facing west: beat 6, line_5 = Steve). Targets: note_<who>_target,
  base_<who>_target, jukebox_target, jukebox_top_target, pedestal_target, center_target, wing_target. Lane:
  lane_kai (2.75, 16.75, facing west), lane_from_south (0.4, 9.8), lane_from_north (0.4, 22.5), lane_note_target,
  lane_door_target (house_e's door); doors: v.doors['house_e'] (the narrator's, v.door_open('house_e', f)).

BEATS (camera = bd.cameras[name]; every camera checked on a still, out/test/music_cams_gold.png and
music_cams_night.png; key holds and notes per shot; night torches scale 1.3)
   1  'b1'  40 mm f/2, low (z 1.0), push in (pos -> pos1). Steve at steve_front (on the right third, sharp); zuri,
           kai, sunny tap (bd.tap(who, p, f)), noor: hold(noor, 'goat_horn', frame=f0); noor.toot(f0, f1) (no note:
           a horn makes none). Sunny's head is at the frame edge; Steve can turn his head 70 degrees, not back.
   2  'b2'  40 mm, close on Zuri's note block on white wool, tilt target -> target1 (her face). notes['zuri'].song(
           zuri, f, count=4, every=8, camera=s): red-magenta, red, ... (one semitone and one colour per tap).
   3  'b3'  45 mm: past Steve's shoulder (steve_kai, soft, right) to Kai's note block on gold; rack focus to
           kai's face (focus=(-7.5, 1.5, 1.2) then kai.head). The sun (south-west) is behind the camera: no rim on
           the gold.
   4  'b4'  30 mm static wide; sunny taps ONE note (bd.tap('sunny', ...)); zuri and kai look_at him; Steve at
           steve_foot looking at the ground.
   5  'b5'  35 mm close on the totem (bd.totem(f0, f1, face=cam['pos'])) rising and pulling back to pos1 (the
           whole stage); alex at alex_post: hold(alex, 'lantern', frame=f0);
           bd.last_lantern.place(f, player=alex); alex.hold(None, frame=f + 1).
   6  'b6'  35 mm, dolly pos -> pos1 along the line (line_1..4: zuri note_block, noor goat_horn, alex
           music_disc_cat, sunny pumpkin; line_5 = Steve, empty hands): hold(p, item, frame=f0); present(p, f0, f1,
           the point the dolly passes in front of p (x -13.0, y_p + 1.0, z 1.5)); rack the focus along the line
           (Shot.focus(..., at_s=...)): the proof holds it on the first act.
   7  'lane' 20 mm from Kai's doorstep: kai at lane_kai (back of his head soft, right), his gold block and note block
           (left), the lantern above his head (right edge), the narrator's door across the lane; Steve
           walk(f, v.paths['lane_home'], sprint=True) (left to right, then in at house_e's door: v.door_open('house_e',
           ...)); the zombie (engine.undead) 4 blocks behind on the same path; kai.look_at(f, steve) to follow.
   8  'b8'  40 mm over Steve's shoulder (steve_watch, head soft lower left): jukebox.play(f0 - 30, f, disc=
           'music_disc_cat'); alex at alex_eject: item = bd.jukebox.eject(f, player=alex, camera=s); st.cast[item.name]
           = item; steve.look_at(f + 2, item.root) then away; rack focus to his profile.
  16  music.creeper_disc(cr_feet, kill_frame, world=v, face=lens, until=f1): ON the killing blow (hostiles shoot
           kill=True returns its frame); aim at item.rest_pos (out/test/music_meadow_disc.png, 'meadow_disc' 40 mm
           from z 0.65: a black shape on the moonlit ground). No experience orbs (a skeleton's kill gives none).
  17  'lane' the same camera; Steve walk(f, v.paths['lane_to_square'], sprint=True) right to left with
           hold(steve, 'music_disc_11', frame=f0) (edge-on while running, as the story allows).
  18  'b18' 35 mm from the stage's front-south at head height: three_sunny, three_steve, three_noor (Steve can walk on
           from steve_wing behind the jukebox first); sunny.look_at(f, steve chest) and back to jukebox_top_target.
  19  'b19' 32 mm from the wing, behind and above Steve walking steve_wing -> steve_jukebox (speed 1.6, disc held);
           zuri, kai, sunny, noor at half_1..4 facing the wing (look_at Steve); alex at alex, steps aside.
  20  'b20' 40 mm from across the jukebox (south of it): steve at steve_jukebox, alex at alex_beside, both
           present(p, f0, f1, cam['pos']) with music_disc_11 / music_disc_cat: both discs face-on; then the arm comes
           down (present ends) and bd.jukebox.insert(f, player=steve, disc='music_disc_11', camera=s): first note.
  21  'b21' 32 mm, the jukebox sharp in front (its notes rising), push pos -> pos1 to Steve at steve_jukebox.
  22  'b22' 30 mm locked-off frontal wide: flank_n1..3 and flank_s1..3 (Steve one of them), all facing the jukebox
           (their faces three-quarter to the lens), jukebox.play running; nobody moves.
  23  'b23' 30 mm from beside the jukebox (over the front gap) along the north row's faces (flank_n1..3 face the
           lens); the south row is behind the camera: put the five turners in the north row for this shot or accept
           profiles. kai steps (walk speed <= 1.0, at least 7 frames), heads turn in sequence (look_at f, f+6, ...).
  24  'b24' 45 mm medium on Steve at steve_center facing the lens, hold(steve, 'totem_of_undying', frame=f0),
           present(steve, f0, f1, cam['pos']); the pedestal (empty: totem(..., picked=f) earlier, or no totem() in
           this shot) at the bottom right; pull back to pos1; the five at the flanks clap(p, f + 2 * i, count=6).

WHAT THE GAME DOES (transcribed from the 26.3 client jar; no game file is copied)
  NoteBlock         triggerEvent: addParticle(NOTE, x + 0.5, y + 1.2, z + 0.5, note / 24, 0, 0) and the sound at pitch
                    2^((note - 12) / 12) (getPitchFromNote); playNote only when the block above is air (or a mob head:
                    worksAboveNoteBlock); useWithoutItem cycles NOTE 0..24 then plays; attack plays; setInstrument:
                    the head above, else the block below's instrument (Blocks: every wool GUITAR, gold block BELL,
                    pumpkin DIDGERIDOO, stone BASEDRUM, planks BASS ..., default HARP). No block entity, no animation.
  NoteParticle      speed = Particle's random start speed x 0.01, + 0.2 up; friction 0.66; lifetime 6; quadSize x 1.5
                    (0.15-0.3, the quad is twice that wide), grows over 6/32 tick; colour rgb = max(0, sin((c + k/3)
                    2 pi) 0.65 + 0.35), c = note / 24, k = 0, 1, 2; layer OPAQUE (cut-out); textures/particle/note.png.
  JukeboxSongPlayer tick: a JUKEBOX_PLAY event and spawnMusicParticles when ticksSinceSongStarted % 20 == 0:
                    sendParticles(NOTE, bottom centre + (0, 1.2, 0), count 0, nextInt(4) / 24, 0, 0, speed 1) = one
                    note of colour value 0..3; JukeboxSong.hasFinished: ticks >= ceil(20 x length) + 20.
  JukeboxBlockEntity.popOutTheItem: Vec3.atLowerCornerWithOffset(pos, 0.5, 1.01, 0.5).offsetRandomXZ(0.7) ->
                    new ItemEntity (velocity nextDouble 0.2 - 0.1, 0.2, nextDouble 0.2 - 0.1), setDefaultPickUpDelay
                    (10 ticks). blockstates/jukebox.json: one model for has_record true and false (cube_top: jukebox_
                    side / jukebox_top).
  ItemEntity        gravity 0.04, drag 0.98 (x 0.6 on the ground), EntityType ITEM 0.25 x 0.25; ItemEntityRenderer:
                    bob sin(age / 10 + bobOffs) 0.1 + 0.1, spin age / 20 + bobOffs (engine.mobs DroppedItem).
  loot_table/entities/creeper.json: pool 2, one roll of #creeper_drop_music_discs when the attacker is in
                    #skeletons (13, cat, blocks, chirp, far, mall, mellohi, stal, strad, ward, 11, wait).
  Items             item/template_music_disc -> item/generated; item/goat_horn (display thirdperson rotation (0, 180, 0))
                    and item/tooting_goat_horn (items/goat_horn.json: using_item) through players.toot;
                    totem_of_undying item/generated; block items: block/block.json display.

WHERE IT DIFFERS FROM THE GAME (on purpose or not modelled)
  - present() is a film gesture: no third-person pose raises an arm to show an item.
  - The note colour of the jukebox is drawn from a seeded generator, the game's from the level random.
  - eject(land="top") chooses the seed of a toss that stays on the jukebox; the game's toss can roll off the side.
  - A dropped item rests where item_track lands it (full cubes and dirt paths); slabs and stairs are not floors.
  - creeper_disc(face=) chooses the spin phase; the game's bobOffs is random.
  - The bandstand, the doorstep and the pedestal are player builds (no vanilla structure has them); every block in
    them is vanilla.
  - Sound is not made here (note block timbres, the disc's song): SCRIPTS / narration.

GOTCHAS
  - KEY HOLDS PER SHOT (hold(p, item, frame=f0)), in film order: Player.hold without a frame is for the whole film.
  - Notes need camera= (the Shot) to face the lens; a cut that jumps in time: engine.fx.stop_particles(first frame).
  - The jukebox's notes rise in front of anybody standing right behind it on its axis (x -5.6, y 0.5) seen from the
    front: steve_center stands 0.75 north of it.
  - Performers at their note blocks are seen from the chest up from the front (the front row is 1 block high on
    the 1-block platform); full figures: the wing (b19) or the frontal wide from higher up.
  - The pedestal's totem covers the face of whoever stands right behind it from a camera at the totem's height.
  - LastLantern is not in v.lantern_lights: Band.lights (not Stage.lights alone) sets its level per shot.
  - A dropped disc / totem must be registered with the Stage (st.cast[item.name] = item) to be hidden in other shots.
  - Night torches at 1.3: the palette check passes (stone G/R 0.98-0.99 at night, 0.93-0.94 at golden hour on the
    proofs). Do not boost the bandstand's lanterns beyond 1.6 near the cobblestone of the well behind the wall.

Self-test:  $BPY -m engine.music                       numbers, the set in the village, the calls' keys (33 checks, 10 s)
            $BPY -m engine.music stills NAME ...        proof stills out/test/music_<NAME>.png through the real look
                                                       (tools/music_proof.py: wide_gold wide_night notes jukebox discs
                                                       totem held horn doorstep clap meadow_disc cams_gold cams_night;
                                                       10-30 s each, 3-4 per call); MUSIC_RES=270x480 for framing tests
            $BPY -m tools.check_music_stamp            the frame fingerprints follow every change (12 cases, 40 s; the
                                                       same digest in two processes)
            $BPY -m tools.music_scout [x0 y0 x1 y1]   a top-down map of the square and the lane (no rendering)
"""
import math

import bpy
import numpy as np
from mathutils import Vector

from . import characters as ch
from .village import yaw_of, yaw_to

FPS = 24
TICK = FPS / 20.0                       # film frames per game tick

# ---- the game's numbers (Java Edition 26.x client jar; class or file named next to each) -------------------------
NOTES = 25                              # NoteBlock.NOTE: IntegerProperty 0..24 (BlockStateProperties.NOTE)
NOTE_SPAWN = (0.5, 1.2, 0.5)            # NoteBlock.triggerEvent: addParticle(NOTE, x + 0.5, y + 1.2, z + 0.5, note / 24,
                                        #   0, 0) (game axes x, y up, z); JukeboxSongPlayer.spawnMusicParticles: the
                                        #   same point (Vec3.atBottomCenterOf(pos).add(0, 1.2, 0))
NOTE_LIFETIME = 6                       # NoteParticle: lifetime = 6 ticks
NOTE_FRICTION = 0.66                    # NoteParticle: friction 0.66 (speed x 0.66 every tick)
NOTE_DAMP = 0.01                        # NoteParticle: xd, yd, zd *= 0.01 (the random start speed of Particle)
NOTE_RISE = 0.2                         # NoteParticle: yd += 0.2 (blocks per tick, straight up)
NOTE_QUAD = 1.5                         # NoteParticle: quadSize *= 1.5 (SingleQuadParticle: 0.1 (0.5 r + 0.5) 2)
NOTE_GROW = 32.0                        # NoteParticle.getQuadSize: quadSize * clamp((age + t) / lifetime * 32, 0, 1)
NOTE_COLOUR_AMP, NOTE_COLOUR_BASE = 0.65, 0.35   # NoteParticle: rCol = max(0, sin((c + 0) 2 pi) 0.65 + 0.35), gCol with
                                        #   c + 1/3, bCol with c + 2/3; c = the 4th addParticle argument = note / 24
NOTE_TEXTURE = "particle/note"          # particles/note.json: "minecraft:note"
NOTE_GLOW = 0.6                         # self-light of the sprite (engine.fx SPRITE_GLOW): the game lights a particle
                                        #   with the light level of its place only, never shaded by direction
JUKEBOX_EVERY_TICKS = 20                # JukeboxSongPlayer.shouldEmitJukeboxPlayingEvent: ticksSinceSongStarted % 20 == 0
JUKEBOX_NOTES = 4                       # JukeboxSongPlayer.spawnMusicParticles: sendParticles(NOTE, ..., 0 count,
                                        #   nextInt(4) / 24, 0, 0, speed 1): the note colour value is 0, 1, 2 or 3
EJECT_UP = 1.01                         # JukeboxBlockEntity.popOutTheItem: Vec3.atLowerCornerWithOffset(pos, 0.5, 1.01,
EJECT_SPREAD = 0.7                      #   0.5).offsetRandomXZ(random, 0.7): x and z each + (nextFloat - 0.5) 0.7
ITEM_TOSS = (0.1, 0.2)                  # ItemEntity(level, x, y, z, stack): velocity (nextDouble 0.2 - 0.1, 0.2, ...)
ITEM_GRAVITY = 0.04                     # ItemEntity: getDefaultGravity
ITEM_DRAG = 0.98                        # ItemEntity.tick: speed x (f, 0.98, f), f = 0.98 in the air ...
ITEM_GROUND = 0.6                       # ... and block friction 0.6 x 0.98 on the ground
ITEM_SIZE = 0.25                        # EntityType.ITEM: sized(0.25, 0.25)
PICKUP_DELAY_TICKS = 10                 # ItemEntity.setDefaultPickUpDelay: 10 ticks before anyone can take it
SONG_SECONDS = {                        # data/minecraft/jukebox_song/<disc>.json length_in_seconds
    "music_disc_11": 71.0, "music_disc_cat": 185.0, "music_disc_13": 178.0,
}
CREEPER_DISCS = ("music_disc_13", "music_disc_cat", "music_disc_blocks", "music_disc_chirp", "music_disc_far",
                 "music_disc_mall", "music_disc_mellohi", "music_disc_stal", "music_disc_strad", "music_disc_ward",
                 "music_disc_11", "music_disc_wait")
# loot_table/entities/creeper.json, second pool: one roll of tag #creeper_drop_music_discs (the 12 above,
# tags/item/creeper_drop_music_discs.json) when the "attacker" is in #skeletons. LivingEntity.die drops the loot ON
# the killing blow (dropAllDeathLoot), at the creeper's feet, as a new ItemEntity with the usual random toss.

# NoteBlock.setInstrument: the instrument of the block ABOVE if it is a mob head, else that of the block BELOW
# (BlockBehaviour.Properties.instrument, set per block in Blocks; HARP where a block sets none). Read from Blocks:
INSTRUMENT_OF = {
    "gold_block": "bell", "pumpkin": "didgeridoo", "hay_block": "banjo", "emerald_block": "bit",
    "packed_ice": "chime", "soul_sand": "cow_bell", "clay": "flute", "glass": "hat", "glass_pane": "hat",
    "sea_lantern": "hat", "beacon": "hat", "iron_block": "iron_xylophone", "glowstone": "pling",
    "sand": "snare", "red_sand": "snare", "gravel": "snare", "bone_block": "xylophone",
    "stone": "basedrum", "cobblestone": "basedrum", "mossy_cobblestone": "basedrum", "andesite": "basedrum",
    "granite": "basedrum", "diorite": "basedrum", "stone_bricks": "basedrum", "smooth_stone": "basedrum",
    "oak_planks": "bass", "spruce_planks": "bass", "birch_planks": "bass", "dark_oak_planks": "bass",
    "oak_log": "bass", "jukebox": "bass", "note_block": "bass",
}
WOOL_COLOURS = ("white", "orange", "magenta", "light_blue", "yellow", "lime", "pink", "gray", "light_gray", "cyan",
                "purple", "blue", "brown", "green", "red", "black")
INSTRUMENT_NAMES = {"harp": "piano (harp)", "basedrum": "bass drum", "snare": "snare drum", "hat": "clicks",
                    "bass": "double bass", "flute": "flute", "bell": "bells (glockenspiel)", "guitar": "guitar",
                    "chime": "chimes", "xylophone": "xylophone", "iron_xylophone": "iron xylophone (vibraphone)",
                    "cow_bell": "cow bell", "didgeridoo": "didgeridoo", "bit": "bit (square wave)",
                    "banjo": "banjo", "pling": "pling (electric piano)"}


def instrument(block_below, block_above=None):
    """NoteBlock.setInstrument: the instrument a note block plays on top of `block_below` (block ids)."""
    if block_above and (block_above.endswith("_head") or block_above.endswith("_skull")):
        return block_above.replace("_wall", "").rsplit("_", 1)[0]          # mob heads above win (worksAboveNoteBlock)
    b = (block_below or "air").replace("minecraft:", "")
    if b.endswith("_wool"):
        return "guitar"                                                  # Blocks: every wool colour GUITAR
    return INSTRUMENT_OF.get(b, "harp")


def note_colour(note):
    """(r, g, b) 0..1 the game tints the note particle of note 0..24 with (NoteParticle)."""
    c = float(note) / 24.0
    return tuple(max(0.0, math.sin((c + k / 3.0) * 2.0 * math.pi) * NOTE_COLOUR_AMP + NOTE_COLOUR_BASE)
                 for k in (0, 1, 2))


def note_pitch(note):
    """NoteBlock.getPitchFromNote: 2 ^ ((note - 12) / 12) (note 12 = the sound file's own pitch)."""
    return 2.0 ** ((int(note) - 12) / 12.0)


# ----------------------------------------------------------------------------------------------------
# note particles (engine.fx particle machinery: camera-facing quads, tick positions, stop_particles)
# ----------------------------------------------------------------------------------------------------
def note_track(pos, rng):
    """The tick positions of one note particle spawned at `pos` (Blender axes): NoteParticle's start speed (the
    random speed of Particle x 0.01, plus 0.2 up), friction 0.66, no gravity, 6 ticks. Returns [(x, y, z) after
    0..6 ticks]."""
    from . import fx

    v = fx._base_velocity(rng, (0.0, 0.0, 0.0)) * NOTE_DAMP
    v[2] += NOTE_RISE
    return fx._simulate(pos, v, NOTE_LIFETIME, 0.0, NOTE_FRICTION, None, 0.02, rng)


def note_rise():
    """How far a note particle rises in its 6 ticks (blocks), the sum of 0.2 x 0.66^k (k = 0..5): 0.537."""
    return sum(NOTE_RISE * NOTE_FRICTION ** k for k in range(NOTE_LIFETIME))


def _rgb8(rgb):
    return tuple(int(round(255.0 * max(0.0, min(1.0, c)))) for c in rgb)


def note_particle(pos, frame, note, camera=None, seed=0, glow=None, collection=None, burst=None):
    """ONE note particle of colour value `note` (0..24; float allowed) at `pos` (its centre at spawn), appearing ON
    `frame` (float: the tick it is spawned on), as NoteParticle draws it: the 8x8 note sprite tinted with
    note_colour(note), a camera-facing quad 0.3 to 0.6 block wide (full size after 6/32 tick), rising 0.54 block
    straight up and slowing (friction 0.66), gone after 6 ticks (7.2 frames). camera = the Shot / Film / camera
    object it faces (engine.fx). Returns the engine.fx Burst (kind 'note')."""
    from . import fx

    frame = float(frame)
    cams = fx._camera_arg(camera)
    col = fx._collection(collection)
    if burst is None:
        burst = fx.Burst("note", int(math.floor(frame)))
    p = Vector(tuple(float(c) for c in pos))
    rng = fx._rng(seed, int(frame * 10), int(p.x * 16), int(p.y * 16), int(p.z * 16), int(float(note) * 100))
    path = note_track((p.x, p.y, p.z), rng)
    quad = 0.1 * (rng.random() * 0.5 + 0.5) * 2.0 * NOTE_QUAD
    glow = NOTE_GLOW if glow is None else float(glow)
    tint = _rgb8(note_colour(note))
    mat = fx._particle_material(NOTE_TEXTURE, tint=tint, glow=glow)
    mname = "music_note_%02x%02x%02x%s" % (tint + ("+%g" % glow if glow else "",))
    mesh = bpy.data.meshes.get(mname) or fx._quad_mesh(mname, (0.0, 1.0, 0.0, 1.0), mat)
    fx._particle_object(burst, "music_note_%d_%d" % (int(frame * 10), len(burst.objects)), mesh, path, frame,
                        quad, cams, col, grow=NOTE_LIFETIME / NOTE_GROW * TICK)
    return burst


# ----------------------------------------------------------------------------------------------------
# dropped items (engine.mobs DroppedItem) with the game's own toss from a point above any floor
# ----------------------------------------------------------------------------------------------------
def _solid_top(world, x, y, z):
    """Top of the solid full block in column cell (x, y) at or under height z (None: nothing within 4 blocks)."""
    cx, cy = int(math.floor(x)), int(math.floor(y))
    for cz in range(int(math.floor(z + 1e-6)), int(math.floor(z)) - 5, -1):
        if world.is_solid(cx, cy, cz) and world.is_full_cube(cx, cy, cz):
            return float(cz + 1)
        bid = world.block_id(cx, cy, cz) or ""
        if bid == "dirt_path":
            return cz + 15.0 / 16.0
    return None


def item_track(world, spawn, velocity, max_ticks=240):
    """ItemEntity.tick from a spawn point in a World: [(tick, (x, y, z))] until the item lies still. Per tick:
    gravity 0.04, move (the 0.25-wide box stops against full blocks sideways and lands on the highest top under
    it), speed x 0.98 (x 0.6 more horizontally on the ground). z is the bottom of the item's box."""
    x, y, z = (float(c) for c in spawn)
    vx, vy, vz = (float(c) for c in velocity)
    h = ITEM_SIZE / 2.0
    out = [(0, (x, y, z))]

    def floor_at(px, py, pz):
        best = None
        for sx in (-h, h):
            for sy in (-h, h):
                t = _solid_top(world, px + sx, py + sy, pz)
                if t is not None and (best is None or t > best):
                    best = t
        return best if best is not None else -64.0

    def blocked(px, py, pz):
        for sx in (-h, h):
            for sy in (-h, h):
                c = (int(math.floor(px + sx)), int(math.floor(py + sy)), int(math.floor(pz + 0.01)))
                if world.is_solid(*c) and world.is_full_cube(*c):
                    return True
        return False

    for tick in range(1, max_ticks + 1):
        vz -= ITEM_GRAVITY
        nx, ny = x + vx, y + vy
        if blocked(nx, y, z):
            nx, vx = x, 0.0
        if blocked(nx, ny, z):
            ny, vy = y, 0.0
        x, y = nx, ny
        z += vz
        fl = floor_at(x, y, z - vz)
        on_ground = z <= fl
        if on_ground:
            z, vz = fl, 0.0
        f = ITEM_DRAG * (ITEM_GROUND if on_ground else 1.0)
        vx, vy, vz = vx * f, vy * f, vz * ITEM_DRAG
        out.append((tick, (x, y, z)))
        if on_ground and vx * vx + vy * vy < 1e-5:
            break
    return out


def _key_track(item, frame, track):
    """Put an engine.mobs DroppedItem on a tick track from `frame` (its drop() bookkeeping first)."""
    from . import fx

    end = track[-1][1]
    item.drop(frame, (end[0], end[1], end[2]), velocity=(0.0, 0.0, 0.0))     # visibility, age, born = frame
    frames = [frame - 1.0] + [frame + t * TICK for t, _p in track]
    for i in range(3):
        vals = [p[i] for _t, p in track]
        fx._write(item.root, "location", i, frames, [vals[0]] + vals, "LINEAR")
    item.rest_pos = Vector(end)
    item.spawn_point = tuple(track[0][1])
    land = next((t for t, p in track[1:] if abs(p[2] - end[2]) < 1e-6), track[-1][0])
    item.land_frame = int(math.ceil(frame + land * TICK))
    item.still_frame = int(math.ceil(frame + track[-1][0] * TICK))
    return item


def creeper_disc(feet, frame, disc="music_disc_11", seed=0, world=None, until=None, collection=None, name=None,
                 face=None):
    """The music disc a creeper drops when a skeleton's arrow kills it (loot_table/entities/creeper.json): an
    engine.mobs dropped item spawned ON the killing-blow frame at the creeper's feet with ItemEntity's random toss
    (+-0.1, 0.2 up, +-0.1 per tick), landing on the ground under it (world = the Village or its World: the terrain
    height there), then bobbing and spinning until `until` (default frame + 240); face = a point (the camera) the
    disc's face turns to on the frame it lands (the spin phase is chosen; the game's is random). Returns the
    DroppedItem (.land_frame, .still_frame, .rest_pos). The game draws one of 12 discs (CREEPER_DISCS) at random."""
    from . import mobs

    if disc not in CREEPER_DISCS:
        raise ValueError("creeper_disc: a creeper drops only %s" % ", ".join(CREEPER_DISCS))
    r = np.random.default_rng([int(seed) & 0x7FFFFFFF, 4111])
    vel = (r.uniform(-ITEM_TOSS[0], ITEM_TOSS[0]), r.uniform(-ITEM_TOSS[0], ITEM_TOSS[0]), ITEM_TOSS[1])
    p = Vector(tuple(float(c) for c in feet))
    item = mobs.make_dropped_item(disc, collection=collection, seed=seed, name=name)
    frame = int(round(frame))
    w = getattr(world, "world", world)
    if w is not None:
        _key_track(item, frame, item_track(w, (p.x, p.y, p.z + 0.01), vel))
    else:
        item.drop(frame, p, velocity=vel)
        item.land_frame = item.still_frame = int(frame + 12)
    if face is not None:
        item.face(item.land_frame, face)
    item.animate(frame, frame + 240 if until is None else int(until))
    return item


# ----------------------------------------------------------------------------------------------------
# the blocks that are played
# ----------------------------------------------------------------------------------------------------
class NoteBlock:
    """A note block of the set: .cell (the note block), .base (the block under it), .instrument, .note0 (the note
    it was tuned to at the start of the film), .top (its top face height), .point (where its particles spawn)."""

    def __init__(self, name, cell, base, note=0, above=None):
        self.name, self.cell, self.base = name, tuple(int(c) for c in cell), base
        self.instrument = instrument(base, above)
        self.note0 = int(note) % NOTES
        self._played = []                 # [(frame, note)]
        self.top = float(self.cell[2] + 1)
        self.point = (self.cell[0] + NOTE_SPAWN[0], self.cell[1] + NOTE_SPAWN[2], self.cell[2] + NOTE_SPAWN[1])
        self.center = (self.cell[0] + 0.5, self.cell[1] + 0.5, self.cell[2] + 0.5)

    def __repr__(self):
        return "<music.NoteBlock %s %s on %s at %s>" % (self.name, self.instrument, self.base, self.cell)

    def note_at(self, frame):
        """The note the block is tuned to at `frame` (after every right-click tap keyed before it)."""
        n = self.note0
        for f, note in sorted(self._played):
            if f <= frame:
                n = note
        return n

    def played(self, frame, note=None, camera=None, seed=0, glow=None, collection=None):
        """What the game shows when the block is played ON `frame`: one note particle above it in the colour of
        `note` (default: the note it is tuned to). The block itself does not move or change (NoteBlock has no
        block entity and no animation: triggerEvent only adds the particle and plays the sound). Returns the fx
        Burst."""
        n = self.note_at(frame) if note is None else int(note) % NOTES
        self._played.append((float(frame), n))
        return note_particle(self.point, frame, n, camera=camera, seed=seed, glow=glow, collection=collection)

    def tap(self, player, frame, use=True, camera=None, seed=0, glow=None, hand="right", collection=None):
        """A player plays the block: the arm swing requested ON `frame` (engine.players attack), the note one tick
        later (the server's block event reaches the client on the next tick). use=True is a right-click
        (NoteBlock.useWithoutItem: the note goes UP one semitone first, 24 wraps to 0: each tap a new colour);
        use=False a left-click (NoteBlock.attack: the same note again). Returns the note played."""
        if player is not None:
            player.attack(frame, hand)
        n = self.note_at(frame)
        if use:
            n = (n + 1) % NOTES
        self.played(frame + TICK, n, camera=camera, seed=seed, glow=glow, collection=collection)
        self._played.append((float(frame), n))
        return n

    def song(self, player, frame, count=4, every=8, use=True, **kw):
        """`count` taps `every` frames apart from `frame` (a riff); returns the notes played."""
        return [self.tap(player, frame + k * every, use=use, **kw) for k in range(int(count))]


class Jukebox:
    """The jukebox of the set: insert / play / eject. .cell, .point (where its notes spawn), .top."""

    def __init__(self, cell, world=None, collection=None):
        self.cell = tuple(int(c) for c in cell)
        self.world = world
        self.collection = collection
        self.point = (self.cell[0] + NOTE_SPAWN[0], self.cell[1] + NOTE_SPAWN[2], self.cell[2] + NOTE_SPAWN[1])
        self.top = float(self.cell[2] + 1)
        self.center = (self.cell[0] + 0.5, self.cell[1] + 0.5, self.cell[2] + 0.5)
        self.spans = []                   # [(first note frame, last frame, disc)]
        self.bursts = []
        self.ejected = []

    def __repr__(self):
        return "<music.Jukebox at %s>" % (self.cell,)

    def playing_at(self, frame):
        """The disc playing at `frame`, or None."""
        for a, b, disc in self.spans:
            if a - TICK <= frame <= b:
                return disc
        return None

    def play(self, frame_start, frame_end, disc="music_disc_11", camera=None, seed=0, glow=None, first=True):
        """The notes of a playing jukebox from `frame_start` (the tick the song starts) to `frame_end`: one note
        particle every 20 ticks (24 frames) at (0.5, 1.2, 0.5) above the block, its colour value 0..3 of 24 drawn at
        random (green, lime, yellow or orange: JukeboxSongPlayer.spawnMusicParticles); the first ON frame_start
        when `first` (ticksSinceSongStarted 0). A song stops by itself one second after its length (JukeboxSong
        .hasFinished; SONG_SECONDS: 11 = 71 s). Returns the frames the notes appear on."""
        a = float(frame_start)
        length = SONG_SECONDS.get(disc)
        b = float(frame_end)
        if length is not None:                          # JukeboxSong.hasFinished: ticks >= ceil(20 s) + 20
            b = min(b, a + (math.ceil(length * 20.0) + 20 - 1) * TICK)
        rng = np.random.default_rng([int(seed) & 0x7FFFFFFF, int(round(a * 10)) & 0x7FFFFFFF, 61])
        frames = []
        f = a if first else a + JUKEBOX_EVERY_TICKS * TICK
        burst = None
        while f <= b + 1e-6:
            note = int(rng.integers(0, JUKEBOX_NOTES))
            burst = note_particle(self.point, f, note, camera=camera, seed=seed + len(frames), glow=glow,
                                  collection=self.collection, burst=burst)
            frames.append(f)
            f += JUKEBOX_EVERY_TICKS * TICK
        if burst is not None:
            self.bursts.append(burst)
        self.spans.append((a, b, disc))
        return frames

    def insert(self, frame, player=None, disc="music_disc_11", hand="right", until=None, camera=None, seed=0,
               glow=None):
        """A player puts the disc held in `hand` into the jukebox ON `frame` (JukeboxBlock.useItemOn ->
        JukeboxPlayable.tryInsertIntoJukebox): the arm swing, the disc gone from the hand one tick later (the stack
        is consumed; the jukebox model does not change: has_record has the same block model), and the song starts:
        its first note one tick after the click, then one every 24 frames until `until` (default frame + 240) or
        the end of the song. Returns the frames of the notes."""
        if player is not None:
            player.attack(frame, hand)
            player.hold(None, hand=hand, frame=int(math.ceil(frame + TICK)))
        end = frame + 240 if until is None else until
        return self.play(frame + TICK, end, disc=disc, camera=camera, seed=seed, glow=glow)

    def _cancel(self, frame):
        """No note spawns ON or after `frame`; the notes already in the air rise and fade as the game's do."""
        f = int(math.ceil(frame - 1e-6))
        for b in self.bursts:
            _cancel_after(b, f)
        self.spans = [(a, min(e, frame - TICK), d) for a, e, d in self.spans]

    def eject(self, frame, player=None, disc="music_disc_cat", seed=0, land="top", hand="right", until=None,
              camera=None, name=None):
        """A player right-clicks the playing jukebox ON `frame` (JukeboxBlock.useWithoutItem -> popOutTheItem): the
        arm swing, the notes stop (a later play() / insert() starts them again), and one tick later the disc is a
        dropped item at (0.5, 1.01, 0.5) +- 0.35 in x and y above the block, tossed with ItemEntity's random speed
        (+-0.1, 0.2 up, +-0.1 per tick): it rises about half a block, falls back and lies on the jukebox (or drops
        off its side onto the stage), turning and bobbing as every dropped item does (engine.mobs DroppedItem:
        1 radian a second, 0.2 up and down every 3.1 s). land='top' picks, from `seed` on, the first seed whose
        toss stays on the jukebox's top; land='any' takes `seed` as it is. Returns the DroppedItem (.land_frame,
        .still_frame, .rest_pos, .seed, .spawn_point)."""
        from . import mobs

        if player is not None:
            player.attack(frame, hand)
        self._cancel(frame + TICK)
        w = getattr(self.world, "world", self.world)
        if w is None:
            raise ValueError("Jukebox.eject needs the jukebox's world (music.band(v) gives it one)")
        chosen = None
        for k in range(200 if land == "top" else 1):
            s = int(seed) + k
            r = np.random.default_rng([s & 0x7FFFFFFF, 8191, self.cell[0] & 0xFFFF, self.cell[1] & 0xFFFF])
            spawn = (self.cell[0] + 0.5 + (r.random() - 0.5) * EJECT_SPREAD,
                     self.cell[1] + 0.5 + (r.random() - 0.5) * EJECT_SPREAD, self.cell[2] + EJECT_UP)
            vel = (r.random() * 0.2 - 0.1, r.random() * 0.2 - 0.1, ITEM_TOSS[1])
            track = item_track(w, spawn, vel)
            end = track[-1][1]
            on_top = (abs(end[2] - self.top) < 1e-6 and self.cell[0] < end[0] < self.cell[0] + 1
                      and self.cell[1] < end[1] < self.cell[1] + 1)
            if land != "top" or on_top:
                chosen = (s, track)
                break
        if chosen is None:
            raise ValueError("Jukebox.eject: no toss from seed %d on stays on the jukebox" % seed)
        s, track = chosen
        f1 = int(math.ceil(frame + TICK))
        item = mobs.make_dropped_item(disc, collection=self.collection, seed=s, name=name)
        _key_track(item, f1, track)
        item.seed = s
        item.animate(f1, f1 + 240 if until is None else int(until))
        self.ejected.append(item)
        return item

    def stop(self, frame):
        """The song stops ON `frame` (no more notes; the ones in the air live on)."""
        self._cancel(frame)


def _cancel_after(burst, frame):
    """Hide, in an engine.fx Burst, every particle that would appear ON or after `frame` (the ones already shown are
    left to live out their 6 ticks). Returns how many were cancelled."""
    from . import fx

    n = 0
    for p in burst.particles:
        if p["first"] >= frame and p["last"] > p["first"]:
            for path in ("hide_render", "hide_viewport"):
                fx._write(p["object"], path, 0, [p["first"] - 1], [1.0], "CONSTANT")
            p["object"].hide_render = p["object"].hide_viewport = True
            p["last"] = p["first"]
            n += 1
    seen = [p["last"] - 1 for p in burst.particles if p["last"] > p["first"]]
    burst.frame_end = max(seen) if seen else burst.frame
    return n


# ----------------------------------------------------------------------------------------------------
# THE SET (built in the village hook: village.build_village(scene, seed=1, edit=lambda b: music.crammys_set(b)))
# ----------------------------------------------------------------------------------------------------
# Blender cells. The bandstand stands on the WEST side of the square with its back to the well, facing west down
# the west street: the street and its corridor in front are the audience's place and the cameras' (10+ blocks of
# open ground in front, the well's roof and the bell over the back wall behind the players).
STAGE = dict(
    front=-8, back=-5, wall=-4, south=-3, north=3, wing=5,     # platform x -8..-5, y -3..5 (top z 1); wall x -4
    wall_top=3,                                                 # wall z 0..3 (its top 3 blocks above the stage floor)
    floor="red_wool", wall_a="blue_wool", wall_b="light_blue_wool", trim="yellow_wool",
)
HEROES = {                                  # performer -> (note block column (x, y), the block under the note block)
    "zuri": ((-8, 2), "white_wool"),        # guitar
    "kai": ((-8, 1), "gold_block"),         # bells
    "sunny": ((-8, -2), "pumpkin"),         # didgeridoo
}
DRESSING_NOTES = ((-8, -1), (-8, 4), (-8, 5))   # the rest of the front row of note blocks (on the red wool: guitar)
HERO_NOTES = {"zuri": 6, "kai": 10, "sunny": 0}     # the note each hero block is tuned to at the start
JUKEBOX_CELL = (-7, 0, 1)                   # centre stage, right behind the gap in the front row (seen from the front)
PEDESTAL = (-9, -1)                         # oak fence (z 0) + gold block (z 1) on the ground before the stage, one
                                            # block south of the centre line (it would hide the jukebox from the front)
POSTS = {"south": (-8, -3), "north": (-8, 3)}       # 2 oak fences + a lantern; the north one is placed on camera
WALL_LANTERNS = ((-4, -3), (-4, 3))         # lanterns standing on the back wall's top (z 4)
LANE = dict(column=(1, 15), lantern=(1, 17), kai=(2.75, 16.75))  # Kai's doorstep in front of house_f (door at (4, 16))
LIGHT_GROUPS = ("bandstand", "lane")        # Stage.lights groups of the set's lanterns (the placed one: Band.lights)
# the skies the proof stills are made under (a film's SKIES may copy them): the stage faces WEST, so the golden sun
# stands in the south-west (az 240: 120 degrees off the lens of a camera looking east at the stage; nothing tall
# stands that way, the farm is low); the night is the moon of tools/check_hostiles_crammys (az 176, from the west:
# the stage front is moonlit, the lanterns are the warm keys)
SKIES = {
    "gold": dict(preset="golden", az=240.0, el=27.0, bloom=1.0, grade="warm"),
    "night": dict(preset="night", az=176.0, el=21.0, bloom=1.3, grade="cool"),
}

# village anchors that the bandstand covers: moved to the nearest free ground (name -> new 2D spot)
MOVED_ANCHORS = {"square_w": (-9.6, 1.7), "square_4": (-6.4, -4.6), "square_6": (-5.6, 6.6)}


def _wall_block(y, z):
    """The back wall's wool: blue / light blue stripes a block wide, a yellow top row."""
    if z == STAGE["wall_top"]:
        return STAGE["trim"]
    return STAGE["wall_a"] if (y % 2) == 0 else STAGE["wall_b"]


def _new_name(b, name):
    if name in b.v.sets:
        raise ValueError("set piece %r exists already in this village" % name)


def _under_to_dirt(b, x, y):
    """The terrain block under a solid block the set puts on the ground: a dirt path or grass under a full block
    turns to dirt in the game (DirtPathBlock.canSurvive / SpreadingSnowyBlock)."""
    h = b.surface_z(x, y)
    if h != -99 and b.w.block_id(x, y, h - 1) in ("dirt_path", "grass_block"):
        b.w.set(x, y, h - 1, "dirt")


def _entry_after(path, start_point):
    """The part of a village path from the point nearest `start_point` on (a house's entry polyline)."""
    i = min(range(len(path)), key=lambda k: math.dist(path[k][:2], start_point[:2]))
    return [tuple(p) for p in path[i:]]


def bandstand(b, name="bandstand"):
    """In the hook: the Crammys bandstand on the west side of the square (STAGE, HEROES ...). Puts every block into
    the World, its lanterns as light group 'bandstand', re-routes the village paths it stands on, moves the three
    square anchors it covers (MOVED_ANCHORS), registers the anchors bandstand_* and returns the set's dict (also
    Village.sets[name])."""
    _new_name(b, name)
    w, S = b.w, STAGE
    x0, x1, y0, y1 = S["front"], S["back"], S["south"], S["wing"]
    b.allow((PEDESTAL[0], y0, S["wall"], y1))                   # the well's template box and the plaza's paths
    for x in range(PEDESTAL[0] - 1, S["wall"] + 1):
        for y in range(y0 - 1, y1 + 2):
            b.clear_plants(x, y)
    cells = []
    for x in range(x0, x1 + 1):                                 # the platform: one block of wool
        for y in range(y0, y1 + 1):
            _under_to_dirt(b, x, y)
            w.set(x, y, 0, S["floor"])
            cells.append((x, y, 0))
            b.reserved.add((x, y))
    for y in range(y0, y1 + 1):                                 # the back wall
        _under_to_dirt(b, S["wall"], y)
        for z in range(0, S["wall_top"] + 1):
            w.set(S["wall"], y, z, _wall_block(y, z))
            cells.append((S["wall"], y, z))
        b.reserved.add((S["wall"], y))
    notes = {}
    for who, ((x, y), base) in HEROES.items():                  # the hero note blocks on their own base blocks
        w.set(x, y, 0, base)
        ins = instrument(base)
        w.set(x, y, 1, "note_block", {"instrument": ins, "note": str(HERO_NOTES[who]), "powered": "false"})
        notes[who] = dict(cell=(x, y, 1), base=base, instrument=ins, note=HERO_NOTES[who])
    for i, (x, y) in enumerate(DRESSING_NOTES):
        w.set(x, y, 1, "note_block", {"instrument": instrument(S["floor"]), "note": str((5 * i + 3) % NOTES),
                                      "powered": "false"})
        notes["row_%d" % (i + 1)] = dict(cell=(x, y, 1), base=S["floor"], instrument=instrument(S["floor"]),
                                         note=(5 * i + 3) % NOTES)
    jx, jy, jz = JUKEBOX_CELL
    w.set(jx, jy, jz, "jukebox", {"has_record": "false"})
    for key, (x, y) in POSTS.items():                           # lantern posts: two fences, a lantern on top
        w.set(x, y, 1, "oak_fence")
        w.set(x, y, 2, "oak_fence")
        if key != "north":
            b.torch((x, y, 3), "lantern", group="bandstand")
    for x, y in WALL_LANTERNS:
        b.torch((x, y, S["wall_top"] + 1), "lantern", group="bandstand")
    px, py = PEDESTAL                                           # the trophy pedestal before the stage
    _under_to_dirt(b, px, py)
    w.set(px, py, 0, "oak_fence")
    w.set(px, py, 1, "gold_block")
    b.reserved.add((px, py))
    moved = _reroute_square(b)
    A = _stage_anchors(b, name)
    res = dict(name=name, cells=cells, notes=notes, jukebox=JUKEBOX_CELL, pedestal=(px, py, 1),
               pedestal_top=(px + 0.5, py + 0.5, 2.0), posts=dict(POSTS), last_lantern=(POSTS["north"] + (3,)),
               wall_lanterns=[(x, y, S["wall_top"] + 1) for x, y in WALL_LANTERNS], moved=moved, anchors=A,
               stage=dict(S), floor_z=1.0)
    b.v.sets[name] = res
    return res


def _reroute_square(b):
    """The village paths that crossed the bandstand, registered again around it; the anchors it covers moved.
    Returns {name: what changed}."""
    v = b.v
    P = v.paths
    out = {}
    for key, spot in MOVED_ANCHORS.items():
        if key in v.anchors:
            old = v.anchors[key]
            b.anchor(key, spot, yaw_to(spot, v.anchors["bell"]), replace=True)
            out[key] = (tuple(round(c, 2) for c in old[:2]), spot)
    door_c, door_e = v.anchors.get("house_c_door_out"), v.anchors.get("house_e_door_out")
    if "square_to_house_c" in P and door_c is not None:
        entry = _entry_after(P["square_to_house_c"], door_c)
        b.path("square_to_house_c", [(-3.5, -6.0), (-6.6, -4.6), (-9.5, -4.3), (-9.5, 2.5), (-8.5, 3.2),
                                      (-8.5, 6.5)] + entry[1:], replace=True)
        out["square_to_house_c"] = "west of the bandstand, through the corridor before it"
    if "square_to_house_d" in P:
        entry = _entry_after(P["square_to_house_d"], (-17.0, 0.4))
        b.path("square_to_house_d", [(-5.0, -7.0), (-6.0, -4.6), (-9.5, -4.4), (-9.5, -1.2), (-10.6, -0.4)]
               + entry, replace=True)
        out["square_to_house_d"] = "round the bandstand's south end"
    if "square_to_house_e" in P and door_e is not None:
        entry = _entry_after(P["square_to_house_e"], door_e)
        b.path("square_to_house_e", [(-1.5, -6.5), (3.5, -4.5), (3.5, 3.5), (-1.6, 9.5)] + entry, replace=True)
        out["square_to_house_e"] = "east of the well"
    if "square_loop" in P:
        b.path("square_loop", [(0.5, -7.5), (6.3, -6.5), (6.9, 0.0), (6.0, 6.5), (0.0, 7.0), (-6.5, 6.6),
                               (-8.5, 6.5), (-8.5, 3.2), (-9.5, 2.5), (-9.5, -4.2), (-6.0, -4.6), (-6.5, -6.5),
                               (0.5, -7.5)], replace=True)
        out["square_loop"] = "round the bandstand through the corridor before it"
    if "street_west" in P:
        pts = [p for p in P["street_west"] if p[0] < -10.0]
        b.path("street_west", [(-9.6, 1.4)] + [p[:2] for p in pts], replace=True)
        out["street_west"] = "starts at the corridor before the bandstand"
    return out


def _stage_anchors(b, name):
    """The standing spots and look targets of the bandstand (Village.anchors '<name>_<key>'). Returns {key: point}."""
    v = b.v
    F = 1.0                                                     # the stage floor
    A = {}

    def put(key, p, look=None, yaw=None, ground=False):
        if yaw is None and look is not None:
            yaw = yaw_to(p, look)
        if len(p) == 2 and not ground:
            p = (p[0], p[1], F)                                 # on the stage floor (2D on the ground: walk height)
        full = b.anchor("%s_%s" % (name, key), p, yaw, replace=True)
        A[key] = full
        return full

    def target(key, p):
        v.anchors["%s_%s_target" % (name, key)] = tuple(float(c) for c in p)
        A[key + "_target"] = tuple(float(c) for c in p)

    for who, ((x, y), _base) in HEROES.items():
        target("note_" + who, (x + 0.5, y + 0.5, 1.5))
        target("base_" + who, (x + 0.5, y + 0.5, 0.5))
    jx, jy, jz = JUKEBOX_CELL
    jc = (jx + 0.5, jy + 0.5)                                   # the jukebox's centre: what everybody faces
    target("jukebox", (jx + 0.5, jy + 0.5, jz + 0.5))
    target("jukebox_top", (jx + 0.5, jy + 0.5, jz + 1.25))
    target("pedestal", (PEDESTAL[0] + 0.5, PEDESTAL[1] + 0.5, 2.25))
    target("center", (-6.0, 0.5, 2.4))
    target("wing", (-6.5, 4.6, 2.0))
    # performers at their note blocks: 0.4 behind the block's back face and 0.35 to its side, facing it
    put("zuri", (-6.6, 2.85), look=(-7.5, 2.5))
    put("kai", (-6.6, 1.65), look=(-7.5, 1.5))
    put("sunny", (-6.6, -1.3), look=(-7.5, -1.5))
    put("noor", (-5.45, 2.45), yaw=yaw_of("west"))
    put("alex", (-5.5, 1.45), look=jc)                          # beside the jukebox, north-east of it
    put("alex_eject", (-5.6, 0.5), look=jc)                     # beat 8: behind the jukebox, facing the audience
    put("steve_center", (-5.6, 1.25), yaw=yaw_of("west"))       # beat 24: centre stage behind the jukebox, 0.75
                                                                # north of its notes (they rise in front of a face)
    put("steve_jukebox", (-6.5, 1.6), look=jc)                  # beats 19-21: at the jukebox, its north side
    put("alex_beside", (-5.6, 1.65), yaw=yaw_of("south"))       # beat 20: beside him, her disc held out
    put("steve_wing", (-6.4, 5.4), look=(-6.4, 0.0))
    # beat 19: the half circle beyond the jukebox (south of it), facing the wing, staggered
    for i, p in enumerate(((-6.65, -0.7), (-6.0, -1.65), (-5.1, -1.9), (-4.6, -0.8)), 1):
        put("half_%d" % i, p, look=(-6.4, 5.0))
    # beats 22-24: two groups flanking the jukebox, all facing it: from the front their faces are three-quarter
    for i, p in enumerate(((-6.45, 2.2), (-5.55, 2.65), (-4.7, 2.95)), 1):     # (clear of b24's medium on Steve)
        put("flank_n%d" % i, p, look=jc)
    for i, p in enumerate(((-6.45, -0.75), (-5.6, -1.25), (-4.75, -1.6)), 1):
        put("flank_s%d" % i, p, look=jc)
    # beat 18: the three-shot, a row across the stage's south half facing the jukebox (Steve between them)
    put("three_sunny", (-5.6, -0.65), look=jc)
    put("three_steve", (-5.3, -1.55), look=jc)
    put("three_noor", (-5.0, -2.45), look=jc)
    # on the ground in front of the stage (the corridor before it and the street)
    put("steve_foot", (-9.75, -1.15), look=(jx + 0.5, jy + 0.5, 2.0), ground=True)   # beat 4: below the stage
    put("steve_watch", (-9.6, -2.3), look=(jx + 0.5, jy + 0.5, 2.0), ground=True)    # beat 8: at its foot
    put("steve_front", (-11.2, -0.3), look=(-16.5, -1.6), ground=True)              # beat 1
    put("steve_kai", (-9.65, 0.05), look=(-7.5, 1.5), ground=True)     # beat 3: his shoulder in the foreground
    for i, y in enumerate((2.3, 1.05, -0.2, -1.45, -2.7), 1):  # beat 6: the line before the stage, facing west
        put("line_%d" % i, (-10.2, y), yaw=yaw_of("west"), ground=True)
    put("alex_post", (-7.0, 3.25), look=(-7.5, 3.5, 3.0))       # beat 5: Alex places the last lantern
    return A


def lane_set(b, name="lane"):
    """In the hook: Kai's doorstep dressing in front of house_f (his gold block with a note block on it south of the
    doorstep, a lantern on a post of two oak fences north of it: light group 'lane'), facing the narrator's front door (house_e, across the exit road). Registers
    the anchors lane_* and the paths lane_home (from the square side up the road and in at house_e's door) and
    lane_to_square (down the road from the north to the square); re-routes square_to_house_f past the lantern."""
    _new_name(b, name)
    w, v = b.w, b.v
    (cx, cy), (lx, ly) = LANE["column"], LANE["lantern"]
    b.allow((min(cx, lx), min(cy, ly), max(cx, lx), max(cy, ly)))
    w.set(cx, cy, -1, "dirt")                                   # the path under a full block turns to dirt
    w.set(cx, cy, 0, "gold_block")
    w.set(cx, cy, 1, "note_block", {"instrument": instrument("gold_block"), "note": "12", "powered": "false"})
    w.set(lx, ly, -1, "dirt")                                   # (a fence keeps no dirt path under it either)
    w.set(lx, ly, 0, "oak_fence")                               # the lantern on a post of two fences (as the
    w.set(lx, ly, 1, "oak_fence")                               # bandstand's): just above Kai's head from the
    b.torch((lx, ly, 2), "lantern", group="lane")               # lane camera
    door_f = v.anchors.get("house_f_door_out")
    if "square_to_house_f" in v.paths and door_f is not None:
        entry = _entry_after(v.paths["square_to_house_f"], door_f)
        b.path("square_to_house_f", [(1.5, -7.0), (6.8, -3.0), (7.0, 5.0), (1.6, 9.5), (0.4, 10.5), (0.4, 16.4)]
               + entry, replace=True)
    A = {}
    A["kai"] = b.anchor(name + "_kai", LANE["kai"], yaw_of("west"), replace=True)
    A["from_south"] = b.anchor(name + "_from_south", (0.4, 9.8), yaw_of("north"), replace=True)
    A["from_north"] = b.anchor(name + "_from_north", (0.4, 22.5), yaw_of("south"), replace=True)
    door_e = v.anchors["house_e_door_out"]
    entry_e = _entry_after(v.paths["square_to_house_e"], door_e)
    home = b.path(name + "_home", [(0.4, 9.8), (0.3, 13.6)] + entry_e, replace=True)
    to_square = b.path(name + "_to_square", [(0.4, 22.5), (0.4, 12.0), (0.2, 8.0), (-2.0, 6.0)], replace=True)
    v.anchors[name + "_note_target"] = (cx + 0.5, cy + 0.5, 1.5)
    v.anchors[name + "_door_target"] = tuple(v.anchors["house_e_door"])
    res = dict(name=name, column=(cx, cy), lantern=(lx, ly, 2), anchors=A, home=home, to_square=to_square,
               narrator_door="house_e", kai_door="house_f")
    b.v.sets[name] = res
    return res


def crammys_set(b):
    """In the hook: everything this module builds for "The Crammys": bandstand(b) and lane_set(b)."""
    return dict(bandstand=bandstand(b), lane=lane_set(b))


# ----------------------------------------------------------------------------------------------------
# after the build: the handles of the set
# ----------------------------------------------------------------------------------------------------
class LastLantern:
    """The lantern on the north front post, placed on camera (beat 5). A block of its own (engine.breaking
    Breakable) and its own point light, both there from the start unless place(frame) is called. Stage.lights does
    not touch its light: Band.lights does (or level()). show(frame, visible) as every Stage cast member (block and
    light are rendered only while shown AND placed)."""

    def __init__(self, cell, world, collection):
        from . import breaking, props

        self.cell = tuple(int(c) for c in cell)
        self.name = "music_last_lantern"
        self.block = breaking.place_block(collection, "lantern", self.cell, {"hanging": "false"}, world=world,
                                          name=self.name)
        self.light = props.make_light("lantern", collection)
        self.light.location = props.flame_position(self.cell, "lantern", {"hanging": "false"})
        self.light.name = "light_music_last_lantern"
        self.light["group"] = "music_last"
        self.base_energy = float(self.light["base_energy"])
        self.placed = None
        self._levels = {}                 # frame -> scale (CONSTANT)
        self._shown = {}                  # frame -> bool (Stage.finish)
        self._rekey()

    def objects(self):
        """The block's objects and the light."""
        return list(self.block.objects) + [self.light]

    def there_at(self, frame):
        """True when the lantern block stands on its post at `frame`."""
        return self.placed is None or frame >= self.placed

    def show(self, frame, visible=True):
        """Per-shot visibility (Stage.finish calls it when the lantern is in st.cast)."""
        self._shown[int(round(frame))] = bool(visible)
        self.block.show(frame, visible)
        self._rekey()

    def place(self, frame, player=None, hand="right"):
        """The lantern appears ON `frame` (placing a block: the game shows it at once, no animation, no particles)
        and its light comes on; player = who places it (the arm swing on the same frame: BlockItem.place is the
        use-item swing). Returns the frame."""
        self.placed = int(round(frame))
        self.block._there0 = False                          # (what breaking.place_block(frame=...) does)
        self.block._there = {self.placed: True}
        self.block._rekey()
        if player is not None:
            player.attack(self.placed, hand)
        self._rekey()
        return self.placed

    def level(self, frame, scale=1.0):
        """The light's strength from `frame` on: base energy (a lantern's 140 W) x scale (CONSTANT)."""
        self._levels[int(round(frame))] = float(scale)
        self._rekey()

    def _scale_at(self, frame):
        best, out = None, 1.0
        for f, s in self._levels.items():
            if f <= frame and (best is None or f > best):
                best, out = f, s
        return out

    def _shown_at(self, frame):
        best, out = None, True
        for f, s in self._shown.items():
            if f <= frame and (best is None or f > best):
                best, out = f, s
        return out

    def _rekey(self):
        from . import fx

        frames = sorted(set(self._levels) | set(self._shown) | ({self.placed} if self.placed is not None else set()))
        ob = self.light
        if not frames:
            ob.data.energy = self.base_energy
            ob.hide_render = False
            return
        first = frames[0] - 1
        keys_f = [first] + frames
        on = [self.there_at(f) and self._shown_at(f) and self._scale_at(f) > 0.0 for f in keys_f]
        en = [self.base_energy * max(self._scale_at(f), 0.0) for f in keys_f]
        fx._write(ob, "hide_render", 0, keys_f, [0.0 if o else 1.0 for o in on], "CONSTANT")
        fx._write(ob, "hide_viewport", 0, keys_f, [0.0 if o else 1.0 for o in on], "CONSTANT")
        fx._write(ob.data, "energy", 0, keys_f, en, "CONSTANT")


class Band:
    """The bandstand and the lane after the build (music.band(v)): see the module docstring."""

    def __init__(self, v, name="bandstand", lane="lane", collection=None):
        from . import fx

        if name not in v.sets:
            raise KeyError("music.band: the village has no %r set: build it with edit=music.crammys_set" % name)
        self.v = v
        self.set = v.sets[name]
        self.lane = v.sets.get(lane)
        self.name = name
        col = collection or fx._collection(None)
        self.collection = col
        self.A = {k: v.anchors[k] for k in v.anchors if k.startswith(name + "_") or k.startswith((lane or "~") + "_")}
        self.A = {k.replace(name + "_", "", 1) if k.startswith(name + "_") else k: p for k, p in self.A.items()}
        self.yaw = {}
        for k in v.yaws:
            if k.startswith(name + "_"):
                self.yaw[k.replace(name + "_", "", 1)] = v.yaws[k]
            elif lane and k.startswith(lane + "_"):
                self.yaw[k] = v.yaws[k]
        w = v.world
        self.notes = {}
        for key, d in self.set["notes"].items():
            c = d["cell"]
            above = w.block_id(c[0], c[1], c[2] + 1)
            self.notes[key] = NoteBlock(key, c, d["base"], d["note"], above)
        if self.lane is not None:
            cx, cy = self.lane["column"]
            self.notes["lane"] = NoteBlock("lane", (cx, cy, 1), "gold_block", 12)
        self.jukebox = Jukebox(self.set["jukebox"], world=v, collection=col)
        self.last_lantern = LastLantern(self.set["last_lantern"], w, col)
        self.pedestal_top = self.set["pedestal_top"]
        self.cameras = cameras(self.A)
        self._totem = None

    def __repr__(self):
        return "<music.Band %s: %d note blocks, jukebox %s>" % (self.name, len(self.notes), self.jukebox.cell)

    def totem(self, frame_start, frame_end, picked=None, face=None, age=40.0):
        """The totem of undying lying on the pedestal's gold block as a dropped item, turning (1 radian a second) and
        bobbing (0.2 block every 3.1 s) from `frame_start` to `frame_end`; picked = the frame it is taken (the
        pedestal is empty from then on, beat 24); face = a point or camera position the sprite's face should turn
        toward at frame_start (DroppedItem.face). Returns the engine.mobs DroppedItem (st.cast[item.name] = item and
        st.use(shot, item) only if it must be hidden in some shots)."""
        from . import mobs

        if self._totem is None:
            self._totem = mobs.make_dropped_item("totem_of_undying", collection=self.collection, name="music_totem")
        t = self._totem
        t.place(frame_start, self.pedestal_top, age=age)
        if face is not None:
            t.face(frame_start, face)
        t.animate(frame_start, frame_end)
        if picked is not None:
            t.pick_up(picked)
        return t

    def lights(self, st, shot, scale=1.0, stage=None, lane=None, at=None, **kw):
        """Stage.lights for a shot plus the placed lantern: every village light x scale, the bandstand's lanterns
        (group 'bandstand' and the placed one) x stage (default scale), Kai's doorstep lantern (group 'lane') x lane
        (default scale). Other Stage.lights keywords pass through (near, radius, extra, inside, groups)."""
        groups = dict(kw.pop("groups", None) or {})
        groups.setdefault("bandstand", scale if stage is None else stage)
        groups.setdefault("lane", scale if lane is None else lane)
        st.lights(shot, scale=scale, groups=groups, at=at, **kw)
        self.last_lantern.level(shot.frame_start if at is None else at, groups["bandstand"])

    def tap(self, who, player, frame, **kw):
        """notes[who].tap(player, frame, **kw): the player plays his note block (see NoteBlock.tap)."""
        return self.notes[who].tap(player, frame, **kw)


def band(v, name="bandstand", lane="lane", collection=None):
    """The handles of the set after village.build_village(..., edit=music.crammys_set): Band (anchors A / yaw,
    cameras, notes, jukebox, last_lantern, totem(), lights())."""
    return Band(v, name, lane, collection)


# ----------------------------------------------------------------------------------------------------
# held items, the arm held out, the applause
# ----------------------------------------------------------------------------------------------------
BLOCK_ITEMS = ("gold_block", "pumpkin", "note_block", "white_wool", "jukebox", "lantern")
FLAT_ITEMS = ("music_disc_11", "music_disc_cat", "goat_horn", "totem_of_undying")


def hold(player, item, hand="right", frame=None):
    """engine.players Player.hold for this film's items: block items ('gold_block', 'pumpkin', 'note_block',
    'white_wool' ...) are drawn as the game draws a block in a hand (models/block/block.json display
    thirdperson_righthand: rotation (75, 45, 0), translation (0, 2.5, 0), scale 0.375); discs, the goat horn and
    the totem as flat sprite items (item/generated: translation (0, 3, 1), scale 0.55; the goat horn has its own
    display, rotation (0, 180, 0)). Returns the item object (a focus target)."""
    return player.hold(item, hand=hand, frame=frame)


def _shoulder(player, side, frame):
    scene = bpy.context.scene
    cur, sub = scene.frame_current, scene.frame_subframe
    scene.frame_set(int(math.floor(frame)))
    arm = player.arm_r if side == "r" else player.arm_l
    p = arm.matrix_world.translation.copy()
    scene.frame_set(cur, subframe=sub)
    return p


def present(player, frame_start, frame_end, target, hand="right", ease=6):
    """Hold the arm straight out toward `target` (a point, e.g. the camera position) from frame_start to frame_end:
    what a player does to show the lens the face of what he holds (the story's beats 6, 20, 24). The arm is
    raised (ease frames) to point at the target from the shoulder and held; it comes back to the item pose after
    frame_end. Not a game pose (third-person players only raise an arm for bows, shields, the horn and the
    spyglass): a film gesture. A flat item then shows the lens its face (as CONTRACT.md's emerald from above).
    Returns the item object in that hand (or None)."""
    side = "r" if str(hand).lower().startswith("r") else "l"
    if hasattr(target, "matrix_world"):
        target = target.matrix_world.translation
    t = Vector(tuple(float(c) for c in target))
    s = _shoulder(player, side, frame_start)
    yaw = player.yaw_at(frame_start)
    fwd = Vector((math.sin(yaw), -math.cos(yaw), 0.0))
    left = Vector((math.cos(yaw), math.sin(yaw), 0.0))
    d = t - s
    F, L, U = d.dot(fwd), d.dot(left), d.z
    a = math.atan2(L, F)
    e = math.atan2(U, math.hypot(F, L))
    x_rot = -math.pi / 2.0 - e

    def fn(_pitch, _yaw, _f):
        return (x_rot, -a)

    player._pose_arm(side, frame_start, frame_end, fn, ease, crouch=False)
    return player.item(hand, frame_start)


def clap(player, frame, count=6, every=4, down=2):
    """The players' applause: `count` fast crouches from `frame`, one every `every` frames, each held `down` frames
    (engine.players sneak: the game's crouch pose snaps on and off, 2 px lower, the torso tipped 0.5 rad). Returns
    the frame he stands up for the last time."""
    f = int(frame)
    for _k in range(int(count)):
        player.sneak(f, True)
        player.sneak(f + int(down), False)
        f += int(every)
    return f - int(every) + int(down)


def hero_item(item_id, collection=None):
    """A flat item on its own (the disc for an insert shot): engine.mcassets.item_object, 1 block = 16 texels, its
    face toward -Y, centred on its origin. Returns the Object (place and key it yourself)."""
    from . import mcassets as mc

    ob = mc.item_object(item_id)
    if collection is not None and ob.name not in collection.objects:
        collection.objects.link(ob)
    return ob


# ----------------------------------------------------------------------------------------------------
# suggested cameras (checked with the proof stills of tools/music_proof.py)
# ----------------------------------------------------------------------------------------------------
def cameras(A=None):
    """name -> dict(pos, target, lens, fstop, focus, beat[, pos1, target1]) for the beats on this module's sets
    (golden hour and night alike; Shot.move(pos, target, pos1, target1), Shot.lens(lens, fstop), Shot.focus)."""
    jt = (-6.5, 0.5, 2.0)
    cams = {
        # 1: low, long lens, slow push in; Steve (steve_front) sharp, the stage soft behind him
        "b1": dict(pos=(-16.2, -0.2, 1.0), target=(-6.6, 0.8, 2.3), pos1=(-15.4, -0.12, 1.05),
                   target1=(-6.6, 0.8, 2.3), lens=40.0, fstop=2.0, focus=(-11.2, -0.3, 1.6), beat=1),



        # 2: close on Zuri's note block on its white wool, then tilt up to her face
        "b2": dict(pos=(-10.9, 3.4, 1.05), target=(-7.5, 2.5, 1.15), target1=(-6.6, 2.85, 2.55),
                   lens=40.0, fstop=2.2, focus=(-7.5, 2.5, 1.0), beat=2),

        # 3: the mirror: past Steve's soft shoulder (steve_foot) to Kai's note block on gold, pull to his face
        "b3": dict(pos=(-10.7, -0.1, 1.45), target=(-7.5, 1.5, 1.4), lens=45.0, fstop=2.2,
                   focus=(-7.5, 1.5, 1.2), beat=3),




        # 4: static wide of the stage (Sunny at the far end, Steve below it)
        "b4": dict(pos=(-16.5, 0.2, 1.6), target=(-6.6, 0.6, 2.0), lens=30.0, fstop=5.6, focus=(-7.0, 0.5, 2.0),
                   beat=4),


        # 5: close on the totem above the pedestal, rising and pulling back to the whole bandstand
        "b5": dict(pos=(-9.75, -0.5, 2.6), target=(-8.5, -0.5, 2.38), pos1=(-18.5, 0.3, 3.9),
                   target1=(-6.4, 0.6, 2.1), lens=35.0, fstop=2.8, focus=(-8.5, -0.5, 2.35), beat=5),




        # 6: travelling along the line beside the stage (line_1 .. line_5 = Steve) at hand height
        "b6": dict(pos=(-13.0, 3.3, 1.5), target=(-10.2, 2.3, 1.3), pos1=(-13.0, -1.7, 1.5),
                   target1=(-10.2, -2.7, 1.3), lens=35.0, fstop=2.8, focus=(-10.2, 2.3, 1.3), beat=6),

        # 8: over Steve's shoulder (steve_foot) at the jukebox: the ejected disc turning above it
        "b8": dict(pos=(-10.42, -3.78, 1.95), target=(-6.5, 0.5, 2.4), lens=40.0, fstop=2.4,
                   focus=(-6.5, 0.5, 2.4), beat=8),




        # 18: from the front of the stage at head height (its north-west corner), a medium three-shot: Sunny,
        # Steve, Noor (three_*) facing the jukebox
        "b18": dict(pos=(-10.2, -1.9, 2.75), target=(-5.3, -1.55, 2.45), lens=35.0, fstop=3.2,
                    focus=(-5.3, -1.55, 2.5), beat=18),



        # 19: from the wing, behind and above Steve walking to the jukebox; the half circle beyond it facing us
        "b19": dict(pos=(-6.2, 6.4, 3.2), target=(-5.9, -0.9, 2.0), lens=32.0, fstop=4.0,
                    focus=(-5.9, -0.9, 2.0), beat=19),


        # 20: close from across the jukebox: Steve's disc face-on to the lens (steve_jukebox, present())
        "b20": dict(pos=(-6.45, -2.6, 2.45), target=(-6.45, 1.0, 2.4), lens=40.0, fstop=2.4,
                    focus=(-6.45, 0.95, 2.45), beat=20),


        # 21: the jukebox sharp in the foreground, notes rising; push past it to Steve beside it
        "b21": dict(pos=(-6.8, -1.9, 2.25), target=(-6.5, 0.5, 2.05), pos1=(-6.75, -1.2, 2.4),
                    target1=(-6.5, 1.6, 2.6), lens=32.0, fstop=2.4, focus=(-6.5, 0.5, 2.05), beat=21),



        # 22: the one locked-off frontal wide of the whole stage
        "b22": dict(pos=(-15.5, 0.6, 3.0), target=(-6.0, 0.6, 2.3), lens=30.0, fstop=5.6, focus=(-6.2, 0.5, 2.2),
                    beat=22),


        # 23: from beside the jukebox (south), along the row of faces on the north flank
        "b23": dict(pos=(-7.7, -0.4, 2.6), target=(-5.2, 2.7, 2.5), lens=30.0, fstop=3.2,
                    focus=(-6.45, 2.2, 2.6), beat=23),



        # 24: medium on Steve centre stage, facing the lens, the totem held out; pull back to the clapping five
        "b24": dict(pos=(-9.8, 1.15, 2.55), target=(-5.6, 1.25, 2.45), pos1=(-14.5, 0.9, 2.9),
                    target1=(-5.8, 0.7, 2.2), lens=45.0, fstop=2.8, focus=(-5.6, 1.25, 2.5), beat=24),


        # 7 and 17: from Kai's doorstep (lane_kai), past his head, across the lane to the narrator's door
        "lane": dict(pos=(3.84, 16.3, 1.75), target=(-4.5, 16.0, 1.2), lens=20.0, fstop=2.8,
                     focus=(1.5, 15.5, 1.2), beat=7),


        # proofs: each hero note block close (with its base block), the held block items, the horn, the jukebox,
        # the dropped discs, the applause
        "note_zuri": dict(pos=(-12.6, 3.3, 1.55), target=(-7.5, 2.5, 1.55), lens=50.0, fstop=4.0,
                          focus=(-7.5, 2.5, 1.5), beat=2),

        "note_kai": dict(pos=(-12.6, 1.2, 1.55), target=(-7.5, 1.5, 1.55), lens=50.0, fstop=4.0,
                         focus=(-7.5, 1.5, 1.5), beat=3),

        "note_sunny": dict(pos=(-12.3, -3.4, 1.55), target=(-7.5, -1.5, 1.55), lens=50.0, fstop=4.0,
                           focus=(-7.5, -1.5, 1.5), beat=4),

        "held": dict(pos=(-13.9, 1.3, 1.55), target=(-10.2, 1.1, 1.2), lens=28.0, fstop=4.0,
                     focus=(-10.2, 1.05, 1.2), beat=6),


        "horn": dict(pos=(-8.9, 1.2, 2.55), target=(-5.45, 2.45, 2.6), lens=55.0, fstop=2.8,
                     focus=(-5.45, 2.45, 2.6), beat=1),
        "jukebox": dict(pos=(-9.0, -1.6, 2.7), target=(-6.5, 0.5, 2.3), lens=45.0, fstop=4.0,
                        focus=(-6.5, 0.5, 2.2), beat=8),

        "discs_drop": dict(pos=(-10.9, 0.5, 2.75), target=(-7.6, -0.3, 2.2), lens=40.0, fstop=4.0,
                           focus=(-7.6, -0.3, 2.2), beat=16),




        "discs_hero": dict(pos=(-9.75, 0.52, 2.42), target=(-7.75, 0.52, 2.35), lens=40.0, fstop=4.0,
                           focus=(-7.75, 0.52, 2.35), beat=20),


        "meadow_disc": dict(pos=(-0.9, 34.0, 0.65), target=(0.7, 36.4, 0.1), lens=40.0, fstop=2.8,
                            focus=(0.7, 36.4, 0.2), beat=16),

        "clap": dict(pos=(-10.5, 1.2, 2.6), target=(-5.6, 2.2, 2.0), lens=35.0, fstop=4.0,
                     focus=(-5.6, 2.2, 2.0), beat=24),

    }
    return cams


# ----------------------------------------------------------------------------------------------------
# self-test
# ----------------------------------------------------------------------------------------------------
def _check():
    """The numbers against the classes, the set in the village, the calls' keys. Returns the list of failures."""
    import sys

    from . import blocks, fx, players, quick, village

    bad = []

    def ok(label, cond, detail=""):
        if not cond:
            bad.append(label)
        print("%-4s %s%s" % ("OK" if cond else "FAIL", label, ("  [%s]" % detail) if detail else ""))
        sys.stdout.flush()

    # ---- numbers (NoteParticle, NoteBlock, JukeboxSongPlayer, JukeboxBlockEntity, ItemEntity) ----
    c0, c24 = note_colour(0), note_colour(24)
    ok("note 0 is green (0.35, 0.91, 0) and note 24 wraps to the same colour", all(abs(a - b) < 1e-3 for a, b in
       zip(c0, (0.35, 0.35 + 0.65 * math.sin(2 * math.pi / 3), 0.0))) and all(abs(a - b) < 1e-6 for a, b in
                                                                                 zip(c0, c24)), "%s" % (c0,))
    cols = [_rgb8(note_colour(n)) for n in range(24)]
    ok("the 24 notes 0..23 have 24 different colours", len(set(cols)) == 24)
    jb = [_rgb8(note_colour(n)) for n in range(JUKEBOX_NOTES)]
    ok("a jukebox's notes (0..3 of 24) run green -> lime -> yellow -> orange, no blue",
       jb[0][1] > jb[0][0] and jb[3][0] > jb[3][1] and all(c[2] == 0 for c in jb), "%s" % (jb,))
    ok("note pitch: note 12 = 1.0, note 0 = 0.5, note 24 = 2.0",
       abs(note_pitch(12) - 1) < 1e-9 and abs(note_pitch(0) - 0.5) < 1e-9 and abs(note_pitch(24) - 2) < 1e-9)
    ok("a note rises 0.54 block in its 6 ticks (0.2 x 0.66^k)", abs(note_rise() - 0.5396) < 1e-3, "%.4f" % note_rise())
    ins = {b: instrument(b) for b in ("white_wool", "red_wool", "gold_block", "pumpkin", "stone", "dirt", "oak_planks")}
    ok("instruments from the block below: wool guitar, gold bell, pumpkin didgeridoo, stone basedrum, dirt harp, "
       "planks bass", ins == {"white_wool": "guitar", "red_wool": "guitar", "gold_block": "bell",
                              "pumpkin": "didgeridoo", "stone": "basedrum", "dirt": "harp", "oak_planks": "bass"},
       "%s" % ins)
    ok("a mob head above wins (worksAboveNoteBlock)", instrument("gold_block", "zombie_head") == "zombie")

    # ---- the set in the village ----
    scene = quick.reset()
    quick.setup(scene, res=(270, 480), samples=1)
    v = village.build_village(scene, seed=1, edit=crammys_set)
    ok("the village with the set builds without a problem (Village.validate: anchors free, paths open)",
       not v.edit_problems, "; ".join(v.edit_problems))
    w = v.world
    bd = band(v)
    for who, ((x, y), base) in HEROES.items():
        st_ = w.get(x, y, 1)
        ok("%s's note block stands on %s, with air above it (NoteBlock.playNote needs air), instrument %s" % (
            who, base, bd.notes[who].instrument), st_ is not None and st_[0] == "note_block"
           and w.block_id(x, y, 0) == base and w.get(x, y, 2) is None
           and st_[1].get("instrument") == bd.notes[who].instrument)
    for key, n in bd.notes.items():
        if w.get(n.cell[0], n.cell[1], n.cell[2] + 1) is not None:
            ok("note block %s has air above it" % key, False)
    jx, jy, jz = JUKEBOX_CELL
    ok("the jukebox stands centre stage behind the gap of the front row (seen from the front)",
       w.block_id(jx, jy, jz) == "jukebox" and w.get(jx - 1, jy, jz) is None and w.block_id(jx, jy, 0) == STAGE["floor"])
    px, py = PEDESTAL
    ok("the pedestal: an oak fence with a gold block on it before the stage, the totem's rest at z 2.0",
       w.block_id(px, py, 0) == "oak_fence" and w.block_id(px, py, 1) == "gold_block"
       and abs(bd.pedestal_top[2] - 2.0) < 1e-9)
    lights = {g: len(obs) for g, obs in v.lights.items() if g in LIGHT_GROUPS}
    ok("the set's lanterns are lights in their own groups (bandstand 3 + the placed one, lane 1)",
       lights.get("bandstand") == 3 and lights.get("lane") == 1, "%s" % lights)
    cx, cy = LANE["column"]
    lx, ly = LANE["lantern"]
    ok("Kai's doorstep: gold block + note block, a lantern on two fences, house_f's door behind him",
       w.block_id(cx, cy, 0) == "gold_block" and w.block_id(cx, cy, 1) == "note_block"
       and w.block_id(lx, ly, 2) == "lantern" and w.block_id(lx, ly, 1) == "oak_fence"
       and math.dist(bd.A["lane_kai"][:2], v.anchors["house_f_door_out"][:2]) < 1.6)
    stage_spots = ["zuri", "kai", "sunny", "noor", "alex", "steve_center", "steve_jukebox", "alex_beside",
                   "steve_wing", "three_sunny", "three_steve", "three_noor"] + ["flank_n%d" % i for i in (1, 2, 3)] + \
                  ["flank_s%d" % i for i in (1, 2, 3)] + ["half_%d" % i for i in (1, 2, 3, 4)]
    ok("performers stand on the stage floor (z 1.0), the others on the ground",
       all(abs(bd.A[k][2] - 1.0) < 1e-9 for k in stage_spots)
       and all(abs(bd.A[k][2] - v.ground(bd.A[k][0], bd.A[k][1])) < 0.07 for k in
               ("steve_foot", "steve_front", "steve_kai", "steve_watch", "line_1", "line_5")))

    def clear_of_blocks(p, r=0.3, h=1.8):
        for dx in (-r, 0.0, r):
            for dy in (-r, 0.0, r):
                for dz in (0.1, 0.9, h - 0.05):
                    c = (int(math.floor(p[0] + dx)), int(math.floor(p[1] + dy)), int(math.floor(p[2] + dz)))
                    if w.is_solid(*c):
                        return False
        return True

    blocked = [k for k in stage_spots + ["steve_foot", "steve_front", "steve_kai", "steve_watch"]
               + ["line_%d" % i for i in range(1, 6)] if not clear_of_blocks(bd.A[k])]
    ok("every standing spot leaves a 0.6-wide, 1.8-tall body clear of blocks", not blocked, "%s" % blocked)
    for i, j in (("flank_n1", "flank_n2"), ("flank_n2", "flank_n3"), ("flank_s1", "flank_s2"),
                 ("flank_s2", "flank_s3"), ("three_sunny", "three_steve"), ("three_steve", "three_noor")):
        if math.dist(bd.A[i][:2], bd.A[j][:2]) < 0.7:
            ok("%s and %s at least 0.7 apart" % (i, j), False)
    inside = [k for k, c in bd.cameras.items() if w.is_solid(*(int(math.floor(a)) for a in c["pos"]))]
    ok("no suggested camera sits inside a block", not inside, "%s" % inside)

    # ---- the calls ----
    from engine import shots

    film = shots.Film(scene, fps=24)
    s = film.shot("t", 0.0, 20.0)
    zuri = players.make_player("zuri", "zuri")
    zuri.place(1, bd.A["zuri"], bd.yaw["zuri"])
    nb = bd.notes["zuri"]
    notes = nb.song(zuri, 10, count=20, every=8, camera=s)
    ok("right-click taps tune up one semitone each and wrap 24 -> 0 (NoteBlock.useWithoutItem: cycle)",
       notes[:3] == [HERO_NOTES["zuri"] + 1, HERO_NOTES["zuri"] + 2, HERO_NOTES["zuri"] + 3]
       and 0 in notes and notes[notes.index(0) - 1] == 24, "%s" % notes)
    left = nb.tap(zuri, 400, use=False, camera=s)
    ok("a left-click plays the same note again (NoteBlock.attack)", left == notes[-1])
    b = bd.notes["kai"].played(100, 7, camera=s)
    p = b.particles[-1]
    path = p["pos"]
    ok("played(): one note particle 1.2 above the block's base, visible from frame 100 for 6 ticks (8 frames)",
       abs(path[0][2] - (bd.notes["kai"].cell[2] + 1.2)) < 0.02 and p["first"] == 100 and p["last"] - p["first"] in (8, 9),
       "z %.3f, frames %d-%d" % (path[0][2], p["first"], p["last"]))
    ok("its quad is 0.3-0.6 block wide (SingleQuadParticle 0.1-0.2 x 1.5) and rises 0.54 straight up",
       0.15 - 1e-6 <= p["size"] <= 0.3 + 1e-6 and abs(path[-1][2] - path[0][2] - note_rise()) < 0.03
       and math.dist(path[-1][:2], path[0][:2]) < 0.05, "size %.3f rise %.3f" % (p["size"], path[-1][2] - path[0][2]))
    mat = p["object"].data.materials[0]
    tint = mat.name.split("#")[1][:6] if "#" in mat.name else ""
    ok("its tint is note_colour(7) through the game's particle/note.png", tint == "%02x%02x%02x" % _rgb8(note_colour(7))
       and "particle/note" in mat.name, mat.name)
    jbx = bd.jukebox
    frames = jbx.play(500, 620, disc="music_disc_11", camera=s)
    ok("a playing jukebox: a note every 20 ticks (24 frames) from the first tick", frames[:3] == [500, 524, 548]
       and len(frames) == 6, "%s" % frames)
    drop = jbx.eject(560, disc="music_disc_11", camera=s)
    bur = jbx.bursts[-1]
    alive = [q for q in bur.particles if q["first"] < 561.2 <= q["last"]]
    later = [q for q in bur.particles if q["first"] >= 562]
    ok("eject: no note after it, the one in the air lives out its 6 ticks", not any(q["last"] > q["first"] for q in later)
       and all(q["last"] - q["first"] >= 8 for q in alive) and len(bur.particles) == 6, "%d later" % len(later))
    tr = item_track(w, drop.spawn_point, (0.05, 0.0, ITEM_TOSS[1]))
    ok("the disc pops out at the top's middle +-0.35, rises about half a block and lands on the jukebox (seed %d)"
       % drop.seed, abs(drop.spawn_point[0] - (jx + 0.5)) <= 0.35 + 1e-9 and abs(drop.spawn_point[1] - (jy + 0.5))
       <= 0.35 + 1e-9 and abs(drop.rest_pos[2] - (jz + 1.0)) < 1e-6 and 0.3 < max(q[2] for _t, q in tr) - (jz + 1) < 0.6
       and jx < drop.rest_pos[0] < jx + 1 and jy < drop.rest_pos[1] < jy + 1,
       "rest %s" % (tuple(round(c, 3) for c in drop.rest_pos),))
    scene.frame_set(drop.land_frame - 30)
    hidden_before = all(ob.hide_render for ob in drop.copies)
    scene.frame_set(drop.land_frame + 5)
    ok("the disc item is not there before its eject and is there after it", hidden_before
       and not all(ob.hide_render for ob in drop.copies))
    try:
        creeper_disc((0.5, 30.5, 0.0), 100, disc="diamond", world=v)
        ok("creeper_disc refuses a disc a creeper cannot drop", False)
    except ValueError:
        ok("creeper_disc refuses a disc a creeper cannot drop", True)
    cd = creeper_disc((0.5, 30.5, v.ground(0.5, 30.5)), 700, world=v, seed=3)
    ok("creeper_disc: the disc lands on the meadow's ground and lies there", abs(cd.rest_pos[2] - v.ground(0.5, 30.5))
       < 0.07 and cd.still_frame > 700, "rest z %.3f ground %.3f" % (cd.rest_pos[2], v.ground(0.5, 30.5)))
    ll = bd.last_lantern
    ll.place(300)
    scene.frame_set(299)
    before = (ll.block.object.hide_render, ll.light.hide_render)
    scene.frame_set(300)
    after = (ll.block.object.hide_render, ll.light.hide_render)
    ok("the last lantern and its light appear ON the frame it is placed", before == (True, True)
       and after == (False, False), "%s -> %s" % (before, after))
    kai = players.make_player("kai", "kai")
    kai.place(1, bd.A["kai"], bd.yaw["kai"])
    clap(kai, 50, count=3)
    ok("clap(): crouch, stand, crouch ... (players sneak snaps)", [kai.crouching_at(f) for f in (49, 50, 52, 54, 56,
                                                                                               58)] ==
       [False, True, False, True, False, True])
    ob = hold(kai, "gold_block", frame=60)
    sc = ob.matrix_basis.to_scale()[0] if ob is not None else 0.0
    ok("a gold block held as the game draws a block in the hand (block.json display scale 0.375 x the model's 0.9375)",
       abs(sc - 0.375 * 0.9375) < 0.005, "%.4f" % sc)
    target = (bd.A["kai"][0] - 4.0, bd.A["kai"][1] + 0.5, 2.6)
    present(kai, 70, 90, target)
    scene.frame_set(80)
    sh = kai.arm_r.matrix_world.translation
    hand = kai.arm_r.matrix_world @ Vector((0.0, 0.0, -10.0 * kai.unit))
    d1 = (hand - sh).normalized()
    d2 = (Vector(target) - sh).normalized()
    ang = math.degrees(d1.angle(d2))
    ok("present(): the arm points at the target (within 6 degrees)", ang < 6.0, "%.1f deg" % ang)
    scene.frame_set(1)
    print("[music] %s (%d checks failed)" % ("OK" if not bad else "FAILED", len(bad)))
    return bad


def _selftest(argv):
    """`$BPY -m engine.music` (numbers) or `$BPY -m engine.music stills NAME ...` (proof stills)."""
    import sys

    if argv and argv[0] == "stills":
        from tools import music_proof

        return music_proof.main(argv[1:])
    bad = _check()
    sys.stdout.flush()
    return 1 if bad else 0


if __name__ == "__main__":
    import sys

    sys.exit(_selftest(sys.argv[1:]))
