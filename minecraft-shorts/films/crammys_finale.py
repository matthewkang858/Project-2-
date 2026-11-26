"""The Crammys, sequence FINALE: the bandstand at night while disc eleven plays: the song, nobody moved, Kai, Best
Vocals. Beats 21-24 (shots fn21_running, fn22_nobody_moved, fn23_kai, fn24_vocals), sky "night". One function per
shot; the contract is in films/crammys_common.py (tags "fn...", C.actor, C.cam, C.lights, C.hold, C.present, C.clap,
C.arrows, C.song, C.totem, st.use / st.hero). STUB by the lead director (fn24's camera and totem, fn21 / fn22's note
frames corrected after the two checks of the plan): every shot builds and renders; its staging is engine/music's worked
example (tools/music_proof.py shot_b21 .. shot_b24) through the C helpers, filmed by the set
builder's cameras (films/crammys_set.py CAMERAS b21-b24 = engine/music's). Make it a film.

THE PLACE (engine/music.py bandstand; films/crammys_common.py "Coordinates"): THE NIGHT STAGE LAYOUT, the same spots
in all four shots: Steve at steve_jukebox (the jukebox's south-east corner, facing it), Alex Kai Zuri Sunny Noor at
ring_<name> (a staggered arc north of the jukebox, all facing it, 0.7-0.75 apart in y: from the front no face is
behind another; nobody in the jukebox's note column y 0..1); Kai's one step ends at kai_step. The jukebox (-7, 0, 1),
its notes rising in its column (x -6.5, y 0.5, z 2.2-2.75); the pedestal (-9, -1) with the totem (C.totem) up to fn23,
EMPTY in fn24. The village lamp post at (-17.3 / -15.7, 2.5) stands in the corridor before the stage (fn22 and
fn24's end are placed south of it).
THE SKY "night": the moon due east, BEHIND the stage: the lanterns are the key; in the frontal wide (fn22) the moon
stands over the bandstand (x 62 %, y 16 %). C.lights(s, "night") (x 1.3).
SHARED: THE SONG (C.song(s) in every shot: the jukebox's notes in phase with jb20's insert; never Jukebox.play here),
THE ARROWS (C.arrows(steve, s) in every shot), THE TOTEM (on the pedestal in fn21-fn23 where in frame; in Steve's
hand in fn24, the pedestal empty), THE NIGHT STAGE LAYOUT.
CONTINUITY CHEAT (the story's, engine/music documents it): Alex stands at alex_beside in jb20 and at ring_alex from
fn22 (fn21 does not show her).
TAGS TAKEN: steve_fn, alex_fn, kai_fn, zuri_fn, sunny_fn, noor_fn (placed on each shot's first frame).
"""
from films import crammys_common as CC

CS = CC.CS


# fn24: the opening medium and the pull back on ONE 32 mm lens (the engine has no zoom): close enough at the start
# for the medium (the set builder's b24 at 40 mm from 5.6 blocks), far enough at the end for all six heads inside
# x 14-69 % (geo at 1550: Noor 14, Sunny 24, Zuri 34, Kai 42, Alex 51, Steve 69; with b24's 40 mm and aim they
# spanned 11-80 %, Steve on the icon column)
FN24_CAM = dict(pos=(-10.1, -0.45, 2.75), target=(-5.6, -0.3, 2.45), pos1=(-19.5, 0.3, 4.6), target1=(-5.5, 1.4, 2.3),
                lens=32.0, fstop=2.8)
FN24_TOTEM_AIM = (0.0, 1.5, -0.6)          # the arm's aim from the lens: north (his right: the frame's left), lower
FN24_SETTLE = 1538                         # the pull back has settled (the last 1.5 s held after "Vocals")


def _six(C, s, look=None):
    """The night stage layout on shot s's first frame: {name: player}, everybody facing the jukebox top (or `look`)."""
    f0 = s.frame_start
    jt = C.P("jukebox_top_target") if look is None else look
    out = {}
    for n in CC.NIGHT_STAGE:
        p = C.actor(n, "fn")
        C.put(p, f0, "ring_" + n)
        p.look_at(f0, jt, ease=0)
        out[n] = p
    steve = C.actor("steve", "fn")
    C.put(steve, f0, "steve_jukebox")
    C.arrows(steve, s)
    steve.look_at(f0, jt, ease=0)
    out["steve"] = steve
    return out


def fn21_running(st, s, C, nar):
    """BEAT 21  "It's just someone running away and breathing hard."   frames 1265-1343 (79 f, 3.29 s), sky night.
    Words: It's 1267, just 1270, someone 1275, running 1285, away 1292, and 1304, breathing 1307, hard 1317. The voice
    ends on 1329; the shot runs on 14 frames after it (0.58 s).

    STORY (beat 21): The jukebox sharp in the foreground, notes drifting up from it. Slow push past it to Steve standing
    stiff beside it with the two arrows in him. His head turns slowly from the jukebox to the others.
    Cast: Steve. Effects: jukebox note particles, arrows stuck in the player, slow push in, optional sound: original
    running feet and panting under the line, not the game's recording.

    MUST BE SEEN, ON WHICH WORD
      frame 1          the jukebox sharp in the foreground (its slot from above), THE PUSH ALREADY MOVING (C.cam's
                       ease_out: the movement on frame 1). No note is in the air on frame 1: the insert's first note
                       (born 1250) is gone by 1257 and the film ends every particle at the change of sequence; THE
                       SONG's first note here rises on 1274 (then 1298, 1322: tools.crammys_probe notes). (Corrected
                       after the technical check: the first docstring promised a note on frame 1.)
      "running away"   the slow push past it to Steve standing stiff beside it, the two arrows in him
      "breathing hard" his head turns slowly from the jukebox to the others
    SHARED: THE SONG (C.song), THE ARROWS. Places: steve_jukebox, ring_kai (his look).
    NEIGHBOURS: before, jb20_eleven (the insert, the first note); after, fn22_nobody_moved (the frontal wide).
    MEASURED (crammys_set_b21_jukebox.png, music b21, 32 mm f/2.4 push): the jukebox slot in front at x 50 %, y 53 % and
      Steve beside it with both arrows plain; at the end of the push his head 50, 48 % (music). (The set builder's
      still had the old unaligned shoulder arrow: see THE ARROWS in films/crammys_common.py.)
    RISK (story): "the joke is a sound and the picture cannot show it; the line carries it" (fallbacks: an original
      sound of running feet and panting; or one second of rd07's chase cut in: NOT available, the cuts are fixed).
    """
    f0, f1 = s.frame_start, s.frame_end
    steve = C.actor("steve", "fn")
    C.put(steve, f0, "steve_jukebox")
    C.arrows(steve, s)
    steve.look_at(f0, C.P("jukebox_top_target"), ease=0)
    steve.look_at(C.at(s, "breathing") - 8, C.eyes("ring_kai"), ease=20)
    C.song(s)
    st.use(s, steve)
    st.hero(s, "steve", steve)
    C.cam(s, "set:b21", focus=(-6.5, 0.5, 2.1), handheld=0.004)
    s.focus(steve.head, at_s=s.film.seconds(C.at(s, "running")))
    C.lights(s, "night")


def fn22_nobody_moved(st, s, C, nar):
    """BEAT 22  "Nobody moved."   frames 1344-1394 (51 f, 2.12 s), sky night.
    Words: Nobody 1346, moved 1358. The voice ends on 1369; the shot runs on 25 frames after it (1.04 s).

    STORY (beat 22): The film's one locked-off frontal wide of the whole stage. Six players stand completely still, all
    facing the jukebox. The only movement is the notes rising and the lantern glow. Hold a full second after the words.
    Cast: Steve, Alex, Zuri, Kai, Sunny, Noor. Effects: jukebox note particles, lantern bloom, all figures frozen, one-
    second hold.

    MUST BE SEEN, ON WHICH WORD
      frame 1 .. end   THE FILM'S ONE LOCKED-OFF FRONTAL WIDE of the whole stage: six players completely still, all
                       facing the jukebox; the only movement the notes rising (C.song: notes on 1346 and 1370; the one
                       on 1394 is left out, since a note born in the last 7 frames of a shot would float on into fn23
                       facing this camera (the technical check); C.song does that for every shot) and the lantern
                       glow; the moon over the bandstand. Hold about a second after "moved" (the shot runs on 1.0 s
                       after the voice).
    SHARED: THE SONG, THE ARROWS, THE NIGHT STAGE LAYOUT, THE TOTEM on the pedestal.
    NEIGHBOURS: before, fn21_running; after, fn23_kai (along the row of faces).
    MEASURED (crammys_set_b22_nobody_moved.png, music b22, 24 mm f/5.6 from (-20.5, -0.3, 3.6)): the six faces at
      x 24-63 %, y 48 % (small: about 4.5 % of the frame wide each: a wide), both lantern posts at 29 % / 84 %, the
      moon at 62, 16 %. "Locked-off" here = no move; the stub keeps a handheld of 0.002 (nothing is ever dead still).
      The lead's geo of this stub at 1370: faces 20-23 px, x 24-63 %, y 48 %; Noor 71 and Sunny 67 degrees off the
      lens (they look at the jukebox: profiles), Steve and Kai 42.
    """
    f0, f1 = s.frame_start, s.frame_end
    six = _six(C, s)
    C.song(s)
    C.totem(s)
    st.use(s, *six.values())
    st.hero(s, "steve", six["steve"])
    C.cam(s, "set:b22", focus=(-5.5, 2.0, 2.4), handheld=0.002)
    C.lights(s, "night")


def fn23_kai(st, s, C, nar):
    """BEAT 23  "Kai said it sounded just like me coming home."   frames 1395-1473 (79 f, 3.29 s), sky night.
    Words: Kai 1397, said 1405, it 1410, sounded 1413, just 1424, like 1432, me 1436, coming 1439, home 1447. The voice
    ends on 1457; the shot runs on 16 frames after it (0.67 s).

    STORY (beat 23): From beside the jukebox, looking along the row of faces. Kai takes one slow step forward and his
    head turns from the jukebox to Steve. Then Zuri's, Sunny's, Noor's and Alex's heads turn to Steve too, one after
    another. Steve looks at the jukebox, then at them.
    Cast: Kai, Zuri, Sunny, Noor, Alex, Steve. Effects: one slow step by Kai (at least seven frames), five head turns in
    sequence, jukebox note particles.

    MUST BE SEEN, ON WHICH WORD
      "Kai"            Kai takes ONE slow step forward (ring_kai -> kai_step, at least 7 frames: speed 0.8) and his
                       head turns from the jukebox to Steve: he is the one who speaks (no mouth, no chat)
      "sounded" .. "like"   then Zuri's, Sunny's, Noor's and Alex's heads turn to Steve, one after another
      "coming home"    Steve looks at the jukebox, then at them
    SHARED: THE SONG, THE ARROWS, THE NIGHT STAGE LAYOUT, THE TOTEM (the pedestal big in the foreground).
    NEIGHBOURS: before, fn22_nobody_moved; after, fn24_vocals (Steve with the totem).
    MEASURED (crammys_set_b23_kai*.png, music b23, 24 mm f/3.2 from (-10.6, -3.4, 3.5)): Noor 12, Sunny 24, Zuri 36,
      Kai 48 then 53 after his step, Alex 62, Steve 76 % (y 44-47 %); the five turned 17-40 degrees from the lens
      once they look at him; the pedestal big in the foreground. The lead's geo of this stub at 1460: the five x
      11-62 %, y 44-45 %, faces 41-44 px, 21-39 degrees off the lens; Steve the back of his head (123 degrees) at 77 %.
    RISK (story): "only works if the viewer remembers the chase ... and knows Kai saw it": Kai's head turns ALONE for
      half a second before the others (the story's fallback, built into the stub's timing).
    """
    f0, f1 = s.frame_start, s.frame_end
    six = _six(C, s)
    kai, steve = six["kai"], six["steve"]
    kai.walk(f0 + 4, [C.P("ring_kai"), C.P("kai_step")], speed=0.8)
    kai.look_at(f0 + 6, steve, ease=10)
    t0 = max(f0 + 22, C.at(s, "sounded") - 2)
    for i, n in enumerate(("zuri", "sunny", "noor", "alex")):
        six[n].look_at(t0 + 7 * i, steve, ease=7)
    steve.look_at(C.at(s, "coming") - 4, C.eyes("ring_zuri"), ease=10)
    C.song(s)
    C.totem(s)
    st.use(s, *six.values())
    st.hero(s, "kai", kai)
    C.cam(s, "set:b23", focus=kai.head, handheld=0.004,
          pos1=tuple(p + d for p, d in zip(CS.CAMERAS["b23"]["pos"], (0.1, 0.12, 0.0))))
    C.lights(s, "night")


def fn24_vocals(st, s, C, nar):
    """BEAT 24  "I won Best Vocals."   frames 1474-1562 (89 f, 3.71 s), sky night.
    Words: I 1476, won 1480, Best 1486, Vocals 1494. The voice ends on 1509; the shot runs on 53 frames after it: 47
    frames of picture (1510-1556 = 1.96 s), then the 6 black frames 1557-1562 (END_BLACK).

    STORY (beat 24): Medium on Steve centre stage, facing the lens, his arm straight out so the totem of undying faces
    the camera, the two arrows still sticking out of him. The gold pedestal in the bottom of the frame is empty. Slow
    pull back to reveal the five others crouching up and down fast, the way players clap. Notes and lantern bloom. Hold
    on Steve standing perfectly still for a second and a half after the last word.
    Cast: Steve, Alex, Zuri, Kai, Sunny, Noor. Effects: held totem of undying, face to the lens, empty gold block
    pedestal, arrows stuck in the player, crouch applause by five players, jukebox note particles, slow pull back, hold
    after the last word.

    MUST BE SEEN, ON WHICH WORD (the cue as corrected after the story check: with C.cam's ease_out the pull back was
    25 % done on "Best" and 40 % on "Vocals", Steve at x 64-69 % and the totem small by the last word)
      frame 1 .. "Best"   medium on Steve centre stage facing the lens, his arm straight out so THE TOTEM faces the
                       camera BESIDE (not over) his face (C.hold + C.present aimed FN24_TOTEM_AIM off the lens), the two
                       arrows still in him, the EMPTY gold pedestal big in the bottom of the frame (no C.totem here);
                       the camera HOLDS (a 3 % creep) through "I won Best"
      "Best" (1486) .. 1538   the slow pull back FROM REST (C.timing_hold_move: 'smooth' from 1484 to FN24_SETTLE =
                       1538) reveals the five others crouching up and down fast (C.clap from "Best", staggered 2
                       frames each; the players' applause), notes (1490, 1514, 1538) and lantern bloom
      1538 .. 1556     settled: Steve standing perfectly still among the five (1.5 s after "Vocals" ends on 1509 and
                       the voice; the picture runs 47 frames = 1.96 s after "Vocals", then 1557-1562 black: END_BLACK)
    SHARED: THE TOTEM (in his hand: the pedestal empty), THE SONG, THE ARROWS, THE NIGHT STAGE LAYOUT.
    NEIGHBOURS: before, fn23_kai; after, none (the Reel loops to gd01).
    THE CAMERA (FN24_CAM): ONE 32 mm lens for the medium and the wide (the engine has no zoom): from (-10.1, -0.45,
      2.75), 4.5 blocks from Steve, back and up to (-19.5, 0.3, 4.6), aimed at (-5.5, 1.4, 2.3) at the end. The set
      builder's b24 (40 mm, ending aimed at y 1.8) left the six heads at x 11-80 %, Steve on the Reels icon column;
      at 40 mm no aim fits all six inside the safe area (geo at 1550).
    MEASURED (tools.crammys_probe track fn24_vocals; out/test/crammys_scout_fn24_vocals_1480 / _1494_zones.png):
      1474  Steve's eyes x 50 %, y 47 %; THE TOTEM x 27-43 %, y 43-54 % (17 % of the frame wide), face-on, beside his
            face (his right hand: the frame's left); both fletchings beside it; the pedestal's gold block filling the
            bottom third; Alex's shoulder at the left edge
      1494  "Vocals": the pull back begun (camera 15 % of the way): Steve x 56 %, the totem x 37-51 % (13 % wide),
            Zuri in at the left, a note rising
      1520  Noor in at the left edge; 1538 settled: Noor 14, Sunny 24, Zuri 34, Kai 42, Alex 51, Steve 69 % (eyes
            y 47-49 %), faces 28-33 px; the totem x 62-67 % (5 % wide) at his side
    RISKS (story): "Crouch applause may puzzle non-players" (fallback: two players jumping; keep the totem inside the
      safe area so the win reads on its own); "held flat items turn edge-on if the arm drops or the camera moves to
      the side": the arm stays aimed at FN24_TOTEM_AIM (about 15 degrees off the end camera); check the totem at phone
      size along the whole pull back.
    """
    f0, f1 = s.frame_start, s.frame_end
    cam = FN24_CAM
    six = _six(C, s, look=cam["pos"])
    steve = six["steve"]
    steve.look_at(f0, cam["pos"], ease=0)
    totem = C.hold(steve, "totem_of_undying", s)
    # the arm points at a spot beside and below the lens (FN24_TOTEM_AIM), not at the lens itself: aimed from the
    # shoulder straight at the lens, the totem sat between his eyes and the camera and covered half his face
    # (the lead's scout, crammys_scout_fn24_vocals_1480_zones.png)
    C.present(steve, s, tuple(c + d for c, d in zip(cam["pos"], FN24_TOTEM_AIM)))
    best = C.at(s, "Best")
    for i, n in enumerate(("zuri", "kai", "sunny", "noor", "alex")):
        six[n].look_at(f0, steve, ease=0)
        C.clap(six[n], best + 2 * i, count=max(1, (FN24_SETTLE - best) // 4))
    C.song(s)
    st.use(s, *six.values())
    st.hero(s, "totem", totem)
    # the camera holds the medium on Steve and the totem through "I won Best" (a slow creep), pulls back from rest
    # on "Best" ('smooth', a written exception to C.cam's ease_out for this one shot) and has settled by
    # FN24_SETTLE: the last 1.5 s are Steve standing still among the five clapping
    C.cam(s, None, focus=totem, handheld=0.004,
          timing=C.timing_hold_move(best - 2, FN24_SETTLE, f0=f0, creep=0.03), **cam)
    s.focus(steve.head, at_s=s.film.seconds(C.at(s, "Vocals")))
    C.lights(s, "night")
