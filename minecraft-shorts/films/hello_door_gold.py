"""The Hello, sequence DOOR GOLD: the front of the child's house in golden light (morning, and late gold in beat
15). Beats 4, 5, 15, 20, 21, 22 (shots dg04_hello, dg05_nod, dg15_a, dg15_b, dg15_c, dg20_walkup, dg21_crouch,
dg22_eyes), sky "gold". One function per shot; the contract is in films/hello_common.py (tags "dg...", C.actor,
C.cam, C.lights, st.use / st.hero).

THE PLACE (house_a's west front, hello_common's docstring): door cell (10, -8), the oak step at (9, -8) (high half
  x 9.5..10 at z 1.0, low half x 9..9.5 at z 0.5), wall torches either side at head height; north of the door one
  block of wall and the corner log: the house's north-west corner is at (10, -5).
  PLACES: "watch_door" (8.9, -5.4) = his spot, facing HC.WATCH_YAW (toward "watch_face" (9.75, -7.2): the door);
  "hello_child" (9.25, -6.41) = the child at his feet, between him and the door; "step", "step_child",
  "watch_far" (8.3, 11.5), "watch_mid" (8.5, 1.5) (moved by the lead from (8.4, 5.2): see dg15_b).
THE SKY: "gold" = sun at azimuth 215 (west-south-west), elevation 24: it lights the west front of the house and
  the plaza before it. He faces the door, so in the doorstep two-shot the sun is behind him and his face is in
  his own shade: C.doorstep_fill(s) is the film-local shadowless fill on his face, the SAME light at the SAME
  strength in dg04 and dg22. Decided on stills: with the fill (out/test/hello_scout_twoshot_dg04_hello_226.png,
  _dg22_eyes_1475.png) the face is lit and the indigo eye pixel reads blue; without it
  (hello_scout_twoshot_nofill_*.png) the face is a stop darker and the iris dark purple.
THE TWO-SHOT (CAMS["two_shot"], 40 mm f/2.4 from (8.8, -8.4, 1.35) aimed at (8.9, -5.4, 1.0), 3 blocks south of
  him), MEASURED ON RENDERS (out/test/hello_scout_gold_dg04_hello_226_zones.png, _dg22_eyes_1480_zones.png): his eyes
  at y 36 % standing (head top 16 %) and y 49 % crouched (chin 56 %, clear of the caption band 62-72 %), x 50 %, face
  178 px wide; a house front and its roofline behind him (the fixed line the crouch reads against); the child's head
  a soft pink block at the lower right (x 56-100 %, y 52-96 %). No lamp post within a third of the frame of his head.
  (Aimed at z 1.2 at first, the crouched chin was IN the caption band: "blue" and "eyes" drawn on his chin.)
  palette_check dg22@1480: every check passes (hero watcher x 33-77 %, y 32-56 %, 100 % inside the safe area).
THE TWO SHOTS THAT MUST MATCH: dg04_hello and dg22_eyes use CAMS["two_shot"] EXACTLY through _two_shot() (no
  override; the same handheld seed TWO_SHOT_SEED and sway TWO_SHOT_HANDHELD 0.012 in both, since C.cam would
  otherwise derive the seed from the shot name), the same fill, the same light levels, Steve in dg04 and the watcher in dg22 on "watch_door" facing
  WATCH_YAW, the child on "hello_child". The roofline behind his head is what makes the crouch read: keep it.
HIS FACE: never readable before dg22, measured (tools.hello_geo, renders): dg15 the right side of his head, 106-108
  degrees off the lens, soft, face 28 / 37 / 78 px; dg20 his head never in the frame (cut by the top at the
  shoulder, 120-126 degrees off); dg21 the back of his head in the top-left corner standing, the back and right side
  (hair and skin, no eyes) 122-125 degrees off once he is down. In dg22 the white eyes are unmistakable from the cut.
THE SEQUENCE NOW (each shot's docstring has its NOW and MEASURED lines):
  dg04  the two-shot: his head comes down to the child on the cut, two quick crouches, the second on "twice"
  dg05  the reverse from his left side, at shoulder height: its face to the lens, two nods on "hello", it runs off
        straight away along the plaza
  dg15  one frame (FRONTS) with one slow push over all three jumps: the child faces the lens, its head turns to him
        (profile) and back; he jumps from house to house while it looks away
  dg20  low behind his right hip: the flesh spinning on the step, the door snaps open, the child walks out past the
        flesh with its head on him, the door snaps shut behind it, it drops down both halves of the step, walks to
        his feet, looks up, nods on "hello"; his head never in the frame
  dg21  behind his right shoulder: the slow crouch from "crouched", his head coming down into the frame from the
        top left, the flesh still spinning on the step, the silence
  dg22  the two-shot again: the white eyes, a small settle of his head on the cut, the hold (the handheld floats it)
  Screen direction: dg04, dg20, dg21 and dg22 film from the same side of the line him-child (the child looks up to
  the LEFT at him); dg05 is from the other side (from his right side the sword covers the child's face), with
  the child's look cheated toward the lens.
LIGHT: C.lights(s, "gold", near="door", radius=16) in every shot; the doorstep fill in dg04 / dg22; "dg_nod"
  (NOD_FILL) in dg05.
TOOLS: tools/hello_door_gold_probe.py (door crack and swing keys; variants of a built film rendered to a scratch
  directory without touching this file; `check`: dg20's feet against the step, its parts against the flesh and the
  door, the flesh-to-head gap for candidate cameras, the flesh's place in dg21).
"""
import math

from engine import breaking, characters, shots
from films import hello_common as HC

TWO_SHOT_SEED = 7          # the handheld of dg04 and dg22: the same seed, so the two frames match
TWO_SHOT_HANDHELD = 0.012  # ... and the same sway (blocks): a slow float of a few pixels. At 0.004 the 2 s hold on
#                            the white eyes (1460-1544) changed by only 0.2-0.7 grey levels a frame: a frozen picture

# beat 15: ONE locked frame for the three jump cuts (the stub's CAMS "house_fronts" moved: lower and half a block
# further back, so the eaves of house_a sit in the top UI strip instead of across the top right; the stub camera is
# gone from hello_common, FRONTS is this shot's own: C.cam(s, None, ...))
FRONTS = dict(pos=(8.75, -15.0, 1.6), target=(9.7, 4.0, 1.4), lens=55.0, fstop=2.8)
FRONTS_SEED = 15
# ... with ONE slow linear push over the whole beat (915 -> 998), keyed by the film's frame so the three jump cuts
# stay one continuous frame: the handheld alone (0.002 at 19 blocks) left 11 dead-still frames after the cut from
# me14 and 23 in the pause after "closer"
FRONTS_PUSH = ((8.75, -15.0, 1.6), (8.75, -14.75, 1.6), 915, 998)     # pos at the first frame, pos at the last + 1
# beat 5: beside his LEFT side at shoulder height (the empty hand: the sword arm is on the other side), down on the
# child (z 1.35, not 1.1: from elbow height the tip of his iron sword, in his far hand, showed past his bare arm as a
#   white chevron beside the child's head all shot. Sword vertices the lens sees, every 4th frame 272-316, ray
#   cast: z 1.25: 0-22 (a faint speck at the arm's edge); z 1.30: 0-8; z 1.35: none)
NOD_CAM = dict(pos=(9.75, -4.3, 1.35), target=(9.2, -6.5, 0.3), lens=32.0, fstop=2.4,
               pos1=(9.73, -4.4, 1.34), target1=(9.2, -6.5, 0.3))
NOD_FILL = dict(pos=(9.55, -4.95, 1.25), watts=160.0)   # beat 5: the child's face is on the sun's far side: a
#                                                         shadowless fill beside the lens lifts it to dg04's level
NOD_RUN = [(8.85, -7.05), (8.8, -9.0), (8.75, -12.0)]   # beat 5: the child runs off along the plaza, straight
#                                                         away from the lens, its east edge along the step's west
#                                                         face (the first run bent right, into his arm and the tip)
# beat 20: low, close behind his right hip (north-west of him), looking past him at the door; the push ends in a
# small truck to the right and up, which opens the gap between the spinning flesh and the child's tipped-back head
# (silhouettes 1303-1357: 18-41 px at 540x960 with the first end (6.99, -5.06, 0.41), 31-60 px now)
WALK_CAM = dict(pos=(6.9, -5.0, 0.4), target=(9.4, -6.65, 0.45), lens=30.0, fstop=2.4,
                pos1=(6.9, -5.26, 0.5), target1=(9.4, -6.76, 0.45))
# beat 21: behind his right shoulder line, down on the child; further back and higher than the first camera
# (7.56, -5.06, 1.41) at 40 mm, which kept his crouched head out of the frame but for a strip of hair
CROUCH_CAM = dict(pos=(7.17, -4.92, 1.5), target=(8.95, -6.15, 0.72), lens=38.0, fstop=2.4,
                  pos1=(7.21, -5.01, 1.49), target1=(8.95, -6.15, 0.72))


def _head_point(c, frame, yaw_deg, pitch_deg=0.0, dist=3.0):
    """A look target that turns c's head `yaw_deg` from its body (+ = to its left) and `pitch_deg` up, at `frame`
    (the body standing still): for head turns that must read the same in every shot of one locked frame."""
    eye = c.eye_point(frame)
    yaw = c.yaw_at(frame) + math.radians(yaw_deg)
    return (eye.x + math.sin(yaw) * dist, eye.y - math.cos(yaw) * dist,
            eye.z + math.tan(math.radians(pitch_deg)) * dist)


# a mob walking off a ledge in the game falls (gravity 0.08 block/tick², drag 0.98, 20 ticks/s): (frames from the
# moment its hitbox clears the edge, fraction of a half-block drop done) - it lands after about 3.7 frames
FALL = ((0.0, 0.0), (1.2, 0.157), (2.4, 0.466), (3.7, 1.0))


def _step_down(c, f_from, f_to, drops):
    """Re-key the height of a walk that was keyed at ONE height (c.walk(f_from, route) ending on f_to): the
    character keeps its height until its hitbox clears an edge, then falls to the next level like a mob in the
    game, while it walks on at full speed (Character.walk would ramp the height along the whole segment: it slid
    down each half of the step like a lift and its feet went into the stair). drops = [(axis 0 / 1, edge, z
    after)]: the drop starts on the (fractional) frame the root's coordinate passes `edge`, in order."""
    keys, z = [(float(f_from), None, "LINEAR")], c.pos_at(f_from).z
    f = f_from
    for axis, edge, z_after in drops:
        before = c.pos_at(f)[axis]
        while f < f_to and (c.pos_at(f + 1)[axis] - edge) * (before - edge) > 0:
            f += 1
            before = c.pos_at(f)[axis]
        a, b = c.pos_at(f)[axis], c.pos_at(f + 1)[axis]
        t = f + (edge - a) / (b - a) if abs(b - a) > 1e-6 else float(f)
        for dt, done in FALL:
            keys.append((t + dt, z + (z_after - z) * done, "LINEAR"))
        z = z_after
        f += 1
    keys.append((float(f_to), z))
    characters._segment(c.root, "location", 2, keys)
    return [k[0] for k in keys]


def _two_shot(s, C):
    """The camera of beats 4 and 22, exactly, with its fill (call it in both)."""
    C.cam(s, "two_shot", seed=TWO_SHOT_SEED, handheld=TWO_SHOT_HANDHELD)
    C.doorstep_fill(s)


def dg04_hello(st, s, C, nar):
    """BEAT 4  "Every morning he crouched at me, twice."   frames 211-271 (61 f, 2.54 s), sky gold.
    Words: Every 213, morning 219, he 227, crouched 230, at 241, me 244, twice 248. The pause after it is 0.45 s.

    NOW: CAMS["two_shot"] + the doorstep fill exactly (_two_shot, as dg22). Steve (iron, sword) on "watch_door" facing
      WATCH_YAW, the child on "hello_child" (a soft pink block at the lower right, its back to us, as in dg22).
      211       on the cut he still looks at the door (watch_face, level); his head comes down to the child over 8
                frames (watch snap=False): something moves on frame 1, and his face is pitched down by "morning" 219
      211-235   Player.idle: the game's arm bob and weight shift (his head stays on the child)
      236-254   C.crouch_twice from "twice" - 12: down 236 (inside "crouched"), up 242, down 248 ON "twice", up 254;
                the snap is the game's; the roofline of the house behind him is the fixed line the drop reads against
      255-271   idle again, the head kept on the child (track); the child's head follows his eyes all shot (track)
      focus his head; hero "steve"; C.lights gold near the door, radius 16.
    MEASURED (tools.hello_geo at 219 / 239; renders out/test/hello_dg_dg04_hello_222_zones.png, _239_zones.png):
      standing eyes x 50 %, y 29 % projected (rendered about y 36 %), face 180 px, 21 degrees off his nose (frontal);
      crouched eyes y 43 % projected (rendered about y 52 %), chin clear of the caption band. The child's head x 56-100 %,
      y 52-96 %, 148 degrees off (from behind; a nose cheat of 30-50 degrees showed no nose: not used). The sword lies
      across the caption band (y 55-70 %) standing and points down crouched. With the handheld at 0.012 (for dg22's
      hold; the same in both) the crouched head box ends at y 57.5 % (236-251): clear. palette_check dg04@226: every
      check passes (hero steve x 33-78 %, y 17-42 %, 100 % in the safe area). Motion: out/test/hello_door_gold_motion.mp4.

    STORY: Golden morning on the plaza at the foot of the doorstep. Steve has stepped outside and stands two blocks
    from the door, facing it, no helmet. The child has come down the step and stands at his feet. Close two-shot
    from child height, camera with its back to the door looking out: the child low in the foreground, three-quarter
    from behind with its nose showing, Steve's face filling the upper part of the frame, pitched down at the child,
    the white and dark blue eye pixels clearly readable, a roofline across the plaza as a fixed line behind his
    head. He drops into the sneak pose and stands again, twice, quickly. The last shot of the film uses this
    camera exactly. About 3 seconds.
    Cast: Steve, baby villager (narrator). Effects: player sneak pose, two quick crouches (six frames down and six
    up), fixed roofline behind his head so the drop reads, film-local neutral fill on his face, the same one as in
    beat 22.
    SHARED: CAMS["two_shot"] + C.doorstep_fill(s) (via _two_shot), PLACES "watch_door" + HC.WATCH_YAW, "hello_child":
      EXACTLY as in dg22. Cast: C.actor("steve_iron", "dg"), C.actor("child", "dg").
    NEIGHBOURS: before, in03_bed (the room turned gold on "ended"); after, dg05_nod (the child nods and runs off).
    RISKS (story): blue eyes: the iris texel is #523d89, the trousers' indigo; under warm light it can read purple or
      dark: the near-neutral fill, the face at least a third of the frame wide. The sneak pose is a drop of a third
      of a block plus a lean and can vanish at phone size: the fixed roofline, six frames down and six up.
    """
    f0, f1 = s.frame_start, s.frame_end
    steve = C.actor("steve_iron", "dg")
    kid = C.actor("child", "dg")
    C.put(steve, f0, "watch_door", yaw=HC.WATCH_YAW)
    C.put(kid, f0, "hello_child", toward="watch_door")
    down = C.at(s, "twice") - 12                      # first crouch inside "crouched", the second ON "twice"
    steve.idle(f0, down - 1)                          # the game's idle arm bob and weight shift until the crouch
    steve.look_at(f0, C.P("watch_face"), ease=0)      # on the cut he still looks at the door ...
    steve.watch(f0, f1, kid, snap=False, ease=8)      # ... and his head comes down to the child by "morning"
    up = C.crouch_twice(steve, down)
    steve.idle(up + 1, f1 + 1)                        # alive again once he is up for good ...
    steve.track(up + 1, f1, kid, step=2, ease=1)      # ... but his head stays on the child (idle glances it away)
    kid.look_at(f0, steve, ease=0)
    kid.track(f0, f1, steve, step=2, ease=1)          # its head follows his eyes down and up
    st.use(s, steve, kid)
    _two_shot(s, C)
    s.focus(steve.head)
    st.hero(s, "steve", steve)
    C.lights(s, "gold", near="door", radius=16.0)


def dg05_nod(st, s, C, nar):
    """BEAT 5  "That meant hello."   frames 272-318 (47 f, 1.96 s), sky gold.
    Words: That 274, meant 279, hello 284. The pause after it is 1.0 s (about 290-318: the run off; the story turns).

    NOW: the reverse, from beside his LEFT side at shoulder height (NOD_CAM, 32 mm f/2.4 from (9.75, -4.3, 1.35), a
      slow push): his iron shoulder and bare left arm at the right edge (x 57-100 %), his iron leg at the lower right,
      soft; the child in the middle, its face to the lens (its look at his eyes cheated 20 degrees toward the lens with
      C.to_lens), the step on the left, trees and the morning sky behind. From z 1.1 (elbow height) the tip of his
      sword showed past his arm as a white chevron beside the child's head; from 1.35 his arm hides all of it (ray
      cast to every sword vertex, every 4th frame).
      "hello" 284   C.hello_nod (two nods, 14 frames)
      296-300       head level again; it turns and runs (walk run=True, 4.4 blocks/s) from 299 straight away along the
                    plaza (NOD_RUN: x 8.85 -> 8.75, its east edge along the step's west face), getting smaller, its
                    head bobbing, to the end of the shot; its head passes the edge of his arm at about 300-306 and is
                    clear of it from 308
      light: the child's face is on the far side of the sun: film-local fill "dg_nod" (NOD_FILL, 160 W, shadowless,
      beside the lens, this shot only) lifts its skin from 121 to 151 (palette_check), nearer dg04's level.
      WHY THIS SIDE: from his right side (the side of the 180-degree line dg04 is on) his sword arm and the sword, which
      points at the child, cover its face at every height tried (hello_geo: blocked by steve_iron_dg_arm_r / _iron_sword_r
      from (7.2..7.9, -4.4..-5.75)); from his left side the child's eyeline is up and right instead of up and left: the
      look cheated to the lens keeps that line cross soft.
    MEASURED (tools.hello_geo at 284 / 312; renders out/test/hello_dg_dg05_nod_286_zones.png, _310_zones.png): on
      "hello" the child's eyes x 48 %, y 39 %, face 193 px, 13 degrees off the lens, nothing in front of it; his head
      x 64-182 %, y -52..19 % (out of the frame: the top right is his iron shoulder; from behind, 122 degrees). At 312
      the running child's eyes x 44 %, y 24 %, 100 px. palette_check dg05@286: every check passes (child's skin 152,
      hero child x 27-67 %, y 23-45 %, 100 % in the safe area).

    STORY: Reverse angle from beside Steve's hip, his arm and iron leg at the edge of the frame. The baby villager
    looks straight up at him and nods twice in answer, the only hello a villager can do, then turns and runs off
    along the plaza with its big head bobbing. About 2 seconds.
    Cast: baby villager (narrator), Steve (hip and arm only). Effects: baby villager nod twice (existing nod), baby
    villager run.
    SHARED: PLACES "watch_door", "hello_child" (its start). Cast: C.actor("steve_iron", "dg") and C.actor("child", "dg")
      (both in dg04, the shot before: placed on f0, nothing keyed before it).
    NEIGHBOURS: before, dg04_hello; after, me06_leave (the gate: one day he walks into the woods). Hard cuts.
    """
    f0, f1 = s.frame_start, s.frame_end
    steve = C.actor("steve_iron", "dg")
    kid = C.actor("child", "dg")
    C.put(steve, f0, "watch_door", yaw=HC.WATCH_YAW)
    here = C.put(kid, f0, "hello_child", toward="watch_door")
    steve.idle(f0, f1 + 1)                            # his arm at the edge of the frame: the idle arm bob
    steve.watch(f0, f1, kid)
    up_at_him = C.to_lens(kid, f0, steve.eye_point(f0), NOD_CAM["pos"], degrees=20.0)
    kid.look_at(f0, up_at_him, ease=0)                # straight up at his face, cheated toward the lens
    end = C.hello_nod(kid, C.at(s, "hello"))
    kid.look_at(end - 2, None, ease=4)                # head level again, then away along the plaza
    kid.walk(end + 1, [here] + [C.stand(p) for p in NOD_RUN], run=True)
    st.use(s, steve, kid)
    C.cam(s, None, focus=kid.head, handheld=0.006, **NOD_CAM)
    C.fill("dg_nod", NOD_FILL["pos"], NOD_FILL["watts"], [s])
    st.hero(s, "child", kid)
    C.lights(s, "gold", near="door", radius=16.0)


AWAY, LOOK = (12.0, -8.0), (-70.0, 3.0)      # beat 15: the child's head (yaw from its body, pitch): to the lens
#                                             side and a little down (its face), and turned to its right as far as a
#                                             head goes (screen left, where he stands: its nose in profile)


def _fronts(st, s, C, place, turns):
    """Beat 15, one of its three jump cuts: the locked frame along the house fronts, the child on the step facing
    the lens, him at `place` in profile. turns = [(frame, AWAY or LOOK, ease)]: the child's head, from f0 (the
    first entry is its pose on the cut)."""
    f0 = s.frame_start
    kid = C.actor("child", "dg")
    p = HC.PLACES[place]
    C.watcher(s, "dg", place=place, yaw=HC.yaw_to(p, (p[0] + 1.0, p[1] + 0.3)))   # facing the fronts: profile
    C.put(kid, f0, "step_child", toward=FRONTS["pos"])
    for frame, (yaw, pitch), ease in turns:
        kid.look_at(frame, _head_point(kid, frame, yaw, pitch), ease=ease)
    st.use(s, kid)
    p0, p1, a, b = FRONTS_PUSH

    def push(f):                                      # where the beat's one push is on film frame f
        k = (f - a) / float(b - a)
        return tuple(u + (v - u) * k for u, v in zip(p0, p1))
    C.cam(s, None, focus=kid.head, seed=FRONTS_SEED, handheld=0.002, ease="linear",
          **dict(FRONTS, pos=push(f0), pos1=push(s.frame_end + 1), target1=FRONTS["target"]))
    st.hero(s, "child", kid)
    C.lights(s, "gold", near="door", radius=16.0)


def dg15_a(st, s, C, nar):
    """BEAT 15, first jump  "Every time I look,"   frames 915-946 (32 f, 1.33 s), sky gold.
    Words: Every 917, time 924, I 932, look 936.

    NOW (all three jumps, _fronts): ONE locked frame, FRONTS = 55 mm f/2.8 from (8.75, -15.0, 1.6) aimed at (9.7, 4.0,
      1.4) (CAMS "house_fronts" moved: 0.6 lower, 0.4 further back, a shorter lens: the eaves of house_a now cross only
      the top of the frame, mostly in the top UI strip), handheld 0.002 with one seed and ONE linear push of 0.25 block
      (FRONTS_PUSH, 915 -> 998, keyed by film frame: continuous over both jump cuts; without it the picture stood
      dead still for 11 frames after the cut from me14 and 23 in the pause after "closer"), focus on the child's head.
      The child on "step_child" with its BODY FACING THE LENS: its head is the device.
      AWAY = its head 12 degrees to its left and 8 down: its face to us (eyes, brow, nose); LOOK = 70 degrees to its
      right (as far as a head turns) and 3 up: the nose in profile pointing at him (screen left). He jumps only while
      the child looks away.
      dg15_a  915 AWAY (its face on the cut) / "time"+2 = 926 LOOK (by 932, "I look") / "look"+4 = 940 AWAY (by 946)
      dg15_b  947 AWAY / 948 LOOK (by 953) / "house" 961 AWAY (by 967)
      dg15_c  968 AWAY / 969 LOOK (by 974) and hold through the pause to 997
      Him: C.watcher on watch_far / watch_mid / watch_door, facing east-north-east (the house fronts): 106-108 degrees
      off the lens in all three, the right side of his head toward us (hair and skin, no eyes): "same pose".
    MEASURED (tools.hello_geo at 920 / 936 / 955 / 980; renders out/test/hello_dg_dg15_a_920_zones.png, _936_zones.png,
      _dg15_c_980_zones.png; dg15_b since the lead's pass: out/test/hello_lead_dg15_b_955_zones.png): the child's eyes
      x 70 %, y 47 % (head x 58-82 %, y 40-51 %, face 48-49 px, a baby's width: hello_geo measured 95-98 before the
      lead's pass, an adult's), 12 degrees off the lens AWAY, 70 LOOK; nothing in front of it. Him: eyes x 32 % / 32 % /
      41 %, y 48-49 %, face 28 / 45 / 78 px, distance 26.4 / 16.4 / 9.4, clear of every block, soft (focus on the
      child at 7.7). He grows in place rather than wanders, in three even steps (watch_mid was (8.4, 5.2), 20.1 blocks
      out: 28 -> 37 px in front of the same house front, the jump read as a glitch; the lead moved it to (8.5, 1.5),
      beside the cobblestone of house_b). palette_check dg15_a@936, dg15_b@955 and dg15_c@980, all with the push:
      every check passes (hero child x 62-81 %, y 40-50 %, 100 % in the safe area; at 980 his shirt hue 174, trousers
      min channel 44).

    STORY (all of beat 15, "Every time I look, he is one house closer."): Late gold at the child's door. The baby
    villager, sharp in the lower foreground on the step, turns its head to look along the house fronts: he stands
    small and soft beyond the next house. The child looks away and back, jump cut in the same frame: he is at the
    next house, same pose. Once more: he is at the corner of the child's own house. About 3 seconds.
    Cast: baby villager (narrator), the watcher (background, out of focus). Effects: two jump cuts in a locked frame,
    each covered by the child's head turn, focus stays on the child.
    SHARED: PLACES "watch_far", "watch_mid", "watch_door" (dg15_c faces the fronts there, not WATCH_YAW: his face
      would be frontal). Cast: C.actor("child", "dg"), C.actor("watcher", "dg") (the same instances in a, b, c).
    NEIGHBOURS: before, me14_pyramid (the meadow); after, in16_empty (night, his bed empty). Hard cuts.
    RISKS (story): jump cuts in a locked frame can look like a render error: each jump happens while the child's face
      is turned to us and is followed by its head turning to him. The child in the foreground looking at a figure
      behind it is from behind by geometry (camera, child and him lie within 8 degrees): the head turned only to
      profile toward screen left keeps its face readable all the time.
    """
    f0 = s.frame_start
    _fronts(st, s, C, "watch_far", [(f0, AWAY, 0), (C.at(s, "time") + 2, LOOK, 6), (C.at(s, "look") + 4, AWAY, 6)])


def dg15_b(st, s, C, nar):
    """BEAT 15, second jump  "he is one house"   frames 947-967 (21 f, 0.88 s), sky gold.
    Words: he 949, is 951, one 954, house 961. (See dg15_a for the beat, the frame and the measurements.)
    NOW: him at "watch_mid" (the next house), the same profile; the child's face to us on the cut (947), its head turns
      to him by 953, and away again from "house" 961 (by 967): he jumps while it looks away.
    MEASURED (the lead's pass: PLACES["watch_mid"] moved from (8.4, 5.2) to (8.5, 1.5); this file unchanged, _fronts
      reads the place by name): him eyes x 32 %, y 48 %, face 45 px (was 37), 16.4 blocks, 106 degrees off: the right
      side of his head, no eyes, soft, beside the cobblestone corner of house_b instead of in front of the same house
      front as in dg15_a: 28 / 45 / 78 px over the three jumps. Render: out/test/hello_lead_dg15_b_955_zones.png;
      palette_check dg15_b@955 (lead's pass) passes everything (stone G/R 0.93, planks s 0.52, robe hue 16, skin
      s 0.48, hero child x 62-81 %, y 40-50 %, 100 % inside); preview 270x480_9spp 947-967 re-rendered.
    """
    f0 = s.frame_start
    _fronts(st, s, C, "watch_mid", [(f0, AWAY, 0), (f0 + 1, LOOK, 5), (C.at(s, "house"), AWAY, 6)])


def dg15_c(st, s, C, nar):
    """BEAT 15, third jump  "closer."   frames 968-997 (30 f, 1.25 s), sky gold.
    Words: closer 968. The pause after it is 0.8 s (to 997): he is at our corner; hold. (See dg15_a for the beat.)
    NOW: him at "watch_door" (the corner of the child's own house: his place in beats 19-22) facing the house fronts,
      not WATCH_YAW; the child's face to us on the cut (968), its head turns to him by 974 ("closer") and holds there
      through the pause; nothing else moves but the handheld.
    MEASURED: him eyes x 41 %, y 49 %, face 78 px, 108 degrees off the lens: the right side of his head (no eyes);
      soft (9.4 blocks against the focus at 7.6). palette_check dg15_c@980 (with the push) passes everything (his
      shirt hue 174, trousers min channel 44). Render: out/test/hello_dg_dg15_c_980_zones.png.
    """
    f0 = s.frame_start
    _fronts(st, s, C, "watch_door", [(f0, AWAY, 0), (f0 + 1, LOOK, 5)])


def dg20_walkup(st, s, C, nar):
    """BEAT 20  "So this morning I walked up to him and waited for my hello."   frames 1258-1357 (100 f, 4.17 s),
    sky gold. Words: So 1260, this 1264, morning 1270, I 1280, walked 1284, up 1293, to 1297, him 1300, and 1312,
    waited 1315, for 1324, my 1328, hello 1334. The pause after it is 0.5 s.

    NOW: a low camera behind his right hip (WALK_CAM, 30 mm f/2.4 from (6.9, -5.0, 0.4), a slow push that ends in a
      small truck right and up to (6.9, -5.26, 0.5)), on the same side of the line as dg21 / dg22: his right arm, teal
      sleeve and jeans as a soft column at the left edge, cut by the top of the frame at the shoulder (his head above
      and left of the frame: never in it); the shut door with its windows in the middle, the step under it, the torch
      at the upper right.
      1258      the rotten flesh (C.item, on "step") already spinning (place + animate), sharp: the focus starts on it;
                breaking.crack(door, f0, -1): whatever the night's knocking left is gone (stage 7 at 1257 otherwise)
      1269      the door snaps open ("morning" - 2 -> - 1, keys CONSTANT: 1268 is cleanly shut, 1269 open, no half-swing
                in the motion blur, as a door changes state in the game)
      1269-     the child (the "dg2" twin) walks out of the door at 2.1 blocks/s (walking, not running), south of the open
                door's panel, then across to the north side of the step's high half, past the flesh (beside it, not
                through it); its head turns to him from 1276 and stays on him (track, every frame) to his feet, so the
                route's short zig-zag round the flesh (1284-1289) turns only its body; 1291 the door shuts behind it
                (a villager closes the door it came through once it is out of the doorway: InteractWithDoor; CONSTANT
                keys again: 1290 open, 1291 shut); 1294 its hitbox clears the high half and it DROPS to the low half
                (FALL: the game's gravity, about 4 frames, walking on), 1299 the same off the low half's north edge to
                the ground (_step_down: walk() would ramp the height along a segment, a lift into the stair), and up
                to his feet on "hello_child" by 1304; the focus racks to its head from 1274 (0.4 s)
      1304-1312 its head tips all the way back to him; "hello" 1334: the two nods; it holds to the cut
      He is dead still (C.watcher). hero "flesh" and "child".
    MEASURED (tools.hello_door_gold_probe check; tools.hello_geo at 1262 / 1290 / 1338; renders
      out/test/hello_dg_dg20_walkup_1262_zones.png, _1268_zones.png, _1286_zones.png, _1290_zones.png, _1338_zones.png;
      tools.hello_door_gold_probe door: the open angle 0 at 1268.0-1268.5, 90 at 1269-1290.5, 0 from 1291): its head's
      world yaw -145 to -170 over 1282-1304 while its body swings -92 / -148 / -94 / 177 (head at most 68 degrees from
      the body; without the track the head flicked 56 degrees to the lens and back in 4 frames); its face 24-44 degrees
      off the lens from the doorstep to his feet. Its feet never more than 0.025
      below the block under them (the old route: 0.52 into the stair); its parts clear of the flesh but for the box of
      its head over the flesh's top at 1284-1288 (rendered: the flesh spins beside the child); the open door's box
      grazes its head by 0.04 inside the dark doorway (1271-1289, not visible). His head box x -57..16 %, y -27..16 %
      (the rendered frames show his shoulder there, not his head), 120-126 degrees off his nose. The child on the step
      at 1290: eyes x 59 %, y 21 %; at his feet (1338): eyes x 38 %, y 44 %, face 154 px, 45 degrees off the lens (its
      face to us), nothing in front of it; the gap between the silhouettes of the flesh and its head 31-60 px from 1303
      to the cut (18-41 px before the truck). palette_check dg20@1338: every check passes (hero flesh x 66-76 %,
      y 25-33 %, hero child x 20-60 %, y 30-50 %, both 100 % in the safe area); dg20@1290: every check passes (the
      child on the step, its head up in the top strip in passing: 77 % in the safe area; the flesh 100 %).

    STORY: Golden morning at the same door. One piece of rotten flesh spins on the step where the zombie stood. He has
    not moved from his spot. The door opens and the baby villager comes out, down the step, walking not running,
    up to him. Side-on long lens along the house wall: the child stops at his feet, tips its head all the way back
    and nods twice. He is cropped at the shoulders by the top of the frame. About 4.2 seconds.
    Cast: baby villager (narrator), the watcher (cropped at the shoulders). Effects: rotten flesh dropped item,
    spinning; door opening; nod twice.
    WHY NOT SIDE-ON: from the plaza (west) a frame 4 blocks wide is 7 blocks tall in 9:16, and the door top (z 3) is
      above his shoulders (z 1.45): the top of the frame cannot crop him at the shoulders and show the child in the
      door. From low and close behind him it can (perspective puts his shoulders above the door's middle).
    SHARED: PLACES "watch_door" + HC.WATCH_YAW, "hello_child", "step". Cast: C.actor("child", "dg2"),
      C.watcher(s, "dg"), C.item("rotten_flesh", "dg").
    NEIGHBOURS: before, dn19_beside (night: their two backs, the zombie knocking); after, dg21_crouch. Hard cuts.
    """
    f0, f1 = s.frame_start, s.frame_end
    him = C.watcher(s, "dg", place="watch_door")
    kid = C.actor("child", "dg2")
    flesh = C.item("rotten_flesh", "dg")
    step = C.P("step")
    flesh.place(f0, step)
    flesh.animate(f0, f1 + 1)
    breaking.crack(C.door, f0, -1, half="both")      # morning: whatever the night's knocking left is gone
    opens = C.at(s, "morning") - 2
    C.v.door_open("house_a", opens, open=True, frames=1)     # a door changes state at once in the game
    here = C.P("hello_child")
    start = (11.45, -7.42, 1.0)                       # inside, behind the shut door
    kid.place(f0, start, HC.yaw_to(start, (9.6, -7.3)))
    # out of the door (south of the open door's panel, y -7.19..-7.0), across to the north side of the step's high
    # half (z 1.0) past the flesh (its box y -7.60..-7.38), west onto the low half (z 0.5), then north off its edge
    # to the ground and up to his feet: walking, not running. Keyed at one height, then each drop re-keyed as a fall
    # once the hitbox (0.3 wide) has cleared the edge: x < 9.35 (the high half ends at 9.5), y > -6.85 (the step
    # ends at -7.0)
    route = [(x, y, start[2]) for x, y in ((11.45, -7.42), (10.05, -7.38), (9.92, -7.17), (9.2, -7.12),
                                           (9.25, -6.6), here[:2])]
    end = kid.walk(opens + 1, route, speed=2.1)
    _step_down(kid, opens + 1, end, [(0, 9.35, 0.5), (1, -6.85, here[2])])
    kid.track(opens + 8, end, him, step=1, ease=6)    # its head on him from the doorway: the route's short zig-zag
    #                                                   round the flesh turns only the body (the head flicked 56
    #                                                   degrees to the lens and back over 1284-1289 otherwise)
    shut = next(f for f in range(opens + 1, end) if kid.pos_at(f).x < 9.8)
    C.v.door_open("house_a", shut, open=False, frames=1)     # a villager shuts the door it came through once it is
    #                                                          out of the doorway (InteractWithDoor)
    for d in C.v._door_sets["house_a"]:               # a door has no swing in the game: hold each state to the next
        for fc in shots.fcurves_of(d):                # key (LINEAR, the half-open swing was in the motion blur of
            if fc.data_path == "rotation_euler" and fc.array_index == 2:      # 1268 and 1290: a ghosted panel)
                for k in fc.keyframe_points:
                    if opens <= k.co.x <= shut + 1:
                        k.interpolation = "CONSTANT"
                fc.update()
    kid.look_at(end, him, ease=8)                     # the head tipped all the way back
    C.hello_nod(kid, max(end + 10, C.at(s, "hello")))
    st.use(s, kid, flesh)
    C.cam(s, None, focus=step, handheld=0.006, **WALK_CAM)
    s.focus(kid.head, at_s=(opens + 6 - 1) / 24.0, rack_s=0.4)   # from the spinning flesh to the child coming out
    st.hero(s, "flesh", flesh.sprite)
    st.hero(s, "child", kid)
    C.lights(s, "gold", near="door", radius=16.0)


def dg21_crouch(st, s, C, nar):
    """BEAT 21  "He crouched, once, and he stayed down."   frames 1358-1447 (90 f, 3.75 s), sky gold.
    Words: He 1360, crouched 1363, once 1374, and 1388, he 1390, stayed 1393, down 1401 (spoken a tenth slower than
    the rest of the film: speed 0.9; "down" ends on 1414). Then 1.5 s of silence (1415-1447).

    NOW: behind his right shoulder line (CROUCH_CAM, 38 mm f/2.4 from (7.17, -4.92, 1.5) pushing to (7.21, -5.01,
      1.49): ease_out, so the push has all but stopped in the silence): the back of his head in the top-left corner,
      his teal shoulder and bare arm soft at the left, the child's face big and sharp in the middle, looking up at him;
      the rotten flesh still spinning soft on the step at the top right (the same item: its age runs on, so the spin
      does not jump at the cut), the door shut as dg20 left it.
      1365-1393  C.crouch_slow from "crouched" + 2 over 28 frames: he sinks while "crouched, once" is spoken and is
                 down on "stayed"; his head comes down into the frame from the top left, seen three-quarter from
                 behind (hair and the right side of his head, no eyes), and ends leaning over the child, filling the
                 left third; his head stays on the child (watch)
      the child's head follows his face down (track); 1415-1447 nothing moves but the handheld, the push that has all
      but stopped and the spinning flesh.
      (The first camera, (7.56, -5.06, 1.41) at 40 mm, kept his crouched head out of the frame but for a strip of hair.)
    MEASURED (tools.hello_geo at 1358 / 1393 / 1425; renders out/test/hello_dg_dg21_crouch_1360_zones.png, _1365_zones.png,
      _1393_zones.png, _1425_zones.png): standing, his head box x -56..36 %, y -17..31 % (the back of his head in the
      top-left corner); down, x -54..34 %, y 10..51 %; 122-125 degrees off his nose (no eyes). The child's eyes x 53-54 %,
      y 47 %, face 188-194 px, 35-36 degrees off the lens, nothing in front of them; his arm passes about 5 px from
      its left eye at 1358-1364 (rendered: the eye stays clear) and his sleeve covers its left cheek once he is down,
      not its eyes or nose. The flesh's place x 74-101 %, y 9-25 % (soft, under the top icons). palette_check
      dg21@1425: every check passes (hero child x 33-84 %, y 30-56 %, 99 % in the safe area).

    STORY: The same place, camera a little behind his shoulder line, the frame cropped at his chin. He sinks slowly
    into the sneak pose: the torso leans forward and his head comes down into the picture from above, seen
    three-quarter from behind, pitched down at the child. He is still taller than the child, so he ends leaning
    over it. He holds there. Neither of them moves. One second of silence. About 3.5 seconds.
    Cast: the watcher (three-quarter from behind), baby villager (narrator). Effects: player sneak pose, one slow
    crouch over a full second, held, no music.
    SHARED: PLACES "watch_door" + HC.WATCH_YAW, "hello_child". Cast: C.watcher(s, "dg") and C.actor("child", "dg2")
      (both in dg20, the shot before: placed on f0).
    NEIGHBOURS: before, dg20_walkup; after, dg22_eyes (the two-shot of beat 4: the white eyes). Hard cuts.
    """
    f0, f1 = s.frame_start, s.frame_end
    him = C.watcher(s, "dg", place="watch_door")
    kid = C.actor("child", "dg2")
    C.put(kid, f0, "hello_child", toward="watch_door")
    C.crouch_slow(him, C.at(s, "crouched") + 2, frames=28)    # sinks while "crouched, once" is spoken; down on
    #                                                           "stayed"; then nothing moves through the silence
    him.watch(f0, f1, kid)                            # his head on the child (the only part of him that turns)
    kid.look_at(f0, him, ease=0)
    kid.track(f0, f1, him, step=3, ease=1)            # its head follows his face down
    flesh = C.item("rotten_flesh", "dg")              # still spinning on the step (placed in dg20; its age goes on,
    flesh.animate(f0, f1 + 1)                         # so the spin and bob run on over the cut), soft, top right
    st.use(s, kid, flesh)
    C.cam(s, None, focus=kid.head, handheld=0.004, **CROUCH_CAM)
    st.hero(s, "child", kid)
    C.lights(s, "gold", near="door", radius=16.0)


def dg22_eyes(st, s, C, nar):
    """BEAT 22  "The player had blue eyes."   frames 1448-1544 (97 f, 4.04 s), sky gold. The film's last shot.
    Words: The 1450, player 1453, had 1463, blue 1467, eyes 1475 (speed 0.9, like beat 21; "eyes" ends on 1489).
    Then the hold on the white eyes, 1490-1538 (2.0 s), and the CUT TO BLACK: the encoder blacks out the last six
    frames, 1539-1544 (films/hello.py END_BLACK); the Reel then loops to frame 1.

    NOW: CAMS["two_shot"] + the doorstep fill exactly (_two_shot, as dg04). watcher_eyes (white eyes, EYE_GLOW 1.5)
      already crouched on "watch_door" facing WATCH_YAW (C.crouch_held on f0), the child ("dg2") on "hello_child"
      looking up at him. On the cut his face is turned a touch above the child (0.18 block) and settles onto it over
      12 frames (watch snap=False): the one movement of the shot besides the handheld; then only the handheld
      (TWO_SHOT_HANDHELD 0.012, as dg04) floats the frame through the hold: a few pixels, never still (at 0.004 the
      hold changed by 0.2-0.7 grey levels a frame, a frozen picture; now 0.4-1.25, median 0.9, 270x480 previews;
      1470 against 1538: 5.0 instead of 2.0). focus his head; hero "watcher".
    MEASURED (tools.hello_geo every 6th frame 1448-1544; renders out/test/hello_dg_dg22_eyes_1449_zones.png,
      _1472_zones.png, _1496_zones.png, with dg04: _dg04_hello_222_zones.png): the same camera, house front and
      roofline as dg04; eyes x 49.7-50.7 %, y 43.2-43.8 % projected over the sway (rendered about y 48 %), face 178 px,
      21 degrees off his nose; both white eyes unmistakable from the cut; the head box's bottom at most y 56.9 %
      (1496, the far end of the sway): the chin clear of the caption band. palette_check dg22@1496: every check passes
      (hero watcher x 31-76 %, y 32-57 %, 100 % in the safe area).

    STORY: The camera of beat 4, exactly, the same roofline behind his head. His face, turned down to the child and
    the lens, fills the upper part of the frame: where the blue was, both pixels of each eye are blank white,
    faintly glowing. He stays down. Hold two seconds on the two of them, the child's big head below the white eyes,
    then cut to black. About 4 seconds.
    Cast: the watcher (face, first time seen), baby villager (narrator). Effects: white-eyed Steve skin, eyes
    slightly emissive in this shot only, same camera and same fill light as beat 4, two-second hold, then cut to
    black.
    SHARED: _two_shot (CAMS["two_shot"] + the doorstep fill: EXACTLY dg04's), "watch_door" + HC.WATCH_YAW,
      "hello_child". Cast: C.watcher(s, "dg", role="watcher_eyes") (THIS SHOT ONLY), C.actor("child", "dg2").
    NEIGHBOURS: before, dg21_crouch; after, nothing (the film ends on frame 1544, black from 1539).
    """
    f0, f1 = s.frame_start, s.frame_end
    him = C.watcher(s, "dg", place="watch_door", role="watcher_eyes")
    kid = C.actor("child", "dg2")
    C.put(kid, f0, "hello_child", toward="watch_door")
    C.crouch_held(him, f0)
    kid.look_at(f0, him, ease=0)
    eye = kid.eye_point(f0)
    him.look_at(f0, (eye.x, eye.y, eye.z + 0.18), ease=0)     # on the cut his face a touch above the child ...
    him.watch(f0, f1, kid, snap=False, ease=12)               # ... it settles onto it: the only thing that moves
    st.use(s, kid)
    _two_shot(s, C)
    s.focus(him.head)
    st.hero(s, "watcher", him)
    C.lights(s, "gold", near="door", radius=16.0)
