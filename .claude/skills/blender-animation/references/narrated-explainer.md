# Narrated 3D explainer ("Branch Education style")

Learned from `learning/branch-clocks/notes.md` (measured, not guessed). Use for any video where a voice explains how a
device works and the picture must show each part as it is named. Scripts: `beat_sheet.py`, `focus_rig.py`,
`callouts_page.py`, plus the exploded-view and camera tools. **Status: method documented and scripts unit-checked
locally; `focus_rig.py` has not yet been run in an EngineX job - first use = one preview job, review, then log.**

## The pipeline (do it in this order; it keeps EngineX calls low)
1. **Script** in beats: one idea per sentence, part names in Title Case, acronyms spelled out on first use, an analogy
   before a mechanism, concrete numbers with units. Target 140-150 wpm.
2. **Voice first** (EngineX Emotive Speech or the user's VO) -> **transcribe** with word timings (1 call). The audio is
   the clock for everything.
3. **Beat sheet**: `python beat_sheet.py transcript.json terms.json beats.json --fps 30`. `terms.json` maps a spoken
   term to {part, shot, chip, number}. Output: per beat the frame the camera must START moving (word onset - 0.6 s,
   the measured Branch lead), the frame it must be settled (word onset), and the hold until the next beat (min 2.5 s;
   shorter beats are merged so nothing flashes).
4. **One Blender job per sequence** (not per shot): `focus_rig.py` keys the camera to each beat's target part, ghosts
   the other parts, glows the named part, then renders 3-6 gate frames; only after review, the animation. Plate only:
   no text in 3D.
5. **One Motion Graphic render per sequence** for chips, ratios, kinetic numbers, disclaimers and 2D schematics, driven
   by the same beat sheet (`callouts_page.py` pattern: tracks + beats in the page).
6. Review the montage of the final cut (1 montage + 1 sign).
Budget for a 10-15 min video: ~1 transcribe + 1 Blender preview + 1 final per sequence (4-6 sequences) + 1 MG per
sequence + review = well under 100 calls. Never re-run a render that already succeeded: use `idempotencyKey`.

## Structure template (from the film)
Real world (photoreal room, the device in use) -> "let's open it" (housing peels / explodes) -> one system at a time
(title chip per system) -> zoom to the physics (scale dive) -> abstract to a 2D schematic over the blurred 3D ->
back to the real part doing the thing -> back to the room. Second topic reuses the first's visuals and diagrams.

## Timing rules (measured)
- Camera arrives on a part **0.5-0.7 s before** its name is spoken (median 0.62 s); a number/label appears ON the word.
- Median shot 6 s; most 3D shots 3-8 s; diagram logic as ONE long take that grows block by block (up to minutes).
- Hold a named part >= 2.5 s; one new element per sentence (~one pause of ~0.6 s per sentence in the VO).
- Cuts ALSO land on sentence starts, not only on part names: validated against the real film, name-only beats
  matched a real cut within 1.5 s for 11/19 beats (median 1.43 s off). Snap each beat's `settle_f` to the nearest
  sentence start (pause > 0.5 s) when one is within 1.5 s; that is the remaining gap to Branch's edit.
- Narration 146 wpm -> about 2.4 words per second -> a 6 s shot carries ~14 words (one sentence).

## Look rules
- Two worlds: **context** = photoreal daylight interior, blind-stripe shadows, 85-135 mm, f/2-2.8;
  **internals** = black void, soft top key + rim + light haze, no floor, 85-200 mm macro, f/4-8, rack focus between parts.
- **Focus by subtraction**: named part solid; others ghosted (blue-grey, ~15 % opacity / wire) or defocused;
  housings become glass to show insides. `focus_rig.ghost()`.
- **Highlight on the word**: orange emissive rim/ring on the named part for the length of its beat. `focus_rig.glow()`.
- **Colour code** fixed for the whole film: orange = active/signal/current; red/blue = poles, +/- charge; white matte
  plastic, real metals. Write the palette in the beat sheet header and never change it.
- **Physics as visuals**: field lines as glowing particle arcs, charges as +/- badges, motion exaggerated WITH a small
  disclaimer ("Movement exaggerated for this visualization").
- **Chips (Motion Graphic)**: system titles bold italic CAPS, yellow-orange, lower-right; ratio chips "12 < 48"
  (arrow at the driven gear); big kinetic numbers with small units; counters roll to the spoken value.
- **Schematics**: dark grid, white 2 px line art, orange accents, Title Case labels, blocks appear on their word, signal
  flow as moving chevrons, waveform boxes. Icons match the 3D part silhouettes. Built in Motion Graphic (SVG + GSAP),
  over a blurred still of the 3D, not modelled in Blender.
- Brand bug bottom-right, every shot.

## Naming rules
Functional names, defined once, reused verbatim on screen and in voice: "Driver Gear", "Compound Gear", "Idler",
"Time Setting Gear", "Crystal Oscillator", "Tuning Fork", "Integrated Circuit", "Inverter", "Binary Counter",
"Voltage-Controlled Oscillator (VCO)", "Phase Comparator", "Integrator", "Frequency Divider". Blender object names =
the same names in snake_case (`driver_gear`), so the beat sheet maps words straight to objects.

## Checklist before the final render of a sequence
Every beat has a target object that exists - every named part is in frame and >= 25 % of frame height when it is
named (`fill_fraction`) - camera settles before the word - no beat shorter than 2.5 s - ghost/glow restore after each
beat - chips and numbers come from the beat sheet, not typed by hand - disclaimers on exaggerated motion.
