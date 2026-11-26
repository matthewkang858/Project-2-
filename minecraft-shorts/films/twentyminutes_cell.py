"""Twenty Minutes, sequence CELL: inside the glass pod at the top of the tower, the zombie's side: the bed and the
zombie in a box, the arms that cannot reach, the fear (twice, from the same window camera). Beats 6, 7, 8 and 23 + the
start of 24 (shots ce06_bed, ce07_reach, ce08_scared, ce23_afraid), sky "gold". One function per shot; the contract
is in films/twentyminutes_common.py (tags "ce...", C.actor, C.cam, C.lights, st.use / st.hero).

THE PLACE (engine/towers.py LAYOUT; films/twentyminutes_set.py): the pod inside x -23..-19, y 18..22, z 10..11 (2 high
  under the glass roof z 12; glass ring x -24..-18, y 17..23). The zombie's cell (-18, 19) in the east wall: the sill
  (-19, 19, 10) on the pod's floor, open air above it, the zombie at (-17.7, 19.5) facing west, its eyes C.zombie_eye
  (z 11.74); its arms reach 0.35 into the pod and stop in the air (to x -18.35); Mom's place 'mom' (-20.5, 19.5) is ONE
  WHOLE EMPTY BLOCK from the arm tips ("The zombie can't reach her": the game's reach ends at x -18.83). The lantern
  (-23, 18, 10) in the front-west corner, the cell's wall torch (-19, 18, 10). Beds, pillows north: white (-23, 21),
  white (-22, 21), Mom's red (-21, 21); the second red bed (-20, 21..22) from gr21 on (the film shows it: you see it in
  ce23). Free floor: rows y 18..20 (but the lantern's and the sill's cells) and the column x -19, y 20..22.
  Places by towers' short names (C.P / C.put): mom, mom_glass, bed_side, bed_beside (before the second bed only),
  back_1 (-22.55, 19.4), back_2 (-22.55, 20.4), back_3 (-21.6, 18.4); the film's narrator_23, mom_23, librarian_23.
  Cutaways (camera only): st.see_through(s, "tower_pod_north" | "_east" | "_south" | "_west" | "_roof").
THE SCOUTING STILLS: out/test/twentyminutes_set_b06_bed_a.png, _b06_bed_b.png, _b07_reach.png, _b08w_window.png,
  _b23w_window.png, _b23_afraid.png, _b24w_window.png (+ _zones.png each).
LIGHT: C.lights(s, "tower") (the lantern and the cell's torch at 1.0; far village torches off).
THIS SEQUENCE OWNS (the contract, amended): CAMS "window" (ce23) and "window_08" (ce08): you may redefine them ONCE as
  constants here (keep ONE lens position for both: "This camera position returns for the last two lines"). FOUR and
  THREE are NOT yours (gm09 / gm10 / gm24 see the same people from the platform).
MOM'S HEAD IS ON THE ZOMBIE IN EVERY FRAME (C.on_zombie / towers.panic with the zombie's eyes: C.pod does it).
TAGS TAKEN (twins): mom_ce, zombie_ce (every shot), cleric_ce, librarian_ce (ce08, ce23), narrator_ce (ce23). New: ce2..
PREVIEWS through render.py: --samples 6 (PREVIEW_SAMPLES["cell"]).
"""
import math

from engine import shots as SH
from engine import towers
from films import twentyminutes_common as TC

# ---------------------------------------------------------------------------------------------------------------
# cameras of this sequence (the contract: CAMS "window" / "window_08" are the cell's; each redefined ONCE below as
# WINDOW / WINDOW_08, used unchanged by the one shot that uses it; ONE lens position for both: TC.CAMS["window"]
# ["pos"], 0.13 from the zombie's right arm, lens and stop unchanged)
# ---------------------------------------------------------------------------------------------------------------


# beat 6: a keyed pan (bearing clockwise from north, pitch) from one fixed lens, the aim keyed through monotone
# cubics (_aim_empty): slow on the bed and Mom through "He gave her a bed", the pan past Mom on "and a", slow on the
# zombie in its window from "zombie" to the cut
CE06_POS = (-20.5, 17.45, 11.3)
CE06_AIM = ((339, 4.0, -12.0), (360, 8.5, -11.0), (382, 47.0, -3.0), (411, 51.0, -2.5))
CE06_LENS = (22.0, 2.8)
CE06_MOM = (-19.5, 22.35, 10.0)          # beside the red bed at its pillow end (bed2's space: free before gr21)

# beat 7: the long lens from outside the back glass (tower_pod_north hidden), north-north-west of the pod so the line
# to the arms passes west of the plug; a slow linear push of 0.5 block
CE07_CAM = dict(pos=(-21.9, 33.0, 11.6), target=(-19.83, 19.15, 11.5), pos1=(-21.82, 32.5, 11.6),
                target1=(-19.83, 19.15, 11.5), lens=60.0, fstop=2.8, ease="linear")
CE07_MOM = (-20.5, 19.25, 10.0)          # 'mom' 0.25 south: her look east is square to the lens (a true profile)

# beat 23: the narrator's head comes round from the back glass (where it was in gp22, watching the player break the
# step) to the zombie: from 69 degrees to his left (the head's reach is 70) in SNAP frames, about the game's head speed
# (LookControl: 10 degrees a tick = 8.3 a frame)
NARRATOR_FROM = (-18.9, 23.2, 11.5)
SNAP = 8


def _pchip(xs, ys, x):
    """Monotone cubic (Fritsch-Carlson) through (xs, ys) at x: no overshoot between keys; the end slopes are the end
    segments' own, so a path keyed this way is already moving on its first frame (films/legday_pens.py)."""
    n = len(xs)
    if x <= xs[0]:
        return ys[0]
    if x >= xs[-1]:
        return ys[-1]
    h = [xs[i + 1] - xs[i] for i in range(n - 1)]
    d = [(ys[i + 1] - ys[i]) / h[i] for i in range(n - 1)]
    m = [d[0]] + [0.0] * (n - 2) + [d[-1]]
    for i in range(1, n - 1):
        if d[i - 1] * d[i] > 0:
            w1, w2 = 2 * h[i] + h[i - 1], h[i] + 2 * h[i - 1]
            m[i] = (w1 + w2) / (w1 / d[i - 1] + w2 / d[i])
    i = max(j for j in range(n - 1) if xs[j] <= x)
    t = (x - xs[i]) / h[i]
    t2, t3 = t * t, t * t * t
    return ((2 * t3 - 3 * t2 + 1) * ys[i] + (t3 - 2 * t2 + t) * h[i] * m[i] + (-2 * t3 + 3 * t2) * ys[i + 1]
            + (t3 - t2) * h[i] * m[i + 1])


def _toward(pos, bearing, pitch, dist=4.0):
    """The point `dist` blocks from `pos` at a compass bearing (degrees clockwise from north) and pitch (up +)."""
    b, p = math.radians(bearing), math.radians(pitch)
    return (pos[0] + dist * math.cos(p) * math.sin(b), pos[1] + dist * math.cos(p) * math.cos(b),
            pos[2] + dist * math.sin(p))


def _aim_empty(s, what, pos, keys, dist=4.0):
    """An empty "ce_<what>_<shot>" keyed on every frame of shot s (and one past its end): the aim of a camera at
    `pos` turning through keys = [(frame, bearing, pitch)] (degrees; monotone cubics in angle, so the pan's speed is
    what the keys say). Never rendered; engine.shots follows an object target."""
    import bpy
    ob = bpy.data.objects.new("ce_%s_%s" % (what, s.name), None)
    s.film.collection.objects.link(ob)
    fr = [k[0] for k in keys]
    for f in range(s.frame_start, s.frame_end + 2):
        b = _pchip(fr, [k[1] for k in keys], f)
        p = _pchip(fr, [k[2] for k in keys], f)
        ob.location = _toward(pos, b, p, dist)
        ob.keyframe_insert("location", frame=f)
    SH._linearize(ob)
    ob.hide_render = True
    return ob


def _bearing_pitch(pos, target):
    """(compass bearing clockwise from north, pitch up) in degrees of the line from pos to target, and its length."""
    dx, dy, dz = (target[i] - pos[i] for i in range(3))
    flat = math.hypot(dx, dy)
    return math.degrees(math.atan2(dx, dy)), math.degrees(math.atan2(dz, flat)), math.sqrt(flat * flat + dz * dz)


def _to_lens(eye, target, cam_pos, degrees):
    """`target` turned about `eye` by up to `degrees` toward the camera (twentyminutes_common.to_lens for a look from a
    point: the zombie's eyes, before it is placed in the shot)."""
    d = (target[0] - eye[0], target[1] - eye[1])
    a0 = math.atan2(d[1], d[0])
    a1 = math.atan2(cam_pos[1] - eye[1], cam_pos[0] - eye[0])
    da = (a1 - a0 + math.pi) % (2.0 * math.pi) - math.pi
    a = a0 + math.copysign(min(abs(da), math.radians(degrees)), da)
    flat = math.hypot(*d)
    return (eye[0] + flat * math.cos(a), eye[1] + flat * math.sin(a), target[2])


def _turned(cam, degrees):
    """cam's target turned `degrees` about the lens (+ = clockwise seen from above: to the frame's right)."""
    b, p, d = _bearing_pitch(cam["pos"], cam["target"])
    return _toward(cam["pos"], b + degrees, p, d)


# beat 8: the set's b08w aim (CAMS "window_08"), turned 1.0 degree to the left (south) on the first frame and drifting
# on to 2.4 degrees, linear: Mom's hat comes in from the safe area's edge (box x 8-37 % with the stub's aim), the
# librarian's head stays clear of the icon column
WINDOW_08 = dict(TC.CAMS["window_08"], target=_turned(TC.CAMS["window_08"], -1.0),
                 target1=_turned(TC.CAMS["window_08"], -2.4), ease="linear")
# beat 23 (+ the start of 24): the lead's re-aimed CAMS "window" on the first frame, drifting 1.2 degrees to the left
# (south), linear, through the hold on "Apparently that"
WINDOW = dict(TC.CAMS["window"], target1=_turned(TC.CAMS["window"], -1.2), ease="linear")


def ce06_bed(st, s, C, nar):
    """BEAT 6  "He gave her a bed, and a zombie in a box."   frames 339-411 (73 f, 3.04 s), sky gold.
    Words: He 341, gave 344, her 350, a 354, bed 356, and 372, a 375, zombie 377, in 388, a 391, box 392. The voice
    ends on 405 (the pause after the line is 0.35 s).
    Before: sq05_wave; after: ce07_reach.

    STORY: Inside the pod, under its low glass roof. Slow pan from Mom's red bed, seen lengthwise from its foot with two
    white beds beyond it, past Mom standing beside it, to the side wall: a one-block cobblestone cell under a stone
    slab, closed at foot level and open at head height. A zombie's head and outstretched arms fill the window, lit by a
    wall torch.
    Cast: Mom (farmer villager), zombie. Effects: red bed (Mom's), two white beds, cobblestone zombie cell with stone
    slab roof and an open window at head height (no glass), wall torch at the cell, lantern on the floor.

    MUST BE SEEN, ON WHICH WORD
      frame 1           the pan already moving (ease_out), the red bed lengthwise from its foot, the white beds beyond
      "bed"             the red bed (focus on it)
      "zombie" .. "box" the cell: the zombie's head and outstretched arms filling the window, the slab over it, the
                        torch below (the focus racked to it)
    SHARED: none. Mom on bed_beside (the second bed's space: allowed here only, before gr21).
    NEIGHBOURS: before, sq05_wave (the foot of the tower, outside); after, ce07_reach.
    MEASURED (the set builder, stills _bed_a at f0 + 2 / _bed_b at the end): the red bed lengthwise with the white beds,
      Mom's hat at the edge; at the end the zombie fills the window over the sill. The technical review (heads at the
      first / middle / last frame): MOM IS OUT OF THE FRAME nearly the whole pan (x 68-130 % at 339, -56..15 at 375,
      -169..-39 at 411), though the story's pan goes "past Mom standing beside it": bring her into the pan (another
      place on its path, or the pan through her) or let the bed and the zombie carry it. The stub's hero is now the
      zombie (in the frame from about 400: x 44-72 / y 30-43 % at 411). The pan: heading 91.7 -> 22.6 degrees,
      ease_out (23 degrees in its first 18 frames).
    NOW (stub = the set's stage_b06): camera "set:b06" (towers' pan_bed, 24 mm, panning to the cell), focus on the red
      bed, racked to the zombie on "zombie"; Mom on bed_beside, head on the zombie; the zombie, arms forward. Hero: the
      zombie.
    """
    f0, f1 = s.frame_start, s.frame_end
    mom = C.actor("mom", "ce")
    C.put(mom, f0, CE06_MOM, toward=C.zombie_eye)
    C.on_zombie(mom, f0, until=f1)
    # the zombie stares at Mom, its look cheated 25 degrees toward the lens (at Mom itself its face is 94 degrees off
    # the lens: a blank green side; she is out of the frame by the time it is in)
    z = C.zombie(s, "ce", look=_to_lens(C.zombie_eye, mom.eye_point(f0), CE06_POS, 25.0))
    st.use(s, mom)
    st.see_through(s, "tower_pod_south")            # the lens stands in the front glass
    aim = _aim_empty(s, "aim", CE06_POS, CE06_AIM)
    C.cam(s, None, pos=CE06_POS, target=aim, lens=CE06_LENS[0], fstop=CE06_LENS[1],
          focus=C.fm.beds["mom"]["pos"])
    C.rack(s, z, C.at(s, "and"), frames=10)
    st.hero(s, "zombie", z)
    C.lights(s, "tower")


def ce07_reach(st, s, C, nar):
    """BEAT 7  "The zombie can't reach her."   frames 412-455 (44 f, 1.83 s), sky gold.
    Words: The 414, zombie 416, can't 428, reach 435, her 442. The voice ends on 447 (the pause after the line is
    0.45 s).
    Before: ce06_bed; after: ce08_scared.

    STORY: Tight profile two-shot on a long lens. On the left the zombie's arms reach out of the window and stop in the
    air. One whole empty block further right, Mom's face, straw hat and nose, looking straight at it. Nothing between
    them but air.
    Cast: Mom (farmer villager), zombie. Effects: zombie arm sway (arms raised, aggressive pose), window sill of the
    cell at the frame edge.

    MUST BE SEEN, ON WHICH WORD
      frame 1           the arms swaying (they sway by themselves), Mom's profile
      "reach"           the arms stopped in the air, the one empty block of air, her face and nose
    SHARED: none (towers' two_shot from behind the back wall: tower_pod_north hidden from the camera).
    NEIGHBOURS: before, ce06_bed; after, ce08_scared (the window camera).
    MEASURED (the set builder, still _reach at f0 + 12): the green arms out of the window at the LEFT EDGE (a sliver:
      look at it at phone size), one empty block, Mom in profile at x 76 / y 49 %. The two-shot is at 45 mm f/2.8 from
      9 blocks: a longer lens from further back (the story's "long lens") would make the arms bigger: try it. The
      lead's probe: Mom's head box x 62-89 / y 42-53 % the whole shot: INTO THE ICON COLUMN (x > 82): re-frame.
    NOW (stub = the set's stage_b07): camera "set:b07" (45 mm), focus on Mom; Mom on 'mom', head on the zombie; the
      zombie aggro (raised arms); the north wall seen through. Heroes: Mom.
    """
    f0, f1 = s.frame_start, s.frame_end
    mom = C.actor("mom", "ce")
    C.put(mom, f0, CE07_MOM, toward=C.zombie_eye)
    C.on_zombie(mom, f0, until=f1)
    towers.panic(mom, f0, f1, C.zombie_eye, seed=TC.PANIC_SEED, amount=0.6, turns=False)    # a held tremble
    C.check_look(mom, f0, C.zombie_eye, until=f1, what="the zombie")
    C.zombie(s, "ce", aggro=False, look=mom)
    st.use(s, mom)
    st.see_through(s, "tower_pod_north")
    C.cam(s, None, focus=mom.head, **CE07_CAM)
    st.hero(s, "mom", mom)
    C.lights(s, "tower")


def ce08_scared(st, s, C, nar):
    """BEAT 8  "It doesn't have to."   frames 456-503 (48 f, 2.00 s), sky gold.
    Words: It 458, doesn't 461, have 468, to 475. The voice ends on 483 (the pause after the line is 0.95 s).
    Before: ce07_reach; after: gm09_golem.

    STORY: From beside the zombie cell, looking across the pod. Mom, a cleric and a librarian are backed against the far
    glass, three heads turned toward the lens side, where the zombie's arm is a soft green shape at the frame edge.
    They tremble and turn on the spot. Behind them, through the glass, the empty stone platform. This camera position
    returns for the last two lines.
    Cast: Mom (farmer villager), cleric villager, librarian villager, zombie (foreground, out of focus). Effects:
    villager panic tremble and quick turns, golem platform visible through the glass, empty.

    MUST BE SEEN, ON WHICH WORD
      frame 1           the three already trembling (towers.panic from f0), the arm blur at the left edge
      "have"            three faces toward the lens' side, trembling, turning on the spot, heads ON the zombie
      the whole shot    the platform empty behind them (it reads in gm09)
    SHARED: CAMS "window_08" (ce23's CAMS "window" position, lens and stop, aimed 0.35 further north), THREE (the same
      three places as gm09 / gm10, where they are seen from the platform), the zombie's arms FORWARD (aggro=False:
      raised arms leave this frame).
    NEIGHBOURS: before, ce07_reach; after, gm09_golem (the platform: the golem comes; the three behind the glass).
    FALLBACKS APPLIED: towers' "impossible" zombie arm at the frame edge is had: the lens 0.13 from the zombie's right
      arm (the set's b08w / b23w): a dark green blur down the left edge (pixels about (46, 68, 37)).
    MEASURED (the set builder, still b08w_window at f0 + 30, this aim): Mom 20 %, the cleric 46 %, the librarian 66 %,
      all y 47-48 %. (With CAMS "window", ce23's aim, tools.twentyminutes_geo ce08_scared:480 put their eyes at 32 /
      58 / 79 % and the librarian's head to x 84.5 %, into the icon column: that is why ce08 has its own aim.)
      The lead's still out/test/twentyminutes_scout_ce08_scared_485.png (+ _zones): three faces to the lens, the arm
      blur at the left edge; tools/twentyminutes_palette 485 passes every rule (hero Mom x 17-35 %, y 40-50 %). The
      probe's head box (hat included): Mom x 8-37 % (on the safe edge at 479), y 39-50. Heads on the zombie: within
      2.7 degrees all shot (tools/twentyminutes_probe looks).
    NOW (stub): CAMS "window_08", focus on the cleric; THREE trembling (C.pod(..., panic=True)); the zombie, arms
      forward. Hero: Mom.
    """
    who = C.pod(s, "ce", TC.THREE, panic=True)
    C.zombie(s, "ce", aggro=False, look=who["mom"])
    C.cam(s, None, focus=who["cleric"].head, **WINDOW_08)
    st.hero(s, "mom", who["mom"])
    C.lights(s, "tower")


def ce23_afraid(st, s, C, nar):
    """BEAT 23+24  "I'm afraid of the zombie."  "Apparently that" (of: Apparently that counts.)   frames 1400-1472 (73
    f, 3.04 s), sky gold.
    Words: I'm 1402, afraid 1406, of 1417, the 1420, zombie 1421, Apparently 1453, that 1467.
    Before: gp22_step; after: gm24_counts.

    STORY (beat 23, and beat 24 up to "counts": "Same shot, held"): The camera from beside the zombie cell again. The
    narrator's head snaps round to the lens side. The zombie's arms reach from the window at the foreground edge. He
    trembles on the spot next to Mom: same height, same pose, both staring at it. The two red beds sit side by side
    below them. [24] Same shot, held. (The golem through the glass and the rack focus: the story's own fallback, the
    cut on "counts" to the platform framing, gm24_counts.)
    Cast: grown narrator, Mom (farmer villager), cleric villager, librarian villager, zombie (foreground edge).
    Effects: villager panic tremble, the narrator's matched to Mom's; two red beds side by side; zombie arm sway.

    MUST BE SEEN, ON WHICH WORD
      frame 1 .. "afraid"   the narrator's head SNAPS round to the lens' side (to the zombie): on f0 it is elsewhere
                        (where he looked in gp22: level, toward the back glass), then on the zombie in 2-3 frames
      "zombie"          the narrator and Mom side by side, same height, same pose, trembling ALIKE (PANIC_SEED: the
                        same tremble frame for frame), both staring at the zombie just over the lens
      "Apparently" .. "that"   the shot HELD (nothing new: the fear goes on); the cut on "counts" goes to gm24
    OWNED: CAMS "window" (ce08's lens position: keep it one position). SHARED ACROSS SEQUENCES (frozen): FOUR (the same
      four places as gm24, where they are seen from the platform), PANIC_SEED; the second bed is in this shot (the
      film's BED2_FROM). The zombie's arms forward (aggro=False).
    NEIGHBOURS: before, gp22_step (the narrator watching Steve break the step, from outside); after, gm24_counts.
    KNOWN (the set builder): "the two red beds below them" cannot be had from beside the cell: the beds are north of
      the four; one red bed shows at the right edge of the window framing (both side by side are seen in gr21).
    MEASURED (the set builder, still b23w_window at f0 + 20): the arm blur at the left edge; Mom 26 %, the narrator
      57 %, the librarian between them behind (41 %), the cleric on back_2 (79 %); a red bed at the right edge. With
      b23w's aim MOM'S HEAD BOX WAS x 3-43 %, cut by the left edge (both reviews): CAMS "window" is now aimed 0.35
      further south from the same position (the lead; tools.twentyminutes_geo ce23_afraid:1440 and the probe): Mom
      x 10-49 / y 35-51 %, the narrator 51-74 / 34-50 %, the librarian 40-55 %, the cleric 78-92 % (cut by the right
      edge: not a hero), the arm's blur still over the left edge (out/test/twentyminutes_scout_ce23_afraid_1440_zones.png,
      270x480: both faces read, the hat whole). Heads on the zombie: within 3.0 degrees (probe looks).
    NOW (stub): CAMS "window", focus on the narrator; FOUR trembling (C.pod(..., panic=True): Mom and the narrator
      with PANIC_SEED); the zombie, arms forward. (The head snap is not staged yet.) Heroes: the narrator, Mom.
    """
    f0, f1 = s.frame_start, s.frame_end
    # FOUR unchanged (places, PANIC_SEEDS): C.pod for the three, the narrator by hand with the same place, facing and
    # seed, so that his head can come round to the zombie from where it was in gp22
    who = C.pod(s, "ce", [w for w in TC.FOUR if w[0] != "narrator"], panic=True)
    narr = C.actor("narrator", "ce")
    p = C.P(dict(TC.FOUR)["narrator"])
    narr.place(f0, p, TC.yaw_to(p, C.zombie_eye))
    narr.look_at(f0, NARRATOR_FROM, ease=0)        # still on the back glass (gp22: watching the player)
    towers.panic(narr, f0, f1, C.zombie_eye, seed=TC.PANIC_SEEDS["narrator"], look=False)
    narr.track(f0, f1, C.zombie_eye, step=2, ease=SNAP)
    C.check_look(narr, f0 + SNAP, C.zombie_eye, until=f1, what="the zombie")
    st.use(s, narr)
    who["narrator"] = narr
    C.zombie(s, "ce", aggro=False, look=who["mom"])
    C.cam(s, None, focus=narr.head, **WINDOW)
    st.hero(s, "narrator", narr)
    st.hero(s, "mom", who["mom"])
    C.lights(s, "tower")
