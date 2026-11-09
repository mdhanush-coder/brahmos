---
name: brahmos-video-project
description: "State of the BrahMos explainer (next video after headphones): ENGLISH ONLY, choices made, files, what's left"
metadata:
  node_type: memory
  type: project
  originSessionId: 248938f3-a843-4c10-bd9d-9d45748e6968
  modified: 2026-11-09T08:13:16.719Z
---

Started 2026-11-09 in projects/brahmos/. User wants >5 min (chose trim to ~6), Branch style mixed with other channels, a visual on every line, script approval BEFORE audio, and all 9 EngineX skills used creatively.

**ENGLISH ONLY** (user, 2026-11-09): narration and every on-screen word in English, no Hindi text. Hindi drafts (03_script_hi*.md) are backup only.

Choices: palette night-blaze/dark; fonts Unbounded (display) + Rajdhani (text/labels) + JetBrains Mono (HUD); voice was "raghav" for Hindi, so re-confirm the English voice (raghav untested in English; arnav/nandini/yash are Indian-accent English heard right).

Files: 01_research.md (fact ledger), 01b_style_mix.md (Branch + Real Engineering + Mark Rober + Animagraffs), 03_script.md (English, 925 words ≈ 6:20, lint 0 errors, visual on every line), 04_creative_plan.md (radar-screen frame idea, role of each EngineX skill).

Voice (2026-11-09): user wants HINGLISH audio first (headphones style: voice sameer, "[calm, narration]" per line, English words in Latin letters, numbers in Hindi words, lineGapMs 400), then English. Hinglish take = speak ee91c1b5 (373.8 s, all 42 lines verified by transcribe-regional 1f32d030), file audio/vo_hinglish_sameer_v1.wav, text vo_hinglish.txt. English take = speak 4a76fa59 (arnav, lineGap 700/para 1200, 349 s) in audio/vo_english_arnav_v1.wav: NOT yet checked (line 23 runs 17 s, flagged lines 19 and 35).
HINGLISH AUDIO FINAL (user, 2026-11-09): final/voice_hinglish_FINAL.wav (= speak ee91c1b5). Chapter times chapters_hinglish.json (9 ch, 373.8 s), word-timed cues cues_hinglish.json (from transcribe 1f32d030).
MODEL: FreeCAD script brahmos_model_fc.py v2 (job bb5f94ad) -> model/brahmos.glb/.step/.FCStd: 8400 mm, 30 named parts, booster nested INSIDE the aft chamber (slides out backwards), fins at the very tail, all overlaps 0. Known nit: intake struts poke ~2 mm through the cowl (hide/scale in Blender). Awaiting user's look at model/brahmos_side_v2.png before Blender chapters.
BLENDER (2026-11-09): user approved model + colours. Shared module brahmos_scene.py (glb import, materials, cam_at with clip 20 km + look_at after view_layer.update — stale matrix_world aimed every camera at the origin = blank renders). Chapter 1 = ch1_job.py (5 shots, procedural warship, sliding sea, x-ray glow); preview v2 523a8a61 approved by me; User supplied projects/brahmos/battleshipwarship.glb (Sketchfab "battleship/warship" by 林柏勳 (Lin), CC-BY-4.0 -> MUST credit in YouTube description); uploaded key in keys.txt, imported as files['warship.glb'], normalized to 150 m, args ship_draft 0.12. Procedural ship replaced; old render 89eab634 cancelled. LOW-RES render v3 = job dddc30b3 (ch1_plate.mp4). Bundle = skilllib.py + brahmos_scene.py + chN_job.py -> job_chN.py; glb key in keys.txt.
PARALLEL WORK (2026-11-09, user OK'd "overlays + remaining Blender code during renders"): overlays/ has overlay_ch1.html (radar HUD, 0:30, BRAHMOS, MACH 2.8, FAN/COMPRESSOR/TURBINE with blaze ✕ beside words — strike bar over lime failed contrast 3.2:1), overlay_ch2.html (two rivers draw -> BRAHMOS, 1998, size cards, 5-part list with colour dots), bg_layer.html (night-blaze), build_pages.py (bg|nobg). ch1 keeps the radar sweep despite motion-check "competing" (deliberate, tell user). check_design has NO idempotency key and timed out once: use run_operation polish + key. Blender queue: ch1 lowres dddc30b3 -> ch2 preview 72d416fd -> ch3 preview 33d7d187. ch3 = procedural 12x12 launcher, erector, launch flame/smoke volumes, baked erector ride -> free pitch-over path, booster slides out the tail.
Left: script approval -> voice -> transcribe -> FreeCAD airframe -> Blender chapters -> overlays -> assemble. Budget per [[enginex-call-budget]], overlay rules per [[overlay-layout-rules]].
