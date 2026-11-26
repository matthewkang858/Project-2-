"""Twenty Minutes, sequence SQUARE: the village square by the well and the foot of the tower, golden hour. Beats 1-5
(shots sq01_afraid, sq02_imnot, sq03_grownups, sq04_tilt, sq04_hat, sq05_wave), sky "gold". One function per shot;
the contract is in films/twentyminutes_common.py (tags "sq...", C.actor, C.cam, C.lights, st.use / st.hero).

THE PLACE (films/twentyminutes_set.py, WHERE EVERY BEAT IS FILMED; engine/towers.py ANCHORS): the plaza east of the
  well (the well x -3..2, y -3..2); CAMS "plaza" low on the path east of it at (9.3, -0.6, 0.55) (the baby's eye
  height: 0.2 lower than the set's b01, so the baby's head stays above the caption band), 40 mm, looking north-west over
  the well at the tower above the roofs (house_c at the left with its door, house_e at the right). The plaza lamp post
  that stood at (-7, 9), right behind the baby's head in this framing, is TAKEN OUT of this film's village
  (films/twentyminutes_set.py LAMP_OUT; both reviews found the tangent).
THIS SEQUENCE OWNS (the contract, amended): CAMS "plaza", "tilt", "hat" and PLACES "baby_square" (nobody else uses
  them): you may redefine each ONCE as a constant here, used by every shot that shares it; say so in your result.
  The baby's spot PLACES "baby_square" (6.38, 1.16) = tm_baby_square, facing north-north-east (C.yaw("tm_baby_square")).
  Steve's paths: tm_steve_square (-1.0, 7.3) -> (8.3, 0.7) (at the lens, passing the baby 1.4 to its right),
  tm_steve_past (4.5, 0.64) -> (6.55, 3.1) (between the b02 lens and the baby), tower_push_square (6.5, 6.0) ->
  (-0.5, 6.0) along the plaza's north path (beat 3); the armorer and the shepherd: tm_flee_armorer / tm_flee_shepherd
  from tm_armorer_from / tm_shepherd_from into house_c through its door (C.v.door_open("house_c", f[, open=False])).
  The foot of the tower (beat 5): towers' foot_front (-20.5, 16.45) at the front of the stone base.
THE SCOUTING STILLS (the set builder's, under this sky; LOOK at them before you shoot):
  out/test/twentyminutes_set_b01_afraid.png, _b01_afraid_door.png, _b02_imnot.png, _b03_push.png, _b04_tilt_b.png,
  _b04_long_hat.png, _b05_arms.png (+ _zones.png each), and the lead's out/test/twentyminutes_scout_*.png.
LIGHT: C.lights(s, "square") on the plaza (every torch at its own level, the pod's lantern and the cell's torch at
  1.0); C.lights(s, "tower") at the foot of the tower (sq05).
TAGS TAKEN (twins): baby_sq (sq01-sq04_tilt, sq05), steve_sq (sq01-sq03), armorer_sq, shepherd_sq (sq01), mom_sq (sq03,
  sq04_tilt, sq04_hat), zombie_sq (sq04_tilt, sq04_hat). A new twin: sq2, sq3 ...
PREVIEWS through render.py: --samples 5 (PREVIEW_SAMPLES["square"]).
"""
import math

from engine import towers
from films import twentyminutes_common as TC


def sq01_afraid(st, s, C, nar):
    """BEAT 1  "In this village, everyone is afraid of the player."   frames 1-87 (87 f, 3.62 s), sky gold.
    Words: In 8, this 10, village 16, everyone 36, is 48, afraid 52, of 63, the 66, player 67. The voice ends on 80
    (the pause after the line is 0.40 s).
    Before: the film's start; after: sq02_imnot.

    STORY: Hook. Camera at baby height on the path by the well, long lens. Steve walks across the square straight at
    the lens. Behind him an armorer and a shepherd turn and hurry to a house, and the door shuts behind the second. In
    the lower middle of the frame, above the caption band, a baby villager stands still, three-quarter from behind so
    its nose shows, and tilts its big head up as he comes. The glass tower is a soft bright shape above the roofs.
    Cast: Steve (the player), baby villager (narrator), armorer villager, shepherd villager. Effects: house door
    closing, iron farm tower out of focus in the background.

    MUST BE SEEN, ON WHICH WORD
      frame 1           already moving: Steve walking at the lens, the two adults hurrying
      "afraid" .. "player"   the door of house_c shuts behind the second (the set's timing: the door opens 12 frames
                        before the armorer reaches it, shuts one frame after the shepherd is in)
      the whole shot    the baby lower middle, above the caption band, ITS NOSE (three-quarter from behind), its head
                        tilting up as he comes; the tower a bright shape above the roofs
    OWNED (this sequence's): CAMS "plaza" (sq01 only now: sq04_tilt has its own move), PLACES "baby_square".
    NEIGHBOURS: first shot of the film; after, sq02_imnot (the baby's face, Steve's legs crossing).
    MEASURED (the lead, after the reviews; tools/twentyminutes_probe heroes and tools.twentyminutes_geo sq01_afraid:1 /
      :44 / :70, lens at z 0.55): the baby's head box x 28-66 / y 36-57 % (f1), 23-65 / 35-59 (44), 20-63 / 35-60
      (87): ABOVE the caption band (with the set's lens at 0.75 it reached y 64-66 %); its nose is 95-96 degrees off
      the lens: in the still out/test/twentyminutes_scout_sq01_afraid_44_zones.png it READS AS A BLANK PINK BOX (the
      story wants its nose, three-quarter from behind): cheat its look toward the lens' side (C.cheat(..., max_off=80)
      or C.to_lens; its body is about 99 degrees from the lens, so the head alone can bring the nose to about 30:
      C.cheat now warns when the head cannot reach); the lamp post is gone from behind its head (the set). Steve:
      eyes 70 / 43 % on f1, 80 / 31 % on 44 (head x 71-90: into the icon column as he nears), past the lens by 70.
      The armorer and the shepherd: on f1 BEHIND THE BABY'S HEAD (x 42 / 56 %), by 44 at the left edge (x 4 / 8 %,
      the armorer behind the well's wall): they read only between f1 + 10 and 44; the door x 10 / y 44 %. The pod's
      glass y 8-22 % (its roof under the top icons: background here).
    NOW (stub = the set's stage_b01): CAMS "plaza", focus on the baby; the baby on baby_square looking 2 ahead and up,
      tilting to 3.4 up from f0 + 30; Steve along tm_steve_square from f0; the two along their flee paths (the
      shepherd 5 frames later), the door open / shut on the set's offsets. Hero: the baby.
    """
    f0, v = s.frame_start, C.v
    baby = C.actor("baby", "sq")
    bp = C.put(baby, f0, "baby_square", yaw=C.yaw("tm_baby_square"))
    by = C.yaw("tm_baby_square")
    steve = C.actor("steve", "sq")
    path = v.paths["tm_steve_square"]
    steve.place(f0, path[0], TC.yaw_to(path[0], path[1]))
    steve.walk(f0, path)
    ahead = (bp[0] + 2.0 * math.sin(by), bp[1] - 2.0 * math.cos(by))
    baby.look_at(f0, (ahead[0], ahead[1], bp[2] + 1.2), ease=0)
    baby.look_at(f0 + 30, (ahead[0], ahead[1], bp[2] + 3.4), ease=24)
    arm, she = C.actor("armorer", "sq"), C.actor("shepherd", "sq")
    ends = []
    for c, key, delay in ((arm, "tm_flee_armorer", 0), (she, "tm_flee_shepherd", 5)):
        pts = v.paths[key]
        c.place(f0, pts[0], TC.yaw_to(pts[0], pts[1]))
        ends.append(c.walk(f0 + delay, pts, run=True))
    v.door_open("house_c", ends[0] - 12, open=True, frames=5)
    v.door_open("house_c", ends[1] + 1, open=False, frames=5)
    st.use(s, baby, steve, arm, she)
    C.cam(s, "plaza", focus=baby.head)
    st.hero(s, "baby", baby)
    C.lights(s, "square")


def sq02_imnot(st, s, C, nar):
    """BEAT 2  "I'm not."   frames 88-131 (44 f, 1.83 s), sky gold.
    Words: I'm 90, not 95. The voice ends on 107 (the pause after the line is 1.15 s).
    Before: sq01_afraid; after: sq03_grownups.

    STORY: Two seconds; the pause after the line is opened to fill the shot. Tight on the baby's face from the front,
    three-quarter, in the upper half of the frame, head tilted up. Steve's legs stride through the foreground and his
    shadow crosses its face. It does not step back. Its head turns to follow him.
    Cast: baby villager (narrator), Steve (legs only). Effects: Steve's shadow passing over the baby.

    MUST BE SEEN, ON WHICH WORD
      frame 1           the baby's face, already looking at him (its head moving)
      "not"             his legs cross the foreground (they are in the 50 mm frame only about 4 frames: time the walk to
                        the word); the baby does NOT step back; its head follows him to the end
    SHARED: PLACES "baby_square" (the same spot as sq01). The set's camera b02 (towers' baby_face).
    NEIGHBOURS: before, sq01_afraid (Steve coming at the lens); after, sq03_grownups (the push).
    RISKS / KNOWN: "his shadow crosses its face" cannot be had under this sun (north-north-east: his shadow falls
      south-west, away from the baby, whichever side of the lens he passes): not had, the legs are the beat.
    MEASURED (the set builder, still _imnot at f0 + 14): the face x 50 / y 44 %. The lead's probe (heroes): the baby's
      head box x 16-79 / y 17-58 % on f1, 11-93 / 17-61 on 109, 12-104 / 15-61 on the last frame: AS ITS HEAD FOLLOWS
      STEVE IT RUNS OFF THE RIGHT EDGE (into the icon column from about 100): keep the head turn small or frame wider.
    NOW (stub = the set's stage_b02): camera "set:b02" (4.69, 2.57, 0.72) -> the baby, 50 mm f/2; Steve along
      tm_steve_past from f0 + 6; the baby's head on him every 4 frames. Hero: the baby.
    """
    f0, v = s.frame_start, C.v
    baby = C.actor("baby", "sq")
    C.put(baby, f0, "baby_square", yaw=C.yaw("tm_baby_square"))
    steve = C.actor("steve", "sq")
    path = v.paths["tm_steve_past"]
    steve.place(f0, path[0], TC.yaw_to(path[0], path[1]))
    steve.walk(f0 + 6, path)
    baby.look_at(f0, steve, ease=0)
    for f in range(f0 + 4, s.frame_end + 1, 4):
        baby.look_at(f, steve, ease=3)
    st.use(s, baby, steve)
    C.cam(s, "set:b02", focus=baby.head)
    st.hero(s, "baby", baby)
    C.lights(s, "square")


def sq03_grownups(st, s, C, nar):
    """BEAT 3  "He only takes grownups."   frames 132-186 (55 f, 2.29 s), sky gold.
    Words: He 134, only 137, takes 145, grownups 153. The voice ends on 170 (the pause after the line is 0.80 s).
    Before: sq02_imnot; after: sq04_tilt.

    STORY: Side-on at baby height. Steve walks into the back of Mom, a farmer in a straw hat, and pushes her step by
    step along the path toward the tower, the way players move villagers. Her head is turned to give hat brim and nose
    in profile. The baby runs three steps after them, 0.7 block clear of his legs, and stops. He passes it without
    turning his head.
    Cast: Steve (the player), Mom (farmer villager, straw hat), baby villager (narrator). Effects: villager pushed
    along by the player (slow continuous shuffle), baby run and stop.

    MUST BE SEEN, ON WHICH WORD
      frame 1           already moving: Steve shoving her (towers.push)
      "grownups"        Mom's straw hat, brim and nose in profile (the viewer meets the hat here: it is how Mom is
                        known at the glass in sq04_hat and in every pod shot)
      the end           the baby has run three steps after them and stopped, 0.7 clear of his legs
    SHARED: none (towers' push_baby, tower_push_square).
    NEIGHBOURS: before, sq02_imnot; after, sq04_tilt (Mom at the top of the tower).
    KNOWN (the set builder, and the lead's geo probe): towers.push keys the WHOLE route at about 0.9 blocks/s and
      keys past the shot's end override the next shot's place(): push only as far as the shot lasts (_push_length:
      the longest route whose last key is 2 frames before the cut; with 0.85 blocks per second of shot, the set's
      rule, Mom was still on the plaza in sq04_tilt).
      towers.push place()s both ON its frame: start it ON f0 (they are in sq02 / sq01 before: no pre-roll).
      In sq03 (on the plaza, before the pod) Mom may look where the push takes her: the story's "Mom never looks at
      me" starts with the pod.
    MEASURED (the set builder, still _push at f0 + 40): Mom x 44 / y 43 % (hat brim and nose to the lens). The lead's
      probe (heroes): Mom's head box x 36-55 (f1), 19-42 (159), -5..29 on the last frame: SHE LEAVES BY THE LEFT EDGE
      (the push was shortened to the shot, the set's linear pan was not): slow the pan or end it earlier.
    NOW (stub = the set's stage_b03, the push from f0): camera "set:b03" (towers' push_square, panning LINEAR along
      the plaza's north path), focus on Mom; her head turned 2 west, 2.2 north, 1.6 up every 12 frames; the baby on
      push_baby runs from f0 + 24 to 1.2 behind Steve. Hero: Mom.
    """
    f0, v = s.frame_start, C.v
    steve, mom = C.actor("steve", "sq"), C.actor("mom", "sq")
    r0 = v.paths["tower_push_square"][0]
    route = [tuple(r0), (r0[0] - _push_length(s.frame_end - 2 - f0), r0[1], r0[2])]
    towers.push(steve, mom, f0, route)
    for f in range(f0, s.frame_end + 1, 12):
        p = mom.pos_at(f)
        mom.look_at(f, (p.x - 2.0, p.y + 2.2, p.z + 1.6), ease=0 if f == f0 else 4)
    baby = C.actor("baby", "sq")
    C.put(baby, f0, "push_baby")
    fb = f0 + 24
    here, his = baby.pos_at(fb), steve.pos_at(fb + 10)
    baby.walk(fb, [tuple(here), (max(his.x + 1.2, here.x - 1.6), here.y, here.z)], run=True)
    baby.look_at(fb, mom, ease=4)
    st.use(s, steve, mom, baby)
    C.cam(s, "set:b03", focus=mom.head)
    st.hero(s, "mom", mom)
    C.lights(s, "square")


def _push_length(frames):
    """The longest push (blocks, towers.push "tap") whose last key falls within `frames` frames: towers.push keys the
    WHOLE route, and a key after the shot's end overrides the next shot's place() (measured: with 0.85 blocks per
    second of shot from f0, Mom was still being pushed on the plaza in sq04_tilt, 8 blocks from the lens)."""
    total = 3.0
    while total > 0.3:
        track = towers.push_route(total)
        if track[-1][0] * towers.TICK <= frames:
            return total
        total -= 0.1
    return total


def sq04_tilt(st, s, C, nar):
    """BEAT 4  "My mom lives at the top of his" (of: My mom lives at the top of his glass tower now.)   frames 187-229
    (43 f, 1.79 s), sky gold.
    Words: My 189, mom 193, lives 205, at 212, the 214, top 216, of 224, his 226.
    Before: sq03_grownups; after: sq04_hat.

    STORY (beat 4, the first of its two shots): Over the baby's shoulder, slow tilt up from the well and the bell to the
    iron farm tower above the roofs: stone pillar, low glass pod with lantern light, an orange glow under the platform
    rim, a brown zigzag of dirt blocks up its flank. At the front glass the straw hat, in profile, looking sideways at
    something inside the pod, not down. Rack focus from the baby to her.
    Cast: baby villager (narrator), Mom (farmer villager, straw hat), cleric villager and librarian villager as shapes
    in the pod. Effects: iron farm tower exterior, lantern in the pod, lava glow under the platform rim, dirt staircase
    visible on the tower's flank, rack focus.

    MUST BE SEEN, ON WHICH WORD
      frame 1           the tilt already moving (CAMS "tilt" is LINEAR: an even 0.27 degrees a frame), aimed down past
                        the baby's shoulder at the ground, the well's mossy wall at the left, the tower above the frame
      "mom" .. "lives"  the tower entering from the top as the camera tilts up
      "at" .. "top"     the focus racks from the baby to the pod (C.rack from "at", 10 frames: sharp from 222)
      the last frames   the pod in the upper part of the frame, inside the safe area (y about 13-27 %), sharp
    OWNED (this sequence's): CAMS "tilt" (REDEFINED by the lead after both reviews: the set's b04 was a 5.5-degree pan
      plus a 0.8-degree tilt, 78 % of it in the first ten frames, ending on sq01's framing), PLACES "baby_square".
    NEIGHBOURS: before, sq03_grownups; after, sq04_hat: THE CUT INSIDE THE LINE (before "glass") to the straw hat.
    FALLBACKS APPLIED (story risk "MOM AT THE TOP OF THE TOWER"): from the square she is a few pixels: the cut inside
      the line to the 200 mm straw hat (sq04_hat). The orange glow under the rim and the dirt zigzag CANNOT be seen
      from the square (the slot is behind the pod's west side, the stairs on its back): they are seen in gm09-gm11 and
      gp13 instead (engine/towers.py NOT THE GAME; the set builder's limits). The bell (-1.5, -2.5) is 36 degrees left
      of the tilt's start: the well only.
    MEASURED (the lead: tools/twentyminutes_probe cams / heroes, stills out/test/twentyminutes_scout_sq04_tilt_187 /
      _208 / _229 (+ _zones; 270x480, 8 samples; 187 and 229 rendered before the last 0.3-degree adjustments)): heading
      / pitch 153.8 / -8.5 (187), 151.1 / -2.8 (208), 148.4 / +2.9 (229); the baby's head box x 46-84 / y 18-40 % (187:
      upper right of the middle), 37-75 / 30-51 (208), 27-65 / 41-62 (229: its chin on the caption band's top edge,
      soft by then); the pod's glass about y 13-27 % at the end, Mom's head x 53 / y 17-19 % (a few pixels). THE
      BABY'S HEAD IS A BLANK PINK BOX from behind (off the lens 165 degrees: it looks at the pod, which is straight
      down the lens' axis): over the shoulder this is the back of its head; a cheat of its look 30-40 degrees to the
      lens' side would show an ear-side profile at the start. The lamp post is gone (the set).
    NOW (stub): CAMS "tilt" (linear), focus on the baby, racked to the pod's front from "at" over 10 frames; the baby on
      baby_square looking at the pod (pod_target); Mom on mom_glass on the zombie (C.on_zombie); the zombie in its cell
      (look=Mom). Hero: the baby (the pod is a point, not an object: check it on the stills).
    """
    f0 = s.frame_start
    baby = C.actor("baby", "sq")
    C.put(baby, f0, "baby_square", yaw=C.yaw("tm_baby_square"))
    baby.look_at(f0, C.A["pod_target"], ease=0)
    mom = C.actor("mom", "sq")
    C.put(mom, f0, "mom_glass")
    C.on_zombie(mom, f0, until=s.frame_end)
    C.zombie(s, "sq", look=mom)
    st.use(s, baby, mom)
    C.cam(s, "tilt", focus=baby.head)
    C.rack(s, TC.TS.POD_FRONT, C.at(s, "at"), frames=10)     # sharp on the pod from 222: 8 frames before the cut
    st.hero(s, "baby", baby)
    C.lights(s, "square")


def sq04_hat(st, s, C, nar):
    """BEAT 4  "glass tower now." (of: My mom lives at the top of his glass tower now.)   frames 230-271 (42 f, 1.75
    s), sky gold.
    Words: glass 230, tower 240, now 250. The voice ends on 258 (the pause after the line is 0.65 s).
    Before: sq04_tilt; after: sq05_wave.

    STORY (beat 4, the second shot: the story's own fallback "cut inside the line to a long-lens view of the straw hat
    at the glass"): At the front glass the straw hat, in profile, looking sideways at something inside the pod, not
    down.

    MUST BE SEEN, ON WHICH WORD
      frame 1           the straw hat in profile behind the glass (a slow drift: something moving)
      "glass" .. "now"  her face and nose in profile, clear of pane lines, the far walls' frames behind her (it reads as
                        glass); her head on the ZOMBIE (sideways, not down): from here on, every frame of Mom in the
                        pod has her head on C.zombie_eye
    OWNED (this sequence's): CAMS "hat" (the set's b04_long, 200 mm f/2.8 from the plaza at z 0.9: used by this shot
      only, re-frame it as you need).
    NEIGHBOURS: before, sq04_tilt (the same line, the cut before "glass"); after, sq05_wave (the foot of the tower).
    KNOWN (the set builder): every pane between the lens and her head, face and shoulders is hidden (C.panes with n=3:
      a grazing line crosses two or three panes); the frames of the far walls stay, so it reads as glass.
    MEASURED (still _hat at f0 + 12): Mom's face x 50 / y 51 %. The lead's probe: her head box x 32-68 / y 41-57 % the
      whole shot. The stub film's tile (out/test/twentyminutes_tiles/) is DOMINATED BY THE GLASS FRAMES' LINES around
      a small hat: look at it at phone size; a tighter crop or other hidden panes may be needed.
    NOW (stub = the set's stage_b04_long): CAMS "hat", focus on Mom; Mom on mom_glass on the zombie; the zombie in its
      cell; the panes on the lines to her hidden. Hero: Mom.
    """
    f0 = s.frame_start
    mom = C.actor("mom", "sq")
    mp = C.put(mom, f0, "mom_glass")
    C.on_zombie(mom, f0, until=s.frame_end)
    C.zombie(s, "sq", look=mom)
    st.use(s, mom)
    c = C.cam(s, "hat", focus=mom.head, handheld=0.003)
    pts = [(mp[0], mp[1], mp[2] + dz) for dz in (1.0, 1.35, 1.62, 1.95, 2.1)]
    pts += [(mp[0] + dx, mp[1], mp[2] + 1.6) for dx in (-0.3, 0.3)]
    C.panes(s, c["pos"], pts, n=3)
    st.hero(s, "mom", mom)
    C.lights(s, "square")


def sq05_wave(st, s, C, nar):
    """BEAT 5  "I would wave, but our arms don't do that."   frames 272-338 (67 f, 2.79 s), sky gold.
    Words: I 274, would 277, wave 281, but 293, our 297, arms 301, don't 310, do 315, that 320. The voice ends on
    327 (the pause after the line is 0.60 s).
    Before: sq04_hat; after: ce06_bed.

    STORY: Full figure of the baby at the foot of the tower, front three-quarter, camera at its own height, the folded
    arms at the centre of the frame and the stone base behind it. Its head is tilted far up. It rocks forward, makes one
    small hop and lands. The arms never unfold. Hold a beat on the stillness.
    Cast: baby villager (narrator). Effects: baby hop, stone base of the tower.

    MUST BE SEEN, ON WHICH WORD
      frame 1           the baby, head tilted far up, already moving (a rock forward, or the camera drifting)
      "wave"            the try: it rocks forward and makes one small hop in place (towers.hop to its own spot)
      "arms" .. "that"  the folded arms in the middle of the frame, never unfolding; then the stillness held
    SHARED: none (towers' foot_front; the set's camera b05 = towers' foot).
    NEIGHBOURS: before, sq04_hat (Mom at the glass); after, ce06_bed (inside the pod).
    RISKS (story "THE WAVE LINE"): a rock and a hop may not read as trying to wave. Fallback: hold on the folded arms in
      a tighter shot for the second half of the line, with nothing moving but the head tilting further up.
    MEASURED (the set builder, still _arms at f0 + 28): the head far up, the arms y 52 %, front three-quarter.
    NOW (stub = the set's stage_b05): camera "set:b05" (towers' foot, 35 mm f/2.8); the baby on foot_front looking
      0.8 east, 2 south, 4 up; one hop in place on "wave". Hero: the baby.
    """
    f0 = s.frame_start
    baby = C.actor("baby", "sq")
    up = C.put(baby, f0, "foot_front")
    baby.look_at(f0, (up[0] + 0.8, up[1] - 2.0, up[2] + 4.0), ease=0)
    towers.hop(baby, C.at(s, "wave"), C.A["foot_front"])
    st.use(s, baby)
    C.cam(s, "set:b05", focus=baby.head)
    st.hero(s, "baby", baby)
    C.lights(s, "tower")
