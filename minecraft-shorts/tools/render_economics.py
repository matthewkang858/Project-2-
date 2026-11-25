"""Render economics: where the time of a final frame goes, and which cheaper setting a one-minute film can use
without it showing on a phone. A measuring tool only: it edits no engine file and writes nothing but
out/test/econ_* (sheets and the encoded test clips) and out/test/econ_raw/ (its own renders, results.jsonl,
summary.json, quality.json, the blind key and answers).

    BPY=/path/to/python-with-bpy ; cd <project root>
    $BPY -m tools.render_economics                # SELF-TEST: renders nothing and writes nothing (builds five film
                                                  #   scenes, ~15 s; add --no-build to skip that): checks the stored
                                                  #   numbers, prints the FINDINGS filled in; exit code 1 on a failure
    $BPY -m tools.render_economics findings       # the FINDINGS alone (no Blender scene is built)
    $BPY -m tools.render_economics noise FILM FRAME [FRAME ...] [--res WxH --samples N]
                                                  # FOR DIRECTORS: what would boil in a film at ITS OWN final quality
                                                  #   (tools/noise_check always measures at 720x1280 / 24 samples)
    $BPY -m tools.render_economics quality [SHOT ...]   # rebuild numbers + sheets of the quality study from the stored
                                                  #   renders (1-2.5 min per shot: give one or two shots per call)
    $BPY -m tools.render_economics crops [SHOT ...]     # the crop sheets alone, from quality.json
    $BPY -m tools.render_economics list           # shots, variants, groups and how many jobs are done
    $BPY -m tools.render_economics run SHOT GROUP [--budget 200] [--threads 2]
                                                  # render the missing jobs of one group for one shot, resumable
    $BPY -m tools.render_economics seq SHOT V1,V2 [--animated | --seed 1] [--budget 200]
                                                  # the 8 consecutive frames of the temporal study for some variants
    $BPY -m tools.render_economics blind [SHOT ...] ; blind-answer TRIAL=L|R ... ; blind-tally
                                                  # unlabelled pairs; the judge's answers; the tally against the key
    $BPY -m tools.render_economics pipeline SHOT [VARIANT]   # one frame rendered exactly as render.py renders a film
    $BPY -m tools.render_economics sync SHOT      # scene-sync cost of 4 consecutive frames, persistent data off / on
    $BPY -m tools.render_economics report         # first pass: tables + sheets of the setting sweeps (summary.json)

RESULT (details, numbers and the exact change: FINDINGS at the end of this file; `findings` prints it filled in):
    RECOMMENDED = 'r540s16'   540x960 at 16 samples, Lanczos x2 to 1080x1920 as engine/post.py does already: 0.49 of
                              the render time (projected: about 3.1 h instead of 6.2 h per 1,440 frames on 4 free
                              cores). Not told from the current final in 40 blind pairs; softer only at 1:1.
    SAFE        = 'r600s16'   600x1066 at 16 samples: 0.63 of the time (about 3.9 h); half of E's softening at 1:1
                              comes back. It does not help a far figure's eyes: only 720x1280 does.
    A film gets either by setting scene.render.resolution_x / _y and scene.cycles.samples in its build(), BEFORE
    its first final frame is rendered; render.py takes them as the film's own FINAL quality. Never pass --res /
    --samples for finals, never render finals in a call that also rendered something with more samples, and leave
    render.FINAL_RES / FINAL_SAMPLES alone (the finished films).

Public API (a film director needs RECOMMENDED / SAFE, FINDINGS and film_noise; the rest is the evidence):

    SHOTS, CROPS       the test shots (film, frame) and the centres of their five 1:1 crops (face, texels, thin,
                       defocus, dark). FIRST_SHOTS = the five of the brief (the whole ladder A-E); MORE_SHOTS = dark
                       interior, running group and the far figure of "The Hello" (E, C and the floor only)
    VARIANTS           every render setting that was measured (name -> overrides); CANDIDATES = the brief's A-E
    RECOMMENDED, SAFE  the recommended final setting of the one-minute films and the safer alternative
    FINDINGS           the conclusions as text; findings() -> the same with the measured tables in front
    film_noise(film, frames, res=None, samples=None) -> {frame: stats}   two-seed noise at the FILM'S OWN final quality
    apply(scene, variant) -> undo      put a variant on a built film's scene; restore(undo) takes it off
    project(seconds_per_frame, frames=1440) -> hours          render time of one film
    projection(anchor='q1') -> {variant: cpu, rel, idle, hours, ...}   cost of the ladder; hours projected from the
                                                               finished films' frame gaps (lower quartile)
    cost_table() -> {shot: {variant: cpu, trace, idle, rel}}   CPU seconds of a frame, every job averaged
    film_frame_seconds() -> {film: {shot: median, q1, min}}    what the finished films' own frames took (file times)
    measure(ses, shot, variant, seed, ...) -> record           render one job on a built render.Session, timed by phase
    run(shot, group) / run_seq(shot, variants, seed=0) / pipeline_check(shot, variant)   the render commands above
    ref_path(shot, frame) / variant_path(shot, variant, frame, seed)             the PNGs (reference = the film's frame;
                                                               a 16-sample still from a 16-sample-only process first)
    deliver(png, how='lanczos') -> PIL 1080x1920               a frame as delivered; the other upscale filters tested
    ssim(a, b), psnr(a, b), acutance(lum), compare(ref_img, img)                 the numbers behind the pictures
    quality(shot) -> {letter: numbers}                         every candidate of a shot against the reference
    temporal(shot, variants) -> stats                          8 consecutive frames, encoded by engine.post.encode
    seed_pair(shot, variant, encoded=True) -> (stats, maps)    the same 8 frames with two noise seeds: motion cancels
    boil(shot, variant) -> stats                               tools/noise_check on encoded frames (two noise seeds)
    far_eyes(variant) -> {head: [(peak, x, y, area), ...]}     the far figure's eyes over 8 delivered frames
    session_order() -> facts                                   16 samples after 24 in one Blender session: noisier
    blind_trials(shots) / blind_answer({trial: 'L'|'R'}) / blind_tally()         many blind pairs, answers stored
    identical_frames() -> {film: counts}                       frames whose scene fingerprint repeats (none do)
    check_final_per_film(film) -> facts                        how render.py takes a film's own setting (one sky or
                                                               several); what a global change of render.FINAL_RES
                                                               would do to finished frames
    quality_report(shots=None) -> dict                         all of the above as tables + sheets; load_quality()
    report() -> dict                                           first pass: setting sweeps on a border region
    selftest() -> exit code

Sheets (out/test/): econ_crops_<shot> (1:1 crops, every candidate), econ_phone_<shot>, econ_upscale_<shot>,
econ_zoom_*, econ_blind2_<shot>_E_{phone,insta} (the 40 blind pairs), econ_boil_<shot> (two seeds, held frame),
econ_seq_<shot> (8 frames), econ_pair_<shot> (two seeds over 8 frames), econ_far_figure (the far figures enlarged),
econ_noise_<film>_<frame> (film_noise). The first-pass sheets (econ_final_*, econ_res_*, econ_samples_*,
econ_combo_*, econ_temporal_*, econ_denoise_*, econ_adaptive_*, econ_paths_*) are rewritten by `report` only.

How time is measured. Other agents render on the same four cores, so wall-clock seconds are useless. Every job
records the CPU seconds of the process (all threads) per phase, from the render_stats handler: sync = render call ->
'Sample 0/N'; trace = -> 'Finished' (path tracing AND the denoiser); comp = compositing; save = the PNG. CPU seconds
still rise with the machine's load (the same reference frame read 69.8, 81 and 85 in three runs), so settings are
compared as RATIOS inside one process, and hours are projected from what the finished films' frames really took.

How likeness is measured. The reference of every shot is the finished film's own final frame on disk (a 'base' job
of this tool is bit-identical to it; the far figure, which is in no film, uses its own 'base' job). Every candidate
is upscaled to 1080x1920 by engine.post.upscale and compared on BT.709 luma: SSIM (8x8 windows) and PSNR of the
whole frame, of the frame at phone size (540x960) and of five 224-pixel crops; 'REF2' is the reference setting
rendered with another noise seed, i.e. what two renders of the CURRENT final differ by (nothing can be closer to
the reference than that). Temporal: 8 consecutive frames are encoded by engine.post.encode itself (caption
included, H.264 crf 16) and decoded again. Three measures: the frame-to-frame change of a clip in still regions
(right for a nearly locked camera, motion-limited in a dolly); tools/noise_check's two-seed test on a held frame;
and the two-seed test over the 8 frames, in which motion cancels (seed_pair), before and after the encoder.

One trap this tool fell into itself: inside one Blender session a 16-sample render that follows a 24-sample render
is noisier than the same setting from a fresh process (session_order()). Groups list 16-sample jobs first, and
the 'fresh*' groups (job tag 'fr') hold the stills that the first pass had rendered the wrong way round.
"""
import json
import math
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

TEST = os.path.join(ROOT, "out", "test")
RAW = os.path.join(TEST, "econ_raw")
RESULTS = os.path.join(RAW, "results.jsonl")
DELIVERY = (1080, 1920)
PHONE = (360, 640)
FINAL_RES, FINAL_SAMPLES = (720, 1280), 24
FILM_FRAMES = 1440                       # one minute at 24 fps

# The test shots (film module, frame of the finished film). 'border' = (x0, y0, x1, y1) as fractions of the frame
# from the TOP LEFT: the part that the six-seed temporal tests and the setting sweeps render (about a third of the
# frame, chosen to hold what boils first: defocused bars, torch-lit walls, grass, out-of-focus backgrounds).
# 'details' = centres of the 1:1 crops shown in the sheets.
SHOTS = {
    "dusk": dict(film="bell", frame=215, border=(0.0, 0.25, 1.0, 0.60),
                 details=[(0.84, 0.31), (0.30, 0.52)],
                 what="Steve at the bell, wide, dusk, two lantern keys, 32 mm f/3.2"),
    "hall": dict(film="nitwit", frame=188, border=(0.0, 0.08, 1.0, 0.43),
                 details=[(0.22, 0.24), (0.60, 0.46)],
                 what="trading hall, defocused iron bars in front of the lens, lantern, 38 mm f/3.4"),
    "sun": dict(film="nitwit", frame=16, border=(0.0, 0.28, 1.0, 0.63),
                details=[(0.45, 0.38), (0.80, 0.62)],
                what="sunlit farmer walking, golden hour, 42 mm f/2.8"),
    "night": dict(film="poppy_night", frame=24, border=(0.0, 0.33, 1.0, 0.68),
                  details=[(0.62, 0.52), (0.18, 0.30)],
                  what="iron golem on night patrol, moonlight, torches, stars"),
    "shallow": dict(film="poppy_day", frame=170, border=(0.0, 0.25, 1.0, 0.60),
                    details=[(0.22, 0.42), (0.52, 0.44)],
                    what="two faces and the poppy, shallow focus, blurred foreground and background"),
    "face": dict(film="nitwit", frame=78, border=(0.0, 0.20, 1.0, 0.55),
                 details=[(0.44, 0.39), (0.86, 0.55)],
                 what="the nitwit's portrait, 66 mm f/2.6: a face in focus, grass blades in front, blurred village"),
    # ---- added after the review: the shot types "The Hello" depends on and the five above do not cover
    "interior": dict(film="bell", frame=120, border=(0.0, 0.20, 1.0, 0.55),
                     details=[(0.47, 0.33), (0.92, 0.50)],
                     what="dark interior, four small faces behind the bed, one torch, 26 mm f/2.6"),
    "run": dict(film="bell", frame=70, border=(0.0, 0.25, 1.0, 0.60),
                details=[(0.42, 0.34), (0.87, 0.59)],
                what="four villagers running at the lens, dusk, 24 mm f/2.8 from the ground (fast motion)"),
    "far": dict(film="_econ_far", frame=12, border=(0.0, 0.25, 1.0, 0.60),
                details=[(0.46, 0.515), (0.35, 0.63)],
                what="the watcher as a small far figure: Herobrine 20 and 32 blocks from a 35 mm lens at night, in "
                     "focus (glowing eyes and plain white eye texels at each distance), handheld"),
}
FIRST_SHOTS = ("dusk", "hall", "sun", "night", "face")       # the five shot types of the brief (the whole ladder A-E)
MORE_SHOTS = ("interior", "run", "far")                      # E and C only (and the floor)
FAR_FILM = "_econ_far"                   # a probe film that exists only in this module (see _far_build)

# Centres (fractions of the frame from the top left) of the 1:1 crops of the quality study, per shot:
# a face, a texture with fine texels, a thin thing, a defocused background and a dark area.
CROPS = {
    "dusk": dict(face=(0.35, 0.45), texels=(0.62, 0.57), thin=(0.44, 0.385), defocus=(0.25, 0.27), dark=(0.06, 0.53)),
    "hall": dict(face=(0.57, 0.46), texels=(0.84, 0.50), thin=(0.22, 0.11), defocus=(0.15, 0.45), dark=(0.14, 0.69)),
    "sun": dict(face=(0.40, 0.37), texels=(0.30, 0.90), thin=(0.80, 0.60), defocus=(0.80, 0.28), dark=(0.30, 0.56)),
    "night": dict(face=(0.58, 0.48), texels=(0.22, 0.74), thin=(0.20, 0.30), defocus=(0.87, 0.60), dark=(0.07, 0.56)),
    "face": dict(face=(0.44, 0.39), texels=(0.42, 0.56), thin=(0.87, 0.55), defocus=(0.30, 0.12), dark=(0.10, 0.42)),
    "shallow": dict(face=(0.21, 0.42), texels=(0.50, 0.66), thin=(0.50, 0.43), defocus=(0.50, 0.10), dark=(0.50, 0.93)),
    "interior": dict(face=(0.47, 0.33), texels=(0.92, 0.50), thin=(0.76, 0.26), defocus=(0.50, 0.88), dark=(0.04, 0.42)),
    "run": dict(face=(0.42, 0.34), texels=(0.87, 0.59), thin=(0.65, 0.56), defocus=(0.75, 0.25), dark=(0.06, 0.60)),
    "far": dict(face=(0.46, 0.515), texels=(0.35, 0.63), thin=(0.10, 0.49), defocus=(0.50, 0.92), dark=(0.18, 0.40)),
}
CROP_NAMES = ("face", "texels", "thin", "defocus", "dark")


def _v(res=None, samples=None, cycles=None, render=None, special=None, min_samples=None, fresh=False, note=""):
    return dict(res=res, samples=samples, cycles=cycles or {}, render=render or {}, special=special or [],
                min_samples=min_samples, fresh=fresh, note=note)


# Every measured variant: overrides on top of the film's final settings (look.setup_render + render.py configure:
# 720x1280, 24 samples, adaptive threshold 0.1, min samples max(4, samples // 3), OIDN albedo+normal, prefilter
# ACCURATE, quality BALANCED). 'fresh' variants change what a Cycles session keeps between frames and need their
# own process.
VARIANTS = {
    "base": _v(note="current final quality"),
    # --- samples
    "s16": _v(samples=16), "s12": _v(samples=12), "s8": _v(samples=8),
    # --- resolution (upscaled to 1080x1920 by engine/post.py, Lanczos)
    "r600": _v(res=(600, 1066)), "r540": _v(res=(540, 960)),
    "r600s16": _v(res=(600, 1066), samples=16), "r600s12": _v(res=(600, 1066), samples=12),
    "r540s16": _v(res=(540, 960), samples=16), "r540s12": _v(res=(540, 960), samples=12),
    "r640s16": _v(res=(640, 1138), samples=16), "r480s16": _v(res=(480, 854), samples=16),
    # 720x1280 at 16 samples as the FIRST job of a process: the picture render.py would make. ('s16' jobs were
    # rendered after a 24-sample job in the same Blender session and reuse the first 16 samples of the reference's
    # own sampling sequence: they are closer to the reference than a real 16-sample film frame would be.)
    "s16f": _v(samples=16, note="A as render.py would render it (fresh session)"),
    "r540s16_fw": _v(res=(540, 960), samples=16, cycles=dict(filter_width=1.0),
                     note="narrower pixel filter (1.0 px instead of 1.3) for the 2x upscale"),
    # --- adaptive sampling
    "ad_off": _v(cycles=dict(use_adaptive_sampling=False), note="every pixel takes all 24 samples"),
    "ad_005": _v(cycles=dict(adaptive_threshold=0.05)),
    "ad_02": _v(cycles=dict(adaptive_threshold=0.2)),
    "ad_min4": _v(min_samples=4), "ad_min12": _v(min_samples=12),
    "s16_min8": _v(samples=16, min_samples=8),
    # --- denoiser
    "dn_off": _v(cycles=dict(use_denoising=False), note="no denoiser: its cost is base - this"),
    "dn_pf_fast": _v(cycles=dict(denoising_prefilter="FAST")),
    "dn_pf_none": _v(cycles=dict(denoising_prefilter="NONE")),
    "dn_q_fast": _v(cycles=dict(denoising_quality="FAST")),
    "dn_q_high": _v(cycles=dict(denoising_quality="HIGH")),
    "dn_rgb_albedo": _v(cycles=dict(denoising_input_passes="RGB_ALBEDO")),
    "dn_rgb": _v(cycles=dict(denoising_input_passes="RGB")),
    # --- light paths and lamps
    "lt_off": _v(cycles=dict(use_light_tree=False), fresh=True, note="light tree off"),
    "lst05": _v(cycles=dict(light_sampling_threshold=0.05)),
    "tb8": _v(cycles=dict(transparent_max_bounces=8)), "tb4": _v(cycles=dict(transparent_max_bounces=4)),
    "gi_full": _v(cycles=dict(use_fast_gi=False), note="full bounce light instead of Fast GI"),
    "diff1": _v(cycles=dict(diffuse_bounces=1, max_bounces=2)),
    "gloss0": _v(cycles=dict(glossy_bounces=0, transmission_bounces=0)),
    "clamp_d": _v(cycles=dict(sample_clamp_direct=4.0)),
    "nomb": _v(render=dict(use_motion_blur=False), fresh=True, note="motion blur off"),
    # --- acceleration structure, threads, compositor
    "bvh2": _v(cycles=dict(debug_bvh_layout="BVH2"), fresh=True, note="Cycles' own BVH2 instead of Embree"),
    "bvh_static": _v(cycles=dict(debug_bvh_type="STATIC_BVH"), fresh=True),
    "spatial": _v(cycles=dict(debug_bvh_type="STATIC_BVH", debug_use_spatial_splits=True), fresh=True),
    "comp_off": _v(render=dict(use_compositing=False), note="no compositor: its cost is base - this"),
    "glare_med": _v(special=["glare_medium"]),
    # --- combinations that were candidates for the recommendation
    "r540s16_pf": _v(res=(540, 960), samples=16, cycles=dict(denoising_prefilter="FAST")),
    "r600s16_pf": _v(res=(600, 1066), samples=16, cycles=dict(denoising_prefilter="FAST")),
    "s16_pf": _v(samples=16, cycles=dict(denoising_prefilter="FAST")),
}

# Job groups: (variant, seeds, border?) lists. 'full' jobs render the whole frame (stills + timing of a frame),
# border jobs render SHOTS[...]['border'] only (a third of the cost).
GROUPS = {
    # the three settings that matter (current, safe, recommended) on every shot ...
    "full": [(v, (0,), False) for v in ("base", "r540s16", "r600s16")],
    # ... resolution and samples apart ...
    "full_more": [(v, (0,), False) for v in ("r540", "s16")],
    "full_rest": [(v, (0,), False) for v in ("r600", "s12", "r540s12", "s8")],
    # ... and six noise seeds of the same frame for the temporal noise (three seeds for the side variants)
    "temporal": [(v, tuple(range(6)), True) for v in ("base", "r540s16", "r600s16")],
    "temporal3": [(v, (0, 1, 2), True) for v in ("s16", "r540")],
    "temporal_low": [(v, (0, 1, 2), True) for v in ("s12", "r540s12", "s8")],
    "denoise": [("base", (0, 1), True), ("dn_off", (0, 1), True), ("dn_pf_fast", (0, 1), True),
                ("dn_pf_none", (0, 1), True), ("dn_q_fast", (0,), True), ("dn_q_high", (0,), True),
                ("dn_rgb_albedo", (0,), True), ("dn_rgb", (0,), True)],
    "adaptive": [(v, (0,), True) for v in ("base", "ad_off", "ad_005", "ad_02", "ad_min4", "ad_min12", "s16_min8")],
    "paths": [(v, (0,), True) for v in ("base", "lst05", "tb4", "diff1", "gloss0", "comp_off", "glare_med")],
    "paths_more": [(v, (0,), True) for v in ("tb8", "gi_full", "clamp_d")],
    "combo": [(v, (0, 1, 2), True) for v in ("r540s16_pf", "r600s16_pf", "s16_pf")],
    # one variant per process (they change what the persistent Cycles session holds); base is rendered beside each
    "lt_off": [("lt_off", (0,), True)], "nomb": [("nomb", (0,), True)], "bvh2": [("bvh2", (0,), True)],
    "bvh_static": [("bvh_static", (0,), True)], "spatial": [("spatial", (0,), True)],
    "threads": [("base", (0,), True)],            # run with --threads 1 / 2 / 4: CPU seconds per thread count
    # ---- the quality study (second pass): the candidates A-E of the brief, cheapest first; the reference is the
    # finished film's own frame on disk (bit-identical to a 'base' job: see ref_path)
    "cand": [(v, (0,), False) for v in ("r540s16", "r600s16", "r540", "r640s16", "s16")],
    "probe": [(v, (0,), False) for v in ("r540s12", "r480s16", "r540s16_fw")],   # cheaper still: where does it break?
    # a second noise seed of the same frame (tools/noise_check's method): the reference's own noise floor and the
    # candidates' boil when nothing moves
    "boil": [(v, (1,), False) for v in ("r540s16", "base", "r600s16")],
    "boil_more": [(v, (1,), False) for v in ("r540", "s16", "r640s16")],
    "boil2": [(v, (1,), False) for v in ("r540", "s16")],
    "afresh": [("s16f", (0,), False)],            # must be the first job of its process: a group of its own
    # the whole ladder again in ONE process (same machine load for every rung): the trustworthy cost ratios, and a
    # check that a second render of a frame is the same picture bit for bit
    "remeasure": [(v, (0,), False) for v in ("r540s16", "base", "r600s16", "r540", "s16", "r640s16")],
    "fresh_b": [("r640s16", (0,), False)],
    # the other direction: 24 samples AFTER 16 in one session (job tag 'gr'); session_order() compares the second
    # job with the same setting rendered as the first job of a process
    "grow": [("r540s16", (0,), False), ("r540", (0,), False)],
    "fresh_probe": [(v, (0,), False) for v in ("r540s12", "r480s16", "r540s16_fw")],
    # the shot types added after the review (MORE_SHOTS): E with two noise seeds, C, then the current final with
    # the other seed (the floor). 16-sample jobs first: see FINDINGS, 'determinism'
    "more": [("r540s16", (0, 1), False), ("r600s16", (0,), False), ("base", (1,), False)],
    "more_ref": [("base", (0,), False)],          # the reference of a shot that is in no finished film ('far')
    # 16-sample stills rendered again in a process that never rendered more samples (job tag 'fr'): the first pass
    # rendered E and C on dusk and hall, and C's second seed on every shot, AFTER a 24-sample job in the same Blender
    # session, and such a render is noisier than the film's frame would be (see FINDINGS, 'determinism').
    # variant_path() prefers the 'fr' job.
    "fresh": [("r540s16", (0,), False), ("r600s16", (0, 1), False)],
    "fresh_c1": [("r600s16", (1,), False)],
}

RECOMMENDED = "r540s16"       # 540x960 at 16 samples: see FINDINGS
SAFE = "r600s16"              # 600x1066 at 16 samples
SAME_SETTING = {"s16f": "s16"}   # two names of one setting (the cost and the two-seed noise are kept under 's16')


# ----------------------------------------------------------------------------------------------------------------
# results store
# ----------------------------------------------------------------------------------------------------------------

def job_key(shot, variant, seed, border, threads=4, tag=""):
    """Key of one job in results.jsonl, e.g. 'hall|r540s16|s3|b|t4'."""
    return "%s|%s|s%d|%s|t%d%s" % (shot, variant, seed, "b" if border else "f", threads, ("|" + tag) if tag else "")


def job_path(key):
    """PNG path of a job's render."""
    return os.path.join(RAW, key.replace("|", "__") + ".png")


def load_results():
    """{key: record} of every finished job (the last record of a key wins)."""
    out = {}
    if os.path.exists(RESULTS):
        with open(RESULTS, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        rec = json.loads(line)
                    except ValueError:
                        continue
                    out[rec["key"]] = rec
    return out


def _append(rec):
    os.makedirs(RAW, exist_ok=True)
    with open(RESULTS, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec) + "\n")


def find_job(shot, variant, seed=0, border=False, tag="", res=None):
    """The record of a finished job whose PNG exists, whatever thread count rendered it (Cycles gives the same
    picture with 2 or 4 threads: checked by the self-test), or None."""
    res = load_results() if res is None else res
    for t in (2, 4, 1, 3):
        rec = res.get(job_key(shot, variant, seed, border, t, tag))
        if rec is not None and os.path.exists(os.path.join(ROOT, rec["path"])):
            return rec
    return None


def project(seconds_per_frame, frames=FILM_FRAMES):
    """Hours to render `frames` frames at `seconds_per_frame`."""
    return seconds_per_frame * frames / 3600.0


# ----------------------------------------------------------------------------------------------------------------
# rendering (needs bpy)
# ----------------------------------------------------------------------------------------------------------------

class _Phases:
    """Timestamps (wall, CPU of the whole process) of the render phases, from Blender's render handlers."""

    def __init__(self, bpy):
        self.bpy = bpy
        self.ev = []
        self._stats = lambda *a: self.ev.append((time.time(), time.process_time(),
                                                 next((x for x in a if isinstance(x, str)), "")))
        self._init = lambda *a: self.ev.append((time.time(), time.process_time(), "H:init"))
        self._post = lambda *a: self.ev.append((time.time(), time.process_time(), "H:post"))
        bpy.app.handlers.render_stats.append(self._stats)
        bpy.app.handlers.render_init.append(self._init)
        bpy.app.handlers.render_post.append(self._post)

    def close(self):
        h = self.bpy.app.handlers
        for lst, fn in ((h.render_stats, self._stats), (h.render_init, self._init), (h.render_post, self._post)):
            if fn in lst:
                lst.remove(fn)

    def split(self, t0, c0, t1, c1):
        """{'sync': (wall, cpu), 'trace': ..., 'comp': ..., 'save': s, 'bvh': wall} from the recorded events."""
        def first(pred, after=0.0):
            for w, c, s in self.ev:
                if w >= after and pred(s):
                    return w, c
            return None

        s0 = first(lambda s: "Sample 0/" in s) or first(lambda s: "Sample " in s) or (t0, c0)
        fin = first(lambda s: s.endswith("Finished"), s0[0]) or first(lambda s: s.startswith("Compositing"), s0[0]) \
            or (t1, c1)
        comp = first(lambda s: s.startswith("Compositing"), fin[0]) or fin
        done = first(lambda s: s.startswith("Time:"), comp[0]) or first(lambda s: s == "H:post", comp[0]) or (t1, c1)
        save = 0.0
        for _w, _c, s in self.ev:
            if s.startswith("Time:") and "Saving:" in s:
                try:
                    mm, ss = s.split("Saving:")[1].strip(" )").split(":")
                    save = int(mm) * 60 + float(ss)
                except ValueError:
                    pass
        b0 = first(lambda s: "Updating Scene BVH" in s)
        b1 = first(lambda s: "Updating Mesh | Computing attributes" in s, b0[0]) if b0 else None
        samples = [s for _w, _c, s in self.ev if "Sample " in s]
        return {
            "sync": (s0[0] - t0, s0[1] - c0), "trace": (fin[0] - s0[0], fin[1] - s0[1]),
            "comp": (max(0.0, done[0] - comp[0] - save), max(0.0, done[1] - comp[1] - save)),
            "tail": (t1 - done[0], c1 - done[1]), "save": save,
            "bvh": (b1[0] - b0[0]) if (b0 and b1) else 0.0,
            "loaded_images": sum("Updating Images | Loading" in s for _w, _c, s in self.ev),
            "last_sample": samples[-1].split("Sample ")[-1] if samples else "",
        }


def apply(scene, variant, threads=4):
    """Put a VARIANTS entry on a built film's scene (on top of the final settings); returns the undo list for
    restore(). Resolution and samples are set the way render.Session.configure does it (adaptive minimum =
    max(4, samples // 3) unless the variant says otherwise)."""
    import bpy

    v = VARIANTS[variant] if isinstance(variant, str) else variant
    undo = []

    def setp(owner, name, value):
        undo.append((owner, name, getattr(owner, name)))
        setattr(owner, name, value)

    r, c = scene.render, scene.cycles
    res = v["res"] or FINAL_RES
    samples = v["samples"] or FINAL_SAMPLES
    setp(r, "resolution_x", int(res[0]))
    setp(r, "resolution_y", int(res[1]))
    setp(r, "resolution_percentage", 100)
    setp(c, "samples", int(samples))
    setp(c, "adaptive_min_samples", int(v["min_samples"] or max(4, samples // 3)))
    setp(r, "threads_mode", "FIXED")
    setp(r, "threads", int(threads))
    for name, value in v["cycles"].items():
        setp(c, name, value)
    for name, value in v["render"].items():
        setp(r, name, value)
    if "glare_medium" in v["special"]:
        from engine import look

        tree = bpy.data.node_groups.get(look.COMP_GROUP)
        node = tree.nodes.get("look_bloom") if tree else None
        if node is not None:
            for s in node.inputs:
                if s.name == "Quality":
                    undo.append((s, "default_value", s.default_value))
                    s.default_value = "Medium"
    return undo


def restore(undo):
    """Undo apply()."""
    for owner, name, value in reversed(undo):
        try:
            setattr(owner, name, value)
        except (AttributeError, TypeError):
            pass


def _set_border(scene, box):
    """Render only `box` = (x0, y0, x1, y1), fractions from the top left; the picture keeps its full size."""
    r = scene.render
    if box is None:
        r.use_border = False
        return
    x0, y0, x1, y1 = box
    r.use_border = True
    r.use_crop_to_border = False
    r.border_min_x, r.border_max_x = float(x0), float(x1)
    r.border_min_y, r.border_max_y = 1.0 - float(y1), 1.0 - float(y0)


def lights_on(scene):
    """(lights that are rendered at the current frame, all light objects)."""
    lights = [o for o in scene.objects if o.type == "LIGHT"]
    on = [o for o in lights if not o.hide_render and o.data.energy > 0.0]
    return len(on), len(lights)


def measure(ses, shot, variant, seed=0, border=False, threads=4, frame=None, tag="", path=None):
    """Render one job on a built render.Session and return its record (phases in wall and CPU seconds). The scene
    is left as it was."""
    bpy = ses.bpy
    scene = ses.scene
    S = SHOTS[shot]
    frame = S["frame"] if frame is None else frame
    key = job_key(shot, variant, seed, border, threads, tag)
    path = path or job_path(key)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    undo = apply(scene, variant, threads)
    old_seed = scene.cycles.seed
    scene.cycles.seed = int(seed)
    _set_border(scene, S["border"] if border else None)
    ph = _Phases(bpy)
    try:
        tg = time.time()
        ses.film.goto(frame)
        goto = time.time() - tg
        scene.render.filepath = path[:-4]
        scene.render.use_file_extension = True
        load = os.getloadavg()[0]
        t0, c0 = time.time(), time.process_time()
        bpy.ops.render.render(write_still=True)
        t1, c1 = time.time(), time.process_time()
        sp = ph.split(t0, c0, t1, c1)
    finally:
        ph.close()
        _set_border(scene, None)
        scene.cycles.seed = old_seed
        r = scene.render
        res = (r.resolution_x, r.resolution_y)
        samples = scene.cycles.samples
        restore(undo)
    on, total = lights_on(scene)
    rec = dict(key=key, shot=shot, variant=variant if isinstance(variant, str) else "?", seed=seed, border=bool(border),
               threads=threads, frame=frame, res=list(res), samples=samples, path=os.path.relpath(path, ROOT),
               wall=round(t1 - t0, 3), cpu=round(c1 - c0, 3), goto=round(goto, 3), load=round(load, 2),
               sync_wall=round(sp["sync"][0], 3), sync_cpu=round(sp["sync"][1], 3),
               trace_wall=round(sp["trace"][0], 3), trace_cpu=round(sp["trace"][1], 3),
               comp_wall=round(sp["comp"][0], 3), comp_cpu=round(sp["comp"][1], 3), save=round(sp["save"], 3),
               tail_wall=round(sp["tail"][0], 3), bvh=round(sp["bvh"], 3), loaded_images=sp["loaded_images"],
               last_sample=sp["last_sample"], lights_on=on, lights=total, tag=tag, when=round(time.time(), 1))
    return rec


def _far_build(scene):
    """build() of the probe film FAR_FILM: one 1.5 s shot of the real village under the night film's own sky
    (films/poppy_night.py: preset night, moon azimuth 176, elevation 21, bloom 1.3, grade cool, torches 1.3).
    Herobrine stands 20 blocks from a 35 mm f/4 lens and is in focus: on the left with glowing eyes
    (players.HEROBRINE_GLOW), on the right with plain white eye texels (glow 0); a child crosses the foreground;
    handheld drift 0.02. That pair is the layout of the reviewer's probe (tools/check_economics_far.py; nothing of
    that file is used): a head is 54 delivered pixels wide, a texel 3.4 rendered pixels at 540x960 and 4.5 at
    720x1280. A second pair stands 32 blocks away, between and left of the first (glowing in the middle, plain on
    the left): a texel is 2.1 rendered pixels at 540x960 and 2.8 at 720x1280, each eye about 4 x 2 pixels."""
    from engine import look, shots, village
    from engine import players as pl
    from films import lookdev

    v = village.build_village(scene, seed=1)
    sky = look.set_time(scene, "night", sun_azimuth=176.0, sun_elevation=21.0)
    look.setup_compositor(scene, bloom=1.3, grade="cool")
    film = shots.Film(scene, fps=24)
    st = lookdev.Stage(scene, film, v, sky)
    s = st.shot("far", 1.5)
    f0 = s.frame_start
    kid = st.actor("kid", "none", child=True)
    hb = pl.add_player(st, "herobrine", "herobrine")
    hb.place(f0, (-0.6, 44.0, 0.0), 0.0)
    hb0 = pl.add_player(st, "herobrine0", "herobrine", glow=0.0)
    hb0.place(f0, (1.6, 44.0, 0.0), 0.0)
    far = pl.add_player(st, "herobrine_far", "herobrine")
    far.place(f0, (0.5, 56.0, float(v.ground(0.5, 56.0) or 0.0)), 0.0)
    far0 = pl.add_player(st, "herobrine_far0", "herobrine", glow=0.0)
    far0.place(f0, (-2.6, 56.0, float(v.ground(-2.6, 56.0) or 0.0)), 0.0)
    kid.place(f0, (5.5, 30.0, 0.0), math.radians(90))
    kid.walk(f0, [(5.5, 30.0, 0.0), (-4.0, 30.0, 0.0)], speed=2.0)
    for h in (hb, hb0, far, far0):
        h.watch(f0, s.frame_end, kid)
    st.use(s, hb, hb0, far, far0, kid)
    s.lens(35, 4.0)
    s.move((0.4, 24.0, 1.3), (0.5, 44.0, 1.5))
    s.focus(hb.head)
    s.handheld(0.02, seed=3)
    st.lights(s, scale=1.3)
    st.finish()
    return {"film": film, "captions": [], "stage": st}


def _session(shot):
    """A built render.Session of the shot's film (the probe film FAR_FILM is registered as a module first)."""
    import types

    import render as R

    name = SHOTS[shot]["film"]
    if name == FAR_FILM and ("films." + name) not in sys.modules:
        mod = types.ModuleType("films." + name)
        mod.build = _far_build
        sys.modules["films." + name] = mod
    ses = R.Session(name)
    return ses


def _warm(ses, shot, threads):
    """One tiny render of the frame before the test frame: loads the textures and builds the BVHs, so that the jobs
    after it are steady-state frames of a chunked render (render.py renders many frames per process)."""
    scene = ses.scene
    tiny = _v(res=(90, 160), samples=1, cycles=dict(use_denoising=False))
    path = os.path.join(RAW, "_warm.png")
    rec = measure(ses, shot, tiny, threads=threads, frame=SHOTS[shot]["frame"] - 1, tag="warm", path=path)
    if os.path.exists(path):
        os.remove(path)
    return rec


def run(shot, group, budget=200.0, threads=4):
    """Render the missing jobs of GROUPS[group] for one shot; stops starting jobs after `budget` seconds."""
    t_start = time.time()
    done = load_results()
    jobs = []
    # 'remeasure' renders everything again, in one process; 'fresh*' renders 16-sample stills again, 16 samples only
    tag = "re" if group == "remeasure" else "fr" if group.startswith("fresh") else "gr" if group == "grow" else ""
    for variant, seeds, border in GROUPS[group]:
        for seed in seeds:
            key = job_key(shot, variant, seed, border, threads, tag)
            if not tag and find_job(shot, variant, seed, border, res=done) is not None:
                continue                                    # rendered before, with whatever thread count
            if key not in done or not os.path.exists(job_path(key)):
                jobs.append((variant, seed, border, key))
    if not jobs:
        print("[econ] %s/%s: nothing to do" % (shot, group))
        return 0
    print("[econ] %s/%s: %d jobs to render" % (shot, group, len(jobs)), flush=True)
    ses = _session(shot)
    fresh = [v for v, _s, _b, _k in jobs if VARIANTS[v]["fresh"]]
    hold = None
    if fresh:
        # a variant that changes what the persistent session holds stays applied for the whole process, warm-up
        # included; the base job of the same region is rendered FIRST, in a session of its own state
        assert len(set(fresh)) == 1 and len(jobs) == len(fresh), "a 'fresh' variant needs a group of its own"
    w = _warm(ses, shot, threads)
    print("[econ] warm-up: sync %.2fs (bvh %.2fs, %d images), lights on %d of %d"
          % (w["sync_wall"], w["bvh"], w["loaded_images"], w["lights_on"], w["lights"]), flush=True)
    if fresh:
        key = job_key(shot, "base", 0, True, threads, tag="pair_" + fresh[0])
        rec = measure(ses, shot, "base", 0, True, threads, tag="pair_" + fresh[0])
        _append(rec)
        print("[econ] %-34s trace %6.1f cpu-s (pair base)" % (key, rec["trace_cpu"]), flush=True)
        hold = apply(ses.scene, fresh[0], threads)
        ses.scene.render.use_persistent_data = False        # the next render builds a new session with the variant
        measure(ses, shot, _v(res=(90, 160), samples=1, cycles=dict(use_denoising=False)), threads=threads,
                frame=SHOTS[shot]["frame"] - 1, tag="warm", path=os.path.join(RAW, "_warm.png"))
        ses.scene.render.use_persistent_data = True
    n = 0
    for variant, seed, border, key in jobs:
        if time.time() - t_start > budget:
            print("[econ] budget used: %d jobs left, run the same command again" % (len(jobs) - n), flush=True)
            break
        rec = measure(ses, shot, variant, seed, border, threads, tag=tag)
        _append(rec)
        n += 1
        print("[econ] %-34s %dx%d %2dspp  sync %.2f  trace %6.1f cpu-s (%5.1f wall)  comp %.2f  save %.2f  load %.1f"
              % (key, rec["res"][0], rec["res"][1], rec["samples"], rec["sync_wall"], rec["trace_cpu"],
                 rec["trace_wall"], rec["comp_cpu"], rec["save"], rec["load"]), flush=True)
    if hold:
        restore(hold)
    return 0


SEQ_FRAMES = 8                # consecutive frames of the temporal study: frames F-3 .. F+4 around SHOTS[...]['frame']


def seq_frames(shot):
    """The 8 consecutive frame numbers of a shot's temporal sequence."""
    f = SHOTS[shot]["frame"]
    return list(range(f - 3, f - 3 + SEQ_FRAMES))


def seq_tag(frame, animated=False):
    """Job tag of one frame of a sequence ('q0021'; 'a0021' when the noise seed follows the frame number)."""
    return "%s%04d" % ("a" if animated else "q", frame)


def run_seq(shot, variants, budget=200.0, threads=2, animated=False, seed=0):
    """Render the missing frames of the 8-frame sequences of one shot for the given variants (noise seed 0 on
    every frame, as render.py renders a film; animated=True: seed = frame number; seed=1: the same 8 frames with
    another fixed seed, for seed_pair()). Resumable. Give 16-sample and 24-sample variants a process each."""
    t_start = time.time()
    jobs = []
    for variant in variants:
        for f in seq_frames(shot):
            sd = f if animated else int(seed)
            if seq_frame_path(shot, variant, f, animated, seed=seed) is None:
                jobs.append((variant, f, sd))
    if not jobs:
        print("[econ] %s sequences %s: nothing to do" % (shot, ",".join(variants)))
        return 0
    print("[econ] %s sequences: %d frames to render" % (shot, len(jobs)), flush=True)
    ses = _session(shot)
    _warm(ses, shot, threads)
    n = 0
    for variant, f, seed in jobs:
        if time.time() - t_start > budget:
            print("[econ] budget used: %d frames left, run the same command again" % (len(jobs) - n), flush=True)
            break
        rec = measure(ses, shot, variant, seed, False, threads, frame=f, tag=seq_tag(f, animated))
        _append(rec)
        n += 1
        print("[econ] %-40s %dx%d %2dspp  trace %6.1f cpu-s (%5.1f wall)  load %.1f"
              % (rec["key"], rec["res"][0], rec["res"][1], rec["samples"], rec["trace_cpu"], rec["trace_wall"],
                 rec["load"]), flush=True)
    return 0


def pipeline_check(shot, variant="r540s16", threads=2):
    """Render one frame of a shot exactly the way render.py renders a film at this setting (Session.configure once,
    then Session.render_frame; no setting is touched between frames): as the FIRST frame of the process, then the
    frame before it, then the same frame AGAIN. Stores out/test/econ_raw/pipe_<shot>_<variant>_{first,again}.png and
    appends a record saying which renders hold the same pixels: first == again (a chunked render gives the same
    frame wherever a chunk starts) and which stored job of this tool they equal."""
    v = VARIANTS[variant]
    ses = _session(shot)
    ses.configure(v["res"] or FINAL_RES, v["samples"] or FINAL_SAMPLES, threads, None)
    f = SHOTS[shot]["frame"]
    first = os.path.join(RAW, "pipe_%s_%s_first.png" % (shot, variant))
    again = os.path.join(RAW, "pipe_%s_%s_again.png" % (shot, variant))
    tmp = os.path.join(RAW, "_pipe_tmp.png")
    ses.render_frame(f, first)
    ses.render_frame(f - 1, tmp)
    ses.render_frame(f, again)
    if os.path.exists(tmp):
        os.remove(tmp)
    res = load_results()
    same = {}
    for key, rec in res.items():
        if rec.get("kind") is None and rec.get("shot") == shot and rec.get("variant") == variant and not rec.get("border") \
                and rec.get("seed") == 0 and rec.get("frame") == f and os.path.exists(os.path.join(ROOT, rec["path"])):
            same[key] = same_pixels(first, os.path.join(ROOT, rec["path"]))
    row = dict(key="%s|pipeline|%s" % (shot, variant), kind="pipeline", shot=shot, variant=variant, frame=f,
               first_equals_again=same_pixels(first, again), equals_job=same, threads=threads)
    _append(row)
    print("[econ] pipeline %s %s frame %d: first frame of the process == the same frame rendered again later: %s"
          % (shot, variant, f, row["first_equals_again"]))
    for k, s_ in same.items():
        print("[econ]   == stored job %-40s %s" % (k, s_))
    return row


def sync_study(shot, threads=2):
    """Scene-sync cost per frame over 4 consecutive frames, with persistent data off and then on (tiny pictures, so
    nothing but the sync, the BVH build and the texture load is measured), plus the cost of render.py's own
    per-frame bookkeeping (film.goto and the scene fingerprint)."""
    ses = _session(shot)
    scene = ses.scene
    f = SHOTS[shot]["frame"]
    tiny = _v(res=(90, 160), samples=1, cycles=dict(use_denoising=False))
    out = []
    for persistent in (False, True):
        scene.render.use_persistent_data = persistent
        for k in range(4):
            tf = time.time()
            ses.fingerprint(f - 3 + k)
            fp = time.time() - tf
            rec = measure(ses, shot, tiny, threads=threads, frame=f - 3 + k, tag="sync",
                          path=os.path.join(RAW, "_sync.png"))
            row = dict(key="%s|sync|p%d|k%d" % (shot, int(persistent), k), shot=shot, kind="sync",
                       persistent=persistent, index=k, frame=f - 3 + k, fingerprint=round(fp, 3),
                       goto=rec["goto"], sync_wall=rec["sync_wall"], sync_cpu=rec["sync_cpu"], bvh=rec["bvh"],
                       loaded_images=rec["loaded_images"], total_wall=rec["wall"], total_cpu=rec["cpu"],
                       load=rec["load"], faces=ses._face_count(), objects=len(scene.objects),
                       lights_on=rec["lights_on"], lights=rec["lights"])
            _append(row)
            out.append(row)
            print("[econ] sync %s persistent=%d frame %d: goto %.2f  fingerprint %.2f  sync %.2f wall / %.2f cpu  "
                  "(bvh %.2f, %d images loaded)  whole tiny render %.2f"
                  % (shot, persistent, row["frame"], row["goto"], fp, row["sync_wall"], row["sync_cpu"], row["bvh"],
                     row["loaded_images"], row["total_wall"]), flush=True)
    scene.render.use_persistent_data = True
    p = os.path.join(RAW, "_sync.png")
    if os.path.exists(p):
        os.remove(p)
    return out


# ----------------------------------------------------------------------------------------------------------------
# analysis (PIL + numpy only)
# ----------------------------------------------------------------------------------------------------------------

def _load(path, box=None, size=DELIVERY):
    """A job's PNG upscaled to `size` the way engine/post.py does it (Lanczos), optionally cut to `box` (fractions
    of the frame from the top left) -> float32 HxWx3 array."""
    import numpy as np
    from PIL import Image

    with Image.open(path) as im:
        im = im.convert("RGB")
        if im.size != tuple(size):
            im = im.resize(tuple(size), Image.LANCZOS)
        if box is not None:
            w, h = im.size
            im = im.crop((int(round(box[0] * w)), int(round(box[1] * h)), int(round(box[2] * w)), int(round(box[3] * h))))
        return np.asarray(im).astype(np.float32)


def _inset(box, margin=0.012):
    """The border box shrunk a little: the denoiser and the bloom behave differently on the rim of a border render."""
    return (box[0] + margin, box[1] + margin, box[2] - margin, box[3] - margin)


def temporal_sigma(paths, box=None, size=DELIVERY):
    """Frame-to-frame noise of N renders of the SAME frame with different noise seeds (what boils in a film when
    nothing moves): per-pixel standard deviation over the N pictures, in 8-bit levels, on the pictures as delivered
    (upscaled to `size`). Returns mean / median / p99 of the per-pixel sigma (largest of the three channels), the
    same for 'flat' pixels (local gradient of the mean picture under 6 levels) and the noise_check numbers of the
    first pair (mean and p99 of the largest channel difference)."""
    import numpy as np

    stack = np.stack([_load(p, box, size) for p in paths])                  # N x H x W x 3
    sig = stack.std(axis=0, ddof=1).max(axis=2)
    mean = stack.mean(axis=0)
    lum = mean.mean(axis=2)
    gy, gx = np.gradient(lum)
    flat = np.hypot(gx, gy) < 6.0
    d = np.abs(stack[0] - stack[1]).max(axis=2)
    out = dict(n=len(paths), mean=float(sig.mean()), median=float(np.median(sig)), p99=float(np.percentile(sig, 99)),
               flat_mean=float(sig[flat].mean()) if flat.any() else 0.0,
               flat_p99=float(np.percentile(sig[flat], 99)) if flat.any() else 0.0, flat_share=float(flat.mean()),
               pair_mean=float(d.mean()), pair_p99=float(np.percentile(d, 99)),
               over6=float((d > 6).mean()))
    return out, sig, mean


def error_to(ref_mean, path, box, size=DELIVERY):
    """RMS difference (8-bit levels) between one render and the seed-averaged reference picture, same crop."""
    import numpy as np

    a = _load(path, box, size)
    return float(np.sqrt(((a - ref_mean) ** 2).mean()))


def _records(res, shot, variant, border, threads=4, tag=""):
    """Finished jobs of one variant, by seed (threads=None: whatever thread count rendered them)."""
    out = [r for r in res.values() if r.get("shot") == shot and r.get("variant") == variant
           and r.get("border") == border and (threads is None or r.get("threads") == threads)
           and r.get("tag", "") == tag and r.get("kind") is None]
    return sorted(out, key=lambda r: (r["seed"], -r["threads"]))


def idle_seconds(rec, threads=4):
    """Estimated seconds of this job on `threads` free cores: the serial phases as measured in CPU time, the
    trace (path tracing + denoising) divided by the thread count."""
    return rec["sync_cpu"] + rec["comp_cpu"] + rec["save"] + rec["trace_cpu"] / float(threads)


def _label(img, text, scale=2, pos=(4, 4)):
    """Draw a small label in the game font (engine.captions.label) on a PIL image."""
    from engine import captions as cap

    lab = cap.label(text, scale=scale)
    img.paste(lab, pos, lab)
    return img


def _crop_centre(arr, centre, size):
    """size x size window of an HxWx3 array around a centre given in fractions (clamped to the picture)."""
    h, w = arr.shape[:2]
    x = int(min(max(centre[0] * w - size / 2, 0), w - size))
    y = int(min(max(centre[1] * h - size / 2, 0), h - size))
    return arr[y:y + size, x:x + size]


AFTER_24 = "tiles under 24 samples were rendered after a 24-sample job in one session: noisier than a film frame"


def sheet_compare(shot, variants, name, res=None, crop=420, threads=None, note=None):
    """Side-by-side sheet of full-frame jobs: one column per variant; rows = the 1:1 crops of the delivered
    1080x1920 picture around SHOTS[shot]['details'], then the whole frame at phone size (360x640). A setting with
    a still from a 16-sample-only process (job tag 'fr') shows that one; `note` is written under the sheet."""
    import numpy as np
    from PIL import Image

    res = res or load_results()
    cost = cost_table().get(shot, {})
    cols = []
    for v in variants:
        recs = _records(res, shot, v, False, threads, tag="fr") or _records(res, shot, v, False, threads)
        if not recs:
            continue
        p = os.path.join(ROOT, recs[0]["path"])
        if not os.path.exists(p):
            continue
        full = _load(p)
        parts = []
        for i, c in enumerate(SHOTS[shot]["details"]):
            tile = Image.fromarray(_crop_centre(full, c, crop).astype(np.uint8))
            if i == 0:
                r = recs[0]
                _label(tile, "%s %dx%d %dspp" % (v, r["res"][0], r["res"][1], r["samples"]))
                # the cost as the FINDINGS table has it (every job of the setting, relative to REF on this shot);
                # no seconds here: a time read from one job on a loaded machine contradicted that table
                row = cost.get(SAME_SETTING.get(v, v))
                if row and row.get("rel"):
                    _label(tile, "cost x%.2f of REF" % row["rel"], pos=(4, 24))
            parts.append(tile)
        with Image.open(p) as im:
            phone = im.convert("RGB").resize(DELIVERY, Image.LANCZOS).resize(PHONE, Image.LANCZOS)
        pad = Image.new("RGB", (crop, PHONE[1]), (18, 18, 22))
        pad.paste(phone, ((crop - PHONE[0]) // 2, 0))
        parts.append(pad)
        col = Image.new("RGB", (crop, sum(p_.size[1] for p_ in parts) + 6 * (len(parts) - 1)), (18, 18, 22))
        y = 0
        for p_ in parts:
            col.paste(p_, (0, y))
            y += p_.size[1] + 6
        cols.append(col)
    if not cols:
        return None
    sheet = Image.new("RGB", (sum(c.size[0] for c in cols) + 6 * (len(cols) - 1), cols[0].size[1] + (24 if note else 0)),
                      (18, 18, 22))
    x = 0
    for c in cols:
        sheet.paste(c, (x, 0))
        x += c.size[0] + 6
    if note:
        _label(sheet, note, scale=1, pos=(4, cols[0].size[1] + 6))
    path = os.path.join(TEST, "econ_%s_%s.png" % (name, shot))
    sheet.save(path)
    return path


def sheet_temporal(shot, variants, name="temporal", res=None, threads=4, gain=24.0):
    """Temporal-noise sheet of the border jobs: per variant the delivered crop (seed 0) above its per-pixel sigma
    over the seeds, x `gain` (a sigma of 255 / gain levels is white)."""
    import numpy as np
    from PIL import Image

    res = res or load_results()
    box = _inset(SHOTS[shot]["border"])
    rows, stats = [], {}
    for v in variants:
        recs = _records(res, shot, v, True, threads)
        paths = [os.path.join(ROOT, r["path"]) for r in recs if os.path.exists(os.path.join(ROOT, r["path"]))]
        if len(paths) < 2:
            continue
        st, sig, _mean = temporal_sigma(paths, box)
        stats[v] = st
        pic = Image.fromarray(_load(paths[0], box).astype(np.uint8)).resize((540, int(540 * sig.shape[0] / sig.shape[1])),
                                                                             Image.LANCZOS)
        heat = Image.fromarray(np.clip(sig * gain, 0, 255).astype(np.uint8)).convert("RGB").resize(pic.size, Image.BILINEAR)
        _label(pic, "%s  n=%d" % (v, st["n"]))
        _label(heat, "sigma mean %.2f p99 %.1f flat %.2f" % (st["mean"], st["p99"], st["flat_mean"]))
        row = Image.new("RGB", (pic.size[0] * 2 + 6, pic.size[1]), (18, 18, 22))
        row.paste(pic, (0, 0))
        row.paste(heat, (pic.size[0] + 6, 0))
        rows.append(row)
    if not rows:
        return None, stats
    sheet = Image.new("RGB", (rows[0].size[0], sum(r.size[1] for r in rows) + 6 * (len(rows) - 1) + 24), (18, 18, 22))
    y = 0
    for r in rows:
        sheet.paste(r, (0, y))
        y += r.size[1] + 6
    _label(sheet, "first pass. " + AFTER_24, scale=1, pos=(4, y + 4))
    path = os.path.join(TEST, "econ_%s_%s.png" % (name, shot))
    sheet.save(path)
    return path, stats


def sheet_border(shot, variants, name, res=None, threads=4, crop=300):
    """Sheet of border jobs (seed 0): per variant a 1:1 crop of the delivered picture around the first detail
    point that lies inside the border region, labelled with its trace cost relative to base."""
    import numpy as np
    from PIL import Image

    res = res or load_results()
    S = SHOTS[shot]
    b = S["border"]
    inside = [c for c in S["details"] if b[0] <= c[0] <= b[2] and b[1] + 0.05 <= c[1] <= b[3] - 0.05] or \
        [((b[0] + b[2]) / 2, (b[1] + b[3]) / 2)]
    base = _records(res, shot, "base", True, threads)
    tiles = []
    for v in variants:
        recs = _records(res, shot, v, True, threads)
        if not recs or not os.path.exists(os.path.join(ROOT, recs[0]["path"])):
            continue
        full = _load(os.path.join(ROOT, recs[0]["path"]))
        tile = Image.fromarray(_crop_centre(full, inside[0], crop).astype(np.uint8))
        _label(tile, v)
        if base:
            _label(tile, "trace x%.2f" % (recs[0]["trace_cpu"] / max(base[0]["trace_cpu"], 1e-6)), pos=(4, 24))
        tiles.append(tile)
    if not tiles:
        return None
    n = min(len(tiles), 5)
    rows = (len(tiles) + n - 1) // n
    sheet = Image.new("RGB", (n * crop + (n - 1) * 6, rows * crop + (rows - 1) * 6), (18, 18, 22))
    for i, t in enumerate(tiles):
        sheet.paste(t, ((i % n) * (crop + 6), (i // n) * (crop + 6)))
    path = os.path.join(TEST, "econ_%s_%s.png" % (name, shot))
    sheet.save(path)
    return path


def report(verbose=True):
    """Everything that was measured: prints the tables, writes the sheets (out/test/econ_*.png) and
    out/test/econ_raw/summary.json; returns the summary dict."""
    res = load_results()
    out = dict(shots={}, sheets=[], sync={}, threads={})
    say = print if verbose else (lambda *a, **k: None)

    # ---- sync
    rows = [r for r in res.values() if r.get("kind") == "sync"]
    for shot in SHOTS:
        mine = sorted([r for r in rows if r["shot"] == shot], key=lambda r: (r["persistent"], r["index"]))
        if not mine:
            continue
        say("\nSYNC %s (%d faces, %d objects, lights on %d of %d): per frame, seconds" % (
            shot, mine[0]["faces"], mine[0]["objects"], mine[0]["lights_on"], mine[0]["lights"]))
        say("  persistent  frame  goto  fingerprint  sync(wall)  sync(cpu)  bvh   images loaded")
        for r in mine:
            say("  %-10s  %5d  %.2f  %.2f         %.2f        %.2f       %.2f  %d" % (
                "on" if r["persistent"] else "off", r["frame"], r["goto"], r["fingerprint"], r["sync_wall"],
                r["sync_cpu"], r["bvh"], r["loaded_images"]))
        off = [r["sync_cpu"] for r in mine if not r["persistent"]]
        on = [r["sync_cpu"] for r in mine if r["persistent"]][1:]
        out["sync"][shot] = dict(off=sum(off) / max(1, len(off)), on=sum(on) / max(1, len(on)),
                                 goto=sum(r["goto"] for r in mine) / len(mine),
                                 fingerprint=sorted(r["fingerprint"] for r in mine)[len(mine) // 2])

    # ---- full frames
    for shot in SHOTS:
        base = _records(res, shot, "base", False, None)
        if not base:
            continue
        b = base[0]
        S = out["shots"].setdefault(shot, {})
        S["full"] = {}
        say("\nFULL FRAMES %s (%s; lights on %d of %d; load %.1f)" % (shot, SHOTS[shot]["what"], b["lights_on"],
                                                                     b["lights"], b["load"]))
        say("  variant       res        spp  sync   trace cpu-s  comp   save   idle-4-thread s   vs base   h per 1440 fr")
        for v in VARIANTS:
            recs = _records(res, shot, v, False, None)
            if not recs:
                continue
            r = recs[0]
            idle = idle_seconds(r)
            S["full"][v] = dict(res=r["res"], samples=r["samples"], sync=r["sync_cpu"], trace_cpu=r["trace_cpu"],
                                comp=r["comp_cpu"], save=r["save"], idle=idle, rel=idle / idle_seconds(b),
                                hours=project(idle), wall=r["wall"], load=r["load"])
            say("  %-12s  %4dx%-4d  %3d  %.2f   %7.1f      %.2f   %.2f   %6.1f            x%.2f     %.1f" % (
                v, r["res"][0], r["res"][1], r["samples"], r["sync_cpu"], r["trace_cpu"], r["comp_cpu"], r["save"],
                idle, idle / idle_seconds(b), project(idle)))

    # ---- border sweeps
    for shot in SHOTS:
        base = _records(res, shot, "base", True)
        if not base:
            continue
        S = out["shots"].setdefault(shot, {})
        S["border"] = {}
        box = _inset(SHOTS[shot]["border"])
        base_paths = [os.path.join(ROOT, r["path"]) for r in base if os.path.exists(os.path.join(ROOT, r["path"]))]
        ref = None
        if len(base_paths) >= 2:
            _st, _sig, ref = temporal_sigma(base_paths, box)
        say("\nBORDER REGION %s: trace CPU seconds (mean over seeds), relative to base; error = RMS difference of one "
            "render to the mean of the base seeds, delivered size" % shot)
        btrace = sum(r["trace_cpu"] for r in base) / len(base)
        for v in VARIANTS:
            recs = _records(res, shot, v, True)
            if not recs:
                continue
            tr = sum(r["trace_cpu"] for r in recs) / len(recs)
            row = dict(trace_cpu=tr, rel=tr / btrace, comp=sum(r["comp_cpu"] for r in recs) / len(recs), n=len(recs))
            p0 = os.path.join(ROOT, recs[0]["path"])
            if ref is not None and os.path.exists(p0):
                row["rms_to_base_mean"] = error_to(ref, p0, box)
            S["border"][v] = row
            say("  %-12s n=%d  trace %6.1f  x%.2f   comp %.2f   rms %s" % (
                v, len(recs), tr, tr / btrace, row["comp"],
                "%.2f" % row["rms_to_base_mean"] if "rms_to_base_mean" in row else "-"))
        # paired fresh variants (their own base in the same process)
        for v in VARIANTS:
            if not VARIANTS[v]["fresh"]:
                continue
            pair = _records(res, shot, "base", True, tag="pair_" + v)
            mine = _records(res, shot, v, True)
            if pair and mine:
                S["border"][v]["rel_pair"] = mine[0]["trace_cpu"] / pair[0]["trace_cpu"]
                S["border"][v]["sync"] = mine[0]["sync_cpu"]
                say("  %-12s against the base of its own process: trace x%.2f (sync %.2f s)" % (
                    v, S["border"][v]["rel_pair"], mine[0]["sync_cpu"]))

    # ---- threads
    for shot in SHOTS:
        rows = {}
        for t in (1, 2, 3, 4):
            recs = _records(res, shot, "base", True, threads=t)
            if recs:
                rows[t] = recs[0]
        if len(rows) >= 2:
            say("\nTHREADS %s (border region, base): CPU seconds of the trace by thread count" % shot)
            for t, r in sorted(rows.items()):
                say("  %d threads: trace %.1f cpu-s, %.1f wall (load %.1f)" % (t, r["trace_cpu"], r["trace_wall"], r["load"]))
            out["threads"][shot] = {t: r["trace_cpu"] for t, r in rows.items()}

    # ---- temporal noise
    for shot in SHOTS:
        names = [v for v in VARIANTS if len(_records(res, shot, v, True)) >= 3]
        if not names:
            continue
        path, stats = sheet_temporal(shot, names, res=res)
        box = _inset(SHOTS[shot]["border"])
        S = out["shots"].setdefault(shot, {})
        S["temporal"] = stats
        if path:
            out["sheets"].append(path)
        say("\nTEMPORAL NOISE %s: sigma over the seeds per pixel, 8-bit levels, as delivered (1080x1920); phone = the "
            "same at 360x640" % shot)
        say("  variant       n   mean   median  p99    flat mean  flat p99   pair mean  pair p99  >6 lv   phone mean  phone p99")
        for v in names:
            st = stats.get(v)
            if not st:
                continue
            recs = _records(res, shot, v, True)
            paths = [os.path.join(ROOT, r["path"]) for r in recs]
            ph, _s, _m = temporal_sigma(paths, box, PHONE)
            st["phone_mean"], st["phone_p99"] = ph["mean"], ph["p99"]
            say("  %-12s  %d   %.2f   %.2f    %5.2f  %.2f       %5.2f      %.2f       %5.2f     %4.1f%%   %.2f        %.2f" % (
                v, st["n"], st["mean"], st["median"], st["p99"], st["flat_mean"], st["flat_p99"], st["pair_mean"],
                st["pair_p99"], 100 * st["over6"], ph["mean"], ph["p99"]))

    # ---- sheets
    for shot in SHOTS:
        for name, vs in (("res", ("base", "r600", "r540")), ("samples", ("base", "s16", "s12", "s8")),
                         ("final", ("base", SAFE, RECOMMENDED)),
                         ("combo", ("base", "r600s16", "r540s16", "r540s12"))):
            fresh = all(_records(res, shot, v, False, None, tag="fr") or (VARIANTS[v]["samples"] or FINAL_SAMPLES) == FINAL_SAMPLES
                        or shot in ("night", "sun", "face") and v in (RECOMMENDED, SAFE) for v in vs)
            p = sheet_compare(shot, vs, name, res=res, note=None if fresh else AFTER_24)
            if p:
                out["sheets"].append(p)
        for name, vs in (("denoise", ("base", "dn_off", "dn_pf_fast", "dn_pf_none", "dn_q_fast", "dn_q_high",
                                      "dn_rgb_albedo", "dn_rgb")),
                         ("adaptive", ("base", "ad_off", "ad_005", "ad_02", "ad_min4", "ad_min12", "s16_min8")),
                         ("paths", ("base", "lst05", "tb8", "tb4", "gi_full", "diff1", "gloss0", "clamp_d", "lt_off",
                                    "nomb", "bvh2", "bvh_static", "spatial", "glare_med"))):
            p = sheet_border(shot, vs, name, res=res)
            if p:
                out["sheets"].append(p)
    os.makedirs(RAW, exist_ok=True)
    with open(os.path.join(RAW, "summary.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1)
    say("\nsheets:")
    for p in out["sheets"]:
        say("  " + p)
    return out


# ----------------------------------------------------------------------------------------------------------------
# second pass: quality (what is indistinguishable on a phone once the film is upscaled, captioned and encoded)
# ----------------------------------------------------------------------------------------------------------------

# A is the 720x1280 / 16-sample job that was the FIRST render of its process ('s16f'): the picture render.py would
# make. 'A+' is the 16-sample job that followed a 24-sample job in the same Blender session ('s16'): it holds the
# first 16 samples of the reference's own sequence and is closer to REF than a film frame would be (see FINDINGS,
# 'determinism'); it is kept as a probe only. Cost and two-seed noise of setting A are stored under 's16'.
CANDIDATES = (("REF", "base"), ("A", "s16f"), ("B", "r640s16"), ("C", "r600s16"), ("D", "r540"), ("E", "r540s16"))
PROBES = (("F", "r540s12"), ("G", "r480s16"), ("H", "r540s16_fw"), ("A+", "s16"))
LETTER = dict((v, k) for k, v in CANDIDATES + PROBES)


def _letter(v):
    """Letter of a variant in the tables: 'REF', 'A' .. 'H' ('s16' and 's16f' are both setting A)."""
    return "REF" if v == "base" else "A" if v in ("s16", "s16f") else LETTER.get(v, v)

PHONE_SIZE = (540, 960)                  # "phone size" of the brief: the delivered frame at half size
CROP = 224                               # side of the 1:1 crops of the delivered 1080x1920 frame
UPSCALES = ("lanczos", "bicubic", "lanczos_usm_mild", "lanczos_usm", "nn_lanczos", "mix", "nearest")
SEQ_SHOTS = ("night", "hall", "far")     # the temporal study: a nearly locked camera (a 0.3-block drift in 2 s,
                                         #   handheld 0.01), a dolly along the counter, and the far figure (handheld)
# still regions of the temporal study (fractions from the top left): dark and defocused parts of each shot
SEQ_BOXES = {
    "night": dict(sky=(0.30, 0.02, 0.95, 0.20), dark_post=(0.00, 0.50, 0.12, 0.60), far_houses=(0.80, 0.52, 1.00, 0.61),
                  shadow_ground=(0.30, 0.86, 0.95, 0.99)),
    "hall": dict(bars_defocused=(0.10, 0.02, 0.70, 0.18), wall=(0.72, 0.36, 0.98, 0.60), dark_counter=(0.02, 0.73, 0.40, 0.84),
                 chest_blur=(0.05, 0.86, 0.95, 0.99)),
    "far": dict(figures=(0.30, 0.475, 0.63, 0.58), sky=(0.05, 0.02, 0.95, 0.20), ground=(0.05, 0.80, 0.95, 0.99)),
}
ACCEPTED_FLAT = 0.9                      # temporal noise in flat areas that the finished films were accepted with
ACCEPTED_P99 = 4.4                       #   (levels of 255) and the 99th percentile once accepted for a grassy foreground
                                         #   (tools/noise_check on another frame; not reproducible on these shots)


def ref_path(shot, frame=None):
    """The reference picture of a shot's frame: the finished film's own final frame on disk (720x1280, 24 samples,
    seed 0; a 'base' job is bit-identical to it, which the self-test checks), else the 'base' job."""
    S = SHOTS[shot]
    frame = S["frame"] if frame is None else frame
    p = os.path.join(ROOT, "out", "frames", S["film"], "f_%04d.png" % frame)
    if os.path.exists(p):
        return p
    rec = find_job(shot, "base", 0, False, "" if frame == S["frame"] else seq_tag(frame))
    return os.path.join(ROOT, rec["path"]) if rec else None


def variant_path(shot, variant, frame=None, seed=0, animated=False):
    """PNG of one variant of one frame of a shot (None when it was not rendered). variant 'base' with seed 0 is
    the reference; animated=True: the job whose noise seed is the frame number."""
    S = SHOTS[shot]
    frame = S["frame"] if frame is None else frame
    if variant == "base" and seed == 0 and not animated:
        return ref_path(shot, frame)
    rec = None
    if frame == S["frame"] and not animated:
        # a still rendered in a 16-sample-only process ('fr') before one that may have followed a 24-sample job
        rec = find_job(shot, variant, seed, False, "fr") or find_job(shot, variant, seed, False)
    if rec is None:
        rec = find_job(shot, variant, frame if animated else seed, False, seq_tag(frame, animated))
    return os.path.join(ROOT, rec["path"]) if rec else None


def deliver(src, how="lanczos", size=DELIVERY):
    """A rendered frame as delivered, 1080x1920 RGB. 'lanczos' is engine.post.upscale itself (what the encoder does
    today); the other filters are the alternatives that were tested: 'bicubic', 'nearest', 'nn_lanczos' (nearest x4,
    then Lanczos down: square texels with softened steps), 'mix' (half nearest, half Lanczos), 'lanczos_usm'
    (Lanczos, then an unsharp mask of radius 1.5 px, 60 %) and 'lanczos_usm_mild' (radius 1.0 px, 35 %)."""
    from PIL import Image, ImageFilter

    from engine import post

    im = Image.open(src) if isinstance(src, str) else src
    im = im.convert("RGB")
    size = tuple(size)
    if im.size == size:
        return im
    if how == "lanczos":
        return post.upscale(im, size)
    if how == "bicubic":
        return im.resize(size, Image.BICUBIC)
    if how == "nearest":
        return im.resize(size, Image.NEAREST)
    if how == "nn_lanczos":
        return im.resize((im.size[0] * 4, im.size[1] * 4), Image.NEAREST).resize(size, Image.LANCZOS)
    if how == "mix":
        return Image.blend(im.resize(size, Image.NEAREST), im.resize(size, Image.LANCZOS), 0.5)
    if how == "lanczos_usm":
        return im.resize(size, Image.LANCZOS).filter(ImageFilter.UnsharpMask(radius=1.5, percent=60, threshold=0))
    if how == "lanczos_usm_mild":
        return im.resize(size, Image.LANCZOS).filter(ImageFilter.UnsharpMask(radius=1.0, percent=35, threshold=0))
    raise ValueError(how)


def to_phone(img):
    """A delivered frame at phone size (540x960, Lanczos)."""
    from PIL import Image

    return img.resize(PHONE_SIZE, Image.LANCZOS)


def luma(arr):
    """BT.709 luma of an HxWx3 array of 8-bit levels (float32)."""
    import numpy as np

    a = np.asarray(arr, dtype=np.float32)
    return a[..., 0] * 0.2126 + a[..., 1] * 0.7152 + a[..., 2] * 0.0722


def psnr(a, b):
    """Peak signal-to-noise ratio in dB of two pictures in 8-bit levels (99 = identical)."""
    import numpy as np

    mse = float(((np.asarray(a, dtype=np.float64) - np.asarray(b, dtype=np.float64)) ** 2).mean())
    return 99.0 if mse < 1e-10 else 10.0 * math.log10(255.0 ** 2 / mse)


def _box(x, k):
    """Mean over every k x k window of a 2-D array (valid part), by cumulative sums."""
    import numpy as np

    c = np.cumsum(np.cumsum(np.pad(np.asarray(x, dtype=np.float64), ((1, 0), (1, 0))), axis=0), axis=1)
    return (c[k:, k:] - c[:-k, k:] - c[k:, :-k] + c[:-k, :-k]) / float(k * k)


def ssim(a, b, k=8):
    """Mean structural similarity of two luma pictures in 8-bit levels (Wang et al. 2004, uniform 8x8 windows)."""
    import numpy as np

    a = np.asarray(a, dtype=np.float64)
    b = np.asarray(b, dtype=np.float64)
    c1, c2 = (0.01 * 255) ** 2, (0.03 * 255) ** 2
    ma, mb = _box(a, k), _box(b, k)
    va, vb, cov = _box(a * a, k) - ma * ma, _box(b * b, k) - mb * mb, _box(a * b, k) - ma * mb
    s = ((2 * ma * mb + c1) * (2 * cov + c2)) / ((ma * ma + mb * mb + c1) * (va + vb + c2))
    return float(s.mean())


def acutance(lum):
    """Mean gradient magnitude of a luma picture (levels per pixel): falls when a picture gets softer."""
    import numpy as np

    gy, gx = np.gradient(np.asarray(lum, dtype=np.float32))
    return float(np.hypot(gx, gy).mean())


def _crop_box(centre, size=CROP, frame=DELIVERY):
    """(x0, y0, x1, y1) pixels of a size x size window around a centre given in fractions, kept inside the frame."""
    w, h = frame
    x = int(min(max(centre[0] * w - size / 2, 0), w - size))
    y = int(min(max(centre[1] * h - size / 2, 0), h - size))
    return x, y, x + size, y + size


def compare(ref_img, img):
    """Numbers of one delivered frame against the reference frame (both 1080x1920 PIL): SSIM / PSNR on luma of the
    whole frame and at phone size, largest phone-size tile difference; no crops (see quality())."""
    import numpy as np

    a, b = luma(np.asarray(ref_img)), luma(np.asarray(img))
    pa, pb = luma(np.asarray(to_phone(ref_img))), luma(np.asarray(to_phone(img)))
    d = np.abs(pa - pb)
    return dict(ssim=ssim(a, b), psnr=psnr(a, b), phone_ssim=ssim(pa, pb), phone_psnr=psnr(pa, pb),
                phone_mean=float(d.mean()), phone_p99=float(np.percentile(d, 99)), sharp=acutance(b) / max(acutance(a), 1e-6))


def quality(shot, how="lanczos", variants=None):
    """{letter: numbers} for every rendered candidate of a shot against the reference, as delivered with the
    upscale `how`: SSIM / PSNR on luma (whole frame, phone size, each of the five crops), relative acutance, the
    cost of the job. 'REF2' = the reference setting with another noise seed (the noise floor: what two renders of
    the current final differ by)."""
    import numpy as np

    rp = ref_path(shot)
    if rp is None:
        return {}
    ref = deliver(rp)
    ref_l = luma(np.asarray(ref))
    cost = cost_table().get(shot, {})
    out = {}
    todo = [(k, v, 0) for k, v in CANDIDATES[1:] + PROBES] + [("REF2", "base", 1), ("E2", "r540s16", 1)]
    for letter, v, seed in todo:
        if variants is not None and letter not in variants:
            continue
        p = variant_path(shot, v, seed=seed)
        if p is None:
            continue
        img = deliver(p, how)
        row = compare(ref, img)
        lum = luma(np.asarray(img))
        row["crops"] = {}
        for name in CROP_NAMES:
            x0, y0, x1, y1 = _crop_box(CROPS[shot][name])
            ca, cb = ref_l[y0:y1, x0:x1], lum[y0:y1, x0:x1]
            row["crops"][name] = dict(ssim=ssim(ca, cb), psnr=psnr(ca, cb), sharp=acutance(cb) / max(acutance(ca), 1e-6))
        rec = find_job(shot, v, seed, False, "fr") or find_job(shot, v, seed, False)
        if rec is not None:
            row.update(variant=v, res=rec["res"], samples=rec["samples"], trace_cpu=rec["trace_cpu"],
                       cpu=rec["sync_cpu"] + rec["trace_cpu"] + rec["comp_cpu"] + rec["save"], idle=idle_seconds(rec),
                       load=rec["load"], threads=rec["threads"])
        c = cost.get(SAME_SETTING.get(v, v))
        if c:                                    # the cost as the FINDINGS table has it: every job of the setting
            row.update(cpu=c["cpu"], rel=c["rel"], load=c["load"], jobs=c["n"])
        out[letter] = row
    return out


def _text(text, scale=2):
    from engine import captions as cap

    return cap.label(text, scale=scale)


def _tile_with_caption(tile, lines, width=None, bar=22):
    """A picture with text lines in a dark strip UNDER it (nothing is drawn over the pixels that are judged)."""
    from PIL import Image

    w = width or tile.size[0]
    out = Image.new("RGB", (w, tile.size[1] + bar * len(lines)), (18, 18, 22))
    out.paste(tile, (0, 0))
    for i, t in enumerate(lines):
        lab = _text(t)
        out.paste(lab, (2, tile.size[1] + 3 + i * bar), lab)
    return out


def _grid(rows, gap=6, bg=(18, 18, 22)):
    """Paste a list of rows (lists of PIL images) into one sheet."""
    from PIL import Image

    hs = [max(t.size[1] for t in r) for r in rows]
    ws = [sum(t.size[0] for t in r) + gap * (len(r) - 1) for r in rows]
    sheet = Image.new("RGB", (max(ws), sum(hs) + gap * (len(rows) - 1)), bg)
    y = 0
    for r, h in zip(rows, hs):
        x = 0
        for t in r:
            sheet.paste(t, (x, y))
            x += t.size[0] + gap
        y += h + gap
    return sheet


def _side_label(lines, height, width=176):
    from PIL import Image

    out = Image.new("RGB", (width, height), (18, 18, 22))
    for i, t in enumerate(lines):
        lab = _text(t)
        out.paste(lab, (4, 6 + i * 22), lab)
    return out


def sheet_crops(shot, letters=("REF", "A", "B", "C", "D", "E"), how="lanczos", name="crops", q=None):
    """out/test/econ_<name>_<shot>.png: one row per candidate, the five 1:1 crops of the delivered 1080x1920 frame
    (face, fine texels, thin thing, defocused background, dark area), SSIM and PSNR of each crop under it."""
    q = quality(shot, how) if q is None else q
    lookup = dict(CANDIDATES + PROBES)
    cost = cost_table().get(shot, {})
    rows = []
    for letter in letters:
        v = lookup[letter]
        p = variant_path(shot, v)
        if p is None:
            continue
        img = deliver(p, how)
        row = q.get(letter, {})
        res = VARIANTS[v]["res"] or FINAL_RES
        side = ["%s  %s" % (letter, shot), "%dx%d" % tuple(res), "%d samples" % (VARIANTS[v]["samples"] or FINAL_SAMPLES)]
        c = cost.get(SAME_SETTING.get(v, v))
        if c:                                    # the numbers of the FINDINGS table (every job of the setting)
            side.append("%.0f cpu-s x%.2f" % (c["cpu"], c["rel"]) if c.get("rel") else "%.0f cpu-s" % c["cpu"])
        if row:
            side += ["frame:", "ssim %.4f" % row["ssim"], "%.1f dB" % row["psnr"], "phone:", "ssim %.4f" % row["phone_ssim"],
                     "%.1f dB" % row["phone_psnr"]]
        tiles = [_side_label(side, CROP + 22)]
        for cn in CROP_NAMES:
            tile = img.crop(_crop_box(CROPS[shot][cn]))
            c = row.get("crops", {}).get(cn)
            tiles.append(_tile_with_caption(tile, ["%s %s" % (cn, ("%.3f %.1fdB" % (c["ssim"], c["psnr"])) if c else "reference")]))
        rows.append(tiles)
    if not rows:
        return None
    path = os.path.join(TEST, "econ_%s_%s.png" % (name, shot))
    _grid(rows).save(path)
    return path


def sheet_zoom(shot, crop, letters=("REF", "C", "E"), zoom=3, size=120, how="lanczos", name="zoom", tag=""):
    """out/test/econ_<name>_<shot>_<crop>.png: a size x size window of the delivered frame, enlarged `zoom` times
    with nearest neighbour (to judge texel edges and stair-steps), one tile per candidate."""
    from PIL import Image

    lookup = dict(CANDIDATES + PROBES)
    tiles = []
    for letter in letters:
        how_l = how
        if ":" in letter:                                  # 'E:nearest' = candidate E with another upscale
            letter, how_l = letter.split(":")
        p = variant_path(shot, lookup[letter])
        if p is None:
            continue
        centre = CROPS[shot][crop] if isinstance(crop, str) else crop
        t = deliver(p, how_l).crop(_crop_box(centre, size)).resize((size * zoom, size * zoom), Image.NEAREST)
        tiles.append(_tile_with_caption(t, ["%s %s" % (letter, how_l if how_l != "lanczos" else "")]))
    if not tiles:
        return None
    path = os.path.join(TEST, "econ_%s_%s_%s.png" % (name, shot, crop if isinstance(crop, str) else tag or "at"))
    per_row = 3 if len(tiles) > 4 else len(tiles)
    _grid([tiles[i:i + per_row] for i in range(0, len(tiles), per_row)]).save(path)
    return path


def sheet_phone(shot, letters=("REF", "C", "E"), name="phone"):
    """out/test/econ_<name>_<shot>.png: the whole delivered frames at phone size (540x960) side by side."""
    lookup = dict(CANDIDATES + PROBES)
    tiles = []
    for letter in letters:
        p = variant_path(shot, lookup[letter])
        if p is None:
            continue
        v = lookup[letter]
        res = VARIANTS[v]["res"] or FINAL_RES
        tiles.append(_tile_with_caption(to_phone(deliver(p)), ["%s %dx%d %dspp" % (letter, res[0], res[1],
                                                                                 VARIANTS[v]["samples"] or FINAL_SAMPLES)]))
    if not tiles:
        return None
    path = os.path.join(TEST, "econ_%s_%s.png" % (name, shot))
    _grid([tiles]).save(path)
    return path


def sheet_upscale(shot, letter="E", name="upscale"):
    """out/test/econ_<name>_<shot>.png: the reference above one candidate delivered with each upscale filter: the
    face, texel, thin and defocus crops at 1:1 and the middle of the thin crop enlarged 3 times; numbers against the
    reference under each tile."""
    import numpy as np
    from PIL import Image

    lookup = dict(CANDIDATES + PROBES)
    p = variant_path(shot, lookup[letter])
    rp = ref_path(shot)
    if p is None or rp is None:
        return None, {}
    ref = deliver(rp)
    ref_l = luma(np.asarray(ref))
    rows, stats = [], {}
    for how in ("ref",) + UPSCALES:
        img = ref if how == "ref" else deliver(p, how)
        lum = luma(np.asarray(img))
        st = None if how == "ref" else compare(ref, img)
        if st:
            stats[how] = st
        side = ["REF 720 lanczos"] if how == "ref" else ["%s %s" % (letter, how), "ssim %.4f" % st["ssim"], "%.1f dB" % st["psnr"],
                                                         "phone %.4f" % st["phone_ssim"], "sharp x%.2f" % st["sharp"]]
        tiles = [_side_label(side, CROP + 22, 200)]
        for cn in ("face", "texels", "thin", "defocus"):
            x0, y0, x1, y1 = _crop_box(CROPS[shot][cn])
            cap_ = cn if how == "ref" else "%s %.3f x%.2f" % (cn, ssim(ref_l[y0:y1, x0:x1], lum[y0:y1, x0:x1]),
                                                             acutance(lum[y0:y1, x0:x1]) / max(acutance(ref_l[y0:y1, x0:x1]), 1e-6))
            tiles.append(_tile_with_caption(img.crop((x0, y0, x1, y1)), [cap_]))
        z = img.crop(_crop_box(CROPS[shot]["thin"], 74)).resize((222, 222), Image.NEAREST)
        tiles.append(_tile_with_caption(z, ["thin x3"]))
        rows.append(tiles)
    path = os.path.join(TEST, "econ_%s_%s.png" % (name, shot))
    _grid(rows).save(path)
    return path, stats


BLIND_KEY = os.path.join(RAW, "blind_key.json")


def sheet_blind(shot, letter, name="blind"):
    """out/test/econ_blind_<shot>_<letter>.png: the reference and one candidate at phone size, unlabelled, in an
    order drawn from os.urandom and stored only in econ_raw/blind_key.json (the judge looks first, reads the key
    afterwards). An existing sheet keeps its order."""
    lookup = dict(CANDIDATES + PROBES)
    p, rp = variant_path(shot, lookup[letter]), ref_path(shot)
    if p is None or rp is None:
        return None
    key = {}
    if os.path.exists(BLIND_KEY):
        with open(BLIND_KEY, encoding="utf-8") as f:
            key = json.load(f)
    k = "%s_%s" % (shot, letter)
    path = os.path.join(TEST, "econ_%s_%s.png" % (name, k))
    if k not in key or not os.path.exists(path):
        key[k] = "left" if os.urandom(1)[0] & 1 else "right"          # where the REFERENCE is
        with open(BLIND_KEY, "w", encoding="utf-8") as f:
            json.dump(key, f, indent=1, sort_keys=True)
    a, b = to_phone(deliver(rp)), to_phone(deliver(p))
    pair = [a, b] if key[k] == "left" else [b, a]
    _grid([pair], gap=0).save(path)
    return path


# ---- temporal: 8 consecutive frames, encoded exactly as engine/post.py encodes a film -----------------------------

def seq_frame_path(shot, variant, frame, animated=False, seed=0):
    """PNG of one frame of a variant's 8-frame sequence (None when it was not rendered). The reference comes from
    the finished film; a 24-sample variant may use the still of the shot's own frame (a second render of it is
    the same picture); a 16-sample variant must have been rendered inside the sequence's own run, because a
    16-sample still that followed a 24-sample job in its Blender session is another noise realisation (see
    FINDINGS, 'determinism'). seed=1: the same frames with the other fixed noise seed (seed_pair)."""
    S = SHOTS[shot]
    if variant == "base" and not animated and not seed:
        return ref_path(shot, frame)
    rec = find_job(shot, variant, frame if animated else int(seed), False, seq_tag(frame, animated))
    if rec is None and not animated and frame == S["frame"] and (VARIANTS[variant]["samples"] or FINAL_SAMPLES) == FINAL_SAMPLES:
        rec = find_job(shot, variant, int(seed), False)
    return os.path.join(ROOT, rec["path"]) if rec else None


def seq_paths(shot, variant, animated=False, seed=0):
    """The 8 PNGs of a variant's sequence, or None while one is missing."""
    out = [seq_frame_path(shot, variant, f, animated, seed) for f in seq_frames(shot)]
    return None if any(p is None for p in out) else out


def seq_name(shot, variant, animated=False, frozen=False, seed=0):
    return "%s_%s%s%s%s" % (shot, variant, "_animseed" if animated else "", "_frozen" if frozen else "",
                            "_seed%d" % seed if seed else "")


def _encode_frames(name, paths, mp4, word="Hello"):
    """Encode a list of PNGs as consecutive frames with engine.post.encode itself (Lanczos to 1080x1920, the
    caption composited after the upscale, H.264 yuv420p crf 16). post.OUT is pointed at out/test/econ_raw/enc for
    the call, so the frames are read from there and nothing of a real film is touched."""
    import shutil

    from engine import post

    film = "_econ_" + name
    old_out = post.OUT
    post.OUT = os.path.join(RAW, "enc")
    try:
        d = post.frames_dir(film)
        os.makedirs(d, exist_ok=True)
        for i, p in enumerate(paths):
            shutil.copyfile(p, post.frame_path(film, i + 1))
        n = len(paths)
        post.write_meta(film, {"fps": 24, "frame_start": 1, "frame_end": n, "captions": [[word, 0.0, n / 24.0]],
                               "signature": "econ", "frames": {str(i + 1): "econ" for i in range(n)}})
        post.encode(film, out_path=mp4)
        for i in range(n):
            os.remove(post.frame_path(film, i + 1))
        os.remove(os.path.join(d, "meta.json"))
        os.rmdir(d)
    finally:
        post.OUT = old_out
    return mp4


def seq_encode(shot, variant, animated=False, frozen=False, word="Hello", paths=None, seed=0):
    """Encode a variant's 8 consecutive frames exactly as a film is encoded -> out/test/econ_seq_<shot>_<variant>.mp4
    (None while frames are missing). frozen=True: frame F eight times (what copying frames with an identical
    fingerprint gives); seed=1: the clip of the other noise seed (..._seed1.mp4)."""
    paths = paths or seq_paths(shot, variant, animated, seed)
    if paths is None:
        return None
    if frozen:
        paths = [paths[3]] * len(paths)
    mp4 = os.path.join(TEST, "econ_seq_%s.mp4" % seq_name(shot, variant, animated, frozen, seed))
    if os.path.exists(mp4) and os.path.getmtime(mp4) > max(os.path.getmtime(p) for p in paths):
        return mp4
    return _encode_frames(seq_name(shot, variant, animated, frozen, seed), paths, mp4, word)


def insta(mp4):
    """An Instagram-like second encode of a clip (ASSUMED, not Instagram's own pipeline: 720x1280, bicubic, x264
    crf 27): what survives of a difference after the platform has had the film."""
    import shutil
    import subprocess

    out = os.path.join(RAW, "insta_" + os.path.basename(mp4))
    if os.path.exists(out) and os.path.getmtime(out) > os.path.getmtime(mp4):
        return out
    subprocess.check_call([shutil.which("ffmpeg"), "-y", "-loglevel", "error", "-i", mp4, "-vf",
                           "scale=720:1280:flags=bicubic", "-c:v", "libx264", "-preset", "medium", "-crf", "27",
                           "-pix_fmt", "yuv420p", "-an", out])
    return out


def decode(mp4):
    """Every frame of a clip as uint8 RGB: N x H x W x 3."""
    import shutil
    import subprocess

    import numpy as np

    info = json.loads(subprocess.check_output([shutil.which("ffprobe"), "-v", "error", "-select_streams", "v:0",
                                               "-show_entries", "stream=width,height", "-of", "json", mp4]))["streams"][0]
    raw = subprocess.check_output([shutil.which("ffmpeg"), "-v", "error", "-i", mp4, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"])
    return np.frombuffer(raw, dtype=np.uint8).reshape(-1, info["height"], info["width"], 3)


def temporal_maps(frames):
    """Per-pixel temporal measures of N consecutive frames (N x H x W x 3, 8-bit): 'sigma' = standard deviation
    over the frames (largest channel); 'noise' = the part of it that is not smooth motion, from second differences
    f[i-1] - 2 f[i] + f[i+1] (sqrt(mean d^2 / 6): white frame-to-frame noise of sigma s gives s, a steady drift
    gives 0); 'pair' = mean over the consecutive pairs of the largest channel difference (tools/noise_check)."""
    import numpy as np

    f = frames.astype(np.float32)
    sigma = f.std(axis=0, ddof=1).max(axis=2)
    d2 = f[:-2] - 2.0 * f[1:-1] + f[2:]
    noise = np.sqrt((d2 ** 2).mean(axis=0) / 6.0).max(axis=2)
    pairs = np.abs(f[1:] - f[:-1]).max(axis=3)                           # (N-1) x H x W
    return dict(sigma=sigma, noise=noise, pair=pairs.mean(axis=0), pairs=pairs)


def flat_mask(frames, grad=2.5, reach=3):
    """Pixels of a clip that are 'still regions' for the noise measure: flat in EVERY frame (luma gradient under
    `grad` levels per pixel everywhere within `reach` pixels, so that a camera drift of a few pixels moves nothing
    visible through them), and outside the caption band."""
    import numpy as np

    from engine import captions as cap

    g = None
    for fr in frames:
        gy, gx = np.gradient(luma(fr))
        m = np.hypot(gx, gy)
        g = m if g is None else np.maximum(g, m)
    k = 2 * reach + 1                                        # box maximum, separable
    pad = np.pad(g, reach, mode="edge")
    g = np.max(np.stack([pad[:, i:i + g.shape[1]] for i in range(k)]), axis=0)
    g = np.max(np.stack([g[i:i + frames.shape[1]] for i in range(k)]), axis=0)
    m = g < grad
    h = m.shape[0]
    m[int(cap.CAPTION_BAND[0] * h) - 8:int(cap.CAPTION_BAND[1] * h) + 8] = False
    return m


def _stats(maps, mask):
    import numpy as np

    if not mask.any():
        return {}
    pr = maps["pairs"][:, mask]
    return dict(sigma=float(maps["sigma"][mask].mean()), sigma_p99=float(np.percentile(maps["sigma"][mask], 99)),
                noise=float(maps["noise"][mask].mean()), noise_p99=float(np.percentile(maps["noise"][mask], 99)),
                pair_mean=float(pr.mean()), pair_p99=float(np.percentile(pr, 99)), over6=float((pr > 6).mean()),
                share=float(mask.mean()))


def temporal(shot, variants, animated=(), frozen=(), platform=False):
    """The temporal study of one shot on ENCODED frames: {name: {'flat': stats, 'all': stats, '<box>': stats,
    'vs_ref': {ssim, psnr, phone_ssim}}} for the reference clip and each variant's clip. The still-region mask is
    taken from the reference clip and used for every variant. platform=True measures after insta()."""
    import numpy as np
    from PIL import Image

    todo = [(v, False, False) for v in variants] + [(v, True, False) for v in animated] + [(v, False, True) for v in frozen]
    clips = {}
    for v, an, fr in todo:
        mp4 = seq_encode(shot, v, an, fr)
        if mp4 is None:
            continue
        clips[seq_name(shot, v, an, fr)[len(shot) + 1:]] = decode(insta(mp4) if platform else mp4)
    if "base" not in clips:
        return {}, {}, None
    ref = clips["base"]
    mask = flat_mask(ref)
    h, w = mask.shape
    band = np.ones_like(mask)
    from engine import captions as cap

    band[int(cap.CAPTION_BAND[0] * h) - 8:int(cap.CAPTION_BAND[1] * h) + 8] = False
    out, maps_all = {}, {}
    for name, fr in clips.items():
        maps = temporal_maps(fr)
        maps_all[name] = (maps, fr)
        row = dict(flat=_stats(maps, mask), all=_stats(maps, band))
        for bn, b in SEQ_BOXES.get(shot, {}).items():
            bm = np.zeros_like(mask)
            bm[int(b[1] * h):int(b[3] * h), int(b[0] * w):int(b[2] * w)] = True
            row[bn] = _stats(maps, bm)
        if name != "base":
            ss, ps, phs = [], [], []
            for i in range(len(fr)):
                a, b = luma(ref[i]), luma(fr[i])
                ss.append(ssim(a, b))
                ps.append(psnr(a, b))
                pa = luma(np.asarray(Image.fromarray(ref[i]).resize((w // 2, h // 2), Image.LANCZOS)))
                pb = luma(np.asarray(Image.fromarray(fr[i]).resize((w // 2, h // 2), Image.LANCZOS)))
                phs.append(ssim(pa, pb))
            row["vs_ref"] = dict(ssim=float(np.mean(ss)), psnr=float(np.mean(ps)), phone_ssim=float(np.mean(phs)))
        out[name] = row
    return out, maps_all, mask


def sheet_seq(shot, variants, animated=(), frozen=(), name="seq", gain=40.0, platform=False):
    """out/test/econ_<name>_<shot>.png: per variant (columns) the 4th encoded frame, and under it the per-pixel
    frame-to-frame noise of the encoded clip x `gain` (white = 255 / gain levels), with the numbers of the still
    regions; returns (path, stats)."""
    import numpy as np
    from PIL import Image

    stats, maps_all, mask = temporal(shot, variants, animated, frozen, platform)
    if not stats:
        return None, stats
    cols = []
    size = (360, 640)
    for nm, (maps, fr) in maps_all.items():
        st = stats[nm]["flat"]
        pic = Image.fromarray(fr[3]).resize(size, Image.LANCZOS)
        heat = Image.fromarray(np.clip(maps["noise"] * gain, 0, 255).astype(np.uint8)).convert("RGB").resize(size, Image.BILINEAR)
        lab = _letter(nm)
        a = _tile_with_caption(pic, ["%s %s" % (lab, nm)])
        b = _tile_with_caption(heat, ["flat noise %.2f p99 %.1f" % (st["noise"], st["noise_p99"]),
                                      "pair %.2f p99 %.1f" % (st["pair_mean"], st["pair_p99"])])
        cols.append((a, b))
    sheet = _grid([[c[0] for c in cols], [c[1] for c in cols]])
    path = os.path.join(TEST, "econ_%s_%s.png" % (name, shot))
    sheet.save(path)
    return path, stats


def sheet_frames(shot, centre, variants=("base", "r600s16", "r540s16"), tag="at", zoom=2, size=150, gain=16.0, n=3):
    """out/test/econ_frames_<shot>_<tag>.png: a size x size window of the ENCODED clips around `centre`, enlarged
    `zoom` times: per variant (rows) `n` consecutive frames, then the difference of each consecutive pair x `gain`
    (what changes from one frame to the next: motion and noise)."""
    import numpy as np
    from PIL import Image

    rows = []
    for v in variants:
        mp4 = seq_encode(shot, v)
        if mp4 is None:
            continue
        fr = decode(mp4)
        x0, y0, x1, y1 = _crop_box(centre, size)
        tiles = []
        for i in range(n):
            t = Image.fromarray(fr[2 + i, y0:y1, x0:x1]).resize((size * zoom, size * zoom), Image.NEAREST)
            tiles.append(_tile_with_caption(t, ["%s f%d" % (_letter(v), seq_frames(shot)[2 + i])]))
        for i in range(n - 1):
            d = np.abs(fr[3 + i, y0:y1, x0:x1].astype(np.float32) - fr[2 + i, y0:y1, x0:x1].astype(np.float32)).max(axis=2)
            t = Image.fromarray(np.clip(d * gain, 0, 255).astype(np.uint8)).convert("RGB").resize((size * zoom, size * zoom), Image.NEAREST)
            tiles.append(_tile_with_caption(t, ["diff x%d mean %.2f" % (gain, float(d.mean()))]))
        rows.append(tiles)
    if not rows:
        return None
    path = os.path.join(TEST, "econ_frames_%s_%s.png" % (shot, tag))
    _grid(rows).save(path)
    return path


def seed_pair(shot, variant, platform=False, encoded=True):
    """The temporal measure in which MOTION CANCELS (a dolly, a handheld drift and a running villager are the same
    in both clips): the same 8 consecutive frames rendered with the fixed noise seeds 0 and 1, each clip encoded
    as a film is, the decoded clips differenced frame by frame. D_i = A_i - B_i holds no picture, only the noise
    of two renders (and, encoded, what x264 made of each). Returns (stats, maps) or None while a clip is missing.
    stats = {region: {...}} for 'all' (the frame outside the caption band), 'flat' (flat in the reference frame),
    'dark' (reference luma under 40) and the SEQ_BOXES of the shot, each with
      frame, frame_p99        mean / 99th percentile of |D_i| (largest channel) over the 8 frames: the noise IN a
                              frame, tools/noise_check's two-seed number;
      temporal, temporal_p99  the same of |D_(i+1) - D_i| / sqrt(2): the noise that CHANGES from one frame to the
                              next. Noise that is new on every frame reads like 'frame'; a pattern that stays where
                              it is (the fixed seed on a still picture) reads 0. This is what boils.
    encoded=False measures the frames as delivered BEFORE the encoder (Lanczos to 1080x1920, no x264): the
    renderer's noise alone. Encoded, every region also has 'codec' = mean |encoded frame - the frame it was
    encoded from| of the seed-0 clip: what x264 at crf 16 itself adds to a frame (in a moving shot more than the
    renderer's noise). The masks come from the REFERENCE clip (base, seed 0), so every setting is measured on the
    same pixels."""
    import numpy as np

    from engine import captions as cap

    codec = None
    if encoded:
        a, b = seq_encode(shot, variant), seq_encode(shot, variant, seed=1)
        ref = seq_encode(shot, "base")
        if a is None or b is None or ref is None:
            return None
        src = seq_paths(shot, variant)
        if platform:
            a, b, ref = insta(a), insta(b), insta(ref)
        R = decode(ref)
        A, B = decode(a).astype(np.int16), decode(b).astype(np.int16)
        if not platform and src is not None:
            codec = np.stack([np.abs(A[i] - np.asarray(deliver(p_)).astype(np.int16)).max(axis=2)
                              for i, p_ in enumerate(src)]).astype(np.float32)
    else:
        pa, pb, pr = seq_paths(shot, variant), seq_paths(shot, variant, seed=1), seq_paths(shot, "base")
        if pa is None or pb is None or pr is None:
            return None
        R = np.stack([np.asarray(deliver(p_)) for p_ in pr])
        A = np.stack([np.asarray(deliver(p_)) for p_ in pa]).astype(np.int16)
        B = np.stack([np.asarray(deliver(p_)) for p_ in pb]).astype(np.int16)
    D = A - B
    del B
    fr = np.abs(D).max(axis=3).astype(np.float32)                                   # N x H x W
    tm = np.abs(D[1:] - D[:-1]).max(axis=3).astype(np.float32) / math.sqrt(2.0)     # (N-1) x H x W
    del D
    n, h, w = fr.shape
    band = np.ones((h, w), dtype=bool)
    band[int(cap.CAPTION_BAND[0] * h) - 8:int(cap.CAPTION_BAND[1] * h) + 8] = False
    lum = np.stack([luma(f) for f in R])
    flat = np.stack([flat_mask(R[i:i + 1]) for i in range(n)])                      # the caption band is out already
    dark = (lum < 40.0) & band[None]
    regions = {"all": np.broadcast_to(band, (n, h, w)), "flat": flat, "dark": dark}
    for bn, bx in SEQ_BOXES.get(shot, {}).items():
        m = np.zeros((n, h, w), dtype=bool)
        m[:, int(bx[1] * h):int(bx[3] * h), int(bx[0] * w):int(bx[2] * w)] = True
        regions[bn] = m
    stats = {}
    for name, m in regions.items():
        mt = m[1:] & m[:-1]
        if not m.any() or not mt.any():
            continue
        vf, vt = fr[m], tm[mt]
        stats[name] = dict(frame=float(vf.mean()), frame_p99=float(np.percentile(vf, 99)), over6=float((vf > 6).mean()),
                           temporal=float(vt.mean()), temporal_p99=float(np.percentile(vt, 99)), share=float(m.mean()))
        if codec is not None:
            stats[name]["codec"] = float(codec[m].mean())
    return stats, dict(frame=fr.mean(axis=0), temporal=tm.mean(axis=0), picture=A[3].astype(np.uint8))


def sheet_pair(shot, variants=("base", "r600s16", "r540s16"), gain=24.0, name="pair"):
    """out/test/econ_pair_<shot>.png: per setting (columns) the 4th encoded frame, under it the two-seed noise IN
    a frame and the two-seed noise that CHANGES between frames (seed_pair), both x `gain`; returns (path, stats)."""
    import numpy as np
    from PIL import Image

    cols, stats = [], {}
    size = (360, 640)
    for v in variants:
        r = seed_pair(shot, v)
        if r is None:
            continue
        st, maps = r
        stats[v] = st
        pic = Image.fromarray(maps["picture"]).resize(size, Image.LANCZOS)
        tiles = [_tile_with_caption(pic, ["%s %s" % (_letter(v), _setting(v))])]
        for key, what in (("frame", "in a frame"), ("temporal", "changing")):
            heat = Image.fromarray(np.clip(maps[key] * gain, 0, 255).astype(np.uint8)).convert("RGB").resize(size, Image.BILINEAR)
            tiles.append(_tile_with_caption(heat, [
                "%s: all %.2f p99 %.1f" % (what, st["all"][key], st["all"][key + "_p99"]),
                "flat %.2f  dark %.2f" % (st.get("flat", {}).get(key, 0.0), st.get("dark", {}).get(key, 0.0))]))
        cols.append(tiles)
    if not cols:
        return None, stats
    path = os.path.join(TEST, "econ_%s_%s.png" % (name, shot))
    _grid([[c[i] for c in cols] for i in range(3)]).save(path)
    return path, stats


def boil(shot, variant, word="Hello"):
    """tools/noise_check on ENCODED frames: the same frame rendered with noise seeds 0 and 1, shown alternately for
    8 frames and encoded as post.py encodes a film; nothing moves, so every frame-to-frame difference is noise that
    survived the denoiser, the upscale and x264. Returns (stats, difference map, decoded frames) or None; stats:
    'pair_mean' / 'pair_p99' / 'over6' = noise_check's numbers over the whole frame outside the caption band,
    'flat_mean' / 'flat_p99' = the same in flat areas, 'sigma_flat' = pair difference / sqrt(2) there."""
    import numpy as np

    a, b = variant_path(shot, variant, seed=0), variant_path(shot, variant, seed=1)
    if a is None or b is None:
        return None
    name = "%s_%s_boil" % (shot, variant)
    mp4 = os.path.join(TEST, "econ_seq_%s.mp4" % name)
    if not (os.path.exists(mp4) and os.path.getmtime(mp4) > max(os.path.getmtime(a), os.path.getmtime(b))):
        _encode_frames(name, [a, b] * 4, mp4, word)
    fr = decode(mp4)
    maps = temporal_maps(fr)
    flat = flat_mask(fr[:1])
    h = flat.shape[0]
    from engine import captions as cap

    band = np.ones_like(flat)
    band[int(cap.CAPTION_BAND[0] * h) - 8:int(cap.CAPTION_BAND[1] * h) + 8] = False
    pr = maps["pairs"]
    st = dict(pair_mean=float(pr[:, band].mean()), pair_p99=float(np.percentile(pr[:, band], 99)),
              over6=float((pr[:, band] > 6).mean()), flat_mean=float(pr[:, flat].mean()),
              flat_p99=float(np.percentile(pr[:, flat], 99)), sigma_flat=float(pr[:, flat].mean() / math.sqrt(2.0)),
              flat_share=float(flat.mean()))
    lum = luma(fr[0])
    dark = band & (lum < 40.0)
    if dark.any():
        st.update(dark_mean=float(pr[:, dark].mean()), dark_p99=float(np.percentile(pr[:, dark], 99)),
                  dark_share=float(dark.mean()))
    for cn in CROP_NAMES:
        x0, y0, x1, y1 = _crop_box(CROPS[shot][cn])
        c = pr[:, y0:y1, x0:x1]
        st["crop_" + cn] = [float(c.mean()), float(np.percentile(c, 99))]
    # the same before the encoder: tools/noise_check's own numbers on the PNGs as rendered ('raw'), and on the
    # frames as delivered, upscaled but not encoded ('up')
    from PIL import Image

    with Image.open(a) as ia, Image.open(b) as ib:
        ra, rb = np.asarray(ia.convert("RGB")).astype(np.float32), np.asarray(ib.convert("RGB")).astype(np.float32)
    d = np.abs(ra - rb).max(axis=2)
    st.update(raw_mean=float(d.mean()), raw_p99=float(np.percentile(d, 99)), raw_over6=float((d > 6).mean()))
    ua, ub = np.asarray(deliver(a)).astype(np.float32), np.asarray(deliver(b)).astype(np.float32)
    d = np.abs(ua - ub).max(axis=2)
    st.update(up_mean=float(d.mean()), up_p99=float(np.percentile(d, 99)), up_over6=float((d > 6).mean()),
              up_flat_mean=float(d[flat].mean()), up_flat_p99=float(np.percentile(d[flat], 99)))
    return st, maps["pair"], fr


def sheet_boil(shot, variants=("base", "r600s16", "r540s16"), gain=24.0, name="boil"):
    """out/test/econ_boil_<shot>.png: per variant the encoded frame and the frame-to-frame difference of its
    two-seed clip x `gain`, at a third of the delivered size; returns (path, {variant: stats})."""
    import numpy as np
    from PIL import Image

    cols, stats = [], {}
    size = (360, 640)
    for v in variants:
        r = boil(shot, v)
        if r is None:
            continue
        st, d, fr = r
        stats[v] = st
        pic = Image.fromarray(fr[0]).resize(size, Image.LANCZOS)
        heat = Image.fromarray(np.clip(d * gain, 0, 255).astype(np.uint8)).convert("RGB").resize(size, Image.BILINEAR)
        lab = _letter(v)
        cols.append((_tile_with_caption(pic, ["%s %s" % (lab, v)]),
                     _tile_with_caption(heat, ["pair %.2f p99 %.1f" % (st["pair_mean"], st["pair_p99"]),
                                               "flat %.2f p99 %.1f" % (st["flat_mean"], st["flat_p99"])])))
    if not cols:
        return None, stats
    path = os.path.join(TEST, "econ_%s_%s.png" % (name, shot))
    _grid([[c[0] for c in cols], [c[1] for c in cols]]).save(path)
    return path, stats


# ---- blind trials: many pairs, the judge's answers stored next to the key ------------------------------------------

BLIND2_KEY = os.path.join(RAW, "blind2_key.json")
BLIND2_ANSWERS = os.path.join(RAW, "blind2_answers.json")
BLIND_REGIONS = ("face", "texels", "thin", "defocus")
INSTA_SIZE = (720, 1280)                 # what Instagram delivers a Reel at
BLIND_TILE = (352, 472)


def _read_json(path, default):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return default


def blind_trials(shots=None, letter="E"):
    """Unlabelled pairs of the reference and one candidate, each pair in an order of its own drawn from os.urandom.
    Per shot two sheets: out/test/econ_blind2_<shot>_<letter>_phone.png = the whole delivered frame at phone size
    (540x960), left | right (trial '<shot>_<letter>_phone'); ..._insta.png = four regions (face, texels, thin,
    defocus) of the delivered frame at 720x1280, Instagram's delivery size, 1:1 on the sheet (trials
    '<shot>_<letter>_insta_<region>'; positions: top left, top right, bottom left, bottom right). The side of the
    REFERENCE goes to out/test/econ_raw/blind2_key.json and is printed nowhere; an existing trial keeps its
    order. The judge names the side he takes for the reference with blind_answer() BEFORE blind_tally() reads
    the key. Returns the list of sheets."""
    from PIL import Image

    lookup = dict(CANDIDATES + PROBES)
    key = _read_json(BLIND2_KEY, {})
    sheets = []

    def side(trial):
        if trial not in key:
            key[trial] = "L" if os.urandom(1)[0] & 1 else "R"
        return key[trial]

    for shot in (shots or FIRST_SHOTS + MORE_SHOTS):
        p, rp = variant_path(shot, lookup[letter]), ref_path(shot)
        if p is None or rp is None:
            continue
        ref, cand = deliver(rp), deliver(p)
        a, b = to_phone(ref), to_phone(cand)
        pair = (a, b) if side("%s_%s_phone" % (shot, letter)) == "L" else (b, a)
        sheet = Image.new("RGB", (PHONE_SIZE[0] * 2 + 8, PHONE_SIZE[1]), (60, 0, 60))
        sheet.paste(pair[0], (0, 0))
        sheet.paste(pair[1], (PHONE_SIZE[0] + 8, 0))
        path = os.path.join(TEST, "econ_blind2_%s_%s_phone.png" % (shot, letter))
        sheet.save(path)
        sheets.append(path)
        a, b = ref.resize(INSTA_SIZE, Image.LANCZOS), cand.resize(INSTA_SIZE, Image.LANCZOS)
        tw, th = BLIND_TILE
        sheet = Image.new("RGB", (4 * tw + 2 * 8 + 24, 2 * th + 24), (60, 0, 60))
        for i, cn in enumerate(BLIND_REGIONS):
            cx, cy = CROPS[shot][cn]
            x = int(min(max(cx * INSTA_SIZE[0] - tw / 2, 0), INSTA_SIZE[0] - tw))
            y = int(min(max(cy * INSTA_SIZE[1] - th / 2, 0), INSTA_SIZE[1] - th))
            ta, tb = a.crop((x, y, x + tw, y + th)), b.crop((x, y, x + tw, y + th))
            pair = (ta, tb) if side("%s_%s_insta_%s" % (shot, letter, cn)) == "L" else (tb, ta)
            px, py = (i % 2) * (2 * tw + 8 + 24), (i // 2) * (th + 24)
            sheet.paste(pair[0], (px, py))
            sheet.paste(pair[1], (px + tw + 8, py))
        path = os.path.join(TEST, "econ_blind2_%s_%s_insta.png" % (shot, letter))
        sheet.save(path)
        sheets.append(path)
    os.makedirs(RAW, exist_ok=True)
    with open(BLIND2_KEY, "w", encoding="utf-8") as f:
        json.dump(key, f, indent=1, sort_keys=True)
    return sheets


def blind_answer(answers):
    """Store the judge's answers {trial: 'L' | 'R'} = the side he takes for the REFERENCE (the current final), in
    out/test/econ_raw/blind2_answers.json. A trial that blind_tally() has already scored cannot be answered again.
    The key is not read. Returns the number of answers stored now."""
    data = _read_json(BLIND2_ANSWERS, {"answers": {}, "scored": []})
    n = 0
    for trial, sd in answers.items():
        sd = sd.upper()[:1]
        if sd not in ("L", "R"):
            raise ValueError("answer %r for %s: L or R" % (sd, trial))
        if trial in data["scored"]:
            print("[econ] %s was scored already: answer not changed" % trial)
            continue
        data["answers"][trial] = sd
        n += 1
    os.makedirs(RAW, exist_ok=True)
    with open(BLIND2_ANSWERS, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=1, sort_keys=True)
    return n


def blind_tally(score=True, verbose=True):
    """Compare the stored answers with the key: {'right', 'n', 'by_scale': {...}, 'by_shot': {...}, 'unanswered',
    'limit'}; 'limit' = the number of right answers above which guessing is unlikely (one-sided 95 %: n / 2 +
    1.645 sqrt(n) / 2). score=True marks the answered trials as scored (their answers are final from then on)."""
    key = _read_json(BLIND2_KEY, {})
    data = _read_json(BLIND2_ANSWERS, {"answers": {}, "scored": []})
    out = dict(right=0, n=0, by_scale={}, by_shot={}, unanswered=[], trials={})
    for trial, where in sorted(key.items()):
        ans = data["answers"].get(trial)
        if ans is None:
            out["unanswered"].append(trial)
            continue
        parts = trial.split("_")
        shot, scale = parts[0], parts[2]
        ok = ans == where
        out["trials"][trial] = dict(reference=where, answer=ans, right=ok)
        out["right"] += ok
        out["n"] += 1
        for group, k in (("by_scale", scale), ("by_shot", shot)):
            g = out[group].setdefault(k, [0, 0])
            g[0] += ok
            g[1] += 1
        if score and trial not in data["scored"]:
            data["scored"].append(trial)
    out["limit"] = out["n"] / 2.0 + 1.645 * math.sqrt(out["n"]) / 2.0
    if score and out["n"]:
        with open(BLIND2_ANSWERS, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=1, sort_keys=True)
    if verbose:
        print("[econ] blind trials: the reference named right in %d of %d (guessing: %.0f, more than %.1f would be a "
              "tell); %d not answered" % (out["right"], out["n"], out["n"] / 2.0, out["limit"], len(out["unanswered"])))
        for group in ("by_scale", "by_shot"):
            print("[econ]   " + "  ".join("%s %d/%d" % (k, v[0], v[1]) for k, v in out[group].items()))
    return out


# ---- the far figure: do the eye texels hold from frame to frame? ---------------------------------------------------

# windows around the four heads of the 'far' shot, fractions of the frame from the top left: 20 blocks away
# (near) and 32 blocks away (far), with glowing eyes and with plain white eye texels
FAR_HEADS = dict(near_glow=(0.375, 0.480, 0.440, 0.515), near_plain=(0.562, 0.478, 0.627, 0.512),
                 far_glow=(0.478, 0.485, 0.522, 0.512), far_plain=(0.307, 0.487, 0.351, 0.514))
FAR_BOX = (0.315, 0.475, 0.62, 0.58)     # the four figures (sheet_far)


def far_eyes(variant, seed=0):
    """Per frame of the 'far' sequence, as delivered (1080x1920): {window: [(peak, x, y, area), ...]} for the four
    head windows FAR_HEADS, or None while frames are missing: the brightest luma in the window, the centre of the
    pixels within 10 % of it (the eyes) and how many they are. Eye texels that twinkle show as a peak or an area
    that changes from frame to frame, or a centre that jumps by more than the handheld drift."""
    import numpy as np

    paths = seq_paths("far", variant, seed=seed)
    if paths is None:
        return None
    out = {k: [] for k in FAR_HEADS}
    for p in paths:
        lum = luma(np.asarray(deliver(p)))
        h, w = lum.shape
        for k, bx in FAR_HEADS.items():
            x0, y0, x1, y1 = int(bx[0] * w), int(bx[1] * h), int(bx[2] * w), int(bx[3] * h)
            part = lum[y0:y1, x0:x1]
            ys, xs = np.nonzero(part >= 0.9 * part.max())
            out[k].append((float(part.max()), float(xs.mean() + x0), float(ys.mean() + y0), int(len(xs))))
    return out


def _eye_summary(rows):
    """(lowest peak, highest peak, largest move of the centre between consecutive frames in pixels, smallest area,
    largest area) of one window's far_eyes() rows."""
    step = max(math.hypot(a[1] - b[1], a[2] - b[2]) for a, b in zip(rows, rows[1:])) if len(rows) > 1 else 0.0
    return min(r[0] for r in rows), max(r[0] for r in rows), step, min(r[3] for r in rows), max(r[3] for r in rows)


def sheet_far(variants=("base", "r600s16", "r540s16"), zoom=3, name="far_figure", frames=(3, 4)):
    """out/test/econ_far_figure.png: the window FAR_BOX around the four far figures in two consecutive delivered
    frames, enlarged `zoom` times with nearest neighbour, one row per setting."""
    from PIL import Image

    box = (int(FAR_BOX[0] * DELIVERY[0]), int(FAR_BOX[1] * DELIVERY[1]), int(FAR_BOX[2] * DELIVERY[0]), int(FAR_BOX[3] * DELIVERY[1]))
    rows = []
    for v in variants:
        paths = seq_paths("far", v)
        which = frames
        if paths is None:                                  # no sequence of this setting: its still, once
            p = variant_path("far", v)
            paths, which = ([p] * 8 if p else None), (3,)
        if paths is None:
            continue
        tiles = []
        for i in which:
            t = deliver(paths[i]).crop(box)
            t = t.resize((t.size[0] * zoom, t.size[1] * zoom), Image.NEAREST)
            tiles.append(_tile_with_caption(t, ["%s %s f%d" % (_letter(v), _setting(v), seq_frames("far")[i])]))
        rows.append(tiles)
    if not rows:
        return None
    path = os.path.join(TEST, "econ_%s.png" % name)
    _grid(rows).save(path)
    return path


# ---- tools/noise_check at a film's OWN final quality ---------------------------------------------------------------

def film_noise(film, frames, res=None, samples=None, threads=2):
    """What would boil in a film at ITS OWN final quality: every frame of `frames` rendered twice (noise seeds 0 and
    1) at the resolution and samples the film's build() sets (res / samples override them), as render.py renders
    it. tools/noise_check.py does the same but always at render.FINAL_RES / FINAL_SAMPLES, which is not the quality
    of a film that sets 540x960 at 16 samples. Returns {frame: stats}: 'raw_*' = noise_check's own numbers on the
    PNGs as rendered (mean / 99th percentile / share over 6 levels of the largest channel difference), 'flat' /
    'p99' = the same on the frames as delivered and encoded (engine.post.encode), in flat areas / over the frame,
    and 'ok' = flat <= ACCEPTED_FLAT (0.9, what the finished films were accepted with). Writes
    out/test/econ_noise_<film>_<frame>.png (seed 0 | seed 1 | difference x 12)."""
    import numpy as np
    from PIL import Image

    import render as R

    ses = R.Session(film)
    ses.configure(res, samples, threads, None)
    r, c = ses.scene.render, ses.scene.cycles
    print("[econ] %s at %dx%d, %d samples (adaptive minimum %d)" % (film, r.resolution_x, r.resolution_y, c.samples,
                                                                     c.adaptive_min_samples), flush=True)
    out = {}
    for f in frames:
        paths = []
        for seed in (0, 1):
            c.seed = seed
            path = os.path.join(RAW, "noise_%s_%04d_s%d.png" % (film, f, seed))
            ses.render_frame(f, path)
            paths.append(path)
        c.seed = 0
        with Image.open(paths[0]) as ia, Image.open(paths[1]) as ib:
            a, b = np.asarray(ia.convert("RGB")).astype(np.float32), np.asarray(ib.convert("RGB")).astype(np.float32)
        d = np.abs(a - b).max(axis=2)
        st = dict(res=[r.resolution_x, r.resolution_y], samples=c.samples, raw_mean=float(d.mean()),
                  raw_p99=float(np.percentile(d, 99)), raw_over6=float((d > 6).mean()))
        sheet = np.concatenate([a, b, np.clip(np.repeat(d[..., None], 3, axis=2) * 12.0, 0, 255)], axis=1)
        st["sheet"] = os.path.join(TEST, "econ_noise_%s_%04d.png" % (film, f))
        Image.fromarray(sheet.astype(np.uint8)).save(st["sheet"])
        mp4 = os.path.join(RAW, "noise_%s_%04d.mp4" % (film, f))
        _encode_frames("noise_%s_%04d" % (film, f), paths * 4, mp4)
        fr = decode(mp4)
        pr = temporal_maps(fr)["pairs"]
        flat = flat_mask(fr[:1])
        st.update(flat=float(pr[:, flat].mean()) if flat.any() else 0.0, p99=float(np.percentile(pr, 99)),
                  mean=float(pr.mean()))
        st["ok"] = st["flat"] <= ACCEPTED_FLAT
        out[f] = st
        print("[econ] %s frame %d: as rendered mean %.2f, 99th percentile %.1f, %.2f %% over 6 levels; encoded: mean "
              "%.2f, 99th percentile %.1f, flat areas %.2f (accepted: %.1f) -> %s" % (
                  film, f, st["raw_mean"], st["raw_p99"], 100 * st["raw_over6"], st["mean"], st["p99"], st["flat"],
                  ACCEPTED_FLAT, st["sheet"]), flush=True)
    return out


# ---- what the order of renders inside one Blender session does to a frame -----------------------------------------

def session_order():
    """From the stored stills: what a render loses when the sample count CHANGES inside one Blender session (render.py
    keeps one persistent Cycles session per process). {'shrink': {shot: {variant: {...}}}, 'grow': {...}}.
    shrink: a 16-sample still that followed a 24-sample job (the first pass rendered E and C on dusk and hall that
    way) against the same setting from a 16-sample-only process ('fr'): 'psnr_after' / 'psnr_fresh' = PSNR on luma
    against the reference as delivered, 'pair_after' / 'pair_fresh' = mean largest-channel difference to the
    other noise seed's fresh render (two-seed noise), 'same' = the two hold the same pixels.
    grow: a 24-sample still that followed a 16-sample job ('gr') against the first job of a process: 'same'."""
    import numpy as np

    def arr(path):
        return np.asarray(deliver(path)).astype(np.float32)

    out = dict(shrink={}, grow={})
    res = load_results()
    for shot in ("dusk", "hall"):
        rp = ref_path(shot)
        if rp is None:
            continue
        ref_l = luma(arr(rp))
        for v in ("r540s16", "r600s16"):
            fresh, after = find_job(shot, v, 0, False, "fr", res), res.get(job_key(shot, v, 0, False, 4))
            other = find_job(shot, v, 1, False, "fr", res) or (find_job(shot, v, 1, False, "", res) if v == "r540s16" else None)
            if not (fresh and after and other) or not os.path.exists(os.path.join(ROOT, after["path"])):
                continue
            f, a, o = (arr(os.path.join(ROOT, r["path"])) for r in (fresh, after, other))
            out["shrink"].setdefault(shot, {})[v] = dict(
                psnr_fresh=psnr(ref_l, luma(f)), psnr_after=psnr(ref_l, luma(a)),
                pair_fresh=float(np.abs(f - o).max(axis=2).mean()), pair_after=float(np.abs(a - o).max(axis=2).mean()),
                same=bool((f == a).all()))
    for shot in SHOTS:
        grown, first = find_job(shot, "r540", 0, False, "gr", res), res.get(job_key(shot, "r540", 0, False, 2))
        if grown and first and os.path.exists(os.path.join(ROOT, first["path"])):
            out["grow"][shot] = dict(same=same_pixels(os.path.join(ROOT, grown["path"]), os.path.join(ROOT, first["path"])))
            e_first, e_fr = find_job(shot, "r540s16", 0, False, "gr", res), find_job(shot, "r540s16", 0, False, "fr", res)
            if e_first and e_fr:
                out["grow"][shot]["first_job_same"] = same_pixels(os.path.join(ROOT, e_first["path"]), os.path.join(ROOT, e_fr["path"]))
    return out


# ---- frames that need not be rendered ---------------------------------------------------------------------------

FINISHED = ("bell", "nitwit", "oneword", "poppy_night", "poppy_day")


def identical_frames(films=FINISHED):
    """{film: {'frames', 'same_as_previous', 'same_as_any_earlier', 'camera_same', 'objects_same', 'lights_same'}}
    from the scene fingerprints stored in out/frames/<film>/meta.json (no Blender, no rendering)."""
    out = {}
    for film in films:
        p = os.path.join(ROOT, "out", "frames", film, "meta.json")
        if not os.path.exists(p):
            continue
        with open(p, encoding="utf-8") as f:
            m = json.load(f)
        fr = m.get("frames", {})
        rng = [f for f in range(m["frame_start"], m["frame_end"] + 1) if str(f) in fr]
        seen, again, prev = set(), 0, 0
        parts = dict(c=0, o=0, l=0)
        for i, f in enumerate(rng):
            fp = fr[str(f)]["fp"]
            again += fp in seen
            seen.add(fp)
            if i and rng[i - 1] == f - 1:
                prev += fp == fr[str(f - 1)]["fp"]
                for k in parts:
                    parts[k] += fr[str(f)]["parts"][k] == fr[str(f - 1)]["parts"][k]
        out[film] = dict(frames=len(rng), same_as_previous=prev, same_as_any_earlier=again, camera_same=parts["c"],
                         objects_same=parts["o"], lights_same=parts["l"])
    return out


def same_pixels(a, b):
    """True when two PNGs hold exactly the same pixels."""
    import numpy as np
    from PIL import Image

    with Image.open(a) as ia, Image.open(b) as ib:
        if ia.size != ib.size:
            return False
        return bool((np.asarray(ia.convert("RGB")) == np.asarray(ib.convert("RGB"))).all())


# ---- cost ---------------------------------------------------------------------------------------------------------

def cost_table(tag=None):
    """{shot: {variant: {'n', 'cpu', 'trace', 'serial', 'idle', 'load', 'rel'}}}: mean CPU seconds of a whole frame
    (sync + trace + comp + save) over every full-frame job of that setting (all seeds, the sequence frames too),
    'idle' = serial part + trace / 4 (seconds on four free cores) and 'rel' = cpu relative to the shot's base.
    tag='re' takes only the jobs of the 'remeasure' group (the whole ladder in one process)."""
    res = load_results()
    acc = {}
    for r in res.values():
        if r.get("kind") is not None or r.get("border") or r.get("variant") not in VARIANTS:
            continue
        t = r.get("tag", "")
        if t == "warm" or (tag is not None and t != tag) or (tag is None and t.startswith("pair_")):
            continue
        acc.setdefault(r["shot"], {}).setdefault(SAME_SETTING.get(r["variant"], r["variant"]), []).append(r)
    out = {}
    for shot, by in acc.items():
        out[shot] = {}
        for v, recs in by.items():
            n = float(len(recs))
            serial = sum(r["sync_cpu"] + r["comp_cpu"] + r["save"] for r in recs) / n
            trace = sum(r["trace_cpu"] for r in recs) / n
            out[shot][v] = dict(n=len(recs), cpu=serial + trace, trace=trace, serial=serial, idle=serial + trace / 4.0,
                                load=sum(r["load"] for r in recs) / n)
        base = out[shot].get("base")
        for v, row in out[shot].items():
            row["rel"] = row["cpu"] / base["cpu"] if base else None
    return out


def film_frame_seconds(films=FINISHED):
    """{film: {shot: {'median', 'q1', 'min', 'n'}}}: seconds between the files of consecutive final frames in
    out/frames/<film>/ (what render.py really needed per 720x1280 / 24-sample frame with 4 threads, bookkeeping
    included). 'min' = the single fastest frame of the shot (a best case); 'q1' = the lower quartile, what a frame
    takes while the machine is free (the anchor of projection()); the median includes other agents' load."""
    out = {}
    for film in films:
        p = os.path.join(ROOT, "out", "frames", film, "meta.json")
        if not os.path.exists(p):
            continue
        with open(p, encoding="utf-8") as f:
            m = json.load(f)
        out[film] = {}
        for s in m.get("shots", []):
            ts = []
            for fr in range(s["frame_start"], s["frame_end"] + 1):
                q = os.path.join(ROOT, "out", "frames", film, "f_%04d.png" % fr)
                if os.path.exists(q):
                    ts.append(os.path.getmtime(q))
            d = sorted(b - a for a, b in zip(ts, ts[1:]) if 0.0 < b - a < 120.0)
            if d:
                out[film][s["name"]] = dict(median=d[len(d) // 2], q1=d[len(d) // 4], min=d[0], n=len(d))
    return out


def shot_of(shot):
    """Name of the film shot that a test shot's frame belongs to (from the film's meta.json), or None."""
    S = SHOTS[shot]
    p = os.path.join(ROOT, "out", "frames", S["film"], "meta.json")
    if not os.path.exists(p):
        return None
    with open(p, encoding="utf-8") as f:
        m = json.load(f)
    for s in m.get("shots", []):
        if s["frame_start"] <= S["frame"] <= s["frame_end"]:
            return s["name"]
    return None


# ---- how a film gets the cheaper final setting, and what a global change would do to the finished films ----------

def check_final_per_film(film="poppy_night", res=(540, 960), samples=16, finished=True):
    """Builds, renders nothing, writes nothing. Two questions about render.py, answered on the built scenes:
    (1) a film whose build() sets scene.render.resolution_x / _y and scene.cycles.samples itself: does render.py
        take that as the film's FINAL quality (frames in out/frames/<film>/, stamped with that setting)? Also
        for a film with several skies (a module with SKIES and build(scene, sky=None), e.g. '_multisky_demo':
        every sky's build is checked, 'own_skies'), and 'own_flag_variant' = the directory that passing the same
        setting as --res / --samples would select (a preview: render.variant_of compares with the module constants).
    (2) finished=True: what would changing render.FINAL_RES / FINAL_SAMPLES for everybody do to a finished film's
        frames on disk?
    Returns a dict of the facts (the self-test checks them)."""
    import importlib
    import types

    import render as R
    from engine import post

    real = importlib.import_module("films." + film)
    name = "_econ_final_probe"
    skies = dict(getattr(real, "SKIES", None) or {})

    def setting(out):
        sc = out["film"].scene
        sc.render.resolution_x, sc.render.resolution_y = res          # the three lines a one-minute film adds
        sc.cycles.samples = samples
        return out

    mod = types.ModuleType("films." + name)
    if skies:
        mod.SKIES = skies
        mod.build = lambda scene, sky=None: setting(real.build(scene, sky=sky))
    else:
        mod.build = lambda scene: setting(real.build(scene))
    sys.modules["films." + name] = mod
    out = {}
    try:
        for sky in (list(skies) or [None]):
            ses = R.Session(name, sky=sky) if sky else R.Session(name)
            variant = R.variant_of(None, None, 1, True)               # what `render <film> --frames all` computes
            ses.configure(None, None, R.FINAL_THREADS, None)          # ... and how it configures the session
            r, c = ses.scene.render, ses.scene.cycles
            if sky:
                out.setdefault("own_skies", {})[sky] = dict(settings=ses.settings_key(), min_samples=c.adaptive_min_samples,
                                                            base=list(ses.base[:3]), meta_base=ses.meta().get("base"))
            if "own_variant" in out:
                continue
            out["own_variant"] = variant
            out["own_flag_variant"] = R.variant_of(tuple(res), samples, 1, True)
            out["own_dir"] = os.path.relpath(post.frames_dir(name, variant), ROOT)
            out["own_settings"] = ses.settings_key()
            out["own_min_samples"] = c.adaptive_min_samples
            out["own_res"] = [r.resolution_x, r.resolution_y]
            f = next(fr for fr in range(ses.film.frame_start, ses.film.frame_end + 1) if ses.owns(fr))
            out["own_fp_g"] = ses.fingerprint(f)["parts"]["g"]
    finally:
        sys.modules.pop("films." + name, None)
    if not finished:
        return out
    # (2) the finished film itself, once as it is and once with the module constants changed for everybody
    meta = post.read_meta(film) or {}
    stamped = meta.get("frames", {})
    for label, final in (("asis", (R.FINAL_RES, R.FINAL_SAMPLES)), ("global", (tuple(res), samples))):
        old = R.FINAL_RES, R.FINAL_SAMPLES
        R.FINAL_RES, R.FINAL_SAMPLES = final
        try:
            ses = R.Session(film)
            ses.configure(None, None, R.FINAL_THREADS, None)
            book = R.Stamps(ses, film, R.variant_of(None, None, 1, True))      # reads meta.json; never saved here
            frames = range(ses.film.frame_start, ses.film.frame_end + 1)
            states = {}
            for fr in frames:
                st = book.status(fr)
                states[st] = states.get(st, 0) + 1
            out[label + "_states"] = states
            if label == "asis":
                out["asis_changed_engine_files"] = book.changed_files(
                    [fr for fr in frames if book.status(fr) in ("engine", "engine+scene")])
            out[label + "_settings"] = ses.settings_key()
            f = ses.film.frame_start
            out[label + "_fp_g"] = ses.fingerprint(f)["parts"]["g"]
            out[label + "_stamp_g"] = (stamped.get(str(f)) or {}).get("parts", {}).get("g")
        finally:
            R.FINAL_RES, R.FINAL_SAMPLES = old
    return out


QUALITY_JSON = os.path.join(RAW, "quality.json")


def load_quality():
    """The stored result of quality_report() ({} when there is none)."""
    try:
        with open(QUALITY_JSON, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def quality_report(verbose=True, sheets=True, shots=None):
    """The second pass as tables: cost and likeness of every candidate on every shot, the upscale filters, the
    temporal study on encoded frames, the two-seed boil test and the frames that need no render; writes
    out/test/econ_raw/quality.json and (sheets=True) the sheets out/test/econ_{crops,phone,upscale,seq,boil,blind}_*.png.
    `shots` limits the work to some shots (the stored results of the others are kept). Returns the summary dict."""
    say = print if verbose else (lambda *a, **k: None)
    old = load_quality()
    out = dict(quality=old.get("quality", {}), upscale=old.get("upscale", {}), temporal=old.get("temporal", {}),
               temporal_platform=old.get("temporal_platform", {}), boil=old.get("boil", {}), pair=old.get("pair", {}),
               pair_raw=old.get("pair_raw", {}), far_eyes=old.get("far_eyes", {}),
               sheets=[p for p in old.get("sheets", []) if os.path.exists(p)], identical=identical_frames())
    wanted = [s_ for s_ in SHOTS if shots is None or s_ in shots]

    def keep(path):
        if path and path not in out["sheets"]:
            out["sheets"].append(path)

    for shot in wanted:
        q = quality(shot)
        if not q:
            continue
        out["quality"][shot] = q
        say("\nQUALITY %s (%s): against the film's final frame, as delivered (1080x1920, Lanczos)" % (shot, SHOTS[shot]["what"]))
        say("       setting          cpu-s  load | frame ssim  psnr | phone ssim  psnr  p99 | " +
            "  ".join("%-12s" % c for c in CROP_NAMES) + "  (crop ssim / psnr)")
        for letter, row in q.items():
            say("  %-4s %-16s %5s  %4s | %.4f   %5.1f | %.4f     %5.1f %4.1f | %s" % (
                letter, ("%dx%d@%d" % (row["res"][0], row["res"][1], row["samples"])) if "res" in row else "",
                ("%.0f" % row["cpu"]) if "cpu" in row else "-", ("%.1f" % row["load"]) if "load" in row else "-",
                row["ssim"], row["psnr"], row["phone_ssim"], row["phone_psnr"], row["phone_p99"],
                "  ".join("%.3f %5.1f " % (row["crops"][c]["ssim"], row["crops"][c]["psnr"]) for c in CROP_NAMES)))
        if sheets:
            for p in (sheet_crops(shot, q=q), sheet_phone(shot), sheet_phone(shot, ("A", "B", "D"), name="phone_abd")):
                keep(p)
            if shot in FIRST_SHOTS:                  # the first report's single pairs (they keep their order)
                for letter in ("E", "C", "D"):
                    keep(sheet_blind(shot, letter))
        for letter in ("E",):
            if letter in q:
                if sheets:
                    p, st = sheet_upscale(shot, letter)
                    keep(p)
                else:
                    st = out["upscale"].get(shot, {}).get(letter, {})
                out["upscale"].setdefault(shot, {})[letter] = st
                if st:
                    say("  upscale filters for %s:  " % letter + "   ".join(
                        "%s ssim %.4f phone %.4f sharp x%.2f" % (h, s["ssim"], s["phone_ssim"], s["sharp"]) for h, s in st.items()))
    for shot in [s_ for s_ in SEQ_SHOTS if s_ in wanted]:
        have = [v for _l, v in CANDIDATES + PROBES if seq_paths(shot, v) is not None]
        if "base" not in have or len(have) < 2:
            continue
        anim = [v for _l, v in CANDIDATES + PROBES if seq_paths(shot, v, animated=True) is not None]
        frozen = [v for v in ("base", RECOMMENDED) if v in have]
        for platform in (False, True):
            if sheets:
                path, stats = sheet_seq(shot, have, anim, frozen, name="seq_insta" if platform else "seq", platform=platform)
                keep(path)
            else:
                stats = temporal(shot, have, anim, frozen, platform)[0]
            out["temporal_platform" if platform else "temporal"][shot] = stats
            say("\nTEMPORAL %s frames %d-%d, %s: 8-bit levels in still (flat) regions; noise = frame-to-frame part that "
                "is not smooth motion; pair = consecutive-frame difference (noise_check)" % (
                    shot, seq_frames(shot)[0], seq_frames(shot)[-1],
                    "after an Instagram-like second encode (720x1280, crf 27)" if platform else "encoded as post.py does (crf 16)"))
            boxes = list(SEQ_BOXES.get(shot, {}))
            say("  clip                  flat: sigma  p99 | noise  p99 | pair  p99  >6 lv |  all: noise p99 | " +
                " | ".join("%s noise p99" % b for b in boxes) + " | vs REF ssim psnr phone-ssim")
            for nm, row in stats.items():
                f, a = row["flat"], row["all"]
                vr = row.get("vs_ref")
                say("  %-20s  %5.2f %5.2f | %5.2f %5.2f | %4.2f %5.2f %4.1f%% | %5.2f %5.2f | %s | %s" % (
                    nm, f["sigma"], f["sigma_p99"], f["noise"], f["noise_p99"], f["pair_mean"], f["pair_p99"],
                    100 * f["over6"], a["noise"], a["noise_p99"],
                    " | ".join("%5.2f %5.2f" % (row[b]["noise"], row[b]["noise_p99"]) for b in boxes),
                    ("%.4f %.1f %.4f" % (vr["ssim"], vr["psnr"], vr["phone_ssim"])) if vr else "reference"))
    for shot in [s_ for s_ in SEQ_SHOTS if s_ in wanted]:
        names = [v for v in ("base", "r600s16", "r540s16") if seq_paths(shot, v) and seq_paths(shot, v, seed=1)]
        if "base" not in names:
            continue
        if sheets:
            path, stats = sheet_pair(shot, names)
            keep(path)
        else:
            stats = {v: seed_pair(shot, v)[0] for v in names}
        out["pair"][shot] = stats
        raw = {v: seed_pair(shot, v, encoded=False)[0] for v in names}
        out["pair_raw"][shot] = raw
        regs = [r_ for r_ in ("all", "flat", "dark") + tuple(SEQ_BOXES.get(shot, {})) if r_ in raw["base"]]
        say("\nTWO SEEDS, 8 FRAMES %s, BEFORE THE ENCODER (as delivered, Lanczos to 1080x1920): the renderer's noise alone"
            % shot)
        say("  setting            " + " | ".join("%-27s" % ("%s: in      chg" % r_) for r_ in regs))
        for v, st in raw.items():
            say("  %-4s %-12s  %s" % (_letter(v), v, " | ".join(
                "%4.2f/%4.1f  %4.2f/%4.1f       " % (st[r_]["frame"], st[r_]["frame_p99"], st[r_]["temporal"],
                                                     st[r_]["temporal_p99"]) if r_ in st else "%-27s" % "-" for r_ in regs)))
        say("\nTWO SEEDS, 8 FRAMES %s (frames %d-%d rendered with noise seeds 0 and 1, both clips encoded as post.py "
            "does, differenced frame by frame: motion cancels). in = noise in a frame, chg = noise that changes "
            "from one frame to the next (mean / 99th percentile)" % (shot, seq_frames(shot)[0], seq_frames(shot)[-1]))
        regs = [r_ for r_ in ("all", "flat", "dark") + tuple(SEQ_BOXES.get(shot, {})) if r_ in stats["base"]]
        say("  setting            " + " | ".join("%-27s" % ("%s: in      chg" % r_) for r_ in regs))
        for v, st in stats.items():
            say("  %-4s %-12s  %s" % (_letter(v), v, " | ".join(
                "%4.2f/%4.1f  %4.2f/%4.1f       " % (st[r_]["frame"], st[r_]["frame_p99"], st[r_]["temporal"],
                                                     st[r_]["temporal_p99"]) if r_ in st else "%-27s" % "-" for r_ in regs)))
    if "far" in wanted:
        eyes = {v: far_eyes(v) for v in ("base", "r600s16", "r540s16")}
        eyes = {v: e for v, e in eyes.items() if e}
        if eyes:
            out["far_eyes"] = eyes
            if sheets:
                keep(sheet_far([v for v in ("base", "r600s16", "r540s16") if v in eyes]))
            say("\nFAR FIGURE: the eyes inside each head window per frame, as delivered (peak luma @ centre x,y, area in pixels)")
            for v, e in eyes.items():
                for k, rows in e.items():
                    say("  %-4s %-10s %s" % (_letter(v), k, "  ".join("%3.0f@%.0f,%.0f/%d" % tuple(r_) for r_ in rows)))
    for shot in wanted:
        names = [v for v in ("base", "s16", "r640s16", "r600s16", "r540", "r540s16") if variant_path(shot, v, seed=1)]
        if "base" not in names:
            continue
        if sheets:
            path, stats = sheet_boil(shot, [v for v in ("base", "r600s16", "r540s16") if v in names])
            keep(path)
        stats = {}
        for v in names:
            r = boil(shot, v)
            if r is not None:
                stats[v] = r[0]
        out["boil"][shot] = stats
        say("\nBOIL %s: the same frame with noise seeds 0 and 1 shown alternately, encoded as post.py does; every "
            "frame-to-frame difference is noise (tools/noise_check on encoded frames). Accepted so far: flat mean "
            "<= %.1f, p99 <= %.1f" % (shot, ACCEPTED_FLAT, ACCEPTED_P99))
        say("  setting            as rendered: mean p99 >6 | upscaled: mean p99 flat | ENCODED whole frame: mean  p99  >6 lv "
            "| flat: mean  p99 | dark (<40): mean  p99 | " + " | ".join("%s mean p99" % c for c in CROP_NAMES))
        for v, st in stats.items():
            say("  %-4s %-12s  %4.2f %4.1f %4.2f%% | %4.2f %4.1f %4.2f | %5.2f %5.1f %5.2f%% | %5.2f %5.1f | %5.2f %5.1f | %s" % (
                _letter(v), v, st["raw_mean"], st["raw_p99"], 100 * st["raw_over6"],
                st["up_mean"], st["up_p99"], st["up_flat_mean"], st["pair_mean"], st["pair_p99"], 100 * st["over6"],
                st["flat_mean"], st["flat_p99"], st.get("dark_mean", 0.0), st.get("dark_p99", 0.0),
                " | ".join("%4.2f %4.1f" % tuple(st["crop_" + c]) for c in CROP_NAMES)))
    out["session_order"] = so = session_order()
    say("\nSESSION ORDER: a 16-sample still that followed a 24-sample job in its Blender session against the same "
        "setting from a 16-sample-only process (PSNR to REF; two-seed difference as delivered)")
    for shot, rows in so["shrink"].items():
        for v, r_ in rows.items():
            say("  %-5s %-4s after 24: %.2f dB, pair %.2f | fresh: %.2f dB, pair %.2f" % (
                shot, _letter(v), r_["psnr_after"], r_["pair_after"], r_["psnr_fresh"], r_["pair_fresh"]))
    for shot, r_ in so["grow"].items():
        say("  %-5s 24 samples after 16: same pixels as a fresh process: %s" % (shot, r_["same"]))
    say("\nIDENTICAL FRAMES (scene fingerprints in out/frames/<film>/meta.json):")
    for film, r in out["identical"].items():
        say("  %-12s %3d frames: %d identical to the frame before, %d identical to any earlier frame "
            "(camera unchanged in %d, objects in %d, lights in %d)" % (film, r["frames"], r["same_as_previous"],
                                                                      r["same_as_any_earlier"], r["camera_same"],
                                                                      r["objects_same"], r["lights_same"]))
    os.makedirs(RAW, exist_ok=True)
    with open(QUALITY_JSON, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1)
    if sheets:
        say("\nsheets:")
        for p in out["sheets"]:
            say("  " + p)
    return out


def listing():
    """Print the shots, variants, groups and the number of finished jobs of every group."""
    res = load_results()
    print("shots:")
    for k, s in SHOTS.items():
        print("  %-8s %s frame %d: %s" % (k, s["film"], s["frame"], s["what"]))
    print("groups (jobs done / jobs, per shot):")
    for g, jobs in GROUPS.items():
        total = sum(len(seeds) for _v_, seeds, _b in jobs)
        row = []
        for shot in SHOTS:
            tag = "re" if g == "remeasure" else "fr" if g.startswith("fresh") else "gr" if g == "grow" else ""
            n = sum(find_job(shot, v, s, b, tag, res=res) is not None for v, seeds, b in jobs for s in seeds)
            row.append("%s %d/%d" % (shot, n, total))
        print("  %-14s %s" % (g, "  ".join(row)))
    return 0


LADDER = ("base", "s16", "r640s16", "r600s16", "r540", "r540s16")


def _setting(v):
    r = VARIANTS[v]["res"] or FINAL_RES
    return "%dx%d@%d" % (r[0], r[1], VARIANTS[v]["samples"] or FINAL_SAMPLES)


def projection(anchor="q1"):
    """{variant: {'cpu', 'rel', 'idle', 'hours', 'hours_low', 'hours_high', 'hours_best'}} for the ladder: mean over
    the five shot types of the brief of the CPU seconds of a frame, the cost relative to the current final (mean
    of the per-shot ratios: the solid number), seconds per frame on four free cores and hours for 1,440 frames.
    'idle' is anchored on what the finished films' own frames took: the LOWER-QUARTILE gap between consecutive
    frame files of each test shot's film shot (film_frame_seconds), times the measured ratio. 'hours_low' /
    'hours_high' = the cheapest / dearest of the five shot types; 'hours_best' = the same projection anchored on
    the single fastest frame of each shot (the best case that the first report quoted). No 4-thread run on an
    idle machine was ever timed: the hours are a projection, the ratio is a measurement."""
    cost = cost_table()
    secs = film_frame_seconds()
    shots = [s for s in FIRST_SHOTS if "base" in cost.get(s, {})]
    out = {}
    for v in LADDER:
        rows = [(s, cost[s][v]) for s in shots if v in cost[s]]
        if not rows:
            continue
        rel = [r["cpu"] / cost[s]["base"]["cpu"] for s, r in rows]
        idle, best = [], []
        for (s, r), k in zip(rows, rel):
            real = secs.get(SHOTS[s]["film"], {}).get(shot_of(s)) or {}
            base = cost[s]["base"]
            # the serial part does not shrink with the samples; the trace does
            f = (r["serial"] + r["trace"] / 4.0) / (base["serial"] + base["trace"] / 4.0)
            idle.append((real.get(anchor) or base["idle"]) * f)
            best.append((real.get("min") or base["idle"]) * f)
        out[v] = dict(cpu=sum(r["cpu"] for _s, r in rows) / len(rows), rel=sum(rel) / len(rel), idle=sum(idle) / len(idle),
                      hours=project(sum(idle) / len(idle)), hours_low=project(min(idle)), hours_high=project(max(idle)),
                      hours_best=project(sum(best) / len(best)), rel_low=min(rel), rel_high=max(rel), shots=len(rows))
    return out


def findings():
    """The conclusions with the measured numbers filled in from the stored results (the text of FINDINGS)."""
    q = load_quality()
    cost = cost_table()
    proj = projection()
    lines = []
    add = lines.append
    add("=" * 100)
    add("RENDER ECONOMICS: FINDINGS  (reference REF = the current final, 720x1280 at 24 samples)")
    add("=" * 100)
    add("1. COST: CPU seconds of one frame (sync + path tracing + denoising + compositing + PNG), all jobs of a setting")
    add("   averaged (n), and in brackets the cost relative to REF on the same shot.")
    add("   %-9s" % "shot" + "".join("%-22s" % ("%s %s" % (_letter(v), _setting(v))) for v in LADDER))
    for shot in SHOTS:
        by = cost.get(shot, {})
        if "base" not in by:
            continue
        add("   %-9s" % shot + "".join(("%-22s" % ("%5.1f (%.2f) n=%d" % (by[v]["cpu"], by[v]["rel"], by[v]["n"]))) if v in by
                                    else "%-22s" % "    -" for v in LADDER))
    if proj:
        add("   %-9s" % "mean*" + "".join("%-22s" % ("%5.1f (%.2f)" % (proj[v]["cpu"], proj[v]["rel"])) for v in LADDER if v in proj))
        add("   * of the five shot types of the brief (%s). The RATIO is the measurement. CPU seconds move about 20 %%"
            % ", ".join(FIRST_SHOTS))
        add("   with the machine's load (the same reference frame read 69.8, 81 and 85 in three runs), the ratio does not.")
        add("   PROJECTED for four free cores (no 4-thread run on an idle machine was ever timed): seconds per frame =")
        add("   the lower-quartile gap between the finished films' own frame files (%s s by shot) x the ratio; hours for"
            % "-".join("%.1f" % x for x in (min(_real_seconds()), max(_real_seconds()))))
        add("   1,440 frames (cheapest .. dearest shot type); best = anchored on each shot's single fastest frame:")
        add("   %-9s" % "s/fr" + "".join("%-22s" % (" %.1f" % proj[v]["idle"]) for v in LADDER if v in proj))
        add("   %-9s" % "hours" + "".join("%-22s" % (" %.1f (%.1f .. %.1f)" % (proj[v]["hours"], proj[v]["hours_low"], proj[v]["hours_high"]))
                                        for v in LADDER if v in proj))
        add("   %-9s" % "best" + "".join("%-22s" % (" %.1f" % proj[v]["hours_best"]) for v in LADDER if v in proj))
        add("   On a machine shared with other agents the finished films took up to twice the projected time.")
    add("")
    add("2. STILLS against REF as delivered (Lanczos to 1080x1920): SSIM on luma of the whole frame / at phone size")
    add("   (540x960), worst of the five 1:1 crops, edge contrast relative to REF. REF2 = REF with another noise seed (what")
    add("   two renders of the current final differ by). A = 720x1280 at 16 as render.py would render it.")
    for shot, rows in q.get("quality", {}).items():
        add("   %-9s" % shot + "  ".join("%s %.4f/%.4f/%.3f/x%.2f" % (
            letter, r["ssim"], r["phone_ssim"], min(c["ssim"] for c in r["crops"].values()), r["sharp"])
            for letter, r in rows.items() if letter in ("REF2", "A", "B", "C", "D", "E", "F", "G")))
    far = q.get("quality", {}).get("far", {})
    if far:
        add("   The far figure's own window (crop 'face' of shot 'far': both figures, 224 px): " + "  ".join(
            "%s ssim %.3f, edge contrast x%.2f" % (letter, far[letter]["crops"]["face"]["ssim"], far[letter]["crops"]["face"]["sharp"])
            for letter in ("REF2", "C", "E") if letter in far))
    bl = blind_tally(score=False, verbose=False)
    if bl["n"]:
        add("   BLIND PAIRS, E against REF, order of every pair drawn at random, key read after all answers were stored:")
        add("   the reference named right in %d of %d (guessing gives %.0f; more than %.1f would be a tell). %s"
            % (bl["right"], bl["n"], bl["n"] / 2.0, bl["limit"],
               "  ".join("%s %d/%d" % (k, v[0], v[1]) for k, v in bl["by_scale"].items())))
        add("   by shot: " + "  ".join("%s %d/%d" % (k, v[0], v[1]) for k, v in bl["by_shot"].items()))
    add("")
    add("3. TEMPORAL, on frames encoded as engine/post.py encodes a film (levels of 255).")
    add("   a) the same frame with two noise seeds, shown alternately (tools/noise_check's method; nothing moves, every")
    add("      difference is noise): mean / 99th percentile over the frame, mean in flat areas. Accepted so far: flat <= %.1f."
        % ACCEPTED_FLAT)
    add("      ~ = a pair with a 16-sample render that followed a 24-sample job in its session: reads too high (see 5).")
    for shot, rows in q.get("boil", {}).items():
        add("      %-9s" % shot + "  ".join("%s%s %.2f/%.0f/%.2f" % (_letter(v), "~" if v in ("s16", "r640s16") else "", st["pair_mean"],
                                                                  st["pair_p99"], st["flat_mean"]) for v, st in rows.items()))
    add("   b) 8 consecutive frames with the film's own fixed seed: frame-to-frame change in still regions / worst dark or")
    add("      defocused box relative to REF. In a MOVING shot this number is residual motion, not noise (the hall): see c).")
    for shot, rows in q.get("temporal", {}).items():
        base = rows.get("base")
        if not base:
            continue
        parts = []
        for nm, st in rows.items():
            if "frozen" in nm or "animseed" in nm:
                continue
            worst = max(st[b]["noise"] / max(base[b]["noise"], 0.05) for b in SEQ_BOXES.get(shot, {}))
            parts.append("%s %.2f/x%.2f" % (_letter(nm), st["flat"]["noise"], worst))
        add("      %-9s" % shot + "  ".join(parts))
        for nm, st in rows.items():
            if "frozen" in nm or "animseed" in nm:
                boxes = "  ".join("%s %.2f" % (b, st[b]["noise"]) for b in SEQ_BOXES.get(shot, {}))
                add("      %-9s %s: %.2f  (%s)" % ("", nm, st["flat"]["noise"], boxes))
    if q.get("pair"):
        add("   c) the same 8 frames rendered with noise seeds 0 and 1, both clips encoded, differenced frame by frame (MOTION")
        add("      CANCELS): noise in a frame > noise that changes from one frame to the next, per region (mean; in")
        add("      brackets the 99th percentile of the changing part over the whole frame).")
        for where, key in (("encoded", "pair"), ("before the encoder", "pair_raw")):
            for shot, rows in q.get(key, {}).items():
                regs = [r_ for r_ in ("all", "flat", "dark") + tuple(SEQ_BOXES.get(shot, {})) if r_ in rows.get("base", {})]
                add("      %s, %s%s:" % (shot, where, (" (x264 itself: %.1f levels per frame)" % rows["base"]["all"]["codec"])
                                         if "codec" in rows.get("base", {}).get("all", {}) else ""))
                for v, st in rows.items():
                    add("        %-4s" % _letter(v) + "  ".join(
                        "%s %.2f>%.2f" % (r_, st[r_]["frame"], st[r_]["temporal"]) for r_ in regs if r_ in st)
                        + "  (p99 %.1f)" % st["all"]["temporal_p99"])
    eyes = q.get("far_eyes") or {}
    if eyes:
        add("   d) the far figure's eyes over the 8 delivered frames, per head (20 blocks = near, 32 = far; glowing / plain")
        add("      white texels): peak luma lowest..highest, bright area in pixels smallest..largest, largest move of its")
        add("      centre between consecutive frames (the handheld drift included).")
        for v, e in eyes.items():
            parts = []
            for k, rows in e.items():
                lo, hi, step, a0, a1 = _eye_summary(rows)
                parts.append("%s %.0f..%.0f, %d..%d px, %.1f" % (k, lo, hi, a0, a1, step))
            add("      %-4s %s" % (_letter(v), "; ".join(parts)))
    so = q.get("session_order") or {}
    if so.get("shrink"):
        add("   e) the order of renders inside one Blender session: a 16-sample still that followed a 24-sample job against")
        add("      the same setting from a 16-sample-only process: PSNR to REF (dB) / two-seed difference as delivered.")
        for shot, rows in so["shrink"].items():
            add("      %-9s" % shot + "  ".join("%s after 24: %.2f / %.2f, fresh: %.2f / %.2f" % (
                _letter(v), r_["psnr_after"], r_["pair_after"], r_["psnr_fresh"], r_["pair_fresh"]) for v, r_ in rows.items()))
        for shot, r_ in so.get("grow", {}).items():
            add("      %-9s24 samples after 16: the same pixels as a fresh process: %s" % (shot, r_["same"]))
    add("")
    ident = q.get("identical") or identical_frames()
    add("4. FRAMES THAT NEED NO RENDER: %d frames of the finished films, %d with the fingerprint of the frame before, %d"
        % (sum(r["frames"] for r in ident.values()), sum(r["same_as_previous"] for r in ident.values()),
           sum(r["same_as_any_earlier"] for r in ident.values())))
    add("   with the fingerprint of any earlier frame. render.py does not look for such frames (it renders every frame).")
    add("")
    add(FINDINGS.strip("\n"))
    return "\n".join(lines)


def _real_seconds(anchor="q1"):
    secs = film_frame_seconds()
    out = []
    for s in FIRST_SHOTS:
        r = (secs.get(SHOTS[s]["film"], {}).get(shot_of(s)) or {}).get(anchor)
        if r:
            out.append(r)
    return out or [0.0]


def _evidence_times():
    """{path: mtime} of every evidence file of this tool (out/test/econ_* and out/test/econ_raw/*)."""
    out = {}
    for d, pre in ((TEST, "econ_"), (RAW, "")):
        if not os.path.isdir(d):
            continue
        for n in os.listdir(d):
            q = os.path.join(d, n)
            if n.startswith(pre) and os.path.isfile(q):
                out[os.path.relpath(q, ROOT)] = os.path.getmtime(q)
    return out


def selftest(build=True):
    """Checks the stored measurements (no rendering; exit code 1 on a failed check): the settings are legal, a
    second render of a frame is the same picture bit for bit, the first-pass numbers are consistent, RECOMMENDED and
    SAFE are cheaper than the current final, as close to it on a phone as the brief asks and inside the accepted
    temporal noise (held frame, 8 frames, two seeds over 8 frames), the far figure's eyes hold, the blind pairs are
    answered and no better than guessing, a 16-sample render after a 24-sample one is the noisier picture, the
    finished films hold no identical frames, the sheets exist, and (build=True: builds five film scenes, about
    15 s) render.py takes a film's own resolution and samples as its final quality, for one sky and for several,
    while a change of render.FINAL_RES for everybody would make every finished frame stale. Writes no file. `quality` rebuilds the numbers
    and the sheets from the stored renders; this reads them (out/test/econ_raw/quality.json)."""
    ok = True

    def check(cond, text):
        nonlocal ok
        print("[econ] %s  %s" % ("ok  " if cond else "FAIL", text))
        ok = ok and bool(cond)

    before = _evidence_times()
    for name, v in VARIANTS.items():
        res = v["res"] or FINAL_RES
        check(abs(res[0] / res[1] - 9.0 / 16.0) < 0.002 and res[0] % 2 == 0 and res[1] % 2 == 0,
              "variant %s: %dx%d is 9:16 with even sides" % (name, res[0], res[1]))
    check(RECOMMENDED in VARIANTS and SAFE in VARIANTS, "RECOMMENDED / SAFE are measured variants")
    check(abs(project(10.0) - 4.0) < 1e-9, "project(): 10 s per frame = 4.0 h for 1440 frames")
    res = load_results()
    if not res:
        print("[econ] no measurements stored yet (run the groups first)")
        return 0 if ok else 1

    # ---- the same frame rendered again is the same picture, bit for bit
    n_same = 0
    for shot, S in SHOTS.items():
        fin = os.path.join(ROOT, "out", "frames", S["film"], "f_%04d.png" % S["frame"])
        for rec in res.values():
            if rec.get("kind") is None and rec.get("shot") == shot and rec.get("variant") == "base" and rec.get("seed") == 0 \
                    and not rec.get("border") and rec.get("frame") == S["frame"] and rec.get("tag", "") in ("", "re") \
                    and os.path.exists(fin) and os.path.exists(os.path.join(ROOT, rec["path"])):
                n_same += 1
                check(same_pixels(fin, os.path.join(ROOT, rec["path"])),
                      "%s: the 'base' job %s is bit-identical to the finished film's frame %s (rendered days earlier)"
                      % (shot, rec["key"], os.path.relpath(fin, ROOT)))
    check(n_same >= 2, "the current final was rendered again %d times, always the same pixels" % n_same)
    for rec in res.values():
        if rec.get("kind") != "pipeline":
            continue
        check(rec["first_equals_again"],
              "%s %s rendered the way render.py renders a film: the first frame of a process and the same frame "
              "rendered again later hold the same pixels" % (rec["shot"], rec["variant"]))
        fresh = [k for k, same in rec["equals_job"].items() if same]
        other = [k for k, same in rec["equals_job"].items() if not same]
        check(fresh, "  it is the picture of this tool's jobs %s" % ", ".join(fresh))
        if other:
            # the trap of Cycles' persistent session that this tool ran into: 16 samples after a 24-sample render
            # in the same session is another, NOISIER picture (session_order(); see FINDINGS)
            print("[econ] note  not the picture of %s: a 16-sample job that followed a 24-sample job in the same "
                  "Blender session is another, noisier picture (see session_order)" % ", ".join(other))

    # ---- first pass (border sweeps of the settings): read from summary.json; `report` rebuilds it and its sheets
    summary = _read_json(os.path.join(RAW, "summary.json"), {})
    check(summary.get("shots"), "the first pass's tables are stored (out/test/econ_raw/summary.json)")
    for shot, S in summary.get("shots", {}).items():
        full = S.get("full", {})
        if "base" in full:
            b = full["base"]
            check(b["trace_cpu"] > 4.0 * (b["sync"] + b["comp"] + b["save"]),
                  "%s: the trace is the bulk of a base frame (%.1f cpu-s against %.2f s serial)"
                  % (shot, b["trace_cpu"], b["sync"] + b["comp"] + b["save"]))
        for v, row in S.get("border", {}).items():
            if v in ("ad_005", "ad_02", "ad_min4", "ad_min12", "lst05", "tb4", "diff1", "gloss0", "glare_med",
                     "dn_pf_fast", "dn_pf_none", "dn_q_fast", "dn_q_high", "dn_rgb", "dn_rgb_albedo"):
                check(abs(row["rel"] - 1.0) <= 0.16, "%s: %s moves the trace by x%.2f (a side issue)" % (shot, v, row["rel"]))

    # ---- cost
    cost = cost_table()
    for shot, by in cost.items():
        if "base" not in by:
            continue
        for v, lim in ((RECOMMENDED, 0.60), (SAME_SETTING.get(SAFE, SAFE), 0.78)):
            if v in by:
                check(by[v]["rel"] < lim, "%s: %s costs x%.2f of the current final (%.0f against %.0f cpu-s)"
                      % (shot, v, by[v]["rel"], by[v]["cpu"], by["base"]["cpu"]))

    # ---- second pass (stored by `quality`)
    q = load_quality()
    stale = not q or os.path.getmtime(QUALITY_JSON) < os.path.getmtime(RESULTS)
    check(not stale, "out/test/econ_raw/quality.json is newer than the last render (else run: quality)")
    rl, sl = LETTER[RECOMMENDED], LETTER[SAFE]
    for shot, rows in q.get("quality", {}).items():
        floor = rows.get("REF2")
        for letter in (rl, sl):
            row = rows.get(letter)
            if not row:
                continue
            lim = min(0.985, (floor["phone_ssim"] - 0.006) if floor else 0.985)
            check(row["phone_ssim"] >= lim and row["phone_p99"] <= 9.0,
                  "%s: %s at phone size: SSIM %.4f (two renders of the current final differ by %s), 99 %% of the "
                  "pixels within %.1f levels" % (shot, letter, row["phone_ssim"],
                                                 ("%.4f" % floor["phone_ssim"]) if floor else "?", row["phone_p99"]))
    for shot, rows in q.get("boil", {}).items():
        base = rows.get("base")
        for v in (RECOMMENDED, SAME_SETTING.get(SAFE, SAFE)):
            st = rows.get(v)
            if not (st and base):
                continue
            # flat areas: the level the finished films were accepted with. The 99th percentile of the whole frame
            # is judged against the current final's own (5-6 here; the 4.4 once accepted for a grassy foreground
            # was another frame and another measure: the current final's grass reads 10 by this one): +2 at most
            check(st["flat_mean"] <= ACCEPTED_FLAT and st["pair_p99"] <= base["pair_p99"] + 2.0,
                  "%s: %s two-seed noise on encoded frames: flat %.2f (current final %.2f, accepted %.1f), 99th "
                  "percentile %.0f (current final %.0f; at most +2)" % (shot, v, st["flat_mean"], base["flat_mean"],
                                                                         ACCEPTED_FLAT, st["pair_p99"], base["pair_p99"]))
    for shot, rows in q.get("temporal", {}).items():
        base = rows.get("base")
        for v in (RECOMMENDED, SAFE):
            st = rows.get(v)
            if not (st and base):
                continue
            worst = max(st[b]["noise"] / max(base[b]["noise"], 0.05) for b in SEQ_BOXES.get(shot, {}))
            check(st["flat"]["noise"] <= 1.15 * base["flat"]["noise"] + 0.05 and worst <= 1.25,
                  "%s: %s over 8 consecutive encoded frames: noise in still regions %.2f (current final %.2f), "
                  "worst dark / defocused box x%.2f of the current final" % (shot, v, st["flat"]["noise"],
                                                                             base["flat"]["noise"], worst))
    # ---- two seeds over 8 frames (motion cancels): the per-frame noise and the part of it that changes between frames
    for shot, rows in q.get("pair", {}).items():
        base = rows.get("base")
        for v in (RECOMMENDED, SAFE):
            st = rows.get(v)
            if not (st and base):
                continue
            worst = max(st[r_]["temporal"] / max(base[r_]["temporal"], 0.05) for r_ in st if r_ in base)
            check(st["flat"]["temporal"] <= 1.15 * base["flat"]["temporal"] + 0.05 and worst <= 1.25
                  and st["all"]["temporal_p99"] <= base["all"]["temporal_p99"] + 2.0,
                  "%s: %s two seeds over 8 ENCODED frames (motion cancels): noise changing between frames, flat areas "
                  "%.2f (current final %.2f), worst region x%.2f of the current final, 99th percentile %.1f (current "
                  "final %.1f; at most +2)" % (shot, v, st["flat"]["temporal"], base["flat"]["temporal"], worst,
                                               st["all"]["temporal_p99"], base["all"]["temporal_p99"]))
        raw = q.get("pair_raw", {}).get(shot, {})
        for v in (RECOMMENDED, SAFE):
            st, rb = raw.get(v), raw.get("base")
            if not (st and rb):
                continue
            check(st["flat"]["frame"] <= max(ACCEPTED_FLAT, 1.15 * rb["flat"]["frame"]) + 0.05
                  and st["all"]["frame"] <= 1.35 * rb["all"]["frame"],
                  "%s: %s the same before the encoder: noise in a frame, flat areas %.2f (current final %.2f; "
                  "accepted %.1f), whole frame %.2f (current final %.2f)" % (
                      shot, v, st["flat"]["frame"], rb["flat"]["frame"], ACCEPTED_FLAT, st["all"]["frame"], rb["all"]["frame"]))
    # ---- the far figure's eyes hold from frame to frame
    eyes = q.get("far_eyes") or {}
    for v in (RECOMMENDED, SAFE):
        if v in eyes and "base" in eyes:
            for k in FAR_HEADS:
                lo, hi, step, a0, a1 = _eye_summary(eyes[v][k])
                rlo, rhi, rstep, ra0, ra1 = _eye_summary(eyes["base"][k])
                check(lo >= rlo - 12.0 and hi - lo <= rhi - rlo + 10.0 and step <= rstep + 3.0,
                      "far figure, %s, %s: eye peak %.0f..%.0f over 8 delivered frames (current final %.0f..%.0f), "
                      "bright area %d..%d px (%d..%d), largest move between frames %.1f px (%.1f)"
                      % (v, k, lo, hi, rlo, rhi, a0, a1, ra0, ra1, step, rstep))
    # ---- the order of renders inside one session
    so = q.get("session_order") or {}
    for shot, rows in so.get("shrink", {}).items():
        for v, r_ in rows.items():
            check(not r_["same"] and r_["psnr_after"] < r_["psnr_fresh"] - 0.2 and r_["pair_after"] > 1.05 * r_["pair_fresh"],
                  "%s %s: 16 samples AFTER a 24-sample job in one session is a noisier picture than from a 16-sample-"
                  "only process (PSNR to REF %.2f against %.2f dB, two-seed difference %.2f against %.2f)"
                  % (shot, v, r_["psnr_after"], r_["psnr_fresh"], r_["pair_after"], r_["pair_fresh"]))
    for shot, r_ in so.get("grow", {}).items():
        check(r_["same"] and r_.get("first_job_same", True),
              "%s: 24 samples after 16 in one session = the same pixels as a fresh process; two fresh processes at E "
              "give the same pixels" % shot)
    # ---- blind pairs: every trial answered before the key was read, and no better than guessing
    bl = blind_tally(score=False, verbose=False)
    if bl["n"] or bl["unanswered"]:
        check(not bl["unanswered"], "blind pairs: all %d trials are answered" % (bl["n"] + len(bl["unanswered"])))
        check(bl["right"] <= bl["limit"], "blind pairs, %s against the current final: the reference named right in %d "
              "of %d (guessing: %.0f; a tell: more than %.1f)" % (LETTER[RECOMMENDED], bl["right"], bl["n"], bl["n"] / 2.0,
                                                                  bl["limit"]))
    ident = identical_frames()
    check(ident and all(r["same_as_previous"] == 0 and r["same_as_any_earlier"] == 0 for r in ident.values()),
          "finished films: %d frames, none has the fingerprint of another frame (nothing to copy)"
          % sum(r["frames"] for r in ident.values()))
    for p in q.get("sheets", []):
        check(os.path.exists(p), "sheet %s" % os.path.relpath(p, ROOT))

    # ---- how the setting gets into render.py
    if build:
        f = check_final_per_film()
        v = VARIANTS[RECOMMENDED]
        want = "%dx%d|%dspp|mb1" % (v["res"][0], v["res"][1], v["samples"])
        check(f["own_variant"] is None and f["own_dir"].startswith(os.path.join("out", "frames")) and f["own_settings"] == want,
              "a film that sets its own resolution and samples in build() renders FINAL frames (%s) stamped %s"
              % (f["own_dir"], f["own_settings"]))
        check(set(f["asis_states"]) <= {"valid", "engine"} and f["asis_fp_g"] == f["asis_stamp_g"],
              "the finished film as it is: frames %s, look fingerprint unchanged" % f["asis_states"])
        check(set(f["global_states"]) == {"size"} and f["global_fp_g"] != f["asis_stamp_g"],
              "render.FINAL_RES / FINAL_SAMPLES changed for everybody: every finished frame turns stale %s"
              % f["global_states"])
        check(f["own_flag_variant"] is not None,
              "the same setting passed as --res / --samples would NOT be the final: render.variant_of gives the "
              "preview directory %r" % f["own_flag_variant"])
        if os.path.exists(os.path.join(ROOT, "films", "_multisky_demo.py")):
            m = check_final_per_film("_multisky_demo", finished=False)
            skies = m.get("own_skies", {})
            check(len(skies) >= 2 and m["own_variant"] is None and all(
                sk["settings"] == want and sk["min_samples"] == 5 and (sk["meta_base"] or [])[:3] == [v["res"][0], v["res"][1], v["samples"]]
                for sk in skies.values()),
                "a film with several skies (films/_multisky_demo.py): every sky's build takes the film's own "
                "setting as final (%s: %s, meta.json base %s)" % (", ".join(skies), want, next(iter(skies.values()))["meta_base"]
                                                                  if skies else None))
    print(findings())
    after = _evidence_times()
    changed = sorted(k for k in set(before) | set(after) if before.get(k) != after.get(k))
    check(not changed, "the self-test wrote no evidence file (out/test/econ_*)%s"
          % ("" if not changed else ": " + ", ".join(changed[:6])))
    return 0 if ok else 1


def main(argv):
    """Entry point."""
    if not argv or argv[0] == "--no-build":
        return selftest(build=not argv)
    cmd = argv[0]
    opt = {}
    opt_s = {}
    rest = []
    it = iter(argv[1:])
    for a in it:
        if a in ("--budget", "--threads", "--seed"):
            opt[a[2:]] = float(next(it))
        elif a in ("--res", "--samples"):
            opt_s[a[2:]] = next(it)
        elif a in ("--animated", "--no-sheets"):
            pass
        else:
            rest.append(a)
    if cmd == "list":
        return listing()
    if cmd == "report":
        report()
        return 0
    if cmd == "sync":
        sync_study(rest[0], threads=int(opt.get("threads", 2)))
        return 0
    if cmd == "run":
        return run(rest[0], rest[1], budget=opt.get("budget", 200.0), threads=int(opt.get("threads", 2)))
    if cmd == "findings":
        print(findings())
        return 0
    if cmd == "pipeline":
        pipeline_check(rest[0], rest[1] if len(rest) > 1 else RECOMMENDED, threads=int(opt.get("threads", 2)))
        return 0
    if cmd == "quality":
        quality_report(sheets="--no-sheets" not in argv, shots=rest or None)
        return 0
    if cmd == "crops":
        q = load_quality().get("quality", {})
        for shot in (rest or list(q)):
            print(sheet_crops(shot, q=q.get(shot)))
        return 0
    if cmd == "blind":
        for path in blind_trials(rest or None):
            print(path)
        return 0
    if cmd == "blind-answer":
        n = blind_answer(dict(a.split("=", 1) for a in rest))
        print("[econ] %d answers stored" % n)
        return 0
    if cmd == "blind-tally":
        blind_tally()
        return 0
    if cmd == "noise":
        frames = [int(a) for a in rest[1:]]
        res = tuple(int(x) for x in opt_s["res"].lower().split("x")) if "res" in opt_s else None
        film_noise(rest[0], frames, res, int(opt_s["samples"]) if "samples" in opt_s else None,
                   threads=int(opt.get("threads", 2)))
        return 0
    if cmd == "seq":
        return run_seq(rest[0], rest[1].split(","), budget=opt.get("budget", 200.0),
                       threads=int(opt.get("threads", 2)), animated="--animated" in argv, seed=int(opt.get("seed", 0)))
    print(__doc__)
    return 1


FINDINGS = """
5. WHAT THE NUMBERS SAY
   COST. A frame costs pixels, hardly samples: adaptive sampling already stops most pixels before the cap, so A
   (720x1280 at 16) saves 0-21 % (nothing in daylight) and D (540x960 at 24) costs what E costs in daylight and
   20-25 % more at dusk and in the hall. E (540x960 at 16) is 0.45-0.55 of the current final on all eight shot
   types, C (600x1066 at 16) 0.54-0.73. The ratio is the solid number. The hours are a projection (see the table):
   about half the time, roughly 3.1 h per 1,440 frames on four idle cores where the current final would take 6.2 h,
   and up to twice that on a shared machine. Time the first 100 final frames of the first film to confirm.

   A TRAP, found while answering the review. Inside one Blender session (render.py keeps one per process) a
   16-sample render that FOLLOWS a 24-sample render is not the picture a film frame would be. It is noisier: PSNR
   against the reference 0.3-0.6 dB lower, two-seed difference 11-13 % higher (E and C on dusk and hall,
   session_order()). The first pass of this study had rendered E and C on dusk and hall, and C's second seed on
   every shot, that way; its "E is 1.5-1.6 times noisier under lantern light" came mostly from that. Every
   16-sample still was rendered again in a 16-sample-only process (job tag 'fr'), and the numbers below are those.
   The other direction is harmless: 24 samples after 16 give the same pixels as a fresh process (hall).
   For production: final frames of a 16-sample film must not come from a process that rendered more samples
   before (a `--still ... --samples 24` in the same call as `--frames`). `--frames` in a call of its own is safe.

   STILLS. Two renders of the CURRENT final (REF and REF2) agree to SSIM 0.990-0.995; that is the floor. A sits on
   the floor on all five shots. B, C, D and E are 0.984-0.990 on all eight shots (phone size 0.987-0.992 against
   a floor of 0.991-0.995): whatever is below 720x1280 loses the same small step and then almost nothing more
   down to 540x960. Edge contrast at 1:1 against REF: E x0.95-0.98 on seven shots and x0.91 on the far night shot
   (its worst crop, thin grass blades against the night sky, x0.87); C x0.97-0.99 and x0.94. Texels stay square,
   there are no stair-steps, faces and large texels are unchanged.
   BLIND PAIRS. 40 pairs of REF and E on the eight shots, each in an order of its own drawn at random, answers
   stored before the key was read (blind2_key.json, blind2_answers.json): the reference named right in 20 of 40.
   Whole frame at phone size 4 of 8, regions at 720x1280 (what Instagram delivers) 16 of 32. No shot stands out.
   (The first report's five single pairs, 3 of 5, were too few to say anything.)
   UPSCALE. engine.post.upscale (Lanczos) stays. Nearest and nearest-x4-then-Lanczos keep hard texel edges but
   put stair-steps on every slanted edge and on depth-of-field blur; an unsharp mask after Lanczos brings the
   edge contrast back to REF's (x1.00-1.08) and draws a bright fringe along high-contrast texel edges (the white
   of an eye beside its green); bicubic is softer. A narrower pixel filter for the 2x upscale (H, filter_width 1.0
   instead of 1.3; night shot only) costs 5-20 % more and changes nothing measurable.

   TEMPORAL. (a) A HELD FRAME, two noise seeds of one frame shown alternately and encoded: E reads x0.93-1.26 of
   REF over the frame (dusk x1.26, hall x1.23, interior x1.13, face x1.05, sun, run, far x1.0, night x0.93); before
   the encoder the same pairs differ by x0.98-1.13, so x264 at crf 16 passes E's coarser grain a little more
   easily. Flat areas: E 0.06-0.52 against REF 0.11-0.55, all inside what the finished films were accepted with
   (0.9). 99th percentile 5-8 against 4-6 (the 4.4 once accepted for a grassy foreground was another measure on
   another frame; the current final's own frames read 4-6 here, so the limit used is REF + 2). C: x0.88-1.15.
   D, 24 samples at 540x960, is no calmer than E (hall 0.92 against 0.90): samples buy nothing there either.
   A~ and B~ in table 3a still hold a render that followed a 24-sample job and read too high.
   (b) 8 CONSECUTIVE FRAMES with the film's fixed seed, frame-to-frame change in still regions: night 0.33 (REF
   0.35), far 0.12 (0.13), every dark or defocused box within 6 % of REF. The hall reads 1.41 for every setting,
   but that number is the dolly's residual motion, not noise (its boxes read up to 7 levels where the frame's
   noise is about 1): it cannot show a difference between settings. (c) can.
   (c) TWO SEEDS OVER THE 8 FRAMES, motion cancelled (seed_pair). Hall, a dolly under lantern light: before the
   encoder the noise in a frame is REF 1.26, C 1.35, E 1.39 (+10 %; flat areas 0.88 / 0.90 / 0.90; the defocused
   bars 1.55 / 1.67 / 1.72); the part that changes from frame to frame 1.06 / 1.14 / 1.17. After the encoder:
   1.70 / 1.79 / 1.82 in a frame, 1.61 / 1.69 / 1.69 changing (+5 %), 99th percentile 6.4 against 7.1. x264 itself
   puts about 2.2 levels of error on every frame of every setting; in a moving shot that, not the renderer,
   is most of what differs between two encodes. Night, nearly locked: E equals REF over the frame (0.84 against
   0.86 before the encoder, 0.97 against 0.99 changing after it) and is 18 % above it in the one place that was
   feared, the dark defocused far houses (changing part 1.51 against 1.28 before the encoder, 1.70 against 1.58
   after it; 99th percentile 7.8 against 6.4).
   THE FIXED SEED. render.py renders every frame with cycles.seed 0. In the nearly locked night shot 70 % of a
   frame's noise still changes from one frame to the next (the handheld drift moves the picture under the
   pattern), in the dolly 85 %. Animating the seed makes all of it change: E's far houses 1.71 against 1.24
   (99th percentile 7.9 against 5.1). KEEP THE SEED FIXED; it is worth about a third of the boil in a still shot.
   (d) THE FAR FIGURE (what "The Hello" shows in six beats). Herobrine at 20 and at 32 blocks from a 35 mm lens,
   night, handheld, 8 frames. Glowing eyes peak at 255 in every frame of every setting, plain white eye texels at
   141-150; no eye jumps (centres move 0.2-1.3 pixels a frame, the drift). At 20 blocks (a texel = 3.4 rendered
   pixels at E) the eyes are REF's. At 32 blocks (2.1 pixels) the saturated core of the glowing eyes is smaller and
   breathes with the drift: 27..46 delivered pixels over the 8 frames at E, 26..47 at C, 42..49 at REF, largest
   step between two frames 5 pixels (REF 7, C 7): a slow change, no flicker. Enlarged three times the far eyes are
   rounded where REF's are rectangles (econ_far_figure.png); the figure's window keeps x0.94 of REF's edge
   contrast at E and at C alike. At phone size none of it showed (blind pairs of this shot: 2 of 5).
   DETERMINISM. A frame rendered again by render.py is the same picture bit for bit: three 'base' jobs equal the
   finished films' frames rendered days earlier; at E the first frame of a process equals the same frame rendered
   later in another position, and two processes give the same pixels (hall). The exception is the trap above.
   IDENTICAL FRAMES. None in the finished films (every shot has handheld drift and idle motion: the camera digest
   never repeats). render.py renders every frame it is asked for and does not look for an equal fingerprint.
   Because the seed is fixed, a frame with the fingerprint of an earlier one would come out bit-identical, so
   copying it is exactly what rendering gives: a held picture (x264 codes it as skipped blocks, temporal sigma
   0.01). That is acceptable and it is what a locked-off shot looks like today; it saves nothing until a film
   holds a truly still shot (no handheld, no idle motion), so it is not worth a change to render.py now.

6. RECOMMENDATION
   RECOMMENDED  E = 540x960 at 16 samples (adaptive minimum 5), everything else as now; delivered by the same
                Lanczos upscale (exactly 2x). About half the time: 0.49 of the current final (0.45-0.55 by shot).
                It is the setting every test still of this project has been judged at (render.py STILL_RES /
                STILL_SAMPLES, engine/quick.py). It passes the decision rule: not told from the current final
                in 40 blind pairs, temporal noise inside the accepted range and within 5-18 % of the current
                final wherever motion allows a measurement.
                What gets worse, all of it at 1:1 beside the current final and none of it at phone size:
                - small texels in wide shots are a little softer (edge contrast x0.95-0.98; the far night shot
                  x0.91, thin grass blades against a night sky x0.87);
                - a far figure: its face keeps x0.94 of the edge contrast; glowing eyes of two-pixel texels
                  (32 blocks at 35 mm) lose their square corners when enlarged and their bright core varies
                  between 27 and 46 pixels with a handheld drift where the current final holds 42-49;
                - noise: a held lantern-lit frame x1.1 before the encoder (x1.2-1.3 after it), a moving one
                  +5-10 %; dark defocused houses at night +18 % before the encoder, +8 % after.
   SAFE         C = 600x1066 at 16 samples: 0.63 of the current final, about 0.8 h more per film than E. Half of
                E's loss of edge contrast comes back (x0.97-0.99, far night shot x0.94) and the noise sits between
                E and the current final. It does NOT help the far figure's eyes (26..47 pixels, as E).
   If the far watcher must hold up at 1:1 like the finished films, only 720x1280 does it: A (720x1280 at 16)
   sits on the current final's own noise floor on all five shots it was rendered for, at 0.88 of the time.
   One setting per film: frames of two sizes cannot be mixed (see 7).
   Nothing cheaper than E is recommended: on the night shot (the only one they were rendered for) G (480x854) is
   softer at 1:1 (x0.92) for another 18 % and F (540x960 at 12 samples) is further from the reference for 10 %;
   540x960 is also the exact half of the delivery size.

7. THE EXACT CHANGE (no engine file and no line of render.py has to change; names, not line numbers: render.py
   is being edited)
   In the film script of each one-minute film, in build(scene) (films with several skies: build(scene, sky=None)),
   on the scene the film is built in, before the return (verified by check_final_per_film, which builds a
   one-sky film and the two skies of films/_multisky_demo.py this way):
       scene.render.resolution_x, scene.render.resolution_y = 540, 960     # SAFE: 600, 1066
       scene.cycles.samples = 16
   render.py takes the film's own values as its final quality: render.Session.__init__ reads them into
   Session.base, Session.configure keeps them when no --res / --samples is given and sets the adaptive minimum
   to max(4, samples // 3) = 5, render.variant_of(None, None, 1) is None, so
   `render <film> --frames all --max-seconds 240` writes out/frames/<film>/f_####.png at 540x960, stamped
   '540x960|16spp|mb1', and `--encode` upscales them (engine.post.upscale, unchanged).
   Rules that go with it:
   - Put the three lines in BEFORE the first final frame of the film is rendered. Added later, every frame on
     disk turns stale by size and the next `--frames all` renders all of them again over the old ones without
     stopping (only engine-source changes stop a run, exit code 3). The same holds for a switch between E and
     SAFE; --encode refuses frames of mixed sizes, so two settings can never be mixed in one film.
   - Never pass --res / --samples for finals. render.variant_of compares them with the module constants, so
     `--res 540x960 --samples 16` on such a film selects the preview directory '540x960_16spp'.
   - Render finals in calls of their own (the trap in 5): no `--still --samples 24` in the same call.
   - Do NOT change render.FINAL_RES / FINAL_SAMPLES or the defaults of engine.look.setup_render: they are the
     final quality of the four finished films. Changed for everybody, all 1,206 finished frames turn stale
     (status 'size'; the 'g' part of every fingerprint changes too) and would be rendered over.
   - Leave scene.cycles.seed at 0 and use_animated_seed off (look.setup_render does not touch them).
   - tools/noise_check.py measures at render.FINAL_RES / FINAL_SAMPLES whatever the film sets. For a film with
     its own setting use `$BPY -m tools.render_economics noise <film> <frame> ...` (film_noise): the same two-seed
     test at the film's own quality, as rendered and as encoded.
   Elsewhere, for whoever owns those files: tools/noise_check.py, engine/stamp.py's self-test, tools/check_sets_ab.py
   and tools/check_sets_hook.py configure with render.FINAL_RES / FINAL_SAMPLES; CONTRACT.md and render.py's
   docstring still say finals are 720x1280 at 24 samples. A film's final quality is what its build() sets, with
   720x1280 at 24 as the default.

8. NOT VERIFIED
   No finished one-minute film was rendered at E; the evidence is eight shot types (stills), three of them as
   8-frame clips, two of those with a second seed. The Instagram re-encode is a stand-in (720x1280, x264 crf
   27), not the platform. The blind pairs were judged by the author of this study on stills, not on moving
   pictures by the client. No 4-thread run on an idle machine was timed: the hours are projected from the
   finished films' file times. The far figure is a probe shot built for this study (the real village, the night
   film's sky, engine.players' Herobrine), not a shot of the film. Why a shrinking sample count degrades a
   persistent Cycles session was not looked into; only its effect was measured.
"""


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
