# HANDOFF: BrahMos explainer video (read this first)

Written 2026-11-09 by the laptop Claude session, so a Claude session on the desktop can continue exactly where it stopped.
Everything here is the state at the moment of the push. Check the in-flight EngineX jobs below with `get_job` before
starting anything new: they may have finished (or need re-running) by the time you read this.

## 1. What this is
A ~6:14 **Hinglish** narrated "How BrahMos works" explainer in the Branch Education style (3D in Blender on EngineX +
Motion Graphic overlays), mixed with Real Engineering (physics cutaways), Mark Rober ("but..." chain, slow-mo reveals)
and Animagraffs (x-ray skin). English version comes AFTER the Hinglish one is finished.

Workflow skills (load them, as CLAUDE.md says): `.claude/skills/tech-explainer-video/SKILL.md` and
`.claude/skills/blender-animation/SKILL.md`. Also the EngineX skills via `get_skill` (motion-director, color-palette,
typography, design-polish, blender, emotive-speech, image-director, poster-director, freecad): the user asked that all
of them are used.

## 2. The user's decisions (do not re-ask)
- **Audio language: HINGLISH first** (Hindi in Devanagari, English words in English letters, numbers in Hindi words),
  then English. **On-screen text: ENGLISH ONLY** (no Hindi text in the video).
- **Voice (Hinglish): `sameer`**, same as the headphones video: `[calm, narration]` on every line, lineGapMs 400,
  paragraphGapMs 650, continuity true, normal speed/pitch. **APPROVED + FINAL**: `projects/brahmos/final/voice_hinglish_FINAL.wav`
  (EngineX speak job `ee91c1b5-de08-4daf-a7c3-34fe3f91512d`, 373.807 s). Text: `projects/brahmos/vo_hinglish.txt`.
- English voice (later): `arnav`, same as the headphones English. A first take exists
  (`projects/brahmos/audio/vo_english_arnav_v1.wav`, job `4a76fa59-...`) but is NOT checked: its line
  "So why would a missile this fast fly so low?..." runs 17 s (183.2-200.3 s) = suspected babble; flagged lines 19 and 35.
- Length ~6 min (trimmed from 7.5). Palette **night-blaze/dark** (#111E26 ground, lime #DAFF01 words, blaze #F74304
  highlight only; never blaze words on lime). Fonts: **Unbounded** (display), **Rajdhani** (text/labels), **JetBrains
  Mono** (HUD). Type minimums on 1920x1080: display >= 72 px, lines >= 48, labels >= 30.
- Missile model + colours APPROVED (silver brushed aluminium, red band at the nose joint, dark section ring, titanium
  intake cone, camo canister with silver dome cap).
- The warship is the user's model `projects/brahmos/battleshipwarship.glb` (Sketchfab "battleship/warship" by
  林柏勳 (Lin), CC-BY-4.0). **Credit goes ONLY in the YouTube description, never on screen** (user's instruction).
- Low-res (960x540) video for the user's review before any 1080p final. The user reviews by eye and catches details.
- No music decided yet (headphones used the user's own track; the user rejected a generated bed then). Ask.

## 3. Standing rules (from the user's memory notes, see handoff/memory/)
- EngineX call budget: <= 500 calls per video; never re-run a job that succeeded; `idempotencyKey` on every job;
  `waitMs: 0` for renders then `get_job`. ~75 calls used so far.
- Text never covers the 3D model; designed background (not a flat stage) behind transparent plates; model right of
  centre, words in the left column; check small parts close up.
- `check_design` has NO idempotency key and its 2-min wait timed out once (job id lost): use
  `run_operation motion-graphic polish` with `idempotencyKey` + `waitMs: 0` instead.
- Blender: `look_at` reads `matrix_world`: call `bpy.context.view_layer.update()` before it (blank renders otherwise).
  `make_camera` clips at 200 m by default: `cam_at` in brahmos_scene.py sets 20 km.

## 4. Files (projects/brahmos/)
| File | What |
|---|---|
| 01_research.md | fact ledger with sources; [EST] = our own estimates (shown as "illustrative" on screen) |
| 01b_style_mix.md | the channel style study and the mixed style guide |
| 02_parts.md | parts list, names, x ranges, materials |
| 03_script.md | English script with a visual directive on EVERY line (after `||`) = the shot bible |
| vo_hinglish.txt | the Hinglish narration actually voiced (same content, line for line) |
| 04_creative_plan.md | the idea (the radar screen frames the whole video), what each EngineX skill does |
| chapters_hinglish.json | 9 chapters: start/end/len from the voice's own line timings (sum 373.807 s) |
| cues_hinglish.json | word-timed cues per chapter (when each part/number is spoken) |
| audio/transcript_hinglish.json | aligned word timings (transcribe-regional job 1f32d030) |
| brahmos_model_fc.py | FreeCAD airframe (v2, job bb5f94ad): 8400 mm, 30 parts, booster INSIDE the aft chamber |
| model/brahmos.glb .step .FCStd | the FreeCAD outputs |
| brahmos_scene.py | shared Blender module: glb import + normalise, materials, night world, `cam_at` |
| ch1_job.py ch2_job.py ch3_job.py | chapter plate jobs (args: mode preview/final, pct, samples) |
| overlays/ | overlay_ch1.html, overlay_ch2.html, bg_layer.html (night-blaze), build_pages.py |
| keys.txt | EngineX upload keys already in the bucket (brahmos.glb, warship.glb): reuse, no re-upload |
| review/ | review sheets already looked at |

**How a Blender job is built and run** (one file per job):
```
cat .claude/skills/blender-animation/scripts/skilllib.py projects/brahmos/brahmos_scene.py projects/brahmos/chN_job.py > job_chN.py
# upload job_chN.py (create_upload_url + curl -T), then:
run_operation blender script {code: "exec(open(inputs['job.py'], encoding='utf-8').read(), globals())",
  files: {"job.py": <key>, "brahmos.glb": <glb key>, "warship.glb": <warship key, ch1 only>},
  args: {mode: "preview"|"final", pct: 50, samples: 24, ship_draft: 0.12 (ch1)}, idempotencyKey: "brahmos-chN-..."}
```
(regenerate skilllib.py with `python .claude/skills/blender-animation/scripts/bundle.py` if it is missing.)

## 5. Chapter status
Timings: ch1 0-45.88 | ch2 45.88-79.90 | ch3 79.90-117.82 | ch4 117.82-180.15 | ch5 180.15-247.30 | ch6 247.30-293.61 |
ch7 293.61-323.99 | ch8 323.99-350.63 | ch9 350.63-373.81 (seconds in the voice).

| Ch | Plate (Blender) | Overlay | State |
|---|---|---|---|
| 1 Hook | ch1_job.py: sea at night + user's warship + moon glitter, chase cam, slow fly-past, side title shot, x-ray "hollow pipe". Preview v2/v3 reviewed OK. **Low-res full render = job `dddc30b3-e2e9-462d-b1e6-2bbea79fcc03`** (out `ch1_plate.mp4`) | overlay_ch1.html: radar HUD, ≈1 KM/S, 0:30 ticking, BRAHMOS, MACH 2.8, FAN/COMPRESSOR/TURBINE + blaze ✕, "?". Motion-check done (radar sweep "competing" kept on purpose: tell the user). Polish v1 fixed; **polish v2 = job `a42a3017-03f1-440f-82cd-79fc2cee02fa`** | render running |
| 2 Open it | ch2_job.py (transparent WEBM): hero turn, procedural ghost bus 10.5 m, x-ray, 5 parts move out on their words. **Preview = job `72d416fd-0489-4a36-aabb-851d84313b5f`** (not reviewed yet: check its `gate` + stills) | overlay_ch2.html: two rivers draw -> BRAHMOS, 1998, size cards, 5-part list. **motion-check `a755e076-...`, polish `6a7db7b4-ae35-4121-bb32-ac17ffd801f5`** | queued |
| 3 Launch | ch3_job.py: procedural 12x12 launcher, erector raises 3 canisters, launch flame/smoke volumes, booster x-ray on "Diwali", pitch-over + shock cone, booster slides out + tumbles. **Preview = job `33d7d187-183a-4483-b607-7e9963ec138f`** (first run of this code: expect fixes) | not written | queued |
| 4-9 | not written | not written | todo |

Shot ideas for ch4-9 are in 03_script.md (visual directive per line) and 04_creative_plan.md section D.

## 6. Next steps (in order)
1. `get_job` the in-flight jobs above. Ch1 render done -> download (sign_output), look at it, send the user the
   low-res link for review. Ch2/ch3 previews -> build a contact sheet from the stills, review, fix, re-preview.
2. Finish overlay checks (polish v2 ch1, motion-check + polish ch2), carry fixes by hand (never accept a fix that kills
   the meaning: polish once moved the strike bars 47 px below the words).
3. Composite per chapter: `python -I overlays/build_pages.py <N> <plate file> bg|nobg` (ch1 = nobg, opaque plate;
   ch2 = bg, transparent webm), then `motion-graphic/render` with the plate in `media`, the voice as `audio` with
   `audioStart` = chapter start, `duration` = chapter length, idempotencyKey.
4. Write ch4 (ramjet cutaway: turbofan vs ramjet split, bike-wind inset, shock lines on the intake cone with air cyan->
   orange, fuel spray, flame, thrust graph), ch5 (guidance: flight profile, INS + satellite, sea-skim, radar-horizon
   diagram, seeker lock, S-weave/dive), ch6 (½mv², 9x bars, cricket ball, 2 min vs 30 s race), ch7 (land/sea/air/
   underwater panels, Su-30MKI, official India map from hf-assets/maps + range rings 290/500/800), ch8 (Sindoor
   headline card, Lucknow factory, 80 %, globe), ch9 (one fly-through nose->nozzle, back to the radar at 0:00, end card).
5. Sound effects (find_sound, check licences), music (ask the user), thumbnail (Poster Director), YouTube text
   (title options, description with chapters + sources + warship credit), then the English version.

## 7. UPDATE (after the first push, same day)
- **Ch1 low-res render DONE** (job `dddc30b3`, 26.9 min = ~1.2 s/frame for 1376 frames): output key
  `output/dddc30b3-e2e9-462d-b1e6-2bbea79fcc03/ch1_plate.mp4`, local copy `projects/brahmos/plates/ch1_plate_lowres_v3.mp4`,
  stills in `review/ch1v3/` + `review/ch1v3_video_sheet.png`. The user has the link; **waiting for the user's feedback.**
- My own review of it (told to the user, who has NOT decided yet):
  1. Chase shot 14-27 s is weak: one angle for 13 s, the missile drifts right -> left in frame, the tail reads as a flat
     glowing orange DISC (the nozzle face lit by the point light). Fix: two angles (behind, then a low side skim), a
     volume exhaust glow instead of the lit disc, no y-drift on camB.
  2. Title shot C2 29-35.5 s too dark (missile nearly a black silhouette under BRAHMOS / MACH 2.8): add a moonlit key.
  3. Opening 0-14 s nearly static: stronger push on camA (the radar HUD overlay also adds change there).
  I asked the user: fix these now (~27 min re-render) OR first composite the HUD overlay + Hinglish voice on this
  version so they can judge it with sound. Ask again on the desktop.
- Renders: write PNG frames (or snapshots) if the user wants live progress in the EngineX dashboard; an mp4 output shows
  "No picture yet" until the end (the user asked why it was "not done").
- Ch2 preview `72d416fd` and ch3 preview `33d7d187` ran after ch1 freed the GPU: check them first.
