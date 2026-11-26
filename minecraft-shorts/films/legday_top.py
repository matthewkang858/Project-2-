"""Leg Day, sequence TOP: the top of the anvil wall: the twelve sticky pistons, the dust line, the lever. Beats 13,
14, 18 (golden) and 24 (dusk, the film's last shot). Shots tp13_sticky, tp14_why, tp18_lever, tp24_reloading. One
function per shot; the contract is in films/legday_common.py (tags "tp...", C.actor / C.narrator / C.patrol, C.cam,
C.lights, C.appear, st.use / st.hero).

STATUS: SHOT by the top director (from the lead's stubs). Every shot docstring carries the beat, its words with their
frames, what must be seen on which word, BEFORE (what the stub did), NOW (what the shot does, frame by frame) and
MEASURED (on the build: tools/legday_top_probe, the stills, the palette check, the motion preview).

THE SEQUENCE NOW
  tp13  from east of the twelfth gap, out over the road: the twelfth sticky piston placed on "put" and its arm
        shooting out TOWARD the lens (the slime-green face square to us, bare until the plank goes on at 839); the
        narrator above it in the top third, anvil 11 on its plank and arm at the left; a slow push and pan
  tp14  from the east over the road, above the shelf: the eleven anvils on their planks across the frame, Steve
        walking in along the wall top, setting the twelfth on the bare plank ON "why" and walking back; the narrator
        at the lever watching him all shot (tp24 repeats this angle and this action at dusk)
  tp18  the lever big, from past the wall top's north-west corner: the narrator three-quarter, his thin arm on the
        handle, the lever's swap and the WHOLE lit dust line dark on 1109 along the wall top behind him; NO patrol in
        the frame (the clock cannot be shown here truthfully above the caption band: see tp18's docstring)
  tp24  the lead's east camera with a longer push: the chipped row on its planks, Steve setting the twelfth on
        "call" and walking off, the narrator's right hand rising to the lever on "reloading" and staying there, his
        torch-lit face, a last look down at the empty road; hold, then black
  Screen direction: tp13 and tp14 both from the road side (east), 45-60 degrees apart; tp18 from the back (west)
  side of the wall top, after the cows (pn17) and before the road (rd19); tp24 from the east, the angle of tp14.
TOOLS: tools/legday_top_probe.py (one build: every head in the frame with face px and angle, the lever's handle and
  the hands' distance to it, st.hero's boxes, the wall's named points, static camera variants and quick stills into
  the scratchpad); tools/legday_top_palette.py (palette_check on a still already rendered at 540x960 / 16 samples,
  and its Reels zones); tools/legday_top_state.py (legday_state's "no body inside a block" for these four shots,
  every 2 frames: legday_state itself runs past the 290 s a command may take on the loaded machine).
THE EVIDENCE (540x960, 16 samples, with the Reels zones; every one looked at):
  tp13  out/test/legday_top_tp13_sticky_828[_zones].png      the green face bare at the arm's end, toward the lens;
        palette_check passes (G/R 0.95; narrator 100 %, the twelfth 94 % inside the safe area)
  tp14  out/test/legday_pal_tp14_why_878[_zones].png          the twelfth anvil just set at the right end of the row;
        palette_check passes (G/R 0.94; Steve 100 %, the twelfth anvil 99 %)
  tp18  out/test/legday_pal_tp18_lever_1110[_zones].png       the arm on the handle, the lever off, the dust dark;
        palette_check passes (G/R 0.96; lever 100 %, narrator 100 %)
  tp24  out/test/legday_pal_tp24_reloading_1550[_zones].png   the hand on the lever, the chipped row on its planks;
        palette_check passes (G/R 0.95; row 88 %, narrator 100 %)
  MOTION: out/test/legday_top_motion.mp4 (12 fps, every second frame of all four shots, 270x480, 9 samples: render.py
        previews out/preview/legday/270x480_9spp_step2, and for tp24 1531-1571 the same frames rendered through
        tools/legday_top_probe at the same settings, to finish inside the time the machine allowed); looked at frame
        by frame around every action (the place on 819, the plank on 839, the set on 876, the flip on 1108-1109, the
        set on 1498, the hand on the lever 1510-1518) and every cut.

THE PLACE (films/legday_set.py, "THE ANVIL WALL"): the walkway is z 18 (the wall's three columns x -4..-2, y 27..60).
  The row: twelve sticky pistons in the top course (-2, 46..57, 17) facing EAST over the road; extended, the head at
  (-1, y, 17) and the plank on it at (0, y, 17), two blocks out from the face; the anvils on the planks (0, y, 18).
  C.row.pistons[i] / C.row.blocks[i] (planks) / C.anvils[i] / C.anvils_dusk[i]: i 0 = the south one (y 46), 11 =
  the north one (y 57), next to the lever: "THE TWELFTH". The dust (-3, 46..59, 18) on the blocks behind the
  pistons, lit from the lever: power 15 by the lever .. 2 at the far (south) end. The lever: a floor lever on its
  pier (-3, 60, 19) at the wall top's NORTH end, facing east; lever_narrator (-1.7, 60.28, 18) facing west (east
  of the lever: Lever.stand()), narrator_edge (-1.25, 60.5, 18). place_12th (-2.55, 57.55, 18) facing east (beside
  the twelfth gap), set_anvil_12th (-2.6, 58.45, 18) facing south-east (Steve on the dust, setting anvil 12 on plank
  12), wall_top_north (-2.5, 59.4, 18), wall_top_south (-1.5, 44.6, 18), stair_top (-0.5, 44.75, 18). Paths
  wall_top (x -1.5, over the pistons) and wall_top_dust (x -2.5, on the dust). Lanterns on the wall top: the front
  edge over the stair, (-4, 60, 18) beside the lever (the face key), the back edge over the shelf.
  The terrain north of the wall is carried on to y 150 (a camera on the wall top looking north sees meadow, not
  void); the patrol's road "patrol_road" (0.5, 84 -> 40) comes from there.
THE WORLD STATE IN YOUR HANDS (legday_common "THE WORLD STATE"): the twelfth piston (tp13: place + extend, then its
  plank), the twelfth anvil of the day set (tp14: C.appear), the lever OFF and the dust dark (tp18), the twelfth
  anvil of the dusk set (tp24: C.appear). NOT the row's retraction (rd19's) nor the re-arm (the lead's, before
  cl22). Before tp13 the twelfth piston is retracted and invisible and its plank hidden (the lead keys that in
  LegDay.__init__); Piston.place(f) makes it appear ON f, "a piston placed where it is powered extends in the same
  tick": p.place(f, player=efe); p.extend(f) (the set builder checked: short head ON f, long head f + 1, out by f + 3).
THE SKIES: tp13 / tp14 / tp18 "gold" (the sun due east, low: the wall top's road edge is lit); tp24 "dusk" (the sun
  down in the west, behind the wall top's back: the narrator's face keyed by his own redstone torch at
  LS.B24_TORCH_WATTS (120 W), the redstone "a weak light in the game ... key his face with a boosted lantern beside
  the lever and let the torch be the red accent": the story's alternative, if the torch key is not enough).
  tools/palette_check failed "stone not magenta" on the dusk wall top from the set's b24 (G/R 0.90, warm); the stub's
  TP24_CAM from the east passes (0.95 on 1545, the row hero 80 % inside the safe area): if yours fails, known and accepted
  (films/legday.py SKIES). Do not boost lanterns to fix it.
THE PATROL CLOCK (legday_common, after review): (the stub's) the patrol of tp18 was C.march_patrol("tp18"), the same
  march as rd15's and rd19's. NOW tp18 shows no patrol (the lever big; see tp18's docstring, THE CHOICE). On "flipped" (1108) the captain's feet are at y 57.4, just short of the shelf's north end (plank 12 is
  y 57-58), his file behind him at 59.4 .. 65.4 on the open road past the wall's north end (y 61): THE STORY'S
  PICTURE, "on the open road just short of the shelf". FROM ANY CAMERA OVER THE WALL TOP THE WALL ITSELF HIDES THEM
  (measured: out/test/legday_tp18var_tp18_lever_1110_v0.png, the set's b18 view: the meadow beyond, empty). Only a
  camera hanging out past the wall top's north-east corner (x > -1.3, y > 60.5) sees the lever and the file below in
  one frame (out/test/legday_scout_tp18_lever_1110[_zones].png). The first stub marched a far patrol of its own 20
  blocks up the road (23 blocks behind rd19's at the same frames): the lever was flipped with nobody near the trap.
  The anvils in hand (C.carry_anvil): whole in tp14 (the morning), CHIPPED in tp24 (the same anvils, carried back
  up after the fall: legday_common THE CHIPPED ANVILS; the dusk set on the shelf is chipped too).
TAGS (twins): efe_tp (tp13: the piston and the plank), efe_tp2 (tp14, soft, his torch), efe_tp3 (tp18: empty right
  hand for the lever), efe_tp4 (tp24: the torch in his LEFT hand, as his key, the right arm for the lever),
  steve_tp (tp14, a whole anvil), steve_tp2 (tp24, a chipped anvil). (No patrol twin: tp18 shows none.)
LIGHT: C.lights(s, "gold" | "dusk", near=(-2.0, 52.0, 18.0), radius=12..14), once per shot; no fill, no boost.
PREVIEW samples for render.py previews: 9 (legday_common.PREVIEW_SAMPLES).
"""
import math

from engine import players, redstone
from films import legday_common as LC
from films import legday_set as LS

WALK_TAIL = 0.26          # blocks a walking player slides after the input is released (engine.players: v g / (1 - g))

# ---------------------------------------------------------------------------------------------------------------
# this sequence's own cameras (starts: the set builder's suggestions; yours to change)
# ---------------------------------------------------------------------------------------------------------------
# tp13: east of the twelfth gap, out over the road, a little north and above the walkway: the twelfth arm shoots out
# TOWARD the lens (its slime-green face to us), the narrator above it, the near anvils on their planks to the left
TP13_CAM = dict(pos=(3.7, 60.4, 20.3), target=(-1.58, 56.63, 16.95), pos1=(3.35, 60.05, 20.15),
                target1=(-1.95, 57.25, 16.95), lens=26.0, fstop=4.0)
GAP12 = (-1.5, 57.5, 17.5)         # the twelfth gap (-2, 57, 17) in the top course, at the narrator's feet
ARM12_END = (0.0, 57.5, 17.5)      # the end of the twelfth arm, extended: its green face (the plank goes on it)
# tp14: from the EAST over the road, above the shelf (the angle tp24 repeats at dusk: the same action, the twelfth
# anvil set from set_anvil_12th, morning and evening): Steve walks in along the wall top with his anvil, stops at the
# last bare plank, sets it (in front of him, toward the lens) and walks back the way he came; the narrator by the
# lever watches him. The sun (east) is behind the lens: the faces lit, the anvils' shadows short
TP14_CAM = dict(pos=(5.2, 51.6, 20.4), target=(-1.37, 57.47, 17.68), pos1=(4.85, 52.0, 20.35),
                target1=(-1.45, 57.65, 17.75), lens=26.0, fstop=2.8)
TP18_CAM_FILE = dict(pos=(-0.6, 62.0, 21.0), target=(-2.0, 59.6, 13.0), pos1=(-0.7, 61.9, 20.9),
                     target1=(-2.0, 59.55, 13.0), lens=16.0, fstop=5.6)     # the stub's (the lever and the file)
# tp18 (CHOSEN): the lever big, from past the wall top's NORTH-WEST corner, above the walkway: the narrator's face
# three-quarter beside the lever with his thin arm on it, the lit dust line receding south along the wall top
# behind him (it goes dark all along its length on "flipped"), the shelf with its anvils beyond on the left
TP18_CAM = dict(pos=(-3.75, 63.4, 20.5), target=(-1.3, 58.0, 18.0), pos1=(-3.55, 63.0, 20.35),
                target1=(-1.35, 58.0, 18.0), lens=26.0, fstop=2.8)
TP18_CAM_LEVER = dict(LC._set_cam("b18"), pos1=(-3.55, 58.05, 20.25))   # the set's b18: the lever big, NO patrol
# tp24: from the EAST, over the road, looking back WNW and down at the row: every anvil of the re-armed row reads as
# standing on its plank, receding to the narrator at the lever (out/test/legday_scout_tp24_*): the row is the hero
TP24_CAM = dict(pos=(5.9, 50.6, 20.6), target=(-1.6, 58.4, 16.7), pos1=(5.1, 52.0, 20.7),
                target1=(-1.75, 58.8, 16.45), lens=32.0, fstop=4.0)


PLANK12_TOP = (0.5, 57.5, 18.1)     # the top of the twelfth plank: where the twelfth anvil is set (tp14, tp24)
ROW_OUT = (0.6, 52.0, 18.6)         # tp24: out over the armed row
ROAD_BELOW = (1.6, 50.0, 13.0)      # tp24: down toward the empty road at the wall's foot


def _hand_on(p, frame, target, ease=8):
    """A player's empty right hand lifted to `target` (a lever's handle) over `ease` frames from `frame` and held
    there: the arm's forward lift (rotation x, as Character.raise_arm) and its sideways swing (rotation z) are searched
    on the evaluated rig (a pattern search like engine.redstone's reach) so that the grip is nearest the target on
    frame + ease. Returns (miss in blocks, lift degrees, swing degrees)."""
    from mathutils import Vector

    from engine import characters as CH
    arm, f1 = p.arm_r, frame + ease
    tgt = Vector(target)

    def put(ax, az):
        CH._ease(arm, "rotation_euler", 0, frame, f1, -math.radians(ax))
        CH._ease(arm, "rotation_euler", 2, frame, f1, math.radians(az))
        return (Vector(p.item_point("right", f1)) - tgt).length

    best = (put(60.0, 0.0), 60.0, 0.0)
    step = 16.0
    while step >= 1.0:
        moved = False
        for dx, dz in ((step, 0.0), (-step, 0.0), (0.0, step), (0.0, -step)):
            ax, az = min(120.0, max(0.0, best[1] + dx)), min(80.0, max(-80.0, best[2] + dz))
            d = put(ax, az)
            if d < best[0] - 1e-4:
                best, moved = (d, ax, az), True
                break
        if not moved:
            step *= 0.5
    put(best[1], best[2])
    return best


def _hold(p, item, frame=None):
    """p.hold(item) when engine.players knows the item (a block item it cannot build raises ValueError)."""
    try:
        return p.hold(item, frame=frame)
    except ValueError as e:
        print("[legday_top] %s cannot hold %s: %s" % (p.name, item, e))
        return None


def tp13_sticky(st, s, C, nar):
    """BEAT 13  "Under each anvil, I put a sticky piston."   frames 784-852 (69 f, 2.88 s), sky gold.
    Words: Under 786, each 793, anvil 800, I 816, put 819, a 822, sticky 824, piston 833.

    STORY: About 3.0 s. Camera just outside the top of the wall, looking back along the row: sticky pistons in the top
    course, each with its arm out over the drop, one oak plank on the end of each arm and an anvil standing on each
    plank, eleven in all. In the last gap the narrator sets the twelfth sticky piston, slime-green face showing for an
    instant. The dust behind it is already lit, so its arm shoots out at once, bare, and he sets one oak plank on the
    end. Behind the pistons a lit line of redstone dust runs to one lever, bright at the lever and duller toward the
    far end.
    Cast: Narrator (Efe, slim-arm model). Effects: twelve sticky pistons, eleven already extended; sticky piston
    placed and extending at once, slime-green face visible; oak plank blocks on the piston arms, one placed in shot;
    eleven anvils as blocks; lit redstone dust line fading with distance from the lever; lever; block placing.

    MUST BE SEEN, ON WHICH WORD
      frame 784       the row of eleven armed pistons with planks and anvils (SHELF "eleven"), the narrator at the
                      twelfth gap, moving
      "anvil" 800     the anvils on their planks, read as standing ON the planks held out by the arms
      "put" 819       the twelfth sticky piston placed (the green slime face toward the lens for an instant), its arm
                      shooting out at once, BARE (the dust is lit)
      "piston" 833 .. ~845   he sets one oak plank on the end of the arm (C.row.blocks[11].show(f, True), a swing)
      the dust        lit, bright by the lever, duller toward the far end (power 15 .. 2: the set does it)
    SHARED: place_12th. THE WORLD STATE: you key C.row.pistons[11].place / extend and C.row.blocks[11].show here.
    NEIGHBOURS: before, cl12_legday (the legs on the stair); after, tp14_why (Steve brings the twelfth anvil).
    RISKS (story): "the viewer must understand that each anvil stands on a plank held out by a piston arm, or the drop
      makes no sense. The green face going in, the arm shooting out and the plank going on must all be in the one
      shot. Fallback: cut the plank placing and show the twelfth piston already carrying its plank; he only places
      the green-faced piston behind it in a first take from the wall top."
    BEFORE (the set builder's b13 / the stub): from beyond the north end, 24 mm, looking back along the row; the green
      head a soft blur in the still (it is mid-extension on the frame: motion blur), the narrator's eyes at x 78-80 %.
    NOW: TP13_CAM, 26 mm f/4, from EAST of the twelfth gap out over the road, a little north and 2.3 above the walkway
      (3.7, 60.4, 20.3), with a slow push in and a small pan right (ease_out: at speed on frame 1): the twelfth arm
      shoots out TOWARD the lens, so its slime-green face is square to us and stays bare at the end of the arm from
      "put" to the plank (821-838), the narrator above it in the top third, anvil 11 on its plank with its arm under it
      at the left, the lit dust on the walkway.
      784-805   "Under each anvil": the sticky piston in his hand, his eyes along the row (to the far end)
      808-815   his head goes down to the gap at his feet (the game's 35 degree pitch limit)
      818 / 819 the swing; the piston there ON "put" and firing at once (short head 819, out by 822: the face square
                to the lens, motion-blurred only on 819-821); his head follows the arm out (820-824)
      823       the planks in his hand (the hotbar); 838 the swing, 839 the plank on the arm ("piston" + 6)
      843-853   his eyes back along the row: twelve
      focus a point between the arm's end (5.2 blocks) and his face (6.5); heroes the narrator, the twelfth piston.
    MEASURED (tools/legday_top_probe, the built camera): the narrator's eyes x 72 % y 21 % on 796, x 62 % y 19-20 %
      on 821-841 (face 57-59 px, 17-24 degrees off the lens while he follows the arm, 89 degrees on 796 while he looks
      along the row); his head box y 15-24 % (inside the top of the safe area); the green face (the arm's end) y 45-60 %;
      plank 12 x 25-33 % y 58 %. Light: the sun (az 0) is 150 degrees off the lens axis (front light, as the face of
      the wall is lit; short shadows). Stills and palette: see the module docstring, THE EVIDENCE.
    """
    f0, f1 = s.frame_start, s.frame_end
    efe = C.actor("efe", "tp")
    C.put(efe, f0, "place_12th")                           # facing east, the gap at his feet
    _hold(efe, "sticky_piston")
    f_put = C.at(s, "put")
    f_set = C.at(s, "piston") + 6
    efe.look_at(f0, (0.5, 54.5, 18.6), ease=0)             # "Under each anvil": his eyes on the row ...
    efe.look_at(f0 + 2, (0.5, 49.5, 18.6), ease=14)        # ... along it, to the far end
    efe.look_at(f_put - 11, GAP12, ease=7)                 # down to the gap at his feet before "put"
    p12 = C.row.pistons[11]
    p12.place(f_put, player=efe)                           # his swing on f_put - 1; there ON f_put ...
    p12.extend(f_put)                                      # ... and it fires at once (the dust is lit): bare
    efe.look_at(f_put + 1, ARM12_END, ease=4)              # following the arm out
    _hold(efe, "oak_planks", frame=f_put + 4)              # the hotbar: the planks
    efe.attack(f_set - 1)                                  # one oak plank on the end of the arm
    C.row.blocks[11].show(f_set, True)
    efe.look_at(f_set + 4, (0.5, 51.5, 18.6), ease=10)     # and back along the row: twelve
    st.use(s, efe)
    C.cam(s, None, focus=(-1.0, 57.6, 18.3), **TP13_CAM)   # between the arm's end (5.2) and his face (7.0)
    st.hero(s, "narrator", efe)
    st.hero(s, "the twelfth", *p12.objects)        # (a property)
    C.lights(s, "gold", near=(-1.0, 54.0, 18.0), radius=12.0)


def tp14_why(st, s, C, nar):
    """BEAT 14  "Nobody asked why."   frames 853-902 (50 f, 2.08 s), sky gold.
    Words: Nobody 855, asked 867, why 876. The pause after it (0.8 s) is the story's turn: the patrol comes next.

    STORY: About 2.0 s. Ground-level on the wall top beside the lever, the glowing dust line leading away from the
    lens. Steve's feet step right over the lit dust, past the lever and the piston backs. He sets his anvil down on
    the last bare plank and walks on, never once looking down. Soft in the background the narrator stands and
    watches him go.
    Cast: Steve, Narrator (Efe, slim-arm model). Effects: anvil held, then placed as the twelfth block; sticky pistons
    extended with planks; lit redstone dust line in the foreground; lever.

    MUST BE SEEN, ON WHICH WORD
      frame 853       Steve already walking over the dust toward the lens, the anvil in his hand
      "Nobody" 855 .. "asked" 867   his feet stepping right over the lit dust (the answer under his feet)
      "why" 876       he sets the anvil on the last bare plank (plank 12, beside the lever): C.appear(s,
                      C.anvils[11], f) with his swing on f - 1 and his hand empty from f (hold(None, frame=f))
      to ~900         he walks on, never once looking down; the narrator soft in the background, watching him go
    SHARED: set_anvil_12th (= tp24's), the lever.
    THE WORLD STATE: you key the twelfth anvil's appearance (C.appear); SHELF "eleven" shows the other eleven.
    NEIGHBOURS: before, tp13_sticky; after, rd15_pillagers (the meadow: the patrol).
    BEFORE (the set's b14 / the stub): on the walkway by the lever looking south, Steve walking toward the lens; the
      anvil's set happened OUT of the frame (plank 12 at x -114 %, Steve's face 82 px at 1.2 blocks from the lens).
      Every camera on the wall top near the lever has the same problem: set_anvil_12th (shared) is 3.1 blocks west of
      plank 12, so from within 6 blocks the two are 40-60 degrees apart. Scouted and rejected (scratchpad stills
      r1/r2/r3_tp14_*): low on the piston column looking north (the walkway a blur over half the frame, the set at the
      far end of a row seen end-on: the twelfth anvil does not separate from the eleven); the plank in the foreground
      from the east at plank height (the new anvil hides Steve).
    NOW: TP14_CAM, 26 mm f/2.8, from the EAST over the road, 2.4 above the walkway (5.2, 51.6, 20.4) looking WNW and
      down at the row, a slow push (ease_out). THE SAME ANGLE AS tp24 (the last shot repeats this action at dusk: the
      twelfth anvil set from set_anvil_12th, morning and evening). The eleven anvils on their planks across the
      middle of the frame, plank 12 bare at the right end of the row (under the narrator), the dust a red line on the
      walkway behind the pistons.
      853       Steve already walking north along the dust at the game's pace (no ramp in), the whole anvil in his
                right hand, entering from the left edge; head level (he never looks down)
      870-876   he slides to a stop on set_anvil_12th (the input released so the 0.26 block slide ends on 872), turns
                to the last bare plank (870-874), swings (875) and the anvil stands on plank 12 ON "why" (876), his
                hand empty from 876; his head level again from 879
      881-902   he walks back south the way he came (the only way down: the stair), toward the left edge, head level
      the narrator (efe_tp2, his redstone torch: the redstoner) at lever_narrator facing down the wall top, his head
                following Steve all shot (track): he watches him come, set it and go.
      focus Steve's head; heroes Steve, the twelfth anvil.
    MEASURED (tools/legday_top_probe, the built camera, before the last 2-degree pan right): Steve's eyes x 16 % y 34 %
      on 856 (44 px, walking away three-quarter), x 52 % y 33 % on 878 (36 px, 26 degrees off the lens), x 19 % y 34 %
      on 898 (45 px); the narrator's eyes x 77 % y 33 % (34-35 px, 48-64 degrees off). After the pan, palette_check
      tp14@878 (rendered): Steve x 45-52 % y 32-36 %, the twelfth anvil x 62-83 % y 42-53 % (99 % inside; it was 82 %
      inside, under the icon column, before the pan); every check passes (stone G/R 0.94). All clear of the caption
      band (the planks sit in it). Light: the sun (az 0) 135 degrees off the lens axis (frontal; the faces lit).
      Stills: see the module docstring, THE EVIDENCE.
    """
    f0, f1 = s.frame_start, s.frame_end
    steve = C.actor("steve", "tp")
    e = C.P("set_anvil_12th")
    f_set = C.at(s, "why")
    # at the game's walking pace from the first frame (no ramp in), the input released so that the slide (0.26 block)
    # ends on the spot four frames before "why": the start is that far back along the dust
    run = WALK_TAIL + players.WALK_SPEED * (f_set - 4 - f0) / 24.0
    a = (e[0] + 0.05, e[1] - run, LS.WALK_Z)
    efe = C.narrator("tp2")                                # his redstone torch: the redstoner, soft at the lever
    C.put(steve, f0, a, toward=e)
    C.put(efe, f0, "lever_narrator", toward=(-1.7, 52.0))   # facing down the wall top: toward Steve, the lens
    C.carry_anvil(steve)                                   # the morning: whole
    efe.look_at(f0, steve.eye_point(f0), ease=0)
    steve.look_at(f0, (e[0], e[1] + 2.0, 19.4), ease=0)    # straight ahead, level: never looking down
    end1 = steve.walk(f0, [a, e], ramp=(False, True))
    plank_top = (0.5, 57.5, 18.05)
    steve.face(f_set - 6, plank_top, ease=4)               # turned to the last bare plank ...
    steve.look_at(f_set - 6, plank_top, ease=4)
    steve.attack(f_set - 1)                                # ... the swing, and the anvil stands on it ON "why"
    C.appear(s, C.anvils[11], f_set)
    steve.hold(None, frame=f_set)
    steve.look_at(f_set + 3, None, ease=5)                 # head level again: he never looks at what is under it
    back = (-2.5, 51.5, LS.WALK_Z)
    steve.walk(max(f_set + 5, end1), [e, back], ramp=(True, False))   # and walks on, back down the wall top
    efe.track(f0, f1, steve, step=3, ease=3)               # the narrator watches him come, set it and go
    st.use(s, steve, efe)
    C.cam(s, None, focus=steve.head, **TP14_CAM)
    st.hero(s, "steve", steve)
    st.hero(s, "the twelfth anvil", *C.anvils[11].objects())
    C.lights(s, "gold", near=(-2.0, 56.0, 18.0), radius=12.0)


def tp18_lever(st, s, C, nar):
    """BEAT 18  "I flipped one lever."   frames 1103-1141 (39 f, 1.62 s), sky gold.
    Words: I 1105, flipped 1108, one 1117, lever 1123.

    STORY: About 2.0 s. Close on the lever on the wall top: the narrator's thin arm reaches in and flips it. The whole
    glowing line of redstone dust goes dark in the same instant, as it does in the game. Soft and far below, on the
    open road just short of the shelf, the captain's banner moves toward it.
    Cast: Narrator (Efe, slim-arm model), patrol captain far below, out of focus. Effects: lever switching off,
    redstone dust line going dark all at once, ominous banner on the captain's head.

    MUST BE SEEN, ON WHICH WORD
      frame 1103      the lever big, the dust lit, the narrator's thin arm coming in
      "flipped" 1108  the lever flips (redstone.flip_by(efe, C.lever, f, ...): the game's model swap) and the WHOLE
                      dust line goes dark on that frame (C.wire.unpower(t))
      the patrol      ON THE CLOCK (C.march_patrol("tp18"): never another march): on "flipped" 1108 the captain at
                      y 57.4 entering under the shelf's north end (the shelf may hide him: that is the truth), his
                      file behind him at 59.4 .. 65.4 on the open road past the wall's north end, walking toward the
                      trap; at 1141 the captain at 55.1
    SHARED: lever_narrator; THE PATROL CLOCK. THE WORLD STATE: you key the lever off and the dust dark; NOT the row:
      the pistons snap back IN rd19 (the overlapping action of the cut: the row is not in this frame, the lever not
      in rd19's). TIME RUNS STRAIGHT THROUGH THE CUT (never compressed): the lever goes off on 1108, the patrol walks
      on, the row answers on "back" 1169 in rd19 (the edit's overlap: rd19 replays the moment from the road).
    NEIGHBOURS: before, pn17_cows; after, rd19_drop (the money shot from the road).
    THE REVIEW (story, the patrol clock; confirmed on the build): the first stub's patrol walked 20 blocks up the road
      at the flip, 23 blocks behind rd19's twin on the same frames, and its docstring called the patrol's position
      "free (time compressed across the cut)" while the plan calls the same cut an overlapping action (time
      EXPANDED: flip 1108, retraction 1169). The trap read as fired early and saved by the edit. Now one clock.
    THE CAMERA (measured, the lead's scouting; out/test/legday_tp18var*_tp18_lever_1110_v*.png): from the lever's
      side of the wall top (the set's b18, TP18_CAM_LEVER) the lever is big but the wall hides the road at its foot:
      no patrol in the frame. The stub hangs the camera out past the NORTH-EAST corner, 16 mm, looking back down
      (TP18_CAM; out/test/legday_scout_tp18_lever_1110[_zones].png): the narrator at the lever from above and behind,
      his arm on it, the dust line dark along the wall top, the corner of the wall dropping 18 blocks, and the file
      on the road at its foot walking into the trap. TO FIX: the file sits at y 55-75 % (in the caption band) and is
      small (the banner does not read at this size; "soft and far below" as written); the narrator's face is not
      seen (the story asks for his thin arm only). Choose between the two (the lever big, or the lever and the file),
      or find a third, but keep the clock.
    THE CHOICE (the top director's): THE LEVER BIG, NO PATROL IN THE FRAME. Measured on the build (tools/
      legday_top_probe; quick stills in the scratchpad, t18_*/t18b_*): the file is 18 blocks below the lever and 3-8
      blocks from it, so from any camera that holds both, the angle between them is 40-55 degrees: the stub's 16 mm and
      a steeper 14 mm vertigo (narrator y 16-22 %, captain y 54 %, followers 56-66 %, faces 8-10 px, the banner a
      speck) still put the rear of the file in the caption band, the narrator seen from behind, and the dust line in
      the top corner; pulled back to 15-25 blocks (24 mm, 18 mm) the narrator's face is 23-28 px with his back to us
      and the file at y 59-82 %. A truthful patrol cannot be "soft and far below" AND above the caption band in one
      frame with the lever close. So the patrol is not in this shot (it is not marched here: THE PATROL CLOCK is kept by
      rd15 and rd19, which show it on the same frames, and nothing here contradicts it); rd19 (the next shot, from the
      road) shows the file under the shelf. What carries the line: his thin arm, the lever, and the whole lit line
      going dark along its length.
    NOW: TP18_CAM, 26 mm f/2.8, from past the wall top's NORTH-WEST corner, 2.5 above the walkway (-3.75, 63.4, 20.5),
      looking south-east and down, a slow push in (ease_out): the narrator three-quarter at the lever (his face to the
      lens: he stands east of it facing west), his thin right arm reaching to the handle, the lit dust line running
      away south along the wall top behind him to the right, the shelf with its anvils beyond on the left, the lantern
      beside the lever low right. The lens never sees the road at the wall's foot (the wall top hides it).
      1103      on the cut his head turns to the handle (flip_by look: from his place() frame, over 5 frames)
      1108      "flipped": the click, his arm lifted onto the handle (flip_by reach=True); 1109 the lever's model swap and
                THE WHOLE LINE DARK on the same frame (C.wire.unpower(t))
      1114-1123 his eyes drop to the dust by the pier (now dark) and hold through "one lever"
      focus the lever's handle; heroes the lever, the narrator.
    MEASURED (tools/legday_top_probe, the built camera): the narrator's eyes x 29-30 % y 38 % (1104-1135), face 93-102
      px, 36-55 degrees off the lens; the handle x 37-70 % y 37-52 % (it swings to the other side on 1109); his right
      hand 0.63 from the handle's middle on 1110 (the reach); the dust from x 63 % y 68 % (by the pier) to the right
      edge. Light: the sun (az 0) 115 degrees off the lens axis (his face side-lit). Stills and palette: see the module
      docstring, THE EVIDENCE.
    """
    f0, f1 = s.frame_start, s.frame_end
    efe = C.actor("efe", "tp3")                            # empty-handed: his right hand is for the lever
    C.put(efe, f0, "lever_narrator")                       # facing west, the lever in front of him
    t = redstone.flip_by(efe, C.lever, C.at(s, "flipped"), look=True, reach=True)   # head to the handle from f0
    C.wire.unpower(t)                                      # the WHOLE line dark on the frame the lever goes off
    efe.look_at(t + 5, (-2.45, 58.2, 18.05), ease=9)       # his eyes drop to the dust by the pier: dark
    st.use(s, efe)
    C.cam(s, None, focus=C.lever.hand_point(f0), **TP18_CAM)
    st.hero(s, "lever", *C.lever.objects)                  # (a property of the kit parts)
    st.hero(s, "narrator", efe)
    C.lights(s, "gold", near=(-3.0, 57.0, 18.0), radius=10.0)


def tp24_reloading(st, s, C, nar):
    """BEAT 24  "I call it reloading."   frames 1491-1572 (82 f, 3.42 s), sky DUSK. The film's last shot.
    Words: I 1493, call 1498, it 1507, reloading 1510 (spoken to about 1524; its caption holds about a second, to
    1536). Then the last image holds to 1566 and the last 6 frames (1567-1572) are black (END_BLACK): the story's cut
    to black.

    STORY: About 3.0 s. Wall top at last light, looking along the row: Steve sets the twelfth anvil on the last plank
    and walks off without a glance. The narrator stays beside the lever, the redstone torch lighting his face, his
    free arm lifting to the lever and stopping there, looking out over the armed row of twelve anvils and the empty
    road below. Hold one second after the last word, then cut to black.
    Cast: Narrator (Efe, slim-arm model), Steve. Effects: twelve anvils as blocks on planks, the last one placed in
    shot; sticky pistons extended; lit redstone dust line; lever; redstone torch held and glowing as the key light on
    his face; lanterns as light.

    MUST BE SEEN, ON WHICH WORD
      frame 1491      the armed row (SHELF "dusk_eleven": eleven of the DUSK set, chipped as they landed), Steve
                      with the twelfth anvil (chipped), the narrator at the lever with his torch, the dusk sky
      "call" 1498 .. "it" 1507   Steve sets the twelfth anvil on the last plank (C.appear(s, C.anvils_dusk[11], f))
                      and walks off without a glance
      "reloading" 1510 .. 1566   the narrator's free arm lifts to the lever and stops there; he looks out over the
                      armed row and the empty road below; his face lit by his torch; HOLD (1.75 s), then black
                      from 1567
      THE ROW IS THE HERO (the review): the anvils standing on their planks must be INSIDE y 14-60 % and clear of
                      the caption band (y 62-72 %, where "reloading" sits 1510-1536) together with the torch-lit face
                      at the lever: st.hero(s, "row", ...) is declared, so --zones / palette_check flag it. PRIORITY:
                      the row first, then the narrator's face size
    SHARED: lever_narrator (= tp18), set_anvil_12th (= tp14). THE WORLD STATE: the twelfth dusk anvil (C.appear).
      The lever is ON again (the lead's re-arm, 1373): no flip here.
    NEIGHBOURS: before, cl23_legday (the legs at dusk); after, the end (the Reel loops to sq01).
    RISKS (story): "At dusk the narrator's face is only as bright as his practical. The redstone torch is a weak light
      in the game: key his face with a boosted lantern beside the lever and let the torch be the red accent."
      "Long caption words (... reloading) need the reduced letter size ... Check that reloading with its full stop
      fits inside the caption width and hold it a full second." (The lead: the caption system draws long words
      smaller by itself; "reloading" is on screen 1510-1536, see tools/legday_timeline.)
    MEASURED (the set builder, out/test/legday_set_b24_reloading[_zones].png): above the road south-east of the lever,
      35 mm: the armed row (dusk set) receding to Steve setting the twelfth and the narrator at the lever with his
      arm up, the dusk sky behind. palette_check fails "stone not magenta" at G/R 0.90: the warm dusk sky on the
      wall top, not the lanterns (0.87 with them off): ACCEPTED (films/legday.py SKIES).
    THE REVIEW (story, confirmed on the lead's first stub still, out/test/legday_scout_tp24_reloading_1530): the
      set's b24 camera put the anvil row at y 52-100 % (under the caption and the Reels UI) and the road out of the
      frame; "come closer to the narrator" would have dropped the row. THE LEAD'S SCOUTING (out/test/legday_tp24var*
      _tp24_reloading_1535_v*.png: from the south end along the row the row hides the narrator, the anvils overlap;
      at the anvils' height the near ones block him; from the EAST over the road, looking back WNW and down, every
      anvil reads as standing on its plank): TP24_CAM from the east, 24 mm (out/test/legday_scout_tp24_reloading_
      1500 / _1545[_zones].png): five chipped anvils on their planks receding to the narrator at the lever, y 43-58 %;
      the planks in the caption band; the lanterns; the dusk sky. TO FIX: the narrator's face is 28 px (tools.
      legday_geo tp24_reloading:1545: eyes x 63 %, y 37 %, 23 degrees off the lens): once Steve has gone the push may
      end closer on him, as long as the last anvils stay inside y 14-60 %. The empty road below is not in this frame.
    THE STAGING: the torch in his LEFT hand (C.narrator(..., hand="left"): toward this camera, the key on his face),
      his body toward the south-west (the lever at his front right), his head on the row; his RIGHT arm lifts to
      the lever on "reloading" (raise_arm side "r"). Check on stills that the hand reaches the lever.
      (THE STUB'S raise_arm(60) left his hand 0.42-0.62 block short of the handle: raise_arm only lifts forward, and
      the lever is at his front RIGHT. Now _hand_on: the forward lift AND the sideways swing searched on the rig.)
    NOW: TP24_CAM, 32 mm f/4 (the stub: 24 mm), from the lead's east position over the road (5.9, 50.6, 20.6), a slow
      push (ease_out: at speed on frame 1, settling into the hold) to (5.1, 52.0, 20.7), aimed lower than the stub: the
      narrator in the top third against the dusk, the last four chipped anvils on their planks across the middle of
      the frame, their planks and the wall face below them (the caption sits on the wall). WHY 32 mm FROM AFAR: pushing
      the 24 mm in to (3.4, 54.0, 20.1) made his face 39 px but brought the nearest anvils down to y 51-82 % (palette
      check FAILED the row hero, 33 % inside: out/test/legday_pal_tp24_reloading_1550 of that version was replaced);
      the longer lens from further back gives the same face size with the row inside the safe area. The same angle as
      tp14 (the morning set of the twelfth): the rhyme of the ending.
      1491      the narrator (efe_tp4, the torch in his LEFT hand at LS.B24_TORCH_WATTS: his key) at lever_narrator facing
                south-west, his eyes on the last plank; steve_tp2 on set_anvil_12th with the chipped twelfth
      1497/1498 Steve's swing; the twelfth (chipped) anvil stands on plank 12 ON "call"; his hand empty
      1501-     Steve's head level (without a glance); from 1504 he walks south along the dust at the game's pace, out of
                the frame's left edge by about 1525 (the push helps)
      1506-1516 the narrator's eyes go from the plank out over the armed row (and the road beyond)
      1510-1518 "reloading": his free RIGHT hand rises to the lever's handle and STAYS there (_hand_on: lift and swing
                searched so the grip is nearest the handle's middle)
      1540-1556 a last slow look down at the empty road at the wall's foot; hold; black from 1567 (END_BLACK)
      focus his head; heroes the row (anvils 9-12 of the dusk set: the last four, the review's "last 4-5"), the
      narrator.
    MEASURED (tools/legday_top_probe, the built camera): his face 36 px on 1493, 39 px on 1515, 42 px on 1550-1566
      (the stub: 28 px), eyes x 66-67 % y 21-26 % (head box y 18-28 %), 13-23 degrees off the lens; his right grip
      0.23 block from the handle's middle from 1518 (the stub's raise_arm: 0.42); the row hero (anvils 9-12) box
      y 32-62 % (palette check, rendered: y 32-60 %, 88 % inside the safe area on 1550); Steve at x 40 % on 1493-1500,
      past the left edge by about 1525. palette_check tp24@1550: every check passes (stone G/R 0.95: the warm-dusk
      failure of the set's b24 does not occur here). Stills: see the module docstring, THE EVIDENCE.
    """
    f0, f1 = s.frame_start, s.frame_end
    f_set, f_rel = C.at(s, "call"), C.at(s, "reloading")
    efe = C.narrator("tp4", watts=LS.B24_TORCH_WATTS, hand="left")    # the torch on the camera's side: his key
    steve = C.actor("steve", "tp2")
    p = C.P("lever_narrator")
    a = C.P("set_anvil_12th")
    C.put(efe, f0, "lever_narrator", toward=(p[0] - 1.0, p[1] - 1.0))   # south-west: the lever at his front right
    steve.place(f0, a, C.yaw("set_anvil_12th"))
    C.carry_anvil(steve, dusk=True, index=11)              # the twelfth, carried back up: chipped (CHIPPED)
    efe.look_at(f0, PLANK12_TOP, ease=0)                   # he watches the last plank (toward the lens) ...
    efe.look_at(f_set + 8, ROW_OUT, ease=10)               # ... then out over the armed row and the road below
    _hand_on(efe, f_rel, C.lever.hand_point(f_rel, 0.5), ease=8)   # his free (right) hand to the lever, and it stays
    efe.look_at(f_rel + 30, ROAD_BELOW, ease=16)           # a last slow look down at the empty road
    steve.look_at(f0, PLANK12_TOP, ease=0)
    steve.attack(f_set - 1)
    C.appear(s, C.anvils_dusk[11], f_set)
    steve.hold(None, frame=f_set)
    steve.look_at(f_set + 3, None, ease=5)                 # without a glance: head level, straight ahead
    away = (-2.5, 50.0, LS.WALK_Z)
    steve.walk(f_set + 6, [a, away])                       # at the game's pace, off the frame's left edge
    st.use(s, efe, steve)
    C.cam(s, None, focus=efe.head, **TP24_CAM)
    st.hero(s, "row", *[an.objects()[0] for an in C.anvils_dusk[8:12]])  # THE PAYOFF: the last four of the
    #                                                                       re-armed row (9-12) first
    st.hero(s, "narrator", efe)
    C.lights(s, "dusk", near=(-2.0, 52.0, 18.0), radius=14.0)
