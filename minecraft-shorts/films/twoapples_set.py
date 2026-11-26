"""THE SETS OF "TWO APPLES" (stories/underground.json, SHOTLISTS.md section 2): a film-local set module. It wraps
engine/underground.py (the whole set of this film, built for it) in the seed-1 village through
village.build_village(edit=...), exactly as engine/sets.py builds hello_set, and adds what the beats needed beyond it.
Nothing in engine/ is changed.

    from films import twoapples_set as TS
    v, ug = TS.build_set(scene)          # village.build_village(scene, seed=1, edit=TS.twoapples_set) + underground.finish
    D = TS.set_data(v, ug)               # anchors, yaws, paths, parts, cutaways, cameras, skies, lights (see below)
    st = Stage(scene, film, v, skies=TS.SKIES, sky=sky)     # copy TS.SKIES into films/twoapples.py (SKIES = ...)
    ug.register(st)                      # the lever in st.cast: st.use(s, ug.lever) where the end pier is seen
    TS.CAMERAS["b24"]                    # a suggested camera per beat (b01 .. b24): dict(pos, target, lens, fstop
                                         #   [, pos0 / target0 = where a move starts, or pos1 / target1 = where it
                                         #   ends], sky, what, see = cutaways it sees through); its still is
                                         #   out/test/twoapples_set_<beat>_<what>[_<tag>].png (+ _zones.png)
    TS.LIGHTS["hall"]                    # the torch levels / film-local lights each place was rendered with

    $BPY -m films.twoapples_set                  # the self-test (numbers, 20 s): the village's checks, every ug_* / ta_*
                                                 #   standing anchor on solid ground with the body free (cutaway and
                                                 #   doorway cells count as solid), every camera position outside every
                                                 #   block, every cutaway it does not see through and the piston door,
                                                 #   the door shut, the lever on its pier, the paths on the ground
    $BPY -m films.twoapples_set b02 b24          # the proof stills of these beats (one build per sky, one shot per beat,
                                                 #   540x960, 16 samples, 2 threads, zones, tools/palette_check; 90-150 s
                                                 #   per still on the shared machine: ONE OR TWO PER CALL under timeout)
    $BPY -m films.twoapples_set b24:main,open    # only some frames of a beat (tags: main, start, hand, hands, open,
                                                 #   grown, empty); --dry: stage only, print where each hero lands and
                                                 #   what hides it; --res 270x480 --samples 8 --no-palette: scouting
                                                 #   (--suffix _lo keeps them apart); --emit / --under / --no-fill:
                                                 #   the hall's light for experiments

WHAT THIS FILE CHANGES AGAINST engine/underground.py (all of it film-local; each one rendered and looked at)
    the hall's light  HALL_EMIT 0.45 (underground.EMIT is 1.0: the game's own brightness at Brightness 50 %) and its
                torches at UNDER 1.0 (the engine's recipe 0.7) with the hall's fill on: the bake alone (EMIT 1) drew the
                whole hall as an evenly lit grey box, torch pools and dark stretches did not read (out/test/
                twoapples_set_b16_aisle_A.png against _B.png, 270x480 scouting). Set through the BlockLight
                environment's own `emit` before the bake (U.env(b).emit), so every baked face of the set, the stair
                mouth's rim and the stairwell included, is drawn at 0.45 of the game's light; the point lights and
                bloom carry the torches. On the hall stills the faces (skin s 0.43-0.49), robes and Steve pass
                tools/palette_check; its stone check does not see the set's baked stone (material names it does not
                know: engine/underground's own proof counted them in a second pass, not done here).
    the skies   "dusk" and "under" exactly as the engine gives them; NO third sky: a "room" sky (dusk, ambient 0.3) was
                tested for the bedroom and changed nothing visible (the room is lit by house_a's lights).
    cameras     b02 (three-quarter from the child's right, 38 degrees off his facing), b04 / b05 (the bedroom), b20
                (the square from the east), b24 (the mirror of b02) are new; the others are U.CAMERAS (b03 without its
                stand-in spot, now the anchor ta_push_kid).
    anchors     ta_* (below): the stand-in spots the stills were staged on.
    paths       ta_round_well / ta_round_well_on (beat 20); ug_round_well is NOT used (from the engine's b20 camera
                neither child is ever in the safe area: they are behind the well or out of the frame for the whole
                run, measured on a dry run).
    film lights MOUTH_GLOW (beat 2), ROOM_COOL (4, 5), DOWN_FILL (7), DAD_SIDE_FILL (13, 19), each a U.bounce for one
                shot; torch boosts (Stage.lights extra=): MOUTH_KEY (2), CORNER_KEY (8), the dad torch (13, 17, 24).
    the village plants are cleared on the ground line of CAMERAS["b20"] (sets.clear_view, width 1.2).

THE SKIES (Blender azimuth: degrees counter-clockwise from east)
    dusk   dict(preset="dusk", az=187, el=5, bloom=1.3, grade="warm")     beats 1-6, 20: the square, the bedroom, the
           stairwell. The sun just under the western houses: the sky over the well is orange-pink at the horizon,
           indigo with the first stars above (b01, b20 look west into it); the square is lit by its lamps.
    under  dict(preset="dusk", az=187, el=5, key=0.0, ambient=0.0, bloom=1.3, grade="neutral", haze=0.0)
           beats 7-19, 21-24: no sun, no sky fill, no bounce lamps under the ground: the baked block light and the
           torches only. Nothing in the set depends on the sky.

WHERE EVERY BEAT IS FILMED (Blender blocks: +X east, +Y north, +Z up; the square's ground z 0, a dirt path 1/16 lower;
the hall's floor z F = -10)
    THE SQUARE (beats 1, 2, 3, 20), dusk. The well's stone is x -3..2, y -3..2 (a 1-high rim, a 2-high core, posts
      and roof); the bell on its south side, the bell lamps at (-4, -4) and (0, -4), the village lamp post at (7, -3).
      THE STAIR MOUTH: 2 wide (x 4..5), open over y -3..0 east of the well, its rim turned to grass (x 3..6, y -4..1),
      wall torches just under the rim (group ug_mouth). ug_lip (4.85, 1.42, 0) is its lip, facing south into it.
    DAD'S HOUSE (beats 4, 5), dusk: house_a (the engine's choice, kept: the roomiest vanilla house, two beds, the
      oak door, windows on three sides). Its bed wing x 15..19, y -13..-9 (floor z 1): dad's bed house_a_bed_2 dyed
      RED at (18..19, -10), pillow east, the white bed_1 south of it at y -12; the wall torch between the pillows
      (19, -11, 2) is the key; the window in the north wall right behind the red bed (17..18, -8, 2) and the gable
      pane over the bed wall (20, -11, 4) show the indigo dusk; the door (10, -8) is at the far west end of the
      house (the lens side in beat 5).
    THE STAIRWELL (beat 6), dusk: ten stone stairs x 4..5 from y 0 down to y -9, stone walls turning to deepslate,
      torches at y -2, -3, -6, -9; the landing y -10 (deepslate bricks).
    THE HALL (beats 7, 9-19, 22, 23), under: the aisle x -8..19, y -12..-11 (west of the stair foot x 5 it is unlit
      and falls off into the dark); the cells face north into it from y -14 (front row y -13: job block at F, window
      at F+1, iron bars at F+2): farmer x 7 (composter), fletcher x 9 (fletching table), cleric x 11 (brewing
      stand), the 2-wide pier x 12..13, DAD x 14 (lectern), the end pier x 15 with the LEVER on its north face
      (15, -12, F+1). The piston wall = dad's back wall (14, -15, F and F+1). Torches: over the farmer / fletcher
      (9, -11, F+1), the hanging lantern (10, -11, F+2), the dad torch (14, -11, F+1), the stair foot (5, -10, F+1).
    THE BACK CORNER AND THE BOX (beats 8, 21, 24), under: the leg x 16..19, y -17..-13 with its one torch (19, -14,
      F+1); the zombie box (14, -16), 1 x 1 x 2 inside, its only opening the slot of iron bars at floor level in its
      east wall (15, -16, F); the open piston wall joins it to dad's cell.

ANCHORS (D["anchors"][name] = (x, y, z), D["yaws"][name]; engine.underground's ug_* are listed in its docstring)
    ta_push_kid      (7.00, 1.40, -0.06)    yaw -1.86   beat 3: the child watching the push from the east (his head
                                                        soft in the frame's bottom right corner)
    ta_kid_bed_foot  (18.50, -9.50, 1.56)   yaw 4.71    beat 4: on the red bed's foot, facing west (the lens)
    ta_kid_bed_door  (18.50, -9.50, 1.56)   yaw -1.82   beat 5: the same spot, facing the door (three-quarter to b05)
    ta_zombie_out    (2.40, -11.00, -10.00) yaw 2.08    beat 22: the zombie stepping out of the dark west aisle
    ta_kill_steve    (5.00, -10.30, -10.00) yaw -0.87   beat 23: Steve at the stair foot ...
    ta_kill_zombie   (3.65, -11.45, -10.00) yaw 2.28    ... the zombie 1.4 blocks from him (one swing)
    ta_box_baby      (14.50, -15.50, -10.00) yaw 2.79   beat 24: the baby in the box turned 20 degrees from the door
                                                        (north) toward the lens (east): the mirror of the child at
                                                        the lip, who is turned 38 degrees from b02's lens
    the engine's, used as they are: ug_lip (beat 2), ug_push_start / ug_push_player (3), ug_cell_farmer / _fletcher /
    _cleric / _dad (7, 9-17), ug_cell_dad_mid (18, 19), ug_lever_stand (9), ug_aisle_dad (14, 17), ug_counter_steve
    (13), ug_jump_spot (16), ug_follow_start -> ug_follow_end (18), ug_stair_foot (22), ug_box (the box's floor),
    U.STEVE_PAST (8, 21: his walk past the slot), ug_door_target / ug_lever_target / ug_lip_target (look targets).
  PATHS: ta_round_well (4.0, 4.6) -> (-4.7, 4.6) -> (-4.7, -4.6) -> (1.5, -4.6): the first child round the well's far
         (north and west) side; ta_round_well_on = the same, then on to (7.5, -4.9): the second child past the
         glowing mouth's south side toward the lens; ug_down (the stairs, with the steps' heights), ug_push, ug_aisle,
         ug_leg (the engine's).

THE PARTS (D["parts"])
    piston_door  ug.door: two stone blocks (14, -15, F / F+1) on sticky pistons west of them. ug.open_wall(f, player=,
                 repeater=4, sync="hand") (beat 9: the wall moves 12 frames after the click), ug.close_wall(f) (beat
                 15, on its last word), ug.door.open(f) / close(f) / is_open(f). It stays OPEN from beat 9 to beat 15
                 (beats 10, 11, 12 see the black doorway beside dad's robe) and SHUT again for 16-21; beat 24 opens it
                 from the box (open_wall(..., relight=(st, s))). Keyed in frame order: a shot that needs it open or
                 shut checks is_open first (this file's _opened / _shut): opening an open door raises RedstoneError.
    lever        ug.lever (15, -12, F+1): registered by ug.register(st); st.use(s, ug.lever) in every shot that sees the
                 end pier's north face, NOT in b13 / b16 / b19 (they see through the pier: it would float).
    doorway      ug.doorway {"dark", "lit"}: the doorway's and the box's faces, black in every shot (the open doorway
                 reads black from the aisle) except the one that calls ug.light_doorway (beat 24).
    house_door   v.doors["house_a"]: the closed oak door of beat 5 (never opened in this film).
    red_bed      v.beds["house_a_bed_2"] (foot (18.5, -9.5, 1.56), head (19.5, -9.5, 1.56), yaw east).
  CUTAWAYS (Stage.see_through): ug_ceiling + ug_caps (b07), ug_end_pier (b13, b16, b19), ug_end_wall (b13, b19, b24),
    ug_box_side + ug_slot (b24); house_a_roof / _east / _south exist but no camera here needs them. NEVER open the
    film on a see-through shot (Stage.see_through keys the cutaway visible on the film's first frame); the scouting
    film has a one-frame lead-in for this.

THE SUGGESTED CAMERAS (CAMERAS; each rendered at 540x960 / 16 samples with --zones under its sky, stand-ins staged as
the beat says, and looked at; the numbers are where the hero lands in the frame, x / y % from the top-left)
    b01 mouth   dusk. U.CAMERAS["b01_mouth"], 28 mm f/3.2: child's eye height east of the mouth, s.move(pos0, steve.head,
                pos, target) (the aim rides on his head, then eases onto the hole while the camera pushes in). Steve
                placed at (5, 6.5, 0), walk([(5, 6.5, 0)] + v.paths["ug_down"][1:10], players.WALK_SPEED). STILL (Steve
                at the lip, frame 36 of the shot): his head x 67 / y 35 in profile, the well and the sunset behind, the
                hole with its torch low left (x 25 / y 63: in the caption band on that frame; the push-in ends on it).
    b02 lip     dusk. NEW: pos (3.37, -0.47, 0.85), target (4.85, 1.42, 0.55), 50 mm f/2.0: from the child's RIGHT
                (south-west, over the rim beside the hole), 38 degrees off his facing; the child at ug_lip, look_at(
                U.cheat(A["ug_lip_target"], A["ug_lip"], pos, 0.35), ease=0): three-quarter front, staring down, cheated
                toward the lens. LIGHTS["lip"]: the warm glow from below lights his face (MOUTH_GLOW 240 W); the square
                soft behind. Head x 50 / y 44, about half the frame wide. THE FRAMING b24 MIRRORS. (The engine's b02_lip
                was 22 degrees off, nearly frontal, looking into the lens, on his left side: the opposite screen
                direction to anything the box allows.)
    b03 push    dusk. U.CAMERAS["b03_push"], 28 mm f/3.2, side-on and low from the east, the well behind. r = U.push(
                steve, dad, f, v.paths["ug_push"] + [(5.0, -2.0, 0.0)], v.world); dad.look_at(f, (9.0, 0.4, 1.4),
                ease=0) held; the child at ta_push_kid, look_at(dad). STILL (10 frames before dad drops a step): dad
                x 46 / y 38 (book hat, face to the lens), Steve x 72 / y 39 at his back, the child's head a soft brown
                block in the bottom right corner (x 88 / y 67).
    b04 bed     dusk. NEW: pos (16.0, -9.6, 2.15), target (19.6, -9.5, 2.45), 22 mm f/2.6: low beyond the
                red bed's foot, looking along it to the pillow; the child at ta_kid_bed_foot (facing the lens),
                U.bed_bounce(kid, f, A["ta_kid_bed_foot"], jumps=6), look_at the lens. LIGHTS["room"]. STILL (the top of
                his first jump, takeoffs[0] + 6): head x 49 / y 24, the bed (red blanket, the empty pillow at its far
                end) fills the bottom third, the wall torch between the pillows right of him, the gable pane with the
                indigo dusk top right (x 74 / y 24). Skin s 0.50, stone G/R 0.93. (The engine's b04_bed, 0.2 above the
                mattress tilted up: a wall of cobblestone, the bed a red block at the bottom edge, no pillow.)
    b05 still   dusk. NEW: pos (11.7, -12.6, 2.4), target (18.6, -9.6, 2.0), 26 mm f/3.2, LOCKED OFF from the west wing's
                south-west corner (the door (10, -8) is behind the lens's left: "the closed door on the lens side"); the
                child at ta_kid_bed_door (on the red bed's foot, body and look on the door): three-quarter to the lens
                (38 degrees), very small (head x 48 / y 48), the bed-wall torch beside him, the north window and the
                gable pane indigo. Stone G/R 0.94.
    b06 stairs  dusk. U.CAMERAS["b06_stairwell"], 26 mm f/4, high behind at the top of the flight: the child placed at
                ug_down[1], walk(ug_down[1:], speed 4.4, run=True), track the west wall's torch (step 2, ease 4).
                STILL (passing that torch): tiny (head x 50 / y 48), his head turned to the torch; stone walls, four
                torches, the deepslate landing at the bottom. Skin s 0.48.
    b07 down    under. U.CAMERAS["b07_down"], 26 mm f/4, see ug_ceiling + ug_caps: from over the farmer's pocket
                (pos0 (7.8, -11.3, -2.6), the frame's up is south) sliding east and down to over dad's (pos (14.5,
                -11.8, -4.3)); farmer, fletcher, cleric look up(ug_aisle_<n>, 1.4), dad looks up at the lens.
                STILLS: start (the straw hat and the fletcher's cap over composter and fletching table), end (dad's
                face up at us x 54 / y 50, the box's smooth stone lid behind his pocket, the lever x 35 / y 74).
                DOWN_FILL (120 W) lifts the pockets (the "start" still was rendered before it was added: darker);
                it still reads partly as a cutaway model (see NOT VERIFIED).
    b08 slot    under. U.CAMERAS["b08_slot"], 35 mm f/2.0 ON THE FLOOR against the corner's east wall, square on to the
                slot 3.75 away, focus on its "boot" point; Steve walks U.STEVE_PAST (2.15 from the lens, frame left to
                right); the baby zombie villager U.hands_in_slot(zv, f) + U.shade_face(v, zv). STILLS: the boots
                (the legs-together frame nearest his crossing: his leg on the left, the slot soft behind, x 51 / y 51)
                and "hands" (16 frames
                later: the dark slot, the green head a shape, the hands a few green pixels in the bars' gaps; the
                corner torch x 1.8 (CORNER_KEY) on them). Lights: no fill. Trousers 22 ok.
    b09 lever   under. U.CAMERAS["b09_lever"], 32 mm f/2.0, U.hold_then_move as the engine's BEATS: STILLS "hand" (his
                arm in from the left on the lever, lever x 39 / y 45) and the end (the wall open: dad x 72 / y 32, the
                black doorway beside his robe x 63 / y 48). r = ug.open_wall(f + 10, player=steve, repeater=4,
                sync="hand"); the wall STAYS OPEN until beat 15.
    b10 hit     under. U.CAMERAS["b10_cell_side"], 28 mm f/2.8, low and east of the axis, the lectern in the bottom
                third: dad x 61 / y 36, the black doorway beside him x 44 / y 53 (wall open). U.hurt_in_cell(dad, f,
                attacker=A["ug_door_target"]); still just before the blow.
    b11 portr.  under. U.CAMERAS["b11_portrait"], 40 mm f/2.0: big nose, brow, book hat, dad x 48 / y 42, the black
                doorway behind his head on the left. The second blow 12+ frames after the first.
    b12 turn    under. U.CAMERAS["b12_cell"], 26 mm f/3.2, frontal and symmetric on the whole cell: zombie dad (after
                U.infect_in_cell + zv.aggro(f, ease=0)) arms out over the lectern, face x 58 / y 33; dead ahead he
                hides the doorway (a strip shows at his left).
    b13 potion  under. U.CAMERAS["b13_counter"], 20 mm f/2.8, see ug_end_pier + ug_end_wall (lever NOT used): side-on
                along the counter from the east, zombie dad left (x 28 / y 44) behind the lectern, Steve right (x 76 /
                y 45) at ug_counter_steve; undead.throw_potion(steve, zv, f, camera=s): the splash in the air between
                them on the still (impact - 3). Lights: the dad torch x 1.8, U.COUNTER_BOUNCE at COUNTER_WATTS 70 (35 W
                clips Steve's trousers at HALL_EMIT 0.45), DAD_SIDE_FILL 10 W inside dad's cell. Trousers 16, shirt ok.
    b14 apple   under. U.CAMERAS["b14_apple"] with target = steve.item_point("right", f) (= U.APPLE_POINT at
                ug_aisle_dad, raise_arm 55), 50 mm f/1.8: the apple x 50 / y 50, the brightest thing in the frame; the
                green face soft at the top right edge (a little higher aim shows more of it, the apple then sinks
                toward the caption band).
    b15 drift   under. U.CAMERAS["b15_drift"], 32 mm f/2.4, pos0 -> pos past his shoulder, focus (14.6, -15.0, F+1):
                the wall open, the black doorway x 60 / y 50, zombie dad's face top right (x 81 / y 24), the first
                yellow swirls. ug.close_wall(f) on the last word ("two").
    b16 aisle   under. U.CAMERAS["b16_aisle"], 20 mm f/4, see ug_end_pier (lever NOT used): wide down the aisle, zombie
                dad shaking in his window on the left (x 16 / y 44, yellow swirls, undead.shake 3.0), the cleric,
                fletcher and farmer in theirs, Steve at the top of a jump at ug_jump_spot (x 74 / y 31,
                U.jump_loop), the lantern right of him, the aisle falling off into the dark. Steve's trousers 36: ok.
    b17 trade   under. U.CAMERAS["b17_ots"], 35 mm f/2.8, over Steve's shoulder at ug_aisle_dad: the emerald
                (raise_arm 55) big and low (x 49 / y 80, below the caption band), dad x 50 / y 45 behind it holding out
                the enchanted book (fx.hold_out(dad, "enchanted_book", f, f_end, enchanted=True): give it its END
                frame, or the book stays visible in every later shot), purple Nausea swirls; the dad torch x 1.6.
                palette: "robe hue" fails on the few near-black robe pixels left between the book and the emerald
                (rgb 24, 16, 19: hue undefined at that level); the face s 0.47.
    b18 follow  under. U.CAMERAS["b18_portrait"], 50 mm f/2.0: dad at ug_cell_dad_mid, dad.look_at(f, steve,
                ease=0) then dad.track(f, f1, steve, step=2, ease=4) while Steve walks ug_follow_start ->
                ug_follow_end under the lens: his face turns into profile to the stop (x 35 / y 47 on the still near
                the end). The book is behind the lens by then (see NOT VERIFIED).
    b19 behind  under. U.CAMERAS["b19_endwall"], 32 mm f/2.4, see ug_end_wall + ug_end_pier (lever NOT used): dad at
                ug_cell_dad_mid gazing up the aisle (look (13.4, -10.3, F+1.6)) in profile (start: x 44 / y 48), the
                slide pos0 -> pos ends on the piston wall's stone behind his back (end: SEAM x 50 / y 50, dad at the
                right edge). DAD_SIDE_FILL 10 W in the cell. palette: "robe hue" fails on his shaded east side
                (near-black, as b17); the face s 0.43.
    b20 grow    dusk. NEW: pos (11.5, -0.4, 1.9), target (-0.5, 0.3, 0.5), 22 mm f/4: the square from the east,
                over the glowing mouth (foreground, x 34-38 / y 58-64) to the well and the sunset behind it. Two
                children on ta_round_well / ta_round_well_on (4.4 blocks/s, the second 4 frames later): west along the
                well's north side (frame right), behind its west side (hidden: 1-block rim, 2-block core), out at its
                south-west corner and east along its south side (frame left), the second on past the mouth toward the
                lens. r = U.swap_hidden(k1, adult, pos, f0, f1, v.world, then=path[2:], speed=ADULT_SPEED): the swap
                lands in the middle of the hidden run. STILLS: both children on the north side (1.8 s into the run),
                the grown-up out at the south-west corner and the second child running (4.9 s). From the engine's
                b20_well camera with ug_round_well neither child is ever in the safe area (measured).
    b21 slot    under. CAMERAS["b08"] again, focus on U.SLOT_FACE, the slow push in (pos -> pos1); no hands, black
                inside; Steve's legs pass (the slot ends at his waist). Slot x 51 / y 51; trousers 15 ok.
    b22 foot    under. U.CAMERAS["b22_foot"], 24 mm f/2.8: the child at ug_stair_foot, look_at the lens: three-quarter
                (x 72 / y 54); the zombie at ta_zombie_out, aggro (arms raised), lit against the black of the unlit
                west aisle (x 22 / y 42). Lights: no fill (LIGHTS["box"]): the foot torch is his rim.
    b23 kill    under. U.CAMERAS["b23_kill"], 24 mm f/2.8: Steve at ta_kill_steve with the iron sword (x 73 / y 39),
                the zombie at ta_kill_zombie: steve.attack(f), undead.die(z, f, camera=s, attacker=steve) - red,
                knocked back, tipping over by the steps on the still (f + 12).
    b24 box     under. NEW, THE MIRROR OF b02: pos (16.9, -14.6, F+0.85), target (14.5, -15.5, F+0.6), 50 mm f/2.0
                (b02's lens, b02's distance 2.4, b02's eye height), pan to pos1 (16.9, -14.5, F+0.95) / target1
                (14.35, -13.6, F+1.3) (dad's back and book hat beyond the doorway); see ug_box_side + ug_slot +
                ug_end_wall. The baby zombie villager at ta_box_baby (body 20 degrees from the door toward the lens),
                look_at(U.cheat(BOX_LOOK, eyes, pos, 0.5), ease=0): head x 50 / y 46, three-quarter, looking down
                and to frame right exactly as the child in b02 (head x 50 / y 44); lit only from below by U.SLOT_STRIP.
                r = ug.open_wall(f_open, relight=(st, s)) + U.DOORWAY_GLOW from r["open"]: STILL "open": the warm light
                across his face. The run and the pan: the engine's recipe (zv.look_at(run - 3, ...), zv.walk(run,
                [A["ug_box"], (14.6, -14.9, F)]), U.hold_then_move(s, run, pos, target, pos1, target1, frame_end=run +
                16)); the pan was NOT rendered from this camera (see NOT VERIFIED).

LIGHT (LIGHTS[...], as the stills were rendered; Stage.lights keywords + the film-local lights named there)
    square  scale 1.3 (the village's lamps at the look-dev dusk level), every ug_* group 1.0, near ug_mouth_target,
            radius 22 (beats 1, 20; beat 3: scale 1.0, near ug_lip, radius 20). The lamp post (7, -3) and the bell
            lamps are on; the mouth glows from its two torches and the bake.
    lip     beat 2: scale 1.0, ug_* 1.0, near ug_lip, radius 18, extra MOUTH_KEY (the two ug_mouth torches x 2.2), and
            MOUTH_GLOW: U.bounce(st, s, MOUTH_GLOW, energy=MOUTH_GLOW_WATTS (240), color=U.POINT_COLOR, kind="torch")
            low over the hole: his face is lit warm from below (the torches alone, under the ground, did not reach
            it: +2 % on the face). Skin s 0.43, stone G/R 0.93.
    room    beats 4, 5: scale 1.2, groups {"house_a": 1.5} (the torch between the pillows is the key), near
            house_a_center, radius 14, house_a's own fill OFF (inside=()): with it the room is the flat, evenly lit box
            of the engine's proof stills; plus ROOM_COOL: U.bounce(st, s, ROOM_COOL, energy=45, color=(0.90, 0.95,
            1.0), kind="fill") (torch light alone pushed the child's skin to s 0.53 against the palette's 0.52).
            The window and the gable pane show the dusk sky; no other sky needed ("room" with ambient 0.3: no change).
    stairs  beat 6: scale 0 (no village light), every ug_* group 1.0.
    hall    beats 7, 9-19 (and 22-23 without the fill): scale 0, every ug_* group UNDER 1.0, inside="ug_hall" (the
            hall's cool shadowless fill), st.use(s, ug.lever) where the pier is seen. With HALL_EMIT 0.45 the
            torches and the lantern make pools on the stone and the stretches between them, the aisle's west end and
            the back corner go dark; faces stay readable (skin s 0.46-0.49). Film-local extras: b07 DOWN_FILL
            (U.bounce 120 W, fill, over the open pockets); b13 the dad torch x 1.8 (extra=[((14.5, -10.6, F + 1.9),
            1.8)]), U.COUNTER_BOUNCE at 70 W, DAD_SIDE_FILL 10 W (torch) in the cell's east corner; b17 the dad torch
            x 1.6; b19 DAD_SIDE_FILL.
    box     beats 8, 21, 22, 23, 24: the same WITHOUT the fill (it passes walls and would light the box; in b22 / b23
            the dark west aisle stays black). Beat 24: U.bounce(st, s, U.SLOT_STRIP, energy=6, color=POINT_COLOR,
            kind="torch") the whole shot (his only light while the wall is shut), U.DOORWAY_GLOW 60 W (torch) from
            r["open"], the dad torch x 2.5, ug.light_doorway via open_wall(relight=(st, s)).
  Palette (tools/palette_check, every still): all checks pass except b17 and b19 "robe hue" (near-black robe
            pixels, rgb about (24, 16, 19), where no torch reaches: hue is undefined there).
            Every face check passes (skin s 0.43-0.50), every
            stone check on the square and in the house (G/R 0.92-0.94; the hall's baked stone is not seen by the
            check), Steve's trousers (min channel 15-42) and shirt everywhere.

NOT VERIFIED / LEFT TO THE DIRECTORS
    - NO ANIMATION WAS RENDERED: stills only (one or two frames per beat). The push, the bed bounce, the runs, the
      jump loop, the lever's hold-then-pan, the drift, the slide in b19, the swap behind the well and the box's pan
      are the engine's numbers or this file's staging, not watched in motion. Nothing went through render.py.
    - b24's pan to dad's back (pos -> pos1 after his first step) was not rendered from this camera (the engine's
      proof of the pan used its own 35 mm camera 90 degrees off his facing). The hold and the open wall were.
    - b18: the book's glint in the distance and dad's face are still not in one frame (Steve walks under the lens).
    - b08: the walking legs smear with motion blur; the still is the legs-together frame near the crossing. The two
      hands are a few green pixels in the dark slot (the corner torch x 1.8 on them); the head a dark green shape.
    - b07: the steep look down still reads partly as a cutaway model (the risk the story names). Its fallback (the
      counter ride from a child's eye height) was NOT built: by the layout (worked out, not rendered) the front
      row's solid pier at x 6 hides the farmer's window from a low camera at the counter west of x 6.5 looking
      along the row; such a ride must start east of it. A 45-degree look along the row from above the aisle was
      tried and dropped (scouting, 270x480): the front row's top bars stand between the lens and every face.
    - b20: the children are small (about 40 px tall at 540x960) in a wide that shows the whole circuit; both are in
      the safe area together for only 9 frames before the well hides the first (1.6-2.0 s into the run; the swap
      3.0 s in, U.swap_hidden), the grown-up and the second child together for 8 frames (4.6-4.9 s). ADULT_SPEED
      2.4 is a film choice (the grown-up walks out briskly; the director slows him). A longer lens panning with
      them would make them bigger; not tried.
    - HALL_EMIT 0.45 is a look choice, not the game (the game draws the hall at EMIT 1.0); not compared with the game.
      It changes every baked face of the set (the stairwell and the mouth's rim too); the square's dusk stills and
      the stairwell were re-rendered with it and pass the palette.
    - jump_loop's 0.05 clip into the aisle's ceiling at the top of each jump (engine note) was not looked for.
    - Characters in the stills are stand-ins: single poses at a single frame (the directors' keys may differ).
"""
import math
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from engine import underground as U       # noqa: E402
from engine import village                # noqa: E402

FPS = 24
F = U.F                                   # the hall's floor (walking surface z -10)

# ------------------------------------------------------------------------------------------------------------------
# the skies the set was scouted under (copy into films/twoapples.py; Blender azimuth: degrees ccw from east)
# ------------------------------------------------------------------------------------------------------------------
SKIES = {
    "dusk": dict(preset="dusk", az=187.0, el=5.0, bloom=1.3, grade="warm"),
    "under": dict(preset="dusk", az=187.0, el=5.0, key=0.0, ambient=0.0, bloom=1.3, grade="neutral", haze=0.0),
}


# ------------------------------------------------------------------------------------------------------------------
# the hook and the build
# ------------------------------------------------------------------------------------------------------------------
def twoapples_set(b):
    """THE HOOK (village.build_village(edit=...)): engine.underground's whole set (stair mouth, stairwell, hall,
    cells, piston wall, zombie box, dad's red bed house_a_bed_2, the baked block light), then this film's own
    additions. Returns Village.sets["twoapples"]."""
    e = U.env(b)
    e.emit = HALL_EMIT
    res = U.underground_set(b, name="underground")
    # beat 20: the chase round the far side of the well (seen from CAMERAS["b20"]) and the second child's run on,
    # past the glowing mouth on its west rim, toward the camera
    b.path("ta_round_well", ROUND_WELL)
    b.path("ta_round_well_on", ROUND_WELL + ROUND_WELL_ON)
    from engine import sets
    sets.clear_view(b, CAMERAS["b20"]["pos"], (-0.5, -0.6), width=1.2)
    anchors = _anchors(b)
    out = dict(underground=res, emit=HALL_EMIT, anchors=anchors, paths=["ta_round_well", "ta_round_well_on"])
    b.v.sets["twoapples"] = out
    return out


def _anchors(b):
    """This film's own standing spots (ta_*), registered on the Village beside engine.underground's ug_* ones.
    Returns {name: (x, y, z)}; the yaws are in Village.yaws."""
    v = b.v
    A = v.anchors
    out = {}

    def put(name, pos, yaw):
        out[name] = b.anchor(name, pos, yaw)

    foot = v.beds[U.BED]["foot"]
    put("ta_push_kid", PUSH_KID, village.yaw_to(PUSH_KID, (A["ug_push_start"][0], 2.0)))          # beat 3
    put("ta_kid_bed_foot", foot, v.beds[U.BED]["yaw"] + math.pi)                                  # beat 4
    put("ta_kid_bed_door", foot, village.yaw_to(foot, DOOR_IN))                                   # beat 5
    zpos = (A["ug_stair_foot"][0] - 2.6, A["ug_aisle_west_end"][1], float(F))
    put("ta_zombie_out", zpos, village.yaw_to(zpos, A["ug_stair_foot"]))                         # beat 22
    foot_ = A["ug_stair_foot"]
    spot = (foot_[0], foot_[1] - 0.75, float(F))
    zk = (foot_[0] - 1.35, -11.45, float(F))
    put("ta_kill_steve", spot, village.yaw_to(spot, zk))                                          # beat 23
    put("ta_kill_zombie", zk, village.yaw_to(zk, spot))
    put("ta_box_baby", A["ug_box"], BOX_YAW)                                                      # beat 24
    return out


PUSH_KID = (7.0, 1.4)       # beat 3: the child watching the push from the east, the soft head at the frame's right
DOOR_IN = (10.5, -7.5, 2.2)                # house_a's door (west front) at a child's look height
DEBUG = False               # scouting: --debug prints beat 20's children frame by frame
HALL_EMIT = 0.45            # the baked block light drawn at this share of the game's brightness (underground.EMIT)
# beat 20 (seen from the east, CAMERAS["b20"]): from the north-east corner of the plaza west along the well's north
# side, behind its west side (hidden), out at its south-west corner and east along its south side
ROUND_WELL = [(4.0, 4.6), (-4.7, 4.6), (-4.7, -4.6), (1.5, -4.6)]
ADULT_SPEED = 2.4             # the grown-up after the swap (blocks / s): out from behind the well within a second
ROUND_WELL_ON = [(7.5, -4.9)]       # ... the second child on, past the glowing mouth (south of it), toward the lens


def build_set(scene):
    """The village of "Two Apples": seed 1 with twoapples_set in its hook, then underground.finish(v).
    Returns (Village, UndergroundSet)."""
    v = village.build_village(scene, seed=1, edit=twoapples_set)
    ug = U.finish(v)
    return v, ug


# ------------------------------------------------------------------------------------------------------------------
# A SUGGESTED CAMERA FOR EVERY BEAT: dict(pos, target, lens, fstop[, pos0 / target0: where a move starts, or pos1 /
# target1: where it ends], sky, what, see = cutaways the camera sees through)
# ------------------------------------------------------------------------------------------------------------------
_C = U.CAMERAS
CAMERAS = {
    "b01": dict(_C["b01_mouth"], sky="dusk", what="mouth"),
    "b02": dict(pos=(3.37, -0.47, 0.85), target=(4.85, 1.42, 0.55), lens=50.0, fstop=2.0, sky="dusk", what="lip"),
    "b03": dict({k: v for k, v in _C["b03_push"].items() if k != "kid"}, sky="dusk", what="push"),
    "b04": dict(pos=(16.0, -9.6, 2.15), target=(19.6, -9.5, 2.45), lens=22.0, fstop=2.6, sky="dusk", what="bed"),
    "b05": dict(pos=(11.7, -12.6, 2.4), target=(18.6, -9.6, 2.0), lens=26.0, fstop=3.2, sky="dusk", what="still"),
    "b06": dict(_C["b06_stairwell"], sky="dusk", what="stairwell"),
    "b07": dict(_C["b07_down"], sky="under", what="down", see=("ug_ceiling", "ug_caps")),
    "b08": dict(_C["b08_slot"], sky="under", what="slot_boots"),
    "b09": dict(_C["b09_lever"], sky="under", what="lever"),
    "b10": dict(_C["b10_cell_side"], sky="under", what="hit"),
    "b11": dict(_C["b11_portrait"], sky="under", what="portrait"),
    "b12": dict(_C["b12_cell"], sky="under", what="turn"),
    "b13": dict(_C["b13_counter"], sky="under", what="potion", see=("ug_end_pier", "ug_end_wall")),
    "b14": dict(_C["b14_apple"], sky="under", what="apple"),
    "b15": dict(_C["b15_drift"], sky="under", what="drift"),
    "b16": dict(_C["b16_aisle"], sky="under", what="aisle", see=("ug_end_pier",)),
    "b17": dict(_C["b17_ots"], sky="under", what="trade"),
    "b18": dict(_C["b18_portrait"], sky="under", what="follow"),
    "b19": dict(_C["b19_endwall"], sky="under", what="behind", see=("ug_end_wall", "ug_end_pier")),
    "b20": dict(pos=(11.5, -0.4, 1.9), target=(-0.5, 0.3, 0.5), lens=22.0, fstop=4.0, sky="dusk", what="grow"),
    "b21": dict(_C["b08_slot"], sky="under", what="slot"),
    "b22": dict(_C["b22_foot"], sky="under", what="foot"),
    "b23": dict(_C["b23_kill"], sky="under", what="kill"),
    "b24": dict(pos=(16.9, -14.6, F + 0.85), target=(14.5, -15.5, F + 0.6), lens=50.0, fstop=2.0,
                pos1=(16.9, -14.5, F + 0.95), target1=(14.35, -13.6, F + 1.3), sky="under", what="box",
                see=("ug_box_side", "ug_end_wall", "ug_slot")),
}
for _k, _c in CAMERAS.items():
    _c.pop("note", None)
    _c.pop("beat", None)
    _c.pop("still", None)
del _k, _c

# beat 2: the stairwell's two top torches (group ug_mouth) as the child's key from below
MOUTH_KEY = [((4.29, -1.5, -0.11), 2.2), ((5.71, -2.5, -1.11), 2.2)]
MOUTH_GLOW = (4.75, -0.9, 0.2)        # a film-local warm light low over the hole: the glow from below on his face
MOUTH_GLOW_WATTS = 240.0

# torch levels below the ground: the engine's measured level (0.7 keeps torch-lit stone near the game's brightness)
UNDER = 1.0



# ------------------------------------------------------------------------------------------------------------------
# scouting: one build per sky and call, one shot per beat
# ------------------------------------------------------------------------------------------------------------------
TEST_DIR = os.path.join(ROOT, "out", "test")


class Scout:
    """One scene: the set, a Stage with SKIES (sky = the active one), a Film with a one-frame lead-in (Stage.see_through
    keys a cutaway visible on the film's first frame), the lever registered. For stills only."""

    def __init__(self, sky="dusk", res=(540, 960), samples=16, threads=2):
        import bpy

        from engine import look, shots
        from films import lookdev as L
        self.bpy = bpy
        bpy.ops.wm.read_factory_settings(use_empty=True)
        self.scene = bpy.context.scene
        look.setup_render(self.scene, res=res, samples=samples, threads=threads)
        t = time.time()
        self.v, self.ug = build_set(self.scene)
        self.A = self.v.anchors
        self.film = shots.Film(self.scene, fps=FPS)
        self.st = L.Stage(self.scene, self.film, self.v, skies=SKIES, sky=sky)
        self.ug.register(self.st)
        self.st.shot("_lead", 1.0 / FPS, sky=sky)
        self.sky = sky
        self.memo = {}
        print("[twoapples_set] built in %.1f s (sky %s)" % (time.time() - t, sky), flush=True)

    def render(self, frame, name, zones=True):
        """Render `frame` to out/test/<name>.png (+ _zones.png). Returns the path."""
        from PIL import Image

        from engine import post
        os.makedirs(TEST_DIR, exist_ok=True)
        path = os.path.join(TEST_DIR, name + ".png")
        self.film.goto(frame)
        self.scene.render.filepath = path[:-4] + "_part"
        self.scene.render.use_file_extension = True
        t = time.time()
        self.bpy.ops.render.render(write_still=True)
        os.replace(path[:-4] + "_part.png", path)
        if zones:
            with Image.open(path) as im:
                post.draw_zones(im.convert("RGB")).save(path[:-4] + "_zones.png")
        print("[twoapples_set] %s (frame %d, sky %s) %.1f s" % (path, frame, self.sky, time.time() - t), flush=True)
        return path


# ---- staging helpers ---------------------------------------------------------------------------------------------
def _cam(s, beat, focus=None, moving=True, **over):
    """CAMERAS[beat] on shot s: its move (pos0 -> pos, or pos -> pos1) when it has one, else locked. Returns it."""
    c = dict(CAMERAS[beat], **over)
    s.lens(c["lens"], c.get("fstop", 2.8))
    if moving and ("pos0" in c or "target0" in c):
        s.move(c.get("pos0", c["pos"]), c.get("target0", c["target"]), c["pos"], c["target"])
    elif moving and ("pos1" in c or "target1" in c):
        s.move(c["pos"], c["target"], c.get("pos1", c["pos"]), c.get("target1", c["target"]))
    else:
        s.move(c["pos"], c["target"])
    s.focus(focus if focus is not None else c["target"])
    for cut in c.get("see", ()):
        sc_stage(s).see_through(s, cut)
    return c


_STAGE = {}                 # the Stage of the scouting film being staged (stills() sets it; _cam's see-through)


def sc_stage(s):
    """The Stage of the scouting film (for _cam's cutaways)."""
    return _STAGE["st"]


def _actor(sc, s, role, tag):
    """A stand-in: role kid (plain baby villager), dad (librarian, level 2), farmer / fletcher / cleric (level 2),
    steve (engine.players), zombie, zv_dad (zombie villager librarian), zv_kid (baby zombie villager)."""
    from engine import players, undead
    st = sc.st
    name = "%s_%s" % (role, tag)
    if role == "kid":
        c = st.actor(name, "none", child=True)
    elif role == "dad":
        c = st.actor(name, "librarian", level=2)
    elif role in ("farmer", "fletcher", "cleric"):
        c = st.actor(name, role, level=2)
    elif role == "adult":
        c = st.actor(name, "none")
    elif role == "steve":
        c = players.add_player(st, name, "steve")
    elif role == "zombie":
        c = undead.add_zombie(st, name)
    elif role == "zv_dad":
        c = undead.add_zombie_villager(st, name, "librarian", level=2)
    elif role == "zv_kid":
        c = undead.add_zombie_villager(st, name, "none", baby=True)
    else:
        raise KeyError(role)
    st.use(s, c)
    return c


def _put(sc, c, frame, anchor, yaw=None, pos=None):
    """place() c on an anchor (its yaw) or a point."""
    p = sc.A[anchor] if anchor else pos
    y = sc.v.yaws.get(anchor, 0.0) if (yaw is None and anchor) else (yaw or 0.0)
    c.place(frame, p, y)
    return p


def _eyes(c, f):
    return tuple(c.eye_point(f))


HALL_FILL = True            # the hall's cool shadowless fill (group ug_hall) in the aisle shots


def _under_lights(sc, s, scale=None, inside=True, extra=(), groups=None, parts=True):
    """Torches below the ground (the engine's recipe): no village torch, every ug group at `scale`, the hall's fill
    with inside=True (never in a box or slot shot: it passes walls). parts: st.use the lever (False: a shot that
    sees through the end pier)."""
    scale = UNDER if scale is None else scale
    inside = inside and HALL_FILL
    g = {k: scale for k in U.LIGHT_GROUPS}
    g.update(groups or {})
    if parts:
        sc.st.use(s, sc.ug.lever)
    sc.st.lights(s, scale=0.0, groups=g, extra=extra, inside="ug_hall" if inside else ())


def _dusk_lights(sc, s, near, radius=22.0, scale=1.3, ug=1.0, extra=()):
    """The square at dusk: the village's lamps at the look-dev dusk level, the stairwell's torches at `ug`."""
    sc.st.lights(s, scale=scale, groups={k: ug for k in U.LIGHT_GROUPS}, near=near, radius=radius, extra=extra)


def _shut(sc, f):
    """The piston wall shut by frame f (closed there if a shot before opened it)."""
    if sc.ug.door.is_open(f):
        sc.ug.door.close(f)


def _opened(sc, f):
    """The piston wall open by frame f (opened there if it is shut)."""
    if not sc.ug.door.is_open(f):
        sc.ug.door.open(f)


def _cells(sc, s, tag, look=None, skip=(), dad_at="ug_cell_dad"):
    """The four villagers in their cells (farmer, fletcher, cleric, dad), each placed on the shot's first frame;
    look(name) -> a point to look at (ease 0)."""
    f0 = s.frame_start
    out = {}
    for n in U.CELL_X:
        if n in skip:
            continue
        c = _actor(sc, s, n if n != "dad" else "dad", tag)
        spot = dad_at if n == "dad" else "ug_cell_%s" % n
        _put(sc, c, f0, spot)
        if look is not None:
            c.look_at(f0, look(n), ease=0)
        out[n] = c
    return out


def _up(p, dz):
    return (p[0], p[1], p[2] + dz)


# ---- one function per beat: stage stand-ins as the beat's picture says; return ([(frame, tag)], {label: point}) --
def stage_b01(sc, s):
    """Beat 1: Steve crosses in profile from the north and walks down into the glowing mouth; the camera rides on
    his head, then pushes in on the hole (still: Steve at the lip)."""
    from engine import players
    f0 = s.frame_start
    steve = _actor(sc, s, "steve", "b01")
    start = (5.0, 6.5, 0.0)
    path = sc.v.paths["ug_down"]
    steve.place(f0, start, math.pi)
    steve.walk(f0, [start] + path[1:10], speed=players.WALK_SPEED)
    c = CAMERAS["b01"]
    s.lens(c["lens"], c["fstop"])
    s.move(c["pos0"], steve.head, c["pos"], c["target"])
    s.focus((5.0, 0.6, 0.9))
    _dusk_lights(sc, s, sc.A["ug_mouth_target"])
    f = min(range(s.frame_start, s.frame_end + 1), key=lambda k: abs(steve.pos_at(k).y - 0.3))
    return [(f, "")], {"steve": _eyes(steve, f), "hole": sc.A["ug_mouth_target"]}


def stage_b02(sc, s):
    """Beat 2: the child alone at the lip, three-quarter front, staring down, cheated toward the lens."""
    f0 = s.frame_start
    kid = _actor(sc, s, "kid", "b02")
    _put(sc, kid, f0, "ug_lip")
    c = CAMERAS["b02"]
    kid.look_at(f0, U.cheat(sc.A["ug_lip_target"], sc.A["ug_lip"], c["pos"], 0.35), ease=0)
    _cam(s, "b02", focus=kid.head)
    _dusk_lights(sc, s, sc.A["ug_lip"], radius=18.0, scale=1.0, extra=MOUTH_KEY)
    U.bounce(sc.st, s, MOUTH_GLOW, energy=MOUTH_GLOW_WATTS, color=U.POINT_COLOR, kind="torch", name="ta_glow_b02")
    f = f0 + 12
    return [(f, "")], {"kid": _eyes(kid, f)}


def stage_b03(sc, s):
    """Beat 3: dad pushed along to the mouth and down the first step, side-on and low; the child soft in the corner."""
    f0 = s.frame_start
    A = sc.A
    dad = _actor(sc, s, "dad", "b03")
    steve = _actor(sc, s, "steve", "b03")
    kid = _actor(sc, s, "kid", "b03")
    path = list(sc.v.paths["ug_push"]) + [(A["ug_push_start"][0], -2.0, 0.0)]
    r = U.push(steve, dad, f0, path, sc.v.world)
    c = CAMERAS["b03"]
    dad.look_at(f0, (c["pos"][0], c["pos"][1] - 0.6, 1.4), ease=0)
    _put(sc, kid, f0, "ta_push_kid")
    kid.look_at(f0, dad, ease=0)
    _cam(s, "b03", focus=dad.head)
    _dusk_lights(sc, s, A["ug_lip"], radius=20.0, scale=1.0)
    f = (r["drops"][0] - 10) if r.get("drops") else f0 + 50
    return [(f, "")], {"dad": _eyes(dad, f), "steve": _eyes(steve, f), "kid": _eyes(kid, f)}


def stage_b04(sc, s):
    """Beat 4: the child bouncing on the red bed (its foot), lengthwise, the pillow end empty."""
    v = sc.v
    f0 = s.frame_start
    kid = _actor(sc, s, "kid", "b04")
    _put(sc, kid, f0, "ta_kid_bed_foot")
    r = U.bed_bounce(kid, f0, sc.A["ta_kid_bed_foot"], jumps=6)
    c = _cam(s, sc.beat, focus=kid.head)
    kid.look_at(f0, c["pos"], ease=0)
    _room_lights(sc, s)
    f = r["takeoffs"][0] + 6
    return [(f, ""), (r["landings"][0] + 12, "rest")], {"kid": _eyes(kid, f), "window": GABLE_PANE}


def stage_b05(sc, s):
    """Beat 5: the same room, wider, locked off; he stands on the bed facing the door."""
    v = sc.v
    f0 = s.frame_start
    kid = _actor(sc, s, "kid", "b05")
    _put(sc, kid, f0, "ta_kid_bed_door")
    kid.look_at(f0, DOOR_IN, ease=0)
    _cam(s, sc.beat, focus=kid.head)
    _room_lights(sc, s)
    f = f0 + 12
    return [(f, "")], {"kid": _eyes(kid, f)}


ROOM_FILL = False           # house_a's shadowless fill (its light group) on in beats 4 and 5


def _room_lights(sc, s, scale=1.2, room=1.5):
    """Dad's bedroom at dusk: house_a's torches at `room` (the wall torch between the pillows is the key), the room's
    own fill only with ROOM_FILL, nothing outside the house; a weak cool film-local fill (ROOM_COOL) keeps the
    child's skin under the palette's saturation limit (torch light alone: 0.53 against 0.52)."""
    sc.st.lights(s, scale=scale, groups={U.HOUSE: room}, near=sc.v.anchors["house_a_center"], radius=14.0,
                 inside=U.HOUSE if ROOM_FILL else ())
    U.bounce(sc.st, s, ROOM_COOL, energy=ROOM_COOL_WATTS, color=ROOM_COOL_COLOR, kind="fill",
             name="ta_roomfill_" + s.name)


ROOM_COOL = (16.6, -10.6, 3.3)          # under the bed wing's ceiling, between the beds and the wing's opening
ROOM_COOL_WATTS = 45.0
ROOM_COOL_COLOR = (0.90, 0.95, 1.0)


GABLE_PANE = (20.5, -10.5, 4.5)            # house_a's gable window over the bed wall (the dusk sky in it)


def stage_b06(sc, s):
    """Beat 6: the stairwell from high behind; the child running down, tiny, head toward the west wall's torch."""
    v = sc.v
    f0 = s.frame_start
    kid = _actor(sc, s, "kid", "b06")
    path = v.paths["ug_down"]
    kid.place(f0, path[1], math.pi)
    kid.walk(f0, path[1:], speed=4.4, run=True)
    torch = (U.LIGHTS[2][0][0] + 0.1, U.LIGHTS[2][0][1] + 0.5, U.LIGHTS[2][0][2] + 0.6)
    kid.track(f0, s.frame_end, torch, step=2, ease=4)
    _cam(s, "b06", focus=kid.head)
    sc.st.lights(s, scale=0.0, groups={k: 1.0 for k in U.LIGHT_GROUPS})
    f = min(range(s.frame_start, s.frame_end + 1), key=lambda k: abs(kid.pos_at(k).y + 5.6))
    return [(f, "")], {"kid": _eyes(kid, f)}


def stage_b07(sc, s):
    """Beat 7: the ceiling and caps off, steeply down into the row of cells, sliding from the farmer to dad, who
    looks up at the lens (stills: start over the farmer, end over dad)."""
    A = sc.A
    c = CAMERAS[sc.beat]
    _shut(sc, s.frame_start - 6)
    cells = _cells(sc, s, sc.beat, look=lambda n: c["pos"] if n == "dad" else _up(A["ug_aisle_%s" % n], 1.4))
    _cam(s, sc.beat, focus=cells["dad"].head)
    _under_lights(sc, s)
    U.bounce(sc.st, s, DOWN_FILL, energy=DOWN_FILL_WATTS, color=(0.95, 0.97, 1.0), kind="fill",
             name="ta_downfill_" + s.name)
    f = s.frame_end
    return [(s.frame_start, "start"), (f, "")], {"dad": _eyes(cells["dad"], f), "farmer": _eyes(cells["farmer"], f),
                                                  "lever": U.LEVER}


CORNER_KEY = [((19.71, -13.5, F + 1.89), 1.8)]   # beat 8: the back corner's torch x 1.8 on the baby's hands (his
#                                                 head and robe are out of its light: U.shade_face)
DOWN_FILL = (11.0, -13.2, F + 3.6)   # beat 7: a film-local shadowless fill over the row of open pockets (the ceiling
DOWN_FILL_WATTS = 120.0              # is off for the camera): hats and faces lifted out of the dark


def _steve_past(sc, s, tag):
    from engine import players
    steve = _actor(sc, s, "steve", tag)
    path = U.STEVE_PAST
    steve.place(s.frame_start, path[0], village.yaw_to(path[0], path[1]))
    steve.walk(s.frame_start, path, speed=players.WALK_SPEED)
    return steve


def _legs_together(s, steve, f):
    """The frame within 3 of f on which Steve's legs are closest together (least motion smear on the boots)."""
    import bpy
    best = None
    for k in range(max(s.frame_start, f - 3), min(s.frame_end, f + 3) + 1):
        bpy.context.scene.frame_set(k)
        a = abs(steve.leg_r.matrix_basis.to_euler().x)
        if best is None or (a, abs(k - f)) < best[0]:
            best = ((a, abs(k - f)), k)
    return best[1]


def _crossing(s, steve, cam_pos, aim):
    """The frame on which Steve's feet are nearest the camera's line to `aim`."""
    ax, ay = cam_pos[0], cam_pos[1]
    dx, dy = aim[0] - ax, aim[1] - ay
    n = math.hypot(dx, dy)
    dx, dy = dx / n, dy / n

    def off(f):
        p = steve.pos_at(f)
        qx, qy = p.x - ax, p.y - ay
        return abs(qx * dy - qy * dx)
    return min(range(s.frame_start, s.frame_end + 1), key=off)


def stage_b08(sc, s):
    """Beat 8: on the floor of the back corner, Steve's boots pass in focus, the slot soft behind with the baby
    zombie villager's two hands between the bars (his face turned away and kept out of the corner torch)."""
    from engine import undead
    f0 = s.frame_start
    _shut(sc, f0 - 6)
    steve = _steve_past(sc, s, "b08")
    zv = _actor(sc, s, "zv_kid", "b08")
    U.hands_in_slot(zv, f0)
    U.shade_face(sc.v, zv)
    c = _cam(s, "b08", focus=CAMERAS["b08"]["boot"], moving=False)
    _under_lights(sc, s, inside=False, extra=CORNER_KEY)
    f = _crossing(s, steve, c["pos"], U.SLOT_FACE)
    del undead
    return [(lambda sc_: _legs_together(s, steve, f), ""), (f + 16, "hands")], {"slot": U.SLOT_FACE,
                                                                                   "boot": c["boot"]}


def stage_b09(sc, s):
    """Beat 9: Steve's arm flips the lever (held on it), then the pan right onto the back wall past dad while the
    focus pulls there; the wall jerks aside 12 frames after the flip (stills: the hand at the lever, the end)."""
    A = sc.A
    f0 = s.frame_start
    _shut(sc, f0 - 6)
    cells = _cells(sc, s, "b09", look=lambda n: _up(A["ug_aisle_%s" % n], 1.5))
    steve = _actor(sc, s, "steve", "b09")
    _put(sc, steve, f0, "ug_lever_stand")
    r = sc.ug.open_wall(f0 + 10, player=steve, repeater=4, sync="hand")
    c = CAMERAS["b09"]
    s.lens(c["lens"], c["fstop"])
    U.hold_then_move(s, r["flip"] + 2, c["pos"], c["target0"], c["pos"], c["target"], frame_end=r["open"] - 1)
    s.focus(A["ug_lever_target"])
    s.focus(A["ug_door_target"], at_s=sc.film.seconds(r["flip"] + 3), rack_s=0.4)
    _under_lights(sc, s)
    sc.memo["b09"] = r
    return [(r["hand"], "hand"), (r["open_end"] + 6, "")], {"lever": A["ug_lever_target"],
                                                           "dad": _eyes(cells["dad"], r["open_end"] + 6),
                                                           "doorway": A["ug_door_target"]}


def stage_b10(sc, s):
    """Beat 10: low from the aisle, a little east, the lectern in the bottom third; the wall open, the doorway black
    beside his robe; the first blow (still: just before it)."""
    A = sc.A
    f0 = s.frame_start
    _opened(sc, f0 - 10)
    cells = _cells(sc, s, "b10", look=lambda n: _up(A["ug_aisle_%s" % n], 1.5))
    U.hurt_in_cell(cells["dad"], f0 + 12, attacker=A["ug_door_target"])
    _cam(s, "b10", focus=cells["dad"].head)
    _under_lights(sc, s)
    f = f0 + 10
    return [(f, ""), (f0 + 14, "blow")], {"dad": _eyes(cells["dad"], f), "doorway": A["ug_door_target"]}


def stage_b11(sc, s):
    """Beat 11: tight three-quarter portrait of dad; the second blow."""
    A = sc.A
    f0 = s.frame_start
    _opened(sc, f0 - 10)
    cells = _cells(sc, s, "b11", look=lambda n: _up(A["ug_aisle_%s" % n], 1.5))
    U.hurt_in_cell(cells["dad"], f0 + 14, attacker=A["ug_door_target"])
    _cam(s, "b11", focus=cells["dad"].head)
    _under_lights(sc, s)
    f = f0 + 10
    return [(f, "")], {"dad": _eyes(cells["dad"], f)}


def stage_b12(sc, s):
    """Beat 12: frontal, symmetric, the whole cell: dad replaced by the zombie villager on the third blow, arms out
    over the lectern (still: after the swap)."""
    A = sc.A
    f0 = s.frame_start
    _opened(sc, f0 - 10)
    cells = _cells(sc, s, "b12", look=lambda n: _up(A["ug_aisle_%s" % n], 1.5))
    zv = _actor(sc, s, "zv_dad", "b12")
    U.infect_in_cell(cells["dad"], zv, f0 + 6, attacker=A["ug_door_target"])
    zv.aggro(f0 + 6, ease=0)
    _cam(s, "b12", focus=cells["dad"].head)
    _under_lights(sc, s)
    f = f0 + 20
    return [(f, "")], {"zombie dad": _eyes(zv, f)}


def _zv_dad(sc, s, tag, at="ug_cell_dad"):
    zv = _actor(sc, s, "zv_dad", tag)
    _put(sc, zv, s.frame_start, at)
    return zv


def stage_b13(sc, s):
    """Beat 13: side-on along the counter from the east (through the end pier and wall): Steve's throw, the splash
    potion in the air over the counter toward zombie dad."""
    from engine import undead
    f0 = s.frame_start
    A = sc.A
    _shut(sc, f0 - 6)
    zv = _zv_dad(sc, s, "b13")
    zv.aggro(f0, ease=0)
    steve = _actor(sc, s, "steve", "b13")
    steve.hold("golden_apple", hand="left")
    spot = A["ug_counter_steve"]
    steve.place(f0, spot, village.yaw_to(spot, A["ug_cell_dad"]))
    hit = undead.throw_potion(steve, zv, f0 + 6, camera=s)
    _cam(s, "b13", focus=zv.head)
    _under_lights(sc, s, extra=[((14.5, -10.6, F + 1.9), 1.8)], parts=False)
    U.bounce(sc.st, s, U.COUNTER_BOUNCE, energy=COUNTER_WATTS)
    U.bounce(sc.st, s, DAD_SIDE_FILL, energy=DAD_SIDE_WATTS, color=U.POINT_COLOR, kind="torch", name="ta_dadfill_b13")
    f = int(hit) - 3
    return [(f, "")], {"zombie dad": _eyes(zv, f), "steve": _eyes(steve, f)}


COUNTER_WATTS = 70.0        # beat 13: U.COUNTER_BOUNCE on Steve's lens side (the engine's 35 W: his trousers clip at
#                             HALL_EMIT 0.45, min channel 11 against the palette's 12)
DAD_SIDE_FILL = (14.88, -13.75, F + 1.7)    # beats 13, 19: a film-local warm light in the east corner of dad's cell, on his
DAD_SIDE_WATTS = 10.0                       # side toward the lens (the end wall and pier, see-through for the camera,
#                                             still cast shadows: nothing from the lens side reaches him)


def stage_b14(sc, s):
    """Beat 14: close on the golden apple in Steve's raised hand, the green face soft behind it."""
    f0 = s.frame_start
    _shut(sc, f0 - 6)
    zv = _zv_dad(sc, s, "b14")
    zv.aggro(f0, ease=0)
    steve = _actor(sc, s, "steve", "b14")
    steve.hold("golden_apple")
    _put(sc, steve, f0, "ug_aisle_dad")
    steve.raise_arm(f0, angle=55, ease=0)
    apple = tuple(steve.item_point("right", f0 + 12))
    _cam(s, "b14", focus=apple, target=apple)
    _under_lights(sc, s)
    f = f0 + 12
    return [(f, "")], {"apple": apple, "zombie dad": _eyes(zv, f)}


def stage_b15(sc, s):
    """Beat 15: the drift past zombie dad's shoulder toward the open black doorway; the first yellow swirls."""
    from engine import undead
    f0 = s.frame_start
    zv = _zv_dad(sc, s, "b15")
    zv.aggro(f0, ease=0)
    _opened(sc, f0 - 8)
    undead.effect_swirls(zv, f0 - 20, s.frame_end, effect="strength", camera=s)
    c = CAMERAS["b15"]
    s.lens(c["lens"], c["fstop"])
    s.move(c["pos0"], c["target"], c["pos"], c["target"])
    s.focus((14.6, -15.0, F + 1.0))
    _under_lights(sc, s)
    f = s.frame_end - 2
    return [(f, "")], {"doorway": sc.A["ug_door_target"], "zombie dad": _eyes(zv, f)}


def stage_b16(sc, s):
    """Beat 16: wide down the aisle from its east end (through the end pier): zombie dad shaking with yellow swirls in
    his window, the three others in theirs, Steve jumping (still: the top of a jump)."""
    from engine import undead
    A = sc.A
    f0 = s.frame_start
    _shut(sc, f0 - 6)
    _cells(sc, s, "b16", look=lambda n: _up(A["ug_aisle_%s" % n], 1.5), skip=("dad",))
    zv = _zv_dad(sc, s, "b16")
    zv.look_at(f0, _up(A["ug_aisle_dad"], 1.5), ease=0)
    zv.aggro(f0, ease=0)
    undead.shake(zv, f0, s.frame_end, 3.0)
    undead.effect_swirls(zv, f0 - 30, s.frame_end, effect="strength", camera=s)
    steve = _actor(sc, s, "steve", "b16")
    _put(sc, steve, f0, "ug_jump_spot")
    take = U.jump_loop(steve, f0 - 6, s.frame_end)
    _cam(s, "b16", focus=steve.head)
    _under_lights(sc, s, parts=False)
    f = take[1] + 7
    return [(f, "")], {"steve": _eyes(steve, f), "zombie dad": _eyes(zv, f)}


def stage_b17(sc, s):
    """Beat 17: over Steve's shoulder at the counter: the emerald held up, dad cured, holding out the enchanted book
    (engine.fx hold_out with its glint), purple swirls."""
    from engine import fx, undead
    A = sc.A
    f0 = s.frame_start
    _shut(sc, f0 - 6)
    cells = _cells(sc, s, "b17", look=lambda n: _up(A["ug_aisle_%s" % n], 1.5))
    steve = _actor(sc, s, "steve", "b17")
    steve.hold("emerald")
    _put(sc, steve, f0, "ug_aisle_dad")
    steve.raise_arm(f0, angle=EMERALD_RAISE, ease=0)
    dad = cells["dad"]
    dad.look_at(f0, steve, ease=0)
    fx.hold_out(dad, "enchanted_book", f0 + 4, s.frame_end + 1, enchanted=True)
    undead.effect_swirls(dad, f0 - 20, s.frame_end, effect="nausea", camera=s)
    _cam(s, "b17", focus=dad.head)
    _under_lights(sc, s, extra=[((14.5, -10.6, F + 1.9), 1.6)])
    f = f0 + 14
    return [(f, "")], {"dad": _eyes(dad, f), "emerald": tuple(steve.item_point("right", f))}


EMERALD_RAISE = 55.0        # beat 17: Steve's arm (degrees): the emerald low in the frame (y 80 %), dad's book above it
#                             (raised 80 the emerald sat in the caption band, y 65 %, and hid the book)


def stage_b18(sc, s):
    """Beat 18: portrait of dad; his head follows Steve walking away up the aisle with the book to its stop."""
    from engine import players
    A = sc.A
    f0 = s.frame_start
    _shut(sc, f0 - 6)
    _cells(sc, s, "b18", look=lambda n: _up(A["ug_aisle_%s" % n], 1.5), skip=("dad",))
    dad = _actor(sc, s, "dad", "b18")
    _put(sc, dad, f0, "ug_cell_dad_mid")
    steve = _actor(sc, s, "steve", "b18")
    steve.hold("enchanted_book")
    a, b = A["ug_follow_start"], A["ug_follow_end"]
    steve.place(f0, a, village.yaw_to(a, b))
    steve.walk(f0, [a, b], speed=players.WALK_SPEED)
    dad.look_at(f0, steve, ease=0)
    dad.track(f0, s.frame_end, steve, step=2, ease=4)
    _cam(s, "b18", focus=dad.head)
    _under_lights(sc, s)
    f = s.frame_end - 4
    return [(f, "")], {"dad": _eyes(dad, f), "book": tuple(steve.item_point("right", f))}


def stage_b19(sc, s):
    """Beat 19: the cell from the side through the end wall and pier: dad gazing up the aisle in profile; the slide
    off his face onto the piston wall's seam behind his back (stills: the start, the end)."""
    A = sc.A
    f0 = s.frame_start
    _shut(sc, f0 - 6)
    c = CAMERAS["b19"]
    cells = _cells(sc, s, "b19", look=lambda n: _up(A["ug_aisle_%s" % n], 1.5) if n != "dad" else c["look"],
                   dad_at="ug_cell_dad_mid")
    _cam(s, "b19", focus=cells["dad"].head)
    _under_lights(sc, s, parts=False)
    U.bounce(sc.st, s, DAD_SIDE_FILL, energy=DAD_SIDE_WATTS, color=U.POINT_COLOR, kind="torch", name="ta_dadfill_b19")
    return [(f0, "start"), (s.frame_end, "")], {"dad": _eyes(cells["dad"], f0), "seam": SEAM}


def _visible(sc, c, f, see=()):
    """Is character c's face point inside the safe area of the shot camera on frame f, not hidden by a block?"""
    sc.film.goto(f)
    cam = sc.scene.camera
    p = tuple(c.eye_point(f))
    x, y, front = project(sc.scene, cam, p)
    return front and 8 <= x <= 82 and 14 <= y <= 60 and ray_block(sc.v, cam.matrix_world.translation, p, see) is None


def stage_b20(sc, s):
    """Beat 20: two children chase each other round the well; the one in front is swapped for a grown-up while the
    well hides it; the other runs on past the glowing mouth (stills: both children in the picture, the grown-up
    coming out)."""
    A = sc.A
    f0 = s.frame_start
    path = sc.v.paths["ta_round_well"]
    p2 = sc.v.paths["ta_round_well_on"]
    k1 = _actor(sc, s, "kid", "b20a")
    k2 = _actor(sc, s, "kid", "b20b")
    adult = _actor(sc, s, "adult", "b20")
    k1.place(f0, path[0], village.yaw_to(path[0], path[1]))
    k1.walk(f0, path, speed=4.4, run=True)
    k2.place(f0, p2[0], village.yaw_to(p2[0], p2[1]))
    k2.walk(f0 + 4, p2, speed=4.4, run=True)
    c = _cam(s, "b20")
    r = U.swap_hidden(k1, adult, c["pos"], f0, s.frame_end, sc.v.world, then=list(path[2:]), speed=ADULT_SPEED)
    _dusk_lights(sc, s, A["well"], radius=24.0)
    sc.memo["b20"] = r

    def both(sc_):
        if DEBUG and False:
            for f in range(s.frame_start, s.frame_end + 1, 6):
                sc_.film.goto(f)
                cam = sc_.scene.camera
                for c in (k1, k2, adult):
                    p = tuple(c.eye_point(f))
                    x, y, fr = project(sc_.scene, cam, p)
                    print("      f%d %s at (%.1f, %.1f, %.2f) -> x %.0f y %.0f %s" % (
                        f, c.name, p[0], p[1], p[2], x, y, ray_block(sc_.v, cam.matrix_world.translation, p)))
        fs = [f for f in range(s.frame_start, r["frame"]) if _visible(sc_, k1, f) and _visible(sc_, k2, f)]
        print("[twoapples_set]   b20: both children in the safe area on %d frames %s; swap on %d" % (
            len(fs), (fs[0], fs[-1]) if fs else "", r["frame"]))
        return fs[len(fs) // 2] if fs else s.frame_start + 20

    def grown(sc_):
        fs = [f for f in range(r["frame"], s.frame_end + 1) if _visible(sc_, adult, f) and _visible(sc_, k2, f)]
        print("[twoapples_set]   b20: the grown-up and the other child in the safe area on %d frames %s" % (
            len(fs), (fs[0], fs[-1]) if fs else ""))
        return fs[min(len(fs) - 1, 6)] if fs else r["frame"] + 20
    return [(both, ""), (grown, "grown")], {"mouth": A["ug_mouth_target"]}


def stage_b21(sc, s):
    """Beat 21: the slot again from the floor, black inside, no hands; Steve's legs walk past (the slot ends at his
    waist); the slow push in."""
    f0 = s.frame_start
    _shut(sc, f0 - 6)
    steve = _steve_past(sc, s, "b21")
    c = _cam(s, "b21", focus=U.SLOT_FACE)
    _under_lights(sc, s, inside=False)
    f = _crossing(s, steve, c["pos"], U.SLOT_FACE)
    return [(f, ""), (f0, "empty")], {"slot": U.SLOT_FACE}


def stage_b22(sc, s):
    """Beat 22: the foot of the stairs, the child three-quarter front; a zombie steps out of the dark west aisle,
    arms raised, rim-lit by the foot torch."""
    from engine import undead
    A = sc.A
    f0 = s.frame_start
    kid = _actor(sc, s, "kid", "b22")
    _put(sc, kid, f0, "ug_stair_foot")
    kid.look_at(f0, CAMERAS["b22"]["pos"], ease=0)
    z = _actor(sc, s, "zombie", "b22")
    _put(sc, z, f0, "ta_zombie_out")
    z.aggro(f0)
    _cam(s, "b22", focus=kid.head)
    _under_lights(sc, s, inside=False)
    del undead
    f = f0 + 12
    return [(f, "")], {"kid": _eyes(kid, f), "zombie": _eyes(z, f)}


def stage_b23(sc, s):
    """Beat 23: Steve's last blow at the stair foot; the zombie red, knocked back, tipping over."""
    from engine import undead
    A = sc.A
    f0 = s.frame_start
    steve = _actor(sc, s, "steve", "b23")
    steve.hold("iron_sword")
    z = _actor(sc, s, "zombie", "b23")
    _put(sc, steve, f0, "ta_kill_steve")
    _put(sc, z, f0, "ta_kill_zombie")
    z.aggro(f0)
    steve.attack(f0 + 2)
    undead.die(z, f0 + 2, camera=s, attacker=steve)
    _cam(s, "b23", focus=steve.head)
    _under_lights(sc, s, inside=False)
    f = f0 + 12
    return [(f, "")], {"steve": _eyes(steve, f)}


def stage_b24(sc, s):
    """Beat 24: inside the box through its see-through side: the baby zombie villager framed as the child in beat 2,
    lit by the strip of torchlight through the slot; the wall opens, warm light falls in, his first step and the pan
    right onto dad's back (stills: the hold, the open wall)."""
    A = sc.A
    f0 = s.frame_start
    _shut(sc, f0 - 6)
    r = sc.ug.open_wall(f0 + 26, relight=(sc.st, s))
    U.bounce(sc.st, s, U.DOORWAY_GLOW, energy=U.DOORWAY_WATTS, color=U.POINT_COLOR, start=r["open"], kind="torch")
    U.bounce(sc.st, s, U.SLOT_STRIP, energy=U.SLOT_STRIP_WATTS, color=U.POINT_COLOR, kind="torch",
             name="ug_strip_" + s.name)
    zv = _actor(sc, s, "zv_kid", "b24")
    _put(sc, zv, f0, "ta_box_baby")
    c = CAMERAS["b24"]
    zv.look_at(f0, U.cheat(BOX_LOOK, _up(A["ug_box"], 0.6), c["pos"], 0.5), ease=0)
    dad = _actor(sc, s, "dad", "b24")
    _put(sc, dad, f0, "ug_cell_dad")
    for cut in c.get("see", ()):
        sc.st.see_through(s, cut)
    s.lens(c["lens"], c["fstop"])
    run = r["open_end"] + 6
    zv.look_at(run - 3, _up(A["ug_cell_dad"], 1.5), ease=3)
    zv.walk(run, [A["ug_box"], (14.6, -14.9, F)])
    U.hold_then_move(s, run, c["pos"], c["target"], c["pos1"], c["target1"], frame_end=run + 16)
    s.focus(zv.head)
    s.focus(dad.head, at_s=sc.film.seconds(run + 4), rack_s=0.5)
    sc.st.lights(s, scale=0.0, groups={k: UNDER for k in U.LIGHT_GROUPS}, extra=[((14.5, -10.6, F + 1.9), 2.5)])
    sc.memo["b24"] = r
    f = f0 + 12
    return [(f, ""), (r["open_end"] + 3, "open")], {"baby": _eyes(zv, f)}


# beat 24, the mirror of beat 2: the baby in the box turned 20 degrees from the door toward the lens (as the child at
# the lip is turned 38 degrees from it), staring down at the foot of the door, the look cheated half way to the lens
BOX_YAW = math.pi - math.radians(20.0)
BOX_LOOK = (14.5, -14.6, F + 0.1)


SEAM = (14.5, -14.0, F + 1.0)     # beat 19: the seam between the piston wall's two blocks, on their face to dad's cell


# ------------------------------------------------------------------------------------------------------------------
# the light of each place, as the stills were rendered (Stage.lights keywords; near = an anchor name; the film-local
# lights are engine.underground.bounce(st, shot, pos, energy=, color=, kind=) for that one shot)
# ------------------------------------------------------------------------------------------------------------------
_UG = tuple(U.LIGHT_GROUPS)
LIGHTS = {
    # the square at dusk (beats 1, 3, 20): the village's lamps at the look-dev dusk level, the stairwell's torches at 1
    "square": dict(scale=1.3, groups={g: 1.0 for g in _UG}, near="ug_mouth_target", radius=22.0),
    # beat 2: the same with the mouth's two torches x 2.2 and MOUTH_GLOW (240 W, kind torch) low over the hole: the
    # warm glow from below on the child's face (beat 3 uses scale 1.0, near ug_lip, radius 20)
    "lip": dict(scale=1.0, groups={g: 1.0 for g in _UG}, near="ug_lip", radius=18.0, extra=MOUTH_KEY,
                film=[("MOUTH_GLOW", MOUTH_GLOW, MOUTH_GLOW_WATTS, "torch")]),
    # beats 4, 5: dad's bedroom, house_a's torches x 1.5, its own fill OFF, ROOM_COOL (45 W, kind fill, cool)
    "room": dict(scale=1.2, groups={U.HOUSE: 1.5}, near="house_a_center", radius=14.0, inside=(),
                 film=[("ROOM_COOL", ROOM_COOL, ROOM_COOL_WATTS, "fill")]),
    # beat 6: the stairwell, every underground torch at 1, nothing in the village
    "stairs": dict(scale=0.0, groups={g: 1.0 for g in _UG}),
    # beats 7, 9-19, 22-23: the hall (its fill on: inside="ug_hall"); beat 7 adds DOWN_FILL (120 W, fill) over the
    # open pockets; beat 13 the dad torch x 1.8 (extra), U.COUNTER_BOUNCE and DAD_SIDE_FILL (10 W, torch)
    "hall": dict(scale=0.0, groups={g: 1.0 for g in _UG}, inside="ug_hall"),
    # beats 8, 21, 24 (the back corner, the slot, the box): the same WITHOUT the fill (it passes walls and would light
    # the box); beat 24 adds U.SLOT_STRIP (6 W, torch) for the whole shot and U.DOORWAY_GLOW (60 W, torch) from the
    # wall's opening, and the dad torch x 2.5 (extra)
    "box": dict(scale=0.0, groups={g: 1.0 for g in _UG}),
}


def set_data(v, ug):
    """What the film plans from, as data (films/twoapples_common.py calls it once after build_set): dict(anchors,
    yaws, paths, parts, cutaways, cameras, skies, lights, emit). anchors / yaws: every ug_* and ta_* standing spot
    and look target; parts: the moving things (piston_door, lever, house_door = house_a's oak door, doorway = the
    dark / lit copies of the doorway's and the box's faces, red_bed = Village.beds entry of dad's bed)."""
    names = sorted(n for n in v.anchors if n.startswith(("ug_", "ta_")))
    return dict(
        anchors={n: v.anchors[n] for n in names},
        yaws={n: v.yaws[n] for n in names if n in v.yaws},
        paths={n: v.paths[n] for n in ("ug_down", "ug_push", "ug_aisle", "ug_leg", "ug_round_well", "ta_round_well",
                                       "ta_round_well_on")},
        parts=dict(piston_door=ug.door, lever=ug.lever, house_door=v.doors[U.HOUSE], doorway=ug.doorway,
                   red_bed=v.beds[U.BED]),
        cutaways=list(U.CUTAWAYS) + [n for n in v.cutaways if n.startswith(U.HOUSE)],
        cameras={k: dict(c) for k, c in CAMERAS.items()},
        skies={k: dict(c) for k, c in SKIES.items()},
        lights={k: dict(c) for k, c in LIGHTS.items()},
        emit=HALL_EMIT,
    )


STAGES = {b: globals()["stage_" + CAMERAS[b].get("stage", b)] for b in CAMERAS}
SECONDS = {"b01": 3.5, "b03": 6.0, "b04": 4.0, "b06": 2.5, "b07": 3.0, "b08": 2.5, "b09": 2.5, "b13": 1.5,
           "b16": 2.0, "b18": 2.5, "b19": 2.0, "b20": 5.0, "b21": 2.5, "b23": 2.0, "b24": 3.0}


# ------------------------------------------------------------------------------------------------------------------
# where things land in the frame, what hides them
# ------------------------------------------------------------------------------------------------------------------
def project(scene, cam, point):
    """(x %, y % from the top) of a world point in the camera's frame, and whether it is in front of the lens."""
    from bpy_extras.object_utils import world_to_camera_view
    from mathutils import Vector
    co = world_to_camera_view(scene, cam, Vector(point))
    return 100.0 * co.x, 100.0 * (1.0 - co.y), co.z > 0.0


def cut_cells(v, unseen=None):
    """{cell: cutaway name} of the cutaway cells (their blocks live in separate meshes, not in the World); `unseen`
    = names that count (default: all)."""
    out = {}
    for name, got in v.sets["underground"]["cut"].items():
        if unseen is None or name in unseen:
            for c in got:
                out[c] = name
    for c in v.sets["underground"].get("relit", {}):          # the doorway's / the box's own faces: two meshes
        out[c] = "doorway mesh"                               # (dark, lit), never in the World, always solid
    return out


def ray_block(v, a, b, see=(), step=0.04, skip_end=0.3):
    """The first solid block (World or a cutaway the shot does NOT see through) on the line a -> b: (cell, what) or
    None. Thin blocks (bars, fences, lanterns, torches) do not count; the last `skip_end` before b is not tested."""
    w = v.world
    cuts = cut_cells(v, [n for n in v.sets["underground"]["cut"] if n not in see])
    ax, ay, az = (float(c) for c in a)
    bx, by, bz = (float(c) for c in b)
    end_cell = (int(math.floor(bx)), int(math.floor(by)), int(math.floor(bz)))
    d = math.dist((ax, ay, az), (bx, by, bz))
    n = max(1, int(d / step))
    seen = set()
    for i in range(1, n):
        t = i / float(n)
        if (1.0 - t) * d < skip_end:
            break
        c = (int(math.floor(ax + (bx - ax) * t)), int(math.floor(ay + (by - ay) * t)),
             int(math.floor(az + (bz - az) * t)))
        if c in seen or c == end_cell:
            continue
        seen.add(c)
        if c in cuts:
            return c, "cutaway " + cuts[c]
        if w.is_solid(*c):
            bid = w.block_id(*c)
            if bid.endswith(("_fence", "_fence_gate", "lantern", "_wall", "iron_bars", "torch", "_pane")):
                continue
            if bid.endswith(("_stairs", "_slab", "_bed", "lectern", "brewing_stand", "pressure_plate")):
                if az + (bz - az) * t > c[2] + 0.5:
                    continue
            return c, bid
    return None


def _report(sc, beat, frame, heroes):
    cam = sc.scene.camera
    see = CAMERAS[beat].get("see", ())
    for label, p in heroes.items():
        x, y, front = project(sc.scene, cam, p)
        blocked = ray_block(sc.v, cam.matrix_world.translation, p, see=see)
        flag = "" if (8 <= x <= 82 and 14 <= y <= 60 and front) else "   (outside the safe area)"
        if blocked:
            flag += "   (hidden by %s at %s)" % (blocked[1], blocked[0])
        print("[twoapples_set]   %-12s x %5.1f %%  y %5.1f %%%s" % (label, x, y, flag), flush=True)


def stills(beats, res=(540, 960), samples=16, threads=2, suffix="", dry=False, palette=True, frames=None):
    """Stage and render the proof stills of these beats: one build per sky, one shot per beat.
    out/test/twoapples_set_<beat>_<what>[_<tag>]<suffix>.png (+ _zones.png). frames: {beat: [tags]} to render
    only some of a beat's frames."""
    by_sky = {}
    for b in beats:
        by_sky.setdefault(CAMERAS[b]["sky"], []).append(b)
    paths = []
    for sky, bs in by_sky.items():
        sc = Scout(sky, res=res, samples=samples, threads=threads)
        _STAGE["st"] = sc.st
        staged = []
        for b in bs:
            s = sc.st.shot(b, SECONDS.get(CAMERAS[b].get("stage", b), 1.5), sky=sky)
            sc.beat = b
            fr, heroes = STAGES[b](sc, s)
            staged.append((b, fr, heroes))
        sc.st.finish()
        for b, fr, heroes in staged:
            for f, tag in fr:
                if callable(f):
                    f = f(sc)
                if frames and b in frames and tag not in frames[b]:
                    continue
                name = "twoapples_set_%s_%s%s%s" % (b, CAMERAS[b]["what"], ("_" + tag) if tag else "", suffix)
                sc.film.goto(f)
                cp = tuple(sc.scene.camera.matrix_world.translation)
                print("[twoapples_set] %s frame %d camera (%.2f, %.2f, %.2f)" % (b, f, cp[0], cp[1], cp[2]))
                _report(sc, b, f, heroes)
                if dry:
                    continue
                path = sc.render(f, name)
                paths.append(path)
                if palette:
                    from tools import palette_check as pc
                    rep = pc.evaluate(pc.probe(sc.scene), path, heroes=sc.st.heroes.get(b, ()))
                    pc.print_report("%s@%d" % (b, f), rep)
        sc.bpy.ops.wm.read_factory_settings(use_empty=True)
    return paths


# ------------------------------------------------------------------------------------------------------------------
# the self-test (numbers, no render): $BPY -m films.twoapples_set
# ------------------------------------------------------------------------------------------------------------------
THIN = ("_fence", "_fence_gate", "lantern", "iron_bars", "torch", "_pane", "_wall_sign", "lever", "pressure_plate",
        "short_grass", "tall_grass", "poppy", "dandelion", "oxeye_daisy", "cornflower", "_carpet")
NOT_STANDING = ("_target", "_station", "_cam", "_cam_beds", "_center", "_door", "_glow")
SPECIAL = {"ug_slot_hands": "the baby's hand tips at the slot's bars (hands_in_slot places him itself)"}


def _solid(w, cuts, x, y, z, unseen=()):
    """Is the point inside something solid: a World block (thin ones excepted; stairs and bottom slabs by their
    halves; a lectern / brewing stand / bed / composter as a full cube) or a cutaway cell (its block lives in a
    mesh of its own) that is not in `unseen`'s complement... i.e. a cutaway not seen through."""
    c = (int(math.floor(x)), int(math.floor(y)), int(math.floor(z)))
    if c in cuts and cuts[c] not in unseen:
        return True
    if not w.is_solid(*c):
        return False
    bid, props = w.get(*c)
    if bid.endswith(THIN):
        return False
    props = props or {}
    if bid.endswith("_slab") and props.get("type", "bottom") == "bottom":
        return z - c[2] < 0.5 - 1e-6
    if bid.endswith("_bed"):
        return z - c[2] < 9.0 / 16.0
    if bid.endswith("_stairs"):
        if z - c[2] < 0.5 - 1e-6:
            return True
        fx, fy = x - c[0], y - c[1]
        back = {"north": fy >= 0.5, "south": fy < 0.5, "east": fx >= 0.5, "west": fx < 0.5}
        return back.get(props.get("facing", "north"), True)
    return True


def check(verbose=True):
    """Build the set and test it: the village's own checks (paths clear, anchors not in blocks), every standing
    anchor of the set on solid ground with the body free (cutaway cells count as solid), every camera position (pos,
    pos0, pos1) outside every block and every cutaway it does not see through, the piston door shut and its cells,
    the lever on its pier, the paths of this file on the ground. Returns the list of failures."""
    import bpy

    from engine import quick
    bad = []
    say = print if verbose else (lambda *a: None)
    t = time.time()
    scene = quick.reset()
    v, ug = build_set(scene)
    w = v.world
    faces = sum(len(o.data.polygons) for o in scene.objects if o.type == "MESH")
    say("[twoapples_set] built in %.1f s: %d faces; sets %s" % (time.time() - t, faces, sorted(v.sets)))
    for p in v.validate() + list(v.edit_problems):
        bad.append("village: " + p)
    cuts = cut_cells(v)
    # 1. anchors: standing spots on solid ground, the body free (a villager / player 1.95, a child 0.98)
    n_ok = 0
    for name, (x, y, z) in sorted(v.anchors.items()):
        if not (name.startswith("ug_") or name.startswith("ta_")) or name.endswith(NOT_STANDING):
            continue
        if name in SPECIAL:
            say("[twoapples_set]   anchor %-20s not a standing spot: %s" % (name, SPECIAL[name]))
            continue
        under = _solid(w, cuts, x, y, z - 0.05)
        body = [round(zz - z, 2) for zz in (z + 0.3, z + 1.0, z + 1.7) if _solid(w, cuts, x, y, zz)]
        if not under or body:
            bad.append("anchor %s at %s: %s" % (name, tuple(round(c, 2) for c in (x, y, z)),
                                               "nothing solid under it" if not under else "body in a block at %s" % body))
        else:
            n_ok += 1
    say("[twoapples_set] anchors standing on solid ground with the body free: %d" % n_ok)
    # 2. cameras: never inside a block, nor inside a cutaway the shot does not see through
    n = 0
    for beat, c in sorted(CAMERAS.items()):
        see = c.get("see", ())
        for key in ("pos", "pos0", "pos1"):
            if key not in c:
                continue
            n += 1
            x, y, z = c[key]
            cell = (int(math.floor(x)), int(math.floor(y)), int(math.floor(z)))
            if cell in cuts and cuts[cell] not in see:
                bad.append("camera %s %s %s is inside the cutaway %s, which it does not see through" % (
                    beat, key, c[key], cuts[cell]))
            elif w.is_solid(*cell) and not w.block_id(*cell).endswith(THIN):
                bad.append("camera %s %s %s is inside %s" % (beat, key, c[key], w.block_id(*cell)))
            for cc in U.door_cells():
                if tuple(cc) == cell:
                    bad.append("camera %s %s %s is inside a cell of the piston door" % (beat, key, c[key]))
            # the line to the target: the first block it meets (information: a target may lie on a surface)
            hit = ray_block(v, c[key], c.get("target" if key != "pos0" else "target0", c["target"]), see=see)
            if hit and verbose:
                say("[twoapples_set]   camera %s %s: the line to its target meets %s at %s" % (beat, key, hit[1],
                                                                                            hit[0]))
    say("[twoapples_set] camera positions checked: %d (%d beats)" % (n, len(CAMERAS)))
    # 3. the parts: the door shut over DOOR, the lever on the end pier
    if ug.door.is_open(1):
        bad.append("the piston door is open on frame 1")
    pier = (U.LEVER[0], U.LEVER[1] - 1, U.LEVER[2])
    if pier not in cuts and not w.is_solid(*pier):
        bad.append("the lever's pier %s is not there" % (pier,))
    say("[twoapples_set] parts: piston door %s (shut), lever %s on the pier %s" % (U.DOOR, U.LEVER, pier))
    # 4. this file's paths follow the ground (b.path heights) and are not blocked (village.validate covers it)
    for name in ("ta_round_well", "ta_round_well_on"):
        pts = v.paths[name]
        for p in pts:
            g = v.ground(p[0], p[1])
            if abs(p[2] - g) > 0.07:
                bad.append("path %s node %s is not on the ground (ground %.2f)" % (name, p, g))
    say("[twoapples_set] paths ta_round_well (%d nodes), ta_round_well_on (%d nodes)" % (
        len(v.paths["ta_round_well"]), len(v.paths["ta_round_well_on"])))
    for b_ in bad:
        print("[twoapples_set] FAIL " + b_)
    print("[twoapples_set] check %s (%d failures)" % ("ok" if not bad else "FAILED", len(bad)))
    bpy.ops.wm.read_factory_settings(use_empty=True)
    return bad


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args or args == ["check"]:
        sys.exit(1 if check() else 0)
    res, samples, suffix, dry, beats, only, palette = (540, 960), 16, "", False, [], {}, True
    it = iter(args)
    for a in it:
        if a == "--res":
            res = tuple(int(c) for c in next(it).split("x"))
        elif a == "--samples":
            samples = int(next(it))
        elif a == "--suffix":
            suffix = next(it)
        elif a == "--dry":
            dry = True
        elif a == "--no-palette":
            palette = False
        elif a == "--debug":
            DEBUG = True
        elif a == "--under":
            UNDER = float(next(it))
        elif a == "--no-fill":
            HALL_FILL = False
        elif a == "--emit":
            HALL_EMIT = float(next(it))
        elif ":" in a:
            b, tags = a.split(":", 1)
            beats.append(b)
            only[b] = ["" if t == "main" else t for t in tags.split(",")]
        else:
            beats.append(a)
    stills(beats, res=res, samples=samples, suffix=suffix, dry=dry, frames=only or None, palette=palette)
