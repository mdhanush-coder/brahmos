---
name: tech-explainer-video
description: Use when the user gives a topic (and optionally a length in minutes) and wants a complete narrated 3D "how it works" video in the Branch Education style, made automatically on EngineX - research, engaging script, human-sounding voiceover, Blender 3D visuals that zoom to each part as it is named, synced callouts, assembly and review. Triggers: "make a video on X", "N minute explainer about X", "Branch style video".
---

# Automated tech explainer (topic + minutes -> finished video)

The user gives **a topic and a length**. Everything else is decided here. The style, timing and grammar come from the
measured study of Branch Education (`learning/branch-clocks/notes.md`, `blender-animation/references/narrated-explainer.md`).
All media, 3D and rendering run on EngineX; local work is planning text, scripts and JSON only.
Load `.claude/skills/blender-animation/SKILL.md` too: its workflow, quality bar and review loop apply to every 3D shot.

## Fixed defaults (decide, do not ask)
1920x1080, 30 fps, English, voice `owen` (Emotive Speech, recorded, "clear and measured tech explainer"; backup `henry`),
**146 words per minute including pauses** (Branch measured), sentence gap ~0.6 s, 16:9, H.264/AAC 48 kHz.
Length: what the user said; if not said, 6 minutes. Audience: curious adults, no prior knowledge.
Ask only if the topic is ambiguous enough that two different videos would result.

**Hindi / Hinglish narration (Temple, 2026-11-07):** script in Devanagari Hinglish (English tech words spelled in Devanagari:
डिवाइस, सेंसर), every number and unit in words (पचासी हज़ार रुपये, ज़ीरो पॉइंट आठ), one documentary brief on every paragraph
and NO feeling tags (the user wants one tone and one pace), `[pause]` before reveals. Voice: offer recorded Hindi voices
(arnav, raghav, aarav, nandini) and let the user pick by ear (they chose **raghav**: steady documentary). Emotive Speech runs
on CPU pods only: leave `tier` out (`gpu` would wait forever); one job per person at a time, so takes queue. Measured: the
~3,860-character script = 4:51 (raghav), 5:03 (arnav), 4:59 (nandini); all 32 lines verified by the job's own read-back
(`checked.lines`). Word timings for Hindi: `transcribe-regional/transcribe` with `language: hi` (786 words aligned); its
result is too big to print, so parse the saved tool output (`d['result']['result']['segments']`) in Python with
`sys.stdout.reconfigure(encoding='utf-8')` (`python -I` ignores PYTHONIOENCODING). Chapter = paragraph; chapter start/end
= the job's `lines` timings; chapter video length = start to the next chapter's start (pauses included).

**Choices to ask once, together, before building** (AskUserQuestion): voice, palette (enginex-color-palette; Temple:
Charcoal Gold, dark lead), font (enginex-typography; Temple: Space Grotesk, English-only), on-screen language (English
labels keep the visuals reusable for other narration languages). Ask for reference pictures of the real product.

**Voice rules (user's instructions):** no cloning of any real narrator (we have no right to their voice); match the
Branch pacing instead. **No emotional tone tags** - only one neutral delivery brief per paragraph
(`[a documentary narrator explaining to a friend, warm and clear, steady pace]`, USER-APPROVED 2026-11-07 for every
video) plus `[pause]` / `[long pause]` lines. Lines are LINKED CLAUSES (who / which / where / and; जो / जिसे / जहाँ / और),
never short facts split by full stops: that read as robotic to the user. `continuity: true`,
no `temperature`, no `emotion`, `speed` normal. Human feel comes from line shape (one thought per line, 2 sentences,
commas where breath goes, contractions), not from tags. Details: `references/voice-direction.md`.

## EngineX call budget (hard rule: <= 500 per video; target <= 15 per finished minute)
Plan the calls before starting (`plan_video.py` prints the plan), use `idempotencyKey` on every job, never re-run a job
that succeeded, predict output keys instead of polling, wait with a background `sleep`, batch `sign_output` (50 keys).
Report the count at the end.

## The pipeline (in order; each step names its tools)
1. **Plan** - `python scripts/plan_video.py "<topic>" <minutes> <project_dir>` -> `plan.json` + `00_plan.md`:
   word budget, chapter skeleton (hook / open it / systems / dive / connect / close), beats per chapter, call budget.
2. **Research** (WebSearch / WebFetch, no EngineX) -> `01_research.md` fact ledger: claim, number, unit, source URL,
   confidence. Every number spoken must be in the ledger. Same rules as the `youtube-science-documentary` skill
   (primary sources, two sources for key numbers, mark estimates). Also collect reference images of the real device
   for modelling (dimensions, part count, materials).
3. **Parts list** -> `02_parts.md`: every component the script will name, in Title Case, with its snake_case Blender
   name, real dimensions, material, and whether it exists in the library (`find_asset.py`) or is modelled.
4. **Script** -> `03_script.md` in the annotated format, written by `references/script-formula.md` (the engagement
   formula). Then `python scripts/script_lint.py 03_script.md --minutes M` until it reports 0 errors. It exports per
   chapter: `chapters/NN.speak.txt` (exact text for Emotive Speech), `chapters/NN.terms.json` (for the beat sheet)
   and `shotlist.json`.
5. **Voice** - ONE `emotive-speech/speak` for the whole video (all chapters' `speak.txt` joined with a blank line =
   paragraph gap; up to 20,000 characters = ~20 min) with owen, `lineGapMs` 350, `paragraphGapMs` 900, continuity,
   wav, gpu, `waitMs: 0` + `idempotencyKey`. Then ONE `transcribe/transcribe`: it is both the word check and the word
   timings. Chapter boundaries = the result's `lines` timings (first and last line of each chapter); split the
   transcript per chapter locally. Check wpm 140-152 and every line present; if a line fails, re-take only the
   chapters around it with a new key and splice by timings in the final audio-replace step.
6. **Beats** - `python ../blender-animation/scripts/beat_sheet.py chapters/NN.transcript.json chapters/NN.terms.json
   chapters/NN.beats.json --snap` -> camera move/settle/hold frames per named part (0.6 s lead, snapped to sentence
   starts, min hold 2.5 s, dwell rule below).
7. **3D per chapter** - ONE `blender/script` job per chapter (preview mode: 4-6 gate frames + all `blender-animation`
   gates), review the sheet, then ONE final job (plate.mp4 + tracks.json). Shot types and how each is built:
   `references/visual-sync.md`. Models: library first, else detailed procedural parts (`product_models.py` standard).
8. **Overlay per chapter (silent)** - `callouts_page.py tracks.json index.html --beats beats.json --duration <chapter s>`
   (chips, kinetic numbers, labels, disclaimers, brand bug) zipped with the plate -> ONE `motion-graphic/render` per
   chapter, `duration` = the chapter's exact voice length from `lines`. Schematic-only chapters: a Motion Graphic page
   with no plate (`tracks` = `-`). The Blender job for a chapter is the same uploaded `chapter_job.py` with
   `args.chapter` = N (upload once).
9. **Assemble** - ONE `video/concat` of the chapter MP4s in order, then ONE `video/audio-replace` with the whole
   voiceover wav (describe_operation once). Optional music bed from `find_sound` + `video/duck`.
10. **Review** - ONE `video/sprite` of the master + sign + look (blender-animation review loop, plus the sync checks
    in `references/visual-sync.md`). Fix only the chapter that fails, re-render only it.
11. **Deliver** - master link, chapter links, script, sources list (for the description), call count, what was fixed.

## Plates, background and overlays (user rules, learned on Temple)
- **Text never covers the 3D model**, at any frame. Every chapter job ends with `finish_plate(scene)`
  (`projects/temple/finish_plate.py`): floor = shadow catcher, film transparent, and `keepout.json` = the device's screen box
  every 2nd frame. The page places the plate right of centre (scale 0.78, +300 px) and keeps ALL words in one left column;
  `keepout_check.py` must print ALL CLEAR (every element vs every frame it is up, +24 px) before any overlay render.
- **A designed background, never a flat stage**: plates render as WebM with alpha (`render` format `webm`, `transparent:
  true`); `bg_layer.html` (palette radial gradient, a gold glow that follows the device, faint drifting dot grid, seeded
  dust from the seek time, vignette) sits behind them; `build_pages.py <ch> <seconds>` assembles background + plate + overlay.
- **Overlays**: one page per chapter, GSAP paused timeline, every element timed to its spoken word from the transcript,
  `<meta charset="utf-8">` ALWAYS (without it ₹ rendered as "â‚¹"; also write it as `'₹'` in scripts), ₹ in Indian
  grouping (`toLocaleString('en-IN')`), 7 % side margin (136 px), no made-up numbers (BrainFlow got a definition card, not
  invented readings). Run Design Polish (`check_design`, palette id) and carry its fixes back into your own file.
- **Load and follow the EngineX skills the user names** (they asked for all of them): Motion Director, Typography, Color
  Palette and Design Polish, read in full (`get_skill`), not only their tools. What they changed on Temple:
  - Motion Director: one lead move at a time; camera still while words are read; one entrance per role (rise 24 px, 0.5 s
    power3.out, exits 0.4 s); `motion-graphic/motion-check` on the merged page (background included) before any render,
    every `should` fixed and re-run (an opacity flicker read as words leaving; a 10 % glow "breath" flagged as competing).
  - Typography video sizes on 1920x1080: display >= 72 px, lines read for meaning >= 48 px, labels >= 30 px.
  - Color Palette (dark lead): gold only on the ONE word or number that matters per frame (kickers, step numbers, borders
    and the second card title went cream); no colour outside the palette (no black vignette); data colours that label the
    real thing (the emitters' green/red/IR) are the one documented exception.
- **Never render through `check_design` with a long wait**: it has no idempotency key, and a 2-minute client timeout
  lost the job id of a chapter composite (Temple ch1), forcing a second run. For any polish WITH `render: true`, call
  `run_operation motion-graphic polish` with `idempotencyKey` + `waitMs: 0`, then `get_job`. A plate in `media` is at
  `assets/<last path segment of its key>` (a Blender render's `render.webm`).
- **Look at every auto-fix in the after-stills before trusting a polish render**: on Temple ch1 `fix: true` grew the
  rotated "TOY?" stamp into a 372 px box with the word sunk to the bottom (a box-centre rule fighting a rotation), and it
  flagged "edges" of the transparent plate's empty area. Carry the useful fixes into your own CSS by hand, give stamps and
  rotated boxes explicit compact padding. Then render the final with `motion-graphic/render` (idempotencyKey, the plate
  in `media`, the voice as `audio` + `audioStart` = chapter start): `polish` with `fix: false` + `render: true` FAILS
  (ENOENT motion.mp4, engine bug seen twice on 2026-11-07). A 25-40 s chapter composite renders in ~20 s.
  `sign_output` refuses keys that do not exist yet: a cheap way to check a predicted output before `get_job`.
- **Low-res first**: the user reviews a 960x540 / 32 spp pass (~1.1 s/frame) of each chapter before any 1080p final.
- **The user's reference pictures are the spec** for the device (shape, layers, PCB artwork, pad texture): ask for them
  before modelling; expect close-up review (they caught an LED outside its window and parts off the PCB edge).

## Rules that keep viewers watching (from the study)
- Open on the device in a real place doing its job, and a question the viewer has never asked (0-20 s).
- A visual change every 5-8 s (new part, new angle, scale dive, diagram block, number), but **dwell**: once the camera
  settles on a named part it does not move off it until the sentence that explains it has ended + 0.4 s, and never
  less than 2.5 s. "Stay there until the mind gets it, then shift."
- One idea per sentence; one sentence per shot (~14 words at 146 wpm).
- A curiosity hook at least every ~60-90 s ("But this raises a problem...", "So how does...").
- Abstraction is always bracketed by the real object: real -> inside -> physics/diagram -> back to the real part.
- Every chapter has one pattern break: a scale dive, an x-ray reveal, a schematic over the blurred 3D, or a number slam.
- End by connecting back to the opening scene and the viewer's own life.

## Status (honest, 2026-11-07)
First real run: **Temple** (5-min Hindi explainer, `projects/temple/`). Done and checked on EngineX: script + Hindi voice
(4 takes, raghav chosen), word timings, the device model, chapter 1 (hero 360) and chapter 4 (explode, crane, tip, light in
skin) scenes approved by the user, overlays for both through Design Polish, the keep-out check ALL CLEAR, transparent
low-res plates rendering. NOT yet done: chapters 2, 3, 5-9, compositing plate + overlay + voice per chapter, assembly with
the music tail to 5:00, full-res finals, the final review. The generic `chapter_job.py` / `focus_rig.py` were NOT used
(the chapters were custom jobs on the local skilllib bundle); they remain untested. ~170 EngineX calls for ch1 + ch4 to
approval: most went into fix passes the user asked for from close-up review, so budget ~80 calls per 3D chapter.
Every defect class found is in `blender-animation/SKILL.md`'s Failure log (19-35).

## Music, end screen, thumbnail, YouTube text (learned on Temple, 2026-11-07)
- **Music:** popular channels' tracks are copyrighted (Kurzgesagt's score is commissioned from Epic Mountain), so do not copy or
  download them. `find_sound` first, but its music is mostly loud trailer scores; for a calm explainer use workflow `text-to-music`
  (caption: calm documentary underscore, soft pads, slow pulse, felt piano, very dry, no reverb/delay/echo, no vocals; lyrics
  `[instrumental]`; it takes no `seed`; ~100 s per piece, vary the key in the caption for variety). Convert mp3 with
  video/extract-audio codec wav, level pieces, crossfade 3 s, fade in 4 s and out 6 s, then `video/duck` (voice = the film's own
  audio, background = the bed; strength `light`, backgroundGainDb -2 gave music about 13 dB under the voice). MEASURE the result:
  `strong` + -9 dB left the music 33 dB under the voice (inaudible). Use `tier: gpu` (the cpu concat/duck was ~10x slower).
- **End screen:** 2 s Motion Graphic card (question + "Tell us in the comments"); render it with a silent wav as `audio` so concat
  keeps an audio stream.
- **Thumbnail:** Imagine-Pro background (no text, empty dark side for words) + a Motion Graphic page for the text (generators garble
  text): huge price, a curiosity hook ("TOY or GENIUS?"), dark gradient behind the words; keep under 2 MB; keep text off the face.
- **YouTube text:** Hindi title (<70 chars, 3 options), ~500-word description with chapter timestamps from the cumulative rendered
  durations, key facts only from the fact ledger, disclaimer, music/voice credit, 20 tags, "altered or synthetic content" checkbox.
- **NEVER use `find_sound` "Trailer scores" tracks (or any library music) in a published video without checking its licence.** On Temple a
  library cue ("Prologue - Birth") got a YouTube Content ID claim. Music = generated for the project (text-to-music) or none.
