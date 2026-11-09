---
name: headphones-video-project
description: "State of the Hindi \"wireless headphone radiation myth\" explainer in headphones/ (cloned xplainedunseen-studio): which chunks exist, chunk 3 v8 re-render, what is left"
metadata:
  node_type: memory
  type: project
  originSessionId: 20cd9717-3635-43e2-afca-1dc82b33bf14
  modified: 2026-11-08T12:47:14.720Z
---

Repo cloned 2026-11-08 to `blender_animation_skills/headphones/` (github mdhanush-coder/xplainedunseen-studio). Script = `wireless-myth/tool_input_hindi.txt` (50 lines), narration `wireless-myth/narration_sameer.mp3` (~297 s).

Chunks done (each is a slice of the one narration file): chunk 1 hook 0-15.2 s (`chunk/hook_chunk_v7.mp4`), chunk 2 15.2-71.0 s (`chunk2/chunk2_v5.mp4`), chunk 3 71.0-131.5 s (latest `chunk3/chunk3_v9.mp4`), chunk 4 131.5-211.7 s (`chunk4/chunk4_v2.mp4`), chunk 5 211.7-269.8 s (`chunk5/chunk5_v1.mp4`). chunk 6 269.8-297.0 s (`chunk6/chunk6_v1.mp4`). All 6 chunks done 2026-11-08; durations sum to 297.1 s. Final assembly done 2026-11-08 in `headphones/final/` (`mix.py`): wireless_myth_hindi.mp4, wireless_myth_english.mp4 (English voice arnav, lines placed at Hindi anchors from `en_segments.json`, max 1.16x speed-up), wireless_myth_hindi_audio.wav/.mp3, all 297.08 s; BGM = user's Pulsar track (The Grey Room / Density & Time, from Downloads; user rejected the EngineX text-to-music bed), 0-211.7 s then again from 2:00, -18 dB; EngineX video/sound-design jobs sat unclaimed in the queue so the mix runs locally; library SFX in `final/sfx/`; sidechain ducking; -14 LUFS. Hook's end fade-to-black (14.7-15.2 s) still in.

Chunk 3 v8: user complained v7 had the 3D clips shifted/shrunk with a black gradient, cutting the headphone and rings in half. v8 = full-frame plates, no black layer, text as its own overlay. The v7 wide-shot plate was lost, so it was rebuilt from `headphones.glb` (`chunk3/wide_plate_v8_blender.py`, `wide_plate_v8.mp4`) in the chunk palette (cream cushions, champagne metal, charcoal housings, bronze plate, blue PCB, copper antenna, pale-blue rings). Page = `chunk3/proj/index_v8.html`. Driver scene = `wireless-myth/scene3b_parts_only.mp4`, chip close-ups = `scene3c_parts_detail.mp4`, ear still guessed as `chunk2/ear1.png`, overlay = `chunk3/ov4.webm`.

Chunk 3 v9 (`chunk3/chunk3_v9.mp4`, latest): user's next rule, 2026-11-08: whenever a part is NAMED in the narration, Blender must zoom to that part (isolated close-up, model on the RIGHT of the text column), with a 2D label beside it. Done for battery (84.4 s), chip (86.5), antenna (88.9, 114.6), chip again (117.0) via `chunk3/closeups_v2.mp4` + `closeups_v1_blender.py`; codec graphic moved right of the SBC/AAC/LDAC chips; crossfades kept short so no two scenes overlap. Page = `chunk3/proj/index_v9.html`. Overlay `ov4.webm` word times: Battery 84.5, Chip 86.5, Antenna 89.0.

Chunk 4 done 2026-11-08: `chunk4/chunk4_v1.mp4` (131.5-211.7 s), beats in `chunk4/BEATS_chunk4.md`; word timings for the whole narration (297 s) in `wireless-myth/narration_words.json`. Chunk 5 done: `chunk5/chunk5_v1.mp4` (211.7-269.8 s), new Blender driver plate `chunk5/driver_v2.mp4`. Next: chunk 6 = 269.8-297.0 s ("so the truth is", antenna weak / driver is the real enemy, volume low + breaks, pick up the old wired headphone, comment CTA).

**Why:** the user reviews by eye and catches cut-off models; keep colours matched to the existing chunks.
**How to apply:** for chunks 4-6 keep plates full frame with the model right of centre (shift_x) so the left text column stays clear; verify the unverified facts in NOTES.md (IARC 2011, WHO 1 billion, 85 dB, milliwatts) before building chunks 4-5. See [[overlay-layout-rules]] and [[enginex-call-budget]].

REELS DONE 2026-11-08 (`headphones/reel/`, `make_reel.py`): 5 beats (0-11.3, 132-140, 160.6-172, 211.7-231.6, 270-297) cut locally with continuous Pulsar bed + whoosh at joins, then EngineX Video Studio video/grid `fit_blur_bg` 9:16 (user asked for Video Studio once): wireless_myth_reel_hindi.mp4 (77.8 s, job 45c80f82), wireless_myth_reel_english.mp4 (78.5 s, job d0a8625c). No captions burned in (caps_hi/en.json written, unused).
REELS v2 (EngineX palette black-ember/dark, user-chosen 2026-11-08) = CURRENT: headphones/reel/wireless_myth_reel_hindi_ember.mp4 (render cd50fd47) and wireless_myth_reel_english_ember.mp4 (render 4eece734). build_page.py = Motion Graphic page: frost beat titles with one ember word, full-width 16:9 band y600-1208, phrase captions below, ember radio rings in the bottom 30%, progress bar, ember right column. The plain fit_blur_bg reels are superseded.
