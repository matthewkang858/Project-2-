"""MUSIC: the bandstand of "The Crammys" (film four, stories/crammys.json), note blocks, the jukebox, music discs,
the goat horn, the totem of undying and the players' applause. (The full docstring is written at the end of the
file's construction; see DOC below.)
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


def creeper_disc(feet, frame, disc="music_disc_11", seed=0, world=None, until=None, collection=None, name=None):
    """The music disc a creeper drops when a skeleton's arrow kills it (loot_table/entities/creeper.json): an
    engine.mobs dropped item spawned ON the killing-blow frame at the creeper's feet with ItemEntity's random toss
    (+-0.1, 0.2 up, +-0.1 per tick), landing on the ground under it (world = the Village or its World: the terrain
    height there), then bobbing and spinning until `until` (default frame + 240). Returns the DroppedItem
    (.land_frame, .still_frame, .rest_pos). The game draws one of 12 discs (CREEPER_DISCS) at random."""
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
        rng = np.random.default_rng([int(seed) & 0x7FFFFFFF, int(a * 10), 61])
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
            if land != "top" or abs(end[2] - self.top) < 1e-6:
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
JUKEBOX_CELL = (-6, 0, 1)                   # centre stage, one row behind the front row
PEDESTAL = (-9, 0)                          # oak fence (z 0) + gold block (z 1) on the ground before the stage
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
    target("jukebox", (jx + 0.5, jy + 0.5, jz + 0.5))
    target("jukebox_top", (jx + 0.5, jy + 0.5, jz + 1.25))
    target("pedestal", (PEDESTAL[0] + 0.5, PEDESTAL[1] + 0.5, 2.25))
    target("center", (-6.5, 0.5, 2.4))
    target("wing", (-6.5, 4.6, 2.0))
    # performers at their note blocks: behind and 0.3 to the side of the block, facing it, 0.1 block behind its back
    put("zuri", (-6.6, 2.85), look=(-7.5, 2.5))
    put("kai", (-6.6, 1.65), look=(-7.5, 1.5))
    put("sunny", (-6.6, -1.3), look=(-7.5, -1.5))
    put("noor", (-5.45, 2.45), yaw=yaw_of("west"))
    put("alex", (-5.5, 1.45), look=(jx + 0.5, jy + 0.5))       # beside the jukebox, north of it
    put("steve_center", (-7.25, 0.5), yaw=yaw_of("west"))       # centre stage, the jukebox behind him
    put("steve_jukebox", (-5.5, 1.7), look=(jx + 0.5, jy + 0.5))
    put("steve_wing", (-6.4, 5.4), look=(-6.4, 0.0))
    # beat 19: the half circle beyond the jukebox, facing the wing (staggered by 0.7)
    for i, p in enumerate(((-6.85, -0.8), (-6.15, -2.0), (-5.15, -2.55), (-4.6, -1.4)), 1):
        put("half_%d" % i, p, look=(-6.4, 5.0))
    # beats 22-24: two groups flanking the jukebox in profile to the front, all facing it
    for i, p in enumerate(((-6.95, 1.6), (-6.2, 2.4), (-5.2, 2.85)), 1):
        put("flank_n%d" % i, p, look=(jx + 0.5, jy + 0.5))
    for i, p in enumerate(((-6.95, -0.6), (-6.2, -1.4), (-5.2, -1.85)), 1):
        put("flank_s%d" % i, p, look=(jx + 0.5, jy + 0.5))
    # on the ground in front of the stage (the corridor before it and the street)
    put("steve_foot", (-9.75, -1.15), look=(jx + 0.5, jy + 0.5, 2.0), ground=True)
    put("steve_front", (-11.2, -0.3), look=(-16.5, -1.6), ground=True)
    put("steve_kai", (-9.95, -0.7), look=(-7.5, 1.5), ground=True)     # beat 3: his shoulder in the foreground
    for i, y in enumerate((2.3, 1.05, -0.2, -1.45, -2.7), 1):  # beat 6: the line beside the stage, facing west
        put("line_%d" % i, (-10.2, y), yaw=yaw_of("west"), ground=True)
    put("alex_post", (-7.0, 3.25), look=(-7.5, 3.5, 3.0))       # beat 5: Alex places the last lantern
    put("alex_beside", (-6.45, 1.75), yaw=yaw_of("south"))      # beat 20: beside steve_jukebox, her disc held out
    # beat 18: the three-shot on the jukebox's south side, all facing it (Steve stops between Sunny and Noor)
    put("three_sunny", (-6.65, -1.0), look=(jx + 0.5, jy + 0.5))
    put("three_steve", (-5.9, -1.3), look=(jx + 0.5, jy + 0.5))
    put("three_noor", (-5.0, -1.1), look=(jx + 0.5, jy + 0.5))
    return A


def lane_set(b, name="lane"):
    """In the hook: Kai's doorstep dressing in front of house_f (his gold block with a note block on it south of the
    doorstep, a lantern on an oak fence post north of it: light group 'lane'), facing the narrator's front door (house_e, across the exit road). Registers
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
    w.set(lx, ly, 0, "oak_fence")                               # the lantern on a fence post: beside Kai's head
    b.torch((lx, ly, 1), "lantern", group="lane")
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
    res = dict(name=name, column=(cx, cy), lantern=(lx, ly, 1), anchors=A, home=home, to_square=to_square,
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
    jt = (-5.5, 0.5, 2.0)
    cams = {
        # 1: low, long lens, slow push in; Steve (steve_front) sharp, the stage soft behind him
        "b1": dict(pos=(-16.2, -0.2, 1.0), target=(-6.6, 0.8, 2.3), pos1=(-15.4, -0.12, 1.05),
                   target1=(-6.6, 0.8, 2.3), lens=40.0, fstop=2.0, focus=(-11.2, -0.3, 1.6), beat=1),



        # 2: close on Zuri's note block on its white wool, then tilt up to her face
        "b2": dict(pos=(-10.9, 3.4, 1.05), target=(-7.5, 2.5, 1.15), target1=(-6.6, 2.85, 2.55),
                   lens=40.0, fstop=2.2, focus=(-7.5, 2.5, 1.0), beat=2),

        # 3: the mirror: past Steve's soft shoulder (steve_foot) to Kai's note block on gold, pull to his face
        "b3": dict(pos=(-10.3, -2.3, 1.35), target=(-7.5, 1.5, 1.4), lens=45.0, fstop=2.2,
                   focus=(-7.5, 1.5, 1.2), beat=3),



        # 4: static wide of the stage (Sunny at the far end, Steve below it)
        "b4": dict(pos=(-16.5, 0.2, 1.6), target=(-6.6, 0.6, 2.0), lens=30.0, fstop=5.6, focus=(-7.0, 0.5, 2.0),
                   beat=4),


        # 5: close on the totem above the pedestal, rising and pulling back to the whole bandstand
        "b5": dict(pos=(-11.2, 0.5, 2.75), target=(-8.5, 0.5, 2.45), pos1=(-18.5, 0.6, 3.9),
                   target1=(-6.4, 0.8, 2.1), lens=55.0, fstop=2.8, focus=(-8.5, 0.5, 2.35), beat=5),


        # 6: travelling along the line beside the stage (line_1 .. line_5 = Steve) at hand height
        "b6": dict(pos=(-13.0, 3.3, 1.5), target=(-10.2, 2.3, 1.3), pos1=(-13.0, -1.7, 1.5),
                   target1=(-10.2, -2.7, 1.3), lens=35.0, fstop=2.8, focus=(-10.2, 2.3, 1.3), beat=6),

        # 8: over Steve's shoulder (steve_foot) at the jukebox: the ejected disc turning above it
        "b8": dict(pos=(-10.38, -1.82, 1.95), target=(-5.5, 0.5, 2.4), lens=45.0, fstop=2.4,
                   focus=(-5.5, 0.5, 2.4), beat=8),


        # 18: from the front of the stage at head height (its north-west corner), a medium three-shot: Sunny,
        # Steve, Noor (three_*) facing the jukebox
        "b18": dict(pos=(-7.4, 1.3, 2.6), target=(-5.9, -1.25, 2.35), lens=32.0, fstop=3.2,
                    focus=(-5.9, -1.3, 2.5), beat=18),

        # 19: from the wing, behind and above Steve walking to the jukebox; the half circle beyond it facing us
        "b19": dict(pos=(-6.2, 6.4, 3.2), target=(-5.8, -1.0, 2.0), lens=32.0, fstop=4.0,
                    focus=(-5.8, -1.0, 2.0), beat=19),

        # 20: close from across the jukebox: Steve's disc face-on to the lens (steve_jukebox, present())
        "b20": dict(pos=(-5.45, -1.75, 2.45), target=(-5.5, 1.2, 2.4), lens=40.0, fstop=2.4,
                    focus=(-5.5, 0.85, 2.45), beat=20),
        # 21: the jukebox sharp in the foreground, notes rising; push past it to Steve beside it
        "b21": dict(pos=(-7.0, -1.9, 2.25), target=(-5.5, 0.5, 2.1), pos1=(-6.7, -1.2, 2.4),
                    target1=(-5.5, 1.7, 2.6), lens=32.0, fstop=2.4, focus=(-5.5, 0.5, 2.1), beat=21),

        # 22: the one locked-off frontal wide of the whole stage
        "b22": dict(pos=(-15.5, 0.6, 3.0), target=(-6.5, 0.6, 2.3), lens=30.0, fstop=5.6, focus=(-6.5, 0.5, 2.2),
                    beat=22),

        # 23: from beside the jukebox (south), along the row of faces on the north flank
        "b23": dict(pos=(-4.7, -0.2, 2.65), target=(-6.6, 2.3, 2.45), lens=30.0, fstop=3.2,
                    focus=(-6.2, 2.4, 2.6), beat=23),

        # 24: medium on Steve centre stage, facing the lens, the totem held out; pull back to the clapping five
        "b24": dict(pos=(-11.2, 0.5, 2.2), target=(-7.25, 0.5, 2.3), pos1=(-15.8, 0.5, 2.45),
                    target1=(-6.6, 0.5, 2.15), lens=45.0, fstop=2.8, focus=(-7.25, 0.5, 2.5), beat=24),
        # 7 and 17: from Kai's doorstep (lane_kai), past his head, across the lane to the narrator's door
        "lane": dict(pos=(3.84, 16.3, 1.75), target=(-4.5, 16.0, 1.2), lens=20.0, fstop=2.8,
                     focus=(1.5, 15.5, 1.2), beat=7),


        # proofs: each hero note block close (with its base block), the held block items, the horn, the jukebox,
        # the dropped discs, the applause
        "note_zuri": dict(pos=(-10.0, 3.6, 1.2), target=(-7.5, 2.5, 1.35), lens=55.0, fstop=2.8,
                          focus=(-7.5, 2.5, 1.2), beat=2),
        "note_kai": dict(pos=(-10.1, 0.2, 1.2), target=(-7.5, 1.5, 1.35), lens=55.0, fstop=2.8,
                         focus=(-7.5, 1.5, 1.2), beat=3),
        "note_sunny": dict(pos=(-10.1, -3.2, 1.2), target=(-7.5, -1.5, 1.35), lens=55.0, fstop=2.8,
                           focus=(-7.5, -1.5, 1.2), beat=4),
        "held": dict(pos=(-13.4, -0.6, 2.0), target=(-10.2, 0.4, 1.55), lens=32.0, fstop=4.0,
                     focus=(-10.2, 1.0, 1.4), beat=6),
        "horn": dict(pos=(-8.9, 1.2, 2.55), target=(-5.45, 2.45, 2.6), lens=55.0, fstop=2.8,
                     focus=(-5.45, 2.45, 2.6), beat=1),
        "jukebox": dict(pos=(-8.6, -1.7, 2.6), target=(-5.5, 0.5, 2.25), lens=45.0, fstop=4.0,
                        focus=(-5.5, 0.5, 2.2), beat=8),
        "discs_drop": dict(pos=(-9.2, -1.6, 1.75), target=(-6.0, 0.5, 1.6), lens=50.0, fstop=4.0,
                           focus=(-6.2, 0.5, 1.5), beat=16),
        "clap": dict(pos=(-11.0, 1.0, 2.6), target=(-6.2, 2.2, 2.0), lens=35.0, fstop=4.0,
                     focus=(-6.2, 2.2, 2.0), beat=24),
    }
    return cams
