"""The Crammys, sequence GOLD: the bandstand on the village square in golden light, before the party. Beats 1-6
(shots gd01_everyone, gd02_zuri, gd03_kai, gd04_sunny, gd05_trophy, gd06_line), sky "gold". One function per shot;
the contract is in films/crammys_common.py (tags "gd...", C.actor, C.cam, C.lights, C.hold, C.present, st.use /
st.hero). STUB by the lead director: every shot below builds and renders; its staging is engine/music's worked
example (tools/music_proof.py shot_b1 .. shot_b6) through the C helpers, filmed by the set builder's cameras
(films/crammys_set.py CAMERAS b01-b06). Make it a film: the words, the timing, the faces, the cuts.

THE PLACE (engine/music.py bandstand, films/crammys_common.py "Coordinates"): the stage faces WEST; the cameras stand
in the corridor west of it looking east; the front row of note blocks at x -8 (Sunny's on a PUMPKIN at y -2, Kai's
on GOLD at y 1, Zuri's on WHITE WOOL at y 2), the jukebox (-7, 0, 1) behind the gap at y 0, the pedestal with the
totem at (-9, -1) before the stage, the lantern posts (-8, +-3). The cast's spots are the band's anchors: C.P("zuri"),
"kai", "sunny", "noor", "alex_post", "steve_front", "steve_kai", "steve_foot", "line_1".."line_5"; look targets
C.P("note_kai_target"), "jukebox_top_target", "last_lantern_target".
THE SKY "gold": the sun low in the SOUTH-WEST (az 240, el 27), in front of the stage, 120 degrees off a camera looking
east at it: the stage front sunlit, the posts' shadows on the wool. C.lights(s, "gold") (every lamp x 1.0).
THE LAST LANTERN: the north post (-8, 3) has NO lantern in gd01-gd04; Alex places it in gd05 (bd.last_lantern.place:
this sequence's, exactly once). Notes: C.bd.notes[who].tap / song(player, frame, ..., camera=s) (the note one tick
after the swing; each right-click one semitone up, a new colour); a goat horn makes no note (players toot).
TAGS TAKEN: steve_gd, zuri_gd, kai_gd, sunny_gd, noor_gd, alex_gd (each placed on its shots' first frames, never
pre-rolled). A twin: C.actor("steve", "gd2") ...
NEIGHBOURS: gd06_line is followed by rd07_chased: THE HARD CUT TO NIGHT (the road sequence, from Kai's doorstep).
"""

from films import crammys_common as CC

GD01_CAM = CC.CS.CAMERAS["b01"]          # (the set builder's suggestions; make them this file's own constants)


def gd01_everyone(st, s, C, nar):
    """BEAT 1  "In this town, everyone is musical except me."   frames 1-85 (85 f, 3.54 s), sky gold.
    Words: In 8, this 10, town 16, everyone 33, is 45, musical 48, except 61, me 71. The voice ends on 77; the shot runs
    on 8 frames after it (0.33 s).

    STORY (beat 1): Golden hour, sun from the side. Low camera, long lens, slow push in. Steve (the narrator) sharp in
    the foreground, three-quarter front, both hands empty. Behind him, soft, on the wool bandstand: Zuri, Kai and Sunny
    each tap a note block and a coloured note pops above each block. Noor raises a goat horn to her face (no note: a
    horn makes none). Nothing rises anywhere near Steve. He turns his head back to look at them, then to the front.
    Cast: Steve, Zuri, Kai, Sunny, Noor. Effects: wool bandstand, three note blocks (on white wool, gold block,
    pumpkin), goat horn raised to the face, note particles above the three note blocks only, arm swing on a note block,
    slow push in.

    MUST BE SEEN, ON WHICH WORD
      frame 1          the film's first picture: something already moving (the push in, a tap, a note in the air)
      "everyone" .. "musical"   the three notes popping above the three note blocks (Zuri, Kai, Sunny: three colours),
                       Noor with the goat horn at her face (NO note: a horn makes none)
      "except me"      Steve sharp in the foreground, NOTHING rising near him; he has turned his head back to them
                       and comes round to the front
    SHARED: none of the camera. Places: steve_front, zuri, kai, sunny, noor. The totem on the pedestal (C.totem).
    NEIGHBOURS: none before (the film opens here); after, gd02_zuri (close on Zuri's note block on wool).
    MEASURED (the set builder, out/test/crammys_set_b01_everyone_zones.png, music b1 aimed 0.25 lower): Steve at x 61 %,
      y 54.5 % (face y 50-59 %); the four acts above him at y 42 % (Zuri 15, Kai 32, Noor with the horn 50, Sunny 74 %);
      their notes at 16 / 31 / 78 %. With music's own aim his chin was at 61 %, on the caption band: keep the lower aim.
      The north post carries no lantern yet (this stub: the lantern is placed in gd05).
      THE LEAD'S SCOUT OF THIS STUB (tools.crammys_geo gd01_everyone:40, render.py --still 0.1): the PEDESTAL STANDS
      RIGHT BEHIND STEVE'S HEAD: its gold block's top at x 54-71 %, y 47 % sits on his hair (head y 49-60 %), and the
      totem on it (C.totem) at x 62 %, y 43 % floats in the row of the four acts' faces (all at y 42 %). A tangent to
      solve here (Steve's spot or the camera; the pedestal and the totem are shared and stay). Steve's eyes x 62 %,
      y 55 %, face 107-111 px; Zuri 14, Kai 31, Noor 50, Sunny 75 % (faces 37-42 px, 3-14 degrees off the lens).
      Rendered (out/test/crammys_scout_gd01_everyone_60_zones.png): on frame 60 his head, turned "back to them" by
      look_at alone, shows the lens only his hair and the side of his face, tipped up (the head stops at 70 degrees of
      yaw and the four are BEHIND him): a glance over the shoulder needs the body (C.turn_to) or a smaller turn; the
      golden totem between Noor's and Sunny's faces and the gold block on his hair are plain at phone size.
    RISKS (story): "Wool is guitar and gold is bells cannot be seen": the block under each note block is big enough in
      gd02 / gd03; here it is the joke's set-up (nothing near Steve).
    """
    f0, f1 = s.frame_start, s.frame_end
    bd = C.bd
    steve = C.actor("steve", "gd")
    z, k, su, no = (C.actor(n, "gd") for n in ("zuri", "kai", "sunny", "noor"))
    C.put(steve, f0, "steve_front")
    for p, spot in ((z, "zuri"), (k, "kai"), (su, "sunny"), (no, "noor")):
        C.put(p, f0, spot)
    C.hold(no, "goat_horn", s)
    no.toot(f0 + 4, f1)
    bd.tap("zuri", z, f0 + 2, camera=s)                     # a note already rising on the first frames
    bd.tap("kai", k, f0 + 14, camera=s)
    bd.tap("sunny", su, f0 + 26, camera=s)
    bd.tap("zuri", z, f0 + 40, camera=s)
    bd.tap("kai", k, f0 + 52, camera=s)
    lens = (GD01_CAM["pos"][0], GD01_CAM["pos"][1], 1.7)
    steve.look_at(f0, lens, ease=0)
    turn = C.at(s, "musical") - 6
    steve.look_at(turn, C.eyes("kai"), ease=10)              # his head back to them ...
    steve.look_at(C.at(s, "except") - 2, lens, ease=10)        # ... and to the front
    C.totem(s)
    st.use(s, steve, z, k, su, no)
    st.hero(s, "steve", steve)
    C.cam(s, "set:b01", focus=steve.head)
    C.lights(s, "gold")


def gd02_zuri(st, s, C, nar):
    """BEAT 2  "Zuri keeps her note block on wool, so she plays guitar."   frames 86-178 (93 f, 3.88 s), sky gold.
    Words: Zuri 88, keeps 98, her 105, note 108, block 114, on 123, wool 127, so 143, she 147, plays 150, guitar 158.
    The voice ends on 172; the shot runs on 6 frames after it (0.25 s).

    STORY (beat 2): Close on a note block sitting on a white wool block, both large in frame. Zuri's arm taps it and a
    note pops with each tap, changing colour as the pitch goes up. Tilt up from the wool to Zuri's face, looking screen
    right. Steve crosses behind her, out of focus, watching.
    Cast: Zuri, Steve. Effects: note block on white wool, note particles changing colour with pitch, arm swing, tilt up.

    MUST BE SEEN, ON WHICH WORD
      frame 1 .. "wool"     the note block on its WHITE WOOL block, both big (the wool's face fills the lower third),
                            a note popping with each tap, one colour per tap (each right-click a semitone up)
      "plays guitar"        the tilt has reached Zuri's face (looking screen right); Steve soft, crossing behind her
    SHARED: none. Places: zuri; Steve's path C.v.paths["bandstand_steve_cross"] (behind her on the stage).
    NEIGHBOURS: before, gd01_everyone (the four acts from the corridor); after, gd03_kai (the mirror: Kai on gold).
    MEASURED (the set builder, crammys_set_b02_zuri*.png): first frame the note block on wool big, its note at
      x 52 %, y 19 %; ZURI'S HEAD IS CUT BY THE TOP EDGE on the first frames (palette_check's safe-area test fails
      there: the tilt has not reached her yet; accepted while the block is the hero); last frame her face x 37-65 %,
      y 40-54 %. The north post's two fences (no lantern yet) stand in front of her shoulder at x 10-30 %: her face is
      clear. The story asks for "tilt up": music b2 tilts AND rises (z 1.05 -> 1.9).
    """
    f0, f1 = s.frame_start, s.frame_end
    z = C.actor("zuri", "gd")
    C.put(z, f0, "zuri")
    every = 9
    C.bd.notes["zuri"].song(z, f0 + 2, count=max(1, (f1 - f0 - 6) // every), every=every, camera=s)
    steve = C.actor("steve", "gd")
    pts = C.v.paths["bandstand_steve_cross"]
    steve.place(f0, pts[0], 0.0)
    steve.walk(f0 + 8, pts, speed=1.6)
    steve.look_at(f0 + 8, z, ease=8)
    st.use(s, z, steve)
    st.hero(s, "zuri", z)
    C.cam(s, "set:b02", focus=(-7.5, 2.5, 1.0))
    s.focus(z.head, at_s=s.film.seconds(C.at(s, "plays") - 10))
    C.lights(s, "gold")


def gd03_kai(st, s, C, nar):
    """BEAT 3  "Kai keeps his on gold, so he plays bells."   frames 179-246 (68 f, 2.83 s), sky gold.
    Words: Kai 181, keeps 186, his 193, on 196, gold 201, so 214, he 218, plays 220, bells 228. The voice ends on 241;
    the shot runs on 5 frames after it (0.21 s).

    STORY (beat 3): The mirror of the last shot, from the other side: past Steve's soft shoulder in the foreground, a
    note block on a gold block with the low sun rimming the gold. Kai taps it, notes pop. Focus pulls from the gold
    block up to Kai's face, looking screen left, and holds on it so he is known later. He does not look at Steve.
    Cast: Kai, Steve. Effects: note block on gold block, note particles, arm swing, focus pull, sun rim on the gold.

    MUST BE SEEN, ON WHICH WORD
      frame 1 .. "gold"     the note block on its GOLD block in focus (the gold's sunlit front face), a note popping
      "plays bells"         the focus has pulled up to Kai's face (looking screen left) and HOLDS on it: he must be
                            known later (beats 7, 23). He does not look at Steve.
      the whole shot        Steve's soft shoulder in the foreground (right fifth), never his face
    SHARED: none. Places: kai, steve_kai.
    NEIGHBOURS: before, gd02_zuri; after, gd04_sunny (the static wide).
    FALLBACK CHOSEN (story risk, the set builder and engine/music measured it): the "low sun rimming the gold" is
      impossible on this set (the gold block is buried on every side but its front): the sunlit front face is the
      brightest gold in the frame. An optional warm kicker behind Kai (C.kicker("gd_rim", s, (-5.9, 2.6, 3.4), 60)) is
      offered by music, never rendered.
    MEASURED (crammys_set_b03_kai_zones.png): Kai's face x 54 %, y 30 %, looking screen left; the gold face 38, 59 %;
      Steve's shoulder soft at the right edge.
    """
    f0, f1 = s.frame_start, s.frame_end
    steve = C.actor("steve", "gd")
    k = C.actor("kai", "gd")
    C.put(steve, f0, "steve_kai")
    steve.look_at(f0, C.P("note_kai_target"), ease=0)
    C.put(k, f0, "kai")
    C.bd.notes["kai"].song(k, f0 + 4, count=max(1, (f1 - f0 - 8) // 12), every=12, camera=s)
    st.use(s, k, steve)
    st.hero(s, "kai", k)
    C.cam(s, "set:b03", focus=(-8.0, 1.5, 0.75))
    s.focus(k.head, at_s=s.film.seconds(C.at(s, "so") - 4))
    C.lights(s, "gold")


def gd04_sunny(st, s, C, nar):
    """BEAT 4  "Sunny keeps his on a pumpkin, and we don't talk about it."   frames 247-335 (89 f, 3.71 s), sky gold.
    Words: Sunny 249, keeps 259, his 266, on 272, a 275, pumpkin 277, and 298, we 301, don't 303, talk 307, about 316,
    it 323. The voice ends on 325; the shot runs on 10 frames after it (0.42 s).

    STORY (beat 4): Static wide of the stage. Sunny, alone at the far end, taps a note block that sits on a pumpkin: one
    single note rises. Zuri and Kai stop tapping, turn their heads to him together, hold a beat, then turn away again.
    Below the stage Steve looks at the ground.
    Cast: Sunny, Zuri, Kai, Steve. Effects: note block on pumpkin (plain, not carved), single note particle, two
    synchronised head turns.

    MUST BE SEEN, ON WHICH WORD
      frame 1          Zuri and Kai still tapping (a note in the air), Sunny alone at the far (south) end
      "pumpkin"        Sunny taps ONE note on the note block that sits on the PUMPKIN (the didgeridoo)
      "and we"         Zuri and Kai stop and turn their heads to him TOGETHER, hold a beat ...
      "talk about it"  ... and turn away again; below the stage Steve looks at the ground
    SHARED: none. Places: zuri, kai, sunny, steve_foot. The totem on the pedestal (C.totem): Steve stands beside it.
    NEIGHBOURS: before, gd03_kai; after, gd05_trophy (close on the totem, then the whole bandstand).
    MEASURED (crammys_set_b04_sunny_zones.png, music b4, 28 mm static wide): Zuri 14 %, Kai 31 %, Sunny 72 % (y 45 %);
      Sunny's note 77, 48 %; Steve below the stage looking at the ground at about 75 %, beside the pedestal. A wide:
      the faces are small; the synchronised turn is what must read.
    RISK (story): non-players may not know a pumpkin makes a didgeridoo: the line carries it; a sound is the fallback.
    """
    f0, f1 = s.frame_start, s.frame_end
    z, k, su = (C.actor(n, "gd") for n in ("zuri", "kai", "sunny"))
    for p, spot in ((z, "zuri"), (k, "kai"), (su, "sunny")):
        C.put(p, f0, spot)
    C.bd.tap("zuri", z, f0 + 1, camera=s)
    C.bd.tap("kai", k, f0 + 5, camera=s)
    one = C.at(s, "pumpkin")
    C.bd.tap("sunny", su, one, camera=s)
    sp = C.eyes("sunny")
    for p in (z, k):
        p.look_at(C.at(s, "and") - 2, sp, ease=6)
        p.look_at(C.at(s, "talk") + 4, C.P("note_%s_target" % p.name.split("_")[0]), ease=6)
    steve = C.actor("steve", "gd")
    C.put(steve, f0, "steve_foot")
    fp = C.P("steve_foot")
    steve.look_at(f0, (fp[0] - 0.6, fp[1] + 0.3, fp[2]), ease=0)
    C.totem(s)
    st.use(s, z, k, su, steve)
    st.hero(s, "sunny", su)
    C.cam(s, "set:b04", handheld=0.003)
    C.lights(s, "gold")


def gd05_trophy(st, s, C, nar):
    """BEAT 5  "Tonight was the Crammys, our biggest party of the year."   frames 336-424 (89 f, 3.71 s), sky gold.
    Words: Tonight 338, was 347, the 352, Crammys 354, our 376, biggest 380, party 391, of 403, the 406, year 407. The
    voice ends on 417; the shot runs on 7 frames after it (0.29 s).

    STORY (beat 5): Start close on the trophy: a totem of undying turning slowly as a dropped item above a gold block on
    a fence-post pedestal at the front of the stage. The camera rises and pulls back to the whole bandstand: coloured
    wool, the row of note blocks, a jukebox centre stage, lanterns on fence posts. Alex places the last lantern.
    Cast: Alex. Effects: totem of undying as a spinning dropped item, gold block on a fence-post pedestal, jukebox,
    lanterns on fence posts, lantern block being placed, rise and pull back.

    MUST BE SEEN, ON WHICH WORD
      frame 1 .. "Crammys"   the totem of undying turning above the gold block of the pedestal, filling the frame
      "biggest party"        the camera has risen and pulled back: the whole bandstand (wool, the row of note
                             blocks, the jukebox centre stage, lanterns on fence posts)
      about 0.9 of the shot  Alex PLACES THE LAST LANTERN on the north post (bd.last_lantern.place(f, player=alex):
                             THIS SEQUENCE ALONE, exactly once; the post is inside the frame only late in the move)
    SHARED: THE TOTEM (C.totem), THE LAST LANTERN. Places: alex_post, last_lantern_target.
    NEIGHBOURS: before, gd04_sunny; after, gd06_line (the dolly along the line of players).
    MEASURED (crammys_set_b05_trophy*.png, music b5): the totem 50, 43 % (x 22-80 %) on the first frame; at the end the
      whole bandstand, the placed lantern at 18 %, Alex at 27 %, the totem at 65, 50 %. The lead's scout of this stub
      (out/test/crammys_scout_gd05_trophy_340_zones.png): the totem face-on and sharp, x 44-72 %, y 44-61 % (its feet
      touch the caption band's top), the gold block below it filling the lower third; in the middle of the move (tile
      380) it is small: hold the first second on it.
    RISK (story): the totem is a flat item: here it is the dropped item, turning (seen face-on part of each turn):
      hold the first frames on it so it is known before Steve holds it in fn24.
    """
    f0, f1 = s.frame_start, s.frame_end
    cam = CC.CS.CAMERAS["b05"]
    t = C.totem(s)
    t.face(f0, cam["pos"])
    a = C.actor("alex", "gd")
    C.put(a, f0, "alex_post")
    fp = f0 + int(round(cam["place_at"] * (f1 - f0)))
    C.hold(a, "lantern", s, until=fp + 1)
    C.bd.last_lantern.place(fp, player=a)
    st.use(s, a)
    st.hero(s, "totem", t.sprite)
    C.cam(s, "set:b05", focus=t.sprite, handheld=0.004)
    C.lights(s, "gold")


def gd06_line(st, s, C, nar):
    """BEAT 6  "Everyone performs, and I never have anything."   frames 425-508 (84 f, 3.50 s), sky gold.
    Words: Everyone 427, performs 438, and 462, I 464, never 468, have 474, anything 480. The voice ends on 494; the
    shot runs on 14 frames after it (0.58 s).

    STORY (beat 6): The camera travels along a line of players beside the stage, a little above hand height. Each holds
    their act straight out toward the lens so flat items show their faces: Zuri a note block, Noor a goat horn, Alex a
    green music disc, Sunny his pumpkin. It stops on Steve at the end of the line, who looks down at his empty hand.
    Cast: Zuri, Noor, Alex, Sunny, Steve. Effects: held note block, held goat horn, held music disc (green, Cat), held
    pumpkin, arms raised to about horizontal so flat items face the lens, Steve's empty hand, sideways tracking move.

    MUST BE SEEN, ON WHICH WORD
      frame 1 .. "performs"  the dolly passes each act held out at the lens, faces of the items to the lens (C.present):
                             Zuri a note block, Noor the goat horn, Alex the green music disc (cat), Sunny his pumpkin
      "never have anything"  the dolly stops on Steve at the end of the line, his EMPTY hand held out low, his head
                             down at it (the head alone pitches at most 35 degrees: the hand is held out to be seen)
    SHARED: THE CAT DISC (Alex holds music_disc_cat). Places: line_1 .. line_5 (line_5 = Steve).
    NEIGHBOURS: before, gd05_trophy; after, rd07_chased: THE HARD CUT TO NIGHT. The last frames here are the last gold
      frames of the film (the lead compared them side by side with rd07's first: films/crammys.py SKIES).
    MEASURED (crammys_set_b06_line*.png, music b6): the acts held at x 28-34 %, each item 33-41 % of the frame wide;
      Zuri's held note block faces the lens (29, 39 %); the last frame ends on Steve holding out his empty hand and
      looking down at it. The lead's scout (crammys_scout_gd06_line_508_zones.png, the first stub with a LINEAR dolly):
      on the last frame Steve's face x 38-68 %, y 30-50 % (geo: eyes 63, 40 %, 154 px) but soft: the dolly was still
      at full speed (motion blur); the stub now eases out to a stop on him (ease_out) and pulls focus to him by
      "never": re-rendered, his face sharp at x 35-66 %, y 29-51 %, his empty hand held out, his eyes down on it
      (crammys_scout_gd06_line_508_zones.png; the side-by-side file keeps the first, soft version). Compared side by side with rd07's first frame (out/test/crammys_scout_cut_gd06_rd07.png): see SKIES.
    """
    f0, f1 = s.frame_start, s.frame_end
    cam = CC.CS.CAMERAS["b06"]
    acts = (("zuri", "note_block"), ("noor", "goat_horn"), ("alex", "music_disc_cat"), ("sunny", "pumpkin"))
    cast = []
    for i, (who, item) in enumerate(acts, 1):
        p = C.actor(who, "gd")
        C.put(p, f0, "line_%d" % i)
        C.hold(p, item, s)
        y = C.P("line_%d" % i)[1]
        C.present(p, s, (cam["pos"][0], y + 1.0, cam["pos"][2]))
        cast.append(p)
    steve = C.actor("steve", "gd")
    C.put(steve, f0, "line_5")
    sp = C.P("line_5")
    hand = (sp[0] - 0.75, sp[1] + 0.25, sp[2] + 1.05)        # his empty right hand, held out low before him
    C.present(steve, s, hand, f0=f0 + 6, ease=8)
    steve.look_at(f0, (cam["pos"][0], sp[1], 1.6), ease=0)
    steve.look_at(C.at(s, "never") - 4, hand, ease=8)          # ... and he looks down at it
    C.totem(s)                  # the pedestal is in frame behind the line (the technical review: x 75 %, y 27 % on
    #                             438; it stood empty here, one shot after gd05 opened on the totem turning on it)
    st.use(s, steve, *cast)
    st.hero(s, "steve", steve)
    # the dolly at speed on frame 1 and STOPPING on Steve (ease_out): at "linear" it was still moving at full speed
    # on the last frame and the motion blur softened his face (lead's scout, crammys_scout_gd06_line_508.png)
    C.cam(s, "set:b06", focus=cast[0].item(frame=f0), ease="ease_out", handheld=0.004)
    # rack the focus along the line, act by act, as the dolly passes each (8 frames before it is level with it)
    y0, y1 = cam["pos"][1], cam["pos1"][1]
    for i, p in enumerate(cast + [steve]):
        if i == 0:
            continue
        yi = C.P("line_%d" % (i + 1))[1] + 1.0
        e = min(1.0, max(0.0, (yi - y0) / (y1 - y0)))            # the eased fraction where the dolly is level ...
        u = 1.0 - (1.0 - e) ** 0.5                                # ... and the time fraction (inverse of ease_out)
        f = f0 + int(round(u * (f1 - f0)))
        if p is steve:                                            # his face sharp by "never" (he looks at his hand)
            f = min(f, C.at(s, "never"))
        s.focus(p.head if p is steve else p.item(frame=f0), at_s=s.film.seconds(max(f0 + 1, f - 8)))
    C.lights(s, "gold")
