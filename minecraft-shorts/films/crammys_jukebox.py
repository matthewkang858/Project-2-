"""The Crammys, sequence JUKEBOX: the bandstand at night, the party begun; the disc that pops out, the arrows
nobody asks about, the walk to the jukebox and disc eleven going in. Beats 8, 18, 19, 20 (shots jb08_eject,
jb18_nobody_asked, jb19_to_jukebox, jb20_eleven), sky "night". One function per shot; the contract is in
films/crammys_common.py (tags "jb...", C.actor, C.cam, C.lights, C.hold, C.present, C.arrows, C.totem, st.use /
st.hero). STUB by the lead director: every shot builds and renders; its staging is engine/music's worked example
(tools/music_proof.py shot_b8, shot_b18, shot_b19, shot_b20) through the C helpers, filmed by the set builder's
cameras (films/crammys_set.py CAMERAS b08, b18-b20 = engine/music's). Make it a film.

THE PLACE (engine/music.py bandstand; films/crammys_common.py "Coordinates"): the stage faces WEST, the cameras
stand west of it or on it; the jukebox (-7, 0, 1) behind the gap of the front row; ITS TOP (THE SLOT) READS ONLY FROM
ABOVE (0.8 block or more above it, within 4 blocks: jb08's start, jb20): from the front its side is one more note
block. The row of note blocks (x -8, z 1-2) hides performers below the chest from the front. Anchors (C.P / C.yaw):
steve_watch (beat 8, on the ground before the gap), alex_eject / zuri_watch / kai_watch (beat 8, on the stage),
steve_wing, three_sunny / three_steve / three_noor (beat 18), alex (19's start), steve_jukebox (the jukebox's south-
east corner: beats 19-24), alex_beside (beat 20), ring_<name> (THE NIGHT STAGE LAYOUT, 19-24); paths
C.v.paths["bandstand_wing_to_three"] (18). Look targets: jukebox_top_target, steve_away_target,
steve_turn_kicker_target.
THE SKY "night": the moon due east BEHIND the stage (the stage front in the well's moonshadow): THE LANTERNS ARE THE
KEY on every face. C.lights(s, "night") (every lamp x 1.3; never above 1.6 by the well).
SHARED: THE CAT DISC (ejected here in jb08: Jukebox.eject is this sequence's alone), THE DISC (disc 11 in Steve's
hand in jb18-jb20: C.hold), THE ARROWS (C.arrows(steve, s) in jb18-jb20), THE INSERT (jb20 on "one": Jukebox.insert
is this sequence's alone, ON C.insert_frame(); after it THE SONG belongs to C.song), THE TOTEM on the pedestal
(C.totem(s) where it is in frame), THE NIGHT STAGE LAYOUT (ring_*, steve_jukebox: fn21-fn24 use the same spots).
CONTINUITY CHEATS (the story's own, kept; engine/music documents them): Sunny and Noor stand beside Steve in jb18
(three_*) and in the half circle beyond the jukebox in jb19 (ring_*): cut on his walk; Alex steps aside to ring_alex
in jb19 and stands at alex_beside in jb20, then at ring_alex again from fn22.
TAGS TAKEN: steve_jb, alex_jb, zuri_jb, kai_jb, sunny_jb, noor_jb (placed on each shot's first frame).
"""
import math

from films import crammys_common as CC

CS = CC.CS

JB18_STOP_AFTER = 3         # jb18: Steve stops this many frames after "Nobody" appears


def _up(p, dz):
    return (p[0], p[1], p[2] + dz)


def jb08_eject(st, s, C, nar):
    """BEAT 8  "But a creeper drops a music disc if a skeleton kills it."   frames 565-654 (90 f, 3.75 s), sky night.
    Words: But 567, a 569, creeper 571, drops 583, a 593, music 595, disc 604, if 615, a 618, skeleton 620, kills 632,
    it 641. The voice ends on 644; the shot runs on 10 frames after it (0.42 s).

    STORY (beat 8): Night, lanterns lit, the party begun. Over Steve's shoulder at the foot of the stage: Alex pops a
    disc out of the jukebox and the disc item turns in the air above it in the lantern light. Steve's head follows the
    disc, then turns slowly away from the stage toward the dark end of the square. Focus pulls from the disc to his
    profile.
    Cast: Steve, Alex, Zuri, Kai. Effects: jukebox, music disc ejected as a spinning dropped item, lantern bloom, focus
    pull.

    MUST BE SEEN, ON WHICH WORD
      frame 1          night, lanterns lit, the party begun: the jukebox playing (its notes rising: the cat disc),
                       high over Steve's shoulder at the foot of the stage, the jukebox's top (the slot) in view
      "creeper drops"  Alex pops the disc out (Jukebox.eject: the swing, the notes stop, the disc tossed up): the disc
                       item turning in the air above the jukebox in the lantern light
      "music disc"     Steve's head follows the disc
      "if a skeleton"  ... then he turns slowly away from the stage toward the dark end of the square (body and head:
                       the head alone stops at 70 degrees); the focus pulls from the disc to his profile
    SHARED: THE CAT DISC (Jukebox.eject here only), the totem (C.totem). Places: steve_watch, alex_eject, zuri_watch,
      kai_watch, steve_away_target; the kicker on his turned face (music b8: 30 W at steve_turn_kicker_target).
    NEIGHBOURS: before, rd07_chased (the lane); after, rd09_torch (the exit gate: he walks out past the last torch).
    MEASURED (crammys_set_b08_eject.png, music b8, 32 mm f/2.4 from z 3.0, its 30 W kicker): the disc above the jukebox
      at x 44 %, y 37 %, the jukebox top 52, 49 %, Alex 56, 37 %, Zuri and Kai watching, Steve's head soft below;
      palette passes (stone G/R 0.96, trousers min channel 23); without the kicker his turned face and trousers were
      crushed (palette 11 < 12, engine/music).
    """
    f0, f1 = s.frame_start, s.frame_end
    jt = C.P("jukebox_top_target")
    z, k, a, steve = (C.actor(n, "jb") for n in ("zuri", "kai", "alex", "steve"))
    for p, spot in ((z, "zuri_watch"), (k, "kai_watch"), (a, "alex_eject"), (steve, "steve_watch")):
        C.put(p, f0, spot)
        p.look_at(f0, jt, ease=0)
    fe = C.at(s, "drops") - 2
    # the cat disc playing: a note born on f0 - 2 (563) is rising on frame 1 (it lives 7.2 frames) and the next
    # one (587) is cancelled by the eject (fe = 581): the first stub's play(f0 - 30) put its notes on 535 and 559,
    # so frame 1 showed only the last frame or two of a dying note (the technical review)
    C.bd.jukebox.play(f0 - 2, fe, disc="music_disc_cat", camera=s)
    item = C.bd.jukebox.eject(fe, player=a, disc="music_disc_cat", camera=s, until=f1 + 1, name="crammys_cat_jb")
    st.cast[item.name] = item
    steve.look_at(fe + 2, item.root, ease=6)
    fa = C.at(s, "if") - 4
    C.turn_to(steve, fa, C.P("steve_away_target"), ease=20, head_ease=16)
    C.totem(s)
    st.use(s, steve, item, z, k, a)
    st.hero(s, "disc", item.sprite)
    C.cam(s, "set:b08", focus=item.sprite, handheld=0.004)
    s.focus(steve.head, at_s=s.film.seconds(fa + 4))
    C.lights(s, "night")
    C.kicker("jb_turn", s, C.P("steve_turn_kicker_target"), watts=30.0)


def jb18_nobody_asked(st, s, C, nar):
    """BEAT 18  "Nobody asked."   frames 1103-1148 (46 f, 1.92 s), sky night.
    Words: Nobody 1105, asked 1118. The voice ends on 1131; the shot runs on 17 frames after it (0.71 s).

    STORY (beat 18): From the front of the stage at head height, a medium three-shot. Steve walks on from the wing,
    already at stage height, and stops between Sunny and Noor, the arrows plain in the lantern light. Sunny's head turns
    to the arrows for one beat, then back to the jukebox. Noor does not turn at all.
    Cast: Steve, Sunny, Noor. Effects: arrows stuck in the player, lantern rim light on the fletching, one head turn
    there and back.

    MUST BE SEEN, ON WHICH WORD
      frame 1          from the front of the stage at head height, a medium three-shot; Steve already walking on from
                       the wing (already at stage height), the disc in his hand
      "Nobody"         he stops between Sunny and Noor, the TWO ARROWS plain in the lantern light (the lantern rim on
                       the fletching)
      "asked"          Sunny's head turns to the arrows for one beat, then back to the jukebox; Noor does not turn
    SHARED: THE DISC (C.hold), THE ARROWS (C.arrows). Places: three_sunny, three_steve, three_noor; path
      bandstand_wing_to_three.
    NEIGHBOURS: before, rd17_run_back (the lane); after, jb19_to_jukebox (from behind him: he walks on to the jukebox).
    MEASURED (crammys_set_b18_nobody_asked.png, music b18, 40 mm f/3.2): Sunny 23 %, Steve 47 % with both arrows plain
      in the lantern light, Noor 72 % (y 46 %). This shot is 46 frames: the walk the camera sees is the path from its
      point 2 (music); the turn there and back must fit after he stops. The lead's scout with the ALIGNED arrows
      (out/test/crammys_scout_aligned_jb18_nobody_asked_1135_zones.png; geo: Sunny 22 %, Steve 47 %, Noor 72 %, faces
      81-90 px): the arrows now stick out to his front right, toward Sunny: the chest arrow's shaft shows beside
      Sunny's raised arm, half hidden by it, the shoulder one hardly: turn Steve a little to his left, or stand Sunny
      back, so the two fletchings stand clear.
    """
    f0, f1 = s.frame_start, s.frame_end
    jt = C.P("jukebox_top_target")
    su, no, steve = (C.actor(n, "jb") for n in ("sunny", "noor", "steve"))
    C.put(su, f0, "three_sunny")
    su.look_at(f0, jt, ease=0)
    C.put(no, f0, "three_noor")
    no.look_at(f0, jt, ease=0)
    # already walking on frame 1 (the game's walk, at speed) on the last leg of bandstand_wing_to_three, placed so
    # that he stops on "Nobody" + 3 (C.walk_lead): the first stub walked the path from its point 2 (3.0 blocks at
    # 1.6 b/s = 45 frames of a 46-frame shot) and never stopped (the technical review)
    sp = C.P("three_steve")
    back = C.v.paths["bandstand_wing_to_three"][-2]
    arrive = C.at(s, "Nobody") + JB18_STOP_AFTER
    lead = C.walk_lead(f0, arrive)
    d = math.dist(back[:2], sp[:2])
    k = min(1.0, lead / d)
    start = (sp[0] + (back[0] - sp[0]) * k, sp[1] + (back[1] - sp[1]) * k, sp[2])
    steve.place(f0, start, CC.yaw_to(start, sp))
    C.arrows(steve, s)
    C.hold(steve, "music_disc_11", s)
    end = steve.walk(f0, [start, sp], ramp=(False, True))
    steve.look_at(end, jt, ease=8)
    su.look_at(end + 4, (sp[0], sp[1], sp[2] + 1.2), ease=6)         # to the arrows (chest height) ...
    su.look_at(end + 16, jt, ease=6)                                 # ... and back to the jukebox
    C.memo["jb18_stop"] = end
    st.use(s, su, no, steve)
    st.hero(s, "steve", steve)
    C.cam(s, "set:b18", focus=steve.head, handheld=0.004,
          pos1=tuple(p + d for p, d in zip(CS.CAMERAS["b18"]["pos"], (0.12, 0.0, 0.0))))
    C.lights(s, "night")


def jb19_to_jukebox(st, s, C, nar):
    """BEAT 19  "I put my disc in the jukebox."   frames 1149-1200 (52 f, 2.17 s), sky night.
    Words: I 1151, put 1154, my 1157, disc 1162, in 1172, the 1175, jukebox 1177. The voice ends on 1195; the shot runs
    on 5 frames after it (0.21 s).

    STORY (beat 19): From behind and a little above Steve, over his shoulder with the arrows in the foreground. He walks
    toward the jukebox at centre stage, the disc in his raised hand. Alex steps aside. Beyond the jukebox Zuri, Kai,
    Sunny and Noor stand in a staggered half circle facing us, watching him come.
    Cast: Steve, Alex, Zuri, Kai, Sunny, Noor. Effects: jukebox, held music disc, arrows stuck in the player, staggered
    half circle so no face hides behind a neighbour.

    MUST BE SEEN, ON WHICH WORD
      frame 1          from behind and a little above Steve, his back and the arrows in the foreground, the disc in
                       his RAISED hand (C.present toward the jukebox top), already walking
      "put my disc"    Alex steps aside (alex -> ring_alex)
      "jukebox"        beyond the jukebox Zuri, Kai, Sunny and Noor in the staggered half circle (ring_*) facing us,
                       watching him come; no face behind a neighbour
    SHARED: THE DISC, THE ARROWS, THE NIGHT STAGE LAYOUT (ring_*, steve_jukebox). Places: three_steve -> steve_jukebox.
    NEIGHBOURS: before, jb18_nobody_asked (cut on his walk); after, jb20_eleven (from across the jukebox).
    MEASURED (crammys_set_b19_to_jukebox.png, music b19, 28 mm f/4 from (-6.9, -3.9, 4.0)): Kai 61, Zuri 50, Sunny 38,
      Noor 29 % (y 44-48 %) face us across the jukebox; Steve's back at the bottom right (x 85-100 %) and THE ARROWS
      HARDLY READ FROM BEHIND (the story's "arrows in the foreground"): a lower or more side-on start, or the lantern
      rim on the fletching, is this shot's open problem. The lead's geo of this stub at 1190: STEVE'S HEAD AT y 52-64 %
      (the back of it, in the caption band) as he nears the jukebox; Alex 121 degrees off the lens as she walks aside;
      the four faces x 28-61 %, y 44-48 %, 47-61 px, 6-14 degrees off the lens.
    """
    f0, f1 = s.frame_start, s.frame_end
    names = ("kai", "zuri", "sunny", "noor")
    four = [C.actor(n, "jb") for n in names]
    for p, n in zip(four, names):
        C.put(p, f0, "ring_" + n)
    steve = C.actor("steve", "jb")
    C.put(steve, f0, "three_steve")
    C.arrows(steve, s)
    C.hold(steve, "music_disc_11", s)
    C.present(steve, s, _up(C.P("jukebox_top_target"), 0.9))
    steve.walk(f0 + 2, [C.P("three_steve"), C.P("steve_jukebox")], speed=1.3)
    for p in four:
        p.look_at(f0, steve, ease=0)
        for f in range(f0 + 8, f1, 8):
            p.look_at(f, steve, ease=6)
    a = C.actor("alex", "jb")
    C.put(a, f0, "alex")
    a.look_at(f0, steve, ease=0)
    a.walk(C.at(s, "put"), [C.P("alex"), C.P("ring_alex")], speed=1.2)
    st.use(s, steve, a, *four)
    for p, n in zip(four, names):
        st.hero(s, n, p)
    C.cam(s, "set:b19", focus=C.P("ring_zuri"), handheld=0.004,
          pos1=tuple(p + d for p, d in zip(CS.CAMERAS["b19"]["pos"], (0.0, 0.25, -0.1))))
    C.lights(s, "night")


def jb20_eleven(st, s, C, nar):
    """BEAT 20  "It was disc eleven, the broken one."   frames 1201-1264 (64 f, 2.67 s), sky night.
    Words: It 1203, was 1206, disc 1209, eleven 1217, the 1234, broken 1236, one 1248. The voice ends on 1255; the shot
    runs on 9 frames after it (0.38 s).

    STORY (beat 20): Close, from across the jukebox. Steve's arm points straight at the lens so the disc is face-on and
    sharp, a third of the frame: black, cracked, a piece missing. His face is soft behind it. Beside it Alex's hand
    holds out her whole green disc for contrast. He lowers the broken one into the jukebox and the first note rises.
    Cast: Steve, Alex. Effects: music disc eleven as a close-up hero prop, face to the lens, green disc (Cat) held
    beside it, disc going into the jukebox, first note particle, lantern key light.

    MUST BE SEEN, ON WHICH WORD
      frame 1 .. "broken"   close, from across the jukebox: Steve's arm straight at the lens, DISC ELEVEN face-on and
                       SHARP, a third of the frame (black, cracked, a piece missing); his face soft behind it; beside it
                       Alex's hand holds out her whole green disc (cat) for contrast
      "broken" .. "one"   he lowers the broken one ...
      "one"            ... INTO THE JUKEBOX ON THIS WORD (THE INSERT: C.insert_frame(); Jukebox.insert(f, player=steve,
                       disc="music_disc_11", camera=s, until=s.frame_end + 1)): the swing, the disc gone one tick later,
                       THE FIRST NOTE one tick after the click, rising before the cut
    SHARED: THE INSERT (this shot alone; THE SONG after it is C.song's in fn21-fn24), THE DISC, THE CAT DISC (Alex),
      THE ARROWS. Places: steve_jukebox, alex_beside.
    NEIGHBOURS: before, jb19_to_jukebox; after, fn21_running (the jukebox sharp in the foreground, notes drifting up).
    MEASURED (crammys_set_b20_disc11.png, music b20, 40 mm f/2.4 from (-8.0, 2.1, 2.65)): disc 11 at x 20 %, y 44 % (a
      third of the frame), the cat disc at 72, 45 %, Steve's face between them. The lead's scout of this stub
      (out/test/crammys_scout_jb20_eleven_1225_zones.png): disc 11 face-on at x 5-37 %, y 38-50 %, broken and black,
      the cat disc face-on at x 58-90 %, Steve's face between (eyes x 40 %, 160 px, 3 degrees off the lens); Alex's
      face is cut by the right edge (geo: x 74-108 %); the jukebox's slot big and soft in the lower third.
    RISK (story): "a sixteen-pixel item may not read as broken at phone size": the arm points at the lens, the disc a
      third of the frame and in focus; the fallback is item frames on the back wall (not built).
    """
    f0, f1 = s.frame_start, s.frame_end
    cam = CS.CAMERAS["b20"]
    steve = C.actor("steve", "jb")
    C.put(steve, f0, "steve_jukebox")
    C.arrows(steve, s)
    fi = C.insert_frame()
    disc = C.hold(steve, "music_disc_11", s)
    steve.look_at(f0, C.P("jukebox_top_target"), ease=0)
    C.present(steve, s, cam["pos"], f1=C.at(s, "broken") - 2)
    a = C.actor("alex", "jb")
    C.put(a, f0, "alex_beside")
    C.hold(a, "music_disc_cat", s)
    a.look_at(f0, steve, ease=0)
    C.present(a, s, cam["pos"])
    C.bd.jukebox.insert(fi, player=steve, disc="music_disc_11", camera=s, until=f1 + 1)
    st.use(s, steve, a)
    st.hero(s, "disc 11", disc)
    C.cam(s, "set:b20", focus=disc, handheld=0.004,
          pos1=tuple(p + d for p, d in zip(cam["pos"], (0.06, -0.05, 0.0))))
    s.focus(C.P("jukebox_top_target"), at_s=s.film.seconds(C.at(s, "broken")))
    C.lights(s, "night")
